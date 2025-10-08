#!/bin/bash

# TTA Staging Environment Health Check Script
# Comprehensive health monitoring for homelab staging deployment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.staging-homelab.yml"
COMPOSE_PROJECT="tta-staging-homelab"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Health check configuration
TIMEOUT=30
RETRY_COUNT=3
RETRY_DELAY=5

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] INFO: $1${NC}"
}

# Check if service is running
check_service_running() {
    local service_name="$1"
    local container_name="${COMPOSE_PROJECT}_${service_name}_1"

    ((TOTAL_CHECKS++))

    if docker ps --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        log "✅ Service $service_name is running"
        ((PASSED_CHECKS++))
        return 0
    else
        error "❌ Service $service_name is not running"
        ((FAILED_CHECKS++))
        return 1
    fi
}

# Check service health status
check_service_health() {
    local service_name="$1"
    local container_name="${COMPOSE_PROJECT}_${service_name}_1"

    ((TOTAL_CHECKS++))

    local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "no-health-check")

    case "$health_status" in
        "healthy")
            log "✅ Service $service_name is healthy"
            ((PASSED_CHECKS++))
            return 0
            ;;
        "unhealthy")
            error "❌ Service $service_name is unhealthy"
            ((FAILED_CHECKS++))
            return 1
            ;;
        "starting")
            warn "⏳ Service $service_name is starting"
            ((WARNING_CHECKS++))
            return 2
            ;;
        "no-health-check")
            info "ℹ️  Service $service_name has no health check configured"
            ((PASSED_CHECKS++))
            return 0
            ;;
        *)
            warn "❓ Service $service_name has unknown health status: $health_status"
            ((WARNING_CHECKS++))
            return 2
            ;;
    esac
}

# Check HTTP endpoint
check_http_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    ((TOTAL_CHECKS++))

    local response_code
    if response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null); then
        if [[ "$response_code" == "$expected_status" ]]; then
            log "✅ $name endpoint is accessible (HTTP $response_code)"
            ((PASSED_CHECKS++))
            return 0
        else
            error "❌ $name endpoint returned HTTP $response_code (expected $expected_status)"
            ((FAILED_CHECKS++))
            return 1
        fi
    else
        error "❌ $name endpoint is not accessible"
        ((FAILED_CHECKS++))
        return 1
    fi
}

# Check database connection
check_database_connection() {
    local db_type="$1"
    local service_name="$2"
    local connection_command="$3"

    ((TOTAL_CHECKS++))

    if docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T "$service_name" \
        bash -c "$connection_command" > /dev/null 2>&1; then
        log "✅ $db_type database connection successful"
        ((PASSED_CHECKS++))
        return 0
    else
        error "❌ $db_type database connection failed"
        ((FAILED_CHECKS++))
        return 1
    fi
}

# Check resource usage
check_resource_usage() {
    local service_name="$1"
    local container_name="${COMPOSE_PROJECT}_${service_name}_1"
    local cpu_threshold="${2:-80}"
    local memory_threshold="${3:-85}"

    ((TOTAL_CHECKS++))

    # Get container stats
    local stats
    if stats=$(docker stats "$container_name" --no-stream --format "table {{.CPUPerc}}\t{{.MemPerc}}" 2>/dev/null | tail -n 1); then
        local cpu_usage=$(echo "$stats" | awk '{print $1}' | sed 's/%//')
        local memory_usage=$(echo "$stats" | awk '{print $2}' | sed 's/%//')

        # Check CPU usage
        if (( $(echo "$cpu_usage > $cpu_threshold" | bc -l) )); then
            warn "⚠️  Service $service_name CPU usage is high: ${cpu_usage}%"
            ((WARNING_CHECKS++))
        fi

        # Check memory usage
        if (( $(echo "$memory_usage > $memory_threshold" | bc -l) )); then
            warn "⚠️  Service $service_name memory usage is high: ${memory_usage}%"
            ((WARNING_CHECKS++))
        fi

        info "📊 Service $service_name: CPU ${cpu_usage}%, Memory ${memory_usage}%"
        ((PASSED_CHECKS++))
        return 0
    else
        warn "❓ Could not get resource usage for service $service_name"
        ((WARNING_CHECKS++))
        return 2
    fi
}

# Check disk space
check_disk_space() {
    local threshold="${1:-80}"

    ((TOTAL_CHECKS++))

    local disk_usage
    disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

    if [[ $disk_usage -gt $threshold ]]; then
        if [[ $disk_usage -gt 90 ]]; then
            error "❌ Disk usage is critically high: ${disk_usage}%"
            ((FAILED_CHECKS++))
            return 1
        else
            warn "⚠️  Disk usage is high: ${disk_usage}%"
            ((WARNING_CHECKS++))
            return 2
        fi
    else
        log "✅ Disk usage is normal: ${disk_usage}%"
        ((PASSED_CHECKS++))
        return 0
    fi
}

# Check Docker daemon
check_docker_daemon() {
    ((TOTAL_CHECKS++))

    if docker info > /dev/null 2>&1; then
        log "✅ Docker daemon is running"
        ((PASSED_CHECKS++))
        return 0
    else
        error "❌ Docker daemon is not accessible"
        ((FAILED_CHECKS++))
        return 1
    fi
}

# Check network connectivity
check_network_connectivity() {
    local service1="$1"
    local service2="$2"
    local port="$3"

    ((TOTAL_CHECKS++))

    local container1="${COMPOSE_PROJECT}_${service1}_1"
    local container2="${COMPOSE_PROJECT}_${service2}_1"

    if docker exec "$container1" nc -z "$service2" "$port" > /dev/null 2>&1; then
        log "✅ Network connectivity from $service1 to $service2:$port"
        ((PASSED_CHECKS++))
        return 0
    else
        error "❌ Network connectivity failed from $service1 to $service2:$port"
        ((FAILED_CHECKS++))
        return 1
    fi
}

# Main health check function
run_health_checks() {
    log "🏥 Starting TTA Staging Environment Health Check"
    log "Timestamp: $(date)"
    log "Project: $COMPOSE_PROJECT"
    echo ""

    # Check Docker daemon
    info "🐳 Checking Docker daemon..."
    check_docker_daemon
    echo ""

    # Check disk space
    info "💾 Checking disk space..."
    check_disk_space 80
    echo ""

    # Check service status
    info "🔍 Checking service status..."
    local services=(
        "neo4j-staging"
        "redis-staging"
        "postgres-staging"
        "player-api-staging"
        "player-frontend-staging"
        "prometheus-staging"
        "grafana-staging"
        "nginx-staging"
    )

    for service in "${services[@]}"; do
        check_service_running "$service"
        check_service_health "$service"
    done
    echo ""

    # Check HTTP endpoints
    info "🌐 Checking HTTP endpoints..."
    check_http_endpoint "Player API Health" "http://localhost:8081/health"
    check_http_endpoint "Player Frontend Health" "http://localhost:3001/health"
    check_http_endpoint "Prometheus" "http://localhost:9091/-/healthy"
    check_http_endpoint "Grafana" "http://localhost:3001/api/health"
    check_http_endpoint "Neo4j Browser" "http://localhost:7475/browser/"
    echo ""

    # Check database connections
    info "🗄️  Checking database connections..."
    check_database_connection "Neo4j" "neo4j-staging" "cypher-shell -u neo4j -p \${NEO4J_STAGING_PASSWORD:-staging_neo4j_secure_pass} 'RETURN 1'"
    check_database_connection "Redis" "redis-staging" "redis-cli ping"
    check_database_connection "PostgreSQL" "postgres-staging" "pg_isready -U tta_staging_user"
    echo ""

    # Check network connectivity
    info "🔗 Checking network connectivity..."
    check_network_connectivity "player-api-staging" "neo4j-staging" "7687"
    check_network_connectivity "player-api-staging" "redis-staging" "6379"
    check_network_connectivity "player-api-staging" "postgres-staging" "5432"
    echo ""

    # Check resource usage
    info "📊 Checking resource usage..."
    for service in "${services[@]}"; do
        if check_service_running "$service" > /dev/null 2>&1; then
            check_resource_usage "$service" 80 85
        fi
    done
    echo ""

    # Summary
    log "📋 Health Check Summary"
    log "Total checks: $TOTAL_CHECKS"
    log "Passed: $PASSED_CHECKS"
    log "Failed: $FAILED_CHECKS"
    log "Warnings: $WARNING_CHECKS"
    echo ""

    # Overall status
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        if [[ $WARNING_CHECKS -eq 0 ]]; then
            log "🎉 All health checks passed! System is healthy."
            return 0
        else
            warn "⚠️  Health checks passed with $WARNING_CHECKS warnings."
            return 1
        fi
    else
        error "❌ Health checks failed! $FAILED_CHECKS critical issues found."
        return 2
    fi
}

# Continuous monitoring mode
continuous_monitoring() {
    local interval="${1:-60}"

    log "🔄 Starting continuous monitoring (interval: ${interval}s)"
    log "Press Ctrl+C to stop"
    echo ""

    while true; do
        run_health_checks
        echo ""
        log "⏰ Next check in ${interval} seconds..."
        sleep "$interval"
        echo ""
        echo "=================================================="
        echo ""
    done
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    --continuous INTERVAL   Run continuous monitoring (default interval: 60s)
    --timeout SECONDS       Set timeout for checks (default: 30s)
    --help                  Show this help message

Examples:
    $0                      # Run single health check
    $0 --continuous 30      # Run continuous monitoring every 30 seconds
    $0 --timeout 60         # Run with 60 second timeout

EOF
}

# Main function
main() {
    local continuous=false
    local interval=60

    while [[ $# -gt 0 ]]; do
        case $1 in
            --continuous)
                continuous=true
                if [[ -n "${2:-}" ]] && [[ "$2" =~ ^[0-9]+$ ]]; then
                    interval="$2"
                    shift
                fi
                shift
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Check if bc is available for resource usage calculations
    if ! command -v bc &> /dev/null; then
        warn "bc command not found, resource usage checks will be limited"
    fi

    if [[ "$continuous" == true ]]; then
        continuous_monitoring "$interval"
    else
        run_health_checks
        exit $?
    fi
}

# Handle Ctrl+C gracefully
trap 'echo ""; log "Health check interrupted by user"; exit 0' INT

# Run main function
main "$@"
