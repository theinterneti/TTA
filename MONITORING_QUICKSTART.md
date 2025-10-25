# Prometheus/Grafana Quick Start - Development

## ✅ Setup Complete!

Your monitoring stack is now configured and ready to use.

## 🚀 Quick Commands

```bash
# Start monitoring
./monitoring-dev.sh start

# Check status
./monitoring-dev.sh status

# View logs
./monitoring-dev.sh logs

# Stop monitoring
./monitoring-dev.sh stop
```

## 🌐 Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |
| **Node Exporter** | http://localhost:9100/metrics | - |

## 📊 What's Currently Monitored

✅ **System Metrics** (via Node Exporter)
- CPU usage, load average
- Memory usage
- Disk I/O and usage
- Network traffic

✅ **Prometheus Self-Monitoring**
- Scrape performance
- Storage metrics

🔄 **Ready to Add** (currently down, need metric exporters):
- Redis metrics
- Neo4j metrics
- Your application metrics

## 📈 Quick Prometheus Queries

Try these in Prometheus (http://localhost:9090):

```promql
# See which targets are up
up

# CPU usage percentage
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage percentage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage percentage
100 - ((node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100)

# Network receive rate
rate(node_network_receive_bytes_total[5m])
```

## 🎯 Next Steps

### 1. Add Application Metrics

See `monitoring/DEV_MONITORING_GUIDE.md` for details on:
- Adding Prometheus metrics to Python/FastAPI apps
- Configuring scrape targets
- Creating custom dashboards

### 2. Explore Pre-built Dashboards

In Grafana, go to:
- **Dashboards** → **Browse** → **TTA** folder

**Working Dashboards (with real data):**
- ✅ **System Metrics (Node Exporter)** - CPU, Memory, Disk, Network metrics
- ✅ **Prometheus Monitoring** - Prometheus health and performance

**Application Dashboards (need app metrics):**
- TTA System Overview
- TTA Story Generation
- TTA Authentication Monitoring
- TTA Model Comparison
- TTA Test Execution

### 3. Enable Redis & Neo4j Metrics (Optional)

To monitor Redis:
```bash
# Use redis_exporter
docker run -d --name redis-exporter --network tta-dev-network \
  -p 9121:9121 \
  oliver006/redis_exporter \
  --redis.addr=tta-dev-redis:6379
```

Then add to `monitoring/prometheus-dev.yml`:
```yaml
  - job_name: "redis-exporter"
    static_configs:
      - targets: ["host.docker.internal:9121"]
```

To monitor Neo4j:
```bash
# Enable Prometheus metrics in Neo4j
# Add to docker-compose.dev.yml under neo4j environment:
- NEO4J_metrics_prometheus_enabled=true
- NEO4J_metrics_prometheus_endpoint=0.0.0.0:2004
```

## 📚 Documentation

- **Full Guide**: `monitoring/DEV_MONITORING_GUIDE.md`
- **Configuration**: `docker-compose.dev.yml`
- **Prometheus Config**: `monitoring/prometheus-dev.yml`
- **Grafana Datasource**: `monitoring/grafana/datasources/prometheus-dev.yml`

## 🐛 Troubleshooting

**Grafana not loading?**
- Wait 10-15 seconds for initialization
- Check: `docker logs tta-grafana-dev`

**No metrics showing?**
- Check Prometheus targets: http://localhost:9090/targets
- Verify datasource in Grafana: Settings → Data Sources

**Port conflicts?**
- Prometheus: Port 9090
- Grafana: Port 3000
- Node Exporter: Port 9100

If any port is in use, modify `docker-compose.dev.yml`

## 🔄 Staging Environment

Note: There's a separate staging monitoring stack running on:
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3003

These are independent systems and won't interfere with dev.

---

**Need Help?** See the full guide: `monitoring/DEV_MONITORING_GUIDE.md`
