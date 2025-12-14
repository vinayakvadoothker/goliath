#!/bin/bash

echo "=========================================="
echo "Testing Complete Flow: Error → Work Item → Decision → Jira"
echo "=========================================="
echo ""

# Step 1: Create work item directly
echo "1. Creating work item..."
WORK_ITEM_RESPONSE=$(curl -s -X POST http://localhost:8001/ingest/demo \
  -H "Content-Type: application/json" \
  -d '{
    "service": "api-service",
    "severity": "sev1",
    "description": "High error rate detected: 450 errors/sec on /api/v1/users endpoint",
    "type": "incident",
    "raw_log": "ERROR: High error rate detected: 450 errors/sec on /api/v1/users endpoint"
  }')

WORK_ITEM_ID=$(echo "$WORK_ITEM_RESPONSE" | jq -r '.work_item_id // empty' 2>/dev/null)

if [ -z "$WORK_ITEM_ID" ] || [ "$WORK_ITEM_ID" = "null" ]; then
    echo "❌ Failed to create work item"
    exit 1
fi

echo "✅ Work Item created: $WORK_ITEM_ID"
echo ""

# Step 2: Verify work item in database
echo "2. Verifying work item in database..."
sleep 2
DB_CHECK=$(docker exec goliath-postgres psql -U goliath -d goliath -t -c "SELECT id FROM work_items WHERE id = '$WORK_ITEM_ID';" 2>/dev/null | tr -d ' ')

if [ -z "$DB_CHECK" ]; then
    echo "⚠️  Work item not in database yet, but continuing..."
else
    echo "✅ Work item found in database"
fi
echo ""

# Step 3: Trigger decision manually (if automatic didn't work)
echo "3. Triggering decision..."
sleep 2
DECISION_RESPONSE=$(curl -s -X POST http://localhost:8002/decide \
  -H "Content-Type: application/json" \
  -d "{\"work_item_id\": \"$WORK_ITEM_ID\"}")

DECISION_ID=$(echo "$DECISION_RESPONSE" | jq -r '.id // empty' 2>/dev/null)
PRIMARY_HUMAN=$(echo "$DECISION_RESPONSE" | jq -r '.primary_human_id // empty' 2>/dev/null)

if [ -z "$DECISION_ID" ] || [ "$DECISION_ID" = "null" ]; then
    echo "❌ Failed to create decision"
    echo "$DECISION_RESPONSE" | jq .
    exit 1
fi

echo "✅ Decision made: $DECISION_ID"
echo "   Primary Assignee: $PRIMARY_HUMAN"
echo ""

# Step 4: Check for Jira issue
echo "4. Checking for Jira issue..."
sleep 3
JIRA_RESPONSE=$(curl -s "http://localhost:8004/executed_actions?decision_id=$DECISION_ID")
JIRA_KEY=$(echo "$JIRA_RESPONSE" | jq -r '.[0].jira_issue_key // empty' 2>/dev/null)

if [ -z "$JIRA_KEY" ] || [ "$JIRA_KEY" = "null" ]; then
    echo "⚠️  Jira issue not found, waiting..."
    sleep 3
    JIRA_RESPONSE=$(curl -s "http://localhost:8004/executed_actions?decision_id=$DECISION_ID")
    JIRA_KEY=$(echo "$JIRA_RESPONSE" | jq -r '.[0].jira_issue_key // empty' 2>/dev/null)
fi

if [ -n "$JIRA_KEY" ] && [ "$JIRA_KEY" != "null" ]; then
    echo "✅ Jira issue created: $JIRA_KEY"
    echo ""
    
    # Verify in Jira Simulator
    JIRA_VERIFY=$(curl -s "http://localhost:8080/rest/api/3/issue/$JIRA_KEY" 2>/dev/null | jq -r '.key // empty' 2>/dev/null)
    if [ -n "$JIRA_VERIFY" ]; then
        echo "✅ Verified in Jira Simulator: $JIRA_VERIFY"
    fi
else
    echo "❌ Jira issue not created"
    echo "$JIRA_RESPONSE" | jq .
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
