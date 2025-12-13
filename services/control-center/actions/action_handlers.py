"""
Action handlers - process button clicks and trigger errors
"""
import asyncio
import logging
from typing import Dict, Any
from actions.error_simulator import generate_error_message, get_error_type_by_name
from integrations.ingest_client import create_work_item
from integrations.decision_client import get_decision_by_work_item
from integrations.executor_client import get_jira_issue_by_decision
from state.system_state import system_state

logger = logging.getLogger(__name__)

SERVICE_NAME = "api-service"

async def handle_error_trigger(error_type: str, intensity: int = None) -> Dict[str, Any]:
    """Handle an error trigger action."""
    try:
        # Get error type configuration
        error_type_config = get_error_type_by_name(error_type)
        
        # Generate error message
        error_message, severity, error_type_name = generate_error_message(
            error_type_config, SERVICE_NAME
        )
        
        # Add log entry
        system_state.add_log("ERROR", error_message)
        
        # Update metrics (simulate error impact)
        system_state.update_metric("error_rate", system_state.metrics.get("error_rate", 0) + 50)
        system_state.update_metric("cpu_usage", min(95, system_state.metrics.get("cpu_usage", 0) + 10))
        
        # Create work item via Ingest
        result = await create_work_item(
            service=SERVICE_NAME,
            severity=severity,
            description=error_message,
            raw_log=error_message
        )
        
        work_item_id = result.get("work_item_id")
        if not work_item_id:
            raise ValueError("No work_item_id in response")
        
        # Add incident to state
        incident = system_state.add_incident(
            work_item_id=work_item_id,
            error_type=error_type_name,
            severity=severity,
            error_message=error_message
        )
        
        # Add INFO log before error
        system_state.add_log("INFO", f"Simulating {error_type_name} error...")
        
        # Start background task to poll for decision
        asyncio.create_task(poll_and_update_decision(work_item_id))
        
        return {
            "success": True,
            "work_item_id": work_item_id,
            "incident": incident
        }
    except Exception as e:
        logger.error(f"Error handling trigger: {e}", exc_info=True)
        system_state.add_log("ERROR", f"Failed to trigger error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def poll_and_update_decision(work_item_id: str):
    """Background task to poll for decision and Jira issue."""
    try:
        # Poll for decision
        decision = await get_decision_by_work_item(work_item_id)
        decision_id = decision.get("id")
        primary_human_id = decision.get("primary_human_id")
        
        # Add log about decision
        system_state.add_log("INFO", f"Decision made: Assigned to {primary_human_id}")
        
        # Update incident status
        system_state.update_incident(
            work_item_id,
            status="assigned",
            assignee=primary_human_id,
            decision_made_at=decision.get("created_at")
        )
        
        # Set latest decision
        system_state.set_decision({
            "work_item_id": work_item_id,
            "primary_human_id": primary_human_id,
            "assignee_name": f"Engineer {primary_human_id[-4:]}",  # Mock name
            "confidence": decision.get("confidence", 0.0),
            "evidence": decision.get("evidence", []),
            "constraints": decision.get("constraints", []),
            "backup_human_ids": decision.get("backup_human_ids", [])
        })
        
        # Poll for Jira issue
        if decision_id:
            asyncio.create_task(poll_and_update_jira(work_item_id, decision_id))
            
    except Exception as e:
        logger.error(f"Error polling decision: {e}", exc_info=True)
        system_state.update_incident(work_item_id, status="routing")

async def poll_and_update_jira(work_item_id: str, decision_id: str):
    """Background task to poll for Jira issue."""
    try:
        # Poll for Jira issue
        action = await get_jira_issue_by_decision(decision_id)
        jira_key = action.get("jira_issue_key")
        
        if jira_key:
            # Add log about Jira creation
            system_state.add_log("INFO", f"Jira issue created: {jira_key}")
            
            # Update incident with Jira key
            system_state.update_incident(
                work_item_id,
                jira_key=jira_key,
                jira_created_at=action.get("created_at")
            )
            
    except Exception as e:
        logger.error(f"Error polling Jira issue: {e}", exc_info=True)

async def handle_normal_action(action_type: str) -> Dict[str, Any]:
    """Handle a normal (non-error) action."""
    normal_messages = [
        f"Processing requests: {150 + (hash(action_type) % 100)} requests/sec",
        f"Cache hit rate: {85 + (hash(action_type) % 10)}%",
        f"Database query latency: {50 + (hash(action_type) % 50)}ms (p50)",
        f"API endpoint serving {100 + (hash(action_type) % 200)} requests/min",
        f"Background job processed {10 + (hash(action_type) % 50)} items",
        "Health check passed: all services operational",
    ]
    
    message = normal_messages[hash(action_type) % len(normal_messages)]
    system_state.add_log("INFO", message)
    
    # Slight metric updates
    current_requests = system_state.metrics.get("requests_per_sec", 150)
    system_state.update_metric("requests_per_sec", current_requests + (hash(action_type) % 20) - 10)
    
    return {
        "success": True,
        "message": message
    }

