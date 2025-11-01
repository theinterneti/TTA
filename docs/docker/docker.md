# Docker Component

The Docker Component ensures Docker configurations are consistent across repositories. It provides methods for standardizing container names, environment variables, and services.

## Overview

The TTA project uses Docker to containerize its components. The Docker Component helps ensure that Docker configurations are consistent across the tta.dev and tta.prototype repositories. It provides methods for standardizing container names, environment variables, and services.

## Configuration

The Docker Component is configured in the `config/tta_config.yaml` file:

```yaml
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
```

### Configuration Options

- `enabled`: Whether the Docker component is enabled
- `use_gpu`: Whether to use GPU acceleration
- `compose_profiles`: Docker Compose profiles to use
- `standardize_container_names`: Whether to standardize container names
- `ensure_consistent_extensions`: Whether to ensure consistent VS Code extensions
- `ensure_consistent_env_vars`: Whether to ensure consistent environment variables
- `ensure_consistent_services`: Whether to ensure consistent Docker Compose services

## Usage

### Using the Docker Component

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

### Using the Docker Component from the Command Line

You can also use the Docker Component from the command line using the TTA Orchestrator:

```bash
# Start the Docker component
python src/main.py start docker

# Run Docker Compose command in both repositories
python src/main.py docker compose up -d

# Run Docker Compose command in a specific repository
python src/main.py docker compose up -d --repository tta.dev
```

## Docker Consistency

The Docker Component ensures consistency across repositories by:

1. **Checking Docker Files**: Ensures that both repositories have the necessary Docker files (Dockerfile, docker-compose.yml, devcontainer.json)
2. **Copying Template Files**: Copies template files from the templates directory if they don't exist in the repositories
3. **Standardizing Container Names**: Ensures that container names follow a consistent naming convention
4. **Ensuring Consistent VS Code Extensions**: Ensures that both repositories have the same VS Code extensions in their devcontainer.json files
5. **Ensuring Consistent Environment Variables**: Ensures that both repositories have the same environment variables in their .env.example files
6. **Ensuring Consistent Docker Compose Services**: Ensures that both repositories have the same Docker Compose services

## Docker Templates

The Docker Component uses templates from the `templates` directory to ensure consistency across repositories. The templates are located in:

- `templates/tta.dev/Dockerfile`
- `templates/tta.dev/docker-compose.yml`
- `templates/tta.dev/.devcontainer/devcontainer.json`
- `templates/tta.prototype/Dockerfile`
- `templates/tta.prototype/docker-compose.yml`
- `templates/tta.prototype/.devcontainer/devcontainer.json`

## Docker Compose Profiles

The Docker Component supports Docker Compose profiles, which allow you to start only a subset of services. The profiles are configured in the `docker.compose_profiles` configuration option.

For example, to start only the services in the `with-jupyter` profile:

```bash
python src/main.py docker compose up -d --profile with-jupyter
```

## GPU Acceleration

The Docker Component supports GPU acceleration for Docker containers. To enable GPU acceleration, set the `docker.use_gpu` configuration option to `true`.

When GPU acceleration is enabled, the Docker Component will add the necessary configuration to the Docker Compose files to enable GPU access in the containers.

## Best Practices

- Use the Docker Component to ensure consistency across repositories
- Use Docker Compose profiles to start only the services you need
- Use the templates directory to maintain consistent Docker configurations
- Use the `docker.use_gpu` option to enable GPU acceleration when needed

## Troubleshooting

If you encounter issues with the Docker Component, check the following:

- Make sure Docker is installed and running
- Check the logs for any error messages
- Verify that the template files exist in the templates directory
- Try running the Docker commands manually to see if there are any errors

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [VS Code DevContainer Documentation](https://code.visualstudio.com/docs/remote/containers)
- [Docker Component Source Code](../../src/components/docker_component.py)
