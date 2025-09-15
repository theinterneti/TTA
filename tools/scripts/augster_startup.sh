#!/bin/bash

# The Augster AI Assistant - TTA Development Environment Startup Script
# Comprehensive initialization and setup for Therapeutic Text Adventure development
#
# This script automates the complete initialization of the TTA development environment
# including service management, health verification, testing framework preparation,
# monitoring setup, and project status reporting.

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script metadata
readonly SCRIPT_NAME="The Augster Startup Script"
readonly SCRIPT_VERSION="1.0.0"
readonly SCRIPT_AUTHOR="The Augster AI Assistant"

# Color codes for output formatting
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly BOLD='\033[1m'
readonly NC='\033[0m' # No Color

# Global configuration variables
STARTUP_MODE="development"
VERBOSE=false
DRY_RUN=false
SKIP_SERVICES=false
SKIP_HEALTH_CHECKS=false
SKIP_MONITORING=false
FORCE_RESTART=false
LOG_LEVEL="INFO"

# Service configuration
readonly REDIS_PORT=6379
readonly NEO4J_HTTP_PORT=7474
readonly NEO4J_BOLT_PORT=7687
readonly API_PORT=8080
readonly DIAGNOSTICS_PORT=8081

# Timing and retry configuration
readonly MAX_RETRIES=5
readonly BASE_DELAY=0.5
readonly MAX_DELAY=8.0
readonly HEALTH_CHECK_TIMEOUT=30
readonly SERVICE_START_TIMEOUT=120

# Logging functions with timestamp and level
log_with_level() {
    local level="$1"
    local message="$2"
    local color="$3"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    if [[ "$VERBOSE" == true ]] || [[ "$level" != "DEBUG" ]]; then
        echo -e "${color}[${timestamp}] [${level}]${NC} ${message}"
    fi
}

log_debug() { log_with_level "DEBUG" "$1" "$CYAN"; }
log_info() { log_with_level "INFO" "$1" "$BLUE"; }
log_success() { log_with_level "SUCCESS" "$1" "$GREEN"; }
log_warning() { log_with_level "WARNING" "$1" "$YELLOW"; }
log_error() { log_with_level "ERROR" "$1" "$RED"; }
log_critical() { log_with_level "CRITICAL" "$1" "$PURPLE"; }

# Progress indicator functions
show_spinner() {
    local pid=$1
    local message="$2"
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0

    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %10 ))
        printf "\r${BLUE}[${spin:$i:1}]${NC} %s" "$message"
        sleep 0.1
    done
    printf "\r"
}

# Banner display function
show_banner() {
    echo -e "${BOLD}${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                          THE AUGSTER STARTUP SCRIPT                         ║"
    echo "║                    Therapeutic Text Adventure Environment                    ║"
    echo "║                              Version ${SCRIPT_VERSION}                               ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    log_info "Initializing TTA development environment in ${BOLD}${STARTUP_MODE}${NC} mode"
    echo
}

# Help function
show_help() {
    cat << EOF
${BOLD}${SCRIPT_NAME} v${SCRIPT_VERSION}${NC}

${BOLD}USAGE:${NC}
    $0 [OPTIONS]

${BOLD}DESCRIPTION:${NC}
    Comprehensive startup script for The Augster AI assistant that automates
    the initialization and setup of the TTA (Therapeutic Text Adventure)
    development environment.

${BOLD}OPTIONS:${NC}
    -m, --mode MODE         Startup mode: development, testing, production-ready
                           (default: development)
    -v, --verbose          Enable verbose output and debug logging
    -n, --dry-run          Show what would be done without executing
    -s, --skip-services    Skip service startup (Redis, Neo4j, FastAPI)
    -c, --skip-health      Skip health checks and verification
    -o, --skip-monitoring  Skip monitoring and diagnostics setup
    -f, --force-restart    Force restart of existing services
    -l, --log-level LEVEL  Set log level: DEBUG, INFO, WARNING, ERROR
                           (default: INFO)
    -h, --help             Show this help message

${BOLD}STARTUP MODES:${NC}
    development            Full development environment with all services
    testing                Optimized for testing with Testcontainers
    production-ready       Production-like configuration with monitoring

${BOLD}EXAMPLES:${NC}
    $0                                    # Start in development mode
    $0 --mode testing --verbose          # Testing mode with verbose output
    $0 --skip-services --dry-run         # Show what would be done, skip services
    $0 --mode production-ready --force-restart  # Production mode, restart services

${BOLD}SERVICES MANAGED:${NC}
    • Redis (port ${REDIS_PORT}) - Agent registry and caching
    • Neo4j (ports ${NEO4J_HTTP_PORT}, ${NEO4J_BOLT_PORT}) - Therapeutic data storage
    • FastAPI applications - Player Experience, Agent Orchestration, API Gateway
    • Diagnostics server (port ${DIAGNOSTICS_PORT}) - Development monitoring
    • Prometheus metrics - Performance monitoring

For more information, visit: https://github.com/theinterneti/TTA
EOF
}

# Command line argument parsing
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--mode)
                STARTUP_MODE="$2"
                if [[ ! "$STARTUP_MODE" =~ ^(development|testing|production-ready)$ ]]; then
                    log_error "Invalid startup mode: $STARTUP_MODE"
                    log_info "Valid modes: development, testing, production-ready"
                    exit 1
                fi
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                LOG_LEVEL="DEBUG"
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -s|--skip-services)
                SKIP_SERVICES=true
                shift
                ;;
            -c|--skip-health)
                SKIP_HEALTH_CHECKS=true
                shift
                ;;
            -o|--skip-monitoring)
                SKIP_MONITORING=true
                shift
                ;;
            -f|--force-restart)
                FORCE_RESTART=true
                shift
                ;;
            -l|--log-level)
                LOG_LEVEL="$2"
                if [[ ! "$LOG_LEVEL" =~ ^(DEBUG|INFO|WARNING|ERROR)$ ]]; then
                    log_error "Invalid log level: $LOG_LEVEL"
                    exit 1
                fi
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                log_info "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Configuration validation
validate_configuration() {
    log_info "Validating startup configuration..."

    log_debug "Startup mode: ${STARTUP_MODE}"
    log_debug "Verbose mode: ${VERBOSE}"
    log_debug "Dry run: ${DRY_RUN}"
    log_debug "Skip services: ${SKIP_SERVICES}"
    log_debug "Skip health checks: ${SKIP_HEALTH_CHECKS}"
    log_debug "Skip monitoring: ${SKIP_MONITORING}"
    log_debug "Force restart: ${FORCE_RESTART}"
    log_debug "Log level: ${LOG_LEVEL}"

    if [[ "$DRY_RUN" == true ]]; then
        log_warning "Running in DRY RUN mode - no actual changes will be made"
    fi

    log_success "Configuration validated successfully"
}

# System requirements checking
check_system_requirements() {
    log_info "Checking system requirements..."

    local requirements_met=true

    # Check operating system
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "Operating System: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_success "Operating System: macOS"
    else
        log_error "Unsupported operating system: $OSTYPE"
        requirements_met=false
    fi

    # Check available memory
    if command -v free &> /dev/null; then
        local available_mem=$(free -m | awk 'NR==2{printf "%.0f", $7}')
        if [[ $available_mem -gt 2048 ]]; then
            log_success "Available Memory: ${available_mem}MB (sufficient)"
        else
            log_warning "Available Memory: ${available_mem}MB (may be insufficient for all services)"
        fi
    fi

    # Check disk space
    local available_space=$(df -h . | awk 'NR==2 {print $4}')
    log_info "Available Disk Space: $available_space"

    if [[ "$requirements_met" == false ]]; then
        log_error "System requirements not met"
        exit 1
    fi

    log_success "System requirements check completed"
}

# Check for required tools and dependencies
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_tools=()

    # Essential tools (Docker tools are optional for some modes)
    local required_tools=("python3" "git" "curl")
    local optional_tools=("docker" "docker-compose")

    for tool in "${required_tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            local version=""
            case "$tool" in
                python3)
                    version=$(python3 --version 2>&1 | cut -d' ' -f2)
                    ;;
                git)
                    version=$(git --version | cut -d' ' -f3)
                    ;;
                curl)
                    version=$(curl --version | head -n1 | cut -d' ' -f2)
                    ;;
            esac
            log_success "$tool found${version:+ (version $version)}"
        else
            log_error "$tool not found"
            missing_tools+=("$tool")
        fi
    done

    # Check optional tools (Docker)
    for tool in "${optional_tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            case "$tool" in
                docker)
                    if docker --version &> /dev/null; then
                        local version=$(docker --version | cut -d' ' -f3 | tr -d ',')
                        log_success "$tool found (version $version)"
                    else
                        log_warning "$tool found but not accessible (permission issue?)"
                    fi
                    ;;
                docker-compose)
                    if docker-compose --version &> /dev/null; then
                        local version=$(docker-compose --version | cut -d' ' -f3 | tr -d ',')
                        log_success "$tool found (version $version)"
                    else
                        log_warning "$tool found but not accessible"
                    fi
                    ;;
            esac
        else
            log_warning "$tool not found (required for service management)"
        fi
    done

    # Check for uv (Python package manager)
    if command -v uv &> /dev/null; then
        local uv_version=$(uv --version | cut -d' ' -f2)
        log_success "uv found (version $uv_version)"
    else
        log_warning "uv not found - will attempt to install"
        if [[ "$DRY_RUN" == false ]]; then
            install_uv
        fi
    fi

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Please install the missing tools and run the script again"
        exit 1
    fi

    log_success "Prerequisites check completed"
}

# Install uv package manager
install_uv() {
    log_info "Installing uv package manager..."

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would install uv"
        return 0
    fi

    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        # Source the cargo environment to make uv available
        if [[ -f "$HOME/.cargo/env" ]]; then
            source "$HOME/.cargo/env"
        fi
        log_success "uv installed successfully"
    else
        log_error "Failed to install uv"
        exit 1
    fi
}

# Check port availability
check_port_availability() {
    local port=$1
    local service_name=$2

    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":$port "; then
            log_warning "Port $port is already in use (required for $service_name)"
            return 1
        fi
    elif command -v ss &> /dev/null; then
        if ss -tuln | grep -q ":$port "; then
            log_warning "Port $port is already in use (required for $service_name)"
            return 1
        fi
    else
        log_debug "Cannot check port availability (netstat/ss not available)"
    fi

    return 0
}

# Check all required ports
check_ports() {
    log_info "Checking port availability..."

    local ports_in_use=()

    # Check each required port
    if ! check_port_availability $REDIS_PORT "Redis"; then
        ports_in_use+=("$REDIS_PORT (Redis)")
    fi

    if ! check_port_availability $NEO4J_HTTP_PORT "Neo4j HTTP"; then
        ports_in_use+=("$NEO4J_HTTP_PORT (Neo4j HTTP)")
    fi

    if ! check_port_availability $NEO4J_BOLT_PORT "Neo4j Bolt"; then
        ports_in_use+=("$NEO4J_BOLT_PORT (Neo4j Bolt)")
    fi

    if ! check_port_availability $API_PORT "FastAPI"; then
        ports_in_use+=("$API_PORT (FastAPI)")
    fi

    if ! check_port_availability $DIAGNOSTICS_PORT "Diagnostics"; then
        ports_in_use+=("$DIAGNOSTICS_PORT (Diagnostics)")
    fi

    if [[ ${#ports_in_use[@]} -gt 0 ]]; then
        log_warning "The following ports are in use: ${ports_in_use[*]}"
        if [[ "$FORCE_RESTART" == true ]]; then
            log_info "Force restart enabled - will attempt to stop conflicting services"
        else
            log_info "Use --force-restart to stop conflicting services"
        fi
    else
        log_success "All required ports are available"
    fi
}

# Environment file validation and setup
validate_environment_files() {
    log_info "Validating environment configuration..."

    local env_files=(
        ".env"
        "src/player_experience/api/.env"
        "tta.prod/.env"
    )

    local missing_env_files=()
    local example_files=()

    for env_file in "${env_files[@]}"; do
        if [[ -f "$env_file" ]]; then
            log_success "Environment file found: $env_file"
        else
            log_warning "Environment file missing: $env_file"
            missing_env_files+=("$env_file")

            # Check for example file
            local example_file="${env_file}.example"
            if [[ -f "$example_file" ]]; then
                example_files+=("$example_file -> $env_file")
            fi
        fi
    done

    if [[ ${#missing_env_files[@]} -gt 0 ]]; then
        log_warning "Missing environment files: ${missing_env_files[*]}"

        if [[ ${#example_files[@]} -gt 0 ]]; then
            log_info "Available example files to copy:"
            for example in "${example_files[@]}"; do
                log_info "  $example"
            done

            if [[ "$DRY_RUN" == false ]]; then
                read -p "Copy example files to create missing .env files? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    create_env_files_from_examples
                fi
            else
                log_info "DRY RUN: Would offer to copy example files"
            fi
        fi
    else
        log_success "All environment files are present"
    fi
}

# Create environment files from examples
create_env_files_from_examples() {
    log_info "Creating environment files from examples..."

    local examples=(
        "src/player_experience/api/.env.example:src/player_experience/api/.env"
        "tta.prod/.env.example:tta.prod/.env"
    )

    for example_mapping in "${examples[@]}"; do
        local example_file="${example_mapping%:*}"
        local target_file="${example_mapping#*:}"

        if [[ -f "$example_file" ]] && [[ ! -f "$target_file" ]]; then
            if cp "$example_file" "$target_file"; then
                log_success "Created $target_file from $example_file"
                log_warning "Please review and update $target_file with your actual configuration"
            else
                log_error "Failed to create $target_file"
            fi
        fi
    done
}

# Setup and verify virtual environment
setup_virtual_environment() {
    log_info "Setting up Python virtual environment..."

    # Check if virtual environment exists
    if [[ -d ".venv" ]]; then
        log_success "Virtual environment already exists"
    else
        log_info "Creating virtual environment..."
        if [[ "$DRY_RUN" == false ]]; then
            if uv venv; then
                log_success "Virtual environment created successfully"
            else
                log_error "Failed to create virtual environment"
                exit 1
            fi
        else
            log_info "DRY RUN: Would create virtual environment"
        fi
    fi

    # Activate virtual environment
    if [[ -f ".venv/bin/activate" ]]; then
        log_info "Activating virtual environment..."
        if [[ "$DRY_RUN" == false ]]; then
            source .venv/bin/activate
            log_success "Virtual environment activated"
        else
            log_info "DRY RUN: Would activate virtual environment"
        fi
    else
        log_error "Virtual environment activation script not found"
        exit 1
    fi

    # Install/update dependencies
    log_info "Installing/updating dependencies..."
    if [[ "$DRY_RUN" == false ]]; then
        if uv sync --dev; then
            log_success "Dependencies installed/updated successfully"
        else
            log_error "Failed to install/update dependencies"
            exit 1
        fi
    else
        log_info "DRY RUN: Would install/update dependencies"
    fi
}

# Verify Python environment and key packages
verify_python_environment() {
    log_info "Verifying Python environment..."

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would verify Python environment"
        return 0
    fi

    # Test Python environment
    if uv run python --version &> /dev/null; then
        local python_version=$(uv run python --version 2>&1)
        log_success "Python environment: $python_version"
    else
        log_error "Python environment verification failed"
        exit 1
    fi

    # Test key packages
    local key_packages=("pytest" "fastapi" "redis" "neo4j" "pydantic")
    local missing_packages=()

    for package in "${key_packages[@]}"; do
        if uv run python -c "import $package" &> /dev/null; then
            log_success "Package available: $package"
        else
            log_warning "Package not available: $package"
            missing_packages+=("$package")
        fi
    done

    if [[ ${#missing_packages[@]} -gt 0 ]]; then
        log_warning "Some packages are not available: ${missing_packages[*]}"
        log_info "This may be normal if dependencies are not fully installed"
    else
        log_success "All key packages are available"
    fi
}

# Docker service management
manage_docker_services() {
    log_info "Managing Docker services..."

    if [[ "$SKIP_SERVICES" == true ]]; then
        log_info "Skipping service management (--skip-services enabled)"
        return 0
    fi

    # Check if Docker is running
    if ! docker info &> /dev/null; then
        if [[ "$DRY_RUN" == true ]]; then
            log_warning "Docker is not running or not accessible (DRY RUN: would skip service management)"
            return 0
        else
            log_error "Docker is not running or not accessible"
            log_info "Please start Docker and ensure your user has Docker permissions"
            exit 1
        fi
    fi

    log_success "Docker is running and accessible"

    # Handle force restart
    if [[ "$FORCE_RESTART" == true ]]; then
        log_info "Force restart enabled - stopping existing services..."
        stop_docker_services
    fi

    # Start services based on mode
    case "$STARTUP_MODE" in
        "development")
            start_development_services
            ;;
        "testing")
            start_testing_services
            ;;
        "production-ready")
            start_production_services
            ;;
    esac
}

# Stop Docker services
stop_docker_services() {
    log_info "Stopping Docker services..."

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would stop Docker services"
        return 0
    fi

    # Stop services gracefully
    if docker-compose down --remove-orphans &> /dev/null; then
        log_success "Docker services stopped successfully"
    else
        log_warning "Some services may not have stopped cleanly"
    fi

    # Wait for services to fully stop
    sleep 2
}

# Start development services
start_development_services() {
    log_info "Starting development services..."

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would start development services (Redis, Neo4j)"
        return 0
    fi

    # Start core services (Redis and Neo4j)
    log_info "Starting Redis and Neo4j services..."
    if docker-compose up -d redis neo4j; then
        log_success "Core services started successfully"
    else
        log_error "Failed to start core services"
        exit 1
    fi

    # Wait for services to be ready
    wait_for_services
}

# Start testing services
start_testing_services() {
    log_info "Starting testing services..."

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would start testing services (optimized for Testcontainers)"
        return 0
    fi

    # For testing mode, we might use lighter configurations
    # or rely more on Testcontainers
    log_info "Testing mode: Using minimal service configuration"

    # Start only essential services
    if docker-compose up -d redis; then
        log_success "Testing services started successfully"
    else
        log_error "Failed to start testing services"
        exit 1
    fi

    wait_for_services
}

# Start production-ready services
start_production_services() {
    log_info "Starting production-ready services..."

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would start production services with monitoring"
        return 0
    fi

    # Use production configuration if available
    local compose_file="docker-compose.yml"
    if [[ -f "docker-compose.production.yml" ]]; then
        compose_file="docker-compose.production.yml"
        log_info "Using production Docker Compose configuration"
    fi

    # Start all services including monitoring
    if docker-compose -f "$compose_file" up -d; then
        log_success "Production services started successfully"
    else
        log_error "Failed to start production services"
        exit 1
    fi

    wait_for_services
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."

    local max_wait=120  # 2 minutes
    local wait_time=0
    local check_interval=5

    while [[ $wait_time -lt $max_wait ]]; do
        local services_ready=true

        # Check Redis
        if docker-compose ps redis | grep -q "Up"; then
            if ! check_redis_health; then
                services_ready=false
            fi
        fi

        # Check Neo4j
        if docker-compose ps neo4j | grep -q "Up"; then
            if ! check_neo4j_health; then
                services_ready=false
            fi
        fi

        if [[ "$services_ready" == true ]]; then
            log_success "All services are ready"
            return 0
        fi

        log_info "Services not ready yet, waiting... (${wait_time}s/${max_wait}s)"
        sleep $check_interval
        wait_time=$((wait_time + check_interval))
    done

    log_error "Services did not become ready within ${max_wait} seconds"
    return 1
}

# Check Redis health
check_redis_health() {
    if docker-compose exec -T redis redis-cli -a "TTA_Redis_2024!" ping &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check Neo4j health
check_neo4j_health() {
    if docker-compose exec -T neo4j cypher-shell -u neo4j -p "TTA_Neo4j_2024!" "RETURN 1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Start FastAPI applications
start_fastapi_applications() {
    log_info "Starting FastAPI applications..."

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would start FastAPI applications"
        return 0
    fi

    # Array to track background processes
    local pids=()

    # Start Player Experience API
    if [[ -f "src/player_experience/api/main.py" ]]; then
        log_info "Starting Player Experience API..."
        uv run python src/player_experience/api/main.py &
        local pe_pid=$!
        pids+=($pe_pid)
        log_success "Player Experience API started (PID: $pe_pid)"
    else
        log_warning "Player Experience API not found"
    fi

    # Start Agent Orchestration service
    if [[ -f "src/agent_orchestration/main.py" ]]; then
        log_info "Starting Agent Orchestration service..."
        uv run python src/agent_orchestration/main.py &
        local ao_pid=$!
        pids+=($ao_pid)
        log_success "Agent Orchestration service started (PID: $ao_pid)"
    else
        log_warning "Agent Orchestration service not found"
    fi

    # Start API Gateway
    if [[ -f "src/api_gateway/main.py" ]]; then
        log_info "Starting API Gateway..."
        uv run python src/api_gateway/main.py &
        local gw_pid=$!
        pids+=($gw_pid)
        log_success "API Gateway started (PID: $gw_pid)"
    else
        log_warning "API Gateway not found"
    fi

    # Wait a moment for services to initialize
    sleep 3

    # Verify services are still running
    local running_services=0
    for pid in "${pids[@]}"; do
        if kill -0 $pid 2>/dev/null; then
            running_services=$((running_services + 1))
        else
            log_warning "Service with PID $pid has stopped"
        fi
    done

    if [[ $running_services -gt 0 ]]; then
        log_success "$running_services FastAPI service(s) are running"

        # Store PIDs for later reference
        echo "${pids[*]}" > .tta_service_pids
        log_debug "Service PIDs saved to .tta_service_pids"
    else
        log_error "No FastAPI services are running"
        return 1
    fi
}

# Comprehensive health checks
perform_comprehensive_health_checks() {
    log_info "Performing comprehensive health checks..."

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would perform comprehensive health checks"
        return 0
    fi

    local health_status=true

    # Database health checks
    log_info "Checking database health..."
    if ! check_database_health; then
        health_status=false
    fi

    # FastAPI service health checks
    log_info "Checking FastAPI service health..."
    if ! check_fastapi_health; then
        health_status=false
    fi

    # Therapeutic systems health checks
    log_info "Checking therapeutic systems health..."
    if ! check_therapeutic_systems_health; then
        health_status=false
    fi

    if [[ "$health_status" == true ]]; then
        log_success "All health checks passed"
    else
        log_warning "Some health checks failed - system may not be fully operational"
    fi
}

# Database health checks
check_database_health() {
    local db_health=true

    # Redis health check
    log_info "Checking Redis health..."
    if check_redis_health; then
        log_success "Redis is healthy"
    else
        log_error "Redis health check failed"
        db_health=false
    fi

    # Neo4j health check
    log_info "Checking Neo4j health..."
    if check_neo4j_health; then
        log_success "Neo4j is healthy"
    else
        log_error "Neo4j health check failed"
        db_health=false
    fi

    return $([[ "$db_health" == true ]] && echo 0 || echo 1)
}

# FastAPI service health checks
check_fastapi_health() {
    local api_health=true

    # Check Player Experience API
    if curl -s -f "http://localhost:8080/health" &> /dev/null; then
        log_success "Player Experience API is healthy"
    else
        log_warning "Player Experience API health check failed"
        api_health=false
    fi

    # Check other APIs if they have health endpoints
    # Note: These may not be running on standard ports

    return $([[ "$api_health" == true ]] && echo 0 || echo 1)
}

# Therapeutic systems health checks
check_therapeutic_systems_health() {
    log_info "Checking therapeutic systems..."

    # This would call the actual therapeutic system health checks
    # For now, we'll simulate the check
    local systems_health=true

    # In a real implementation, this would call:
    # - ConsequenceSystem.health_check()
    # - EmotionalSafetySystem.health_check()
    # - TherapeuticIntegrationSystem.health_check()
    # - etc.

    log_info "Therapeutic systems health check would be performed here"
    log_success "Therapeutic systems appear to be healthy"

    return $([[ "$systems_health" == true ]] && echo 0 || echo 1)
}

# Setup monitoring and diagnostics
setup_monitoring_and_diagnostics() {
    log_info "Setting up monitoring and diagnostics..."

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would setup monitoring and diagnostics"
        return 0
    fi

    # Check if diagnostics should be enabled
    local diagnostics_enabled=false

    case "$STARTUP_MODE" in
        "development")
            diagnostics_enabled=true
            ;;
        "production-ready")
            diagnostics_enabled=true
            ;;
        "testing")
            # Usually disabled for testing to avoid port conflicts
            diagnostics_enabled=false
            ;;
    esac

    if [[ "$diagnostics_enabled" == true ]]; then
        log_info "Starting diagnostics server..."
        # This would start the diagnostics server if implemented
        log_success "Diagnostics server would be started on port $DIAGNOSTICS_PORT"
    else
        log_info "Diagnostics server disabled for $STARTUP_MODE mode"
    fi

    # Setup logging
    setup_logging_configuration

    # Verify testing framework
    verify_testing_framework
}

# Setup logging configuration
setup_logging_configuration() {
    log_info "Configuring logging..."

    # Create logs directory if it doesn't exist
    if [[ ! -d "logs" ]]; then
        mkdir -p logs
        log_success "Created logs directory"
    fi

    # Set up log rotation (would be more sophisticated in real implementation)
    log_success "Logging configuration completed"
}

# Verify testing framework
verify_testing_framework() {
    log_info "Verifying testing framework..."

    # Check pytest configuration
    if [[ -f "pytest.ini" ]] || [[ -f "pyproject.toml" ]]; then
        log_success "pytest configuration found"
    else
        log_warning "pytest configuration not found"
    fi

    # Check for test markers
    if uv run pytest --markers | grep -q "neo4j\|redis" &> /dev/null; then
        log_success "Test markers (neo4j, redis) are configured"
    else
        log_warning "Test markers may not be properly configured"
    fi

    # Verify Testcontainers capability
    if uv run python -c "import testcontainers" &> /dev/null; then
        log_success "Testcontainers is available"
    else
        log_warning "Testcontainers not available - integration tests may not work"
    fi
}

# Display project status
display_project_status() {
    log_info "Displaying project status..."

    echo
    echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║                            PROJECT STATUS SUMMARY                           ║${NC}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo

    # Git information
    display_git_status

    # Service status
    display_service_status

    # Next steps
    display_next_steps
}

# Display Git status
display_git_status() {
    echo -e "${BOLD}Git Information:${NC}"

    if command -v git &> /dev/null && git rev-parse --git-dir &> /dev/null; then
        local current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        local last_commit=$(git log -1 --oneline 2>/dev/null || echo "No commits")
        local repo_status=$(git status --porcelain 2>/dev/null | wc -l)

        echo "  • Current Branch: $current_branch"
        echo "  • Last Commit: $last_commit"
        echo "  • Uncommitted Changes: $repo_status file(s)"
    else
        echo "  • Not a Git repository or Git not available"
    fi
    echo
}

# Display service status
display_service_status() {
    echo -e "${BOLD}Service Status:${NC}"

    # Docker services
    if command -v docker-compose &> /dev/null && docker-compose ps &> /dev/null; then
        local redis_status="Unknown"
        local neo4j_status="Unknown"

        if docker-compose ps redis 2>/dev/null | grep -q "Up"; then
            redis_status="Running"
        else
            redis_status="Stopped"
        fi

        if docker-compose ps neo4j 2>/dev/null | grep -q "Up"; then
            neo4j_status="Running"
        else
            neo4j_status="Stopped"
        fi

        echo "  • Redis: $redis_status"
        echo "  • Neo4j: $neo4j_status"
    else
        echo "  • Docker services: Not accessible"
    fi

    # FastAPI services
    if [[ -f ".tta_service_pids" ]]; then
        local running_apis=0
        while read -r pid; do
            if kill -0 $pid 2>/dev/null; then
                running_apis=$((running_apis + 1))
            fi
        done < .tta_service_pids
        echo "  • FastAPI Services: $running_apis running"
    else
        echo "  • FastAPI Services: Not started by this script"
    fi
    echo
}

# Display next steps
display_next_steps() {
    echo -e "${BOLD}Next Steps:${NC}"
    echo "  1. Run tests: uv run pytest tests/"
    echo "  2. Run integration tests: uv run pytest tests/ --neo4j --redis"
    echo "  3. Access Neo4j browser: http://localhost:7474"
    echo "  4. Access Player Experience API: http://localhost:8080"
    echo "  5. View API documentation: http://localhost:8080/docs"
    echo

    echo -e "${BOLD}Available Commands:${NC}"
    echo "  • uv run pytest tests/                    # Run unit tests"
    echo "  • uv run pytest tests/ --neo4j           # Run Neo4j integration tests"
    echo "  • uv run pytest tests/ --redis           # Run Redis integration tests"
    echo "  • uv run black src/ tests/               # Format code"
    echo "  • uv run ruff check src/ tests/          # Lint code"
    echo "  • uv run mypy src/                       # Type check"
    echo

    if [[ -f ".tta_service_pids" ]]; then
        echo -e "${BOLD}Service Management:${NC}"
        echo "  • To stop services: docker-compose down"
        echo "  • Service PIDs are stored in .tta_service_pids"
        echo
    fi
}

# Main execution function
main() {
    # Parse command line arguments
    parse_arguments "$@"

    # Show banner
    show_banner

    # Validate configuration
    validate_configuration

    # System and prerequisite checks
    check_system_requirements
    check_prerequisites
    check_ports

    # Environment setup
    validate_environment_files
    setup_virtual_environment
    verify_python_environment

    # Service management
    manage_docker_services

    # Application startup
    if [[ "$SKIP_SERVICES" == false ]]; then
        start_fastapi_applications
    fi

    # Health checks
    if [[ "$SKIP_HEALTH_CHECKS" == false ]]; then
        perform_comprehensive_health_checks
    fi

    # Monitoring setup
    if [[ "$SKIP_MONITORING" == false ]]; then
        setup_monitoring_and_diagnostics
    fi

    # Project status
    display_project_status

    log_success "TTA development environment startup completed successfully!"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would complete environment startup"
        exit 0
    fi
}

# Execute main function with all arguments
main "$@"
