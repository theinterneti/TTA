"""
Gameplay Chat Manager

This module provides enhanced WebSocket connection management for therapeutic gameplay sessions,
integrating with the GameplayLoopController for session-aware messaging and lifecycle management.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from fastapi import WebSocket

from src.components.gameplay_loop.controllers.gameplay_loop_controller import (
    GameplayLoopController,
)
from src.components.gameplay_loop.services.session_state import (
    SessionState,
)

logger = logging.getLogger(__name__)


@dataclass
class GameplayConnection:
    """Represents a gameplay WebSocket connection with session context."""

    websocket: WebSocket
    player_id: str
    connection_id: str
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    current_session_id: str | None = None
    session_state: SessionState | None = None
    is_active: bool = True
    message_count: int = 0
    therapeutic_flags: dict[str, Any] = field(default_factory=dict)


class GameplayChatManager:
    """
    Enhanced connection manager for therapeutic gameplay WebSocket sessions.

    Integrates with GameplayLoopController to provide session-aware messaging,
    therapeutic monitoring, and proper lifecycle management for gameplay connections.
    """

    def __init__(self, gameplay_controller: GameplayLoopController | None = None):
        """
        Initialize the Gameplay Chat Manager.

        Args:
            gameplay_controller: Optional GameplayLoopController instance
        """
        self.gameplay_controller = gameplay_controller

        # Connection management
        self.active_connections: dict[str, set[GameplayConnection]] = (
            {}
        )  # player_id -> connections
        self.connection_registry: dict[str, GameplayConnection] = (
            {}
        )  # connection_id -> connection
        self.session_connections: dict[str, set[str]] = (
            {}
        )  # session_id -> connection_ids

        # Configuration
        self.max_connections_per_player = 3  # Allow multiple tabs/devices
        self.connection_timeout = timedelta(minutes=30)  # Idle timeout
        self.heartbeat_interval = timedelta(seconds=30)  # Heartbeat frequency

        # Metrics
        self.metrics = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "sessions_managed": 0,
            "therapeutic_interventions": 0,
        }

        # Background tasks
        self._cleanup_task: asyncio.Task | None = None
        self._heartbeat_task: asyncio.Task | None = None

        logger.info("GameplayChatManager initialized")

    async def start_background_tasks(self):
        """Start background maintenance tasks."""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        if not self._heartbeat_task:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop_background_tasks(self):
        """Stop background maintenance tasks."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

    async def connect(self, player_id: str, websocket: WebSocket) -> str:
        """
        Connect a player to the gameplay WebSocket system.

        Args:
            player_id: Player identifier
            websocket: WebSocket connection

        Returns:
            Connection ID

        Raises:
            Exception: If connection cannot be established
        """
        # Check connection limits
        if player_id in self.active_connections:
            if (
                len(self.active_connections[player_id])
                >= self.max_connections_per_player
            ):
                await websocket.close(code=1013, reason="Too many connections")
                raise Exception(f"Maximum connections exceeded for player {player_id}")

        # Accept the WebSocket connection
        await websocket.accept()

        # Create connection record
        connection_id = f"gameplay_{player_id}_{datetime.utcnow().timestamp()}"
        connection = GameplayConnection(
            websocket=websocket, player_id=player_id, connection_id=connection_id
        )

        # Register connection
        if player_id not in self.active_connections:
            self.active_connections[player_id] = set()

        self.active_connections[player_id].add(connection)
        self.connection_registry[connection_id] = connection

        # Update metrics
        self.metrics["total_connections"] += 1
        self.metrics["active_connections"] = len(self.connection_registry)

        # Start background tasks if not already running
        await self.start_background_tasks()

        logger.info(
            f"Player {player_id} connected to gameplay (connection: {connection_id})"
        )
        return connection_id

    async def disconnect(self, player_id: str, websocket: WebSocket) -> None:
        """
        Disconnect a player from the gameplay WebSocket system.

        Args:
            player_id: Player identifier
            websocket: WebSocket connection to disconnect
        """
        # Find and remove the connection
        connection_to_remove = None
        if player_id in self.active_connections:
            for connection in list(self.active_connections[player_id]):
                if connection.websocket == websocket:
                    connection_to_remove = connection
                    break

        if connection_to_remove:
            # Remove from active connections
            self.active_connections[player_id].discard(connection_to_remove)
            if not self.active_connections[player_id]:
                del self.active_connections[player_id]

            # Remove from registry
            if connection_to_remove.connection_id in self.connection_registry:
                del self.connection_registry[connection_to_remove.connection_id]

            # Remove from session connections
            if connection_to_remove.current_session_id:
                session_id = connection_to_remove.current_session_id
                if session_id in self.session_connections:
                    self.session_connections[session_id].discard(
                        connection_to_remove.connection_id
                    )
                    if not self.session_connections[session_id]:
                        del self.session_connections[session_id]

            # Update metrics
            self.metrics["active_connections"] = len(self.connection_registry)

            logger.info(
                f"Player {player_id} disconnected from gameplay (connection: {connection_to_remove.connection_id})"
            )

        # Close WebSocket if still open
        try:
            if websocket.client_state.name != "DISCONNECTED":
                await websocket.close()
        except Exception as e:
            logger.debug(f"Error closing WebSocket: {e}")

    async def send_json(self, websocket: WebSocket, payload: dict[str, Any]) -> bool:
        """
        Send JSON message to a specific WebSocket connection.

        Args:
            websocket: Target WebSocket connection
            payload: Message payload

        Returns:
            True if message was sent successfully
        """
        try:
            await websocket.send_text(json.dumps(payload, default=str))
            self.metrics["messages_sent"] += 1

            # Update connection activity
            connection = self._find_connection_by_websocket(websocket)
            if connection:
                connection.last_activity = datetime.utcnow()
                connection.message_count += 1

            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def broadcast_to_player(self, player_id: str, payload: dict[str, Any]) -> int:
        """
        Broadcast message to all connections for a specific player.

        Args:
            player_id: Target player ID
            payload: Message payload

        Returns:
            Number of connections that received the message
        """
        sent_count = 0
        if player_id in self.active_connections:
            for connection in list(self.active_connections[player_id]):
                if await self.send_json(connection.websocket, payload):
                    sent_count += 1
                else:
                    # Remove failed connection
                    await self._remove_failed_connection(connection)

        return sent_count

    async def broadcast_to_session(
        self, session_id: str, payload: dict[str, Any]
    ) -> int:
        """
        Broadcast message to all connections in a gameplay session.

        Args:
            session_id: Target session ID
            payload: Message payload

        Returns:
            Number of connections that received the message
        """
        sent_count = 0
        if session_id in self.session_connections:
            for connection_id in list(self.session_connections[session_id]):
                connection = self.connection_registry.get(connection_id)
                if connection and connection.is_active:
                    if await self.send_json(connection.websocket, payload):
                        sent_count += 1
                    else:
                        # Remove failed connection
                        await self._remove_failed_connection(connection)

        return sent_count

    async def associate_session(
        self, connection_id: str, session_id: str, session_state: SessionState
    ) -> bool:
        """
        Associate a connection with a gameplay session.

        Args:
            connection_id: Connection identifier
            session_id: Session identifier
            session_state: Current session state

        Returns:
            True if association was successful
        """
        connection = self.connection_registry.get(connection_id)
        if not connection:
            logger.error(f"Connection {connection_id} not found")
            return False

        # Update connection with session info
        connection.current_session_id = session_id
        connection.session_state = session_state

        # Add to session connections
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(connection_id)

        # Update metrics
        self.metrics["sessions_managed"] = len(self.session_connections)

        logger.info(f"Associated connection {connection_id} with session {session_id}")
        return True

    async def dissociate_session(self, connection_id: str) -> bool:
        """
        Remove session association from a connection.

        Args:
            connection_id: Connection identifier

        Returns:
            True if dissociation was successful
        """
        connection = self.connection_registry.get(connection_id)
        if not connection or not connection.current_session_id:
            return False

        session_id = connection.current_session_id

        # Remove from session connections
        if session_id in self.session_connections:
            self.session_connections[session_id].discard(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]

        # Clear connection session info
        connection.current_session_id = None
        connection.session_state = None

        # Update metrics
        self.metrics["sessions_managed"] = len(self.session_connections)

        logger.info(f"Dissociated connection {connection_id} from session {session_id}")
        return True

    async def update_therapeutic_flags(
        self, connection_id: str, flags: dict[str, Any]
    ) -> bool:
        """
        Update therapeutic monitoring flags for a connection.

        Args:
            connection_id: Connection identifier
            flags: Therapeutic flags to update

        Returns:
            True if update was successful
        """
        connection = self.connection_registry.get(connection_id)
        if not connection:
            return False

        connection.therapeutic_flags.update(flags)

        # Check for therapeutic interventions needed
        if flags.get("crisis_detected") or flags.get("safety_concern"):
            self.metrics["therapeutic_interventions"] += 1

            # Notify gameplay controller if available
            if self.gameplay_controller and connection.current_session_id:
                await self._notify_therapeutic_concern(
                    connection.current_session_id, flags
                )

        return True

    def get_connection_info(self, connection_id: str) -> dict[str, Any] | None:
        """
        Get information about a specific connection.

        Args:
            connection_id: Connection identifier

        Returns:
            Connection information or None if not found
        """
        connection = self.connection_registry.get(connection_id)
        if not connection:
            return None

        return {
            "connection_id": connection.connection_id,
            "player_id": connection.player_id,
            "connected_at": connection.connected_at.isoformat(),
            "last_activity": connection.last_activity.isoformat(),
            "current_session_id": connection.current_session_id,
            "is_active": connection.is_active,
            "message_count": connection.message_count,
            "therapeutic_flags": connection.therapeutic_flags,
            "session_state": (
                connection.session_state.state_type.value
                if connection.session_state
                else None
            ),
        }

    def get_player_connections(self, player_id: str) -> list[dict[str, Any]]:
        """
        Get all connections for a specific player.

        Args:
            player_id: Player identifier

        Returns:
            List of connection information
        """
        connections = []
        if player_id in self.active_connections:
            for connection in self.active_connections[player_id]:
                info = self.get_connection_info(connection.connection_id)
                if info:
                    connections.append(info)

        return connections

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the gameplay chat manager."""
        return {
            **self.metrics,
            "active_players": len(self.active_connections),
            "active_sessions": len(self.session_connections),
            "total_active_connections": len(self.connection_registry),
        }

    def _find_connection_by_websocket(
        self, websocket: WebSocket
    ) -> GameplayConnection | None:
        """Find connection by WebSocket instance."""
        for connection in self.connection_registry.values():
            if connection.websocket == websocket:
                return connection
        return None

    async def _remove_failed_connection(self, connection: GameplayConnection) -> None:
        """Remove a failed connection from all tracking structures."""
        try:
            # Mark as inactive
            connection.is_active = False

            # Remove from active connections
            if connection.player_id in self.active_connections:
                self.active_connections[connection.player_id].discard(connection)
                if not self.active_connections[connection.player_id]:
                    del self.active_connections[connection.player_id]

            # Remove from registry
            if connection.connection_id in self.connection_registry:
                del self.connection_registry[connection.connection_id]

            # Remove from session connections
            if connection.current_session_id:
                session_id = connection.current_session_id
                if session_id in self.session_connections:
                    self.session_connections[session_id].discard(
                        connection.connection_id
                    )
                    if not self.session_connections[session_id]:
                        del self.session_connections[session_id]

            # Update metrics
            self.metrics["active_connections"] = len(self.connection_registry)
            self.metrics["sessions_managed"] = len(self.session_connections)

            logger.info(f"Removed failed connection {connection.connection_id}")

        except Exception as e:
            logger.error(f"Error removing failed connection: {e}")

    async def _notify_therapeutic_concern(
        self, session_id: str, flags: dict[str, Any]
    ) -> None:
        """Notify gameplay controller of therapeutic concerns."""
        try:
            if self.gameplay_controller:
                # This would integrate with the GameplayLoopController's therapeutic monitoring
                logger.info(
                    f"Therapeutic concern detected in session {session_id}: {flags}"
                )
                # Additional therapeutic intervention logic would go here
        except Exception as e:
            logger.error(f"Error notifying therapeutic concern: {e}")

    async def _cleanup_loop(self) -> None:
        """Background task to clean up inactive connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute

                current_time = datetime.utcnow()
                connections_to_remove = []

                # Find inactive connections
                for connection in self.connection_registry.values():
                    if (
                        current_time - connection.last_activity
                    ) > self.connection_timeout:
                        connections_to_remove.append(connection)

                # Remove inactive connections
                for connection in connections_to_remove:
                    logger.info(
                        f"Cleaning up inactive connection {connection.connection_id}"
                    )
                    await self._remove_failed_connection(connection)

                    # Try to close the WebSocket
                    try:
                        if connection.websocket.client_state.name != "DISCONNECTED":
                            await connection.websocket.close(
                                code=1000, reason="Inactive connection cleanup"
                            )
                    except Exception as e:
                        logger.debug(f"Error closing inactive WebSocket: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _heartbeat_loop(self) -> None:
        """Background task to send heartbeat messages to active connections."""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval.total_seconds())

                heartbeat_payload = {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                    "server_time": datetime.utcnow().timestamp(),
                }

                # Send heartbeat to all active connections
                for connection in list(self.connection_registry.values()):
                    if connection.is_active:
                        success = await self.send_json(
                            connection.websocket, heartbeat_payload
                        )
                        if not success:
                            await self._remove_failed_connection(connection)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")

    async def shutdown(self) -> None:
        """Gracefully shutdown the gameplay chat manager."""
        logger.info("Shutting down GameplayChatManager")

        # Stop background tasks
        await self.stop_background_tasks()

        # Close all active connections
        for connection in list(self.connection_registry.values()):
            try:
                if connection.websocket.client_state.name != "DISCONNECTED":
                    await connection.websocket.close(
                        code=1001, reason="Server shutdown"
                    )
            except Exception as e:
                logger.debug(f"Error closing connection during shutdown: {e}")

        # Clear all tracking structures
        self.active_connections.clear()
        self.connection_registry.clear()
        self.session_connections.clear()

        logger.info("GameplayChatManager shutdown complete")
