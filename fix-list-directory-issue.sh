#!/bin/bash
# Fix the persistent `list` directory recreation issue
# Root cause: VIRTUAL_ENV environment variable pointing to `list`

set -e

WORKSPACE_DIR="/home/thein/recovered-tta-storytelling"

echo "=========================================="
echo "Fix: Stop 'list' Directory Recreation"
echo "=========================================="
echo ""

# Step 1: Show current environment
echo "Step 1: Checking current environment variables..."
if env | grep -q "VIRTUAL_ENV.*list"; then
    echo "  ❌ FOUND: VIRTUAL_ENV is set to 'list'"
    env | grep VIRTUAL_ENV
    echo ""
    echo "  This is the ROOT CAUSE of the issue!"
else
    echo "  ✓ VIRTUAL_ENV is not set to 'list'"
fi
echo ""

# Step 2: Deactivate and unset
echo "Step 2: Deactivating virtual environment and unsetting variables..."
deactivate 2>/dev/null || true
unset VIRTUAL_ENV 2>/dev/null || true
unset VIRTUAL_ENV_PROMPT 2>/dev/null || true
echo "  ✓ Deactivated and unset environment variables"
echo ""

# Step 3: Remove list directory
echo "Step 3: Removing 'list' directory..."
cd "$WORKSPACE_DIR"
if [ -d "list" ]; then
    rm -rf list
    echo "  ✓ Removed 'list' directory"
else
    echo "  ℹ 'list' directory not found (already removed)"
fi
echo ""

# Step 4: Verify .venv exists
echo "Step 4: Verifying .venv exists..."
if [ -d ".venv" ]; then
    echo "  ✓ .venv directory exists"
    echo "  ✓ Python: $(.venv/bin/python --version)"
else
    echo "  ⚠ .venv directory not found"
    echo "  Creating .venv..."
    uv venv
    echo "  ✓ Created .venv"
fi
echo ""

# Step 5: Configure UV to use .venv
echo "Step 5: Configuring UV to use .venv..."
SHELL_RC=""
if [ -f ~/.bashrc ]; then
    SHELL_RC=~/.bashrc
elif [ -f ~/.zshrc ]; then
    SHELL_RC=~/.zshrc
fi

if [ -n "$SHELL_RC" ]; then
    if grep -q "UV_PROJECT_ENVIRONMENT" "$SHELL_RC"; then
        echo "  ℹ UV_PROJECT_ENVIRONMENT already configured in $SHELL_RC"
    else
        echo "" >> "$SHELL_RC"
        echo "# UV Configuration - Force use of .venv" >> "$SHELL_RC"
        echo "export UV_PROJECT_ENVIRONMENT=\".venv\"" >> "$SHELL_RC"
        echo "  ✓ Added UV_PROJECT_ENVIRONMENT to $SHELL_RC"
    fi
else
    echo "  ⚠ Could not find shell RC file"
fi
echo ""

# Step 6: Test that list doesn't get recreated
echo "Step 6: Testing that 'list' doesn't get recreated..."
rm -rf list 2>/dev/null || true
echo "  Running: uv sync (this should NOT create 'list')..."
uv sync --quiet 2>&1 | head -5 || true
sleep 2
if [ -d "list" ]; then
    echo "  ❌ FAILED: 'list' directory was recreated!"
    echo "  The VIRTUAL_ENV variable is still set in your environment."
    echo "  You MUST close all terminals and restart VS Code."
else
    echo "  ✓ SUCCESS: 'list' directory was NOT recreated"
fi
echo ""

echo "=========================================="
echo "Fix Script Complete"
echo "=========================================="
echo ""
echo "IMPORTANT NEXT STEPS:"
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
echo "3. VERIFY IN NEW TERMINAL"
echo "   - Open new terminal in VS Code"
echo "   - Run: env | grep VIRTUAL_ENV"
echo "   - Should be EMPTY or show .venv (not list)"
echo ""
echo "4. TEST THE FIX"
echo "   - Run: rm -rf list && uv sync"
echo "   - Run: ls -la | grep list"
echo "   - Should NOT show 'list' directory"
echo ""
echo "If 'list' still gets created after restarting VS Code,"
echo "see: FIX_LIST_DIRECTORY_RECREATION.md for advanced troubleshooting"
echo ""
