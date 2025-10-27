#!/bin/bash
# Validate Agentic Primitives Structure
# This script validates that both .github/ and .augment/ structures are properly configured

set -e

echo "🔍 Validating Agentic Primitives Structure..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track validation status
ERRORS=0
WARNINGS=0

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Found: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Missing: $1"
        ((ERRORS++))
        return 1
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} Found: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Missing: $1"
        ((ERRORS++))
        return 1
    fi
}

# Function to check YAML frontmatter
check_yaml_frontmatter() {
    if head -n 1 "$1" | grep -q "^---$"; then
        echo -e "${GREEN}✓${NC} YAML frontmatter: $1"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} No YAML frontmatter: $1"
        ((WARNINGS++))
        return 1
    fi
}

echo "📁 Checking Root-Level Files..."
check_file "apm.yml"
check_file "AGENTS.md"
check_file "CLAUDE.md"
check_file "GEMINI.md"
check_file ".github/copilot-instructions.md"
echo ""

echo "📁 Checking .github/ Structure..."
check_dir ".github/instructions"
check_dir ".github/chatmodes"
check_dir ".github/prompts"
check_dir ".github/specs"
echo ""

echo "📄 Checking Instruction Files..."
check_file ".github/instructions/safety.instructions.md"
check_file ".github/instructions/graph-db.instructions.md"
check_file ".github/instructions/testing-battery.instructions.md"
echo ""

echo "📄 Checking Chat Mode Files..."
check_file ".github/chatmodes/safety-architect.chatmode.md"
check_file ".github/chatmodes/backend-implementer.chatmode.md"
echo ""

echo "📄 Checking Workflow Files..."
check_file ".github/prompts/narrative-creation.prompt.md"
echo ""

echo "📄 Checking Specification Templates..."
check_file ".github/specs/therapeutic-feature.spec.md"
check_file ".github/specs/api-endpoint.spec.md"
echo ""

echo "📁 Checking .augment/ Structure (Legacy)..."
check_dir ".augment/chatmodes"
check_dir ".augment/context"
check_dir ".augment/docs"
check_dir ".augment/instructions"
check_dir ".augment/memory"
check_dir ".augment/rules"
check_dir ".augment/workflows"
echo ""

echo "🔍 Validating YAML Frontmatter..."
for file in .github/instructions/*.instructions.md; do
    if [ -f "$file" ]; then
        check_yaml_frontmatter "$file"
    fi
done

for file in .github/chatmodes/*.chatmode.md; do
    if [ -f "$file" ]; then
        check_yaml_frontmatter "$file"
    fi
done

for file in .github/prompts/*.prompt.md; do
    if [ -f "$file" ]; then
        check_yaml_frontmatter "$file"
    fi
done

for file in .github/specs/*.spec.md; do
    if [ -f "$file" ]; then
        check_yaml_frontmatter "$file"
    fi
done
echo ""

echo "📊 Validation Summary"
echo "===================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "✅ Agentic primitives structure is valid"
    echo "✅ Both .github/ and .augment/ structures are present"
    echo "✅ All required files exist"
    echo "✅ YAML frontmatter is present in all files"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validation completed with warnings${NC}"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "⚠️  Some files are missing YAML frontmatter"
    echo "⚠️  This may affect selective context loading"
    exit 0
else
    echo -e "${RED}✗ Validation failed${NC}"
    echo "Errors: $ERRORS"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "❌ Some required files or directories are missing"
    echo "❌ Please review the migration guide: AGENTIC_PRIMITIVES_MIGRATION.md"
    exit 1
fi
