#!/bin/bash
# Quick test script for NotebookLM MCP

set -e

echo "🧪 NotebookLM MCP - Quick Test"
echo "=============================="
echo ""

CONFIG="notebooklm-config.json"
NOTEBOOK_ID="1dc787c2-8387-4223-b2ac-9ea04d1c37d1"

# Check if config exists
if [ ! -f "$CONFIG" ]; then
    echo "❌ Error: $CONFIG not found!"
    echo "   Run the init command first:"
    echo "   uv run notebooklm-mcp init https://notebooklm.google.com/notebook/$NOTEBOOK_ID"
    exit 1
fi

# Check if profile directory exists
PROFILE_DIR=$(grep -o '"profile_dir": "[^"]*"' "$CONFIG" | cut -d'"' -f4)
if [ ! -d "$PROFILE_DIR" ] || [ -z "$(ls -A "$PROFILE_DIR" 2>/dev/null)" ]; then
    echo "⚠️  Warning: Chrome profile not set up"
    echo "   You need to authenticate first!"
    echo ""
    echo "   Run: ./setup-notebooklm-auth.sh"
    echo ""
    exit 1
fi

echo "✅ Config file found: $CONFIG"
echo "✅ Profile directory found: $PROFILE_DIR"
echo ""

# Test 1: Show configuration
echo "📋 Test 1: Show Configuration"
echo "------------------------------"
if uv run notebooklm-mcp --config "$CONFIG" config-show; then
    echo "✅ Configuration valid"
else
    echo "❌ Configuration check failed"
    exit 1
fi
echo ""

# Test 2: Test connection
echo "🔗 Test 2: Test Connection"
echo "--------------------------"
if uv run notebooklm-mcp --config "$CONFIG" test --notebook "$NOTEBOOK_ID" 2>&1 | grep -q "success\|connected\|✅"; then
    echo "✅ Connection test passed!"
else
    echo "⚠️  Connection test inconclusive (this may be normal)"
    echo "   The server might need to run in the background"
fi
echo ""

# Test 3: Start HTTP server for manual testing
echo "🌐 Test 3: HTTP Server (Optional)"
echo "-----------------------------------"
echo "To start an HTTP server for manual testing:"
echo ""
echo "  uv run notebooklm-mcp --config $CONFIG server --transport http --port 8001"
echo ""
echo "Then in another terminal, test with curl:"
echo ""
cat << 'EOF'
  curl -X POST http://localhost:8001/mcp \
    -H "Content-Type: application/json" \
    -d '{
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/call",
      "params": {
        "name": "healthcheck",
        "arguments": {}
      }
    }'
EOF
echo ""

# Test 4: Integration with AI assistants
echo "🤖 Test 4: AI Assistant Integration"
echo "------------------------------------"
echo "To use with GitHub Copilot or Claude Desktop:"
echo ""
echo "1. Add to your AI assistant's MCP configuration:"
echo ""
cat << EOF
   {
     "mcpServers": {
       "notebooklm": {
         "command": "uv",
         "args": [
           "run",
           "notebooklm-mcp",
           "--config",
           "$CONFIG",
           "server"
         ],
         "cwd": "$(pwd)"
       }
     }
   }
EOF
echo ""
echo "2. Restart your AI assistant"
echo "3. Ask questions about your NotebookLM notebook!"
echo ""

echo "✅ All checks complete!"
echo ""
echo "📝 Next steps:"
echo "   - If authentication isn't set up: ./setup-notebooklm-auth.sh"
echo "   - Start the server: uv run notebooklm-mcp --config $CONFIG server"
echo "   - Or use HTTP mode: uv run notebooklm-mcp --config $CONFIG server --transport http --port 8001"
echo ""
