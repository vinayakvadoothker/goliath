"""
Stats calculation service - fit_score, time-windowed calculations, and decay.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from db import get_or_create_stats, get_service_stats

logger = logging.getLogger(__name__)


def calculate_fit_score(
    human_id: str,
    service: str,
    stats: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculate fit_score based on resolves and transfers (last 90 days) with time decay.
    
    Formula:
    - Base score: 0.5 (neutral)
    - Resolve boost: min(0.5, resolves_count * 0.05) - max +0.5 from resolves
    - Transfer penalty: min(0.3, transfers_count * 0.1) - max -0.3 from transfers
    - Recency boost: decays over 90 days
    - Time decay: 0.99^days_since_last_activity
    
    Args:
        human_id: Human ID
        service: Service name
        stats: Optional pre-fetched stats dict
    
    Returns:
        Fit score between 0.0 and 1.0
    """
    if stats is None:
        stats = get_or_create_stats(human_id, service)
    
    if not stats:
        return 0.5  # Default neutral score
    
    # Base score
    base_score = 0.5
    
    # Resolves boost (max +0.5)
    resolves_count = stats.get("resolves_count", 0)
    resolve_boost = min(0.5, resolves_count * 0.05)
    
    # Transfers penalty (max -0.3)
    transfers_count = stats.get("transfers_count", 0)
    transfer_penalty = min(0.3, transfers_count * 0.1)
    
    # Recency boost (expertise decays)
    last_resolved_at = stats.get("last_resolved_at")
    if last_resolved_at:
        if isinstance(last_resolved_at, str):
            last_resolved_at = datetime.fromisoformat(last_resolved_at.replace('Z', '+00:00'))
        days_since_last_resolve = (datetime.now() - last_resolved_at.replace(tzinfo=None)).days
        # Recency boost decays over 90 days
        recency_boost = max(0.0, 0.2 * (1 - days_since_last_resolve / 90))
    else:
        days_since_last_resolve = 90  # No recent activity
        recency_boost = 0.0
    
    # Calculate base fit_score
    fit_score = base_score + resolve_boost - transfer_penalty + recency_boost
    
    # Apply time decay (expertise fades over time)
    days_since_last_activity = days_since_last_resolve
    decay_factor = 0.99 ** days_since_last_activity  # 1% decay per day
    fit_score = fit_score * decay_factor
    
    # Clamp to valid range
    fit_score = max(0.0, min(1.0, fit_score))
    
    return fit_score


def get_time_windowed_stats(
    human_id: str,
    service: str,
    days: int = 90
) -> Dict[str, Any]:
    """
    Get stats for a human-service pair, only counting outcomes in the last N days.
    
    Args:
        human_id: Human ID
        service: Service name
        days: Number of days to look back (default: 90)
    
    Returns:
        Dict with time-windowed stats
    """
    stats = get_or_create_stats(human_id, service)
    if not stats:
        return {
            "resolves_count": 0,
            "transfers_count": 0,
            "last_resolved_at": None
        }
    
    cutoff_date = datetime.now() - timedelta(days=days)
    last_resolved_at = stats.get("last_resolved_at")
    
    # Filter by time window
    if last_resolved_at:
        if isinstance(last_resolved_at, str):
            last_resolved_at = datetime.fromisoformat(last_resolved_at.replace('Z', '+00:00'))
        
        if last_resolved_at.replace(tzinfo=None) < cutoff_date:
            # Last resolve is outside time window
            return {
                "resolves_count": 0,
                "transfers_count": 0,
                "last_resolved_at": None
            }
    
    # For now, we return the stats as-is
    # In a production system, we'd query resolved_edges and transferred_edges
    # with time filters to get accurate counts
    return {
        "resolves_count": stats.get("resolves_count", 0),
        "transfers_count": stats.get("transfers_count", 0),
        "last_resolved_at": stats.get("last_resolved_at")
    }


def calculate_recency_score(last_resolved_at: Optional[datetime]) -> float:
    """
    Calculate recency score (0.0-1.0) based on last resolved date.
    
    Args:
        last_resolved_at: Last resolved timestamp
    
    Returns:
        Recency score (1.0 = very recent, 0.0 = very old)
    """
    if not last_resolved_at:
        return 0.0
    
    if isinstance(last_resolved_at, str):
        last_resolved_at = datetime.fromisoformat(last_resolved_at.replace('Z', '+00:00'))
    
    days_ago = (datetime.now() - last_resolved_at.replace(tzinfo=None)).days
    
    # Score decays linearly over 90 days
    if days_ago >= 90:
        return 0.0
    elif days_ago <= 0:
        return 1.0
    else:
        return 1.0 - (days_ago / 90.0)


def apply_time_decay(score: float, days_since_activity: int) -> float:
    """
    Apply exponential time decay to a score.
    
    Args:
        score: Base score
        days_since_activity: Days since last activity
    
    Returns:
        Decayed score
    """
    decay_factor = 0.99 ** days_since_activity
    return score * decay_factor
