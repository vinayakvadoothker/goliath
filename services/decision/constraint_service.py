"""
Constraint filtering service - applies veto filters to candidates.
"""
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


def check_capacity_constraint(
    human: Dict[str, Any],
    work_item_story_points: Optional[int]
) -> Tuple[bool, Optional[str]]:
    """
    Check if human has capacity for this work item.
    
    Args:
        human: Human profile with max_story_points and current_story_points
        work_item_story_points: Story points required for work item
    
    Returns:
        (passed, reason)
    """
    if not work_item_story_points:
        return True, None  # No story points requirement
    
    max_points = human.get("max_story_points", 21)
    current_points = human.get("current_story_points", 0)
    available = max_points - current_points
    
    if available < work_item_story_points:
        return False, f"Insufficient capacity: {available}/{max_points} available, need {work_item_story_points}"
    
    return True, None


def check_availability_constraint(
    human: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """
    Check if human is available (not on PTO, etc.).
    For now, just checks if active.
    
    Args:
        human: Human profile
    
    Returns:
        (passed, reason)
    """
    active = human.get("active", True)
    if not active:
        return False, "Human is not active"
    
    return True, None


def apply_constraints(
    candidates: List[Dict[str, Any]],
    work_item: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Apply all constraint filters to candidates.
    Returns (passed_candidates, filtered_candidates_with_reasons).
    
    Args:
        candidates: List of candidate humans
        work_item: Work item with story_points, etc.
    
    Returns:
        (passed_candidates, filtered_candidates)
        filtered_candidates include filter_reason
    """
    passed = []
    filtered = []
    
    work_item_story_points = work_item.get("story_points")
    
    for candidate in candidates:
        # Check capacity
        capacity_passed, capacity_reason = check_capacity_constraint(
            candidate, work_item_story_points
        )
        if not capacity_passed:
            candidate["filtered"] = True
            candidate["filter_reason"] = capacity_reason
            filtered.append(candidate)
            continue
        
        # Check availability
        availability_passed, availability_reason = check_availability_constraint(candidate)
        if not availability_passed:
            candidate["filtered"] = True
            candidate["filter_reason"] = availability_reason
            filtered.append(candidate)
            continue
        
        # Passed all constraints
        candidate["filtered"] = False
        passed.append(candidate)
    
    return passed, filtered

