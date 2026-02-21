# TTA Port Reference Guide

## Overview

This document provides a comprehensive reference for all ports used across TTA development and staging environments. The port allocation strategy ensures both environments can run simultaneously without conflicts.

## Port Allocation Strategy

### Development Environment
- Uses **standard ports** for ease of access and familiarity
- Ports: 3000, 5432, 6379, 7474, 7687, 8080, 8081, 9090

### Staging Environment
- Uses **offset ports** to avoid conflicts with development
- Database ports: +1 offset (7475, 7688, 6380, 5433)
- Service ports: +1 or +100 offset depending on service type
- Additional services not in dev (e.g., health check on 8090)

## Complete Port Reference

### Database Services

| Service | Development | Staging | Protocol | Purpose |
|---------|-------------|---------|----------|---------|
| **Neo4j HTTP** | 7474 | 7475 | HTTP | Browser interface, REST API |
| **Neo4j Bolt** | 7687 | 7688 | Bolt | Database connection protocol |
| **Redis** | 6379 | 6380 | Redis | Cache and session store |
| **PostgreSQL** | 5432 | 5433 | PostgreSQL | Relational database |

### Application Services

| Service | Development | Staging | Protocol | Purpose |
|---------|-------------|---------|----------|---------|
| **Player API** | 8080 | 8081 | HTTP | Backend REST API |
| **Player Frontend** | 3000 | 3001 | HTTP | React web interface |

### Monitoring Services

| Service | Development | Staging | Protocol | Purpose |
|---------|-------------|---------|----------|---------|
| **Grafana** | 3000 | 3002 | HTTP | Monitoring dashboards |
| **Prometheus** | 9090 | 9091 | HTTP | Metrics collection |
| **Health Check** | N/A | 8090 | HTTP | Service health monitoring |

### Management Tools

| Service | Development | Staging | Protocol | Purpose |
|---------|-------------|---------|----------|---------|
| **Redis Commander** | 8081 | 8082 | HTTP | Redis management UI |
| **Neo4j Browser** | 8080 | N/A | HTTP | Neo4j query interface |

## Port Usage by Environment

### Development Environment Ports

```
3000  - Grafana Dashboard
5432  - PostgreSQL Database
6379  - Redis Cache
7474  - Neo4j HTTP Interface
7687  - Neo4j Bolt Protocol
8080  - Player API Server / Neo4j Browser
8081  - Redis Commander
9090  - Prometheus Metrics
```

### Staging Environment Ports

```
3001  - Player Frontend
3002  - Grafana Dashboard
5433  - PostgreSQL Database
6380  - Redis Cache
7475  - Neo4j HTTP Interface
7688  - Neo4j Bolt Protocol
8081  - Player API Server
8082  - Redis Commander
8090  - Health Check Service
9091  - Prometheus Metrics
```

## Connection Strings

### Development Environment

#### Neo4j
```bash
# Bolt connection
bolt://localhost:7687

# HTTP connection
http://localhost:7474

# Browser URL
http://localhost:7474/browser/

# Connection in code
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=tta_dev_password_2024
```

#### Redis
```bash
# Connection string
redis://localhost:6379

# With password
redis://:password@localhost:6379

# Connection in code
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### PostgreSQL
```bash
# Connection string
postgresql://tta_dev_user:password@localhost:5432/tta_dev

# Connection in code
DATABASE_URL=postgresql://tta_dev_user:password@localhost:5432/tta_dev
```

### Staging Environment

#### Neo4j
```bash
# Bolt connection
bolt://localhost:7688

# HTTP connection
http://localhost:7475

# Browser URL
http://localhost:7475/browser/

# Connection in code
NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_PASSWORD=staging_neo4j_secure_password
```

#### Redis
```bash
# Connection string
redis://:password@localhost:6380

# Connection in code
REDIS_URL=redis://:password@localhost:6380
REDIS_HOST=localhost
REDIS_PORT=6380
```

#### PostgreSQL
```bash
# Connection string
postgresql://tta_staging_user:password@localhost:5433/tta_staging

# Connection in code
DATABASE_URL=postgresql://tta_staging_user:password@localhost:5433/tta_staging
```

## Docker Network Ports

### Internal Container Ports

Containers communicate internally using standard ports within their Docker networks:

#### Development Network (tta-dev-network)
```
neo4j:7474    - Neo4j HTTP (internal)
neo4j:7687    - Neo4j Bolt (internal)
redis:6379    - Redis (internal)
postgres:5432 - PostgreSQL (internal)
```

#### Staging Network (tta-staging)
```
neo4j-staging:7474    - Neo4j HTTP (internal)
neo4j-staging:7687    - Neo4j Bolt (internal)
redis-staging:6379    - Redis (internal)
postgres-staging:5432 - PostgreSQL (internal)
```

**Note:** Internal container ports remain standard (7474, 7687, 6379, 5432) within their respective networks. Only the host-exposed ports differ.

## Port Conflict Resolution

### Checking for Port Conflicts

```bash
# Check if a port is in use
sudo lsof -i :7474
sudo lsof -i :7687
sudo lsof -i :6379

# Check all TTA-related ports
for port in 3000 3001 3002 5432 5433 6379 6380 7474 7475 7687 7688 8080 8081 8082 8090 9090 9091; do
    echo "Port $port:"
    sudo lsof -i :$port || echo "  Not in use"
done
```

### Resolving Conflicts

If you encounter port conflicts:

1. **Stop conflicting services:**
   ```bash
   docker-compose -f docker-compose.dev.yml down
   docker-compose -f docker-compose.staging-homelab.yml down
   ```

2. **Identify the conflicting process:**
   ```bash
   sudo lsof -i :<port_number>
   ```

3. **Stop the conflicting process:**
   ```bash
   sudo kill <PID>
   ```

4. **Restart TTA services:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

## Firewall Configuration

### WSL2 Firewall Rules

If you need to access services from Windows or other machines:

```bash
# Allow specific ports through Windows Firewall
# Run in PowerShell as Administrator

# Development ports
New-NetFirewallRule -DisplayName "TTA Dev Neo4j" -Direction Inbound -LocalPort 7474,7687 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "TTA Dev Redis" -Direction Inbound -LocalPort 6379 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "TTA Dev API" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow

# Staging ports
New-NetFirewallRule -DisplayName "TTA Staging Neo4j" -Direction Inbound -LocalPort 7475,7688 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "TTA Staging Redis" -Direction Inbound -LocalPort 6380 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "TTA Staging API" -Direction Inbound -LocalPort 8081 -Protocol TCP -Action Allow
```

## Testing Port Connectivity

### From Command Line

```bash
# Test Neo4j HTTP
curl http://localhost:7474
curl http://localhost:7475

# Test API endpoints
curl http://localhost:8080/health
curl http://localhost:8081/health

# Test Redis
redis-cli -p 6379 ping
redis-cli -p 6380 ping

# Test PostgreSQL
pg_isready -h localhost -p 5432
pg_isready -h localhost -p 5433
```

### From Python

```python
import redis
import neo4j
import psycopg2

# Test Redis (dev)
r = redis.Redis(host='localhost', port=6379)
print(r.ping())

# Test Redis (staging)
r = redis.Redis(host='localhost', port=6380)
print(r.ping())

# Test Neo4j (dev)
driver = neo4j.GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
driver.verify_connectivity()

# Test Neo4j (staging)
driver = neo4j.GraphDatabase.driver("bolt://localhost:7688", auth=("neo4j", "password"))
driver.verify_connectivity()
```

## Port Security Considerations

### Development Environment
- Ports are exposed on localhost only by default
- Suitable for local development
- No external access required

### Staging Environment
- Ports are exposed on localhost only by default
- Can be configured for homelab network access
- Consider firewall rules for network exposure
- Use strong passwords for all services

### Production Environment
- Use reverse proxy (nginx) for external access
- Expose only necessary ports (80, 443)
- Keep database ports internal to Docker network
- Implement proper authentication and encryption

## Quick Reference Card

```
╔════════════════════════════════════════════════════════════╗
║                  TTA PORT QUICK REFERENCE                  ║
╠════════════════════════════════════════════════════════════╣
║ Service          │ Dev Port │ Staging Port │ Protocol     ║
╠══════════════════╪══════════╪══════════════╪══════════════╣
║ Neo4j HTTP       │   7474   │     7475     │ HTTP         ║
║ Neo4j Bolt       │   7687   │     7688     │ Bolt         ║
║ Redis            │   6379   │     6380     │ Redis        ║
║ PostgreSQL       │   5432   │     5433     │ PostgreSQL   ║
║ API Server       │   8080   │     8081     │ HTTP         ║
║ Frontend         │   3000   │     3001     │ HTTP         ║
║ Grafana          │   3000   │     3002     │ HTTP         ║
║ Prometheus       │   9090   │     9091     │ HTTP         ║
║ Redis Commander  │   8081   │     8082     │ HTTP         ║
║ Health Check     │   N/A    │     8090     │ HTTP         ║
╚════════════════════════════════════════════════════════════╝
```

## Related Documentation

- [Environment Setup Guide](ENVIRONMENT_SETUP_GUIDE.md) - Complete setup instructions
- [Switching Environments](SWITCHING_ENVIRONMENTS.md) - How to switch between environments
- [Docker Compose Reference](../docker/DOCKER_COMPOSE_REFERENCE.md) - Docker configuration details


---
**Logseq:** [[TTA.dev/Docs/Environments/Port_reference]]
