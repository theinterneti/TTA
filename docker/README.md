# TTA Docker Infrastructure

This directory contains the consolidated Docker infrastructure for the TTA platform, replacing the previous fragmented approach of 42 docker-compose files.

## 📁 Directory Structure

```
docker/
├── compose/                      # Docker Compose configurations
│   ├── docker-compose.base.yml   # Base services (shared across all envs)
│   ├── docker-compose.dev.yml    # Development overrides
│   ├── docker-compose.test.yml   # Test/CI overrides
│   ├── docker-compose.staging.yml # Staging overrides (TODO)
│   └── docker-compose.prod.yml   # Production configuration
├── dockerfiles/                  # Centralized Dockerfiles
│   ├── api/                      # API service Dockerfiles
│   ├── frontend/                 # Frontend Dockerfiles
│   └── services/                 # Supporting service Dockerfiles
├── configs/                      # Service configurations
│   ├── neo4j/                    # Neo4j configuration files
│   ├── redis/                    # Redis configuration files
│   ├── prometheus/               # Prometheus configs
│   ├── resource-limits-template.yml
│   └── health-check-guide.md
├── scripts/                      # Helper scripts
│   └── tta-docker.sh            # Unified management script
└── README.md                     # This file
```

## 🚀 Quick Start

### Development Environment

```bash
# Start all services
bash docker/scripts/tta-docker.sh dev up -d

# View logs
bash docker/scripts/tta-docker.sh dev logs

# Stop services
bash docker/scripts/tta-docker.sh dev down
```

### Test Environment (CI/CD)

```bash
# Start test services (constrained resources)
bash docker/scripts/tta-docker.sh test up -d

# Run tests
uv run pytest tests/integration/

# Cleanup
bash docker/scripts/tta-docker.sh test down
```

### Production Environment

```bash
# Validate configuration
bash docker/scripts/tta-docker.sh prod config

# Deploy (requires external secrets)
bash docker/scripts/tta-docker.sh prod up -d

# Backup databases
bash docker/scripts/tta-docker.sh prod backup
```

## 🔧 Environment Configuration

### Development (`docker-compose.dev.yml`)

**Purpose**: Local development with hot reload, debug ports, and generous resources

**Features**:
- All ports exposed
- Debug logging enabled
- Hot reload volumes
- Grafana included
- Resource limits: Generous for debugging

**Services**:
- Neo4j: 7474 (HTTP), 7687 (Bolt)
- Redis: 6379
- Prometheus: 9090
- Grafana: 3000

### Test (`docker-compose.test.yml`)

**Purpose**: CI/CD testing with constrained resources

**Features**:
- No exposed ports (internal only)
- Minimal plugins
- 50% resource limits vs dev
- No Grafana (too heavy)

**Use Case**: Automated testing in GitHub Actions

### Staging (`docker-compose.staging.yml`)

**Purpose**: Production-like environment for pre-deployment validation

**Features** (TODO):
- Production-sized resources
- External secrets
- Reverse proxy integration
- Automated backups

### Production (`docker-compose.prod.yml`)

**Purpose**: Production deployment

**Critical Requirements**:
- ✅ External secrets (AWS Secrets Manager / Vault)
- ✅ TLS certificates configured
- ✅ Reverse proxy (Nginx/Traefik)
- ✅ Automated backups
- ✅ Log aggregation
- ✅ Monitoring alerts
- ✅ Read-only filesystems
- ✅ Resource limits tuned

## 🔐 Secrets Management

Secrets are **never** stored in docker-compose files.

### Development & Test

```bash
# Generate secrets
bash scripts/docker/setup-secrets.sh

# Secrets stored in:
secrets/
├── dev/
│   ├── neo4j_auth.txt
│   ├── redis_password.txt
│   └── grafana_admin_password.txt
└── test/
    ├── neo4j_auth.txt
    └── redis_password.txt
```

### Production

Production uses **external secrets managers**:

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
    --name tta-prod-neo4j-auth \
    --secret-string "neo4j/STRONG_PASSWORD"

# Docker references external secret
secrets:
  neo4j_auth:
    external: true
    name: tta-prod-neo4j-auth
```

See `secrets/README.md` for details.

## 📊 Service Architecture

### Base Services (All Environments)

1. **Neo4j** - Graph database for narrative world state
   - Community Edition 5.26.1
   - APOC and GDS plugins
   - Health checks configured

2. **Redis** - Cache and message queue
   - Alpine 7.2.4
   - Persistence enabled
   - Health checks configured

3. **Prometheus** - Metrics collection
   - Version 2.48.1
   - Configured scrape targets
   - 15-day retention (dev/test), 90-day (prod)

4. **Grafana** - Metrics visualization
   - Version 10.2.3
   - Pre-configured dashboards
   - OAuth integration (prod)

### Environment-Specific Overrides

Each environment adds specific configuration:
- Port mappings
- Volume mounts
- Resource limits
- Secret references
- Environment variables

## 🏗️ Image Version Pinning

All images use **specific version tags** (no `:latest`):

```yaml
# ✅ Good (pinned versions)
neo4j:5.26.1-community
redis:7.2.4-alpine3.19
grafana/grafana:10.2.3
prom/prometheus:v2.48.1

# ❌ Bad (unpinned)
neo4j:5-community
redis:7-alpine
grafana/grafana:latest
```

## 💾 Volume Naming Convention

Consistent naming pattern: `tta_{service}_{environment}_data`

```yaml
volumes:
  tta_neo4j_dev_data:      # Development Neo4j data
  tta_redis_test_data:     # Test Redis data
  tta_grafana_prod_data:   # Production Grafana data
```

## 🔄 Resource Limits

All services have configured resource limits:

### Development
- Neo4j: 2 CPU, 4GB RAM
- Redis: 1 CPU, 512MB RAM
- Others: See `docker-compose.dev.yml`

### Test (CI)
- 50% of development limits
- Optimized for parallel test runs

### Production
- Right-sized per load testing
- See `docker-compose.prod.yml`

## 📝 Common Commands

### Using Management Script

```bash
# Start environment
bash docker/scripts/tta-docker.sh <env> up [-d]

# View logs
bash docker/scripts/tta-docker.sh <env> logs [service]

# Check status
bash docker/scripts/tta-docker.sh <env> status

# Restart service
bash docker/scripts/tta-docker.sh <env> restart [service]

# Backup databases
bash docker/scripts/tta-docker.sh <env> backup

# Clean up
bash docker/scripts/tta-docker.sh <env> clean [-f]
```

### Manual Docker Compose

```bash
# Development
docker-compose -f docker/compose/docker-compose.base.yml \
               -f docker/compose/docker-compose.dev.yml up -d

# Test
docker-compose -f docker/compose/docker-compose.base.yml \
               -f docker/compose/docker-compose.test.yml up -d

# Validate config
docker-compose -f docker/compose/docker-compose.base.yml \
               -f docker/compose/docker-compose.dev.yml config
```

## 🧪 Health Checks

All services have health checks configured:

### Neo4j
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:7474 || exit 1"]
  interval: 10s
  timeout: 10s
  retries: 5
  start_period: 40s
```

### Redis
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 5s
  timeout: 3s
  retries: 5
```

Services with `depends_on` wait for health checks:

```yaml
depends_on:
  neo4j:
    condition: service_healthy  # Wait for Neo4j health
  redis:
    condition: service_healthy  # Wait for Redis health
```

## 🔍 Troubleshooting

### Services won't start

```bash
# Check configuration
bash docker/scripts/tta-docker.sh dev config

# View detailed logs
bash docker/scripts/tta-docker.sh dev logs

# Check health status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Secrets not found

```bash
# Generate secrets
bash scripts/docker/setup-secrets.sh

# Verify secrets exist
ls -la secrets/dev/
```

### Volume permission issues

```bash
# Fix permissions
docker-compose -f docker/compose/docker-compose.base.yml \
               -f docker/compose/docker-compose.dev.yml \
               down -v

# Recreate with correct permissions
bash docker/scripts/tta-docker.sh dev up -d
```

## 📚 Migration from Old Setup

### For Developers

1. **Old**: 42 different docker-compose files
2. **New**: 1 base + 4 environment overrides

```bash
# Old way
docker-compose -f docker-compose.dev.yml up

# New way (use management script)
bash docker/scripts/tta-docker.sh dev up -d

# Or manual
docker-compose -f docker/compose/docker-compose.base.yml \
               -f docker/compose/docker-compose.dev.yml up -d
```

### Data Migration

Existing volumes are **not** automatically migrated:

```bash
# Backup old data
docker cp tta-dev-neo4j:/data /tmp/neo4j-backup

# Start new environment
bash docker/scripts/tta-docker.sh dev up -d

# Restore data
docker cp /tmp/neo4j-backup tta-dev-neo4j:/data
```

## 🛡️ Security Best Practices

1. **Never commit secrets** - Use `.gitignore` and secret files
2. **Pin image versions** - Avoid `:latest` tags
3. **Use read-only filesystems** - Production services (where possible)
4. **No new privileges** - `security_opt: no-new-privileges:true`
5. **Resource limits** - Prevent resource exhaustion
6. **External secrets** - Production uses AWS Secrets Manager / Vault

## 📖 Related Documentation

- [Docker Improvements Guide](../../.github/instructions/docker-improvements.md)
- [Secrets Management](../../secrets/README.md)
- [Environment Variables](../../.vscode/ENVIRONMENT_PORTS_REFERENCE.md)
- [Data Separation Strategy](../../.github/instructions/data-separation-strategy.md)

## 🚧 TODO

- [ ] Create `docker-compose.staging.yml`
- [ ] Integrate Traefik reverse proxy for production
- [ ] Set up automated backup scheduling
- [ ] Configure log aggregation (CloudWatch/ELK)
- [ ] Load testing and production sizing
- [ ] CI/CD integration for automated deployments

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review full documentation in `.github/instructions/`
3. Create GitHub issue with `docker` label
