"""
Jira utility functions for mapping between project keys and service names.
"""
from typing import Optional


def project_key_to_service(project_key: str) -> str:
    """
    Map Jira project key to service name.
    
    Args:
        project_key: Jira project key (e.g., "API", "PAYMENT")
    
    Returns:
        Service name (e.g., "api-service", "payment-service")
    """
    # Mapping from Jira Simulator outcome_generator
    mapping = {
        "API": "api-service",
        "APISERVICE": "api-service",
        "PAYMENT": "payment-service",
        "PAYMENTSERVICE": "payment-service",
        "FRONTEND": "frontend-app",
        "FRONTENDAPP": "frontend-app",
        "DATA": "data-pipeline",
        "DATAPIPELINE": "data-pipeline",
        "INFRA": "infrastructure",
        "INFRASTRUCTURE": "infrastructure"
    }
    
    # Try exact match first
    if project_key.upper() in mapping:
        return mapping[project_key.upper()]
    
    # Try to derive from project name pattern
    # If project key is uppercase, convert to lowercase and add "-service"
    if project_key.isupper():
        return project_key.lower().replace("_", "-")
    
    # Default: return as-is (might already be service name)
    return project_key.lower().replace("_", "-")


def service_to_project_key(service: str) -> str:
    """
    Map service name to Jira project key.
    
    Args:
        service: Service name (e.g., "api-service", "payment-service")
    
    Returns:
        Project key (e.g., "API", "PAYMENT")
    """
    # Reverse mapping
    reverse_mapping = {
        "api-service": "API",
        "payment-service": "PAYMENT",
        "frontend-app": "FRONTEND",
        "data-pipeline": "DATA",
        "infrastructure": "INFRA"
    }
    
    if service.lower() in reverse_mapping:
        return reverse_mapping[service.lower()]
    
    # Default: uppercase and remove dashes
    return service.upper().replace("-", "")

