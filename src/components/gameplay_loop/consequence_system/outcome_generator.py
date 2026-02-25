"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Consequence_system/Outcome_generator]]

# Logseq: [[TTA/Components/Gameplay_loop/Consequence_system/Outcome_generator]]
Outcome Generator for Therapeutic Text Adventure

This module implements outcome generation functionality that creates logical,
meaningful outcomes from player choices based on choice analysis, scene context,
and therapeutic goals while maintaining narrative coherence.
"""

from __future__ import annotations

import logging
from typing import Any

from ..models.core import ChoiceType, EmotionalState, Scene, SessionState
from ..models.interactions import UserChoice

logger = logging.getLogger(__name__)


class OutcomeTemplate:
    """Template for generating outcomes based on choice patterns."""

    def __init__(self, choice_type: ChoiceType, outcome_data: dict[str, Any]):
        self.choice_type = choice_type
        self.outcome_data = outcome_data
        self.immediate_patterns = outcome_data.get("immediate_patterns", [])
        self.delayed_patterns = outcome_data.get("delayed_patterns", [])
        self.emotional_impacts = outcome_data.get("emotional_impacts", {})
        self.narrative_consequences = outcome_data.get("narrative_consequences", [])


class OutcomeGenerator:
    """
    Generates logical, meaningful outcomes from player choices based on
    choice analysis, scene context, and therapeutic goals.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Outcome generation resources
        self.outcome_templates: dict[ChoiceType, list[OutcomeTemplate]] = {}
        self.therapeutic_outcome_patterns: dict[str, dict[str, Any]] = {}
        self.narrative_outcome_patterns: dict[str, dict[str, Any]] = {}
        self.emotional_outcome_mappings: dict[EmotionalState, dict[str, Any]] = {}
        self.causality_patterns: dict[str, list[str]] = {}

        logger.info("OutcomeGenerator initialized")

    async def initialize(self) -> bool:
        """Initialize outcome generation templates and patterns."""
        try:
            await self._load_outcome_templates()
            await self._load_therapeutic_patterns()
            await self._load_narrative_patterns()
            await self._load_emotional_mappings()
            await self._load_causality_patterns()

            logger.info("OutcomeGenerator initialization completed")
            return True

        except Exception as e:
            logger.error(f"OutcomeGenerator initialization failed: {e}")
            return False

    async def generate_outcomes(
        self, user_choice: UserChoice, scene: Scene, session_state: SessionState
    ) -> dict[str, Any]:
        """
        Generate comprehensive outcomes for a user's choice.

        Args:
            user_choice: The choice made by the user
            scene: The scene where the choice was made
            session_state: Current session state

        Returns:
            Dictionary with all generated outcomes
        """
        try:
            logger.info(f"Generating outcomes for choice {user_choice.choice_id}")

            outcomes = {
                "immediate": [],
                "delayed": [],
                "emotional_impact": {},
                "narrative": [],
                "character_development": {},
                "world_state_changes": {},
            }

            # Generate immediate outcomes
            immediate_outcomes = await self._generate_immediate_outcomes(
                user_choice, scene, session_state
            )
            outcomes["immediate"] = immediate_outcomes

            # Generate delayed outcomes
            delayed_outcomes = await self._generate_delayed_outcomes(
                user_choice, scene, session_state
            )
            outcomes["delayed"] = delayed_outcomes

            # Generate emotional impact
            emotional_impact = await self._generate_emotional_impact(
                user_choice, scene, session_state
            )
            outcomes["emotional_impact"] = emotional_impact

            # Generate narrative consequences
            narrative_consequences = await self._generate_narrative_consequences(
                user_choice, scene, session_state
            )
            outcomes["narrative"] = narrative_consequences

            # Generate character development
            character_development = await self._generate_character_development(
                user_choice, session_state
            )
            outcomes["character_development"] = character_development

            # Generate world state changes
            world_state_changes = await self._generate_world_state_changes(
                user_choice, scene, session_state
            )
            outcomes["world_state_changes"] = world_state_changes

            logger.info("Generated comprehensive outcomes")
            return outcomes

        except Exception as e:
            logger.error(f"Failed to generate outcomes: {e}")
            return await self._generate_fallback_outcomes(user_choice)

    # Initialization Methods
    async def _load_outcome_templates(self) -> None:
        """Load outcome templates for different choice types."""
        # Therapeutic choice templates
        therapeutic_templates = [
            OutcomeTemplate(
                ChoiceType.THERAPEUTIC,
                {
                    "immediate_patterns": [
                        "You feel a sense of {emotional_response} as you {action}",
                        "The practice of {therapeutic_technique} brings {immediate_benefit}",
                        "You notice {awareness_insight} about yourself",
                    ],
                    "delayed_patterns": [
                        "Over time, this practice strengthens your {skill_area}",
                        "You find yourself naturally applying this {technique} in daily life",
                        "Your capacity for {therapeutic_goal} continues to grow",
                    ],
                    "emotional_impacts": {
                        "primary_emotions": ["calm", "centered", "aware", "hopeful"],
                        "intensity_range": [0.6, 0.9],
                    },
                    "narrative_consequences": [
                        "Your inner wisdom guides your next steps",
                        "You feel more connected to your authentic self",
                        "A sense of inner strength emerges",
                    ],
                },
            )
        ]

        # Narrative choice templates
        narrative_templates = [
            OutcomeTemplate(
                ChoiceType.NARRATIVE,
                {
                    "immediate_patterns": [
                        "Your choice leads you to {new_location}",
                        "You discover {interesting_element} that {significance}",
                        "The path ahead {path_description}",
                    ],
                    "delayed_patterns": [
                        "This decision opens new possibilities for {future_opportunity}",
                        "You remember this moment when facing {future_challenge}",
                        "The consequences of this choice ripple through {time_frame}",
                    ],
                    "emotional_impacts": {
                        "primary_emotions": ["curious", "engaged", "adventurous"],
                        "intensity_range": [0.4, 0.8],
                    },
                    "narrative_consequences": [
                        "The story takes an unexpected turn",
                        "New characters enter your journey",
                        "Hidden aspects of the world are revealed",
                    ],
                },
            )
        ]

        # Skill building choice templates
        skill_building_templates = [
            OutcomeTemplate(
                ChoiceType.SKILL_BUILDING,
                {
                    "immediate_patterns": [
                        "You successfully apply {skill_name} to {situation}",
                        "The practice feels {difficulty_level} but {encouraging_aspect}",
                        "You notice improvement in your {skill_area}",
                    ],
                    "delayed_patterns": [
                        "Your {skill_name} becomes more natural with practice",
                        "You find new ways to use {skill_name} in different situations",
                        "Others begin to notice your growth in {skill_area}",
                    ],
                    "emotional_impacts": {
                        "primary_emotions": ["accomplished", "confident", "capable"],
                        "intensity_range": [0.5, 0.8],
                    },
                    "narrative_consequences": [
                        "Your growing skills open new paths",
                        "Challenges that once seemed impossible become manageable",
                        "You become a source of strength for others",
                    ],
                },
            )
        ]

        # Emotional regulation choice templates
        emotional_regulation_templates = [
            OutcomeTemplate(
                ChoiceType.EMOTIONAL_REGULATION,
                {
                    "immediate_patterns": [
                        "You feel your emotions {regulation_action} as you {technique}",
                        "The intensity of {emotion} {change_direction} to a manageable level",
                        "You experience {positive_emotion} as you work with your feelings",
                    ],
                    "delayed_patterns": [
                        "Your emotional resilience continues to strengthen",
                        "You develop greater trust in your ability to handle difficult emotions",
                        "Emotional balance becomes more natural and sustainable",
                    ],
                    "emotional_impacts": {
                        "primary_emotions": ["balanced", "regulated", "stable"],
                        "intensity_range": [0.6, 0.9],
                    },
                    "narrative_consequences": [
                        "Your emotional wisdom guides your relationships",
                        "You become a calming presence for others",
                        "Inner peace radiates outward into your world",
                    ],
                },
            )
        ]

        # Social interaction choice templates
        social_interaction_templates = [
            OutcomeTemplate(
                ChoiceType.SOCIAL_INTERACTION,
                {
                    "immediate_patterns": [
                        "Your {interaction_style} creates {social_outcome}",
                        "The other person responds with {response_type}",
                        "You feel {social_emotion} about the connection",
                    ],
                    "delayed_patterns": [
                        "This interaction strengthens your {relationship_aspect}",
                        "You carry forward the {positive_element} from this exchange",
                        "Your social confidence grows through {interaction_learning}",
                    ],
                    "emotional_impacts": {
                        "primary_emotions": ["connected", "understood", "valued"],
                        "intensity_range": [0.4, 0.8],
                    },
                    "narrative_consequences": [
                        "New relationships begin to form",
                        "Existing bonds deepen and strengthen",
                        "Your social world expands with meaningful connections",
                    ],
                },
            )
        ]

        self.outcome_templates = {
            ChoiceType.THERAPEUTIC: therapeutic_templates,
            ChoiceType.NARRATIVE: narrative_templates,
            ChoiceType.SKILL_BUILDING: skill_building_templates,
            ChoiceType.EMOTIONAL_REGULATION: emotional_regulation_templates,
            ChoiceType.SOCIAL_INTERACTION: social_interaction_templates,
        }

    async def _load_therapeutic_patterns(self) -> None:
        """Load therapeutic outcome patterns."""
        self.therapeutic_outcome_patterns = {
            "mindfulness": {
                "immediate_benefits": [
                    "present_moment_awareness",
                    "reduced_anxiety",
                    "mental_clarity",
                ],
                "long_term_benefits": [
                    "emotional_regulation",
                    "stress_resilience",
                    "self_awareness",
                ],
                "skill_development": [
                    "attention_training",
                    "non_judgmental_awareness",
                    "acceptance",
                ],
            },
            "grounding": {
                "immediate_benefits": [
                    "physical_stability",
                    "reduced_overwhelm",
                    "safety_feeling",
                ],
                "long_term_benefits": [
                    "emotional_stability",
                    "crisis_management",
                    "self_soothing",
                ],
                "skill_development": [
                    "sensory_awareness",
                    "body_connection",
                    "safety_creation",
                ],
            },
            "self_compassion": {
                "immediate_benefits": [
                    "self_kindness",
                    "reduced_self_criticism",
                    "emotional_warmth",
                ],
                "long_term_benefits": ["self_acceptance", "resilience", "inner_peace"],
                "skill_development": [
                    "self_kindness_practice",
                    "common_humanity",
                    "mindful_self_awareness",
                ],
            },
            "emotional_regulation": {
                "immediate_benefits": [
                    "emotional_balance",
                    "reduced_intensity",
                    "clarity",
                ],
                "long_term_benefits": [
                    "emotional_intelligence",
                    "relationship_skills",
                    "life_satisfaction",
                ],
                "skill_development": [
                    "emotion_identification",
                    "regulation_strategies",
                    "distress_tolerance",
                ],
            },
        }

    async def _load_narrative_patterns(self) -> None:
        """Load narrative outcome patterns."""
        self.narrative_outcome_patterns = {
            "exploration": {
                "discovery_types": [
                    "hidden_location",
                    "secret_knowledge",
                    "new_character",
                    "ancient_wisdom",
                ],
                "progression_types": [
                    "path_opening",
                    "barrier_removal",
                    "skill_unlock",
                    "relationship_deepening",
                ],
                "world_changes": [
                    "environment_shift",
                    "character_reaction",
                    "story_revelation",
                    "mystery_deepening",
                ],
            },
            "character_interaction": {
                "relationship_outcomes": [
                    "trust_building",
                    "conflict_resolution",
                    "mutual_understanding",
                    "shared_experience",
                ],
                "character_development": [
                    "personality_reveal",
                    "backstory_sharing",
                    "growth_moment",
                    "vulnerability_expression",
                ],
                "social_dynamics": [
                    "group_harmony",
                    "leadership_emergence",
                    "support_network",
                    "community_building",
                ],
            },
            "challenge_facing": {
                "success_outcomes": [
                    "obstacle_overcome",
                    "skill_demonstration",
                    "confidence_boost",
                    "recognition_gained",
                ],
                "learning_outcomes": [
                    "lesson_learned",
                    "wisdom_gained",
                    "perspective_shift",
                    "growth_achieved",
                ],
                "resilience_outcomes": [
                    "strength_discovered",
                    "courage_found",
                    "perseverance_rewarded",
                    "character_forged",
                ],
            },
        }

    async def _load_emotional_mappings(self) -> None:
        """Load emotional outcome mappings."""
        self.emotional_outcome_mappings = {
            EmotionalState.CALM: {
                "positive_outcomes": [
                    "deeper_peace",
                    "expanded_awareness",
                    "gentle_growth",
                ],
                "intensity_modifiers": [0.3, 0.7],
                "progression_emotions": ["content", "serene", "balanced"],
            },
            EmotionalState.ENGAGED: {
                "positive_outcomes": [
                    "increased_enthusiasm",
                    "deeper_involvement",
                    "active_participation",
                ],
                "intensity_modifiers": [0.6, 0.9],
                "progression_emotions": ["excited", "motivated", "energized"],
            },
            EmotionalState.ANXIOUS: {
                "positive_outcomes": [
                    "reduced_anxiety",
                    "increased_calm",
                    "greater_security",
                ],
                "intensity_modifiers": [0.4, 0.8],
                "progression_emotions": ["relieved", "calmer", "more_secure"],
            },
            EmotionalState.OVERWHELMED: {
                "positive_outcomes": [
                    "reduced_overwhelm",
                    "increased_clarity",
                    "manageable_steps",
                ],
                "intensity_modifiers": [0.5, 0.8],
                "progression_emotions": ["clearer", "more_manageable", "supported"],
            },
            EmotionalState.DISTRESSED: {
                "positive_outcomes": [
                    "comfort_found",
                    "support_received",
                    "hope_restored",
                ],
                "intensity_modifiers": [0.6, 0.9],
                "progression_emotions": ["comforted", "supported", "hopeful"],
            },
            EmotionalState.CRISIS: {
                "positive_outcomes": [
                    "safety_established",
                    "immediate_support",
                    "crisis_stabilization",
                ],
                "intensity_modifiers": [0.7, 1.0],
                "progression_emotions": ["safer", "supported", "stabilized"],
            },
        }

    async def _load_causality_patterns(self) -> None:
        """Load causality patterns for outcome explanation."""
        self.causality_patterns = {
            "therapeutic_choice": [
                "Your commitment to self-care creates positive change",
                "Practicing therapeutic techniques builds inner strength",
                "Choosing growth over comfort leads to transformation",
            ],
            "narrative_choice": [
                "Your curiosity opens new paths of discovery",
                "Taking action moves the story forward",
                "Your choices shape the world around you",
            ],
            "skill_building_choice": [
                "Practice and effort lead to skill development",
                "Challenging yourself creates growth opportunities",
                "Consistent application builds competence",
            ],
            "emotional_regulation_choice": [
                "Working with emotions creates emotional intelligence",
                "Accepting feelings leads to emotional freedom",
                "Regulating emotions improves life satisfaction",
            ],
            "social_interaction_choice": [
                "Authentic connection creates meaningful relationships",
                "Vulnerability and openness build trust",
                "Social engagement enriches life experience",
            ],
        }

    # Outcome Generation Methods
    async def _generate_immediate_outcomes(  # noqa: ARG002
        self, user_choice: UserChoice, scene: Scene, session_state: SessionState
    ) -> list[str]:
        """Generate immediate outcomes from choice."""
        patterns = self.outcome_templates.get(user_choice.choice_type, [])
        if patterns:
            template = patterns[0]
            return template.immediate_patterns[:2]
        return ["Your choice creates an immediate shift in your journey"]

    async def _generate_delayed_outcomes(  # noqa: ARG002
        self, user_choice: UserChoice, scene: Scene, session_state: SessionState
    ) -> list[str]:
        """Generate delayed outcomes from choice."""
        patterns = self.outcome_templates.get(user_choice.choice_type, [])
        if patterns:
            template = patterns[0]
            return template.delayed_patterns[:1]
        return []

    async def _generate_emotional_impact(  # noqa: ARG002
        self, user_choice: UserChoice, scene: Scene, session_state: SessionState
    ) -> dict[str, Any]:
        """Generate emotional impact from choice."""
        emotional_mapping = self.emotional_outcome_mappings.get(
            session_state.emotional_state, {}
        )
        return {
            "primary_emotion": emotional_mapping.get("positive_transition", "neutral"),
            "intensity": user_choice.therapeutic_value,
        }

    async def _generate_narrative_consequences(  # noqa: ARG002
        self, user_choice: UserChoice, scene: Scene, session_state: SessionState
    ) -> list[str]:
        """Generate narrative consequences from choice."""
        patterns = self.outcome_templates.get(user_choice.choice_type, [])
        if patterns:
            template = patterns[0]
            return template.narrative_consequences[:2]
        return ["The story continues to unfold"]

    async def _generate_character_development(  # noqa: ARG002
        self, user_choice: UserChoice, session_state: SessionState
    ) -> dict[str, Any]:
        """Generate character development from choice."""
        development: dict[str, Any] = {}
        if user_choice.therapeutic_value > 0.5:
            development["resilience"] = user_choice.therapeutic_value * 0.1
            development["self_awareness"] = user_choice.therapeutic_value * 0.1
        return development

    async def _generate_world_state_changes(  # noqa: ARG002
        self, user_choice: UserChoice, scene: Scene, session_state: SessionState
    ) -> dict[str, Any]:
        """Generate world state changes from choice."""
        return {}

    async def _generate_fallback_outcomes(  # noqa: ARG002
        self, user_choice: UserChoice
    ) -> dict[str, Any]:
        """Generate safe fallback outcomes when normal generation fails."""
        return {
            "immediate": ["Your choice leads to new understanding"],
            "delayed": [],
            "emotional_impact": {"primary_emotion": "neutral", "intensity": 0.5},
            "narrative": ["The story continues"],
            "character_development": {},
            "world_state_changes": {},
        }
