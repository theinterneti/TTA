"""

# Logseq: [[TTA.dev/Monitoring/Realtime_alerts]]
Real-time Alerting System for TTA Monitoring

Integrates with the existing real-time dashboard system to provide
intelligent alerting based on Prometheus metrics and system health.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status."""

    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class AlertRule:
    """Definition of an alert rule."""

    name: str
    description: str
    query: str  # Prometheus query
    threshold: float
    comparison: str  # "gt", "lt", "eq", "gte", "lte"
    severity: AlertSeverity
    duration: int = 300  # seconds
    enabled: bool = True
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """Active alert instance."""

    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    value: float
    threshold: float
    started_at: datetime
    resolved_at: datetime | None = None
    acknowledged_at: datetime | None = None
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)


class AlertManager:
    """Manages real-time alerts for TTA monitoring."""

    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus_url = prometheus_url
        self.alert_rules: dict[str, AlertRule] = {}
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: list[Alert] = []
        self.notification_handlers: list[Callable[[Alert], None]] = []
        self.is_running = False
        self.check_interval = 30  # seconds

        # Initialize default alert rules
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize default alert rules for TTA system."""
        default_rules = [
            AlertRule(
                name="high_cpu_usage",
                description="High CPU usage detected",
                query="tta_system_cpu_usage_percent",
                threshold=85.0,
                comparison="gt",
                severity=AlertSeverity.WARNING,
                duration=300,
                annotations={
                    "summary": "High CPU usage on {{$labels.service}}",
                    "description": "CPU usage is {{$value}}% on {{$labels.service}}",
                },
            ),
            AlertRule(
                name="high_memory_usage",
                description="High memory usage detected",
                query="tta_system_memory_usage_percent",
                threshold=90.0,
                comparison="gt",
                severity=AlertSeverity.CRITICAL,
                duration=300,
                annotations={
                    "summary": "High memory usage on {{$labels.service}}",
                    "description": "Memory usage is {{$value}}% on {{$labels.service}}",
                },
            ),
            AlertRule(
                name="high_error_rate",
                description="High HTTP error rate",
                query="rate(tta_http_requests_total{status_code=~'5..'}[5m]) / rate(tta_http_requests_total[5m]) * 100",
                threshold=10.0,
                comparison="gt",
                severity=AlertSeverity.WARNING,
                duration=300,
                annotations={
                    "summary": "High error rate on {{$labels.service}}",
                    "description": "Error rate is {{$value}}% on {{$labels.service}}",
                },
            ),
            AlertRule(
                name="slow_response_time",
                description="Slow response times detected",
                query="histogram_quantile(0.95, rate(tta_http_request_duration_seconds_bucket[5m]))",
                threshold=2.0,
                comparison="gt",
                severity=AlertSeverity.WARNING,
                duration=300,
                annotations={
                    "summary": "Slow response times on {{$labels.service}}",
                    "description": "95th percentile response time is {{$value}}s on {{$labels.service}}",
                },
            ),
            AlertRule(
                name="story_generation_failures",
                description="Story generation failure rate too high",
                query="rate(tta_story_generation_requests_total{success='false'}[5m]) / rate(tta_story_generation_requests_total[5m]) * 100",
                threshold=5.0,
                comparison="gt",
                severity=AlertSeverity.CRITICAL,
                duration=120,
                annotations={
                    "summary": "High story generation failure rate",
                    "description": "Story generation failure rate is {{$value}}% for {{$labels.model_type}}",
                },
            ),
            AlertRule(
                name="model_response_time_high",
                description="Model response time is too high",
                query="histogram_quantile(0.95, rate(tta_model_response_time_seconds_bucket[5m]))",
                threshold=30.0,
                comparison="gt",
                severity=AlertSeverity.WARNING,
                duration=180,
                annotations={
                    "summary": "High model response time",
                    "description": "95th percentile model response time is {{$value}}s for {{$labels.model_name}}",
                },
            ),
        ]

        for rule in default_rules:
            self.alert_rules[rule.name] = rule

    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule."""
        self.alert_rules[rule.name] = rule
        logger.info(f"Added alert rule: {rule.name}")

    def remove_alert_rule(self, rule_name: str):
        """Remove an alert rule."""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            logger.info(f"Removed alert rule: {rule_name}")

    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """Add a notification handler for alerts."""
        self.notification_handlers.append(handler)

    async def start(self):
        """Start the alert manager."""
        if self.is_running:
            return

        self.is_running = True
        logger.info("Starting TTA Alert Manager")

        # Start the alert checking loop
        asyncio.create_task(self._alert_check_loop())

    async def stop(self):
        """Stop the alert manager."""
        self.is_running = False
        logger.info("Stopping TTA Alert Manager")

    async def _alert_check_loop(self):
        """Main loop for checking alert conditions."""
        while self.is_running:
            try:
                await self._check_all_rules()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert check loop: {e}")
                await asyncio.sleep(self.check_interval)

    async def _check_all_rules(self):
        """Check all alert rules."""
        if not REQUESTS_AVAILABLE:
            logger.debug("Requests library not available, skipping Prometheus queries")
            return

        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue

            try:
                await self._check_rule(rule)
            except Exception as e:
                logger.error(f"Error checking rule {rule_name}: {e}")

    async def _check_rule(self, rule: AlertRule):
        """Check a specific alert rule."""
        try:
            # Query Prometheus
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": rule.query},
                timeout=10,
            )

            if response.status_code != 200:
                logger.warning(
                    f"Prometheus query failed for rule {rule.name}: {response.status_code}"
                )
                return

            data = response.json()

            if data["status"] != "success":
                logger.warning(
                    f"Prometheus query error for rule {rule.name}: {data.get('error', 'Unknown error')}"
                )
                return

            results = data["data"]["result"]

            for result in results:
                metric_value = float(result["value"][1])
                labels = result["metric"]

                # Check if alert condition is met
                alert_triggered = self._evaluate_condition(
                    metric_value, rule.threshold, rule.comparison
                )

                alert_key = f"{rule.name}_{hash(str(sorted(labels.items())))}"

                if alert_triggered:
                    if alert_key not in self.active_alerts:
                        # New alert
                        alert = Alert(
                            rule_name=rule.name,
                            severity=rule.severity,
                            status=AlertStatus.ACTIVE,
                            message=self._format_message(
                                rule.annotations.get("summary", rule.description),
                                labels,
                                metric_value,
                            ),
                            value=metric_value,
                            threshold=rule.threshold,
                            started_at=datetime.now(),
                            labels=labels,
                            annotations=rule.annotations,
                        )

                        self.active_alerts[alert_key] = alert
                        self.alert_history.append(alert)

                        logger.warning(f"Alert triggered: {alert.message}")
                        await self._send_notifications(alert)
                elif alert_key in self.active_alerts:
                    # Resolve existing alert
                    alert = self.active_alerts[alert_key]
                    alert.status = AlertStatus.RESOLVED
                    alert.resolved_at = datetime.now()

                    del self.active_alerts[alert_key]

                    logger.info(f"Alert resolved: {alert.message}")
                    await self._send_notifications(alert)

        except requests.RequestException as e:
            logger.error(f"Error querying Prometheus for rule {rule.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error checking rule {rule.name}: {e}")

    def _evaluate_condition(
        self, value: float, threshold: float, comparison: str
    ) -> bool:
        """Evaluate alert condition."""
        if comparison == "gt":
            return value > threshold
        if comparison == "gte":
            return value >= threshold
        if comparison == "lt":
            return value < threshold
        if comparison == "lte":
            return value <= threshold
        if comparison == "eq":
            return value == threshold
        logger.warning(f"Unknown comparison operator: {comparison}")
        return False

    def _format_message(
        self, template: str, labels: dict[str, str], value: float
    ) -> str:
        """Format alert message with labels and values."""
        message = template
        message = message.replace("{{$value}}", f"{value:.2f}")

        for key, val in labels.items():
            message = message.replace(f"{{{{$labels.{key}}}}}", val)

        return message

    async def _send_notifications(self, alert: Alert):
        """Send notifications for an alert."""
        for handler in self.notification_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Error in notification handler: {e}")

    def get_active_alerts(self) -> list[Alert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())

    def get_alert_history(self, limit: int = 100) -> list[Alert]:
        """Get alert history."""
        return self.alert_history[-limit:]

    def acknowledge_alert(self, alert_key: str) -> bool:
        """Acknowledge an active alert."""
        if alert_key in self.active_alerts:
            self.active_alerts[alert_key].status = AlertStatus.ACKNOWLEDGED
            self.active_alerts[alert_key].acknowledged_at = datetime.now()
            return True
        return False


# Notification handlers
def console_notification_handler(alert: Alert):
    """Simple console notification handler."""


def webhook_notification_handler(webhook_url: str):
    """Create a webhook notification handler."""

    def handler(alert: Alert):
        if not REQUESTS_AVAILABLE:
            return

        payload = {
            "alert": {
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "message": alert.message,
                "value": alert.value,
                "threshold": alert.threshold,
                "started_at": alert.started_at.isoformat(),
                "labels": alert.labels,
                "annotations": alert.annotations,
            }
        }

        try:
            requests.post(webhook_url, json=payload, timeout=10)
        except requests.RequestException as e:
            logger.error(f"Failed to send webhook notification: {e}")

    return handler


# Global alert manager instance
_alert_manager: AlertManager | None = None


def get_alert_manager(prometheus_url: str = "http://localhost:9090") -> AlertManager:
    """Get or create the global alert manager."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager(prometheus_url)
    return _alert_manager
