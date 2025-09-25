# TTA Franchise World System - Production Deployment Guide

## 🚀 **PRODUCTION-READY DEPLOYMENT COMPLETE**

This directory contains a comprehensive, production-ready deployment infrastructure for the TTA Franchise World System, featuring Docker containerization, monitoring, security, and automated backup systems.

## 📋 **Prerequisites**

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Linux/macOS** environment (tested on Ubuntu 20.04+)
- **4GB RAM minimum** (8GB recommended for production)
- **20GB disk space** (for logs, backups, and databases)
- **Network access** for container image downloads

## 🏗️ **Architecture Overview**

### **Core Services**
- **TTA Franchise API** (Python FastAPI) - Main therapeutic gaming API
- **Bridge Service** (Node.js) - TypeScript-Python integration layer
- **Nginx** - Reverse proxy, load balancer, SSL termination
- **Redis** - Session storage and caching
- **Neo4j** - Knowledge graph database for world relationships

### **Monitoring Stack**
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Monitoring dashboards and visualization
- **Loki** - Log aggregation and analysis
- **Promtail** - Log shipping agent

### **Operations**
- **Backup Service** - Automated database and configuration backups
- **Health Checks** - Comprehensive service monitoring
- **Security** - Rate limiting, CORS, security headers

## 🚀 **Quick Start Deployment**

### **1. Initial Setup**
```bash
# Clone and navigate to deployment directory
cd src/player_experience/franchise_worlds/deployment

# Copy and configure environment
cp .env.example .env
# Edit .env with your production values (see Configuration section)

# Make scripts executable
chmod +x deploy.sh validate-deployment.sh backup.sh
```

### **2. Deploy System**
```bash
# Full production deployment
./deploy.sh

# Or update existing deployment
./deploy.sh --update
```

### **3. Validate Deployment**
```bash
# Run comprehensive validation
./validate-deployment.sh

# Quick health check
./validate-deployment.sh --quick
```

## ⚙️ **Configuration**

### **Required Environment Variables**
Edit `.env` file with these critical settings:

```bash
# Security (REQUIRED)
NEO4J_PASSWORD=your_secure_neo4j_password_here
JWT_SECRET_KEY=your_very_long_and_secure_jwt_secret_key_here_at_least_32_characters
GRAFANA_PASSWORD=your_secure_grafana_admin_password_here

# Domain Configuration
DOMAIN_NAME=tta.yourdomain.com
CORS_ORIGINS=https://tta.yourdomain.com,https://admin.yourdomain.com

# Backup Configuration (Optional but Recommended)
BACKUP_S3_BUCKET=your-tta-backup-bucket
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
```

### **SSL Configuration**
For production with custom domain:
1. Obtain SSL certificates (Let's Encrypt recommended)
2. Place certificates in `ssl/` directory
3. Update `nginx.conf` to enable HTTPS server block
4. Restart nginx: `docker-compose restart nginx`

## 📊 **Service URLs**

After successful deployment:

| Service | URL | Description |
|---------|-----|-------------|
| **API** | `http://localhost/api/v1/` | Main TTA Franchise API |
| **Bridge** | `http://localhost/bridge/` | Node.js bridge service |
| **Grafana** | `http://localhost:3000/` | Monitoring dashboards |
| **Prometheus** | `http://localhost:9090/` | Metrics and alerting |
| **Neo4j Browser** | `http://localhost:7474/` | Database management |

## 🔧 **Management Commands**

### **Service Management**
```bash
# View service status
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Restart services
docker-compose restart [service_name]

# Stop all services
./deploy.sh --stop

# Update deployment
./deploy.sh --update
```

### **Backup Management**
```bash
# Manual backup
docker-compose exec backup /app/backup.sh

# Verify backups
docker-compose exec backup /app/backup.sh --verify

# Redis-only backup
docker-compose exec backup /app/backup.sh --redis-only
```

### **Monitoring**
```bash
# System health check
curl http://localhost/health

# API metrics
curl http://localhost/metrics

# Bridge service status
curl http://localhost/bridge/system/status
```

## 🛡️ **Security Features**

### **Implemented Security Measures**
- **Rate Limiting** - API and authentication endpoints protected
- **CORS Configuration** - Restricted to configured origins
- **Security Headers** - X-Frame-Options, X-Content-Type-Options, etc.
- **Input Validation** - Comprehensive request validation
- **Error Handling** - Secure error responses without information leakage
- **Container Security** - Non-root users, minimal attack surface

### **Production Security Checklist**
- [ ] Change all default passwords in `.env`
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Set up firewall rules (ports 80, 443 only)
- [ ] Configure monitoring alerts
- [ ] Set up log rotation and retention
- [ ] Enable backup encryption
- [ ] Review and test disaster recovery procedures

## 📈 **Monitoring and Alerting**

### **Grafana Dashboards**
- **System Overview** - Service health, response times, error rates
- **API Performance** - Request rates, latencies, throughput
- **Database Metrics** - Connection pools, query performance
- **World Usage** - Therapeutic session analytics

### **Prometheus Alerts**
- Service downtime detection
- High error rate alerts
- Performance degradation warnings
- Database connectivity issues
- Disk space monitoring

### **Log Management**
- Structured JSON logging
- Centralized log aggregation with Loki
- Log retention policies
- Error tracking with Sentry (if configured)

## 🔄 **Backup and Recovery**

### **Automated Backups**
- **Schedule**: Daily at 2 AM (configurable)
- **Retention**: 30 days (configurable)
- **Components**: Redis data, Neo4j database, application logs, configuration
- **Storage**: Local + S3 (if configured)

### **Recovery Procedures**
```bash
# Restore Redis backup
docker exec tta-redis redis-cli FLUSHALL
docker cp backup_file.rdb tta-redis:/data/dump.rdb
docker-compose restart redis

# Restore Neo4j backup
docker exec tta-neo4j neo4j-admin database load --from-path=/tmp backup_file.dump
docker-compose restart neo4j
```

## 🚨 **Troubleshooting**

### **Common Issues**

**Services won't start:**
```bash
# Check logs
docker-compose logs [service_name]

# Check disk space
df -h

# Check memory usage
free -h
```

**API returning 500 errors:**
```bash
# Check API logs
docker-compose logs tta-franchise-api

# Verify database connectivity
./validate-deployment.sh --quick
```

**Bridge service failing:**
```bash
# Check Node.js bridge logs
docker-compose logs tta-franchise-bridge

# Test bridge scripts manually
docker exec tta-franchise-bridge node scripts/initialize-system.js
```

### **Performance Issues**
- Monitor Grafana dashboards for bottlenecks
- Check database connection pool usage
- Review API response times
- Verify adequate system resources

## 📞 **Support and Maintenance**

### **Health Monitoring**
- Set up external monitoring (UptimeRobot, Pingdom)
- Configure alert notifications (email, Slack)
- Regular backup verification
- Monthly security updates

### **Scaling Considerations**
- **Horizontal Scaling**: Add more API containers behind load balancer
- **Database Scaling**: Neo4j clustering, Redis Cluster
- **CDN Integration**: Static asset delivery
- **Caching Strategy**: Redis-based response caching

## 🎯 **Production Readiness Checklist**

- [x] **Docker Infrastructure** - Multi-container orchestration
- [x] **Security Configuration** - Rate limiting, CORS, headers
- [x] **Monitoring Stack** - Prometheus, Grafana, Loki
- [x] **Backup System** - Automated backups with S3 integration
- [x] **Health Checks** - Comprehensive service monitoring
- [x] **CI/CD Pipeline** - GitHub Actions workflow
- [x] **Documentation** - Complete deployment and operations guide
- [x] **Validation Testing** - Automated deployment verification

## 🌟 **Next Steps**

1. **Deploy to Staging** - Test with staging environment
2. **Load Testing** - Comprehensive performance validation
3. **Security Audit** - Third-party security assessment
4. **User Acceptance Testing** - Real-world therapeutic session validation
5. **Production Deployment** - Go-live with monitoring and support

---

**The TTA Franchise World System is now production-ready with enterprise-grade infrastructure, monitoring, and operational capabilities!** 🎉
