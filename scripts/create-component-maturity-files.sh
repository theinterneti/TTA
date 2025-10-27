#!/bin/bash
# TTA Component Maturity Files Creation Script
# Creates MATURITY.md files for all existing components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}TTA Component Maturity Files Creation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Template file
TEMPLATE="src/components/MATURITY.md.template"

if [ ! -f "$TEMPLATE" ]; then
    echo -e "${RED}Error: Template file not found: $TEMPLATE${NC}"
    exit 1
fi

# Function to create MATURITY.md for a component
create_maturity_file() {
    local component_name=$1
    local component_dir=$2
    local functional_group=$3
    local current_stage=$4
    local owner=$5

    local maturity_file="$component_dir/MATURITY.md"

    if [ -f "$maturity_file" ]; then
        echo -e "${YELLOW}⚠${NC} MATURITY.md already exists for $component_name, skipping"
        return
    fi

    # Copy template and customize
    cp "$TEMPLATE" "$maturity_file"

    # Replace placeholders (using different delimiter to avoid issues with /)
    sed -i "s|<Component Name>|$component_name|g" "$maturity_file"
    sed -i "s|<Development\|Staging\|Production>|$current_stage|g" "$maturity_file"
    sed -i "s|<YYYY-MM-DD>|$(date +%Y-%m-%d)|g" "$maturity_file"
    sed -i "s|<GitHub Username>|$owner|g" "$maturity_file"
    sed -i "s|<Core Infrastructure\|AI/Agent Systems\|Player Experience\|Therapeutic Content\|Monitoring & Operations>|$functional_group|g" "$maturity_file"

    echo -e "${GREEN}✓${NC} Created MATURITY.md for $component_name"
}

echo -e "${BLUE}Creating MATURITY.md files for components...${NC}"
echo ""

# Core Infrastructure Components
echo -e "${BLUE}Core Infrastructure Components:${NC}"
create_maturity_file "Neo4j" "src/components" "Core Infrastructure" "Development" "theinterneti"
create_maturity_file "Docker" "src/components" "Core Infrastructure" "Development" "theinterneti"
create_maturity_file "Carbon" "src/components" "Core Infrastructure" "Development" "theinterneti"

# AI/Agent Systems Components
echo ""
echo -e "${BLUE}AI/Agent Systems Components:${NC}"
create_maturity_file "Agent Orchestration" "src/components" "AI/Agent Systems" "Development" "theinterneti"
create_maturity_file "LLM" "src/components" "AI/Agent Systems" "Development" "theinterneti"
create_maturity_file "Model Management" "src/components/model_management" "AI/Agent Systems" "Development" "theinterneti"
create_maturity_file "Narrative Arc Orchestrator" "src/components/narrative_arc_orchestrator" "AI/Agent Systems" "Development" "theinterneti"

# Player Experience Components
echo ""
echo -e "${BLUE}Player Experience Components:${NC}"
create_maturity_file "Player Experience" "src/components" "Player Experience" "Development" "theinterneti"
create_maturity_file "Gameplay Loop" "src/components/gameplay_loop" "Player Experience" "Development" "theinterneti"
create_maturity_file "Character Arc Manager" "src/components" "Player Experience" "Development" "theinterneti"

# Therapeutic Content Components
echo ""
echo -e "${BLUE}Therapeutic Content Components:${NC}"
create_maturity_file "Therapeutic Systems" "src/components/therapeutic_systems_enhanced" "Therapeutic Content" "Development" "theinterneti"
create_maturity_file "Narrative Coherence" "src/components/narrative_coherence" "Therapeutic Content" "Development" "theinterneti"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}MATURITY.md Files Creation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  - Core Infrastructure: 3 components"
echo "  - AI/Agent Systems: 4 components"
echo "  - Player Experience: 3 components"
echo "  - Therapeutic Content: 2 components"
echo "  - Total: 12 components"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Review and customize each MATURITY.md file"
echo "  2. Update component-specific information"
echo "  3. Add components to GitHub Project board"
echo "  4. Create promotion milestones"
echo ""
