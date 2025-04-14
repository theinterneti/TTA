#!/bin/bash

# TTA Container Orchestration Script
# This script manages the startup and coordination of all TTA containers

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}TTA Container Orchestration${NC}"
echo "=============================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Function to display usage information
show_usage() {
    echo -e "${BLUE}Usage:${NC} $0 [OPTION] [ENVIRONMENT]"
    echo "Orchestrate TTA containers"
    echo ""
    echo -e "${BLUE}Options:${NC}"
    echo "  start         Start containers"
    echo "  stop          Stop containers"
    echo "  restart       Restart containers"
    echo "  status        Show container status"
    echo "  logs          Show container logs"
    echo "  exec          Execute command in container"
    echo "  build         Build containers"
    echo "  help          Show this help message"
    echo ""
    echo -e "${BLUE}Environments:${NC}"
    echo "  dev           Development environment (default)"
    echo "  prod          Production environment"
    echo "  jupyter       Include Jupyter notebook"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  $0 start dev        # Start development environment"
    echo "  $0 start prod       # Start production environment"
    echo "  $0 start jupyter    # Start with Jupyter notebook"
    echo "  $0 logs app         # Show logs for app container"
    echo "  $0 exec app bash    # Run bash in app container"
    echo ""
}

# Function to check container status
check_status() {
    echo -e "${GREEN}Container Status:${NC}"
    echo "-----------------------------"

    # Check root containers
    echo -e "${YELLOW}Root Containers:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "tta-" || echo "No TTA containers running"

    # Check health status
    echo -e "\n${YELLOW}Health Status:${NC}"
    docker ps --format "{{.Names}}\t{{.Status}}" | grep "tta-" | grep "(healthy)" && echo -e "${GREEN}All containers are healthy!${NC}" || echo -e "${RED}Some containers may not be healthy!${NC}"

    echo "-----------------------------"
}

# Function to start containers
start_containers() {
    local env=$1
    local compose_files="-f docker-compose.yml"

    echo -e "${GREEN}Starting TTA containers...${NC}"

    # Determine which compose files to use
    case $env in
        prod)
            echo "Starting production environment..."
            compose_files="$compose_files -f docker-compose.prod.yml"
            ;;
        jupyter)
            echo "Starting with Jupyter notebook..."
            compose_files="$compose_files -f docker-compose.dev.yml"
            profile_arg="--profile with-jupyter"
            ;;
        dev|*)
            echo "Starting development environment..."
            compose_files="$compose_files -f docker-compose.dev.yml"
            ;;
    esac

    # Start the containers
    docker-compose $compose_files up -d $profile_arg

    # Wait for containers to start
    echo "Waiting for containers to start..."
    sleep 10

    # Ensure volume sharing
    bash scripts/ensure_volume_sharing.sh

    # Check container health
    echo -e "${GREEN}Checking container health...${NC}"
    docker ps --format "{{.Names}}\t{{.Status}}" | grep "tta-"

    echo -e "${GREEN}Containers started successfully!${NC}"
}

# Function to stop containers
stop_containers() {
    local env=$1
    local compose_files="-f docker-compose.yml"

    echo -e "${GREEN}Stopping TTA containers...${NC}"

    # Determine which compose files to use
    case $env in
        prod)
            compose_files="$compose_files -f docker-compose.prod.yml"
            ;;
        jupyter)
            compose_files="$compose_files -f docker-compose.dev.yml"
            ;;
        dev|*)
            compose_files="$compose_files -f docker-compose.dev.yml"
            ;;
    esac

    docker-compose $compose_files down
    echo -e "${GREEN}Containers stopped successfully!${NC}"
}

# Function to show container logs
show_logs() {
    local container=$1
    local lines=${2:-100}

    if [ -z "$container" ]; then
        echo -e "${RED}Error: Container name is required${NC}"
        echo "Usage: $0 logs CONTAINER [LINES]"
        exit 1
    fi

    echo -e "${GREEN}Showing logs for $container (last $lines lines)...${NC}"
    docker logs --tail=$lines -f "tta-$container" || docker logs --tail=$lines -f "$container"
}

# Function to execute command in container
exec_command() {
    local container=$1
    shift
    local command=$@

    if [ -z "$container" ]; then
        echo -e "${RED}Error: Container name is required${NC}"
        echo "Usage: $0 exec CONTAINER COMMAND"
        exit 1
    fi

    if [ -z "$command" ]; then
        command="bash"
    fi

    echo -e "${GREEN}Executing '$command' in $container...${NC}"
    docker exec -it "tta-$container" $command || docker exec -it "$container" $command
}

# Function to build containers
build_containers() {
    local env=$1
    local compose_files="-f docker-compose.yml"

    echo -e "${GREEN}Building TTA containers...${NC}"

    # Determine which compose files to use
    case $env in
        prod)
            echo "Building production environment..."
            compose_files="$compose_files -f docker-compose.prod.yml"
            ;;
        jupyter)
            echo "Building with Jupyter notebook..."
            compose_files="$compose_files -f docker-compose.dev.yml"
            profile_arg="--profile with-jupyter"
            ;;
        dev|*)
            echo "Building development environment..."
            compose_files="$compose_files -f docker-compose.dev.yml"
            ;;
    esac

    # Build the containers
    docker-compose $compose_files build $profile_arg

    echo -e "${GREEN}Containers built successfully!${NC}"
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    show_usage
    exit 0
fi

command=$1
shift

case $command in
    start)
        start_containers $1
        ;;
    stop)
        stop_containers $1
        ;;
    restart)
        stop_containers $1
        start_containers $1
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs $@
        ;;
    exec)
        exec_command $@
        ;;
    build)
        build_containers $1
        ;;
    help)
        show_usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$command'${NC}"
        show_usage
        exit 1
        ;;
esac

exit 0
