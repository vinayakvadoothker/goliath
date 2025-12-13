# Jira Simulator Database Schema

**Complete database schema documentation for the Jira Simulator.**

## Overview

The Jira Simulator uses PostgreSQL to store:
- **Projects** (e.g., "api-service", "payment-service")
- **Users** (200 people with roles, capacity limits)
- **Issues** (tickets: bugs, tasks, stories with status, priority, story points)

All tables are created automatically by the seeding script (`scripts/seed_jira_data.py`) if they don't exist.

---

## Tables

### 1. `jira_projects`

**Purpose**: Stores Jira projects (each project = one service in Goliath)

```sql
CREATE TABLE jira_projects (
    key TEXT PRIMARY KEY,              -- Project key (e.g., "API", "PAYMENT")
    name TEXT NOT NULL,                -- Project name (e.g., "api-service")
    project_type_key TEXT NOT NULL     -- Always "software"
);
```

**Example Data:**
```
key      | name           | project_type_key
---------|----------------|------------------
API      | api-service    | software
PAYMENT  | payment-service| software
FRONTEND | frontend-app   | software
```

**Relationships:**
- One project has many issues (`jira_issues.project_key` → `jira_projects.key`)

---

### 2. `jira_users`

**Purpose**: Stores 200 people with their roles, capacity limits, and current load

```sql
CREATE TABLE jira_users (
    account_id TEXT PRIMARY KEY,           -- Jira account ID (e.g., "557058:abc12345")
    display_name TEXT NOT NULL,            -- Full name (e.g., "John Doe")
    email_address TEXT,                     -- Email address
    active BOOLEAN DEFAULT TRUE,           -- Is user active?
    max_story_points INTEGER DEFAULT 21,   -- Capacity limit (13, 21, or 34)
    current_story_points INTEGER DEFAULT 0, -- Currently assigned story points
    role TEXT                              -- Role (e.g., "backend-engineer", "sre")
);
```

**Example Data:**
```
account_id      | display_name | email              | active | max_story_points | current_story_points | role
----------------|--------------|--------------------|--------|------------------|----------------------|------------------
557058:abc12345 | John Doe     | john@example.com   | true   | 21               | 8                    | backend-engineer
557058:def67890 | Jane Smith   | jane@example.com   | true   | 13               | 13                   | frontend-engineer
557058:ghi11111 | Bob Wilson   | bob@example.com    | true   | 34               | 5                    | sre
```

**Key Fields Explained:**
- **`account_id`**: Jira-style account ID (format: `557058:xxxxx`). This is what the Jira API uses to identify users.
- **`max_story_points`**: Sprint capacity limit. Values: 13 (2-week sprint), 21 (3-week sprint), or 34 (5-week sprint).
- **`current_story_points`**: Sum of story points from all open issues assigned to this user.
- **`role`**: One of: `backend-engineer`, `frontend-engineer`, `sre`, `devops-engineer`, `product-manager`, `qa-engineer`, `data-engineer`, `security-engineer`

**Relationships:**
- One user can be assigned many issues (`jira_issues.assignee_account_id` → `jira_users.account_id`)
- One user can report many issues (`jira_issues.reporter_account_id` → `jira_users.account_id`)

**Capacity Logic:**
- When an issue is created with `status_name IN ('To Do', 'In Progress')` and has `story_points`, it counts toward `current_story_points`.
- When an issue is resolved (`status_name = 'Done'`), it no longer counts toward capacity.
- The Decision Engine uses `current_story_points < max_story_points` to check if a user has capacity.

---

### 3. `jira_issues`

**Purpose**: Stores all Jira issues (tickets) - both open and closed

```sql
CREATE TABLE jira_issues (
    id TEXT PRIMARY KEY,                    -- UUID (internal ID)
    key TEXT UNIQUE NOT NULL,               -- Issue key (e.g., "API-123", "PAYMENT-456")
    project_key TEXT NOT NULL,              -- Which project (FK to jira_projects)
    summary TEXT NOT NULL,                  -- Issue title
    description TEXT,                       -- Issue description
    issuetype_name TEXT NOT NULL,           -- "Bug", "Task", "Story", "Epic"
    priority_name TEXT NOT NULL,            -- "Critical", "High", "Medium", "Low"
    status_name TEXT NOT NULL,              -- "To Do", "In Progress", "Done", "Closed"
    assignee_account_id TEXT,               -- Who it's assigned to (FK to jira_users)
    reporter_account_id TEXT,               -- Who reported it (FK to jira_users)
    story_points INTEGER,                   -- Story points (NULL for bugs, 1-21 for stories/tasks)
    created_at TIMESTAMP NOT NULL,          -- When issue was created
    updated_at TIMESTAMP NOT NULL,          -- Last update time
    resolved_at TIMESTAMP,                  -- When issue was resolved (NULL if open)
    FOREIGN KEY (project_key) REFERENCES jira_projects(key),
    FOREIGN KEY (assignee_account_id) REFERENCES jira_users(account_id),
    FOREIGN KEY (reporter_account_id) REFERENCES jira_users(account_id)
);
```

**Example Data:**
```
id          | key      | project_key | summary              | issuetype_name | priority_name | status_name | assignee_account_id | story_points | created_at          | resolved_at
------------|----------|-------------|----------------------|----------------|---------------|-------------|---------------------|--------------|---------------------|---------------------
uuid-123    | API-123  | API         | Fix login bug        | Bug            | High          | Done        | 557058:abc12345     | NULL         | 2024-01-15 10:00:00 | 2024-01-16 14:30:00
uuid-456    | API-456  | API         | Add user endpoint    | Story          | Medium        | In Progress | 557058:abc12345     | 5            | 2024-01-20 09:00:00 | NULL
uuid-789    | PAY-789  | PAYMENT     | Payment processing   | Task           | Critical      | To Do      | 557058:def67890     | 8            | 2024-01-22 11:00:00 | NULL
```

**Key Fields Explained:**
- **`key`**: Human-readable issue key (e.g., "API-123"). This is what users see in Jira.
- **`issuetype_name`**: 
  - `Bug`: No story points (always NULL)
  - `Task`: Can have story points
  - `Story`: Can have story points
  - `Epic`: Large feature (not used in MVP)
- **`priority_name`**: Maps to severity in Goliath:
  - `Critical` → `sev1`
  - `High` → `sev2`
  - `Medium` → `sev3`
  - `Low` → `sev4`
- **`status_name`**:
  - `To Do`, `In Progress` → **Open** (counts toward capacity)
  - `Done`, `Closed` → **Closed** (doesn't count toward capacity, used for learning)
- **`story_points`**: 
  - NULL for bugs
  - 1, 2, 3, 5, 8, 13 for stories/tasks (Fibonacci sequence)
  - Used to calculate `current_story_points` for capacity checks
- **`resolved_at`**: 
  - NULL for open issues
  - Timestamp for closed issues
  - Used by Learner service to find issues resolved in last 90 days

**Relationships:**
- Belongs to one project (`project_key` → `jira_projects.key`)
- Assigned to one user (`assignee_account_id` → `jira_users.account_id`)
- Reported by one user (`reporter_account_id` → `jira_users.account_id`)

---

## Data Seeding

**Script**: `scripts/seed_jira_data.py`

**What it creates:**
1. **5 Projects** (one per service):
   - `API` → `api-service`
   - `PAYMENT` → `payment-service`
   - `FRONTEND` → `frontend-app`
   - `DATA` → `data-pipeline`
   - `INFRA` → `infrastructure`

2. **200 Users**:
   - Random names (using Faker)
   - Random roles (from 8 role types)
   - Random capacity (13, 21, or 34 story points)
   - Account IDs: `557058:xxxxx` format

3. **5000+ Closed Issues** (last 90 days):
   - Random project assignment
   - Random assignee
   - Random issue type (Bug, Task, Story)
   - Random priority
   - Status: `Done`
   - `resolved_at` set to random time in last 90 days
   - Story points assigned (except for bugs)

4. **1000+ Open Issues** (current capacity):
   - Random project assignment
   - Random assignee
   - Random issue type
   - Random priority
   - Status: `To Do` or `In Progress`
   - `resolved_at` = NULL
   - Story points assigned (except for bugs)
   - **Updates `current_story_points`** for assigned users

---

## How It Works

### 1. Capacity Tracking

**When an issue is created/updated:**
```sql
-- If issue is open (To Do, In Progress) and has story_points:
UPDATE jira_users
SET current_story_points = (
    SELECT COALESCE(SUM(story_points), 0)
    FROM jira_issues
    WHERE assignee_account_id = jira_users.account_id
    AND status_name IN ('To Do', 'In Progress')
)
WHERE account_id = '557058:abc12345';
```

**Decision Engine uses this to check capacity:**
```python
if user.current_story_points + work_item.story_points > user.max_story_points:
    # User doesn't have capacity
    filter_candidate(user, reason="capacity_exceeded")
```

### 2. Learning from Closed Issues

**Learner service queries closed issues:**
```sql
-- Get all issues resolved by a user in last 90 days
SELECT *
FROM jira_issues
WHERE assignee_account_id = '557058:abc12345'
AND status_name = 'Done'
AND resolved_at >= NOW() - INTERVAL '90 days'
AND project_key = 'API';  -- Filter by service
```

**This is used to calculate:**
- `fit_score`: Based on resolves vs transfers
- `resolves_count`: Number of resolved issues
- `last_resolved_at`: Most recent resolution

### 3. JQL Search (Jira Query Language)

**The Jira Simulator supports JQL queries like:**
```
project = API AND status = Done AND resolved >= -90d
assignee = 557058:abc12345 AND status IN (To Do, In Progress)
priority = Critical AND issuetype = Bug
```

**The simulator parses JQL and converts to SQL:**
```sql
-- JQL: project = API AND status = Done
SELECT * FROM jira_issues
WHERE project_key = 'API'
AND status_name = 'Done';
```

---

## Example Queries

### Get all open issues for a user
```sql
SELECT *
FROM jira_issues
WHERE assignee_account_id = '557058:abc12345'
AND status_name IN ('To Do', 'In Progress');
```

### Get user's current capacity
```sql
SELECT 
    display_name,
    current_story_points,
    max_story_points,
    (max_story_points - current_story_points) as available_capacity
FROM jira_users
WHERE account_id = '557058:abc12345';
```

### Get all issues resolved in last 30 days
```sql
SELECT *
FROM jira_issues
WHERE status_name = 'Done'
AND resolved_at >= NOW() - INTERVAL '30 days';
```

### Get issues by service (project)
```sql
SELECT i.*
FROM jira_issues i
JOIN jira_projects p ON i.project_key = p.key
WHERE p.name = 'api-service';
```

---

## Indexes (Recommended)

For performance, add these indexes:

```sql
CREATE INDEX idx_jira_issues_assignee ON jira_issues(assignee_account_id);
CREATE INDEX idx_jira_issues_status ON jira_issues(status_name);
CREATE INDEX idx_jira_issues_resolved_at ON jira_issues(resolved_at);
CREATE INDEX idx_jira_issues_project_key ON jira_issues(project_key);
CREATE INDEX idx_jira_issues_key ON jira_issues(key);
```

---

## Integration with Goliath Services

### Learner Service
- **Reads**: Closed issues (`status_name = 'Done'`) to learn capabilities
- **Queries**: `SELECT * FROM jira_issues WHERE assignee_account_id = ? AND status_name = 'Done' AND resolved_at >= ?`

### Decision Service
- **Reads**: User capacity (`current_story_points`, `max_story_points`) to filter candidates
- **Queries**: `SELECT current_story_points, max_story_points FROM jira_users WHERE account_id = ?`

### Executor Service
- **Writes**: Creates new issues when decisions are executed
- **Queries**: `INSERT INTO jira_issues (...) VALUES (...)`

---

## Notes

1. **Tables are created automatically** by the seeding script - no manual setup needed
2. **Foreign keys ensure data integrity** - can't create issue with invalid project or user
3. **Capacity is calculated** - `current_story_points` is updated when issues are created/updated
4. **Timestamps are in UTC** - all `created_at`, `updated_at`, `resolved_at` are UTC
5. **Account IDs are Jira-format** - `557058:xxxxx` format matches real Jira API

