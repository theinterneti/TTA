#!/bin/bash
# Fix VS Code Pytest Integration
# Resolves test discovery issues after interpreter updates

set -e

WORKSPACE_DIR="/home/thein/recovered-tta-storytelling"
cd "$WORKSPACE_DIR"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "VS Code Pytest Integration Fix"
echo "=========================================="
echo ""

# Step 1: Verify pytest is installed
echo -e "${BLUE}[1/8] Verifying pytest installation...${NC}"
if [ -f ".venv/bin/pytest" ]; then
    PYTEST_VERSION=$(.venv/bin/pytest --version | head -n 1)
    echo "  ✓ $PYTEST_VERSION"
else
    echo "  ✗ pytest not found in .venv"
    echo "  Installing pytest..."
    uv sync --all-extras
fi
echo ""

# Step 2: Test pytest discovery from command line
echo -e "${BLUE}[2/8] Testing pytest discovery from command line...${NC}"
TEST_COUNT=$(.venv/bin/python -m pytest --collect-only tests 2>/dev/null | grep -c "::test_" || echo "0")
if [ "$TEST_COUNT" -gt 0 ]; then
    echo "  ✓ Discovered $TEST_COUNT tests"
else
    echo "  ✗ No tests discovered"
    echo "  This indicates a pytest configuration issue"
fi
echo ""

# Step 3: Clear Python extension cache
echo -e "${BLUE}[3/8] Clearing Python extension cache...${NC}"
CACHE_DIRS=$(find ~/.vscode-server/data/User/workspaceStorage -type d -name "ms-python.python" 2>/dev/null | wc -l)
if [ "$CACHE_DIRS" -gt 0 ]; then
    find ~/.vscode-server/data/User/workspaceStorage -type d -name "ms-python.python" -exec rm -rf {} + 2>/dev/null || true
    echo "  ✓ Cleared $CACHE_DIRS cache directories"
else
    echo "  ℹ No cache directories found"
fi
echo ""

# Step 4: Clear pytest cache
echo -e "${BLUE}[4/8] Clearing pytest cache...${NC}"
if [ -d ".pytest_cache" ]; then
    rm -rf .pytest_cache
    echo "  ✓ Cleared .pytest_cache"
else
    echo "  ℹ No pytest cache found"
fi
echo ""

# Step 5: Verify VS Code settings
echo -e "${BLUE}[5/8] Verifying VS Code settings...${NC}"
if grep -q "python.testing.pytestPath" .vscode/settings.json; then
    echo "  ✓ pytestPath is configured"
else
    echo "  ⚠ pytestPath not configured (should be set)"
fi

if grep -q "python.testing.pytestEnabled.*true" .vscode/settings.json; then
    echo "  ✓ pytest is enabled"
else
    echo "  ✗ pytest is not enabled"
fi

if grep -q "python.defaultInterpreterPath.*\.venv" .vscode/settings.json; then
    echo "  ✓ Interpreter path points to .venv"
else
    echo "  ✗ Interpreter path not configured for .venv"
fi
echo ""

# Step 6: Check for conflicting test frameworks
echo -e "${BLUE}[6/8] Checking for conflicting test frameworks...${NC}"
if grep -q "python.testing.unittestEnabled.*true" .vscode/settings.json; then
    echo "  ⚠ unittest is enabled (should be disabled)"
else
    echo "  ✓ unittest is disabled"
fi

if grep -q "python.testing.nosetestsEnabled.*true" .vscode/settings.json; then
    echo "  ⚠ nosetests is enabled (should be disabled)"
else
    echo "  ✓ nosetests is disabled"
fi
echo ""

# Step 7: Verify pytest.ini configuration
echo -e "${BLUE}[7/8] Verifying pytest.ini configuration...${NC}"
if [ -f "pytest.ini" ]; then
    if grep -q "testpaths.*tests" pytest.ini; then
        echo "  ✓ testpaths configured correctly"
    else
        echo "  ⚠ testpaths not configured"
    fi
else
    echo "  ⚠ pytest.ini not found"
fi
echo ""

# Step 8: Create test discovery verification file
echo -e "${BLUE}[8/8] Creating test discovery verification...${NC}"
cat > .vscode/pytest-discovery-test.sh << 'EOF'
#!/bin/bash
# Quick test discovery verification
cd "$(dirname "$0")/.."
echo "Testing pytest discovery..."
.venv/bin/python -m pytest --collect-only tests 2>&1 | head -20
echo ""
echo "Test count:"
.venv/bin/python -m pytest --collect-only tests 2>/dev/null | grep -c "::test_" || echo "0"
EOF
chmod +x .vscode/pytest-discovery-test.sh
echo "  ✓ Created .vscode/pytest-discovery-test.sh"
echo ""

echo "=========================================="
echo "Fix Complete"
echo "=========================================="
echo ""
echo -e "${YELLOW}IMPORTANT: You MUST restart VS Code for changes to take effect${NC}"
echo ""
echo "Steps to complete the fix:"
echo ""
echo "1. CLOSE ALL VS CODE TERMINALS"
echo "   - Terminal panel → Click trash icon for each terminal"
echo "   - Or: Ctrl+Shift+P → 'Terminal: Kill All Terminals'"
echo ""
echo "2. RESTART VS CODE"
echo "   - Close VS Code completely"
echo "   - Run: pkill -f 'vscode-server'"
echo "   - Wait 5 seconds"
echo "   - Reopen: code $WORKSPACE_DIR"
echo ""
echo "3. SELECT INTERPRETER (if needed)"
echo "   - Ctrl+Shift+P → 'Python: Select Interpreter'"
echo "   - Choose: .venv/bin/python (Python 3.12.3)"
echo ""
echo "4. CONFIGURE TESTS (if needed)"
echo "   - Ctrl+Shift+P → 'Python: Configure Tests'"
echo "   - Select: pytest"
echo "   - Select: tests (directory)"
echo ""
echo "5. REFRESH TESTS"
echo "   - Open Testing panel (flask icon in sidebar)"
echo "   - Click 'Refresh Tests' button"
echo ""
echo "6. VERIFY"
echo "   - You should see all tests in the Testing panel"
echo "   - Run: ./.vscode/pytest-discovery-test.sh"
echo ""
echo "If tests still don't appear:"
echo "  - Check VS Code Output panel → Python Test Log"
echo "  - Look for error messages"
echo "  - Ensure .venv/bin/python is selected as interpreter"
echo ""
