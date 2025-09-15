#!/usr/bin/env python3
"""
WebSocket Test Client for Conversational Character Creation

This script tests the complete conversational character creation flow
through WebSocket communication.
"""

import asyncio
import json
import logging
from datetime import datetime

import websockets

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConversationalTestClient:
    """Test client for conversational character creation."""

    def __init__(self, websocket_url: str = "ws://localhost:8000/ws/conversational-character-creation"):
        self.websocket_url = websocket_url
        self.websocket = None
        self.conversation_id = None
        self.current_stage = None
        self.progress = {}
        self.character_preview = None
        self.messages_received = []

    async def connect(self):
        """Connect to WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            logger.info(f"Connected to {self.websocket_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    async def disconnect(self):
        """Disconnect from WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from WebSocket")

    async def send_message(self, message: dict):
        """Send message to server."""
        if not self.websocket:
            logger.error("Not connected to WebSocket")
            return False

        try:
            await self.websocket.send(json.dumps(message))
            logger.info(f"Sent: {message['type']}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def receive_message(self) -> dict | None:
        """Receive message from server."""
        if not self.websocket:
            return None

        try:
            message_text = await self.websocket.recv()
            message = json.loads(message_text)
            self.messages_received.append(message)
            logger.info(f"Received: {message['type']}")
            return message
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            return None

    async def start_conversation(self, player_id: str = "test_player_123"):
        """Start a new conversation."""
        message = {
            "type": "start_conversation",
            "player_id": player_id,
            "metadata": {
                "source": "test_client",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        success = await self.send_message(message)
        if success:
            # Wait for conversation_started response
            response = await self.receive_message()
            if response and response["type"] == "conversation_started":
                self.conversation_id = response["conversation_id"]
                logger.info(f"Conversation started: {self.conversation_id}")

                # Wait for welcome message
                welcome_msg = await self.receive_message()
                if welcome_msg and welcome_msg["type"] == "assistant_message":
                    self.current_stage = welcome_msg["stage"]
                    logger.info(f"Welcome message: {welcome_msg['content'][:100]}...")

                # Wait for progress update
                progress_msg = await self.receive_message()
                if progress_msg and progress_msg["type"] == "progress_update":
                    self.progress = progress_msg["progress"]
                    logger.info(f"Progress: {self.progress['progress_percentage']}%")

                return True

        return False

    async def send_user_response(self, content: str):
        """Send user response."""
        if not self.conversation_id:
            logger.error("No active conversation")
            return False

        message = {
            "type": "user_response",
            "conversation_id": self.conversation_id,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }

        success = await self.send_message(message)
        if success:
            # Wait for assistant response or completion
            response = await self.receive_message()
            if response:
                if response["type"] == "assistant_message":
                    self.current_stage = response["stage"]
                    logger.info(f"Assistant: {response['content'][:100]}...")
                elif response["type"] == "conversation_completed":
                    self.character_preview = response["character_preview"]
                    logger.info("Conversation completed!")
                    return "completed"
                elif response["type"] == "crisis_detected":
                    logger.warning(f"Crisis detected: {response['crisis_level']}")
                    return "crisis"

                # Wait for progress update
                progress_msg = await self.receive_message()
                if progress_msg and progress_msg["type"] == "progress_update":
                    self.progress = progress_msg["progress"]
                    logger.info(f"Progress: {self.progress['progress_percentage']}% - Stage: {self.progress['current_stage']}")

        return "continue"

    async def run_complete_conversation_flow(self):
        """Run a complete conversation flow for testing."""
        logger.info("=== Starting Complete Conversation Flow Test ===")

        # Test responses for each stage
        test_responses = {
            "welcome": "Hi, you can call me Sarah. I'm a bit nervous but excited to start this journey.",
            "identity": "I'm an adult woman, 28 years old. I identify as female and consider myself creative and empathetic.",
            "appearance": "I have shoulder-length brown hair, green eyes, and I'm about average height. I usually dress casually but like to add colorful accessories.",
            "background": "I grew up in a small town with loving parents. I studied art in college and now work as a graphic designer. I've always been sensitive and caring toward others.",
            "values": "Honesty, compassion, and creativity are most important to me. I believe in treating others with kindness and standing up for what's right.",
            "relationships": "I have a close relationship with my family and a few deep friendships. I tend to be the person people come to for support, but sometimes I struggle to ask for help myself.",
            "therapeutic_transition": "I'm here because I've been feeling overwhelmed lately. I give so much to others that I sometimes forget to take care of myself.",
            "concerns": "I struggle with anxiety, especially social anxiety. I also have trouble setting boundaries and often feel guilty when I try to prioritize my own needs.",
            "goals": "I want to learn how to manage my anxiety better and develop healthier boundaries. I'd like to feel more confident in social situations and be kinder to myself.",
            "preferences": "I prefer a gentle but steady approach. I'm ready to do the work, but I need to feel safe and supported. I like having concrete strategies I can practice.",
            "readiness": "I'd say I'm about 7 out of 10 ready. I'm motivated to change but also a bit scared of the process.",
            "summary": "That sounds like a good summary of who I am and what I'm looking for. I'm ready to create my therapeutic companion.",
            "completion": "Yes, I'd like to create this character. She sounds like someone who would really understand and support me."
        }

        # Start conversation
        if not await self.start_conversation():
            logger.error("Failed to start conversation")
            return False

        # Go through each stage
        for stage, response in test_responses.items():
            if self.current_stage == stage:
                logger.info(f"\n--- Stage: {stage.upper()} ---")
                logger.info(f"User response: {response}")

                result = await self.send_user_response(response)

                if result == "completed":
                    logger.info("Conversation completed successfully!")
                    break
                elif result == "crisis":
                    logger.warning("Crisis detected - stopping conversation")
                    break

                # Small delay between responses
                await asyncio.sleep(1)

        # Print final results
        logger.info("\n=== Conversation Results ===")
        logger.info(f"Final progress: {self.progress}")
        if self.character_preview:
            logger.info(f"Character preview: {json.dumps(self.character_preview, indent=2)}")

        return True

    async def test_crisis_detection(self):
        """Test crisis detection functionality."""
        logger.info("\n=== Testing Crisis Detection ===")

        # Start new conversation
        if not await self.start_conversation("crisis_test_player"):
            return False

        # Send crisis-indicating response
        crisis_response = "I've been thinking about ending it all. I don't see any point in continuing."
        logger.info(f"Sending crisis response: {crisis_response}")

        result = await self.send_user_response(crisis_response)

        if result == "crisis":
            logger.info("✅ Crisis detection working correctly!")
            return True
        else:
            logger.error("❌ Crisis detection failed!")
            return False

    async def test_conversation_persistence(self):
        """Test conversation state persistence."""
        logger.info("\n=== Testing Conversation Persistence ===")

        # Start conversation and send a few responses
        if not await self.start_conversation("persistence_test_player"):
            return False

        await self.send_user_response("My name is Alex")
        await self.send_user_response("I'm an adult")

        # Store conversation ID for later
        test_conversation_id = self.conversation_id

        # Disconnect and reconnect
        await self.disconnect()
        await asyncio.sleep(2)

        if not await self.connect():
            return False

        # Try to get conversation state via REST API
        import aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"http://localhost:8000/api/conversations/{test_conversation_id}/state") as response:
                    if response.status == 200:
                        conversation_data = await response.json()
                        logger.info("✅ Conversation persistence working!")
                        logger.info(f"Recovered conversation: {conversation_data['conversation_id']}")
                        return True
                    else:
                        logger.error(f"❌ Failed to retrieve conversation: {response.status}")
                        return False
            except Exception as e:
                logger.error(f"❌ Persistence test failed: {e}")
                return False

async def main():
    """Main test function."""
    client = ConversationalTestClient()

    # Connect to server
    if not await client.connect():
        logger.error("Failed to connect to server")
        return

    try:
        # Test 1: Complete conversation flow
        success1 = await client.run_complete_conversation_flow()

        # Test 2: Crisis detection
        success2 = await client.test_crisis_detection()

        # Test 3: Conversation persistence
        success3 = await client.test_conversation_persistence()

        # Summary
        logger.info("\n=== TEST SUMMARY ===")
        logger.info(f"Complete conversation flow: {'✅ PASS' if success1 else '❌ FAIL'}")
        logger.info(f"Crisis detection: {'✅ PASS' if success2 else '❌ FAIL'}")
        logger.info(f"Conversation persistence: {'✅ PASS' if success3 else '❌ FAIL'}")

        total_tests = 3
        passed_tests = sum([success1, success2, success3])
        logger.info(f"Overall: {passed_tests}/{total_tests} tests passed")

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
