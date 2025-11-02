# Docker and Devcontainer Setup

This document provides an overview of the Docker and devcontainer setup for the TTA project.

## Table of Contents

- [Overview](#overview)
- [Docker Structure](#docker-structure)
- [Environment Configurations](#environment-configurations)
- [CodeCarbon Integration](#codecarbon-integration)
- [Troubleshooting](#troubleshooting)

## Overview

The TTA project uses Docker and VS Code devcontainers to provide a consistent development environment across all repositories. The setup includes:

- Multi-stage Docker builds for different environments (development, production)
- Docker Compose for orchestrating multiple containers
- VS Code devcontainer integration for seamless development
- CodeCarbon integration for tracking energy usage and CO2 emissions

## Docker Structure

The Docker setup is organized as follows:

```
TTA/
├── docker-compose.yml         # Base configuration
├── docker-compose.dev.yml     # Development environment
├── docker-compose.prod.yml    # Production environment
├── Dockerfile                 # Multi-stage container definition
├── .devcontainer/             # VS Code integration
├── config/docker/             # Shared Docker configurations
│   ├── compose/               # Base compose files
│   └── dockerfiles/           # Specialized Dockerfiles
├── tta.dev/                   # AI development submodule
│   ├── docker-compose.yml     # ML-specific configuration
│   └── .devcontainer/         # ML development container
└── TTA.prototype/            # Content submodule
    ├── docker-compose.yml     # Content-specific configuration
    └── .devcontainer/         # Content development container
```

## Environment Configurations

### Development Environment

The development environment is configured in `docker-compose.dev.yml` and includes:

- Development tools (black, isort, mypy, pytest)
- Jupyter notebook support
- Hot-reloading for code changes
- CodeCarbon tracking for energy usage

To start the development environment:

```bash
./scripts/orchestrate.sh start dev
```

### Production Environment

The production environment is configured in `docker-compose.prod.yml` and includes:

- Optimized for performance
- Reduced container size
- Proper resource limits
- Read-only file system for security

To start the production environment:

```bash
./scripts/orchestrate.sh start prod
```

## CodeCarbon Integration

The project includes [CodeCarbon](https://codecarbon.io/) for tracking energy usage and CO2 emissions during development and production.

### Configuration

CodeCarbon is configured with the following settings:

- Project name: TTA
- Measurement interval: 15 seconds
- Log level: DEBUG (development) / INFO (production)
- Output directory: /app/logs/codecarbon

### Usage

```python
from codecarbon import EmissionsTracker

# Track emissions for a specific function
tracker = EmissionsTracker(project_name="TTA")
tracker.start()
# Your code here
emissions = tracker.stop()
print(f"Emissions: {emissions} kg CO2eq")

# Or use as a decorator
from codecarbon import track_emissions

@track_emissions(project_name="TTA")
def my_function():
    # Your code here
    pass
```

## Troubleshooting

### Neo4j Health Check Issues

If the Neo4j container is marked as "unhealthy", check the following:

1. Make sure the Neo4j container has access to port 7474
2. Verify that the health check command is using the correct syntax
3. Check the Neo4j logs for any errors

Current health check configuration:

```yaml
healthcheck:
  test: ["CMD-SHELL", "wget --quiet --spider http://localhost:7474 || exit 1"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

### Container Startup Issues

If containers fail to start, try the following:

1. Check the logs: `./scripts/orchestrate.sh logs <container-name>`
2. Restart the containers: `./scripts/orchestrate.sh restart`
3. Rebuild the containers: `./scripts/orchestrate.sh build`

For more detailed troubleshooting, see the [Devcontainer Troubleshooting Guide](../devcontainer/troubleshooting.md).
