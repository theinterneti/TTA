#!/bin/bash

# Repository Configuration Validation Script for TTA E2E Testing
# This script validates that all required GitHub repository settings are configured

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

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  TTA Repository Config Validation${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

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

echo -e "${CHECK} GitHub CLI is installed and authenticated"

# Get repository information
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login')
REPO_NAME=$(gh repo view --json name --jq '.name')
REPO_FULL_NAME="${REPO_OWNER}/${REPO_NAME}"

echo -e "${INFO} Repository: ${REPO_FULL_NAME}"
echo ""

# Required secrets
REQUIRED_SECRETS=(
    "STAGING_DEPLOY_KEY"
    "PRODUCTION_DEPLOY_KEY"
    "OPENROUTER_API_KEY"
    "NEO4J_CLOUD_PASSWORD"
    "REDIS_CLOUD_PASSWORD"
    "SENTRY_DSN"
    "SLACK_WEBHOOK_URL"
    "TEST_USER_PASSWORD"
    "PREMIUM_TEST_PASSWORD"
)

# Required variables
REQUIRED_VARIABLES=(
    "STAGING_API_URL"
    "PRODUCTION_API_URL"
    "STAGING_WS_URL"
    "PRODUCTION_WS_URL"
    "TEST_USERNAME"
    "TEST_EMAIL"
    "PREMIUM_TEST_USERNAME"
    "PREMIUM_TEST_EMAIL"
    "PERFORMANCE_BUDGET_AUTH_LOAD_TIME"
    "PERFORMANCE_BUDGET_DASHBOARD_LOAD_TIME"
    "PERFORMANCE_BUDGET_CHAT_RESPONSE_TIME"
    "ENABLE_VISUAL_REGRESSION_TESTS"
    "ENABLE_PERFORMANCE_BUDGETS"
    "ENABLE_SECURITY_SCANNING"
    "NOTIFICATION_CHANNELS"
    "CRITICAL_FAILURE_NOTIFICATION"
)

# Required environments
REQUIRED_ENVIRONMENTS=(
    "development"
    "staging"
    "production"
    "test"
)

# Function to check secrets
check_secrets() {
    echo -e "${BLUE}Checking Repository Secrets...${NC}"

    # Get list of secrets
    SECRETS_JSON=$(gh api repos/${REPO_FULL_NAME}/actions/secrets --jq '.secrets[].name')

    MISSING_SECRETS=()

    for secret in "${REQUIRED_SECRETS[@]}"; do
        if echo "$SECRETS_JSON" | grep -q "^${secret}$"; then
            echo -e "${CHECK} Secret: ${secret}"
        else
            echo -e "${CROSS} Missing secret: ${secret}"
            MISSING_SECRETS+=("$secret")
        fi
    done

    if [ ${#MISSING_SECRETS[@]} -eq 0 ]; then
        echo -e "${CHECK} All required secrets are configured"
    else
        echo -e "${WARNING} ${#MISSING_SECRETS[@]} secrets are missing"
    fi

    echo ""
}

# Function to check variables
check_variables() {
    echo -e "${BLUE}Checking Repository Variables...${NC}"

    # Get list of variables
    VARIABLES_JSON=$(gh api repos/${REPO_FULL_NAME}/actions/variables --jq '.variables[].name')

    MISSING_VARIABLES=()

    for variable in "${REQUIRED_VARIABLES[@]}"; do
        if echo "$VARIABLES_JSON" | grep -q "^${variable}$"; then
            echo -e "${CHECK} Variable: ${variable}"
        else
            echo -e "${CROSS} Missing variable: ${variable}"
            MISSING_VARIABLES+=("$variable")
        fi
    done

    if [ ${#MISSING_VARIABLES[@]} -eq 0 ]; then
        echo -e "${CHECK} All required variables are configured"
    else
        echo -e "${WARNING} ${#MISSING_VARIABLES[@]} variables are missing"
    fi

    echo ""
}

# Function to check environments
check_environments() {
    echo -e "${BLUE}Checking Repository Environments...${NC}"

    # Get list of environments
    ENVIRONMENTS_JSON=$(gh api repos/${REPO_FULL_NAME}/environments --jq '.environments[].name' 2>/dev/null || echo "")

    MISSING_ENVIRONMENTS=()

    for env in "${REQUIRED_ENVIRONMENTS[@]}"; do
        if echo "$ENVIRONMENTS_JSON" | grep -q "^${env}$"; then
            echo -e "${CHECK} Environment: ${env}"
        else
            echo -e "${CROSS} Missing environment: ${env}"
            MISSING_ENVIRONMENTS+=("$env")
        fi
    done

    if [ ${#MISSING_ENVIRONMENTS[@]} -eq 0 ]; then
        echo -e "${CHECK} All required environments are configured"
    else
        echo -e "${WARNING} ${#MISSING_ENVIRONMENTS[@]} environments are missing"
    fi

    echo ""
}

# Function to check branch protection
check_branch_protection() {
    echo -e "${BLUE}Checking Branch Protection Rules...${NC}"

    # Check main branch protection
    MAIN_PROTECTION=$(gh api repos/${REPO_FULL_NAME}/branches/main/protection 2>/dev/null || echo "null")

    if [ "$MAIN_PROTECTION" != "null" ]; then
        echo -e "${CHECK} Main branch protection is enabled"

        # Check required status checks
        REQUIRED_CHECKS=$(echo "$MAIN_PROTECTION" | jq -r '.required_status_checks.contexts[]?' 2>/dev/null || echo "")
        if echo "$REQUIRED_CHECKS" | grep -q "E2E Tests"; then
            echo -e "${CHECK} E2E Tests are required for main branch"
        else
            echo -e "${WARNING} E2E Tests are not required for main branch"
        fi

        # Check required reviews
        REQUIRED_REVIEWS=$(echo "$MAIN_PROTECTION" | jq -r '.required_pull_request_reviews.required_approving_review_count' 2>/dev/null || echo "0")
        if [ "$REQUIRED_REVIEWS" -ge 2 ]; then
            echo -e "${CHECK} Main branch requires ${REQUIRED_REVIEWS} reviews"
        else
            echo -e "${WARNING} Main branch should require at least 2 reviews (currently: ${REQUIRED_REVIEWS})"
        fi
    else
        echo -e "${CROSS} Main branch protection is not enabled"
    fi

    # Check development branch protection
    DEVELOPMENT_PROTECTION=$(gh api repos/${REPO_FULL_NAME}/branches/development/protection 2>/dev/null || echo "null")

    if [ "$DEVELOPMENT_PROTECTION" != "null" ]; then
        echo -e "${CHECK} Development branch protection is enabled"
    else
        echo -e "${WARNING} Development branch protection is not enabled"
    fi

    # Check staging branch protection
    STAGING_PROTECTION=$(gh api repos/${REPO_FULL_NAME}/branches/staging/protection 2>/dev/null || echo "null")

    if [ "$STAGING_PROTECTION" != "null" ]; then
        echo -e "${CHECK} Staging branch protection is enabled"
    else
        echo -e "${WARNING} Staging branch protection is not enabled"
    fi

    echo ""
}

# Function to check workflow files
check_workflow_files() {
    echo -e "${BLUE}Checking Workflow Files...${NC}"

    REQUIRED_WORKFLOWS=(
        ".github/workflows/e2e-tests.yml"
        ".github/workflows/security-scan.yml"
    )

    for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
        if [ -f "$workflow" ]; then
            echo -e "${CHECK} Workflow: $(basename $workflow)"
        else
            echo -e "${CROSS} Missing workflow: $(basename $workflow)"
        fi
    done

    echo ""
}

# Function to check configuration files
check_config_files() {
    echo -e "${BLUE}Checking Configuration Files...${NC}"

    REQUIRED_CONFIG_FILES=(
        ".github/repository-config/secrets-configuration.yml"
        ".github/repository-config/environments-configuration.yml"
        ".github/repository-config/branch-protection-rules.yml"
        "scripts/check-performance-budget.js"
        ".env.test.template"
    )

    for config in "${REQUIRED_CONFIG_FILES[@]}"; do
        if [ -f "$config" ]; then
            echo -e "${CHECK} Config: $(basename $config)"
        else
            echo -e "${CROSS} Missing config: $(basename $config)"
        fi
    done

    echo ""
}

# Function to generate setup instructions
generate_setup_instructions() {
    echo -e "${BLUE}Setup Instructions${NC}"
    echo -e "${BLUE}==================${NC}"
    echo ""

    if [ ${#MISSING_SECRETS[@]} -gt 0 ]; then
        echo -e "${YELLOW}Missing Secrets:${NC}"
        for secret in "${MISSING_SECRETS[@]}"; do
            echo "  gh secret set $secret --body \"your-secret-value\""
        done
        echo ""
    fi

    if [ ${#MISSING_VARIABLES[@]} -gt 0 ]; then
        echo -e "${YELLOW}Missing Variables:${NC}"
        for variable in "${MISSING_VARIABLES[@]}"; do
            echo "  gh variable set $variable --body \"your-variable-value\""
        done
        echo ""
    fi

    if [ ${#MISSING_ENVIRONMENTS[@]} -gt 0 ]; then
        echo -e "${YELLOW}Missing Environments:${NC}"
        echo "  Create environments in GitHub repository settings:"
        for env in "${MISSING_ENVIRONMENTS[@]}"; do
            echo "  - $env"
        done
        echo ""
    fi

    echo -e "${INFO} For detailed setup instructions, see:"
    echo "  - .github/repository-config/secrets-configuration.yml"
    echo "  - .github/repository-config/environments-configuration.yml"
    echo "  - .github/repository-config/branch-protection-rules.yml"
    echo ""
}

# Function to run validation tests
run_validation_tests() {
    echo -e "${BLUE}Running Validation Tests...${NC}"

    # Test performance budget script
    if [ -f "scripts/check-performance-budget.js" ]; then
        echo -e "${INFO} Testing performance budget script..."
        if node scripts/check-performance-budget.js --help &>/dev/null; then
            echo -e "${CHECK} Performance budget script is executable"
        else
            echo -e "${WARNING} Performance budget script may have issues"
        fi
    fi

    # Test workflow syntax
    if command -v yamllint &> /dev/null; then
        echo -e "${INFO} Validating workflow YAML syntax..."
        if yamllint .github/workflows/*.yml &>/dev/null; then
            echo -e "${CHECK} Workflow YAML syntax is valid"
        else
            echo -e "${WARNING} Workflow YAML syntax issues detected"
        fi
    else
        echo -e "${INFO} yamllint not installed, skipping YAML validation"
    fi

    echo ""
}

# Main execution
main() {
    check_secrets
    check_variables
    check_environments
    check_branch_protection
    check_workflow_files
    check_config_files
    run_validation_tests

    # Calculate overall status
    TOTAL_ISSUES=$((${#MISSING_SECRETS[@]} + ${#MISSING_VARIABLES[@]} + ${#MISSING_ENVIRONMENTS[@]}))

    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Validation Summary${NC}"
    echo -e "${BLUE}================================${NC}"

    if [ $TOTAL_ISSUES -eq 0 ]; then
        echo -e "${CHECK} Repository configuration is complete!"
        echo -e "${GREEN}Ready for production deployment${NC}"
    else
        echo -e "${WARNING} Found $TOTAL_ISSUES configuration issues"
        echo -e "${YELLOW}Setup required before production deployment${NC}"
        echo ""
        generate_setup_instructions
    fi

    echo ""
    echo -e "${INFO} For more information, visit:"
    echo "  https://docs.github.com/en/actions/security-guides/encrypted-secrets"
    echo "  https://docs.github.com/en/actions/learn-github-actions/variables"
    echo "  https://docs.github.com/en/actions/deployment/targeting-different-environments"
}

# Run main function
main
