"""
Decision Service - Core decision engine
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime

app = FastAPI(title="Decision Service", version="0.1.0")


class DecisionRequest(BaseModel):
    work_item_id: str
    service: str
    severity: str


class DecisionResponse(BaseModel):
    id: str
    work_item_id: str
    primary_human_id: str
    backup_human_ids: List[str]
    confidence: float
    created_at: str


@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "decision"}


@app.post("/decide", response_model=DecisionResponse)
async def make_decision(request: DecisionRequest):
    """Make a decision for a work item"""
    decision = {
        "id": f"dec-{datetime.now().isoformat()}",
        "work_item_id": request.work_item_id,
        "primary_human_id": "human-1",
        "backup_human_ids": ["human-2", "human-3"],
        "confidence": 0.85,
        "created_at": datetime.now().isoformat()
    }
    return decision


@app.get("/decisions/{work_item_id}")
async def get_decision(work_item_id: str):
    """Get decision for a work item"""
    return {
        "id": f"dec-{work_item_id}",
        "work_item_id": work_item_id,
        "primary_human_id": "human-1",
        "backup_human_ids": ["human-2"],
        "confidence": 0.85,
        "created_at": datetime.now().isoformat()
    }


@app.get("/audit/{work_item_id}")
async def get_audit_trail(work_item_id: str):
    """Get full audit trail for a decision"""
    return {
        "work_item_id": work_item_id,
        "decision_id": f"dec-{work_item_id}",
        "audit_trail": []
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DECISION_SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

