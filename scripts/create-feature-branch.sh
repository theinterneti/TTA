#!/bin/bash
# create-feature-branch.sh - Helper script to create feature branches following naming conventions
# Usage: ./scripts/create-feature-branch.sh <domain> <description>
# Example: ./scripts/create-feature-branch.sh clinical add-patient-notes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo -e "${BLUE}Usage:${NC} $0 <domain> <description>"
    echo ""
    echo -e "${BLUE}Domains:${NC}"
    echo "  clinical  - Clinical/therapeutic features"
    echo "  game      - Game mechanics and narrative features"
    echo "  infra     - Infrastructure, DevOps, CI/CD"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  $0 clinical add-patient-notes"
    echo "  $0 game improve-dialogue-system"
    echo "  $0 infra update-docker-config"
    exit 1
}

# Check arguments
if [ $# -ne 2 ]; then
    echo -e "${RED}Error: Invalid number of arguments${NC}"
    usage
fi

DOMAIN=$1
DESCRIPTION=$2

# Validate domain
case $DOMAIN in
    clinical|game|infra)
        ;;
    *)
        echo -e "${RED}Error: Invalid domain '${DOMAIN}'${NC}"
        echo -e "${YELLOW}Valid domains: clinical, game, infra${NC}"
        exit 1
        ;;
esac

# Validate description (alphanumeric and hyphens only)
if ! [[ $DESCRIPTION =~ ^[a-z0-9-]+$ ]]; then
    echo -e "${RED}Error: Description must contain only lowercase letters, numbers, and hyphens${NC}"
    exit 1
fi

# Construct branch name
BRANCH_NAME="feature/${DOMAIN}-${DESCRIPTION}"

echo -e "${BLUE}Creating feature branch: ${GREEN}${BRANCH_NAME}${NC}"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Check if branch already exists
if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
    echo -e "${RED}Error: Branch '${BRANCH_NAME}' already exists locally${NC}"
    exit 1
fi

if git ls-remote --heads origin "${BRANCH_NAME}" | grep -q "${BRANCH_NAME}"; then
    echo -e "${RED}Error: Branch '${BRANCH_NAME}' already exists on remote${NC}"
    exit 1
fi

# Ensure we're on development branch and it's up to date
echo -e "${YELLOW}Switching to development branch...${NC}"
git checkout development

echo -e "${YELLOW}Pulling latest changes from remote...${NC}"
git pull origin development

# Create and checkout new branch
echo -e "${YELLOW}Creating new branch from development...${NC}"
git checkout -b "${BRANCH_NAME}"

echo ""
echo -e "${GREEN}✓ Successfully created feature branch: ${BRANCH_NAME}${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Make your changes"
echo "  2. Commit your changes: git commit -m 'feat(${DOMAIN}): your message'"
echo "  3. Push to remote: git push -u origin ${BRANCH_NAME}"
echo "  4. Create PR to development branch"
echo ""
echo -e "${BLUE}Commit message format:${NC}"
echo "  feat(${DOMAIN}): add new feature"
echo "  fix(${DOMAIN}): fix bug"
echo "  docs(${DOMAIN}): update documentation"
echo "  refactor(${DOMAIN}): refactor code"
echo "  test(${DOMAIN}): add tests"
echo ""
echo -e "${YELLOW}Note: PRs to development require unit tests to pass${NC}"
