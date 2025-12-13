# Goliath Control Center - Interactive Error Simulator

## What Is It?

The **Control Center** is an interactive web UI that lets you **trigger errors and watch Goliath route them in real-time**. It's the "Goliath search tool" that creates work items and generates errors for the pipeline, which should then create Jira bugs.

---

## How to Access

### Option 1: Via Docker (Recommended)

```bash
# Start all services (includes Control Center)
make start

# Access Control Center UI
open http://localhost:6767
```

### Option 2: Manual Development

```bash
# Terminal 1: Start Control Center API (backend)
cd services/control-center
python3 -m uvicorn main:app --port 8007

# Terminal 2: Start Control Center UI (frontend)
cd apps/control-center
pnpm install
pnpm dev  # Runs on port 6767
```

---

## Architecture

### Services

1. **Control Center API** (FastAPI backend)
   - Port: `8007`
   - WebSocket server for real-time updates
   - Handles error triggers and action processing

2. **Control Center UI** (Next.js frontend)
   - Port: `6767`
   - Interactive dashboard with error trigger buttons
   - Real-time updates via WebSocket

### Integration Flow

```
User clicks error button
  ↓
Control Center API generates error message
  ↓
Creates WorkItem via Ingest Service (POST /ingest/demo)
  ↓
[Automatic Orchestration]
  ↓
Ingest → Decision Service (automatic)
  ↓
Decision → Explain Service (automatic)
  ↓
Decision → Executor Service (automatic)
  ↓
Executor creates Jira issue
  ↓
Control Center polls for decision/Jira issue
  ↓
Updates UI in real-time
```

---

## Features

### 1. Interactive Error Triggers

Click buttons to trigger different error types:

- **High Error Rate** (`high_error_rate`) - sev1
- **Database Timeout** (`database_timeout`) - sev2
- **Memory Leak** (`memory_leak`) - sev1
- **API 500 Errors** (`api_500_errors`) - sev2
- **Service Degradation** (`service_degradation`) - sev2
- **Cache Miss Spike** (`cache_miss_spike`) - sev3
- **Response Time Degradation** (`response_time_degradation`) - sev3
- **Disk I/O Saturation** (`disk_io_saturation`) - sev2
- **CPU Throttling** (`cpu_throttling`) - sev2
- **Network Packet Loss** (`network_packet_loss`) - sev2
- **Queue Backlog** (`queue_backlog`) - sev2

### 2. Real-Time Dashboard

- **System Metrics**: CPU, memory, error rate, latency
- **Live Logs**: Real-time log stream
- **Incidents**: List of triggered incidents
- **Decisions**: Latest routing decision with evidence
- **Jira Issues**: Created Jira issue keys

### 3. Full Pipeline Integration

With **automatic orchestration** implemented:

1. ✅ **WorkItem Creation** - Creates WorkItem via Ingest Service
2. ✅ **Automatic Decision** - Ingest Service automatically calls Decision Service
3. ✅ **Automatic Explain** - Decision Service automatically calls Explain Service
4. ✅ **Automatic Execution** - Decision Service automatically calls Executor Service
5. ✅ **Jira Bug Creation** - Executor Service creates Jira issue
6. ✅ **Real-Time Updates** - Control Center polls and displays results

---

## How It Works

### Step 1: User Triggers Error

User clicks a button (e.g., "High Error Rate") in the UI.

### Step 2: Error Generation

Control Center API:
- Generates realistic error message using `error_simulator.py`
- Example: `"High error rate detected: 450 errors/sec on /api/v1/users"`

### Step 3: WorkItem Creation

Control Center calls Ingest Service:
```python
POST /ingest/demo
{
  "service": "api-service",
  "severity": "sev1",
  "description": "High error rate detected: 450 errors/sec on /api/v1/users",
  "type": "incident",
  "raw_log": "High error rate detected: 450 errors/sec on /api/v1/users"
}
```

### Step 4: Automatic Orchestration

**Ingest Service** automatically:
- Creates WorkItem in PostgreSQL
- Stores embedding in Weaviate
- **Calls Decision Service** (`POST /decide`)

**Decision Service** automatically:
- Makes routing decision
- **Calls Explain Service** (`POST /explainDecision`)
- **Calls Executor Service** (`POST /executeDecision`)

**Executor Service**:
- Creates Jira issue
- Returns Jira issue key

### Step 5: Polling & Updates

Control Center polls for:
1. **Decision** - Checks Decision Service for routing decision
2. **Jira Issue** - Checks Executor Service for created Jira issue

Updates UI in real-time via WebSocket.

---

## Error Types

All error types are defined in `services/control-center/actions/error_simulator.py`:

| Error Type | Severity | Description |
|------------|----------|-------------|
| `high_error_rate` | sev1 | High error rate on API endpoints |
| `database_timeout` | sev2 | Database connection pool exhausted |
| `memory_leak` | sev1 | Memory usage critical |
| `api_500_errors` | sev2 | API endpoint returning 500 errors |
| `service_degradation` | sev2 | Service response time increased |
| `cache_miss_spike` | sev3 | Cache miss rate spike |
| `response_time_degradation` | sev3 | Response time degradation |
| `disk_io_saturation` | sev2 | Disk I/O saturation |
| `cpu_throttling` | sev2 | CPU usage critical |
| `network_packet_loss` | sev2 | Network packet loss |
| `queue_backlog` | sev2 | Message queue backlog |

---

## Testing the Full Pipeline

### Prerequisites

1. **Start all services:**
   ```bash
   make start
   ```

2. **Seed data (optional, but recommended):**
   ```bash
   make seed  # Creates 5 specialized users with work history
   ```

3. **Access Control Center:**
   ```bash
   open http://localhost:6767
   ```

### Test Flow

1. **Open Control Center UI** at `http://localhost:6767`
2. **Click an error button** (e.g., "High Error Rate")
3. **Watch the pipeline:**
   - Error appears in logs
   - WorkItem created (check Ingest Service logs)
   - Decision made (check Decision Service logs)
   - Jira issue created (check Executor Service logs)
   - UI updates with decision and Jira key

### Verify Jira Issue Created

```bash
# Check Executor Service logs
make logs SERVICE=executor

# Or check Jira Simulator
curl "http://localhost:8080/rest/api/3/search?jql=order+by+created+DESC&maxResults=5" | jq

# Or check real Jira (if configured)
# Visit your Jira instance and search for recently created issues
```

---

## Troubleshooting

### Issue: Control Center UI not loading

**Solution:**
- Check Control Center API is running: `curl http://localhost:8007/healthz`
- Check Control Center UI is running: `curl http://localhost:6767`
- Check logs: `make logs SERVICE=control-center-api`

### Issue: Errors not creating WorkItems

**Solution:**
- Check Ingest Service is running: `curl http://localhost:8001/healthz`
- Check Ingest Service logs: `make logs SERVICE=ingest`
- Verify `INGEST_SERVICE_URL` in Control Center API environment

### Issue: Decisions not being made

**Solution:**
- Check Decision Service is running: `curl http://localhost:8002/healthz`
- Check Decision Service logs: `make logs SERVICE=decision`
- Verify automatic orchestration is working (Ingest should call Decision automatically)

### Issue: Jira issues not being created

**Solution:**
- Check Executor Service is running: `curl http://localhost:8004/healthz`
- Check Executor Service logs: `make logs SERVICE=executor`
- Verify Jira configuration (Jira Simulator or real Jira)
- Check `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_KEY` in `.env` (if using real Jira)

### Issue: Polling timeout

**Solution:**
- Increase polling attempts in `decision_client.py` and `executor_client.py`
- Check service logs for errors
- Verify services are healthy: `make health`

---

## Code Locations

- **Control Center API**: `services/control-center/`
  - `main.py` - FastAPI app and WebSocket server
  - `actions/action_handlers.py` - Error trigger handlers
  - `actions/error_simulator.py` - Error message generation
  - `integrations/ingest_client.py` - Ingest Service client
  - `integrations/decision_client.py` - Decision Service client
  - `integrations/executor_client.py` - Executor Service client
  - `state/system_state.py` - System state management

- **Control Center UI**: `apps/control-center/`
  - Next.js 14 application
  - WebSocket client for real-time updates
  - Interactive dashboard components

---

## Summary

✅ **Control Center is the "Goliath search tool"** that:
- Creates WorkItems via Ingest Service
- Generates realistic errors for testing
- **Should create Jira bugs** via automatic orchestration
- Provides real-time UI updates

**With automatic orchestration implemented:**
- WorkItem creation → **Automatic** Decision → **Automatic** Explain → **Automatic** Executor → **Jira bug created** ✅

**Access it at:** `http://localhost:6767` (after running `make start`)

