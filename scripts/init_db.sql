-- Goliath Database Initialization Script
-- This script runs automatically when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Knowledge Graph Tables (used by multiple services)
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

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_work_items_service ON work_items(service);
CREATE INDEX IF NOT EXISTS idx_work_items_severity ON work_items(severity);
CREATE INDEX IF NOT EXISTS idx_work_items_created_at ON work_items(created_at);
CREATE INDEX IF NOT EXISTS idx_work_items_jira_issue_key ON work_items(jira_issue_key);

CREATE INDEX IF NOT EXISTS idx_humans_jira_account_id ON humans(jira_account_id);

-- Knowledge graph edges
CREATE TABLE IF NOT EXISTS resolved_edges (
  id SERIAL PRIMARY KEY,
  human_id TEXT NOT NULL,
  work_item_id TEXT NOT NULL,
  resolved_at TIMESTAMP NOT NULL,
  FOREIGN KEY (work_item_id) REFERENCES work_items(id),
  FOREIGN KEY (human_id) REFERENCES humans(id)
);

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

CREATE TABLE IF NOT EXISTS co_worked_edges (
  id SERIAL PRIMARY KEY,
  human1_id TEXT NOT NULL,
  human2_id TEXT NOT NULL,
  work_item_id TEXT NOT NULL,
  worked_at TIMESTAMP NOT NULL,
  FOREIGN KEY (work_item_id) REFERENCES work_items(id),
  FOREIGN KEY (human1_id) REFERENCES humans(id),
  FOREIGN KEY (human2_id) REFERENCES humans(id)
);

-- Indexes for edges
CREATE INDEX IF NOT EXISTS idx_resolved_edges_human_id ON resolved_edges(human_id);
CREATE INDEX IF NOT EXISTS idx_resolved_edges_work_item_id ON resolved_edges(work_item_id);
CREATE INDEX IF NOT EXISTS idx_resolved_edges_resolved_at ON resolved_edges(resolved_at);

CREATE INDEX IF NOT EXISTS idx_transferred_edges_work_item_id ON transferred_edges(work_item_id);
CREATE INDEX IF NOT EXISTS idx_transferred_edges_from_human_id ON transferred_edges(from_human_id);
CREATE INDEX IF NOT EXISTS idx_transferred_edges_to_human_id ON transferred_edges(to_human_id);

CREATE INDEX IF NOT EXISTS idx_co_worked_edges_human1_id ON co_worked_edges(human1_id);
CREATE INDEX IF NOT EXISTS idx_co_worked_edges_human2_id ON co_worked_edges(human2_id);
CREATE INDEX IF NOT EXISTS idx_co_worked_edges_work_item_id ON co_worked_edges(work_item_id);

