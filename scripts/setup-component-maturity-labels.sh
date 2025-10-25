#!/bin/bash
# TTA Component Maturity Labels Setup Script
# Creates all labels needed for the component maturity promotion workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}TTA Component Maturity Labels Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to create label
create_label() {
    local name=$1
    local description=$2
    local color=$3

    if gh label create "$name" --description "$description" --color "$color" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Created label: $name"
    else
        echo -e "${YELLOW}⚠${NC} Label already exists: $name"
    fi
}

echo -e "${BLUE}Creating Component Labels...${NC}"

# Core Infrastructure Components
create_label "component:core-infrastructure" "Core Infrastructure functional group" "0E8A16"
create_label "component:neo4j" "Neo4j database component" "1D76DB"
create_label "component:redis" "Redis cache component" "DC382D"
create_label "component:docker" "Docker infrastructure component" "2496ED"
create_label "component:postgres" "PostgreSQL database component" "336791"

# AI/Agent Systems Components
create_label "component:ai-agent-systems" "AI/Agent Systems functional group" "5319E7"
create_label "component:agent-orchestration" "Agent orchestration component" "7057FF"
create_label "component:llm" "LLM service component" "8B5CF6"
create_label "component:model-management" "Model management component" "A78BFA"
create_label "component:narrative-arc-orchestrator" "Narrative arc orchestrator component" "C4B5FD"

# Player Experience Components
create_label "component:player-experience" "Player Experience functional group" "D93F0B"
create_label "component:player-experience-api" "Player Experience API component" "E99695"
create_label "component:player-experience-frontend" "Player Experience Frontend component" "FBCA04"
create_label "component:gameplay-loop" "Gameplay loop component" "FEF2C0"
create_label "component:session-management" "Session management component" "F9D0C4"
create_label "component:character-management" "Character management component" "C2E0C6"

# Therapeutic Content Components
create_label "component:therapeutic-content" "Therapeutic Content functional group" "0075CA"
create_label "component:therapeutic-systems" "Therapeutic systems component" "1F77B4"
create_label "component:narrative-coherence" "Narrative coherence component" "AEC7E8"
create_label "component:emotional-safety" "Emotional safety component" "FFBB78"
create_label "component:consequence-system" "Consequence system component" "98DF8A"

# Monitoring & Operations Components
create_label "component:monitoring-operations" "Monitoring & Operations functional group" "006B75"
create_label "component:monitoring" "Monitoring component" "0E8A16"
create_label "component:analytics" "Analytics component" "BFD4F2"
create_label "component:developer-dashboard" "Developer dashboard component" "D4C5F9"

echo ""
echo -e "${BLUE}Creating Target Environment Labels...${NC}"

create_label "target:staging" "Target environment: Staging" "FBCA04"
create_label "target:production" "Target environment: Production" "D93F0B"

echo ""
echo -e "${BLUE}Creating Promotion Workflow Labels...${NC}"

create_label "promotion:requested" "Promotion request submitted" "0075CA"
create_label "promotion:in-review" "Promotion request under review" "5319E7"
create_label "promotion:approved" "Promotion request approved" "0E8A16"
create_label "promotion:blocked" "Promotion blocked by issues" "D93F0B"
create_label "promotion:completed" "Promotion completed successfully" "1D76DB"

echo ""
echo -e "${BLUE}Creating Blocker Type Labels...${NC}"

create_label "blocker:tests" "Blocked by insufficient or failing tests" "B60205"
create_label "blocker:documentation" "Blocked by missing or incomplete documentation" "FFA500"
create_label "blocker:performance" "Blocked by performance issues" "FBCA04"
create_label "blocker:security" "Blocked by security vulnerabilities" "D93F0B"
create_label "blocker:dependencies" "Blocked by dependency issues" "8B5CF6"
create_label "blocker:integration" "Blocked by integration issues" "1D76DB"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Label Creation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  - Component Labels: 24"
echo "  - Target Environment Labels: 2"
echo "  - Promotion Workflow Labels: 5"
echo "  - Blocker Type Labels: 6"
echo "  - Total: 37 labels"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Create GitHub Project board (manual via GitHub UI)"
echo "  2. Create issue templates"
echo "  3. Create documentation"
echo ""
