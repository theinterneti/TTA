# Logseq: [[TTA.dev/Scripts/Execute_batch_test_generation]]
# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Execute batch test generation using OpenHands integration.

Usage:
    python scripts/execute_batch_test_generation.py batch1
    python scripts/execute_batch_test_generation.py batch2
    python scripts/execute_batch_test_generation.py batch3
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_orchestration.openhands_integration.config import OpenHandsIntegrationConfig
from agent_orchestration.openhands_integration.docker_client import (
    DockerOpenHandsClient,
)

# Batch definitions
BATCHES = {
    "batch1": [
        "src/monitoring/metrics_collector.py",
        "src/agent_orchestration/validators.py",
        "src/monitoring/performance_monitor.py",
        "src/monitoring/logging_config.py",
        "src/player_experience/api/main.py",
        "src/components/narrative_arc_orchestrator/resolution_engine.py",
        "src/components/narrative_coherence/rules.py",
        "src/components/narrative_arc_orchestrator/causal_graph.py",
        "src/agent_orchestration/state.py",
        "src/player_experience/monitoring/alerting.py",
        "src/components/narrative_arc_orchestrator/conflict_detection.py",
        "src/player_experience/api/routers/progress.py",
        "src/agent_orchestration/messaging.py",
    ],
    "batch2": [
        "src/agent_orchestration/workflow.py",
        "src/common/time_utils.py",
        "src/agent_orchestration/admin/recover.py",
        "src/agent_orchestration/tools/callable_registry.py",
        "src/player_experience/models/enums.py",
        "src/player_experience/utils/normalization.py",
        "src/agent_orchestration/metrics.py",
        "src/agent_orchestration/interfaces.py",
        "src/agent_orchestration/openhands_integration/models.py",
        "src/agent_orchestration/performance/step_aggregator.py",
        "src/player_experience/api/routers/metrics.py",
        "src/agent_orchestration/langgraph_integration.py",
        "src/components/narrative_arc_orchestrator/models.py",
        "src/player_experience/api/test_containerized.py",
        "src/agent_orchestration/tools/coordinator.py",
        "src/common/process_utils.py",
        "src/player_experience/api/routers/sessions.py",
        "src/player_experience/frontend/node_modules/flatted/python/flatted.py",
    ],
    "batch3": [
        "src/agent_orchestration/workflow_transaction.py",
        "src/agent_orchestration/openhands_integration/test_generation_models.py",
        "src/agent_orchestration/tools/invocation_service.py",
        "src/agent_orchestration/tools/metrics.py",
        "src/agent_orchestration/tools/policy_config.py",
        "src/components/narrative_coherence/models.py",
        "src/player_experience/models/player.py",
        "src/agent_orchestration/tools/models.py",
        "src/components/narrative_arc_orchestrator/impact_analysis.py",
        "src/player_experience/utils/validation.py",
        "src/agent_orchestration/config/real_agent_config.py",
        "src/player_experience/api/test_sentry_integration.py",
        "src/player_experience/managers/player_experience_manager.py",
        "src/agent_orchestration/openhands_integration/test_task_builder.py",
        "src/player_experience/api/config.py",
        "src/player_experience/models/character.py",
        "src/agent_orchestration/tools/redis_tool_registry.py",
        "src/components/gameplay_loop/models/validation.py",
        "src/components/app_component.py",
        "src/agent_orchestration/openhands_integration/test_file_extractor.py",
        "src/agent_orchestration/openhands_integration/retry_policy.py",
        "src/player_experience/api/routers/health.py",
        "src/player_experience/models/session.py",
        "src/orchestration/decorators.py",
        "src/agent_orchestration/openhands_integration/metrics_collector.py",
    ],
}


async def generate_tests_for_module(
    client: DockerOpenHandsClient,
    module_path: str,
    batch_name: str,
    index: int,
    total: int,
) -> dict:
    """Generate tests for a single module."""

    task = f"""
    Generate comprehensive unit tests for the Python module at:
    {module_path}

    Requirements:
    1. Use pytest framework
    2. Target >80% code coverage
    3. Include edge cases and error handling
    4. Add docstrings to all test functions
    5. Save tests to: tests/{Path(module_path).parent.name}/test_{Path(module_path).stem}.py
    6. Ensure tests can be run with: uv run pytest

    Steps:
    1. Analyze the module's functionality
    2. Generate comprehensive unit tests
    3. Save to appropriate tests/ directory
    4. Verify tests are syntactically correct
    """

    start_time = datetime.now()
    try:
        result = await client.execute_task(
            task_description=task,
            workspace_path=Path.cwd(),
            timeout=1800.0,  # 30 minutes per module
        )
    except Exception as e:
        return {
            "module": module_path,
            "success": False,
            "elapsed_seconds": (datetime.now() - start_time).total_seconds(),
            "error": str(e)[:200],
            "output_length": 0,
        }
    elapsed = (datetime.now() - start_time).total_seconds()

    return {
        "module": module_path,
        "success": result.success,
        "elapsed_seconds": elapsed,
        "error": result.error if not result.success else None,
        "output_length": len(result.output) if result.output else 0,
    }


async def execute_batch(batch_name: str):
    """Execute test generation for a batch."""

    if batch_name not in BATCHES:
        return

    modules = BATCHES[batch_name]

    # Load configuration
    config = OpenHandsIntegrationConfig.from_env()
    client = DockerOpenHandsClient(config.to_client_config())

    results = []
    for i, module in enumerate(modules, 1):
        result = await generate_tests_for_module(
            client, module, batch_name, i, len(modules)
        )
        results.append(result)

        # Print status
        "✅ SUCCESS" if result["success"] else "❌ FAILED"
        if result["error"]:
            pass

    # Summary
    sum(1 for r in results if r["success"])
    sum(r["elapsed_seconds"] for r in results)

    # Failed modules
    failed = [r for r in results if not r["success"]]
    if failed:
        for _r in failed:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    batch_name = sys.argv[1]
    asyncio.run(execute_batch(batch_name))
