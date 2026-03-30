"""Emergency protocol execution engine."""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Crisis_detection/Protocols]]

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from .enums import CrisisLevel, CrisisType


class EmergencyProtocolEngine:
    """Automated response system for different crisis types with configurable protocols.

    Manages emergency protocols, automated responses, and escalation procedures
    for different crisis situations with comprehensive logging and monitoring.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the Emergency Protocol Engine."""
        self.config = config or self._default_protocol_config()
        self.active_protocols: dict[str, dict[str, Any]] = {}
        self.protocol_history: list[dict[str, Any]] = []

        # Statistics tracking
        self.protocols_executed = 0
        self.successful_protocols = 0
        self.failed_protocols = 0

        # Initialize logging
        self.logger = logging.getLogger(__name__ + ".EmergencyProtocolEngine")

    def execute_protocol(
        self,
        crisis_type: CrisisType,
        crisis_level: CrisisLevel,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute the appropriate emergency protocol for the given crisis type and level."""
        protocol_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        protocol_execution = {
            "protocol_id": protocol_id,
            "crisis_type": crisis_type.value,
            "crisis_level": crisis_level.value,
            "start_time": time.time(),
            "context": context,
            "steps_executed": [],
            "success": False,
            "error": None,
            "response_time_ms": 0.0,
        }

        self.active_protocols[protocol_id] = protocol_execution
        self.protocols_executed += 1

        try:
            # Get protocol steps for this crisis type and level
            protocol_steps = self._get_protocol_steps(crisis_type, crisis_level)

            # Execute each step in sequence
            for step in protocol_steps:
                step_result = self._execute_protocol_step(step, context)
                protocol_execution["steps_executed"].append(step_result)

                # If a critical step fails, abort protocol
                if step.get("critical", False) and not step_result["success"]:
                    raise Exception(f"Critical protocol step failed: {step_result['error']}")

            protocol_execution["success"] = True
            self.successful_protocols += 1

            self.logger.info(
                f"Emergency protocol {protocol_id} executed successfully for {crisis_type.value}"
            )

        except Exception as e:
            protocol_execution["error"] = str(e)
            protocol_execution["success"] = False
            self.failed_protocols += 1

            self.logger.error(f"Emergency protocol {protocol_id} failed: {e}")

        finally:
            # Calculate response time
            protocol_execution["response_time_ms"] = (time.perf_counter() - start_time) * 1000

            # Move to history
            self.protocol_history.append(protocol_execution.copy())
            del self.active_protocols[protocol_id]

        return protocol_execution

    def _get_protocol_steps(
        self, crisis_type: CrisisType, crisis_level: CrisisLevel
    ) -> list[dict[str, Any]]:
        """Get the protocol steps for a specific crisis type and level."""
        protocols = self.config.get("protocols", {})

        # Get crisis-specific protocol
        crisis_protocol = protocols.get(crisis_type.value, {})

        # Get level-specific steps
        level_steps = crisis_protocol.get(crisis_level.value, [])

        # If no specific steps, use default
        if not level_steps:
            level_steps = crisis_protocol.get("default", [])

        # If still no steps, use global default
        if not level_steps:
            level_steps = protocols.get("default", [])

        return level_steps

    def _execute_protocol_step(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a single protocol step."""
        start_time = time.perf_counter()
        step_result = {
            "step_type": step.get("type", "unknown"),
            "description": step.get("description", ""),
            "success": False,
            "response_time_ms": 0.0,
            "output": None,
            "error": None,
        }

        try:
            step_type = step.get("type")

            if step_type == "generate_response":
                step_result["output"] = self._generate_protocol_response(step, context)
                step_result["success"] = True

            elif step_type == "log_event":
                self._log_protocol_event(step, context)
                step_result["success"] = True

            elif step_type == "notify_human":
                step_result["output"] = self._notify_human_oversight(step, context)
                step_result["success"] = True

            elif step_type == "contact_emergency":
                step_result["output"] = self._contact_emergency_services(step, context)
                step_result["success"] = True

            elif step_type == "provide_resources":
                step_result["output"] = self._provide_crisis_resources(step, context)
                step_result["success"] = True

            elif step_type == "schedule_followup":
                step_result["output"] = self._schedule_followup(step, context)
                step_result["success"] = True

            else:
                raise Exception(f"Unknown protocol step type: {step_type}")

        except Exception as e:
            step_result["error"] = str(e)
            step_result["success"] = False

        finally:
            step_result["response_time_ms"] = (time.perf_counter() - start_time) * 1000

        return step_result

    def _generate_protocol_response(self, step: dict[str, Any], context: dict[str, Any]) -> str:
        """Generate a protocol-specific response message."""
        template = step.get("template", "")

        # Simple template substitution
        return template.format(
            user_id=context.get("user_id", "unknown"),
            session_id=context.get("session_id", "unknown"),
            crisis_type=context.get("crisis_type", "unknown"),
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def _log_protocol_event(self, step: dict[str, Any], context: dict[str, Any]) -> None:
        """Log a protocol event."""
        log_level = step.get("log_level", "info").lower()
        message = step.get("message", "Protocol event")

        # Format message with context
        formatted_message = message.format(**context)

        if log_level == "critical":
            self.logger.critical(formatted_message)
        elif log_level == "error":
            self.logger.error(formatted_message)
        elif log_level == "warning":
            self.logger.warning(formatted_message)
        else:
            self.logger.info(formatted_message)

    def _notify_human_oversight(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Notify human oversight personnel."""
        notification = {
            "type": "human_oversight",
            "priority": step.get("priority", "high"),
            "message": step.get("message", "Human oversight required"),
            "context": context,
            "timestamp": time.time(),
            "channels": step.get("channels", ["email", "dashboard"]),
        }

        # In a real implementation, this would send actual notifications
        self.logger.warning(f"HUMAN OVERSIGHT NOTIFICATION: {notification['message']}")

        return notification

    def _contact_emergency_services(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Contact emergency services."""
        emergency_contact = {
            "type": "emergency_services",
            "service": step.get("service", "911"),
            "reason": step.get("reason", "Mental health crisis"),
            "context": context,
            "timestamp": time.time(),
            "location": context.get("location", "unknown"),
        }

        # In a real implementation, this would contact actual emergency services
        self.logger.critical(f"EMERGENCY SERVICES CONTACT: {emergency_contact['reason']}")

        return emergency_contact

    def _provide_crisis_resources(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Provide crisis resources to the user."""
        resources = step.get("resources", [])

        # Default crisis resources
        if not resources:
            resources = [
                {
                    "name": "National Suicide Prevention Lifeline",
                    "phone": "988",
                    "description": "24/7 crisis support",
                    "website": "https://suicidepreventionlifeline.org",
                },
                {
                    "name": "Crisis Text Line",
                    "text": "HOME to 741741",
                    "description": "24/7 text-based crisis support",
                    "website": "https://crisistextline.org",
                },
            ]

        return resources

    def _schedule_followup(self, step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Schedule follow-up contact."""
        followup = {
            "type": "followup",
            "interval_hours": step.get("interval_hours", 24),
            "method": step.get("method", "system_check"),
            "context": context,
            "scheduled_time": time.time() + (step.get("interval_hours", 24) * 3600),
            "priority": step.get("priority", "high"),
        }

        self.logger.info(f"Follow-up scheduled for {followup['interval_hours']} hours")

        return followup

    def get_protocol_metrics(self) -> dict[str, Any]:
        """Get comprehensive protocol execution metrics."""
        success_rate = (self.successful_protocols / max(1, self.protocols_executed)) * 100

        # Protocol type distribution
        protocol_types = {}
        for protocol in self.protocol_history:
            crisis_type = protocol["crisis_type"]
            protocol_types[crisis_type] = protocol_types.get(crisis_type, 0) + 1

        # Average response times by crisis type
        avg_response_times = {}
        for crisis_type in protocol_types:
            times = [
                p["response_time_ms"]
                for p in self.protocol_history
                if p["crisis_type"] == crisis_type
            ]
            avg_response_times[crisis_type] = sum(times) / len(times) if times else 0.0

        return {
            "protocols_executed": self.protocols_executed,
            "successful_protocols": self.successful_protocols,
            "failed_protocols": self.failed_protocols,
            "success_rate_percent": success_rate,
            "protocol_type_distribution": protocol_types,
            "average_response_times_ms": avg_response_times,
            "active_protocols": len(self.active_protocols),
        }

    def _default_protocol_config(self) -> dict[str, Any]:
        """Default configuration for emergency protocols."""
        return {
            "protocols": {
                "suicidal_ideation": {
                    "critical": [
                        {
                            "type": "log_event",
                            "log_level": "critical",
                            "message": "CRITICAL SUICIDAL IDEATION: User {user_id} in session {session_id}",
                            "critical": True,
                        },
                        {
                            "type": "generate_response",
                            "template": "I'm deeply concerned about what you've shared. Your life has value and there are people who want to help. Please contact emergency services (911) or the National Suicide Prevention Lifeline at 988 immediately.",
                            "critical": True,
                        },
                        {
                            "type": "contact_emergency",
                            "service": "911",
                            "reason": "Suicidal ideation - critical risk",
                            "critical": True,
                        },
                        {
                            "type": "notify_human",
                            "priority": "critical",
                            "message": "CRITICAL: Suicidal ideation detected - emergency services contacted",
                            "channels": ["email", "sms", "dashboard"],
                        },
                        {
                            "type": "provide_resources",
                            "resources": [
                                {
                                    "name": "National Suicide Prevention Lifeline",
                                    "phone": "988",
                                    "description": "24/7 crisis support",
                                }
                            ],
                        },
                    ],
                    "high": [
                        {
                            "type": "log_event",
                            "log_level": "warning",
                            "message": "HIGH RISK SUICIDAL IDEATION: User {user_id} in session {session_id}",
                        },
                        {
                            "type": "generate_response",
                            "template": "I'm very worried about you and want to help you stay safe. Please reach out to the National Suicide Prevention Lifeline at 988 or contact a mental health professional immediately.",
                        },
                        {
                            "type": "notify_human",
                            "priority": "high",
                            "message": "High risk suicidal ideation detected - immediate oversight required",
                            "channels": ["email", "dashboard"],
                        },
                        {"type": "provide_resources"},
                        {
                            "type": "schedule_followup",
                            "interval_hours": 2,
                            "priority": "high",
                        },
                    ],
                    "moderate": [
                        {
                            "type": "log_event",
                            "log_level": "warning",
                            "message": "MODERATE SUICIDAL IDEATION: User {user_id} in session {session_id}",
                        },
                        {
                            "type": "generate_response",
                            "template": "I'm concerned about what you've shared. Having thoughts of suicide can be frightening, but you don't have to face this alone. Please consider reaching out to the National Suicide Prevention Lifeline at 988.",
                        },
                        {
                            "type": "notify_human",
                            "priority": "medium",
                            "message": "Moderate suicidal ideation detected - oversight recommended",
                            "channels": ["dashboard"],
                        },
                        {"type": "provide_resources"},
                        {"type": "schedule_followup", "interval_hours": 6},
                    ],
                },
                "self_harm": {
                    "critical": [
                        {
                            "type": "log_event",
                            "log_level": "critical",
                            "message": "CRITICAL SELF-HARM RISK: User {user_id} in session {session_id}",
                        },
                        {
                            "type": "generate_response",
                            "template": "I'm very concerned about your safety. Self-harm can be dangerous and I want to help you stay safe. Please contact emergency services (911) if you're in immediate danger.",
                        },
                        {
                            "type": "contact_emergency",
                            "service": "911",
                            "reason": "Self-harm - immediate danger",
                        },
                        {
                            "type": "notify_human",
                            "priority": "critical",
                            "message": "CRITICAL: Self-harm risk - emergency services contacted",
                            "channels": ["email", "sms", "dashboard"],
                        },
                    ],
                    "high": [
                        {
                            "type": "log_event",
                            "log_level": "warning",
                            "message": "HIGH RISK SELF-HARM: User {user_id} in session {session_id}",
                        },
                        {
                            "type": "generate_response",
                            "template": "I'm worried about you and want to help you stay safe. Self-harm might feel like a way to cope, but there are healthier alternatives. Please consider reaching out to a mental health professional.",
                        },
                        {
                            "type": "notify_human",
                            "priority": "high",
                            "message": "High risk self-harm detected - immediate oversight required",
                        },
                        {"type": "schedule_followup", "interval_hours": 4},
                    ],
                },
                "severe_depression": {
                    "high": [
                        {
                            "type": "log_event",
                            "log_level": "warning",
                            "message": "SEVERE DEPRESSION: User {user_id} in session {session_id}",
                        },
                        {
                            "type": "generate_response",
                            "template": "I hear that you're going through an incredibly difficult time. Depression can make everything feel hopeless, but professional support can make a real difference.",
                        },
                        {
                            "type": "notify_human",
                            "priority": "medium",
                            "message": "Severe depression detected - professional referral recommended",
                        },
                        {"type": "schedule_followup", "interval_hours": 12},
                    ]
                },
                "default": [
                    {
                        "type": "log_event",
                        "log_level": "info",
                        "message": "Crisis protocol executed for user {user_id}",
                    },
                    {
                        "type": "generate_response",
                        "template": "I'm here to support you. Please let me know how I can help, and consider reaching out to a mental health professional if you need additional support.",
                    },
                ],
            },
            "timeouts": {"step_timeout_ms": 5000, "protocol_timeout_ms": 30000},
            "retry_policy": {"max_retries": 3, "retry_delay_ms": 1000},
        }
