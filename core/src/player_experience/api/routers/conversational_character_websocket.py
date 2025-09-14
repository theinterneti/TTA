"""
Conversational Character Creation WebSocket Handlers

This module extends the existing WebSocket infrastructure to support
conversational character creation with specialized message handlers.
"""

import json
import logging
from collections import deque
from datetime import datetime
from typing import Any

from fastapi import WebSocket, status
from fastapi.routing import APIRouter

from src.components.therapeutic_safety import SafetyValidationOrchestrator

from ...database.character_repository import CharacterRepository
from ...managers.character_avatar_manager import CharacterAvatarManager
from ...models.conversation_state import (
    ConversationCompletedMessage,
    CrisisDetectedMessage,
    ErrorMessage,
    MessageType,
    StartConversationMessage,
    UserResponseMessage,
    ValidationErrorMessage,
)
from ...services.conversation_flow_controller import ConversationFlowController
from ...services.conversational_character_service import ConversationalCharacterService

logger = logging.getLogger(__name__)

router = APIRouter()

# Metrics for monitoring
METRICS = {
    "conversations_started": 0,
    "conversations_completed": 0,
    "conversations_abandoned": 0,
    "messages_processed": 0,
    "crisis_detected": 0,
    "validation_errors": 0,
}


class ConversationalWebSocketManager:
    """Manages WebSocket connections for conversational character creation."""

    def __init__(self):
        # Active connections: player_id -> set of WebSocket connections
        self.active_connections: dict[str, set] = {}
        # Conversation sessions: conversation_id -> player_id
        self.conversation_sessions: dict[str, str] = {}

    async def connect(self, player_id: str, websocket: WebSocket) -> None:
        """Connect a player to the conversational WebSocket."""
        await websocket.accept()

        if player_id not in self.active_connections:
            self.active_connections[player_id] = set()

        self.active_connections[player_id].add(websocket)
        logger.info(
            f"Player {player_id} connected to conversational character creation"
        )

    def disconnect(self, player_id: str, websocket: WebSocket) -> None:
        """Disconnect a player from the conversational WebSocket."""
        if player_id in self.active_connections:
            self.active_connections[player_id].discard(websocket)
            if not self.active_connections[player_id]:
                del self.active_connections[player_id]

        # Clean up conversation sessions
        sessions_to_remove = [
            conv_id
            for conv_id, pid in self.conversation_sessions.items()
            if pid == player_id
        ]
        for conv_id in sessions_to_remove:
            del self.conversation_sessions[conv_id]

        logger.info(
            f"Player {player_id} disconnected from conversational character creation"
        )

    async def send_json(self, websocket: WebSocket, payload: dict[str, Any]) -> None:
        """Send JSON message to a specific WebSocket."""
        try:
            await websocket.send_text(json.dumps(payload, default=str))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    async def broadcast_to_player(
        self, player_id: str, payload: dict[str, Any]
    ) -> None:
        """Broadcast message to all connections for a player."""
        if player_id in self.active_connections:
            for websocket in list(self.active_connections[player_id]):
                try:
                    await self.send_json(websocket, payload)
                except Exception as e:
                    logger.error(f"Failed to broadcast to player {player_id}: {e}")
                    # Remove failed connection
                    self.active_connections[player_id].discard(websocket)


# Global manager instance
conversation_manager = ConversationalWebSocketManager()


def _auth_from_ws(websocket: WebSocket) -> Any:
    """Extract authentication from WebSocket connection."""
    # Check query parameters for token
    token = websocket.query_params.get("token")
    if not token:
        # Check headers (if supported by client)
        auth_header = websocket.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise PermissionError("No authentication token provided")

    # Validate token (simplified - would use proper JWT validation)
    try:
        # This would be replaced with proper JWT validation
        from ...auth import decode_jwt_token

        token_data = decode_jwt_token(token)
        return token_data
    except Exception:
        raise PermissionError("Invalid authentication token") from None


def _serialize_message(message: Any) -> dict[str, Any]:
    """Serialize message objects to JSON-compatible dictionaries."""
    if hasattr(message, "dict"):
        return message.dict()
    elif hasattr(message, "__dict__"):
        return {k: v for k, v in message.__dict__.items() if not k.startswith("_")}
    else:
        return {"content": str(message)}


@router.websocket("/conversational-character-creation")
async def websocket_conversational_character_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for conversational character creation."""

    # Rate limiting setup
    max_msgs = 30  # Max messages per window
    window_seconds = 60  # Window duration
    window = deque()  # Sliding window for rate limiting

    # Authenticate
    try:
        token_data = _auth_from_ws(websocket)
    except PermissionError:
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    player_id = token_data.player_id or ""
    await conversation_manager.connect(player_id, websocket)

    # Initialize services (would be dependency-injected in production)
    try:
        character_repository = CharacterRepository()
        character_manager = CharacterAvatarManager(character_repository)
        safety_validator = SafetyValidationOrchestrator()

        conversational_service = ConversationalCharacterService(
            character_manager=character_manager,
            character_repository=character_repository,
            safety_validator=safety_validator,
        )

        flow_controller = ConversationFlowController(safety_validator)

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    # Send welcome message
    welcome_payload = {
        "type": "system",
        "content": {
            "text": "Welcome to conversational character creation! I'm here to help you create your therapeutic companion through a natural conversation."
        },
        "metadata": {"system": "conversational_character_creation"},
    }
    await conversation_manager.send_json(websocket, welcome_payload)

    try:
        while True:
            raw = await websocket.receive_text()

            # Rate limiting
            now_ts = datetime.utcnow().timestamp()
            while window and (now_ts - window[0]) > window_seconds:
                window.popleft()
            window.append(now_ts)

            if len(window) > max_msgs:
                rate_limit_msg = {
                    "type": "system",
                    "content": {
                        "text": "Please slow down - you're sending messages too quickly."
                    },
                }
                await conversation_manager.send_json(websocket, rate_limit_msg)
                continue

            # Parse message
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                error_msg = {
                    "type": "error",
                    "content": {"text": "Invalid message format."},
                }
                await conversation_manager.send_json(websocket, error_msg)
                continue

            # Process message based on type
            message_type = msg.get("type", "")
            METRICS["messages_processed"] += 1

            try:
                if message_type == MessageType.START_CONVERSATION:
                    await _handle_start_conversation(
                        msg, player_id, websocket, conversational_service
                    )

                elif message_type == MessageType.USER_RESPONSE:
                    await _handle_user_response(
                        msg, websocket, conversational_service, flow_controller
                    )

                elif message_type == MessageType.PAUSE_CONVERSATION:
                    await _handle_pause_conversation(
                        msg, websocket, conversational_service
                    )

                elif message_type == MessageType.RESUME_CONVERSATION:
                    await _handle_resume_conversation(
                        msg, websocket, conversational_service
                    )

                elif message_type == MessageType.ABANDON_CONVERSATION:
                    await _handle_abandon_conversation(
                        msg, websocket, conversational_service
                    )

                else:
                    error_msg = ErrorMessage(
                        error_code="UNKNOWN_MESSAGE_TYPE",
                        error_message=f"Unknown message type: {message_type}",
                    )
                    await conversation_manager.send_json(
                        websocket, _serialize_message(error_msg)
                    )

            except Exception as e:
                logger.error(f"Error processing message type {message_type}: {e}")
                error_msg = ErrorMessage(
                    error_code="PROCESSING_ERROR",
                    error_message="Failed to process message",
                )
                await conversation_manager.send_json(
                    websocket, _serialize_message(error_msg)
                )

    except Exception as e:
        logger.error(f"WebSocket error for player {player_id}: {e}")

    finally:
        conversation_manager.disconnect(player_id, websocket)


async def _handle_start_conversation(
    msg: dict[str, Any],
    player_id: str,
    websocket: WebSocket,
    service: ConversationalCharacterService,
) -> None:
    """Handle start conversation message."""
    try:
        # Validate message
        start_msg = StartConversationMessage(**msg)

        # Start conversation
        conversation_id, assistant_message = await service.start_conversation(
            player_id, start_msg.metadata
        )

        # Track conversation session
        conversation_manager.conversation_sessions[conversation_id] = player_id

        # Send conversation started confirmation
        started_msg = {
            "type": MessageType.CONVERSATION_STARTED,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await conversation_manager.send_json(websocket, started_msg)

        # Send initial assistant message
        await conversation_manager.send_json(
            websocket, _serialize_message(assistant_message)
        )

        METRICS["conversations_started"] += 1
        logger.info(f"Started conversation {conversation_id} for player {player_id}")

    except Exception as e:
        logger.error(f"Failed to start conversation: {e}")
        error_msg = ErrorMessage(
            error_code="START_CONVERSATION_FAILED",
            error_message="Failed to start conversation",
        )
        await conversation_manager.send_json(websocket, _serialize_message(error_msg))


async def _handle_user_response(
    msg: dict[str, Any],
    websocket: WebSocket,
    service: ConversationalCharacterService,
    flow_controller: ConversationFlowController,
) -> None:
    """Handle user response message."""
    try:
        # Validate message
        response_msg = UserResponseMessage(**msg)

        # Get conversation state
        conversation_state = await service.get_conversation_state(
            response_msg.conversation_id
        )
        if not conversation_state:
            error_msg = ErrorMessage(
                conversation_id=response_msg.conversation_id,
                error_code="CONVERSATION_NOT_FOUND",
                error_message="Conversation not found",
            )
            await conversation_manager.send_json(
                websocket, _serialize_message(error_msg)
            )
            return

        # Validate progression if needed
        next_stage = flow_controller.get_next_stage_recommendation(conversation_state)
        if next_stage:
            can_progress, reason = await flow_controller.validate_stage_progression(
                conversation_state, next_stage
            )
            if not can_progress:
                validation_msg = ValidationErrorMessage(
                    conversation_id=response_msg.conversation_id,
                    error_message=reason or "Cannot progress at this time",
                    retry_prompt="Let's continue with the current topic for now.",
                )
                await conversation_manager.send_json(
                    websocket, _serialize_message(validation_msg)
                )
                return

        # Process user response
        response_messages = await service.process_user_response(
            response_msg.conversation_id, response_msg.content
        )

        # Send all response messages
        for response in response_messages:
            await conversation_manager.send_json(
                websocket, _serialize_message(response)
            )

            # Track metrics
            if isinstance(response, CrisisDetectedMessage):
                METRICS["crisis_detected"] += 1
            elif isinstance(response, ValidationErrorMessage):
                METRICS["validation_errors"] += 1
            elif isinstance(response, ConversationCompletedMessage):
                METRICS["conversations_completed"] += 1

    except Exception as e:
        logger.error(f"Failed to handle user response: {e}")
        error_msg = ErrorMessage(
            conversation_id=msg.get("conversation_id"),
            error_code="RESPONSE_PROCESSING_FAILED",
            error_message="Failed to process response",
        )
        await conversation_manager.send_json(websocket, _serialize_message(error_msg))


async def _handle_pause_conversation(
    msg: dict[str, Any], websocket: WebSocket, service: ConversationalCharacterService
) -> None:
    """Handle pause conversation message."""
    try:
        conversation_id = msg.get("conversation_id")
        if not conversation_id:
            raise ValueError("Missing conversation_id")

        success = await service.pause_conversation(conversation_id)

        if success:
            pause_msg = {
                "type": MessageType.CONVERSATION_PAUSED,
                "conversation_id": conversation_id,
                "message": "Conversation paused. You can resume anytime.",
                "timestamp": datetime.utcnow().isoformat(),
            }
            await conversation_manager.send_json(websocket, pause_msg)
        else:
            error_msg = ErrorMessage(
                conversation_id=conversation_id,
                error_code="PAUSE_FAILED",
                error_message="Failed to pause conversation",
            )
            await conversation_manager.send_json(
                websocket, _serialize_message(error_msg)
            )

    except Exception as e:
        logger.error(f"Failed to pause conversation: {e}")


async def _handle_resume_conversation(
    msg: dict[str, Any], websocket: WebSocket, service: ConversationalCharacterService
) -> None:
    """Handle resume conversation message."""
    try:
        conversation_id = msg.get("conversation_id")
        if not conversation_id:
            raise ValueError("Missing conversation_id")

        assistant_message = await service.resume_conversation(conversation_id)

        if assistant_message:
            await conversation_manager.send_json(
                websocket, _serialize_message(assistant_message)
            )
        else:
            error_msg = ErrorMessage(
                conversation_id=conversation_id,
                error_code="RESUME_FAILED",
                error_message="Failed to resume conversation",
            )
            await conversation_manager.send_json(
                websocket, _serialize_message(error_msg)
            )

    except Exception as e:
        logger.error(f"Failed to resume conversation: {e}")


async def _handle_abandon_conversation(
    msg: dict[str, Any], websocket: WebSocket, service: ConversationalCharacterService
) -> None:
    """Handle abandon conversation message."""
    try:
        conversation_id = msg.get("conversation_id")
        if not conversation_id:
            raise ValueError("Missing conversation_id")

        # Get conversation state and mark as abandoned
        conversation_state = await service.get_conversation_state(conversation_id)
        if conversation_state:
            conversation_state.status = "abandoned"
            conversation_state.update_activity()

        # Clean up session tracking
        if conversation_id in conversation_manager.conversation_sessions:
            del conversation_manager.conversation_sessions[conversation_id]

        abandon_msg = {
            "type": "conversation_abandoned",
            "conversation_id": conversation_id,
            "message": "Conversation ended. You can start a new one anytime.",
            "timestamp": datetime.utcnow().isoformat(),
        }
        await conversation_manager.send_json(websocket, abandon_msg)

        METRICS["conversations_abandoned"] += 1
        logger.info(f"Conversation {conversation_id} abandoned")

    except Exception as e:
        logger.error(f"Failed to abandon conversation: {e}")


@router.get("/conversational-character-creation/metrics")
async def get_conversation_metrics():
    """Get conversation metrics for monitoring."""
    return {
        "metrics": METRICS,
        "active_connections": len(conversation_manager.active_connections),
        "active_conversations": len(conversation_manager.conversation_sessions),
    }
