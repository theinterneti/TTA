#!/bin/bash

# TTA Storytelling Project - GitHub Secrets and Variables Configuration
# This script helps you set up all necessary GitHub secrets and variables for your TTA project

set -e

echo "🚀 TTA Storytelling Project - GitHub Configuration Setup"
echo "======================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local result

    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " result
        echo "${result:-$default}"
    else
        read -p "$prompt: " result
        echo "$result"
    fi
}

# Function to prompt for sensitive input (hidden)
prompt_sensitive() {
    local prompt="$1"
    local result

    read -s -p "$prompt: " result
    echo ""
    echo "$result"
}

echo -e "${BLUE}This script will help you configure GitHub secrets and variables for your TTA project.${NC}"
echo -e "${YELLOW}Please have the following information ready:${NC}"
echo "- Sentry account and project DSN"
echo "- Your staging and production domain names"
echo "- OpenRouter API key (if using)"
echo "- Database credentials for staging/production"
echo ""

read -p "Press Enter to continue..."

echo -e "\n${GREEN}=== STEP 1: Error Monitoring (Sentry) ===${NC}"
echo "Sentry helps track errors and performance in your TTA application."
echo "1. Sign up at https://sentry.io (free tier available)"
echo "2. Create a new project for 'TTA Storytelling'"
echo "3. Go to Settings → Projects → [Your Project] → Client Keys (DSN)"
echo ""

SENTRY_DSN=$(prompt_with_default "Enter your Sentry DSN" "")

if [ -n "$SENTRY_DSN" ]; then
    echo "Setting Sentry DSN..."
    gh secret set SENTRY_DSN --body "$SENTRY_DSN"
    echo -e "${GREEN}✅ Sentry DSN configured${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping Sentry configuration${NC}"
fi

echo -e "\n${GREEN}=== STEP 2: API URLs ===${NC}"
echo "Configure your staging and production API endpoints."
echo ""

STAGING_DOMAIN=$(prompt_with_default "Enter your staging domain (e.g., staging.tta-storytelling.com)" "staging.tta-storytelling.com")
PRODUCTION_DOMAIN=$(prompt_with_default "Enter your production domain (e.g., tta-storytelling.com)" "tta-storytelling.com")

STAGING_API_URL="https://${STAGING_DOMAIN}"
PRODUCTION_API_URL="https://${PRODUCTION_DOMAIN}"

echo "Setting API URLs..."
gh variable set STAGING_API_URL --body "$STAGING_API_URL"
gh variable set PRODUCTION_API_URL --body "$PRODUCTION_API_URL"

# Also set WebSocket URLs for real-time features
gh variable set STAGING_WS_URL --body "wss://${STAGING_DOMAIN}"
gh variable set PRODUCTION_WS_URL --body "wss://${PRODUCTION_DOMAIN}"

echo -e "${GREEN}✅ API URLs configured${NC}"
echo "  Staging API: $STAGING_API_URL"
echo "  Production API: $PRODUCTION_API_URL"

echo -e "\n${GREEN}=== STEP 3: AI Model Configuration ===${NC}"
echo "Configure AI model service credentials."
echo ""

OPENROUTER_KEY=$(prompt_sensitive "Enter your OpenRouter API key (or press Enter to skip)")

if [ -n "$OPENROUTER_KEY" ]; then
    gh secret set OPENROUTER_API_KEY --body "$OPENROUTER_KEY"
    echo -e "${GREEN}✅ OpenRouter API key configured${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping OpenRouter configuration${NC}"
fi

echo -e "\n${GREEN}=== STEP 4: Database Configuration ===${NC}"
echo "Configure database credentials for staging and production."
echo ""

# Neo4j Configuration
NEO4J_STAGING_PASSWORD=$(prompt_sensitive "Enter Neo4j staging password (or press Enter to skip)")
if [ -n "$NEO4J_STAGING_PASSWORD" ]; then
    gh secret set NEO4J_STAGING_PASSWORD --body "$NEO4J_STAGING_PASSWORD"
    echo -e "${GREEN}✅ Neo4j staging password configured${NC}"
fi

NEO4J_PRODUCTION_PASSWORD=$(prompt_sensitive "Enter Neo4j production password (or press Enter to skip)")
if [ -n "$NEO4J_PRODUCTION_PASSWORD" ]; then
    gh secret set NEO4J_PRODUCTION_PASSWORD --body "$NEO4J_PRODUCTION_PASSWORD"
    echo -e "${GREEN}✅ Neo4j production password configured${NC}"
fi

# Redis Configuration
REDIS_STAGING_PASSWORD=$(prompt_sensitive "Enter Redis staging password (or press Enter to skip)")
if [ -n "$REDIS_STAGING_PASSWORD" ]; then
    gh secret set REDIS_STAGING_PASSWORD --body "$REDIS_STAGING_PASSWORD"
    echo -e "${GREEN}✅ Redis staging password configured${NC}"
fi

REDIS_PRODUCTION_PASSWORD=$(prompt_sensitive "Enter Redis production password (or press Enter to skip)")
if [ -n "$REDIS_PRODUCTION_PASSWORD" ]; then
    gh secret set REDIS_PRODUCTION_PASSWORD --body "$REDIS_PRODUCTION_PASSWORD"
    echo -e "${GREEN}✅ Redis production password configured${NC}"
fi

echo -e "\n${GREEN}=== STEP 5: Security Configuration ===${NC}"
echo "Configure JWT secrets for different environments."
echo ""

JWT_STAGING_SECRET=$(prompt_sensitive "Enter JWT secret for staging (or press Enter for auto-generated)")
if [ -z "$JWT_STAGING_SECRET" ]; then
    JWT_STAGING_SECRET=$(openssl rand -base64 32)
    echo "Generated JWT staging secret"
fi
gh secret set JWT_STAGING_SECRET --body "$JWT_STAGING_SECRET"

JWT_PRODUCTION_SECRET=$(prompt_sensitive "Enter JWT secret for production (or press Enter for auto-generated)")
if [ -z "$JWT_PRODUCTION_SECRET" ]; then
    JWT_PRODUCTION_SECRET=$(openssl rand -base64 32)
    echo "Generated JWT production secret"
fi
gh secret set JWT_PRODUCTION_SECRET --body "$JWT_PRODUCTION_SECRET"

echo -e "${GREEN}✅ JWT secrets configured${NC}"

echo -e "\n${GREEN}=== STEP 6: Additional Configuration ===${NC}"
echo "Setting up additional variables for your TTA project..."

# Test configuration
gh variable set TEST_USERNAME --body "e2e_test_user"
gh variable set TEST_EMAIL --body "test@tta-storytelling.com"

# Feature flags
gh variable set ENABLE_PERFORMANCE_MONITORING --body "true"
gh variable set ENABLE_SECURITY_SCANNING --body "true"
gh variable set ENABLE_THERAPEUTIC_MONITORING --body "true"

# Performance budgets (based on your therapeutic application needs)
gh variable set PERFORMANCE_BUDGET_AUTH_LOAD_TIME --body "2000"
gh variable set PERFORMANCE_BUDGET_DASHBOARD_LOAD_TIME --body "3000"
gh variable set PERFORMANCE_BUDGET_CHAT_RESPONSE_TIME --body "1500"

echo -e "${GREEN}✅ Additional configuration completed${NC}"

echo -e "\n${BLUE}=== Configuration Summary ===${NC}"
echo "The following secrets and variables have been configured:"
echo ""
echo "🔐 Secrets (encrypted):"
echo "  - SENTRY_DSN"
echo "  - OPENROUTER_API_KEY"
echo "  - NEO4J_STAGING_PASSWORD"
echo "  - NEO4J_PRODUCTION_PASSWORD"
echo "  - REDIS_STAGING_PASSWORD"
echo "  - REDIS_PRODUCTION_PASSWORD"
echo "  - JWT_STAGING_SECRET"
echo "  - JWT_PRODUCTION_SECRET"
echo ""
echo "📝 Variables (plain text):"
echo "  - STAGING_API_URL: $STAGING_API_URL"
echo "  - PRODUCTION_API_URL: $PRODUCTION_API_URL"
echo "  - STAGING_WS_URL: wss://${STAGING_DOMAIN}"
echo "  - PRODUCTION_WS_URL: wss://${PRODUCTION_DOMAIN}"
echo "  - Various test and performance configuration"
echo ""
echo -e "${GREEN}🎉 GitHub configuration completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Verify your configuration in GitHub repository settings"
echo "2. Set up your staging and production servers"
echo "3. Configure your domain DNS to point to your servers"
echo "4. Test your deployment pipeline"
echo ""
echo "For more details, see your PRODUCTION_DEPLOYMENT_GUIDE.md"
