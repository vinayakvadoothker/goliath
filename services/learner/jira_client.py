"""
Jira Simulator client - calls Person 1's Jira Simulator service.
"""
import os
import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from jira_utils import service_to_project_key

logger = logging.getLogger(__name__)


async def search_closed_tickets(
    project: Optional[str] = None,
    days_back: int = 90,
    start_at: int = 0,
    max_results: int = 100
) -> Dict[str, Any]:
    """
    Search for closed Jira tickets using JQL.
    
    Args:
        project: Project key (e.g., "API"). If None, searches all projects.
        days_back: Number of days to look back (default: 90)
        start_at: Pagination offset
        max_results: Maximum results per page
    
    Returns:
        Jira API response with issues array
    """
    jira_url = os.getenv("JIRA_SIMULATOR_URL", "http://jira-simulator:8080")
    
    # Build JQL query
    jql_parts = ["status=Done", f"resolved >= -{days_back}d"]
    if project:
        jql_parts.insert(0, f"project={project}")
    
    jql = " AND ".join(jql_parts)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{jira_url}/rest/api/3/search",
                params={
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": max_results
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error(f"Jira Simulator timeout when searching closed tickets")
        return {"issues": [], "total": 0, "startAt": 0, "maxResults": 0}
    except httpx.HTTPStatusError as e:
        logger.error(f"Jira Simulator error: {e.response.status_code} - {e.response.text}")
        return {"issues": [], "total": 0, "startAt": 0, "maxResults": 0}
    except Exception as e:
        logger.error(f"Failed to search Jira Simulator: {e}")
        return {"issues": [], "total": 0, "startAt": 0, "maxResults": 0}


async def get_all_closed_tickets(
    project: Optional[str] = None,
    days_back: int = 90
) -> List[Dict[str, Any]]:
    """
    Get all closed tickets (handles pagination automatically).
    
    Args:
        project: Project key (optional)
        days_back: Number of days to look back
    
    Returns:
        List of all closed issues
    """
    all_issues = []
    start_at = 0
    max_results = 100
    
    while True:
        response = await search_closed_tickets(
            project=project,
            days_back=days_back,
            start_at=start_at,
            max_results=max_results
        )
        
        issues = response.get("issues", [])
        if not issues:
            break
        
        all_issues.extend(issues)
        
        total = response.get("total", 0)
        if start_at + len(issues) >= total:
            break
        
        start_at += max_results
    
    logger.info(f"Retrieved {len(all_issues)} closed tickets from Jira Simulator")
    return all_issues


async def get_user_story_points(user_account_id: str) -> Dict[str, int]:
    """
    Get current story points for a user from Jira Simulator database.
    
    Args:
        user_account_id: Jira account ID
    
    Returns:
        Dict with max_story_points and current_story_points
    """
    # Query Jira Simulator database directly (same database)
    from db import execute_query
    
    try:
        query = """
            SELECT max_story_points, current_story_points
            FROM jira_users
            WHERE account_id = %s
        """
        results = execute_query(query, [user_account_id])
            
        if results:
                return {
                "max_story_points": results[0].get("max_story_points", 21),
                "current_story_points": results[0].get("current_story_points", 0)
                }
    except Exception as e:
        logger.warning(f"Failed to get story points for user {user_account_id}: {e}")
    
    return {"max_story_points": 21, "current_story_points": 0}


async def get_user_resolved_by_severity(user_account_id: str, service: str, days: int = 90) -> Dict[str, int]:
    """
    Get resolved ticket count by severity for a user in a service.
    
    Args:
        user_account_id: Jira account ID
        service: Service/project name
        days: Number of days to look back
    
    Returns:
        Dict with sev1, sev2, sev3, sev4 counts
    """
    # Map Jira priority to severity
    priority_to_severity = {
        "Critical": "sev1",
        "High": "sev2",
        "Medium": "sev3",
        "Low": "sev4"
    }
    
    jira_url = os.getenv("JIRA_SIMULATOR_URL", "http://jira-simulator:8080")
    
    # Map service name to project key
    project_key = service_to_project_key(service)
    
    # Build JQL query
    jql = f"assignee={user_account_id} AND project={project_key} AND status=Done AND resolved >= -{days}d"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{jira_url}/rest/api/3/search",
                params={
                    "jql": jql,
                    "maxResults": 1000  # Should be enough for 90 days
                }
            )
            response.raise_for_status()
            data = response.json()
            
            resolved_by_severity = {"sev1": 0, "sev2": 0, "sev3": 0, "sev4": 0}
            
            for issue in data.get("issues", []):
                priority = issue.get("fields", {}).get("priority", {}).get("name", "")
                severity = priority_to_severity.get(priority, "sev4")
                resolved_by_severity[severity] = resolved_by_severity.get(severity, 0) + 1
            
            return resolved_by_severity
    except Exception as e:
        logger.warning(f"Failed to get resolved by severity for user {user_account_id}: {e}")
        return {"sev1": 0, "sev2": 0, "sev3": 0, "sev4": 0}


async def get_user_on_call_status(user_account_id: str) -> bool:
    """
    Get on-call status for a user (placeholder - would need real on-call system).
    
    Args:
        user_account_id: Jira account ID
    
    Returns:
        Boolean indicating if user is on-call
    """
    # TODO: Integrate with actual on-call system (PagerDuty, etc.)
    # For now, return False as placeholder
    return False
