# TTA Components

This directory contains documentation for the TTA components.

## Overview

The TTA project is built around the concept of "components", which are individual pieces of functionality that can be started, stopped, and managed independently. Components can have dependencies on other components, which are automatically handled by the orchestrator.

## Available Components

### Neo4j Component

The Neo4j component manages the Neo4j database for both tta.dev and tta.prototype repositories. It uses Docker Compose to start and stop the Neo4j container.

```python
from src.orchestration import TTAConfig
from src.components import Neo4jComponent

# Create a configuration object
config = TTAConfig()

# Create a Neo4j component
neo4j = Neo4jComponent(config, repository="tta.dev")

# Start the Neo4j component
neo4j.start()

# Stop the Neo4j component
neo4j.stop()
```

### LLM Component

The LLM component manages the LLM service for the tta.dev repository. It uses Docker Compose to start and stop the LLM container.

```python
from src.orchestration import TTAConfig
from src.components import LLMComponent

# Create a configuration object
config = TTAConfig()

# Create an LLM component
llm = LLMComponent(config, repository="tta.dev")

# Start the LLM component
llm.start()

# Stop the LLM component
llm.stop()
```

### App Component

The App component manages the TTA.prototype app. It uses Docker Compose to start and stop the app container.

```python
from src.orchestration import TTAConfig
from src.components import AppComponent

# Create a configuration object
config = TTAConfig()

# Create an App component
app = AppComponent(config)

# Start the App component
app.start()

# Stop the App component
app.stop()
```

### Docker Component

The Docker component ensures Docker configurations are consistent across repositories. It provides methods for standardizing container names, environment variables, and services.

```python
from src.orchestration import TTAConfig
from src.components import DockerComponent

# Create a configuration object
config = TTAConfig()

# Create a Docker component
docker = DockerComponent(config)

# Start the Docker component (standardize configurations)
docker.start()

# Ensure Docker consistency across repositories
docker.ensure_consistency()
```

### Carbon Component

The Carbon component provides methods for tracking carbon emissions of functions and components using the codecarbon library.

```python
from src.orchestration import TTAConfig
from src.components import CarbonComponent

# Create a configuration object
config = TTAConfig()

# Create a Carbon component
carbon = CarbonComponent(config)

# Start the Carbon component
carbon.start()

# Track emissions for a specific function
emissions = carbon.track_function(my_function, *args, **kwargs)

# Get emissions report
report = carbon.get_emissions_report()

# Stop the Carbon component
carbon.stop()
```

## Adding a New Component

To add a new component, create a new Python file in the `src/components` directory. The file should define a class that inherits from `Component` and implements the `_start_impl` and `_stop_impl` methods.

Example:

```python
from src.orchestration.component import Component, ComponentStatus

class MyComponent(Component):
    def __init__(self, config):
        super().__init__(config, name="my_component", dependencies=["neo4j"])
    
    def _start_impl(self) -> bool:
        # Implement component-specific start logic
        return True
    
    def _stop_impl(self) -> bool:
        # Implement component-specific stop logic
        return True
```

The component will be automatically discovered and registered with the orchestrator.

## Configuration

Components are configured using the `TTAConfig` class. The configuration is loaded from the `config/tta_config.yaml` file.

Example configuration:

```yaml
# TTA Configuration File

# TTA.dev Repository Configuration
tta.dev:
  enabled: true
  components:
    neo4j:
      enabled: true
      port: 7687
      username: neo4j
      password: password
    llm:
      enabled: true
      model: qwen2.5-7b-instruct
      api_base: http://localhost:1234/v1

# TTA.prototype Repository Configuration
tta.prototype:
  enabled: true
  components:
    neo4j:
      enabled: true
      port: 7688
      username: neo4j
      password: password
    app:
      enabled: true
      port: 8501

# Docker Configuration
docker:
  enabled: true
  use_gpu: false
  compose_profiles:
    - default
  standardize_container_names: true
  ensure_consistent_extensions: true
  ensure_consistent_env_vars: true
  ensure_consistent_services: true

# Carbon Tracking Configuration
carbon:
  enabled: true
  project_name: TTA
  output_dir: logs/codecarbon
  log_level: info
  measurement_interval: 15
  track_components: true

# Environment Configuration
environment:
  name: development
  log_level: info
```
