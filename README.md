# TTA - Therapeutic Text Adventure

This repository contains the code for the Therapeutic Text Adventure (TTA) project, which consists of two main components:

## Repository Structure

- **tta.dev**: Reusable AI components (agents, RAG, database integration), including MCP materials
- **tta.prototype**: Narrative elements (worldbuilding, characters, storytelling)

## Directory Structure

- **Documentation**: Project documentation
- **config**: Configuration files
- **scripts**: Utility scripts
- **src**: Source code for the TTA orchestration module
- **templates**: Template files for tta.dev and tta.prototype
- **tests**: Tests for the TTA project
- **external_data**: External data files
- **logs**: Log files
- **notebooks**: Jupyter notebooks

## Getting Started

To set up the project, run the following command:

```bash
./scripts/setup.sh
```

## Orchestration

The TTA project includes an orchestration module that coordinates both tta.dev and tta.prototype components. To use the orchestrator, run:

```bash
# Start all components
./tta.sh start

# Start specific components
./tta.sh start tta.dev_neo4j tta.dev_llm

# Stop all components
./tta.sh stop

# Get status of all components
./tta.sh status
```

For more information, see the [Orchestration Module Documentation](src/orchestration/README.md).

## Docker and DevContainer

Both tta.dev and tta.prototype have Docker and DevContainer configurations. You can use the orchestration module to manage Docker containers, or run Docker commands directly:

```bash
# Using the orchestrator
./tta.sh docker compose up -d --repository tta.dev

# Or directly
cd tta.dev
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

## Testing

To run the tests for the TTA project, use the following command:

```bash
python -m unittest discover tests
```

## Agent Orchestration Diagnostics (Local)

Enable the diagnostics server for the Agent Orchestration component to inspect health and metrics locally.

- Configuration keys (example values for local dev):

  - `agent_orchestration.diagnostics.enabled = true`
  - `agent_orchestration.port = 8503` # default if unset
  - `player_experience.api.redis_url = redis://localhost:6379/0`

- Start the Agent Orchestration component (via orchestrator):

```bash
# Enables diagnostics in memory; adjust your config source accordingly
./tta.sh start agent_orchestration
```

- Endpoints (bound to 127.0.0.1):

  - JSON snapshot: http://127.0.0.1:8503/metrics
  - Prometheus format: http://127.0.0.1:8503/metrics-prom
  - Health: http://127.0.0.1:8503/health

- Notes:

  - The server only starts if `agent_orchestration.diagnostics.enabled=true`
  - Override the default port with `agent_orchestration.port`
  - Prometheus endpoint requires `prometheus_client` (installed automatically in dev)

- Tools Diagnostics:
  - GET /tools — list tools with status/metadata and cache stats
  - GET /tools/summary — paginated, filterable summary suitable for UI/CLI
  - See Documentation/components/agent_orchestration_tools.md for configuration and security details

## Admin: Manual Message Recovery

Trigger global recovery and print per-agent stats using the CLI:

```bash
uv run python src/main.py admin recover redis://localhost:6379/0 --key-prefix ao
```
