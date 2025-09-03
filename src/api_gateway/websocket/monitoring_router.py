"""
WebSocket monitoring endpoint for the API Gateway.

Provides real-time monitoring data aggregation from all backend services including:
- Service health status and request routing metrics
- Authentication events and connection management
- Load balancing metrics and service discovery status
- Request/response performance metrics and error rates
- Custom application-specific debug events from all services
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any
from uuid import uuid4

import psutil
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..auth.jwt_handler import verify_token
from ..monitoring.health import health_monitor
from ..service_discovery.manager import ServiceDiscoveryManager
from .connection_manager import WebSocketConnectionManager

logger = logging.getLogger(__name__)
router = APIRouter()


class GatewayMonitoringEvent(BaseModel):
    """Gateway monitoring event schema."""

    type: str
    timestamp: str
    service_id: str = "api-gateway"
    data: dict[str, Any]


class ServiceHealthAggregation(BaseModel):
    """Aggregated service health data."""

    services: dict[str, dict[str, Any]]
    overall_status: str
    total_services: int
    healthy_services: int
    response_times: dict[str, float]
    last_check: str


class RequestMetrics(BaseModel):
    """Request routing and performance metrics."""

    total_requests: int
    requests_per_second: float
    average_response_time: float
    error_rate: float
    status_codes: dict[str, int]
    service_routing: dict[str, int]
    timestamp: str


class AuthenticationMetrics(BaseModel):
    """Authentication and authorization metrics."""

    total_auth_attempts: int
    successful_auths: int
    failed_auths: int
    active_sessions: int
    token_validations: int
    auth_errors: list[str]
    timestamp: str


class GatewayMonitoringManager:
    """Manager for API Gateway monitoring WebSocket connections."""

    def __init__(
        self,
        connection_manager: WebSocketConnectionManager,
        discovery_manager: ServiceDiscoveryManager,
    ):
        self.connections: dict[str, WebSocket] = {}
        self.authenticated_connections: set[str] = set()
        self.connection_manager = connection_manager
        self.discovery_manager = discovery_manager
        self.health_monitor = health_monitor

        # Metrics tracking
        self.request_metrics = {
            "total_requests": 0,
            "request_times": [],
            "status_codes": {},
            "service_routing": {},
            "auth_attempts": 0,
            "auth_successes": 0,
            "auth_failures": 0,
        }

        self._monitoring_task: asyncio.Task | None = None
        self._start_monitoring()

    def _start_monitoring(self):
        """Start background monitoring task."""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """Background monitoring loop that broadcasts gateway metrics."""
        while True:
            try:
                if self.connections:
                    # Broadcast different types of monitoring data
                    await self._broadcast_service_health()
                    await self._broadcast_request_metrics()
                    await self._broadcast_auth_metrics()
                    await self._broadcast_gateway_performance()

                # Wait 5 seconds before next broadcast
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error in gateway monitoring loop: {e}")
                await asyncio.sleep(10)

    async def _broadcast_service_health(self):
        """Broadcast aggregated service health status."""
        try:
            # Get health status from all discovered services
            services = await self.discovery_manager.get_all_services()
            service_health = {}
            healthy_count = 0
            total_count = len(services)

            for service_name, service_info in services.items():
                try:
                    # Get health status for each service
                    health_status = await self._check_service_health(service_info)
                    service_health[service_name] = health_status

                    if health_status.get("status") == "healthy":
                        healthy_count += 1

                except Exception as e:
                    service_health[service_name] = {
                        "status": "unknown",
                        "error": str(e),
                        "response_time": 0,
                    }

            # Determine overall status
            if healthy_count == total_count and total_count > 0:
                overall_status = "healthy"
            elif healthy_count > 0:
                overall_status = "degraded"
            else:
                overall_status = "unhealthy"

            health_data = ServiceHealthAggregation(
                services=service_health,
                overall_status=overall_status,
                total_services=total_count,
                healthy_services=healthy_count,
                response_times={
                    name: info.get("response_time", 0)
                    for name, info in service_health.items()
                },
                last_check=datetime.utcnow().isoformat(),
            )

            event = GatewayMonitoringEvent(
                type="service_health_aggregation",
                timestamp=datetime.utcnow().isoformat(),
                data=health_data.dict(),
            )

            await self._broadcast_to_all(event.dict())

        except Exception as e:
            logger.error(f"Error broadcasting service health: {e}")

    async def _check_service_health(
        self, service_info: dict[str, Any]
    ) -> dict[str, Any]:
        """Check health of a specific service."""
        try:
            # This would typically make an HTTP request to the service's health endpoint
            # For now, we'll simulate based on service discovery status
            return {
                "status": "healthy",
                "response_time": 50.0,  # Simulated response time
                "last_check": datetime.utcnow().isoformat(),
                "version": service_info.get("version", "unknown"),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": 0,
                "last_check": datetime.utcnow().isoformat(),
            }

    async def _broadcast_request_metrics(self):
        """Broadcast request routing and performance metrics."""
        try:
            # Calculate metrics from tracked data
            current_time = time.time()
            recent_requests = [
                t
                for t in self.request_metrics["request_times"]
                if current_time - t < 60
            ]

            request_data = RequestMetrics(
                total_requests=self.request_metrics["total_requests"],
                requests_per_second=len(recent_requests) / 60.0,
                average_response_time=150.0,  # TODO: Calculate from actual metrics
                error_rate=0.02,  # TODO: Calculate from actual error tracking
                status_codes=self.request_metrics["status_codes"].copy(),
                service_routing=self.request_metrics["service_routing"].copy(),
                timestamp=datetime.utcnow().isoformat(),
            )

            event = GatewayMonitoringEvent(
                type="request_metrics",
                timestamp=datetime.utcnow().isoformat(),
                data=request_data.dict(),
            )

            await self._broadcast_to_all(event.dict())

        except Exception as e:
            logger.error(f"Error broadcasting request metrics: {e}")

    async def _broadcast_auth_metrics(self):
        """Broadcast authentication and authorization metrics."""
        try:
            auth_data = AuthenticationMetrics(
                total_auth_attempts=self.request_metrics["auth_attempts"],
                successful_auths=self.request_metrics["auth_successes"],
                failed_auths=self.request_metrics["auth_failures"],
                active_sessions=len(self.connection_manager.connections),
                token_validations=self.request_metrics["auth_attempts"],  # Simplified
                auth_errors=[],  # TODO: Track actual auth errors
                timestamp=datetime.utcnow().isoformat(),
            )

            event = GatewayMonitoringEvent(
                type="authentication_metrics",
                timestamp=datetime.utcnow().isoformat(),
                data=auth_data.dict(),
            )

            await self._broadcast_to_all(event.dict())

        except Exception as e:
            logger.error(f"Error broadcasting auth metrics: {e}")

    async def _broadcast_gateway_performance(self):
        """Broadcast gateway performance metrics."""
        try:
            # Get system performance metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()

            performance_data = {
                "interface_id": "api-gateway",
                "metrics": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "memory_used": memory.used,
                    "memory_total": memory.total,
                    "active_connections": len(self.connections),
                    "websocket_connections": len(self.connection_manager.connections),
                    "services_discovered": len(
                        await self.discovery_manager.get_all_services()
                    ),
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

            event = GatewayMonitoringEvent(
                type="performance_metric",
                timestamp=datetime.utcnow().isoformat(),
                data=performance_data,
            )

            await self._broadcast_to_all(event.dict())

        except Exception as e:
            logger.error(f"Error broadcasting gateway performance: {e}")

    async def connect(
        self, websocket: WebSocket, connection_id: str, is_authenticated: bool = False
    ):
        """Add a new monitoring WebSocket connection."""
        await websocket.accept()
        self.connections[connection_id] = websocket

        if is_authenticated:
            self.authenticated_connections.add(connection_id)

        logger.info(
            f"Gateway monitoring WebSocket connected: {connection_id} (authenticated: {is_authenticated})"
        )

        # Send initial status
        await self._send_initial_status(websocket)

    async def disconnect(self, connection_id: str):
        """Remove a monitoring WebSocket connection."""
        if connection_id in self.connections:
            del self.connections[connection_id]

        if connection_id in self.authenticated_connections:
            self.authenticated_connections.remove(connection_id)

        logger.info(f"Gateway monitoring WebSocket disconnected: {connection_id}")

    async def _send_initial_status(self, websocket: WebSocket):
        """Send initial status to a newly connected client."""
        try:
            welcome_event = GatewayMonitoringEvent(
                type="connection_status",
                timestamp=datetime.utcnow().isoformat(),
                data={
                    "status": "connected",
                    "service": "API Gateway",
                    "version": "1.0.0",
                    "capabilities": [
                        "service_health_aggregation",
                        "request_metrics",
                        "authentication_metrics",
                        "performance_metrics",
                        "load_balancing_metrics",
                    ],
                },
            )

            await websocket.send_text(json.dumps(welcome_event.dict()))

        except Exception as e:
            logger.error(f"Error sending initial status: {e}")

    async def _broadcast_to_all(self, message: dict[str, Any]):
        """Broadcast message to all connected monitoring clients."""
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

    def track_request(self, status_code: int, service_name: str, response_time: float):
        """Track request metrics for monitoring."""
        self.request_metrics["total_requests"] += 1
        self.request_metrics["request_times"].append(time.time())

        # Track status codes
        status_str = str(status_code)
        self.request_metrics["status_codes"][status_str] = (
            self.request_metrics["status_codes"].get(status_str, 0) + 1
        )

        # Track service routing
        self.request_metrics["service_routing"][service_name] = (
            self.request_metrics["service_routing"].get(service_name, 0) + 1
        )

        # Keep only recent request times (last hour)
        current_time = time.time()
        self.request_metrics["request_times"] = [
            t for t in self.request_metrics["request_times"] if current_time - t < 3600
        ]

    def track_auth_attempt(self, success: bool):
        """Track authentication attempt for monitoring."""
        self.request_metrics["auth_attempts"] += 1
        if success:
            self.request_metrics["auth_successes"] += 1
        else:
            self.request_metrics["auth_failures"] += 1


def create_gateway_monitoring_manager(
    connection_manager: WebSocketConnectionManager,
    discovery_manager: ServiceDiscoveryManager,
) -> GatewayMonitoringManager:
    """Create and return a gateway monitoring manager instance."""
    return GatewayMonitoringManager(connection_manager, discovery_manager)


def _authenticate_websocket(websocket: WebSocket) -> dict[str, Any] | None:
    """Authenticate WebSocket connection using JWT token."""
    try:
        # Try to get token from query parameters
        token = websocket.query_params.get("token")

        if not token:
            # Try to get token from headers
            auth_header = websocket.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]

        if not token:
            return None

        # Verify token
        token_data = verify_token(token)
        return token_data

    except Exception as e:
        logger.warning(f"Gateway WebSocket authentication failed: {e}")
        return None


async def create_monitoring_websocket_endpoint(
    gateway_monitoring_manager: GatewayMonitoringManager,
):
    """Create the monitoring WebSocket endpoint."""

    @router.websocket("/monitoring")
    async def websocket_monitoring_endpoint(websocket: WebSocket):
        """
        Real-time WebSocket endpoint for API Gateway monitoring data.

        Provides aggregated monitoring information including:
        - Service health status and discovery metrics
        - Request routing and performance metrics
        - Authentication and authorization statistics
        - Load balancing and connection management data
        """
        connection_id = str(uuid4())

        try:
            # Attempt authentication
            auth_data = _authenticate_websocket(websocket)
            is_authenticated = auth_data is not None

            # Connect to monitoring manager
            await gateway_monitoring_manager.connect(
                websocket, connection_id, is_authenticated
            )

            # Keep connection alive and handle incoming messages
            while True:
                try:
                    message = await websocket.receive_text()

                    # Parse and handle commands
                    try:
                        command = json.loads(message)
                        await _handle_monitoring_command(
                            command,
                            connection_id,
                            is_authenticated,
                            gateway_monitoring_manager,
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
            logger.error(f"Error in gateway monitoring WebSocket endpoint: {e}")

        finally:
            await gateway_monitoring_manager.disconnect(connection_id)

    return router


async def _handle_monitoring_command(
    command: dict[str, Any],
    connection_id: str,
    is_authenticated: bool,
    manager: GatewayMonitoringManager,
):
    """Handle incoming monitoring commands."""
    try:
        command_type = command.get("type")

        if command_type == "service_health_request":
            await manager._broadcast_service_health()

        elif command_type == "request_metrics_request":
            await manager._broadcast_request_metrics()

        elif command_type == "auth_metrics_request":
            await manager._broadcast_auth_metrics()

        elif command_type == "performance_request":
            await manager._broadcast_gateway_performance()

        else:
            logger.warning(f"Unknown command: {command_type} from {connection_id}")

    except Exception as e:
        logger.error(f"Error handling gateway monitoring command: {e}")


__all__ = [
    "router",
    "GatewayMonitoringManager",
    "create_gateway_monitoring_manager",
    "create_monitoring_websocket_endpoint",
]
