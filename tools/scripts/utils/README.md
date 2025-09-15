# TTA Utility Scripts

This directory contains utility scripts for the TTA project.

## Scripts

- **orchestrate.sh**: Script for orchestrating Docker containers
- **ensure_volume_sharing.sh**: Script for ensuring volume sharing between containers
- **rebuild_devcontainer.sh**: Script for rebuilding the devcontainer

## Usage

### Docker Orchestration

The orchestration script provides a convenient way to manage Docker containers:

```bash
# Start development environment
./scripts/utils/orchestrate.sh start dev

# Start production environment
./scripts/utils/orchestrate.sh start prod

# Start with Jupyter notebook
./scripts/utils/orchestrate.sh start jupyter

# Check container status
./scripts/utils/orchestrate.sh status

# View logs for app container
./scripts/utils/orchestrate.sh logs app

# Run bash in app container
./scripts/utils/orchestrate.sh exec app bash

# Build containers
./scripts/utils/orchestrate.sh build

# Stop all containers
./scripts/utils/orchestrate.sh stop
```

### Volume Sharing

The volume sharing script ensures proper volume sharing between containers:

```bash
./scripts/utils/ensure_volume_sharing.sh
```

### Devcontainer Rebuild

The devcontainer rebuild script rebuilds the devcontainer:

```bash
./scripts/utils/rebuild_devcontainer.sh
```

## Related Documentation

For more information on Docker orchestration and utilities in the TTA project, see:

- [Docker Orchestration](../../Documentation/deployment/orchestration/docker-orchestration.md)
- [Docker Configuration](../../Documentation/setup/docker/README.md)
- [Development Environment](../../Documentation/development/README.md)
