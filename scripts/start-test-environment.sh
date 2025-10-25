#!/bin/bash

# TTA Test Environment Startup Script
# Starts all necessary services for E2E testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/src/player_experience/frontend"
MOCK_SERVER_DIR="$PROJECT_ROOT/tests/e2e/mocks"
ENV_FILE="$PROJECT_ROOT/.env.test"

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Default values
MOCK_API_PORT=${MOCK_API_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
USE_DOCKER=${USE_DOCKER:-false}
SKIP_FRONTEND_BUILD=${SKIP_FRONTEND_BUILD:-false}

# PID files for cleanup
MOCK_API_PID_FILE="/tmp/tta-mock-api.pid"
FRONTEND_PID_FILE="/tmp/tta-frontend.pid"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  TTA Test Environment Setup${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

cleanup() {
    print_info "Cleaning up test environment..."

    # Stop mock API server
    if [ -f "$MOCK_API_PID_FILE" ]; then
        PID=$(cat "$MOCK_API_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            print_info "Stopped mock API server (PID: $PID)"
        fi
        rm -f "$MOCK_API_PID_FILE"
    fi

    # Stop frontend
    if [ -f "$FRONTEND_PID_FILE" ]; then
        PID=$(cat "$FRONTEND_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            print_info "Stopped frontend server (PID: $PID)"
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi

    # Stop Docker services if running
    if [ "$USE_DOCKER" = "true" ]; then
        cd "$PROJECT_ROOT"
        if docker-compose -f docker-compose.test.yml ps -q | grep -q .; then
            docker-compose -f docker-compose.test.yml down
            print_info "Stopped Docker test services"
        fi
    fi

    print_success "Cleanup completed"
}

# Trap cleanup on script exit
trap cleanup EXIT INT TERM

check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi

    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi

    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi

    # Check if mock server directory exists
    if [ ! -d "$MOCK_SERVER_DIR" ]; then
        print_error "Mock server directory not found: $MOCK_SERVER_DIR"
        exit 1
    fi

    print_success "Prerequisites check passed"
}

install_dependencies() {
    print_info "Installing dependencies..."

    # Install root dependencies
    cd "$PROJECT_ROOT"
    if [ -f "package.json" ]; then
        npm install
        print_success "Installed root dependencies"
    fi

    # Install frontend dependencies
    cd "$FRONTEND_DIR"
    if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
        npm install
        print_success "Installed frontend dependencies"
    else
        print_info "Frontend dependencies already installed"
    fi

    # Install mock server dependencies
    cd "$MOCK_SERVER_DIR"
    if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
        npm install
        print_success "Installed mock server dependencies"
    else
        print_info "Mock server dependencies already installed"
    fi
}

start_docker_services() {
    if [ "$USE_DOCKER" = "true" ]; then
        print_info "Starting Docker test services..."

        cd "$PROJECT_ROOT"

        # Check if Docker is available
        if ! command -v docker &> /dev/null; then
            print_warning "Docker not available, skipping Docker services"
            return 0
        fi

        # Start services
        docker-compose -f docker-compose.test.yml up -d

        # Wait for services to be ready
        print_info "Waiting for Docker services to be ready..."

        # Wait for Neo4j
        for i in {1..30}; do
            if curl -s http://localhost:7474/db/data/ > /dev/null 2>&1; then
                print_success "Neo4j is ready"
                break
            fi
            if [ $i -eq 30 ]; then
                print_warning "Neo4j health check timeout, continuing anyway"
            fi
            sleep 2
        done

        # Wait for Redis
        for i in {1..15}; do
            if redis-cli ping > /dev/null 2>&1; then
                print_success "Redis is ready"
                break
            fi
            if [ $i -eq 15 ]; then
                print_warning "Redis health check timeout, continuing anyway"
            fi
            sleep 2
        done
    else
        print_info "Skipping Docker services (USE_DOCKER=false)"
    fi
}

start_mock_api() {
    print_info "Starting mock API server..."

    cd "$MOCK_SERVER_DIR"

    # Check if port is already in use
    if lsof -Pi :$MOCK_API_PORT -sTCP:LISTEN -t >/dev/null; then
        print_warning "Port $MOCK_API_PORT is already in use"
        # Try to find the process and kill it
        PID=$(lsof -Pi :$MOCK_API_PORT -sTCP:LISTEN -t)
        if [ ! -z "$PID" ]; then
            kill "$PID" 2>/dev/null || true
            sleep 2
        fi
    fi

    # Start mock API server
    PORT=$MOCK_API_PORT npm start > /tmp/tta-mock-api.log 2>&1 &
    MOCK_API_PID=$!
    echo $MOCK_API_PID > "$MOCK_API_PID_FILE"

    # Wait for mock API to be ready
    print_info "Waiting for mock API server to be ready..."
    for i in {1..30}; do
        if curl -s "http://localhost:$MOCK_API_PORT/health" > /dev/null 2>&1; then
            print_success "Mock API server is ready at http://localhost:$MOCK_API_PORT"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Mock API server failed to start within 60 seconds"
            cat /tmp/tta-mock-api.log
            exit 1
        fi
        sleep 2
    done
}

build_frontend() {
    if [ "$SKIP_FRONTEND_BUILD" = "true" ]; then
        print_info "Skipping frontend build (SKIP_FRONTEND_BUILD=true)"
        return 0
    fi

    print_info "Building frontend..."

    cd "$FRONTEND_DIR"

    # Set environment variables for build
    export REACT_APP_API_BASE_URL="http://localhost:$MOCK_API_PORT"
    export REACT_APP_WS_URL="ws://localhost:$MOCK_API_PORT"

    # Build frontend
    npm run build
    print_success "Frontend build completed"
}

start_frontend() {
    print_info "Starting frontend server..."

    cd "$FRONTEND_DIR"

    # Check if port is already in use
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null; then
        print_warning "Port $FRONTEND_PORT is already in use"
        # Try to find the process and kill it
        PID=$(lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t)
        if [ ! -z "$PID" ]; then
            kill "$PID" 2>/dev/null || true
            sleep 2
        fi
    fi

    # Set environment variables
    export REACT_APP_API_BASE_URL="http://localhost:$MOCK_API_PORT"
    export REACT_APP_WS_URL="ws://localhost:$MOCK_API_PORT"
    export PORT=$FRONTEND_PORT

    # Start frontend server
    npm start > /tmp/tta-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"

    # Wait for frontend to be ready
    print_info "Waiting for frontend server to be ready..."
    for i in {1..60}; do
        if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
            print_success "Frontend server is ready at http://localhost:$FRONTEND_PORT"
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "Frontend server failed to start within 120 seconds"
            cat /tmp/tta-frontend.log
            exit 1
        fi
        sleep 2
    done
}

show_status() {
    print_info "Test environment status:"
    echo ""

    # Mock API status
    if curl -s "http://localhost:$MOCK_API_PORT/health" > /dev/null 2>&1; then
        print_success "Mock API: http://localhost:$MOCK_API_PORT (Running)"
    else
        print_error "Mock API: http://localhost:$MOCK_API_PORT (Not responding)"
    fi

    # Frontend status
    if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
        print_success "Frontend: http://localhost:$FRONTEND_PORT (Running)"
    else
        print_error "Frontend: http://localhost:$FRONTEND_PORT (Not responding)"
    fi

    # Docker services status
    if [ "$USE_DOCKER" = "true" ]; then
        if curl -s http://localhost:7474/db/data/ > /dev/null 2>&1; then
            print_success "Neo4j: http://localhost:7474 (Running)"
        else
            print_warning "Neo4j: http://localhost:7474 (Not responding)"
        fi

        if redis-cli ping > /dev/null 2>&1; then
            print_success "Redis: localhost:6379 (Running)"
        else
            print_warning "Redis: localhost:6379 (Not responding)"
        fi
    fi

    echo ""
    print_info "Environment ready for E2E testing!"
    print_info "Run tests with: npm run test:e2e"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --use-docker)
            USE_DOCKER=true
            shift
            ;;
        --skip-build)
            SKIP_FRONTEND_BUILD=true
            shift
            ;;
        --mock-port)
            MOCK_API_PORT="$2"
            shift 2
            ;;
        --frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --use-docker          Start Docker services (Neo4j, Redis)"
            echo "  --skip-build          Skip frontend build step"
            echo "  --mock-port PORT      Mock API server port (default: 8000)"
            echo "  --frontend-port PORT  Frontend server port (default: 3000)"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header

    check_prerequisites
    install_dependencies
    start_docker_services
    start_mock_api
    build_frontend
    start_frontend
    show_status

    # Keep script running
    print_info "Test environment is running. Press Ctrl+C to stop."
    while true; do
        sleep 10

        # Check if services are still running
        if ! kill -0 $(cat "$MOCK_API_PID_FILE" 2>/dev/null) 2>/dev/null; then
            print_error "Mock API server stopped unexpectedly"
            exit 1
        fi

        if ! kill -0 $(cat "$FRONTEND_PID_FILE" 2>/dev/null) 2>/dev/null; then
            print_error "Frontend server stopped unexpectedly"
            exit 1
        fi
    done
}

# Run main function
main "$@"
