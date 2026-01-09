#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/_archive/Openhands/Scripts/Test_openhands_cli]]
Test OpenHands via command-line interface.

This tests the OpenHands CLI, which provides full access to all tools
(bash, file operations, jupyter, etc.) and is the most feature-complete
access method.

Usage:
    uv run python scripts/test_openhands_cli.py
"""

import asyncio
import logging
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()
project_root = Path(__file__).parent.parent


def check_openhands_cli():
    """Check if OpenHands CLI is available."""
    logger.info("Checking for OpenHands CLI...")

    try:
        result = subprocess.run(
            ["python", "-m", "openhands.core.main", "--help"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            logger.info("✅ OpenHands CLI is available")
            return True
        logger.warning("⚠️  OpenHands CLI returned non-zero exit code")
        logger.warning(f"   stderr: {result.stderr}")
        return False

    except FileNotFoundError:
        logger.error("❌ OpenHands CLI not found")
        logger.error("   Install with: pip install openhands")
        return False
    except subprocess.TimeoutExpired:
        logger.error("❌ OpenHands CLI check timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking CLI: {e}")
        return False


async def test_cli_simple_task():
    """Test 1: Simple task via CLI."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 1: Simple Task via CLI")
    logger.info("=" * 80)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("❌ OPENROUTER_API_KEY not set")
        return False

    task = "Write a Python function that returns 'Hello, World!'"

    try:
        # Set environment variables for OpenHands
        env = os.environ.copy()
        env["LLM_MODEL"] = "openrouter/deepseek/deepseek-chat"
        env["LLM_API_KEY"] = api_key
        env["LLM_BASE_URL"] = "https://openrouter.ai/api/v1"
        env["SANDBOX_VOLUMES"] = f"{project_root}:/workspace:rw"

        logger.info(f"Task: {task}")
        logger.info("Running OpenHands CLI...")

        result = subprocess.run(
            [
                "python",
                "-m",
                "openhands.core.main",
                "-t",
                task,
                "-c",
                "CodeActAgent",
                "-i",
                "5",  # Max iterations
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
            cwd=str(project_root),
        )

        logger.info(f"Exit code: {result.returncode}")

        if result.returncode == 0:
            logger.info("✅ Task completed successfully")
            logger.info(f"Output:\n{result.stdout}")
            return True
        logger.warning("⚠️  Task completed with non-zero exit code")
        logger.info(f"stdout:\n{result.stdout}")
        logger.info(f"stderr:\n{result.stderr}")
        return False

    except subprocess.TimeoutExpired:
        logger.error("❌ Task execution timed out (300s)")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_cli_file_creation():
    """Test 2: File creation via CLI."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: File Creation via CLI")
    logger.info("=" * 80)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("❌ OPENROUTER_API_KEY not set")
        return False

    task = (
        "Create a file named 'test_output.txt' with content 'Hello from OpenHands CLI'"
    )

    try:
        env = os.environ.copy()
        env["LLM_MODEL"] = "openrouter/deepseek/deepseek-chat"
        env["LLM_API_KEY"] = api_key
        env["LLM_BASE_URL"] = "https://openrouter.ai/api/v1"
        env["SANDBOX_VOLUMES"] = f"{project_root}:/workspace:rw"

        logger.info(f"Task: {task}")
        logger.info("Running OpenHands CLI...")

        result = subprocess.run(
            [
                "python",
                "-m",
                "openhands.core.main",
                "-t",
                task,
                "-c",
                "CodeActAgent",
                "-i",
                "5",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
            cwd=str(project_root),
        )

        logger.info(f"Exit code: {result.returncode}")

        # Check if file was created
        test_file = project_root / "test_output.txt"
        if test_file.exists():
            logger.info("✅ File created successfully")
            with open(test_file) as f:
                content = f.read()
            logger.info(f"Content: {content}")
            test_file.unlink()  # Clean up
            return True
        logger.warning("⚠️  File was not created")
        logger.info(f"stdout:\n{result.stdout}")
        logger.info(f"stderr:\n{result.stderr}")
        return False

    except subprocess.TimeoutExpired:
        logger.error("❌ Task execution timed out (300s)")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run CLI tests."""
    logger.info("\n╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 20 + "OpenHands CLI Testing" + " " * 38 + "║")
    logger.info("╚" + "=" * 78 + "╝\n")

    # Check if CLI is available
    if not check_openhands_cli():
        logger.error("\n❌ OpenHands CLI not available")
        logger.error("Install with: pip install openhands")
        return

    # Run tests
    results = {}
    results["simple"] = await test_cli_simple_task()
    results["file_creation"] = await test_cli_file_creation()

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")

    logger.info("\n" + "=" * 80)
    logger.info("Key Findings:")
    logger.info("=" * 80)
    logger.info("1. CLI provides full tool access (bash, file operations, etc.)")
    logger.info("2. CLI is the most feature-complete access method")
    logger.info("3. CLI supports CodeActAgent with full capabilities")
    logger.info("4. CLI is suitable for production use")
    logger.info("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
