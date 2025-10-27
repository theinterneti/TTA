#!/bin/bash
# TTA Component GitHub Project Population Script
# Adds all components to the GitHub Project board

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}TTA Component GitHub Project Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${YELLOW}Note: This script provides instructions for adding components to the GitHub Project.${NC}"
echo -e "${YELLOW}GitHub Projects (new) must be managed via the web UI.${NC}"
echo ""

echo -e "${BLUE}Step 1: Create the GitHub Project${NC}"
echo "  1. Go to: https://github.com/users/theinterneti/projects"
echo "  2. Click 'New project'"
echo "  3. Name: 'TTA Component Maturity Tracker'"
echo "  4. Follow the guide in: docs/development/GITHUB_PROJECT_SETUP.md"
echo ""
read -p "Press Enter when the project is created..."

echo ""
echo -e "${BLUE}Step 2: Get Project URL${NC}"
echo "  1. Navigate to your new project"
echo "  2. Copy the project URL (e.g., https://github.com/users/theinterneti/projects/1)"
echo ""
read -p "Enter the project URL: " PROJECT_URL

if [ -z "$PROJECT_URL" ]; then
    echo -e "${RED}Error: Project URL is required${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 3: Component List${NC}"
echo ""
echo "The following components should be added to the project:"
echo ""

# Core Infrastructure
echo -e "${GREEN}Core Infrastructure:${NC}"
echo "  1. Neo4j (Development)"
echo "  2. Docker (Development)"
echo "  3. Carbon (Development)"
echo ""

# AI/Agent Systems
echo -e "${GREEN}AI/Agent Systems:${NC}"
echo "  4. Model Management (Development)"
echo "  5. LLM (Development)"
echo "  6. Agent Orchestration (Development)"
echo "  7. Narrative Arc Orchestrator (Development)"
echo ""

# Player Experience
echo -e "${GREEN}Player Experience:${NC}"
echo "  8. Gameplay Loop (Development)"
echo "  9. Character Arc Manager (Development)"
echo "  10. Player Experience (Development)"
echo ""

# Therapeutic Content
echo -e "${GREEN}Therapeutic Content:${NC}"
echo "  11. Narrative Coherence (Development)"
echo "  12. Therapeutic Systems (Development)"
echo ""

echo -e "${BLUE}Step 4: Add Components to Project${NC}"
echo ""
echo "For each component above:"
echo "  1. Navigate to: $PROJECT_URL"
echo "  2. Click '+ Add item' at the bottom of the 'Development' column"
echo "  3. Create a draft item with the component name"
echo "  4. Set the custom fields:"
echo "     - Functional Group: [Core Infrastructure|AI/Agent Systems|Player Experience|Therapeutic Content]"
echo "     - Current Stage: Development"
echo "     - Target Stage: Staging"
echo "     - Promotion Blocker Count: 0"
echo "     - Test Coverage: 0%"
echo "     - Last Updated: $(date +%Y-%m-%d)"
echo "     - Owner: theinterneti"
echo "     - Priority: [High|Medium|Low]"
echo "     - Dependencies: [List dependencies]"
echo ""

echo -e "${BLUE}Step 5: Create Promotion Milestones${NC}"
echo ""
echo "Create the following milestones in the repository:"
echo ""

# Function to create milestone
create_milestone() {
    local title=$1
    local description=$2
    local due_date=$3

    echo -e "${BLUE}Creating milestone: $title${NC}"

    if gh api repos/theinterneti/TTA/milestones \
        -X POST \
        -f title="$title" \
        -f description="$description" \
        -f due_on="$due_date" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Created milestone: $title"
    else
        echo -e "${YELLOW}⚠${NC} Milestone may already exist or creation failed: $title"
    fi
}

echo -e "${BLUE}Creating promotion milestones...${NC}"
echo ""

# Calculate dates (2 weeks from now for first milestone)
MILESTONE_1_DATE=$(date -d "+2 weeks" +%Y-%m-%dT23:59:59Z)
MILESTONE_2_DATE=$(date -d "+4 weeks" +%Y-%m-%dT23:59:59Z)
MILESTONE_3_DATE=$(date -d "+6 weeks" +%Y-%m-%dT23:59:59Z)
MILESTONE_4_DATE=$(date -d "+8 weeks" +%Y-%m-%dT23:59:59Z)

create_milestone \
    "Phase 1: Core Infrastructure → Staging" \
    "Promote core infrastructure components (Neo4j, Docker, Carbon) to staging environment" \
    "$MILESTONE_1_DATE"

create_milestone \
    "Phase 2: AI/Agent Systems → Staging" \
    "Promote AI/Agent systems components (Model Management, LLM, Agent Orchestration, Narrative Arc Orchestrator) to staging environment" \
    "$MILESTONE_2_DATE"

create_milestone \
    "Phase 3: Player Experience → Staging" \
    "Promote player experience components (Gameplay Loop, Character Arc Manager, Player Experience) to staging environment" \
    "$MILESTONE_3_DATE"

create_milestone \
    "Phase 4: Therapeutic Content → Staging" \
    "Promote therapeutic content components (Narrative Coherence, Therapeutic Systems) to staging environment" \
    "$MILESTONE_4_DATE"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GitHub Project Setup Instructions Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  - Project URL: $PROJECT_URL"
echo "  - Components to add: 12"
echo "  - Milestones created: 4"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Add all 12 components to the project board"
echo "  2. Configure custom fields for each component"
echo "  3. Review component MATURITY.md files"
echo "  4. Begin Phase 1: Core Infrastructure promotion"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  - GitHub Project Setup: docs/development/GITHUB_PROJECT_SETUP.md"
echo "  - Component Inventory: docs/development/COMPONENT_INVENTORY.md"
echo "  - Component Maturity Workflow: docs/development/COMPONENT_MATURITY_WORKFLOW.md"
echo ""
