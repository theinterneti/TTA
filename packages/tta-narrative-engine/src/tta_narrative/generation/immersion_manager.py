"""
Immersion Manager for Therapeutic Text Adventure

This module implements immersion management functionality that enhances
player engagement and presence within the therapeutic narrative experience
while maintaining therapeutic effectiveness.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from ..models.core import EmotionalState, Scene, SceneType, SessionState

logger = logging.getLogger(__name__)


class ImmersionTechnique(str, Enum):
    """Techniques for enhancing narrative immersion."""

    SENSORY_DETAIL = "sensory_detail"
    ENVIRONMENTAL_ATMOSPHERE = "environmental_atmosphere"
    CHARACTER_PRESENCE = "character_presence"
    EMOTIONAL_RESONANCE = "emotional_resonance"
    INTERACTIVE_ELEMENTS = "interactive_elements"
    CONTINUITY_WEAVING = "continuity_weaving"
    PERSONAL_CONNECTION = "personal_connection"


class ImmersionLevel(str, Enum):
    """Levels of immersion to target."""

    MINIMAL = "minimal"
    MODERATE = "moderate"
    HIGH = "high"
    DEEP = "deep"


class ImmersionManager:
    """
    Manages narrative immersion to create engaging, present-moment experiences
    that support therapeutic goals while maintaining player engagement.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Immersion enhancement resources
        self.sensory_libraries: dict[str, list[str]] = {}
        self.atmosphere_templates: dict[str, dict[str, Any]] = {}
        self.character_archetypes: dict[str, dict[str, Any]] = {}
        self.immersion_techniques: dict[SceneType, list[ImmersionTechnique]] = {}

        logger.info("ImmersionManager initialized")

    async def initialize(self) -> bool:
        """Initialize immersion enhancement resources."""
        try:
            await self._load_sensory_libraries()
            await self._load_atmosphere_templates()
            await self._load_character_archetypes()
            await self._load_immersion_techniques()

            logger.info("ImmersionManager initialization completed")
            return True

        except Exception as e:
            logger.error(f"ImmersionManager initialization failed: {e}")
            return False

    async def enhance_scene_immersion(self, scene: Scene, session_state: SessionState) -> Scene:
        """
        Enhance scene immersion based on therapeutic needs and user state.

        Args:
            scene: The scene to enhance
            session_state: Current session state for context

        Returns:
            Scene with enhanced immersion elements
        """
        try:
            logger.info(f"Enhancing immersion for scene {scene.scene_id}")

            # Determine target immersion level
            target_level = await self._determine_immersion_level(scene, session_state)

            # Select appropriate immersion techniques
            techniques = await self._select_immersion_techniques(
                scene.scene_type, target_level, session_state.emotional_state
            )

            # Apply immersion enhancements
            enhanced_scene = Scene(**scene.model_dump())

            for technique in techniques:
                enhanced_scene = await self._apply_immersion_technique(
                    enhanced_scene, technique, session_state
                )

            # Ensure therapeutic integration
            enhanced_scene = await self._integrate_therapeutic_immersion(
                enhanced_scene, session_state
            )

            logger.info(f"Enhanced scene immersion using techniques: {techniques}")
            return enhanced_scene

        except Exception as e:
            logger.error(f"Failed to enhance scene immersion: {e}")
            return scene

    async def assess_immersion_quality(self, scene: Scene) -> dict[str, float]:
        """
        Assess the immersion quality of a scene across different dimensions.

        Args:
            scene: The scene to assess

        Returns:
            Dictionary mapping immersion dimensions to quality scores (0.0-1.0)
        """
        try:
            return {
                "sensory_richness": await self._assess_sensory_richness(scene),
                "atmospheric_depth": await self._assess_atmospheric_depth(scene),
                "emotional_engagement": await self._assess_emotional_engagement(scene),
                "interactive_potential": await self._assess_interactive_potential(scene),
                "personal_relevance": await self._assess_personal_relevance(scene),
                "continuity_strength": await self._assess_continuity_strength(scene),
            }

        except Exception as e:
            logger.error(f"Failed to assess immersion quality: {e}")
            return {}

    # Initialization Methods
    async def _load_sensory_libraries(self) -> None:
        """Load sensory detail libraries for different environments."""
        self.sensory_libraries = {
            "visual": [
                "soft, golden light filtering through leaves",
                "gentle shadows dancing on the ground",
                "warm colors that seem to glow from within",
                "textures that invite touch and exploration",
                "subtle movements that catch the eye",
            ],
            "auditory": [
                "the gentle sound of flowing water",
                "soft rustling of leaves in a light breeze",
                "distant, melodic bird songs",
                "the quiet rhythm of your own breathing",
                "peaceful silence that feels full rather than empty",
            ],
            "tactile": [
                "the solid, reassuring ground beneath your feet",
                "a gentle breeze touching your skin",
                "the smooth texture of worn stone",
                "soft grass that cushions your steps",
                "warmth from sunlight on your face",
            ],
            "olfactory": [
                "the fresh scent of clean air",
                "subtle floral fragrances carried on the breeze",
                "the earthy smell of rich soil",
                "the crisp scent of morning dew",
                "natural aromas that bring a sense of peace",
            ],
            "kinesthetic": [
                "a sense of groundedness and stability",
                "gentle energy flowing through your body",
                "the natural rhythm of your breath",
                "a feeling of being supported and held",
                "subtle sensations of relaxation spreading through you",
            ],
        }

    async def _load_atmosphere_templates(self) -> None:
        """Load atmospheric templates for different moods and settings."""
        self.atmosphere_templates = {
            "peaceful_sanctuary": {
                "mood": "deeply calming",
                "energy": "gentle and supportive",
                "lighting": "soft, warm illumination",
                "space_quality": "open yet intimate",
                "emotional_tone": "safe and nurturing",
            },
            "growth_garden": {
                "mood": "hopeful and encouraging",
                "energy": "vibrant yet balanced",
                "lighting": "natural, life-giving light",
                "space_quality": "expansive with room to grow",
                "emotional_tone": "inspiring and supportive",
            },
            "reflection_chamber": {
                "mood": "contemplative and wise",
                "energy": "still and centered",
                "lighting": "gentle, focused illumination",
                "space_quality": "intimate and contained",
                "emotional_tone": "thoughtful and accepting",
            },
            "healing_space": {
                "mood": "restorative and gentle",
                "energy": "healing and renewing",
                "lighting": "soft, therapeutic glow",
                "space_quality": "protective and embracing",
                "emotional_tone": "compassionate and hopeful",
            },
        }

    async def _load_character_archetypes(self) -> None:
        """Load character archetypes for immersive presence."""
        self.character_archetypes = {
            "wise_companion": {
                "presence": "gentle and knowing",
                "communication_style": "thoughtful questions and reflections",
                "role": "supportive guide without being directive",
                "energy": "calm wisdom and unconditional acceptance",
            },
            "fellow_journeyer": {
                "presence": "warm and relatable",
                "communication_style": "sharing experiences and insights",
                "role": "companion who normalizes the journey",
                "energy": "encouraging solidarity and mutual support",
            },
            "inner_wisdom": {
                "presence": "quiet and intuitive",
                "communication_style": "gentle inner voice and knowing",
                "role": "connection to personal strength and insight",
                "energy": "deep knowing and self-compassion",
            },
        }

    async def _load_immersion_techniques(self) -> None:
        """Load immersion techniques appropriate for different scene types."""
        self.immersion_techniques = {
            SceneType.INTRODUCTION: [
                ImmersionTechnique.SENSORY_DETAIL,
                ImmersionTechnique.ENVIRONMENTAL_ATMOSPHERE,
                ImmersionTechnique.EMOTIONAL_RESONANCE,
            ],
            SceneType.EXPLORATION: [
                ImmersionTechnique.INTERACTIVE_ELEMENTS,
                ImmersionTechnique.SENSORY_DETAIL,
                ImmersionTechnique.CHARACTER_PRESENCE,
            ],
            SceneType.THERAPEUTIC: [
                ImmersionTechnique.EMOTIONAL_RESONANCE,
                ImmersionTechnique.PERSONAL_CONNECTION,
                ImmersionTechnique.ENVIRONMENTAL_ATMOSPHERE,
            ],
            SceneType.CHALLENGE: [
                ImmersionTechnique.INTERACTIVE_ELEMENTS,
                ImmersionTechnique.EMOTIONAL_RESONANCE,
                ImmersionTechnique.CHARACTER_PRESENCE,
            ],
            SceneType.REFLECTION: [
                ImmersionTechnique.PERSONAL_CONNECTION,
                ImmersionTechnique.ENVIRONMENTAL_ATMOSPHERE,
                ImmersionTechnique.CONTINUITY_WEAVING,
            ],
            SceneType.RESOLUTION: [
                ImmersionTechnique.EMOTIONAL_RESONANCE,
                ImmersionTechnique.CONTINUITY_WEAVING,
                ImmersionTechnique.PERSONAL_CONNECTION,
            ],
        }

    # Core Enhancement Methods
    async def _determine_immersion_level(
        self, scene: Scene, session_state: SessionState
    ) -> ImmersionLevel:
        """Determine appropriate immersion level based on context."""
        # Consider emotional state
        if session_state.emotional_state in [
            EmotionalState.CRISIS,
            EmotionalState.DISTRESSED,
        ]:
            return ImmersionLevel.MINIMAL  # Focus on safety, not immersion
        if session_state.emotional_state in [
            EmotionalState.ANXIOUS,
            EmotionalState.OVERWHELMED,
        ]:
            return ImmersionLevel.MODERATE  # Gentle immersion
        if session_state.emotional_state == EmotionalState.ENGAGED:
            return ImmersionLevel.HIGH  # Full immersion
        return ImmersionLevel.MODERATE  # Default

    async def _select_immersion_techniques(
        self,
        scene_type: SceneType,
        target_level: ImmersionLevel,
        emotional_state: EmotionalState,
    ) -> list[ImmersionTechnique]:
        """Select appropriate immersion techniques."""
        available_techniques = self.immersion_techniques.get(scene_type, [])

        # Adjust based on target level
        if target_level == ImmersionLevel.MINIMAL:
            return available_techniques[:1]  # Use only one technique
        if target_level == ImmersionLevel.MODERATE:
            return available_techniques[:2]  # Use two techniques
        return available_techniques  # Use all available techniques

    async def _apply_immersion_technique(
        self, scene: Scene, technique: ImmersionTechnique, session_state: SessionState
    ) -> Scene:
        """Apply a specific immersion technique to the scene."""
        if technique == ImmersionTechnique.SENSORY_DETAIL:
            return await self._apply_sensory_detail(scene)
        if technique == ImmersionTechnique.ENVIRONMENTAL_ATMOSPHERE:
            return await self._apply_environmental_atmosphere(scene)
        if technique == ImmersionTechnique.CHARACTER_PRESENCE:
            return await self._apply_character_presence(scene)
        if technique == ImmersionTechnique.EMOTIONAL_RESONANCE:
            return await self._apply_emotional_resonance(scene, session_state)
        if technique == ImmersionTechnique.INTERACTIVE_ELEMENTS:
            return await self._apply_interactive_elements(scene)
        if technique == ImmersionTechnique.CONTINUITY_WEAVING:
            return await self._apply_continuity_weaving(scene, session_state)
        if technique == ImmersionTechnique.PERSONAL_CONNECTION:
            return await self._apply_personal_connection(scene, session_state)
        return scene

    async def _apply_sensory_detail(self, scene: Scene) -> Scene:
        """Add rich sensory details to enhance immersion."""
        # Select sensory details appropriate for the scene
        visual_detail = self.sensory_libraries["visual"][0]
        auditory_detail = self.sensory_libraries["auditory"][0]
        tactile_detail = self.sensory_libraries["tactile"][0]

        sensory_enhancement = (
            f"As you take in your surroundings, you notice {visual_detail}. "
            f"You become aware of {auditory_detail}, while {tactile_detail}."
        )

        scene.narrative_content += f"\n\n{sensory_enhancement}"
        return scene

    async def _apply_environmental_atmosphere(self, scene: Scene) -> Scene:
        """Enhance environmental atmosphere for deeper immersion."""
        # Select appropriate atmosphere template
        atmosphere = self.atmosphere_templates["peaceful_sanctuary"]  # Default

        atmospheric_enhancement = (
            f"The atmosphere here is {atmosphere['mood']}, filled with {atmosphere['energy']}. "
            f"The {atmosphere['lighting']} creates a {atmosphere['space_quality']} feeling, "
            f"evoking a sense that is {atmosphere['emotional_tone']}."
        )

        scene.narrative_content += f"\n\n{atmospheric_enhancement}"
        return scene

    async def _apply_character_presence(self, scene: Scene) -> Scene:
        """Add character presence to enhance connection and guidance."""
        archetype = self.character_archetypes["wise_companion"]

        character_enhancement = (
            f"You sense a {archetype['presence']} presence nearby - not intrusive, but available. "
            f"This presence embodies {archetype['energy']}, offering {archetype['role']} "
            f"through {archetype['communication_style']}."
        )

        scene.narrative_content += f"\n\n{character_enhancement}"
        return scene

    async def _apply_emotional_resonance(self, scene: Scene, session_state: SessionState) -> Scene:
        """Enhance emotional resonance based on current emotional state."""
        emotional_state = session_state.emotional_state

        if emotional_state == EmotionalState.CALM:
            resonance = "This space seems to reflect and amplify your inner calm, creating a harmonious resonance between your peaceful state and the environment around you."
        elif emotional_state == EmotionalState.ANXIOUS:
            resonance = "The environment gently acknowledges any tension you might be carrying, offering a sense of understanding and gradual ease."
        elif emotional_state == EmotionalState.ENGAGED:
            resonance = "Your engagement with this experience is met by the environment's responsive energy, creating a dynamic interplay between your curiosity and the space's offerings."
        else:
            resonance = "The space around you seems to attune to your current state, offering exactly what you need in this moment."

        scene.narrative_content += f"\n\n{resonance}"
        return scene

    async def _apply_interactive_elements(self, scene: Scene) -> Scene:
        """Add interactive elements that invite engagement."""
        interactive_enhancement = (
            "This space invites your participation and engagement. You notice elements that seem to "
            "respond to your presence and attention, creating opportunities for meaningful interaction "
            "and discovery. Your choices here will shape your experience in meaningful ways."
        )

        scene.narrative_content += f"\n\n{interactive_enhancement}"
        return scene

    async def _apply_continuity_weaving(self, scene: Scene, session_state: SessionState) -> Scene:
        """Weave continuity elements from previous experiences."""
        if session_state.choice_history:
            continuity_enhancement = (
                "Elements from your previous experiences in this journey subtly weave into this moment, "
                "creating a sense of continuity and growth. You can feel how each step has led you here, "
                "building upon the insights and strengths you've already discovered."
            )

            scene.narrative_content += f"\n\n{continuity_enhancement}"

        return scene

    async def _apply_personal_connection(self, scene: Scene, session_state: SessionState) -> Scene:
        """Enhance personal connection and relevance."""
        therapeutic_goals = session_state.therapeutic_context.primary_goals

        if therapeutic_goals:
            primary_goal = therapeutic_goals[0]
            connection_enhancement = (
                f"This experience connects directly with your journey toward {primary_goal}, "
                f"offering you a personalized opportunity to explore and develop this aspect of yourself. "
                f"What unfolds here is uniquely meaningful for your individual path of growth."
            )
        else:
            connection_enhancement = (
                "This moment is uniquely yours, shaped by your individual journey and personal needs. "
                "The experience that unfolds here is tailored to support your specific path of growth and discovery."
            )

        scene.narrative_content += f"\n\n{connection_enhancement}"
        return scene

    async def _integrate_therapeutic_immersion(
        self, scene: Scene, session_state: SessionState
    ) -> Scene:
        """Ensure immersion enhancements support therapeutic goals."""
        # Add therapeutic integration that maintains immersion
        therapeutic_integration = (
            "As you become fully present in this experience, you notice how naturally it supports "
            "your wellbeing and growth. The immersive quality of this moment creates an ideal "
            "environment for therapeutic insight and positive change."
        )

        scene.narrative_content += f"\n\n{therapeutic_integration}"
        return scene

    # Assessment Methods
    async def _assess_sensory_richness(self, scene: Scene) -> float:
        """Assess the sensory richness of a scene (0.0-1.0)."""
        sensory_keywords = {
            "visual": ["see", "look", "light", "color", "shadow", "bright", "dim"],
            "auditory": ["hear", "sound", "listen", "quiet", "loud", "music", "voice"],
            "tactile": ["feel", "touch", "texture", "smooth", "rough", "warm", "cool"],
            "olfactory": ["smell", "scent", "fragrance", "aroma"],
            "kinesthetic": ["movement", "flow", "energy", "rhythm", "balance"],
        }

        content_lower = scene.narrative_content.lower()
        total_sensory_words = 0

        for keywords in sensory_keywords.values():
            sense_count = sum(1 for keyword in keywords if keyword in content_lower)
            total_sensory_words += sense_count

        # Normalize based on content length
        word_count = len(scene.narrative_content.split())
        if word_count == 0:
            return 0.0

        sensory_density = total_sensory_words / word_count
        return min(sensory_density * 5, 1.0)  # Scale up the density

    async def _assess_atmospheric_depth(self, scene: Scene) -> float:
        """Assess the atmospheric depth of a scene (0.0-1.0)."""
        atmospheric_keywords = [
            "atmosphere",
            "mood",
            "feeling",
            "energy",
            "presence",
            "quality",
            "ambiance",
            "environment",
            "space",
            "surroundings",
        ]

        content_lower = scene.narrative_content.lower()
        atmospheric_count = sum(1 for keyword in atmospheric_keywords if keyword in content_lower)

        # Also check for descriptive adjectives that create atmosphere
        descriptive_keywords = [
            "peaceful",
            "calming",
            "warm",
            "gentle",
            "serene",
            "vibrant",
            "mysterious",
            "welcoming",
            "sacred",
            "healing",
        ]

        descriptive_count = sum(1 for keyword in descriptive_keywords if keyword in content_lower)

        total_atmospheric = atmospheric_count + descriptive_count
        word_count = len(scene.narrative_content.split())

        if word_count == 0:
            return 0.0

        atmospheric_density = total_atmospheric / word_count
        return min(atmospheric_density * 8, 1.0)

    async def _assess_emotional_engagement(self, scene: Scene) -> float:
        """Assess the emotional engagement potential of a scene (0.0-1.0)."""
        emotional_keywords = [
            "feel",
            "emotion",
            "heart",
            "soul",
            "spirit",
            "connection",
            "resonate",
            "touch",
            "move",
            "inspire",
            "comfort",
            "support",
        ]

        content_lower = scene.narrative_content.lower()
        emotional_count = sum(1 for keyword in emotional_keywords if keyword in content_lower)

        # Check for emotional tone indicators
        tone_indicators = [
            "you feel",
            "you sense",
            "you experience",
            "you notice",
            "touches you",
            "moves you",
            "resonates with",
        ]

        tone_count = sum(1 for indicator in tone_indicators if indicator in content_lower)

        total_emotional = emotional_count + (tone_count * 2)  # Weight tone indicators more
        word_count = len(scene.narrative_content.split())

        if word_count == 0:
            return 0.0

        emotional_density = total_emotional / word_count
        return min(emotional_density * 6, 1.0)

    async def _assess_interactive_potential(self, scene: Scene) -> float:
        """Assess the interactive potential of a scene (0.0-1.0)."""
        interactive_keywords = [
            "choose",
            "decide",
            "explore",
            "discover",
            "interact",
            "engage",
            "participate",
            "respond",
            "action",
            "opportunity",
            "invitation",
        ]

        content_lower = scene.narrative_content.lower()
        interactive_count = sum(1 for keyword in interactive_keywords if keyword in content_lower)

        # Check for direct invitations to interact
        invitation_phrases = [
            "you can",
            "you might",
            "you may",
            "invites you",
            "offers you",
            "what will you",
            "how will you",
        ]

        invitation_count = sum(1 for phrase in invitation_phrases if phrase in content_lower)

        total_interactive = interactive_count + (invitation_count * 2)
        word_count = len(scene.narrative_content.split())

        if word_count == 0:
            return 0.0

        interactive_density = total_interactive / word_count
        return min(interactive_density * 7, 1.0)

    async def _assess_personal_relevance(self, scene: Scene) -> float:
        """Assess the personal relevance of a scene (0.0-1.0)."""
        personal_keywords = [
            "you",
            "your",
            "yourself",
            "personal",
            "individual",
            "unique",
            "journey",
            "path",
            "growth",
            "development",
            "learning",
        ]

        content_lower = scene.narrative_content.lower()
        personal_count = sum(1 for keyword in personal_keywords if keyword in content_lower)

        # Check for therapeutic relevance
        therapeutic_keywords = [
            "healing",
            "wellness",
            "wellbeing",
            "therapeutic",
            "support",
            "growth",
            "insight",
            "awareness",
            "understanding",
        ]

        therapeutic_count = sum(1 for keyword in therapeutic_keywords if keyword in content_lower)

        total_relevance = personal_count + therapeutic_count
        word_count = len(scene.narrative_content.split())

        if word_count == 0:
            return 0.0

        relevance_density = total_relevance / word_count
        return min(relevance_density * 4, 1.0)

    async def _assess_continuity_strength(self, scene: Scene) -> float:
        """Assess the continuity strength of a scene (0.0-1.0)."""
        continuity_keywords = [
            "previous",
            "before",
            "earlier",
            "journey",
            "path",
            "progress",
            "building",
            "continuing",
            "developing",
            "growing",
            "connecting",
        ]

        content_lower = scene.narrative_content.lower()
        continuity_count = sum(1 for keyword in continuity_keywords if keyword in content_lower)

        # Check for explicit continuity references
        continuity_phrases = [
            "from your",
            "building on",
            "continuing from",
            "as you've",
            "your journey",
            "your path",
            "your progress",
        ]

        phrase_count = sum(1 for phrase in continuity_phrases if phrase in content_lower)

        total_continuity = continuity_count + (phrase_count * 2)
        word_count = len(scene.narrative_content.split())

        if word_count == 0:
            return 0.0

        continuity_density = total_continuity / word_count
        return min(continuity_density * 8, 1.0)
