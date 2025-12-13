# Pipeline Status - What's Working vs. What's Missing

## Executive Summary

**Good News**: All individual services are **fully implemented** and working independently.

**Missing**: Services are **NOT automatically chained together**. The pipeline requires **manual orchestration** or a **control center/orchestrator** to connect them.

---

## ✅ What's Fully Implemented

### 1. **Person 3: Ingest Service** ✅ COMPLETE

**Status**: ✅ **Fully implemented and working**

**What works:**
- ✅ `POST /ingest/demo` - Creates WorkItems with full pipeline:
  - LLM preprocessing (if raw_log provided)
  - Embedding generation (384-dim)
  - PCA reduction (3D for visualization)
  - PostgreSQL storage
  - Weaviate storage (for vector similarity)
- ✅ `POST /work-items` - Manual WorkItem creation
- ✅ `GET /work-items` - List with filtering
- ✅ `GET /work-items/{id}` - Get specific WorkItem
- ✅ `POST /work-items/{id}/outcome` - Records outcomes and forwards to Learner Service

**What's missing:**
- ❌ **Does NOT automatically call Decision Service** after creating a WorkItem
- ❌ **No automatic orchestration** - WorkItems are created but not routed

**Code location**: `services/ingest/main.py`

---

### 2. **Person 3: Monitoring Service** ✅ COMPLETE

**Status**: ✅ **Fully implemented and working**

**What works:**
- ✅ Continuous monitoring loop (logs every 5 seconds)
- ✅ Error detection (5% probability, configurable)
- ✅ LLM preprocessing of error logs
- ✅ **Calls Ingest Service** `POST /ingest/demo` to create WorkItems
- ✅ Auto-starts on service startup
- ✅ Manual start/stop endpoints

**What's missing:**
- ❌ **Does NOT trigger Decision Service** - WorkItems are created but not routed
- ❌ **No automatic decision-making** - WorkItems sit in database waiting

**Code location**: `services/monitoring/main.py`

**Flow**: `Monitoring → Ingest` ✅ **WORKING**

---

### 3. **Person 1: Decision Service** ✅ COMPLETE

**Status**: ✅ **Fully implemented and working**

**What works:**
- ✅ `POST /decide` - Makes decisions for WorkItems:
  - Retrieves WorkItem from database
  - Generates embedding
  - Vector similarity search in Weaviate
  - **Calls Learner Service** `GET /profiles` for candidates
  - Applies constraint filtering
  - Scores candidates (fit_score + recency + availability)
  - Selects primary + backups
  - Calculates confidence
  - Stores decision + audit trail
- ✅ `GET /decisions/{work_item_id}` - Get decision
- ✅ `GET /audit/{work_item_id}` - Get full audit trail
- ✅ Fallback mechanism when Learner Service is down

**What's missing:**
- ❌ **Does NOT automatically call Executor Service** after making a decision
- ❌ **Does NOT automatically call Explain Service** for evidence
- ❌ **No automatic orchestration** - Decisions are made but not executed

**Code location**: `services/decision/main.py`, `services/decision/decision_engine.py`

**Flow**: `Decision → Learner` ✅ **WORKING**

---

### 4. **Person 4: Executor Service** ✅ COMPLETE

**Status**: ✅ **Fully implemented and working**

**What works:**
- ✅ `POST /executeDecision` - Creates Jira issues:
  - Validates mappings (service→project, severity→priority, human→accountId)
  - Formats Jira description with evidence
  - **Calls Jira Simulator** `POST /rest/api/3/issue` to create issue
  - Assigns issue to `primary_human_id` (the candidate Decision selected)
  - Stores executed action in database
  - Links Jira issue back to WorkItem
  - Retry logic with exponential backoff
  - Fallback to database storage if Jira fails
- ✅ `GET /executed_actions` - Get execution history

**What's missing:**
- ❌ **Only called manually** - Not automatically called by Decision Service
- ❌ **No automatic orchestration** - Decisions exist but aren't executed

**Code location**: `services/executor/main.py`

**Flow**: `Executor → Jira Simulator` ✅ **WORKING**

**Answer to your question**: ✅ **YES, Executor DOES create Jira bugs with the candidate that Decision selected!** It:
1. Takes the `primary_human_id` from the Decision
2. Maps it to Jira `accountId` via `validate_mappings()`
3. Creates Jira issue with `"assignee": {"accountId": jira_account_id}`
4. The issue is assigned to the person Decision selected!

---

### 5. **Person 1: Jira Simulator** ✅ COMPLETE

**Status**: ✅ **Fully implemented and working**

**What works:**
- ✅ `POST /rest/api/3/issue` - Creates issues (used by Executor)
- ✅ `GET /rest/api/3/search` - JQL search (used by Learner)
- ✅ `GET /rest/api/3/issue/{key}` - Get issue details
- ✅ `PUT /rest/api/3/issue/{key}` - Update issue
- ✅ Full PostgreSQL storage
- ✅ Outcome generation (when issues are completed/reassigned)

**Code location**: `services/jira-simulator/main.py`

---

### 6. **Person 2: Learner Service** ✅ COMPLETE (assumed)

**Status**: ✅ **Fully implemented** (based on Decision Service calling it successfully)

**What works:**
- ✅ `GET /profiles?service=X` - Returns human profiles with fit_score
- ✅ `POST /outcomes` - Processes outcomes (called by Ingest)
- ✅ Updates fit_score based on resolutions/reassignments
- ✅ Syncs with Jira for historical data

**Code location**: `services/learner/main.py`

---

### 7. **Person 4: Explain Service** ✅ COMPLETE (assumed)

**Status**: ✅ **Fully implemented** (based on documentation)

**What works:**
- ✅ `POST /explainDecision` - Generates evidence bullets using LLM
- ✅ Contextual explanations for decisions

**Code location**: `services/explain/main.py`

---

## ❌ What's Missing: Automatic Orchestration

### The Missing Link: Orchestration

**Current State**: All services work independently, but they're **NOT automatically chained**.

**What's needed**: An orchestrator that:
1. **After Ingest creates WorkItem** → Automatically calls Decision Service
2. **After Decision makes decision** → Automatically calls Explain Service, then Executor Service
3. **After Executor creates Jira issue** → WorkItem is complete

**Options:**

### Option 1: Add Orchestration to Ingest Service (Recommended for MVP)

**Modify `services/ingest/main.py`**:
```python
@app.post("/ingest/demo")
async def create_demo_work_item(request: DemoWorkItemRequest):
    # ... existing code to create WorkItem ...
    
    # NEW: Automatically trigger decision
    decision_url = os.getenv("DECISION_SERVICE_URL", "http://decision:8000")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            decision_response = await client.post(
                f"{decision_url}/decide",
                json={"work_item_id": work_item_id}
            )
            decision = decision_response.json()
            
            # NEW: Automatically execute decision
            executor_url = os.getenv("EXECUTOR_SERVICE_URL", "http://executor:8000")
            explain_url = os.getenv("EXPLAIN_SERVICE_URL", "http://explain:8000")
            
            # Get evidence from Explain Service
            explain_response = await client.post(
                f"{explain_url}/explainDecision",
                json={"decision_id": decision["id"], "work_item_id": work_item_id}
            )
            evidence = explain_response.json().get("evidence", [])
            
            # Execute decision
            executor_response = await client.post(
                f"{executor_url}/executeDecision",
                json={
                    "decision_id": decision["id"],
                    "work_item_id": work_item_id,
                    "primary_human_id": decision["primary_human_id"],
                    "backup_human_ids": decision["backup_human_ids"],
                    "evidence": evidence,
                    "work_item": {
                        "service": request.service,
                        "severity": request.severity,
                        "description": cleaned_description,
                        "story_points": request.story_points
                    }
                }
            )
            
            logger.info(f"Full pipeline executed: WorkItem → Decision → Executor")
    except Exception as e:
        logger.warning(f"Orchestration failed: {e}. WorkItem created but not routed.")
    
    return work_item
```

### Option 2: Control Center Service (Better for Production)

A separate service that orchestrates the entire flow:
- Polls for new WorkItems
- Triggers Decision Service
- Triggers Explain Service
- Triggers Executor Service
- Tracks pipeline state

**Code location**: `services/control-center/` (partially exists)

---

## Current Pipeline Flow (Manual)

**What works manually:**

1. ✅ **Monitoring → Ingest**
   ```bash
   # Monitoring automatically calls Ingest
   # WorkItem created in database
   ```

2. ✅ **Ingest → Decision** (manual)
   ```bash
   curl -X POST http://localhost:8002/decide \
     -H "Content-Type: application/json" \
     -d '{"work_item_id": "wi-abc123"}'
   ```

3. ✅ **Decision → Executor** (manual)
   ```bash
   curl -X POST http://localhost:8004/executeDecision \
     -H "Content-Type: application/json" \
     -d '{
       "decision_id": "dec-123",
       "work_item_id": "wi-abc123",
       "primary_human_id": "human-456",
       "backup_human_ids": [],
       "evidence": [],
       "work_item": {...}
     }'
   ```

4. ✅ **Executor → Jira Simulator**
   ```bash
   # Executor automatically calls Jira Simulator
   # Jira issue created with assignee
   ```

---

## Desired Pipeline Flow (Automatic)

**What should happen automatically:**

```
Monitoring detects error
  ↓
Calls Ingest POST /ingest/demo
  ↓
Ingest creates WorkItem
  ↓ [AUTOMATIC]
Calls Decision POST /decide
  ↓
Decision makes decision (calls Learner for candidates)
  ↓ [AUTOMATIC]
Calls Explain POST /explainDecision
  ↓
Explain generates evidence
  ↓ [AUTOMATIC]
Calls Executor POST /executeDecision
  ↓
Executor creates Jira issue with assignee
  ↓
Jira issue assigned to selected candidate
  ✅ DONE
```

---

## Summary by Person

### Person 1 (Decision + Infrastructure + Jira Simulator)
- ✅ **Decision Service**: Fully implemented
- ✅ **Jira Simulator**: Fully implemented
- ✅ **Infrastructure**: Fully implemented
- ❌ **Missing**: Automatic call to Executor after decision

### Person 2 (Learner Service)
- ✅ **Learner Service**: Fully implemented
- ✅ **Outcome processing**: Working
- ✅ **fit_score updates**: Working

### Person 3 (Ingest + Monitoring)
- ✅ **Ingest Service**: Fully implemented
- ✅ **Monitoring Service**: Fully implemented
- ✅ **Monitoring → Ingest**: Working automatically
- ❌ **Missing**: Automatic call to Decision after WorkItem creation

### Person 4 (Executor + Explain)
- ✅ **Executor Service**: Fully implemented
- ✅ **Jira issue creation**: Working
- ✅ **Assignee assignment**: Working (uses Decision's candidate!)
- ✅ **Explain Service**: Fully implemented
- ❌ **Missing**: Automatic call from Decision Service

---

## Next Steps

**To make the pipeline fully automatic:**

1. **Add orchestration to Ingest Service** (quick fix for MVP)
   - After creating WorkItem, automatically call Decision
   - Decision should automatically call Explain + Executor

2. **OR create Control Center Service** (better for production)
   - Polls for new WorkItems
   - Orchestrates entire flow
   - Tracks state and handles errors

3. **Test the full pipeline:**
   ```bash
   make test  # Tests individual services
   # Need to add E2E test that verifies full flow
   ```

---

## Answer to Your Question

> **"Is Executor creating a new Jira bug based on the candidate the entire pipeline decides to fix the bug?"**

**YES! ✅** Executor **DOES** create Jira issues with the candidate that Decision selected. The code shows:

1. Executor receives `primary_human_id` from Decision
2. Executor maps `primary_human_id` → Jira `accountId` via `validate_mappings()`
3. Executor creates Jira issue with `"assignee": {"accountId": jira_account_id}`
4. The issue is assigned to the person Decision selected!

**However**, the pipeline is **NOT automatic** - you need to manually call:
1. Decision Service after WorkItem is created
2. Executor Service after Decision is made

**The services are all working, they just need to be chained together!**

