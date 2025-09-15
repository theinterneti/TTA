#!/bin/bash
# Docker Desktop WSL2 Integration Error Fix Script
# Specifically addresses the "running wsl distro proxy" error

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }

print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                   DOCKER DESKTOP WSL2 INTEGRATION FIX                       ║"
    echo "║                 Resolves 'running wsl distro proxy' Error                   ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if Docker Desktop components are present
check_docker_desktop() {
    if [[ -d "/mnt/wsl/docker-desktop" ]] && [[ -f "/mnt/wsl/docker-desktop/docker-desktop-user-distro" ]]; then
        log_info "Docker Desktop WSL2 components found"
        return 0
    else
        log_error "Docker Desktop WSL2 components not found"
        return 1
    fi
}

# Test Docker Desktop proxy
test_docker_proxy() {
    log_step "Testing Docker Desktop proxy..."
    
    if /mnt/wsl/docker-desktop/docker-desktop-user-distro --help &> /dev/null; then
        log_success "Docker Desktop proxy is executable"
        return 0
    else
        log_error "Docker Desktop proxy execution failed"
        return 1
    fi
}

# Check current Docker status
check_docker_status() {
    log_step "Checking current Docker status..."
    
    if command -v docker &> /dev/null; then
        if docker ps &> /dev/null 2>&1; then
            log_success "Docker is working correctly!"
            return 0
        else
            log_warning "Docker command exists but daemon not accessible"
            return 1
        fi
    else
        log_warning "Docker command not found"
        return 1
    fi
}

# Clean existing Docker configurations
clean_docker_config() {
    log_step "Cleaning existing Docker configurations..."
    
    # Remove user Docker config
    rm -rf ~/.docker 2>/dev/null || true
    
    # Remove any existing Docker binaries that might conflict
    sudo rm -rf /usr/local/bin/docker* 2>/dev/null || true
    
    # Clear Docker environment variables
    unset DOCKER_HOST DOCKER_CONTEXT 2>/dev/null || true
    
    log_success "Docker configuration cleaned"
}

# Fix WSL2 configuration for Docker Desktop compatibility
fix_wsl_config() {
    log_step "Optimizing WSL2 configuration for Docker Desktop..."
    
    # Backup existing config
    if [[ -f /etc/wsl.conf ]]; then
        sudo cp /etc/wsl.conf /etc/wsl.conf.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    # Create optimized WSL2 configuration
    sudo tee /etc/wsl.conf > /dev/null << 'EOF'
[automount]
enabled = true
options = "metadata,uid=1000,gid=1000,umask=022,fmask=111,case=off"
mountFsTab = true
crossDistro = true

[network]
generateHosts = true
generateResolvConf = true

[interop]
enabled = true
appendWindowsPath = true

[user]
default = thein

[boot]
systemd = true

[filesystem]
umask = 022
EOF
    
    log_success "WSL2 configuration optimized"
    log_warning "WSL2 restart required for changes to take effect"
}

# Provide Windows commands for Docker Desktop reset
provide_windows_commands() {
    log_step "Docker Desktop WSL2 Integration Reset Instructions"
    echo
    log_info "Please run these commands from Windows Command Prompt (as Administrator):"
    echo
    echo -e "${YELLOW}# Stop Docker Desktop${NC}"
    echo "taskkill /f /im \"Docker Desktop.exe\""
    echo
    echo -e "${YELLOW}# Shutdown WSL2${NC}"
    echo "wsl --shutdown"
    echo
    echo -e "${YELLOW}# Wait 10 seconds, then restart Docker Desktop${NC}"
    echo "start \"\" \"C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe\""
    echo
    echo -e "${YELLOW}# Check your WSL distribution name${NC}"
    echo "wsl --list --verbose"
    echo
    log_info "After running these commands:"
    echo "1. Wait for Docker Desktop to fully start (2-3 minutes)"
    echo "2. Go to Docker Desktop Settings → Resources → WSL Integration"
    echo "3. Disable all integrations, Apply & Restart"
    echo "4. Enable integration with your exact distribution name from 'wsl --list'"
    echo "5. Apply & Restart again"
    echo "6. Return to this WSL2 terminal and test: docker --version"
    echo
}

# Install Docker Engine as fallback
install_docker_engine_fallback() {
    log_step "Installing Docker Engine as fallback solution..."
    
    read -p "Docker Desktop integration failed. Install Docker Engine directly? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installing Docker Engine..."
        
        # Use the existing setup script
        if [[ -f "./scripts/setup_docker.sh" ]]; then
            ./scripts/setup_docker.sh
        else
            # Fallback installation
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            sudo service docker start
            
            # Add auto-start to bashrc
            if ! grep -q "sudo service docker start" ~/.bashrc; then
                echo "# Auto-start Docker service" >> ~/.bashrc
                echo "sudo service docker start &> /dev/null" >> ~/.bashrc
            fi
            
            log_success "Docker Engine installed"
            log_warning "Please restart terminal or run: newgrp docker"
        fi
    else
        log_info "Skipping Docker Engine installation"
    fi
}

# Test TTA integration
test_tta_integration() {
    log_step "Testing TTA development environment integration..."
    
    if check_docker_status; then
        log_info "Testing TTA startup script..."
        if [[ -f "./scripts/vscode_terminal_startup.sh" ]]; then
            ./scripts/vscode_terminal_startup.sh | grep -E "(docker|Tools:)" || true
        fi
        
        log_info "Testing TTA development environment..."
        if [[ -f "./scripts/augster_startup.sh" ]]; then
            ./scripts/augster_startup.sh --dry-run | head -10 || true
        fi
        
        log_success "TTA integration test completed"
    else
        log_warning "Docker not accessible - TTA integration test skipped"
    fi
}

# Main execution
main() {
    print_header
    
    log_info "Diagnosing Docker Desktop WSL2 integration error..."
    echo
    
    # Check if we're in the right environment
    if ! check_docker_desktop; then
        log_error "Docker Desktop WSL2 components not found"
        log_info "Please ensure Docker Desktop is installed and WSL2 backend is enabled"
        exit 1
    fi
    
    # Test proxy functionality
    if ! test_docker_proxy; then
        log_error "Docker Desktop proxy is not working"
        log_info "This indicates a serious Docker Desktop installation issue"
        install_docker_engine_fallback
        exit 1
    fi
    
    # Check current Docker status
    if check_docker_status; then
        log_success "Docker is already working! No fix needed."
        test_tta_integration
        exit 0
    fi
    
    log_warning "Docker Desktop WSL2 integration is not working"
    echo
    
    # Clean existing configurations
    clean_docker_config
    
    # Fix WSL2 configuration
    fix_wsl_config
    
    # Provide Windows reset instructions
    provide_windows_commands
    
    echo
    log_info "After completing the Windows commands above, test Docker access:"
    echo "  docker --version"
    echo "  docker ps"
    echo
    log_info "If Docker Desktop integration still fails, run this script again"
    log_info "and choose to install Docker Engine as a reliable alternative."
    echo
    log_info "For detailed troubleshooting, see:"
    echo "  cat ./scripts/DOCKER_WSL2_INTEGRATION_FIX.md"
}

# Run main function
main "$@"
