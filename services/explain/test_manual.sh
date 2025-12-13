#!/bin/bash

# Manual test script for Explain service
# Tests the service with curl commands

set -e

EXPLAIN_URL="${EXPLAIN_URL:-http://localhost:8005}"

echo "🧪 Testing Explain Service"
echo "=========================="
echo ""

# Check if service is running
echo "1. Checking health..."
curl -f "${EXPLAIN_URL}/healthz" || {
    echo "❌ Explain service is not running at ${EXPLAIN_URL}"
    echo "   Start it with: docker-compose -f ../../infra/docker-compose.yml up -d explain"
    exit 1
}
echo "✅ Service is healthy"
echo ""

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set. LLM features will not work."
    echo "   Set it with: export OPENAI_API_KEY=sk-..."
    echo ""
fi

# Test explainDecision endpoint
echo "2. Testing explainDecision endpoint..."
RESPONSE=$(curl -s -X POST "${EXPLAIN_URL}/explainDecision" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: test-$(date +%s)" \
  -d '{
    "decision_id": "test-decision-123",
    "work_item": {
      "id": "test-work-item-123",
      "service": "api",
      "severity": "sev2",
      "description": "API endpoint returning 500 errors",
      "type": "incident"
    },
    "primary_human_id": "human-1",
    "primary_features": {
      "human_id": "human-1",
      "display_name": "Alice Engineer",
      "fit_score": 0.85,
      "resolves_count": 12,
      "transfers_count": 1,
      "last_resolved_at": "2024-01-15T10:30:00Z",
      "on_call": true,
      "pages_7d": 0,
      "active_items": 2,
      "similar_incident_score": 0.92
    },
    "backup_human_ids": ["human-2"],
    "backup_features": [
      {
        "human_id": "human-2",
        "display_name": "Bob Engineer",
        "fit_score": 0.72,
        "resolves_count": 8,
        "transfers_count": 2,
        "last_resolved_at": "2024-01-10T14:20:00Z",
        "on_call": false,
        "pages_7d": 3,
        "active_items": 5,
        "similar_incident_score": 0.75
      }
    ],
    "constraints_checked": [
      {
        "name": "capacity",
        "passed": true,
        "reason": "Within story point limit"
      },
      {
        "name": "availability",
        "passed": true,
        "reason": "On call and available"
      }
    ]
  }')

echo "Response:"
echo "$RESPONSE" | jq '.' || echo "$RESPONSE"
echo ""

# Check if response contains evidence
if echo "$RESPONSE" | grep -q "evidence"; then
    EVIDENCE_COUNT=$(echo "$RESPONSE" | jq '.evidence | length' 2>/dev/null || echo "0")
    echo "✅ Evidence generated successfully"
    echo "   Evidence bullets: $EVIDENCE_COUNT"
    
    if echo "$RESPONSE" | grep -q "why_not_next_best"; then
        echo "✅ Why not next best comparison included"
    fi
    
    if echo "$RESPONSE" | grep -q "constraints"; then
        echo "✅ Constraints summary included"
    fi
else
    echo "❌ Unexpected response format"
    exit 1
fi

echo ""
echo "✅ All tests passed!"
