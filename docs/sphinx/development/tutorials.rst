Development Tutorials
=====================

Step-by-step tutorials for developing with the TTA platform.

.. toctree::
   :maxdepth: 2
   :caption: Tutorial Topics:

   tutorials/getting-started
   tutorials/creating-components
   tutorials/api-development
   tutorials/testing-guide
   tutorials/deployment-guide

Quick Start Tutorial
--------------------

This tutorial will get you up and running with TTA development in 15 minutes.

Prerequisites
~~~~~~~~~~~~~

- Python 3.11+
- Git
- Docker (optional, for databases)
- uv package manager

Step 1: Clone and Setup
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/theinterneti/TTA.git
   cd TTA

   # Run the setup script
   ./scripts/setup_dev_environment.sh

   # Verify installation
   uv run python -c "import src; print('TTA setup successful!')"

Step 2: Start Development Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start databases (optional)
   docker-compose up -d neo4j redis

   # Start the development server
   uv run python src/main.py

Step 3: Run Your First Test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run unit tests
   uv run pytest tests/ -v

   # Run with coverage
   uv run pytest tests/ --cov=src --cov-report=html

Step 4: Make Your First Change
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create a new branch:

.. code-block:: bash

   git checkout -b feature/my-first-change

2. Edit a file (e.g., add a simple function):

.. code-block:: python

   # src/utils/hello.py
   def say_hello(name: str) -> str:
       """Say hello to someone."""
       return f"Hello, {name}!"

3. Add a test:

.. code-block:: python

   # tests/utils/test_hello.py
   from src.utils.hello import say_hello

   def test_say_hello():
       assert say_hello("World") == "Hello, World!"

4. Run tests and commit:

.. code-block:: bash

   uv run pytest tests/utils/test_hello.py
   git add .
   git commit -m "feat: add hello function"

Congratulations! You've made your first contribution to TTA.

Next Steps
~~~~~~~~~~

- Read the :doc:`creating-components` tutorial
- Explore the :doc:`api-development` guide
- Learn about :doc:`testing-guide` best practices
- Check out the :doc:`deployment-guide` for production deployment

Common Development Tasks
------------------------

Adding a New Component
~~~~~~~~~~~~~~~~~~~~~~

Components are the building blocks of TTA. Here's how to create one:

1. **Create the component structure:**

.. code-block:: bash

   mkdir -p src/components/my_component
   touch src/components/my_component/__init__.py
   touch src/components/my_component/component.py
   touch src/components/my_component/models.py

2. **Implement the component:**

.. code-block:: python

   # src/components/my_component/component.py
   from src.orchestration.component import Component
   from typing import Dict, Any

   class MyComponent(Component):
       """My custom component."""

       def __init__(self, config: Dict[str, Any]):
           super().__init__("my_component", config)

       async def start(self) -> None:
           """Start the component."""
           self.logger.info("Starting MyComponent")
           # Component initialization logic here

       async def stop(self) -> None:
           """Stop the component."""
           self.logger.info("Stopping MyComponent")
           # Component cleanup logic here

       async def health_check(self) -> bool:
           """Check component health."""
           return True

3. **Add tests:**

.. code-block:: python

   # tests/components/test_my_component.py
   import pytest
   from src.components.my_component.component import MyComponent

   @pytest.fixture
   def component():
       return MyComponent({"test": True})

   @pytest.mark.asyncio
   async def test_component_lifecycle(component):
       await component.start()
       assert await component.health_check()
       await component.stop()

Creating API Endpoints
~~~~~~~~~~~~~~~~~~~~~~

TTA uses FastAPI for its REST API. Here's how to add new endpoints:

1. **Create a router:**

.. code-block:: python

   # src/player_experience/api/routers/my_router.py
   from fastapi import APIRouter, HTTPException
   from pydantic import BaseModel
   from typing import List

   router = APIRouter(prefix="/api/v1/my-resource", tags=["my-resource"])

   class MyResource(BaseModel):
       id: str
       name: str
       description: str

   @router.get("/", response_model=List[MyResource])
   async def list_resources():
       """List all resources."""
       return []

   @router.post("/", response_model=MyResource)
   async def create_resource(resource: MyResource):
       """Create a new resource."""
       # Implementation here
       return resource

2. **Register the router:**

.. code-block:: python

   # src/player_experience/api/app.py
   from .routers.my_router import router as my_router

   app.include_router(my_router)

3. **Add tests:**

.. code-block:: python

   # tests/api/test_my_router.py
   from fastapi.testclient import TestClient
   from src.player_experience.api.app import app

   client = TestClient(app)

   def test_list_resources():
       response = client.get("/api/v1/my-resource/")
       assert response.status_code == 200
       assert response.json() == []

Working with Databases
~~~~~~~~~~~~~~~~~~~~~~

TTA uses Neo4j for graph data and Redis for caching:

1. **Neo4j queries:**

.. code-block:: python

   # src/database/my_queries.py
   from src.components.neo4j_component import Neo4jComponent

   class MyQueries:
       def __init__(self, neo4j: Neo4jComponent):
           self.neo4j = neo4j

       async def create_node(self, name: str) -> str:
           """Create a new node."""
           query = """
           CREATE (n:MyNode {name: $name, created_at: datetime()})
           RETURN n.name as name
           """
           result = await self.neo4j.execute_query(query, name=name)
           return result[0]["name"]

2. **Redis caching:**

.. code-block:: python

   # src/services/my_cache.py
   import json
   from typing import Optional, Any
   from src.components.redis_component import RedisComponent

   class MyCache:
       def __init__(self, redis: RedisComponent):
           self.redis = redis

       async def get(self, key: str) -> Optional[Any]:
           """Get value from cache."""
           value = await self.redis.get(key)
           return json.loads(value) if value else None

       async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
           """Set value in cache."""
           await self.redis.set(key, json.dumps(value), ex=ttl)

Debugging and Troubleshooting
------------------------------

Common Issues
~~~~~~~~~~~~~

**Import Errors**
   Make sure you're using relative imports and the Python path is correct:

.. code-block:: bash

   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

**Database Connection Issues**
   Check that services are running:

.. code-block:: bash

   docker-compose ps
   # Restart if needed
   docker-compose restart neo4j redis

**Test Failures**
   Run tests with verbose output:

.. code-block:: bash

   uv run pytest tests/ -v --tb=short

Debugging Tools
~~~~~~~~~~~~~~~

1. **Use the debugger:**

.. code-block:: python

   import pdb; pdb.set_trace()  # Add breakpoint
   # Or use ipdb for better experience
   import ipdb; ipdb.set_trace()

2. **Enable debug logging:**

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.DEBUG)

3. **Use pytest debugging:**

.. code-block:: bash

   uv run pytest tests/test_file.py::test_function -s --pdb

Performance Profiling
~~~~~~~~~~~~~~~~~~~~~~

Profile your code to identify bottlenecks:

.. code-block:: python

   import cProfile
   import pstats

   def profile_function():
       # Your code here
       pass

   cProfile.run('profile_function()', 'profile_stats')
   stats = pstats.Stats('profile_stats')
   stats.sort_stats('cumulative').print_stats(10)

Best Practices
--------------

Code Organization
~~~~~~~~~~~~~~~~~

- Keep components focused and single-purpose
- Use dependency injection for better testability
- Follow the existing project structure
- Write comprehensive docstrings

Error Handling
~~~~~~~~~~~~~~

- Use specific exception types
- Log errors with context
- Provide meaningful error messages
- Handle edge cases gracefully

Testing
~~~~~~~

- Write tests before implementing features (TDD)
- Use fixtures for common test setup
- Mock external dependencies
- Test both happy path and error cases

Documentation
~~~~~~~~~~~~~

- Document all public APIs
- Include usage examples
- Keep documentation up to date
- Use type hints consistently

Getting Help
------------

If you need help:

1. **Check the documentation** - Most questions are answered here
2. **Search existing issues** - Someone might have had the same problem
3. **Ask in discussions** - Use GitHub Discussions for questions
4. **Create an issue** - For bugs or feature requests

Resources
---------

- :doc:`../api/modules` - Complete API reference
- :doc:`../testing/index` - Testing documentation
- :doc:`../deployment/index` - Deployment guides
- `GitHub Repository <https://github.com/theinterneti/TTA>`_ - Source code and issues
