# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Minimal FastAPI Server for TTA Core Gameplay Loop Integration Testing

This script creates a minimal FastAPI server that includes only the essential
components needed to test the gameplay loop integration, avoiding complex
dependencies that might cause startup issues.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
import uuid
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TTA Core Gameplay Loop API",
    description="Minimal API for testing TTA Core Gameplay Loop integration",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# In-memory storage for testing
sessions_store: dict[str, dict[str, Any]] = {}
users_store: dict[str, dict[str, Any]] = {
    "demo_user": {
        "username": "demo_user",
        "password": "demo_password",  # In real app, this would be hashed
        "email": "demo@example.com",
    },
    "api_test_user": {
        "username": "api_test_user",
        "password": "TestPassword123!",
        "email": "apitest@example.com",
    },
}


# Pydantic models
class CreateSessionRequest(BaseModel):
    therapeutic_context: dict[str, Any] | None = None


class CreateSessionResponse(BaseModel):
    session_id: str
    status: str
    message: str


class ProcessChoiceRequest(BaseModel):
    choice_id: str


class ProcessChoiceResponse(BaseModel):
    success: bool
    narrative_update: dict[str, Any] | None = None
    message: str


class SessionStatusResponse(BaseModel):
    session_id: str
    session_status: dict[str, Any]
    is_active: bool


class ProgressResponse(BaseModel):
    session_id: str
    progress: dict[str, Any]
    therapeutic_metrics: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: str
    message: str
    components: dict[str, str]
    timestamp: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    message: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class RegisterResponse(BaseModel):
    message: str
    user_id: str


# Authentication functions
def verify_credentials(username: str, password: str) -> bool:
    """Verify user credentials."""
    user = users_store.get(username)
    return user is not None and user["password"] == password


def create_access_token(username: str) -> str:
    """Create a simple access token (in real app, use JWT)."""
    return f"token_{username}_{uuid.uuid4().hex[:8]}"


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify access token and return username."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    token = credentials.credentials
    if not token.startswith("token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format"
        )

    # Extract username from token (simplified)
    try:
        username = token.split("_")[1]
        if username not in users_store:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        return username
    except (IndexError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


# Authentication endpoints
@app.post("/api/v1/auth/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """Register a new user."""
    if request.username in users_store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    user_id = str(uuid.uuid4())
    users_store[request.username] = {
        "user_id": user_id,
        "username": request.username,
        "email": request.email,
        "password": request.password,  # In real app, hash this
    }

    return RegisterResponse(message="User registered successfully", user_id=user_id)


@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login and get access token."""
    if not verify_credentials(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = create_access_token(request.username)

    return LoginResponse(
        access_token=access_token, token_type="bearer", message="Login successful"
    )


# Gameplay endpoints
@app.get("/api/v1/gameplay/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from datetime import datetime

    return HealthResponse(
        status="healthy",
        message="TTA Core Gameplay Loop API is operational",
        components={
            "api_server": "running",
            "gameplay_integration": "active",
            "session_management": "ready",
            "authentication": "enabled",
        },
        timestamp=datetime.utcnow().isoformat(),
    )


@app.post("/api/v1/gameplay/sessions", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest, username: str = Depends(verify_token)
):
    """Create a new gameplay session."""
    session_id = str(uuid.uuid4())

    session_data = {
        "session_id": session_id,
        "username": username,
        "therapeutic_context": request.therapeutic_context or {},
        "status": "active",
        "created_at": "2025-09-23T11:00:00Z",
        "last_activity": "2025-09-23T11:00:00Z",
        "narrative_state": {
            "current_scene": "introduction",
            "character_state": {},
            "world_state": {},
        },
        "choices_made": [],
        "therapeutic_progress": {
            "goals_addressed": [],
            "insights_gained": [],
            "skills_practiced": [],
        },
    }

    sessions_store[session_id] = session_data

    logger.info(f"Created session {session_id} for user {username}")

    return CreateSessionResponse(
        session_id=session_id,
        status="created",
        message="Gameplay session created successfully",
    )


@app.get("/api/v1/gameplay/sessions/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(session_id: str, username: str = Depends(verify_token)):
    """Get session status."""
    if session_id not in sessions_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    session = sessions_store[session_id]

    # Check ownership
    if session["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return SessionStatusResponse(
        session_id=session_id,
        session_status={
            "status": session["status"],
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "choices_count": len(session["choices_made"]),
        },
        is_active=session["status"] == "active",
    )


@app.post(
    "/api/v1/gameplay/sessions/{session_id}/choices",
    response_model=ProcessChoiceResponse,
)
async def process_choice(
    session_id: str,
    request: ProcessChoiceRequest,
    username: str = Depends(verify_token),
):
    """Process a player choice."""
    if session_id not in sessions_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    session = sessions_store[session_id]

    # Check ownership
    if session["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Process the choice (simplified)
    choice_data = {
        "choice_id": request.choice_id,
        "timestamp": "2025-09-23T11:00:00Z",
        "narrative_impact": "positive",
    }

    session["choices_made"].append(choice_data)
    session["last_activity"] = "2025-09-23T11:00:00Z"

    # Update narrative state
    session["narrative_state"]["current_scene"] = f"scene_after_{request.choice_id}"

    logger.info(f"Processed choice {request.choice_id} for session {session_id}")

    return ProcessChoiceResponse(
        success=True,
        narrative_update={
            "new_scene": session["narrative_state"]["current_scene"],
            "description": f"You chose {request.choice_id}. The story continues...",
            "available_choices": [
                {"id": "choice_1", "text": "Continue exploring"},
                {"id": "choice_2", "text": "Reflect on your decision"},
            ],
        },
        message="Choice processed successfully",
    )


@app.get(
    "/api/v1/gameplay/sessions/{session_id}/progress", response_model=ProgressResponse
)
async def get_progress(session_id: str, username: str = Depends(verify_token)):
    """Get session progress."""
    if session_id not in sessions_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    session = sessions_store[session_id]

    # Check ownership
    if session["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return ProgressResponse(
        session_id=session_id,
        progress={
            "choices_made": len(session["choices_made"]),
            "current_scene": session["narrative_state"]["current_scene"],
            "session_duration": "15 minutes",
            "completion_percentage": min(len(session["choices_made"]) * 10, 100),
        },
        therapeutic_metrics={
            "goals_addressed": len(session["therapeutic_progress"]["goals_addressed"]),
            "insights_gained": len(session["therapeutic_progress"]["insights_gained"]),
            "engagement_score": 8.5,
        },
    )


@app.delete("/api/v1/gameplay/sessions/{session_id}")
async def end_session(session_id: str, username: str = Depends(verify_token)):
    """End a gameplay session."""
    if session_id not in sessions_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    session = sessions_store[session_id]

    # Check ownership
    if session["username"] != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    session["status"] = "ended"
    logger.info(f"Ended session {session_id} for user {username}")

    return {"message": "Session ended successfully"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TTA Core Gameplay Loop API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/api/v1/gameplay/health",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting TTA Core Gameplay Loop API server...")
    logger.info("Available endpoints:")
    logger.info("  - Health: http://localhost:8000/api/v1/gameplay/health")
    logger.info("  - Docs: http://localhost:8000/docs")
    logger.info("  - Auth: http://localhost:8000/api/v1/auth/")
    logger.info("  - Gameplay: http://localhost:8000/api/v1/gameplay/")

    uvicorn.run(
        "scripts.minimal_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
