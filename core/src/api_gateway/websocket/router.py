"""
WebSocket router for the API Gateway.

This module provides FastAPI WebSocket routing with authentication integration,
service discovery, and therapeutic session management.
"""

import logging
import time
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    status,
)

from ..core.service_router import ServiceRouter
from ..models import AuthContext
from ..services import ServiceDiscoveryManager
from ..utils.auth_utils import get_websocket_auth_context
from .connection_manager import ConnectionType, WebSocketConnectionManager
from .proxy import WebSocketProxy

logger = logging.getLogger(__name__)


class WebSocketRouter:
    """
    WebSocket router for the API Gateway.

    Provides FastAPI WebSocket endpoints with authentication, service discovery,
    and therapeutic session management integration.
    """

    def __init__(
        self,
        connection_manager: WebSocketConnectionManager,
        service_router: ServiceRouter,
        discovery_manager: ServiceDiscoveryManager,
    ):
        """
        Initialize WebSocket router.

        Args:
            connection_manager: WebSocket connection manager
            service_router: Service router for backend selection
            discovery_manager: Service discovery manager
        """
        self.connection_manager = connection_manager
        self.service_router = service_router
        self.discovery_manager = discovery_manager

        # Initialize WebSocket proxy
        self.proxy = WebSocketProxy(
            connection_manager, service_router, discovery_manager
        )

        # Create FastAPI router
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup WebSocket routes."""

        @self.router.websocket("/ws/chat")
        async def chat_websocket(websocket: WebSocket, token: str | None = None):
            """Chat WebSocket endpoint."""
            auth_context = await self._get_auth_context(websocket, token)
            await self.proxy.handle_connection(
                websocket=websocket,
                connection_type=ConnectionType.CHAT,
                service_name="player-experience-interface",
                auth_context=auth_context,
            )

        @self.router.websocket("/ws/narrative")
        async def narrative_websocket(websocket: WebSocket, token: str | None = None):
            """Narrative WebSocket endpoint."""
            auth_context = await self._get_auth_context(websocket, token)
            await self.proxy.handle_connection(
                websocket=websocket,
                connection_type=ConnectionType.NARRATIVE,
                service_name="player-experience-interface",
                auth_context=auth_context,
            )

        @self.router.websocket("/ws/therapeutic/{session_id}")
        async def therapeutic_websocket(
            websocket: WebSocket, session_id: str, token: str | None = None
        ):
            """Therapeutic session WebSocket endpoint."""
            auth_context = await self._get_auth_context(websocket, token, required=True)

            # Verify therapeutic access
            if not auth_context or not auth_context.is_therapeutic_context():
                await websocket.close(code=1008, reason="Therapeutic access required")
                return

            await self.proxy.handle_connection(
                websocket=websocket,
                connection_type=ConnectionType.THERAPEUTIC_SESSION,
                service_name="core-gameplay-loop",
                auth_context=auth_context,
                therapeutic_session_id=session_id,
            )

        @self.router.websocket("/ws/crisis")
        async def crisis_websocket(websocket: WebSocket, token: str | None = None):
            """Crisis support WebSocket endpoint."""
            auth_context = await self._get_auth_context(websocket, token, required=True)

            # Mark as crisis mode
            if auth_context:
                auth_context.crisis_mode = True

            await self.proxy.handle_connection(
                websocket=websocket,
                connection_type=ConnectionType.CRISIS_SUPPORT,
                service_name="core-gameplay-loop",
                auth_context=auth_context,
            )

        @self.router.websocket("/ws/admin")
        async def admin_websocket(websocket: WebSocket, token: str | None = None):
            """Admin WebSocket endpoint."""
            auth_context = await self._get_auth_context(websocket, token, required=True)

            # Verify admin access
            if not auth_context or not auth_context.permissions.is_admin():
                await websocket.close(code=1008, reason="Admin access required")
                return

            await self.proxy.handle_connection(
                websocket=websocket,
                connection_type=ConnectionType.ADMIN,
                service_name="agent-orchestration",
                auth_context=auth_context,
            )

        @self.router.websocket("/ws/monitoring")
        async def monitoring_websocket(websocket: WebSocket, token: str | None = None):
            """Monitoring WebSocket endpoint."""
            auth_context = await self._get_auth_context(websocket, token, required=True)

            # Verify monitoring access
            if not auth_context or not (
                auth_context.permissions.is_admin()
                or auth_context.permissions.is_therapist()
            ):
                await websocket.close(code=1008, reason="Monitoring access required")
                return

            await self.proxy.handle_connection(
                websocket=websocket,
                connection_type=ConnectionType.MONITORING,
                service_name="agent-orchestration",
                auth_context=auth_context,
            )

        # HTTP endpoints for WebSocket management
        @self.router.get("/ws/stats")
        async def websocket_stats(
            auth_context: AuthContext = Depends(get_websocket_auth_context),
        ):
            """Get WebSocket connection statistics."""
            if not auth_context.permissions.is_admin():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            connection_stats = self.connection_manager.get_connection_stats()
            proxy_stats = self.proxy.get_proxy_stats()

            return {
                "connections": connection_stats,
                "proxy": proxy_stats,
                "timestamp": time.time(),
            }

        @self.router.post("/ws/broadcast/user/{user_id}")
        async def broadcast_to_user(
            user_id: str,
            message: dict[str, Any],
            auth_context: AuthContext = Depends(get_websocket_auth_context),
        ):
            """Broadcast message to all connections of a user."""
            if not auth_context.permissions.is_admin():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            sent_count = await self.connection_manager.broadcast_to_user(
                user_id, message
            )
            return {"sent_to_connections": sent_count}

        @self.router.post("/ws/broadcast/session/{session_id}")
        async def broadcast_to_session(
            session_id: str,
            message: dict[str, Any],
            auth_context: AuthContext = Depends(get_websocket_auth_context),
        ):
            """Broadcast message to all connections in a therapeutic session."""
            if not (
                auth_context.permissions.is_admin()
                or auth_context.permissions.is_therapist()
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin or therapist access required",
                )

            sent_count = await self.connection_manager.broadcast_to_session(
                session_id, message
            )
            return {"sent_to_connections": sent_count}

        @self.router.delete("/ws/connection/{connection_id}")
        async def disconnect_connection(
            connection_id: str,
            auth_context: AuthContext = Depends(get_websocket_auth_context),
        ):
            """Disconnect a specific WebSocket connection."""
            if not auth_context.permissions.is_admin():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required",
                )

            await self.connection_manager.disconnect(connection_id, "admin_disconnect")
            return {"status": "disconnected", "connection_id": connection_id}

    async def _get_auth_context(
        self, websocket: WebSocket, token: str | None = None, required: bool = False
    ) -> AuthContext | None:
        """
        Get authentication context for WebSocket connection.

        Args:
            websocket: WebSocket connection
            token: Authentication token
            required: Whether authentication is required

        Returns:
            Authentication context or None
        """
        try:
            # Try to get token from query parameter if not provided
            if not token:
                token = websocket.query_params.get("token")

            # Try to get token from headers
            if not token:
                auth_header = websocket.headers.get("authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header[7:]

            if not token:
                if required:
                    await websocket.close(code=1008, reason="Authentication required")
                    return None
                return None

            # Validate token and get auth context
            # This would integrate with your authentication service
            auth_context = await get_websocket_auth_context(token)

            if not auth_context and required:
                await websocket.close(code=1008, reason="Invalid authentication")
                return None

            return auth_context

        except Exception as e:
            logger.error(f"Error getting auth context: {e}")
            if required:
                await websocket.close(code=1011, reason="Authentication error")
            return None

    def get_router(self) -> APIRouter:
        """Get the FastAPI router."""
        return self.router


def create_websocket_router(
    connection_manager: WebSocketConnectionManager,
    service_router: ServiceRouter,
    discovery_manager: ServiceDiscoveryManager,
) -> APIRouter:
    """
    Create WebSocket router with all dependencies.

    Args:
        connection_manager: WebSocket connection manager
        service_router: Service router
        discovery_manager: Service discovery manager

    Returns:
        Configured FastAPI router
    """
    websocket_router = WebSocketRouter(
        connection_manager, service_router, discovery_manager
    )
    return websocket_router.get_router()
