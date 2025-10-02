"""
Therapeutic Storyteller for Gameplay Loop

This module implements therapeutic storytelling functionality that weaves evidence-based
therapeutic interventions and concepts naturally into narrative content without breaking
immersion or feeling clinical.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from ..models.core import DifficultyLevel, EmotionalState, Scene, TherapeuticContext

logger = logging.getLogger(__name__)


class TherapeuticApproach(str, Enum):
    """Therapeutic approaches that can be integrated into storytelling."""

    CBT = "cognitive_behavioral_therapy"
    DBT = "dialectical_behavior_therapy"
    MINDFULNESS = "mindfulness_based_therapy"
    ACT = "acceptance_commitment_therapy"
    HUMANISTIC = "humanistic_therapy"
    NARRATIVE_THERAPY = "narrative_therapy"
    SOLUTION_FOCUSED = "solution_focused_therapy"


class StorytellingTechnique(str, Enum):
    """Storytelling techniques for therapeutic integration."""

    METAPHOR = "metaphor"
    SYMBOLISM = "symbolism"
    CHARACTER_MODELING = "character_modeling"
    EXPERIENTIAL_LEARNING = "experiential_learning"
    GUIDED_IMAGERY = "guided_imagery"
    REFLECTIVE_DIALOGUE = "reflective_dialogue"


class TherapeuticStoryteller:
    """
    Integrates therapeutic concepts and interventions into narrative content
    using storytelling techniques that maintain immersion and engagement.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # Therapeutic integration mappings
        self.approach_techniques: dict[
            TherapeuticApproach, list[StorytellingTechnique]
        ] = {}
        self.metaphor_library: dict[str, dict[str, Any]] = {}
        self.character_archetypes: dict[str, dict[str, Any]] = {}
        self.therapeutic_narratives: dict[str, dict[str, Any]] = {}

        logger.info("TherapeuticStoryteller initialized")

    async def initialize(self) -> bool:
        """Initialize therapeutic storytelling resources."""
        try:
            await self._load_therapeutic_approaches()
            await self._load_metaphor_library()
            await self._load_character_archetypes()
            await self._load_therapeutic_narratives()

            logger.info("TherapeuticStoryteller initialization completed")
            return True

        except Exception as e:
            logger.error(f"TherapeuticStoryteller initialization failed: {e}")
            return False

    async def enhance_scene_with_therapy(
        self, scene: Scene, therapeutic_context: TherapeuticContext
    ) -> Scene:
        """
        Enhance a scene with therapeutic elements while maintaining narrative flow.

        Args:
            scene: The scene to enhance
            therapeutic_context: Therapeutic goals and context

        Returns:
            Enhanced scene with integrated therapeutic elements
        """
        try:
            logger.info(f"Enhancing scene {scene.scene_id} with therapeutic elements")

            # Determine primary therapeutic approach
            primary_approach = await self._determine_therapeutic_approach(
                therapeutic_context
            )

            # Select appropriate storytelling techniques
            techniques = await self._select_storytelling_techniques(
                primary_approach, scene.scene_type, therapeutic_context.primary_goals
            )

            # Apply therapeutic enhancements
            enhanced_scene = Scene(**scene.model_dump())

            for technique in techniques:
                enhanced_scene = await self._apply_storytelling_technique(
                    enhanced_scene, technique, therapeutic_context, primary_approach
                )

            # Add therapeutic depth without being clinical
            enhanced_scene = await self._add_therapeutic_depth(
                enhanced_scene, therapeutic_context
            )

            logger.info(
                f"Enhanced scene with therapeutic elements using {primary_approach}"
            )
            return enhanced_scene

        except Exception as e:
            logger.error(f"Failed to enhance scene with therapy: {e}")
            return scene  # Return original scene if enhancement fails

    async def enhance_intervention_scene(
        self,
        scene: Scene,
        intervention_type: str,
        therapeutic_context: TherapeuticContext,
    ) -> Scene:
        """
        Enhance an intervention scene with specific therapeutic storytelling.

        Args:
            scene: The intervention scene to enhance
            intervention_type: Type of therapeutic intervention
            therapeutic_context: Therapeutic context and goals

        Returns:
            Enhanced intervention scene
        """
        try:
            logger.info(f"Enhancing intervention scene: {intervention_type}")

            # Get intervention-specific narrative enhancements
            enhancements = await self._get_intervention_enhancements(
                intervention_type, therapeutic_context
            )

            enhanced_scene = Scene(**scene.model_dump())

            # Apply intervention-specific storytelling
            enhanced_scene.narrative_content = await self._weave_intervention_narrative(
                enhanced_scene.narrative_content, enhancements
            )

            # Add therapeutic metaphors for the intervention
            metaphors = await self._select_intervention_metaphors(intervention_type)
            if metaphors:
                enhanced_scene.narrative_content += f"\n\n{metaphors}"

            # Enhance with character guidance if appropriate
            if intervention_type not in [
                "crisis_support"
            ]:  # Crisis support should be direct
                guidance = await self._add_therapeutic_guidance(intervention_type)
                if guidance:
                    enhanced_scene.narrative_content += f"\n\n{guidance}"

            logger.info(f"Enhanced intervention scene: {enhanced_scene.scene_id}")
            return enhanced_scene

        except Exception as e:
            logger.error(f"Failed to enhance intervention scene: {e}")
            return scene

    async def create_therapeutic_metaphor(
        self,
        concept: str,
        emotional_state: EmotionalState,
        difficulty_level: DifficultyLevel,
    ) -> str | None:
        """
        Create a therapeutic metaphor for a specific concept.

        Args:
            concept: The therapeutic concept to metaphorize
            emotional_state: Current emotional state for context
            difficulty_level: Complexity level for the metaphor

        Returns:
            Therapeutic metaphor or None if creation failed
        """
        try:
            # Get base metaphor for the concept
            base_metaphor = self.metaphor_library.get(concept)
            if not base_metaphor:
                return None

            # Adapt metaphor for emotional state and difficulty
            adapted_metaphor = await self._adapt_metaphor(
                base_metaphor, emotional_state, difficulty_level
            )

            return adapted_metaphor

        except Exception as e:
            logger.error(f"Failed to create therapeutic metaphor: {e}")
            return None

    # Initialization Methods
    async def _load_therapeutic_approaches(self) -> None:
        """Load therapeutic approaches and their associated storytelling techniques."""
        self.approach_techniques = {
            TherapeuticApproach.CBT: [
                StorytellingTechnique.REFLECTIVE_DIALOGUE,
                StorytellingTechnique.CHARACTER_MODELING,
                StorytellingTechnique.EXPERIENTIAL_LEARNING,
            ],
            TherapeuticApproach.DBT: [
                StorytellingTechnique.METAPHOR,
                StorytellingTechnique.EXPERIENTIAL_LEARNING,
                StorytellingTechnique.GUIDED_IMAGERY,
            ],
            TherapeuticApproach.MINDFULNESS: [
                StorytellingTechnique.GUIDED_IMAGERY,
                StorytellingTechnique.SYMBOLISM,
                StorytellingTechnique.EXPERIENTIAL_LEARNING,
            ],
            TherapeuticApproach.ACT: [
                StorytellingTechnique.METAPHOR,
                StorytellingTechnique.SYMBOLISM,
                StorytellingTechnique.REFLECTIVE_DIALOGUE,
            ],
            TherapeuticApproach.HUMANISTIC: [
                StorytellingTechnique.CHARACTER_MODELING,
                StorytellingTechnique.REFLECTIVE_DIALOGUE,
                StorytellingTechnique.EXPERIENTIAL_LEARNING,
            ],
            TherapeuticApproach.NARRATIVE_THERAPY: [
                StorytellingTechnique.METAPHOR,
                StorytellingTechnique.SYMBOLISM,
                StorytellingTechnique.CHARACTER_MODELING,
            ],
        }

    async def _load_metaphor_library(self) -> None:
        """Load therapeutic metaphors for different concepts."""
        self.metaphor_library = {
            "emotional_regulation": {
                "base": "Like a skilled sailor learning to navigate changing weather, you're developing the ability to work with your emotions rather than being overwhelmed by them.",
                "gentle": "Your emotions are like clouds in the sky - they come and go, but the sky itself remains vast and peaceful.",
                "standard": "Think of your emotions as waves in the ocean. You can learn to surf them skillfully rather than being pulled under.",
                "challenging": "You are becoming the captain of your emotional ship, learning to navigate through storms with wisdom and skill.",
            },
            "mindfulness": {
                "base": "Like a gardener tending to their garden, mindfulness is about paying gentle attention to the present moment.",
                "gentle": "Mindfulness is like sitting by a peaceful stream, simply watching the water flow without needing to change its course.",
                "standard": "Your awareness is like a lighthouse beam, illuminating whatever it touches with clarity and presence.",
                "challenging": "Mindfulness is the art of being fully present, like a master craftsperson completely absorbed in their work.",
            },
            "resilience": {
                "base": "Like a tree that bends in the wind but doesn't break, resilience is your ability to adapt and grow through challenges.",
                "gentle": "You have an inner strength like a seed that can grow through concrete, finding a way to flourish.",
                "standard": "Resilience is like a muscle that grows stronger with use, helping you bounce back from life's challenges.",
                "challenging": "You are forging your resilience like a blacksmith shapes metal - through heat and pressure, creating something strong and beautiful.",
            },
            "self_compassion": {
                "base": "Self-compassion is like being a good friend to yourself, offering the same kindness you'd give to someone you care about.",
                "gentle": "Treat yourself with the same gentle care you'd give to a beloved pet or small child.",
                "standard": "Self-compassion is like having an inner ally who always has your back, even when things get tough.",
                "challenging": "You are learning to be both the wounded healer and the wise counselor within yourself.",
            },
        }

    async def _load_character_archetypes(self) -> None:
        """Load therapeutic character archetypes for storytelling."""
        self.character_archetypes = {
            "wise_guide": {
                "description": "A gentle, wise character who offers guidance without being directive",
                "therapeutic_role": "modeling wisdom and self-compassion",
                "dialogue_style": "questioning, reflective, supportive",
            },
            "fellow_traveler": {
                "description": "A character on their own journey who shares experiences and insights",
                "therapeutic_role": "normalizing struggles and modeling growth",
                "dialogue_style": "sharing, empathetic, encouraging",
            },
            "inner_voice": {
                "description": "Represents the player's own inner wisdom and strength",
                "therapeutic_role": "helping access internal resources",
                "dialogue_style": "gentle, knowing, empowering",
            },
        }

    async def _load_therapeutic_narratives(self) -> None:
        """Load narrative patterns for different therapeutic goals."""
        self.therapeutic_narratives = {
            "anxiety_management": {
                "pattern": "journey_to_calm",
                "elements": [
                    "safe_spaces",
                    "breathing_practices",
                    "grounding_techniques",
                ],
                "progression": "overwhelm -> tools -> practice -> mastery",
            },
            "depression_support": {
                "pattern": "rekindling_light",
                "elements": ["small_steps", "connection", "meaning_making"],
                "progression": "darkness -> spark -> nurturing -> growth",
            },
            "trauma_healing": {
                "pattern": "reclaiming_power",
                "elements": ["safety_first", "choice", "integration"],
                "progression": "fragmentation -> safety -> integration -> wholeness",
            },
        }

    # Core Enhancement Methods
    async def _determine_therapeutic_approach(
        self, therapeutic_context: TherapeuticContext
    ) -> TherapeuticApproach:
        """Determine the primary therapeutic approach based on context."""
        primary_goals = therapeutic_context.primary_goals

        # Map goals to approaches
        if (
            "mindfulness" in primary_goals
            or "present_moment_awareness" in primary_goals
        ):
            return TherapeuticApproach.MINDFULNESS
        elif (
            "cognitive_reframing" in primary_goals
            or "thought_patterns" in primary_goals
        ):
            return TherapeuticApproach.CBT
        elif (
            "emotional_regulation" in primary_goals
            or "distress_tolerance" in primary_goals
        ):
            return TherapeuticApproach.DBT
        elif "values" in primary_goals or "acceptance" in primary_goals:
            return TherapeuticApproach.ACT
        elif "self_compassion" in primary_goals or "personal_growth" in primary_goals:
            return TherapeuticApproach.HUMANISTIC
        else:
            return TherapeuticApproach.CBT  # Default approach

    async def _select_storytelling_techniques(
        self, approach: TherapeuticApproach, scene_type: str, goals: list[str]
    ) -> list[StorytellingTechnique]:
        """Select appropriate storytelling techniques for the therapeutic approach."""
        available_techniques = self.approach_techniques.get(approach, [])

        # Select techniques based on scene type and goals
        selected = []

        if scene_type == "introduction":
            selected.append(StorytellingTechnique.CHARACTER_MODELING)
        elif scene_type == "therapeutic":
            selected.extend(
                [StorytellingTechnique.METAPHOR, StorytellingTechnique.GUIDED_IMAGERY]
            )
        elif scene_type == "challenge":
            selected.append(StorytellingTechnique.EXPERIENTIAL_LEARNING)
        else:
            selected.append(StorytellingTechnique.REFLECTIVE_DIALOGUE)

        # Ensure selected techniques are available for the approach
        return [tech for tech in selected if tech in available_techniques][
            :2
        ]  # Limit to 2

    async def _apply_storytelling_technique(
        self,
        scene: Scene,
        technique: StorytellingTechnique,
        therapeutic_context: TherapeuticContext,
        approach: TherapeuticApproach,
    ) -> Scene:
        """Apply a specific storytelling technique to enhance the scene."""
        if technique == StorytellingTechnique.METAPHOR:
            return await self._apply_metaphor_technique(scene, therapeutic_context)
        elif technique == StorytellingTechnique.CHARACTER_MODELING:
            return await self._apply_character_modeling(scene, therapeutic_context)
        elif technique == StorytellingTechnique.GUIDED_IMAGERY:
            return await self._apply_guided_imagery(scene, therapeutic_context)
        elif technique == StorytellingTechnique.REFLECTIVE_DIALOGUE:
            return await self._apply_reflective_dialogue(scene, therapeutic_context)
        elif technique == StorytellingTechnique.EXPERIENTIAL_LEARNING:
            return await self._apply_experiential_learning(scene, therapeutic_context)
        else:
            return scene

    async def _apply_metaphor_technique(
        self, scene: Scene, therapeutic_context: TherapeuticContext
    ) -> Scene:
        """Apply therapeutic metaphors to the scene."""
        primary_goal = (
            therapeutic_context.primary_goals[0]
            if therapeutic_context.primary_goals
            else "mindfulness"
        )

        metaphor = await self.create_therapeutic_metaphor(
            primary_goal, EmotionalState.CALM, scene.difficulty_level
        )

        if metaphor:
            scene.narrative_content += f"\n\n{metaphor}"

        return scene

    async def _apply_character_modeling(
        self, scene: Scene, therapeutic_context: TherapeuticContext
    ) -> Scene:
        """Add therapeutic character modeling to the scene."""
        archetype = self.character_archetypes["wise_guide"]

        modeling_content = (
            f"A {archetype['description']} appears in the scene, demonstrating "
            f"{archetype['therapeutic_role']} through their presence and actions."
        )

        scene.narrative_content += f"\n\n{modeling_content}"
        return scene

    async def _apply_guided_imagery(
        self, scene: Scene, therapeutic_context: TherapeuticContext
    ) -> Scene:
        """Add guided imagery elements to the scene."""
        imagery_content = (
            "Take a moment to fully immerse yourself in this experience. "
            "Notice the details around you - the colors, textures, sounds, and sensations. "
            "Allow yourself to be fully present in this safe and supportive space."
        )

        scene.narrative_content += f"\n\n{imagery_content}"
        return scene

    async def _apply_reflective_dialogue(
        self, scene: Scene, therapeutic_context: TherapeuticContext
    ) -> Scene:
        """Add reflective dialogue elements to the scene."""
        dialogue_content = (
            "A gentle voice within you asks: 'What are you noticing about this experience? "
            "What feels important or meaningful to you right now?' "
            "There's no need to answer immediately - simply let the questions settle."
        )

        scene.narrative_content += f"\n\n{dialogue_content}"
        return scene

    async def _apply_experiential_learning(
        self, scene: Scene, therapeutic_context: TherapeuticContext
    ) -> Scene:
        """Add experiential learning elements to the scene."""
        learning_content = (
            "This space invites you to learn through direct experience. "
            "Each choice you make here is an opportunity to discover something new about yourself "
            "and to practice skills that can serve you well beyond this moment."
        )

        scene.narrative_content += f"\n\n{learning_content}"
        return scene

    async def _add_therapeutic_depth(
        self, scene: Scene, therapeutic_context: TherapeuticContext
    ) -> Scene:
        """Add therapeutic depth without being clinical."""
        # Add subtle therapeutic elements based on context
        if "anxiety" in therapeutic_context.primary_goals:
            depth_content = "There's something deeply calming about this space that helps quiet the mind's chatter."
        elif "depression" in therapeutic_context.primary_goals:
            depth_content = "A gentle warmth fills this space, reminding you of your inherent worth and potential."
        elif "trauma" in therapeutic_context.primary_goals:
            depth_content = "This space holds you with complete safety, honoring your strength and resilience."
        else:
            depth_content = "This environment supports your natural capacity for growth and healing."

        scene.narrative_content += f"\n\n{depth_content}"
        return scene

    async def _get_intervention_enhancements(
        self, intervention_type: str, therapeutic_context: TherapeuticContext
    ) -> dict[str, Any]:
        """Get narrative enhancements for specific interventions."""
        enhancements = {
            "mindfulness": {
                "narrative_elements": [
                    "present_moment",
                    "gentle_awareness",
                    "non_judgment",
                ],
                "sensory_focus": [
                    "breathing",
                    "body_sensations",
                    "environmental_sounds",
                ],
                "guidance_style": "gentle_invitation",
            },
            "grounding": {
                "narrative_elements": [
                    "physical_connection",
                    "sensory_awareness",
                    "stability",
                ],
                "sensory_focus": ["touch", "sight", "sound", "physical_presence"],
                "guidance_style": "structured_practice",
            },
            "crisis_support": {
                "narrative_elements": ["safety", "support", "connection", "hope"],
                "sensory_focus": ["warmth", "protection", "comfort"],
                "guidance_style": "direct_support",
            },
            "breathing": {
                "narrative_elements": ["rhythm", "flow", "release", "renewal"],
                "sensory_focus": ["breath_movement", "chest_expansion", "air_quality"],
                "guidance_style": "rhythmic_guidance",
            },
            "emotional_regulation": {
                "narrative_elements": [
                    "acceptance",
                    "observation",
                    "choice",
                    "balance",
                ],
                "sensory_focus": [
                    "emotional_sensations",
                    "body_awareness",
                    "energy_flow",
                ],
                "guidance_style": "exploratory_support",
            },
        }

        return enhancements.get(intervention_type, enhancements["mindfulness"])

    async def _weave_intervention_narrative(
        self, base_content: str, enhancements: dict[str, Any]
    ) -> str:
        """Weave intervention-specific narrative enhancements into base content."""
        # Add narrative elements naturally
        elements = enhancements["narrative_elements"]
        guidance_style = enhancements["guidance_style"]

        if guidance_style == "gentle_invitation":
            addition = f"This space gently invites you to explore {', '.join(elements[:2])} at your own pace."
        elif guidance_style == "structured_practice":
            addition = f"Here, you can practice {elements[0]} through {elements[1]} in a structured, supportive way."
        elif guidance_style == "direct_support":
            addition = f"You are surrounded by {', '.join(elements)} in this completely safe environment."
        else:
            addition = f"This experience offers you {', '.join(elements[:2])} through gentle practice."

        return f"{base_content}\n\n{addition}"

    async def _select_intervention_metaphors(
        self, intervention_type: str
    ) -> str | None:
        """Select appropriate metaphors for intervention types."""
        metaphors = {
            "mindfulness": "Like a gentle observer watching clouds pass through the sky, you can observe your thoughts and feelings with peaceful awareness.",
            "grounding": "Like a tree with deep roots, you can find stability and strength by connecting with the solid ground beneath you.",
            "breathing": "Like the ocean's natural rhythm, your breath flows in and out, bringing calm and renewal with each cycle.",
            "emotional_regulation": "Like a skilled gardener tending to their plants, you can learn to care for your emotions with patience and wisdom.",
            "crisis_support": None,  # No metaphors for crisis - direct support is better
        }

        return metaphors.get(intervention_type)

    async def _add_therapeutic_guidance(self, intervention_type: str) -> str | None:
        """Add therapeutic guidance appropriate for the intervention."""
        guidance = {
            "mindfulness": "A wise inner voice reminds you: 'There's no right or wrong way to do this. Simply be present with whatever arises.'",
            "grounding": "You hear gentle encouragement: 'Take your time. Notice what helps you feel most grounded and centered.'",
            "breathing": "A calming presence suggests: 'Let your breath find its natural rhythm. Trust your body's wisdom.'",
            "emotional_regulation": "An understanding voice offers: 'All emotions are welcome here. You can observe them with curiosity and kindness.'",
        }

        return guidance.get(intervention_type)

    async def _adapt_metaphor(
        self,
        base_metaphor: dict[str, str],
        emotional_state: EmotionalState,
        difficulty_level: DifficultyLevel,
    ) -> str:
        """Adapt a metaphor based on emotional state and difficulty level."""
        # Select appropriate complexity level
        if difficulty_level == DifficultyLevel.GENTLE:
            metaphor_key = "gentle"
        elif difficulty_level == DifficultyLevel.CHALLENGING:
            metaphor_key = "challenging"
        else:
            metaphor_key = "standard"

        # Get base metaphor
        metaphor = base_metaphor.get(metaphor_key, base_metaphor.get("base", ""))

        # Adapt for emotional state
        if emotional_state in [EmotionalState.ANXIOUS, EmotionalState.OVERWHELMED]:
            # Make more calming and reassuring
            metaphor = metaphor.replace("learning to", "gently learning to")
            metaphor = metaphor.replace("developing", "slowly developing")
        elif emotional_state == EmotionalState.DISTRESSED:
            # Make more supportive and hopeful
            metaphor = f"Even in difficult times, {metaphor.lower()}"

        return metaphor
