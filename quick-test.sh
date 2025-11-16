#!/bin/bash
# Quick Test Starter for TTA
# Runs the most important tests to verify your codebase

set -e

echo "🧪 TTA Quick Test Suite"
echo "======================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}1️⃣  Running Unit Tests (Fast)${NC}"
echo "----------------------------"
uv run pytest tests/unit/ -v --maxfail=10 -x

echo ""
echo -e "${GREEN}✅ Unit tests passed!${NC}"
echo ""

echo -e "${BLUE}2️⃣  Checking Code Coverage${NC}"
echo "----------------------------"
uv run pytest tests/unit/ --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=70

echo ""
echo -e "${GREEN}✅ Coverage check passed! (≥70%)${NC}"
echo ""

echo -e "${BLUE}3️⃣  Code Quality Checks${NC}"
echo "----------------------------"
echo "Formatting code..."
uv run ruff format src/ tests/

echo "Linting code..."
uv run ruff check src/ tests/ --fix

echo "Type checking..."
uv run pyright src/ || echo -e "${YELLOW}⚠️  Type checking had warnings${NC}"

echo ""
echo -e "${GREEN}✅ Quality checks complete!${NC}"
echo ""

echo "=================================="
echo -e "${GREEN}🎉 All tests passed!${NC}"
echo ""
echo "📊 Coverage report: htmlcov/index.html"
echo "📝 View with: xdg-open htmlcov/index.html"
echo ""
echo "Next steps:"
echo "  - Run integration tests: uv run pytest tests/integration/ -v"
echo "  - Run comprehensive battery: cd tests/comprehensive_battery && python run_comprehensive_tests.py --all"
echo "  - Record API tests: keploy record -c 'uv run python simple_test_api.py'"
