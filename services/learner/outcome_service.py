"""
Outcome processing service - the core learning loop.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from db import (
    check_outcome_processed,
    mark_outcome_processed,
    get_or_create_stats,
    get_or_create_load,
    update_stats,
    update_load,
    create_resolved_edge,
    create_transferred_edge,
    get_resolved_work_items,
    get_or_create_human
)
from stats_service import calculate_fit_score
from embedding_utils import (
    generate_embedding,
    aggregate_embeddings,
    pca_reduce,
    generate_capability_summary
)
from weaviate_client import update_human_embedding
from db import update_human_3d_coords

logger = logging.getLogger(__name__)


def process_outcome(outcome: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process outcome and update stats (idempotent).
    
    This is THE learning loop:
    - Resolved → fit_score increases (+0.1), resolves_count increases
    - Reassigned → fit_score decreases (-0.15), transfers_count increases
    
    Args:
        outcome: Outcome dict with event_id, work_item_id, type, actor_id, service, timestamp, etc.
    
    Returns:
        Dict with processed status and updates
    """
    event_id = outcome.get("event_id")
    if not event_id:
        raise ValueError("event_id is required")
    
    # Check idempotency
    if check_outcome_processed(event_id):
        logger.info(f"Outcome {event_id} already processed, skipping")
        return {
            "processed": False,
            "reason": "Already processed",
            "event_id": event_id
        }
    
    outcome_type = outcome.get("type")
    actor_id = outcome.get("actor_id")
    service = outcome.get("service")
    work_item_id = outcome.get("work_item_id")
    timestamp_str = outcome.get("timestamp")
    
    if not all([outcome_type, actor_id, service, work_item_id, timestamp_str]):
        raise ValueError("Missing required outcome fields")
    
    # Parse timestamp
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        if timestamp.tzinfo:
            timestamp = timestamp.replace(tzinfo=None)
    except Exception as e:
        logger.error(f"Failed to parse timestamp {timestamp_str}: {e}")
        timestamp = datetime.now()
    
    updates = []
    
    try:
        if outcome_type == "resolved":
            updates.extend(_process_resolved_outcome(actor_id, service, work_item_id, timestamp))
        
        elif outcome_type == "reassigned":
            decision_id = outcome.get("decision_id")
            new_assignee_id = outcome.get("new_assignee_id") or actor_id
            updates.extend(_process_reassigned_outcome(
                decision_id, work_item_id, actor_id, new_assignee_id, service, timestamp
            ))
        
        elif outcome_type == "escalated":
            # Escalated is similar to reassigned but with different penalty
            decision_id = outcome.get("decision_id")
            updates.extend(_process_escalated_outcome(
                decision_id, work_item_id, actor_id, service, timestamp
            ))
        
        else:
            raise ValueError(f"Unknown outcome type: {outcome_type}")
        
        # Mark as processed
        mark_outcome_processed(event_id, timestamp)
        
        logger.info(f"Processed outcome {event_id} ({outcome_type}) with {len(updates)} updates")
        
        return {
            "processed": True,
            "event_id": event_id,
            "updates": updates,
            "message": "Stats updated successfully"
        }
    
    except Exception as e:
        logger.error(f"Failed to process outcome {event_id}: {e}")
        raise


def _process_resolved_outcome(
    actor_id: str,
    service: str,
    work_item_id: str,
    timestamp: datetime
) -> List[Dict[str, Any]]:
    """Process resolved outcome - increases fit_score."""
    updates = []
    
    # Get or create stats
    stats = get_or_create_stats(actor_id, service)
    old_fit_score = stats.get("fit_score", 0.5)
    
    # Update stats
    new_fit_score = min(1.0, old_fit_score + 0.1)  # Boost by +0.1
    update_stats(
        human_id=actor_id,
        service=service,
        fit_score=new_fit_score,
        resolves_count_delta=1,
        last_resolved_at=timestamp
    )
    
    # Create resolved edge in knowledge graph
    create_resolved_edge(actor_id, work_item_id, timestamp)
    
    # Update human embedding in Weaviate
    _update_human_embedding_from_resolution(actor_id, service, work_item_id)
    
    # Update load (decrement active_items)
    load = get_or_create_load(actor_id)
    update_load(actor_id, active_items_delta=-1)
    
    updates.append({
        "human_id": actor_id,
        "fit_score_delta": new_fit_score - old_fit_score,
        "resolves_count_delta": 1
    })
    
    return updates


def _process_reassigned_outcome(
    decision_id: Optional[str],
    work_item_id: str,
    original_assignee_id: str,
    new_assignee_id: str,
    service: str,
    timestamp: datetime
) -> List[Dict[str, Any]]:
    """Process reassigned outcome - decreases original assignee fit_score."""
    updates = []
    
    # Original assignee: penalty
    original_stats = get_or_create_stats(original_assignee_id, service)
    old_fit_score_original = original_stats.get("fit_score", 0.5)
    
    new_fit_score_original = max(0.0, old_fit_score_original - 0.15)  # Penalty -0.15
    update_stats(
        human_id=original_assignee_id,
        service=service,
        fit_score=new_fit_score_original,
        transfers_count_delta=1
    )
    
    updates.append({
        "human_id": original_assignee_id,
        "fit_score_delta": new_fit_score_original - old_fit_score_original,
        "transfers_count_delta": 1
    })
    
    # New assignee: slight boost (they accepted it)
    new_stats = get_or_create_stats(new_assignee_id, service)
    old_fit_score_new = new_stats.get("fit_score", 0.5)
    
    new_fit_score_new = min(1.0, old_fit_score_new + 0.05)  # Slight boost +0.05
    update_stats(
        human_id=new_assignee_id,
        service=service,
        fit_score=new_fit_score_new
    )
    
    updates.append({
        "human_id": new_assignee_id,
        "fit_score_delta": new_fit_score_new - old_fit_score_new
    })
    
    # Create transferred edge in knowledge graph
    create_transferred_edge(work_item_id, original_assignee_id, new_assignee_id, timestamp)
    
    return updates


def _process_escalated_outcome(
    decision_id: Optional[str],
    work_item_id: str,
    actor_id: str,
    service: str,
    timestamp: datetime
) -> List[Dict[str, Any]]:
    """Process escalated outcome - similar to reassigned but different penalty."""
    # For now, treat escalated same as reassigned
    # In future, could have different penalty
    return _process_reassigned_outcome(decision_id, work_item_id, actor_id, actor_id, service, timestamp)


def _update_human_embedding_from_resolution(human_id: str, service: str, work_item_id: str) -> None:
    """Update human embedding when they resolve a work item."""
    try:
        # Get all resolved work items for this human
        resolved_items = get_resolved_work_items(human_id, limit=50)
        
        if not resolved_items:
            return
        
        # Generate embeddings for all resolved items
        embeddings = []
        weights = []
        
        for i, item in enumerate(resolved_items):
            description = item.get("description", "")
            if description:
                embedding = generate_embedding(description)
                embeddings.append(embedding)
                # More recent = higher weight
                weights.append(1.0 / (i + 1))
        
        if not embeddings:
            return
        
        # Aggregate embeddings (weighted average)
        aggregated_embedding = aggregate_embeddings(embeddings, weights)
        
        # Reduce to 3D for visualization
        x, y, z = pca_reduce(aggregated_embedding)
        
        # Update PostgreSQL with 3D coordinates
        update_human_3d_coords(human_id, x, y, z)
        
        # Generate capability summary
        capability_summary = generate_capability_summary(resolved_items)
        
        # Get human display name
        from db import execute_query
        human_query = "SELECT display_name FROM humans WHERE id = %s"
        human_results = execute_query(human_query, [human_id])
        display_name = human_results[0].get("display_name", human_id) if human_results else human_id
        
        # Update Weaviate
        update_human_embedding(
            human_id=human_id,
            display_name=display_name,
            service=service,
            embedding=aggregated_embedding,
            capability_summary=capability_summary
        )
        
        logger.info(f"Updated human embedding for {human_id} in service {service}")
    
    except Exception as e:
        logger.error(f"Failed to update human embedding: {e}")
