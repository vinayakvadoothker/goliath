"""
Standalone tests for Executor Service.
Tests Jira issue creation, fallback handling, and database operations.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, ExecuteDecisionRequest, WorkItemData, Evidence
from db import execute_query, execute_update
import httpx


# Test data
MOCK_DECISION_REQUEST = ExecuteDecisionRequest(
    decision_id="test_decision_1",
    work_item_id="test_work_item_1",
    primary_human_id="test_human_1",
    backup_human_ids=["test_human_2"],
    evidence=[
        Evidence(
            type="recent_resolution",
            text="Resolved 3 similar incidents in last 7 days",
            time_window="last 7 days",
            source="Learner stats"
        )
    ],
    work_item=WorkItemData(
        service="api-service",
        severity="sev2",
        description="Test incident: API endpoint returning 500 errors",
        story_points=3
    )
)

MOCK_JIRA_RESPONSE = {
    "id": "jira_12345",
    "key": "API-123",
    "self": "http://jira-simulator:8080/rest/api/3/issue/jira_12345"
}


@pytest.fixture
def client():
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def db_setup():
    """Setup test database data."""
    # Ensure executed_actions table exists
    try:
        execute_update("""
            CREATE TABLE IF NOT EXISTS executed_actions (
                id TEXT PRIMARY KEY,
                decision_id TEXT NOT NULL,
                jira_issue_key TEXT,
                jira_issue_id TEXT,
                assigned_human_id TEXT NOT NULL,
                backup_human_ids TEXT,
                created_at TEXT NOT NULL,
                slack_message_id TEXT,
                fallback_message TEXT
            )
        """, [])
    except Exception:
        pass  # Table might already exist
    
    # Create test human with Jira accountId
    execute_update(
        """
        INSERT INTO humans (id, display_name, jira_account_id)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET display_name = EXCLUDED.display_name,
            jira_account_id = EXCLUDED.jira_account_id
        """,
        ["test_human_1", "Test Human 1", "test_account_1"]
    )
    
    # Create test work item
    execute_update(
        """
        INSERT INTO work_items (id, type, service, severity, description)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET type = EXCLUDED.type,
            service = EXCLUDED.service,
            severity = EXCLUDED.severity,
            description = EXCLUDED.description
        """,
        ["test_work_item_1", "incident", "api-service", "sev2", "Test incident"]
    )
    
    yield
    
    # Cleanup
    try:
        execute_update("DELETE FROM executed_actions WHERE decision_id LIKE %s", ["test_%"])
    except Exception:
        pass
    try:
        execute_update("DELETE FROM work_items WHERE id LIKE %s", ["test_%"])
    except Exception:
        pass
    try:
        execute_update("DELETE FROM humans WHERE id LIKE %s", ["test_%"])
    except Exception:
        pass


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_endpoint(self, client):
        """Health endpoint should return healthy status."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "executor"


class TestExecuteDecision:
    """Test decision execution."""
    
    def test_execute_decision_creates_jira_issue(self, client, db_setup):
        """Executor should create Jira issue successfully."""
        with patch('main.create_jira_issue_with_retry') as mock_create:
            mock_create.return_value = MOCK_JIRA_RESPONSE
            
            response = client.post(
                "/executeDecision",
                json=MOCK_DECISION_REQUEST.model_dump(),
                headers={"X-Correlation-ID": "test-correlation-123"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["jira_issue_key"] == "API-123"
            assert data["jira_issue_id"] == "jira_12345"
            assert data["assigned_human_id"] == "test_human_1"
            assert data["fallback_used"] == False
            assert "executed_action_id" in data
            
            # Verify executed action stored in DB
            actions = execute_query(
                "SELECT * FROM executed_actions WHERE decision_id = %s ORDER BY created_at DESC",
                ["test_decision_1"]
            )
            # Get the most recent one (might be multiple from previous test runs)
            assert len(actions) >= 1
            latest_action = actions[0]
            assert latest_action["jira_issue_key"] == "API-123"
    
    def test_execute_decision_fallback_on_jira_failure(self, client, db_setup):
        """Executor should fallback to DB storage if Jira fails."""
        with patch('main.create_jira_issue_with_retry') as mock_create:
            mock_create.side_effect = httpx.HTTPStatusError(
                "Jira API error",
                request=MagicMock(),
                response=MagicMock(status_code=500)
            )
            
            response = client.post(
                "/executeDecision",
                json=MOCK_DECISION_REQUEST.model_dump()
            )
            
            # The code stores fallback but still returns 200 (with fallback_used=True)
            # This is actually correct behavior - it gracefully degrades
            assert response.status_code == 200
            data = response.json()
            assert data["fallback_used"] == True
            assert data["jira_issue_key"] is None
            
            # Verify executed action stored in DB (even on failure)
            actions = execute_query(
                "SELECT * FROM executed_actions WHERE decision_id = %s ORDER BY created_at DESC",
                ["test_decision_1"]
            )
            assert len(actions) >= 1
            latest_action = actions[0]
            assert latest_action["jira_issue_key"] is None  # No Jira issue created
            assert latest_action["fallback_message"] is not None  # Fallback message stored
    
    def test_execute_decision_missing_human(self, client):
        """Executor should fail if human doesn't exist."""
        request = MOCK_DECISION_REQUEST.model_dump()
        request["primary_human_id"] = "nonexistent_human"
        
        response = client.post("/executeDecision", json=request)
        
        assert response.status_code == 400
        assert "accountId" in response.json()["detail"].lower() or "human" in response.json()["detail"].lower()
    
    def test_execute_decision_invalid_service(self, client, db_setup):
        """Executor should handle invalid service mapping."""
        request = MOCK_DECISION_REQUEST.model_dump()
        request["work_item"]["service"] = "invalid-service"
        
        with patch('main.create_jira_issue_with_retry') as mock_create:
            # Jira Simulator might reject invalid project, so it fails
            mock_create.side_effect = httpx.HTTPStatusError(
                "Jira API error",
                request=MagicMock(),
                response=MagicMock(status_code=500)
            )
            
            response = client.post("/executeDecision", json=request)
            
            # Should fallback to DB storage (returns 200 with fallback_used=True)
            assert response.status_code == 200
            data = response.json()
            assert data["fallback_used"] == True
    
    def test_execute_decision_updates_work_item(self, client, db_setup):
        """Executor should link Jira issue back to work item."""
        with patch('main.create_jira_issue_with_retry') as mock_create:
            mock_create.return_value = MOCK_JIRA_RESPONSE
            
            response = client.post("/executeDecision", json=MOCK_DECISION_REQUEST.model_dump())
            
            assert response.status_code == 200
            
            # Verify work item updated
            work_items = execute_query(
                "SELECT jira_issue_key FROM work_items WHERE id = %s",
                ["test_work_item_1"]
            )
            assert len(work_items) == 1
            assert work_items[0]["jira_issue_key"] == "API-123"


class TestCorrelationID:
    """Test correlation ID middleware."""
    
    def test_correlation_id_in_response(self, client):
        """Response should include correlation ID header."""
        response = client.get("/healthz", headers={"X-Correlation-ID": "test-123"})
        assert response.headers.get("X-Correlation-ID") == "test-123"
    
    def test_correlation_id_generated(self, client):
        """Correlation ID should be generated if not provided."""
        response = client.get("/healthz")
        assert "X-Correlation-ID" in response.headers
        assert len(response.headers["X-Correlation-ID"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

