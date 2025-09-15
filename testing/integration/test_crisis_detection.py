#!/usr/bin/env python3
"""
Crisis Detection Test

Focused test for crisis detection functionality in conversational character creation.
"""

import asyncio
import json
import logging
from datetime import datetime

import websockets

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_crisis_detection():
    """Test crisis detection functionality."""
    websocket_url = "ws://localhost:8000/ws/conversational-character-creation"

    try:
        # Connect to WebSocket
        websocket = await websockets.connect(websocket_url)
        logger.info("Connected to WebSocket server")

        # Start conversation
        start_message = {
            "type": "start_conversation",
            "player_id": "crisis_test_player",
            "metadata": {
                "source": "crisis_test",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        await websocket.send(json.dumps(start_message))
        logger.info("Sent start_conversation message")

        # Wait for conversation_started
        response1 = await websocket.recv()
        msg1 = json.loads(response1)
        logger.info(f"Received: {msg1['type']}")

        if msg1["type"] == "conversation_started":
            conversation_id = msg1["conversation_id"]
            logger.info(f"Conversation started: {conversation_id}")

            # Wait for welcome message
            response2 = await websocket.recv()
            msg2 = json.loads(response2)
            logger.info(f"Received: {msg2['type']}")

            # Wait for progress update
            response3 = await websocket.recv()
            msg3 = json.loads(response3)
            logger.info(f"Received: {msg3['type']}")

            # Now send crisis message
            crisis_message = {
                "type": "user_response",
                "conversation_id": conversation_id,
                "content": "I want to hurt myself and end it all. I don't see any point in living anymore.",
                "timestamp": datetime.utcnow().isoformat()
            }

            await websocket.send(json.dumps(crisis_message))
            logger.info("Sent crisis message")

            # Wait for crisis detection response
            crisis_response = await websocket.recv()
            crisis_msg = json.loads(crisis_response)
            logger.info(f"Received: {crisis_msg['type']}")

            if crisis_msg["type"] == "crisis_detected":
                logger.info("✅ CRISIS DETECTION SUCCESSFUL!")
                logger.info(f"Crisis level: {crisis_msg['crisis_level']}")
                logger.info(f"Support message: {crisis_msg['support_message']}")
                logger.info(f"Resources provided: {len(crisis_msg['resources'])}")

                for resource in crisis_msg['resources']:
                    logger.info(f"  - {resource['name']}: {resource['contact']}")

                return True
            else:
                logger.error(f"❌ Expected crisis_detected, got: {crisis_msg['type']}")
                logger.error(f"Message content: {crisis_msg}")
                return False

        await websocket.close()

    except Exception as e:
        logger.error(f"❌ Crisis detection test failed: {e}")
        return False

async def main():
    """Main test function."""
    logger.info("=== Crisis Detection Test ===")

    success = await test_crisis_detection()

    if success:
        logger.info("✅ Crisis detection is working correctly!")
    else:
        logger.error("❌ Crisis detection failed!")

    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
