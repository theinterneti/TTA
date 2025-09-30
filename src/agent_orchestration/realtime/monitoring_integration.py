"""
Integration between monitoring system and real-time event broadcasting.

This module connects the monitoring system from Task 16.2 with the real-time
WebSocket event system to provide live system health dashboards.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass

from .event_publisher import EventPublisher
from .models import SystemMetricsEvent, AgentStatusEvent, EventType, AgentStatus, create_system_metrics_event
from ..monitoring import SystemMonitor, AgentMonitor, AlertManager
from ..performance.response_time_monitor import ResponseTimeMonitor, get_response_time_monitor
from ..performance.analytics import PerformanceAnalytics
from ..performance.alerting import PerformanceAlerting, Alert

logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """Configuration for monitoring integration."""
    enabled: bool = True
    metrics_interval: float = 5.0  # seconds
    alert_broadcast: bool = True
    system_metrics_broadcast: bool = True
    agent_metrics_broadcast: bool = True
    performance_threshold_broadcast: bool = True


class MonitoringEventIntegrator:
    """Integrates monitoring system with real-time event broadcasting."""
    
    def __init__(
        self,
        event_publisher: Optional[EventPublisher] = None,
        system_monitor: Optional[SystemMonitor] = None,
        alert_manager: Optional[AlertManager] = None,
        response_time_monitor: Optional[ResponseTimeMonitor] = None,
        performance_analytics: Optional[PerformanceAnalytics] = None,
        performance_alerting: Optional[PerformanceAlerting] = None,
        config: Optional[MonitoringConfig] = None
    ):
        self.event_publisher = event_publisher
        self.system_monitor = system_monitor
        self.alert_manager = alert_manager
        self.response_time_monitor = response_time_monitor or get_response_time_monitor()
        self.performance_analytics = performance_analytics
        self.performance_alerting = performance_alerting
        self.config = config or MonitoringConfig()
        
        # State tracking
        self.is_running = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.last_metrics_time = 0.0
        
        # Agent monitors
        self.agent_monitors: Dict[str, AgentMonitor] = {}
        
        # Alert handlers
        self.alert_handlers: List[Callable] = []
        
        logger.info(f"MonitoringEventIntegrator initialized, enabled: {self.config.enabled}")
    
    async def start(self) -> None:
        """Start monitoring integration."""
        if not self.config.enabled or self.is_running:
            return
        
        if not self.event_publisher:
            logger.warning("No event publisher available, monitoring integration disabled")
            return
        
        self.is_running = True
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        # Set up alert handler
        if self.alert_manager:
            self.alert_manager.add_handler(self._handle_alert)

        # Set up performance alert handler
        if self.performance_alerting:
            self.performance_alerting.add_alert_handler(self._handle_performance_alert)

        logger.info("Monitoring event integration started")
    
    async def stop(self) -> None:
        """Stop monitoring integration."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Monitoring event integration stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop that broadcasts metrics."""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Check if it's time to broadcast metrics
                if current_time - self.last_metrics_time >= self.config.metrics_interval:
                    await self._broadcast_system_metrics()
                    await self._broadcast_agent_metrics()
                    await self._broadcast_performance_metrics()
                    self.last_metrics_time = current_time
                
                # Sleep for a short interval
                await asyncio.sleep(1.0)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5.0)  # Back off on error
    
    async def _broadcast_system_metrics(self) -> None:
        """Broadcast system metrics as real-time events."""
        if not self.config.system_metrics_broadcast or not self.system_monitor:
            return
        
        try:
            # Get system metrics
            metrics = self.system_monitor.get_system_metrics()
            
            # Create system metrics event
            event = SystemMetricsEvent(
                cpu_usage=metrics.get("cpu_usage", 0.0),
                memory_usage=metrics.get("memory_usage", 0.0),
                active_connections=metrics.get("active_connections", 0),
                queue_depth=metrics.get("queue_depth", 0),
                response_time_avg=metrics.get("response_time_avg", 0.0),
                error_rate=metrics.get("error_rate", 0.0),
                throughput_rps=metrics.get("throughput_rps", 0.0),
                metadata={
                    "disk_usage": metrics.get("disk_usage", 0.0),
                    "network_io": metrics.get("network_io", {}),
                    "process_count": metrics.get("process_count", 0),
                    "uptime": metrics.get("uptime", 0.0)
                },
                source="monitoring_system"
            )
            
            # Publish event
            await self.event_publisher.publish_event(event)
            
        except Exception as e:
            logger.error(f"Failed to broadcast system metrics: {e}")
    
    async def _broadcast_agent_metrics(self) -> None:
        """Broadcast agent-specific metrics as real-time events."""
        if not self.config.agent_metrics_broadcast:
            return
        
        try:
            # Broadcast metrics for each agent monitor
            for agent_id, agent_monitor in self.agent_monitors.items():
                metrics = agent_monitor.get_metrics()
                
                # Determine agent status based on metrics
                status = self._determine_agent_status(metrics)
                
                # Create agent status event
                event = AgentStatusEvent(
                    agent_id=agent_id,
                    status=status,
                    message=f"Agent metrics update",
                    metadata={
                        "response_time_avg": metrics.get("response_time_avg", 0.0),
                        "error_rate": metrics.get("error_rate", 0.0),
                        "throughput_rps": metrics.get("throughput_rps", 0.0),
                        "queue_depth": metrics.get("queue_depth", 0),
                        "memory_usage": metrics.get("memory_usage", 0.0),
                        "last_activity": metrics.get("last_activity", 0.0)
                    },
                    source="monitoring_system"
                )
                
                # Publish event
                await self.event_publisher.publish_event(event)
                
        except Exception as e:
            logger.error(f"Failed to broadcast agent metrics: {e}")
    
    def _determine_agent_status(self, metrics: Dict[str, Any]) -> AgentStatus:
        """Determine agent status based on metrics."""
        error_rate = metrics.get("error_rate", 0.0)
        response_time = metrics.get("response_time_avg", 0.0)
        last_activity = metrics.get("last_activity", 0.0)
        
        # Check if agent is inactive
        if time.time() - last_activity > 300:  # 5 minutes
            return AgentStatus.IDLE
        
        # Check for high error rate
        if error_rate > 0.2:  # 20% error rate
            return AgentStatus.ERROR
        
        # Check for slow response times
        if response_time > 30.0:  # 30 seconds
            return AgentStatus.BUSY  # Use BUSY instead of non-existent DEGRADED

        # Check if actively processing
        if last_activity > time.time() - 60:  # Active in last minute
            return AgentStatus.BUSY  # Use BUSY instead of non-existent PROCESSING

        return AgentStatus.IDLE
    
    async def _handle_alert(self, alert: Dict[str, Any]) -> None:
        """Handle alerts from the alert manager."""
        if not self.config.alert_broadcast:
            return
        
        try:
            # Determine event type based on alert
            if alert.get("type") == "system":
                event = SystemMetricsEvent(
                    cpu_usage=alert.get("cpu_usage", 0.0),
                    memory_usage=alert.get("memory_usage", 0.0),
                    active_connections=alert.get("active_connections", 0),
                    queue_depth=alert.get("queue_depth", 0),
                    metadata={
                        "alert": True,
                        "alert_message": alert.get("message", ""),
                        "alert_severity": alert.get("severity", "unknown"),
                        "alert_timestamp": alert.get("timestamp", time.time())
                    },
                    source="alert_manager"
                )
            else:
                # Agent-specific alert
                agent_id = alert.get("agent_id", "unknown")
                event = AgentStatusEvent(
                    agent_id=agent_id,
                    status=AgentStatus.ERROR,
                    message=alert.get("message", "Alert triggered"),
                    metadata={
                        "alert": True,
                        "alert_severity": alert.get("severity", "unknown"),
                        "alert_timestamp": alert.get("timestamp", time.time()),
                        **alert.get("details", {})
                    },
                    source="alert_manager"
                )
            
            # Publish alert event
            await self.event_publisher.publish_event(event)
            
        except Exception as e:
            logger.error(f"Failed to broadcast alert: {e}")

    async def _broadcast_performance_metrics(self) -> None:
        """Broadcast performance metrics as real-time events."""
        if not self.config.system_metrics_broadcast or not self.response_time_monitor:
            return

        try:
            # Get performance summary
            performance_summary = self.response_time_monitor.get_performance_summary()

            # Create performance metrics event
            event = create_system_metrics_event(
                cpu_usage=0.0,  # Will be filled by system monitor
                memory_usage=0.0,  # Will be filled by system monitor
                active_connections=performance_summary.get("active_operations", 0),
                queue_depth=0,  # Will be filled by system monitor
                metadata={
                    "performance_metrics": True,
                    "total_operations": performance_summary.get("total_operations", 0),
                    "overall_performance": performance_summary.get("overall_performance", "unknown"),
                    "sla_compliance": performance_summary.get("sla_compliance", 0.0),
                    "operation_types": performance_summary.get("operation_types", 0),
                    "statistics_by_type": performance_summary.get("statistics_by_type", {})
                }
            )

            # Publish event
            await self.event_publisher.publish_event(event)

        except Exception as e:
            logger.error(f"Failed to broadcast performance metrics: {e}")

    async def _handle_performance_alert(self, alert: Alert) -> None:
        """Handle performance alerts and broadcast them."""
        if not self.config.alert_broadcast:
            return

        try:
            # Create alert event based on alert type
            if alert.operation_type:
                # Agent-specific performance alert
                event = AgentStatusEvent(
                    agent_id=f"performance_{alert.operation_type.value}",
                    status=AgentStatus.ERROR if alert.severity.value in ["error", "critical"] else AgentStatus.DEGRADED,
                    message=alert.description,
                    metadata={
                        "alert": True,
                        "alert_id": alert.alert_id,
                        "alert_type": alert.alert_type.value,
                        "alert_severity": alert.severity.value,
                        "metric_value": alert.metric_value,
                        "threshold_value": alert.threshold_value,
                        "escalation_level": alert.escalation_level.value,
                        "escalation_count": alert.escalation_count,
                        **alert.metadata
                    },
                    source="performance_alerting"
                )
            else:
                # System-wide performance alert
                event = create_system_metrics_event(
                    cpu_usage=0.0,
                    memory_usage=0.0,
                    active_connections=0,
                    queue_depth=0,
                    metadata={
                        "alert": True,
                        "alert_id": alert.alert_id,
                        "alert_type": alert.alert_type.value,
                        "alert_severity": alert.severity.value,
                        "alert_title": alert.title,
                        "alert_description": alert.description,
                        "metric_value": alert.metric_value,
                        "threshold_value": alert.threshold_value,
                        **alert.metadata
                    }
                )

            # Publish alert event
            await self.event_publisher.publish_event(event)

        except Exception as e:
            logger.error(f"Failed to broadcast performance alert: {e}")

    async def broadcast_performance_analysis(self, analysis_results: Dict[str, Any]) -> None:
        """Broadcast performance analysis results."""
        if not self.event_publisher:
            return

        try:
            # Create performance analysis event
            event = create_system_metrics_event(
                cpu_usage=0.0,
                memory_usage=0.0,
                active_connections=0,
                queue_depth=0,
                metadata={
                    "performance_analysis": True,
                    "analysis_timestamp": analysis_results.get("analysis_timestamp", time.time()),
                    "overall_health": analysis_results.get("overall_health", "unknown"),
                    "bottlenecks_count": len(analysis_results.get("bottlenecks", [])),
                    "trends_count": len(analysis_results.get("trends", [])),
                    "recommendations_count": len(analysis_results.get("recommendations", [])),
                    "bottlenecks": analysis_results.get("bottlenecks", []),
                    "trends": analysis_results.get("trends", []),
                    "recommendations": analysis_results.get("recommendations", [])
                }
            )

            await self.event_publisher.publish_event(event)

        except Exception as e:
            logger.error(f"Failed to broadcast performance analysis: {e}")

    def add_agent_monitor(self, agent_id: str, agent_monitor: AgentMonitor) -> None:
        """Add an agent monitor for real-time tracking."""
        self.agent_monitors[agent_id] = agent_monitor
        logger.debug(f"Added agent monitor for {agent_id}")
    
    def remove_agent_monitor(self, agent_id: str) -> None:
        """Remove an agent monitor."""
        self.agent_monitors.pop(agent_id, None)
        logger.debug(f"Removed agent monitor for {agent_id}")
    
    def add_alert_handler(self, handler: Callable) -> None:
        """Add custom alert handler."""
        self.alert_handlers.append(handler)
    
    async def broadcast_performance_threshold_event(
        self,
        threshold_type: str,
        current_value: float,
        threshold_value: float,
        agent_id: Optional[str] = None
    ) -> None:
        """Broadcast performance threshold breach event."""
        if not self.config.performance_threshold_broadcast:
            return
        
        try:
            if agent_id:
                # Agent-specific threshold breach
                event = AgentStatusEvent(
                    agent_id=agent_id,
                    status=AgentStatus.DEGRADED,
                    message=f"Performance threshold breached: {threshold_type}",
                    metadata={
                        "threshold_type": threshold_type,
                        "current_value": current_value,
                        "threshold_value": threshold_value,
                        "breach_ratio": current_value / threshold_value if threshold_value > 0 else 0
                    },
                    source="performance_monitor"
                )
            else:
                # System-wide threshold breach
                event = SystemMetricsEvent(
                    cpu_usage=current_value if threshold_type == "cpu" else 0.0,
                    memory_usage=current_value if threshold_type == "memory" else 0.0,
                    active_connections=int(current_value) if threshold_type == "connections" else 0,
                    queue_depth=int(current_value) if threshold_type == "queue" else 0,
                    metadata={
                        "threshold_breach": True,
                        "threshold_type": threshold_type,
                        "current_value": current_value,
                        "threshold_value": threshold_value
                    },
                    source="performance_monitor"
                )
            
            await self.event_publisher.publish_event(event)
            
        except Exception as e:
            logger.error(f"Failed to broadcast performance threshold event: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring integration status."""
        return {
            "enabled": self.config.enabled,
            "running": self.is_running,
            "metrics_interval": self.config.metrics_interval,
            "last_metrics_time": self.last_metrics_time,
            "agent_monitors_count": len(self.agent_monitors),
            "alert_handlers_count": len(self.alert_handlers),
            "event_publisher_available": self.event_publisher is not None,
            "system_monitor_available": self.system_monitor is not None,
            "alert_manager_available": self.alert_manager is not None
        }


# Global monitoring integrator
_monitoring_integrator: Optional[MonitoringEventIntegrator] = None


def get_monitoring_event_integrator(
    event_publisher: Optional[EventPublisher] = None,
    system_monitor: Optional[SystemMonitor] = None,
    alert_manager: Optional[AlertManager] = None,
    config: Optional[MonitoringConfig] = None
) -> MonitoringEventIntegrator:
    """Get or create monitoring event integrator."""
    global _monitoring_integrator
    
    if _monitoring_integrator is None or event_publisher is not None:
        _monitoring_integrator = MonitoringEventIntegrator(
            event_publisher=event_publisher,
            system_monitor=system_monitor,
            alert_manager=alert_manager,
            config=config
        )
    
    return _monitoring_integrator
