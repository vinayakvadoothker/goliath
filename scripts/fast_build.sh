#!/bin/bash
# Fast Docker build script using BuildKit for better caching
# Usage: ./scripts/fast_build.sh [service1] [service2] ...

set -e

# Enable BuildKit for faster builds with cache mounts
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Get services from args, or default to all
SERVICES="${@:-decision learner ingest jira-simulator}"

echo "🚀 Fast building services with BuildKit: $SERVICES"
echo "   (Using cache mounts - pip packages cached between builds)"

cd "$(dirname "$0")/.."

docker-compose -f infra/docker-compose.yml build $SERVICES

echo "✅ Build complete!"

