# Jupyter Environment

This document provides detailed information about the Jupyter environment configuration for the TTA project.

## Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Features](#features)
- [Usage](#usage)
- [Customization](#customization)
- [Best Practices](#best-practices)

## Overview

The Jupyter environment extends the development environment with a Jupyter notebook server for interactive development and experimentation.

## Configuration

The Jupyter environment is configured in `docker-compose.dev.yml` with the `with-jupyter` profile:

```yaml
# Development-specific services
jupyter:
  build:
    context: .
    dockerfile: Dockerfile
    target: development
  container_name: tta-jupyter
  volumes:
    - .:/app:delegated
    - venv-data:/app/.venv
    - huggingface-cache:/root/.cache/huggingface
    - model-cache:/app/.model_cache
    - ./data:/app/external_data:delegated
    - ./notebooks:/app/notebooks:delegated
  environment:
    - PYTHONPATH=/app
    - VIRTUAL_ENV=/app/.venv
    - PATH=/app/.venv/bin:$PATH
    - CODECARBON_LOG_LEVEL=DEBUG
    - CODECARBON_OUTPUT_DIR=/app/logs/codecarbon
  command: jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
  ports:
    - "8888:8888"
  networks:
    - tta-network
  depends_on:
    app:
      condition: service_healthy
  profiles: ["with-jupyter"]
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:8888 || exit 1"]
    interval: 10s
    timeout: 5s
    retries: 3
    start_period: 10s
```

## Features

### Jupyter Notebook Server

The Jupyter environment includes a Jupyter notebook server with:

- **Web Interface**: Access notebooks through a web browser
- **Python Kernel**: Python kernel for executing Python code
- **Interactive Development**: Interactive development and experimentation
- **Visualization**: Rich visualization capabilities

### Volume Mounts

The Jupyter environment mounts several volumes:

- `.:/app:delegated`: The project root directory
- `venv-data:/app/.venv`: Python virtual environment
- `huggingface-cache:/root/.cache/huggingface`: Hugging Face model cache
- `model-cache:/app/.model_cache`: Custom model cache
- `./data:/app/external_data:delegated`: Data directory
- `./notebooks:/app/notebooks:delegated`: Jupyter notebooks

### Environment Variables

The Jupyter environment sets several environment variables:

- `PYTHONPATH=/app`: Python module search path
- `VIRTUAL_ENV=/app/.venv`: Python virtual environment path
- `PATH=/app/.venv/bin:$PATH`: Path to include virtual environment binaries
- `CODECARBON_LOG_LEVEL=DEBUG`: CodeCarbon logging level
- `CODECARBON_OUTPUT_DIR=/app/logs/codecarbon`: CodeCarbon output directory

## Usage

### Starting the Jupyter Environment

To start the Jupyter environment:

```bash
./scripts/orchestrate.sh start jupyter
```

Or with Docker Compose directly:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile with-jupyter up -d
```

### Accessing the Jupyter Notebook Server

Once the Jupyter environment is running, you can access the Jupyter notebook server at:

```
http://localhost:8888
```

The server is configured without authentication for local development. In a production environment, you should enable authentication.

### Creating a New Notebook

To create a new notebook:

1. Navigate to http://localhost:8888
2. Click "New" > "Python 3" to create a new Python notebook
3. Start writing and executing code

### Using Existing Notebooks

Notebooks are stored in the `./notebooks` directory. To use an existing notebook:

1. Navigate to http://localhost:8888
2. Browse to the notebook file
3. Click on the notebook to open it

### Importing Project Modules

You can import project modules in your notebooks:

```python
# Import project modules
import tta
from tta import models, utils

# Use project modules
model = models.load_model("my_model")
```

## Customization

### Installing Additional Packages

To install additional packages in the Jupyter environment:

1. Connect to the Jupyter container:
   ```bash
   ./scripts/orchestrate.sh exec jupyter bash
   ```

2. Install the package:
   ```bash
   pip install package-name
   ```

3. Update the requirements.txt file:
   ```bash
   pip freeze > /app/requirements.txt
   ```

### Configuring Jupyter

To customize the Jupyter configuration:

1. Create a custom Jupyter configuration file:
   ```bash
   ./scripts/orchestrate.sh exec jupyter jupyter notebook --generate-config
   ```

2. Edit the configuration file:
   ```bash
   ./scripts/orchestrate.sh exec jupyter vi /root/.jupyter/jupyter_notebook_config.py
   ```

3. Update the command in `docker-compose.dev.yml`:
   ```yaml
   command: jupyter notebook --config=/root/.jupyter/jupyter_notebook_config.py
   ```

### Adding Jupyter Extensions

To add Jupyter extensions:

1. Install the extension:
   ```bash
   ./scripts/orchestrate.sh exec jupyter pip install jupyter_contrib_nbextensions
   ```

2. Enable the extension:
   ```bash
   ./scripts/orchestrate.sh exec jupyter jupyter contrib nbextension install --user
   ```

3. Enable specific extensions:
   ```bash
   ./scripts/orchestrate.sh exec jupyter jupyter nbextension enable extension_name/main
   ```

## Best Practices

### Notebook Organization

- **Use Descriptive Names**: Give notebooks descriptive names
- **Create Subdirectories**: Organize notebooks in subdirectories by purpose
- **Include Documentation**: Add markdown cells to document the notebook

### Code Quality

- **Use Relative Imports**: Use relative imports for project modules
- **Clean Up Resources**: Close file handles and release resources
- **Handle Exceptions**: Use try/except blocks to handle exceptions

### Performance

- **Limit Data Size**: Limit the amount of data loaded into memory
- **Use Efficient Operations**: Use vectorized operations when possible
- **Monitor Memory Usage**: Monitor memory usage with `%memit` magic

### Version Control

- **Clear Output**: Clear output cells before committing to version control
- **Use .gitignore**: Add `.ipynb_checkpoints` to .gitignore
- **Consider nbdime**: Use nbdime for notebook diffing and merging

For more information about Docker and container setup, see the [Docker Setup Guide](../README.md).
