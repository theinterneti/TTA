#!/bin/bash
# Rebuild TTA Player Frontend for Staging Environment
# This script ensures fresh builds by using cache-busting and proper cleanup

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TTA Frontend Staging Rebuild${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Navigate to project root
cd "$PROJECT_ROOT"

# Step 1: Stop the running container
echo -e "${YELLOW}Step 1: Stopping player-frontend-staging container...${NC}"
docker-compose -f docker-compose.staging-homelab.yml stop player-frontend-staging || true
echo -e "${GREEN}✓ Container stopped${NC}"
echo ""

# Step 2: Remove the container
echo -e "${YELLOW}Step 2: Removing player-frontend-staging container...${NC}"
docker-compose -f docker-compose.staging-homelab.yml rm -f player-frontend-staging || true
echo -e "${GREEN}✓ Container removed${NC}"
echo ""

# Step 3: Remove the image
echo -e "${YELLOW}Step 3: Removing old Docker image...${NC}"
docker rmi recovered-tta-storytelling-player-frontend-staging:latest 2>/dev/null || true
docker rmi $(docker images -q recovered-tta-storytelling-player-frontend-staging) 2>/dev/null || true
echo -e "${GREEN}✓ Old image removed${NC}"
echo ""

# Step 4: Prune build cache
echo -e "${YELLOW}Step 4: Pruning Docker build cache...${NC}"
docker builder prune -f
echo -e "${GREEN}✓ Build cache pruned${NC}"
echo ""

# Step 5: Build with cache-busting
echo -e "${YELLOW}Step 5: Building fresh image with cache-busting...${NC}"
CACHE_BUST=$(date +%s)
echo -e "Cache bust timestamp: ${CACHE_BUST}"
export CACHE_BUST
docker-compose -f docker-compose.staging-homelab.yml build --no-cache player-frontend-staging
echo -e "${GREEN}✓ Fresh image built${NC}"
echo ""

# Step 6: Start the container
echo -e "${YELLOW}Step 6: Starting player-frontend-staging container...${NC}"
docker-compose -f docker-compose.staging-homelab.yml up -d player-frontend-staging
echo -e "${GREEN}✓ Container started${NC}"
echo ""

# Step 7: Wait for container to be healthy
echo -e "${YELLOW}Step 7: Waiting for container to be healthy...${NC}"
MAX_WAIT=60
WAIT_COUNT=0
while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    HEALTH=$(docker inspect --format='{{.State.Health.Status}}' tta-staging-player-frontend 2>/dev/null || echo "starting")
    if [ "$HEALTH" = "healthy" ]; then
        echo -e "${GREEN}✓ Container is healthy${NC}"
        break
    fi
    echo -n "."
    sleep 2
    WAIT_COUNT=$((WAIT_COUNT + 2))
done
echo ""

if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
    echo -e "${RED}⚠ Warning: Container did not become healthy within ${MAX_WAIT}s${NC}"
    echo -e "${YELLOW}Checking container logs:${NC}"
    docker logs tta-staging-player-frontend --tail 50
else
    echo -e "${GREEN}✓ Container is running and healthy${NC}"
fi
echo ""

# Step 8: Verify deployment
echo -e "${YELLOW}Step 8: Verifying deployment...${NC}"
echo -e "Testing frontend endpoint..."
if curl -f -s http://localhost:3001/ > /dev/null; then
    echo -e "${GREEN}✓ Frontend is accessible at http://localhost:3001${NC}"
else
    echo -e "${RED}✗ Frontend is not accessible${NC}"
    echo -e "${YELLOW}Container logs:${NC}"
    docker logs tta-staging-player-frontend --tail 50
    exit 1
fi
echo ""

# Step 9: Display build info
echo -e "${YELLOW}Step 9: Build information...${NC}"
docker exec tta-staging-player-frontend cat /usr/share/nginx/html/config.js 2>/dev/null || echo "No config.js found"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Frontend Rebuild Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Frontend URL: ${GREEN}http://localhost:3001${NC}"
echo -e "Cache Bust: ${GREEN}${CACHE_BUST}${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Clear your browser cache (Ctrl+Shift+R or Cmd+Shift+R)"
echo -e "2. Navigate to http://localhost:3001"
echo -e "3. Verify that your changes are reflected"
echo ""

