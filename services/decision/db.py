"""
Database connection and query utilities for Decision Service.
"""
import os
import json
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Connection pool (initialized on first use)
_connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None


def get_db_connection():
    """Get database connection from pool."""
    global _connection_pool
    
    if _connection_pool is None:
        _init_connection_pool()
    
    return _connection_pool.getconn()


def return_db_connection(conn):
    """Return connection to pool."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.putconn(conn)


def _init_connection_pool():
    """Initialize PostgreSQL connection pool."""
    global _connection_pool
    
    postgres_url = os.getenv("POSTGRES_URL", "postgresql://goliath:goliath@postgres:5432/goliath")
    parsed = urlparse(postgres_url)
    
    try:
        _connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host=parsed.hostname or "postgres",
            port=parsed.port or 5432,
            database=parsed.path[1:] or "goliath",
            user=parsed.username or "goliath",
            password=parsed.password or "goliath",
            cursor_factory=RealDictCursor
        )
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database connection pool: {e}")
        raise


def execute_query(query: str, params: Optional[List] = None, commit: bool = False) -> List[Dict[str, Any]]:
    """
    Execute a SELECT query (or INSERT/UPDATE with RETURNING) and return results as list of dicts.
    
    Args:
        query: SQL query string
        params: Query parameters
        commit: Whether to commit the transaction (for INSERT/UPDATE with RETURNING)
    
    Returns:
        List of dictionaries (one per row)
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, params or [])
        results = cur.fetchall()
        if commit:
            conn.commit()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            return_db_connection(conn)


def execute_update(query: str, params: Optional[List] = None) -> int:
    """
    Execute an INSERT/UPDATE/DELETE query.
    
    Args:
        query: SQL query string
        params: Query parameters
    
    Returns:
        Number of rows affected
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, params or [])
        conn.commit()
        return cur.rowcount
    except Exception as e:
        logger.error(f"Update execution failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            return_db_connection(conn)


def get_work_item(work_item_id: str) -> Optional[Dict[str, Any]]:
    """Get work item from database."""
    query = """
        SELECT id, type, service, severity, description, raw_log, 
               story_points, impact, created_at, origin_system, creator_id, jira_issue_key
        FROM work_items
        WHERE id = %s
    """
    results = execute_query(query, [work_item_id])
    return results[0] if results else None


def save_decision(
    decision_id: str,
    work_item_id: str,
    primary_human_id: str,
    backup_human_ids: List[str],
    confidence: float
) -> None:
    """Save decision to database."""
    query = """
        INSERT INTO decisions (id, work_item_id, primary_human_id, backup_human_ids, confidence, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON CONFLICT (work_item_id) DO UPDATE
        SET primary_human_id = EXCLUDED.primary_human_id,
            backup_human_ids = EXCLUDED.backup_human_ids,
            confidence = EXCLUDED.confidence
    """
    backup_ids_json = json.dumps(backup_human_ids)
    execute_update(query, [decision_id, work_item_id, primary_human_id, backup_ids_json, confidence])


def save_decision_candidate(
    decision_id: str,
    human_id: str,
    score: float,
    rank: int,
    filtered: bool,
    filter_reason: Optional[str],
    score_breakdown: Dict[str, float]
) -> None:
    """Save decision candidate to audit trail."""
    query = """
        INSERT INTO decision_candidates 
        (decision_id, human_id, score, rank, filtered, filter_reason, score_breakdown)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (decision_id, human_id) DO UPDATE
        SET score = EXCLUDED.score,
            rank = EXCLUDED.rank,
            filtered = EXCLUDED.filtered,
            filter_reason = EXCLUDED.filter_reason,
            score_breakdown = EXCLUDED.score_breakdown
    """
    score_breakdown_json = json.dumps(score_breakdown)
    execute_update(query, [decision_id, human_id, score, rank, filtered, filter_reason, score_breakdown_json])


def save_constraint_result(
    decision_id: str,
    constraint_name: str,
    passed: bool,
    reason: Optional[str]
) -> None:
    """Save constraint check result."""
    query = """
        INSERT INTO constraint_results (decision_id, constraint_name, passed, reason)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (decision_id, constraint_name) DO UPDATE
        SET passed = EXCLUDED.passed,
            reason = EXCLUDED.reason
    """
    execute_update(query, [decision_id, constraint_name, passed, reason])


def get_decision(work_item_id: str) -> Optional[Dict[str, Any]]:
    """Get decision for a work item."""
    query = """
        SELECT id, work_item_id, primary_human_id, backup_human_ids, confidence, created_at
        FROM decisions
        WHERE work_item_id = %s
    """
    results = execute_query(query, [work_item_id])
    if results:
        result = dict(results[0])
        # Parse JSON backup_human_ids
        if result.get('backup_human_ids'):
            result['backup_human_ids'] = json.loads(result['backup_human_ids'])
        else:
            result['backup_human_ids'] = []
        return result
    return None


def get_decision_candidates(decision_id: str, service: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all candidates for a decision (audit trail) with human details.
    
    Args:
        decision_id: Decision ID
        service: Optional service name for filtering human_service_stats
    """
    # Get service from decision if not provided
    if not service:
        decision_query = "SELECT work_item_id FROM decisions WHERE id = %s"
        decision_result = execute_query(decision_query, [decision_id])
        if decision_result:
            work_item_id = decision_result[0]["work_item_id"]
            work_item_query = "SELECT service FROM work_items WHERE id = %s"
            work_item_result = execute_query(work_item_query, [work_item_id])
            if work_item_result:
                service = work_item_result[0]["service"]
    
    # Build query with service filter for human_service_stats
    if service:
        query = """
            SELECT 
                dc.human_id, 
                dc.score, 
                dc.rank, 
                dc.filtered, 
                dc.filter_reason, 
                dc.score_breakdown,
                h.display_name,
                h.jira_account_id,
                COALESCE(hss.fit_score, 0.5) as fit_score,
                COALESCE(hss.resolves_count, 0) as resolves_count,
                COALESCE(hss.transfers_count, 0) as transfers_count,
                hss.last_resolved_at,
                COALESCE(hl.pages_7d, 0) as pages_7d,
                COALESCE(hl.active_items, 0) as active_items
            FROM decision_candidates dc
            LEFT JOIN humans h ON dc.human_id = h.id
            LEFT JOIN human_service_stats hss ON dc.human_id = hss.human_id AND hss.service = %s
            LEFT JOIN human_load hl ON dc.human_id = hl.human_id
            WHERE dc.decision_id = %s
            ORDER BY dc.rank
        """
        results = execute_query(query, [service, decision_id])
    else:
        # Fallback if service not available
        query = """
            SELECT 
                dc.human_id, 
                dc.score, 
                dc.rank, 
                dc.filtered, 
                dc.filter_reason, 
                dc.score_breakdown,
                h.display_name,
                h.jira_account_id,
                0.5 as fit_score,
                0 as resolves_count,
                0 as transfers_count,
                NULL as last_resolved_at,
                COALESCE(hl.pages_7d, 0) as pages_7d,
                COALESCE(hl.active_items, 0) as active_items
            FROM decision_candidates dc
            LEFT JOIN humans h ON dc.human_id = h.id
            LEFT JOIN human_load hl ON dc.human_id = hl.human_id
            WHERE dc.decision_id = %s
            ORDER BY dc.rank
        """
        results = execute_query(query, [decision_id])
    
    candidates = []
    for row in results:
        candidate = dict(row)
        if candidate.get('score_breakdown'):
            candidate['score_breakdown'] = json.loads(candidate['score_breakdown'])
        else:
            candidate['score_breakdown'] = {}
        candidates.append(candidate)
    return candidates


def get_constraint_results(decision_id: str) -> List[Dict[str, Any]]:
    """Get all constraint results for a decision."""
    query = """
        SELECT constraint_name, passed, reason
        FROM constraint_results
        WHERE decision_id = %s
        ORDER BY constraint_name
    """
    results = execute_query(query, [decision_id])
    return [dict(row) for row in results]

