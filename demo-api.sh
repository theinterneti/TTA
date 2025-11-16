#!/bin/bash
# Quick Keploy Demo for TTA
# This demonstrates Keploy recording and testing with your API

set -e

echo "🎯 Keploy Quick Demo for TTA"
echo "================================"
echo ""

# Check if API is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ API is not running on port 8000"
    echo "Starting the test API..."
    uv run python simple_test_api.py &
    API_PID=$!
    sleep 3
    echo "✅ API started (PID: $API_PID)"
else
    echo "✅ API is already running"
fi

echo ""
echo "📋 Making some test API calls..."
echo ""

# Test 1: Root endpoint
echo "1️⃣ Testing root endpoint..."
curl -s http://localhost:8000/ | jq .

echo ""
echo "2️⃣ Testing health endpoint..."
curl -s http://localhost:8000/health | jq .

echo ""
echo "3️⃣ Creating a session..."
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo-user", "game_type": "adventure"}')
echo "$SESSION_RESPONSE" | jq .
SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r .session_id)

echo ""
echo "4️⃣ Getting the session..."
curl -s http://localhost:8000/api/v1/sessions/$SESSION_ID | jq .

echo ""
echo "5️⃣ Listing all sessions..."
curl -s http://localhost:8000/api/v1/sessions | jq .

echo ""
echo "6️⃣ Deleting the session..."
curl -s -X DELETE http://localhost:8000/api/v1/sessions/$SESSION_ID | jq .

echo ""
echo "================================"
echo "✅ Demo complete!"
echo ""
echo "📊 Your API is working on http://localhost:8000"
echo "📝 API Docs: http://localhost:8000/docs"
echo ""
echo "Next steps with Keploy:"
echo "1. Install: curl --silent -O -L https://keploy.io/install.sh && source install.sh"
echo "2. Record: keploy record -c 'uv run python simple_test_api.py'"
echo "3. Make API calls (like above)"
echo "4. Test: keploy test -c 'uv run python simple_test_api.py'"
