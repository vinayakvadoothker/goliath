"""
PagerDuty webhook handler for incident creation (ingestion).
Processes incident.triggered and incident.created events to create WorkItems.
"""
import os
import json
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from db import execute_query, execute_update

logger = logging.getLogger(__name__)


def _parse_datetime(dt_str: str) -> datetime:
    """
    Parse ISO 8601 datetime string, handling various formats.
    
    Args:
        dt_str: ISO 8601 datetime string
    
    Returns:
        datetime object (timezone-naive)
    """
    try:
        # Handle Z suffix (UTC)
        if dt_str.endswith('Z'):
            dt_str = dt_str.replace('Z', '+00:00')
        
        # Parse with timezone
        dt = datetime.fromisoformat(dt_str)
        
        # Convert to timezone-naive (PostgreSQL expects naive datetime)
        if dt.tzinfo:
            dt = dt.replace(tzinfo=None)
        
        return dt
    except Exception as e:
        logger.warning(f"Failed to parse datetime '{dt_str}': {e}, using current time")
        return datetime.now()


# Service mapping: PagerDuty service name → Goliath service name
# Can be configured via environment variable or defaults
PAGERDUTY_SERVICE_MAP: Dict[str, str] = {
    "api-service": "api",
    "frontend-service": "frontend",
    "backend-service": "backend",
    "infrastructure": "infrastructure",
    "data-service": "data",
    "mobile-service": "mobile",
}


def map_pagerduty_service(pagerduty_service_name: str) -> str:
    """
    Map PagerDuty service name to Goliath service name.
    
    Args:
        pagerduty_service_name: PagerDuty service name
    
    Returns:
        Goliath service name (defaults to lowercase of input if no mapping found)
    """
    service_lower = pagerduty_service_name.lower()
    
    # Check environment variable override
    env_key = f"PAGERDUTY_SERVICE_{service_lower.upper().replace('-', '_')}"
    env_service = os.getenv(env_key)
    if env_service:
        return env_service
    
    # Check default mapping
    if service_lower in PAGERDUTY_SERVICE_MAP:
        return PAGERDUTY_SERVICE_MAP[service_lower]
    
    # Fallback: use service name as-is (lowercase)
    logger.warning(f"No service mapping found for '{pagerduty_service_name}', using '{service_lower}'")
    return service_lower


def map_pagerduty_urgency_to_severity(urgency: str) -> str:
    """
    Map PagerDuty urgency to Goliath severity.
    
    Args:
        urgency: PagerDuty urgency ("high" or "low")
    
    Returns:
        Goliath severity ("sev1", "sev2", "sev3", or "sev4")
    """
    urgency_lower = urgency.lower()
    
    if urgency_lower == "high":
        return "sev2"  # High urgency → sev2 (can be adjusted based on priority if available)
    elif urgency_lower == "low":
        return "sev3"  # Low urgency → sev3
    else:
        logger.warning(f"Unknown urgency '{urgency}', defaulting to sev3")
        return "sev3"


def create_work_item_from_pagerduty_incident(
    incident_id: str,
    incident_number: str,
    title: str,
    description: str,
    service_name: str,
    urgency: str,
    created_at: str
) -> Dict[str, Any]:
    """
    Create a WorkItem from PagerDuty incident data.
    
    Args:
        incident_id: PagerDuty incident ID
        incident_number: PagerDuty incident number (e.g., "INC-12345")
        title: Incident title
        description: Incident description
        service_name: PagerDuty service name
        urgency: PagerDuty urgency
        created_at: ISO 8601 timestamp
    
    Returns:
        Created work item data
    """
    work_item_id = f"wi-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    # Map PagerDuty service → Goliath service
    goliath_service = map_pagerduty_service(service_name)
    
    # Map PagerDuty urgency → Goliath severity
    severity = map_pagerduty_urgency_to_severity(urgency)
    
    # Combine title and description for work item description
    work_item_description = f"{title}\n\n{description}" if description else title
    
    # Store in database
    try:
        query = """
            INSERT INTO work_items (
                id, type, service, severity, description, raw_log,
                created_at, origin_system, pagerduty_incident_id, raw_payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = [
            work_item_id,
            "incident",
            goliath_service,
            severity,
            work_item_description,
            description,  # Store original description as raw_log
            _parse_datetime(created_at) if created_at else datetime.now(),
            f"PAGERDUTY-{incident_number}",  # Store PagerDuty incident number in origin_system
            incident_id,  # Store PagerDuty incident ID for tracking
            json.dumps({"incident_id": incident_id, "incident_number": str(incident_number)})  # Store incident metadata as JSON
        ]
        execute_update(query, params)
        
        logger.info(
            f"Created WorkItem {work_item_id} from PagerDuty incident {incident_number} "
            f"(service: {goliath_service}, severity: {severity})"
        )
        
        return {
            "work_item_id": work_item_id,
            "service": goliath_service,
            "severity": severity,
            "description": work_item_description,
            "created_at": created_at,
            "origin_system": f"PAGERDUTY-{incident_number}"
        }
    
    except Exception as e:
        logger.error(f"Failed to create WorkItem from PagerDuty incident: {e}", exc_info=True)
        raise


async def process_pagerduty_incident_webhook(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process PagerDuty webhook event for incident creation.
    
    Handles:
    - incident.triggered: New incident created
    - incident.created: Incident created (alternative event type)
    
    Args:
        webhook_data: PagerDuty webhook payload
    
    Returns:
        Processing result with work_item_id
    """
    try:
        # Extract event data from PagerDuty webhook format
        event = webhook_data.get("event", {})
        event_type = event.get("event_type")
        incident = event.get("data", {}).get("incident", {})
        
        if not incident:
            logger.warning("No incident data in webhook payload")
            return {"status": "error", "message": "No incident data"}
        
        # Only process incident creation events
        if event_type not in ["incident.triggered", "incident.created"]:
            logger.info(f"Ignoring event type: {event_type} (only processing incident.triggered/created)")
            return {"status": "skipped", "message": f"Event type {event_type} not handled"}
        
        incident_id = incident.get("id")
        incident_number = incident.get("incident_number")
        title = incident.get("title", "")
        urgency = incident.get("urgency", "low")
        
        # Get service information
        service = incident.get("service", {})
        service_name = service.get("name", "unknown") if isinstance(service, dict) else str(service)
        
        # Get incident body/description
        body = incident.get("body", {})
        description = ""
        if isinstance(body, dict):
            description = body.get("details", "")
        
        # Get created timestamp
        created_at = incident.get("created_at") or datetime.now().isoformat()
        
        if not incident_id:
            logger.warning("No incident ID in webhook payload")
            return {"status": "error", "message": "No incident ID"}
        
        # Create WorkItem
        work_item = create_work_item_from_pagerduty_incident(
            incident_id=incident_id,
            incident_number=str(incident_number) if incident_number else incident_id,
            title=title,
            description=description,
            service_name=service_name,
            urgency=urgency,
            created_at=created_at
        )
        
        logger.info(
            f"Processed PagerDuty incident creation: {incident_number} → WorkItem {work_item['work_item_id']}"
        )
        
        return {
            "status": "success",
            "work_item_id": work_item["work_item_id"],
            "incident_id": incident_id,
            "incident_number": incident_number,
            "service": work_item["service"],
            "severity": work_item["severity"]
        }
    
    except Exception as e:
        logger.error(f"Failed to process PagerDuty incident webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


def validate_pagerduty_signature(payload: bytes, signature: Optional[str]) -> bool:
    """
    Validate PagerDuty webhook signature.
    
    Note: PagerDuty webhooks can include an X-PagerDuty-Signature header
    for verification. This is a simplified check - in production,
    you should verify the signature properly.
    
    Args:
        payload: Request payload
        signature: Signature from X-PagerDuty-Signature header
    
    Returns:
        True if signature is valid (or if validation is disabled)
    """
    # For MVP, we'll skip signature validation
    # In production, implement proper signature verification
    signature_secret = os.getenv("PAGERDUTY_WEBHOOK_SECRET")
    
    if not signature_secret:
        logger.warning("PAGERDUTY_WEBHOOK_SECRET not set, skipping signature validation")
        return True
    
    # TODO: Implement proper signature verification
    # PagerDuty uses HMAC-SHA256 for signature verification
    return True
