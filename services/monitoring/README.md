# Monitoring Service

**Simulates monitoring/observability systems - continuously logs and detects errors.**

## Quick Start

The Monitoring Service **auto-starts** the monitoring loop when the service starts (by default).

```bash
# Start service (via Docker) - monitoring loop will auto-start
docker-compose -f ../../infra/docker-compose.yml up -d monitoring

# Or run locally - monitoring loop will auto-start
python -m uvicorn main:app --host 0.0.0.0 --port 8006 --reload
```

**That's it!** The monitoring loop will start automatically and begin:
- Logging normal messages (INFO, WARN, DEBUG) every 5 seconds
- Detecting errors with 5% probability per cycle
- Creating WorkItems via Ingest service when errors are detected

## Auto-Start Behavior

**By default, the monitoring loop starts automatically** when the service starts. This is controlled by the `MONITORING_AUTO_START` environment variable:

- `MONITORING_AUTO_START=true` (default) - Loop starts automatically
- `MONITORING_AUTO_START=false` - Loop does NOT start automatically (must start manually)

## Manual Control

You can start/stop the monitoring loop manually via API:

```bash
# Check if monitoring is running
curl http://localhost:8006/monitoring/status

# Start monitoring loop (if stopped)
curl -X POST http://localhost:8006/monitoring/start

# Stop monitoring loop (if running)
curl -X POST http://localhost:8006/monitoring/stop

# Get detailed status
curl http://localhost:8006/monitoring/status
```

**Response example:**
```json
{
  "status": "running",
  "service_name": "api-service",
  "error_count": 3,
  "last_error_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:00:00Z",
  "error_probability": 0.05,
  "log_interval": 5
}
```

## API Endpoints

- `GET /healthz` - Health check (includes uptime)
- `POST /monitoring/start` - Start monitoring loop manually
- `POST /monitoring/stop` - Stop monitoring loop manually
- `GET /monitoring/status` - Get monitoring status (running/stopped, error count, last error time)

## Environment Variables

```bash
# Service configuration
MONITORING_SERVICE_PORT=8006
MONITORING_SERVICE_NAME=api-service          # Service name to monitor
MONITORING_ERROR_PROBABILITY=0.05          # Probability of error per log cycle (5%)
MONITORING_LOG_INTERVAL=5                   # Seconds between log cycles
MONITORING_INGEST_URL=http://ingest:8000    # Ingest service URL
MONITORING_AUTO_START=true                  # Auto-start monitoring loop (default: true)

# LLM configuration (optional)
OPENAI_API_KEY=sk-...                       # OpenAI API key for log preprocessing
OPENAI_MODEL=gpt-4                          # OpenAI model to use
```

## How It Works

1. **Service starts** → Monitoring loop auto-starts (if `MONITORING_AUTO_START=true`)
2. **Every 5 seconds** (configurable):
   - Logs normal messages: `[INFO] Processing 123 requests/sec`
   - Random check: 5% chance (configurable) → Error detected
3. **When error detected**:
   - Generates realistic error message (e.g., "High error rate detected: 500 errors/sec")
   - LLM preprocesses error log (cleans, normalizes)
   - Determines severity (sev1, sev2, sev3)
   - Calls Ingest service `POST /ingest/demo` to create WorkItem
   - Logs incident creation
4. **Ingest creates WorkItem** → Decision service routes it → Executor creates Jira issue
5. **Loop continues** until stopped

## Error Types

The service simulates 10 different error types:
- High error rate (sev1)
- Database connection timeout (sev2)
- Memory leak (sev1)
- API endpoint 500 errors (sev2)
- Service degradation (sev2)
- Cache miss rate spike (sev3)
- Response time degradation (sev3)
- Disk I/O saturation (sev2)
- CPU throttling (sev2)
- Network packet loss (sev2)

## Testing

```bash
# Standalone testing
./scripts/test_standalone.sh

# Check monitoring status
curl http://localhost:8006/monitoring/status

# View logs
docker logs goliath-monitoring -f
```

## Troubleshooting

**Monitoring loop not starting?**
- Check `MONITORING_AUTO_START` environment variable (should be `true`)
- Check service logs: `docker logs goliath-monitoring`
- Manually start: `curl -X POST http://localhost:8006/monitoring/start`

**No errors being detected?**
- Check `MONITORING_ERROR_PROBABILITY` (default: 0.05 = 5% chance per cycle)
- Increase probability for testing: `MONITORING_ERROR_PROBABILITY=0.5` (50% chance)
- Wait longer - errors are probabilistic

**WorkItems not being created?**
- Check Ingest service is running: `curl http://localhost:8001/healthz`
- Check `MONITORING_INGEST_URL` is correct
- Check service logs for connection errors

## Documentation

See [Person 3 Developer Guide](../../for_developer_docs/person3_ingest_monitoring.md) for complete documentation.

