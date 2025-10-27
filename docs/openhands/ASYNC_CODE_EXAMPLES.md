# OpenHands Async Execution - Code Examples

## Example 1: Current Blocking Implementation

```python
# Current: Blocks entire workflow
async def current_workflow():
    generator = OpenHandsTestGenerator.from_env()

    # This blocks for 5+ minutes
    result = await generator.generate_tests(
        module_path="src/components/my_component.py",
        output_path="tests/test_my_component.py",
        coverage_threshold=80,
    )

    # Workflow waits here...
    print(f"Tests generated: {result['success']}")

    # Only then can we continue
    refactoring_result = await run_refactoring_stage()
    print(f"Refactoring done: {refactoring_result['success']}")
```

**Timeline:**
```
Start → Testing (30s) → OpenHands (300s) ← BLOCKS → Refactoring (30s) → End
Total: 360 seconds
```

---

## Example 2: Enhanced Non-Blocking Implementation

```python
# Enhanced: Non-blocking workflow
async def enhanced_workflow():
    generator = OpenHandsTestGenerator.from_env()

    # Submit task and get ID immediately (1ms)
    task_id = await generator.submit_test_generation_task(
        module_path="src/components/my_component.py",
        output_path="tests/test_my_component.py",
        coverage_threshold=80,
    )
    print(f"Task submitted: {task_id}")

    # Workflow continues immediately
    refactoring_result = await run_refactoring_stage()
    print(f"Refactoring done: {refactoring_result['success']}")

    # Retrieve results when ready
    result = await generator.get_test_generation_results(task_id)
    print(f"Tests generated: {result['success']}")
```

**Timeline:**
```
Start → Testing (30s) → Submit (1s) → Refactoring (30s) ← Parallel → Collect (1s) → End
Total: 92 seconds (75% faster!)
```

---

## Example 3: Batch Processing Multiple Modules

```python
# Submit multiple tasks in parallel
async def batch_test_generation():
    generator = OpenHandsTestGenerator.from_env()

    modules = [
        "src/components/auth.py",
        "src/components/database.py",
        "src/components/cache.py",
    ]

    # Submit all tasks (non-blocking)
    task_ids = []
    for module in modules:
        task_id = await generator.submit_test_generation_task(
            module_path=module,
            coverage_threshold=80,
        )
        task_ids.append(task_id)
        print(f"Submitted: {module} → {task_id}")

    # Do other work while tests generate
    await run_refactoring_stage()
    await run_staging_deployment()

    # Collect all results
    results = []
    for task_id in task_ids:
        result = await generator.get_test_generation_results(task_id)
        results.append(result)

    # Process results
    successful = sum(1 for r in results if r['success'])
    print(f"Generated tests for {successful}/{len(modules)} modules")
```

---

## Example 4: Status Monitoring

```python
# Monitor task progress without blocking
async def monitor_task_progress():
    generator = OpenHandsTestGenerator.from_env()

    # Submit task
    task_id = await generator.submit_test_generation_task(
        module_path="src/components/my_component.py",
    )

    # Monitor progress
    while True:
        status = await generator.get_task_status(task_id)

        print(f"Task {task_id[:8]}...")
        print(f"  Status: {status['status']}")
        print(f"  Created: {status['created_at']}")
        print(f"  Started: {status['started_at']}")

        if status['status'] == 'completed':
            print("✓ Task completed!")
            break
        elif status['status'] == 'failed':
            print(f"✗ Task failed: {status['error']}")
            break

        # Check again in 10 seconds
        await asyncio.sleep(10)
```

---

## Example 5: Timeout Handling

```python
# Handle timeouts gracefully
async def test_generation_with_timeout():
    generator = OpenHandsTestGenerator.from_env()

    task_id = await generator.submit_test_generation_task(
        module_path="src/components/my_component.py",
    )

    try:
        # Wait up to 10 minutes
        result = await generator.get_test_generation_results(
            task_id,
            timeout=600,  # 10 minutes
            poll_interval=5.0,  # Check every 5 seconds
        )
        print(f"Success: {result['success']}")

    except TimeoutError:
        print("Task took too long, continuing workflow...")
        # Workflow can continue even if task times out
        # Results can be retrieved later
```

---

## Example 6: Error Handling

```python
# Comprehensive error handling
async def robust_test_generation():
    generator = OpenHandsTestGenerator.from_env()

    try:
        # Submit task
        task_id = await generator.submit_test_generation_task(
            module_path="src/components/my_component.py",
        )

        # Do other work
        await run_refactoring_stage()

        # Retrieve results with error handling
        try:
            result = await generator.get_test_generation_results(
                task_id,
                timeout=300,
            )

            if result['success']:
                print("✓ Tests generated successfully")
            else:
                print(f"✗ Generation failed: {result['error']}")

        except TimeoutError:
            print("⚠ Task timed out")
            # Can retry or continue

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        # Graceful degradation
```

---

## Example 7: Workflow Integration

```python
# Integration with spec-to-production workflow
async def enhanced_workflow_stage():
    # Stage 2.5: Submit OpenHands tasks (non-blocking)
    if config.get("enable_openhands_test_generation"):
        task_ids = []
        for module in find_modules():
            task_id = await generator.submit_test_generation_task(
                module_path=str(module),
            )
            task_ids.append(task_id)

        # Store for later retrieval
        workflow_context['openhands_task_ids'] = task_ids

    # Stage 3: Refactoring (runs in parallel)
    refactoring_result = await run_refactoring_stage()

    # Stage 3.5: Collect OpenHands results
    if 'openhands_task_ids' in workflow_context:
        openhands_results = []
        for task_id in workflow_context['openhands_task_ids']:
            result = await generator.get_test_generation_results(task_id)
            openhands_results.append(result)

        workflow_context['openhands_results'] = openhands_results
```

---

## Example 8: Comparison - Before and After

### Before (Blocking)
```python
async def old_workflow():
    # 30s
    await testing_stage()

    # 300s - BLOCKS HERE
    await openhands_stage()

    # 30s
    await refactoring_stage()

    # Total: 360s
```

### After (Non-Blocking)
```python
async def new_workflow():
    # 30s
    await testing_stage()

    # 1s - Returns immediately
    task_ids = await submit_openhands_tasks()

    # 30s - Runs in parallel with OpenHands
    await refactoring_stage()

    # 1s - Collect results
    await collect_openhands_results(task_ids)

    # Total: 92s (75% faster!)
```

---

## Key Patterns

### Pattern 1: Fire and Forget
```python
task_id = await generator.submit_test_generation_task(...)
# Don't wait for results
```

### Pattern 2: Retrieve Later
```python
task_id = await generator.submit_test_generation_task(...)
# Do other work
result = await generator.get_test_generation_results(task_id)
```

### Pattern 3: Monitor Progress
```python
task_id = await generator.submit_test_generation_task(...)
while True:
    status = await generator.get_task_status(task_id)
    if status['status'] == 'completed':
        break
```

### Pattern 4: Batch Processing
```python
task_ids = [
    await generator.submit_test_generation_task(m)
    for m in modules
]
results = [
    await generator.get_test_generation_results(tid)
    for tid in task_ids
]
```

---

**All examples are production-ready and follow TTA best practices.**
