"""
Standalone tests for Explain Service.
Tests evidence generation, LLM integration, and fallback handling.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from dotenv import load_dotenv

# Load .env file if it exists
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    app,
    ExplainDecisionRequest,
    WorkItemData,
    CandidateFeature,
    ConstraintResult,
    Evidence
)
from openai import OpenAI


# Test data
MOCK_EXPLAIN_REQUEST = ExplainDecisionRequest(
    decision_id="test_decision_1",
    work_item=WorkItemData(
        id="test_work_item_1",
        service="api-service",
        severity="sev2",
        description="Test incident: API endpoint returning 500 errors",
        type="incident"
    ),
    primary_human_id="test_human_1",
    primary_features=CandidateFeature(
        human_id="test_human_1",
        display_name="Alice Engineer",
        fit_score=0.85,
        resolves_count=12,
        transfers_count=1,
        last_resolved_at="2024-01-15T10:30:00Z",
        on_call=True,
        pages_7d=0,
        active_items=2,
        similar_incident_score=0.92
    ),
    backup_human_ids=["test_human_2"],
    backup_features=[
        CandidateFeature(
            human_id="test_human_2",
            display_name="Bob Engineer",
            fit_score=0.75,
            resolves_count=8,
            transfers_count=2,
            on_call=False,
            pages_7d=5,
            active_items=5
        )
    ],
    constraints_checked=[
        ConstraintResult(name="on_call_required", passed=True),
        ConstraintResult(name="capacity_check", passed=True)
    ]
)

MOCK_LLM_RESPONSE = {
    "evidence": [
        {
            "type": "recent_resolution",
            "text": "Resolved 12 similar incidents in last 90 days",
            "time_window": "last 90 days",
            "source": "Learner stats"
        },
        {
            "type": "on_call",
            "text": "Currently on-call, matching the need for immediate response",
            "time_window": "current on-call shift",
            "source": "On-call status"
        },
        {
            "type": "similar_incident",
            "text": "High similarity score (0.92) to previously handled incidents",
            "time_window": "last 90 days",
            "source": "Vector similarity"
        }
    ],
    "why_not_next_best": "Higher fit score (0.85 vs 0.75) and currently on-call",
    "constraints_summary": [
        "on_call_required: passed",
        "capacity_check: passed"
    ]
}


@pytest.fixture
def client():
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_endpoint(self, client):
        """Health endpoint should return healthy status."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "explain"


class TestExplainDecision:
    """Test decision explanation."""
    
    def test_explain_decision_with_llm(self, client):
        """Explain service should generate evidence using LLM."""
        with patch('main.get_openai_client') as mock_get_client:
            mock_client = MagicMock()
            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = json.dumps(MOCK_LLM_RESPONSE)
            mock_client.chat.completions.create.return_value = mock_completion
            mock_get_client.return_value = mock_client
            
            response = client.post(
                "/explainDecision",
                json=MOCK_EXPLAIN_REQUEST.model_dump(),
                headers={"X-Correlation-ID": "test-correlation-123"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "evidence" in data
            assert len(data["evidence"]) > 0
            assert all("type" in ev and "text" in ev for ev in data["evidence"])
            assert "constraints" in data
            assert "why_not_next_best" in data
    
    def test_explain_decision_fallback_on_llm_failure(self, client):
        """Explain service should fallback to template if LLM fails."""
        with patch('main.get_openai_client') as mock_get_client:
            mock_get_client.side_effect = Exception("OpenAI API error")
            
            response = client.post("/explainDecision", json=MOCK_EXPLAIN_REQUEST.model_dump())
            
            # Should still return evidence (from template fallback)
            assert response.status_code == 200
            data = response.json()
            assert "evidence" in data
            assert len(data["evidence"]) > 0  # Template-based evidence
    
    def test_explain_decision_no_backup_humans(self, client):
        """Explain service should work without backup humans."""
        request = MOCK_EXPLAIN_REQUEST.model_dump()
        request["backup_human_ids"] = []
        request["backup_features"] = []
        
        with patch('main.get_openai_client') as mock_get_client:
            mock_client = MagicMock()
            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = json.dumps({
                "evidence": [{"type": "fit_score", "text": "High fit score", "time_window": "current", "source": "Learner"}],
                "why_not_next_best": "No backup candidates",
                "constraints_summary": []
            })
            mock_client.chat.completions.create.return_value = mock_completion
            mock_get_client.return_value = mock_client
            
            response = client.post("/explainDecision", json=request)
            
            assert response.status_code == 200
            data = response.json()
            assert "evidence" in data
    
    def test_explain_decision_invalid_llm_response(self, client):
        """Explain service should handle invalid LLM response."""
        with patch('main.get_openai_client') as mock_get_client:
            mock_client = MagicMock()
            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = "Invalid JSON response"
            mock_client.chat.completions.create.return_value = mock_completion
            mock_get_client.return_value = mock_client
            
            response = client.post("/explainDecision", json=MOCK_EXPLAIN_REQUEST.model_dump())
            
            # Should fallback to template
            assert response.status_code == 200
            data = response.json()
            assert "evidence" in data
    
    def test_explain_decision_missing_openai_key(self, client):
        """Explain service should handle missing OpenAI API key."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('main.get_openai_client') as mock_get_client:
                mock_get_client.side_effect = ValueError("OPENAI_API_KEY environment variable is required")
                
                response = client.post("/explainDecision", json=MOCK_EXPLAIN_REQUEST.model_dump())
                
                # Should fallback to template
                assert response.status_code == 200
                data = response.json()
                assert "evidence" in data


class TestEvidenceGeneration:
    """Test evidence generation logic."""
    
    def test_evidence_types(self, client):
        """Evidence should include various types."""
        with patch('main.get_openai_client') as mock_get_client:
            mock_client = MagicMock()
            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = json.dumps({
                "evidence": [
                    {"type": "recent_resolution", "text": "Resolved 12 items", "time_window": "last 90 days", "source": "Learner"},
                    {"type": "on_call", "text": "On-call", "time_window": "current", "source": "On-call status"},
                    {"type": "low_load", "text": "Low load", "time_window": "current", "source": "Load tracking"},
                    {"type": "similar_incident", "text": "Similar incidents", "time_window": "last 90 days", "source": "Vector similarity"},
                    {"type": "fit_score", "text": "High fit score", "time_window": "current", "source": "Learner"}
                ],
                "why_not_next_best": "Higher fit score",
                "constraints_summary": []
            })
            mock_client.chat.completions.create.return_value = mock_completion
            mock_get_client.return_value = mock_client
            
            response = client.post("/explainDecision", json=MOCK_EXPLAIN_REQUEST.model_dump())
            
            assert response.status_code == 200
            data = response.json()
            evidence_types = [ev["type"] for ev in data["evidence"]]
            assert "recent_resolution" in evidence_types or "fit_score" in evidence_types


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

