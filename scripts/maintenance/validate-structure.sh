#!/bin/bash
# TTA Project Structure Validation Script
# Purpose: Validate reorganization was successful and no broken references exist
# Date: 2025-10-04
# Usage: ./scripts/maintenance/validate-structure.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ERRORS=0
WARNINGS=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((ERRORS++))
}

cd "$PROJECT_ROOT"

log_info "=== TTA Project Structure Validation ==="
echo ""

# Check directory structure
log_info "Checking directory structure..."

required_dirs=(
    "archive"
    "archive/phases"
    "archive/tasks"
    "archive/fixes"
    "archive/validation"
    "archive/ci-cd"
    "archive/integration"
    "docs/setup"
    "docs/deployment"
    "docs/testing"
    "docs/development"
    "docs/operations"
    "docs/operations/security"
    "docs/operations/monitoring"
    "docs/integration"
    "docs/environments"
    "artifacts"
    "artifacts/test-scripts"
    "artifacts/screenshots"
    "artifacts/test-results"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        log_success "Directory exists: $dir"
    else
        log_error "Missing directory: $dir"
    fi
done

echo ""

# Check for remaining files in root
log_info "Checking for scattered files in root..."

md_count=$(find . -maxdepth 1 -name "*.md" -type f ! -name "README.md" ! -name "PROJECT_REORGANIZATION_PLAN.md" | wc -l)
test_count=$(find . -maxdepth 1 -name "test*" -type f | wc -l)
png_count=$(find . -maxdepth 1 -name "*.png" -type f | wc -l)

if [ "$md_count" -gt 0 ]; then
    log_warning "Found $md_count markdown files still in root (excluding README.md)"
    find . -maxdepth 1 -name "*.md" -type f ! -name "README.md" ! -name "PROJECT_REORGANIZATION_PLAN.md" | head -5
else
    log_success "No scattered markdown files in root"
fi

if [ "$test_count" -gt 0 ]; then
    log_warning "Found $test_count test files still in root"
    find . -maxdepth 1 -name "test*" -type f | head -5
else
    log_success "No test files in root"
fi

if [ "$png_count" -gt 0 ]; then
    log_warning "Found $png_count PNG files still in root"
    find . -maxdepth 1 -name "*.png" -type f | head -5
else
    log_success "No PNG files in root"
fi

echo ""

# Check docker-compose files
log_info "Checking docker-compose files..."

current_compose=(
    "docker-compose.yml"
    "docker-compose.dev.yml"
    "docker-compose.staging-homelab.yml"
    "docker-compose.test.yml"
)

for file in "${current_compose[@]}"; do
    if [ -f "$file" ]; then
        log_success "Current compose file exists: $file"
    else
        log_error "Missing compose file: $file"
    fi
done

obsolete_compose=(
    "docker-compose.homelab.yml"
    "docker-compose.staging.yml"
    "docker-compose.hotreload.yml"
    "docker-compose.phase2a.yml"
)

for file in "${obsolete_compose[@]}"; do
    if [ -f "$file" ]; then
        log_warning "Obsolete compose file still in root: $file"
    else
        log_success "Obsolete compose file removed: $file"
    fi
done

echo ""

# Check obsolete subdirectories
log_info "Checking obsolete subdirectories..."

obsolete_dirs=("tta.dev" "tta.prototype" "tta.prod")

for dir in "${obsolete_dirs[@]}"; do
    if [ -d "$dir" ]; then
        log_warning "Obsolete directory still exists: $dir"
    else
        log_success "Obsolete directory removed: $dir"
    fi
done

echo ""

# Check for broken references (sample check)
log_info "Checking for potential broken references..."

# Check if any files reference moved documentation
if grep -r "PHASE1A_COMPLETE\.md" --include="*.py" --include="*.md" --include="*.sh" . 2>/dev/null | grep -v "archive/" | grep -v ".git/" | head -1 > /dev/null; then
    log_warning "Found references to moved files (may need updating)"
else
    log_success "No obvious broken references found"
fi

echo ""

# Summary
log_info "=== Validation Summary ==="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    log_success "✓ All checks passed! Project structure is valid."
    exit 0
elif [ $ERRORS -eq 0 ]; then
    log_warning "⚠ Validation complete with $WARNINGS warnings"
    log_info "Review warnings above and address if needed"
    exit 0
else
    log_error "✗ Validation failed with $ERRORS errors and $WARNINGS warnings"
    log_info "Fix errors above before proceeding"
    exit 1
fi

