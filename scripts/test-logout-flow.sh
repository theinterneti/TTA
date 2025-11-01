#!/bin/bash

# Test Logout Flow - Comprehensive Testing Script
# This script runs the logout flow tests against the staging environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STAGING_URL="${STAGING_URL:-http://localhost:3001}"
API_URL="${API_URL:-http://localhost:8081}"
TEST_DIR="tests/e2e-staging"

echo -e "${BLUE}=== TTA Logout Flow Testing ===${NC}\n"

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Function to check if services are running
check_services() {
    print_section "Checking Services"

    # Check frontend
    if curl -s -o /dev/null -w "%{http_code}" "$STAGING_URL" | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✓${NC} Frontend is running at $STAGING_URL"
    else
        echo -e "${RED}✗${NC} Frontend is not running at $STAGING_URL"
        return 1
    fi

    # Check API (health endpoint requires auth, so check if port is open)
    if curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/health" | grep -qE "200|401"; then
        echo -e "${GREEN}✓${NC} API is running at $API_URL"
    else
        echo -e "${RED}✗${NC} API is not running at $API_URL"
        return 1
    fi

    # Check Redis
    if curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/health/redis" | grep -q "200"; then
        echo -e "${GREEN}✓${NC} Redis is running"
    else
        echo -e "${YELLOW}⚠${NC} Redis health check failed (may still be functional)"
    fi
}

# Function to run basic logout test
run_basic_logout_test() {
    print_section "Running Basic Logout Test"

    echo "Running: npx playwright test --config=playwright.staging.config.ts tests/e2e-staging/01-authentication.staging.spec.ts -g 'should logout successfully'"
    npx playwright test --config=playwright.staging.config.ts tests/e2e-staging/01-authentication.staging.spec.ts -g "should logout successfully" || {
        echo -e "${RED}✗${NC} Basic logout test failed"
        return 1
    }
    echo -e "${GREEN}✓${NC} Basic logout test passed"
}

# Function to run comprehensive logout tests
run_comprehensive_logout_tests() {
    print_section "Running Comprehensive Logout Tests"

    echo "Running: npx playwright test --config=playwright.staging.config.ts tests/e2e-staging/02-logout-flow.staging.spec.ts"
    npx playwright test --config=playwright.staging.config.ts tests/e2e-staging/02-logout-flow.staging.spec.ts || {
        echo -e "${RED}✗${NC} Comprehensive logout tests failed"
        return 1
    }
    echo -e "${GREEN}✓${NC} Comprehensive logout tests passed"
}

# Function to run debug logout test
run_debug_logout_test() {
    print_section "Running Debug Logout Test"

    echo "Running: npx playwright test --config=playwright.staging.config.ts tests/e2e-staging/debug-logout.staging.spec.ts --headed"
    npx playwright test --config=playwright.staging.config.ts tests/e2e-staging/debug-logout.staging.spec.ts --headed || {
        echo -e "${RED}✗${NC} Debug logout test failed"
        return 1
    }
    echo -e "${GREEN}✓${NC} Debug logout test passed"
}

# Function to run all logout tests
run_all_logout_tests() {
    print_section "Running All Logout Tests"

    echo "Running: npx playwright test --config=playwright.staging.config.ts --grep 'Logout|logout'"
    npx playwright test --config=playwright.staging.config.ts --grep "Logout|logout" || {
        echo -e "${RED}✗${NC} Some logout tests failed"
        return 1
    }
    echo -e "${GREEN}✓${NC} All logout tests passed"
}

# Function to generate test report
generate_report() {
    print_section "Test Report"

    if [ -f "playwright-staging-report/index.html" ]; then
        echo -e "${GREEN}✓${NC} Test report generated at: playwright-staging-report/index.html"
        echo "  Open in browser: file://$(pwd)/playwright-staging-report/index.html"
    else
        echo -e "${YELLOW}⚠${NC} Test report not found"
    fi
}

# Main execution
main() {
    local test_type="${1:-all}"

    # Check services first
    if ! check_services; then
        echo -e "\n${RED}Services are not running. Please start the staging environment first.${NC}"
        echo "Run: docker-compose -f docker-compose.staging.yml up -d"
        exit 1
    fi

    # Run tests based on argument
    case "$test_type" in
        basic)
            run_basic_logout_test
            ;;
        comprehensive)
            run_comprehensive_logout_tests
            ;;
        debug)
            run_debug_logout_test
            ;;
        all)
            run_basic_logout_test
            run_comprehensive_logout_tests
            ;;
        *)
            echo -e "${RED}Unknown test type: $test_type${NC}"
            echo "Usage: $0 [basic|comprehensive|debug|all]"
            exit 1
            ;;
    esac

    # Generate report
    generate_report

    print_section "Testing Complete"
    echo -e "${GREEN}✓${NC} Logout flow testing completed successfully"
}

# Run main function
main "$@"
