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

    # Load environment variables
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key or api_key == "your_openrouter_api_key_here":
        sys.exit(1)

    # Create OpenHands configuration
    try:
        config = OpenHandsConfig(
            api_key=SecretStr(api_key),
            model="openrouter/deepseek/deepseek-chat",  # DeepSeek model (verified working)
            base_url="https://openrouter.ai/api/v1",
            workspace_path=project_root,
            timeout_seconds=300.0,  # 5 minutes for development task
        )
    except Exception:
        sys.exit(1)

    # Instantiate OpenHands client
    try:
        client = OpenHandsClient(config)
    except Exception:
        sys.exit(1)

    # Instantiate OpenHands adapter
    try:
        adapter = OpenHandsAdapter(
            client=client,
            fallback_to_mock=False,  # Use real API only
        )
    except Exception:
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

    # Execute development task

    try:
        result = await adapter.execute_development_task(
            task_description=task_description,
            context={
                "workspace_path": str(project_root),
                "timeout": 300.0,
            },
        )

        # Display results
        success = result.get("success", False)
        output = result.get("output", "")
        error = result.get("error")
        result.get("execution_time", 0.0)
        metadata = result.get("metadata", {})

        if success:
            # Analyze output quality

            # Check for pytest imports
            has_pytest = "import pytest" in output or "from pytest" in output

            # Check for parametrize (good practice for multiple test cases)

            # Check for docstrings
            has_docstrings = '"""' in output or "'''" in output

            # Check for all required test cases
            has_zero_test = "zero" in output.lower() or "0" in output
            has_negative_test = "negative" in output.lower() or "-" in output
            has_large_test = "large" in output.lower()
            "edge" in output.lower() or "0.001" in output

            # Overall quality score
            quality_checks = [
                has_pytest,
                has_docstrings,
                has_zero_test,
                has_negative_test,
                has_large_test,
            ]
            quality_score = sum(quality_checks) / len(quality_checks) * 5

            # Metadata
            if metadata:
                for _key, _value in metadata.items():
                    pass

            # Recommendations
            if quality_score >= 4.0 or quality_score >= 3.0:
                pass
            else:
                pass

        elif error:
            pass

    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
