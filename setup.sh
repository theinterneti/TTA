#!/bin/bash

# TTA Setup Script
# This script initializes and updates the TTA environment with its submodules

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}TTA Setup Script${NC}"
echo "=============================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed. Please install git and try again.${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Warning: Docker is not installed. The TTA environment requires Docker.${NC}"
    echo "Please install Docker before using the TTA environment."
fi

# Initialize submodules if they don't exist
if [ ! -f ".gitmodules" ] || [ ! -d "tta.dev/.git" ] || [ ! -d "TTA.prototype/.git" ]; then
    echo -e "${YELLOW}Initializing submodules...${NC}"
    
    # Check if the directories exist but are not submodules
    if [ -d "tta.dev" ]; then
        echo "tta.dev directory exists but is not a submodule."
        echo -e "${YELLOW}Would you like to backup and replace it? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            mv tta.dev tta.dev.bak
            echo "Backed up to tta.dev.bak"
        else
            echo "Skipping tta.dev submodule initialization."
        fi
    fi
    
    if [ -d "TTA.prototype" ]; then
        echo "TTA.prototype directory exists but is not a submodule."
        echo -e "${YELLOW}Would you like to backup and replace it? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            mv TTA.prototype TTA.prototype.bak
            echo "Backed up to TTA.prototype.bak"
        else
            echo "Skipping TTA.prototype submodule initialization."
        fi
    fi
    
    # Initialize submodules
    if [ ! -d "tta.dev" ]; then
        echo "Initializing tta.dev submodule..."
        git submodule add https://github.com/theinterneti/tta.dev.git tta.dev
    fi
    
    if [ ! -d "TTA.prototype" ]; then
        echo "Initializing TTA.prototype submodule..."
        git submodule add https://github.com/theinterneti/TTA.prototype.git TTA.prototype
    fi
else
    echo -e "${GREEN}Updating submodules...${NC}"
    git submodule update --init --recursive
fi

# Copy Docker configuration files if they don't exist in submodules
echo -e "${GREEN}Checking Docker configuration files...${NC}"

# For tta.dev
if [ ! -f "tta.dev/docker-compose.yml" ]; then
    echo "Copying docker-compose.yml to tta.dev..."
    cp templates/tta.dev/docker-compose.yml tta.dev/
fi

if [ ! -f "tta.dev/Dockerfile" ]; then
    echo "Copying Dockerfile to tta.dev..."
    cp templates/tta.dev/Dockerfile tta.dev/
fi

if [ ! -f "tta.dev/.devcontainer/devcontainer.json" ]; then
    echo "Copying devcontainer.json to tta.dev..."
    mkdir -p tta.dev/.devcontainer
    cp templates/tta.dev/.devcontainer/devcontainer.json tta.dev/.devcontainer/
fi

# For TTA.prototype
if [ ! -f "TTA.prototype/docker-compose.yml" ]; then
    echo "Copying docker-compose.yml to TTA.prototype..."
    cp templates/TTA.prototype/docker-compose.yml TTA.prototype/
fi

if [ ! -f "TTA.prototype/Dockerfile" ]; then
    echo "Copying Dockerfile to TTA.prototype..."
    cp templates/TTA.prototype/Dockerfile TTA.prototype/
fi

if [ ! -f "TTA.prototype/.devcontainer/devcontainer.json" ]; then
    echo "Copying devcontainer.json to TTA.prototype..."
    mkdir -p TTA.prototype/.devcontainer
    cp templates/TTA.prototype/.devcontainer/devcontainer.json TTA.prototype/.devcontainer/
fi

echo -e "${GREEN}Setup complete!${NC}"
echo "You can now use the TTA environment with Docker."
echo "To open a repository in VS Code with Docker support:"
echo "1. Open VS Code"
echo "2. Open either tta.dev or TTA.prototype folder"
echo "3. When prompted, click 'Reopen in Container'"
