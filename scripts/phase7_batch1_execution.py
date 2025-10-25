#!/usr/bin/env python3
"""
Phase 7 Batch 1 Execution - Tier 1 Unit Tests (Items 1-6)

Executes critical unit test generation tasks for:
- Agent Orchestration: adapters.py, agents.py, service.py (5% → 70%)
- Player Experience: auth.py, characters.py, player_experience_manager.py (3% → 70%)

Total: 6 tasks, 18 hours estimated, $45-60 cost savings
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_orchestration.openhands_integration.config import (
    OpenHandsConfig,
    OpenHandsIntegrationConfig,
)
from agent_orchestration.openhands_integration.execution_engine import ExecutionEngine
from agent_orchestration.openhands_integration.task_queue import (
    QueuedTask,
    TaskPriority,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Batch 1 Work Items
BATCH1_ITEMS = [
    {
        "id": 1,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/adapters.py",
        "coverage": "5%",
        "target": "70%",
        "complexity": "simple",
        "model": "Mistral Small",
    },
    {
        "id": 2,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/agents.py",
        "coverage": "5%",
        "target": "70%",
        "complexity": "moderate",
        "model": "Llama 3.3",
    },
    {
        "id": 3,
        "module": "Agent Orchestration",
        "file": "src/agent_orchestration/service.py",
        "coverage": "5%",
        "target": "70%",
        "complexity": "moderate",
        "model": "Llama 3.3",
    },
    {
        "id": 4,
        "module": "Player Experience",
        "file": "src/player_experience/api/routers/auth.py",
        "coverage": "3%",
        "target": "70%",
        "complexity": "moderate",
        "model": "Llama 3.3",
    },
    {
        "id": 5,
        "module": "Player Experience",
        "file": "src/player_experience/api/routers/characters.py",
        "coverage": "3%",
        "target": "70%",
        "complexity": "moderate",
        "model": "Llama 3.3",
    },
    {
        "id": 6,
        "module": "Player Experience",
        "file": "src/player_experience/managers/player_experience_manager.py",
        "coverage": "3%",
        "target": "70%",
        "complexity": "complex",
        "model": "DeepSeek Chat",
    },
]


def create_task(item: dict[str, Any]) -> QueuedTask:
    """Create a unit test generation task."""
    return QueuedTask(
        task_type="unit_test",
        description=f"Generate unit tests for {Path(item['file']).name} ({item['coverage']} → {item['target']})",
        target_file=Path(item["file"]),
        priority=TaskPriority.CRITICAL,
        metadata={
            "category": "unit_test",
            "module": item["module"],
            "complexity": item["complexity"],
            "current_coverage": item["coverage"],
            "target_coverage": item["target"],
            "recommended_model": item["model"],
            "work_item_id": item["id"],
            "batch": 1,
        },
    )


async def main():
    """Execute Batch 1 tasks."""
    logger.info("=" * 80)
    logger.info("🚀 PHASE 7 BATCH 1 EXECUTION - TIER 1 UNIT TESTS")
    logger.info("=" * 80)

    try:
        # Load configuration
        integration_config = OpenHandsIntegrationConfig.from_env()
        config = OpenHandsConfig(
            api_key=integration_config.api_key,
            model=integration_config.custom_model_id or integration_config.model_preset,
            workspace_path=integration_config.workspace_root,
        )

        # Create execution engine
        engine = ExecutionEngine(config, max_concurrent_tasks=3)

        # Start engine
        await engine.start()
        logger.info("✅ Execution engine started with 3 workers")

        # Create tasks
        logger.info(f"\n📋 Creating {len(BATCH1_ITEMS)} unit test tasks...")
        tasks = [create_task(item) for item in BATCH1_ITEMS]

        # Submit tasks
        logger.info("\n🚀 Submitting tasks to queue...")
        task_ids = []
        for i, task in enumerate(tasks, 1):
            try:
                task_id = await engine.submit_task(task)
                task_ids.append(task_id)
                logger.info(f"  [{i}/6] ✅ {task.description}")
                logger.info(f"       Task ID: {task_id}")
            except Exception as e:
                logger.error(f"  [{i}/6] ❌ Failed: {e}")

        logger.info(f"\n✅ Submitted {len(task_ids)}/6 tasks")

        # Get queue stats
        stats = await engine.get_queue_stats()
        logger.info("\n📊 Queue Statistics:")
        logger.info(f"   Total tasks: {stats.get('total_tasks', 0)}")
        logger.info(f"   Pending: {stats.get('pending_count', 0)}")
        logger.info(f"   Running: {stats.get('running_count', 0)}")

        # Stop engine
        await engine.stop()
        logger.info("\n✅ Execution engine stopped")

        # Save results
        results = {
            "batch": 1,
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(task_ids),
            "task_ids": task_ids,
            "items": BATCH1_ITEMS,
        }

        output_file = Path(__file__).parent.parent / "batch1_submission_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"\n💾 Results saved to {output_file}")
        logger.info("\n" + "=" * 80)
        logger.info("✅ BATCH 1 SUBMISSION COMPLETE")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
