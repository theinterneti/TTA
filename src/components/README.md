# TTA Components

This directory contains component implementations for the TTA project.

## Overview

Components are individual pieces of functionality that can be started, stopped, and managed independently. Components can have dependencies on other components, which are automatically handled by the orchestrator.

## Available Components

### Neo4j Component

The Neo4j component manages the Neo4j database for both tta.dev and tta.prototype repositories. It uses Docker Compose to start and stop the Neo4j container.

### LLM Component

The LLM component manages the LLM service for the tta.dev repository. It uses Docker Compose to start and stop the LLM container.

### App Component

The App component manages the main application for the tta.prototype repository. It uses Docker Compose to start and stop the app container.

## Creating New Components

To create a new component, create a new Python file in this directory. The file should define a class that inherits from `Component` and implements the `_start_impl` and `_stop_impl` methods.

Example:

```python
from src.orchestration.component import Component, ComponentStatus

class MyComponent(Component):
    def __init__(self, config):
        super().__init__(config, name="my_component", dependencies=["neo4j"])

    def _start_impl(self):
        # Implement component-specific start logic
        return True

    def _stop_impl(self):
        # Implement component-specific stop logic
        return True
```

The component will be automatically discovered and registered with the orchestrator.
