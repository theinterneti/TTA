"""
Conversation Flow Controller with Therapeutic Progression

This module manages the therapeutic progression of conversational character creation,
ensuring appropriate pacing, validation of conversation stages, and therapeutic safety.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from src.components.therapeutic_safety import (
    ContentPayload,
    SafetyValidationOrchestrator,
    ValidationContext,
)

from ..models.conversation_state import (
    ConversationState,
)
from ..services.conversation_scripts import (
    ConversationScriptManager,
    ConversationStage,
)

logger = logging.getLogger(__name__)


class TherapeuticPacing(str, Enum):
    """Therapeutic pacing levels."""

    SLOW = "slow"  # Extra time between stages, gentle progression
    NORMAL = "normal"  # Standard pacing
    ACCELERATED = "accelerated"  # Faster progression for ready users


class ProgressionRule(str, Enum):
    """Rules for therapeutic progression."""

    SAFETY_FIRST = "safety_first"  # Safety concerns override progression
    READINESS_BASED = "readiness_based"  # Progress based on user readiness
    ENGAGEMENT_DRIVEN = "engagement_driven"  # Progress based on engagement level
    TIME_BOUNDED = "time_bounded"  # Respect session time limits
    COMPLETENESS_GATED = "completeness_gated"  # Require minimum data before advancing


class ConversationFlowController:
    """Controls conversation flow with therapeutic progression."""

    def __init__(self, safety_validator: SafetyValidationOrchestrator):
        self.safety_validator = safety_validator
        self.script_manager = ConversationScriptManager()

        # Therapeutic progression rules
        self.progression_rules = self._initialize_progression_rules()
        self.stage_requirements = self._initialize_stage_requirements()
        self.pacing_adjustments = self._initialize_pacing_adjustments()

        logger.info("ConversationFlowController initialized")

    def _initialize_progression_rules(
        self,
    ) -> dict[ConversationStage, list[ProgressionRule]]:
        """Initialize progression rules for each conversation stage."""
        return {
            ConversationStage.WELCOME: [
                ProgressionRule.SAFETY_FIRST,
                ProgressionRule.ENGAGEMENT_DRIVEN,
            ],
            ConversationStage.IDENTITY: [
                ProgressionRule.SAFETY_FIRST,
                ProgressionRule.READINESS_BASED,
                ProgressionRule.COMPLETENESS_GATED,
            ],
            ConversationStage.APPEARANCE: [
                ProgressionRule.SAFETY_FIRST,
                ProgressionRule.ENGAGEMENT_DRIVEN,
            ],
            ConversationStage.BACKGROUND: [
                ProgressionRule.SAFETY_FIRST,
                ProgressionRule.READINESS_BASED,
                ProgressionRule.TIME_BOUNDED,
            ],
            ConversationStage.VALUES: [
                ProgressionRule.SAFETY_FIRST,
                ProgressionRule.READINESS_BASED,
                ProgressionRule.COMPLETENESS_GATED,
            ],
            ConversationStage.THERAPEUTIC_TRANSITION: [
                ProgressionRule.SAFETY_FIRST,
                ProgressionRule.READINESS_BASED,
                ProgressionRule.TIME_BOUNDED,
            ],
            ConversationStage.CONCERNS: [
                ProgressionRule.SAFETY_FIRST,
                ProgressionRule.READINESS_BASED,
                ProgressionRule.COMPLETENESS_GATED,
            ],
            ConversationStage.GOALS: [
                ProgressionRule.SAFETY_FIRST,
                ProgressionRule.READINESS_BASED,
            ],
            ConversationStage.PREFERENCES: [
                ProgressionRule.SAFETY_FIRST,
                ProgressionRule.COMPLETENESS_GATED,
            ],
            ConversationStage.READINESS: [
                ProgressionRule.SAFETY_FIRST,
                ProgressionRule.COMPLETENESS_GATED,
            ],
        }

    def _initialize_stage_requirements(self) -> dict[ConversationStage, dict[str, Any]]:
        """Initialize requirements for each conversation stage."""
        return {
            ConversationStage.WELCOME: {
                "min_exchanges": 1,
                "required_data": ["name"],
                "safety_check": True,
                "engagement_threshold": 0.3,
            },
            ConversationStage.IDENTITY: {
                "min_exchanges": 2,
                "required_data": ["age_range", "gender_identity"],
                "safety_check": True,
                "engagement_threshold": 0.4,
            },
            ConversationStage.APPEARANCE: {
                "min_exchanges": 1,
                "required_data": ["physical_description"],
                "safety_check": True,
                "engagement_threshold": 0.3,
            },
            ConversationStage.BACKGROUND: {
                "min_exchanges": 2,
                "required_data": ["backstory", "personality_traits"],
                "safety_check": True,
                "engagement_threshold": 0.5,
                "max_duration_minutes": 15,
            },
            ConversationStage.VALUES: {
                "min_exchanges": 2,
                "required_data": ["core_values", "strengths_and_skills"],
                "safety_check": True,
                "engagement_threshold": 0.5,
            },
            ConversationStage.THERAPEUTIC_TRANSITION: {
                "min_exchanges": 1,
                "required_data": [],
                "safety_check": True,
                "engagement_threshold": 0.6,
                "crisis_monitoring": True,
            },
            ConversationStage.CONCERNS: {
                "min_exchanges": 1,
                "required_data": ["primary_concerns"],
                "safety_check": True,
                "engagement_threshold": 0.6,
                "crisis_monitoring": True,
            },
            ConversationStage.GOALS: {
                "min_exchanges": 1,
                "required_data": ["therapeutic_goals"],
                "safety_check": True,
                "engagement_threshold": 0.5,
            },
            ConversationStage.PREFERENCES: {
                "min_exchanges": 2,
                "required_data": ["preferred_intensity", "comfort_zones"],
                "safety_check": True,
                "engagement_threshold": 0.4,
            },
            ConversationStage.READINESS: {
                "min_exchanges": 1,
                "required_data": ["readiness_level"],
                "safety_check": True,
                "engagement_threshold": 0.4,
            },
        }

    def _initialize_pacing_adjustments(
        self,
    ) -> dict[TherapeuticPacing, dict[str, float]]:
        """Initialize pacing adjustments for different therapeutic pacing levels."""
        return {
            TherapeuticPacing.SLOW: {
                "min_exchange_multiplier": 1.5,
                "engagement_threshold_reduction": 0.1,
                "additional_validation_prompts": True,
                "extended_therapeutic_responses": True,
            },
            TherapeuticPacing.NORMAL: {
                "min_exchange_multiplier": 1.0,
                "engagement_threshold_reduction": 0.0,
                "additional_validation_prompts": False,
                "extended_therapeutic_responses": False,
            },
            TherapeuticPacing.ACCELERATED: {
                "min_exchange_multiplier": 0.8,
                "engagement_threshold_reduction": -0.1,
                "additional_validation_prompts": False,
                "extended_therapeutic_responses": False,
            },
        }

    async def validate_stage_progression(
        self, conversation_state: ConversationState, target_stage: ConversationStage
    ) -> tuple[bool, str | None]:
        """Validate if conversation can progress to target stage."""
        current_stage = conversation_state.progress.current_stage

        # Check progression rules
        rules = self.progression_rules.get(current_stage, [])

        for rule in rules:
            is_valid, reason = await self._check_progression_rule(
                rule, conversation_state, target_stage
            )
            if not is_valid:
                return False, reason

        # Check stage requirements
        requirements = self.stage_requirements.get(current_stage, {})
        is_valid, reason = await self._check_stage_requirements(
            requirements, conversation_state
        )
        if not is_valid:
            return False, reason

        return True, None

    async def _check_progression_rule(
        self,
        rule: ProgressionRule,
        conversation_state: ConversationState,
        target_stage: ConversationStage,
    ) -> tuple[bool, str | None]:
        """Check a specific progression rule."""

        if rule == ProgressionRule.SAFETY_FIRST:
            # Check for safety concerns
            if conversation_state.crisis_detected:
                return False, "Safety concerns must be addressed before progression"

            # Check recent messages for safety issues
            recent_messages = conversation_state.message_history[-3:]  # Last 3 messages
            for message in recent_messages:
                if message.sender == "user":
                    safety_result = await self._check_message_safety(
                        message.content, conversation_state
                    )
                    if not safety_result:
                        return False, "Recent safety concerns detected"

        elif rule == ProgressionRule.READINESS_BASED:
            # Check user engagement and readiness indicators
            engagement_score = self._calculate_engagement_score(conversation_state)
            if engagement_score < 0.5:
                return False, "User engagement level insufficient for progression"

        elif rule == ProgressionRule.ENGAGEMENT_DRIVEN:
            # Check if user is actively participating
            recent_responses = [
                msg
                for msg in conversation_state.message_history[-5:]
                if msg.sender == "user"
            ]
            if not recent_responses:
                return False, "No recent user engagement"

            # Check response quality
            avg_response_length = sum(
                len(msg.content.split()) for msg in recent_responses
            ) / len(recent_responses)
            if avg_response_length < 3:  # Very brief responses
                return False, "User responses indicate low engagement"

        elif rule == ProgressionRule.TIME_BOUNDED:
            # Check session duration
            session_duration = datetime.utcnow() - conversation_state.created_at
            if session_duration > timedelta(minutes=45):  # Max 45 minutes per session
                return False, "Session duration limit reached - consider breaking"

        elif rule == ProgressionRule.COMPLETENESS_GATED:
            # Check if required data is collected
            requirements = self.stage_requirements.get(
                conversation_state.progress.current_stage, {}
            )
            required_data = requirements.get("required_data", [])

            missing_data = self._check_missing_data(required_data, conversation_state)
            if missing_data:
                return False, f"Required data missing: {', '.join(missing_data)}"

        return True, None

    async def _check_stage_requirements(
        self, requirements: dict[str, Any], conversation_state: ConversationState
    ) -> tuple[bool, str | None]:
        """Check if stage requirements are met."""

        # Check minimum exchanges
        min_exchanges = requirements.get("min_exchanges", 1)
        stage_messages = [
            msg
            for msg in conversation_state.message_history
            if msg.metadata.get("stage")
            == conversation_state.progress.current_stage.value
        ]
        user_messages = [msg for msg in stage_messages if msg.sender == "user"]

        if len(user_messages) < min_exchanges:
            return False, f"Minimum {min_exchanges} exchanges required for this stage"

        # Check engagement threshold
        engagement_threshold = requirements.get("engagement_threshold", 0.3)
        current_engagement = self._calculate_engagement_score(conversation_state)

        if current_engagement < engagement_threshold:
            return (
                False,
                f"Engagement level ({current_engagement:.2f}) below threshold ({engagement_threshold})",
            )

        # Check required data
        required_data = requirements.get("required_data", [])
        missing_data = self._check_missing_data(required_data, conversation_state)

        if missing_data:
            return False, f"Required data missing: {', '.join(missing_data)}"

        # Check duration limits
        max_duration = requirements.get("max_duration_minutes")
        if max_duration:
            stage_start_time = self._get_stage_start_time(conversation_state)
            if stage_start_time:
                stage_duration = datetime.utcnow() - stage_start_time
                if stage_duration > timedelta(minutes=max_duration):
                    return (
                        False,
                        f"Stage duration limit ({max_duration} minutes) exceeded",
                    )

        return True, None

    def _calculate_engagement_score(
        self, conversation_state: ConversationState
    ) -> float:
        """Calculate user engagement score based on conversation history."""
        if not conversation_state.message_history:
            return 0.0

        user_messages = [
            msg for msg in conversation_state.message_history if msg.sender == "user"
        ]
        if not user_messages:
            return 0.0

        # Factors for engagement calculation
        total_score = 0.0
        factors = 0

        # Response length factor
        avg_response_length = sum(
            len(msg.content.split()) for msg in user_messages
        ) / len(user_messages)
        length_score = min(avg_response_length / 20.0, 1.0)  # Normalize to 0-1
        total_score += length_score
        factors += 1

        # Response frequency factor
        total_duration = (
            datetime.utcnow() - conversation_state.created_at
        ).total_seconds()
        response_frequency = len(user_messages) / max(
            total_duration / 60, 1
        )  # Responses per minute
        frequency_score = min(response_frequency / 2.0, 1.0)  # Normalize to 0-1
        total_score += frequency_score
        factors += 1

        # Emotional engagement factor (presence of emotional words)
        emotional_words = [
            "feel",
            "think",
            "believe",
            "hope",
            "want",
            "need",
            "love",
            "fear",
            "worry",
        ]
        emotional_responses = sum(
            1
            for msg in user_messages
            if any(word in msg.content.lower() for word in emotional_words)
        )
        emotional_score = min(emotional_responses / len(user_messages), 1.0)
        total_score += emotional_score
        factors += 1

        return total_score / factors if factors > 0 else 0.0

    def _check_missing_data(
        self, required_fields: list[str], conversation_state: ConversationState
    ) -> list[str]:
        """Check for missing required data fields."""
        missing = []
        collected_data = conversation_state.collected_data

        for field in required_fields:
            if field == "name" and not collected_data.name:
                missing.append("name")
            elif field == "age_range" and not collected_data.age_range:
                missing.append("age_range")
            elif field == "gender_identity" and not collected_data.gender_identity:
                missing.append("gender_identity")
            elif (
                field == "physical_description"
                and not collected_data.physical_description
            ):
                missing.append("physical_description")
            elif field == "backstory" and not collected_data.backstory:
                missing.append("backstory")
            elif (
                field == "personality_traits" and not collected_data.personality_traits
            ):
                missing.append("personality_traits")
            elif field == "core_values" and not collected_data.core_values:
                missing.append("core_values")
            elif (
                field == "strengths_and_skills"
                and not collected_data.strengths_and_skills
            ):
                missing.append("strengths_and_skills")
            elif field == "primary_concerns" and not collected_data.primary_concerns:
                missing.append("primary_concerns")
            elif field == "therapeutic_goals" and not collected_data.therapeutic_goals:
                missing.append("therapeutic_goals")
            elif (
                field == "preferred_intensity"
                and not collected_data.preferred_intensity
            ):
                missing.append("preferred_intensity")
            elif field == "comfort_zones" and not collected_data.comfort_zones:
                missing.append("comfort_zones")
            elif field == "readiness_level" and collected_data.readiness_level is None:
                missing.append("readiness_level")

        return missing

    async def _check_message_safety(
        self, message: str, conversation_state: ConversationState
    ) -> bool:
        """Check if a message is safe."""
        try:
            validation_context = ValidationContext(
                user_id=conversation_state.player_id,
                session_id=conversation_state.conversation_id,
                content_type="user_response",
            )

            content_payload = ContentPayload(
                content_text=message, content_type="text", source="user_input"
            )

            validation_result = await self.safety_validator.validate_content(
                content_payload, validation_context
            )

            # Consider safe if no high-level crisis detected
            if validation_result.crisis_assessment:
                return validation_result.crisis_assessment.crisis_level.value not in [
                    "high",
                    "emergency",
                ]

            return True

        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            return False  # Err on the side of caution

    def _get_stage_start_time(
        self, conversation_state: ConversationState
    ) -> datetime | None:
        """Get the start time of the current stage."""
        current_stage = conversation_state.progress.current_stage

        # Find first message in current stage
        for message in conversation_state.message_history:
            if message.metadata.get("stage") == current_stage.value:
                return message.timestamp

        return None

    def determine_therapeutic_pacing(
        self, conversation_state: ConversationState
    ) -> TherapeuticPacing:
        """Determine appropriate therapeutic pacing for the conversation."""
        engagement_score = self._calculate_engagement_score(conversation_state)

        # Check for indicators of needing slower pacing
        if conversation_state.crisis_detected:
            return TherapeuticPacing.SLOW

        if engagement_score < 0.3:
            return TherapeuticPacing.SLOW

        # Check for indicators of readiness for faster pacing
        if engagement_score > 0.8:
            user_messages = [
                msg
                for msg in conversation_state.message_history
                if msg.sender == "user"
            ]
            avg_response_length = (
                sum(len(msg.content.split()) for msg in user_messages)
                / len(user_messages)
                if user_messages
                else 0
            )

            if avg_response_length > 15:  # Detailed responses
                return TherapeuticPacing.ACCELERATED

        return TherapeuticPacing.NORMAL

    def get_next_stage_recommendation(
        self, conversation_state: ConversationState
    ) -> ConversationStage | None:
        """Get recommendation for next conversation stage."""
        current_stage = conversation_state.progress.current_stage
        stage_order = self.script_manager.scripts.stage_order

        try:
            current_index = stage_order.index(current_stage)
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
        except ValueError:
            logger.warning(f"Current stage {current_stage} not found in stage order")

        return None
