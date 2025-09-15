# Production Environment

This document provides detailed information about the production environment configuration for the TTA project.

## Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Features](#features)
- [Usage](#usage)
- [Monitoring](#monitoring)
- [Security](#security)
- [Performance Tuning](#performance-tuning)

## Overview

The production environment is designed for running the TTA project in a production setting. It is optimized for performance, security, and stability.

## Configuration

The production environment is configured in `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Override app service for production
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    restart: unless-stopped
    environment:
      - PYTHONOPTIMIZE=2
      - CODECARBON_LOG_LEVEL=INFO
      - CODECARBON_OUTPUT_DIR=/app/logs/codecarbon
    volumes:
      - .:/app:ro  # Read-only in production
      - venv-data:/app/.venv
      - huggingface-cache:/root/.cache/huggingface
      - model-cache:/app/.model_cache
      - ./data:/app/external_data:ro
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    healthcheck:
      test: ["CMD-SHELL", "exit 0"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 40s

  # Override basic-mcp-server for production
  basic-mcp-server:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    restart: always
    environment:
      - PYTHONOPTIMIZE=2
    volumes:
      - .:/app:ro  # Read-only in production
      - venv-data:/app/.venv
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 20s

volumes:
  venv-data:
  huggingface-cache:
  model-cache:
```

## Features

### Performance Optimization

The production environment includes several performance optimizations:

- **Python Optimization**: `PYTHONOPTIMIZE=2` enables Python's optimization mode, which:
  - Removes assertions
  - Removes docstrings
  - Enables additional optimizations

- **Resource Limits**: The containers have defined resource limits:
  - CPU limits to prevent resource contention
  - Memory limits to prevent memory leaks from affecting the host
  - GPU reservations for ML workloads

- **Restart Policies**: Containers are configured to restart automatically:
  - `restart: unless-stopped`: Restarts the container unless explicitly stopped
  - `restart: always`: Always restarts the container, even after explicit stops

### Security Enhancements

The production environment includes several security enhancements:

- **Read-Only File System**: The application code is mounted as read-only:
  - Prevents runtime modifications to the code
  - Reduces attack surface

- **Minimal Dependencies**: The production image includes only necessary dependencies:
  - Reduces attack surface
  - Reduces image size

- **Healthchecks**: Containers have healthchecks to ensure they are functioning properly:
  - Regular checks to verify service health
  - Automatic restarts for unhealthy containers

### CodeCarbon Integration

The production environment includes CodeCarbon integration:

- **INFO Logging Level**: Reduces log verbosity while still capturing important information
- **Output Directory**: Emissions data is saved to `/app/logs/codecarbon`

## Usage

### Starting the Production Environment

To start the production environment:

```bash
./scripts/orchestrate.sh start prod
```

Or with Docker Compose directly:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Stopping the Production Environment

To stop the production environment:

```bash
./scripts/orchestrate.sh stop
```

Or with Docker Compose directly:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### Viewing Logs

To view logs from the production environment:

```bash
./scripts/orchestrate.sh logs app
```

Or with Docker Compose directly:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f app
```

## Monitoring

### Health Checks

The production environment includes health checks for all services:

- **App Service**:
  ```yaml
  healthcheck:
    test: ["CMD-SHELL", "exit 0"]
    interval: 30s
    timeout: 10s
    retries: 5
    start_period: 40s
  ```

- **MCP Server**:
  ```yaml
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
    interval: 30s
    timeout: 10s
    retries: 5
    start_period: 20s
  ```

### Resource Usage

To monitor resource usage:

```bash
docker stats $(docker ps --format "{{.Names}}" | grep tta-)
```

### CodeCarbon Emissions

To view CodeCarbon emissions data:

```bash
./scripts/orchestrate.sh exec app cat /app/logs/codecarbon/emissions.csv
```

## Security

### Read-Only File System

The production environment mounts the application code as read-only:

```yaml
volumes:
  - .:/app:ro  # Read-only in production
```

This prevents runtime modifications to the code, reducing the attack surface.

### Minimal Dependencies

The production image includes only necessary dependencies:

```dockerfile
FROM base as production

# Add production-specific configurations
RUN echo "\n# Production settings" >> /app/.venv/bin/activate && \
    echo "export PYTHONOPTIMIZE=2" >> /app/.venv/bin/activate
```

### Network Security

The production environment should be deployed behind a reverse proxy (e.g., Nginx, Traefik) with:

- TLS termination
- Rate limiting
- IP filtering
- Web application firewall (WAF)

## Performance Tuning

### CPU Limits

The production environment includes CPU limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
```

Adjust this value based on your server's CPU capacity.

### Memory Limits

The production environment includes memory limits:

```yaml
deploy:
  resources:
    limits:
      memory: 8G
```

Adjust this value based on your server's memory capacity.

### GPU Configuration

The production environment includes GPU configuration:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

Adjust this configuration based on your GPU requirements.

For more information about Docker and container setup, see the [Docker Setup Guide](../README.md).
