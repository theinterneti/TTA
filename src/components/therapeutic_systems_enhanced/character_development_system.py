"""
Therapeutic CharacterDevelopmentSystem Implementation

This module provides production-ready character development and progression
for the TTA therapeutic platform, implementing evidence-based character
attribute systems aligned with therapeutic goals and frameworks.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class TherapeuticAttribute(Enum):
    """12 core therapeutic character attributes aligned with evidence-based frameworks."""

    COURAGE = "courage"
    WISDOM = "wisdom"
    COMPASSION = "compassion"
    RESILIENCE = "resilience"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    COMMUNICATION = "communication"
    MINDFULNESS = "mindfulness"
    SELF_AWARENESS = "self_awareness"
    EMPATHY = "empathy"
    CONFIDENCE = "confidence"
    ADAPTABILITY = "adaptability"
    INTEGRITY = "integrity"


class MilestoneType(Enum):
    """Types of therapeutic milestones that can be achieved."""

    THERAPEUTIC_BREAKTHROUGH = "therapeutic_breakthrough"
    SKILL_MASTERY = "skill_mastery"
    EMOTIONAL_GROWTH = "emotional_growth"
    RELATIONSHIP_IMPROVEMENT = "relationship_improvement"
    COPING_STRATEGY_DEVELOPMENT = "coping_strategy_development"
    CONFIDENCE_BUILDING = "confidence_building"
    MINDFULNESS_ACHIEVEMENT = "mindfulness_achievement"
    COMMUNICATION_MILESTONE = "communication_milestone"


@dataclass
class CharacterAttributes:
    """Container for character attribute values and progression."""

    courage: float = 5.0
    wisdom: float = 5.0
    compassion: float = 5.0
    resilience: float = 5.0
    emotional_intelligence: float = 5.0
    communication: float = 5.0
    mindfulness: float = 5.0
    self_awareness: float = 5.0
    empathy: float = 5.0
    confidence: float = 5.0
    adaptability: float = 5.0
    integrity: float = 5.0

    def to_dict(self) -> dict[str, float]:
        """Convert attributes to dictionary format."""
        return {
            "courage": self.courage,
            "wisdom": self.wisdom,
            "compassion": self.compassion,
            "resilience": self.resilience,
            "emotional_intelligence": self.emotional_intelligence,
            "communication": self.communication,
            "mindfulness": self.mindfulness,
            "self_awareness": self.self_awareness,
            "empathy": self.empathy,
            "confidence": self.confidence,
            "adaptability": self.adaptability,
            "integrity": self.integrity,
        }

    def get_attribute(self, attribute: TherapeuticAttribute) -> float:
        """Get specific attribute value."""
        return getattr(self, attribute.value)

    def set_attribute(self, attribute: TherapeuticAttribute, value: float):
        """Set specific attribute value (clamped to 0.0-10.0 range)."""
        clamped_value = max(0.0, min(10.0, value))
        setattr(self, attribute.value, clamped_value)


@dataclass
class TherapeuticMilestone:
    """Represents a therapeutic milestone achievement."""

    milestone_id: str
    milestone_type: MilestoneType
    title: str
    description: str
    therapeutic_value: float
    attributes_impacted: list[TherapeuticAttribute]
    achievement_date: datetime
    session_context: dict[str, Any] = field(default_factory=dict)


@dataclass
class CharacterProgressionEvent:
    """Represents a character progression event."""

    event_id: str
    character_id: str
    event_type: str
    attribute_changes: dict[str, float]
    milestone_achieved: TherapeuticMilestone | None
    therapeutic_context: dict[str, Any]
    timestamp: datetime


@dataclass
class TherapeuticCharacter:
    """Complete therapeutic character with attributes and progression."""

    character_id: str
    user_id: str
    name: str
    attributes: CharacterAttributes
    milestones: list[TherapeuticMilestone] = field(default_factory=list)
    progression_events: list[CharacterProgressionEvent] = field(default_factory=list)
    therapeutic_goals: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    total_therapeutic_value: float = 0.0
    session_count: int = 0


class TherapeuticCharacterDevelopmentSystem:
    """
    Production CharacterDevelopmentSystem that provides evidence-based character
    development aligned with therapeutic goals and frameworks.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the therapeutic character development system."""
        self.config = config or {}

        # Character storage
        self.characters = {}  # user_id -> TherapeuticCharacter
        self.character_lookup = {}  # character_id -> user_id

        # Progression tracking
        self.progression_history = {}  # user_id -> List[CharacterProgressionEvent]
        self.milestone_templates = self._initialize_milestone_templates()

        # Configuration parameters
        self.attribute_growth_rate = self.config.get("attribute_growth_rate", 0.1)
        self.milestone_threshold = self.config.get("milestone_threshold", 2.0)
        self.max_attribute_value = self.config.get("max_attribute_value", 10.0)
        self.therapeutic_alignment_bonus = self.config.get(
            "therapeutic_alignment_bonus", 0.2
        )

        # Therapeutic framework mappings
        self.framework_attribute_mappings = {
            "CBT": [
                TherapeuticAttribute.SELF_AWARENESS,
                TherapeuticAttribute.WISDOM,
                TherapeuticAttribute.RESILIENCE,
            ],
            "DBT": [
                TherapeuticAttribute.EMOTIONAL_INTELLIGENCE,
                TherapeuticAttribute.MINDFULNESS,
                TherapeuticAttribute.ADAPTABILITY,
            ],
            "MINDFULNESS": [
                TherapeuticAttribute.MINDFULNESS,
                TherapeuticAttribute.SELF_AWARENESS,
                TherapeuticAttribute.COMPASSION,
            ],
            "ACT": [
                TherapeuticAttribute.COURAGE,
                TherapeuticAttribute.INTEGRITY,
                TherapeuticAttribute.ADAPTABILITY,
            ],
        }

        # Performance metrics
        self.metrics = {
            "characters_created": 0,
            "milestones_achieved": 0,
            "attribute_progressions": 0,
            "therapeutic_alignments": 0,
            "progression_events": 0,
        }

        logger.info("TherapeuticCharacterDevelopmentSystem initialized")

    async def initialize(self):
        """Initialize the character development system."""
        # Any async initialization can go here
        logger.info("TherapeuticCharacterDevelopmentSystem initialization complete")

    async def create_character(
        self,
        user_id: str,
        session_id: str | None = None,
        therapeutic_goals: list[str] | None = None,
        character_name: str | None = None,
        initial_attributes: dict[str, float] | None = None,
    ) -> TherapeuticCharacter:
        """
        Create a new therapeutic character for the user.

        This method provides the interface expected by E2E tests for character
        creation with therapeutic goal alignment.

        Args:
            user_id: Unique identifier for the user
            session_id: Current session identifier
            therapeutic_goals: List of therapeutic goals for character alignment
            character_name: Optional custom name for the character
            initial_attributes: Optional initial attribute values

        Returns:
            TherapeuticCharacter instance with therapeutic alignment
        """
        try:
            start_time = datetime.utcnow()

            # Generate character ID and name
            character_id = f"char_{user_id}_{uuid4().hex[:8]}"
            name = character_name or self._generate_character_name(therapeutic_goals)

            # Initialize attributes with therapeutic alignment
            attributes = self._initialize_character_attributes(
                therapeutic_goals, initial_attributes
            )

            # Create therapeutic character
            character = TherapeuticCharacter(
                character_id=character_id,
                user_id=user_id,
                name=name,
                attributes=attributes,
                therapeutic_goals=therapeutic_goals or [],
                session_count=1,
            )

            # Store character
            self.characters[user_id] = character
            self.character_lookup[character_id] = user_id

            # Initialize progression history
            if user_id not in self.progression_history:
                self.progression_history[user_id] = []

            # Create initial progression event
            initial_event = CharacterProgressionEvent(
                event_id=str(uuid4()),
                character_id=character_id,
                event_type="character_creation",
                attribute_changes={},
                milestone_achieved=None,
                therapeutic_context={
                    "session_id": session_id,
                    "therapeutic_goals": therapeutic_goals,
                    "creation_method": "therapeutic_alignment",
                },
                timestamp=start_time,
            )

            character.progression_events.append(initial_event)
            self.progression_history[user_id].append(initial_event)

            # Update metrics
            self.metrics["characters_created"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.info(
                f"Created therapeutic character {character_id} for user {user_id} "
                f"in {processing_time.total_seconds():.3f}s"
            )

            return character

        except Exception as e:
            logger.error(f"Error creating character for user {user_id}: {e}")

            # Return fallback character
            fallback_character = TherapeuticCharacter(
                character_id=f"fallback_{user_id}",
                user_id=user_id,
                name="Therapeutic Character",
                attributes=CharacterAttributes(),
                therapeutic_goals=therapeutic_goals or [],
            )

            return fallback_character

    def _generate_character_name(self, therapeutic_goals: list[str] | None) -> str:
        """Generate a character name based on therapeutic goals."""
        if not therapeutic_goals:
            return "Therapeutic Character"

        # Name suggestions based on primary therapeutic goal
        goal_names = {
            "anxiety_management": "Serenity",
            "confidence_building": "Valor",
            "communication_skills": "Harmony",
            "emotional_regulation": "Balance",
            "mindfulness": "Zen",
            "resilience": "Phoenix",
            "self_awareness": "Insight",
            "empathy": "Compassion",
            "social_skills": "Unity",
            "stress_management": "Calm",
        }

        primary_goal = therapeutic_goals[0] if therapeutic_goals else "general"
        return goal_names.get(primary_goal, "Journey")

    def _initialize_character_attributes(
        self,
        therapeutic_goals: list[str] | None,
        initial_attributes: dict[str, float] | None,
    ) -> CharacterAttributes:
        """Initialize character attributes with therapeutic goal alignment."""
        # Start with base attributes
        attributes = CharacterAttributes()

        # Apply initial attributes if provided
        if initial_attributes:
            for attr_name, value in initial_attributes.items():
                if hasattr(attributes, attr_name):
                    setattr(attributes, attr_name, max(0.0, min(10.0, value)))

        # Apply therapeutic goal bonuses
        if therapeutic_goals:
            goal_bonuses = self._calculate_therapeutic_goal_bonuses(therapeutic_goals)
            for attr_name, bonus in goal_bonuses.items():
                current_value = getattr(attributes, attr_name, 5.0)
                new_value = min(10.0, current_value + bonus)
                setattr(attributes, attr_name, new_value)

        return attributes

    def _calculate_therapeutic_goal_bonuses(
        self, therapeutic_goals: list[str]
    ) -> dict[str, float]:
        """Calculate attribute bonuses based on therapeutic goals."""
        bonuses = {}

        # Goal-to-attribute mappings
        goal_mappings = {
            "anxiety_management": {
                "mindfulness": 1.0,
                "resilience": 0.8,
                "self_awareness": 0.6,
            },
            "confidence_building": {
                "courage": 1.2,
                "confidence": 1.0,
                "resilience": 0.5,
            },
            "communication_skills": {
                "communication": 1.2,
                "empathy": 0.8,
                "emotional_intelligence": 0.6,
            },
            "emotional_regulation": {
                "emotional_intelligence": 1.0,
                "mindfulness": 0.8,
                "self_awareness": 0.7,
            },
            "mindfulness": {
                "mindfulness": 1.2,
                "self_awareness": 0.9,
                "compassion": 0.6,
            },
            "resilience": {"resilience": 1.2, "courage": 0.8, "adaptability": 0.7},
            "self_awareness": {
                "self_awareness": 1.2,
                "wisdom": 0.8,
                "mindfulness": 0.6,
            },
            "empathy": {
                "empathy": 1.2,
                "compassion": 1.0,
                "emotional_intelligence": 0.7,
            },
            "social_skills": {"communication": 1.0, "empathy": 0.9, "confidence": 0.7},
            "stress_management": {
                "resilience": 1.0,
                "mindfulness": 0.9,
                "adaptability": 0.6,
            },
        }

        # Accumulate bonuses from all goals
        for goal in therapeutic_goals:
            if goal in goal_mappings:
                for attr, bonus in goal_mappings[goal].items():
                    bonuses[attr] = bonuses.get(attr, 0.0) + bonus

        return bonuses

    def _initialize_milestone_templates(self) -> dict[MilestoneType, dict[str, Any]]:
        """Initialize milestone templates for therapeutic achievements."""
        return {
            MilestoneType.THERAPEUTIC_BREAKTHROUGH: {
                "title": "Therapeutic Breakthrough",
                "description": "Achieved a significant breakthrough in therapeutic understanding",
                "therapeutic_value": 3.0,
                "attributes": [
                    TherapeuticAttribute.SELF_AWARENESS,
                    TherapeuticAttribute.WISDOM,
                ],
            },
            MilestoneType.SKILL_MASTERY: {
                "title": "Skill Mastery",
                "description": "Mastered a key therapeutic skill or coping strategy",
                "therapeutic_value": 2.5,
                "attributes": [
                    TherapeuticAttribute.CONFIDENCE,
                    TherapeuticAttribute.RESILIENCE,
                ],
            },
            MilestoneType.EMOTIONAL_GROWTH: {
                "title": "Emotional Growth",
                "description": "Demonstrated significant emotional intelligence development",
                "therapeutic_value": 2.8,
                "attributes": [
                    TherapeuticAttribute.EMOTIONAL_INTELLIGENCE,
                    TherapeuticAttribute.EMPATHY,
                ],
            },
            MilestoneType.RELATIONSHIP_IMPROVEMENT: {
                "title": "Relationship Improvement",
                "description": "Improved interpersonal relationships and communication",
                "therapeutic_value": 2.6,
                "attributes": [
                    TherapeuticAttribute.COMMUNICATION,
                    TherapeuticAttribute.EMPATHY,
                ],
            },
            MilestoneType.COPING_STRATEGY_DEVELOPMENT: {
                "title": "Coping Strategy Development",
                "description": "Developed effective coping strategies for challenges",
                "therapeutic_value": 2.4,
                "attributes": [
                    TherapeuticAttribute.RESILIENCE,
                    TherapeuticAttribute.ADAPTABILITY,
                ],
            },
            MilestoneType.CONFIDENCE_BUILDING: {
                "title": "Confidence Building",
                "description": "Built significant confidence and self-assurance",
                "therapeutic_value": 2.7,
                "attributes": [
                    TherapeuticAttribute.CONFIDENCE,
                    TherapeuticAttribute.COURAGE,
                ],
            },
            MilestoneType.MINDFULNESS_ACHIEVEMENT: {
                "title": "Mindfulness Achievement",
                "description": "Achieved mindfulness and present-moment awareness",
                "therapeutic_value": 2.5,
                "attributes": [
                    TherapeuticAttribute.MINDFULNESS,
                    TherapeuticAttribute.SELF_AWARENESS,
                ],
            },
            MilestoneType.COMMUNICATION_MILESTONE: {
                "title": "Communication Milestone",
                "description": "Reached a significant communication and expression milestone",
                "therapeutic_value": 2.3,
                "attributes": [
                    TherapeuticAttribute.COMMUNICATION,
                    TherapeuticAttribute.CONFIDENCE,
                ],
            },
        }

    async def process_therapeutic_consequence(
        self,
        user_id: str,
        consequence_data: dict[str, Any],
        session_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process therapeutic consequences and update character development.

        This method integrates with the ConsequenceSystem to apply character
        attribute changes based on therapeutic choices and outcomes.

        Args:
            user_id: Unique identifier for the user
            consequence_data: Consequence data from ConsequenceSystem
            session_context: Current session context

        Returns:
            Dictionary containing character development results
        """
        try:
            start_time = datetime.utcnow()

            # Get user's character
            if user_id not in self.characters:
                logger.warning(
                    f"No character found for user {user_id}, creating default character"
                )
                await self.create_character(user_id)

            character = self.characters[user_id]

            # Extract attribute impacts from consequence data
            attribute_impacts = consequence_data.get("character_impact", {})
            therapeutic_value = consequence_data.get("therapeutic_value", 0.0)

            # Apply attribute changes
            attribute_changes = {}
            for attr_name, impact in attribute_impacts.items():
                if hasattr(character.attributes, attr_name):
                    current_value = getattr(character.attributes, attr_name)

                    # Apply therapeutic alignment bonus
                    aligned_bonus = self._calculate_alignment_bonus(
                        attr_name, character.therapeutic_goals
                    )
                    adjusted_impact = impact * (1.0 + aligned_bonus)

                    # Calculate new value with growth rate
                    change = adjusted_impact * self.attribute_growth_rate
                    new_value = max(
                        0.0, min(self.max_attribute_value, current_value + change)
                    )

                    setattr(character.attributes, attr_name, new_value)
                    attribute_changes[attr_name] = change

            # Check for milestone achievements
            milestone_achieved = self._check_milestone_achievement(
                character, attribute_changes, therapeutic_value
            )

            # Create progression event
            progression_event = CharacterProgressionEvent(
                event_id=str(uuid4()),
                character_id=character.character_id,
                event_type="therapeutic_consequence",
                attribute_changes=attribute_changes,
                milestone_achieved=milestone_achieved,
                therapeutic_context={
                    "session_context": session_context,
                    "therapeutic_value": therapeutic_value,
                    "consequence_type": consequence_data.get(
                        "consequence_type", "unknown"
                    ),
                },
                timestamp=start_time,
            )

            # Update character
            character.progression_events.append(progression_event)
            character.total_therapeutic_value += therapeutic_value
            character.last_updated = start_time

            # Update progression history
            self.progression_history[user_id].append(progression_event)

            # Update metrics
            self.metrics["progression_events"] += 1
            self.metrics["attribute_progressions"] += len(attribute_changes)
            if milestone_achieved:
                self.metrics["milestones_achieved"] += 1

            processing_time = datetime.utcnow() - start_time
            logger.debug(
                f"Processed therapeutic consequence for user {user_id} in {processing_time.total_seconds():.3f}s"
            )

            return {
                "character_id": character.character_id,
                "attribute_changes": attribute_changes,
                "milestone_achieved": (
                    milestone_achieved.title if milestone_achieved else None
                ),
                "total_therapeutic_value": character.total_therapeutic_value,
                "processing_time": processing_time.total_seconds(),
            }

        except Exception as e:
            logger.error(
                f"Error processing therapeutic consequence for user {user_id}: {e}"
            )
            return {
                "error": str(e),
                "character_id": None,
                "attribute_changes": {},
            }

    def _calculate_alignment_bonus(
        self, attribute_name: str, therapeutic_goals: list[str]
    ) -> float:
        """Calculate therapeutic alignment bonus for attribute growth."""
        if not therapeutic_goals:
            return 0.0

        # Check if attribute aligns with therapeutic goals
        alignment_score = 0.0
        for goal in therapeutic_goals:
            goal_bonuses = self._calculate_therapeutic_goal_bonuses([goal])
            if attribute_name in goal_bonuses:
                alignment_score += (
                    goal_bonuses[attribute_name] * self.therapeutic_alignment_bonus
                )

        return min(0.5, alignment_score)  # Cap bonus at 50%

    def _check_milestone_achievement(
        self,
        character: TherapeuticCharacter,
        attribute_changes: dict[str, float],
        therapeutic_value: float,
    ) -> TherapeuticMilestone | None:
        """Check if character has achieved a therapeutic milestone."""
        # Check if therapeutic value meets milestone threshold
        if therapeutic_value < self.milestone_threshold:
            return None

        # Determine milestone type based on attribute changes and therapeutic value
        milestone_type = self._determine_milestone_type(
            attribute_changes, therapeutic_value
        )
        if not milestone_type:
            return None

        # Create milestone
        template = self.milestone_templates[milestone_type]
        milestone = TherapeuticMilestone(
            milestone_id=str(uuid4()),
            milestone_type=milestone_type,
            title=template["title"],
            description=template["description"],
            therapeutic_value=therapeutic_value,
            attributes_impacted=template["attributes"],
            achievement_date=datetime.utcnow(),
            session_context={"attribute_changes": attribute_changes},
        )

        # Add to character milestones
        character.milestones.append(milestone)

        return milestone

    def _determine_milestone_type(
        self, attribute_changes: dict[str, float], therapeutic_value: float
    ) -> MilestoneType | None:
        """Determine the type of milestone based on attribute changes."""
        if not attribute_changes:
            return None

        # Find the attribute with the highest positive change
        max_change_attr = max(attribute_changes.items(), key=lambda x: x[1])
        max_attr_name, max_change = max_change_attr

        if max_change <= 0:
            return None

        # Map attributes to milestone types
        attr_milestone_mapping = {
            "self_awareness": MilestoneType.THERAPEUTIC_BREAKTHROUGH,
            "wisdom": MilestoneType.THERAPEUTIC_BREAKTHROUGH,
            "confidence": MilestoneType.CONFIDENCE_BUILDING,
            "courage": MilestoneType.CONFIDENCE_BUILDING,
            "emotional_intelligence": MilestoneType.EMOTIONAL_GROWTH,
            "empathy": MilestoneType.EMOTIONAL_GROWTH,
            "communication": MilestoneType.COMMUNICATION_MILESTONE,
            "resilience": MilestoneType.COPING_STRATEGY_DEVELOPMENT,
            "adaptability": MilestoneType.COPING_STRATEGY_DEVELOPMENT,
            "mindfulness": MilestoneType.MINDFULNESS_ACHIEVEMENT,
            "compassion": MilestoneType.RELATIONSHIP_IMPROVEMENT,
        }

        # Special case for high therapeutic value
        if therapeutic_value >= 3.0:
            return MilestoneType.THERAPEUTIC_BREAKTHROUGH

        return attr_milestone_mapping.get(max_attr_name, MilestoneType.SKILL_MASTERY)

    async def get_character_summary(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive character development summary for a user."""
        try:
            if user_id not in self.characters:
                return {"error": "No character found for user"}

            character = self.characters[user_id]

            # Calculate character level (average of all attributes)
            attributes_dict = character.attributes.to_dict()
            total_level = sum(attributes_dict.values())
            average_level = total_level / len(attributes_dict)

            # Get top attributes
            top_attributes = sorted(
                attributes_dict.items(), key=lambda x: x[1], reverse=True
            )[:3]

            # Get recent milestones
            recent_milestones = sorted(
                character.milestones, key=lambda x: x.achievement_date, reverse=True
            )[:5]

            # Calculate progression rate
            progression_rate = self._calculate_progression_rate(character)

            return {
                "character_id": character.character_id,
                "name": character.name,
                "overall_level": round(average_level, 2),
                "total_therapeutic_value": character.total_therapeutic_value,
                "session_count": character.session_count,
                "attributes": attributes_dict,
                "top_attributes": [
                    {"name": name, "value": value} for name, value in top_attributes
                ],
                "milestone_count": len(character.milestones),
                "recent_milestones": [
                    {
                        "title": m.title,
                        "type": m.milestone_type.value,
                        "date": m.achievement_date.isoformat(),
                        "therapeutic_value": m.therapeutic_value,
                    }
                    for m in recent_milestones
                ],
                "progression_rate": progression_rate,
                "therapeutic_goals": character.therapeutic_goals,
                "created_at": character.created_at.isoformat(),
                "last_updated": character.last_updated.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting character summary for user {user_id}: {e}")
            return {"error": str(e)}

    def _calculate_progression_rate(self, character: TherapeuticCharacter) -> float:
        """Calculate character progression rate based on recent activity."""
        if not character.progression_events:
            return 0.0

        # Look at events from the last 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        recent_events = [
            event
            for event in character.progression_events
            if event.timestamp > cutoff_date
        ]

        if not recent_events:
            return 0.0

        # Calculate average therapeutic value per event
        total_value = sum(
            event.therapeutic_context.get("therapeutic_value", 0.0)
            for event in recent_events
        )

        return total_value / len(recent_events)

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the character development system."""
        try:
            return {
                "status": "healthy",
                "characters_tracked": len(self.characters),
                "total_milestones": sum(
                    len(char.milestones) for char in self.characters.values()
                ),
                "total_progression_events": sum(
                    len(char.progression_events) for char in self.characters.values()
                ),
                "therapeutic_attributes": len(TherapeuticAttribute),
                "milestone_types": len(MilestoneType),
                "framework_mappings": len(self.framework_attribute_mappings),
                "metrics": self.get_metrics(),
            }

        except Exception as e:
            logger.error(f"Error in character development system health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_metrics(self) -> dict[str, Any]:
        """Get character development system metrics."""
        # Calculate additional metrics
        total_attributes_tracked = sum(
            len(char.attributes.to_dict()) for char in self.characters.values()
        )

        average_therapeutic_value = 0.0
        if self.characters:
            total_value = sum(
                char.total_therapeutic_value for char in self.characters.values()
            )
            average_therapeutic_value = total_value / len(self.characters)

        return {
            **self.metrics,
            "characters_tracked": len(self.characters),
            "total_attributes_tracked": total_attributes_tracked,
            "average_therapeutic_value": round(average_therapeutic_value, 2),
            "therapeutic_attributes_available": len(TherapeuticAttribute),
            "milestone_types_available": len(MilestoneType),
            "framework_mappings_configured": len(self.framework_attribute_mappings),
        }


# Alias for backward compatibility
CharacterDevelopmentSystem = TherapeuticCharacterDevelopmentSystem
