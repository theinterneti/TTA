#!/bin/bash
# TTA Repository Cleanup - Phase 2: Status Report Consolidation
# Organizes markdown documentation by category

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 TTA Repository Cleanup - Phase 2${NC}"
echo "=================================================="
echo ""

# Navigate to repo root
cd "$(dirname "$0")/../.." || exit 1

# Function to move files with reporting
move_files() {
    local pattern="$1"
    local destination="$2"
    local count=0

    for file in $pattern; do
        if [ -f "$file" ]; then
            mv "$file" "$destination/" && ((count++)) || true
        fi
    done
    echo "$count"
}

# 2.1 Archive Phase Reports
echo -e "${YELLOW}📋 Archiving Phase completion reports...${NC}"
count=$(move_files "PHASE*.md" ".archive/status-reports/2025-10")
echo -e "${GREEN}✓ Archived $count Phase reports${NC}"
echo ""

# 2.2 Archive *_COMPLETE.md Reports
echo -e "${YELLOW}✅ Archiving completion reports...${NC}"
count=$(move_files "*_COMPLETE.md" ".archive/status-reports/2025-10")
echo -e "${GREEN}✓ Archived $count completion reports${NC}"
echo ""

# 2.3 Archive *_SUMMARY.md Reports
echo -e "${YELLOW}📝 Archiving summary reports...${NC}"
count=$(move_files "*_SUMMARY.md" ".archive/status-reports/2025-10")
echo -e "${GREEN}✓ Archived $count summary reports${NC}"
echo ""

# 2.4 Archive *_REPORT.md Reports
echo -e "${YELLOW}📊 Archiving detailed reports...${NC}"
count=$(move_files "*_REPORT.md" ".archive/status-reports/2025-10")
echo -e "${GREEN}✓ Archived $count detailed reports${NC}"
echo ""

# 2.5 Archive CI/CD Reports
echo -e "${YELLOW}🔄 Archiving CI/CD reports...${NC}"
count=0
for file in CI_CD_*.md CICD_*.md WORKFLOW_*.md PR_*.md; do
    if [ -f "$file" ]; then
        mv "$file" .archive/cicd/2025-10/ && ((count++)) || true
    fi
done
echo -e "${GREEN}✓ Archived $count CI/CD reports${NC}"
echo ""

# 2.6 Archive Testing Reports
echo -e "${YELLOW}🧪 Archiving testing reports...${NC}"
count=0
for file in E2E_*.md TEST_*.md TESTING_*.md TIER_*.md VALIDATION_*.md; do
    if [ -f "$file" ]; then
        # Keep TESTING_GUIDE.md in root for now (will move to docs/ in Phase 3)
        if [ "$file" != "TESTING_GUIDE.md" ]; then
            mv "$file" .archive/testing/2025-10/ && ((count++)) || true
        fi
    fi
done
echo -e "${GREEN}✓ Archived $count testing reports${NC}"
echo ""

# 2.7 Archive Database Reports
echo -e "${YELLOW}💾 Archiving database reports...${NC}"
count=0
for file in DATABASE_*.md NEO4J_*.md REDIS_*.md; do
    if [ -f "$file" ]; then
        # Keep DATABASE_QUICK_REF.md in root for now
        if [ "$file" != "DATABASE_QUICK_REF.md" ]; then
            mv "$file" .archive/database/2025-10/ && ((count++)) || true
        fi
    fi
done
echo -e "${GREEN}✓ Archived $count database reports${NC}"
echo ""

# 2.8 Archive Docker/Infrastructure Reports
echo -e "${YELLOW}🐳 Archiving infrastructure reports...${NC}"
count=0
for file in DOCKER_*.md DEPLOYMENT_*.md INFRASTRUCTURE_*.md; do
    if [ -f "$file" ]; then
        # Keep DOCKER_QUICK_START.md in root for now
        if [ "$file" != "DOCKER_QUICK_START.md" ]; then
            mv "$file" .archive/infrastructure/2025-10/ && ((count++)) || true
        fi
    fi
done
echo -e "${GREEN}✓ Archived $count infrastructure reports${NC}"
echo ""

# 2.9 Archive Observability Reports
echo -e "${YELLOW}📈 Archiving observability reports...${NC}"
count=$(move_files "OBSERVABILITY_*.md" ".archive/observability/2025-10")
echo -e "${GREEN}✓ Archived $count observability reports${NC}"
echo ""

# 2.10 Archive Tooling Reports
echo -e "${YELLOW}🔧 Archiving tooling reports...${NC}"
count=0
for file in OPENHANDS_*.md KEPLOY_*.md; do
    if [ -f "$file" ]; then
        mv "$file" .archive/tooling/2025-10/ && ((count++)) || true
    fi
done
echo -e "${GREEN}✓ Archived $count tooling reports${NC}"
echo ""

# 2.11 Archive Component Reports
echo -e "${YELLOW}🧩 Archiving component reports...${NC}"
count=0
for file in COMPONENT_*.md CARBON_*.md NARRATIVE_*.md CHARACTER_*.md MODEL_MANAGEMENT_*.md; do
    if [ -f "$file" ]; then
        # Keep COMPONENT_MATURITY_REANALYSIS.md in root (current status)
        if [ "$file" != "COMPONENT_MATURITY_REANALYSIS.md" ]; then
            mv "$file" .archive/components/2025-10/ && ((count++)) || true
        fi
    fi
done
echo -e "${GREEN}✓ Archived $count component reports${NC}"
echo ""

# 2.12 Archive Package Reports
echo -e "${YELLOW}📦 Archiving package reports...${NC}"
count=0
for file in *_PACKAGE.md APM_*.md AI_DEV_TOOLKIT_*.md; do
    if [ -f "$file" ]; then
        mv "$file" .archive/packages/2025-10/ && ((count++)) || true
    fi
done
echo -e "${GREEN}✓ Archived $count package reports${NC}"
echo ""

# 2.13 Archive Setup/Migration Reports
echo -e "${YELLOW}🛠️  Archiving setup reports...${NC}"
count=0
for file in *_SETUP*.md *_MIGRATION*.md *_EXTRACTION*.md SETUP_*.md; do
    if [ -f "$file" ]; then
        # Skip ADVANCED_TESTING_GETTING_STARTED.md (guide)
        if [[ "$file" != *"GETTING_STARTED"* ]]; then
            mv "$file" .archive/infrastructure/2025-10/ && ((count++)) || true
        fi
    fi
done
echo -e "${GREEN}✓ Archived $count setup reports${NC}"
echo ""

# 2.14 Archive Audit/Analysis Reports
echo -e "${YELLOW}🔍 Archiving audit reports...${NC}"
count=0
for file in *_AUDIT*.md *_ANALYSIS*.md AUDIT_*.md *_INVESTIGATION*.md; do
    if [ -f "$file" ]; then
        # Keep TODO-AUDIT* files (active)
        if [[ "$file" != TODO-AUDIT* ]]; then
            mv "$file" .archive/status-reports/2025-10/ && ((count++)) || true
        fi
    fi
done
echo -e "${GREEN}✓ Archived $count audit reports${NC}"
echo ""

# 2.15 Archive Plan/Strategy Documents
echo -e "${YELLOW}📋 Archiving plan documents...${NC}"
count=0
for file in *_PLAN.md *_STRATEGY.md GIT_ORGANIZATION_PLAN.md MERGE_*.md; do
    if [ -f "$file" ]; then
        # Keep REPOSITORY_CLEANUP_PLAN.md (current)
        if [ "$file" != "REPOSITORY_CLEANUP_PLAN.md" ]; then
            mv "$file" .archive/status-reports/2025-10/ && ((count++)) || true
        fi
    fi
done
echo -e "${GREEN}✓ Archived $count plan documents${NC}"
echo ""

# Summary
echo "=================================================="
echo -e "${BLUE}✅ Phase 2 Complete!${NC}"
echo ""
echo "Root directory cleanup progress:"
remaining_md=$(find . -maxdepth 1 -type f -name '*.md' | wc -l)
echo "  - Markdown files remaining: $remaining_md"
echo ""
echo "Next steps:"
echo "  1. Review .archive/ organization"
echo "  2. Run Phase 3: Documentation Hierarchy"
echo "  3. Commit changes with descriptive message"
echo ""
echo "=================================================="
