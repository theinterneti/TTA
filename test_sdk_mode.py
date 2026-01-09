#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Test_sdk_mode]]
Test OpenHands SDK mode for file generation capability.

This script tests whether the OpenHands Python SDK can create files.
According to documentation, SDK mode only has 2 tools (think, finish) and
cannot execute bash or create files.
"""

import asyncio
import os
import sys
from pathlib import Path

from pydantic import SecretStr

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent_orchestration.openhands_integration.client import OpenHandsClient
from agent_orchestration.openhands_integration.config import OpenHandsConfig


async def test_sdk_mode():
    """Test SDK mode file generation."""
    print("=" * 80)
    print("TEST: OpenHands SDK Mode File Generation")
    print("=" * 80)

    # Create test workspace
    workspace = Path("/tmp/openhands_sdk_test")
    workspace.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Created workspace: {workspace}")

    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("\n❌ ERROR: OPENROUTER_API_KEY not set")
        return False

    # Create config
    config = OpenHandsConfig(
        api_key=SecretStr(api_key),
        model="openrouter/deepseek/deepseek-chat-v3.1:free",
        workspace_path=workspace,
        timeout_seconds=60,
    )
    print(f"✓ Created config with model: {config.model}")

    # Create client
    client = OpenHandsClient(config)
    print("✓ Created OpenHandsClient")

    # Test task: create a file
    task = "Create a file named test_sdk.txt with content 'Hello from SDK mode'"
    print(f"\n📝 Task: {task}")
    print("\nExecuting task...")

    try:
        result = await client.execute_task(task)

        print(f"\n✓ Task completed in {result.execution_time:.2f}s")
        print(f"  Success: {result.success}")
        print(f"  Error: {result.error}")
        print(f"\nOutput:\n{result.output[:500]}")

        # Check if file was created
        test_file = workspace / "test_sdk.txt"
        if test_file.exists():
            print(f"\n✅ SUCCESS: File created at {test_file}")
            print(f"   Content: {test_file.read_text()}")
            return True
        print(f"\n❌ FAILED: File not created at {test_file}")
        print(f"   Workspace contents: {list(workspace.glob('*'))}")
        return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        await client.cleanup()
        print("\n✓ Cleaned up client")


if __name__ == "__main__":
    success = asyncio.run(test_sdk_mode())
    sys.exit(0 if success else 1)
