"""
Database connection and query utilities for Ingest Service.
"""
import os
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
