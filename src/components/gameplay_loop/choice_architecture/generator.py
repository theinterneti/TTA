"""
Choice Generator for Therapeutic Text Adventure

This module implements choice generation functionality that creates meaningful,
therapeutically relevant choices that support narrative progression and
therapeutic goals while maintaining player agency.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from ..models.core import (
    Choice,
    ChoiceType,
    DifficultyLevel,
    EmotionalState,
    Scene,
    SessionState,
)

logger = logging.getLogger(__name__)


class ChoiceTemplate:
    """Template for generating therapeutic choices."""

    def __init__(self, choice_type: ChoiceType, template_data: dict[str, Any]):
        self.choice_type = choice_type
        self.template_data = template_data
        self.therapeutic_tags = template_data.get("therapeutic_tags", [])
        self.text_patterns = template_data.get("text_patterns", [])
        self.difficulty_variants = template_data.get("difficulty_variants", {})


class ChoiceGenerator:
    """
    Generates meaningful therapeutic choices that support both narrative
    progression and therapeutic goals while maintaining player agency.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Choice generation resources
        self.choice_templates: dict[ChoiceType, list[ChoiceTemplate]] = {}
        self.therapeutic_choice_patterns: dict[str, dict[str, Any]] = {}
        self.narrative_choice_patterns: dict[str, dict[str, Any]] = {}
        self.emotional_adaptations: dict[EmotionalState, dict[str, Any]] = {}

        logger.info("ChoiceGenerator initialized")

    async def initialize(self) -> bool:
        """Initialize choice generation templates and patterns."""
        try:
            await self._load_choice_templates()
            await self._load_therapeutic_patterns()
            await self._load_narrative_patterns()
            await self._load_emotional_adaptations()

            logger.info("ChoiceGenerator initialization completed")
            return True

        except Exception as e:
            logger.error(f"ChoiceGenerator initialization failed: {e}")
            return False

    async def generate_choices(
        self, scene: Scene, session_state: SessionState, requirements: dict[str, Any]
    ) -> list[Choice]:
        """
        Generate choices for a scene based on requirements.

        Args:
            scene: The scene to generate choices for
            session_state: Current session state
            requirements: Choice generation requirements

        Returns:
            List of generated choices
        """
        try:
            logger.info(f"Generating choices for scene {scene.scene_id}")

            generated_choices = []
            choice_types_needed = requirements.get("choice_types_needed", [])
            max_choices = requirements.get("max_choices", 4)

            # Generate choices for each required type
            for choice_type in choice_types_needed:
                choice = await self._generate_choice_by_type(
                    choice_type, scene, session_state, requirements
                )
                if choice:
                    generated_choices.append(choice)

            # Fill remaining slots with additional choices
            while len(generated_choices) < max_choices:
                additional_choice = await self._generate_additional_choice(
                    scene, session_state, generated_choices, requirements
                )
                if additional_choice:
                    generated_choices.append(additional_choice)
                else:
                    break

            logger.info(f"Generated {len(generated_choices)} choices")
            return generated_choices

        except Exception as e:
            logger.error(f"Failed to generate choices: {e}")
            return []

    async def generate_emotion_appropriate_choice(
        self, choice_type: ChoiceType, emotional_state: str, session_state: SessionState
    ) -> Choice | None:
        """
        Generate a choice appropriate for a specific emotional state.

        Args:
            choice_type: Type of choice to generate
            emotional_state: Target emotional state
            session_state: Current session state

        Returns:
            Generated choice or None if generation failed
        """
        try:
            # Get emotional adaptations
            adaptations = self.emotional_adaptations.get(
                EmotionalState(emotional_state), {}
            )

            # Generate base choice
            base_choice = await self._generate_base_choice(choice_type, session_state)
            if not base_choice:
                return None

            # Apply emotional adaptations
            adapted_choice = await self._apply_emotional_adaptations(
                base_choice, adaptations, emotional_state
            )

            return adapted_choice

        except Exception as e:
            logger.error(f"Failed to generate emotion-appropriate choice: {e}")
            return None

    async def generate_safe_choice(
        self, emotional_state: str, session_state: SessionState
    ) -> Choice | None:
        """
        Generate a safe, supportive choice for any emotional state.

        Args:
            emotional_state: Current emotional state
            session_state: Current session state

        Returns:
            Safe choice or None if generation failed
        """
        try:
            safe_choice_texts = {
                "anxious": "Take a moment to breathe and feel grounded",
                "overwhelmed": "Rest here in this safe space",
                "distressed": "Focus on what feels supportive right now",
                "crisis": "Connect with the safety and support available to you",
                "calm": "Continue with gentle awareness",
                "engaged": "Explore this moment with curiosity",
            }

            choice_text = safe_choice_texts.get(
                emotional_state, "Take your time and choose what feels right"
            )

            safe_choice = Choice(
                choice_text=choice_text,
                description="A gentle, supportive option that honors your current state",
                choice_type=ChoiceType.THERAPEUTIC,
                therapeutic_tags=["safety", "support", "grounding"],
                difficulty_level=DifficultyLevel.GENTLE,
                agency_level=0.8,
                meaningfulness_score=0.7,
                emotional_context=[emotional_state],
                therapeutic_value=0.8,
            )

            return safe_choice

        except Exception as e:
            logger.error(f"Failed to generate safe choice: {e}")
            return None

    # Initialization Methods
    async def _load_choice_templates(self) -> None:
        """Load choice templates for different choice types."""
        # Narrative choice templates
        narrative_templates = [
            ChoiceTemplate(
                ChoiceType.NARRATIVE,
                {
                    "therapeutic_tags": ["exploration", "curiosity"],
                    "text_patterns": [
                        "Explore the {location} more deeply",
                        "Move toward the {interesting_element}",
                        "Investigate what draws your attention",
                    ],
                    "difficulty_variants": {
                        "gentle": "Gently explore what interests you",
                        "standard": "Explore this space with curiosity",
                        "challenging": "Boldly investigate the mysteries here",
                    },
                },
            ),
            ChoiceTemplate(
                ChoiceType.NARRATIVE,
                {
                    "therapeutic_tags": ["connection", "relationship"],
                    "text_patterns": [
                        "Approach the {character} with openness",
                        "Share your thoughts with {character}",
                        "Listen deeply to what {character} offers",
                    ],
                    "difficulty_variants": {
                        "gentle": "Gently connect with the presence here",
                        "standard": "Engage with the character you encounter",
                        "challenging": "Open yourself fully to this connection",
                    },
                },
            ),
        ]

        # Therapeutic choice templates
        therapeutic_templates = [
            ChoiceTemplate(
                ChoiceType.THERAPEUTIC,
                {
                    "therapeutic_tags": ["mindfulness", "present_moment"],
                    "text_patterns": [
                        "Take a mindful breath and center yourself",
                        "Notice what you're experiencing right now",
                        "Bring gentle awareness to this moment",
                    ],
                    "difficulty_variants": {
                        "gentle": "Simply notice your breathing",
                        "standard": "Practice mindful awareness",
                        "challenging": "Deepen your mindfulness practice",
                    },
                },
            ),
            ChoiceTemplate(
                ChoiceType.THERAPEUTIC,
                {
                    "therapeutic_tags": ["emotional_regulation", "self_compassion"],
                    "text_patterns": [
                        "Offer yourself compassion for what you're feeling",
                        "Acknowledge your emotions with kindness",
                        "Practice self-acceptance in this moment",
                    ],
                    "difficulty_variants": {
                        "gentle": "Be gentle with yourself",
                        "standard": "Practice self-compassion",
                        "challenging": "Embrace yourself with full acceptance",
                    },
                },
            ),
        ]

        # Skill building choice templates
        skill_building_templates = [
            ChoiceTemplate(
                ChoiceType.SKILL_BUILDING,
                {
                    "therapeutic_tags": ["coping_skills", "resilience"],
                    "text_patterns": [
                        "Practice a coping skill you've learned",
                        "Apply your resilience to this situation",
                        "Use your inner strength to navigate this",
                    ],
                    "difficulty_variants": {
                        "gentle": "Try a simple coping technique",
                        "standard": "Apply your developing skills",
                        "challenging": "Challenge yourself to grow stronger",
                    },
                },
            )
        ]

        # Emotional regulation choice templates
        emotional_regulation_templates = [
            ChoiceTemplate(
                ChoiceType.EMOTIONAL_REGULATION,
                {
                    "therapeutic_tags": ["emotional_balance", "regulation"],
                    "text_patterns": [
                        "Take steps to regulate your emotional state",
                        "Find balance in your emotional experience",
                        "Work with your emotions skillfully",
                    ],
                    "difficulty_variants": {
                        "gentle": "Gently tend to your emotions",
                        "standard": "Practice emotional regulation",
                        "challenging": "Master your emotional responses",
                    },
                },
            )
        ]

        # Social interaction choice templates
        social_interaction_templates = [
            ChoiceTemplate(
                ChoiceType.SOCIAL_INTERACTION,
                {
                    "therapeutic_tags": ["connection", "communication"],
                    "text_patterns": [
                        "Communicate openly and honestly",
                        "Build connection through sharing",
                        "Practice healthy social interaction",
                    ],
                    "difficulty_variants": {
                        "gentle": "Share something simple about yourself",
                        "standard": "Engage in meaningful dialogue",
                        "challenging": "Open yourself to deep connection",
                    },
                },
            )
        ]

        # Store all templates
        self.choice_templates = {
            ChoiceType.NARRATIVE: narrative_templates,
            ChoiceType.THERAPEUTIC: therapeutic_templates,
            ChoiceType.SKILL_BUILDING: skill_building_templates,
            ChoiceType.EMOTIONAL_REGULATION: emotional_regulation_templates,
            ChoiceType.SOCIAL_INTERACTION: social_interaction_templates,
        }

    async def _load_emotional_adaptations(self) -> None:
        """Load emotional state adaptations for choice generation."""
        self.emotional_adaptations = {
            EmotionalState.CALM: {
                "tone": "balanced",
                "complexity": "standard",
                "therapeutic_emphasis": "growth",
            },
            EmotionalState.ENGAGED: {
                "tone": "dynamic",
                "complexity": "increased",
                "therapeutic_emphasis": "exploration",
            },
            EmotionalState.ANXIOUS: {
                "tone": "calming",
                "complexity": "reduced",
                "therapeutic_emphasis": "grounding",
            },
            EmotionalState.OVERWHELMED: {
                "tone": "deeply_supportive",
                "complexity": "minimal",
                "therapeutic_emphasis": "safety",
            },
            EmotionalState.DISTRESSED: {
                "tone": "protective",
                "complexity": "minimal",
                "therapeutic_emphasis": "support",
            },
            EmotionalState.CRISIS: {
                "tone": "crisis_supportive",
                "complexity": "minimal",
                "therapeutic_emphasis": "immediate_safety",
            },
        }

    # Core Generation Methods
    async def _generate_choice_by_type(
        self,
        choice_type: ChoiceType,
        scene: Scene,
        session_state: SessionState,
        requirements: dict[str, Any],
    ) -> Choice | None:
        """Generate a choice of a specific type."""
        templates = self.choice_templates.get(choice_type, [])
        if not templates:
            return None

        # Select appropriate template
        template = await self._select_template(templates, scene, session_state)

        # Generate choice from template
        choice = await self._generate_from_template(
            template, scene, session_state, requirements
        )

        return choice

    async def _generate_additional_choice(
        self,
        scene: Scene,
        session_state: SessionState,
        existing_choices: list[Choice],
        requirements: dict[str, Any],
    ) -> Choice | None:
        """Generate an additional choice to fill remaining slots."""
        # Determine what type of choice would be most beneficial
        existing_types = [choice.choice_type for choice in existing_choices]

        # Prefer therapeutic choices if we don't have enough
        therapeutic_count = sum(
            1 for t in existing_types if t == ChoiceType.THERAPEUTIC
        )
        total_choices = len(existing_choices)
        therapeutic_ratio = requirements.get("therapeutic_choice_ratio", 0.6)

        if therapeutic_count / (total_choices + 1) < therapeutic_ratio:
            return await self._generate_choice_by_type(
                ChoiceType.THERAPEUTIC, scene, session_state, requirements
            )

        # Otherwise, generate a narrative choice
        return await self._generate_choice_by_type(
            ChoiceType.NARRATIVE, scene, session_state, requirements
        )

    async def _select_template(
        self, templates: list[ChoiceTemplate], scene: Scene, session_state: SessionState
    ) -> ChoiceTemplate:
        """Select the most appropriate template for the context."""
        if not templates:
            return templates[0]

        # Score templates based on therapeutic focus alignment
        best_template = None
        best_score = 0

        for template in templates:
            score = 0

            # Score based on therapeutic tag alignment
            for tag in template.therapeutic_tags:
                if tag in scene.therapeutic_focus:
                    score += 2
                elif any(tag in focus for focus in scene.therapeutic_focus):
                    score += 1

            if score > best_score:
                best_score = score
                best_template = template

        return best_template or templates[0]

    async def _generate_from_template(
        self,
        template: ChoiceTemplate,
        scene: Scene,
        session_state: SessionState,
        requirements: dict[str, Any],
    ) -> Choice:
        """Generate a choice from a template."""
        # Determine difficulty level
        difficulty_level = scene.difficulty_level
        complexity_preference = requirements.get("complexity_preference", "standard")

        if complexity_preference == "simple":
            difficulty_level = DifficultyLevel.GENTLE
        elif complexity_preference == "complex":
            difficulty_level = DifficultyLevel.CHALLENGING

        # Get appropriate text variant
        difficulty_key = difficulty_level.value
        choice_text = template.difficulty_variants.get(
            difficulty_key,
            (
                template.text_patterns[0]
                if template.text_patterns
                else "Continue your journey"
            ),
        )

        # Generate description
        description = await self._generate_choice_description(
            template, scene, session_state
        )

        # Calculate therapeutic value
        therapeutic_value = await self._calculate_therapeutic_value(
            template, scene, session_state
        )

        # Calculate agency and meaningfulness
        agency_level = await self._calculate_agency_level(template, scene)
        meaningfulness_score = await self._calculate_meaningfulness(
            template, scene, session_state
        )

        # Create choice
        choice = Choice(
            choice_text=choice_text,
            description=description,
            choice_type=template.choice_type,
            therapeutic_tags=template.therapeutic_tags.copy(),
            difficulty_level=difficulty_level,
            agency_level=agency_level,
            meaningfulness_score=meaningfulness_score,
            emotional_context=[session_state.emotional_state.value],
            therapeutic_value=therapeutic_value,
        )

        return choice

    async def _generate_base_choice(
        self, choice_type: ChoiceType, session_state: SessionState
    ) -> Choice | None:
        """Generate a base choice of the specified type."""
        templates = self.choice_templates.get(choice_type, [])
        if not templates:
            return None

        template = templates[0]  # Use first template as base

        base_choice = Choice(
            choice_text="Take a meaningful action",
            description="A choice that supports your journey",
            choice_type=choice_type,
            therapeutic_tags=template.therapeutic_tags.copy(),
            difficulty_level=DifficultyLevel.STANDARD,
            agency_level=0.7,
            meaningfulness_score=0.6,
            emotional_context=[session_state.emotional_state.value],
            therapeutic_value=0.6,
        )

        return base_choice

    async def _apply_emotional_adaptations(
        self, base_choice: Choice, adaptations: dict[str, Any], emotional_state: str
    ) -> Choice:
        """Apply emotional adaptations to a base choice."""
        adapted_choice = Choice(**base_choice.model_dump())
        adapted_choice.choice_id = str(uuid4())  # New ID for adapted choice

        tone = adaptations.get("tone", "balanced")
        complexity = adaptations.get("complexity", "standard")
        therapeutic_emphasis = adaptations.get("therapeutic_emphasis", "growth")

        # Adapt choice text based on tone
        if tone == "calming":
            adapted_choice.choice_text = f"Gently {base_choice.choice_text.lower()}"
        elif tone == "deeply_supportive":
            adapted_choice.choice_text = (
                f"With full support, {base_choice.choice_text.lower()}"
            )
        elif tone == "protective":
            adapted_choice.choice_text = (
                f"In complete safety, {base_choice.choice_text.lower()}"
            )
        elif tone == "crisis_supportive":
            adapted_choice.choice_text = (
                "Focus on what feels most safe and supportive right now"
            )
        elif tone == "dynamic":
            adapted_choice.choice_text = f"Actively {base_choice.choice_text.lower()}"

        # Adjust difficulty based on complexity
        if complexity == "reduced":
            adapted_choice.difficulty_level = DifficultyLevel.GENTLE
        elif complexity == "minimal":
            adapted_choice.difficulty_level = DifficultyLevel.GENTLE
            adapted_choice.therapeutic_value = min(
                adapted_choice.therapeutic_value, 0.7
            )
        elif complexity == "increased":
            if adapted_choice.difficulty_level == DifficultyLevel.GENTLE:
                adapted_choice.difficulty_level = DifficultyLevel.STANDARD

        # Add therapeutic emphasis tags
        if therapeutic_emphasis not in adapted_choice.therapeutic_tags:
            adapted_choice.therapeutic_tags.append(therapeutic_emphasis)

        # Update emotional context
        adapted_choice.emotional_context = [emotional_state]

        return adapted_choice

    # Helper Calculation Methods
    async def _generate_choice_description(
        self, template: ChoiceTemplate, scene: Scene, session_state: SessionState
    ) -> str:
        """Generate a description for a choice based on template and context."""
        base_descriptions = {
            ChoiceType.NARRATIVE: "Advance the story through meaningful action",
            ChoiceType.THERAPEUTIC: "Support your wellbeing and growth",
            ChoiceType.SKILL_BUILDING: "Practice and develop important life skills",
            ChoiceType.EMOTIONAL_REGULATION: "Work with your emotions skillfully",
            ChoiceType.SOCIAL_INTERACTION: "Connect and communicate with others",
        }

        base_description = base_descriptions.get(
            template.choice_type, "Take meaningful action"
        )

        # Enhance description based on therapeutic tags
        if "mindfulness" in template.therapeutic_tags:
            return f"{base_description} through mindful awareness"
        if "grounding" in template.therapeutic_tags:
            return f"{base_description} while staying grounded and centered"
        if "self_compassion" in template.therapeutic_tags:
            return f"{base_description} with kindness toward yourself"
        return base_description

    async def _calculate_therapeutic_value(
        self, template: ChoiceTemplate, scene: Scene, session_state: SessionState
    ) -> float:
        """Calculate the therapeutic value of a choice."""
        base_value = 0.5

        # Increase value based on therapeutic tag alignment
        tag_alignment = len(
            set(template.therapeutic_tags) & set(scene.therapeutic_focus)
        )
        base_value += tag_alignment * 0.1

        # Adjust based on choice type
        type_values = {
            ChoiceType.THERAPEUTIC: 0.8,
            ChoiceType.SKILL_BUILDING: 0.7,
            ChoiceType.EMOTIONAL_REGULATION: 0.7,
            ChoiceType.SOCIAL_INTERACTION: 0.6,
            ChoiceType.NARRATIVE: 0.5,
        }

        type_value = type_values.get(template.choice_type, 0.5)
        base_value = max(base_value, type_value)

        # Adjust for emotional state appropriateness
        if session_state.emotional_state in [
            EmotionalState.ANXIOUS,
            EmotionalState.OVERWHELMED,
        ]:
            if (
                "grounding" in template.therapeutic_tags
                or "safety" in template.therapeutic_tags
            ):
                base_value += 0.1
        elif session_state.emotional_state == EmotionalState.ENGAGED:
            if (
                "exploration" in template.therapeutic_tags
                or "growth" in template.therapeutic_tags
            ):
                base_value += 0.1

        return min(base_value, 1.0)

    async def _calculate_agency_level(
        self, template: ChoiceTemplate, scene: Scene
    ) -> float:
        """Calculate the agency level of a choice."""
        base_agency = 0.7

        # Narrative choices typically offer high agency
        if template.choice_type == ChoiceType.NARRATIVE:
            base_agency = 0.8

        # Therapeutic choices offer moderate agency (guided but meaningful)
        elif template.choice_type == ChoiceType.THERAPEUTIC:
            base_agency = 0.6

        # Skill building choices offer high agency (active practice)
        elif template.choice_type == ChoiceType.SKILL_BUILDING:
            base_agency = 0.8

        # Adjust based on scene difficulty
        if scene.difficulty_level == DifficultyLevel.GENTLE:
            base_agency *= 0.9  # Slightly less agency for gentler experiences
        elif scene.difficulty_level == DifficultyLevel.CHALLENGING:
            base_agency *= 1.1  # More agency for challenging experiences

        return min(base_agency, 1.0)

    async def _calculate_meaningfulness(
        self, template: ChoiceTemplate, scene: Scene, session_state: SessionState
    ) -> float:
        """Calculate the meaningfulness score of a choice."""
        base_meaningfulness = 0.6

        # Increase meaningfulness based on therapeutic relevance
        therapeutic_relevance = len(
            set(template.therapeutic_tags) & set(scene.therapeutic_focus)
        )
        base_meaningfulness += therapeutic_relevance * 0.1

        # Therapeutic choices are inherently meaningful
        if (
            template.choice_type == ChoiceType.THERAPEUTIC
            or template.choice_type == ChoiceType.SKILL_BUILDING
        ):
            base_meaningfulness += 0.1

        # Adjust based on session context
        if len(session_state.choice_history) > 5:  # Later in session
            base_meaningfulness += (
                0.05  # Choices become more meaningful as session progresses
            )

        # Adjust for emotional state
        if session_state.emotional_state in [
            EmotionalState.DISTRESSED,
            EmotionalState.CRISIS,
        ]:
            if (
                "safety" in template.therapeutic_tags
                or "support" in template.therapeutic_tags
            ):
                base_meaningfulness += (
                    0.2  # Safety choices are highly meaningful in distress
                )

        return min(base_meaningfulness, 1.0)

    async def _load_therapeutic_patterns(self) -> None:
        """Load therapeutic choice patterns."""
        self.therapeutic_choice_patterns = {
            "mindfulness": {
                "focus": "present_moment_awareness",
                "approach": "gentle_invitation",
                "language": "non_directive",
                "therapeutic_value": 0.8,
            },
            "grounding": {
                "focus": "physical_connection",
                "approach": "structured_practice",
                "language": "concrete_instructions",
                "therapeutic_value": 0.9,
            },
            "emotional_regulation": {
                "focus": "emotional_awareness",
                "approach": "skill_application",
                "language": "supportive_guidance",
                "therapeutic_value": 0.7,
            },
            "self_compassion": {
                "focus": "self_acceptance",
                "approach": "gentle_encouragement",
                "language": "compassionate_voice",
                "therapeutic_value": 0.8,
            },
        }

    async def _load_narrative_patterns(self) -> None:
        """Load narrative choice patterns."""
        self.narrative_choice_patterns = {
            "exploration": {
                "focus": "discovery",
                "approach": "curious_investigation",
                "language": "inviting_adventure",
                "agency_level": 0.8,
            },
            "character_interaction": {
                "focus": "relationship_building",
                "approach": "social_connection",
                "language": "interpersonal_engagement",
                "agency_level": 0.7,
            },
            "problem_solving": {
                "focus": "solution_finding",
                "approach": "analytical_thinking",
                "language": "challenge_oriented",
                "agency_level": 0.9,
            },
        }
