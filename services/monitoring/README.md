# Monitoring Service

**Simulates monitoring/observability systems - continuously logs and detects errors.**

## Quick Start

```bash
# Start service (via Docker)
docker-compose -f ../../infra/docker-compose.yml up -d monitoring

# Or run locally
python -m uvicorn main:app --host 0.0.0.0 --port 8006 --reload
```

## API Endpoints

- `GET /healthz` - Health check
- `POST /monitoring/start` - Start monitoring loop
- `POST /monitoring/stop` - Stop monitoring loop
- `GET /monitoring/status` - Get monitoring status

## Environment Variables

```bash
MONITORING_SERVICE_PORT=8006
MONITORING_SERVICE_NAME=api-service
MONITORING_ERROR_PROBABILITY=0.05
MONITORING_LOG_INTERVAL=5
MONITORING_INGEST_URL=http://localhost:8001
OPENAI_API_KEY=sk-...
```

## Testing

```bash
# Standalone testing
./scripts/test_standalone.sh
```

## Documentation

See [Person 3 Developer Guide](../../for_developer_docs/person3_ingest_monitoring.md) for complete documentation.

