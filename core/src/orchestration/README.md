# TTA Orchestration Module

This module provides orchestration capabilities for the TTA project, coordinating both tta.dev and tta.prototype components.

## Overview

The TTA Orchestration Module is designed to:

1. Provide a unified interface for starting, stopping, and managing components
2. Handle dependencies between components
3. Provide configuration management across repositories
4. Support both development and production environments

## Components

The module is built around the concept of "components", which are individual pieces of functionality that can be started, stopped, and managed independently. Components can have dependencies on other components, which are automatically handled by the orchestrator.

## Usage

### Command Line Interface

The orchestration module provides a command-line interface through the `src/main.py` script:

```bash
# Start all components
python src/main.py start

# Start specific components
python src/main.py start neo4j llm

# Stop all components
python src/main.py stop

# Stop specific components
python src/main.py stop neo4j llm

# Restart all components
python src/main.py restart

# Restart specific components
python src/main.py restart neo4j llm

# Get status of all components
python src/main.py status

# Get status of specific components
python src/main.py status neo4j llm

# Run Docker Compose command in both repositories
python src/main.py docker compose up -d

# Run Docker Compose command in a specific repository
python src/main.py docker compose up -d --repository tta.dev

# Get configuration value
python src/main.py config get tta.dev.enabled

# Set configuration value
python src/main.py config set tta.dev.enabled true

# Save configuration
python src/main.py config save
```

### Python API

The orchestration module can also be used as a Python API:

```python
from src.orchestration import TTAOrchestrator

# Create the orchestrator
orchestrator = TTAOrchestrator()

# Start all components
orchestrator.start_all()

# Start a specific component
orchestrator.start_component('neo4j')

# Stop all components
orchestrator.stop_all()

# Stop a specific component
orchestrator.stop_component('neo4j')

# Get status of a specific component
status = orchestrator.get_component_status('neo4j')

# Get status of all components
statuses = orchestrator.get_all_statuses()

# Run Docker Compose command
results = orchestrator.run_docker_compose_command(['up', '-d'], 'both')
```

## Configuration

The orchestration module uses a YAML configuration file by default, located at `config/tta_config.yaml`. The configuration can be overridden using environment variables with the format `TTA_SECTION_KEY=value`, e.g., `TTA_TTADEV_ENABLED=true`.

## Adding New Components

To add a new component, create a new Python file in the `src/components` directory of either the tta.dev or tta.prototype repository. The file should define a class that inherits from `Component` and implements the `_start_impl` and `_stop_impl` methods.

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
