.PHONY: help setup start stop restart logs status rebuild seed health clean test

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

# One-command setup
setup: check-prereqs create-env create-dirs start-infra seed start-services
	@echo ""
	@echo "✅ Setup complete! All services are running."
	@echo ""
	@echo "🌐 Service URLs:"
	@echo "  Ingest:        http://localhost:8001"
	@echo "  Decision:      http://localhost:8002"
	@echo "  Learner:       http://localhost:8003"
	@echo "  Executor:      http://localhost:8004"
	@echo "  Explain:       http://localhost:8005"
	@echo "  Monitoring:    http://localhost:8006"
	@echo "  Jira Sim:      http://localhost:8080"
	@echo "  UI:            http://localhost:3000"
	@echo ""
	@make health

# Check prerequisites
check-prereqs:
	@echo "📋 Checking prerequisites..."
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1 || { echo "❌ Docker Compose is required"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required"; exit 1; }
	@echo "✅ Prerequisites met"

# Create .env file
create-env:
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env and add your OPENAI_API_KEY"; \
	else \
		echo "✅ .env file already exists"; \
	fi

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
	@docker-compose -f infra/docker-compose.yml up -d postgres weaviate
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "✅ Infrastructure ready"

# Seed Jira Simulator (defined later, no-op here)

# Start all services
start-services:
	@echo "🔨 Building all services..."
	@docker-compose -f infra/docker-compose.yml build
	@echo "🚀 Starting all services..."
	@docker-compose -f infra/docker-compose.yml up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 15
	@echo "✅ All services started"

# Start services
start:
	@echo "🚀 Starting all services..."
	@docker-compose -f infra/docker-compose.yml up -d
	@make status

# Stop services
stop:
	@echo "🛑 Stopping all services..."
	@docker-compose -f infra/docker-compose.yml down

# Restart services
restart:
	@echo "🔄 Restarting all services..."
	@docker-compose -f infra/docker-compose.yml restart
	@make status

# View logs
logs:
	@if [ -z "$(SERVICE)" ]; then \
		docker-compose -f infra/docker-compose.yml logs -f; \
	else \
		docker-compose -f infra/docker-compose.yml logs -f $(SERVICE); \
	fi

# Service status
status:
	@echo "📊 Service Status:"
	@docker-compose -f infra/docker-compose.yml ps

# Rebuild service
rebuild:
	@if [ -z "$(SERVICE)" ]; then \
		echo "🔨 Rebuilding all services..."; \
		docker-compose -f infra/docker-compose.yml build --no-cache; \
	else \
		echo "🔨 Rebuilding $(SERVICE)..."; \
		docker-compose -f infra/docker-compose.yml build --no-cache $(SERVICE); \
		docker-compose -f infra/docker-compose.yml up -d $(SERVICE); \
	fi

# Seed Jira data
seed:
	@echo "🌱 Seeding Jira Simulator..."
	@python3 -m pip install --user faker psycopg2-binary >/dev/null 2>&1 || echo "⚠️  Installing dependencies..."
	@python3 scripts/seed_jira_data.py

# Health check
health:
	@echo "🏥 Checking service health..."
	@for service in ingest:8001 decision:8002 learner:8003 executor:8004 explain:8005 monitoring:8006 jira-simulator:8080; do \
		name=$$(echo $$service | cut -d: -f1); \
		port=$$(echo $$service | cut -d: -f2); \
		if curl -f http://localhost:$$port/healthz >/dev/null 2>&1; then \
			echo "✅ $$name is healthy"; \
		else \
			echo "❌ $$name is not responding"; \
		fi; \
	done

# Run tests
test:
	@echo "🧪 Running tests..."
	@echo "TODO: Add test commands"

# Clean everything
clean:
	@echo "🧹 Cleaning up..."
	@docker-compose -f infra/docker-compose.yml down -v
	@echo "✅ Cleanup complete"

