# Neo4j Component

**Status**: Development → Staging Promotion
**Coverage**: 88%
**Version**: 1.0.0
**Owner**: theinterneti

---

## Overview

The Neo4j Component provides graph database management for the TTA (Therapeutic Text Adventure) system. It manages Neo4j database instances across multiple environments (development, staging, production) using Docker Compose, with automated health monitoring, lifecycle management, and multi-repository support.

### Purpose

Neo4j serves as the foundational graph database for the TTA system, providing persistent storage for:
- Narrative state and story progression
- Character relationships and interactions
- World knowledge and lore
- Player choices and consequences
- Therapeutic content connections

### Key Features

- **Docker-Based Deployment**: Automated Neo4j container management via Docker Compose
- **Multi-Environment Support**: Separate instances for `tta.dev` (port 7687) and `tta.prototype` (port 7688)
- **Health Monitoring**: Automated health checks using Docker container status
- **Lifecycle Management**: Start, stop, and status checking with proper error handling
- **Configuration Management**: Flexible configuration via `tta_config.yaml`
- **Connection Pooling**: Efficient database connection management
- **Backup & Restore**: Support for database backup and restore operations

---

## Architecture

### Component Structure

```
src/components/
└── neo4j_component.py          # Main Neo4j component implementation
    ├── Neo4jComponent          # Component class
    ├── _start_impl()           # Start Neo4j container
    ├── _stop_impl()            # Stop Neo4j container
    ├── _is_neo4j_running()     # Health check
    └── _run_docker_compose()   # Docker Compose wrapper
```

### Dependencies

**None** - Neo4j is a foundational component with no dependencies on other TTA components.

### Dependent Components

The following components depend on Neo4j:
- Agent Orchestration
- Narrative Arc Orchestrator
- Gameplay Loop
- Living Worlds
- Knowledge Management

---

## Configuration

### Configuration File

Neo4j is configured via `config/tta_config.yaml`:

```yaml
# Development Environment (tta.dev)
tta.dev:
  enabled: true
  components:
    neo4j:
      enabled: true
      port: 7687
      username: neo4j
      password: your_dev_password

# Prototype Environment (tta.prototype)
tta.prototype:
  enabled: true
  components:
    neo4j:
      enabled: true
      port: 7688
      username: neo4j
      password: your_prototype_password
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable Neo4j component |
| `port` | int | `7687` (dev) / `7688` (prototype) | Bolt protocol port |
| `username` | str | `"neo4j"` | Database username |
| `password` | str | `"password"` | Database password |

---

## Usage Examples

### Basic Usage

```python
from src.orchestration import TTAConfig
from src.components.neo4j_component import Neo4jComponent

# Create configuration
config = TTAConfig()

# Create Neo4j component for development environment
neo4j = Neo4jComponent(config, repository="tta.dev")

# Start Neo4j
if neo4j.start():
    print("Neo4j started successfully")
else:
    print("Failed to start Neo4j")

# Check if Neo4j is running
if neo4j._is_neo4j_running():
    print(f"Neo4j is running on port {neo4j.port}")

# Stop Neo4j
if neo4j.stop():
    print("Neo4j stopped successfully")
```

### Multi-Repository Usage

```python
# Development environment
neo4j_dev = Neo4jComponent(config, repository="tta.dev")
neo4j_dev.start()  # Runs on port 7687

# Prototype environment
neo4j_proto = Neo4jComponent(config, repository="tta.prototype")
neo4j_proto.start()  # Runs on port 7688

# Both instances can run simultaneously
```

### Using with Orchestrator

```python
from src.orchestration import TTAOrchestrator

# Create orchestrator (automatically manages Neo4j)
orchestrator = TTAOrchestrator()

# Start all components (including Neo4j)
orchestrator.start_all()

# Access Neo4j component
neo4j = orchestrator.components["tta.dev_neo4j"]
print(f"Neo4j status: {neo4j.status}")

# Stop all components
orchestrator.stop_all()
```

### Health Checks

```python
# Check if Neo4j is running
if neo4j._is_neo4j_running():
    print("✅ Neo4j is healthy")
else:
    print("❌ Neo4j is down")

# Get component status
from src.orchestration.component import ComponentStatus

if neo4j.status == ComponentStatus.RUNNING:
    print("Component is running")
elif neo4j.status == ComponentStatus.STOPPED:
    print("Component is stopped")
elif neo4j.status == ComponentStatus.ERROR:
    print("Component has errors")
```

---

## Docker Integration

### Docker Compose Configuration

Neo4j uses Docker Compose files located in each repository:
- `tta.dev/docker-compose.yml`
- `tta.prototype/docker-compose.yml`

### Docker Commands

The component executes the following Docker Compose commands:

**Start Neo4j:**
```bash
docker-compose -f /path/to/repo/docker-compose.yml up -d neo4j
```

**Stop Neo4j:**
```bash
docker-compose -f /path/to/repo/docker-compose.yml stop neo4j
```

**Check Status:**
```bash
docker ps --filter publish=7687 --format '{{.Names}}'
```

### Container Management

- **Startup Timeout**: 30 seconds (configurable)
- **Shutdown Timeout**: 10 seconds (configurable)
- **Health Check Method**: Docker container status via port publishing
- **Restart Policy**: Managed by Docker Compose configuration

---

## Multi-Environment Support

### Environment Separation

| Environment | Repository | Port | Purpose |
|-------------|-----------|------|---------|
| Development | `tta.dev` | 7687 | Active development and testing |
| Prototype | `tta.prototype` | 7688 | Prototype features and experiments |
| Production | `tta.prod` | 7689 | Production deployment (future) |

### Port Allocation

Ports are automatically assigned based on repository:
- Development uses standard Neo4j port (7687)
- Prototype uses offset port (7688)
- Production will use (7689)

This allows all environments to run simultaneously without conflicts.

---

## Testing

### Running Tests

```bash
# Run Neo4j component tests
uv run pytest tests/test_neo4j_component.py -v

# Run with coverage
uv run pytest tests/test_neo4j_component.py \
  --cov=src.components.neo4j_component \
  --cov-report=term

# Run specific test class
uv run pytest tests/test_neo4j_component.py::TestNeo4jComponentLifecycle -v
```

### Test Coverage

**Current Coverage**: 88% (exceeds 70% staging requirement)

**Test Categories**:
- Lifecycle Operations (7 tests)
- Health Checks (3 tests)
- Configuration Management (4 tests)
- Docker Integration (3 tests)
- Error Handling (3 tests)

**Total Tests**: 20 tests, all passing

---

## Troubleshooting

### Common Issues

#### Neo4j Won't Start

**Symptoms**: `start()` returns `False`, timeout waiting for Neo4j

**Solutions**:
1. Check Docker is running: `docker ps`
2. Check port availability: `lsof -i :7687`
3. Check Docker Compose file exists: `ls tta.dev/docker-compose.yml`
4. Check logs: `docker-compose -f tta.dev/docker-compose.yml logs neo4j`

#### Port Already in Use

**Symptoms**: Container fails to start, port conflict error

**Solutions**:
1. Check what's using the port: `lsof -i :7687`
2. Stop conflicting service
3. Or use different port in configuration

#### Health Check Fails

**Symptoms**: `_is_neo4j_running()` returns `False` when container is running

**Solutions**:
1. Verify container is publishing port: `docker ps | grep neo4j`
2. Check firewall settings
3. Verify Docker network configuration

#### Permission Denied

**Symptoms**: Docker Compose commands fail with permission errors

**Solutions**:
1. Add user to docker group: `sudo usermod -aG docker $USER`
2. Restart shell session
3. Or use `sudo` (not recommended for production)

---

## Promotion Status

### Development → Staging Criteria

- [x] Core features complete (100%)
- [x] Unit tests passing (88% coverage, exceeds 70% requirement)
- [x] API documented
- [x] Passes security scan (0 issues)
- [x] Passes type checking (0 errors)
- [x] Passes linting (0 errors)
- [x] Component README complete
- [x] All dependencies identified (none)
- [x] Integration validated

**Status**: ✅ **READY FOR STAGING PROMOTION** (9/9 criteria met)

### Next Steps

1. Create promotion request issue
2. Deploy to staging environment
3. Monitor for 7 days (99.5% uptime target)
4. Validate integration with dependent components
5. Prepare for production promotion

---

## Related Documentation

- [Component Maturity Status](./MATURITY.md)
- [Component Promotion Guide](../../docs/development/COMPONENT_PROMOTION_GUIDE.md)
- [TTA Configuration Guide](../../config/README.md)
- [Docker Deployment Guide](../../docs/deployment/docker-deployment.md)

---

**Last Updated**: 2025-10-09
**Maintained By**: theinterneti
**Component Version**: 1.0.0
