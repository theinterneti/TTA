#!/bin/bash

# TTA Franchise World System - Deployment Validation Script
# Comprehensive validation of the production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_URL="http://localhost"
API_URL="$BASE_URL/api/v1"
BRIDGE_URL="$BASE_URL/bridge"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test function wrapper
run_test() {
    local test_name="$1"
    local test_function="$2"

    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    log_info "Running test: $test_name"

    if $test_function; then
        log_success "✓ $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "✗ $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Docker container health checks
test_containers_running() {
    local containers=(
        "tta-franchise-api"
        "tta-franchise-bridge"
        "tta-redis"
        "tta-neo4j"
        "tta-nginx"
        "tta-prometheus"
        "tta-grafana"
    )

    for container in "${containers[@]}"; do
        if ! docker ps --format "table {{.Names}}" | grep -q "^$container$"; then
            log_error "Container $container is not running"
            return 1
        fi
    done

    return 0
}

# Health endpoint tests
test_health_endpoints() {
    # Test main health endpoint
    if ! curl -f -s "$BASE_URL/health" > /dev/null; then
        log_error "Main health endpoint failed"
        return 1
    fi

    # Test API health
    if ! curl -f -s "$API_URL/../health" > /dev/null; then
        log_error "API health endpoint failed"
        return 1
    fi

    # Test bridge health
    if ! curl -f -s "$BRIDGE_URL/health" > /dev/null; then
        log_error "Bridge health endpoint failed"
        return 1
    fi

    return 0
}

# API endpoint tests
test_api_endpoints() {
    # Test franchise worlds listing
    if ! curl -f -s "$API_URL/franchise-worlds/" > /dev/null; then
        log_error "Franchise worlds listing failed"
        return 1
    fi

    # Test archetypes listing
    if ! curl -f -s "$API_URL/franchise-worlds/archetypes/" > /dev/null; then
        log_error "Archetypes listing failed"
        return 1
    fi

    # Test world details
    if ! curl -f -s "$API_URL/franchise-worlds/eldermere_realms" > /dev/null; then
        log_error "World details endpoint failed"
        return 1
    fi

    # Test system stats
    if ! curl -f -s "$API_URL/franchise-worlds/stats/summary" > /dev/null; then
        log_error "System stats endpoint failed"
        return 1
    fi

    return 0
}

# Bridge service tests
test_bridge_endpoints() {
    # Test worlds endpoint
    if ! curl -f -s "$BRIDGE_URL/worlds" > /dev/null; then
        log_error "Bridge worlds endpoint failed"
        return 1
    fi

    # Test archetypes endpoint
    if ! curl -f -s "$BRIDGE_URL/archetypes" > /dev/null; then
        log_error "Bridge archetypes endpoint failed"
        return 1
    fi

    # Test system status
    if ! curl -f -s "$BRIDGE_URL/system/status" > /dev/null; then
        log_error "Bridge system status failed"
        return 1
    fi

    return 0
}

# Database connectivity tests
test_database_connectivity() {
    # Test Redis connectivity
    if ! docker exec tta-redis redis-cli ping | grep -q "PONG"; then
        log_error "Redis connectivity failed"
        return 1
    fi

    # Test Neo4j connectivity
    if ! docker exec tta-neo4j cypher-shell -u neo4j -p "${NEO4J_PASSWORD:-password}" "RETURN 1" > /dev/null 2>&1; then
        log_error "Neo4j connectivity failed"
        return 1
    fi

    return 0
}

# Performance tests
test_response_times() {
    local max_response_time=2000  # 2 seconds in milliseconds

    # Test API response time
    local api_time=$(curl -o /dev/null -s -w "%{time_total}" "$API_URL/franchise-worlds/")
    local api_time_ms=$(echo "$api_time * 1000" | bc -l | cut -d. -f1)

    if [ "$api_time_ms" -gt "$max_response_time" ]; then
        log_error "API response time too slow: ${api_time_ms}ms"
        return 1
    fi

    # Test bridge response time
    local bridge_time=$(curl -o /dev/null -s -w "%{time_total}" "$BRIDGE_URL/worlds")
    local bridge_time_ms=$(echo "$bridge_time * 1000" | bc -l | cut -d. -f1)

    if [ "$bridge_time_ms" -gt "$max_response_time" ]; then
        log_error "Bridge response time too slow: ${bridge_time_ms}ms"
        return 1
    fi

    return 0
}

# Data integrity tests
test_data_integrity() {
    # Test that we have the expected number of worlds
    local worlds_count=$(curl -s "$API_URL/franchise-worlds/" | jq length)
    if [ "$worlds_count" -ne 5 ]; then
        log_error "Expected 5 worlds, found $worlds_count"
        return 1
    fi

    # Test that we have the expected number of archetypes
    local archetypes_count=$(curl -s "$API_URL/franchise-worlds/archetypes/" | jq length)
    if [ "$archetypes_count" -ne 5 ]; then
        log_error "Expected 5 archetypes, found $archetypes_count"
        return 1
    fi

    # Test world validation
    local validation_result=$(curl -s -X POST "$API_URL/franchise-worlds/eldermere_realms/validate" | jq -r '.is_valid')
    if [ "$validation_result" != "true" ]; then
        log_error "World validation failed"
        return 1
    fi

    return 0
}

# Security tests
test_security_headers() {
    # Test that security headers are present
    local headers=$(curl -I -s "$BASE_URL/health")

    if ! echo "$headers" | grep -q "X-Frame-Options"; then
        log_error "X-Frame-Options header missing"
        return 1
    fi

    if ! echo "$headers" | grep -q "X-Content-Type-Options"; then
        log_error "X-Content-Type-Options header missing"
        return 1
    fi

    return 0
}

# Monitoring tests
test_monitoring_endpoints() {
    # Test Prometheus metrics
    if ! curl -f -s "$BASE_URL:9090/metrics" > /dev/null; then
        log_error "Prometheus metrics endpoint failed"
        return 1
    fi

    # Test Grafana
    if ! curl -f -s "$BASE_URL:3000/api/health" > /dev/null; then
        log_error "Grafana health endpoint failed"
        return 1
    fi

    return 0
}

# Load test (basic)
test_basic_load() {
    log_info "Running basic load test (10 concurrent requests)..."

    # Use Apache Bench if available, otherwise skip
    if command -v ab &> /dev/null; then
        local result=$(ab -n 10 -c 5 -q "$API_URL/franchise-worlds/" 2>&1)
        if echo "$result" | grep -q "Failed requests: 0"; then
            return 0
        else
            log_error "Load test failed"
            return 1
        fi
    else
        log_warning "Apache Bench not available, skipping load test"
        return 0
    fi
}

# Backup system test
test_backup_system() {
    # Test backup script exists and is executable
    if [ ! -x "$SCRIPT_DIR/backup.sh" ]; then
        log_error "Backup script not found or not executable"
        return 1
    fi

    # Test backup directory exists
    if ! docker exec tta-backup ls /app/backups > /dev/null 2>&1; then
        log_error "Backup directory not accessible"
        return 1
    fi

    return 0
}

# Main validation function
main() {
    log_info "Starting TTA Franchise World System deployment validation..."
    echo

    # Source environment if available
    if [ -f "$SCRIPT_DIR/.env" ]; then
        source "$SCRIPT_DIR/.env"
    fi

    # Run all tests
    run_test "Container Health Check" test_containers_running
    run_test "Health Endpoints" test_health_endpoints
    run_test "API Endpoints" test_api_endpoints
    run_test "Bridge Service Endpoints" test_bridge_endpoints
    run_test "Database Connectivity" test_database_connectivity
    run_test "Response Times" test_response_times
    run_test "Data Integrity" test_data_integrity
    run_test "Security Headers" test_security_headers
    run_test "Monitoring Endpoints" test_monitoring_endpoints
    run_test "Basic Load Test" test_basic_load
    run_test "Backup System" test_backup_system

    # Display results
    echo
    log_info "Validation Results:"
    echo "  Total Tests: $TESTS_TOTAL"
    echo "  Passed: $TESTS_PASSED"
    echo "  Failed: $TESTS_FAILED"
    echo

    if [ $TESTS_FAILED -eq 0 ]; then
        log_success "🎉 All validation tests passed! Deployment is ready for production."
        echo
        echo "🌐 Service URLs:"
        echo "   • API: $API_URL/"
        echo "   • Bridge: $BRIDGE_URL/"
        echo "   • Grafana: $BASE_URL:3000/"
        echo "   • Prometheus: $BASE_URL:9090/"
        echo
        return 0
    else
        log_error "❌ $TESTS_FAILED validation test(s) failed. Please review and fix issues before production deployment."
        return 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    --quick)
        log_info "Running quick validation (essential tests only)..."
        run_test "Container Health Check" test_containers_running
        run_test "Health Endpoints" test_health_endpoints
        run_test "API Endpoints" test_api_endpoints
        ;;
    --security)
        log_info "Running security validation..."
        run_test "Security Headers" test_security_headers
        ;;
    --performance)
        log_info "Running performance validation..."
        run_test "Response Times" test_response_times
        run_test "Basic Load Test" test_basic_load
        ;;
    --help)
        echo "TTA Franchise World System Deployment Validation"
        echo
        echo "Usage: $0 [OPTION]"
        echo
        echo "Options:"
        echo "  (no option)  Full validation suite"
        echo "  --quick      Quick validation (essential tests only)"
        echo "  --security   Security-focused validation"
        echo "  --performance Performance-focused validation"
        echo "  --help       Show this help message"
        ;;
    *)
        main
        ;;
esac
