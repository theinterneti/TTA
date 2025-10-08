#!/bin/bash

# TTA E2E Test Runner Script
# This script provides convenient commands for running Playwright E2E tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:3000"
FRONTEND_DIR="src/player_experience/frontend"
TEST_DIR="tests/e2e"
REPORT_DIR="test-results"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  TTA E2E Test Suite Runner${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi

    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi

    # Check if Playwright is installed
    if ! npm list @playwright/test &> /dev/null; then
        print_warning "Playwright is not installed. Installing..."
        npm install @playwright/test
    fi

    # Check if browsers are installed
    if ! npx playwright --version &> /dev/null; then
        print_warning "Playwright browsers not installed. Installing..."
        npx playwright install
    fi

    print_success "Prerequisites check completed"
}

start_frontend() {
    print_info "Starting frontend application..."

    if ! curl -s "$BASE_URL" > /dev/null 2>&1; then
        print_info "Frontend not running. Starting..."
        cd "$FRONTEND_DIR"
        npm start &
        FRONTEND_PID=$!
        cd - > /dev/null

        # Wait for frontend to start
        print_info "Waiting for frontend to start..."
        for i in {1..30}; do
            if curl -s "$BASE_URL" > /dev/null 2>&1; then
                print_success "Frontend is running at $BASE_URL"
                return 0
            fi
            sleep 2
        done

        print_error "Frontend failed to start within 60 seconds"
        exit 1
    else
        print_success "Frontend is already running at $BASE_URL"
    fi
}

stop_frontend() {
    if [ ! -z "$FRONTEND_PID" ]; then
        print_info "Stopping frontend application..."
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "Frontend stopped"
    fi
}

run_tests() {
    local test_type="$1"
    local browser="$2"
    local headed="$3"
    local debug="$4"

    print_info "Running $test_type tests..."

    # Build command
    local cmd="npx playwright test"

    # Add test file if specified
    case "$test_type" in
        "auth")
            cmd="$cmd tests/e2e/specs/auth.spec.ts"
            ;;
        "dashboard")
            cmd="$cmd tests/e2e/specs/dashboard.spec.ts"
            ;;
        "character")
            cmd="$cmd tests/e2e/specs/character-management.spec.ts"
            ;;
        "chat")
            cmd="$cmd tests/e2e/specs/chat.spec.ts"
            ;;
        "settings")
            cmd="$cmd tests/e2e/specs/settings.spec.ts"
            ;;
        "accessibility")
            cmd="$cmd tests/e2e/specs/accessibility.spec.ts"
            ;;
        "responsive")
            cmd="$cmd tests/e2e/specs/responsive.spec.ts"
            ;;
        "all")
            # Run all tests
            ;;
        *)
            print_error "Unknown test type: $test_type"
            exit 1
            ;;
    esac

    # Add browser if specified
    if [ ! -z "$browser" ]; then
        cmd="$cmd --project=$browser"
    fi

    # Add headed mode if specified
    if [ "$headed" = "true" ]; then
        cmd="$cmd --headed"
    fi

    # Add debug mode if specified
    if [ "$debug" = "true" ]; then
        cmd="$cmd --debug"
    fi

    # Run the tests
    echo "Executing: $cmd"
    if eval "$cmd"; then
        print_success "$test_type tests completed successfully"
    else
        print_error "$test_type tests failed"
        return 1
    fi
}

generate_report() {
    print_info "Generating test report..."

    if [ -d "$REPORT_DIR" ]; then
        npx playwright show-report
        print_success "Test report generated and opened"
    else
        print_warning "No test results found"
    fi
}

show_help() {
    echo "TTA E2E Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS] [TEST_TYPE]"
    echo ""
    echo "TEST_TYPE:"
    echo "  all           Run all tests (default)"
    echo "  auth          Run authentication tests"
    echo "  dashboard     Run dashboard tests"
    echo "  character     Run character management tests"
    echo "  chat          Run chat/storytelling tests"
    echo "  settings      Run settings tests"
    echo "  accessibility Run accessibility tests"
    echo "  responsive    Run responsive design tests"
    echo ""
    echo "OPTIONS:"
    echo "  -b, --browser BROWSER    Run tests on specific browser (chromium, firefox, webkit)"
    echo "  -h, --headed            Run tests in headed mode (visible browser)"
    echo "  -d, --debug             Run tests in debug mode"
    echo "  -r, --report            Generate and show test report"
    echo "  -s, --skip-start        Skip starting the frontend (assume it's already running)"
    echo "  --help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                      # Run all tests"
    echo "  $0 auth                 # Run authentication tests"
    echo "  $0 -b chromium auth     # Run auth tests on Chromium only"
    echo "  $0 -h -d auth           # Run auth tests in headed debug mode"
    echo "  $0 -r                   # Generate and show test report"
    echo ""
}

cleanup() {
    print_info "Cleaning up..."
    stop_frontend
    exit 0
}

# Trap cleanup on script exit
trap cleanup EXIT INT TERM

# Main script
main() {
    local test_type="all"
    local browser=""
    local headed="false"
    local debug="false"
    local skip_start="false"
    local show_report="false"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -b|--browser)
                browser="$2"
                shift 2
                ;;
            -h|--headed)
                headed="true"
                shift
                ;;
            -d|--debug)
                debug="true"
                shift
                ;;
            -r|--report)
                show_report="true"
                shift
                ;;
            -s|--skip-start)
                skip_start="true"
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            auth|dashboard|character|chat|settings|accessibility|responsive|all)
                test_type="$1"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    print_header

    # Show report only
    if [ "$show_report" = "true" ]; then
        generate_report
        exit 0
    fi

    # Check prerequisites
    check_prerequisites

    # Start frontend if needed
    if [ "$skip_start" = "false" ]; then
        start_frontend
    fi

    # Run tests
    if run_tests "$test_type" "$browser" "$headed" "$debug"; then
        print_success "All tests completed successfully!"

        # Generate report if tests passed
        if [ -d "$REPORT_DIR" ]; then
            print_info "Test report available at: $REPORT_DIR/index.html"
        fi
    else
        print_error "Some tests failed. Check the output above for details."
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
