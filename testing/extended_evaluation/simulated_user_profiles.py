"""
Simulated User Profiles for Extended Session Testing

Provides sophisticated user behavior modeling for realistic testing of
TTA storytelling system with diverse interaction patterns, decision-making
approaches, and engagement styles.
"""

import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class DecisionMakingStyle(Enum):
    """User decision-making approaches."""

    IMPULSIVE = "impulsive"  # Quick, instinctive decisions
    ANALYTICAL = "analytical"  # Careful, thoughtful decisions
    INTUITIVE = "intuitive"  # Emotion-based decisions
    STRATEGIC = "strategic"  # Long-term planning focused
    CAUTIOUS = "cautious"  # Risk-averse, safe choices
    ADVENTUROUS = "adventurous"  # Risk-taking, bold choices


class InteractionStyle(Enum):
    """User interaction patterns."""

    ACTIVE_PARTICIPANT = "active"  # Highly engaged, detailed responses
    PASSIVE_OBSERVER = "passive"  # Minimal input, follows story
    MIXED_ENGAGEMENT = "mixed"  # Varies between active and passive
    CREATIVE_COLLABORATOR = "creative"  # Adds creative elements
    GOAL_ORIENTED = "goal_oriented"  # Focused on objectives
    EXPLORATORY = "exploratory"  # Enjoys world exploration


class NarrativePreference(Enum):
    """User narrative style preferences."""

    CHARACTER_DRIVEN = "character_driven"  # Focus on character development
    PLOT_DRIVEN = "plot_driven"  # Focus on story progression
    WORLD_EXPLORATION = "world_exploration"  # Focus on world discovery
    DIALOGUE_HEAVY = "dialogue_heavy"  # Enjoys conversations
    ACTION_ORIENTED = "action_oriented"  # Prefers action sequences
    MYSTERY_SOLVING = "mystery_solving"  # Enjoys puzzles and mysteries


@dataclass
class UserBehaviorPattern:
    """Defines specific user behavior patterns for simulation."""

    decision_making_style: DecisionMakingStyle
    interaction_style: InteractionStyle
    narrative_preference: NarrativePreference

    # Timing characteristics
    min_thinking_time: float = 2.0  # Minimum seconds between responses
    max_thinking_time: float = 30.0  # Maximum seconds between responses
    response_length_preference: str = "medium"  # short, medium, long

    # Engagement patterns
    engagement_consistency: float = 0.8  # 0-1, how consistent engagement is
    attention_span_turns: int = 15  # How many turns before engagement may drop

    # Choice preferences
    risk_tolerance: float = 0.5  # 0-1, willingness to take risks
    creativity_level: float = 0.6  # 0-1, tendency to add creative elements
    goal_focus: float = 0.7  # 0-1, focus on achieving objectives


@dataclass
class SimulatedUserProfile:
    """
    Comprehensive simulated user profile for extended session testing.

    Combines demographic information, therapeutic profile, and behavioral
    patterns to create realistic user simulation for testing.
    """

    name: str
    description: str

    # Demographics (anonymized)
    age_range: str
    gaming_experience: str
    tech_comfort: str
    time_availability: str

    # Therapeutic profile
    primary_concerns: list[str]
    comfort_zones: list[str]
    challenge_areas: list[str]
    preferred_intensity: str
    therapeutic_goals: list[str]

    # Behavioral patterns
    behavior_pattern: UserBehaviorPattern

    # Session preferences
    preferred_session_length: int = 45  # minutes
    preferred_turn_count: int = 25  # turns per session
    break_frequency: int = 10  # turns between breaks

    # Response patterns
    response_templates: dict[str, list[str]] = field(default_factory=dict)
    choice_preferences: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize response templates and choice preferences."""
        self._initialize_response_templates()
        self._initialize_choice_preferences()

    def _initialize_response_templates(self):
        """Initialize response templates based on behavior pattern."""
        style = self.behavior_pattern.interaction_style

        if style == InteractionStyle.ACTIVE_PARTICIPANT:
            self.response_templates = {
                "exploration": [
                    "I want to explore the {location} more thoroughly.",
                    "Let me investigate {object} to understand it better.",
                    "I'm curious about {character}'s background and motivations.",
                ],
                "decision": [
                    "I think we should {action} because {reasoning}.",
                    "After considering the options, I believe {choice} is best.",
                    "Let me weigh the consequences before deciding on {action}.",
                ],
                "dialogue": [
                    "I'd like to ask {character} about {topic}.",
                    "Let me share my thoughts on {subject} with {character}.",
                    "I want to understand {character}'s perspective on {issue}.",
                ],
            }
        elif style == InteractionStyle.PASSIVE_OBSERVER:
            self.response_templates = {
                "exploration": [
                    "I'll follow along.",
                    "Let's see what happens.",
                    "I'm ready to continue.",
                ],
                "decision": [
                    "I'll go with the first option.",
                    "Whatever seems best.",
                    "I trust your judgment.",
                ],
                "dialogue": ["Okay.", "I see.", "That makes sense."],
            }
        else:  # Mixed or other styles
            self.response_templates = {
                "exploration": [
                    "Let's check out {location}.",
                    "I'm interested in {object}.",
                    "What about {character}?",
                ],
                "decision": [
                    "I think {choice} could work.",
                    "Let's try {action}.",
                    "Maybe we should {alternative}.",
                ],
                "dialogue": [
                    "Tell me more about {topic}.",
                    "What do you think about {subject}?",
                    "I'd like to know {information}.",
                ],
            }

    def _initialize_choice_preferences(self):
        """Initialize choice preferences based on behavior pattern."""
        pattern = self.behavior_pattern

        # Base preferences on decision-making style
        if pattern.decision_making_style == DecisionMakingStyle.ADVENTUROUS:
            self.choice_preferences = {
                "risk_taking": 0.8,
                "exploration": 0.9,
                "confrontation": 0.7,
                "helping_others": 0.6,
                "creative_solutions": 0.8,
            }
        elif pattern.decision_making_style == DecisionMakingStyle.CAUTIOUS:
            self.choice_preferences = {
                "risk_taking": 0.2,
                "exploration": 0.4,
                "confrontation": 0.3,
                "helping_others": 0.8,
                "creative_solutions": 0.5,
            }
        elif pattern.decision_making_style == DecisionMakingStyle.ANALYTICAL:
            self.choice_preferences = {
                "risk_taking": 0.4,
                "exploration": 0.7,
                "confrontation": 0.5,
                "helping_others": 0.7,
                "creative_solutions": 0.6,
            }
        else:  # Default balanced preferences
            self.choice_preferences = {
                "risk_taking": 0.5,
                "exploration": 0.6,
                "confrontation": 0.5,
                "helping_others": 0.7,
                "creative_solutions": 0.6,
            }

    def get_thinking_time(self, decision_complexity: str) -> float:
        """
        Calculate realistic thinking time based on decision complexity and user behavior.

        Args:
            decision_complexity: 'simple', 'moderate', 'complex'

        Returns:
            Thinking time in seconds
        """
        base_time = self.behavior_pattern.min_thinking_time
        max_time = self.behavior_pattern.max_thinking_time

        # Adjust based on decision-making style
        style = self.behavior_pattern.decision_making_style
        if style == DecisionMakingStyle.IMPULSIVE:
            multiplier = 0.3
        elif style == DecisionMakingStyle.ANALYTICAL:
            multiplier = 1.5
        elif style == DecisionMakingStyle.CAUTIOUS:
            multiplier = 1.2
        else:
            multiplier = 1.0

        # Adjust based on complexity
        complexity_multipliers = {"simple": 0.5, "moderate": 1.0, "complex": 2.0}
        complexity_mult = complexity_multipliers.get(decision_complexity, 1.0)

        # Calculate final thinking time with some randomness
        thinking_time = base_time * multiplier * complexity_mult
        thinking_time += random.uniform(0, max_time - thinking_time) * 0.3

        return min(max(thinking_time, base_time), max_time)

    def generate_response(self, context: dict[str, Any], turn: int) -> str:
        """
        Generate a realistic user response based on context and behavior pattern.

        Args:
            context: Current story context and available choices
            turn: Current turn number

        Returns:
            Simulated user response
        """
        response_type = self._determine_response_type(context, turn)
        templates = self.response_templates.get(response_type, ["I continue."])

        # Select template based on behavior pattern
        if self.behavior_pattern.creativity_level > 0.7:
            # High creativity - modify templates
            template = random.choice(templates)
            response = self._add_creative_elements(template, context)
        else:
            # Standard response
            template = random.choice(templates)
            response = self._fill_template(template, context)

        return response

    def _determine_response_type(self, context: dict[str, Any], turn: int) -> str:
        """Determine the type of response based on context."""
        # Simple logic - would be more sophisticated in full implementation
        if "choices" in context:
            return "decision"
        if "character" in context:
            return "dialogue"
        return "exploration"

    def _fill_template(self, template: str, context: dict[str, Any]) -> str:
        """Fill template with context information."""
        # Simple template filling - would be more sophisticated in full implementation
        filled = template
        for key, value in context.items():
            if f"{{{key}}}" in filled:
                filled = filled.replace(f"{{{key}}}", str(value))
        return filled

    def _add_creative_elements(self, template: str, context: dict[str, Any]) -> str:
        """Add creative elements to response for high-creativity users."""
        base_response = self._fill_template(template, context)

        # Add creative flourishes based on narrative preference
        if (
            self.behavior_pattern.narrative_preference
            == NarrativePreference.CHARACTER_DRIVEN
        ):
            creative_additions = [
                " I wonder what motivates this character.",
                " There's something deeper here I want to understand.",
                " This reminds me of someone I once knew.",
            ]
        elif (
            self.behavior_pattern.narrative_preference
            == NarrativePreference.WORLD_EXPLORATION
        ):
            creative_additions = [
                " I'm fascinated by the history of this place.",
                " The atmosphere here tells a story of its own.",
                " I want to understand how this world works.",
            ]
        else:
            creative_additions = [
                " This is intriguing.",
                " I have a feeling about this.",
                " Something tells me this is important.",
            ]

        if random.random() < self.behavior_pattern.creativity_level:
            base_response += random.choice(creative_additions)

        return base_response

    def should_take_break(self, turn: int) -> bool:
        """Determine if user should take a break based on behavior pattern."""
        if turn % self.break_frequency == 0:
            # Factor in attention span and engagement consistency
            break_probability = 1.0 - self.behavior_pattern.engagement_consistency
            if turn > self.behavior_pattern.attention_span_turns:
                break_probability *= 1.5

            return random.random() < break_probability

        return False

    def get_choice_preference_score(self, choice_type: str) -> float:
        """Get preference score for a specific choice type."""
        return self.choice_preferences.get(choice_type, 0.5)


class SimulatedUserProfileFactory:
    """Factory for creating predefined simulated user profiles."""

    @staticmethod
    def create_diverse_profiles() -> list[SimulatedUserProfile]:
        """Create a diverse set of user profiles for testing."""
        profiles = []

        # Active participant profile
        active_pattern = UserBehaviorPattern(
            decision_making_style=DecisionMakingStyle.ANALYTICAL,
            interaction_style=InteractionStyle.ACTIVE_PARTICIPANT,
            narrative_preference=NarrativePreference.CHARACTER_DRIVEN,
            engagement_consistency=0.9,
            creativity_level=0.7,
            attention_span_turns=100,
        )
        profiles.append(
            SimulatedUserProfile(
                name="active_participant",
                description="Highly engaged user with detailed responses",
                age_range="25-35",
                gaming_experience="moderate",
                tech_comfort="high",
                time_availability="flexible",
                primary_concerns=["personal_growth", "stress_management"],
                comfort_zones=["character_development", "dialogue"],
                challenge_areas=["conflict_resolution"],
                preferred_intensity="moderate",
                therapeutic_goals=["self_reflection", "emotional_awareness"],
                behavior_pattern=active_pattern,
                break_frequency=50,
            )
        )

        # Passive observer profile
        passive_pattern = UserBehaviorPattern(
            decision_making_style=DecisionMakingStyle.CAUTIOUS,
            interaction_style=InteractionStyle.PASSIVE_OBSERVER,
            narrative_preference=NarrativePreference.PLOT_DRIVEN,
            engagement_consistency=0.6,
            creativity_level=0.3,
            attention_span_turns=30,
        )
        profiles.append(
            SimulatedUserProfile(
                name="passive_observer",
                description="Minimal input user who follows the story",
                age_range="18-25",
                gaming_experience="low",
                tech_comfort="moderate",
                time_availability="limited",
                primary_concerns=["anxiety", "social_comfort"],
                comfort_zones=["observation", "simple_choices"],
                challenge_areas=["active_participation"],
                preferred_intensity="low",
                therapeutic_goals=["comfort_building", "gradual_engagement"],
                behavior_pattern=passive_pattern,
                break_frequency=20,
            )
        )

        # Creative collaborator profile
        creative_pattern = UserBehaviorPattern(
            decision_making_style=DecisionMakingStyle.INTUITIVE,
            interaction_style=InteractionStyle.CREATIVE_COLLABORATOR,
            narrative_preference=NarrativePreference.WORLD_EXPLORATION,
            engagement_consistency=0.8,
            creativity_level=0.9,
            attention_span_turns=80,
        )
        profiles.append(
            SimulatedUserProfile(
                name="creative_collaborator",
                description="Creative user who adds imaginative elements",
                age_range="20-30",
                gaming_experience="high",
                tech_comfort="high",
                time_availability="flexible",
                primary_concerns=["creative_expression", "exploration"],
                comfort_zones=["world_building", "character_creation"],
                challenge_areas=["structured_narratives"],
                preferred_intensity="high",
                therapeutic_goals=["creative_outlet", "self_expression"],
                behavior_pattern=creative_pattern,
                break_frequency=40,
            )
        )

        # Goal-oriented profile
        goal_pattern = UserBehaviorPattern(
            decision_making_style=DecisionMakingStyle.STRATEGIC,
            interaction_style=InteractionStyle.GOAL_ORIENTED,
            narrative_preference=NarrativePreference.ACTION_ORIENTED,
            engagement_consistency=0.9,
            creativity_level=0.5,
            attention_span_turns=120,
        )
        profiles.append(
            SimulatedUserProfile(
                name="goal_oriented",
                description="Focused user who pursues objectives efficiently",
                age_range="30-40",
                gaming_experience="moderate",
                tech_comfort="high",
                time_availability="structured",
                primary_concerns=["achievement", "progress"],
                comfort_zones=["clear_objectives", "strategic_planning"],
                challenge_areas=["open_ended_exploration"],
                preferred_intensity="moderate",
                therapeutic_goals=["goal_achievement", "confidence_building"],
                behavior_pattern=goal_pattern,
                break_frequency=60,
            )
        )

        # Exploratory profile
        explorer_pattern = UserBehaviorPattern(
            decision_making_style=DecisionMakingStyle.ADVENTUROUS,
            interaction_style=InteractionStyle.EXPLORATORY,
            narrative_preference=NarrativePreference.MYSTERY_SOLVING,
            engagement_consistency=0.7,
            creativity_level=0.8,
            attention_span_turns=90,
        )
        profiles.append(
            SimulatedUserProfile(
                name="exploratory",
                description="Curious user who enjoys discovering new elements",
                age_range="22-32",
                gaming_experience="high",
                tech_comfort="moderate",
                time_availability="flexible",
                primary_concerns=["curiosity", "discovery"],
                comfort_zones=["exploration", "mystery_solving"],
                challenge_areas=["linear_narratives"],
                preferred_intensity="moderate",
                therapeutic_goals=["curiosity_satisfaction", "problem_solving"],
                behavior_pattern=explorer_pattern,
                break_frequency=45,
            )
        )

        return profiles

    @staticmethod
    def create_marathon_user() -> SimulatedUserProfile:
        """Create a user profile optimized for ultra-long sessions."""
        marathon_pattern = UserBehaviorPattern(
            decision_making_style=DecisionMakingStyle.STRATEGIC,
            interaction_style=InteractionStyle.MIXED_ENGAGEMENT,
            narrative_preference=NarrativePreference.CHARACTER_DRIVEN,
            engagement_consistency=0.8,
            creativity_level=0.6,
            attention_span_turns=200,  # Very high attention span
        )
        return SimulatedUserProfile(
            name="marathon_user",
            description="Endurance user optimized for ultra-long sessions",
            age_range="25-40",
            gaming_experience="high",
            tech_comfort="high",
            time_availability="extensive",
            primary_concerns=["long_term_engagement", "narrative_depth"],
            comfort_zones=["extended_sessions", "complex_narratives"],
            challenge_areas=["short_interactions"],
            preferred_intensity="moderate",
            therapeutic_goals=["deep_exploration", "sustained_engagement"],
            behavior_pattern=marathon_pattern,
            break_frequency=100,  # Less frequent breaks
        )

    @staticmethod
    def create_typical_user() -> SimulatedUserProfile:
        """Create a typical user profile for baseline testing."""
        typical_pattern = UserBehaviorPattern(
            decision_making_style=DecisionMakingStyle.ANALYTICAL,
            interaction_style=InteractionStyle.ACTIVE_PARTICIPANT,
            narrative_preference=NarrativePreference.PLOT_DRIVEN,
            engagement_consistency=0.7,
            creativity_level=0.5,
            attention_span_turns=60,
        )
        return SimulatedUserProfile(
            name="typical_user",
            description="Baseline user profile for standard testing",
            age_range="25-35",
            gaming_experience="moderate",
            tech_comfort="moderate",
            time_availability="moderate",
            primary_concerns=["general_wellness", "entertainment"],
            comfort_zones=["familiar_scenarios", "moderate_complexity"],
            challenge_areas=["extreme_scenarios"],
            preferred_intensity="moderate",
            therapeutic_goals=["relaxation", "mild_engagement"],
            behavior_pattern=typical_pattern,
            break_frequency=30,
        )
