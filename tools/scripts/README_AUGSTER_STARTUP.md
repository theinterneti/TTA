# The Augster Startup Script

A comprehensive BASH startup script for The Augster AI assistant that automates the initialization and setup of the TTA (Therapeutic Text Adventure) development environment.

## Overview

The `augster_startup.sh` script provides a complete, automated solution for setting up the TTA development environment, including:

- **Environment Setup**: Virtual environment activation and dependency verification
- **Service Management**: Redis, Neo4j, and FastAPI application orchestration
- **Health Verification**: Database connections and therapeutic systems validation
- **Testing Framework**: pytest configuration and Testcontainers setup
- **Monitoring & Diagnostics**: Development monitoring and metrics endpoints
- **Project Status**: Git information, service health, and next steps guidance

## Features

### 🚀 **Multiple Startup Modes**
- **Development**: Full development environment with all services
- **Testing**: Optimized for testing with Testcontainers integration
- **Production-Ready**: Production-like configuration with monitoring

### 🔧 **Comprehensive Environment Setup**
- Automatic uv virtual environment management
- Dependency installation and verification
- Environment file validation and creation assistance
- System requirements checking

### 🐳 **Intelligent Service Management**
- Docker Compose service orchestration
- Service health monitoring with retry logic
- Graceful startup ordering and dependency handling
- Port conflict detection and resolution

### 🏥 **Health Verification**
- Database connection testing (Redis, Neo4j)
- FastAPI service health checks
- Therapeutic systems validation
- Performance benchmark verification

### 📊 **Monitoring & Diagnostics**
- Configurable diagnostics server
- Prometheus metrics endpoint setup
- Comprehensive logging configuration
- Agent orchestration monitoring

### 📋 **Project Status Dashboard**
- Git branch and commit information
- Service health status display
- Next steps guidance
- Available commands reference

## Usage

### Basic Usage

```bash
# Start in development mode (default)
./scripts/augster_startup.sh

# Show help
./scripts/augster_startup.sh --help

# Dry run to see what would be done
./scripts/augster_startup.sh --dry-run
```

### Startup Modes

```bash
# Development mode with all services
./scripts/augster_startup.sh --mode development

# Testing mode optimized for Testcontainers
./scripts/augster_startup.sh --mode testing

# Production-ready mode with monitoring
./scripts/augster_startup.sh --mode production-ready
```

### Advanced Options

```bash
# Verbose output with debug logging
./scripts/augster_startup.sh --verbose

# Skip specific components
./scripts/augster_startup.sh --skip-services --skip-health

# Force restart existing services
./scripts/augster_startup.sh --force-restart

# Custom log level
./scripts/augster_startup.sh --log-level DEBUG
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `-m, --mode MODE` | Startup mode: development, testing, production-ready |
| `-v, --verbose` | Enable verbose output and debug logging |
| `-n, --dry-run` | Show what would be done without executing |
| `-s, --skip-services` | Skip service startup (Redis, Neo4j, FastAPI) |
| `-c, --skip-health` | Skip health checks and verification |
| `-o, --skip-monitoring` | Skip monitoring and diagnostics setup |
| `-f, --force-restart` | Force restart of existing services |
| `-l, --log-level LEVEL` | Set log level: DEBUG, INFO, WARNING, ERROR |
| `-h, --help` | Show help message |

## Services Managed

### Core Services
- **Redis** (port 6379): Agent registry and caching
- **Neo4j** (ports 7474, 7687): Therapeutic data storage
- **FastAPI Applications**: Player Experience, Agent Orchestration, API Gateway

### Development Services
- **Diagnostics Server** (port 8081): Development monitoring
- **Prometheus Metrics**: Performance monitoring endpoints

## Prerequisites

### Required Tools
- Python 3.11+
- Git
- curl
- uv (automatically installed if missing)

### Optional Tools (for service management)
- Docker
- Docker Compose

### System Requirements
- Linux or macOS
- 2GB+ available memory (recommended)
- Available disk space for services and logs

## Environment Configuration

The script validates and helps create necessary environment files:

- `.env` (root level)
- `src/player_experience/api/.env`
- `tta.prod/.env`

Example files (`.env.example`) are automatically detected and can be copied to create missing configuration files.

## Integration with Existing Workflow

The script builds upon and integrates with existing TTA infrastructure:

- **Extends** `setup_dev_environment.sh` patterns
- **Leverages** existing Docker Compose configurations
- **Integrates** with pytest markers (@redis, @neo4j)
- **Utilizes** existing health check methods
- **Maintains** compatibility with current development workflow

## Error Handling

The script provides robust error handling:

- **Graceful Degradation**: Continues with available services if some fail
- **Retry Logic**: Exponential backoff for service connections
- **Clear Error Messages**: Informative output for troubleshooting
- **Recovery Suggestions**: Actionable next steps for common issues

## Output and Logging

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **SUCCESS**: Successful operations
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures
- **CRITICAL**: System-level failures

### Color-Coded Output
- 🔵 **Blue**: Informational messages
- 🟢 **Green**: Success messages
- 🟡 **Yellow**: Warnings
- 🔴 **Red**: Errors
- 🟣 **Purple**: Critical issues

## Examples

### Complete Development Setup
```bash
./scripts/augster_startup.sh --mode development --verbose
```

### Testing Environment
```bash
./scripts/augster_startup.sh --mode testing --skip-monitoring
```

### Quick Environment Check
```bash
./scripts/augster_startup.sh --dry-run --verbose
```

### Production-Ready Setup
```bash
./scripts/augster_startup.sh --mode production-ready --force-restart
```

## Troubleshooting

### Common Issues

1. **Docker Permission Issues**
   - Ensure Docker is running
   - Add user to docker group: `sudo usermod -aG docker $USER`
   - Restart terminal session

2. **Port Conflicts**
   - Use `--force-restart` to stop conflicting services
   - Check running services: `docker ps`
   - Manually stop services: `docker-compose down`

3. **Missing Dependencies**
   - Script will attempt to install uv automatically
   - Ensure Python 3.11+ is installed
   - Check system package manager for missing tools

4. **Environment File Issues**
   - Script offers to copy example files
   - Review and update configuration values
   - Ensure sensitive credentials are properly set

## Contributing

When modifying the script:

1. Maintain modular function structure
2. Add appropriate error handling
3. Update help text and documentation
4. Test all startup modes and options
5. Ensure backward compatibility

## Support

For issues or questions:
1. Run with `--verbose` for detailed output
2. Check the project status display
3. Review logs in the `logs/` directory
4. Consult the main TTA documentation

---

**The Augster Startup Script v1.0.0**  
*Comprehensive TTA Development Environment Automation*
