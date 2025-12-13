"""
Ingest Service client - creates WorkItems
"""
import httpx
import os
import logging

logger = logging.getLogger(__name__)

INGEST_URL = os.getenv("INGEST_SERVICE_URL", "http://ingest:8000")

async def create_work_item(service: str, severity: str, description: str, raw_log: str) -> dict:
    """Create a work item via Ingest Service."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "service": service,
                "severity": severity,
                "description": description,
                "type": "incident",
                "raw_log": raw_log
            }
            
            response = await client.post(
                f"{INGEST_URL}/ingest/demo",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"WorkItem created: {result.get('work_item_id', 'unknown')}")
            return result
    except Exception as e:
        logger.error(f"Failed to create work item: {e}")
        raise

