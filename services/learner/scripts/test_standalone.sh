#!/bin/bash

# Standalone test script for Learner service
# Tests service without other services running

set -e

echo "🧪 Testing Learner Service (Standalone)"

# Start dependencies
docker-compose -f ../../../infra/docker-compose.yml up -d postgres weaviate jira-simulator

# Wait for services
echo "⏳ Waiting for services..."
sleep 10

# Run tests
echo "🔍 Running tests..."
pytest tests/test_standalone.py -v

echo "✅ Tests complete!"

