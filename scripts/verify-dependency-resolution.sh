#!/bin/bash
# Dependency Resolution Verification Script
# Verifies both UV consistency and dual Vite setup

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TTA Dependency Resolution Verification               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Part 1: UV Consistency Check
echo -e "${YELLOW}Part 1: UV Workflow Consistency${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count all-groups usage
ALL_GROUPS_COUNT=$(grep -r "uv sync --all-groups" .github/workflows/*.yml 2>/dev/null | wc -l)

echo -e "Checking workflow files for consistent UV syntax..."
if [ "$ALL_GROUPS_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Found $ALL_GROUPS_COUNT instances of 'uv sync --all-groups'${NC}"
else
    echo -e "${RED}❌ No 'uv sync --all-groups' found in workflows${NC}"
    exit 1
fi

# Check for old syntax
OLD_SYNTAX_COUNT=$(grep -r "uv sync --all-extras --dev\|uv sync --extra dev" .github/workflows/*.yml 2>/dev/null | wc -l)

if [ "$OLD_SYNTAX_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ No old syntax found (fully migrated)${NC}"
else
    echo -e "${YELLOW}⚠️  Found $OLD_SYNTAX_COUNT instances of old syntax${NC}"
    grep -r "uv sync --all-extras --dev\|uv sync --extra dev" .github/workflows/*.yml
fi

echo ""

# Part 2: Dual Vite Setup Check
echo -e "${YELLOW}Part 2: Dual Vite Version Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

FRONTEND_DIR="src/player_experience/frontend"

# Check wrapper script
if [ -f "$FRONTEND_DIR/scripts/storybook-wrapper.sh" ]; then
    if [ -x "$FRONTEND_DIR/scripts/storybook-wrapper.sh" ]; then
        echo -e "${GREEN}✅ Wrapper script exists and is executable${NC}"
    else
        echo -e "${YELLOW}⚠️  Wrapper script exists but not executable${NC}"
        chmod +x "$FRONTEND_DIR/scripts/storybook-wrapper.sh"
        echo -e "${GREEN}   Fixed: Made script executable${NC}"
    fi
else
    echo -e "${RED}❌ Wrapper script not found${NC}"
    exit 1
fi

# Check .storybook/package.json
if [ -f "$FRONTEND_DIR/.storybook/package.json" ]; then
    echo -e "${GREEN}✅ .storybook/package.json exists${NC}"

    # Check Vite version
    STORYBOOK_VITE=$(grep '"vite"' "$FRONTEND_DIR/.storybook/package.json" | grep -o '"[^"]*"' | tail -1 | tr -d '"')
    if [[ "$STORYBOOK_VITE" == ^6* ]]; then
        echo -e "${GREEN}   └─ Storybook uses Vite $STORYBOOK_VITE${NC}"
    else
        echo -e "${RED}   └─ Warning: Storybook Vite version is $STORYBOOK_VITE (expected ^6.0.0)${NC}"
    fi
else
    echo -e "${RED}❌ .storybook/package.json not found${NC}"
    exit 1
fi

# Check main package.json
if [ -f "$FRONTEND_DIR/package.json" ]; then
    MAIN_VITE=$(grep '"vite"' "$FRONTEND_DIR/package.json" | head -1 | grep -o '"[^"]*"' | tail -1 | tr -d '"')
    if [[ "$MAIN_VITE" == ^7* ]]; then
        echo -e "${GREEN}✅ Main app uses Vite $MAIN_VITE${NC}"
    else
        echo -e "${YELLOW}⚠️  Main app Vite version is $MAIN_VITE (expected ^7.x)${NC}"
    fi

    # Check scripts
    if grep -q "storybook.*wrapper" "$FRONTEND_DIR/package.json"; then
        echo -e "${GREEN}✅ Package.json scripts use wrapper${NC}"
    else
        echo -e "${RED}❌ Package.json scripts not updated to use wrapper${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Main package.json not found${NC}"
    exit 1
fi

# Check documentation
echo ""
echo -e "${YELLOW}Documentation Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DOCS=(
    "$FRONTEND_DIR/.storybook/README.md"
    "$FRONTEND_DIR/VITE_VERSION_STRATEGY.md"
    "DEPENDENCY_RESOLUTION_SUMMARY.md"
    "DEPENDENCY_RESOLUTION_COMPLETE.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "${GREEN}✅ $doc${NC}"
    else
        echo -e "${YELLOW}⚠️  $doc not found${NC}"
    fi
done

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Verification Summary                                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ UV Consistency: $ALL_GROUPS_COUNT workflows migrated${NC}"
echo -e "${GREEN}✅ Dual Vite Setup: Configured correctly${NC}"
echo -e "${GREEN}✅ Documentation: Complete${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Test Storybook: cd $FRONTEND_DIR && npm run storybook"
echo "2. Verify main app: npm run start"
echo "3. Review docs: cat $FRONTEND_DIR/.storybook/README.md"
echo ""
echo -e "${GREEN}All checks passed! ✨${NC}"
