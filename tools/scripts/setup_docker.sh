#!/bin/bash
# Docker Setup Script for TTA Development Environment
# Handles Docker installation and configuration for WSL2/Linux environments

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
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Header
print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                        DOCKER SETUP FOR TTA DEVELOPMENT                     ║"
    echo "║                     Automated Docker Installation & Configuration           ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check current Docker status
check_docker_status() {
    log_step "Checking current Docker status..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker command found: $(docker --version)"
        
        if docker ps &> /dev/null 2>&1; then
            log_success "Docker is working correctly!"
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            return 0
        else
            log_warning "Docker command exists but daemon is not accessible"
            return 1
        fi
    else
        log_warning "Docker command not found"
        return 1
    fi
}

# Detect environment
detect_environment() {
    log_step "Detecting environment..."
    
    if [[ -f /proc/version ]] && grep -q microsoft /proc/version; then
        echo "WSL2"
    elif [[ -f /.dockerenv ]]; then
        echo "CONTAINER"
    elif [[ -n "$SSH_CLIENT" ]] || [[ -n "$SSH_TTY" ]]; then
        echo "REMOTE"
    else
        echo "LINUX"
    fi
}

# Check for Docker Desktop on Windows (WSL2 only)
check_docker_desktop() {
    if [[ -f "/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" ]]; then
        log_info "Docker Desktop found on Windows host"
        return 0
    else
        log_info "Docker Desktop not found on Windows host"
        return 1
    fi
}

# Enable Docker Desktop WSL2 integration
setup_docker_desktop_wsl2() {
    log_step "Setting up Docker Desktop WSL2 integration..."
    
    if ! check_docker_desktop; then
        log_error "Docker Desktop not found. Please install Docker Desktop first."
        return 1
    fi
    
    echo
    log_info "To enable Docker Desktop WSL2 integration:"
    echo "  1. Open Docker Desktop on Windows"
    echo "  2. Go to Settings (gear icon)"
    echo "  3. Navigate to Resources → WSL Integration"
    echo "  4. Enable 'Enable integration with my default WSL distro'"
    echo "  5. Enable integration with your Ubuntu distribution"
    echo "  6. Click 'Apply & Restart'"
    echo "  7. Restart this WSL2 terminal"
    echo
    
    read -p "Press Enter after completing these steps to test Docker access..."
    
    if check_docker_status; then
        log_success "Docker Desktop WSL2 integration is working!"
        return 0
    else
        log_error "Docker Desktop WSL2 integration is not working yet"
        log_info "Try restarting WSL2: wsl --shutdown (from Windows), then reopen terminal"
        return 1
    fi
}

# Install Docker Engine directly in Linux/WSL2
install_docker_engine() {
    log_step "Installing Docker Engine..."
    
    # Update package index
    log_info "Updating package index..."
    sudo apt update
    
    # Install prerequisites
    log_info "Installing prerequisites..."
    sudo apt install -y ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    log_info "Adding Docker's official GPG key..."
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Add Docker repository
    log_info "Adding Docker repository..."
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    log_info "Installing Docker Engine..."
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add user to docker group
    log_info "Adding user to docker group..."
    sudo usermod -aG docker $USER
    
    # Start Docker service
    log_info "Starting Docker service..."
    sudo service docker start
    
    # Enable Docker to start automatically
    if command -v systemctl &> /dev/null; then
        sudo systemctl enable docker
    else
        # For WSL2 without systemd
        if ! grep -q "sudo service docker start" ~/.bashrc; then
            echo "# Auto-start Docker service" >> ~/.bashrc
            echo "sudo service docker start &> /dev/null" >> ~/.bashrc
        fi
    fi
    
    log_success "Docker Engine installation completed!"
    log_warning "Please restart your terminal or run: newgrp docker"
    
    return 0
}

# Test Docker installation
test_docker() {
    log_step "Testing Docker installation..."
    
    if check_docker_status; then
        log_info "Running Docker hello-world test..."
        if docker run --rm hello-world &> /dev/null; then
            log_success "Docker is working correctly!"
            return 0
        else
            log_error "Docker hello-world test failed"
            return 1
        fi
    else
        return 1
    fi
}

# Main setup function
main() {
    print_header
    
    local env=$(detect_environment)
    log_info "Environment detected: $env"
    
    # Check if Docker is already working
    if check_docker_status; then
        log_success "Docker is already working correctly!"
        echo
        log_info "You can now use the TTA development environment:"
        echo "  cd /home/thein/projects/projects/TTA"
        echo "  ./scripts/augster_startup.sh"
        return 0
    fi
    
    echo
    log_info "Docker is not accessible. Let's fix this!"
    echo
    
    case $env in
        "WSL2")
            log_info "WSL2 environment detected"
            
            if check_docker_desktop; then
                log_info "Docker Desktop found - attempting WSL2 integration setup"
                if setup_docker_desktop_wsl2; then
                    test_docker
                    return $?
                else
                    log_warning "Docker Desktop WSL2 integration failed"
                    log_info "Falling back to Docker Engine installation..."
                    install_docker_engine
                fi
            else
                log_info "Docker Desktop not found - installing Docker Engine"
                install_docker_engine
            fi
            ;;
        "LINUX")
            log_info "Linux environment detected - installing Docker Engine"
            install_docker_engine
            ;;
        "CONTAINER")
            log_error "Running inside a container - Docker-in-Docker not recommended"
            log_info "Please run this script on the host system"
            return 1
            ;;
        "REMOTE")
            log_info "Remote environment detected - installing Docker Engine"
            install_docker_engine
            ;;
        *)
            log_warning "Unknown environment - attempting Docker Engine installation"
            install_docker_engine
            ;;
    esac
    
    echo
    log_info "Setup completed! Testing Docker access..."
    if test_docker; then
        echo
        log_success "🎉 Docker setup successful!"
        echo
        log_info "Next steps:"
        echo "  1. Restart your terminal (or run: newgrp docker)"
        echo "  2. Navigate to TTA project: cd /home/thein/projects/projects/TTA"
        echo "  3. Start development environment: ./scripts/augster_startup.sh"
        echo "  4. Test VS Code terminal: should now show 'docker ✅'"
        echo
    else
        echo
        log_error "Docker setup completed but testing failed"
        log_info "Please restart your terminal and try again"
        log_info "If issues persist, check: scripts/DOCKER_SETUP_GUIDE.md"
        return 1
    fi
}

# Run main function
main "$@"
