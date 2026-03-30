"""

# Logseq: [[TTA.dev/Agent_orchestration/Realtime/Websocket_manager]]
WebSocket connection manager for real-time agent orchestration communication.

This module provides WebSocket connection lifecycle management, authentication,
heartbeat monitoring, and event broadcasting capabilities.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from typing import Any
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from .models import (
    ConnectionStatusEvent,
    EventFilter,
    EventSubscription,
    EventType,
    HeartbeatEvent,
    WebSocketEvent,
    create_error_event,
)

logger = logging.getLogger(__name__)


class WebSocketConnection:
    """Represents a single WebSocket connection with metadata."""

    def __init__(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: str | None = None,
        client_info: dict[str, Any] | None = None,
    ):
        self.websocket = websocket
        self.connection_id = connection_id
        self.user_id = user_id
        self.client_info = client_info or {}
        self.connected_at = time.time()
        self.last_heartbeat = time.time()
        self.last_pong = time.time()
        self.ping_count = 0
        self.pong_count = 0
        self.missed_pongs = 0
        self.subscriptions: set[EventType] = set()
        self.filters: EventFilter = EventFilter()
        self.is_authenticated = False
        self.agent_subscriptions: set[str] = set()

    def to_dict(self) -> dict[str, Any]:
        """Convert connection to dictionary representation."""
        return {
            "connection_id": self.connection_id,
            "user_id": self.user_id,
            "client_info": self.client_info,
            "connected_at": self.connected_at,
            "last_heartbeat": self.last_heartbeat,
            "last_pong": self.last_pong,
            "ping_count": self.ping_count,
            "pong_count": self.pong_count,
            "missed_pongs": self.missed_pongs,
            "subscriptions": list(self.subscriptions),
            "is_authenticated": self.is_authenticated,
            "uptime": time.time() - self.connected_at,
            "health_status": self._get_health_status(),
        }

    def _get_health_status(self) -> str:
        """Get connection health status based on heartbeat and pong responses."""
        current_time = time.time()

        # Check if connection is stale
        if current_time - self.last_heartbeat > 120:  # 2 minutes
            return "stale"

        # Check missed pongs
        if self.missed_pongs > 3:
            return "unhealthy"
        if self.missed_pongs > 1:
            return "degraded"

        # Check recent activity
        if current_time - self.last_pong > 60:  # 1 minute
            return "inactive"

        return "healthy"


class WebSocketConnectionManager:
    """Manages WebSocket connections for real-time communication."""

    def __init__(
        self,
        config: dict[str, Any],
        agent_registry: Any | None = None,
        redis_client: Redis | None = None,
    ):
        self.config = config
        self.agent_registry = agent_registry
        self.redis_client = redis_client

        # Connection management
        self.connections: dict[str, WebSocketConnection] = {}
        self.user_connections: dict[str, set[str]] = {}  # user_id -> connection_ids

        # Configuration
        self.heartbeat_interval = float(
            config.get(
                "agent_orchestration.realtime.websocket.heartbeat_interval", 30.0
            )
        )
        self.connection_timeout = float(
            config.get(
                "agent_orchestration.realtime.websocket.connection_timeout", 60.0
            )
        )
        self.max_connections = int(
            config.get("agent_orchestration.realtime.websocket.max_connections", 1000)
        )
        self.auth_required = bool(
            config.get("agent_orchestration.realtime.websocket.auth_required", True)
        )

        # Background tasks
        self._heartbeat_task: asyncio.Task | None = None
        self._cleanup_task: asyncio.Task | None = None
        self._recovery_task: asyncio.Task | None = None

        # Event subscription
        self._event_subscriber: Any | None = None
        self._event_subscription_enabled = bool(
            config.get("agent_orchestration.realtime.events.enabled", False)
        )

        # User-specific event filtering
        self.user_event_filters: dict[str, dict[str, Any]] = {}  # user_id -> filters
        self.user_subscriptions: dict[str, set[str]] = {}  # user_id -> event_types

        # Connection recovery
        self.connection_history: dict[
            str, dict[str, Any]
        ] = {}  # user_id -> connection_info
        self.recovery_enabled = bool(
            config.get("agent_orchestration.realtime.recovery.enabled", True)
        )
        self.recovery_timeout = float(
            config.get("agent_orchestration.realtime.recovery.timeout", 300.0)
        )  # 5 minutes

        # Background tasks will be started when first connection is handled
        # to ensure we have an active event loop

        # Initialize event subscriber if enabled
        if self._event_subscription_enabled and self.redis_client:
            self._initialize_event_subscriber()

    def _start_background_tasks(self) -> None:
        """Start background tasks for heartbeat and cleanup."""
        try:
            # Only start tasks if we have an active event loop
            asyncio.get_running_loop()

            if self._heartbeat_task is None or self._heartbeat_task.done():
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            if self._cleanup_task is None or self._cleanup_task.done():
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())

            if self.recovery_enabled and (
                self._recovery_task is None or self._recovery_task.done()
            ):
                self._recovery_task = asyncio.create_task(self._recovery_loop())

        except RuntimeError:
            # No event loop running, tasks will be started when needed
            pass

    async def handle_connection(self, websocket: WebSocket) -> None:
        """Handle a new WebSocket connection."""
        # Check connection limits
        if len(self.connections) >= self.max_connections:
            await websocket.close(code=1008, reason="connection limit exceeded")
            return

        # Generate connection ID
        connection_id = uuid4().hex

        # Accept the connection
        await websocket.accept()

        # Create connection object
        connection = WebSocketConnection(
            websocket=websocket,
            connection_id=connection_id,
            client_info=self._extract_client_info(websocket),
        )

        # Add to connections
        self.connections[connection_id] = connection

        # Start background tasks if not already running
        self._start_background_tasks()

        # Start event subscription if not already started
        if self._event_subscriber and not self._event_subscriber.is_running:
            asyncio.create_task(self._start_event_subscription())

        logger.info(f"WebSocket connection established: {connection_id}")

        try:
            # Send connection status event
            await self._send_to_connection(
                connection,
                ConnectionStatusEvent(
                    connection_id=connection_id,
                    status="connected",
                    client_info=connection.client_info,
                    source="websocket_manager",
                ),
            )

            # Handle authentication if required
            if self.auth_required:
                if not await self._authenticate_connection(connection):
                    await websocket.close(code=1008, reason="authentication failed")
                    return
            else:
                connection.is_authenticated = True

            # Handle messages
            await self._handle_messages(connection)

        except WebSocketDisconnect:
            logger.info(f"WebSocket connection disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            # Clean up connection
            await self._remove_connection(connection_id)

    async def _authenticate_connection(self, connection: WebSocketConnection) -> bool:
        """Authenticate a WebSocket connection using JWT tokens."""
        try:
            # First try to extract token from query params or headers (like existing chat WebSocket)
            token = self._extract_token_from_websocket(connection.websocket)

            if token:
                # Direct token authentication (query param or header)
                return await self._authenticate_with_token(connection, token)
            # Wait for authentication message
            auth_timeout = 10.0  # 10 seconds to authenticate
            auth_message = await asyncio.wait_for(
                connection.websocket.receive_text(), timeout=auth_timeout
            )

            # Parse authentication message
            auth_data = json.loads(auth_message)

            if auth_data.get("type") != "auth":
                await self._send_error(
                    connection, "AUTH_REQUIRED", "Authentication required"
                )
                return False

            # Extract token from message
            token = auth_data.get("token")
            if not token:
                await self._send_error(connection, "INVALID_TOKEN", "Token required")
                return False

            return await self._authenticate_with_token(connection, token)

        except TimeoutError:
            await self._send_error(connection, "AUTH_TIMEOUT", "Authentication timeout")
            return False
        except json.JSONDecodeError:
            await self._send_error(
                connection, "INVALID_JSON", "Invalid JSON in authentication message"
            )
            return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            await self._send_error(connection, "AUTH_ERROR", "Authentication error")
            return False

    def _extract_token_from_websocket(self, websocket: WebSocket) -> str | None:
        """Extract JWT token from WebSocket query params or headers."""
        # Try query parameter first (same as existing chat WebSocket)
        token = websocket.query_params.get("token")
        if token:
            return token

        # Fallback to Authorization header if present
        auth_header = websocket.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            return auth_header.split(" ", 1)[1]

        return None

    async def _authenticate_with_token(
        self, connection: WebSocketConnection, token: str
    ) -> bool:
        """Authenticate connection with JWT token using existing auth system."""
        # Define fallback AuthenticationError in case the import fails
        _AuthenticationError: type[Exception] = Exception
        try:
            # Import the existing JWT verification function
            from src.player_experience.api.auth import (  # type: ignore[assignment]
                AuthenticationError as _AuthenticationError,
            )
            from src.player_experience.api.auth import (
                verify_token,
            )

            # Verify the token using existing auth system
            token_data = verify_token(token)

            # Set connection user info
            connection.user_id = token_data.player_id or "anonymous"
            connection.is_authenticated = True

            # Store additional token data in client_info
            connection.client_info.update(
                {
                    "username": token_data.username,
                    "email": token_data.email,
                    "token_exp": token_data.exp.isoformat() if token_data.exp else None,
                }
            )

            # Add to user connections
            if connection.user_id:
                if connection.user_id not in self.user_connections:
                    self.user_connections[connection.user_id] = set()
                self.user_connections[connection.user_id].add(connection.connection_id)

            # Send authentication success
            await self._send_to_connection(
                connection,
                WebSocketEvent(
                    event_type=EventType.CONNECTION_STATUS,
                    source="websocket_manager",
                    data={
                        "status": "authenticated",
                        "user_id": connection.user_id,
                        "username": token_data.username,
                    },
                ),
            )

            # Attempt connection recovery
            recovered = False
            if self.recovery_enabled and connection.user_id:
                recovered = await self._recover_connection(connection)

            # Store connection info for future recovery
            if self.recovery_enabled and connection.user_id:
                self._store_connection_info(connection)

            if not recovered:
                logger.info(
                    f"WebSocket connection authenticated: {connection.connection_id} (user: {connection.user_id})"
                )

            return True

        except _AuthenticationError as e:
            await self._send_error(
                connection, "INVALID_TOKEN", f"Token verification failed: {str(e)}"
            )
            return False
        except ImportError:
            # Fallback if auth module is not available
            logger.warning(
                "Player experience auth module not available, using basic authentication"
            )
            connection.user_id = "anonymous"
            connection.is_authenticated = True
            return True
        except Exception as e:
            logger.error(f"Token authentication error: {e}")
            await self._send_error(
                connection, "AUTH_ERROR", "Token authentication error"
            )
            return False

    async def _handle_messages(self, connection: WebSocketConnection) -> None:
        """Handle incoming WebSocket messages."""
        while True:
            try:
                # Receive message
                message = await connection.websocket.receive_text()
                data = json.loads(message)

                # Update last heartbeat
                connection.last_heartbeat = time.time()

                # Handle different message types
                message_type = data.get("type")

                if message_type == "subscribe":
                    await self._handle_subscription(connection, data)
                elif message_type == "unsubscribe":
                    await self._handle_unsubscription(connection, data)
                elif message_type == "subscribe_agent":
                    await self._handle_agent_subscription(connection, data)
                elif message_type == "unsubscribe_agent":
                    await self._handle_agent_unsubscription(connection, data)
                elif message_type == "update_filters":
                    await self._handle_filter_update(connection, data)
                elif message_type == "ping":
                    await self._handle_ping(connection, data)
                elif message_type == "pong":
                    await self._handle_pong(connection, data)
                else:
                    await self._send_error(
                        connection,
                        "UNKNOWN_MESSAGE_TYPE",
                        f"Unknown message type: {message_type}",
                    )

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await self._send_error(
                    connection, "INVALID_JSON", "Invalid JSON message"
                )
            except Exception as e:
                logger.error(f"Message handling error: {e}")
                await self._send_error(
                    connection, "MESSAGE_ERROR", "Error handling message"
                )

    async def _handle_subscription(
        self, connection: WebSocketConnection, data: dict[str, Any]
    ) -> None:
        """Handle event subscription request with authorization checks."""
        try:
            subscription = EventSubscription(**data.get("subscription", {}))

            # Check authorization for requested event types
            authorized_event_types = []
            unauthorized_event_types = []

            for event_type in subscription.event_types:
                if self._is_authorized_for_event_type(connection, event_type):
                    authorized_event_types.append(event_type)
                    connection.subscriptions.add(event_type)
                else:
                    unauthorized_event_types.append(event_type)

            # Update filters (with authorization checks)
            if subscription.filters:
                authorized_filters = self._filter_authorized_filters(
                    connection, subscription.filters
                )
                connection.filters = EventFilter(**authorized_filters)

            # Send confirmation with authorization results
            response_data = {
                "status": "subscribed",
                "authorized_event_types": [et.value for et in authorized_event_types],
                "filters": subscription.filters,
            }

            if unauthorized_event_types:
                response_data["unauthorized_event_types"] = [
                    et.value for et in unauthorized_event_types
                ]
                response_data["warning"] = (
                    "Some event types were not authorized for your user level"
                )

            await self._send_to_connection(
                connection,
                WebSocketEvent(
                    event_type=EventType.CONNECTION_STATUS,
                    source="websocket_manager",
                    data=response_data,
                ),
            )

        except Exception as e:
            logger.error(f"Subscription error: {e}")
            await self._send_error(
                connection, "SUBSCRIPTION_ERROR", "Error processing subscription"
            )

    def _is_authorized_for_event_type(
        self, connection: WebSocketConnection, event_type: EventType
    ) -> bool:
        """Check if connection is authorized for a specific event type."""
        # Basic authorization rules - can be extended based on user roles/permissions

        # All authenticated users can subscribe to basic events
        basic_events = {
            EventType.CONNECTION_STATUS,
            EventType.HEARTBEAT,
            EventType.ERROR,
        }

        if event_type in basic_events:
            return connection.is_authenticated

        # Agent status and workflow progress require authentication
        user_events = {
            EventType.AGENT_STATUS,
            EventType.WORKFLOW_PROGRESS,
            EventType.PROGRESSIVE_FEEDBACK,
        }

        if event_type in user_events:
            return connection.is_authenticated

        # System metrics and optimization events require admin privileges
        # For now, allow all authenticated users - can be restricted later
        admin_events = {
            EventType.SYSTEM_METRICS,
            EventType.OPTIMIZATION,
        }

        if event_type in admin_events:
            # Note: Admin role checking can be implemented when role-based auth is added
            # For now, all authenticated users can access system events
            return connection.is_authenticated

        # Default: deny unknown event types
        return False

    def _filter_authorized_filters(
        self, connection: WebSocketConnection, filters: dict[str, Any]
    ) -> dict[str, Any]:
        """Filter subscription filters based on user authorization."""
        authorized_filters = filters.copy()

        # Users can only filter by their own user_id unless they have admin privileges
        if "user_ids" in authorized_filters:
            user_ids = authorized_filters["user_ids"]
            if isinstance(user_ids, list) and connection.user_id:
                # Non-admin users can only filter by their own user_id
                # Note: Admin role checking can be implemented when role-based auth is added
                if connection.user_id not in user_ids:
                    # If user tries to filter by other user IDs, restrict to their own
                    authorized_filters["user_ids"] = [connection.user_id]

        return authorized_filters

    async def _handle_unsubscription(
        self, connection: WebSocketConnection, data: dict[str, Any]
    ) -> None:
        """Handle event unsubscription request."""
        try:
            event_types = data.get("event_types", [])

            for event_type_str in event_types:
                with contextlib.suppress(ValueError):
                    event_type = EventType(event_type_str)
                    connection.subscriptions.discard(event_type)

            # Send confirmation
            await self._send_to_connection(
                connection,
                WebSocketEvent(
                    event_type=EventType.CONNECTION_STATUS,
                    source="websocket_manager",
                    data={"status": "unsubscribed", "event_types": event_types},
                ),
            )

        except Exception as e:
            logger.error(f"Unsubscription error: {e}")
            await self._send_error(
                connection, "UNSUBSCRIPTION_ERROR", "Error processing unsubscription"
            )

    async def _handle_ping(
        self, connection: WebSocketConnection, data: dict[str, Any]
    ) -> None:
        """Handle ping message and respond with pong."""
        # Send pong response
        pong_event = WebSocketEvent(
            event_type=EventType.HEARTBEAT,
            source="websocket_manager",
            data={
                "type": "pong",
                "connection_id": connection.connection_id,
                "timestamp": time.time(),
                "ping_id": data.get("ping_id"),  # Echo back ping ID if provided
            },
        )
        await self._send_to_connection(connection, pong_event)

    async def _handle_pong(
        self, connection: WebSocketConnection, data: dict[str, Any]
    ) -> None:
        """Handle pong response from client."""
        connection.last_pong = time.time()
        connection.pong_count += 1

        # Reset missed pongs counter
        if connection.missed_pongs > 0:
            logger.info(
                f"Connection {connection.connection_id} recovered, missed pongs reset"
            )
        connection.missed_pongs = 0

        logger.debug(f"Received pong from connection {connection.connection_id}")

    async def _handle_agent_subscription(
        self, connection: WebSocketConnection, data: dict[str, Any]
    ) -> None:
        """Handle agent-specific subscription request."""
        try:
            agent_id = data.get("agent_id")
            if not agent_id:
                await self._send_error(
                    connection,
                    "MISSING_AGENT_ID",
                    "Agent ID required for agent subscription",
                )
                return

            success = await self.subscribe_connection_to_agent(
                connection.connection_id, agent_id
            )

            if success:
                await self._send_to_connection(
                    connection,
                    WebSocketEvent(
                        event_type=EventType.CONNECTION_STATUS,
                        source="websocket_manager",
                        data={"status": "agent_subscribed", "agent_id": agent_id},
                    ),
                )
            else:
                await self._send_error(
                    connection,
                    "AGENT_SUBSCRIPTION_FAILED",
                    f"Failed to subscribe to agent {agent_id}",
                )

        except Exception as e:
            logger.error(f"Agent subscription error: {e}")
            await self._send_error(
                connection,
                "AGENT_SUBSCRIPTION_ERROR",
                "Error processing agent subscription",
            )

    async def _handle_agent_unsubscription(
        self, connection: WebSocketConnection, data: dict[str, Any]
    ) -> None:
        """Handle agent-specific unsubscription request."""
        try:
            agent_id = data.get("agent_id")
            if not agent_id:
                await self._send_error(
                    connection,
                    "MISSING_AGENT_ID",
                    "Agent ID required for agent unsubscription",
                )
                return

            success = await self.unsubscribe_connection_from_agent(
                connection.connection_id, agent_id
            )

            await self._send_to_connection(
                connection,
                WebSocketEvent(
                    event_type=EventType.CONNECTION_STATUS,
                    source="websocket_manager",
                    data={
                        "status": "agent_unsubscribed",
                        "agent_id": agent_id,
                        "success": success,
                    },
                ),
            )

        except Exception as e:
            logger.error(f"Agent unsubscription error: {e}")
            await self._send_error(
                connection,
                "AGENT_UNSUBSCRIPTION_ERROR",
                "Error processing agent unsubscription",
            )

    async def _handle_filter_update(
        self, connection: WebSocketConnection, data: dict[str, Any]
    ) -> None:
        """Handle filter update request."""
        try:
            new_filters = data.get("filters", {})

            # Validate and apply authorized filters
            authorized_filters = self._filter_authorized_filters(
                connection, new_filters
            )

            # Update connection filters
            try:
                from .models import EventFilter

                connection.filters = EventFilter(**authorized_filters)

                await self._send_to_connection(
                    connection,
                    WebSocketEvent(
                        event_type=EventType.CONNECTION_STATUS,
                        source="websocket_manager",
                        data={
                            "status": "filters_updated",
                            "filters": authorized_filters,
                        },
                    ),
                )

            except Exception as e:
                await self._send_error(
                    connection, "INVALID_FILTERS", f"Invalid filter format: {str(e)}"
                )

        except Exception as e:
            logger.error(f"Filter update error: {e}")
            await self._send_error(
                connection, "FILTER_UPDATE_ERROR", "Error processing filter update"
            )

    async def _send_to_connection(
        self, connection: WebSocketConnection, event: WebSocketEvent
    ) -> bool:
        """Send an event to a specific connection."""
        try:
            message = event.model_dump_json()
            await connection.websocket.send_text(message)
            return True
        except Exception as e:
            logger.error(f"Error sending to connection {connection.connection_id}: {e}")
            return False

    async def _send_error(
        self, connection: WebSocketConnection, error_code: str, error_message: str
    ) -> None:
        """Send an error event to a connection."""
        error_event = create_error_event(
            error_code=error_code,
            error_message=error_message,
            component="websocket_manager",
            source="websocket_manager",
        )
        await self._send_to_connection(connection, error_event)

    def _extract_client_info(self, websocket: WebSocket) -> dict[str, Any]:
        """Extract client information from WebSocket."""
        return {
            "client_host": (
                getattr(websocket.client, "host", None) if websocket.client else None
            ),
            "client_port": (
                getattr(websocket.client, "port", None) if websocket.client else None
            ),
            "headers": dict(websocket.headers) if hasattr(websocket, "headers") else {},
        }

    async def _remove_connection(self, connection_id: str) -> None:
        """Remove a connection and clean up."""
        if connection_id in self.connections:
            connection = self.connections[connection_id]

            # Remove from user connections
            if connection.user_id and connection.user_id in self.user_connections:
                self.user_connections[connection.user_id].discard(connection_id)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]

            # Remove from connections
            del self.connections[connection_id]

            # Mark connection as disconnected in recovery history
            if self.recovery_enabled and connection.user_id:
                self._mark_connection_disconnected(connection)

            logger.info(f"WebSocket connection removed: {connection_id}")

    def _store_connection_info(self, connection: WebSocketConnection) -> None:
        """Store connection information for recovery purposes."""
        if not connection.user_id:
            return

        self.connection_history[connection.user_id] = {
            "connection_id": connection.connection_id,
            "subscriptions": list(connection.subscriptions),
            "filters": connection.filters.model_dump() if connection.filters else {},
            "last_connected": time.time(),
            "disconnected_at": None,
            "client_info": connection.client_info.copy(),
        }

    def _mark_connection_disconnected(self, connection: WebSocketConnection) -> None:
        """Mark a connection as disconnected for recovery tracking."""
        if not connection.user_id or connection.user_id not in self.connection_history:
            return

        self.connection_history[connection.user_id]["disconnected_at"] = time.time()

    def _can_recover_connection(self, user_id: str) -> bool:
        """Check if a connection can be recovered for a user."""
        if not self.recovery_enabled or user_id not in self.connection_history:
            return False

        history = self.connection_history[user_id]
        disconnected_at = history.get("disconnected_at")

        if not disconnected_at:
            return False

        # Check if within recovery timeout
        return (time.time() - disconnected_at) <= self.recovery_timeout

    async def _recover_connection(self, connection: WebSocketConnection) -> bool:
        """Attempt to recover a previous connection's state."""
        if not connection.user_id or not self._can_recover_connection(
            connection.user_id
        ):
            return False

        try:
            history = self.connection_history[connection.user_id]

            # Restore subscriptions
            if history.get("subscriptions"):
                for event_type_str in history["subscriptions"]:
                    with contextlib.suppress(ValueError):
                        event_type = EventType(event_type_str)
                        connection.subscriptions.add(event_type)

            # Restore filters
            if history.get("filters"):
                with contextlib.suppress(Exception):
                    connection.filters = EventFilter(**history["filters"])

            # Update connection history
            history["connection_id"] = connection.connection_id
            history["last_connected"] = time.time()
            history["disconnected_at"] = None

            # Send recovery notification
            await self._send_to_connection(
                connection,
                WebSocketEvent(
                    event_type=EventType.CONNECTION_STATUS,
                    source="websocket_manager",
                    data={
                        "status": "recovered",
                        "recovered_subscriptions": list(connection.subscriptions),
                        "recovered_filters": history.get("filters", {}),
                        "recovery_time": time.time(),
                    },
                ),
            )

            logger.info(f"Connection recovered for user {connection.user_id}")
            return True

        except Exception as e:
            logger.error(
                f"Error recovering connection for user {connection.user_id}: {e}"
            )
            return False

    async def _heartbeat_loop(self) -> None:
        """Background task for sending heartbeats and pings."""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                current_time = time.time()

                # Send ping to all connections and track responses
                for connection in list(self.connections.values()):
                    try:
                        # Check if we should send a ping
                        time_since_last_pong = current_time - connection.last_pong

                        if time_since_last_pong > self.heartbeat_interval:
                            # Send ping
                            ping_id = f"ping_{connection.ping_count}"
                            ping_event = WebSocketEvent(
                                event_type=EventType.HEARTBEAT,
                                source="websocket_manager",
                                data={
                                    "type": "ping",
                                    "connection_id": connection.connection_id,
                                    "ping_id": ping_id,
                                    "timestamp": current_time,
                                },
                            )

                            if await self._send_to_connection(connection, ping_event):
                                connection.ping_count += 1

                                # Check if previous ping was missed
                                if time_since_last_pong > self.heartbeat_interval * 2:
                                    connection.missed_pongs += 1
                                    logger.warning(
                                        f"Connection {connection.connection_id} missed pong "
                                        f"(missed: {connection.missed_pongs})"
                                    )

                        # Also send periodic heartbeat for compatibility
                        if connection.ping_count % 3 == 0:  # Every 3rd ping cycle
                            await self._send_to_connection(
                                connection,
                                HeartbeatEvent(
                                    connection_id=connection.connection_id,
                                    source="websocket_manager",
                                ),
                            )

                    except Exception as e:
                        logger.debug(
                            f"Error sending heartbeat to {connection.connection_id}: {e}"
                        )
                        # Connection will be cleaned up by cleanup loop

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")

    async def _cleanup_loop(self) -> None:
        """Background task for cleaning up stale connections."""
        while True:
            try:
                await asyncio.sleep(30.0)  # Check every 30 seconds

                current_time = time.time()
                stale_connections = []

                for connection_id, connection in self.connections.items():
                    # Check for stale connections (no heartbeat activity)
                    if (
                        current_time - connection.last_heartbeat
                        > self.connection_timeout
                    ):
                        stale_connections.append(connection_id)
                    # Check for unhealthy connections (too many missed pongs)
                    elif connection.missed_pongs > 5:
                        stale_connections.append(connection_id)
                        logger.warning(
                            f"Removing unhealthy connection {connection_id} (missed {connection.missed_pongs} pongs)"
                        )
                    # Check for inactive connections (no pong responses)
                    elif (
                        current_time - connection.last_pong
                        > self.connection_timeout * 2
                    ):
                        stale_connections.append(connection_id)
                        logger.warning(
                            f"Removing inactive connection {connection_id} (no pong for {current_time - connection.last_pong:.1f}s)"
                        )

                # Remove stale connections
                for connection_id in stale_connections:
                    with contextlib.suppress(Exception):
                        connection = self.connections.get(connection_id)
                        if connection:
                            await connection.websocket.close(
                                code=1001, reason="timeout"
                            )
                    await self._remove_connection(connection_id)

                if stale_connections:
                    logger.info(
                        f"Cleaned up {len(stale_connections)} stale connections"
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    async def _recovery_loop(self) -> None:
        """Background task for cleaning up old recovery history."""
        while True:
            try:
                await asyncio.sleep(300.0)  # Check every 5 minutes

                current_time = time.time()
                expired_users = []

                for user_id, history in self.connection_history.items():
                    disconnected_at = history.get("disconnected_at")
                    if (
                        disconnected_at
                        and (current_time - disconnected_at) > self.recovery_timeout
                    ):
                        expired_users.append(user_id)

                # Remove expired recovery history
                for user_id in expired_users:
                    del self.connection_history[user_id]

                if expired_users:
                    logger.info(
                        f"Cleaned up recovery history for {len(expired_users)} users"
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Recovery loop error: {e}")

    def get_status(self) -> dict[str, Any]:
        """Get WebSocket manager status."""
        return {
            "total_connections": len(self.connections),
            "authenticated_connections": sum(
                1 for c in self.connections.values() if c.is_authenticated
            ),
            "unique_users": len(self.user_connections),
            "configuration": {
                "heartbeat_interval": self.heartbeat_interval,
                "connection_timeout": self.connection_timeout,
                "max_connections": self.max_connections,
                "auth_required": self.auth_required,
            },
            "connections": [conn.to_dict() for conn in self.connections.values()],
            "recovery": {
                "enabled": self.recovery_enabled,
                "timeout": self.recovery_timeout,
                "history_count": len(self.connection_history),
                "recoverable_users": [
                    user_id
                    for user_id in self.connection_history
                    if self._can_recover_connection(user_id)
                ],
            },
        }

    async def broadcast_event(
        self, event: WebSocketEvent, user_filter: set[str] | None = None
    ) -> int:
        """Broadcast an event to subscribed connections with filtering."""
        sent_count = 0

        for connection in list(self.connections.values()):
            # Check if connection should receive this event
            if await self._should_send_event_to_connection(
                connection, event, user_filter
            ) and await self._send_to_connection(connection, event):
                sent_count += 1

        return sent_count

    async def _should_send_event_to_connection(
        self,
        connection: WebSocketConnection,
        event: WebSocketEvent,
        user_filter: set[str] | None = None,
    ) -> bool:
        """Determine if an event should be sent to a specific connection."""
        # Check if connection is authenticated
        if not connection.is_authenticated:
            return False

        # Check user filter
        if user_filter and connection.user_id not in user_filter:
            return False

        # Check if connection is subscribed to this event type
        if event.event_type not in connection.subscriptions:
            return False

        # Apply connection-specific filters
        return self._apply_event_filters(connection, event)

    def _apply_event_filters(
        self, connection: WebSocketConnection, event: WebSocketEvent
    ) -> bool:
        """Apply connection-specific filters to determine if event should be sent."""
        filters = connection.filters

        # Agent type filtering
        if filters.agent_types and hasattr(event, "agent_type"):
            if event.agent_type not in filters.agent_types:  # type: ignore[union-attr]
                return False

        # Workflow type filtering
        if filters.workflow_types and hasattr(event, "workflow_type"):
            if event.workflow_type not in filters.workflow_types:  # type: ignore[union-attr]
                return False

        # User ID filtering
        if filters.user_ids and hasattr(event, "user_id"):
            uid = event.user_id  # type: ignore[union-attr]
            if uid and uid not in filters.user_ids:
                return False

        # Severity level filtering (for error events)
        if filters.severity_levels and hasattr(event, "severity"):
            if event.severity not in filters.severity_levels:  # type: ignore[union-attr]
                return False

        # Progress filtering (for progress events)
        if hasattr(event, "progress_percentage"):
            progress: float = event.progress_percentage  # type: ignore[union-attr]

            if filters.min_progress is not None and progress < filters.min_progress:
                return False

            if filters.max_progress is not None and progress > filters.max_progress:
                return False

        # Agent-specific filtering
        if hasattr(event, "agent_id"):
            # Check if user is authorized to see this agent's events
            if not self._is_authorized_for_agent(connection, event.agent_id):  # type: ignore[union-attr]
                return False

        return True

    def _is_authorized_for_agent(
        self, connection: WebSocketConnection, agent_id: str
    ) -> bool:
        """Check if connection is authorized to receive events for a specific agent."""
        # Basic authorization - all authenticated users can see all agents
        # This can be extended with role-based access control
        return connection.is_authenticated

    async def subscribe_connection_to_agent(
        self, connection_id: str, agent_id: str
    ) -> bool:
        """Subscribe a connection to events for a specific agent."""
        connection = self.connections.get(connection_id)
        if not connection or not connection.is_authenticated:
            return False

        # Add agent-specific subscription
        connection.agent_subscriptions.add(agent_id)

        # Also subscribe to agent status events if not already subscribed
        connection.subscriptions.add(EventType.AGENT_STATUS)

        logger.debug(f"Connection {connection_id} subscribed to agent {agent_id}")
        return True

    async def unsubscribe_connection_from_agent(
        self, connection_id: str, agent_id: str
    ) -> bool:
        """Unsubscribe a connection from events for a specific agent."""
        connection = self.connections.get(connection_id)
        if not connection:
            return False

        connection.agent_subscriptions.discard(agent_id)

        logger.debug(f"Connection {connection_id} unsubscribed from agent {agent_id}")
        return True

    async def subscribe_connection_to_user_events(
        self, connection_id: str, user_id: str
    ) -> bool:
        """Subscribe a connection to events for a specific user."""
        connection = self.connections.get(connection_id)
        if not connection or not connection.is_authenticated:
            return False

        # Users can only subscribe to their own events unless they have admin privileges
        if connection.user_id != user_id:
            # Note: Admin role checking can be implemented when role-based auth is added
            logger.warning(
                f"Connection {connection_id} attempted to subscribe to other user's events"
            )
            return False

        # Update filters to include this user
        if not connection.filters.user_ids:
            connection.filters.user_ids = []

        if user_id not in connection.filters.user_ids:
            connection.filters.user_ids.append(user_id)

        logger.debug(
            f"Connection {connection_id} subscribed to user events for {user_id}"
        )
        return True

    def get_connection_subscriptions(self, connection_id: str) -> dict[str, Any] | None:
        """Get subscription information for a connection."""
        connection = self.connections.get(connection_id)
        if not connection:
            return None

        return {
            "event_types": list(connection.subscriptions),
            "filters": connection.filters.model_dump() if connection.filters else {},
            "agent_subscriptions": list(
                getattr(connection, "agent_subscriptions", set())
            ),
        }

    async def shutdown(self) -> None:
        """Shutdown the WebSocket manager."""
        # Stop event subscription
        await self._stop_event_subscription()

        # Cancel background tasks
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._recovery_task:
            self._recovery_task.cancel()

        # Close all connections
        for connection in list(self.connections.values()):
            with contextlib.suppress(Exception):
                await connection.websocket.close(code=1001, reason="server shutdown")

        # Clear connections
        self.connections.clear()
        self.user_connections.clear()

        logger.info("WebSocket manager shutdown complete")

    def _initialize_event_subscriber(self) -> None:
        """Initialize the event subscriber for Redis events."""
        try:
            from .event_subscriber import EventSubscriber

            channel_prefix = self.config.get(
                "agent_orchestration.realtime.events.redis_channel_prefix", "ao:events"
            )
            assert self.redis_client is not None
            self._event_subscriber = EventSubscriber(
                redis_client=self.redis_client,
                channel_prefix=channel_prefix,
                subscriber_id=f"websocket_manager_{uuid4().hex[:8]}",
            )

            logger.info("Event subscriber initialized for WebSocket manager")

        except Exception as e:
            logger.error(f"Failed to initialize event subscriber: {e}")
            self._event_subscriber = None

    async def _start_event_subscription(self) -> None:
        """Start event subscription and set up handlers."""
        if not self._event_subscriber:
            return

        try:
            # Start the subscriber
            await self._event_subscriber.start()

            # Subscribe to all events to broadcast to WebSocket clients
            await self._event_subscriber.subscribe_to_all_events(
                self._handle_redis_event
            )

            logger.info("Event subscription started for WebSocket manager")

        except Exception as e:
            logger.error(f"Failed to start event subscription: {e}")

    async def _stop_event_subscription(self) -> None:
        """Stop event subscription."""
        if self._event_subscriber and self._event_subscriber.is_running:
            try:
                await self._event_subscriber.stop()
                logger.info("Event subscription stopped for WebSocket manager")
            except Exception as e:
                logger.error(f"Error stopping event subscription: {e}")

    async def _handle_redis_event(self, event: WebSocketEvent) -> None:
        """Handle events received from Redis and broadcast to WebSocket clients."""
        try:
            # Broadcast the event to all connected WebSocket clients
            sent_count = await self.broadcast_event(event)

            if sent_count > 0:
                logger.debug(
                    f"Broadcasted Redis event {event.event_type} to {sent_count} WebSocket clients"
                )

        except Exception as e:
            logger.error(f"Error handling Redis event: {e}")

    async def subscribe_user_to_events(
        self,
        user_id: str,
        event_types: list[str],
        filters: dict[str, Any] | None = None,
    ) -> bool:
        """Subscribe a user to specific event types with optional filters."""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()

        # Add event type subscriptions
        self.user_subscriptions[user_id].update(event_types)

        # Store user-specific filters
        if filters:
            if user_id not in self.user_event_filters:
                self.user_event_filters[user_id] = {}
            self.user_event_filters[user_id].update(filters)

        logger.debug(f"User {user_id} subscribed to events: {event_types}")
        return True

    async def unsubscribe_user_from_events(
        self, user_id: str, event_types: list[str] | None = None
    ) -> bool:
        """Unsubscribe a user from specific event types or all events."""
        if user_id not in self.user_subscriptions:
            return False

        if event_types is None:
            # Unsubscribe from all events
            self.user_subscriptions.pop(user_id, None)
            self.user_event_filters.pop(user_id, None)
        else:
            # Unsubscribe from specific event types
            for event_type in event_types:
                self.user_subscriptions[user_id].discard(event_type)

            # Remove user if no subscriptions left
            if not self.user_subscriptions[user_id]:
                self.user_subscriptions.pop(user_id, None)
                self.user_event_filters.pop(user_id, None)

        logger.debug(f"User {user_id} unsubscribed from events")
        return True

    async def update_user_event_filters(
        self, user_id: str, filters: dict[str, Any]
    ) -> bool:
        """Update event filters for a user."""
        if user_id not in self.user_subscriptions:
            return False

        if user_id not in self.user_event_filters:
            self.user_event_filters[user_id] = {}

        self.user_event_filters[user_id].update(filters)
        logger.debug(f"Updated event filters for user {user_id}")
        return True

    async def get_user_subscriptions(self, user_id: str) -> dict[str, Any]:
        """Get subscription information for a user."""
        return {
            "event_types": list(self.user_subscriptions.get(user_id, set())),
            "filters": self.user_event_filters.get(user_id, {}),
            "active_connections": len(
                [conn for conn in self.connections.values() if conn.user_id == user_id]
            ),
        }
