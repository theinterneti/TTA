"""
Response time alerting system with configurable thresholds and escalation.

This module provides comprehensive alerting for response time violations,
performance degradation, and SLA breaches with escalation workflows.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .analytics import BottleneckIdentification, PerformanceTrend, TrendDirection
from .response_time_monitor import OperationType

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of performance alerts."""

    RESPONSE_TIME_VIOLATION = "response_time_violation"
    SLA_BREACH = "sla_breach"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    BOTTLENECK_DETECTED = "bottleneck_detected"
    TREND_ALERT = "trend_alert"
    SYSTEM_OVERLOAD = "system_overload"
    RECOVERY_NOTIFICATION = "recovery_notification"


class EscalationLevel(int, Enum):
    """Escalation levels for alerts."""

    LEVEL_1 = 1  # Initial alert
    LEVEL_2 = 2  # First escalation
    LEVEL_3 = 3  # Second escalation
    LEVEL_4 = 4  # Critical escalation


@dataclass
class AlertThreshold:
    """Configurable alert threshold."""

    operation_type: OperationType | None = None  # None for global
    metric_name: str = "response_time"
    warning_threshold: float = 1.0
    error_threshold: float = 2.0
    critical_threshold: float = 5.0
    evaluation_window_minutes: int = 5
    min_samples: int = 3
    enabled: bool = True


@dataclass
class Alert:
    """Performance alert."""

    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    operation_type: OperationType | None
    metric_value: float
    threshold_value: float
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)

    # Escalation tracking
    escalation_level: EscalationLevel = EscalationLevel.LEVEL_1
    escalation_count: int = 0
    last_escalation_time: float = 0.0
    acknowledged: bool = False
    resolved: bool = False
    resolution_time: float | None = None


@dataclass
class EscalationRule:
    """Alert escalation rule."""

    alert_type: AlertType
    severity: AlertSeverity
    escalation_delay_minutes: int
    max_escalations: int
    escalation_targets: list[str]  # Target identifiers
    auto_resolve_minutes: int | None = None


class PerformanceAlerting:
    """Comprehensive performance alerting system."""

    def __init__(
        self,
        default_thresholds: list[AlertThreshold] | None = None,
        escalation_rules: list[EscalationRule] | None = None,
    ):
        # Alert configuration
        self.thresholds: list[AlertThreshold] = default_thresholds or self._get_default_thresholds()
        self.escalation_rules: dict[tuple, EscalationRule] = {}

        if escalation_rules:
            for rule in escalation_rules:
                key = (rule.alert_type, rule.severity)
                self.escalation_rules[key] = rule
        else:
            self._setup_default_escalation_rules()

        # Alert state
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: deque[Alert] = deque(maxlen=1000)
        self.suppressed_alerts: set[str] = set()  # Alert IDs to suppress

        # Alert handlers
        self.alert_handlers: list[Callable] = []
        self.escalation_handlers: dict[str, Callable] = {}  # target -> handler

        # Background tasks
        self.escalation_task: asyncio.Task | None = None
        self.cleanup_task: asyncio.Task | None = None
        self.is_running = False

        # Alert statistics
        self.alert_counts: dict[AlertType, int] = defaultdict(int)
        self.escalation_counts: dict[EscalationLevel, int] = defaultdict(int)

        logger.info("PerformanceAlerting initialized")

    async def start(self) -> None:
        """Start the alerting system."""
        if self.is_running:
            return

        self.is_running = True

        # Start background tasks
        self.escalation_task = asyncio.create_task(self._escalation_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("PerformanceAlerting started")

    async def stop(self) -> None:
        """Stop the alerting system."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel background tasks
        for task in [self.escalation_task, self.cleanup_task]:
            if task:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        logger.info("PerformanceAlerting stopped")

    async def evaluate_thresholds(
        self,
        operation_type: OperationType,
        metric_value: float,
        metric_name: str = "response_time",
        metadata: dict[str, Any] | None = None,
    ) -> Alert | None:
        """Evaluate metric against thresholds and generate alert if needed."""
        # Find applicable threshold
        threshold = self._find_threshold(operation_type, metric_name)
        if not threshold or not threshold.enabled:
            return None

        # Determine severity
        severity = None
        threshold_value = None

        if metric_value >= threshold.critical_threshold:
            severity = AlertSeverity.CRITICAL
            threshold_value = threshold.critical_threshold
        elif metric_value >= threshold.error_threshold:
            severity = AlertSeverity.ERROR
            threshold_value = threshold.error_threshold
        elif metric_value >= threshold.warning_threshold:
            severity = AlertSeverity.WARNING
            threshold_value = threshold.warning_threshold

        if severity is None:
            return None

        # Create alert
        alert_id = (
            f"{AlertType.RESPONSE_TIME_VIOLATION.value}_{operation_type.value}_{int(time.time())}"
        )

        alert = Alert(
            alert_id=alert_id,
            alert_type=AlertType.RESPONSE_TIME_VIOLATION,
            severity=severity,
            title=f"Response Time Violation - {operation_type.value}",
            description=f"{operation_type.value} response time ({metric_value:.2f}s) exceeded {severity.value} threshold ({threshold_value:.2f}s)",
            operation_type=operation_type,
            metric_value=metric_value,
            threshold_value=threshold_value,
            timestamp=time.time(),
            metadata=metadata or {},
        )

        await self._process_alert(alert)
        return alert

    async def create_sla_breach_alert(
        self,
        operation_type: OperationType,
        p95_duration: float,
        sla_threshold: float = 2.0,
        metadata: dict[str, Any] | None = None,
    ) -> Alert:
        """Create SLA breach alert."""
        alert_id = f"{AlertType.SLA_BREACH.value}_{operation_type.value}_{int(time.time())}"

        alert = Alert(
            alert_id=alert_id,
            alert_type=AlertType.SLA_BREACH,
            severity=AlertSeverity.ERROR,
            title=f"SLA Breach - {operation_type.value}",
            description=f"{operation_type.value} P95 response time ({p95_duration:.2f}s) breached SLA threshold ({sla_threshold:.2f}s)",
            operation_type=operation_type,
            metric_value=p95_duration,
            threshold_value=sla_threshold,
            timestamp=time.time(),
            metadata=metadata or {},
        )

        await self._process_alert(alert)
        return alert

    async def create_bottleneck_alert(self, bottleneck: BottleneckIdentification) -> Alert:
        """Create bottleneck detection alert."""
        alert_id = f"{AlertType.BOTTLENECK_DETECTED.value}_{bottleneck.bottleneck_type.value}_{int(time.time())}"

        # Determine severity based on bottleneck severity
        if bottleneck.severity >= 0.8:
            severity = AlertSeverity.CRITICAL
        elif bottleneck.severity >= 0.6:
            severity = AlertSeverity.ERROR
        elif bottleneck.severity >= 0.3:
            severity = AlertSeverity.WARNING
        else:
            severity = AlertSeverity.INFO

        alert = Alert(
            alert_id=alert_id,
            alert_type=AlertType.BOTTLENECK_DETECTED,
            severity=severity,
            title=f"Performance Bottleneck Detected - {bottleneck.bottleneck_type.value}",
            description=bottleneck.description,
            operation_type=(
                bottleneck.affected_operations[0] if bottleneck.affected_operations else None
            ),
            metric_value=bottleneck.severity,
            threshold_value=0.3,  # Minimum severity for alerting
            timestamp=time.time(),
            metadata={
                "bottleneck_type": bottleneck.bottleneck_type.value,
                "affected_operations": [op.value for op in bottleneck.affected_operations],
                "evidence": bottleneck.evidence,
                "recommendations": bottleneck.recommendations,
                "confidence": bottleneck.confidence,
            },
        )

        await self._process_alert(alert)
        return alert

    async def create_trend_alert(self, trend: PerformanceTrend) -> Alert | None:
        """Create trend-based alert."""
        # Only alert on degrading trends with high confidence
        if (
            trend.trend_direction != TrendDirection.DEGRADING
            or trend.confidence < 0.7
            or trend.trend_strength < 0.5
        ):
            return None

        alert_id = f"{AlertType.TREND_ALERT.value}_{trend.operation_type.value}_{int(time.time())}"

        # Determine severity based on predicted performance
        if trend.predicted_performance > 5.0:
            severity = AlertSeverity.CRITICAL
        elif trend.predicted_performance > 2.0:
            severity = AlertSeverity.ERROR
        else:
            severity = AlertSeverity.WARNING

        alert = Alert(
            alert_id=alert_id,
            alert_type=AlertType.TREND_ALERT,
            severity=severity,
            title=f"Performance Degradation Trend - {trend.operation_type.value}",
            description=f"{trend.operation_type.value} showing degrading performance trend. Predicted performance: {trend.predicted_performance:.2f}s",
            operation_type=trend.operation_type,
            metric_value=trend.current_performance,
            threshold_value=trend.predicted_performance,
            timestamp=time.time(),
            metadata={
                "trend_direction": trend.trend_direction.value,
                "trend_strength": trend.trend_strength,
                "time_horizon_minutes": trend.time_horizon_minutes,
                "confidence": trend.confidence,
            },
        )

        await self._process_alert(alert)
        return alert

    async def create_recovery_notification(
        self,
        original_alert_id: str,
        current_metric_value: float,
        metadata: dict[str, Any] | None = None,
    ) -> Alert | None:
        """Create recovery notification for resolved performance issue."""
        # Find original alert
        original_alert = None
        for alert in self.alert_history:
            if alert.alert_id == original_alert_id:
                original_alert = alert
                break

        if not original_alert:
            return None

        alert_id = f"{AlertType.RECOVERY_NOTIFICATION.value}_{original_alert_id}_{int(time.time())}"

        alert = Alert(
            alert_id=alert_id,
            alert_type=AlertType.RECOVERY_NOTIFICATION,
            severity=AlertSeverity.INFO,
            title=f"Performance Recovery - {original_alert.operation_type.value if original_alert.operation_type else 'System'}",
            description=f"Performance has recovered. Current metric: {current_metric_value:.2f}s (was {original_alert.metric_value:.2f}s)",
            operation_type=original_alert.operation_type,
            metric_value=current_metric_value,
            threshold_value=original_alert.threshold_value,
            timestamp=time.time(),
            metadata={
                "original_alert_id": original_alert_id,
                "recovery_time_minutes": (time.time() - original_alert.timestamp) / 60,
                **(metadata or {}),
            },
        )

        await self._process_alert(alert)
        return alert

    async def _process_alert(self, alert: Alert) -> None:
        """Process a new alert."""
        # Check if alert should be suppressed
        if alert.alert_id in self.suppressed_alerts:
            return

        # Add to active alerts
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)

        # Update statistics
        self.alert_counts[alert.alert_type] += 1

        # Send to handlers
        await self._send_alert(alert)

        logger.warning(f"Alert generated: {alert.title} (Severity: {alert.severity.value})")

    async def _send_alert(self, alert: Alert) -> None:
        """Send alert to all registered handlers."""
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")

    async def _escalation_loop(self) -> None:
        """Background task for alert escalation."""
        while self.is_running:
            try:
                current_time = time.time()

                for alert in list(self.active_alerts.values()):
                    if not alert.acknowledged and not alert.resolved:
                        await self._check_escalation(alert, current_time)

                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in escalation loop: {e}")
                await asyncio.sleep(60)

    async def _check_escalation(self, alert: Alert, current_time: float) -> None:
        """Check if alert needs escalation."""
        escalation_key = (alert.alert_type, alert.severity)
        escalation_rule = self.escalation_rules.get(escalation_key)

        if not escalation_rule:
            return

        # Check if enough time has passed for escalation
        time_since_last = current_time - (alert.last_escalation_time or alert.timestamp)
        if time_since_last < escalation_rule.escalation_delay_minutes * 60:
            return

        # Check if we've reached max escalations
        if alert.escalation_count >= escalation_rule.max_escalations:
            return

        # Escalate
        alert.escalation_count += 1
        alert.escalation_level = EscalationLevel(min(4, alert.escalation_level.value + 1))
        alert.last_escalation_time = current_time

        self.escalation_counts[alert.escalation_level] += 1

        # Send escalation notifications
        await self._send_escalation(alert, escalation_rule)

        logger.warning(f"Alert escalated: {alert.alert_id} to level {alert.escalation_level.value}")

    async def _send_escalation(self, alert: Alert, escalation_rule: EscalationRule) -> None:
        """Send escalation notifications."""
        for target in escalation_rule.escalation_targets:
            handler = self.escalation_handlers.get(target)
            if handler:
                try:
                    await handler(alert, escalation_rule)
                except Exception as e:
                    logger.error(f"Escalation handler failed for target {target}: {e}")

    async def _cleanup_loop(self) -> None:
        """Background task for cleaning up old alerts."""
        while self.is_running:
            try:
                current_time = time.time()
                cutoff_time = current_time - (24 * 3600)  # 24 hours

                # Remove old resolved alerts
                resolved_alerts = [
                    alert_id
                    for alert_id, alert in self.active_alerts.items()
                    if alert.resolved and (alert.resolution_time or 0) < cutoff_time
                ]

                for alert_id in resolved_alerts:
                    self.active_alerts.pop(alert_id, None)

                await asyncio.sleep(3600)  # Clean up every hour

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)

    def _find_threshold(
        self, operation_type: OperationType, metric_name: str
    ) -> AlertThreshold | None:
        """Find applicable threshold for operation type and metric."""
        # Look for specific threshold first
        for threshold in self.thresholds:
            if threshold.operation_type == operation_type and threshold.metric_name == metric_name:
                return threshold

        # Look for global threshold
        for threshold in self.thresholds:
            if threshold.operation_type is None and threshold.metric_name == metric_name:
                return threshold

        return None

    def _get_default_thresholds(self) -> list[AlertThreshold]:
        """Get default alert thresholds."""
        return [
            # Global response time thresholds
            AlertThreshold(
                operation_type=None,
                metric_name="response_time",
                warning_threshold=1.0,
                error_threshold=2.0,
                critical_threshold=5.0,
            ),
            # Agent-specific thresholds
            AlertThreshold(
                operation_type=OperationType.AGENT_PROCESSING,
                metric_name="response_time",
                warning_threshold=0.8,
                error_threshold=1.5,
                critical_threshold=3.0,
            ),
            # Workflow-specific thresholds
            AlertThreshold(
                operation_type=OperationType.WORKFLOW_EXECUTION,
                metric_name="response_time",
                warning_threshold=2.0,
                error_threshold=5.0,
                critical_threshold=10.0,
            ),
        ]

    def _setup_default_escalation_rules(self) -> None:
        """Set up default escalation rules."""
        default_rules = [
            EscalationRule(
                alert_type=AlertType.RESPONSE_TIME_VIOLATION,
                severity=AlertSeverity.CRITICAL,
                escalation_delay_minutes=5,
                max_escalations=3,
                escalation_targets=["ops_team", "engineering_lead"],
            ),
            EscalationRule(
                alert_type=AlertType.SLA_BREACH,
                severity=AlertSeverity.ERROR,
                escalation_delay_minutes=10,
                max_escalations=2,
                escalation_targets=["ops_team"],
            ),
            EscalationRule(
                alert_type=AlertType.BOTTLENECK_DETECTED,
                severity=AlertSeverity.CRITICAL,
                escalation_delay_minutes=15,
                max_escalations=2,
                escalation_targets=["engineering_team"],
            ),
        ]

        for rule in default_rules:
            key = (rule.alert_type, rule.severity)
            self.escalation_rules[key] = rule

    def add_alert_handler(self, handler: Callable) -> None:
        """Add alert handler."""
        self.alert_handlers.append(handler)

    def add_escalation_handler(self, target: str, handler: Callable) -> None:
        """Add escalation handler for specific target."""
        self.escalation_handlers[target] = handler

    def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """Acknowledge an alert."""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            logger.info(f"Alert {alert_id} acknowledged by {user}")
            return True
        return False

    def resolve_alert(self, alert_id: str, user: str = "system") -> bool:
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = time.time()
            logger.info(f"Alert {alert_id} resolved by {user}")
            return True
        return False

    def get_alert_statistics(self) -> dict[str, Any]:
        """Get alerting statistics."""
        return {
            "active_alerts": len(self.active_alerts),
            "total_alerts": len(self.alert_history),
            "alerts_by_type": dict(self.alert_counts),
            "escalations_by_level": dict(self.escalation_counts),
            "suppressed_alerts": len(self.suppressed_alerts),
            "configured_thresholds": len(self.thresholds),
            "escalation_rules": len(self.escalation_rules),
        }
