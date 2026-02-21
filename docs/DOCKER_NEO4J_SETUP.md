# 🐳 Docker + Neo4j Setup Guide for TTA

## 🎯 Overview

This guide covers proper Neo4j setup with Docker for TTA development in WSL/Windows environments.

## 🔧 The Problem

**Issue**: Neo4j authentication fails with `NEO4J_AUTH=none` even though it's configured in docker-compose.

**Root Cause**: When Neo4j starts with existing data volumes that have authentication already configured, the `NEO4J_AUTH=none` environment variable is **ignored**. This is by design for security - Neo4j won't disable auth on an existing database.

**Error Message**:
```
neo4j.exceptions.AuthError: {code: Neo.ClientError.Security.Unauthorized}
{message: Unsupported authentication token, missing key `scheme`}
```

## ✅ Solutions

### Option 1: Use Password Authentication (Recommended for Development)

This is the **safest and most reliable** approach:

#### 1. Update docker-compose.dev.yml

```yaml
services:
  neo4j:
    image: neo4j:5.26.1-community
    container_name: ${CONTAINER_PREFIX:-tta-dev}-neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      # Set explicit password instead of NEO4J_AUTH=none
      - NEO4J_AUTH=neo4j/dev_password_2024
      - NEO4J_PLUGINS=["apoc", "graph-data-science"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.*
      - NEO4J_dbms_security_procedures_allowlist=apoc.*,gds.*
      - NEO4J_dbms_connector_bolt_listen__address=0.0.0.0:7687
      - NEO4J_dbms_connector_http_listen__address=0.0.0.0:7474
      - NEO4J_dbms_memory_heap_initial__size=1G
      - NEO4J_dbms_memory_heap_max__size=2G
      - NEO4J_dbms_memory_pagecache_size=512m
```

#### 2. Update .env.example (and your .env file)

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=dev_password_2024
NEO4J_DATABASE=neo4j
```

#### 3. Recreate the container

```bash
# Stop and remove the container and volume
docker-compose -f docker-compose.dev.yml down neo4j
docker volume rm recovered-tta-storytelling_neo4j_dev_data

# Start with new configuration
docker-compose -f docker-compose.dev.yml up -d neo4j
```

#### 4. Test connection

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "dev_password_2024")
)
driver.verify_connectivity()
print("✅ Connected!")
driver.close()
```

### Option 2: Truly Disable Auth (Fresh Start Required)

If you really want `NEO4J_AUTH=none` to work:

```bash
# 1. Stop Neo4j
docker-compose -f docker-compose.dev.yml down neo4j

# 2. DELETE the data volume (⚠️ THIS REMOVES ALL DATA!)
docker volume rm recovered-tta-storytelling_neo4j_dev_data
docker volume rm recovered-tta-storytelling_neo4j_dev_logs
docker volume rm recovered-tta-storytelling_neo4j_dev_plugins

# 3. Start fresh with NEO4J_AUTH=none
docker-compose -f docker-compose.dev.yml up -d neo4j

# 4. Connect without auth
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("", ""))
# Note: Use empty strings, not None or ()
```

## 🌐 WSL-Specific Considerations

### Docker Desktop Integration

1. **Enable WSL Integration**:
   - Open Docker Desktop
   - Settings → Resources → WSL Integration
   - Enable integration for your WSL distro

2. **Network Access**:
   - Use `localhost` for accessing containers from WSL
   - Windows can also access via `localhost` (Docker Desktop handles port forwarding)
   - Container-to-container: use service names (e.g., `neo4j:7687`)

### Port Bindings

Current TTA setup:

| Service | Container Port | Host Port | Access URL |
|---------|---------------|-----------|------------|
| **Neo4j Dev** | 7687 (Bolt) | 7687 | `bolt://localhost:7687` |
| Neo4j Dev | 7474 (HTTP) | 7474 | `http://localhost:7474` |
| **Neo4j Staging** | 7687 (Bolt) | 7688 | `bolt://localhost:7688` |
| Neo4j Staging | 7474 (HTTP) | 7475 | `http://localhost:7475` |
| **Neo4j Test** | 7687 (Bolt) | 8687 | `bolt://localhost:8687` |
| Neo4j Test | 7474 (HTTP) | 8474 | `http://localhost:8474` |
| **Redis Dev** | 6379 | 6379 | `redis://localhost:6379` |
| **Redis Staging** | 6379 | 6380 | `redis://localhost:6380` |
| **Redis Test** | 6379 | 7379 | `redis://localhost:7379` |

## 📝 Environment Configuration

### Development (.env)

```bash
# Development environment - default ports
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=dev_password_2024
REDIS_URL=redis://localhost:6379
```

### Staging (.env.staging)

```bash
# Staging environment - offset ports to avoid conflicts
NEO4J_URI=bolt://localhost:7688
NEO4J_PASSWORD=staging_neo4j_secure_pass_2024
REDIS_URL=redis://localhost:6380
```

### Testing (.env.test)

```bash
# Test environment - completely isolated
NEO4J_URI=bolt://localhost:8687
NEO4J_PASSWORD=test_password_2024
REDIS_URL=redis://localhost:7379
```

## 🧪 Testing Connections

### Quick Test Script

Run the comprehensive test:

```bash
uv run python scripts/test_database_connections.py
```

### Manual Python Test

```python
import os
from neo4j import GraphDatabase
import redis

# Neo4j
neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
neo4j_password = os.getenv("NEO4J_PASSWORD", "dev_password_2024")

driver = GraphDatabase.driver(neo4j_uri, auth=("neo4j", neo4j_password))
driver.verify_connectivity()
print("✅ Neo4j connected")
driver.close()

# Redis
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.Redis.from_url(redis_url)
r.ping()
print("✅ Redis connected")
```

### Using VS Code Tasks

```bash
# Test connections
Ctrl+Shift+P → "Tasks: Run Task" → "🗄️ Database: Test Connections"

# View database quick reference
Ctrl+Shift+P → "Tasks: Run Task" → "🗄️ Database: Show Quick Reference"
```

## 🔍 Troubleshooting

### Neo4j Auth Errors

**Error**: `Unsupported authentication token, missing key 'scheme'`

**Cause**: Auth mismatch between container config and Python driver

**Solutions**:
1. Check what's actually configured:
   ```bash
   docker exec tta-dev-neo4j env | grep NEO4J_AUTH
   ```

2. If `NEO4J_AUTH=none`, recreate volume (see Option 2 above)

3. If `NEO4J_AUTH=neo4j/password`, use matching auth in code:
   ```python
   driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))
   ```

### Connection Refused

**Error**: `Connection refused` or `Port not accessible`

**Solutions**:
1. Check if container is running:
   ```bash
   docker ps | grep neo4j
   ```

2. Check container health:
   ```bash
   docker inspect tta-dev-neo4j | grep -A 10 Health
   ```

3. View logs:
   ```bash
   docker logs tta-dev-neo4j
   ```

4. Restart container:
   ```bash
   docker-compose -f docker-compose.dev.yml restart neo4j
   ```

### WSL Networking Issues

**Problem**: Can't connect from Windows or WSL

**Solutions**:
1. Restart Docker Desktop
2. Check WSL integration is enabled
3. Try `host.docker.internal` instead of `localhost`
4. Verify Windows firewall isn't blocking ports

### Container Unhealthy

**Symptom**: `docker ps` shows `(unhealthy)` status

**Diagnosis**:
```bash
# Check health check logs
docker inspect tta-dev-neo4j --format='{{json .State.Health}}' | jq

# View recent logs
docker logs --tail 50 tta-dev-neo4j
```

**Common Causes**:
- Insufficient memory (increase heap size)
- Plugins not loaded properly
- Volume permissions issues

## 🎯 Best Practices

### 1. Use Password Auth for Development

Don't use `NEO4J_AUTH=none` - it causes more problems than it solves:
- ✅ Use explicit passwords in development
- ✅ Store passwords in `.env` (gitignored)
- ✅ Use different passwords per environment
- ❌ Don't commit passwords to git
- ❌ Don't use `NEO4J_AUTH=none` with persistent volumes

### 2. Environment Separation

Keep environments isolated:
```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Staging
docker-compose -f docker-compose.staging.yml up -d

# Testing
docker-compose -f docker-compose.test.yml up -d
```

### 3. Health Checks

Always configure health checks:
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:7474 || exit 1"]
  interval: 10s
  timeout: 10s
  retries: 5
  start_period: 40s
```

### 4. Volume Management

Be explicit about volumes:
```yaml
volumes:
  - neo4j_dev_data:/data          # Database files
  - neo4j_dev_logs:/logs          # Log files
  - neo4j_dev_import:/var/lib/neo4j/import  # Import directory
  - neo4j_dev_plugins:/plugins    # Plugins (APOC, GDS)
```

## 📚 Additional Resources

- [Neo4j Docker Hub](https://hub.docker.com/_/neo4j)
- [Neo4j Docker Operations Manual](https://neo4j.com/docs/operations-manual/current/docker/)
- [Neo4j Python Driver Docs](https://neo4j.com/docs/python-manual/current/)
- [Docker Desktop WSL Integration](https://docs.docker.com/desktop/wsl/)

## 🚀 Quick Start (TL;DR)

```bash
# 1. Update docker-compose.dev.yml with password auth
#    NEO4J_AUTH=neo4j/dev_password_2024

# 2. Clean start
docker-compose -f docker-compose.dev.yml down neo4j
docker volume rm recovered-tta-storytelling_neo4j_dev_data
docker-compose -f docker-compose.dev.yml up -d neo4j

# 3. Update .env
echo "NEO4J_PASSWORD=dev_password_2024" >> .env

# 4. Test
uv run python scripts/test_database_connections.py
```

✅ **Done!** Neo4j should now work properly from both Windows and WSL.


---
**Logseq:** [[TTA.dev/Docs/Docker_neo4j_setup]]
