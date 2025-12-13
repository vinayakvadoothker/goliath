"""
Decision Service client - polls for decisions
"""
import httpx
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

DECISION_URL = os.getenv("DECISION_SERVICE_URL", "http://decision:8002")

async def poll_decision(work_item_id: str, max_attempts: int = 30, delay: float = 1.0) -> dict:
    """Poll Decision Service for a decision on a work item."""
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{DECISION_URL}/decisions/{work_item_id}"
                )
                
                if response.status_code == 200:
                    decision = response.json()
                    logger.info(f"Decision found for {work_item_id}")
                    return decision
                elif response.status_code == 404:
                    # Decision not ready yet, wait and retry
                    await asyncio.sleep(delay)
                    continue
                else:
                    response.raise_for_status()
        except httpx.HTTPError as e:
            logger.warning(f"Error polling decision (attempt {attempt + 1}/{max_attempts}): {e}")
            if attempt < max_attempts - 1:
                await asyncio.sleep(delay)
            else:
                raise
    
    raise TimeoutError(f"Decision not found after {max_attempts} attempts")

async def get_decision_by_work_item(work_item_id: str) -> dict:
    """Get decision for a work item (with polling)."""
    return await poll_decision(work_item_id)

