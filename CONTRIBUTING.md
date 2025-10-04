# Contributing to TTA

Thank you for your interest in contributing to the TTA (Therapeutic Text Adventure) project! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## 🤝 Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment for all contributors.

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** with uv package manager
- **Node.js 18+** for frontend development
- **Docker** and Docker Compose for local services
- **Git** for version control
- **GitHub CLI** (optional but recommended)

### Initial Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub
   gh repo fork theinterneti/TTA --clone
   cd TTA
   ```

2. **Install Dependencies**
   ```bash
   # Python dependencies
   uv sync --all-extras --dev
   
   # Node.js dependencies (for E2E tests)
   npm install
   
   # Pre-commit hooks
   pre-commit install
   ```

3. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your API keys
   # Get free OpenRouter API key at https://openrouter.ai
   ```

4. **Start Local Services**
   ```bash
   # Start Neo4j and Redis
   docker-compose up -d neo4j redis
   
   # Verify services are running
   docker-compose ps
   ```

5. **Run Tests**
   ```bash
   # Unit tests
   uv run pytest -q
   
   # Integration tests (requires services)
   uv run pytest -q --neo4j --redis
   ```

## 🔄 Development Workflow

### 1. Pick an Issue

- Browse [open issues](https://github.com/theinterneti/TTA/issues)
- Look for issues labeled `good first issue` for newcomers
- Comment on the issue to let others know you're working on it

### 2. Create a Branch

```bash
# Create a feature branch
git checkout -b feat/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 3. Make Changes

- Write clean, well-documented code
- Follow the code standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 4. Test Locally

```bash
# Run code quality checks
uv run ruff check src/ tests/
uv run black --check src/ tests/
uv run isort --check-only src/ tests/
uv run mypy src/

# Run tests
uv run pytest -q

# Run pre-commit hooks
pre-commit run --all-files
```

### 5. Commit Changes

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: <type>(<scope>): <description>

git commit -m "feat(api): add new endpoint for character creation"
git commit -m "fix(auth): resolve token expiration issue"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(integration): add tests for session management"
git commit -m "chore(deps): update dependencies"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

### 6. Push and Create PR

```bash
# Push your branch
git push origin feat/your-feature-name

# Create pull request
gh pr create --fill
```

## 📝 Code Standards

### Python Code Style

- **Formatting:** Black (line length: 88)
- **Import Sorting:** isort (Black-compatible profile)
- **Linting:** Ruff (replaces flake8, pylint)
- **Type Checking:** mypy with strict mode
- **Docstrings:** Google style

### Code Quality Tools

All tools run automatically via pre-commit hooks:

```bash
# Manual execution
uv run black src/ tests/
uv run isort src/ tests/
uv run ruff check src/ tests/ --fix
uv run mypy src/
uv run bandit -r src/  # Security scanning
```

### Best Practices

1. **Keep functions small** - Single responsibility principle
2. **Write descriptive names** - Variables, functions, classes
3. **Add type hints** - For all function signatures
4. **Write docstrings** - For all public functions and classes
5. **Handle errors gracefully** - Use proper exception handling
6. **Avoid magic numbers** - Use named constants
7. **DRY principle** - Don't repeat yourself

### Example Code

```python
from typing import Optional

def calculate_therapeutic_score(
    session_id: str,
    user_responses: list[str],
    baseline_score: float = 0.0
) -> Optional[float]:
    """Calculate therapeutic effectiveness score for a session.
    
    Args:
        session_id: Unique identifier for the therapy session
        user_responses: List of user responses during the session
        baseline_score: Starting score for comparison (default: 0.0)
    
    Returns:
        Calculated therapeutic score, or None if calculation fails
        
    Raises:
        ValueError: If session_id is empty or user_responses is empty
    """
    if not session_id or not user_responses:
        raise ValueError("session_id and user_responses are required")
    
    # Implementation here
    pass
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/              # Fast, isolated unit tests
├── integration/       # Tests with real services (Neo4j, Redis)
├── e2e/              # End-to-end tests with Playwright
└── conftest.py       # Shared fixtures
```

### Writing Tests

```python
import pytest
from src.your_module import your_function

def test_your_function_success():
    """Test successful execution of your_function."""
    result = your_function(valid_input)
    assert result == expected_output

def test_your_function_error():
    """Test error handling in your_function."""
    with pytest.raises(ValueError):
        your_function(invalid_input)

@pytest.mark.redis
def test_redis_integration(redis_client):
    """Test Redis integration (requires Redis service)."""
    redis_client.set("key", "value")
    assert redis_client.get("key") == "value"
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_specific.py

# Specific test function
uv run pytest tests/test_specific.py::test_function_name

# With coverage
uv run pytest --cov=src --cov-report=html

# Integration tests only
uv run pytest -m "redis or neo4j" --redis --neo4j

# Skip slow tests
uv run pytest -m "not slow"
```

## 🔍 Pull Request Process

### Before Submitting

- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages follow conventional commits
- [ ] Branch is up to date with main

### PR Template

When creating a PR, use the appropriate template:
- **Feature:** `.github/PULL_REQUEST_TEMPLATE/feature.md`
- **Bug Fix:** `.github/PULL_REQUEST_TEMPLATE/bug_fix.md`
- **Documentation:** `.github/PULL_REQUEST_TEMPLATE/documentation.md`

### Review Process

1. **Automated Checks:** CI/CD runs automatically
   - Code quality (ruff, black, isort, mypy)
   - Tests (unit, integration, e2e)
   - Security scanning

2. **Code Review:** Maintainer reviews your code
   - Provides feedback and suggestions
   - May request changes

3. **Approval:** Once approved, PR can be merged
   - Squash and merge (default)
   - Commit message follows conventional commits

### After Merge

- Your branch will be automatically deleted
- Changes will be included in the next release
- You'll be credited in the changelog

## 👥 Community

### Communication Channels

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** Q&A and general discussion (coming soon)
- **Pull Requests:** Code contributions and reviews

### Getting Help

- Check existing [documentation](Documentation/)
- Search [closed issues](https://github.com/theinterneti/TTA/issues?q=is%3Aissue+is%3Aclosed)
- Ask in [GitHub Discussions](https://github.com/theinterneti/TTA/discussions) (coming soon)
- Create a new issue with the `question` label

### Recognition

Contributors are recognized in:
- Repository contributors list
- Release changelogs
- Project documentation

## 📚 Additional Resources

- [Architecture Documentation](Documentation/architecture/)
- [API Documentation](Documentation/api/)
- [Development Guides](Documentation/development/)
- [Testing Framework](docs/testing-framework.md)
- [Security Policy](SECURITY.md)

## 📄 License

By contributing to TTA, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to TTA!** 🎉

Your contributions help make therapeutic AI technology more accessible and effective.

