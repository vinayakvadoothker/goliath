"""
Jira Simulator - Full Jira REST API v3 mock
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime

app = FastAPI(title="Jira Simulator", version="0.1.0")


class Issue(BaseModel):
    id: str
    key: str
    fields: dict


class SearchResponse(BaseModel):
    issues: List[Issue]
    total: int
    startAt: int
    maxResults: int


@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "jira-simulator"}


@app.get("/rest/api/3/search")
async def search_issues(
    jql: str = Query(..., description="JQL query"),
    startAt: int = Query(0, ge=0),
    maxResults: int = Query(50, ge=1, le=100)
):
    """JQL search endpoint"""
    return {
        "issues": [],
        "total": 0,
        "startAt": startAt,
        "maxResults": maxResults
    }


@app.post("/rest/api/3/issue")
async def create_issue(issue: dict):
    """Create a Jira issue"""
    return {
        "id": f"issue-{datetime.now().timestamp()}",
        "key": f"PROJ-{datetime.now().timestamp()}",
        "self": "http://localhost:8080/rest/api/3/issue/PROJ-1"
    }


@app.get("/rest/api/3/issue/{issue_key}")
async def get_issue(issue_key: str):
    """Get a Jira issue"""
    return {
        "id": f"issue-{issue_key}",
        "key": issue_key,
        "fields": {
            "summary": "Sample issue",
            "status": {"name": "To Do"},
            "assignee": {"accountId": "557058:12345"}
        }
    }


@app.put("/rest/api/3/issue/{issue_key}")
async def update_issue(issue_key: str, update: dict):
    """Update a Jira issue"""
    return {"status": "updated"}


@app.get("/rest/api/3/user/search")
async def search_users(query: Optional[str] = None):
    """Search users"""
    return [
        {
            "accountId": "557058:12345",
            "displayName": "John Doe",
            "emailAddress": "john@example.com"
        }
    ]


@app.get("/rest/api/3/project")
async def list_projects():
    """List projects"""
    return [
        {
            "key": "API",
            "name": "api-service",
            "projectTypeKey": "software"
        }
    ]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("JIRA_SIMULATOR_PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)

