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

## Updating Submodules

To update the submodules to their latest versions:

```bash
git submodule update --remote --merge
```

## Adding New Docker Configuration

If you need to update the Docker configuration:

1. Modify the templates in the `templates/` directory
2. Run the setup script to apply the changes to the submodules

## Notes

- The Docker socket mount allows containers to communicate with the host's Docker daemon
- This setup enables nested container creation and management
- The Docker CLI is installed in the containers, but the Docker daemon runs on the host
- Git submodules can be tricky to work with; always make sure you're in the right directory when making changes
