#!/bin/bash
# validate-quality-gates.sh - Validate that code meets quality gate requirements before pushing
# Usage: ./scripts/validate-quality-gates.sh [branch]
# Example: ./scripts/validate-quality-gates.sh staging

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get target branch (default to current branch's upstream)
TARGET_BRANCH=${1:-$(git rev-parse --abbrev-ref HEAD)}

echo -e "${BLUE}=== TTA Quality Gate Validation ===${NC}"
echo -e "${BLUE}Target Branch: ${GREEN}${TARGET_BRANCH}${NC}"
echo ""

# Determine which quality gates to run based on target branch
case $TARGET_BRANCH in
    development|feature/*)
        GATES=("unit")
        echo -e "${YELLOW}Quality Gates for development: Unit tests${NC}"
        ;;
    staging)
        GATES=("unit" "integration" "e2e-core" "code-quality" "security")
        echo -e "${YELLOW}Quality Gates for staging: Unit, Integration, E2E (core), Code Quality, Security${NC}"
        ;;
    main)
        GATES=("unit" "integration" "e2e-full" "code-quality" "security" "comprehensive")
        echo -e "${YELLOW}Quality Gates for main: All tests + Comprehensive battery${NC}"
        ;;
    *)
        echo -e "${YELLOW}Unknown branch, running basic validation (unit tests)${NC}"
        GATES=("unit")
        ;;
esac

echo ""

# Track failures
FAILED_GATES=()

# Function to run a quality gate
run_gate() {
    local gate=$1
    local description=$2
    local command=$3
    
    echo -e "${BLUE}Running: ${description}${NC}"
    
    if eval "$command"; then
        echo -e "${GREEN}✓ ${description} passed${NC}"
        return 0
    else
        echo -e "${RED}✗ ${description} failed${NC}"
        FAILED_GATES+=("$description")
        return 1
    fi
}

# Run quality gates
for gate in "${GATES[@]}"; do
    case $gate in
        unit)
            run_gate "unit" "Unit Tests" "uv run pytest -q --tb=short -m 'not integration and not e2e'" || true
            ;;
        integration)
            run_gate "integration" "Integration Tests" "uv run pytest -q --tb=short -m integration" || true
            ;;
        e2e-core)
            run_gate "e2e-core" "E2E Tests (Core Flows)" "npx playwright test tests/e2e/specs/auth.spec.ts tests/e2e/specs/dashboard.spec.ts --project=chromium" || true
            ;;
        e2e-full)
            run_gate "e2e-full" "E2E Tests (Full Suite)" "npx playwright test --project=chromium" || true
            ;;
        code-quality)
            echo -e "${BLUE}Running: Code Quality Checks${NC}"
            
            # Ruff linting
            if uv run ruff check src/ tests/ --output-format=text; then
                echo -e "${GREEN}✓ Ruff linting passed${NC}"
            else
                echo -e "${RED}✗ Ruff linting failed${NC}"
                FAILED_GATES+=("Ruff linting")
            fi
            
            # Black formatting check
            if uv run black --check src/ tests/; then
                echo -e "${GREEN}✓ Black formatting passed${NC}"
            else
                echo -e "${RED}✗ Black formatting failed${NC}"
                FAILED_GATES+=("Black formatting")
            fi
            
            # isort import sorting check
            if uv run isort --check-only src/ tests/; then
                echo -e "${GREEN}✓ isort import sorting passed${NC}"
            else
                echo -e "${RED}✗ isort import sorting failed${NC}"
                FAILED_GATES+=("isort import sorting")
            fi
            
            # mypy type checking
            if uv run mypy src/; then
                echo -e "${GREEN}✓ mypy type checking passed${NC}"
            else
                echo -e "${RED}✗ mypy type checking failed${NC}"
                FAILED_GATES+=("mypy type checking")
            fi
            ;;
        security)
            echo -e "${BLUE}Running: Security Scans${NC}"
            
            # Bandit security scan
            if uv run bandit -r src/ -f json -o bandit-results.json; then
                echo -e "${GREEN}✓ Bandit security scan passed${NC}"
            else
                echo -e "${RED}✗ Bandit security scan failed${NC}"
                FAILED_GATES+=("Bandit security scan")
            fi
            ;;
        comprehensive)
            run_gate "comprehensive" "Comprehensive Test Battery" "uv run pytest tests/comprehensive/ -q --tb=short" || true
            ;;
    esac
    echo ""
done

# Summary
echo -e "${BLUE}=== Validation Summary ===${NC}"
if [ ${#FAILED_GATES[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All quality gates passed!${NC}"
    echo -e "${GREEN}You can safely push to ${TARGET_BRANCH}${NC}"
    exit 0
else
    echo -e "${RED}✗ ${#FAILED_GATES[@]} quality gate(s) failed:${NC}"
    for gate in "${FAILED_GATES[@]}"; do
        echo -e "${RED}  - ${gate}${NC}"
    done
    echo ""
    echo -e "${YELLOW}Please fix the issues before pushing${NC}"
    exit 1
fi

