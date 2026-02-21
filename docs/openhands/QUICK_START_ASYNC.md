# OpenHands Async Execution - Quick Start Guide

## Overview

Three new non-blocking methods enable efficient async test generation:

1. **`submit_test_generation_task()`** - Submit and return immediately
2. **`get_test_generation_results()`** - Retrieve results later
3. **`get_task_status()`** - Check status without waiting

---

## Basic Usage

### Pattern 1: Fire and Forget

```python
from src.agent_orchestration.openhands_integration.workflow_integration import (
    OpenHandsTestGenerator,
)

async def main():
    generator = OpenHandsTestGenerator.from_env()

    # Submit task (returns immediately)
    task_id = await generator.submit_test_generation_task(
        module_path="src/components/auth.py",
        output_path="tests/test_auth.py",
        coverage_threshold=80,
    )

    print(f"Task submitted: {task_id}")
    # Workflow continues immediately
```

### Pattern 2: Submit and Retrieve Later

```python
async def main():
    generator = OpenHandsTestGenerator.from_env()

    # Submit task
    task_id = await generator.submit_test_generation_task(
        module_path="src/components/database.py",
    )

    # Do other work
    await run_refactoring_stage()
    await run_staging_deployment()

    # Retrieve results when ready
    result = await generator.get_test_generation_results(task_id)

    if result['success']:
        print("✓ Tests generated successfully")
    else:
        print(f"✗ Generation failed: {result['error']}")
```

### Pattern 3: Monitor Progress

```python
async def main():
    generator = OpenHandsTestGenerator.from_env()

    # Submit task
    task_id = await generator.submit_test_generation_task(
        module_path="src/components/cache.py",
    )

    # Monitor progress
    while True:
        status = await generator.get_task_status(task_id)
        print(f"Status: {status['status']}")

        if status['status'] == 'completed':
            break
        elif status['status'] == 'failed':
            print(f"Error: {status['error']}")
            break

        await asyncio.sleep(10)  # Check every 10 seconds
```

---

## Method Reference

### submit_test_generation_task()

**Returns task ID immediately (non-blocking)**

```python
task_id = await generator.submit_test_generation_task(
    module_path="src/components/my_component.py",  # Required
    output_path="tests/test_my_component.py",      # Optional
    coverage_threshold=80,                          # Optional (default: 80)
)
```

**Returns**: `str` - Task ID for later retrieval

**Raises**: `RuntimeError` if submission fails

---

### get_test_generation_results()

**Polls and retrieves results (blocking until complete)**

```python
result = await generator.get_test_generation_results(
    task_id="abc123...",           # Required
    timeout=600,                    # Optional (default: config.default_timeout_seconds)
    poll_interval=2.0,              # Optional (default: 2.0 seconds)
)
```

**Returns**: `dict` with keys:
- `success`: bool
- `task_id`: str
- `result`: dict (if successful)
- `error`: str (if failed)
- `module_path`: str
- `output_path`: str

**Raises**:
- `TimeoutError` if task exceeds timeout
- `RuntimeError` if task not found

---

### get_task_status()

**Returns current status immediately (non-blocking)**

```python
status = await generator.get_task_status(task_id="abc123...")
```

**Returns**: `dict` with keys:
- `task_id`: str
- `status`: str (PENDING, QUEUED, RUNNING, COMPLETED, FAILED)
- `created_at`: str (ISO format)
- `started_at`: str (ISO format, or None)
- `completed_at`: str (ISO format, or None)
- `error`: str (or None)
- `retry_count`: int
- `metadata`: dict

**Raises**: `RuntimeError` if task not found

---

## Comparison: Old vs New

### Old Way (Blocking)
```python
# Blocks entire workflow
result = await generator.generate_tests(
    module_path="src/components/my_component.py",
)
# Workflow waits here for 5+ minutes...
```

### New Way (Non-Blocking)
```python
# Submit and continue
task_id = await generator.submit_test_generation_task(
    module_path="src/components/my_component.py",
)

# Do other work while tests generate
await run_refactoring_stage()

# Retrieve results when ready
result = await generator.get_test_generation_results(task_id)
```

---

## Error Handling

### Handle Timeout
```python
try:
    result = await generator.get_test_generation_results(
        task_id,
        timeout=300,  # 5 minutes
    )
except TimeoutError:
    print("Task took too long")
    # Can retry or continue
```

### Handle Task Not Found
```python
try:
    status = await generator.get_task_status(task_id)
except RuntimeError as e:
    print(f"Task not found: {e}")
```

### Handle Generation Failure
```python
result = await generator.get_test_generation_results(task_id)

if not result['success']:
    print(f"Generation failed: {result['error']}")
```

---

## Batch Processing

```python
async def batch_generate():
    generator = OpenHandsTestGenerator.from_env()

    modules = [
        "src/components/auth.py",
        "src/components/database.py",
        "src/components/cache.py",
    ]

    # Submit all tasks
    task_ids = []
    for module in modules:
        task_id = await generator.submit_test_generation_task(
            module_path=module,
        )
        task_ids.append(task_id)

    # Do other work
    await run_refactoring_stage()

    # Retrieve all results
    results = []
    for task_id in task_ids:
        result = await generator.get_test_generation_results(task_id)
        results.append(result)

    # Process results
    successful = sum(1 for r in results if r['success'])
    print(f"Generated tests for {successful}/{len(modules)} modules")
```

---

## Performance Tips

1. **Use non-blocking methods** for long-running tasks
2. **Adjust poll_interval** based on expected task duration
   - Short tasks: 1-2 seconds
   - Long tasks: 5-10 seconds
3. **Set appropriate timeout** based on task complexity
   - Simple modules: 300 seconds (5 minutes)
   - Complex modules: 600 seconds (10 minutes)
4. **Batch submit** multiple tasks for efficiency

---

## Backward Compatibility

The old `generate_tests()` method still works:

```python
# Old way still works (blocking)
result = await generator.generate_tests(
    module_path="src/components/my_component.py",
)
```

But new non-blocking methods are recommended for better performance.

---

## Next Steps

- ✅ Phase 1: Non-blocking methods (COMPLETE)
- ⏳ Phase 2: Workflow integration (Optional)
- ⏳ Phase 3: Extended features (Optional)

---

**For more details, see**: `PHASE1_IMPLEMENTATION_COMPLETE.md`


---
**Logseq:** [[TTA.dev/Docs/Openhands/Quick_start_async]]
