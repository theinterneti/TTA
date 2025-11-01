#!/bin/bash
#
# TTA Component Metrics Validation Script
#
# Validates that component metrics in documentation files match
# the automated component-maturity-analysis.json data.
#
# This script is designed to be used as a pre-commit hook to prevent
# documentation from becoming stale or inconsistent.
#
# Usage:
#   ./scripts/validate-component-metrics.sh
#
# Exit codes:
#   0 - All metrics are consistent
#   1 - Inconsistencies found or validation failed
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
METRICS_FILE="component-maturity-analysis.json"
DOCS_DIR="docs/component-promotion"

echo "========================================================================"
echo "TTA Component Metrics Validation"
echo "========================================================================"
echo ""

# Check if metrics file exists
if [ ! -f "$METRICS_FILE" ]; then
    echo -e "${YELLOW}⚠️  WARNING: $METRICS_FILE not found${NC}"
    echo "Skipping validation (metrics file may not be generated yet)"
    echo ""
    echo "To generate metrics file, run:"
    echo "  uv run python scripts/analyze-component-maturity.py"
    exit 0
fi

echo "✅ Found metrics file: $METRICS_FILE"

# Check if documentation directory exists
if [ ! -d "$DOCS_DIR" ]; then
    echo -e "${RED}❌ ERROR: Documentation directory not found: $DOCS_DIR${NC}"
    exit 1
fi

echo "✅ Found documentation directory: $DOCS_DIR"
echo ""

# Run Python validation script
echo "Running validation..."
echo ""

if python3 scripts/sync-component-docs.py --dry-run; then
    echo ""
    echo "========================================================================"
    echo -e "${GREEN}✅ VALIDATION PASSED${NC}"
    echo "========================================================================"
    echo ""
    echo "All component metrics in documentation are consistent with"
    echo "automated reporting (component-maturity-analysis.json)."
    echo ""
    exit 0
else
    echo ""
    echo "========================================================================"
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo "========================================================================"
    echo ""
    echo "Inconsistencies found between documentation and automated metrics."
    echo ""
    echo "To fix:"
    echo "  1. Review the inconsistencies listed above"
    echo "  2. Update documentation files to match component-maturity-analysis.json"
    echo "  3. Commit the corrected documentation"
    echo ""
    echo "To see current metrics:"
    echo "  python3 scripts/sync-component-docs.py --report"
    echo ""
    echo "To bypass this check (NOT RECOMMENDED):"
    echo "  git commit --no-verify"
    echo ""
    exit 1
fi
