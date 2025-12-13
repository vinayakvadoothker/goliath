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

-- Decision Service Tables
CREATE TABLE IF NOT EXISTS decisions (
  id TEXT PRIMARY KEY,
  work_item_id TEXT UNIQUE NOT NULL,
  primary_human_id TEXT NOT NULL,
  backup_human_ids TEXT, -- JSON array
  confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY (work_item_id) REFERENCES work_items(id)
);

-- Decision candidates (for audit trail)
CREATE TABLE IF NOT EXISTS decision_candidates (
  decision_id TEXT NOT NULL,
  human_id TEXT NOT NULL,
  score REAL NOT NULL,
  rank INTEGER NOT NULL,
  filtered BOOLEAN DEFAULT FALSE,
  filter_reason TEXT,
  score_breakdown TEXT, -- JSON: {fit_score: 0.8, recency: 0.6, severity_match: 0.9, capacity: 0.7, vector_similarity: 0.85}
  PRIMARY KEY (decision_id, human_id),
  FOREIGN KEY (decision_id) REFERENCES decisions(id) ON DELETE CASCADE
);

-- Constraint results
CREATE TABLE IF NOT EXISTS constraint_results (
  decision_id TEXT NOT NULL,
  constraint_name TEXT NOT NULL,
  passed BOOLEAN NOT NULL,
  reason TEXT,
  PRIMARY KEY (decision_id, constraint_name),
  FOREIGN KEY (decision_id) REFERENCES decisions(id) ON DELETE CASCADE
);

-- Indexes for Decision Service
CREATE INDEX IF NOT EXISTS idx_decisions_work_item_id ON decisions(work_item_id);
CREATE INDEX IF NOT EXISTS idx_decisions_primary_human_id ON decisions(primary_human_id);
CREATE INDEX IF NOT EXISTS idx_decisions_created_at ON decisions(created_at);
CREATE INDEX IF NOT EXISTS idx_decision_candidates_decision_id ON decision_candidates(decision_id);
CREATE INDEX IF NOT EXISTS idx_decision_candidates_human_id ON decision_candidates(human_id);
CREATE INDEX IF NOT EXISTS idx_constraint_results_decision_id ON constraint_results(decision_id);

-- Learner Service Tables
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

CREATE TABLE IF NOT EXISTS human_load (
  human_id TEXT NOT NULL,
  pages_7d INTEGER DEFAULT 0,
  active_items INTEGER DEFAULT 0,
  last_updated TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (human_id),
  FOREIGN KEY (human_id) REFERENCES humans(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS outcomes_dedupe (
  event_id TEXT PRIMARY KEY,
  processed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for Learner Service
CREATE INDEX IF NOT EXISTS idx_human_service_stats_human_id ON human_service_stats(human_id);
CREATE INDEX IF NOT EXISTS idx_human_service_stats_service ON human_service_stats(service);
CREATE INDEX IF NOT EXISTS idx_human_service_stats_last_resolved_at ON human_service_stats(last_resolved_at);
CREATE INDEX IF NOT EXISTS idx_human_load_human_id ON human_load(human_id);
CREATE INDEX IF NOT EXISTS idx_outcomes_dedupe_event_id ON outcomes_dedupe(event_id);
CREATE INDEX IF NOT EXISTS idx_outcomes_dedupe_processed_at ON outcomes_dedupe(processed_at);

-- Executor Service: Executed Actions Table
CREATE TABLE IF NOT EXISTS executed_actions (
  id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL,
  jira_issue_key TEXT, -- e.g., "PROJ-123"
  jira_issue_id TEXT, -- Jira's internal ID
  assigned_human_id TEXT NOT NULL,
  backup_human_ids TEXT, -- JSON array
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  slack_message_id TEXT, -- If Slack notification sent
  fallback_message TEXT -- If Jira failed, store rendered message
);

-- Indexes for executed_actions
CREATE INDEX IF NOT EXISTS idx_executed_actions_decision_id ON executed_actions(decision_id);
CREATE INDEX IF NOT EXISTS idx_executed_actions_jira_issue_key ON executed_actions(jira_issue_key);
CREATE INDEX IF NOT EXISTS idx_executed_actions_assigned_human_id ON executed_actions(assigned_human_id);
CREATE INDEX IF NOT EXISTS idx_executed_actions_created_at ON executed_actions(created_at);

