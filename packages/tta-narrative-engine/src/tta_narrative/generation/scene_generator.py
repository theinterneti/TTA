"""

# Logseq: [[TTA.dev/Packages/Tta-narrative-engine/Src/Tta_narrative/Generation/Scene_generator]]
Scene Generator for Therapeutic Text Adventure

This module implements scene generation functionality for creating immersive,
therapeutically-focused narrative scenes within the gameplay loop system.
"""

from __future__ import annotations

import logging
from typing import Any

from ..models.core import DifficultyLevel, Scene, SceneType, TherapeuticContext

logger = logging.getLogger(__name__)


class SceneTemplate:
    """Template for generating therapeutic scenes."""

    def __init__(self, scene_type: SceneType, template_data: dict[str, Any]):
        self.scene_type = scene_type
        self.template_data = template_data
        self.therapeutic_elements = template_data.get("therapeutic_elements", [])
        self.narrative_patterns = template_data.get("narrative_patterns", [])
        self.setting_options = template_data.get("settings", [])


class SceneGenerator:
    """
    Generates therapeutic narrative scenes with appropriate content,
    therapeutic elements, and immersive storytelling.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.scene_templates: dict[SceneType, list[SceneTemplate]] = {}
        self.therapeutic_settings = {}
        self.narrative_patterns = {}

        logger.info("SceneGenerator initialized")

    async def initialize(self) -> bool:
        """Initialize scene templates and therapeutic content."""
        try:
            await self._load_scene_templates()
            await self._load_therapeutic_settings()
            await self._load_narrative_patterns()

            logger.info("SceneGenerator initialization completed")
            return True

        except Exception as e:
            logger.error(f"SceneGenerator initialization failed: {e}")
            return False

    async def generate_therapeutic_scene(
        self,
        scene_type: SceneType,
        therapeutic_focus: list[str],
        emotional_tone: str = "neutral",
        difficulty_level: DifficultyLevel = DifficultyLevel.STANDARD,
        **kwargs,
    ) -> Scene | None:
        """
        Generate a therapeutic scene with specified parameters.

        Args:
            scene_type: Type of scene to generate
            therapeutic_focus: List of therapeutic goals/focuses
            emotional_tone: Desired emotional tone
            difficulty_level: Complexity level for the scene
            **kwargs: Additional scene parameters

        Returns:
            Generated Scene object or None if generation failed
        """
        try:
            logger.info(f"Generating {scene_type} scene with focus: {therapeutic_focus}")

            # Select appropriate template
            template = await self._select_scene_template(scene_type, therapeutic_focus)
            if not template:
                logger.warning(f"No template found for {scene_type} with focus {therapeutic_focus}")
                return None

            # Generate scene content
            scene_content = await self._generate_scene_content(
                template, therapeutic_focus, emotional_tone, **kwargs
            )

            # Create scene object
            scene = Scene(
                title=scene_content["title"],
                description=scene_content["description"],
                narrative_content=scene_content["narrative_content"],
                scene_type=scene_type,
                difficulty_level=difficulty_level,
                therapeutic_focus=therapeutic_focus,
                learning_objectives=scene_content.get("learning_objectives", []),
                emotional_tone=emotional_tone,
                estimated_duration=scene_content.get("estimated_duration", 300),
            )

            logger.info(f"Generated scene: {scene.scene_id}")
            return scene

        except Exception as e:
            logger.error(f"Failed to generate therapeutic scene: {e}")
            return None

    async def generate_intervention_scene(
        self,
        intervention_type: str,
        emotional_state: str,
        therapeutic_context: TherapeuticContext,
        difficulty_level: DifficultyLevel,
    ) -> Scene | None:
        """
        Generate a scene specifically for therapeutic intervention.

        Args:
            intervention_type: Type of intervention (mindfulness, grounding, etc.)
            emotional_state: Current emotional state
            therapeutic_context: Therapeutic context and goals
            difficulty_level: Complexity level

        Returns:
            Generated intervention scene or None if generation failed
        """
        try:
            logger.info(f"Generating intervention scene: {intervention_type}")

            # Get intervention-specific content
            intervention_content = await self._generate_intervention_content(
                intervention_type, emotional_state, therapeutic_context
            )

            # Create intervention scene
            scene = Scene(
                title=intervention_content["title"],
                description=intervention_content["description"],
                narrative_content=intervention_content["narrative_content"],
                scene_type=SceneType.THERAPEUTIC,
                difficulty_level=DifficultyLevel.GENTLE,  # Always gentle for interventions
                therapeutic_focus=[intervention_type, "safety", "support"],
                learning_objectives=intervention_content.get("learning_objectives", []),
                emotional_tone="supportive",
                estimated_duration=intervention_content.get(
                    "duration", 600
                ),  # Longer for interventions
            )

            logger.info(f"Generated intervention scene: {scene.scene_id}")
            return scene

        except Exception as e:
            logger.error(f"Failed to generate intervention scene: {e}")
            return None

    # Template and Content Management
    async def _load_scene_templates(self) -> None:
        """Load scene templates for different scene types."""
        # Introduction scene templates
        intro_templates = [
            SceneTemplate(
                SceneType.INTRODUCTION,
                {
                    "therapeutic_elements": [
                        "safety_establishment",
                        "rapport_building",
                    ],
                    "settings": ["peaceful_garden", "cozy_library", "quiet_beach"],
                    "narrative_patterns": [
                        "welcoming_guide",
                        "safe_exploration",
                        "gentle_introduction",
                    ],
                },
            ),
            SceneTemplate(
                SceneType.INTRODUCTION,
                {
                    "therapeutic_elements": ["grounding", "present_moment_awareness"],
                    "settings": [
                        "mountain_meadow",
                        "forest_clearing",
                        "riverside_sanctuary",
                    ],
                    "narrative_patterns": [
                        "nature_connection",
                        "mindful_arrival",
                        "sensory_grounding",
                    ],
                },
            ),
        ]

        # Exploration scene templates
        exploration_templates = [
            SceneTemplate(
                SceneType.EXPLORATION,
                {
                    "therapeutic_elements": [
                        "curiosity",
                        "self_discovery",
                        "gentle_challenge",
                    ],
                    "settings": ["ancient_library", "art_gallery", "botanical_garden"],
                    "narrative_patterns": [
                        "discovery_journey",
                        "meaningful_choices",
                        "personal_reflection",
                    ],
                },
            ),
            SceneTemplate(
                SceneType.EXPLORATION,
                {
                    "therapeutic_elements": ["social_connection", "empathy_building"],
                    "settings": [
                        "village_square",
                        "community_center",
                        "shared_workspace",
                    ],
                    "narrative_patterns": [
                        "character_interaction",
                        "helping_others",
                        "community_engagement",
                    ],
                },
            ),
        ]

        # Therapeutic scene templates
        therapeutic_templates = [
            SceneTemplate(
                SceneType.THERAPEUTIC,
                {
                    "therapeutic_elements": [
                        "mindfulness",
                        "emotional_regulation",
                        "coping_skills",
                    ],
                    "settings": ["meditation_space", "healing_garden", "therapy_room"],
                    "narrative_patterns": [
                        "guided_practice",
                        "skill_learning",
                        "therapeutic_dialogue",
                    ],
                },
            ),
            SceneTemplate(
                SceneType.THERAPEUTIC,
                {
                    "therapeutic_elements": [
                        "cognitive_reframing",
                        "perspective_taking",
                    ],
                    "settings": [
                        "reflection_chamber",
                        "wisdom_tree",
                        "insight_pavilion",
                    ],
                    "narrative_patterns": [
                        "thought_exploration",
                        "perspective_shift",
                        "wisdom_sharing",
                    ],
                },
            ),
        ]

        # Challenge scene templates
        challenge_templates = [
            SceneTemplate(
                SceneType.CHALLENGE,
                {
                    "therapeutic_elements": [
                        "resilience_building",
                        "problem_solving",
                        "confidence",
                    ],
                    "settings": ["puzzle_chamber", "skill_arena", "growth_garden"],
                    "narrative_patterns": [
                        "manageable_challenge",
                        "skill_application",
                        "success_building",
                    ],
                },
            )
        ]

        # Reflection scene templates
        reflection_templates = [
            SceneTemplate(
                SceneType.REFLECTION,
                {
                    "therapeutic_elements": [
                        "self_awareness",
                        "insight_integration",
                        "meaning_making",
                    ],
                    "settings": ["quiet_study", "reflection_pool", "journal_nook"],
                    "narrative_patterns": [
                        "thoughtful_review",
                        "insight_discovery",
                        "learning_integration",
                    ],
                },
            )
        ]

        # Resolution scene templates
        resolution_templates = [
            SceneTemplate(
                SceneType.RESOLUTION,
                {
                    "therapeutic_elements": [
                        "closure",
                        "celebration",
                        "future_planning",
                    ],
                    "settings": [
                        "achievement_hall",
                        "celebration_space",
                        "planning_room",
                    ],
                    "narrative_patterns": [
                        "accomplishment_recognition",
                        "future_visioning",
                        "positive_closure",
                    ],
                },
            )
        ]

        # Store templates
        self.scene_templates = {
            SceneType.INTRODUCTION: intro_templates,
            SceneType.EXPLORATION: exploration_templates,
            SceneType.THERAPEUTIC: therapeutic_templates,
            SceneType.CHALLENGE: challenge_templates,
            SceneType.REFLECTION: reflection_templates,
            SceneType.RESOLUTION: resolution_templates,
        }

    async def _load_therapeutic_settings(self) -> None:
        """Load therapeutic setting descriptions and atmospheres."""
        self.therapeutic_settings = {
            "peaceful_garden": {
                "description": "A serene garden with gentle pathways, blooming flowers, and the soft sound of flowing water",
                "atmosphere": "peaceful, safe, nurturing",
                "therapeutic_benefits": [
                    "grounding",
                    "stress_relief",
                    "connection_with_nature",
                ],
            },
            "cozy_library": {
                "description": "A warm, inviting library with comfortable reading nooks, soft lighting, and the gentle scent of books",
                "atmosphere": "contemplative, secure, intellectually stimulating",
                "therapeutic_benefits": [
                    "reflection",
                    "learning",
                    "quiet_contemplation",
                ],
            },
            "quiet_beach": {
                "description": "A tranquil beach with gentle waves, warm sand, and a horizon that stretches endlessly",
                "atmosphere": "expansive, calming, rhythmic",
                "therapeutic_benefits": [
                    "mindfulness",
                    "emotional_regulation",
                    "perspective",
                ],
            },
            "meditation_space": {
                "description": "A dedicated space for inner work, with soft cushions, gentle lighting, and an atmosphere of deep peace",
                "atmosphere": "centered, focused, spiritually nurturing",
                "therapeutic_benefits": [
                    "mindfulness",
                    "self_awareness",
                    "emotional_balance",
                ],
            },
            "healing_garden": {
                "description": "A therapeutic garden designed for healing, with medicinal plants, comfortable seating, and healing energy",
                "atmosphere": "restorative, hopeful, growth-oriented",
                "therapeutic_benefits": ["healing", "growth", "renewal"],
            },
        }

    async def _load_narrative_patterns(self) -> None:
        """Load narrative patterns for different therapeutic approaches."""
        self.narrative_patterns = {
            "welcoming_guide": {
                "opening": "A gentle presence welcomes you to this safe space, inviting you to explore at your own pace.",
                "development": "Your guide offers support and encouragement as you navigate this new environment.",
                "therapeutic_integration": "Through gentle guidance, you discover your own inner wisdom and strength.",
            },
            "discovery_journey": {
                "opening": "Before you lies a path of discovery, filled with opportunities for growth and learning.",
                "development": "Each step reveals new insights about yourself and your capabilities.",
                "therapeutic_integration": "Your journey becomes a metaphor for personal growth and self-discovery.",
            },
            "guided_practice": {
                "opening": "You are invited to engage in a practice that can support your wellbeing and growth.",
                "development": "Step by step, you learn and apply new skills in a supportive environment.",
                "therapeutic_integration": "The practice becomes a tool you can use in your daily life for continued growth.",
            },
        }

    async def _select_scene_template(
        self, scene_type: SceneType, therapeutic_focus: list[str]
    ) -> SceneTemplate | None:
        """Select the most appropriate template for the scene."""
        templates = self.scene_templates.get(scene_type, [])
        if not templates:
            return None

        # Score templates based on therapeutic focus alignment
        best_template = None
        best_score = 0

        for template in templates:
            score = 0
            template_elements = template.therapeutic_elements

            # Calculate alignment score
            for focus in therapeutic_focus:
                if focus in template_elements:
                    score += 2
                elif any(focus in element for element in template_elements):
                    score += 1

            if score > best_score:
                best_score = score
                best_template = template

        return best_template or templates[0]  # Return first template if no good match

    async def _generate_scene_content(
        self,
        template: SceneTemplate,
        therapeutic_focus: list[str],
        emotional_tone: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate scene content based on template and parameters."""
        # Select setting
        setting_key = kwargs.get(
            "setting",
            (template.setting_options[0] if template.setting_options else "peaceful_garden"),
        )
        setting = self.therapeutic_settings.get(
            setting_key, self.therapeutic_settings["peaceful_garden"]
        )

        # Select narrative pattern
        pattern_key = (
            template.narrative_patterns[0] if template.narrative_patterns else "welcoming_guide"
        )
        pattern = self.narrative_patterns.get(
            pattern_key, self.narrative_patterns["welcoming_guide"]
        )

        # Generate title
        title = await self._generate_scene_title(
            template.scene_type, setting_key, therapeutic_focus
        )

        # Generate description
        description = setting["description"]

        # Generate narrative content
        narrative_content = await self._generate_narrative_content(
            pattern, setting, therapeutic_focus, emotional_tone, **kwargs
        )

        # Generate learning objectives
        learning_objectives = await self._generate_learning_objectives(
            therapeutic_focus, template.scene_type
        )

        return {
            "title": title,
            "description": description,
            "narrative_content": narrative_content,
            "learning_objectives": learning_objectives,
            "estimated_duration": kwargs.get("estimated_duration", 300),
        }

    async def _generate_scene_title(
        self, scene_type: SceneType, setting_key: str, therapeutic_focus: list[str]
    ) -> str:
        """Generate an appropriate title for the scene."""
        setting_names = {
            "peaceful_garden": "Peaceful Garden",
            "cozy_library": "Quiet Library",
            "quiet_beach": "Tranquil Shore",
            "meditation_space": "Meditation Sanctuary",
            "healing_garden": "Healing Garden",
            "mountain_meadow": "Mountain Meadow",
            "forest_clearing": "Forest Clearing",
            "riverside_sanctuary": "Riverside Sanctuary",
        }

        base_name = setting_names.get(setting_key, "Safe Space")

        # Add therapeutic context to title
        if "mindfulness" in therapeutic_focus:
            return f"Mindful Moments in the {base_name}"
        if "grounding" in therapeutic_focus:
            return f"Grounding in the {base_name}"
        if "reflection" in therapeutic_focus:
            return f"Reflection at the {base_name}"
        if scene_type == SceneType.INTRODUCTION:
            return f"Welcome to the {base_name}"
        if scene_type == SceneType.THERAPEUTIC:
            return f"Healing in the {base_name}"
        return base_name

    async def _generate_narrative_content(
        self,
        pattern: dict[str, str],
        setting: dict[str, Any],
        therapeutic_focus: list[str],
        emotional_tone: str,
        **kwargs,
    ) -> str:
        """Generate the main narrative content for the scene."""
        # Start with pattern opening
        content_parts = [pattern["opening"]]

        # Add setting description
        content_parts.append(setting["description"] + ".")

        # Add therapeutic elements based on focus
        therapeutic_content = await self._generate_therapeutic_content(
            therapeutic_focus, emotional_tone
        )
        if therapeutic_content:
            content_parts.append(therapeutic_content)

        # Add pattern development
        content_parts.append(pattern["development"])

        # Add emotional tone adjustments
        tone_content = await self._generate_tone_content(emotional_tone)
        if tone_content:
            content_parts.append(tone_content)

        # Add therapeutic integration
        content_parts.append(pattern["therapeutic_integration"])

        return " ".join(content_parts)

    async def _generate_therapeutic_content(
        self, therapeutic_focus: list[str], emotional_tone: str
    ) -> str:
        """Generate therapeutic content based on focus areas."""
        therapeutic_elements = []

        for focus in therapeutic_focus:
            if focus == "mindfulness":
                therapeutic_elements.append(
                    "Take a moment to notice your breathing, the sensations in your body, and the present moment."
                )
            elif focus == "grounding":
                therapeutic_elements.append(
                    "Feel your connection to this safe space, noticing the solid ground beneath you and the stability it provides."
                )
            elif focus == "emotional_regulation":
                therapeutic_elements.append(
                    "This space offers you the opportunity to observe your emotions with kindness and understanding."
                )
            elif focus == "self_awareness":
                therapeutic_elements.append(
                    "Here, you can explore your thoughts and feelings in a safe, non-judgmental environment."
                )
            elif focus == "stress_relief":
                therapeutic_elements.append(
                    "Allow the peaceful atmosphere to help release any tension or stress you may be carrying."
                )

        return " ".join(therapeutic_elements[:2])  # Limit to avoid overwhelming

    async def _generate_tone_content(self, emotional_tone: str) -> str:
        """Generate content that reinforces the desired emotional tone."""
        tone_content = {
            "welcoming": "You feel welcomed and accepted in this space, free to be yourself.",
            "calming": "A sense of deep calm settles over you as you take in your surroundings.",
            "encouraging": "There's an energy of possibility and growth in the air around you.",
            "supportive": "You sense that this is a place where you are truly supported and understood.",
            "hopeful": "A gentle sense of hope and possibility fills the atmosphere.",
            "grounding": "You feel more centered and grounded with each moment you spend here.",
            "deeply_calming": "Profound peace washes over you, bringing deep relaxation to your mind and body.",
            "deeply_supportive": "You are surrounded by an atmosphere of unconditional support and care.",
        }

        return tone_content.get(emotional_tone, "")

    async def _generate_learning_objectives(
        self, therapeutic_focus: list[str], scene_type: SceneType
    ) -> list[str]:
        """Generate learning objectives based on therapeutic focus and scene type."""
        objectives = []

        for focus in therapeutic_focus:
            if focus == "mindfulness":
                objectives.append("Practice present-moment awareness")
            elif focus == "grounding":
                objectives.append("Develop grounding techniques")
            elif focus == "emotional_regulation":
                objectives.append("Learn to observe emotions without judgment")
            elif focus == "self_awareness":
                objectives.append("Increase self-understanding")
            elif focus == "stress_relief":
                objectives.append("Experience stress reduction techniques")

        # Add scene-type specific objectives
        if scene_type == SceneType.INTRODUCTION:
            objectives.append("Establish safety and comfort")
        elif scene_type == SceneType.THERAPEUTIC:
            objectives.append("Apply therapeutic skills")
        elif scene_type == SceneType.CHALLENGE:
            objectives.append("Build confidence and resilience")

        return objectives[:3]  # Limit to 3 objectives

    async def _generate_intervention_content(
        self,
        intervention_type: str,
        emotional_state: str,
        therapeutic_context: TherapeuticContext,
    ) -> dict[str, Any]:
        """Generate content for therapeutic intervention scenes."""
        intervention_content = {
            "mindfulness": {
                "title": "Mindful Breathing Space",
                "description": "A dedicated space for mindfulness practice and present-moment awareness",
                "narrative_content": (
                    "You find yourself in a peaceful space designed for mindfulness practice. "
                    "The atmosphere invites you to slow down and connect with the present moment. "
                    "Take a comfortable position and begin to notice your breathing. "
                    "There's no need to change anything - simply observe each breath as it comes and goes. "
                    "If your mind wanders, gently guide your attention back to your breath. "
                    "This is your time to be present with yourself."
                ),
                "learning_objectives": [
                    "Practice mindful breathing",
                    "Develop present-moment awareness",
                    "Learn to redirect attention gently",
                ],
                "duration": 600,
            },
            "grounding": {
                "title": "Grounding Sanctuary",
                "description": "A safe space designed to help you feel more grounded and centered",
                "narrative_content": (
                    "You enter a sanctuary specifically designed for grounding and centering. "
                    "Feel your feet making contact with the solid floor beneath you. "
                    "Notice five things you can see around you, taking time to really observe each one. "
                    "Listen for four different sounds in your environment. "
                    "Identify three things you can touch, feeling their texture and temperature. "
                    "This practice helps anchor you in the present moment and in your body."
                ),
                "learning_objectives": [
                    "Practice 5-4-3-2-1 grounding technique",
                    "Connect with physical sensations",
                    "Develop anchoring skills",
                ],
                "duration": 480,
            },
            "crisis_support": {
                "title": "Safe Haven",
                "description": "A completely safe and supportive environment for crisis support",
                "narrative_content": (
                    "You are in a completely safe space, surrounded by warmth and protection. "
                    "Here, you are valued, supported, and never alone. "
                    "Take all the time you need to feel safe and supported. "
                    "Remember that difficult feelings are temporary, and you have survived challenges before. "
                    "You have inner strength and resilience, even when it's hard to feel. "
                    "Help and support are always available to you."
                ),
                "learning_objectives": [
                    "Experience safety and support",
                    "Remember personal resilience",
                    "Connect with available resources",
                ],
                "duration": 900,
            },
            "breathing": {
                "title": "Breathing Practice Space",
                "description": "A calming environment designed for breathing exercises and relaxation",
                "narrative_content": (
                    "You enter a space filled with gentle, flowing air and soft natural light. "
                    "This is a place dedicated to the healing power of conscious breathing. "
                    "Begin by taking a slow, deep breath in through your nose, feeling your chest and belly expand. "
                    "Hold for a moment, then slowly exhale through your mouth, releasing any tension. "
                    "Continue this rhythm, allowing each breath to bring you deeper into relaxation and peace."
                ),
                "learning_objectives": [
                    "Learn deep breathing techniques",
                    "Experience relaxation response",
                    "Develop breath awareness",
                ],
                "duration": 420,
            },
            "emotional_regulation": {
                "title": "Emotional Balance Chamber",
                "description": "A supportive space for exploring and regulating emotions",
                "narrative_content": (
                    "You find yourself in a space designed to help you understand and work with your emotions. "
                    "Here, all feelings are welcome and accepted without judgment. "
                    "Take a moment to notice what you're feeling right now, without trying to change it. "
                    "Observe your emotions like clouds passing through the sky - present, but not permanent. "
                    "You have the power to acknowledge your feelings while choosing how to respond to them."
                ),
                "learning_objectives": [
                    "Practice emotional awareness",
                    "Learn non-judgmental observation",
                    "Develop emotional choice",
                ],
                "duration": 540,
            },
        }

        return intervention_content.get(intervention_type, intervention_content["mindfulness"])
