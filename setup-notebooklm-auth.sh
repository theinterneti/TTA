#!/bin/bash
# NotebookLM MCP Manual Authentication Setup

set -e

echo "🔐 NotebookLM MCP - Manual Authentication Setup"
echo "=============================================="
echo ""

NOTEBOOK_ID="1dc787c2-8387-4223-b2ac-9ea04d1c37d1"
PROFILE_DIR="$(pwd)/chrome_profile_notebooklm"
NOTEBOOK_URL="https://notebooklm.google.com/notebook/$NOTEBOOK_ID"

echo "📋 Configuration:"
echo "   Notebook ID: $NOTEBOOK_ID"
echo "   Profile Directory: $PROFILE_DIR"
echo "   Notebook URL: $NOTEBOOK_URL"
echo ""

# Check if Chrome is available
if command -v google-chrome &> /dev/null; then
    CHROME_CMD="google-chrome"
elif command -v chromium &> /dev/null; then
    CHROME_CMD="chromium"
elif command -v chromium-browser &> /dev/null; then
    CHROME_CMD="chromium-browser"
else
    echo "❌ Error: Chrome/Chromium not found!"
    echo "   Please install Google Chrome or Chromium"
    exit 1
fi

echo "✅ Found browser: $CHROME_CMD"
echo ""

# Create profile directory if it doesn't exist
mkdir -p "$PROFILE_DIR"

echo "🌐 Opening Chrome with persistent profile..."
echo ""
echo "📝 Instructions:"
echo "   1. A Chrome window will open"
echo "   2. Log in to your Google account if prompted"
echo "   3. Navigate to your NotebookLM notebook"
echo "   4. Once logged in and the notebook loads, close the browser"
echo "   5. Your authentication will be saved in the profile"
echo ""
echo "Press Enter to open Chrome..."
read

# Open Chrome with the profile
$CHROME_CMD \
    --user-data-dir="$PROFILE_DIR" \
    --no-first-run \
    --no-default-browser-check \
    "$NOTEBOOK_URL" &

CHROME_PID=$!

echo "✅ Chrome opened (PID: $CHROME_PID)"
echo ""
echo "⏳ Waiting for you to complete authentication..."
echo "   (Chrome will remain open until you close it)"
echo ""

# Wait for Chrome to close
wait $CHROME_PID

echo ""
echo "✅ Authentication complete!"
echo ""
echo "🧪 Testing the MCP server..."
echo ""

# Test the server
if uv run notebooklm-mcp --config notebooklm-config.json test --notebook "$NOTEBOOK_ID"; then
    echo ""
    echo "🎉 Success! NotebookLM MCP is ready to use!"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Start the server:"
    echo "      uv run notebooklm-mcp --config notebooklm-config.json server"
    echo ""
    echo "   2. Or test with chat:"
    echo "      uv run notebooklm-mcp --config notebooklm-config.json chat --message 'Hello'"
    echo ""
    echo "   3. Integrate with VS Code using .vscode/notebooklm-mcp-config.json"
    echo ""
else
    echo ""
    echo "⚠️  Warning: Test failed"
    echo "   This might be normal if the server needs to be running"
    echo "   Try starting the server manually:"
    echo "   uv run notebooklm-mcp --config notebooklm-config.json server"
    echo ""
fi
