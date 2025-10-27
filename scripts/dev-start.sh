#!/bin/bash

# TTA Development Environment Startup Script
# This script provides convenient commands for starting different development configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
}

# Function to show help
show_help() {
    print_header "TTA Development Environment Startup Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev         Start TTA services with hot reloading (default)"
    echo "  monitoring  Start monitoring stack (Prometheus + Grafana + Loki)"
    echo "  full        Start TTA services + monitoring stack"
    echo "  stop        Stop all TTA services"
    echo "  clean       Stop and remove all containers, networks, and volumes"
    echo "  status      Show status of all TTA services"
    echo "  logs        Show logs for TTA services"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev          # Start development environment with hot reloading"
    echo "  $0 monitoring   # Start only monitoring stack"
    echo "  $0 full         # Start everything"
    echo "  $0 stop         # Stop all services"
    echo ""
}

# Function to start development environment
start_dev() {
    print_status "Starting TTA development environment with hot reloading..."
    docker-compose -f tta.dev/docker-compose.yml -f docker-compose.hotreload.yml up -d

    print_status "Waiting for services to be ready..."
    sleep 10

    print_header "🚀 TTA Development Environment Started!"
    echo ""
    echo "Services available at:"
    echo "  • Frontend:      http://localhost:3000"
    echo "  • Admin API:     http://localhost:8001"
    echo "  • Clinical API:  http://localhost:8002"
    echo "  • Developer API: http://localhost:8003"
    echo "  • Patient API:   http://localhost:8004"
    echo "  • LangGraph:     http://localhost:8005"
    echo "  • Redis:         localhost:6379"
    echo "  • Neo4j:         http://localhost:7474"
    echo ""
    echo "Hot reloading is enabled - code changes will automatically restart services."
}

# Function to start monitoring stack
start_monitoring() {
    print_status "Starting monitoring stack..."
    cd monitoring
    docker-compose up -d
    cd ..

    print_status "Waiting for monitoring services to be ready..."
    sleep 15

    print_header "📊 Monitoring Stack Started!"
    echo ""
    echo "Monitoring services available at:"
    echo "  • Grafana:    http://localhost:3001 (admin/admin)"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • Loki:       http://localhost:3100"
    echo ""
}

# Function to start full environment
start_full() {
    print_status "Starting full TTA development environment..."
    start_dev
    start_monitoring

    print_header "🎉 Full TTA Development Environment Started!"
    echo ""
    echo "All services are now running with monitoring enabled."
}

# Function to stop services
stop_services() {
    print_status "Stopping TTA services..."
    docker-compose -f tta.dev/docker-compose.yml -f docker-compose.hotreload.yml down

    print_status "Stopping monitoring services..."
    cd monitoring
    docker-compose down
    cd ..

    print_status "All TTA services stopped."
}

# Function to clean up everything
clean_all() {
    print_warning "This will remove all containers, networks, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up TTA environment..."

        # Stop and remove TTA services
        docker-compose -f tta.dev/docker-compose.yml -f docker-compose.hotreload.yml down -v --remove-orphans

        # Stop and remove monitoring services
        cd monitoring
        docker-compose down -v --remove-orphans
        cd ..

        # Remove TTA-related images
        docker images | grep tta | awk '{print $3}' | xargs -r docker rmi -f

        print_status "Cleanup completed."
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to show service status
show_status() {
    print_header "TTA Services Status"
    echo ""

    print_status "TTA Application Services:"
    docker-compose -f tta.dev/docker-compose.yml ps

    echo ""
    print_status "Monitoring Services:"
    cd monitoring
    docker-compose ps
    cd ..
}

# Function to show logs
show_logs() {
    print_status "Showing TTA service logs (press Ctrl+C to exit)..."
    docker-compose -f tta.dev/docker-compose.yml -f docker-compose.hotreload.yml logs -f
}

# Main script logic
main() {
    check_docker

    case "${1:-dev}" in
        "dev")
            start_dev
            ;;
        "monitoring")
            start_monitoring
            ;;
        "full")
            start_full
            ;;
        "stop")
            stop_services
            ;;
        "clean")
            clean_all
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
