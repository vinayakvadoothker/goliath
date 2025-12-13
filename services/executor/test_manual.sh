#!/bin/bash

# Manual test script for Executor service
# Tests the service with curl commands

set -e

EXECUTOR_URL="${EXECUTOR_URL:-http://localhost:8004}"
JIRA_SIMULATOR_URL="${JIRA_SIMULATOR_URL:-http://localhost:8080}"

echo "🧪 Testing Executor Service"
echo "=========================="
echo ""

# Check if service is running
echo "1. Checking health..."
curl -f "${EXECUTOR_URL}/healthz" || {
    echo "❌ Executor service is not running at ${EXECUTOR_URL}"
    echo "   Start it with: docker-compose -f ../../infra/docker-compose.yml up -d executor"
    exit 1
}
echo "✅ Service is healthy"
echo ""

# Check if Jira Simulator is running
echo "2. Checking Jira Simulator..."
curl -f "${JIRA_SIMULATOR_URL}/healthz" || {
    echo "❌ Jira Simulator is not running at ${JIRA_SIMULATOR_URL}"
    echo "   Start it with: docker-compose -f ../../infra/docker-compose.yml up -d jira-simulator"
    exit 1
}
echo "✅ Jira Simulator is healthy"
echo ""

# Test executeDecision endpoint
echo "3. Testing executeDecision endpoint..."
RESPONSE=$(curl -s -X POST "${EXECUTOR_URL}/executeDecision" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: test-$(date +%s)" \
  -d '{
    "decision_id": "test-decision-123",
    "work_item_id": "test-work-item-123",
    "primary_human_id": "human-1",
    "backup_human_ids": ["human-2", "human-3"],
    "evidence": [
      {
        "type": "recent_resolution",
        "text": "Resolved 3 similar incidents in the last 7 days",
        "time_window": "last 7 days",
        "source": "Learner stats"
      }
    ],
    "work_item": {
      "service": "api",
      "severity": "sev2",
      "description": "Test incident: API endpoint returning 500 errors",
      "story_points": 3
    }
  }')

echo "Response:"
echo "$RESPONSE" | jq '.' || echo "$RESPONSE"
echo ""

# Check if response contains jira_issue_key
if echo "$RESPONSE" | grep -q "jira_issue_key"; then
    echo "✅ Jira issue created successfully"
    JIRA_KEY=$(echo "$RESPONSE" | jq -r '.jira_issue_key // empty')
    if [ -n "$JIRA_KEY" ]; then
        echo "   Jira Issue Key: $JIRA_KEY"
    else
        echo "   ⚠️  Fallback used (Jira issue creation failed, stored in DB)"
    fi
else
    echo "❌ Unexpected response format"
    exit 1
fi

echo ""
echo "✅ All tests passed!"
