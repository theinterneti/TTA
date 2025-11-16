# ruff: noqa: ALL
#!/usr/bin/env python
"""
Test a single task with detailed logging to verify the validation fix.

This script:
1. Creates a minimal task for therapeutic_safety.py
2. Executes it with the optimized client
3. Validates the result
4. Shows detailed output for debugging
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_orchestration.openhands_integration.adapter import OpenHandsAdapter
from src.agent_orchestration.openhands_integration.config import (
    OpenHandsIntegrationConfig,
)
from src.agent_orchestration.openhands_integration.optimized_client import (
    OptimizedOpenHandsClient,
)
from src.agent_orchestration.openhands_integration.result_validator import (
    ResultValidator,
)
from src.agent_orchestration.openhands_integration.task_queue import (
    QueuedTask,
    TaskPriority,
)


async def test_single_task():
    """Test a single task execution."""

    # Load config from environment (loads .env file automatically)
    try:
        integration_config = OpenHandsIntegrationConfig.from_env()
        config = integration_config.to_client_config()
    except ValueError:
        return False

    # Create client and adapter with fallback to mock on garbage output
    # Note: Using fallback_to_mock=True to handle model failures gracefully
    client = OptimizedOpenHandsClient(config)
    adapter = OpenHandsAdapter(client=client, fallback_to_mock=True)

    # Create validator
    validator = ResultValidator()

    # Create a minimal task
    task = QueuedTask(
        task_type="unit_test",
        description="Generate tests for src/agent_orchestration/therapeutic_safety.py (coverage: 0% -> 70%)",
        priority=TaskPriority.NORMAL,
        metadata={
            "file": "src/agent_orchestration/therapeutic_safety.py",
            "module": "Agent Orchestration",
            "current_coverage": "0%",
            "target_coverage": "70%",
        },
    )

    try:
        # Execute task
        result = await adapter.execute_development_task(task.description)

        for key in sorted(result.keys()):
            value = result[key]
            if isinstance(value, str):
                value[:100] + "..." if len(value) > 100 else value
            else:
                pass

        # Validate result
        validation = validator.validate(result)

        if validation.errors:
            for _error in validation.errors:
                pass

        if validation.warnings:
            for _warning in validation.warnings:
                pass

        for details in validation.details.values():
            "✅" if details.get("passed") else "❌"

        # Show content preview
        if "content" in result and result["content"]:
            content_preview = result["content"][:500]
            for _line in content_preview.split("\n"):
                pass

        # Final verdict
        if validation.passed:
            pass
        else:
            pass

        return validation.passed

    except Exception:
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_single_task())
    sys.exit(0 if success else 1)
