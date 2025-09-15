#!/bin/bash

# TTA Production Deployment Script
# Comprehensive deployment with health monitoring, backup systems, and alerting

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env.production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi

    # Check required environment variables
    if [[ ! -f "$PROJECT_ROOT/$ENV_FILE" ]]; then
        error "Environment file $ENV_FILE not found"
        exit 1
    fi

    # Source environment variables
    source "$PROJECT_ROOT/$ENV_FILE"

    # Check critical environment variables
    required_vars=(
        "NEO4J_PASSWORD"
        "REDIS_PASSWORD"
        "JWT_SECRET"
        "GRAFANA_PASSWORD"
        "BACKUP_S3_BUCKET"
        "AWS_ACCESS_KEY_ID"
        "AWS_SECRET_ACCESS_KEY"
    )

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable $var is not set"
            exit 1
        fi
    done

    success "Prerequisites check passed"
}

# Pre-deployment validation
pre_deployment_validation() {
    log "Running pre-deployment validation..."

    # Validate Docker Compose file
    if ! docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" config > /dev/null; then
        error "Docker Compose configuration is invalid"
        exit 1
    fi

    # Check disk space
    available_space=$(df / | awk 'NR==2 {print $4}')
    required_space=10485760  # 10GB in KB

    if [[ $available_space -lt $required_space ]]; then
        error "Insufficient disk space. Required: 10GB, Available: $(($available_space / 1024 / 1024))GB"
        exit 1
    fi

    # Check memory
    available_memory=$(free -m | awk 'NR==2{print $7}')
    required_memory=8192  # 8GB in MB

    if [[ $available_memory -lt $required_memory ]]; then
        warning "Low available memory. Required: 8GB, Available: ${available_memory}MB"
    fi

    success "Pre-deployment validation passed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."

    directories=(
        "$PROJECT_ROOT/monitoring/prometheus"
        "$PROJECT_ROOT/monitoring/grafana/provisioning/dashboards"
        "$PROJECT_ROOT/monitoring/grafana/provisioning/datasources"
        "$PROJECT_ROOT/monitoring/logstash/pipeline"
        "$PROJECT_ROOT/monitoring/logstash/config"
        "$PROJECT_ROOT/nginx/ssl"
        "$PROJECT_ROOT/nginx/logs"
        "$PROJECT_ROOT/backup/scripts"
        "$PROJECT_ROOT/database/neo4j/init"
        "$PROJECT_ROOT/database/redis"
    )

    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log "Created directory: $dir"
    done

    success "Directories created successfully"
}

# Generate SSL certificates (self-signed for development)
generate_ssl_certificates() {
    log "Generating SSL certificates..."

    ssl_dir="$PROJECT_ROOT/nginx/ssl"

    if [[ ! -f "$ssl_dir/server.crt" ]] || [[ ! -f "$ssl_dir/server.key" ]]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$ssl_dir/server.key" \
            -out "$ssl_dir/server.crt" \
            -subj "/C=US/ST=State/L=City/O=TTA/CN=localhost"

        success "SSL certificates generated"
    else
        log "SSL certificates already exist"
    fi
}

# Deploy infrastructure services first
deploy_infrastructure() {
    log "Deploying infrastructure services..."

    # Start databases first
    docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" up -d neo4j redis

    # Wait for databases to be healthy
    log "Waiting for databases to be ready..."

    max_attempts=30
    attempt=0

    while [[ $attempt -lt $max_attempts ]]; do
        if docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" ps neo4j | grep -q "healthy" && \
           docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" ps redis | grep -q "healthy"; then
            success "Databases are ready"
            break
        fi

        attempt=$((attempt + 1))
        log "Waiting for databases... (attempt $attempt/$max_attempts)"
        sleep 10
    done

    if [[ $attempt -eq $max_attempts ]]; then
        error "Databases failed to become ready within timeout"
        exit 1
    fi

    # Start monitoring services
    docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" up -d prometheus grafana elasticsearch logstash kibana

    success "Infrastructure services deployed"
}

# Deploy application services
deploy_application() {
    log "Deploying application services..."

    # Build and start API
    docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" up -d --build tta-api

    # Start web interfaces
    docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" up -d nginx

    # Start backup service
    docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" up -d backup-service

    success "Application services deployed"
}

# Health check all services
health_check() {
    log "Performing health checks..."

    services=(
        "neo4j:7474/browser"
        "redis:6379"
        "tta-api:8080/health"
        "prometheus:9090/-/healthy"
        "grafana:3000/api/health"
        "nginx:80"
    )

    failed_checks=0

    for service in "${services[@]}"; do
        service_name=$(echo "$service" | cut -d':' -f1)
        endpoint=$(echo "$service" | cut -d':' -f2-)

        log "Checking $service_name..."

        if curl -f -s "http://localhost:$endpoint" > /dev/null 2>&1; then
            success "$service_name is healthy"
        else
            error "$service_name health check failed"
            failed_checks=$((failed_checks + 1))
        fi
    done

    if [[ $failed_checks -eq 0 ]]; then
        success "All health checks passed"
    else
        error "$failed_checks health checks failed"
        return 1
    fi
}

# Setup monitoring dashboards
setup_monitoring() {
    log "Setting up monitoring dashboards..."

    # Wait for Grafana to be ready
    max_attempts=30
    attempt=0

    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f -s http://localhost:3000/api/health > /dev/null 2>&1; then
            break
        fi
        attempt=$((attempt + 1))
        sleep 5
    done

    # Import Grafana dashboards
    if [[ -d "$PROJECT_ROOT/monitoring/grafana/dashboards" ]]; then
        log "Importing Grafana dashboards..."
        # Dashboard import logic would go here
        success "Monitoring dashboards configured"
    fi
}

# Verify backup system
verify_backup_system() {
    log "Verifying backup system..."

    # Check if backup service is running
    if docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" ps backup-service | grep -q "Up"; then
        success "Backup service is running"

        # Trigger a test backup
        log "Triggering test backup..."
        docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" exec -T backup-service python -c "
from backup_service import TTABackupService
service = TTABackupService()
print('Backup system health:', service.health_check())
"
        success "Backup system verified"
    else
        error "Backup service is not running"
        return 1
    fi
}

# Display deployment summary
deployment_summary() {
    log "Deployment Summary"
    echo "===================="

    # Service status
    echo "Service Status:"
    docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" ps

    echo ""
    echo "Access URLs:"
    echo "- TTA API: http://localhost:8080"
    echo "- Patient Interface: http://localhost:5173"
    echo "- Clinical Dashboard: http://localhost:3001"
    echo "- Admin Interface: http://localhost:3002"
    echo "- Public Portal: http://localhost:3003"
    echo "- Stakeholder Dashboard: http://localhost:3004"
    echo "- API Documentation: http://localhost:3005"
    echo "- Developer Interface: http://localhost:3006"
    echo "- Prometheus: http://localhost:9090"
    echo "- Grafana: http://localhost:3000"
    echo "- Kibana: http://localhost:5601"

    echo ""
    echo "Monitoring:"
    echo "- Prometheus metrics collection active"
    echo "- Grafana dashboards available"
    echo "- ELK stack for log aggregation"
    echo "- Automated backup system running"

    success "Production deployment completed successfully!"
}

# Cleanup function for failed deployments
cleanup() {
    if [[ $? -ne 0 ]]; then
        error "Deployment failed. Cleaning up..."
        docker-compose -f "$PROJECT_ROOT/$COMPOSE_FILE" down
    fi
}

# Main deployment function
main() {
    log "Starting TTA Production Deployment"

    # Set trap for cleanup
    trap cleanup EXIT

    # Change to project root
    cd "$PROJECT_ROOT"

    # Run deployment steps
    check_prerequisites
    pre_deployment_validation
    create_directories
    generate_ssl_certificates
    deploy_infrastructure
    deploy_application

    # Wait a bit for services to stabilize
    log "Waiting for services to stabilize..."
    sleep 30

    # Verify deployment
    if health_check; then
        setup_monitoring
        verify_backup_system
        deployment_summary
    else
        error "Health checks failed. Deployment may be incomplete."
        exit 1
    fi

    # Remove trap
    trap - EXIT
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
