#!/usr/bin/env bash
#
# Deploy Neo4j to Staging Environment
#
# This script deploys the Neo4j component to the staging environment
# as part of the Component Maturity Promotion Workflow.
#
# Usage: ./scripts/deploy-neo4j-staging.sh
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Log file
LOG_DIR="${PROJECT_ROOT}/logs/staging"
mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/neo4j-deployment-$(date +%Y%m%d-%H%M%S).log"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "${LOG_FILE}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Check environment variables
check_env_vars() {
    log_info "Checking environment variables..."

    if [ -z "${NEO4J_PASSWORD:-}" ]; then
        log_warning "NEO4J_PASSWORD not set, using default (not recommended for staging)"
        export NEO4J_PASSWORD="staging_password_change_me"
    fi

    log_success "Environment variables checked"
}

# Stop existing Neo4j staging container (if any)
stop_existing() {
    log_info "Stopping existing Neo4j staging container (if any)..."

    cd "${PROJECT_ROOT}"

    if docker ps -a | grep -q "tta-neo4j-staging"; then
        log_info "Found existing container, stopping..."
        docker-compose -f docker-compose.neo4j-staging.yml stop neo4j-staging || true
        docker-compose -f docker-compose.neo4j-staging.yml rm -f neo4j-staging || true
        log_success "Existing container stopped"
    else
        log_info "No existing container found"
    fi
}

# Deploy Neo4j to staging
deploy_neo4j() {
    log_info "Deploying Neo4j to staging environment..."

    cd "${PROJECT_ROOT}"

    # Start Neo4j using docker-compose
    log_info "Starting Neo4j container..."
    docker-compose -f docker-compose.neo4j-staging.yml up -d neo4j-staging

    if [ $? -eq 0 ]; then
        log_success "Neo4j container started"
    else
        log_error "Failed to start Neo4j container"
        exit 1
    fi
}

# Wait for Neo4j to be ready
wait_for_neo4j() {
    log_info "Waiting for Neo4j to be ready..."

    local max_attempts=30
    local attempt=0
    local wait_time=10

    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))
        log_info "Health check attempt $attempt/$max_attempts..."

        # Check if container is running
        if docker ps | grep -q "tta-neo4j-staging"; then
            # Check if Neo4j is responding
            if docker exec tta-neo4j-staging cypher-shell -u neo4j -p "${NEO4J_PASSWORD}" "RETURN 1" &> /dev/null; then
                log_success "Neo4j is ready!"
                return 0
            fi
        fi

        if [ $attempt -lt $max_attempts ]; then
            log_info "Neo4j not ready yet, waiting ${wait_time}s..."
            sleep $wait_time
        fi
    done

    log_error "Neo4j failed to become ready after $((max_attempts * wait_time)) seconds"
    return 1
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    # Check container status
    log_info "Checking container status..."
    if docker ps | grep -q "tta-neo4j-staging"; then
        log_success "Container is running"
    else
        log_error "Container is not running"
        return 1
    fi

    # Check ports
    log_info "Checking exposed ports..."
    if docker port tta-neo4j-staging | grep -q "7476"; then
        log_success "HTTP port 7476 is exposed"
    else
        log_warning "HTTP port 7476 is not exposed"
    fi

    if docker port tta-neo4j-staging | grep -q "7690"; then
        log_success "Bolt port 7690 is exposed"
    else
        log_error "Bolt port 7690 is not exposed"
        return 1
    fi

    # Test connection
    log_info "Testing Neo4j connection..."
    if docker exec tta-neo4j-staging cypher-shell -u neo4j -p "${NEO4J_PASSWORD}" "RETURN 1 AS test" &> /dev/null; then
        log_success "Neo4j connection test passed"
    else
        log_error "Neo4j connection test failed"
        return 1
    fi

    # Check resource usage
    log_info "Checking resource usage..."
    docker stats --no-stream tta-neo4j-staging | tee -a "${LOG_FILE}"

    log_success "Deployment verification complete"
}

# Print deployment summary
print_summary() {
    echo ""
    echo "========================================" | tee -a "${LOG_FILE}"
    echo "Neo4j Staging Deployment Summary" | tee -a "${LOG_FILE}"
    echo "========================================" | tee -a "${LOG_FILE}"
    echo "" | tee -a "${LOG_FILE}"
    echo "Container Name: tta-neo4j-staging" | tee -a "${LOG_FILE}"
    echo "HTTP Port: 7476 (external) -> 7474 (internal)" | tee -a "${LOG_FILE}"
    echo "Bolt Port: 7690 (external) -> 7687 (internal)" | tee -a "${LOG_FILE}"
    echo "Username: neo4j" | tee -a "${LOG_FILE}"
    echo "Password: ${NEO4J_PASSWORD}" | tee -a "${LOG_FILE}"
    echo "" | tee -a "${LOG_FILE}"
    echo "Access Neo4j Browser: http://localhost:7476" | tee -a "${LOG_FILE}"
    echo "Bolt URI: bolt://localhost:7690" | tee -a "${LOG_FILE}"
    echo "" | tee -a "${LOG_FILE}"
    echo "Log file: ${LOG_FILE}" | tee -a "${LOG_FILE}"
    echo "========================================" | tee -a "${LOG_FILE}"
    echo ""
}

# Main execution
main() {
    log_info "Starting Neo4j staging deployment..."
    log_info "Log file: ${LOG_FILE}"
    echo ""

    check_prerequisites
    check_env_vars
    stop_existing
    deploy_neo4j

    if wait_for_neo4j; then
        if verify_deployment; then
            print_summary
            log_success "Neo4j staging deployment completed successfully!"
            exit 0
        else
            log_error "Deployment verification failed"
            exit 1
        fi
    else
        log_error "Neo4j failed to start"
        exit 1
    fi
}

# Run main function
main "$@"
