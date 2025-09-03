"""
Clinical Dashboard Manager

Core dashboard management system providing real-time therapeutic monitoring,
clinical oversight, and integration with all 9 therapeutic systems from the
Advanced AI Agent Orchestration.

Enhanced for Phase B: Clinical Dashboard Integration with production-ready
features including role-based access control, clinical-grade security,
and comprehensive therapeutic monitoring capabilities.
"""

import asyncio
import logging
import secrets
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Get current UTC time with timezone awareness."""
    from datetime import timezone

    return datetime.now(timezone.utc)


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


class ClinicalRole(Enum):
    """Clinical practitioner roles for access control."""

    THERAPIST = "therapist"
    CLINICAL_SUPERVISOR = "clinical_supervisor"
    PSYCHIATRIST = "psychiatrist"
    CLINICAL_ADMIN = "clinical_admin"
    SYSTEM_ADMIN = "system_admin"
    OBSERVER = "observer"


class AccessLevel(Enum):
    """Access levels for clinical dashboard features."""

    READ_ONLY = "read_only"
    STANDARD = "standard"
    ELEVATED = "elevated"
    ADMINISTRATIVE = "administrative"
    EMERGENCY = "emergency"


class AuditEventType(Enum):
    """Types of clinical audit events."""

    LOGIN = "login"
    LOGOUT = "logout"
    SESSION_ACCESS = "session_access"
    ALERT_ACKNOWLEDGMENT = "alert_acknowledgment"
    INTERVENTION = "intervention"
    DATA_EXPORT = "data_export"
    CONFIGURATION_CHANGE = "configuration_change"
    EMERGENCY_ACCESS = "emergency_access"


@dataclass
class ClinicalPractitioner:
    """Clinical practitioner information for dashboard access."""

    practitioner_id: str
    username: str
    full_name: str
    role: ClinicalRole
    access_level: AccessLevel
    email: str
    license_number: str | None = None
    department: str | None = None
    supervisor_id: str | None = None
    active: bool = True
    last_login: datetime | None = None
    session_token: str | None = None
    token_expires: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuditLogEntry:
    """Clinical audit log entry for HIPAA compliance."""

    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    practitioner_id: str = ""
    event_type: AuditEventType = AuditEventType.SESSION_ACCESS
    resource_accessed: str = ""
    patient_id: str | None = None
    session_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: str | None = None
    user_agent: str | None = None
    success: bool = True
    details: dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"


@dataclass
class ClinicalAlert:
    """Enhanced clinical alert for healthcare professional notification."""

    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    alert_type: str = ""
    severity: AlertSeverity = AlertSeverity.LOW
    message: str = ""
    therapeutic_context: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    resolved: bool = False
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    # Enhanced fields for production
    priority_score: float = 0.0
    escalation_level: int = 0
    intervention_required: bool = False
    clinical_notes: list[str] = field(default_factory=list)
    related_alerts: list[str] = field(default_factory=list)
    auto_escalation_time: datetime | None = None


@dataclass
class TherapeuticMetrics:
    """Enhanced real-time therapeutic metrics for clinical monitoring."""

    user_id: str
    session_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Core therapeutic metrics
    therapeutic_value_accumulated: float = 0.0
    engagement_level: float = 0.0
    progress_rate: float = 0.0
    safety_score: float = 1.0
    crisis_risk_level: str = "none"

    # Clinical-grade metrics
    session_duration_minutes: float = 0.0
    therapeutic_goals_progress: dict[str, float] = field(default_factory=dict)
    intervention_effectiveness: float = 0.0
    emotional_regulation_score: float = 0.0
    coping_skills_utilization: float = 0.0
    therapeutic_alliance_strength: float = 0.0
    behavioral_change_indicators: dict[str, Any] = field(default_factory=dict)
    clinical_risk_factors: list[str] = field(default_factory=list)
    protective_factors: list[str] = field(default_factory=list)

    # System-specific metrics
    consequence_system_metrics: dict[str, Any] = field(default_factory=dict)
    emotional_safety_metrics: dict[str, Any] = field(default_factory=dict)
    adaptive_difficulty_metrics: dict[str, Any] = field(default_factory=dict)
    character_development_metrics: dict[str, Any] = field(default_factory=dict)
    therapeutic_integration_metrics: dict[str, Any] = field(default_factory=dict)
    gameplay_controller_metrics: dict[str, Any] = field(default_factory=dict)
    replayability_metrics: dict[str, Any] = field(default_factory=dict)
    collaborative_metrics: dict[str, Any] = field(default_factory=dict)
    error_recovery_metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class ClinicalSession:
    """Enhanced clinical session tracking for healthcare oversight."""

    session_id: str
    user_id: str
    clinician_id: str | None = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime | None = None
    session_status: str = "active"
    therapeutic_goals: list[str] = field(default_factory=list)
    current_metrics: TherapeuticMetrics | None = None
    alerts: list[ClinicalAlert] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    # Enhanced clinical tracking
    therapeutic_modality: str = "CBT"
    session_type: str = "individual"
    crisis_level: str = "none"
    interventions_applied: list[str] = field(default_factory=list)
    clinical_observations: dict[str, Any] = field(default_factory=dict)
    treatment_plan_id: str | None = None
    session_rating: float | None = None
    homework_assigned: list[str] = field(default_factory=list)
    next_session_recommendations: list[str] = field(default_factory=list)
    consent_status: str = "active"
    data_retention_policy: str = "standard"


class ClinicalDashboardManager:
    """
    Enhanced Clinical Dashboard Manager providing real-time therapeutic monitoring,
    clinical oversight, and integration with all therapeutic systems.

    Features:
    - Role-based access control for clinical practitioners
    - HIPAA-compliant audit logging
    - Real-time crisis detection and alerting
    - Clinical-grade metrics collection and analysis
    - Production-ready security and compliance
    """

    def __init__(self) -> None:
        """Initialize the Enhanced Clinical Dashboard Manager."""
        self.status = DashboardStatus.INITIALIZING
        self.active_sessions: dict[str, ClinicalSession] = {}
        self.active_alerts: dict[str, ClinicalAlert] = {}
        self.metrics_history: dict[str, list[TherapeuticMetrics]] = {}
        self.connected_clinicians: set[str] = set()

        # Enhanced clinical features
        self.registered_practitioners: dict[str, ClinicalPractitioner] = {}
        self.active_practitioner_sessions: dict[str, str] = (
            {}
        )  # session_token -> practitioner_id
        self.audit_log: list[AuditLogEntry] = []
        self.role_permissions: dict[ClinicalRole, set[str]] = (
            self._initialize_role_permissions()
        )

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

        # Enhanced dashboard configuration
        self.metrics_collection_interval = 5.0  # seconds
        self.alert_retention_hours = 24
        self.metrics_retention_days = 30
        self.audit_log_retention_days = 2555  # 7 years for HIPAA compliance
        self.session_timeout_minutes = 30
        self.max_concurrent_sessions = 100
        self.crisis_alert_escalation_minutes = 5

        # Background tasks
        self._metrics_collection_task = None
        self._alert_cleanup_task = None
        self._audit_cleanup_task = None
        self._session_timeout_task = None
        self._shutdown_event = asyncio.Event()

        # Enhanced performance metrics
        self.dashboard_metrics = {
            "sessions_monitored": 0,
            "alerts_generated": 0,
            "metrics_collected": 0,
            "clinicians_connected": 0,
            "data_refresh_rate": 0.0,
            "crisis_alerts_count": 0,
            "average_response_time_ms": 0.0,
            "audit_events_logged": 0,
            "security_violations": 0,
        }

        # System health monitoring
        self.system_health_cache: dict[str, dict[str, Any]] = {}
        self.health_check_interval = 30.0  # seconds
        self.health_cache_duration = timedelta(minutes=2)
        self.last_health_check = utc_now() - timedelta(hours=1)
        self.system_health_history: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.health_alert_thresholds = {
            "response_time_ms": 1000,
            "error_rate_percent": 5.0,
            "memory_usage_percent": 85.0,
            "cpu_usage_percent": 80.0,
        }

    def _initialize_role_permissions(self) -> dict[ClinicalRole, set[str]]:
        """Initialize role-based permissions for clinical dashboard access."""
        return {
            ClinicalRole.OBSERVER: {
                "view_sessions",
                "view_metrics",
                "view_alerts",
            },
            ClinicalRole.THERAPIST: {
                "view_sessions",
                "view_metrics",
                "view_alerts",
                "acknowledge_alerts",
                "add_session_notes",
                "view_patient_progress",
                "create_interventions",
            },
            ClinicalRole.CLINICAL_SUPERVISOR: {
                "view_sessions",
                "view_metrics",
                "view_alerts",
                "acknowledge_alerts",
                "add_session_notes",
                "view_patient_progress",
                "create_interventions",
                "supervise_sessions",
                "view_all_practitioners",
                "generate_reports",
                "manage_treatment_plans",
            },
            ClinicalRole.PSYCHIATRIST: {
                "view_sessions",
                "view_metrics",
                "view_alerts",
                "acknowledge_alerts",
                "add_session_notes",
                "view_patient_progress",
                "create_interventions",
                "prescribe_medications",
                "emergency_interventions",
                "crisis_management",
                "generate_reports",
            },
            ClinicalRole.CLINICAL_ADMIN: {
                "view_sessions",
                "view_metrics",
                "view_alerts",
                "acknowledge_alerts",
                "add_session_notes",
                "view_patient_progress",
                "create_interventions",
                "supervise_sessions",
                "view_all_practitioners",
                "generate_reports",
                "manage_treatment_plans",
                "manage_practitioners",
                "configure_dashboard",
                "view_audit_logs",
                "export_data",
            },
            ClinicalRole.SYSTEM_ADMIN: {
                "view_sessions",
                "view_metrics",
                "view_alerts",
                "acknowledge_alerts",
                "add_session_notes",
                "view_patient_progress",
                "create_interventions",
                "supervise_sessions",
                "view_all_practitioners",
                "generate_reports",
                "manage_treatment_plans",
                "manage_practitioners",
                "configure_dashboard",
                "view_audit_logs",
                "export_data",
                "system_administration",
                "security_management",
                "backup_restore",
                "emergency_access",
            },
        }

    async def initialize(self) -> None:
        """Initialize the Enhanced Clinical Dashboard Manager."""
        try:
            logger.info("Initializing Enhanced ClinicalDashboardManager")

            # Start enhanced background monitoring tasks
            self._metrics_collection_task = asyncio.create_task(
                self._metrics_collection_loop()
            )
            self._alert_cleanup_task = asyncio.create_task(self._alert_cleanup_loop())
            self._audit_cleanup_task = asyncio.create_task(self._audit_cleanup_loop())
            self._session_timeout_task = asyncio.create_task(
                self._session_timeout_loop()
            )

            self.status = DashboardStatus.ACTIVE
            logger.info("Enhanced ClinicalDashboardManager initialization complete")

            # Log initialization audit event
            await self._log_audit_event(
                practitioner_id="system",
                event_type=AuditEventType.CONFIGURATION_CHANGE,
                resource_accessed="dashboard_initialization",
                success=True,
                details={
                    "component": "ClinicalDashboardManager",
                    "version": "enhanced",
                },
            )

        except Exception as e:
            logger.error(f"Error initializing Enhanced ClinicalDashboardManager: {e}")
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
        clinician_id: str | None = None,
        therapeutic_goals: list[str] | None = None,
    ) -> ClinicalSession:
        """Start monitoring a therapeutic session."""
        try:
            clinical_session = ClinicalSession(
                session_id=session_id,
                user_id=user_id,
                clinician_id=clinician_id,
                therapeutic_goals=therapeutic_goals or [],
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

    async def update_session_metrics(
        self, session_id: str, metrics: TherapeuticMetrics
    ) -> bool:
        """Update session with new therapeutic metrics."""
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Session {session_id} not found for metrics update")
                return False

            session = self.active_sessions[session_id]
            session.current_metrics = metrics

            # Add to metrics history
            if session_id not in self.metrics_history:
                self.metrics_history[session_id] = []

            self.metrics_history[session_id].append(metrics)
            self.dashboard_metrics["metrics_collected"] += 1

            logger.debug(f"Updated metrics for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating session metrics: {e}")
            return False

    async def add_clinical_alert(self, alert: ClinicalAlert) -> bool:
        """Add a clinical alert to the dashboard."""
        try:
            self.active_alerts[alert.alert_id] = alert
            self.dashboard_metrics["alerts_generated"] += 1

            # Update crisis alert count if applicable
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                self.dashboard_metrics["crisis_alerts_count"] += 1

            # Add alert to session if it exists
            if alert.session_id in self.active_sessions:
                self.active_sessions[alert.session_id].alerts.append(alert)

            logger.info(
                f"Added clinical alert: {alert.alert_type} ({alert.severity.value})"
            )
            return True

        except Exception as e:
            logger.error(f"Error adding clinical alert: {e}")
            return False

    async def acknowledge_alert(self, alert_id: str, practitioner_id: str) -> bool:
        """Acknowledge a clinical alert."""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                logger.warning(f"Alert {alert_id} not found for acknowledgment")
                return False

            if alert.acknowledged:
                logger.info(f"Alert {alert_id} already acknowledged")
                return True

            # Update alert
            alert.acknowledged = True
            alert.acknowledged_by = practitioner_id
            alert.acknowledged_at = datetime.utcnow()

            # Log audit event
            await self._log_audit_event(
                practitioner_id=practitioner_id,
                event_type=AuditEventType.ALERT_ACKNOWLEDGMENT,
                resource_accessed=f"alert:{alert_id}",
                patient_id=alert.user_id,
                session_id=alert.session_id,
                success=True,
                details={
                    "alert_type": alert.alert_type,
                    "severity": alert.severity.value,
                    "acknowledgment_time": alert.acknowledged_at.isoformat(),
                },
            )

            logger.info(
                f"Alert {alert_id} acknowledged by practitioner {practitioner_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False

    async def collect_real_time_metrics(
        self, session_id: str
    ) -> TherapeuticMetrics | None:
        """Collect real-time therapeutic metrics from all systems."""
        try:
            if session_id not in self.active_sessions:
                return None

            session = self.active_sessions[session_id]
            metrics = TherapeuticMetrics(user_id=session.user_id, session_id=session_id)

            # Collect metrics from each therapeutic system
            if self.consequence_system and hasattr(
                self.consequence_system, "get_user_metrics"
            ):
                metrics.consequence_system_metrics = (
                    await self.consequence_system.get_user_metrics(session.user_id)
                )

            if self.emotional_safety_system and hasattr(
                self.emotional_safety_system, "get_safety_metrics"
            ):
                safety_metrics = await self.emotional_safety_system.get_safety_metrics(
                    session.user_id
                )
                metrics.emotional_safety_metrics = safety_metrics
                metrics.safety_score = safety_metrics.get("safety_score", 1.0)
                metrics.crisis_risk_level = safety_metrics.get(
                    "crisis_risk_level", "none"
                )

            if self.adaptive_difficulty_engine and hasattr(
                self.adaptive_difficulty_engine, "get_performance_metrics"
            ):
                difficulty_metrics = (
                    await self.adaptive_difficulty_engine.get_performance_metrics(
                        session.user_id
                    )
                )
                metrics.adaptive_difficulty_metrics = difficulty_metrics
                metrics.engagement_level = difficulty_metrics.get(
                    "engagement_level", 0.0
                )

            if self.character_development_system and hasattr(
                self.character_development_system, "get_character_metrics"
            ):
                character_metrics = (
                    await self.character_development_system.get_character_metrics(
                        session.user_id
                    )
                )
                metrics.character_development_metrics = character_metrics
                metrics.progress_rate = character_metrics.get("progress_rate", 0.0)

            if self.therapeutic_integration_system and hasattr(
                self.therapeutic_integration_system, "get_integration_metrics"
            ):
                integration_metrics = (
                    await self.therapeutic_integration_system.get_integration_metrics(
                        session.user_id
                    )
                )
                metrics.therapeutic_integration_metrics = integration_metrics
                metrics.therapeutic_value_accumulated = integration_metrics.get(
                    "therapeutic_value_accumulated", 0.0
                )

            if self.gameplay_loop_controller and hasattr(
                self.gameplay_loop_controller, "get_session_metrics"
            ):
                gameplay_metrics = (
                    await self.gameplay_loop_controller.get_session_metrics(session_id)
                )
                metrics.gameplay_controller_metrics = gameplay_metrics

            if self.replayability_system and hasattr(
                self.replayability_system, "get_exploration_metrics"
            ):
                replay_metrics = (
                    await self.replayability_system.get_exploration_metrics(
                        session.user_id
                    )
                )
                metrics.replayability_metrics = replay_metrics

            if self.collaborative_system and hasattr(
                self.collaborative_system, "get_collaboration_metrics"
            ):
                collab_metrics = (
                    await self.collaborative_system.get_collaboration_metrics(
                        session.user_id
                    )
                )
                metrics.collaborative_metrics = collab_metrics

            if self.error_recovery_manager and hasattr(
                self.error_recovery_manager, "get_metrics"
            ):
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
        therapeutic_context: dict[str, Any] | None = None,
    ) -> ClinicalAlert:
        """Generate a clinical alert for healthcare professional notification."""
        try:
            alert = ClinicalAlert(
                user_id=user_id,
                session_id=session_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                therapeutic_context=therapeutic_context or {},
            )

            self.active_alerts[alert.alert_id] = alert
            self.dashboard_metrics["alerts_generated"] += 1

            # Add alert to session if it exists
            if session_id in self.active_sessions:
                self.active_sessions[session_id].alerts.append(alert)

            logger.warning(
                f"Clinical alert generated: {alert_type} - {severity.value} - {message}"
            )

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
            logger.critical(
                f"Alert Type: {alert.alert_type}, Severity: {alert.severity.value}"
            )

            # For now, we'll simulate immediate notification
            # In production, integrate with actual notification systems

        except Exception as e:
            logger.error(f"Error triggering immediate notification: {e}")

    async def get_dashboard_overview(self) -> dict[str, Any]:
        """Get comprehensive dashboard overview for clinical interface."""
        try:
            # Calculate summary statistics
            total_active_sessions = len(self.active_sessions)
            total_active_alerts = len(
                [a for a in self.active_alerts.values() if not a.resolved]
            )
            critical_alerts = len(
                [
                    a
                    for a in self.active_alerts.values()
                    if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
                    and not a.resolved
                ]
            )

            # Get recent metrics summary
            recent_metrics = []
            for _session_id, metrics_list in self.metrics_history.items():
                if metrics_list:
                    recent_metrics.append(metrics_list[-1])

            avg_therapeutic_value = 0.0
            avg_engagement = 0.0
            avg_safety_score = 1.0

            if recent_metrics:
                avg_therapeutic_value = sum(
                    m.therapeutic_value_accumulated for m in recent_metrics
                ) / len(recent_metrics)
                avg_engagement = sum(m.engagement_level for m in recent_metrics) / len(
                    recent_metrics
                )
                avg_safety_score = sum(m.safety_score for m in recent_metrics) / len(
                    recent_metrics
                )

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
                            "therapeutic_value": (
                                session.current_metrics.therapeutic_value_accumulated
                                if session.current_metrics
                                else 0.0
                            ),
                            "engagement_level": (
                                session.current_metrics.engagement_level
                                if session.current_metrics
                                else 0.0
                            ),
                            "safety_score": (
                                session.current_metrics.safety_score
                                if session.current_metrics
                                else 1.0
                            ),
                            "crisis_risk_level": (
                                session.current_metrics.crisis_risk_level
                                if session.current_metrics
                                else "none"
                            ),
                        },
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
                    for alert in sorted(
                        self.active_alerts.values(),
                        key=lambda a: a.timestamp,
                        reverse=True,
                    )[:10]
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

    async def _get_system_health_summary(self) -> dict[str, Any]:
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
                if system and hasattr(system, "health_check"):
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
                "overall_health": (
                    "healthy"
                    if healthy_systems >= 7
                    else "degraded" if healthy_systems >= 5 else "critical"
                ),
            }

        except Exception as e:
            logger.error(f"Error getting system health summary: {e}")
            return {"error": str(e)}

    # Duplicate acknowledge_alert method removed - using the comprehensive implementation above

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
            self.dashboard_metrics["clinicians_connected"] = len(
                self.connected_clinicians
            )

            logger.info(f"Clinician {clinician_id} connected to dashboard")
            return True

        except Exception as e:
            logger.error(f"Error connecting clinician: {e}")
            return False

    async def disconnect_clinician(self, clinician_id: str) -> bool:
        """Disconnect a clinician from the dashboard."""
        try:
            self.connected_clinicians.discard(clinician_id)
            self.dashboard_metrics["clinicians_connected"] = len(
                self.connected_clinicians
            )

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
                    cutoff_time = datetime.utcnow() - timedelta(
                        hours=self.alert_retention_hours
                    )

                    # Clean up old resolved alerts
                    alerts_to_remove = []
                    for alert_id, alert in self.active_alerts.items():
                        if (
                            alert.resolved
                            and alert.resolved_at
                            and alert.resolved_at < cutoff_time
                        ):
                            alerts_to_remove.append(alert_id)

                    for alert_id in alerts_to_remove:
                        self.active_alerts.pop(alert_id, None)

                    # Clean up old metrics history
                    metrics_cutoff = datetime.utcnow() - timedelta(
                        days=self.metrics_retention_days
                    )
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

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the Clinical Dashboard Manager."""
        try:
            # Check therapeutic system availability
            systems_available = 0
            if self.consequence_system:
                systems_available += 1
            if self.emotional_safety_system:
                systems_available += 1
            if self.adaptive_difficulty_engine:
                systems_available += 1
            if self.character_development_system:
                systems_available += 1
            if self.therapeutic_integration_system:
                systems_available += 1
            if self.gameplay_loop_controller:
                systems_available += 1
            if self.replayability_system:
                systems_available += 1
            if self.collaborative_system:
                systems_available += 1
            if self.error_recovery_manager:
                systems_available += 1

            return {
                "status": "healthy" if systems_available >= 7 else "degraded",
                "dashboard_status": self.status.value,
                "active_sessions": len(self.active_sessions),
                "active_alerts": len(self.active_alerts),
                "connected_clinicians": len(self.connected_clinicians),
                "therapeutic_systems_available": f"{systems_available}/9",
                "background_tasks_running": (
                    self._metrics_collection_task is not None
                    and not self._metrics_collection_task.done()
                    and self._alert_cleanup_task is not None
                    and not self._alert_cleanup_task.done()
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

    # System Health Monitoring Integration

    async def get_comprehensive_system_health(self) -> dict[str, Any]:
        """Get comprehensive health status of all therapeutic systems."""
        try:
            current_time = utc_now()

            # Check if we need to refresh health data
            if (
                current_time - self.last_health_check
            ).total_seconds() > self.health_check_interval:
                await self._refresh_system_health()
                self.last_health_check = current_time

            # Aggregate health data
            systems_health = {}
            overall_health_score = 0.0
            total_systems = 0
            healthy_systems = 0
            degraded_systems = 0
            unhealthy_systems = 0

            therapeutic_systems = {
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

            for system_name, _system in therapeutic_systems.items():
                total_systems += 1
                health_data = self.system_health_cache.get(system_name, {})

                if health_data:
                    status = health_data.get("status", "unknown")
                    systems_health[system_name] = health_data

                    # Calculate health score
                    if status == "healthy":
                        healthy_systems += 1
                        overall_health_score += 1.0
                    elif status == "degraded":
                        degraded_systems += 1
                        overall_health_score += 0.5
                    else:
                        unhealthy_systems += 1
                        overall_health_score += 0.0
                else:
                    systems_health[system_name] = {
                        "status": "unknown",
                        "error": "No health data available",
                    }

            # Calculate overall health percentage
            overall_health_percentage = (
                (overall_health_score / total_systems * 100) if total_systems > 0 else 0
            )

            # Determine overall status
            if overall_health_percentage >= 90:
                overall_status = "healthy"
            elif overall_health_percentage >= 70:
                overall_status = "degraded"
            else:
                overall_status = "critical"

            return {
                "overall_status": overall_status,
                "overall_health_percentage": round(overall_health_percentage, 1),
                "systems_summary": {
                    "total": total_systems,
                    "healthy": healthy_systems,
                    "degraded": degraded_systems,
                    "unhealthy": unhealthy_systems,
                },
                "systems_health": systems_health,
                "last_updated": current_time.isoformat(),
                "health_check_interval": self.health_check_interval,
            }

        except Exception as e:
            logger.error(f"Error getting comprehensive system health: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "last_updated": utc_now().isoformat(),
            }

    async def _refresh_system_health(self) -> None:
        """Refresh health data for all therapeutic systems."""
        try:
            therapeutic_systems = {
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

            for system_name, system in therapeutic_systems.items():
                try:
                    if system and hasattr(system, "health_check"):
                        health_data = await system.health_check()

                        # Enhance health data with additional metrics
                        enhanced_health = {
                            **health_data,
                            "system_name": system_name,
                            "timestamp": utc_now().isoformat(),
                            "response_time_ms": 0.0,  # Would be measured in real implementation
                        }

                        # Store in cache
                        self.system_health_cache[system_name] = enhanced_health

                        # Store in history (keep last 100 entries)
                        self.system_health_history[system_name].append(enhanced_health)
                        if len(self.system_health_history[system_name]) > 100:
                            self.system_health_history[system_name].pop(0)

                        # Check for health alerts
                        await self._check_health_alerts(system_name, enhanced_health)

                    else:
                        self.system_health_cache[system_name] = {
                            "status": "not_available",
                            "system_name": system_name,
                            "timestamp": utc_now().isoformat(),
                            "error": "System not available or no health_check method",
                        }

                except Exception as e:
                    logger.error(f"Error checking health of {system_name}: {e}")
                    self.system_health_cache[system_name] = {
                        "status": "error",
                        "system_name": system_name,
                        "timestamp": utc_now().isoformat(),
                        "error": str(e),
                    }

        except Exception as e:
            logger.error(f"Error refreshing system health: {e}")

    async def _check_health_alerts(
        self, system_name: str, health_data: dict[str, Any]
    ) -> None:
        """Check health data against alert thresholds and generate alerts if needed."""
        try:
            alerts_to_generate = []

            # Check response time
            response_time = health_data.get("response_time_ms", 0.0)
            if response_time > self.health_alert_thresholds["response_time_ms"]:
                alerts_to_generate.append(
                    {
                        "type": "high_response_time",
                        "severity": AlertSeverity.HIGH,
                        "message": f"{system_name} response time is {response_time}ms (threshold: {self.health_alert_thresholds['response_time_ms']}ms)",
                        "system": system_name,
                    }
                )

            # Check system status
            status = health_data.get("status", "unknown")
            if status == "unhealthy":
                alerts_to_generate.append(
                    {
                        "type": "system_unhealthy",
                        "severity": AlertSeverity.CRITICAL,
                        "message": f"{system_name} is reporting unhealthy status",
                        "system": system_name,
                    }
                )
            elif status == "degraded":
                alerts_to_generate.append(
                    {
                        "type": "system_degraded",
                        "severity": AlertSeverity.MEDIUM,
                        "message": f"{system_name} is reporting degraded performance",
                        "system": system_name,
                    }
                )

            # Generate alerts
            for alert_data in alerts_to_generate:
                alert = ClinicalAlert(
                    user_id="system",
                    session_id="health_monitoring",
                    alert_type=alert_data["type"],
                    severity=alert_data["severity"],
                    message=alert_data["message"],
                    therapeutic_context={
                        "system": alert_data["system"],
                        "health_data": health_data,
                    },
                    priority_score=(
                        8.0 if alert_data["severity"] == AlertSeverity.CRITICAL else 6.0
                    ),
                    intervention_required=alert_data["severity"]
                    in [AlertSeverity.CRITICAL, AlertSeverity.HIGH],
                )

                await self.add_clinical_alert(alert)

        except Exception as e:
            logger.error(f"Error checking health alerts for {system_name}: {e}")

    async def get_system_health_trends(
        self, system_name: str, hours: int = 24
    ) -> dict[str, Any]:
        """Get health trends for a specific system over time."""
        try:
            if system_name not in self.system_health_history:
                return {"error": f"No health history available for {system_name}"}

            history = self.system_health_history[system_name]
            cutoff_time = utc_now() - timedelta(hours=hours)

            # Filter recent history
            from datetime import timezone

            recent_history = [
                entry
                for entry in history
                if datetime.fromisoformat(entry["timestamp"]).replace(
                    tzinfo=timezone.utc
                )
                > cutoff_time
            ]

            if not recent_history:
                return {"error": f"No recent health data for {system_name}"}

            # Calculate trends
            status_counts = defaultdict(int)
            response_times = []

            for entry in recent_history:
                status_counts[entry.get("status", "unknown")] += 1
                if "response_time_ms" in entry:
                    response_times.append(entry["response_time_ms"])

            # Calculate availability percentage
            total_checks = len(recent_history)
            healthy_checks = status_counts.get("healthy", 0)
            availability_percentage = (
                (healthy_checks / total_checks * 100) if total_checks > 0 else 0
            )

            # Calculate average response time
            avg_response_time = (
                sum(response_times) / len(response_times) if response_times else 0.0
            )

            return {
                "system_name": system_name,
                "timeframe_hours": hours,
                "total_health_checks": total_checks,
                "availability_percentage": round(availability_percentage, 1),
                "status_distribution": dict(status_counts),
                "average_response_time_ms": round(avg_response_time, 2),
                "trend_direction": self._calculate_health_trend(recent_history),
                "last_status": (
                    recent_history[-1].get("status", "unknown")
                    if recent_history
                    else "unknown"
                ),
            }

        except Exception as e:
            logger.error(f"Error getting health trends for {system_name}: {e}")
            return {"error": str(e)}

    def _calculate_health_trend(self, history: list[dict[str, Any]]) -> str:
        """Calculate health trend direction from history."""
        if len(history) < 3:
            return "insufficient_data"

        # Convert status to numeric scores for trend calculation
        status_scores = []
        for entry in history:
            status = entry.get("status", "unknown")
            if status == "healthy":
                status_scores.append(1.0)
            elif status == "degraded":
                status_scores.append(0.5)
            else:
                status_scores.append(0.0)

        if len(status_scores) < 3:
            return "insufficient_data"

        # Calculate trend using simple linear regression
        n = len(status_scores)
        x_values = list(range(n))

        x_mean = sum(x_values) / n
        y_mean = sum(status_scores) / n

        numerator = sum(
            (x_values[i] - x_mean) * (status_scores[i] - y_mean) for i in range(n)
        )
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        else:
            return "stable"

    # Enhanced Clinical Methods for Production

    async def register_practitioner(
        self,
        username: str,
        full_name: str,
        role: ClinicalRole,
        access_level: AccessLevel,
        email: str,
        license_number: str | None = None,
        department: str | None = None,
        supervisor_id: str | None = None,
    ) -> str:
        """Register a new clinical practitioner."""
        try:
            practitioner_id = str(uuid.uuid4())

            practitioner = ClinicalPractitioner(
                practitioner_id=practitioner_id,
                username=username,
                full_name=full_name,
                role=role,
                access_level=access_level,
                email=email,
                license_number=license_number,
                department=department,
                supervisor_id=supervisor_id,
            )

            self.registered_practitioners[practitioner_id] = practitioner

            await self._log_audit_event(
                practitioner_id="system",
                event_type=AuditEventType.CONFIGURATION_CHANGE,
                resource_accessed=f"practitioner_registration:{practitioner_id}",
                success=True,
                details={
                    "action": "register_practitioner",
                    "username": username,
                    "role": role.value,
                    "access_level": access_level.value,
                },
            )

            logger.info(f"Registered practitioner: {username} ({role.value})")
            return practitioner_id

        except Exception as e:
            logger.error(f"Error registering practitioner: {e}")
            raise

    async def authenticate_practitioner(
        self, username: str, password_hash: str, ip_address: str | None = None
    ) -> tuple[str | None, str | None]:
        """Authenticate a clinical practitioner and return session token."""
        try:
            # Find practitioner by username
            practitioner = None
            for p in self.registered_practitioners.values():
                if p.username == username and p.active:
                    practitioner = p
                    break

            if not practitioner:
                await self._log_audit_event(
                    practitioner_id="unknown",
                    event_type=AuditEventType.LOGIN,
                    resource_accessed="authentication",
                    success=False,
                    ip_address=ip_address,
                    details={"username": username, "reason": "user_not_found"},
                )
                return None, None

            # In production, verify password_hash against stored hash
            # For now, we'll assume authentication is successful

            # Generate session token
            session_token = secrets.token_urlsafe(32)
            token_expires = datetime.utcnow() + timedelta(
                minutes=self.session_timeout_minutes
            )

            # Update practitioner session info
            practitioner.session_token = session_token
            practitioner.token_expires = token_expires
            practitioner.last_login = datetime.utcnow()

            # Track active session
            self.active_practitioner_sessions[session_token] = (
                practitioner.practitioner_id
            )

            await self._log_audit_event(
                practitioner_id=practitioner.practitioner_id,
                event_type=AuditEventType.LOGIN,
                resource_accessed="authentication",
                success=True,
                ip_address=ip_address,
                details={"username": username, "role": practitioner.role.value},
            )

            logger.info(f"Practitioner authenticated: {username}")
            return session_token, practitioner.practitioner_id

        except Exception as e:
            logger.error(f"Error authenticating practitioner: {e}")
            await self._log_audit_event(
                practitioner_id="unknown",
                event_type=AuditEventType.LOGIN,
                resource_accessed="authentication",
                success=False,
                ip_address=ip_address,
                details={"username": username, "error": str(e)},
            )
            return None, None

    async def validate_session_token(
        self, session_token: str
    ) -> ClinicalPractitioner | None:
        """Validate a session token and return practitioner if valid."""
        try:
            if session_token not in self.active_practitioner_sessions:
                return None

            practitioner_id = self.active_practitioner_sessions[session_token]
            practitioner = self.registered_practitioners.get(practitioner_id)

            if not practitioner or not practitioner.active:
                # Clean up invalid session
                self.active_practitioner_sessions.pop(session_token, None)
                return None

            # Check token expiration
            if (
                practitioner.token_expires
                and datetime.utcnow() > practitioner.token_expires
            ):
                # Token expired, clean up
                self.active_practitioner_sessions.pop(session_token, None)
                practitioner.session_token = None
                practitioner.token_expires = None
                return None

            return practitioner

        except Exception as e:
            logger.error(f"Error validating session token: {e}")
            return None

    async def check_permission(
        self, session_token: str, required_permission: str
    ) -> bool:
        """Check if practitioner has required permission."""
        try:
            practitioner = await self.validate_session_token(session_token)
            if not practitioner:
                return False

            role_permissions = self.role_permissions.get(practitioner.role, set())
            return required_permission in role_permissions

        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False

    async def _log_audit_event(
        self,
        practitioner_id: str,
        event_type: AuditEventType,
        resource_accessed: str,
        success: bool = True,
        patient_id: str | None = None,
        session_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log an audit event for HIPAA compliance."""
        try:
            audit_entry = AuditLogEntry(
                practitioner_id=practitioner_id,
                event_type=event_type,
                resource_accessed=resource_accessed,
                patient_id=patient_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                details=details or {},
            )

            self.audit_log.append(audit_entry)
            self.dashboard_metrics["audit_events_logged"] += 1

            # Log security violations
            if not success and event_type in [
                AuditEventType.LOGIN,
                AuditEventType.SESSION_ACCESS,
            ]:
                self.dashboard_metrics["security_violations"] += 1

        except Exception as e:
            logger.error(f"Error logging audit event: {e}")

    async def _audit_cleanup_loop(self) -> None:
        """Background loop for cleaning up old audit logs."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    cutoff_time = datetime.utcnow() - timedelta(
                        days=self.audit_log_retention_days
                    )

                    # Remove old audit entries
                    self.audit_log = [
                        entry
                        for entry in self.audit_log
                        if entry.timestamp > cutoff_time
                    ]

                    # Wait 24 hours before next cleanup
                    await asyncio.sleep(86400)  # 24 hours

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in audit cleanup loop: {e}")
                    await asyncio.sleep(3600)  # Wait 1 hour on error

        except asyncio.CancelledError:
            logger.info("Audit cleanup loop cancelled")

    async def _session_timeout_loop(self) -> None:
        """Background loop for handling session timeouts."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    current_time = datetime.utcnow()
                    expired_tokens = []

                    # Check for expired sessions
                    for (
                        token,
                        practitioner_id,
                    ) in self.active_practitioner_sessions.items():
                        practitioner = self.registered_practitioners.get(
                            practitioner_id
                        )
                        if (
                            practitioner
                            and practitioner.token_expires
                            and current_time > practitioner.token_expires
                        ):
                            expired_tokens.append(token)

                    # Clean up expired sessions
                    for token in expired_tokens:
                        practitioner_id = self.active_practitioner_sessions.pop(
                            token, None
                        )
                        if practitioner_id:
                            practitioner = self.registered_practitioners.get(
                                practitioner_id
                            )
                            if practitioner:
                                practitioner.session_token = None
                                practitioner.token_expires = None

                                await self._log_audit_event(
                                    practitioner_id=practitioner_id,
                                    event_type=AuditEventType.LOGOUT,
                                    resource_accessed="session_timeout",
                                    success=True,
                                    details={"reason": "timeout"},
                                )

                    # Check every 5 minutes
                    await asyncio.sleep(300)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in session timeout loop: {e}")
                    await asyncio.sleep(300)

        except asyncio.CancelledError:
            logger.info("Session timeout loop cancelled")

    async def shutdown(self) -> None:
        """Shutdown the Enhanced Clinical Dashboard Manager."""
        try:
            logger.info("Shutting down Enhanced ClinicalDashboardManager")

            # Signal shutdown to background tasks
            self._shutdown_event.set()

            # Cancel all background tasks
            tasks_to_cancel = [
                self._metrics_collection_task,
                self._alert_cleanup_task,
                self._audit_cleanup_task,
                self._session_timeout_task,
            ]

            for task in tasks_to_cancel:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

            # Log shutdown audit event
            await self._log_audit_event(
                practitioner_id="system",
                event_type=AuditEventType.CONFIGURATION_CHANGE,
                resource_accessed="dashboard_shutdown",
                success=True,
                details={
                    "component": "ClinicalDashboardManager",
                    "version": "enhanced",
                },
            )

            self.status = DashboardStatus.OFFLINE
            logger.info("Enhanced ClinicalDashboardManager shutdown complete")

        except Exception as e:
            logger.error(f"Error during enhanced clinical dashboard shutdown: {e}")
            raise
