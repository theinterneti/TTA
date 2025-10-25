#!/bin/bash

# =============================================================================
# TTA Staging E2E Test Runner
# =============================================================================
# This script runs comprehensive Playwright tests against the staging environment
#
# Usage:
#   ./scripts/run-staging-tests.sh [options]
#
# Options:
#   --headed          Run tests in headed mode (visible browser)
#   --debug           Run tests in debug mode
#   --ui              Run tests with Playwright UI
#   --skip-validation Skip environment validation
#   --report          Open HTML report after tests
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
HEADED=false
DEBUG=false
UI=false
SKIP_VALIDATION=false
OPEN_REPORT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --headed)
            HEADED=true
            shift
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --ui)
            UI=true
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        --report)
            OPEN_REPORT=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  TTA Staging E2E Test Runner                               ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Validate environment unless skipped
if [ "$SKIP_VALIDATION" = false ]; then
    echo -e "${YELLOW}🔍 Validating staging environment...${NC}"
    echo ""

    if ./scripts/validate-staging-environment.sh; then
        echo ""
    else
        echo -e "${RED}❌ Environment validation failed!${NC}"
        echo -e "${YELLOW}💡 Fix the issues above or use --skip-validation to run anyway${NC}"
        exit 1
    fi
fi

# Build test command
TEST_CMD="npx playwright test --config=playwright.staging.config.ts"

if [ "$HEADED" = true ]; then
    TEST_CMD="$TEST_CMD --headed"
fi

if [ "$DEBUG" = true ]; then
    TEST_CMD="$TEST_CMD --debug"
fi

if [ "$UI" = true ]; then
    TEST_CMD="$TEST_CMD --ui"
fi

# Run tests
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Running Staging E2E Tests                                 ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Command: $TEST_CMD${NC}"
echo ""

START_TIME=$(date +%s)

if eval "$TEST_CMD"; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ All tests passed!                                      ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}⏱  Duration: ${DURATION}s${NC}"
    echo ""

    if [ "$OPEN_REPORT" = true ]; then
        echo -e "${BLUE}📊 Opening test report...${NC}"
        npx playwright show-report playwright-staging-report
    else
        echo -e "${BLUE}📊 View detailed report:${NC}"
        echo -e "   ${CYAN}npx playwright show-report playwright-staging-report${NC}"
    fi

    echo ""
    exit 0
else
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ Some tests failed!                                     ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${RED}⏱  Duration: ${DURATION}s${NC}"
    echo ""
    echo -e "${YELLOW}💡 View detailed report:${NC}"
    echo -e "   ${CYAN}npx playwright show-report playwright-staging-report${NC}"
    echo ""
    echo -e "${YELLOW}💡 Run in debug mode:${NC}"
    echo -e "   ${CYAN}./scripts/run-staging-tests.sh --debug${NC}"
    echo ""
    echo -e "${YELLOW}💡 Run with UI:${NC}"
    echo -e "   ${CYAN}./scripts/run-staging-tests.sh --ui${NC}"
    echo ""
    exit 1
fi
