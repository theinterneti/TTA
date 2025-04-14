# Docker Environment Configurations

This document explains the different Docker environment configurations available in the TTA project.

## Table of Contents

- [Overview](#overview)
- [Development Environment](#development-environment)
- [Production Environment](#production-environment)
- [Jupyter Environment](#jupyter-environment)
- [Custom Environments](#custom-environments)

## Overview

The TTA project uses different Docker Compose files to configure different environments:

- `docker-compose.yml`: Base configuration shared by all environments
- `docker-compose.dev.yml`: Development-specific configuration
- `docker-compose.prod.yml`: Production-specific configuration

These files can be combined to create different environments for different purposes.

## Development Environment

The development environment is configured in `docker-compose.dev.yml` and is designed for active development.

### Features

- Development tools (black, isort, mypy, pytest)
- Hot-reloading for code changes
- Debugging support
- CodeCarbon tracking in debug mode
- Volume mounts for code editing

### Configuration

```yaml
# docker-compose.dev.yml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    volumes:
      - .:/app:delegated
      - venv-data:/app/.venv
    environment:
      - PYTHONPATH=/app
      - CODECARBON_LOG_LEVEL=DEBUG
```

### Usage

To start the development environment:

```bash
./scripts/orchestrate.sh start dev
```

Or with Docker Compose directly:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## Production Environment

The production environment is configured in `docker-compose.prod.yml` and is optimized for performance and security.

### Features

- Optimized for performance
- Reduced container size
- Proper resource limits
- Read-only file system for security
- CodeCarbon tracking in production mode

### Configuration

```yaml
# docker-compose.prod.yml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    volumes:
      - .:/app:ro  # Read-only
    environment:
      - PYTHONOPTIMIZE=2
      - CODECARBON_LOG_LEVEL=INFO
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

### Usage

To start the production environment:

```bash
./scripts/orchestrate.sh start prod
```

Or with Docker Compose directly:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Jupyter Environment

The Jupyter environment includes a Jupyter notebook server for interactive development.

### Features

- Jupyter notebook server
- Development tools
- CodeCarbon tracking
- Volume mounts for notebooks

### Configuration

```yaml
# docker-compose.dev.yml (with jupyter profile)
services:
  jupyter:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    command: jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
    ports:
      - "8888:8888"
    profiles: ["with-jupyter"]
```

### Usage

To start the Jupyter environment:

```bash
./scripts/orchestrate.sh start jupyter
```

Or with Docker Compose directly:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile with-jupyter up -d
```

## Custom Environments

You can create custom environments by combining different Docker Compose files and profiles.

### Creating a Custom Environment

1. Create a new Docker Compose file (e.g., `docker-compose.custom.yml`)
2. Define your custom services and configurations
3. Use Docker Compose to combine the files:

```bash
docker-compose -f docker-compose.yml -f docker-compose.custom.yml up -d
```

### Example: GPU-Optimized Environment

```yaml
# docker-compose.gpu.yml
services:
  app:
    environment:
      - CUDA_VISIBLE_DEVICES=0,1
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 2
              capabilities: [gpu]
```

Usage:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.gpu.yml up -d
```

For more information about Docker and container orchestration, see the [Docker Orchestration Guide](../orchestration.md).
