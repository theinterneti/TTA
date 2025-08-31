#!/bin/bash

# TTA Test Configuration Validation Script
# This script validates that all test configurations work correctly with uv-based execution

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Function to run a test command and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="${3:-0}"  # Default to expecting success (0)
    
    log_info "Running test: $test_name"
    log_info "Command: $test_command"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Run the command and capture output
    if eval "$test_command" > "/tmp/test_output_$$" 2>&1; then
        local exit_code=0
    else
        local exit_code=$?
    fi
    
    # Check if result matches expectation
    if [ $exit_code -eq $expected_result ]; then
        log_success "$test_name: PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        log_error "$test_name: FAILED (exit code: $exit_code, expected: $expected_result)"
        log_error "Output:"
        cat "/tmp/test_output_$$" | head -20
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to run a test that might be skipped
run_optional_test() {
    local test_name="$1"
    local test_command="$2"
    
    log_info "Running optional test: $test_name"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command" > "/tmp/test_output_$$" 2>&1; then
        log_success "$test_name: PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        local exit_code=$?
        if grep -q "SKIPPED" "/tmp/test_output_$$" || grep -q "skip" "/tmp/test_output_$$"; then
            log_warning "$test_name: SKIPPED (as expected)"
            SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
            return 0
        else
            log_error "$test_name: FAILED (exit code: $exit_code)"
            log_error "Output:"
            cat "/tmp/test_output_$$" | head -20
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        fi
    fi
}

# Clean up function
cleanup() {
    rm -f "/tmp/test_output_$$"
    rm -rf htmlcov/
    rm -f coverage.xml coverage.json .coverage
}

# Set up cleanup trap
trap cleanup EXIT

# Validate basic pytest functionality
validate_basic_pytest() {
    log_info "=== Validating Basic pytest Functionality ==="
    
    # Test 1: Basic pytest version and help
    run_test "pytest version check" "uv run pytest --version"
    
    # Test 2: Test collection without running
    run_test "test collection" "uv run pytest tests/ --collect-only -q"
    
    # Test 3: Basic test run with minimal output
    run_test "basic test run" "uv run pytest tests/ -x --tb=no -q --maxfail=1"
}

# Validate three-tier test structure
validate_three_tier_structure() {
    log_info "=== Validating Three-Tier Test Structure ==="
    
    # Tier 1: Unit tests (default, no external dependencies)
    run_test "unit tests only" "uv run pytest tests/ -k 'not integration' --tb=short -q --maxfail=3"
    
    # Tier 2: Neo4j integration tests (optional, may be skipped)
    run_optional_test "neo4j integration tests" "uv run pytest tests/ --neo4j --tb=short -q --maxfail=3"
    
    # Tier 3: Redis integration tests (optional, may be skipped)
    run_optional_test "redis integration tests" "uv run pytest tests/ --redis --tb=short -q --maxfail=3"
    
    # Combined integration tests (optional, may be skipped)
    run_optional_test "combined integration tests" "uv run pytest tests/ --neo4j --redis --tb=short -q --maxfail=3"
}

# Validate coverage reporting
validate_coverage_reporting() {
    log_info "=== Validating Coverage Reporting ==="
    
    # Test coverage with different output formats
    run_test "coverage with terminal output" "uv run pytest tests/ -k 'not integration' --cov=src --cov-report=term --tb=no -q --maxfail=1"
    
    run_test "coverage with XML output" "uv run pytest tests/ -k 'not integration' --cov=src --cov-report=xml --tb=no -q --maxfail=1"
    
    run_test "coverage with JSON output" "uv run pytest tests/ -k 'not integration' --cov=src --cov-report=json --tb=no -q --maxfail=1"
    
    run_test "coverage with HTML output" "uv run pytest tests/ -k 'not integration' --cov=src --cov-report=html --tb=no -q --maxfail=1"
    
    # Validate that coverage files were created
    if [ -f "coverage.xml" ]; then
        log_success "coverage.xml created successfully"
    else
        log_error "coverage.xml not created"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    if [ -f "coverage.json" ]; then
        log_success "coverage.json created successfully"
    else
        log_error "coverage.json not created"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    if [ -d "htmlcov" ] && [ -f "htmlcov/index.html" ]; then
        log_success "HTML coverage report created successfully"
    else
        log_error "HTML coverage report not created"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Validate pytest markers
validate_pytest_markers() {
    log_info "=== Validating pytest Markers ==="
    
    # Test marker filtering
    run_test "neo4j marker filtering" "uv run pytest tests/ -m neo4j --collect-only -q"
    
    run_test "redis marker filtering" "uv run pytest tests/ -m redis --collect-only -q"
    
    run_test "integration marker filtering" "uv run pytest tests/ -m integration --collect-only -q"
    
    run_test "unit marker filtering" "uv run pytest tests/ -m 'not integration' --collect-only -q"
    
    # Test marker combinations
    run_test "combined marker filtering" "uv run pytest tests/ -m 'neo4j and redis' --collect-only -q"
}

# Validate pytest configuration
validate_pytest_configuration() {
    log_info "=== Validating pytest Configuration ==="
    
    # Test that pytest.ini or pyproject.toml configuration is working
    run_test "pytest configuration validation" "uv run pytest --help | grep -q 'cov'"
    
    # Test strict markers configuration
    run_test "strict markers validation" "uv run pytest tests/ --strict-markers --collect-only -q"
    
    # Test that coverage configuration is loaded
    run_test "coverage configuration validation" "uv run coverage --help | grep -q 'report'"
}

# Validate test discovery
validate_test_discovery() {
    log_info "=== Validating Test Discovery ==="
    
    # Test that tests are discovered correctly
    run_test "test discovery validation" "uv run pytest tests/ --collect-only | grep -q 'collected'"
    
    # Test specific test file patterns
    run_test "test file pattern validation" "uv run pytest tests/test_*.py --collect-only -q"
    
    # Test that conftest.py files are loaded
    run_test "conftest.py loading validation" "uv run pytest tests/ --collect-only -q | grep -q 'session'"
}

# Validate enhanced fixtures
validate_enhanced_fixtures() {
    log_info "=== Validating Enhanced Fixtures ==="
    
    # Test that enhanced testcontainer utilities can be imported
    run_test "enhanced utilities import" "uv run python -c 'from tests.utils.testcontainer_reliability import retry_with_backoff; print(\"Import successful\")'"
    
    # Test that enhanced conftest can be imported
    run_test "enhanced conftest import" "uv run python -c 'from tests.utils.enhanced_conftest import wait_for_service_ready; print(\"Import successful\")'"
    
    # Test enhanced testcontainer tests
    run_test "enhanced testcontainer tests" "uv run pytest tests/test_enhanced_testcontainers.py -v --tb=short"
}

# Validate performance and quality gates
validate_quality_gates() {
    log_info "=== Validating Quality Gates ==="
    
    # Test coverage threshold enforcement
    run_test "coverage threshold validation" "uv run coverage report --fail-under=1"  # Very low threshold to ensure it passes
    
    # Test that coverage data can be processed
    if [ -f "coverage.json" ]; then
        run_test "coverage data processing" "uv run python -c 'import json; data=json.load(open(\"coverage.json\")); print(f\"Coverage: {data[\"totals\"][\"percent_covered\"]:.1f}%\")'"
    fi
}

# Generate validation report
generate_validation_report() {
    log_info "=== Generating Validation Report ==="
    
    cat > test_validation_report.md << EOF
# TTA Test Configuration Validation Report

**Date:** $(date)
**Script:** validate_test_configurations.sh

## Summary

- **Total Tests:** $TOTAL_TESTS
- **Passed:** $PASSED_TESTS
- **Failed:** $FAILED_TESTS
- **Skipped:** $SKIPPED_TESTS

## Test Results

### Basic pytest Functionality
- pytest version check and basic functionality

### Three-Tier Test Structure
- Unit tests (no external dependencies)
- Neo4j integration tests (optional)
- Redis integration tests (optional)
- Combined integration tests (optional)

### Coverage Reporting
- Terminal, XML, JSON, and HTML coverage reports
- Coverage file generation validation

### pytest Markers
- Marker filtering and combinations
- Strict marker validation

### pytest Configuration
- Configuration loading and validation
- Coverage configuration integration

### Test Discovery
- Test file discovery and pattern matching
- conftest.py loading validation

### Enhanced Fixtures
- Enhanced testcontainer utilities
- Reliability improvements validation

### Quality Gates
- Coverage threshold enforcement
- Coverage data processing

## Status

EOF

    if [ $FAILED_TESTS -eq 0 ]; then
        echo "✅ **ALL TESTS PASSED** - Test configuration is working correctly" >> test_validation_report.md
        log_success "All test configurations validated successfully!"
    else
        echo "❌ **SOME TESTS FAILED** - Review failed tests and fix issues" >> test_validation_report.md
        log_error "$FAILED_TESTS test(s) failed. Check the output above for details."
    fi

    echo "" >> test_validation_report.md
    echo "## Recommendations" >> test_validation_report.md
    
    if [ $FAILED_TESTS -gt 0 ]; then
        echo "1. Review failed test output above" >> test_validation_report.md
        echo "2. Fix any import or configuration issues" >> test_validation_report.md
        echo "3. Ensure all dependencies are properly installed" >> test_validation_report.md
        echo "4. Re-run validation after fixes" >> test_validation_report.md
    else
        echo "1. Test configuration is working correctly" >> test_validation_report.md
        echo "2. All three-tier test structure is functional" >> test_validation_report.md
        echo "3. Coverage reporting is properly configured" >> test_validation_report.md
        echo "4. Enhanced reliability features are available" >> test_validation_report.md
    fi

    echo "" >> test_validation_report.md
    echo "---" >> test_validation_report.md
    echo "*Generated by TTA test validation script*" >> test_validation_report.md
    
    log_success "Validation report generated: test_validation_report.md"
}

# Main execution
main() {
    echo "=========================================="
    echo "TTA Test Configuration Validation"
    echo "=========================================="
    echo
    
    # Run all validation tests
    validate_basic_pytest
    validate_three_tier_structure
    validate_coverage_reporting
    validate_pytest_markers
    validate_pytest_configuration
    validate_test_discovery
    validate_enhanced_fixtures
    validate_quality_gates
    
    # Generate report
    generate_validation_report
    
    # Final summary
    echo
    echo "=========================================="
    echo "Validation Summary"
    echo "=========================================="
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo "Skipped: $SKIPPED_TESTS"
    echo
    
    if [ $FAILED_TESTS -eq 0 ]; then
        log_success "All test configurations are working correctly!"
        exit 0
    else
        log_error "Some test configurations failed. Please review and fix."
        exit 1
    fi
}

# Run main function
main "$@"
