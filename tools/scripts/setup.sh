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
if [ ! -f ".gitmodules" ] || [ ! -d "tta.dev/.git" ] || [ ! -d "tta.prototype/.git" ]; then
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

    if [ -d "tta.prototype" ]; then
        echo "tta.prototype directory exists but is not a submodule."
        echo -e "${YELLOW}Would you like to backup and replace it? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            mv tta.prototype tta.prototype.bak
            echo "Backed up to tta.prototype.bak"
        else
            echo "Skipping tta.prototype submodule initialization."
        fi
    fi

    # Initialize submodules
    if [ ! -d "tta.dev" ]; then
        echo "Initializing tta.dev submodule..."
        git submodule add https://github.com/theinterneti/tta.dev.git tta.dev
    fi

    if [ ! -d "tta.prototype" ]; then
        echo "Initializing tta.prototype submodule..."
        git submodule add https://github.com/theinterneti/tta.prototype.git tta.prototype
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

# For tta.prototype
if [ ! -f "tta.prototype/docker-compose.yml" ]; then
    echo "Copying docker-compose.yml to tta.prototype..."
    cp templates/tta.prototype/docker-compose.yml tta.prototype/
fi

if [ ! -f "tta.prototype/Dockerfile" ]; then
    echo "Copying Dockerfile to tta.prototype..."
    cp templates/tta.prototype/Dockerfile tta.prototype/
fi

if [ ! -f "tta.prototype/.devcontainer/devcontainer.json" ]; then
    echo "Copying devcontainer.json to tta.prototype..."
    mkdir -p tta.prototype/.devcontainer
    cp templates/tta.prototype/.devcontainer/devcontainer.json tta.prototype/.devcontainer/
fi

echo -e "${GREEN}Setup complete!${NC}"
echo "You can now use the TTA environment with Docker."
echo "To open a repository in VS Code with Docker support:"
echo "1. Open VS Code"
echo "2. Open either tta.dev or tta.prototype folder"
echo "3. When prompted, click 'Reopen in Container'"
