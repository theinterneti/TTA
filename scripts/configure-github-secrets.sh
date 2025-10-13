#!/bin/bash
# Configure GitHub repository secrets for TTA Component Maturity Tracker
# Usage: configure-github-secrets.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CONFIG_FILE=".github/project-config.env"
OWNER="theinterneti"
REPO="TTA"

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) not found. Please install it first."
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        log_error "jq not found. Please install it first."
        exit 1
    fi

    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        log_error "Not authenticated with GitHub CLI. Run: gh auth login"
        exit 1
    fi

    log_success "Prerequisites OK"
}

# Load configuration
load_config() {
    log_info "Loading configuration from $CONFIG_FILE..."

    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Configuration file not found: $CONFIG_FILE"
        echo "Run: scripts/project-setup.sh --save-config"
        exit 1
    fi

    source "$CONFIG_FILE"

    # Validate required variables
    if [ -z "$PROJECT_ID" ]; then
        log_error "PROJECT_ID not set in $CONFIG_FILE"
        exit 1
    fi

    log_success "Configuration loaded"
}

# Get repository public key for encrypting secrets
get_repo_public_key() {
    log_info "Fetching repository public key..."

    PUBLIC_KEY_DATA=$(gh api repos/$OWNER/$REPO/actions/secrets/public-key)
    PUBLIC_KEY=$(echo "$PUBLIC_KEY_DATA" | jq -r '.key')
    PUBLIC_KEY_ID=$(echo "$PUBLIC_KEY_DATA" | jq -r '.key_id')

    if [ -z "$PUBLIC_KEY" ] || [ "$PUBLIC_KEY" = "null" ]; then
        log_error "Failed to fetch repository public key"
        exit 1
    fi

    log_success "Public key retrieved"
}

# Encrypt secret value using sodium (libsodium)
# Note: GitHub CLI handles encryption automatically, so we'll use gh secret set
set_secret() {
    local secret_name="$1"
    local secret_value="$2"

    if [ -z "$secret_value" ] || [ "$secret_value" = "null" ]; then  # pragma: allowlist secret
        log_warning "Skipping $secret_name (empty or null value)"
        return 0
    fi

    log_info "Setting secret: $secret_name"

    # Use gh secret set which handles encryption automatically
    if echo "$secret_value" | gh secret set "$secret_name" --repo "$OWNER/$REPO"; then
        log_success "Set secret: $secret_name"
        return 0
    else
        log_error "Failed to set secret: $secret_name"
        return 1
    fi
}

# Configure all secrets
configure_secrets() {
    log_info "Configuring GitHub repository secrets..."
    echo ""

    local errors=0

    # Project configuration secrets
    set_secret "PROJECT_ID" "$PROJECT_ID" || ((errors++))
    set_secret "PROJECT_NUMBER" "$PROJECT_NUMBER" || ((errors++))

    # Field ID secrets
    set_secret "FIELD_CURRENT_STAGE_ID" "$FIELD_CURRENT_STAGE_ID" || ((errors++))
    set_secret "FIELD_TARGET_STAGE_ID" "$FIELD_TARGET_STAGE_ID" || ((errors++))
    set_secret "FIELD_BLOCKER_COUNT_ID" "$FIELD_BLOCKER_COUNT_ID" || ((errors++))
    set_secret "FIELD_TEST_COVERAGE_ID" "$FIELD_TEST_COVERAGE_ID" || ((errors++))
    set_secret "FIELD_LAST_UPDATED_ID" "$FIELD_LAST_UPDATED_ID" || ((errors++))
    set_secret "FIELD_FUNCTIONAL_GROUP_ID" "$FIELD_FUNCTIONAL_GROUP_ID" || ((errors++))

    # Current Stage option ID secrets
    set_secret "OPTION_DEVELOPMENT_ID" "$OPTION_DEVELOPMENT_ID" || ((errors++))
    set_secret "OPTION_STAGING_ID" "$OPTION_STAGING_ID" || ((errors++))
    set_secret "OPTION_PRODUCTION_ID" "$OPTION_PRODUCTION_ID" || ((errors++))

    # Target Stage option ID secrets
    set_secret "OPTION_TARGET_STAGING_ID" "$OPTION_TARGET_STAGING_ID" || ((errors++))
    set_secret "OPTION_TARGET_PRODUCTION_ID" "$OPTION_TARGET_PRODUCTION_ID" || ((errors++))

    # Functional Group option ID secrets
    set_secret "OPTION_CORE_INFRA_ID" "$OPTION_CORE_INFRA_ID" || ((errors++))
    set_secret "OPTION_AI_AGENT_ID" "$OPTION_AI_AGENT_ID" || ((errors++))
    set_secret "OPTION_PLAYER_EXP_ID" "$OPTION_PLAYER_EXP_ID" || ((errors++))
    set_secret "OPTION_THERAPEUTIC_ID" "$OPTION_THERAPEUTIC_ID" || ((errors++))

    echo ""

    if [ $errors -eq 0 ]; then
        log_success "All secrets configured successfully"
        return 0
    else
        log_error "Failed to configure $errors secret(s)"
        return 1
    fi
}

# Verify secrets
verify_secrets() {
    log_info "Verifying configured secrets..."
    echo ""

    # List all secrets
    SECRETS_LIST=$(gh api repos/$OWNER/$REPO/actions/secrets | jq -r '.secrets[].name' | sort)

    # Expected secrets
    EXPECTED_SECRETS=(
        "FIELD_BLOCKER_COUNT_ID"
        "FIELD_CURRENT_STAGE_ID"
        "FIELD_FUNCTIONAL_GROUP_ID"
        "FIELD_LAST_UPDATED_ID"
        "FIELD_TARGET_STAGE_ID"
        "FIELD_TEST_COVERAGE_ID"
        "OPTION_AI_AGENT_ID"
        "OPTION_CORE_INFRA_ID"
        "OPTION_DEVELOPMENT_ID"
        "OPTION_PLAYER_EXP_ID"
        "OPTION_PRODUCTION_ID"
        "OPTION_STAGING_ID"
        "OPTION_TARGET_PRODUCTION_ID"
        "OPTION_TARGET_STAGING_ID"
        "OPTION_THERAPEUTIC_ID"
        "PROJECT_ID"
        "PROJECT_NUMBER"
    )

    local missing=0

    echo -e "${BLUE}Configured Secrets:${NC}"
    for secret in "${EXPECTED_SECRETS[@]}"; do
        if echo "$SECRETS_LIST" | grep -q "^$secret$"; then
            echo -e "  ${GREEN}✓${NC} $secret"
        else
            echo -e "  ${RED}✗${NC} $secret (missing)"
            ((missing++))
        fi
    done

    echo ""

    # Check for GH_PROJECT_TOKEN
    if echo "$SECRETS_LIST" | grep -q "^GH_PROJECT_TOKEN$"; then
        echo -e "${GREEN}✓${NC} GH_PROJECT_TOKEN is configured"
    else
        echo -e "${YELLOW}⚠${NC} GH_PROJECT_TOKEN is not configured"
        echo "  You need to manually add this secret with a GitHub Personal Access Token"
        echo "  that has 'repo' and 'project' scopes."
        echo ""
        echo "  To create a token:"
        echo "    1. Go to: https://github.com/settings/tokens/new"
        echo "    2. Select scopes: repo, project"
        echo "    3. Generate token"
        echo "    4. Run: echo 'YOUR_TOKEN' | gh secret set GH_PROJECT_TOKEN --repo $OWNER/$REPO"
    fi

    echo ""

    if [ $missing -eq 0 ]; then
        log_success "All expected secrets are configured"
        return 0
    else
        log_error "$missing secret(s) missing"
        return 1
    fi
}

# Main execution
main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}Configure GitHub Repository Secrets${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Repository: $OWNER/$REPO"
    echo ""

    check_prerequisites
    load_config
    configure_secrets
    verify_secrets

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✓ Configuration Complete!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "View secrets at:"
    echo "  https://github.com/$OWNER/$REPO/settings/secrets/actions"
    echo ""
}

main
