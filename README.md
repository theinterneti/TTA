# TTA Project

This repository manages two sub-repositories as Git submodules:
- `tta.dev`: For known working implementations
- `TTA.prototype`: For active development

This meta-repository provides consistent Docker configuration and development environment setup for both sub-repositories.

## Repository Structure

```
TTA/
├── .gitmodules           # Submodule configuration
├── README.md             # This file
├── setup.sh              # Setup script
├── templates/            # Template files for submodules
│   ├── tta.dev/          # Templates for tta.dev
│   └── TTA.prototype/    # Templates for TTA.prototype
├── tta.dev/              # Submodule for stable implementations
└── TTA.prototype/        # Submodule for active development
```

## Setup Instructions

### Initial Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/theinterneti/TTA.git
   cd TTA
   ```

2. Run the setup script to initialize submodules:
   ```bash
   ./setup.sh
   ```

3. The setup script will:
   - Initialize the Git submodules
   - Copy Docker configuration files if needed
   - Set up the development environment

### Docker Setup

Both repositories use their own devcontainer and docker-compose setup. The devcontainers have been configured to have access to the host's Docker daemon, allowing you to run Docker commands from within the containers.

#### Key Features

1. **Docker-in-Docker Access**:
   - The Docker socket is mounted from the host to the containers
   - Docker CLI is installed in the containers
   - The devcontainer.json files include the Docker-outside-of-Docker feature

2. **Volume Mounts**:
   - Host directories are mounted for data sharing
   - Docker socket is mounted at `/var/run/docker.sock`

3. **Development Environment**:
   - VS Code extensions for Docker, Python, and other tools are pre-configured
   - CUDA support for GPU acceleration

## Development Workflow

1. Open either `tta.dev` or `TTA.prototype` in VS Code
2. Use the "Reopen in Container" option when prompted
3. The container will have access to the host's Docker daemon

### Working with TTA.prototype

The TTA.prototype repository is the active development environment. To use it:

1. Open the TTA.prototype folder in VS Code
2. When prompted, select "Reopen in Container"
3. The devcontainer will start with the following features:
   - Docker access via the host's Docker socket
   - Neo4j database for graph storage
   - Python environment with all dependencies
   - Access to the shared data directory

### Troubleshooting Devcontainer Issues

If the devcontainer fails to start:

1. Check the Docker logs: `docker logs tta-app`
2. Verify the Docker socket is accessible: `ls -la /var/run/docker.sock`
3. Make sure the init script has execute permissions: `chmod +x TTA.prototype/scripts/init_dev_environment.sh`
4. Try rebuilding the container: VS Code > Command Palette > "Remote-Containers: Rebuild Container"

## Updating Submodules

To update the submodules to their latest versions:

```bash
git submodule update --remote --merge
```

## Adding New Docker Configuration

If you need to update the Docker configuration:

1. Modify the templates in the `templates/` directory
2. Run the setup script to apply the changes to the submodules

## Environment Variable Structure

See [ENV_STRUCTURE.md](ENV_STRUCTURE.md) for detailed documentation on the environment variable structure.

## Port allocation strategy
TTA.prototype (Development):
- Neo4j Browser: 7474
- Neo4j Bolt: 7687
- MCP Server: 8000

tta.dev (Stable):
- Neo4j Browser: 7475
- Neo4j Bolt: 7688
- MCP Server: 8001

Root TTA:
- Neo4j Browser: 7476
- Neo4j Bolt: 7689
- MCP Server: 8002

## Volume strategy
version: '3.8'

services:
  neo4j:
    container_name: tta-root-neo4j
    ports:
      - "7476:7474"
      - "7689:7687"
    volumes:
      - tta-root-neo4j-data:/data
      - ./neo4j/conf:/conf
      - ./neo4j/logs:/logs
      - ./neo4j/plugins:/plugins

  app:
    container_name: tta-root-app
    volumes:
      - .:/app:delegated
      - tta-root-venv:/app/.venv
      - tta-root-hf-cache:/root/.cache/huggingface
      - tta-root-model-cache:/app/.model_cache
      - ./data:/app/external_data:delegated
      - /var/run/docker.sock:/var/run/docker.sock:rw

  basic-mcp-server:
    container_name: tta-root-mcp
    ports:
      - "8002:8000"

volumes:
  tta-root-neo4j-data:
  tta-root-venv:
  tta-root-hf-cache:
  tta-root-model-cache:
  
## Notes

- The Docker socket mount allows containers to communicate with the host's Docker daemon
- This setup enables nested container creation and management
- The Docker CLI is installed in the containers, but the Docker daemon runs on the host
- Git submodules can be tricky to work with; always make sure you're in the right directory when making changes
