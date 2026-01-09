# OpenHands Async Enhancement Implementation Guide

## Overview

This guide provides step-by-step instructions to enhance the OpenHands integration to support true non-blocking asynchronous execution, allowing the workflow to continue while tests generate in the background.

---

## Phase 1: Add Non-Blocking Methods to OpenHandsTestGenerator

### Step 1.1: Add `submit_test_generation_task()` Method

**File**: `src/agent_orchestration/openhands_integration/workflow_integration.py`

**Purpose**: Submit test generation task and return immediately with task_id

```python
async def submit_test_generation_task(
    self,
    module_path: str,
    output_path: str | None = None,
    coverage_threshold: int = 80,
) -> str:
    """
    Submit test generation task asynchronously (non-blocking).

    Returns task_id immediately. Use get_test_generation_results()
    to retrieve results later.

    Args:
        module_path: Path to module to generate tests for
        output_path: Path where generated tests should be saved
        coverage_threshold: Target coverage percentage

    Returns:
        Task ID for later result retrieval

    Raises:
        RuntimeError: If task submission fails
    """
    task_description = f"""
Generate comprehensive unit tests for the Python module at {module_path}.

Requirements:
- Target coverage: {coverage_threshold}%
- Use pytest framework
- Include edge cases and error conditions
- Add docstrings to test functions
- Follow existing test patterns in the codebase
"""

    if output_path:
        task_description += f"\nSave generated tests to: {output_path}"

    task = QueuedTask(
        task_type="unit_test",
        description=task_description,
        target_file=Path(module_path),
        priority=TaskPriority.HIGH,
        metadata={
            "coverage_threshold": coverage_threshold,
            "output_path": output_path,
        },
    )

    task_id = await self.engine.submit_task(task)
    logger.info(f"Submitted test generation task: {task_id}")
    return task_id
```

### Step 1.2: Add `get_test_generation_results()` Method

**Purpose**: Retrieve results for previously submitted task

```python
async def get_test_generation_results(
    self,
    task_id: str,
    timeout: float | None = None,
    poll_interval: float = 2.0,
) -> dict[str, Any]:
    """
    Retrieve results for previously submitted test generation task.

    Polls task status until completion or timeout.

    Args:
        task_id: Task ID from submit_test_generation_task()
        timeout: Maximum time to wait (seconds)
        poll_interval: Time between status checks (seconds)

    Returns:
        Dictionary with generation results

    Raises:
        TimeoutError: If task doesn't complete within timeout
        RuntimeError: If task fails
    """
    timeout = timeout or self.config.default_timeout_seconds
    start_time = asyncio.get_event_loop().time()

    while True:
        task_status = await self.engine.get_task_status(task_id)

        if not task_status:
            raise RuntimeError(f"Task {task_id} not found")

        if task_status.status == "completed":
            result = task_status.result or {}
            logger.info(f"Test generation completed: {task_id}")
            return {
                "success": True,
                "task_id": task_id,
                "result": result,
            }

        if task_status.status == "failed":
            error = task_status.error or "Unknown error"
            logger.error(f"Test generation failed: {error}")
            return {
                "success": False,
                "task_id": task_id,
                "error": error,
            }

        # Check timeout
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > timeout:
            logger.error(f"Test generation timeout after {elapsed:.1f}s")
            raise TimeoutError(f"Task {task_id} exceeded timeout")

        # Wait before checking again
        await asyncio.sleep(poll_interval)
```

### Step 1.3: Add `get_task_status()` Method

**Purpose**: Check status of submitted task without waiting

```python
async def get_task_status(self, task_id: str) -> dict[str, Any]:
    """
    Get current status of a submitted task.

    Args:
        task_id: Task ID from submit_test_generation_task()

    Returns:
        Dictionary with task status and metadata
    """
    task = await self.engine.get_task_status(task_id)

    if not task:
        return {"status": "not_found", "task_id": task_id}

    return {
        "task_id": task_id,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "error": task.error,
    }
```

---

## Phase 2: Update Workflow Integration

### Step 2.1: Modify openhands_stage.py

**Change**: Add support for non-blocking task submission

```python
async def execute_async(self) -> OpenHandsStageResult:
    """Execute stage asynchronously (non-blocking)."""
    # Submit tasks and return immediately
    # Don't wait for completion
    pass

def get_task_ids(self) -> list[str]:
    """Get submitted task IDs for later result collection."""
    pass
```

### Step 2.2: Modify spec_to_production.py

**Change**: Submit tasks and continue workflow

```python
# Stage 2.5: Submit OpenHands tasks (non-blocking)
if self.config.get("enable_openhands_test_generation", False):
    openhands_task_ids = await self._submit_openhands_tasks()
    result.openhands_task_ids = openhands_task_ids

# Stage 3: Refactoring (runs in parallel with OpenHands)
refactoring_result = self._run_refactoring_stage()

# Stage 3.5: Collect OpenHands results
if result.openhands_task_ids:
    openhands_results = await self._collect_openhands_results(
        result.openhands_task_ids
    )
    result.stage_results["openhands_test_generation"] = openhands_results
```

---

## Phase 3: Testing

### Test Cases to Add

1. **Non-blocking submission**: Verify task_id returned immediately
2. **Parallel execution**: Verify other stages run while tests generate
3. **Result retrieval**: Verify results can be retrieved later
4. **Timeout handling**: Verify timeout works correctly
5. **Error handling**: Verify errors are properly reported

---

## Implementation Checklist

- [ ] Add `submit_test_generation_task()` method
- [ ] Add `get_test_generation_results()` method
- [ ] Add `get_task_status()` method
- [ ] Update openhands_stage.py for async support
- [ ] Update spec_to_production.py workflow
- [ ] Add tests for non-blocking behavior
- [ ] Update documentation
- [ ] Performance testing (measure improvement)

---

## Expected Outcomes

✅ Workflow continues while tests generate
✅ 30-50% faster workflow execution
✅ Better resource utilization
✅ Foundation for parallel task execution
✅ Improved user experience (responsive workflow)

---

**Estimated Effort**: 2-3 hours
**Priority**: Medium (Performance optimization)
**Risk**: Low (Backward compatible)


---
**Logseq:** [[TTA.dev/Docs/Openhands/Async_enhancement_implementation]]
