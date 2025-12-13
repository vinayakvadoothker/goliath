"""
System state management - tracks metrics, logs, incidents
"""
from typing import List, Dict, Optional
from datetime import datetime
import uuid

class SystemState:
    def __init__(self):
        self.metrics: Dict[str, float] = {
            "requests_per_sec": 150.0,
            "error_rate": 0.0,
            "cpu_usage": 45.0,
            "memory_usage": 60.0,
            "avg_latency": 120.0,
        }
        self.logs: List[Dict] = []
        self.incidents: Dict[str, Dict] = {}
        self.latest_decision: Optional[Dict] = None
        self.max_logs = 1000
        
        # Add initial logs
        self.add_log("INFO", "System initialized - Control Center ready")
        self.add_log("INFO", "WebSocket server started")
        self.add_log("INFO", "Waiting for actions...")

    def add_log(self, level: str, message: str):
        """Add a log entry."""
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        self.logs.append(log_entry)
        # Keep only last max_logs entries
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]

    def update_metric(self, name: str, value: float):
        """Update a metric value."""
        self.metrics[name] = value

    def add_incident(self, work_item_id: str, error_type: str, severity: str, error_message: str):
        """Add a new incident."""
        incident = {
            "id": str(uuid.uuid4()),
            "work_item_id": work_item_id,
            "error_type": error_type,
            "severity": severity,
            "error_message": error_message,
            "status": "detected",
            "created_at": datetime.now().isoformat(),
        }
        self.incidents[work_item_id] = incident
        return incident

    def update_incident(self, work_item_id: str, **updates):
        """Update an incident."""
        if work_item_id in self.incidents:
            self.incidents[work_item_id].update(updates)

    def set_decision(self, decision: Dict):
        """Set the latest decision."""
        self.latest_decision = decision

    def get_state(self) -> Dict:
        """Get current system state."""
        return {
            "metrics": self.metrics,
            "logs": self.logs[-100:],  # Last 100 logs
            "incidents": list(self.incidents.values()),
            "latest_decision": self.latest_decision
        }

# Global state instance
system_state = SystemState()

