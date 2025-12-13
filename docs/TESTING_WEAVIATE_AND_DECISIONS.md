# Testing Weaviate Storage and Live Decision Making

## Quick Start

After running `make seed` to create initial data, test the full pipeline:

```bash
# Make sure all services are running
make start

# Run the comprehensive test
make test-weaviate
```

Or run directly:
```bash
./scripts/test_weaviate_and_decisions.sh
```

---

## What This Test Does

### 1. **Service Health Check**
- Verifies all services are running (Ingest, Decision, Executor, Learner, Weaviate, Jira)

### 2. **Check Existing WorkItems**
- Verifies WorkItems from `make seed` exist in the database
- Uses these for testing decisions with real data

### 3. **Weaviate Storage Verification**
- Checks if WorkItems are stored in Weaviate
- Weaviate is used for vector similarity search during decision making

### 4. **Create New WorkItem**
- Creates a new WorkItem via Ingest Service
- This tests:
  - LLM preprocessing
  - Embedding generation
  - PostgreSQL storage
  - **Weaviate storage** (for vector similarity)

### 5. **Live Decision Making**
- Makes a decision for the new WorkItem
- This tests:
  - Decision Service retrieves WorkItem
  - Generates embedding
  - **Searches Weaviate for similar incidents**
  - Calls Learner Service for candidates
  - Applies constraints and scores candidates
  - Selects primary + backup assignees

### 6. **Execute Decision**
- Creates Jira issue via Executor Service
- This tests:
  - Executor receives decision
  - Maps service → Jira project
  - Maps human → Jira accountId
  - Creates Jira issue with assignee
  - Links back to WorkItem

### 7. **Verify Jira Issue**
- Confirms Jira issue was created
- Verifies assignee is correct

### 8. **Test with Seeded Data**
- Makes decision for existing WorkItem from seed
- Tests full pipeline with real historical data

---

## Expected Output

```
🧪 Testing Weaviate Storage and Live Decision Making
====================================================

📡 Step 1: Checking Service Health
✅ Ingest is healthy
✅ Decision is healthy
✅ Executor is healthy
✅ Learner is healthy
✅ Weaviate is healthy
✅ Jira is healthy

Test: Check WorkItems from seed exist
✅ PASSED
Found 150 WorkItems in database
Using WorkItem: wi-abc123def456

Test: Verify WorkItem is stored in Weaviate
✅ PASSED
✅ Weaviate WorkItem collection exists and has data

Test: Create new WorkItem via Ingest (tests Weaviate storage)
✅ PASSED
✅ Created new WorkItem: wi-xyz789
✅ WorkItem confirmed in PostgreSQL database

Test: Make decision for new WorkItem
✅ PASSED
✅ Decision made successfully!
   Decision ID: dec-123
   Primary Human: human-456
   Confidence: 0.85

Test: Execute decision (create Jira issue)
✅ PASSED
✅ Jira issue created successfully!
   Jira Issue Key: API-123
   Assigned to: human-456

Test: Verify Jira issue exists
✅ PASSED
✅ Jira issue verified!

Test: Test decision with existing WorkItem from seed
✅ PASSED
✅ Decision made for seeded WorkItem!

📊 Test Summary
✅ Passed: 7
❌ Failed: 0

🎉 All tests passed!
✅ Weaviate Framework: Working
✅ Live Decision Making: Working
✅ Full Pipeline: Working
```

---

## Manual Testing Steps

If you want to test manually:

### 1. Check Weaviate Storage

```bash
# Check Weaviate is running
curl http://localhost:8081/v1/.well-known/ready

# Query WorkItems in Weaviate (if accessible)
curl http://localhost:8081/v1/objects?class=WorkItem&limit=5
```

### 2. Create WorkItem and Verify Storage

```bash
# Create WorkItem
curl -X POST http://localhost:8001/ingest/demo \
  -H "Content-Type: application/json" \
  -d '{
    "service": "api-service",
    "severity": "sev2",
    "description": "High error rate detected: 500 errors/sec",
    "type": "incident",
    "raw_log": "[ERROR] High error rate detected"
  }'

# Note the work_item_id from response
# Verify in database
curl http://localhost:8001/work-items/WORK_ITEM_ID
```

### 3. Make Decision

```bash
# Make decision
curl -X POST http://localhost:8002/decide \
  -H "Content-Type: application/json" \
  -d '{"work_item_id": "WORK_ITEM_ID"}'

# Note the decision_id and primary_human_id from response
```

### 4. Execute Decision

```bash
# Execute decision (create Jira issue)
curl -X POST http://localhost:8004/executeDecision \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "DECISION_ID",
    "work_item_id": "WORK_ITEM_ID",
    "primary_human_id": "PRIMARY_HUMAN_ID",
    "backup_human_ids": [],
    "evidence": [{
      "type": "recent_resolution",
      "text": "Resolved 3 similar incidents",
      "time_window": "last 7 days",
      "source": "Learner stats"
    }],
    "work_item": {
      "service": "api-service",
      "severity": "sev2",
      "description": "High error rate detected: 500 errors/sec"
    }
  }'

# Note the jira_issue_key from response
```

### 5. Verify Jira Issue

```bash
# Check Jira issue (if using Jira Simulator)
curl http://localhost:8080/rest/api/3/issue/JIRA_ISSUE_KEY

# Or check in real Jira dashboard
```

---

## Troubleshooting

### Issue: "No WorkItems found"

**Solution:**
```bash
# Run seed to create WorkItems
make seed
```

### Issue: "Weaviate not accessible"

**Solution:**
```bash
# Check Weaviate is running
docker ps | grep weaviate

# Check logs
docker logs goliath-weaviate

# Restart if needed
docker restart goliath-weaviate
```

### Issue: "Decision failed - No candidates found"

**Solution:**
```bash
# Check Learner Service is running
curl http://localhost:8003/healthz

# Check if humans exist in database
docker exec -it goliath-postgres psql -U goliath -d goliath -c "SELECT COUNT(*) FROM humans;"

# If no humans, run seed
make seed
```

### Issue: "Jira issue creation failed"

**Solution:**
```bash
# Check Jira Simulator is running
curl http://localhost:8080/healthz

# Or check real Jira credentials in .env
cat .env | grep JIRA

# Verify credentials are correct
```

### Issue: "Weaviate collection doesn't exist"

**Solution:**
- This is OK - Weaviate collections are created automatically when WorkItems are stored
- The test will verify this works by creating a new WorkItem
- If it fails, check Ingest Service logs: `make logs SERVICE=ingest`

---

## What Success Looks Like

✅ **Weaviate Framework Working:**
- WorkItems are stored in Weaviate when created via Ingest
- Decision Service can search Weaviate for similar incidents
- Vector similarity search returns relevant results

✅ **Live Decision Making Working:**
- Decision Service makes decisions for new WorkItems
- Decisions use Weaviate for similarity search
- Decisions use Learner Service for candidate profiles
- Decisions select appropriate assignees based on fit_score

✅ **Full Pipeline Working:**
- WorkItem → Ingest → PostgreSQL + Weaviate
- WorkItem → Decision → Candidate selection
- Decision → Executor → Jira issue creation
- Jira issue → Assigned to selected candidate

---

## Next Steps

After verifying everything works:

1. **Monitor the system:**
   ```bash
   make logs SERVICE=monitoring
   ```

2. **Watch decisions being made:**
   ```bash
   make logs SERVICE=decision
   ```

3. **Check Jira issues being created:**
   ```bash
   make logs SERVICE=executor
   ```

4. **View WorkItems:**
   ```bash
   curl http://localhost:8001/work-items | jq
   ```

The system is now ready for production use! 🎉

