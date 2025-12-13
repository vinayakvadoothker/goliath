# Person 1: Decision Engine + Infrastructure + Jira Simulator

## Your Role

You are the **Lead** and own three critical components:

1. **Decision Engine** - The core brain that routes incidents to the right people
2. **Infrastructure** - Docker, contracts, setup scripts, main README
3. **Jira Simulator** - Full Jira API mock that all other services depend on

**Why you?** As lead, you own the single source of truth (contracts), the most complex service (Decision Engine), and the infrastructure that everyone depends on (Jira Simulator).

---

## What You're Building

### 1. Decision Engine (`/services/decision/`)

**The Core Brain** - This is where the magic happens. Takes a WorkItem, returns a Decision with:
- Primary assignee (who should handle it)
- Backup assignees (fallbacks)
- Confidence score (0-1)
- Evidence (why this person was chosen)
- Constraints checked (veto filters)

**Why it exists:**
- **The routing logic**: All incident routing flows through here
- **Deterministic**: Same inputs → same decision (except time-varying load)
- **Auditable**: Every step logged (candidates, constraints, scores)
- **Production-ready**: Uses vector similarity, knowledge graphs, LLM for flexibility

### 2. Infrastructure

**Everything that makes the project work:**
- Docker Compose setup (all services)
- Contracts (TypeScript types, OpenAPI spec)
- Setup scripts (one-command setup)
- Main README (quick start, architecture)
- Environment variables template

**Why it exists:**
- **Standardization**: Everyone works in the same environment
- **Contracts**: Single source of truth for data shapes
- **Onboarding**: New developers can start immediately

### 3. Jira Simulator (`/services/jira-simulator/`)

**Full Jira REST API v3 Mock** - Exact endpoint compatibility with real Jira:
- `GET /rest/api/3/search` - JQL search (for Learner to read closed tickets)
- `POST /rest/api/3/issue` - Create issue (for Executor to create issues)
- `GET /rest/api/3/issue/:key` - Get issue details
- `PUT /rest/api/3/issue/:key` - Update issue
- `GET /rest/api/3/user/search` - Search users
- `GET /rest/api/3/project` - List projects

**Why it exists:**
- **No cloud dependencies**: Everything runs locally
- **Realistic data**: 200 people, 5000+ closed tickets, 1000+ open tickets
- **Exact API compatibility**: Same endpoints as real Jira, so code works in production
- **Independent testing**: Each developer can test without real Jira

---

## Why You're Doing This

### Decision Engine
- **Most complex service**: Requires candidate generation, constraint filtering, scoring, vector similarity, knowledge graph updates
- **Core differentiator**: This is what makes Goliath intelligent
- **Trust critical**: Must be deterministic, auditable, explainable

### Infrastructure
- **Lead responsibility**: You own the foundation everyone builds on
- **Contracts are sacred**: Single source of truth prevents breaking changes
- **Developer experience**: Good infrastructure = productive team

### Jira Simulator
- **Infrastructure dependency**: All services need Jira for learning/execution
- **Realistic testing**: 200 people, 5000+ tickets = production-like data
- **No external dependencies**: Everything runs locally

---

## Complete Work Breakdown

### Hour 0-1: Infrastructure Foundation

**What to create:**
- `/infra/docker-compose.yml` - All services, PostgreSQL, Weaviate
- `/contracts/types.ts` - Core TypeScript types
- `.env.example` - Environment variables template
- PostgreSQL schema setup (knowledge graph tables)
- Weaviate schema setup (vector database)

**Deliverables:**
- ✅ `/infra/docker-compose.yml`
- ✅ `/contracts/types.ts`
- ✅ `.env.example`
- ✅ PostgreSQL + Weaviate setup

### Hour 2-3: Service Scaffolding

**What to create:**
- `/services/decision/` - FastAPI service scaffold
- `/services/jira-simulator/` - FastAPI service scaffold
- `/healthz` endpoints
- Request logging middleware
- Correlation ID middleware
- LLM client utilities (OpenAI/Anthropic wrapper)
- Embedding utilities (sentence-transformers, PCA reduction)
- Weaviate client setup
- PostgreSQL connection pool

**Deliverables:**
- ✅ Both services scaffolded
- ✅ All utilities set up
- ✅ Database connections working

### Hour 3-4: Contract Finalization

**What to create:**
- Finalize `/contracts/types.ts` based on team feedback
- Create `/contracts/openapi.yaml` (optional)
- Document service endpoints in `/contracts/README.md`
- Create `/contracts/llm_prompts.md` - document all LLM prompts
- Setup LLM client with error handling and retries

**Deliverables:**
- ✅ Contracts locked (no changes without approval)
- ✅ LLM prompt patterns documented
- ✅ All endpoints documented

### Hour 6-8: Decision Service Core

**What to build:**
- `POST /decide` - Core decision endpoint
- `GET /decisions/:work_item_id` - Get decision
- `GET /audit/:work_item_id` - Full audit trace
- Candidate generation logic
- Constraint filtering (veto-only)
- Scoring algorithm (with severity/impact matching)
- Confidence calculation
- Vector similarity search (Weaviate)
- Knowledge graph updates (PostgreSQL)

**Deliverables:**
- ✅ All endpoints working
- ✅ Decision algorithm complete
- ✅ Audit trail complete

### Hour 18-22: Jira Simulator Completion

**What to build:**
- All Jira REST API v3 endpoints
- JQL parser (complex!)
- Database schema (projects, users, issues, history)
- Seeding script (`/scripts/seed_jira_data.py`)
  - 200 people
  - 5000+ closed tickets (last 90 days)
  - 1000+ open tickets (current capacity)
  - Realistic story points, priorities, severities

**Deliverables:**
- ✅ All endpoints implemented
- ✅ JQL parser working
- ✅ Seeding script complete
- ✅ Database schema complete

### Hour 28-32: Decision Service Testing

**What to test:**
- Determinism: same inputs → same outputs
- Constraint edge cases (zero candidates, all filtered)
- Fallback paths (learner down, GitHub down)
- Score edge cases (all same score, very different scores)

**Deliverables:**
- ✅ All test cases passing
- ✅ Edge cases handled

### Hour 48-50: Service Integration Setup

**What to do:**
- Update docker-compose.yml with all service URLs
- Test all services start correctly
- Verify health checks

**Deliverables:**
- ✅ All services integrated
- ✅ Health checks working

---

## Database Schemas

### Decision Service (PostgreSQL)

```sql
-- Decisions table
CREATE TABLE decisions (
  id TEXT PRIMARY KEY,
  work_item_id TEXT UNIQUE NOT NULL,
  primary_human_id TEXT NOT NULL,
  backup_human_ids TEXT, -- JSON array
  confidence REAL NOT NULL,
  created_at TEXT NOT NULL
);

-- Decision candidates (for audit)
CREATE TABLE decision_candidates (
  decision_id TEXT NOT NULL,
  human_id TEXT NOT NULL,
  score REAL NOT NULL,
  rank INTEGER NOT NULL,
  filtered BOOLEAN DEFAULT FALSE,
  filter_reason TEXT,
  score_breakdown TEXT, -- JSON: {fit_score: 0.8, recency: 0.6, severity_match: 0.9, capacity: 0.7}
  PRIMARY KEY (decision_id, human_id),
  FOREIGN KEY (decision_id) REFERENCES decisions(id)
);

-- Constraint results
CREATE TABLE constraint_results (
  decision_id TEXT NOT NULL,
  constraint_name TEXT NOT NULL,
  passed BOOLEAN NOT NULL,
  reason TEXT,
  PRIMARY KEY (decision_id, constraint_name),
  FOREIGN KEY (decision_id) REFERENCES decisions(id)
);
```

### Jira Simulator (PostgreSQL)

```sql
-- Jira projects
CREATE TABLE jira_projects (
  key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  project_type_key TEXT DEFAULT 'software'
);

-- Jira users (200 people)
CREATE TABLE jira_users (
  account_id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  email_address TEXT,
  active BOOLEAN DEFAULT TRUE,
  max_story_points INTEGER DEFAULT 21, -- Capacity limit
  current_story_points INTEGER DEFAULT 0, -- Currently assigned
  role TEXT -- e.g., "backend-engineer", "sre"
);

-- Jira issues
CREATE TABLE jira_issues (
  id TEXT PRIMARY KEY,
  key TEXT UNIQUE NOT NULL, -- e.g., "PROJ-123"
  project_key TEXT NOT NULL,
  summary TEXT NOT NULL,
  description TEXT,
  issuetype_name TEXT NOT NULL, -- "Bug", "Task", "Story"
  priority_name TEXT NOT NULL, -- "Critical", "High", "Medium", "Low"
  status_name TEXT NOT NULL, -- "To Do", "In Progress", "Done", "Closed"
  assignee_account_id TEXT,
  reporter_account_id TEXT,
  story_points INTEGER, -- NULL for bugs, 1-21 for stories/tasks
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  resolved_at TIMESTAMP,
  FOREIGN KEY (project_key) REFERENCES jira_projects(key),
  FOREIGN KEY (assignee_account_id) REFERENCES jira_users(account_id)
);

-- Jira issue history (for audit)
CREATE TABLE jira_issue_history (
  id SERIAL PRIMARY KEY,
  issue_key TEXT NOT NULL,
  field TEXT NOT NULL, -- "status", "assignee", "priority"
  from_value TEXT,
  to_value TEXT,
  changed_at TIMESTAMP NOT NULL,
  changed_by_account_id TEXT,
  FOREIGN KEY (issue_key) REFERENCES jira_issues(key)
);
```

### Weaviate Schema

```json
{
  "class": "WorkItem",
  "vectorizer": "none",
  "properties": [
    {"name": "id", "dataType": ["string"]},
    {"name": "description", "dataType": ["text"]},
    {"name": "service", "dataType": ["string"]},
    {"name": "severity", "dataType": ["string"]},
    {"name": "resolver_id", "dataType": ["string"]},
    {"name": "resolved_at", "dataType": ["date"]}
  ]
}
```

---

## API Endpoints

### Decision Service

#### `POST /decide`

**Purpose**: Core decision engine. Takes WorkItem, returns Decision.

**Request Body:**
```typescript
{
  work_item_id: string;
}
```

**Response (200 OK):**
```typescript
{
  decision_id: string;
  work_item_id: string;
  primary_human_id: string;
  backup_human_ids: string[];
  confidence: number; // 0.0-1.0
  constraints_checked: Array<{
    name: string;
    passed: boolean;
    reason?: string;
  }>;
  evidence: Array<{
    type: string;
    text: string;
    time_window: string;
    source: string;
  }>;
  created_at: string;
}
```

**Processing Flow:**
1. Retrieve WorkItem from Ingest (PostgreSQL)
2. Generate embedding for work item description (if not cached)
3. Vector similarity search in Weaviate for similar incidents
4. Call Learner `GET /profiles?service=X` for candidates
5. LLM extracts entities from description (for evidence)
6. Apply constraint filtering (veto-only)
7. Score remaining candidates (fit_score + severity_match + capacity + similar_incident_score)
8. Call Explain service for evidence
9. Create Decision node in knowledge graph (PostgreSQL)
10. Return Decision with audit trail

**Error Responses:**
- `400 Bad Request`: Invalid work_item_id
- `404 Not Found`: Work item doesn't exist
- `500 Internal Server Error`: Decision engine failure

**Latency Requirement**: <2 seconds

#### `GET /decisions/:work_item_id`

**Purpose**: Get decision for a work item.

**Response (200 OK):**
```typescript
{
  decision_id: string;
  work_item_id: string;
  primary_human_id: string;
  backup_human_ids: string[];
  confidence: number;
  constraints_checked: Array<{
    name: string;
    passed: boolean;
    reason?: string;
  }>;
  evidence: Array<{
    type: string;
    text: string;
    time_window: string;
    source: string;
  }>;
  created_at: string;
}
```

#### `GET /audit/:work_item_id`

**Purpose**: Get full audit trace for a decision.

**Response (200 OK):**
```typescript
{
  decision_id: string;
  work_item_id: string;
  inputs_snapshot: {
    work_item: WorkItem;
    timestamp: string;
  };
  candidate_set: Array<{
    human_id: string;
    score: number;
    rank: number;
    filtered: boolean;
    filter_reason?: string;
    score_breakdown: {
      fit_score: number;
      recency_score: number;
      availability_score: number;
      severity_match_score: number;
      capacity_score: number;
      risk_penalty: number;
    };
  }>;
  constraint_results: Array<{
    name: string;
    passed: boolean;
    reason?: string;
  }>;
  final_selection: {
    primary_human_id: string;
    backup_human_ids: string[];
    confidence: number;
  };
  correlation_id: string;
  created_at: string;
}
```

### Jira Simulator

#### `GET /rest/api/3/search?jql=...`

**Purpose**: JQL search endpoint - used by Learner to read closed tickets.

**Query Parameters:**
- `jql`: string (required) - JQL query, e.g., `project=PROJ AND status=Done AND resolved >= -90d`
- `startAt`: number (default: 0)
- `maxResults`: number (default: 50)

**Response (200 OK):**
```typescript
{
  expand: string;
  startAt: number;
  maxResults: number;
  total: number;
  issues: Array<{
    id: string;
    key: string; // e.g., "PROJ-123"
    fields: {
      summary: string;
      description?: string;
      assignee?: {
        accountId: string;
        displayName: string;
      };
      reporter: {
        accountId: string;
        displayName: string;
      };
      project: {
        key: string;
        name: string;
      };
      issuetype: {
        name: string; // "Bug", "Task", "Story"
      };
      priority: {
        name: string; // "Critical", "High", "Medium", "Low"
      };
      status: {
        name: string; // "To Do", "In Progress", "Done", "Closed"
      };
      resolutiondate?: string; // ISO 8601
      created: string; // ISO 8601
      updated: string; // ISO 8601
    };
  }>;
}
```

**JQL Parser Requirements:**
- Support: `project=PROJ`, `status=Done`, `resolved >= -90d`, `AND`, `OR`
- Parse and convert to SQL queries
- Return results in Jira format

#### `POST /rest/api/3/issue`

**Purpose**: Create issue - used by Executor to create issues with assignees.

**Request Body:**
```typescript
{
  fields: {
    project: {
      key: string; // e.g., "PROJ"
    };
    summary: string;
    description?: string;
    issuetype: {
      name: string; // "Bug", "Task", "Story"
    };
    priority: {
      name: string; // "Critical", "High", "Medium", "Low"
    };
    assignee?: {
      accountId: string;
    };
  };
}
```

**Response (201 Created):**
```typescript
{
  id: string;
  key: string; // e.g., "PROJ-123"
  self: string; // URL
}
```

#### `GET /rest/api/3/issue/:key`

**Purpose**: Get issue details.

**Response (200 OK):**
```typescript
{
  id: string;
  key: string;
  fields: {
    summary: string;
    description?: string;
    assignee?: {
      accountId: string;
      displayName: string;
    };
    status: {
      name: string;
    };
    // ... other fields
  };
}
```

#### `PUT /rest/api/3/issue/:key`

**Purpose**: Update issue (assignee, status, etc.).

**Request Body:**
```typescript
{
  fields: {
    assignee?: {
      accountId: string;
    };
    status?: {
      name: string;
    };
    // ... other fields
  };
}
```

**Response (204 No Content)**

---

## Decision Algorithm

### 1. Candidate Generation

```python
def generate_candidates(work_item: WorkItem) -> List[Human]:
    # Call Learner service
    profiles = await learner_client.get_profiles(service=work_item.service)
    
    # Optionally: Check GitHub for recent committers (cached, optional)
    # This is optional - don't block if GitHub is down
    
    # Return 3-10 candidates
    return profiles.humans[:10]
```

### 2. Constraint Filtering (Veto-Only)

```python
def apply_constraints(candidates: List[Human], work_item: WorkItem) -> List[Human]:
    filtered = []
    
    for candidate in candidates:
        # On-call required for sev1/sev2 (unless none exist)
        if work_item.severity in ['sev1', 'sev2']:
            if not candidate.on_call:
                # Check if ANY candidate is on-call
                if any(c.on_call for c in candidates):
                    filtered.append({
                        'candidate': candidate,
                        'reason': 'On-call required for sev1/sev2'
                    })
                    continue
        
        # Interruption threshold: if pages_7d > 10, filter out (unless sev1)
        if work_item.severity != 'sev1' and candidate.pages_7d > 10:
            filtered.append({
                'candidate': candidate,
                'reason': f'Interruption threshold exceeded (pages_7d={candidate.pages_7d})'
            })
            continue
        
        # Exclude creator if present
        if work_item.creator_id == candidate.id:
            filtered.append({
                'candidate': candidate,
                'reason': 'Excluded: incident creator'
            })
            continue
    
    return [c for c in candidates if c not in [f['candidate'] for f in filtered]], filtered
```

### 3. Scoring (with Severity/Impact Matching)

```python
def score_candidate(candidate: Human, work_item: WorkItem) -> float:
    fit_score = candidate.fit_score  # from learner
    recency_score = calculate_recency(candidate.last_resolved_at)
    availability_score = 1.0 if candidate.on_call else (0.8 if candidate.pages_7d < 5 else 0.5)
    
    # Severity/Impact matching (NEW)
    severity_match_score = calculate_severity_match(candidate, work_item)
    # High-severity work items should go to people who've handled high-severity before
    
    # Capacity check (story points)
    capacity_score = calculate_capacity_score(candidate, work_item)
    # If candidate is at capacity, penalize (unless sev1)
    
    risk_penalty = 0.0 if work_item.severity == 'sev1' else 0.2
    
    score = (
        fit_score * 0.35 +              # Capability (reduced from 0.4)
        recency_score * 0.25 +          # Recency (reduced from 0.3)
        availability_score * 0.15 +     # Availability (reduced from 0.2)
        severity_match_score * 0.15 +   # NEW: Severity/impact matching
        capacity_score * 0.10 -         # NEW: Capacity (story points)
        risk_penalty * 0.05              # Risk (reduced from 0.1)
    )
    return max(0.0, min(1.0, score))

def calculate_severity_match(candidate: Human, work_item: WorkItem) -> float:
    """Match candidate's historical severity handling to work item severity."""
    # Get candidate's resolved work items by severity from Jira
    resolved_by_severity = get_resolved_by_severity(candidate.id, work_item.service)
    
    # If work item is sev1, prefer candidates who've resolved sev1 before
    if work_item.severity == 'sev1':
        sev1_count = resolved_by_severity.get('sev1', 0)
        if sev1_count > 0:
            return 1.0  # Perfect match
        elif resolved_by_severity.get('sev2', 0) > 0:
            return 0.7  # Close match
        else:
            return 0.4  # No high-severity experience
    
    # If work item is sev2, prefer sev2 or sev1 experience
    elif work_item.severity == 'sev2':
        sev2_count = resolved_by_severity.get('sev2', 0)
        sev1_count = resolved_by_severity.get('sev1', 0)
        if sev2_count > 0 or sev1_count > 0:
            return 1.0
        else:
            return 0.6
    
    # sev3/sev4: less critical, capacity matters more
    else:
        return 0.8  # Default good score

def calculate_capacity_score(candidate: Human, work_item: WorkItem) -> float:
    """Check if candidate has capacity (story points)."""
    # Get current story points assigned from Jira
    current_story_points = get_current_story_points(candidate.id)
    max_capacity = candidate.max_story_points  # e.g., 21 (3-week sprint)
    work_item_story_points = work_item.story_points or 3  # Default 3
    
    # If adding this work item would exceed capacity
    if current_story_points + work_item_story_points > max_capacity:
        if work_item.severity == 'sev1':
            return 0.0  # sev1 can exceed capacity
        else:
            return -0.3  # Penalty for exceeding capacity
    
    # Capacity utilization
    utilization = current_story_points / max_capacity
    if utilization < 0.5:
        return 1.0  # Plenty of capacity
    elif utilization < 0.8:
        return 0.7  # Some capacity
    else:
        return 0.3  # Near capacity
```

### 4. Confidence Calculation

```python
def calculate_confidence(top1_score: float, top2_score: float) -> float:
    """
    Confidence = 1.0 - (top2_score - top1_score) / top1_score
    
    If top1 and top2 are close → low confidence
    If top1 is clearly best → high confidence
    """
    if top1_score == 0:
        return 0.0
    
    margin = (top2_score - top1_score) / top1_score
    confidence = 1.0 - margin
    return max(0.0, min(1.0, confidence))
```

### 5. Vector Similarity Search

```python
def find_similar_incidents(work_item: WorkItem) -> List[dict]:
    """Use Weaviate to find similar incidents via vector similarity."""
    # Generate embedding for work item description
    embedding = generate_embedding(work_item.description)  # 768D
    
    # Search Weaviate for similar work items
    similar = weaviate_client.query.get(
        "WorkItem",
        ["id", "description", "service", "severity", "resolver_id", "resolved_at"]
    ).with_near_vector({
        "vector": embedding
    }).with_limit(5).do()
    
    return similar['data']['Get']['WorkItem']
```

---

## How to Test

### Standalone Testing (Without Other Services)

**1. Create test script: `/services/decision/scripts/test_standalone.sh`**

```bash
#!/bin/bash
# Test Decision service standalone

# Start PostgreSQL and Weaviate
docker-compose -f docker-compose.test.yml up -d postgres weaviate

# Wait for services to be ready
sleep 5

# Run tests
pytest tests/test_decision_standalone.py

# Cleanup
docker-compose -f docker-compose.test.yml down
```

**2. Create mock data: `/services/decision/scripts/mock_data.json`**

```json
{
  "work_items": [
    {
      "id": "wi_test_1",
      "service": "api-service",
      "severity": "sev1",
      "description": "High error rate detected on /api/v1/users endpoint",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "candidates": [
    {
      "human_id": "human_1",
      "display_name": "Alice Engineer",
      "fit_score": 0.85,
      "resolves_count": 12,
      "transfers_count": 1,
      "last_resolved_at": "2024-01-10T14:20:00Z",
      "on_call": true,
      "pages_7d": 2,
      "active_items": 3,
      "max_story_points": 21,
      "current_story_points": 8,
      "resolved_by_severity": {
        "sev1": 3,
        "sev2": 5,
        "sev3": 4
      }
    }
  ]
}
```

**3. Test cases:**

```python
# tests/test_decision_standalone.py

def test_decision_deterministic():
    """Same inputs → same decision."""
    work_item = load_mock_work_item("wi_test_1")
    
    decision1 = decision_service.decide(work_item.id)
    decision2 = decision_service.decide(work_item.id)
    
    assert decision1.primary_human_id == decision2.primary_human_id
    assert decision1.confidence == decision2.confidence

def test_constraint_filtering():
    """Constraints filter correctly."""
    work_item = create_work_item(severity="sev1")
    candidates = load_mock_candidates()
    
    # All candidates should be on-call for sev1
    filtered, passed = decision_service.apply_constraints(candidates, work_item)
    
    assert all(c.on_call for c in passed)
    assert len(filtered) > 0  # Some should be filtered

def test_severity_matching():
    """High-severity work prefers high-severity experience."""
    work_item = create_work_item(severity="sev1")
    candidates = [
        create_candidate(sev1_resolves=5),  # Has sev1 experience
        create_candidate(sev1_resolves=0),  # No sev1 experience
    ]
    
    scores = [decision_service.score_candidate(c, work_item) for c in candidates]
    
    assert scores[0] > scores[1]  # First candidate should score higher

def test_capacity_matching():
    """Candidates at capacity are penalized (unless sev1)."""
    work_item = create_work_item(severity="sev2", story_points=5)
    candidates = [
        create_candidate(current_story_points=5, max_story_points=21),  # Low capacity
        create_candidate(current_story_points=20, max_story_points=21),  # Near capacity
    ]
    
    scores = [decision_service.score_candidate(c, work_item) for c in candidates]
    
    assert scores[0] > scores[1]  # First candidate should score higher

def test_confidence_calculation():
    """Confidence reflects top1-top2 margin."""
    candidates = [
        create_candidate(score=0.9),  # Top1
        create_candidate(score=0.5),  # Top2 (big gap)
    ]
    
    confidence = decision_service.calculate_confidence(candidates[0].score, candidates[1].score)
    
    assert confidence > 0.7  # High confidence due to big gap
```

### Jira Simulator Testing

**1. Test JQL parser:**

```python
def test_jql_parser():
    """JQL queries parse correctly."""
    jql = "project=PROJ AND status=Done AND resolved >= -90d"
    
    parsed = jira_simulator.parse_jql(jql)
    
    assert parsed['project'] == 'PROJ'
    assert parsed['status'] == 'Done'
    assert parsed['resolved'] >= -90  # days

def test_jira_search():
    """JQL search returns correct results."""
    # Seed test data
    seed_test_data()
    
    # Search for closed tickets
    response = jira_simulator.search(jql="project=PROJ AND status=Done")
    
    assert response['total'] > 0
    assert all(issue['fields']['status']['name'] == 'Done' for issue in response['issues'])

def test_jira_create_issue():
    """Creating issue works correctly."""
    issue_data = {
        "fields": {
            "project": {"key": "PROJ"},
            "summary": "Test issue",
            "issuetype": {"name": "Bug"},
            "priority": {"name": "Critical"},
            "assignee": {"accountId": "557058:abc123"}
        }
    }
    
    response = jira_simulator.create_issue(issue_data)
    
    assert response['key'].startswith('PROJ-')
    assert response['id'] is not None
```

**2. Test seeding script:**

```python
def test_seeding_script():
    """Seeding script creates realistic data."""
    data = seed_jira_data()
    
    assert len(data['users']) == 200
    assert len(data['closed_issues']) == 5000
    assert len(data['open_issues']) == 1000
    
    # Check story points distribution
    story_points = [u['current_story_points'] for u in data['users']]
    assert all(0 <= sp <= u['max_story_points'] for u, sp in zip(data['users'], story_points))
```

---

## Complete Checklist

### Infrastructure (Hour 0-1)
- [ ] Create `/infra/docker-compose.yml` with all services
- [ ] Create `/contracts/types.ts` with core types
- [ ] Create `.env.example` with all variables
- [ ] Setup PostgreSQL database
- [ ] Setup Weaviate instance
- [ ] Create schemas for both databases

### Service Scaffolding (Hour 2-3)
- [ ] Scaffold `/services/decision/` (FastAPI)
- [ ] Scaffold `/services/jira-simulator/` (FastAPI)
- [ ] Add `/healthz` endpoints to both
- [ ] Add request logging middleware
- [ ] Add correlation ID middleware
- [ ] Setup LLM client utilities
- [ ] Setup embedding utilities (sentence-transformers, PCA)
- [ ] Setup Weaviate client
- [ ] Setup PostgreSQL connection pool

### Contract Finalization (Hour 3-4)
- [ ] Finalize `/contracts/types.ts` based on feedback
- [ ] Create `/contracts/openapi.yaml` (optional)
- [ ] Document endpoints in `/contracts/README.md`
- [ ] Create `/contracts/llm_prompts.md`
- [ ] Lock contracts (no changes without approval)

### Decision Service Core (Hour 6-8)
- [ ] Implement `POST /decide` endpoint
- [ ] Implement `GET /decisions/:work_item_id` endpoint
- [ ] Implement `GET /audit/:work_item_id` endpoint
- [ ] Implement candidate generation
- [ ] Implement constraint filtering
- [ ] Implement scoring algorithm (with severity/capacity matching)
- [ ] Implement confidence calculation
- [ ] Implement vector similarity search
- [ ] Implement knowledge graph updates
- [ ] Create database schema
- [ ] Write tests

### Jira Simulator (Hour 18-22)
- [ ] Implement `GET /rest/api/3/search` (with JQL parser)
- [ ] Implement `POST /rest/api/3/issue`
- [ ] Implement `GET /rest/api/3/issue/:key`
- [ ] Implement `PUT /rest/api/3/issue/:key`
- [ ] Implement `GET /rest/api/3/user/search`
- [ ] Implement `GET /rest/api/3/project`
- [ ] Create database schema
- [ ] Create seeding script (`/scripts/seed_jira_data.py`)
- [ ] Test JQL parser
- [ ] Test all endpoints
- [ ] Verify exact Jira API compatibility

### Testing (Hour 28-32)
- [ ] Test determinism (same inputs → same outputs)
- [ ] Test constraint edge cases
- [ ] Test fallback paths
- [ ] Test score edge cases
- [ ] Test Jira Simulator JQL parser
- [ ] Test seeding script

### Integration (Hour 48-50)
- [ ] Update docker-compose.yml with all service URLs
- [ ] Test all services start correctly
- [ ] Verify health checks
- [ ] Test service-to-service calls

### Documentation
- [ ] Create `/services/decision/README.md`
- [ ] Create `/services/jira-simulator/README.md`
- [ ] Create `/scripts/test_standalone.sh` for Decision
- [ ] Create `/scripts/test_standalone.sh` for Jira Simulator
- [ ] Create mock data files
- [ ] Document all API endpoints
- [ ] Document decision algorithm
- [ ] Document JQL parser

---

## Key Principles

1. **Deterministic**: Same inputs → same decision (except time-varying load)
2. **Auditable**: Every step logged (candidates, constraints, scores)
3. **Explainable**: Evidence must be clear and contextual
4. **Production-ready**: Uses vector similarity, knowledge graphs, LLM for flexibility
5. **No hardcoding**: LLM handles variations, vector search handles similarity

---

## Dependencies

### Decision Service
- **Learner Service**: `GET /profiles?service=X` (for candidates)
- **Explain Service**: `POST /explainDecision` (for evidence)
- **Ingest Service**: `GET /work-items/:id` (for work item details)
- **PostgreSQL**: Knowledge graph storage
- **Weaviate**: Vector similarity search
- **LLM API**: OpenAI or Anthropic (for entity extraction, evidence generation)

### Jira Simulator
- **PostgreSQL**: Issue storage
- **No external dependencies**: Everything runs locally

---

## Environment Variables

```bash
# Decision Service
DECISION_SERVICE_PORT=8002
LEARNER_SERVICE_URL=http://localhost:8003
EXPLAIN_SERVICE_URL=http://localhost:8005
INGEST_SERVICE_URL=http://localhost:8001
POSTGRES_URL=postgresql://goliath:goliath@postgres:5432/goliath
WEAVIATE_URL=http://weaviate:8080
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2

# Jira Simulator
JIRA_SIMULATOR_PORT=8080
POSTGRES_URL=postgresql://goliath:goliath@postgres:5432/goliath
```

---

## Success Criteria

- ✅ Decision appears <2 seconds after work item created
- ✅ Decision is deterministic (same inputs → same outputs)
- ✅ All candidates logged with scores and filter reasons
- ✅ Audit endpoint returns full reasoning chain
- ✅ Jira Simulator has exact API compatibility with real Jira
- ✅ JQL parser handles all required queries
- ✅ Seeding script creates realistic data (200 people, 5000+ tickets)

---

## Why This Matters

**Decision Engine:**
- **The core differentiator**: This is what makes Goliath intelligent
- **Trust critical**: Must be deterministic, auditable, explainable
- **Production-ready**: Uses vector similarity, knowledge graphs, LLM

**Infrastructure:**
- **Foundation**: Everyone builds on your work
- **Developer experience**: Good infrastructure = productive team
- **Contracts**: Single source of truth prevents breaking changes

**Jira Simulator:**
- **No external dependencies**: Everything runs locally
- **Realistic testing**: Production-like data for all services
- **Exact compatibility**: Code works with real Jira in production

Good luck. Build the brain.

