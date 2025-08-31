Testing Documentation
=====================

Comprehensive testing documentation for the TTA platform.

.. toctree::
   :maxdepth: 2
   :caption: Testing Guides:

   overview
   patterns
   fixtures
   coverage

Testing Overview
----------------

TTA uses a comprehensive three-tier testing approach:

**Tier 1: Unit Tests**
   Fast tests with no external dependencies

**Tier 2: Integration Tests**
   Tests with Neo4j or Redis databases

**Tier 3: End-to-End Tests**
   Full system integration tests

Running Tests
-------------

.. code-block:: bash

   # Unit tests only
   uv run pytest tests/ -k "not integration"

   # Neo4j integration tests
   uv run pytest tests/ --neo4j

   # Redis integration tests
   uv run pytest tests/ --redis

   # All tests
   uv run pytest tests/ --neo4j --redis

Coverage Reporting
------------------

.. code-block:: bash

   # Generate coverage report
   uv run pytest tests/ --cov=src --cov-report=html

   # View coverage in browser
   open htmlcov/index.html

Quality Gates
-------------

- **Minimum Coverage**: 70%
- **Target Coverage**: 80%
- **Critical Modules**: 90%+ coverage required

For detailed testing information, see the comprehensive guides in the ``docs/testing/`` directory.
