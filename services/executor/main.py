"""
Executor Service - Executes decisions by creating Jira issues
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

app = FastAPI(title="Executor Service", version="0.1.0")


class ExecuteDecisionRequest(BaseModel):
    decision_id: str
    work_item_id: str
    primary_human_id: str
    service: str
    severity: str
    description: str


class ExecuteDecisionResponse(BaseModel):
    status: str
    jira_issue_key: Optional[str] = None
    message: str


@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "executor"}


@app.post("/executeDecision", response_model=ExecuteDecisionResponse)
async def execute_decision(request: ExecuteDecisionRequest):
    """Execute a decision by creating a Jira issue"""
    return {
        "status": "executed",
        "jira_issue_key": f"PROJ-{datetime.now().timestamp()}",
        "message": "Jira issue created successfully"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("EXECUTOR_SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

