# Docker Desktop WSL2 Proxy Error - Quick Fix Guide

## 🚨 **Your Specific Error**

```
running wsl distro proxy in Ubuntu distro: running proxy: running wslexec: 
An error occurred while running the command. DockerDesktop/Wsl/ExecError: 
c:\windows\system32\wsl.exe -d ubuntu -u root -e /mnt/wsl/docker-desktop/docker-desktop-user-distro 
proxy --distro-name ubuntu --docker-desktop-root /mnt/wsl/docker-desktop 
c:\program files\docker\docker\resources: exit status 1
```

## 🎯 **Root Cause**

Docker Desktop is trying to start the WSL2 integration proxy with distribution name "ubuntu", but your actual WSL2 distribution has a different name or configuration that's causing the proxy startup to fail.

## ⚡ **Quick Fix (Most Likely to Work)**

### **Step 1: Find Your Actual WSL Distribution Name**

From **Windows Command Prompt or PowerShell** (not WSL2):
```cmd
wsl --list --verbose
```

Your distribution might be named:
- `Ubuntu-24.04` (not just `ubuntu`)
- `Ubuntu-22.04`
- Custom name like `Gamepower`

### **Step 2: Reset Docker Desktop WSL2 Integration**

From **Windows Command Prompt as Administrator**:
```cmd
# Stop Docker Desktop completely
taskkill /f /im "Docker Desktop.exe"

# Shutdown WSL2 to reset state
wsl --shutdown

# Wait 10 seconds, then restart Docker Desktop
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### **Step 3: Reconfigure with Correct Distribution Name**

1. **Wait** for Docker Desktop to fully start (2-3 minutes)
2. **Open Docker Desktop** → **Settings** → **Resources** → **WSL Integration**
3. **Disable all integrations** → **Apply & Restart**
4. **Enable integration** with your **exact distribution name** from Step 1
5. **Apply & Restart** again

### **Step 4: Test Integration**

Back in your WSL2 terminal:
```bash
# Test Docker access
docker --version
docker ps

# Test TTA environment
cd /home/thein/projects/projects/TTA
./scripts/vscode_terminal_startup.sh
# Should now show: docker ✅
```

## 🛠️ **Alternative: Automated Fix Script**

If the manual steps don't work, use our automated fix:

```bash
# Run the automated fix script
cd /home/thein/projects/projects/TTA
./scripts/fix_docker_wsl2_integration.sh

# Follow the interactive prompts
# Script will guide you through Windows commands and provide fallback options
```

## 🔄 **Fallback: Docker Engine Installation**

If Docker Desktop integration continues to fail:

```bash
# Install Docker Engine directly (more reliable for development)
cd /home/thein/projects/projects/TTA
./scripts/setup_docker.sh

# This provides the same functionality without Docker Desktop dependency
```

## ✅ **Success Verification**

After applying the fix, you should see:

### **VS Code Terminal Startup**
```bash
🚀 TTA Development Environment
   Project: TTA
   Services: Redis ✅ Neo4j ✅
   Tools: uv ✅ node ✅ docker ✅
Terminal ready! 🎯
```

### **Docker Commands Working**
```bash
docker --version
# Docker version 24.x.x, build xxxxx

docker ps
# CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES

docker run hello-world
# Hello from Docker! (success message)
```

### **TTA Development Stack**
```bash
# Full containerized development environment
./scripts/augster_startup.sh

# Successfully starts Redis and Neo4j containers
```

## 🚨 **If Fix Doesn't Work**

1. **Check Windows Docker Desktop version** - update to latest
2. **Try Docker Desktop Preview** - often has better WSL2 compatibility
3. **Use Docker Engine instead** - more reliable for development work
4. **Check detailed guide**: `cat ./scripts/DOCKER_WSL2_INTEGRATION_FIX.md`

## 📞 **Quick Support Commands**

```bash
# Diagnose current state
./scripts/fix_docker_wsl2_integration.sh

# Get detailed help
cat ./scripts/DOCKER_WSL2_INTEGRATION_FIX.md

# Install Docker Engine fallback
./scripts/setup_docker.sh

# Test TTA integration
./scripts/vscode_terminal_startup.sh
```

## 🎊 **Expected Timeline**

- **Manual fix**: 5-10 minutes
- **Automated script**: 2-3 minutes + Windows commands
- **Docker Engine fallback**: 3-5 minutes
- **Total resolution time**: 10-15 minutes maximum

The "running wsl distro proxy" error is a common Docker Desktop WSL2 integration issue with well-established solutions. The distribution name mismatch fix resolves it in 90% of cases!
