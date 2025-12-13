# Person 2: Learner Service

## Your Role

You own the **Learner Service** - the "memory" of the system. This service:

1. **Maintains capability profiles** - Tracks who can do what, based on Jira closed tickets
2. **Learns from outcomes** - When tasks are assigned/completed, updates fit_score, resolves_count, transfers_count
3. **Provides candidate data** - Decision service calls you to get humans with stats for routing

**Why you?** You own the learning/capability tracking - the core differentiator that makes Goliath get smarter over time.

---

## What You're Building

### Learner Service (`/services/learner/`)

**The Memory** - This service tracks:
- Who worked on what (from Jira closed tickets)
- When they worked on it (recency matters - expertise decays)
- Outcomes (resolved vs transferred - asymmetric learning)
- Load (pages_7d, active_items - don't interrupt overloaded people)
- Story points and capacity (for capacity matching)

**Why it exists:**
- **Capability modeling**: Tracks who can do what, based on actual work (not resumes)
- **Time-aware**: Stats decay over time (expertise drifts)
- **Outcome learning (CORE MVP FEATURE)**: 
  - When Jira issue is assigned/completed → Learner updates capability profiles
  - Resolved without transfer → fit_score increases (+0.1), resolves_count increases
  - Reassigned/transferred → fit_score decreases (-0.15), transfers_count increases
  - Future decisions → use updated fit_score → better routing over time
  - **This is THE moat**: System gets smarter with every assignment/completion
- **Jira as source of truth**: Jira closed tickets are the ground truth for "who can do what"

---

## Why You're Doing This

### The Learning Loop is THE Core Differentiator

**This is what makes Goliath special:**
1. System routes incident to Person A
2. Person A completes it → fit_score increases
3. Next similar incident → Person A is more likely to be chosen
4. If Person A transfers it → fit_score decreases
5. Next similar incident → System learned from mistake

**Without this, Goliath is just a routing system. With this, it's an intelligent system that gets better over time.**

---

## Complete Work Breakdown

### Hour 2-3: Service Scaffolding

**What to create:**
- `/services/learner/` - FastAPI service scaffold
- PostgreSQL schema: `humans`, `human_service_stats`, `human_load`, `outcomes_dedupe`, knowledge graph edges
- Weaviate schemas: `WorkItem`, `Human`
- `/healthz` endpoint
- Setup embedding generation pipeline (sentence-transformers)
- Setup PCA reduction for 3D coordinates (768D → 3D)

**Deliverables:**
- ✅ Service scaffolded
- ✅ Database schemas created
- ✅ Embedding pipeline set up

### Hour 4-6: Learner Service Foundation

**What to build:**
- `GET /profiles?service=X` - returns humans with stats for service
- `POST /outcomes` - updates stats idempotently (dedupe by event_id)
- `GET /stats?human_id=X` - returns stats for UI display
- `POST /sync/jira` - syncs closed Jira tickets to build capability profiles (background job)

**Deliverables:**
- ✅ All endpoints working
- ✅ Basic stats calculation

### Hour 20-24: Learner Service Completion

**What to complete:**
- Outcome processing logic
- Stats update algorithm
- Time-windowed calculations
- Seeding script improvements

**Deliverables:**
- ✅ Outcome processing complete
- ✅ Stats update algorithm working
- ✅ Time-windowed calculations implemented

---

## Database Schemas

### PostgreSQL Schema

```sql
-- Humans table
CREATE TABLE humans (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  slack_handle TEXT,
  email TEXT,
  jira_account_id TEXT, -- Jira accountId for API calls
  embedding_3d_x REAL, -- PCA-reduced 3D coordinates (aggregated from work items)
  embedding_3d_y REAL,
  embedding_3d_z REAL
);

-- Human capability stats (per service)
CREATE TABLE human_service_stats (
  human_id TEXT NOT NULL,
  service TEXT NOT NULL,
  fit_score REAL DEFAULT 0.5, -- 0-1, starts neutral
  resolves_count INTEGER DEFAULT 0,
  transfers_count INTEGER DEFAULT 0,
  last_resolved_at TIMESTAMP,
  PRIMARY KEY (human_id, service),
  FOREIGN KEY (human_id) REFERENCES humans(id)
);

-- Human load tracking
CREATE TABLE human_load (
  human_id TEXT NOT NULL,
  pages_7d INTEGER DEFAULT 0,
  active_items INTEGER DEFAULT 0,
  last_updated TIMESTAMP NOT NULL,
  PRIMARY KEY (human_id),
  FOREIGN KEY (human_id) REFERENCES humans(id)
);

-- Outcomes dedupe (idempotent processing)
CREATE TABLE outcomes_dedupe (
  event_id TEXT PRIMARY KEY,
  processed_at TIMESTAMP NOT NULL
);

-- Knowledge graph edges (temporal relationships)
CREATE TABLE resolved_edges (
  id SERIAL PRIMARY KEY,
  human_id TEXT NOT NULL,
  work_item_id TEXT NOT NULL,
  resolved_at TIMESTAMP NOT NULL,
  FOREIGN KEY (work_item_id) REFERENCES work_items(id)
);

CREATE TABLE transferred_edges (
  id SERIAL PRIMARY KEY,
  work_item_id TEXT NOT NULL,
  from_human_id TEXT NOT NULL,
  to_human_id TEXT NOT NULL,
  transferred_at TIMESTAMP NOT NULL,
  FOREIGN KEY (work_item_id) REFERENCES work_items(id)
);

CREATE TABLE co_worked_edges (
  id SERIAL PRIMARY KEY,
  human1_id TEXT NOT NULL,
  human2_id TEXT NOT NULL,
  work_item_id TEXT NOT NULL,
  worked_at TIMESTAMP NOT NULL,
  FOREIGN KEY (work_item_id) REFERENCES work_items(id)
);
```

### Weaviate Schema

```json
{
  "class": "Human",
  "vectorizer": "none",
  "properties": [
    {"name": "id", "dataType": ["string"]},
    {"name": "display_name", "dataType": ["string"]},
    {"name": "service", "dataType": ["string"]},
    {"name": "capability_summary", "dataType": ["text"]}
  ]
}
```

---

## API Endpoints

### `GET /profiles?service=X`

**Purpose**: Returns humans with capability stats for a service. Used by Decision service for candidate generation.

**Query Parameters:**
- `service`: string (required)

**Response (200 OK):**
```typescript
{
  service: string;
  humans: Array<{
    human_id: string;
    display_name: string;
    fit_score: number;        // 0.0-1.0, based on outcomes
    resolves_count: number;   // Last 90 days
    transfers_count: number;  // Last 90 days
    last_resolved_at?: string; // ISO 8601
    on_call: boolean;
    pages_7d: number;
    active_items: number;
    similar_incident_score?: number; // From vector similarity search
    max_story_points: number;  // Capacity limit
    current_story_points: number;  // Currently assigned
    resolved_by_severity: {  // NEW: Severity matching data
      sev1: number;
      sev2: number;
      sev3: number;
      sev4: number;
    };
  }>;
}
```

**Why these fields:**
- `fit_score`: Primary signal from outcomes (resolves boost, transfers penalize)
- `resolves_count`: How many they've resolved (capability indicator)
- `transfers_count`: How many they've transferred (negative signal)
- `last_resolved_at`: Recency (expertise decays)
- `on_call`: Availability signal
- `pages_7d`: Load signal (don't interrupt overloaded people)
- `active_items`: Current workload
- `resolved_by_severity`: For severity matching in Decision service

**Processing Logic:**
1. Query `human_service_stats` for service
2. Join with `human_load` for load data
3. Query Jira Simulator for current story points
4. Query Jira Simulator for resolved_by_severity breakdown
5. Apply time-windowed filtering (only last 90 days)
6. Return sorted by fit_score (descending)

**Error Responses:**
- `400 Bad Request`: Missing service parameter
- `500 Internal Server Error`: Database error

### `POST /outcomes`

**Purpose**: Updates capability profiles based on outcomes. **This is THE learning mechanism.**

**Request Body:**
```typescript
{
  event_id: string;        // Unique ID for dedupe (idempotent)
  decision_id?: string;    // Original decision (if reassigned)
  work_item_id: string;
  type: "resolved" | "reassigned" | "escalated";
  actor_id: string;        // Who performed the action
  service: string;
  timestamp: string;       // ISO 8601
  new_assignee_id?: string; // If reassigned
}
```

**Response (200 OK):**
```typescript
{
  processed: boolean;
  event_id: string;
  updates: Array<{
    human_id: string;
    fit_score_delta: number;  // Change in fit_score
    resolves_count_delta?: number;
    transfers_count_delta?: number;
  }>;
  message: "Stats updated successfully"
}
```

**Processing Logic:**

```python
def process_outcome(outcome: Outcome):
    # Dedupe check
    if outcomes_dedupe.exists(outcome.event_id):
        return  # already processed
    
    # Update stats
    if outcome.type == 'resolved':
        stats = get_stats(outcome.actor_id, outcome.service)
        stats.resolves_count += 1
        stats.fit_score = min(1.0, stats.fit_score + 0.1)  # boost
        stats.last_resolved_at = outcome.timestamp
        
        # Create RESOLVED edge in knowledge graph
        create_resolved_edge(outcome.actor_id, outcome.work_item_id, outcome.timestamp)
        
        # Update human embedding in Weaviate
        update_human_embedding(outcome.actor_id, outcome.work_item_id)
        
    elif outcome.type == 'reassigned':
        # Original assignee: penalty
        original_decision = get_decision(outcome.decision_id)
        stats = get_stats(original_decision.primary_human_id, outcome.service)
        stats.transfers_count += 1
        stats.fit_score = max(0.0, stats.fit_score - 0.15)  # penalty
        
        # New assignee: slight boost (they accepted it)
        new_stats = get_stats(outcome.actor_id, outcome.service)
        new_stats.fit_score = min(1.0, new_stats.fit_score + 0.05)
        
        # Create TRANSFERRED edge in knowledge graph
        create_transferred_edge(
            outcome.work_item_id,
            original_decision.primary_human_id,
            outcome.actor_id,
            outcome.timestamp
        )
    
    # Update load
    load = get_load(outcome.actor_id)
    if outcome.type == 'resolved':
        load.active_items = max(0, load.active_items - 1)
    
    # Mark processed
    outcomes_dedupe.insert(outcome.event_id, outcome.timestamp)
```

**Why these deltas:**
- **Asymmetric**: Transfers are worse than resolves (penalty is larger: -0.15 vs +0.1)
- **Time-aware**: Old outcomes decay (multiply by 0.99 per day)
- **Dedupe**: Idempotent updates prevent double-counting

**Error Responses:**
- `400 Bad Request`: Invalid outcome type or missing fields
- `409 Conflict`: Event already processed (idempotent)

### `GET /stats?human_id=X`

**Purpose**: Returns stats for a human. Used by UI to display capability profiles.

**Query Parameters:**
- `human_id`: string (required)

**Response (200 OK):**
```typescript
{
  human_id: string;
  display_name: string;
  service_stats: Array<{
    service: string;
    fit_score: number;
    resolves_count: number;
    transfers_count: number;
    last_resolved_at?: string;
  }>;
  load: {
    pages_7d: number;
    active_items: number;
    last_updated: string;
  };
}
```

**Error Responses:**
- `400 Bad Request`: Missing human_id
- `404 Not Found`: Human doesn't exist

### `POST /sync/jira`

**Purpose**: Syncs closed Jira tickets to build initial capability profiles. Background job.

**Request Body (optional):**
```typescript
{
  project?: string;        // Specific project, or all if omitted
  days_back?: number;     // Default: 90
}
```

**Response (200 OK):**
```typescript
{
  synced: number;          // Number of tickets synced
  humans_updated: number;
  message: "Sync completed successfully"
}
```

**Processing Logic:**
1. Query Jira Simulator: `GET /rest/api/3/search?jql=project=PROJ AND status=Done AND resolved >= -90d`
2. For each closed ticket:
   - Extract assignee, project, resolution date
   - LLM extracts entities from description (optional, for better matching)
   - Update human capability profiles
3. Calculate initial fit_score based on resolve count + recency

**Jira Integration (READ) - Uses Person 1's Jira Simulator:**
- **Purpose**: Read closed Jira tickets to determine capability and recency
- **Jira API Query**: `GET /rest/api/3/search?jql=project=PROJ AND status=Done AND resolved >= -90d`
- **Note**: Calls Person 1's Jira Simulator service (not real Jira)
- **What we extract**:
  - `issue.fields.assignee.accountId` → human_id
  - `issue.fields.project.key` → service
  - `issue.fields.resolutiondate` → last_resolved_at
  - `issue.fields.status.name` → outcome (Done=resolved, Closed=resolved)
  - `issue.fields.issuetype.name` → work type (Bug, Task, Story)
  - `issue.fields.priority.name` → severity (Critical=sev1, High=sev2, etc.)
- **LLM Usage for Entity Extraction**:
  - Instead of hardcoded pattern matching, use LLM to extract structured entities from ticket descriptions
  - **Prompt**: "Extract entities from this Jira ticket description: [description]. Return JSON: {service_components: [], error_types: [], affected_systems: []}"
  - **Why**: Flexible, handles variations in how people write tickets
  - **Deterministic**: Same input → same output (with temperature=0)
  - **Auditable**: Store LLM response in audit trail
- **How we use it**:
  - Count resolves per human per service (last 90 days)
  - Track recency (most recent resolve date)
  - Calculate fit_score based on resolve count + recency
  - Track teams (from Jira project → team mapping)
  - Track resolved_by_severity (for severity matching)
  - **LLM-extracted entities** used for similar incident matching (not keyword matching)
- **Sync strategy**:
  - Initial sync: Pull last 90 days of closed tickets
  - Incremental: Poll every 5 minutes for new closed tickets
  - Cache in PostgreSQL to avoid hitting Jira API constantly

---

## Algorithms

### Time-Windowed Calculations

```python
def calculate_fit_score(human_id: string, service: string) -> float:
    """Calculate fit_score based on resolves and transfers (last 90 days)."""
    stats = get_stats(human_id, service)
    
    # Base score from outcomes
    base_score = 0.5  # Neutral starting point
    
    # Resolves boost
    resolve_boost = min(0.5, stats.resolves_count * 0.05)  # Max +0.5 from resolves
    
    # Transfers penalty
    transfer_penalty = min(0.3, stats.transfers_count * 0.1)  # Max -0.3 from transfers
    
    # Recency boost (expertise decays)
    days_since_last_resolve = (datetime.now() - stats.last_resolved_at).days if stats.last_resolved_at else 90
    recency_boost = max(0.0, 0.2 * (1 - days_since_last_resolve / 90))  # Decays over 90 days
    
    fit_score = base_score + resolve_boost - transfer_penalty + recency_boost
    
    # Apply time decay (expertise fades)
    days_since_last_activity = days_since_last_resolve
    decay_factor = 0.99 ** days_since_last_activity  # 1% decay per day
    fit_score = fit_score * decay_factor
    
    return max(0.0, min(1.0, fit_score))
```

### Outcome Processing

```python
def process_outcome(outcome: Outcome):
    """Process outcome and update stats (idempotent)."""
    # Dedupe check
    if outcomes_dedupe.exists(outcome.event_id):
        return {'processed': False, 'reason': 'Already processed'}
    
    updates = []
    
    if outcome.type == 'resolved':
        # Get or create stats
        stats = get_or_create_stats(outcome.actor_id, outcome.service)
        
        # Update stats
        old_fit_score = stats.fit_score
        stats.resolves_count += 1
        stats.fit_score = min(1.0, stats.fit_score + 0.1)  # boost
        stats.last_resolved_at = outcome.timestamp
        stats.save()
        
        # Create RESOLVED edge in knowledge graph
        create_resolved_edge(outcome.actor_id, outcome.work_item_id, outcome.timestamp)
        
        # Update human embedding in Weaviate
        update_human_embedding(outcome.actor_id, outcome.work_item_id)
        
        updates.append({
            'human_id': outcome.actor_id,
            'fit_score_delta': stats.fit_score - old_fit_score,
            'resolves_count_delta': 1
        })
        
    elif outcome.type == 'reassigned':
        # Get original decision
        original_decision = get_decision(outcome.decision_id)
        original_assignee_id = original_decision.primary_human_id
        
        # Original assignee: penalty
        original_stats = get_or_create_stats(original_assignee_id, outcome.service)
        old_fit_score = original_stats.fit_score
        original_stats.transfers_count += 1
        original_stats.fit_score = max(0.0, original_stats.fit_score - 0.15)  # penalty
        original_stats.save()
        
        updates.append({
            'human_id': original_assignee_id,
            'fit_score_delta': original_stats.fit_score - old_fit_score,
            'transfers_count_delta': 1
        })
        
        # New assignee: slight boost (they accepted it)
        new_stats = get_or_create_stats(outcome.actor_id, outcome.service)
        old_fit_score_new = new_stats.fit_score
        new_stats.fit_score = min(1.0, new_stats.fit_score + 0.05)
        new_stats.save()
        
        updates.append({
            'human_id': outcome.actor_id,
            'fit_score_delta': new_stats.fit_score - old_fit_score_new
        })
        
        # Create TRANSFERRED edge in knowledge graph
        create_transferred_edge(
            outcome.work_item_id,
            original_assignee_id,
            outcome.actor_id,
            outcome.timestamp
        )
    
    # Update load
    load = get_or_create_load(outcome.actor_id)
    if outcome.type == 'resolved':
        load.active_items = max(0, load.active_items - 1)
    load.last_updated = outcome.timestamp
    load.save()
    
    # Mark processed
    outcomes_dedupe.insert(outcome.event_id, outcome.timestamp)
    
    return {'processed': True, 'updates': updates}
```

### Human Embedding Updates

```python
def update_human_embedding(human_id: string, work_item_id: string):
    """Update human embedding in Weaviate based on resolved work items."""
    # Get all resolved work items for this human
    resolved_items = get_resolved_work_items(human_id)
    
    # Generate embeddings for all resolved items
    embeddings = [generate_embedding(item.description) for item in resolved_items]
    
    # Aggregate (weighted average, more recent = higher weight)
    weights = [1.0 / (i + 1) for i in range(len(embeddings))]  # More recent = higher weight
    aggregated_embedding = np.average(embeddings, axis=0, weights=weights)
    
    # Reduce to 3D for visualization
    embedding_3d = pca_reduce(aggregated_embedding)  # 768D → 3D
    
    # Update Weaviate
    weaviate_client.data_object.update(
        uuid=human_id,
        class_name="Human",
        data_object={
            "id": human_id,
            "capability_summary": generate_capability_summary(resolved_items)
        },
        vector=aggregated_embedding
    )
    
    # Update PostgreSQL with 3D coordinates
    update_human_3d_coords(human_id, embedding_3d)
```

---

## How to Test

### Standalone Testing (Without Other Services)

**1. Create test script: `/services/learner/scripts/test_standalone.sh`**

```bash
#!/bin/bash
# Test Learner service standalone

# Start PostgreSQL and Weaviate
docker-compose -f docker-compose.test.yml up -d postgres weaviate

# Wait for services to be ready
sleep 5

# Run tests
pytest tests/test_learner_standalone.py

# Cleanup
docker-compose -f docker-compose.test.yml down
```

**2. Create mock data: `/services/learner/scripts/mock_data.json`**

```json
{
  "humans": [
    {
      "id": "human_1",
      "display_name": "Alice Engineer",
      "jira_account_id": "557058:abc123",
      "slack_handle": "@alice",
      "email": "alice@example.com"
    }
  ],
  "outcomes": [
    {
      "event_id": "outcome_1",
      "work_item_id": "wi_1",
      "type": "resolved",
      "actor_id": "human_1",
      "service": "api-service",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**3. Test cases:**

```python
# tests/test_learner_standalone.py

def test_outcome_processing_resolved():
    """Resolved outcome increases fit_score."""
    outcome = create_outcome(type="resolved", actor_id="human_1", service="api-service")
    
    # Process outcome
    result = learner_service.process_outcome(outcome)
    
    # Check stats updated
    stats = learner_service.get_stats("human_1", "api-service")
    assert stats.fit_score > 0.5  # Increased from neutral
    assert stats.resolves_count == 1
    assert stats.transfers_count == 0

def test_outcome_processing_reassigned():
    """Reassigned outcome decreases original assignee fit_score."""
    # Create decision
    decision = create_decision(primary_human_id="human_1")
    
    # Process reassigned outcome
    outcome = create_outcome(
        type="reassigned",
        decision_id=decision.id,
        actor_id="human_2",  # New assignee
        service="api-service"
    )
    
    result = learner_service.process_outcome(outcome)
    
    # Original assignee: penalty
    original_stats = learner_service.get_stats("human_1", "api-service")
    assert original_stats.fit_score < 0.5  # Decreased from neutral
    assert original_stats.transfers_count == 1
    
    # New assignee: slight boost
    new_stats = learner_service.get_stats("human_2", "api-service")
    assert new_stats.fit_score > 0.5  # Increased slightly

def test_outcome_idempotency():
    """Same event_id = no duplicate update."""
    outcome = create_outcome(event_id="test_1", type="resolved")
    
    # Process twice
    result1 = learner_service.process_outcome(outcome)
    result2 = learner_service.process_outcome(outcome)
    
    assert result1['processed'] == True
    assert result2['processed'] == False  # Already processed
    
    # Stats should only be updated once
    stats = learner_service.get_stats(outcome.actor_id, outcome.service)
    assert stats.resolves_count == 1  # Not 2

def test_time_windowed_calculations():
    """Only count resolves/transfers in last 90 days."""
    # Create old outcome (100 days ago)
    old_outcome = create_outcome(
        type="resolved",
        timestamp=(datetime.now() - timedelta(days=100)).isoformat()
    )
    
    # Create recent outcome (10 days ago)
    recent_outcome = create_outcome(
        type="resolved",
        timestamp=(datetime.now() - timedelta(days=10)).isoformat()
    )
    
    learner_service.process_outcome(old_outcome)
    learner_service.process_outcome(recent_outcome)
    
    # Only recent outcome should count
    stats = learner_service.get_stats(recent_outcome.actor_id, recent_outcome.service)
    assert stats.resolves_count == 1  # Only recent one

def test_fit_score_decay():
    """Fit_score decays over time."""
    # Create outcome 60 days ago
    old_outcome = create_outcome(
        type="resolved",
        timestamp=(datetime.now() - timedelta(days=60)).isoformat()
    )
    
    learner_service.process_outcome(old_outcome)
    
    # Fit_score should be lower due to decay
    stats = learner_service.get_stats(old_outcome.actor_id, old_outcome.service)
    assert stats.fit_score < 0.6  # Decayed from 0.6 (0.5 + 0.1)

def test_jira_sync():
    """Jira sync builds capability profiles."""
    # Mock Jira Simulator response
    mock_jira_response = {
        "issues": [
            {
                "id": "jira_1",
                "key": "PROJ-123",
                "fields": {
                    "assignee": {"accountId": "557058:abc123"},
                    "project": {"key": "PROJ"},
                    "resolutiondate": "2024-01-10T14:20:00Z",
                    "status": {"name": "Done"},
                    "priority": {"name": "Critical"}
                }
            }
        ]
    }
    
    # Sync
    result = learner_service.sync_jira(project="PROJ", days_back=90)
    
    # Check stats created
    stats = learner_service.get_stats("557058:abc123", "PROJ")
    assert stats.resolves_count > 0
    assert stats.last_resolved_at is not None
```

---

## Complete Checklist

### Service Scaffolding (Hour 2-3)
- [ ] Scaffold `/services/learner/` (FastAPI + PostgreSQL + Weaviate)
- [ ] Create PostgreSQL schema: `humans`, `human_service_stats`, `human_load`, `outcomes_dedupe`, knowledge graph edges
- [ ] Create Weaviate schemas: `WorkItem`, `Human`
- [ ] Add `/healthz` endpoint
- [ ] Setup embedding generation pipeline (sentence-transformers)
- [ ] Setup PCA reduction for 3D coordinates (768D → 3D)

### Learner Service Foundation (Hour 4-6)
- [ ] Implement `GET /profiles?service=X` endpoint
- [ ] Implement `POST /outcomes` endpoint
- [ ] Implement `GET /stats?human_id=X` endpoint
- [ ] Implement `POST /sync/jira` endpoint
- [ ] Implement basic stats calculation
- [ ] Implement outcome processing (idempotent)
- [ ] Create database schema
- [ ] Write tests

### Learner Service Completion (Hour 20-24)
- [ ] Complete outcome processing logic
- [ ] Complete stats update algorithm
- [ ] Implement time-windowed calculations
- [ ] Implement fit_score decay
- [ ] Implement human embedding updates
- [ ] Implement knowledge graph edge creation
- [ ] Improve seeding script
- [ ] Test all edge cases

### Documentation
- [ ] Create `/services/learner/README.md`
- [ ] Create `/scripts/test_standalone.sh`
- [ ] Create mock data files
- [ ] Document all API endpoints
- [ ] Document outcome processing algorithm
- [ ] Document time-windowed calculations

---

## Key Principles

1. **Idempotent**: Same `event_id` = no duplicate update
2. **Time-aware**: Only count last 90 days, decay over time
3. **Asymmetric learning**: Transfers are worse than resolves (penalty is larger)
4. **Knowledge graph**: All relationships timestamped for temporal queries
5. **Vector embeddings**: Human capabilities represented as embeddings for similarity

---

## Dependencies

- **Jira Simulator** (Person 1): `GET /rest/api/3/search` (for reading closed tickets)
- **PostgreSQL**: Capability stats storage, knowledge graph
- **Weaviate**: Human capability embeddings
- **LLM API**: OpenAI or Anthropic (for entity extraction from ticket descriptions)

---

## Environment Variables

```bash
# Learner Service
LEARNER_SERVICE_PORT=8003
JIRA_SIMULATOR_URL=http://localhost:8080
POSTGRES_URL=postgresql://goliath:goliath@postgres:5432/goliath
WEAVIATE_URL=http://weaviate:8080
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
```

---

## Success Criteria

- ✅ `GET /profiles` returns humans with fit_score, resolves, transfers, pages_7d, active_items
- ✅ `POST /outcomes` updates stats idempotently (same event_id = no duplicate update)
- ✅ Stats are time-windowed (only count recent activity)
- ✅ `POST /sync/jira` can sync closed tickets and update capability profiles
- ✅ Fit_score increases on resolve (+0.1), decreases on transfer (-0.15)
- ✅ Knowledge graph edges created (RESOLVED, TRANSFERRED)
- ✅ Human embeddings updated in Weaviate

---

## Why This Matters

**The Learning Loop is THE Core Differentiator:**
- Without it: Goliath is just a routing system
- With it: Goliath is an intelligent system that gets better over time
- **This is THE moat**: System gets smarter with every assignment/completion

**The Learning Loop Must Be Visible:**
- When Jira issue is completed → fit_score must increase (visible in UI stats)
- When reassigned → fit_score must decrease (visible in UI stats)
- Next decision must use updated fit_score (different assignee or confidence)
- **This is THE core differentiator - if this doesn't work, demo fails**

Good luck. Build the memory.

