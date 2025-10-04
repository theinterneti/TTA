#!/bin/bash

# TTA Storytelling Platform - Staging Deployment Script
# Automated deployment with health checks, rollback capability, and monitoring

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STAGING_ENV_FILE="$PROJECT_ROOT/.env.staging"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.staging.yml"
BACKUP_DIR="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$PROJECT_ROOT/logs/deployment_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
    
    case $level in
        "ERROR")   echo -e "${RED}[ERROR]${NC} $message" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} $message" ;;
        "WARNING") echo -e "${YELLOW}[WARNING]${NC} $message" ;;
        "INFO")    echo -e "${BLUE}[INFO]${NC} $message" ;;
    esac
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    log "ERROR" "Deployment failed. Check logs at: $LOG_FILE"
    exit 1
}

# Cleanup function
cleanup() {
    log "INFO" "Performing cleanup..."
    # Add any cleanup operations here
}

# Trap for cleanup on exit
trap cleanup EXIT

# Check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error_exit "Docker is not installed"
    fi
    
    if ! docker info &> /dev/null; then
        error_exit "Docker daemon is not running"
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error_exit "Docker Compose is not installed"
    fi
    
    # Check if staging environment file exists
    if [[ ! -f "$STAGING_ENV_FILE" ]]; then
        error_exit "Staging environment file not found: $STAGING_ENV_FILE"
    fi
    
    # Check if Docker Compose file exists
    if [[ ! -f "$DOCKER_COMPOSE_FILE" ]]; then
        error_exit "Docker Compose file not found: $DOCKER_COMPOSE_FILE"
    fi
    
    # Check available disk space (minimum 10GB)
    available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 10485760 ]]; then  # 10GB in KB
        error_exit "Insufficient disk space. At least 10GB required."
    fi
    
    log "SUCCESS" "Prerequisites check passed"
}

# Load environment variables
load_environment() {
    log "INFO" "Loading staging environment variables..."
    
    if [[ -f "$STAGING_ENV_FILE" ]]; then
        set -a  # Automatically export all variables
        source "$STAGING_ENV_FILE"
        set +a
        log "SUCCESS" "Environment variables loaded"
    else
        error_exit "Staging environment file not found"
    fi
}

# Create backup of current deployment
create_backup() {
    log "INFO" "Creating backup of current deployment..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps postgres-primary | grep -q "Up"; then
        log "INFO" "Backing up PostgreSQL database..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres-primary \
            pg_dump -U tta_user tta_staging_db > "$BACKUP_DIR/postgres_backup.sql" || \
            log "WARNING" "PostgreSQL backup failed"
    fi
    
    # Backup Neo4j database
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps neo4j-cluster | grep -q "Up"; then
        log "INFO" "Backing up Neo4j database..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T neo4j-cluster \
            neo4j-admin dump --database=neo4j --to=/tmp/neo4j_backup.dump && \
        docker cp "$(docker-compose -f "$DOCKER_COMPOSE_FILE" ps -q neo4j-cluster):/tmp/neo4j_backup.dump" \
            "$BACKUP_DIR/neo4j_backup.dump" || \
            log "WARNING" "Neo4j backup failed"
    fi
    
    # Backup Redis data
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps redis-cluster | grep -q "Up"; then
        log "INFO" "Backing up Redis data..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis-cluster \
            redis-cli BGSAVE && \
        docker cp "$(docker-compose -f "$DOCKER_COMPOSE_FILE" ps -q redis-cluster):/data/dump.rdb" \
            "$BACKUP_DIR/redis_backup.rdb" || \
            log "WARNING" "Redis backup failed"
    fi
    
    # Backup configuration files
    cp -r "$PROJECT_ROOT/config" "$BACKUP_DIR/" 2>/dev/null || true
    cp "$DOCKER_COMPOSE_FILE" "$BACKUP_DIR/" 2>/dev/null || true
    cp "$STAGING_ENV_FILE" "$BACKUP_DIR/" 2>/dev/null || true
    
    log "SUCCESS" "Backup created at: $BACKUP_DIR"
}

# Build Docker images
build_images() {
    log "INFO" "Building Docker images..."
    
    # Build all services
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --parallel || \
        error_exit "Failed to build Docker images"
    
    log "SUCCESS" "Docker images built successfully"
}

# Deploy services with rolling update
deploy_services() {
    log "INFO" "Deploying services..."
    
    # Start infrastructure services first
    log "INFO" "Starting infrastructure services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d \
        postgres-primary postgres-replica redis-cluster neo4j-cluster || \
        error_exit "Failed to start infrastructure services"
    
    # Wait for databases to be ready
    wait_for_databases
    
    # Start application services
    log "INFO" "Starting application services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d \
        patient-api clinical-api langgraph-service || \
        error_exit "Failed to start application services"
    
    # Start frontend services
    log "INFO" "Starting frontend services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d \
        shared-components patient-interface clinical-dashboard || \
        error_exit "Failed to start frontend services"
    
    # Start monitoring and proxy services
    log "INFO" "Starting monitoring and proxy services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d \
        prometheus grafana nginx || \
        error_exit "Failed to start monitoring services"
    
    log "SUCCESS" "All services deployed"
}

# Wait for databases to be ready
wait_for_databases() {
    log "INFO" "Waiting for databases to be ready..."
    
    # Wait for PostgreSQL
    local postgres_ready=false
    for i in {1..60}; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres-primary \
           pg_isready -U tta_user -d tta_staging_db &>/dev/null; then
            postgres_ready=true
            break
        fi
        log "INFO" "Waiting for PostgreSQL... ($i/60)"
        sleep 5
    done
    
    if [[ "$postgres_ready" != true ]]; then
        error_exit "PostgreSQL failed to start within timeout"
    fi
    
    # Wait for Redis
    local redis_ready=false
    for i in {1..30}; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis-cluster \
           redis-cli ping | grep -q "PONG"; then
            redis_ready=true
            break
        fi
        log "INFO" "Waiting for Redis... ($i/30)"
        sleep 2
    done
    
    if [[ "$redis_ready" != true ]]; then
        error_exit "Redis failed to start within timeout"
    fi
    
    # Wait for Neo4j
    local neo4j_ready=false
    for i in {1..60}; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T neo4j-cluster \
           cypher-shell -u neo4j -p "$NEO4J_PASSWORD" "RETURN 1" &>/dev/null; then
            neo4j_ready=true
            break
        fi
        log "INFO" "Waiting for Neo4j... ($i/60)"
        sleep 5
    done
    
    if [[ "$neo4j_ready" != true ]]; then
        error_exit "Neo4j failed to start within timeout"
    fi
    
    log "SUCCESS" "All databases are ready"
}

# Run database migrations
run_migrations() {
    log "INFO" "Running database migrations..."
    
    # PostgreSQL migrations
    if [[ -d "$PROJECT_ROOT/migrations/postgresql" ]]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres-primary \
            psql -U tta_user -d tta_staging_db -f /docker-entrypoint-initdb.d/init_db.sql || \
            log "WARNING" "PostgreSQL migrations failed"
    fi
    
    # Neo4j setup
    if [[ -f "$PROJECT_ROOT/scripts/setup_neo4j.cypher" ]]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T neo4j-cluster \
            cypher-shell -u neo4j -p "$NEO4J_PASSWORD" -f /var/lib/neo4j/import/setup_neo4j.cypher || \
            log "WARNING" "Neo4j setup failed"
    fi
    
    log "SUCCESS" "Database migrations completed"
}

# Perform health checks
health_checks() {
    log "INFO" "Performing health checks..."
    
    local services=(
        "patient-api:8001:/api/patient/health"
        "clinical-api:8002:/api/clinical/health"
        "langgraph-service:8005:/health"
        "patient-interface:3002:/health"
        "clinical-dashboard:3003:/health"
    )
    
    local failed_services=()
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service port endpoint <<< "$service_info"
        
        log "INFO" "Checking health of $service..."
        
        local healthy=false
        for i in {1..30}; do
            if curl -f -s "http://localhost:$port$endpoint" &>/dev/null; then
                healthy=true
                break
            fi
            sleep 2
        done
        
        if [[ "$healthy" == true ]]; then
            log "SUCCESS" "$service is healthy"
        else
            log "ERROR" "$service health check failed"
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        error_exit "Health checks failed for services: ${failed_services[*]}"
    fi
    
    log "SUCCESS" "All health checks passed"
}

# Run smoke tests
run_smoke_tests() {
    log "INFO" "Running smoke tests..."
    
    # Test patient API
    local patient_response
    patient_response=$(curl -s -X POST "http://localhost:8001/api/patient/sessions" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer test_token" \
        -d '{"patient_id":"smoke_test_patient","therapeutic_framework":"CBT"}' || echo "FAILED")
    
    if [[ "$patient_response" == "FAILED" ]] || ! echo "$patient_response" | grep -q "id"; then
        error_exit "Patient API smoke test failed"
    fi
    
    # Test clinical API
    local clinical_response
    clinical_response=$(curl -s "http://localhost:8002/api/clinical/dashboard/smoke_test_clinician" \
        -H "Authorization: Bearer test_token" || echo "FAILED")
    
    if [[ "$clinical_response" == "FAILED" ]]; then
        error_exit "Clinical API smoke test failed"
    fi
    
    # Test frontend interfaces
    if ! curl -f -s "http://localhost:3002/" &>/dev/null; then
        error_exit "Patient interface smoke test failed"
    fi
    
    if ! curl -f -s "http://localhost:3003/" &>/dev/null; then
        error_exit "Clinical dashboard smoke test failed"
    fi
    
    log "SUCCESS" "Smoke tests passed"
}

# Setup monitoring alerts
setup_monitoring() {
    log "INFO" "Setting up monitoring and alerts..."
    
    # Wait for Prometheus to be ready
    local prometheus_ready=false
    for i in {1..30}; do
        if curl -f -s "http://localhost:9090/-/ready" &>/dev/null; then
            prometheus_ready=true
            break
        fi
        sleep 2
    done
    
    if [[ "$prometheus_ready" != true ]]; then
        log "WARNING" "Prometheus is not ready"
    else
        log "SUCCESS" "Prometheus is ready"
    fi
    
    # Wait for Grafana to be ready
    local grafana_ready=false
    for i in {1..30}; do
        if curl -f -s "http://localhost:3000/api/health" &>/dev/null; then
            grafana_ready=true
            break
        fi
        sleep 2
    done
    
    if [[ "$grafana_ready" != true ]]; then
        log "WARNING" "Grafana is not ready"
    else
        log "SUCCESS" "Grafana is ready"
    fi
    
    log "SUCCESS" "Monitoring setup completed"
}

# Generate deployment report
generate_report() {
    log "INFO" "Generating deployment report..."
    
    local report_file="$PROJECT_ROOT/deployment_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# TTA Staging Deployment Report

**Deployment Date**: $(date)
**Deployment Status**: SUCCESS
**Backup Location**: $BACKUP_DIR

## Services Status

$(docker-compose -f "$DOCKER_COMPOSE_FILE" ps)

## Health Check Results

- Patient API: ✅ Healthy
- Clinical API: ✅ Healthy
- LangGraph Service: ✅ Healthy
- Patient Interface: ✅ Healthy
- Clinical Dashboard: ✅ Healthy

## Database Status

- PostgreSQL: ✅ Running
- Redis: ✅ Running
- Neo4j: ✅ Running

## Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Access URLs

- Patient Interface: http://localhost:3002
- Clinical Dashboard: http://localhost:3003
- API Documentation: http://localhost:8001/docs

## Next Steps

1. Run comprehensive load tests
2. Perform security audit
3. Coordinate user acceptance testing
4. Plan production deployment

EOF
    
    log "SUCCESS" "Deployment report generated: $report_file"
}

# Rollback function
rollback() {
    log "WARNING" "Initiating rollback..."
    
    # Stop current services
    docker-compose -f "$DOCKER_COMPOSE_FILE" down || true
    
    # Restore from backup if available
    if [[ -d "$BACKUP_DIR" ]]; then
        log "INFO" "Restoring from backup..."
        
        # Restore databases
        if [[ -f "$BACKUP_DIR/postgres_backup.sql" ]]; then
            docker-compose -f "$DOCKER_COMPOSE_FILE" up -d postgres-primary
            sleep 10
            docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres-primary \
                psql -U tta_user -d tta_staging_db < "$BACKUP_DIR/postgres_backup.sql" || true
        fi
        
        log "SUCCESS" "Rollback completed"
    else
        log "ERROR" "No backup available for rollback"
    fi
}

# Main deployment function
main() {
    log "INFO" "Starting TTA Staging Deployment"
    log "INFO" "Timestamp: $(date)"
    log "INFO" "Project Root: $PROJECT_ROOT"
    
    # Create logs directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Run deployment steps
    check_prerequisites
    load_environment
    create_backup
    build_images
    deploy_services
    run_migrations
    health_checks
    run_smoke_tests
    setup_monitoring
    generate_report
    
    log "SUCCESS" "TTA Staging Deployment completed successfully!"
    log "INFO" "Access the platform at:"
    log "INFO" "  - Patient Interface: http://localhost:3002"
    log "INFO" "  - Clinical Dashboard: http://localhost:3003"
    log "INFO" "  - Monitoring: http://localhost:3000"
    log "INFO" "  - API Docs: http://localhost:8001/docs"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health-check")
        health_checks
        ;;
    "backup")
        create_backup
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health-check|backup}"
        exit 1
        ;;
esac
