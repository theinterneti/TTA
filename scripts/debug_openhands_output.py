# ruff: noqa: ALL
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

import contextlib

from src.agent_orchestration.openhands_integration.config import (
    OpenHandsIntegrationConfig,
)
from src.agent_orchestration.openhands_integration.optimized_client import (
    OptimizedOpenHandsClient,
)


async def debug_conversation_structure():
    """Debug the conversation history structure."""

    # Load config
    try:
        integration_config = OpenHandsIntegrationConfig.from_env()
        config = integration_config.to_client_config()
    except ValueError:
        return False

    # Create client
    client = OptimizedOpenHandsClient(config)

    # Initialize SDK
    client._initialize_sdk()
    client._initialize_agent()
    client._reset_conversation()

    # Send a simple task
    task = "Write a simple Python function that adds two numbers"

    client._conversation.send_message(task)
    client._conversation.run()

    # Inspect conversation structure

    # Check for history
    if hasattr(client._conversation, "history"):
        history = client._conversation.history

        # Inspect each event
        for _i, event in enumerate(history):
            # Try to extract useful info
            if hasattr(event, "source"):
                pass
            if hasattr(event, "message"):
                pass
            if hasattr(event, "content"):
                pass
            if hasattr(event, "action"):
                pass
            if hasattr(event, "observation"):
                pass

            # Print all attributes with values
            for attr in dir(event):
                if not attr.startswith("_"):
                    try:
                        value = getattr(event, attr)
                        if not callable(value):
                            pass
                    except Exception:
                        pass

    # Check for agent_final_response (it's a method!)
    elif hasattr(client._conversation, "agent_final_response"):
        with contextlib.suppress(Exception):
            client._conversation.agent_final_response()

    # Check for other output methods
    if hasattr(client._conversation, "messages"):
        for _i, _msg in enumerate(client._conversation.messages[:3]):
            pass

    if hasattr(client._conversation, "state"):
        pass

    # Try to get the last agent message
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
        for _i, _line in enumerate(output_lines):
            pass
    else:
        pass

    return None


if __name__ == "__main__":
    asyncio.run(debug_conversation_structure())
