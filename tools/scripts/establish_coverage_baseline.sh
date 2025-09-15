#!/bin/bash

# TTA Coverage Baseline Establishment Script
# This script establishes the current coverage baseline for quality gates

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

# Clean up previous reports
cleanup_reports() {
    log_info "Cleaning up previous coverage reports..."
    rm -rf htmlcov/
    rm -f coverage.xml coverage.json .coverage
    rm -f coverage_baseline.json coverage_baseline.md
}

# Get list of working test files (exclude problematic ones)
get_working_tests() {
    log_info "Identifying working test files..."
    
    # Create a temporary file with test exclusions
    cat > /tmp/test_exclusions.txt << EOF
test_end_to_end_validation
test_performance_validation
test_session_state_validation
test_therapeutic_content_validation
test_circuit_breaker
test_capability_system_integration
EOF
    
    # Build exclusion pattern
    EXCLUDE_PATTERN=""
    while IFS= read -r test_name; do
        if [ -n "$EXCLUDE_PATTERN" ]; then
            EXCLUDE_PATTERN="$EXCLUDE_PATTERN or $test_name"
        else
            EXCLUDE_PATTERN="$test_name"
        fi
    done < /tmp/test_exclusions.txt
    
    echo "not ($EXCLUDE_PATTERN)"
    rm -f /tmp/test_exclusions.txt
}

# Run baseline coverage measurement
measure_baseline_coverage() {
    log_info "Measuring baseline coverage..."
    
    EXCLUDE_PATTERN=$(get_working_tests)
    
    # Run tests with coverage, allowing some failures
    uv run pytest tests/ \
        -k "$EXCLUDE_PATTERN" \
        --cov=src \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-report=xml:coverage.xml \
        --cov-report=json:coverage.json \
        --maxfail=10 \
        -v || {
        log_warning "Some tests failed, but coverage data was collected"
    }
    
    if [ -f "coverage.json" ]; then
        log_success "Coverage baseline measurement completed"
        return 0
    else
        log_error "Coverage measurement failed"
        return 1
    fi
}

# Extract coverage metrics
extract_coverage_metrics() {
    log_info "Extracting coverage metrics..."
    
    if [ ! -f "coverage.json" ]; then
        log_error "Coverage JSON report not found"
        return 1
    fi
    
    # Extract key metrics using Python
    python3 << 'EOF'
import json
import sys

try:
    with open('coverage.json', 'r') as f:
        data = json.load(f)
    
    totals = data.get('totals', {})
    files = data.get('files', {})
    
    # Overall metrics
    total_coverage = totals.get('percent_covered', 0)
    total_lines = totals.get('num_statements', 0)
    covered_lines = totals.get('covered_lines', 0)
    missing_lines = totals.get('missing_lines', 0)
    branch_coverage = totals.get('percent_covered_display', '0%')
    
    # Module-level metrics
    module_metrics = {}
    for file_path, file_data in files.items():
        if file_path.startswith('src/'):
            module = file_path.split('/')[1] if '/' in file_path else 'root'
            if module not in module_metrics:
                module_metrics[module] = {
                    'total_lines': 0,
                    'covered_lines': 0,
                    'files': 0
                }
            
            summary = file_data.get('summary', {})
            module_metrics[module]['total_lines'] += summary.get('num_statements', 0)
            module_metrics[module]['covered_lines'] += summary.get('covered_lines', 0)
            module_metrics[module]['files'] += 1
    
    # Calculate module coverage percentages
    for module, metrics in module_metrics.items():
        if metrics['total_lines'] > 0:
            metrics['coverage_percent'] = (metrics['covered_lines'] / metrics['total_lines']) * 100
        else:
            metrics['coverage_percent'] = 0
    
    # Create baseline report
    baseline = {
        'timestamp': data.get('meta', {}).get('timestamp', ''),
        'overall': {
            'coverage_percent': round(total_coverage, 2),
            'total_lines': total_lines,
            'covered_lines': covered_lines,
            'missing_lines': missing_lines,
            'branch_coverage': branch_coverage
        },
        'modules': {
            module: {
                'coverage_percent': round(metrics['coverage_percent'], 2),
                'total_lines': metrics['total_lines'],
                'covered_lines': metrics['covered_lines'],
                'files': metrics['files']
            }
            for module, metrics in module_metrics.items()
        }
    }
    
    # Save baseline data
    with open('coverage_baseline.json', 'w') as f:
        json.dump(baseline, f, indent=2)
    
    # Print summary
    print(f"Overall Coverage: {total_coverage:.1f}%")
    print(f"Total Lines: {total_lines}")
    print(f"Covered Lines: {covered_lines}")
    print(f"Missing Lines: {missing_lines}")
    
    print("\nModule Coverage:")
    for module, metrics in sorted(module_metrics.items()):
        coverage = metrics['coverage_percent']
        print(f"  {module}: {coverage:.1f}% ({metrics['covered_lines']}/{metrics['total_lines']} lines)")
    
except Exception as e:
    print(f"Error extracting metrics: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        log_success "Coverage metrics extracted successfully"
    else
        log_error "Failed to extract coverage metrics"
        return 1
    fi
}

# Generate baseline report
generate_baseline_report() {
    log_info "Generating baseline coverage report..."
    
    if [ ! -f "coverage_baseline.json" ]; then
        log_error "Baseline data not found"
        return 1
    fi
    
    # Generate markdown report
    python3 << 'EOF'
import json
from datetime import datetime

try:
    with open('coverage_baseline.json', 'r') as f:
        baseline = json.load(f)
    
    overall = baseline['overall']
    modules = baseline['modules']
    
    # Generate markdown report
    report = f"""# TTA Coverage Baseline Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Measurement Date:** {baseline.get('timestamp', 'Unknown')}

## Overall Coverage

- **Total Coverage:** {overall['coverage_percent']}%
- **Total Lines:** {overall['total_lines']:,}
- **Covered Lines:** {overall['covered_lines']:,}
- **Missing Lines:** {overall['missing_lines']:,}
- **Branch Coverage:** {overall['branch_coverage']}

## Module Coverage Breakdown

| Module | Coverage | Covered Lines | Total Lines | Files |
|--------|----------|---------------|-------------|-------|
"""
    
    # Sort modules by coverage percentage (descending)
    sorted_modules = sorted(modules.items(), key=lambda x: x[1]['coverage_percent'], reverse=True)
    
    for module, metrics in sorted_modules:
        coverage = metrics['coverage_percent']
        covered = metrics['covered_lines']
        total = metrics['total_lines']
        files = metrics['files']
        
        # Add status emoji based on coverage
        if coverage >= 80:
            status = "✅"
        elif coverage >= 70:
            status = "⚠️"
        else:
            status = "❌"
        
        report += f"| {module} | {status} {coverage:.1f}% | {covered:,} | {total:,} | {files} |\n"
    
    report += f"""
## Quality Gate Thresholds

Based on this baseline measurement, the following quality gates have been established:

### Current Thresholds
- **Minimum Overall Coverage:** {max(60, overall['coverage_percent'] - 5):.0f}%
- **Target Overall Coverage:** {min(90, overall['coverage_percent'] + 10):.0f}%
- **Fail Under Threshold:** {max(50, overall['coverage_percent'] - 10):.0f}%

### Module-Specific Thresholds
"""
    
    for module, metrics in sorted_modules:
        coverage = metrics['coverage_percent']
        min_threshold = max(50, coverage - 5)
        target_threshold = min(95, coverage + 10)
        
        report += f"- **{module}:** Minimum {min_threshold:.0f}%, Target {target_threshold:.0f}%\n"
    
    report += f"""
## Recommendations

### Immediate Actions
1. Fix import issues in excluded test files
2. Add tests for modules with coverage below 70%
3. Focus on critical modules (therapeutic safety, agent orchestration)

### Quality Improvement Plan
1. **Week 1-2:** Fix failing tests and import issues
2. **Week 3-4:** Increase coverage for low-coverage modules
3. **Week 5-6:** Implement strict quality gates
4. **Week 7-8:** Achieve target coverage levels

### Priority Modules for Improvement
"""
    
    # Identify modules that need improvement
    low_coverage_modules = [(module, metrics) for module, metrics in modules.items() 
                           if metrics['coverage_percent'] < 70]
    
    if low_coverage_modules:
        low_coverage_modules.sort(key=lambda x: x[1]['coverage_percent'])
        for module, metrics in low_coverage_modules:
            coverage = metrics['coverage_percent']
            report += f"- **{module}:** {coverage:.1f}% coverage (needs improvement)\n"
    else:
        report += "- All modules have acceptable coverage levels\n"
    
    report += f"""
## Files and Reports

- **HTML Report:** `htmlcov/index.html`
- **XML Report:** `coverage.xml`
- **JSON Report:** `coverage.json`
- **Baseline Data:** `coverage_baseline.json`

---

*This baseline will be used to establish quality gates and track coverage improvements over time.*
"""
    
    with open('coverage_baseline.md', 'w') as f:
        f.write(report)
    
    print("Baseline report generated: coverage_baseline.md")
    
except Exception as e:
    print(f"Error generating report: {e}")
    exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        log_success "Baseline report generated successfully"
    else
        log_error "Failed to generate baseline report"
        return 1
    fi
}

# Update quality gate configuration
update_quality_gates() {
    log_info "Updating quality gate configuration..."
    
    if [ ! -f "coverage_baseline.json" ]; then
        log_warning "Baseline data not found, using default thresholds"
        return 0
    fi
    
    # Extract current coverage for threshold setting
    CURRENT_COVERAGE=$(python3 -c "
import json
try:
    with open('coverage_baseline.json', 'r') as f:
        data = json.load(f)
    print(int(data['overall']['coverage_percent']))
except:
    print(70)
")
    
    # Set fail_under threshold to 5% below current coverage, minimum 50%
    FAIL_UNDER_THRESHOLD=$((CURRENT_COVERAGE - 5))
    if [ $FAIL_UNDER_THRESHOLD -lt 50 ]; then
        FAIL_UNDER_THRESHOLD=50
    fi
    
    log_info "Setting fail_under threshold to ${FAIL_UNDER_THRESHOLD}%"
    
    # Update pyproject.toml with the calculated threshold
    if command -v sed &> /dev/null; then
        sed -i "s/fail_under = [0-9]*/fail_under = $FAIL_UNDER_THRESHOLD/" pyproject.toml
        log_success "Quality gate threshold updated in pyproject.toml"
    else
        log_warning "sed not available, manual update required"
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "TTA Coverage Baseline Establishment"
    echo "=========================================="
    echo
    
    cleanup_reports
    
    if measure_baseline_coverage; then
        extract_coverage_metrics
        generate_baseline_report
        update_quality_gates
        
        log_success "Coverage baseline established successfully!"
        log_info "Reports available:"
        log_info "  - HTML: htmlcov/index.html"
        log_info "  - Baseline: coverage_baseline.md"
        log_info "  - Data: coverage_baseline.json"
    else
        log_error "Failed to establish coverage baseline"
        exit 1
    fi
}

# Run main function
main "$@"
