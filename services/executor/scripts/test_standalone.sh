#!/bin/bash

# Standalone test script for Executor service
# Tests service without other services running

set -e

echo "🧪 Testing Executor Service (Standalone)"

# Start dependencies
docker-compose -f ../../../infra/docker-compose.yml up -d postgres jira-simulator

# Wait for services
echo "⏳ Waiting for services..."
sleep 5

# Run tests
echo "🔍 Running tests..."
pytest tests/test_standalone.py -v

echo "✅ Tests complete!"

