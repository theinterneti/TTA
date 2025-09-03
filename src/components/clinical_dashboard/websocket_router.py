"""
Clinical Dashboard WebSocket Router

Real-time WebSocket endpoints for clinical dashboard functionality including
practitioner authentication, session monitoring, alert broadcasting, and
therapeutic metrics streaming.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter

from .clinical_dashboard_manager import (
    AuditEventType,
    ClinicalDashboardManager,
)

logger = logging.getLogger(__name__)


class ClinicalWebSocketConnection:
    """Represents a clinical practitioner WebSocket connection."""

    def __init__(
        self,
        websocket: WebSocket,
        connection_id: str,
        practitioner_id: str,
        session_token: str,
    ):
        self.websocket = websocket
        self.connection_id = connection_id
        self.practitioner_id = practitioner_id
        self.session_token = session_token
        self.connected_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.subscribed_sessions: set[str] = set()
        self.subscribed_alerts: bool = True
        self.subscribed_metrics: bool = True


class ClinicalDashboardWebSocketRouter:
    """
    WebSocket router for clinical dashboard real-time communication.

    Provides real-time streaming of:
    - Therapeutic session metrics
    - Clinical alerts and notifications
    - System health status
    - Practitioner activity monitoring
    """

    def __init__(self, dashboard_manager: ClinicalDashboardManager):
        self.dashboard_manager = dashboard_manager
        self.router = APIRouter()
        self.active_connections: dict[str, ClinicalWebSocketConnection] = {}
        self.practitioner_connections: dict[str, list[str]] = (
            {}
        )  # practitioner_id -> connection_ids

        # Performance metrics
        self.metrics = {
            "connections_established": 0,
            "connections_closed": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "alerts_broadcasted": 0,
            "metrics_streamed": 0,
        }

        # Background tasks
        self._metrics_broadcast_task: asyncio.Task | None = None
        self._connection_cleanup_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()

        self._setup_routes()
        self._start_background_tasks()

        logger.info("ClinicalDashboardWebSocketRouter initialized")

    def _setup_routes(self) -> None:
        """Setup WebSocket routes for clinical dashboard."""

        @self.router.websocket("/clinical/dashboard/{session_token}")
        async def clinical_dashboard_websocket(
            websocket: WebSocket, session_token: str
        ):
            """Main clinical dashboard WebSocket endpoint."""
            await self._handle_clinical_connection(websocket, session_token)

        @self.router.websocket("/clinical/monitoring/{session_token}")
        async def clinical_monitoring_websocket(
            websocket: WebSocket, session_token: str
        ):
            """Clinical monitoring WebSocket endpoint for real-time metrics."""
            await self._handle_monitoring_connection(websocket, session_token)

    def _start_background_tasks(self) -> None:
        """Start background tasks for real-time broadcasting."""
        self._metrics_broadcast_task = asyncio.create_task(
            self._metrics_broadcast_loop()
        )
        self._connection_cleanup_task = asyncio.create_task(
            self._connection_cleanup_loop()
        )

    async def _handle_clinical_connection(
        self, websocket: WebSocket, session_token: str
    ) -> None:
        """Handle clinical dashboard WebSocket connection."""
        connection_id = None
        try:
            # Validate session token
            practitioner = await self.dashboard_manager.validate_session_token(
                session_token
            )
            if not practitioner:
                await websocket.close(code=1008, reason="Invalid session token")
                return

            # Accept connection
            await websocket.accept()

            # Create connection record
            connection_id = f"clinical_{practitioner.practitioner_id}_{datetime.utcnow().timestamp()}"
            connection = ClinicalWebSocketConnection(
                websocket=websocket,
                connection_id=connection_id,
                practitioner_id=practitioner.practitioner_id,
                session_token=session_token,
            )

            # Register connection
            self.active_connections[connection_id] = connection
            if practitioner.practitioner_id not in self.practitioner_connections:
                self.practitioner_connections[practitioner.practitioner_id] = []
            self.practitioner_connections[practitioner.practitioner_id].append(
                connection_id
            )

            self.metrics["connections_established"] += 1

            # Log connection audit event
            await self.dashboard_manager._log_audit_event(
                practitioner_id=practitioner.practitioner_id,
                event_type=AuditEventType.LOGIN,
                resource_accessed="clinical_dashboard_websocket",
                success=True,
                details={
                    "connection_id": connection_id,
                    "connection_type": "clinical_dashboard",
                },
            )

            # Send initial dashboard state
            await self._send_initial_dashboard_state(connection)

            # Handle messages
            await self._handle_connection_messages(connection)

        except WebSocketDisconnect:
            logger.info(f"Clinical WebSocket disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"Error in clinical WebSocket connection: {e}")
            if websocket.client_state.name != "DISCONNECTED":
                await websocket.close(code=1011, reason="Internal server error")
        finally:
            if connection_id:
                await self._cleanup_connection(connection_id)

    async def _handle_monitoring_connection(
        self, websocket: WebSocket, session_token: str
    ) -> None:
        """Handle clinical monitoring WebSocket connection."""
        # Similar to clinical connection but focused on metrics streaming
        await self._handle_clinical_connection(websocket, session_token)

    async def _send_initial_dashboard_state(
        self, connection: ClinicalWebSocketConnection
    ) -> None:
        """Send initial dashboard state to newly connected practitioner."""
        try:
            # Get dashboard overview
            overview = await self.dashboard_manager.get_dashboard_overview()

            # Get practitioner permissions
            practitioner = self.dashboard_manager.registered_practitioners.get(
                connection.practitioner_id
            )
            if not practitioner:
                return

            permissions = self.dashboard_manager.role_permissions.get(
                practitioner.role, set()
            )

            initial_state = {
                "type": "initial_state",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "dashboard_overview": overview,
                    "practitioner_info": {
                        "id": practitioner.practitioner_id,
                        "username": practitioner.username,
                        "full_name": practitioner.full_name,
                        "role": practitioner.role.value,
                        "access_level": practitioner.access_level.value,
                        "permissions": list(permissions),
                    },
                    "connection_info": {
                        "connection_id": connection.connection_id,
                        "connected_at": connection.connected_at.isoformat(),
                    },
                },
            }

            await connection.websocket.send_text(json.dumps(initial_state))
            self.metrics["messages_sent"] += 1

        except Exception as e:
            logger.error(f"Error sending initial dashboard state: {e}")

    async def _handle_connection_messages(
        self, connection: ClinicalWebSocketConnection
    ) -> None:
        """Handle incoming messages from clinical WebSocket connection."""
        try:
            while True:
                # Receive message
                message_text = await connection.websocket.receive_text()
                self.metrics["messages_received"] += 1
                connection.last_activity = datetime.utcnow()

                try:
                    message = json.loads(message_text)
                    await self._process_clinical_message(connection, message)
                except json.JSONDecodeError:
                    await self._send_error_message(connection, "Invalid JSON format")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await self._send_error_message(
                        connection, "Error processing message"
                    )

        except WebSocketDisconnect:
            raise
        except Exception as e:
            logger.error(f"Error handling connection messages: {e}")
            raise

    async def _process_clinical_message(
        self, connection: ClinicalWebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Process incoming clinical message."""
        message_type = message.get("type")

        if message_type == "subscribe_session":
            await self._handle_session_subscription(connection, message)
        elif message_type == "unsubscribe_session":
            await self._handle_session_unsubscription(connection, message)
        elif message_type == "acknowledge_alert":
            await self._handle_alert_acknowledgment(connection, message)
        elif message_type == "request_metrics":
            await self._handle_metrics_request(connection, message)
        elif message_type == "ping":
            await self._handle_ping(connection, message)
        else:
            await self._send_error_message(
                connection, f"Unknown message type: {message_type}"
            )

    async def _handle_session_subscription(
        self, connection: ClinicalWebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Handle session subscription request."""
        session_id = message.get("session_id")
        if not session_id:
            await self._send_error_message(connection, "Missing session_id")
            return

        # Check permissions
        has_permission = await self.dashboard_manager.check_permission(
            connection.session_token, "view_sessions"
        )
        if not has_permission:
            await self._send_error_message(connection, "Insufficient permissions")
            return

        connection.subscribed_sessions.add(session_id)

        # Send confirmation
        response = {
            "type": "subscription_confirmed",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await connection.websocket.send_text(json.dumps(response))
        self.metrics["messages_sent"] += 1

    async def _handle_session_unsubscription(
        self, connection: ClinicalWebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Handle session unsubscription request."""
        session_id = message.get("session_id")
        if not session_id:
            await self._send_error_message(connection, "Missing session_id")
            return

        connection.subscribed_sessions.discard(session_id)

        # Send confirmation
        response = {
            "type": "unsubscription_confirmed",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await connection.websocket.send_text(json.dumps(response))
        self.metrics["messages_sent"] += 1

    async def _handle_metrics_request(
        self, connection: ClinicalWebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Handle metrics request."""
        session_id = message.get("session_id")
        if not session_id:
            await self._send_error_message(connection, "Missing session_id")
            return

        # Check permissions
        has_permission = await self.dashboard_manager.check_permission(
            connection.session_token, "view_metrics"
        )
        if not has_permission:
            await self._send_error_message(connection, "Insufficient permissions")
            return

        # Get current metrics for session
        metrics = await self.dashboard_manager.collect_real_time_metrics(session_id)
        if metrics:
            await self.broadcast_metrics_update(session_id, metrics)

    async def _handle_alert_acknowledgment(
        self, connection: ClinicalWebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Handle alert acknowledgment."""
        alert_id = message.get("alert_id")
        if not alert_id:
            await self._send_error_message(connection, "Missing alert_id")
            return

        # Check permissions
        has_permission = await self.dashboard_manager.check_permission(
            connection.session_token, "acknowledge_alerts"
        )
        if not has_permission:
            await self._send_error_message(connection, "Insufficient permissions")
            return

        # Acknowledge alert
        success = await self.dashboard_manager.acknowledge_alert(
            alert_id, connection.practitioner_id
        )

        if success:
            # Broadcast acknowledgment to other practitioners
            await self._broadcast_alert_acknowledgment(
                alert_id, connection.practitioner_id
            )

        # Send response
        response = {
            "type": "alert_acknowledged" if success else "alert_acknowledgment_failed",
            "alert_id": alert_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await connection.websocket.send_text(json.dumps(response))
        self.metrics["messages_sent"] += 1

    async def _handle_ping(
        self, connection: ClinicalWebSocketConnection, message: dict[str, Any]
    ) -> None:
        """Handle ping message."""
        response = {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat(),
        }
        await connection.websocket.send_text(json.dumps(response))
        self.metrics["messages_sent"] += 1

    async def _send_error_message(
        self, connection: ClinicalWebSocketConnection, error: str
    ) -> None:
        """Send error message to connection."""
        try:
            error_message = {
                "type": "error",
                "error": error,
                "timestamp": datetime.utcnow().isoformat(),
            }
            await connection.websocket.send_text(json.dumps(error_message))
            self.metrics["messages_sent"] += 1
        except Exception as e:
            logger.error(f"Error sending error message: {e}")

    async def broadcast_alert(self, alert_id: str) -> None:
        """Broadcast new alert to all connected practitioners."""
        try:
            alert = self.dashboard_manager.active_alerts.get(alert_id)
            if not alert:
                return

            alert_message = {
                "type": "new_alert",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "alert_id": alert.alert_id,
                    "user_id": alert.user_id,
                    "session_id": alert.session_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "therapeutic_context": alert.therapeutic_context,
                    "priority_score": alert.priority_score,
                    "escalation_level": alert.escalation_level,
                    "intervention_required": alert.intervention_required,
                    "created_at": alert.timestamp.isoformat(),
                },
            }

            # Broadcast to all practitioners with alert permissions
            for connection in self.active_connections.values():
                if connection.subscribed_alerts:
                    has_permission = await self.dashboard_manager.check_permission(
                        connection.session_token, "view_alerts"
                    )
                    if has_permission:
                        try:
                            await connection.websocket.send_text(
                                json.dumps(alert_message)
                            )
                            self.metrics["messages_sent"] += 1
                        except Exception as e:
                            logger.error(
                                f"Error broadcasting alert to {connection.connection_id}: {e}"
                            )

            self.metrics["alerts_broadcasted"] += 1
            logger.info(f"Broadcasted alert {alert_id} to clinical practitioners")

        except Exception as e:
            logger.error(f"Error broadcasting alert: {e}")

    async def broadcast_metrics_update(self, session_id: str, metrics: Any) -> None:
        """Broadcast metrics update to subscribed practitioners."""
        try:
            metrics_message = {
                "type": "metrics_update",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "session_id": session_id,
                    "user_id": metrics.user_id,
                    "therapeutic_value_accumulated": metrics.therapeutic_value_accumulated,
                    "engagement_level": metrics.engagement_level,
                    "progress_rate": metrics.progress_rate,
                    "safety_score": metrics.safety_score,
                    "crisis_risk_level": metrics.crisis_risk_level,
                    "session_duration_minutes": metrics.session_duration_minutes,
                    "therapeutic_goals_progress": metrics.therapeutic_goals_progress,
                    "intervention_effectiveness": metrics.intervention_effectiveness,
                    "emotional_regulation_score": metrics.emotional_regulation_score,
                    "coping_skills_utilization": metrics.coping_skills_utilization,
                    "therapeutic_alliance_strength": metrics.therapeutic_alliance_strength,
                    "clinical_risk_factors": metrics.clinical_risk_factors,
                    "protective_factors": metrics.protective_factors,
                },
            }

            # Broadcast to practitioners subscribed to this session
            for connection in self.active_connections.values():
                if (
                    session_id in connection.subscribed_sessions
                    and connection.subscribed_metrics
                ):
                    has_permission = await self.dashboard_manager.check_permission(
                        connection.session_token, "view_metrics"
                    )
                    if has_permission:
                        try:
                            await connection.websocket.send_text(
                                json.dumps(metrics_message)
                            )
                            self.metrics["messages_sent"] += 1
                        except Exception as e:
                            logger.error(
                                f"Error broadcasting metrics to {connection.connection_id}: {e}"
                            )

            self.metrics["metrics_streamed"] += 1

        except Exception as e:
            logger.error(f"Error broadcasting metrics update: {e}")

    async def _broadcast_alert_acknowledgment(
        self, alert_id: str, acknowledged_by: str
    ) -> None:
        """Broadcast alert acknowledgment to other practitioners."""
        try:
            ack_message = {
                "type": "alert_acknowledged_by_other",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "alert_id": alert_id,
                    "acknowledged_by": acknowledged_by,
                },
            }

            # Broadcast to all other practitioners
            for connection in self.active_connections.values():
                if connection.practitioner_id != acknowledged_by:
                    try:
                        await connection.websocket.send_text(json.dumps(ack_message))
                        self.metrics["messages_sent"] += 1
                    except Exception as e:
                        logger.error(
                            f"Error broadcasting acknowledgment to {connection.connection_id}: {e}"
                        )

        except Exception as e:
            logger.error(f"Error broadcasting alert acknowledgment: {e}")

    async def _metrics_broadcast_loop(self) -> None:
        """Background loop for broadcasting periodic metrics updates."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Broadcast dashboard overview to all connected practitioners
                    if self.active_connections:
                        overview = await self.dashboard_manager.get_dashboard_overview()

                        overview_message = {
                            "type": "dashboard_overview_update",
                            "timestamp": datetime.utcnow().isoformat(),
                            "data": overview,
                        }

                        for connection in self.active_connections.values():
                            try:
                                await connection.websocket.send_text(
                                    json.dumps(overview_message)
                                )
                                self.metrics["messages_sent"] += 1
                            except Exception as e:
                                logger.error(
                                    f"Error broadcasting overview to {connection.connection_id}: {e}"
                                )

                    # Wait 30 seconds before next broadcast
                    await asyncio.sleep(30)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in metrics broadcast loop: {e}")
                    await asyncio.sleep(30)

        except asyncio.CancelledError:
            logger.info("Metrics broadcast loop cancelled")

    async def _connection_cleanup_loop(self) -> None:
        """Background loop for cleaning up stale connections."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    current_time = datetime.utcnow()
                    stale_connections = []

                    # Find stale connections (inactive for more than 5 minutes)
                    for connection_id, connection in self.active_connections.items():
                        time_since_activity = (
                            current_time - connection.last_activity
                        ).total_seconds()
                        if time_since_activity > 300:  # 5 minutes
                            stale_connections.append(connection_id)

                    # Clean up stale connections
                    for connection_id in stale_connections:
                        await self._cleanup_connection(connection_id)

                    # Wait 60 seconds before next cleanup
                    await asyncio.sleep(60)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in connection cleanup loop: {e}")
                    await asyncio.sleep(60)

        except asyncio.CancelledError:
            logger.info("Connection cleanup loop cancelled")

    async def _cleanup_connection(self, connection_id: str) -> None:
        """Clean up a WebSocket connection."""
        try:
            connection = self.active_connections.get(connection_id)
            if not connection:
                return

            # Remove from active connections
            self.active_connections.pop(connection_id, None)

            # Remove from practitioner connections
            if connection.practitioner_id in self.practitioner_connections:
                practitioner_connections = self.practitioner_connections[
                    connection.practitioner_id
                ]
                if connection_id in practitioner_connections:
                    practitioner_connections.remove(connection_id)
                if not practitioner_connections:
                    self.practitioner_connections.pop(connection.practitioner_id, None)

            self.metrics["connections_closed"] += 1

            # Log disconnection audit event
            await self.dashboard_manager._log_audit_event(
                practitioner_id=connection.practitioner_id,
                event_type=AuditEventType.LOGOUT,
                resource_accessed="clinical_dashboard_websocket",
                success=True,
                details={"connection_id": connection_id, "reason": "disconnected"},
            )

            logger.info(f"Cleaned up clinical WebSocket connection: {connection_id}")

        except Exception as e:
            logger.error(f"Error cleaning up connection {connection_id}: {e}")

    async def shutdown(self) -> None:
        """Shutdown the WebSocket router."""
        try:
            logger.info("Shutting down ClinicalDashboardWebSocketRouter")

            # Signal shutdown
            self._shutdown_event.set()

            # Cancel background tasks
            if self._metrics_broadcast_task and not self._metrics_broadcast_task.done():
                self._metrics_broadcast_task.cancel()
                try:
                    await self._metrics_broadcast_task
                except asyncio.CancelledError:
                    pass

            if (
                self._connection_cleanup_task
                and not self._connection_cleanup_task.done()
            ):
                self._connection_cleanup_task.cancel()
                try:
                    await self._connection_cleanup_task
                except asyncio.CancelledError:
                    pass

            # Close all active connections
            for connection_id in list(self.active_connections.keys()):
                await self._cleanup_connection(connection_id)

            logger.info("ClinicalDashboardWebSocketRouter shutdown complete")

        except Exception as e:
            logger.error(f"Error during WebSocket router shutdown: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """Get WebSocket router metrics."""
        return {
            "active_connections": len(self.active_connections),
            "connected_practitioners": len(self.practitioner_connections),
            **self.metrics,
        }
