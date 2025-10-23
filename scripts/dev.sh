#!/usr/bin/env bash
# Development convenience commands for TTA project
# Usage: ./scripts/dev.sh <command>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function for colored output
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Command functions
cmd_lint() {
    info "Running Ruff linter..."
    uv run ruff check src/ tests/
}

cmd_lint_fix() {
    info "Running Ruff linter with auto-fix..."
    uv run ruff check --fix src/ tests/
}

cmd_format() {
    info "Formatting code with Ruff..."
    uv run ruff format src/ tests/
}

cmd_format_check() {
    info "Checking code formatting..."
    uv run ruff format --check src/ tests/
}

cmd_quality() {
    info "Running quality checks (lint + format-check)..."
    cmd_lint
    cmd_format_check
    info "✓ All quality checks passed!"
}

cmd_quality_fix() {
    info "Running quality fixes (lint-fix + format)..."
    cmd_lint_fix
    cmd_format
    info "✓ All quality fixes applied!"
}

cmd_typecheck() {
    info "Running Pyright type checker (10-100x faster than MyPy)..."
    uv run pyright src/
}

cmd_test() {
    info "Running tests..."
    uv run pytest tests/
}

cmd_test_fast() {
    info "Running tests (fast mode: stop on first failure, run failed tests first)..."
    uv run pytest tests/ -x --ff
}

cmd_test_cov() {
    info "Running tests with coverage..."
    uv run pytest tests/ --cov=src --cov-report=html --cov-report=term
    info "Coverage report generated in htmlcov/index.html"
}

cmd_test_parallel() {
    info "Running tests in parallel..."
    uv run pytest tests/ -n auto
}

cmd_check_all() {
    info "Running full validation (quality + typecheck + test)..."
    cmd_quality
    cmd_typecheck
    cmd_test
    info "✓ All checks passed!"
}

cmd_dev_check() {
    info "Running quick dev workflow (quality-fix + test-fast)..."
    cmd_quality_fix
    cmd_test_fast
    info "✓ Dev check complete!"
}

cmd_help() {
    cat << EOF
TTA Development Commands
========================

Linting and Formatting:
  lint              Run Ruff linter
  lint-fix          Run Ruff linter with auto-fix
  format            Format code with Ruff
  format-check      Check code formatting

Combined Quality Checks:
  quality           Run lint + format-check
  quality-fix       Run lint-fix + format

Type Checking:
  typecheck         Run Pyright type checker (10-100x faster than MyPy)

Testing:
  test              Run all tests
  test-fast         Run tests (stop on first failure, run failed tests first)
  test-cov          Run tests with coverage report
  test-parallel     Run tests in parallel

Combined Workflows:
  check-all         Full validation (quality + typecheck + test)
  dev-check         Quick dev workflow (quality-fix + test-fast)

Usage:
  ./scripts/dev.sh <command>

Examples:
  ./scripts/dev.sh dev-check      # Quick check before commit
  ./scripts/dev.sh check-all      # Full validation
  ./scripts/dev.sh quality-fix    # Fix all linting and formatting issues
  ./scripts/dev.sh test-cov       # Run tests with coverage

EOF
}

# Main command dispatcher
main() {
    if [ $# -eq 0 ]; then
        cmd_help
        exit 0
    fi

    local command=$1
    shift

    case "$command" in
        lint)           cmd_lint "$@" ;;
        lint-fix)       cmd_lint_fix "$@" ;;
        format)         cmd_format "$@" ;;
        format-check)   cmd_format_check "$@" ;;
        quality)        cmd_quality "$@" ;;
        quality-fix)    cmd_quality_fix "$@" ;;
        typecheck)      cmd_typecheck "$@" ;;
        test)           cmd_test "$@" ;;
        test-fast)      cmd_test_fast "$@" ;;
        test-cov)       cmd_test_cov "$@" ;;
        test-parallel)  cmd_test_parallel "$@" ;;
        check-all)      cmd_check_all "$@" ;;
        dev-check)      cmd_dev_check "$@" ;;
        help|--help|-h) cmd_help ;;
        *)
            error "Unknown command: $command"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
