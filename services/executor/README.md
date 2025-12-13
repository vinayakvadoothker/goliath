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

# Jira Configuration (supports both real Jira and Jira Simulator)
# Option 1: Use real Jira (requires all three)
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_KEY=your-api-key

# Option 2: Use Jira Simulator (default, no auth required)
JIRA_SIMULATOR_URL=http://localhost:8080

# If JIRA_URL, JIRA_EMAIL, and JIRA_API_KEY are all set, real Jira will be used.
# Otherwise, Jira Simulator will be used.

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

