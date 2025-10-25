#!/usr/bin/env python3
"""
Phase 7 Task Re-queuing Script

Re-submits all 47 tasks from batch results to the running execution engine.
This ensures tasks are properly queued for processing.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_orchestration.openhands_integration.config import (
    OpenHandsConfig,
    OpenHandsIntegrationConfig,
)
from agent_orchestration.openhands_integration.execution_engine import ExecutionEngine
from agent_orchestration.openhands_integration.task_queue import QueuedTask, TaskPriority


# Load all task IDs from batch results
def load_all_tasks():
    """Load all tasks from batch result files."""
    tasks = []
    batch_files = [
        "batch1_results.json",
        "batch2_results.json",
        "batch3_results.json",
        "batch4_results.json",
        "batch5_results.json",
    ]

    for batch_file in batch_files:
        path = Path(batch_file)
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                for result in data.get("results", []):
                    item = result.get("item", {})
                    task_id = result.get("task_id")
                    if task_id:
                        tasks.append(
                            {
                                "task_id": task_id,
                                "item": item,
                                "batch": data.get("batch"),
                            }
                        )

    return tasks


async def requeue_tasks():
    """Re-queue all tasks to the running engine."""
    print("=" * 80)
    print("🔄 PHASE 7 TASK RE-QUEUING")
    print("=" * 80)
    print()

    # Load configuration
    integration_config = OpenHandsIntegrationConfig.from_env()
    config = OpenHandsConfig(
        api_key=integration_config.api_key,
        model=integration_config.custom_model_id or integration_config.model_preset,
        workspace_path=integration_config.workspace_root,
    )

    # Create engine
    engine = ExecutionEngine(config, max_concurrent_tasks=5)

    # Load all tasks
    all_tasks = load_all_tasks()
    print(f"📋 Loaded {len(all_tasks)} tasks from batch results")
    print()

    # Re-queue each task
    requeued = 0
    failed = 0

    for task_data in all_tasks:
        item = task_data["item"]
        batch = task_data["batch"]

        # Determine task type and priority based on batch
        if batch in [1, 2]:
            task_type = "unit_test"
            priority = TaskPriority.CRITICAL if batch == 1 else TaskPriority.HIGH
        elif batch == 3:
            task_type = "refactoring"
            priority = TaskPriority.HIGH
        elif batch == 4:
            task_type = "documentation"
            priority = TaskPriority.NORMAL
        else:  # batch 5
            task_type = "code_generation"
            priority = TaskPriority.NORMAL

        # Create task
        description = f"[Batch {batch}] {item.get('task', item.get('module', 'Task'))}"
        task = QueuedTask(
            task_type=task_type,
            description=description,
            target_file=Path(item.get("file")) if item.get("file") else None,
            priority=priority,
            metadata={
                "batch": batch,
                "complexity": item.get("complexity", "moderate"),
                "original_task_id": task_data["task_id"],
            },
        )

        try:
            # Submit task
            new_task_id = await engine.submit_task(task)
            print(f"✅ Batch {batch}: {description[:50]}")
            print(f"   New Task ID: {new_task_id}")
            requeued += 1
        except Exception as e:
            print(f"❌ Batch {batch}: {description[:50]}")
            print(f"   Error: {e}")
            failed += 1

    print()
    print("=" * 80)
    print(f"✅ RE-QUEUING COMPLETE")
    print(f"   Re-queued: {requeued}/{len(all_tasks)} tasks")
    print(f"   Failed: {failed}/{len(all_tasks)} tasks")
    print("=" * 80)

    # Get queue stats
    stats = await engine.get_queue_stats()
    print()
    print("📊 Queue Statistics:")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    asyncio.run(requeue_tasks())

