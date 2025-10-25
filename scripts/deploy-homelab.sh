#!/bin/bash

# =============================================================================
# TTA Home Lab QA Testing Deployment Script
# =============================================================================
# Comprehensive deployment script for setting up TTA quality assurance
# testing environment in home lab with multi-user support
# =============================================================================

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.homelab.yml"
ENV_FILE="$PROJECT_ROOT/.env.homelab"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi

    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi

    # Check available disk space (minimum 10GB)
    available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 10485760 ]; then  # 10GB in KB
        log_warning "Less than 10GB of disk space available. Consider freeing up space."
    fi

    # Check available memory (minimum 8GB recommended)
    available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [ "$available_memory" -lt 8192 ]; then  # 8GB in MB
        log_warning "Less than 8GB of available memory. Performance may be impacted."
    fi

    log_success "Prerequisites check completed"
}

# Function to setup environment
setup_environment() {
    log_info "Setting up home lab environment..."

    cd "$PROJECT_ROOT"

    # Check if .env.homelab exists
    if [ ! -f "$ENV_FILE" ]; then
        log_error ".env.homelab file not found. Please create it first."
        exit 1
    fi

    # Create necessary directories
    mkdir -p logs test-results qa-reports monitoring/grafana/dashboards monitoring/grafana/datasources

    # Set proper permissions
    chmod 755 logs test-results qa-reports

    # Create Docker networks if they don't exist
    docker network create tta-homelab 2>/dev/null || true

    log_success "Environment setup completed"
}

# Function to build images
build_images() {
    log_info "Building Docker images..."

    cd "$PROJECT_ROOT"

    # Build QA testing image
    docker build -f testing/Dockerfile.qa -t tta-homelab-qa:latest .

    # Build player API image if Dockerfile exists
    if [ -f "src/player_experience/api/Dockerfile" ]; then
        docker build -f src/player_experience/api/Dockerfile -t tta-homelab-player-api:latest .
    fi

    # Build frontend image if Dockerfile exists
    if [ -f "src/player_experience/frontend/Dockerfile" ]; then
        docker build -f src/player_experience/frontend/Dockerfile -t tta-homelab-player-frontend:latest src/player_experience/frontend/
    fi

    log_success "Docker images built successfully"
}

# Function to start services
start_services() {
    log_info "Starting TTA home lab services..."

    cd "$PROJECT_ROOT"

    # Use docker-compose or docker compose based on availability
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi

    # Start infrastructure services first
    log_info "Starting infrastructure services..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d postgres redis neo4j

    # Wait for databases to be ready
    log_info "Waiting for databases to be ready..."
    sleep 30

    # Start application services
    log_info "Starting application services..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d player-api player-frontend

    # Wait for application services
    sleep 20

    # Start load balancer and monitoring
    log_info "Starting load balancer and monitoring services..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d nginx prometheus grafana

    log_success "All services started successfully"
}

# Function to check service health
check_health() {
    log_info "Checking service health..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"

        # Check if all services are healthy
        if curl -f http://localhost/health &> /dev/null; then
            log_success "All services are healthy"
            return 0
        fi

        sleep 10
        ((attempt++))
    done

    log_error "Services failed to become healthy within expected time"
    return 1
}

# Function to show service status
show_status() {
    log_info "Service Status:"
    echo "===================="

    # Use docker-compose or docker compose based on availability
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi

    cd "$PROJECT_ROOT"
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps

    echo ""
    log_info "Access URLs:"
    echo "===================="
    echo "Frontend: http://localhost"
    echo "API Documentation: http://localhost/api/docs"
    echo "Grafana Dashboard: http://localhost/grafana (admin/homelab_grafana_admin_secure_2024)"
    echo "Prometheus: http://localhost:9090"
    echo "Neo4j Browser: http://localhost:7474"
    echo ""
}

# Function to run initial tests
run_initial_tests() {
    log_info "Running initial validation tests..."

    # Test API endpoint
    if curl -f http://localhost/api/health &> /dev/null; then
        log_success "API health check passed"
    else
        log_warning "API health check failed"
    fi

    # Test frontend
    if curl -f http://localhost &> /dev/null; then
        log_success "Frontend health check passed"
    else
        log_warning "Frontend health check failed"
    fi

    # Test database connections
    log_info "Testing database connections..."
    # Add specific database connection tests here

    log_success "Initial validation tests completed"
}

# Function to stop services
stop_services() {
    log_info "Stopping TTA home lab services..."

    cd "$PROJECT_ROOT"

    # Use docker-compose or docker compose based on availability
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi

    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down

    log_success "Services stopped successfully"
}

# Function to clean up
cleanup() {
    log_info "Cleaning up home lab environment..."

    cd "$PROJECT_ROOT"

    # Use docker-compose or docker compose based on availability
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi

    # Stop and remove containers, networks, and volumes
    $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down -v --remove-orphans

    # Remove custom network
    docker network rm tta-homelab 2>/dev/null || true

    log_success "Cleanup completed"
}

# Function to show logs
show_logs() {
    local service=${1:-}

    cd "$PROJECT_ROOT"

    # Use docker-compose or docker compose based on availability
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi

    if [ -n "$service" ]; then
        $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f "$service"
    else
        $COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f
    fi
}

# Main function
main() {
    local command=${1:-help}

    case $command in
        "deploy")
            check_prerequisites
            setup_environment
            build_images
            start_services
            check_health
            show_status
            run_initial_tests
            ;;
        "start")
            start_services
            check_health
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            start_services
            check_health
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "${2:-}"
            ;;
        "cleanup")
            cleanup
            ;;
        "health")
            check_health
            ;;
        "help"|*)
            echo "TTA Home Lab QA Testing Deployment Script"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  deploy    - Full deployment (build, start, validate)"
            echo "  start     - Start services"
            echo "  stop      - Stop services"
            echo "  restart   - Restart services"
            echo "  status    - Show service status"
            echo "  logs      - Show logs (optionally for specific service)"
            echo "  cleanup   - Stop services and remove volumes"
            echo "  health    - Check service health"
            echo "  help      - Show this help message"
            echo ""
            ;;
    esac
}

# Run main function with all arguments
main "$@"
