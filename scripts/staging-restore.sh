#!/bin/bash

# TTA Staging Environment Restore Script
# Comprehensive restore solution for homelab staging deployment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-/opt/tta-staging/backups}"
RESTORE_TIMESTAMP="${RESTORE_TIMESTAMP:-}"

# Docker compose configuration
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.staging-homelab.yml"
COMPOSE_PROJECT="tta-staging-homelab"

# Logging
LOG_FILE="$BACKUP_DIR/restore_$(date +"%Y%m%d_%H%M%S").log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Restore TTA Staging Environment from backup

OPTIONS:
    -t, --timestamp TIMESTAMP    Backup timestamp to restore (YYYYMMDD_HHMMSS)
    -l, --list                   List available backups
    -f, --force                  Force restore without confirmation
    -h, --help                   Show this help message

EXAMPLES:
    $0 --list                           # List available backups
    $0 --timestamp 20241201_143000      # Restore specific backup
    $0 --timestamp 20241201_143000 -f  # Force restore without confirmation

ENVIRONMENT VARIABLES:
    BACKUP_DIR      Backup directory (default: /opt/tta-staging/backups)
EOF
}

# List available backups
list_backups() {
    log "Available backups:"

    if [[ ! -d "$BACKUP_DIR" ]]; then
        error "Backup directory not found: $BACKUP_DIR"
        exit 1
    fi

    local manifests=($(find "$BACKUP_DIR" -name "backup_manifest_*.json" | sort -r))

    if [[ ${#manifests[@]} -eq 0 ]]; then
        log "No backups found in $BACKUP_DIR"
        exit 0
    fi

    printf "%-20s %-15s %-10s %s\n" "TIMESTAMP" "TYPE" "SIZE" "COMPONENTS"
    printf "%-20s %-15s %-10s %s\n" "--------" "----" "----" "----------"

    for manifest in "${manifests[@]}"; do
        if [[ -f "$manifest" ]]; then
            local timestamp=$(basename "$manifest" | sed 's/backup_manifest_\(.*\)\.json/\1/')
            local backup_type=$(jq -r '.backup_type // "unknown"' "$manifest")
            local total_size=$(jq -r '.total_size // 0' "$manifest")
            local components=$(jq -r '.components | keys | join(",")' "$manifest")

            # Convert size to human readable
            local size_human=$(numfmt --to=iec --suffix=B "$total_size" 2>/dev/null || echo "${total_size}B")

            printf "%-20s %-15s %-10s %s\n" "$timestamp" "$backup_type" "$size_human" "$components"
        fi
    done
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        error "jq is not installed or not in PATH"
        exit 1
    fi

    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi

    log "Prerequisites check passed"
}

# Validate backup timestamp
validate_backup() {
    local timestamp="$1"
    local manifest_file="$BACKUP_DIR/backup_manifest_${timestamp}.json"

    if [[ ! -f "$manifest_file" ]]; then
        error "Backup manifest not found: $manifest_file"
        exit 1
    fi

    log "Validating backup: $timestamp"

    # Check if all backup files exist
    local components=$(jq -r '.components | keys[]' "$manifest_file")
    local missing_files=()

    for component in $components; do
        local file_path=$(jq -r ".components.${component}.file" "$manifest_file")
        local full_path="$BACKUP_DIR/$file_path"

        if [[ ! -f "$full_path" ]]; then
            missing_files+=("$full_path")
        fi
    done

    if [[ ${#missing_files[@]} -gt 0 ]]; then
        error "Missing backup files:"
        for file in "${missing_files[@]}"; do
            error "  - $file"
        done
        exit 1
    fi

    log "Backup validation passed"
}

# Stop staging services
stop_services() {
    log "Stopping staging services..."

    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" down

    log "Services stopped"
}

# Start staging services
start_services() {
    log "Starting staging services..."

    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" up -d

    # Wait for services to be healthy
    log "Waiting for services to become healthy..."
    sleep 30

    local max_attempts=30
    local attempt=0

    while [[ $attempt -lt $max_attempts ]]; do
        local healthy_services=$(docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" ps --filter "health=healthy" --format "table {{.Service}}" | tail -n +2 | wc -l)
        local total_services=$(docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" ps --format "table {{.Service}}" | tail -n +2 | wc -l)

        if [[ $healthy_services -eq $total_services ]]; then
            log "All services are healthy"
            return 0
        fi

        log "Waiting for services to become healthy ($healthy_services/$total_services)..."
        sleep 10
        ((attempt++))
    done

    error "Services did not become healthy within expected time"
    exit 1
}

# Restore Neo4j database
restore_neo4j() {
    local timestamp="$1"
    local backup_file="$BACKUP_DIR/neo4j/neo4j_backup_${timestamp}.dump.gz"

    log "Restoring Neo4j database..."

    # Decompress backup
    local temp_file="/tmp/neo4j_restore_${timestamp}.dump"
    gunzip -c "$backup_file" > "$temp_file"

    # Copy to container
    docker cp "$temp_file" "${COMPOSE_PROJECT}_neo4j-staging_1:/tmp/restore.dump"

    # Stop Neo4j service
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" stop neo4j-staging

    # Restore database
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" run --rm neo4j-staging \
        neo4j-admin database load --from-path=/tmp --database=tta_staging --overwrite-destination=true

    # Start Neo4j service
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" start neo4j-staging

    # Cleanup
    rm -f "$temp_file"

    log "Neo4j database restored"
}

# Restore Redis database
restore_redis() {
    local timestamp="$1"
    local backup_file="$BACKUP_DIR/redis/redis_backup_${timestamp}.rdb.gz"

    log "Restoring Redis database..."

    # Decompress backup
    local temp_file="/tmp/redis_restore_${timestamp}.rdb"
    gunzip -c "$backup_file" > "$temp_file"

    # Stop Redis service
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" stop redis-staging

    # Copy to container
    docker cp "$temp_file" "${COMPOSE_PROJECT}_redis-staging_1:/data/dump-staging.rdb"

    # Start Redis service
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" start redis-staging

    # Cleanup
    rm -f "$temp_file"

    log "Redis database restored"
}

# Restore PostgreSQL database
restore_postgres() {
    local timestamp="$1"
    local backup_file="$BACKUP_DIR/postgres/postgres_backup_${timestamp}.sql.gz"

    log "Restoring PostgreSQL database..."

    # Decompress and restore
    gunzip -c "$backup_file" | docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T postgres-staging \
        psql -U tta_staging_user -d tta_staging

    log "PostgreSQL database restored"
}

# Main restore function
main() {
    local timestamp="$RESTORE_TIMESTAMP"
    local force=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--timestamp)
                timestamp="$2"
                shift 2
                ;;
            -l|--list)
                list_backups
                exit 0
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    if [[ -z "$timestamp" ]]; then
        error "Backup timestamp is required"
        show_usage
        exit 1
    fi

    log "Starting TTA Staging Environment restore..."
    log "Timestamp: $timestamp"
    log "Backup directory: $BACKUP_DIR"

    check_prerequisites
    validate_backup "$timestamp"

    # Confirmation
    if [[ "$force" != true ]]; then
        echo "WARNING: This will overwrite the current staging environment data!"
        echo "Backup timestamp: $timestamp"
        read -p "Are you sure you want to continue? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log "Restore cancelled by user"
            exit 0
        fi
    fi

    # Perform restore
    stop_services
    restore_neo4j "$timestamp"
    restore_redis "$timestamp"
    restore_postgres "$timestamp"
    start_services

    log "TTA Staging Environment restore completed successfully"
    log "Restored from backup: $timestamp"
    log "Log file: $LOG_FILE"
}

# Run main function with all arguments
main "$@"
