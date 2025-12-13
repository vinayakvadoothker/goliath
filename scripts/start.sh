#!/bin/bash

# Start all services
docker-compose -f infra/docker-compose.yml up -d

echo "✅ All services started!"
echo ""
echo "🌐 Service URLs:"
echo "  Ingest:        http://localhost:8001"
echo "  Decision:      http://localhost:8002"
echo "  Learner:       http://localhost:8003"
echo "  Executor:      http://localhost:8004"
echo "  Explain:       http://localhost:8005"
echo "  Monitoring:    http://localhost:8006"
echo "  Jira Sim:      http://localhost:8080"
echo "  UI:            http://localhost:3000"

