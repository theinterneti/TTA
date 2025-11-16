#!/bin/bash
# Repository Cleanup and Organization Script
# Purpose: Clean up TTA repository root directory and organize files properly
# Safety: Creates backups before any destructive operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
DRY_RUN=true
BACKUP_BRANCH="backup-pre-cleanup-$(date +%Y%m%d-%H%M%S)"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   TTA Repository Cleanup & Organization   ║${NC}"
echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
echo ""

# Parse arguments
for arg in "$@"; do
    case $arg in
        --execute)
            DRY_RUN=false
            shift
            ;;
        --help)
            cat << 'HELP'
Usage: ./cleanup_and_organize_repo.sh [OPTIONS]

Options:
  --execute    Actually perform the cleanup (default is dry-run)
  --help       Show this help message

Description:
  This script organizes the TTA repository by:
  1. Creating a safety backup branch
  2. Moving documentation to docs/
  3. Archiving logs and test results
  4. Organizing scripts
  5. Cleaning up root directory
  6. Updating .gitignore

Safety Features:
  - Dry-run by default
  - Creates backup branch before changes
  - Preserves all files (moves, doesn't delete)
  - Git operations only (no destructive rm commands)

HELP
            exit 0
            ;;
    esac
done

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}🔍 DRY RUN MODE - No changes will be made${NC}"
    echo -e "${YELLOW}   Run with --execute to apply changes${NC}"
    echo ""
else
    echo -e "${RED}⚠️  EXECUTE MODE - Changes will be made${NC}"
    echo -e "${YELLOW}   Press Ctrl+C within 5 seconds to cancel...${NC}"
    sleep 5
    echo ""
fi

# Function to execute or simulate command
run_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${BLUE}[DRY RUN]${NC} $*"
    else
        echo -e "${GREEN}[EXECUTE]${NC} $*"
        eval "$@"
    fi
}

# Safety checks
echo -e "${BLUE}📋 Pre-flight Checks${NC}"
echo "-------------------"

if [[ -n $(git diff --cached --name-only) ]]; then
    echo -e "${RED}✗ You have staged changes${NC}"
    echo "  Please commit or stash before running this script"
    exit 1
fi
echo -e "${GREEN}✓ No staged changes${NC}"

if [[ ! -d .git ]]; then
    echo -e "${RED}✗ Not in a git repository${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Git repository detected${NC}"

CURRENT_BRANCH=$(git branch --show-current)
echo -e "${GREEN}✓ Current branch: ${CURRENT_BRANCH}${NC}"
echo ""

# Phase 1: Create Safety Backup
echo -e "${BLUE}Phase 1: Safety Backup${NC}"
echo "----------------------"
run_cmd "git branch $BACKUP_BRANCH"
echo -e "${GREEN}✓ Created backup branch: ${BACKUP_BRANCH}${NC}"
echo ""

# Phase 2: Create Directory Structure
echo -e "${BLUE}Phase 2: Directory Structure${NC}"
echo "----------------------------"

DIRS_TO_CREATE=(
    "docs/phases"
    "docs/reports"
    "docs/guides"
    "docs/agentic-primitives"
    "docs/mvp"
    "docs/architecture"
    ".archive/logs"
    ".archive/test-results"
    ".archive/old-scripts"
    ".archive/backups"
    ".archive/obsolete-docs"
    "artifacts/test-results"
    "artifacts/coverage"
    "artifacts/benchmarks"
)

for dir in "${DIRS_TO_CREATE[@]}"; do
    run_cmd "mkdir -p $dir"
done
echo -e "${GREEN}✓ Directory structure created${NC}"
echo ""

# Phase 3: Move Documentation Files
echo -e "${BLUE}Phase 3: Organize Documentation${NC}"
echo "--------------------------------"

# Phase documentation
echo "📁 Phase Documentation"
for file in PHASE*.md; do
    [ -f "$file" ] && run_cmd "git mv '$file' docs/phases/"
done

# Reports and summaries
echo "📁 Reports & Summaries"
for pattern in "*REPORT*.md" "*SUMMARY*.md" "*COMPLETE*.md" "*STATUS*.md" "*VALIDATION*.md"; do
    for file in $pattern; do
        [ -f "$file" ] && run_cmd "git mv '$file' docs/reports/"
    done
done

# Guides and quickrefs
echo "📁 Guides & References"
for pattern in "*GUIDE*.md" "*QUICKREF*.md" "*QUICKSTART*.md" "*WORKFLOW*.md" "*STRATEGY*.md"; do
    for file in $pattern; do
        [ -f "$file" ] && run_cmd "git mv '$file' docs/guides/"
    done
done

# Agentic primitives documentation
echo "📁 Agentic Primitives Documentation"
for file in AGENTIC_*.md GITHUB_*.md COMPONENT_PACKAGING_STRATEGY.md; do
    [ -f "$file" ] && run_cmd "git mv '$file' docs/agentic-primitives/"
done

# MVP documentation
echo "📁 MVP Documentation"
for file in MVP_*.md; do
    [ -f "$file" ] && run_cmd "git mv '$file' docs/mvp/"
done

# Implementation and analysis docs
echo "📁 Implementation Documentation"
for file in IMPLEMENTATION_*.md IMPLEMENTATION_*.txt; do
    [ -f "$file" ] && run_cmd "git mv '$file' docs/reports/"
done

echo -e "${GREEN}✓ Documentation organized${NC}"
echo ""

# Phase 4: Archive Logs and Test Results
echo -e "${BLUE}Phase 4: Archive Artifacts${NC}"
echo "---------------------------"

# Move logs
echo "📁 Logs"
for file in *.log; do
    [ -f "$file" ] && run_cmd "git mv '$file' .archive/logs/"
done

# Move test results
echo "📁 Test Results"
for pattern in "*test*.json" "*results*.json" "test*.txt" "*_results.txt" "*test*.spec.ts"; do
    for file in $pattern; do
        [ -f "$file" ] && ! [[ "$file" == "test-simple.spec.ts" || "$file" == "quick-validation.spec.ts" || "$file" == "e2e-validation.spec.ts" ]] && run_cmd "git mv '$file' .archive/test-results/"
    done
done

# Move backup directories
echo "📁 Backup Directories"
for dir in backup-*; do
    [ -d "$dir" ] && run_cmd "git mv '$dir' .archive/backups/"
done

# Move old coverage files
echo "📁 Coverage Artifacts"
[ -d "htmlcov" ] && run_cmd "git mv htmlcov artifacts/coverage/"
[ -f "coverage.xml" ] && run_cmd "git mv coverage.xml artifacts/coverage/"
[ -f "coverage.json" ] && run_cmd "git mv coverage.json artifacts/coverage/"
for file in coverage_*.json coverage_*.txt; do
    [ -f "$file" ] && run_cmd "git mv '$file' artifacts/coverage/"
done

# Move mutation testing results
echo "📁 Mutation Testing"
for file in mutation*.html cosmic-ray*.log cosmic-ray*.toml session*.sqlite *mutation*.json; do
    [ -f "$file" ] && run_cmd "git mv '$file' .archive/test-results/"
done

echo -e "${GREEN}✓ Artifacts archived${NC}"
echo ""

# Phase 5: Organize Scripts
echo -e "${BLUE}Phase 5: Organize Scripts${NC}"
echo "--------------------------"

# Development scripts
echo "📁 Development Scripts"
for file in fix-*.sh force-*.sh verify-*.sh debug-*.py; do
    [ -f "$file" ] && run_cmd "git mv '$file' scripts/development/"
done

# Testing scripts
echo "📁 Testing Scripts"
for file in test_*.py *_test.py validate-*.py validate-*.sh; do
    [ -f "$file" ] && ! [[ "$file" == "conftest.py" || "$file" == "test_mvp.py" ]] && run_cmd "git mv '$file' scripts/testing/"
done

# Deployment scripts
echo "📁 Deployment Scripts"
for file in setup-*.sh deploy*.sh start_*.sh staging*.sh production*.sh; do
    [ -f "$file" ] && run_cmd "git mv '$file' scripts/deployment/"
done

# Validation scripts
echo "📁 Validation Scripts"
for file in github-*-validator.sh *-validation.sh; do
    [ -f "$file" ] && run_cmd "git mv '$file' scripts/validation/"
done

echo -e "${GREEN}✓ Scripts organized${NC}"
echo ""

# Phase 6: Archive Old/Obsolete Files
echo -e "${BLUE}Phase 6: Archive Obsolete Files${NC}"
echo "--------------------------------"

# Obsolete Python scripts
echo "📁 Obsolete Scripts"
for file in cleanup_obsolete_files.py generate_therapeutic_worlds.py populate_tta_system.py neo4j_*.py *_demo.py enhanced_*.py minimal_*.py simple_*.py; do
    [ -f "$file" ] && run_cmd "git mv '$file' .archive/old-scripts/"
done

# Obsolete config/data files
echo "📁 Obsolete Data Files"
for file in cookies.txt bandit-report.json semgrep*.json docker-warnings.json engine_state.json task_queue.json emissions.csv monkeytype.sqlite3; do
    [ -f "$file" ] && run_cmd "git mv '$file' .archive/test-results/"
done

# Test workspace
[ -d "test_workspace" ] && run_cmd "git mv test_workspace .archive/"

# Obsolete markdown
for file in tta_work_analysis.md; do
    [ -f "$file" ] && run_cmd "git mv '$file' .archive/obsolete-docs/"
done

echo -e "${GREEN}✓ Obsolete files archived${NC}"
echo ""

# Phase 7: Update .gitignore
echo -e "${BLUE}Phase 7: Update .gitignore${NC}"
echo "---------------------------"

if [ "$DRY_RUN" = false ]; then
    cat >> .gitignore << 'GITIGNORE'

# -------------------------------------------------
# Repository Organization - Archive & Artifacts
# -------------------------------------------------
# These are tracked but built/generated files
*.log
*.sqlite
*.sqlite3
*test_results*.json
*_results.json
phase*_execution.log
batch*_results.json

# Test coverage artifacts (tracked in artifacts/)
htmlcov/
coverage/
.coverage
coverage.xml
coverage.json
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Temporary test files
test_workspace/
.hypothesis/

# Session and state files
session*.sqlite
engine_state.json
task_queue.json
cookies.txt

# Old backups (tracked in .archive/)
backup-*/

# -------------------------------------------------
# Build and benchmark artifacts
# -------------------------------------------------
mutants/
site/
dist/
*.egg-info/

GITIGNORE
    echo -e "${GREEN}✓ .gitignore updated${NC}"
else
    echo -e "${BLUE}[DRY RUN] Would update .gitignore${NC}"
fi
echo ""

# Phase 8: Summary
echo -e "${BLUE}Phase 8: Summary${NC}"
echo "----------------"

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}This was a dry run. No changes were made.${NC}"
    echo ""
    echo "To execute these changes, run:"
    echo -e "${GREEN}  ./scripts/cleanup_and_organize_repo.sh --execute${NC}"
    echo ""
    echo "Review the proposed changes above and ensure they look correct."
else
    echo -e "${GREEN}✅ Repository cleanup complete!${NC}"
    echo ""
    echo "📊 Summary:"
    echo "  - Documentation moved to docs/"
    echo "  - Logs archived to .archive/logs/"
    echo "  - Test results archived to .archive/test-results/"
    echo "  - Scripts organized in scripts/"
    echo "  - Backup created: $BACKUP_BRANCH"
    echo ""
    echo "🔍 Next Steps:"
    echo "  1. Review changes: git status"
    echo "  2. View diff: git diff --stat"
    echo "  3. Commit changes: git commit -m 'chore: organize repository structure'"
    echo "  4. If needed, restore from: git checkout $BACKUP_BRANCH"
    echo ""
    echo "📝 Files that should remain in root:"
    echo "  - README.md, CHANGELOG.md, CONTRIBUTING.md, SECURITY.md"
    echo "  - pyproject.toml, Makefile"
    echo "  - docker-compose*.yml, Dockerfile.*"
    echo "  - .env.example and core config files"
    echo ""
fi

# Statistics
echo -e "${CYAN}📈 Repository Statistics${NC}"
echo "-----------------------"
echo "Root .md files now: $(find . -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l)"
echo "Root .log files now: $(find . -maxdepth 1 -name "*.log" -type f 2>/dev/null | wc -l)"
echo "Root .json files now: $(find . -maxdepth 1 -name "*.json" -type f 2>/dev/null | wc -l)"
echo ""
echo -e "${GREEN}✨ Done!${NC}"
