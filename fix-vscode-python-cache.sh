#!/bin/bash
# Comprehensive VS Code Python Extension Cache Cleanup Script
# This script clears all cached Python interpreter selections

set -e

WORKSPACE_DIR="/home/thein/recovered-tta-storytelling"
VSCODE_SERVER_DIR="$HOME/.vscode-server"
CORRECT_INTERPRETER="$WORKSPACE_DIR/.venv/bin/python"

echo "=========================================="
echo "VS Code Python Cache Cleanup Script"
echo "=========================================="
echo ""

# Verify correct interpreter exists
if [ ! -f "$CORRECT_INTERPRETER" ]; then
    echo "❌ ERROR: Correct interpreter not found at: $CORRECT_INTERPRETER"
    exit 1
fi

echo "✓ Correct interpreter found: $CORRECT_INTERPRETER"
echo "  Python version: $($CORRECT_INTERPRETER --version)"
echo ""

# Step 1: Clear Python extension workspace storage
echo "Step 1: Clearing Python extension workspace storage..."
CLEARED_COUNT=0
for ws_dir in "$VSCODE_SERVER_DIR/data/User/workspaceStorage"/*/ms-python.python; do
    if [ -d "$ws_dir" ]; then
        echo "  Removing: $ws_dir"
        rm -rf "$ws_dir"
        CLEARED_COUNT=$((CLEARED_COUNT + 1))
    fi
done
echo "  ✓ Cleared $CLEARED_COUNT workspace storage directories"
echo ""

# Step 2: Clear Python locator cache
echo "Step 2: Clearing Python locator cache..."
LOCATOR_DIR="$VSCODE_SERVER_DIR/data/User/globalStorage/ms-python.python/pythonLocator"
if [ -d "$LOCATOR_DIR" ]; then
    echo "  Removing: $LOCATOR_DIR"
    rm -rf "$LOCATOR_DIR"
    echo "  ✓ Cleared Python locator cache"
else
    echo "  ℹ Python locator cache not found (already clean)"
fi
echo ""

# Step 3: Clear Python extension global state
echo "Step 3: Clearing Python extension global state..."
GLOBAL_STATE_DIR="$VSCODE_SERVER_DIR/data/User/globalStorage/ms-python.python"
if [ -d "$GLOBAL_STATE_DIR" ]; then
    # Keep the extension but clear cache files
    find "$GLOBAL_STATE_DIR" -type f -name "*.json" -delete 2>/dev/null || true
    find "$GLOBAL_STATE_DIR" -type f -name "*.cache" -delete 2>/dev/null || true
    echo "  ✓ Cleared Python extension cache files"
else
    echo "  ℹ Python extension global state not found"
fi
echo ""

# Step 4: Clear pytest cache
echo "Step 4: Clearing pytest cache in workspace..."
cd "$WORKSPACE_DIR"
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "  ✓ Cleared pytest and Python caches"
echo ""

# Step 5: Verify .vscode/settings.json
echo "Step 5: Verifying .vscode/settings.json..."
if grep -q "python.defaultInterpreterPath" "$WORKSPACE_DIR/.vscode/settings.json"; then
    echo "  ✓ Interpreter path configured in settings.json"
else
    echo "  ⚠ Warning: Interpreter path not found in settings.json"
fi
echo ""

# Step 6: Create interpreter verification file
echo "Step 6: Creating interpreter verification file..."
cat > "$WORKSPACE_DIR/.vscode/python-interpreter.txt" << EOF
Correct Python Interpreter Path:
$CORRECT_INTERPRETER

To manually select in VS Code:
1. Press Ctrl+Shift+P
2. Type: Python: Select Interpreter
3. Choose: .venv/bin/python (Python 3.12.3)

Or enter path manually:
$CORRECT_INTERPRETER
EOF
echo "  ✓ Created .vscode/python-interpreter.txt"
echo ""

echo "=========================================="
echo "✅ Cache cleanup complete!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo "1. Close VS Code completely (all windows)"
echo "2. Reopen VS Code and this workspace"
echo "3. Press Ctrl+Shift+P"
echo "4. Type: Python: Select Interpreter"
echo "5. Select: .venv/bin/python"
echo "6. Press Ctrl+Shift+P"
echo "7. Type: Python: Clear Cache and Reload Window"
echo "8. Test pytest discovery in the Testing panel"
echo ""
echo "If issues persist, run: ./force-vscode-interpreter-reset.sh"
echo ""
