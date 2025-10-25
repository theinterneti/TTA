#!/usr/bin/env bash
# =============================================================================
# TTA Environment Switcher
# =============================================================================
# This script helps switch between development and staging environments
# Usage: ./scripts/switch-environment.sh [dev|staging]
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [dev|staging] [options]

Switch between TTA development and staging environments.

Arguments:
    dev         Switch to development environment
    staging     Switch to staging environment

Options:
    -h, --help          Show this help message
    -s, --status        Show current environment status
    -b, --both          Show status of both environments
    -c, --check         Check environment configuration

Examples:
    $0 dev              Switch to development environment
    $0 staging          Switch to staging environment
    $0 --status         Show current environment status
    $0 --both           Show both environments status

EOF
}

# Function to check if environment file exists
check_env_file() {
    local env_file="$1"
    if [[ ! -f "$PROJECT_ROOT/$env_file" ]]; then
        print_warning "Environment file $env_file not found"
        print_info "Creating from template..."

        local template_file="${env_file}.example"
        if [[ -f "$PROJECT_ROOT/$template_file" ]]; then
            cp "$PROJECT_ROOT/$template_file" "$PROJECT_ROOT/$env_file"
            print_success "Created $env_file from template"
            print_warning "Please edit $env_file and set your actual values"
            return 1
        else
            print_error "Template file $template_file not found"
            return 1
        fi
    fi
    return 0
}

# Function to get environment status
get_env_status() {
    local compose_file="$1"
    local env_name="$2"

    print_info "Checking $env_name environment..."

    if docker-compose -f "$compose_file" ps --services --filter "status=running" 2>/dev/null | grep -q .; then
        local running_services=$(docker-compose -f "$compose_file" ps --services --filter "status=running" 2>/dev/null | wc -l)
        print_success "$env_name: $running_services services running"
        docker-compose -f "$compose_file" ps
    else
        print_info "$env_name: No services running"
    fi
    echo ""
}

# Function to show both environments status
show_both_status() {
    echo ""
    print_info "=== TTA Environment Status ==="
    echo ""

    get_env_status "$PROJECT_ROOT/docker-compose.dev.yml" "Development"
    get_env_status "$PROJECT_ROOT/docker-compose.staging-homelab.yml" "Staging"

    print_info "=== Port Allocation ==="
    echo ""
    cat << EOF
Service          | Development | Staging  | Purpose
-----------------|-------------|----------|---------------------------
Neo4j HTTP       | 7474        | 7475     | Browser interface
Neo4j Bolt       | 7687        | 7688     | Database connection
Redis            | 6379        | 6380     | Cache/session store
PostgreSQL       | 5432        | 5433     | Relational database
API Server       | 8080        | 8081     | Backend API
Frontend         | 3000        | 3001     | Web interface
Grafana          | 3000        | 3002     | Monitoring dashboard
Prometheus       | 9090        | 9091     | Metrics collection
Redis Commander  | 8081        | 8082     | Redis management UI
Health Check     | N/A         | 8090     | Service health monitoring
EOF
    echo ""
}

# Function to check environment configuration
check_environment() {
    local env_type="$1"
    local env_file=".env.$env_type"
    local compose_file

    if [[ "$env_type" == "dev" ]]; then
        compose_file="docker-compose.dev.yml"
    else
        compose_file="docker-compose.staging-homelab.yml"
    fi

    print_info "Checking $env_type environment configuration..."
    echo ""

    # Check environment file
    if [[ -f "$PROJECT_ROOT/$env_file" ]]; then
        print_success "Environment file: $env_file exists"
    else
        print_error "Environment file: $env_file missing"
    fi

    # Check compose file
    if [[ -f "$PROJECT_ROOT/$compose_file" ]]; then
        print_success "Compose file: $compose_file exists"
    else
        print_error "Compose file: $compose_file missing"
    fi

    # Check workspace file
    local workspace_file
    if [[ "$env_type" == "dev" ]]; then
        workspace_file="TTA-Development.code-workspace"
    else
        workspace_file="TTA-Staging.code-workspace"
    fi

    if [[ -f "$PROJECT_ROOT/$workspace_file" ]]; then
        print_success "Workspace file: $workspace_file exists"
    else
        print_warning "Workspace file: $workspace_file missing"
    fi

    echo ""
}

# Function to switch environment
switch_environment() {
    local env_type="$1"
    local env_file=".env.$env_type"
    local compose_file
    local workspace_file

    if [[ "$env_type" == "dev" ]]; then
        compose_file="docker-compose.dev.yml"
        workspace_file="TTA-Development.code-workspace"
    elif [[ "$env_type" == "staging" ]]; then
        compose_file="docker-compose.staging-homelab.yml"
        workspace_file="TTA-Staging.code-workspace"
    else
        print_error "Invalid environment: $env_type"
        show_usage
        exit 1
    fi

    cd "$PROJECT_ROOT"

    print_info "Switching to $env_type environment..."
    echo ""

    # Check environment file
    if ! check_env_file "$env_file"; then
        print_error "Please configure $env_file before starting services"
        exit 1
    fi

    # Show current status
    get_env_status "$compose_file" "$env_type"

    # Provide instructions
    print_info "To start $env_type environment:"
    echo "  docker-compose -f $compose_file --env-file $env_file up -d"
    echo ""

    print_info "To stop $env_type environment:"
    echo "  docker-compose -f $compose_file down"
    echo ""

    print_info "To open VS Code workspace:"
    echo "  code $workspace_file"
    echo ""

    print_info "Quick access URLs:"
    if [[ "$env_type" == "dev" ]]; then
        echo "  Neo4j Browser:    http://localhost:7474"
        echo "  API Server:       http://localhost:8080"
        echo "  Frontend:         http://localhost:3000"
        echo "  Grafana:          http://localhost:3000"
        echo "  Prometheus:       http://localhost:9090"
        echo "  Redis Commander:  http://localhost:8081"
    else
        echo "  Neo4j Browser:    http://localhost:7475"
        echo "  API Server:       http://localhost:8081"
        echo "  Frontend:         http://localhost:3001"
        echo "  Grafana:          http://localhost:3002"
        echo "  Prometheus:       http://localhost:9091"
        echo "  Redis Commander:  http://localhost:8082"
        echo "  Health Check:     http://localhost:8090"
    fi
    echo ""
}

# Main script logic
main() {
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 0
    fi

    case "$1" in
        dev|development)
            switch_environment "dev"
            ;;
        staging)
            switch_environment "staging"
            ;;
        -s|--status)
            if [[ $# -gt 1 ]]; then
                get_env_status "$PROJECT_ROOT/docker-compose.$2.yml" "$2"
            else
                show_both_status
            fi
            ;;
        -b|--both)
            show_both_status
            ;;
        -c|--check)
            if [[ $# -gt 1 ]]; then
                check_environment "$2"
            else
                print_error "Please specify environment: dev or staging"
                exit 1
            fi
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
