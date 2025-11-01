#!/bin/bash
# Verification Script for Priority 2: Frontend Deployment Fix

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PRIORITY 2 VERIFICATION: Frontend Deployment Fix${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Test 1: Verify Dockerfile uses correct build directory
echo -e "${YELLOW}TEST 1: Verify Dockerfile copies from correct build directory${NC}"
if grep -q "COPY --from=builder /app/build /usr/share/nginx/html" src/player_experience/frontend/Dockerfile.staging; then
    echo -e "${GREEN}✓ PASS: Dockerfile copies from /app/build (correct for CRA)${NC}"
    TEST1=true
else
    echo -e "${RED}✗ FAIL: Dockerfile still copies from wrong directory${NC}"
    TEST1=false
fi
echo ""

# Test 2: Verify Dockerfile uses correct build command
echo -e "${YELLOW}TEST 2: Verify Dockerfile uses correct build command${NC}"
if grep -q "RUN yarn build$" src/player_experience/frontend/Dockerfile.staging; then
    echo -e "${GREEN}✓ PASS: Dockerfile uses 'yarn build' command${NC}"
    TEST2=true
else
    echo -e "${RED}✗ FAIL: Dockerfile uses incorrect build command${NC}"
    TEST2=false
fi
echo ""

# Test 3: Verify cache-busting mechanism exists
echo -e "${YELLOW}TEST 3: Verify cache-busting mechanism in Dockerfile${NC}"
if grep -q "ARG CACHE_BUST" src/player_experience/frontend/Dockerfile.staging; then
    echo -e "${GREEN}✓ PASS: CACHE_BUST argument present in Dockerfile${NC}"
    TEST3=true
else
    echo -e "${RED}✗ FAIL: CACHE_BUST argument missing${NC}"
    TEST3=false
fi
echo ""

# Test 4: Verify docker-compose has CACHE_BUST build arg
echo -e "${YELLOW}TEST 4: Verify docker-compose.staging-homelab.yml has CACHE_BUST${NC}"
if grep -q "CACHE_BUST:" docker-compose.staging-homelab.yml; then
    echo -e "${GREEN}✓ PASS: CACHE_BUST build argument in docker-compose${NC}"
    TEST4=true
else
    echo -e "${RED}✗ FAIL: CACHE_BUST missing from docker-compose${NC}"
    TEST4=false
fi
echo ""

# Test 5: Verify nginx cache headers for index.html
echo -e "${YELLOW}TEST 5: Verify nginx cache headers prevent index.html caching${NC}"
if grep -q "location = /index.html" src/player_experience/frontend/Dockerfile.staging; then
    echo -e "${GREEN}✓ PASS: Nginx has specific location block for index.html${NC}"
    if grep -A 3 "location = /index.html" src/player_experience/frontend/Dockerfile.staging | grep -q "no-cache"; then
        echo -e "${GREEN}✓ PASS: index.html has no-cache headers${NC}"
        TEST5=true
    else
        echo -e "${RED}✗ FAIL: index.html location block missing no-cache headers${NC}"
        TEST5=false
    fi
else
    echo -e "${RED}✗ FAIL: No specific nginx location block for index.html${NC}"
    TEST5=false
fi
echo ""

# Test 6: Verify build script exists
echo -e "${YELLOW}TEST 6: Verify 'yarn build' script exists in package.json${NC}"
if grep -q '"build":' src/player_experience/frontend/package.json; then
    echo -e "${GREEN}✓ PASS: 'build' script exists in package.json${NC}"
    TEST6=true
else
    echo -e "${RED}✗ FAIL: 'build' script missing from package.json${NC}"
    TEST6=false
fi
echo ""

# Test 7: Verify rebuild script exists and is executable
echo -e "${YELLOW}TEST 7: Verify automated rebuild script exists${NC}"
if [ -f "scripts/rebuild-frontend-staging.sh" ]; then
    echo -e "${GREEN}✓ PASS: rebuild-frontend-staging.sh exists${NC}"
    if [ -x "scripts/rebuild-frontend-staging.sh" ]; then
        echo -e "${GREEN}✓ PASS: rebuild-frontend-staging.sh is executable${NC}"
        TEST7=true
    else
        echo -e "${RED}✗ FAIL: rebuild-frontend-staging.sh is not executable${NC}"
        TEST7=false
    fi
else
    echo -e "${RED}✗ FAIL: rebuild-frontend-staging.sh does not exist${NC}"
    TEST7=false
fi
echo ""

# Test 8: Verify documentation exists
echo -e "${YELLOW}TEST 8: Verify deployment fix documentation exists${NC}"
if [ -f "docs/FRONTEND_DEPLOYMENT_FIX.md" ]; then
    echo -e "${GREEN}✓ PASS: FRONTEND_DEPLOYMENT_FIX.md exists${NC}"
    TEST8=true
else
    echo -e "${RED}✗ FAIL: FRONTEND_DEPLOYMENT_FIX.md does not exist${NC}"
    TEST8=false
fi
echo ""

# Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}VERIFICATION SUMMARY${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

ALL_PASSED=true
[ "$TEST1" = true ] && echo -e "${GREEN}✅ PASS: Build directory fix${NC}" || { echo -e "${RED}❌ FAIL: Build directory fix${NC}"; ALL_PASSED=false; }
[ "$TEST2" = true ] && echo -e "${GREEN}✅ PASS: Build command fix${NC}" || { echo -e "${RED}❌ FAIL: Build command fix${NC}"; ALL_PASSED=false; }
[ "$TEST3" = true ] && echo -e "${GREEN}✅ PASS: Cache-busting in Dockerfile${NC}" || { echo -e "${RED}❌ FAIL: Cache-busting in Dockerfile${NC}"; ALL_PASSED=false; }
[ "$TEST4" = true ] && echo -e "${GREEN}✅ PASS: Cache-busting in docker-compose${NC}" || { echo -e "${RED}❌ FAIL: Cache-busting in docker-compose${NC}"; ALL_PASSED=false; }
[ "$TEST5" = true ] && echo -e "${GREEN}✅ PASS: Nginx cache headers${NC}" || { echo -e "${RED}❌ FAIL: Nginx cache headers${NC}"; ALL_PASSED=false; }
[ "$TEST6" = true ] && echo -e "${GREEN}✅ PASS: Build script exists${NC}" || { echo -e "${RED}❌ FAIL: Build script exists${NC}"; ALL_PASSED=false; }
[ "$TEST7" = true ] && echo -e "${GREEN}✅ PASS: Rebuild script${NC}" || { echo -e "${RED}❌ FAIL: Rebuild script${NC}"; ALL_PASSED=false; }
[ "$TEST8" = true ] && echo -e "${GREEN}✅ PASS: Documentation${NC}" || { echo -e "${RED}❌ FAIL: Documentation${NC}"; ALL_PASSED=false; }

echo ""
echo -e "${GREEN}========================================${NC}"
if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED - Priority 2 Fix Verified${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED - Review output above${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 1
fi
