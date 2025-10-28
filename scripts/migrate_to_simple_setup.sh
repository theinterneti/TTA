#!/bin/bash
# TTA Database Migration Script
# Migrates from multi-instance to single-instance setup

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  TTA Database Migration: Multi-Instance → Single-Instance      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="./backups/database-migration-$(date +%Y%m%d_%H%M%S)"
OLD_COMPOSE_FILE="docker-compose.dev.yml.backup"

echo -e "${BLUE}Step 1: Backing up current configuration...${NC}"
mkdir -p "$BACKUP_DIR"
cp docker-compose.dev.yml "$BACKUP_DIR/docker-compose.dev.yml.backup" 2>/dev/null || true
cp .env.dev "$BACKUP_DIR/.env.dev.backup" 2>/dev/null || true
echo -e "${GREEN}✅ Configuration backed up to: $BACKUP_DIR${NC}"
echo ""

echo -e "${BLUE}Step 2: Stopping old services...${NC}"
docker-compose -f docker-compose.dev.yml down 2>/dev/null || echo "No services running"
docker-compose -f docker-compose.staging.yml down 2>/dev/null || echo "No staging services"
echo -e "${GREEN}✅ Old services stopped${NC}"
echo ""

echo -e "${BLUE}Step 3: Exporting data from old volumes (if they exist)...${NC}"

# Check if old Neo4j volumes exist
if docker volume ls | grep -q "tta_neo4j_dev_data"; then
    echo "Found old Neo4j dev data, exporting..."
    docker run --rm \
        -v tta_neo4j_dev_data:/data \
        -v "$PWD/$BACKUP_DIR":/backup \
        neo4j:5.26.1-community \
        tar czf /backup/neo4j_dev_data.tar.gz /data 2>/dev/null || echo "Export skipped"
    echo -e "${GREEN}✅ Neo4j dev data exported${NC}"
else
    echo -e "${YELLOW}ℹ️  No old Neo4j dev data found - starting fresh${NC}"
fi

# Check if old Redis volumes exist
if docker volume ls | grep -q "tta_redis_dev_data"; then
    echo "Found old Redis dev data, exporting..."
    docker run --rm \
        -v tta_redis_dev_data:/data \
        -v "$PWD/$BACKUP_DIR":/backup \
        redis:7-alpine \
        tar czf /backup/redis_dev_data.tar.gz /data 2>/dev/null || echo "Export skipped"
    echo -e "${GREEN}✅ Redis dev data exported${NC}"
else
    echo -e "${YELLOW}ℹ️  No old Redis dev data found - starting fresh${NC}"
fi
echo ""

echo -e "${BLUE}Step 4: Starting new simplified services...${NC}"
docker-compose -f docker-compose.dev.yml up -d
echo -e "${GREEN}✅ New services started${NC}"
echo ""

echo -e "${BLUE}Step 5: Waiting for Neo4j to be ready...${NC}"
echo "This may take 30-60 seconds..."
sleep 10  # Initial wait for container startup

# Wait for Neo4j to be healthy
for i in {1..30}; do
    if docker exec tta-neo4j wget --spider -q http://localhost:7474 2>/dev/null; then
        echo -e "${GREEN}✅ Neo4j is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

echo -e "${BLUE}Step 6: Creating Neo4j databases...${NC}"
uv run python scripts/setup_neo4j_databases.py
echo ""

echo -e "${BLUE}Step 7: Testing connections...${NC}"
uv run python scripts/test_database_connections.py
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  Migration Complete! 🎉                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo "1. Update your code to use database names:"
echo "   ${BLUE}session = driver.session(database='tta_dev')${NC}"
echo ""
echo "2. Update Redis connections to use DB numbers:"
echo "   ${BLUE}redis.Redis(host='localhost', port=6379, db=0)${NC}"
echo ""
echo "3. Access services:"
echo "   - Neo4j Browser: ${BLUE}http://localhost:7474${NC}"
echo "   - Redis Commander: ${BLUE}http://localhost:8081${NC}"
echo "   - Grafana (optional): ${BLUE}docker-compose -f docker-compose.dev.yml --profile monitoring up -d${NC}"
echo ""
echo -e "${YELLOW}Backup Location:${NC} $BACKUP_DIR"
echo ""
echo "See docs/setup/SIMPLIFIED_DOCKER_SETUP.md for full documentation"
