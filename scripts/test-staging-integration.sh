#!/bin/bash
# TTA Staging Integration Test Suite
# Tests comprehensive functionality after deployment

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')] ✅ $1${NC}"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️  $1${NC}"; }
error() { echo -e "${RED}[$(date '+%H:%M:%S')] ❌ $1${NC}"; }
info() { echo -e "${BLUE}[$(date '+%H:%M:%S')] ℹ️  $1${NC}"; }

PROJECT_ROOT="/home/thein/recovered-tta-storytelling"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.staging-homelab.yml"
COMPOSE_PROJECT="tta-staging-homelab"
API_URL="http://localhost:8081"
FRONTEND_URL="http://localhost:3001"

cd "$PROJECT_ROOT"

echo "========================================================================"
echo "  TTA STAGING INTEGRATION TEST SUITE"
echo "========================================================================"
echo ""

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    local test_name="$1"
    local test_command="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    info "Test $TOTAL_TESTS: $test_name"

    if eval "$test_command" > /dev/null 2>&1; then
        log "✓ PASSED: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        error "✗ FAILED: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "========================================================================"
echo "  TEST SUITE 1: HEALTH & CONNECTIVITY"
echo "========================================================================"
echo ""

run_test "Health endpoint responding" "curl -f -s $API_URL/health"
run_test "API docs accessible" "curl -f -s $API_URL/docs"
run_test "Metrics endpoint responding" "curl -f -s $API_URL/metrics"
run_test "Root endpoint responding" "curl -f -s $API_URL/"

echo ""
echo "========================================================================"
echo "  TEST SUITE 2: DATABASE CONNECTIVITY"
echo "========================================================================"
echo ""

run_test "Redis connection" "docker-compose -f $COMPOSE_FILE -p $COMPOSE_PROJECT exec -T redis-staging redis-cli ping"
run_test "PostgreSQL connection" "docker-compose -f $COMPOSE_FILE -p $COMPOSE_PROJECT exec -T postgres-staging psql -U tta_staging_user -d tta_staging -c 'SELECT 1;'"
run_test "Neo4j connection" "curl -f -s http://localhost:7475/"

echo ""
echo "========================================================================"
echo "  TEST SUITE 3: CONTAINER HEALTH"
echo "========================================================================"
echo ""

run_test "Player API container healthy" "docker inspect --format='{{.State.Health.Status}}' tta-staging-player-api | grep -q healthy"
run_test "PostgreSQL container healthy" "docker inspect --format='{{.State.Health.Status}}' tta-staging-postgres | grep -q healthy"
run_test "Redis container healthy" "docker inspect --format='{{.State.Health.Status}}' tta-staging-redis | grep -q healthy"
run_test "Neo4j container healthy" "docker inspect --format='{{.State.Health.Status}}' tta-staging-neo4j | grep -q healthy"

echo ""
echo "========================================================================"
echo "  TEST SUITE 4: LOG ANALYSIS"
echo "========================================================================"
echo ""

# Check for errors in logs
error_count=$(docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" logs --tail=200 player-api-staging 2>&1 | grep -i "error" | grep -v "0 errors" | wc -l)

if [[ $error_count -eq 0 ]]; then
    log "✓ PASSED: No errors in recent logs"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    warn "⚠️  WARNING: Found $error_count error messages in logs"
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" logs --tail=200 player-api-staging 2>&1 | grep -i "error" | grep -v "0 errors" | head -5
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "========================================================================"
echo "  TEST SUITE 5: PERFORMANCE BASELINE"
echo "========================================================================"
echo ""

info "Measuring health endpoint response time..."
response_time=$(curl -o /dev/null -s -w '%{time_total}\n' $API_URL/health)
log "Health endpoint response time: ${response_time}s"

info "Checking container resource usage..."
docker stats tta-staging-player-api --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "========================================================================"
echo "  TEST RESULTS SUMMARY"
echo "========================================================================"
echo ""

echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"
echo ""

if [[ $FAILED_TESTS -eq 0 ]]; then
    log "✅ ALL INTEGRATION TESTS PASSED!"
    echo ""
    log "Staging environment is ready for comprehensive user journey testing."
    echo ""
    echo "Next Steps:"
    echo "  1. Manual testing: Navigate to $FRONTEND_URL"
    echo "  2. Test OAuth sign-in flow"
    echo "  3. Test gameplay functionality"
    echo "  4. Verify database persistence"
    echo "  5. Monitor for 24 hours before production deployment"
    echo ""
    exit 0
else
    error "❌ SOME TESTS FAILED!"
    echo ""
    error "Please review failed tests and investigate issues before proceeding."
    echo ""
    echo "Troubleshooting:"
    echo "  - Check logs: docker-compose -f $COMPOSE_FILE -p $COMPOSE_PROJECT logs player-api-staging"
    echo "  - Check container status: docker ps --filter 'name=staging'"
    echo "  - Review deployment report: /tmp/staging_deployment_final_report.md"
    echo ""
    exit 1
fi
