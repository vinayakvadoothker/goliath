# Ingest Service

**Single source of truth for all work items.**

## Quick Start

```bash
# Start service (via Docker)
docker-compose -f ../../infra/docker-compose.yml up -d ingest

# Or run locally
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## API Endpoints

- `POST /ingest/demo` - Create demo work item
- `POST /webhooks/jira` - Jira webhook handler
- `POST /work-items` - Manual work item creation
- `GET /work-items` - List work items
- `GET /work-items/:id` - Get work item
- `POST /work-items/:id/outcome` - Record outcome
- `GET /healthz` - Health check

## Environment Variables

```bash
INGEST_SERVICE_PORT=8001
POSTGRES_URL=postgresql://goliath:goliath@postgres:5432/goliath
WEAVIATE_URL=http://weaviate:8080
LEARNER_SERVICE_URL=http://localhost:8003
OPENAI_API_KEY=sk-...
```

## Testing

```bash
# Standalone testing
./scripts/test_standalone.sh
```

## Documentation

See [Person 3 Developer Guide](../../for_developer_docs/person3_ingest_monitoring.md) for complete documentation.

