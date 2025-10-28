#!/bin/bash
# Record REAL API interactions with proper request/response capture

set -e

echo "🎬 Recording Real API Interactions"
echo "===================================="
echo ""

# Start fresh
rm -rf keploy/tests/*.yaml 2>/dev/null
mkdir -p keploy/tests

# Ensure API is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "🚀 Starting API..."
    uv run python simple_test_api.py > /tmp/api.log 2>&1 &
    sleep 3
fi

echo "📝 Recording actual API calls..."
echo ""

# Counter for test files
counter=1

# Helper function to create test case from real API call
create_test_case() {
    local name=$1
    local method=$2
    local path=$3
    local req_body=$4
    local description=$5

    echo "  Recording: $description"

    # Make actual API call and capture response
    if [ "$method" == "POST" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "http://localhost:8000$path" \
          -H "Content-Type: application/json" \
          -d "$req_body")
    elif [ "$method" == "DELETE" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "http://localhost:8000$path")
    else
        RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:8000$path")
    fi

    # Extract status code and body
    STATUS=$(echo "$RESPONSE" | tail -n 1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    # Escape body for YAML
    BODY_ESCAPED=$(echo "$BODY" | sed 's/"/\\"/g')

    # Create test file
    cat > "keploy/tests/test-$(printf "%03d" $counter)-${name}.yaml" << TESTEOF
version: api.keploy.io/v1beta1
kind: Http
name: ${name}
spec:
  metadata:
    description: ${description}
  req:
    method: ${method}
    proto_major: 1
    proto_minor: 1
    url: http://localhost:8000${path}
    header:
      Accept: "*/*"
      Content-Type: application/json
      Host: localhost:8000
    body: '${req_body}'
    timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
  resp:
    status_code: ${STATUS}
    header:
      Content-Type: application/json
    body: '${BODY_ESCAPED}'
    timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
  objects: []
  assertions:
    noise:
      - "body.session_id"
      - "body.timestamp"
      - "body.created_at"
  created: $(date +%s)
TESTEOF

    ((counter++))
}

# ============================================================================
# Test Suite 1: Health & Status
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Suite 1: Health & Status Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

create_test_case "health-check" "GET" "/health" "" "Health endpoint check"
create_test_case "root-endpoint" "GET" "/" "" "Root API information"

# ============================================================================
# Test Suite 2: Session Management
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Suite 2: Session Management"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create sessions and capture IDs
SESSION1_BODY='{"user_id": "player_001", "game_type": "adventure"}'
create_test_case "create-session-adventure" "POST" "/api/v1/sessions" "$SESSION1_BODY" "Create adventure session"

# Get the actual session ID from last response
SESSION1_ID=$(curl -s -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d "$SESSION1_BODY" | jq -r .session_id)

SESSION2_BODY='{"user_id": "player_002", "game_type": "mystery"}'
create_test_case "create-session-mystery" "POST" "/api/v1/sessions" "$SESSION2_BODY" "Create mystery session"

SESSION2_ID=$(curl -s -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d "$SESSION2_BODY" | jq -r .session_id)

# Read operations
create_test_case "get-session" "GET" "/api/v1/sessions/$SESSION1_ID" "" "Get specific session"
create_test_case "list-all-sessions" "GET" "/api/v1/sessions" "" "List all sessions"

# Delete operation
create_test_case "delete-session" "DELETE" "/api/v1/sessions/$SESSION2_ID" "" "Delete session"

# ============================================================================
# Test Suite 3: Error Handling
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Suite 3: Error Handling"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

create_test_case "get-nonexistent-session" "GET" "/api/v1/sessions/invalid-uuid-123" "" "Attempt to get non-existent session"
create_test_case "create-invalid-session" "POST" "/api/v1/sessions" '{"invalid": "data"}' "Attempt invalid session creation"

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Recording Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TEST_COUNT=$(ls -1 keploy/tests/*.yaml 2>/dev/null | wc -l)
echo "📊 Recorded $TEST_COUNT test cases from real API calls"
echo ""
echo "Test files created:"
ls -1 keploy/tests/ | head -20

echo ""
echo "🚀 Ready to run tests: ./complete-keploy-workflow.sh"
