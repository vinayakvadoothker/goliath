"""
Executor Service client - polls for Jira issue creation
"""
import httpx
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

EXECUTOR_URL = os.getenv("EXECUTOR_SERVICE_URL", "http://executor:8004")

async def poll_jira_issue(decision_id: str, max_attempts: int = 30, delay: float = 1.0) -> dict:
    """Poll Executor Service for Jira issue creation."""
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try to get executed action by decision_id
                response = await client.get(
                    f"{EXECUTOR_URL}/executed_actions",
                    params={"decision_id": decision_id}
                )
                
                if response.status_code == 200:
                    actions = response.json()
                    if actions and len(actions) > 0:
                        action = actions[0]
                        if action.get("jira_issue_key"):
                            logger.info(f"Jira issue found: {action['jira_issue_key']}")
                            return action
                
                # Not ready yet, wait and retry
                await asyncio.sleep(delay)
        except httpx.HTTPError as e:
            logger.warning(f"Error polling Jira issue (attempt {attempt + 1}/{max_attempts}): {e}")
            if attempt < max_attempts - 1:
                await asyncio.sleep(delay)
            else:
                raise
    
    raise TimeoutError(f"Jira issue not found after {max_attempts} attempts")

async def get_jira_issue_by_decision(decision_id: str) -> dict:
    """Get Jira issue for a decision (with polling)."""
    return await poll_jira_issue(decision_id)

