-- Migration: Create outcome generation tables
-- Run this to enable outcome generation in Jira Simulator

-- Table to track issue history (status changes, assignee changes)
CREATE TABLE IF NOT EXISTS jira_issue_history (
    id SERIAL PRIMARY KEY,
    issue_key TEXT NOT NULL,
    field TEXT NOT NULL,  -- 'status', 'assignee', etc.
    from_value TEXT,
    to_value TEXT,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    changed_by TEXT,
    FOREIGN KEY (issue_key) REFERENCES jira_issues(key) ON DELETE CASCADE
);

-- Table to store generated outcomes (for deduplication)
CREATE TABLE IF NOT EXISTS jira_outcomes (
    event_id TEXT PRIMARY KEY,
    issue_key TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'resolved', 'reassigned'
    actor_id TEXT,  -- Who did the action
    service TEXT,
    timestamp TIMESTAMP NOT NULL,
    original_assignee_id TEXT,  -- For reassigned outcomes
    new_assignee_id TEXT,  -- For reassigned outcomes
    work_item_id TEXT,  -- Link to work_items table if exists
    processed BOOLEAN DEFAULT FALSE,  -- Whether Ingest has processed it
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (issue_key) REFERENCES jira_issues(key) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_jira_issue_history_issue_key ON jira_issue_history(issue_key);
CREATE INDEX IF NOT EXISTS idx_jira_issue_history_field ON jira_issue_history(field);
CREATE INDEX IF NOT EXISTS idx_jira_issue_history_changed_at ON jira_issue_history(changed_at);
CREATE INDEX IF NOT EXISTS idx_jira_outcomes_issue_key ON jira_outcomes(issue_key);
CREATE INDEX IF NOT EXISTS idx_jira_outcomes_type ON jira_outcomes(type);
CREATE INDEX IF NOT EXISTS idx_jira_outcomes_timestamp ON jira_outcomes(timestamp);
CREATE INDEX IF NOT EXISTS idx_jira_outcomes_processed ON jira_outcomes(processed);

-- Trigger to automatically create history entries when issues are updated
CREATE OR REPLACE FUNCTION track_issue_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Track status changes
    IF OLD.status_name IS DISTINCT FROM NEW.status_name THEN
        INSERT INTO jira_issue_history (issue_key, field, from_value, to_value, changed_at)
        VALUES (NEW.key, 'status', OLD.status_name, NEW.status_name, NOW());
        
        -- If status changed to Done, set resolved_at
        IF NEW.status_name = 'Done' AND OLD.status_name != 'Done' THEN
            NEW.resolved_at = NOW();
        END IF;
    END IF;
    
    -- Track assignee changes
    IF OLD.assignee_account_id IS DISTINCT FROM NEW.assignee_account_id THEN
        INSERT INTO jira_issue_history (issue_key, field, from_value, to_value, changed_at)
        VALUES (NEW.key, 'assignee', OLD.assignee_account_id, NEW.assignee_account_id, NOW());
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS issue_changes_trigger ON jira_issues;
CREATE TRIGGER issue_changes_trigger
    BEFORE UPDATE ON jira_issues
    FOR EACH ROW
    EXECUTE FUNCTION track_issue_changes();

