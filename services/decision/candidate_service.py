"""
Candidate generation service - fetches candidates from Learner Service.
"""
import os
import httpx
import logging
from typing import List, Dict, Any, Optional
from db import execute_query

logger = logging.getLogger(__name__)


def _get_fallback_candidates(service: str) -> List[Dict[str, Any]]:
    """
    Fallback: Get candidates from Jira users table.
    Used when Learner Service is down.
    
    Args:
        service: Service name
    
    Returns:
        List of basic candidate profiles with default fit_score
    """
    try:
        # Map service name to project name (they should match)
        # Get users who have worked on issues for this service/project
        query = """
            SELECT DISTINCT
                ju.account_id,
                ju.display_name,
                ju.max_story_points,
                ju.current_story_points
            FROM jira_users ju
            JOIN jira_issues ji ON ji.assignee_account_id = ju.account_id
            JOIN jira_projects jp ON ji.project_key = jp.key
            WHERE ju.active = TRUE
            AND jp.name = %s
            LIMIT 20
        """
        
        results = execute_query(query, [service])
        
        candidates = []
        for row in results:
            candidates.append({
                "id": row["account_id"],  # Use account_id as id (matches human.id format)
                "display_name": row["display_name"],
                "fit_score": 0.5,  # Default neutral score
                "resolves_count": 0,
                "transfers_count": 0,
                "on_call": False,  # Default
                "pages_7d": 0,
                "active_items": 0,
                "max_story_points": row.get("max_story_points", 21),
                "current_story_points": row.get("current_story_points", 0),
                "resolved_by_severity": {"sev1": 0, "sev2": 0, "sev3": 0, "sev4": 0}
            })
        
        if candidates:
            logger.warning(f"Using fallback candidates from Jira: {len(candidates)} candidates for {service}")
            return candidates
        
        # If no service-specific candidates, get any active users
        query = """
            SELECT account_id, display_name, max_story_points, current_story_points
            FROM jira_users
            WHERE active = TRUE
            LIMIT 20
        """
        
        results = execute_query(query)
        
        for row in results:
            candidates.append({
                "id": row["account_id"],
                "display_name": row["display_name"],
                "fit_score": 0.5,
                "resolves_count": 0,
                "transfers_count": 0,
                "on_call": False,
                "pages_7d": 0,
                "active_items": 0,
                "max_story_points": row.get("max_story_points", 21),
                "current_story_points": row.get("current_story_points", 0),
                "resolved_by_severity": {"sev1": 0, "sev2": 0, "sev3": 0, "sev4": 0}
            })
        
        if candidates:
            logger.warning(f"Using generic fallback candidates: {len(candidates)} candidates")
            return candidates
        
        logger.error(f"No fallback candidates found")
        return []
        
    except Exception as e:
        logger.error(f"Fallback candidate generation failed: {e}", exc_info=True)
        return []


async def get_candidates(service: str, use_fallback: bool = True) -> List[Dict[str, Any]]:
    """
    Get candidate humans from Learner Service for a given service.
    Falls back to database if Learner Service is unavailable.
    
    Args:
        service: Service name (e.g., "api-service")
        use_fallback: If True, use database fallback when Learner is down
    
    Returns:
        List of human profiles with fit_score, resolves_count, transfers_count
    """
    learner_url = os.getenv("LEARNER_SERVICE_URL", "http://learner:8000")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{learner_url}/profiles",
                params={"service": service}
            )
            response.raise_for_status()
            data = response.json()
            profiles = data.get("profiles", [])
            
            if profiles:
                return profiles
            else:
                # Empty response - try fallback
                if use_fallback:
                    logger.warning(f"Learner Service returned empty profiles for {service}, using fallback")
                    return _get_fallback_candidates(service)
                return []
                
    except httpx.TimeoutException:
        logger.error(f"Learner Service timeout when fetching candidates for {service}")
        if use_fallback:
            logger.warning("Using fallback candidates due to timeout")
            return _get_fallback_candidates(service)
        return []
    except httpx.HTTPStatusError as e:
        logger.error(f"Learner Service error: {e.response.status_code}")
        if use_fallback:
            logger.warning("Using fallback candidates due to HTTP error")
            return _get_fallback_candidates(service)
        return []
    except Exception as e:
        logger.error(f"Failed to get candidates from Learner Service: {e}")
        if use_fallback:
            logger.warning("Using fallback candidates due to exception")
            return _get_fallback_candidates(service)
        return []

