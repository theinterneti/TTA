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

    print("\n" + "=" * 80)
    print("PHASE 7 VALIDATION FIX TEST")
    print("=" * 80)

    # Load config from environment (loads .env file automatically)
    try:
        integration_config = OpenHandsIntegrationConfig.from_env()
        config = integration_config.to_client_config()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        return False

    # Create client and adapter with fallback to mock on garbage output
    # Note: Using fallback_to_mock=True to handle model failures gracefully
    client = OptimizedOpenHandsClient(config)
    adapter = OpenHandsAdapter(client=client, fallback_to_mock=True)

    print("\n⚙️  Configuration:")
    print(f"   Model: {config.model}")
    print("   Fallback to Mock: True (handles model failures)")
    print(f"   Workspace: {config.workspace_path}")

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

    print("\n📋 Task Details:")
    print(f"   Task ID: {task.task_id[:8]}...")
    print(f"   Description: {task.description}")
    print(f"   File: {task.metadata['file']}")

    try:
        # Execute task
        print("\n⏳ Executing task...")
        result = await adapter.execute_development_task(task.description)

        print("\n✅ Task executed successfully")
        print("\n📊 Result Structure:")
        for key in sorted(result.keys()):
            value = result[key]
            if isinstance(value, str):
                preview = value[:100] + "..." if len(value) > 100 else value
                print(f"   {key}: {preview}")
            else:
                print(f"   {key}: {value}")

        # Validate result
        print("\n🔍 Validating result...")
        validation = validator.validate(result)

        print("\n📋 Validation Result:")
        print(f"   Passed: {validation.passed}")
        print(f"   Score: {validation.score:.2f}")
        print(f"   Errors: {len(validation.errors)}")
        print(f"   Warnings: {len(validation.warnings)}")

        if validation.errors:
            print("\n❌ Errors:")
            for error in validation.errors:
                print(f"   - {error}")

        if validation.warnings:
            print("\n⚠️  Warnings:")
            for warning in validation.warnings:
                print(f"   - {warning}")

        print("\n📋 Validation Details:")
        for rule_name, details in validation.details.items():
            status = "✅" if details.get("passed") else "❌"
            print(f"   {status} {rule_name}: {details.get('message', 'N/A')}")

        # Show content preview
        if "content" in result and result["content"]:
            print("\n📝 Generated Content (first 500 chars):")
            print("   " + "-" * 76)
            content_preview = result["content"][:500]
            for line in content_preview.split("\n"):
                print(f"   {line}")
            print("   " + "-" * 76)

        # Final verdict
        print("\n" + "=" * 80)
        if validation.passed:
            print("✅ VALIDATION PASSED - Task output is valid!")
        else:
            print("❌ VALIDATION FAILED - Task output has issues")
        print("=" * 80)

        return validation.passed

    except Exception as e:
        print(f"\n❌ Error executing task: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_single_task())
    sys.exit(0 if success else 1)
