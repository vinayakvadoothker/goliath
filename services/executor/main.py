"""
Executor Service - Executes decisions by creating Jira issues
"""
import os
import json
import uuid
import logging
import asyncio
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from contextlib import asynccontextmanager

from db import execute_query, execute_update
from mappings import validate_mappings, get_jira_project, get_jira_priority, get_jira_account_id

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Request/Response Models
class Evidence(BaseModel):
    """Evidence bullet point."""
    type: str
    text: str
    time_window: Optional[str] = None
    source: Optional[str] = None


class WorkItemData(BaseModel):
    """Work item data for execution."""
    service: str
    severity: str
    description: str
    story_points: Optional[int] = None


class ExecuteDecisionRequest(BaseModel):
    """Request to execute a decision."""
    decision_id: str
    work_item_id: str
    primary_human_id: str
    backup_human_ids: List[str] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    work_item: WorkItemData
    correlation_id: Optional[str] = None


class ExecuteDecisionResponse(BaseModel):
    """Response from execution."""
    executed_action_id: str
    jira_issue_key: Optional[str] = None
    jira_issue_id: Optional[str] = None
    assigned_human_id: str
    created_at: str
    message: str
    fallback_used: bool = False


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Executor Service starting up...")
    yield
    logger.info("Executor Service shutting down...")


app = FastAPI(
    title="Executor Service",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Correlation ID middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to request if not present."""
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def format_jira_description(
    work_item: WorkItemData,
    primary_human_id: str,
    backup_human_ids: List[str],
    evidence: List[Evidence]
) -> str:
    """
    Format Jira issue description with evidence and assignment info.
    
    Args:
        work_item: Work item data
        primary_human_id: Primary assignee human ID
        backup_human_ids: Backup assignee human IDs
        evidence: List of evidence bullets
    
    Returns:
        Formatted description string
    """
    description_parts = [
        "Assigned by Goliath Decision Engine",
        "",
        f"*Primary Assignee:* {primary_human_id}",
    ]
    
    if backup_human_ids:
        description_parts.append(f"*Backup Assignees:* {', '.join(backup_human_ids)}")
    
    if evidence:
        description_parts.append("")
        description_parts.append("*Evidence:*")
        for ev in evidence:
            time_info = f" ({ev.time_window})" if ev.time_window else ""
            source_info = f" [{ev.source}]" if ev.source else ""
            description_parts.append(f"- {ev.text}{time_info}{source_info}")
    
    description_parts.append("")
    description_parts.append(f"*Original Description:*\n{work_item.description}")
    
    return "\n".join(description_parts)


def get_jira_config() -> Tuple[str, Dict[str, str]]:
    """
    Get Jira URL and authentication headers.
    
    Supports both real Jira (with API keys) and Jira Simulator (no auth).
    
    Returns:
        Tuple of (jira_url, headers)
    """
    # Check if using real Jira
    jira_url = os.getenv("JIRA_URL", "").rstrip("/")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_key = os.getenv("JIRA_API_KEY")
    
    # If real Jira credentials provided, use them
    if jira_url and jira_email and jira_api_key:
        logger.info(f"Using real Jira: {jira_url}")
        credentials = f"{jira_email}:{jira_api_key}"
        encoded = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        return jira_url, headers
    
    # Otherwise, use Jira Simulator (no auth)
    jira_url = os.getenv("JIRA_SIMULATOR_URL", "http://localhost:8080")
    logger.info(f"Using Jira Simulator: {jira_url}")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return jira_url, headers


async def create_jira_issue_with_retry(
    jira_issue: Dict[str, Any],
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Create Jira issue with exponential backoff retry.
    
    Supports both real Jira (with API keys) and Jira Simulator (no auth).
    
    Args:
        jira_issue: Jira issue payload
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds for exponential backoff
    
    Returns:
        Jira API response
    
    Raises:
        httpx.HTTPError: If all retries fail
    """
    jira_url, headers = get_jira_config()
    timeout = httpx.Timeout(10.0, connect=5.0)
    
    last_error = None
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{jira_url}/rest/api/3/issue",
                    json=jira_issue,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    f"Jira API call failed (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"Jira API call failed after {max_retries} attempts: {e}")
                raise
    
    raise last_error


def store_executed_action(
    executed_action_id: str,
    decision_id: str,
    assigned_human_id: str,
    backup_human_ids: List[str],
    jira_issue_key: Optional[str] = None,
    jira_issue_id: Optional[str] = None,
    fallback_message: Optional[str] = None,
    slack_message_id: Optional[str] = None
) -> None:
    """
    Store executed action in database.
    
    Args:
        executed_action_id: Unique action ID
        decision_id: Decision ID
        assigned_human_id: Assigned human ID
        backup_human_ids: Backup human IDs
        jira_issue_key: Jira issue key (if created)
        jira_issue_id: Jira issue ID (if created)
        fallback_message: Fallback message (if execution failed)
        slack_message_id: Slack message ID (if sent)
    """
    try:
        query = """
            INSERT INTO executed_actions (
                id, decision_id, jira_issue_key, jira_issue_id,
                assigned_human_id, backup_human_ids, created_at,
                fallback_message, slack_message_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = [
            executed_action_id,
            decision_id,
            jira_issue_key,
            jira_issue_id,
            assigned_human_id,
            json.dumps(backup_human_ids),
            datetime.now(),
            fallback_message,
            slack_message_id,
        ]
        execute_update(query, params)
        logger.info(f"Stored executed action: {executed_action_id}")
    except Exception as e:
        logger.error(f"Failed to store executed action: {e}", exc_info=True)
        raise


def update_work_item_jira_key(work_item_id: str, jira_issue_key: str) -> None:
    """
    Update work item with Jira issue key.
    
    Args:
        work_item_id: Work item ID
        jira_issue_key: Jira issue key
    """
    try:
        query = "UPDATE work_items SET jira_issue_key = %s WHERE id = %s"
        execute_update(query, [jira_issue_key, work_item_id])
        logger.info(f"Updated work_item {work_item_id} with jira_issue_key {jira_issue_key}")
    except Exception as e:
        logger.warning(f"Failed to update work_item jira_issue_key: {e}")


@app.get("/healthz")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "executor"}


@app.get("/executed_actions")
async def get_executed_actions(decision_id: Optional[str] = None):
    """Get executed actions, optionally filtered by decision_id."""
    try:
        if decision_id:
            query = "SELECT * FROM executed_actions WHERE decision_id = %s ORDER BY created_at DESC"
            actions = execute_query(query, [decision_id])
        else:
            query = "SELECT * FROM executed_actions ORDER BY created_at DESC LIMIT 100"
            actions = execute_query(query)
        
        return actions
    except Exception as e:
        logger.error(f"Failed to get executed actions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/executeDecision", response_model=ExecuteDecisionResponse)
async def execute_decision(request: ExecuteDecisionRequest, req: Request):
    """
    Execute a decision by creating a Jira issue.
    
    This endpoint:
    1. Validates all mappings (service→project, severity→priority, human→accountId)
    2. Creates Jira issue via Jira Simulator API with retry logic
    3. Stores executed action in database
    4. Links Jira issue back to work item
    5. Falls back to database storage if Jira fails
    
    Args:
        request: Execution request
        req: FastAPI request object
    
    Returns:
        Execution response with Jira issue details
    """
    correlation_id = getattr(req.state, "correlation_id", str(uuid.uuid4()))
    executed_action_id = generate_id()
    
    logger.info(
        f"Executing decision {request.decision_id} "
        f"(correlation_id: {correlation_id}, action_id: {executed_action_id})"
    )
    
    try:
        return await _execute_jira(request, executed_action_id)
    
    except ValueError as e:
        logger.error(f"Validation error for decision {request.decision_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error executing decision {request.decision_id}: {e}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Failed to execute decision: {str(e)}")


async def _execute_jira(request: ExecuteDecisionRequest, executed_action_id: str) -> ExecuteDecisionResponse:
    """Execute decision by creating Jira issue."""
    # Validate all mappings before execution
    jira_project, jira_priority, jira_account_id = validate_mappings(
        request.work_item.service,
        request.work_item.severity,
        request.primary_human_id
    )
    
    logger.info(
        f"Mappings validated: service={request.work_item.service}→{jira_project}, "
        f"severity={request.work_item.severity}→{jira_priority}, "
        f"human={request.primary_human_id}→{jira_account_id}"
    )
    
    # Format Jira issue description
    description = format_jira_description(
        request.work_item,
        request.primary_human_id,
        request.backup_human_ids,
        request.evidence
    )
    
    # Build Jira issue payload
    jira_issue = {
        "fields": {
            "project": {"key": jira_project},
            "summary": request.work_item.description[:255],  # Jira summary max length
            "description": description,
            "issuetype": {"name": "Bug"},
            "priority": {"name": jira_priority},
            "assignee": {"accountId": jira_account_id},
        }
    }
    
    # Add story points if provided
    if request.work_item.story_points:
        jira_issue["fields"]["customfield_10016"] = request.work_item.story_points
    
    # Try to create Jira issue with retry
    try:
        jira_response = await create_jira_issue_with_retry(jira_issue)
        jira_issue_key = jira_response["key"]
        jira_issue_id = jira_response["id"]
        
        logger.info(
            f"Jira issue created successfully: {jira_issue_key} "
            f"(decision_id: {request.decision_id})"
        )
        
        # Store executed action
        store_executed_action(
            executed_action_id,
            request.decision_id,
            request.primary_human_id,
            request.backup_human_ids,
            jira_issue_key=jira_issue_key,
            jira_issue_id=jira_issue_id,
        )
        
        # Link back to work item
        update_work_item_jira_key(request.work_item_id, jira_issue_key)
        
        return ExecuteDecisionResponse(
            executed_action_id=executed_action_id,
            jira_issue_key=jira_issue_key,
            jira_issue_id=jira_issue_id,
            assigned_human_id=request.primary_human_id,
            created_at=datetime.now().isoformat(),
            message="Jira issue created successfully",
            fallback_used=False,
        )
    
    except Exception as jira_error:
        # Fallback: store rendered message in database
        logger.error(
            f"Jira API failed for decision {request.decision_id}: {jira_error}. "
            f"Using fallback storage."
        )
        
        fallback_message = (
            f"Jira Issue Creation Failed\n\n"
            f"Decision ID: {request.decision_id}\n"
            f"Work Item ID: {request.work_item_id}\n"
            f"Service: {request.work_item.service}\n"
            f"Severity: {request.work_item.severity}\n"
            f"Primary Assignee: {request.primary_human_id}\n"
            f"Backup Assignees: {', '.join(request.backup_human_ids) if request.backup_human_ids else 'None'}\n\n"
            f"Description:\n{request.work_item.description}\n\n"
            f"Evidence:\n" + "\n".join([f"- {ev.text}" for ev in request.evidence])
        )
        
        # Store executed action with fallback message
        store_executed_action(
            executed_action_id,
            request.decision_id,
            request.primary_human_id,
            request.backup_human_ids,
            fallback_message=fallback_message,
        )
        
        return ExecuteDecisionResponse(
            executed_action_id=executed_action_id,
            jira_issue_key=None,
            jira_issue_id=None,
            assigned_human_id=request.primary_human_id,
            created_at=datetime.now().isoformat(),
            message="Jira issue creation failed, stored in database as fallback",
            fallback_used=True,
            execution_target="jira",
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("EXECUTOR_SERVICE_PORT", "8004"))
    uvicorn.run(app, host="0.0.0.0", port=port)
