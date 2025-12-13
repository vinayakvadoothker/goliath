"""
Scoring algorithm for ranking candidates.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def calculate_severity_match_score(
    candidate_fit_score: float,
    work_item_severity: str
) -> float:
    """
    Adjust score based on severity matching.
    Higher severity (sev1) should prefer higher fit_score candidates.
    
    Args:
        candidate_fit_score: Candidate's fit_score (0-1)
        work_item_severity: Work item severity (sev1-sev4)
    
    Returns:
        Severity match multiplier (0.8-1.2)
    """
    severity_weights = {
        "sev1": 1.2,  # Critical - strongly prefer high fit_score
        "sev2": 1.1,  # High - prefer high fit_score
        "sev3": 1.0,  # Medium - neutral
        "sev4": 0.9   # Low - can use lower fit_score
    }
    
    weight = severity_weights.get(work_item_severity, 1.0)
    
    # Higher fit_score gets more boost for high severity
    if work_item_severity in ["sev1", "sev2"]:
        return 1.0 + (weight - 1.0) * candidate_fit_score
    else:
        return weight


def calculate_capacity_score(
    human: Dict[str, Any],
    work_item_story_points: Optional[int]
) -> float:
    """
    Calculate capacity score (how much capacity remaining).
    Higher score = more capacity available.
    
    Args:
        human: Human profile
        work_item_story_points: Story points required
    
    Returns:
        Capacity score (0-1)
    """
    if not work_item_story_points:
        return 1.0  # No capacity requirement
    
    max_points = human.get("max_story_points", 21)
    current_points = human.get("current_story_points", 0)
    available = max_points - current_points
    
    if available <= 0:
        return 0.0
    
    # Score based on percentage of capacity remaining after assignment
    after_assignment = available - work_item_story_points
    if after_assignment < 0:
        return 0.0
    
    # Prefer candidates with more capacity remaining (but not too much - indicates underutilization)
    # Ideal: 20-40% capacity remaining
    remaining_pct = after_assignment / max_points
    
    if remaining_pct >= 0.4:
        # Too much capacity - might indicate underutilization, slight penalty
        return 0.9
    elif remaining_pct >= 0.2:
        # Ideal range
        return 1.0
    elif remaining_pct >= 0.1:
        # Getting tight but okay
        return 0.8
    else:
        # Very tight
        return 0.6


def calculate_vector_similarity_score(
    similar_incidents: List[Dict[str, Any]],
    candidate_id: str
) -> float:
    """
    Calculate score based on vector similarity to past incidents resolved by this candidate.
    
    Args:
        similar_incidents: List of similar work items with resolver_id and similarity
        candidate_id: Candidate human ID to check
    
    Returns:
        Vector similarity score (0-1)
    """
    if not similar_incidents:
        return 0.5  # Neutral if no similar incidents
    
    # Find incidents resolved by this candidate
    candidate_resolved = [
        inc for inc in similar_incidents
        if inc.get("resolver_id") == candidate_id
    ]
    
    if not candidate_resolved:
        return 0.5  # Neutral if candidate hasn't resolved similar incidents
    
    # Weight by similarity score
    total_score = 0.0
    for incident in candidate_resolved:
        similarity = incident.get("similarity", 0.5)
        # Weight by similarity (higher similarity = more relevant)
        total_score += similarity
    
    # Average similarity, with boost for multiple similar resolutions
    avg_similarity = total_score / len(candidate_resolved)
    # Boost if candidate resolved multiple similar incidents (shows expertise)
    if len(candidate_resolved) > 1:
        boost = min(0.2, len(candidate_resolved) * 0.05)
        avg_similarity = min(1.0, avg_similarity + boost)
    
    return min(1.0, avg_similarity)


def calculate_final_score(
    candidate: Dict[str, Any],
    work_item: Dict[str, Any],
    similar_incidents: List[Dict[str, Any]]
) -> Dict[str, float]:
    """
    Calculate final composite score for a candidate.
    
    Returns score breakdown:
    {
        "fit_score": 0.8,
        "severity_match": 1.1,
        "capacity": 0.9,
        "vector_similarity": 0.85,
        "final_score": 0.87
    }
    """
    fit_score = candidate.get("fit_score", 0.5)
    work_item_severity = work_item.get("severity", "sev3")
    work_item_story_points = work_item.get("story_points")
    
    # Component scores
    severity_match = calculate_severity_match_score(fit_score, work_item_severity)
    capacity_score = calculate_capacity_score(candidate, work_item_story_points)
    vector_similarity = calculate_vector_similarity_score(similar_incidents, candidate.get("id"))
    
    # Weighted combination
    # fit_score is most important (40%), then vector_similarity (30%), capacity (20%), severity_match (10%)
    # Note: severity_match is a multiplier, so we apply it to fit_score component
    final_score = (
        fit_score * 0.4 +
        vector_similarity * 0.3 +
        capacity_score * 0.2 +
        (fit_score * severity_match) * 0.1
    )
    
    # Normalize to 0-1
    final_score = min(1.0, max(0.0, final_score))
    
    return {
        "fit_score": fit_score,
        "severity_match": severity_match,
        "capacity": capacity_score,
        "vector_similarity": vector_similarity,
        "final_score": final_score
    }


def score_candidates(
    candidates: List[Dict[str, Any]],
    work_item: Dict[str, Any],
    similar_incidents: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Score all candidates and return sorted by final_score (descending).
    
    Args:
        candidates: List of candidate humans (after constraint filtering)
        work_item: Work item details
        similar_incidents: Similar work items from vector search
    
    Returns:
        List of candidates with scores, sorted by final_score descending
    """
    scored = []
    
    for candidate in candidates:
        score_breakdown = calculate_final_score(candidate, work_item, similar_incidents)
        candidate["score_breakdown"] = score_breakdown
        candidate["final_score"] = score_breakdown["final_score"]
        scored.append(candidate)
    
    # Sort by final_score descending
    scored.sort(key=lambda x: x["final_score"], reverse=True)
    
    # Add rank
    for i, candidate in enumerate(scored):
        candidate["rank"] = i + 1
    
    return scored


def calculate_confidence(
    primary_candidate: Dict[str, Any],
    backup_candidates: List[Dict[str, Any]],
    total_candidates: int
) -> float:
    """
    Calculate confidence score (0-1) for the decision.
    
    Confidence factors:
    - Primary candidate's final_score
    - Gap between primary and next best
    - Number of candidates considered
    
    Args:
        primary_candidate: Selected primary candidate with final_score
        backup_candidates: Backup candidates
        total_candidates: Total number of candidates before filtering
    
    Returns:
        Confidence score (0-1)
    """
    primary_score = primary_candidate.get("final_score", 0.5)
    
    # Base confidence from primary score
    base_confidence = primary_score
    
    # Boost if there's a clear winner (large gap to next best)
    if backup_candidates:
        next_best_score = backup_candidates[0].get("final_score", 0.0)
        score_gap = primary_score - next_best_score
        
        # Large gap (>0.2) = high confidence
        if score_gap > 0.2:
            gap_boost = 0.15
        elif score_gap > 0.1:
            gap_boost = 0.1
        elif score_gap > 0.05:
            gap_boost = 0.05
        else:
            gap_boost = 0.0
        
        base_confidence += gap_boost
    else:
        # No backups - lower confidence
        base_confidence *= 0.9
    
    # Penalty if very few candidates
    if total_candidates < 3:
        base_confidence *= 0.9
    
    # Normalize to 0-1
    return min(1.0, max(0.0, base_confidence))

