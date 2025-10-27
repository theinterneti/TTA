#!/bin/bash

# TTA Staging Environment Backup Script
# Comprehensive backup solution for homelab staging deployment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-/opt/tta-staging/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ENVIRONMENT="staging"

# Docker compose configuration
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.staging-homelab.yml"
COMPOSE_PROJECT="tta-staging-homelab"

# Logging
LOG_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.log"
mkdir -p "$BACKUP_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
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

    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi

    log "Prerequisites check passed"
}

# Create backup directories
create_backup_dirs() {
    log "Creating backup directories..."

    mkdir -p "$BACKUP_DIR/neo4j"
    mkdir -p "$BACKUP_DIR/redis"
    mkdir -p "$BACKUP_DIR/postgres"
    mkdir -p "$BACKUP_DIR/logs"
    mkdir -p "$BACKUP_DIR/configs"

    log "Backup directories created"
}

# Backup Neo4j database
backup_neo4j() {
    log "Starting Neo4j backup..."

    local backup_file="$BACKUP_DIR/neo4j/neo4j_backup_${TIMESTAMP}.dump"

    # Create Neo4j dump
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T neo4j-staging \
        neo4j-admin database dump --database=tta_staging --to-path=/tmp/backup

    # Copy dump from container
    docker cp "${COMPOSE_PROJECT}_neo4j-staging_1:/tmp/backup/tta_staging.dump" "$backup_file"

    # Compress backup
    gzip "$backup_file"

    log "Neo4j backup completed: ${backup_file}.gz"
}

# Backup Redis database
backup_redis() {
    log "Starting Redis backup..."

    local backup_file="$BACKUP_DIR/redis/redis_backup_${TIMESTAMP}.rdb"

    # Trigger Redis save
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T redis-staging \
        redis-cli BGSAVE

    # Wait for background save to complete
    while [[ $(docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T redis-staging redis-cli LASTSAVE) == $(docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T redis-staging redis-cli LASTSAVE) ]]; do
        sleep 1
    done

    # Copy RDB file from container
    docker cp "${COMPOSE_PROJECT}_redis-staging_1:/data/dump-staging.rdb" "$backup_file"

    # Compress backup
    gzip "$backup_file"

    log "Redis backup completed: ${backup_file}.gz"
}

# Backup PostgreSQL database
backup_postgres() {
    log "Starting PostgreSQL backup..."

    local backup_file="$BACKUP_DIR/postgres/postgres_backup_${TIMESTAMP}.sql"

    # Create PostgreSQL dump
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T postgres-staging \
        pg_dump -U tta_staging_user -d tta_staging --no-password > "$backup_file"

    # Compress backup
    gzip "$backup_file"

    log "PostgreSQL backup completed: ${backup_file}.gz"
}

# Backup application logs
backup_logs() {
    log "Starting logs backup..."

    local logs_backup="$BACKUP_DIR/logs/logs_backup_${TIMESTAMP}.tar.gz"

    # Create logs archive
    docker-compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T player-api-staging \
        tar -czf /tmp/logs_backup.tar.gz -C /app/logs .

    # Copy logs from container
    docker cp "${COMPOSE_PROJECT}_player-api-staging_1:/tmp/logs_backup.tar.gz" "$logs_backup"

    log "Logs backup completed: $logs_backup"
}

# Backup configurations
backup_configs() {
    log "Starting configurations backup..."

    local config_backup="$BACKUP_DIR/configs/configs_backup_${TIMESTAMP}.tar.gz"

    # Create configuration archive
    tar -czf "$config_backup" -C "$PROJECT_ROOT" \
        config/ \
        nginx/ \
        monitoring/ \
        .env.staging-homelab.example \
        docker-compose.staging-homelab.yml

    log "Configurations backup completed: $config_backup"
}

# Create backup manifest
create_manifest() {
    log "Creating backup manifest..."

    local manifest_file="$BACKUP_DIR/backup_manifest_${TIMESTAMP}.json"

    cat > "$manifest_file" << EOF
{
    "backup_timestamp": "$TIMESTAMP",
    "environment": "$ENVIRONMENT",
    "backup_type": "full",
    "components": {
        "neo4j": {
            "file": "neo4j/neo4j_backup_${TIMESTAMP}.dump.gz",
            "size": "$(stat -c%s "$BACKUP_DIR/neo4j/neo4j_backup_${TIMESTAMP}.dump.gz" 2>/dev/null || echo 0)"
        },
        "redis": {
            "file": "redis/redis_backup_${TIMESTAMP}.rdb.gz",
            "size": "$(stat -c%s "$BACKUP_DIR/redis/redis_backup_${TIMESTAMP}.rdb.gz" 2>/dev/null || echo 0)"
        },
        "postgres": {
            "file": "postgres/postgres_backup_${TIMESTAMP}.sql.gz",
            "size": "$(stat -c%s "$BACKUP_DIR/postgres/postgres_backup_${TIMESTAMP}.sql.gz" 2>/dev/null || echo 0)"
        },
        "logs": {
            "file": "logs/logs_backup_${TIMESTAMP}.tar.gz",
            "size": "$(stat -c%s "$BACKUP_DIR/logs/logs_backup_${TIMESTAMP}.tar.gz" 2>/dev/null || echo 0)"
        },
        "configs": {
            "file": "configs/configs_backup_${TIMESTAMP}.tar.gz",
            "size": "$(stat -c%s "$BACKUP_DIR/configs/configs_backup_${TIMESTAMP}.tar.gz" 2>/dev/null || echo 0)"
        }
    },
    "total_size": "$(du -sb "$BACKUP_DIR" | cut -f1)",
    "retention_policy": "${RETENTION_DAYS} days"
}
EOF

    log "Backup manifest created: $manifest_file"
}

# Clean old backups
cleanup_old_backups() {
    log "Cleaning up old backups (retention: $RETENTION_DAYS days)..."

    find "$BACKUP_DIR" -type f -name "*.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -type f -name "*.json" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -type f -name "*.log" -mtime +$RETENTION_DAYS -delete

    log "Old backups cleaned up"
}

# Verify backup integrity
verify_backups() {
    log "Verifying backup integrity..."

    local errors=0

    # Check Neo4j backup
    if [[ -f "$BACKUP_DIR/neo4j/neo4j_backup_${TIMESTAMP}.dump.gz" ]]; then
        if ! gzip -t "$BACKUP_DIR/neo4j/neo4j_backup_${TIMESTAMP}.dump.gz"; then
            error "Neo4j backup integrity check failed"
            ((errors++))
        fi
    else
        error "Neo4j backup file not found"
        ((errors++))
    fi

    # Check Redis backup
    if [[ -f "$BACKUP_DIR/redis/redis_backup_${TIMESTAMP}.rdb.gz" ]]; then
        if ! gzip -t "$BACKUP_DIR/redis/redis_backup_${TIMESTAMP}.rdb.gz"; then
            error "Redis backup integrity check failed"
            ((errors++))
        fi
    else
        error "Redis backup file not found"
        ((errors++))
    fi

    # Check PostgreSQL backup
    if [[ -f "$BACKUP_DIR/postgres/postgres_backup_${TIMESTAMP}.sql.gz" ]]; then
        if ! gzip -t "$BACKUP_DIR/postgres/postgres_backup_${TIMESTAMP}.sql.gz"; then
            error "PostgreSQL backup integrity check failed"
            ((errors++))
        fi
    else
        error "PostgreSQL backup file not found"
        ((errors++))
    fi

    if [[ $errors -eq 0 ]]; then
        log "All backup integrity checks passed"
    else
        error "$errors backup integrity checks failed"
        exit 1
    fi
}

# Main backup function
main() {
    log "Starting TTA Staging Environment backup..."
    log "Timestamp: $TIMESTAMP"
    log "Backup directory: $BACKUP_DIR"
    log "Retention: $RETENTION_DAYS days"

    check_prerequisites
    create_backup_dirs

    # Perform backups
    backup_neo4j
    backup_redis
    backup_postgres
    backup_logs
    backup_configs

    # Create manifest and verify
    create_manifest
    verify_backups

    # Cleanup
    cleanup_old_backups

    log "TTA Staging Environment backup completed successfully"
    log "Backup location: $BACKUP_DIR"
    log "Log file: $LOG_FILE"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--help]"
        echo "Backup TTA Staging Environment"
        echo ""
        echo "Environment variables:"
        echo "  BACKUP_DIR      Backup directory (default: /opt/tta-staging/backups)"
        echo "  RETENTION_DAYS  Backup retention in days (default: 7)"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
