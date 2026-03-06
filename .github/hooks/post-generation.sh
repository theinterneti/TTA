#!/usr/bin/env bash
# Copilot CLI Post-Generation Hook
# Automatically enforces quality gates after code modifications
# Called by: GitHub Copilot CLI after code generation

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAX_ITERATIONS=5
LOG_DIR=".github/hooks/logs"
LOG_FILE="${LOG_DIR}/quality-gates-$(date +%Y%m%d-%H%M%S).log"
ITERATION=0
ALL_PASSED=false

# Create log directory
mkdir -p "${LOG_DIR}"

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] ${level}: ${message}" | tee -a "${LOG_FILE}"
}

# Pretty print functions
print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if uv is available
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "uv not found. Please install: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
}

# Run ruff check
run_ruff() {
    local fix_mode=${1:-""}
    log "INFO" "Running ruff check${fix_mode:+ with $fix_mode}"
    
    local cmd="uv run ruff check src/ tests/"
    if [[ -n "$fix_mode" ]]; then
        cmd="$cmd $fix_mode"
    fi
    
    if eval "$cmd" 2>&1 | tee -a "${LOG_FILE}"; then
        print_success "Ruff check passed"
        return 0
    else
        print_error "Ruff check failed"
        return 1
    fi
}

# Run pyright check
run_pyright() {
    log "INFO" "Running pyright type check"
    
    if uv run pyright src/ 2>&1 | tee -a "${LOG_FILE}"; then
        print_success "Pyright check passed"
        return 0
    else
        print_error "Pyright check failed"
        return 1
    fi
}

# Run pytest
run_pytest() {
    log "INFO" "Running pytest (viable subset)"
    
    local test_files=(
        "tests/unit/test_message_service.py"
        "tests/unit/test_characters_router.py"
        "tests/unit/tools/"
        "tests/agent_orchestration/test_capability_matcher.py"
    )
    
    if uv run pytest "${test_files[@]}" -q --tb=line 2>&1 | tee -a "${LOG_FILE}"; then
        print_success "Pytest passed"
        return 0
    else
        print_error "Pytest failed"
        return 1
    fi
}

# Repair strategy for ruff failures
repair_ruff() {
    local iteration=$1
    
    log "INFO" "Attempting ruff auto-repair (iteration $iteration)"
    
    if [[ $iteration -eq 1 ]]; then
        print_warning "Applying safe auto-fixes..."
        uv run ruff check --fix src/ tests/ 2>&1 | tee -a "${LOG_FILE}" || true
    elif [[ $iteration -eq 2 ]]; then
        print_warning "Applying unsafe auto-fixes..."
        uv run ruff check --fix --unsafe-fixes src/ tests/ 2>&1 | tee -a "${LOG_FILE}" || true
    else
        print_warning "Manual intervention may be required for remaining ruff errors"
    fi
}

# Main quality gate check
run_quality_gates() {
    local iteration=$1
    local ruff_passed=false
    local pyright_passed=false
    local pytest_passed=false
    
    print_header "Quality Gate Check - Iteration $iteration"
    
    # 1. Ruff check
    echo -e "\n${BLUE}1. Ruff Linting${NC}"
    if run_ruff; then
        ruff_passed=true
    else
        repair_ruff "$iteration"
        return 1
    fi
    
    # 2. Pyright check
    echo -e "\n${BLUE}2. Pyright Type Checking${NC}"
    if run_pyright; then
        pyright_passed=true
    else
        print_warning "Pyright failures detected. Manual type annotation fixes may be required."
        return 1
    fi
    
    # 3. Pytest
    echo -e "\n${BLUE}3. Pytest Test Suite${NC}"
    if run_pytest; then
        pytest_passed=true
    else
        print_warning "Test failures detected. Review test output above."
        return 1
    fi
    
    # Check if all passed
    if [[ "$ruff_passed" == true && "$pyright_passed" == true && "$pytest_passed" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Main execution
main() {
    print_header "Copilot CLI Quality Gate Enforcement"
    
    log "INFO" "Starting quality gate checks"
    log "INFO" "Log file: ${LOG_FILE}"
    
    # Check prerequisites
    check_uv
    
    # Repair loop
    while [[ $ITERATION -lt $MAX_ITERATIONS ]]; do
        ITERATION=$((ITERATION + 1))
        
        if run_quality_gates "$ITERATION"; then
            ALL_PASSED=true
            break
        fi
        
        if [[ $ITERATION -lt $MAX_ITERATIONS ]]; then
            print_warning "Quality gates failed. Retrying (attempt $ITERATION/$MAX_ITERATIONS)..."
            sleep 2
        fi
    done
    
    # Final report
    echo ""
    print_header "Quality Gate Summary"
    
    if [[ "$ALL_PASSED" == true ]]; then
        print_success "All quality gates passed after $ITERATION iteration(s)"
        log "INFO" "Quality gates: PASSED"
        exit 0
    else
        print_error "Quality gates failed after $MAX_ITERATIONS iterations"
        print_warning "Manual intervention required. Review logs: ${LOG_FILE}"
        log "ERROR" "Quality gates: FAILED after max iterations"
        exit 1
    fi
}

# Run main function
main "$@"
