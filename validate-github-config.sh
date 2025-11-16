#!/bin/bash

# TTA Storytelling Project - GitHub Configuration Validator
# This script validates your GitHub secrets and variables configuration

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 TTA Storytelling - GitHub Configuration Validator${NC}"
echo "=================================================="

# Check if GitHub CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI is not authenticated${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI is installed and authenticated${NC}"

# Function to check if a secret exists
check_secret() {
    local secret_name="$1"
    local description="$2"

    if gh secret list | grep -q "^$secret_name"; then
        echo -e "${GREEN}✅ Secret: $secret_name${NC} - $description"
        return 0
    else
        echo -e "${RED}❌ Secret: $secret_name${NC} - $description"
        return 1
    fi
}

# Function to check if a variable exists
check_variable() {
    local var_name="$1"
    local description="$2"

    if gh variable list | grep -q "^$var_name"; then
        local value=$(gh variable get "$var_name" 2>/dev/null || echo "Unable to retrieve")
        echo -e "${GREEN}✅ Variable: $var_name${NC} - $description (Value: $value)"
        return 0
    else
        echo -e "${RED}❌ Variable: $var_name${NC} - $description"
        return 1
    fi
}

echo -e "\n${BLUE}=== Checking Required Secrets ===${NC}"

# Error Monitoring
check_secret "SENTRY_DSN" "Error monitoring and performance tracking"

# AI Model Services
check_secret "OPENROUTER_API_KEY" "OpenRouter AI model access"

# Database Credentials
check_secret "NEO4J_STAGING_PASSWORD" "Neo4j staging database password"
check_secret "NEO4J_PRODUCTION_PASSWORD" "Neo4j production database password"
check_secret "REDIS_STAGING_PASSWORD" "Redis staging cache password"
check_secret "REDIS_PRODUCTION_PASSWORD" "Redis production cache password"

# Security
check_secret "JWT_STAGING_SECRET" "JWT signing secret for staging"
check_secret "JWT_PRODUCTION_SECRET" "JWT signing secret for production"

# Test Credentials
check_secret "TEST_USER_PASSWORD" "Test user account password"

echo -e "\n${BLUE}=== Checking Required Variables ===${NC}"

# API URLs
check_variable "STAGING_API_URL" "Staging environment API endpoint"
check_variable "PRODUCTION_API_URL" "Production environment API endpoint"

# WebSocket URLs
check_variable "STAGING_WS_URL" "Staging WebSocket endpoint"
check_variable "PRODUCTION_WS_URL" "Production WebSocket endpoint"

# Test Configuration
check_variable "TEST_USERNAME" "Test user account username"
check_variable "TEST_EMAIL" "Test user email address"

# Performance Budgets
check_variable "PERFORMANCE_BUDGET_AUTH_LOAD_TIME" "Authentication page load time budget"
check_variable "PERFORMANCE_BUDGET_DASHBOARD_LOAD_TIME" "Dashboard load time budget"
check_variable "PERFORMANCE_BUDGET_CHAT_RESPONSE_TIME" "Chat response time budget"

echo -e "\n${BLUE}=== Optional Configuration ===${NC}"

# Optional secrets
check_secret "OPENAI_API_KEY" "OpenAI API access (optional)" || echo -e "${YELLOW}  ℹ️  Optional: Only needed if using OpenAI models${NC}"
check_secret "ANTHROPIC_API_KEY" "Anthropic API access (optional)" || echo -e "${YELLOW}  ℹ️  Optional: Only needed if using Anthropic models${NC}"

# Optional variables
check_variable "OPENROUTER_PREFER_FREE_MODELS" "OpenRouter free model preference" || echo -e "${YELLOW}  ℹ️  Optional: Defaults to false${NC}"

echo -e "\n${BLUE}=== Configuration Validation ===${NC}"

# Validate API URLs format
if gh variable list | grep -q "STAGING_API_URL"; then
    STAGING_URL=$(gh variable get "STAGING_API_URL" 2>/dev/null)
    if [[ $STAGING_URL =~ ^https:// ]]; then
        echo -e "${GREEN}✅ Staging API URL uses HTTPS${NC}"
    else
        echo -e "${YELLOW}⚠️  Staging API URL should use HTTPS for security${NC}"
    fi
fi

if gh variable list | grep -q "PRODUCTION_API_URL"; then
    PRODUCTION_URL=$(gh variable get "PRODUCTION_API_URL" 2>/dev/null)
    if [[ $PRODUCTION_URL =~ ^https:// ]]; then
        echo -e "${GREEN}✅ Production API URL uses HTTPS${NC}"
    else
        echo -e "${RED}❌ Production API URL must use HTTPS${NC}"
    fi
fi

# Check for common misconfigurations
echo -e "\n${BLUE}=== Security Checks ===${NC}"

# Check if any secrets are accidentally stored as variables
POTENTIAL_SECRETS=("password" "secret" "key" "token" "dsn")
for term in "${POTENTIAL_SECRETS[@]}"; do
    if gh variable list | grep -i "$term" | grep -v -E "(url|username|email|time|budget)"; then
        echo -e "${YELLOW}⚠️  Found potentially sensitive data in variables (should be secrets):${NC}"
        gh variable list | grep -i "$term" | grep -v -E "(url|username|email|time|budget)"
    fi
done

echo -e "\n${BLUE}=== Workflow Validation ===${NC}"

# Check if workflows exist that use these secrets/variables
WORKFLOW_DIR=".github/workflows"
if [ -d "$WORKFLOW_DIR" ]; then
    echo -e "${GREEN}✅ GitHub workflows directory exists${NC}"

    # List workflow files
    WORKFLOWS=$(find "$WORKFLOW_DIR" -name "*.yml" -o -name "*.yaml" 2>/dev/null)
    if [ -n "$WORKFLOWS" ]; then
        echo -e "${GREEN}✅ Found workflow files:${NC}"
        echo "$WORKFLOWS" | sed 's/^/  - /'
    else
        echo -e "${YELLOW}⚠️  No workflow files found${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No GitHub workflows directory found${NC}"
fi

echo -e "\n${BLUE}=== Summary ===${NC}"

# Count configured items
SECRET_COUNT=$(gh secret list | wc -l)
VARIABLE_COUNT=$(gh variable list | wc -l)

echo "📊 Configuration Summary:"
echo "  - Secrets configured: $SECRET_COUNT"
echo "  - Variables configured: $VARIABLE_COUNT"

echo -e "\n${GREEN}🎉 Configuration validation completed!${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Fix any missing or misconfigured items shown above"
echo "2. Test your workflows to ensure they can access the secrets/variables"
echo "3. Set up your staging and production environments"
echo "4. Run your deployment pipeline to validate everything works"
echo ""
echo "For detailed setup instructions, see: GITHUB_SECRETS_GUIDE.md"
