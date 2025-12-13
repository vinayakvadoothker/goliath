# Jira Simulator

**Full Jira REST API v3 mock - exact endpoint compatibility.**

## Quick Start

```bash
# Start service (via Docker)
docker-compose -f ../../infra/docker-compose.yml up -d jira-simulator

# Or run locally
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## Setup Database Schema

Before first use, run the migration to create outcome generation tables:

```bash
# From inside the jira-simulator container or with psql
psql $POSTGRES_URL -f migrations/create_outcome_tables.sql
```

Or manually:

```sql
-- See migrations/create_outcome_tables.sql
```

## API Endpoints

- `GET /rest/api/3/search?jql=...` - JQL search
- `POST /rest/api/3/issue` - Create issue
- `GET /rest/api/3/issue/:key` - Get issue
- `PUT /rest/api/3/issue/:key` - Update issue
- `GET /rest/api/3/user/search` - Search users
- `GET /rest/api/3/project` - List projects
- `GET /rest/api/3/outcomes/pending` - Get pending outcomes (for Ingest)
- `GET /healthz` - Health check

## Outcome Generation

The Jira Simulator automatically generates outcomes when:
- Issues are marked as "Done" (resolved outcome)
- Issues are reassigned (reassigned outcome)

**Configuration:**
- `JIRA_OUTCOME_GENERATION_ENABLED=true` (default: true)
- `JIRA_OUTCOME_POLL_INTERVAL=30` (seconds, default: 30)
- `INGEST_SERVICE_URL=http://ingest:8000`

**Two modes:**
1. **Polling**: Ingest calls `GET /rest/api/3/outcomes/pending` to check for new outcomes
2. **Webhook simulation**: Jira Simulator calls Ingest directly when outcomes are generated (default)

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
JIRA_OUTCOME_GENERATION_ENABLED=true
JIRA_OUTCOME_POLL_INTERVAL=30
INGEST_SERVICE_URL=http://ingest:8000
```

## Testing

```bash
# Standalone testing
./scripts/test_standalone.sh

# Or run pytest directly
pytest tests/test_jql_parser.py -v
```

## JQL Parser

The JQL parser supports:
- Basic operators: `=`, `!=`, `>`, `<`, `>=`, `<=`
- Logical operators: `AND`, `OR`
- Relative dates: `resolved >= -90d`
- Field mappings: `project` → `project_key`, `status` → `status_name`, etc.

**Examples:**
- `project=API AND status=Done`
- `status=Done OR status=Closed`
- `resolved >= -90d AND assignee=557058:abc123`

## Documentation

See [Person 1 Developer Guide](../../for_developer_docs/person1_decision_infrastructure_jira.md) for complete documentation.
