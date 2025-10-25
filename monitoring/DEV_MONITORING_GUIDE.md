# TTA Monitoring Setup - Development Guide

This guide will help you set up Prometheus and Grafana for monitoring your TTA development environment.

## Quick Start

### 1. Start the Monitoring Stack

```bash
./monitoring-dev.sh start
```

This will start:
- **Prometheus** on http://localhost:9090
- **Grafana** on http://localhost:3000 (login: admin/admin)
- **Node Exporter** on http://localhost:9100

### 2. Access Grafana

1. Open http://localhost:3000 in your browser
2. Login with username: `admin` and password: `admin`
3. Pre-configured dashboards will be available under "Dashboards" → "TTA" folder

### 3. View Metrics in Prometheus

1. Open http://localhost:9090
2. Try queries like:
   - `up` - Shows which targets are being scraped
   - `node_cpu_seconds_total` - System CPU metrics
   - `node_memory_MemAvailable_bytes` - Available memory

## Available Commands

```bash
./monitoring-dev.sh start      # Start monitoring stack
./monitoring-dev.sh stop       # Stop monitoring stack
./monitoring-dev.sh restart    # Restart monitoring stack
./monitoring-dev.sh logs       # View logs
./monitoring-dev.sh status     # Check service status
./monitoring-dev.sh clean      # Remove all data (WARNING: deletes metrics)
./monitoring-dev.sh help       # Show help
```

## Adding Metrics to Your Application

### Python/FastAPI Example

1. Install the Prometheus client:
```bash
pip install prometheus-client
```

2. Add to your FastAPI app:
```python
from prometheus_client import Counter, Histogram, make_asgi_app
from fastapi import FastAPI

app = FastAPI()

# Metrics
REQUEST_COUNT = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Request duration', ['method', 'endpoint'])

# Add prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/api/example")
async def example():
    REQUEST_COUNT.labels(method='GET', endpoint='/api/example').inc()
    return {"status": "ok"}
```

3. Add your service to `monitoring/prometheus-dev.yml`:
```yaml
  - job_name: "my-service"
    static_configs:
      - targets: ["localhost:8000"]
    metrics_path: "/metrics"
    scrape_interval: 15s
```

4. Reload Prometheus config:
```bash
curl -X POST http://localhost:9090/-/reload
```

## Pre-configured Dashboards

The following dashboards are automatically loaded:

- **TTA System Overview** - Overall system health
- **TTA Story Generation** - Story generation metrics
- **TTA Authentication Monitoring** - Auth system metrics
- **TTA Model Comparison** - AI model performance
- **TTA Simulation Framework** - Simulation metrics
- **TTA Test Execution** - Test run metrics

## Useful Prometheus Queries

### System Metrics
```promql
# CPU Usage
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory Usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk Usage
100 - ((node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100)
```

### Application Metrics (example)
```promql
# Request rate
rate(app_requests_total[5m])

# Average request duration
rate(app_request_duration_seconds_sum[5m]) / rate(app_request_duration_seconds_count[5m])

# Error rate
rate(app_requests_total{status="500"}[5m])
```

## Troubleshooting

### Grafana won't start
- Check logs: `./monitoring-dev.sh logs`
- Common issue: Port 3000 already in use
  - Solution: Stop other services on port 3000 or change port in docker-compose.dev.yml

### Prometheus not scraping targets
1. Check Prometheus targets: http://localhost:9090/targets
2. Verify your service is accessible from the container
3. Check the service exposes metrics at `/metrics`
4. Review Prometheus logs: `docker logs tta-prometheus-dev`

### No metrics showing in Grafana
1. Verify Prometheus datasource is configured (should be automatic)
2. Check Grafana → Configuration → Data Sources
3. Test the connection to Prometheus

## Architecture

```
┌─────────────────┐
│  Your Services  │
│  (with /metrics)│
└────────┬────────┘
         │
         │ scrape
         ↓
    ┌────────────┐
    │ Prometheus │ ← stores time-series data
    │  :9090     │
    └─────┬──────┘
          │
          │ query
          ↓
     ┌────────────┐
     │  Grafana   │ ← visualizes data
     │   :3000    │
     └────────────┘
```

## Configuration Files

- **docker-compose.dev.yml** - Main Docker Compose configuration
- **monitoring/prometheus-dev.yml** - Prometheus scrape configuration
- **monitoring/grafana/datasources/prometheus-dev.yml** - Grafana datasource
- **monitoring/grafana/dashboards/*.json** - Pre-built dashboards
- **monitoring/grafana/grafana.ini** - Grafana server configuration

## Staging Environment

The staging environment has its own monitoring stack running on different ports:
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3003

These are managed separately via `docker-compose.staging.yml`.

## Production Considerations

When deploying to production, consider:

1. **Security**: Change default passwords, enable authentication
2. **Retention**: Adjust data retention periods in Prometheus
3. **Alerting**: Configure AlertManager for notifications
4. **Backup**: Set up regular backups of Grafana dashboards
5. **High Availability**: Consider running multiple Prometheus instances
6. **Storage**: Monitor and manage disk usage for metrics storage

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Node Exporter Metrics](https://github.com/prometheus/node_exporter)

## Next Steps

1. Start the monitoring stack: `./monitoring-dev.sh start`
2. Add metrics to your application
3. Create custom dashboards in Grafana
4. Set up alerts for important metrics
5. Configure log aggregation with Loki (optional, in monitoring/docker-compose.monitoring.yml)
