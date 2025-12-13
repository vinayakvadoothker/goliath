# Testing the Goliath Pipeline

## Quick Start: Running the Entire Pipeline

### 1. Initial Setup (First Time Only)

```bash
# This will:
# - Create .env file
# - Start PostgreSQL and Weaviate
# - Seed Jira Simulator with data
# - Build and start all services
make setup
```

### 2. Start Services (After Setup)

```bash
# Start all services
make start

# Check service health
make health
```

### 3. Test the Entire Pipeline

```bash
# Run comprehensive pipeline test with simulated errors
make test

# Or use the alias
make pipeline
```

**What `make test` does:**
- ✅ Checks all services are healthy
- ✅ Tests Monitoring → Ingest flow (creates WorkItems)
- ✅ Tests Decision Service (if available)
- ✅ Tests multiple error types (sev1, sev2, sev3)
- ✅ Tests WorkItem listing and filtering
- ✅ Tests outcome recording and forwarding to Learner
- ✅ Verifies database storage
- ✅ Provides detailed test report

This is the **recommended way** to test the entire pipeline!

### 3. Verify Services Are Running

```bash
# Check status
make status

# View logs for a specific service
make logs SERVICE=ingest
make logs SERVICE=monitoring
```

---

## How Monitoring Service Works

### Overview

The **Monitoring Service** simulates a real monitoring/observability system (like Datadog, ServiceNow, or PagerDuty). It:

1. **Continuously logs** normal messages every 5 seconds (configurable)
2. **Randomly detects errors** (5% probability per cycle, configurable)
3. **When error detected**:
   - Generates realistic error message
   - Uses LLM to preprocess/clean the error log
   - Calls Ingest Service `POST /ingest/demo` to create WorkItem
   - Logs the incident creation

### Data Flow

```
Monitoring Service
  ↓ (detects error)
  ↓ (LLM preprocesses)
  ↓ POST /ingest/demo
Ingest Service
  ↓ (normalizes, generates embedding)
  ↓ (stores in PostgreSQL + Weaviate)
Decision Service (future)
  ↓ (routes to best human)
Executor Service (future)
  ↓ (creates Jira issue)
```

### Monitoring Service Configuration

Environment variables (in `.env` or `docker-compose.yml`):

```bash
MONITORING_SERVICE_NAME=api-service          # Service being monitored
MONITORING_ERROR_PROBABILITY=0.05          # 5% chance of error per cycle
MONITORING_LOG_INTERVAL=5                   # Seconds between log cycles
MONITORING_INGEST_URL=http://ingest:8000    # Ingest service URL
MONITORING_AUTO_START=true                  # Auto-start on service start
```

### Monitoring Service Endpoints

- `GET http://localhost:8006/healthz` - Health check
- `GET http://localhost:8006/monitoring/status` - Get monitoring status
- `POST http://localhost:8006/monitoring/start` - Start monitoring loop
- `POST http://localhost:8006/monitoring/stop` - Stop monitoring loop

---

## Testing the Pipeline

### Test 1: Verify Monitoring is Running

```bash
# Check monitoring status
curl http://localhost:8006/monitoring/status

# Expected response:
# {
#   "status": "running",
#   "service_name": "api-service",
#   "error_count": 0,
#   "last_error_at": null,
#   "started_at": "2024-01-01T12:00:00",
#   "error_probability": 0.05,
#   "log_interval": 5
# }
```

### Test 2: View Monitoring Logs

```bash
# View real-time logs
make logs SERVICE=monitoring

# Or directly
docker logs goliath-monitoring -f
```

You should see:
- `[INFO]` / `[WARN]` / `[DEBUG]` messages every 5 seconds
- Occasionally `[ERROR]` messages when errors are detected
- `WorkItem created successfully: wi-...` messages when incidents are created

### Test 3: Verify WorkItems Are Created in Ingest

```bash
# List all work items
curl http://localhost:8001/work-items

# Expected response:
# {
#   "work_items": [
#     {
#       "id": "wi-...",
#       "type": "incident",
#       "service": "api-service",
#       "severity": "sev2",
#       "description": "...",
#       "created_at": "2024-01-01T12:00:00",
#       "origin_system": "demo"
#     }
#   ],
#   "total": 1,
#   "limit": 50,
#   "offset": 0
# }
```

### Test 4: Get a Specific WorkItem

```bash
# Replace WORK_ITEM_ID with actual ID from previous step
curl http://localhost:8001/work-items/WORK_ITEM_ID
```

### Test 5: Check Database Directly

```bash
# Connect to PostgreSQL
docker exec -it goliath-postgres psql -U goliath -d goliath

# Query work_items table
SELECT id, service, severity, description, created_at, origin_system 
FROM work_items 
ORDER BY created_at DESC 
LIMIT 10;
```

### Test 6: Verify Weaviate Storage

```bash
# Check Weaviate is running
curl http://localhost:8081/v1/.well-known/ready

# Query WorkItem collection (requires Weaviate client)
# This is done internally by the Decision Service
```

---

## Testing a Specific Issue with Monitoring

### Option 1: Manually Create WorkItem

```bash
# Create a work item manually
curl -X POST http://localhost:8001/ingest/demo \
  -H "Content-Type: application/json" \
  -d '{
    "service": "api-service",
    "severity": "sev1",
    "description": "High error rate detected: 500 errors/sec on /api/v1/users",
    "type": "incident",
    "raw_log": "[ERROR] High error rate detected: 500 errors/sec on /api/v1/users"
  }'
```

### Option 2: Increase Error Probability (Temporary)

```bash
# Stop monitoring
curl -X POST http://localhost:8006/monitoring/stop

# Edit docker-compose.yml or .env to increase error probability
# MONITORING_ERROR_PROBABILITY=0.5  # 50% chance instead of 5%

# Restart monitoring service
make rebuild SERVICE=monitoring

# Or restart entire stack
make restart
```

### Option 3: Trigger Error Manually (For Testing)

You can modify the Monitoring service temporarily to force an error:

1. Edit `services/monitoring/main.py`
2. In `monitoring_loop()`, change:
   ```python
   # From:
   if random.random() < ERROR_PROBABILITY:
   
   # To:
   if True:  # Always trigger error
   ```
3. Rebuild: `make rebuild SERVICE=monitoring`

### Option 4: Use Monitoring API to Control Behavior

```bash
# Stop monitoring
curl -X POST http://localhost:8006/monitoring/stop

# Start monitoring (will use current config)
curl -X POST http://localhost:8006/monitoring/start

# Check status
curl http://localhost:8006/monitoring/status
```

---

## Troubleshooting

### Issue: Monitoring Not Creating WorkItems

**Check 1: Is Monitoring Running?**
```bash
curl http://localhost:8006/monitoring/status
# Should return "status": "running"
```

**Check 2: Are Errors Being Detected?**
```bash
make logs SERVICE=monitoring
# Look for [ERROR] messages
```

**Check 3: Is Ingest Service Reachable?**
```bash
# Check Ingest health
curl http://localhost:8001/healthz

# Check Monitoring can reach Ingest
docker exec goliath-monitoring curl http://ingest:8000/healthz
```

**Check 4: Check Ingest Logs**
```bash
make logs SERVICE=ingest
# Look for "Created WorkItem" messages
```

### Issue: WorkItems Not Appearing in Database

**Check 1: Database Connection**
```bash
# Check PostgreSQL is running
docker exec goliath-postgres pg_isready -U goliath

# Check Ingest can connect
docker exec goliath-ingest python -c "from db import get_db_connection; conn = get_db_connection(); print('Connected!')"
```

**Check 2: Check Ingest Logs for Errors**
```bash
make logs SERVICE=ingest
# Look for database errors
```

**Check 3: Verify Table Exists**
```bash
docker exec -it goliath-postgres psql -U goliath -d goliath -c "\d work_items"
```

### Issue: LLM Preprocessing Not Working

**Check 1: OpenAI API Key**
```bash
# Check .env file
grep OPENAI_API_KEY .env
# Should have: OPENAI_API_KEY=sk-...

# If missing, add it to .env and restart
make restart
```

**Check 2: LLM Client Initialization**
```bash
# Check Monitoring logs
make logs SERVICE=monitoring
# Should NOT see: "OPENAI_API_KEY not provided"
```

**Note:** LLM preprocessing is optional. If API key is missing, Monitoring will use basic cleaning (removes log prefixes).

---

## Expected Behavior

### Normal Operation

1. **Monitoring Service** logs every 5 seconds
2. **Every ~20 cycles** (5% probability), an error is detected
3. **Error is preprocessed** (LLM if available, basic cleaning otherwise)
4. **WorkItem is created** via Ingest Service
5. **WorkItem is stored** in PostgreSQL and Weaviate
6. **Monitoring continues** logging

### What You Should See

**Monitoring Logs:**
```
[INFO] Processing 123 requests/sec
[INFO] Cache hit rate: 95%
[ERROR] High error rate detected: 500 errors/sec on /api/v1/users
WorkItem created successfully: wi-abc123def456
[INFO] Handling 456 concurrent connections
```

**Ingest Logs:**
```
Created WorkItem wi-abc123def456 for service api-service
```

**Database:**
```sql
SELECT COUNT(*) FROM work_items;  -- Should increase over time
```

---

## Next Steps

Once Monitoring → Ingest is working:

1. **Decision Service** will route WorkItems to humans
2. **Executor Service** will create Jira issues
3. **Learner Service** will process outcomes and update human profiles
4. **Explain Service** will generate evidence for decisions

The pipeline is designed to be **incremental** - each service can be tested independently!

