# Goliath MVP Plan: 72-Hour Hackathon

## Mission
Build a decision-grade incident routing system that demonstrates: **evidence-backed assignment → bounded execution → outcome learning → audit replay**.

**Core MVP Feature: Learning Loop**
- When tasks get assigned/completed → system learns and gets better
- Jira issue assigned/completed → Learner updates capability profiles (fit_score, resolves, transfers)
- Future decisions use updated profiles → better routing over time
- **This is THE differentiator and MUST work in MVP**

## Core Principle
**Zero overlapping work until Hour 48.** Each person builds in isolation with clear contracts. Integration happens in final 24 hours.

---

## Jira Integration Overview

**Jira is used for capability learning and execution (not required for incident ingestion, but it can be in the case of an unassigned ticket right):**

1. **READ (Learner Service)**: 
   - Reads **closed Jira tickets** to determine capability and recency
   - Queries: `GET /rest/api/3/search?jql=project=PROJ AND status=Done AND resolved >= -90d`
   - Extracts: assignee, project (service), resolution date, issue type
   - Builds capability profiles: who worked on what, when, outcomes
   - **Purpose**: Learn from past work (closed tickets = ground truth)

2. **WRITE (Executor Service)**:
   - Creates **Jira issues** with assigned assignees
   - API: `POST /rest/api/3/issue` with assignee field
   - Links back to WorkItem via `jira_issue_key`
   - **Purpose**: Execute decision by creating ticket with assignee

**Why Jira for learning + execution?**
- Enterprise-friendly (most orgs have Jira)
- Good API (REST v3, well-documented)
- Closed tickets = ground truth for capability
- Creating issues = actual execution (not just suggestions)

**Note**: Work items can come from anywhere (demo endpoint, manual creation, other systems). Jira webhook is optional - if configured, we can ingest unassigned Jira issues, but it's not required.

---

, b## Team Structure

**Person 1 (Lead)**: Decision Engine + Infrastructure (Docker, Contracts, Setup) + **Jira Simulator** (Full Jira API Mock)  
**Person 2**: Learner (Capability Profiles + Outcome Learning)  
**Person 3**: Ingest + Monitoring Service  
**Person 4**: Executor (Bounded Actions) + Explain (Evidence Compiler)  
**Person 5**: UI (Evidence-First Interface)

---

## Ownership & Deliverables

**Who creates what - complete breakdown:**

**Updated Team Structure:**
- **Person 1 (Lead)**: Decision Engine + Infrastructure + Jira Simulator
- **Person 2**: Learner (Capability Profiles + Outcome Learning)
- **Person 3**: Ingest + Monitoring Service
- **Person 4**: Executor + Explain
- **Person 5**: UI (Evidence-First Interface)

### Person 1 (Lead) - Infrastructure & Core Services

**Creates:**
- `/infra/docker-compose.yml` - Docker Compose configuration for all services
- `/scripts/setup.sh` - One-command setup script for developers
- `/README.md` - Main project README with:
  - Quick start guide
  - Architecture overview
  - Service ports mapping
  - Independent testing guide
  - Troubleshooting
- `/contracts/types.ts` - Core TypeScript types (shared contracts)
- `/contracts/openapi.yaml` - OpenAPI specification (optional)
- `/contracts/README.md` - API documentation
- `/contracts/llm_prompts.md` - LLM prompt patterns documentation
- `.env.example` - Environment variables template
- `/services/decision/` - **Decision service (FastAPI)** - THE CORE BRAIN
  - `/services/decision/README.md` - Service-specific README
  - `/services/decision/scripts/test_standalone.sh` - Standalone test script
  - `/services/decision/scripts/mock_data.json` - Mock data for testing
- `/services/jira-simulator/` - **Jira Simulator service (Full Jira API Mock)**
  - `/services/jira-simulator/README.md` - Service-specific README
  - `/services/jira-simulator/scripts/test_standalone.sh` - Standalone test script
  - `/services/jira-simulator/Dockerfile` - Docker configuration
- `/scripts/seed_jira_data.py` - **Jira Simulator seeding script**
  - Creates 200 people
  - Creates 5000+ closed tickets (last 90 days)
  - Creates 1000+ open tickets (current capacity)
  - Realistic story points, priorities, severities

**Why Person 1?** Lead owns infrastructure, contracts (single source of truth), the core decision engine, and the Jira Simulator (infrastructure/mocking service that all other services depend on).

---

### Person 2 - Learning & Capability Tracking

**Creates:**
- `/services/learner/` - Learner service (FastAPI + PostgreSQL + Weaviate)
  - `/services/learner/README.md` - Service-specific README
  - `/services/learner/scripts/test_standalone.sh` - Standalone test script
  - `/services/learner/scripts/mock_data.json` - Mock data for testing
- `/scripts/seed_demo_data.py` - Learner demo data seeding (if needed)

**Why Person 2?** Owns learning/capability tracking - the "memory" of the system. Focuses on outcome processing, stats updates, and capability profiles.

---

### Person 3 - Ingestion & Monitoring

**Creates:**
- `/services/ingest/` - Ingest service (FastAPI)
  - `/services/ingest/README.md` - Service-specific README
  - `/services/ingest/scripts/test_standalone.sh` - Standalone test script
  - `/services/ingest/scripts/mock_data.json` - Mock data for testing
- `/services/monitoring/` - Monitoring service (FastAPI)
  - `/services/monitoring/README.md` - Service-specific README
  - `/services/monitoring/scripts/test_standalone.sh` - Standalone test script

**Why Person 3?** Both services handle work item ingestion (one from monitoring, one from manual/demo). Natural pairing.

---

### Person 4 - Execution & Explanation

**Creates:**
- `/services/executor/` - Executor service (FastAPI)
  - `/services/executor/README.md` - Service-specific README
  - `/services/executor/scripts/test_standalone.sh` - Standalone test script
  - `/services/executor/scripts/mock_data.json` - Mock data for testing
- `/services/explain/` - Explain service (FastAPI, no DB)
  - `/services/explain/README.md` - Service-specific README
  - `/services/explain/scripts/test_standalone.sh` - Standalone test script
  - `/services/explain/scripts/mock_data.json` - Mock data for testing

**Why Person 4?** Both are simpler services (Executor just creates Jira issues, Explain just LLM calls). Together they're a reasonable workload.

---

### Person 5 - User Interface

**Creates:**
- `/apps/ui/` - Next.js UI application
  - `/apps/ui/README.md` - UI-specific README
  - `/apps/ui/package.json` - Dependencies
  - `/apps/ui/components/` - React components
  - `/apps/ui/pages/` - Next.js pages
  - `/apps/ui/lib/` - API client utilities
- Design system tokens (colors, typography, spacing)
- Knowledge graph 3D visualization component

**Why Person 5?** UI person owns all frontend code and design system.

---

### Shared/Everyone

**Each person creates for their service:**
- `Dockerfile` - Service containerization
- `requirements.txt` or `package.json` - Dependencies
- `.dockerignore` - Docker ignore patterns
- `README.md` - Service-specific documentation
- `scripts/test_standalone.sh` - How to test without other services
- `scripts/mock_data.json` - Mock data for standalone testing

**Why shared?** Each service needs its own Docker setup and testing strategy for independent development.

---

## Tech Stack

- **APIs**: Python (FastAPI) - all services
- **Frontend**: Next.js 14 (App Router), TypeScript, shadcn/ui
- **Database**: PostgreSQL (shared knowledge graph) + Weaviate (vector database)
- **Integration**: HTTP REST only (no message bus)
- **Containerization**: Docker + Docker Compose (all services containerized)
  - Each service runs in its own container
  - PostgreSQL, Weaviate, all services containerized
  - Standardized environment for all developers
  - `docker-compose up` starts everything
- **Jira Simulator**: Full Jira API mock (REST v3 compatible)
  - **Port**: 8080 (standard Jira port)
  - **Endpoints**: Exact match to Jira Cloud REST API v3
  - **READ**: Closed tickets → capability/recency data (Learner)
  - **WRITE**: Create issues with assignees (Executor)
  - **WEBHOOK (optional)**: New unassigned issues → WorkItems (Ingest)
  - **Seeded Data**: 200 people, realistic work history, story points, capacity limits
  - **No Cloud**: Everything runs locally, no external dependencies
  - **Independent Testing**: Each developer can run Jira Simulator standalone for testing
- **Monitoring Service**: Simulates monitoring/observability systems
  - Continuously logs (INFO, WARN, DEBUG)
  - Periodically logs errors (ERROR, CRITICAL) → triggers WorkItem creation
  - Simulates what ServiceNow/Datadog/PagerDuty would do
- **Design System**: Palantir + Apple aesthetic
  - Background: `#0a0a0a` (off-black)
  - Text: `#f5f5f5` (off-white)
  - Accents: `#3b82f6` (blue), `#10b981` (green), `#ef4444` (red)
  - Borders: `#1a1a1a`
  - Surfaces: `#141414`

---

## Design Philosophy

**Opinionated, not ambiguous.** Every UI element has:
- Clear purpose (what it does)
- Contextual explanation (why it exists)
- Visual hierarchy (how to read it)

**No questions left unanswered.** If a user wonders "what does this mean?", the design failed.

---

## Architecture Overview

```
┌─────────────┐
│  Monitoring │───(error detected)──▶┌─────────┐     ┌──────────┐     ┌─────────┐     ┌──────────┐
│   Service   │                      │ Ingest  │────▶│ Decision │────▶│ Explain │────▶│ Executor │
└─────────────┘                      └────┬────┘     └─────┬─────┘     └─────────┘     └──────────┘
     │                                      │                │
     │                                      │                │
     │                                      ▼                ▼
     │                                ┌─────────┐     ┌──────────┐
     │                                │ Learner │◀────│   UI     │
     │                                └────┬────┘     └─────┬────┘
     │                                     │                │
     │                                     │                │
     │                                     ▼                ▼
     │                            ┌─────────────┐   ┌──────────────┐
     │                            │ PostgreSQL  │   │  react-force │
     │                            │(Knowledge   │   │  -graph-3d   │
     │                            │   Graph)    │   │ (3D Viz)     │
     │                            └─────┬───────┘   └──────────────┘
     │                                  │
     │                                  ▼
     │                            ┌─────────────┐
     │                            │  Weaviate   │
     │                            │  (Vectors)   │
     │                            └─────────────┘
     │
     └──(continuous logging)──▶ [Logs]
```

**Why this architecture?**
- **Monitoring Service** simulates real monitoring/observability systems
  - Continuously logs (INFO, WARN, DEBUG) for a service
  - Periodically logs errors (ERROR, CRITICAL) that trigger incidents
  - When error detected → calls Ingest to create WorkItem
  - **Purpose**: Realistic simulation of what ServiceNow/Datadog/PagerDuty would do
- **Ingest** normalizes external events into WorkItems (single source of truth)
  - Accepts work items from multiple sources (monitoring service, demo endpoint, manual creation, optional Jira webhook)
  - Normalizes any source → canonical WorkItem
- **Decision** is the core: candidate gen → constraints → ranking (the "brain")
- **Learner** maintains capability profiles and learns from outcomes (the "memory")
  - Reads Jira closed tickets to determine capability/recency
  - Tracks who worked on what, when, and outcomes
- **Explain** generates evidence bullets (the "justification")
- **Executor** performs bounded actions (the "hands")
  - Creates Jira issues with assigned assignees
  - Links back to original WorkItem
- **UI** is read-only observer + override interface (the "window")

**Isolation principle**: Each service can be built/tested independently. Only contracts matter.

---

## Contract Definitions

### Shared Types (`/contracts/types.ts`)

```typescript
// Core entities
interface WorkItem {
  id: string;
  type: 'incident' | 'ticket' | 'alert';
  service: string;
  severity: 'sev1' | 'sev2' | 'sev3' | 'sev4';
  description: string;
  created_at: string;
  origin_system: string;
  creator_id?: string;
  story_points?: number;  // For capacity matching (1-21, typically)
  impact?: 'high' | 'medium' | 'low';  // Impact level (separate from severity)
}

interface Human {
  id: string;
  display_name: string;
  contact_handles: {
    slack?: string;
    email?: string;
  };
}

interface Decision {
  id: string;
  work_item_id: string;
  primary_human_id: string;
  backup_human_ids: string[];
  confidence: number; // 0-1
  constraints_checked: ConstraintResult[];
  created_at: string;
}

interface ConstraintResult {
  name: string;
  passed: boolean;
  reason?: string;
}

interface Evidence {
  type: 'recent_resolution' | 'recent_commit' | 'on_call' | 'low_load' | 'similar_incident';
  text: string;
  time_window: string;
  source: string;
}

interface Outcome {
  event_id: string;
  decision_id: string;
  type: 'resolved' | 'reassigned' | 'escalated';
  actor_id: string;
  timestamp: string;
}
```

---

## API Documentation

Complete endpoint specifications with input/output schemas, rationale, and examples.

### Ingest Service

#### `POST /ingest/demo`
**Purpose**: Creates a demo WorkItem to simulate monitoring/observability systems. Primary source for MVP testing.

**Why it exists**: Real integrations (ServiceNow, Datadog, PagerDuty) require OAuth, webhook setup, API keys - too much scope for MVP. This endpoint simulates the same data structure.

**Request Body**:
```typescript
{
  service: string;        // e.g., "api-service", "payment-service"
  severity: "sev1" | "sev2" | "sev3" | "sev4";
  description: string;    // Raw error description (will be LLM preprocessed)
  type?: "incident" | "ticket" | "alert";  // Default: "incident"
  story_points?: number;  // Optional: story points for capacity matching (1-21)
  impact?: "high" | "medium" | "low";  // Optional: impact level (separate from severity)
}
```

**Response** (201 Created):
```typescript
{
  work_item_id: string;
  created_at: string;     // ISO 8601 timestamp
  message: "WorkItem created successfully"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input (missing required fields, invalid severity)
- `500 Internal Server Error`: Database error, LLM preprocessing failure

**Example**:
```json
// Request
{
  "service": "api-service",
  "severity": "sev1",
  "description": "High error rate detected: 500 errors/sec on /api/v1/users endpoint"
}

// Response
{
  "work_item_id": "wi_abc123",
  "created_at": "2024-01-15T10:30:00Z",
  "message": "WorkItem created successfully"
}
```

**Processing Flow**:
1. LLM preprocesses `description` (clean, normalize, extract key info)
2. Creates WorkItem with cleaned description
3. Stores both `raw_log` (original) and `description` (cleaned) in DB
4. Triggers Decision service automatically

---

#### `POST /webhooks/jira`
**Purpose**: Receives Jira webhooks when issues are created/updated. Optional - only processes unassigned issues.

**Why it exists**: Allows routing unassigned Jira issues through Goliath's decision engine.

**Request Body** (Jira webhook format):
```typescript
{
  webhookEvent: string;   // e.g., "jira:issue_created", "jira:issue_updated"
  issue: {
    key: string;          // e.g., "PROJ-123"
    fields: {
      summary: string;
      description?: string;
      priority: { name: string };  // "Critical", "High", "Medium", "Low"
      project: { key: string };     // e.g., "PROJ"
      assignee?: { accountId: string };
      status: { name: string };
    };
  };
}
```

**Response** (200 OK):
```typescript
{
  processed: boolean;
  work_item_id?: string;  // Only if issue was unassigned and processed
  message: string;
}
```

**Processing Logic**:
- Only processes if `issue.fields.assignee` is null (unassigned)
- Maps Jira priority → severity (Critical=sev1, High=sev2, etc.)
- Maps Jira project → service (via `JIRA_PROJECT_TO_SERVICE_MAP` config)
- LLM preprocesses description before creating WorkItem

**Error Responses**:
- `400 Bad Request`: Invalid webhook format
- `200 OK` with `processed: false`: Issue already assigned, skipped

---

#### `POST /work-items`
**Purpose**: Manual work item creation from UI. Allows users to create incidents directly.

**Why it exists**: Users may need to create work items manually (not from monitoring systems).

**Request Body**:
```typescript
{
  service: string;
  severity: "sev1" | "sev2" | "sev3" | "sev4";
  description: string;
  type?: "incident" | "ticket" | "alert";
  creator_id?: string;    // Optional: who created it
}
```

**Response** (201 Created):
```typescript
{
  work_item_id: string;
  created_at: string;
  message: "WorkItem created successfully"
}
```

---

#### `GET /work-items`
**Purpose**: List all work items. Used by UI to display work items table.

**Why it exists**: UI needs to show all work items with filtering/sorting.

**Query Parameters**:
```typescript
{
  service?: string;       // Filter by service
  severity?: "sev1" | "sev2" | "sev3" | "sev4";  // Filter by severity
  status?: "open" | "assigned" | "resolved";     // Filter by status
  limit?: number;         // Default: 50, max: 100
  offset?: number;        // For pagination
}
```

**Response** (200 OK):
```typescript
{
  work_items: Array<{
    id: string;
    service: string;
    severity: string;
    description: string;
    created_at: string;
    origin_system: string;
    status: string;
  }>;
  total: number;
  limit: number;
  offset: number;
}
```

---

#### `GET /work-items/:id`
**Purpose**: Get single work item by ID. Used by UI detail page and Decision service.

**Why it exists**: Need to retrieve full work item details for decision-making and display.

**Path Parameters**:
- `id`: string (work_item_id)

**Response** (200 OK):
```typescript
{
  id: string;
  type: string;
  service: string;
  severity: string;
  description: string;    // Cleaned/normalized
  raw_log?: string;        // Original raw log (if available)
  created_at: string;
  origin_system: string;
  creator_id?: string;
  jira_issue_key?: string; // If linked to Jira issue
}
```

**Error Responses**:
- `404 Not Found`: Work item doesn't exist

---

#### `POST /work-items/:id/outcome`
**Purpose**: Record outcome (resolved, reassigned, escalated). Triggers learning loop.

**Why it exists**: This is THE core learning mechanism. When humans override/resolve, outcomes feed back into Learner to update capability profiles.

**Path Parameters**:
- `id`: string (work_item_id)

**Request Body**:
```typescript
{
  type: "resolved" | "reassigned" | "escalated";
  actor_id: string;        // Who performed the action
  decision_id?: string;    // If reassigned, original decision ID
  new_assignee_id?: string; // If reassigned, new assignee
  timestamp?: string;      // ISO 8601, defaults to now
  notes?: string;          // Optional notes
}
```

**Response** (200 OK):
```typescript
{
  outcome_id: string;
  processed: boolean;
  message: "Outcome recorded and forwarded to Learner"
}
```

**Processing Flow**:
1. Creates outcome record in Ingest DB
2. Forwards to Learner `POST /outcomes`
3. Learner updates fit_score, resolves_count, transfers_count
4. Next decision uses updated stats

**Error Responses**:
- `400 Bad Request`: Invalid outcome type or missing actor_id
- `404 Not Found`: Work item doesn't exist

---

### Decision Service

#### `POST /decide`
**Purpose**: Core decision engine. Takes WorkItem, returns Decision with primary assignee, backups, confidence, evidence.

**Why it exists**: This is THE brain. All routing decisions flow through here.

**Request Body**:
```typescript
{
  work_item_id: string;
}
```

**Response** (200 OK):
```typescript
{
  decision_id: string;
  work_item_id: string;
  primary_human_id: string;
  backup_human_ids: string[];
  confidence: number;     // 0.0-1.0
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

**Processing Flow**:
1. Retrieves WorkItem from Ingest (PostgreSQL)
2. Generates embedding for work item description (if not cached)
3. Vector similarity search in Weaviate for similar incidents
4. Calls Learner `GET /profiles?service=X` for candidates
5. LLM extracts entities from description (for evidence)
6. Applies constraint filtering (veto-only)
7. Scores remaining candidates (fit_score + similar_incident_score from vector search)
8. Calls Explain service for evidence
9. Creates Decision node in knowledge graph (PostgreSQL)
10. Returns Decision with audit trail

**Error Responses**:
- `400 Bad Request`: Invalid work_item_id
- `404 Not Found`: Work item doesn't exist
- `500 Internal Server Error`: Decision engine failure

**Latency Requirement**: <2 seconds

---

#### `GET /decisions/:work_item_id`
**Purpose**: Get decision for a work item. Used by UI to display decision details.

**Why it exists**: UI needs to show decision details (assignee, evidence, confidence).

**Path Parameters**:
- `work_item_id`: string

**Response** (200 OK):
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

**Error Responses**:
- `404 Not Found`: Decision doesn't exist for this work item

---

#### `GET /audit/:work_item_id`
**Purpose**: Get full audit trace for a decision. Shows complete reasoning chain.

**Why it exists**: Trust and accountability. Must be able to replay and explain every decision.

**Path Parameters**:
- `work_item_id`: string

**Response** (200 OK):
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

**Why audit exists**: 
- Replayability: Same inputs → same decision (except time-varying load)
- Accountability: Can explain why decision was made
- Trust: Full transparency in high-stakes orgs

---

### Learner Service

#### `GET /profiles?service=X`
**Purpose**: Returns humans with capability stats for a service. Used by Decision service for candidate generation.

**Why it exists**: Decision service needs capability profiles to rank candidates.

**Query Parameters**:
- `service`: string (required)

**Response** (200 OK):
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
    similar_incident_score?: number; // From LLM matching
  }>;
}
```

**Why these fields**:
- `fit_score`: Primary signal from outcomes (resolves boost, transfers penalize)
- `resolves_count`: How many they've resolved (capability indicator)
- `transfers_count`: How many they've transferred (negative signal)
- `last_resolved_at`: Recency (expertise decays)
- `on_call`: Availability signal
- `pages_7d`: Load signal (don't interrupt overloaded people)
- `active_items`: Current workload

**Error Responses**:
- `400 Bad Request`: Missing service parameter
- `500 Internal Server Error`: Database error

---

#### `POST /outcomes`
**Purpose**: Updates capability profiles based on outcomes. This is THE learning mechanism.

**Why it exists**: When tasks are assigned/completed, system learns and gets better. This is the moat.

**Request Body**:
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

**Response** (200 OK):
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

**Processing Logic**:
- **Idempotent**: Same `event_id` = no duplicate update
- **Resolved**: 
  - fit_score +0.1, resolves_count +1, last_resolved_at updated
  - Creates RESOLVED edge in knowledge graph (human → work_item, timestamped)
  - Updates human embedding in Weaviate:
    - Aggregates embeddings from all resolved work items (weighted average)
    - Recalculates 3D coordinates (PCA reduction: 768D → 3D)
    - Stores updated embedding + 3D coords in PostgreSQL
  - Graph visualization updates: new edge appears, human node position may shift
- **Reassigned**: 
  - Original assignee fit_score -0.15, transfers_count +1
  - New assignee fit_score +0.05
  - Creates TRANSFERRED edge in knowledge graph (work_item, from_human → to_human, timestamped)
- **Time-windowed**: Only counts last 90 days
- **Knowledge graph updates**: All edges timestamped for temporal queries

**Why these deltas**:
- Asymmetric: Transfers are worse than resolves (penalty is larger)
- Time-aware: Old outcomes decay (multiply by 0.99 per day)

**Error Responses**:
- `400 Bad Request`: Invalid outcome type or missing fields
- `409 Conflict`: Event already processed (idempotent)

---

#### `GET /stats?human_id=X`
**Purpose**: Returns stats for a human. Used by UI to display capability profiles.

**Why it exists**: UI needs to show human stats (for transparency and trust).

**Query Parameters**:
- `human_id`: string (required)

**Response** (200 OK):
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

**Error Responses**:
- `400 Bad Request`: Missing human_id
- `404 Not Found`: Human doesn't exist

---

#### `POST /sync/jira`
**Purpose**: Syncs closed Jira tickets to build initial capability profiles. Background job.

**Why it exists**: Need historical data to bootstrap capability profiles. Reads closed tickets to see who worked on what.

**Request Body** (optional):
```typescript
{
  project?: string;        // Specific project, or all if omitted
  days_back?: number;     // Default: 90
}
```

**Response** (200 OK):
```typescript
{
  synced: number;          // Number of tickets synced
  humans_updated: number;
  message: "Sync completed successfully"
}
```

**Processing Logic**:
1. Queries Jira: `GET /rest/api/3/search?jql=project=PROJ AND status=Done AND resolved >= -90d`
2. For each closed ticket:
   - Extracts assignee, project, resolution date
   - LLM extracts entities from description
   - Updates human capability profiles
3. Calculates initial fit_score based on resolve count + recency

---

### Executor Service

#### `POST /executeDecision`
**Purpose**: Executes decision by creating Jira issue with assigned assignee. This is the actual execution.

**Why it exists**: Decisions are useless without execution. This creates the actual ticket with assignee.

**Request Body**:
```typescript
{
  decision_id: string;
  work_item_id: string;
  primary_human_id: string;
  backup_human_ids: string[];
  evidence: Array<{
    type: string;
    text: string;
  }>;
  work_item: {
    service: string;
    severity: string;
    description: string;
  };
}
```

**Response** (200 OK):
```typescript
{
  executed_action_id: string;
  jira_issue_key: string;  // e.g., "PROJ-123"
  jira_issue_id: string;   // Jira's internal ID
  assigned_human_id: string;
  created_at: string;
  message: "Jira issue created successfully"
}
```

**Processing Flow**:
1. Maps WorkItem.service → Jira project (via config)
2. Maps WorkItem.severity → Jira priority
3. Maps Human.id → Jira accountId
4. Creates Jira issue via API with assignee
5. Stores Jira issue key in DB
6. Links back to WorkItem

**Jira Issue Format**:
```json
{
  "fields": {
    "project": {"key": "PROJ"},
    "summary": "[WorkItem description]",
    "description": "Assigned by Goliath\n\n*Primary:* [human_name]\n*Backup:* [backup_name]\n\n*Evidence:*\n- [evidence 1]\n- [evidence 2]",
    "issuetype": {"name": "Bug"},
    "priority": {"name": "Critical"},
    "assignee": {"accountId": "[jira_account_id]"}
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid decision_id or missing fields
- `500 Internal Server Error`: Jira API failure (falls back to DB storage)
- `503 Service Unavailable`: Jira API down (stores in DB, shows in UI)

**Fallback**: If Jira API fails, stores rendered message in DB. UI can display it.

---

### Explain Service

#### `POST /explainDecision`
**Purpose**: Generates contextual evidence bullets explaining why a decision was made. Uses LLM (not templates).

**Why it exists**: Trust requires explanation. People need to know WHY a decision was made.

**Request Body**:
```typescript
{
  work_item: {
    id: string;
    service: string;
    severity: string;
    description: string;
  };
  decision: {
    primary_human_id: string;
    confidence: number;
  };
  candidate_features: Array<{
    human_id: string;
    fit_score: number;
    recent_resolves: number;
    on_call: boolean;
    pages_7d: number;
    similar_incidents: number;
  }>;
  top2_margin: number;      // Difference between top1 and top2 scores
  constraint_results: Array<{
    name: string;
    passed: boolean;
    reason?: string;
  }>;
}
```

**Response** (200 OK):
```typescript
{
  evidence: Array<{
    type: "recent_resolution" | "on_call" | "low_load" | "similar_incident" | "fit_score";
    text: string;          // Contextual, time-bounded explanation
    time_window: string;   // e.g., "last 7 days"
    source: string;        // Where this evidence came from
  }>;
  why_not_next_best: string[];  // 1-2 specific reasons
  constraints_summary: string[]; // All constraints with pass/fail
}
```

**Why LLM (not templates)**:
- Flexible: Handles any combination of stats/constraints
- Contextual: Generates specific explanations based on actual data
- Deterministic: Temperature=0, same input → same output
- No hardcoding: Works for edge cases automatically

**Evidence Rules**:
- No hallucinations: Only uses provided data
- Time-bounded: Always includes time window
- Contextual: "For this incident" not "best engineer"
- Specific: "Resolved 3 similar API timeout incidents in last 7 days" not "experienced"

**Error Responses**:
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: LLM API failure

---

### Knowledge Graph API (New Endpoint)

#### `GET /graph/nodes`
**Purpose**: Returns nodes and edges for 3D knowledge graph visualization. Used by UI to render interactive graph.

**Why it exists**: Visual exploration of relationships (who worked on what, when, with whom) is powerful for understanding patterns and building trust.

**Query Parameters**:
```typescript
{
  node_type?: "human" | "work_item" | "service" | "decision" | "outcome";  // Filter by type
  service?: string;        // Filter by service
  time_range?: {          // Temporal filtering
    start: string;         // ISO 8601
    end: string;           // ISO 8601
  };
  limit?: number;          // Default: 1000 nodes
}
```

**Response** (200 OK):
```typescript
{
  nodes: Array<{
    id: string;
    type: "human" | "work_item" | "service" | "decision" | "outcome";
    label: string;         // Display name
    x: number;            // 3D coordinate (PCA-reduced from 768D embedding)
    y: number;
    z: number;
    color: string;        // Hex color based on type
    metadata: {           // Type-specific metadata
      // For humans:
      display_name?: string;
      fit_score?: number;
      // For work_items:
      severity?: string;
      description?: string;
      // For services:
      name?: string;
      // etc.
    };
  }>;
  edges: Array<{
    source: string;        // Node ID
    target: string;        // Node ID
    type: "resolved" | "transferred" | "co_worked" | "assigned" | "belongs_to";
    timestamp: string;     // ISO 8601
    weight?: number;      // Edge weight (e.g., similarity score)
  }>;
  stats: {
    total_nodes: number;
    total_edges: number;
    by_type: {
      human: number;
      work_item: number;
      service: number;
      decision: number;
      outcome: number;
    };
  };
}
```

**Processing Flow**:
1. Query PostgreSQL for nodes (filtered by params)
2. Query PostgreSQL for edges (filtered by time range)
3. Get 3D coordinates from `embedding_3d_x/y/z` columns (pre-computed via PCA)
4. Apply color coding based on node type
5. Return nodes + edges for visualization

**Why 3D coordinates**:
- PCA reduces 768D embeddings to 3D (preserves similarity structure)
- Similar incidents cluster together in 3D space
- Humans who worked on similar things cluster together
- Visual patterns emerge that tables can't show

**Error Responses**:
- `400 Bad Request`: Invalid query parameters
- `500 Internal Server Error`: Database error

---

#### `GET /graph/similar/:work_item_id`
**Purpose**: Returns similar work items in 3D space. Shows clustering of similar incidents.

**Why it exists**: Visualize why certain incidents are considered similar (they cluster in 3D space).

**Path Parameters**:
- `work_item_id`: string

**Query Parameters**:
```typescript
{
  limit?: number;          // Default: 10
  certainty?: number;     // Minimum similarity (0.0-1.0), default: 0.7
}
```

**Response** (200 OK):
```typescript
{
  current: {
    id: string;
    x: number;
    y: number;
    z: number;
    description: string;
  };
  similar: Array<{
    id: string;
    x: number;
    y: number;
    z: number;
    description: string;
    similarity_score: number;  // Cosine similarity from vector search
    resolver_id: string;
  }>;
}
```

**Processing Flow**:
1. Get current work item embedding from Weaviate
2. Vector similarity search in Weaviate
3. Get 3D coordinates for current + similar items
4. Return for visualization (shows clustering)

---

### Monitoring Service

#### `GET /healthz`
**Purpose**: Health check endpoint. Standard for all services.

**Response** (200 OK):
```typescript
{
  status: "healthy";
  service: "monitoring";
  uptime: number;  // seconds
}
```

---

#### `POST /monitoring/start`
**Purpose**: Start monitoring loop. Optional - can auto-start on service start.

**Request Body** (optional):
```typescript
{
  service_name?: string;      // Override config
  error_probability?: number;  // Override config
  log_interval?: number;      // Override config
}
```

**Response** (200 OK):
```typescript
{
  started: boolean;
  service_name: string;
  error_probability: number;
  log_interval: number;
  message: "Monitoring loop started"
}
```

---

#### `POST /monitoring/stop`
**Purpose**: Stop monitoring loop.

**Response** (200 OK):
```typescript
{
  stopped: boolean;
  message: "Monitoring loop stopped"
}
```

---

#### `GET /monitoring/status`
**Purpose**: Get current monitoring status.

**Response** (200 OK):
```typescript
{
  running: boolean;
  service_name: string;
  error_count: number;      // Errors logged since start
  last_error_at?: string;   // ISO 8601
  log_interval: number;
  error_probability: number;
}
```

---

### Common Endpoints (All Services)

#### `GET /healthz`
**Purpose**: Health check. Standard for all services.

**Response** (200 OK):
```typescript
{
  status: "healthy";
  service: string;  // "ingest" | "decision" | "learner" | "executor" | "explain" | "monitoring"
  version: string;
  uptime: number;  // seconds
}
```

**Error Responses**:
- `503 Service Unavailable`: Service is unhealthy

---

## API Design Principles

1. **RESTful**: Standard HTTP methods, status codes
2. **Idempotent**: Outcome endpoints use `event_id` for dedupe
3. **Structured**: All responses are JSON with consistent schemas
4. **Auditable**: All requests logged with correlation IDs
5. **Deterministic**: LLM calls use temperature=0 for reproducibility
6. **Error Handling**: Clear error messages, proper HTTP status codes
7. **Versioning**: Future: `/v1/` prefix for API versioning

---

## Hour-by-Hour Breakdown

### HOUR 0-4: Foundation & Contracts

#### Hour 0-1: All Hands Kickoff
**Everyone:**
- Clone repo, setup local env
- Review architecture diagram
- Understand contract structure
- Assign service ownership

**Person 1:**
- Initialize monorepo structure
- Create `/contracts/types.ts` with core types (including graph node/edge types)
- Setup Python FastAPI template for all services
- Create `/infra/docker-compose.yml` skeleton:
  - All services (ingest, decision, learner, executor, explain, monitoring, jira-simulator)
  - UI (Next.js)
  - PostgreSQL (knowledge graph)
  - Weaviate (vector database)
- Add `.env.example` with all service URLs, database connections
- Setup PostgreSQL database:
  - Create schema for knowledge graph (nodes, edges tables)
  - Setup connection pool
- Setup Weaviate instance:
  - Create schemas for WorkItem and Human classes
  - Configure vector dimensions (768 for all-mpnet-base-v2)

**Deliverables (Person 1 - Hour 0-1):**
- ✅ `/infra/docker-compose.yml`
- ✅ `/contracts/types.ts`
- ✅ `.env.example`
- ✅ PostgreSQL + Weaviate setup

**Why Person 1 does contracts?** Lead owns the "single source of truth" for data shapes. Others will PR additions.

#### Hour 1-2: Design System Foundation

**Person 5:**
- Initialize Next.js 14 project with shadcn/ui
- Create design system tokens (colors, typography, spacing)
- Build base layout component (off-black bg, off-white text)
- Create typography scale (headings, body, code)
- Setup Tailwind config with design tokens

**Why Person 5 does design system?** UI person needs design foundation before building pages. Others reference this.

**Everyone else:**
- Review contracts, ask questions
- Setup local dev environment
- Familiarize with service they'll build

#### Hour 2-3: Service Scaffolding

**Person 1:**
- Scaffold `/services/ingest` (FastAPI + SQLite)
- Scaffold `/services/decision` (FastAPI + SQLite)
- Scaffold `/services/monitoring` (FastAPI, background task)
- Add `/healthz` endpoints to all
- Add request logging middleware
- Add correlation ID middleware (`x-correlation-id`)

**Person 2:**
- Scaffold `/services/learner` (FastAPI + PostgreSQL + Weaviate)
- Create PostgreSQL schema: `humans`, `human_service_stats`, `human_load`, `outcomes_dedupe`, knowledge graph edges
- Create Weaviate schemas: `WorkItem`, `Human`
- Add `/healthz` endpoint
- Setup embedding generation pipeline (sentence-transformers)
- Setup PCA reduction for 3D coordinates (768D → 3D)

**Person 3:**
- Scaffold `/services/executor` (FastAPI + SQLite)
- Create SQLite schema: `executed_messages`
- Add `/healthz` endpoint

**Person 4:**
- Scaffold `/services/explain` (FastAPI, no DB needed)
- Add `/healthz` endpoint

**Person 5:**
- Create base UI components (Button, Card, Badge, Table)
- Create layout structure (sidebar, main content)
- Add API client utilities (fetch with correlation IDs)
- Setup react-force-graph-3d:
  - Install: `npm install react-force-graph-3d`
  - Create KnowledgeGraph3D component
  - Setup 3D canvas with controls (drag, zoom, rotate)
- Setup graph data fetching:
  - API endpoint: `GET /graph/nodes` (from Decision or new Graph service)
  - Load nodes/edges, apply 3D coordinates
  - Color coding based on node type
- Setup filtering UI:
  - Filter by node type, service, time range
  - Search nodes
  - Temporal slider

**Why separate scaffolding?** Each service is independent. No dependencies yet.

#### Hour 3-4: Contract Finalization + LLM Setup

**Person 1:**
- Finalize `/contracts/types.ts` based on team feedback
- Create `/contracts/openapi.yaml` (optional, but helpful)
- Document service endpoints in `/contracts/README.md`
- Create `/contracts/llm_prompts.md` - document all LLM prompts for consistency
- Setup LLM client (OpenAI or Anthropic) with error handling and retries

**Everyone:**
- Review contracts, ensure understanding
- Review LLM prompt patterns (deterministic, structured outputs)
- Document any questions/assumptions
- Lock contracts (no changes after this without team approval)

**Why lock contracts?** Prevents breaking changes during parallel development.
**Why LLM prompts doc?** Ensures consistent prompt patterns across services (deterministic, structured, auditable).

---

### HOUR 4-12: Core Service Implementation (Isolated)

#### Hour 4-5: Monitoring Service (Person 3)

**What to build:**
- Background service that continuously logs for a service
- Periodically logs errors (ERROR, CRITICAL level)
- When error detected → calls Ingest `POST /ingest/demo` to create WorkItem
- Configurable: service name, error frequency, log rate

**Implementation:**
```python
# Background task that runs continuously
async def monitoring_loop():
    service_name = "api-service"  # or from config
    error_probability = 0.05  # 5% chance of error per cycle
    log_interval = 5  # seconds between log cycles
    
    while True:
        # Normal logging (INFO, WARN, DEBUG)
        log_level = random.choice(["INFO", "WARN", "DEBUG"])
        log_message = generate_log_message(service_name, log_level)
        print(f"[{log_level}] {log_message}")
        
        # Occasionally log error
        if random.random() < error_probability:
            error_type = random.choice([
                "High error rate detected",
                "Database connection timeout",
                "Memory leak detected",
                "API endpoint returning 500",
                "Service degradation"
            ])
            
            # Preprocess error with LLM (clean, normalize, extract key info)
            cleaned_description = await llm_preprocess_log(error_type, service_name)
            # cleaned_description = structured, normalized version of error
            
            # Create WorkItem via Ingest
            work_item = {
                "service": service_name,
                "severity": random.choice(["sev1", "sev2", "sev3"]),
                "description": cleaned_description,  # Use cleaned version
                "raw_log": error_type,  # Store original for audit
                "type": "incident"
            }
            
            # Call Ingest service
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{INGEST_URL}/ingest/demo",
                    json=work_item
                )
            
            print(f"[ERROR] {error_type} - WorkItem created (cleaned: {cleaned_description})")

async def llm_preprocess_log(raw_log: str, service_name: str) -> str:
    """Use LLM to clean and normalize log text before processing."""
    prompt = f"""
Clean and normalize this error log. Return ONLY the cleaned description, no other text.

Raw log: {raw_log}
Service: {service_name}

Rules:
- Remove noise (timestamps, log levels, file paths if not relevant)
- Normalize terminology (consistent error type names)
- Fix typos if obvious
- Extract key information (error type, affected component, severity indicators)
- Keep it concise but informative
- Return clean, structured description ready for entity extraction

Cleaned description:
"""
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # Deterministic
    )
    return response.choices[0].message.content.strip()
        
        await asyncio.sleep(log_interval)
```

**Endpoints:**
- `GET /healthz` - health check
- `POST /monitoring/start` - start monitoring loop (optional, can auto-start)
- `POST /monitoring/stop` - stop monitoring loop
- `GET /monitoring/status` - get current status (service name, error count, etc.)

**Configuration:**
- `MONITORING_SERVICE_NAME`: Service to monitor (e.g., "api-service", "payment-service")
- `MONITORING_ERROR_PROBABILITY`: Probability of error per cycle (0.0-1.0)
- `MONITORING_LOG_INTERVAL`: Seconds between log cycles
- `MONITORING_INGEST_URL`: URL of Ingest service

**Why Monitoring Service exists:**
- **Realistic simulation**: Simulates what ServiceNow/Datadog/PagerDuty would do
- **Continuous operation**: Runs in background, creates incidents automatically
- **Demo-friendly**: No manual triggering needed, errors appear naturally
- **Production-ready pattern**: Same pattern would work with real monitoring systems

**How it connects:**
- Calls Ingest `POST /ingest/demo` when error detected
- Ingest creates WorkItem → triggers Decision → Executor creates Jira issue

**Acceptance criteria:**
- Continuously logs (INFO, WARN, DEBUG)
- Periodically logs errors (ERROR, CRITICAL)
- Creates WorkItem via Ingest when error detected
- Configurable service name, error frequency, log rate
- Can start/stop monitoring loop

**Deliverables (Person 3 - Monitoring):**
- ✅ `/services/monitoring/` - Complete Monitoring service
- ✅ `/services/monitoring/README.md` - Monitoring service docs
- ✅ `/services/monitoring/scripts/test_standalone.sh` - Standalone testing

#### Hour 5-6: Ingest Service (Person 3)

**What to build:**
- `POST /ingest/demo` - creates demo WorkItem (simulates monitoring/observability systems) - **PRIMARY SOURCE FOR MVP**
- `POST /webhooks/jira` - accepts Jira webhook (optional, if unassigned issues need routing)
- `POST /work-items` - manual work item creation (from UI)
- `GET /work-items` - list all work items
- `GET /work-items/:id` - get single work item
- `POST /work-items/:id/outcome` - record outcome, forward to learner

**Work Item Sources:**

**For MVP (Demo):**
- **Demo endpoint** (primary): Simulates what would come from monitoring/observability systems
  - In production: ServiceNow incidents, Datadog alerts, PagerDuty incidents, New Relic alerts, etc.
  - For demo: Simple POST with service, severity, description
  - Format: `{service: "api", severity: "sev1", description: "High error rate detected"}`
  - **Why demo endpoint?** Real integrations (ServiceNow, Datadog, etc.) require OAuth, webhook setup, API keys - too much scope for MVP. Demo endpoint simulates the same data structure.

**For Production (Future):**
- **ServiceNow webhook**: Incident created → WorkItem
- **Datadog webhook**: Alert triggered → WorkItem
- **PagerDuty webhook**: Incident created → WorkItem
- **New Relic webhook**: Alert fired → WorkItem
- **Jira webhook** (optional): Unassigned issue → WorkItem
- **Manual creation** (from UI): User creates work item directly

**Jira Webhook Handling (if configured):**
- Extract: `issue.key`, `issue.fields.summary`, `issue.fields.description`, `issue.fields.priority`, `issue.fields.project.key`
- Map Jira priority → severity (Critical=sev1, High=sev2, Medium=sev3, Low=sev4)
- Map Jira project → service (config: `JIRA_PROJECT_TO_SERVICE_MAP`)
- Store `issue.key` in `origin_system` field (e.g., "JIRA-123")
- Only process if `issue.fields.assignee` is null (unassigned)

**Database Schema (PostgreSQL for knowledge graph):**
```sql
-- WorkItems table (also stored in Weaviate as vectors)
CREATE TABLE work_items (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  service TEXT NOT NULL,
  severity TEXT NOT NULL,
  description TEXT, -- cleaned/normalized description (LLM preprocessed)
  raw_log TEXT, -- original raw log/description before preprocessing (for audit)
  embedding_3d_x REAL, -- PCA-reduced 3D coordinates for visualization
  embedding_3d_y REAL,
  embedding_3d_z REAL,
  created_at TIMESTAMP NOT NULL,
  origin_system TEXT, -- e.g., "JIRA-123" or "demo-abc"
  creator_id TEXT,
  jira_issue_key TEXT, -- if created via Executor, link back
  raw_payload TEXT -- store original webhook
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

**Weaviate Schema:**
```json
{
  "class": "WorkItem",
  "vectorizer": "none",  // We provide embeddings
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

CREATE TABLE outcomes (
  id TEXT PRIMARY KEY,
  work_item_id TEXT NOT NULL,
  event_id TEXT UNIQUE NOT NULL, -- for dedupe
  type TEXT NOT NULL,
  decision_id TEXT,
  actor_id TEXT,
  timestamp TEXT NOT NULL,
  FOREIGN KEY (work_item_id) REFERENCES work_items(id)
);
```

**Why Ingest exists:**
- **Single source of truth**: All work items flow through here, regardless of source
- **Normalization**: Different sources have different formats. Ingest creates canonical WorkItem.
  - **Demo endpoint** → WorkItem (simulates ServiceNow/Datadog/PagerDuty/etc.)
  - **Jira issue** → WorkItem (if webhook configured, project=service, priority=severity, key=origin_system)
  - **Manual creation** → WorkItem (direct mapping)
  - **Future**: ServiceNow incident → WorkItem, Datadog alert → WorkItem, etc.
- **Outcome collection**: When humans override/resolve, outcomes flow back here first, then to Learner.

**Note on Demo vs Production:**
- **MVP**: Demo endpoint simulates monitoring/observability systems (ServiceNow, Datadog, PagerDuty, etc.)
- **Production**: Real webhooks from these systems would flow through same normalization logic
- **Why not integrate real systems in MVP?** OAuth, webhook setup, API keys, rate limits - too much scope. Demo endpoint proves the concept.

**How it connects:**
- Decision service calls `GET /work-items/:id` to get work item
- UI calls `GET /work-items` to list items
- UI calls `POST /work-items/:id/outcome` when user overrides
- Ingest calls Learner `POST /outcomes` when outcome is recorded

**Acceptance criteria:**
- Can create WorkItem via demo endpoint
- Can list work items
- Can record outcome (forwards to learner)
- All requests logged with correlation ID

**Deliverables (Person 3 - Ingest):**
- ✅ `/services/ingest/` - Complete Ingest service
- ✅ `/services/ingest/README.md` - Ingest service docs
- ✅ `/services/ingest/scripts/test_standalone.sh` - Standalone testing
- ✅ `/services/ingest/scripts/mock_data.json` - Mock data

#### Hour 4-6: Learner Service + Jira Simulator Foundation (Person 2)

**What to build (Learner):**
- `GET /profiles?service=X` - returns humans with stats for service
- `POST /outcomes` - updates stats idempotently (dedupe by event_id)
- `GET /stats?human_id=X` - returns stats for UI display
- `POST /sync/jira` - syncs closed Jira tickets to build capability profiles (background job)

**What to build (Jira Simulator):**
- Full Jira REST API v3 mock (exact endpoint compatibility)
- Port: 8080
- Endpoints:
  - `GET /rest/api/3/search` - JQL search (for Learner to read closed tickets)
  - `POST /rest/api/3/issue` - Create issue (for Executor to create issues)
  - `GET /rest/api/3/issue/:key` - Get issue details
  - `PUT /rest/api/3/issue/:key` - Update issue (assignee, status, etc.)
  - `GET /rest/api/3/user/search` - Search users
  - `GET /rest/api/3/project` - List projects
- Seeding script: `scripts/seed_jira_data.py` - populates 200 people with realistic data

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
  - **LLM-extracted entities** used for similar incident matching (not keyword matching)
- **Sync strategy**:
  - Initial sync: Pull last 90 days of closed tickets
  - Incremental: Poll every 5 minutes for new closed tickets
  - Cache in SQLite to avoid hitting Jira API constantly

**PostgreSQL Schema (Knowledge Graph):**
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
```

**Weaviate Schema (Human Embeddings):**
```json
{
  "class": "Human",
  "vectorizer": "none",  // We provide embeddings
  "properties": [
    {"name": "id", "dataType": ["string"]},
    {"name": "display_name", "dataType": ["string"]},
    {"name": "service", "dataType": ["string"]},
    {"name": "capability_summary", "dataType": ["text"]}  // Aggregated from resolved work items
  ]
}
```

**Why Learner exists:**
- **Capability modeling**: Tracks who can do what, based on Jira closed tickets (not resumes)
  - Reads Jira closed tickets to see who actually worked on what
  - Tracks recency (expertise decays - someone who fixed bugs 6 months ago may not remember)
  - Tracks teams (Jira projects map to teams/services)
- **Time-aware**: Stats decay over time (expertise drifts)
- **Outcome learning (CORE MVP FEATURE)**: 
  - **When Jira issue is assigned/completed** → Learner updates capability profiles
  - **Resolved without transfer** → fit_score increases (+0.1), resolves_count increases
  - **Reassigned/transferred** → fit_score decreases (-0.15), transfers_count increases
  - **Future decisions** → use updated fit_score → better routing over time
  - **This is THE moat**: System gets smarter with every assignment/completion
- **Jira as source of truth**: Jira closed tickets are the ground truth for "who can do what"

**How it connects:**
- Decision service calls `GET /profiles?service=X` to get candidates
- Ingest calls `POST /outcomes` when outcome recorded
- UI calls `GET /stats?human_id=X` to show stats

**Acceptance criteria:**
- Seeding script creates 2-3 services, 8-12 humans with realistic distributions
- `GET /profiles` returns humans with fit_score, resolves, transfers, pages_7d, active_items
- `POST /outcomes` updates stats idempotently (same event_id = no duplicate update)
- Stats are time-windowed (only count recent activity)
- `POST /sync/jira` can sync closed tickets and update capability profiles
- Jira integration works (with API token in env vars)

#### Hour 6-8: Decision Service Core (Person 1)

**What to build:**
- `POST /decide` - takes WorkItem, returns Decision
- `GET /decisions/:work_item_id` - get decision for work item
- `GET /audit/:work_item_id` - get full audit trace

**SQLite schema:**
```sql
CREATE TABLE decisions (
  id TEXT PRIMARY KEY,
  work_item_id TEXT UNIQUE NOT NULL,
  primary_human_id TEXT NOT NULL,
  backup_human_ids TEXT, -- JSON array
  confidence REAL NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE decision_candidates (
  decision_id TEXT NOT NULL,
  human_id TEXT NOT NULL,
  score REAL NOT NULL,
  rank INTEGER NOT NULL,
  filtered BOOLEAN DEFAULT FALSE,
  filter_reason TEXT,
  score_breakdown TEXT, -- JSON: {expertise: 0.8, recency: 0.6, ...}
  PRIMARY KEY (decision_id, human_id),
  FOREIGN KEY (decision_id) REFERENCES decisions(id)
);

CREATE TABLE constraint_results (
  decision_id TEXT NOT NULL,
  constraint_name TEXT NOT NULL,
  passed BOOLEAN NOT NULL,
  reason TEXT,
  PRIMARY KEY (decision_id, constraint_name),
  FOREIGN KEY (decision_id) REFERENCES decisions(id)
);
```

**Decision algorithm (simplified for MVP):**

1. **Candidate Generation:**
   - Call Learner `GET /profiles?service=X`
   - Optionally: Check GitHub for recent committers (cached, optional)
   - Return 3-10 candidates

2. **Constraint Filtering (veto-only):**
   - On-call required for sev1/sev2 (unless none exist)
   - Interruption threshold: if `pages_7d > 10`, filter out (unless sev1)
   - Exclude creator if present
   - Log filter reason for each filtered candidate

3. **Scoring:**
   ```
   score = (
     fit_score * 0.4 +           # from learner
     recency_score * 0.3 +       # time since last resolve
     availability_score * 0.2 +  # on-call, low load
     risk_penalty * 0.1          # high severity = less penalty
   )
   ```
   - `recency_score`: 1.0 if resolved similar incident in last 7 days, decays to 0.3
   - `availability_score`: 1.0 if on-call, 0.8 if low load, 0.5 otherwise
   - `risk_penalty`: 0.0 for sev1, increases for lower severity

4. **Confidence:**
   ```
   confidence = 1.0 - (top2_score - top1_score) / top1_score
   ```
   - If top1 and top2 are close → low confidence
   - If top1 is clearly best → high confidence

**Why Decision exists:**
- **The brain**: This is where the magic happens. Takes WorkItem, returns Decision.
- **Deterministic**: Same inputs → same decision (except time-varying load)
- **Auditable**: Every step logged (candidates, constraints, scores)

**How it connects:**
- Called by Ingest (or UI) when work item created
- Calls Learner `GET /profiles` for candidates
- Calls Explain `POST /explainDecision` for evidence
- Calls Executor `POST /executeDecision` to execute

**Acceptance criteria:**
- `POST /decide` returns Decision with primary + backups + confidence
- All candidates logged with scores and filter reasons
- `GET /audit` returns full reasoning chain
- Deterministic: same WorkItem → same Decision (given same state)

#### Hour 8-10: Executor Service (Person 4)

**What to build:**
- `POST /executeDecision` - takes Decision, creates Jira issue with assignee
- Slack integration (optional, behind flag, for notifications)
- Fallback: store rendered message in SQLite if Jira fails

**SQLite schema:**
```sql
CREATE TABLE executed_actions (
  id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL,
  jira_issue_key TEXT, -- e.g., "PROJ-123"
  jira_issue_id TEXT, -- Jira's internal ID
  assigned_human_id TEXT NOT NULL,
  backup_human_ids TEXT, -- JSON array
  created_at TEXT NOT NULL
);
```

**Jira Integration (WRITE) - Uses Person 1's Jira Simulator:**
- **Purpose**: Create Jira issues with assigned assignees (the actual execution)
- **Jira API Call**: `POST /rest/api/3/issue`
- **Note**: Calls Person 1's Jira Simulator service (not real Jira)
- **Request Body**:
  ```json
  {
    "fields": {
      "project": {"key": "PROJ"},
      "summary": "[WorkItem description]",
      "description": "Assigned by Goliath\n\n*Primary:* [human_name]\n*Backup:* [backup_name]\n\n*Evidence:*\n- [evidence 1]\n- [evidence 2]",
      "issuetype": {"name": "Bug"},
      "priority": {"name": "[severity mapping]"},
      "assignee": {"accountId": "[primary_human_jira_account_id]"}
    }
  }
  ```
- **What we store**:
  - `jira_issue_key` (e.g., "PROJ-123") - links back to WorkItem
  - `jira_issue_id` - for future updates
  - `assigned_human_id` - who we assigned
- **Mapping**:
  - WorkItem.service → Jira project (config: `SERVICE_TO_JIRA_PROJECT_MAP`)
  - WorkItem.severity → Jira priority (sev1=Critical, sev2=High, etc.)
  - Human.id → Jira accountId (from Learner's human table, needs Jira accountId field)

**Execution logic:**
1. Map WorkItem → Jira issue fields
2. Map Human.id → Jira accountId (from human table)
3. Create Jira issue via API
4. Store Jira issue key in executed_actions table
5. Link back to WorkItem (store jira_issue_key in WorkItem table)
6. Optional: Post to Slack channel with Jira link (if enabled)

**Why Executor exists:**
- **Bounded actions**: Doesn't make decisions, just executes them
- **Jira as execution surface**: Creates the actual ticket with assignee
- **Reversible**: Jira issue can be reassigned (triggers outcome)
- **Safe**: No free-form text, only structured Jira API calls

**How it connects:**
- Called by Decision service (or UI) after decision made
- Creates Jira issue with assigned assignee
- **Learning Loop (CORE MVP)**:
  1. Executor creates Jira issue with assignee
  2. Human works on issue → completes it in Jira
  3. Jira issue status changes to "Done" → Jira webhook fires
  4. Ingest receives webhook → creates outcome (type="resolved")
  5. Ingest calls Learner `POST /outcomes` with outcome
  6. Learner updates fit_score (+0.1), resolves_count (+1), last_resolved_at
  7. **Next decision** → uses updated fit_score → better routing!
  
  **OR if reassigned:**
  1. Human reassigns Jira issue to someone else
  2. Jira webhook fires → Ingest → Learner
  3. Original assignee: fit_score decreases (-0.15), transfers_count (+1)
  4. New assignee: fit_score increases slightly (+0.05)
  5. **Next decision** → uses updated fit_score → learns from mistake!

**Acceptance criteria:**
- Can create Jira issue with assigned assignee
- Jira issue key stored and linked to WorkItem
- Falls back gracefully if Jira API fails (store in DB, show in UI)
- Optional Slack notification works (if enabled)

**Deliverables (Person 4 - Executor):**
- ✅ `/services/executor/` - Complete Executor service
- ✅ `/services/executor/README.md` - Executor service docs
- ✅ `/services/executor/scripts/test_standalone.sh` - Standalone testing
- ✅ `/services/executor/scripts/mock_data.json` - Mock data

#### Hour 10-12: Explain Service (Person 4)

**What to build:**
- `POST /explainDecision` - takes Decision + candidate features, returns Evidence[]
- **Uses LLM** for evidence generation (not hardcoded templates)

**Input:**
```typescript
{
  work_item: WorkItem;
  decision: Decision;
  candidate_features: {
    human_id: string;
    fit_score: number;
    recent_resolves: number;
    on_call: boolean;
    pages_7d: number;
    similar_incidents: number; // from LLM matching
  }[];
  top2_margin: number; // difference between top1 and top2 scores
  constraint_results: ConstraintResult[];
}
```

**Output:**
```typescript
{
  evidence: Evidence[]; // 5-7 bullets
  why_not_next_best: string[]; // 1-2 reasons
  constraints_summary: string[]; // constraint results
}
```

**LLM-based Evidence Generation:**
```python
def generate_evidence(work_item: WorkItem, decision: Decision, candidates: List[dict]) -> dict:
    """Use LLM to generate contextual evidence (not templates)."""
    
    prompt = f"""
Generate evidence bullets explaining why {decision.primary_human_id} was chosen for this incident.

Incident: {work_item.description}
Service: {work_item.service}
Severity: {work_item.severity}

Primary candidate stats:
- fit_score: {candidates[0]['fit_score']}
- recent_resolves: {candidates[0]['recent_resolves']}
- on_call: {candidates[0]['on_call']}
- pages_7d: {candidates[0]['pages_7d']}
- similar_incidents: {candidates[0]['similar_incidents']}

Next best candidate stats:
- fit_score: {candidates[1]['fit_score']}
- recent_resolves: {candidates[1]['recent_resolves']}
- on_call: {candidates[1]['on_call']}

Constraints checked: {json.dumps(decision.constraints_checked)}

Return ONLY valid JSON with this structure:
{{
  "evidence": [
    {{
      "type": "recent_resolution" | "on_call" | "low_load" | "similar_incident" | "fit_score",
      "text": "specific, time-bounded explanation",
      "time_window": "last 7 days" | "last 30 days" | etc.
    }}
  ],
  "why_not_next_best": [
    "specific reason why primary is better than next best"
  ],
  "constraints_summary": [
    "constraint_name: passed/failed - reason"
  ]
}}

Rules:
- evidence: 5-7 bullets, all factual and time-bounded
- why_not_next_best: 1-2 specific reasons
- constraints_summary: all constraints with pass/fail status
- NO global claims ("best engineer") - only contextual ("for this incident")
- NO hallucinations - only use provided stats
- Be specific: "Resolved 3 similar API timeout incidents in last 7 days" not "experienced"
"""
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # Deterministic
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)
```

**Why LLM instead of templates:**
- **Flexible**: Handles variations in stats, contexts, edge cases
- **Contextual**: Generates specific explanations based on actual data
- **Deterministic**: Same input → same output (temperature=0)
- **Auditable**: LLM response stored in audit trail
- **No hardcoding**: Works for any combination of stats/constraints

**Why Explain exists:**
- **Trust**: People need to know WHY a decision was made
- **Auditability**: Evidence is part of audit trail
- **Reversibility**: "Why not X?" helps people understand overrides

**How it connects:**
- Called by Decision service after decision made
- Evidence included in Decision object
- UI displays evidence

**Acceptance criteria:**
- Returns 5-7 evidence bullets (all factual, time-bounded)
- Returns 1-2 "why not next best" reasons
- Returns constraints summary
- No global claims, all contextual

**Deliverables (Person 4 - Explain):**
- ✅ `/services/explain/` - Complete Explain service
- ✅ `/services/explain/README.md` - Explain service docs
- ✅ `/services/explain/scripts/test_standalone.sh` - Standalone testing
- ✅ `/services/explain/scripts/mock_data.json` - Mock data

---

### HOUR 12-24: Feature Completion & UI Foundation

#### Hour 12-16: UI Foundation (Person 5)

**What to build:**
- Work Items List page
- Work Item Detail page (decision, evidence, constraints, audit)
- Override workflow
- Stats display
- **Knowledge Graph Visualization** (3D interactive graph)
  - react-force-graph-3d component
  - Load nodes/edges from PostgreSQL
  - 3D coordinates from embedding PCA reduction
  - Color-coded nodes (Humans=blue, WorkItems=red, Services=green, Decisions=purple, Outcomes=amber)
  - Interactive: drag to rotate, scroll to zoom, click for details
  - Filter by node type, time range, service
  - Legend showing node counts

**Design specs:**

**Work Items List:**
- Table: ID, Service, Severity, Created, Status, Actions
- Filter by service, severity
- Click row → navigate to detail

**Work Item Detail:**
- Header: Service, Severity, Created, Status
- Decision Card:
  - Primary assignee (large, prominent)
  - Backup assignees (smaller)
  - Confidence badge
  - Evidence bullets (collapsible)
  - Constraints table
- Actions:
  - Override button (opens modal)
  - Mark resolved button
- Audit drawer (slide-out):
  - Candidate set with scores
  - Filter reasons
  - Score breakdown

**Override Modal:**
- Dropdown: select new assignee
- Reason field (optional)
- Submit → calls `POST /work-items/:id/outcome` with type=reassigned

**Design tokens:**
```css
--bg-primary: #0a0a0a;
--bg-secondary: #141414;
--text-primary: #f5f5f5;
--text-secondary: #a0a0a0;
--border: #1a1a1a;
--accent-blue: #3b82f6;
--accent-green: #10b981;
--accent-red: #ef4444;
```

**Why UI exists:**
- **Visibility**: People need to see decisions and evidence
- **Reversibility**: Override is the learning signal
- **Trust**: Audit trail must be inspectable

**How it connects:**
- Calls Ingest `GET /work-items`, `GET /work-items/:id`
- Calls Decision `GET /decisions/:work_item_id`, `GET /audit/:work_item_id`
- Calls Learner `GET /stats?human_id=X`
- Calls Ingest `POST /work-items/:id/outcome` for overrides

**Acceptance criteria:**
- Can list work items
- Can view decision with evidence
- Can override (updates learner stats)
- Can view audit trace
- Design is clean, opinionated, no ambiguity

**Deliverables (Person 5):**
- ✅ `/apps/ui/` - Complete UI application
- ✅ `/apps/ui/README.md` - UI docs
- ✅ Design system tokens
- ✅ Knowledge graph 3D visualization component
- ✅ All pages (Work Items List, Detail, Override, Stats, Audit)

#### Hour 16-18: Monitoring Service Completion (Person 1)

**What to complete:**
- Error detection logic (different error types, severities)
- WorkItem creation with realistic data
- Configurable error patterns (burst errors, gradual degradation, etc.)
- Log aggregation (count errors, track patterns)
- Integration with Ingest service

**Error patterns to simulate:**
- **Burst errors**: Multiple errors in short time → sev1
- **Gradual degradation**: Increasing error rate → sev2
- **Intermittent errors**: Random errors → sev3
- **Service-specific errors**: Different error types per service

**Why this matters:**
- **Realistic demo**: Errors appear naturally, not manually triggered
- **Pattern variety**: Different error types test different routing scenarios
- **Production pattern**: Same logic would work with real monitoring systems

**Acceptance criteria:**
- Multiple error types simulated
- Different severities based on error pattern
- WorkItems created automatically when errors detected
- Monitoring loop runs continuously in background

#### Hour 18-22: Decision Service Completion (Person 1)

**What to complete:**
- Real candidate generation (not placeholder)
- Constraint filtering logic
- Scoring algorithm implementation
- Confidence calculation
- Audit endpoint

**Candidate generation:**
```python
def generate_candidates(work_item: WorkItem) -> List[Human]:
    # 1. Get profiles from learner
    profiles = learner_client.get_profiles(service=work_item.service)
    
    # 2. Vector-based similar incident matching (production-grade)
    # Generate embedding for current work item
    current_embedding = embedding_model.encode(work_item.description)
    
    # Vector similarity search in Weaviate
    similar_incidents = weaviate_client.query.get(
        "WorkItem",
        ["id", "description", "resolver_id", "service", "resolved_at"]
    ).with_near_vector({
        "vector": current_embedding.tolist(),
        "certainty": 0.7  # Minimum similarity threshold
    }).with_limit(10).do()
    
    # Returns: [{incident_id, similarity_score, resolver_id, service}]
    # similarity_score from vector cosine similarity (0.0-1.0)
    
    # Boost candidates who resolved similar incidents
    for incident in similar_incidents:
        resolver = find_human(incident.resolver_id)
        if resolver in profiles and incident.service == work_item.service:
            resolver.similar_incident_score = incident.similarity_score
    
    # 3. LLM entity extraction (for evidence and explanation)
    entities = llm_extract_entities(work_item.description)
    # entities = {service_components: [...], error_types: [...], affected_systems: [...]}
    
    # 3. Optionally: Get GitHub committers (cached)
    if github_enabled:
        committers = get_recent_committers(work_item.service)  # cached
        # Merge with profiles, boost committers
    
    # 4. Return top 10 by fit_score + similar_incident_score
    return sorted(profiles, key=lambda p: p.fit_score + p.similar_incident_score, reverse=True)[:10]

def llm_extract_entities(description: str) -> dict:
    """Use LLM to extract structured entities from incident description."""
    prompt = f"""
Extract structured entities from this incident description. Return ONLY valid JSON, no other text.

Description: {description}

Return JSON with this exact structure:
{{
  "service_components": ["component1", "component2"],
  "error_types": ["timeout", "connection_error"],
  "affected_systems": ["api", "database"],
  "severity_indicators": ["high_error_rate", "service_degradation"]
}}

Rules:
- Be specific and factual (no interpretation)
- Only extract what is explicitly mentioned
- Return empty arrays if nothing found
- Use consistent terminology
"""
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # Deterministic
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# Vector similarity search (replaces LLM-based matching)
def find_similar_incidents_vector(work_item: WorkItem) -> List[dict]:
    """Use vector embeddings to find similar incidents (production-grade)."""
    from sentence_transformers import SentenceTransformer
    import weaviate
    
    # Generate embedding for current work item
    embedding_model = SentenceTransformer('all-mpnet-base-v2')
    current_embedding = embedding_model.encode(work_item.description)
    
    # Query Weaviate for similar work items
    similar = weaviate_client.query.get(
        "WorkItem",
        ["id", "description", "resolver_id", "service", "resolved_at", "severity"]
    ).with_near_vector({
        "vector": current_embedding.tolist(),
        "certainty": 0.7  # Minimum similarity threshold
    }).with_where({
        "path": ["service"],
        "operator": "Equal",
        "valueString": work_item.service
    }).with_limit(10).do()
    
    return [
        {
            "incident_id": item["id"],
            "similarity_score": item["_additional"]["certainty"],  # Cosine similarity
            "resolver_id": item["resolver_id"],
            "service": item["service"]
        }
        for item in similar["data"]["Get"]["WorkItem"]
    ]
```

**Constraint filtering:**
```python
def filter_candidates(candidates: List[Human], work_item: WorkItem) -> List[Tuple[Human, Optional[str]]]:
    filtered = []
    for candidate in candidates:
        reason = None
        
        # On-call check
        if work_item.severity in ['sev1', 'sev2']:
            if not candidate.on_call:
                reason = "Not on-call (required for sev1/sev2)"
        
        # Interruption threshold
        if candidate.pages_7d > 10 and work_item.severity != 'sev1':
            reason = f"High interruption load ({candidate.pages_7d} pages in 7d)"
        
        # Exclude creator
        if work_item.creator_id == candidate.id:
            reason = "Incident creator (excluded)"
        
        if reason:
            filtered.append((candidate, reason))
        else:
            filtered.append((candidate, None))
    
    return filtered
```

**Scoring (with Severity/Impact Matching):**
```python
def score_candidate(candidate: Human, work_item: WorkItem) -> float:
    fit_score = candidate.fit_score  # from learner
    recency_score = calculate_recency(candidate.last_resolved_at)
    availability_score = 1.0 if candidate.on_call else (0.8 if candidate.pages_7d < 5 else 0.5)
    
    # Severity/Impact matching (NEW)
    severity_match_score = calculate_severity_match(candidate, work_item)
    # High-severity work items should go to people who've handled high-severity before
    # Low-severity work items can go to anyone, but prefer people with capacity
    
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

**Why these algorithms:**
- **fit_score (40%)**: Primary signal from outcomes
- **recency (30%)**: Expertise decays, recent activity matters
- **availability (20%)**: On-call and low load = better
- **risk_penalty (10%)**: Don't interrupt high-value people for low-severity

**Acceptance criteria:**
- Candidate generation returns 3-10 candidates
- Constraints filter correctly
- Scoring produces reasonable rankings
- Confidence reflects top1-top2 margin
- Audit endpoint returns full trace

#### Hour 18-22: Jira Simulator Completion (Person 1)

**Jira Simulator Implementation:**

**Database Schema (PostgreSQL):**
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
  max_story_points INTEGER DEFAULT 21, -- Capacity limit (3-week sprint)
  current_story_points INTEGER DEFAULT 0, -- Currently assigned
  role TEXT -- e.g., "backend-engineer", "frontend-engineer", "sre", "product-manager"
);

-- Jira issues (work items)
CREATE TABLE jira_issues (
  id TEXT PRIMARY KEY,
  key TEXT UNIQUE NOT NULL, -- e.g., "PROJ-123"
  project_key TEXT NOT NULL,
  summary TEXT NOT NULL,
  description TEXT,
  issuetype_name TEXT NOT NULL, -- "Bug", "Task", "Story", "Epic"
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

**Seeding Script (`scripts/seed_jira_data.py`):**
```python
"""
Seeds Jira Simulator with realistic data:
- 200 people across different roles
- 3-5 services/projects
- Realistic work history (last 90 days):
  - Closed tickets (bugs, tasks, stories)
  - Open tickets (current capacity)
  - Story points assigned
  - Different severities/priorities
  - Different resolution times
"""
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# 200 people with different roles
ROLES = [
    "backend-engineer", "frontend-engineer", "sre", "devops-engineer",
    "product-manager", "qa-engineer", "data-engineer", "security-engineer"
]

SERVICES = ["api-service", "payment-service", "frontend-app", "data-pipeline", "infrastructure"]

def seed_jira_data():
    # Create projects
    projects = []
    for service in SERVICES:
        projects.append({
            "key": service.upper().replace("-", "")[:10],  # e.g., "APISERVICE"
            "name": service,
            "project_type_key": "software"
        })
    
    # Create 200 users
    users = []
    for i in range(200):
        role = random.choice(ROLES)
        max_story_points = random.choice([13, 21, 34])  # 2-week, 3-week, 5-week capacity
        users.append({
            "account_id": f"557058:{fake.uuid4()[:8]}",
            "display_name": fake.name(),
            "email_address": fake.email(),
            "active": True,
            "max_story_points": max_story_points,
            "current_story_points": random.randint(0, max_story_points // 2),  # Some capacity used
            "role": role
        })
    
    # Create closed tickets (last 90 days)
    closed_issues = []
    start_date = datetime.now() - timedelta(days=90)
    
    for _ in range(5000):  # 5000 closed tickets
        project = random.choice(projects)
        assignee = random.choice(users)
        created_at = fake.date_time_between(start_date=start_date, end_date='now')
        resolved_at = created_at + timedelta(
            days=random.randint(0, 7),  # Resolved within 0-7 days
            hours=random.randint(0, 23)
        )
        
        issue_type = random.choice(["Bug", "Task", "Story"])
        priority = random.choice(["Critical", "High", "Medium", "Low"])
        story_points = random.choice([1, 2, 3, 5, 8, 13]) if issue_type != "Bug" else None
        
        closed_issues.append({
            "id": fake.uuid4(),
            "key": f"{project['key']}-{random.randint(100, 9999)}",
            "project_key": project['key'],
            "summary": fake.sentence(),
            "description": fake.text(),
            "issuetype_name": issue_type,
            "priority_name": priority,
            "status_name": "Done",
            "assignee_account_id": assignee['account_id'],
            "reporter_account_id": random.choice(users)['account_id'],
            "story_points": story_points,
            "created_at": created_at,
            "updated_at": resolved_at,
            "resolved_at": resolved_at
        })
    
    # Create open tickets (current capacity)
    open_issues = []
    for _ in range(1000):  # 1000 open tickets
        project = random.choice(projects)
        assignee = random.choice(users)
        created_at = fake.date_time_between(start_date=start_date, end_date='now')
        
        issue_type = random.choice(["Bug", "Task", "Story"])
        priority = random.choice(["Critical", "High", "Medium", "Low"])
        story_points = random.choice([1, 2, 3, 5, 8, 13]) if issue_type != "Bug" else None
        status = random.choice(["To Do", "In Progress"])
        
        open_issues.append({
            "id": fake.uuid4(),
            "key": f"{project['key']}-{random.randint(100, 9999)}",
            "project_key": project['key'],
            "summary": fake.sentence(),
            "description": fake.text(),
            "issuetype_name": issue_type,
            "priority_name": priority,
            "status_name": status,
            "assignee_account_id": assignee['account_id'],
            "reporter_account_id": random.choice(users)['account_id'],
            "story_points": story_points,
            "created_at": created_at,
            "updated_at": created_at,
            "resolved_at": None
        })
    
    # Update user current_story_points based on open tickets
    for user in users:
        user_open_issues = [i for i in open_issues if i['assignee_account_id'] == user['account_id']]
        user['current_story_points'] = sum(i['story_points'] or 0 for i in user_open_issues)
    
    return {
        "projects": projects,
        "users": users,
        "closed_issues": closed_issues,
        "open_issues": open_issues
    }
```

**Jira Simulator Endpoints (REST v3 compatible):**
```python
# GET /rest/api/3/search?jql=...
@app.get("/rest/api/3/search")
async def jira_search(jql: str, startAt: int = 0, maxResults: int = 50):
    """
    JQL search endpoint - used by Learner to read closed tickets.
    Supports: project=PROJ AND status=Done AND resolved >= -90d
    """
    # Parse JQL, query database, return Jira format
    pass

# POST /rest/api/3/issue
@app.post("/rest/api/3/issue")
async def jira_create_issue(issue: dict):
    """
    Create issue - used by Executor to create issues with assignees.
    """
    pass

# GET /rest/api/3/issue/:key
@app.get("/rest/api/3/issue/{key}")
async def jira_get_issue(key: str):
    """Get issue details."""
    pass

# PUT /rest/api/3/issue/:key
@app.put("/rest/api/3/issue/{key}")
async def jira_update_issue(key: str, update: dict):
    """Update issue (assignee, status, etc.)."""
    pass
```

**Why Jira Simulator:**
- **No cloud dependencies**: Everything runs locally
- **Realistic data**: 200 people, 5000+ closed tickets, 1000+ open tickets
- **Story points & capacity**: Real capacity management (max_story_points, current_story_points)
- **Exact API compatibility**: Same endpoints as real Jira, so code works in production
- **Independent testing**: Each developer can run Jira Simulator standalone

**Independent Testing Strategy:**
- Each service can be tested without others running
- Jira Simulator can be run standalone: `docker run jira-simulator`
- Mock data seeded automatically on startup
- Services use environment variables for URLs (can point to mocks)
- Test scripts in each service directory: `scripts/test_standalone.sh`

**What to complete:**
- Outcome processing logic
- Stats update algorithm
- Time-windowed calculations
- Seeding script improvements

**Outcome processing:**
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
    elif outcome.type == 'reassigned':
        # Original assignee: penalty
        original_decision = get_decision(outcome.decision_id)
        stats = get_stats(original_decision.primary_human_id, outcome.service)
        stats.transfers_count += 1
        stats.fit_score = max(0.0, stats.fit_score - 0.15)  # penalty
        
        # New assignee: slight boost (they accepted it)
        new_stats = get_stats(outcome.actor_id, outcome.service)
        new_stats.fit_score = min(1.0, new_stats.fit_score + 0.05)
    
    # Update load
    load = get_load(outcome.actor_id)
    if outcome.type == 'resolved':
        load.active_items = max(0, load.active_items - 1)
    
    # Mark processed
    outcomes_dedupe.insert(outcome.event_id, outcome.timestamp)
```

**Time-windowed calculations:**
- Only count resolves/transfers in last 90 days
- Decay fit_score over time (multiply by 0.99 per day)
- Reset pages_7d daily (rolling window)

**Why these algorithms:**
- **fit_score updates**: Resolve = +0.1, transfer = -0.15 (asymmetric, transfers are worse)
- **Time decay**: Expertise fades, don't rely on old data
- **Dedupe**: Idempotent updates prevent double-counting

**Acceptance criteria:**
- Outcome processing updates stats correctly
- Dedupe works (same event_id = no duplicate)
- Time windows respected
- Seeding creates realistic data

#### Hour 20-24: Learner Service Completion (Person 2)

**What to complete:**
- Outcome processing logic
- Stats update algorithm
- Time-windowed calculations
- Seeding script improvements

**Deliverables (Person 2 - Learner Completion):**
- ✅ Outcome processing logic complete
- ✅ Stats update algorithm working
- ✅ Time-windowed calculations implemented
- ✅ Seeding creates realistic data

---

### HOUR 24-36: Polish & Testing

#### Hour 24-28: UI Polish (Person 5)

**What to polish:**
- Evidence display (collapsible, well-formatted)
- Constraints table (clear pass/fail indicators)
- Audit drawer (readable score breakdown)
- Override flow (smooth, clear feedback)
- Loading states, error states
- Responsive design

**Design details:**
- Evidence bullets: Icon + text, grouped by type
- Constraints: Green checkmark (passed), Red X (failed) with reason
- Score breakdown: Bar chart or table showing weights
- Confidence: Progress bar with color (green >0.7, yellow 0.4-0.7, red <0.4)

**Why polish matters:**
- **Trust**: Rough UI = untrustworthy system
- **Clarity**: Evidence must be readable
- **Reversibility**: Override must be obvious

#### Hour 28-32: Decision Service Testing (Person 1)

**What to test:**
- Determinism: same inputs → same outputs
- Constraint edge cases (zero candidates, all filtered)
- Fallback paths (learner down, GitHub down)
- Score edge cases (all same score, very different scores)

**Test cases:**
1. Sev1 incident, 3 on-call candidates → should pick highest fit_score
2. Sev3 incident, all candidates filtered → should relax one constraint
3. Learner down → should use cached profiles
4. GitHub down → should work without GitHub signals

**Why testing matters:**
- **Reliability**: System must work in production
- **Edge cases**: Real incidents are edge cases

#### Hour 32-36: Integration Testing Prep (Everyone)

**What to prepare:**
- Docker Compose setup (all services)
- Seeding script (realistic demo data)
- Demo incident script
- Health check endpoints working
- Correlation IDs flowing through

**Why prep matters:**
- Integration will be chaotic if services aren't ready
- Demo data must be believable

---

### HOUR 36-48: Feature Completion & Edge Cases

#### Hour 36-40: Executor + Explain Polish (Person 4)

**What to polish:**
- Slack message formatting (beautiful, clear)
- Fallback message display in UI
- Optional Slack buttons (if time permits)
- Error handling (Slack API failures)

**Slack message format:**
```
🚨 *Incident: [title]*
Service: `[service]` | Severity: `[severity]`

*Primary:* @[primary] (confidence: [X]%)
*Backup:* @[backup]

*Evidence:*
• [evidence 1]
• [evidence 2]

[Override in UI](link)
```

**Why polish matters:**
- **First impression**: Slack message is what people see first
- **Clarity**: Must be immediately actionable

#### Hour 40-44: Explain Service Completion (Person 4 - continued)

**What to complete:**
- All evidence types implemented
- "Why not next best" logic
- Constraints summary formatting
- Edge cases (no evidence, all same score)

**"Why not next best" logic:**
```python
def why_not_next_best(top1: Candidate, top2: Candidate) -> List[str]:
    reasons = []
    
    if top1.fit_score > top2.fit_score:
        reasons.append(f"Higher fit score ({top1.fit_score:.2f} vs {top2.fit_score:.2f})")
    
    if top1.on_call and not top2.on_call:
        reasons.append("Currently on-call")
    
    if top1.pages_7d < top2.pages_7d:
        reasons.append(f"Lower interruption load ({top1.pages_7d} vs {top2.pages_7d} pages)")
    
    return reasons
```

**Why this matters:**
- **Transparency**: People need to understand why X was chosen over Y
- **Trust**: Shows system is reasoning, not random

#### Hour 44-48: UI Completion (Person 5)

**What to complete:**
- All pages functional
- All API integrations working
- Override flow end-to-end
- Stats display
- Error handling
- Loading states

**Final UI checklist:**
- [ ] Work items list loads and filters
- [ ] Work item detail shows decision + evidence
- [ ] Override modal works (updates learner)
- [ ] Stats display updates after override
- [ ] Audit drawer shows full trace
- [ ] All error states handled
- [ ] Design is clean and opinionated

---

### HOUR 48-60: Integration Phase

#### Hour 48-50: Service Integration Setup

**Person 1:**
- Update docker-compose.yml with all service URLs
- Test all services start correctly
- Verify health checks

**Everyone:**
- Update service URLs in code (from env vars)
- Test service-to-service calls
- Fix any contract mismatches

**Why integration now:**
- Services are complete, time to wire together
- Need to test real data flow

#### Hour 50-54: End-to-End Flow Testing

**Test flow (Learning Loop Critical):**
1. Seed demo data (2-3 services, 8-12 humans)
2. Trigger demo incident
3. Verify decision appears (<2 seconds)
4. Verify executor creates Jira issue with assignee
5. **Complete Jira issue** (mark as Done) → Jira webhook fires
6. **Verify Learner stats update**: fit_score increased, resolves_count increased (visible in UI)
7. Trigger new incident (same service)
8. **Verify decision uses updated fit_score**: Different assignee or higher confidence
9. **Override scenario**: Reassign Jira issue → verify fit_score decreases
10. **Verify next decision learns from override**: Uses updated fit_score

**Why this matters:**
- **Learning loop is THE core MVP feature**
- Must be visible: stats update → decision changes
- If this doesn't work, demo fails

**Person 1:**
- Test decision → explain → executor flow
- Test Jira Simulator → learner/executor flow
- Fix any integration bugs

**Person 2:**
- Test outcome → learner → stats update flow
- Verify stats are visible in UI

**Person 3:**
- Test ingest → decision flow
- Test monitoring → ingest flow
- Fix any integration bugs

**Person 4:**
- Test executor → Jira Simulator flow
- Test explain service integration
- Fix any integration bugs

**Person 5:**
- Test UI → API → UI flow
- Fix any API integration bugs

**Why E2E testing:**
- **Reality check**: Does the system actually work?
- **Demo prep**: Need working flow for judges

#### Hour 54-58: Learning Loop Verification

**Critical test:**
1. Create incident → decision assigns Person A
2. Override → assign Person B
3. Verify Person A's fit_score decreases, Person B's increases
4. Create similar incident
5. Verify decision changes (Person B now preferred, or confidence lower)

**Person 1 + Person 2:**
- Debug learning loop if not working
- Ensure stats updates are visible
- Ensure decision service uses updated stats

**Why this matters:**
- **Core value prop**: Learning loop is the differentiator
- **Demo critical**: Judges need to see this work

#### Hour 58-60: Integration Bug Fixes

**Everyone:**
- Fix any remaining integration issues
- Test edge cases
- Verify all services handle failures gracefully

---

### HOUR 60-72: Demo Prep & Polish

#### Hour 60-64: Demo Script Preparation

**Person 1:**
- Write demo script (step-by-step)
- Prepare demo data (realistic scenarios)
- Test demo flow multiple times
- Prepare backup plans (if Slack fails, etc.)

**Demo script outline:**
1. **Opening (0:00-0:30)**: Problem statement, solution overview
2. **Show monitoring (0:30-0:45)**: Monitoring service running, continuous logs, error appears
3. **Trigger incident (0:45-1:00)**: Error detected → WorkItem created → decision appears
4. **Show decision (1:00-2:00)**: Evidence, constraints, confidence
5. **Show execution (2:00-2:30)**: Jira issue created with assignee
6. **Show knowledge graph (2:30-3:00)**: 
   - Open 3D visualization
   - Show nodes (Humans=blue, WorkItems=red, Services=green)
   - Show edges (resolved, transferred relationships)
   - Click on work item → see similar incidents cluster nearby
   - **Visual proof**: Similar incidents cluster in 3D space
7. **Show learning (3:00-3:30)**: 
   - Complete Jira issue (mark as Done)
   - Show Learner stats update: fit_score increased, resolves_count increased
   - Show knowledge graph update: new RESOLVED edge appears
   - **This is THE differentiator**: System learned from completion
8. **Replay (3:30-4:00)**: 
   - New error → new decision
   - Show updated fit_score affects decision (different assignee or higher confidence)
   - Show in graph: new work item clusters near similar past incidents
   - **System got smarter!**
9. **Override scenario (4:00-4:30)**: 
   - Show override → fit_score decreases → next decision learns from mistake
   - Show TRANSFERRED edge in graph
10. **Audit (4:30-5:00)**: Show full trace
11. **Close (5:00-5:30)**: Value prop, next steps

**Why script matters:**
- **Smooth demo**: Judges see polished flow
- **Time management**: 5 minutes is short, need structure

#### Hour 64-68: UI Final Polish

**Person 5:**
- Final design pass (spacing, typography, colors)
- Ensure all text is clear and unambiguous
- Add tooltips/explaners where needed
- Test on different screen sizes
- Ensure loading/error states are polished

**Design checklist:**
- [ ] All text is opinionated (no ambiguity)
- [ ] All actions have clear purpose
- [ ] Evidence is readable and contextual
- [ ] Constraints are clear (pass/fail)
- [ ] Audit trace is navigable
- [ ] Override flow is obvious

#### Hour 68-70: Demo Rehearsal

**Everyone:**
- Run through demo script 2-3 times
- Time each section
- Identify any issues
- Prepare Q&A answers

**Q&A prep:**
- "How does it learn?" → Show stats update, replay decision
- "What if it's wrong?" → Show override, explain learning
- "Why not just use Jira?" → We decide who Jira assigns, based on evidence and outcomes
- "Is this politically sensitive?" → No global rankings, contextual only

#### Hour 70-72: Final Bug Fixes & Backup Plans

**Person 1:**
- Final integration test
- Prepare backup demo (if Slack fails, show DB logs)
- Document any known issues

**Everyone:**
- Final code review
- Ensure all services are production-ready (for demo)
- Test failure scenarios

**Backup plans:**
- Slack down → Show executor DB logs in UI
- GitHub down → System works without GitHub signals
- Learner down → Use cached profiles
- Any service down → Show health check status

---

## Local Development Setup

### Prerequisites
- Docker & Docker Compose installed
- Python 3.11+ (for services)
- Node.js 18+ (for UI)
- Git

### One-Command Setup
```bash
# Clone repo
git clone <repo-url>
cd goliath

# Run setup script (creates .env, starts all services)
./scripts/setup.sh

# Or manually:
docker-compose up -d
```

### Service Ports
- **Ingest**: http://localhost:8001
- **Decision**: http://localhost:8002
- **Learner**: http://localhost:8003
- **Executor**: http://localhost:8004
- **Explain**: http://localhost:8005
- **Monitoring**: http://localhost:8006
- **Jira Simulator**: http://localhost:8080
- **UI**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Weaviate**: http://localhost:8081

### Independent Testing

**Each developer can test their service without others:**

```bash
# Person 1 (Ingest/Decision/Monitoring)
cd services/ingest
docker-compose -f docker-compose.test.yml up  # Only ingest + dependencies
./scripts/test_standalone.sh

# Person 2 (Learner/Jira Simulator)
cd services/learner
docker-compose -f docker-compose.test.yml up  # Only learner + Jira Simulator + PostgreSQL
./scripts/test_standalone.sh

# Person 3 (Executor)
cd services/executor
docker-compose -f docker-compose.test.yml up  # Only executor + Jira Simulator
./scripts/test_standalone.sh

# Person 4 (Explain)
cd services/explain
./scripts/test_standalone.sh  # No dependencies, just LLM API

# Person 5 (UI)
cd apps/ui
npm run dev  # Runs standalone, can mock API responses
```

**Mock Data for Testing:**
- Each service includes `scripts/mock_data.json` for standalone testing
- Jira Simulator seeds automatically on startup (200 people, 5000+ tickets)
- PostgreSQL seeds knowledge graph on first run

### Docker Compose Structure

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: goliath
      POSTGRES_USER: goliath
      POSTGRES_PASSWORD: goliath
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8081:8080"
    environment:
      PERSISTENCE_DATA_PATH: /var/lib/weaviate
    volumes:
      - weaviate_data:/var/lib/weaviate
  
  jira-simulator:
    build: ./services/jira-simulator
    ports:
      - "8080:8080"
    environment:
      POSTGRES_URL: postgresql://goliath:goliath@postgres:5432/goliath
    depends_on:
      - postgres
  
  ingest:
    build: ./services/ingest
    ports:
      - "8001:8000"
    environment:
      POSTGRES_URL: postgresql://goliath:goliath@postgres:5432/goliath
      WEAVIATE_URL: http://weaviate:8080
    depends_on:
      - postgres
      - weaviate
  
  # ... other services
```

### README Structure

Each service has its own README:
- `/services/ingest/README.md` - How to run, test, develop
- `/services/decision/README.md` - How to run, test, develop
- etc.

Main README (`/README.md`) includes:
- Quick start
- Architecture overview
- Service ports
- Independent testing guide
- Docker setup
- Troubleshooting

---

## Success Criteria

### Must Have (Demo Fails Without These):
1. ✅ Decision appears <2 seconds after incident ingest
2. ✅ Evidence-first explanation is shown (5-7 bullets)
3. ✅ **Learning loop works**: Jira issue assigned/completed → Learner updates fit_score → visible in stats
4. ✅ **Next decision uses updated fit_score**: Replay or new incident shows different decision/confidence
5. ✅ Override works and produces visible learning update
6. ✅ Audit trace is inspectable and coherent

**Critical: Learning Loop Must Be Visible**
- When Jira issue is completed → fit_score must increase (visible in UI stats)
- When reassigned → fit_score must decrease (visible in UI stats)
- Next decision must use updated fit_score (different assignee or confidence)
- **This is THE core differentiator - if this doesn't work, demo fails**

### Should Have (Nice to Have):
- Slack integration working (for notifications)
- Beautiful UI design
- Smooth demo flow

### Jira Integration Requirements (for Learner + Executor):
- **Jira Cloud instance** (or Jira Server with API access)
- **API Token**: Jira API token for authentication
- **Configuration**:
  - `JIRA_BASE_URL`: e.g., "https://yourcompany.atlassian.net"
  - `JIRA_API_TOKEN`: API token for authentication
  - `JIRA_PROJECT_TO_SERVICE_MAP`: JSON mapping Jira projects to services (for Learner)
  - `SERVICE_TO_JIRA_PROJECT_MAP`: Reverse mapping (for Executor)
  - `JIRA_PRIORITY_TO_SEVERITY_MAP`: Map Jira priorities to sev1/sev2/sev3/sev4
- **Webhook (optional)**: Jira webhook configured to `POST /webhooks/jira` (only if ingesting unassigned issues)

### Won't Have (Out of Scope):
- **Real monitoring/observability integrations** (ServiceNow, Datadog, PagerDuty, New Relic webhooks)
  - **Why?** OAuth setup, webhook configuration, API keys, rate limits - too much scope for MVP
  - **Demo**: Monitoring service simulates what these systems would do (continuous logging + error detection)
  - **Production**: Same normalization logic, just different webhook sources
- OWL 2 / ELK reasoner (hardcoded constraints)
- Multiple Jira instance support (single instance only)

### Knowledge Graph & Vector Architecture (Production-Grade):

**Backend:**
- **Weaviate**: Vector database stores embeddings for similarity search
  - WorkItem embeddings (768D from all-mpnet-base-v2)
  - Human capability embeddings (aggregated from resolved work items)
  - Service/component embeddings
- **PostgreSQL**: Stores knowledge graph relationships
  - Nodes: Humans, WorkItems, Services, Decisions, Outcomes
  - Edges: RESOLVED(h, w, t), TRANSFERRED(w, from, to, t), TOUCHED(h, component, t), ONCALL(h, schedule, t), CO_WORKED(h1, h2, w, t)
  - All edges timestamped for temporal queries
- **Embeddings**: sentence-transformers with `all-mpnet-base-v2` model (768 dimensions)
- **3D Reduction**: PCA (Principal Component Analysis) from sklearn reduces 768D embeddings to 3D coordinates for visualization

**Frontend Visualization:**
- **Library**: react-force-graph-3d for interactive 3D knowledge graph
- **Visualization Type**: Force-directed graph with nodes and edges
- **Color Coding**:
  - Humans: Blue (#3b82f6)
  - WorkItems: Red (#ef4444)
  - Services: Green (#10b981)
  - Decisions: Purple (#8b5cf6)
  - Outcomes: Amber (#f59e0b)
- **Features**:
  - Interactive 3D space (drag to rotate, scroll to zoom)
  - Search and filter by node type
  - Click nodes to view details
  - Auto-zoom to fit all visible nodes
  - Legend showing node type counts
  - Edge visualization shows relationships (resolved, transferred, co-worked)
  - Temporal filtering (show graph at specific time)

**Why Knowledge Graph:**
- **Relationships matter**: Who resolved what, when, with whom
- **Temporal awareness**: Expertise decays, relationships change over time
- **Visual understanding**: 3D graph shows patterns humans can't see in tables
- **Production-grade**: Scales to millions of nodes/edges
- **Query flexibility**: Graph queries find complex patterns (e.g., "who worked with X on similar incidents?")

### LLM Usage:
- **Log preprocessing**: Clean and normalize raw logs before processing
- **Entity extraction**: Incident descriptions → structured entities (service components, error types)
- **Evidence generation**: LLM generates contextual evidence bullets (not templates)
- **Scoring explanations**: LLM explains why candidate was chosen (not hardcoded rules)
- **Key principle**: Temperature=0 for deterministic outputs, all LLM responses stored in audit trail
- **Note**: Similar incident matching uses vector embeddings (not LLM) for production-grade performance

---

## Guardrails (Non-Negotiable)

1. **No global rankings**: Every output is scoped to a specific work item
2. **No expert search**: No "find experts" feature
3. **No free-form natural language**: All evidence is structured
4. **Decisions are contextual, reversible, and auditable**: Core principle

---

## Demo Day Checklist

### Before Demo:
- [ ] All services running in docker-compose
- [ ] PostgreSQL running (knowledge graph storage)
- [ ] Weaviate running (vector database)
- [ ] Demo data seeded (with embeddings and 3D coordinates)
- [ ] Monitoring service running (continuously logging, errors will trigger incidents)
- [ ] Demo endpoint working (`POST /ingest/demo`) - for manual triggers if needed
- [ ] **LLM API configured** (OpenAI or Anthropic API key, model selected)
- [ ] **Embedding model loaded** (sentence-transformers, all-mpnet-base-v2)
- [ ] **Vector database populated** (Weaviate with work item embeddings)
- [ ] **Knowledge graph populated** (PostgreSQL with nodes and edges)
- [ ] **3D visualization working** (react-force-graph-3d rendering graph)
- [ ] Jira API configured (base URL, token, project mappings) - for Learner + Executor
- [ ] Jira webhook configured (optional, only if ingesting unassigned issues)
- [ ] Slack configured (optional, for notifications)
- [ ] UI accessible
- [ ] Demo script rehearsed
- [ ] Backup plans ready (including LLM API fallback if needed)

### During Demo:
- [ ] Follow script (don't wing it)
- [ ] Show learning loop (critical differentiator)
- [ ] Show audit trace (trust builder)
- [ ] Handle questions confidently

### After Demo:
- [ ] Answer Q&A
- [ ] Show code if asked
- [ ] Explain architecture if asked

---

## Key Principles

1. **Isolation until Hour 48**: No overlapping work
2. **Contracts are sacred**: Don't break them
3. **Evidence-first**: Everything must be explainable
4. **Reversibility**: Every decision can be overridden
5. **Auditability**: Every decision can be replayed
6. **Opinionated design**: No ambiguity, no questions

---

## Why This Plan Works

1. **Clear separation**: Each person owns a service, no conflicts
2. **Progressive complexity**: Start simple, add features
3. **Integration late**: Services are complete before wiring
4. **Demo-focused**: Everything serves the demo
5. **Realistic timeline**: 72 hours is tight but doable with coding agents

---

## Final Notes

- **Coding agents**: Use them liberally. They can scaffold, implement algorithms, write tests.
- **Don't overthink**: MVP is about proving the concept, not perfection.
- **Demo is everything**: If it doesn't work in demo, it doesn't matter.
- **Learning loop is critical**: This is the differentiator. Make sure it works.

Good luck. Build something that matters.

