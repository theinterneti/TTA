#!/bin/bash
# Mutation Testing Runner Script
# Runs mutation testing for Model Management services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
THRESHOLD=85
SERVICES=("model-selector" "fallback-handler" "performance-monitor")

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  ${1}${NC}"
}

print_error() {
    echo -e "${RED}❌ ${1}${NC}"
}

# Function to check if cosmic-ray is installed
check_dependencies() {
    print_info "Checking dependencies..."

    if ! command -v uv &> /dev/null; then
        print_error "uv is not installed. Please install it first:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    # Check if cosmic-ray is available
    if ! uv run cosmic-ray --version &> /dev/null; then
        print_warning "cosmic-ray not found. Installing..."
        uv add --dev cosmic-ray
    fi

    print_success "Dependencies OK"
}

# Function to run mutation testing for a service
run_mutation_test() {
    local service=$1
    local module_path=""
    local test_files=""
    local config_file=""
    local session_file=""
    local report_prefix=""

    case $service in
        "model-selector")
            module_path="src/components/model_management/services/model_selector.py"
            test_files="tests/unit/model_management/services/test_model_selector_properties.py tests/unit/model_management/services/test_model_selector_concrete.py"
            config_file="cosmic-ray-model-selector.toml"
            session_file="session-model-selector.sqlite"
            report_prefix="model-selector"
            ;;
        "fallback-handler")
            module_path="src/components/model_management/services/fallback_handler.py"
            test_files="tests/unit/model_management/services/test_fallback_handler_properties.py tests/unit/model_management/services/test_fallback_handler_concrete.py"
            config_file="cosmic-ray-fallback.toml"
            session_file="session-fallback.sqlite"
            report_prefix="fallback-handler"
            ;;
        "performance-monitor")
            module_path="src/components/model_management/services/performance_monitor.py"
            test_files="tests/unit/model_management/services/test_performance_monitor_properties.py tests/unit/model_management/services/test_performance_monitor_concrete.py"
            config_file="cosmic-ray-performance.toml"
            session_file="session-performance.sqlite"
            report_prefix="performance-monitor"
            ;;
        *)
            print_error "Unknown service: $service"
            return 1
            ;;
    esac

    print_info "Running mutation testing for ${service}..."

    # Create configuration file
    cat > "$config_file" << EOF
[cosmic-ray]
module-path = "${module_path}"
timeout = 10.0
excluded-modules = []
test-command = "uv run pytest ${test_files} -x -q --tb=no -p no:warnings"

[cosmic-ray.distributor]
name = "local"
EOF

    print_info "Configuration created: ${config_file}"

    # Clean up old session if exists
    if [ -f "$session_file" ]; then
        print_warning "Removing old session file: ${session_file}"
        rm "$session_file"
    fi

    # Initialize
    print_info "Initializing mutation testing session..."
    uv run cosmic-ray init "$config_file" "$session_file"

    # Execute
    print_info "Executing mutations (this may take a while)..."
    uv run cosmic-ray exec "$config_file" "$session_file"

    # Generate reports
    print_info "Generating reports..."
    uv run cr-report "$session_file" > "${report_prefix}-report.txt"
    uv run cr-html "$session_file" > "${report_prefix}-report.html"

    # Extract and display mutation score
    local surviving=$(uv run cr-report "$session_file" | grep -oP 'surviving mutants: \d+ \(\K[0-9.]+' | head -1)
    local score=$(echo "100 - $surviving" | bc)

    echo ""
    print_info "Results for ${service}:"
    echo "  Mutation Score: ${score}%"
    echo "  Text Report: ${report_prefix}-report.txt"
    echo "  HTML Report: ${report_prefix}-report.html"
    echo ""

    # Check threshold
    if (( $(echo "$score < $THRESHOLD" | bc -l) )); then
        print_error "Mutation score ${score}% is below threshold ${THRESHOLD}%"
        return 1
    else
        print_success "Mutation score ${score}% meets threshold ${THRESHOLD}%"
        return 0
    fi
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS] [SERVICE]"
    echo ""
    echo "Run mutation testing for Model Management services"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -t, --threshold NUM     Set mutation score threshold (default: 85)"
    echo "  -a, --all               Run all services (default if no service specified)"
    echo ""
    echo "Services:"
    echo "  model-selector          Run ModelSelector mutation tests"
    echo "  fallback-handler        Run FallbackHandler mutation tests"
    echo "  performance-monitor     Run PerformanceMonitor mutation tests"
    echo ""
    echo "Examples:"
    echo "  $0                      # Run all services"
    echo "  $0 model-selector       # Run only ModelSelector"
    echo "  $0 -t 90 --all          # Run all with 90% threshold"
}

# Parse command line arguments
RUN_ALL=false
SELECTED_SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -t|--threshold)
            THRESHOLD="$2"
            shift 2
            ;;
        -a|--all)
            RUN_ALL=true
            shift
            ;;
        model-selector|fallback-handler|performance-monitor)
            SELECTED_SERVICE="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         TTA Mutation Testing Runner                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check dependencies
check_dependencies

# Determine which services to run
SERVICES_TO_RUN=()
if [ -n "$SELECTED_SERVICE" ]; then
    SERVICES_TO_RUN=("$SELECTED_SERVICE")
elif [ "$RUN_ALL" = true ] || [ ${#SERVICES_TO_RUN[@]} -eq 0 ]; then
    SERVICES_TO_RUN=("${SERVICES[@]}")
fi

print_info "Services to test: ${SERVICES_TO_RUN[*]}"
print_info "Mutation score threshold: ${THRESHOLD}%"
echo ""

# Run mutation tests
FAILED_SERVICES=()
PASSED_SERVICES=()

for service in "${SERVICES_TO_RUN[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if run_mutation_test "$service"; then
        PASSED_SERVICES+=("$service")
    else
        FAILED_SERVICES+=("$service")
    fi
    echo ""
done

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Summary                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ ${#PASSED_SERVICES[@]} -gt 0 ]; then
    print_success "Passed (${#PASSED_SERVICES[@]}):"
    for service in "${PASSED_SERVICES[@]}"; do
        echo "  - $service"
    done
    echo ""
fi

if [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
    print_error "Failed (${#FAILED_SERVICES[@]}):"
    for service in "${FAILED_SERVICES[@]}"; do
        echo "  - $service"
    done
    echo ""
    exit 1
else
    print_success "All mutation tests passed!"
    exit 0
fi
