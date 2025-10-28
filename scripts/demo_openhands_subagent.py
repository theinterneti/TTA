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
    print(f"✅ Loaded environment variables from {env_file}")
else:
    print(f"⚠️  .env file not found at {env_file}")

# Add src to path
sys.path.insert(0, str(repo_root / "src"))

from agent_orchestration.openhands_integration.config import OpenHandsConfig
from agent_orchestration.openhands_integration.docker_client import (
    DockerOpenHandsClient,
)


async def demo_simple_task():
    """Demo: Use OpenHands to create a simple Python utility function"""
    print("\n" + "=" * 80)
    print("DEMO: Using OpenHands as a Sub-Agent")
    print("=" * 80)
    
    # Setup workspace
    workspace = Path("/tmp/openhands_demo")
    workspace.mkdir(exist_ok=True)
    print(f"\n📁 Workspace: {workspace}")
    
    # Configure OpenHands
    config = OpenHandsConfig(
        api_key=SecretStr(os.getenv("OPENROUTER_API_KEY")),
        model="deepseek/deepseek-chat-v3.1:free",
        base_url="https://openrouter.ai/api/v1",
        workspace_path=workspace,
    )
    
    # Create client
    print("\n🤖 Creating OpenHands sub-agent...")
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
    
    print(f"\n📝 Task for sub-agent:")
    print(task)
    
    print("\n⏳ Executing task (this may take 30-60 seconds)...")
    
    try:
        result = await client.execute_task(task, timeout=120)
        
        if result.success:
            print("\n✅ Task completed successfully!")
            print(f"⏱️  Duration: {result.duration:.2f}s")
            print(f"🔢 Exit Code: {result.exit_code}")
            
            # Check if file was created
            output_file = workspace / "string_utils.py"
            if output_file.exists():
                print(f"\n✅ File created: {output_file}")
                content = output_file.read_text()
                print(f"\n📄 Generated code ({len(content)} bytes):")
                print("-" * 80)
                print(content)
                print("-" * 80)
                
                # Test the generated code
                print("\n🧪 Testing generated code...")
                try:
                    # Import the module
                    sys.path.insert(0, str(workspace))
                    import string_utils
                    
                    # Test functions
                    print(f"reverse_string('hello'): {string_utils.reverse_string('hello')}")
                    print(f"is_palindrome('racecar'): {string_utils.is_palindrome('racecar')}")
                    print(f"count_vowels('hello'): {string_utils.count_vowels('hello')}")
                    
                    print("\n✅ All functions work correctly!")
                    
                except Exception as e:
                    print(f"\n⚠️  Error testing code: {e}")
                
                return True
            else:
                print(f"\n❌ File was NOT created")
                print(f"Output: {result.output[:500]}")
                return False
        else:
            print(f"\n❌ Task failed")
            print(f"Exit Code: {result.exit_code}")
            print(f"Output: {result.output[:500]}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the demo"""
    print("\n" + "=" * 80)
    print("OpenHands Sub-Agent Demo")
    print("=" * 80)
    print("\nThis demo shows how to use OpenHands as a development assistant")
    print("sub-agent to perform simple tasks like generating code.")
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        print("\n❌ ERROR: OPENROUTER_API_KEY is not set or is using placeholder value")
        print(f"Please set it in your .env file at: {env_file}")
        return
    
    print(f"\n✅ API key is set")
    
    # Run demo
    success = await demo_simple_task()
    
    # Summary
    print("\n" + "=" * 80)
    print("DEMO SUMMARY")
    print("=" * 80)
    
    if success:
        print("\n🎉 SUCCESS! OpenHands sub-agent completed the task.")
        print("\n✅ What this demonstrates:")
        print("  - OpenHands can be used as a sub-agent for development tasks")
        print("  - It automatically loads .env file (no manual export needed)")
        print("  - It can generate code, create files, and perform other tasks")
        print("  - The generated code is functional and ready to use")
        print("\n💡 Use cases:")
        print("  - Generate utility functions")
        print("  - Create test files")
        print("  - Scaffold new components")
        print("  - Refactor existing code")
        print("  - Generate documentation")
    else:
        print("\n⚠️  Demo did not complete successfully.")
        print("Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())

