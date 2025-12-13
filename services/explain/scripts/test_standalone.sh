#!/bin/bash

# Standalone test script for Explain service
# Tests service without other services running

set -e

echo "🧪 Testing Explain Service (Standalone)"

# No dependencies needed (just LLM API)

# Run tests
echo "🔍 Running tests..."
pytest tests/test_standalone.py -v

echo "✅ Tests complete!"

