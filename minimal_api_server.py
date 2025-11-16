#!/usr/bin/env python3
"""
Minimal TTA API Server for Demo Purposes
This provides core functionality without complex dependencies.
"""

import json
import logging
import random
import time
import uuid
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TTA Player Experience API",
    description="Therapeutic Text Adventure API - Minimal Demo Version",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
sessions = {}
players = {}
chat_history = {}
characters = {}


# Data models
class ChatMessage(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    therapeutic_notes: str | None = None


class PlayerProfile(BaseModel):
    player_id: str
    name: str
    preferences: dict[str, Any] = {}


class SessionInfo(BaseModel):
    session_id: str
    player_id: str
    status: str
    created_at: str
    turn_count: int = 0


class CharacterCreate(BaseModel):
    name: str
    description: str = ""
    personality_traits: list[str] = []
    stats: dict[str, int] = {}
    location_name: str | None = None


class CharacterResponse(BaseModel):
    id: str
    name: str
    description: str
    personality_traits: list[str] = []
    stats: dict[str, int] = {}
    location: str | None = None
    created_at: str


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {"api": "running", "database": "mock_mode"},
    }


# Authentication endpoints
@app.post("/auth/login")
async def login(credentials: dict):
    """Simple login endpoint"""
    username = credentials.get("username")
    password = credentials.get("password")

    if username == "demo_user" and password == "demo_password":
        player_id = str(uuid.uuid4())
        token = f"demo_token_{player_id}"

        # Store player info
        players[player_id] = {
            "player_id": player_id,
            "name": username,
            "email": "demo@example.com",
            "created_at": datetime.now().isoformat(),
            "status": "active",
        }

        return {
            "token": token,  # Frontend expects 'token' not 'access_token'
            "user": {"player_id": player_id, "username": username},
        }

    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/api/v1/auth/login")
async def login_v1(credentials: dict):
    """API v1 login endpoint for frontend compatibility"""
    player_id = str(uuid.uuid4())
    token = f"demo_token_{player_id}"

    # Store player info
    players[player_id] = {
        "player_id": player_id,
        "name": credentials.get("username", "Demo Player"),
        "email": credentials.get("email", "demo@example.com"),
        "created_at": datetime.now().isoformat(),
        "status": "active",
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "player_id": player_id,
        "expires_in": 3600,
    }


@app.post("/auth/register")
async def register(user_data: dict):
    """Simple registration endpoint"""
    player_id = str(uuid.uuid4())

    players[player_id] = {
        "player_id": player_id,
        "name": user_data.get("name", "Anonymous"),
        "email": user_data.get("email", ""),
        "created_at": datetime.now().isoformat(),
        "status": "active",
    }

    return {
        "player_id": player_id,
        "message": "Registration successful",
        "status": "active",
    }


# Player management
@app.get("/players/{player_id}")
async def get_player(player_id: str):
    """Get player profile"""
    if player_id in players:
        return players[player_id]

    # Mock response
    return {
        "player_id": player_id,
        "name": "Demo Player",
        "status": "active",
        "sessions_count": len(
            [s for s in sessions.values() if s.get("player_id") == player_id]
        ),
        "total_turns": sum(
            s.get("turn_count", 0)
            for s in sessions.values()
            if s.get("player_id") == player_id
        ),
    }


# Session management
@app.post("/sessions")
async def create_session(session_data: dict):
    """Create a new therapeutic session"""
    session_id = str(uuid.uuid4())
    player_id = session_data.get("player_id", str(uuid.uuid4()))

    session_info = {
        "session_id": session_id,
        "player_id": player_id,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "turn_count": 0,
        "scenario": session_data.get("scenario", "general_therapy"),
        "ai_model": session_data.get(
            "ai_model", "meta-llama/llama-3.2-3b-instruct:free"
        ),
    }

    sessions[session_id] = session_info
    chat_history[session_id] = []

    return session_info


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    if session_id in sessions:
        return sessions[session_id]

    # Mock response
    return {
        "session_id": session_id,
        "status": "active",
        "turn_count": 0,
        "created_at": datetime.now().isoformat(),
    }


# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """Process chat message and return AI response"""
    session_id = message.session_id or str(uuid.uuid4())

    # Therapeutic AI responses
    therapeutic_responses = [
        "I understand you're going through a challenging time. Can you tell me more about what's been on your mind?",
        "That sounds really difficult. How are you feeling about this situation right now?",
        "It's completely normal to feel that way. What do you think might help you feel more grounded?",
        "You've shown a lot of strength in sharing that with me. What would you like to explore next?",
        "I hear that you're working through some complex emotions. What feels most important to address today?",
        "Thank you for trusting me with that. How long have you been feeling this way?",
        "It sounds like you're being really thoughtful about this. What comes up for you when you sit with these feelings?",
        "I can sense the courage it took to share that. What would support look like for you right now?",
        "That's a really important insight. How does recognizing that feel for you?",
        "I'm here with you in this moment. What would you like to focus on as we continue?",
    ]

    ai_response = random.choice(therapeutic_responses)

    # Update session
    if session_id not in sessions:
        sessions[session_id] = {
            "session_id": session_id,
            "player_id": "demo_player",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "turn_count": 0,
        }
        chat_history[session_id] = []

    sessions[session_id]["turn_count"] += 1
    sessions[session_id]["last_activity"] = datetime.now().isoformat()

    # Store chat history
    chat_history[session_id].append(
        {
            "user_message": message.message,
            "ai_response": ai_response,
            "timestamp": datetime.now().isoformat(),
        }
    )

    return ChatResponse(
        response=ai_response,
        session_id=session_id,
        timestamp=datetime.now().isoformat(),
        therapeutic_notes="Patient engaging well, showing openness to therapeutic process",
    )


# Get chat history
@app.get("/sessions/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    if session_id in chat_history:
        return {
            "session_id": session_id,
            "history": chat_history[session_id],
            "total_messages": len(chat_history[session_id]),
        }

    return {"session_id": session_id, "history": [], "total_messages": 0}


# Character management endpoints
@app.post("/characters", response_model=CharacterResponse)
async def create_character(character_data: CharacterCreate):
    """Create a new character"""
    character_id = str(uuid.uuid4())

    character = {
        "id": character_id,
        "name": character_data.name,
        "description": character_data.description,
        "personality_traits": character_data.personality_traits,
        "stats": character_data.stats,
        "location": character_data.location_name,
        "created_at": datetime.now().isoformat(),
    }

    characters[character_id] = character

    return CharacterResponse(**character)


@app.get("/characters")
async def list_characters():
    """List all characters"""
    return {"characters": list(characters.values()), "total_count": len(characters)}


@app.get("/characters/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: str):
    """Get a specific character"""
    if character_id in characters:
        return CharacterResponse(**characters[character_id])

    raise HTTPException(status_code=404, detail="Character not found")


@app.put("/characters/{character_id}", response_model=CharacterResponse)
async def update_character(character_id: str, character_data: CharacterCreate):
    """Update a character"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")

    characters[character_id].update(
        {
            "name": character_data.name,
            "description": character_data.description,
            "personality_traits": character_data.personality_traits,
            "stats": character_data.stats,
            "location": character_data.location_name,
        }
    )

    return CharacterResponse(**characters[character_id])


@app.delete("/characters/{character_id}")
async def delete_character(character_id: str):
    """Delete a character"""
    if character_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")

    deleted_character = characters.pop(character_id)
    return {
        "message": f"Character '{deleted_character['name']}' deleted successfully",
        "character_id": character_id,
    }


# WebSocket for real-time chat
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    logger.info(f"WebSocket connected for session: {session_id}")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Process message
            therapeutic_responses = [
                "I'm here to listen. What would you like to talk about?",
                "That's a very thoughtful observation. How does that make you feel?",
                "It sounds like you're processing some important feelings. Take your time.",
                "I appreciate you sharing that with me. What comes up for you when you think about it?",
                "You're doing important work by exploring these thoughts. What feels most significant to you right now?",
            ]

            ai_response = random.choice(therapeutic_responses)

            # Update session
            if session_id not in sessions:
                sessions[session_id] = {
                    "session_id": session_id,
                    "player_id": "demo_player",
                    "status": "active",
                    "created_at": datetime.now().isoformat(),
                    "turn_count": 0,
                }
                chat_history[session_id] = []

            sessions[session_id]["turn_count"] += 1

            # Store in history
            chat_history[session_id].append(
                {
                    "user_message": message_data.get("message", ""),
                    "ai_response": ai_response,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Send response back to client
            response_data = {
                "type": "ai_response",
                "message": ai_response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "turn_count": sessions[session_id]["turn_count"],
            }

            await websocket.send_text(json.dumps(response_data))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")


# WebSocket for therapeutic chat (frontend-compatible endpoint)
@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """WebSocket endpoint for therapeutic chat - frontend compatible"""
    # Extract token from query params for authentication
    token = websocket.query_params.get("token")
    session_id = websocket.query_params.get("session_id", str(uuid.uuid4()))

    if not token or token != "demo_token_09be0dde-2a3f-42fc-aa73-153654":
        await websocket.close(code=1008, reason="Authentication failed")
        return

    await websocket.accept()
    logger.info(f"WebSocket chat connected for session: {session_id}")

    # Send welcome message
    welcome_message = {
        "type": "system",
        "content": {"text": "Connected to therapeutic chat. You're safe here."},
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
    }
    await websocket.send_text(json.dumps(welcome_message))

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle different message types
            msg_type = message_data.get("type", "user_message")
            content = message_data.get("content", {})

            if msg_type == "user_message":
                user_text = content.get("text", "")
                logger.info(f"Received user message: {user_text[:50]}...")

                # Store message in session
                if session_id not in sessions:
                    sessions[session_id] = {
                        "messages": [],
                        "turn_count": 0,
                        "created_at": datetime.now().isoformat(),
                    }

                # Add user message
                user_message = {
                    "role": "user",
                    "content": user_text,
                    "timestamp": datetime.now().isoformat(),
                }
                sessions[session_id]["messages"].append(user_message)
                sessions[session_id]["turn_count"] += 1

                # Generate contextual therapeutic response
                therapeutic_responses = [
                    "I hear that you're feeling anxious about exploring. That's completely natural. Let's imagine we're standing at the edge of a peaceful forest. What do you notice first - the sounds, the smells, or the way the light filters through the trees?",
                    "The sound of birds singing can be very grounding. Let's focus on that together. Can you imagine hearing different types of birds? Maybe a gentle robin, or the distant call of a dove? What feelings come up when you focus on these sounds?",
                    "A stream is a wonderful place for breathing exercises. Picture yourself sitting on a smooth rock beside flowing water. Let's try breathing in for 4 counts as the water flows toward you, holding for 4, then breathing out for 6 as it flows away. How does that feel?",
                    "I'm glad you're feeling more relaxed. As we go deeper into this forest, imagine discovering a hidden path lined with soft moss. Each step you take represents letting go of a worry. What would you like to leave behind on this path?",
                    "What a beautiful discovery! Wildflowers often represent growth and resilience. Each flower in this clearing has grown through challenges, just like you. Which flower draws your attention, and what might it teach you about handling your anxiety?",
                    "This peaceful place you've found can become an anchor for you. When you feel stressed in daily life, you can return here in your mind. What specific details about this clearing would you want to remember - the colors, the feeling of the breeze, or the sense of safety?",
                    "Mindfulness in this beautiful setting is powerful. Let's practice the 5-4-3-2-1 technique here: Can you imagine 5 things you see in this clearing, 4 things you might touch, 3 sounds you hear, 2 scents you notice, and 1 taste - perhaps the fresh air?",
                    "This forest has many therapeutic gifts to offer. We could practice progressive muscle relaxation by imagining the trees teaching us to be both strong and flexible, or we could do a walking meditation along a forest path. What calls to you?",
                    "You've learned that nature can be a powerful ally in managing anxiety. You've discovered that you can find peace even when starting from a place of worry. You've practiced breathing, mindfulness, and connecting with your inner wisdom. What feels most important to remember?",
                    "You're so welcome. The calm you've cultivated here lives within you always. When you need it, you can close your eyes and return to this peaceful clearing. Remember: you have the strength to find peace even in challenging moments. What's one word that captures how you feel right now?",
                ]

                # Select response based on turn count for more natural flow
                turn_index = min(
                    sessions[session_id]["turn_count"] - 1,
                    len(therapeutic_responses) - 1,
                )
                ai_response = therapeutic_responses[turn_index]

                ai_message = {
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.now().isoformat(),
                }
                sessions[session_id]["messages"].append(ai_message)

                # Send response back to client
                response_data = {
                    "type": "assistant_message",
                    "content": {"text": ai_response},
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                    "metadata": {
                        "turn_count": sessions[session_id]["turn_count"],
                        "therapeutic_context": "forest_exploration",
                    },
                }

                await websocket.send_text(json.dumps(response_data))
                logger.info(
                    f"Sent therapeutic response for turn {sessions[session_id]['turn_count']}"
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket chat disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason="Internal server error")


# Simple test WebSocket endpoint
@app.websocket("/ws/test")
async def websocket_test(websocket: WebSocket):
    """Simple WebSocket test endpoint"""
    await websocket.accept()
    await websocket.send_text("Hello WebSocket!")
    await websocket.close()


# System status endpoints
@app.get("/system/status")
async def system_status():
    """Get system status"""
    return {
        "status": "operational",
        "version": "1.0.0-demo",
        "uptime": time.time(),
        "active_sessions": len(sessions),
        "total_players": len(players),
        "features": {
            "chat": True,
            "websocket": True,
            "database_persistence": False,  # Mock mode
            "ai_models": ["meta-llama/llama-3.2-3b-instruct:free"],
            "therapeutic_frameworks": ["CBT", "DBT", "Mindfulness"],
        },
        "database_status": {
            "mode": "in_memory_demo",
            "redis": "simulated",
            "neo4j": "simulated",
        },
    }


@app.get("/models")
async def get_available_models():
    """Get available AI models"""
    return {
        "models": [
            {
                "id": "meta-llama/llama-3.2-3b-instruct:free",
                "name": "Llama 3.2 3B Instruct",
                "provider": "OpenRouter",
                "cost": "$0.00",
                "therapeutic_optimized": True,
                "status": "available",
            },
            {
                "id": "qwen/qwen-2.5-7b-instruct:free",
                "name": "Qwen 2.5 7B Instruct",
                "provider": "OpenRouter",
                "cost": "$0.00",
                "therapeutic_optimized": True,
                "status": "available",
            },
        ]
    }


# Statistics endpoint
@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    total_turns = sum(s.get("turn_count", 0) for s in sessions.values())

    return {
        "total_sessions": len(sessions),
        "active_sessions": len(
            [s for s in sessions.values() if s.get("status") == "active"]
        ),
        "total_players": len(players),
        "total_turns": total_turns,
        "average_turns_per_session": total_turns / len(sessions) if sessions else 0,
        "uptime_hours": time.time() / 3600,
    }


@app.get("/api/v1/nexus/state")
async def get_nexus_state():
    """Get nexus state for frontend compatibility"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "nexus": {
            "active_connections": len(sessions),
            "total_characters": len(characters),
            "system_load": "low",
        },
    }


# Frontend-compatible character endpoints
@app.post("/players/{player_id}/characters")
async def create_character_for_player(player_id: str, character_data: dict):
    """Create a character for a specific player (frontend compatible)"""
    character_id = str(uuid.uuid4())

    # Extract data from nested frontend format
    name = character_data.get("name", "Unnamed Character")
    appearance = character_data.get("appearance", {})
    background = character_data.get("background", {})
    therapeutic_profile = character_data.get("therapeutic_profile", {})

    character = {
        "character_id": character_id,
        "player_id": player_id,
        "name": name,
        "appearance": {
            "description": appearance.get("description", ""),
            "age_range": appearance.get("age_range", "adult"),
            "gender_identity": appearance.get("gender_identity", "non-binary"),
            "clothing_style": appearance.get("clothing_style", "casual"),
            "avatar_url": appearance.get("avatar_url"),
        },
        "background": {
            "story": background.get("story", ""),
            "personality_traits": background.get("personality_traits", []),
            "goals": background.get("goals", []),
        },
        "therapeutic_profile": {
            "comfort_level": therapeutic_profile.get("comfort_level", 5),
            "preferred_intensity": therapeutic_profile.get(
                "preferred_intensity", "MEDIUM"
            ),
            "therapeutic_goals": therapeutic_profile.get("therapeutic_goals", []),
        },
        "created_at": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat(),
        "active_worlds": [],
    }

    characters[character_id] = character

    return character


@app.get("/players/{player_id}/characters")
async def get_characters_for_player(player_id: str):
    """Get all characters for a specific player"""
    player_characters = [
        char for char in characters.values() if char.get("player_id") == player_id
    ]
    return player_characters


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
