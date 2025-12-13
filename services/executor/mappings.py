"""
Mapping functions for Executor Service.
Maps service → Jira project, severity → priority, human → Jira accountId.
"""
import os
import logging
from typing import Optional, Dict
from db import execute_query

logger = logging.getLogger(__name__)

# Service → Jira Project mapping (configurable via env or defaults)
SERVICE_TO_JIRA_PROJECT_MAP: Dict[str, str] = {
    "api": "API",
    "frontend": "FE",
    "backend": "BE",
    "infrastructure": "INFRA",
    "data": "DATA",
    "mobile": "MOBILE",
}

# Severity → Jira Priority mapping
SEVERITY_TO_PRIORITY_MAP: Dict[str, str] = {
    "sev1": "Critical",
    "sev2": "High",
    "sev3": "Medium",
    "sev4": "Low",
}


def get_jira_project(service: str) -> str:
    """
    Map service name to Jira project key.
    
    Args:
        service: Service name (e.g., "api", "frontend")
    
    Returns:
        Jira project key (e.g., "API", "FE")
    
    Raises:
        ValueError: If service mapping not found
    """
    service_lower = service.lower()
    
    # Check environment variable override first
    env_key = f"SERVICE_{service_lower.upper()}_PROJECT"
    env_project = os.getenv(env_key)
    if env_project:
        return env_project
    
    # Check default mapping
    if service_lower in SERVICE_TO_JIRA_PROJECT_MAP:
        return SERVICE_TO_JIRA_PROJECT_MAP[service_lower]
    
    # Fallback: use service name as project key (uppercase)
    logger.warning(f"No mapping found for service '{service}', using '{service.upper()}' as project key")
    return service.upper()


def get_jira_priority(severity: str) -> str:
    """
    Map severity to Jira priority.
    
    Args:
        severity: Severity level (e.g., "sev1", "sev2")
    
    Returns:
        Jira priority name (e.g., "Critical", "High")
    
    Raises:
        ValueError: If severity mapping not found
    """
    severity_lower = severity.lower()
    
    if severity_lower not in SEVERITY_TO_PRIORITY_MAP:
        logger.warning(f"No mapping found for severity '{severity}', using 'Medium' as default")
        return "Medium"
    
    return SEVERITY_TO_PRIORITY_MAP[severity_lower]


def get_jira_account_id(human_id: str) -> Optional[str]:
    """
    Get Jira accountId for a human from the database.
    
    Args:
        human_id: Human ID
    
    Returns:
        Jira accountId if found, None otherwise
    """
    try:
        query = "SELECT jira_account_id FROM humans WHERE id = %s"
        results = execute_query(query, [human_id])
        
        if results and results[0].get('jira_account_id'):
            return results[0]['jira_account_id']
        
        logger.warning(f"No jira_account_id found for human_id '{human_id}'")
        return None
    except Exception as e:
        logger.error(f"Failed to get jira_account_id for human_id '{human_id}': {e}")
        return None


def validate_mappings(service: str, severity: str, human_id: str) -> tuple[str, str, Optional[str]]:
    """
    Validate all mappings before execution.
    
    Args:
        service: Service name
        severity: Severity level
        human_id: Human ID
    
    Returns:
        Tuple of (jira_project, jira_priority, jira_account_id)
    
    Raises:
        ValueError: If required mappings are missing
    """
    jira_project = get_jira_project(service)
    jira_priority = get_jira_priority(severity)
    jira_account_id = get_jira_account_id(human_id)
    
    if not jira_account_id:
        raise ValueError(f"No Jira accountId found for human_id '{human_id}'. Cannot create Jira issue.")
    
    return jira_project, jira_priority, jira_account_id
