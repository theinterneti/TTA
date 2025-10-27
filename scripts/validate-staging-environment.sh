#!/bin/bash

# =============================================================================
# TTA Staging Environment Validation Script
# =============================================================================
# This script validates that the staging environment is ready for E2E testing
#
# Usage:
#   ./scripts/validate-staging-environment.sh
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_URL="${STAGING_BASE_URL:-http://localhost:3001}"
API_URL="${STAGING_API_URL:-http://localhost:8081}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6380}"
NEO4J_HOST="${NEO4J_HOST:-localhost}"
NEO4J_PORT="${NEO4J_PORT:-7688}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5433}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TTA Staging Environment Validation                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if a service is running
check_service() {
    local name=$1
    local host=$2
    local port=$3

    echo -n "Checking $name ($host:$port)... "

    if timeout 5 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not accessible${NC}"
        return 1
    fi
}

# Function to check HTTP endpoint
check_http() {
    local name=$1
    local url=$2

    echo -n "Checking $name ($url)... "

    if curl -s -f -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✓ Accessible${NC}"
        return 0
    else
        echo -e "${RED}✗ Not accessible${NC}"
        return 1
    fi
}

# Track failures
FAILURES=0

echo -e "${YELLOW}📊 Checking Core Services${NC}"
echo ""

# Check Frontend
if check_http "Frontend" "$FRONTEND_URL"; then
    :
else
    ((FAILURES++))
fi

# Check API
if check_http "API Health" "$API_URL/health"; then
    :
else
    ((FAILURES++))
fi

# Check API Docs
if check_http "API Docs" "$API_URL/docs"; then
    :
else
    echo -e "${YELLOW}  ⚠ API docs not accessible (non-critical)${NC}"
fi

echo ""
echo -e "${YELLOW}📊 Checking Database Services${NC}"
echo ""

# Check Redis
if check_service "Redis" "$REDIS_HOST" "$REDIS_PORT"; then
    :
else
    ((FAILURES++))
fi

# Check Neo4j
if check_service "Neo4j" "$NEO4J_HOST" "$NEO4J_PORT"; then
    :
else
    ((FAILURES++))
fi

# Check PostgreSQL
if check_service "PostgreSQL" "$POSTGRES_HOST" "$POSTGRES_PORT"; then
    :
else
    ((FAILURES++))
fi

echo ""
echo -e "${YELLOW}📊 Checking Docker Containers${NC}"
echo ""

# Check if docker-compose is running
if docker-compose -f docker-compose.staging-homelab.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Docker containers are running${NC}"

    # Show container status
    echo ""
    echo "Container Status:"
    docker-compose -f docker-compose.staging-homelab.yml ps --format "table {{.Name}}\t{{.Status}}"
else
    echo -e "${RED}✗ Docker containers not running${NC}"
    ((FAILURES++))
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"

if [ $FAILURES -eq 0 ]; then
    echo -e "${BLUE}║  ${GREEN}✅ All checks passed! Staging environment is ready.${BLUE}      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}🚀 You can now run Playwright tests:${NC}"
    echo -e "   ${BLUE}npm run test:staging${NC}"
    echo ""
    exit 0
else
    echo -e "${BLUE}║  ${RED}❌ $FAILURES check(s) failed!${BLUE}                                  ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}💡 To start the staging environment:${NC}"
    echo -e "   ${BLUE}docker-compose -f docker-compose.staging-homelab.yml up -d${NC}"
    echo ""
    echo -e "${YELLOW}💡 To check logs:${NC}"
    echo -e "   ${BLUE}docker-compose -f docker-compose.staging-homelab.yml logs -f${NC}"
    echo ""
    exit 1
fi
