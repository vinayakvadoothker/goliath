"""
Integration tests for Learner Service.
Tests service-to-service communication.
"""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import get_profiles, process_outcome_endpoint, sync_jira_endpoint
from outcome_service import process_outcome
from decision_client import get_decision_by_work_item


class TestLearnerToDecisionIntegration:
    """Test Learner Service → Decision Service communication."""
    
    @pytest.mark.asyncio
    async def test_get_decision_for_reassigned_outcome(self):
        """Learner Service successfully calls Decision Service for reassigned outcomes."""
        mock_decision = {
            "id": "dec_test_1",
            "work_item_id": "wi_test_1",
            "primary_human_id": "human_1",
            "backup_human_ids": ["human_2"],
            "confidence": 0.85
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_decision
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            decision = await get_decision_by_work_item("wi_test_1")
            
            assert decision is not None
            assert decision["primary_human_id"] == "human_1"
            assert mock_client.called
    
    @pytest.mark.asyncio
    async def test_get_decision_handles_404(self):
        """Learner Service handles Decision Service 404 gracefully."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not found", request=MagicMock(), response=mock_response
            )
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            decision = await get_decision_by_work_item("wi_nonexistent")
            
            assert decision is None


class TestLearnerToJiraIntegration:
    """Test Learner Service → Jira Simulator communication."""
    
    @pytest.mark.asyncio
    async def test_sync_jira_calls_jira_simulator(self):
        """POST /sync/jira successfully calls Jira Simulator."""
        from main import SyncJiraRequest, sync_jira_endpoint
        
        mock_jira_response = {
            "issues": [
                {
                    "id": "jira_1",
                    "key": "API-123",
                    "fields": {
                        "assignee": {"accountId": "557058:user1", "displayName": "Alice"},
                        "project": {"key": "API"},
                        "resolutiondate": "2024-01-10T14:20:00Z",
                        "status": {"name": "Done"},
                        "priority": {"name": "Critical"}
                    }
                }
            ],
            "total": 1
        }
        
        # Mock Jira client (external service)
        # Need to patch at the import site in main.py
        with patch('main.get_all_closed_tickets') as mock_get_tickets:
            # Return the list of issues directly (get_all_closed_tickets returns List[Dict])
            mock_get_tickets.return_value = mock_jira_response["issues"]
            
            request = SyncJiraRequest(project="API", days_back=90)
            result = await sync_jira_endpoint(request)
            
            # The sync should process the issue
            assert result["synced"] == 1
            assert result["humans_updated"] == 1
            mock_get_tickets.assert_called_once()
            
            # Verify human was created in database
            from db import get_or_create_human
            human = get_or_create_human("557058:user1", "Alice", "557058:user1")
            assert human["id"] == "557058:user1"
            
            # Verify stats were created
            from db import get_or_create_stats
            stats = get_or_create_stats("557058:user1", "api-service")
            assert stats["resolves_count"] > 0


class TestOutcomeProcessingIntegration:
    """Test outcome processing with real dependencies."""
    
    @pytest.mark.asyncio
    async def test_resolved_outcome_updates_stats(self):
        """Resolved outcome updates stats correctly."""
        from db import get_or_create_human, get_or_create_stats, execute_update
        
        outcome = {
            "event_id": "test_int_1",
            "work_item_id": "wi_int_1",
            "type": "resolved",
            "actor_id": "human_1",
            "service": "api-service",
            "timestamp": "2024-01-15T10:00:00Z"
        }
        
        # Create human and work item
        get_or_create_human("human_1", "Test Human", "test_account_1")
        execute_update(
            "INSERT INTO work_items (id, type, service, severity, description) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            ["wi_int_1", "bug", "api-service", "sev2", "Test work item"]
        )
        
        # Mock embedding update (doesn't need real Weaviate)
        with patch('outcome_service._update_human_embedding_from_resolution'):
            result = await process_outcome(outcome)
            
            assert result["processed"] == True
            
            # Verify stats were actually updated in database
            stats = get_or_create_stats("human_1", "api-service")
            assert stats["resolves_count"] == 1
            assert stats["fit_score"] == 0.6  # 0.5 + 0.1
    
    @pytest.mark.asyncio
    async def test_reassigned_outcome_with_decision_lookup(self):
        """Reassigned outcome looks up decision when original_assignee_id missing."""
        from db import get_or_create_human, get_or_create_stats, execute_update, update_stats
        
        outcome = {
            "event_id": "test_int_2",
            "work_item_id": "wi_int_2",
            "type": "reassigned",
            "actor_id": "human_2",  # New assignee
            "original_assignee_id": None,  # Missing - should look up
            "new_assignee_id": "human_2",
            "service": "api-service",
            "timestamp": "2024-01-15T10:00:00Z"
        }
        
        # Create humans and work item
        get_or_create_human("human_1", "Test Human 1", "test_account_1")
        get_or_create_human("human_2", "Test Human 2", "test_account_2")
        execute_update(
            "INSERT INTO work_items (id, type, service, severity, description) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            ["wi_int_2", "bug", "api-service", "sev2", "Test work item"]
        )
        
        # Set initial stats
        update_stats("human_1", "api-service", fit_score=0.6)
        update_stats("human_2", "api-service", fit_score=0.5)
        
        # Mock Decision Service to return original assignee
        # Need to patch at the import site in outcome_service
        with patch('outcome_service.get_decision_by_work_item') as mock_get_decision:
            # Make it an async function that returns the decision
            async def mock_decision_func(*args):
                return {"primary_human_id": "human_1"}
            mock_get_decision.side_effect = mock_decision_func
            
            result = await process_outcome(outcome)
            
            assert result["processed"] == True
            # Should have called Decision Service
            mock_get_decision.assert_called_once_with("wi_int_2")
            # Should have updated both original and new assignee
            assert len(result["updates"]) == 2
            
            # Verify in database
            original_stats = get_or_create_stats("human_1", "api-service")
            assert original_stats["transfers_count"] == 1
            assert original_stats["fit_score"] < 0.6  # Decreased
            
            new_stats = get_or_create_stats("human_2", "api-service")
            assert new_stats["fit_score"] > 0.5  # Increased


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

