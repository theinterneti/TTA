# TTA Monitoring Stack Architecture

## Overview

The TTA monitoring stack provides comprehensive observability for the Therapeutic Text Adventure system through metrics collection, log aggregation, and visualization.

## Architecture

### Services

#### 1. Prometheus (Metrics Collection)
- **Image**: `prom/prometheus:v2.45.0`
- **Port**: 9090
- **Purpose**: Time-series metrics database and query engine
- **Configuration**: `monitoring/prometheus/prometheus.yml`
- **Health Check**: `wget http://localhost:9090/-/healthy`
- **Data Retention**: 30 days
- **Dependencies**: None (base service)

#### 2. Grafana (Visualization)
- **Image**: `grafana/grafana:10.0.0`
- **Port**: 3001 (mapped from 3000)
- **Purpose**: Metrics visualization and dashboarding
- **Configuration**: 
  - Dashboards: `monitoring/grafana/dashboards/`
  - Datasources: `monitoring/grafana/datasources/`
- **Health Check**: `wget http://localhost:3000/api/health`
- **Dependencies**: Prometheus, Loki
- **Default Credentials**: admin/admin

#### 3. Loki (Log Aggregation)
- **Image**: `grafana/loki:2.9.0`
- **Port**: 3100
- **Purpose**: Log aggregation and querying
- **Configuration**: Built-in `/etc/loki/local-config.yaml`
- **Health Check**: `wget http://localhost:3100/ready`
- **Dependencies**: None (base service)

#### 4. Promtail (Log Shipping)
- **Image**: `grafana/promtail:2.9.0`
- **Purpose**: Log collection and forwarding to Loki
- **Configuration**: `monitoring/promtail/promtail.yml`
- **Dependencies**: Loki
- **Volumes**:
  - `/var/log:/var/log:ro` - System logs
  - `/var/lib/docker/containers:/var/lib/docker/containers:ro` - Container logs

#### 5. Node Exporter (Host Metrics)
- **Image**: `prom/node-exporter:v1.6.0`
- **Port**: 9100
- **Purpose**: Host-level metrics (CPU, memory, disk, network)
- **Dependencies**: None (base service)

#### 6. cAdvisor (Container Metrics)
- **Image**: `gcr.io/cadvisor/cadvisor:v0.47.0`
- **Port**: 8080
- **Purpose**: Container-level metrics and resource usage
- **Dependencies**: None (base service)
- **Requires**: Privileged mode for full metrics access

### Service Dependency Chain

```
┌─────────────┐
│ Prometheus  │ (Base - No dependencies)
└──────┬──────┘
       │
       ├──────────────────┐
       │                  │
┌──────▼──────┐    ┌──────▼──────┐
│    Loki     │    │Node Exporter│
└──────┬──────┘    └─────────────┘
       │
       ├──────────────────┐
       │                  │
┌──────▼──────┐    ┌──────▼──────┐
│  Promtail   │    │   Grafana   │
└─────────────┘    └─────────────┘
                          │
                   ┌──────▼──────┐
                   │  cAdvisor   │
                   └─────────────┘
```

### Network Configuration

- **Network Name**: `tta-monitoring`
- **Driver**: bridge
- **Purpose**: Isolated network for monitoring services

### Volume Configuration

- **prometheus-data**: Persistent storage for Prometheus metrics
- **grafana-data**: Persistent storage for Grafana dashboards and settings
- **loki-data**: Persistent storage for Loki logs

## Deployment

### Local Development (WSL2)

```bash
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

**Verification:**
```bash
# Check container status
docker ps --filter "name=tta-"

# Check Prometheus health
curl http://localhost:9090/-/healthy

# Check Grafana health
curl http://localhost:3000/api/health

# Check Loki health
curl http://localhost:3100/ready
```

**Cleanup:**
```bash
cd monitoring
docker-compose -f docker-compose.monitoring.yml down -v
```

### CI/CD (GitHub Actions)

The monitoring stack is validated in the `monitoring-validation` job of `.github/workflows/tests.yml`:

1. **Checkout**: Repository is checked out first
2. **Start Services**: `docker-compose up -d prometheus grafana`
3. **Health Checks**: Wait for services to be healthy (60s timeout)
4. **Validation**: Test API endpoints and metrics queries
5. **Cleanup**: `docker-compose down -v` in always() block

**Key Fix**: Services are started AFTER checkout to ensure configuration files are available.

## Health Checks

### Prometheus
- **Endpoint**: `http://localhost:9090/-/healthy`
- **Method**: wget/curl
- **Interval**: 30s
- **Timeout**: 10s
- **Retries**: 3
- **Start Period**: 30s

### Grafana
- **Endpoint**: `http://localhost:3000/api/health`
- **Method**: wget/curl
- **Interval**: 30s
- **Timeout**: 10s
- **Retries**: 3
- **Start Period**: 30s

### Loki
- **Endpoint**: `http://localhost:3100/ready`
- **Method**: wget/curl
- **Interval**: 30s
- **Timeout**: 10s
- **Retries**: 3
- **Start Period**: 30s

## Troubleshooting

### Issue: Containers fail to start in GitHub Actions

**Symptom**: Volume mount errors, configuration files not found

**Root Cause**: GitHub Actions services start BEFORE repository checkout

**Solution**: Use explicit docker-compose steps AFTER checkout instead of services section

```yaml
steps:
  - uses: actions/checkout@v4
  - name: Start monitoring stack
    run: |
      cd monitoring
      docker-compose -f docker-compose.monitoring.yml up -d prometheus grafana
```

### Issue: Health checks failing

**Symptom**: Containers start but health checks timeout

**Diagnosis**:
```bash
# Check container logs
docker logs tta-prometheus
docker logs tta-grafana
docker logs tta-loki

# Check if services are listening
docker exec tta-prometheus wget --spider http://localhost:9090/-/healthy
docker exec tta-grafana wget --spider http://localhost:3000/api/health
```

**Common Causes**:
1. Configuration file syntax errors
2. Port conflicts with existing services
3. Insufficient resources (memory/CPU)
4. Network connectivity issues

### Issue: Prometheus not scraping metrics

**Diagnosis**:
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Prometheus configuration
docker exec tta-prometheus cat /etc/prometheus/prometheus.yml
```

**Solution**: Verify scrape configs in `monitoring/prometheus/prometheus.yml`

### Issue: Grafana datasource connection failed

**Diagnosis**:
```bash
# Test Prometheus connectivity from Grafana container
docker exec tta-grafana wget -O- http://prometheus:9090/api/v1/query?query=up

# Check datasource configuration
docker exec tta-grafana cat /etc/grafana/provisioning/datasources/prometheus.yml
```

**Solution**: Ensure datasource URL uses service name (`http://prometheus:9090`) not localhost

### Issue: Loki not receiving logs

**Diagnosis**:
```bash
# Check Promtail logs
docker logs tta-promtail

# Test Loki API
curl http://localhost:3100/loki/api/v1/labels

# Check Promtail configuration
docker exec tta-promtail cat /etc/promtail/config.yml
```

**Solution**: Verify Promtail can access log directories and Loki URL is correct

## Security Considerations

### Container Security
- All services run with `no-new-privileges:true`
- Promtail, Node Exporter, and cAdvisor run in read-only mode
- Only cAdvisor requires privileged mode (for container metrics)

### Network Security
- Services communicate over isolated bridge network
- Only necessary ports exposed to host
- No external network access required

### Secrets Management
- Grafana admin password set via environment variable
- Consider using Docker secrets for production
- Rotate credentials regularly

## Performance Tuning

### Prometheus
- **Retention**: Adjust `--storage.tsdb.retention.time` for longer/shorter retention
- **Memory**: Increase container memory for large metric volumes
- **Scrape Interval**: Balance between granularity and resource usage

### Grafana
- **Plugins**: Install only necessary plugins to reduce startup time
- **Caching**: Configure caching for frequently accessed dashboards

### Loki
- **Retention**: Configure retention policies in Loki config
- **Compaction**: Enable compaction for better query performance

## Monitoring Best Practices

1. **Start Simple**: Begin with Prometheus and Grafana only
2. **Add Gradually**: Add Loki/Promtail when log aggregation needed
3. **Monitor the Monitors**: Set up alerts for monitoring stack health
4. **Regular Backups**: Backup Grafana dashboards and Prometheus data
5. **Resource Limits**: Set appropriate CPU/memory limits in production
6. **Log Rotation**: Configure log rotation for Promtail sources

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

