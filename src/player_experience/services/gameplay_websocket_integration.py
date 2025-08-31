"""
Gameplay WebSocket Integration Service

This module provides integration between the GameplayLoopController and WebSocket communication,
enabling real-time session management, break point detection, and therapeutic monitoring.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.components.gameplay_loop.controllers.gameplay_loop_controller import (
    GameplayLoopController,
    SessionBreakPoint,
    SessionConfiguration,
)
from src.components.gameplay_loop.narrative.events import (
    EventBus,
    EventType,
    NarrativeEvent,
)
from src.components.gameplay_loop.services.session_state import (
    SessionState,
)

from .gameplay_chat_manager import GameplayChatManager

logger = logging.getLogger(__name__)


@dataclass
class WebSocketSessionContext:
    """Context for a WebSocket-enabled gameplay session."""

    session_id: str
    player_id: str
    connection_ids: list[str]
    session_state: SessionState
    last_break_point: SessionBreakPoint | None = None
    websocket_callbacks: dict[str, Callable] = None

    def __post_init__(self):
        if self.websocket_callbacks is None:
            self.websocket_callbacks = {}


class GameplayWebSocketIntegration:
    """
    Integration service connecting GameplayLoopController with WebSocket communication.

    Provides real-time session management, break point notifications, therapeutic monitoring,
    and seamless communication between gameplay sessions and connected clients.
    """

    def __init__(
        self,
        gameplay_controller: GameplayLoopController,
        chat_manager: GameplayChatManager,
        event_bus: EventBus | None = None,
    ):
        """
        Initialize the WebSocket integration service.

        Args:
            gameplay_controller: GameplayLoopController instance
            chat_manager: GameplayChatManager instance
            event_bus: Optional EventBus for event handling
        """
        self.gameplay_controller = gameplay_controller
        self.chat_manager = chat_manager
        self.event_bus = event_bus

        # Session tracking
        self.websocket_sessions: dict[str, WebSocketSessionContext] = {}
        self.player_sessions: dict[str, list[str]] = {}  # player_id -> session_ids

        # Event handlers
        self.event_handlers: dict[EventType, list[Callable]] = {}

        # Configuration
        self.auto_break_point_detection = True
        self.real_time_monitoring = True
        self.therapeutic_intervention_enabled = True

        # Metrics
        self.metrics = {
            "websocket_sessions_created": 0,
            "break_points_sent": 0,
            "therapeutic_interventions_sent": 0,
            "real_time_updates_sent": 0,
            "session_state_broadcasts": 0,
        }

        # Setup event handlers
        self._setup_event_handlers()

        logger.info("GameplayWebSocketIntegration initialized")

    def _setup_event_handlers(self):
        """Setup event handlers for gameplay events."""
        if self.event_bus:
            # Session lifecycle events
            self.event_bus.subscribe(
                EventType.SESSION_STARTED, self._handle_session_started
            )
            self.event_bus.subscribe(
                EventType.SESSION_PAUSED, self._handle_session_paused
            )
            self.event_bus.subscribe(
                EventType.SESSION_RESUMED, self._handle_session_resumed
            )
            self.event_bus.subscribe(
                EventType.SESSION_ENDED, self._handle_session_ended
            )

            # Break point events
            self.event_bus.subscribe(
                EventType.BREAK_POINT_DETECTED, self._handle_break_point_detected
            )

            # Therapeutic events
            self.event_bus.subscribe(
                EventType.THERAPEUTIC_INTERVENTION,
                self._handle_therapeutic_intervention,
            )

            # Narrative events
            self.event_bus.subscribe(
                EventType.SCENE_COMPLETED, self._handle_scene_completed
            )
            self.event_bus.subscribe(EventType.CHOICE_MADE, self._handle_choice_made)

    async def create_websocket_session(
        self,
        player_id: str,
        connection_id: str,
        session_config: SessionConfiguration | None = None,
        therapeutic_goals: list[str] | None = None,
    ) -> str:
        """
        Create a new WebSocket-enabled gameplay session.

        Args:
            player_id: Player identifier
            connection_id: WebSocket connection identifier
            session_config: Optional session configuration
            therapeutic_goals: Optional therapeutic goals

        Returns:
            Session ID
        """
        try:
            # Start session with GameplayLoopController
            session_state, session_summary = (
                await self.gameplay_controller.start_session(
                    user_id=player_id, session_config=session_config
                )
            )

            session_id = session_state.session_id

            # Create WebSocket session context
            websocket_context = WebSocketSessionContext(
                session_id=session_id,
                player_id=player_id,
                connection_ids=[connection_id],
                session_state=session_state,
            )

            # Register session
            self.websocket_sessions[session_id] = websocket_context

            if player_id not in self.player_sessions:
                self.player_sessions[player_id] = []
            self.player_sessions[player_id].append(session_id)

            # Associate connection with session in chat manager
            await self.chat_manager.associate_session(
                connection_id, session_id, session_state
            )

            # Send session started notification
            await self._broadcast_session_event(
                session_id,
                {
                    "type": "session_started",
                    "session_id": session_id,
                    "content": {
                        "message": "Your therapeutic gameplay session has started!",
                        "session_config": {
                            "pacing": (
                                session_config.pacing.value
                                if session_config
                                else "standard"
                            ),
                            "therapeutic_goals": therapeutic_goals or [],
                        },
                        "session_summary": {
                            "estimated_duration": session_summary.estimated_duration_minutes,
                            "therapeutic_focus": session_summary.therapeutic_focus,
                        },
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            # Update metrics
            self.metrics["websocket_sessions_created"] += 1

            logger.info(
                f"Created WebSocket gameplay session {session_id} for player {player_id}"
            )
            return session_id

        except Exception as e:
            logger.error(
                f"Failed to create WebSocket session for player {player_id}: {e}"
            )
            raise

    async def add_connection_to_session(
        self, session_id: str, connection_id: str
    ) -> bool:
        """
        Add an additional WebSocket connection to an existing session.

        Args:
            session_id: Session identifier
            connection_id: WebSocket connection identifier

        Returns:
            True if connection was added successfully
        """
        try:
            websocket_context = self.websocket_sessions.get(session_id)
            if not websocket_context:
                logger.error(f"Session {session_id} not found")
                return False

            # Add connection to session context
            if connection_id not in websocket_context.connection_ids:
                websocket_context.connection_ids.append(connection_id)

            # Associate connection with session in chat manager
            await self.chat_manager.associate_session(
                connection_id, session_id, websocket_context.session_state
            )

            # Send current session state to new connection
            connection = self.chat_manager.connection_registry.get(connection_id)
            if connection:
                await self.chat_manager.send_json(
                    connection.websocket,
                    {
                        "type": "session_state_update",
                        "session_id": session_id,
                        "content": {
                            "current_state": websocket_context.session_state.state_type.value,
                            "session_phase": websocket_context.session_state.current_scene_id,
                            "therapeutic_context": websocket_context.session_state.therapeutic_context,
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

            logger.info(f"Added connection {connection_id} to session {session_id}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to add connection {connection_id} to session {session_id}: {e}"
            )
            return False

    async def remove_connection_from_session(
        self, session_id: str, connection_id: str
    ) -> bool:
        """
        Remove a WebSocket connection from a session.

        Args:
            session_id: Session identifier
            connection_id: WebSocket connection identifier

        Returns:
            True if connection was removed successfully
        """
        try:
            websocket_context = self.websocket_sessions.get(session_id)
            if not websocket_context:
                return False

            # Remove connection from session context
            if connection_id in websocket_context.connection_ids:
                websocket_context.connection_ids.remove(connection_id)

            # Dissociate connection from session in chat manager
            await self.chat_manager.dissociate_session(connection_id)

            # If no connections remain, consider pausing the session
            if not websocket_context.connection_ids:
                await self._handle_session_disconnection(session_id)

            logger.info(f"Removed connection {connection_id} from session {session_id}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to remove connection {connection_id} from session {session_id}: {e}"
            )
            return False

    async def end_websocket_session(
        self, session_id: str, completion_reason: str = "user_completed"
    ) -> bool:
        """
        End a WebSocket-enabled gameplay session.

        Args:
            session_id: Session identifier
            completion_reason: Reason for session completion

        Returns:
            True if session was ended successfully
        """
        try:
            websocket_context = self.websocket_sessions.get(session_id)
            if not websocket_context:
                logger.warning(f"Session {session_id} not found in WebSocket sessions")
                return False

            # End session with GameplayLoopController
            session_summary = await self.gameplay_controller.end_session(
                session_id, completion_reason
            )

            # Send session ended notification
            await self._broadcast_session_event(
                session_id,
                {
                    "type": "session_ended",
                    "session_id": session_id,
                    "content": {
                        "message": "Your therapeutic gameplay session has ended.",
                        "completion_reason": completion_reason,
                        "session_summary": {
                            "duration_minutes": session_summary.actual_duration_minutes,
                            "scenes_completed": len(session_summary.scenes_completed),
                            "therapeutic_progress": session_summary.therapeutic_progress,
                            "achievements": session_summary.achievements,
                        },
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            # Clean up WebSocket session context
            await self._cleanup_websocket_session(session_id)

            logger.info(f"Ended WebSocket gameplay session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to end WebSocket session {session_id}: {e}")
            return False

    async def pause_websocket_session(
        self, session_id: str, pause_reason: str | None = None
    ) -> bool:
        """
        Pause a WebSocket-enabled gameplay session.

        Args:
            session_id: Session identifier
            pause_reason: Optional reason for pausing

        Returns:
            True if session was paused successfully
        """
        try:
            # Pause session with GameplayLoopController
            session_state = await self.gameplay_controller.pause_session(
                session_id, pause_reason
            )

            # Update WebSocket session context
            websocket_context = self.websocket_sessions.get(session_id)
            if websocket_context:
                websocket_context.session_state = session_state

            # Send session paused notification
            await self._broadcast_session_event(
                session_id,
                {
                    "type": "session_paused",
                    "session_id": session_id,
                    "content": {
                        "message": "Your session has been paused. You can resume anytime.",
                        "pause_reason": pause_reason,
                        "pause_timestamp": datetime.utcnow().isoformat(),
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            logger.info(f"Paused WebSocket gameplay session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to pause WebSocket session {session_id}: {e}")
            return False

    async def resume_websocket_session(self, session_id: str) -> bool:
        """
        Resume a paused WebSocket-enabled gameplay session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was resumed successfully
        """
        try:
            # Resume session with GameplayLoopController
            session_state = await self.gameplay_controller.resume_session(session_id)

            # Update WebSocket session context
            websocket_context = self.websocket_sessions.get(session_id)
            if websocket_context:
                websocket_context.session_state = session_state

            # Send session resumed notification
            await self._broadcast_session_event(
                session_id,
                {
                    "type": "session_resumed",
                    "session_id": session_id,
                    "content": {
                        "message": "Welcome back! Your session has been resumed.",
                        "resume_timestamp": datetime.utcnow().isoformat(),
                        "current_scene": session_state.current_scene_id,
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            logger.info(f"Resumed WebSocket gameplay session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to resume WebSocket session {session_id}: {e}")
            return False

    async def broadcast_session_update(
        self, session_id: str, update_data: dict[str, Any]
    ) -> int:
        """
        Broadcast a session update to all connected clients.

        Args:
            session_id: Session identifier
            update_data: Update data to broadcast

        Returns:
            Number of connections that received the update
        """
        try:
            update_message = {
                "type": "session_update",
                "session_id": session_id,
                "content": update_data,
                "timestamp": datetime.utcnow().isoformat(),
            }

            sent_count = await self.chat_manager.broadcast_to_session(
                session_id, update_message
            )
            self.metrics["real_time_updates_sent"] += sent_count

            return sent_count

        except Exception as e:
            logger.error(f"Failed to broadcast session update for {session_id}: {e}")
            return 0

    # Event Handlers

    async def _handle_session_started(self, event: NarrativeEvent) -> None:
        """Handle session started event."""
        session_id = event.session_id
        await self._broadcast_session_event(
            session_id,
            {
                "type": "session_lifecycle_event",
                "event": "started",
                "session_id": session_id,
                "content": {"message": "Session started successfully"},
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def _handle_session_paused(self, event: NarrativeEvent) -> None:
        """Handle session paused event."""
        session_id = event.session_id
        await self._broadcast_session_event(
            session_id,
            {
                "type": "session_lifecycle_event",
                "event": "paused",
                "session_id": session_id,
                "content": {"message": "Session paused"},
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def _handle_session_resumed(self, event: NarrativeEvent) -> None:
        """Handle session resumed event."""
        session_id = event.session_id
        await self._broadcast_session_event(
            session_id,
            {
                "type": "session_lifecycle_event",
                "event": "resumed",
                "session_id": session_id,
                "content": {"message": "Session resumed"},
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def _handle_session_ended(self, event: NarrativeEvent) -> None:
        """Handle session ended event."""
        session_id = event.session_id
        await self._broadcast_session_event(
            session_id,
            {
                "type": "session_lifecycle_event",
                "event": "ended",
                "session_id": session_id,
                "content": {"message": "Session ended"},
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        # Clean up WebSocket session
        await self._cleanup_websocket_session(session_id)

    async def _handle_break_point_detected(self, event: NarrativeEvent) -> None:
        """Handle break point detected event."""
        if not self.auto_break_point_detection:
            return

        session_id = event.session_id
        break_point_data = event.data.get("break_point", {})

        # Send break point notification
        await self._broadcast_session_event(
            session_id,
            {
                "type": "break_point_detected",
                "session_id": session_id,
                "content": {
                    "break_point_type": break_point_data.get("type"),
                    "message": break_point_data.get(
                        "message", "Would you like to take a break?"
                    ),
                    "suggested_duration": break_point_data.get("suggested_duration", 5),
                    "options": ["take_break", "continue_playing", "end_session"],
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        self.metrics["break_points_sent"] += 1

    async def _handle_therapeutic_intervention(self, event: NarrativeEvent) -> None:
        """Handle therapeutic intervention event."""
        if not self.therapeutic_intervention_enabled:
            return

        session_id = event.session_id
        intervention_data = event.data.get("intervention", {})

        # Send therapeutic intervention
        await self._broadcast_session_event(
            session_id,
            {
                "type": "therapeutic_intervention",
                "session_id": session_id,
                "content": {
                    "intervention_type": intervention_data.get("type"),
                    "message": intervention_data.get("message"),
                    "resources": intervention_data.get("resources", []),
                    "severity": intervention_data.get("severity", "low"),
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        self.metrics["therapeutic_interventions_sent"] += 1

    async def _handle_scene_completed(self, event: NarrativeEvent) -> None:
        """Handle scene completed event."""
        session_id = event.session_id
        scene_data = event.data.get("scene", {})

        # Send scene completion notification
        await self._broadcast_session_event(
            session_id,
            {
                "type": "scene_completed",
                "session_id": session_id,
                "content": {
                    "scene_id": scene_data.get("scene_id"),
                    "scene_title": scene_data.get("title"),
                    "completion_message": scene_data.get("completion_message"),
                    "achievements": scene_data.get("achievements", []),
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def _handle_choice_made(self, event: NarrativeEvent) -> None:
        """Handle choice made event."""
        session_id = event.session_id
        choice_data = event.data.get("choice", {})

        # Send choice confirmation
        await self._broadcast_session_event(
            session_id,
            {
                "type": "choice_confirmed",
                "session_id": session_id,
                "content": {
                    "choice_id": choice_data.get("choice_id"),
                    "choice_text": choice_data.get("text"),
                    "consequences": choice_data.get("consequences", []),
                },
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    # Helper Methods

    async def _broadcast_session_event(
        self, session_id: str, event_data: dict[str, Any]
    ) -> int:
        """Broadcast an event to all connections in a session."""
        sent_count = await self.chat_manager.broadcast_to_session(
            session_id, event_data
        )
        self.metrics["session_state_broadcasts"] += 1
        return sent_count

    async def _handle_session_disconnection(self, session_id: str) -> None:
        """Handle when all connections disconnect from a session."""
        try:
            # Pause the session to preserve state
            await self.pause_websocket_session(
                session_id, "all_connections_disconnected"
            )
            logger.info(f"Auto-paused session {session_id} due to disconnection")
        except Exception as e:
            logger.error(
                f"Failed to handle session disconnection for {session_id}: {e}"
            )

    async def _cleanup_websocket_session(self, session_id: str) -> None:
        """Clean up WebSocket session context."""
        try:
            websocket_context = self.websocket_sessions.get(session_id)
            if not websocket_context:
                return

            # Remove from player sessions
            player_id = websocket_context.player_id
            if player_id in self.player_sessions:
                if session_id in self.player_sessions[player_id]:
                    self.player_sessions[player_id].remove(session_id)
                if not self.player_sessions[player_id]:
                    del self.player_sessions[player_id]

            # Dissociate all connections
            for connection_id in websocket_context.connection_ids:
                await self.chat_manager.dissociate_session(connection_id)

            # Remove from WebSocket sessions
            del self.websocket_sessions[session_id]

            logger.info(f"Cleaned up WebSocket session context for {session_id}")

        except Exception as e:
            logger.error(f"Failed to cleanup WebSocket session {session_id}: {e}")

    def get_session_info(self, session_id: str) -> dict[str, Any] | None:
        """Get information about a WebSocket session."""
        websocket_context = self.websocket_sessions.get(session_id)
        if not websocket_context:
            return None

        return {
            "session_id": session_id,
            "player_id": websocket_context.player_id,
            "connection_count": len(websocket_context.connection_ids),
            "session_state": websocket_context.session_state.state_type.value,
            "current_scene": websocket_context.session_state.current_scene_id,
            "last_break_point": (
                websocket_context.last_break_point.break_point_type.value
                if websocket_context.last_break_point
                else None
            ),
        }

    def get_player_sessions(self, player_id: str) -> list[dict[str, Any]]:
        """Get all WebSocket sessions for a player."""
        sessions = []
        session_ids = self.player_sessions.get(player_id, [])

        for session_id in session_ids:
            session_info = self.get_session_info(session_id)
            if session_info:
                sessions.append(session_info)

        return sessions

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the WebSocket integration."""
        return {
            **self.metrics,
            "active_websocket_sessions": len(self.websocket_sessions),
            "players_with_sessions": len(self.player_sessions),
        }
