#!/bin/bash

# Script to ensure proper volume sharing between TTA containers
# This script should be run after all containers are started

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Ensuring proper volume sharing between TTA containers...${NC}"
echo "=============================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if containers are running
if ! docker ps | grep -q "tta-root-app"; then
    echo -e "${YELLOW}Warning: TTA root container is not running. Please start it first.${NC}"
    exit 1
fi

# Create directories if they don't exist
echo "Creating necessary directories..."
mkdir -p data
mkdir -p tta.dev/.model_cache
mkdir -p TTA.prototype/ai_models

# Ensure proper permissions
echo "Setting proper permissions..."
chmod -R 777 data
chmod -R 777 tta.dev/.model_cache
chmod -R 777 TTA.prototype/ai_models

# Create symbolic links for shared volumes if needed
echo "Setting up symbolic links for shared volumes..."

# Link tta.dev models to TTA.prototype
if [ -d "tta.dev/.model_cache" ] && [ -d "TTA.prototype/ai_models" ]; then
    echo "Linking tta.dev models to TTA.prototype..."

    # Get container IDs
    ROOT_CONTAINER=$(docker ps -qf "name=tta-root-app")
    DEV_CONTAINER=$(docker ps -qf "name=tta-dev-app")
    PROTOTYPE_CONTAINER=$(docker ps -qf "name=tta-prototype-app")

    if [ -n "$ROOT_CONTAINER" ]; then
        echo "Root container is running."

        # Ensure the model cache directory exists in the root container
        docker exec $ROOT_CONTAINER mkdir -p /app/.model_cache

        # If dev container is running, copy models from dev to root
        if [ -n "$DEV_CONTAINER" ]; then
            echo "Dev container is running. Copying models from dev to root..."
            docker exec $DEV_CONTAINER bash -c "cp -r /app/.model_cache/* /app/external_data/models/ 2>/dev/null || true"
        fi

        # If prototype container is running, copy models from root to prototype
        if [ -n "$PROTOTYPE_CONTAINER" ]; then
            echo "Prototype container is running. Copying models from root to prototype..."
            docker exec $PROTOTYPE_CONTAINER bash -c "mkdir -p /app/ai_models && cp -r /app/external_data/models/* /app/ai_models/ 2>/dev/null || true"
        fi
    fi
else
    echo -e "${YELLOW}Warning: Model directories not found. Skipping model linking.${NC}"
fi

echo -e "${GREEN}Volume sharing setup complete!${NC}"
