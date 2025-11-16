#!/bin/bash
# TTA Repository Cleanup - Phase 3: Documentation Hierarchy
# Organizes remaining markdown files respecting Logseq KB structure

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
echo -e "${YELLOW}ℹ️  Respecting Logseq KB structure (.augment/kb/)${NC}"
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

# 3.5 Create Reference Links to KB
echo -e "${YELLOW}🔗 Creating KB reference documents...${NC}"

cat > docs/reference/logseq-kb.md << 'EOF'
# TTA Knowledge Base Reference

> 📚 **Primary Documentation Location**
>
> Most TTA documentation has been consolidated into a Logseq-powered knowledge base.

## Access

**Location:** `.augment/kb/` (306 documents)
**Logseq Repo:** `~/repos/TTA-notes/logseq/pages/TTA/`

## Quick Navigation

### Architecture
- `TTA___Architecture___Docs Architecture Agent Orchestration.md` - Multi-agent system design
- `TTA___Architecture___Docs Database Architecture Simplification Document.md` - Database patterns
- `TTA___Architecture___Docs Architecture Overview.md` - System overview

### Components
- `TTA___Components___Component Maturity Reanalysis Document.md` - Component status
- `TTA___Components___Docs Component Promotion Guide Document.md` - Promotion workflow
- Individual component docs: Carbon, Model Management, Narrative Coherence, etc.

### Workflows
- `TTA___Workflows___Docs Testing Testing Guide Document.md` - Testing workflows
- `TTA___Workflows___Docs Development Contributing Document.md` - Development process
- `TTA___Workflows___Cross Repo Guide Document.md` - Multi-repo development

### Status & Timeline
- `TTA___Status___Project Timeline.md` - Phase 1-7 history
- `TTA___Status___Implementation Dashboard.md` - Current status
- `TTA___Status___Phase7 Metrics Report Document.md` - Latest metrics

### References
- `TTA___References___Agents Document.md` - Agent system reference
- `TTA___References___Claude Document.md` - Claude AI context
- `TTA___References___Gemini Document.md` - Gemini AI context

## Usage Tips

1. **Search:** Use `Ctrl+K` in Logseq to find pages
2. **Wiki Links:** Click `[[TTA___Category___Page]]` to navigate
3. **Bidirectional:** Explore backlinks to see related content
4. **Tags:** Search `#TTA` to see all pages

## Why Logseq?

- **Bidirectional Links:** Explore connections between concepts
- **Query Power:** Dynamic views based on properties
- **Graph View:** Visualize documentation relationships
- **Version Control:** All files are markdown in git
- **Offline Access:** No cloud dependency

## Complementary Docs

This `docs/` directory contains:
- **Guides:** How-to documentation for common tasks
- **Status:** Current project dashboards
- **Setup:** Environment configuration
- **Development:** Process and workflow docs

For deep architectural docs, agent behavior, and historical context, see the KB.
EOF

echo "  ✓ Created docs/reference/logseq-kb.md"
echo ""

# 3.6 Archive Historical/Completed Documents
echo -e "${YELLOW}📦 Archiving historical documents...${NC}"
mkdir -p .archive/status-reports/2025-11
[ -f "TODO-CLEANUP-REPORT.md" ] && mv "TODO-CLEANUP-REPORT.md" .archive/status-reports/2025-11/ && echo "  ✓ TODO-CLEANUP-REPORT.md"
[ -f "README_E2E_VALIDATION.md" ] && mv "README_E2E_VALIDATION.md" .archive/testing/2025-10/ && echo "  ✓ README_E2E_VALIDATION.md"
[ -f "READM_DATABASE_SIMPLIFICATION.md" ] && mv "READM_DATABASE_SIMPLIFICATION.md" .archive/database/2025-10/ && echo "  ✓ READM_DATABASE_SIMPLIFICATION.md"
[ -f "OPENROUTER_API_KEY_FIX.md" ] && mv "OPENROUTER_API_KEY_FIX.md" .archive/infrastructure/2025-10/ && echo "  ✓ OPENROUTER_API_KEY_FIX.md"
[ -f "tta_work_analysis.md" ] && mv "tta_work_analysis.md" .archive/status-reports/2025-10/ && echo "  ✓ tta_work_analysis.md"
echo ""

# 3.7 Create docs README
echo -e "${YELLOW}📝 Creating docs/README.md...${NC}"
cat > docs/README.md << 'EOF'
# TTA Documentation

Welcome to the TTA (Therapeutic Text Adventure) documentation!

## Documentation Structure

### 📚 Primary Knowledge Base
Most documentation lives in the **Logseq Knowledge Base** at `.augment/kb/`:
- 306 interconnected documents
- Architecture, components, workflows, testing, and more
- See [docs/reference/logseq-kb.md](reference/logseq-kb.md) for navigation

### 📖 This Directory (`docs/`)
Complementary documentation for active development:

#### [guides/](guides/) - How-To Documentation
- [Testing Guide](guides/testing.md) - Comprehensive testing workflows
- [Docker Quick Start](guides/docker-quick-start.md) - Container setup
- [Database Quick Reference](guides/database-quick-ref.md) - Redis & Neo4j
- [Advanced Testing](guides/advanced-testing.md) - E2E, mutation, load tests
- [Cross-Repo Development](guides/cross-repo-development.md) - Multi-repo workflow
- [Secrets Management](guides/secrets-management.md) - Credential handling
- [NotebookLM with Copilot](guides/notebooklm-copilot.md) - AI integration
- [CodeCov Setup](guides/codecov-setup.md) - Coverage reporting

#### [status/](status/) - Project Dashboards
- [Current Sprint](status/current-sprint.md) - Active work tracking
- [P0 Components](status/p0-components.md) - Critical component status
- [Component Maturity](status/component-maturity.md) - Maturity levels
- [AI Toolkit Submission](status/ai-toolkit-submission.md) - Package status
- [Code Quality](status/code-quality.md) - Linting & workflow health
- [TODO Audit](status/todo-audit.md) - Incomplete work tracking

#### [setup/](setup/) - Environment Setup
- [Dev Environment](setup/dev-environment.md) - Complete setup guide
- [MCP Servers](setup/mcp-servers.md) - Model Context Protocol setup
- [VSCode Database](setup/vscode-database.md) - Database integration
- [Keploy Integration](setup/keploy-integration.md) - Testing framework

#### [development/](development/) - Process Documentation
- [GitHub Issues](development/github-issues.md) - Issue management
- [Workflow Recommendations](development/workflow-recommendations.md) - Best practices
- [Primitives Comparison](development/primitives-comparison.md) - Implementation patterns
- [Primitives Improvements](development/primitives-improvements.md) - Enhancement plans
- [Next Steps](development/next-steps.md) - Upcoming work
- [Test Targets](development/test-targets.md) - Test generation priorities

#### [reference/](reference/) - Quick References
- [Logseq KB Guide](reference/logseq-kb.md) - Navigate the knowledge base

## Getting Started

### New Contributors
1. Read [CONTRIBUTING.md](../CONTRIBUTING.md) in the repository root
2. Follow [setup/dev-environment.md](setup/dev-environment.md) for environment setup
3. Review [guides/testing.md](guides/testing.md) for testing workflow
4. Check [status/current-sprint.md](status/current-sprint.md) for active work

### Existing Contributors
- **Daily:** Check [status/current-sprint.md](status/current-sprint.md)
- **New Features:** Review component architecture in `.augment/kb/TTA___Components___`
- **Debugging:** Check [guides/database-quick-ref.md](guides/database-quick-ref.md)
- **Deployment:** Follow [guides/docker-quick-start.md](guides/docker-quick-start.md)

## Documentation Philosophy

### Repository `docs/` (This Directory)
**Purpose:** Active development reference
- Current status and dashboards
- Quick-start guides
- Environment setup
- Common workflows

### Logseq KB (`.augment/kb/`)
**Purpose:** Deep knowledge and context
- System architecture
- Component design decisions
- Historical context and evolution
- Agent behavior and patterns
- Cross-cutting concerns

### When to Add New Docs

**Add to `docs/`:**
- Quick reference guides
- Current project status
- Active work tracking
- Environment setup instructions

**Add to KB:**
- Architectural decisions
- Component specifications
- Long-term design docs
- Agent behavioral patterns
- Cross-project learnings

## Maintenance

- **`docs/`**: Updated frequently with current status
- **`.augment/kb/`**: Updated for significant changes or new components
- **`.archive/`**: Historical reports preserved but not actively maintained

---

**Questions?** Check the [Logseq KB Guide](reference/logseq-kb.md) or ask in team chat!
EOF
echo "  ✓ Created docs/README.md"
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
echo -e "${GREEN}KB Structure Respected:${NC}"
echo "  - Primary docs remain in .augment/kb/ (306 files)"
echo "  - Reference link created at docs/reference/logseq-kb.md"
echo "  - Complementary docs organized by purpose"
echo ""
echo "Next steps:"
echo "  1. Review moved files and update internal links"
echo "  2. Update README.md to reference new docs/ structure"
echo "  3. Commit changes: git add -A && git commit -m 'docs: Phase 3 - Documentation hierarchy'"
echo ""
echo "=================================================="
