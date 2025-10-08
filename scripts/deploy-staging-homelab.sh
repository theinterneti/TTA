#!/bin/bash

# TTA Staging Homelab Deployment Script
# Comprehensive deployment automation for homelab staging environment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.staging-homelab.yml"
ENV_FILE="$PROJECT_ROOT/.env.staging-homelab"
COMPOSE_PROJECT="tta-staging-homelab"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/deployment_$(date +"%Y%m%d_%H%M%S").log"
mkdir -p "$LOG_DIR"

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE" >&2
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
    deploy      Deploy the staging environment
    update      Update existing deployment
    stop        Stop the staging environment
    restart     Restart the staging environment
    status      Show deployment status
    logs        Show service logs
    backup      Create backup before deployment
    restore     Restore from backup
    validate    Validate deployment
    cleanup     Clean up old resources

Options:
    --env-file FILE     Use specific environment file
    --no-backup         Skip backup before deployment
    --force             Force deployment without confirmation
    --verbose           Enable verbose output
    --help              Show this help message

Examples:
    $0 deploy                    # Deploy with default settings
    $0 deploy --no-backup        # Deploy without backup
    $0 update --force            # Force update without confirmation
    $0 status                    # Show current status
    $0 logs player-api-staging   # Show logs for specific service

Environment Variables:
    BACKUP_ENABLED      Enable/disable backups (default: true)
    DEPLOYMENT_TIMEOUT  Deployment timeout in seconds (default: 600)
    HEALTH_CHECK_TIMEOUT Health check timeout in seconds (default: 300)
EOF
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    local missing_tools=()

    # Check required tools
    for tool in docker docker-compose jq curl; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        error "Missing required tools: ${missing_tools[*]}"
        error "Please install the missing tools and try again"
        exit 1
    fi

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi

    # Check compose file
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi

    # Check environment file
    if [[ ! -f "$ENV_FILE" ]]; then
        warn "Environment file not found: $ENV_FILE"
        warn "Please copy .env.staging-homelab.example to .env.staging-homelab and configure it"

        if [[ -f "$PROJECT_ROOT/.env.staging-homelab.example" ]]; then
            info "Example environment file available at: $PROJECT_ROOT/.env.staging-homelab.example"
        fi

        read -p "Continue without environment file? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    log "Prerequisites check passed"
}

# Validate environment configuration
validate_environment() {
    log "Validating environment configuration..."

    if [[ -f "$ENV_FILE" ]]; then
        # Check for required variables
        local required_vars=(
            "NEO4J_STAGING_PASSWORD"
            "REDIS_STAGING_PASSWORD"
            "POSTGRES_STAGING_PASSWORD"
            "JWT_STAGING_SECRET_KEY"
        )

        local missing_vars=()
        for var in "${required_vars[@]}"; do
            if ! grep -q "^${var}=" "$ENV_FILE" || grep -q "^${var}=CHANGE_ME" "$ENV_FILE"; then
                missing_vars+=("$var")
            fi
        done

        if [[ ${#missing_vars[@]} -gt 0 ]]; then
            error "Missing or unconfigured environment variables:"
            for var in "${missing_vars[@]}"; do
                error "  - $var"
            done
            error "Please configure these variables in $ENV_FILE"
            exit 1
        fi
    fi

    log "Environment validation passed"
}

# Create backup before deployment
create_backup() {
    if [[ "${BACKUP_ENABLED:-true}" == "true" ]]; then
        log "Creating backup before deployment..."

        if [[ -f "$SCRIPT_DIR/staging-backup.sh" ]]; then
            bash "$SCRIPT_DIR/staging-backup.sh"
        else
            warn "Backup script not found, skipping backup"
        fi
    else
        info "Backup disabled, skipping"
    fi
}

# Pull latest images
pull_images() {
    log "Pulling latest Docker images..."

    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" pull --quiet

    log "Images pulled successfully"
}

# Build custom images
build_images() {
    log "Building custom Docker images..."

    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" build --no-cache

    log "Images built successfully"
}

# Deploy services
deploy_services() {
    log "Deploying staging services..."

    # Start infrastructure services first
    log "Starting infrastructure services..."
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" up -d \
        neo4j-staging redis-staging postgres-staging

    # Wait for databases to be ready
    log "Waiting for databases to be ready..."
    sleep 30

    # Start application services
    log "Starting application services..."
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" up -d \
        player-api-staging player-frontend-staging

    # Start monitoring services
    log "Starting monitoring services..."
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" up -d \
        prometheus-staging grafana-staging

    # Start load balancer
    log "Starting load balancer..."
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" up -d \
        nginx-staging

    log "All services started"
}

# Wait for services to be healthy
wait_for_health() {
    log "Waiting for services to become healthy..."

    local timeout="${HEALTH_CHECK_TIMEOUT:-300}"
    local start_time=$(date +%s)
    local services=(
        "neo4j-staging"
        "redis-staging"
        "postgres-staging"
        "player-api-staging"
        "player-frontend-staging"
    )

    while true; do
        local healthy_count=0
        local current_time=$(date +%s)

        if [[ $((current_time - start_time)) -gt $timeout ]]; then
            error "Health check timeout after ${timeout} seconds"
            show_service_status
            exit 1
        fi

        for service in "${services[@]}"; do
            local health_status=$(docker inspect --format='{{.State.Health.Status}}' "${COMPOSE_PROJECT}_${service}_1" 2>/dev/null || echo "no-health-check")

            if [[ "$health_status" == "healthy" ]] || [[ "$health_status" == "no-health-check" ]]; then
                ((healthy_count++))
            fi
        done

        if [[ $healthy_count -eq ${#services[@]} ]]; then
            log "All services are healthy"
            break
        fi

        info "Waiting for services to become healthy ($healthy_count/${#services[@]})"
        sleep 10
    done
}

# Validate deployment
validate_deployment() {
    log "Validating deployment..."

    local validation_errors=0

    # Check service endpoints
    local endpoints=(
        "http://localhost:8081/health"
        "http://localhost:3001/health"
        "http://localhost:9091/-/healthy"
    )

    for endpoint in "${endpoints[@]}"; do
        if curl -f -s "$endpoint" > /dev/null; then
            log "✅ $endpoint is accessible"
        else
            error "❌ $endpoint is not accessible"
            ((validation_errors++))
        fi
    done

    # Check database connections
    if docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T neo4j-staging \
        cypher-shell -u neo4j -p "${NEO4J_STAGING_PASSWORD:-staging_neo4j_secure_pass}" \
        "RETURN 1" > /dev/null 2>&1; then
        log "✅ Neo4j connection successful"
    else
        error "❌ Neo4j connection failed"
        ((validation_errors++))
    fi

    if docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T redis-staging \
        redis-cli ping > /dev/null 2>&1; then
        log "✅ Redis connection successful"
    else
        error "❌ Redis connection failed"
        ((validation_errors++))
    fi

    if docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T postgres-staging \
        pg_isready -U tta_staging_user > /dev/null 2>&1; then
        log "✅ PostgreSQL connection successful"
    else
        error "❌ PostgreSQL connection failed"
        ((validation_errors++))
    fi

    if [[ $validation_errors -eq 0 ]]; then
        log "✅ Deployment validation passed"
        return 0
    else
        error "❌ Deployment validation failed with $validation_errors errors"
        return 1
    fi
}

# Show service status
show_service_status() {
    log "Service Status:"
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" ps

    log "Service Health:"
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
}

# Show service logs
show_logs() {
    local service="${1:-}"

    if [[ -n "$service" ]]; then
        log "Showing logs for service: $service"
        docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" logs -f "$service"
    else
        log "Showing logs for all services:"
        docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" logs -f
    fi
}

# Stop services
stop_services() {
    log "Stopping staging services..."

    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" down

    log "Services stopped"
}

# Update deployment
update_deployment() {
    log "Updating staging deployment..."

    # Pull latest images
    pull_images

    # Recreate services
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" up -d --force-recreate

    # Wait for health
    wait_for_health

    # Validate
    validate_deployment

    log "Deployment updated successfully"
}

# Main deployment function
deploy() {
    local no_backup=false
    local force=false

    # Parse deployment options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-backup)
                no_backup=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    log "Starting TTA Staging Homelab deployment..."
    log "Compose file: $COMPOSE_FILE"
    log "Environment file: $ENV_FILE"
    log "Project: $COMPOSE_PROJECT"

    # Confirmation
    if [[ "$force" != true ]]; then
        echo "This will deploy the TTA staging environment to your homelab."
        echo "Compose file: $COMPOSE_FILE"
        echo "Environment file: $ENV_FILE"
        read -p "Continue with deployment? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Deployment cancelled by user"
            exit 0
        fi
    fi

    # Prerequisites and validation
    check_prerequisites
    validate_environment

    # Backup
    if [[ "$no_backup" != true ]]; then
        create_backup
    fi

    # Deployment steps
    pull_images
    build_images
    deploy_services
    wait_for_health

    # Validation
    if validate_deployment; then
        log "🎉 TTA Staging Environment deployed successfully!"
        log ""
        log "Access URLs:"
        log "  Frontend: http://localhost:3001"
        log "  API: http://localhost:8081"
        log "  Grafana: http://localhost:3001 (admin/staging_grafana_admin_pass)"
        log "  Prometheus: http://localhost:9091"
        log ""
        log "Database Access:"
        log "  Neo4j Browser: http://localhost:7475 (neo4j/staging_neo4j_secure_pass)"
        log "  Redis: localhost:6380"
        log "  PostgreSQL: localhost:5433"
        log ""
        log "Logs: $LOG_FILE"
    else
        error "Deployment validation failed"
        show_service_status
        exit 1
    fi
}

# Main function
main() {
    local command="${1:-deploy}"
    shift || true

    case "$command" in
        deploy)
            deploy "$@"
            ;;
        update)
            update_deployment "$@"
            ;;
        stop)
            stop_services "$@"
            ;;
        restart)
            stop_services "$@"
            deploy --force "$@"
            ;;
        status)
            show_service_status "$@"
            ;;
        logs)
            show_logs "$@"
            ;;
        backup)
            create_backup "$@"
            ;;
        restore)
            if [[ -f "$SCRIPT_DIR/staging-restore.sh" ]]; then
                bash "$SCRIPT_DIR/staging-restore.sh" "$@"
            else
                error "Restore script not found"
                exit 1
            fi
            ;;
        validate)
            check_prerequisites
            validate_environment
            validate_deployment
            ;;
        cleanup)
            log "Cleaning up old resources..."
            docker system prune -f
            docker volume prune -f
            log "Cleanup completed"
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Set environment variables from file if it exists
if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# Run main function
main "$@"
