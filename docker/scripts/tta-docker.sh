#!/usr/bin/env bash
# TTA Docker Management Script
# Unified interface for managing Docker environments
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DOCKER_DIR="${REPO_ROOT}/docker"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_header() { echo -e "${CYAN}━━━ $* ━━━${NC}"; }

# Usage information
usage() {
    cat << EOF
${CYAN}TTA Docker Management${NC}

Usage: $(basename "$0") <environment> <command> [options]

${YELLOW}Environments:${NC}
  dev         Development environment (hot reload, debug ports)
  test        Test environment (CI/CD, constrained resources)
  staging     Staging environment (production-like)
  prod        Production environment (requires external secrets)

${YELLOW}Commands:${NC}
  up          Start services
  down        Stop services
  restart     Restart services
  logs        View logs
  status      Show service status
  config      Validate and display configuration
  clean       Remove volumes and images
  backup      Backup databases
  restore     Restore from backup

${YELLOW}Examples:${NC}
  $(basename "$0") dev up                # Start development environment
  $(basename "$0") dev logs neo4j        # View Neo4j logs
  $(basename "$0") test down             # Stop test environment
  $(basename "$0") staging backup        # Backup staging databases
  $(basename "$0") prod config           # Validate production config

${YELLOW}Options:${NC}
  -d, --detach       Run in background (for 'up' command)
  -f, --force        Force operation without confirmation
  -v, --verbose      Verbose output
  -h, --help         Show this help message

${YELLOW}Documentation:${NC}
  ${REPO_ROOT}/docker/README.md
  ${REPO_ROOT}/.github/instructions/docker-improvements.md

EOF
    exit 0
}

# Validate environment
validate_env() {
    local env="$1"
    case "$env" in
        dev|test|staging|prod)
            return 0
            ;;
        *)
            log_error "Invalid environment: $env"
            echo "Valid environments: dev, test, staging, prod"
            exit 1
            ;;
    esac
}

# Get compose files for environment
get_compose_files() {
    local env="$1"
    echo "-f ${DOCKER_DIR}/compose/docker-compose.base.yml -f ${DOCKER_DIR}/compose/docker-compose.${env}.yml"
}

# Command: up
cmd_up() {
    local env="$1"
    local detach="${2:-}"

    log_header "Starting ${env} environment"

    # Check secrets exist (except for test)
    if [ "$env" != "test" ] && [ "$env" != "dev" ]; then
        if [ ! -d "${REPO_ROOT}/secrets/${env}" ]; then
            log_error "Secrets directory not found: secrets/${env}"
            log_info "Run: bash scripts/docker/setup-secrets.sh"
            exit 1
        fi
    fi

    local compose_cmd="docker-compose $(get_compose_files "$env")"

    if [ "$detach" = "-d" ]; then
        eval "$compose_cmd up -d"
    else
        eval "$compose_cmd up"
    fi

    log_success "${env} environment started"
    log_info "View logs: $0 $env logs"
}

# Command: down
cmd_down() {
    local env="$1"
    log_header "Stopping ${env} environment"

    local compose_cmd="docker-compose $(get_compose_files "$env")"
    eval "$compose_cmd down"

    log_success "${env} environment stopped"
}

# Command: restart
cmd_restart() {
    local env="$1"
    local service="${2:-}"

    log_header "Restarting ${env} environment"

    local compose_cmd="docker-compose $(get_compose_files "$env")"
    eval "$compose_cmd restart $service"

    log_success "${env} environment restarted"
}

# Command: logs
cmd_logs() {
    local env="$1"
    local service="${2:-}"
    local follow="${3:--f}"

    local compose_cmd="docker-compose $(get_compose_files "$env")"
    eval "$compose_cmd logs $follow $service"
}

# Command: status
cmd_status() {
    local env="$1"

    log_header "${env} environment status"

    local compose_cmd="docker-compose $(get_compose_files "$env")"
    eval "$compose_cmd ps"
}

# Command: config
cmd_config() {
    local env="$1"

    log_header "Validating ${env} configuration"

    local compose_cmd="docker-compose $(get_compose_files "$env")"
    eval "$compose_cmd config"
}

# Command: clean
cmd_clean() {
    local env="$1"
    local force="${2:-}"

    log_warning "This will remove all volumes and images for ${env} environment"

    if [ "$force" != "-f" ]; then
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Cancelled"
            exit 0
        fi
    fi

    log_header "Cleaning ${env} environment"

    # Stop services
    cmd_down "$env"

    # Remove volumes
    docker volume ls -q | grep "tta_.*_${env}_" | xargs -r docker volume rm

    log_success "${env} environment cleaned"
}

# Command: backup
cmd_backup() {
    local env="$1"
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local backup_dir="${REPO_ROOT}/backups/docker-${env}-${timestamp}"

    mkdir -p "$backup_dir"

    log_header "Backing up ${env} environment"

    # Backup Neo4j
    log_info "Backing up Neo4j..."
    docker exec "tta-${env}-neo4j" neo4j-admin database dump neo4j --to-path=/backups
    docker cp "tta-${env}-neo4j:/backups" "$backup_dir/neo4j"

    # Backup Redis
    log_info "Backing up Redis..."
    docker exec "tta-${env}-redis" redis-cli --rdb /data/backup.rdb BGSAVE
    sleep 5  # Wait for BGSAVE
    docker cp "tta-${env}-redis:/data/backup.rdb" "$backup_dir/redis.rdb"

    log_success "Backup complete: $backup_dir"
}

# Main
main() {
    if [ $# -eq 0 ]; then
        usage
    fi

    local env="$1"
    local cmd="${2:-}"

    # Handle help
    if [ "$env" = "-h" ] || [ "$env" = "--help" ]; then
        usage
    fi

    # Validate environment
    validate_env "$env"

    # Execute command
    case "$cmd" in
        up)
            cmd_up "$env" "${3:-}"
            ;;
        down)
            cmd_down "$env"
            ;;
        restart)
            cmd_restart "$env" "${3:-}"
            ;;
        logs)
            cmd_logs "$env" "${3:-}" "${4:--f}"
            ;;
        status)
            cmd_status "$env"
            ;;
        config)
            cmd_config "$env"
            ;;
        clean)
            cmd_clean "$env" "${3:-}"
            ;;
        backup)
            cmd_backup "$env"
            ;;
        *)
            log_error "Unknown command: $cmd"
            usage
            ;;
    esac
}

main "$@"
