#!/bin/bash

# Stop all services
docker-compose -f infra/docker-compose.yml down

echo "✅ All services stopped!"

