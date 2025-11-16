#!/bin/bash
# TTA Staging Environment - Quick Actions Script
# Provides convenient commands for common staging operations

set -e

PROJECT_ROOT="/home/thein/recovered-tta-storytelling"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Action: Start all staging services
start_all() {
    print_header "Starting All Staging Services"
    docker-compose -f docker-compose.staging-homelab.yml up -d
    print_success "All services started"
    sleep 5
    docker ps --filter "name=staging" --format "table {{.Names}}\t{{.Status}}"
}

# Action: Start application services only
start_apps() {
    print_header "Starting Application Services"
    docker-compose -f docker-compose.staging-homelab.yml up -d player-api-staging player-frontend-staging grafana-staging
    print_success "Application services started"
    sleep 5
    docker ps --filter "name=staging" --format "table {{.Names}}\t{{.Status}}"
}

# Action: Check service status
status() {
    print_header "Staging Services Status"
    docker ps --filter "name=staging" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    echo ""
    print_header "Database Connectivity"

    # Redis
    if docker exec tta-staging-redis redis-cli -a staging_redis_secure_pass_2024 ping 2>/dev/null | grep -q "PONG"; then
        print_success "Redis: Connected"
    else
        print_error "Redis: Not accessible"
    fi

    # Neo4j
    if docker exec tta-staging-neo4j cypher-shell -u neo4j -p staging_neo4j_secure_pass_2024 "RETURN 1" 2>/dev/null | grep -q "1"; then
        print_success "Neo4j: Connected"
    else
        print_error "Neo4j: Not accessible"
    fi

    # Postgres
    if docker exec tta-staging-postgres pg_isready -U tta_staging_user 2>/dev/null | grep -q "accepting"; then
        print_success "Postgres: Connected"
    else
        print_error "Postgres: Not accessible"
    fi
}

# Action: Run unit tests
test_unit() {
    print_header "Running Unit Tests"
    uv run pytest -q -m "not neo4j and not redis and not integration" --tb=short
}

# Action: Run integration tests
test_integration() {
    print_header "Running Integration Tests"
    ENVIRONMENT=staging uv run pytest tests/integration/ -v --tb=short --maxfail=20
}

# Action: Run all tests
test_all() {
    print_header "Running All Tests"
    ENVIRONMENT=staging uv run pytest -v --tb=short
}

# Action: Run code quality checks
check_quality() {
    print_header "Running Code Quality Checks"

    echo "Running Ruff linter..."
    uv run ruff check src/ --output-format=grouped || true

    echo ""
    echo "Running Ruff formatter check..."
    uv run ruff format --check src/ || true
}

# Action: Auto-fix code quality issues
fix_quality() {
    print_header "Auto-fixing Code Quality Issues"

    echo "Running Ruff auto-fix..."
    uv run ruff check src/ --fix

    echo ""
    echo "Running Ruff formatter..."
    uv run ruff format src/

    print_success "Auto-fix complete"
}

# Action: Run comprehensive validation
validate() {
    print_header "Running Comprehensive Validation"
    python3 staging_comprehensive_validation.py
}

# Action: View logs
logs() {
    SERVICE=${1:-""}
    if [ -z "$SERVICE" ]; then
        print_info "Available services:"
        docker ps --filter "name=staging" --format "  - {{.Names}}"
        echo ""
        print_info "Usage: $0 logs <service-name>"
        return
    fi

    print_header "Logs for $SERVICE"
    docker logs --tail 100 -f "$SERVICE"
}

# Action: Stop all staging services
stop() {
    print_header "Stopping All Staging Services"
    docker-compose -f docker-compose.staging-homelab.yml down
    print_success "All services stopped"
}

# Action: Restart all staging services
restart() {
    print_header "Restarting All Staging Services"
    docker-compose -f docker-compose.staging-homelab.yml restart
    print_success "All services restarted"
    sleep 5
    docker ps --filter "name=staging" --format "table {{.Names}}\t{{.Status}}"
}

# Action: Health check
health() {
    print_header "Health Check"

    # Check if player-api is running
    if docker ps --filter "name=tta-staging-player-api" --filter "status=running" | grep -q "tta-staging-player-api"; then
        print_info "Checking Player API health..."
        if curl -sf http://localhost:3004/health > /dev/null 2>&1; then
            print_success "Player API: Healthy"
        else
            print_warning "Player API: Running but not responding"
        fi
    else
        print_warning "Player API: Not running"
    fi

    # Check if player-frontend is running
    if docker ps --filter "name=tta-staging-player-frontend" --filter "status=running" | grep -q "tta-staging-player-frontend"; then
        print_info "Checking Player Frontend..."
        if curl -sf http://localhost:3000 > /dev/null 2>&1; then
            print_success "Player Frontend: Healthy"
        else
            print_warning "Player Frontend: Running but not responding"
        fi
    else
        print_warning "Player Frontend: Not running"
    fi

    # Check databases
    status
}

# Action: Show help
help() {
    cat << EOF
TTA Staging Environment - Quick Actions

Usage: $0 <action> [options]

Actions:
  start-all       Start all staging services
  start-apps      Start application services only (API, Frontend, Grafana)
  status          Show status of all staging services
  health          Perform health checks on services

  test-unit       Run unit tests
  test-integration Run integration tests
  test-all        Run all tests

  check-quality   Run code quality checks (Ruff)
  fix-quality     Auto-fix code quality issues

  validate        Run comprehensive validation

  logs <service>  View logs for a specific service
  restart         Restart all staging services
  stop            Stop all staging services

  help            Show this help message

Examples:
  $0 start-apps              # Start application services
  $0 status                  # Check service status
  $0 test-integration        # Run integration tests
  $0 logs tta-staging-redis  # View Redis logs
  $0 health                  # Perform health checks

EOF
}

# Main script logic
ACTION=${1:-help}

case "$ACTION" in
    start-all)
        start_all
        ;;
    start-apps)
        start_apps
        ;;
    status)
        status
        ;;
    health)
        health
        ;;
    test-unit)
        test_unit
        ;;
    test-integration)
        test_integration
        ;;
    test-all)
        test_all
        ;;
    check-quality)
        check_quality
        ;;
    fix-quality)
        fix_quality
        ;;
    validate)
        validate
        ;;
    logs)
        logs "$2"
        ;;
    restart)
        restart
        ;;
    stop)
        stop
        ;;
    help|*)
        help
        ;;
esac
