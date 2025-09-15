# TTA Developer Onboarding Guide

Welcome to the TTA (Therapeutic Text Adventure) project! This guide will help you get up and running with the development environment quickly and efficiently.

## Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - Required for the application
- **Git** - For version control
- **curl** - For downloading dependencies
- **Docker** (optional) - For running databases locally

### Automated Setup

The fastest way to get started is using our automated setup script:

```bash
# Clone the repository
git clone https://github.com/theinterneti/TTA.git
cd TTA

# Run the setup script
./scripts/setup_dev_environment.sh
```

This script will:
- Install uv (Python package manager)
- Create a virtual environment
- Install all dependencies
- Set up pre-commit hooks
- Configure development tools

### Manual Setup

If you prefer manual setup or the script fails:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

## Development Environment

### Project Structure

```
TTA/
├── src/                          # Main source code
│   ├── agent_orchestration/      # Agent coordination system
│   ├── api_gateway/              # API gateway service
│   ├── components/               # Core components
│   ├── player_experience/        # Player experience API
│   └── main.py                   # Main application entry
├── tests/                        # Test suite
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
├── .vscode/                      # VS Code configuration
├── .pre-commit-config.yaml       # Pre-commit hooks
├── .editorconfig                 # Editor configuration
└── pyproject.toml               # Project configuration
```

### Development Tools

The project uses modern Python development tools:

- **uv** - Fast Python package manager
- **black** - Code formatting
- **isort** - Import sorting
- **ruff** - Fast linting
- **mypy** - Type checking
- **pytest** - Testing framework
- **pre-commit** - Git hooks for quality assurance

### IDE Setup

#### VS Code (Recommended)

The project includes comprehensive VS Code configuration:

1. Open the project: `code .`
2. Install recommended extensions (VS Code will prompt you)
3. The workspace is pre-configured with:
   - Python interpreter settings
   - Formatting on save
   - Linting integration
   - Testing configuration
   - Debug configurations

#### Other IDEs

The `.editorconfig` file ensures consistent formatting across all editors.

## Running the Application

### Core Services

```bash
# Main application
uv run python src/main.py

# Player Experience API
uv run python src/player_experience/api/main.py

# API Gateway
uv run python src/api_gateway/app.py
```

### Testing

The project uses a three-tier testing approach:

```bash
# Unit tests (fast, no external dependencies)
uv run pytest tests/

# Integration tests with Neo4j
uv run pytest tests/ --neo4j

# Integration tests with Redis
uv run pytest tests/ --redis

# All tests
uv run pytest tests/ --neo4j --redis

# With coverage
uv run pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Sort imports
uv run isort src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type check
uv run mypy src/

# Run all quality checks
uv run pre-commit run --all-files
```

## Development Workflow

### 1. Before Starting Work

```bash
# Update your local repository
git pull origin main

# Ensure dependencies are up to date
uv sync --dev

# Run tests to ensure everything works
uv run pytest tests/
```

### 2. Making Changes

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Write/update tests
4. Run quality checks: `uv run pre-commit run --all-files`
5. Commit your changes (pre-commit hooks will run automatically)

### 3. Submitting Changes

1. Push your branch: `git push origin feature/your-feature-name`
2. Create a Pull Request on GitHub
3. Ensure all CI checks pass
4. Request review from team members

## Database Setup

### Local Development

For local development, you can use either:

1. **Mock Services** (default) - No setup required
2. **Docker Containers** - Run `docker-compose up -d`
3. **Local Installations** - Install Neo4j and Redis locally

### Environment Variables

Create a `.env` file for local configuration:

```bash
# Database Configuration
TTA_NEO4J_URI=bolt://localhost:7687
TTA_NEO4J_USER=neo4j
TTA_NEO4J_PASSWORD=password

TTA_REDIS_HOST=localhost
TTA_REDIS_PORT=6379

# Application Configuration
TTA_ENV=development
TTA_LOG_LEVEL=DEBUG
```

## Troubleshooting

### Common Issues

#### uv not found
```bash
# Reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

#### Pre-commit hooks failing
```bash
# Update hooks
uv run pre-commit autoupdate

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

#### Tests failing
```bash
# Check if databases are running
docker ps

# Run with verbose output
uv run pytest tests/ -v --tb=long

# Run specific test
uv run pytest tests/path/to/test.py::test_function -v
```

#### Import errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Or use uv run
uv run python -c "import src.main"
```

### Getting Help

- **Documentation**: Check the `docs/` directory
- **Issues**: Create a GitHub issue
- **Team Chat**: Use project communication channels
- **Code Review**: Ask for help in pull requests

## Contributing Guidelines

### Code Style

- Follow PEP 8 (enforced by black and ruff)
- Use type hints for all functions
- Write docstrings for public APIs
- Keep functions small and focused

### Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names
- Test both happy path and edge cases

### Documentation

- Update documentation for new features
- Include examples in docstrings
- Keep README.md current
- Document breaking changes

### Commit Messages

Use conventional commits format:
```
feat: add new player experience endpoint
fix: resolve database connection timeout
docs: update API documentation
test: add integration tests for auth flow
```

## Resources

- [Project README](../../README.md)
- [API Documentation](../api/)
- [Architecture Overview](../architecture/)
- [Deployment Guide](../deployment/)
- [Testing Guide](../testing/)

---

**Welcome to the team! Happy coding! 🚀**
