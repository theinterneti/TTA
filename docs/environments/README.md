# TTA Environment Documentation

## Overview

This directory contains comprehensive documentation for managing TTA's development and staging environments. The TTA project supports running multiple isolated environments simultaneously on your homelab infrastructure.

## Quick Links

- **[Environment Setup Guide](ENVIRONMENT_SETUP_GUIDE.md)** - Complete setup instructions for dev and staging
- **[Port Reference](PORT_REFERENCE.md)** - Detailed port allocation and connection strings
- **[Switching Environments](SWITCHING_ENVIRONMENTS.md)** - Advanced switching techniques and workflows

## Environment Architecture

### Development Environment
- **Purpose:** Active development, rapid iteration, experimentation
- **Ports:** Standard ports (7474, 7687, 6379, 8080, 3000, 9090)
- **Security:** Relaxed for ease of development
- **Data:** Ephemeral, can be reset frequently
- **Logging:** DEBUG level, verbose output

### Staging Environment
- **Purpose:** Production-like testing, validation, multi-user testing
- **Ports:** Offset ports (7475, 7688, 6380, 8081, 3001, 9091)
- **Security:** Production-like settings
- **Data:** Persistent, production-like
- **Logging:** INFO level, structured output

## Quick Start

### 1. Initial Setup

```bash
# Create environment files from templates
cp .env.dev.example .env.dev
cp .env.staging.example .env.staging

# Edit and configure
nano .env.dev
nano .env.staging
```

### 2. Start Development

```bash
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d
code TTA-Development.code-workspace
```

### 3. Start Staging

```bash
docker-compose -f docker-compose.staging-homelab.yml --env-file .env.staging up -d
code TTA-Staging.code-workspace
```

### 4. Check Status

```bash
./scripts/switch-environment.sh --both
```

## Port Quick Reference

| Service | Development | Staging | Purpose |
|---------|-------------|---------|---------|
| Neo4j HTTP | 7474 | 7475 | Browser interface |
| Neo4j Bolt | 7687 | 7688 | Database connection |
| Redis | 6379 | 6380 | Cache/session store |
| PostgreSQL | 5432 | 5433 | Relational database |
| API Server | 8080 | 8081 | Backend API |
| Frontend | 3000 | 3001 | Web interface |
| Grafana | 3000 | 3002 | Monitoring |
| Prometheus | 9090 | 9091 | Metrics |
| Redis Commander | 8081 | 8082 | Redis UI |
| Health Check | N/A | 8090 | Health monitoring |

## Key Features

### Simultaneous Operation
- Both environments can run at the same time
- No port conflicts
- Separate Docker networks and volumes
- Independent configuration

### VS Code Integration
- Environment-specific workspaces
- Pre-configured tasks for each environment
- Debug configurations
- Quick access to service URLs

### Environment Isolation
- Separate databases and data volumes
- Independent Docker networks
- Environment-specific configuration files
- Isolated logs and cache directories

### Easy Switching
- Helper script for environment management
- VS Code workspace switching
- Docker Compose profiles
- Shell aliases and functions

## Common Workflows

### Daily Development

```bash
# Morning
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d
code TTA-Development.code-workspace

# Work...

# Evening
docker-compose -f docker-compose.dev.yml down
```

### Testing in Staging

```bash
# Start staging
docker-compose -f docker-compose.staging-homelab.yml --env-file .env.staging up -d

# Run tests
ENVIRONMENT=staging uv run pytest tests/integration/ -v

# Stop when done
docker-compose -f docker-compose.staging-homelab.yml down
```

### Parallel Development and Testing

```bash
# Start both
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d
docker-compose -f docker-compose.staging-homelab.yml --env-file .env.staging up -d

# Develop on port 8080, test on port 8081
```

## Documentation Structure

```
docs/environments/
├── README.md                      # This file
├── ENVIRONMENT_SETUP_GUIDE.md     # Complete setup instructions
├── PORT_REFERENCE.md              # Port allocation reference
└── SWITCHING_ENVIRONMENTS.md      # Advanced switching techniques
```

## Related Documentation

### Setup and Configuration
- [Environment Setup Guide](ENVIRONMENT_SETUP_GUIDE.md) - Initial setup
- [Environment Variables](../../ENVIRONMENT_SETUP.md) - Variable reference
- [Docker Configuration](../docker/) - Docker setup

### Development
- [Development Setup](../../DEVELOPMENT_SETUP.md) - Development guide
- [Testing Guide](../testing/TESTING_GUIDE.md) - Running tests
- [Contributing Guide](../../CONTRIBUTING.md) - Contribution guidelines

### Deployment
- [Production Deployment](../../PRODUCTION_DEPLOYMENT_GUIDE.md) - Production setup
- [Staging Deployment](../../STAGING_DEPLOYMENT_PLAN.md) - Staging setup
- [Homelab Deployment](../deployment/homelab/) - Homelab-specific guides

### Operations
- [Monitoring Guide](../monitoring/) - Monitoring and observability
- [Backup and Recovery](../operations/backup-recovery.md) - Data management
- [Troubleshooting](../operations/troubleshooting.md) - Common issues

## Tools and Scripts

### Environment Switcher Script

```bash
./scripts/switch-environment.sh [dev|staging] [options]
```

Features:
- Switch between environments
- Check environment status
- Validate configuration
- Show service URLs

### VS Code Workspaces

- `TTA-Development.code-workspace` - Development environment
- `TTA-Staging.code-workspace` - Staging environment

Features:
- Pre-configured tasks
- Debug configurations
- Environment-specific settings
- Quick access commands

### Docker Compose Files

- `docker-compose.dev.yml` - Development services
- `docker-compose.staging-homelab.yml` - Staging services
- `docker-compose.test.yml` - Test services

## Environment Files

### Templates (Committed)
- `.env.dev.example` - Development template
- `.env.staging.example` - Staging template
- `.env.example` - General template

### Actual Files (Not Committed)
- `.env.dev` - Development configuration
- `.env.staging` - Staging configuration
- `.env.local` - Personal overrides

## Best Practices

### Security
1. Never commit actual `.env` files
2. Use strong passwords in staging
3. Rotate credentials regularly
4. Keep API keys separate per environment

### Resource Management
1. Stop unused environments
2. Clean up old Docker volumes
3. Monitor resource usage
4. Use appropriate resource limits

### Testing
1. Test in development first
2. Validate in staging before production
3. Run full test suite in staging
4. Use production-like data in staging

### Configuration
1. Keep environment files updated
2. Document configuration changes
3. Use templates for new setups
4. Review and validate regularly

## Troubleshooting

### Common Issues

**Port Conflicts**
```bash
# Check ports
sudo lsof -i :7474

# Stop services
docker-compose -f docker-compose.dev.yml down
```

**Environment Variables Not Loading**
```bash
# Verify files exist
ls -la .env.dev .env.staging

# Check syntax
cat .env.dev | grep -v '^#' | grep -v '^$'
```

**Database Connection Issues**
```bash
# Check containers
docker ps | grep neo4j

# Check logs
docker logs tta-dev-neo4j

# Restart
docker-compose -f docker-compose.dev.yml restart neo4j
```

### Getting Help

1. Check the troubleshooting sections in each guide
2. Review Docker logs: `docker-compose logs`
3. Verify configuration: `./scripts/switch-environment.sh --check`
4. Consult the main [README](../../README.md)

## Contributing

When adding new services or changing configurations:

1. Update both dev and staging configurations
2. Ensure port allocations don't conflict
3. Update documentation
4. Test both environments
5. Update workspace files if needed

## Support

For questions or issues:
- Check the documentation in this directory
- Review the main project [README](../../README.md)
- Check existing issues on GitHub
- Create a new issue if needed

## Version History

- **v1.0** (2025-01-04) - Initial environment separation
  - Created dev and staging environments
  - Implemented port allocation strategy
  - Added VS Code workspace integration
  - Created helper scripts and documentation
