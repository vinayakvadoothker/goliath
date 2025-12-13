"""
Ingest Service - Single source of truth for all work items
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

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


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("INGEST_SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

