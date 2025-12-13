# Complete Pipeline Guide: Seeding to Testing

## Overview

This guide explains:
1. **How user tasks are generated** (seeding process)
2. **How to test the entire pipeline** from Control Center

---

## Part 1: Generating User Tasks (Seeding Process)

### What Gets Created

When you run `make seed`, the system creates:

#### 1. **5 Specialized Users**

Each user has a specific role and expertise:

| User | Role | Service | Expertise |
|------|------|---------|-----------|
| **Agrim Dhingra** | Backend Engineer | `api-service` | API endpoints, authentication, rate limiting |
| **ishaanbansal.dev** | Frontend Engineer | `frontend-app` | React components, UI layout, accessibility |
| **Sahil Tallam** | DevOps Engineer | `infrastructure` | CI/CD, deployments, container orchestration |
| **sasankgamini** | Backend Engineer | `payment-service` | Payment processing, transactions, PCI compliance |
| **Vin Vadoothker** | Data Engineer | `data-pipeline` | ETL pipelines, data processing, batch jobs |

#### 2. **Historical Work (Closed Tickets)**

For each user:
- **30-50 closed tickets** (last 90 days)
- All marked as "Done" in Jira
- Matching their specialization (e.g., API issues for Agrim)
- Distributed over the last 90 days
- **WorkItems created via Ingest Service** (flows through full pipeline)
- **`resolved_edges` created** in database (links humans to resolved WorkItems)

#### 3. **Current Workload (Open Tickets)**

For each user:
- **5-10 open tickets**
- Some in "To Do", some in "In Progress"
- Matching their specialization
- **WorkItems created via Ingest Service**

### Step-by-Step Seeding Process

#### Step 1: Run Setup (First Time)

```bash
# This does everything automatically:
make setup
```

**What happens:**
1. ✅ Checks prerequisites
2. ✅ Creates `.env` file
3. ✅ Starts infrastructure (PostgreSQL, Weaviate)
4. ✅ **Runs `make seed`** - Creates 5 users + 200+ tickets
5. ✅ Starts all services
6. ✅ **Runs `make sync-learner`** - Processes closed tickets through Learner Service
7. ✅ Checks health

**Time:** ~5-10 minutes (depending on network speed if using real Jira)

#### Step 2: What the Seed Script Does

**File:** `scripts/seed_jira_data.py`

**Process:**

1. **Creates Users**
   - Creates users in Jira Simulator (or searches in real Jira)
   - Creates human records in main database (`humans` table)
   - Assigns consistent account IDs: `557058:user001`, `557058:user002`, etc.

2. **Creates Closed Tickets (Historical Data)**
   ```
   For each user (30-50 tickets):
     - Generate ticket matching their specialization
     - Set priority based on their severity focus (sev1/sev2/sev3)
     - Create in Jira (or Jira Simulator)
     - Transition to "Done" status
     - Create WorkItem via Ingest Service (POST /ingest/demo)
     - Create resolved_edge in database (links human to WorkItem)
   ```

3. **Creates Open Tickets (Current Workload)**
   ```
   For each user (5-10 tickets):
     - Generate ticket matching their specialization
     - Create in Jira (or Jira Simulator)
     - Randomly transition ~40% to "In Progress"
     - Create WorkItem via Ingest Service (POST /ingest/demo)
   ```

4. **Data Storage**
   - **Jira Simulator/Real Jira**: All issues stored
   - **PostgreSQL (work_items)**: All WorkItems stored
   - **PostgreSQL (humans)**: All users stored
   - **PostgreSQL (resolved_edges)**: Closed ticket relationships
   - **Weaviate**: WorkItem embeddings for similarity search

#### Step 3: Learner Service Processing

**What `make sync-learner` does:**

1. **Calls Learner Service** `POST /sync/jira`
   ```bash
   curl -X POST http://localhost:8003/sync/jira \
     -H "Content-Type: application/json" \
     -d '{"days_back": 90}'
   ```

2. **Learner Service Process:**
   - Reads all closed tickets from Jira (last 90 days)
   - For each closed ticket:
     - Gets assignee (human)
     - Maps project to service
     - Updates `human_service_stats`:
       - Increments `resolves_count`
       - Updates `last_resolved_at`
       - Calculates `fit_score` (with recency boost)
   - Builds capability profiles for each human per service

3. **Result:**
   - Each user now has capability profiles
   - `fit_score` reflects their expertise
   - `resolves_count` shows their experience
   - Decision Service can now route incidents correctly

### Verification After Seeding

```bash
# Check humans created
docker exec -it goliath-postgres psql -U goliath -d goliath -c \
  "SELECT id, display_name FROM humans LIMIT 10;"

# Check WorkItems created
curl http://localhost:8001/work-items?limit=10 | jq

# Check Learner Service profiles
curl "http://localhost:8003/profiles?service=api-service" | jq

# Check Jira issues (if using Jira Simulator)
curl "http://localhost:8080/rest/api/3/search?jql=order+by+created+DESC&maxResults=10" | jq
```

---

## Part 2: Testing the Entire Pipeline from Control Center

### Prerequisites

1. **Services Running:**
   ```bash
   make start
   # Or if you just ran make setup, services are already running
   ```

2. **Data Seeded:**
   ```bash
   # If you haven't seeded yet:
   make seed
   make sync-learner
   ```

3. **Access Control Center:**
   ```bash
   open http://localhost:6767
   ```

### Complete Pipeline Flow

When you trigger an error from Control Center, here's what happens:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER CLICKS ERROR BUTTON (Control Center UI)             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. CONTROL CENTER API                                       │
│    - Generates error message (e.g., "High error rate...")  │
│    - Calls Ingest Service POST /ingest/demo                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. INGEST SERVICE                                            │
│    - Preprocesses description with LLM                      │
│    - Generates embedding (384-dim)                          │
│    - Reduces to 3D (PCA)                                    │
│    - Stores in PostgreSQL (work_items table)               │
│    - Stores in Weaviate (for similarity search)              │
│    - AUTOMATIC: Calls Decision Service POST /decide        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. DECISION SERVICE                                          │
│    - Gets WorkItem from database                            │
│    - Searches Weaviate for similar incidents                │
│    - Gets human profiles from Learner Service               │
│    - Scores candidates (fit_score, recency, similarity)     │
│    - Checks constraints (capacity, on-call, load)          │
│    - Selects primary + backup assignees                     │
│    - Stores decision in database                             │
│    - AUTOMATIC: Calls Explain Service POST /explainDecision │
│    - AUTOMATIC: Calls Executor Service POST /executeDecision│
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. EXPLAIN SERVICE                                           │
│    - Generates evidence bullets using LLM                   │
│    - Explains why this human was selected                   │
│    - Returns evidence list                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. EXECUTOR SERVICE                                          │
│    - Creates Jira issue with assignee                       │
│    - Maps service → project key                             │
│    - Maps severity → priority                               │
│    - Maps human_id → Jira account_id                        │
│    - Creates issue in Jira (Simulator or Real Jira)         │
│    - Stores executed_action in database                      │
│    - Returns Jira issue key                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. CONTROL CENTER                                            │
│    - Polls Decision Service for decision                     │
│    - Polls Executor Service for Jira issue                   │
│    - Updates UI in real-time                                │
│    - Shows: Decision, Assignee, Evidence, Jira Key          │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step Testing Guide

#### Step 1: Open Control Center

```bash
# Access Control Center UI
open http://localhost:6767
```

You should see:
- Dashboard with system metrics
- Error trigger buttons
- Live log stream
- Incidents list
- Decisions panel

#### Step 2: Trigger an Error

**Click any error button**, for example:
- "High Error Rate" (sev1)
- "Database Timeout" (sev2)
- "Memory Leak" (sev1)

**What to watch:**
- Error appears in logs immediately
- Incident appears in incidents list
- Status changes: "detected" → "routing" → "assigned"

#### Step 3: Monitor the Pipeline

**In Control Center UI:**
- Watch the "Latest Decision" panel
- Should show:
  - Primary assignee (one of the 5 specialized users)
  - Confidence score
  - Evidence bullets
  - Jira issue key (e.g., "API-123")

**Expected Timeline:**
- **0-2 seconds**: WorkItem created
- **2-5 seconds**: Decision made
- **5-10 seconds**: Jira issue created
- **10-15 seconds**: UI updates with all information

#### Step 4: Verify Each Step

**Check Ingest Service:**
```bash
# View logs
make logs SERVICE=ingest

# Should see:
# - "WorkItem created successfully"
# - "Triggering decision for WorkItem {id}"
```

**Check Decision Service:**
```bash
# View logs
make logs SERVICE=decision

# Should see:
# - "Making decision for WorkItem {id}"
# - "Calling Explain Service..."
# - "Calling Executor Service..."
```

**Check Executor Service:**
```bash
# View logs
make logs SERVICE=executor

# Should see:
# - "Executing decision {id}"
# - "Jira issue created successfully: {key}"
```

**Check Jira:**
```bash
# If using Jira Simulator
curl "http://localhost:8080/rest/api/3/search?jql=order+by+created+DESC&maxResults=1" | jq

# Should see the newly created issue with assignee
```

#### Step 5: Verify Routing Correctness

**Check if the right person was assigned:**

```bash
# Get the decision
curl "http://localhost:8002/decisions/{work_item_id}" | jq

# Check the assignee's profile
curl "http://localhost:8003/profiles?service=api-service" | jq

# The assigned person should have:
# - High fit_score for that service
# - Recent resolves (last 90 days)
# - Matching expertise
```

**Example:**
- If you trigger an API error (`api-service`), it should route to **Agrim Dhingra** (API Backend Specialist)
- If you trigger a frontend error (`frontend-app`), it should route to **ishaanbansal.dev** (Frontend UI Specialist)

### Testing Different Scenarios

#### Scenario 1: API Error (Should Route to Agrim)

1. Click "High Error Rate" button
2. **Expected:** Routes to Agrim Dhingra (API Backend Specialist)
3. **Verify:**
   ```bash
   # Check decision
   curl "http://localhost:8002/decisions/{work_item_id}" | jq '.primary_human_id'
   # Should be Agrim's human_id
   ```

#### Scenario 2: Frontend Error (Should Route to ishaanbansal)

1. Create a custom error (or modify Control Center to trigger frontend errors)
2. **Expected:** Routes to ishaanbansal.dev (Frontend UI Specialist)

#### Scenario 3: Payment Error (Should Route to sasankgamini)

1. Trigger a payment-related error
2. **Expected:** Routes to sasankgamini (Payment Systems Specialist)

### Troubleshooting

#### Issue: Decision not being made

**Check:**
```bash
# Is Decision Service running?
curl http://localhost:8002/healthz

# Check logs
make logs SERVICE=decision

# Check if Ingest is calling Decision
make logs SERVICE=ingest | grep "Triggering decision"
```

#### Issue: Jira issue not created

**Check:**
```bash
# Is Executor Service running?
curl http://localhost:8004/healthz

# Check logs
make logs SERVICE=executor

# Check Jira configuration
# If using real Jira, verify JIRA_URL, JIRA_EMAIL, JIRA_API_KEY in .env
```

#### Issue: Wrong person assigned

**Check:**
```bash
# Check Learner Service profiles
curl "http://localhost:8003/profiles?service={service}" | jq

# Verify fit_scores are correct
# Verify seed data was processed (make sync-learner)
```

#### Issue: Control Center not updating

**Check:**
```bash
# Is Control Center API running?
curl http://localhost:8007/healthz

# Check WebSocket connection in browser console
# Should see WebSocket messages
```

### Complete Test Checklist

- [ ] Services running (`make start`)
- [ ] Data seeded (`make seed`)
- [ ] Learner synced (`make sync-learner`)
- [ ] Control Center accessible (`http://localhost:6767`)
- [ ] Error triggered successfully
- [ ] WorkItem created (check Ingest logs)
- [ ] Decision made (check Decision logs)
- [ ] Evidence generated (check Explain logs)
- [ ] Jira issue created (check Executor logs)
- [ ] Correct person assigned (check decision)
- [ ] UI updated with all information

---

## Summary

### Seeding Process:
1. `make setup` → Creates 5 users + 200+ tickets
2. `make sync-learner` → Processes closed tickets → Builds capability profiles
3. System ready for decision-making

### Testing Process:
1. Open Control Center (`http://localhost:6767`)
2. Trigger error → Watch automatic pipeline
3. Verify routing → Check logs and decisions
4. Confirm Jira issue created → Check Jira

**The entire pipeline is now automatic:**
- Ingest → Decision (automatic)
- Decision → Explain + Executor (automatic)
- Executor → Jira (automatic)

**No manual orchestration needed!** 🎉

