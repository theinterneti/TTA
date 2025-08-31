"""
Gameplay WebSocket Router

This module provides WebSocket endpoints for real-time therapeutic gameplay interactions,
integrating with the GameplayLoopController for session-aware messaging and narrative delivery.
"""

import json
import logging
from collections import deque
from datetime import datetime
from typing import Any

from fastapi import WebSocket, status
from fastapi.routing import APIRouter

from src.components.gameplay_loop.controllers.gameplay_loop_controller import (
    GameplayLoopController,
)
from src.components.therapeutic_safety import SafetyValidationOrchestrator

from ...services.gameplay_chat_manager import GameplayChatManager
from ...services.narrative_generation_service import NarrativeGenerationService
from ...services.story_initialization_service import StoryInitializationService

logger = logging.getLogger(__name__)

router = APIRouter()

# Metrics for monitoring
METRICS = {
    "gameplay_sessions_started": 0,
    "gameplay_sessions_completed": 0,
    "gameplay_sessions_abandoned": 0,
    "messages_processed": 0,
    "story_events_generated": 0,
    "choices_presented": 0,
    "therapeutic_interventions": 0,
    "narrative_responses_sent": 0,
}

# Global managers (would be dependency-injected in production)
gameplay_chat_manager = GameplayChatManager()


def _auth_from_ws(websocket: WebSocket):
    """Extract and validate JWT token from WebSocket connection."""
    # Try query parameter first
    token = websocket.query_params.get("token")

    # Try Authorization header if no query param
    if not token:
        auth_header = websocket.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise PermissionError("No authentication token provided")

    # Validate token using existing auth system
    from ..auth import verify_token

    try:
        token_data = verify_token(token)
        return token_data
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise PermissionError("Invalid authentication token")


def _create_system_message(
    content: str, session_id: str | None = None
) -> dict[str, Any]:
    """Create a system message for WebSocket communication."""
    return {
        "type": "system_message",
        "session_id": session_id,
        "content": {"text": content},
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"source": "gameplay_system"},
    }


def _create_error_message(error: str, session_id: str | None = None) -> dict[str, Any]:
    """Create an error message for WebSocket communication."""
    return {
        "type": "error",
        "session_id": session_id,
        "content": {"error": error},
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"source": "gameplay_system"},
    }


@router.websocket("/gameplay/{player_id}/{session_id}")
async def websocket_gameplay_endpoint(
    websocket: WebSocket, player_id: str, session_id: str
) -> None:
    """
    WebSocket endpoint for therapeutic gameplay interactions.

    Provides real-time communication for story events, choice presentations,
    narrative responses, and therapeutic interventions during gameplay sessions.

    Args:
        player_id: Unique player identifier
        session_id: Unique session identifier

    Auth via query param token or Authorization header.
    """
    # Rate limiting setup
    max_msgs = 60  # Max messages per window (higher than chat for gameplay)
    window_seconds = 60  # Window duration
    window = deque()  # Sliding window for rate limiting

    # Authenticate
    try:
        token_data = _auth_from_ws(websocket)
    except PermissionError:
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Verify player_id matches token
    if token_data.player_id and token_data.player_id != player_id:
        await websocket.accept()
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Player ID mismatch"
        )
        return

    await gameplay_chat_manager.connect(player_id, websocket)

    # Initialize services (would be dependency-injected in production)
    try:
        # Initialize core gameplay services
        story_service = StoryInitializationService()
        narrative_service = NarrativeGenerationService()
        safety_validator = SafetyValidationOrchestrator()

        # Get or create gameplay loop controller
        gameplay_controller = GameplayLoopController.get_instance()

    except Exception as e:
        logger.error(f"Failed to initialize gameplay services: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    # Send welcome message
    welcome_msg = _create_system_message(
        "Connected to therapeutic gameplay. Your adventure awaits!"
    )
    await gameplay_chat_manager.send_json(websocket, welcome_msg)

    # Track active session
    current_session_id: str | None = None

    try:
        while True:
            raw = await websocket.receive_text()

            # Rate limiting
            now_ts = datetime.utcnow().timestamp()
            while window and (now_ts - window[0]) > window_seconds:
                window.popleft()
            window.append(now_ts)

            if len(window) > max_msgs:
                rate_limit_msg = _create_error_message(
                    "Please slow down - you're sending messages too quickly."
                )
                await gameplay_chat_manager.send_json(websocket, rate_limit_msg)
                continue

            # Parse message
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                error_msg = _create_error_message("Invalid message format.")
                await gameplay_chat_manager.send_json(websocket, error_msg)
                continue

            # Transform front-end message types to gameplay message types
            message_type = msg.get("type", "")
            if message_type == "user_message":
                # Transform front-end user_message to player_input
                message_type = "player_input"
                msg["type"] = "player_input"
                # Ensure content has the expected structure
                if "content" in msg and isinstance(msg["content"], dict):
                    if "text" in msg["content"] and "input_type" not in msg["content"]:
                        msg["content"]["input_type"] = "narrative_action"

            METRICS["messages_processed"] += 1

            if message_type == "player_input":
                # Handle player input messages (transformed from user_message)
                content = msg.get("content", {})
                message_text = content.get("text", "")

                if not message_text.strip():
                    error_msg = _create_error_message("Message text cannot be empty")
                    await gameplay_chat_manager.send_json(websocket, error_msg)
                    continue

                # Process through dynamic story generation
                try:
                    # Use the session_id from the URL path
                    story_response = (
                        await DynamicStoryGenerationService().process_player_message(
                            session_id=session_id,
                            player_id=player_id,
                            message_text=message_text,
                        )
                    )

                    if story_response and story_response.success:
                        # Send narrative response back to front-end
                        narrative_msg = {
                            "type": "narrative_response",
                            "session_id": session_id,
                            "content": {
                                "text": story_response.narrative_text,
                                "scene_updates": getattr(
                                    story_response, "scene_updates", {}
                                ),
                                "therapeutic_elements": getattr(
                                    story_response, "therapeutic_elements", {}
                                ),
                            },
                            "timestamp": datetime.utcnow().isoformat(),
                            "metadata": {
                                "response_type": story_response.response_type,
                                "therapeutic_focus": getattr(
                                    story_response, "therapeutic_focus", []
                                ),
                            },
                        }
                        await gameplay_chat_manager.send_json(websocket, narrative_msg)
                        METRICS["story_responses_sent"] += 1
                    else:
                        error_msg = _create_error_message(
                            "Failed to generate story response"
                        )
                        await gameplay_chat_manager.send_json(websocket, error_msg)

                except Exception as e:
                    logger.error(f"Error processing player message: {e}")
                    error_msg = _create_error_message(
                        "Story generation temporarily unavailable"
                    )
                    await gameplay_chat_manager.send_json(websocket, error_msg)

            elif message_type == "start_gameplay":
                # Start new gameplay session
                character_id = msg.get("character_id")
                world_id = msg.get("world_id")
                therapeutic_goals = msg.get("therapeutic_goals", [])

                if not character_id:
                    error_msg = _create_error_message(
                        "Character ID required to start gameplay"
                    )
                    await gameplay_chat_manager.send_json(websocket, error_msg)
                    continue

                # Initialize story session
                session_id = await story_service.initialize_story_session(
                    player_id=player_id,
                    character_id=character_id,
                    world_id=world_id,
                    therapeutic_goals=therapeutic_goals,
                )

                if session_id:
                    current_session_id = session_id
                    METRICS["gameplay_sessions_started"] += 1

                    # Send session started confirmation
                    session_msg = {
                        "type": "session_started",
                        "session_id": session_id,
                        "content": {
                            "message": "Your therapeutic adventure has begun!",
                            "character_id": character_id,
                            "world_id": world_id,
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    await gameplay_chat_manager.send_json(websocket, session_msg)

                    # Generate initial narrative
                    initial_story = await narrative_service.generate_opening_narrative(
                        session_id=session_id,
                        character_id=character_id,
                        world_id=world_id,
                    )

                    if initial_story:
                        story_msg = {
                            "type": "narrative_response",
                            "session_id": session_id,
                            "content": initial_story,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                        await gameplay_chat_manager.send_json(websocket, story_msg)
                        METRICS["narrative_responses_sent"] += 1
                else:
                    error_msg = _create_error_message(
                        "Failed to initialize gameplay session"
                    )
                    await gameplay_chat_manager.send_json(websocket, error_msg)

            elif message_type == "player_action":
                # Process player action in active session
                if not current_session_id:
                    error_msg = _create_error_message("No active gameplay session")
                    await gameplay_chat_manager.send_json(websocket, error_msg)
                    continue

                action_text = msg.get("content", {}).get("text", "")
                action_type = msg.get("content", {}).get(
                    "action_type", "narrative_input"
                )

                # Safety validation
                is_safe, safety_issues = await safety_validator.validate_content(
                    content=action_text,
                    context={"player_id": player_id, "session_id": current_session_id},
                )

                if not is_safe:
                    # Handle safety issues with therapeutic response
                    safety_msg = {
                        "type": "therapeutic_intervention",
                        "session_id": current_session_id,
                        "content": {
                            "intervention_type": "safety_guidance",
                            "message": "Let's explore that in a different way. What would feel safer to try?",
                            "resources": safety_issues.get("resources", []),
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    await gameplay_chat_manager.send_json(websocket, safety_msg)
                    METRICS["therapeutic_interventions"] += 1
                    continue

                # Process action through narrative service
                response = await narrative_service.process_player_action(
                    session_id=current_session_id,
                    action_text=action_text,
                    action_type=action_type,
                )

                if response:
                    # Send narrative response
                    narrative_msg = {
                        "type": "narrative_response",
                        "session_id": current_session_id,
                        "content": response,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    await gameplay_chat_manager.send_json(websocket, narrative_msg)
                    METRICS["narrative_responses_sent"] += 1

                    # Check if choices should be presented
                    if response.get("choices"):
                        choice_msg = {
                            "type": "choice_request",
                            "session_id": current_session_id,
                            "content": {
                                "prompt": response.get(
                                    "choice_prompt", "What do you do?"
                                ),
                                "choices": response["choices"],
                            },
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                        await gameplay_chat_manager.send_json(websocket, choice_msg)
                        METRICS["choices_presented"] += 1

            elif message_type == "end_session":
                # End current gameplay session
                if current_session_id:
                    await gameplay_controller.end_session(current_session_id)
                    METRICS["gameplay_sessions_completed"] += 1

                    end_msg = {
                        "type": "session_ended",
                        "session_id": current_session_id,
                        "content": {
                            "message": "Gameplay session ended. Thank you for playing!"
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    await gameplay_chat_manager.send_json(websocket, end_msg)
                    current_session_id = None

            else:
                logger.warning(f"Unknown message type: {message_type}")
                error_msg = _create_error_message(
                    f"Unknown message type: {message_type}"
                )
                await gameplay_chat_manager.send_json(websocket, error_msg)

    except Exception as e:
        logger.error(f"Error in gameplay WebSocket: {e}")
        if current_session_id:
            METRICS["gameplay_sessions_abandoned"] += 1

    finally:
        # Clean up connection
        await gameplay_chat_manager.disconnect(player_id, websocket)
        logger.info(f"Player {player_id} disconnected from gameplay")


@router.get("/gameplay/metrics")
async def get_gameplay_metrics():
    """Get gameplay WebSocket metrics."""
    return {
        "metrics": METRICS,
        "active_connections": len(gameplay_chat_manager.active_connections),
        "timestamp": datetime.utcnow().isoformat(),
    }
