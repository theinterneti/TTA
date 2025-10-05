#!/bin/bash
# GitHub Environments Setup Script for TTA Project
# This script documents the manual steps needed to complete environment configuration
# Environments have been created via API, but variables and secrets must be set manually

set -e

REPO_OWNER="theinterneti"
REPO_NAME="TTA"
REPO_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}"

echo "=========================================="
echo "GitHub Environments Setup for TTA"
echo "=========================================="
echo ""
echo "✅ Environments Created:"
echo "  - development"
echo "  - staging"
echo "  - production"
echo "  - test"
echo ""
echo "🔧 Manual Configuration Required:"
echo ""
echo "Navigate to: ${REPO_URL}/settings/environments"
echo ""

# Function to display environment variable setup
setup_env_vars() {
    local env_name=$1
    shift
    echo "----------------------------------------"
    echo "Environment: ${env_name}"
    echo "----------------------------------------"
    echo ""
    echo "Environment Variables to Add:"
    while [ $# -gt 0 ]; do
        echo "  • $1"
        shift
    done
    echo ""
}

# Function to display environment secret setup
setup_env_secrets() {
    local env_name=$1
    shift
    echo "Environment Secrets to Add:"
    while [ $# -gt 0 ]; do
        echo "  • $1"
        shift
    done
    echo ""
}

echo "=========================================="
echo "DEVELOPMENT ENVIRONMENT"
echo "=========================================="
setup_env_vars "development" \
    "ENVIRONMENT_NAME = development" \
    "LOG_LEVEL = DEBUG" \
    "ENABLE_DEBUG_FEATURES = true" \
    "RATE_LIMIT_ENABLED = false"

setup_env_secrets "development" \
    "API_BASE_URL = https://dev-api.tta.example.com (or your dev URL)" \
    "DATABASE_URL = bolt://dev-neo4j.tta.example.com:7687 (or your dev Neo4j)" \
    "REDIS_URL = redis://dev-redis.tta.example.com:6379 (or your dev Redis)" \
    "WS_URL = wss://dev-ws.tta.example.com (or your dev WebSocket URL)"

echo "=========================================="
echo "STAGING ENVIRONMENT"
echo "=========================================="
echo "Protection Rules:"
echo "  ✅ Required reviewers: 1"
echo "  ✅ Wait timer: 5 minutes"
echo "  ✅ Deployment branch policy: Protected branches only"
echo ""
setup_env_vars "staging" \
    "ENVIRONMENT_NAME = staging" \
    "LOG_LEVEL = INFO" \
    "ENABLE_DEBUG_FEATURES = false" \
    "RATE_LIMIT_ENABLED = true" \
    "PERFORMANCE_MONITORING = true"

setup_env_secrets "staging" \
    "API_BASE_URL = https://staging-api.tta.example.com (or your staging URL)" \
    "DATABASE_URL = bolt://staging-neo4j.tta.example.com:7687 (or your staging Neo4j)" \
    "REDIS_URL = redis://staging-redis.tta.example.com:6379 (or your staging Redis)" \
    "WS_URL = wss://staging-ws.tta.example.com (or your staging WebSocket URL)" \
    "OPENROUTER_API_KEY = \${{ secrets.OPENROUTER_STAGING_KEY }} (reference repo secret)"

echo "=========================================="
echo "PRODUCTION ENVIRONMENT"
echo "=========================================="
echo "Protection Rules:"
echo "  ✅ Required reviewers: 1"
echo "  ✅ Wait timer: 30 minutes"
echo "  ✅ Deployment branch policy: Protected branches only (main)"
echo ""
setup_env_vars "production" \
    "ENVIRONMENT_NAME = production" \
    "LOG_LEVEL = WARN" \
    "ENABLE_DEBUG_FEATURES = false" \
    "RATE_LIMIT_ENABLED = true" \
    "PERFORMANCE_MONITORING = true" \
    "SECURITY_HEADERS_ENABLED = true" \
    "COMPLIANCE_LOGGING = true"

setup_env_secrets "production" \
    "API_BASE_URL = https://api.tta.example.com (your production URL)" \
    "DATABASE_URL = bolt://prod-neo4j.tta.example.com:7687 (your production Neo4j)" \
    "REDIS_URL = redis://prod-redis.tta.example.com:6379 (your production Redis)" \
    "WS_URL = wss://ws.tta.example.com (your production WebSocket URL)" \
    "OPENROUTER_API_KEY = \${{ secrets.OPENROUTER_PRODUCTION_KEY }} (reference repo secret)" \
    "SENTRY_DSN = \${{ secrets.SENTRY_PRODUCTION_DSN }} (reference repo secret)"

echo "=========================================="
echo "TEST ENVIRONMENT"
echo "=========================================="
setup_env_vars "test" \
    "ENVIRONMENT_NAME = test" \
    "LOG_LEVEL = DEBUG" \
    "ENABLE_MOCK_SERVICES = true" \
    "ENABLE_TEST_DATA_GENERATION = true" \
    "CLEANUP_TEST_DATA = true"

setup_env_secrets "test" \
    "API_BASE_URL = http://localhost:8000" \
    "WS_URL = ws://localhost:8000" \
    "TEST_USER_PASSWORD = \${{ secrets.TEST_USER_PASSWORD }} (reference repo secret)"

echo "=========================================="
echo "REPOSITORY SECRETS TO CREATE"
echo "=========================================="
echo ""
echo "Navigate to: ${REPO_URL}/settings/secrets/actions"
echo ""
echo "Create the following repository secrets:"
echo "  • OPENROUTER_STAGING_KEY - OpenRouter API key for staging"
echo "  • OPENROUTER_PRODUCTION_KEY - OpenRouter API key for production"
echo "  • SENTRY_PRODUCTION_DSN - Sentry DSN for production error tracking"
echo "  • TEST_USER_PASSWORD - Password for test user accounts"
echo ""

echo "=========================================="
echo "VERIFICATION STEPS"
echo "=========================================="
echo ""
echo "1. Navigate to: ${REPO_URL}/settings/environments"
echo "2. Click on each environment (development, staging, production, test)"
echo "3. Add the environment variables listed above"
echo "4. Add the environment secrets listed above"
echo "5. Verify protection rules are correctly configured"
echo "6. Test deployment workflows to ensure environments work correctly"
echo ""

echo "=========================================="
echo "USAGE IN WORKFLOWS"
echo "=========================================="
echo ""
echo "Example workflow usage:"
echo ""
cat << 'EOF'
deploy-staging:
  runs-on: ubuntu-latest
  environment: staging
  steps:
    - name: Deploy to Staging
      run: |
        echo "Environment: ${{ vars.ENVIRONMENT_NAME }}"
        echo "API URL: ${{ secrets.API_BASE_URL }}"
        echo "Log Level: ${{ vars.LOG_LEVEL }}"
EOF
echo ""

echo "=========================================="
echo "SECURITY NOTES"
echo "=========================================="
echo ""
echo "• Use different API keys/credentials for each environment"
echo "• Regularly rotate environment-specific secrets"
echo "• Monitor environment access through GitHub audit logs"
echo "• Production environment has the strictest protection rules"
echo "• Never commit secrets to the repository"
echo ""

echo "✅ Environment setup documentation complete!"
echo ""
echo "For more details, see:"
echo "  .github/repository-config/environments-configuration.yml"
echo ""

