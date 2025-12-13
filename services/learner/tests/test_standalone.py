"""
Integration tests for Learner Service.
Tests core learning loop functionality with real database.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from outcome_service import process_outcome, _process_resolved_outcome, _process_reassigned_outcome
from stats_service import calculate_fit_score, get_time_windowed_stats
from db import (
    get_or_create_stats,
    check_outcome_processed,
    get_or_create_human,
    update_stats,
    get_or_create_load,
    create_resolved_edge,
    create_transferred_edge,
    mark_outcome_processed
)


# Mock data
MOCK_OUTCOME_RESOLVED = {
    "event_id": "test_resolved_1",
    "work_item_id": "wi_test_1",
    "type": "resolved",
    "actor_id": "human_1",
    "service": "api-service",
    "timestamp": datetime.now().isoformat()
}

MOCK_OUTCOME_REASSIGNED = {
    "event_id": "test_reassigned_1",
    "work_item_id": "wi_test_2",
    "type": "reassigned",
    "actor_id": "human_2",  # New assignee
    "original_assignee_id": "human_1",  # Original assignee
    "new_assignee_id": "human_2",
    "service": "api-service",
    "timestamp": datetime.now().isoformat()
}


class TestOutcomeProcessing:
    """Test outcome processing - THE learning loop with real database."""
    
    @pytest.mark.asyncio
    async def test_resolved_outcome_increases_fit_score(self):
        """Resolved outcome should increase fit_score."""
        # Create human and work item first (required for foreign keys)
        get_or_create_human("human_1", "Test Human", "test_account_1")
        from db import execute_update
        execute_update(
            "INSERT INTO work_items (id, type, service, severity, description) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            ["wi_test_1", "bug", "api-service", "sev2", "Test work item"]
        )
        
        # Mock only embedding update (doesn't need real Weaviate)
        with patch('outcome_service._update_human_embedding_from_resolution'):
            result = await process_outcome(MOCK_OUTCOME_RESOLVED)
            
            assert result["processed"] == True
            assert len(result["updates"]) == 1
            assert result["updates"][0]["fit_score_delta"] > 0  # Increased
            assert result["updates"][0]["resolves_count_delta"] == 1
            
            # Verify stats were actually updated in database
            stats = get_or_create_stats("human_1", "api-service")
            assert stats["resolves_count"] == 1
            assert stats["fit_score"] > 0.5  # Increased from 0.5
    
    @pytest.mark.asyncio
    async def test_reassigned_outcome_decreases_original_fit_score(self):
        """Reassigned outcome should decrease original assignee fit_score."""
        # Create humans first
        get_or_create_human("human_1", "Test Human 1", "test_account_1")
        get_or_create_human("human_2", "Test Human 2", "test_account_2")
        
        # Set initial stats
        update_stats("human_1", "api-service", fit_score=0.6)
        update_stats("human_2", "api-service", fit_score=0.5)
        
        # Create a work item for the edge
        from db import execute_update
        execute_update(
            "INSERT INTO work_items (id, type, service, severity, description) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            ["wi_test_2", "bug", "api-service", "sev2", "Test work item"]
        )
        
        result = await process_outcome(MOCK_OUTCOME_REASSIGNED)
        
        assert result["processed"] == True
        assert len(result["updates"]) == 2  # Original and new assignee
        
        # Original assignee should have negative delta
        original_update = next((u for u in result["updates"] if u["human_id"] == "human_1"), None)
        assert original_update is not None
        assert original_update["fit_score_delta"] < 0  # Decreased
        assert original_update["transfers_count_delta"] == 1
        
        # Verify in database
        original_stats = get_or_create_stats("human_1", "api-service")
        assert original_stats["transfers_count"] == 1
        assert original_stats["fit_score"] < 0.6  # Decreased from 0.6
        
        # New assignee should have positive delta
        new_update = next((u for u in result["updates"] if u["human_id"] == "human_2"), None)
        assert new_update is not None
        assert new_update["fit_score_delta"] > 0  # Increased slightly
        
        # Verify in database
        new_stats = get_or_create_stats("human_2", "api-service")
        assert new_stats["fit_score"] > 0.5  # Increased from 0.5
    
    @pytest.mark.asyncio
    async def test_outcome_idempotency(self):
        """Same event_id should not be processed twice."""
        # Create human and work item first
        get_or_create_human("human_1", "Test Human", "test_account_1")
        from db import execute_update
        execute_update(
            "INSERT INTO work_items (id, type, service, severity, description) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            ["wi_test_1", "bug", "api-service", "sev2", "Test work item"]
        )
        
        # Process outcome first time
        with patch('outcome_service._update_human_embedding_from_resolution'):
            result1 = await process_outcome(MOCK_OUTCOME_RESOLVED)
            assert result1["processed"] == True
        
        # Process same outcome again (should be idempotent)
        with patch('outcome_service._update_human_embedding_from_resolution'):
            result2 = await process_outcome(MOCK_OUTCOME_RESOLVED)
            assert result2["processed"] == False
            assert result2["reason"] == "Already processed"
        
        # Verify stats only updated once
        stats = get_or_create_stats("human_1", "api-service")
        assert stats["resolves_count"] == 1  # Not 2
    
    @pytest.mark.asyncio
    async def test_reassigned_without_original_assignee(self):
        """Reassigned outcome without original_assignee_id should still work."""
        outcome = {
            **MOCK_OUTCOME_REASSIGNED,
            "original_assignee_id": None  # Missing
        }
        
        # Create humans and work item
        get_or_create_human("human_1", "Test Human 1", "test_account_1")
        get_or_create_human("human_2", "Test Human 2", "test_account_2")
        from db import execute_update
        execute_update(
            "INSERT INTO work_items (id, type, service, severity, description) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            ["wi_test_2", "bug", "api-service", "sev2", "Test work item"]
        )
        
        # Mock Decision Service to return original assignee
        # Need to patch at the import site in outcome_service
        with patch('outcome_service.get_decision_by_work_item') as mock_get_decision:
            # Make it an async function that returns the decision
            async def mock_decision_func(*args):
                return {"primary_human_id": "human_1"}
            mock_get_decision.side_effect = mock_decision_func
            
            result = await process_outcome(outcome)
            
            # Should still process correctly
            assert result["processed"] == True
            # Should have called Decision Service to get original assignee
            mock_get_decision.assert_called_once_with("wi_test_2")
            
            # Verify both humans were updated
            assert len(result["updates"]) == 2


class TestFitScoreCalculation:
    """Test fit_score calculation with decay."""
    
    def test_fit_score_increases_with_resolves(self):
        """More resolves should increase fit_score."""
        stats1 = {"resolves_count": 0, "transfers_count": 0, "last_resolved_at": None}
        stats2 = {"resolves_count": 5, "transfers_count": 0, "last_resolved_at": datetime.now()}
        
        score1 = calculate_fit_score("human_1", "api-service", stats1)
        score2 = calculate_fit_score("human_1", "api-service", stats2)
        
        assert score2 > score1
    
    def test_fit_score_decreases_with_transfers(self):
        """More transfers should decrease fit_score."""
        stats1 = {"resolves_count": 5, "transfers_count": 0, "last_resolved_at": datetime.now()}
        stats2 = {"resolves_count": 5, "transfers_count": 3, "last_resolved_at": datetime.now()}
        
        score1 = calculate_fit_score("human_1", "api-service", stats1)
        score2 = calculate_fit_score("human_1", "api-service", stats2)
        
        assert score2 < score1
    
    def test_fit_score_decays_over_time(self):
        """Fit_score should decay when last_resolved_at is old."""
        recent = {"resolves_count": 5, "transfers_count": 0, "last_resolved_at": datetime.now()}
        old = {"resolves_count": 5, "transfers_count": 0, "last_resolved_at": datetime.now() - timedelta(days=60)}
        
        score_recent = calculate_fit_score("human_1", "api-service", recent)
        score_old = calculate_fit_score("human_1", "api-service", old)
        
        assert score_recent > score_old
    
    def test_fit_score_clamped_to_0_1(self):
        """Fit_score should always be between 0.0 and 1.0."""
        stats = {"resolves_count": 100, "transfers_count": 0, "last_resolved_at": datetime.now()}
        
        score = calculate_fit_score("human_1", "api-service", stats)
        
        assert 0.0 <= score <= 1.0


class TestTimeWindowedStats:
    """Test time-windowed calculations."""
    
    def test_time_windowed_stats_filters_old_data(self):
        """Should only count stats within time window."""
        # Create human and stats
        get_or_create_human("human_1", "Test Human", "test_account_1")
        # Set resolves_count to 5 and last_resolved_at to 10 days ago (within 90 day window)
        # First get stats to set initial values
        stats = get_or_create_stats("human_1", "api-service")
        # Then update with delta
        update_stats(
            "human_1", 
            "api-service", 
            fit_score=0.6,
            resolves_count_delta=5,
            last_resolved_at=datetime.now() - timedelta(days=10)
        )
        
        # Get updated stats to verify
        updated_stats = get_or_create_stats("human_1", "api-service")
        assert updated_stats["resolves_count"] == 5  # Should be 5 after delta
        
        # Now test time windowed stats
        stats = get_time_windowed_stats("human_1", "api-service", days=90)
        assert isinstance(stats, dict)
        assert "resolves_count" in stats
        assert "transfers_count" in stats
        # Since last_resolved_at is 10 days ago (within 90 days), stats should be returned
        # The function returns the stats if within window, so resolves_count should be 5
        assert stats["resolves_count"] == 5


class TestProfilesEndpoint:
    """Test GET /profiles endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_profiles_returns_humans(self):
        """GET /profiles should return humans with stats."""
        from main import get_profiles
        from jira_client import get_user_story_points, get_user_resolved_by_severity, get_user_on_call_status
        
        # Create human and stats in database
        # Need to set last_resolved_at so get_service_stats includes it (filters by last_resolved_at >= cutoff)
        get_or_create_human("human_1", "Alice", "test_account_1")
        # First create stats, then update with last_resolved_at
        stats = get_or_create_stats("human_1", "api-service")
        update_stats(
            "human_1",
            "api-service",
            fit_score=0.6,
            resolves_count_delta=5,
            transfers_count_delta=1,
            last_resolved_at=datetime.now() - timedelta(days=10)  # Within 90 day window
        )
        get_or_create_load("human_1")
        
        # Verify stats exist in database
        verify_stats = get_or_create_stats("human_1", "api-service")
        assert verify_stats["resolves_count"] == 5
        assert verify_stats["last_resolved_at"] is not None
        
        # Mock Jira client calls (external service)
        with patch('jira_client.get_user_story_points') as mock_story_points, \
             patch('jira_client.get_user_resolved_by_severity') as mock_severity, \
             patch('jira_client.get_user_on_call_status') as mock_on_call:
            
            mock_story_points.return_value = {"max_story_points": 21, "current_story_points": 8}
            mock_severity.return_value = {"sev1": 2, "sev2": 3, "sev3": 0, "sev4": 0}
            mock_on_call.return_value = True
            
            result = await get_profiles("api-service")
            
            assert "humans" in result
            assert len(result["humans"]) == 1
            assert result["humans"][0]["human_id"] == "human_1"
            assert result["humans"][0]["fit_score"] > 0
            assert result["humans"][0]["resolves_count"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

