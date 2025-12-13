"""
Core decision engine - orchestrates the decision-making process.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from db import (
    get_work_item, save_decision, save_decision_candidate,
    save_constraint_result, get_decision
)
from candidate_service import get_candidates
from constraint_service import apply_constraints
from scoring_service import score_candidates, calculate_confidence
from weaviate_client import search_similar_work_items, store_work_item
from llm_client import generate_embedding, extract_entities

logger = logging.getLogger(__name__)


async def make_decision(work_item_id: str) -> Dict[str, Any]:
    """
    Make a decision for a work item.
    
    Processing flow:
    1. Retrieve WorkItem from database
    2. Generate embedding for work item description
    3. Vector similarity search in Weaviate for similar incidents
    4. Call Learner Service for candidates
    5. Apply constraint filtering
    6. Score remaining candidates
    7. Select primary + backups
    8. Calculate confidence
    9. Store decision + audit trail
    10. Return decision
    
    Args:
        work_item_id: Work item ID
    
    Returns:
        Decision with primary_human_id, backup_human_ids, confidence, etc.
    """
    # Check if decision already exists
    existing_decision = get_decision(work_item_id)
    if existing_decision:
        logger.info(f"Decision already exists for work_item {work_item_id}, returning existing")
        return existing_decision
    
    # 1. Get work item
    work_item = get_work_item(work_item_id)
    if not work_item:
        raise ValueError(f"Work item {work_item_id} not found")
    
    service = work_item.get("service")
    description = work_item.get("description", "")
    severity = work_item.get("severity", "sev3")
    
    # 2. Generate embedding (non-blocking - continue if it fails)
    embedding = None
    try:
        if description:
            embedding = generate_embedding(description)
            if not embedding:
                logger.warning("Failed to generate embedding, continuing without vector similarity")
        else:
            logger.warning("No description provided, skipping embedding generation")
    except Exception as e:
        logger.warning(f"Embedding generation failed: {e}, continuing without vector similarity")
    
    # 3. Vector similarity search (non-blocking - continue if it fails)
    similar_incidents = []
    if embedding:
        try:
            similar_incidents = search_similar_work_items(embedding, service=service, limit=20)
            logger.info(f"Found {len(similar_incidents)} similar incidents")
        except Exception as e:
            logger.warning(f"Vector similarity search failed: {e}, continuing without similarity data")
    
    # 4. Get candidates from Learner Service
    candidates = await get_candidates(service)
    if not candidates:
        logger.error(f"No candidates found for service {service}")
        raise ValueError(f"No candidates found for service {service}. Learner Service may be down or service has no profiles.")
    
    logger.info(f"Retrieved {len(candidates)} candidates from Learner Service")
    
    # 5. Apply constraints
    passed_candidates, filtered_candidates = apply_constraints(candidates, work_item)
    
    if not passed_candidates:
        raise ValueError(f"All candidates filtered out for work_item {work_item_id}")
    
    logger.info(f"After constraints: {len(passed_candidates)} passed, {len(filtered_candidates)} filtered")
    
    # 6. Score candidates
    scored_candidates = score_candidates(passed_candidates, work_item, similar_incidents)
    
    # 7. Select primary + backups
    primary = scored_candidates[0]
    backups = scored_candidates[1:3] if len(scored_candidates) > 1 else []  # Top 2 backups
    
    # 8. Calculate confidence
    confidence = calculate_confidence(primary, backups, len(candidates))
    
    # 9. Create decision ID
    decision_id = f"dec-{uuid.uuid4().hex[:12]}"
    
    # 10. Store decision
    save_decision(
        decision_id=decision_id,
        work_item_id=work_item_id,
        primary_human_id=primary["id"],
        backup_human_ids=[b["id"] for b in backups],
        confidence=confidence
    )
    
    # 11. Store audit trail (all candidates)
    for candidate in scored_candidates:
        save_decision_candidate(
            decision_id=decision_id,
            human_id=candidate["id"],
            score=candidate["final_score"],
            rank=candidate["rank"],
            filtered=False,
            filter_reason=None,
            score_breakdown=candidate["score_breakdown"]
        )
    
    for candidate in filtered_candidates:
        save_decision_candidate(
            decision_id=decision_id,
            human_id=candidate["id"],
            score=0.0,
            rank=len(scored_candidates) + filtered_candidates.index(candidate) + 1,
            filtered=True,
            filter_reason=candidate.get("filter_reason"),
            score_breakdown={}
        )
    
    # 12. Store constraint results
    # Check capacity constraint
    capacity_passed = len(passed_candidates) > 0
    save_constraint_result(
        decision_id=decision_id,
        constraint_name="capacity",
        passed=capacity_passed,
        reason=f"{len(passed_candidates)} candidates passed capacity check" if capacity_passed else "All candidates failed capacity check"
    )
    
    # Check availability constraint
    availability_passed = len(passed_candidates) > 0
    save_constraint_result(
        decision_id=decision_id,
        constraint_name="availability",
        passed=availability_passed,
        reason=f"{len(passed_candidates)} candidates are available" if availability_passed else "No available candidates"
    )
    
    # 13. Store work item in Weaviate for future similarity searches (if embedding exists)
    # Do this asynchronously - don't block decision return
    if embedding:
        try:
            store_work_item(
                work_item_id=work_item_id,
                description=description,
                service=service,
                severity=severity,
                embedding=embedding
            )
        except Exception as e:
            logger.warning(f"Failed to store work item in Weaviate: {e}, continuing")
    
    # 14. Return decision
    return {
        "id": decision_id,
        "work_item_id": work_item_id,
        "primary_human_id": primary["id"],
        "backup_human_ids": [b["id"] for b in backups],
        "confidence": confidence,
        "created_at": datetime.now().isoformat()
    }

