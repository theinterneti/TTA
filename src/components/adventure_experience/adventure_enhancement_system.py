"""
Adventure Enhancement System

This module provides adventure-specific enhancements to make therapeutic
gaming experiences more engaging, immersive, and fun while maintaining
therapeutic value.
"""

import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Get current UTC time with timezone awareness."""
    return datetime.now(timezone.utc)


class AdventureTheme(Enum):
    """Adventure themes for different therapeutic contexts."""

    FANTASY_QUEST = "fantasy_quest"
    MODERN_MYSTERY = "modern_mystery"
    SPACE_EXPLORATION = "space_exploration"
    HISTORICAL_ADVENTURE = "historical_adventure"
    MAGICAL_ACADEMY = "magical_academy"
    SUPERHERO_JOURNEY = "superhero_journey"
    NATURE_EXPEDITION = "nature_expedition"
    CYBERPUNK_FUTURE = "cyberpunk_future"


class EngagementLevel(Enum):
    """Levels of user engagement."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXCEPTIONAL = "exceptional"


@dataclass
class AdventureContext:
    """Context for adventure experiences."""

    theme: AdventureTheme
    current_location: str
    world_state: dict[str, Any] = field(default_factory=dict)
    character_relationships: dict[str, float] = field(default_factory=dict)
    story_progression: float = 0.0
    exploration_opportunities: list[str] = field(default_factory=list)
    narrative_threads: list[str] = field(default_factory=list)


@dataclass
class EngagementMetrics:
    """Metrics for tracking user engagement."""

    current_score: float = 0.0
    choice_engagement: float = 0.0
    narrative_engagement: float = 0.0
    exploration_engagement: float = 0.0
    social_engagement: float = 0.0
    challenge_engagement: float = 0.0
    last_updated: datetime = field(default_factory=utc_now)


@dataclass
class NarrativeResponse:
    """Rich narrative response to user choices."""

    main_text: str
    flavor_text: str = ""
    world_changes: list[str] = field(default_factory=list)
    character_reactions: dict[str, str] = field(default_factory=dict)
    exploration_hints: list[str] = field(default_factory=list)
    emotional_tone: str = "neutral"
    immersion_elements: list[str] = field(default_factory=list)


class AdventureEnhancementSystem:
    """
    System for enhancing therapeutic gaming with adventure elements.

    This system adds engaging narrative, world-building, and immersive
    elements while maintaining therapeutic value and clinical effectiveness.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the adventure enhancement system."""
        self.config = config or {}

        # Adventure contexts for active sessions
        self.adventure_contexts: dict[str, AdventureContext] = {}

        # Engagement tracking
        self.engagement_metrics: dict[str, EngagementMetrics] = {}

        # Narrative templates and content
        self.narrative_templates = self._initialize_narrative_templates()
        self.world_elements = self._initialize_world_elements()
        self.character_archetypes = self._initialize_character_archetypes()

        # Engagement calculation parameters
        self.engagement_weights = {
            "choice_variety": 0.2,
            "narrative_richness": 0.25,
            "exploration_depth": 0.2,
            "social_interaction": 0.15,
            "challenge_level": 0.2,
        }

        # Performance metrics
        self.metrics = {
            "adventures_enhanced": 0,
            "engagement_calculations": 0,
            "narrative_responses_generated": 0,
            "world_state_updates": 0,
            "exploration_opportunities_created": 0,
        }

        logger.info("AdventureEnhancementSystem initialized")

    async def initialize(self):
        """Initialize the adventure enhancement system."""
        logger.info("AdventureEnhancementSystem initialization complete")

    def enhance_choice_response(
        self,
        session_id: str,
        user_choice: str,
        choice_context: dict[str, Any],
        base_response: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Enhance a choice response with adventure elements.

        This is the main method that adds adventure features to therapeutic responses.
        """
        try:
            # Get or create adventure context
            adventure_context = self._get_adventure_context(session_id, choice_context)

            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(
                session_id, user_choice, choice_context, adventure_context
            )

            # Generate narrative response
            narrative_response = self._generate_narrative_response(
                user_choice, choice_context, adventure_context
            )

            # Update world state
            world_changes = self._update_world_state(
                user_choice, choice_context, adventure_context
            )

            # Create exploration opportunities
            exploration_opportunities = self._create_exploration_opportunities(
                choice_context, adventure_context
            )

            # Update character relationships
            relationship_changes = self._update_character_relationships(
                user_choice, choice_context, adventure_context
            )

            # Calculate adventure progression
            progression_update = self._calculate_adventure_progression(
                choice_context, adventure_context
            )

            # Enhance the base response
            enhanced_response = {
                **base_response,
                "engagement_score": engagement_score,
                "narrative_response": narrative_response.main_text,
                "flavor_text": narrative_response.flavor_text,
                "world_state_changes": world_changes,
                "character_relationships": relationship_changes,
                "adventure_progression": progression_update,
                "story_context": self._get_story_context(adventure_context),
                "immersive_elements": narrative_response.immersion_elements,
                "choice_consequences": self._format_choice_consequences(
                    narrative_response
                ),
                "exploration_opportunities": exploration_opportunities,
            }

            # Update session progress with engagement
            if "session_progress" in enhanced_response:
                enhanced_response["session_progress"][
                    "engagement_score"
                ] = engagement_score

            # Update metrics
            self.metrics["adventures_enhanced"] += 1
            self.metrics["engagement_calculations"] += 1
            self.metrics["narrative_responses_generated"] += 1

            return enhanced_response

        except Exception as e:
            logger.error(f"Error enhancing choice response: {e}")
            # Return base response with minimal enhancements
            return {
                **base_response,
                "engagement_score": 0.5,  # Default moderate engagement
                "narrative_response": "You continue your journey with determination.",
                "adventure_enhancement_error": str(e),
            }

    def _get_adventure_context(
        self, session_id: str, choice_context: dict[str, Any]
    ) -> AdventureContext:
        """Get or create adventure context for a session."""
        if session_id not in self.adventure_contexts:
            # Determine theme from context or use default
            theme_name = choice_context.get("adventure_theme", "fantasy_quest")
            try:
                theme = AdventureTheme(theme_name)
            except ValueError:
                theme = AdventureTheme.FANTASY_QUEST

            # Create new adventure context
            self.adventure_contexts[session_id] = AdventureContext(
                theme=theme,
                current_location=self._get_starting_location(theme),
                world_state=self._initialize_world_state(theme),
                exploration_opportunities=self._get_initial_exploration_opportunities(
                    theme
                ),
                narrative_threads=self._get_initial_narrative_threads(theme),
            )

        return self.adventure_contexts[session_id]

    def _calculate_engagement_score(
        self,
        session_id: str,
        user_choice: str,
        choice_context: dict[str, Any],
        adventure_context: AdventureContext,
    ) -> float:
        """Calculate engagement score based on choice and context."""
        try:
            # Get or create engagement metrics
            if session_id not in self.engagement_metrics:
                self.engagement_metrics[session_id] = EngagementMetrics()

            metrics = self.engagement_metrics[session_id]

            # Calculate component scores
            choice_variety_score = self._calculate_choice_variety_score(
                user_choice, choice_context
            )
            narrative_richness_score = self._calculate_narrative_richness_score(
                choice_context, adventure_context
            )
            exploration_depth_score = self._calculate_exploration_depth_score(
                choice_context, adventure_context
            )
            social_interaction_score = self._calculate_social_interaction_score(
                choice_context, adventure_context
            )
            challenge_level_score = self._calculate_challenge_level_score(
                choice_context
            )

            # Weighted engagement score
            engagement_score = (
                choice_variety_score * self.engagement_weights["choice_variety"]
                + narrative_richness_score
                * self.engagement_weights["narrative_richness"]
                + exploration_depth_score * self.engagement_weights["exploration_depth"]
                + social_interaction_score
                * self.engagement_weights["social_interaction"]
                + challenge_level_score * self.engagement_weights["challenge_level"]
            )

            # Update metrics
            metrics.current_score = engagement_score
            metrics.choice_engagement = choice_variety_score
            metrics.narrative_engagement = narrative_richness_score
            metrics.exploration_engagement = exploration_depth_score
            metrics.social_engagement = social_interaction_score
            metrics.challenge_engagement = challenge_level_score
            metrics.last_updated = utc_now()

            return max(0.0, min(1.0, engagement_score))  # Clamp to [0, 1]

        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.5  # Default moderate engagement

    def _generate_narrative_response(
        self,
        user_choice: str,
        choice_context: dict[str, Any],
        adventure_context: AdventureContext,
    ) -> NarrativeResponse:
        """Generate rich narrative response to user choice."""
        try:
            theme = adventure_context.theme
            location = adventure_context.current_location

            # Get narrative templates for theme
            templates = self.narrative_templates.get(
                theme.value, self.narrative_templates["fantasy_quest"]
            )

            # Select appropriate template based on choice context
            scenario_type = choice_context.get("scenario", "general")
            template = templates.get(scenario_type, templates["general"])

            # Generate main narrative text
            main_text = template["main"].format(
                choice=user_choice, location=location, **choice_context
            )

            # Generate flavor text
            flavor_options = template.get(
                "flavor", ["You feel a sense of accomplishment."]
            )
            flavor_text = random.choice(flavor_options)

            # Generate world changes
            world_changes = self._generate_world_changes(
                user_choice, choice_context, adventure_context
            )

            # Generate character reactions
            character_reactions = self._generate_character_reactions(
                user_choice, adventure_context
            )

            # Generate exploration hints
            exploration_hints = self._generate_exploration_hints(
                choice_context, adventure_context
            )

            # Determine emotional tone
            emotional_tone = choice_context.get("emotional_tone", "determined")

            # Generate immersion elements
            immersion_elements = self._generate_immersion_elements(
                theme, location, choice_context
            )

            return NarrativeResponse(
                main_text=main_text,
                flavor_text=flavor_text,
                world_changes=world_changes,
                character_reactions=character_reactions,
                exploration_hints=exploration_hints,
                emotional_tone=emotional_tone,
                immersion_elements=immersion_elements,
            )

        except Exception as e:
            logger.error(f"Error generating narrative response: {e}")
            return NarrativeResponse(
                main_text=f"You {user_choice} and continue your journey with purpose.",
                flavor_text="Your actions have meaning in this world.",
            )

    def _calculate_choice_variety_score(
        self, user_choice: str, choice_context: dict[str, Any]
    ) -> float:
        """Calculate engagement score based on choice variety and creativity."""
        # Higher scores for creative, varied choices
        creative_keywords = [
            "creative",
            "innovative",
            "unique",
            "original",
            "thoughtful",
        ]
        variety_keywords = ["explore", "discover", "investigate", "experiment", "try"]

        choice_lower = user_choice.lower()
        score = 0.5  # Base score

        # Boost for creative choices
        if any(keyword in choice_lower for keyword in creative_keywords):
            score += 0.2

        # Boost for variety-seeking choices
        if any(keyword in choice_lower for keyword in variety_keywords):
            score += 0.15

        # Boost for complex choices (longer descriptions often indicate more thought)
        if len(user_choice) > 20:
            score += 0.1

        return min(1.0, score)

    def _calculate_narrative_richness_score(
        self, choice_context: dict[str, Any], adventure_context: AdventureContext
    ) -> float:
        """Calculate engagement score based on narrative richness."""
        score = 0.6  # Base narrative score

        # Boost for rich story context
        if len(adventure_context.narrative_threads) > 2:
            score += 0.2

        # Boost for world complexity
        if len(adventure_context.world_state) > 3:
            score += 0.15

        # Boost for character relationships
        if len(adventure_context.character_relationships) > 1:
            score += 0.15

        return min(1.0, score)

    def _calculate_exploration_depth_score(
        self, choice_context: dict[str, Any], adventure_context: AdventureContext
    ) -> float:
        """Calculate engagement score based on exploration opportunities."""
        score = 0.5  # Base exploration score

        # Boost for available exploration opportunities
        if len(adventure_context.exploration_opportunities) > 2:
            score += 0.3

        # Boost for exploration-focused choices
        if choice_context.get("scenario_type") == "exploration":
            score += 0.2

        return min(1.0, score)

    def _calculate_social_interaction_score(
        self, choice_context: dict[str, Any], adventure_context: AdventureContext
    ) -> float:
        """Calculate engagement score based on social interactions."""
        score = 0.4  # Base social score

        # Boost for character relationships
        if adventure_context.character_relationships:
            score += 0.3

        # Boost for social scenarios
        if choice_context.get("scenario_type") in [
            "social_interaction",
            "collaboration",
        ]:
            score += 0.3

        return min(1.0, score)

    def _calculate_challenge_level_score(self, choice_context: dict[str, Any]) -> float:
        """Calculate engagement score based on challenge level."""
        challenge_level = choice_context.get("challenge_level", "moderate")

        challenge_scores = {
            "easy": 0.4,
            "moderate": 0.7,
            "hard": 0.9,
            "expert": 0.8,  # Slightly lower as it might be frustrating
        }

        return challenge_scores.get(challenge_level, 0.6)

    def _update_world_state(
        self,
        user_choice: str,
        choice_context: dict[str, Any],
        adventure_context: AdventureContext,
    ) -> list[str]:
        """Update world state based on user choice."""
        changes = []

        # Example world state changes based on choice patterns
        choice_lower = user_choice.lower()

        if "help" in choice_lower:
            changes.append("The community's trust in you has grown")
            adventure_context.world_state["community_trust"] = (
                adventure_context.world_state.get("community_trust", 0) + 1
            )

        if "explore" in choice_lower:
            changes.append("New areas of the world have been revealed")
            adventure_context.world_state["areas_explored"] = (
                adventure_context.world_state.get("areas_explored", 0) + 1
            )

        if "solve" in choice_lower or "creative" in choice_lower:
            changes.append("Your reputation as a problem-solver spreads")
            adventure_context.world_state["reputation"] = (
                adventure_context.world_state.get("reputation", 0) + 1
            )

        # Update story progression
        adventure_context.story_progression = min(
            1.0, adventure_context.story_progression + 0.1
        )

        self.metrics["world_state_updates"] += 1
        return changes

    def _create_exploration_opportunities(
        self, choice_context: dict[str, Any], adventure_context: AdventureContext
    ) -> list[str]:
        """Create new exploration opportunities based on context."""
        opportunities = []
        theme = adventure_context.theme

        # Theme-specific exploration opportunities
        theme_opportunities = {
            AdventureTheme.FANTASY_QUEST: [
                "Investigate the mysterious glowing cave",
                "Follow the ancient forest path",
                "Explore the abandoned wizard's tower",
                "Search for the legendary artifact",
            ],
            AdventureTheme.MODERN_MYSTERY: [
                "Examine the crime scene more closely",
                "Interview the suspicious witness",
                "Research the victim's background",
                "Follow the digital trail",
            ],
            AdventureTheme.SPACE_EXPLORATION: [
                "Scan the unknown planet",
                "Investigate the alien signal",
                "Explore the derelict spacecraft",
                "Analyze the strange energy readings",
            ],
        }

        available_opportunities = theme_opportunities.get(
            theme, theme_opportunities[AdventureTheme.FANTASY_QUEST]
        )

        # Select 2-3 random opportunities
        selected_opportunities = random.sample(
            available_opportunities, min(3, len(available_opportunities))
        )
        opportunities.extend(selected_opportunities)

        # Update adventure context
        adventure_context.exploration_opportunities = opportunities

        self.metrics["exploration_opportunities_created"] += 1
        return opportunities

    def _update_character_relationships(
        self,
        user_choice: str,
        choice_context: dict[str, Any],
        adventure_context: AdventureContext,
    ) -> dict[str, float]:
        """Update character relationships based on user choice."""
        relationships = adventure_context.character_relationships.copy()

        # Example relationship updates
        choice_lower = user_choice.lower()

        if "help" in choice_lower or "support" in choice_lower:
            # Positive relationship changes
            for character in ["mentor", "companion", "villager"]:
                if character in relationships:
                    relationships[character] = min(1.0, relationships[character] + 0.1)
                else:
                    relationships[character] = 0.6

        if "empathy" in choice_lower or "compassion" in choice_lower:
            # Strong positive relationship changes
            for character in ["ally", "friend", "mentor"]:
                if character in relationships:
                    relationships[character] = min(1.0, relationships[character] + 0.15)
                else:
                    relationships[character] = 0.7

        # Update adventure context
        adventure_context.character_relationships = relationships

        return relationships

    def _calculate_adventure_progression(
        self, choice_context: dict[str, Any], adventure_context: AdventureContext
    ) -> dict[str, Any]:
        """Calculate adventure progression metrics."""
        return {
            "story_completion": adventure_context.story_progression,
            "areas_explored": adventure_context.world_state.get("areas_explored", 0),
            "relationships_formed": len(adventure_context.character_relationships),
            "narrative_threads_active": len(adventure_context.narrative_threads),
            "world_impact_score": sum(adventure_context.world_state.values())
            / max(1, len(adventure_context.world_state)),
        }

    def _get_story_context(self, adventure_context: AdventureContext) -> dict[str, Any]:
        """Get current story context for the adventure."""
        return {
            "theme": adventure_context.theme.value,
            "current_location": adventure_context.current_location,
            "story_progression": adventure_context.story_progression,
            "active_narrative_threads": adventure_context.narrative_threads,
            "world_state_summary": self._summarize_world_state(
                adventure_context.world_state
            ),
        }

    def _format_choice_consequences(
        self, narrative_response: NarrativeResponse
    ) -> list[str]:
        """Format choice consequences for display."""
        consequences = []

        if narrative_response.world_changes:
            consequences.extend(
                [
                    f"World Impact: {change}"
                    for change in narrative_response.world_changes
                ]
            )

        if narrative_response.character_reactions:
            consequences.extend(
                [
                    f"{char}: {reaction}"
                    for char, reaction in narrative_response.character_reactions.items()
                ]
            )

        if not consequences:
            consequences.append("Your choice ripples through the world in subtle ways.")

        return consequences

    def _initialize_narrative_templates(self) -> dict[str, dict[str, dict[str, Any]]]:
        """Initialize narrative templates for different themes and scenarios."""
        return {
            "fantasy_quest": {
                "general": {
                    "main": "In the mystical realm, you {choice}. The ancient magic responds to your determination.",
                    "flavor": [
                        "The wind carries whispers of your growing legend.",
                        "Magical energies swirl around you, recognizing your purpose.",
                        "The very stones beneath your feet seem to acknowledge your journey.",
                    ],
                },
                "social_interaction": {
                    "main": "You {choice} with the inhabitants of this magical world. Your words carry weight here.",
                    "flavor": [
                        "The bonds you forge will echo through the ages.",
                        "Trust is a precious currency in these lands.",
                        "Your empathy opens doors that force cannot.",
                    ],
                },
                "exploration": {
                    "main": "As you {choice}, new wonders of this realm reveal themselves to you.",
                    "flavor": [
                        "Every step forward is a step into legend.",
                        "The unknown beckons with promises of discovery.",
                        "Adventure flows through your veins like liquid courage.",
                    ],
                },
            },
            "modern_mystery": {
                "general": {
                    "main": "In the shadows of the city, you {choice}. The truth draws closer.",
                    "flavor": [
                        "Every clue is a piece of a larger puzzle.",
                        "The city holds its secrets close, but not from you.",
                        "Justice moves through you like a steady current.",
                    ],
                }
            },
        }

    def _initialize_world_elements(self) -> dict[str, list[str]]:
        """Initialize world elements for different themes."""
        return {
            "fantasy_quest": [
                "Ancient forests with talking trees",
                "Mystical caves filled with glowing crystals",
                "Floating islands connected by rainbow bridges",
                "Villages of friendly magical creatures",
                "Towers of wise wizards and scholars",
            ],
            "modern_mystery": [
                "Rain-soaked city streets",
                "Dimly lit detective offices",
                "High-tech forensics laboratories",
                "Shadowy alleyways with hidden secrets",
                "Bustling cafes where information is traded",
            ],
        }

    def _initialize_character_archetypes(self) -> dict[str, dict[str, Any]]:
        """Initialize character archetypes for different themes."""
        return {
            "fantasy_quest": {
                "mentor": {"name": "Wise Sage", "relationship": 0.7, "role": "guide"},
                "companion": {
                    "name": "Loyal Friend",
                    "relationship": 0.8,
                    "role": "support",
                },
                "villager": {
                    "name": "Grateful Citizen",
                    "relationship": 0.5,
                    "role": "community",
                },
            },
            "modern_mystery": {
                "partner": {
                    "name": "Detective Partner",
                    "relationship": 0.6,
                    "role": "ally",
                },
                "informant": {
                    "name": "Street Contact",
                    "relationship": 0.4,
                    "role": "information",
                },
                "witness": {
                    "name": "Key Witness",
                    "relationship": 0.3,
                    "role": "evidence",
                },
            },
        }

    def _get_starting_location(self, theme: AdventureTheme) -> str:
        """Get starting location for a theme."""
        locations = {
            AdventureTheme.FANTASY_QUEST: "The Village Square",
            AdventureTheme.MODERN_MYSTERY: "Detective's Office",
            AdventureTheme.SPACE_EXPLORATION: "Starship Bridge",
            AdventureTheme.HISTORICAL_ADVENTURE: "Ancient Marketplace",
            AdventureTheme.MAGICAL_ACADEMY: "Academy Entrance Hall",
            AdventureTheme.SUPERHERO_JOURNEY: "City Rooftop",
            AdventureTheme.NATURE_EXPEDITION: "Forest Trailhead",
            AdventureTheme.CYBERPUNK_FUTURE: "Neon-lit Street",
        }
        return locations.get(theme, "The Starting Point")

    def _initialize_world_state(self, theme: AdventureTheme) -> dict[str, Any]:
        """Initialize world state for a theme."""
        return {
            "community_trust": 0,
            "areas_explored": 0,
            "reputation": 0,
            "story_events_completed": 0,
            "relationships_formed": 0,
        }

    def _get_initial_exploration_opportunities(
        self, theme: AdventureTheme
    ) -> list[str]:
        """Get initial exploration opportunities for a theme."""
        opportunities = {
            AdventureTheme.FANTASY_QUEST: [
                "Explore the Enchanted Forest",
                "Visit the Ancient Library",
                "Investigate the Mysterious Cave",
            ],
            AdventureTheme.MODERN_MYSTERY: [
                "Examine the Crime Scene",
                "Interview Witnesses",
                "Research Case Files",
            ],
        }
        return opportunities.get(
            theme, ["Begin your adventure", "Look around", "Talk to someone"]
        )

    def _get_initial_narrative_threads(self, theme: AdventureTheme) -> list[str]:
        """Get initial narrative threads for a theme."""
        threads = {
            AdventureTheme.FANTASY_QUEST: [
                "The Quest for the Lost Artifact",
                "The Mystery of the Disappearing Magic",
                "The Legend of the Ancient Hero",
            ],
            AdventureTheme.MODERN_MYSTERY: [
                "The Case of the Missing Person",
                "The Corporate Conspiracy",
                "The Serial Killer's Pattern",
            ],
        }
        return threads.get(theme, ["Your Personal Journey", "The Main Quest"])

    def _generate_world_changes(
        self,
        user_choice: str,
        choice_context: dict[str, Any],
        adventure_context: AdventureContext,
    ) -> list[str]:
        """Generate world changes based on user choice."""
        changes = []
        choice_lower = user_choice.lower()

        # Add thematic world changes
        if adventure_context.theme == AdventureTheme.FANTASY_QUEST:
            if "magic" in choice_lower:
                changes.append(
                    "The magical energies of the realm shift in response to your actions"
                )
            if "nature" in choice_lower:
                changes.append("The natural world seems more vibrant and alive")

        return changes

    def _generate_character_reactions(
        self, user_choice: str, adventure_context: AdventureContext
    ) -> dict[str, str]:
        """Generate character reactions to user choice."""
        reactions = {}
        choice_lower = user_choice.lower()

        # Generate reactions based on existing relationships
        for (
            character,
            relationship_level,
        ) in adventure_context.character_relationships.items():
            if relationship_level > 0.7:
                if "help" in choice_lower:
                    reactions[character] = "smiles warmly at your kindness"
                elif "brave" in choice_lower or "courage" in choice_lower:
                    reactions[character] = "nods approvingly at your bravery"
            elif relationship_level > 0.4:
                reactions[character] = "watches your actions with interest"

        return reactions

    def _generate_exploration_hints(
        self, choice_context: dict[str, Any], adventure_context: AdventureContext
    ) -> list[str]:
        """Generate exploration hints based on context."""
        hints = []

        if adventure_context.story_progression < 0.3:
            hints.append("There are still many mysteries to uncover in this world")

        if len(adventure_context.character_relationships) < 3:
            hints.append(
                "Building relationships with others might open new opportunities"
            )

        if adventure_context.world_state.get("areas_explored", 0) < 2:
            hints.append("This world has many hidden places waiting to be discovered")

        return hints

    def _generate_immersion_elements(
        self, theme: AdventureTheme, location: str, choice_context: dict[str, Any]
    ) -> list[str]:
        """Generate immersion elements for the current context."""
        elements = []

        # Theme-specific immersion elements
        if theme == AdventureTheme.FANTASY_QUEST:
            elements.extend(
                [
                    "The air shimmers with magical possibility",
                    "Ancient runes glow softly on nearby stones",
                    "The sound of distant adventure calls to you",
                ]
            )
        elif theme == AdventureTheme.MODERN_MYSTERY:
            elements.extend(
                [
                    "The city's secrets whisper in the shadows",
                    "Neon lights reflect off rain-slicked streets",
                    "The weight of truth presses against your consciousness",
                ]
            )

        # Add location-specific elements
        elements.append(
            f"The atmosphere of {location} surrounds you with its unique energy"
        )

        return elements[:3]  # Limit to 3 elements for readability

    def _summarize_world_state(self, world_state: dict[str, Any]) -> str:
        """Summarize the current world state."""
        if not world_state:
            return "The world awaits your influence"

        summary_parts = []

        trust = world_state.get("community_trust", 0)
        if trust > 0:
            summary_parts.append(f"You are trusted by {trust} communities")

        explored = world_state.get("areas_explored", 0)
        if explored > 0:
            summary_parts.append(f"You have explored {explored} new areas")

        reputation = world_state.get("reputation", 0)
        if reputation > 0:
            summary_parts.append("Your reputation as a problem-solver is growing")

        if not summary_parts:
            return "Your journey is just beginning"

        return "; ".join(summary_parts)

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the adventure enhancement system."""
        return {
            "status": "healthy",
            "adventure_contexts_active": len(self.adventure_contexts),
            "engagement_metrics_tracked": len(self.engagement_metrics),
            "narrative_templates_loaded": len(self.narrative_templates),
            "metrics": self.metrics,
            "ready_for_adventure_enhancement": True,
        }
