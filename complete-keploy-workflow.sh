#!/bin/bash
# Complete Automated Testing Workflow with Keploy
# This script demonstrates the full automated testing cycle

set -e

echo "🎯 Complete Automated Testing Workflow with Keploy"
echo "===================================================="
echo ""

# Step 1: Record test cases (if not already done)
if [ ! -d "keploy/tests" ] || [ -z "$(ls -A keploy/tests 2>/dev/null)" ]; then
    echo "📝 Step 1: Recording API test cases..."
    ./automate-keploy-record.sh
else
    echo "✅ Step 1: Test cases already recorded"
    echo "   Found: $(ls keploy/tests/*.yaml 2>/dev/null | wc -l) test case(s)"
fi

echo ""

# Step 2: Start API if not running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "🚀 Step 2: Starting API..."
    uv run python simple_test_api.py > /tmp/api.log 2>&1 &
    API_PID=$!
    echo "   API started (PID: $API_PID)"
    sleep 3
else
    echo "✅ Step 2: API already running"
fi

echo ""

# Step 3: Run automated tests
echo "🧪 Step 3: Running automated Keploy tests..."
echo ""
uv run python run-keploy-tests.py

echo ""

# Step 4: Summary and next steps
echo "===================================================="
echo "✅ Automated Testing Complete!"
echo "===================================================="
echo ""
echo "📊 What just happened:"
echo "  1. ✅ API test cases were recorded (or loaded)"
echo "  2. ✅ API was started (or verified running)"
echo "  3. ✅ Tests were automatically executed"
echo "  4. ✅ Results were validated"
echo ""
echo "🔄 Continuous Integration:"
echo "  Add to your CI/CD pipeline (.github/workflows/test.yml):"
echo ""
echo "  jobs:"
echo "    test:"
echo "      steps:"
echo "        - name: Run Automated Keploy Tests"
echo "          run: ./complete-keploy-workflow.sh"
echo ""
echo "🎯 Benefits of Keploy Automation:"
echo "  ✓ Zero manual test writing"
echo "  ✓ Real API behavior captured"
echo "  ✓ Instant regression detection"
echo "  ✓ Fast test execution (milliseconds)"
echo "  ✓ No mocking needed - tests use real responses"
echo ""
echo "📈 Coverage: API endpoints tested:"
echo "  - GET  /health"
echo "  - GET  /"
echo "  - POST /api/v1/sessions"
echo "  - GET  /api/v1/sessions/:id"
echo "  - GET  /api/v1/sessions"
echo "  - DELETE /api/v1/sessions/:id"
echo ""
echo "🚀 Next steps:"
echo "  1. Add more API interactions to record:"
echo "     - Edit automate-keploy-record.sh"
echo "     - Add your API endpoints"
echo "     - Re-run to capture new tests"
echo ""
echo "  2. Integrate into development workflow:"
echo "     - Pre-commit hook: ./complete-keploy-workflow.sh"
echo "     - CI/CD pipeline: automated on every push"
echo ""
echo "  3. Extend to other APIs:"
echo "     - Player Experience API (port 8080)"
echo "     - Franchise Worlds API (port 8000/api/v1)"
echo "     - Agent Orchestration endpoints"
