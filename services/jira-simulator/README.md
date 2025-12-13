# Jira Simulator

**Full Jira REST API v3 mock - exact endpoint compatibility.**

## Quick Start

```bash
# Start service (via Docker)
docker-compose -f ../../infra/docker-compose.yml up -d jira-simulator

# Or run locally
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## API Endpoints

- `GET /rest/api/3/search?jql=...` - JQL search
- `POST /rest/api/3/issue` - Create issue
- `GET /rest/api/3/issue/:key` - Get issue
- `PUT /rest/api/3/issue/:key` - Update issue
- `GET /rest/api/3/user/search` - Search users
- `GET /rest/api/3/project` - List projects
- `GET /healthz` - Health check

## Seeding Data

```bash
# Seed with 200 users and 5000+ tickets
python ../../scripts/seed_jira_data.py
```

## Environment Variables

```bash
JIRA_SIMULATOR_PORT=8080
POSTGRES_URL=postgresql://goliath:goliath@postgres:5432/goliath
JIRA_SIMULATOR_SEED_USERS=200
JIRA_SIMULATOR_SEED_CLOSED_TICKETS=5000
JIRA_SIMULATOR_SEED_OPEN_TICKETS=1000
```

## Testing

```bash
# Standalone testing
./scripts/test_standalone.sh
```

## Documentation

See [Person 1 Developer Guide](../../for_developer_docs/person1_decision_infrastructure_jira.md) for complete documentation.

