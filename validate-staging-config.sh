#!/bin/bash

# 🔍 TTA Staging Configuration Validation Script
# This script validates your staging environment configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 TTA Staging Configuration Validation${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# Check if GitHub CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed.${NC}"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub CLI.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI is available and authenticated${NC}"
echo ""

# Function to check if a secret exists
check_secret() {
    local secret_name="$1"
    if gh secret list | grep -q "^$secret_name"; then
        echo -e "${GREEN}✅ Secret: $secret_name${NC}"
        return 0
    else
        echo -e "${RED}❌ Missing Secret: $secret_name${NC}"
        return 1
    fi
}

# Function to check if a variable exists
check_variable() {
    local var_name="$1"
    if gh variable list | grep -q "^$var_name"; then
        echo -e "${GREEN}✅ Variable: $var_name${NC}"
        return 0
    else
        echo -e "${RED}❌ Missing Variable: $var_name${NC}"
        return 1
    fi
}

# Function to test URL accessibility
test_url() {
    local url="$1"
    local name="$2"

    echo -n "Testing $name ($url)... "

    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$url" | grep -q "^[23]"; then
        echo -e "${GREEN}✅ Accessible${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Not accessible (may not be deployed yet)${NC}"
        return 1
    fi
}

# Check GitHub Secrets
echo -e "${BLUE}🔐 Checking GitHub Secrets...${NC}"
secrets_missing=0

check_secret "STAGING_API_URL" || ((secrets_missing++))
check_secret "STAGING_WEB_URL" || ((secrets_missing++))
check_secret "STAGING_CLINICAL_URL" || ((secrets_missing++))
check_secret "STAGING_ADMIN_URL" || ((secrets_missing++))
check_secret "STAGING_DATABASE_URL" || ((secrets_missing++))
check_secret "STAGING_REDIS_URL" || ((secrets_missing++))
check_secret "STAGING_NEO4J_URL" || ((secrets_missing++))
check_secret "STAGING_NEO4J_PASSWORD" || ((secrets_missing++))
check_secret "STAGING_SENTRY_DSN" || ((secrets_missing++))
check_secret "STAGING_JWT_SECRET" || ((secrets_missing++))

echo ""

# Check GitHub Variables
echo -e "${BLUE}⚙️ Checking GitHub Variables...${NC}"
variables_missing=0

check_variable "STAGING_ENVIRONMENT" || ((variables_missing++))
check_variable "STAGING_DEBUG" || ((variables_missing++))
check_variable "STAGING_LOG_LEVEL" || ((variables_missing++))
check_variable "STAGING_MAX_CONCURRENT_SESSIONS" || ((variables_missing++))
check_variable "STAGING_RATE_LIMIT_CALLS" || ((variables_missing++))
check_variable "STAGING_RATE_LIMIT_PERIOD" || ((variables_missing++))
check_variable "STAGING_FEATURE_REAL_TIME_MONITORING" || ((variables_missing++))
check_variable "STAGING_FEATURE_ADVANCED_ANALYTICS" || ((variables_missing++))
check_variable "STAGING_FEATURE_BETA_FEATURES" || ((variables_missing++))
check_variable "STAGING_SENTRY_ENVIRONMENT" || ((variables_missing++))
check_variable "STAGING_SENTRY_TRACES_SAMPLE_RATE" || ((variables_missing++))
check_variable "STAGING_SENTRY_PROFILES_SAMPLE_RATE" || ((variables_missing++))

echo ""

# Get URLs from GitHub secrets for testing
echo -e "${BLUE}🌐 Testing Staging URLs...${NC}"

# Note: We can't directly access secret values via CLI, so we'll test common staging URLs
STAGING_URLS=(
    "https://staging-tta.theinterneti.com"
    "https://api-staging.tta.theinterneti.com"
    "https://clinical-staging.tta.theinterneti.com"
    "https://admin-staging.tta.theinterneti.com"
)

url_tests_passed=0
for url in "${STAGING_URLS[@]}"; do
    if test_url "$url" "$(basename "$url")"; then
        ((url_tests_passed++))
    fi
done

echo ""

# DNS Resolution Check
echo -e "${BLUE}🔍 Checking DNS Resolution...${NC}"
dns_issues=0

for url in "${STAGING_URLS[@]}"; do
    domain=$(echo "$url" | sed 's|https\?://||' | cut -d'/' -f1)
    echo -n "DNS for $domain... "

    if dig +short "$domain" | grep -q .; then
        echo -e "${GREEN}✅ Resolved${NC}"
    else
        echo -e "${RED}❌ Not resolved${NC}"
        ((dns_issues++))
    fi
done

echo ""

# SSL Certificate Check
echo -e "${BLUE}🔒 Checking SSL Certificates...${NC}"
ssl_issues=0

for url in "${STAGING_URLS[@]}"; do
    domain=$(echo "$url" | sed 's|https\?://||' | cut -d'/' -f1)
    echo -n "SSL for $domain... "

    if echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep -q "notAfter"; then
        echo -e "${GREEN}✅ Valid${NC}"
    else
        echo -e "${YELLOW}⚠️  Certificate issue or not accessible${NC}"
        ((ssl_issues++))
    fi
done

echo ""

# Summary
echo -e "${BLUE}📊 Validation Summary${NC}"
echo -e "${BLUE}===================${NC}"

if [ $secrets_missing -eq 0 ]; then
    echo -e "${GREEN}✅ All required secrets are configured${NC}"
else
    echo -e "${RED}❌ $secrets_missing secrets are missing${NC}"
fi

if [ $variables_missing -eq 0 ]; then
    echo -e "${GREEN}✅ All required variables are configured${NC}"
else
    echo -e "${RED}❌ $variables_missing variables are missing${NC}"
fi

echo -e "${YELLOW}⚠️  $url_tests_passed/${#STAGING_URLS[@]} staging URLs are accessible${NC}"
echo -e "${YELLOW}⚠️  $((${#STAGING_URLS[@]} - dns_issues))/${#STAGING_URLS[@]} domains have DNS resolution${NC}"
echo -e "${YELLOW}⚠️  $((${#STAGING_URLS[@]} - ssl_issues))/${#STAGING_URLS[@]} domains have valid SSL certificates${NC}"

echo ""

# Recommendations
echo -e "${BLUE}💡 Recommendations${NC}"
echo -e "${BLUE}===============${NC}"

if [ $secrets_missing -gt 0 ] || [ $variables_missing -gt 0 ]; then
    echo -e "${YELLOW}1. Run ./setup-staging-github-config.sh to configure missing secrets/variables${NC}"
fi

if [ $dns_issues -gt 0 ]; then
    echo -e "${YELLOW}2. Configure DNS records in Cloudflare for unresolved domains${NC}"
fi

if [ $ssl_issues -gt 0 ]; then
    echo -e "${YELLOW}3. Ensure SSL certificates are properly configured in Cloudflare${NC}"
fi

if [ $url_tests_passed -lt ${#STAGING_URLS[@]} ]; then
    echo -e "${YELLOW}4. Deploy your staging environment to make URLs accessible${NC}"
fi

echo ""

# Overall status
total_issues=$((secrets_missing + variables_missing + dns_issues + ssl_issues))

if [ $total_issues -eq 0 ] && [ $url_tests_passed -eq ${#STAGING_URLS[@]} ]; then
    echo -e "${GREEN}🎉 Staging configuration is complete and functional!${NC}"
    exit 0
elif [ $secrets_missing -eq 0 ] && [ $variables_missing -eq 0 ]; then
    echo -e "${YELLOW}⚠️  GitHub configuration is complete, but staging environment needs deployment${NC}"
    exit 0
else
    echo -e "${RED}❌ Configuration issues found. Please address the missing items above.${NC}"
    exit 1
fi
