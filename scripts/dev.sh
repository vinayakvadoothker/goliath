#!/bin/bash

# Development helper script
# Usage: ./scripts/dev.sh [command]

COMMAND=${1:-"help"}

case $COMMAND in
  "start")
    echo "🚀 Starting all services..."
    docker-compose -f infra/docker-compose.yml up -d
    ;;
  "stop")
    echo "🛑 Stopping all services..."
    docker-compose -f infra/docker-compose.yml down
    ;;
  "restart")
    echo "🔄 Restarting all services..."
    docker-compose -f infra/docker-compose.yml restart
    ;;
  "logs")
    SERVICE=${2:-""}
    if [ -z "$SERVICE" ]; then
      docker-compose -f infra/docker-compose.yml logs -f
    else
      docker-compose -f infra/docker-compose.yml logs -f $SERVICE
    fi
    ;;
  "status")
    echo "📊 Service Status:"
    docker-compose -f infra/docker-compose.yml ps
    ;;
  "rebuild")
    SERVICE=${2:-""}
    if [ -z "$SERVICE" ]; then
      echo "🔨 Rebuilding all services..."
      docker-compose -f infra/docker-compose.yml build --no-cache
    else
      echo "🔨 Rebuilding $SERVICE..."
      docker-compose -f infra/docker-compose.yml build --no-cache $SERVICE
    fi
    ;;
  "seed")
    echo "🌱 Seeding Jira Simulator..."
    python3 scripts/seed_jira_data.py
    ;;
  "health")
    echo "🏥 Checking service health..."
    SERVICES=("ingest:8001" "decision:8002" "learner:8003" "executor:8004" "explain:8005" "monitoring:8006" "jira-simulator:8080")
    for service in "${SERVICES[@]}"; do
      name=$(echo $service | cut -d: -f1)
      port=$(echo $service | cut -d: -f2)
      if curl -f http://localhost:$port/healthz &>/dev/null; then
        echo "✅ $name is healthy"
      else
        echo "❌ $name is not responding"
      fi
    done
    ;;
  "help"|*)
    echo "Goliath Development Helper"
    echo ""
    echo "Usage: ./scripts/dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start      - Start all services"
    echo "  stop       - Stop all services"
    echo "  restart    - Restart all services"
    echo "  logs       - View logs (optionally for specific service)"
    echo "  status     - Show service status"
    echo "  rebuild    - Rebuild services (optionally specific service)"
    echo "  seed       - Seed Jira Simulator with data"
    echo "  health     - Check health of all services"
    echo "  help       - Show this help message"
    ;;
esac

