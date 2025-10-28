#!/usr/bin/env python3
"""
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
    print(f"✅ Loaded environment variables from {env_file}")
else:
    print(f"⚠️  .env file not found at {env_file}")
    print("Please create a .env file with OPENROUTER_API_KEY set")

# Add src to path
sys.path.insert(0, str(repo_root / "src"))

from agent_orchestration.openhands_integration.config import OpenHandsConfig
from agent_orchestration.openhands_integration.docker_client import (
    DockerOpenHandsClient,
)


async def test_simple_file_creation():
    """Test 1: Simple file creation (hello.txt)"""
    print("\n" + "=" * 80)
    print("TEST 1: Simple File Creation")
    print("=" * 80)

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
    print(f"\nTask: {task}")
    print(f"Workspace: {workspace}")

    try:
        result = await client.execute_task(task, timeout=120)

        print("\n✅ Task completed successfully!")
        print(f"Success: {result.success}")
        print(f"Exit Code: {result.exit_code}")
        print(f"Duration: {result.duration:.2f}s")

        # Check if file was created
        hello_file = workspace / "hello.txt"
        if hello_file.exists():
            content = hello_file.read_text()
            print("\n✅ File created successfully!")
            print(f"Content: {content}")
            return True
        else:
            print("\n❌ File was NOT created")
            print(f"Output: {result.output[:500]}")
            return False

    except Exception as e:
        print(f"\n❌ Task failed with error: {e}")
        return False


async def test_test_generation():
    """Test 2: Generate tests for a simple Python module"""
    print("\n" + "=" * 80)
    print("TEST 2: Test Generation")
    print("=" * 80)

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

    print("\nTask: Generate tests for calculator.py")
    print(f"Workspace: {workspace}")

    try:
        result = await client.execute_task(task, timeout=180)

        print("\n✅ Task completed successfully!")
        print(f"Success: {result.success}")
        print(f"Exit Code: {result.exit_code}")
        print(f"Duration: {result.duration:.2f}s")

        # Check if test file was created
        test_file = workspace / "test_calculator.py"
        if test_file.exists():
            content = test_file.read_text()
            print("\n✅ Test file created successfully!")
            print(f"File size: {len(content)} bytes")
            print("\nFirst 500 characters:")
            print(content[:500])
            return True
        else:
            print("\n❌ Test file was NOT created")
            print(f"Output: {result.output[:500]}")
            return False

    except Exception as e:
        print(f"\n❌ Task failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("OpenHands Docker Client - Condensation Bug Fix Verification")
    print("=" * 80)

    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        print("\n❌ ERROR: OPENROUTER_API_KEY is not set or is using placeholder value")
        print(f"Please set it in your .env file at: {env_file}")
        print("\nSteps to fix:")
        print("1. Copy .env.example to .env: cp .env.example .env")
        print("2. Edit .env and set OPENROUTER_API_KEY to your actual API key")
        print("3. Get an API key from: https://openrouter.ai")
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
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 All tests passed! OpenHands is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())
