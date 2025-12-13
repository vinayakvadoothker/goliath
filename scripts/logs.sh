#!/bin/bash

# View logs for a service
# Usage: ./scripts/logs.sh [service-name]
# Example: ./scripts/logs.sh ingest

SERVICE=${1:-""}

if [ -z "$SERVICE" ]; then
    echo "Usage: ./scripts/logs.sh [service-name]"
    echo ""
    echo "Available services:"
    echo "  - ingest"
    echo "  - decision"
    echo "  - learner"
    echo "  - executor"
    echo "  - explain"
    echo "  - monitoring"
    echo "  - jira-simulator"
    echo "  - ui"
    echo "  - postgres"
    echo "  - weaviate"
    exit 1
fi

docker-compose -f infra/docker-compose.yml logs -f $SERVICE

