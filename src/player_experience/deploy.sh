#!/bin/bash

# Player Experience Interface Deployment Script
# Usage: ./deploy.sh [environment] [action]
# Environment: development, staging, production
# Action: build, deploy, stop, restart, logs, status

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
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
    case "$ENVIRONMENT" in
        development|staging|production)
            log_info "Using environment: $ENVIRONMENT"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            log_error "Valid environments: development, staging, production"
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
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
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

# Build Docker images
build_images() {
    log_info "Building Docker images for $ENVIRONMENT environment..."
    
    cd "$SCRIPT_DIR"
    
    # Build the main API image
    docker build \
        --build-arg ENVIRONMENT="$ENVIRONMENT" \
        -t "tta-player-experience-api:$ENVIRONMENT" \
        -t "tta-player-experience-api:latest" \
        -f Dockerfile \
        "$PROJECT_ROOT"
    
    log_success "Docker images built successfully"
}

# Deploy services
deploy_services() {
    log_info "Deploying Player Experience Interface services..."
    
    cd "$SCRIPT_DIR"
    
    # Set environment variables for docker-compose
    export COMPOSE_PROJECT_NAME="tta-player-experience-$ENVIRONMENT"
    export ENVIRONMENT="$ENVIRONMENT"
    
    # Deploy using docker-compose
    docker-compose -f docker-compose.yml up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check service health
    if check_service_health; then
        log_success "Player Experience Interface deployed successfully"
        show_service_status
    else
        log_error "Deployment failed - services are not healthy"
        show_logs
        exit 1
    fi
}

# Stop services
stop_services() {
    log_info "Stopping Player Experience Interface services..."
    
    cd "$SCRIPT_DIR"
    
    export COMPOSE_PROJECT_NAME="tta-player-experience-$ENVIRONMENT"
    docker-compose -f docker-compose.yml down
    
    log_success "Services stopped successfully"
}

# Restart services
restart_services() {
    log_info "Restarting Player Experience Interface services..."
    stop_services
    deploy_services
}

# Check service health
check_service_health() {
    local api_port="${API_PORT:-8080}"
    local max_attempts=30
    local attempt=1
    
    log_info "Checking service health on port $api_port..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "http://localhost:$api_port/health" > /dev/null 2>&1; then
            log_success "API service is healthy"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts - waiting for API service..."
        sleep 2
        ((attempt++))
    done
    
    log_error "API service health check failed after $max_attempts attempts"
    return 1
}

# Show service status
show_service_status() {
    log_info "Service Status:"
    
    cd "$SCRIPT_DIR"
    export COMPOSE_PROJECT_NAME="tta-player-experience-$ENVIRONMENT"
    docker-compose -f docker-compose.yml ps
    
    # Show health status if API is running
    local api_port="${API_PORT:-8080}"
    if curl -f -s "http://localhost:$api_port/health" > /dev/null 2>&1; then
        echo ""
        log_info "API Health Status:"
        curl -s "http://localhost:$api_port/health" | python3 -m json.tool 2>/dev/null || echo "Health endpoint not available"
    fi
}

# Show logs
show_logs() {
    log_info "Service Logs:"
    
    cd "$SCRIPT_DIR"
    export COMPOSE_PROJECT_NAME="tta-player-experience-$ENVIRONMENT"
    docker-compose -f docker-compose.yml logs --tail=50
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Apply Kubernetes manifests
    kubectl apply -f "$SCRIPT_DIR/k8s/"
    
    # Wait for deployment to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/player-experience-api-deployment -n tta-player-experience
    
    log_success "Kubernetes deployment completed"
    
    # Show status
    kubectl get pods -n tta-player-experience
}

# Main execution
main() {
    log_info "Player Experience Interface Deployment Script"
    log_info "Environment: $ENVIRONMENT, Action: $ACTION"
    
    validate_environment
    load_environment
    
    case "$ACTION" in
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
        k8s)
            deploy_kubernetes
            ;;
        *)
            log_error "Invalid action: $ACTION"
            log_error "Valid actions: build, deploy, stop, restart, logs, status, k8s"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"