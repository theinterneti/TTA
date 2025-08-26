"""
Comprehensive monitoring and metrics for agent communication.

This module provides detailed monitoring capabilities for real agent communication,
including performance metrics, health checks, and alerting.
"""
from __future__ import annotations

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Metrics for individual agent performance."""
    agent_type: str
    agent_instance: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    last_request_time: Optional[float] = None
    error_rate: float = 0.0
    average_response_time: float = 0.0
    requests_per_second: float = 0.0
    recent_response_times: deque = field(default_factory=lambda: deque(maxlen=100))


@dataclass
class SystemMetrics:
    """System-wide metrics for agent coordination."""
    total_workflows: int = 0
    successful_workflows: int = 0
    failed_workflows: int = 0
    average_workflow_time: float = 0.0
    concurrent_workflows: int = 0
    peak_concurrent_workflows: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0
    queue_depth: int = 0


@dataclass
class HealthStatus:
    """Health status for agent or system component."""
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    last_check: datetime
    response_time_ms: float
    error_count: int
    details: Dict[str, Any] = field(default_factory=dict)


class AgentMonitor:
    """Monitor for individual agent performance and health."""
    
    def __init__(self, agent_type: str, agent_instance: str):
        self.metrics = AgentMetrics(agent_type, agent_instance)
        self._lock = threading.Lock()
        self._start_time = time.time()
    
    def record_request(self, response_time: float, success: bool, error: Optional[str] = None):
        """Record a request and its outcome."""
        with self._lock:
            self.metrics.total_requests += 1
            self.metrics.last_request_time = time.time()
            
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
            
            # Update response time metrics
            self.metrics.total_response_time += response_time
            self.metrics.min_response_time = min(self.metrics.min_response_time, response_time)
            self.metrics.max_response_time = max(self.metrics.max_response_time, response_time)
            self.metrics.recent_response_times.append(response_time)
            
            # Calculate derived metrics
            if self.metrics.total_requests > 0:
                self.metrics.error_rate = self.metrics.failed_requests / self.metrics.total_requests
                self.metrics.average_response_time = self.metrics.total_response_time / self.metrics.total_requests
                
                # Calculate RPS over the monitoring period
                elapsed_time = time.time() - self._start_time
                if elapsed_time > 0:
                    self.metrics.requests_per_second = self.metrics.total_requests / elapsed_time
    
    def get_current_metrics(self) -> AgentMetrics:
        """Get current metrics snapshot."""
        with self._lock:
            return AgentMetrics(
                agent_type=self.metrics.agent_type,
                agent_instance=self.metrics.agent_instance,
                total_requests=self.metrics.total_requests,
                successful_requests=self.metrics.successful_requests,
                failed_requests=self.metrics.failed_requests,
                total_response_time=self.metrics.total_response_time,
                min_response_time=self.metrics.min_response_time if self.metrics.min_response_time != float('inf') else 0.0,
                max_response_time=self.metrics.max_response_time,
                last_request_time=self.metrics.last_request_time,
                error_rate=self.metrics.error_rate,
                average_response_time=self.metrics.average_response_time,
                requests_per_second=self.metrics.requests_per_second,
                recent_response_times=self.metrics.recent_response_times.copy()
            )
    
    async def health_check(self, health_check_func: Optional[Callable] = None) -> HealthStatus:
        """Perform health check for this agent."""
        start_time = time.time()
        
        try:
            if health_check_func:
                await health_check_func()
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Determine health status based on metrics
            status = "healthy"
            if self.metrics.error_rate > 0.1:  # More than 10% error rate
                status = "degraded"
            if self.metrics.error_rate > 0.5:  # More than 50% error rate
                status = "unhealthy"
            
            return HealthStatus(
                component=f"{self.metrics.agent_type}:{self.metrics.agent_instance}",
                status=status,
                last_check=datetime.utcnow(),
                response_time_ms=response_time,
                error_count=self.metrics.failed_requests,
                details={
                    "total_requests": self.metrics.total_requests,
                    "error_rate": self.metrics.error_rate,
                    "average_response_time": self.metrics.average_response_time,
                    "requests_per_second": self.metrics.requests_per_second
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthStatus(
                component=f"{self.metrics.agent_type}:{self.metrics.agent_instance}",
                status="unhealthy",
                last_check=datetime.utcnow(),
                response_time_ms=response_time,
                error_count=self.metrics.failed_requests + 1,
                details={"health_check_error": str(e)}
            )


class SystemMonitor:
    """System-wide monitoring for agent coordination."""
    
    def __init__(self):
        self.metrics = SystemMetrics()
        self.agent_monitors: Dict[str, AgentMonitor] = {}
        self._lock = threading.Lock()
        self._workflow_start_times: Dict[str, float] = {}
        
    def get_agent_monitor(self, agent_type: str, agent_instance: str) -> AgentMonitor:
        """Get or create agent monitor."""
        monitor_key = f"{agent_type}:{agent_instance}"
        
        if monitor_key not in self.agent_monitors:
            with self._lock:
                if monitor_key not in self.agent_monitors:
                    self.agent_monitors[monitor_key] = AgentMonitor(agent_type, agent_instance)
        
        return self.agent_monitors[monitor_key]
    
    def start_workflow(self, workflow_id: str):
        """Record the start of a workflow."""
        with self._lock:
            self._workflow_start_times[workflow_id] = time.time()
            self.metrics.concurrent_workflows += 1
            self.metrics.peak_concurrent_workflows = max(
                self.metrics.peak_concurrent_workflows,
                self.metrics.concurrent_workflows
            )
    
    def end_workflow(self, workflow_id: str, success: bool):
        """Record the end of a workflow."""
        with self._lock:
            start_time = self._workflow_start_times.pop(workflow_id, time.time())
            workflow_time = time.time() - start_time
            
            self.metrics.total_workflows += 1
            self.metrics.concurrent_workflows = max(0, self.metrics.concurrent_workflows - 1)
            
            if success:
                self.metrics.successful_workflows += 1
            else:
                self.metrics.failed_workflows += 1
            
            # Update average workflow time
            if self.metrics.total_workflows > 0:
                total_time = self.metrics.average_workflow_time * (self.metrics.total_workflows - 1) + workflow_time
                self.metrics.average_workflow_time = total_time / self.metrics.total_workflows
    
    def update_system_resources(self, memory_mb: float, cpu_percent: float, active_connections: int, queue_depth: int):
        """Update system resource metrics."""
        with self._lock:
            self.metrics.memory_usage_mb = memory_mb
            self.metrics.cpu_usage_percent = cpu_percent
            self.metrics.active_connections = active_connections
            self.metrics.queue_depth = queue_depth
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        with self._lock:
            return SystemMetrics(
                total_workflows=self.metrics.total_workflows,
                successful_workflows=self.metrics.successful_workflows,
                failed_workflows=self.metrics.failed_workflows,
                average_workflow_time=self.metrics.average_workflow_time,
                concurrent_workflows=self.metrics.concurrent_workflows,
                peak_concurrent_workflows=self.metrics.peak_concurrent_workflows,
                memory_usage_mb=self.metrics.memory_usage_mb,
                cpu_usage_percent=self.metrics.cpu_usage_percent,
                active_connections=self.metrics.active_connections,
                queue_depth=self.metrics.queue_depth
            )
    
    def get_all_agent_metrics(self) -> Dict[str, AgentMetrics]:
        """Get metrics for all monitored agents."""
        return {
            monitor_key: monitor.get_current_metrics()
            for monitor_key, monitor in self.agent_monitors.items()
        }
    
    async def system_health_check(self) -> List[HealthStatus]:
        """Perform system-wide health check."""
        health_statuses = []
        
        # Check individual agents
        for monitor_key, monitor in self.agent_monitors.items():
            agent_health = await monitor.health_check()
            health_statuses.append(agent_health)
        
        # Check system-level health
        system_status = "healthy"
        if self.metrics.memory_usage_mb > 1000:  # More than 1GB
            system_status = "degraded"
        if self.metrics.memory_usage_mb > 2000:  # More than 2GB
            system_status = "unhealthy"
        
        system_health = HealthStatus(
            component="system",
            status=system_status,
            last_check=datetime.utcnow(),
            response_time_ms=0.0,
            error_count=self.metrics.failed_workflows,
            details={
                "total_workflows": self.metrics.total_workflows,
                "concurrent_workflows": self.metrics.concurrent_workflows,
                "memory_usage_mb": self.metrics.memory_usage_mb,
                "cpu_usage_percent": self.metrics.cpu_usage_percent,
                "queue_depth": self.metrics.queue_depth
            }
        )
        
        health_statuses.append(system_health)
        return health_statuses


class AlertManager:
    """Manage alerts based on monitoring metrics."""
    
    def __init__(self, alert_handlers: Optional[List[Callable]] = None):
        self.alert_handlers = alert_handlers or []
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def add_alert_handler(self, handler: Callable):
        """Add an alert handler function."""
        self.alert_handlers.append(handler)
    
    async def check_alerts(self, system_monitor: SystemMonitor):
        """Check for alert conditions and trigger alerts."""
        system_metrics = system_monitor.get_system_metrics()
        agent_metrics = system_monitor.get_all_agent_metrics()
        
        alerts_to_trigger = []
        
        # Check system-level alerts
        if system_metrics.memory_usage_mb > 1500:  # High memory usage
            alerts_to_trigger.append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'message': f'High memory usage: {system_metrics.memory_usage_mb:.1f}MB',
                'details': {'memory_mb': system_metrics.memory_usage_mb}
            })
        
        if system_metrics.queue_depth > 100:  # High queue depth
            alerts_to_trigger.append({
                'type': 'high_queue_depth',
                'severity': 'warning',
                'message': f'High queue depth: {system_metrics.queue_depth}',
                'details': {'queue_depth': system_metrics.queue_depth}
            })
        
        # Check agent-level alerts
        for agent_key, metrics in agent_metrics.items():
            if metrics.error_rate > 0.2:  # High error rate
                alerts_to_trigger.append({
                    'type': 'high_error_rate',
                    'severity': 'critical',
                    'message': f'High error rate for {agent_key}: {metrics.error_rate:.1%}',
                    'details': {
                        'agent': agent_key,
                        'error_rate': metrics.error_rate,
                        'failed_requests': metrics.failed_requests
                    }
                })
            
            if metrics.average_response_time > 10.0:  # Slow response time
                alerts_to_trigger.append({
                    'type': 'slow_response_time',
                    'severity': 'warning',
                    'message': f'Slow response time for {agent_key}: {metrics.average_response_time:.2f}s',
                    'details': {
                        'agent': agent_key,
                        'response_time': metrics.average_response_time
                    }
                })
        
        # Trigger alerts
        for alert in alerts_to_trigger:
            await self._trigger_alert(alert)
    
    async def _trigger_alert(self, alert: Dict[str, Any]):
        """Trigger an alert through all registered handlers."""
        alert_key = f"{alert['type']}:{alert.get('details', {}).get('agent', 'system')}"
        
        with self._lock:
            # Check if this alert is already active (avoid spam)
            if alert_key in self.active_alerts:
                last_triggered = self.active_alerts[alert_key].get('last_triggered', 0)
                if time.time() - last_triggered < 300:  # 5-minute cooldown
                    return
            
            # Record alert as active
            self.active_alerts[alert_key] = {
                'alert': alert,
                'last_triggered': time.time()
            }
        
        # Send alert through handlers
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")


# Global system monitor instance
_system_monitor = SystemMonitor()


def get_system_monitor() -> SystemMonitor:
    """Get the global system monitor instance."""
    return _system_monitor
