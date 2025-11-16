#!/bin/bash
# Quick start script for TTA Monitoring Stack (Development)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== TTA Monitoring Stack Setup ===${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Function to show help
show_help() {
    cat << EOF
Usage: $0 [command]

Commands:
    start       Start monitoring stack (Prometheus + Grafana)
    stop        Stop monitoring stack
    restart     Restart monitoring stack
    logs        Show logs from monitoring services
    status      Show status of monitoring services
    clean       Stop and remove all monitoring volumes (WARNING: deletes data)
    help        Show this help message

Examples:
    $0 start            # Start the monitoring stack
    $0 logs             # View logs
    $0 status           # Check if services are running

Access URLs:
    Prometheus:  http://localhost:9090
    Grafana:     http://localhost:3000 (admin/admin)
    Node Exporter: http://localhost:9100

EOF
}

# Function to start monitoring
start_monitoring() {
    echo -e "${YELLOW}Starting monitoring stack...${NC}"
    docker-compose -f docker-compose.dev.yml --profile monitoring up -d

    echo ""
    echo -e "${GREEN}Monitoring stack started successfully!${NC}"
    echo ""
    echo "Access the services at:"
    echo -e "  Prometheus:  ${GREEN}http://localhost:9090${NC}"
    echo -e "  Grafana:     ${GREEN}http://localhost:3000${NC} (admin/admin)"
    echo -e "  Node Exporter: ${GREEN}http://localhost:9100${NC}"
    echo ""
    echo "Tip: Run '$0 logs' to view logs"
}

# Function to stop monitoring
stop_monitoring() {
    echo -e "${YELLOW}Stopping monitoring stack...${NC}"
    docker-compose -f docker-compose.dev.yml --profile monitoring down
    echo -e "${GREEN}Monitoring stack stopped.${NC}"
}

# Function to restart monitoring
restart_monitoring() {
    echo -e "${YELLOW}Restarting monitoring stack...${NC}"
    stop_monitoring
    sleep 2
    start_monitoring
}

# Function to show logs
show_logs() {
    docker-compose -f docker-compose.dev.yml --profile monitoring logs -f
}

# Function to show status
show_status() {
    echo -e "${YELLOW}Monitoring Stack Status:${NC}"
    echo ""
    docker ps --filter "name=tta-prometheus-dev" --filter "name=tta-grafana-dev" --filter "name=tta-node-exporter-dev" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    echo ""
    echo -e "${YELLOW}Checking service health...${NC}"

    # Check Prometheus
    if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
        echo -e "  Prometheus:  ${GREEN}✓ Healthy${NC}"
    else
        echo -e "  Prometheus:  ${RED}✗ Not responding${NC}"
    fi

    # Check Grafana
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo -e "  Grafana:     ${GREEN}✓ Healthy${NC}"
    else
        echo -e "  Grafana:     ${RED}✗ Not responding${NC}"
    fi

    # Check Node Exporter
    if curl -s http://localhost:9100/metrics > /dev/null 2>&1; then
        echo -e "  Node Exporter: ${GREEN}✓ Healthy${NC}"
    else
        echo -e "  Node Exporter: ${RED}✗ Not responding${NC}"
    fi
}

# Function to clean everything
clean_monitoring() {
    echo -e "${RED}WARNING: This will stop monitoring and delete all stored metrics!${NC}"
    read -p "Are you sure? (yes/no): " -r
    echo
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}Cleaning monitoring stack...${NC}"
        docker-compose -f docker-compose.dev.yml --profile monitoring down -v
        echo -e "${GREEN}Monitoring stack cleaned.${NC}"
    else
        echo "Cancelled."
    fi
}

# Main command handler
case "${1:-help}" in
    start)
        start_monitoring
        ;;
    stop)
        stop_monitoring
        ;;
    restart)
        restart_monitoring
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    clean)
        clean_monitoring
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
