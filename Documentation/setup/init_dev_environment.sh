#!/bin/bash
# TTA Development Environment Initialization Script
set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}TTA Development Environment Initialization Script${NC}"
echo "=============================="
# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker and try again.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose and try again.${NC}"
    exit 1
fi
# Initialize and update submodules
echo -e "${GREEN}Initializing and updating submodules...${NC}"
git submodule update --init --recursive

# Copy Docker configuration files if they don't exist in submodules
echo -e "${GREEN}Checking Docker configuration files...${NC}"
# For tta.dev
if [ ! -f "tta.dev/docker-compose.yml" ]; then
    echo "Copying docker-compose.yml to tta.dev..."
    cp templates/tta.dev/docker-compose.yml tta.dev
fi

if [ ! -f "tta.dev/Dockerfile" ]; then
    echo "Copying Dockerfile to tta.dev..."
    cp templates/tta.dev/Dockerfile tta.dev/
fi
# For TTA.prototype
if [ ! -f "TTA.prototype/docker-compose.yml" ]; then
    echo "Copying docker-compose.yml to TTA.prototype..."
    cp templates/TTA.prototype/docker-compose.yml TTA.prototype
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
# Build and start Docker containers
echo -e "${GREEN}Building and starting Docker containers...${NC}"
docker-compose -f tta.dev/docker-compose.yml up -d --build
docker-compose -f TTA.prototype/docker-compose.yml up -d --build

echo -e "${GREEN}Development environment initialization complete!${NC}"
echo "You can now use the TTA development environment with Docker."
echo "To open a repository in VS Code with Docker support:"
echo "1. Open VS Code"
echo "2. Open either tta.dev or TTA.prototype folder"
echo "3. When prompted, click 'Reopen in Container'"
