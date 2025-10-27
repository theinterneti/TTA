# TTA Staging Environment - Operations Guide

This guide covers day-to-day operations, maintenance procedures, and troubleshooting for the TTA staging environment.

## 📋 Daily Operations

### Morning Checklist

```bash
# 1. Check overall system health
./scripts/staging-health-check.sh

# 2. Review overnight logs
./scripts/deploy-staging-homelab.sh logs | grep ERROR

# 3. Check resource usage
docker stats --no-stream

# 4. Verify backup completion
ls -la backups/ | tail -5

# 5. Check monitoring dashboards
# Visit: http://localhost:3001 (Grafana)
```

### Service Management

#### Starting Services
```bash
# Start all services
./scripts/deploy-staging-homelab.sh deploy --force

# Start specific service
docker-compose -f docker-compose.staging-homelab.yml up -d neo4j-staging

# Start with logs
docker-compose -f docker-compose.staging-homelab.yml up neo4j-staging
```

#### Stopping Services
```bash
# Stop all services
./scripts/deploy-staging-homelab.sh stop

# Stop specific service
docker-compose -f docker-compose.staging-homelab.yml stop neo4j-staging

# Stop and remove containers
docker-compose -f docker-compose.staging-homelab.yml down
```

#### Restarting Services
```bash
# Restart all services
./scripts/deploy-staging-homelab.sh restart

# Restart specific service
docker-compose -f docker-compose.staging-homelab.yml restart neo4j-staging

# Force recreate service
docker-compose -f docker-compose.staging-homelab.yml up -d --force-recreate neo4j-staging
```

### Log Management

#### Viewing Logs
```bash
# All services
./scripts/deploy-staging-homelab.sh logs

# Specific service
./scripts/deploy-staging-homelab.sh logs player-api-staging

# Follow logs in real-time
docker-compose -f docker-compose.staging-homelab.yml logs -f player-api-staging

# Last 100 lines
docker-compose -f docker-compose.staging-homelab.yml logs --tail=100 player-api-staging
```

#### Log Rotation
```bash
# Configure log rotation (add to /etc/logrotate.d/tta-staging)
/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

## 🔧 Maintenance Procedures

### Weekly Maintenance

#### System Updates
```bash
# Update Docker images
docker-compose -f docker-compose.staging-homelab.yml pull

# Rebuild custom images
docker-compose -f docker-compose.staging-homelab.yml build --no-cache

# Update deployment
./scripts/deploy-staging-homelab.sh update
```

#### Database Maintenance
```bash
# Neo4j maintenance
docker exec tta-staging-homelab_neo4j-staging_1 \
  cypher-shell -u neo4j -p $NEO4J_STAGING_PASSWORD \
  "CALL db.stats.retrieve('GRAPH COUNTS')"

# PostgreSQL maintenance
docker exec tta-staging-homelab_postgres-staging_1 \
  psql -U tta_staging_user -d tta_staging -c "VACUUM ANALYZE;"

# Redis maintenance
docker exec tta-staging-homelab_redis-staging_1 \
  redis-cli BGREWRITEAOF
```

#### Cleanup Operations
```bash
# Clean up Docker resources
./scripts/deploy-staging-homelab.sh cleanup

# Remove old backups (keep last 7 days)
find backups/ -name "staging_backup_*" -mtime +7 -delete

# Clean up old logs
find logs/ -name "*.log" -mtime +30 -delete
```

### Monthly Maintenance

#### Security Updates
```bash
# Update base system
sudo apt update && sudo apt upgrade -y

# Update Docker
sudo apt update docker-ce docker-ce-cli containerd.io

# Restart Docker daemon
sudo systemctl restart docker
```

#### Performance Review
```bash
# Generate performance report
./scripts/staging-health-check.sh > reports/monthly_health_$(date +%Y%m).txt

# Review resource usage trends in Grafana
# Check: CPU, Memory, Disk, Network usage over past month
```

#### Backup Verification
```bash
# Test backup restore process
./scripts/staging-restore.sh --test /path/to/recent/backup

# Verify backup integrity
./scripts/staging-backup.sh --verify
```

## 🚨 Incident Response

### Service Down Procedure

1. **Immediate Assessment**
   ```bash
   # Check service status
   ./scripts/staging-health-check.sh

   # Check Docker daemon
   sudo systemctl status docker

   # Check system resources
   top
   df -h
   ```

2. **Service Recovery**
   ```bash
   # Try restart first
   docker-compose -f docker-compose.staging-homelab.yml restart [service-name]

   # If restart fails, recreate
   docker-compose -f docker-compose.staging-homelab.yml up -d --force-recreate [service-name]

   # Check logs for errors
   docker-compose -f docker-compose.staging-homelab.yml logs [service-name]
   ```

3. **Escalation**
   - If service won't start, check system resources
   - If database corruption suspected, restore from backup
   - Document incident in logs/incidents/

### Database Issues

#### Neo4j Problems
```bash
# Check Neo4j status
docker exec tta-staging-homelab_neo4j-staging_1 \
  cypher-shell -u neo4j -p $NEO4J_STAGING_PASSWORD "CALL dbms.components()"

# Check database consistency
docker exec tta-staging-homelab_neo4j-staging_1 \
  neo4j-admin check-consistency --database=neo4j

# Repair if needed
docker exec tta-staging-homelab_neo4j-staging_1 \
  neo4j-admin check-consistency --database=neo4j --fix
```

#### Redis Problems
```bash
# Check Redis status
docker exec tta-staging-homelab_redis-staging_1 redis-cli ping

# Check memory usage
docker exec tta-staging-homelab_redis-staging_1 redis-cli info memory

# Clear cache if needed
docker exec tta-staging-homelab_redis-staging_1 redis-cli flushall
```

#### PostgreSQL Problems
```bash
# Check PostgreSQL status
docker exec tta-staging-homelab_postgres-staging_1 pg_isready

# Check database connections
docker exec tta-staging-homelab_postgres-staging_1 \
  psql -U tta_staging_user -d tta_staging -c "SELECT count(*) FROM pg_stat_activity;"

# Restart PostgreSQL if needed
docker-compose -f docker-compose.staging-homelab.yml restart postgres-staging
```

### Performance Issues

#### High CPU Usage
```bash
# Identify high CPU processes
docker stats --no-stream | sort -k3 -nr

# Check system load
uptime
htop

# Scale down if needed
docker-compose -f docker-compose.staging-homelab.yml scale player-api-staging=2
```

#### High Memory Usage
```bash
# Check memory usage by container
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Check system memory
free -h

# Restart memory-intensive services
docker-compose -f docker-compose.staging-homelab.yml restart neo4j-staging
```

#### Disk Space Issues
```bash
# Check disk usage
df -h

# Clean up Docker resources
docker system prune -f
docker volume prune -f

# Remove old backups
find backups/ -name "staging_backup_*" -mtime +3 -delete
```

## 📊 Monitoring and Alerting

### Key Metrics to Monitor

#### Application Metrics
- API response times (p50, p95, p99)
- Request rate and error rate
- Active user sessions
- WebSocket connections

#### Infrastructure Metrics
- CPU usage per service
- Memory usage per service
- Disk usage and I/O
- Network throughput

#### Database Metrics
- Neo4j query performance
- Redis hit rate and memory usage
- PostgreSQL connection count and query time

### Alert Thresholds

#### Critical Alerts
- Service down for > 1 minute
- Disk space < 10%
- Memory usage > 95%
- API error rate > 10%

#### Warning Alerts
- CPU usage > 80% for 5 minutes
- Memory usage > 85% for 5 minutes
- API response time p95 > 2 seconds
- Disk space < 20%

### Grafana Dashboard URLs

- **Overview**: http://localhost:3001/d/tta-staging-overview
- **Infrastructure**: http://localhost:3001/d/tta-staging-infrastructure
- **Application**: http://localhost:3001/d/tta-staging-application
- **Database**: http://localhost:3001/d/tta-staging-database

## 🔄 Backup and Recovery

### Backup Schedule

#### Automated Backups
```bash
# Add to crontab for automated backups
# Daily backup at 2 AM
0 2 * * * /path/to/scripts/staging-backup.sh

# Weekly full backup on Sunday at 1 AM
0 1 * * 0 /path/to/scripts/staging-backup.sh --full
```

#### Manual Backups
```bash
# Create immediate backup
./scripts/staging-backup.sh

# Create backup with custom name
./scripts/staging-backup.sh --name "pre-update-backup"

# Create full backup (includes logs and configs)
./scripts/staging-backup.sh --full
```

### Recovery Procedures

#### Full System Recovery
```bash
# Stop all services
./scripts/deploy-staging-homelab.sh stop

# Restore from backup
./scripts/staging-restore.sh /path/to/backup/directory

# Start services
./scripts/deploy-staging-homelab.sh deploy --force

# Verify recovery
./scripts/staging-health-check.sh
```

#### Partial Recovery
```bash
# Restore specific database
./scripts/staging-restore.sh --database neo4j /path/to/backup

# Restore configuration only
./scripts/staging-restore.sh --config-only /path/to/backup
```

## 📝 Documentation Updates

### Keeping Documentation Current

1. **After Configuration Changes**
   - Update environment variable documentation
   - Update configuration examples
   - Test all documented procedures

2. **After Service Updates**
   - Update version numbers
   - Update API endpoints if changed
   - Update monitoring dashboards

3. **After Incident Resolution**
   - Document root cause
   - Update troubleshooting procedures
   - Add preventive measures

### Documentation Locations

- **Main Guide**: `docs/staging-homelab/README.md`
- **Operations**: `docs/staging-homelab/OPERATIONS.md`
- **Troubleshooting**: `docs/staging-homelab/TROUBLESHOOTING.md`
- **API Documentation**: `docs/api/`
- **Runbooks**: `docs/runbooks/`

## 🔐 Security Operations

### Security Checklist

#### Daily
- [ ] Review authentication logs
- [ ] Check for failed login attempts
- [ ] Verify SSL certificate status
- [ ] Review firewall logs

#### Weekly
- [ ] Update passwords if needed
- [ ] Review user access logs
- [ ] Check for security updates
- [ ] Scan for vulnerabilities

#### Monthly
- [ ] Full security audit
- [ ] Update security documentation
- [ ] Review and rotate API keys
- [ ] Test backup encryption

### Security Incident Response

1. **Immediate Actions**
   - Isolate affected services
   - Change compromised credentials
   - Review access logs
   - Document incident

2. **Investigation**
   - Analyze logs for attack vectors
   - Check for data exfiltration
   - Assess damage scope
   - Preserve evidence

3. **Recovery**
   - Restore from clean backups
   - Apply security patches
   - Update security measures
   - Monitor for reoccurrence

---

## 📞 Emergency Contacts

- **System Administrator**: [Your contact info]
- **Database Administrator**: [Your contact info]
- **Security Team**: [Your contact info]
- **On-call Rotation**: [Your rotation schedule]
