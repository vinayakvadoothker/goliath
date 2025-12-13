"""
Integration tests for Decision Service.
Tests service-to-service communication with real or mocked dependencies.
"""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decision_engine import make_decision
from candidate_service import get_candidates
from db import get_work_item, save_decision


# Mock data
MOCK_WORK_ITEM = {
    "id": "wi_integration_1",
    "type": "incident",
    "service": "api-service",
    "severity": "sev1",
    "description": "High error rate on payment endpoint",
    "story_points": 5,
    "created_at": "2024-01-15T10:00:00Z"
}

MOCK_LEARNER_RESPONSE = {
    "profiles": [
        {
            "id": "human_1",
            "display_name": "Alice Engineer",
            "fit_score": 0.85,
            "resolves_count": 12,
            "transfers_count": 1,
            "on_call": True,
            "pages_7d": 2,
            "active_items": 3,
            "max_story_points": 21,
            "current_story_points": 8,
            "resolved_by_severity": {"sev1": 3, "sev2": 5, "sev3": 4, "sev4": 0}
        },
        {
            "id": "human_2",
            "display_name": "Bob Developer",
            "fit_score": 0.75,
            "resolves_count": 8,
            "transfers_count": 0,
            "on_call": False,
            "pages_7d": 5,
            "active_items": 2,
            "max_story_points": 21,
            "current_story_points": 12,
            "resolved_by_severity": {"sev1": 1, "sev2": 3, "sev3": 4, "sev4": 0}
        }
    ]
}


class TestDecisionToLearnerIntegration:
    """Test Decision Service → Learner Service communication."""
    
    @pytest.mark.asyncio
    async def test_get_candidates_calls_learner(self):
        """Decision Service successfully calls Learner Service."""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock successful Learner response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = MOCK_LEARNER_RESPONSE
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            # Call candidate service
            candidates = await get_candidates("api-service", use_fallback=False)
            
            # Verify Learner was called
            assert mock_client.called
            get_call = mock_client.return_value.__aenter__.return_value.get
            assert get_call.called
            
            # Verify correct URL and params
            call_args = get_call.call_args
            assert "profiles" in str(call_args[0][0])
            assert call_args[1]["params"]["service"] == "api-service"
            
            # Verify response
            assert len(candidates) == 2
            assert candidates[0]["id"] == "human_1"
            assert candidates[0]["fit_score"] == 0.85
    
    @pytest.mark.asyncio
    async def test_get_candidates_handles_learner_timeout(self):
        """Decision Service handles Learner Service timeout gracefully."""
        with patch('httpx.AsyncClient') as mock_client:
            from httpx import TimeoutException
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=TimeoutException("Request timed out")
            )
            
            # Should return empty list (or use fallback if enabled)
            candidates = await get_candidates("api-service", use_fallback=False)
            
            assert candidates == []
    
    @pytest.mark.asyncio
    async def test_get_candidates_handles_learner_error(self):
        """Decision Service handles Learner Service 500 error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server error", request=MagicMock(), response=mock_response
            )
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            candidates = await get_candidates("api-service", use_fallback=False)
            
            assert candidates == []
    
    @pytest.mark.asyncio
    async def test_get_candidates_fallback_when_learner_down(self):
        """Decision Service uses fallback when Learner is down."""
        with patch('httpx.AsyncClient') as mock_client:
            from httpx import TimeoutException
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=TimeoutException("Request timed out")
            )
            
            # Mock fallback
            with patch('candidate_service._get_fallback_candidates') as mock_fallback:
                mock_fallback.return_value = [
                    {
                        "id": "fallback_1",
                        "display_name": "Fallback User",
                        "fit_score": 0.5,
                        "resolves_count": 0,
                        "transfers_count": 0,
                        "on_call": False,
                        "pages_7d": 0,
                        "active_items": 0,
                        "max_story_points": 21,
                        "current_story_points": 0,
                        "resolved_by_severity": {"sev1": 0, "sev2": 0, "sev3": 0, "sev4": 0}
                    }
                ]
                
                candidates = await get_candidates("api-service", use_fallback=True)
                
                assert len(candidates) == 1
                assert candidates[0]["id"] == "fallback_1"
                mock_fallback.assert_called_once_with("api-service")


class TestEndToEndDecisionFlow:
    """Test complete decision flow with mocked dependencies."""
    
    @pytest.mark.asyncio
    async def test_make_decision_with_mocked_learner(self):
        """Full decision flow works with mocked Learner Service."""
        # Mock work item in database
        with patch('decision_engine.get_work_item') as mock_get_work_item:
            mock_get_work_item.return_value = MOCK_WORK_ITEM
            
            # Mock Learner Service
            with patch('candidate_service.get_candidates') as mock_get_candidates:
                mock_get_candidates.return_value = MOCK_LEARNER_RESPONSE["profiles"]
                
                # Mock embedding generation (non-blocking)
                with patch('decision_engine.generate_embedding') as mock_embedding:
                    mock_embedding.return_value = None
                    
                    # Mock Weaviate search
                    with patch('decision_engine.search_similar_work_items') as mock_search:
                        mock_search.return_value = []
                        
                        # Mock database saves
                        with patch('decision_engine.save_decision') as mock_save_decision, \
                             patch('decision_engine.save_decision_candidate') as mock_save_candidate, \
                             patch('decision_engine.save_constraint_result') as mock_save_constraint:
                            
                            # Make decision
                            decision = await make_decision("wi_integration_1")
                            
                            # Verify decision was made
                            assert decision is not None
                            assert decision["work_item_id"] == "wi_integration_1"
                            assert "primary_human_id" in decision
                            assert "confidence" in decision
                            
                            # Verify Learner was called
                            mock_get_candidates.assert_called_once_with("api-service", use_fallback=True)
                            
                            # Verify decision was saved
                            assert mock_save_decision.called


class TestDecisionServiceEndpoints:
    """Test Decision Service HTTP endpoints with mocked backend."""
    
    @pytest.mark.asyncio
    async def test_decide_endpoint_integration(self):
        """POST /decide endpoint works end-to-end."""
        from main import app
        from fastapi.testclient import TestClient
        from unittest.mock import patch
        
        client = TestClient(app)
        
        # Mock the decision engine
        with patch('main.make_decision') as mock_make_decision:
            mock_decision = {
                "id": "dec_test_1",
                "work_item_id": "wi_test_1",
                "primary_human_id": "human_1",
                "backup_human_ids": ["human_2"],
                "confidence": 0.85,
                "created_at": "2024-01-15T10:00:00Z"
            }
            mock_make_decision.return_value = mock_decision
            
            # Mock constraint results
            with patch('main.get_constraint_results') as mock_constraints:
                mock_constraints.return_value = [
                    {"constraint_name": "capacity", "passed": True, "reason": "All candidates have capacity"},
                    {"constraint_name": "availability", "passed": True, "reason": "All candidates available"}
                ]
                
                # Make request
                response = client.post(
                    "/decide",
                    json={"work_item_id": "wi_test_1"}
                )
                
                # Verify response
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == "dec_test_1"
                assert data["primary_human_id"] == "human_1"
                assert len(data["constraints_checked"]) == 2
                
                # Verify decision engine was called
                mock_make_decision.assert_called_once_with("wi_test_1")
    
    @pytest.mark.asyncio
    async def test_decide_endpoint_handles_learner_down(self):
        """POST /decide handles Learner Service being down."""
        from main import app
        from fastapi.testclient import TestClient
        from unittest.mock import patch
        
        client = TestClient(app)
        
        # Mock decision engine to raise error (simulating Learner down)
        with patch('main.make_decision') as mock_make_decision:
            mock_make_decision.side_effect = ValueError("No candidates found for service api-service. Learner Service may be down and no fallback candidates available.")
            
            # Make request
            response = client.post(
                "/decide",
                json={"work_item_id": "wi_test_1"}
            )
            
            # Should return 404 (work item not found) or 500 (service error)
            assert response.status_code in [404, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

