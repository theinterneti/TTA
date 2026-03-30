# NotebookLM MCP Setup Guide

## Current Status

✅ **Package Installed**: `notebooklm-mcp` has been added to your project
✅ **Config Created**: `notebooklm-config.json` is configured for your notebook
✅ **Profile Directory**: `chrome_profile_notebooklm/` is ready for authentication

## Issue Encountered

Chrome/ChromeDriver version mismatch:

- Current Chrome: version 140.0.7339.185
- Required: version 142

## Solutions

### Option 1: Update Chrome (Recommended)

```bash
# Update Chrome to the latest version
sudo apt update
sudo apt upgrade google-chrome-stable

# Then try initialization again
uv run notebooklm-mcp init https://notebooklm.google.com/notebook/1dc787c2-8387-4223-b2ac-9ea04d1c37d1
```

### Option 2: Manual Browser Authentication

If Chrome update doesn't work, you can manually set up authentication:

1. **Open Chrome with the profile:**
   ```bash
   google-chrome --user-data-dir="$(pwd)/chrome_profile_notebooklm" https://notebooklm.google.com/notebook/1dc787c2-8387-4223-b2ac-9ea04d1c37d1
   ```

2. **Log in to your Google account** in the browser window that opens

3. **Once logged in**, close the browser

4. **The authentication is now saved** in the profile directory


### Option 3: Use Docker (Alternative)

```bash
# Build the Docker image
docker build -t notebooklm-mcp .

# Run with your config
docker run -d \
  --name notebooklm-mcp \
  -v $(pwd)/notebooklm-config.json:/app/notebooklm-config.json:ro \
  -v $(pwd)/chrome_profile_notebooklm:/app/chrome_profile_notebooklm \
  notebooklm-mcp:latest
```

## Using NotebookLM MCP

### Important: Authentication Required First!

Before you can use any NotebookLM MCP commands, you MUST complete authentication. Run:

```bash
./setup-notebooklm-auth.sh
```

Once authentication is complete, you can:

### 1. Test the Connection

```bash
uv run notebooklm-mcp --config notebooklm-config.json test --notebook 1dc787c2-8387-4223-b2ac-9ea04d1c37d1
```

### 2. Start the MCP Server (for AI assistants to connect)

**STDIO mode** (for GitHub Copilot, Claude Desktop):

```bash
uv run notebooklm-mcp --config notebooklm-config.json server
```

**HTTP mode** (for web testing and debugging):

```bash
uv run notebooklm-mcp --config notebooklm-config.json server --transport http --port 8001
```

### 3. Interactive Chat Mode

**Note**: The `chat` command doesn't work the way you might expect. Instead, use the MCP server with an AI assistant.

To test manually, use the HTTP server and curl:

```bash
# Start HTTP server in background
uv run notebooklm-mcp --config notebooklm-config.json server --transport http --port 8001 &

# Test with curl
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "chat_with_notebook",
      "arguments": {
        "message": "What are the main topics?"
      }
    }
  }'
```

## Available Tools

Once connected, you'll have access to:

- **healthcheck**: Check server status
- **send_chat_message**: Send a message to NotebookLM
- **get_chat_response**: Get response with timeout
- **chat_with_notebook**: Complete interaction (send + receive)
- **navigate_to_notebook**: Switch between notebooks
- **get_default_notebook**: Get current notebook ID
- **set_default_notebook**: Set a default notebook
- **get_quick_response**: Get an instant response

## VS Code Integration

The MCP configuration has been created at `.vscode/notebooklm-mcp-config.json`.

To use with GitHub Copilot or Claude Desktop, merge this into your MCP settings:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "uv",
      "args": [
        "run",
        "notebooklm-mcp",
        "--config",
        "notebooklm-config.json",
        "server"
      ],
      "env": {},
      "cwd": "${workspaceFolder}"
    }
  }
}
```

## Configuration Details

Your notebook configuration (in `notebooklm-config.json`):

```json
{
  "default_notebook_id": "1dc787c2-8387-4223-b2ac-9ea04d1c37d1",
  "base_url": "https://notebooklm.google.com",
  "headless": false,
  "timeout": 60,
  "auth": {
    "profile_dir": "./chrome_profile_notebooklm",
    "use_persistent_session": true,
    "auto_login": true
  }
}
```

## Next Steps

1. **Update Chrome** or **manually authenticate** (see options above)
2. **Test the connection** using one of the commands above
3. **Integrate with your AI assistant** using the VS Code MCP config

## Troubleshooting

### Browser Opens But Doesn't Navigate

- Check your internet connection
- Ensure the notebook URL is accessible
- Try manually opening the URL in a regular browser first

### Authentication Fails

- Clear the `chrome_profile_notebooklm` directory and try again
- Make sure you're logged into the correct Google account
- Check if NotebookLM is accessible from your region

### MCP Server Won't Start

- Check if ports are available (8001 for HTTP)
- Ensure the config file path is correct
- Try running with `--debug` flag for more info

## Resources

- [NotebookLM MCP GitHub](https://github.com/khengyun/notebooklm-mcp)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://spec.modelcontextprotocol.io/)
- [Your Notebook](https://notebooklm.google.com/notebook/1dc787c2-8387-4223-b2ac-9ea04d1c37d1)


---
**Logseq:** [[TTA.dev/.archive/Infrastructure/2025-10/Notebooklm_mcp_setup]]
