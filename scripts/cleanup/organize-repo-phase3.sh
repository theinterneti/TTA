#!/bin/bash
# TTA Repository Cleanup - Phase 3: Documentation Hierarchy
# Organizes remaining markdown files into docs/ hierarchy

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 TTA Repository Cleanup - Phase 3${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}ℹ️  Creating complementary docs/ hierarchy${NC}"
echo ""

# Navigate to repo root
cd "$(dirname "$0")/../.." || exit 1

# Create docs structure
echo -e "${YELLOW}📁 Creating docs/ structure...${NC}"
mkdir -p docs/{guides,status,setup,development,reference}
echo -e "${GREEN}✓ Docs structure created${NC}"
echo ""

# Function to move file with git tracking
git_move() {
    local src="$1"
    local dest="$2"
    if [ -f "$src" ]; then
        git mv "$src" "$dest" 2>/dev/null || mv "$src" "$dest"
        echo "  ✓ $src → $dest"
        return 0
    else
        echo -e "${RED}  ✗ $src not found${NC}"
        return 1
    fi
}

# 3.1 Move Guides (How-to documentation)
echo -e "${YELLOW}📚 Organizing guides...${NC}"
git_move "TESTING_GUIDE.md" "docs/guides/testing.md"
git_move "DOCKER_QUICK_START.md" "docs/guides/docker-quick-start.md"
git_move "DATABASE_QUICK_REF.md" "docs/guides/database-quick-ref.md"
git_move "ADVANCED_TESTING_GETTING_STARTED.md" "docs/guides/advanced-testing.md"
git_move "CROSS-REPO-GUIDE.md" "docs/guides/cross-repo-development.md"
git_move "SECRETS_MANAGEMENT.md" "docs/guides/secrets-management.md"
git_move "USING_NOTEBOOKLM_WITH_COPILOT.md" "docs/guides/notebooklm-copilot.md"
git_move "CODECOV_QUICK_START.md" "docs/guides/codecov-setup.md"
echo ""

# 3.2 Move Status Dashboards (Current state tracking)
echo -e "${YELLOW}📊 Organizing status dashboards...${NC}"
git_move "CURRENT_STATUS.md" "docs/status/current-sprint.md"
git_move "ACCURATE_P0_COMPONENT_STATUS.md" "docs/status/p0-components.md"
git_move "COMPONENT_MATURITY_REANALYSIS.md" "docs/status/component-maturity.md"
git_move "SUBMISSION_STATUS.md" "docs/status/ai-toolkit-submission.md"
git_move "LINTING_AND_WORKFLOW_STATUS.md" "docs/status/code-quality.md"
git_move "TODO-AUDIT-SUMMARY.md" "docs/status/todo-audit.md"
echo ""

# 3.3 Move Setup Guides (Environment configuration)
echo -e "${YELLOW}⚙️  Organizing setup guides...${NC}"
git_move "TTA_DEV_ENVIRONMENT_READY.md" "docs/setup/dev-environment.md"
git_move "MCP_CONFIGURED.md" "docs/setup/mcp-servers.md"
git_move "VS_CODE_DATABASE_INTEGRATION.md" "docs/setup/vscode-database.md"
git_move "TTA_DEV_KEPLOY_INTEGRATION.md" "docs/setup/keploy-integration.md"
echo ""

# 3.4 Move Development Process Docs
echo -e "${YELLOW}🔧 Organizing development docs...${NC}"
git_move "GITHUB_ISSUES_TO_CREATE.md" "docs/development/github-issues.md"
git_move "GITHUB_WORKFLOW_REVIEW_AND_RECOMMENDATIONS.md" "docs/development/workflow-recommendations.md"
git_move "GITHUB_PRIMITIVES_COMPARISON.md" "docs/development/primitives-comparison.md"
git_move "AGENTIC_PRIMITIVES_REVIEW_AND_IMPROVEMENTS.md" "docs/development/primitives-improvements.md"
git_move "NEXT_STEPS_WORKFLOW_TESTING.md" "docs/development/next-steps.md"
git_move "NEXT_TEST_GENERATION_TARGETS.md" "docs/development/test-targets.md"
echo ""

# 3.5 Archive Historical/Completed Documents
echo -e "${YELLOW}📦 Archiving historical documents...${NC}"
mkdir -p .archive/status-reports/2025-11
[ -f "TODO-CLEANUP-REPORT.md" ] && mv "TODO-CLEANUP-REPORT.md" .archive/status-reports/2025-11/ && echo "  ✓ TODO-CLEANUP-REPORT.md"
[ -f "README_E2E_VALIDATION.md" ] && mv "README_E2E_VALIDATION.md" .archive/testing/2025-10/ && echo "  ✓ README_E2E_VALIDATION.md"
[ -f "READM_DATABASE_SIMPLIFICATION.md" ] && mv "READM_DATABASE_SIMPLIFICATION.md" .archive/database/2025-10/ && echo "  ✓ READM_DATABASE_SIMPLIFICATION.md"
[ -f "OPENROUTER_API_KEY_FIX.md" ] && mv "OPENROUTER_API_KEY_FIX.md" .archive/infrastructure/2025-10/ && echo "  ✓ OPENROUTER_API_KEY_FIX.md"
[ -f "tta_work_analysis.md" ] && mv "tta_work_analysis.md" .archive/status-reports/2025-10/ && echo "  ✓ tta_work_analysis.md"
echo ""

# Summary
echo "=================================================="
echo -e "${BLUE}✅ Phase 3 Complete!${NC}"
echo ""
echo "Documentation organization:"
remaining_md=$(find . -maxdepth 1 -type f -name '*.md' | wc -l)
echo "  - Root markdown files: $remaining_md (target: <10)"
echo "  - docs/guides/: $(find docs/guides -type f 2>/dev/null | wc -l) files"
echo "  - docs/status/: $(find docs/status -type f 2>/dev/null | wc -l) files"
echo "  - docs/setup/: $(find docs/setup -type f 2>/dev/null | wc -l) files"
echo "  - docs/development/: $(find docs/development -type f 2>/dev/null | wc -l) files"
echo "  - docs/reference/: $(find docs/reference -type f 2>/dev/null | wc -l) files"
echo ""
echo -e "${GREEN}Docs Organized:${NC}"
echo "  - Complementary docs organized by purpose"
echo ""
echo "Next steps:"
echo "  1. Review moved files and update internal links"
echo "  2. Update README.md to reference new docs/ structure"
echo "  3. Commit changes: git add -A && git commit -m 'docs: Phase 3 - Documentation hierarchy'"
echo ""
echo "=================================================="
