# VS Code Terminal Startup Script Configuration

## For the VS Code Terminal Startup Script Box

### **Option 1: Full TTA Development Script (Recommended)**
```bash
/home/thein/projects/projects/TTA/scripts/vscode_terminal_startup.sh
```

### **Option 2: Simple One-Liner**
```bash
[[ -f /home/thein/projects/projects/TTA/scripts/vscode_terminal_startup.sh ]] && source /home/thein/projects/projects/TTA/scripts/vscode_terminal_startup.sh
```

### **Option 3: Inline TTA Setup**
```bash
[[ -f "pyproject.toml" && -d "src" && -f "scripts/augster_startup.sh" ]] && echo "🚀 TTA Dev Environment Ready" && alias tta-start='./scripts/augster_startup.sh' && alias tta-test='uv run pytest tests/'
```

## What Each Option Does

### **Option 1: Full Script** ✨ **(Recommended)**
- **TTA Project Detection**: Automatically detects if you're in a TTA project
- **Smart Aliases**: Sets up `tta-start`, `tta-test`, `tta-format`, `tta-lint`, `tta-type`
- **Service Status**: Shows Redis/Neo4j status and startup hints
- **Tool Verification**: Checks uv, Node.js, Docker availability
- **Performance Info**: Shows if optimized shell is installed
- **Context Awareness**: Different behavior for TTA vs other projects

**Output Example:**
```
🚀 TTA Development Environment
   Project: TTA
   Quick commands: tta-start, tta-test, tta-format, tta-lint, tta-type
   Shell: ⚡ Optimized (99.5% faster startup)
   Services: Redis ✅ Neo4j ✅
   Tools: uv ✅ node ✅ docker ✅
Terminal ready! 🎯
```

### **Option 2: Safe One-Liner**
- **Conditional Loading**: Only runs if the script exists
- **Error Prevention**: Won't break if script is missing
- **Same Features**: All functionality of Option 1 when available

### **Option 3: Minimal Inline**
- **Basic TTA Detection**: Simple project detection
- **Essential Aliases**: Just the most important shortcuts
- **Lightweight**: Minimal overhead, fast execution

## How to Configure in VS Code

### **Step 1: Open VS Code Settings**
- Press `Ctrl+,` (or `Cmd+,` on Mac)
- Search for "terminal startup"
- Find "Terminal › Integrated › Shell Args"

### **Step 2: Set the Startup Script**
1. Look for the "Start-up script" section
2. In the text box, paste one of the options above
3. The setting will be saved automatically

### **Step 3: Test the Configuration**
1. Open a new terminal in VS Code (`Ctrl+`` ` or `Terminal > New Terminal`)
2. You should see the TTA development environment message
3. Test the aliases: `tta-start`, `tta-test`, etc.

## Advanced Configuration

### **Quiet Mode**
To reduce output, set environment variable:
```bash
export VSCODE_TERMINAL_QUIET=true && /home/thein/projects/projects/TTA/scripts/vscode_terminal_startup.sh
```

### **Project-Specific Settings**
For TTA project only, create `.vscode/settings.json`:
```json
{
    "terminal.integrated.shellArgs.linux": [
        "-c",
        "source /home/thein/projects/projects/TTA/scripts/vscode_terminal_startup.sh; exec bash"
    ]
}
```

### **Global Settings**
For all projects, add to VS Code user settings:
```json
{
    "terminal.integrated.profiles.linux": {
        "TTA Optimized": {
            "path": "bash",
            "args": [
                "-c",
                "source /home/thein/projects/projects/TTA/scripts/vscode_terminal_startup.sh; exec bash"
            ]
        }
    },
    "terminal.integrated.defaultProfile.linux": "TTA Optimized"
}
```

## Features Provided

### **🚀 TTA Project Features**
- **Instant Recognition**: Detects TTA projects automatically
- **Quick Commands**: Pre-configured aliases for common tasks
- **Service Status**: Shows Docker service status
- **Performance Info**: Displays shell optimization status
- **Smart Hints**: Contextual suggestions for next steps

### **🔧 General Development Features**
- **Tool Verification**: Checks essential development tools
- **Git Integration**: Shows repository and branch information
- **Navigation Helpers**: Quick project navigation commands
- **Performance Utilities**: Shell performance testing functions

### **⚡ Performance Optimizations**
- **Lazy Loading**: Expensive tools load only when needed
- **Context Awareness**: Different behavior based on project type
- **Minimal Overhead**: Fast execution, no unnecessary delays
- **Smart Caching**: Avoids redundant operations

## Troubleshooting

### **Script Not Found**
If you get "file not found" error:
```bash
# Check if script exists
ls -la /home/thein/projects/projects/TTA/scripts/vscode_terminal_startup.sh

# Make sure it's executable
chmod +x /home/thein/projects/projects/TTA/scripts/vscode_terminal_startup.sh
```

### **Permission Issues**
```bash
# Fix permissions
chmod +x /home/thein/projects/projects/TTA/scripts/vscode_terminal_startup.sh
```

### **Path Issues**
Update the path in the startup script box to match your actual TTA location:
```bash
# Replace with your actual path
/path/to/your/TTA/scripts/vscode_terminal_startup.sh
```

## Integration with Shell Optimization

The VS Code terminal startup script works perfectly with the optimized shell configuration:

- **If optimized shell installed**: Uses optimized configuration for maximum performance
- **If standard shell**: Provides basic optimizations for the session
- **Seamless integration**: No conflicts, enhanced functionality

## Recommendation

**Use Option 1** (Full Script) for the best development experience. It provides:
- Complete TTA development environment setup
- Smart context awareness
- Performance monitoring
- Service status checking
- Helpful development shortcuts

Simply paste this into your VS Code terminal startup script box:
```bash
/home/thein/projects/projects/TTA/scripts/vscode_terminal_startup.sh
```
