#!/usr/bin/env bash
# TTA Docker Secrets Setup Script
# Creates secure secret files for each environment
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SECRETS_DIR="${REPO_ROOT}/secrets"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $*"; }

# Generate secure password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

log_info "Setting up TTA Docker secrets..."

# Create directory structure
for env in dev test staging production; do
    mkdir -p "${SECRETS_DIR}/${env}"
    log_success "Created ${env} secrets directory"
done

# Development environment
log_info "Setting up development secrets..."
if [ ! -f "${SECRETS_DIR}/dev/neo4j_auth.txt" ]; then
    echo "neo4j/$(generate_password)" > "${SECRETS_DIR}/dev/neo4j_auth.txt"
    chmod 600 "${SECRETS_DIR}/dev/neo4j_auth.txt"
    log_success "Created dev/neo4j_auth.txt"
else
    log_warning "dev/neo4j_auth.txt already exists, skipping"
fi

if [ ! -f "${SECRETS_DIR}/dev/redis_password.txt" ]; then
    generate_password > "${SECRETS_DIR}/dev/redis_password.txt"
    chmod 600 "${SECRETS_DIR}/dev/redis_password.txt"
    log_success "Created dev/redis_password.txt"
else
    log_warning "dev/redis_password.txt already exists, skipping"
fi

if [ ! -f "${SECRETS_DIR}/dev/grafana_admin_password.txt" ]; then
    generate_password > "${SECRETS_DIR}/dev/grafana_admin_password.txt"
    chmod 600 "${SECRETS_DIR}/dev/grafana_admin_password.txt"
    log_success "Created dev/grafana_admin_password.txt"
else
    log_warning "dev/grafana_admin_password.txt already exists, skipping"
fi

# Test environment
log_info "Setting up test secrets..."
if [ ! -f "${SECRETS_DIR}/test/neo4j_auth.txt" ]; then
    echo "neo4j/$(generate_password)" > "${SECRETS_DIR}/test/neo4j_auth.txt"
    chmod 600 "${SECRETS_DIR}/test/neo4j_auth.txt"
    log_success "Created test/neo4j_auth.txt"
else
    log_warning "test/neo4j_auth.txt already exists, skipping"
fi

if [ ! -f "${SECRETS_DIR}/test/redis_password.txt" ]; then
    generate_password > "${SECRETS_DIR}/test/redis_password.txt"
    chmod 600 "${SECRETS_DIR}/test/redis_password.txt"
    log_success "Created test/redis_password.txt"
else
    log_warning "test/redis_password.txt already exists, skipping"
fi

# Staging environment
log_info "Setting up staging secrets..."
log_warning "Staging secrets should be set manually with secure values"
if [ ! -f "${SECRETS_DIR}/staging/neo4j_auth.txt" ]; then
    echo "# Set manually: neo4j/SECURE_PASSWORD" > "${SECRETS_DIR}/staging/neo4j_auth.txt"
    chmod 600 "${SECRETS_DIR}/staging/neo4j_auth.txt"
    log_success "Created staging/neo4j_auth.txt template"
fi

# Production guide
cat > "${SECRETS_DIR}/production/README.md" << 'EOF'
# Production Secrets

**DO NOT store production secrets in files.**

Use a proper secrets management system:

## AWS Secrets Manager

```bash
# Store secrets
aws secretsmanager create-secret \
    --name tta-prod-neo4j-auth \
    --secret-string "neo4j/PRODUCTION_PASSWORD"

# Reference in docker-compose.prod.yml
secrets:
  neo4j_auth:
    external: true
    name: tta-prod-neo4j-auth
```

## HashiCorp Vault

```bash
# Store secrets
vault kv put secret/tta/neo4j \
    username=neo4j \
    password=PRODUCTION_PASSWORD

# Use Vault agent for injection
```

## Docker Swarm Secrets

```bash
# Create secret
echo "neo4j/PRODUCTION_PASSWORD" | docker secret create neo4j_auth -

# Deploy stack
docker stack deploy -c docker-compose.prod.yml tta
```
EOF

log_success "Created production/README.md"

# Summary
log_info "Secrets setup complete!"
echo ""
echo "Generated secrets:"
echo "  • Development: neo4j, redis, grafana"
echo "  • Test: neo4j, redis"
echo "  • Staging: templates created (set manually)"
echo "  • Production: guide created"
echo ""
echo "Next steps:"
echo "  1. Review secrets in secrets/dev/"
echo "  2. Set staging secrets manually"
echo "  3. Update docker-compose files to use secrets"
echo "  4. Test with: docker-compose -f docker-compose.dev.yml up -d"
