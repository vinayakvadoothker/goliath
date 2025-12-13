# Decision Service

**The core brain - decision engine for incident routing.**

## Quick Start

```bash
# Start service (via Docker)
docker-compose -f ../../infra/docker-compose.yml up -d decision

# Or run locally
python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

## API Endpoints

- `POST /decide` - Make decision for work item
- `GET /decisions/:work_item_id` - Get decision
- `GET /audit/:work_item_id` - Get full audit trail
- `GET /healthz` - Health check

## Environment Variables

```bash
DECISION_SERVICE_PORT=8002
POSTGRES_URL=postgresql://goliath:goliath@postgres:5432/goliath
WEAVIATE_URL=http://weaviate:8080
LEARNER_SERVICE_URL=http://localhost:8003
EXPLAIN_SERVICE_URL=http://localhost:8005
INGEST_SERVICE_URL=http://localhost:8001
OPENAI_API_KEY=sk-...
```

## Testing

```bash
# Standalone testing
./scripts/test_standalone.sh
```

## Documentation

See [Person 1 Developer Guide](../../for_developer_docs/person1_decision_infrastructure_jira.md) for complete documentation.

