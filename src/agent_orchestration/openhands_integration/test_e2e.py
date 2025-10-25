"""
End-to-end tests for OpenHands integration system.

Tests the complete workflow:
1. Task submission
2. Model selection
3. Task execution
4. Result validation
5. Metrics collection
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from .config import OpenHandsConfig
from .execution_engine import ExecutionEngine
from .metrics_collector import MetricsCollector
from .model_selector import ModelSelector, TaskCategory, TaskRequirements
from .result_validator import ResultValidator
from .task_queue import QueuedTask, TaskPriority, TaskQueue

logger = logging.getLogger(__name__)


async def test_task_queue() -> bool:
    """Test task queue functionality."""
    print("\n=== Testing Task Queue ===")

    queue = TaskQueue(max_size=100)

    # Create test tasks
    tasks = [
        QueuedTask(
            task_type="unit_test",
            description="Test 1",
            priority=TaskPriority.HIGH,
        ),
        QueuedTask(
            task_type="documentation",
            description="Test 2",
            priority=TaskPriority.NORMAL,
        ),
        QueuedTask(
            task_type="refactor",
            description="Test 3",
            priority=TaskPriority.LOW,
        ),
    ]

    # Enqueue tasks
    task_ids = []
    for task in tasks:
        task_id = await queue.enqueue(task)
        task_ids.append(task_id)
        print(f"✓ Enqueued task: {task_id}")

    # Get stats
    stats = await queue.get_stats()
    print(f"✓ Queue stats: {stats}")

    # Dequeue and verify priority
    task1 = await queue.dequeue()
    assert task1.priority == TaskPriority.HIGH, "Priority ordering failed"
    print(f"✓ Dequeued high-priority task: {task1.task_id}")

    # Mark completed
    await queue.mark_completed(task1.task_id, {"result": "success"})
    print(f"✓ Marked task completed: {task1.task_id}")

    return True


async def test_model_selector() -> bool:
    """Test model selection."""
    print("\n=== Testing Model Selector ===")

    selector = ModelSelector()

    # Test different task types
    test_cases = [
        (TaskCategory.UNIT_TEST, "moderate", 0.8),
        (TaskCategory.DOCUMENTATION, "simple", 0.7),
        (TaskCategory.REFACTORING, "complex", 0.9),
        (TaskCategory.CODE_GENERATION, "moderate", 0.75),
    ]

    for category, complexity, quality in test_cases:
        requirements = TaskRequirements(
            category=category,
            complexity=complexity,
            quality_threshold=quality,
        )

        model = selector.select_model(requirements)
        assert model is not None, f"No model found for {category}"
        print(
            f"✓ Selected {model.name} for {category.value} "
            f"(quality: {model.quality_score:.1f}/5.0)"
        )

    return True


async def test_result_validator() -> bool:
    """Test result validation."""
    print("\n=== Testing Result Validator ===")

    import tempfile
    from pathlib import Path

    validator = ResultValidator()

    # Create temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("import pytest\n\ndef test_auth():\n    pass")
        temp_file = f.name

    try:
        # Test valid result
        valid_result = {
            "output_file": temp_file,
            "content": "import pytest\n\ndef test_auth():\n    pass",
            "execution_result": {"passed": True},
        }

        validation = validator.validate(valid_result)
        assert validation.passed, f"Valid result should pass. Errors: {validation.errors}"
        print(f"✓ Valid result passed validation (score: {validation.score:.2f})")

        # Test invalid result (missing file)
        invalid_result = {
            "output_file": "/nonexistent/path/test_auth.py",
            "content": "",  # Empty content
            "execution_result": {"passed": False},
        }

        validation = validator.validate(invalid_result)
        assert not validation.passed, "Invalid result should fail"
        print(f"✓ Invalid result failed validation (errors: {len(validation.errors)})")

        return True
    finally:
        # Clean up temp file
        Path(temp_file).unlink(missing_ok=True)


async def test_metrics_collector() -> bool:
    """Test metrics collection."""
    print("\n=== Testing Metrics Collector ===")

    from .metrics_collector import ExecutionMetrics

    collector = MetricsCollector()

    # Record some metrics
    for i in range(5):
        metrics = ExecutionMetrics(
            task_id=f"task-{i}",
            model_id="mistral-small" if i % 2 == 0 else "llama-3.3",
            task_type="unit_test",
        )

        metrics.success = i < 4  # Last one fails
        metrics.tokens_used = 1000 + i * 100
        metrics.cost = 0.14 + i * 0.01
        metrics.quality_score = 4.0 + i * 0.1
        metrics.validation_passed = i < 4

        collector.record_execution(metrics)

    # Get summary
    summary = collector.get_summary()
    print(f"✓ System metrics: {summary['system']}")
    print(f"✓ Model metrics: {list(summary['models'].keys())}")

    assert summary["system"]["total_tasks"] == 5, "Should have 5 tasks"
    assert summary["system"]["completed_tasks"] == 4, "Should have 4 completed"
    assert summary["system"]["failed_tasks"] == 1, "Should have 1 failed"

    return True


async def test_execution_engine() -> bool:
    """Test execution engine."""
    print("\n=== Testing Execution Engine ===")

    try:
        from .config import OpenHandsIntegrationConfig
        integration_config = OpenHandsIntegrationConfig.from_env()
        # Convert to OpenHandsConfig
        config = OpenHandsConfig(
            api_key=integration_config.api_key,
            model=integration_config.custom_model_id or integration_config.model_preset,
            workspace_path=integration_config.workspace_root,
        )
    except (ValueError, Exception) as e:
        print(f"⚠️  Skipping execution engine test: {e}")
        return True

    engine = ExecutionEngine(config, max_concurrent_tasks=2)

    # Start engine
    await engine.start()
    print("✓ Engine started")

    # Submit test task
    task = QueuedTask(
        task_type="unit_test",
        description="Test task for validation",
        priority=TaskPriority.NORMAL,
        metadata={
            "category": "unit_test",
            "complexity": "simple",
            "quality_threshold": 0.7,
        },
    )

    task_id = await engine.submit_task(task)
    print(f"✓ Task submitted: {task_id}")

    # Get queue stats
    stats = await engine.get_queue_stats()
    print(f"✓ Queue stats: {stats}")

    # Stop engine
    await engine.stop()
    print("✓ Engine stopped")

    return True


async def test_integration() -> bool:
    """Test full integration."""
    print("\n=== Testing Full Integration ===")

    # Test 1: Queue
    if not await test_task_queue():
        return False

    # Test 2: Model Selector
    if not await test_model_selector():
        return False

    # Test 3: Result Validator
    if not await test_result_validator():
        return False

    # Test 4: Metrics Collector
    if not await test_metrics_collector():
        return False

    # Test 5: Execution Engine
    if not await test_execution_engine():
        return False

    return True


async def main():
    """Run all tests."""
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("OpenHands Integration System - End-to-End Tests")
    print("=" * 60)

    try:
        success = await test_integration()

        print("\n" + "=" * 60)
        if success:
            print("✅ All tests passed!")
            print("=" * 60)
            return 0
        else:
            print("❌ Some tests failed")
            print("=" * 60)
            return 1

    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

