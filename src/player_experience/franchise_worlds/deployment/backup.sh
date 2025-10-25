#!/bin/bash

# TTA Franchise World System - Backup Script
# Performs automated backups of Redis, Neo4j, and application data

set -e

# Configuration
BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# Create backup directory structure
mkdir -p "$BACKUP_DIR/redis"
mkdir -p "$BACKUP_DIR/neo4j"
mkdir -p "$BACKUP_DIR/application"
mkdir -p "$BACKUP_DIR/logs"

# Backup Redis data
backup_redis() {
    log "Starting Redis backup..."

    if docker exec tta-redis redis-cli BGSAVE; then
        # Wait for background save to complete
        while [ "$(docker exec tta-redis redis-cli LASTSAVE)" = "$(docker exec tta-redis redis-cli LASTSAVE)" ]; do
            sleep 1
        done

        # Copy the dump file
        docker cp tta-redis:/data/dump.rdb "$BACKUP_DIR/redis/dump_${TIMESTAMP}.rdb"

        # Compress the backup
        gzip "$BACKUP_DIR/redis/dump_${TIMESTAMP}.rdb"

        log "Redis backup completed: dump_${TIMESTAMP}.rdb.gz"
    else
        log_error "Redis backup failed"
        return 1
    fi
}

# Backup Neo4j data
backup_neo4j() {
    log "Starting Neo4j backup..."

    # Create Neo4j backup using neo4j-admin
    if docker exec tta-neo4j neo4j-admin database dump --database=neo4j --to-path=/tmp neo4j-backup-${TIMESTAMP}.dump; then
        # Copy the backup file
        docker cp tta-neo4j:/tmp/neo4j-backup-${TIMESTAMP}.dump "$BACKUP_DIR/neo4j/"

        # Compress the backup
        gzip "$BACKUP_DIR/neo4j/neo4j-backup-${TIMESTAMP}.dump"

        # Clean up temporary file
        docker exec tta-neo4j rm -f /tmp/neo4j-backup-${TIMESTAMP}.dump

        log "Neo4j backup completed: neo4j-backup-${TIMESTAMP}.dump.gz"
    else
        log_error "Neo4j backup failed"
        return 1
    fi
}

# Backup application logs
backup_logs() {
    log "Starting logs backup..."

    # Create logs archive
    tar -czf "$BACKUP_DIR/logs/logs_${TIMESTAMP}.tar.gz" -C /app/logs . 2>/dev/null || true

    log "Logs backup completed: logs_${TIMESTAMP}.tar.gz"
}

# Backup application configuration
backup_config() {
    log "Starting configuration backup..."

    # Backup configuration files
    tar -czf "$BACKUP_DIR/application/config_${TIMESTAMP}.tar.gz" -C /app/config . 2>/dev/null || true

    log "Configuration backup completed: config_${TIMESTAMP}.tar.gz"
}

# Upload to S3 (if configured)
upload_to_s3() {
    if [ -n "$S3_BUCKET" ] && [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        log "Uploading backups to S3..."

        # Upload Redis backup
        aws s3 cp "$BACKUP_DIR/redis/dump_${TIMESTAMP}.rdb.gz" "s3://$S3_BUCKET/tta-franchise/redis/" || log_error "Failed to upload Redis backup to S3"

        # Upload Neo4j backup
        aws s3 cp "$BACKUP_DIR/neo4j/neo4j-backup-${TIMESTAMP}.dump.gz" "s3://$S3_BUCKET/tta-franchise/neo4j/" || log_error "Failed to upload Neo4j backup to S3"

        # Upload logs backup
        aws s3 cp "$BACKUP_DIR/logs/logs_${TIMESTAMP}.tar.gz" "s3://$S3_BUCKET/tta-franchise/logs/" || log_error "Failed to upload logs backup to S3"

        # Upload config backup
        aws s3 cp "$BACKUP_DIR/application/config_${TIMESTAMP}.tar.gz" "s3://$S3_BUCKET/tta-franchise/config/" || log_error "Failed to upload config backup to S3"

        log "S3 upload completed"
    else
        log "S3 configuration not found, skipping upload"
    fi
}

# Clean up old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."

    # Clean up local backups
    find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

    # Clean up S3 backups (if configured)
    if [ -n "$S3_BUCKET" ] && [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        # This would require a more complex script to handle S3 lifecycle policies
        log "S3 cleanup should be handled by lifecycle policies"
    fi

    log "Cleanup completed"
}

# Verify backup integrity
verify_backups() {
    log "Verifying backup integrity..."

    # Verify Redis backup
    if [ -f "$BACKUP_DIR/redis/dump_${TIMESTAMP}.rdb.gz" ]; then
        if gzip -t "$BACKUP_DIR/redis/dump_${TIMESTAMP}.rdb.gz"; then
            log "Redis backup integrity verified"
        else
            log_error "Redis backup integrity check failed"
            return 1
        fi
    fi

    # Verify Neo4j backup
    if [ -f "$BACKUP_DIR/neo4j/neo4j-backup-${TIMESTAMP}.dump.gz" ]; then
        if gzip -t "$BACKUP_DIR/neo4j/neo4j-backup-${TIMESTAMP}.dump.gz"; then
            log "Neo4j backup integrity verified"
        else
            log_error "Neo4j backup integrity check failed"
            return 1
        fi
    fi

    log "Backup integrity verification completed"
}

# Send notification (if configured)
send_notification() {
    local status=$1
    local message=$2

    if [ -n "$NOTIFICATION_WEBHOOK" ]; then
        curl -X POST "$NOTIFICATION_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"TTA Franchise Backup $status: $message\"}" \
            2>/dev/null || log_error "Failed to send notification"
    fi
}

# Main backup function
main() {
    log "Starting TTA Franchise World System backup..."

    local backup_success=true

    # Perform backups
    backup_redis || backup_success=false
    backup_neo4j || backup_success=false
    backup_logs
    backup_config

    if [ "$backup_success" = true ]; then
        # Verify backups
        verify_backups || backup_success=false

        if [ "$backup_success" = true ]; then
            # Upload to S3
            upload_to_s3

            # Clean up old backups
            cleanup_old_backups

            log "Backup completed successfully"
            send_notification "SUCCESS" "All backups completed successfully at $TIMESTAMP"
        else
            log_error "Backup verification failed"
            send_notification "FAILED" "Backup verification failed at $TIMESTAMP"
            exit 1
        fi
    else
        log_error "Backup process failed"
        send_notification "FAILED" "Backup process failed at $TIMESTAMP"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    --redis-only)
        log "Running Redis-only backup..."
        backup_redis
        verify_backups
        ;;
    --neo4j-only)
        log "Running Neo4j-only backup..."
        backup_neo4j
        verify_backups
        ;;
    --verify)
        log "Verifying latest backups..."
        # Find latest backups and verify them
        latest_redis=$(ls -t "$BACKUP_DIR/redis/"*.gz 2>/dev/null | head -1)
        latest_neo4j=$(ls -t "$BACKUP_DIR/neo4j/"*.gz 2>/dev/null | head -1)

        if [ -n "$latest_redis" ]; then
            gzip -t "$latest_redis" && log "Latest Redis backup is valid" || log_error "Latest Redis backup is corrupted"
        fi

        if [ -n "$latest_neo4j" ]; then
            gzip -t "$latest_neo4j" && log "Latest Neo4j backup is valid" || log_error "Latest Neo4j backup is corrupted"
        fi
        ;;
    --cleanup)
        log "Running cleanup only..."
        cleanup_old_backups
        ;;
    *)
        main
        ;;
esac
