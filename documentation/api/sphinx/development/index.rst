Development Documentation
=========================

This section contains comprehensive development documentation for the TTA platform.

.. toctree::
   :maxdepth: 2
   :caption: Development Guides:

   setup
   workflow
   standards
   tooling
   tutorials

Development Setup
-----------------

For detailed setup instructions, see the main :doc:`../getting-started` guide.

Quick Reference
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone and setup
   git clone https://github.com/theinterneti/TTA.git
   cd TTA
   ./scripts/setup_dev_environment.sh

   # Run tests
   uv run pytest tests/

   # Start development server
   uv run python src/main.py

Development Standards
---------------------

Code Quality
~~~~~~~~~~~~

- **Formatting**: Black for code formatting
- **Linting**: Ruff for fast Python linting
- **Type Checking**: MyPy for static type analysis
- **Security**: Bandit for security vulnerability scanning

Testing Requirements
~~~~~~~~~~~~~~~~~~~~

- **Unit Tests**: Required for all new code
- **Integration Tests**: Required for database interactions
- **Coverage**: Minimum 70% code coverage
- **Documentation**: All public APIs must be documented

Development Workflow
--------------------

1. **Create Feature Branch**: ``git checkout -b feature/name``
2. **Implement Changes**: Follow coding standards
3. **Write Tests**: Ensure comprehensive test coverage
4. **Run Quality Checks**: ``uv run pre-commit run --all-files``
5. **Create Pull Request**: Submit for review
6. **Address Feedback**: Iterate based on review comments
7. **Merge**: After approval and CI passes

Tooling and Scripts
-------------------

Development Scripts
~~~~~~~~~~~~~~~~~~~

- ``scripts/setup_dev_environment.sh`` - Complete development setup
- ``scripts/validate_test_configurations.sh`` - Test infrastructure validation
- ``scripts/establish_coverage_baseline.sh`` - Coverage baseline measurement

Quality Assurance
~~~~~~~~~~~~~~~~~

- Pre-commit hooks for automated quality checks
- GitHub Actions for CI/CD pipeline
- Comprehensive test suite with three-tier structure
- Coverage reporting with quality gates
