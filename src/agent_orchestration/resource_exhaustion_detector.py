"""
Resource exhaustion detection with configurable thresholds.

Provides comprehensive resource monitoring and exhaustion detection
that integrates with workflow error handling and circuit breaker systems.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

import psutil

logger = logging.getLogger(__name__)


@dataclass
class ResourceThresholds:
    """Configurable resource thresholds for exhaustion detection."""

    # Memory thresholds (percentage)
    memory_warning_percent: float = 75.0
    memory_critical_percent: float = 80.0
    memory_exhaustion_percent: float = 90.0

    # CPU thresholds (percentage)
    cpu_warning_percent: float = 75.0
    cpu_critical_percent: float = 90.0
    cpu_exhaustion_percent: float = 95.0

    # Disk thresholds (percentage used)
    disk_warning_percent: float = 75.0
    disk_critical_percent: float = 85.0
    disk_exhaustion_percent: float = 90.0

    # Early warning threshold (percentage of critical threshold)
    early_warning_percent: float = 75.0

    # Sustained threshold duration (seconds)
    sustained_duration_seconds: float = 30.0

    def validate(self) -> list[str]:
        """Validate threshold configuration."""
        errors = []

        # Check memory thresholds
        if not (
            0
            < self.memory_warning_percent
            < self.memory_critical_percent
            < self.memory_exhaustion_percent
            <= 100
        ):
            errors.append(
                "Memory thresholds must be: 0 < warning < critical < exhaustion <= 100"
            )

        # Check CPU thresholds
        if not (
            0
            < self.cpu_warning_percent
            < self.cpu_critical_percent
            < self.cpu_exhaustion_percent
            <= 100
        ):
            errors.append(
                "CPU thresholds must be: 0 < warning < critical < exhaustion <= 100"
            )

        # Check disk thresholds
        if not (
            0
            < self.disk_warning_percent
            < self.disk_critical_percent
            < self.disk_exhaustion_percent
            <= 100
        ):
            errors.append(
                "Disk thresholds must be: 0 < warning < critical < exhaustion <= 100"
            )

        # Check early warning percentage
        if not (0 < self.early_warning_percent < 100):
            errors.append("Early warning percent must be between 0 and 100")

        # Check sustained duration
        if self.sustained_duration_seconds <= 0:
            errors.append("Sustained duration must be positive")

        return errors


@dataclass
class ResourceExhaustionEvent:
    """Represents a resource exhaustion event."""

    timestamp: float
    resource_type: str  # 'memory', 'cpu', 'disk'
    current_value: float
    threshold_value: float
    severity: str  # 'warning', 'critical', 'exhaustion'
    sustained_duration: float = 0.0
    additional_info: dict[str, Any] = field(default_factory=dict)


class ResourceExhaustionDetector:
    """
    Detects resource exhaustion with configurable thresholds and sustained monitoring.

    Provides early warning, critical, and exhaustion level detection with
    integration for workflow error handling and circuit breaker systems.
    """

    def __init__(
        self,
        thresholds: ResourceThresholds | None = None,
        check_interval_seconds: float = 5.0,
        circuit_breaker_registry: Any = None,
    ) -> None:
        self.thresholds = thresholds or ResourceThresholds()
        self.check_interval_seconds = check_interval_seconds
        self._circuit_breaker_registry = circuit_breaker_registry

        # Validation
        validation_errors = self.thresholds.validate()
        if validation_errors:
            logger.error(f"Resource threshold validation failed: {validation_errors}")
            raise ValueError(f"Invalid resource thresholds: {validation_errors}")

        # State tracking
        self._monitoring_task: asyncio.Task | None = None
        self._resource_history: dict[str, list[float]] = {
            "memory": [],
            "cpu": [],
            "disk": [],
        }
        self._threshold_breach_times: dict[str, float | None] = {
            "memory": None,
            "cpu": None,
            "disk": None,
        }
        self._last_exhaustion_events: dict[str, ResourceExhaustionEvent | None] = {
            "memory": None,
            "cpu": None,
            "disk": None,
        }

        # Callbacks
        self._exhaustion_callbacks: list[
            Callable[[ResourceExhaustionEvent], Awaitable[None]]
        ] = []
        self._warning_callbacks: list[
            Callable[[ResourceExhaustionEvent], Awaitable[None]]
        ] = []

        # Statistics
        self._total_checks = 0
        self._warning_events = 0
        self._critical_events = 0
        self._exhaustion_events = 0

    async def start_monitoring(self) -> None:
        """Start continuous resource monitoring."""
        if self._monitoring_task and not self._monitoring_task.done():
            logger.warning("Resource exhaustion monitoring already running")
            return

        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started resource exhaustion monitoring")

    async def stop_monitoring(self) -> None:
        """Stop continuous resource monitoring."""
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._monitoring_task
        logger.info("Stopped resource exhaustion monitoring")

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while True:
            try:
                await self.check_resource_exhaustion()
                await asyncio.sleep(self.check_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Resource exhaustion monitoring error: {e}")
                await asyncio.sleep(self.check_interval_seconds)

    async def check_resource_exhaustion(self) -> list[ResourceExhaustionEvent]:
        """Check for resource exhaustion and return any detected events."""
        self._total_checks += 1
        current_time = time.time()
        events = []

        try:
            # Get current resource usage
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent(interval=0.1)
            disk_percent = psutil.disk_usage("/").percent

            # Check each resource type
            events.extend(
                await self._check_resource_type(
                    "memory",
                    memory_percent,
                    current_time,
                    self.thresholds.memory_warning_percent,
                    self.thresholds.memory_critical_percent,
                    self.thresholds.memory_exhaustion_percent,
                )
            )

            events.extend(
                await self._check_resource_type(
                    "cpu",
                    cpu_percent,
                    current_time,
                    self.thresholds.cpu_warning_percent,
                    self.thresholds.cpu_critical_percent,
                    self.thresholds.cpu_exhaustion_percent,
                )
            )

            events.extend(
                await self._check_resource_type(
                    "disk",
                    disk_percent,
                    current_time,
                    self.thresholds.disk_warning_percent,
                    self.thresholds.disk_critical_percent,
                    self.thresholds.disk_exhaustion_percent,
                )
            )

        except Exception as e:
            logger.error(f"Failed to check resource exhaustion: {e}")

        return events

    async def _check_resource_type(
        self,
        resource_type: str,
        current_value: float,
        current_time: float,
        warning_threshold: float,
        critical_threshold: float,
        exhaustion_threshold: float,
    ) -> list[ResourceExhaustionEvent]:
        """Check exhaustion for a specific resource type."""
        events = []

        # Update history
        history = self._resource_history[resource_type]
        history.append(current_value)
        # Keep only last 100 readings
        if len(history) > 100:
            history.pop(0)

        # Determine severity level
        severity = None
        threshold_value = 0.0

        if current_value >= exhaustion_threshold:
            severity = "exhaustion"
            threshold_value = exhaustion_threshold
            self._exhaustion_events += 1
        elif current_value >= critical_threshold:
            severity = "critical"
            threshold_value = critical_threshold
            self._critical_events += 1
        elif current_value >= warning_threshold:
            severity = "warning"
            threshold_value = warning_threshold
            self._warning_events += 1

        if severity:
            # Check for sustained threshold breach
            breach_time = self._threshold_breach_times[resource_type]
            if breach_time is None:
                # First time breaching threshold
                self._threshold_breach_times[resource_type] = current_time
                sustained_duration = 0.0
            else:
                sustained_duration = current_time - breach_time

            # Create event
            event = ResourceExhaustionEvent(
                timestamp=current_time,
                resource_type=resource_type,
                current_value=current_value,
                threshold_value=threshold_value,
                severity=severity,
                sustained_duration=sustained_duration,
                additional_info={
                    "history_avg": sum(history) / len(history) if history else 0.0,
                    "history_max": max(history) if history else 0.0,
                    "trend": self._calculate_trend(history),
                },
            )

            events.append(event)
            self._last_exhaustion_events[resource_type] = event

            # Log event
            logger.log(
                (
                    logging.ERROR
                    if severity == "exhaustion"
                    else logging.WARNING
                    if severity == "critical"
                    else logging.INFO
                ),
                f"Resource {severity}: {resource_type} at {current_value:.1f}% (threshold: {threshold_value:.1f}%)",
                extra={
                    "resource_type": resource_type,
                    "current_value": current_value,
                    "threshold_value": threshold_value,
                    "severity": severity,
                    "sustained_duration": sustained_duration,
                    "event_type": f"resource_{severity}",
                },
            )

            # Trigger callbacks and circuit breakers for sustained exhaustion
            if (
                severity == "exhaustion"
                and sustained_duration >= self.thresholds.sustained_duration_seconds
            ):
                await self._handle_sustained_exhaustion(event)
            elif severity in ["warning", "critical"]:
                await self._handle_resource_warning(event)

        else:
            # Reset breach time if no longer breaching
            self._threshold_breach_times[resource_type] = None

        return events

    def _calculate_trend(self, history: list[float]) -> str:
        """Calculate resource usage trend from history."""
        if len(history) < 3:
            return "stable"

        recent = history[-3:]
        if all(recent[i] > recent[i - 1] for i in range(1, len(recent))):
            return "increasing"
        if all(recent[i] < recent[i - 1] for i in range(1, len(recent))):
            return "decreasing"
        return "stable"

    async def _handle_sustained_exhaustion(
        self, event: ResourceExhaustionEvent
    ) -> None:
        """Handle sustained resource exhaustion."""
        logger.error(
            f"Sustained resource exhaustion detected: {event.resource_type}",
            extra={
                "event": event.__dict__,
                "event_type": "sustained_resource_exhaustion",
            },
        )

        # Trigger exhaustion callbacks
        for callback in self._exhaustion_callbacks:
            try:
                await callback(event)
            except Exception as e:
                logger.warning(f"Exhaustion callback failed: {e}")

        # Trigger circuit breakers if registry is available
        if self._circuit_breaker_registry:
            await self._trigger_circuit_breakers_for_exhaustion(event)

    async def _handle_resource_warning(self, event: ResourceExhaustionEvent) -> None:
        """Handle resource warning events."""
        # Trigger warning callbacks
        for callback in self._warning_callbacks:
            try:
                await callback(event)
            except Exception as e:
                logger.warning(f"Warning callback failed: {e}")

    async def _trigger_circuit_breakers_for_exhaustion(
        self, event: ResourceExhaustionEvent
    ) -> None:
        """Trigger circuit breakers when sustained exhaustion is detected."""
        try:
            # Get all workflow circuit breakers
            all_metrics = await self._circuit_breaker_registry.get_all_metrics()

            for cb_name in all_metrics:
                if cb_name.startswith("workflow:"):
                    circuit_breaker = await self._circuit_breaker_registry.get(cb_name)
                    if circuit_breaker:
                        await circuit_breaker._transition_to_open()
                        logger.warning(
                            f"Opened circuit breaker {cb_name} due to sustained {event.resource_type} exhaustion"
                        )
        except Exception as e:
            logger.error(f"Failed to trigger circuit breakers for exhaustion: {e}")

    # ---- Callback management ----
    def register_exhaustion_callback(
        self, callback: Callable[[ResourceExhaustionEvent], Awaitable[None]]
    ) -> None:
        """Register callback for exhaustion events."""
        self._exhaustion_callbacks.append(callback)

    def register_warning_callback(
        self, callback: Callable[[ResourceExhaustionEvent], Awaitable[None]]
    ) -> None:
        """Register callback for warning events."""
        self._warning_callbacks.append(callback)

    def unregister_exhaustion_callback(
        self, callback: Callable[[ResourceExhaustionEvent], Awaitable[None]]
    ) -> bool:
        """Unregister exhaustion callback."""
        try:
            self._exhaustion_callbacks.remove(callback)
            return True
        except ValueError:
            return False

    def unregister_warning_callback(
        self, callback: Callable[[ResourceExhaustionEvent], Awaitable[None]]
    ) -> bool:
        """Unregister warning callback."""
        try:
            self._warning_callbacks.remove(callback)
            return True
        except ValueError:
            return False

    # ---- Status and metrics ----
    def get_current_status(self) -> dict[str, Any]:
        """Get current resource exhaustion detector status."""
        try:
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent(interval=0.1)
            disk_percent = psutil.disk_usage("/").percent
        except Exception:
            memory_percent = cpu_percent = disk_percent = 0.0

        return {
            "monitoring_active": self._monitoring_task is not None
            and not self._monitoring_task.done(),
            "current_usage": {
                "memory_percent": memory_percent,
                "cpu_percent": cpu_percent,
                "disk_percent": disk_percent,
            },
            "thresholds": {
                "memory": {
                    "warning": self.thresholds.memory_warning_percent,
                    "critical": self.thresholds.memory_critical_percent,
                    "exhaustion": self.thresholds.memory_exhaustion_percent,
                },
                "cpu": {
                    "warning": self.thresholds.cpu_warning_percent,
                    "critical": self.thresholds.cpu_critical_percent,
                    "exhaustion": self.thresholds.cpu_exhaustion_percent,
                },
                "disk": {
                    "warning": self.thresholds.disk_warning_percent,
                    "critical": self.thresholds.disk_critical_percent,
                    "exhaustion": self.thresholds.disk_exhaustion_percent,
                },
            },
            "statistics": {
                "total_checks": self._total_checks,
                "warning_events": self._warning_events,
                "critical_events": self._critical_events,
                "exhaustion_events": self._exhaustion_events,
            },
            "last_events": {
                resource: event.__dict__ if event else None
                for resource, event in self._last_exhaustion_events.items()
            },
        }
