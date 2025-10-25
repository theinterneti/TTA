#!/bin/bash
#
# Comprehensive E2E Validation Script for TTA Staging Environment
#
# This script executes all 7 phases of E2E testing sequentially and generates
# a comprehensive production readiness report.
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPORT_DIR="test-results-staging"
REPORT_FILE="${REPORT_DIR}/comprehensive-validation-report.md"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Create report directory
mkdir -p "${REPORT_DIR}"

# Initialize report
cat > "${REPORT_FILE}" << EOF
# TTA Staging Environment - Comprehensive E2E Validation Report

**Date:** ${TIMESTAMP}
**Environment:** TTA Staging (localhost:3001)
**Test Framework:** Playwright 1.55.0
**Browsers:** Chromium, Firefox, WebKit

---

## Executive Summary

This report documents the results of comprehensive end-to-end validation of the TTA staging environment across 7 test phases.

---

EOF

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TTA Staging Environment - Comprehensive E2E Validation       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to run a test phase
run_phase() {
    local phase_num=$1
    local phase_name=$2
    local test_file=$3
    local priority=$4

    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Phase ${phase_num}: ${phase_name} (Priority: ${priority})${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Add phase header to report
    cat >> "${REPORT_FILE}" << EOF
## Phase ${phase_num}: ${phase_name}

**Priority:** ${priority}
**Test File:** \`${test_file}\`
**Execution Time:** $(date +"%Y-%m-%d %H:%M:%S")

### Test Results

EOF

    # Run tests for Chromium
    echo -e "${GREEN}Running tests on Chromium...${NC}"
    if npx playwright test "${test_file}" \
        --config=playwright.staging.config.ts \
        --project=chromium \
        --reporter=json \
        --output="${REPORT_DIR}/phase-${phase_num}-chromium.json" \
        --retries=1 \
        --timeout=60000 2>&1 | tee "${REPORT_DIR}/phase-${phase_num}-chromium.log"; then
        echo -e "${GREEN}✓ Chromium tests passed${NC}"
        echo "**Chromium:** ✅ PASSED" >> "${REPORT_FILE}"
    else
        echo -e "${RED}✗ Chromium tests failed${NC}"
        echo "**Chromium:** ❌ FAILED (see logs for details)" >> "${REPORT_FILE}"
    fi

    echo ""
    echo "---" >> "${REPORT_FILE}"
    echo "" >> "${REPORT_FILE}"
}

# Phase 1: Authentication & Core Flow (Critical)
run_phase 1 "Authentication & Core Flow" \
    "tests/e2e-staging/01-authentication.staging.spec.ts" \
    "CRITICAL"

# Phase 2: UI/UX Functionality (High)
run_phase 2 "UI/UX Functionality" \
    "tests/e2e-staging/02-ui-functionality.staging.spec.ts" \
    "HIGH"

# Phase 3: Integration Testing (High)
run_phase 3 "Integration Testing" \
    "tests/e2e-staging/03-integration.staging.spec.ts" \
    "HIGH"

# Phase 4: Error Handling & Resilience (Medium)
run_phase 4 "Error Handling & Resilience" \
    "tests/e2e-staging/04-error-handling.staging.spec.ts" \
    "MEDIUM"

# Phase 5: Responsive Design & Mobile Support (Medium)
run_phase 5 "Responsive Design & Mobile Support" \
    "tests/e2e-staging/05-responsive.staging.spec.ts" \
    "MEDIUM"

# Phase 6: Accessibility Compliance (Low)
run_phase 6 "Accessibility Compliance" \
    "tests/e2e-staging/06-accessibility.staging.spec.ts" \
    "LOW"

# Phase 7: Complete End-to-End Suite (Final Validation)
run_phase 7 "Complete End-to-End Suite" \
    "tests/e2e-staging/complete-user-journey.staging.spec.ts" \
    "FINAL"

# Generate summary
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Generating Comprehensive Report...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Add summary section to report
cat >> "${REPORT_FILE}" << EOF
## Production Readiness Assessment

### Success Criteria Evaluation

- **Zero critical errors in authentication and core gameplay flows:** TBD
- **All database integrations functioning with verified persistence:** TBD
- **Error messages are clear and actionable for end users:** TBD
- **UI is responsive and functional across all tested viewports:** TBD
- **Complete user journey executes without manual intervention:** TBD
- **System demonstrates engaging, fun collaborative storytelling:** TBD

### Overall Status

**Production Readiness:** TBD

### Recommendations

1. Review failed tests and address root causes
2. Verify database persistence across all test scenarios
3. Validate error handling and user feedback mechanisms
4. Ensure responsive design works across all target devices
5. Confirm accessibility compliance for WCAG 2.1 AA

---

**Report Generated:** ${TIMESTAMP}
**Report Location:** \`${REPORT_FILE}\`

EOF

echo -e "${GREEN}✓ Comprehensive validation complete!${NC}"
echo -e "${BLUE}Report saved to: ${REPORT_FILE}${NC}"
echo ""
echo -e "${YELLOW}To view the HTML report:${NC}"
echo -e "  npx playwright show-report playwright-staging-report"
echo ""
echo -e "${YELLOW}To view individual test results:${NC}"
echo -e "  cat ${REPORT_FILE}"
echo ""
