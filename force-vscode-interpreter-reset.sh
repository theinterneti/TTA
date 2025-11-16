#!/bin/bash
# Force VS Code to completely reset Python interpreter selection
# Use this if the standard cleanup script doesn't work

set -e

WORKSPACE_DIR="/home/thein/recovered-tta-storytelling"
VSCODE_SERVER_DIR="$HOME/.vscode-server"
CORRECT_INTERPRETER="$WORKSPACE_DIR/.venv/bin/python"

echo "=========================================="
echo "FORCE VS Code Python Interpreter Reset"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will clear ALL VS Code workspace storage"
echo "    for this workspace. You may lose some workspace-specific"
echo "    settings and extension data."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Starting aggressive cleanup..."
echo ""

# Step 1: Find and remove ALL workspace storage for this workspace
echo "Step 1: Removing ALL workspace storage..."
WORKSPACE_HASH=$(echo -n "$WORKSPACE_DIR" | md5sum | cut -d' ' -f1)
echo "  Workspace hash: $WORKSPACE_HASH"

# Remove by hash if found
for ws_dir in "$VSCODE_SERVER_DIR/data/User/workspaceStorage"/*; do
    if [ -d "$ws_dir" ]; then
        # Check if this workspace storage contains references to our workspace
        if grep -r "recovered-tta-storytelling" "$ws_dir" 2>/dev/null | grep -q .; then
            echo "  Removing workspace storage: $(basename $ws_dir)"
            rm -rf "$ws_dir"
        fi
    fi
done
echo "  ✓ Workspace storage cleared"
echo ""

# Step 2: Clear ALL Python extension data
echo "Step 2: Clearing ALL Python extension data..."
PYTHON_EXT_DIR="$VSCODE_SERVER_DIR/data/User/globalStorage/ms-python.python"
if [ -d "$PYTHON_EXT_DIR" ]; then
    echo "  Removing: $PYTHON_EXT_DIR"
    rm -rf "$PYTHON_EXT_DIR"
    echo "  ✓ Python extension data cleared"
else
    echo "  ℹ Python extension data not found"
fi
echo ""

# Step 3: Clear Python extension cache in extensions directory
echo "Step 3: Clearing Python extension cache..."
PYTHON_EXT_CACHE="$VSCODE_SERVER_DIR/extensions/ms-python.python-*/pythonFiles/__pycache__"
rm -rf $PYTHON_EXT_CACHE 2>/dev/null || true
echo "  ✓ Extension cache cleared"
echo ""

# Step 4: Create a .python-version file to help VS Code
echo "Step 4: Creating .python-version file..."
echo "3.12.3" > "$WORKSPACE_DIR/.python-version"
echo "  ✓ Created .python-version"
echo ""

# Step 5: Create explicit interpreter configuration
echo "Step 5: Creating explicit interpreter configuration..."
mkdir -p "$WORKSPACE_DIR/.vscode"
cat > "$WORKSPACE_DIR/.vscode/python.json" << EOF
{
  "interpreterPath": "$CORRECT_INTERPRETER",
  "version": "3.12.3",
  "pytest": {
    "enabled": true,
    "path": "$WORKSPACE_DIR/.venv/bin/pytest"
  }
}
EOF
echo "  ✓ Created .vscode/python.json"
echo ""

# Step 6: Verify interpreter
echo "Step 6: Verifying interpreter..."
if [ -f "$CORRECT_INTERPRETER" ]; then
    echo "  ✓ Interpreter exists: $CORRECT_INTERPRETER"
    echo "  ✓ Python version: $($CORRECT_INTERPRETER --version)"
    echo "  ✓ Pytest version: $($CORRECT_INTERPRETER -m pytest --version 2>&1 | head -n1)"
else
    echo "  ❌ ERROR: Interpreter not found!"
    exit 1
fi
echo ""

# Step 7: Create VS Code tasks for interpreter selection
echo "Step 7: Creating VS Code tasks..."
mkdir -p "$WORKSPACE_DIR/.vscode"
cat > "$WORKSPACE_DIR/.vscode/tasks.json" << 'EOF'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Select Python Interpreter",
      "type": "shell",
      "command": "echo",
      "args": [
        "Run: Ctrl+Shift+P -> 'Python: Select Interpreter' -> Choose .venv/bin/python"
      ],
      "problemMatcher": []
    },
    {
      "label": "Verify Python Environment",
      "type": "shell",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": [
        "--version"
      ],
      "problemMatcher": []
    },
    {
      "label": "Test Pytest Discovery",
      "type": "shell",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": [
        "-m",
        "pytest",
        "--collect-only",
        "tests",
        "-q"
      ],
      "problemMatcher": []
    }
  ]
}
EOF
echo "  ✓ Created .vscode/tasks.json"
echo ""

echo "=========================================="
echo "✅ FORCE RESET COMPLETE!"
echo "=========================================="
echo ""
echo "CRITICAL NEXT STEPS:"
echo ""
echo "1. CLOSE VS CODE COMPLETELY"
echo "   - Close all VS Code windows"
echo "   - Kill any remaining VS Code processes:"
echo "     pkill -f 'vscode-server'"
echo ""
echo "2. WAIT 10 SECONDS"
echo ""
echo "3. REOPEN VS CODE"
echo "   - Open this workspace: $WORKSPACE_DIR"
echo ""
echo "4. MANUALLY SELECT INTERPRETER"
echo "   - Press: Ctrl+Shift+P"
echo "   - Type: Python: Select Interpreter"
echo "   - Choose: .venv/bin/python (Python 3.12.3)"
echo ""
echo "5. CLEAR CACHE AND RELOAD"
echo "   - Press: Ctrl+Shift+P"
echo "   - Type: Python: Clear Cache and Reload Window"
echo ""
echo "6. VERIFY PYTEST"
echo "   - Open Testing panel (flask icon)"
echo "   - Click 'Refresh Tests'"
echo "   - Should see 952 tests"
echo ""
echo "If this STILL doesn't work, there may be a VS Code bug."
echo "Try: code --disable-extensions (to test without extensions)"
echo ""
