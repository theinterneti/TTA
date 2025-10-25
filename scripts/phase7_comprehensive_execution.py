#!/usr/bin/env python3
"""
Phase 7 Comprehensive Execution Script

Loads all 47 tasks from batch results and executes them using the OpenHands
execution engine in a single process with persistent queue.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_orchestration.openhands_integration.config import (
    OpenHandsConfig,
    OpenHandsIntegrationConfig,
    get_model_by_preset,
)
from agent_orchestration.openhands_integration.execution_engine import ExecutionEngine
from agent_orchestration.openhands_integration.task_queue import (
    QueuedTask,
    TaskPriority,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
                    if item:
                        batch = data.get("batch")
                        # Determine task type and priority
                        if batch in [1, 2]:
                            task_type = "unit_test"
                            priority = (
                                TaskPriority.CRITICAL
                                if batch == 1
                                else TaskPriority.HIGH
                            )
                        elif batch == 3:
                            task_type = "refactoring"
                            priority = TaskPriority.HIGH
                        elif batch == 4:
                            task_type = "documentation"
                            priority = TaskPriority.NORMAL
                        else:  # batch 5
                            task_type = "code_generation"
                            priority = TaskPriority.NORMAL

                        description = f"[Batch {batch}] {item.get('task', item.get('module', 'Task'))}"
                        task = QueuedTask(
                            task_type=task_type,
                            description=description,
                            target_file=(
                                Path(item.get("file"))
                                if item.get("file")
                                else None
                            ),
                            priority=priority,
                            metadata={
                                "batch": batch,
                                "complexity": item.get("complexity", "moderate"),
                            },
                        )
                        tasks.append(task)

    return tasks


async def run_execution():
    """Run comprehensive execution."""
    print("=" * 80)
    print("🚀 PHASE 7 COMPREHENSIVE EXECUTION")
    print("=" * 80)
    print()

    # Load configuration
    integration_config = OpenHandsIntegrationConfig.from_env()

    # Resolve model preset to full model ID
    # Use llama-3.3-8b as primary model (100% success rate, 0.88s avg latency)
    model_id = integration_config.custom_model_id
    if not model_id:
        # Use high-performance Llama model instead of rate-limited Gemini
        model_id = "openrouter/meta-llama/llama-3.3-8b-instruct:free"

    config = OpenHandsConfig(
        api_key=integration_config.api_key,
        model=model_id,
        workspace_path=integration_config.workspace_root,
    )

    # Create engine
    engine = ExecutionEngine(config, max_concurrent_tasks=5)

    # Load all tasks
    all_tasks = load_all_tasks()
    print(f"📋 Loaded {len(all_tasks)} tasks from batch results")
    print()

    # Start engine
    print("🔧 Starting execution engine...")
    await engine.start()
    print("✅ Engine started")
    print()

    # Submit all tasks
    print("📤 Submitting tasks to queue...")
    submitted = 0
    for i, task in enumerate(all_tasks, 1):
        try:
            task_id = await engine.submit_task(task)
            submitted += 1
            if i % 10 == 0:
                print(f"   [{i}/{len(all_tasks)}] Tasks submitted")
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")

    print(f"✅ Submitted {submitted}/{len(all_tasks)} tasks")
    print()

    # Get initial queue stats
    stats = await engine.get_queue_stats()
    print("📊 Initial Queue Statistics:")
    print(json.dumps(stats, indent=2))
    print()

    # Run engine for specified duration
    duration = 3600  # 1 hour
    print(f"⏱️  Running engine for {duration}s ({duration//60} minutes)...")
    print("   (Press Ctrl+C to stop early)")
    print()

    try:
        await asyncio.sleep(duration)
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")

    # Get final stats
    print()
    print("📊 Final Queue Statistics:")
    final_stats = await engine.get_queue_stats()
    print(json.dumps(final_stats, indent=2))

    # Get metrics
    print()
    print("📈 Execution Metrics:")
    metrics = engine.get_metrics_summary()
    print(json.dumps(metrics, indent=2))

    # Stop engine
    print()
    print("🛑 Stopping execution engine...")
    await engine.stop()
    print("✅ Engine stopped")

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tasks": len(all_tasks),
        "submitted": submitted,
        "initial_stats": stats,
        "final_stats": final_stats,
        "metrics": metrics,
    }

    output_file = Path("phase7_execution_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print("=" * 80)
    print(f"✅ EXECUTION COMPLETE")
    print(f"   Results saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_execution())

