"""
WebSocket proxy for the API Gateway.

This module provides WebSocket proxying functionality to backend services
with message routing, authentication integration, and therapeutic safety features.
"""

import asyncio
import json
import logging
import time
from collections.abc import Callable
from typing import Any
from uuid import uuid4

import aiohttp
from fastapi import WebSocket, WebSocketDisconnect

from ..core.service_router import ServiceRouter
from ..models import AuthContext, ServiceInfo
from ..services import ServiceDiscoveryManager
from .connection_manager import (
    ConnectionType,
    WebSocketConnection,
    WebSocketConnectionManager,
)

logger = logging.getLogger(__name__)


class WebSocketProxy:
    """
    WebSocket proxy for routing messages between clients and backend services.

    Provides intelligent message routing, service discovery integration,
    authentication handling, and therapeutic safety features.
    """

    def __init__(
        self,
        connection_manager: WebSocketConnectionManager,
        service_router: ServiceRouter,
        discovery_manager: ServiceDiscoveryManager,
    ):
        """
        Initialize WebSocket proxy.

        Args:
            connection_manager: WebSocket connection manager
            service_router: Service router for backend selection
            discovery_manager: Service discovery manager
        """
        self.connection_manager = connection_manager
        self.service_router = service_router
        self.discovery_manager = discovery_manager

        # Backend WebSocket connections
        self.backend_connections: dict[str, aiohttp.ClientWebSocketResponse] = {}
        self.connection_to_backend: dict[str, str] = {}  # connection_id -> backend_key
        self.backend_to_connections: dict[str, list[str]] = (
            {}
        )  # backend_key -> connection_ids

        # Message handlers
        self.message_handlers: dict[str, Callable] = {
            "ping": self._handle_ping,
            "authenticate": self._handle_authenticate,
            "join_session": self._handle_join_session,
            "leave_session": self._handle_leave_session,
            "therapeutic_event": self._handle_therapeutic_event,
            "crisis_alert": self._handle_crisis_alert,
        }

    async def handle_connection(
        self,
        websocket: WebSocket,
        connection_type: ConnectionType,
        service_name: str,
        auth_context: AuthContext | None = None,
        therapeutic_session_id: str | None = None,
    ) -> None:
        """
        Handle a new WebSocket connection with proxying to backend service.

        Args:
            websocket: Client WebSocket connection
            connection_type: Type of connection
            service_name: Target backend service name
            auth_context: Authentication context
            therapeutic_session_id: Therapeutic session ID if applicable
        """
        connection_id = None
        backend_key = None

        try:
            # Get target service
            target_service = await self._select_backend_service(
                service_name, auth_context
            )
            if not target_service:
                await websocket.close(code=1011, reason="Service unavailable")
                return

            # Register client connection
            connection_id = await self.connection_manager.connect(
                websocket=websocket,
                connection_type=connection_type,
                auth_context=auth_context,
                therapeutic_session_id=therapeutic_session_id,
                target_service=target_service,
            )

            # Establish backend connection
            backend_key = await self._connect_to_backend(
                target_service, connection_id, auth_context
            )
            if not backend_key:
                await self.connection_manager.disconnect(
                    connection_id, "backend_unavailable"
                )
                return

            # Start message routing
            await self._start_message_routing(connection_id, backend_key)

        except WebSocketDisconnect:
            logger.info(f"Client WebSocket disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"Error handling WebSocket connection: {e}")
        finally:
            # Cleanup
            if connection_id:
                await self.connection_manager.disconnect(
                    connection_id, "connection_ended"
                )
            if backend_key:
                await self._disconnect_from_backend(backend_key, connection_id)

    async def _select_backend_service(
        self, service_name: str, auth_context: AuthContext | None
    ) -> ServiceInfo | None:
        """Select backend service using service router."""
        try:
            # Create a mock gateway request for service selection
            from ..models import GatewayRequest, RequestMethod

            gateway_request = GatewayRequest(
                correlation_id=str(uuid4()),
                method=RequestMethod.GET,
                path=f"/ws/{service_name}",
                client_ip="websocket",
                is_therapeutic=(
                    auth_context.is_therapeutic_context() if auth_context else False
                ),
                crisis_mode=auth_context.crisis_mode if auth_context else False,
                auth_context=(
                    {
                        "user_id": (
                            str(auth_context.user_id)
                            if auth_context and auth_context.user_id
                            else None
                        ),
                        "username": auth_context.username if auth_context else None,
                        "role": (
                            auth_context.permissions.role.value
                            if auth_context
                            else None
                        ),
                        "therapeutic_context": (
                            auth_context.is_therapeutic_context()
                            if auth_context
                            else False
                        ),
                        "crisis_mode": (
                            auth_context.crisis_mode if auth_context else False
                        ),
                    }
                    if auth_context
                    else None
                ),
            )

            return await self.service_router.select_service(
                service_name, gateway_request
            )

        except Exception as e:
            logger.error(f"Error selecting backend service {service_name}: {e}")
            return None

    async def _connect_to_backend(
        self,
        target_service: ServiceInfo,
        connection_id: str,
        auth_context: AuthContext | None,
    ) -> str | None:
        """
        Establish WebSocket connection to backend service.

        Args:
            target_service: Target service information
            connection_id: Client connection ID
            auth_context: Authentication context

        Returns:
            Backend connection key or None if failed
        """
        try:
            # Build backend WebSocket URL
            backend_url = (
                f"ws://{target_service.endpoint.host}:{target_service.endpoint.port}/ws"
            )

            # Prepare headers
            headers = {}
            if auth_context:
                headers.update(
                    {
                        "X-User-ID": (
                            str(auth_context.user_id) if auth_context.user_id else ""
                        ),
                        "X-Username": auth_context.username or "",
                        "X-User-Role": (
                            auth_context.permissions.role.value
                            if auth_context.permissions
                            else ""
                        ),
                        "X-Therapeutic-Context": str(
                            auth_context.is_therapeutic_context()
                        ),
                        "X-Crisis-Mode": str(auth_context.crisis_mode),
                        "X-Gateway-Connection-ID": connection_id,
                    }
                )

            # Create HTTP session
            session = aiohttp.ClientSession()

            # Connect to backend
            backend_ws = await session.ws_connect(
                backend_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            )

            # Generate backend key
            backend_key = f"{target_service.name}:{target_service.endpoint.host}:{target_service.endpoint.port}:{connection_id}"

            # Store connections
            self.backend_connections[backend_key] = backend_ws
            self.connection_to_backend[connection_id] = backend_key

            if backend_key not in self.backend_to_connections:
                self.backend_to_connections[backend_key] = []
            self.backend_to_connections[backend_key].append(connection_id)

            logger.info(f"Connected to backend service: {backend_key}")
            return backend_key

        except Exception as e:
            logger.error(
                f"Failed to connect to backend service {target_service.name}: {e}"
            )
            return None

    async def _disconnect_from_backend(
        self, backend_key: str, connection_id: str
    ) -> None:
        """Disconnect from backend service."""
        try:
            # Remove connection mapping
            if connection_id in self.connection_to_backend:
                del self.connection_to_backend[connection_id]

            if backend_key in self.backend_to_connections:
                if connection_id in self.backend_to_connections[backend_key]:
                    self.backend_to_connections[backend_key].remove(connection_id)

                # If no more connections, close backend WebSocket
                if not self.backend_to_connections[backend_key]:
                    if backend_key in self.backend_connections:
                        backend_ws = self.backend_connections[backend_key]
                        if not backend_ws.closed:
                            await backend_ws.close()
                        del self.backend_connections[backend_key]
                    del self.backend_to_connections[backend_key]

            logger.info(f"Disconnected from backend service: {backend_key}")

        except Exception as e:
            logger.error(f"Error disconnecting from backend {backend_key}: {e}")

    async def _start_message_routing(
        self, connection_id: str, backend_key: str
    ) -> None:
        """
        Start bidirectional message routing between client and backend.

        Args:
            connection_id: Client connection ID
            backend_key: Backend connection key
        """
        connection = self.connection_manager.get_connection(connection_id)
        backend_ws = self.backend_connections.get(backend_key)

        if not connection or not backend_ws:
            return

        # Create tasks for bidirectional message routing
        client_to_backend_task = asyncio.create_task(
            self._route_client_to_backend(connection, backend_ws)
        )
        backend_to_client_task = asyncio.create_task(
            self._route_backend_to_client(connection, backend_ws)
        )

        try:
            # Wait for either task to complete (indicating disconnection)
            done, pending = await asyncio.wait(
                [client_to_backend_task, backend_to_client_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        except Exception as e:
            logger.error(f"Error in message routing for {connection_id}: {e}")

    async def _route_client_to_backend(
        self,
        connection: WebSocketConnection,
        backend_ws: aiohttp.ClientWebSocketResponse,
    ) -> None:
        """Route messages from client to backend."""
        try:
            while True:
                # Receive message from client
                message = await connection.websocket.receive_text()
                connection.update_activity()

                # Parse and process message
                try:
                    parsed_message = json.loads(message)

                    # Handle special gateway messages
                    if await self._handle_gateway_message(connection, parsed_message):
                        continue

                    # Add gateway metadata
                    parsed_message["_gateway"] = {
                        "connection_id": connection.connection_id,
                        "user_id": connection.user_id,
                        "username": connection.username,
                        "therapeutic_session_id": connection.therapeutic_session_id,
                        "timestamp": time.time(),
                    }

                    # Forward to backend
                    await backend_ws.send_str(json.dumps(parsed_message))

                except json.JSONDecodeError:
                    # Forward raw message if not JSON
                    await backend_ws.send_str(message)

        except WebSocketDisconnect:
            logger.info(f"Client disconnected: {connection.connection_id}")
        except Exception as e:
            logger.error(f"Error routing client to backend: {e}")

    async def _route_backend_to_client(
        self,
        connection: WebSocketConnection,
        backend_ws: aiohttp.ClientWebSocketResponse,
    ) -> None:
        """Route messages from backend to client."""
        try:
            async for msg in backend_ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    # Process and forward message
                    try:
                        parsed_message = json.loads(msg.data)

                        # Add gateway response metadata
                        parsed_message["_gateway_response"] = {
                            "processed_at": time.time(),
                            "connection_id": connection.connection_id,
                        }

                        # Send to client
                        await connection.websocket.send_text(json.dumps(parsed_message))

                    except json.JSONDecodeError:
                        # Forward raw message if not JSON
                        await connection.websocket.send_text(msg.data)

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"Backend WebSocket error: {backend_ws.exception()}")
                    break

        except Exception as e:
            logger.error(f"Error routing backend to client: {e}")

    async def _handle_gateway_message(
        self, connection: WebSocketConnection, message: dict[str, Any]
    ) -> bool:
        """
        Handle special gateway messages.

        Args:
            connection: WebSocket connection
            message: Parsed message

        Returns:
            True if message was handled by gateway
        """
        message_type = message.get("type")
        if not message_type:
            return False

        handler = self.message_handlers.get(message_type)
        if handler:
            try:
                await handler(connection, message)
                return True
            except Exception as e:
                logger.error(f"Error handling gateway message {message_type}: {e}")
                await self._send_error_response(connection, message_type, str(e))
                return True

        return False

    async def _handle_ping(
        self, connection: WebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Handle ping message."""
        await connection.websocket.send_text(
            json.dumps(
                {
                    "type": "pong",
                    "timestamp": time.time(),
                    "connection_id": connection.connection_id,
                }
            )
        )

    async def _handle_authenticate(
        self, connection: WebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Handle authentication message."""
        # Authentication should be handled at connection time
        # This is for re-authentication or authentication updates
        await self._send_error_response(
            connection,
            "authenticate",
            "Authentication must be performed at connection time",
        )

    async def _handle_join_session(
        self, connection: WebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Handle join therapeutic session message."""
        session_id = message.get("session_id")
        if not session_id:
            await self._send_error_response(
                connection, "join_session", "Missing session_id"
            )
            return

        # Update connection with session ID
        connection.therapeutic_session_id = session_id

        # Add to session index
        if session_id not in self.connection_manager.session_connections:
            self.connection_manager.session_connections[session_id] = set()
        self.connection_manager.session_connections[session_id].add(
            connection.connection_id
        )

        await connection.websocket.send_text(
            json.dumps(
                {
                    "type": "session_joined",
                    "session_id": session_id,
                    "connection_id": connection.connection_id,
                }
            )
        )

    async def _handle_leave_session(
        self, connection: WebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Handle leave therapeutic session message."""
        session_id = connection.therapeutic_session_id
        if session_id and session_id in self.connection_manager.session_connections:
            self.connection_manager.session_connections[session_id].discard(
                connection.connection_id
            )
            if not self.connection_manager.session_connections[session_id]:
                del self.connection_manager.session_connections[session_id]

        connection.therapeutic_session_id = None

        await connection.websocket.send_text(
            json.dumps(
                {
                    "type": "session_left",
                    "session_id": session_id,
                    "connection_id": connection.connection_id,
                }
            )
        )

    async def _handle_therapeutic_event(
        self, connection: WebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Handle therapeutic event message."""
        event_type = message.get("event_type")
        if not event_type:
            await self._send_error_response(
                connection, "therapeutic_event", "Missing event_type"
            )
            return

        # Log therapeutic event
        logger.info(
            f"Therapeutic event: {event_type}",
            extra={
                "connection_id": connection.connection_id,
                "user_id": connection.user_id,
                "session_id": connection.therapeutic_session_id,
                "event_type": event_type,
                "event_data": message.get("data", {}),
            },
        )

        # Acknowledge event
        await connection.websocket.send_text(
            json.dumps(
                {
                    "type": "therapeutic_event_ack",
                    "event_type": event_type,
                    "timestamp": time.time(),
                }
            )
        )

    async def _handle_crisis_alert(
        self, connection: WebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Handle crisis alert message."""
        # Mark connection as crisis mode
        connection.crisis_mode = True

        # Log crisis alert
        logger.critical(
            "Crisis alert received",
            extra={
                "connection_id": connection.connection_id,
                "user_id": connection.user_id,
                "session_id": connection.therapeutic_session_id,
                "alert_data": message.get("data", {}),
                "client_ip": connection.client_ip,
            },
        )

        # Acknowledge crisis alert
        await connection.websocket.send_text(
            json.dumps(
                {
                    "type": "crisis_alert_ack",
                    "timestamp": time.time(),
                    "support_available": True,
                }
            )
        )

        # TODO: Trigger crisis response procedures
        # This could include notifying crisis support staff,
        # escalating to emergency services, etc.

    async def _send_error_response(
        self, connection: WebSocketConnection, message_type: str, error: str
    ) -> None:
        """Send error response to client."""
        await connection.websocket.send_text(
            json.dumps(
                {
                    "type": "error",
                    "original_type": message_type,
                    "error": error,
                    "timestamp": time.time(),
                }
            )
        )

    def get_proxy_stats(self) -> dict[str, Any]:
        """Get proxy statistics."""
        return {
            "backend_connections": len(self.backend_connections),
            "active_proxies": len(self.connection_to_backend),
            "backend_services": len(
                {key.split(":")[0] for key in self.backend_connections.keys()}
            ),
        }
