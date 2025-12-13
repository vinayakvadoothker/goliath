# Executor Service

**Executes decisions by creating Jira issues.**

## Quick Start

```bash
# Start service (via Docker)
docker-compose -f ../../infra/docker-compose.yml up -d executor

# Or run locally
python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

## API Endpoints

- `POST /executeDecision` - Execute decision (create Jira issue)
- `GET /healthz` - Health check

## Environment Variables

```bash
EXECUTOR_SERVICE_PORT=8004
POSTGRES_URL=postgresql://goliath:goliath@postgres:5432/goliath
JIRA_SIMULATOR_URL=http://localhost:8080
SLACK_WEBHOOK_URL= (optional)
SLACK_ENABLED=false
```

## Testing

```bash
# Standalone testing
./scripts/test_standalone.sh
```

## Documentation

See [Person 4 Developer Guide](../../for_developer_docs/person4_executor_explain.md) for complete documentation.

