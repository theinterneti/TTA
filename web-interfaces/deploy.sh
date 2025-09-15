#!/bin/bash

# TTA Web Interfaces Deployment Script
# Deploys all web interfaces with proper configuration and health checks

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENVIRONMENT="${1:-development}"
ACTION="${2:-deploy}"

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

# Validate environment
validate_environment() {
    if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
        log_error "Invalid environment: $ENVIRONMENT"
        log_error "Valid environments: development, staging, production"
        exit 1
    fi
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
    if [[ "$ENVIRONMENT" == "development" ]] && ! command -v node &> /dev/null; then
        log_warning "Node.js is not installed. Required for local development."
    fi

    log_success "Prerequisites check completed"
}

# Load environment configuration
load_environment() {
    local env_file="$SCRIPT_DIR/config/${ENVIRONMENT}.env"

    if [[ -f "$env_file" ]]; then
        log_info "Loading environment configuration from $env_file"
        set -a  # automatically export all variables
        source "$env_file"
        set +a
    else
        log_warning "Environment file not found: $env_file"
        log_warning "Using default configuration"
    fi
}

# Build all Docker images
build_images() {
    log_info "Building Docker images for all web interfaces..."

    cd "$SCRIPT_DIR"

    # Build shared components first
    log_info "Building shared components..."
    cd shared && npm install && npm run build && cd ..

    # Build each interface
    local interfaces=("patient-interface" "clinical-dashboard" "admin-interface" "public-portal" "stakeholder-dashboard" "api-docs-portal" "developer-interface")

    for interface in "${interfaces[@]}"; do
        log_info "Building $interface..."
        docker build \
            --build-arg ENVIRONMENT="$ENVIRONMENT" \
            -t "tta-$interface:$ENVIRONMENT" \
            -t "tta-$interface:latest" \
            "./$interface"
    done

    log_success "All Docker images built successfully"
}

# Deploy services
deploy_services() {
    log_info "Deploying TTA Web Interfaces..."

    cd "$SCRIPT_DIR"

    # Set environment variables for docker-compose
    export COMPOSE_PROJECT_NAME="tta-web-interfaces-$ENVIRONMENT"
    export ENVIRONMENT="$ENVIRONMENT"

    # Create external network if it doesn't exist
    docker network create tta-web-network 2>/dev/null || true

    # Deploy using docker-compose
    docker-compose -f docker-compose.yml up -d

    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30

    # Check service health
    if check_service_health; then
        log_success "TTA Web Interfaces deployed successfully"
        show_service_status
    else
        log_error "Deployment failed - some services are not healthy"
        show_logs
        exit 1
    fi
}

# Check service health
check_service_health() {
    log_info "Checking service health..."

    local services=("nginx-proxy" "patient-interface" "clinical-dashboard" "admin-interface" "public-portal" "stakeholder-dashboard" "api-docs-portal" "developer-interface")
    local healthy_count=0

    for service in "${services[@]}"; do
        if docker-compose ps "$service" | grep -q "healthy\|Up"; then
            log_success "$service is healthy"
            ((healthy_count++))
        else
            log_error "$service is not healthy"
        fi
    done

    if [[ $healthy_count -eq ${#services[@]} ]]; then
        return 0
    else
        return 1
    fi
}

# Show service status
show_service_status() {
    log_info "Service Status:"
    docker-compose ps

    log_info "Access URLs:"
    echo "  Patient Interface:      http://localhost/"
    echo "  Clinical Dashboard:     http://localhost/clinical"
    echo "  Admin Interface:        http://localhost/admin"
    echo "  Public Portal:          http://localhost/public"
    echo "  Stakeholder Dashboard:  http://localhost/stakeholder"
    echo "  API Documentation:      http://localhost/docs"
    echo "  Developer Interface:    http://localhost/dev"
}

# Show logs
show_logs() {
    log_info "Recent logs:"
    docker-compose logs --tail=50
}

# Stop services
stop_services() {
    log_info "Stopping TTA Web Interfaces..."
    cd "$SCRIPT_DIR"
    docker-compose down
    log_success "Services stopped"
}

# Restart services
restart_services() {
    log_info "Restarting TTA Web Interfaces..."
    stop_services
    deploy_services
}

# Development setup
setup_development() {
    log_info "Setting up development environment..."

    cd "$SCRIPT_DIR"

    # Install dependencies for all interfaces
    local interfaces=("shared" "patient-interface" "clinical-dashboard" "admin-interface" "public-portal" "stakeholder-dashboard" "api-docs-portal" "developer-interface")

    for interface in "${interfaces[@]}"; do
        if [[ -d "$interface" ]]; then
            log_info "Installing dependencies for $interface..."
            cd "$interface" && npm install && cd ..
        fi
    done

    log_success "Development environment setup completed"
}

# Main execution
main() {
    log_info "TTA Web Interfaces Deployment Script"
    log_info "Environment: $ENVIRONMENT, Action: $ACTION"

    validate_environment
    load_environment

    case "$ACTION" in
        setup)
            setup_development
            ;;
        build)
            check_prerequisites
            build_images
            ;;
        deploy)
            check_prerequisites
            build_images
            deploy_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs
            ;;
        status)
            show_service_status
            ;;
        health)
            check_service_health
            ;;
        *)
            log_error "Invalid action: $ACTION"
            log_error "Valid actions: setup, build, deploy, stop, restart, logs, status, health"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
