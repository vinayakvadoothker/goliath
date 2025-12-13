"""
Pytest configuration and fixtures for Learner Service tests.
Sets up real database with schema initialization.
"""
import pytest
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse


@pytest.fixture(scope="session")
def db_connection():
    """Get database connection for test setup."""
    postgres_url = os.getenv("POSTGRES_URL", "postgresql://goliath:goliath@postgres:5432/goliath")
    parsed = urlparse(postgres_url)
    
    conn = psycopg2.connect(
        host=parsed.hostname or "postgres",
        port=parsed.port or 5432,
        database=parsed.path[1:] or "goliath",
        user=parsed.username or "goliath",
        password=parsed.password or "goliath"
    )
    return conn


@pytest.fixture(scope="session", autouse=True)
def init_database_schema(db_connection):
    """Initialize database schema before all tests run."""
    cursor = db_connection.cursor()
    
    # Always use inline schema (more reliable in Docker)
    schema_sql = """
        -- Create extensions
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        -- Work items (if not exists)
        CREATE TABLE IF NOT EXISTS work_items (
          id TEXT PRIMARY KEY,
          type TEXT NOT NULL,
          service TEXT NOT NULL,
          severity TEXT NOT NULL,
          description TEXT,
          raw_log TEXT,
          embedding_3d_x REAL,
          embedding_3d_y REAL,
          embedding_3d_z REAL,
          created_at TIMESTAMP NOT NULL DEFAULT NOW(),
          origin_system TEXT,
          creator_id TEXT,
          jira_issue_key TEXT,
          raw_payload TEXT,
          story_points INTEGER,
          impact TEXT
        );

        -- Humans (if not exists)
        CREATE TABLE IF NOT EXISTS humans (
          id TEXT PRIMARY KEY,
          display_name TEXT NOT NULL,
          slack_handle TEXT,
          email TEXT,
          jira_account_id TEXT,
          embedding_3d_x REAL,
          embedding_3d_y REAL,
          embedding_3d_z REAL
        );

        -- Human service stats
        CREATE TABLE IF NOT EXISTS human_service_stats (
          human_id TEXT NOT NULL,
          service TEXT NOT NULL,
          fit_score REAL DEFAULT 0.5 CHECK (fit_score >= 0 AND fit_score <= 1),
          resolves_count INTEGER DEFAULT 0,
          transfers_count INTEGER DEFAULT 0,
          last_resolved_at TIMESTAMP,
          PRIMARY KEY (human_id, service),
          FOREIGN KEY (human_id) REFERENCES humans(id) ON DELETE CASCADE
        );

        -- Human load
        CREATE TABLE IF NOT EXISTS human_load (
          human_id TEXT NOT NULL,
          pages_7d INTEGER DEFAULT 0,
          active_items INTEGER DEFAULT 0,
          last_updated TIMESTAMP NOT NULL DEFAULT NOW(),
          PRIMARY KEY (human_id),
          FOREIGN KEY (human_id) REFERENCES humans(id) ON DELETE CASCADE
        );

        -- Outcomes dedupe
        CREATE TABLE IF NOT EXISTS outcomes_dedupe (
          event_id TEXT PRIMARY KEY,
          processed_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        -- Resolved edges
        CREATE TABLE IF NOT EXISTS resolved_edges (
          id SERIAL PRIMARY KEY,
          human_id TEXT NOT NULL,
          work_item_id TEXT NOT NULL,
          resolved_at TIMESTAMP NOT NULL,
          FOREIGN KEY (work_item_id) REFERENCES work_items(id),
          FOREIGN KEY (human_id) REFERENCES humans(id)
        );

        -- Transferred edges
        CREATE TABLE IF NOT EXISTS transferred_edges (
          id SERIAL PRIMARY KEY,
          work_item_id TEXT NOT NULL,
          from_human_id TEXT NOT NULL,
          to_human_id TEXT NOT NULL,
          transferred_at TIMESTAMP NOT NULL,
          FOREIGN KEY (work_item_id) REFERENCES work_items(id),
          FOREIGN KEY (from_human_id) REFERENCES humans(id),
          FOREIGN KEY (to_human_id) REFERENCES humans(id)
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_human_service_stats_human_id ON human_service_stats(human_id);
        CREATE INDEX IF NOT EXISTS idx_human_service_stats_service ON human_service_stats(service);
        CREATE INDEX IF NOT EXISTS idx_human_load_human_id ON human_load(human_id);
        CREATE INDEX IF NOT EXISTS idx_outcomes_dedupe_event_id ON outcomes_dedupe(event_id);
        CREATE INDEX IF NOT EXISTS idx_resolved_edges_human_id ON resolved_edges(human_id);
        CREATE INDEX IF NOT EXISTS idx_transferred_edges_work_item_id ON transferred_edges(work_item_id);
        """
    
    # Execute schema creation
    try:
        cursor.execute(schema_sql)
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        # If tables already exist, that's fine
        if "already exists" not in str(e).lower():
            raise
    finally:
        cursor.close()
    
    yield
    
    # Cleanup: truncate tables after all tests
    cursor = db_connection.cursor()
    try:
        cursor.execute("""
            TRUNCATE TABLE 
                outcomes_dedupe,
                transferred_edges,
                resolved_edges,
                human_load,
                human_service_stats,
                humans,
                work_items
            CASCADE;
        """)
        db_connection.commit()
    finally:
        cursor.close()


@pytest.fixture(autouse=True)
def clean_database(db_connection):
    """Clean database before each test."""
    cursor = db_connection.cursor()
    cursor.execute("""
        TRUNCATE TABLE 
            outcomes_dedupe,
            transferred_edges,
            resolved_edges,
            human_load,
            human_service_stats
        CASCADE;
    """)
    # Don't truncate humans and work_items - they might be needed across tests
    db_connection.commit()
    cursor.close()
    yield
    # Cleanup after test
    cursor = db_connection.cursor()
    cursor.execute("""
        TRUNCATE TABLE 
            outcomes_dedupe,
            transferred_edges,
            resolved_edges,
            human_load,
            human_service_stats
        CASCADE;
    """)
    db_connection.commit()
    cursor.close()

