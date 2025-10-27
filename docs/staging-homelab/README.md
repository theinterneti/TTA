# TTA Staging Environment - Homelab Deployment Guide

This guide provides comprehensive instructions for deploying and managing the TTA (Turn-Taking Adventure) staging environment in a homelab infrastructure.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Testing](#testing)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

## 🎯 Overview

The TTA staging environment provides a production-like deployment optimized for testing, validation, and demonstration purposes in a homelab setting. It includes:

- **Complete TTA Stack**: Player API, Frontend, and Testing services
- **Database Layer**: Neo4j (knowledge graphs), Redis (caching), PostgreSQL (structured data)
- **Monitoring Stack**: Prometheus (metrics), Grafana (dashboards)
- **Load Balancing**: Nginx with rate limiting and security headers
- **Testing Framework**: Multi-user session testing, performance validation
- **Automation**: Deployment scripts, backup/restore, health monitoring

## 🔧 Prerequisites

### Hardware Requirements

- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection for image pulls

### Software Requirements

- **Docker**: Version 20.10+ with Docker Compose
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, or similar)
- **Tools**: `curl`, `jq`, `bc` (for health checks)

### Network Requirements

- **Ports**: 3001, 5433, 6380, 7475, 7688, 8081, 9091, 3001 (Grafana)
- **Firewall**: Configure to allow access to required ports
- **DNS**: Optional - configure local DNS for friendly hostnames

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd tta-project

# Copy environment configuration
cp .env.staging-homelab.example .env.staging-homelab

# Edit configuration (see Configuration section)
nano .env.staging-homelab
```

### 2. Configure Environment

Edit `.env.staging-homelab` and update the following critical settings:

```bash
# Database passwords (CHANGE THESE!)
NEO4J_STAGING_PASSWORD=your_secure_neo4j_password
REDIS_STAGING_PASSWORD=your_secure_redis_password
POSTGRES_STAGING_PASSWORD=your_secure_postgres_password

# Security keys (GENERATE NEW ONES!)
JWT_STAGING_SECRET_KEY=your_jwt_secret_key
ENCRYPTION_STAGING_KEY=your_encryption_key

# AI Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_SHOW_FREE_ONLY=true
```

### 3. Deploy

```bash
# Make deployment script executable
chmod +x scripts/deploy-staging-homelab.sh

# Deploy the staging environment
./scripts/deploy-staging-homelab.sh deploy
```

### 4. Verify Deployment

```bash
# Check service status
./scripts/deploy-staging-homelab.sh status

# Run health checks
./scripts/staging-health-check.sh

# Access the application
open http://localhost:3001
```

## ⚙️ Configuration

### Environment Variables

The staging environment uses `.env.staging-homelab` for configuration. Key sections:

#### Database Configuration
```bash
# Neo4j Settings
NEO4J_STAGING_PASSWORD=staging_neo4j_secure_pass
NEO4J_STAGING_HEAP_INITIAL=1G
NEO4J_STAGING_HEAP_MAX=4G
NEO4J_STAGING_PAGECACHE=2G

# Redis Settings
REDIS_STAGING_PASSWORD=staging_redis_secure_pass
REDIS_STAGING_MAXMEMORY=1gb
REDIS_STAGING_MAXMEMORY_POLICY=allkeys-lru

# PostgreSQL Settings
POSTGRES_STAGING_PASSWORD=staging_postgres_secure_pass
POSTGRES_STAGING_DB=tta_staging
POSTGRES_STAGING_USER=tta_staging_user
```

#### Application Configuration
```bash
# API Settings
PLAYER_API_STAGING_PORT=8081
PLAYER_API_STAGING_WORKERS=4
PLAYER_API_STAGING_LOG_LEVEL=INFO

# Frontend Settings
PLAYER_FRONTEND_STAGING_PORT=3001
REACT_APP_STAGING_API_URL=http://localhost:8081

# Security
JWT_STAGING_SECRET_KEY=your_jwt_secret_here
JWT_STAGING_ALGORITHM=HS256
JWT_STAGING_EXPIRE_MINUTES=1440
```

#### AI Model Configuration
```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_SHOW_FREE_ONLY=true
OPENROUTER_STAGING_MODEL=mistralai/mistral-7b-instruct:free

# Model Settings
AI_STAGING_MAX_TOKENS=2048
AI_STAGING_TEMPERATURE=0.7
AI_STAGING_TOP_P=0.9
```

### Service Configuration Files

- **Neo4j**: `config/neo4j-staging.conf`
- **Redis**: `config/redis-staging.conf`
- **PostgreSQL**: `config/postgres-staging-init.sql`
- **Nginx**: `nginx/staging.conf`
- **Prometheus**: `monitoring/prometheus-staging.yml`

## 🚢 Deployment

### Deployment Commands

```bash
# Full deployment
./scripts/deploy-staging-homelab.sh deploy

# Deploy without backup
./scripts/deploy-staging-homelab.sh deploy --no-backup

# Force deployment (skip confirmation)
./scripts/deploy-staging-homelab.sh deploy --force

# Update existing deployment
./scripts/deploy-staging-homelab.sh update

# Stop services
./scripts/deploy-staging-homelab.sh stop

# Restart services
./scripts/deploy-staging-homelab.sh restart
```

### Deployment Process

1. **Prerequisites Check**: Validates Docker, tools, and configuration
2. **Environment Validation**: Checks required environment variables
3. **Backup Creation**: Creates backup of existing data (optional)
4. **Image Management**: Pulls latest images and builds custom ones
5. **Service Deployment**: Starts services in dependency order
6. **Health Verification**: Waits for services to become healthy
7. **Validation**: Tests endpoints and database connections

### Service Startup Order

1. **Infrastructure**: Neo4j, Redis, PostgreSQL
2. **Applications**: Player API, Player Frontend
3. **Monitoring**: Prometheus, Grafana
4. **Load Balancer**: Nginx

## 📊 Monitoring

### Access URLs

- **Grafana**: http://localhost:3001 (admin/staging_grafana_admin_pass)
- **Prometheus**: http://localhost:9091
- **Neo4j Browser**: http://localhost:7475 (neo4j/your_password)

### Key Metrics

#### Application Metrics
- API request rate and response times
- WebSocket connection counts
- Active user sessions
- Error rates and status codes

#### Infrastructure Metrics
- CPU and memory usage per service
- Database connection pools
- Cache hit rates
- Disk usage and I/O

#### Business Metrics
- User engagement levels
- Story generation success rates
- Session duration and activity

### Alerting Rules

Alerts are configured in `monitoring/rules-staging/tta-staging-alerts.yml`:

- **Critical**: Service down, disk space < 10%
- **Warning**: High CPU/memory usage, slow response times
- **Info**: Low user engagement, performance regressions

### Health Monitoring

```bash
# Single health check
./scripts/staging-health-check.sh

# Continuous monitoring (every 60 seconds)
./scripts/staging-health-check.sh --continuous 60

# Custom timeout
./scripts/staging-health-check.sh --timeout 30
```

## 🧪 Testing

### Test Configuration

Test settings are in `testing/configs-staging/test_config.yaml`:

- **Load Testing**: 50 concurrent users, 30-minute duration
- **Multi-user Testing**: 25 concurrent users with different profiles
- **Performance Thresholds**: API p95 < 2s, WebSocket latency < 200ms

### Running Tests

```bash
# Create test users
cd testing
python scripts/create_test_users.py --api-url http://localhost:8081 --count 50

# Run test suite (from testing container)
docker-compose -f docker-compose.staging-homelab.yml exec testing-staging \
  python -m pytest tests/ -v --html=reports/test_report.html

# Load testing
docker-compose -f docker-compose.staging-homelab.yml exec testing-staging \
  locust -f tests/load/locustfile.py --host http://player-api-staging:8080
```

### Test Categories

- **Smoke Tests**: Basic functionality verification
- **Integration Tests**: End-to-end user journeys
- **API Tests**: REST endpoint validation
- **Frontend Tests**: UI functionality with Playwright
- **Database Tests**: Data persistence and integrity
- **Performance Tests**: Load and stress testing
- **Multi-user Tests**: Concurrent session handling

## 🔧 Maintenance

### Backup and Restore

```bash
# Create backup
./scripts/staging-backup.sh

# Restore from backup
./scripts/staging-restore.sh /path/to/backup/directory

# Automated backup (add to crontab)
0 2 * * * /path/to/scripts/staging-backup.sh
```

### Log Management

```bash
# View service logs
./scripts/deploy-staging-homelab.sh logs [service-name]

# Log locations
logs/
├── deployment_YYYYMMDD_HHMMSS.log
├── backup_YYYYMMDD_HHMMSS.log
└── health_check_YYYYMMDD_HHMMSS.log
```

### Updates and Upgrades

```bash
# Update to latest images
./scripts/deploy-staging-homelab.sh update

# Rebuild custom images
docker-compose -f docker-compose.staging-homelab.yml build --no-cache

# Clean up old resources
./scripts/deploy-staging-homelab.sh cleanup
```

## 🔍 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check Docker daemon
sudo systemctl status docker

# Check logs
docker-compose -f docker-compose.staging-homelab.yml logs [service-name]

# Check resource usage
docker stats
```

#### Database Connection Issues
```bash
# Test Neo4j connection
docker exec tta-staging-homelab_neo4j-staging_1 \
  cypher-shell -u neo4j -p your_password "RETURN 1"

# Test Redis connection
docker exec tta-staging-homelab_redis-staging_1 redis-cli ping

# Test PostgreSQL connection
docker exec tta-staging-homelab_postgres-staging_1 \
  pg_isready -U tta_staging_user
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8081

# Stop conflicting services
sudo systemctl stop service-name

# Use different ports in .env.staging-homelab
```

#### Performance Issues
```bash
# Check resource usage
./scripts/staging-health-check.sh

# Monitor in real-time
docker stats

# Check disk space
df -h
```

### Debug Mode

Enable debug logging by setting in `.env.staging-homelab`:
```bash
PLAYER_API_STAGING_LOG_LEVEL=DEBUG
REACT_APP_STAGING_DEBUG=true
```

## 🏗️ Architecture

### Network Architecture

```
Internet
    ↓
Nginx Load Balancer (Port 80/443)
    ↓
┌─────────────────────────────────────┐
│         Docker Network              │
│      (172.26.0.0/16)               │
│                                     │
│  ┌─────────────┐  ┌──────────────┐ │
│  │ Frontend    │  │ Player API   │ │
│  │ (React)     │  │ (FastAPI)    │ │
│  └─────────────┘  └──────────────┘ │
│         │                 │        │
│         └─────────┬───────┘        │
│                   │                │
│  ┌─────────────┐  │  ┌──────────┐  │
│  │ Neo4j       │  │  │ Redis    │  │
│  │ (Graph DB)  │  │  │ (Cache)  │  │
│  └─────────────┘  │  └──────────┘  │
│                   │                │
│  ┌─────────────┐  │  ┌──────────┐  │
│  │ PostgreSQL  │  │  │ Testing  │  │
│  │ (RDBMS)     │  │  │ Suite    │  │
│  └─────────────┘  │  └──────────┘  │
│                   │                │
│  ┌─────────────┐  │  ┌──────────┐  │
│  │ Prometheus  │  │  │ Grafana  │  │
│  │ (Metrics)   │  │  │ (Dashboards)│ │
│  └─────────────┘  │  └──────────┘  │
└─────────────────────────────────────┘
```

### Data Flow

1. **User Request** → Nginx → Frontend/API
2. **API Processing** → Database queries (Neo4j/PostgreSQL/Redis)
3. **AI Integration** → OpenRouter API calls
4. **Real-time Updates** → WebSocket connections
5. **Monitoring** → Prometheus scraping → Grafana visualization

### Storage Layout

```
/var/lib/docker/volumes/
├── tta-staging-homelab_neo4j-data/
├── tta-staging-homelab_redis-data/
├── tta-staging-homelab_postgres-data/
├── tta-staging-homelab_prometheus-data/
└── tta-staging-homelab_grafana-data/
```

---

### Security Considerations

- **Passwords**: Change all default passwords in `.env.staging-homelab`
- **Network**: Use firewall rules to restrict access to staging ports
- **SSL/TLS**: Consider adding SSL certificates for production-like testing
- **Secrets**: Never commit `.env.staging-homelab` to version control
- **Access**: Limit access to staging environment to authorized users only

### Performance Tuning

#### Database Optimization
```bash
# Neo4j memory tuning (in .env.staging-homelab)
NEO4J_STAGING_HEAP_INITIAL=2G
NEO4J_STAGING_HEAP_MAX=8G
NEO4J_STAGING_PAGECACHE=4G

# Redis memory optimization
REDIS_STAGING_MAXMEMORY=2gb
REDIS_STAGING_MAXMEMORY_POLICY=allkeys-lru

# PostgreSQL tuning
POSTGRES_STAGING_SHARED_BUFFERS=256MB
POSTGRES_STAGING_EFFECTIVE_CACHE_SIZE=1GB
```

#### Application Scaling
```bash
# API worker scaling
PLAYER_API_STAGING_WORKERS=8

# Frontend optimization
REACT_APP_STAGING_OPTIMIZE=true
```

## 📞 Support

For issues and questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review service logs: `./scripts/deploy-staging-homelab.sh logs`
3. Run health checks: `./scripts/staging-health-check.sh`
4. Check monitoring dashboards at http://localhost:3001

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
