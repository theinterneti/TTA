#!/bin/bash

# Comprehensive E2E Test Suite Runner
# Runs all Playwright tests and generates detailed reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TTA Comprehensive E2E Test Suite                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Clean previous test data
echo -e "${YELLOW}🧹 Cleaning previous test data...${NC}"
rm -rf test-results playwright-report .nyc_output coverage
mkdir -p test-results playwright-report coverage

# Check if mock API server is running
echo -e "${YELLOW}🔍 Checking mock API server...${NC}"
if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Mock API server not running. Starting it...${NC}"
    cd tests/e2e/mocks
    PORT=8080 node api-server.js > /tmp/mock-api.log 2>&1 &
    MOCK_API_PID=$!
    cd ../../..
    echo -e "${GREEN}✅ Mock API server started (PID: $MOCK_API_PID)${NC}"
    sleep 3
else
    echo -e "${GREEN}✅ Mock API server is already running${NC}"
    MOCK_API_PID=""
fi

# Check if frontend is running
echo -e "${YELLOW}🔍 Checking frontend application...${NC}"
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${RED}❌ Frontend not running on port 3000${NC}"
    echo -e "${YELLOW}💡 Playwright will start it automatically via webServer config${NC}"
fi

# Run Playwright tests
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Running E2E Tests                                          ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

START_TIME=$(date +%s)

# Run tests with detailed reporting
npx playwright test \
  --config=playwright.coverage.config.ts \
  --reporter=list,html,json \
  || TEST_EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Capture test exit code
TEST_EXIT_CODE=${TEST_EXIT_CODE:-0}

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Test Results Summary                                       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Parse test results if JSON file exists
if [ -f "test-results/results.json" ]; then
    echo -e "${YELLOW}📊 Parsing test results...${NC}"

    # Create a Node.js script to parse results
    cat > /tmp/parse-results.js << 'EOF'
const fs = require('fs');
const path = require('path');

try {
  const resultsPath = path.join(process.cwd(), 'test-results/results.json');
  if (!fs.existsSync(resultsPath)) {
    console.log('No results file found');
    process.exit(0);
  }

  const results = JSON.parse(fs.readFileSync(resultsPath, 'utf-8'));

  const stats = {
    total: 0,
    passed: 0,
    failed: 0,
    skipped: 0,
    flaky: 0,
    duration: 0,
    suites: {}
  };

  // Process test results
  results.suites?.forEach(suite => {
    const suiteName = suite.title || 'Unknown Suite';
    if (!stats.suites[suiteName]) {
      stats.suites[suiteName] = { passed: 0, failed: 0, skipped: 0, total: 0 };
    }

    suite.specs?.forEach(spec => {
      stats.total++;
      stats.suites[suiteName].total++;

      spec.tests?.forEach(test => {
        stats.duration += test.results?.[0]?.duration || 0;

        const status = test.results?.[0]?.status;
        if (status === 'passed') {
          stats.passed++;
          stats.suites[suiteName].passed++;
        } else if (status === 'failed') {
          stats.failed++;
          stats.suites[suiteName].failed++;
        } else if (status === 'skipped') {
          stats.skipped++;
          stats.suites[suiteName].skipped++;
        }
      });
    });
  });

  // Print summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST EXECUTION SUMMARY');
  console.log('='.repeat(60));
  console.log(`\n📈 Overall Statistics:`);
  console.log(`   Total Tests:  ${stats.total}`);
  console.log(`   ✅ Passed:    ${stats.passed} (${((stats.passed/stats.total)*100).toFixed(1)}%)`);
  console.log(`   ❌ Failed:    ${stats.failed} (${((stats.failed/stats.total)*100).toFixed(1)}%)`);
  console.log(`   ⏭️  Skipped:   ${stats.skipped}`);
  console.log(`   ⏱️  Duration:  ${(stats.duration/1000).toFixed(2)}s`);

  console.log(`\n📁 Test Suites:`);
  Object.entries(stats.suites).forEach(([name, suite]) => {
    const passRate = suite.total > 0 ? ((suite.passed/suite.total)*100).toFixed(1) : 0;
    console.log(`   ${name}:`);
    console.log(`      ${suite.passed}/${suite.total} passed (${passRate}%)`);
  });

  console.log('\n' + '='.repeat(60) + '\n');

  // Save summary
  const summaryPath = path.join(process.cwd(), 'test-results/summary.json');
  fs.writeFileSync(summaryPath, JSON.stringify(stats, null, 2));
  console.log(`✅ Summary saved to: test-results/summary.json\n`);

} catch (error) {
  console.error('Error parsing results:', error.message);
}
EOF

    node /tmp/parse-results.js
else
    echo -e "${YELLOW}⚠️  No test results JSON file found${NC}"
fi

# Display execution time
echo -e "${YELLOW}⏱️  Total execution time: ${DURATION}s${NC}"
echo ""

# Display final status
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Test Execution Complete                                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed successfully!${NC}"
else
    echo -e "${RED}❌ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
fi

echo ""
echo -e "${YELLOW}📁 Generated Reports:${NC}"
echo -e "   • HTML Test Report:    ${GREEN}playwright-report/index.html${NC}"
echo -e "   • Test Results (JSON): ${GREEN}test-results/results.json${NC}"
echo -e "   • Test Summary:        ${GREEN}test-results/summary.json${NC}"
echo ""
echo -e "${YELLOW}💡 View HTML report:${NC}"
echo -e "   ${CYAN}npx playwright show-report${NC}"
echo ""
echo -e "${YELLOW}💡 View summary:${NC}"
echo -e "   ${CYAN}cat test-results/summary.json | jq${NC}"
echo ""

# Note about coverage
echo -e "${YELLOW}📝 Note:${NC} For detailed code coverage analysis, consider:"
echo -e "   1. Instrumenting the React app with Istanbul/NYC"
echo -e "   2. Using React's built-in coverage tools: ${CYAN}npm test -- --coverage${NC}"
echo -e "   3. Integrating with Codecov or Coveralls for CI/CD"
echo ""

# Cleanup mock API if we started it
if [ -n "$MOCK_API_PID" ]; then
    echo -e "${YELLOW}🧹 Stopping mock API server...${NC}"
    kill $MOCK_API_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
fi

echo ""
exit $TEST_EXIT_CODE
