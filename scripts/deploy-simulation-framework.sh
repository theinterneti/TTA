#!/bin/bash

# =============================================================================
# TTA Simulation Framework Deployment Script
# =============================================================================
# Automated deployment and management script for the TTA Simulation Framework
# in homelab and production environments.
# =============================================================================

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SIMULATION_DIR="$PROJECT_ROOT/testing/simulation"

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

# Help function
show_help() {
    cat << EOF
TTA Simulation Framework Deployment Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    deploy      Deploy the simulation framework
    start       Start the simulation framework services
    stop        Stop the simulation framework services
    restart     Restart the simulation framework services
    status      Check the status of simulation framework services
    logs        Show logs from simulation framework services
    test        Run framework validation tests
    update      Update the simulation framework
    cleanup     Clean up old simulation data and logs

Options:
    -e, --environment ENV    Target environment (homelab, staging, production)
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

Examples:
    $0 deploy --environment homelab
    $0 start
    $0 test --verbose
    $0 logs --follow

EOF
}

# Environment validation
validate_environment() {
    local env="$1"

    case "$env" in
        homelab|staging|production)
            log_info "Deploying to $env environment"
            ;;
        *)
            log_error "Invalid environment: $env"
            log_error "Valid environments: homelab, staging, production"
            exit 1
            ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi

    # Check Node.js (for local development)
    if ! command -v node &> /dev/null; then
        log_warning "Node.js is not installed - required for local development"
    fi

    # Check if simulation directory exists
    if [ ! -d "$SIMULATION_DIR" ]; then
        log_error "Simulation directory not found: $SIMULATION_DIR"
        exit 1
    fi

    log_success "Prerequisites check completed"
}

# Build simulation framework
build_framework() {
    log_info "Building simulation framework..."

    cd "$SIMULATION_DIR"

    # Install dependencies
    if [ -f "package.json" ]; then
        log_info "Installing Node.js dependencies..."
        npm ci
    fi

    # Build TypeScript
    log_info "Building TypeScript..."
    npm run build

    # Build Docker image
    log_info "Building Docker image..."
    docker build -t tta-simulation-framework .

    log_success "Framework build completed"
}

# Deploy simulation framework
deploy_framework() {
    local environment="$1"

    log_info "Deploying TTA Simulation Framework to $environment..."

    # Validate environment
    validate_environment "$environment"

    # Check prerequisites
    check_prerequisites

    # Build framework
    build_framework

    # Deploy using Docker Compose
    cd "$PROJECT_ROOT"

    case "$environment" in
        homelab)
            log_info "Starting homelab deployment..."
            docker-compose -f docker-compose.homelab.yml up -d simulation-framework
            ;;
        staging)
            log_info "Starting staging deployment..."
            docker-compose -f docker-compose.staging.yml up -d simulation-framework
            ;;
        production)
            log_info "Starting production deployment..."
            docker-compose -f docker-compose.yml up -d simulation-framework
            ;;
    esac

    # Wait for service to be healthy
    log_info "Waiting for simulation framework to be healthy..."
    sleep 30

    # Check health
    if curl -f http://localhost:3002/health &> /dev/null; then
        log_success "Simulation framework deployed successfully!"
        log_info "Framework API available at: http://localhost:3002"
        log_info "Health check: http://localhost:3002/health"
        log_info "Configurations: http://localhost:3002/configurations"
    else
        log_error "Simulation framework deployment failed - health check failed"
        exit 1
    fi
}

# Start services
start_services() {
    log_info "Starting simulation framework services..."

    cd "$PROJECT_ROOT"
    docker-compose -f docker-compose.homelab.yml start simulation-framework

    log_success "Services started"
}

# Stop services
stop_services() {
    log_info "Stopping simulation framework services..."

    cd "$PROJECT_ROOT"
    docker-compose -f docker-compose.homelab.yml stop simulation-framework

    log_success "Services stopped"
}

# Restart services
restart_services() {
    log_info "Restarting simulation framework services..."

    stop_services
    sleep 5
    start_services

    log_success "Services restarted"
}

# Check status
check_status() {
    log_info "Checking simulation framework status..."

    cd "$PROJECT_ROOT"
    docker-compose -f docker-compose.homelab.yml ps simulation-framework

    # Check health endpoint
    if curl -f http://localhost:3002/health &> /dev/null; then
        log_success "Simulation framework is healthy"
    else
        log_warning "Simulation framework health check failed"
    fi
}

# Show logs
show_logs() {
    local follow_flag=""

    if [[ "${1:-}" == "--follow" ]]; then
        follow_flag="-f"
    fi

    log_info "Showing simulation framework logs..."

    cd "$PROJECT_ROOT"
    docker-compose -f docker-compose.homelab.yml logs $follow_flag simulation-framework
}

# Run tests
run_tests() {
    local verbose=""

    if [[ "${1:-}" == "--verbose" ]]; then
        verbose="--verbose"
    fi

    log_info "Running simulation framework validation tests..."

    cd "$SIMULATION_DIR"
    npm run validate $verbose

    log_success "Framework validation completed"
}

# Update framework
update_framework() {
    log_info "Updating simulation framework..."

    # Pull latest changes
    cd "$PROJECT_ROOT"
    git pull origin main

    # Rebuild and redeploy
    deploy_framework "homelab"

    log_success "Framework updated successfully"
}

# Cleanup old data
cleanup_data() {
    log_info "Cleaning up old simulation data and logs..."

    cd "$SIMULATION_DIR"

    # Remove old simulation results (older than 30 days)
    find . -name "simulation-results-*.json" -mtime +30 -delete 2>/dev/null || true

    # Remove old log files (older than 7 days)
    find . -name "*.log" -mtime +7 -delete 2>/dev/null || true

    # Clean npm cache
    npm cache clean --force

    # Clean Docker images
    docker image prune -f

    log_success "Cleanup completed"
}

# Main script logic
main() {
    local command="${1:-}"
    local environment="homelab"
    local verbose=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                environment="$2"
                shift 2
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            deploy|start|stop|restart|status|logs|test|update|cleanup)
                command="$1"
                shift
                ;;
            --follow)
                # Special case for logs command
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Execute command
    case "$command" in
        deploy)
            deploy_framework "$environment"
            ;;
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
            check_status
            ;;
        logs)
            show_logs "${2:-}"
            ;;
        test)
            run_tests "$($verbose && echo '--verbose' || echo '')"
            ;;
        update)
            update_framework
            ;;
        cleanup)
            cleanup_data
            ;;
        "")
            log_error "No command specified"
            show_help
            exit 1
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
