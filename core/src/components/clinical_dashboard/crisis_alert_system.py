"""
Crisis Alert System

Specialized alert system for clinical crisis detection and immediate notification,
integrating with the EmotionalSafetySystem for real-time crisis monitoring.
"""

import asyncio
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CrisisLevel(Enum):
    """Crisis severity levels for clinical escalation."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class CrisisType(Enum):
    """Types of clinical crises detected."""
    SUICIDE_IDEATION = "suicide_ideation"
    SELF_HARM = "self_harm"
    SEVERE_DEPRESSION = "severe_depression"
    PANIC_ATTACK = "panic_attack"
    PSYCHOTIC_EPISODE = "psychotic_episode"
    SUBSTANCE_ABUSE = "substance_abuse"
    DOMESTIC_VIOLENCE = "domestic_violence"
    CHILD_ABUSE = "child_abuse"
    EATING_DISORDER = "eating_disorder"
    TRAUMA_RESPONSE = "trauma_response"


@dataclass
class CrisisAlert:
    """Crisis alert for immediate clinical intervention."""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    crisis_type: CrisisType = CrisisType.SUICIDE_IDEATION
    crisis_level: CrisisLevel = CrisisLevel.NONE
    detected_at: datetime = field(default_factory=datetime.utcnow)

    # Crisis detection details
    trigger_indicators: list[str] = field(default_factory=list)
    risk_assessment_score: float = 0.0
    user_input_context: str = ""
    therapeutic_context: dict[str, Any] = field(default_factory=dict)

    # Clinical response tracking
    response_time_seconds: float | None = None
    clinician_notified: bool = False
    clinician_id: str | None = None
    intervention_initiated: bool = False
    intervention_type: str | None = None

    # Follow-up tracking
    follow_up_required: bool = True
    follow_up_scheduled: bool = False
    follow_up_completed: bool = False
    resolution_notes: str = ""


@dataclass
class CrisisProtocol:
    """Crisis response protocol definition."""
    crisis_type: CrisisType
    crisis_level: CrisisLevel
    response_time_target_seconds: float
    notification_channels: list[str]
    intervention_steps: list[str]
    escalation_criteria: dict[str, Any]
    follow_up_requirements: dict[str, Any]


class CrisisAlertSystem:
    """
    Crisis Alert System providing real-time crisis detection and immediate
    clinical notification with integration to EmotionalSafetySystem.
    """

    def __init__(self):
        """Initialize the Crisis Alert System."""
        self.active_crisis_alerts: dict[str, CrisisAlert] = {}
        self.crisis_protocols: dict[CrisisType, dict[CrisisLevel, CrisisProtocol]] = {}
        self.notification_callbacks: list[Callable] = []

        # System references
        self.emotional_safety_system = None
        self.clinical_dashboard_manager = None

        # Configuration
        self.crisis_detection_interval = 1.0  # seconds - real-time monitoring
        self.alert_retention_hours = 72  # Keep crisis alerts for 72 hours
        self.max_response_time_seconds = 30  # Maximum acceptable response time

        # Background monitoring
        self._crisis_monitoring_task = None
        self._shutdown_event = asyncio.Event()

        # Performance metrics
        self.crisis_metrics = {
            "crises_detected": 0,
            "alerts_generated": 0,
            "average_response_time": 0.0,
            "interventions_initiated": 0,
            "false_positives": 0,
            "successful_interventions": 0,
        }

        # Initialize default crisis protocols
        self._initialize_crisis_protocols()

    def _initialize_crisis_protocols(self):
        """Initialize default crisis response protocols."""
        # Suicide ideation protocols
        self.crisis_protocols[CrisisType.SUICIDE_IDEATION] = {
            CrisisLevel.MODERATE: CrisisProtocol(
                crisis_type=CrisisType.SUICIDE_IDEATION,
                crisis_level=CrisisLevel.MODERATE,
                response_time_target_seconds=30.0,
                notification_channels=["clinical_dashboard", "email"],
                intervention_steps=[
                    "Immediate safety assessment",
                    "Engage therapeutic conversation",
                    "Provide crisis resources",
                    "Schedule follow-up within 24 hours"
                ],
                escalation_criteria={"risk_score_threshold": 0.7},
                follow_up_requirements={"within_hours": 24, "type": "clinical_check_in"}
            ),
            CrisisLevel.HIGH: CrisisProtocol(
                crisis_type=CrisisType.SUICIDE_IDEATION,
                crisis_level=CrisisLevel.HIGH,
                response_time_target_seconds=15.0,
                notification_channels=["clinical_dashboard", "sms", "email", "phone"],
                intervention_steps=[
                    "Immediate clinical intervention",
                    "Safety plan activation",
                    "Emergency contact notification",
                    "Consider emergency services",
                    "Continuous monitoring"
                ],
                escalation_criteria={"risk_score_threshold": 0.8},
                follow_up_requirements={"within_hours": 6, "type": "clinical_assessment"}
            ),
            CrisisLevel.CRITICAL: CrisisProtocol(
                crisis_type=CrisisType.SUICIDE_IDEATION,
                crisis_level=CrisisLevel.CRITICAL,
                response_time_target_seconds=5.0,
                notification_channels=["clinical_dashboard", "emergency_alert", "sms", "phone"],
                intervention_steps=[
                    "Immediate emergency intervention",
                    "Emergency services contact",
                    "Safety plan implementation",
                    "Emergency contact notification",
                    "Continuous clinical supervision"
                ],
                escalation_criteria={"immediate_escalation": True},
                follow_up_requirements={"within_hours": 2, "type": "emergency_assessment"}
            ),
        }

        # Self-harm protocols
        self.crisis_protocols[CrisisType.SELF_HARM] = {
            CrisisLevel.MODERATE: CrisisProtocol(
                crisis_type=CrisisType.SELF_HARM,
                crisis_level=CrisisLevel.MODERATE,
                response_time_target_seconds=45.0,
                notification_channels=["clinical_dashboard", "email"],
                intervention_steps=[
                    "Safety assessment",
                    "Harm reduction strategies",
                    "Therapeutic engagement",
                    "Coping skills activation"
                ],
                escalation_criteria={"risk_score_threshold": 0.6},
                follow_up_requirements={"within_hours": 48, "type": "therapeutic_check_in"}
            ),
            CrisisLevel.HIGH: CrisisProtocol(
                crisis_type=CrisisType.SELF_HARM,
                crisis_level=CrisisLevel.HIGH,
                response_time_target_seconds=20.0,
                notification_channels=["clinical_dashboard", "sms", "email"],
                intervention_steps=[
                    "Immediate safety intervention",
                    "Medical assessment if needed",
                    "Crisis counseling",
                    "Safety plan review"
                ],
                escalation_criteria={"risk_score_threshold": 0.75},
                follow_up_requirements={"within_hours": 12, "type": "clinical_assessment"}
            ),
        }

    async def initialize(self):
        """Initialize the Crisis Alert System."""
        try:
            logger.info("Initializing CrisisAlertSystem")

            # Start crisis monitoring task
            self._crisis_monitoring_task = asyncio.create_task(
                self._crisis_monitoring_loop()
            )

            logger.info("CrisisAlertSystem initialization complete")

        except Exception as e:
            logger.error(f"Error initializing CrisisAlertSystem: {e}")
            raise

    def inject_systems(
        self,
        emotional_safety_system=None,
        clinical_dashboard_manager=None
    ):
        """Inject system dependencies."""
        self.emotional_safety_system = emotional_safety_system
        self.clinical_dashboard_manager = clinical_dashboard_manager

        logger.info("Systems injected into CrisisAlertSystem")

    def add_notification_callback(self, callback: Callable):
        """Add a notification callback for crisis alerts."""
        self.notification_callbacks.append(callback)

    async def detect_crisis(
        self,
        user_id: str,
        session_id: str,
        user_input: str,
        session_context: dict[str, Any] | None = None
    ) -> CrisisAlert | None:
        """Detect potential crisis from user input and context."""
        try:
            # Use EmotionalSafetySystem for crisis detection
            if not self.emotional_safety_system:
                logger.warning("EmotionalSafetySystem not available for crisis detection")
                return None

            # Get crisis risk assessment
            safety_result = await self.emotional_safety_system.assess_crisis_risk(
                user_id=user_id,
                user_input=user_input,
                session_context=session_context or {}
            )

            # Check if crisis detected
            if not safety_result.get("crisis_detected", False):
                return None

            # Extract crisis details
            crisis_level_str = safety_result.get("crisis_level", "none")
            crisis_indicators = safety_result.get("crisis_indicators", [])
            risk_score = safety_result.get("risk_assessment_score", 0.0)

            # Map crisis level
            crisis_level = CrisisLevel.NONE
            try:
                crisis_level = CrisisLevel(crisis_level_str.lower())
            except ValueError:
                crisis_level = CrisisLevel.MODERATE  # Default to moderate if unknown

            # Determine crisis type based on indicators
            crisis_type = self._determine_crisis_type(crisis_indicators)

            # Create crisis alert
            crisis_alert = CrisisAlert(
                user_id=user_id,
                session_id=session_id,
                crisis_type=crisis_type,
                crisis_level=crisis_level,
                trigger_indicators=crisis_indicators,
                risk_assessment_score=risk_score,
                user_input_context=user_input,
                therapeutic_context=session_context or {}
            )

            # Store active crisis alert
            self.active_crisis_alerts[crisis_alert.alert_id] = crisis_alert
            self.crisis_metrics["crises_detected"] += 1

            # Trigger immediate response
            await self._trigger_crisis_response(crisis_alert)

            logger.critical(f"Crisis detected: {crisis_type.value} - {crisis_level.value} for user {user_id}")

            return crisis_alert

        except Exception as e:
            logger.error(f"Error detecting crisis: {e}")
            return None

    def _determine_crisis_type(self, indicators: list[str]) -> CrisisType:
        """Determine crisis type based on indicators."""
        # Map indicators to crisis types
        indicator_mapping = {
            "suicide_ideation": CrisisType.SUICIDE_IDEATION,
            "self_harm": CrisisType.SELF_HARM,
            "severe_depression": CrisisType.SEVERE_DEPRESSION,
            "panic_attack": CrisisType.PANIC_ATTACK,
            "psychotic_episode": CrisisType.PSYCHOTIC_EPISODE,
            "substance_abuse": CrisisType.SUBSTANCE_ABUSE,
            "domestic_violence": CrisisType.DOMESTIC_VIOLENCE,
            "child_abuse": CrisisType.CHILD_ABUSE,
            "eating_disorder": CrisisType.EATING_DISORDER,
            "trauma_response": CrisisType.TRAUMA_RESPONSE,
        }

        # Find the most severe crisis type from indicators
        for indicator in indicators:
            if indicator in indicator_mapping:
                return indicator_mapping[indicator]

        # Default to suicide ideation if no specific type found
        return CrisisType.SUICIDE_IDEATION

    async def _trigger_crisis_response(self, crisis_alert: CrisisAlert):
        """Trigger immediate crisis response protocol."""
        try:
            start_time = datetime.utcnow()

            # Get appropriate protocol
            protocol = self._get_crisis_protocol(crisis_alert.crisis_type, crisis_alert.crisis_level)

            if protocol:
                # Notify clinical dashboard
                if self.clinical_dashboard_manager:
                    await self.clinical_dashboard_manager.generate_clinical_alert(
                        user_id=crisis_alert.user_id,
                        session_id=crisis_alert.session_id,
                        alert_type=f"crisis_{crisis_alert.crisis_type.value}",
                        severity=self._map_crisis_to_alert_severity(crisis_alert.crisis_level),
                        message=f"Crisis detected: {crisis_alert.crisis_type.value} - {crisis_alert.crisis_level.value}",
                        therapeutic_context=crisis_alert.therapeutic_context
                    )

                # Execute notification callbacks
                for callback in self.notification_callbacks:
                    try:
                        await callback(crisis_alert, protocol)
                    except Exception as e:
                        logger.error(f"Error in crisis notification callback: {e}")

                # Mark intervention as initiated
                crisis_alert.intervention_initiated = True
                crisis_alert.intervention_type = "crisis_protocol"

                # Calculate response time
                response_time = (datetime.utcnow() - start_time).total_seconds()
                crisis_alert.response_time_seconds = response_time

                # Update metrics
                self.crisis_metrics["alerts_generated"] += 1
                self.crisis_metrics["interventions_initiated"] += 1

                # Update average response time
                current_avg = self.crisis_metrics["average_response_time"]
                total_alerts = self.crisis_metrics["alerts_generated"]
                self.crisis_metrics["average_response_time"] = (
                    (current_avg * (total_alerts - 1) + response_time) / total_alerts
                )

                logger.info(f"Crisis response triggered in {response_time:.3f}s for alert {crisis_alert.alert_id}")

        except Exception as e:
            logger.error(f"Error triggering crisis response: {e}")

    def _get_crisis_protocol(self, crisis_type: CrisisType, crisis_level: CrisisLevel) -> CrisisProtocol | None:
        """Get appropriate crisis protocol for type and level."""
        if crisis_type in self.crisis_protocols:
            if crisis_level in self.crisis_protocols[crisis_type]:
                return self.crisis_protocols[crisis_type][crisis_level]

        return None

    def _map_crisis_to_alert_severity(self, crisis_level: CrisisLevel):
        """Map crisis level to clinical alert severity."""
        from .clinical_dashboard_manager import AlertSeverity

        mapping = {
            CrisisLevel.NONE: AlertSeverity.LOW,
            CrisisLevel.LOW: AlertSeverity.LOW,
            CrisisLevel.MODERATE: AlertSeverity.MEDIUM,
            CrisisLevel.HIGH: AlertSeverity.HIGH,
            CrisisLevel.CRITICAL: AlertSeverity.CRITICAL,
            CrisisLevel.EMERGENCY: AlertSeverity.EMERGENCY,
        }

        return mapping.get(crisis_level, AlertSeverity.MEDIUM)

    async def _crisis_monitoring_loop(self):
        """Background loop for continuous crisis monitoring."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Monitor active crisis alerts for escalation
                    for _alert_id, alert in list(self.active_crisis_alerts.items()):
                        await self._monitor_crisis_alert(alert)

                    # Clean up old resolved alerts
                    await self._cleanup_old_alerts()

                    # Wait for next monitoring cycle
                    await asyncio.sleep(self.crisis_detection_interval)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in crisis monitoring loop: {e}")
                    await asyncio.sleep(self.crisis_detection_interval)

        except asyncio.CancelledError:
            logger.info("Crisis monitoring loop cancelled")

    async def _monitor_crisis_alert(self, alert: CrisisAlert):
        """Monitor individual crisis alert for escalation needs."""
        try:
            # Check if response time exceeded
            if alert.response_time_seconds and alert.response_time_seconds > self.max_response_time_seconds:
                logger.warning(f"Crisis alert {alert.alert_id} exceeded response time target")

            # Check for escalation criteria
            protocol = self._get_crisis_protocol(alert.crisis_type, alert.crisis_level)
            if protocol and protocol.escalation_criteria.get("immediate_escalation", False):
                # Trigger escalation if needed
                await self._escalate_crisis_alert(alert)

        except Exception as e:
            logger.error(f"Error monitoring crisis alert: {e}")

    async def _escalate_crisis_alert(self, alert: CrisisAlert):
        """Escalate crisis alert to higher level of intervention."""
        try:
            logger.critical(f"Escalating crisis alert {alert.alert_id} for user {alert.user_id}")

            # In production, this would trigger:
            # - Emergency services contact
            # - Hospital notification
            # - Emergency contact notification
            # - Supervisor escalation

        except Exception as e:
            logger.error(f"Error escalating crisis alert: {e}")

    async def _cleanup_old_alerts(self):
        """Clean up old resolved crisis alerts."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.alert_retention_hours)

            alerts_to_remove = []
            for alert_id, alert in self.active_crisis_alerts.items():
                if alert.follow_up_completed and alert.detected_at < cutoff_time:
                    alerts_to_remove.append(alert_id)

            for alert_id in alerts_to_remove:
                self.active_crisis_alerts.pop(alert_id, None)

        except Exception as e:
            logger.error(f"Error cleaning up old crisis alerts: {e}")

    async def get_active_crises(self) -> list[dict[str, Any]]:
        """Get all active crisis alerts."""
        try:
            return [
                {
                    "alert_id": alert.alert_id,
                    "user_id": alert.user_id,
                    "session_id": alert.session_id,
                    "crisis_type": alert.crisis_type.value,
                    "crisis_level": alert.crisis_level.value,
                    "detected_at": alert.detected_at.isoformat(),
                    "risk_score": alert.risk_assessment_score,
                    "response_time": alert.response_time_seconds,
                    "intervention_initiated": alert.intervention_initiated,
                    "follow_up_required": alert.follow_up_required,
                }
                for alert in self.active_crisis_alerts.values()
            ]

        except Exception as e:
            logger.error(f"Error getting active crises: {e}")
            return []

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the Crisis Alert System."""
        try:
            return {
                "status": "healthy",
                "active_crisis_alerts": len(self.active_crisis_alerts),
                "crisis_protocols_loaded": len(self.crisis_protocols),
                "notification_callbacks": len(self.notification_callbacks),
                "emotional_safety_system_available": self.emotional_safety_system is not None,
                "clinical_dashboard_available": self.clinical_dashboard_manager is not None,
                "monitoring_active": self._crisis_monitoring_task is not None and not self._crisis_monitoring_task.done(),
                "crisis_metrics": self.crisis_metrics,
            }

        except Exception as e:
            logger.error(f"Error in crisis alert system health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def shutdown(self):
        """Shutdown the Crisis Alert System."""
        try:
            logger.info("Shutting down CrisisAlertSystem")

            # Signal shutdown
            self._shutdown_event.set()

            # Cancel monitoring task
            if self._crisis_monitoring_task:
                self._crisis_monitoring_task.cancel()
                try:
                    await self._crisis_monitoring_task
                except asyncio.CancelledError:
                    pass

            logger.info("CrisisAlertSystem shutdown complete")

        except Exception as e:
            logger.error(f"Error during crisis alert system shutdown: {e}")
            raise
