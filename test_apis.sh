#!/bin/bash

echo "=========================================="
echo "Testing All Goliath APIs"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        echo "$body"
        ((FAILED++))
        return 1
    fi
    echo ""
}

echo "1. Testing Health Checks"
echo "-----------------------"
test_endpoint "Ingest Health" "GET" "http://localhost:8001/healthz"
test_endpoint "Decision Health" "GET" "http://localhost:8002/healthz"
test_endpoint "Learner Health" "GET" "http://localhost:8003/healthz"
test_endpoint "Executor Health" "GET" "http://localhost:8004/healthz"
test_endpoint "Explain Health" "GET" "http://localhost:8005/healthz"
echo ""

echo "2. Testing Database Connectivity"
echo "--------------------------------"
echo -n "Testing PostgreSQL connection... "
if docker exec goliath-postgres psql -U goliath -d goliath -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Testing work_items table... "
if docker exec goliath-postgres psql -U goliath -d goliath -c "SELECT COUNT(*) FROM work_items;" > /dev/null 2>&1; then
    count=$(docker exec goliath-postgres psql -U goliath -d goliath -t -c "SELECT COUNT(*) FROM work_items;" | tr -d ' ')
    echo -e "${GREEN}✓ PASS${NC} ($count work items)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Testing humans table... "
if docker exec goliath-postgres psql -U goliath -d goliath -c "SELECT COUNT(*) FROM humans;" > /dev/null 2>&1; then
    count=$(docker exec goliath-postgres psql -U goliath -d goliath -t -c "SELECT COUNT(*) FROM humans;" | tr -d ' ')
    echo -e "${GREEN}✓ PASS${NC} ($count humans)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Testing decisions table... "
if docker exec goliath-postgres psql -U goliath -d goliath -c "SELECT COUNT(*) FROM decisions;" > /dev/null 2>&1; then
    count=$(docker exec goliath-postgres psql -U goliath -d goliath -t -c "SELECT COUNT(*) FROM decisions;" | tr -d ' ')
    echo -e "${GREEN}✓ PASS${NC} ($count decisions)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

echo "3. Testing Ingest Service APIs"
echo "------------------------------"
test_endpoint "List Work Items" "GET" "http://localhost:8001/work-items?limit=5"
test_endpoint "List Work Items (filtered)" "GET" "http://localhost:8001/work-items?service=api-service&limit=5"

# Create a test work item
echo -n "Creating test work item... "
create_response=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{
    "type": "incident",
    "service": "api-service",
    "severity": "sev2",
    "description": "Test API endpoint - High latency detected",
    "origin_system": "test-script"
  }' \
  "http://localhost:8001/work-items")

work_item_id=$(echo "$create_response" | jq -r '.id // empty' 2>/dev/null)
if [ -n "$work_item_id" ] && [ "$work_item_id" != "null" ]; then
    echo -e "${GREEN}✓ PASS${NC} (ID: $work_item_id)"
    ((PASSED++))
    
    # Test getting the work item
    test_endpoint "Get Work Item" "GET" "http://localhost:8001/work-items/$work_item_id"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "$create_response"
    ((FAILED++))
fi
echo ""

echo "4. Testing Decision Service APIs"
echo "---------------------------------"
if [ -n "$work_item_id" ] && [ "$work_item_id" != "null" ]; then
    # Trigger a decision
    echo -n "Triggering decision for work item... "
    decision_response=$(curl -s -X POST -H "Content-Type: application/json" \
      -d "{\"work_item_id\": \"$work_item_id\"}" \
      "http://localhost:8002/decide")
    
    decision_id=$(echo "$decision_response" | jq -r '.id // empty' 2>/dev/null)
    if [ -n "$decision_id" ] && [ "$decision_id" != "null" ]; then
        echo -e "${GREEN}✓ PASS${NC} (Decision ID: $decision_id)"
        ((PASSED++))
        
        # Test getting the decision
        test_endpoint "Get Decision" "GET" "http://localhost:8002/decisions/$work_item_id"
        test_endpoint "Get Audit Trail" "GET" "http://localhost:8002/audit/$work_item_id"
    else
        echo -e "${YELLOW}⚠ SKIP${NC} (No decision created - may need humans in DB)"
        echo "$decision_response" | jq . 2>/dev/null || echo "$decision_response"
    fi
else
    echo -e "${YELLOW}⚠ SKIP${NC} (No work item ID available)"
fi
echo ""

echo "5. Testing Learner Service APIs"
echo "-------------------------------"
test_endpoint "Get Profiles (api-service)" "GET" "http://localhost:8003/profiles?service=api-service"
test_endpoint "Get Profiles (payment-service)" "GET" "http://localhost:8003/profiles?service=payment-service"

# Get a human ID if available
human_id=$(docker exec goliath-postgres psql -U goliath -d goliath -t -c "SELECT id FROM humans LIMIT 1;" 2>/dev/null | tr -d ' ' | head -1)
if [ -n "$human_id" ] && [ "$human_id" != "" ]; then
    test_endpoint "Get Human Stats" "GET" "http://localhost:8003/stats?human_id=$human_id"
else
    echo -e "${YELLOW}⚠ SKIP${NC} Get Human Stats (no humans in database)"
fi
echo ""

echo "6. Testing Graph API"
echo "--------------------"
test_endpoint "Graph API (all nodes)" "GET" "http://localhost:3000/api/graph?limit=10"
test_endpoint "Graph API (work items only)" "GET" "http://localhost:3000/api/graph?node_type=work_item&limit=10"
echo ""

echo "7. Testing Weaviate"
echo "-------------------"
echo -n "Testing Weaviate health... "
weaviate_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/v1/.well-known/ready)
if [ "$weaviate_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (HTTP $weaviate_code)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} (HTTP $weaviate_code)"
    ((FAILED++))
fi
echo ""

echo "=========================================="
echo "Summary"
echo "=========================================="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed! ✗${NC}"
    exit 1
fi
