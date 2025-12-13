"""
Database connection and query utilities for Learner Service.
"""
import os
import json
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
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


def execute_transaction(queries: List[tuple]) -> None:
    """
    Execute multiple queries in a single transaction.
    
    Args:
        queries: List of (query, params) tuples
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for query, params in queries:
            cur.execute(query, params or [])
        conn.commit()
    except Exception as e:
        logger.error(f"Transaction execution failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            return_db_connection(conn)


def get_or_create_human(human_id: str, display_name: Optional[str] = None, jira_account_id: Optional[str] = None) -> Dict[str, Any]:
    """Get or create human record."""
    query = """
        INSERT INTO humans (id, display_name, jira_account_id)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET display_name = COALESCE(EXCLUDED.display_name, humans.display_name),
            jira_account_id = COALESCE(EXCLUDED.jira_account_id, humans.jira_account_id)
        RETURNING id, display_name, slack_handle, email, jira_account_id, embedding_3d_x, embedding_3d_y, embedding_3d_z
    """
    results = execute_query(query, [human_id, display_name, jira_account_id], commit=True)
    return results[0] if results else {}


def get_or_create_stats(human_id: str, service: str) -> Dict[str, Any]:
    """Get or create human_service_stats record."""
    query = """
        INSERT INTO human_service_stats (human_id, service, fit_score, resolves_count, transfers_count)
        VALUES (%s, %s, 0.5, 0, 0)
        ON CONFLICT (human_id, service) DO NOTHING
        RETURNING human_id, service, fit_score, resolves_count, transfers_count, last_resolved_at
    """
    results = execute_query(query, [human_id, service], commit=True)
    if results:
        return results[0]
    
    # If no result, fetch existing record
    query = """
        SELECT human_id, service, fit_score, resolves_count, transfers_count, last_resolved_at
        FROM human_service_stats
        WHERE human_id = %s AND service = %s
    """
    results = execute_query(query, [human_id, service])
    return results[0] if results else {}


def update_stats(
    human_id: str,
    service: str,
    fit_score: Optional[float] = None,
    resolves_count_delta: int = 0,
    transfers_count_delta: int = 0,
    last_resolved_at: Optional[datetime] = None
) -> None:
    """Update human_service_stats."""
    updates = []
    params = []
    
    if fit_score is not None:
        updates.append("fit_score = %s")
        params.append(max(0.0, min(1.0, fit_score)))
    
    if resolves_count_delta != 0:
        updates.append("resolves_count = resolves_count + %s")
        params.append(resolves_count_delta)
    
    if transfers_count_delta != 0:
        updates.append("transfers_count = transfers_count + %s")
        params.append(transfers_count_delta)
    
    if last_resolved_at is not None:
        updates.append("last_resolved_at = %s")
        params.append(last_resolved_at)
    
    if not updates:
        return
    
    params.extend([human_id, service])
    query = f"""
        UPDATE human_service_stats
        SET {', '.join(updates)}
        WHERE human_id = %s AND service = %s
    """
    execute_update(query, params)


def get_or_create_load(human_id: str) -> Dict[str, Any]:
    """Get or create human_load record."""
    query = """
        INSERT INTO human_load (human_id, pages_7d, active_items, last_updated)
        VALUES (%s, 0, 0, NOW())
        ON CONFLICT (human_id) DO NOTHING
        RETURNING human_id, pages_7d, active_items, last_updated
    """
    results = execute_query(query, [human_id], commit=True)
    if results:
        return results[0]
    
    query = """
        SELECT human_id, pages_7d, active_items, last_updated
        FROM human_load
        WHERE human_id = %s
    """
    results = execute_query(query, [human_id])
    return results[0] if results else {}


def update_load(human_id: str, pages_7d: Optional[int] = None, active_items_delta: int = 0) -> None:
    """Update human_load."""
    updates = []
    params = []
    
    if pages_7d is not None:
        updates.append("pages_7d = %s")
        params.append(pages_7d)
    
    if active_items_delta != 0:
        updates.append("active_items = GREATEST(0, active_items + %s)")
        params.append(active_items_delta)
    
    if not updates:
        return
    
    updates.append("last_updated = NOW()")
    params.append(human_id)
    
    query = f"""
        UPDATE human_load
        SET {', '.join(updates)}
        WHERE human_id = %s
    """
    execute_update(query, params)


def check_outcome_processed(event_id: str) -> bool:
    """Check if outcome has already been processed."""
    query = """
        SELECT event_id FROM outcomes_dedupe WHERE event_id = %s
    """
    results = execute_query(query, [event_id])
    return len(results) > 0


def mark_outcome_processed(event_id: str, timestamp: datetime) -> None:
    """Mark outcome as processed."""
    query = """
        INSERT INTO outcomes_dedupe (event_id, processed_at)
        VALUES (%s, %s)
        ON CONFLICT (event_id) DO NOTHING
    """
    execute_update(query, [event_id, timestamp])


def get_service_stats(service: str, days: int = 90) -> List[Dict[str, Any]]:
    """Get all human stats for a service (time-windowed)."""
    cutoff_date = datetime.now() - timedelta(days=days)
    query = """
        SELECT 
            hss.human_id,
            h.display_name,
            hss.service,
            hss.fit_score,
            hss.resolves_count,
            hss.transfers_count,
            hss.last_resolved_at
        FROM human_service_stats hss
        JOIN humans h ON h.id = hss.human_id
        WHERE hss.service = %s
        AND (hss.last_resolved_at IS NULL OR hss.last_resolved_at >= %s)
        ORDER BY hss.fit_score DESC
    """
    return execute_query(query, [service, cutoff_date])


def get_human_stats(human_id: str) -> Dict[str, Any]:
    """Get all stats for a human."""
    query = """
        SELECT 
            h.id as human_id,
            h.display_name,
            h.slack_handle,
            h.email,
            h.jira_account_id
        FROM humans h
        WHERE h.id = %s
    """
    results = execute_query(query, [human_id])
    if not results:
        return {}
    
    human = dict(results[0])
    
    # Get service stats
    query = """
        SELECT service, fit_score, resolves_count, transfers_count, last_resolved_at
        FROM human_service_stats
        WHERE human_id = %s
        ORDER BY fit_score DESC
    """
    service_stats = execute_query(query, [human_id])
    human['service_stats'] = [dict(row) for row in service_stats]
    
    # Get load
    query = """
        SELECT pages_7d, active_items, last_updated
        FROM human_load
        WHERE human_id = %s
    """
    load_results = execute_query(query, [human_id])
    human['load'] = dict(load_results[0]) if load_results else {"pages_7d": 0, "active_items": 0, "last_updated": None}
    
    return human


def create_resolved_edge(human_id: str, work_item_id: str, resolved_at: datetime) -> None:
    """Create resolved edge in knowledge graph."""
    query = """
        INSERT INTO resolved_edges (human_id, work_item_id, resolved_at)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    execute_update(query, [human_id, work_item_id, resolved_at])


def create_transferred_edge(work_item_id: str, from_human_id: str, to_human_id: str, transferred_at: datetime) -> None:
    """Create transferred edge in knowledge graph."""
    query = """
        INSERT INTO transferred_edges (work_item_id, from_human_id, to_human_id, transferred_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    execute_update(query, [work_item_id, from_human_id, to_human_id, transferred_at])


def get_resolved_work_items(human_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get resolved work items for a human (for embedding aggregation)."""
    query = """
        SELECT 
            re.work_item_id,
            re.resolved_at,
            wi.description,
            wi.service
        FROM resolved_edges re
        JOIN work_items wi ON wi.id = re.work_item_id
        WHERE re.human_id = %s
        ORDER BY re.resolved_at DESC
        LIMIT %s
    """
    return execute_query(query, [human_id, limit])


def update_human_3d_coords(human_id: str, x: float, y: float, z: float) -> None:
    """Update human 3D embedding coordinates."""
    query = """
        UPDATE humans
        SET embedding_3d_x = %s, embedding_3d_y = %s, embedding_3d_z = %s
        WHERE id = %s
    """
    execute_update(query, [x, y, z, human_id])
