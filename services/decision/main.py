"""
Decision Service - Core decision engine
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
import httpx
from datetime import datetime

from decision_engine import make_decision
from db import get_decision, get_decision_candidates, get_constraint_results, get_work_item

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
        
        # AUTOMATIC ORCHESTRATION: Trigger Explain + Executor
        explain_url = os.getenv("EXPLAIN_SERVICE_URL", "http://explain:8000")
        executor_url = os.getenv("EXECUTOR_SERVICE_URL", "http://executor:8000")
        
        try:
            # Get WorkItem details for Explain and Executor
            work_item = get_work_item(request.work_item_id)
            if not work_item:
                logger.warning(f"WorkItem {request.work_item_id} not found for orchestration")
            else:
                # Get decision candidates for Explain Service (with service for proper stats)
                candidates = get_decision_candidates(decision["id"], service=work_item["service"])
                primary_candidate = next((c for c in candidates if c["human_id"] == decision["primary_human_id"]), None)
                backup_candidates = [c for c in candidates if c["human_id"] in decision["backup_human_ids"]]
                
                # Convert candidates to Explain Service format
                def format_candidate_features(candidate):
                    """Convert candidate dict to Explain Service CandidateFeature format."""
                    if not candidate:
                        return {}
                    # Get similar_incident_score from score_breakdown if available
                    score_breakdown = candidate.get("score_breakdown", {})
                    similar_incident_score = score_breakdown.get("vector_similarity") if isinstance(score_breakdown, dict) else None
                    
                    return {
                        "human_id": candidate.get("human_id", ""),
                        "display_name": candidate.get("display_name", "Unknown"),
                        "fit_score": float(candidate.get("fit_score", 0.5)),
                        "resolves_count": int(candidate.get("resolves_count", 0)),
                        "transfers_count": int(candidate.get("transfers_count", 0)),
                        "last_resolved_at": candidate.get("last_resolved_at"),
                        "on_call": candidate.get("on_call", False),  # Will be False if not available
                        "pages_7d": int(candidate.get("pages_7d", 0)),
                        "active_items": int(candidate.get("active_items", 0)),
                        "similar_incident_score": similar_incident_score,
                        "score_breakdown": score_breakdown
                    }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Step 1: Get evidence from Explain Service
                    evidence = []
                    try:
                        logger.info(f"Calling Explain Service for decision {decision['id']}")
                        explain_request = {
                            "decision_id": decision["id"],
                            "work_item": {
                                "id": work_item["id"],
                                "service": work_item["service"],
                                "severity": work_item["severity"],
                                "description": work_item["description"],
                                "type": work_item.get("type", "incident")
                            },
                            "primary_human_id": decision["primary_human_id"],
                            "primary_features": format_candidate_features(primary_candidate),
                            "backup_human_ids": decision["backup_human_ids"],
                            "backup_features": [format_candidate_features(c) for c in backup_candidates],
                            "constraints_checked": [
                                {
                                    "name": cr["constraint_name"],
                                    "passed": cr["passed"],
                                    "reason": cr.get("reason")
                                }
                                for cr in constraint_results
                            ]
                        }
                        
                        explain_response = await client.post(
                            f"{explain_url}/explainDecision",
                            json=explain_request
                        )
                        explain_response.raise_for_status()
                        explain_result = explain_response.json()
                        evidence = explain_result.get("evidence", [])
                        logger.info(f"Explain Service returned {len(evidence)} evidence bullets")
                    except httpx.RequestError as e:
                        logger.warning(f"Explain Service failed (network error): {e}. Continuing without evidence.")
                    except httpx.HTTPStatusError as e:
                        logger.warning(f"Explain Service failed (HTTP {e.response.status_code}): {e.response.text}. Continuing without evidence.")
                    except Exception as e:
                        logger.warning(f"Explain Service failed (unexpected error): {e}. Continuing without evidence.")
                    
                    # Step 2: Execute decision via Executor Service
                    try:
                        logger.info(f"Calling Executor Service for decision {decision['id']}")
                        executor_request = {
                            "decision_id": decision["id"],
                            "work_item_id": request.work_item_id,
                            "primary_human_id": decision["primary_human_id"],
                            "backup_human_ids": decision["backup_human_ids"],
                            "evidence": evidence,
                            "work_item": {
                                "service": work_item["service"],
                                "severity": work_item["severity"],
                                "description": work_item["description"],
                                "story_points": work_item.get("story_points")
                            }
                        }
                        
                        executor_response = await client.post(
                            f"{executor_url}/executeDecision",
                            json=executor_request
                        )
                        executor_response.raise_for_status()
                        executor_result = executor_response.json()
                        jira_key = executor_result.get("jira_issue_key")
                        if jira_key:
                            logger.info(f"Executor Service created Jira issue: {jira_key}")
                        else:
                            logger.warning(f"Executor Service completed but no Jira issue key returned (fallback used?)")
                    except httpx.RequestError as e:
                        logger.warning(f"Executor Service failed (network error): {e}. Decision made but not executed.")
                    except httpx.HTTPStatusError as e:
                        logger.warning(f"Executor Service failed (HTTP {e.response.status_code}): {e.response.text}. Decision made but not executed.")
                    except Exception as e:
                        logger.warning(f"Executor Service failed (unexpected error): {e}. Decision made but not executed.")
        except Exception as e:
            logger.warning(f"Orchestration failed: {e}. Decision made but Explain/Executor not called.")
        
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
        # Get service from work_item for proper stats
        work_item = get_work_item(work_item_id)
        service = work_item.get("service") if work_item else None
        candidates = get_decision_candidates(decision["id"], service=service)
        
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
