Getting Started
===============

This guide will help you set up a development environment for the TTA platform and get you started with contributing to the project.

Prerequisites
-------------

Before you begin, ensure you have the following installed on your system:

Required Software
~~~~~~~~~~~~~~~~~

- **Python 3.11+**: The core runtime for TTA
- **Git**: For version control
- **Docker**: For running databases and services (optional but recommended)
- **curl**: For downloading dependencies

System Requirements
~~~~~~~~~~~~~~~~~~~

- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+ with WSL2
- **Memory**: Minimum 8GB RAM (16GB recommended for development)
- **Storage**: At least 10GB free space
- **Network**: Internet connection for downloading dependencies

Quick Setup
------------

The fastest way to get started is using our automated setup script:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/theinterneti/TTA.git
   cd TTA

   # Run the automated setup script
   ./scripts/setup_dev_environment.sh

This script will:

1. Install uv (Python package manager)
2. Create a virtual environment
3. Install all dependencies
4. Set up pre-commit hooks
5. Configure development tools

Manual Setup
-------------

If you prefer to set up the environment manually or the automated script fails:

Step 1: Install uv
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install uv (Python package manager)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.cargo/env

Step 2: Create Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create virtual environment
   uv venv

   # Activate virtual environment (Linux/macOS)
   source .venv/bin/activate

   # On Windows
   .venv\Scripts\activate

Step 3: Install Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install all dependencies including development tools
   uv sync --dev

Step 4: Set Up Pre-commit Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install pre-commit hooks
   uv run pre-commit install
   uv run pre-commit install --hook-type commit-msg

Step 5: Verify Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run tests to verify everything is working
   uv run pytest tests/ -k "not integration" --maxfail=5

   # Check code quality tools
   uv run black --version
   uv run ruff --version
   uv run mypy --version

Development Environment
-----------------------

IDE Configuration
~~~~~~~~~~~~~~~~~

The project includes comprehensive IDE configuration:

**VS Code (Recommended)**

1. Open the project: ``code .``
2. Install recommended extensions (VS Code will prompt you)
3. The workspace is pre-configured with:
   - Python interpreter settings
   - Formatting on save
   - Linting integration
   - Testing configuration
   - Debug configurations

**Other IDEs**

The ``.editorconfig`` file ensures consistent formatting across all editors.

Project Structure
~~~~~~~~~~~~~~~~~

.. code-block:: text

   TTA/
   ├── src/                          # Main source code
   │   ├── agent_orchestration/      # Agent coordination system
   │   ├── api_gateway/              # API gateway service
   │   ├── components/               # Core components
   │   ├── player_experience/        # Player experience API
   │   └── main.py                   # Main application entry
   ├── tests/                        # Test suite
   │   ├── unit/                     # Unit tests
   │   ├── integration/              # Integration tests
   │   └── utils/                    # Test utilities
   ├── docs/                         # Documentation
   │   ├── sphinx/                   # Sphinx documentation
   │   ├── development/              # Development guides
   │   └── testing/                  # Testing documentation
   ├── scripts/                      # Utility scripts
   ├── .vscode/                      # VS Code configuration
   └── pyproject.toml               # Project configuration

Running the Application
-----------------------

Local Development
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start the main application
   uv run python src/main.py

   # Start the Player Experience API
   uv run python src/player_experience/api/main.py

   # Start the API Gateway
   uv run python src/api_gateway/app.py

With Docker Compose
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start all services with databases
   docker-compose up -d

   # View logs
   docker-compose logs -f

   # Stop services
   docker-compose down

Testing
-------

TTA uses a three-tier testing approach:

Unit Tests
~~~~~~~~~~

Fast tests with no external dependencies:

.. code-block:: bash

   # Run unit tests
   uv run pytest tests/ -k "not integration"

   # Run with coverage
   uv run pytest tests/ -k "not integration" --cov=src --cov-report=html

Integration Tests
~~~~~~~~~~~~~~~~~

Tests that require external services:

.. code-block:: bash

   # Neo4j integration tests
   uv run pytest tests/ --neo4j

   # Redis integration tests
   uv run pytest tests/ --redis

   # All integration tests
   uv run pytest tests/ --neo4j --redis

Test Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run specific test file
   uv run pytest tests/test_specific_module.py

   # Run tests matching pattern
   uv run pytest tests/ -k "test_user"

   # Run tests with verbose output
   uv run pytest tests/ -v

   # Stop on first failure
   uv run pytest tests/ -x

Code Quality
------------

The project uses several tools to maintain code quality:

Formatting
~~~~~~~~~~

.. code-block:: bash

   # Format code with black
   uv run black src/ tests/

   # Sort imports with isort
   uv run isort src/ tests/

Linting
~~~~~~~

.. code-block:: bash

   # Lint with ruff
   uv run ruff check src/ tests/

   # Auto-fix issues
   uv run ruff check src/ tests/ --fix

Type Checking
~~~~~~~~~~~~~

.. code-block:: bash

   # Type check with mypy
   uv run mypy src/

Security Scanning
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Security scan with bandit
   uv run bandit -r src/

Pre-commit Hooks
~~~~~~~~~~~~~~~~

All quality checks run automatically on commit:

.. code-block:: bash

   # Run all pre-commit hooks manually
   uv run pre-commit run --all-files

   # Skip hooks for emergency commits (not recommended)
   git commit --no-verify

Development Workflow
--------------------

Creating a Feature
~~~~~~~~~~~~~~~~~~

1. **Create a branch**:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make your changes**:
   - Write code following the project's style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:

   .. code-block:: bash

      # Run tests
      uv run pytest tests/

      # Check code quality
      uv run pre-commit run --all-files

4. **Commit your changes**:

   .. code-block:: bash

      git add .
      git commit -m "feat: add new feature description"

5. **Push and create PR**:

   .. code-block:: bash

      git push origin feature/your-feature-name

Debugging
~~~~~~~~~

**Using VS Code Debugger**:

1. Set breakpoints in your code
2. Use the configured debug configurations
3. Start debugging with F5

**Using pytest debugger**:

.. code-block:: bash

   # Drop into debugger on failure
   uv run pytest tests/ --pdb

   # Drop into debugger on first failure
   uv run pytest tests/ --pdb -x

**Logging**:

.. code-block:: bash

   # Set log level for debugging
   export TTA_LOG_LEVEL=DEBUG
   uv run python src/main.py

Database Setup
--------------

Local Development Databases
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Option 1: Docker Compose (Recommended)**

.. code-block:: bash

   # Start databases
   docker-compose up -d neo4j redis

   # Check status
   docker-compose ps

**Option 2: Local Installation**

Install Neo4j and Redis locally following their respective installation guides.

**Option 3: Mock Services**

For unit testing, mock services are used automatically.

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Create a ``.env`` file for local configuration:

.. code-block:: bash

   # Database Configuration
   TTA_NEO4J_URI=bolt://localhost:7687
   TTA_NEO4J_USER=neo4j
   TTA_NEO4J_PASSWORD=password

   TTA_REDIS_HOST=localhost
   TTA_REDIS_PORT=6379

   # Application Configuration
   TTA_ENV=development
   TTA_LOG_LEVEL=DEBUG

Common Issues
-------------

Installation Problems
~~~~~~~~~~~~~~~~~~~~~

**uv not found**:

.. code-block:: bash

   # Reinstall uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.cargo/env

**Permission errors**:

.. code-block:: bash

   # Fix permissions on scripts
   chmod +x scripts/*.sh

**Import errors**:

.. code-block:: bash

   # Ensure PYTHONPATH includes src
   export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

Testing Issues
~~~~~~~~~~~~~~

**Container startup failures**:

.. code-block:: bash

   # Clean up containers
   docker system prune -f

   # Restart Docker service
   sudo systemctl restart docker

**Test failures**:

.. code-block:: bash

   # Run with verbose output
   uv run pytest tests/ -v --tb=long

   # Run specific failing test
   uv run pytest tests/path/to/test.py::test_function -v

Getting Help
------------

- **Documentation**: This comprehensive guide and API reference
- **Issues**: `GitHub Issues <https://github.com/theinterneti/TTA/issues>`_
- **Discussions**: `GitHub Discussions <https://github.com/theinterneti/TTA/discussions>`_
- **Code Review**: Ask for help in pull requests

Next Steps
----------

Once you have your development environment set up:

1. **Explore the codebase**: Start with the :doc:`architecture` documentation
2. **Run the tests**: Familiarize yourself with the test suite
3. **Read the API docs**: Check out the :doc:`api/modules` reference
4. **Pick an issue**: Look for "good first issue" labels on GitHub
5. **Join discussions**: Participate in project discussions and planning

Welcome to the TTA development community!
