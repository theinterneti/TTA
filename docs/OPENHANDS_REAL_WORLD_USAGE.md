# OpenHands Real-World Usage Guide

## Overview

Now that the OpenHands integration is fully validated and production-ready, you can use it to execute real-world tasks like generating unit tests for Python modules.

---

## Quick Start

### 1. Run the Validation Test Suite

First, verify everything is working:
```bash
python scripts/test_openhands_integration.py
```

Expected output:
```
✅ PASS: Environment File
✅ PASS: Config Loading
✅ PASS: Docker Client Init
✅ PASS: Real Task Execution

Total: 4/4 tests passed
🎉 ALL TESTS PASSED! OpenHands integration is ready for production.
```

---

## Real-World Example: Generate Unit Tests

### Task: Generate tests for a Python module

**Module:** `src/agent_orchestration/openhands_integration/config.py`

**Estimated Execution Time:** 2-3 minutes
**Estimated Cost:** $0.03-0.08 (using OpenRouter free tier)

### Implementation

```python
import asyncio
from pathlib import Path
from agent_orchestration.openhands_integration.config import OpenHandsIntegrationConfig
from agent_orchestration.openhands_integration.docker_client import DockerOpenHandsClient

async def generate_tests():
    # Load configuration
    config = OpenHandsIntegrationConfig.from_env()
    client_config = config.to_client_config()
    client = DockerOpenHandsClient(client_config)

    # Prepare workspace
    workspace = config.workspace_root
    workspace.mkdir(parents=True, exist_ok=True)

    # Define task
    task = """
    Generate comprehensive unit tests for the Python module at:
    src/agent_orchestration/openhands_integration/config.py

    Requirements:
    1. Test all public functions and classes
    2. Include edge cases and error conditions
    3. Use pytest framework
    4. Aim for >80% code coverage
    5. Save tests to: tests/test_openhands_config.py
    """

    # Execute task
    print("Generating unit tests...")
    result = await client.execute_task(
        task_description=task,
        workspace_path=workspace,
        timeout=600.0,  # 10 minutes
    )

    # Check results
    if result.success:
        print("✅ Tests generated successfully!")
        test_file = workspace / "tests" / "test_openhands_config.py"
        if test_file.exists():
            print(f"Test file: {test_file}")
            print(f"Size: {test_file.stat().st_size} bytes")
    else:
        print(f"❌ Task failed: {result.error}")

    return result

# Run the task
if __name__ == "__main__":
    result = asyncio.run(generate_tests())
```

---

## Common Tasks

### 1. Generate Unit Tests
```python
task = """
Generate comprehensive unit tests for the Python module at:
<path_to_module>

Requirements:
1. Use pytest framework
2. Test all public functions and classes
3. Include edge cases and error conditions
4. Aim for >80% code coverage
5. Save tests to: tests/test_<module_name>.py
"""
```

### 2. Code Review and Refactoring
```python
task = """
Review the Python code at: <path_to_file>

Provide:
1. Code quality assessment
2. Refactoring suggestions
3. Performance improvements
4. Security issues (if any)
5. Best practices recommendations

Save the review to: reviews/<filename>_review.md
"""
```

### 3. Documentation Generation
```python
task = """
Generate comprehensive documentation for the Python module at:
<path_to_module>

Include:
1. Module overview
2. Class and function documentation
3. Usage examples
4. API reference
5. Common patterns

Save to: docs/<module_name>_documentation.md
"""
```

### 4. Bug Analysis and Fixes
```python
task = """
Analyze the bug in: <path_to_file>

Provide:
1. Root cause analysis
2. Proposed fix
3. Test cases to verify the fix
4. Regression test cases

Save analysis to: bug_analysis/<bug_id>.md
Save fix to: fixes/<bug_id>.patch
"""
```

---

## Performance Expectations

### Execution Time Breakdown

| Phase | Duration | Notes |
|-------|----------|-------|
| Docker startup | 5-10s | Pull image, initialize container |
| Runtime setup | 10-15s | Start sandbox, initialize tools |
| Model inference | 20-40s | LLM processing (depends on task complexity) |
| Task execution | 10-30s | File operations, code generation |
| **Total** | **50-95s** | For simple tasks |

### Cost Estimation

Using OpenRouter free tier models:

| Task Type | Tokens | Cost |
|-----------|--------|------|
| Simple file creation | 5K | $0.00 |
| Unit test generation | 50-100K | $0.03-0.08 |
| Code review | 100-200K | $0.06-0.15 |
| Documentation | 50-150K | $0.03-0.10 |

---

## Best Practices

### 1. Task Description
- Be specific and detailed
- Include file paths and requirements
- Specify output format and location
- Provide context about the codebase

### 2. Workspace Management
- Use isolated workspaces for different tasks
- Clean up old workspaces periodically
- Monitor disk usage for large tasks

### 3. Error Handling
```python
try:
    result = await client.execute_task(...)
    if result.success:
        # Process results
        pass
    else:
        # Handle failure
        print(f"Task failed: {result.error}")
except Exception as e:
    print(f"Execution error: {e}")
```

### 4. Timeout Configuration
- Simple tasks: 60-120 seconds
- Medium tasks: 300-600 seconds
- Complex tasks: 600-1800 seconds

---

## Troubleshooting

### Task Timeout
If a task times out:
1. Increase `timeout` parameter
2. Simplify the task
3. Break into smaller subtasks

### Out of Memory
If Docker container runs out of memory:
1. Reduce task complexity
2. Process files in smaller chunks
3. Increase Docker memory limit

### API Rate Limiting
If you hit OpenRouter rate limits:
1. Implement exponential backoff
2. Use fallback models
3. Batch requests with delays

---

## Integration with TTA Pipeline

The OpenHands integration is designed to work with the TTA (Test-Driven Architecture) pipeline:

```python
from tta_pipeline import TestGenerationPipeline
from agent_orchestration.openhands_integration.docker_client import DockerOpenHandsClient

# Create pipeline with OpenHands backend
pipeline = TestGenerationPipeline(
    backend=DockerOpenHandsClient,
    config=config,
)

# Generate tests for multiple modules
results = await pipeline.generate_tests(
    modules=["module1.py", "module2.py", "module3.py"],
    coverage_target=0.85,
)
```

---

## Next Steps

1. ✅ Validation complete
2. ⏭️ Run real-world test generation task
3. ⏭️ Integrate with TTA pipeline
4. ⏭️ Set up batch processing
5. ⏭️ Deploy to production

---

## Support

For issues or questions:
1. Check `docs/OPENHANDS_INTEGRATION_TROUBLESHOOTING.md`
2. Review `docs/OPENHANDS_ARCHITECTURE.md`
3. Run validation tests: `python scripts/test_openhands_integration.py`
4. Check Docker logs: `docker logs <container_id>`


---
**Logseq:** [[TTA.dev/Docs/Openhands_real_world_usage]]
