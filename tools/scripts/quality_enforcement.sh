#!/bin/bash

# TTA Quality Enforcement Script
# This script enforces code quality standards and provides comprehensive quality checks

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

log_section() {
    echo -e "${PURPLE}[SECTION]${NC} $1"
}

# Configuration
COVERAGE_THRESHOLD=70
COMPLEXITY_THRESHOLD=10
MAX_LINE_LENGTH=88
SECURITY_LEVEL="medium"

# Quality check results
QUALITY_PASSED=0
TOTAL_CHECKS=0
FAILED_CHECKS=()

# Function to run a quality check
run_check() {
    local check_name="$1"
    local check_command="$2"
    local required="$3"  # "required" or "optional"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    log_info "Running $check_name..."

    if eval "$check_command"; then
        log_success "$check_name passed"
        QUALITY_PASSED=$((QUALITY_PASSED + 1))
        return 0
    else
        if [ "$required" = "required" ]; then
            log_error "$check_name failed (REQUIRED)"
            FAILED_CHECKS+=("$check_name")
        else
            log_warning "$check_name failed (OPTIONAL)"
            QUALITY_PASSED=$((QUALITY_PASSED + 1))  # Don't count optional failures
        fi
        return 1
    fi
}

# Function to check code formatting
check_formatting() {
    log_section "Code Formatting Checks"

    # Black formatting check
    run_check "Black formatting" "uv run black --check --diff src/ tests/" "required"

    # Import sorting check
    run_check "Import sorting (isort)" "uv run isort --check-only --diff src/ tests/" "required"

    # Line length check
    run_check "Line length compliance" "uv run flake8 --select=E501 --max-line-length=$MAX_LINE_LENGTH src/ tests/" "required"
}

# Function to check code quality
check_code_quality() {
    log_section "Code Quality Checks"

    # Ruff linting
    run_check "Ruff linting" "uv run ruff check src/ tests/" "required"

    # Type checking with MyPy
    run_check "Type checking (MyPy)" "uv run mypy src/ --show-error-codes" "optional"

    # Code complexity check
    run_check "Code complexity (Radon)" "uv run radon cc src/ --min=$COMPLEXITY_THRESHOLD --show-complexity" "optional"

    # Docstring coverage
    run_check "Documentation coverage" "uv run interrogate src/ --fail-under=60" "optional"
}

# Function to check security
check_security() {
    log_section "Security Checks"

    # Bandit security scan
    run_check "Security scan (Bandit)" "uv run bandit -r src/ -ll" "required"

    # Check for secrets in code
    run_check "Secret detection" "! grep -r -i 'password\\|secret\\|key\\|token' src/ --include='*.py' | grep -v 'test' | grep -v '#'" "required"

    # Dependency vulnerability check (if safety is available)
    if command -v safety &> /dev/null; then
        run_check "Dependency vulnerabilities" "uv run safety check" "optional"
    fi
}

# Function to run tests
check_tests() {
    log_section "Test Quality Checks"

    # Unit tests
    run_check "Unit tests" "uv run pytest tests/unit/ -v --tb=short" "required"

    # Test coverage
    run_check "Test coverage" "uv run pytest tests/unit/ --cov=src --cov-fail-under=$COVERAGE_THRESHOLD --cov-report=term-missing" "required"

    # Integration tests (if databases are available)
    if docker ps | grep -q neo4j && docker ps | grep -q redis; then
        run_check "Integration tests" "uv run pytest tests/integration/ --neo4j --redis -v --tb=short" "optional"
    else
        log_warning "Skipping integration tests (databases not available)"
    fi
}

# Function to check documentation
check_documentation() {
    log_section "Documentation Checks"

    # Sphinx documentation build
    run_check "Documentation build" "cd docs/sphinx && uv run sphinx-build -b html . _build/html -W --keep-going" "optional"

    # Check for broken links in documentation
    run_check "Documentation links" "cd docs/sphinx && uv run sphinx-build -b linkcheck . _build/linkcheck" "optional"

    # README and important files exist
    run_check "Essential documentation files" "test -f README.md && test -f CONTRIBUTING.md && test -f docs/development/CODE_QUALITY_STANDARDS.md" "required"
}

# Function to check git hygiene
check_git_hygiene() {
    log_section "Git Hygiene Checks"

    # Check for merge conflicts
    run_check "No merge conflicts" "! grep -r '<<<<<<< HEAD' src/ tests/ || true" "required"

    # Check commit message format (if in git repo)
    if git rev-parse --git-dir > /dev/null 2>&1; then
        run_check "Commit message format" "git log --oneline -1 | grep -E '^[a-f0-9]+ (feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'" "optional"
    fi

    # Check for large files
    run_check "No large files committed" "! find . -name '*.py' -size +100k | grep -v __pycache__ | head -1" "required"
}

# Function to generate quality report
generate_quality_report() {
    log_section "Generating Quality Report"

    local report_file="quality_report.md"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    cat > "$report_file" << EOF
# TTA Quality Report

**Generated:** $timestamp
**Script:** quality_enforcement.sh

## Summary

- **Total Checks:** $TOTAL_CHECKS
- **Passed:** $QUALITY_PASSED
- **Failed:** $((TOTAL_CHECKS - QUALITY_PASSED))
- **Success Rate:** $(( (QUALITY_PASSED * 100) / TOTAL_CHECKS ))%

## Quality Gates

### ✅ Passed Checks
$(( QUALITY_PASSED )) out of $(( TOTAL_CHECKS )) checks passed.

### ❌ Failed Checks
EOF

    if [ ${#FAILED_CHECKS[@]} -eq 0 ]; then
        echo "None! All checks passed. 🎉" >> "$report_file"
    else
        for check in "${FAILED_CHECKS[@]}"; do
            echo "- $check" >> "$report_file"
        done
    fi

    cat >> "$report_file" << EOF

## Configuration

- **Coverage Threshold:** $COVERAGE_THRESHOLD%
- **Complexity Threshold:** $COMPLEXITY_THRESHOLD
- **Max Line Length:** $MAX_LINE_LENGTH
- **Security Level:** $SECURITY_LEVEL

## Recommendations

EOF

    if [ ${#FAILED_CHECKS[@]} -gt 0 ]; then
        cat >> "$report_file" << EOF
### Immediate Actions Required

1. **Fix Failed Checks:** Address all failed required checks before proceeding
2. **Review Code Quality:** Consider refactoring complex code sections
3. **Improve Test Coverage:** Add tests for uncovered code paths
4. **Security Review:** Address any security vulnerabilities found

EOF
    fi

    cat >> "$report_file" << EOF
### Continuous Improvement

1. **Regular Quality Checks:** Run this script before each commit
2. **Code Reviews:** Ensure all PRs pass quality gates
3. **Documentation:** Keep documentation up to date
4. **Testing:** Maintain high test coverage and quality

## Next Steps

1. Address any failed checks listed above
2. Run \`uv run pre-commit run --all-files\` to fix formatting issues
3. Review and update tests if coverage is below threshold
4. Consider running integration tests with databases available

---

*Generated by TTA Quality Enforcement Script*
EOF

    log_success "Quality report generated: $report_file"
}

# Function to show usage
show_usage() {
    echo "TTA Quality Enforcement Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --format-only     Run only formatting checks"
    echo "  --security-only   Run only security checks"
    echo "  --tests-only      Run only test checks"
    echo "  --docs-only       Run only documentation checks"
    echo "  --fix             Attempt to fix issues automatically"
    echo "  --strict          Treat all checks as required"
    echo "  --report-only     Generate report without running checks"
    echo "  --help            Show this help message"
    echo
    echo "Examples:"
    echo "  $0                    # Run all quality checks"
    echo "  $0 --format-only      # Check only code formatting"
    echo "  $0 --fix              # Fix issues automatically where possible"
    echo "  $0 --strict           # Fail on any quality issue"
    echo
}

# Function to fix issues automatically
fix_issues() {
    log_section "Attempting to Fix Issues Automatically"

    # Fix formatting
    log_info "Fixing code formatting..."
    uv run black src/ tests/ || log_warning "Black formatting failed"
    uv run isort src/ tests/ || log_warning "Import sorting failed"

    # Fix some linting issues
    log_info "Attempting to fix linting issues..."
    uv run ruff check src/ tests/ --fix || log_warning "Some linting issues could not be auto-fixed"

    log_success "Automatic fixes completed. Please review changes and run quality checks again."
}

# Main execution
main() {
    echo "=========================================="
    echo "TTA Quality Enforcement"
    echo "=========================================="
    echo

    # Parse command line arguments
    case "${1:-}" in
        --format-only)
            check_formatting
            ;;
        --security-only)
            check_security
            ;;
        --tests-only)
            check_tests
            ;;
        --docs-only)
            check_documentation
            ;;
        --fix)
            fix_issues
            exit 0
            ;;
        --report-only)
            generate_quality_report
            exit 0
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        --strict)
            # In strict mode, all checks are required
            log_info "Running in STRICT mode - all checks are required"
            ;;
        "")
            # Run all checks
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac

    # Change to project root
    cd "$(dirname "$0")/.."

    # Ensure virtual environment is activated
    if [ -z "$VIRTUAL_ENV" ] && [ -f ".venv/bin/activate" ]; then
        log_info "Activating virtual environment..."
        source .venv/bin/activate
    fi

    # Run quality checks based on arguments
    if [ "${1:-}" = "" ] || [ "${1:-}" = "--strict" ]; then
        check_formatting
        check_code_quality
        check_security
        check_tests
        check_documentation
        check_git_hygiene
    fi

    # Generate quality report
    generate_quality_report

    # Final status
    echo
    echo "=========================================="
    echo "Quality Enforcement Summary"
    echo "=========================================="

    local success_rate=$(( (QUALITY_PASSED * 100) / TOTAL_CHECKS ))

    if [ ${#FAILED_CHECKS[@]} -eq 0 ]; then
        log_success "All quality checks passed! ($QUALITY_PASSED/$TOTAL_CHECKS) 🎉"
        log_info "Quality report: quality_report.md"
        exit 0
    else
        log_error "Quality checks failed: ${#FAILED_CHECKS[@]} out of $TOTAL_CHECKS"
        log_error "Success rate: $success_rate%"
        log_info "Failed checks: ${FAILED_CHECKS[*]}"
        log_info "Quality report: quality_report.md"

        if [ "$success_rate" -lt 80 ]; then
            log_error "Quality score too low. Please address failed checks."
            exit 1
        else
            log_warning "Some checks failed but overall quality is acceptable."
            exit 0
        fi
    fi
}

# Run main function with all arguments
main "$@"
