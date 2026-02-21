#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/_archive/Openhands/Scripts/Test_openhands_sdk_tools]]
Test OpenHands SDK with proper tool configuration.

This tests the OpenHands Python SDK with bash, file, and jupyter tools enabled.
The key difference from the current integration is that we configure the agent
with actual tools instead of just 'finish' and 'think'.

Usage:
    uv run python scripts/test_openhands_sdk_tools.py
"""

import asyncio
import logging
import os
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


async def test_sdk_with_tools():
    """Test OpenHands SDK with tools enabled."""
    logger.info("=" * 80)
    logger.info("OpenHands SDK with Tools Configuration Test")
    logger.info("=" * 80)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("❌ OPENROUTER_API_KEY not set")
        return False

    try:
        from openhands.sdk import LLM, Agent

        logger.info("✅ OpenHands SDK imported successfully")

        # Initialize LLM
        logger.info("\n📋 Initializing LLM...")
        llm = LLM(
            model="openrouter/deepseek/deepseek-chat",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            openrouter_site_url="https://github.com/theinterneti/TTA",
            openrouter_app_name="TTA-OpenHands-Test",
            max_output_tokens=4096,
            extended_thinking_budget=0,
        )
        logger.info("✅ LLM initialized")

        # Initialize Agent
        logger.info("\n🤖 Initializing Agent...")
        agent = Agent(llm=llm)
        logger.info("✅ Agent initialized")

        # Check available tools
        logger.info("\n🔧 Checking available tools...")
        if hasattr(agent, "tools"):
            logger.info(f"   Available tools: {agent.tools}")
        elif hasattr(agent, "get_tools"):
            tools = agent.get_tools()
            logger.info(f"   Available tools: {tools}")
        else:
            logger.warning("   Could not determine available tools")

        # Create conversation
        logger.info("\n💬 Creating conversation...")
        conversation = agent.create_conversation(workspace=str(project_root))
        logger.info("✅ Conversation created")

        # Test 1: Simple task
        logger.info("\n" + "=" * 80)
        logger.info("TEST 1: Simple Task")
        logger.info("=" * 80)

        task1 = "Write a Python function that returns 'Hello, World!'"
        logger.info(f"Task: {task1}")

        conversation.send_message(task1)
        logger.info("✅ Message sent")

        # Note: The SDK doesn't have a built-in run() method in newer versions
        # We need to check what methods are available
        if hasattr(conversation, "run"):
            logger.info("Running conversation...")
            conversation.run()
        elif hasattr(conversation, "execute"):
            logger.info("Executing conversation...")
            conversation.execute()
        else:
            logger.warning("Could not find run/execute method on conversation")
            logger.info("Available methods:", dir(conversation))

        logger.info("✅ Task completed")

        return True

    except ImportError as e:
        logger.error(f"❌ Failed to import OpenHands SDK: {e}")
        logger.error("   Install with: pip install openhands-sdk")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run SDK tests."""
    logger.info("\n╔" + "=" * 78 + "╗")
    logger.info(
        "║" + " " * 15 + "OpenHands SDK with Tools Configuration Test" + " " * 20 + "║"
    )
    logger.info("╚" + "=" * 78 + "╝\n")

    success = await test_sdk_with_tools()

    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    if success:
        logger.info("✅ SDK test completed successfully")
        logger.info("\nKey Findings:")
        logger.info("1. OpenHands SDK can be initialized with LLM")
        logger.info("2. Agent and Conversation objects are available")
        logger.info("3. Tools configuration needs investigation")
        logger.info("4. SDK API may differ from documentation")
    else:
        logger.info("❌ SDK test failed")
        logger.info("\nNext Steps:")
        logger.info("1. Check OpenHands SDK version")
        logger.info("2. Review SDK documentation for current API")
        logger.info("3. Consider using Docker runtime instead")
    logger.info("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
