"""
Character Development System for Core Gameplay Loop

This module provides character growth, attribute tracking, milestone detection,
and progression visualization for enhanced user engagement and therapeutic progress representation.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from src.components.gameplay_loop.models.core import (
    ChoiceType,
)
from src.components.gameplay_loop.services.session_state import SessionState

from .events import EventBus, EventType, NarrativeEvent

logger = logging.getLogger(__name__)


class CharacterAttribute(str, Enum):
    """Core character attributes that can develop over time."""

    COURAGE = "courage"
    WISDOM = "wisdom"
    COMPASSION = "compassion"
    RESILIENCE = "resilience"
    COMMUNICATION = "communication"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    PROBLEM_SOLVING = "problem_solving"
    SELF_AWARENESS = "self_awareness"
    LEADERSHIP = "leadership"
    CREATIVITY = "creativity"
    PATIENCE = "patience"
    DETERMINATION = "determination"


class CharacterMilestone(str, Enum):
    """Types of character development milestones."""

    FIRST_BRAVE_ACT = "first_brave_act"
    WISE_DECISION_MAKER = "wise_decision_maker"
    COMPASSIONATE_HELPER = "compassionate_helper"
    RESILIENT_SURVIVOR = "resilient_survivor"
    SKILLED_COMMUNICATOR = "skilled_communicator"
    EMOTIONALLY_AWARE = "emotionally_aware"
    CREATIVE_PROBLEM_SOLVER = "creative_problem_solver"
    SELF_REFLECTIVE_INDIVIDUAL = "self_reflective_individual"
    INSPIRING_LEADER = "inspiring_leader"
    PATIENT_GUIDE = "patient_guide"
    DETERMINED_ACHIEVER = "determined_achiever"
    MASTER_OF_SKILLS = "master_of_skills"


class DevelopmentTrigger(str, Enum):
    """Triggers for character development."""

    CHOICE_CONSEQUENCE = "choice_consequence"
    THERAPEUTIC_PROGRESS = "therapeutic_progress"
    SKILL_DEMONSTRATION = "skill_demonstration"
    MILESTONE_ACHIEVEMENT = "milestone_achievement"
    STORY_EVENT = "story_event"
    REPEATED_BEHAVIOR = "repeated_behavior"
    CHALLENGE_OVERCOME = "challenge_overcome"
    LEARNING_MOMENT = "learning_moment"


class AbilityType(str, Enum):
    """Types of abilities characters can unlock."""

    THERAPEUTIC_SKILL = "therapeutic_skill"
    SOCIAL_ABILITY = "social_ability"
    PROBLEM_SOLVING_TECHNIQUE = "problem_solving_technique"
    EMOTIONAL_REGULATION_TOOL = "emotional_regulation_tool"
    COMMUNICATION_STYLE = "communication_style"
    LEADERSHIP_APPROACH = "leadership_approach"
    CREATIVE_METHOD = "creative_method"
    COPING_STRATEGY = "coping_strategy"


@dataclass
class CharacterAttributeLevel:
    """Represents the level and progress of a character attribute."""

    attribute: CharacterAttribute = CharacterAttribute.COURAGE
    current_level: float = 0.0  # 0.0-10.0 scale
    experience_points: int = 0
    level_progress: float = 0.0  # Progress toward next level (0.0-1.0)

    # Development tracking
    last_increased: datetime | None = None
    development_rate: float = 0.0  # Average increase per session
    peak_level: float = 0.0  # Highest level achieved

    # Story integration
    story_manifestations: list[str] = field(default_factory=list)
    character_reactions: list[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CharacterAbility:
    """Represents an ability or skill the character has unlocked."""

    ability_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    ability_type: AbilityType = AbilityType.THERAPEUTIC_SKILL

    # Requirements and unlocking
    required_attributes: dict[CharacterAttribute, float] = field(default_factory=dict)
    unlock_trigger: DevelopmentTrigger = DevelopmentTrigger.MILESTONE_ACHIEVEMENT
    unlock_condition: str = ""

    # Usage and effectiveness
    usage_count: int = 0
    effectiveness_rating: float = 0.0  # 0.0-1.0
    last_used: datetime | None = None

    # Story integration
    unlock_story: str = ""
    usage_examples: list[str] = field(default_factory=list)
    character_dialogue: list[str] = field(default_factory=list)

    # Metadata
    unlocked_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class CharacterMilestoneAchievement:
    """Records achievement of a character development milestone."""

    achievement_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    session_id: str = ""

    # Milestone details
    milestone: CharacterMilestone = CharacterMilestone.FIRST_BRAVE_ACT
    trigger: DevelopmentTrigger = DevelopmentTrigger.CHOICE_CONSEQUENCE

    # Achievement context
    triggering_choice: str | None = None
    story_context: str = ""
    attribute_levels_at_achievement: dict[CharacterAttribute, float] = field(
        default_factory=dict
    )

    # Recognition and celebration
    celebration_story: str = ""
    character_recognition: str = ""
    new_abilities_unlocked: list[str] = field(default_factory=list)

    # Impact
    attribute_bonuses: dict[CharacterAttribute, float] = field(default_factory=dict)
    story_unlocks: list[str] = field(default_factory=list)

    # Metadata
    achieved_at: datetime = field(default_factory=datetime.utcnow)
    celebration_shown: bool = False


@dataclass
class CharacterDevelopmentEvent:
    """Records a character development event."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    session_id: str = ""

    # Event details
    event_type: DevelopmentTrigger = DevelopmentTrigger.CHOICE_CONSEQUENCE
    description: str = ""

    # Attribute changes
    attribute_changes: dict[CharacterAttribute, float] = field(default_factory=dict)
    experience_gained: dict[CharacterAttribute, int] = field(default_factory=dict)

    # Story integration
    story_context: str = ""
    character_feedback: str = ""
    narrative_impact: str = ""

    # Metadata
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    processed: bool = False


class CharacterDevelopmentSystem:
    """Main system for character development, growth tracking, and milestone management."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

        # Character development tracking
        self.character_attributes: dict[
            str, dict[CharacterAttribute, CharacterAttributeLevel]
        ] = {}
        self.character_abilities: dict[str, list[CharacterAbility]] = {}
        self.milestone_achievements: dict[str, list[CharacterMilestoneAchievement]] = {}
        self.development_events: dict[str, list[CharacterDevelopmentEvent]] = {}

        # Development configuration
        self.attribute_templates = self._load_attribute_templates()
        self.ability_templates = self._load_ability_templates()
        self.milestone_templates = self._load_milestone_templates()
        self.development_rules = self._load_development_rules()

        # Progression parameters
        self.level_thresholds = [
            0,
            10,
            25,
            50,
            100,
            175,
            275,
            400,
            550,
            750,
            1000,
        ]  # XP needed for each level
        self.milestone_thresholds = self._load_milestone_thresholds()
        self.ability_unlock_conditions = self._load_ability_unlock_conditions()

        # Metrics
        self.metrics = {
            "attribute_increases": 0,
            "abilities_unlocked": 0,
            "milestones_achieved": 0,
            "development_events_processed": 0,
            "character_celebrations": 0,
        }

    def _load_attribute_templates(self) -> dict[CharacterAttribute, dict[str, Any]]:
        """Load character attribute templates and descriptions."""
        return {
            CharacterAttribute.COURAGE: {
                "name": "Courage",
                "description": "The ability to face fears and take brave actions despite uncertainty",
                "story_manifestations": [
                    "Standing up for what's right even when it's difficult",
                    "Facing challenging situations with determination",
                    "Taking risks for personal growth and helping others",
                ],
                "development_indicators": [
                    "Making difficult but necessary choices",
                    "Confronting fears and anxieties",
                    "Taking initiative in challenging situations",
                ],
            },
            CharacterAttribute.WISDOM: {
                "name": "Wisdom",
                "description": "The ability to make sound judgments and learn from experience",
                "story_manifestations": [
                    "Offering thoughtful advice to other characters",
                    "Learning from mistakes and applying lessons",
                    "Seeing the bigger picture in complex situations",
                ],
                "development_indicators": [
                    "Reflecting on experiences and extracting insights",
                    "Making decisions based on long-term consequences",
                    "Helping others learn from their experiences",
                ],
            },
            CharacterAttribute.COMPASSION: {
                "name": "Compassion",
                "description": "The ability to understand and care for others' wellbeing",
                "story_manifestations": [
                    "Showing kindness and empathy to struggling characters",
                    "Putting others' needs before personal gain",
                    "Creating inclusive and supportive environments",
                ],
                "development_indicators": [
                    "Choosing to help others even at personal cost",
                    "Showing understanding for different perspectives",
                    "Creating positive outcomes for multiple characters",
                ],
            },
            CharacterAttribute.RESILIENCE: {
                "name": "Resilience",
                "description": "The ability to bounce back from setbacks and adapt to challenges",
                "story_manifestations": [
                    "Recovering quickly from failures and disappointments",
                    "Adapting strategies when initial approaches don't work",
                    "Maintaining hope and determination through difficulties",
                ],
                "development_indicators": [
                    "Persisting through multiple failed attempts",
                    "Finding alternative solutions when blocked",
                    "Maintaining positive attitude during setbacks",
                ],
            },
            CharacterAttribute.COMMUNICATION: {
                "name": "Communication",
                "description": "The ability to express ideas clearly and listen effectively",
                "story_manifestations": [
                    "Resolving conflicts through effective dialogue",
                    "Inspiring others with clear and compelling messages",
                    "Building bridges between different groups or perspectives",
                ],
                "development_indicators": [
                    "Successfully negotiating difficult conversations",
                    "Helping others understand complex ideas",
                    "Facilitating cooperation between conflicting parties",
                ],
            },
            CharacterAttribute.EMOTIONAL_INTELLIGENCE: {
                "name": "Emotional Intelligence",
                "description": "The ability to understand and manage emotions effectively",
                "story_manifestations": [
                    "Recognizing and responding appropriately to others' emotions",
                    "Managing personal emotional reactions in challenging situations",
                    "Creating emotionally supportive environments for others",
                ],
                "development_indicators": [
                    "Choosing emotional regulation over reactive responses",
                    "Helping others process difficult emotions",
                    "Maintaining emotional balance during stress",
                ],
            },
        }

    def _load_ability_templates(self) -> dict[AbilityType, list[dict[str, Any]]]:
        """Load ability templates for different ability types."""
        return {
            AbilityType.THERAPEUTIC_SKILL: [
                {
                    "name": "Mindful Breathing",
                    "description": "The ability to use breathing techniques to manage stress and anxiety",
                    "required_attributes": {
                        CharacterAttribute.EMOTIONAL_INTELLIGENCE: 3.0
                    },
                    "unlock_story": "Through practice and patience, you've learned to harness the power of breath to find calm in any storm.",
                    "usage_examples": [
                        "Using deep breathing before difficult conversations",
                        "Teaching breathing techniques to anxious characters",
                    ],
                },
                {
                    "name": "Cognitive Reframing",
                    "description": "The ability to challenge and reframe negative thought patterns",
                    "required_attributes": {
                        CharacterAttribute.WISDOM: 4.0,
                        CharacterAttribute.SELF_AWARENESS: 3.0,
                    },
                    "unlock_story": "Your growing wisdom allows you to see situations from multiple perspectives and help others do the same.",
                    "usage_examples": [
                        "Helping characters see challenges as opportunities",
                        "Reframing setbacks as learning experiences",
                    ],
                },
            ],
            AbilityType.SOCIAL_ABILITY: [
                {
                    "name": "Empathetic Listening",
                    "description": "The ability to truly hear and understand others' perspectives",
                    "required_attributes": {
                        CharacterAttribute.COMPASSION: 3.0,
                        CharacterAttribute.COMMUNICATION: 2.0,
                    },
                    "unlock_story": "Your compassionate heart and growing communication skills allow you to truly connect with others.",
                    "usage_examples": [
                        "Providing comfort to distressed characters",
                        "Mediating conflicts through understanding",
                    ],
                },
                {
                    "name": "Inspiring Leadership",
                    "description": "The ability to motivate and guide others toward positive outcomes",
                    "required_attributes": {
                        CharacterAttribute.LEADERSHIP: 4.0,
                        CharacterAttribute.COURAGE: 3.0,
                    },
                    "unlock_story": "Your courage and natural leadership abilities inspire others to believe in themselves and take positive action.",
                    "usage_examples": [
                        "Rallying characters to work together",
                        "Inspiring hope in difficult situations",
                    ],
                },
            ],
        }

    def _load_milestone_templates(self) -> dict[CharacterMilestone, dict[str, Any]]:
        """Load milestone templates and celebration stories."""
        return {
            CharacterMilestone.FIRST_BRAVE_ACT: {
                "name": "First Brave Act",
                "description": "Taking your first truly courageous action despite fear",
                "required_attributes": {CharacterAttribute.COURAGE: 2.0},
                "celebration_story": "The other characters notice a new strength in your bearing. Your first act of true courage has not gone unnoticed, and you feel a newfound confidence growing within you.",
                "attribute_bonuses": {
                    CharacterAttribute.COURAGE: 0.5,
                    CharacterAttribute.SELF_AWARENESS: 0.2,
                },
                "story_unlocks": [
                    "courage_based_story_paths",
                    "leadership_opportunities",
                ],
            },
            CharacterMilestone.WISE_DECISION_MAKER: {
                "name": "Wise Decision Maker",
                "description": "Consistently making thoughtful, well-considered decisions",
                "required_attributes": {CharacterAttribute.WISDOM: 3.0},
                "celebration_story": "Your reputation for wise counsel spreads among the characters. They begin seeking your advice, recognizing the depth of your insight and judgment.",
                "attribute_bonuses": {
                    CharacterAttribute.WISDOM: 0.5,
                    CharacterAttribute.LEADERSHIP: 0.3,
                },
                "story_unlocks": [
                    "advisor_role_opportunities",
                    "complex_decision_scenarios",
                ],
            },
            CharacterMilestone.COMPASSIONATE_HELPER: {
                "name": "Compassionate Helper",
                "description": "Consistently showing kindness and support to others",
                "required_attributes": {CharacterAttribute.COMPASSION: 3.0},
                "celebration_story": "Your kindness has touched many hearts. Characters speak of your compassion with gratitude, and you've become known as someone who truly cares.",
                "attribute_bonuses": {
                    CharacterAttribute.COMPASSION: 0.5,
                    CharacterAttribute.EMOTIONAL_INTELLIGENCE: 0.3,
                },
                "story_unlocks": [
                    "healing_role_opportunities",
                    "community_building_scenarios",
                ],
            },
        }

    def _load_development_rules(self) -> dict[str, Any]:
        """Load rules for character development progression."""
        return {
            "attribute_gain_rates": {
                "choice_consequence": 0.1,  # Base attribute gain from choice consequences
                "therapeutic_progress": 0.2,  # Gain from therapeutic milestone achievement
                "skill_demonstration": 0.15,  # Gain from successfully using skills
                "repeated_behavior": 0.05,  # Smaller gain for repeated positive behaviors
                "challenge_overcome": 0.25,  # Larger gain for overcoming significant challenges
            },
            "experience_multipliers": {
                "first_time": 2.0,  # Double XP for first time doing something
                "milestone_related": 1.5,  # 50% bonus for milestone-related actions
                "therapeutic_aligned": 1.3,  # 30% bonus for therapeutically aligned actions
                "story_significant": 1.2,  # 20% bonus for story-significant actions
            },
            "regression_rules": {
                "enabled": True,
                "max_regression": 0.5,  # Maximum attribute loss from negative events
                "recovery_multiplier": 1.2,  # Faster recovery after regression
                "story_explanation": "temporary setback that strengthens character through overcoming",
            },
        }

    def _load_milestone_thresholds(self) -> dict[CharacterMilestone, dict[str, Any]]:
        """Load thresholds and conditions for milestone achievement."""
        return {
            CharacterMilestone.FIRST_BRAVE_ACT: {
                "min_courage": 2.0,
                "required_actions": ["face_fear", "take_risk", "stand_up_for_others"],
                "story_contexts": [
                    "conflict_resolution",
                    "personal_challenge",
                    "helping_others",
                ],
            },
            CharacterMilestone.WISE_DECISION_MAKER: {
                "min_wisdom": 3.0,
                "required_actions": [
                    "thoughtful_choice",
                    "learn_from_mistake",
                    "give_advice",
                ],
                "consecutive_wise_decisions": 3,
            },
            CharacterMilestone.COMPASSIONATE_HELPER: {
                "min_compassion": 3.0,
                "required_actions": [
                    "help_others",
                    "show_empathy",
                    "sacrifice_for_others",
                ],
                "helping_actions_count": 5,
            },
        }

    def _load_ability_unlock_conditions(self) -> dict[str, dict[str, Any]]:
        """Load conditions for unlocking specific abilities."""
        return {
            "mindful_breathing": {
                "required_attributes": {CharacterAttribute.EMOTIONAL_INTELLIGENCE: 3.0},
                "required_milestones": [],
                "story_conditions": ["experienced_stress", "learned_coping"],
            },
            "cognitive_reframing": {
                "required_attributes": {
                    CharacterAttribute.WISDOM: 4.0,
                    CharacterAttribute.SELF_AWARENESS: 3.0,
                },
                "required_milestones": [CharacterMilestone.WISE_DECISION_MAKER],
                "story_conditions": [
                    "challenged_negative_thoughts",
                    "helped_others_reframe",
                ],
            },
            "empathetic_listening": {
                "required_attributes": {
                    CharacterAttribute.COMPASSION: 3.0,
                    CharacterAttribute.COMMUNICATION: 2.0,
                },
                "required_milestones": [CharacterMilestone.COMPASSIONATE_HELPER],
                "story_conditions": [
                    "listened_to_others",
                    "provided_emotional_support",
                ],
            },
        }

    async def process_character_development(
        self,
        session_state: SessionState,
        trigger: DevelopmentTrigger,
        context: dict[str, Any],
    ) -> CharacterDevelopmentEvent:
        """Process character development based on user actions and story events."""
        try:
            user_id = session_state.user_id

            # Create development event
            event = CharacterDevelopmentEvent(
                user_id=user_id,
                session_id=session_state.session_id,
                event_type=trigger,
                description=context.get(
                    "description", f"Character development triggered by {trigger.value}"
                ),
                story_context=context.get("story_context", ""),
            )

            # Initialize character attributes if needed
            if user_id not in self.character_attributes:
                await self._initialize_character_attributes(user_id)

            # Calculate attribute changes based on trigger and context
            attribute_changes = await self._calculate_attribute_changes(
                trigger, context, session_state
            )
            event.attribute_changes = attribute_changes

            # Apply attribute changes
            for attribute, change in attribute_changes.items():
                await self._apply_attribute_change(user_id, attribute, change, trigger)

            # Calculate experience gained
            experience_gained = await self._calculate_experience_gained(
                trigger, context, attribute_changes
            )
            event.experience_gained = experience_gained

            # Apply experience points
            for attribute, xp in experience_gained.items():
                await self._apply_experience_points(user_id, attribute, xp)

            # Generate character feedback
            event.character_feedback = await self._generate_character_feedback(
                attribute_changes, context
            )

            # Generate narrative impact
            event.narrative_impact = await self._generate_narrative_impact(
                attribute_changes, context
            )

            # Check for milestone achievements
            await self._check_milestone_achievements(user_id, session_state, event)

            # Check for ability unlocks
            await self._check_ability_unlocks(user_id, session_state, event)

            # Store development event
            if user_id not in self.development_events:
                self.development_events[user_id] = []

            self.development_events[user_id].append(event)
            event.processed = True

            # Update session context
            session_state.context["recent_character_development"] = {
                "event_id": event.event_id,
                "attribute_changes": {
                    attr.value: change for attr, change in attribute_changes.items()
                },
                "character_feedback": event.character_feedback,
                "narrative_impact": event.narrative_impact,
            }

            # Publish development event
            await self._publish_development_event(session_state, event)

            self.metrics["development_events_processed"] += 1

            return event

        except Exception as e:
            logger.error(
                f"Failed to process character development for user {session_state.user_id}: {e}"
            )
            # Return minimal event
            return CharacterDevelopmentEvent(
                user_id=session_state.user_id,
                session_id=session_state.session_id,
                event_type=trigger,
                description=f"Character development event: {trigger.value}",
            )

    async def _initialize_character_attributes(self, user_id: str) -> None:
        """Initialize character attributes for a new user."""
        self.character_attributes[user_id] = {}

        for attribute in CharacterAttribute:
            self.character_attributes[user_id][attribute] = CharacterAttributeLevel(
                attribute=attribute,
                current_level=1.0,  # Start at level 1
                experience_points=0,
                level_progress=0.0,
            )

    async def _calculate_attribute_changes(
        self,
        trigger: DevelopmentTrigger,
        context: dict[str, Any],
        session_state: SessionState,
    ) -> dict[CharacterAttribute, float]:
        """Calculate attribute changes based on trigger and context."""
        changes = {}

        # Get base gain rate for trigger type
        base_rate = self.development_rules["attribute_gain_rates"].get(
            trigger.value, 0.1
        )

        # Determine which attributes should be affected
        if trigger == DevelopmentTrigger.CHOICE_CONSEQUENCE:
            # Analyze choice to determine relevant attributes
            choice_type = context.get("choice_type")
            therapeutic_relevance = context.get("therapeutic_relevance", 0.5)

            if choice_type == ChoiceType.EMOTIONAL_REGULATION:
                changes[CharacterAttribute.EMOTIONAL_INTELLIGENCE] = (
                    base_rate * therapeutic_relevance
                )
                changes[CharacterAttribute.RESILIENCE] = (
                    base_rate * 0.5 * therapeutic_relevance
                )
            elif choice_type == ChoiceType.COMMUNICATION:
                changes[CharacterAttribute.COMMUNICATION] = (
                    base_rate * therapeutic_relevance
                )
                changes[CharacterAttribute.COMPASSION] = (
                    base_rate * 0.3 * therapeutic_relevance
                )
            elif choice_type == ChoiceType.PROBLEM_SOLVING:
                changes[CharacterAttribute.PROBLEM_SOLVING] = (
                    base_rate * therapeutic_relevance
                )
                changes[CharacterAttribute.WISDOM] = (
                    base_rate * 0.4 * therapeutic_relevance
                )
            elif choice_type == ChoiceType.SELF_REFLECTION:
                changes[CharacterAttribute.SELF_AWARENESS] = (
                    base_rate * therapeutic_relevance
                )
                changes[CharacterAttribute.WISDOM] = (
                    base_rate * 0.3 * therapeutic_relevance
                )
            else:
                # Default attribute gains for other choice types
                changes[CharacterAttribute.WISDOM] = base_rate * 0.5
                changes[CharacterAttribute.SELF_AWARENESS] = base_rate * 0.3

        elif trigger == DevelopmentTrigger.THERAPEUTIC_PROGRESS:
            # Therapeutic progress affects multiple attributes
            therapeutic_concept = context.get("therapeutic_concept", "")
            progress_level = context.get("progress_level", 0.5)

            if "anxiety" in therapeutic_concept.lower():
                changes[CharacterAttribute.RESILIENCE] = base_rate * progress_level
                changes[CharacterAttribute.EMOTIONAL_INTELLIGENCE] = (
                    base_rate * 0.7 * progress_level
                )
            elif "communication" in therapeutic_concept.lower():
                changes[CharacterAttribute.COMMUNICATION] = base_rate * progress_level
                changes[CharacterAttribute.COMPASSION] = (
                    base_rate * 0.5 * progress_level
                )
            elif "emotional" in therapeutic_concept.lower():
                changes[CharacterAttribute.EMOTIONAL_INTELLIGENCE] = (
                    base_rate * progress_level
                )
                changes[CharacterAttribute.SELF_AWARENESS] = (
                    base_rate * 0.6 * progress_level
                )
            else:
                # General therapeutic progress
                changes[CharacterAttribute.WISDOM] = base_rate * progress_level
                changes[CharacterAttribute.RESILIENCE] = (
                    base_rate * 0.5 * progress_level
                )

        elif trigger == DevelopmentTrigger.CHALLENGE_OVERCOME:
            # Overcoming challenges builds resilience and courage
            challenge_difficulty = context.get("challenge_difficulty", 0.5)
            changes[CharacterAttribute.RESILIENCE] = base_rate * challenge_difficulty
            changes[CharacterAttribute.COURAGE] = base_rate * 0.8 * challenge_difficulty
            changes[CharacterAttribute.DETERMINATION] = (
                base_rate * 0.6 * challenge_difficulty
            )

        elif trigger == DevelopmentTrigger.SKILL_DEMONSTRATION:
            # Skill demonstration affects related attributes
            skill_type = context.get("skill_type", "general")
            effectiveness = context.get("effectiveness", 0.5)

            if skill_type == "communication":
                changes[CharacterAttribute.COMMUNICATION] = base_rate * effectiveness
            elif skill_type == "emotional_regulation":
                changes[CharacterAttribute.EMOTIONAL_INTELLIGENCE] = (
                    base_rate * effectiveness
                )
            elif skill_type == "problem_solving":
                changes[CharacterAttribute.PROBLEM_SOLVING] = base_rate * effectiveness
            else:
                changes[CharacterAttribute.WISDOM] = base_rate * effectiveness

        # Apply multipliers
        multipliers = self.development_rules["experience_multipliers"]

        if context.get("first_time", False):
            for attr in changes:
                changes[attr] *= multipliers["first_time"]

        if context.get("milestone_related", False):
            for attr in changes:
                changes[attr] *= multipliers["milestone_related"]

        if context.get("therapeutic_aligned", False):
            for attr in changes:
                changes[attr] *= multipliers["therapeutic_aligned"]

        return changes

    async def _apply_attribute_change(
        self,
        user_id: str,
        attribute: CharacterAttribute,
        change: float,
        trigger: DevelopmentTrigger,
    ) -> None:
        """Apply attribute change to character."""
        if user_id not in self.character_attributes:
            await self._initialize_character_attributes(user_id)

        attr_level = self.character_attributes[user_id][attribute]

        # Apply change
        attr_level.current_level = max(
            0.0, min(10.0, attr_level.current_level + change)
        )

        # Update peak level
        attr_level.peak_level = max(attr_level.peak_level, attr_level.current_level)

        # Update development rate
        if attr_level.last_increased:
            time_diff = datetime.utcnow() - attr_level.last_increased
            if time_diff.total_seconds() > 0:
                attr_level.development_rate = change / (
                    time_diff.total_seconds() / 3600
                )  # Per hour

        attr_level.last_increased = datetime.utcnow()
        attr_level.last_updated = datetime.utcnow()

        # Add story manifestation
        if change > 0:
            template = self.attribute_templates.get(attribute, {})
            manifestations = template.get("story_manifestations", [])
            if manifestations:
                attr_level.story_manifestations.append(manifestations[0])

        if change > 0:
            self.metrics["attribute_increases"] += 1

    async def _calculate_experience_gained(
        self,
        trigger: DevelopmentTrigger,
        context: dict[str, Any],
        attribute_changes: dict[CharacterAttribute, float],
    ) -> dict[CharacterAttribute, int]:
        """Calculate experience points gained for each attribute."""
        experience = {}

        base_xp = 10  # Base XP per development event

        for attribute, change in attribute_changes.items():
            # XP proportional to attribute change
            xp = int(base_xp * change * 10)  # Scale up for meaningful XP values

            # Apply multipliers
            if context.get("first_time", False):
                xp = int(xp * 2.0)

            if context.get("milestone_related", False):
                xp = int(xp * 1.5)

            experience[attribute] = max(1, xp)  # Minimum 1 XP

        return experience

    async def _apply_experience_points(
        self, user_id: str, attribute: CharacterAttribute, xp: int
    ) -> None:
        """Apply experience points and handle level ups."""
        if user_id not in self.character_attributes:
            await self._initialize_character_attributes(user_id)

        attr_level = self.character_attributes[user_id][attribute]
        attr_level.experience_points += xp

        # Check for level up
        current_level_index = int(attr_level.current_level)
        if current_level_index < len(self.level_thresholds) - 1:
            next_level_threshold = self.level_thresholds[current_level_index]

            if attr_level.experience_points >= next_level_threshold:
                # Level up!
                attr_level.current_level = float(current_level_index + 1)
                attr_level.level_progress = 0.0

                # Add character reaction for level up
                template = self.attribute_templates.get(attribute, {})
                attr_name = template.get("name", attribute.value)
                attr_level.character_reactions.append(
                    f"You feel your {attr_name.lower()} growing stronger through your experiences and choices."
                )
            else:
                # Update progress toward next level
                current_level_threshold = (
                    self.level_thresholds[current_level_index - 1]
                    if current_level_index > 0
                    else 0
                )
                progress = (attr_level.experience_points - current_level_threshold) / (
                    next_level_threshold - current_level_threshold
                )
                attr_level.level_progress = min(1.0, progress)

    async def _generate_character_feedback(
        self,
        attribute_changes: dict[CharacterAttribute, float],
        context: dict[str, Any],
    ) -> str:
        """Generate character feedback for development event."""
        if not attribute_changes:
            return "Your character reflects on the recent experience."

        # Find the attribute with the largest change
        primary_attribute = max(
            attribute_changes.keys(), key=lambda attr: attribute_changes[attr]
        )
        primary_change = attribute_changes[primary_attribute]

        template = self.attribute_templates.get(primary_attribute, {})
        attr_name = template.get("name", primary_attribute.value)

        if primary_change > 0.2:
            return f"You feel a significant growth in your {attr_name.lower()}. This experience has strengthened an important part of who you are."
        elif primary_change > 0.1:
            return f"Your {attr_name.lower()} develops through this experience. You notice yourself becoming more capable."
        elif primary_change > 0.05:
            return f"You sense a subtle improvement in your {attr_name.lower()}. Small steps forward are still progress."
        else:
            return f"This experience contributes to your ongoing development in {attr_name.lower()}."

    async def _generate_narrative_impact(
        self,
        attribute_changes: dict[CharacterAttribute, float],
        context: dict[str, Any],
    ) -> str:
        """Generate narrative impact description for development event."""
        if not attribute_changes:
            return "The story continues to unfold around your character's journey."

        # Find the most significant attribute change
        primary_attribute = max(
            attribute_changes.keys(), key=lambda attr: attribute_changes[attr]
        )
        primary_change = attribute_changes[primary_attribute]

        template = self.attribute_templates.get(primary_attribute, {})
        manifestations = template.get("story_manifestations", [])

        if manifestations and primary_change > 0.1:
            return f"Other characters begin to notice your growing {primary_attribute.value.replace('_', ' ')}. {manifestations[0]}"
        else:
            return f"Your character's development in {primary_attribute.value.replace('_', ' ')} subtly influences the story around you."

    async def _check_milestone_achievements(
        self,
        user_id: str,
        session_state: SessionState,
        event: CharacterDevelopmentEvent,
    ) -> None:
        """Check for milestone achievements and create celebrations."""
        user_attributes = self.character_attributes.get(user_id, {})

        # Get existing milestone achievements
        existing_milestones = set()
        if user_id in self.milestone_achievements:
            existing_milestones = {
                achievement.milestone
                for achievement in self.milestone_achievements[user_id]
            }

        # Check each milestone
        for milestone, template in self.milestone_templates.items():
            if milestone in existing_milestones:
                continue  # Already achieved

            # Check if milestone requirements are met
            if await self._check_milestone_requirements(
                milestone, template, user_attributes, event
            ):
                await self._achieve_milestone(
                    user_id, session_state, milestone, template, event
                )

    async def _check_milestone_requirements(
        self,
        milestone: CharacterMilestone,
        template: dict[str, Any],
        user_attributes: dict[CharacterAttribute, CharacterAttributeLevel],
        event: CharacterDevelopmentEvent,
    ) -> bool:
        """Check if milestone requirements are satisfied."""
        # Check required attributes
        required_attributes = template.get("required_attributes", {})
        for attr, min_level in required_attributes.items():
            if (
                attr not in user_attributes
                or user_attributes[attr].current_level < min_level
            ):
                return False

        # Check milestone-specific conditions
        self.milestone_thresholds.get(milestone, {})

        if milestone == CharacterMilestone.FIRST_BRAVE_ACT:
            # Check if this event involved courage
            if CharacterAttribute.COURAGE in event.attribute_changes:
                courage_change = event.attribute_changes[CharacterAttribute.COURAGE]
                if courage_change > 0.1:  # Significant courage development
                    return True

        elif milestone == CharacterMilestone.WISE_DECISION_MAKER:
            # Check for wisdom development and decision-making context
            if CharacterAttribute.WISDOM in event.attribute_changes:
                wisdom_change = event.attribute_changes[CharacterAttribute.WISDOM]
                if wisdom_change > 0.1 and "decision" in event.story_context.lower():
                    return True

        elif milestone == CharacterMilestone.COMPASSIONATE_HELPER:
            # Check for compassion development and helping context
            if CharacterAttribute.COMPASSION in event.attribute_changes:
                compassion_change = event.attribute_changes[
                    CharacterAttribute.COMPASSION
                ]
                if compassion_change > 0.1 and (
                    "help" in event.story_context.lower()
                    or "support" in event.story_context.lower()
                ):
                    return True

        return False

    async def _achieve_milestone(
        self,
        user_id: str,
        session_state: SessionState,
        milestone: CharacterMilestone,
        template: dict[str, Any],
        triggering_event: CharacterDevelopmentEvent,
    ) -> None:
        """Process milestone achievement."""
        try:
            # Create milestone achievement record
            achievement = CharacterMilestoneAchievement(
                user_id=user_id,
                session_id=session_state.session_id,
                milestone=milestone,
                trigger=triggering_event.event_type,
                triggering_choice=triggering_event.description,
                story_context=triggering_event.story_context,
                attribute_levels_at_achievement={
                    attr: level.current_level
                    for attr, level in self.character_attributes[user_id].items()
                },
                celebration_story=template.get("celebration_story", ""),
                character_recognition=f"Achievement unlocked: {template.get('name', milestone.value)}",
                attribute_bonuses=template.get("attribute_bonuses", {}),
                story_unlocks=template.get("story_unlocks", []),
            )

            # Apply attribute bonuses
            for attr, bonus in achievement.attribute_bonuses.items():
                await self._apply_attribute_change(
                    user_id, attr, bonus, DevelopmentTrigger.MILESTONE_ACHIEVEMENT
                )

            # Store achievement
            if user_id not in self.milestone_achievements:
                self.milestone_achievements[user_id] = []

            self.milestone_achievements[user_id].append(achievement)

            # Update session context
            session_state.context["recent_milestone_achievement"] = {
                "milestone": milestone.value,
                "name": template.get("name", milestone.value),
                "celebration_story": achievement.celebration_story,
                "attribute_bonuses": {
                    attr.value: bonus
                    for attr, bonus in achievement.attribute_bonuses.items()
                },
                "story_unlocks": achievement.story_unlocks,
            }

            # Publish milestone achievement event
            await self._publish_milestone_event(session_state, achievement)

            self.metrics["milestones_achieved"] += 1
            self.metrics["character_celebrations"] += 1

        except Exception as e:
            logger.error(
                f"Failed to achieve milestone {milestone} for user {user_id}: {e}"
            )

    async def _check_ability_unlocks(
        self,
        user_id: str,
        session_state: SessionState,
        event: CharacterDevelopmentEvent,
    ) -> None:
        """Check for ability unlocks based on character development."""
        user_attributes = self.character_attributes.get(user_id, {})
        user_milestones = set()

        if user_id in self.milestone_achievements:
            user_milestones = {
                achievement.milestone
                for achievement in self.milestone_achievements[user_id]
            }

        # Get existing abilities
        existing_abilities = set()
        if user_id in self.character_abilities:
            existing_abilities = {
                ability.name for ability in self.character_abilities[user_id]
            }

        # Check each ability type
        for ability_type, abilities in self.ability_templates.items():
            for ability_template in abilities:
                ability_name = ability_template["name"]

                if ability_name in existing_abilities:
                    continue  # Already unlocked

                # Check unlock conditions
                if await self._check_ability_unlock_conditions(
                    ability_template, user_attributes, user_milestones, event
                ):
                    await self._unlock_ability(
                        user_id, session_state, ability_type, ability_template
                    )

    async def _check_ability_unlock_conditions(
        self,
        ability_template: dict[str, Any],
        user_attributes: dict[CharacterAttribute, CharacterAttributeLevel],
        user_milestones: set[CharacterMilestone],
        event: CharacterDevelopmentEvent,
    ) -> bool:
        """Check if ability unlock conditions are satisfied."""
        # Check required attributes
        required_attributes = ability_template.get("required_attributes", {})
        for attr, min_level in required_attributes.items():
            if (
                attr not in user_attributes
                or user_attributes[attr].current_level < min_level
            ):
                return False

        # Check required milestones (if any)
        required_milestones = ability_template.get("required_milestones", [])
        for milestone in required_milestones:
            if milestone not in user_milestones:
                return False

        # Check story conditions (simplified for now)
        story_conditions = ability_template.get("story_conditions", [])
        if story_conditions:
            # Check if any story condition is met in the current event
            event_context = event.story_context.lower()
            if any(condition in event_context for condition in story_conditions):
                return True
            return False

        return True  # All conditions met

    async def _unlock_ability(
        self,
        user_id: str,
        session_state: SessionState,
        ability_type: AbilityType,
        ability_template: dict[str, Any],
    ) -> None:
        """Unlock a new ability for the character."""
        try:
            # Create ability
            ability = CharacterAbility(
                name=ability_template["name"],
                description=ability_template["description"],
                ability_type=ability_type,
                required_attributes=ability_template.get("required_attributes", {}),
                unlock_trigger=DevelopmentTrigger.MILESTONE_ACHIEVEMENT,
                unlock_story=ability_template.get("unlock_story", ""),
                usage_examples=ability_template.get("usage_examples", []),
            )

            # Store ability
            if user_id not in self.character_abilities:
                self.character_abilities[user_id] = []

            self.character_abilities[user_id].append(ability)

            # Update session context
            session_state.context["recent_ability_unlock"] = {
                "ability_name": ability.name,
                "ability_description": ability.description,
                "ability_type": ability.ability_type.value,
                "unlock_story": ability.unlock_story,
                "usage_examples": ability.usage_examples,
            }

            # Publish ability unlock event
            await self._publish_ability_unlock_event(session_state, ability)

            self.metrics["abilities_unlocked"] += 1

        except Exception as e:
            logger.error(
                f"Failed to unlock ability {ability_template['name']} for user {user_id}: {e}"
            )

    async def _publish_development_event(
        self, session_state: SessionState, event: CharacterDevelopmentEvent
    ) -> None:
        """Publish character development event."""
        narrative_event = NarrativeEvent(
            event_type=EventType.CHARACTER_DEVELOPED,
            session_id=session_state.session_id,
            user_id=session_state.user_id,
            context={
                "event_id": event.event_id,
                "development_trigger": event.event_type.value,
                "attribute_changes": {
                    attr.value: change
                    for attr, change in event.attribute_changes.items()
                },
                "experience_gained": {
                    attr.value: xp for attr, xp in event.experience_gained.items()
                },
                "character_feedback": event.character_feedback,
                "narrative_impact": event.narrative_impact,
            },
        )

        await self.event_bus.publish(narrative_event)

    async def _publish_milestone_event(
        self, session_state: SessionState, achievement: CharacterMilestoneAchievement
    ) -> None:
        """Publish milestone achievement event."""
        narrative_event = NarrativeEvent(
            event_type=EventType.CHARACTER_MILESTONE_ACHIEVED,
            session_id=session_state.session_id,
            user_id=session_state.user_id,
            context={
                "achievement_id": achievement.achievement_id,
                "milestone": achievement.milestone.value,
                "celebration_story": achievement.celebration_story,
                "character_recognition": achievement.character_recognition,
                "attribute_bonuses": {
                    attr.value: bonus
                    for attr, bonus in achievement.attribute_bonuses.items()
                },
                "story_unlocks": achievement.story_unlocks,
            },
        )

        await self.event_bus.publish(narrative_event)

    async def _publish_ability_unlock_event(
        self, session_state: SessionState, ability: CharacterAbility
    ) -> None:
        """Publish ability unlock event."""
        narrative_event = NarrativeEvent(
            event_type=EventType.CHARACTER_ABILITY_UNLOCKED,
            session_id=session_state.session_id,
            user_id=session_state.user_id,
            context={
                "ability_id": ability.ability_id,
                "ability_name": ability.name,
                "ability_description": ability.description,
                "ability_type": ability.ability_type.value,
                "unlock_story": ability.unlock_story,
                "usage_examples": ability.usage_examples,
            },
        )

        await self.event_bus.publish(narrative_event)

    def get_character_summary(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive character development summary for a user."""
        if user_id not in self.character_attributes:
            return {"error": "No character data available"}

        user_attributes = self.character_attributes[user_id]
        user_abilities = self.character_abilities.get(user_id, [])
        user_milestones = self.milestone_achievements.get(user_id, [])

        # Calculate overall character level (average of all attributes)
        total_level = sum(attr.current_level for attr in user_attributes.values())
        average_level = total_level / len(user_attributes)

        # Get top attributes
        top_attributes = sorted(
            user_attributes.items(), key=lambda x: x[1].current_level, reverse=True
        )[:3]

        # Get recent development
        recent_events = []
        if user_id in self.development_events:
            recent_events = sorted(
                self.development_events[user_id],
                key=lambda x: x.occurred_at,
                reverse=True,
            )[:5]

        return {
            "user_id": user_id,
            "overall_level": round(average_level, 1),
            "total_experience": sum(
                attr.experience_points for attr in user_attributes.values()
            ),
            "attributes": {
                attr.value: {
                    "current_level": attr.current_level,
                    "experience_points": attr.experience_points,
                    "level_progress": attr.level_progress,
                    "peak_level": attr.peak_level,
                    "development_rate": attr.development_rate,
                }
                for attr, attr_level in user_attributes.items()
            },
            "top_attributes": [
                {
                    "attribute": attr.value,
                    "level": attr_level.current_level,
                    "name": self.attribute_templates.get(attr, {}).get(
                        "name", attr.value
                    ),
                }
                for attr, attr_level in top_attributes
            ],
            "abilities": [
                {
                    "name": ability.name,
                    "description": ability.description,
                    "type": ability.ability_type.value,
                    "usage_count": ability.usage_count,
                    "effectiveness": ability.effectiveness_rating,
                    "unlocked_at": ability.unlocked_at.isoformat(),
                }
                for ability in user_abilities
            ],
            "milestones": [
                {
                    "milestone": achievement.milestone.value,
                    "name": self.milestone_templates.get(achievement.milestone, {}).get(
                        "name", achievement.milestone.value
                    ),
                    "achieved_at": achievement.achieved_at.isoformat(),
                    "celebration_story": achievement.celebration_story,
                }
                for achievement in user_milestones
            ],
            "recent_development": [
                {
                    "event_type": event.event_type.value,
                    "description": event.description,
                    "attribute_changes": {
                        attr.value: change
                        for attr, change in event.attribute_changes.items()
                    },
                    "occurred_at": event.occurred_at.isoformat(),
                }
                for event in recent_events
            ],
        }

    def get_character_progression_visualization(self, user_id: str) -> dict[str, Any]:
        """Get character progression data for visualization."""
        if user_id not in self.character_attributes:
            return {"error": "No character data available"}

        user_attributes = self.character_attributes[user_id]

        # Prepare attribute progression data
        attribute_data = []
        for attribute, attr_level in user_attributes.items():
            template = self.attribute_templates.get(attribute, {})

            attribute_data.append(
                {
                    "attribute": attribute.value,
                    "name": template.get("name", attribute.value),
                    "current_level": attr_level.current_level,
                    "level_progress": attr_level.level_progress,
                    "experience_points": attr_level.experience_points,
                    "peak_level": attr_level.peak_level,
                    "development_rate": attr_level.development_rate,
                    "story_manifestations": attr_level.story_manifestations[
                        -3:
                    ],  # Last 3
                    "character_reactions": attr_level.character_reactions[
                        -3:
                    ],  # Last 3
                }
            )

        # Calculate next level requirements
        next_level_data = []
        for attribute, attr_level in user_attributes.items():
            current_level_index = int(attr_level.current_level)
            if current_level_index < len(self.level_thresholds) - 1:
                next_threshold = self.level_thresholds[current_level_index]
                xp_needed = next_threshold - attr_level.experience_points

                next_level_data.append(
                    {
                        "attribute": attribute.value,
                        "current_xp": attr_level.experience_points,
                        "next_level_xp": next_threshold,
                        "xp_needed": max(0, xp_needed),
                        "progress_percentage": attr_level.level_progress * 100,
                    }
                )

        return {
            "user_id": user_id,
            "attribute_progression": attribute_data,
            "next_level_requirements": next_level_data,
            "total_milestones": len(self.milestone_achievements.get(user_id, [])),
            "total_abilities": len(self.character_abilities.get(user_id, [])),
            "development_events_count": len(self.development_events.get(user_id, [])),
        }

    async def handle_character_regression(
        self,
        user_id: str,
        session_state: SessionState,
        regression_context: dict[str, Any],
    ) -> CharacterDevelopmentEvent:
        """Handle temporary character regression as learning opportunity."""
        try:
            # Create regression event
            event = CharacterDevelopmentEvent(
                user_id=user_id,
                session_id=session_state.session_id,
                event_type=DevelopmentTrigger.CHALLENGE_OVERCOME,  # Regression is a challenge to overcome
                description=regression_context.get(
                    "description", "Character faces a temporary setback"
                ),
                story_context=regression_context.get("story_context", ""),
            )

            # Apply temporary regression
            regression_rules = self.development_rules["regression_rules"]
            if regression_rules["enabled"]:
                affected_attributes = regression_context.get(
                    "affected_attributes", [CharacterAttribute.RESILIENCE]
                )
                max_regression = regression_rules["max_regression"]

                for attribute in affected_attributes:
                    if (
                        user_id in self.character_attributes
                        and attribute in self.character_attributes[user_id]
                    ):
                        # Apply small regression
                        regression_amount = -min(
                            max_regression, 0.2
                        )  # Small regression
                        await self._apply_attribute_change(
                            user_id,
                            attribute,
                            regression_amount,
                            DevelopmentTrigger.CHALLENGE_OVERCOME,
                        )
                        event.attribute_changes[attribute] = regression_amount

                # Generate story explanation
                event.character_feedback = regression_rules["story_explanation"]
                event.narrative_impact = "This setback is temporary - an opportunity to demonstrate resilience and growth."

            # Store event
            if user_id not in self.development_events:
                self.development_events[user_id] = []

            self.development_events[user_id].append(event)

            # Update session context
            session_state.context["character_regression"] = {
                "event_id": event.event_id,
                "is_temporary": True,
                "recovery_opportunity": True,
                "story_explanation": event.character_feedback,
            }

            return event

        except Exception as e:
            logger.error(
                f"Failed to handle character regression for user {user_id}: {e}"
            )
            return CharacterDevelopmentEvent(
                user_id=user_id,
                session_id=session_state.session_id,
                event_type=DevelopmentTrigger.CHALLENGE_OVERCOME,
                description="Character regression event",
            )

    def get_metrics(self) -> dict[str, Any]:
        """Get character development system metrics."""
        return {
            **self.metrics,
            "total_characters_tracked": len(self.character_attributes),
            "total_abilities_unlocked": sum(
                len(abilities) for abilities in self.character_abilities.values()
            ),
            "total_milestones_achieved": sum(
                len(achievements)
                for achievements in self.milestone_achievements.values()
            ),
            "total_development_events": sum(
                len(events) for events in self.development_events.values()
            ),
            "attribute_templates_loaded": len(self.attribute_templates),
            "ability_templates_loaded": sum(
                len(abilities) for abilities in self.ability_templates.values()
            ),
            "milestone_templates_loaded": len(self.milestone_templates),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of character development system."""
        return {
            "status": "healthy",
            "attribute_templates_loaded": len(self.attribute_templates),
            "ability_templates_loaded": sum(
                len(abilities) for abilities in self.ability_templates.values()
            ),
            "milestone_templates_loaded": len(self.milestone_templates),
            "development_rules_configured": len(self.development_rules),
            "level_thresholds_configured": len(self.level_thresholds),
            "milestone_thresholds_configured": len(self.milestone_thresholds),
            "ability_unlock_conditions_configured": len(self.ability_unlock_conditions),
            "metrics": self.get_metrics(),
        }
