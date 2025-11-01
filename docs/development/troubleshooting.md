# Devcontainer Troubleshooting Guide

This guide provides solutions for common issues encountered with the VS Code devcontainer setup.

## Table of Contents

- [Common Issues](#common-issues)
- [Resetting the Devcontainer](#resetting-the-devcontainer)
- [Environment Variables](#environment-variables)
- [Volume Mounting Issues](#volume-mounting-issues)
- [GPU Access Issues](#gpu-access-issues)
- [Getting Help](#getting-help)

## Common Issues

### Container Fails to Start

**Symptoms:**
- VS Code shows "Failed to start container"
- Error message about port conflicts

**Solutions:**
1. Check if another container is using the same ports:
   ```bash
   docker ps
   ```
2. Stop conflicting containers or change the port mapping in `docker-compose.yml`
3. Try restarting Docker:
   ```bash
   sudo systemctl restart docker
   ```

### Python Environment Issues

**Symptoms:**
- "Python interpreter not found"
- Import errors for installed packages

**Solutions:**
1. Verify the Python path in `.devcontainer/devcontainer.json`:
   ```json
   "python.defaultInterpreterPath": "/app/.venv/bin/python"
   ```
2. Rebuild the container to reinstall dependencies:
   ```bash
   ./scripts/orchestrate.sh build dev
   ```
3. Check if the virtual environment is activated:
   ```bash
   echo $VIRTUAL_ENV
   ```

### Neo4j Connection Issues

**Symptoms:**
- Cannot connect to Neo4j database
- Neo4j container is marked as "unhealthy"

**Solutions:**
1. Check if the Neo4j container is running:
   ```bash
   docker ps | grep neo4j
   ```
2. Verify the Neo4j credentials in `.env`:
   ```
   NEO4J_PASSWORD=password
   ```
3. Check the Neo4j logs:
   ```bash
   ./scripts/orchestrate.sh logs neo4j
   ```

## Resetting the Devcontainer

If you encounter persistent issues, you may need to reset the devcontainer:

1. Stop all containers:
   ```bash
   ./scripts/orchestrate.sh stop
   ```

2. Remove the containers and volumes:
   ```bash
   docker-compose down -v
   ```

3. Rebuild the containers:
   ```bash
   ./scripts/orchestrate.sh build
   ```

4. Restart the containers:
   ```bash
   ./scripts/orchestrate.sh start dev
   ```

## Environment Variables

Environment variables are loaded from the `.env` file. If you're experiencing issues with environment variables:

1. Check if the `.env` file exists in the root directory
2. Verify that the variables are correctly formatted
3. Make sure the container has access to the `.env` file

You can check environment variables inside the container with:

```bash
./scripts/orchestrate.sh exec app env
```

## Volume Mounting Issues

**Symptoms:**
- Changes to files are not reflected in the container
- Permission errors when accessing files

**Solutions:**
1. Check the volume mounts in `docker-compose.yml`:
   ```yaml
   volumes:
     - .:/app:delegated
   ```
2. Verify file permissions:
   ```bash
   ls -la
   ```
3. Run the volume sharing script:
   ```bash
   ./scripts/ensure_volume_sharing.sh
   ```

## GPU Access Issues

**Symptoms:**
- CUDA not available in the container
- GPU-accelerated code runs slowly

**Solutions:**
1. Check if NVIDIA drivers are installed on the host:
   ```bash
   nvidia-smi
   ```
2. Verify that the container has access to the GPU:
   ```bash
   ./scripts/orchestrate.sh exec app python -c "import torch; print(torch.cuda.is_available())"
   ```
3. Check the Docker runtime configuration:
   ```bash
   docker info | grep -i runtime
   ```

## Getting Help

If you're still experiencing issues after trying the solutions above:

1. Check the [GitHub Issues](https://github.com/yourusername/TTA/issues) for similar problems
2. Create a new issue with detailed information about the problem
3. Include logs and error messages to help diagnose the issue

For more information about the Docker and devcontainer setup, see the [Docker Setup Guide](../docker/README.md).
