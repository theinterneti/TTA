#!/usr/bin/env bash
#
# Monitor Neo4j Staging Environment
#
# This script performs health checks and collects metrics for the Neo4j
# staging deployment as part of the 7-day observation period for the
# Component Maturity Promotion Workflow.
#
# Usage: ./scripts/monitor-neo4j-staging.sh
#
# To run continuously (every 5 minutes):
# watch -n 300 ./scripts/monitor-neo4j-staging.sh
#
# Or set up a cron job:
# */5 * * * * /path/to/scripts/monitor-neo4j-staging.sh
#

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Log directory and files
LOG_DIR="${PROJECT_ROOT}/logs/staging"
mkdir -p "${LOG_DIR}"
HEALTH_LOG="${LOG_DIR}/neo4j-health.log"
METRICS_LOG="${LOG_DIR}/neo4j-metrics.log"

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
TIMESTAMP_UNIX=$(date '+%s')

# Container name
CONTAINER_NAME="tta-neo4j-staging"

# Neo4j credentials
NEO4J_USER="neo4j"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-staging_password_change_me}"

# Health check function
check_health() {
    local status="UNKNOWN"
    local response_time=0
    local error_msg=""

    # Check if container is running
    if ! docker ps | grep -q "${CONTAINER_NAME}"; then
        status="DOWN"
        error_msg="Container not running"
        echo "${TIMESTAMP},${TIMESTAMP_UNIX},${status},${response_time},${error_msg}" >> "${HEALTH_LOG}"
        return 1
    fi

    # Check Neo4j connectivity with timing
    local start_time=$(date +%s%N)
    if docker exec "${CONTAINER_NAME}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" "RETURN 1 AS test" &> /dev/null; then
        local end_time=$(date +%s%N)
        response_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
        status="UP"
    else
        status="DOWN"
        error_msg="Connection failed"
    fi

    # Log health check result
    echo "${TIMESTAMP},${TIMESTAMP_UNIX},${status},${response_time},${error_msg}" >> "${HEALTH_LOG}"

    if [ "${status}" = "UP" ]; then
        return 0
    else
        return 1
    fi
}

# Collect metrics function
collect_metrics() {
    # Get container stats
    local stats=$(docker stats --no-stream --format "{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}}" "${CONTAINER_NAME}" 2>/dev/null || echo "N/A,N/A,N/A,N/A,N/A")

    # Parse stats
    IFS=',' read -r cpu_perc mem_usage mem_perc net_io block_io <<< "${stats}"

    # Get Neo4j-specific metrics (if available)
    local db_size="N/A"
    local node_count="N/A"
    local relationship_count="N/A"

    if docker exec "${CONTAINER_NAME}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" "CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Store file sizes') YIELD attributes RETURN attributes.TotalStoreSize.value AS size" 2>/dev/null | grep -q "size"; then
        db_size=$(docker exec "${CONTAINER_NAME}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" "CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Store file sizes') YIELD attributes RETURN attributes.TotalStoreSize.value AS size" 2>/dev/null | tail -n 1 || echo "N/A")
    fi

    # Count nodes and relationships (lightweight query)
    if docker exec "${CONTAINER_NAME}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" "MATCH (n) RETURN count(n) AS count LIMIT 1" &> /dev/null; then
        node_count=$(docker exec "${CONTAINER_NAME}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" "MATCH (n) RETURN count(n) AS count" 2>/dev/null | tail -n 1 || echo "N/A")
        relationship_count=$(docker exec "${CONTAINER_NAME}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" "MATCH ()-[r]->() RETURN count(r) AS count" 2>/dev/null | tail -n 1 || echo "N/A")
    fi

    # Log metrics
    echo "${TIMESTAMP},${TIMESTAMP_UNIX},${cpu_perc},${mem_usage},${mem_perc},${net_io},${block_io},${db_size},${node_count},${relationship_count}" >> "${METRICS_LOG}"
}

# Initialize log files if they don't exist
initialize_logs() {
    if [ ! -f "${HEALTH_LOG}" ]; then
        echo "timestamp,timestamp_unix,status,response_time_ms,error" > "${HEALTH_LOG}"
    fi

    if [ ! -f "${METRICS_LOG}" ]; then
        echo "timestamp,timestamp_unix,cpu_percent,memory_usage,memory_percent,network_io,block_io,db_size,node_count,relationship_count" > "${METRICS_LOG}"
    fi
}

# Print current status
print_status() {
    echo "========================================="
    echo "Neo4j Staging Health Check"
    echo "========================================="
    echo "Timestamp: ${TIMESTAMP}"
    echo ""

    if check_health; then
        echo "Status: ✅ UP"
        echo ""
        echo "Collecting metrics..."
        collect_metrics
        echo "✅ Metrics collected"
    else
        echo "Status: ❌ DOWN"
        echo ""
        echo "⚠️  Neo4j is not responding"
    fi

    echo ""
    echo "Logs:"
    echo "  Health: ${HEALTH_LOG}"
    echo "  Metrics: ${METRICS_LOG}"
    echo "========================================="
}

# Main execution
main() {
    initialize_logs

    # Run health check and collect metrics
    if check_health; then
        collect_metrics
    fi

    # Print status if running interactively
    if [ -t 1 ]; then
        print_status
    fi
}

# Run main function
main "$@"
