# Quick Start - Goliath

## One Command Setup

```bash
make setup
```

**That's it!** This will:
1. Check prerequisites (Docker, Python, etc.)
2. Create `.env` file from `.env.example`
3. Create all directories
4. Start PostgreSQL and Weaviate
5. Seed Jira Simulator (200 people, 5000+ tickets)
6. Build and start all services
7. Check health of all services

## After Setup

**All services are running:**
- Ingest: http://localhost:8001
- Decision: http://localhost:8002
- Learner: http://localhost:8003
- Executor: http://localhost:8004
- Explain: http://localhost:8005
- Monitoring: http://localhost:8006
- Jira Sim: http://localhost:8080
- UI: http://localhost:3000

## Common Commands

```bash
# View all commands
make help

# Start services
make start

# Stop services
make stop

# View logs
make logs SERVICE=ingest

# Check health
make health

# Rebuild a service
make rebuild SERVICE=ingest
```

## Next Steps

1. Read your developer guide: `for_developer_docs/person[1-5]_*.md`
2. Check your service README: `services/[your-service]/README.md`
3. Start coding!

## Troubleshooting

**Services won't start?**
```bash
make logs SERVICE=ingest
make rebuild SERVICE=ingest
```

**Database connection errors?**
```bash
make stop
make start-infra
# Wait 10 seconds, then:
make start
```

**Port already in use?**
```bash
# Find process
lsof -i :8001

# Kill or change port in docker-compose.yml
```
