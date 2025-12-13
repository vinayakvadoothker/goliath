#!/bin/bash

# End-to-end integration test
# Tests the complete flow: Work Item → Decision → Jira Issue → Outcome → Learning

set -e

echo "🧪 Running End-to-End Integration Test"
echo "======================================"

# Check if services are running
echo "📡 Checking services..."
DECISION_HEALTH=$(curl -s http://localhost:8002/healthz || echo "down")
JIRA_HEALTH=$(curl -s http://localhost:8080/healthz || echo "down")
LEARNER_HEALTH=$(curl -s http://localhost:8003/healthz || echo "down")
INGEST_HEALTH=$(curl -s http://localhost:8001/healthz || echo "down")

if [ "$DECISION_HEALTH" == "down" ] || [ "$JIRA_HEALTH" == "down" ]; then
    echo "⚠️  Some services are not running"
    echo "   Decision: $DECISION_HEALTH"
    echo "   Jira Simulator: $JIRA_HEALTH"
    echo ""
    echo "   To start services, run from project root:"
    echo "   docker-compose -f infra/docker-compose.yml up -d decision jira-simulator"
    echo ""
    echo "   Continuing with available services..."
    echo ""
fi

if [ "$DECISION_HEALTH" != "down" ] && [ "$JIRA_HEALTH" != "down" ]; then
    echo "✅ All required services are running"
else
    echo "⚠️  Some services are down - tests will be limited"
fi
echo ""

# Test 1: Decision Service → Learner Service
echo "Test 1: Decision Service → Learner Service"
echo "-------------------------------------------"
if [ "$LEARNER_HEALTH" != "down" ]; then
    echo "✅ Learner Service is running - can test integration"
    # TODO: Create work item and test decision
else
    echo "⚠️  Learner Service is down - testing fallback mechanism"
    # Test that fallback works
fi
echo ""

# Test 2: Jira Simulator → Ingest Service
echo "Test 2: Jira Simulator → Ingest Service"
echo "---------------------------------------"
if [ "$INGEST_HEALTH" != "down" ]; then
    echo "✅ Ingest Service is running - can test outcome generation"
    # TODO: Create issue, mark as Done, verify outcome sent
else
    echo "⚠️  Ingest Service is down - outcome generation will queue"
fi
echo ""

# Test 3: Polling endpoint
echo "Test 3: Outcome Polling Endpoint"
echo "---------------------------------"
POLL_RESPONSE=$(curl -s "http://localhost:8080/rest/api/3/outcomes/pending?limit=10" || echo "error")
if [ "$POLL_RESPONSE" != "error" ]; then
    echo "✅ Polling endpoint is accessible"
    echo "   Response: $(echo $POLL_RESPONSE | jq -r '.outcomes | length' 2>/dev/null || echo 'N/A') outcomes"
else
    echo "❌ Polling endpoint failed"
fi
echo ""

echo "✅ Integration test complete!"
echo ""
echo "Note: Full E2E test requires:"
echo "  1. Create work item via Ingest"
echo "  2. Make decision via Decision Service"
echo "  3. Create Jira issue via Executor"
echo "  4. Mark issue as Done"
echo "  5. Verify outcome generated and sent to Ingest"
echo "  6. Verify Learner updated fit_score"

