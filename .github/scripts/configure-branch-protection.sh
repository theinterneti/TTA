#!/bin/bash
# Configure Branch Protection Rules for TTA Repository
# Solo Developer Optimized Configuration
#
# This script configures branch protection rules via GitHub API
# Designed for solo developer workflow with practical protections

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Repository information
REPO_OWNER="theinterneti"
REPO_NAME="TTA"

echo -e "${GREEN}=== TTA Branch Protection Configuration ===${NC}"
echo "Repository: ${REPO_OWNER}/${REPO_NAME}"
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

# Function to configure main branch protection
configure_main_branch() {
    echo -e "${YELLOW}Configuring main branch protection...${NC}"
    
    # Main branch protection - Solo developer optimized
    # - Require status checks (only existing workflows)
    # - Require 1 approval (can be self-approved or use auto-merge)
    # - No force pushes
    # - Linear history preferred
    # - Allow admins to bypass (for emergencies)
    
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
        -f block_creations=false \
        -f required_conversation_resolution=true \
        -f lock_branch=false \
        -f allow_fork_syncing=true
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Main branch protection configured${NC}"
    else
        echo -e "${RED}✗ Failed to configure main branch protection${NC}"
        return 1
    fi
}

# Function to configure develop branch protection (if it exists)
configure_develop_branch() {
    echo -e "${YELLOW}Checking if develop branch exists...${NC}"
    
    if gh api "/repos/${REPO_OWNER}/${REPO_NAME}/branches/develop" &> /dev/null; then
        echo -e "${YELLOW}Configuring develop branch protection...${NC}"
        
        # Develop branch protection - More flexible for experimentation
        gh api \
            --method PUT \
            -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "/repos/${REPO_OWNER}/${REPO_NAME}/branches/develop/protection" \
            -f required_status_checks[strict]=false \
            -f "required_status_checks[contexts][]=unit" \
            -f required_pull_request_reviews[required_approving_review_count]=0 \
            -f enforce_admins=false \
            -f required_linear_history=false \
            -f allow_force_pushes=false \
            -f allow_deletions=false
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Develop branch protection configured${NC}"
        else
            echo -e "${RED}✗ Failed to configure develop branch protection${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⊘ Develop branch does not exist, skipping${NC}"
    fi
}

# Function to configure feature branch protection pattern
configure_feature_branches() {
    echo -e "${YELLOW}Configuring feat/* branch protection pattern...${NC}"
    
    # Feature branches - Minimal protection, allow experimentation
    # Note: GitHub API doesn't support wildcard patterns directly
    # This would need to be configured via web UI or using branch rulesets
    
    echo -e "${YELLOW}⊘ Feature branch patterns must be configured via GitHub web UI${NC}"
    echo "   Navigate to: Settings > Branches > Add branch protection rule"
    echo "   Pattern: feat/*"
    echo "   Settings: Minimal (no required checks, allow force pushes)"
}

# Main execution
main() {
    echo -e "${GREEN}Starting branch protection configuration...${NC}"
    echo ""
    
    # Configure main branch
    configure_main_branch
    echo ""
    
    # Configure develop branch if it exists
    configure_develop_branch
    echo ""
    
    # Note about feature branches
    configure_feature_branches
    echo ""
    
    echo -e "${GREEN}=== Branch Protection Configuration Complete ===${NC}"
    echo ""
    echo "Summary:"
    echo "  ✓ Main branch: Protected with required status checks and 1 approval"
    echo "  ✓ Develop branch: Protected with flexible rules (if exists)"
    echo "  ⊘ Feature branches: Configure manually via web UI"
    echo ""
    echo "Next steps:"
    echo "  1. Verify protection rules in GitHub web UI"
    echo "  2. Test with a sample PR to main branch"
    echo "  3. Adjust rules as needed for your workflow"
    echo ""
    echo "To view current protection:"
    echo "  gh api /repos/${REPO_OWNER}/${REPO_NAME}/branches/main/protection"
}

# Run main function
main

