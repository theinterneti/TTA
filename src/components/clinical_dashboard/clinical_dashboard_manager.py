"""
Clinical Dashboard Manager

Core dashboard management system providing real-time therapeutic monitoring,
clinical oversight, and integration with all 9 therapeutic systems from the
Advanced AI Agent Orchestration.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class DashboardStatus(Enum):
    """Dashboard operational status."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class AlertSeverity(Enum):
    """Clinical alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class ClinicalAlert:
    """Clinical alert for healthcare professional notification."""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    alert_type: str = ""
    severity: AlertSeverity = AlertSeverity.LOW
    message: str = ""
    therapeutic_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None


@dataclass
class TherapeuticMetrics:
    """Real-time therapeutic metrics for clinical monitoring."""
    user_id: str
    session_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Core therapeutic metrics
    therapeutic_value_accumulated: float = 0.0
    engagement_level: float = 0.0
    progress_rate: float = 0.0
    safety_score: float = 1.0
    crisis_risk_level: str = "none"

    # System-specific metrics
    consequence_system_metrics: Dict[str, Any] = field(default_factory=dict)
    emotional_safety_metrics: Dict[str, Any] = field(default_factory=dict)
    adaptive_difficulty_metrics: Dict[str, Any] = field(default_factory=dict)
    character_development_metrics: Dict[str, Any] = field(default_factory=dict)
    therapeutic_integration_metrics: Dict[str, Any] = field(default_factory=dict)
    gameplay_controller_metrics: Dict[str, Any] = field(default_factory=dict)
    replayability_metrics: Dict[str, Any] = field(default_factory=dict)
    collaborative_metrics: Dict[str, Any] = field(default_factory=dict)
    error_recovery_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClinicalSession:
    """Clinical session tracking for healthcare oversight."""
    session_id: str
    user_id: str
    clinician_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    session_status: str = "active"
    therapeutic_goals: List[str] = field(default_factory=list)
    current_metrics: Optional[TherapeuticMetrics] = None
    alerts: List[ClinicalAlert] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


class ClinicalDashboardManager:
    """
    Core Clinical Dashboard Manager providing real-time therapeutic monitoring
    and clinical oversight integration with all therapeutic systems.
    """

    def __init__(self):
        """Initialize the Clinical Dashboard Manager."""
        self.status = DashboardStatus.INITIALIZING
        self.active_sessions: Dict[str, ClinicalSession] = {}
        self.active_alerts: Dict[str, ClinicalAlert] = {}
        self.metrics_history: Dict[str, List[TherapeuticMetrics]] = {}
        self.connected_clinicians: Set[str] = set()

        # Therapeutic system references (injected)
        self.consequence_system = None
        self.emotional_safety_system = None
        self.adaptive_difficulty_engine = None
        self.character_development_system = None
        self.therapeutic_integration_system = None
        self.gameplay_loop_controller = None
        self.replayability_system = None
        self.collaborative_system = None
        self.error_recovery_manager = None

        # Dashboard configuration
        self.metrics_collection_interval = 5.0  # seconds
        self.alert_retention_hours = 24
        self.metrics_retention_days = 30

        # Background tasks
        self._metrics_collection_task = None
        self._alert_cleanup_task = None
        self._shutdown_event = asyncio.Event()

        # Performance metrics
        self.dashboard_metrics = {
            "sessions_monitored": 0,
            "alerts_generated": 0,
            "metrics_collected": 0,
            "clinicians_connected": 0,
            "data_refresh_rate": 0.0,
        }

    async def initialize(self):
        """Initialize the Clinical Dashboard Manager."""
        try:
            logger.info("Initializing ClinicalDashboardManager")

            # Start background monitoring tasks
            self._metrics_collection_task = asyncio.create_task(
                self._metrics_collection_loop()
            )
            self._alert_cleanup_task = asyncio.create_task(
                self._alert_cleanup_loop()
            )

            self.status = DashboardStatus.ACTIVE
            logger.info("ClinicalDashboardManager initialization complete")

        except Exception as e:
            logger.error(f"Error initializing ClinicalDashboardManager: {e}")
            self.status = DashboardStatus.OFFLINE
            raise

    def inject_therapeutic_systems(
        self,
        consequence_system=None,
        emotional_safety_system=None,
        adaptive_difficulty_engine=None,
        character_development_system=None,
        therapeutic_integration_system=None,
        gameplay_loop_controller=None,
        replayability_system=None,
        collaborative_system=None,
        error_recovery_manager=None,
    ):
        """Inject therapeutic systems for dashboard integration."""
        self.consequence_system = consequence_system
        self.emotional_safety_system = emotional_safety_system
        self.adaptive_difficulty_engine = adaptive_difficulty_engine
        self.character_development_system = character_development_system
        self.therapeutic_integration_system = therapeutic_integration_system
        self.gameplay_loop_controller = gameplay_loop_controller
        self.replayability_system = replayability_system
        self.collaborative_system = collaborative_system
        self.error_recovery_manager = error_recovery_manager

        logger.info("Therapeutic systems injected into ClinicalDashboardManager")

    async def start_session_monitoring(
        self,
        session_id: str,
        user_id: str,
        clinician_id: Optional[str] = None,
        therapeutic_goals: Optional[List[str]] = None
    ) -> ClinicalSession:
        """Start monitoring a therapeutic session."""
        try:
            clinical_session = ClinicalSession(
                session_id=session_id,
                user_id=user_id,
                clinician_id=clinician_id,
                therapeutic_goals=therapeutic_goals or []
            )

            self.active_sessions[session_id] = clinical_session
            self.dashboard_metrics["sessions_monitored"] += 1

            # Initialize metrics history for this session
            if session_id not in self.metrics_history:
                self.metrics_history[session_id] = []

            logger.info(f"Started clinical monitoring for session {session_id}")
            return clinical_session

        except Exception as e:
            logger.error(f"Error starting session monitoring: {e}")
            raise

    async def collect_real_time_metrics(self, session_id: str) -> Optional[TherapeuticMetrics]:
        """Collect real-time therapeutic metrics from all systems."""
        try:
            if session_id not in self.active_sessions:
                return None

            session = self.active_sessions[session_id]
            metrics = TherapeuticMetrics(
                user_id=session.user_id,
                session_id=session_id
            )

            # Collect metrics from each therapeutic system
            if self.consequence_system and hasattr(self.consequence_system, 'get_user_metrics'):
                metrics.consequence_system_metrics = await self.consequence_system.get_user_metrics(session.user_id)

            if self.emotional_safety_system and hasattr(self.emotional_safety_system, 'get_safety_metrics'):
                safety_metrics = await self.emotional_safety_system.get_safety_metrics(session.user_id)
                metrics.emotional_safety_metrics = safety_metrics
                metrics.safety_score = safety_metrics.get('safety_score', 1.0)
                metrics.crisis_risk_level = safety_metrics.get('crisis_risk_level', 'none')

            if self.adaptive_difficulty_engine and hasattr(self.adaptive_difficulty_engine, 'get_performance_metrics'):
                difficulty_metrics = await self.adaptive_difficulty_engine.get_performance_metrics(session.user_id)
                metrics.adaptive_difficulty_metrics = difficulty_metrics
                metrics.engagement_level = difficulty_metrics.get('engagement_level', 0.0)

            if self.character_development_system and hasattr(self.character_development_system, 'get_character_metrics'):
                character_metrics = await self.character_development_system.get_character_metrics(session.user_id)
                metrics.character_development_metrics = character_metrics
                metrics.progress_rate = character_metrics.get('progress_rate', 0.0)

            if self.therapeutic_integration_system and hasattr(self.therapeutic_integration_system, 'get_integration_metrics'):
                integration_metrics = await self.therapeutic_integration_system.get_integration_metrics(session.user_id)
                metrics.therapeutic_integration_metrics = integration_metrics
                metrics.therapeutic_value_accumulated = integration_metrics.get('therapeutic_value_accumulated', 0.0)

            if self.gameplay_loop_controller and hasattr(self.gameplay_loop_controller, 'get_session_metrics'):
                gameplay_metrics = await self.gameplay_loop_controller.get_session_metrics(session_id)
                metrics.gameplay_controller_metrics = gameplay_metrics

            if self.replayability_system and hasattr(self.replayability_system, 'get_exploration_metrics'):
                replay_metrics = await self.replayability_system.get_exploration_metrics(session.user_id)
                metrics.replayability_metrics = replay_metrics

            if self.collaborative_system and hasattr(self.collaborative_system, 'get_collaboration_metrics'):
                collab_metrics = await self.collaborative_system.get_collaboration_metrics(session.user_id)
                metrics.collaborative_metrics = collab_metrics

            if self.error_recovery_manager and hasattr(self.error_recovery_manager, 'get_metrics'):
                recovery_metrics = self.error_recovery_manager.get_metrics()
                metrics.error_recovery_metrics = recovery_metrics

            # Update session with current metrics
            session.current_metrics = metrics

            # Store metrics in history
            self.metrics_history[session_id].append(metrics)
            self.dashboard_metrics["metrics_collected"] += 1

            return metrics

        except Exception as e:
            logger.error(f"Error collecting real-time metrics: {e}")
            return None

    async def generate_clinical_alert(
        self,
        user_id: str,
        session_id: str,
        alert_type: str,
        severity: AlertSeverity,
        message: str,
        therapeutic_context: Optional[Dict[str, Any]] = None
    ) -> ClinicalAlert:
        """Generate a clinical alert for healthcare professional notification."""
        try:
            alert = ClinicalAlert(
                user_id=user_id,
                session_id=session_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                therapeutic_context=therapeutic_context or {}
            )

            self.active_alerts[alert.alert_id] = alert
            self.dashboard_metrics["alerts_generated"] += 1

            # Add alert to session if it exists
            if session_id in self.active_sessions:
                self.active_sessions[session_id].alerts.append(alert)

            logger.warning(f"Clinical alert generated: {alert_type} - {severity.value} - {message}")

            # For critical/emergency alerts, trigger immediate notification
            if severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                await self._trigger_immediate_notification(alert)

            return alert

        except Exception as e:
            logger.error(f"Error generating clinical alert: {e}")
            raise

    async def _trigger_immediate_notification(self, alert: ClinicalAlert):
        """Trigger immediate notification for critical alerts."""
        try:
            # In a production system, this would integrate with:
            # - SMS/email notification systems
            # - Hospital paging systems
            # - Clinical communication platforms
            # - Emergency response protocols

            logger.critical(f"IMMEDIATE CLINICAL ATTENTION REQUIRED: {alert.message}")
            logger.critical(f"User: {alert.user_id}, Session: {alert.session_id}")
            logger.critical(f"Alert Type: {alert.alert_type}, Severity: {alert.severity.value}")

            # For now, we'll simulate immediate notification
            # In production, integrate with actual notification systems

        except Exception as e:
            logger.error(f"Error triggering immediate notification: {e}")

    async def get_dashboard_overview(self) -> Dict[str, Any]:
        """Get comprehensive dashboard overview for clinical interface."""
        try:
            # Calculate summary statistics
            total_active_sessions = len(self.active_sessions)
            total_active_alerts = len([a for a in self.active_alerts.values() if not a.resolved])
            critical_alerts = len([a for a in self.active_alerts.values()
                                 if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
                                 and not a.resolved])

            # Get recent metrics summary
            recent_metrics = []
            for session_id, metrics_list in self.metrics_history.items():
                if metrics_list:
                    recent_metrics.append(metrics_list[-1])

            avg_therapeutic_value = 0.0
            avg_engagement = 0.0
            avg_safety_score = 1.0

            if recent_metrics:
                avg_therapeutic_value = sum(m.therapeutic_value_accumulated for m in recent_metrics) / len(recent_metrics)
                avg_engagement = sum(m.engagement_level for m in recent_metrics) / len(recent_metrics)
                avg_safety_score = sum(m.safety_score for m in recent_metrics) / len(recent_metrics)

            return {
                "dashboard_status": self.status.value,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": {
                    "active_sessions": total_active_sessions,
                    "active_alerts": total_active_alerts,
                    "critical_alerts": critical_alerts,
                    "connected_clinicians": len(self.connected_clinicians),
                    "avg_therapeutic_value": avg_therapeutic_value,
                    "avg_engagement_level": avg_engagement,
                    "avg_safety_score": avg_safety_score,
                },
                "active_sessions": [
                    {
                        "session_id": session.session_id,
                        "user_id": session.user_id,
                        "clinician_id": session.clinician_id,
                        "start_time": session.start_time.isoformat(),
                        "status": session.session_status,
                        "therapeutic_goals": session.therapeutic_goals,
                        "alert_count": len(session.alerts),
                        "current_metrics": {
                            "therapeutic_value": session.current_metrics.therapeutic_value_accumulated if session.current_metrics else 0.0,
                            "engagement_level": session.current_metrics.engagement_level if session.current_metrics else 0.0,
                            "safety_score": session.current_metrics.safety_score if session.current_metrics else 1.0,
                            "crisis_risk_level": session.current_metrics.crisis_risk_level if session.current_metrics else "none",
                        }
                    }
                    for session in self.active_sessions.values()
                ],
                "recent_alerts": [
                    {
                        "alert_id": alert.alert_id,
                        "user_id": alert.user_id,
                        "session_id": alert.session_id,
                        "alert_type": alert.alert_type,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "timestamp": alert.timestamp.isoformat(),
                        "acknowledged": alert.acknowledged,
                        "resolved": alert.resolved,
                    }
                    for alert in sorted(self.active_alerts.values(),
                                      key=lambda a: a.timestamp, reverse=True)[:10]
                ],
                "system_health": await self._get_system_health_summary(),
                "performance_metrics": self.dashboard_metrics,
            }

        except Exception as e:
            logger.error(f"Error getting dashboard overview: {e}")
            return {
                "dashboard_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _get_system_health_summary(self) -> Dict[str, Any]:
        """Get health summary of all integrated therapeutic systems."""
        try:
            systems_health = {}

            # Check health of all therapeutic systems
            systems = {
                "consequence_system": self.consequence_system,
                "emotional_safety_system": self.emotional_safety_system,
                "adaptive_difficulty_engine": self.adaptive_difficulty_engine,
                "character_development_system": self.character_development_system,
                "therapeutic_integration_system": self.therapeutic_integration_system,
                "gameplay_loop_controller": self.gameplay_loop_controller,
                "replayability_system": self.replayability_system,
                "collaborative_system": self.collaborative_system,
                "error_recovery_manager": self.error_recovery_manager,
            }

            healthy_systems = 0
            for system_name, system in systems.items():
                if system and hasattr(system, 'health_check'):
                    try:
                        health = await system.health_check()
                        systems_health[system_name] = health.get("status", "unknown")
                        if health.get("status") in ["healthy", "degraded"]:
                            healthy_systems += 1
                    except Exception as e:
                        systems_health[system_name] = "error"
                        logger.error(f"Error checking health of {system_name}: {e}")
                else:
                    systems_health[system_name] = "not_available"

            return {
                "systems_health": systems_health,
                "healthy_systems": f"{healthy_systems}/9",
                "overall_health": "healthy" if healthy_systems >= 7 else "degraded" if healthy_systems >= 5 else "critical"
            }

        except Exception as e:
            logger.error(f"Error getting system health summary: {e}")
            return {"error": str(e)}

    async def acknowledge_alert(self, alert_id: str, clinician_id: str) -> bool:
        """Acknowledge a clinical alert."""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.acknowledged = True
                alert.acknowledged_by = clinician_id
                alert.acknowledged_at = datetime.utcnow()

                logger.info(f"Alert {alert_id} acknowledged by clinician {clinician_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False

    async def resolve_alert(self, alert_id: str, clinician_id: str) -> bool:
        """Resolve a clinical alert."""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_by = clinician_id
                alert.resolved_at = datetime.utcnow()

                logger.info(f"Alert {alert_id} resolved by clinician {clinician_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False

    async def connect_clinician(self, clinician_id: str) -> bool:
        """Connect a clinician to the dashboard."""
        try:
            self.connected_clinicians.add(clinician_id)
            self.dashboard_metrics["clinicians_connected"] = len(self.connected_clinicians)

            logger.info(f"Clinician {clinician_id} connected to dashboard")
            return True

        except Exception as e:
            logger.error(f"Error connecting clinician: {e}")
            return False

    async def disconnect_clinician(self, clinician_id: str) -> bool:
        """Disconnect a clinician from the dashboard."""
        try:
            self.connected_clinicians.discard(clinician_id)
            self.dashboard_metrics["clinicians_connected"] = len(self.connected_clinicians)

            logger.info(f"Clinician {clinician_id} disconnected from dashboard")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting clinician: {e}")
            return False

    async def _metrics_collection_loop(self):
        """Background loop for collecting real-time metrics."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    start_time = datetime.utcnow()

                    # Collect metrics for all active sessions
                    for session_id in list(self.active_sessions.keys()):
                        await self.collect_real_time_metrics(session_id)

                    # Calculate data refresh rate
                    collection_time = (datetime.utcnow() - start_time).total_seconds()
                    self.dashboard_metrics["data_refresh_rate"] = collection_time

                    # Wait for next collection interval
                    await asyncio.sleep(self.metrics_collection_interval)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in metrics collection loop: {e}")
                    await asyncio.sleep(self.metrics_collection_interval)

        except asyncio.CancelledError:
            logger.info("Metrics collection loop cancelled")

    async def _alert_cleanup_loop(self):
        """Background loop for cleaning up old alerts."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    cutoff_time = datetime.utcnow() - timedelta(hours=self.alert_retention_hours)

                    # Clean up old resolved alerts
                    alerts_to_remove = []
                    for alert_id, alert in self.active_alerts.items():
                        if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_time:
                            alerts_to_remove.append(alert_id)

                    for alert_id in alerts_to_remove:
                        self.active_alerts.pop(alert_id, None)

                    # Clean up old metrics history
                    metrics_cutoff = datetime.utcnow() - timedelta(days=self.metrics_retention_days)
                    for session_id, metrics_list in self.metrics_history.items():
                        self.metrics_history[session_id] = [
                            m for m in metrics_list if m.timestamp > metrics_cutoff
                        ]

                    # Wait for next cleanup cycle (every hour)
                    await asyncio.sleep(3600)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in alert cleanup loop: {e}")
                    await asyncio.sleep(3600)

        except asyncio.CancelledError:
            logger.info("Alert cleanup loop cancelled")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the Clinical Dashboard Manager."""
        try:
            # Check therapeutic system availability
            systems_available = 0
            if self.consequence_system: systems_available += 1
            if self.emotional_safety_system: systems_available += 1
            if self.adaptive_difficulty_engine: systems_available += 1
            if self.character_development_system: systems_available += 1
            if self.therapeutic_integration_system: systems_available += 1
            if self.gameplay_loop_controller: systems_available += 1
            if self.replayability_system: systems_available += 1
            if self.collaborative_system: systems_available += 1
            if self.error_recovery_manager: systems_available += 1

            return {
                "status": "healthy" if systems_available >= 7 else "degraded",
                "dashboard_status": self.status.value,
                "active_sessions": len(self.active_sessions),
                "active_alerts": len(self.active_alerts),
                "connected_clinicians": len(self.connected_clinicians),
                "therapeutic_systems_available": f"{systems_available}/9",
                "background_tasks_running": (
                    self._metrics_collection_task is not None and not self._metrics_collection_task.done() and
                    self._alert_cleanup_task is not None and not self._alert_cleanup_task.done()
                ),
                "metrics_collection_interval": self.metrics_collection_interval,
                "performance_metrics": self.dashboard_metrics,
            }

        except Exception as e:
            logger.error(f"Error in clinical dashboard health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def shutdown(self):
        """Shutdown the Clinical Dashboard Manager."""
        try:
            logger.info("Shutting down ClinicalDashboardManager")

            # Signal shutdown to background tasks
            self._shutdown_event.set()

            # Cancel background tasks
            if self._metrics_collection_task:
                self._metrics_collection_task.cancel()
                try:
                    await self._metrics_collection_task
                except asyncio.CancelledError:
                    pass

            if self._alert_cleanup_task:
                self._alert_cleanup_task.cancel()
                try:
                    await self._alert_cleanup_task
                except asyncio.CancelledError:
                    pass

            self.status = DashboardStatus.OFFLINE
            logger.info("ClinicalDashboardManager shutdown complete")

        except Exception as e:
            logger.error(f"Error during clinical dashboard shutdown: {e}")
            raise
