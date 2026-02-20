"""

# Logseq: [[TTA.dev/Analytics/Services/Realtime_monitoring_service]]
Enhanced Real-time Monitoring Service for TTA Analytics

This service provides advanced alerting, anomaly detection, performance analytics,
and real-time therapeutic intervention triggers.
"""

import asyncio
import json
import logging
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

import numpy as np
import redis
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from scipy import stats

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts."""

    THERAPEUTIC_INTERVENTION = "therapeutic_intervention"
    SYSTEM_PERFORMANCE = "system_performance"
    USER_ENGAGEMENT = "user_engagement"
    ANOMALY_DETECTION = "anomaly_detection"
    SAFETY_CONCERN = "safety_concern"


@dataclass
class Alert:
    """Represents a real-time alert."""

    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    data: dict[str, Any]
    user_cohort: str | None
    triggered_at: datetime
    is_resolved: bool = False
    resolved_at: datetime | None = None
    resolved_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["triggered_at"] = self.triggered_at.isoformat()
        if self.resolved_at:
            data["resolved_at"] = self.resolved_at.isoformat()
        return data


@dataclass
class PerformanceMetric:
    """Represents a performance metric."""

    metric_id: str
    metric_name: str
    metric_value: float
    metric_unit: str
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime

    def is_warning(self) -> bool:
        """Check if metric exceeds warning threshold."""
        return self.metric_value >= self.threshold_warning

    def is_critical(self) -> bool:
        """Check if metric exceeds critical threshold."""
        return self.metric_value >= self.threshold_critical


class AnomalyDetector:
    """Detects anomalies in real-time data using statistical methods."""

    def __init__(self, window_size: int = 100, z_threshold: float = 3.0):
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.data_windows: dict[str, list[float]] = {}

    def add_data_point(self, metric_name: str, value: float) -> dict[str, Any] | None:
        """Add data point and check for anomalies."""
        if metric_name not in self.data_windows:
            self.data_windows[metric_name] = []

        window = self.data_windows[metric_name]
        window.append(value)

        # Keep only the most recent window_size points
        if len(window) > self.window_size:
            window.pop(0)

        # Need at least 10 points for anomaly detection
        if len(window) < 10:
            return None

        # Calculate z-score
        mean = np.mean(window[:-1])  # Exclude current point from baseline
        std = np.std(window[:-1])

        if std == 0:  # No variation in data
            return None

        z_score = abs((value - mean) / std)

        if z_score > self.z_threshold:
            return {
                "metric_name": metric_name,
                "value": value,
                "z_score": z_score,
                "mean": mean,
                "std": std,
                "anomaly_type": "statistical_outlier",
            }

        return None

    def detect_trend_anomaly(
        self, metric_name: str, values: list[float]
    ) -> dict[str, Any] | None:
        """Detect trend-based anomalies."""
        if len(values) < 5:
            return None

        # Calculate trend using linear regression
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)

        # Check for sudden trend changes
        if abs(slope) > 2 * std_err and p_value < 0.05:
            trend_type = "increasing" if slope > 0 else "decreasing"
            return {
                "metric_name": metric_name,
                "trend_type": trend_type,
                "slope": slope,
                "r_squared": r_value**2,
                "p_value": p_value,
                "anomaly_type": "trend_change",
            }

        return None


class TherapeuticInterventionTrigger:
    """Triggers therapeutic interventions based on real-time data."""

    def __init__(self):
        self.intervention_rules = {
            "low_engagement": {
                "condition": lambda data: data.get("engagement_score", 1.0) < 0.3,
                "intervention": "engagement_boost",
                "message": "User engagement is critically low. Consider intervention.",
            },
            "extended_session": {
                "condition": lambda data: (
                    data.get("session_duration", 0) > 120
                ),  # 2 hours
                "intervention": "session_break_reminder",
                "message": "User has been in session for over 2 hours. Suggest a break.",
            },
            "negative_sentiment": {
                "condition": lambda data: data.get("sentiment_score", 0.5) < 0.2,
                "intervention": "emotional_support",
                "message": "Negative sentiment detected. Consider emotional support intervention.",
            },
            "crisis_indicators": {
                "condition": lambda data: any(
                    keyword in data.get("recent_messages", [])
                    for keyword in ["hurt myself", "end it all", "no point"]
                ),
                "intervention": "crisis_support",
                "message": "Crisis indicators detected. Immediate intervention required.",
            },
        }

    def evaluate_interventions(self, user_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Evaluate if any interventions should be triggered."""
        triggered_interventions = []

        for rule_name, rule in self.intervention_rules.items():
            try:
                if rule["condition"](user_data):
                    intervention = {
                        "rule_name": rule_name,
                        "intervention_type": rule["intervention"],
                        "message": rule["message"],
                        "user_data": user_data,
                        "triggered_at": datetime.utcnow().isoformat(),
                    }
                    triggered_interventions.append(intervention)
            except Exception as e:
                logger.error(f"Error evaluating intervention rule {rule_name}: {e}")

        return triggered_interventions


class AlertManager:
    """Manages alert generation, notification, and resolution."""

    def __init__(self, redis_client: redis.Redis | None = None):
        self.redis_client = redis_client or redis.Redis(
            host="localhost", port=6379, db=0
        )
        self.active_alerts: dict[str, Alert] = {}
        self.alert_subscribers: list[WebSocket] = []
        self.notification_handlers: dict[AlertSeverity, list[Callable]] = {
            AlertSeverity.LOW: [],
            AlertSeverity.MEDIUM: [],
            AlertSeverity.HIGH: [self._send_email_notification],
            AlertSeverity.CRITICAL: [
                self._send_email_notification,
                self._send_sms_notification,
            ],
        }

    async def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        data: dict[str, Any],
        user_cohort: str | None = None,
    ) -> Alert:
        """Create and process a new alert."""
        alert = Alert(
            alert_id=str(uuid4()),
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            data=data,
            user_cohort=user_cohort,
            triggered_at=datetime.utcnow(),
        )

        # Store alert
        self.active_alerts[alert.alert_id] = alert

        # Store in Redis for persistence
        try:
            self.redis_client.hset(f"alert:{alert.alert_id}", mapping=alert.to_dict())
            self.redis_client.lpush("alerts:active", alert.alert_id)
            self.redis_client.expire(f"alert:{alert.alert_id}", 86400)  # 24 hours
        except Exception as e:
            logger.error(f"Error storing alert in Redis: {e}")

        # Send notifications
        await self._send_notifications(alert)

        # Broadcast to WebSocket subscribers
        await self._broadcast_alert(alert)

        return alert

    async def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Resolve an active alert."""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by

        # Update in Redis
        try:
            self.redis_client.hset(
                f"alert:{alert_id}",
                mapping={
                    "is_resolved": True,
                    "resolved_at": alert.resolved_at.isoformat(),
                    "resolved_by": resolved_by,
                },
            )
            self.redis_client.lrem("alerts:active", 1, alert_id)
            self.redis_client.lpush("alerts:resolved", alert_id)
        except Exception as e:
            logger.error(f"Error updating resolved alert in Redis: {e}")

        # Remove from active alerts
        del self.active_alerts[alert_id]

        return True

    async def _send_notifications(self, alert: Alert):
        """Send notifications based on alert severity."""
        handlers = self.notification_handlers.get(alert.severity, [])
        for handler in handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Error sending notification: {e}")

    async def _send_email_notification(self, alert: Alert):
        """Send email notification for alert."""
        # Mock email notification - implement with actual SMTP in production
        logger.info(f"EMAIL ALERT: {alert.title} - {alert.message}")

    async def _send_sms_notification(self, alert: Alert):
        """Send SMS notification for critical alerts."""
        # Mock SMS notification - implement with SMS service in production
        logger.info(f"SMS ALERT: {alert.title} - {alert.message}")

    async def _broadcast_alert(self, alert: Alert):
        """Broadcast alert to WebSocket subscribers."""
        if not self.alert_subscribers:
            return

        alert_data = json.dumps(alert.to_dict())
        disconnected_clients = []

        for websocket in self.alert_subscribers:
            try:
                await websocket.send_text(alert_data)
            except WebSocketDisconnect:
                disconnected_clients.append(websocket)
            except Exception as e:
                logger.error(f"Error broadcasting alert: {e}")
                disconnected_clients.append(websocket)

        # Remove disconnected clients
        for client in disconnected_clients:
            self.alert_subscribers.remove(client)

    def add_websocket_subscriber(self, websocket: WebSocket):
        """Add WebSocket subscriber for real-time alerts."""
        self.alert_subscribers.append(websocket)

    def remove_websocket_subscriber(self, websocket: WebSocket):
        """Remove WebSocket subscriber."""
        if websocket in self.alert_subscribers:
            self.alert_subscribers.remove(websocket)


class RealTimeMonitoringService:
    """Main real-time monitoring service."""

    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.intervention_trigger = TherapeuticInterventionTrigger()
        self.alert_manager = AlertManager()
        self.performance_metrics: dict[str, PerformanceMetric] = {}
        self.monitoring_active = False

    async def start_monitoring(self):
        """Start real-time monitoring."""
        self.monitoring_active = True
        logger.info("Real-time monitoring started")

        # Start background monitoring tasks
        asyncio.create_task(self._monitor_system_performance())
        asyncio.create_task(self._monitor_user_engagement())
        asyncio.create_task(self._monitor_therapeutic_indicators())

    async def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.monitoring_active = False
        logger.info("Real-time monitoring stopped")

    async def process_metric(
        self,
        metric_name: str,
        value: float,
        warning_threshold: float,
        critical_threshold: float,
    ):
        """Process a new metric value."""
        # Create performance metric
        metric = PerformanceMetric(
            metric_id=str(uuid4()),
            metric_name=metric_name,
            metric_value=value,
            metric_unit="",
            threshold_warning=warning_threshold,
            threshold_critical=critical_threshold,
            timestamp=datetime.utcnow(),
        )

        self.performance_metrics[metric_name] = metric

        # Check for threshold violations
        if metric.is_critical():
            await self.alert_manager.create_alert(
                AlertType.SYSTEM_PERFORMANCE,
                AlertSeverity.CRITICAL,
                f"Critical: {metric_name}",
                f"{metric_name} has reached critical level: {value}",
                {
                    "metric": metric_name,
                    "value": value,
                    "threshold": critical_threshold,
                },
            )
        elif metric.is_warning():
            await self.alert_manager.create_alert(
                AlertType.SYSTEM_PERFORMANCE,
                AlertSeverity.HIGH,
                f"Warning: {metric_name}",
                f"{metric_name} has exceeded warning threshold: {value}",
                {"metric": metric_name, "value": value, "threshold": warning_threshold},
            )

        # Check for anomalies
        anomaly = self.anomaly_detector.add_data_point(metric_name, value)
        if anomaly:
            await self.alert_manager.create_alert(
                AlertType.ANOMALY_DETECTION,
                AlertSeverity.MEDIUM,
                f"Anomaly Detected: {metric_name}",
                f"Statistical anomaly detected in {metric_name}",
                anomaly,
            )

    async def process_user_data(self, user_data: dict[str, Any]):
        """Process user data for therapeutic interventions."""
        interventions = self.intervention_trigger.evaluate_interventions(user_data)

        for intervention in interventions:
            severity = (
                AlertSeverity.CRITICAL
                if intervention["intervention_type"] == "crisis_support"
                else AlertSeverity.HIGH
            )

            await self.alert_manager.create_alert(
                AlertType.THERAPEUTIC_INTERVENTION,
                severity,
                f"Intervention Required: {intervention['intervention_type']}",
                intervention["message"],
                intervention,
            )

    async def _monitor_system_performance(self):
        """Background task to monitor system performance."""
        while self.monitoring_active:
            try:
                # Mock system metrics - in production, collect from actual system
                await self.process_metric(
                    "cpu_usage", np.random.uniform(10, 90), 70, 90
                )
                await self.process_metric(
                    "memory_usage", np.random.uniform(20, 85), 75, 90
                )
                await self.process_metric(
                    "response_time", np.random.uniform(50, 500), 200, 500
                )

                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in system performance monitoring: {e}")
                await asyncio.sleep(60)

    async def _monitor_user_engagement(self):
        """Background task to monitor user engagement."""
        while self.monitoring_active:
            try:
                # Mock user engagement monitoring - in production, collect from user sessions
                mock_user_data = {
                    "user_id": "mock_user",
                    "engagement_score": np.random.uniform(0.1, 1.0),
                    "session_duration": np.random.uniform(5, 150),
                    "sentiment_score": np.random.uniform(0.1, 1.0),
                }

                await self.process_user_data(mock_user_data)
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in user engagement monitoring: {e}")
                await asyncio.sleep(120)

    async def _monitor_therapeutic_indicators(self):
        """Background task to monitor therapeutic indicators."""
        while self.monitoring_active:
            try:
                # Mock therapeutic monitoring - in production, analyze session data
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Error in therapeutic monitoring: {e}")
                await asyncio.sleep(600)


# FastAPI app for the real-time monitoring service
app = FastAPI(title="TTA Enhanced Real-time Monitoring Service", version="1.0.0")

# Global service instance
monitoring_service = RealTimeMonitoringService()


# API Models
class MetricData(BaseModel):
    """Model for metric data."""

    metric_name: str
    value: float
    warning_threshold: float = 100.0
    critical_threshold: float = 200.0


class UserDataModel(BaseModel):
    """Model for user data."""

    user_id: str
    engagement_score: float | None = None
    session_duration: float | None = None
    sentiment_score: float | None = None
    recent_messages: list[str] = Field(default_factory=list)


@app.on_event("startup")
async def startup_event():
    """Start monitoring on application startup."""
    await monitoring_service.start_monitoring()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop monitoring on application shutdown."""
    await monitoring_service.stop_monitoring()


@app.post("/metrics/process")
async def process_metric(metric: MetricData):
    """Process a new metric value."""
    await monitoring_service.process_metric(
        metric.metric_name,
        metric.value,
        metric.warning_threshold,
        metric.critical_threshold,
    )
    return {"status": "processed", "metric": metric.metric_name}


@app.post("/users/process")
async def process_user_data(user_data: UserDataModel):
    """Process user data for therapeutic monitoring."""
    await monitoring_service.process_user_data(user_data.dict())
    return {"status": "processed", "user_id": user_data.user_id}


@app.websocket("/alerts/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time alert streaming."""
    await websocket.accept()
    monitoring_service.alert_manager.add_websocket_subscriber(websocket)

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        monitoring_service.alert_manager.remove_websocket_subscriber(websocket)


@app.get("/alerts/active")
async def get_active_alerts():
    """Get all active alerts."""
    alerts = [
        alert.to_dict()
        for alert in monitoring_service.alert_manager.active_alerts.values()
    ]
    return {"alerts": alerts, "count": len(alerts)}


@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolved_by: str = "system"):
    """Resolve an active alert."""
    success = await monitoring_service.alert_manager.resolve_alert(
        alert_id, resolved_by
    )
    if success:
        return {"status": "resolved", "alert_id": alert_id}
    raise HTTPException(status_code=404, detail="Alert not found")


@app.get("/metrics/current")
async def get_current_metrics():
    """Get current performance metrics."""
    metrics = {}
    for name, metric in monitoring_service.performance_metrics.items():
        metrics[name] = {
            "value": metric.metric_value,
            "timestamp": metric.timestamp.isoformat(),
            "warning_threshold": metric.threshold_warning,
            "critical_threshold": metric.threshold_critical,
            "status": (
                "critical"
                if metric.is_critical()
                else "warning"
                if metric.is_warning()
                else "normal"
            ),
        }

    return {"metrics": metrics, "timestamp": datetime.utcnow().isoformat()}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "realtime-monitoring",
        "monitoring_active": monitoring_service.monitoring_active,
        "active_alerts": len(monitoring_service.alert_manager.active_alerts),
        "websocket_subscribers": len(
            monitoring_service.alert_manager.alert_subscribers
        ),
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8097)
