# VS Code Devcontainer Setup Guide

This guide explains how to set up and use the VS Code devcontainer for the TTA project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Devcontainer Features](#devcontainer-features)
- [Customizing the Devcontainer](#customizing-the-devcontainer)
- [Working with Multiple Repositories](#working-with-multiple-repositories)

## Prerequisites

Before you can use the devcontainer, you need to install:

1. [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. [Visual Studio Code](https://code.visualstudio.com/)
3. [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

For GPU support, you also need:
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- NVIDIA GPU drivers

## Getting Started

To start using the devcontainer:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TTA.git
   cd TTA
   ```

2. Open the project in VS Code:
   ```bash
   code .
   ```

3. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Remote-Containers: Reopen in Container"

4. VS Code will build and start the devcontainer, which may take a few minutes the first time

5. Once the devcontainer is running, you can use VS Code as normal, with all the development tools pre-configured

## Devcontainer Features

The TTA devcontainer includes:

### Development Tools

- Python with virtual environment
- Black code formatter
- isort import sorter
- mypy type checker
- pytest for testing
- Jupyter notebook support
- CodeCarbon for energy tracking

### VS Code Extensions

The devcontainer comes with pre-configured VS Code extensions:

- Python extension
- Pylance for Python language server
- Black formatter
- Jupyter notebook support
- Docker extension
- Remote development extensions
- And many more

### Environment Configuration

The devcontainer sets up the following environment:

- Python path configured to use the virtual environment
- PYTHONPATH set to include the project root
- Environment variables loaded from `.env` file
- Docker socket mounted for Docker-in-Docker support

## Customizing the Devcontainer

You can customize the devcontainer by editing the following files:

### .devcontainer/devcontainer.json

This file configures the VS Code devcontainer:

```json
{
  "name": "TTA Development Environment",
  "dockerComposeFile": [
    "../docker-compose.yml",
    "../docker-compose.dev.yml"
  ],
  "service": "app",
  "workspaceFolder": "/app",
  "customizations": {
    "vscode": {
      "extensions": [
        // Extensions to install
      ],
      "settings": {
        // VS Code settings
      }
    }
  }
}
```

### Adding Custom Extensions

To add custom extensions, edit the `extensions` array in `devcontainer.json`:

```json
"extensions": [
  "ms-python.python",
  "your-custom-extension"
]
```

### Changing VS Code Settings

To change VS Code settings, edit the `settings` object in `devcontainer.json`:

```json
"settings": {
  "python.formatting.provider": "black",
  "your.custom.setting": true
}
```

## Working with Multiple Repositories

The TTA project consists of multiple repositories. To work with them in the devcontainer:

### Root Repository

The root repository (`TTA`) contains the main devcontainer configuration and orchestrates all services.

### tta.dev Repository

To work with the `tta.dev` repository:

1. Open the `tta.dev` directory in VS Code
2. Use the command palette (F1) and select "Remote-Containers: Open Folder in Container"
3. Select the `tta.dev` directory

### TTA.prototype Repository

To work with the `TTA.prototype` repository:

1. Open the `TTA.prototype` directory in VS Code
2. Use the command palette (F1) and select "Remote-Containers: Open Folder in Container"
3. Select the `TTA.prototype` directory

For more information about Docker and container setup, see the [Docker Setup Guide](../docker/README.md).


---
**Logseq:** [[TTA.dev/Docs/Development/Setup]]
