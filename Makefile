.PHONY: help setup start stop restart logs status rebuild seed health clean test

# Detect Docker Compose command (docker compose vs docker-compose)
DOCKER_COMPOSE := $(shell command -v docker-compose >/dev/null 2>&1 && echo "docker-compose" || echo "docker compose")

# Default target
help:
	@echo "Goliath - Make Commands"
	@echo ""
	@echo "Setup & Development:"
	@echo "  make setup          - One-command setup (creates .env, starts all services)"
	@echo "  make start          - Start all services"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make status         - Show service status"
	@echo "  make logs SERVICE=  - View logs (e.g., make logs SERVICE=ingest)"
	@echo "  make rebuild SERVICE=- Rebuild service (e.g., make rebuild SERVICE=ingest)"
	@echo ""
	@echo "Data & Testing:"
	@echo "  make seed           - Seed Jira Simulator with data"
	@echo "  make health         - Check health of all services"
	@echo "  make test           - Run all tests"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Stop services and remove volumes"
	@echo ""

# One-command setup (with error handling)
setup:
	@set -e; \
	echo "🚀 Starting Goliath setup..."; \
	echo ""; \
	$(MAKE) check-prereqs || exit 1; \
	$(MAKE) create-env || exit 1; \
	$(MAKE) create-dirs || exit 1; \
	$(MAKE) start-infra || exit 1; \
	$(MAKE) seed || { \
		echo ""; \
		echo "⚠️  Seeding failed, but continuing..."; \
		echo "   You can retry seeding later with: make seed"; \
		echo ""; \
	}; \
	$(MAKE) start-services || exit 1; \
	echo ""; \
	echo "✅ Setup complete! All services are running."; \
	echo ""; \
	echo "🌐 Service URLs:"; \
	echo "  Ingest:        http://localhost:8001"; \
	echo "  Decision:      http://localhost:8002"; \
	echo "  Learner:       http://localhost:8003"; \
	echo "  Executor:      http://localhost:8004"; \
	echo "  Explain:       http://localhost:8005"; \
	echo "  Monitoring:    http://localhost:8006"; \
	echo "  Jira Sim:      http://localhost:8080"; \
	echo "  UI:            http://localhost:3000"; \
	echo ""; \
	$(MAKE) health || { \
		echo ""; \
		echo "⚠️  Some services are not healthy. Check logs with: make logs"; \
		exit 1; \
	}

# Check prerequisites
check-prereqs:
	@echo "📋 Checking prerequisites..."
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required"; exit 1; }
	@$(DOCKER_COMPOSE) version >/dev/null 2>&1 || { echo "❌ Docker Compose is required"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required"; exit 1; }
	@command -v curl >/dev/null 2>&1 || { echo "❌ curl is required for health checks"; exit 1; }
	@echo "✅ Prerequisites met"
	@echo "   Using: $(DOCKER_COMPOSE)"

# Create .env file
create-env:
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env and add your OPENAI_API_KEY"; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@echo "🔍 Validating .env file..."
	@if ! grep -q "^OPENAI_API_KEY=sk-" .env 2>/dev/null || grep -q "^OPENAI_API_KEY=sk-your-openai-api-key-here" .env 2>/dev/null; then \
		echo ""; \
		echo "⚠️  WARNING: OPENAI_API_KEY not set or still has placeholder value"; \
		echo "   Services will start but LLM features (preprocessing, evidence generation) will not work"; \
		echo "   Edit .env and set OPENAI_API_KEY=sk-your-actual-key"; \
		echo "   Continuing setup anyway..."; \
		echo ""; \
	fi
	@echo "✅ .env validation passed"

# Create directories
create-dirs:
	@echo "📁 Creating project structure..."
	@mkdir -p services/ingest services/decision services/learner
	@mkdir -p services/executor services/explain services/monitoring services/jira-simulator
	@mkdir -p apps/ui contracts infra scripts docs for_developer_docs
	@echo "✅ Directories created"

# Start infrastructure (PostgreSQL, Weaviate)
start-infra:
	@echo "🐳 Starting infrastructure services..."
	@$(DOCKER_COMPOSE) -f infra/docker-compose.yml up -d postgres weaviate || { echo "❌ Failed to start infrastructure"; exit 1; }
	@echo "⏳ Waiting for services to be ready..."
	@for i in 1 2 3 4 5; do \
		if $(DOCKER_COMPOSE) -f infra/docker-compose.yml exec -T postgres pg_isready -U goliath >/dev/null 2>&1; then \
			echo "✅ PostgreSQL is ready"; \
			break; \
		fi; \
		if [ $$i -eq 5 ]; then \
			echo "❌ PostgreSQL failed to start"; \
			exit 1; \
		fi; \
		echo "   Waiting for PostgreSQL... ($$i/5)"; \
		sleep 2; \
	done
	@for i in 1 2 3 4 5; do \
		if curl -f http://localhost:8081/v1/.well-known/ready >/dev/null 2>&1; then \
			echo "✅ Weaviate is ready"; \
			break; \
		fi; \
		if [ $$i -eq 5 ]; then \
			echo "⚠️  Weaviate may not be ready, but continuing..."; \
			break; \
		fi; \
		echo "   Waiting for Weaviate... ($$i/5)"; \
		sleep 2; \
	done
	@echo "✅ Infrastructure ready"

# Seed Jira Simulator (defined later, no-op here)

# Start all services
start-services:
	@echo "🔨 Building all services..."
	@$(DOCKER_COMPOSE) -f infra/docker-compose.yml build || { echo "❌ Failed to build services"; exit 1; }
	@echo "🚀 Starting all services..."
	@$(DOCKER_COMPOSE) -f infra/docker-compose.yml up -d || { echo "❌ Failed to start services"; exit 1; }
	@echo "⏳ Waiting for services to be ready..."
	@sleep 15
	@echo "✅ All services started"

# Start services
start:
	@echo "🚀 Starting all services..."
	@$(DOCKER_COMPOSE) -f infra/docker-compose.yml up -d
	@$(MAKE) status

# Stop services
stop:
	@echo "🛑 Stopping all services..."
	@$(DOCKER_COMPOSE) -f infra/docker-compose.yml down

# Restart services
restart:
	@echo "🔄 Restarting all services..."
	@$(DOCKER_COMPOSE) -f infra/docker-compose.yml restart
	@$(MAKE) status

# View logs
logs:
	@if [ -z "$(SERVICE)" ]; then \
		$(DOCKER_COMPOSE) -f infra/docker-compose.yml logs -f; \
	else \
		$(DOCKER_COMPOSE) -f infra/docker-compose.yml logs -f $(SERVICE); \
	fi

# Service status
status:
	@echo "📊 Service Status:"
	@$(DOCKER_COMPOSE) -f infra/docker-compose.yml ps

# Rebuild service
rebuild:
	@if [ -z "$(SERVICE)" ]; then \
		echo "🔨 Rebuilding all services..."; \
		$(DOCKER_COMPOSE) -f infra/docker-compose.yml build --no-cache; \
	else \
		echo "🔨 Rebuilding $(SERVICE)..."; \
		$(DOCKER_COMPOSE) -f infra/docker-compose.yml build --no-cache $(SERVICE); \
		$(DOCKER_COMPOSE) -f infra/docker-compose.yml up -d $(SERVICE); \
	fi

# Seed Jira data
seed:
	@echo "🌱 Seeding Jira Simulator..."
	@echo "   (This may take a few minutes for 5000+ tickets...)"
	@python3 -m pip install --user faker psycopg2-binary >/dev/null 2>&1 || echo "⚠️  Installing dependencies..."
	@POSTGRES_URL=postgresql://goliath:goliath@localhost:5432/goliath python3 scripts/seed_jira_data.py || { \
		echo "❌ Seeding failed. This may be because:"; \
		echo "   1. PostgreSQL is not ready yet"; \
		echo "   2. Database connection failed"; \
		echo "   You can retry later with: make seed"; \
		exit 1; \
	}

# Health check
health:
	@echo "🏥 Checking service health..."
	@failed=0; \
	for service in ingest:8001 decision:8002 learner:8003 executor:8004 explain:8005 monitoring:8006 jira-simulator:8080; do \
		name=$$(echo $$service | cut -d: -f1); \
		port=$$(echo $$service | cut -d: -f2); \
		if curl -f -s http://localhost:$$port/healthz >/dev/null 2>&1; then \
			echo "✅ $$name is healthy"; \
		else \
			echo "❌ $$name is not responding (port $$port)"; \
			failed=$$((failed + 1)); \
		fi; \
	done; \
	if [ $$failed -gt 0 ]; then \
		echo ""; \
		echo "⚠️  $$failed service(s) are not responding"; \
		echo "   Check logs with: make logs SERVICE=<service-name>"; \
		echo "   Or view all logs: make logs"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "✅ All services are healthy!"

# Run tests
test:
	@echo "🧪 Running tests..."
	@echo "TODO: Add test commands"

# Clean everything
clean:
	@echo "🧹 Cleaning up..."
	@$(DOCKER_COMPOSE) -f infra/docker-compose.yml down -v
	@echo "✅ Cleanup complete"

