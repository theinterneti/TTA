# 🚀 TTA Simulation Framework - Production Deployment Guide

## 📋 **Overview**

This guide provides comprehensive instructions for deploying the TTA Simulation Framework in production environments, including homelab, staging, and production deployments.

## ✅ **Prerequisites**

### **System Requirements**
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Node.js**: Version 18 or higher (for development)
- **Memory**: Minimum 4GB RAM, Recommended 8GB+
- **Storage**: Minimum 20GB free space
- **Network**: Stable internet connection for AI model access

### **Environment Setup**
- Access to TTA homelab infrastructure
- Valid OpenRouter API key
- Database credentials (PostgreSQL, Redis, Neo4j)
- Monitoring stack (Prometheus, Grafana) configured

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    TTA Homelab Environment                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Player API    │  │ Player Frontend │  │   Nginx     │ │
│  │   (Port 8080)   │  │   (Port 3000)   │  │ (Port 80)   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   PostgreSQL    │  │      Redis      │  │    Neo4j    │ │
│  │   (Port 5432)   │  │   (Port 6379)   │  │ (Port 7687) │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Prometheus    │  │     Grafana     │  │ Simulation  │ │
│  │   (Port 9090)   │  │   (Port 3001)   │  │ Framework   │ │
│  │                 │  │                 │  │ (Port 3002) │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Deployment**

### **1. Automated Deployment (Recommended)**

```bash
# Clone the repository
git clone https://github.com/theinterneti/TTA.git
cd TTA

# Deploy to homelab environment
./scripts/deploy-simulation-framework.sh deploy --environment homelab

# Check deployment status
./scripts/deploy-simulation-framework.sh status
```

### **2. Manual Deployment**

```bash
# Navigate to simulation framework directory
cd testing/simulation

# Install dependencies
npm ci

# Build the framework
npm run build

# Build Docker image
docker build -t tta-simulation-framework .

# Deploy using Docker Compose
cd ../../
docker-compose -f docker-compose.homelab.yml up -d simulation-framework
```

## ⚙️ **Configuration**

### **Environment Variables**

The framework uses environment-specific configuration files:

- **Development**: `.env.development`
- **Homelab**: Uses `.env.homelab` from project root
- **Production**: `.env.production`

### **Key Configuration Settings**

```bash
# Core Settings
NODE_ENV=production
PORT=3002
HOST=0.0.0.0

# Performance Settings
MAX_CONCURRENT_SIMULATIONS=5
SIMULATION_TIMEOUT_MINUTES=300

# Quality Thresholds
MIN_ENGAGEMENT_SCORE=0.85
MIN_IMMERSION_SCORE=0.80
MIN_THERAPEUTIC_INTEGRATION_SCORE=0.75

# Integration Settings
API_BASE_URL=http://player-api:8080
REDIS_URL=redis://redis:6379
NEO4J_URI=bolt://neo4j:7687
```

## 📊 **Monitoring and Observability**

### **Health Checks**

The framework provides comprehensive health monitoring:

```bash
# Check framework health
curl http://localhost:3002/health

# Expected response:
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 3600,
    "activeSimulations": 2,
    "environment": "production"
  },
  "timestamp": 1640995200000
}
```

### **Grafana Dashboard**

Access the simulation framework dashboard:
- **URL**: http://localhost:3001
- **Username**: admin
- **Password**: Set in `.env.homelab` as `GRAFANA_PASSWORD`

**Key Metrics Monitored**:
- Simulation success rates
- Average engagement scores
- World generation quality
- Persona performance distribution
- Entertainment vs therapeutic balance

### **Prometheus Metrics**

Available at `http://localhost:3002/metrics`:

```
# Simulation Framework Metrics
tta_active_simulations_total
tta_simulations_completed_total
tta_simulations_failed_total
tta_engagement_score
tta_immersion_score
tta_world_generation_score
tta_therapeutic_integration_score
```

## 🔧 **Management Commands**

### **Using the Deployment Script**

```bash
# Deploy framework
./scripts/deploy-simulation-framework.sh deploy --environment homelab

# Start services
./scripts/deploy-simulation-framework.sh start

# Stop services
./scripts/deploy-simulation-framework.sh stop

# Restart services
./scripts/deploy-simulation-framework.sh restart

# Check status
./scripts/deploy-simulation-framework.sh status

# View logs
./scripts/deploy-simulation-framework.sh logs

# Run validation tests
./scripts/deploy-simulation-framework.sh test

# Update framework
./scripts/deploy-simulation-framework.sh update

# Cleanup old data
./scripts/deploy-simulation-framework.sh cleanup
```

### **Direct Docker Commands**

```bash
# View container status
docker-compose -f docker-compose.homelab.yml ps simulation-framework

# View logs
docker-compose -f docker-compose.homelab.yml logs -f simulation-framework

# Execute commands in container
docker-compose -f docker-compose.homelab.yml exec simulation-framework npm run test:quick

# Scale services (if needed)
docker-compose -f docker-compose.homelab.yml up -d --scale simulation-framework=2
```

## 🧪 **Running Simulations**

### **API Endpoints**

```bash
# Get available configurations
curl http://localhost:3002/configurations

# Start a simulation
curl -X POST http://localhost:3002/simulations \
  -H "Content-Type: application/json" \
  -d '{"configName": "QUICK_TEST"}'

# Check simulation status
curl http://localhost:3002/simulations/{simulationId}

# Get active simulations
curl http://localhost:3002/simulations
```

### **Available Test Configurations**

1. **QUICK_TEST** (15 minutes)
   - 2 personas, simple worlds
   - Ideal for CI/CD validation

2. **COMPREHENSIVE** (2 hours)
   - 8 personas, multiple complexity levels
   - Full platform validation

3. **PRODUCTION_VALIDATION** (4 hours)
   - Complete assessment
   - Pre-deployment validation

### **Command Line Testing**

```bash
# Quick validation test
npm run test:quick

# Comprehensive test
npm run test:comprehensive

# Custom configuration test
npm run test:custom

# Validate framework
npm run validate
```

## 📈 **Performance Optimization**

### **Resource Allocation**

```yaml
# Docker Compose resource limits
simulation-framework:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
```

### **Scaling Considerations**

- **Horizontal Scaling**: Multiple framework instances
- **Load Balancing**: Nginx upstream configuration
- **Database Optimization**: Connection pooling
- **Caching**: Redis for simulation state

## 🔒 **Security**

### **Network Security**
- Internal Docker network isolation
- API rate limiting enabled
- CORS configuration for allowed origins

### **Data Security**
- Simulation data encryption at rest
- Secure API endpoints
- No sensitive data in logs

### **Access Control**
- Container runs as non-root user
- Minimal container privileges
- Health check endpoints only

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Framework Won't Start**
   ```bash
   # Check logs
   docker-compose -f docker-compose.homelab.yml logs simulation-framework

   # Verify dependencies
   docker-compose -f docker-compose.homelab.yml ps
   ```

2. **Health Check Failures**
   ```bash
   # Check service status
   curl -v http://localhost:3002/health

   # Verify port binding
   netstat -tlnp | grep 3002
   ```

3. **Simulation Failures**
   ```bash
   # Check simulation logs
   docker-compose -f docker-compose.homelab.yml exec simulation-framework npm run validate

   # Verify AI model access
   curl -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models
   ```

### **Log Analysis**

```bash
# Framework logs
docker-compose -f docker-compose.homelab.yml logs simulation-framework

# System resource usage
docker stats tta-homelab-simulation-framework

# Container health
docker inspect tta-homelab-simulation-framework --format='{{.State.Health.Status}}'
```

## 📞 **Support and Maintenance**

### **Regular Maintenance**

- **Daily**: Automated health checks and log rotation
- **Weekly**: Performance metrics review
- **Monthly**: Framework updates and security patches

### **Backup and Recovery**

```bash
# Backup simulation data
docker-compose -f docker-compose.homelab.yml exec simulation-framework npm run backup

# Restore from backup
docker-compose -f docker-compose.homelab.yml exec simulation-framework npm run restore
```

### **Updates and Upgrades**

```bash
# Update framework
./scripts/deploy-simulation-framework.sh update

# Manual update process
git pull origin main
docker-compose -f docker-compose.homelab.yml build simulation-framework
docker-compose -f docker-compose.homelab.yml up -d simulation-framework
```

## 🎯 **Success Metrics**

### **Key Performance Indicators**

- **Availability**: >99.5% uptime
- **Response Time**: <2s for API endpoints
- **Simulation Success Rate**: >95%
- **Average Engagement Score**: >85%
- **Framework Validation**: 100% pass rate

### **Quality Thresholds**

- **Engagement**: Minimum 85%
- **Immersion**: Minimum 80%
- **Therapeutic Integration**: Minimum 75%
- **Entertainment Value**: Minimum 85%
- **World Generation Success**: Minimum 95%

---

**🎉 The TTA Simulation Framework is now ready for production use in your homelab environment!**

For additional support or questions, refer to the framework documentation or contact the development team.
