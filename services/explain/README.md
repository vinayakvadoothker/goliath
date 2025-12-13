# Explain Service

**Generates contextual evidence bullets for decisions.**

## Quick Start

```bash
# Start service (via Docker)
docker-compose -f ../../infra/docker-compose.yml up -d explain

# Or run locally
python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload
```

## API Endpoints

- `POST /explainDecision` - Generate evidence bullets
- `GET /healthz` - Health check

## Environment Variables

```bash
EXPLAIN_SERVICE_PORT=8005
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2
```

## Testing

```bash
# Standalone testing
./scripts/test_standalone.sh
```

## Documentation

See [Person 4 Developer Guide](../../for_developer_docs/person4_executor_explain.md) for complete documentation.

