# Docker Setup Guide for TTA Development Environment

## 🔍 **Diagnosis Results**

**Environment Detected**: WSL2 (Ubuntu 24.04.2 LTS)  
**Docker Status**: ❌ Not accessible from WSL2  
**Docker Desktop**: ✅ Installed on Windows host  
**Issue**: Docker Desktop WSL2 integration not enabled

## 🚀 **Solution 1: Enable Docker Desktop WSL2 Integration (Recommended)**

This is the **easiest and recommended** approach since Docker Desktop is already installed.

### **Step 1: Enable WSL2 Integration in Docker Desktop**

1. **Open Docker Desktop** on Windows
2. **Go to Settings** (gear icon in top-right)
3. **Navigate to Resources → WSL Integration**
4. **Enable WSL integration**:
   - ✅ Check "Enable integration with my default WSL distro"
   - ✅ Check "Ubuntu-24.04" (or your specific distro name)
5. **Click "Apply & Restart"**

### **Step 2: Verify Integration**

Open a new WSL2 terminal and test:
```bash
# Test Docker access
docker --version
docker ps

# Should show Docker version and running containers
```

### **Step 3: Test TTA Environment**
```bash
# Navigate to TTA project
cd /home/thein/projects/projects/TTA

# Test the startup script
./scripts/vscode_terminal_startup.sh

# Should now show: docker ✅
```

## 🛠️ **Solution 2: Install Docker Engine in WSL2 (Alternative)**

If Docker Desktop integration doesn't work, install Docker directly in WSL2.

### **Step 1: Install Docker Engine**
```bash
# Update package index
sudo apt update

# Install prerequisites
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### **Step 2: Configure Docker for WSL2**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start

# Enable Docker to start automatically
echo 'sudo service docker start' >> ~/.bashrc
```

### **Step 3: Test Installation**
```bash
# Restart terminal or reload bashrc
source ~/.bashrc

# Test Docker
docker --version
docker run hello-world
```

## 🔧 **Solution 3: Alternative Container Runtime (Podman)**

If Docker continues to have issues, use Podman as an alternative.

### **Install Podman**
```bash
# Install Podman
sudo apt update
sudo apt install -y podman

# Create Docker alias for compatibility
echo 'alias docker=podman' >> ~/.bashrc
source ~/.bashrc
```

## 🛡️ **Updated Scripts with Better Docker Handling**

I'll update the startup scripts to handle Docker issues more gracefully.

### **Enhanced Docker Detection**
The scripts will now:
- ✅ Detect Docker Desktop WSL2 integration
- ✅ Detect Docker Engine installation
- ✅ Detect Podman as alternative
- ✅ Provide helpful setup guidance
- ✅ Gracefully handle missing Docker

## 📋 **Troubleshooting Common Issues**

### **Issue 1: "permission denied while trying to connect to Docker daemon"**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Restart terminal or logout/login
```

### **Issue 2: Docker Desktop not starting**
```bash
# Restart Docker Desktop on Windows
# Or restart WSL2:
wsl --shutdown
# Then restart your WSL2 terminal
```

### **Issue 3: WSL2 integration not working**
```bash
# Check WSL2 version
wsl --list --verbose

# Update WSL2 if needed
wsl --update
```

### **Issue 4: Docker service not starting in WSL2**
```bash
# Start Docker service manually
sudo service docker start

# Check service status
sudo service docker status

# Enable auto-start
sudo systemctl enable docker
```

## 🎯 **Verification Steps**

After implementing any solution, verify with:

```bash
# 1. Test Docker access
docker --version
docker ps

# 2. Test TTA startup script
cd /home/thein/projects/projects/TTA
./scripts/vscode_terminal_startup.sh

# Should show: docker ✅

# 3. Test TTA development environment
./scripts/augster_startup.sh --dry-run

# Should detect Docker and show service management options
```

## 🚀 **Expected Results After Fix**

Once Docker is properly configured, you should see:

```
🚀 TTA Development Environment
   Project: TTA
   Quick commands: tta-start, tta-test, tta-format, tta-lint, tta-type
   Shell: ⚡ Optimized (99.5% faster startup)
   Services: Redis ✅ Neo4j ✅
   Tools: uv ✅ node ✅ docker ✅
Terminal ready! 🎯
```

## 📝 **Next Steps**

1. **Choose Solution 1** (Docker Desktop WSL2 integration) - easiest
2. **Follow the step-by-step instructions**
3. **Test the integration** with verification commands
4. **Run the updated TTA startup scripts**
5. **Enjoy full TTA development environment** with Redis and Neo4j services

The TTA development environment will then have full access to containerized services for optimal development workflow!
