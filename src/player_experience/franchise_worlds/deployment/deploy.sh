#!/bin/bash

# TTA Franchise World System - Production Deployment Script
# This script handles the complete deployment process for the TTA Franchise World System

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"
ENV_FILE="$SCRIPT_DIR/.env"

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

# Check prerequisites
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

    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        log_error ".env file not found. Please copy .env.example to .env and configure it."
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Validate environment configuration
validate_environment() {
    log_info "Validating environment configuration..."

    # Source the .env file
    source "$ENV_FILE"

    # Check required environment variables
    required_vars=(
        "NEO4J_PASSWORD"
        "JWT_SECRET_KEY"
        "GRAFANA_PASSWORD"
    )

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done

    # Validate JWT secret key length
    if [ ${#JWT_SECRET_KEY} -lt 32 ]; then
        log_error "JWT_SECRET_KEY must be at least 32 characters long"
        exit 1
    fi

    log_success "Environment configuration validated"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."

    directories=(
        "$SCRIPT_DIR/logs"
        "$SCRIPT_DIR/logs/nginx"
        "$SCRIPT_DIR/backups"
        "$SCRIPT_DIR/ssl"
        "$SCRIPT_DIR/config"
        "$SCRIPT_DIR/grafana/dashboards"
        "$SCRIPT_DIR/grafana/datasources"
    )

    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log_info "Created directory: $dir"
    done

    log_success "Directories created"
}

# Generate SSL certificates (self-signed for development)
generate_ssl_certificates() {
    log_info "Generating SSL certificates..."

    if [ ! -f "$SCRIPT_DIR/ssl/cert.pem" ] || [ ! -f "$SCRIPT_DIR/ssl/key.pem" ]; then
        openssl req -x509 -newkey rsa:4096 -keyout "$SCRIPT_DIR/ssl/key.pem" -out "$SCRIPT_DIR/ssl/cert.pem" -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        log_success "SSL certificates generated"
    else
        log_info "SSL certificates already exist"
    fi
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."

    cd "$PROJECT_ROOT"

    # Build API image
    log_info "Building TTA Franchise API image..."
    docker build -f deployment/Dockerfile.api -t tta-franchise-api:latest .

    # Build Bridge service image
    log_info "Building TTA Franchise Bridge image..."
    docker build -f deployment/Dockerfile.bridge -t tta-franchise-bridge:latest .

    log_success "Docker images built successfully"
}

# Run pre-deployment tests
run_tests() {
    log_info "Running pre-deployment tests..."

    cd "$PROJECT_ROOT"

    # Test Node.js scripts
    log_info "Testing Node.js bridge scripts..."
    node scripts/initialize-system.js > /dev/null
    if [ $? -eq 0 ]; then
        log_success "Node.js bridge scripts test passed"
    else
        log_error "Node.js bridge scripts test failed"
        exit 1
    fi

    # Test system validation
    log_info "Running system validation..."
    node test-system.js > /dev/null
    if [ $? -eq 0 ]; then
        log_success "System validation passed"
    else
        log_error "System validation failed"
        exit 1
    fi
}

# Deploy services
deploy_services() {
    log_info "Deploying TTA Franchise World System..."

    cd "$SCRIPT_DIR"

    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose down --remove-orphans

    # Start services
    log_info "Starting services..."
    docker-compose up -d

    log_success "Services deployed"
}

# Wait for services to be healthy
wait_for_services() {
    log_info "Waiting for services to be healthy..."

    services=(
        "tta-redis:6379"
        "tta-neo4j:7687"
        "tta-franchise-bridge:3001"
        "tta-franchise-api:8000"
        "tta-nginx:80"
    )

    for service in "${services[@]}"; do
        service_name=$(echo "$service" | cut -d':' -f1)
        port=$(echo "$service" | cut -d':' -f2)

        log_info "Waiting for $service_name to be ready..."

        timeout=60
        counter=0

        while [ $counter -lt $timeout ]; do
            if docker exec "$service_name" nc -z localhost "$port" 2>/dev/null; then
                log_success "$service_name is ready"
                break
            fi

            sleep 2
            counter=$((counter + 2))
        done

        if [ $counter -ge $timeout ]; then
            log_error "$service_name failed to start within $timeout seconds"
            exit 1
        fi
    done
}

# Run post-deployment health checks
run_health_checks() {
    log_info "Running post-deployment health checks..."

    # Check API health
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        exit 1
    fi

    # Check bridge service health
    if curl -f http://localhost/bridge/health > /dev/null 2>&1; then
        log_success "Bridge service health check passed"
    else
        log_error "Bridge service health check failed"
        exit 1
    fi

    # Check system initialization
    if curl -f http://localhost/bridge/system/status > /dev/null 2>&1; then
        log_success "System status check passed"
    else
        log_error "System status check failed"
        exit 1
    fi

    log_success "All health checks passed"
}

# Display deployment information
show_deployment_info() {
    log_success "TTA Franchise World System deployed successfully!"
    echo
    echo "🌐 Service URLs:"
    echo "   • API: http://localhost/api/"
    echo "   • Bridge Service: http://localhost/bridge/"
    echo "   • Grafana: http://localhost:3000/ (admin/\$GRAFANA_PASSWORD)"
    echo "   • Prometheus: http://localhost:9090/"
    echo "   • Neo4j Browser: http://localhost:7474/ (neo4j/\$NEO4J_PASSWORD)"
    echo
    echo "📊 Monitoring:"
    echo "   • Logs: docker-compose logs -f"
    echo "   • Status: docker-compose ps"
    echo "   • Stop: docker-compose down"
    echo
    echo "🔧 Management:"
    echo "   • Backup: docker-compose exec backup /app/backup.sh"
    echo "   • Update: ./deploy.sh --update"
    echo "   • Restart: docker-compose restart"
    echo
}

# Main deployment function
main() {
    log_info "Starting TTA Franchise World System deployment..."

    check_prerequisites
    validate_environment
    create_directories
    generate_ssl_certificates
    build_images
    run_tests
    deploy_services
    wait_for_services
    run_health_checks
    show_deployment_info

    log_success "Deployment completed successfully! 🎉"
}

# Handle command line arguments
case "${1:-}" in
    --update)
        log_info "Updating existing deployment..."
        build_images
        deploy_services
        wait_for_services
        run_health_checks
        log_success "Update completed successfully!"
        ;;
    --stop)
        log_info "Stopping TTA Franchise World System..."
        cd "$SCRIPT_DIR"
        docker-compose down
        log_success "System stopped"
        ;;
    --logs)
        cd "$SCRIPT_DIR"
        docker-compose logs -f
        ;;
    --status)
        cd "$SCRIPT_DIR"
        docker-compose ps
        ;;
    --help)
        echo "TTA Franchise World System Deployment Script"
        echo
        echo "Usage: $0 [OPTION]"
        echo
        echo "Options:"
        echo "  (no option)  Full deployment"
        echo "  --update     Update existing deployment"
        echo "  --stop       Stop all services"
        echo "  --logs       Show service logs"
        echo "  --status     Show service status"
        echo "  --help       Show this help message"
        ;;
    *)
        main
        ;;
esac
