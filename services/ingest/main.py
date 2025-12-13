"""
Ingest Service - Single source of truth for all work items
"""
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from datetime import datetime
import logging

from pagerduty_webhook import process_pagerduty_incident_webhook, validate_pagerduty_signature

logger = logging.getLogger(__name__)

app = FastAPI(title="Ingest Service", version="0.1.0")


class WorkItemCreate(BaseModel):
    type: str
    service: str
    severity: str
    description: str
    origin_system: str
    creator_id: Optional[str] = None
    raw_log: Optional[str] = None


class WorkItemResponse(BaseModel):
    id: str
    type: str
    service: str
    severity: str
    description: str
    created_at: str
    origin_system: str


class OutcomeRequest(BaseModel):
    event_id: str
    decision_id: str
    type: str
    actor_id: str
    timestamp: str


@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ingest"}


class DemoWorkItemRequest(BaseModel):
    service: str
    severity: str
    description: str
    type: Optional[str] = "incident"
    story_points: Optional[int] = None
    impact: Optional[str] = None
    raw_log: Optional[str] = None


@app.post("/ingest/demo")
async def create_demo_work_item(request: DemoWorkItemRequest):
    """Create a demo work item for testing - simulates monitoring/observability systems"""
    work_item_id = f"wi-{datetime.now().strftime('%Y%m%d%H%M%S')}-{os.urandom(4).hex()}"
    
    work_item = {
        "work_item_id": work_item_id,
        "created_at": datetime.now().isoformat(),
        "message": "WorkItem created successfully"
    }
    
    return work_item


@app.post("/work-items", response_model=WorkItemResponse)
async def create_work_item(item: WorkItemCreate):
    """Create a new work item"""
    work_item = {
        "id": f"wi-{datetime.now().isoformat()}",
        "type": item.type,
        "service": item.service,
        "severity": item.severity,
        "description": item.description,
        "created_at": datetime.now().isoformat(),
        "origin_system": item.origin_system
    }
    return work_item


@app.get("/work-items")
async def list_work_items():
    """List all work items"""
    return {"work_items": [], "total": 0}


@app.get("/work-items/{work_item_id}")
async def get_work_item(work_item_id: str):
    """Get a specific work item"""
    return {
        "id": work_item_id,
        "type": "incident",
        "service": "api-service",
        "severity": "sev2",
        "description": "Sample work item",
        "created_at": datetime.now().isoformat()
    }


@app.post("/work-items/{work_item_id}/outcome")
async def record_outcome(work_item_id: str, outcome: OutcomeRequest):
    """Record an outcome for a work item"""
    return {"status": "recorded", "event_id": outcome.event_id}


@app.post("/webhooks/pagerduty")
async def pagerduty_webhook(request: Request):
    """
    Handle PagerDuty webhook events for incident creation (ingestion).
    
    Processes:
    - incident.triggered: New incident created → creates WorkItem
    - incident.created: Incident created → creates WorkItem
    
    This is the ingestion point: PagerDuty detects issues and creates incidents,
    which are then converted to WorkItems for the Decision Engine.
    """
    try:
        # Get signature from header (optional, for validation)
        signature = request.headers.get("X-PagerDuty-Signature")
        
        # Read request body
        body = await request.body()
        
        # Validate signature (if configured)
        if not validate_pagerduty_signature(body, signature):
            logger.warning("Invalid PagerDuty webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON payload
        webhook_data = await request.json()
        
        # Process webhook (creates WorkItem)
        result = await process_pagerduty_incident_webhook(webhook_data)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Webhook processing failed"))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process PagerDuty webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("INGEST_SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

