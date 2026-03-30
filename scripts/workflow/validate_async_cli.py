"""Validation script for async workflow CLI integration."""

# Logseq: [[TTA.dev/Scripts/Workflow/Validate_async_cli]]

import asyncio
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.workflow.spec_to_production import WorkflowOrchestrator


async def validate_async_workflow():
    """Validate that async workflow can be invoked and runs correctly."""

    # Create a minimal test spec
    test_spec = Path("specs/calculator_operations.md")
    if not test_spec.exists():
        return False

    # Test 1: Async workflow can be instantiated
    try:
        orchestrator = WorkflowOrchestrator(
            spec_file=test_spec,
            component_name="calculator",
            target_stage="dev",
            config={
                "enable_openhands_test_generation": False
            },  # Disable OpenHands for validation
        )
    except Exception:
        return False

    # Test 2: Async method exists and is callable
    if not hasattr(orchestrator, "run_async_with_parallel_openhands"):
        return False

    # Test 3: Async method can be called (will fail at spec parsing, but that's OK)
    try:
        await orchestrator.run_async_with_parallel_openhands()
    except Exception:
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(validate_async_workflow())
    sys.exit(0 if success else 1)
