#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/_archive/Openhands/Scripts/Test_openhands_e2e]]
End-to-end test for OpenHands integration.

Tests:
1. Simple file creation
2. Workspace file verification
3. Model rotation (if primary fails)
4. Metrics collection
"""

import asyncio
import logging
import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from pydantic import SecretStr

from agent_orchestration.openhands_integration import (
    DockerOpenHandsClient,
    OpenHandsConfig,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_simple_file_creation():
    """Test creating a simple file with OpenHands."""
    logger.info("=" * 80)
    logger.info("TEST: Simple File Creation with OpenHands")
    logger.info("=" * 80)

    # Create temporary workspace
    workspace = Path(tempfile.mkdtemp(prefix="openhands_e2e_"))
    logger.info(f"Workspace: {workspace}")

    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key.startswith("your_"):
        logger.error("OPENROUTER_API_KEY not set properly")
        return False

    # Create config
    config = OpenHandsConfig(
        api_key=SecretStr(api_key),
        model="openrouter/deepseek/deepseek-chat-v3.1:free",
        workspace_path=workspace,
        timeout_seconds=120,
    )

    # Create client
    client = DockerOpenHandsClient(config)
    logger.info(f"Client initialized: {client.openhands_image}")

    # Define task
    task_description = "Create a file named hello.txt with the content 'Hello from OpenHands! This is a validation test.'"
    logger.info(f"Task: {task_description}")

    # Execute task
    try:
        logger.info("Executing task (this may take 60-120 seconds)...")
        result = await client.execute_task(
            task_description=task_description, workspace_path=workspace, timeout=120.0
        )

        logger.info(f"Task completed: success={result.success}")
        logger.info(f"Output length: {len(result.output)} chars")

        # Check if file was created
        hello_file = workspace / "hello.txt"
        if hello_file.exists():
            content = hello_file.read_text()
            logger.info("✅ File created successfully!")
            logger.info(f"Content: {content}")
            return True
        logger.error(f"❌ File not created at {hello_file}")
        logger.info(f"Workspace contents: {list(workspace.iterdir())}")
        return False

    except Exception as e:
        logger.error(f"❌ Task execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Cleanup
        await client.cleanup()


async def main():
    """Run all tests."""
    logger.info("\n🚀 Starting OpenHands End-to-End Tests\n")

    # Test 1: Simple file creation
    test1_passed = await test_simple_file_creation()

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Simple File Creation: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    logger.info("=" * 80 + "\n")

    return 0 if test1_passed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
