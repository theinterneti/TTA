"""Crisis intervention management and coordination."""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Crisis_detection/Manager]]

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from ..safety_validation.models import ValidationResult
from .enums import CrisisLevel, CrisisType, EscalationStatus, InterventionType
from .models import CrisisAssessment, CrisisIntervention, InterventionAction


class CrisisInterventionManager:
    """Central coordinator for crisis situations detected by the TherapeuticValidator.

    Manages crisis assessment, intervention protocols, escalation procedures,
    and monitoring of crisis situations with comprehensive logging and reporting.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the Crisis Intervention Manager."""
        self.config = config or self._default_crisis_config()
        self.active_interventions: dict[str, CrisisIntervention] = {}
        self.intervention_history: list[CrisisIntervention] = []

        # Statistics tracking
        self.total_interventions = 0
        self.successful_interventions = 0
        self.escalations_triggered = 0
        self.emergency_contacts = 0

        # Load crisis response templates
        self.response_templates = self._load_response_templates()

        # Initialize logging
        self.logger = logging.getLogger(__name__ + ".CrisisInterventionManager")

    def assess_crisis(
        self, validation_result: ValidationResult, session_context: dict[str, Any]
    ) -> CrisisAssessment:
        """Assess the severity and type of crisis from validation results."""
        if not validation_result.crisis_detected:
            return CrisisAssessment(
                crisis_level=CrisisLevel.LOW,
                crisis_types=[],
                confidence=0.0,
                risk_factors=[],
                protective_factors=[],
                immediate_risk=False,
                intervention_recommended=InterventionType.AUTOMATED_RESPONSE,
                escalation_required=False,
                assessment_timestamp=time.time(),
                context=session_context,
            )

        # Determine crisis level based on multiple factors
        crisis_level = self._determine_crisis_level(validation_result, session_context)

        # Identify risk and protective factors
        risk_factors = self._identify_risk_factors(validation_result, session_context)
        protective_factors = self._identify_protective_factors(session_context)

        # Determine intervention type
        intervention_type = self._determine_intervention_type(crisis_level, validation_result)

        # Check for immediate risk
        immediate_risk = self._assess_immediate_risk(validation_result, crisis_level)

        # Calculate overall confidence
        confidence = self._calculate_crisis_confidence(validation_result, session_context)

        # Convert crisis_types from strings to CrisisType enums
        crisis_types_enums = []
        for ct_str in validation_result.crisis_types:
            try:
                crisis_types_enums.append(CrisisType(ct_str))
            except ValueError:
                # Skip invalid crisis types
                pass

        return CrisisAssessment(
            crisis_level=crisis_level,
            crisis_types=crisis_types_enums,
            confidence=confidence,
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            immediate_risk=immediate_risk,
            intervention_recommended=intervention_type,
            escalation_required=validation_result.escalation_recommended or immediate_risk,
            assessment_timestamp=time.time(),
            context=session_context,
        )

    def initiate_intervention(
        self, assessment: CrisisAssessment, session_id: str, user_id: str
    ) -> CrisisIntervention:
        """Initiate a crisis intervention based on the assessment."""
        intervention_id = str(uuid.uuid4())

        intervention = CrisisIntervention(
            intervention_id=intervention_id,
            session_id=session_id,
            user_id=user_id,
            crisis_assessment=assessment,
            created_timestamp=time.time(),
        )

        # Store active intervention
        self.active_interventions[intervention_id] = intervention
        self.total_interventions += 1

        # Log crisis intervention initiation
        self.logger.warning(
            f"Crisis intervention initiated: {intervention_id} for user {user_id} "
            f"(level: {assessment.crisis_level.value}, types: {[ct.value for ct in assessment.crisis_types]})"
        )

        # Execute immediate response
        self._execute_immediate_response(intervention)

        # Handle escalation if required
        if assessment.escalation_required:
            self._handle_escalation(intervention)

        # Generate alert for monitoring (if we have access to dashboard)
        try:
            # This would be injected in a real implementation
            # For now, we'll add a simple alert mechanism
            alert_severity = (
                "critical" if assessment.crisis_level == CrisisLevel.CRITICAL else "high"
            )
            self.logger.warning(
                f"CRISIS ALERT: {alert_severity.upper()} intervention {intervention_id} "
                f"for crisis types {[ct.value for ct in assessment.crisis_types]}"
            )
        except Exception as e:
            self.logger.error(f"Failed to generate crisis alert: {e}")

        return intervention

    def _determine_crisis_level(
        self, validation_result: ValidationResult, context: dict[str, Any]
    ) -> CrisisLevel:
        """Determine the crisis level based on validation results and context."""
        # High-risk crisis types
        high_risk_types = {CrisisType.SUICIDAL_IDEATION, CrisisType.SELF_HARM}

        # Check for critical indicators - more specific criteria
        if any(ct in high_risk_types for ct in validation_result.crisis_types):
            # Critical: Very low safety score AND escalation recommended
            if validation_result.score < 0.15 and validation_result.escalation_recommended:
                return CrisisLevel.CRITICAL
            # High: Low safety score OR escalation recommended
            if validation_result.score < 0.25 or validation_result.escalation_recommended:
                return CrisisLevel.HIGH
            # Moderate: Crisis detected but not severe
            return CrisisLevel.MODERATE

        # Severe depression with high confidence
        if CrisisType.SEVERE_DEPRESSION in validation_result.crisis_types:
            if validation_result.score < 0.2 and validation_result.escalation_recommended:
                return CrisisLevel.HIGH
            return CrisisLevel.MODERATE

        # Other crisis types - default to moderate
        if validation_result.crisis_detected:
            # Check overall sentiment and therapeutic appropriateness for level
            if (
                validation_result.overall_sentiment
                and validation_result.overall_sentiment < -0.8
                and validation_result.therapeutic_appropriateness < 0.2
            ):
                return CrisisLevel.HIGH
            return CrisisLevel.MODERATE

        return CrisisLevel.LOW

    def _identify_risk_factors(
        self, validation_result: ValidationResult, context: dict[str, Any]
    ) -> list[str]:
        """Identify risk factors from validation results and context."""
        risk_factors = []

        # Crisis-specific risk factors
        if CrisisType.SUICIDAL_IDEATION in validation_result.crisis_types:
            risk_factors.extend(["suicidal_ideation", "death_wish", "hopelessness"])

        if CrisisType.SELF_HARM in validation_result.crisis_types:
            risk_factors.extend(["self_harm_behavior", "self_punishment", "coping_mechanism"])

        if CrisisType.SEVERE_DEPRESSION in validation_result.crisis_types:
            risk_factors.extend(["severe_depression", "worthlessness", "emotional_numbness"])

        # Sentiment-based risk factors
        if validation_result.overall_sentiment and validation_result.overall_sentiment < -0.7:
            risk_factors.append("severe_negative_sentiment")

        # Context-based risk factors
        if context.get("previous_violations", 0) > 2:
            risk_factors.append("repeated_safety_violations")

        if context.get("session_count", 0) < 3:
            risk_factors.append("new_user_vulnerability")

        return list(set(risk_factors))  # Remove duplicates

    def _identify_protective_factors(self, context: dict[str, Any]) -> list[str]:
        """Identify protective factors from context."""
        protective_factors = []

        # Session engagement
        if context.get("session_count", 0) > 5:
            protective_factors.append("ongoing_engagement")

        # Previous positive interactions
        if context.get("positive_interactions", 0) > 0:
            protective_factors.append("positive_therapeutic_history")

        # Support system indicators
        if context.get("has_support_system", False):
            protective_factors.append("social_support")

        # Professional help
        if context.get("has_therapist", False):
            protective_factors.append("professional_support")

        return protective_factors

    def _determine_intervention_type(
        self, crisis_level: CrisisLevel, validation_result: ValidationResult
    ) -> InterventionType:
        """Determine the appropriate intervention type."""
        if crisis_level == CrisisLevel.CRITICAL:
            return InterventionType.EMERGENCY_SERVICES
        if crisis_level == CrisisLevel.HIGH:
            return InterventionType.HUMAN_OVERSIGHT
        if crisis_level == CrisisLevel.MODERATE:
            return InterventionType.THERAPEUTIC_REFERRAL
        return InterventionType.AUTOMATED_RESPONSE

    def _assess_immediate_risk(
        self, validation_result: ValidationResult, crisis_level: CrisisLevel
    ) -> bool:
        """Assess if there is immediate risk requiring urgent intervention."""
        # Critical level always indicates immediate risk
        if crisis_level == CrisisLevel.CRITICAL:
            return True

        # High-risk crisis types with low safety scores
        high_risk_types = {CrisisType.SUICIDAL_IDEATION, CrisisType.SELF_HARM}
        if (
            any(ct in high_risk_types for ct in validation_result.crisis_types)
            and validation_result.score < 0.3
        ):
            return True

        # Multiple crisis types present
        return len(validation_result.crisis_types) >= 2

    def _calculate_crisis_confidence(
        self, validation_result: ValidationResult, context: dict[str, Any]
    ) -> float:
        """Calculate overall confidence in crisis assessment."""
        if not validation_result.crisis_detected:
            return 0.0

        # Base confidence from validation findings
        if validation_result.findings:
            base_confidence = sum(f.confidence for f in validation_result.findings) / len(
                validation_result.findings
            )
        else:
            base_confidence = 0.5

        # Adjust based on sentiment
        if validation_result.overall_sentiment and validation_result.overall_sentiment < -0.5:
            base_confidence += 0.1

        # Adjust based on therapeutic appropriateness
        if validation_result.therapeutic_appropriateness < 0.3:
            base_confidence += 0.1

        # Adjust based on context
        if context.get("previous_violations", 0) > 1:
            base_confidence += 0.05

        return min(1.0, max(0.0, base_confidence))

    def _execute_immediate_response(self, intervention: CrisisIntervention) -> None:
        """Execute immediate response actions for the crisis intervention."""
        start_time = time.perf_counter()

        try:
            # Generate appropriate response based on crisis type
            response_message = self._generate_crisis_response(intervention.crisis_assessment)

            # Record the action
            action = InterventionAction(
                action_type=InterventionType.AUTOMATED_RESPONSE,
                description=f"Generated crisis response: {response_message[:100]}...",
                timestamp=time.time(),
                success=True,
                response_time_ms=(time.perf_counter() - start_time) * 1000,
                metadata={"response_message": response_message},
            )

            intervention.actions_taken.append(action)

            self.logger.info(
                f"Immediate response executed for intervention {intervention.intervention_id}"
            )

        except Exception as e:
            # Record failed action
            action = InterventionAction(
                action_type=InterventionType.AUTOMATED_RESPONSE,
                description=f"Failed to generate crisis response: {str(e)}",
                timestamp=time.time(),
                success=False,
                response_time_ms=(time.perf_counter() - start_time) * 1000,
                metadata={"error": str(e)},
            )

            intervention.actions_taken.append(action)

            self.logger.error(
                f"Failed to execute immediate response for intervention {intervention.intervention_id}: {e}"
            )

    def _handle_escalation(self, intervention: CrisisIntervention) -> None:
        """Handle escalation procedures for crisis intervention."""

        intervention.escalation_status = EscalationStatus.PENDING

        crisis_level = intervention.crisis_assessment.crisis_level

        try:
            if crisis_level == CrisisLevel.CRITICAL:
                self._escalate_to_emergency_services(intervention)
            elif crisis_level in [CrisisLevel.HIGH, CrisisLevel.MODERATE]:
                self._escalate_to_human_oversight(intervention)

            intervention.escalation_status = EscalationStatus.COMPLETED
            self.escalations_triggered += 1

        except Exception as e:
            intervention.escalation_status = EscalationStatus.FAILED
            self.logger.error(
                f"Escalation failed for intervention {intervention.intervention_id}: {e}"
            )

    def _escalate_to_emergency_services(self, intervention: CrisisIntervention) -> None:
        """Escalate to emergency services for critical situations."""
        start_time = time.perf_counter()

        # In a real implementation, this would contact emergency services
        # For now, we'll log and record the action

        action = InterventionAction(
            action_type=InterventionType.EMERGENCY_SERVICES,
            description="Emergency services notification triggered",
            timestamp=time.time(),
            success=True,  # Assume success for now
            response_time_ms=(time.perf_counter() - start_time) * 1000,
            metadata={
                "crisis_level": intervention.crisis_assessment.crisis_level.value,
                "crisis_types": [ct.value for ct in intervention.crisis_assessment.crisis_types],
                "user_id": intervention.user_id,
                "session_id": intervention.session_id,
            },
        )

        intervention.actions_taken.append(action)
        intervention.emergency_contacted = True
        self.emergency_contacts += 1

        self.logger.critical(
            f"EMERGENCY SERVICES ESCALATION: Intervention {intervention.intervention_id} "
            f"for user {intervention.user_id} - Crisis level: {intervention.crisis_assessment.crisis_level.value}"
        )

    def _escalate_to_human_oversight(self, intervention: CrisisIntervention) -> None:
        """Escalate to human oversight for high/moderate risk situations."""
        start_time = time.perf_counter()

        # In a real implementation, this would notify human therapists/supervisors
        # For now, we'll log and record the action

        action = InterventionAction(
            action_type=InterventionType.HUMAN_OVERSIGHT,
            description="Human oversight notification sent",
            timestamp=time.time(),
            success=True,  # Assume success for now
            response_time_ms=(time.perf_counter() - start_time) * 1000,
            metadata={
                "crisis_level": intervention.crisis_assessment.crisis_level.value,
                "crisis_types": [ct.value for ct in intervention.crisis_assessment.crisis_types],
                "risk_factors": intervention.crisis_assessment.risk_factors,
                "protective_factors": intervention.crisis_assessment.protective_factors,
            },
        )

        intervention.actions_taken.append(action)
        intervention.human_notified = True

        self.logger.warning(
            f"HUMAN OVERSIGHT ESCALATION: Intervention {intervention.intervention_id} "
            f"for user {intervention.user_id} - Crisis level: {intervention.crisis_assessment.crisis_level.value}"
        )

    def _generate_crisis_response(self, assessment: CrisisAssessment) -> str:
        """Generate appropriate crisis response message."""
        if not assessment.crisis_types:
            return "I'm here to support you. Please let me know how I can help."

        # Get the most severe crisis type
        primary_crisis = assessment.crisis_types[0]

        # Use response templates
        if primary_crisis in self.response_templates:
            template = self.response_templates[primary_crisis]

            # Customize based on crisis level
            if assessment.crisis_level == CrisisLevel.CRITICAL:
                return template["critical"]
            if assessment.crisis_level == CrisisLevel.HIGH:
                return template["high"]
            if assessment.crisis_level == CrisisLevel.MODERATE:
                return template["moderate"]
            return template["low"]

        # Fallback response
        return (
            "I'm concerned about what you've shared and want to help you stay safe. "
            "Please consider reaching out to a mental health professional or crisis helpline. "
            "You can contact the National Suicide Prevention Lifeline at 988 for immediate support."
        )

    def _load_response_templates(self) -> dict[CrisisType, dict[str, str]]:
        """Load crisis response templates for different crisis types and levels."""
        return {
            CrisisType.SUICIDAL_IDEATION: {
                "critical": (
                    "I'm deeply concerned about what you've shared. Your life has value and there are people who want to help. "
                    "Please contact emergency services (911) or the National Suicide Prevention Lifeline at 988 immediately. "
                    "Do not wait - reach out for help right now. You don't have to face this alone."
                ),
                "high": (
                    "I'm very worried about you and want to help you stay safe. Please reach out to the National Suicide Prevention Lifeline at 988 "
                    "or contact a mental health professional immediately. Your life matters and there are people who care about you. "
                    "Would you like me to help you find local crisis resources?"
                ),
                "moderate": (
                    "I'm concerned about what you've shared. Having thoughts of suicide can be frightening, but you don't have to face this alone. "
                    "Please consider reaching out to the National Suicide Prevention Lifeline at 988 or a mental health professional. "
                    "Would you like to talk about what's been making you feel this way?"
                ),
                "low": (
                    "I hear that you're going through a difficult time. If you're having thoughts of suicide, please know that help is available. "
                    "The National Suicide Prevention Lifeline (988) is available 24/7. Would you like to explore some coping strategies together?"
                ),
            },
            CrisisType.SELF_HARM: {
                "critical": (
                    "I'm very concerned about your safety. Self-harm can be dangerous and I want to help you stay safe. "
                    "Please contact emergency services (911) if you're in immediate danger, or reach out to a crisis helpline immediately. "
                    "You deserve care and support, not harm."
                ),
                "high": (
                    "I'm worried about you and want to help you stay safe. Self-harm might feel like a way to cope, but there are healthier alternatives. "
                    "Please consider reaching out to a mental health professional or crisis helpline. "
                    "Would you like to explore some grounding techniques that might help?"
                ),
                "moderate": (
                    "I'm concerned about what you've shared. Self-harm can be a way of coping with difficult feelings, but it's not safe. "
                    "There are healthier ways to manage these feelings. Would you like to talk about what's been troubling you, "
                    "or explore some alternative coping strategies?"
                ),
                "low": (
                    "I hear that you're struggling with difficult feelings. If you're thinking about self-harm, please know that there are "
                    "healthier ways to cope. Would you like to explore some grounding techniques or talk about what's been on your mind?"
                ),
            },
            CrisisType.SEVERE_DEPRESSION: {
                "critical": (
                    "I'm deeply concerned about how you're feeling. Severe depression can make everything feel overwhelming, "
                    "but you don't have to face this alone. Please reach out to a mental health professional or crisis helpline immediately. "
                    "The National Suicide Prevention Lifeline (988) is available 24/7 for support."
                ),
                "high": (
                    "I hear that you're going through an incredibly difficult time. Depression can make everything feel hopeless, "
                    "but professional support can make a real difference. Please consider reaching out to a mental health professional. "
                    "Would you like to talk about what's been weighing on you most heavily?"
                ),
                "moderate": (
                    "I'm sorry you're experiencing such difficult feelings. Depression can make everything feel overwhelming, "
                    "but there is hope and help available. Would you like to talk about what's been troubling you, "
                    "or explore some resources that might provide support?"
                ),
                "low": (
                    "I hear that you're feeling down and struggling. These feelings are valid, and it's okay to reach out for support. "
                    "Would you like to talk about what's been on your mind, or explore some ways to take care of yourself?"
                ),
            },
        }

    def get_intervention_status(self, intervention_id: str) -> CrisisIntervention | None:
        """Get the status of a specific intervention."""
        return self.active_interventions.get(intervention_id)

    def resolve_intervention(self, intervention_id: str, resolution_notes: str = "") -> bool:
        """Mark an intervention as resolved."""
        if intervention_id not in self.active_interventions:
            return False

        intervention = self.active_interventions[intervention_id]
        intervention.resolution_status = "resolved"
        intervention.resolved_timestamp = time.time()

        # Move to history
        self.intervention_history.append(intervention)
        del self.active_interventions[intervention_id]

        self.successful_interventions += 1

        self.logger.info(f"Intervention {intervention_id} resolved: {resolution_notes}")

        return True

    def get_crisis_metrics(self) -> dict[str, Any]:
        """Get comprehensive crisis intervention metrics."""
        active_count = len(self.active_interventions)
        total_count = self.total_interventions
        success_rate = (self.successful_interventions / max(1, total_count)) * 100

        # Crisis level distribution
        crisis_levels = {}
        for intervention in list(self.active_interventions.values()) + self.intervention_history:
            level = intervention.crisis_assessment.crisis_level.value
            crisis_levels[level] = crisis_levels.get(level, 0) + 1

        # Crisis type distribution
        crisis_types = {}
        for intervention in list(self.active_interventions.values()) + self.intervention_history:
            for crisis_type in intervention.crisis_assessment.crisis_types:
                type_name = crisis_type.value
                crisis_types[type_name] = crisis_types.get(type_name, 0) + 1

        return {
            "active_interventions": active_count,
            "total_interventions": total_count,
            "successful_interventions": self.successful_interventions,
            "success_rate_percent": success_rate,
            "escalations_triggered": self.escalations_triggered,
            "emergency_contacts": self.emergency_contacts,
            "crisis_level_distribution": crisis_levels,
            "crisis_type_distribution": crisis_types,
            "average_response_time_ms": self._calculate_average_response_time(),
        }

    def _calculate_average_response_time(self) -> float:
        """Calculate average response time for interventions."""
        all_interventions = list(self.active_interventions.values()) + self.intervention_history

        if not all_interventions:
            return 0.0

        total_time = 0.0
        action_count = 0

        for intervention in all_interventions:
            for action in intervention.actions_taken:
                total_time += action.response_time_ms
                action_count += 1

        return total_time / max(1, action_count)

    def _default_crisis_config(self) -> dict[str, Any]:
        """Default configuration for crisis intervention."""
        return {
            "escalation_thresholds": {"critical": 0.9, "high": 0.7, "moderate": 0.5},
            "response_timeouts": {
                "immediate_response_ms": 1000,
                "escalation_timeout_ms": 5000,
                "emergency_timeout_ms": 2000,
            },
            "monitoring": {
                "track_all_interventions": True,
                "log_escalations": True,
                "alert_on_emergency": True,
            },
            "notifications": {
                "human_oversight_enabled": True,
                "emergency_services_enabled": True,
                "email_notifications": False,
                "webhook_notifications": False,
            },
        }
