# Using NotebookLM with GitHub Copilot

Your VS Code is now configured to use NotebookLM as an MCP server! 🎉

## ✅ What's Been Configured

The file `.vscode/settings.json` now includes:

```json
"github.copilot.chat.mcp": {
  "servers": {
    "notebooklm": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "notebooklm-mcp", "--config", "notebooklm-config.json", "server"],
      "cwd": "${workspaceFolder}",
      "env": {}
    }
  }
}
```

## 🚀 How to Use

### 1. Reload VS Code Window

Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) and run:
```
Developer: Reload Window
```

This ensures the new MCP server configuration is loaded.

### 2. Open GitHub Copilot Chat

Click the Copilot icon in the sidebar or press `Ctrl+Alt+I`.

### 3. Check Available MCP Servers

In the chat, you can check if NotebookLM is available by typing:
```
@workspace what MCP servers are available?
```

### 4. Ask Questions About Your NotebookLM Notebook

You can now query your NotebookLM notebook directly through Copilot!

**Example queries:**

```
What are the main topics covered in my NotebookLM notebook?
```

```
Can you summarize the key points from my NotebookLM research?
```

```
What insights can you find in my NotebookLM notebook about [specific topic]?
```

```
Help me understand the connections between the sources in my NotebookLM notebook
```

## 🔧 Available NotebookLM Tools

Your Copilot now has access to these NotebookLM tools:

- **healthcheck** - Check if the NotebookLM connection is working
- **chat_with_notebook** - Send a message and get a response from NotebookLM
- **send_chat_message** - Send a message to NotebookLM
- **get_chat_response** - Get the response from NotebookLM
- **navigate_to_notebook** - Switch to a different notebook
- **get_default_notebook** - Get the current notebook ID
- **set_default_notebook** - Set a different default notebook
- **get_quick_response** - Get a quick response from NotebookLM

## 🧪 Testing the Connection

Try this in Copilot Chat:

```
Can you use the NotebookLM healthcheck tool to verify the connection is working?
```

Or:

```
Use NotebookLM to tell me what my notebook is about
```

## 🎯 Example Use Cases

### 1. Research Assistant

```
Use my NotebookLM notebook to help me understand [concept]
```

### 2. Content Extraction

```
What are the key quotes from my NotebookLM sources about [topic]?
```

### 3. Cross-Reference

```
How does the information in my NotebookLM notebook relate to this code I'm working on?
```

### 4. Idea Generation

```
Based on my NotebookLM research, suggest 5 features I could add to this project
```

## 🐛 Troubleshooting

### "MCP server not found" or "NotebookLM not available"

**Solution 1: Reload the window**
```
Ctrl+Shift+P → Developer: Reload Window
```

**Solution 2: Check if authentication is set up**
```bash
./test-notebooklm-mcp.sh
```

If authentication isn't complete, run:
```bash
./setup-notebooklm-auth.sh
```

**Solution 3: Verify the config file exists**
```bash
ls -la notebooklm-config.json
ls -la chrome_profile_notebooklm/
```

### "Connection failed" or timeout errors

The NotebookLM MCP server needs to connect to Google's servers. Check:

1. **Internet connection** - Make sure you're online
2. **Google authentication** - Run `./setup-notebooklm-auth.sh` to re-authenticate
3. **Notebook access** - Verify you can access https://notebooklm.google.com/notebook/1dc787c2-8387-4223-b2ac-9ea04d1c37d1

### "Chrome/ChromeDriver version mismatch"

Update Chrome and try again:
```bash
sudo apt update
sudo apt upgrade google-chrome-stable
```

## 📝 Notes

- The NotebookLM MCP server will start automatically when you use it in Copilot
- It runs in headless mode (no visible browser window)
- Authentication is persisted in `chrome_profile_notebooklm/`
- Each query may take a few seconds as it communicates with Google's servers

## 🎉 Next Steps

1. **Reload VS Code** to activate the configuration
2. **Open Copilot Chat** and try asking about your notebook
3. **Experiment** with different queries and see what insights you can extract!

## 📚 Additional Resources

- [NotebookLM MCP Setup Guide](NOTEBOOKLM_MCP_SETUP.md)
- [Your NotebookLM Notebook](https://notebooklm.google.com/notebook/1dc787c2-8387-4223-b2ac-9ea04d1c37d1)
- [GitHub Copilot MCP Documentation](https://docs.github.com/en/copilot)
- [FastMCP Documentation](https://gofastmcp.com)

---

**Happy researching with NotebookLM + Copilot! 🚀**


---
**Logseq:** [[TTA.dev/Docs/Guides/Notebooklm-copilot]]
