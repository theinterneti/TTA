#!/bin/bash

# Run E2E tests with code coverage collection
# This script runs Playwright tests and collects V8 coverage data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TTA E2E Test Suite with Code Coverage                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Clean previous coverage data
echo -e "${YELLOW}🧹 Cleaning previous coverage data...${NC}"
rm -rf .nyc_output coverage test-results playwright-report
mkdir -p .nyc_output coverage test-results

# Check if mock API server is running
echo -e "${YELLOW}🔍 Checking mock API server...${NC}"
if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Mock API server not running. Starting it...${NC}"
    cd tests/e2e/mocks
    PORT=8080 node api-server.js > /tmp/mock-api.log 2>&1 &
    MOCK_API_PID=$!
    cd ../../..
    echo -e "${GREEN}✅ Mock API server started (PID: $MOCK_API_PID)${NC}"
    sleep 2
else
    echo -e "${GREEN}✅ Mock API server is already running${NC}"
    MOCK_API_PID=""
fi

# Run Playwright tests with coverage collection
echo -e "${YELLOW}🧪 Running E2E tests with coverage collection...${NC}"
echo ""

export COLLECT_COVERAGE=true

# Run tests on Chromium only for coverage (faster)
npx playwright test \
  --config=playwright.coverage.config.ts \
  --project=chromium \
  --reporter=list,html,json \
  || TEST_EXIT_CODE=$?

# Capture test exit code
TEST_EXIT_CODE=${TEST_EXIT_CODE:-0}

echo ""
echo -e "${YELLOW}📊 Generating coverage report...${NC}"

# Generate coverage report using Node.js
node -e "
const { generateCoverageReport } = require('./tests/e2e/utils/coverage-helper.ts');
generateCoverageReport().catch(console.error);
" || echo -e "${YELLOW}⚠️  Coverage report generation skipped (TypeScript compilation needed)${NC}"

# Alternative: Use a simple Node script to process coverage
cat > /tmp/process-coverage.js << 'EOF'
const fs = require('fs');
const path = require('path');

const COVERAGE_DIR = path.join(process.cwd(), '.nyc_output');
const COVERAGE_REPORT_DIR = path.join(process.cwd(), 'coverage');

try {
  if (!fs.existsSync(COVERAGE_DIR)) {
    console.log('No coverage data found');
    process.exit(0);
  }

  const files = fs.readdirSync(COVERAGE_DIR).filter(f => f.startsWith('coverage-'));

  if (files.length === 0) {
    console.log('No coverage files found');
    process.exit(0);
  }

  console.log(`\n📊 Processing ${files.length} coverage files...`);

  let totalFiles = new Set();
  let totalBytes = 0;
  let coveredBytes = 0;

  files.forEach(file => {
    const data = JSON.parse(fs.readFileSync(path.join(COVERAGE_DIR, file), 'utf-8'));
    if (data.result) {
      data.result.forEach(entry => {
        totalFiles.add(entry.url);
        entry.functions?.forEach(func => {
          func.ranges?.forEach(range => {
            const bytes = range.endOffset - range.startOffset;
            totalBytes += bytes;
            if (range.count > 0) {
              coveredBytes += bytes;
            }
          });
        });
      });
    }
  });

  const coverage = totalBytes > 0 ? (coveredBytes / totalBytes) * 100 : 0;

  console.log('\n' + '='.repeat(60));
  console.log('📊 E2E TEST COVERAGE SUMMARY');
  console.log('='.repeat(60));
  console.log(`\n📁 Files Analyzed: ${totalFiles.size}`);
  console.log(`📈 Byte Coverage: ${coverage.toFixed(2)}% (${coveredBytes}/${totalBytes} bytes)`);
  console.log('\n' + '='.repeat(60) + '\n');

  // Save summary
  if (!fs.existsSync(COVERAGE_REPORT_DIR)) {
    fs.mkdirSync(COVERAGE_REPORT_DIR, { recursive: true });
  }

  const summary = {
    timestamp: new Date().toISOString(),
    files: totalFiles.size,
    totalBytes,
    coveredBytes,
    coverage: coverage.toFixed(2) + '%'
  };

  fs.writeFileSync(
    path.join(COVERAGE_REPORT_DIR, 'summary.json'),
    JSON.stringify(summary, null, 2)
  );

  console.log(`✅ Coverage summary saved to: ${path.join(COVERAGE_REPORT_DIR, 'summary.json')}`);

} catch (error) {
  console.error('Error processing coverage:', error);
  process.exit(1);
}
EOF

node /tmp/process-coverage.js

# Display test results summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Test Execution Complete                                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
fi

echo ""
echo -e "${YELLOW}📁 Reports generated:${NC}"
echo -e "   • HTML Test Report:    ${GREEN}playwright-report/index.html${NC}"
echo -e "   • Coverage Summary:    ${GREEN}coverage/summary.json${NC}"
echo -e "   • Test Results (JSON): ${GREEN}test-results/results.json${NC}"
echo ""
echo -e "${YELLOW}💡 View reports:${NC}"
echo -e "   npx playwright show-report"
echo -e "   cat coverage/summary.json"
echo ""

# Cleanup mock API if we started it
if [ -n "$MOCK_API_PID" ]; then
    echo -e "${YELLOW}🧹 Stopping mock API server...${NC}"
    kill $MOCK_API_PID 2>/dev/null || true
fi

exit $TEST_EXIT_CODE
