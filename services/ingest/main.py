"""
Ingest Service - Single source of truth for all work items
"""
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import uuid
from datetime import datetime
import logging
import httpx

from pagerduty_webhook import process_pagerduty_incident_webhook, validate_pagerduty_signature
from db import execute_query, execute_update
from embedding_utils import generate_embedding, pca_reduce
from weaviate_client import store_work_item
from llm_client import llm_preprocess_log

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Ingest Service", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    decision_id: Optional[str] = None
    type: str
    actor_id: str
    timestamp: str
    new_assignee_id: Optional[str] = None


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
    """
    Create a demo work item for testing - simulates monitoring/observability systems.
    
    This is the PRIMARY SOURCE for MVP - all WorkItems flow through here.
    Processing:
    1. LLM preprocess description (if raw_log provided)
    2. Generate embedding
    3. Reduce to 3D for visualization
    4. Store in PostgreSQL
    5. Store in Weaviate (for vector similarity search)
    """
    try:
        # Generate WorkItem ID
        work_item_id = f"wi-{uuid.uuid4().hex[:12]}"
        created_at = datetime.now()
        
        # LLM preprocess description if raw_log provided
        if request.raw_log:
            cleaned_description = await llm_preprocess_log(request.raw_log, request.service)
        else:
            cleaned_description = request.description
        
        # Generate embedding
        embedding = generate_embedding(cleaned_description)
        
        # Reduce to 3D for visualization
        embedding_3d = pca_reduce(embedding)
        
        # Store in PostgreSQL
        execute_update("""
            INSERT INTO work_items (
                id, type, service, severity, description, raw_log,
                embedding_3d_x, embedding_3d_y, embedding_3d_z,
                created_at, origin_system, story_points, impact
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            work_item_id,
            request.type or "incident",
            request.service,
            request.severity,
            cleaned_description,
            request.raw_log,
            embedding_3d[0],
            embedding_3d[1],
            embedding_3d[2],
            created_at,
            "demo",
            request.story_points,
            request.impact
        ])
        
        # Store in Weaviate (for vector similarity search)
        store_work_item(
            work_item_id=work_item_id,
            description=cleaned_description,
            service=request.service,
            severity=request.severity,
            embedding=embedding
        )
        
        logger.info(f"Created WorkItem {work_item_id} for service {request.service}")
        
        # AUTOMATIC ORCHESTRATION: Trigger decision making
        decision_url = os.getenv("DECISION_SERVICE_URL", "http://decision:8000")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Triggering decision for WorkItem {work_item_id}")
                decision_response = await client.post(
                    f"{decision_url}/decide",
                    json={"work_item_id": work_item_id}
                )
                decision_response.raise_for_status()
                decision = decision_response.json()
                logger.info(f"Decision made successfully: {decision.get('id')} (primary: {decision.get('primary_human_id')})")
        except httpx.RequestError as e:
            logger.warning(f"Failed to trigger decision (network error): {e}. WorkItem created but not routed.")
        except httpx.HTTPStatusError as e:
            logger.warning(f"Failed to trigger decision (HTTP {e.response.status_code}): {e.response.text}. WorkItem created but not routed.")
        except Exception as e:
            logger.warning(f"Failed to trigger decision (unexpected error): {e}. WorkItem created but not routed.")
        
        return {
            "work_item_id": work_item_id,
            "created_at": created_at.isoformat(),
            "message": "WorkItem created successfully"
        }
    except Exception as e:
        logger.error(f"Failed to create WorkItem: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create WorkItem: {str(e)}")


@app.post("/work-items", response_model=WorkItemResponse)
async def create_work_item(item: WorkItemCreate):
    """Create a new work item (manual creation from UI)"""
    try:
        # Generate WorkItem ID
        work_item_id = f"wi-{uuid.uuid4().hex[:12]}"
        created_at = datetime.now()
        
        # LLM preprocess description if raw_log provided
        if item.raw_log:
            cleaned_description = await llm_preprocess_log(item.raw_log, item.service)
        else:
            cleaned_description = item.description
        
        # Generate embedding
        embedding = generate_embedding(cleaned_description)
        
        # Reduce to 3D for visualization
        embedding_3d = pca_reduce(embedding)
        
        # Store in PostgreSQL
        execute_update("""
            INSERT INTO work_items (
                id, type, service, severity, description, raw_log,
                embedding_3d_x, embedding_3d_y, embedding_3d_z,
                created_at, origin_system, creator_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            work_item_id,
            item.type,
            item.service,
            item.severity,
            cleaned_description,
            item.raw_log,
            embedding_3d[0],
            embedding_3d[1],
            embedding_3d[2],
            created_at,
            item.origin_system,
            item.creator_id
        ])
        
        # Store in Weaviate
        store_work_item(
            work_item_id=work_item_id,
            description=cleaned_description,
            service=item.service,
            severity=item.severity,
            embedding=embedding
        )
        
        logger.info(f"Created WorkItem {work_item_id} from {item.origin_system}")
        
        return {
            "id": work_item_id,
            "type": item.type,
            "service": item.service,
            "severity": item.severity,
            "description": cleaned_description,
            "created_at": created_at.isoformat(),
            "origin_system": item.origin_system
        }
    except Exception as e:
        logger.error(f"Failed to create WorkItem: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create WorkItem: {str(e)}")


@app.get("/work-items")
async def list_work_items(
    service: Optional[str] = Query(None, description="Filter by service"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """List all work items with optional filtering"""
    try:
        # Build query
        where_clauses = []
        params = []
        
        if service:
            where_clauses.append("service = %s")
            params.append(service)
        
        if severity:
            where_clauses.append("severity = %s")
            params.append(severity)
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM work_items {where_sql}"
        count_result = execute_query(count_query, params)
        total = count_result[0]["total"] if count_result else 0
        
        # Get work items
        query = f"""
            SELECT id, type, service, severity, description, created_at, origin_system,
                   jira_issue_key, story_points, impact
            FROM work_items
            {where_sql}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        work_items = execute_query(query, params)
        
        return {
            "work_items": [
                {
                    "id": item["id"],
                    "type": item["type"],
                    "service": item["service"],
                    "severity": item["severity"],
                    "description": item["description"],
                    "created_at": item["created_at"].isoformat() if isinstance(item["created_at"], datetime) else item["created_at"],
                    "origin_system": item["origin_system"],
                    "jira_issue_key": item.get("jira_issue_key"),
                    "story_points": item.get("story_points"),
                    "impact": item.get("impact")
                }
                for item in work_items
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to list work items: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list work items: {str(e)}")


@app.get("/work-items/{work_item_id}")
async def get_work_item(work_item_id: str):
    """Get a specific work item by ID"""
    try:
        results = execute_query("""
            SELECT id, type, service, severity, description, raw_log,
                   created_at, origin_system, creator_id, jira_issue_key,
                   story_points, impact
            FROM work_items
            WHERE id = %s
        """, [work_item_id])
        
        if not results:
            raise HTTPException(status_code=404, detail=f"WorkItem {work_item_id} not found")
        
        item = results[0]
        
        return {
            "id": item["id"],
            "type": item["type"],
            "service": item["service"],
            "severity": item["severity"],
            "description": item["description"],
            "raw_log": item.get("raw_log"),
            "created_at": item["created_at"].isoformat() if isinstance(item["created_at"], datetime) else item["created_at"],
            "origin_system": item["origin_system"],
            "creator_id": item.get("creator_id"),
            "jira_issue_key": item.get("jira_issue_key"),
            "story_points": item.get("story_points"),
            "impact": item.get("impact")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get work item {work_item_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get work item: {str(e)}")


@app.post("/work-items/{work_item_id}/outcome")
async def record_outcome(work_item_id: str, outcome: OutcomeRequest):
    """
    Record an outcome for a work item and forward to Learner Service.
    
    This is where the learning loop starts - outcomes flow here first, then to Learner.
    """
    try:
        # Verify work item exists
        work_item = execute_query("""
            SELECT id, service FROM work_items WHERE id = %s
        """, [work_item_id])
        
        if not work_item:
            raise HTTPException(status_code=404, detail=f"WorkItem {work_item_id} not found")
        
        service = work_item[0]["service"]
        
        # Store outcome in database (if outcomes table exists)
        # Note: outcomes table may not exist in init_db.sql, so we'll handle gracefully
        try:
            outcome_id = f"outcome-{uuid.uuid4().hex[:12]}"
            execute_update("""
                INSERT INTO outcomes (
                    id, work_item_id, event_id, type, decision_id, actor_id,
                    service, timestamp, new_assignee_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
            """, [
                outcome_id,
                work_item_id,
                outcome.event_id,
                outcome.type,
                outcome.decision_id,
                outcome.actor_id,
                service,
                outcome.timestamp,
                outcome.new_assignee_id
            ])
        except Exception as e:
            logger.warning(f"Failed to store outcome in database (table may not exist): {e}")
            # Continue - we'll still forward to Learner
        
        # Forward to Learner Service
        learner_url = os.getenv("LEARNER_SERVICE_URL", "http://learner:8003")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{learner_url}/outcomes",
                    json={
                        "event_id": outcome.event_id,
                        "decision_id": outcome.decision_id,
                        "work_item_id": work_item_id,
                        "type": outcome.type,
                        "actor_id": outcome.actor_id,
                        "service": service,
                        "timestamp": outcome.timestamp,
                        "new_assignee_id": outcome.new_assignee_id
                    }
                )
                response.raise_for_status()
                logger.info(f"Forwarded outcome {outcome.event_id} to Learner Service")
        except httpx.RequestError as e:
            logger.error(f"Failed to forward outcome to Learner Service: {e}")
            # Don't fail the request - outcome is recorded
        except httpx.HTTPStatusError as e:
            logger.error(f"Learner Service returned error: {e.response.status_code} - {e.response.text}")
            # Don't fail the request - outcome is recorded
        
        return {
            "outcome_id": outcome_id if 'outcome_id' in locals() else None,
            "processed": True,
            "message": "Outcome recorded and forwarded to Learner"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record outcome: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to record outcome: {str(e)}")


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

