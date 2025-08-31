Getting Started with TTA Development
====================================

This comprehensive guide will walk you through setting up your development environment and making your first contribution to the Therapeutic Text Adventure (TTA) platform.

Overview
--------

TTA is a sophisticated platform that combines therapeutic interventions with interactive narrative experiences. The platform consists of several key components:

- **Agent Orchestration**: Manages AI agents and their interactions
- **Player Experience**: Handles user interactions and game mechanics
- **API Gateway**: Routes and manages API requests
- **Narrative Engine**: Generates and manages story content
- **Therapeutic Safety**: Ensures safe and beneficial user experiences

Prerequisites
-------------

Before you begin, ensure you have the following installed:

**Required Software**
~~~~~~~~~~~~~~~~~~~~~

- **Python 3.11+**: The platform is built with modern Python
- **Git**: For version control and collaboration
- **uv**: Fast Python package manager (recommended)
- **Docker**: For running databases and services (optional but recommended)

**Recommended Tools**
~~~~~~~~~~~~~~~~~~~~

- **VS Code** or **PyCharm**: IDEs with excellent Python support
- **Postman** or **Insomnia**: For API testing
- **Neo4j Desktop**: For database visualization
- **Redis CLI**: For cache inspection

Installation Guide
------------------

Step 1: Clone the Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone the main repository
   git clone https://github.com/theinterneti/TTA.git
   cd TTA

   # Add your fork as a remote (if you've forked the repo)
   git remote add fork https://github.com/YOUR_USERNAME/TTA.git

Step 2: Set Up Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using uv (Recommended):

.. code-block:: bash

   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   uv pip install -r requirements.txt
   uv pip install -r requirements-dev.txt

Using pip:

.. code-block:: bash

   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

Step 3: Set Up Development Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start the required databases:

.. code-block:: bash

   # Start Neo4j and Redis using Docker Compose
   docker-compose up -d neo4j redis

   # Verify services are running
   docker-compose ps

   # Check logs if needed
   docker-compose logs neo4j redis

Step 4: Configure Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create your local configuration:

.. code-block:: bash

   # Copy example environment file
   cp .env.example .env

   # Edit configuration as needed
   nano .env  # or use your preferred editor

Key configuration options:

.. code-block:: bash

   # Database connections
   TTA_NEO4J_URI=bolt://localhost:7687
   TTA_NEO4J_USER=neo4j
   TTA_NEO4J_PASSWORD=password

   TTA_REDIS_HOST=localhost
   TTA_REDIS_PORT=6379

   # Application settings
   TTA_ENV=development
   TTA_LOG_LEVEL=DEBUG

Step 5: Run Initial Setup
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run the development setup script
   ./scripts/setup_dev_environment.sh

   # This script will:
   # - Validate your environment
   # - Set up pre-commit hooks
   # - Initialize databases
   # - Run initial tests

Step 6: Verify Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Test Python imports
   uv run python -c "import src; print('✓ TTA imports working')"

   # Run quick tests
   uv run pytest tests/unit/ -v --tb=short

   # Start the development server
   uv run python src/main.py

   # In another terminal, test the API
   curl http://localhost:8000/health

Development Workflow
--------------------

Daily Development Routine
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Start your development session:**

.. code-block:: bash

   # Pull latest changes
   git pull origin main

   # Start services
   docker-compose up -d

   # Activate environment
   source .venv/bin/activate

2. **Create a feature branch:**

.. code-block:: bash

   # Create and switch to feature branch
   git checkout -b feature/your-feature-name

3. **Make your changes and test:**

.. code-block:: bash

   # Run tests frequently
   uv run pytest tests/ -x  # Stop on first failure

   # Run specific test files
   uv run pytest tests/components/test_my_component.py -v

4. **Commit your changes:**

.. code-block:: bash

   # Stage changes
   git add .

   # Commit with conventional commit message
   git commit -m "feat: add new therapeutic assessment component"

5. **Push and create PR:**

.. code-block:: bash

   # Push to your fork
   git push fork feature/your-feature-name

   # Create PR through GitHub interface

Code Quality Standards
~~~~~~~~~~~~~~~~~~~~~

The project uses several tools to maintain code quality:

**Formatting and Linting:**

.. code-block:: bash

   # Format code with Black
   uv run black src/ tests/

   # Sort imports with isort
   uv run isort src/ tests/

   # Lint with Ruff
   uv run ruff check src/ tests/

   # Type checking with MyPy
   uv run mypy src/

**Pre-commit Hooks:**

The project uses pre-commit hooks to automatically check code quality:

.. code-block:: bash

   # Install pre-commit hooks (done by setup script)
   pre-commit install

   # Run hooks manually
   pre-commit run --all-files

**Testing Standards:**

.. code-block:: bash

   # Run all tests
   uv run pytest tests/

   # Run with coverage
   uv run pytest tests/ --cov=src --cov-report=html

   # Run specific test categories
   uv run pytest tests/ -m "not integration"  # Unit tests only
   uv run pytest tests/ --neo4j  # Neo4j integration tests
   uv run pytest tests/ --redis  # Redis integration tests

Understanding the Codebase
--------------------------

Project Structure
~~~~~~~~~~~~~~~~

.. code-block:: text

   TTA/
   ├── src/                          # Main source code
   │   ├── agent_orchestration/      # AI agent management
   │   ├── api_gateway/              # API routing and management
   │   ├── components/               # Reusable components
   │   ├── orchestration/            # System orchestration
   │   └── player_experience/        # User-facing functionality
   ├── tests/                        # Test suite
   │   ├── unit/                     # Unit tests
   │   ├── integration/              # Integration tests
   │   └── fixtures/                 # Test fixtures
   ├── docs/                         # Documentation
   ├── scripts/                      # Development scripts
   ├── config/                       # Configuration files
   └── docker-compose.yml            # Development services

Key Components
~~~~~~~~~~~~~

**Agent Orchestration** (``src/agent_orchestration/``)
   Manages AI agents, workflows, and inter-agent communication.

**Player Experience** (``src/player_experience/``)
   Handles user interactions, game state, and therapeutic interventions.

**API Gateway** (``src/api_gateway/``)
   Routes requests, handles authentication, and manages rate limiting.

**Components** (``src/components/``)
   Reusable system components like database connections and LLM interfaces.

Making Your First Contribution
------------------------------

Let's create a simple feature to get familiar with the development process.

Example: Adding a Health Check Endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Create the endpoint:**

.. code-block:: python

   # src/player_experience/api/routers/system.py
   from fastapi import APIRouter
   from datetime import datetime
   import psutil

   router = APIRouter(prefix="/api/v1/system", tags=["system"])

   @router.get("/health/detailed")
   async def detailed_health_check():
       """Get detailed system health information."""
       return {
           "status": "healthy",
           "timestamp": datetime.utcnow().isoformat(),
           "system": {
               "cpu_percent": psutil.cpu_percent(),
               "memory_percent": psutil.virtual_memory().percent,
               "disk_percent": psutil.disk_usage('/').percent
           }
       }

2. **Add tests:**

.. code-block:: python

   # tests/api/test_system_router.py
   import pytest
   from fastapi.testclient import TestClient
   from src.player_experience.api.app import app

   client = TestClient(app)

   def test_detailed_health_check():
       """Test detailed health check endpoint."""
       response = client.get("/api/v1/system/health/detailed")

       assert response.status_code == 200
       data = response.json()

       assert data["status"] == "healthy"
       assert "timestamp" in data
       assert "system" in data
       assert "cpu_percent" in data["system"]

3. **Register the router:**

.. code-block:: python

   # src/player_experience/api/app.py
   from .routers.system import router as system_router

   app.include_router(system_router)

4. **Test your changes:**

.. code-block:: bash

   # Run the specific test
   uv run pytest tests/api/test_system_router.py -v

   # Start the server and test manually
   uv run python src/main.py &
   curl http://localhost:8000/api/v1/system/health/detailed

5. **Commit and push:**

.. code-block:: bash

   git add .
   git commit -m "feat: add detailed system health check endpoint"
   git push fork feature/detailed-health-check

Common Development Tasks
-----------------------

Running Tests
~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   uv run pytest

   # Run specific test file
   uv run pytest tests/components/test_neo4j_component.py

   # Run tests matching pattern
   uv run pytest -k "test_health"

   # Run with coverage
   uv run pytest --cov=src --cov-report=term-missing

Debugging
~~~~~~~~

.. code-block:: bash

   # Run with debugger
   uv run pytest tests/test_file.py::test_function --pdb

   # Enable debug logging
   TTA_LOG_LEVEL=DEBUG uv run python src/main.py

Database Operations
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Connect to Neo4j
   docker exec -it tta_neo4j_1 cypher-shell -u neo4j -p password

   # Connect to Redis
   docker exec -it tta_redis_1 redis-cli

   # Reset databases
   docker-compose down -v
   docker-compose up -d

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

**Import Errors**
   - Ensure virtual environment is activated
   - Check PYTHONPATH includes src directory
   - Verify all dependencies are installed

**Database Connection Issues**
   - Check Docker containers are running: ``docker-compose ps``
   - Verify connection strings in ``.env`` file
   - Check firewall settings

**Test Failures**
   - Run tests with ``-v`` flag for verbose output
   - Check test database is clean
   - Ensure all fixtures are properly set up

**Performance Issues**
   - Use profiling tools to identify bottlenecks
   - Check database query performance
   - Monitor memory usage during development

Getting Help
-----------

When you need assistance:

1. **Documentation**: Check this documentation first
2. **Code Examples**: Look at existing similar implementations
3. **GitHub Issues**: Search for existing issues
4. **Discussions**: Use GitHub Discussions for questions
5. **Code Review**: Ask for feedback in pull requests

Next Steps
----------

Now that you have your development environment set up:

1. Explore the :doc:`creating-components` tutorial
2. Learn about :doc:`api-development` patterns
3. Read the :doc:`testing-guide` for best practices
4. Check out the :doc:`deployment-guide` for production deployment

Happy coding! 🚀
