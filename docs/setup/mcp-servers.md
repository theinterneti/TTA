# ✅ NotebookLM MCP Configured for GitHub Copilot!

## 📍 Configuration Location

Your NotebookLM MCP server has been configured at:
```
~/.config/Code/User/globalStorage/automatalabs.copilot-mcp/mcp.json
```

This is the global MCP configuration for the **Copilot MCP extension** by Automata Labs.

## 🔄 Reload Required

**IMPORTANT:** You must reload VS Code for the MCP server to be recognized!

### Steps:

1. **Press:** `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. **Type:** `Developer: Reload Window`
3. **Press:** `Enter`

## 🧪 Testing the Connection

After reloading, open GitHub Copilot Chat and try:

### 1. Check MCP Server Status

```
List the available MCP tools
```

or

```
What MCP servers are connected?
```

You should see **notebooklm** in the list!

### 2. Use NotebookLM

```
Use the notebooklm chat_with_notebook tool to ask: "What are the main topics in this notebook?"
```

or more naturally:

```
What are the main topics in my NotebookLM notebook?
```

### 3. Check Health

```
Use the notebooklm healthcheck tool
```

## 🎯 Your Notebook

Your configured NotebookLM notebook:
https://notebooklm.google.com/notebook/1dc787c2-8387-4223-b2ac-9ea04d1c37d1

## 📋 Available Tools

Once connected, you'll have access to:

| Tool | Description |
|------|-------------|
| `healthcheck` | Check NotebookLM connection status |
| `chat_with_notebook` | Send a message and get a response |
| `send_chat_message` | Send a message to NotebookLM |
| `get_chat_response` | Get the response from NotebookLM |
| `navigate_to_notebook` | Switch to a different notebook |
| `get_default_notebook` | Get current notebook ID |
| `set_default_notebook` | Set a different default notebook |
| `get_quick_response` | Get a quick response |

## 🐛 Troubleshooting

### "notebooklm not found" or No MCP tools visible

1. **Verify the config file exists:**
   ```bash
   cat ~/.config/Code/User/globalStorage/automatalabs.copilot-mcp/mcp.json
   ```

2. **Reload VS Code window** (this is critical!)

3. **Check Copilot MCP extension is active:**
   - Look for the Copilot MCP icon in the status bar
   - Or run: `code --list-extensions | grep copilot-mcp`

4. **Verify authentication is complete:**
   ```bash
   ./test-notebooklm-mcp.sh
   ```

### MCP Server Starts But Times Out

1. **Complete authentication first:**
   ```bash
   ./setup-notebooklm-auth.sh
   ```

2. **Check Chrome profile exists:**
   ```bash
   ls -la chrome_profile_notebooklm/
   ```

3. **Test manually:**
   ```bash
   uv run notebooklm-mcp --config notebooklm-config.json test
   ```

### "Chrome/ChromeDriver version mismatch"

Update Chrome:
```bash
sudo apt update
sudo apt upgrade google-chrome-stable
```

## 🎨 Using with Copilot

### Natural Language Queries

Copilot will automatically use NotebookLM when relevant. Just ask naturally:

```
What topics are covered in my research notebook?
```

```
Summarize the key points from my NotebookLM sources
```

```
Based on my NotebookLM research, what should I focus on next?
```

### Explicit Tool Use

You can also explicitly call NotebookLM tools:

```
@workspace Use the notebooklm MCP server to check what my notebook contains
```

### Combining with Code

```
Based on my NotebookLM notebook and this code, suggest improvements
```

## 📁 Related Files

- **Global MCP Config:** `~/.config/Code/User/globalStorage/automatalabs.copilot-mcp/mcp.json`
- **Notebook Config:** `notebooklm-config.json`
- **Chrome Profile:** `chrome_profile_notebooklm/`
- **Setup Script:** `./setup-notebooklm-auth.sh`
- **Test Script:** `./test-notebooklm-mcp.sh`

## 🔗 Alternative: Claude Desktop

If you also use Claude Desktop, you can add NotebookLM there too:

**File:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "uv",
      "args": [
        "run",
        "notebooklm-mcp",
        "--config",
        "/home/thein/recovered-tta-storytelling/notebooklm-config.json",
        "server"
      ]
    }
  }
}
```

## 🎉 Next Steps

1. **Reload VS Code** (`Ctrl+Shift+P` → `Developer: Reload Window`)
2. **Open Copilot Chat**
3. **Ask about your notebook!**

---

**Ready to explore your NotebookLM notebook with AI assistance! 🚀**


---
**Logseq:** [[TTA.dev/Docs/Setup/Mcp-servers]]
