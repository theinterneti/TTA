# TTA - Therapeutic Text Adventure

[![Tests](https://github.com/theinterneti/TTA/workflows/Tests/badge.svg)](https://github.com/theinterneti/TTA/actions/workflows/tests.yml)
[![Code Quality](https://github.com/theinterneti/TTA/workflows/Code%20Quality/badge.svg)](https://github.com/theinterneti/TTA/actions/workflows/code-quality.yml)
[![Security Scan](https://github.com/theinterneti/TTA/workflows/Security%20Scan/badge.svg)](https://github.com/theinterneti/TTA/actions/workflows/security-scan.yml)
[![E2E Tests](https://github.com/theinterneti/TTA/workflows/E2E%20Tests/badge.svg)](https://github.com/theinterneti/TTA/actions/workflows/e2e-tests.yml)

> AI-powered therapeutic text adventure platform combining evidence-based mental health support with engaging interactive storytelling

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

## Environment Setup

The TTA project uses a secure, consolidated environment configuration structure. To get started:

```bash
# 1. Copy the environment template
cp .env.example .env

# 2. Get a free OpenRouter API key at https://openrouter.ai
# 3. Edit .env and set your API key:
OPENROUTER_API_KEY=your_actual_key_here

# 4. Validate your setup
python scripts/validate_environment.py
```

For detailed setup instructions, see: [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)

## Documentation

For more information, see the documentation in the `Documentation` directory:

- [Environment Structure](Documentation/ENV_STRUCTURE.md) - **Updated with new consolidated structure**
- [Environment Setup Guide](ENVIRONMENT_SETUP.md) - **Comprehensive setup instructions**
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

The TTA project includes comprehensive testing infrastructure with multiple layers of validation:

### Comprehensive Test Battery 🧪

The TTA Comprehensive Test Battery provides robust, multi-dimensional testing with automatic mock fallback:

```bash
# Quick validation (standard tests)
python tests/comprehensive_battery/run_comprehensive_tests.py --categories standard

# Full test battery (all categories)
python tests/comprehensive_battery/run_comprehensive_tests.py --all --detailed-report

# Force mock mode (no external dependencies)
python tests/comprehensive_battery/run_comprehensive_tests.py --all --force-mock

# Using Makefile shortcuts
make test-all
make test-standard
make test-adversarial
```

**Test Categories:**
- **Standard Tests**: Normal user interactions and story generation flows
- **Adversarial Tests**: Security vulnerabilities and edge cases
- **Load/Stress Tests**: Performance under concurrent load
- **Data Pipeline Tests**: End-to-end data flow validation
- **Dashboard Tests**: Real-time monitoring functionality

**Key Features:**
- ✅ **Mock/Real Service Support**: Automatic fallback when services unavailable
- ✅ **CI/CD Integration**: GitHub Actions workflows included
- ✅ **Developer Dashboard**: Real-time monitoring and results visualization
- ✅ **Flexible Execution**: Run individual categories or full battery
- ✅ **Comprehensive Reporting**: JSON, HTML, CSV, and TXT formats

See [Comprehensive Test Battery Documentation](docs/testing/comprehensive-test-battery.md) for detailed usage.

### Traditional Testing

```bash
# Run traditional unit tests
python -m unittest discover tests

# Run with pytest (if available)
pytest

# Integration with comprehensive test battery
COMPREHENSIVE_TEST_MODE=true pytest tests/test_comprehensive_integration.py
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
