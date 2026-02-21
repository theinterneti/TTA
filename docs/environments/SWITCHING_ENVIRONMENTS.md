# Switching Between TTA Environments

## Overview

This guide covers advanced techniques for switching between development and staging environments, managing multiple environments simultaneously, and optimizing your workflow.

## Quick Switching Methods

### Method 1: Using the Environment Switcher Script

The fastest way to switch environments:

```bash
# Switch to development
./scripts/switch-environment.sh dev

# Switch to staging
./scripts/switch-environment.sh staging

# Check status of both
./scripts/switch-environment.sh --both
```

### Method 2: Using VS Code Workspaces

Open the appropriate workspace file:

```bash
# Development workspace
code TTA-Development.code-workspace

# Staging workspace
code TTA-Staging.code-workspace
```

Each workspace has pre-configured tasks and settings for its environment.

### Method 3: Using Docker Compose Directly

Manual control over services:

```bash
# Development
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d

# Staging
docker-compose -f docker-compose.staging-homelab.yml --env-file .env.staging up -d
```

## Running Multiple Environments

### Simultaneous Operation

Both environments can run at the same time thanks to different port allocations:

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d

# Start staging environment (no conflicts!)
docker-compose -f docker-compose.staging-homelab.yml --env-file .env.staging up -d

# Verify both are running
docker ps | grep tta
```

### Resource Considerations

Running both environments requires:
- **CPU:** ~4-8 cores recommended
- **RAM:** ~8-16 GB recommended
- **Disk:** Separate Docker volumes for each environment

Monitor resource usage:
```bash
# Check Docker resource usage
docker stats

# Check system resources
htop
```

## Environment-Specific Workflows

### Development Workflow

1. **Start development environment:**
   ```bash
   docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d
   ```

2. **Open development workspace:**
   ```bash
   code TTA-Development.code-workspace
   ```

3. **Run development tasks:**
   - Use VS Code tasks: `Ctrl+Shift+P` → "Tasks: Run Task"
   - Or use command line:
     ```bash
     uv run pytest tests/ -v
     uv run ruff check .
     ```

4. **Access development services:**
   - Neo4j: http://localhost:7474
   - API: http://localhost:8080
   - Frontend: http://localhost:3000

5. **Stop when done:**
   ```bash
   docker-compose -f docker-compose.dev.yml down
   ```

### Staging Workflow

1. **Start staging environment:**
   ```bash
   docker-compose -f docker-compose.staging-homelab.yml --env-file .env.staging up -d
   ```

2. **Open staging workspace:**
   ```bash
   code TTA-Staging.code-workspace
   ```

3. **Run staging tests:**
   ```bash
   ENVIRONMENT=staging uv run pytest tests/integration/ -v
   ENVIRONMENT=staging uv run pytest tests/e2e/ -v
   ```

4. **Access staging services:**
   - Neo4j: http://localhost:7475
   - API: http://localhost:8081
   - Frontend: http://localhost:3001
   - Health Check: http://localhost:8090

5. **Stop when done:**
   ```bash
   docker-compose -f docker-compose.staging-homelab.yml down
   ```

## Advanced Switching Techniques

### Selective Service Management

Start only specific services:

```bash
# Development: Start only databases
docker-compose -f docker-compose.dev.yml up -d neo4j redis postgres

# Staging: Start only API and frontend
docker-compose -f docker-compose.staging-homelab.yml up -d player-api-staging player-frontend-staging
```

### Environment Variables Override

Override specific variables without editing files:

```bash
# Development with custom log level
LOG_LEVEL=DEBUG docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d

# Staging with custom API port
API_PORT=8082 docker-compose -f docker-compose.staging-homelab.yml --env-file .env.staging up -d
```

### Hot Switching

Switch between environments without stopping services:

```bash
# Check what's running
./scripts/switch-environment.sh --both

# Stop development, start staging
docker-compose -f docker-compose.dev.yml down && \
docker-compose -f docker-compose.staging-homelab.yml --env-file .env.staging up -d
```

## VS Code Workspace Features

### Development Workspace Tasks

Available tasks in `TTA-Development.code-workspace`:

- **Dev: Start All Services** - Start development environment
- **Dev: Stop All Services** - Stop development environment
- **Dev: View Logs** - Follow service logs
- **Dev: Restart Services** - Restart all services
- **Dev: Check Service Status** - Show running services
- **Dev: Run Tests** - Execute test suite
- **Dev: Format Code** - Format Python code
- **Dev: Lint Code** - Run linting checks
- **Dev: Open Neo4j Browser** - Open Neo4j in browser
- **Dev: Open Grafana** - Open Grafana dashboard

### Staging Workspace Tasks

Available tasks in `TTA-Staging.code-workspace`:

- **Staging: Start All Services** - Start staging environment
- **Staging: Stop All Services** - Stop staging environment
- **Staging: View Logs** - Follow service logs
- **Staging: Run Integration Tests** - Execute integration tests
- **Staging: Run E2E Tests** - Execute end-to-end tests
- **Staging: Health Check** - Check service health
- **Staging: Open Neo4j Browser** - Open Neo4j (port 7475)
- **Staging: Open API** - Open API (port 8081)
- **Staging: Backup Databases** - Run backup script

### Using Tasks

1. Open Command Palette: `Ctrl+Shift+P` (Linux/Windows) or `Cmd+Shift+P` (Mac)
2. Type "Tasks: Run Task"
3. Select the desired task from the list

Or use keyboard shortcut: `Ctrl+Shift+B` for default build task

## Environment Isolation

### Data Isolation

Each environment has separate Docker volumes:

```bash
# Development volumes
tta_neo4j_dev_data
tta_redis_dev_data
tta_postgres_dev_data

# Staging volumes
neo4j-staging-data
redis-staging-data
postgres-staging-data
```

### Network Isolation

Each environment has its own Docker network:

```bash
# Development network
tta-dev-network

# Staging network
tta-staging
```

### Configuration Isolation

Each environment has separate configuration files:

```
.env.dev              # Development environment variables
.env.staging          # Staging environment variables
docker-compose.dev.yml                # Development services
docker-compose.staging-homelab.yml    # Staging services
```

## Troubleshooting Switching Issues

### Issue: Port Already in Use

```bash
# Find what's using the port
sudo lsof -i :7474

# Stop the conflicting service
docker-compose -f docker-compose.dev.yml down
```

### Issue: Environment Variables Not Loading

```bash
# Verify environment file exists
ls -la .env.dev .env.staging

# Check file permissions
chmod 600 .env.dev .env.staging

# Verify syntax
cat .env.dev | grep -v '^#' | grep -v '^$'
```

### Issue: Services Not Starting

```bash
# Check Docker daemon
sudo systemctl status docker

# Check logs
docker-compose -f docker-compose.dev.yml logs

# Restart Docker
sudo systemctl restart docker
```

### Issue: Database Connection Failures

```bash
# Check database containers
docker ps | grep neo4j
docker ps | grep redis

# Check database logs
docker logs tta-dev-neo4j
docker logs tta-staging-neo4j

# Restart databases
docker-compose -f docker-compose.dev.yml restart neo4j redis
```

## Best Practices

### 1. Clean Switching

Always stop services before switching:

```bash
# Stop current environment
docker-compose -f docker-compose.dev.yml down

# Start new environment
docker-compose -f docker-compose.staging-homelab.yml --env-file .env.staging up -d
```

### 2. Resource Management

Monitor and manage resources:

```bash
# Check resource usage
docker stats

# Clean up unused resources
docker system prune -a --volumes

# Remove specific environment volumes
docker volume rm tta_neo4j_dev_data
```

### 3. Configuration Management

Keep environment files updated:

```bash
# Backup current configuration
cp .env.dev .env.dev.backup
cp .env.staging .env.staging.backup

# Update from templates when needed
diff .env.dev.example .env.dev
```

### 4. Testing Before Switching

Verify environment health before switching:

```bash
# Check development health
curl http://localhost:8080/health

# Check staging health
curl http://localhost:8081/health
```

## Automation Scripts

### Create Custom Switching Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# TTA environment aliases
alias tta-dev='docker-compose -f docker-compose.dev.yml --env-file .env.dev'
alias tta-staging='docker-compose -f docker-compose.staging-homelab.yml --env-file .env.staging'
alias tta-dev-up='tta-dev up -d'
alias tta-dev-down='tta-dev down'
alias tta-staging-up='tta-staging up -d'
alias tta-staging-down='tta-staging down'
alias tta-status='./scripts/switch-environment.sh --both'
```

Reload shell:
```bash
source ~/.bashrc
```

Usage:
```bash
tta-dev-up      # Start development
tta-staging-up  # Start staging
tta-status      # Check both environments
```

### Create Switching Functions

Add to your shell configuration:

```bash
# Switch to development environment
tta-switch-dev() {
    echo "Switching to development environment..."
    docker-compose -f docker-compose.staging-homelab.yml down 2>/dev/null
    docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d
    code TTA-Development.code-workspace
}

# Switch to staging environment
tta-switch-staging() {
    echo "Switching to staging environment..."
    docker-compose -f docker-compose.dev.yml down 2>/dev/null
    docker-compose -f docker-compose.staging-homelab.yml --env-file .env.staging up -d
    code TTA-Staging.code-workspace
}
```

## Related Documentation

- [Environment Setup Guide](ENVIRONMENT_SETUP_GUIDE.md) - Initial setup instructions
- [Port Reference](PORT_REFERENCE.md) - Complete port allocation reference
- [Docker Compose Guide](../docker/DOCKER_COMPOSE_REFERENCE.md) - Docker configuration details
- [Testing Guide](../testing/TESTING_GUIDE.md) - Running tests in each environment


---
**Logseq:** [[TTA.dev/Docs/Environments/Switching_environments]]
