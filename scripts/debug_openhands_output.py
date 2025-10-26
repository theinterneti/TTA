#!/usr/bin/env python3
"""
Debug script to inspect OpenHands SDK conversation history structure.
This helps us understand how to properly extract agent output.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_orchestration.openhands_integration.config import (
    OpenHandsIntegrationConfig,
)
from src.agent_orchestration.openhands_integration.optimized_client import (
    OptimizedOpenHandsClient,
)


async def debug_conversation_structure():
    """Debug the conversation history structure."""
    print("\n" + "=" * 80)
    print("OPENHANDS SDK CONVERSATION STRUCTURE DEBUG")
    print("=" * 80)

    # Load config
    try:
        integration_config = OpenHandsIntegrationConfig.from_env()
        config = integration_config.to_client_config()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        return False

    # Create client
    client = OptimizedOpenHandsClient(config)

    # Initialize SDK
    client._initialize_sdk()
    client._initialize_agent()
    client._reset_conversation()

    # Send a simple task
    task = "Write a simple Python function that adds two numbers"
    print(f"\n📝 Task: {task}")
    print("⏳ Executing task...")

    client._conversation.send_message(task)
    client._conversation.run()

    print("\n✅ Task completed")

    # Inspect conversation structure
    print("\n🔍 Inspecting conversation structure...")
    print(f"   Conversation type: {type(client._conversation)}")
    print(f"   Conversation attributes: {dir(client._conversation)}")

    # Check for history
    if hasattr(client._conversation, "history"):
        history = client._conversation.history
        print("\n📋 History found!")
        print(f"   History type: {type(history)}")
        print(f"   History length: {len(history)}")

        # Inspect each event
        for i, event in enumerate(history):
            print(f"\n   Event {i}:")
            print(f"      Type: {type(event)}")
            print(f"      Attributes: {dir(event)}")

            # Try to extract useful info
            if hasattr(event, "source"):
                print(f"      Source: {event.source}")
            if hasattr(event, "message"):
                print(f"      Message: {str(event.message)[:200]}")
            if hasattr(event, "content"):
                print(f"      Content: {str(event.content)[:200]}")
            if hasattr(event, "action"):
                print(f"      Action: {event.action}")
            if hasattr(event, "observation"):
                print(f"      Observation: {str(event.observation)[:200]}")

            # Print all attributes with values
            print("      All attributes:")
            for attr in dir(event):
                if not attr.startswith("_"):
                    try:
                        value = getattr(event, attr)
                        if not callable(value):
                            print(f"         {attr}: {str(value)[:100]}")
                    except Exception as e:
                        print(f"         {attr}: <error: {e}>")
    else:
        print("\n❌ No history attribute found")

        # Check for agent_final_response (it's a method!)
        if hasattr(client._conversation, "agent_final_response"):
            print("\n📋 agent_final_response found!")
            try:
                response = client._conversation.agent_final_response()
                print(f"   Type: {type(response)}")
                print(f"   Value: {str(response)[:500]}")
            except Exception as e:
                print(f"   Error calling agent_final_response(): {e}")

    # Check for other output methods
    print("\n🔍 Checking for other output methods...")
    if hasattr(client._conversation, "messages"):
        print(f"   Messages found: {len(client._conversation.messages)}")
        for i, msg in enumerate(client._conversation.messages[:3]):
            print(f"      Message {i}: {str(msg)[:200]}")

    if hasattr(client._conversation, "state"):
        print(f"   State found: {client._conversation.state}")

    # Try to get the last agent message
    print("\n🔍 Extracting agent output...")
    output_lines = []
    if hasattr(client._conversation, "history"):
        for event in reversed(client._conversation.history):
            if hasattr(event, "source") and event.source == "agent":
                if hasattr(event, "message"):
                    output_lines.append(event.message)
                elif hasattr(event, "content"):
                    output_lines.append(event.content)
                if len(output_lines) >= 5:
                    break

    if output_lines:
        print(f"   ✅ Found {len(output_lines)} agent messages")
        for i, line in enumerate(output_lines):
            print(f"      Message {i}: {str(line)[:200]}")
    else:
        print("   ❌ No agent messages found")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(debug_conversation_structure())
