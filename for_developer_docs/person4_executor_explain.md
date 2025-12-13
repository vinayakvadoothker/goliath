# Person 4: Executor Service + Explain Service

## Your Role

You own two simpler services that support the decision engine:

1. **Executor Service** - Executes decisions by creating Jira issues with assigned assignees
2. **Explain Service** - Generates contextual evidence bullets explaining why a decision was made

**Why you?** Both are simpler services (Executor just creates Jira issues, Explain just LLM calls). Together they're a reasonable workload.

---

## What You're Building

### 1. Executor Service (`/services/executor/`)

**The Hands** - Executes decisions by creating Jira issues:
- Takes Decision object
- Creates Jira issue with assigned assignee
- Links back to WorkItem
- Optional: Slack notifications

**Why it exists:**
- **Bounded actions**: Doesn't make decisions, just executes them
- **Jira as execution surface**: Creates the actual ticket with assignee
- **Reversible**: Jira issue can be reassigned (triggers outcome)
- **Safe**: No free-form text, only structured Jira API calls

### 2. Explain Service (`/services/explain/`)

**The Justification** - Generates evidence bullets:
- Takes Decision + candidate features
- Uses LLM to generate contextual evidence (not templates)
- Returns 5-7 evidence bullets, "why not next best" reasons, constraints summary

**Why it exists:**
- **Trust**: People need to know WHY a decision was made
- **Auditability**: Evidence is part of audit trail
- **Reversibility**: "Why not X?" helps people understand overrides

---

## Why You're Doing This

### Executor Service
- **Execution is critical**: Decisions are useless without execution
- **Learning loop connection**: Jira issue creation → completion → outcome → learning
- **Simple but important**: Just creates Jira issues, but it's the execution surface

### Explain Service
- **Trust requires explanation**: People need to know WHY
- **LLM flexibility**: Handles variations in stats, contexts, edge cases
- **No hardcoding**: Works for any combination of stats/constraints

---

## Complete Work Breakdown

### Hour 2-3: Service Scaffolding

**What to create:**
- `/services/executor/` - FastAPI service scaffold
- `/services/explain/` - FastAPI service scaffold
- `/healthz` endpoints to both
- Request logging middleware
- Correlation ID middleware
- PostgreSQL connection (for Executor)
- LLM client setup (for Explain)

**Deliverables:**
- ✅ Both services scaffolded
- ✅ Database connections working

### Hour 8-10: Executor Service

**What to build:**
- `POST /executeDecision` - takes Decision, creates Jira issue with assignee
- Jira API integration (calls Person 1's Jira Simulator)
- Slack integration (optional, behind flag)
- Fallback: store rendered message in DB if Jira fails

**Deliverables:**
- ✅ All endpoints working
- ✅ Jira issue creation working
- ✅ Fallback handling

### Hour 10-12: Explain Service

**What to build:**
- `POST /explainDecision` - takes Decision + candidate features, returns Evidence[]
- LLM-based evidence generation (not templates)
- "Why not next best" logic
- Constraints summary formatting

**Deliverables:**
- ✅ All endpoints working
- ✅ LLM evidence generation working

### Hour 36-40: Executor + Explain Polish

**What to polish:**
- Slack message formatting (beautiful, clear)
- Fallback message display in UI
- Optional Slack buttons (if time permits)
- Error handling (Slack API failures)
- All evidence types implemented
- Edge cases (no evidence, all same score)

**Deliverables:**
- ✅ Both services polished
- ✅ All edge cases handled

---

## Database Schemas

### Executor Service (PostgreSQL)

```sql
CREATE TABLE executed_actions (
  id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL,
  jira_issue_key TEXT, -- e.g., "PROJ-123"
  jira_issue_id TEXT, -- Jira's internal ID
  assigned_human_id TEXT NOT NULL,
  backup_human_ids TEXT, -- JSON array
  created_at TEXT NOT NULL,
  slack_message_id TEXT, -- If Slack notification sent
  fallback_message TEXT -- If Jira failed, store rendered message
);
```

### Explain Service (No Database)

Explain service doesn't need a database - it's stateless (just LLM calls).

---

## API Endpoints

### Executor Service

#### `POST /executeDecision`

**Purpose**: Executes decision by creating Jira issue with assigned assignee.

**Request Body:**
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

**Response (200 OK):**
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

**Processing Flow:**
1. Map WorkItem.service → Jira project (via config: `SERVICE_TO_JIRA_PROJECT_MAP`)
2. Map WorkItem.severity → Jira priority (sev1=Critical, sev2=High, etc.)
3. Map Human.id → Jira accountId (from Learner's human table)
4. Create Jira issue via API (calls Person 1's Jira Simulator)
5. Store Jira issue key in DB
6. Link back to WorkItem (store jira_issue_key in WorkItem table)
7. Optional: Post to Slack channel with Jira link (if enabled)

**Jira Issue Format:**
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

**Error Responses:**
- `400 Bad Request`: Invalid decision_id or missing fields
- `500 Internal Server Error`: Jira API failure (falls back to DB storage)
- `503 Service Unavailable`: Jira API down (stores in DB, shows in UI)

**Fallback**: If Jira API fails, stores rendered message in DB. UI can display it.

**Learning Loop Connection:**
1. Executor creates Jira issue with assignee
2. Human works on issue → completes it in Jira
3. Jira issue status changes to "Done" → Jira webhook fires (optional)
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

### Explain Service

#### `POST /explainDecision`

**Purpose**: Generates contextual evidence bullets explaining why a decision was made.

**Request Body:**
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

**Response (200 OK):**
```typescript
{
  evidence: Array<{
    type: "recent_resolution" | "on_call" | "low_load" | "similar_incident" | "fit_score";
    text: string;          // Contextual, time-bounded explanation
    time_window: string;  // e.g., "last 7 days"
    source: string;       // e.g., "Learner stats", "Vector similarity"
  }>;
  why_not_next_best: Array<string>;  // 1-2 specific reasons
  constraints_summary: Array<string>;  // constraint results
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
        model="gpt-5.2",
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

---

## Implementation Details

### Executor Service - Jira Issue Creation

```python
async def execute_decision(decision_data: dict) -> dict:
    """Execute decision by creating Jira issue."""
    # Get work item
    work_item = await get_work_item(decision_data['work_item_id'])
    
    # Map service → Jira project
    project_key = SERVICE_TO_JIRA_PROJECT_MAP.get(work_item.service, work_item.service.upper())
    
    # Map severity → Jira priority
    priority_map = {
        'sev1': 'Critical',
        'sev2': 'High',
        'sev3': 'Medium',
        'sev4': 'Low'
    }
    priority_name = priority_map.get(work_item.severity, 'Medium')
    
    # Get human's Jira accountId
    human = await get_human(decision_data['primary_human_id'])
    jira_account_id = human.jira_account_id
    
    # Format evidence for description
    evidence_text = "\n".join([f"- {e['text']}" for e in decision_data['evidence']])
    
    # Create Jira issue
    jira_issue = {
        "fields": {
            "project": {"key": project_key},
            "summary": work_item.description[:255],  # Jira summary limit
            "description": f"""Assigned by Goliath

*Primary:* {human.display_name}
*Backup:* {', '.join([get_human(b).display_name for b in decision_data['backup_human_ids']])}

*Evidence:*
{evidence_text}

*Confidence:* {decision_data['confidence']:.0%}""",
            "issuetype": {"name": "Bug"},
            "priority": {"name": priority_name},
            "assignee": {"accountId": jira_account_id}
        }
    }
    
    # Call Jira Simulator (Person 1's service)
    jira_url = os.getenv("JIRA_SIMULATOR_URL", "http://localhost:8080")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{jira_url}/rest/api/3/issue",
                json=jira_issue,
                timeout=10.0
            )
            response.raise_for_status()
            jira_response = response.json()
            
            # Store executed action
            executed_action = ExecutedAction(
                id=generate_id(),
                decision_id=decision_data['decision_id'],
                jira_issue_key=jira_response['key'],
                jira_issue_id=jira_response['id'],
                assigned_human_id=decision_data['primary_human_id'],
                backup_human_ids=json.dumps(decision_data['backup_human_ids']),
                created_at=datetime.now().isoformat()
            )
            db.session.add(executed_action)
            db.session.commit()
            
            # Link back to work item
            work_item.jira_issue_key = jira_response['key']
            db.session.commit()
            
            return {
                "executed_action_id": executed_action.id,
                "jira_issue_key": jira_response['key'],
                "jira_issue_id": jira_response['id'],
                "assigned_human_id": decision_data['primary_human_id'],
                "created_at": executed_action.created_at,
                "message": "Jira issue created successfully"
            }
            
        except Exception as e:
            # Fallback: store rendered message
            executed_action = ExecutedAction(
                id=generate_id(),
                decision_id=decision_data['decision_id'],
                assigned_human_id=decision_data['primary_human_id'],
                backup_human_ids=json.dumps(decision_data['backup_human_ids']),
                created_at=datetime.now().isoformat(),
                fallback_message=format_slack_message(decision_data, work_item)
            )
            db.session.add(executed_action)
            db.session.commit()
            
            raise HTTPException(
                status_code=503,
                detail=f"Jira API unavailable. Message stored in DB: {executed_action.id}"
            )
```

### Explain Service - Evidence Generation

```python
async def explain_decision(explain_data: dict) -> dict:
    """Generate evidence bullets using LLM."""
    work_item = explain_data['work_item']
    decision = explain_data['decision']
    candidates = explain_data['candidate_features']
    top2_margin = explain_data['top2_margin']
    constraints = explain_data['constraint_results']
    
    # Get top candidate
    top1 = candidates[0]
    top2 = candidates[1] if len(candidates) > 1 else None
    
    # Build prompt
    prompt = f"""
Generate evidence bullets explaining why {decision['primary_human_id']} was chosen for this incident.

Incident: {work_item['description']}
Service: {work_item['service']}
Severity: {work_item['severity']}

Primary candidate stats:
- fit_score: {top1['fit_score']:.2f}
- recent_resolves: {top1['recent_resolves']}
- on_call: {top1['on_call']}
- pages_7d: {top1['pages_7d']}
- similar_incidents: {top1.get('similar_incidents', 0)}

Next best candidate stats:
- fit_score: {top2['fit_score']:.2f} (if top2 else 'N/A')
- recent_resolves: {top2['recent_resolves']} (if top2 else 'N/A')
- on_call: {top2['on_call']} (if top2 else 'N/A')

Top2 margin: {top2_margin:.2f}
Confidence: {decision['confidence']:.2f}

Constraints checked: {json.dumps(constraints)}

Return ONLY valid JSON with this structure:
{{
  "evidence": [
    {{
      "type": "recent_resolution" | "on_call" | "low_load" | "similar_incident" | "fit_score",
      "text": "specific, time-bounded explanation",
      "time_window": "last 7 days" | "last 30 days" | etc.,
      "source": "Learner stats" | "Vector similarity" | etc.
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
- why_not_next_best: 1-2 specific reasons (only if top2 exists)
- constraints_summary: all constraints with pass/fail status
- NO global claims ("best engineer") - only contextual ("for this incident")
- NO hallucinations - only use provided stats
- Be specific: "Resolved 3 similar API timeout incidents in last 7 days" not "experienced"
"""
    
    response = openai_client.chat.completions.create(
        model="gpt-5.2",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # Deterministic
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    
    # Validate and format
    return {
        "evidence": result.get("evidence", []),
        "why_not_next_best": result.get("why_not_next_best", []),
        "constraints_summary": result.get("constraints_summary", [])
    }
```

---

## How to Test

### Standalone Testing (Without Other Services)

**1. Create test script: `/services/executor/scripts/test_standalone.sh`**

```bash
#!/bin/bash
# Test Executor service standalone

# Start PostgreSQL and Jira Simulator
docker-compose -f docker-compose.test.yml up -d postgres jira-simulator

# Wait for services to be ready
sleep 5

# Run tests
pytest tests/test_executor_standalone.py

# Cleanup
docker-compose -f docker-compose.test.yml down
```

**2. Create mock data: `/services/executor/scripts/mock_data.json`**

```json
{
  "decisions": [
    {
      "decision_id": "dec_1",
      "work_item_id": "wi_1",
      "primary_human_id": "human_1",
      "backup_human_ids": ["human_2"],
      "confidence": 0.85,
      "evidence": [
        {"type": "recent_resolution", "text": "Resolved 3 similar incidents in last 7 days"}
      ]
    }
  ],
  "work_items": [
    {
      "id": "wi_1",
      "service": "api-service",
      "severity": "sev1",
      "description": "High error rate detected"
    }
  ]
}
```

**3. Test cases:**

```python
# tests/test_executor_standalone.py

def test_create_jira_issue():
    """Executor creates Jira issue with assignee."""
    decision = load_mock_decision("dec_1")
    
    # Mock Jira Simulator
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            "id": "jira_123",
            "key": "PROJ-123"
        }
        
        response = executor_service.execute_decision(decision)
        
        assert response["jira_issue_key"] == "PROJ-123"
        assert mock_post.called

def test_jira_fallback():
    """Executor falls back to DB storage if Jira fails."""
    decision = load_mock_decision("dec_1")
    
    # Mock Jira Simulator failure
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.side_effect = Exception("Jira API down")
        
        with pytest.raises(HTTPException) as exc_info:
            executor_service.execute_decision(decision)
        
        assert exc_info.value.status_code == 503
        
        # Check fallback message stored
        executed_action = get_executed_action(decision['decision_id'])
        assert executed_action.fallback_message is not None
```

### Explain Service Testing

**1. Test evidence generation:**

```python
def test_evidence_generation():
    """Explain service generates evidence bullets."""
    explain_data = {
        "work_item": {
            "id": "wi_1",
            "service": "api-service",
            "severity": "sev1",
            "description": "High error rate detected"
        },
        "decision": {
            "primary_human_id": "human_1",
            "confidence": 0.85
        },
        "candidate_features": [
            {
                "human_id": "human_1",
                "fit_score": 0.9,
                "recent_resolves": 5,
                "on_call": True,
                "pages_7d": 2,
                "similar_incidents": 3
            }
        ],
        "top2_margin": 0.2,
        "constraint_results": [
            {"name": "on_call_required", "passed": True}
        ]
    }
    
    # Mock LLM response
    with patch('openai_client.chat.completions.create') as mock_llm:
        mock_llm.return_value.choices[0].message.content = json.dumps({
            "evidence": [
                {
                    "type": "recent_resolution",
                    "text": "Resolved 5 similar incidents in last 7 days",
                    "time_window": "last 7 days",
                    "source": "Learner stats"
                }
            ],
            "why_not_next_best": ["Higher fit score"],
            "constraints_summary": ["on_call_required: passed"]
        })
        
        response = explain_service.explain_decision(explain_data)
        
        assert len(response["evidence"]) > 0
        assert len(response["why_not_next_best"]) > 0
```

---

## Complete Checklist

### Service Scaffolding (Hour 2-3)
- ✅ Scaffold `/services/executor/` (FastAPI + PostgreSQL)
- ✅ Scaffold `/services/explain/` (FastAPI, no DB)
- ✅ Add `/healthz` endpoints to both
- ✅ Add request logging middleware
- ✅ Add correlation ID middleware
- ✅ Setup PostgreSQL connection (Executor)
- ✅ Setup LLM client (Explain)

### Executor Service (Hour 8-10)
- ✅ Implement `POST /executeDecision` endpoint
- ✅ Implement Jira API integration (calls Person 1's Jira Simulator)
- ✅ Implement service → project mapping
- ✅ Implement severity → priority mapping
- ✅ Implement human → Jira accountId mapping
- ✅ Implement fallback (DB storage if Jira fails)
- [ ] Implement optional Slack integration (optional, not critical)
- ✅ Create database schema
- ✅ Write tests (8/8 tests passing)

### Explain Service (Hour 10-12)
- ✅ Implement `POST /explainDecision` endpoint
- ✅ Implement LLM evidence generation
- ✅ Implement "why not next best" logic
- ✅ Implement constraints summary formatting
- ✅ Handle edge cases (no evidence, all same score)
- ✅ Write tests (9/9 tests passing)

### Polish (Hour 36-40)
- [ ] Polish Slack message formatting (optional, Slack not implemented)
- ✅ Polish fallback message display
- [ ] Implement optional Slack buttons (optional, Slack not implemented)
- ✅ Improve error handling
- ✅ Test all edge cases (all tests passing: Executor 8/8, Explain 9/9)

### Documentation
- ✅ Create `/services/executor/README.md`
- ✅ Create `/services/explain/README.md`
- ✅ Create `/scripts/test_standalone.sh` for Executor
- ✅ Create `/scripts/test_standalone.sh` for Explain
- [ ] Create mock data files
- ✅ Document all API endpoints
- ✅ Document LLM prompt patterns

---

## Key Principles

1. **Bounded actions**: Executor only creates Jira issues (no free-form text)
2. **LLM flexibility**: Explain uses LLM for contextual evidence (not templates)
3. **Deterministic**: Same input → same output (temperature=0)
4. **Fallback handling**: Graceful degradation if Jira/Slack fails
5. **No hardcoding**: LLM handles variations, works for any stats/constraints

---

## Dependencies

### Executor Service
- **Jira Simulator** (Person 1): `POST /rest/api/3/issue` (for creating issues)
- **PostgreSQL**: Executed actions storage
- **Slack API** (optional): For notifications

### Explain Service
- **LLM API**: OpenAI or Anthropic (for evidence generation)
- **No other dependencies**: Stateless service

---

## Environment Variables

```bash
# Executor Service
EXECUTOR_SERVICE_PORT=8004
JIRA_SIMULATOR_URL=http://localhost:8080
POSTGRES_URL=postgresql://goliath:goliath@postgres:5432/goliath
SLACK_WEBHOOK_URL=https://hooks.slack.com/... (optional)
SLACK_ENABLED=false

# Explain Service
EXPLAIN_SERVICE_PORT=8005
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
```

---

## Success Criteria

### Executor Service
- ✅ Can create Jira issue with assigned assignee
- ✅ Jira issue key stored and linked to WorkItem
- ✅ Falls back gracefully if Jira API fails (store in DB, show in UI)
- ✅ Optional Slack notification works (if enabled)

### Explain Service
- ✅ Returns 5-7 evidence bullets (all factual, time-bounded)
- ✅ Returns 1-2 "why not next best" reasons
- ✅ Returns constraints summary
- ✅ No global claims, all contextual
- ✅ Deterministic (same input → same output)

---

## Why This Matters

**Executor Service:**
- **Execution is critical**: Decisions are useless without execution
- **Learning loop connection**: Jira issue creation → completion → outcome → learning
- **Simple but important**: Just creates Jira issues, but it's the execution surface

**Explain Service:**
- **Trust requires explanation**: People need to know WHY
- **LLM flexibility**: Handles variations in stats, contexts, edge cases
- **No hardcoding**: Works for any combination of stats/constraints

Good luck. Build the execution and explanation layer.

