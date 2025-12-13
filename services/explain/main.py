"""
Explain Service - Generates contextual evidence bullets explaining decisions
"""
import os
import json
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client."""
    global openai_client
    if openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        openai_client = OpenAI(api_key=api_key)
    return openai_client


# Request/Response Models
class CandidateFeature(BaseModel):
    """Candidate feature data."""
    human_id: str
    display_name: str
    fit_score: float
    resolves_count: int
    transfers_count: int
    last_resolved_at: Optional[str] = None
    on_call: bool = False
    pages_7d: int = 0
    active_items: int = 0
    similar_incident_score: Optional[float] = None
    score_breakdown: Optional[Dict[str, float]] = None


class ConstraintResult(BaseModel):
    """Constraint check result."""
    name: str
    passed: bool
    reason: Optional[str] = None


class WorkItemData(BaseModel):
    """Work item data."""
    id: str
    service: str
    severity: str
    description: str
    type: str


class ExplainDecisionRequest(BaseModel):
    """Request to explain a decision."""
    decision_id: str
    work_item: WorkItemData
    primary_human_id: str
    primary_features: CandidateFeature
    backup_human_ids: List[str] = Field(default_factory=list)
    backup_features: List[CandidateFeature] = Field(default_factory=list)
    constraints_checked: List[ConstraintResult] = Field(default_factory=list)
    correlation_id: Optional[str] = None


class Evidence(BaseModel):
    """Evidence bullet point."""
    type: str
    text: str
    time_window: str
    source: str


class ExplainDecisionResponse(BaseModel):
    """Response with evidence and explanation."""
    decision_id: str
    evidence: List[Evidence]
    constraints: List[ConstraintResult]
    why_not_next_best: str


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Explain Service starting up...")
    # Initialize OpenAI client on startup
    try:
        get_openai_client()
        logger.info("OpenAI client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
    yield
    logger.info("Explain Service shutting down...")


app = FastAPI(
    title="Explain Service",
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


def generate_evidence_prompt(
    work_item: WorkItemData,
    primary_features: CandidateFeature,
    backup_features: List[CandidateFeature],
    constraints: List[ConstraintResult]
) -> str:
    """
    Generate prompt for LLM evidence generation.
    
    Args:
        work_item: Work item data
        primary_features: Primary candidate features
        backup_features: Backup candidate features
        constraints: Constraint check results
    
    Returns:
        Prompt string
    """
    # Format primary candidate stats
    primary_stats = f"""
Primary Candidate: {primary_features.display_name} ({primary_features.human_id})
- Fit Score: {primary_features.fit_score:.2f}
- Resolves (last 90 days): {primary_features.resolves_count}
- Transfers (last 90 days): {primary_features.transfers_count}
- Last Resolved: {primary_features.last_resolved_at or 'Never'}
- On Call: {primary_features.on_call}
- Pages (7 days): {primary_features.pages_7d}
- Active Items: {primary_features.active_items}
- Similar Incident Score: {primary_features.similar_incident_score or 'N/A'}
"""
    
    # Format backup candidates
    backup_stats = ""
    if backup_features:
        backup_stats = "\nBackup Candidates:\n"
        for i, backup in enumerate(backup_features[:3], 1):  # Top 3 backups
            backup_stats += f"""
{i}. {backup.display_name} ({backup.human_id})
   - Fit Score: {backup.fit_score:.2f}
   - Resolves: {backup.resolves_count}
   - Transfers: {backup.transfers_count}
   - Last Resolved: {backup.last_resolved_at or 'Never'}
"""
    
    # Format constraints
    constraints_text = "\nConstraints Checked:\n"
    for constraint in constraints:
        status = "✓ PASSED" if constraint.passed else "✗ FAILED"
        reason = f" ({constraint.reason})" if constraint.reason else ""
        constraints_text += f"- {constraint.name}: {status}{reason}\n"
    
    prompt = f"""You are generating evidence bullets for a work item assignment decision.

Work Item:
- Service: {work_item.service}
- Severity: {work_item.severity}
- Type: {work_item.type}
- Description: {work_item.description}

{primary_stats}
{backup_stats}
{constraints_text}

Generate 5-7 evidence bullets explaining why the primary candidate was selected. Each bullet must:
1. Be FACTUAL (only use provided stats, no hallucinations)
2. Be TIME-BOUNDED (include time windows like "last 7 days", "last 30 days", "last 90 days")
3. Include SOURCE (e.g., "Learner stats", "Vector similarity", "On-call status")
4. Be SPECIFIC (e.g., "Resolved 3 similar incidents" not "experienced")
5. Be CONTEXTUAL (related to this specific work item)

Return JSON in this exact format:
{{
  "evidence": [
    {{
      "type": "recent_resolution|recent_commit|on_call|low_load|similar_incident",
      "text": "Specific factual evidence",
      "time_window": "last X days",
      "source": "Learner stats|Vector similarity|On-call status|Load tracking"
    }}
  ],
  "why_not_next_best": "Factual comparison explaining why primary was chosen over next best candidate. Be specific about differences in fit_score, resolves_count, transfers_count, or other metrics. Never make global claims."
}}

Important:
- Temperature=0 (deterministic)
- All evidence must be factual and verifiable
- No global claims ("best engineer") - only contextual
- Include specific numbers and time windows
- Compare primary to next best candidate in "why_not_next_best"
"""
    
    return prompt


def generate_evidence_with_llm(prompt: str) -> Dict[str, Any]:
    """
    Generate evidence using LLM.
    
    Args:
        prompt: Evidence generation prompt
    
    Returns:
        LLM response as dictionary
    
    Raises:
        ValueError: If LLM response is invalid
    """
    client = get_openai_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    try:
        logger.info(f"Calling OpenAI API (model: {model}) for evidence generation")
        start_time = datetime.now()
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a factual evidence generator. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,  # Deterministic output
            response_format={"type": "json_object"}  # Force JSON output
        )
        
        latency = (datetime.now() - start_time).total_seconds()
        logger.info(f"OpenAI API call completed in {latency:.2f}s")
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from LLM")
        
        # Parse JSON response
        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.error(f"Response content: {content}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        
        # Validate response structure
        if "evidence" not in result:
            raise ValueError("LLM response missing 'evidence' field")
        if "why_not_next_best" not in result:
            raise ValueError("LLM response missing 'why_not_next_best' field")
        
        # Validate evidence items
        for i, ev in enumerate(result["evidence"]):
            required_fields = ["type", "text", "time_window", "source"]
            for field in required_fields:
                if field not in ev:
                    raise ValueError(f"Evidence item {i} missing required field: {field}")
        
        return result
    
    except Exception as e:
        logger.error(f"LLM evidence generation failed: {e}", exc_info=True)
        raise


def generate_fallback_evidence(
    primary_features: CandidateFeature,
    backup_features: List[CandidateFeature]
) -> tuple[List[Evidence], str]:
    """
    Generate fallback evidence if LLM fails.
    
    Args:
        primary_features: Primary candidate features
        backup_features: Backup candidate features
    
    Returns:
        Tuple of (evidence list, why_not_next_best string)
    """
    evidence = []
    
    # Add evidence based on available stats
    if primary_features.resolves_count > 0:
        evidence.append(Evidence(
            type="recent_resolution",
            text=f"Resolved {primary_features.resolves_count} similar incidents in the last 90 days",
            time_window="last 90 days",
            source="Learner stats"
        ))
    
    if primary_features.last_resolved_at:
        evidence.append(Evidence(
            type="recent_resolution",
            text=f"Last resolved similar incident on {primary_features.last_resolved_at}",
            time_window="recent",
            source="Learner stats"
        ))
    
    if primary_features.on_call:
        evidence.append(Evidence(
            type="on_call",
            text="Currently on call and available",
            time_window="current",
            source="On-call status"
        ))
    
    if primary_features.pages_7d == 0:
        evidence.append(Evidence(
            type="low_load",
            text="No pages in the last 7 days, indicating low current load",
            time_window="last 7 days",
            source="Load tracking"
        ))
    
    if primary_features.similar_incident_score:
        evidence.append(Evidence(
            type="similar_incident",
            text=f"High similarity score ({primary_features.similar_incident_score:.2f}) to this work item",
            time_window="current",
            source="Vector similarity"
        ))
    
    # Generate why_not_next_best
    why_not = "Primary candidate selected based on fit score and availability."
    if backup_features:
        next_best = backup_features[0]
        if primary_features.fit_score > next_best.fit_score:
            why_not = (
                f"Primary candidate has higher fit_score ({primary_features.fit_score:.2f} vs "
                f"{next_best.fit_score:.2f}) and has resolved more incidents "
                f"({primary_features.resolves_count} vs {next_best.resolves_count}) in the last 90 days."
            )
    
    return evidence, why_not


@app.get("/healthz")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "explain"}


@app.post("/explainDecision", response_model=ExplainDecisionResponse)
async def explain_decision(request: ExplainDecisionRequest, req: Request):
    """
    Generate evidence bullets explaining a decision.
    
    This endpoint:
    1. Uses LLM to generate contextual evidence (temperature=0 for deterministic output)
    2. Validates all LLM responses
    3. Generates "why not next best" comparison
    4. Formats constraints summary
    5. Falls back to template-based evidence if LLM fails
    
    Args:
        request: Explanation request
        req: FastAPI request object
    
    Returns:
        Explanation response with evidence, constraints, and comparison
    """
    correlation_id = getattr(req.state, "correlation_id", str(uuid.uuid4()))
    
    logger.info(
        f"Explaining decision {request.decision_id} "
        f"(correlation_id: {correlation_id})"
    )
    
    try:
        # Generate evidence using LLM
        try:
            prompt = generate_evidence_prompt(
                request.work_item,
                request.primary_features,
                request.backup_features,
                request.constraints_checked
            )
            
            llm_result = generate_evidence_with_llm(prompt)
            
            # Convert to Evidence objects
            evidence = [
                Evidence(
                    type=ev["type"],
                    text=ev["text"],
                    time_window=ev["time_window"],
                    source=ev["source"]
                )
                for ev in llm_result["evidence"]
            ]
            
            why_not_next_best = llm_result["why_not_next_best"]
            
            logger.info(
                f"Generated {len(evidence)} evidence bullets for decision {request.decision_id}"
            )
        
        except Exception as llm_error:
            # Fallback to template-based evidence
            logger.warning(
                f"LLM evidence generation failed for decision {request.decision_id}: {llm_error}. "
                f"Using fallback evidence."
            )
            evidence, why_not_next_best = generate_fallback_evidence(
                request.primary_features,
                request.backup_features
            )
        
        # Ensure we have at least some evidence
        if not evidence:
            evidence = [
                Evidence(
                    type="general",
                    text=f"Selected based on fit_score of {request.primary_features.fit_score:.2f}",
                    time_window="current",
                    source="Decision engine"
                )
            ]
        
        return ExplainDecisionResponse(
            decision_id=request.decision_id,
            evidence=evidence,
            constraints=request.constraints_checked,
            why_not_next_best=why_not_next_best
        )
    
    except Exception as e:
        logger.error(
            f"Unexpected error explaining decision {request.decision_id}: {e}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Failed to explain decision: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("EXPLAIN_SERVICE_PORT", "8005"))
    uvicorn.run(app, host="0.0.0.0", port=port)
