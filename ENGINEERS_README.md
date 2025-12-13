# Goliath - Engineers Quick Start Guide

**Welcome to Goliath! This is your complete setup guide.**

## 🚀 One-Command Setup

```bash
make setup
```

Or use the wrapper:

```bash
./scripts/setup.sh
```

**That's it. Everything is set up.**

---

## 📋 What Just Happened?

The setup script:
1. ✅ Created all project directories
2. ✅ Started PostgreSQL and Weaviate
3. ✅ Seeded Jira Simulator (200 people, 5000+ tickets)
4. ✅ Built and started all services
5. ✅ Ready for development!

---

## 🎯 Your Role

**Find your developer guide:**
- **Person 1**: `for_developer_docs/person1_decision_infrastructure_jira.md`
- **Person 2**: `for_developer_docs/person2_learner.md`
- **Person 3**: `for_developer_docs/person3_ingest_monitoring.md`
- **Person 4**: `for_developer_docs/person4_executor_explain.md`
- **Person 5**: `for_developer_docs/person5_ui.md`

**Each guide has:**
- Complete role breakdown
- What to build and why
- API schemas and examples
- Database schemas
- Testing strategies
- Complete checklists

---

## 🛠️ Daily Development Commands

**All commands use `make`:**

```bash
# Start all services
make start

# Stop all services
make stop

# Restart all services
make restart

# View logs (all services)
make logs

# View logs for specific service
make logs SERVICE=ingest

# Check service status
make status

# Check service health
make health

# Rebuild a service
make rebuild SERVICE=ingest

# Seed Jira Simulator
make seed

# Show all commands
make help
```

---

## 🧪 Testing Your Service

**Each service can be tested independently:**

```bash
# Navigate to your service
cd services/[your-service]

# Run standalone tests
./scripts/test_standalone.sh
```

**This starts only your service + its dependencies (not all services).**

---

## 📁 Project Structure

```
goliath/
├── services/          # Your service goes here
│   ├── [your-service]/
│   │   ├── README.md
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── scripts/
│   │       └── test_standalone.sh
├── apps/ui/           # UI (Person 5)
├── contracts/         # Shared types (Person 1)
├── infra/             # Docker Compose (Person 1)
├── scripts/           # Setup scripts
└── for_developer_docs/ # Your guide!
```

---

## 🔧 Environment Setup

**1. Copy environment file:**
```bash
cp .env.example .env
```

**2. Add your LLM API key:**
```bash
# Edit .env and add:
OPENAI_API_KEY=sk-your-key-here
```

**3. Restart services:**
```bash
./scripts/stop.sh
./scripts/start.sh
```

---

## 🐳 Docker Commands

```bash
# View all services
docker-compose -f infra/docker-compose.yml ps

# View logs
docker-compose -f infra/docker-compose.yml logs -f [service]

# Restart a service
docker-compose -f infra/docker-compose.yml restart [service]

# Rebuild a service
docker-compose -f infra/docker-compose.yml build [service]
```

---

## 🌐 Service URLs

| Service | URL | Your Service? |
|---------|-----|---------------|
| Ingest | http://localhost:8001 | Person 3 |
| Decision | http://localhost:8002 | Person 1 |
| Learner | http://localhost:8003 | Person 2 |
| Executor | http://localhost:8004 | Person 4 |
| Explain | http://localhost:8005 | Person 4 |
| Monitoring | http://localhost:8006 | Person 3 |
| Jira Sim | http://localhost:8080 | Person 1 |
| UI | http://localhost:3000 | Person 5 |

---

## ✅ Health Checks

**All services expose `/healthz`:**

```bash
curl http://localhost:8001/healthz  # Ingest
curl http://localhost:8002/healthz  # Decision
curl http://localhost:8003/healthz  # Learner
# ... etc
```

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker ps

# Check logs
./scripts/logs.sh [service-name]

# Rebuild
./scripts/dev.sh rebuild [service-name]
```

### Database connection errors
```bash
# Check PostgreSQL is running
docker-compose -f infra/docker-compose.yml ps postgres

# Check connection string in .env
```

### Port already in use
```bash
# Find process using port
lsof -i :8001  # Replace with your port

# Kill process or change port in docker-compose.yml
```

---

## �� Next Steps

1. **Read your developer guide**: `for_developer_docs/person[1-5]_*.md`
2. **Check your cursor rules**: `.cursor/rules/person[1-5]-*/RULE.md`
3. **Read your service README**: `services/[your-service]/README.md`
4. **Start coding!**

---

## 🎯 Success Criteria

**Your service must:**
- ✅ Have `/healthz` endpoint
- ✅ Have standalone test script
- ✅ Have README with API docs
- ✅ Follow cursor rules
- ✅ Handle errors gracefully
- ✅ Log with correlation IDs

---

## 🆘 Getting Help

1. Read your developer guide
2. Check service README
3. Review cursor rules
4. Check logs: `./scripts/logs.sh [service]`

---

**Happy coding! Build something that matters.**
