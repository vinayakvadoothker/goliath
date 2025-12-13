# Goliath

**Intelligent Incident Routing System** - Decision-grade incident routing with evidence-backed assignment, bounded execution, outcome learning, and audit replay.

> 📖 **New to Goliath?** Start here: [**MISSION.md**](MISSION.md) - Complete mission, vision, why, what, and how.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

## 🚀 Quick Start

**One command to rule them all:**

```bash
make setup
```

Or use the wrapper script:

```bash
./scripts/setup.sh
```

This will:
- ✅ Create all necessary directories
- ✅ Set up Docker containers (PostgreSQL, Weaviate, all services)
- ✅ Install all dependencies
- ✅ Seed Jira Simulator with 200 people and 5000+ tickets
- ✅ Start all services
- ✅ Ready for development!

**That's it. You're ready to code.**

---

## 👋 New Developer Onboarding

**Complete step-by-step guide for first-time setup:**

### Step 1: Prerequisites Check

**Before running anything, make sure you have:**

1. **Docker & Docker Compose**
   ```bash
   # Check if installed
   docker --version
   docker-compose --version
   # OR (newer Docker)
   docker compose version
   
   # If not installed:
   # macOS: brew install docker docker-compose
   # Linux: Follow https://docs.docker.com/get-docker/
   # Windows: Install Docker Desktop
   ```

2. **Python 3.11+**
   ```bash
   # Check version
   python3 --version
   # Should be 3.11 or higher
   
   # If not installed:
   # macOS: brew install python@3.11
   # Linux: sudo apt-get install python3.11
   ```

3. **Node.js 18+** (only if working on UI)
   ```bash
   # Check version
   node --version
   # Should be 18 or higher
   
   # If not installed:
   # macOS: brew install node
   # Linux: Follow https://nodejs.org/
   ```

4. **Git**
   ```bash
   # Check if installed
   git --version
   ```

5. **OpenAI API Key** (or Anthropic)
   - Get your API key from https://platform.openai.com/api-keys
   - Or use Anthropic: https://console.anthropic.com/
   - You'll add this in Step 3

### Step 2: Clone the Repository

```bash
# Clone the repo
git clone https://github.com/vinayakvadoothker/goliath.git

# Navigate to project
cd goliath

# Verify you're in the right place
ls -la
# Should see: Makefile, README.md, services/, apps/, etc.
```

### Step 3: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
# Use your preferred editor:
nano .env
# OR
vim .env
# OR
code .env  # VS Code

# In .env, find this line and add your key:
OPENAI_API_KEY=sk-your-actual-api-key-here

# Save and close the file
```

**Important:** 
- Never commit `.env` to git (it's in `.gitignore`)
- Keep your API key secret
- The `.env` file is for local development only

### Step 4: Run Setup

```bash
# Run the one-command setup
make setup
```

**What happens:**
1. ✅ Checks prerequisites (Docker, Python, etc.)
2. ✅ Creates `.env` if it doesn't exist (you already did this)
3. ✅ Creates all project directories
4. ✅ Starts PostgreSQL and Weaviate
5. ✅ Seeds Jira Simulator (200 users, 5000+ tickets)
6. ✅ Builds all Docker containers
7. ✅ Starts all services
8. ✅ Checks health of all services

**This takes 5-10 minutes the first time** (building Docker images).

### Step 5: Verify Everything Works

```bash
# Check service status
make status

# Check health of all services
make health

# You should see:
# ✅ ingest is healthy
# ✅ decision is healthy
# ✅ learner is healthy
# ✅ executor is healthy
# ✅ explain is healthy
# ✅ monitoring is healthy
# ✅ jira-simulator is healthy
```

**Test a service:**
```bash
# Test Ingest service
curl http://localhost:8001/healthz
# Should return: {"status":"healthy","service":"ingest"}

# Test Decision service
curl http://localhost:8002/healthz
# Should return: {"status":"healthy","service":"decision"}

# Test Jira Simulator
curl http://localhost:8080/healthz
# Should return: {"status":"healthy","service":"jira-simulator"}
```

### Step 6: Find Your Developer Guide

**Each person has their own guide:**

```bash
# Person 1: Decision + Infrastructure + Jira Simulator
cat for_developer_docs/person1_decision_infrastructure_jira.md

# Person 2: Learner Service
cat for_developer_docs/person2_learner.md

# Person 3: Ingest + Monitoring
cat for_developer_docs/person3_ingest_monitoring.md

# Person 4: Executor + Explain
cat for_developer_docs/person4_executor_explain.md

# Person 5: UI
cat for_developer_docs/person5_ui.md
```

**Your guide includes:**
- Complete role breakdown
- What to build and why
- API schemas and examples
- Database schemas
- Testing strategies
- Complete checklists

### Step 7: Check Your Cursor Rules

**Cursor rules are in `.cursor/rules/`:**

```bash
# View your cursor rules
cat .cursor/rules/person[1-5]-*/RULE.md

# These provide coding standards and best practices
# Cursor will automatically apply them when you work on relevant files
```

### Step 8: Start Developing

**Daily workflow:**

```bash
# Morning: Start services
make start

# Check everything is running
make status

# View logs for your service
make logs SERVICE=your-service-name

# Make code changes...

# Rebuild your service after changes
make rebuild SERVICE=your-service-name

# Test your service
curl http://localhost:YOUR_PORT/healthz

# End of day: Stop services (optional)
make stop
```

### Step 9: Common Tasks

**View logs:**
```bash
# All services
make logs

# Specific service
make logs SERVICE=ingest
make logs SERVICE=decision
make logs SERVICE=learner
```

**Rebuild after code changes:**
```bash
# Rebuild your service
make rebuild SERVICE=ingest

# Rebuild all services
make rebuild
```

**Check health:**
```bash
# Quick health check
make health
```

**Restart services:**
```bash
# Restart all
make restart

# Or stop and start
make stop
make start
```

### Step 10: Troubleshooting

**Services won't start?**
```bash
# Check Docker is running
docker ps

# Check logs
make logs SERVICE=service-name

# Rebuild
make rebuild SERVICE=service-name
```

**Port already in use?**
```bash
# Find what's using the port
lsof -i :8001  # Replace with your port

# Kill the process or change port in docker-compose.yml
```

**Database connection errors?**
```bash
# Check PostgreSQL is running
make status
# Look for postgres service

# Check logs
make logs SERVICE=postgres
```

**API key errors?**
```bash
# Verify API key is set
cat .env | grep OPENAI_API_KEY

# Should show: OPENAI_API_KEY=sk-...
# If empty, add your key to .env
```

**Need a fresh start?**
```bash
# Nuclear option: Remove everything
make clean

# Start fresh
make setup
```

### Step 11: Next Steps

1. **Read your developer guide** - Complete breakdown of your role
2. **Check your service README** - `services/your-service/README.md`
3. **Review cursor rules** - `.cursor/rules/person[1-5]-*/RULE.md`
4. **Start coding!** - Build your service according to the plan

**Remember:**
- Each service can be tested independently
- Use `make logs SERVICE=name` to debug
- Use `make rebuild SERVICE=name` after code changes
- All services expose `/healthz` endpoint
- Check `make help` for all available commands

---

## 📋 Prerequisites

- **Docker** & **Docker Compose** (v2.0+)
- **Python** 3.11+ (for local development)
- **Node.js** 18+ (for UI development)
- **Git**

**Install Docker:**
- macOS: `brew install docker docker-compose`
- Linux: Follow [Docker installation guide](https://docs.docker.com/get-docker/)
- Windows: Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

---

## 🏗️ Architecture

```
┌─────────────┐
│  Monitoring │───(error detected)──▶┌─────────┐     ┌──────────┐     ┌─────────┐     ┌──────────┐
│   Service   │                      │ Ingest  │────▶│ Decision │────▶│ Explain │────▶│ Executor │
└─────────────┘                      └────┬────┘     └─────┬─────┘     └─────────┘     └──────────┘
     │                                      │                │
     │                                      │                │
     │                                      ▼                ▼
     │                                ┌─────────┐     ┌──────────┐
     │                                │ Learner │◀────│   UI     │
     │                                └────┬────┘     └─────┬────┘
     │                                     │                │
     │                                     │                │
     │                                     ▼                ▼
     │                            ┌─────────────┐   ┌──────────────┐
     │                            │ PostgreSQL  │   │  react-force │
     │                            │(Knowledge   │   │  -graph-3d   │
     │                            │   Graph)    │   │ (3D Viz)     │
     │                            └─────┬───────┘   └──────────────┘
     │                                  │
     │                                  ▼
     │                            ┌─────────────┐
     │                            │  Weaviate   │
     │                            │  (Vectors)   │
     │                            └─────────────┘
     │
     └──(continuous logging)──▶ [Logs]
```

**Services:**
- **Ingest** (Port 8001): Single source of truth for all work items
- **Decision** (Port 8002): Core decision engine (the brain)
- **Learner** (Port 8003): Capability profiles and learning loop
- **Executor** (Port 8004): Executes decisions (creates Jira issues)
- **Explain** (Port 8005): Generates evidence bullets
- **Monitoring** (Port 8006): Simulates monitoring systems
- **Jira Simulator** (Port 8080): Full Jira API mock
- **UI** (Port 3000): Next.js frontend
- **PostgreSQL** (Port 5432): Knowledge graph storage
- **Weaviate** (Port 8081): Vector database

---

## 📁 Project Structure

```
goliath/
├── .cursor/
│   └── rules/                    # Cursor rules for each developer
├── apps/
│   └── ui/                       # Next.js 14 UI application
├── services/
│   ├── ingest/                   # Ingest service (Person 3)
│   ├── decision/                 # Decision engine (Person 1)
│   ├── learner/                  # Learner service (Person 2)
│   ├── executor/                 # Executor service (Person 4)
│   ├── explain/                  # Explain service (Person 4)
│   ├── monitoring/               # Monitoring service (Person 3)
│   └── jira-simulator/           # Jira API mock (Person 1)
├── contracts/
│   ├── types.ts                  # Shared TypeScript types
│   ├── openapi.yaml              # OpenAPI specification
│   └── llm_prompts.md            # LLM prompt patterns
├── infra/
│   └── docker-compose.yml        # Docker Compose configuration
├── scripts/
│   ├── setup.sh                  # One-command setup
│   └── seed_jira_data.py         # Jira Simulator seeding
├── docs/
│   ├── initial_plan.md           # Initial product plan
│   └── mvp_plan.md               # 72-hour hackathon plan
├── for_developer_docs/           # Developer documentation
│   ├── person1_*.md              # Person 1's guide
│   ├── person2_*.md              # Person 2's guide
│   ├── person3_*.md              # Person 3's guide
│   ├── person4_*.md              # Person 4's guide
│   └── person5_*.md              # Person 5's guide
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

---

## 🛠️ Development Setup

### Option 1: Full Setup (Recommended)

```bash
# Clone the repo
git clone https://github.com/vinayakvadoothker/goliath.git
cd goliath

# Run setup (does everything)
make setup
```

### Option 2: Manual Setup

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Start infrastructure (PostgreSQL, Weaviate)
make start-infra

# 3. Seed Jira Simulator
make seed

# 4. Start all services
make start

# 5. Install UI dependencies (if developing UI)
cd apps/ui && npm install && cd ../..
```

---

## 🎯 Service Ports

| Service | Port | URL |
|---------|------|-----|
| Ingest | 8001 | http://localhost:8001 |
| Decision | 8002 | http://localhost:8002 |
| Learner | 8003 | http://localhost:8003 |
| Executor | 8004 | http://localhost:8004 |
| Explain | 8005 | http://localhost:8005 |
| Monitoring | 8006 | http://localhost:8006 |
| Jira Simulator | 8080 | http://localhost:8080 |
| UI | 3000 | http://localhost:3000 |
| PostgreSQL | 5432 | localhost:5432 |
| Weaviate | 8081 | http://localhost:8081 |

---

## 🧪 Testing Your Service

Each service can be tested independently:

```bash
# Test Ingest service
cd services/ingest
./scripts/test_standalone.sh

# Test Decision service
cd services/decision
./scripts/test_standalone.sh

# Test Learner service
cd services/learner
./scripts/test_standalone.sh

# Test Executor service
cd services/executor
./scripts/test_standalone.sh

# Test Explain service
cd services/explain
./scripts/test_standalone.sh

# Test UI (local development)
cd apps/ui
npm install
npm run dev
```

**Or use make commands:**

```bash
# Check health of all services
make health

# View logs to debug
make logs SERVICE=your-service

# Rebuild and restart after changes
make rebuild SERVICE=your-service
```

---

## 📊 Monitoring Service (Auto-Start)

**The Monitoring Service automatically starts when the service starts** - no separate command needed!

### What It Does

The Monitoring Service simulates real monitoring/observability systems (like Datadog, PagerDuty):

1. **Continuously logs** normal messages (INFO, WARN, DEBUG) every 5 seconds
2. **Detects errors** with 5% probability per cycle (configurable)
3. **Creates WorkItems** via Ingest service when errors are detected
4. **LLM preprocesses** error logs (cleans, normalizes)
5. **Determines severity** (sev1, sev2, sev3) based on error type

### Auto-Start Behavior

**By default, the monitoring loop starts automatically** when the service starts:

```bash
# When you run make setup or make start, Monitoring Service:
# 1. Starts the container
# 2. Auto-starts the monitoring loop
# 3. Begins logging and detecting errors immediately
```

**No action needed** - it just works! You'll see logs like:
```
[INFO] Processing 123 requests/sec
[INFO] Cache hit rate: 95%
[ERROR] High error rate detected: 500 errors/sec on /api/v1/users
```

### Manual Control

You can start/stop the monitoring loop manually:

```bash
# Check if monitoring is running
curl http://localhost:8006/monitoring/status

# Start monitoring loop (if stopped)
curl -X POST http://localhost:8006/monitoring/start

# Stop monitoring loop (if running)
curl -X POST http://localhost:8006/monitoring/stop
```

### Configuration

Control auto-start behavior via environment variable:

```bash
# In .env or docker-compose.yml
MONITORING_AUTO_START=true   # Auto-start on service start (default)
MONITORING_AUTO_START=false  # Don't auto-start (must start manually)
```

### Viewing Monitoring Logs

```bash
# View Monitoring service logs
make logs SERVICE=monitoring

# You'll see:
# - Normal log messages every 5 seconds
# - Error detections when they occur
# - WorkItem creation confirmations
```

### What Happens When Errors Are Detected

1. **Error detected** → Monitoring Service generates realistic error message
2. **LLM preprocesses** → Cleans and normalizes the error log
3. **Creates WorkItem** → Calls Ingest service `POST /ingest/demo`
4. **Decision service routes** → Routes to appropriate person
5. **Executor creates Jira issue** → Creates ticket with assigned assignee

**The full flow happens automatically!** Just watch the logs to see incidents being created.

For complete documentation, see: [`services/monitoring/README.md`](services/monitoring/README.md)

---

---

## 📚 Developer Documentation

**Each developer has their own comprehensive guide:**

- **[Person 1: Decision + Infrastructure + Jira Simulator](for_developer_docs/person1_decision_infrastructure_jira.md)**
- **[Person 2: Learner Service](for_developer_docs/person2_learner.md)**
- **[Person 3: Ingest + Monitoring](for_developer_docs/person3_ingest_monitoring.md)**
- **[Person 4: Executor + Explain](for_developer_docs/person4_executor_explain.md)**
- **[Person 5: UI](for_developer_docs/person5_ui.md)**

**Each guide includes:**
- Complete role breakdown
- What to build and why
- API schemas and examples
- Database schemas
- Testing strategies
- Complete checklists

---

## 🛠️ Make Commands

**All commands use `make`. Here's the complete reference with explanations:**

### Setup & Development

```bash
# One-command setup (does everything)
# - Checks prerequisites (Docker, Python, etc.)
# - Creates .env file from .env.example
# - Creates all project directories
# - Starts PostgreSQL and Weaviate
# - Seeds Jira Simulator (200 people, 5000+ tickets)
# - Builds all Docker containers
# - Starts all services
# - Checks health of all services
make setup

# Start all services
# - Starts all Docker containers defined in docker-compose.yml
# - Services will be available at their respective ports
# - Use this after stopping services or restarting your machine
make start

# Stop all services
# - Gracefully stops all running containers
# - Preserves data in volumes (database, Weaviate data)
# - Use this when you're done developing for the day
make stop

# Restart all services
# - Stops and then starts all services
# - Useful when services are in a bad state
# - Faster than stop + start
make restart

# Show service status
# - Displays status of all containers (running, stopped, health)
# - Shows which ports are mapped
# - Quick way to see what's up and what's down
make status
```

### Logs & Monitoring

```bash
# View logs for all services
# - Shows logs from all containers simultaneously
# - Use Ctrl+C to exit
# - Useful for debugging cross-service issues
make logs

# View logs for specific service
# - Shows only logs from the specified service
# - Follows logs in real-time (like tail -f)
# - Examples:
make logs SERVICE=ingest        # View Ingest service logs
make logs SERVICE=decision      # View Decision service logs
make logs SERVICE=learner       # View Learner service logs
make logs SERVICE=executor      # View Executor service logs
make logs SERVICE=explain        # View Explain service logs
make logs SERVICE=monitoring    # View Monitoring service logs
make logs SERVICE=jira-simulator # View Jira Simulator logs
make logs SERVICE=ui            # View UI application logs
make logs SERVICE=postgres      # View PostgreSQL logs
make logs SERVICE=weaviate      # View Weaviate logs
```

### Building & Rebuilding

```bash
# Rebuild all services
# - Rebuilds Docker images for all services from scratch
# - Use when you've changed Dockerfiles or dependencies
# - Takes longer but ensures everything is fresh
make rebuild

# Rebuild specific service
# - Rebuilds only the specified service's Docker image
# - Restarts the service after rebuilding
# - Much faster than rebuilding everything
# - Use this after making code changes to a service
# Examples:
make rebuild SERVICE=ingest        # Rebuild Ingest service
make rebuild SERVICE=decision      # Rebuild Decision service
make rebuild SERVICE=learner       # Rebuild Learner service
make rebuild SERVICE=executor      # Rebuild Executor service
make rebuild SERVICE=explain       # Rebuild Explain service
make rebuild SERVICE=monitoring   # Rebuild Monitoring service
make rebuild SERVICE=jira-simulator # Rebuild Jira Simulator
make rebuild SERVICE=ui           # Rebuild UI application
```

### Data & Testing

```bash
# Seed Jira Simulator with data
# - Creates 200 users with different roles
# - Creates 5000+ closed tickets (last 90 days)
# - Creates 1000+ open tickets (current capacity)
# - Populates story points, priorities, severities
# - Only needs to run once (or when you want fresh data)
# - Automatically creates database tables if they don't exist
make seed

# Check health of all services
# - Tests /healthz endpoint on each service
# - Shows which services are responding
# - Quick way to verify everything is working
# - Services checked: ingest, decision, learner, executor, explain, monitoring, jira-simulator
make health

# Run all tests (when implemented)
# - Will run test suites for all services
# - Currently a placeholder for future test implementation
make test
```

### Cleanup

```bash
# Stop all services and remove volumes
# - Stops all containers
# - Removes all Docker volumes (database data, Weaviate data)
# - Use this when you want a completely fresh start
# - WARNING: This deletes all data! Use with caution.
# - After running this, you'll need to run 'make setup' again
make clean
```

### Help

```bash
# Show all available commands
# - Displays a formatted list of all make commands
# - Shows what each command does
# - Great reference when you forget a command name
make help
```

### Common Workflows

```bash
# Complete setup from scratch (first time)
# - Run this when you first clone the repo
# - Sets up everything automatically
make setup

# Daily development workflow
# - Start services in the morning
make start

# - Check if everything is healthy
make health

# - View logs when debugging
make logs SERVICE=your-service

# - Rebuild after code changes
make rebuild SERVICE=your-service

# - Stop services at end of day
make stop

# Debugging a specific service
# - View logs to see what's happening
make logs SERVICE=ingest

# - Rebuild if code changed
make rebuild SERVICE=ingest

# - Check if it's healthy
make health

# Fresh start (nuclear option)
# - Removes everything including data
make clean

# - Set up again from scratch
make setup
```

### Service-Specific Examples

```bash
# Working on Ingest service
make logs SERVICE=ingest          # See what's happening
make rebuild SERVICE=ingest        # Rebuild after code changes
curl http://localhost:8001/healthz  # Test health endpoint

# Working on Decision service
make logs SERVICE=decision        # Monitor decision making
make rebuild SERVICE=decision      # Apply code changes
curl http://localhost:8002/healthz  # Verify it's running

# Working on Learner service
make logs SERVICE=learner         # Watch learning loop
make rebuild SERVICE=learner       # Update learning logic
make seed                         # Re-seed if needed

# Working on UI
make logs SERVICE=ui              # See Next.js logs
make rebuild SERVICE=ui            # Rebuild after changes
# Or develop locally:
cd apps/ui && npm run dev
```

**Or use Docker Compose directly:**

```bash
# Start all services
docker-compose -f infra/docker-compose.yml up -d

# Stop all services
docker-compose -f infra/docker-compose.yml down

# View logs
docker-compose -f infra/docker-compose.yml logs -f [service-name]

# Check service status
docker-compose -f infra/docker-compose.yml ps
```

---

## 🔧 Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# LLM API (required)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2

# Or use Anthropic
ANTHROPIC_API_KEY=sk-...
ANTHROPIC_MODEL=claude-3-opus-20240229

# Database
POSTGRES_URL=postgresql://goliath:goliath@postgres:5432/goliath

# Weaviate
WEAVIATE_URL=http://weaviate:8080

# Service URLs (for service-to-service calls)
INGEST_SERVICE_URL=http://localhost:8001
DECISION_SERVICE_URL=http://localhost:8002
LEARNER_SERVICE_URL=http://localhost:8003
EXECUTOR_SERVICE_URL=http://localhost:8004
EXPLAIN_SERVICE_URL=http://localhost:8005
JIRA_SIMULATOR_URL=http://localhost:8080
```

---

## 🎨 Design System

**Colors:**
- Background: `#0a0a0a` (off-black)
- Text: `#f5f5f5` (off-white)
- Accents: `#3b82f6` (blue), `#10b981` (green), `#ef4444` (red)

**Philosophy:**
- Opinionated, not ambiguous
- Beautifully simple
- Every element has purpose and explanation
- No questions left unanswered

---

## 🧠 Core Features

### 1. Decision Engine
- Deterministic routing (same inputs → same outputs)
- Evidence-backed assignment
- Full audit trail

### 2. Learning Loop (THE Differentiator)
- System learns from outcomes
- Jira issue completed → fit_score increases
- Reassigned → fit_score decreases
- Next decision uses updated stats

### 3. Knowledge Graph
- 3D interactive visualization
- Nodes: Humans, WorkItems, Services, Decisions, Outcomes
- Edges: RESOLVED, TRANSFERRED, CO_WORKED
- Vector similarity search

### 4. Evidence-First UI
- Clear explanations for every decision
- Override workflow
- Full audit trail
- Beautiful, opinionated design

---

## 🚦 Health Checks

All services expose `/healthz` endpoint:

```bash
# Check all services
curl http://localhost:8001/healthz  # Ingest
curl http://localhost:8002/healthz  # Decision
curl http://localhost:8003/healthz  # Learner
curl http://localhost:8004/healthz  # Executor
curl http://localhost:8005/healthz  # Explain
curl http://localhost:8006/healthz  # Monitoring
curl http://localhost:8080/healthz  # Jira Simulator
```

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker ps

# Check logs
docker-compose -f infra/docker-compose.yml logs

# Rebuild containers
docker-compose -f infra/docker-compose.yml build --no-cache
```

### Database connection errors
```bash
# Check PostgreSQL is running
docker-compose -f infra/docker-compose.yml ps postgres

# Check connection string in .env
# Should be: postgresql://goliath:goliath@postgres:5432/goliath
```

### Port already in use
```bash
# Find process using port
lsof -i :8001  # Replace with your port

# Kill process or change port in docker-compose.yml
```

### LLM API errors
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Check API key is valid
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## 📖 API Documentation

**OpenAPI Spec:** `/contracts/openapi.yaml`

**Service-specific docs:**
- [Ingest API](services/ingest/README.md)
- [Decision API](services/decision/README.md)
- [Learner API](services/learner/README.md)
- [Executor API](services/executor/README.md)
- [Explain API](services/explain/README.md)
- [Jira Simulator API](services/jira-simulator/README.md)

---

## 🤝 Contributing

**Team Structure:**
- **Person 1**: Decision Engine + Infrastructure + Jira Simulator
- **Person 2**: Learner Service
- **Person 3**: Ingest + Monitoring
- **Person 4**: Executor + Explain
- **Person 5**: UI

**Workflow:**
1. Read your developer guide in `for_developer_docs/`
2. Follow your cursor rules in `.cursor/rules/`
3. Build your service independently (until Hour 48)
4. Test with standalone scripts
5. Integrate at Hour 48+

---

## 📝 License

Apache 2.0 License - see [LICENSE](LICENSE) file.

---

## 🎯 Success Criteria

**MVP Must Have:**
- ✅ Decision appears <2 seconds after incident ingest
- ✅ Evidence-first explanation (5-7 bullets)
- ✅ **Learning loop works**: Jira issue completed → fit_score increases → visible in stats
- ✅ **Next decision uses updated fit_score**: Replay shows different decision/confidence
- ✅ Override works and produces visible learning update
- ✅ Audit trace is inspectable and coherent

**The learning loop is THE core differentiator. If it doesn't work, demo fails.**

---

## 🆘 Getting Help

1. **Read your developer guide**: `for_developer_docs/person[1-5]_*.md`
2. **Check service README**: `services/[service-name]/README.md`
3. **Review cursor rules**: `.cursor/rules/person[1-5]-*/RULE.md`
4. **Check logs**: `docker-compose -f infra/docker-compose.yml logs [service-name]`

---

**Built with ❤️ for intelligent incident routing.**

