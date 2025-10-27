#!/bin/bash
# TTA Post-Deployment Tests Runner
#
# Standalone script for running post-deployment tests without full verification.
#
# Usage:
#   ./scripts/run-post-deployment-tests.sh [options]
#
# Options:
#   -e, --environment ENV    Environment to test (staging, production, local)
#   -a, --api-url URL        API base URL
#   -f, --frontend-url URL   Frontend base URL
#   -m, --markers MARKERS    Pytest markers to use
#   -h, --help               Show this help message

set -e

# Default values
ENVIRONMENT="staging"
API_URL=""
FRONTEND_URL=""
MARKERS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -a|--api-url)
            API_URL="$2"
            shift 2
            ;;
        -f|--frontend-url)
            FRONTEND_URL="$2"
            shift 2
            ;;
        -m|--markers)
            MARKERS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -e, --environment ENV    Environment to test (staging, production, local)"
            echo "  -a, --api-url URL        API base URL"
            echo "  -f, --frontend-url URL   Frontend base URL"
            echo "  -m, --markers MARKERS    Pytest markers to use"
            echo "  -h, --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 -e staging"
            echo "  $0 -e production -m 'not neo4j'"
            echo "  $0 -a http://localhost:8081 -f http://localhost:3001"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Set environment variables
export DEPLOYMENT_ENV="$ENVIRONMENT"

if [ -n "$API_URL" ]; then
    export API_BASE_URL="$API_URL"
fi

if [ -n "$FRONTEND_URL" ]; then
    export FRONTEND_BASE_URL="$FRONTEND_URL"
fi

# Build pytest command
PYTEST_CMD="uv run pytest tests/post_deployment/ -v --tb=short"

if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m '$MARKERS'"
fi

# Add HTML report
PYTEST_CMD="$PYTEST_CMD --html=post-deployment-report.html --self-contained-html"

# Run tests
echo "Running post-deployment tests..."
echo "Environment: $ENVIRONMENT"
echo "API URL: ${API_BASE_URL:-default}"
echo "Frontend URL: ${FRONTEND_BASE_URL:-default}"
echo ""

eval $PYTEST_CMD
