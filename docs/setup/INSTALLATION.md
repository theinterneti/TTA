# TTA Installation Guide

## Overview

This guide provides step-by-step instructions for installing and setting up the TTA project, including its submodules and dependencies.

## Prerequisites

- **Git**: Version 2.20 or higher
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Python**: Version 3.10 or higher (for local development)
- **CUDA**: Version 11.8 or higher (for GPU support)

## Installation Options

There are three main ways to install and set up the TTA project:

1. **Automated Setup**: Using the provided setup script
2. **Manual Setup**: Step-by-step manual installation
3. **Development Container**: Using VS Code devcontainers

## 1. Automated Setup

The easiest way to set up the TTA project is to use the provided setup script:

```bash
# Clone the repository
git clone --recurse-submodules https://github.com/theinterneti/TTA.git
cd TTA

# Run the setup script
./scripts/setup/setup.sh
```

The setup script will:
- Initialize and update submodules
- Set up Docker environments
- Configure environment variables
- Build and start Docker containers

## 2. Manual Setup

If you prefer to set up the project manually, follow these steps:

### 2.1. Clone the Repository

```bash
# Clone the repository with submodules
git clone --recurse-submodules https://github.com/theinterneti/TTA.git
cd TTA
```

### 2.2. Initialize Submodules

If you didn't use the `--recurse-submodules` flag when cloning, initialize the submodules:

```bash
git submodule update --init --recursive
```

### 2.3. Set Up Environment Variables

Create `.env` files in the appropriate directories:

```bash
# Root .env file
cp .env.example .env

# TTA.prototype .env file
cp TTA.prototype/.env.example TTA.prototype/.env

# TTA.dev .env file
cp tta.dev/.env.example tta.dev/.env
```

Edit the `.env` files as needed for your environment.

### 2.4. Build and Start Docker Containers

```bash
# Build and start the containers
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## 3. Development Container

The TTA project includes configuration for VS Code devcontainers, which provide a consistent development environment:

### 3.1. Prerequisites

- **VS Code**: Latest version
- **Remote - Containers extension**: Install from VS Code marketplace

### 3.2. Open in Container

```bash
# Clone the repository
git clone --recurse-submodules https://github.com/theinterneti/TTA.git

# Open in VS Code
code TTA
```

When prompted, click "Reopen in Container" to open the project in a devcontainer.

Alternatively, you can:
1. Open VS Code
2. Press F1 to open the command palette
3. Type "Remote-Containers: Open Folder in Container"
4. Select the TTA directory

## Component-Specific Setup

### TTA.prototype Setup

For detailed setup instructions specific to the TTA.prototype component:

```bash
cd TTA.prototype
./scripts/setup_dev_environment.sh
```

### tta.dev Setup

For detailed setup instructions specific to the tta.dev component:

```bash
cd tta.dev
./src/scripts/init_dev_environment.sh
```

## Verification

To verify that the installation was successful:

```bash
# Check Docker containers
docker-compose ps

# Check Neo4j
curl http://localhost:7474

# Check MCP server
curl http://localhost:8000/health
```

## Troubleshooting

### Docker Issues

If you encounter Docker-related issues, try the following:

```bash
# Fix Docker socket permissions
./scripts/docker/fixes/fix_docker_socket_permissions.sh

# Restart Docker
sudo systemctl restart docker

# Rebuild containers
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

### Submodule Issues

If you encounter issues with submodules:

```bash
# Reset submodules
git submodule update --init --recursive --force

# Check submodule status
git submodule status
```

### Environment Variable Issues

If you encounter issues with environment variables:

```bash
# Check environment variables
docker-compose config

# Verify .env files
cat .env
cat TTA.prototype/.env
cat tta.dev/.env
```

## Next Steps

After installation, you can:

1. **Explore the Documentation**: See the [Documentation Index](../index.md)
2. **Run Tests**: See the [Testing Guide](../development/testing/testing-guidelines.md)
3. **Start Development**: See the [Development Guide](../development/README.md)


---
**Logseq:** [[TTA.dev/Docs/Setup/Installation]]
