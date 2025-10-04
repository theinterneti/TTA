# Code Quality Standards

This document defines the code quality standards and best practices for the TTA (Therapeutic Text Adventure) project.

## 📋 Overview

Code quality is essential for maintaining a robust, scalable, and maintainable codebase. These standards ensure consistency across the project and help new contributors understand our expectations.

## 🎯 Quality Principles

### Core Principles
1. **Readability**: Code should be self-documenting and easy to understand
2. **Maintainability**: Code should be easy to modify and extend
3. **Reliability**: Code should be robust and handle edge cases gracefully
4. **Performance**: Code should be efficient and scalable
5. **Security**: Code should follow security best practices
6. **Testability**: Code should be designed for easy testing

## 🔧 Code Style and Formatting

### Python Code Style
We follow [PEP 8](https://pep8.org/) with some project-specific modifications:

#### Formatting Tools
- **Black**: Automatic code formatting
- **isort**: Import sorting and organization
- **Ruff**: Fast Python linting

#### Configuration
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.ruff]
line-length = 88
target-version = "py311"
```

#### Key Style Rules
- **Line Length**: Maximum 88 characters
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings, single quotes for string literals in code
- **Trailing Commas**: Use trailing commas in multi-line structures
- **Blank Lines**: Two blank lines between top-level functions/classes

### Import Organization
```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import fastapi
import pydantic
from sqlalchemy import Column, String

# Local imports
from src.components.base import Component
from src.utils.logging import get_logger
```

## 📝 Documentation Standards

### Docstring Format
Use Google-style docstrings for all public functions, classes, and modules:

```python
def calculate_therapeutic_score(
    anxiety_level: int,
    depression_level: int,
    history: Optional[List[str]] = None
) -> float:
    """Calculate a therapeutic intervention score.

    This function analyzes user mental health indicators and returns
    a score that can be used to determine appropriate interventions.

    Args:
        anxiety_level: User's anxiety level on a scale of 0-10
        depression_level: User's depression level on a scale of 0-10
        history: Optional list of previous therapeutic interventions

    Returns:
        A therapeutic score between 0.0 and 1.0, where higher scores
        indicate greater need for intervention

    Raises:
        ValueError: If anxiety_level or depression_level is out of range

    Example:
        >>> score = calculate_therapeutic_score(7, 5, ["CBT", "mindfulness"])
        >>> print(f"Therapeutic score: {score:.2f}")
        Therapeutic score: 0.65
    """
    if not (0 <= anxiety_level <= 10):
        raise ValueError("Anxiety level must be between 0 and 10")
    if not (0 <= depression_level <= 10):
        raise ValueError("Depression level must be between 0 and 10")

    # Implementation here
    pass
```

### Code Comments
- Use comments sparingly for complex logic
- Explain **why**, not **what**
- Keep comments up-to-date with code changes
- Use TODO comments for future improvements

```python
# TODO: Implement caching for frequently accessed therapeutic profiles
# This will improve response times for returning users

# Calculate weighted score based on clinical research findings
# Reference: Smith et al. (2023) - Therapeutic Intervention Scoring
weighted_score = (anxiety_level * 0.6) + (depression_level * 0.4)
```

## 🏗️ Architecture and Design

### SOLID Principles
Follow SOLID principles for object-oriented design:

1. **Single Responsibility**: Each class should have one reason to change
2. **Open/Closed**: Open for extension, closed for modification
3. **Liskov Substitution**: Subtypes must be substitutable for base types
4. **Interface Segregation**: Clients shouldn't depend on unused interfaces
5. **Dependency Inversion**: Depend on abstractions, not concretions

### Design Patterns
Preferred patterns for common scenarios:

- **Factory Pattern**: For creating objects based on configuration
- **Strategy Pattern**: For interchangeable algorithms
- **Observer Pattern**: For event-driven architectures
- **Dependency Injection**: For loose coupling and testability

### Component Structure
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class TherapeuticComponent(ABC):
    """Base class for all therapeutic components."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def process(self, user_input: str) -> Dict[str, Any]:
        """Process user input and return therapeutic response."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the component is healthy."""
        pass
```

## 🧪 Testing Standards

### Test Coverage Requirements
- **Minimum Coverage**: 70% overall
- **Critical Modules**: 90% coverage required
- **New Code**: 80% coverage required

### Test Types
1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Test system performance
5. **Security Tests**: Test security vulnerabilities

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch

from src.therapeutic.assessment import TherapeuticAssessment

class TestTherapeuticAssessment:
    """Test suite for TherapeuticAssessment class."""

    @pytest.fixture
    def assessment(self):
        """Create a TherapeuticAssessment instance for testing."""
        config = {"model": "test", "threshold": 0.5}
        return TherapeuticAssessment(config)

    def test_calculate_score_valid_input(self, assessment):
        """Test score calculation with valid input."""
        score = assessment.calculate_score(anxiety=5, depression=3)

        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)

    def test_calculate_score_invalid_input(self, assessment):
        """Test score calculation with invalid input."""
        with pytest.raises(ValueError, match="Anxiety level must be"):
            assessment.calculate_score(anxiety=15, depression=3)

    @patch('src.therapeutic.assessment.external_api_call')
    def test_external_dependency(self, mock_api, assessment):
        """Test interaction with external dependencies."""
        mock_api.return_value = {"status": "success"}

        result = assessment.process_external_data()

        assert result["status"] == "success"
        mock_api.assert_called_once()
```

### Test Naming Conventions
- Test files: `test_*.py` or `*_test.py`
- Test classes: `TestClassName`
- Test methods: `test_method_name_scenario`

## 🔒 Security Standards

### Input Validation
Always validate and sanitize user input:

```python
from pydantic import BaseModel, validator
from typing import Optional

class UserInput(BaseModel):
    """Validated user input model."""

    message: str
    user_id: str
    session_id: Optional[str] = None

    @validator('message')
    def validate_message(cls, v):
        if len(v) > 1000:
            raise ValueError('Message too long')
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v.isalnum():
            raise ValueError('Invalid user ID format')
        return v
```

### Sensitive Data Handling
- Never log sensitive information
- Use environment variables for secrets
- Implement proper encryption for stored data
- Follow GDPR and HIPAA compliance requirements

```python
import os
from cryptography.fernet import Fernet

class SecureDataHandler:
    """Handle sensitive therapeutic data securely."""

    def __init__(self):
        # Get encryption key from environment
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable required")
        self.cipher = Fernet(key.encode())

    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(encrypted_data).decode()
```

## ⚡ Performance Standards

### Performance Guidelines
- Database queries should complete in <100ms
- API responses should be <200ms for 95th percentile
- Memory usage should not exceed 512MB per process
- CPU usage should not exceed 80% sustained

### Optimization Techniques
```python
import asyncio
from functools import lru_cache
from typing import List, Dict

class PerformantTherapeuticEngine:
    """High-performance therapeutic processing engine."""

    @lru_cache(maxsize=1000)
    def get_cached_assessment(self, user_profile_hash: str) -> Dict:
        """Cache frequently accessed assessments."""
        # Expensive computation here
        pass

    async def batch_process_users(self, user_ids: List[str]) -> List[Dict]:
        """Process multiple users concurrently."""
        tasks = [self.process_user(user_id) for user_id in user_ids]
        return await asyncio.gather(*tasks)

    async def process_user(self, user_id: str) -> Dict:
        """Process individual user asynchronously."""
        # Async processing logic
        pass
```

## 🔍 Code Review Standards

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Documentation is complete and accurate
- [ ] Tests are comprehensive and pass
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Error handling is appropriate
- [ ] No code duplication
- [ ] Dependencies are justified

### Review Process
1. **Self Review**: Author reviews their own code first
2. **Automated Checks**: CI/CD pipeline runs all checks
3. **Peer Review**: At least one team member reviews
4. **Security Review**: Security-sensitive changes get additional review
5. **Final Approval**: Maintainer approves and merges

## 📊 Quality Metrics

### Automated Quality Checks
- **Code Coverage**: Measured by pytest-cov
- **Code Complexity**: Measured by radon
- **Security Vulnerabilities**: Scanned by bandit
- **Type Coverage**: Checked by mypy
- **Documentation Coverage**: Measured by interrogate

### Quality Gates
All PRs must pass these quality gates:
- All tests pass
- Coverage >= 70%
- No high-severity security issues
- No type errors
- Documentation coverage >= 80%
- Code complexity within acceptable limits

## 🛠️ Tools and Automation

### Development Tools
```bash
# Install development dependencies
uv pip install -r requirements-dev.txt

# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Lint code
uv run ruff check src/ tests/
uv run mypy src/

# Run tests with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Security scan
uv run bandit -r src/

# Check documentation
uv run interrogate src/
```

### Pre-commit Hooks
Automated quality checks run on every commit:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.287
    hooks:
      - id: ruff
```

## 📈 Continuous Improvement

### Quality Monitoring
- Weekly code quality reports
- Monthly technical debt assessment
- Quarterly architecture reviews
- Annual security audits

### Learning and Development
- Regular code review sessions
- Technical talks on best practices
- External training and conferences
- Knowledge sharing documentation

## 🎯 Enforcement

### Automated Enforcement
- Pre-commit hooks prevent low-quality commits
- CI/CD pipeline blocks merges that don't meet standards
- Automated code review tools provide feedback

### Manual Enforcement
- Code review process ensures human oversight
- Regular quality audits identify areas for improvement
- Team discussions address quality concerns

---

## 📚 Resources

### External References
- [PEP 8 - Style Guide for Python Code](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Clean Code by Robert Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [Effective Python by Brett Slatkin](https://effectivepython.com/)

### Internal Resources
- [Contributing Guidelines](../CONTRIBUTING.md)
- [Development Setup Guide](../docs/development/setup.md)
- [Testing Guide](../docs/testing/README.md)
- [Security Guidelines](../docs/security/README.md)

---

*These standards are living documents that evolve with the project. Suggestions for improvements are always welcome!*
