#!/bin/bash

# Standalone test script for Jira Simulator
# Tests JQL parser and endpoints without other services running

set -e

echo "🧪 Testing Jira Simulator (Standalone)"

# Start dependencies
docker-compose -f ../../infra/docker-compose.yml up -d postgres

# Wait for services
echo "⏳ Waiting for services..."
sleep 5

# Install test dependencies if needed
if ! python -c "import pytest" 2>/dev/null; then
    echo "📦 Installing test dependencies..."
    pip install pytest
fi

# Run tests
echo "🔍 Running tests..."
cd "$(dirname "$0")/.."
python -m pytest tests/test_jql_parser.py -v

echo "✅ Tests complete!"

