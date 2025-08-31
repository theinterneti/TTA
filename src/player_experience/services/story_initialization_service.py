"""
Story Initialization Service

This service detects character creation completion and initializes personalized story experiences
using character data and therapeutic goals to create seamless transitions into gameplay.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.components.gameplay_loop.controllers.gameplay_loop_controller import (
    GameplayLoopController,
    SessionConfiguration,
    SessionPacing,
)

from ..database.character_repository import CharacterRepository
from ..managers.world_management_module import WorldManagementModule
from ..models.character import Character
from ..models.world import World

logger = logging.getLogger(__name__)


@dataclass
class StoryInitializationContext:
    """Context for story initialization."""

    player_id: str
    character_id: str
    character_data: Character
    world_id: str | None = None
    world_data: World | None = None
    therapeutic_goals: list[str] = None
    story_preferences: dict[str, Any] = None

    def __post_init__(self):
        if self.therapeutic_goals is None:
            self.therapeutic_goals = []
        if self.story_preferences is None:
            self.story_preferences = {}


@dataclass
class StoryInitializationResult:
    """Result of story initialization."""

    session_id: str
    story_context: dict[str, Any]
    initial_scene_id: str
    narrative_prompt: str
    success: bool
    error_message: str | None = None


class StoryInitializationService:
    """
    Service for initializing personalized story experiences based on character data and therapeutic goals.

    Handles the transition from character creation to active gameplay by:
    - Analyzing character attributes and background
    - Selecting appropriate story worlds and scenarios
    - Initializing narrative context with therapeutic integration
    - Creating personalized opening scenes
    """

    def __init__(
        self,
        character_repository: CharacterRepository | None = None,
        world_manager: WorldManagementModule | None = None,
        gameplay_controller: GameplayLoopController | None = None,
    ):
        """
        Initialize the Story Initialization Service.

        Args:
            character_repository: Repository for character data
            world_manager: Manager for world selection and data
            gameplay_controller: Controller for gameplay sessions
        """
        self.character_repository = character_repository or CharacterRepository()
        self.world_manager = world_manager or WorldManagementModule()
        self.gameplay_controller = gameplay_controller

        # Story templates and scenarios
        self.story_templates = self._load_story_templates()
        self.therapeutic_scenarios = self._load_therapeutic_scenarios()
        self.world_compatibility_matrix = self._load_world_compatibility()

        # Configuration
        self.default_session_duration = 35  # minutes
        self.max_initialization_attempts = 3

        # Metrics
        self.metrics = {
            "stories_initialized": 0,
            "character_analysis_performed": 0,
            "world_selections_made": 0,
            "therapeutic_integrations": 0,
            "initialization_failures": 0,
        }

        logger.info("StoryInitializationService initialized")

    async def initialize_story_session(
        self,
        player_id: str,
        character_id: str,
        world_id: str | None = None,
        therapeutic_goals: list[str] | None = None,
        story_preferences: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Initialize a new story session for a player with their character.

        Args:
            player_id: Player identifier
            character_id: Character identifier
            world_id: Optional specific world ID
            therapeutic_goals: Optional therapeutic goals
            story_preferences: Optional story preferences

        Returns:
            Session ID if successful, None otherwise
        """
        try:
            # Create initialization context
            context = await self._create_initialization_context(
                player_id=player_id,
                character_id=character_id,
                world_id=world_id,
                therapeutic_goals=therapeutic_goals or [],
                story_preferences=story_preferences or {},
            )

            if not context:
                logger.error(
                    f"Failed to create initialization context for player {player_id}"
                )
                return None

            # Initialize the story
            result = await self._initialize_story(context)

            if result.success:
                self.metrics["stories_initialized"] += 1
                logger.info(
                    f"Successfully initialized story session {result.session_id} for player {player_id}"
                )
                return result.session_id
            else:
                self.metrics["initialization_failures"] += 1
                logger.error(f"Failed to initialize story: {result.error_message}")
                return None

        except Exception as e:
            self.metrics["initialization_failures"] += 1
            logger.error(
                f"Error initializing story session for player {player_id}: {e}"
            )
            return None

    async def _create_initialization_context(
        self,
        player_id: str,
        character_id: str,
        world_id: str | None,
        therapeutic_goals: list[str],
        story_preferences: dict[str, Any],
    ) -> StoryInitializationContext | None:
        """Create initialization context with character and world data."""
        try:
            # Get character data
            character_data = await self.character_repository.get_character(character_id)
            if not character_data:
                logger.error(f"Character {character_id} not found")
                return None

            # Select or validate world
            if world_id:
                world_data = await self.world_manager.get_world(world_id)
                if not world_data:
                    logger.warning(
                        f"Specified world {world_id} not found, selecting automatically"
                    )
                    world_id, world_data = await self._select_compatible_world(
                        character_data, therapeutic_goals
                    )
            else:
                world_id, world_data = await self._select_compatible_world(
                    character_data, therapeutic_goals
                )

            if not world_data:
                logger.error("No compatible world found for character")
                return None

            return StoryInitializationContext(
                player_id=player_id,
                character_id=character_id,
                character_data=character_data,
                world_id=world_id,
                world_data=world_data,
                therapeutic_goals=therapeutic_goals,
                story_preferences=story_preferences,
            )

        except Exception as e:
            logger.error(f"Error creating initialization context: {e}")
            return None

    async def _initialize_story(
        self, context: StoryInitializationContext
    ) -> StoryInitializationResult:
        """Initialize the story with the given context."""
        try:
            session_id = f"story_{uuid.uuid4().hex[:12]}"

            # Analyze character for story personalization
            character_analysis = await self._analyze_character_for_story(
                context.character_data
            )
            self.metrics["character_analysis_performed"] += 1

            # Create story context
            story_context = await self._create_story_context(
                context, character_analysis
            )

            # Generate initial scene
            initial_scene_id, narrative_prompt = await self._generate_opening_scene(
                context, story_context
            )

            # Create gameplay session if controller is available
            if self.gameplay_controller:
                session_config = SessionConfiguration(
                    user_id=context.player_id,
                    pacing=self._determine_session_pacing(context),
                    therapeutic_goals=context.therapeutic_goals,
                    estimated_duration_minutes=self.default_session_duration,
                )

                session_state, _ = await self.gameplay_controller.start_session(
                    user_id=context.player_id, session_config=session_config
                )
                session_id = session_state.session_id

            # Integrate therapeutic elements
            await self._integrate_therapeutic_elements(
                story_context, context.therapeutic_goals
            )
            self.metrics["therapeutic_integrations"] += 1

            return StoryInitializationResult(
                session_id=session_id,
                story_context=story_context,
                initial_scene_id=initial_scene_id,
                narrative_prompt=narrative_prompt,
                success=True,
            )

        except Exception as e:
            logger.error(f"Error initializing story: {e}")
            return StoryInitializationResult(
                session_id="",
                story_context={},
                initial_scene_id="",
                narrative_prompt="",
                success=False,
                error_message=str(e),
            )

    async def _select_compatible_world(
        self, character_data: Character, therapeutic_goals: list[str]
    ) -> tuple[str | None, World | None]:
        """Select a world compatible with character and therapeutic goals."""
        try:
            # Get available worlds
            available_worlds = await self.world_manager.get_available_worlds()

            # Score worlds based on compatibility
            world_scores = []
            for world in available_worlds:
                score = await self._calculate_world_compatibility_score(
                    world, character_data, therapeutic_goals
                )
                world_scores.append((world.id, world, score))

            # Sort by score and select best match
            world_scores.sort(key=lambda x: x[2], reverse=True)

            if world_scores:
                world_id, world_data, score = world_scores[0]
                logger.info(
                    f"Selected world {world_id} with compatibility score {score}"
                )
                self.metrics["world_selections_made"] += 1
                return world_id, world_data

            logger.warning("No compatible worlds found")
            return None, None

        except Exception as e:
            logger.error(f"Error selecting compatible world: {e}")
            return None, None

    async def _calculate_world_compatibility_score(
        self, world: World, character_data: Character, therapeutic_goals: list[str]
    ) -> float:
        """Calculate compatibility score between world, character, and therapeutic goals."""
        score = 0.0

        # Character attribute compatibility
        character_attributes = character_data.attributes or {}
        world_themes = world.themes or []

        # Match character personality with world themes
        if character_attributes.get("personality_type"):
            personality = character_attributes["personality_type"]
            if (
                personality in ["adventurous", "curious"]
                and "exploration" in world_themes
            ):
                score += 2.0
            elif (
                personality in ["cautious", "analytical"] and "mystery" in world_themes
            ):
                score += 2.0
            elif (
                personality in ["social", "empathetic"]
                and "relationships" in world_themes
            ):
                score += 2.0

        # Therapeutic goal alignment
        world_therapeutic_focus = world.therapeutic_focus or []
        for goal in therapeutic_goals:
            if goal in world_therapeutic_focus:
                score += 3.0  # High weight for therapeutic alignment

        # Character background compatibility
        character_background = character_attributes.get("background", "")
        if character_background and any(
            theme in character_background.lower() for theme in world_themes
        ):
            score += 1.5

        # Difficulty level matching
        character_experience = character_attributes.get("experience_level", "beginner")
        world_difficulty = world.difficulty_level or "medium"

        difficulty_match = {
            ("beginner", "easy"): 2.0,
            ("beginner", "medium"): 1.0,
            ("intermediate", "medium"): 2.0,
            ("intermediate", "hard"): 1.0,
            ("advanced", "hard"): 2.0,
            ("advanced", "medium"): 1.5,
        }
        score += difficulty_match.get((character_experience, world_difficulty), 0.0)

        return score

    async def _analyze_character_for_story(
        self, character_data: Character
    ) -> dict[str, Any]:
        """Analyze character data to inform story personalization."""
        analysis = {
            "personality_traits": [],
            "strengths": [],
            "growth_areas": [],
            "preferred_interaction_style": "balanced",
            "emotional_themes": [],
            "narrative_hooks": [],
        }

        attributes = character_data.attributes or {}

        # Extract personality traits
        if "personality_type" in attributes:
            analysis["personality_traits"].append(attributes["personality_type"])

        # Identify strengths from character attributes
        for attr, value in attributes.items():
            if isinstance(value, (int, float)) and value > 7:  # High attribute values
                analysis["strengths"].append(attr)
            elif isinstance(value, (int, float)) and value < 4:  # Low attribute values
                analysis["growth_areas"].append(attr)

        # Determine interaction style based on social attributes
        social_score = attributes.get("social_confidence", 5)
        if social_score > 7:
            analysis["preferred_interaction_style"] = "social"
        elif social_score < 4:
            analysis["preferred_interaction_style"] = "introspective"

        # Extract emotional themes from background
        background = attributes.get("background", "")
        if "trauma" in background.lower():
            analysis["emotional_themes"].append("healing")
        if "loss" in background.lower():
            analysis["emotional_themes"].append("grief_processing")
        if "anxiety" in background.lower():
            analysis["emotional_themes"].append("anxiety_management")

        # Create narrative hooks based on character elements
        if attributes.get("goals"):
            analysis["narrative_hooks"].extend(attributes["goals"])
        if attributes.get("fears"):
            analysis["narrative_hooks"].extend(
                [f"overcoming_{fear}" for fear in attributes["fears"]]
            )

        return analysis

    async def _create_story_context(
        self, context: StoryInitializationContext, character_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Create comprehensive story context for narrative generation."""
        story_context = {
            "session_metadata": {
                "player_id": context.player_id,
                "character_id": context.character_id,
                "world_id": context.world_id,
                "initialization_timestamp": datetime.utcnow().isoformat(),
            },
            "character_context": {
                "name": context.character_data.name,
                "attributes": context.character_data.attributes,
                "background": context.character_data.background,
                "personality_analysis": character_analysis,
            },
            "world_context": {
                "name": context.world_data.name,
                "description": context.world_data.description,
                "themes": context.world_data.themes,
                "setting": context.world_data.setting,
                "therapeutic_focus": context.world_data.therapeutic_focus,
            },
            "therapeutic_context": {
                "goals": context.therapeutic_goals,
                "focus_areas": character_analysis.get("growth_areas", []),
                "strengths_to_leverage": character_analysis.get("strengths", []),
                "interaction_style": character_analysis.get(
                    "preferred_interaction_style", "balanced"
                ),
            },
            "narrative_context": {
                "current_scene": "opening",
                "emotional_tone": "welcoming",
                "pacing": "gentle_introduction",
                "available_themes": character_analysis.get("emotional_themes", []),
                "narrative_hooks": character_analysis.get("narrative_hooks", []),
            },
            "preferences": context.story_preferences,
        }

        return story_context

    async def _generate_opening_scene(
        self, context: StoryInitializationContext, story_context: dict[str, Any]
    ) -> tuple[str, str]:
        """Generate the opening scene and narrative prompt."""
        scene_id = f"opening_{context.world_id}_{uuid.uuid4().hex[:8]}"

        # Select appropriate opening template based on character and world
        opening_template = await self._select_opening_template(context, story_context)

        # Personalize the narrative prompt
        narrative_prompt = await self._personalize_narrative_prompt(
            opening_template, story_context
        )

        return scene_id, narrative_prompt

    async def _select_opening_template(
        self, context: StoryInitializationContext, story_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Select appropriate opening template based on context."""
        # Default opening template structure
        template = {
            "setting_introduction": True,
            "character_integration": True,
            "gentle_engagement": True,
            "therapeutic_framing": True,
            "choice_introduction": False,  # Start with narrative, introduce choices gradually
        }

        # Adjust based on character analysis
        personality_analysis = story_context["character_context"][
            "personality_analysis"
        ]
        interaction_style = personality_analysis.get(
            "preferred_interaction_style", "balanced"
        )

        if interaction_style == "social":
            template["character_interaction"] = True
            template["choice_introduction"] = True
        elif interaction_style == "introspective":
            template["internal_reflection"] = True
            template["gentle_engagement"] = True

        # Adjust based on therapeutic goals
        therapeutic_goals = context.therapeutic_goals
        if "anxiety_management" in therapeutic_goals:
            template["safe_environment_emphasis"] = True
            template["control_options"] = True
        if "social_skills" in therapeutic_goals:
            template["character_interaction"] = True

        return template

    async def _personalize_narrative_prompt(
        self, template: dict[str, Any], story_context: dict[str, Any]
    ) -> str:
        """Create personalized narrative prompt based on template and context."""
        character_name = story_context["character_context"]["name"]
        world_name = story_context["world_context"]["name"]
        world_description = story_context["world_context"]["description"]

        # Build narrative prompt components
        prompt_parts = []

        # Setting introduction
        if template.get("setting_introduction"):
            prompt_parts.append(
                f"Welcome to {world_name}, {character_name}. {world_description}"
            )

        # Character integration
        if template.get("character_integration"):
            background = story_context["character_context"]["background"]
            if background:
                prompt_parts.append(
                    f"As someone with your background in {background}, you find yourself..."
                )
            else:
                prompt_parts.append("You find yourself...")

        # Therapeutic framing
        if template.get("therapeutic_framing"):
            therapeutic_goals = story_context["therapeutic_context"]["goals"]
            if therapeutic_goals:
                goals_text = ", ".join(therapeutic_goals)
                prompt_parts.append(
                    f"This journey will help you explore {goals_text} in a safe, supportive environment."
                )

        # Safe environment emphasis
        if template.get("safe_environment_emphasis"):
            prompt_parts.append(
                "Remember, this is your space to explore and grow at your own pace. You're in control of your experience."
            )

        # Gentle engagement
        if template.get("gentle_engagement"):
            prompt_parts.append(
                "Take a moment to look around and get comfortable with your surroundings."
            )

        # Combine parts into cohesive narrative
        narrative_prompt = " ".join(prompt_parts)

        # Add opening scene specific content based on world themes
        world_themes = story_context["world_context"]["themes"]
        if "nature" in world_themes:
            narrative_prompt += " The gentle sounds of nature surround you, creating a peaceful atmosphere."
        elif "urban" in world_themes:
            narrative_prompt += (
                " The familiar sounds of city life provide a comforting backdrop."
            )
        elif "fantasy" in world_themes:
            narrative_prompt += " The air shimmers with possibility and wonder."

        return narrative_prompt

    async def _integrate_therapeutic_elements(
        self, story_context: dict[str, Any], therapeutic_goals: list[str]
    ) -> None:
        """Integrate therapeutic elements into the story context."""
        therapeutic_elements = {
            "coping_strategies": [],
            "skill_practice_opportunities": [],
            "reflection_prompts": [],
            "safety_mechanisms": [],
            "progress_markers": [],
        }

        # Map therapeutic goals to specific elements
        goal_mappings = {
            "anxiety_management": {
                "coping_strategies": [
                    "breathing_exercises",
                    "grounding_techniques",
                    "progressive_relaxation",
                ],
                "skill_practice_opportunities": [
                    "mindful_observation",
                    "anxiety_reframing",
                    "safe_space_creation",
                ],
                "reflection_prompts": [
                    "anxiety_triggers",
                    "coping_effectiveness",
                    "progress_recognition",
                ],
            },
            "social_skills": {
                "coping_strategies": [
                    "conversation_starters",
                    "active_listening",
                    "empathy_building",
                ],
                "skill_practice_opportunities": [
                    "character_interaction",
                    "group_dynamics",
                    "conflict_resolution",
                ],
                "reflection_prompts": [
                    "social_comfort",
                    "communication_effectiveness",
                    "relationship_building",
                ],
            },
            "self_esteem": {
                "coping_strategies": [
                    "positive_self_talk",
                    "strength_recognition",
                    "achievement_celebration",
                ],
                "skill_practice_opportunities": [
                    "decision_making",
                    "leadership_moments",
                    "creative_expression",
                ],
                "reflection_prompts": [
                    "personal_strengths",
                    "growth_recognition",
                    "self_compassion",
                ],
            },
            "emotional_regulation": {
                "coping_strategies": [
                    "emotion_identification",
                    "intensity_scaling",
                    "healthy_expression",
                ],
                "skill_practice_opportunities": [
                    "emotional_choice_points",
                    "empathy_practice",
                    "boundary_setting",
                ],
                "reflection_prompts": [
                    "emotional_awareness",
                    "regulation_strategies",
                    "emotional_growth",
                ],
            },
        }

        # Integrate elements for each therapeutic goal
        for goal in therapeutic_goals:
            if goal in goal_mappings:
                mapping = goal_mappings[goal]
                for element_type, elements in mapping.items():
                    therapeutic_elements[element_type].extend(elements)

        # Add safety mechanisms for all sessions
        therapeutic_elements["safety_mechanisms"].extend(
            ["pause_option", "support_access", "intensity_control", "safe_exit"]
        )

        # Add to story context
        story_context["therapeutic_context"]["elements"] = therapeutic_elements

    def _determine_session_pacing(
        self, context: StoryInitializationContext
    ) -> SessionPacing:
        """Determine appropriate session pacing based on character and goals."""
        # Default to standard pacing
        pacing = SessionPacing.STANDARD

        # Adjust based on character attributes
        attributes = context.character_data.attributes or {}

        # Check for anxiety or stress indicators
        if attributes.get("anxiety_level", 5) > 7:
            pacing = SessionPacing.RELAXED
        elif "anxiety_management" in context.therapeutic_goals:
            pacing = SessionPacing.RELAXED

        # Check for high engagement preferences
        if attributes.get("engagement_preference") == "high_intensity":
            pacing = SessionPacing.INTENSIVE
        elif attributes.get("experience_level") == "advanced":
            pacing = SessionPacing.STANDARD

        return pacing

    def _load_story_templates(self) -> dict[str, Any]:
        """Load story templates for different scenarios."""
        # In a real implementation, this would load from a database or configuration files
        return {
            "gentle_introduction": {
                "pacing": "slow",
                "complexity": "low",
                "therapeutic_integration": "high",
            },
            "adventure_start": {
                "pacing": "medium",
                "complexity": "medium",
                "therapeutic_integration": "medium",
            },
            "skill_focused": {
                "pacing": "structured",
                "complexity": "variable",
                "therapeutic_integration": "high",
            },
        }

    def _load_therapeutic_scenarios(self) -> dict[str, Any]:
        """Load therapeutic scenarios and interventions."""
        # In a real implementation, this would load from a therapeutic content database
        return {
            "anxiety_management": {
                "scenarios": [
                    "safe_exploration",
                    "gradual_exposure",
                    "comfort_zone_expansion",
                ],
                "interventions": [
                    "breathing_guidance",
                    "grounding_exercises",
                    "reassurance",
                ],
            },
            "social_skills": {
                "scenarios": [
                    "character_meeting",
                    "group_interaction",
                    "conflict_resolution",
                ],
                "interventions": [
                    "conversation_coaching",
                    "empathy_building",
                    "social_feedback",
                ],
            },
            "self_esteem": {
                "scenarios": [
                    "achievement_opportunities",
                    "strength_discovery",
                    "positive_recognition",
                ],
                "interventions": [
                    "strength_highlighting",
                    "success_celebration",
                    "self_compassion",
                ],
            },
        }

    def _load_world_compatibility(self) -> dict[str, Any]:
        """Load world compatibility matrix for character-world matching."""
        # In a real implementation, this would be a comprehensive compatibility database
        return {
            "personality_world_match": {
                "adventurous": ["fantasy_realm", "exploration_world", "adventure_land"],
                "analytical": [
                    "mystery_world",
                    "puzzle_realm",
                    "investigation_setting",
                ],
                "social": ["community_world", "relationship_realm", "social_hub"],
                "creative": ["artistic_world", "imagination_realm", "creative_space"],
            },
            "therapeutic_world_match": {
                "anxiety_management": ["peaceful_garden", "safe_haven", "comfort_zone"],
                "social_skills": [
                    "community_center",
                    "social_world",
                    "interaction_hub",
                ],
                "self_esteem": [
                    "achievement_world",
                    "success_realm",
                    "confidence_builder",
                ],
            },
        }

    async def get_initialization_status(self, player_id: str) -> dict[str, Any]:
        """Get the initialization status for a player."""
        # This would check if character creation is complete and ready for story initialization
        try:
            # Check for completed characters
            characters = await self.character_repository.get_player_characters(
                player_id
            )
            completed_characters = [char for char in characters if char.is_complete]

            return {
                "player_id": player_id,
                "characters_available": len(completed_characters),
                "ready_for_initialization": len(completed_characters) > 0,
                "available_characters": [
                    {
                        "id": char.id,
                        "name": char.name,
                        "completion_status": (
                            "complete" if char.is_complete else "incomplete"
                        ),
                    }
                    for char in characters
                ],
            }
        except Exception as e:
            logger.error(
                f"Error getting initialization status for player {player_id}: {e}"
            )
            return {
                "player_id": player_id,
                "characters_available": 0,
                "ready_for_initialization": False,
                "error": str(e),
            }

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for the story initialization service."""
        return {
            **self.metrics,
            "templates_loaded": len(self.story_templates),
            "therapeutic_scenarios_loaded": len(self.therapeutic_scenarios),
        }
