"""
WebSocket monitoring endpoint for the Player Experience API.

Provides real-time monitoring data for the Developer Interface including:
- Interface health status and performance metrics
- Build completion notifications and error reporting
- Live reload events and hot module replacement status
- System performance metrics and resource usage
- Custom application-specific debug events
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

import psutil
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ...auth.jwt_handler import verify_token
from ...monitoring.metrics_collector import get_metrics_collector
from ...monitoring.performance_monitor import get_performance_monitor

logger = logging.getLogger(__name__)
router = APIRouter()

# Global connection manager for monitoring WebSocket connections
monitoring_connections: dict[str, WebSocket] = {}
authenticated_connections: set[str] = set()


class MonitoringEvent(BaseModel):
    """Base monitoring event schema."""

    type: str
    timestamp: str
    service_id: str = "player-experience-api"
    data: dict[str, Any]


class InterfaceHealthData(BaseModel):
    """Interface health status data."""

    id: str
    name: str
    port: int
    status: str  # 'healthy' | 'unhealthy' | 'unknown'
    response_time: float
    last_check: str
    error: str | None = None
    build_time: float | None = None
    error_count: int = 0


class BuildStatusData(BaseModel):
    """Build status event data."""

    interface_id: str
    status: str  # 'building' | 'success' | 'error' | 'idle'
    build_time: float
    errors: list[str]
    warnings: list[str]
    timestamp: str


class LiveReloadData(BaseModel):
    """Live reload event data."""

    interface_id: str
    status: str  # 'reloading' | 'completed' | 'failed'
    timestamp: str
    build_time: float | None = None
    changes: list[str] | None = None


class PerformanceMetricData(BaseModel):
    """Performance metric data."""

    interface_id: str
    metrics: dict[str, float]
    timestamp: str


class MonitoringWebSocketManager:
    """Manager for monitoring WebSocket connections."""

    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.authenticated_connections: set[str] = set()
        self.metrics_collector = get_metrics_collector()
        self.performance_monitor = get_performance_monitor()
        self._monitoring_task: asyncio.Task | None = None
        self._start_monitoring()

    def _start_monitoring(self):
        """Start background monitoring task."""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """Background monitoring loop that broadcasts system metrics."""
        while True:
            try:
                if self.connections:
                    # Collect system metrics
                    await self._broadcast_health_status()
                    await self._broadcast_performance_metrics()

                # Wait 5 seconds before next broadcast
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait longer on error

    async def _broadcast_health_status(self):
        """Broadcast interface health status."""
        try:
            # Get current health metrics
            health_data = InterfaceHealthData(
                id="player-experience",
                name="Player Experience API",
                port=8080,
                status="healthy",  # TODO: Implement actual health check
                response_time=50.0,  # TODO: Get from actual metrics
                last_check=datetime.utcnow().isoformat(),
                error_count=0,
                build_time=2.3,
            )

            event = MonitoringEvent(
                type="interface_health",
                timestamp=datetime.utcnow().isoformat(),
                data=health_data.dict(),
            )

            await self._broadcast_to_all(event.dict())

        except Exception as e:
            logger.error(f"Error broadcasting health status: {e}")

    async def _broadcast_performance_metrics(self):
        """Broadcast performance metrics."""
        try:
            # Get system performance metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()

            performance_data = PerformanceMetricData(
                interface_id="player-experience",
                metrics={
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "memory_used": memory.used,
                    "memory_total": memory.total,
                    "active_connections": len(self.connections),
                    "authenticated_connections": len(self.authenticated_connections),
                },
                timestamp=datetime.utcnow().isoformat(),
            )

            event = MonitoringEvent(
                type="performance_metric",
                timestamp=datetime.utcnow().isoformat(),
                data=performance_data.dict(),
            )

            await self._broadcast_to_all(event.dict())

        except Exception as e:
            logger.error(f"Error broadcasting performance metrics: {e}")

    async def connect(
        self, websocket: WebSocket, connection_id: str, is_authenticated: bool = False
    ):
        """Add a new WebSocket connection."""
        await websocket.accept()
        self.connections[connection_id] = websocket

        if is_authenticated:
            self.authenticated_connections.add(connection_id)

        logger.info(
            f"Monitoring WebSocket connected: {connection_id} (authenticated: {is_authenticated})"
        )

        # Send initial status
        await self._send_initial_status(websocket)

    async def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.connections:
            del self.connections[connection_id]

        if connection_id in self.authenticated_connections:
            self.authenticated_connections.remove(connection_id)

        logger.info(f"Monitoring WebSocket disconnected: {connection_id}")

    async def _send_initial_status(self, websocket: WebSocket):
        """Send initial status to a newly connected client."""
        try:
            # Send welcome message
            welcome_event = MonitoringEvent(
                type="connection_status",
                timestamp=datetime.utcnow().isoformat(),
                data={
                    "status": "connected",
                    "service": "Player Experience API",
                    "version": "1.0.0",
                    "capabilities": [
                        "interface_health",
                        "performance_metrics",
                        "build_status",
                        "live_reload",
                        "error_reporting",
                    ],
                },
            )

            await websocket.send_text(json.dumps(welcome_event.dict()))

        except Exception as e:
            logger.error(f"Error sending initial status: {e}")

    async def _broadcast_to_all(self, message: dict[str, Any]):
        """Broadcast message to all connected clients."""
        if not self.connections:
            return

        message_json = json.dumps(message)
        disconnected = []

        for connection_id, websocket in self.connections.items():
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.warning(f"Failed to send to {connection_id}: {e}")
                disconnected.append(connection_id)

        # Clean up disconnected clients
        for connection_id in disconnected:
            await self.disconnect(connection_id)

    async def broadcast_build_status(self, build_data: BuildStatusData):
        """Broadcast build status event."""
        event = MonitoringEvent(
            type="build_status",
            timestamp=datetime.utcnow().isoformat(),
            data=build_data.dict(),
        )

        await self._broadcast_to_all(event.dict())

    async def broadcast_live_reload(self, reload_data: LiveReloadData):
        """Broadcast live reload event."""
        event = MonitoringEvent(
            type="live_reload",
            timestamp=datetime.utcnow().isoformat(),
            data=reload_data.dict(),
        )

        await self._broadcast_to_all(event.dict())

    async def broadcast_error_report(self, error_data: dict[str, Any]):
        """Broadcast error report event."""
        event = MonitoringEvent(
            type="error_report",
            timestamp=datetime.utcnow().isoformat(),
            data=error_data,
        )

        await self._broadcast_to_all(event.dict())

    async def broadcast_custom_event(self, event_type: str, event_data: dict[str, Any]):
        """Broadcast custom application-specific event."""
        event = MonitoringEvent(
            type=event_type, timestamp=datetime.utcnow().isoformat(), data=event_data
        )

        await self._broadcast_to_all(event.dict())


# Global monitoring manager instance
monitoring_manager = MonitoringWebSocketManager()


def _authenticate_websocket(websocket: WebSocket) -> dict[str, Any] | None:
    """Authenticate WebSocket connection using JWT token."""
    try:
        # Try to get token from query parameters
        token = websocket.query_params.get("token")

        if not token:
            # Try to get token from headers (if supported by client)
            auth_header = websocket.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]

        if not token:
            return None

        # Verify token
        token_data = verify_token(token)
        return token_data

    except Exception as e:
        logger.warning(f"WebSocket authentication failed: {e}")
        return None


@router.websocket("/monitoring")
async def websocket_monitoring_endpoint(websocket: WebSocket):
    """
    Real-time WebSocket endpoint for monitoring data.

    Provides real-time monitoring information for the Developer Interface including:
    - Interface health status and performance metrics
    - Build completion notifications and error reporting
    - Live reload events and system resource usage
    - Custom application-specific debug events

    Authentication is optional but recommended for full access to monitoring data.
    """
    connection_id = str(uuid4())

    try:
        # Attempt authentication
        auth_data = _authenticate_websocket(websocket)
        is_authenticated = auth_data is not None

        # Connect to monitoring manager
        await monitoring_manager.connect(websocket, connection_id, is_authenticated)

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for incoming messages (for potential commands)
                message = await websocket.receive_text()

                # Parse and handle commands
                try:
                    command = json.loads(message)
                    await _handle_monitoring_command(
                        command, connection_id, is_authenticated
                    )
                except json.JSONDecodeError:
                    logger.warning(
                        f"Invalid JSON received from {connection_id}: {message}"
                    )

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                break

    except Exception as e:
        logger.error(f"Error in monitoring WebSocket endpoint: {e}")

    finally:
        await monitoring_manager.disconnect(connection_id)


async def _handle_monitoring_command(
    command: dict[str, Any], connection_id: str, is_authenticated: bool
):
    """Handle incoming monitoring commands."""
    try:
        command_type = command.get("type")

        if command_type == "health_check_request":
            # Trigger immediate health check broadcast
            await monitoring_manager._broadcast_health_status()

        elif command_type == "performance_request":
            # Trigger immediate performance metrics broadcast
            await monitoring_manager._broadcast_performance_metrics()

        elif command_type == "custom_event" and is_authenticated:
            # Handle custom event broadcasting (authenticated users only)
            event_type = command.get("event_type")
            event_data = command.get("data", {})

            if event_type:
                await monitoring_manager.broadcast_custom_event(event_type, event_data)

        else:
            logger.warning(
                f"Unknown or unauthorized command: {command_type} from {connection_id}"
            )

    except Exception as e:
        logger.error(f"Error handling monitoring command: {e}")


# Export monitoring manager for use by other modules
__all__ = [
    "router",
    "monitoring_manager",
    "MonitoringEvent",
    "InterfaceHealthData",
    "BuildStatusData",
    "LiveReloadData",
    "PerformanceMetricData",
]
