# Installation

This guide will walk you through installing the Therapeutic Text Adventure (TTA) platform on your local machine.

## Prerequisites

Before installing TTA, ensure you have the following software installed:

### Required Software

- **Python 3.12+**: TTA requires Python 3.12 or higher
  - Download from [python.org](https://www.python.org/downloads/)
  - Verify installation: `python --version`

- **uv Package Manager**: Modern Python package manager
  - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Verify installation: `uv --version`
  - Documentation: [uv docs](https://github.com/astral-sh/uv)

- **Node.js 18+**: Required for frontend development
  - Download from [nodejs.org](https://nodejs.org/)
  - Verify installation: `node --version` and `npm --version`

- **Docker & Docker Compose**: For running services (Neo4j, Redis)
  - Download from [docker.com](https://www.docker.com/get-started)
  - Verify installation: `docker --version` and `docker-compose --version`

- **Git**: For version control
  - Download from [git-scm.com](https://git-scm.com/)
  - Verify installation: `git --version`

### Optional Software

- **GitHub CLI**: For creating pull requests and managing issues
  - Install: See [cli.github.com](https://cli.github.com/)
  - Verify installation: `gh --version`

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/theinterneti/TTA.git
cd TTA
```

### 2. Set Up Environment Variables

TTA requires several environment variables for configuration. Copy the example environment file and customize it:

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` with your preferred text editor:

```bash
nano .env  # or use vim, code, etc.
```

**Required Environment Variables:**

```bash
# OpenRouter API Key (get a free key at https://openrouter.ai)
OPENROUTER_API_KEY=your_api_key_here

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_AUTH=neo4j/your_password_here

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

!!! tip "Getting an OpenRouter API Key"
    1. Visit [openrouter.ai](https://openrouter.ai)
    2. Sign up for a free account
    3. Navigate to API Keys section
    4. Create a new API key
    5. Copy the key to your `.env` file

### 3. Install Python Dependencies

TTA uses `uv` for fast, reliable dependency management:

```bash
# Install all dependencies including development tools
uv sync --all-extras --dev
```

This command will:

- Create a virtual environment (if not exists)
- Install all package dependencies from `pyproject.toml`
- Install development dependencies (testing, linting, etc.)
- Install all optional extras (monitoring, security, etc.)

### 4. Install Pre-commit Hooks

Pre-commit hooks ensure code quality before commits:

```bash
# Install pre-commit hooks
pre-commit install
```

The hooks will automatically run:

- **Ruff**: Linting and formatting
- **Secret Detection**: Prevent committing secrets
- **Conventional Commits**: Enforce commit message format
- **Pytest Fixture Validation**: Ensure proper async fixture decorators

### 5. Start Docker Services

TTA requires Neo4j (graph database) and Redis (caching/sessions):

```bash
# Start Neo4j and Redis in detached mode
docker-compose up -d neo4j redis

# Verify services are running
docker-compose ps
```

Expected output:

```
NAME                COMMAND                  SERVICE             STATUS              PORTS
tta-neo4j-1         "/startup/docker-ent…"   neo4j               running             0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp
tta-redis-1         "docker-entrypoint.s…"   redis               running             0.0.0.0:6379->6379/tcp
```

### 6. Verify Installation

Run the environment validation script to ensure everything is configured correctly:

```bash
python scripts/validate_environment.py
```

This script checks:

- ✅ Python version compatibility
- ✅ Required dependencies installed
- ✅ Environment variables configured
- ✅ Docker services running
- ✅ Database connectivity

## Troubleshooting

### Python Version Issues

If you have multiple Python versions installed:

```bash
# Use uv to specify Python version
uv python install 3.12

# Verify uv is using correct version
uv run python --version
```

### Docker Service Issues

If services fail to start:

```bash
# Check Docker logs
docker-compose logs neo4j
docker-compose logs redis

# Restart services
docker-compose restart neo4j redis

# Clean up and restart
docker-compose down -v
docker-compose up -d neo4j redis
```

### Permission Issues

On Linux/macOS, you may need to adjust permissions:

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Fix Docker socket permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

### Environment Variable Issues

If environment variables aren't loading:

```bash
# Verify .env file exists
ls -la .env

# Check file contents (be careful not to expose secrets)
cat .env | grep -v "API_KEY"

# Ensure no trailing spaces or quotes
# Use: VARIABLE=value
# Not: VARIABLE="value" or VARIABLE=value
```

## Next Steps

Once installation is complete:

1. **[Quick Start Guide](quickstart.md)**: Run your first TTA session
2. **[Configuration Guide](configuration.md)**: Customize TTA settings
3. **[Development Guide](../development/contributing.md)**: Start contributing

## Additional Resources

- **[Environment Setup Guide](../../ENVIRONMENT_SETUP.md)**: Detailed environment configuration
- **[Docker Setup Guide](../../Documentation/docker/docker_setup_guide.md)**: Advanced Docker configuration
- **[Troubleshooting Guide](../../Documentation/docker/devcontainer_troubleshooting_guide.md)**: Common issues and solutions


---
**Logseq:** [[TTA.dev/Docs/Getting-started/Installation]]
