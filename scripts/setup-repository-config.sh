#!/bin/bash

# Repository Configuration Setup Script for TTA E2E Testing
# This script automates the setup of GitHub repository settings

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emojis
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  TTA Repository Setup${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${INFO} Checking prerequisites..."

    # Check if GitHub CLI is installed
    if ! command -v gh &> /dev/null; then
        echo -e "${CROSS} GitHub CLI (gh) is not installed"
        echo -e "${INFO} Please install GitHub CLI: https://cli.github.com/"
        exit 1
    fi

    # Check if user is authenticated
    if ! gh auth status &> /dev/null; then
        echo -e "${CROSS} Not authenticated with GitHub CLI"
        echo -e "${INFO} Please run: gh auth login"
        exit 1
    fi

    echo -e "${CHECK} Prerequisites satisfied"
    echo ""
}

# Get repository information
get_repo_info() {
    REPO_OWNER=$(gh repo view --json owner --jq '.owner.login')
    REPO_NAME=$(gh repo view --json name --jq '.name')
    REPO_FULL_NAME="${REPO_OWNER}/${REPO_NAME}"

    echo -e "${INFO} Repository: ${REPO_FULL_NAME}"
    echo ""
}

# Setup repository variables
setup_variables() {
    echo -e "${BLUE}Setting up Repository Variables...${NC}"

    # Default values for variables
    declare -A VARIABLES=(
        ["STAGING_API_URL"]="https://staging-api.tta.example.com"
        ["PRODUCTION_API_URL"]="https://api.tta.example.com"
        ["STAGING_WS_URL"]="wss://staging-ws.tta.example.com"
        ["PRODUCTION_WS_URL"]="wss://ws.tta.example.com"
        ["TEST_USERNAME"]="e2e_test_user"
        ["TEST_EMAIL"]="e2e-test@tta.example.com"
        ["PREMIUM_TEST_USERNAME"]="e2e_premium_user"
        ["PREMIUM_TEST_EMAIL"]="e2e-premium@tta.example.com"
        ["PERFORMANCE_BUDGET_AUTH_LOAD_TIME"]="2000"
        ["PERFORMANCE_BUDGET_DASHBOARD_LOAD_TIME"]="3000"
        ["PERFORMANCE_BUDGET_CHAT_RESPONSE_TIME"]="1500"
        ["ENABLE_VISUAL_REGRESSION_TESTS"]="true"
        ["ENABLE_PERFORMANCE_BUDGETS"]="true"
        ["ENABLE_SECURITY_SCANNING"]="true"
        ["NOTIFICATION_CHANNELS"]="slack"
        ["CRITICAL_FAILURE_NOTIFICATION"]="true"
    )

    for var_name in "${!VARIABLES[@]}"; do
        var_value="${VARIABLES[$var_name]}"

        # Check if variable already exists
        if gh variable list | grep -q "^${var_name}"; then
            echo -e "${WARNING} Variable ${var_name} already exists, skipping"
        else
            if gh variable set "$var_name" --body "$var_value"; then
                echo -e "${CHECK} Set variable: ${var_name}"
            else
                echo -e "${CROSS} Failed to set variable: ${var_name}"
            fi
        fi
    done

    echo ""
}

# Setup repository secrets (with placeholder values)
setup_secrets() {
    echo -e "${BLUE}Setting up Repository Secrets...${NC}"
    echo -e "${WARNING} Setting placeholder values - you must update these with real values!"

    # Secrets with placeholder values
    declare -A SECRETS=(
        ["STAGING_DEPLOY_KEY"]="PLACEHOLDER_SSH_KEY"
        ["PRODUCTION_DEPLOY_KEY"]="PLACEHOLDER_SSH_KEY"
        ["OPENROUTER_API_KEY"]="PLACEHOLDER_API_KEY"
        ["NEO4J_CLOUD_PASSWORD"]="PLACEHOLDER_PASSWORD"
        ["REDIS_CLOUD_PASSWORD"]="PLACEHOLDER_PASSWORD"
        ["SENTRY_DSN"]="PLACEHOLDER_SENTRY_DSN"
        ["SLACK_WEBHOOK_URL"]="PLACEHOLDER_WEBHOOK_URL"
        ["TEST_USER_PASSWORD"]="test_password_123"
        ["PREMIUM_TEST_PASSWORD"]="premium_test_password_123"
    )

    for secret_name in "${!SECRETS[@]}"; do
        secret_value="${SECRETS[$secret_name]}"

        # Check if secret already exists
        if gh secret list | grep -q "^${secret_name}"; then
            echo -e "${WARNING} Secret ${secret_name} already exists, skipping"
        else
            if gh secret set "$secret_name" --body "$secret_value"; then
                echo -e "${CHECK} Set secret: ${secret_name} (placeholder)"
            else
                echo -e "${CROSS} Failed to set secret: ${secret_name}"
            fi
        fi
    done

    echo ""
    echo -e "${WARNING} IMPORTANT: Update all secrets with real values before production use!"
    echo ""
}

# Setup environments
setup_environments() {
    echo -e "${BLUE}Setting up Repository Environments...${NC}"

    ENVIRONMENTS=("development" "staging" "production" "test")

    for env in "${ENVIRONMENTS[@]}"; do
        echo -e "${INFO} Creating environment: ${env}"

        # Create environment (this will fail if it already exists, which is fine)
        gh api repos/${REPO_FULL_NAME}/environments/${env} \
            --method PUT \
            --field wait_timer=0 \
            --field prevent_self_review=false \
            --field reviewers='[]' \
            --field deployment_branch_policy='{"protected_branches":false,"custom_branch_policies":false}' \
            2>/dev/null && echo -e "${CHECK} Created environment: ${env}" || echo -e "${WARNING} Environment ${env} may already exist"
    done

    echo ""
}

# Setup branch protection rules
setup_branch_protection() {
    echo -e "${BLUE}Setting up Branch Protection Rules...${NC}"

    # Main branch protection
    echo -e "${INFO} Setting up main branch protection..."
    gh api repos/${REPO_FULL_NAME}/branches/main/protection \
        --method PUT \
        --field required_status_checks='{
            "strict": true,
            "contexts": [
                "E2E Tests (chromium - auth)",
                "E2E Tests (chromium - dashboard)",
                "Comprehensive Accessibility Audit",
                "Performance Benchmarks",
                "Security Scan"
            ]
        }' \
        --field enforce_admins=false \
        --field required_pull_request_reviews='{
            "required_approving_review_count": 2,
            "dismiss_stale_reviews": true,
            "require_code_owner_reviews": true,
            "require_last_push_approval": true
        }' \
        --field restrictions=null \
        --field allow_force_pushes=false \
        --field allow_deletions=false \
        --field required_linear_history=true \
        2>/dev/null && echo -e "${CHECK} Main branch protection configured" || echo -e "${WARNING} Failed to configure main branch protection"

    # Development branch protection
    echo -e "${INFO} Setting up development branch protection..."
    gh api repos/${REPO_FULL_NAME}/branches/development/protection \
        --method PUT \
        --field required_status_checks='{
            "strict": true,
            "contexts": [
                "lint / Lint with Ruff",
                "format-check / Format Check",
                "type-check / Type Check with mypy",
                "unit"
            ]
        }' \
        --field enforce_admins=false \
        --field required_pull_request_reviews=null \
        --field restrictions=null \
        --field allow_force_pushes=false \
        --field allow_deletions=false \
        2>/dev/null && echo -e "${CHECK} Development branch protection configured" || echo -e "${WARNING} Failed to configure development branch protection (branch may not exist)"

    # Staging branch protection
    echo -e "${INFO} Setting up staging branch protection..."
    gh api repos/${REPO_FULL_NAME}/branches/staging/protection \
        --method PUT \
        --field required_status_checks='{
            "strict": true,
            "contexts": [
                "lint / Lint with Ruff",
                "format-check / Format Check",
                "type-check / Type Check with mypy",
                "unit",
                "integration",
                "E2E Tests (chromium - auth)",
                "E2E Tests (chromium - dashboard)"
            ]
        }' \
        --field enforce_admins=false \
        --field required_pull_request_reviews=null \
        --field restrictions=null \
        --field allow_force_pushes=false \
        --field allow_deletions=false \
        2>/dev/null && echo -e "${CHECK} Staging branch protection configured" || echo -e "${WARNING} Failed to configure staging branch protection (branch may not exist)"

    echo ""
}

# Enable GitHub Pages for test reports
setup_github_pages() {
    echo -e "${BLUE}Setting up GitHub Pages for test reports...${NC}"

    gh api repos/${REPO_FULL_NAME}/pages \
        --method POST \
        --field source='{
            "branch": "gh-pages",
            "path": "/"
        }' \
        2>/dev/null && echo -e "${CHECK} GitHub Pages enabled" || echo -e "${WARNING} GitHub Pages may already be enabled or gh-pages branch doesn't exist"

    echo ""
}

# Create CODEOWNERS file
create_codeowners() {
    echo -e "${BLUE}Creating CODEOWNERS file...${NC}"

    if [ ! -f ".github/CODEOWNERS" ]; then
        cat > .github/CODEOWNERS << 'EOF'
# TTA Repository Code Owners
# These users/teams will be automatically requested for review when PRs are opened

# Global owners
* @tta-core-team

# E2E Testing
/tests/e2e/ @tta-qa-team @tta-core-team
/.github/workflows/ @tta-devops-team @tta-core-team
/scripts/ @tta-devops-team @tta-core-team

# Frontend
/src/player_experience/frontend/ @tta-frontend-team @tta-core-team

# Configuration
/.github/repository-config/ @tta-devops-team @tta-core-team
/playwright.config.ts @tta-qa-team @tta-core-team

# Security
/.github/workflows/security-scan.yml @tta-security-team @tta-core-team
/scripts/check-performance-budget.js @tta-performance-team @tta-core-team
EOF
        echo -e "${CHECK} Created CODEOWNERS file"
    else
        echo -e "${WARNING} CODEOWNERS file already exists"
    fi

    echo ""
}

# Create issue templates
create_issue_templates() {
    echo -e "${BLUE}Creating issue templates...${NC}"

    mkdir -p .github/ISSUE_TEMPLATE

    # Bug report template
    if [ ! -f ".github/ISSUE_TEMPLATE/bug_report.yml" ]; then
        cat > .github/ISSUE_TEMPLATE/bug_report.yml << 'EOF'
name: Bug Report
description: Report a bug in the TTA application
title: "[BUG] "
labels: ["bug", "needs-triage"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!

  - type: textarea
    id: what-happened
    attributes:
      label: What happened?
      description: A clear description of what the bug is
      placeholder: Tell us what you see!
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
      description: Steps to reproduce the behavior
      placeholder: |
        1. Go to '...'
        2. Click on '....'
        3. Scroll down to '....'
        4. See error
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
      description: A clear description of what you expected to happen
    validations:
      required: true

  - type: dropdown
    id: browsers
    attributes:
      label: What browsers are you seeing the problem on?
      multiple: true
      options:
        - Firefox
        - Chrome
        - Safari
        - Microsoft Edge

  - type: textarea
    id: logs
    attributes:
      label: Relevant log output
      description: Please copy and paste any relevant log output
      render: shell
EOF
        echo -e "${CHECK} Created bug report template"
    else
        echo -e "${WARNING} Bug report template already exists"
    fi

    # Feature request template
    if [ ! -f ".github/ISSUE_TEMPLATE/feature_request.yml" ]; then
        cat > .github/ISSUE_TEMPLATE/feature_request.yml << 'EOF'
name: Feature Request
description: Suggest an idea for the TTA application
title: "[FEATURE] "
labels: ["enhancement", "needs-triage"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for suggesting a new feature!

  - type: textarea
    id: problem
    attributes:
      label: Is your feature request related to a problem?
      description: A clear description of what the problem is
      placeholder: I'm always frustrated when...

  - type: textarea
    id: solution
    attributes:
      label: Describe the solution you'd like
      description: A clear description of what you want to happen
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Describe alternatives you've considered
      description: A clear description of any alternative solutions or features you've considered

  - type: textarea
    id: context
    attributes:
      label: Additional context
      description: Add any other context or screenshots about the feature request here
EOF
        echo -e "${CHECK} Created feature request template"
    else
        echo -e "${WARNING} Feature request template already exists"
    fi

    echo ""
}

# Generate summary report
generate_summary() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Setup Complete!${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""

    echo -e "${ROCKET} Repository configuration has been set up!"
    echo ""

    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Update placeholder secrets with real values:"
    echo "   - STAGING_DEPLOY_KEY"
    echo "   - PRODUCTION_DEPLOY_KEY"
    echo "   - OPENROUTER_API_KEY"
    echo "   - NEO4J_CLOUD_PASSWORD"
    echo "   - REDIS_CLOUD_PASSWORD"
    echo "   - SENTRY_DSN"
    echo "   - SLACK_WEBHOOK_URL"
    echo ""

    echo "2. Create teams in your GitHub organization:"
    echo "   - tta-core-team"
    echo "   - tta-qa-team"
    echo "   - tta-frontend-team"
    echo "   - tta-devops-team"
    echo "   - tta-security-team"
    echo "   - tta-performance-team"
    echo ""

    echo "3. Update environment-specific URLs in variables:"
    echo "   - STAGING_API_URL"
    echo "   - PRODUCTION_API_URL"
    echo "   - STAGING_WS_URL"
    echo "   - PRODUCTION_WS_URL"
    echo ""

    echo "4. Test the configuration:"
    echo "   ./scripts/validate-repository-config.sh"
    echo ""

    echo "5. Create a test PR to verify E2E tests run correctly"
    echo ""

    echo -e "${INFO} For detailed configuration information, see:"
    echo "  - .github/repository-config/secrets-configuration.yml"
    echo "  - .github/repository-config/environments-configuration.yml"
    echo "  - .github/repository-config/branch-protection-rules.yml"
}

# Main execution
main() {
    check_prerequisites
    get_repo_info

    echo -e "${WARNING} This script will configure your GitHub repository with default settings."
    echo -e "${WARNING} Some settings may overwrite existing configurations."
    echo ""
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi

    echo ""

    setup_variables
    setup_secrets
    setup_environments
    setup_branch_protection
    setup_github_pages
    create_codeowners
    create_issue_templates

    generate_summary
}

# Run main function
main "$@"
