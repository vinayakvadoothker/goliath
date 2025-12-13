# Integration Tests

**End-to-end tests for service-to-service communication.**

## Test Files

- `test_e2e_flow.sh` - Manual E2E test script (checks service health and basic integration)
- `services/decision/tests/test_integration.py` - Decision Service integration tests
- `services/jira-simulator/tests/test_integration.py` - Jira Simulator integration tests

## Running Tests

### Decision Service Integration Tests

```bash
cd services/decision
pytest tests/test_integration.py -v
```

**Tests:**
- Decision Service → Learner Service communication
- Timeout handling
- Error handling
- Fallback mechanism
- End-to-end decision flow

### Jira Simulator Integration Tests

```bash
cd services/jira-simulator
pytest tests/test_integration.py -v
```

**Tests:**
- Jira Simulator → Ingest Service communication
- Outcome generation
- Polling endpoint
- Error handling

### Manual E2E Test

```bash
# Make sure all services are running
docker-compose -f infra/docker-compose.yml up -d

# Run E2E test
./tests/integration/test_e2e_flow.sh
```

## What's Tested

### ✅ Decision Service → Learner Service
- Successful candidate retrieval
- Timeout handling
- Error handling (500, network errors)
- Fallback mechanism when Learner is down

### ✅ Jira Simulator → Ingest Service
- Outcome generation and sending
- Timeout handling
- Error handling
- Polling endpoint functionality

### ✅ End-to-End Flow
- Work Item → Decision → Jira Issue → Outcome → Learning
- Service health checks
- Basic integration verification

## Notes

- Integration tests use mocks for external services
- For full E2E testing, all services must be running
- Manual E2E test script checks service health and basic connectivity
- Full E2E flow requires creating actual work items and issues

