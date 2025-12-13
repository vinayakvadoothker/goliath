#!/bin/bash

# Standalone test script for Decision service
# Tests service without other services running

set -e

echo "🧪 Testing Decision Service (Standalone)"

# Start dependencies
docker-compose -f ../../infra/docker-compose.yml up -d postgres weaviate

# Wait for services
echo "⏳ Waiting for services..."
sleep 5

# Install test dependencies if needed
if ! python -c "import pytest" 2>/dev/null; then
    echo "📦 Installing test dependencies..."
    pip install pytest pytest-asyncio
fi

# Run tests
echo "🔍 Running tests..."
cd "$(dirname "$0")/.."
python -m pytest tests/test_standalone.py -v

echo "✅ Tests complete!"

