#!/bin/bash

# TTA Coverage Integration Validation Script
# This script validates that coverage reporting works correctly with the three-tier test structure

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

# Clean up previous coverage reports
cleanup_coverage() {
    log_info "Cleaning up previous coverage reports..."
    rm -rf htmlcov/
    rm -f coverage.xml coverage.json .coverage
    log_success "Coverage reports cleaned up"
}

# Test unit tests only (no external dependencies)
test_unit_coverage() {
    log_info "Testing unit test coverage (no external dependencies)..."
    
    # Exclude problematic test files that have import issues
    EXCLUDE_PATTERN="not (test_end_to_end_validation or test_performance_validation or test_session_state_validation or test_capability_system_integration)"
    
    uv run pytest tests/ \
        -k "$EXCLUDE_PATTERN and not integration" \
        --cov=src \
        --cov-report=term-missing \
        --cov-report=html:htmlcov/unit \
        --cov-report=xml:coverage_unit.xml \
        --cov-report=json:coverage_unit.json \
        --maxfail=5 \
        -v || {
        log_warning "Some unit tests failed, but continuing with coverage validation"
    }
    
    if [ -f "coverage_unit.xml" ]; then
        log_success "Unit test coverage report generated successfully"
        
        # Extract coverage percentage
        UNIT_COVERAGE=$(python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('coverage_unit.xml')
    root = tree.getroot()
    coverage = root.attrib.get('line-rate', '0')
    print(f'{float(coverage) * 100:.1f}')
except:
    print('0.0')
")
        log_info "Unit test coverage: ${UNIT_COVERAGE}%"
    else
        log_error "Unit test coverage report not generated"
        return 1
    fi
}

# Test Neo4j integration coverage
test_neo4j_coverage() {
    log_info "Testing Neo4j integration test coverage..."
    
    # Check if Neo4j tests exist and can be collected
    NEO4J_TESTS=$(uv run pytest tests/ --collect-only -q --neo4j 2>/dev/null | grep -c "test session starts" || echo "0")
    
    if [ "$NEO4J_TESTS" -gt 0 ]; then
        log_info "Found Neo4j tests, running with coverage..."
        
        uv run pytest tests/ \
            --neo4j \
            --cov=src \
            --cov-report=term-missing \
            --cov-report=html:htmlcov/neo4j \
            --cov-report=xml:coverage_neo4j.xml \
            --cov-report=json:coverage_neo4j.json \
            --maxfail=3 \
            -v || {
            log_warning "Some Neo4j tests failed, but coverage was collected"
        }
        
        if [ -f "coverage_neo4j.xml" ]; then
            log_success "Neo4j integration test coverage report generated"
            
            NEO4J_COVERAGE=$(python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('coverage_neo4j.xml')
    root = tree.getroot()
    coverage = root.attrib.get('line-rate', '0')
    print(f'{float(coverage) * 100:.1f}')
except:
    print('0.0')
")
            log_info "Neo4j integration coverage: ${NEO4J_COVERAGE}%"
        fi
    else
        log_warning "No Neo4j tests found or they cannot be collected"
    fi
}

# Test Redis integration coverage
test_redis_coverage() {
    log_info "Testing Redis integration test coverage..."
    
    # Check if Redis tests exist and can be collected
    REDIS_TESTS=$(uv run pytest tests/ --collect-only -q --redis 2>/dev/null | grep -c "test session starts" || echo "0")
    
    if [ "$REDIS_TESTS" -gt 0 ]; then
        log_info "Found Redis tests, running with coverage..."
        
        uv run pytest tests/ \
            --redis \
            --cov=src \
            --cov-report=term-missing \
            --cov-report=html:htmlcov/redis \
            --cov-report=xml:coverage_redis.xml \
            --cov-report=json:coverage_redis.json \
            --maxfail=3 \
            -v || {
            log_warning "Some Redis tests failed, but coverage was collected"
        }
        
        if [ -f "coverage_redis.xml" ]; then
            log_success "Redis integration test coverage report generated"
            
            REDIS_COVERAGE=$(python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('coverage_redis.xml')
    root = tree.getroot()
    coverage = root.attrib.get('line-rate', '0')
    print(f'{float(coverage) * 100:.1f}')
except:
    print('0.0')
")
            log_info "Redis integration coverage: ${REDIS_COVERAGE}%"
        fi
    else
        log_warning "No Redis tests found or they cannot be collected"
    fi
}

# Test combined integration coverage
test_combined_coverage() {
    log_info "Testing combined integration test coverage..."
    
    uv run pytest tests/ \
        -k "not (test_end_to_end_validation or test_performance_validation or test_session_state_validation or test_capability_system_integration)" \
        --cov=src \
        --cov-report=term-missing \
        --cov-report=html:htmlcov/combined \
        --cov-report=xml:coverage_combined.xml \
        --cov-report=json:coverage_combined.json \
        --maxfail=10 \
        -v || {
        log_warning "Some tests failed, but coverage was collected"
    }
    
    if [ -f "coverage_combined.xml" ]; then
        log_success "Combined test coverage report generated"
        
        COMBINED_COVERAGE=$(python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('coverage_combined.xml')
    root = tree.getroot()
    coverage = root.attrib.get('line-rate', '0')
    print(f'{float(coverage) * 100:.1f}')
except:
    print('0.0')
")
        log_info "Combined test coverage: ${COMBINED_COVERAGE}%"
    fi
}

# Validate coverage reports
validate_reports() {
    log_info "Validating coverage report formats..."
    
    # Check HTML reports
    for report_type in unit neo4j redis combined; do
        if [ -d "htmlcov/$report_type" ]; then
            if [ -f "htmlcov/$report_type/index.html" ]; then
                log_success "HTML coverage report for $report_type is valid"
            else
                log_warning "HTML coverage report for $report_type is missing index.html"
            fi
        fi
    done
    
    # Check XML reports
    for report_type in unit neo4j redis combined; do
        if [ -f "coverage_${report_type}.xml" ]; then
            # Validate XML structure
            python3 -c "
import xml.etree.ElementTree as ET
try:
    ET.parse('coverage_${report_type}.xml')
    print('✅ XML coverage report for $report_type is valid')
except Exception as e:
    print(f'❌ XML coverage report for $report_type is invalid: {e}')
"
        fi
    done
    
    # Check JSON reports
    for report_type in unit neo4j redis combined; do
        if [ -f "coverage_${report_type}.json" ]; then
            # Validate JSON structure
            python3 -c "
import json
try:
    with open('coverage_${report_type}.json') as f:
        data = json.load(f)
    if 'totals' in data and 'files' in data:
        print('✅ JSON coverage report for $report_type is valid')
    else:
        print('❌ JSON coverage report for $report_type is missing required fields')
except Exception as e:
    print(f'❌ JSON coverage report for $report_type is invalid: {e}')
"
        fi
    done
}

# Generate summary report
generate_summary() {
    log_info "Generating coverage integration validation summary..."
    
    cat > coverage_validation_summary.md << EOF
# Coverage Integration Validation Summary

**Date:** $(date)
**Validation Script:** validate_coverage_integration.sh

## Test Results

### Unit Tests (No External Dependencies)
- Status: $([ -f "coverage_unit.xml" ] && echo "✅ Success" || echo "❌ Failed")
- Coverage: ${UNIT_COVERAGE:-"N/A"}%
- Report Files: $([ -f "coverage_unit.xml" ] && echo "XML, " || "")$([ -f "coverage_unit.json" ] && echo "JSON, " || "")$([ -d "htmlcov/unit" ] && echo "HTML" || "")

### Neo4j Integration Tests
- Status: $([ -f "coverage_neo4j.xml" ] && echo "✅ Success" || echo "⚠️ Skipped/Failed")
- Coverage: ${NEO4J_COVERAGE:-"N/A"}%
- Report Files: $([ -f "coverage_neo4j.xml" ] && echo "XML, " || "")$([ -f "coverage_neo4j.json" ] && echo "JSON, " || "")$([ -d "htmlcov/neo4j" ] && echo "HTML" || "")

### Redis Integration Tests
- Status: $([ -f "coverage_redis.xml" ] && echo "✅ Success" || echo "⚠️ Skipped/Failed")
- Coverage: ${REDIS_COVERAGE:-"N/A"}%
- Report Files: $([ -f "coverage_redis.xml" ] && echo "XML, " || "")$([ -f "coverage_redis.json" ] && echo "JSON, " || "")$([ -d "htmlcov/redis" ] && echo "HTML" || "")

### Combined Tests
- Status: $([ -f "coverage_combined.xml" ] && echo "✅ Success" || echo "❌ Failed")
- Coverage: ${COMBINED_COVERAGE:-"N/A"}%
- Report Files: $([ -f "coverage_combined.xml" ] && echo "XML, " || "")$([ -f "coverage_combined.json" ] && echo "JSON, " || "")$([ -d "htmlcov/combined" ] && echo "HTML" || "")

## Coverage Report Formats Validated

- **HTML Reports:** Interactive coverage reports with line-by-line analysis
- **XML Reports:** Machine-readable coverage data for CI/CD integration
- **JSON Reports:** Structured coverage data for programmatic analysis

## Issues Identified

- Some test files have import issues and were excluded from validation
- Integration tests may require external services to run properly
- Coverage thresholds need to be established based on baseline measurements

## Recommendations

1. Fix import issues in excluded test files
2. Set up proper test isolation for integration tests
3. Establish coverage quality gates based on current baseline
4. Integrate coverage reporting with CI/CD pipeline

EOF

    log_success "Coverage validation summary generated: coverage_validation_summary.md"
}

# Main execution
main() {
    echo "=========================================="
    echo "TTA Coverage Integration Validation"
    echo "=========================================="
    echo
    
    cleanup_coverage
    test_unit_coverage
    test_neo4j_coverage
    test_redis_coverage
    test_combined_coverage
    validate_reports
    generate_summary
    
    log_success "Coverage integration validation completed!"
    log_info "Check coverage_validation_summary.md for detailed results"
    log_info "HTML reports available in htmlcov/ directory"
}

# Run main function
main "$@"
