#!/bin/bash
# TTA Post-Deployment Verification Script
#
# This script runs automated post-deployment tests to verify that critical
# fixes (Issues #2, #3, #4) remain effective after deployment.
#
# Usage:
#   ./scripts/verify-deployment.sh [environment]
#
# Arguments:
#   environment - Deployment environment to test (staging, production, local)
#                 Default: staging
#
# Environment Variables:
#   API_BASE_URL       - API base URL (overrides default)
#   FRONTEND_BASE_URL  - Frontend base URL (overrides default)
#   NEO4J_URI          - Neo4j connection URI
#   NEO4J_USERNAME     - Neo4j username
#   NEO4J_PASSWORD     - Neo4j password
#   REDIS_HOST         - Redis host
#   REDIS_PORT         - Redis port
#   REDIS_PASSWORD     - Redis password

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default values
ENVIRONMENT="${1:-staging}"
DEPLOYMENT_ENV="${ENVIRONMENT}"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=1

    print_info "Waiting for service at $url..."

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            print_success "Service is ready"
            return 0
        fi

        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo ""
    print_error "Service not ready after $max_attempts attempts"
    return 1
}

# Main script
main() {
    print_header "TTA Post-Deployment Verification"

    print_info "Environment: $ENVIRONMENT"
    print_info "Project Root: $PROJECT_ROOT"
    echo ""

    # Check prerequisites
    print_info "Checking prerequisites..."

    if ! command_exists uv; then
        print_error "UV package manager not found. Please install UV first."
        exit 1
    fi
    print_success "UV found"

    if ! command_exists curl; then
        print_error "curl not found. Please install curl first."
        exit 1
    fi
    print_success "curl found"

    # Set environment-specific URLs if not provided
    if [ -z "$API_BASE_URL" ]; then
        case "$ENVIRONMENT" in
            staging)
                export API_BASE_URL="http://localhost:8081"
                ;;
            production)
                export API_BASE_URL="https://api.tta.example.com"
                ;;
            local)
                export API_BASE_URL="http://localhost:8080"
                ;;
            *)
                print_error "Unknown environment: $ENVIRONMENT"
                print_info "Valid environments: staging, production, local"
                exit 1
                ;;
        esac
    fi

    if [ -z "$FRONTEND_BASE_URL" ]; then
        case "$ENVIRONMENT" in
            staging)
                export FRONTEND_BASE_URL="http://localhost:3001"
                ;;
            production)
                export FRONTEND_BASE_URL="https://tta.example.com"
                ;;
            local)
                export FRONTEND_BASE_URL="http://localhost:3000"
                ;;
        esac
    fi

    print_info "API URL: $API_BASE_URL"
    print_info "Frontend URL: $FRONTEND_BASE_URL"
    echo ""

    # Wait for services to be ready
    print_header "Service Health Checks"

    print_info "Checking API health..."
    if wait_for_service "$API_BASE_URL/api/v1/health/"; then
        print_success "API is healthy"
    else
        print_error "API health check failed"
        print_warning "Continuing with tests anyway..."
    fi

    print_info "Checking frontend..."
    if wait_for_service "$FRONTEND_BASE_URL"; then
        print_success "Frontend is accessible"
    else
        print_error "Frontend health check failed"
        print_warning "Continuing with tests anyway..."
    fi

    echo ""

    # Run post-deployment tests
    print_header "Running Post-Deployment Tests"

    cd "$PROJECT_ROOT"

    # Export environment variables for pytest
    export DEPLOYMENT_ENV="$ENVIRONMENT"

    # Determine test markers based on environment
    if [ "$ENVIRONMENT" = "production" ]; then
        # In production, skip tests that create data
        TEST_MARKERS="-m 'not neo4j'"
        print_warning "Running in production mode - skipping database tests"
    else
        # In staging/local, run all tests
        TEST_MARKERS=""
        print_info "Running all post-deployment tests"
    fi

    # Run tests
    print_info "Executing pytest..."
    echo ""

    if uv run pytest tests/post_deployment/ \
        -v \
        --tb=short \
        $TEST_MARKERS \
        --html=post-deployment-report.html \
        --self-contained-html; then

        print_success "All post-deployment tests passed!"
        TEST_RESULT=0
    else
        print_error "Some post-deployment tests failed"
        TEST_RESULT=1
    fi

    echo ""

    # Generate summary
    print_header "Verification Summary"

    if [ $TEST_RESULT -eq 0 ]; then
        print_success "Deployment verification PASSED"
        print_info "All critical fixes (Issues #2, #3, #4) are working correctly"
    else
        print_error "Deployment verification FAILED"
        print_warning "One or more critical fixes may have regressed"
        print_info "Review the test output above for details"
    fi

    echo ""
    print_info "Detailed test report: $PROJECT_ROOT/post-deployment-report.html"
    echo ""

    # Exit with test result
    exit $TEST_RESULT
}

# Run main function
main "$@"
