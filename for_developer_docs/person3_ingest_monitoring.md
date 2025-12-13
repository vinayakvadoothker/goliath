# Person 3: Ingest Service + Monitoring Service

## Your Role

You own two services that handle **work item ingestion**:

1. **Ingest Service** - Single source of truth for all work items (normalizes from multiple sources)
2. **Monitoring Service** - Simulates monitoring/observability systems (continuously logs, detects errors, creates incidents)

**Why you?** Both services handle work item ingestion - one from monitoring systems, one from manual/demo. Natural pairing.

---

## What You're Building

### 1. Ingest Service (`/services/ingest/`)

**The Single Source of Truth** - All work items flow through here, regardless of source:
- Demo endpoint (simulates ServiceNow/Datadog/PagerDuty)
- Jira webhook (optional, for unassigned issues)
- Manual creation (from UI)
- Future: ServiceNow, Datadog, PagerDuty webhooks

**Why it exists:**
- **Normalization**: Different sources have different formats. Ingest creates canonical WorkItem.
- **Outcome collection**: When humans override/resolve, outcomes flow back here first, then to Learner.
- **Single source of truth**: All work items stored here, regardless of origin

### 2. Monitoring Service (`/services/monitoring/`)

**The Error Generator** - Simulates real monitoring/observability systems:
- Continuously logs (INFO, WARN, DEBUG)
- Periodically logs errors (ERROR, CRITICAL)
- When error detected → calls Ingest to create WorkItem
- Configurable: service name, error frequency, log rate

**Why it exists:**
- **Realistic simulation**: Simulates what ServiceNow/Datadog/PagerDuty would do
- **Continuous operation**: Runs in background, creates incidents automatically
- **Demo-friendly**: No manual triggering needed, errors appear naturally
- **Production-ready pattern**: Same pattern would work with real monitoring systems

---

## Why You're Doing This

### Ingest Service
- **Normalization is critical**: Different sources (ServiceNow, Datadog, Jira, manual) have different formats
- **Outcome collection**: This is where the learning loop starts (outcomes → Learner)
- **Single source of truth**: All work items stored here, Decision service reads from here

### Monitoring Service
- **Realistic demo**: Errors appear naturally, not manually triggered
- **Pattern variety**: Different error types test different routing scenarios
- **Production pattern**: Same logic would work with real monitoring systems

---

## Complete Work Breakdown

### Hour 2-3: Service Scaffolding

**What to create:**
- `/services/ingest/` - FastAPI service scaffold
- `/services/monitoring/` - FastAPI service scaffold
- `/healthz` endpoints to both
- Request logging middleware
- Correlation ID middleware (`x-correlation-id`)
- PostgreSQL connection (for Ingest)
- LLM client setup (for log preprocessing in Monitoring)

**Deliverables:**
- ✅ Both services scaffolded
- ✅ Database connections working

### Hour 4-5: Monitoring Service

**What to build:**
- Background service that continuously logs for a service
- Periodically logs errors (ERROR, CRITICAL level)
- When error detected → calls Ingest `POST /ingest/demo` to create WorkItem
- LLM preprocessing of error logs (clean, normalize)
- Configurable: service name, error frequency, log rate

**Deliverables:**
- ✅ Monitoring loop working
- ✅ Error detection working
- ✅ LLM preprocessing working
- ✅ WorkItem creation via Ingest

### Hour 5-6: Ingest Service

**What to build:**
- `POST /ingest/demo` - creates demo WorkItem (PRIMARY SOURCE FOR MVP)
- `POST /webhooks/jira` - accepts Jira webhook (optional)
- `POST /work-items` - manual work item creation (from UI)
- `GET /work-items` - list all work items
- `GET /work-items/:id` - get single work item
- `POST /work-items/:id/outcome` - record outcome, forward to learner

**Deliverables:**
- ✅ All endpoints working
- ✅ Outcome forwarding to Learner
- ✅ Database schema complete

### Hour 16-18: Monitoring Service Completion

**What to complete:**
- Error detection logic (different error types, severities)
- WorkItem creation with realistic data
- Configurable error patterns (burst errors, gradual degradation, etc.)
- Log aggregation (count errors, track patterns)
- Integration with Ingest service

**Deliverables:**
- ✅ Multiple error types simulated
- ✅ Different severities based on error pattern
- ✅ Monitoring loop runs continuously

---

## Database Schemas

### Ingest Service (PostgreSQL)

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
  raw_payload TEXT, -- store original webhook
  story_points INTEGER, -- For capacity matching
  impact TEXT -- "high" | "medium" | "low"
);

-- Outcomes table
CREATE TABLE outcomes (
  id TEXT PRIMARY KEY,
  work_item_id TEXT NOT NULL,
  event_id TEXT UNIQUE NOT NULL, -- for dedupe
  type TEXT NOT NULL,
  decision_id TEXT,
  actor_id TEXT,
  service TEXT NOT NULL, -- Added for Learner processing
  timestamp TEXT NOT NULL,
  new_assignee_id TEXT, -- If reassigned
  FOREIGN KEY (work_item_id) REFERENCES work_items(id)
);
```

### Monitoring Service (No Database)

Monitoring service doesn't need a database - it just calls Ingest service.

---

## API Endpoints

### Ingest Service

#### `POST /ingest/demo`

**Purpose**: Creates a demo WorkItem to simulate monitoring/observability systems. **PRIMARY SOURCE FOR MVP.**

**Request Body:**
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

**Response (201 Created):**
```typescript
{
  work_item_id: string;
  created_at: string;     // ISO 8601 timestamp
  message: "WorkItem created successfully"
}
```

**Processing Flow:**
1. LLM preprocesses `description` (clean, normalize, extract key info)
2. Creates WorkItem with cleaned description
3. Stores both `raw_log` (original) and `description` (cleaned) in DB
4. Generates embedding for work item (for vector similarity)
5. Stores in Weaviate (for vector search)
6. Stores in PostgreSQL (for knowledge graph)
7. Triggers Decision service automatically (or Decision service polls)

**Error Responses:**
- `400 Bad Request`: Invalid input (missing required fields, invalid severity)
- `500 Internal Server Error`: Database error, LLM preprocessing failure

**Example:**
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

#### `POST /webhooks/jira`

**Purpose**: Receives Jira webhooks when issues are created/updated. Optional - only processes unassigned issues.

**Request Body (Jira webhook format):**
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

**Response (200 OK):**
```typescript
{
  processed: boolean;
  work_item_id?: string;  // Only if issue was unassigned and processed
  message: string;
}
```

**Processing Logic:**
- Only processes if `issue.fields.assignee` is null (unassigned)
- Maps Jira priority → severity (Critical=sev1, High=sev2, etc.)
- Maps Jira project → service (via `JIRA_PROJECT_TO_SERVICE_MAP` config)
- LLM preprocesses description before creating WorkItem
- Store `issue.key` in `origin_system` field (e.g., "JIRA-123")

**Error Responses:**
- `400 Bad Request`: Invalid webhook format
- `200 OK` with `processed: false`: Issue already assigned, skipped

#### `POST /work-items`

**Purpose**: Manual work item creation from UI.

**Request Body:**
```typescript
{
  service: string;
  severity: "sev1" | "sev2" | "sev3" | "sev4";
  description: string;
  type?: "incident" | "ticket" | "alert";
  creator_id?: string;
}
```

**Response (201 Created):**
```typescript
{
  work_item_id: string;
  created_at: string;
  message: "WorkItem created successfully"
}
```

#### `GET /work-items`

**Purpose**: List all work items. Used by UI to display work items table.

**Query Parameters:**
```typescript
{
  service?: string;       // Filter by service
  severity?: "sev1" | "sev2" | "sev3" | "sev4";  // Filter by severity
  status?: "open" | "assigned" | "resolved";     // Filter by status
  limit?: number;         // Default: 50, max: 100
  offset?: number;        // For pagination
}
```

**Response (200 OK):**
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

#### `GET /work-items/:id`

**Purpose**: Get single work item by ID.

**Response (200 OK):**
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
  story_points?: number;
  impact?: "high" | "medium" | "low";
}
```

#### `POST /work-items/:id/outcome`

**Purpose**: Record outcome (resolved, reassigned, escalated). **Triggers learning loop.**

**Request Body:**
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

**Response (200 OK):**
```typescript
{
  outcome_id: string;
  processed: boolean;
  message: "Outcome recorded and forwarded to Learner"
}
```

**Processing Flow:**
1. Creates outcome record in Ingest DB
2. Forwards to Learner `POST /outcomes` with full outcome data
3. Learner updates fit_score, resolves_count, transfers_count
4. Next decision uses updated stats

**Error Responses:**
- `400 Bad Request`: Invalid outcome type or missing actor_id
- `404 Not Found`: Work item doesn't exist

### Monitoring Service

#### `GET /healthz`

**Purpose**: Health check endpoint.

**Response (200 OK):**
```typescript
{
  status: "healthy";
  service: "monitoring";
  uptime: number;  // seconds
}
```

#### `POST /monitoring/start`

**Purpose**: Start monitoring loop. Optional - can auto-start on service start.

**Request Body (optional):**
```typescript
{
  service_name?: string;  // Override default
  error_probability?: number;  // Override default
  log_interval?: number;  // Override default
}
```

**Response (200 OK):**
```typescript
{
  status: "started";
  service_name: string;
  error_probability: number;
  log_interval: number;
}
```

#### `POST /monitoring/stop`

**Purpose**: Stop monitoring loop.

**Response (200 OK):**
```typescript
{
  status: "stopped";
  message: "Monitoring loop stopped"
}
```

#### `GET /monitoring/status`

**Purpose**: Get current monitoring status.

**Response (200 OK):**
```typescript
{
  status: "running" | "stopped";
  service_name: string;
  error_count: number;  // Total errors detected
  last_error_at?: string;  // ISO 8601
  error_probability: number;
  log_interval: number;
}
```

---

## Implementation Details

### Monitoring Service - Monitoring Loop

```python
# Background task that runs continuously
async def monitoring_loop():
    service_name = os.getenv("MONITORING_SERVICE_NAME", "api-service")
    error_probability = float(os.getenv("MONITORING_ERROR_PROBABILITY", "0.05"))
    log_interval = int(os.getenv("MONITORING_LOG_INTERVAL", "5"))
    ingest_url = os.getenv("MONITORING_INGEST_URL", "http://localhost:8001")
    
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
            
            # Determine severity based on error type
            severity = determine_severity(error_type)
            
            # Create WorkItem via Ingest
            work_item = {
                "service": service_name,
                "severity": severity,
                "description": cleaned_description,  # Use cleaned version
                "raw_log": error_type,  # Store original for audit
                "type": "incident"
            }
            
            # Call Ingest service
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{ingest_url}/ingest/demo",
                        json=work_item,
                        timeout=5.0
                    )
                    response.raise_for_status()
                    print(f"[ERROR] {error_type} - WorkItem created (cleaned: {cleaned_description})")
                except Exception as e:
                    print(f"[ERROR] Failed to create WorkItem: {e}")
        
        await asyncio.sleep(log_interval)

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
        model="gpt-5.2",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # Deterministic
    )
    return response.choices[0].message.content.strip()

def determine_severity(error_type: str) -> str:
    """Determine severity based on error type."""
    sev1_patterns = ["High error rate", "Service degradation", "Memory leak"]
    sev2_patterns = ["Database connection", "API endpoint returning 500"]
    sev3_patterns = ["Timeout", "Connection error"]
    
    if any(pattern in error_type for pattern in sev1_patterns):
        return "sev1"
    elif any(pattern in error_type for pattern in sev2_patterns):
        return "sev2"
    else:
        return "sev3"
```

### Ingest Service - Work Item Creation

```python
async def create_work_item(data: dict) -> WorkItem:
    """Create work item with LLM preprocessing and embedding generation."""
    # LLM preprocess description
    if data.get('raw_log'):
        cleaned_description = await llm_preprocess_log(data['raw_log'], data['service'])
    else:
        cleaned_description = data['description']
    
    # Generate embedding
    embedding = generate_embedding(cleaned_description)  # 768D
    
    # Reduce to 3D for visualization
    embedding_3d = pca_reduce(embedding)  # 768D → 3D
    
    # Create work item
    work_item = WorkItem(
        id=generate_id(),
        type=data.get('type', 'incident'),
        service=data['service'],
        severity=data['severity'],
        description=cleaned_description,
        raw_log=data.get('raw_log'),
        embedding_3d_x=embedding_3d[0],
        embedding_3d_y=embedding_3d[1],
        embedding_3d_z=embedding_3d[2],
        created_at=datetime.now(),
        origin_system=data.get('origin_system', 'demo'),
        creator_id=data.get('creator_id'),
        story_points=data.get('story_points'),
        impact=data.get('impact')
    )
    
    # Store in PostgreSQL
    db.session.add(work_item)
    db.session.commit()
    
    # Store in Weaviate (for vector similarity)
    weaviate_client.data_object.create(
        data_object={
            "id": work_item.id,
            "description": cleaned_description,
            "service": work_item.service,
            "severity": work_item.severity
        },
        class_name="WorkItem",
        vector=embedding.tolist()
    )
    
    return work_item
```

### Ingest Service - Outcome Processing

```python
async def record_outcome(work_item_id: str, outcome_data: dict) -> Outcome:
    """Record outcome and forward to Learner."""
    # Get work item
    work_item = get_work_item(work_item_id)
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # Create outcome
    outcome = Outcome(
        id=generate_id(),
        work_item_id=work_item_id,
        event_id=generate_event_id(),  # Unique for dedupe
        type=outcome_data['type'],
        decision_id=outcome_data.get('decision_id'),
        actor_id=outcome_data['actor_id'],
        service=work_item.service,  # Added for Learner processing
        timestamp=outcome_data.get('timestamp', datetime.now().isoformat()),
        new_assignee_id=outcome_data.get('new_assignee_id')
    )
    
    # Store in DB
    db.session.add(outcome)
    db.session.commit()
    
    # Forward to Learner
    async with httpx.AsyncClient() as client:
        try:
            learner_url = os.getenv("LEARNER_SERVICE_URL", "http://localhost:8003")
            response = await client.post(
                f"{learner_url}/outcomes",
                json={
                    "event_id": outcome.event_id,
                    "decision_id": outcome.decision_id,
                    "work_item_id": outcome.work_item_id,
                    "type": outcome.type,
                    "actor_id": outcome.actor_id,
                    "service": outcome.service,
                    "timestamp": outcome.timestamp,
                    "new_assignee_id": outcome.new_assignee_id
                },
                timeout=5.0
            )
            response.raise_for_status()
        except Exception as e:
            # Log error but don't fail - outcome is recorded
            logger.error(f"Failed to forward outcome to Learner: {e}")
    
    return outcome
```

---

## How to Test

### Standalone Testing (Without Other Services)

**1. Create test script: `/services/ingest/scripts/test_standalone.sh`**

```bash
#!/bin/bash
# Test Ingest service standalone

# Start PostgreSQL
docker-compose -f docker-compose.test.yml up -d postgres

# Wait for service to be ready
sleep 5

# Run tests
pytest tests/test_ingest_standalone.py

# Cleanup
docker-compose -f docker-compose.test.yml down
```

**2. Create mock data: `/services/ingest/scripts/mock_data.json`**

```json
{
  "work_items": [
    {
      "service": "api-service",
      "severity": "sev1",
      "description": "High error rate detected on /api/v1/users endpoint",
      "type": "incident"
    }
  ],
  "outcomes": [
    {
      "work_item_id": "wi_test_1",
      "type": "resolved",
      "actor_id": "human_1"
    }
  ]
}
```

**3. Test cases:**

```python
# tests/test_ingest_standalone.py

def test_create_work_item():
    """Create work item via demo endpoint."""
    response = client.post("/ingest/demo", json={
        "service": "api-service",
        "severity": "sev1",
        "description": "High error rate detected"
    })
    
    assert response.status_code == 201
    assert response.json()["work_item_id"] is not None

def test_list_work_items():
    """List work items with filtering."""
    # Create test work items
    create_test_work_items()
    
    # Filter by service
    response = client.get("/work-items?service=api-service")
    
    assert response.status_code == 200
    assert all(item["service"] == "api-service" for item in response.json()["work_items"])

def test_record_outcome():
    """Record outcome and forward to Learner."""
    work_item = create_test_work_item()
    
    # Mock Learner service
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 200
        
        response = client.post(f"/work-items/{work_item.id}/outcome", json={
            "type": "resolved",
            "actor_id": "human_1"
        })
        
        assert response.status_code == 200
        assert mock_post.called  # Learner was called
```

### Monitoring Service Testing

**1. Test monitoring loop:**

```python
def test_monitoring_loop():
    """Monitoring loop creates work items."""
    # Mock Ingest service
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 201
        
        # Run monitoring loop for a short time
        asyncio.run(run_monitoring_loop(duration=10))
        
        # Check that work items were created
        assert mock_post.called

def test_llm_preprocessing():
    """LLM preprocesses logs correctly."""
    raw_log = "[2024-01-15 10:30:00,123 ERROR] Database connection timeout"
    
    cleaned = await llm_preprocess_log(raw_log, "api-service")
    
    assert "Database connection timeout" in cleaned
    assert "2024-01-15" not in cleaned  # Timestamp removed
```

---

## Complete Checklist

### Service Scaffolding (Hour 2-3)
- [ ] Scaffold `/services/ingest/` (FastAPI + PostgreSQL)
- [x] Scaffold `/services/monitoring/` (FastAPI, background task)
- [x] Add `/healthz` endpoints to both
- [ ] Add request logging middleware
- [ ] Add correlation ID middleware
- [ ] Setup PostgreSQL connection (Ingest)
- [x] Setup LLM client (Monitoring)

### Monitoring Service (Hour 4-5)
- [x] Implement monitoring loop (background task)
- [x] Implement error detection logic
- [x] Implement LLM log preprocessing
- [x] Implement WorkItem creation via Ingest
- [x] Implement `GET /healthz` endpoint
- [x] Implement `POST /monitoring/start` endpoint
- [x] Implement `POST /monitoring/stop` endpoint
- [x] Implement `GET /monitoring/status` endpoint
- [x] Test monitoring loop
- [x] Test error detection

### Ingest Service (Hour 5-6)
- [x] Implement `POST /ingest/demo` endpoint
- [ ] Implement `POST /webhooks/jira` endpoint
- [ ] Implement `POST /work-items` endpoint
- [ ] Implement `GET /work-items` endpoint
- [ ] Implement `GET /work-items/:id` endpoint
- [ ] Implement `POST /work-items/:id/outcome` endpoint
- [ ] Implement LLM preprocessing
- [ ] Implement embedding generation
- [ ] Implement Weaviate storage
- [ ] Implement PostgreSQL storage
- [ ] Implement outcome forwarding to Learner
- [ ] Create database schema
- [ ] Write tests

### Monitoring Service Completion (Hour 16-18)
- [x] Implement multiple error types
- [x] Implement severity determination
- [x] Implement error pattern simulation (burst, gradual, intermittent)
- [x] Test all error patterns
- [x] Test integration with Ingest

### Documentation
- [ ] Create `/services/ingest/README.md`
- [ ] Create `/services/monitoring/README.md`
- [ ] Create `/scripts/test_standalone.sh` for Ingest
- [ ] Create `/scripts/test_standalone.sh` for Monitoring
- [ ] Create mock data files
- [ ] Document all API endpoints
- [ ] Document monitoring loop behavior

---

## Key Principles

1. **Normalization**: All sources → canonical WorkItem
2. **Single source of truth**: All work items stored in Ingest
3. **Outcome collection**: Outcomes flow back here first, then to Learner
4. **Realistic simulation**: Monitoring service simulates real monitoring systems
5. **LLM preprocessing**: Clean and normalize logs before processing

---

## Dependencies

### Ingest Service
- **PostgreSQL**: Work item storage
- **Weaviate**: Vector storage (for similarity search)
- **Learner Service**: `POST /outcomes` (for forwarding outcomes)
- **LLM API**: OpenAI or Anthropic (for log preprocessing)

### Monitoring Service
- **Ingest Service**: `POST /ingest/demo` (for creating work items)
- **LLM API**: OpenAI or Anthropic (for log preprocessing)

---

## Environment Variables

```bash
# Ingest Service
INGEST_SERVICE_PORT=8001
POSTGRES_URL=postgresql://goliath:goliath@postgres:5432/goliath
WEAVIATE_URL=http://weaviate:8080
LEARNER_SERVICE_URL=http://localhost:8003
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2

# Monitoring Service
MONITORING_SERVICE_PORT=8006
MONITORING_SERVICE_NAME=api-service
MONITORING_ERROR_PROBABILITY=0.05
MONITORING_LOG_INTERVAL=5
MONITORING_INGEST_URL=http://localhost:8001
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
```

---

## Success Criteria

### Ingest Service
- ✅ Can create WorkItem via demo endpoint
- ✅ Can list work items with filtering
- ✅ Can record outcome (forwards to learner)
- ✅ All requests logged with correlation ID
- ✅ LLM preprocessing works correctly
- ✅ Embeddings generated and stored

### Monitoring Service
- ✅ Continuously logs (INFO, WARN, DEBUG)
- ✅ Periodically logs errors (ERROR, CRITICAL)
- ✅ Creates WorkItem via Ingest when error detected
- ✅ Configurable service name, error frequency, log rate
- ✅ Can start/stop monitoring loop

---

## Why This Matters

**Ingest Service:**
- **Single source of truth**: All work items flow through here
- **Normalization**: Different sources → canonical format
- **Outcome collection**: Learning loop starts here

**Monitoring Service:**
- **Realistic demo**: Errors appear naturally
- **Pattern variety**: Different error types test routing
- **Production pattern**: Same logic works with real monitoring systems

Good luck. Build the ingestion layer.

