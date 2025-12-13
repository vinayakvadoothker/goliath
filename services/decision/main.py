"""
Decision Service - Core decision engine
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
from datetime import datetime

from decision_engine import make_decision
from db import get_decision, get_decision_candidates, get_constraint_results

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Decision Service", version="0.1.0")


class DecisionRequest(BaseModel):
    work_item_id: str
    service: Optional[str] = None  # Optional, will be retrieved from work item
    severity: Optional[str] = None  # Optional, will be retrieved from work item


class ConstraintResult(BaseModel):
    name: str
    passed: bool
    reason: Optional[str] = None


class DecisionResponse(BaseModel):
    id: str
    work_item_id: str
    primary_human_id: str
    backup_human_ids: List[str]
    confidence: float
    constraints_checked: List[ConstraintResult]
    created_at: str


@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "decision"}


@app.post("/decide", response_model=DecisionResponse)
async def decide(request: DecisionRequest):
    """
    Make a decision for a work item.
    
    This is the core decision engine that:
    1. Retrieves work item from database
    2. Gets candidates from Learner Service
    3. Applies constraint filtering
    4. Scores candidates (fit_score + vector similarity + capacity)
    5. Selects primary + backups
    6. Stores decision + audit trail
    """
    try:
        decision = await make_decision(request.work_item_id)
        
        # Get constraint results
        constraint_results = get_constraint_results(decision["id"])
        constraints_checked = [
            ConstraintResult(
                name=cr["constraint_name"],
                passed=cr["passed"],
                reason=cr.get("reason")
            )
            for cr in constraint_results
        ]
        
        return DecisionResponse(
            id=decision["id"],
            work_item_id=decision["work_item_id"],
            primary_human_id=decision["primary_human_id"],
            backup_human_ids=decision["backup_human_ids"],
            confidence=decision["confidence"],
            constraints_checked=constraints_checked,
            created_at=decision["created_at"]
        )
    
    except ValueError as e:
        logger.error(f"Decision failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Decision engine error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Decision engine failed: {str(e)}")


@app.get("/decisions/{work_item_id}")
async def get_decision_endpoint(work_item_id: str):
    """Get decision for a work item."""
    try:
        decision = get_decision(work_item_id)
        if not decision:
            raise HTTPException(status_code=404, detail=f"Decision not found for work_item {work_item_id}")
        
        # Get constraint results
        constraint_results = get_constraint_results(decision["id"])
        constraints_checked = [
            {
                "name": cr["constraint_name"],
                "passed": cr["passed"],
                "reason": cr.get("reason")
            }
            for cr in constraint_results
        ]
        
        return {
            "id": decision["id"],
            "work_item_id": decision["work_item_id"],
            "primary_human_id": decision["primary_human_id"],
            "backup_human_ids": decision["backup_human_ids"],
            "confidence": decision["confidence"],
            "constraints_checked": constraints_checked,
            "created_at": decision["created_at"].isoformat() if hasattr(decision["created_at"], 'isoformat') else str(decision["created_at"])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get decision failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get decision: {str(e)}")


@app.get("/audit/{work_item_id}")
async def get_audit_trail(work_item_id: str):
    """
    Get full audit trail for a decision.
    
    Returns:
    - Decision details
    - All candidates with scores and filter reasons
    - Constraint results
    - Score breakdowns
    """
    try:
        decision = get_decision(work_item_id)
        if not decision:
            raise HTTPException(status_code=404, detail=f"Decision not found for work_item {work_item_id}")
        
        # Get all candidates (audit trail)
        candidates = get_decision_candidates(decision["id"])
        
        # Get constraint results
        constraint_results = get_constraint_results(decision["id"])
        
        return {
            "work_item_id": work_item_id,
            "decision_id": decision["id"],
            "decision": {
                "primary_human_id": decision["primary_human_id"],
                "backup_human_ids": decision["backup_human_ids"],
                "confidence": decision["confidence"],
                "created_at": decision["created_at"].isoformat() if hasattr(decision["created_at"], 'isoformat') else str(decision["created_at"])
            },
            "candidates": candidates,
            "constraints": [
                {
                    "name": cr["constraint_name"],
                    "passed": cr["passed"],
                    "reason": cr.get("reason")
                }
                for cr in constraint_results
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get audit trail failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get audit trail: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DECISION_SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
