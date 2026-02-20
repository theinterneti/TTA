"""

# Logseq: [[TTA.dev/Monitoring/Mock_monitoring]]
Mock Monitoring Implementation

Provides mock implementations of monitoring components for environments
without full infrastructure (Prometheus, Grafana, etc.).
"""

import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MockMetric:
    """Mock metric data point."""

    name: str
    value: float
    timestamp: float
    labels: dict[str, str] = field(default_factory=dict)


class MockPrometheusClient:
    """Mock Prometheus client that generates realistic test data."""

    def __init__(self):
        self.metrics: dict[str, list[MockMetric]] = {}
        self.start_time = time.time()

    def _generate_realistic_value(
        self, metric_name: str, base_value: float = 50.0
    ) -> float:
        """Generate realistic metric values with some variation."""
        # Add some randomness and trends
        time_factor = (time.time() - self.start_time) / 3600  # Hours since start

        if "cpu" in metric_name.lower():
            # CPU usage: 20-80% with occasional spikes
            base = 30 + 20 * random.random()
            spike = 30 if random.random() < 0.1 else 0
            return min(95, base + spike + 5 * random.random())

        if "memory" in metric_name.lower():
            # Memory usage: gradually increasing with some variation
            base = 40 + time_factor * 2  # Gradual increase
            return min(90, base + 10 * random.random())

        if "response_time" in metric_name.lower():
            # Response times: mostly fast with occasional slow responses
            base = 0.1 + 0.05 * random.random()
            slow = 2.0 if random.random() < 0.05 else 0
            return base + slow

        if "error_rate" in metric_name.lower():
            # Error rate: mostly low with occasional spikes
            base = 1.0 + 2.0 * random.random()
            spike = 10.0 if random.random() < 0.02 else 0
            return min(20, base + spike)

        if "requests" in metric_name.lower():
            # Request rate: varies throughout the day
            hour = (time.time() % 86400) / 3600  # Hour of day
            daily_pattern = 0.5 + 0.5 * abs(12 - hour) / 12  # Peak at noon
            return 10 + 40 * daily_pattern * (0.8 + 0.4 * random.random())

        # Default: some variation around base value
        return base_value * (0.8 + 0.4 * random.random())

    def query(self, query: str) -> dict[str, Any]:
        """Mock Prometheus query."""
        # Parse query to determine metric type
        metric_name = query.split("{", maxsplit=1)[0].split("(", maxsplit=1)[0].strip()

        # Generate mock data
        current_time = time.time()
        value = self._generate_realistic_value(metric_name)

        # Store metric
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []

        mock_metric = MockMetric(
            name=metric_name,
            value=value,
            timestamp=current_time,
            labels={"service": "mock-service", "instance": "localhost:8000"},
        )

        self.metrics[metric_name].append(mock_metric)

        # Keep only recent metrics (last hour)
        cutoff_time = current_time - 3600
        self.metrics[metric_name] = [
            m for m in self.metrics[metric_name] if m.timestamp > cutoff_time
        ]

        # Return Prometheus-like response
        return {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {"metric": mock_metric.labels, "value": [current_time, str(value)]}
                ],
            },
        }

    def get_metrics_text(self) -> str:
        """Generate Prometheus text format metrics."""
        lines = ["# Mock TTA Metrics"]

        for metric_name, metric_list in self.metrics.items():
            if metric_list:
                latest_metric = metric_list[-1]
                labels_str = ",".join(
                    [f'{k}="{v}"' for k, v in latest_metric.labels.items()]
                )
                if labels_str:
                    labels_str = "{" + labels_str + "}"

                lines.append(f"{metric_name}{labels_str} {latest_metric.value}")

        return "\n".join(lines)


class MockGrafanaClient:
    """Mock Grafana client for testing dashboard functionality."""

    def __init__(self):
        self.dashboards = {}
        self.datasources = {}

    def health_check(self) -> dict[str, Any]:
        """Mock health check."""
        return {"commit": "mock-commit", "database": "ok", "version": "mock-version"}

    def create_dashboard(self, dashboard_config: dict[str, Any]) -> dict[str, Any]:
        """Mock dashboard creation."""
        dashboard_id = f"mock-dashboard-{len(self.dashboards) + 1}"
        self.dashboards[dashboard_id] = dashboard_config

        return {
            "id": dashboard_id,
            "slug": dashboard_config.get("title", "mock-dashboard")
            .lower()
            .replace(" ", "-"),
            "status": "success",
            "uid": dashboard_id,
            "url": f"/d/{dashboard_id}",
            "version": 1,
        }

    def get_dashboard(self, dashboard_id: str) -> dict[str, Any] | None:
        """Get mock dashboard."""
        return self.dashboards.get(dashboard_id)


class MockAlertManager:
    """Mock alert manager for testing alerting functionality."""

    def __init__(self):
        self.alerts: list[dict[str, Any]] = []
        self.rules: list[dict[str, Any]] = []

    def add_rule(self, rule: dict[str, Any]):
        """Add mock alert rule."""
        self.rules.append(rule)

    def trigger_alert(self, alert_name: str, severity: str = "warning"):
        """Manually trigger a mock alert for testing."""
        alert = {
            "alertname": alert_name,
            "severity": severity,
            "status": "firing",
            "startsAt": datetime.now().isoformat(),
            "labels": {"service": "mock-service"},
            "annotations": {"summary": f"Mock alert: {alert_name}"},
        }
        self.alerts.append(alert)
        logger.info(f"Mock alert triggered: {alert_name}")

    def get_alerts(self) -> list[dict[str, Any]]:
        """Get active mock alerts."""
        return [a for a in self.alerts if a["status"] == "firing"]

    def resolve_alert(self, alert_name: str):
        """Resolve a mock alert."""
        for alert in self.alerts:
            if alert["alertname"] == alert_name and alert["status"] == "firing":
                alert["status"] = "resolved"
                alert["endsAt"] = datetime.now().isoformat()
                logger.info(f"Mock alert resolved: {alert_name}")


class MockMonitoringEnvironment:
    """Complete mock monitoring environment for testing."""

    def __init__(self):
        self.prometheus = MockPrometheusClient()
        self.grafana = MockGrafanaClient()
        self.alert_manager = MockAlertManager()
        self.is_running = False

    def start(self):
        """Start the mock monitoring environment."""
        self.is_running = True
        logger.info("Mock monitoring environment started")

        # Add some default alert rules
        self.alert_manager.add_rule(
            {
                "alert": "HighCPUUsage",
                "expr": "cpu_usage > 80",
                "for": "5m",
                "labels": {"severity": "warning"},
            }
        )

    def stop(self):
        """Stop the mock monitoring environment."""
        self.is_running = False
        logger.info("Mock monitoring environment stopped")

    def simulate_load(self):
        """Simulate system load for testing."""
        # Trigger some mock alerts occasionally
        if random.random() < 0.1:  # 10% chance
            alert_types = ["HighCPUUsage", "HighMemoryUsage", "SlowResponseTime"]
            alert_name = random.choice(alert_types)
            severity = "critical" if random.random() < 0.3 else "warning"
            self.alert_manager.trigger_alert(alert_name, severity)

    def get_status(self) -> dict[str, Any]:
        """Get mock environment status."""
        return {
            "prometheus": {"status": "running" if self.is_running else "stopped"},
            "grafana": {"status": "running" if self.is_running else "stopped"},
            "alert_manager": {
                "status": "running" if self.is_running else "stopped",
                "active_alerts": len(self.alert_manager.get_alerts()),
            },
            "mock_mode": True,
        }


# Global mock environment instance
_mock_environment: MockMonitoringEnvironment | None = None


def get_mock_monitoring_environment() -> MockMonitoringEnvironment:
    """Get or create the global mock monitoring environment."""
    global _mock_environment
    if _mock_environment is None:
        _mock_environment = MockMonitoringEnvironment()
    return _mock_environment


def create_mock_metrics_endpoint():
    """Create a mock metrics endpoint for FastAPI."""

    def mock_metrics():
        env = get_mock_monitoring_environment()
        return env.prometheus.get_metrics_text()

    return mock_metrics


def create_mock_health_endpoint():
    """Create a mock health endpoint for FastAPI."""

    def mock_health():
        env = get_mock_monitoring_environment()
        return {
            "status": "healthy",
            "service": "mock-tta-service",
            "monitoring": env.get_status(),
            "timestamp": datetime.now().isoformat(),
        }

    return mock_health


# Environment detection and auto-configuration
def should_use_mock_monitoring() -> bool:
    """Determine if mock monitoring should be used."""
    try:
        import requests

        # Try to connect to Prometheus
        response = requests.get("http://localhost:9090/-/healthy", timeout=2)
        return response.status_code != 200
    except Exception:
        return True


def auto_configure_monitoring():
    """Automatically configure monitoring based on environment."""
    if should_use_mock_monitoring():
        logger.info("Using mock monitoring environment")
        env = get_mock_monitoring_environment()
        env.start()
        return env
    logger.info("Using real monitoring environment")
    return None
