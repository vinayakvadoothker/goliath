"""
Integration tests for Jira Simulator.
Tests service-to-service communication with Ingest Service.
"""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from datetime import datetime

from outcome_generator import OutcomeGenerator
from db import execute_query, execute_update


class TestJiraToIngestIntegration:
    """Test Jira Simulator → Ingest Service communication."""
    
    @pytest.mark.asyncio
    async def test_outcome_generator_calls_ingest(self):
        """Outcome generator successfully calls Ingest Service."""
        # Mock database query
        mock_outcomes = [
            {
                "key": "API-123",
                "assignee_account_id": "557058:user1",
                "project_key": "API",
                "resolved_at": datetime.now(),
                "changed_at": datetime.now()
            }
        ]
        
        with patch('outcome_generator.execute_query') as mock_query:
            mock_query.return_value = mock_outcomes
            
            # Mock Ingest Service call
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.raise_for_status = MagicMock()
                
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
                
                # Create outcome generator
                generator = OutcomeGenerator(
                    ingest_url="http://ingest:8000",
                    poll_interval=30
                )
                
                # Mock store and mark processed
                with patch.object(generator, '_store_outcome') as mock_store, \
                     patch.object(generator, '_mark_outcome_processed') as mock_mark:
                    
                    # Run check
                    await generator._check_for_outcomes()
                    
                    # Verify Ingest was called
                    assert mock_client.called
                    post_call = mock_client.return_value.__aenter__.return_value.post
                    assert post_call.called
                    
                    # Verify correct URL
                    call_args = post_call.call_args
                    assert "webhooks/jira" in str(call_args[0][0])
                    
                    # Verify payload structure
                    payload = call_args[1]["json"]
                    assert "outcome" in payload
                    assert payload["outcome"]["type"] == "resolved"
                    assert payload["outcome"]["issue_key"] == "API-123"
    
    @pytest.mark.asyncio
    async def test_outcome_generator_handles_ingest_timeout(self):
        """Outcome generator handles Ingest Service timeout gracefully."""
        mock_outcomes = [
            {
                "key": "API-123",
                "assignee_account_id": "557058:user1",
                "project_key": "API",
                "resolved_at": datetime.now(),
                "changed_at": datetime.now()
            }
        ]
        
        with patch('outcome_generator.execute_query') as mock_query:
            mock_query.return_value = mock_outcomes
            
            with patch('httpx.AsyncClient') as mock_client:
                from httpx import TimeoutException
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    side_effect=TimeoutException("Request timed out")
                )
                
                generator = OutcomeGenerator(
                    ingest_url="http://ingest:8000",
                    poll_interval=30
                )
                
                with patch.object(generator, '_store_outcome'):
                    # Should not raise exception, just log error
                    try:
                        await generator._check_for_outcomes()
                        # If we get here, it handled the timeout gracefully
                        assert True
                    except Exception as e:
                        pytest.fail(f"Should handle timeout gracefully, but raised: {e}")
    
    @pytest.mark.asyncio
    async def test_outcome_generator_handles_ingest_error(self):
        """Outcome generator handles Ingest Service 500 error."""
        mock_outcomes = [
            {
                "key": "API-123",
                "assignee_account_id": "557058:user1",
                "project_key": "API",
                "resolved_at": datetime.now(),
                "changed_at": datetime.now()
            }
        ]
        
        with patch('outcome_generator.execute_query') as mock_query:
            mock_query.return_value = mock_outcomes
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 500
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "Server error", request=MagicMock(), response=mock_response
                )
                
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
                
                generator = OutcomeGenerator(
                    ingest_url="http://ingest:8000",
                    poll_interval=30
                )
                
                with patch.object(generator, '_store_outcome'):
                    # Should not raise exception, just log error
                    try:
                        await generator._check_for_outcomes()
                        assert True
                    except Exception as e:
                        pytest.fail(f"Should handle error gracefully, but raised: {e}")


class TestOutcomePollingEndpoint:
    """Test GET /rest/api/3/outcomes/pending endpoint."""
    
    @pytest.mark.asyncio
    async def test_polling_endpoint_returns_outcomes(self):
        """Polling endpoint returns pending outcomes."""
        from main import app
        from fastapi.testclient import TestClient
        from unittest.mock import patch
        
        client = TestClient(app)
        
        # Mock database query
        mock_outcomes = [
            {
                "event_id": "jira-resolved-API-123-1234567890",
                "issue_key": "API-123",
                "type": "resolved",
                "actor_id": "557058:user1",
                "service": "api-service",
                "timestamp": datetime.now(),
                "original_assignee_id": None,
                "new_assignee_id": None,
                "work_item_id": None
            }
        ]
        
        with patch('main.execute_query') as mock_query:
            mock_query.return_value = mock_outcomes
            
            # Make request
            response = client.get("/rest/api/3/outcomes/pending?limit=50")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert "outcomes" in data
            assert "next_poll_after" in data
            assert len(data["outcomes"]) == 1
            assert data["outcomes"][0]["type"] == "resolved"
    
    @pytest.mark.asyncio
    async def test_polling_endpoint_filters_by_since(self):
        """Polling endpoint filters outcomes by since parameter."""
        from main import app
        from fastapi.testclient import TestClient
        from unittest.mock import patch
        
        client = TestClient(app)
        
        with patch('main.execute_query') as mock_query:
            mock_query.return_value = []
            
            # Make request with since parameter
            since = "2024-01-15T10:00:00Z"
            response = client.get(f"/rest/api/3/outcomes/pending?since={since}&limit=50")
            
            # Verify query was called with correct timestamp
            assert mock_query.called
            call_args = mock_query.call_args
            assert len(call_args[0][1]) >= 1  # Should have timestamp param


class TestEndToEndOutcomeFlow:
    """Test complete outcome generation flow."""
    
    @pytest.mark.asyncio
    async def test_issue_resolved_triggers_outcome(self):
        """When issue is marked Done, outcome is generated and sent to Ingest."""
        # This would require:
        # 1. Create issue via POST /rest/api/3/issue
        # 2. Update issue to Done via PUT /rest/api/3/issue/:key
        # 3. Wait for outcome generator to process
        # 4. Verify outcome was sent to Ingest
        # 5. Verify outcome appears in polling endpoint
        
        # For now, test the components separately
        # Full E2E test would require running all services
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

