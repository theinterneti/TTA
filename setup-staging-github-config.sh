#!/bin/bash

# 🌐 TTA Staging GitHub Configuration Setup Script
# This script configures GitHub secrets and variables for staging deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="theinterneti.com"
STAGING_PREFIX="staging-tta"
API_PREFIX="api-staging"
CLINICAL_PREFIX="clinical-staging"
ADMIN_PREFIX="admin-staging"

echo -e "${BLUE}🌐 TTA Staging GitHub Configuration Setup${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed.${NC}"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub CLI.${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI is installed and authenticated${NC}"
echo ""

# Function to prompt for input with default
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local result

    read -p "$prompt [$default]: " result
    echo "${result:-$default}"
}

# Function to prompt for sensitive input
prompt_sensitive() {
    local prompt="$1"
    local result

    read -s -p "$prompt: " result
    echo ""
    echo "$result"
}

echo -e "${YELLOW}📝 Please provide the following information:${NC}"
echo ""

# Staging URLs (with defaults)
STAGING_WEB_URL=$(prompt_with_default "Staging Web URL" "https://${STAGING_PREFIX}.${DOMAIN}")
STAGING_API_URL=$(prompt_with_default "Staging API URL" "https://${API_PREFIX}.tta.${DOMAIN}")
STAGING_CLINICAL_URL=$(prompt_with_default "Staging Clinical URL" "https://${CLINICAL_PREFIX}.tta.${DOMAIN}")
STAGING_ADMIN_URL=$(prompt_with_default "Staging Admin URL" "https://${ADMIN_PREFIX}.tta.${DOMAIN}")

echo ""
echo -e "${YELLOW}🔐 Database and Infrastructure Configuration:${NC}"

# Database URLs
STAGING_DATABASE_URL=$(prompt_sensitive "Staging Database URL (PostgreSQL)")
STAGING_REDIS_URL=$(prompt_with_default "Staging Redis URL" "redis://staging-redis.${DOMAIN}:6379")
STAGING_NEO4J_URL=$(prompt_with_default "Staging Neo4j URL" "bolt://staging-neo4j.${DOMAIN}:7687")
STAGING_NEO4J_PASSWORD=$(prompt_sensitive "Staging Neo4j Password")

echo ""
echo -e "${YELLOW}📊 Monitoring Configuration:${NC}"

# Sentry configuration
STAGING_SENTRY_DSN=$(prompt_sensitive "Staging Sentry DSN")

echo ""
echo -e "${YELLOW}⚙️ Application Configuration:${NC}"

# Application settings
STAGING_JWT_SECRET=$(prompt_sensitive "Staging JWT Secret Key (min 32 chars)")
STAGING_OPENROUTER_API_KEY=$(prompt_sensitive "OpenRouter API Key (optional)")

echo ""
echo -e "${BLUE}🚀 Setting up GitHub Secrets and Variables...${NC}"
echo ""

# Set GitHub Secrets
echo -e "${GREEN}Setting GitHub Secrets...${NC}"

gh secret set STAGING_API_URL --body "$STAGING_API_URL"
echo "✅ STAGING_API_URL set"

gh secret set STAGING_WEB_URL --body "$STAGING_WEB_URL"
echo "✅ STAGING_WEB_URL set"

gh secret set STAGING_CLINICAL_URL --body "$STAGING_CLINICAL_URL"
echo "✅ STAGING_CLINICAL_URL set"

gh secret set STAGING_ADMIN_URL --body "$STAGING_ADMIN_URL"
echo "✅ STAGING_ADMIN_URL set"

gh secret set STAGING_DATABASE_URL --body "$STAGING_DATABASE_URL"
echo "✅ STAGING_DATABASE_URL set"

gh secret set STAGING_REDIS_URL --body "$STAGING_REDIS_URL"
echo "✅ STAGING_REDIS_URL set"

gh secret set STAGING_NEO4J_URL --body "$STAGING_NEO4J_URL"
echo "✅ STAGING_NEO4J_URL set"

gh secret set STAGING_NEO4J_PASSWORD --body "$STAGING_NEO4J_PASSWORD"
echo "✅ STAGING_NEO4J_PASSWORD set"

gh secret set STAGING_SENTRY_DSN --body "$STAGING_SENTRY_DSN"
echo "✅ STAGING_SENTRY_DSN set"

gh secret set STAGING_JWT_SECRET --body "$STAGING_JWT_SECRET"
echo "✅ STAGING_JWT_SECRET set"

if [ -n "$STAGING_OPENROUTER_API_KEY" ]; then
    gh secret set STAGING_OPENROUTER_API_KEY --body "$STAGING_OPENROUTER_API_KEY"
    echo "✅ STAGING_OPENROUTER_API_KEY set"
fi

echo ""
echo -e "${GREEN}Setting GitHub Variables...${NC}"

# Set GitHub Variables
gh variable set STAGING_ENVIRONMENT --body "staging"
echo "✅ STAGING_ENVIRONMENT set"

gh variable set STAGING_DEBUG --body "false"
echo "✅ STAGING_DEBUG set"

gh variable set STAGING_LOG_LEVEL --body "INFO"
echo "✅ STAGING_LOG_LEVEL set"

gh variable set STAGING_MAX_CONCURRENT_SESSIONS --body "500"
echo "✅ STAGING_MAX_CONCURRENT_SESSIONS set"

gh variable set STAGING_RATE_LIMIT_CALLS --body "1000"
echo "✅ STAGING_RATE_LIMIT_CALLS set"

gh variable set STAGING_RATE_LIMIT_PERIOD --body "60"
echo "✅ STAGING_RATE_LIMIT_PERIOD set"

# Feature flags for staging
gh variable set STAGING_FEATURE_REAL_TIME_MONITORING --body "true"
echo "✅ STAGING_FEATURE_REAL_TIME_MONITORING set"

gh variable set STAGING_FEATURE_ADVANCED_ANALYTICS --body "true"
echo "✅ STAGING_FEATURE_ADVANCED_ANALYTICS set"

gh variable set STAGING_FEATURE_BETA_FEATURES --body "true"
echo "✅ STAGING_FEATURE_BETA_FEATURES set"

# Sentry configuration variables
gh variable set STAGING_SENTRY_ENVIRONMENT --body "staging"
echo "✅ STAGING_SENTRY_ENVIRONMENT set"

gh variable set STAGING_SENTRY_TRACES_SAMPLE_RATE --body "0.2"
echo "✅ STAGING_SENTRY_TRACES_SAMPLE_RATE set"

gh variable set STAGING_SENTRY_PROFILES_SAMPLE_RATE --body "0.2"
echo "✅ STAGING_SENTRY_PROFILES_SAMPLE_RATE set"

echo ""
echo -e "${GREEN}🎉 GitHub Configuration Complete!${NC}"
echo ""
echo -e "${BLUE}📋 Summary of Configured URLs:${NC}"
echo -e "  🌐 Web Interface: ${STAGING_WEB_URL}"
echo -e "  🔌 API Endpoint:  ${STAGING_API_URL}"
echo -e "  🏥 Clinical:      ${STAGING_CLINICAL_URL}"
echo -e "  ⚙️  Admin:        ${STAGING_ADMIN_URL}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Configure Cloudflare DNS records for the above domains"
echo "2. Update your docker-compose.staging.yml with these URLs"
echo "3. Deploy your staging environment"
echo "4. Test all endpoints to ensure proper functionality"
echo ""
echo -e "${BLUE}🔍 To verify your configuration:${NC}"
echo "  gh secret list"
echo "  gh variable list"
echo ""
echo -e "${GREEN}✅ Staging configuration setup completed successfully!${NC}"
