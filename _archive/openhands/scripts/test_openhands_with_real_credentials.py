#!/usr/bin/env python3
# ruff: noqa: ALL
"""
Test OpenHands integration with real OpenRouter API credentials.

This script:
1. Loads the OpenRouter API key from .env file
2. Initializes the DockerOpenHandsClient with real credentials
3. Executes a simple test task to verify end-to-end functionality
4. Validates that files are created in the workspace
5. Reports success/failure with detailed diagnostics

Usage:
    python scripts/test_openhands_with_real_credentials.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def main():
    """Run the OpenHands integration test."""

    # Step 1: Load configuration from environment
    try:
        from agent_orchestration.openhands_integration.config import (
            OpenHandsIntegrationConfig,
        )

        config = OpenHandsIntegrationConfig.from_env()
    except Exception:
        return False

    # Step 2: Initialize Docker client
    try:
        from agent_orchestration.openhands_integration.docker_client import (
            DockerOpenHandsClient,
        )

        # Create OpenHandsConfig from integration config
        client_config = config.to_client_config()

        client = DockerOpenHandsClient(client_config)
    except Exception:
        import traceback

        traceback.print_exc()
        return False

    # Step 3: Create workspace
    try:
        workspace = config.workspace_root
        workspace.mkdir(parents=True, exist_ok=True)
    except Exception:
        return False

    # Step 4: Execute test task
    try:
        task_description = "Create a file named 'openhands_test.txt' in the workspace with content 'Hello from OpenHands'"

        result = await client.execute_task(
            task_description=task_description,
            workspace_path=workspace,
            timeout=config.default_timeout_seconds,
        )

        if result.error:
            pass

    except Exception:
        import traceback

        traceback.print_exc()
        return False

    # Step 5: Verify file creation
    try:
        test_file = workspace / "openhands_test.txt"
        if test_file.exists():
            test_file.read_text()
        else:
            return False

    except Exception:
        return False

    # Step 6: Summary

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
