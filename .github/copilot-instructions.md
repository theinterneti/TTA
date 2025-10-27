# GitHub Copilot Instructions for TTA Repository

## Repository Overview

**TTA (Therapeutic Text Adventure)** is an AI-powered therapeutic platform combining evidence-based mental health support with interactive storytelling. The system uses multi-agent orchestration (LangGraph) to create adaptive therapeutic narratives.

- **Size:** ~36,000 lines of Python code across multiple components
- **Languages:** Python 3.12+, TypeScript/React (frontend)
- **Architecture:** Microservices with FastAPI backend, Neo4j graph database, Redis cache
- **Package Manager:** UV (modern, fast Python package manager - replaces pip/poetry)
- **Key Frameworks:** FastAPI, LangGraph, Neo4j, Redis, React/Next.js

## Critical: Always Use UV, Never Use pip

**IMPORTANT:** This project uses UV exclusively for package management. NEVER use `pip`, `pip install`, `poetry`, or other package managers.

```bash
# ✅ CORRECT - Use UV commands
uv sync                    # Install all dependencies
uv sync --group test       # Install test dependencies only
uv run pytest              # Run tests in UV environment
uvx pytest                 # Run pytest as standalone tool
uvx ruff check src/        # Run ruff linter

# ❌ WRONG - Never use these
pip install -r requirements.txt   # NO requirements.txt exists
poetry install                    # Project doesn't use poetry
python -m pytest                  # Won't find dependencies
```

## Build and Test Process

### Initial Setup (First Time Only)

```bash
# 1. Install UV package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# 2. Install all dependencies (~2-3 minutes first time, cached thereafter)
uv sync --all-extras --dev

# 3. Install pre-commit hooks
pre-commit install

# 4. Copy environment template and configure
cp .env.example .env
# Edit .env to add OPENROUTER_API_KEY (get free key at https://openrouter.ai)

# 5. Start required services (Neo4j and Redis)
docker compose up -d neo4j redis
# Note: Use 'docker compose' (not 'docker-compose') - modern syntax
```

### Running Tests (CRITICAL - Read This)

**Test execution varies by branch to optimize CI/CD performance:**

```bash
# Development branch: Unit tests only (~5-10 minutes)
uv run pytest -q

# Staging/Main branches: Full test suite (~20-30 minutes)
uv run pytest -q --neo4j --redis

# Run specific test types
uv run pytest tests/unit/              # Unit tests only
uv run pytest tests/integration/       # Integration tests (requires services)
uv run pytest tests/e2e/              # E2E tests (requires services + frontend)

# With coverage reporting
uv run pytest --cov=src --cov-report=html

# Using Makefile shortcuts
make test                  # Unit tests only
make test-integration      # Full integration tests
```

**Important:** Integration tests require Neo4j and Redis services running. If tests fail with connection errors, start services with `docker compose up -d neo4j redis`.

### Code Quality Checks (MUST RUN BEFORE COMMIT)

```bash
# Linting with Ruff (replaces flake8, pylint, isort, black)
uvx ruff check src/ tests/              # Check for issues
uvx ruff check --fix src/ tests/        # Auto-fix issues
uvx ruff format src/ tests/             # Format code

# Type checking with Pyright (replaces mypy - 10-100x faster)
uvx pyright src/

# Security scanning
uvx bandit -r src/ -c pyproject.toml

# Run all quality gates (validates before PR)
./scripts/validate-quality-gates.sh development

# Or use pre-commit hooks (runs automatically on commit)
pre-commit run --all-files
```

### Docker Services

```bash
# Start all services
docker compose up -d

# Start specific services only (faster for development)
docker compose up -d neo4j redis

# View logs
docker compose logs -f neo4j
docker compose logs -f redis

# Stop services
docker compose down

# Clean up volumes (WARNING: deletes all data)
docker compose down -v

# Check service health
docker compose ps
```

## Project Structure and Key Files

### Root Directory Files
```
.github/                    # CI/CD workflows and issue templates
├── workflows/             # GitHub Actions workflows
│   ├── tests.yml         # Test automation (branch-specific)
│   ├── code-quality.yml  # Ruff linting, Pyright type checking
│   ├── security-scan.yml # Security scanning (Bandit, CodeQL, Trivy)
│   ├── e2e-tests.yml     # End-to-end tests with Playwright
│   └── mutation-testing.yml # Mutation testing for critical services

src/                       # Python source code (~36k lines)
├── components/           # Core TTA components
│   ├── model_management/     # LLM model selection and fallback
│   ├── gameplay_loop/        # Turn-based game mechanics
│   ├── narrative_coherence/  # Story consistency validation
│   ├── therapeutic_systems_enhanced/ # Safety and therapeutic frameworks
│   └── narrative_arc_orchestrator/   # Story progression management
├── api_gateway/          # API gateway service
├── player_experience/    # Player-facing services
│   ├── api/             # FastAPI backend
│   ├── frontend/        # React/Next.js frontend
│   └── services/        # Business logic
└── monitoring/          # Prometheus/Grafana monitoring

tests/                    # Test suites
├── unit/                # Fast isolated tests
├── integration/         # Tests with Neo4j/Redis
├── e2e/                # Playwright end-to-end tests
└── comprehensive_battery/ # Full validation suite

scripts/                 # Automation scripts (81+ shell/Python scripts)
├── validate-quality-gates.sh    # Pre-PR validation
├── validate-environment.py      # Environment setup validation
├── run-mutation-tests.sh        # Mutation testing
└── create-feature-branch.sh     # Branch creation helper

Configuration Files:
├── pyproject.toml       # Python project config, dependencies, tool settings
├── pytest.ini          # Pytest configuration
├── pyrightconfig.json  # Pyright type checker config
├── .pre-commit-config.yaml  # Pre-commit hooks
├── docker-compose.yml  # Docker services (minimal: redis only)
├── docker-compose.dev.yml    # Development environment
└── Makefile            # Test tier shortcuts
```

### Source Code Architecture

**Component-Based Architecture:** Each component in `src/components/` follows a standard pattern:
- `__init__.py` - Component interface
- `component.py` - Core implementation
- `models.py` - Pydantic data models
- `tests/` - Component-specific tests

**Critical Components (Do NOT break these):**
- `model_management/` - Has 100% mutation test coverage (534/534 mutations killed)
- `gameplay_loop/` - Core game mechanics
- `therapeutic_systems_enhanced/` - Safety validation (HIPAA compliance)
- `narrative_arc_orchestrator/` - Story progression logic

## CI/CD Workflows and Validation

### Branch Strategy (Three-Tier)

```
development → staging → main
    ↓           ↓        ↓
  unit tests  full tests  comprehensive tests
   ~5-10min   ~20-30min    ~45-60min
```

**Important Auto-Merge Rules:**
- PRs to `development`: Auto-merge when unit tests pass (no approval needed)
- PRs to `staging`: Auto-merge when full test suite passes (no approval needed)
- PRs to `main`: Requires manual approval after comprehensive tests

### Creating Feature Branches

```bash
# ALWAYS use the helper script (enforces naming conventions)
./scripts/create-feature-branch.sh <domain> <description>

# Domains: clinical, game, infra
# Example:
./scripts/create-feature-branch.sh game player-inventory

# This creates: feature/game-player-inventory
# And ensures base branch is 'development'
```

### Pre-Commit Hooks (Run Automatically)

The following checks run automatically on every commit:
- ✅ Ruff linting and formatting (auto-fixes most issues)
- ✅ Trailing whitespace removal
- ✅ YAML/JSON/TOML validation
- ✅ Bandit security scanning
- ✅ Secret detection (uses .secrets.baseline)
- ✅ Conventional commit message validation
- ✅ pytest-asyncio fixture decorator validation

**If pre-commit fails:**
```bash
# Hooks often auto-fix issues, just re-add and commit
git add .
git commit -m "feat(component): your message"

# To bypass temporarily (use sparingly)
git commit --no-verify -m "wip: work in progress"
```

### Commit Message Format (Enforced)

Use Conventional Commits format:
```bash
# Format: <type>(<scope>): <description>

feat(api): add new character creation endpoint
fix(auth): resolve token expiration issue
docs(readme): update installation instructions
test(integration): add session management tests
refactor(orchestration): extract filesystem operations
perf(cache): optimize Redis connection pooling
ci(workflow): update test timeout settings
chore(deps): update dependencies
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `ci`, `chore`

## Common Issues and Solutions

### Issue: UV command not found
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Or add to ~/.bashrc for persistence
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Issue: Tests fail with "connection refused" (Neo4j/Redis)
```bash
# Start required services
docker compose up -d neo4j redis

# Verify services are healthy
docker compose ps

# Check logs if still failing
docker compose logs neo4j
docker compose logs redis
```

### Issue: Pre-commit hooks fail
```bash
# Update pre-commit hooks to latest versions
pre-commit autoupdate

# Run manually to see detailed errors
pre-commit run --all-files

# Clear cache if hooks behave strangely
pre-commit clean
pre-commit install
```

### Issue: Import errors after adding dependencies
```bash
# ALWAYS sync dependencies after pyproject.toml changes
uv sync --all-extras --dev

# For specific dependency groups
uv sync --group test
uv sync --group lint
```

### Issue: Docker Compose command not found
```bash
# Modern Docker includes 'docker compose' (not 'docker-compose')
# If using old version, install Docker Compose V2
# Or use: docker-compose (with hyphen) for legacy versions
```

### Issue: Pyright/Ruff errors in IDE
```bash
# Ensure your IDE uses the UV-managed Python interpreter
# Location: .venv/bin/python

# VS Code: Select interpreter from .venv
# PyCharm: Configure Python interpreter to use .venv
```

## Testing Strategy

### Test Markers (Use to Filter Tests)

```bash
# Skip slow tests during development
uv run pytest -m "not slow"

# Run only Neo4j tests
uv run pytest -m neo4j --neo4j

# Run only Redis tests
uv run pytest -m redis --redis

# Skip integration tests
uv run pytest -m "not integration"

# Available markers: unit, integration, e2e, performance, neo4j, redis, slow
```

### Coverage Requirements by Component Stage

- **Development:** 60% test coverage minimum
- **Staging:** 70% test coverage minimum
- **Production:** 80% test coverage minimum

Check coverage:
```bash
uv run pytest --cov=src --cov-report=term
uv run pytest --cov=src --cov-report=html  # Opens htmlcov/index.html
```

## Environment Variables (Required)

```bash
# Copy environment template
cp .env.example .env

# Required variables (edit .env):
OPENROUTER_API_KEY=<your-key>      # Get free key at https://openrouter.ai
NEO4J_URI=bolt://localhost:7687
NEO4J_AUTH=neo4j/testpassword
REDIS_URL=redis://localhost:6379/0

# Optional (for monitoring)
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

## Performance Notes

### UV is Fast - Leverage It

```bash
# UV caches packages aggressively
# First install: ~2-3 minutes
# Subsequent installs: ~5-10 seconds

# Use UV's locked dependencies (uv.lock) for reproducibility
uv sync                    # Uses lock file
uv sync --upgrade          # Updates dependencies
```

### Test Performance Tips

```bash
# Use xdist for parallel test execution
uv run pytest -n auto      # Auto-detect CPU cores

# Run only fast tests during development
uv run pytest -m "not slow" -n auto

# For quick validation (unit tests only)
make test
```

## Security and Secrets

- **Never commit secrets** - Use .env files (gitignored)
- **Secret scanning runs automatically** via detect-secrets
- **Baseline file:** `.secrets.baseline` (contains known false positives)
- **Security scans:** Bandit, CodeQL, Trivy run in CI/CD

```bash
# Update secrets baseline if adding intentional "secrets" (e.g., test data)
detect-secrets scan > .secrets.baseline
```

## Key Dependencies and Versions

- **Python:** 3.12+ (strict requirement)
- **UV:** Latest (install via curl script)
- **Node.js:** 18+ (for frontend and E2E tests)
- **Docker:** 20.10+ (use modern `docker compose`, not `docker-compose`)
- **Neo4j:** 5.x community edition
- **Redis:** 7.x

## Additional Validation Commands

```bash
# Validate environment setup
python scripts/validate_environment.py

# Check Docker runtime
python scripts/verify_docker_runtime_setup.py

# Validate Docker Compose configuration
docker compose config

# Run comprehensive test battery (all categories)
python tests/comprehensive_battery/run_comprehensive_tests.py --all

# Mutation testing (critical components only)
./scripts/run-mutation-tests.sh --all
```

## Important Notes for Copilot

1. **Always use UV commands** - Never suggest pip, poetry, or other package managers
2. **Respect the three-tier branch strategy** - Feature branches always target `development`
3. **Run tests before committing** - `development` branch runs unit tests only in CI
4. **Follow conventional commits** - Commit messages are validated via pre-commit hook
5. **Check for running services** - Integration tests need Neo4j and Redis running
6. **Use modern Docker syntax** - `docker compose` (space), not `docker-compose` (hyphen)
7. **Pyright over MyPy** - Project uses Pyright for type checking (10-100x faster)
8. **Ruff over Black/isort/flake8** - Single tool for linting, formatting, import sorting
9. **Watch for test markers** - Different tests require different services (neo4j, redis)
10. **Component maturity matters** - Don't break production components (80%+ coverage)

## Trust These Instructions

These instructions are comprehensive and tested. Only search the codebase if:
- Information here is incomplete or contradictory
- You need specific implementation details not covered
- You encounter errors not documented in "Common Issues"

For most tasks, these instructions provide everything needed to work efficiently in this repository.
