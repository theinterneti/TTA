#!/bin/bash
# Automated Keploy Testing for TTA
# Records API interactions and replays them as automated tests

set -e

echo "🤖 Keploy Automated Testing"
echo "============================"
echo ""

# Step 1: Start API with Keploy recording
echo "📝 Step 1: Starting API with Keploy recording..."
echo ""

# Run Keploy in record mode - it will start the API and record traffic
docker run --rm -it \
    --name keploy-record \
    -p 8000:8000 \
    -v "$(pwd):/workspace" \
    -v "/tmp:/tmp" \
    --workdir /workspace \
    --privileged \
    ghcr.io/keploy/keploy:latest \
    record \
    -c "python3 simple_test_api.py" \
    --delay 10 \
    --path "/workspace/keploy" &

KEPLOY_PID=$!
echo "✅ Keploy recording started (PID: $KEPLOY_PID)"
echo ""

# Step 2: Wait for API to start
echo "⏳ Step 2: Waiting for API to start..."
sleep 12

# Step 3: Make automated API calls
echo "📞 Step 3: Making automated API calls..."
echo ""

# Test 1: Health check
echo "  ✓ Testing /health endpoint..."
curl -s http://localhost:8000/health | jq . || true

# Test 2: Root endpoint
echo "  ✓ Testing / endpoint..."
curl -s http://localhost:8000/ | jq . || true

# Test 3: Create session
echo "  ✓ Creating a session..."
SESSION=$(curl -s -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "automated-test-user", "game_type": "adventure"}')
echo "$SESSION" | jq . || true
SESSION_ID=$(echo "$SESSION" | jq -r .session_id)

# Test 4: Get session
echo "  ✓ Getting session..."
curl -s http://localhost:8000/api/v1/sessions/$SESSION_ID | jq . || true

# Test 5: List sessions
echo "  ✓ Listing all sessions..."
curl -s http://localhost:8000/api/v1/sessions | jq . || true

# Test 6: Delete session
echo "  ✓ Deleting session..."
curl -s -X DELETE http://localhost:8000/api/v1/sessions/$SESSION_ID | jq . || true

echo ""
echo "✅ Step 3 complete: All API calls made"
echo ""

# Step 4: Stop recording
echo "🛑 Step 4: Stopping Keploy recording..."
sleep 2
kill $KEPLOY_PID 2>/dev/null || docker stop keploy-record 2>/dev/null || true
echo ""

# Step 5: Show recorded tests
echo "📊 Step 5: Recorded test cases:"
if [ -d "keploy/tests" ]; then
    ls -lh keploy/tests/
    echo ""
    echo "✅ Test cases recorded in keploy/tests/"
else
    echo "⚠️  No tests recorded yet"
fi

echo ""
echo "=================================="
echo "🎉 Automated testing setup complete!"
echo ""
echo "To replay these tests anytime:"
echo "  ./keploy.sh test"
echo ""
echo "Or manually:"
echo "  docker run --rm -it -v \$(pwd):/workspace --privileged ghcr.io/keploy/keploy:latest test -c 'python3 simple_test_api.py' --path /workspace/keploy"
