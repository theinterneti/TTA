# OpenHands Integration with TTA Test Generation Pipeline

This document describes how to integrate the OpenHands Docker-based execution engine with the TTA (Test-Driven Architecture) test generation pipeline.

## Overview

The OpenHands integration provides:
- **Automated test generation** using LLM-powered agents
- **Docker-based execution** for isolated, reproducible environments
- **Error recovery** with automatic model rotation and retry logic
- **Batch processing** for multiple modules
- **Performance metrics** collection and monitoring

## Architecture

```
TTA Pipeline
    ↓
[Test Generation Request]
    ↓
OpenHands Integration Layer
    ├─ Configuration Management
    ├─ Model Selection & Rotation
    ├─ Error Recovery
    └─ Metrics Collection
    ↓
Docker OpenHands Client
    ├─ Docker Command Construction
    ├─ Container Execution
    └─ Output Validation
    ↓
OpenRouter LLM API
    ├─ DeepSeek V3 (Primary)
    ├─ Mistral Small (Fallback)
    └─ Llama Scout (Fallback)
    ↓
[Generated Test Files]
```

## Integration Points

### 1. Test Generation Request

**Input:**
```python
{
    "module_path": "src/my_module.py",
    "test_requirements": {
        "coverage_target": 0.85,
        "test_types": ["unit", "integration"],
        "frameworks": ["pytest", "unittest"]
    },
    "workspace": "/path/to/workspace"
}
```

**Processing:**
```python
from agent_orchestration.openhands_integration import DockerOpenHandsClient
from agent_orchestration.openhands_integration.config import OpenHandsIntegrationConfig

# Load configuration
config = OpenHandsIntegrationConfig.from_env()
client = DockerOpenHandsClient(config.to_client_config())

# Generate tests
task = f"""
Generate comprehensive unit tests for the module at {module_path}.
Requirements:
- Target coverage: {coverage_target}%
- Test types: {', '.join(test_types)}
- Frameworks: {', '.join(frameworks)}
- Output: tests/test_*.py files
"""

result = await client.execute_task(
    task_description=task,
    workspace_path=workspace,
    timeout=config.default_timeout_seconds
)
```

### 2. Output Validation

**Expected Output:**
```
Generated test files:
- tests/test_my_module.py (unit tests)
- tests/test_my_module_integration.py (integration tests)
- tests/conftest.py (fixtures and configuration)

Coverage report:
- Line coverage: 87%
- Branch coverage: 82%
- Function coverage: 90%
```

**Validation:**
```python
from agent_orchestration.openhands_integration.result_validator import ResultValidator

validator = ResultValidator()
validation_result = validator.validate_output(
    output=result.output,
    expected_files=["tests/test_*.py"],
    min_coverage=0.85
)

if validation_result.is_valid:
    print("✓ Tests generated successfully")
else:
    print(f"✗ Validation failed: {validation_result.errors}")
```

### 3. Error Handling & Recovery

The integration includes automatic error recovery:

```python
# Error types handled:
# - Connection errors (retry with backoff)
# - Timeout errors (increase timeout, retry)
# - Authentication errors (check API key)
# - Rate limit errors (rotate to fallback model)
# - Validation errors (adjust prompt, retry)

# Recovery strategies:
# 1. Retry with exponential backoff
# 2. Fallback to alternative model
# 3. Mock response (for testing)
# 4. Circuit breaker (prevent cascading failures)
# 5. Escalate to manual review
```

## Implementation Example

### Basic Integration

```python
import asyncio
from pathlib import Path
from agent_orchestration.openhands_integration import DockerOpenHandsClient
from agent_orchestration.openhands_integration.config import OpenHandsIntegrationConfig

async def generate_tests_for_module(module_path: str) -> dict:
    """Generate tests for a single module."""

    # Load configuration
    config = OpenHandsIntegrationConfig.from_env()
    client = DockerOpenHandsClient(config.to_client_config())

    # Create task
    task = f"""
    Generate comprehensive unit tests for: {module_path}

    Requirements:
    - Use pytest framework
    - Target 85% code coverage
    - Include edge cases and error handling
    - Add docstrings to all test functions
    - Output to: tests/test_{Path(module_path).stem}.py
    """

    # Execute task
    result = await client.execute_task(
        task_description=task,
        workspace_path=Path.cwd(),
        timeout=config.default_timeout_seconds
    )

    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time": result.execution_time,
        "metadata": result.metadata
    }

# Usage
if __name__ == "__main__":
    result = asyncio.run(generate_tests_for_module("src/my_module.py"))
    print(f"Success: {result['success']}")
    print(f"Time: {result['execution_time']:.2f}s")
```

### Batch Processing

```python
import asyncio
from pathlib import Path
from agent_orchestration.openhands_integration.task_queue import TaskQueue
from agent_orchestration.openhands_integration.config import OpenHandsIntegrationConfig

async def generate_tests_batch(module_paths: list[str]) -> list[dict]:
    """Generate tests for multiple modules."""

    config = OpenHandsIntegrationConfig.from_env()
    queue = TaskQueue(max_concurrent=3)  # 3 concurrent tasks

    tasks = []
    for module_path in module_paths:
        task = {
            "description": f"Generate tests for {module_path}",
            "module_path": module_path,
            "priority": 1
        }
        tasks.append(queue.enqueue(task))

    results = await asyncio.gather(*tasks)
    return results

# Usage
modules = [
    "src/module_a.py",
    "src/module_b.py",
    "src/module_c.py"
]
results = asyncio.run(generate_tests_batch(modules))
```

### With Metrics Collection

```python
from agent_orchestration.openhands_integration.metrics_collector import MetricsCollector

async def generate_tests_with_metrics(module_path: str):
    """Generate tests and collect metrics."""

    config = OpenHandsIntegrationConfig.from_env()
    client = DockerOpenHandsClient(config.to_client_config())
    metrics = MetricsCollector()

    # Start metrics collection
    metrics.start_task("test_generation")

    try:
        result = await client.execute_task(
            task_description=f"Generate tests for {module_path}",
            workspace_path=Path.cwd(),
            timeout=config.default_timeout_seconds
        )

        # Record metrics
        metrics.record_success(
            task_name="test_generation",
            execution_time=result.execution_time,
            output_size=len(result.output)
        )

        return result

    except Exception as e:
        metrics.record_failure(
            task_name="test_generation",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise

    finally:
        # Get metrics summary
        summary = metrics.get_summary()
        print(f"Metrics: {summary}")
```

## Configuration for TTA Pipeline

### Development Environment

```bash
# .env
OPENROUTER_API_KEY=sk-or-v1-...
OPENHANDS_MODEL=gemini-flash
OPENHANDS_TIMEOUT=300.0
OPENHANDS_ENABLE_CIRCUIT_BREAKER=true
```

### Production Environment

```bash
# .env or CI/CD secrets
OPENROUTER_API_KEY=sk-or-v1-...
OPENHANDS_MODEL=deepseek-v3
OPENHANDS_TIMEOUT=600.0
OPENHANDS_ENABLE_CIRCUIT_BREAKER=true
OPENHANDS_USE_DOCKER_RUNTIME=true
```

## Expected Inputs and Outputs

### Input Format

```python
{
    "module_path": "src/my_module.py",
    "test_requirements": {
        "coverage_target": 0.85,
        "test_types": ["unit", "integration"],
        "frameworks": ["pytest"],
        "include_edge_cases": True,
        "include_error_handling": True
    },
    "workspace": "/path/to/workspace",
    "timeout": 300
}
```

### Output Format

```python
{
    "success": True,
    "generated_files": [
        "tests/test_my_module.py",
        "tests/conftest.py"
    ],
    "coverage": {
        "line": 0.87,
        "branch": 0.82,
        "function": 0.90
    },
    "execution_time": 45.2,
    "model_used": "openrouter/deepseek/deepseek-chat-v3.1:free",
    "metadata": {
        "tokens_used": 2500,
        "cost": 0.0025,
        "retries": 0
    }
}
```

## Performance Considerations

### Optimization Tips

1. **Batch Processing:** Process multiple modules concurrently (3-5 tasks)
2. **Model Selection:** Use `gemini-flash` for development, `deepseek-v3` for production
3. **Timeout Configuration:** 300s for small modules, 600s for large modules
4. **Workspace Isolation:** Create separate workspaces per task to avoid conflicts
5. **Caching:** Cache model registry and configuration

### Cost Estimation

- **DeepSeek V3:** ~$0.0025 per test generation
- **Mistral Small:** ~$0.001 per test generation
- **Gemini Flash:** Free tier available
- **Batch of 100 modules:** ~$0.25-$0.50

## Monitoring and Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("openhands_integration")

# Logs will show:
# - Configuration loading
# - Task execution progress
# - Error recovery attempts
# - Performance metrics
```

## Next Steps

1. ✅ Configure environment variables
2. ✅ Test configuration loading
3. ✅ Test with real credentials
4. 📋 Implement TTA pipeline integration
5. 📊 Set up monitoring and metrics
6. 🚀 Deploy to production

## Support

- Configuration: See `ENVIRONMENT_SETUP.md`
- Integration Analysis: See `INTEGRATION_ANALYSIS_AND_RECOMMENDATION.md`
- Quick Start: See `QUICK_START_DOCKER.md`
