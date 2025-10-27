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
    print("\n" + "=" * 80)
    print("OpenHands Integration Test with Real Credentials")
    print("=" * 80 + "\n")

    # Step 1: Load configuration from environment
    print("Step 1: Loading configuration from environment...")
    try:
        from agent_orchestration.openhands_integration.config import (
            OpenHandsIntegrationConfig,
        )

        config = OpenHandsIntegrationConfig.from_env()
        print("✓ Configuration loaded successfully")
        print(f"  - API Key: {config.api_key.get_secret_value()[:20]}...")
        print(f"  - Model: {config.model_preset}")
        print(f"  - Base URL: {config.base_url}")
        print(f"  - Workspace: {config.workspace_root}")
        print(f"  - Timeout: {config.default_timeout_seconds}s")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False

    # Step 2: Initialize Docker client
    print("\nStep 2: Initializing DockerOpenHandsClient...")
    try:
        from agent_orchestration.openhands_integration.docker_client import (
            DockerOpenHandsClient,
        )

        # Create OpenHandsConfig from integration config
        client_config = config.to_client_config()

        client = DockerOpenHandsClient(client_config)
        print("✓ DockerOpenHandsClient initialized")
        print(f"  - Image: {client.openhands_image}")
        print(f"  - Runtime: {client.runtime_image}")
    except Exception as e:
        print(f"✗ Failed to initialize client: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 3: Create workspace
    print("\nStep 3: Preparing workspace...")
    try:
        workspace = config.workspace_root
        workspace.mkdir(parents=True, exist_ok=True)
        print(f"✓ Workspace ready: {workspace}")
        print(f"  - Exists: {workspace.exists()}")
        print(f"  - Writable: {workspace.is_dir()}")
    except Exception as e:
        print(f"✗ Failed to prepare workspace: {e}")
        return False

    # Step 4: Execute test task
    print("\nStep 4: Executing test task via Docker...")
    print(
        "  Task: Create a file named 'openhands_test.txt' with content 'Hello from OpenHands'"
    )
    try:
        task_description = "Create a file named 'openhands_test.txt' in the workspace with content 'Hello from OpenHands'"

        result = await client.execute_task(
            task_description=task_description,
            workspace_path=workspace,
            timeout=config.default_timeout_seconds,
        )

        print("✓ Task executed")
        print(f"  - Success: {result.success}")
        print(f"  - Execution time: {result.execution_time:.2f}s")
        if result.error:
            print(f"  - Error: {result.error}")
        print(f"  - Output: {result.output[:200]}...")
        print(f"  - Metadata: {result.metadata}")

    except Exception as e:
        print(f"✗ Task execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 5: Verify file creation
    print("\nStep 5: Verifying file creation...")
    try:
        test_file = workspace / "openhands_test.txt"
        if test_file.exists():
            content = test_file.read_text()
            print("✓ File created successfully")
            print(f"  - Path: {test_file}")
            print(f"  - Size: {test_file.stat().st_size} bytes")
            print(f"  - Content: {content}")
        else:
            print(f"✗ File not found: {test_file}")
            print(f"  - Workspace contents: {list(workspace.glob('*'))}")
            return False

    except Exception as e:
        print(f"✗ File verification failed: {e}")
        return False

    # Step 6: Summary
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - OpenHands integration is working correctly!")
    print("=" * 80 + "\n")

    print("Next steps:")
    print("1. Review the generated file in the workspace")
    print("2. Integrate OpenHands with the TTA test generation pipeline")
    print("3. Configure batch processing for multiple modules")
    print("4. Set up monitoring and metrics collection\n")

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
