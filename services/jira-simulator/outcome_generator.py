"""
Outcome Generator - Automatically generates outcomes when Jira issues are completed or reassigned.
"""
import os
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from db import execute_query, execute_update

logger = logging.getLogger(__name__)


class OutcomeGenerator:
    """Generates outcomes when Jira issues are completed or reassigned."""
    
    def __init__(self, ingest_url: str, poll_interval: int = 30):
        self.ingest_url = ingest_url
        self.poll_interval = poll_interval  # seconds
        self.running = False
        self.last_check_time = datetime.now() - timedelta(minutes=5)  # Start 5 minutes ago
    
    async def start(self):
        """Start background process."""
        self.running = True
        logger.info("Outcome generator started")
        
        while self.running:
            try:
                await self._check_for_outcomes()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Outcome generator error: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)
    
    async def stop(self):
        """Stop background process."""
        self.running = False
        logger.info("Outcome generator stopped")
    
    async def _check_for_outcomes(self):
        """Check for new outcomes and send to Ingest."""
        # Get issues that changed status to "Done" since last check
        resolved_outcomes = self._get_resolved_outcomes()
        
        # Get issues that were reassigned since last check
        reassigned_outcomes = self._get_reassigned_outcomes()
        
        all_outcomes = resolved_outcomes + reassigned_outcomes
        
        if not all_outcomes:
            return
        
        logger.info(f"Found {len(all_outcomes)} new outcomes")
        
        # Send to Ingest service
        async with httpx.AsyncClient(timeout=10.0) as client:
            for outcome in all_outcomes:
                try:
                    # Store outcome in database (for dedupe)
                    self._store_outcome(outcome)
                    
                    # Send to Ingest
                    response = await client.post(
                        f"{self.ingest_url}/webhooks/jira",
                        json={"outcome": outcome}
                    )
                    response.raise_for_status()
                    
                    # Mark as processed
                    self._mark_outcome_processed(outcome['event_id'])
                    
                    logger.info(f"Outcome {outcome['event_id']} sent to Ingest")
                except Exception as e:
                    logger.error(f"Failed to send outcome {outcome['event_id']}: {e}")
        
        # Update last check time
        self.last_check_time = datetime.now()
    
    def _get_resolved_outcomes(self) -> List[Dict[str, Any]]:
        """Get issues that were resolved since last check."""
        try:
            # Query issues that changed to Done status since last check
            # Use jira_issue_history if available, otherwise check resolved_at directly
            query = """
                SELECT 
                    i.key,
                    i.assignee_account_id,
                    i.project_key,
                    COALESCE(i.resolved_at, i.updated_at) as resolved_at,
                    COALESCE(h.changed_at, i.updated_at) as changed_at
                FROM jira_issues i
                LEFT JOIN jira_issue_history h ON i.key = h.issue_key 
                    AND h.field = 'status' 
                    AND h.to_value = 'Done'
                WHERE i.status_name = 'Done'
                AND COALESCE(h.changed_at, i.updated_at) > %s
                AND NOT EXISTS (
                    SELECT 1 FROM jira_outcomes o
                    WHERE o.issue_key = i.key
                    AND o.type = 'resolved'
                )
            """
            
            results = execute_query(query, [self.last_check_time])
            outcomes = []
            
            for row in results:
                # Map project key to service
                service = self._project_to_service(row['project_key'])
                
                outcome = {
                    "event_id": f"jira-resolved-{row['key']}-{int(row['changed_at'].timestamp())}",
                    "issue_key": row['key'],
                    "type": "resolved",
                    "actor_id": row['assignee_account_id'],
                    "service": service,
                    "timestamp": row['resolved_at'].isoformat() if row['resolved_at'] else row['changed_at'].isoformat()
                }
                outcomes.append(outcome)
            
            return outcomes
        except Exception as e:
            logger.error(f"Failed to get resolved outcomes: {e}", exc_info=True)
            return []
    
    def _get_reassigned_outcomes(self) -> List[Dict[str, Any]]:
        """Get issues that were reassigned since last check."""
        try:
            # Query issues that had assignee changes since last check
            query = """
                SELECT 
                    i.key,
                    h.from_value as original_assignee,
                    h.to_value as new_assignee,
                    i.project_key,
                    h.changed_at
                FROM jira_issues i
                JOIN jira_issue_history h ON i.key = h.issue_key
                WHERE h.field = 'assignee'
                AND h.changed_at > %s
                AND h.from_value IS NOT NULL
                AND h.to_value IS NOT NULL
                AND h.from_value != h.to_value
                AND NOT EXISTS (
                    SELECT 1 FROM jira_outcomes o
                    WHERE o.issue_key = i.key
                    AND o.type = 'reassigned'
                    AND o.timestamp >= h.changed_at
                )
            """
            
            results = execute_query(query, [self.last_check_time])
            outcomes = []
            
            for row in results:
                service = self._project_to_service(row['project_key'])
                
                outcome = {
                    "event_id": f"jira-reassigned-{row['key']}-{int(row['changed_at'].timestamp())}",
                    "issue_key": row['key'],
                    "type": "reassigned",
                    "actor_id": row['new_assignee'],  # New assignee
                    "service": service,
                    "timestamp": row['changed_at'].isoformat(),
                    "original_assignee_id": row['original_assignee'],
                    "new_assignee_id": row['new_assignee']
                }
                outcomes.append(outcome)
            
            return outcomes
        except Exception as e:
            logger.error(f"Failed to get reassigned outcomes: {e}", exc_info=True)
            return []
    
    def _store_outcome(self, outcome: Dict[str, Any]):
        """Store outcome in database for deduplication."""
        try:
            query = """
                INSERT INTO jira_outcomes 
                (event_id, issue_key, type, actor_id, service, timestamp, 
                 original_assignee_id, new_assignee_id, work_item_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
            """
            
            execute_update(query, [
                outcome['event_id'],
                outcome['issue_key'],
                outcome['type'],
                outcome['actor_id'],
                outcome['service'],
                outcome['timestamp'],
                outcome.get('original_assignee_id'),
                outcome.get('new_assignee_id'),
                outcome.get('work_item_id')
            ])
        except Exception as e:
            logger.error(f"Failed to store outcome: {e}", exc_info=True)
    
    def _mark_outcome_processed(self, event_id: str):
        """Mark outcome as processed by Ingest."""
        try:
            query = """
                UPDATE jira_outcomes
                SET processed = TRUE
                WHERE event_id = %s
            """
            execute_update(query, [event_id])
        except Exception as e:
            logger.error(f"Failed to mark outcome as processed: {e}", exc_info=True)
    
    def _project_to_service(self, project_key: str) -> str:
        """Map Jira project key to service name."""
        # Default mapping
        mapping = {
            "API": "api-service",
            "APISERVICE": "api-service",
            "PAYMENT": "payment-service",
            "PAYMENTSERVICE": "payment-service",
            "FRONTEND": "frontend-app",
            "FRONTENDAPP": "frontend-app",
            "DATA": "data-pipeline",
            "DATAPIPELINE": "data-pipeline",
            "INFRA": "infrastructure",
            "INFRASTRUCTURE": "infrastructure"
        }
        return mapping.get(project_key.upper(), project_key.lower().replace("-", "-"))

