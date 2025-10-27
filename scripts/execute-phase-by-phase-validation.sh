#!/bin/bash
#
# Phase-by-Phase E2E Validation Executor
# Runs each test phase individually with detailed reporting
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
REPORT_DIR="test-results-staging"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SUMMARY_FILE="${REPORT_DIR}/validation-summary-${TIMESTAMP}.md"

mkdir -p "${REPORT_DIR}"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     TTA Staging - Comprehensive E2E Validation Execution        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Timestamp: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${CYAN}Report Directory: ${REPORT_DIR}${NC}"
echo ""

# Initialize summary
cat > "${SUMMARY_FILE}" << 'EOF'
# TTA Staging Environment - E2E Validation Summary

## Test Execution Overview

EOF

echo "**Execution Started:** $(date '+%Y-%m-%d %H:%M:%S')" >> "${SUMMARY_FILE}"
echo "" >> "${SUMMARY_FILE}"

# Test phases configuration
declare -A PHASES
PHASES[1]="Authentication & Core Flow|01-authentication.staging.spec.ts|CRITICAL"
PHASES[2]="UI/UX Functionality|02-ui-functionality.staging.spec.ts|HIGH"
PHASES[3]="Integration Testing|03-integration.staging.spec.ts|HIGH"
PHASES[4]="Error Handling & Resilience|04-error-handling.staging.spec.ts|MEDIUM"
PHASES[5]="Responsive Design & Mobile|05-responsive.staging.spec.ts|MEDIUM"
PHASES[6]="Accessibility Compliance|06-accessibility.staging.spec.ts|LOW"
PHASES[7]="Complete User Journey|complete-user-journey.staging.spec.ts|FINAL"

# Results tracking
TOTAL_PHASES=7
PASSED_PHASES=0
FAILED_PHASES=0

# Function to run a single phase
run_phase() {
    local phase_num=$1
    local phase_info="${PHASES[$phase_num]}"

    IFS='|' read -r phase_name test_file priority <<< "$phase_info"

    local log_file="${REPORT_DIR}/phase-${phase_num}-execution.log"
    local result_file="${REPORT_DIR}/phase-${phase_num}-results.txt"

    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Phase ${phase_num}/${TOTAL_PHASES}: ${phase_name}${NC}"
    echo -e "${CYAN}Priority: ${priority} | Test File: ${test_file}${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Add to summary
    echo "### Phase ${phase_num}: ${phase_name}" >> "${SUMMARY_FILE}"
    echo "" >> "${SUMMARY_FILE}"
    echo "- **Priority:** ${priority}" >> "${SUMMARY_FILE}"
    echo "- **Test File:** \`tests/e2e-staging/${test_file}\`" >> "${SUMMARY_FILE}"
    echo "- **Started:** $(date '+%Y-%m-%d %H:%M:%S')" >> "${SUMMARY_FILE}"
    echo "" >> "${SUMMARY_FILE}"

    # Run test with Chromium
    echo -e "${GREEN}▶ Running tests on Chromium browser...${NC}"

    if npx playwright test "tests/e2e-staging/${test_file}" \
        --config=playwright.staging.config.ts \
        --project=chromium \
        --reporter=list \
        --retries=1 \
        --timeout=90000 \
        > "${log_file}" 2>&1; then

        echo -e "${GREEN}✓ Phase ${phase_num} PASSED${NC}"
        echo "- **Status:** ✅ PASSED" >> "${SUMMARY_FILE}"
        PASSED_PHASES=$((PASSED_PHASES + 1))
        echo "PASSED" > "${result_file}"
    else
        echo -e "${RED}✗ Phase ${phase_num} FAILED${NC}"
        echo -e "${YELLOW}  See log: ${log_file}${NC}"
        echo "- **Status:** ❌ FAILED" >> "${SUMMARY_FILE}"
        FAILED_PHASES=$((FAILED_PHASES + 1))
        echo "FAILED" > "${result_file}"

        # Extract failure summary from log
        if [ -f "${log_file}" ]; then
            echo "" >> "${SUMMARY_FILE}"
            echo "**Failure Summary:**" >> "${SUMMARY_FILE}"
            echo '```' >> "${SUMMARY_FILE}"
            tail -50 "${log_file}" >> "${SUMMARY_FILE}"
            echo '```' >> "${SUMMARY_FILE}"
        fi
    fi

    echo "- **Completed:** $(date '+%Y-%m-%d %H:%M:%S')" >> "${SUMMARY_FILE}"
    echo "" >> "${SUMMARY_FILE}"
    echo "---" >> "${SUMMARY_FILE}"
    echo "" >> "${SUMMARY_FILE}"
}

# Execute all phases
for phase_num in {1..7}; do
    run_phase $phase_num

    # Brief pause between phases
    sleep 2
done

# Generate final summary
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Validation Complete - Generating Summary${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Add final summary
cat >> "${SUMMARY_FILE}" << EOF
## Final Results

### Statistics

- **Total Phases:** ${TOTAL_PHASES}
- **Passed:** ${PASSED_PHASES}
- **Failed:** ${FAILED_PHASES}
- **Success Rate:** $(( PASSED_PHASES * 100 / TOTAL_PHASES ))%

### Production Readiness Assessment

EOF

if [ $FAILED_PHASES -eq 0 ]; then
    echo "**Overall Status:** ✅ PRODUCTION READY" >> "${SUMMARY_FILE}"
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  ✓ ALL PHASES PASSED                             ║${NC}"
    echo -e "${GREEN}║              STAGING ENVIRONMENT IS READY                        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
elif [ $FAILED_PHASES -le 2 ]; then
    echo "**Overall Status:** ⚠️  NEEDS ATTENTION (Minor Issues)" >> "${SUMMARY_FILE}"
    echo ""
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║              ⚠ SOME PHASES FAILED                                ║${NC}"
    echo -e "${YELLOW}║          REVIEW FAILURES BEFORE PRODUCTION                       ║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════════╝${NC}"
else
    echo "**Overall Status:** ❌ NOT PRODUCTION READY (Critical Issues)" >> "${SUMMARY_FILE}"
    echo ""
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║            ✗ MULTIPLE PHASES FAILED                              ║${NC}"
    echo -e "${RED}║        CRITICAL ISSUES MUST BE RESOLVED                          ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo "**Execution Completed:** $(date '+%Y-%m-%d %H:%M:%S')" >> "${SUMMARY_FILE}"
echo ""

# Display results
echo ""
echo -e "${CYAN}Results Summary:${NC}"
echo -e "  Passed: ${GREEN}${PASSED_PHASES}${NC}/${TOTAL_PHASES}"
echo -e "  Failed: ${RED}${FAILED_PHASES}${NC}/${TOTAL_PHASES}"
echo ""
echo -e "${CYAN}Detailed Report: ${SUMMARY_FILE}${NC}"
echo -e "${CYAN}HTML Report: npx playwright show-report playwright-staging-report${NC}"
echo ""
