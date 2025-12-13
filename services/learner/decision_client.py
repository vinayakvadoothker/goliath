"""
Decision Service client - fetches decision data for reassigned outcomes.
"""
import os
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


async def get_decision_by_work_item(work_item_id: str) -> Optional[Dict[str, Any]]:
    """
    Get decision for a work item from Decision Service.
    
    Args:
        work_item_id: Work item ID
    
    Returns:
        Decision dict with primary_human_id, or None if not found
    """
    decision_url = os.getenv("DECISION_SERVICE_URL", "http://decision:8002")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{decision_url}/decisions/{work_item_id}"
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.warning(f"Decision Service timeout when fetching decision for {work_item_id}")
        return None
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.warning(f"Decision not found for work_item {work_item_id}")
            return None
        logger.error(f"Decision Service error: {e.response.status_code}")
        return None
    except Exception as e:
        logger.warning(f"Failed to get decision from Decision Service: {e}")
        return None


async def get_decision_by_id(decision_id: str) -> Optional[Dict[str, Any]]:
    """
    Get decision by decision ID (if we have decision_id but not work_item_id).
    
    Note: Decision Service doesn't have this endpoint, so we'd need to query by work_item_id.
    For now, this is a placeholder.
    """
    # Decision Service doesn't expose decision by ID directly
    # We'd need to query the database or add an endpoint
    # For now, return None
    return None

