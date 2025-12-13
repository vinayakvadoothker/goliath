"""
Learner Service - Capability profiles and learning loop
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
from datetime import datetime

from db import (
    get_service_stats,
    get_human_stats,
    get_or_create_human
)
from stats_service import calculate_fit_score
from outcome_service import process_outcome as process_outcome_service
from jira_client import (
    get_all_closed_tickets,
    get_user_story_points,
    get_user_resolved_by_severity,
    get_user_on_call_status
)

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Learner Service", version="0.1.0")


# Request/Response Models
class OutcomeRequest(BaseModel):
    event_id: str
    decision_id: Optional[str] = None
    work_item_id: str
    type: str  # "resolved", "reassigned", "escalated"
    actor_id: str
    service: str
    timestamp: str  # ISO 8601
    new_assignee_id: Optional[str] = None


class SyncJiraRequest(BaseModel):
    project: Optional[str] = None
    days_back: int = 90


@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "learner"}


@app.get("/profiles")
async def get_profiles(service: str = Query(..., description="Service name")):
    """
    Get human profiles for a service with full stats.
    
    Returns humans with fit_score, resolves, transfers, load metrics, story points, and severity breakdown.
    """
    if not service:
        raise HTTPException(status_code=400, detail="service parameter is required")
    
    try:
        # Get service stats from database
        stats_list = get_service_stats(service, days=90)
        
        # Get jira_account_id for each human
        from db import execute_query
        human_ids = [s["human_id"] for s in stats_list]
        jira_account_map = {}
        if human_ids:
            placeholders = ",".join(["%s"] * len(human_ids))
            jira_query = f"SELECT id, jira_account_id FROM humans WHERE id IN ({placeholders})"
            jira_results = execute_query(jira_query, human_ids)
            jira_account_map = {r["id"]: r.get("jira_account_id") for r in jira_results}
        
        humans = []
        for stats in stats_list:
            human_id = stats["human_id"]
            display_name = stats["display_name"]
            
            # Calculate current fit_score (with decay)
            fit_score = calculate_fit_score(human_id, service, stats)
            
            # Get load data
            from db import get_or_create_load
            load = get_or_create_load(human_id)
            pages_7d = load.get("pages_7d", 0)
            active_items = load.get("active_items", 0)
            
            # Get story points from Jira Simulator
            jira_account_id = jira_account_map.get(human_id)
            story_points_data = {"max_story_points": 21, "current_story_points": 0}
            resolved_by_severity = {"sev1": 0, "sev2": 0, "sev3": 0, "sev4": 0}
            on_call = False
            
            if jira_account_id:
                try:
                    story_points_data = await get_user_story_points(jira_account_id)
                    resolved_by_severity = await get_user_resolved_by_severity(jira_account_id, service, days=90)
                    on_call = await get_user_on_call_status(jira_account_id)
                except Exception as e:
                    logger.warning(f"Failed to get Jira data for {human_id}: {e}")
            
            humans.append({
                "human_id": human_id,
                "display_name": display_name,
                "fit_score": fit_score,
                "resolves_count": stats.get("resolves_count", 0),
                "transfers_count": stats.get("transfers_count", 0),
                "last_resolved_at": stats.get("last_resolved_at").isoformat() if stats.get("last_resolved_at") else None,
                "on_call": on_call,
                "pages_7d": pages_7d,
                "active_items": active_items,
                "max_story_points": story_points_data.get("max_story_points", 21),
                "current_story_points": story_points_data.get("current_story_points", 0),
                "resolved_by_severity": resolved_by_severity
            })
        
        # Sort by fit_score descending
        humans.sort(key=lambda x: x["fit_score"], reverse=True)
        
        return {
            "service": service,
            "humans": humans
        }
    
    except Exception as e:
        logger.error(f"Failed to get profiles for service {service}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/outcomes")
async def process_outcome_endpoint(outcome: OutcomeRequest):
    """
    Process an outcome (learning loop).
    
    This is THE core learning mechanism:
    - Resolved → fit_score increases (+0.1), resolves_count increases
    - Reassigned → fit_score decreases (-0.15), transfers_count increases
    
    Idempotent: same event_id = no duplicate update.
    """
    try:
        outcome_dict = outcome.dict()
        result = process_outcome_service(outcome_dict)
        
        if not result.get("processed"):
            # Already processed
            return {
                "processed": False,
                "event_id": result.get("event_id"),
                "message": "Outcome already processed"
            }
        
        return result
    
    except ValueError as e:
        logger.error(f"Invalid outcome request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process outcome: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/stats")
async def get_stats_endpoint(human_id: str = Query(..., description="Human ID")):
    """
    Get stats for a human (for UI display).
    
    Returns all service stats and load data for a human.
    """
    if not human_id:
        raise HTTPException(status_code=400, detail="human_id parameter is required")
    
    try:
        stats = get_human_stats(human_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail=f"Human {human_id} not found")
        
        return stats
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stats for human {human_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/sync/jira")
async def sync_jira_endpoint(request: Optional[SyncJiraRequest] = None):
    """
    Sync closed Jira tickets to build capability profiles.
    
    Reads closed tickets from Jira Simulator and updates human capability profiles.
    """
    project = request.project if request else None
    days_back = request.days_back if request else 90
    
    try:
        # Get all closed tickets from Jira Simulator
        logger.info(f"Syncing Jira tickets (project={project}, days_back={days_back})")
        closed_tickets = await get_all_closed_tickets(project=project, days_back=days_back)
        
        synced_count = 0
        humans_updated = set()
        
        # Map Jira priority to severity
        priority_to_severity = {
            "Critical": "sev1",
            "High": "sev2",
            "Medium": "sev3",
            "Low": "sev4"
        }
        
        for issue in closed_tickets:
            try:
                fields = issue.get("fields", {})
                assignee = fields.get("assignee")
                
                if not assignee:
                    continue
                
                account_id = assignee.get("accountId")
                display_name = assignee.get("displayName", "")
                project_key = fields.get("project", {}).get("key", "")
                resolution_date = fields.get("resolutiondate")
                priority_name = fields.get("priority", {}).get("name", "Low")
                
                if not account_id or not project_key:
                    continue
                
                # Get or create human
                human = get_or_create_human(
                    human_id=account_id,
                    display_name=display_name,
                    jira_account_id=account_id
                )
                
                # Parse resolution date
                resolved_at = None
                if resolution_date:
                    try:
                        resolved_at = datetime.fromisoformat(resolution_date.replace('Z', '+00:00'))
                        if resolved_at.tzinfo:
                            resolved_at = resolved_at.replace(tzinfo=None)
                    except Exception:
                        pass
                
                # Update stats
                from db import get_or_create_stats, update_stats
                stats = get_or_create_stats(account_id, project_key)
                
                # Calculate initial fit_score based on resolve count + recency
                resolves_count = stats.get("resolves_count", 0) + 1
                
                # Update stats
                update_stats(
                    human_id=account_id,
                    service=project_key,
                    resolves_count_delta=1,
                    last_resolved_at=resolved_at or datetime.now()
                )
                
                # Track resolved_by_severity (stored in a separate table or calculated on demand)
                # For now, we'll calculate it on demand in get_profiles
                
                humans_updated.add(account_id)
                synced_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to process ticket {issue.get('key', 'unknown')}: {e}")
                continue
        
        logger.info(f"Jira sync completed: {synced_count} tickets synced, {len(humans_updated)} humans updated")
        
        return {
            "synced": synced_count,
            "humans_updated": len(humans_updated),
            "message": "Sync completed successfully"
        }
    
    except Exception as e:
        logger.error(f"Failed to sync Jira: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("LEARNER_SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
