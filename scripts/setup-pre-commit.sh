#!/usr/bin/env bash
#
# Setup script for pre-commit hooks
# Optimized for solo developer WSL2 workflow
#
# Usage:
#   ./scripts/setup-pre-commit.sh [--skip-install] [--update]
#
# Options:
#   --skip-install    Skip installing pre-commit package (if already installed)
#   --update          Update all hooks to latest versions
#   --run-all         Run all hooks on all files after installation
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse arguments
SKIP_INSTALL=false
UPDATE_HOOKS=false
RUN_ALL=false

for arg in "$@"; do
    case $arg in
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        --update)
            UPDATE_HOOKS=true
            shift
            ;;
        --run-all)
            RUN_ALL=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            echo "Usage: $0 [--skip-install] [--update] [--run-all]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TTA Pre-Commit Hooks Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

cd "$PROJECT_ROOT"

# Step 1: Check if pre-commit is installed
echo -e "${YELLOW}[1/5]${NC} Checking pre-commit installation..."

if command -v pre-commit &> /dev/null; then
    PRECOMMIT_VERSION=$(pre-commit --version | awk '{print $2}')
    echo -e "${GREEN}✓${NC} pre-commit is installed (version $PRECOMMIT_VERSION)"
elif uv run pre-commit --version &> /dev/null; then
    PRECOMMIT_VERSION=$(uv run pre-commit --version | awk '{print $2}')
    echo -e "${GREEN}✓${NC} pre-commit is available via uv (version $PRECOMMIT_VERSION)"
    PRECOMMIT_CMD="uv run pre-commit"
else
    if [ "$SKIP_INSTALL" = true ]; then
        echo -e "${RED}✗${NC} pre-commit not found and --skip-install specified"
        exit 1
    fi

    echo -e "${YELLOW}→${NC} Installing pre-commit via uv..."
    uv pip install pre-commit

    if uv run pre-commit --version &> /dev/null; then
        PRECOMMIT_VERSION=$(uv run pre-commit --version | awk '{print $2}')
        echo -e "${GREEN}✓${NC} pre-commit installed successfully (version $PRECOMMIT_VERSION)"
        PRECOMMIT_CMD="uv run pre-commit"
    else
        echo -e "${RED}✗${NC} Failed to install pre-commit"
        exit 1
    fi
fi

# Set pre-commit command
if [ -z "${PRECOMMIT_CMD:-}" ]; then
    if command -v pre-commit &> /dev/null; then
        PRECOMMIT_CMD="pre-commit"
    else
        PRECOMMIT_CMD="uv run pre-commit"
    fi
fi

# Step 2: Update hooks if requested
if [ "$UPDATE_HOOKS" = true ]; then
    echo ""
    echo -e "${YELLOW}[2/5]${NC} Updating pre-commit hooks..."
    $PRECOMMIT_CMD autoupdate
    echo -e "${GREEN}✓${NC} Hooks updated to latest versions"
else
    echo ""
    echo -e "${YELLOW}[2/5]${NC} Skipping hook updates (use --update to update)"
fi

# Step 3: Install git hooks
echo ""
echo -e "${YELLOW}[3/5]${NC} Installing git hooks..."

# Install pre-commit hook
$PRECOMMIT_CMD install
echo -e "${GREEN}✓${NC} pre-commit hook installed"

# Install commit-msg hook for conventional commits
$PRECOMMIT_CMD install --hook-type commit-msg
echo -e "${GREEN}✓${NC} commit-msg hook installed"

# Step 4: Initialize secrets baseline if it doesn't exist
echo ""
echo -e "${YELLOW}[4/5]${NC} Checking secrets baseline..."

if [ ! -f ".secrets.baseline" ] || [ ! -s ".secrets.baseline" ]; then
    echo -e "${YELLOW}→${NC} Creating secrets baseline..."
    echo '{}' > .secrets.baseline
    echo -e "${GREEN}✓${NC} Secrets baseline created"
else
    echo -e "${GREEN}✓${NC} Secrets baseline exists"
fi

# Step 5: Make custom hook scripts executable
echo ""
echo -e "${YELLOW}[5/5]${NC} Setting up custom hooks..."

if [ -f "scripts/pre-commit/check-pytest-asyncio-fixtures.py" ]; then
    chmod +x scripts/pre-commit/check-pytest-asyncio-fixtures.py
    echo -e "${GREEN}✓${NC} pytest-asyncio fixture checker is executable"
else
    echo -e "${YELLOW}⚠${NC}  pytest-asyncio fixture checker not found"
fi

# Optional: Run all hooks on all files
if [ "$RUN_ALL" = true ]; then
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Running hooks on all files...${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    if $PRECOMMIT_CMD run --all-files; then
        echo ""
        echo -e "${GREEN}✓${NC} All hooks passed!"
    else
        echo ""
        echo -e "${YELLOW}⚠${NC}  Some hooks failed or made changes"
        echo -e "${YELLOW}→${NC} Review the changes and commit them if appropriate"
    fi
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}✓${NC} Pre-commit hooks are installed and ready"
echo ""
echo "Next steps:"
echo "  1. Hooks will run automatically on 'git commit'"
echo "  2. To run manually: $PRECOMMIT_CMD run --all-files"
echo "  3. To bypass hooks: git commit --no-verify"
echo "  4. For more info: docs/PRE_COMMIT_HOOKS.md"
echo ""
echo "Configured hooks:"
echo "  • Ruff (linting & formatting)"
echo "  • Black (code formatting)"
echo "  • isort (import sorting)"
echo "  • Bandit (security scanning)"
echo "  • detect-secrets (credential detection)"
echo "  • pytest-asyncio fixture validator (custom)"
echo "  • Conventional commits (commit message format)"
echo "  • File validation (YAML, JSON, TOML)"
echo "  • Trailing whitespace & EOF fixes"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
