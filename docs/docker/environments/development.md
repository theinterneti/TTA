# Development Environment

This document provides detailed information about the development environment configuration for the TTA project.

## Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Features](#features)
- [Usage](#usage)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

## Overview

The development environment is designed for active development of the TTA project. It includes development tools, debugging support, and hot-reloading for code changes.

## Configuration

The development environment is configured in `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  # Override app service for development
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    environment:
      - PYTHONPATH=/app
      - VIRTUAL_ENV=/app/.venv
      - PATH=/app/.venv/bin:$PATH
      - CODECARBON_LOG_LEVEL=DEBUG
      - CODECARBON_OUTPUT_DIR=/app/logs/codecarbon
    volumes:
      - .:/app:delegated
      - venv-data:/app/.venv
      - huggingface-cache:/root/.cache/huggingface
      - model-cache:/app/.model_cache
      - ./data:/app/external_data:delegated
      - ./logs:/app/logs:delegated
      - ./notebooks:/app/notebooks:delegated
      - /var/run/docker.sock:/var/run/docker.sock
    command: python3 -c "import time; print('Development environment running...'); time.sleep(3600)"
    ports:
      - "8888:8888"  # Jupyter notebook
    healthcheck:
      test: ["CMD-SHELL", "exit 0"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  # Development-specific services
  jupyter:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: tta-jupyter
    volumes:
      - .:/app:delegated
      - venv-data:/app/.venv
      - huggingface-cache:/root/.cache/huggingface
      - model-cache:/app/.model_cache
      - ./data:/app/external_data:delegated
      - ./notebooks:/app/notebooks:delegated
    environment:
      - PYTHONPATH=/app
      - VIRTUAL_ENV=/app/.venv
      - PATH=/app/.venv/bin:$PATH
      - CODECARBON_LOG_LEVEL=DEBUG
      - CODECARBON_OUTPUT_DIR=/app/logs/codecarbon
    command: jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
    ports:
      - "8888:8888"
    networks:
      - tta-network
    depends_on:
      app:
        condition: service_healthy
    profiles: ["with-jupyter"]
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8888 || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  venv-data:
  huggingface-cache:
  model-cache:
```

## Features

### Development Tools

The development environment includes:

- **Python Development Tools**:
  - Black code formatter
  - isort import sorter
  - mypy type checker
  - flake8 linter
  - pytest for testing

- **Jupyter Notebook**:
  - Jupyter notebook server
  - ipykernel for Python kernels
  - Jupyter extensions

- **Debugging Support**:
  - VS Code debugger integration
  - Python debugpy

- **CodeCarbon Integration**:
  - Debug logging level
  - Output directory for emissions data

### Volume Mounts

The development environment mounts several volumes:

- `.:/app:delegated`: The project root directory
- `venv-data:/app/.venv`: Python virtual environment
- `huggingface-cache:/root/.cache/huggingface`: Hugging Face model cache
- `model-cache:/app/.model_cache`: Custom model cache
- `./data:/app/external_data:delegated`: Data directory
- `./logs:/app/logs:delegated`: Log directory
- `./notebooks:/app/notebooks:delegated`: Jupyter notebooks
- `/var/run/docker.sock:/var/run/docker.sock`: Docker socket for Docker-in-Docker

### Environment Variables

The development environment sets several environment variables:

- `PYTHONPATH=/app`: Python module search path
- `VIRTUAL_ENV=/app/.venv`: Python virtual environment path
- `PATH=/app/.venv/bin:$PATH`: Path to include virtual environment binaries
- `CODECARBON_LOG_LEVEL=DEBUG`: CodeCarbon logging level
- `CODECARBON_OUTPUT_DIR=/app/logs/codecarbon`: CodeCarbon output directory

## Usage

### Starting the Development Environment

To start the development environment:

```bash
./scripts/orchestrate.sh start dev
```

Or with Docker Compose directly:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Starting with Jupyter Notebook

To start the development environment with Jupyter notebook:

```bash
./scripts/orchestrate.sh start jupyter
```

Or with Docker Compose directly:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile with-jupyter up -d
```

### Accessing the Development Environment

- **VS Code**: Use the Remote - Containers extension to attach to the container
- **Terminal**: Use the orchestration script to execute commands:
  ```bash
  ./scripts/orchestrate.sh exec app bash
  ```
- **Jupyter Notebook**: Access the Jupyter notebook server at http://localhost:8888

## Customization

### Adding Development Tools

To add additional development tools:

1. Edit the Dockerfile to install the tools in the development stage:
   ```dockerfile
   FROM base as development

   RUN /app/.venv/bin/pip install --no-cache-dir \
       your-tool-name
   ```

2. Rebuild the development environment:
   ```bash
   ./scripts/orchestrate.sh build dev
   ```

### Changing Environment Variables

To change environment variables:

1. Edit the `docker-compose.dev.yml` file:
   ```yaml
   services:
     app:
       environment:
         - YOUR_VARIABLE=value
   ```

2. Restart the development environment:
   ```bash
   ./scripts/orchestrate.sh restart dev
   ```

## Troubleshooting

### Common Issues

#### Python Package Not Found

If a Python package is not found:

1. Check if the package is installed:
   ```bash
   ./scripts/orchestrate.sh exec app pip list | grep package-name
   ```

2. Install the package:
   ```bash
   ./scripts/orchestrate.sh exec app pip install package-name
   ```

3. Update the requirements.txt file:
   ```bash
   ./scripts/orchestrate.sh exec app pip freeze > requirements.txt
   ```

#### Volume Mount Issues

If changes to files are not reflected in the container:

1. Check the volume mounts:
   ```bash
   ./scripts/orchestrate.sh exec app ls -la /app
   ```

2. Restart the container:
   ```bash
   ./scripts/orchestrate.sh restart dev
   ```

For more information about Docker and container setup, see the [Docker Setup Guide](../README.md).


---
**Logseq:** [[TTA.dev/Docs/Docker/Environments/Development]]
