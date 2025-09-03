"""
Crisis Detection Dashboard Components

Real-time crisis detection dashboard integration with EmotionalSafetySystem,
clinical intervention workflows, and crisis notification systems for
clinical practitioners.
"""

import asyncio
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from ..therapeutic_systems.emotional_safety_system import (
    CrisisIndicator,
    CrisisLevel,
    TherapeuticEmotionalSafetySystem,
)

logger = logging.getLogger(__name__)


class InterventionStatus(Enum):
    """Status of clinical interventions."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class InterventionType(Enum):
    """Types of clinical interventions."""

    IMMEDIATE_CONTACT = "immediate_contact"
    SAFETY_PLANNING = "safety_planning"
    CRISIS_COUNSELING = "crisis_counseling"
    EMERGENCY_SERVICES = "emergency_services"
    FAMILY_NOTIFICATION = "family_notification"
    HOSPITALIZATION = "hospitalization"
    FOLLOW_UP_SCHEDULING = "follow_up_scheduling"


@dataclass
class CrisisEvent:
    """Crisis event detected by the system."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    crisis_level: CrisisLevel = CrisisLevel.NONE
    indicators: list[CrisisIndicator] = field(default_factory=list)
    risk_score: float = 0.0
    user_input: str = ""
    detected_at: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: float = 0.0
    assessment_data: dict[str, Any] = field(default_factory=dict)
    intervention_required: bool = False
    escalation_needed: bool = False


@dataclass
class ClinicalIntervention:
    """Clinical intervention for crisis response."""

    intervention_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    crisis_event_id: str = ""
    user_id: str = ""
    intervention_type: InterventionType = InterventionType.IMMEDIATE_CONTACT
    status: InterventionStatus = InterventionStatus.PENDING
    assigned_practitioner: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: list[str] = field(default_factory=list)
    outcome: str | None = None
    follow_up_required: bool = False
    follow_up_date: datetime | None = None


@dataclass
class CrisisNotification:
    """Crisis notification for clinical practitioners."""

    notification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    crisis_event_id: str = ""
    practitioner_id: str = ""
    notification_type: str = "crisis_alert"
    priority: str = "high"
    message: str = ""
    sent_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_at: datetime | None = None
    response_required: bool = True
    response_deadline: datetime | None = None


class CrisisDetectionDashboard:
    """
    Crisis Detection Dashboard Components for clinical practitioners.

    Integrates with EmotionalSafetySystem to provide:
    - Real-time crisis detection monitoring
    - Clinical intervention workflow management
    - Crisis notification system
    - Risk assessment visualization
    - Intervention tracking and outcomes
    """

    def __init__(self, emotional_safety_system: TherapeuticEmotionalSafetySystem):
        """Initialize crisis detection dashboard."""
        self.emotional_safety_system = emotional_safety_system

        # Crisis event tracking
        self.active_crisis_events: dict[str, CrisisEvent] = {}
        self.crisis_history: dict[str, list[CrisisEvent]] = defaultdict(list)

        # Intervention management
        self.active_interventions: dict[str, ClinicalIntervention] = {}
        self.intervention_history: dict[str, list[ClinicalIntervention]] = defaultdict(
            list
        )

        # Notification system
        self.pending_notifications: dict[str, CrisisNotification] = {}
        self.notification_history: dict[str, list[CrisisNotification]] = defaultdict(
            list
        )

        # Crisis monitoring configuration
        self.crisis_response_timeout = timedelta(minutes=5)
        self.high_risk_escalation_timeout = timedelta(minutes=2)
        self.critical_immediate_response = timedelta(seconds=30)

        # Performance metrics
        self.dashboard_metrics = {
            "crisis_events_detected": 0,
            "interventions_initiated": 0,
            "notifications_sent": 0,
            "average_response_time_ms": 0.0,
            "successful_interventions": 0,
            "escalations_required": 0,
        }

        # Background monitoring
        self._monitoring_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()

        logger.info("CrisisDetectionDashboard initialized")

    async def initialize(self) -> None:
        """Initialize the crisis detection dashboard."""
        try:
            logger.info("Initializing CrisisDetectionDashboard")

            # Start background monitoring
            self._monitoring_task = asyncio.create_task(self._crisis_monitoring_loop())

            logger.info("CrisisDetectionDashboard initialization complete")

        except Exception as e:
            logger.error(f"Error initializing CrisisDetectionDashboard: {e}")
            raise

    async def process_crisis_assessment(
        self,
        user_id: str,
        session_id: str,
        user_input: str,
        session_context: dict[str, Any] | None = None,
        user_history: dict[str, Any] | None = None,
    ) -> CrisisEvent:
        """Process crisis assessment and create crisis event if needed."""
        try:
            start_time = datetime.utcnow()

            # Perform crisis assessment using EmotionalSafetySystem
            assessment = await self.emotional_safety_system.assess_crisis_risk(
                user_id=user_id,
                user_input=user_input,
                session_context=session_context,
                user_history=user_history,
            )

            response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Create crisis event
            crisis_level_str = assessment["crisis_level"].upper()
            crisis_level = CrisisLevel(crisis_level_str)

            crisis_event = CrisisEvent(
                user_id=user_id,
                session_id=session_id,
                crisis_level=crisis_level,
                indicators=[
                    CrisisIndicator(ind) for ind in assessment.get("indicators", [])
                ],
                risk_score=assessment.get("risk_score", 0.0),
                user_input=user_input,
                response_time_ms=response_time_ms,
                assessment_data=assessment,
                intervention_required=assessment.get("immediate_intervention", False),
                escalation_needed=crisis_level
                in [CrisisLevel.HIGH, CrisisLevel.CRITICAL],
            )

            # Store crisis event if crisis detected
            if assessment.get("crisis_detected", False):
                self.active_crisis_events[crisis_event.event_id] = crisis_event
                self.crisis_history[user_id].append(crisis_event)
                self.dashboard_metrics["crisis_events_detected"] += 1

                # Trigger crisis response workflow
                await self._trigger_crisis_response(crisis_event)

                logger.critical(
                    f"Crisis event created: {crisis_event.event_id} for user {user_id}"
                )

            return crisis_event

        except Exception as e:
            logger.error(f"Error processing crisis assessment: {e}")
            raise

    async def _trigger_crisis_response(self, crisis_event: CrisisEvent) -> None:
        """Trigger appropriate crisis response based on crisis level."""
        try:
            # Determine intervention types based on crisis level
            intervention_types = self._determine_intervention_types(crisis_event)

            # Create interventions
            for intervention_type in intervention_types:
                intervention = ClinicalIntervention(
                    crisis_event_id=crisis_event.event_id,
                    user_id=crisis_event.user_id,
                    intervention_type=intervention_type,
                    follow_up_required=crisis_event.crisis_level
                    in [CrisisLevel.HIGH, CrisisLevel.CRITICAL],
                )

                self.active_interventions[intervention.intervention_id] = intervention
                self.intervention_history[crisis_event.user_id].append(intervention)
                self.dashboard_metrics["interventions_initiated"] += 1

            # Send notifications to practitioners
            await self._send_crisis_notifications(crisis_event)

            # Set up monitoring for response timeouts
            await self._schedule_crisis_monitoring(crisis_event)

        except Exception as e:
            logger.error(f"Error triggering crisis response: {e}")

    def _determine_intervention_types(
        self, crisis_event: CrisisEvent
    ) -> list[InterventionType]:
        """Determine appropriate intervention types based on crisis event."""
        interventions = []

        if crisis_event.crisis_level == CrisisLevel.CRITICAL:
            interventions.extend(
                [
                    InterventionType.IMMEDIATE_CONTACT,
                    InterventionType.EMERGENCY_SERVICES,
                    InterventionType.SAFETY_PLANNING,
                    InterventionType.FAMILY_NOTIFICATION,
                ]
            )
        elif crisis_event.crisis_level == CrisisLevel.HIGH:
            interventions.extend(
                [
                    InterventionType.IMMEDIATE_CONTACT,
                    InterventionType.CRISIS_COUNSELING,
                    InterventionType.SAFETY_PLANNING,
                    InterventionType.FOLLOW_UP_SCHEDULING,
                ]
            )
        elif crisis_event.crisis_level == CrisisLevel.MODERATE:
            interventions.extend(
                [
                    InterventionType.CRISIS_COUNSELING,
                    InterventionType.FOLLOW_UP_SCHEDULING,
                ]
            )

        # Add specific interventions based on indicators
        if CrisisIndicator.SUICIDE_IDEATION in crisis_event.indicators:
            if InterventionType.SAFETY_PLANNING not in interventions:
                interventions.append(InterventionType.SAFETY_PLANNING)

        if CrisisIndicator.SELF_HARM in crisis_event.indicators:
            if InterventionType.IMMEDIATE_CONTACT not in interventions:
                interventions.append(InterventionType.IMMEDIATE_CONTACT)

        return interventions

    async def _send_crisis_notifications(self, crisis_event: CrisisEvent) -> None:
        """Send crisis notifications to appropriate practitioners."""
        try:
            # Determine notification priority and deadline
            if crisis_event.crisis_level == CrisisLevel.CRITICAL:
                priority = "critical"
                deadline = datetime.utcnow() + self.critical_immediate_response
            elif crisis_event.crisis_level == CrisisLevel.HIGH:
                priority = "high"
                deadline = datetime.utcnow() + self.high_risk_escalation_timeout
            else:
                priority = "medium"
                deadline = datetime.utcnow() + self.crisis_response_timeout

            # Create notification message
            message = self._create_crisis_notification_message(crisis_event)

            # For now, create a general notification (in production, would target specific practitioners)
            notification = CrisisNotification(
                crisis_event_id=crisis_event.event_id,
                practitioner_id="on_call_practitioner",  # Would be determined by scheduling system
                priority=priority,
                message=message,
                response_deadline=deadline,
            )

            self.pending_notifications[notification.notification_id] = notification
            self.notification_history[crisis_event.user_id].append(notification)
            self.dashboard_metrics["notifications_sent"] += 1

            logger.warning(f"Crisis notification sent: {notification.notification_id}")

        except Exception as e:
            logger.error(f"Error sending crisis notifications: {e}")

    def _create_crisis_notification_message(self, crisis_event: CrisisEvent) -> str:
        """Create crisis notification message for practitioners."""
        indicators_text = ", ".join([ind.value for ind in crisis_event.indicators])

        message = f"""
CRISIS ALERT - {crisis_event.crisis_level.value.upper()}

User ID: {crisis_event.user_id}
Session ID: {crisis_event.session_id}
Crisis Level: {crisis_event.crisis_level.value}
Indicators: {indicators_text}
Risk Score: {crisis_event.risk_score:.2f}
Detected At: {crisis_event.detected_at.strftime('%Y-%m-%d %H:%M:%S')}

User Input Context: "{crisis_event.user_input[:200]}..."

Immediate intervention required: {crisis_event.intervention_required}
Escalation needed: {crisis_event.escalation_needed}
        """.strip()

        return message

    async def _schedule_crisis_monitoring(self, crisis_event: CrisisEvent) -> None:
        """Schedule monitoring for crisis response timeouts."""
        try:
            # This would integrate with a task scheduler in production
            # For now, we'll track the timing requirements

            if crisis_event.crisis_level == CrisisLevel.CRITICAL:
                # Critical events need immediate response
                logger.critical(
                    f"CRITICAL crisis event {crisis_event.event_id} requires immediate response within {self.critical_immediate_response}"
                )
            elif crisis_event.crisis_level == CrisisLevel.HIGH:
                # High-risk events need rapid response
                logger.error(
                    f"HIGH-RISK crisis event {crisis_event.event_id} requires response within {self.high_risk_escalation_timeout}"
                )

        except Exception as e:
            logger.error(f"Error scheduling crisis monitoring: {e}")

    async def _crisis_monitoring_loop(self) -> None:
        """Background loop for monitoring crisis events and interventions."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Monitor active crisis events for timeouts
                    await self._check_crisis_timeouts()

                    # Monitor active interventions for completion
                    await self._check_intervention_status()

                    # Check for notification acknowledgments
                    await self._check_notification_responses()

                    # Wait before next monitoring cycle
                    await asyncio.sleep(30)  # Check every 30 seconds

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in crisis monitoring loop: {e}")
                    await asyncio.sleep(30)

        except asyncio.CancelledError:
            logger.info("Crisis monitoring loop cancelled")

    async def _check_crisis_timeouts(self) -> None:
        """Check for crisis events that have exceeded response timeouts."""
        try:
            current_time = datetime.utcnow()

            for crisis_event in list(self.active_crisis_events.values()):
                # Check if critical events have exceeded immediate response time
                if crisis_event.crisis_level == CrisisLevel.CRITICAL:
                    if (
                        current_time - crisis_event.detected_at
                        > self.critical_immediate_response
                    ):
                        await self._escalate_crisis_event(
                            crisis_event, "Critical response timeout exceeded"
                        )

                # Check if high-risk events have exceeded escalation timeout
                elif crisis_event.crisis_level == CrisisLevel.HIGH:
                    if (
                        current_time - crisis_event.detected_at
                        > self.high_risk_escalation_timeout
                    ):
                        await self._escalate_crisis_event(
                            crisis_event, "High-risk escalation timeout exceeded"
                        )

        except Exception as e:
            logger.error(f"Error checking crisis timeouts: {e}")

    async def _check_intervention_status(self) -> None:
        """Check status of active interventions."""
        try:
            # In production, this would check with external systems
            # For now, we'll simulate intervention progress tracking
            pass

        except Exception as e:
            logger.error(f"Error checking intervention status: {e}")

    async def _check_notification_responses(self) -> None:
        """Check for notification acknowledgments and responses."""
        try:
            current_time = datetime.utcnow()

            for notification in list(self.pending_notifications.values()):
                if (
                    notification.response_deadline
                    and current_time > notification.response_deadline
                    and not notification.acknowledged
                ):

                    # Escalate unacknowledged notifications
                    await self._escalate_notification(notification)

        except Exception as e:
            logger.error(f"Error checking notification responses: {e}")

    async def _escalate_crisis_event(
        self, crisis_event: CrisisEvent, reason: str
    ) -> None:
        """Escalate crisis event due to timeout or other criteria."""
        try:
            logger.critical(
                f"Escalating crisis event {crisis_event.event_id}: {reason}"
            )

            # Create escalation intervention
            escalation_intervention = ClinicalIntervention(
                crisis_event_id=crisis_event.event_id,
                user_id=crisis_event.user_id,
                intervention_type=InterventionType.EMERGENCY_SERVICES,
                status=InterventionStatus.PENDING,
                notes=[f"Escalated due to: {reason}"],
            )

            self.active_interventions[escalation_intervention.intervention_id] = (
                escalation_intervention
            )
            self.dashboard_metrics["escalations_required"] += 1

            # Send high-priority notification
            escalation_notification = CrisisNotification(
                crisis_event_id=crisis_event.event_id,
                practitioner_id="emergency_coordinator",
                notification_type="crisis_escalation",
                priority="critical",
                message=f"ESCALATION: {reason}\n\nOriginal Crisis: {crisis_event.crisis_level.value}\nUser: {crisis_event.user_id}",
                response_required=True,
                response_deadline=datetime.utcnow() + timedelta(minutes=1),
            )

            self.pending_notifications[escalation_notification.notification_id] = (
                escalation_notification
            )

        except Exception as e:
            logger.error(f"Error escalating crisis event: {e}")

    async def _escalate_notification(self, notification: CrisisNotification) -> None:
        """Escalate unacknowledged notification."""
        try:
            logger.warning(
                f"Escalating unacknowledged notification {notification.notification_id}"
            )

            # Create escalation notification
            escalation = CrisisNotification(
                crisis_event_id=notification.crisis_event_id,
                practitioner_id="supervisor",
                notification_type="notification_escalation",
                priority="critical",
                message=f"UNACKNOWLEDGED CRISIS NOTIFICATION\n\nOriginal notification: {notification.notification_id}\nSent at: {notification.sent_at}\nDeadline: {notification.response_deadline}",
                response_required=True,
                response_deadline=datetime.utcnow() + timedelta(minutes=2),
            )

            self.pending_notifications[escalation.notification_id] = escalation

        except Exception as e:
            logger.error(f"Error escalating notification: {e}")

    # Dashboard Interface Methods

    async def get_active_crisis_events(self) -> list[dict[str, Any]]:
        """Get all active crisis events for dashboard display."""
        try:
            events = []
            for crisis_event in self.active_crisis_events.values():
                events.append(
                    {
                        "event_id": crisis_event.event_id,
                        "user_id": crisis_event.user_id,
                        "session_id": crisis_event.session_id,
                        "crisis_level": crisis_event.crisis_level.value,
                        "indicators": [ind.value for ind in crisis_event.indicators],
                        "risk_score": crisis_event.risk_score,
                        "detected_at": crisis_event.detected_at.isoformat(),
                        "response_time_ms": crisis_event.response_time_ms,
                        "intervention_required": crisis_event.intervention_required,
                        "escalation_needed": crisis_event.escalation_needed,
                    }
                )

            # Sort by crisis level and detection time
            events.sort(
                key=lambda x: (
                    {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3, "NONE": 4}.get(
                        x["crisis_level"], 5
                    ),
                    x["detected_at"],
                )
            )

            return events

        except Exception as e:
            logger.error(f"Error getting active crisis events: {e}")
            return []

    async def get_pending_interventions(self) -> list[dict[str, Any]]:
        """Get all pending interventions for dashboard display."""
        try:
            interventions = []
            for intervention in self.active_interventions.values():
                if intervention.status == InterventionStatus.PENDING:
                    interventions.append(
                        {
                            "intervention_id": intervention.intervention_id,
                            "crisis_event_id": intervention.crisis_event_id,
                            "user_id": intervention.user_id,
                            "intervention_type": intervention.intervention_type.value,
                            "status": intervention.status.value,
                            "assigned_practitioner": intervention.assigned_practitioner,
                            "created_at": intervention.created_at.isoformat(),
                            "follow_up_required": intervention.follow_up_required,
                            "notes": intervention.notes,
                        }
                    )

            # Sort by creation time (oldest first)
            interventions.sort(key=lambda x: x["created_at"])

            return interventions

        except Exception as e:
            logger.error(f"Error getting pending interventions: {e}")
            return []

    async def get_crisis_dashboard_summary(self) -> dict[str, Any]:
        """Get crisis dashboard summary for clinical overview."""
        try:
            current_time = datetime.utcnow()

            # Count active events by level
            crisis_counts = {
                "CRITICAL": 0,
                "HIGH": 0,
                "MODERATE": 0,
                "LOW": 0,
                "NONE": 0,
            }
            for event in self.active_crisis_events.values():
                crisis_counts[event.crisis_level.value] += 1

            # Count pending interventions by type
            intervention_counts = {}
            for intervention in self.active_interventions.values():
                if intervention.status == InterventionStatus.PENDING:
                    intervention_type = intervention.intervention_type.value
                    intervention_counts[intervention_type] = (
                        intervention_counts.get(intervention_type, 0) + 1
                    )

            # Count unacknowledged notifications
            unacknowledged_notifications = len(
                [n for n in self.pending_notifications.values() if not n.acknowledged]
            )

            # Calculate response time metrics
            response_times = [
                event.response_time_ms for event in self.active_crisis_events.values()
            ]
            avg_response_time = (
                sum(response_times) / len(response_times) if response_times else 0.0
            )

            return {
                "active_crisis_events": len(self.active_crisis_events),
                "crisis_counts_by_level": crisis_counts,
                "pending_interventions": len(
                    [
                        i
                        for i in self.active_interventions.values()
                        if i.status == InterventionStatus.PENDING
                    ]
                ),
                "intervention_counts_by_type": intervention_counts,
                "unacknowledged_notifications": unacknowledged_notifications,
                "average_response_time_ms": round(avg_response_time, 2),
                "dashboard_metrics": self.dashboard_metrics,
                "last_updated": current_time.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting crisis dashboard summary: {e}")
            return {"error": str(e)}

    async def acknowledge_notification(
        self, notification_id: str, practitioner_id: str
    ) -> bool:
        """Acknowledge a crisis notification."""
        try:
            if notification_id in self.pending_notifications:
                notification = self.pending_notifications[notification_id]
                notification.acknowledged = True
                notification.acknowledged_at = datetime.utcnow()

                logger.info(
                    f"Notification {notification_id} acknowledged by {practitioner_id}"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Error acknowledging notification: {e}")
            return False

    async def update_intervention_status(
        self,
        intervention_id: str,
        status: InterventionStatus,
        practitioner_id: str,
        notes: str | None = None,
    ) -> bool:
        """Update intervention status."""
        try:
            if intervention_id in self.active_interventions:
                intervention = self.active_interventions[intervention_id]
                intervention.status = status
                intervention.assigned_practitioner = practitioner_id

                if (
                    status == InterventionStatus.IN_PROGRESS
                    and not intervention.started_at
                ):
                    intervention.started_at = datetime.utcnow()
                elif status == InterventionStatus.COMPLETED:
                    intervention.completed_at = datetime.utcnow()
                    self.dashboard_metrics["successful_interventions"] += 1

                if notes:
                    intervention.notes.append(
                        f"{datetime.utcnow().isoformat()}: {notes}"
                    )

                logger.info(
                    f"Intervention {intervention_id} updated to {status.value} by {practitioner_id}"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Error updating intervention status: {e}")
            return False

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of crisis detection dashboard."""
        try:
            return {
                "status": "healthy",
                "service": "crisis_detection_dashboard",
                "active_crisis_events": len(self.active_crisis_events),
                "active_interventions": len(self.active_interventions),
                "pending_notifications": len(self.pending_notifications),
                "monitoring_task_running": self._monitoring_task
                and not self._monitoring_task.done(),
                "metrics": self.dashboard_metrics,
            }

        except Exception as e:
            logger.error(f"Error in crisis detection dashboard health check: {e}")
            return {
                "status": "unhealthy",
                "service": "crisis_detection_dashboard",
                "error": str(e),
            }

    async def shutdown(self) -> None:
        """Shutdown the crisis detection dashboard."""
        try:
            logger.info("Shutting down CrisisDetectionDashboard")

            # Signal shutdown
            self._shutdown_event.set()

            # Cancel monitoring task
            if self._monitoring_task and not self._monitoring_task.done():
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass

            logger.info("CrisisDetectionDashboard shutdown complete")

        except Exception as e:
            logger.error(f"Error during crisis detection dashboard shutdown: {e}")
            raise
