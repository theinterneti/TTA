# TTA Docker Scripts

This directory contains scripts for managing Docker configurations across the TTA repositories.

## Scripts

### ensure_docker_consistency.sh

This script ensures Docker and DevContainer configurations are consistent across repositories. It:

- Checks if Docker files exist in both repositories
- Copies template files if needed
- Standardizes container names
- Ensures consistent VS Code extensions
- Ensures consistent environment variables
- Ensures consistent Docker Compose services

Usage:
```bash
./scripts/docker/ensure_docker_consistency.sh
```

## Orchestration

For orchestrating Docker containers across repositories, use the main orchestration script:

```bash
# Start all containers in development mode
./scripts/utils/orchestrate.sh start all dev

# Start tta.dev containers in production mode
./scripts/utils/orchestrate.sh start dev prod

# Start tta.prototype containers with Jupyter notebook
./scripts/utils/orchestrate.sh start prototype jupyter

# Check container status
./scripts/utils/orchestrate.sh status

# View container logs
./scripts/utils/orchestrate.sh logs dev app

# Execute command in container
./scripts/utils/orchestrate.sh exec prototype app bash

# Stop all containers
./scripts/utils/orchestrate.sh stop all

# Restart all containers
./scripts/utils/orchestrate.sh restart all

# Build all containers
./scripts/utils/orchestrate.sh build all
```

## Docker Configuration Files

The Docker configuration files are located in the respective repositories:

- `tta.dev/Dockerfile`: Dockerfile for the tta.dev repository
- `tta.dev/docker-compose.yml`: Docker Compose file for the tta.dev repository
- `tta.dev/.devcontainer/devcontainer.json`: DevContainer configuration for the tta.dev repository
- `tta.prototype/Dockerfile`: Dockerfile for the tta.prototype repository
- `tta.prototype/docker-compose.yml`: Docker Compose file for the tta.prototype repository
- `tta.prototype/.devcontainer/devcontainer.json`: DevContainer configuration for the tta.prototype repository

## Templates

Template files are located in the `templates` directory:

- `templates/tta.dev/`: Templates for the tta.dev repository
- `templates/tta.prototype/`: Templates for the tta.prototype repository
