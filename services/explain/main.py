"""
Explain Service - Generates contextual evidence bullets
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from datetime import datetime

app = FastAPI(title="Explain Service", version="0.1.0")


class ExplainDecisionRequest(BaseModel):
    decision_id: str
    work_item_id: str
    primary_human_id: str
    backup_human_ids: List[str]
    service: str
    severity: str


class Evidence(BaseModel):
    type: str
    text: str
    time_window: str
    source: str


class ExplainDecisionResponse(BaseModel):
    decision_id: str
    evidence: List[Evidence]
    constraints: List[dict]
    why_not_next_best: str


@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "explain"}


@app.post("/explainDecision", response_model=ExplainDecisionResponse)
async def explain_decision(request: ExplainDecisionRequest):
    """Generate evidence bullets for a decision"""
    return {
        "decision_id": request.decision_id,
        "evidence": [
            {
                "type": "recent_resolution",
                "text": "Resolved 3 similar incidents in the last 7 days",
                "time_window": "last 7 days",
                "source": "Learner stats"
            }
        ],
        "constraints": [
            {
                "name": "capacity",
                "passed": True,
                "reason": "Within story point limit"
            }
        ],
        "why_not_next_best": "Primary candidate has higher fit_score and lower current load"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("EXPLAIN_SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

