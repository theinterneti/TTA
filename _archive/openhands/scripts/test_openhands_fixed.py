#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/_archive/Openhands/Scripts/Test_openhands_fixed]]
Test script to verify OpenHands Docker client works with condensation bug fix.

This script tests the fixed OpenHands implementation with:
1. --no-condense flag added to command
2. CONDENSATION_ENABLED=false environment variable
3. MAX_CONDENSATION_ATTEMPTS=0 environment variable

The script automatically loads environment variables from the .env file at the
repository root, so you don't need to manually export OPENROUTER_API_KEY.

Usage:
    python scripts/test_openhands_fixed.py
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr

# Load environment variables from .env file at repository root
repo_root = Path(__file__).parent.parent
env_file = repo_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    pass

# Add src to path
sys.path.insert(0, str(repo_root / "src"))

from agent_orchestration.openhands_integration.config import OpenHandsConfig
from agent_orchestration.openhands_integration.docker_client import (
    DockerOpenHandsClient,
)


async def test_simple_file_creation():
    """Test 1: Simple file creation (hello.txt)"""

    # Setup
    workspace = Path("/tmp/openhands_test_fixed")
    workspace.mkdir(exist_ok=True)

    config = OpenHandsConfig(
        api_key=SecretStr(os.getenv("OPENROUTER_API_KEY", "")),
        model="deepseek/deepseek-chat-v3.1:free",
        base_url="https://openrouter.ai/api/v1",
        workspace_path=workspace,
    )

    client = DockerOpenHandsClient(config)

    # Execute task
    task = "Create a file named hello.txt with content 'Hello from OpenHands with condensation fix!'"

    try:
        await client.execute_task(task, timeout=120)

        # Check if file was created
        hello_file = workspace / "hello.txt"
        if hello_file.exists():
            hello_file.read_text()
            return True
        return False

    except Exception:
        return False


async def test_test_generation():
    """Test 2: Generate tests for a simple Python module"""

    # Setup
    workspace = Path("/tmp/openhands_test_fixed")
    workspace.mkdir(exist_ok=True)

    # Create a simple module to test
    module_file = workspace / "calculator.py"
    module_file.write_text("""
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b

def subtract(a: int, b: int) -> int:
    \"\"\"Subtract b from a.\"\"\"
    return a - b

def multiply(a: int, b: int) -> int:
    \"\"\"Multiply two numbers.\"\"\"
    return a * b
""")

    config = OpenHandsConfig(
        api_key=SecretStr(os.getenv("OPENROUTER_API_KEY", "")),
        model="deepseek/deepseek-chat-v3.1:free",
        base_url="https://openrouter.ai/api/v1",
        workspace_path=workspace,
    )

    client = DockerOpenHandsClient(config)

    # Execute task
    task = """
Generate comprehensive unit tests for the calculator.py module.
Create a file named test_calculator.py with pytest tests that:
1. Test the add() function with positive and negative numbers
2. Test the subtract() function with positive and negative numbers
3. Test the multiply() function with positive and negative numbers
4. Include edge cases (zero, negative numbers)
"""

    try:
        await client.execute_task(task, timeout=180)

        # Check if test file was created
        test_file = workspace / "test_calculator.py"
        if test_file.exists():
            test_file.read_text()
            return True
        return False

    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests"""

    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        return

    # Run tests
    results = []

    # Test 1: Simple file creation
    test1_passed = await test_simple_file_creation()
    results.append(("Simple File Creation", test1_passed))

    # Test 2: Test generation
    test2_passed = await test_test_generation()
    results.append(("Test Generation", test2_passed))

    # Summary

    for _test_name, _passed in results:
        pass

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    if total_passed == total_tests:
        pass
    else:
        pass


if __name__ == "__main__":
    asyncio.run(main())
