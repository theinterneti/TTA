# TTA Source Code

This directory contains the source code for the TTA project.

## Directory Structure

- **orchestration**: Orchestration module for coordinating tta.dev and tta.prototype components
- **components**: Component implementations for the TTA project

## Main Script

The `main.py` script provides a command-line interface for the TTA Orchestrator:

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

## Adding New Components

To add a new component, create a new Python file in the `components` directory. The file should define a class that inherits from `Component` and implements the `_start_impl` and `_stop_impl` methods.

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
