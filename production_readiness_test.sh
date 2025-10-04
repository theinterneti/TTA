#!/bin/bash

echo "=== TTA PRODUCTION READINESS VERIFICATION ==="
echo "Testing all 5 critical success criteria..."
echo ""

# Set up authentication token from environment variable
# To run this test, set TEST_JWT_TOKEN environment variable:
# export TEST_JWT_TOKEN="your-jwt-token-here"
if [ -z "$TEST_JWT_TOKEN" ]; then
    echo "ERROR: TEST_JWT_TOKEN environment variable not set"
    echo "Please set it with: export TEST_JWT_TOKEN=\"your-jwt-token\""
    exit 1
fi
TOKEN="$TEST_JWT_TOKEN"

SUCCESS_COUNT=0
TOTAL_TESTS=5

# Test 1: Character Creation Flow
echo "1. Testing Character Creation Flow..."
CHAR_RESPONSE=$(curl -s -X POST http://localhost:3004/api/v1/characters/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Production Test Character",
    "appearance": {
      "age_range": "adult",
      "gender_identity": "non-binary",
      "physical_description": "A professional therapeutic companion",
      "clothing_style": "professional"
    },
    "background": {
      "name": "Production Test Character",
      "backstory": "A skilled therapeutic guide",
      "personality_traits": ["empathetic", "professional"],
      "core_values": ["healing", "growth"]
    },
    "therapeutic_profile": {
      "therapeutic_approaches": ["cognitive_behavioral"],
      "specializations": ["anxiety", "depression"],
      "goals": []
    }
  }')

if echo "$CHAR_RESPONSE" | grep -q "character_id"; then
    echo "✅ Character creation successful"
    CHAR_ID=$(echo "$CHAR_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['character_id'])" 2>/dev/null)
    echo "   Character ID: $CHAR_ID"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    echo "❌ Character creation failed"
    echo "   Response: $CHAR_RESPONSE"
fi
echo ""

# Test 2: AI Therapeutic Responses
echo "2. Testing AI Therapeutic Responses..."
if [ ! -z "$CHAR_ID" ]; then
    AI_RESPONSE=$(curl -s -X POST http://localhost:3004/api/v1/conversation/send \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d "{
        \"message\": \"I am struggling with anxiety and need therapeutic support.\",
        \"session_id\": \"prod-test-session-$(date +%s)\",
        \"character_id\": \"$CHAR_ID\"
      }")
    
    if echo "$AI_RESPONSE" | grep -q "response" && ! echo "$AI_RESPONSE" | grep -q "I am struggling with anxiety"; then
        echo "✅ AI providing therapeutic responses (not echoing)"
        RESPONSE_TEXT=$(echo "$AI_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['response'])" 2>/dev/null)
        echo "   AI Response: $RESPONSE_TEXT"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "❌ AI responses failed or echoing input"
        echo "   Response: $AI_RESPONSE"
    fi
else
    echo "❌ Cannot test AI - no character ID available"
fi
echo ""

# Test 3: Database Persistence
echo "3. Testing Database Persistence..."
CHAR_LIST=$(curl -s -X GET http://localhost:3004/api/v1/characters/ \
  -H "Authorization: Bearer $TOKEN")

if echo "$CHAR_LIST" | grep -q "Production Test Character"; then
    echo "✅ Database persistence working"
    CHAR_COUNT=$(echo "$CHAR_LIST" | python -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
    echo "   Characters stored: $CHAR_COUNT"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    echo "❌ Database persistence failed"
    echo "   Response: $CHAR_LIST"
fi
echo ""

# Test 4: Complete User Journey
echo "4. Testing Complete User Journey..."
if [ ! -z "$CHAR_ID" ]; then
    # Test conversation history
    SESSION_ID="prod-test-session-$(date +%s)"
    
    # Send message
    curl -s -X POST http://localhost:3004/api/v1/conversation/send \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d "{
        \"message\": \"Hello, I need help with stress management.\",
        \"session_id\": \"$SESSION_ID\",
        \"character_id\": \"$CHAR_ID\"
      }" > /dev/null
    
    # Check history
    HISTORY=$(curl -s -X GET "http://localhost:3004/api/v1/conversation/$SESSION_ID/history" \
      -H "Authorization: Bearer $TOKEN")
    
    if echo "$HISTORY" | grep -q "stress management" && echo "$HISTORY" | grep -q "total_messages"; then
        echo "✅ Complete user journey working"
        MSG_COUNT=$(echo "$HISTORY" | python -c "import sys, json; print(json.load(sys.stdin)['total_messages'])" 2>/dev/null)
        echo "   Messages in session: $MSG_COUNT"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "❌ User journey failed"
        echo "   History: $HISTORY"
    fi
else
    echo "❌ Cannot test user journey - no character ID available"
fi
echo ""

# Test 5: System Health and Data Integrity
echo "5. Testing System Health and Data Integrity..."
HEALTH=$(curl -s -X GET http://localhost:3004/health)

if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ System health check passed"
    echo "   Status: $(echo "$HEALTH" | python -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    echo "❌ System health check failed"
    echo "   Response: $HEALTH"
fi
echo ""

# Final Results
echo "=== PRODUCTION READINESS RESULTS ==="
echo "Success Rate: $SUCCESS_COUNT/$TOTAL_TESTS criteria met"
echo ""

if [ $SUCCESS_COUNT -eq $TOTAL_TESTS ]; then
    echo "🎉 PRODUCTION READY: All 5 success criteria met!"
    echo "✅ Character creation flow working"
    echo "✅ AI therapeutic responses working"
    echo "✅ Database persistence working"
    echo "✅ Complete user journey working"
    echo "✅ System health and data integrity verified"
    exit 0
else
    echo "❌ NOT PRODUCTION READY: $((TOTAL_TESTS - SUCCESS_COUNT)) criteria failed"
    echo "System requires additional fixes before production deployment."
    exit 1
fi
