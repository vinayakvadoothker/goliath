# Learner Service

**The memory - capability profiles and learning loop.**

## Quick Start

```bash
# Start service (via Docker)
docker-compose -f ../../infra/docker-compose.yml up -d learner

# Or run locally
python -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

## API Endpoints

- `GET /profiles?service=X` - Get human profiles for service
- `POST /outcomes` - Process outcome (learning loop)
- `GET /stats?human_id=X` - Get human stats
- `POST /sync/jira` - Sync Jira tickets
- `GET /healthz` - Health check

## Environment Variables

```bash
LEARNER_SERVICE_PORT=8003
POSTGRES_URL=postgresql://goliath:goliath@postgres:5432/goliath
WEAVIATE_URL=http://weaviate:8080
JIRA_SIMULATOR_URL=http://localhost:8080
OPENAI_API_KEY=sk-...
```

## Testing

```bash
# Standalone testing
./scripts/test_standalone.sh
```

## Documentation

See [Person 2 Developer Guide](../../for_developer_docs/person2_learner.md) for complete documentation.

