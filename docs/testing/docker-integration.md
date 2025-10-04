# Docker Integration for TTA Comprehensive Test Battery

This guide covers the Docker container integration for the TTA Comprehensive Test Battery, providing robust testing capabilities with automatic fallback to mock implementations.

## 🐳 Overview

The Docker integration enhances our existing test framework with:

- **Container Detection**: Automatic detection of running Docker containers
- **Health Checking**: Robust multi-stage health checks for Neo4j and Redis
- **Automatic Fallback**: Seamless fallback to mock implementations when containers aren't available
- **Local Development**: Easy container management for development environments
- **CI/CD Integration**: Improved GitHub Actions workflows with reliable container startup

## 🚀 Quick Start

### 1. Start Test Environment

```bash
# Start containers for testing
./scripts/manage-containers.sh start test

# Check container health
./scripts/manage-containers.sh health

# Run tests with container support
python tests/comprehensive_battery/run_comprehensive_tests.py --categories standard
```

### 2. Start Development Environment

```bash
# Start development environment with additional tools
./scripts/manage-containers.sh start dev

# View container status
./scripts/manage-containers.sh status

# Test connections
./scripts/manage-containers.sh test-connection
```

## 📋 Container Management

### Available Commands

```bash
# Container lifecycle
./scripts/manage-containers.sh start [test|dev]    # Start containers
./scripts/manage-containers.sh stop [test|dev]     # Stop containers
./scripts/manage-containers.sh restart [test|dev]  # Restart containers

# Monitoring and debugging
./scripts/manage-containers.sh status              # Show status
./scripts/manage-containers.sh health              # Check health
./scripts/manage-containers.sh logs [service]      # View logs
./scripts/manage-containers.sh shell [service]     # Open shell

# Maintenance
./scripts/manage-containers.sh clean               # Remove containers
./scripts/manage-containers.sh reset               # Reset all data
./scripts/manage-containers.sh test-connection     # Test connectivity
```

### Container Configurations

#### Test Environment (`docker-compose.test.yml`)
- **Neo4j**: Community edition with APOC plugin
- **Redis**: Alpine version with persistence
- **Optimized**: For fast startup and testing

#### Development Environment (`docker-compose.dev.yml`)
- **Neo4j**: Community edition with APOC and GDS plugins
- **Redis**: With custom configuration
- **Tools**: Redis Commander, optional Grafana/Prometheus
- **Persistent**: Data volumes for development continuity

## 🔧 Configuration

### Test Battery Configuration

The comprehensive test battery automatically detects and uses containers when available:

```yaml
# tests/comprehensive_battery/config/comprehensive_test_config.yaml

containers:
  enabled: true                    # Enable container integration
  auto_start: false               # Don't auto-start containers
  health_check_timeout: 30        # Health check timeout (seconds)
  startup_wait_timeout: 120       # Container startup timeout
  fallback_to_mock: true          # Fall back to mocks if containers fail
  
  neo4j:
    container_name: "tta-neo4j-test"
    ports:
      bolt: 7687
      http: 7474
    auth:
      username: "neo4j"
      password: "testpassword"
      
  redis:
    container_name: "tta-redis-test"
    ports:
      redis: 6379
```

### Service Detection Hierarchy

The enhanced service manager follows this detection order:

1. **Direct Connection**: Try connecting to specified URI
2. **Container Detection**: Check for running Docker containers
3. **Mock Fallback**: Use mock implementations if containers unavailable

## 🏥 Health Checking

### Multi-Stage Health Checks

#### Neo4j Health Checking
1. **HTTP Endpoint**: Check `http://localhost:7474/db/data/`
2. **Bolt Connection**: Verify Bolt protocol connectivity
3. **Query Execution**: Run test query to ensure database is ready

#### Redis Health Checking
1. **TCP Connection**: Verify port accessibility
2. **PING Command**: Execute Redis PING
3. **Read/Write Test**: Perform basic operations

### Health Check Configuration

```python
# Custom health check timeouts
health_checker = ContainerHealthChecker(
    max_retries=5,
    base_timeout=2.0
)

# Wait for service with exponential backoff
result = await health_checker.wait_for_service_health(
    service_name="neo4j",
    check_func=lambda: health_checker.check_neo4j_health(uri),
    max_wait_time=120.0,
    check_interval=2.0
)
```

## 🔄 Integration Examples

### Basic Usage

```python
from tests.comprehensive_battery.containers.enhanced_service_manager import EnhancedServiceManager

# Initialize with container support
service_manager = EnhancedServiceManager(force_mock=False)

# Initialize services (containers + fallback)
services = await service_manager.initialize_services(
    neo4j_uri="bolt://localhost:7687",
    redis_url="redis://localhost:6379"
)

# Get service connections (real or mock)
neo4j_driver = await service_manager.get_neo4j_driver()
redis_client = await service_manager.get_redis_client()

# Check service status
status = service_manager.get_service_status()
print(f"Neo4j: {status['neo4j']['backend']} ({status['neo4j']['status']})")
print(f"Redis: {status['redis']['backend']} ({status['redis']['status']})")
```

### Force Mock Mode

```python
# Force mock mode (ignore containers)
service_manager = EnhancedServiceManager(force_mock=True)
services = await service_manager.initialize_services()

# All services will use mock implementations
```

### Container-Only Mode

```python
# Fail if containers aren't available
service_manager = EnhancedServiceManager(force_mock=False)
services = await service_manager.initialize_services()

# Check if any service fell back to mock
for name, status in services.items():
    if status.backend == ServiceBackend.MOCK:
        raise RuntimeError(f"{name} service not available in container mode")
```

## 🚀 CI/CD Integration

### GitHub Actions Improvements

The updated workflows include:

1. **Enhanced Health Checks**: More robust container health checking
2. **Extended Timeouts**: Longer startup periods for Neo4j
3. **Better Error Handling**: Detailed logging and fallback behavior
4. **Service Verification**: Pre-test connectivity validation

### Workflow Configuration

```yaml
services:
  neo4j:
    image: neo4j:5-community
    env:
      NEO4J_AUTH: neo4j/testpassword
      NEO4J_dbms_memory_heap_initial__size: 512m
      NEO4J_dbms_memory_heap_max__size: 1G
    options: >-
      --health-cmd "wget --no-verbose --tries=1 --spider http://localhost:7474/db/data/ || exit 1"
      --health-interval 15s
      --health-timeout 15s
      --health-retries 8
      --health-start-period 60s
```

## 🛠️ Troubleshooting

### Common Issues

#### Container Startup Failures
```bash
# Check Docker daemon
docker info

# View container logs
./scripts/manage-containers.sh logs neo4j

# Check container health
docker inspect tta-neo4j-test --format='{{.State.Health.Status}}'
```

#### Connection Issues
```bash
# Test port accessibility
telnet localhost 7687
telnet localhost 6379

# Test HTTP endpoints
curl http://localhost:7474/db/data/

# Run connectivity test
./scripts/manage-containers.sh test-connection
```

#### Memory Issues
```bash
# Check container resource usage
docker stats tta-neo4j-test tta-redis-test

# Increase container memory limits in docker-compose files
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.getLogger('tests.comprehensive_battery.containers').setLevel(logging.DEBUG)
```

## 🔒 Security Considerations

### Container Security
- Use specific image versions (avoid `latest`)
- Configure resource limits
- Use non-root users where possible
- Regularly update base images

### Network Security
- Containers use bridge networking
- Services only exposed on localhost
- No external network access required

### Data Security
- Test data is ephemeral by default
- Development volumes are local only
- No sensitive data in container images

## 📊 Performance Optimization

### Container Resource Limits

```yaml
# docker-compose.yml
services:
  neo4j:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
```

### Health Check Optimization

- Use HTTP health checks for faster response
- Configure appropriate timeouts and retries
- Implement exponential backoff for startup waits

## 🔄 Migration Guide

### From Mock-Only to Container-Enabled

1. **Install Docker**: Ensure Docker is installed and running
2. **Update Configuration**: Enable container support in config
3. **Start Containers**: Use management scripts to start services
4. **Run Tests**: Execute tests normally - automatic detection handles the rest

### Gradual Adoption

- Start with development environment containers
- Test locally before enabling in CI/CD
- Use force mock mode as fallback during transition
- Monitor container resource usage and adjust limits

## 📈 Monitoring and Metrics

### Container Health Monitoring

```python
# Get detailed service status
status = service_manager.get_service_status()
for name, info in status.items():
    print(f"{name}:")
    print(f"  Backend: {info['backend']}")
    print(f"  Status: {info['status']}")
    print(f"  URI: {info['uri']}")
    if info['container_id']:
        print(f"  Container: {info['container_id']}")
```

### Performance Metrics

- Container startup time
- Health check response time
- Service connection latency
- Resource utilization

The Docker integration provides a robust, production-ready testing environment while maintaining the flexibility and reliability of our existing mock fallback system.
