# TTA Monitoring Infrastructure

This directory contains the complete monitoring setup for the TTA (Turn-Taking Agent) storytelling application, including Prometheus, Grafana, and alerting configurations.

## Quick Start

### 1. Start Monitoring Stack

```bash
# Start all monitoring services
cd monitoring
docker-compose up -d

# Check service status
docker-compose ps
```

### 2. Access Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### 3. Start TTA Application

```bash
# From project root
python -m src.player_experience.api.app
```

The application will automatically detect the monitoring infrastructure and configure itself accordingly.

## Architecture

### Components

1. **Prometheus** (Port 9090)
   - Metrics collection and storage
   - Scrapes TTA application endpoints
   - Evaluates alerting rules

2. **Grafana** (Port 3000)
   - Visualization dashboards
   - Pre-configured TTA dashboards
   - Real-time monitoring views

3. **Alertmanager** (Port 9093)
   - Alert routing and notifications
   - Webhook integration with TTA
   - Email notifications for critical alerts

4. **Node Exporter** (Port 9100)
   - System-level metrics
   - CPU, memory, disk, network stats

### TTA Application Integration

The TTA application includes:

- **Automatic Environment Detection**: Detects if monitoring infrastructure is available
- **Mock Fallback**: Uses mock monitoring when Prometheus/Grafana unavailable
- **Metrics Middleware**: Automatic HTTP request metrics collection
- **Real-time Alerts**: Integration with dashboard system
- **Performance Regression Detection**: CI/CD pipeline integration

## Configuration Files

### Core Configuration

- `prometheus.yml` - Prometheus configuration with TTA scrape targets
- `alertmanager.yml` - Alert routing and notification configuration
- `docker-compose.yml` - Complete monitoring stack definition

### Grafana Dashboards

- `grafana/dashboards/tta-system-overview.json` - System health overview
- `grafana/dashboards/tta-story-generation.json` - Story generation metrics
- `grafana/dashboards/tta-model-comparison.json` - Model performance comparison
- `grafana/dashboards/tta-test-execution.json` - Test execution monitoring
- `grafana/dashboards/tta-authentication-monitoring.json` - Authentication & player profile monitoring (NEW)

### Alert Rules

- `rules/tta-alerts.yml` - TTA-specific alerting rules
  - High CPU/memory usage
  - HTTP error rates
  - Story generation failures
  - Model response times

## Environment Detection and Fallback

The TTA application automatically detects the monitoring environment:

### Full Monitoring Mode
When Prometheus and Grafana are available:
- Full metrics collection
- Real-time dashboards
- Alerting system active
- Performance monitoring

### Mock Monitoring Mode
When monitoring infrastructure is unavailable:
- Mock metrics generation
- Simulated alerts for testing
- Graceful degradation
- Development-friendly fallback

### Environment Variables

```bash
# Force mock monitoring (for testing)
export TTA_FORCE_MOCK_MONITORING=true

# Disable monitoring entirely
export TTA_DISABLE_MONITORING=true

# Custom Prometheus URL
export TTA_PROMETHEUS_URL=http://custom-prometheus:9090
```

## Development Workflow

### Local Development

1. **With Full Monitoring**:
   ```bash
   docker-compose up -d
   python -m src.player_experience.api.app
   ```

2. **Mock Mode Only**:
   ```bash
   export TTA_FORCE_MOCK_MONITORING=true
   python -m src.player_experience.api.app
   ```

### Testing

The monitoring system includes comprehensive testing:

```bash
# Run monitoring tests
pytest tests/monitoring/

# Performance regression detection
python scripts/performance_regression_check.py --test-results ./test-results

# Generate monitoring report
python scripts/generate_monitoring_report.py --test-results ./test-results --output report.html
```

### CI/CD Integration

The GitHub Actions workflow includes:

- Monitoring infrastructure validation
- Performance regression detection
- Test result integration
- Automated reporting

## Metrics Reference

### HTTP Metrics
- `tta_http_requests_total` - Total HTTP requests
- `tta_http_request_duration_seconds` - Request duration histogram
- `tta_http_requests_in_progress` - Active requests

### System Metrics
- `tta_system_cpu_usage_percent` - CPU usage
- `tta_system_memory_usage_percent` - Memory usage
- `tta_system_disk_usage_percent` - Disk usage

### Application Metrics
- `tta_story_generation_requests_total` - Story generation requests
- `tta_story_generation_duration_seconds` - Generation time
- `tta_model_response_time_seconds` - Model response times
- `tta_user_interactions_total` - User interaction counts

### Authentication & Player Profile Metrics (NEW)
- `tta_jwt_token_generation_total` - JWT token generation attempts (success/failure)
- `tta_jwt_token_generation_duration_seconds` - JWT token generation latency
- `tta_jwt_token_verification_total` - JWT token verification attempts
- `tta_player_id_field_presence_total` - Player ID field presence tracking
- `tta_player_id_presence_rate_percent` - Player ID presence rate by endpoint
- `tta_player_profile_autocreation_total` - Player profile auto-creation attempts
- `tta_player_profile_autocreation_duration_seconds` - Profile creation latency
- `tta_player_profile_autocreation_errors_total` - Profile creation errors by category

See [AUTHENTICATION_METRICS.md](./AUTHENTICATION_METRICS.md) for detailed documentation.

### Test Metrics
- `tta_test_execution_total` - Test executions
- `tta_test_duration_seconds` - Test duration
- `tta_test_coverage_percent` - Test coverage

## Troubleshooting

### Common Issues

1. **Prometheus not scraping TTA metrics**:
   - Check TTA application is running on expected port
   - Verify `/metrics` endpoint is accessible
   - Check Prometheus logs: `docker-compose logs prometheus`

2. **Grafana dashboards not loading**:
   - Verify Prometheus datasource configuration
   - Check dashboard provisioning: `docker-compose logs grafana`
   - Ensure dashboard files are in correct location

3. **Alerts not firing**:
   - Check alert rule syntax in `rules/tta-alerts.yml`
   - Verify Alertmanager configuration
   - Test webhook endpoints

4. **Mock mode not working**:
   - Check Python dependencies
   - Verify environment detection logic
   - Enable debug logging

### Logs and Debugging

```bash
# View all monitoring logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f alertmanager

# TTA application logs (with monitoring debug)
export TTA_LOG_LEVEL=DEBUG
python -m src.player_experience.api.app
```

## Customization

### Adding Custom Metrics

1. **In Application Code**:
   ```python
   from src.monitoring.prometheus_metrics import get_metrics_collector

   collector = get_metrics_collector("my-service")
   collector.record_custom_metric("my_metric", 42.0, {"label": "value"})
   ```

2. **Add to Prometheus Config**:
   ```yaml
   - job_name: 'my-service'
     static_configs:
       - targets: ['localhost:8001']
   ```

3. **Create Grafana Dashboard**:
   - Use existing dashboards as templates
   - Add to `grafana/dashboards/` directory

### Custom Alert Rules

Add to `rules/tta-alerts.yml`:

```yaml
- alert: MyCustomAlert
  expr: my_metric > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Custom alert triggered"
    description: "My metric is {{ $value }}"
```

## Production Deployment

### Security Considerations

1. **Change Default Passwords**:
   - Grafana admin password
   - Database passwords
   - SMTP credentials

2. **Network Security**:
   - Use proper firewall rules
   - Consider VPN for external access
   - Enable HTTPS/TLS

3. **Data Retention**:
   - Configure appropriate retention policies
   - Set up backup procedures
   - Monitor disk usage

### Scaling

1. **Prometheus**:
   - Configure federation for multiple instances
   - Use remote storage for long-term retention
   - Implement sharding for high-volume metrics

2. **Grafana**:
   - Use external database for HA
   - Configure load balancing
   - Set up LDAP/OAuth integration

3. **Alertmanager**:
   - Configure clustering
   - Set up redundant notification channels
   - Implement escalation policies

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review application logs with debug logging enabled
3. Consult Prometheus/Grafana documentation
4. File issues in the project repository
