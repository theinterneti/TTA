# Player Experience Interface - Deployment Guide

This guide covers the deployment of the Player Experience Interface for the TTA (Therapeutic Text Adventure) system.

## Overview

The Player Experience Interface consists of:
- **API Service**: FastAPI-based REST and WebSocket API
- **Database Services**: Redis (caching) and Neo4j (graph database)
- **Web Interface**: React-based frontend (future implementation)

## Prerequisites

### System Requirements
- Docker 20.10+ and Docker Compose 2.0+
- Python 3.11+ (for development)
- Node.js 18+ (for frontend development)
- Kubernetes 1.24+ (for production deployment)

### Network Requirements
- Port 8080: API service
- Port 6379: Redis
- Port 7687: Neo4j bolt protocol
- Port 7474: Neo4j web interface

## Quick Start

### Development Environment

1. **Clone and setup the repository:**
   ```bash
   git clone <repository-url>
   cd TTA/src/player_experience
   ```

2. **Deploy using the deployment script:**
   ```bash
   ./deploy.sh development deploy
   ```

3. **Verify deployment:**
   ```bash
   python test_deployment.py --environment development
   ```

4. **Access the services:**
   - API: http://localhost:8080
   - API Documentation: http://localhost:8080/docs
   - Health Check: http://localhost:8080/health
### Prod
uction Environment

1. **Configure environment variables:**
   ```bash
   # Copy and customize the production environment file
   cp config/production.env config/production.local.env
   # Edit production.local.env with your production values
   ```

2. **Deploy to production:**
   ```bash
   ./deploy.sh production deploy
   ```

3. **Validate deployment:**
   ```bash
   python test_deployment.py --environment production --host your-production-host
   ```

## Environment Configuration

### Development (`config/development.env`)
- Debug mode enabled
- Relaxed security settings
- Local database connections
- Verbose logging

### Staging (`config/staging.env`)
- Production-like configuration
- Moderate security settings
- External database connections
- Structured logging

### Production (`config/production.env`)
- Strict security settings
- Environment variable overrides required
- Performance optimizations
- Minimal logging

### Required Environment Variables (Production)

```bash
# Security
JWT_SECRET_KEY=your-secure-jwt-secret-key
CORS_ORIGINS=https://your-domain.com,https://api.your-domain.com

# Database
REDIS_URL=redis://your-redis-host:6379
NEO4J_URL=bolt://your-neo4j-host:7687
NEO4J_USERNAME=your-neo4j-username
NEO4J_PASSWORD=your-neo4j-password
```

## Deployment Methods

### 1. Docker Compose (Recommended for Development/Staging)

**Start services:**
```bash
./deploy.sh [environment] deploy
```

**Stop services:**
```bash
./deploy.sh [environment] stop
```

**View logs:**
```bash
./deploy.sh [environment] logs
```

**Check status:**
```bash
./deploy.sh [environment] status
```

### 2. Kubernetes (Recommended for Production)

**Deploy to Kubernetes:**
```bash
./deploy.sh production k8s
```

**Manual Kubernetes deployment:**
```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n tta-player-experience

# View logs
kubectl logs -f deployment/player-experience-api-deployment -n tta-player-experience
```

### 3. TTA Orchestration System

The Player Experience Interface integrates with the main TTA orchestration system:

```bash
# From the TTA root directory
./tta.sh start player_experience

# Or using Python
uv run python src/main.py start player_experience
```## Health C
hecks and Monitoring

### Health Endpoints
- `/health`: Basic health check
- `/health/detailed`: Detailed health with database status

### Monitoring Integration
The service includes built-in monitoring capabilities:
- Prometheus metrics (production)
- Structured logging
- Performance tracking
- Error reporting

### Deployment Validation
Use the deployment validation script to verify your deployment:

```bash
# Basic validation
python test_deployment.py

# Full validation with custom endpoint
python test_deployment.py --host api.yourdomain.com --port 443 --environment production

# Save results to file
python test_deployment.py --output deployment-results.json
```

## Integration with TTA System

The Player Experience Interface integrates with the main TTA orchestration system through:

1. **Component Registration:** Automatically discovered by the TTA orchestrator
2. **Configuration:** Managed through `config/tta_config.yaml`
3. **Dependencies:** Depends on Redis and Neo4j services
4. **Health Monitoring:** Integrated with TTA health checking

### TTA Configuration
```yaml
# config/tta_config.yaml
player_experience:
  enabled: true
  api:
    port: 8080
  database:
    redis_url: "redis://localhost:6379"
    neo4j_url: "bolt://localhost:7687"
```

## Development and Testing

### Local Development Setup
```bash
# Install dependencies
uv sync

# Run in development mode
uv run python -m src.player_experience.api.main

# Run tests
uv run python -m pytest tests/
```

### Testing Deployment
```bash
# Run all deployment tests
python test_deployment.py --environment development

# Run specific test categories
python test_deployment.py --environment staging --output results.json
```

This deployment guide provides comprehensive coverage of all deployment scenarios and troubleshooting steps for the Player Experience Interface.