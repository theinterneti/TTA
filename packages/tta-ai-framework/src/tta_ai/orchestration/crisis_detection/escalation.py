"""Human oversight escalation and notification systems."""

from __future__ import annotations

import logging
import time
from typing import Any

from .enums import CrisisLevel
from .models import CrisisIntervention


class HumanOversightEscalation:
    """Integration points for notifying human therapists or emergency services.

    Manages escalation to human oversight, notification systems, and emergency
    service coordination with comprehensive tracking and reporting.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the Human Oversight Escalation system."""
        self.config = config or self._default_escalation_config()
        self.active_escalations: dict[str, dict[str, Any]] = {}
        self.escalation_history: list[dict[str, Any]] = []

        # Statistics tracking
        self.total_escalations = 0
        self.successful_notifications = 0
        self.failed_notifications = 0
        self.emergency_escalations = 0

        # Initialize logging
        self.logger = logging.getLogger(__name__ + ".HumanOversightEscalation")

    def escalate_to_human(
        self, intervention: CrisisIntervention, escalation_type: str = "standard"
    ) -> dict[str, Any]:
        """Escalate a crisis intervention to human oversight."""
        import uuid

        escalation_id = str(uuid.uuid4())

        escalation = {
            "escalation_id": escalation_id,
            "intervention_id": intervention.intervention_id,
            "escalation_type": escalation_type,
            "crisis_level": intervention.crisis_assessment.crisis_level.value,
            "crisis_types": [
                ct.value for ct in intervention.crisis_assessment.crisis_types
            ],
            "user_id": intervention.user_id,
            "session_id": intervention.session_id,
            "timestamp": time.time(),
            "notifications_sent": [],
            "status": "pending",
            "assigned_human": None,
            "response_received": False,
            "resolution_time": None,
        }

        self.active_escalations[escalation_id] = escalation
        self.total_escalations += 1

        # Send notifications based on escalation type and crisis level
        self._send_notifications(escalation, intervention)

        self.logger.warning(
            f"Human oversight escalation {escalation_id} initiated for intervention {intervention.intervention_id} "
            f"(type: {escalation_type}, level: {intervention.crisis_assessment.crisis_level.value})"
        )

        return escalation

    def escalate_to_emergency_services(
        self, intervention: CrisisIntervention, emergency_type: str = "mental_health"
    ) -> dict[str, Any]:
        """Escalate to emergency services for critical situations."""
        import uuid

        escalation_id = str(uuid.uuid4())

        escalation = {
            "escalation_id": escalation_id,
            "intervention_id": intervention.intervention_id,
            "escalation_type": "emergency_services",
            "emergency_type": emergency_type,
            "crisis_level": intervention.crisis_assessment.crisis_level.value,
            "crisis_types": [
                ct.value for ct in intervention.crisis_assessment.crisis_types
            ],
            "user_id": intervention.user_id,
            "session_id": intervention.session_id,
            "timestamp": time.time(),
            "emergency_contacts": [],
            "status": "critical",
            "response_time_required": "immediate",
            "location_info": intervention.crisis_assessment.context.get(
                "location", "unknown"
            )
            if intervention.crisis_assessment.context
            else "unknown",
        }

        self.active_escalations[escalation_id] = escalation
        self.emergency_escalations += 1

        # Contact emergency services
        self._contact_emergency_services(escalation, intervention)

        self.logger.critical(
            f"EMERGENCY SERVICES ESCALATION {escalation_id} for intervention {intervention.intervention_id} "
            f"(type: {emergency_type}, level: {intervention.crisis_assessment.crisis_level.value})"
        )

        return escalation

    def _send_notifications(
        self, escalation: dict[str, Any], intervention: CrisisIntervention
    ) -> None:
        """Send notifications to appropriate human oversight personnel."""
        crisis_level = intervention.crisis_assessment.crisis_level
        escalation_type = escalation["escalation_type"]

        # Determine notification channels based on crisis level
        channels = self._get_notification_channels(crisis_level, escalation_type)

        for channel in channels:
            try:
                notification_result = self._send_notification(
                    channel, escalation, intervention
                )
                escalation["notifications_sent"].append(notification_result)

                if notification_result["success"]:
                    self.successful_notifications += 1
                else:
                    self.failed_notifications += 1

            except Exception as e:
                self.failed_notifications += 1
                self.logger.error(f"Failed to send notification via {channel}: {e}")

    def _get_notification_channels(
        self, crisis_level: CrisisLevel, escalation_type: str
    ) -> list[str]:
        """Determine appropriate notification channels based on crisis level and type."""
        channels = []

        if crisis_level == CrisisLevel.CRITICAL:
            channels.extend(["sms", "phone", "email", "dashboard", "pager"])
        elif crisis_level == CrisisLevel.HIGH:
            channels.extend(["sms", "email", "dashboard"])
        elif crisis_level == CrisisLevel.MODERATE:
            channels.extend(["email", "dashboard"])
        else:
            channels.append("dashboard")

        # Filter based on configuration
        enabled_channels = self.config.get("notification_channels", {})
        return [
            ch for ch in channels if enabled_channels.get(ch, {}).get("enabled", False)
        ]

    def _send_notification(
        self, channel: str, escalation: dict[str, Any], intervention: CrisisIntervention
    ) -> dict[str, Any]:
        """Send a notification via the specified channel."""
        start_time = time.perf_counter()

        notification = {
            "channel": channel,
            "timestamp": time.time(),
            "success": False,
            "response_time_ms": 0.0,
            "message_id": None,
            "error": None,
        }

        try:
            # Generate notification content
            content = self._generate_notification_content(escalation, intervention)

            # Send via specific channel
            if channel == "email":
                result = self._send_email_notification(content, escalation)
            elif channel == "sms":
                result = self._send_sms_notification(content, escalation)
            elif channel == "phone":
                result = self._send_phone_notification(content, escalation)
            elif channel == "dashboard":
                result = self._send_dashboard_notification(content, escalation)
            elif channel == "pager":
                result = self._send_pager_notification(content, escalation)
            else:
                raise Exception(f"Unknown notification channel: {channel}")

            notification.update(result)
            notification["success"] = True

        except Exception as e:
            notification["error"] = str(e)
            notification["success"] = False

        finally:
            notification["response_time_ms"] = (time.perf_counter() - start_time) * 1000

        return notification

    def _generate_notification_content(
        self, escalation: dict[str, Any], intervention: CrisisIntervention
    ) -> dict[str, Any]:
        """Generate notification content for human oversight."""
        return {
            "subject": f"CRISIS INTERVENTION ESCALATION - {escalation['crisis_level'].upper()}",
            "message": (
                f"Crisis intervention escalation required:\n\n"
                f"Escalation ID: {escalation['escalation_id']}\n"
                f"User ID: {escalation['user_id']}\n"
                f"Session ID: {escalation['session_id']}\n"
                f"Crisis Level: {escalation['crisis_level']}\n"
                f"Crisis Types: {', '.join(escalation['crisis_types'])}\n"
                f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(escalation['timestamp']))}\n\n"
                f"Risk Factors: {', '.join(intervention.crisis_assessment.risk_factors)}\n"
                f"Protective Factors: {', '.join(intervention.crisis_assessment.protective_factors)}\n"
                f"Immediate Risk: {intervention.crisis_assessment.immediate_risk}\n\n"
                f"Please review and respond immediately."
            ),
            "priority": (
                "high"
                if escalation["crisis_level"] in ["high", "critical"]
                else "medium"
            ),
            "metadata": {
                "escalation_id": escalation["escalation_id"],
                "intervention_id": escalation["intervention_id"],
                "crisis_level": escalation["crisis_level"],
                "user_id": escalation["user_id"],
            },
        }

    def _send_email_notification(
        self, content: dict[str, Any], escalation: dict[str, Any]
    ) -> dict[str, Any]:
        """Send email notification (placeholder implementation)."""
        # In a real implementation, this would send actual emails
        self.logger.info(f"EMAIL NOTIFICATION: {content['subject']}")
        return {
            "message_id": f"email_{escalation['escalation_id']}",
            "recipients": self.config.get("notification_channels", {})
            .get("email", {})
            .get("recipients", []),
            "delivery_status": "sent",
        }

    def _send_sms_notification(
        self, content: dict[str, Any], escalation: dict[str, Any]
    ) -> dict[str, Any]:
        """Send SMS notification (placeholder implementation)."""
        # In a real implementation, this would send actual SMS messages
        self.logger.warning(
            f"SMS NOTIFICATION: Crisis escalation {escalation['escalation_id']}"
        )
        return {
            "message_id": f"sms_{escalation['escalation_id']}",
            "recipients": self.config.get("notification_channels", {})
            .get("sms", {})
            .get("recipients", []),
            "delivery_status": "sent",
        }

    def _send_phone_notification(
        self, content: dict[str, Any], escalation: dict[str, Any]
    ) -> dict[str, Any]:
        """Send phone notification (placeholder implementation)."""
        # In a real implementation, this would make actual phone calls
        self.logger.critical(
            f"PHONE NOTIFICATION: Crisis escalation {escalation['escalation_id']}"
        )
        return {
            "message_id": f"phone_{escalation['escalation_id']}",
            "recipients": self.config.get("notification_channels", {})
            .get("phone", {})
            .get("recipients", []),
            "delivery_status": "attempted",
        }

    def _send_dashboard_notification(
        self, content: dict[str, Any], escalation: dict[str, Any]
    ) -> dict[str, Any]:
        """Send dashboard notification (placeholder implementation)."""
        # In a real implementation, this would update a monitoring dashboard
        self.logger.info(
            f"DASHBOARD NOTIFICATION: Crisis escalation {escalation['escalation_id']}"
        )
        return {
            "message_id": f"dashboard_{escalation['escalation_id']}",
            "dashboard_url": self.config.get("notification_channels", {})
            .get("dashboard", {})
            .get("url", ""),
            "delivery_status": "posted",
        }

    def _send_pager_notification(
        self, content: dict[str, Any], escalation: dict[str, Any]
    ) -> dict[str, Any]:
        """Send pager notification (placeholder implementation)."""
        # In a real implementation, this would send to pager systems
        self.logger.critical(
            f"PAGER NOTIFICATION: Crisis escalation {escalation['escalation_id']}"
        )
        return {
            "message_id": f"pager_{escalation['escalation_id']}",
            "recipients": self.config.get("notification_channels", {})
            .get("pager", {})
            .get("recipients", []),
            "delivery_status": "sent",
        }

    def _contact_emergency_services(
        self, escalation: dict[str, Any], intervention: CrisisIntervention
    ) -> None:
        """Contact emergency services for critical situations."""
        emergency_type = escalation.get("emergency_type", "mental_health")

        # Determine appropriate emergency service
        if emergency_type == "mental_health":
            service_number = "988"  # National Suicide Prevention Lifeline
            service_name = "National Suicide Prevention Lifeline"
        elif emergency_type == "medical":
            service_number = "911"
            service_name = "Emergency Medical Services"
        else:
            service_number = "911"
            service_name = "Emergency Services"

        # In a real implementation, this would contact actual emergency services
        emergency_contact = {
            "service": service_name,
            "number": service_number,
            "timestamp": time.time(),
            "reason": f"Crisis intervention escalation - {escalation['crisis_level']}",
            "user_info": {
                "user_id": escalation["user_id"],
                "session_id": escalation["session_id"],
                "location": escalation.get("location_info", "unknown"),
            },
            "crisis_details": {
                "types": escalation["crisis_types"],
                "level": escalation["crisis_level"],
                "immediate_risk": intervention.crisis_assessment.immediate_risk,
            },
        }

        escalation["emergency_contacts"].append(emergency_contact)

        self.logger.critical(
            f"EMERGENCY SERVICES CONTACTED: {service_name} ({service_number}) "
            f"for escalation {escalation['escalation_id']}"
        )

    def acknowledge_escalation(
        self, escalation_id: str, human_id: str, response_notes: str = ""
    ) -> bool:
        """Acknowledge an escalation by a human oversight person."""
        if escalation_id not in self.active_escalations:
            return False

        escalation = self.active_escalations[escalation_id]
        escalation["status"] = "acknowledged"
        escalation["assigned_human"] = human_id
        escalation["response_received"] = True
        escalation["response_time"] = time.time()
        escalation["response_notes"] = response_notes

        self.logger.info(
            f"Escalation {escalation_id} acknowledged by {human_id}: {response_notes}"
        )

        return True

    def resolve_escalation(
        self, escalation_id: str, resolution_notes: str = ""
    ) -> bool:
        """Mark an escalation as resolved."""
        if escalation_id not in self.active_escalations:
            return False

        escalation = self.active_escalations[escalation_id]
        escalation["status"] = "resolved"
        escalation["resolution_time"] = time.time()
        escalation["resolution_notes"] = resolution_notes

        # Move to history
        self.escalation_history.append(escalation.copy())
        del self.active_escalations[escalation_id]

        self.logger.info(f"Escalation {escalation_id} resolved: {resolution_notes}")

        return True

    def get_escalation_status(self, escalation_id: str) -> dict[str, Any] | None:
        """Get the status of a specific escalation."""
        return self.active_escalations.get(escalation_id)

    def get_escalation_metrics(self) -> dict[str, Any]:
        """Get comprehensive escalation metrics."""
        total_notifications = self.successful_notifications + self.failed_notifications
        notification_success_rate = (
            self.successful_notifications / max(1, total_notifications)
        ) * 100

        # Response time analysis
        response_times = []
        for escalation in self.escalation_history:
            if escalation.get("response_time") and escalation.get("timestamp"):
                response_time = escalation["response_time"] - escalation["timestamp"]
                response_times.append(response_time)

        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0.0
        )

        # Escalation type distribution
        escalation_types = {}
        for escalation in (
            list(self.active_escalations.values()) + self.escalation_history
        ):
            esc_type = escalation.get("escalation_type", "unknown")
            escalation_types[esc_type] = escalation_types.get(esc_type, 0) + 1

        return {
            "total_escalations": self.total_escalations,
            "active_escalations": len(self.active_escalations),
            "resolved_escalations": len(self.escalation_history),
            "emergency_escalations": self.emergency_escalations,
            "successful_notifications": self.successful_notifications,
            "failed_notifications": self.failed_notifications,
            "notification_success_rate_percent": notification_success_rate,
            "average_response_time_seconds": avg_response_time,
            "escalation_type_distribution": escalation_types,
        }

    def _default_escalation_config(self) -> dict[str, Any]:
        """Default configuration for human oversight escalation."""
        return {
            "notification_channels": {
                "email": {
                    "enabled": True,
                    "recipients": ["crisis-team@example.com", "supervisor@example.com"],
                    "smtp_server": "smtp.example.com",
                    "smtp_port": 587,
                },
                "sms": {
                    "enabled": True,
                    "recipients": ["+1234567890", "+0987654321"],
                    "service_provider": "twilio",
                },
                "phone": {
                    "enabled": False,
                    "recipients": ["+1234567890"],
                    "service_provider": "twilio",
                },
                "dashboard": {
                    "enabled": True,
                    "url": "https://dashboard.example.com/crisis",
                    "api_key": "dashboard_api_key",
                },
                "pager": {
                    "enabled": False,
                    "recipients": ["pager123", "pager456"],
                    "service_provider": "pagerduty",
                },
            },
            "escalation_rules": {
                "critical": {
                    "immediate_notification": True,
                    "required_channels": ["sms", "phone", "email"],
                    "response_timeout_minutes": 5,
                },
                "high": {
                    "immediate_notification": True,
                    "required_channels": ["sms", "email"],
                    "response_timeout_minutes": 15,
                },
                "moderate": {
                    "immediate_notification": False,
                    "required_channels": ["email", "dashboard"],
                    "response_timeout_minutes": 60,
                },
            },
            "emergency_services": {
                "mental_health_crisis": "988",
                "medical_emergency": "911",
                "general_emergency": "911",
            },
            "retry_policy": {
                "max_retries": 3,
                "retry_delay_minutes": 2,
                "escalate_on_failure": True,
            },
        }
