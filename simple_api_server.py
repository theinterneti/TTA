#!/usr/bin/env python3
"""
Simplified TTA API Server for Demo Purposes
This bypasses complex dependencies and provides core functionality for testing.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from neo4j import AsyncGraphDatabase
from pydantic import BaseModel
from redis import asyncio as aioredis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TTA Player Experience API",
    description="Therapeutic Text Adventure API - Simplified Demo Version",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global connections
redis_client = None
neo4j_driver = None


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


# Connection management
async def initialize_connections():
    """Initialize database connections"""
    global redis_client, neo4j_driver

    try:
        # Redis connection
        redis_client = await aioredis.from_url("redis://localhost:6379")
        await redis_client.ping()
        logger.info("✅ Redis connected")

        # Neo4j connection
        neo4j_driver = AsyncGraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("tta_integration", "tta_integration_password_2024"),
        )
        await neo4j_driver.verify_connectivity()
        logger.info("✅ Neo4j connected")

        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    await initialize_connections()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections on shutdown"""
    global redis_client, neo4j_driver

    if redis_client:
        await redis_client.close()
    if neo4j_driver:
        await neo4j_driver.close()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "redis": "connected" if redis_client else "disconnected",
            "neo4j": "connected" if neo4j_driver else "disconnected",
        },
    }
    return status


# Authentication endpoints
@app.post("/auth/login")
async def login(credentials: dict):
    """Simple login endpoint"""
    # Mock authentication
    player_id = str(uuid.uuid4())
    token = f"demo_token_{player_id}"

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

    # Store in Redis for demo
    if redis_client:
        await redis_client.setex(
            f"player:{player_id}",
            3600,
            json.dumps(
                {
                    "player_id": player_id,
                    "name": user_data.get("name", "Anonymous"),
                    "email": user_data.get("email", ""),
                    "created_at": datetime.now().isoformat(),
                }
            ),
        )

    return {
        "player_id": player_id,
        "message": "Registration successful",
        "status": "active",
    }


# Player management
@app.get("/players/{player_id}")
async def get_player(player_id: str):
    """Get player profile"""
    if redis_client:
        player_data = await redis_client.get(f"player:{player_id}")
        if player_data:
            return json.loads(player_data)

    # Mock response
    return {
        "player_id": player_id,
        "name": "Demo Player",
        "status": "active",
        "sessions_count": 5,
        "total_turns": 150,
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

    # Store in Redis
    if redis_client:
        await redis_client.setex(
            f"session:{session_id}",
            7200,
            json.dumps(session_info),  # 2 hours
        )

    return session_info


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    if redis_client:
        session_data = await redis_client.get(f"session:{session_id}")
        if session_data:
            return json.loads(session_data)

    # Mock response
    return {
        "session_id": session_id,
        "status": "active",
        "turn_count": 10,
        "created_at": datetime.now().isoformat(),
    }


# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """Process chat message and return AI response"""
    session_id = message.session_id or str(uuid.uuid4())

    # Mock AI response (in real system, this would call OpenRouter API)
    responses = [
        "I understand you're going through a challenging time. Can you tell me more about what's been on your mind?",
        "That sounds really difficult. How are you feeling about this situation right now?",
        "It's completely normal to feel that way. What do you think might help you feel more grounded?",
        "You've shown a lot of strength in sharing that with me. What would you like to explore next?",
        "I hear that you're working through some complex emotions. What feels most important to address today?",
    ]

    import random

    ai_response = random.choice(responses)

    # Update session turn count
    if redis_client:
        session_key = f"session:{session_id}"
        session_data = await redis_client.get(session_key)
        if session_data:
            session_info = json.loads(session_data)
            session_info["turn_count"] += 1
            session_info["last_activity"] = datetime.now().isoformat()
            await redis_client.setex(session_key, 7200, json.dumps(session_info))

    return ChatResponse(
        response=ai_response,
        session_id=session_id,
        timestamp=datetime.now().isoformat(),
        therapeutic_notes="Patient engaging well, showing openness to therapeutic process",
    )


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

            # Process message (mock AI response)
            responses = [
                "I'm here to listen. What would you like to talk about?",
                "That's a very thoughtful observation. How does that make you feel?",
                "It sounds like you're processing some important feelings. Take your time.",
                "I appreciate you sharing that with me. What comes up for you when you think about it?",
            ]

            import random

            ai_response = random.choice(responses)

            # Send response back to client
            response_data = {
                "type": "ai_response",
                "message": ai_response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
            }

            await websocket.send_text(json.dumps(response_data))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")


# System status endpoints
@app.get("/system/status")
async def system_status():
    """Get system status"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "uptime": time.time(),
        "features": {
            "chat": True,
            "websocket": True,
            "database_persistence": True,
            "ai_models": ["meta-llama/llama-3.2-3b-instruct:free"],
            "therapeutic_frameworks": ["CBT", "DBT", "Mindfulness"],
        },
        "database_status": {
            "redis": "connected" if redis_client else "disconnected",
            "neo4j": "connected" if neo4j_driver else "disconnected",
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
            },
            {
                "id": "qwen/qwen-2.5-7b-instruct:free",
                "name": "Qwen 2.5 7B Instruct",
                "provider": "OpenRouter",
                "cost": "$0.00",
                "therapeutic_optimized": True,
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
