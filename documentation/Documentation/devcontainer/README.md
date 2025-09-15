# Devcontainer Documentation

This directory contains documentation related to the VS Code devcontainer setup for the TTA project.

## Contents

- [Devcontainer Troubleshooting Guide](devcontainer_troubleshooting_guide.md): Solutions for common issues that may arise when using the devcontainer for development.

## Overview

The TTA project uses VS Code devcontainers to provide a consistent development environment across all platforms. The devcontainer setup includes:

1. **Docker Compose Integration**: Uses docker-compose.yml to define the development environment
2. **VS Code Extensions**: Pre-configured extensions for Python development, Docker, and more
3. **Development Tools**: Includes tools for linting, formatting, and testing
4. **GPU Support**: Configuration for NVIDIA GPU access in the container

## Getting Started

To use the devcontainer:

1. Install [VS Code](https://code.visualstudio.com/)
2. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
3. Clone the TTA repository
4. Open the repository in VS Code
5. When prompted, click "Reopen in Container"

For troubleshooting, see the [Devcontainer Troubleshooting Guide](devcontainer_troubleshooting_guide.md).
