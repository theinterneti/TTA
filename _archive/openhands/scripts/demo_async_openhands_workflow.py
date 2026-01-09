# Logseq: [[TTA.dev/_archive/Openhands/Scripts/Demo_async_openhands_workflow]]
# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Demo script for async OpenHands test generation workflow.

This script demonstrates:
1. AsyncOpenHandsTestGenerationStage task submission
2. Parallel execution of other workflow stages while OpenHands runs
3. Result collection and timing measurements
4. Performance comparison between sync and async execution

Usage:
    python scripts/demo_async_openhands_workflow.py --component <component_name>

    # Example with a real component:
    python scripts/demo_async_openhands_workflow.py --component agent_orchestration

    # Dry run mode (simulates without actual OpenHands calls):
    python scripts/demo_async_openhands_workflow.py --component agent_orchestration --dry-run
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.workflow.openhands_stage import (
    AsyncOpenHandsStageResult,
    AsyncOpenHandsTestGenerationStage,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class AsyncWorkflowDemo:
    """Demonstration of async OpenHands workflow execution."""

    def __init__(self, component_path: Path, dry_run: bool = False):
        """
        Initialize demo.

        Args:
            component_path: Path to component directory
            dry_run: If True, simulate without actual OpenHands calls
        """
        self.component_path = component_path
        self.dry_run = dry_run
        self.config = {
            "coverage_threshold": 80,
            "timeout_seconds": 300,
            "poll_interval_seconds": 2.0,
            "enable_openhands_test_generation": True,
        }

    async def simulate_other_stages(self, duration_seconds: float = 30.0):
        """
        Simulate other workflow stages running in parallel.

        Args:
            duration_seconds: How long to simulate work
        """

        # Simulate refactoring stage
        await asyncio.sleep(duration_seconds / 3)

        # Simulate quality checks
        await asyncio.sleep(duration_seconds / 3)

        # Simulate staging deployment prep
        await asyncio.sleep(duration_seconds / 3)

    async def run_async_workflow(self) -> dict[str, Any]:
        """
        Run async workflow with parallel execution.

        Returns:
            Dictionary with execution results and timings
        """

        workflow_start = datetime.utcnow()
        results = {
            "success": False,
            "component_path": str(self.component_path),
            "dry_run": self.dry_run,
            "timings": {},
            "submitted_tasks": {},
            "completed_tasks": {},
            "failed_tasks": {},
            "errors": [],
        }

        try:
            # Stage 1: Submit OpenHands tasks (non-blocking)
            submission_start = datetime.utcnow()

            if self.dry_run:
                # Simulate task submission
                await asyncio.sleep(0.1)
                submitted_tasks = {
                    f"{self.component_path}/module1.py": "task-001",
                    f"{self.component_path}/module2.py": "task-002",
                    f"{self.component_path}/module3.py": "task-003",
                }
                submission_result = AsyncOpenHandsStageResult(
                    success=True,
                    submitted_tasks=submitted_tasks,
                    total_execution_time_ms=100.0,
                )
            else:
                stage = AsyncOpenHandsTestGenerationStage(
                    self.component_path, self.config
                )
                submission_result = await stage.submit_tasks()
                submitted_tasks = submission_result.submitted_tasks

            submission_time = (
                datetime.utcnow() - submission_start
            ).total_seconds() * 1000
            results["timings"]["submission_ms"] = submission_time
            results["submitted_tasks"] = submitted_tasks

            for _module_path, _task_id in submitted_tasks.items():
                pass

            # Stage 2: Run other workflow stages in parallel
            parallel_start = datetime.utcnow()

            # Simulate other stages running while OpenHands generates tests
            await self.simulate_other_stages(duration_seconds=30.0)

            parallel_time = (datetime.utcnow() - parallel_start).total_seconds() * 1000
            results["timings"]["parallel_stages_ms"] = parallel_time

            # Stage 3: Collect OpenHands results
            collection_start = datetime.utcnow()

            if self.dry_run:
                # Simulate result collection
                await asyncio.sleep(0.5)
                completed_tasks = {
                    "task-001": {"success": True, "coverage": 85.0},
                    "task-002": {"success": True, "coverage": 90.0},
                    "task-003": {"success": False, "error": "Timeout"},
                }
                failed_tasks = {"task-003": "Timeout"}
            else:
                collection_result = await stage.collect_results(submitted_tasks)
                completed_tasks = collection_result.completed_tasks
                failed_tasks = collection_result.failed_tasks

            collection_time = (
                datetime.utcnow() - collection_start
            ).total_seconds() * 1000
            results["timings"]["collection_ms"] = collection_time
            results["completed_tasks"] = completed_tasks
            results["failed_tasks"] = failed_tasks

            # Calculate total time and savings
            workflow_time = (datetime.utcnow() - workflow_start).total_seconds() * 1000
            results["timings"]["total_workflow_ms"] = workflow_time

            # Estimate sync workflow time (sequential execution)
            estimated_sync_time = (
                submission_time + 300000 + parallel_time + collection_time
            )  # 300s for OpenHands
            time_savings = estimated_sync_time - workflow_time
            savings_percentage = (time_savings / estimated_sync_time) * 100

            results["timings"]["estimated_sync_ms"] = estimated_sync_time
            results["timings"]["time_savings_ms"] = time_savings
            results["timings"]["savings_percentage"] = savings_percentage

            results["success"] = len(completed_tasks) > 0

            # Print summary

            return results

        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}", exc_info=True)
            results["errors"].append(str(e))
            return results


async def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Demo async OpenHands test generation workflow"
    )
    parser.add_argument(
        "--component",
        required=True,
        help="Component name (e.g., agent_orchestration)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate without actual OpenHands calls",
    )

    args = parser.parse_args()

    # Resolve component path
    component_path = Path("src") / args.component
    if not component_path.exists():
        logger.error(f"Component path does not exist: {component_path}")
        sys.exit(1)

    # Run demo
    demo = AsyncWorkflowDemo(component_path, dry_run=args.dry_run)
    results = await demo.run_async_workflow()

    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    asyncio.run(main())
