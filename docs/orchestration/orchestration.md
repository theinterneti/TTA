# Docker Orchestration Guide

This guide explains how to use the orchestration script to manage the TTA Docker containers.

## Table of Contents

- [Overview](#overview)
- [Basic Commands](#basic-commands)
- [Environment Options](#environment-options)
- [Advanced Usage](#advanced-usage)
- [Customizing the Orchestration](#customizing-the-orchestration)

## Overview

The TTA project uses a custom orchestration script (`scripts/orchestrate.sh`) to manage Docker containers. This script provides a simplified interface for starting, stopping, and managing containers across different environments.

## Basic Commands

### Starting Containers

To start the containers:

```bash
./scripts/orchestrate.sh start [environment]
```

Where `[environment]` can be:
- `dev` - Development environment (default)
- `prod` - Production environment
- `jupyter` - Development environment with Jupyter notebook

Examples:
```bash
./scripts/orchestrate.sh start dev       # Start development environment
./scripts/orchestrate.sh start prod      # Start production environment
./scripts/orchestrate.sh start jupyter   # Start with Jupyter notebook
```

### Stopping Containers

To stop all containers:

```bash
./scripts/orchestrate.sh stop
```

### Checking Container Status

To check the status of all containers:

```bash
./scripts/orchestrate.sh status
```

### Viewing Container Logs

To view logs for a specific container:

```bash
./scripts/orchestrate.sh logs [container-name] [lines]
```

Examples:
```bash
./scripts/orchestrate.sh logs app        # View logs for app container
./scripts/orchestrate.sh logs neo4j 100  # View last 100 lines of neo4j logs
```

### Executing Commands in Containers

To execute a command in a container:

```bash
./scripts/orchestrate.sh exec [container-name] [command]
```

Examples:
```bash
./scripts/orchestrate.sh exec app bash   # Start a bash shell in app container
./scripts/orchestrate.sh exec app python # Start Python in app container
```

### Building Containers

To build the containers:

```bash
./scripts/orchestrate.sh build [environment]
```

Examples:
```bash
./scripts/orchestrate.sh build dev       # Build development environment
./scripts/orchestrate.sh build prod      # Build production environment
```

## Environment Options

The orchestration script supports different environments:

### Development Environment

The development environment includes:
- Development tools (black, isort, mypy, pytest)
- Hot-reloading for code changes
- Debugging support
- CodeCarbon tracking in debug mode

```bash
./scripts/orchestrate.sh start dev
```

### Production Environment

The production environment includes:
- Optimized performance settings
- Reduced container size
- Proper resource limits
- Read-only file system for security

```bash
./scripts/orchestrate.sh start prod
```

### Jupyter Environment

The Jupyter environment includes:
- Jupyter notebook server
- Development tools
- CodeCarbon tracking

```bash
./scripts/orchestrate.sh start jupyter
```

## Advanced Usage

### Using Multiple Compose Files

The orchestration script uses multiple Docker Compose files to configure different environments. You can also use Docker Compose directly:

```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Start production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Start with Jupyter notebook
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile with-jupyter up -d
```

### Volume Sharing

The orchestration script ensures proper volume sharing between containers. You can run this step manually:

```bash
./scripts/ensure_volume_sharing.sh
```

## Customizing the Orchestration

You can customize the orchestration script by editing `scripts/orchestrate.sh`. Common customizations include:

### Adding New Environments

To add a new environment:

1. Create a new Docker Compose file (e.g., `docker-compose.custom.yml`)
2. Add a new case in the `start_containers` function:

```bash
custom)
    echo "Starting custom environment..."
    compose_files="$compose_files -f docker-compose.custom.yml"
    ;;
```

### Adding New Commands

To add a new command:

1. Create a new function in the script
2. Add a new case in the command switch:

```bash
custom_command)
    custom_function $@
    ;;
```

For more information about Docker and devcontainer setup, see the [Docker Setup Guide](README.md).


---
**Logseq:** [[TTA.dev/Docs/Orchestration/Orchestration]]
