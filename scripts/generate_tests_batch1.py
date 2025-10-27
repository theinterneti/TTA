# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Batch 1 Test Generation Script for OpenHands Integration.

Generates unit tests for the smallest modules (< 50 lines) using OpenHands.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_orchestration.openhands_integration.config import (
    OpenHandsIntegrationConfig,
)
from agent_orchestration.openhands_integration.execution_engine import ExecutionEngine
from agent_orchestration.openhands_integration.test_generation_models import (
    TestTaskSpecification,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Batch 1 modules (< 50 lines)
BATCH_1_MODULES = [
    "src/monitoring/metrics_collector.py",
    "src/monitoring/performance_monitor.py",
    "src/monitoring/logging_config.py",
    "src/agent_orchestration/validators.py",
    "src/components/narrative_arc_orchestrator/resolution_engine.py",
    "src/components/narrative_coherence/rules.py",
    "src/components/narrative_arc_orchestrator/causal_graph.py",
    "src/player_experience/api/routers/progress.py",
    "src/agent_orchestration/messaging.py",
    "src/agent_orchestration/workflow.py",
]


async def generate_tests_for_module(engine: ExecutionEngine, module_path: str) -> dict:
    """Generate tests for a single module."""
    logger.info(f"Generating tests for {module_path}...")

    # Create test task specification
    task_spec = TestTaskSpecification(
        module_path=module_path,
        test_requirements={
            "coverage_threshold": 80,
            "framework": "pytest",
            "output_path": f"tests/{module_path.replace('src/', '').replace('.py', '')}_test.py",
        },
        workspace="/home/thein/recovered-tta-storytelling",
        timeout=300,
    )

    # Queue the task
    task_id = engine.queue.add_task(
        task_type="test_generation",
        payload=task_spec.model_dump(),
        priority=1,
    )

    logger.info(f"Queued task {task_id} for {module_path}")
    return {"module": module_path, "task_id": task_id}


async def main():
    """Main execution function."""
    logger.info("Starting Batch 1 Test Generation...")

    # Load configuration
    config = OpenHandsIntegrationConfig.from_env()
    logger.info(f"Configuration loaded: {config.model_name}")

    # Create execution engine
    engine = ExecutionEngine(config, max_concurrent_tasks=3)

    # Generate tasks for all modules
    tasks = []
    for module in BATCH_1_MODULES[:5]:  # Start with first 5 modules
        task = await generate_tests_for_module(engine, module)
        tasks.append(task)

    # Save task list
    output_file = Path("batch1_tasks.json")
    with open(output_file, "w") as f:
        json.dump(tasks, f, indent=2)

    logger.info(f"Generated {len(tasks)} test generation tasks")
    logger.info(f"Task list saved to {output_file}")

    # Start engine
    logger.info("Starting execution engine...")
    await engine.start()

    # Wait for completion
    try:
        await asyncio.sleep(600)  # Wait up to 10 minutes
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        await engine.stop()

    logger.info("Batch 1 test generation complete!")


if __name__ == "__main__":
    asyncio.run(main())
