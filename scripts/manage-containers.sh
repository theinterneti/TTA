#!/bin/bash

# TTA Container Management Script
# Provides easy management of Docker containers for testing and development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_TEST_FILE="docker-compose.test.yml"
COMPOSE_DEV_FILE="docker-compose.dev.yml"
PROJECT_NAME="tta"

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
}

check_compose_file() {
    local file=$1
    if [[ ! -f "$file" ]]; then
        log_error "Docker Compose file not found: $file"
        exit 1
    fi
}

show_usage() {
    echo "TTA Container Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [test|dev]     Start containers (default: test)"
    echo "  stop [test|dev]      Stop containers (default: test)"
    echo "  restart [test|dev]   Restart containers (default: test)"
    echo "  status [test|dev]    Show container status (default: both)"
    echo "  logs [service]       Show logs for service (neo4j, redis, or all)"
    echo "  health               Check container health"
    echo "  clean                Stop and remove containers, networks, and volumes"
    echo "  reset                Reset all data (clean + remove volumes)"
    echo "  shell [service]      Open shell in container (neo4j or redis)"
    echo "  test-connection      Test service connections"
    echo ""
    echo "Examples:"
    echo "  $0 start test        # Start test environment"
    echo "  $0 start dev         # Start development environment"
    echo "  $0 logs neo4j        # Show Neo4j logs"
    echo "  $0 health            # Check all container health"
    echo "  $0 test-connection   # Test service connectivity"
}

start_containers() {
    local env=${1:-test}
    local compose_file
    local env_file

    if [[ "$env" == "dev" ]]; then
        compose_file=$COMPOSE_DEV_FILE
        env_file=".env.dev"
        log_info "Starting development environment..."
    else
        compose_file=$COMPOSE_TEST_FILE
        env_file=".env.test"
        log_info "Starting test environment..."
    fi

    check_compose_file "$compose_file"

    # Check if environment file exists
    if [[ -f "$env_file" ]]; then
        log_info "Using environment file: $env_file"
        export $(grep -v '^#' "$env_file" | xargs)
    else
        log_warning "Environment file $env_file not found, using defaults"
    fi

    log_info "Pulling latest images..."
    docker-compose -f "$compose_file" -p "${PROJECT_NAME}-${env}" pull

    log_info "Starting containers..."
    docker-compose -f "$compose_file" -p "${PROJECT_NAME}-${env}" up -d

    log_success "Containers started successfully"

    # Wait for health checks
    log_info "Waiting for services to become healthy..."
    sleep 5
    show_health "$env"
}

stop_containers() {
    local env=${1:-test}
    local compose_file

    if [[ "$env" == "dev" ]]; then
        compose_file=$COMPOSE_DEV_FILE
        log_info "Stopping development environment..."
    else
        compose_file=$COMPOSE_TEST_FILE
        log_info "Stopping test environment..."
    fi

    check_compose_file "$compose_file"

    docker-compose -f "$compose_file" -p "${PROJECT_NAME}-${env}" down
    log_success "Containers stopped successfully"
}

restart_containers() {
    local env=${1:-test}
    log_info "Restarting $env environment..."
    stop_containers "$env"
    sleep 2
    start_containers "$env"
}

show_status() {
    local env=${1:-both}

    if [[ "$env" == "both" || "$env" == "test" ]]; then
        log_info "Test Environment Status:"
        if docker-compose -f "$COMPOSE_TEST_FILE" -p "${PROJECT_NAME}-test" ps 2>/dev/null; then
            echo ""
        else
            echo "  No test containers running"
        fi
    fi

    if [[ "$env" == "both" || "$env" == "dev" ]]; then
        log_info "Development Environment Status:"
        if docker-compose -f "$COMPOSE_DEV_FILE" -p "${PROJECT_NAME}-dev" ps 2>/dev/null; then
            echo ""
        else
            echo "  No development containers running"
        fi
    fi
}

show_logs() {
    local service=${1:-all}
    local env="test"

    # Try to determine which environment is running
    if docker ps --format "table {{.Names}}" | grep -q "tta-.*-dev"; then
        env="dev"
    fi

    local compose_file
    if [[ "$env" == "dev" ]]; then
        compose_file=$COMPOSE_DEV_FILE
    else
        compose_file=$COMPOSE_TEST_FILE
    fi

    if [[ "$service" == "all" ]]; then
        log_info "Showing logs for all services..."
        docker-compose -f "$compose_file" -p "${PROJECT_NAME}-${env}" logs -f --tail=50
    else
        log_info "Showing logs for $service..."
        docker-compose -f "$compose_file" -p "${PROJECT_NAME}-${env}" logs -f --tail=50 "$service"
    fi
}

show_health() {
    local env=${1:-test}

    log_info "Checking container health..."

    # Check Neo4j
    local neo4j_container="tta-neo4j-${env}"
    if docker ps --format "table {{.Names}}" | grep -q "$neo4j_container"; then
        local neo4j_health=$(docker inspect --format='{{.State.Health.Status}}' "$neo4j_container" 2>/dev/null || echo "no-healthcheck")
        if [[ "$neo4j_health" == "healthy" ]]; then
            log_success "Neo4j: Healthy"
        elif [[ "$neo4j_health" == "starting" ]]; then
            log_warning "Neo4j: Starting..."
        else
            log_error "Neo4j: Unhealthy ($neo4j_health)"
        fi
    else
        log_warning "Neo4j: Not running"
    fi

    # Check Redis
    local redis_container="tta-redis-${env}"
    if docker ps --format "table {{.Names}}" | grep -q "$redis_container"; then
        local redis_health=$(docker inspect --format='{{.State.Health.Status}}' "$redis_container" 2>/dev/null || echo "no-healthcheck")
        if [[ "$redis_health" == "healthy" ]]; then
            log_success "Redis: Healthy"
        elif [[ "$redis_health" == "starting" ]]; then
            log_warning "Redis: Starting..."
        else
            log_error "Redis: Unhealthy ($redis_health)"
        fi
    else
        log_warning "Redis: Not running"
    fi
}

clean_containers() {
    log_warning "This will stop and remove all TTA containers and networks"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up containers..."

        # Stop and remove test environment
        if [[ -f "$COMPOSE_TEST_FILE" ]]; then
            docker-compose -f "$COMPOSE_TEST_FILE" -p "${PROJECT_NAME}-test" down --remove-orphans 2>/dev/null || true
        fi

        # Stop and remove dev environment
        if [[ -f "$COMPOSE_DEV_FILE" ]]; then
            docker-compose -f "$COMPOSE_DEV_FILE" -p "${PROJECT_NAME}-dev" down --remove-orphans 2>/dev/null || true
        fi

        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

reset_data() {
    log_warning "This will remove ALL TTA container data and volumes"
    read -p "Are you sure? This cannot be undone! (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Resetting all data..."

        # Stop and remove everything including volumes
        if [[ -f "$COMPOSE_TEST_FILE" ]]; then
            docker-compose -f "$COMPOSE_TEST_FILE" -p "${PROJECT_NAME}-test" down -v --remove-orphans 2>/dev/null || true
        fi

        if [[ -f "$COMPOSE_DEV_FILE" ]]; then
            docker-compose -f "$COMPOSE_DEV_FILE" -p "${PROJECT_NAME}-dev" down -v --remove-orphans 2>/dev/null || true
        fi

        # Remove any remaining TTA volumes
        docker volume ls -q | grep "tta_" | xargs -r docker volume rm 2>/dev/null || true

        log_success "Data reset completed"
    else
        log_info "Reset cancelled"
    fi
}

open_shell() {
    local service=${1:-neo4j}
    local env="test"

    # Try to determine which environment is running
    if docker ps --format "table {{.Names}}" | grep -q "tta-.*-dev"; then
        env="dev"
    fi

    local container_name="tta-${service}-${env}"

    if ! docker ps --format "table {{.Names}}" | grep -q "$container_name"; then
        log_error "Container $container_name is not running"
        exit 1
    fi

    log_info "Opening shell in $container_name..."

    if [[ "$service" == "neo4j" ]]; then
        docker exec -it "$container_name" /bin/bash
    elif [[ "$service" == "redis" ]]; then
        docker exec -it "$container_name" /bin/sh
    else
        log_error "Unknown service: $service"
        exit 1
    fi
}

test_connection() {
    log_info "Testing service connections..."

    # Test Neo4j HTTP
    if curl -s http://localhost:7474/db/data/ > /dev/null; then
        log_success "Neo4j HTTP: Connected"
    else
        log_error "Neo4j HTTP: Connection failed"
    fi

    # Test Redis
    if command -v redis-cli &> /dev/null; then
        if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
            log_success "Redis: Connected"
        else
            log_error "Redis: Connection failed"
        fi
    else
        log_warning "Redis: redis-cli not available for testing"
    fi

    # Test with Python if available
    if command -v python3 &> /dev/null; then
        log_info "Running Python connectivity test..."
        python3 -c "
import sys
try:
    # Test Neo4j
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'testpassword'))
    driver.verify_connectivity()
    print('✅ Neo4j Bolt: Connected')
    driver.close()
except Exception as e:
    print(f'❌ Neo4j Bolt: {e}')

try:
    # Test Redis
    import redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.ping()
    print('✅ Redis Python: Connected')
except Exception as e:
    print(f'❌ Redis Python: {e}')
"
    fi
}

# Main script logic
check_docker

case "${1:-help}" in
    start)
        start_containers "$2"
        ;;
    stop)
        stop_containers "$2"
        ;;
    restart)
        restart_containers "$2"
        ;;
    status)
        show_status "$2"
        ;;
    logs)
        show_logs "$2"
        ;;
    health)
        show_health "$2"
        ;;
    clean)
        clean_containers
        ;;
    reset)
        reset_data
        ;;
    shell)
        open_shell "$2"
        ;;
    test-connection)
        test_connection
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
