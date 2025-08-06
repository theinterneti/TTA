# Technology Stack & Build System

## Core Technologies

### Programming Languages
- **Python 3.x**: Primary language for orchestration, AI components, and backend services
- **YAML**: Configuration files and Docker Compose definitions
- **Shell/Bash**: Setup and maintenance scripts

### AI & Machine Learning
- **PyTorch**: Deep learning framework with GPU support
- **Transformers**: Hugging Face library for NLP models
- **Accelerate**: Distributed training and inference
- **Ray**: Distributed computing for AI workloads
- **CodeCarbon**: Carbon footprint tracking for AI operations

### Databases & Storage
- **Neo4j**: Knowledge graph database (ports 7687, 7688)
- **Redis**: Caching and session storage

### Infrastructure & Deployment
- **Docker & Docker Compose**: Containerization and orchestration
- **Nix**: Development environment management via flake.nix
- **Git Submodules**: Multi-repository architecture management

### Development Tools
- **Rich**: Enhanced CLI output and formatting
- **VS Code DevContainers**: Consistent development environments
- **Firebase Tools**: Deployment and hosting utilities

## Build System & Commands

### Main Orchestration Commands
```bash
# Start all components
./tta.sh start
python src/main.py start

# Start specific components
./tta.sh start neo4j llm
python src/main.py start neo4j llm

# Stop all components
./tta.sh stop

# Get component status
./tta.sh status

# Docker operations
./tta.sh docker compose up -d
./tta.sh docker compose up -d --repository tta.dev

# Configuration management
./tta.sh config get tta.dev.enabled
./tta.sh config set tta.dev.enabled true
```

### Setup & Maintenance
```bash
# Initial project setup
./scripts/setup.sh

# Update submodules
./scripts/update_submodules.sh

# Fix submodule issues
./scripts/fix_submodules.sh

# Organize project structure
./scripts/organize_tta.sh

# Docker consistency checks
./scripts/ensure_docker_consistency.sh
```

### Testing
```bash
# Run all tests
python -m unittest discover tests

# Test specific components
python -m unittest tests.test_orchestrator
python -m unittest tests.test_components
```

### Development Environment
```bash
# Enter Nix development shell
nix develop

# Setup with DevContainer
# Open in VS Code and select "Reopen in Container"
```

## Configuration Files

- **config/tta_config.yaml**: Main configuration for all components
- **docker-compose.yml**: Redis and shared services
- **gpu_requirements.txt**: GPU-dependent Python packages
- **.gitmodules**: Submodule definitions for tta.dev, tta.prototype, tta.prod

## Architecture Patterns

- **Component-based orchestration**: Modular services with dependency management
- **Multi-repository structure**: Separate concerns via Git submodules
- **Docker-first deployment**: Consistent environments across development and production
- **Configuration-driven**: YAML-based configuration with environment-specific overrides