"""

# Logseq: [[TTA.dev/Player_experience/Api/Routers/Gameplay]]
Gameplay Loop API Router

This module provides REST API endpoints for the Core Gameplay Loop system,
including session management, choice processing, and progress tracking.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from ...services.gameplay_service import GameplayService
from ...services.message_service import MessageService
from ..auth import security, verify_token

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class CreateSessionRequest(BaseModel):
    """Request model for creating a new gameplay session."""

    therapeutic_context: dict[str, Any] | None = Field(
        None, description="Therapeutic context and goals for the session"
    )


class CreateSessionResponse(BaseModel):
    """Response model for session creation."""

    success: bool
    session_id: str | None = None
    user_id: str | None = None
    session_status: dict[str, Any] | None = None
    created_at: str | None = None
    error: str | None = None
    code: str | None = None


class ProcessChoiceRequest(BaseModel):
    """Request model for processing a user choice."""

    choice_id: str = Field(..., description="ID of the choice made by the user")


class ProcessChoiceResponse(BaseModel):
    """Response model for choice processing."""

    success: bool
    session_id: str | None = None
    choice_result: dict[str, Any] | None = None
    processed_at: str | None = None
    safety_warning: str | None = None
    error: str | None = None
    code: str | None = None


class SessionStatusResponse(BaseModel):
    """Response model for session status."""

    success: bool
    session_status: dict[str, Any] | None = None
    retrieved_at: str | None = None
    error: str | None = None
    code: str | None = None


class EndSessionResponse(BaseModel):
    """Response model for ending a session."""

    success: bool
    session_id: str | None = None
    ended_at: str | None = None
    error: str | None = None
    code: str | None = None


class UserSessionsResponse(BaseModel):
    """Response model for user sessions."""

    success: bool
    user_id: str | None = None
    session_metrics: dict[str, Any] | None = None
    retrieved_at: str | None = None
    error: str | None = None
    code: str | None = None


class SendMessageRequest(BaseModel):
    """Request model for sending a player message in a gameplay session."""

    session_id: str = Field(..., description="Active session ID")
    message: str = Field(
        ..., min_length=1, max_length=2000, description="Player's message"
    )
    character_name: str | None = Field(
        None, description="Character name for narrative context"
    )
    world_name: str | None = Field(None, description="World name for narrative context")


class SendMessageResponse(BaseModel):
    """Response model for a gameplay message."""

    success: bool
    message_id: str | None = None
    session_id: str | None = None
    response: str | None = None
    timestamp: str | None = None
    error: str | None = None
    code: str | None = None


# Dependency to get gameplay service
async def get_gameplay_service() -> GameplayService:
    """Get the gameplay service instance."""
    # This would be dependency injected in a real implementation
    # For now, we'll create a singleton instance
    if not hasattr(get_gameplay_service, "_instance"):
        get_gameplay_service._instance = GameplayService()
    return get_gameplay_service._instance


async def get_message_service() -> MessageService:
    """Get the message service singleton, sharing the session store with the sessions router."""
    if not hasattr(get_message_service, "_instance"):
        from ..routers.sessions import get_session_store  # noqa: PLC0415

        get_message_service._instance = MessageService(session_store=get_session_store())
    return get_message_service._instance


@router.post("/message", response_model=SendMessageResponse)
async def send_gameplay_message(
    request: SendMessageRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    message_service: MessageService = Depends(get_message_service),
) -> SendMessageResponse:
    """Send a player message in an active session and receive an AI narrative response.

    Calls the LLM (OpenRouter or Ollama) with the full conversation history
    to generate a contextual therapeutic narrative response.
    Falls back to a static supportive message if the LLM is unavailable.
    """
    try:
        token_data = verify_token(credentials.credentials)
        player_id = token_data.player_id or "anonymous"

        result = await message_service.send_message(
            session_id=request.session_id,
            player_id=player_id,
            message=request.message,
            character_name=request.character_name,
            world_name=request.world_name,
        )
        return SendMessageResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to process gameplay message: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    gameplay_service: GameplayService = Depends(get_gameplay_service),
):
    """
    Create a new gameplay session.

    Creates a new therapeutic text adventure session for the authenticated user
    with optional therapeutic context and goals.
    """
    try:
        result = await gameplay_service.create_authenticated_session(
            auth_token=credentials.credentials,
            therapeutic_context=request.therapeutic_context,
        )

        if result.get("success"):
            return CreateSessionResponse(**result)
        # Map error codes to HTTP status codes
        status_code = status.HTTP_400_BAD_REQUEST
        if result.get("code") == "AUTH_ERROR":
            status_code = status.HTTP_401_UNAUTHORIZED
        elif result.get("code") == "SAFETY_ERROR":
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        raise HTTPException(
            status_code=status_code, detail=result.get("error", "Unknown error")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


@router.post("/sessions/{session_id}/choices", response_model=ProcessChoiceResponse)
async def process_choice(
    session_id: str,
    request: ProcessChoiceRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    gameplay_service: GameplayService = Depends(get_gameplay_service),
):
    """
    Process a user choice within a gameplay session.

    Processes the user's choice, generates consequences, and advances the narrative
    with authentication and safety validation.
    """
    try:
        result = await gameplay_service.process_validated_choice(
            session_id=session_id,
            choice_id=request.choice_id,
            auth_token=credentials.credentials,
        )

        if result.get("success"):
            return ProcessChoiceResponse(**result)
        # Map error codes to HTTP status codes
        status_code = status.HTTP_400_BAD_REQUEST
        if result.get("code") == "AUTH_ERROR":
            status_code = status.HTTP_401_UNAUTHORIZED
        elif result.get("code") == "SESSION_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        elif result.get("code") == "ACCESS_DENIED":
            status_code = status.HTTP_403_FORBIDDEN

        raise HTTPException(
            status_code=status_code, detail=result.get("error", "Unknown error")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process choice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


@router.get("/sessions/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    gameplay_service: GameplayService = Depends(get_gameplay_service),
):
    """
    Get the status of a gameplay session.

    Retrieves the current status and state of a gameplay session with
    authentication verification.
    """
    try:
        result = await gameplay_service.get_session_with_auth(
            session_id=session_id, auth_token=credentials.credentials
        )

        if result.get("success"):
            return SessionStatusResponse(**result)
        # Map error codes to HTTP status codes
        status_code = status.HTTP_400_BAD_REQUEST
        if result.get("code") == "AUTH_ERROR":
            status_code = status.HTTP_401_UNAUTHORIZED
        elif result.get("code") == "SESSION_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        elif result.get("code") == "ACCESS_DENIED":
            status_code = status.HTTP_403_FORBIDDEN

        raise HTTPException(
            status_code=status_code, detail=result.get("error", "Unknown error")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


@router.delete("/sessions/{session_id}", response_model=EndSessionResponse)
async def end_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    gameplay_service: GameplayService = Depends(get_gameplay_service),
):
    """
    End a gameplay session.

    Ends the specified gameplay session with authentication verification
    and performs cleanup operations.
    """
    try:
        result = await gameplay_service.end_session_with_auth(
            session_id=session_id, auth_token=credentials.credentials
        )

        if result.get("success"):
            return EndSessionResponse(**result)
        # Map error codes to HTTP status codes
        status_code = status.HTTP_400_BAD_REQUEST
        if result.get("code") == "AUTH_ERROR":
            status_code = status.HTTP_401_UNAUTHORIZED
        elif result.get("code") == "SESSION_NOT_FOUND":
            status_code = status.HTTP_404_NOT_FOUND
        elif result.get("code") == "ACCESS_DENIED":
            status_code = status.HTTP_403_FORBIDDEN

        raise HTTPException(
            status_code=status_code, detail=result.get("error", "Unknown error")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to end session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


@router.get("/sessions", response_model=UserSessionsResponse)
async def get_user_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    gameplay_service: GameplayService = Depends(get_gameplay_service),
):
    """
    Get all sessions for the authenticated user.

    Retrieves session metrics and information for all sessions
    belonging to the authenticated user.
    """
    try:
        result = await gameplay_service.get_user_sessions(
            auth_token=credentials.credentials
        )

        if result.get("success"):
            return UserSessionsResponse(**result)
        # Map error codes to HTTP status codes
        status_code = status.HTTP_400_BAD_REQUEST
        if result.get("code") == "AUTH_ERROR":
            status_code = status.HTTP_401_UNAUTHORIZED

        raise HTTPException(
            status_code=status_code, detail=result.get("error", "Unknown error")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


@router.get("/health")
async def gameplay_health_check(
    gameplay_service: GameplayService = Depends(get_gameplay_service),
):
    """
    Health check endpoint for the gameplay loop system.

    Returns the health status of the gameplay loop integration
    and all connected systems.
    """
    try:
        integration_status = gameplay_service.get_integration_status()

        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "integration_status": integration_status,
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "error": str(e),
        }
