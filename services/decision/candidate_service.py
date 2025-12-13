"""
Candidate generation service - fetches candidates from Learner Service.
"""
import os
import httpx
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


async def get_candidates(service: str) -> List[Dict[str, Any]]:
    """
    Get candidate humans from Learner Service for a given service.
    
    Args:
        service: Service name (e.g., "api-service")
    
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
            return data.get("profiles", [])
    except httpx.TimeoutException:
        logger.error(f"Learner Service timeout when fetching candidates for {service}")
        return []
    except httpx.HTTPStatusError as e:
        logger.error(f"Learner Service error: {e.response.status_code}")
        return []
    except Exception as e:
        logger.error(f"Failed to get candidates from Learner Service: {e}")
        return []

