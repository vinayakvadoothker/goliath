#!/bin/bash

echo "=========================================="
echo "Testing Full Flow: Simulate Error → Jira Ticket"
echo "=========================================="
echo ""

# Step 1: Simulate error via Control Center API (simulating button click)
echo "1. Simulating error via Control Center..."
ERROR_RESPONSE=$(curl -s -X POST http://localhost:8001/ingest/demo \
  -H "Content-Type: application/json" \
  -d '{
    "service": "api-service",
    "severity": "sev1",
    "description": "High error rate detected: 450 errors/sec on /api/v1/users endpoint",
    "type": "incident",
    "raw_log": "ERROR: High error rate detected: 450 errors/sec on /api/v1/users endpoint"
  }')

WORK_ITEM_ID=$(echo "$ERROR_RESPONSE" | jq -r '.work_item_id // empty' 2>/dev/null)

if [ -z "$WORK_ITEM_ID" ] || [ "$WORK_ITEM_ID" = "null" ]; then
    echo "❌ Failed to create work item"
    echo "$ERROR_RESPONSE"
    exit 1
fi

echo "✅ Work Item created: $WORK_ITEM_ID"
echo ""

# Step 2: Wait for decision (orchestration should happen automatically)
echo "2. Waiting for decision (automatic orchestration)..."
sleep 3

DECISION=$(curl -s "http://localhost:8002/decisions/$WORK_ITEM_ID" 2>/dev/null)
DECISION_ID=$(echo "$DECISION" | jq -r '.id // empty' 2>/dev/null)
PRIMARY_HUMAN=$(echo "$DECISION" | jq -r '.primary_human_id // empty' 2>/dev/null)

if [ -z "$DECISION_ID" ] || [ "$DECISION_ID" = "null" ]; then
    echo "⚠️  Decision not found yet, checking if it's being processed..."
    sleep 2
    DECISION=$(curl -s "http://localhost:8002/decisions/$WORK_ITEM_ID" 2>/dev/null)
    DECISION_ID=$(echo "$DECISION" | jq -r '.id // empty' 2>/dev/null)
    PRIMARY_HUMAN=$(echo "$DECISION" | jq -r '.primary_human_id // empty' 2>/dev/null)
fi

if [ -n "$DECISION_ID" ] && [ "$DECISION_ID" != "null" ]; then
    echo "✅ Decision made: $DECISION_ID"
    echo "   Primary Assignee: $PRIMARY_HUMAN"
    echo ""
else
    echo "❌ Decision not found"
    echo "$DECISION"
    exit 1
fi

# Step 3: Check for Jira issue (executor should create it automatically)
echo "3. Checking for Jira issue (automatic execution)..."
sleep 2

JIRA_ISSUES=$(curl -s "http://localhost:8004/executed_actions?decision_id=$DECISION_ID" 2>/dev/null)
JIRA_KEY=$(echo "$JIRA_ISSUES" | jq -r '.[0].jira_issue_key // empty' 2>/dev/null)

if [ -z "$JIRA_KEY" ] || [ "$JIRA_KEY" = "null" ]; then
    echo "⚠️  Jira issue not found yet, waiting..."
    sleep 3
    JIRA_ISSUES=$(curl -s "http://localhost:8004/executed_actions?decision_id=$DECISION_ID" 2>/dev/null)
    JIRA_KEY=$(echo "$JIRA_ISSUES" | jq -r '.[0].jira_issue_key // empty' 2>/dev/null)
fi

if [ -n "$JIRA_KEY" ] && [ "$JIRA_KEY" != "null" ]; then
    echo "✅ Jira issue created: $JIRA_KEY"
    echo ""
    
    # Verify in database
    JIRA_VERIFY=$(docker exec goliath-postgres psql -U goliath -d goliath -t -c "SELECT jira_issue_key FROM executed_actions WHERE decision_id = '$DECISION_ID';" 2>/dev/null | tr -d ' ')
    if [ -n "$JIRA_VERIFY" ]; then
        echo "✅ Verified in database: $JIRA_VERIFY"
    fi
else
    echo "❌ Jira issue not created"
    echo "$JIRA_ISSUES"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Full Flow Test: PASSED"
echo "=========================================="
echo "Work Item: $WORK_ITEM_ID"
echo "Decision: $DECISION_ID"
echo "Assignee: $PRIMARY_HUMAN"
echo "Jira Issue: $JIRA_KEY"
echo ""
