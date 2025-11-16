#!/bin/bash
# Comprehensive UV Configuration Verification Script
# Verifies that UV is properly configured for WSL2 + VS Code environment

set -e

WORKSPACE_DIR="/home/thein/recovered-tta-storytelling"
cd "$WORKSPACE_DIR"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

echo "=========================================="
echo "UV Configuration Verification"
echo "=========================================="
echo ""

# Function to print test result
print_result() {
    local status=$1
    local message=$2
    local details=$3

    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC}: $message"
        ((PASS_COUNT++))
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}✗ FAIL${NC}: $message"
        ((FAIL_COUNT++))
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠ WARN${NC}: $message"
        ((WARN_COUNT++))
    fi

    if [ -n "$details" ]; then
        echo "  Details: $details"
    fi
    echo ""
}

# Test 1: UV Installation
echo -e "${BLUE}[1/15] Checking UV Installation...${NC}"
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    print_result "PASS" "UV is installed" "$UV_VERSION"
else
    print_result "FAIL" "UV is not installed" "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# Test 2: UV Configuration Files
echo -e "${BLUE}[2/15] Checking UV Configuration Files...${NC}"
if [ -f "uv.toml" ]; then
    print_result "PASS" "uv.toml exists"
else
    print_result "FAIL" "uv.toml not found" "This file should exist in project root"
fi

if grep -q "\[tool.uv\]" pyproject.toml; then
    print_result "PASS" "pyproject.toml has [tool.uv] section"
else
    print_result "FAIL" "pyproject.toml missing [tool.uv] section"
fi

# Test 3: Virtual Environment
echo -e "${BLUE}[3/15] Checking Virtual Environment...${NC}"
if [ -d ".venv" ]; then
    print_result "PASS" ".venv directory exists"

    if [ -f ".venv/bin/python" ]; then
        PYTHON_VERSION=$(.venv/bin/python --version)
        print_result "PASS" "Python interpreter exists in .venv" "$PYTHON_VERSION"
    else
        print_result "FAIL" "Python interpreter not found in .venv"
    fi
else
    print_result "FAIL" ".venv directory not found" "Run: uv venv"
fi

# Test 4: Unwanted 'list' Directory
echo -e "${BLUE}[4/15] Checking for Unwanted 'list' Directory...${NC}"
if [ -d "list" ]; then
    print_result "FAIL" "list directory exists (should not exist)" "Run: rm -rf list"
else
    print_result "PASS" "No list directory found"
fi

# Test 5: Environment Variables
echo -e "${BLUE}[5/15] Checking Environment Variables...${NC}"
if env | grep -q "VIRTUAL_ENV.*list"; then
    VENV_VALUE=$(env | grep VIRTUAL_ENV)
    print_result "FAIL" "VIRTUAL_ENV points to 'list'" "$VENV_VALUE - Run: unset VIRTUAL_ENV"
elif env | grep -q "VIRTUAL_ENV.*\.venv"; then
    VENV_VALUE=$(env | grep VIRTUAL_ENV)
    print_result "PASS" "VIRTUAL_ENV points to .venv" "$VENV_VALUE"
elif env | grep -q "VIRTUAL_ENV"; then
    VENV_VALUE=$(env | grep VIRTUAL_ENV)
    print_result "WARN" "VIRTUAL_ENV is set but not to .venv" "$VENV_VALUE"
else
    print_result "PASS" "VIRTUAL_ENV not set (UV will use default .venv)"
fi

if env | grep -q "UV_PROJECT_ENVIRONMENT"; then
    UV_ENV=$(env | grep UV_PROJECT_ENVIRONMENT)
    print_result "PASS" "UV_PROJECT_ENVIRONMENT is set" "$UV_ENV"
else
    print_result "WARN" "UV_PROJECT_ENVIRONMENT not set" "Consider adding to ~/.bashrc: export UV_PROJECT_ENVIRONMENT=\".venv\""
fi

# Test 6: UV Cache
echo -e "${BLUE}[6/15] Checking UV Cache Configuration...${NC}"
if [ -d ".uv_cache" ]; then
    CACHE_SIZE=$(du -sh .uv_cache 2>/dev/null | cut -f1)
    print_result "PASS" "UV cache directory exists" "Size: $CACHE_SIZE"
else
    print_result "PASS" "UV cache not yet created (will be created on first sync)"
fi

if grep -q ".uv_cache" .gitignore; then
    print_result "PASS" ".uv_cache is in .gitignore"
else
    print_result "FAIL" ".uv_cache not in .gitignore" "Add to .gitignore"
fi

# Test 7: VS Code Configuration
echo -e "${BLUE}[7/15] Checking VS Code Configuration...${NC}"
if [ -f ".vscode/settings.json" ]; then
    if grep -q "\.venv/bin/python" .vscode/settings.json; then
        print_result "PASS" "VS Code configured to use .venv"
    else
        print_result "FAIL" "VS Code not configured for .venv"
    fi
else
    print_result "WARN" ".vscode/settings.json not found"
fi

# Test 8: UV Lock File
echo -e "${BLUE}[8/15] Checking UV Lock File...${NC}"
if [ -f "uv.lock" ]; then
    LOCK_VERSION=$(head -n 1 uv.lock | grep -oP 'version = \K\d+')
    print_result "PASS" "uv.lock exists" "Version: $LOCK_VERSION"
else
    print_result "FAIL" "uv.lock not found" "Run: uv lock"
fi

# Test 9: Python Version
echo -e "${BLUE}[9/15] Checking Python Version...${NC}"
if [ -f ".venv/bin/python" ]; then
    PYTHON_VERSION=$(.venv/bin/python --version | grep -oP '\d+\.\d+\.\d+')
    REQUIRED_VERSION="3.10"

    if [[ "$PYTHON_VERSION" > "$REQUIRED_VERSION" ]] || [[ "$PYTHON_VERSION" == "$REQUIRED_VERSION"* ]]; then
        print_result "PASS" "Python version meets requirements" "Found: $PYTHON_VERSION, Required: >=$REQUIRED_VERSION"
    else
        print_result "FAIL" "Python version too old" "Found: $PYTHON_VERSION, Required: >=$REQUIRED_VERSION"
    fi
fi

# Test 10: Pytest Installation
echo -e "${BLUE}[10/15] Checking Pytest Installation...${NC}"
if [ -f ".venv/bin/pytest" ]; then
    PYTEST_VERSION=$(.venv/bin/pytest --version | head -n 1)
    print_result "PASS" "Pytest is installed" "$PYTEST_VERSION"
else
    print_result "FAIL" "Pytest not found in .venv" "Run: uv sync --all-extras"
fi

# Test 11: UV Managed Setting
echo -e "${BLUE}[11/15] Checking UV Managed Setting...${NC}"
if grep -q "managed = true" pyproject.toml; then
    print_result "PASS" "UV managed mode is enabled"
else
    print_result "WARN" "UV managed mode not explicitly set" "Add 'managed = true' to [tool.uv]"
fi

# Test 12: Default Groups
echo -e "${BLUE}[12/15] Checking Default Groups...${NC}"
if grep -q "default-groups.*dev" pyproject.toml; then
    print_result "PASS" "Dev dependencies included in default groups"
else
    print_result "WARN" "Dev dependencies not in default groups" "Add 'default-groups = [\"dev\"]' to [tool.uv]"
fi

# Test 13: Test UV Sync (Dry Run)
echo -e "${BLUE}[13/15] Testing UV Sync (Dry Run)...${NC}"
if uv sync --dry-run &> /dev/null; then
    print_result "PASS" "UV sync dry run successful"
else
    print_result "FAIL" "UV sync dry run failed" "Check uv.lock and pyproject.toml"
fi

# Test 14: Check for List Recreation
echo -e "${BLUE}[14/15] Testing List Directory Recreation...${NC}"
rm -rf list 2>/dev/null || true
uv sync --quiet &> /dev/null || true
sleep 1
if [ -d "list" ]; then
    print_result "FAIL" "list directory was recreated!" "VIRTUAL_ENV is still set to 'list' - restart VS Code"
else
    print_result "PASS" "list directory not recreated"
fi

# Test 15: VS Code Tasks
echo -e "${BLUE}[15/15] Checking VS Code Tasks...${NC}"
if [ -f ".vscode/tasks.json" ]; then
    if grep -q "UV: Verify Environment" .vscode/tasks.json; then
        print_result "PASS" "VS Code tasks configured for UV"
    else
        print_result "WARN" "VS Code tasks.json exists but may not have UV tasks"
    fi
else
    print_result "WARN" ".vscode/tasks.json not found" "Consider creating UV tasks"
fi

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${YELLOW}Warnings: $WARN_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Your UV configuration is properly set up for WSL2 + VS Code."
    exit 0
else
    echo -e "${RED}✗ Some checks failed.${NC}"
    echo ""
    echo "Please address the failed checks above."
    echo "See UV_CONFIGURATION_GUIDE.md for detailed instructions."
    exit 1
fi
