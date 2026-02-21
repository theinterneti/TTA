"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Narrative/Complexity_adapter]]

# Logseq: [[TTA/Components/Gameplay_loop/Narrative/Complexity_adapter]]
Narrative Complexity Adapter for Therapeutic Text Adventure

This module implements adaptive complexity management for narrative content,
adjusting difficulty, cognitive load, and therapeutic intensity based on
user state, progress, and therapeutic needs.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from ..models.core import DifficultyLevel, EmotionalState, Scene, SessionState

logger = logging.getLogger(__name__)


class ComplexityDimension(str, Enum):
    """Dimensions of narrative complexity that can be adapted."""

    COGNITIVE_LOAD = "cognitive_load"
    EMOTIONAL_INTENSITY = "emotional_intensity"
    CHOICE_COMPLEXITY = "choice_complexity"
    THERAPEUTIC_DEPTH = "therapeutic_depth"
    NARRATIVE_LENGTH = "narrative_length"
    VOCABULARY_LEVEL = "vocabulary_level"
    CONCEPTUAL_ABSTRACTION = "conceptual_abstraction"


class AdaptationStrategy(str, Enum):
    """Strategies for complexity adaptation."""

    SIMPLIFY = "simplify"
    MAINTAIN = "maintain"
    INCREASE = "increase"
    GRADUAL_INCREASE = "gradual_increase"
    EMERGENCY_SIMPLIFY = "emergency_simplify"


class NarrativeComplexityAdapter:
    """
    Adapts narrative complexity based on user state, therapeutic progress,
    and real-time feedback to optimize engagement and therapeutic effectiveness.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Complexity thresholds and mappings
        self.complexity_thresholds: dict[ComplexityDimension, dict[str, float]] = {}
        self.adaptation_rules: dict[
            EmotionalState, dict[ComplexityDimension, AdaptationStrategy]
        ] = {}
        self.difficulty_mappings: dict[
            DifficultyLevel, dict[ComplexityDimension, float]
        ] = {}

        logger.info("NarrativeComplexityAdapter initialized")

    async def initialize(self) -> bool:
        """Initialize complexity adaptation rules and thresholds."""
        try:
            await self._load_complexity_thresholds()
            await self._load_adaptation_rules()
            await self._load_difficulty_mappings()

            logger.info("NarrativeComplexityAdapter initialization completed")
            return True

        except Exception as e:
            logger.error(f"NarrativeComplexityAdapter initialization failed: {e}")
            return False

    async def adapt_scene_complexity(
        self, scene: Scene, session_state: SessionState
    ) -> Scene:
        """
        Adapt scene complexity based on current session state.

        Args:
            scene: The scene to adapt
            session_state: Current session state with user context

        Returns:
            Scene with adapted complexity
        """
        try:
            logger.info(f"Adapting complexity for scene {scene.scene_id}")

            # Analyze current user state
            complexity_analysis = await self._analyze_complexity_needs(session_state)

            # Determine adaptation strategies for each dimension
            adaptation_strategies = await self._determine_adaptation_strategies(
                complexity_analysis, session_state.emotional_state
            )

            # Apply adaptations
            adapted_scene = Scene(**scene.model_dump())

            for dimension, strategy in adaptation_strategies.items():
                adapted_scene = await self._apply_complexity_adaptation(
                    adapted_scene, dimension, strategy, session_state
                )

            logger.info(
                f"Adapted scene complexity using strategies: {adaptation_strategies}"
            )
            return adapted_scene

        except Exception as e:
            logger.error(f"Failed to adapt scene complexity: {e}")
            return scene

    async def simplify_for_intervention(
        self, scene: Scene, session_state: SessionState
    ) -> Scene:
        """
        Simplify scene complexity for therapeutic interventions.

        Args:
            scene: The scene to simplify
            session_state: Current session state

        Returns:
            Simplified scene optimized for intervention
        """
        try:
            logger.info(f"Simplifying scene {scene.scene_id} for intervention")

            simplified_scene = Scene(**scene.model_dump())

            # Apply emergency simplification across all dimensions
            for dimension in ComplexityDimension:
                simplified_scene = await self._apply_complexity_adaptation(
                    simplified_scene,
                    dimension,
                    AdaptationStrategy.EMERGENCY_SIMPLIFY,
                    session_state,
                )

            # Ensure intervention-appropriate characteristics
            simplified_scene.difficulty_level = DifficultyLevel.GENTLE
            simplified_scene.estimated_duration = min(
                simplified_scene.estimated_duration, 600
            )

            logger.info(
                f"Simplified scene for intervention: {simplified_scene.scene_id}"
            )
            return simplified_scene

        except Exception as e:
            logger.error(f"Failed to simplify scene for intervention: {e}")
            return scene

    async def assess_scene_complexity(
        self, scene: Scene
    ) -> dict[ComplexityDimension, float]:
        """
        Assess the current complexity level of a scene across all dimensions.

        Args:
            scene: The scene to assess

        Returns:
            Dictionary mapping complexity dimensions to their current levels (0.0-1.0)
        """
        try:
            complexity_scores = {}

            # Assess cognitive load
            complexity_scores[
                ComplexityDimension.COGNITIVE_LOAD
            ] = await self._assess_cognitive_load(scene)

            # Assess emotional intensity
            complexity_scores[
                ComplexityDimension.EMOTIONAL_INTENSITY
            ] = await self._assess_emotional_intensity(scene)

            # Assess choice complexity
            complexity_scores[
                ComplexityDimension.CHOICE_COMPLEXITY
            ] = await self._assess_choice_complexity(scene)

            # Assess therapeutic depth
            complexity_scores[
                ComplexityDimension.THERAPEUTIC_DEPTH
            ] = await self._assess_therapeutic_depth(scene)

            # Assess narrative length
            complexity_scores[
                ComplexityDimension.NARRATIVE_LENGTH
            ] = await self._assess_narrative_length(scene)

            # Assess vocabulary level
            complexity_scores[
                ComplexityDimension.VOCABULARY_LEVEL
            ] = await self._assess_vocabulary_level(scene)

            # Assess conceptual abstraction
            complexity_scores[
                ComplexityDimension.CONCEPTUAL_ABSTRACTION
            ] = await self._assess_conceptual_abstraction(scene)

            return complexity_scores

        except Exception as e:
            logger.error(f"Failed to assess scene complexity: {e}")
            return {}

    # Initialization Methods
    async def _load_complexity_thresholds(self) -> None:
        """Load complexity thresholds for different dimensions."""
        self.complexity_thresholds = {
            ComplexityDimension.COGNITIVE_LOAD: {
                "low": 0.3,
                "medium": 0.6,
                "high": 0.8,
                "maximum": 1.0,
            },
            ComplexityDimension.EMOTIONAL_INTENSITY: {
                "gentle": 0.2,
                "moderate": 0.5,
                "intense": 0.7,
                "maximum": 0.9,
            },
            ComplexityDimension.CHOICE_COMPLEXITY: {
                "simple": 0.25,
                "moderate": 0.5,
                "complex": 0.75,
                "very_complex": 1.0,
            },
            ComplexityDimension.THERAPEUTIC_DEPTH: {
                "surface": 0.2,
                "moderate": 0.5,
                "deep": 0.8,
                "profound": 1.0,
            },
            ComplexityDimension.NARRATIVE_LENGTH: {
                "brief": 0.3,
                "moderate": 0.6,
                "extended": 0.8,
                "lengthy": 1.0,
            },
            ComplexityDimension.VOCABULARY_LEVEL: {
                "simple": 0.3,
                "standard": 0.6,
                "advanced": 0.8,
                "complex": 1.0,
            },
            ComplexityDimension.CONCEPTUAL_ABSTRACTION: {
                "concrete": 0.2,
                "mixed": 0.5,
                "abstract": 0.8,
                "highly_abstract": 1.0,
            },
        }

    async def _load_adaptation_rules(self) -> None:
        """Load adaptation rules based on emotional states."""
        self.adaptation_rules = {
            EmotionalState.CALM: {
                ComplexityDimension.COGNITIVE_LOAD: AdaptationStrategy.MAINTAIN,
                ComplexityDimension.EMOTIONAL_INTENSITY: AdaptationStrategy.MAINTAIN,
                ComplexityDimension.CHOICE_COMPLEXITY: AdaptationStrategy.MAINTAIN,
                ComplexityDimension.THERAPEUTIC_DEPTH: AdaptationStrategy.GRADUAL_INCREASE,
            },
            EmotionalState.ENGAGED: {
                ComplexityDimension.COGNITIVE_LOAD: AdaptationStrategy.GRADUAL_INCREASE,
                ComplexityDimension.EMOTIONAL_INTENSITY: AdaptationStrategy.MAINTAIN,
                ComplexityDimension.CHOICE_COMPLEXITY: AdaptationStrategy.INCREASE,
                ComplexityDimension.THERAPEUTIC_DEPTH: AdaptationStrategy.INCREASE,
            },
            EmotionalState.ANXIOUS: {
                ComplexityDimension.COGNITIVE_LOAD: AdaptationStrategy.SIMPLIFY,
                ComplexityDimension.EMOTIONAL_INTENSITY: AdaptationStrategy.SIMPLIFY,
                ComplexityDimension.CHOICE_COMPLEXITY: AdaptationStrategy.SIMPLIFY,
                ComplexityDimension.THERAPEUTIC_DEPTH: AdaptationStrategy.MAINTAIN,
            },
            EmotionalState.OVERWHELMED: {
                ComplexityDimension.COGNITIVE_LOAD: AdaptationStrategy.EMERGENCY_SIMPLIFY,
                ComplexityDimension.EMOTIONAL_INTENSITY: AdaptationStrategy.EMERGENCY_SIMPLIFY,
                ComplexityDimension.CHOICE_COMPLEXITY: AdaptationStrategy.EMERGENCY_SIMPLIFY,
                ComplexityDimension.THERAPEUTIC_DEPTH: AdaptationStrategy.SIMPLIFY,
            },
            EmotionalState.DISTRESSED: {
                ComplexityDimension.COGNITIVE_LOAD: AdaptationStrategy.EMERGENCY_SIMPLIFY,
                ComplexityDimension.EMOTIONAL_INTENSITY: AdaptationStrategy.EMERGENCY_SIMPLIFY,
                ComplexityDimension.CHOICE_COMPLEXITY: AdaptationStrategy.EMERGENCY_SIMPLIFY,
                ComplexityDimension.THERAPEUTIC_DEPTH: AdaptationStrategy.EMERGENCY_SIMPLIFY,
            },
            EmotionalState.CRISIS: {
                ComplexityDimension.COGNITIVE_LOAD: AdaptationStrategy.EMERGENCY_SIMPLIFY,
                ComplexityDimension.EMOTIONAL_INTENSITY: AdaptationStrategy.EMERGENCY_SIMPLIFY,
                ComplexityDimension.CHOICE_COMPLEXITY: AdaptationStrategy.EMERGENCY_SIMPLIFY,
                ComplexityDimension.THERAPEUTIC_DEPTH: AdaptationStrategy.EMERGENCY_SIMPLIFY,
            },
        }

    async def _load_difficulty_mappings(self) -> None:
        """Load mappings between difficulty levels and complexity dimensions."""
        self.difficulty_mappings = {
            DifficultyLevel.GENTLE: {
                ComplexityDimension.COGNITIVE_LOAD: 0.3,
                ComplexityDimension.EMOTIONAL_INTENSITY: 0.2,
                ComplexityDimension.CHOICE_COMPLEXITY: 0.25,
                ComplexityDimension.THERAPEUTIC_DEPTH: 0.4,
                ComplexityDimension.NARRATIVE_LENGTH: 0.4,
                ComplexityDimension.VOCABULARY_LEVEL: 0.3,
                ComplexityDimension.CONCEPTUAL_ABSTRACTION: 0.3,
            },
            DifficultyLevel.STANDARD: {
                ComplexityDimension.COGNITIVE_LOAD: 0.6,
                ComplexityDimension.EMOTIONAL_INTENSITY: 0.5,
                ComplexityDimension.CHOICE_COMPLEXITY: 0.5,
                ComplexityDimension.THERAPEUTIC_DEPTH: 0.6,
                ComplexityDimension.NARRATIVE_LENGTH: 0.6,
                ComplexityDimension.VOCABULARY_LEVEL: 0.6,
                ComplexityDimension.CONCEPTUAL_ABSTRACTION: 0.5,
            },
            DifficultyLevel.CHALLENGING: {
                ComplexityDimension.COGNITIVE_LOAD: 0.8,
                ComplexityDimension.EMOTIONAL_INTENSITY: 0.7,
                ComplexityDimension.CHOICE_COMPLEXITY: 0.75,
                ComplexityDimension.THERAPEUTIC_DEPTH: 0.8,
                ComplexityDimension.NARRATIVE_LENGTH: 0.8,
                ComplexityDimension.VOCABULARY_LEVEL: 0.8,
                ComplexityDimension.CONCEPTUAL_ABSTRACTION: 0.7,
            },
            DifficultyLevel.INTENSIVE: {
                ComplexityDimension.COGNITIVE_LOAD: 1.0,
                ComplexityDimension.EMOTIONAL_INTENSITY: 0.9,
                ComplexityDimension.CHOICE_COMPLEXITY: 1.0,
                ComplexityDimension.THERAPEUTIC_DEPTH: 1.0,
                ComplexityDimension.NARRATIVE_LENGTH: 1.0,
                ComplexityDimension.VOCABULARY_LEVEL: 1.0,
                ComplexityDimension.CONCEPTUAL_ABSTRACTION: 0.9,
            },
        }

    # Core Analysis and Adaptation Methods
    async def _analyze_complexity_needs(
        self, session_state: SessionState
    ) -> dict[str, Any]:
        """Analyze current session state to determine complexity needs."""
        return {
            "emotional_state": session_state.emotional_state,
            "difficulty_level": session_state.difficulty_level,
            "session_duration": len(session_state.choice_history) * 300,  # Estimate
            "therapeutic_progress": session_state.therapeutic_context.progress_markers,
            "recent_performance": self._analyze_recent_performance(session_state),
            "cognitive_load_indicators": self._assess_cognitive_load_indicators(
                session_state
            ),
        }

    async def _determine_adaptation_strategies(
        self, complexity_analysis: dict[str, Any], emotional_state: EmotionalState
    ) -> dict[ComplexityDimension, AdaptationStrategy]:
        """Determine adaptation strategies based on analysis."""
        # Start with emotional state rules
        base_strategies = self.adaptation_rules.get(emotional_state, {})

        # Adjust based on other factors
        strategies = base_strategies.copy()

        # Adjust for session duration (fatigue factor)
        session_duration = complexity_analysis.get("session_duration", 0)
        if session_duration > 1800:  # 30 minutes
            for dimension in [
                ComplexityDimension.COGNITIVE_LOAD,
                ComplexityDimension.NARRATIVE_LENGTH,
            ]:
                if strategies.get(dimension) == AdaptationStrategy.INCREASE:
                    strategies[dimension] = AdaptationStrategy.MAINTAIN
                elif strategies.get(dimension) == AdaptationStrategy.MAINTAIN:
                    strategies[dimension] = AdaptationStrategy.SIMPLIFY

        # Adjust for recent performance
        recent_performance = complexity_analysis.get("recent_performance", 0.5)
        if recent_performance < 0.3:  # Poor performance
            for dimension in strategies:
                if strategies[dimension] in [
                    AdaptationStrategy.INCREASE,
                    AdaptationStrategy.GRADUAL_INCREASE,
                ]:
                    strategies[dimension] = AdaptationStrategy.MAINTAIN
        elif recent_performance > 0.8:  # Excellent performance
            for dimension in strategies:
                if strategies[dimension] == AdaptationStrategy.MAINTAIN:
                    strategies[dimension] = AdaptationStrategy.GRADUAL_INCREASE

        return strategies

    async def _apply_complexity_adaptation(
        self,
        scene: Scene,
        dimension: ComplexityDimension,
        strategy: AdaptationStrategy,
        session_state: SessionState,
    ) -> Scene:
        """Apply complexity adaptation for a specific dimension."""
        if dimension == ComplexityDimension.COGNITIVE_LOAD:
            return await self._adapt_cognitive_load(scene, strategy)
        if dimension == ComplexityDimension.EMOTIONAL_INTENSITY:
            return await self._adapt_emotional_intensity(scene, strategy)
        if dimension == ComplexityDimension.CHOICE_COMPLEXITY:
            return await self._adapt_choice_complexity(scene, strategy)
        if dimension == ComplexityDimension.THERAPEUTIC_DEPTH:
            return await self._adapt_therapeutic_depth(scene, strategy)
        if dimension == ComplexityDimension.NARRATIVE_LENGTH:
            return await self._adapt_narrative_length(scene, strategy)
        if dimension == ComplexityDimension.VOCABULARY_LEVEL:
            return await self._adapt_vocabulary_level(scene, strategy)
        if dimension == ComplexityDimension.CONCEPTUAL_ABSTRACTION:
            return await self._adapt_conceptual_abstraction(scene, strategy)
        return scene

    # Helper Methods
    def _analyze_recent_performance(self, session_state: SessionState) -> float:
        """Analyze recent performance based on choice history."""
        if not session_state.choice_history:
            return 0.5  # Neutral performance

        # Look at last 3 choices
        recent_choices = session_state.choice_history[-3:]

        # Calculate average therapeutic value
        total_value = sum(
            choice.get("therapeutic_value", 0.5) for choice in recent_choices
        )
        return total_value / len(recent_choices)

    def _assess_cognitive_load_indicators(
        self, session_state: SessionState
    ) -> dict[str, Any]:
        """Assess indicators of cognitive load from session state."""
        indicators = {
            "choice_time_average": 30,  # Default assumption
            "choice_complexity_preference": "standard",
            "error_rate": 0.1,  # Default assumption
            "engagement_level": 0.7,  # Default assumption
        }

        # Adjust based on choice history length (proxy for engagement)
        if len(session_state.choice_history) > 10:
            indicators["engagement_level"] = 0.8
        elif len(session_state.choice_history) < 3:
            indicators["engagement_level"] = 0.5

        return indicators

    # Dimension-Specific Adaptation Methods
    async def _adapt_cognitive_load(
        self, scene: Scene, strategy: AdaptationStrategy
    ) -> Scene:
        """Adapt cognitive load of the scene."""
        if strategy in (
            AdaptationStrategy.SIMPLIFY,
            AdaptationStrategy.EMERGENCY_SIMPLIFY,
        ):
            # Simplify narrative structure and reduce information density
            content_parts = scene.narrative_content.split(". ")
            if len(content_parts) > 3:
                # Keep only the most essential parts
                scene.narrative_content = ". ".join(content_parts[:3]) + "."

            # Reduce learning objectives
            scene.learning_objectives = scene.learning_objectives[:2]

        elif strategy == AdaptationStrategy.INCREASE:
            # Add more detailed descriptions and context
            scene.narrative_content += " The richness of this experience offers multiple layers of meaning and opportunity for exploration."

        return scene

    async def _adapt_emotional_intensity(
        self, scene: Scene, strategy: AdaptationStrategy
    ) -> Scene:
        """Adapt emotional intensity of the scene."""
        if strategy in (
            AdaptationStrategy.SIMPLIFY,
            AdaptationStrategy.EMERGENCY_SIMPLIFY,
        ):
            # Make content more calming and less emotionally challenging
            scene.emotional_tone = "deeply_calming"

            # Add calming elements
            calming_addition = (
                " A profound sense of peace and safety permeates this space."
            )
            scene.narrative_content += calming_addition

        elif strategy == AdaptationStrategy.INCREASE:
            # Add more emotional depth and engagement
            scene.narrative_content += " This moment invites you to explore the full spectrum of your emotional experience."

        return scene

    async def _adapt_choice_complexity(
        self, scene: Scene, strategy: AdaptationStrategy
    ) -> Scene:
        """Adapt choice complexity (this affects future choice generation)."""
        # Store complexity preference for choice generation
        if not hasattr(scene, "choice_complexity_preference"):
            scene.choice_complexity_preference = "standard"

        if strategy in (
            AdaptationStrategy.SIMPLIFY,
            AdaptationStrategy.EMERGENCY_SIMPLIFY,
        ):
            scene.choice_complexity_preference = "simple"
        elif strategy == AdaptationStrategy.INCREASE:
            scene.choice_complexity_preference = "complex"

        return scene

    async def _adapt_therapeutic_depth(
        self, scene: Scene, strategy: AdaptationStrategy
    ) -> Scene:
        """Adapt therapeutic depth of the scene."""
        if strategy in (
            AdaptationStrategy.SIMPLIFY,
            AdaptationStrategy.EMERGENCY_SIMPLIFY,
        ):
            # Focus on basic therapeutic elements
            scene.therapeutic_focus = scene.therapeutic_focus[:2]  # Limit focus areas

        elif strategy in (
            AdaptationStrategy.INCREASE,
            AdaptationStrategy.GRADUAL_INCREASE,
        ):
            # Add deeper therapeutic elements
            if "self_awareness" not in scene.therapeutic_focus:
                scene.therapeutic_focus.append("self_awareness")

        return scene

    async def _adapt_narrative_length(
        self, scene: Scene, strategy: AdaptationStrategy
    ) -> Scene:
        """Adapt narrative length."""
        if strategy in (
            AdaptationStrategy.SIMPLIFY,
            AdaptationStrategy.EMERGENCY_SIMPLIFY,
        ):
            # Shorten narrative content
            sentences = scene.narrative_content.split(". ")
            if len(sentences) > 4:
                scene.narrative_content = ". ".join(sentences[:4]) + "."

            # Reduce estimated duration
            scene.estimated_duration = min(scene.estimated_duration, 180)

        elif strategy == AdaptationStrategy.INCREASE:
            # Extend narrative with additional detail
            scene.narrative_content += " Take time to fully absorb and appreciate all the nuances of this experience."
            scene.estimated_duration = min(scene.estimated_duration + 120, 600)

        return scene

    async def _adapt_vocabulary_level(
        self, scene: Scene, strategy: AdaptationStrategy
    ) -> Scene:
        """Adapt vocabulary complexity."""
        if strategy in (
            AdaptationStrategy.SIMPLIFY,
            AdaptationStrategy.EMERGENCY_SIMPLIFY,
        ):
            # Replace complex words with simpler alternatives
            replacements = {
                "contemplation": "thinking",
                "serenity": "peace",
                "profound": "deep",
                "encompasses": "includes",
                "facilitate": "help",
                "therapeutic": "healing",
            }

            content = scene.narrative_content
            for complex_word, simple_word in replacements.items():
                content = content.replace(complex_word, simple_word)
            scene.narrative_content = content

        return scene

    async def _adapt_conceptual_abstraction(
        self, scene: Scene, strategy: AdaptationStrategy
    ) -> Scene:
        """Adapt conceptual abstraction level."""
        if strategy in (
            AdaptationStrategy.SIMPLIFY,
            AdaptationStrategy.EMERGENCY_SIMPLIFY,
        ):
            # Make concepts more concrete and tangible
            scene.narrative_content += (
                " Focus on what you can directly see, hear, and feel in this moment."
            )

        elif strategy == AdaptationStrategy.INCREASE:
            # Add more abstract therapeutic concepts
            scene.narrative_content += " Consider the deeper meanings and connections that emerge from this experience."

        return scene

    # Assessment Methods
    async def _assess_cognitive_load(self, scene: Scene) -> float:
        """Assess cognitive load of a scene (0.0-1.0)."""
        load_score = 0.0

        # Assess based on content length
        word_count = len(scene.narrative_content.split())
        if word_count > 200:
            load_score += 0.4
        elif word_count > 100:
            load_score += 0.2

        # Assess based on learning objectives count
        objective_count = len(scene.learning_objectives)
        load_score += min(objective_count * 0.15, 0.3)

        # Assess based on therapeutic focus count
        focus_count = len(scene.therapeutic_focus)
        load_score += min(focus_count * 0.1, 0.3)

        return min(load_score, 1.0)

    async def _assess_emotional_intensity(self, scene: Scene) -> float:
        """Assess emotional intensity of a scene (0.0-1.0)."""
        intensity_keywords = {
            "high": ["intense", "overwhelming", "powerful", "dramatic", "challenging"],
            "medium": ["meaningful", "significant", "important", "engaging"],
            "low": ["gentle", "calm", "peaceful", "soothing", "quiet"],
        }

        content_lower = scene.narrative_content.lower()

        high_count = sum(
            1 for word in intensity_keywords["high"] if word in content_lower
        )
        medium_count = sum(
            1 for word in intensity_keywords["medium"] if word in content_lower
        )
        low_count = sum(
            1 for word in intensity_keywords["low"] if word in content_lower
        )

        if high_count > 0:
            return 0.8
        if medium_count > low_count:
            return 0.5
        return 0.2

    async def _assess_choice_complexity(self, scene: Scene) -> float:
        """Assess choice complexity (0.0-1.0)."""
        # This would typically assess the choices available in the scene
        # For now, return a default based on scene type
        complexity_by_type = {
            "introduction": 0.3,
            "exploration": 0.5,
            "therapeutic": 0.4,
            "challenge": 0.7,
            "reflection": 0.5,
            "resolution": 0.4,
        }

        return complexity_by_type.get(
            (
                scene.scene_type.value
                if hasattr(scene.scene_type, "value")
                else str(scene.scene_type)
            ),
            0.5,
        )

    async def _assess_therapeutic_depth(self, scene: Scene) -> float:
        """Assess therapeutic depth of a scene (0.0-1.0)."""
        depth_score = 0.0

        # Assess based on therapeutic focus count and type
        focus_count = len(scene.therapeutic_focus)
        depth_score += min(focus_count * 0.2, 0.4)

        # Assess based on therapeutic keywords
        therapeutic_keywords = [
            "awareness",
            "insight",
            "growth",
            "healing",
            "understanding",
            "reflection",
            "mindfulness",
            "compassion",
            "resilience",
        ]

        content_lower = scene.narrative_content.lower()
        keyword_count = sum(
            1 for keyword in therapeutic_keywords if keyword in content_lower
        )
        depth_score += min(keyword_count * 0.1, 0.6)

        return min(depth_score, 1.0)

    async def _assess_narrative_length(self, scene: Scene) -> float:
        """Assess narrative length (0.0-1.0)."""
        word_count = len(scene.narrative_content.split())

        if word_count < 50:
            return 0.2
        if word_count < 100:
            return 0.4
        if word_count < 200:
            return 0.6
        if word_count < 300:
            return 0.8
        return 1.0

    async def _assess_vocabulary_level(self, scene: Scene) -> float:
        """Assess vocabulary complexity (0.0-1.0)."""
        complex_words = [
            "contemplation",
            "serenity",
            "profound",
            "encompasses",
            "facilitate",
            "therapeutic",
            "introspection",
            "mindfulness",
            "resilience",
            "cognitive",
        ]

        content_lower = scene.narrative_content.lower()
        complex_count = sum(1 for word in complex_words if word in content_lower)

        word_count = len(scene.narrative_content.split())
        if word_count == 0:
            return 0.0

        complexity_ratio = complex_count / word_count
        return min(complexity_ratio * 10, 1.0)  # Scale up the ratio

    async def _assess_conceptual_abstraction(self, scene: Scene) -> float:
        """Assess conceptual abstraction level (0.0-1.0)."""
        abstract_concepts = [
            "meaning",
            "purpose",
            "connection",
            "wisdom",
            "insight",
            "transformation",
            "journey",
            "growth",
            "potential",
            "essence",
        ]

        concrete_concepts = [
            "see",
            "hear",
            "touch",
            "feel",
            "ground",
            "breath",
            "body",
            "hands",
            "feet",
            "eyes",
            "sound",
        ]

        content_lower = scene.narrative_content.lower()

        abstract_count = sum(
            1 for concept in abstract_concepts if concept in content_lower
        )
        concrete_count = sum(
            1 for concept in concrete_concepts if concept in content_lower
        )

        if abstract_count + concrete_count == 0:
            return 0.5  # Neutral

        return abstract_count / (abstract_count + concrete_count)
