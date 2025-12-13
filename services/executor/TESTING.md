# Testing Guide for Person 4 Services

## Where is PostgreSQL?

PostgreSQL runs in a **Docker container** defined in `infra/docker-compose.yml`:
- **Container name**: `goliath-postgres`
- **Port**: `5432` (mapped to host)
- **Database**: `goliath`
- **User/Password**: `goliath/goliath`
- **Connection URL**: `postgresql://goliath:goliath@postgres:5432/goliath` (from inside Docker)
- **Connection URL (host)**: `postgresql://goliath:goliath@localhost:5432/goliath` (from host machine)

The database is automatically initialized with `scripts/init_db.sql` when the container first starts, which includes:
- `work_items` table
- `humans` table
- `executed_actions` table (added for Executor)
- All knowledge graph edge tables

## Is Everything Set Up?

### ✅ Completed (Person 4 Tasks)

**Executor Service:**
- ✅ Service scaffolded with FastAPI
- ✅ Database connection (`db.py`) with connection pooling
- ✅ Mapping functions (`mappings.py`) - service→project, severity→priority, human→accountId
- ✅ `POST /executeDecision` endpoint implemented
- ✅ Jira API integration with retry logic (exponential backoff)
- ✅ Fallback strategy (stores in DB if Jira fails)
- ✅ Error handling and logging
- ✅ Type safety with Pydantic models
- ✅ Correlation ID middleware
- ✅ Database schema (`executed_actions` table) added to `init_db.sql`
- ✅ README.md created

**Explain Service:**
- ✅ Service scaffolded with FastAPI
- ✅ `POST /explainDecision` endpoint implemented
- ✅ LLM-based evidence generation (OpenAI, temperature=0)
- ✅ "Why not next best" logic
- ✅ Constraints summary formatting
- ✅ Fallback to template-based evidence if LLM fails
- ✅ Error handling and logging
- ✅ Type safety with Pydantic models
- ✅ Correlation ID middleware
- ✅ README.md created

### ⚠️ Optional/Not Yet Implemented

- [ ] Slack integration (optional, behind flag)
- [ ] Unit tests with pytest (test files don't exist yet)
- [ ] Integration tests
- [ ] Mock data files for testing

## How to Test

### Option 1: Quick Manual Test (Recommended)

**Test Executor Service:**
```bash
cd services/executor
./test_manual.sh
```

**Test Explain Service:**
```bash
cd services/explain
export OPENAI_API_KEY=sk-your-key-here  # Required for Explain service
./test_manual.sh
```

### Option 2: Start Services and Test with curl

**1. Start infrastructure:**
```bash
# From project root
make start  # Starts all services
# OR just start what you need:
docker-compose -f infra/docker-compose.yml up -d postgres jira-simulator executor explain
```

**2. Wait for services to be healthy:**
```bash
make health
```

**3. Test Executor:**
```bash
curl -X POST http://localhost:8004/executeDecision \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "test-123",
    "work_item_id": "work-123",
    "primary_human_id": "human-1",
    "backup_human_ids": [],
    "evidence": [],
    "work_item": {
      "service": "api",
      "severity": "sev2",
      "description": "Test incident"
    }
  }'
```

**4. Test Explain:**
```bash
curl -X POST http://localhost:8005/explainDecision \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "test-123",
    "work_item": {
      "id": "work-123",
      "service": "api",
      "severity": "sev2",
      "description": "Test incident",
      "type": "incident"
    },
    "primary_human_id": "human-1",
    "primary_features": {
      "human_id": "human-1",
      "display_name": "Test User",
      "fit_score": 0.8,
      "resolves_count": 10,
      "transfers_count": 1,
      "on_call": false,
      "pages_7d": 0,
      "active_items": 2
    },
    "backup_human_ids": [],
    "backup_features": [],
    "constraints_checked": []
  }'
```

### Option 3: Test via Docker Compose

**Start all services:**
```bash
make setup  # First time setup
# OR
make start  # If already set up
```

**Check service health:**
```bash
curl http://localhost:8004/healthz  # Executor
curl http://localhost:8005/healthz  # Explain
```

**View logs:**
```bash
make logs SERVICE=executor
make logs SERVICE=explain
```

## Prerequisites

1. **Docker & Docker Compose** - For running services
2. **PostgreSQL** - Runs in Docker container (auto-started)
3. **Jira Simulator** - Runs in Docker container (dependency for Executor)
4. **OpenAI API Key** - Required for Explain service (set in `.env` file)

## Environment Setup

Create `.env` file in project root:
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4, etc.
```

## Troubleshooting

**Executor fails to connect to Jira Simulator:**
- Check Jira Simulator is running: `curl http://localhost:8080/healthz`
- Check `JIRA_SIMULATOR_URL` env var is set correctly

**Executor fails to connect to PostgreSQL:**
- Check PostgreSQL is running: `docker ps | grep postgres`
- Check `POSTGRES_URL` env var is set correctly
- Check database was initialized: `docker exec -it goliath-postgres psql -U goliath -d goliath -c "\dt"`

**Explain service fails:**
- Check `OPENAI_API_KEY` is set in `.env` file
- Check API key is valid
- Check you have credits/quota in OpenAI account

**Database table missing:**
- Restart PostgreSQL container to re-run `init_db.sql`
- Or manually run: `docker exec -i goliath-postgres psql -U goliath -d goliath < scripts/init_db.sql`

## Next Steps

1. **Add unit tests** - Create `tests/test_standalone.py` files
2. **Add integration tests** - Test full flow with other services
3. **Add Slack integration** (optional)
4. **Add more error scenarios** - Test edge cases
