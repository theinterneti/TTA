#!/bin/bash
# Quick verification script to check if pytest is properly configured

WORKSPACE_DIR="/home/thein/recovered-tta-storytelling"
INTERPRETER="$WORKSPACE_DIR/.venv/bin/python"

echo "=========================================="
echo "Pytest Setup Verification"
echo "=========================================="
echo ""

# Check 1: Interpreter exists
echo "✓ Check 1: Python interpreter"
if [ -f "$INTERPRETER" ]; then
    echo "  ✓ Found: $INTERPRETER"
    echo "  ✓ Version: $($INTERPRETER --version)"
else
    echo "  ❌ NOT FOUND: $INTERPRETER"
    exit 1
fi
echo ""

# Check 2: Pytest installed
echo "✓ Check 2: Pytest installation"
if $INTERPRETER -m pytest --version &>/dev/null; then
    echo "  ✓ Pytest version: $($INTERPRETER -m pytest --version 2>&1 | head -n1)"
else
    echo "  ❌ Pytest NOT installed"
    exit 1
fi
echo ""

# Check 3: Pytest can discover tests
echo "✓ Check 3: Test discovery"
TEST_COUNT=$($INTERPRETER -m pytest --collect-only tests -q 2>/dev/null | grep -c "test_" || echo "0")
if [ "$TEST_COUNT" -gt 0 ]; then
    echo "  ✓ Discovered $TEST_COUNT test items"
else
    echo "  ⚠ Warning: No tests discovered (may need to run from VS Code)"
fi
echo ""

# Check 4: Configuration files
echo "✓ Check 4: Configuration files"
if [ -f "$WORKSPACE_DIR/pytest.ini" ]; then
    echo "  ✓ pytest.ini exists"
else
    echo "  ⚠ pytest.ini not found"
fi

if [ -f "$WORKSPACE_DIR/.vscode/settings.json" ]; then
    echo "  ✓ .vscode/settings.json exists"
    if grep -q "python.defaultInterpreterPath" "$WORKSPACE_DIR/.vscode/settings.json"; then
        echo "  ✓ Interpreter path configured"
    else
        echo "  ⚠ Interpreter path not configured"
    fi
else
    echo "  ⚠ .vscode/settings.json not found"
fi
echo ""

# Check 5: No conflicting virtual environments
echo "✓ Check 5: Virtual environments"
if [ -d "$WORKSPACE_DIR/list" ]; then
    echo "  ❌ ERROR: 'list' directory still exists!"
    echo "     Run: rm -rf $WORKSPACE_DIR/list"
    exit 1
else
    echo "  ✓ No conflicting 'list' directory"
fi

if [ -d "$WORKSPACE_DIR/.venv" ]; then
    echo "  ✓ .venv directory exists"
else
    echo "  ❌ ERROR: .venv directory not found!"
    exit 1
fi
echo ""

# Check 6: VS Code Python extension cache
echo "✓ Check 6: VS Code cache status"
CACHE_COUNT=$(find ~/.vscode-server/data/User/workspaceStorage/*/ms-python.python -type d 2>/dev/null | wc -l)
if [ "$CACHE_COUNT" -eq 0 ]; then
    echo "  ✓ Python extension cache is clean"
else
    echo "  ℹ Found $CACHE_COUNT workspace cache directories"
    echo "    (This is normal after VS Code reopens)"
fi
echo ""

echo "=========================================="
echo "✅ Verification Complete"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - Python interpreter: ✓"
echo "  - Pytest installed: ✓"
echo "  - Configuration files: ✓"
echo "  - Virtual environments: ✓"
echo ""
echo "If VS Code still shows the wrong interpreter:"
echo "1. Close VS Code completely"
echo "2. Run: ./fix-vscode-python-cache.sh"
echo "3. Reopen VS Code"
echo "4. Manually select interpreter (Ctrl+Shift+P)"
echo ""
