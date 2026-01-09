"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Consequence_system/Progress_tracker]]

# Logseq: [[TTA/Components/Gameplay_loop/Consequence_system/Progress_tracker]]
Progress Tracker for Therapeutic Text Adventure

This module implements progress tracking functionality that monitors and
records therapeutic progress through player choices and consequences,
identifying growth patterns and milestone achievements.
"""

from __future__ import annotations

import logging
from typing import Any

from ..models.core import ChoiceType, SessionState
from ..models.interactions import UserChoice
from ..models.progress import ProgressMarker, ProgressType

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    Tracks therapeutic progress through player choices and consequences,
    identifying growth patterns and milestone achievements.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Progress tracking resources
        self.progress_patterns: dict[str, dict[str, Any]] = {}
        self.milestone_definitions: dict[str, dict[str, Any]] = {}
        self.skill_development_tracks: dict[str, list[str]] = {}
        self.growth_indicators: dict[str, list[str]] = {}

        logger.info("ProgressTracker initialized")

    async def initialize(self) -> bool:
        """Initialize progress tracking patterns and definitions."""
        try:
            await self._load_progress_patterns()
            await self._load_milestone_definitions()
            await self._load_skill_tracks()
            await self._load_growth_indicators()

            logger.info("ProgressTracker initialization completed")
            return True

        except Exception as e:
            logger.error(f"ProgressTracker initialization failed: {e}")
            return False

    async def track_progress(
        self,
        user_choice: UserChoice,
        outcomes: dict[str, Any],
        session_state: SessionState,
    ) -> dict[str, Any]:
        """
        Track therapeutic progress from choice and outcomes.

        Args:
            user_choice: The choice made by the user
            outcomes: Generated outcomes from the choice
            session_state: Current session state

        Returns:
            Dictionary with progress tracking information
        """
        try:
            logger.info(f"Tracking progress for choice {user_choice.choice_id}")

            progress_update = {
                "progress_markers": [],
                "skill_development": [],
                "growth_patterns": [],
                "milestone_achievements": [],
                "therapeutic_gains": [],
            }

            # Identify progress markers
            progress_markers = await self._identify_progress_markers(
                user_choice, outcomes, session_state
            )
            progress_update["progress_markers"] = progress_markers

            # Track skill development
            skill_development = await self._track_skill_development(
                user_choice, outcomes
            )
            progress_update["skill_development"] = skill_development

            # Identify growth patterns
            growth_patterns = await self._identify_growth_patterns(
                user_choice, session_state
            )
            progress_update["growth_patterns"] = growth_patterns

            # Check for milestone achievements
            milestones = await self._check_milestone_achievements(
                user_choice, session_state
            )
            progress_update["milestone_achievements"] = milestones

            # Assess therapeutic gains
            therapeutic_gains = await self._assess_therapeutic_gains(
                user_choice, outcomes
            )
            progress_update["therapeutic_gains"] = therapeutic_gains

            logger.info("Progress tracking completed")
            return progress_update

        except Exception as e:
            logger.error(f"Failed to track progress: {e}")
            return {"progress_markers": [], "skill_development": []}

    # Initialization Methods
    async def _load_progress_patterns(self) -> None:
        """Load progress tracking patterns."""
        self.progress_patterns = {
            "therapeutic_engagement": {
                "indicators": [
                    "therapeutic_choice_frequency",
                    "therapeutic_value_trend",
                    "insight_depth",
                ],
                "thresholds": {"low": 0.3, "moderate": 0.6, "high": 0.8},
                "progress_type": ProgressType.THERAPEUTIC_ENGAGEMENT,
            },
            "skill_development": {
                "indicators": [
                    "skill_choice_frequency",
                    "skill_application_success",
                    "skill_variety",
                ],
                "thresholds": {"low": 0.3, "moderate": 0.6, "high": 0.8},
                "progress_type": ProgressType.SKILL_DEVELOPMENT,
            },
            "emotional_regulation": {
                "indicators": [
                    "emotional_stability",
                    "regulation_choice_frequency",
                    "emotional_awareness",
                ],
                "thresholds": {"low": 0.4, "moderate": 0.7, "high": 0.9},
                "progress_type": ProgressType.EMOTIONAL_REGULATION,
            },
            "self_awareness": {
                "indicators": [
                    "insight_frequency",
                    "self_reflection_depth",
                    "awareness_application",
                ],
                "thresholds": {"low": 0.3, "moderate": 0.6, "high": 0.8},
                "progress_type": ProgressType.SELF_AWARENESS,
            },
            "resilience_building": {
                "indicators": [
                    "challenge_engagement",
                    "coping_strategy_use",
                    "recovery_speed",
                ],
                "thresholds": {"low": 0.4, "moderate": 0.7, "high": 0.9},
                "progress_type": ProgressType.RESILIENCE_BUILDING,
            },
        }

    async def _load_milestone_definitions(self) -> None:
        """Load milestone definitions."""
        self.milestone_definitions = {
            "first_therapeutic_choice": {
                "description": "Made first therapeutic choice",
                "criteria": {"therapeutic_choices": 1},
                "significance": "Beginning of therapeutic engagement",
            },
            "consistent_engagement": {
                "description": "Consistent therapeutic engagement",
                "criteria": {"therapeutic_choices": 5, "session_length": 10},
                "significance": "Sustained therapeutic participation",
            },
            "skill_application": {
                "description": "Successfully applied therapeutic skill",
                "criteria": {"skill_building_choices": 3, "therapeutic_value": 0.7},
                "significance": "Practical skill development",
            },
            "emotional_breakthrough": {
                "description": "Significant emotional insight or regulation",
                "criteria": {
                    "emotional_regulation_choices": 2,
                    "therapeutic_value": 0.8,
                },
                "significance": "Emotional growth milestone",
            },
            "self_compassion_practice": {
                "description": "Demonstrated self-compassion",
                "criteria": {"self_compassion_tags": 3},
                "significance": "Self-kindness development",
            },
            "resilience_demonstration": {
                "description": "Showed resilience in challenging situation",
                "criteria": {"challenging_choices": 2, "positive_outcomes": 1},
                "significance": "Resilience building",
            },
        }

    async def _load_skill_tracks(self) -> None:
        """Load skill development tracks."""
        self.skill_development_tracks = {
            "mindfulness": [
                "present_moment_awareness",
                "non_judgmental_observation",
                "mindful_breathing",
                "body_awareness",
                "thought_observation",
            ],
            "emotional_regulation": [
                "emotion_identification",
                "distress_tolerance",
                "emotion_modulation",
                "emotional_expression",
                "emotional_intelligence",
            ],
            "self_compassion": [
                "self_kindness",
                "common_humanity",
                "mindful_self_awareness",
                "self_forgiveness",
                "inner_critic_management",
            ],
            "coping_skills": [
                "problem_solving",
                "stress_management",
                "relaxation_techniques",
                "cognitive_restructuring",
                "behavioral_activation",
            ],
            "interpersonal_skills": [
                "active_listening",
                "empathy_expression",
                "boundary_setting",
                "conflict_resolution",
                "authentic_communication",
            ],
        }

    async def _load_growth_indicators(self) -> None:
        """Load growth indicators."""
        self.growth_indicators = {
            "increasing_therapeutic_value": "Choices show increasing therapeutic benefit",
            "skill_variety_expansion": "Using wider variety of therapeutic skills",
            "emotional_stability_improvement": "Greater emotional stability over time",
            "insight_depth_increase": "Deeper therapeutic insights",
            "challenge_engagement_growth": "More willing to engage with challenges",
            "self_compassion_increase": "Growing self-kindness and acceptance",
            "resilience_demonstration": "Showing greater resilience",
            "mindfulness_integration": "Integrating mindfulness into choices",
        }

    # Core Tracking Methods
    async def _identify_progress_markers(
        self,
        user_choice: UserChoice,
        outcomes: dict[str, Any],
        session_state: SessionState,
    ) -> list[ProgressMarker]:
        """Identify progress markers from choice and outcomes."""
        progress_markers = []

        # High therapeutic value marker
        if user_choice.therapeutic_value > 0.7:
            progress_markers.append(
                ProgressMarker(
                    marker_type=ProgressType.THERAPEUTIC_ENGAGEMENT,
                    description="High therapeutic value choice",
                    significance="Strong therapeutic engagement",
                    timestamp=None,  # Would be set by system
                )
            )

        # Skill building marker
        if user_choice.choice_type == ChoiceType.SKILL_BUILDING:
            progress_markers.append(
                ProgressMarker(
                    marker_type=ProgressType.SKILL_DEVELOPMENT,
                    description="Skill building choice made",
                    significance="Active skill development",
                    timestamp=None,
                )
            )

        # Emotional regulation marker
        if user_choice.choice_type == ChoiceType.EMOTIONAL_REGULATION:
            progress_markers.append(
                ProgressMarker(
                    marker_type=ProgressType.EMOTIONAL_REGULATION,
                    description="Emotional regulation practice",
                    significance="Emotional skill development",
                    timestamp=None,
                )
            )

        # Self-awareness marker
        if any(
            tag in user_choice.therapeutic_tags
            for tag in ["self_awareness", "insight", "reflection"]
        ):
            progress_markers.append(
                ProgressMarker(
                    marker_type=ProgressType.SELF_AWARENESS,
                    description="Self-awareness demonstration",
                    significance="Growing self-understanding",
                    timestamp=None,
                )
            )

        return progress_markers

    async def _track_skill_development(
        self, user_choice: UserChoice, outcomes: dict[str, Any]
    ) -> list[str]:
        """Track skill development from choice."""
        skills_developed = []

        # Map therapeutic tags to skills
        tag_to_skill_mapping = {
            "mindfulness": "mindfulness_practice",
            "grounding": "grounding_techniques",
            "self_compassion": "self_compassion_practice",
            "emotional_regulation": "emotional_regulation_skills",
            "coping_skills": "coping_strategy_application",
            "resilience": "resilience_building",
            "communication": "interpersonal_skills",
        }

        for tag in user_choice.therapeutic_tags:
            if tag in tag_to_skill_mapping:
                skills_developed.append(tag_to_skill_mapping[tag])

        # Add skill based on choice type
        if user_choice.choice_type == ChoiceType.SKILL_BUILDING:
            skills_developed.append("general_skill_building")
        elif user_choice.choice_type == ChoiceType.THERAPEUTIC:
            skills_developed.append("therapeutic_engagement")

        return list(set(skills_developed))  # Remove duplicates

    async def _identify_growth_patterns(
        self, user_choice: UserChoice, session_state: SessionState
    ) -> list[str]:
        """Identify growth patterns from choice history."""
        growth_patterns = []

        # Analyze choice history for patterns
        choice_history = session_state.choice_history

        if len(choice_history) >= 3:
            # Check for increasing therapeutic value
            recent_values = [
                choice.get("therapeutic_value", 0) for choice in choice_history[-3:]
            ]
            if len(recent_values) >= 2 and recent_values[-1] > recent_values[0]:
                growth_patterns.append("increasing_therapeutic_engagement")

        # Check for skill variety
        if len(choice_history) >= 5:
            recent_tags = []
            for choice in choice_history[-5:]:
                recent_tags.extend(choice.get("therapeutic_tags", []))

            unique_tags = set(recent_tags)
            if len(unique_tags) >= 4:
                growth_patterns.append("expanding_skill_variety")

        # Current choice patterns
        if user_choice.therapeutic_value > 0.8:
            growth_patterns.append("high_therapeutic_engagement")

        if (
            user_choice.choice_type == ChoiceType.SKILL_BUILDING
            and user_choice.therapeutic_value > 0.6
        ):
            growth_patterns.append("effective_skill_application")

        return growth_patterns

    async def _check_milestone_achievements(
        self, user_choice: UserChoice, session_state: SessionState
    ) -> list[str]:
        """Check for milestone achievements."""
        milestones = []

        choice_history = session_state.choice_history

        # First therapeutic choice
        therapeutic_choices = sum(
            1 for choice in choice_history if choice.get("choice_type") == "therapeutic"
        )
        if therapeutic_choices == 1:
            milestones.append("first_therapeutic_choice")

        # Consistent engagement
        if len(choice_history) >= 10 and therapeutic_choices >= 5:
            milestones.append("consistent_engagement")

        # High value choice
        if user_choice.therapeutic_value > 0.8:
            milestones.append("high_value_choice")

        return milestones

    async def _assess_therapeutic_gains(
        self, user_choice: UserChoice, outcomes: dict[str, Any]
    ) -> list[str]:
        """Assess therapeutic gains from choice and outcomes."""
        gains = []

        # Based on therapeutic value
        if user_choice.therapeutic_value > 0.8:
            gains.append("significant_therapeutic_benefit")
        elif user_choice.therapeutic_value > 0.6:
            gains.append("moderate_therapeutic_benefit")

        # Based on choice type
        if user_choice.choice_type == ChoiceType.THERAPEUTIC:
            gains.append("therapeutic_skill_practice")
        elif user_choice.choice_type == ChoiceType.SKILL_BUILDING:
            gains.append("skill_development_progress")
        elif user_choice.choice_type == ChoiceType.EMOTIONAL_REGULATION:
            gains.append("emotional_regulation_practice")

        # Based on outcomes
        if outcomes.get("emotional_impact", {}).get("primary_emotion") in [
            "positive",
            "hopeful",
            "empowered",
        ]:
            gains.append("positive_emotional_outcome")

        return gains
