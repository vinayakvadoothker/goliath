-- Migration: Add PagerDuty support for incident ingestion
-- PagerDuty is used for incident detection/creation (ingestion), not execution
-- Jira is used for execution (assigning tickets)

-- Add PagerDuty incident ID to work_items table (to track which PagerDuty incident created this WorkItem)
ALTER TABLE work_items
ADD COLUMN IF NOT EXISTS pagerduty_incident_id TEXT;

-- Add index for PagerDuty incident lookup in work_items
CREATE INDEX IF NOT EXISTS idx_work_items_pagerduty_incident_id 
ON work_items(pagerduty_incident_id);

-- Note: PagerDuty user IDs can be stored in humans table if needed for future use
-- but are not required for the current architecture (Jira is used for execution)
ALTER TABLE humans
ADD COLUMN IF NOT EXISTS pagerduty_user_id TEXT;

CREATE INDEX IF NOT EXISTS idx_humans_pagerduty_user_id 
ON humans(pagerduty_user_id);
