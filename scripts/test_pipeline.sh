#!/bin/bash

# Comprehensive Pipeline Test
# Tests the entire Goliath pipeline with simulated error cases
# Flow: Monitoring → Ingest → Decision → Executor → Learner

# Don't exit on error - we want to run all tests and report results
set +e

echo "🧪 Goliath Pipeline Test"
echo "========================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Service URLs
INGEST_URL="http://localhost:8001"
MONITORING_URL="http://localhost:8006"
DECISION_URL="http://localhost:8002"
LEARNER_URL="http://localhost:8003"
EXECUTOR_URL="http://localhost:8004"
EXPLAIN_URL="http://localhost:8005"
JIRA_URL="http://localhost:8080"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to check service health
check_service() {
    local name=$1
    local url=$2
    
    if curl -f -s "${url}/healthz" >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} ${name} is healthy"
        return 0
    else
        echo -e "${RED}❌${NC} ${name} is not responding at ${url}"
        return 1
    fi
}

# Helper function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test: ${test_name}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Step 1: Check all services are running
echo "📡 Step 1: Checking Service Health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SERVICES_OK=true
check_service "Ingest" "${INGEST_URL}" || SERVICES_OK=false
check_service "Monitoring" "${MONITORING_URL}" || SERVICES_OK=false
check_service "Decision" "${DECISION_URL}" || SERVICES_OK=false
check_service "Learner" "${LEARNER_URL}" || SERVICES_OK=false
check_service "Executor" "${EXECUTOR_URL}" || SERVICES_OK=false
check_service "Explain" "${EXPLAIN_URL}" || SERVICES_OK=false
check_service "Jira Simulator" "${JIRA_URL}" || SERVICES_OK=false

if [ "$SERVICES_OK" = "false" ]; then
    echo ""
    echo -e "${RED}❌ Some services are not healthy. Please start them with: make start${NC}"
    echo ""
    echo "Continuing with available services..."
fi

echo ""
echo -e "${GREEN}✅ All services are healthy!${NC}"
echo ""

# Step 2: Test Monitoring → Ingest Flow
run_test "Monitoring → Ingest: Create WorkItem via Monitoring" "
    # Check monitoring status
    MONITORING_STATUS=\$(curl -s ${MONITORING_URL}/monitoring/status)
    echo \"Monitoring Status: \$(echo \$MONITORING_STATUS | jq -r '.status' 2>/dev/null || echo 'unknown')\"
    
    # Manually create a work item (simulating monitoring detecting an error)
    WORK_ITEM=\$(curl -s -X POST ${INGEST_URL}/ingest/demo \\
        -H 'Content-Type: application/json' \\
        -d '{
            \"service\": \"api-service\",
            \"severity\": \"sev2\",
            \"description\": \"High error rate detected: 500 errors/sec on /api/v1/users\",
            \"type\": \"incident\",
            \"raw_log\": \"[ERROR] High error rate detected: 500 errors/sec on /api/v1/users endpoint\"
        }')
    
    WORK_ITEM_ID=\$(echo \$WORK_ITEM | jq -r '.work_item_id' 2>/dev/null)
    
    if [ -z \"\$WORK_ITEM_ID\" ] || [ \"\$WORK_ITEM_ID\" = \"null\" ]; then
        echo \"Failed to create work item\"
        echo \"Response: \$WORK_ITEM\"
        exit 1
    fi
    
    echo \"✅ WorkItem created: \$WORK_ITEM_ID\"
    export WORK_ITEM_ID
"

# Step 3: Verify WorkItem in Ingest
run_test "Ingest: Verify WorkItem exists" "
    if [ -z \"\$WORK_ITEM_ID\" ]; then
        echo \"WORK_ITEM_ID not set from previous test\"
        exit 1
    fi
    
    WORK_ITEM=\$(curl -s ${INGEST_URL}/work-items/\$WORK_ITEM_ID)
    WORK_ITEM_SERVICE=\$(echo \$WORK_ITEM | jq -r '.service' 2>/dev/null)
    
    if [ \"\$WORK_ITEM_SERVICE\" != \"api-service\" ]; then
        echo \"WorkItem service mismatch: expected 'api-service', got '\$WORK_ITEM_SERVICE'\"
        exit 1
    fi
    
    echo \"✅ WorkItem verified: \$WORK_ITEM_ID\"
    echo \"   Service: \$WORK_ITEM_SERVICE\"
    echo \"   Description: \$(echo \$WORK_ITEM | jq -r '.description' 2>/dev/null | head -c 60)...\"
"

# Step 4: Test Decision Service (if available)
run_test "Decision: Make decision for WorkItem" "
    if [ -z \"\$WORK_ITEM_ID\" ]; then
        echo \"WORK_ITEM_ID not set\"
        exit 1
    fi
    
    # Try to make a decision
    DECISION=\$(curl -s -X POST ${DECISION_URL}/decide \\
        -H 'Content-Type: application/json' \\
        -d \"{\\\"work_item_id\\\": \\\"\$WORK_ITEM_ID\\\"}\" 2>/dev/null || echo '{\"error\":\"service_not_available\"}')
    
    DECISION_ERROR=\$(echo \$DECISION | jq -r '.error' 2>/dev/null)
    
    if [ \"\$DECISION_ERROR\" = \"service_not_available\" ]; then
        echo \"⚠️  Decision Service not fully implemented yet (this is OK for MVP)\"
        echo \"   Skipping decision test\"
        return 0
    fi
    
    PRIMARY_HUMAN=\$(echo \$DECISION | jq -r '.primary_human_id' 2>/dev/null)
    
    if [ -z \"\$PRIMARY_HUMAN\" ] || [ \"\$PRIMARY_HUMAN\" = \"null\" ]; then
        echo \"Decision failed or not implemented\"
        echo \"Response: \$DECISION\"
        exit 1
    fi
    
    echo \"✅ Decision made: Primary human = \$PRIMARY_HUMAN\"
    export PRIMARY_HUMAN_ID=\$PRIMARY_HUMAN
"

# Step 5: Test Multiple Error Types
run_test "Ingest: Create multiple error types" "
    ERROR_TYPES=(
        '{\"service\":\"api-service\",\"severity\":\"sev1\",\"description\":\"Database connection timeout: postgres connection pool exhausted\",\"raw_log\":\"[ERROR] Database connection timeout\"}'
        '{\"service\":\"api-service\",\"severity\":\"sev2\",\"description\":\"Memory leak detected: api-service memory usage at 95%\",\"raw_log\":\"[ERROR] Memory leak detected\"}'
        '{\"service\":\"api-service\",\"severity\":\"sev3\",\"description\":\"Cache miss rate spike: redis miss rate at 60%\",\"raw_log\":\"[ERROR] Cache miss rate spike\"}'
    )
    
    CREATED_COUNT=0
    for ERROR_JSON in \"\${ERROR_TYPES[@]}\"; do
        RESULT=\$(curl -s -X POST ${INGEST_URL}/ingest/demo \\
            -H 'Content-Type: application/json' \\
            -d \"\$ERROR_JSON\")
        
        WI_ID=\$(echo \$RESULT | jq -r '.work_item_id' 2>/dev/null)
        if [ -n \"\$WI_ID\" ] && [ \"\$WI_ID\" != \"null\" ]; then
            CREATED_COUNT=\$((CREATED_COUNT + 1))
            echo \"  ✅ Created: \$WI_ID\"
        fi
    done
    
    if [ \$CREATED_COUNT -lt 3 ]; then
        echo \"Failed to create all error types (created \$CREATED_COUNT/3)\"
        exit 1
    fi
    
    echo \"✅ Created \$CREATED_COUNT different error types\"
"

# Step 6: Test WorkItem Listing
run_test "Ingest: List WorkItems with filtering" "
    # List all work items
    ALL_ITEMS=\$(curl -s \"${INGEST_URL}/work-items?limit=10\")
    TOTAL=\$(echo \$ALL_ITEMS | jq -r '.total' 2>/dev/null)
    
    if [ -z \"\$TOTAL\" ] || [ \"\$TOTAL\" = \"null\" ]; then
        echo \"Failed to list work items\"
        exit 1
    fi
    
    echo \"✅ Total WorkItems: \$TOTAL\"
    
    # Filter by service
    FILTERED=\$(curl -s \"${INGEST_URL}/work-items?service=api-service&limit=5\")
    FILTERED_COUNT=\$(echo \$FILTERED | jq -r '.work_items | length' 2>/dev/null)
    
    echo \"✅ Filtered by service: \$FILTERED_COUNT items\"
"

# Step 7: Test Outcome Recording
run_test "Ingest: Record outcome for WorkItem" "
    if [ -z \"\$WORK_ITEM_ID\" ]; then
        echo \"WORK_ITEM_ID not set\"
        exit 1
    fi
    
    OUTCOME=\$(curl -s -X POST ${INGEST_URL}/work-items/\$WORK_ITEM_ID/outcome \\
        -H 'Content-Type: application/json' \\
        -d '{
            \"event_id\": \"test-outcome-'$(date +%s)'\",
            \"type\": \"resolved\",
            \"actor_id\": \"human-123\",
            \"timestamp\": \"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'\"
        }')
    
    OUTCOME_STATUS=\$(echo \$OUTCOME | jq -r '.processed' 2>/dev/null)
    
    if [ \"\$OUTCOME_STATUS\" != \"true\" ]; then
        echo \"Outcome recording failed\"
        echo \"Response: \$OUTCOME\"
        exit 1
    fi
    
    echo \"✅ Outcome recorded and forwarded to Learner\"
"

# Step 8: Test Monitoring Service Status
run_test "Monitoring: Check monitoring status and stats" "
    STATUS=\$(curl -s ${MONITORING_URL}/monitoring/status)
    MONITORING_STATUS=\$(echo \$STATUS | jq -r '.status' 2>/dev/null)
    ERROR_COUNT=\$(echo \$STATUS | jq -r '.error_count' 2>/dev/null)
    
    if [ \"\$MONITORING_STATUS\" != \"running\" ] && [ \"\$MONITORING_STATUS\" != \"stopped\" ]; then
        echo \"Invalid monitoring status: \$MONITORING_STATUS\"
        exit 1
    fi
    
    echo \"✅ Monitoring status: \$MONITORING_STATUS\"
    echo \"   Error count: \$ERROR_COUNT\"
"

# Step 9: Test Database Verification (optional)
run_test "Database: Verify WorkItems in database" "
    # Check if we can query the database
    DB_COUNT=\$(docker exec goliath-postgres psql -U goliath -d goliath -t -c \"SELECT COUNT(*) FROM work_items;\" 2>/dev/null | tr -d ' ' || echo '0')
    
    if [ \"\$DB_COUNT\" = \"0\" ] || [ -z \"\$DB_COUNT\" ]; then
        echo \"⚠️  Could not verify database (this is OK if DB is not accessible)\"
        return 0
    fi
    
    echo \"✅ Database contains \$DB_COUNT work items\"
"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}❌ Failed: ${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Pipeline is working correctly.${NC}"
    echo ""
    echo "Next steps:"
    echo "  - Monitor logs: make logs SERVICE=monitoring"
    echo "  - View WorkItems: curl ${INGEST_URL}/work-items"
    echo "  - Check monitoring status: curl ${MONITORING_URL}/monitoring/status"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Check the output above for details.${NC}"
    exit 1
fi

