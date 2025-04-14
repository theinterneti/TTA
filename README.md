# TTA - Therapeutic Text Adventure

This repository contains the code for the Therapeutic Text Adventure (TTA) project, which consists of two main components:

## Repository Structure

- **tta.dev**: Reusable AI components (agents, RAG, database integration), including MCP materials
- **tta.prototype**: Narrative elements (worldbuilding, characters, storytelling)

## Directory Structure

- **Documentation**: Project documentation
- **config**: Configuration files
- **scripts**: Utility scripts
- **templates**: Template files for tta.dev and tta.prototype
- **external_data**: External data files
- **logs**: Log files
- **notebooks**: Jupyter notebooks

## Getting Started

To set up the project, run the following command:

```bash
./scripts/setup.sh
```

## Docker and DevContainer

Both tta.dev and tta.prototype have Docker and DevContainer configurations. To use Docker, run:

```bash
cd tta.dev
docker-compose up
```

or

```bash
cd tta.prototype
docker-compose up
```

## Documentation

For more information, see the documentation in the `Documentation` directory:

- [Environment Structure](Documentation/ENV_STRUCTURE.md)
- [GitHub Setup](Documentation/GITHUB_SETUP.md)
- [Docker Setup Guide](Documentation/docker/docker_setup_guide.md)
- [DevContainer Troubleshooting Guide](Documentation/docker/devcontainer_troubleshooting_guide.md)

## Organization Scripts

The repository includes several scripts to help organize the codebase:

- `scripts/organize_tta.sh`: Main script to organize the TTA repository
- `scripts/standardize_naming.sh`: Script to standardize naming conventions
- `scripts/organize_files.sh`: Script to organize files in the TTA repository
- `scripts/organize_documentation.sh`: Script to organize documentation in the TTA repository
- `scripts/docker/ensure_docker_consistency.sh`: Script to ensure Docker and DevContainer consistency across repositories
