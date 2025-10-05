#!/bin/bash
# Configure Branch Protection Rules for TTA Repository
# Three-Tier Strategy: development → staging → main
#
# This script configures branch protection rules via GitHub API
# Designed for solo developer workflow with quality gates
# Version: 2.0.0
# Updated: 2025-10-05

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository information
REPO_OWNER="theinterneti"
REPO_NAME="TTA"

# Configuration mode
MODE="${1:-three-tier}"  # Options: three-tier, solo-dev

echo -e "${GREEN}=== TTA Branch Protection Configuration ===${NC}"
echo "Repository: ${REPO_OWNER}/${REPO_NAME}"
echo "Mode: ${MODE}"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✓ GitHub CLI authenticated${NC}"
echo ""

# Function to configure main branch protection (Production)
configure_main_branch() {
    echo -e "${YELLOW}Configuring main branch protection (Production)...${NC}"

    if [ "$MODE" = "three-tier" ]; then
        # Three-tier mode: Comprehensive tests + manual approval
        gh api \
            --method PUT \
            -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "/repos/${REPO_OWNER}/${REPO_NAME}/branches/main/protection" \
            -f required_status_checks[strict]=true \
            -f "required_status_checks[contexts][]=unit" \
            -f "required_status_checks[contexts][]=integration" \
            -f "required_status_checks[contexts][]=e2e-tests / E2E Tests (chromium - auth)" \
            -f "required_status_checks[contexts][]=e2e-tests / E2E Tests (chromium - dashboard)" \
            -f "required_status_checks[contexts][]=code-quality / Lint and Format" \
            -f "required_status_checks[contexts][]=code-quality / Type Check" \
            -f "required_status_checks[contexts][]=security-scan / Security Scan" \
            -f required_pull_request_reviews[required_approving_review_count]=1 \
            -f required_pull_request_reviews[dismiss_stale_reviews]=true \
            -f required_pull_request_reviews[require_code_owner_reviews]=false \
            -f enforce_admins=false \
            -f required_linear_history=true \
            -f allow_force_pushes=false \
            -f allow_deletions=false \
            -f required_conversation_resolution=true \
            -f lock_branch=false \
            -f allow_fork_syncing=true
    else
        # Solo-dev mode: Basic protection
        gh api \
            --method PUT \
            -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "/repos/${REPO_OWNER}/${REPO_NAME}/branches/main/protection" \
            -f required_status_checks[strict]=true \
            -f "required_status_checks[contexts][]=unit" \
            -f "required_status_checks[contexts][]=integration" \
            -f required_pull_request_reviews[required_approving_review_count]=1 \
            -f required_pull_request_reviews[dismiss_stale_reviews]=true \
            -f required_pull_request_reviews[require_code_owner_reviews]=false \
            -f enforce_admins=false \
            -f required_linear_history=true \
            -f allow_force_pushes=false \
            -f allow_deletions=false \
            -f required_conversation_resolution=true \
            -f lock_branch=false \
            -f allow_fork_syncing=true
    fi

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Main branch protection configured${NC}"
    else
        echo -e "${RED}✗ Failed to configure main branch protection${NC}"
        return 1
    fi
}

# Function to configure staging branch protection (Pre-Production)
configure_staging_branch() {
    echo -e "${YELLOW}Checking if staging branch exists...${NC}"

    if gh api "/repos/${REPO_OWNER}/${REPO_NAME}/branches/staging" &> /dev/null; then
        echo -e "${YELLOW}Configuring staging branch protection (Pre-Production)...${NC}"

        # Staging branch protection - Full test suite, auto-merge
        gh api \
            --method PUT \
            -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "/repos/${REPO_OWNER}/${REPO_NAME}/branches/staging/protection" \
            -f required_status_checks[strict]=true \
            -f "required_status_checks[contexts][]=unit" \
            -f "required_status_checks[contexts][]=integration" \
            -f "required_status_checks[contexts][]=e2e-tests / E2E Tests (chromium - auth)" \
            -f "required_status_checks[contexts][]=e2e-tests / E2E Tests (chromium - dashboard)" \
            -f "required_status_checks[contexts][]=code-quality / Lint and Format" \
            -f "required_status_checks[contexts][]=code-quality / Type Check" \
            -f "required_status_checks[contexts][]=security-scan / Security Scan" \
            -f required_pull_request_reviews[required_approving_review_count]=0 \
            -f enforce_admins=false \
            -f required_linear_history=true \
            -f allow_force_pushes=false \
            -f allow_deletions=false

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Staging branch protection configured${NC}"
        else
            echo -e "${RED}✗ Failed to configure staging branch protection${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⊘ Staging branch does not exist, skipping${NC}"
    fi
}

# Function to configure development branch protection (Active Development)
configure_development_branch() {
    echo -e "${YELLOW}Checking if development branch exists...${NC}"

    if gh api "/repos/${REPO_OWNER}/${REPO_NAME}/branches/development" &> /dev/null; then
        echo -e "${YELLOW}Configuring development branch protection (Active Development)...${NC}"

        # Development branch protection - Fast feedback, unit tests only
        gh api \
            --method PUT \
            -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "/repos/${REPO_OWNER}/${REPO_NAME}/branches/development/protection" \
            -f required_status_checks[strict]=false \
            -f "required_status_checks[contexts][]=unit" \
            -f required_pull_request_reviews[required_approving_review_count]=0 \
            -f enforce_admins=false \
            -f required_linear_history=false \
            -f allow_force_pushes=false \
            -f allow_deletions=false

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Development branch protection configured${NC}"
        else
            echo -e "${RED}✗ Failed to configure development branch protection${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⊘ Development branch does not exist, skipping${NC}"
    fi
}

# Function to configure feature branch protection pattern
configure_feature_branches() {
    echo -e "${YELLOW}Configuring feature/* branch protection pattern...${NC}"

    # Feature branches - Minimal protection, allow experimentation
    # Note: GitHub API doesn't support wildcard patterns directly
    # This would need to be configured via web UI or using branch rulesets

    echo -e "${YELLOW}⊘ Feature branch patterns must be configured via GitHub web UI${NC}"
    echo "   Navigate to: Settings > Branches > Add branch protection rule"
    echo "   Pattern: feature/*"
    echo "   Settings: Minimal (no required checks, allow force pushes)"
}

# Main execution
main() {
    echo -e "${GREEN}Starting branch protection configuration...${NC}"
    echo -e "${BLUE}Mode: ${MODE}${NC}"
    echo ""

    if [ "$MODE" = "three-tier" ]; then
        # Three-tier strategy: development → staging → main

        # Configure main branch (Production)
        configure_main_branch
        echo ""

        # Configure staging branch (Pre-Production)
        configure_staging_branch
        echo ""

        # Configure development branch (Active Development)
        configure_development_branch
        echo ""

        # Note about feature branches
        configure_feature_branches
        echo ""

        echo -e "${GREEN}=== Three-Tier Branch Protection Configuration Complete ===${NC}"
        echo ""
        echo "Summary:"
        echo "  ✓ main: Production (comprehensive tests + manual approval)"
        echo "  ✓ staging: Pre-Production (full test suite + auto-merge)"
        echo "  ✓ development: Active Development (unit tests only)"
        echo "  ⊘ feature/*: Configure manually via web UI"
        echo ""
        echo "Quality Gates:"
        echo "  Level 1: development → staging (auto-merge when tests pass)"
        echo "  Level 2: staging → main (manual approval required)"
        echo ""
    else
        # Solo-dev mode: main + develop

        # Configure main branch
        configure_main_branch
        echo ""

        # Configure develop branch if it exists
        configure_development_branch
        echo ""

        # Note about feature branches
        configure_feature_branches
        echo ""

        echo -e "${GREEN}=== Solo-Dev Branch Protection Configuration Complete ===${NC}"
        echo ""
        echo "Summary:"
        echo "  ✓ Main branch: Protected with required status checks and 1 approval"
        echo "  ✓ Development branch: Protected with flexible rules (if exists)"
        echo "  ⊘ Feature branches: Configure manually via web UI"
        echo ""
    fi

    echo "Next steps:"
    echo "  1. Verify protection rules in GitHub web UI"
    echo "  2. Test with sample PRs to each branch"
    echo "  3. Adjust rules as needed for your workflow"
    echo ""
    echo "To view current protection:"
    echo "  gh api /repos/${REPO_OWNER}/${REPO_NAME}/branches/main/protection"
    echo "  gh api /repos/${REPO_OWNER}/${REPO_NAME}/branches/staging/protection"
    echo "  gh api /repos/${REPO_OWNER}/${REPO_NAME}/branches/development/protection"
}

# Run main function
main

