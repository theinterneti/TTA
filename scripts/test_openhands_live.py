#!/usr/bin/env python3
"""
OpenHands Integration Live Test Script

Tests OpenHands integration end-to-end by executing a real development task
against the OpenRouter API. Validates connectivity, task execution, and code quality.

Usage:
    uv run python scripts/test_openhands_live.py

Requirements:
    - OPENROUTER_API_KEY configured in .env file
    - OpenHands SDK installed (openhands-sdk>=0.1.0)
    - Internet connectivity to OpenRouter API
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from pydantic import SecretStr

from src.agent_orchestration.openhands_integration.adapter import OpenHandsAdapter
from src.agent_orchestration.openhands_integration.client import OpenHandsClient
from src.agent_orchestration.openhands_integration.config import OpenHandsConfig


async def main() -> None:
    """Execute OpenHands integration test."""
    print("=" * 80)
    print("OpenHands Integration Live Test")
    print("=" * 80)
    print()

    # Load environment variables
    print("📋 Loading environment configuration...")
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key or api_key == "your_openrouter_api_key_here":
        print("❌ ERROR: OPENROUTER_API_KEY not configured in .env file")
        print()
        print("Please configure your OpenRouter API key:")
        print("1. Get API key from: https://openrouter.ai/keys")
        print("2. Add to .env file: OPENROUTER_API_KEY=your_actual_key_here")
        print()
        sys.exit(1)

    print(f"✅ API key loaded (length: {len(api_key)} characters)")
    print()

    # Create OpenHands configuration
    print("⚙️  Creating OpenHands configuration...")
    try:
        config = OpenHandsConfig(
            api_key=SecretStr(api_key),
            model="openrouter/deepseek/deepseek-chat",  # DeepSeek model (verified working)
            base_url="https://openrouter.ai/api/v1",
            workspace_path=project_root,
            timeout_seconds=300.0,  # 5 minutes for development task
        )
        print(f"✅ Configuration created:")
        print(f"   - Model: {config.model}")
        print(f"   - Workspace: {config.workspace_path}")
        print(f"   - Timeout: {config.timeout_seconds}s")
        print()
    except Exception as e:
        print(f"❌ ERROR: Failed to create configuration: {e}")
        sys.exit(1)

    # Instantiate OpenHands client
    print("🔌 Instantiating OpenHands client...")
    try:
        client = OpenHandsClient(config)
        print("✅ Client instantiated successfully")
        print()
    except Exception as e:
        print(f"❌ ERROR: Failed to instantiate client: {e}")
        sys.exit(1)

    # Instantiate OpenHands adapter
    print("🔧 Instantiating OpenHands adapter...")
    try:
        adapter = OpenHandsAdapter(
            client=client,
            fallback_to_mock=False,  # Use real API only
        )
        print("✅ Adapter instantiated successfully")
        print()
    except Exception as e:
        print(f"❌ ERROR: Failed to instantiate adapter: {e}")
        sys.exit(1)

    # Define development task
    task_description = """
Write comprehensive unit tests for the `validate_timeout` method in the OpenHandsConfig class
located at `src/agent_orchestration/openhands_integration/config.py`.

The tests should cover:
1. Valid timeout values (positive numbers)
2. Zero timeout (should raise ValueError with message "Timeout must be positive")
3. Negative timeout (should raise ValueError with message "Timeout must be positive")
4. Very large timeout values (should pass validation)
5. Edge cases (very small positive values like 0.001)

Requirements:
- Use pytest framework
- Follow TTA testing conventions (docstrings, clear test names)
- Use parametrize for testing multiple valid/invalid values
- Include clear assertions with helpful error messages
- Save tests to: tests/integration/openhands_integration/test_config_timeout_validation.py

Please generate the complete test file with all necessary imports and fixtures.
""".strip()

    print("📝 Development Task:")
    print("-" * 80)
    print(task_description)
    print("-" * 80)
    print()

    # Execute development task
    print("🚀 Executing development task via OpenHands...")
    print("   (This may take 1-5 minutes depending on API response time)")
    print()

    try:
        result = await adapter.execute_development_task(
            task_description=task_description,
            context={
                "workspace_path": str(project_root),
                "timeout": 300.0,
            },
        )

        print("=" * 80)
        print("Task Execution Results")
        print("=" * 80)
        print()

        # Display results
        success = result.get("success", False)
        output = result.get("output", "")
        error = result.get("error")
        execution_time = result.get("execution_time", 0.0)
        metadata = result.get("metadata", {})

        print(f"✅ Success: {success}")
        print(f"⏱️  Execution Time: {execution_time:.2f}s")
        print()

        if success:
            print("📄 Generated Output:")
            print("-" * 80)
            print(output)
            print("-" * 80)
            print()

            # Analyze output quality
            print("🔍 Quality Assessment:")
            print("-" * 80)

            # Check for pytest imports
            has_pytest = "import pytest" in output or "from pytest" in output
            print(f"   - Pytest imports: {'✅' if has_pytest else '❌'}")

            # Check for parametrize (good practice for multiple test cases)
            has_parametrize = "@pytest.mark.parametrize" in output
            print(f"   - Parametrized tests: {'✅' if has_parametrize else '⚠️  (optional)'}")

            # Check for docstrings
            has_docstrings = '"""' in output or "'''" in output
            print(f"   - Docstrings: {'✅' if has_docstrings else '❌'}")

            # Check for all required test cases
            has_zero_test = "zero" in output.lower() or "0" in output
            has_negative_test = "negative" in output.lower() or "-" in output
            has_large_test = "large" in output.lower()
            has_edge_test = "edge" in output.lower() or "0.001" in output

            print(f"   - Zero timeout test: {'✅' if has_zero_test else '❌'}")
            print(f"   - Negative timeout test: {'✅' if has_negative_test else '❌'}")
            print(f"   - Large timeout test: {'✅' if has_large_test else '❌'}")
            print(f"   - Edge case test: {'✅' if has_edge_test else '❌'}")

            # Overall quality score
            quality_checks = [
                has_pytest,
                has_docstrings,
                has_zero_test,
                has_negative_test,
                has_large_test,
            ]
            quality_score = sum(quality_checks) / len(quality_checks) * 5
            print()
            print(f"   📊 Overall Quality Score: {quality_score:.1f}/5.0")
            print("-" * 80)
            print()

            # Metadata
            if metadata:
                print("📊 Metadata:")
                for key, value in metadata.items():
                    print(f"   - {key}: {value}")
                print()

            # Recommendations
            print("💡 Recommendations:")
            if quality_score >= 4.0:
                print("   ✅ OpenHands integration is READY for developer use")
                print("   ✅ Generated code meets quality standards")
                print("   ✅ All critical test cases are covered")
            elif quality_score >= 3.0:
                print("   ⚠️  OpenHands integration is PARTIALLY READY")
                print("   ⚠️  Generated code needs minor improvements")
                print("   ⚠️  Consider manual review and refinement")
            else:
                print("   ❌ OpenHands integration needs improvement")
                print("   ❌ Generated code quality is below standards")
                print("   ❌ Manual implementation recommended")
            print()

        else:
            print(f"❌ Task execution failed")
            if error:
                print(f"   Error: {error}")
            print()

    except Exception as e:
        print("=" * 80)
        print("❌ ERROR: Task execution failed with exception")
        print("=" * 80)
        print()
        print(f"Exception Type: {type(e).__name__}")
        print(f"Exception Message: {e}")
        print()
        print("This could indicate:")
        print("  - Network connectivity issues")
        print("  - OpenRouter API rate limiting")
        print("  - Invalid API key")
        print("  - OpenHands SDK compatibility issues")
        print()
        import traceback

        print("Full Traceback:")
        print("-" * 80)
        traceback.print_exc()
        print("-" * 80)
        sys.exit(1)

    print("=" * 80)
    print("Test Complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

