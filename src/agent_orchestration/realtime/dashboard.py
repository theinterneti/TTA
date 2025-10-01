"""
Real-time system health and performance dashboards.

This module provides real-time dashboard capabilities for monitoring system
health, agent performance, and workflow status through WebSocket connections.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..monitoring import SystemMonitor, get_system_monitor
from .event_publisher import EventPublisher

# Import alerting system with fallback
try:
    from ...monitoring.realtime_alerts import (
        console_notification_handler,
        get_alert_manager,
    )

    ALERTING_AVAILABLE = True
except ImportError:
    ALERTING_AVAILABLE = False

logger = logging.getLogger(__name__)


class DashboardType(str, Enum):
    """Types of real-time dashboards."""

    SYSTEM_HEALTH = "system_health"
    AGENT_PERFORMANCE = "agent_performance"
    WORKFLOW_STATUS = "workflow_status"
    ERROR_MONITORING = "error_monitoring"
    RESOURCE_USAGE = "resource_usage"
    ALERTS = "alerts"


@dataclass
class DashboardConfig:
    """Configuration for real-time dashboards."""

    enabled: bool = True
    update_interval: float = 2.0  # seconds
    max_data_points: int = 100
    auto_cleanup: bool = True
    cleanup_interval: float = 300.0  # 5 minutes


@dataclass
class DashboardData:
    """Container for dashboard data."""

    dashboard_type: DashboardType
    timestamp: float
    data: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


class RealtimeDashboardManager:
    """Manages real-time dashboards for system monitoring."""

    def __init__(
        self,
        event_publisher: EventPublisher | None = None,
        system_monitor: SystemMonitor | None = None,
        config: DashboardConfig | None = None,
    ):
        self.event_publisher = event_publisher
        self.system_monitor = system_monitor or get_system_monitor()
        self.config = config or DashboardConfig()

        # Dashboard data storage
        self.dashboard_data: dict[DashboardType, list[DashboardData]] = {
            dashboard_type: [] for dashboard_type in DashboardType
        }

        # Active dashboard subscriptions
        self.active_subscriptions: dict[str, set[DashboardType]] = (
            {}
        )  # connection_id -> dashboard_types

        # Alert manager integration
        self.alert_manager = None
        if ALERTING_AVAILABLE:
            try:
                self.alert_manager = get_alert_manager()
                self.alert_manager.add_notification_handler(
                    self._handle_alert_notification
                )
            except Exception as e:
                logger.warning(f"Could not initialize alert manager: {e}")

        # Background tasks
        self.update_task: asyncio.Task | None = None
        self.cleanup_task: asyncio.Task | None = None
        self.is_running = False

        # Performance tracking
        self.last_update_times: dict[DashboardType, float] = {}
        self.update_counts: dict[DashboardType, int] = {}

        logger.info("RealtimeDashboardManager initialized")

    async def start(self) -> None:
        """Start the dashboard manager."""
        if not self.config.enabled or self.is_running:
            return

        self.is_running = True

        # Start background tasks
        self.update_task = asyncio.create_task(self._update_loop())
        if self.config.auto_cleanup:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("RealtimeDashboardManager started")

    async def stop(self) -> None:
        """Stop the dashboard manager."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel background tasks
        for task in [self.update_task, self.cleanup_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("RealtimeDashboardManager stopped")

    async def subscribe_to_dashboard(
        self, connection_id: str, dashboard_types: list[DashboardType]
    ) -> bool:
        """Subscribe a connection to specific dashboard types."""
        if connection_id not in self.active_subscriptions:
            self.active_subscriptions[connection_id] = set()

        self.active_subscriptions[connection_id].update(dashboard_types)

        # Send initial data for subscribed dashboards
        for dashboard_type in dashboard_types:
            await self._send_dashboard_snapshot(connection_id, dashboard_type)

        logger.debug(
            f"Connection {connection_id} subscribed to dashboards: {dashboard_types}"
        )
        return True

    async def unsubscribe_from_dashboard(
        self, connection_id: str, dashboard_types: list[DashboardType] | None = None
    ) -> bool:
        """Unsubscribe a connection from dashboard types."""
        if connection_id not in self.active_subscriptions:
            return False

        if dashboard_types is None:
            # Unsubscribe from all
            self.active_subscriptions.pop(connection_id, None)
        else:
            # Unsubscribe from specific types
            for dashboard_type in dashboard_types:
                self.active_subscriptions[connection_id].discard(dashboard_type)

            # Remove connection if no subscriptions left
            if not self.active_subscriptions[connection_id]:
                self.active_subscriptions.pop(connection_id, None)

        logger.debug(f"Connection {connection_id} unsubscribed from dashboards")
        return True

    async def _update_loop(self) -> None:
        """Main update loop for dashboard data."""
        while self.is_running:
            try:
                current_time = time.time()

                # Update each dashboard type
                for dashboard_type in DashboardType:
                    last_update = self.last_update_times.get(dashboard_type, 0)

                    if current_time - last_update >= self.config.update_interval:
                        await self._update_dashboard_data(dashboard_type)
                        self.last_update_times[dashboard_type] = current_time
                        self.update_counts[dashboard_type] = (
                            self.update_counts.get(dashboard_type, 0) + 1
                        )

                await asyncio.sleep(1.0)  # Check every second

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in dashboard update loop: {e}")
                await asyncio.sleep(5.0)

    async def _update_dashboard_data(self, dashboard_type: DashboardType) -> None:
        """Update data for a specific dashboard type."""
        try:
            if dashboard_type == DashboardType.SYSTEM_HEALTH:
                await self._update_system_health_data()
            elif dashboard_type == DashboardType.AGENT_PERFORMANCE:
                await self._update_agent_performance_data()
            elif dashboard_type == DashboardType.WORKFLOW_STATUS:
                await self._update_workflow_status_data()
            elif dashboard_type == DashboardType.ERROR_MONITORING:
                await self._update_error_monitoring_data()
            elif dashboard_type == DashboardType.RESOURCE_USAGE:
                await self._update_resource_usage_data()
            elif dashboard_type == DashboardType.ALERTS:
                await self._update_alerts_data()

        except Exception as e:
            logger.error(f"Failed to update {dashboard_type} data: {e}")

    async def _update_system_health_data(self) -> None:
        """Update system health dashboard data."""
        if not self.system_monitor:
            return

        metrics = self.system_monitor.get_system_metrics()

        dashboard_data = DashboardData(
            dashboard_type=DashboardType.SYSTEM_HEALTH,
            timestamp=time.time(),
            data={
                "cpu_usage": metrics.get("cpu_usage", 0.0),
                "memory_usage": metrics.get("memory_usage", 0.0),
                "disk_usage": metrics.get("disk_usage", 0.0),
                "network_io": metrics.get("network_io", {}),
                "active_connections": metrics.get("active_connections", 0),
                "uptime": metrics.get("uptime", 0.0),
                "health_status": self._determine_health_status(metrics),
            },
            metadata={
                "update_count": self.update_counts.get(DashboardType.SYSTEM_HEALTH, 0)
            },
        )

        await self._store_and_broadcast_data(dashboard_data)

    async def _update_agent_performance_data(self) -> None:
        """Update agent performance dashboard data."""
        if not self.system_monitor:
            return

        agent_metrics = self.system_monitor.get_all_agent_metrics()

        dashboard_data = DashboardData(
            dashboard_type=DashboardType.AGENT_PERFORMANCE,
            timestamp=time.time(),
            data={
                "total_agents": len(agent_metrics),
                "active_agents": len(
                    [m for m in agent_metrics.values() if m.get("status") == "active"]
                ),
                "agent_details": {
                    agent_id: {
                        "response_time_avg": metrics.get("response_time_avg", 0.0),
                        "throughput_rps": metrics.get("throughput_rps", 0.0),
                        "error_rate": metrics.get("error_rate", 0.0),
                        "queue_depth": metrics.get("queue_depth", 0),
                        "last_activity": metrics.get("last_activity", 0.0),
                    }
                    for agent_id, metrics in agent_metrics.items()
                },
                "performance_summary": self._calculate_performance_summary(
                    agent_metrics
                ),
            },
        )

        await self._store_and_broadcast_data(dashboard_data)

    async def _update_workflow_status_data(self) -> None:
        """Update workflow status dashboard data."""
        # This would integrate with workflow tracking system
        dashboard_data = DashboardData(
            dashboard_type=DashboardType.WORKFLOW_STATUS,
            timestamp=time.time(),
            data={
                "active_workflows": 0,  # Would be populated from workflow tracker
                "completed_workflows": 0,
                "failed_workflows": 0,
                "average_completion_time": 0.0,
                "workflow_details": {},
            },
        )

        await self._store_and_broadcast_data(dashboard_data)

    async def _update_error_monitoring_data(self) -> None:
        """Update error monitoring dashboard data."""
        # This would integrate with error reporting system
        dashboard_data = DashboardData(
            dashboard_type=DashboardType.ERROR_MONITORING,
            timestamp=time.time(),
            data={
                "total_errors": 0,  # Would be populated from error manager
                "critical_errors": 0,
                "error_rate": 0.0,
                "recent_errors": [],
                "error_trends": {},
            },
        )

        await self._store_and_broadcast_data(dashboard_data)

    async def _update_resource_usage_data(self) -> None:
        """Update resource usage dashboard data."""
        if not self.system_monitor:
            return

        metrics = self.system_monitor.get_system_metrics()

        dashboard_data = DashboardData(
            dashboard_type=DashboardType.RESOURCE_USAGE,
            timestamp=time.time(),
            data={
                "cpu_cores": metrics.get("cpu_cores", 1),
                "cpu_usage_per_core": metrics.get("cpu_usage_per_core", []),
                "memory_total": metrics.get("memory_total", 0),
                "memory_available": metrics.get("memory_available", 0),
                "disk_total": metrics.get("disk_total", 0),
                "disk_free": metrics.get("disk_free", 0),
                "network_bytes_sent": metrics.get("network_bytes_sent", 0),
                "network_bytes_recv": metrics.get("network_bytes_recv", 0),
                "process_count": metrics.get("process_count", 0),
            },
        )

        await self._store_and_broadcast_data(dashboard_data)

    async def _store_and_broadcast_data(self, dashboard_data: DashboardData) -> None:
        """Store dashboard data and broadcast to subscribers."""
        # Store data
        data_list = self.dashboard_data[dashboard_data.dashboard_type]
        data_list.append(dashboard_data)

        # Limit data points
        if len(data_list) > self.config.max_data_points:
            data_list.pop(0)

        # Broadcast to subscribers
        await self._broadcast_dashboard_update(dashboard_data)

    async def _broadcast_dashboard_update(self, dashboard_data: DashboardData) -> None:
        """Broadcast dashboard update to subscribed connections."""
        if not self.event_publisher:
            return

        try:
            # Create dashboard update event
            event_data = {
                "event_type": "dashboard_update",
                "dashboard_type": dashboard_data.dashboard_type.value,
                "timestamp": dashboard_data.timestamp,
                "data": dashboard_data.data,
                "metadata": dashboard_data.metadata,
            }

            # This would be sent to WebSocket connections subscribed to this dashboard type
            # Implementation would depend on WebSocket manager integration

        except Exception as e:
            logger.error(f"Failed to broadcast dashboard update: {e}")

    async def _send_dashboard_snapshot(
        self, connection_id: str, dashboard_type: DashboardType
    ) -> None:
        """Send current dashboard snapshot to a connection."""
        data_list = self.dashboard_data[dashboard_type]

        if not data_list:
            return

        # Send recent data points
        recent_data = data_list[-10:]  # Last 10 data points

        snapshot_data = {
            "event_type": "dashboard_snapshot",
            "dashboard_type": dashboard_type.value,
            "data_points": [
                {
                    "timestamp": data.timestamp,
                    "data": data.data,
                    "metadata": data.metadata,
                }
                for data in recent_data
            ],
        }

        # This would be sent to the specific WebSocket connection
        # Implementation would depend on WebSocket manager integration

    async def _cleanup_loop(self) -> None:
        """Background task to clean up old dashboard data."""
        while self.is_running:
            try:
                current_time = time.time()
                cutoff_time = current_time - self.config.cleanup_interval

                for dashboard_type, data_list in self.dashboard_data.items():
                    # Remove old data points
                    self.dashboard_data[dashboard_type] = [
                        data for data in data_list if data.timestamp > cutoff_time
                    ]

                await asyncio.sleep(self.config.cleanup_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in dashboard cleanup loop: {e}")

    def _determine_health_status(self, metrics: dict[str, Any]) -> str:
        """Determine overall system health status."""
        cpu_usage = metrics.get("cpu_usage", 0.0)
        memory_usage = metrics.get("memory_usage", 0.0)

        if cpu_usage > 90 or memory_usage > 90:
            return "critical"
        elif cpu_usage > 70 or memory_usage > 70:
            return "warning"
        else:
            return "healthy"

    def _calculate_performance_summary(
        self, agent_metrics: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate performance summary from agent metrics."""
        if not agent_metrics:
            return {
                "avg_response_time": 0.0,
                "total_throughput": 0.0,
                "avg_error_rate": 0.0,
            }

        response_times = [
            m.get("response_time_avg", 0.0) for m in agent_metrics.values()
        ]
        throughputs = [m.get("throughput_rps", 0.0) for m in agent_metrics.values()]
        error_rates = [m.get("error_rate", 0.0) for m in agent_metrics.values()]

        return {
            "avg_response_time": sum(response_times) / len(response_times),
            "total_throughput": sum(throughputs),
            "avg_error_rate": sum(error_rates) / len(error_rates),
        }

    async def _handle_alert_notification(self, alert):
        """Handle alert notifications from the alert manager."""
        if not ALERTING_AVAILABLE:
            return

        try:
            # Create alert dashboard data
            alert_data = DashboardData(
                dashboard_type=DashboardType.ALERTS,
                timestamp=time.time(),
                data={
                    "rule_name": alert.rule_name,
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                    "message": alert.message,
                    "value": alert.value,
                    "threshold": alert.threshold,
                    "started_at": alert.started_at.isoformat(),
                    "resolved_at": (
                        alert.resolved_at.isoformat() if alert.resolved_at else None
                    ),
                    "labels": alert.labels,
                    "annotations": alert.annotations,
                },
                metadata={
                    "alert_id": f"{alert.rule_name}_{hash(str(sorted(alert.labels.items())))}"
                },
            )

            # Store alert data
            self.dashboard_data[DashboardType.ALERTS].append(alert_data)

            # Broadcast to subscribers
            await self._broadcast_dashboard_update(DashboardType.ALERTS, alert_data)

        except Exception as e:
            logger.error(f"Error handling alert notification: {e}")

    async def _update_alerts_data(self) -> None:
        """Update alerts dashboard data."""
        if not self.alert_manager:
            return

        try:
            # Get active alerts
            active_alerts = self.alert_manager.get_active_alerts()

            dashboard_data = DashboardData(
                dashboard_type=DashboardType.ALERTS,
                timestamp=time.time(),
                data={
                    "active_alerts_count": len(active_alerts),
                    "critical_alerts": len(
                        [a for a in active_alerts if a.severity.value == "critical"]
                    ),
                    "warning_alerts": len(
                        [a for a in active_alerts if a.severity.value == "warning"]
                    ),
                    "active_alerts": [
                        {
                            "rule_name": alert.rule_name,
                            "severity": alert.severity.value,
                            "message": alert.message,
                            "started_at": alert.started_at.isoformat(),
                            "labels": alert.labels,
                        }
                        for alert in active_alerts[:10]  # Limit to 10 most recent
                    ],
                },
                metadata={
                    "update_count": self.update_counts.get(DashboardType.ALERTS, 0)
                },
            )

            self.dashboard_data[DashboardType.ALERTS].append(dashboard_data)
            await self._broadcast_dashboard_update(DashboardType.ALERTS, dashboard_data)

        except Exception as e:
            logger.error(f"Error updating alerts data: {e}")

    def get_dashboard_status(self) -> dict[str, Any]:
        """Get dashboard manager status."""
        status = {
            "enabled": self.config.enabled,
            "running": self.is_running,
            "active_subscriptions": len(self.active_subscriptions),
            "dashboard_data_points": {
                dashboard_type.value: len(data_list)
                for dashboard_type, data_list in self.dashboard_data.items()
            },
            "alerting_enabled": ALERTING_AVAILABLE and self.alert_manager is not None,
        }

        if self.alert_manager:
            active_alerts = self.alert_manager.get_active_alerts()
            status["active_alerts_count"] = len(active_alerts)
            status["critical_alerts_count"] = len(
                [a for a in active_alerts if a.severity.value == "critical"]
            )

        status["update_counts"] = {
            dashboard_type.value: count
            for dashboard_type, count in self.update_counts.items()
        }
        status["last_update_times"] = {
            dashboard_type.value: timestamp
            for dashboard_type, timestamp in self.last_update_times.items()
        }

        return status
