#!/usr/bin/env python3
"""
Demo: Using OpenHands as a Sub-Agent

This script demonstrates using OpenHands as a development assistant sub-agent
to perform simple tasks like creating files, generating code, etc.

Usage:
    python scripts/demo_openhands_subagent.py
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


async def demo_simple_task():
    """Demo: Use OpenHands to create a simple Python utility function"""

    # Setup workspace
    workspace = Path("/tmp/openhands_demo")
    workspace.mkdir(exist_ok=True)

    # Configure OpenHands
    config = OpenHandsConfig(
        api_key=SecretStr(os.getenv("OPENROUTER_API_KEY")),
        model="deepseek/deepseek-chat-v3.1:free",
        base_url="https://openrouter.ai/api/v1",
        workspace_path=workspace,
    )

    # Create client
    client = DockerOpenHandsClient(config)

    # Task: Create a simple utility function
    task = """
Create a Python file named string_utils.py with the following utility functions:

1. reverse_string(s: str) -> str
   - Reverses a string
   - Example: reverse_string("hello") -> "olleh"

2. is_palindrome(s: str) -> bool
   - Checks if a string is a palindrome (case-insensitive)
   - Example: is_palindrome("racecar") -> True

3. count_vowels(s: str) -> int
   - Counts the number of vowels in a string
   - Example: count_vowels("hello") -> 2

Include:
- Type hints for all functions
- Docstrings with examples
- Clean, readable code
"""

    try:
        result = await client.execute_task(task, timeout=120)

        if result.success:
            # Check if file was created
            output_file = workspace / "string_utils.py"
            if output_file.exists():
                output_file.read_text()

                # Test the generated code
                try:
                    # Import the module
                    sys.path.insert(0, str(workspace))

                    # Test functions

                except Exception:
                    pass

                return True
            return False
        return False

    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the demo"""

    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        return

    # Run demo
    success = await demo_simple_task()

    # Summary

    if success:
        pass
    else:
        pass


if __name__ == "__main__":
    asyncio.run(main())
