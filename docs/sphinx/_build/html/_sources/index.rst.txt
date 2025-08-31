TTA - Therapeutic Text Adventure Documentation
==============================================

Welcome to the comprehensive documentation for the **Therapeutic Text Adventure (TTA)** platform. TTA is an innovative therapeutic platform that combines interactive storytelling with evidence-based therapeutic interventions to provide personalized mental health support.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   getting-started
   architecture
   api/modules
   development/index
   testing/index
   deployment/index
   contributing

Quick Start
-----------

To get started with TTA development:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/theinterneti/TTA.git
   cd TTA

   # Set up development environment
   ./scripts/setup_dev_environment.sh

   # Run tests
   uv run pytest tests/

   # Start the application
   uv run python src/main.py

Key Features
------------

🎭 **Interactive Storytelling**
   Dynamic narrative generation with therapeutic integration

🧠 **AI-Powered Agents**
   Sophisticated agent orchestration for personalized experiences

🛡️ **Therapeutic Safety**
   Built-in safety mechanisms and crisis intervention protocols

📊 **Real-time Analytics**
   Comprehensive monitoring and performance tracking

🔧 **Modular Architecture**
   Scalable, maintainable component-based design

Architecture Overview
---------------------

TTA is built with a modern, scalable architecture:

.. mermaid::

   graph TB
       A[Player Experience API] --> B[API Gateway]
       B --> C[Agent Orchestration]
       C --> D[Therapeutic Safety]
       C --> E[Session Management]
       C --> F[Crisis Detection]

       G[Neo4j Database] --> C
       H[Redis Cache] --> C
       I[External APIs] --> C

       J[Monitoring] --> C
       K[Logging] --> C

Core Components
---------------

Agent Orchestration
~~~~~~~~~~~~~~~~~~~

The heart of TTA's intelligent behavior, managing multiple AI agents that work together to provide therapeutic support.

.. automodule:: agent_orchestration
   :members:
   :undoc-members:
   :show-inheritance:

Therapeutic Safety
~~~~~~~~~~~~~~~~~~

Critical safety mechanisms ensuring user wellbeing and crisis intervention capabilities.

.. automodule:: components.therapeutic_safety
   :members:
   :undoc-members:
   :show-inheritance:

Player Experience API
~~~~~~~~~~~~~~~~~~~~~

RESTful API providing the interface for client applications to interact with the TTA platform.

.. automodule:: player_experience.api
   :members:
   :undoc-members:
   :show-inheritance:

Development Workflow
--------------------

TTA follows modern development practices:

1. **Code Quality**: Pre-commit hooks with black, ruff, mypy, and bandit
2. **Testing**: Three-tier test structure (unit, Neo4j, Redis integration)
3. **Coverage**: Comprehensive coverage reporting with quality gates
4. **Documentation**: Automated API documentation generation
5. **CI/CD**: GitHub Actions with quality enforcement

Testing
-------

TTA uses a comprehensive three-tier testing approach:

.. code-block:: bash

   # Unit tests (fast, no external dependencies)
   uv run pytest tests/

   # Neo4j integration tests
   uv run pytest tests/ --neo4j

   # Redis integration tests
   uv run pytest tests/ --redis

   # Full integration tests
   uv run pytest tests/ --neo4j --redis

API Reference
-------------

Complete API documentation is available in the :doc:`api/modules` section, automatically generated from source code docstrings.

Contributing
------------

We welcome contributions! Please see our :doc:`contributing` guide for details on:

- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

Support
-------

- **Documentation**: This comprehensive guide
- **Issues**: `GitHub Issues <https://github.com/theinterneti/TTA/issues>`_
- **Discussions**: `GitHub Discussions <https://github.com/theinterneti/TTA/discussions>`_

License
-------

TTA is released under the MIT License. See the `LICENSE <https://github.com/theinterneti/TTA/blob/main/LICENSE>`_ file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
