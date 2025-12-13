"""
Datadog API Simulator - Generates Datadog-format monitoring data
"""
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from state.system_state import system_state

def generate_datadog_metric(name: str, value: float, tags: List[str] = None) -> Dict[str, Any]:
    """
    Generate a Datadog-format metric.
    
    Format: https://docs.datadoghq.com/api/latest/metrics/#submit-metrics
    """
    return {
        "metric": name,
        "points": [[int(time.time()), value]],
        "tags": tags or [],
        "type": "gauge"
    }

def generate_datadog_log(level: str, message: str, service: str = "goliath-search", **attributes) -> Dict[str, Any]:
    """
    Generate a Datadog-format log.
    
    Format: https://docs.datadoghq.com/api/latest/logs/#send-logs
    """
    return {
        "ddsource": "goliath",
        "ddtags": f"env:demo,service:{service}",
        "hostname": "goliath-search-1",
        "message": message,
        "service": service,
        "status": level.lower(),
        "timestamp": int(time.time() * 1000),  # Datadog uses milliseconds
        **attributes
    }

def generate_datadog_event(title: str, text: str, alert_type: str = "info", **attributes) -> Dict[str, Any]:
    """
    Generate a Datadog-format event.
    
    Format: https://docs.datadoghq.com/api/latest/events/#post-an-event
    """
    return {
        "title": title,
        "text": text,
        "alert_type": alert_type,  # info, warning, error, success
        "date_happened": int(time.time()),
        "tags": attributes.get("tags", []),
        **attributes
    }

def process_product_action(action: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process a product action and generate Datadog monitoring data.
    
    Returns list of Datadog-format data points (metrics, logs, events).
    """
    datadog_data = []
    service_name = "goliath-search"
    
    if action == "search":
        query = data.get("query", "")
        
        # Generate metrics
        datadog_data.append(generate_datadog_metric(
            "goliath.search.requests.count",
            1.0,
            tags=[f"query:{query[:20]}", "service:search"]
        ))
        
        # Generate log
        datadog_data.append(generate_datadog_log(
            "info",
            f"Search request: {query}",
            service=service_name,
            query=query,
            response_time_ms=120
        ))
        
        # Update system state
        current_requests = system_state.metrics.get("requests_per_sec", 150)
        system_state.update_metric("requests_per_sec", current_requests + 1)
        system_state.add_log("INFO", f"Search: {query}")
    
    elif action == "browse_page":
        page = data.get("page", "unknown")
        
        datadog_data.append(generate_datadog_metric(
            "goliath.page.views.count",
            1.0,
            tags=[f"page:{page}"]
        ))
        
        datadog_data.append(generate_datadog_log(
            "info",
            f"Page view: {page}",
            service=service_name,
            page=page
        ))
        
        system_state.add_log("INFO", f"Page view: {page}")
    
    elif action == "upload_file":
        datadog_data.append(generate_datadog_metric(
            "goliath.upload.count",
            1.0,
            tags=["type:file"]
        ))
        
        datadog_data.append(generate_datadog_log(
            "info",
            "File upload initiated",
            service=service_name
        ))
        
        system_state.add_log("INFO", "File upload initiated")
    
    elif action == "trigger_error":
        error_type = data.get("type", "unknown")
        
        # Generate error event
        datadog_data.append(generate_datadog_event(
            "Error Detected",
            f"Error type: {error_type}",
            alert_type="error",
            tags=[f"error_type:{error_type}", "service:goliath-search"]
        ))
        
        # Generate error metric
        datadog_data.append(generate_datadog_metric(
            "goliath.errors.count",
            1.0,
            tags=[f"error_type:{error_type}"]
        ))
        
        # Generate error log
        datadog_data.append(generate_datadog_log(
            "error",
            f"Error triggered: {error_type}",
            service=service_name,
            error_type=error_type
        ))
        
        # Trigger actual error in system (will be handled by action handler)
        # The error will be processed asynchronously
    
    elif action == "generate_load":
        intensity = data.get("intensity", 100)
        
        datadog_data.append(generate_datadog_metric(
            "goliath.requests.rate",
            float(intensity),
            tags=["type:load_test"]
        ))
        
        datadog_data.append(generate_datadog_log(
            "info",
            f"Load test: {intensity} requests/sec",
            service=service_name,
            load_intensity=intensity
        ))
        
        # Update metrics
        system_state.update_metric("requests_per_sec", intensity)
        system_state.add_log("INFO", f"Load test: {intensity} req/sec")
    
    return datadog_data

