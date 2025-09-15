#!/usr/bin/env python3
"""
Test API Server for Conversational Character Creation

This script creates a minimal FastAPI server to test the conversational
character creation system with WebSocket support.
"""

import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock data and services
class MockSafetyValidator:
    """Mock safety validation service."""

    async def validate_content(self, content_payload, validation_context):
        """Mock content validation - always returns safe."""
        from types import SimpleNamespace

        # Check for crisis keywords for testing
        crisis_keywords = ["hurt myself", "end it all", "suicide", "kill myself"]
        content_lower = content_payload.content_text.lower()

        if any(keyword in content_lower for keyword in crisis_keywords):
            crisis_assessment = SimpleNamespace(
                crisis_level="HIGH",
                crisis_indicators=["suicidal ideation"],
                recommended_actions=["immediate_intervention"],
                confidence_score=0.95
            )

            return SimpleNamespace(
                is_safe=False,
                crisis_assessment=crisis_assessment,
                content_flags=["crisis", "suicidal_ideation"],
                therapeutic_notes=["Immediate professional intervention required"]
            )

        return SimpleNamespace(
            is_safe=True,
            crisis_assessment=None,
            content_flags=[],
            therapeutic_notes=[]
        )

class MockCharacterManager:
    """Mock character avatar manager."""

    def create_character(self, character_data):
        """Mock character creation."""
        from types import SimpleNamespace

        return SimpleNamespace(
            character_id=str(uuid.uuid4()),
            name=character_data.name or "Test Character",
            appearance=SimpleNamespace(
                age_range=character_data.appearance.age_range,
                gender_identity=character_data.appearance.gender_identity,
                physical_description=character_data.appearance.physical_description
            ),
            therapeutic_profile=SimpleNamespace(
                primary_concerns=character_data.therapeutic_profile.primary_concerns,
                preferred_intensity=character_data.therapeutic_profile.preferred_intensity,
                readiness_level=character_data.therapeutic_profile.readiness_level
            )
        )

class MockCharacterRepository:
    """Mock character repository."""

    def __init__(self):
        self.characters = {}

    async def save_character(self, character):
        """Mock save character."""
        self.characters[character.character_id] = character
        return character

    async def get_character(self, character_id):
        """Mock get character."""
        return self.characters.get(character_id)

# Global services
mock_safety_validator = MockSafetyValidator()
mock_character_manager = MockCharacterManager()
mock_character_repository = MockCharacterRepository()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.conversation_connections: dict[str, str] = {}  # conversation_id -> connection_id

    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        # Remove from conversation mapping
        for conv_id, conn_id in list(self.conversation_connections.items()):
            if conn_id == connection_id:
                del self.conversation_connections[conv_id]
        logger.info(f"WebSocket disconnected: {connection_id}")

    async def send_message(self, connection_id: str, message: dict):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            await websocket.send_text(json.dumps(message))

    async def send_to_conversation(self, conversation_id: str, message: dict):
        if conversation_id in self.conversation_connections:
            connection_id = self.conversation_connections[conversation_id]
            await self.send_message(connection_id, message)

manager = ConnectionManager()

# Redis connection (optional - fallback to in-memory)
redis_client = None
conversation_storage = {}

async def get_redis():
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host='localhost',
                port=6379,
                password='TTA_Redis_2024!',
                decode_responses=True
            )
            await redis_client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory storage.")
            redis_client = None
    return redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await get_redis()
    logger.info("API server starting up...")
    yield
    # Shutdown
    if redis_client:
        await redis_client.close()
    logger.info("API server shutting down...")

# FastAPI app
app = FastAPI(
    title="TTA Conversational Character Creation API",
    description="Test API for conversational character creation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conversation stages
CONVERSATION_STAGES = [
    "welcome", "identity", "appearance", "background", "values",
    "relationships", "therapeutic_transition", "concerns", "goals",
    "preferences", "readiness", "summary", "completion"
]

# Stage prompts
STAGE_PROMPTS = {
    "welcome": "Welcome! I'm here to help you create a therapeutic companion that truly understands you. This is a safe space where you can share as much or as little as feels comfortable. What would you like me to call you?",
    "identity": "Thank you for sharing your name. Now, let's explore your identity a bit. How do you see yourself in the world? What age range would you say you're in?",
    "appearance": "Great! Now, let's talk about how you'd like your character to look. How would you describe your physical appearance?",
    "background": "Wonderful! Now I'd love to learn about your story. What experiences have shaped who you are today?",
    "values": "Thank you for sharing your story. What values are most important to you? What principles guide your decisions?",
    "relationships": "Those are beautiful values. How do you connect with others? What are your important relationships like?",
    "therapeutic_transition": "I appreciate you sharing about your relationships. Now, if it feels comfortable, I'd like to gently explore what brings you here today for therapeutic support.",
    "concerns": "What challenges or concerns would you like support with? Remember, you can share as much or as little as feels right.",
    "goals": "Thank you for your openness. What positive changes are you hoping to see? What would success look like for you?",
    "preferences": "Those are meaningful goals. How do you prefer to work on challenges? Do you like a gentle approach or are you ready for more intensive work?",
    "readiness": "Almost there! On a scale of 1-10, how ready do you feel to begin this therapeutic journey?",
    "summary": "Let me summarize what we've discussed and show you a preview of your therapeutic companion.",
    "completion": "Congratulations! Your therapeutic companion is ready. Would you like to create them now?"
}

async def store_conversation(conversation_id: str, conversation_data: dict):
    """Store conversation data."""
    if redis_client:
        try:
            await redis_client.setex(
                f"conversation:{conversation_id}",
                3600,  # 1 hour TTL
                json.dumps(conversation_data, default=str)
            )
        except Exception as e:
            logger.error(f"Redis storage failed: {e}")
            conversation_storage[conversation_id] = conversation_data
    else:
        conversation_storage[conversation_id] = conversation_data

async def get_conversation(conversation_id: str) -> dict | None:
    """Get conversation data."""
    if redis_client:
        try:
            data = await redis_client.get(f"conversation:{conversation_id}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis retrieval failed: {e}")
            return conversation_storage.get(conversation_id)
    else:
        return conversation_storage.get(conversation_id)

def extract_data_from_response(stage: str, response: str, current_data: dict) -> dict:
    """Extract character data from user response."""
    response_lower = response.lower()

    if stage == "welcome":
        # Extract name
        if "call me" in response_lower or "name is" in response_lower or "i'm" in response_lower:
            import re
            name_patterns = [
                r"call me ([a-zA-Z\s\-']+)",
                r"name is ([a-zA-Z\s\-']+)",
                r"i'm ([a-zA-Z\s\-']+)"
            ]
            for pattern in name_patterns:
                match = re.search(pattern, response_lower)
                if match:
                    current_data["name"] = match.group(1).strip().title()
                    break

    elif stage == "identity":
        # Extract age range
        if any(word in response_lower for word in ["child", "kid", "young"]):
            current_data["age_range"] = "child"
        elif any(word in response_lower for word in ["teen", "teenager", "adolescent"]):
            current_data["age_range"] = "teen"
        elif any(word in response_lower for word in ["adult", "grown"]):
            current_data["age_range"] = "adult"
        elif any(word in response_lower for word in ["elder", "senior", "older"]):
            current_data["age_range"] = "elder"

        # Extract gender identity
        if "gender" in response_lower or "identify" in response_lower:
            current_data["gender_identity"] = response.strip()

    elif stage == "appearance":
        current_data["physical_description"] = response.strip()

    elif stage == "background":
        current_data["backstory"] = response.strip()

    elif stage == "values":
        current_data["core_values"] = [v.strip() for v in response.replace(",", ";").split(";")]

    elif stage == "concerns":
        current_data["primary_concerns"] = [c.strip() for c in response.replace(",", ";").split(";")]

    elif stage == "goals":
        current_data["therapeutic_goals"] = [g.strip() for g in response.replace(",", ";").split(";")]

    elif stage == "preferences":
        if any(word in response_lower for word in ["gentle", "slow", "easy"]):
            current_data["preferred_intensity"] = "low"
        elif any(word in response_lower for word in ["intensive", "intense", "challenging"]):
            current_data["preferred_intensity"] = "high"
        else:
            current_data["preferred_intensity"] = "medium"

    elif stage == "readiness":
        import re
        # Extract numeric readiness
        numbers = re.findall(r'\d+', response)
        if numbers:
            readiness = int(numbers[0])
            if readiness <= 10:
                current_data["readiness_level"] = readiness / 10.0
            else:
                current_data["readiness_level"] = readiness / 100.0

    return current_data

# WebSocket endpoint
@app.websocket("/ws/conversational-character-creation")
async def websocket_endpoint(websocket: WebSocket):
    connection_id = str(uuid.uuid4())
    await manager.connect(websocket, connection_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "start_conversation":
                # Start new conversation
                conversation_id = str(uuid.uuid4())
                manager.conversation_connections[conversation_id] = connection_id

                conversation_data = {
                    "conversation_id": conversation_id,
                    "player_id": message.get("player_id", "test_player"),
                    "status": "active",
                    "current_stage": "welcome",
                    "stage_index": 0,
                    "collected_data": {},
                    "message_history": [],
                    "created_at": datetime.utcnow().isoformat(),
                    "crisis_detected": False
                }

                await store_conversation(conversation_id, conversation_data)

                # Send conversation started message
                await manager.send_message(connection_id, {
                    "type": "conversation_started",
                    "conversation_id": conversation_id,
                    "timestamp": datetime.utcnow().isoformat()
                })

                # Send welcome message
                await manager.send_message(connection_id, {
                    "type": "assistant_message",
                    "message_id": str(uuid.uuid4()),
                    "conversation_id": conversation_id,
                    "content": STAGE_PROMPTS["welcome"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "stage": "welcome",
                    "prompt_id": "welcome_intro"
                })

                # Send progress update
                await manager.send_message(connection_id, {
                    "type": "progress_update",
                    "conversation_id": conversation_id,
                    "progress": {
                        "current_stage": "welcome",
                        "progress_percentage": 0,
                        "completed_stages": []
                    },
                    "timestamp": datetime.utcnow().isoformat()
                })

            elif message["type"] == "user_response":
                conversation_id = message["conversation_id"]
                user_content = message["content"]

                # Get conversation data
                conversation_data = await get_conversation(conversation_id)
                if not conversation_data:
                    await manager.send_message(connection_id, {
                        "type": "error",
                        "error_message": "Conversation not found",
                        "error_code": "CONVERSATION_NOT_FOUND"
                    })
                    continue

                # Validate content for safety
                from types import SimpleNamespace
                content_payload = SimpleNamespace(content_text=user_content)
                validation_context = SimpleNamespace(session_id=conversation_id)

                validation_result = await mock_safety_validator.validate_content(
                    content_payload, validation_context
                )

                # Check for crisis
                if not validation_result.is_safe and validation_result.crisis_assessment:
                    conversation_data["crisis_detected"] = True
                    await store_conversation(conversation_id, conversation_data)

                    await manager.send_message(connection_id, {
                        "type": "crisis_detected",
                        "conversation_id": conversation_id,
                        "crisis_level": validation_result.crisis_assessment.crisis_level.lower(),
                        "support_message": "I'm concerned about what you've shared. Your safety is important. Please reach out for immediate support.",
                        "resources": [
                            {"name": "National Suicide Prevention Lifeline", "contact": "988"},
                            {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
                            {"name": "Emergency Services", "contact": "911"}
                        ],
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    continue

                # Extract data from response
                current_stage = conversation_data["current_stage"]
                conversation_data["collected_data"] = extract_data_from_response(
                    current_stage, user_content, conversation_data["collected_data"]
                )

                # Add user message to history
                conversation_data["message_history"].append({
                    "message_id": str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "sender": "user",
                    "content": user_content,
                    "message_type": "response"
                })

                # Move to next stage
                stage_index = conversation_data["stage_index"]
                if stage_index < len(CONVERSATION_STAGES) - 1:
                    stage_index += 1
                    next_stage = CONVERSATION_STAGES[stage_index]
                    conversation_data["current_stage"] = next_stage
                    conversation_data["stage_index"] = stage_index

                    # Calculate progress
                    progress_percentage = int((stage_index / len(CONVERSATION_STAGES)) * 100)
                    completed_stages = CONVERSATION_STAGES[:stage_index]

                    await store_conversation(conversation_id, conversation_data)

                    # Send assistant response
                    if next_stage == "completion":
                        # Generate character preview
                        character_preview = {
                            "character_id": str(uuid.uuid4()),
                            "completeness_score": min(len(conversation_data["collected_data"]) / 10, 1.0),
                            "ready_for_creation": len(conversation_data["collected_data"]) >= 5,
                            "character_preview": conversation_data["collected_data"]
                        }

                        await manager.send_message(connection_id, {
                            "type": "conversation_completed",
                            "conversation_id": conversation_id,
                            "character_preview": character_preview,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    else:
                        await manager.send_message(connection_id, {
                            "type": "assistant_message",
                            "message_id": str(uuid.uuid4()),
                            "conversation_id": conversation_id,
                            "content": STAGE_PROMPTS[next_stage],
                            "timestamp": datetime.utcnow().isoformat(),
                            "stage": next_stage,
                            "prompt_id": f"{next_stage}_prompt"
                        })

                    # Send progress update
                    await manager.send_message(connection_id, {
                        "type": "progress_update",
                        "conversation_id": conversation_id,
                        "progress": {
                            "current_stage": next_stage,
                            "progress_percentage": progress_percentage,
                            "completed_stages": completed_stages
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    })

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(connection_id)

# REST endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/conversations/{conversation_id}/state")
async def get_conversation_state(conversation_id: str):
    conversation_data = await get_conversation(conversation_id)
    if not conversation_data:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation_data

if __name__ == "__main__":
    uvicorn.run(
        "test_conversational_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
