#!/usr/bin/env bash
# TTA Development Environment Manager
# Manages Redis + Neo4j for TTA agent development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.tta-dev.yml"
ENV_FILE="$PROJECT_ROOT/.env.tta-dev"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  TTA Development Environment${NC}"
    echo -e "${BLUE}========================================${NC}"
}

function print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function print_error() {
    echo -e "${RED}❌ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

function check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi

    print_success "Docker is available"
}

function start_services() {
    print_header
    print_info "Starting TTA development services..."

    check_docker

    # Start services
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

    print_success "Services started!"
    print_info "Waiting for services to be healthy..."
    sleep 5

    status_services
}

function stop_services() {
    print_header
    print_info "Stopping TTA development services..."

    docker compose -f "$COMPOSE_FILE" down

    print_success "Services stopped!"
}

function restart_services() {
    print_header
    print_info "Restarting TTA development services..."

    stop_services
    sleep 2
    start_services
}

function status_services() {
    print_header
    print_info "TTA Development Services Status:\n"

    # Check if containers exist
    if ! docker ps -a --format "{{.Names}}" | grep -q "tta-"; then
        print_warning "No TTA services are running"
        print_info "Run '$0 start' to start services"
        return
    fi

    # Get container status
    echo -e "${BLUE}Container Status:${NC}"
    docker ps -a --filter "name=tta-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "tta-|NAMES"

    echo ""

    # Check health
    print_info "Health Checks:"

    # Redis
    if docker ps --filter "name=tta-redis" --filter "health=healthy" | grep -q tta-redis; then
        print_success "Redis: Healthy"
    elif docker ps --filter "name=tta-redis" | grep -q tta-redis; then
        print_warning "Redis: Starting..."
    else
        print_error "Redis: Not Running"
    fi

    # Neo4j
    if docker ps --filter "name=tta-neo4j" --filter "health=healthy" | grep -q tta-neo4j; then
        print_success "Neo4j: Healthy"
    elif docker ps --filter "name=tta-neo4j" | grep -q tta-neo4j; then
        print_warning "Neo4j: Starting..."
    else
        print_error "Neo4j: Not Running"
    fi

    echo ""
    print_info "Service URLs:"
    echo "  Redis:         redis://localhost:6379"
    echo "  Neo4j Browser: http://localhost:7474"
    echo "  Neo4j Bolt:    bolt://localhost:7687"
    echo ""
    print_info "Credentials (from .env.tta-dev):"
    echo "  Neo4j:  neo4j / tta_dev_neo4j_2024"
}

function logs_services() {
    print_header

    if [ -n "$1" ]; then
        print_info "Showing logs for $1..."
        docker compose -f "$COMPOSE_FILE" logs -f "$1"
    else
        print_info "Showing logs for all services (Ctrl+C to stop)..."
        docker compose -f "$COMPOSE_FILE" logs -f
    fi
}

function test_connections() {
    print_header
    print_info "Testing TTA service connections...\n"

    # Test Redis
    echo -e "${BLUE}Testing Redis...${NC}"
    if docker exec tta-redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
        print_success "Redis connection: OK"

        # Get Redis info
        REDIS_VERSION=$(docker exec tta-redis redis-cli INFO SERVER 2>/dev/null | grep "redis_version" | cut -d: -f2 | tr -d '\r')
        REDIS_KEYS=$(docker exec tta-redis redis-cli DBSIZE 2>/dev/null | cut -d: -f2 | tr -d '\r')
        echo "  Version: $REDIS_VERSION"
        echo "  Keys: $REDIS_KEYS"
    else
        print_error "Redis connection: FAILED"
    fi

    echo ""

    # Test Neo4j
    echo -e "${BLUE}Testing Neo4j...${NC}"
    if docker exec tta-neo4j cypher-shell -u neo4j -p tta_dev_neo4j_2024 "RETURN 1" &>/dev/null; then
        print_success "Neo4j connection: OK"

        # Get Neo4j version
        NEO4J_VERSION=$(docker exec tta-neo4j cypher-shell -u neo4j -p tta_dev_neo4j_2024 "CALL dbms.components() YIELD versions RETURN versions[0]" 2>/dev/null | grep -v "versions" | tr -d ' "')
        echo "  Version: $NEO4J_VERSION"

        # Count nodes
        NODE_COUNT=$(docker exec tta-neo4j cypher-shell -u neo4j -p tta_dev_neo4j_2024 "MATCH (n) RETURN count(n)" 2>/dev/null | tail -1 | tr -d ' ')
        echo "  Nodes: $NODE_COUNT"
    else
        print_error "Neo4j connection: FAILED"
        print_info "Neo4j may still be starting up. Wait 30-60 seconds and try again."
    fi

    echo ""

    # Python connection test
    if command -v uv &> /dev/null; then
        print_info "Running Python connection test..."
        cd "$PROJECT_ROOT"

        # Update .env with correct password
        export NEO4J_PASSWORD=tta_dev_neo4j_2024

        if uv run python scripts/test_database_connections.py 2>/dev/null; then
            print_success "Python connections: OK"
        else
            print_warning "Python connections: Some issues detected"
            print_info "Check output above for details"
        fi
    else
        print_info "UV not found, skipping Python connection test"
    fi
}

function clean_services() {
    print_header
    print_warning "This will stop services and remove volumes (DATA WILL BE DELETED)"
    read -p "Are you sure? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        print_info "Cancelled"
        return
    fi

    print_info "Stopping and removing services..."
    docker compose -f "$COMPOSE_FILE" down -v

    print_success "Services cleaned!"
    print_info "Run '$0 start' to start fresh services"
}

function shell_service() {
    local service=$1

    if [ -z "$service" ]; then
        print_error "Please specify a service: redis or neo4j"
        exit 1
    fi

    case $service in
        redis)
            print_info "Connecting to Redis CLI..."
            docker exec -it tta-redis redis-cli
            ;;
        neo4j)
            print_info "Connecting to Neo4j Cypher Shell..."
            docker exec -it tta-neo4j cypher-shell -u neo4j -p tta_dev_neo4j_2024
            ;;
        *)
            print_error "Unknown service: $service"
            print_info "Available services: redis, neo4j"
            exit 1
            ;;
    esac
}

function usage() {
    print_header
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start       Start TTA development services"
    echo "  stop        Stop TTA development services"
    echo "  restart     Restart TTA development services"
    echo "  status      Show status of services"
    echo "  logs [svc]  Show logs (optionally for specific service)"
    echo "  test        Test database connections"
    echo "  clean       Stop services and remove volumes (DELETES DATA)"
    echo "  shell <svc> Open shell to service (redis|neo4j)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs neo4j"
    echo "  $0 shell redis"
    echo "  $0 test"
    echo ""
}

# Main command dispatcher
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        status_services
        ;;
    logs)
        logs_services "$2"
        ;;
    test)
        test_connections
        ;;
    clean)
        clean_services
        ;;
    shell)
        shell_service "$2"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        print_error "Unknown command: $1"
        usage
        exit 1
        ;;
esac
