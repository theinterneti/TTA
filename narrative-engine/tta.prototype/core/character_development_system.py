"""
Character Development System for TTA Prototype

This module implements the character development system that manages character personalities,
relationships, mood tracking, and character evolution over time. It provides the core
functionality for maintaining consistent character behavior and therapeutic dialogue.

Classes:
    CharacterDevelopmentSystem: Main system for character management
    PersonalityManager: Handles personality trait management and consistency
    RelationshipTracker: Manages character relationships and interactions
    CharacterMemoryManager: Handles character memory and interaction history
"""

import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add models path for data models access
models_path = Path(__file__).parent.parent / "models"
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    from data_models import (
        CharacterState,
        DialogueContext,
        DialogueStyle,
        EmotionalState,
        MemoryFragment,
        TherapeuticOpportunity,
        ValidationError,
    )
except ImportError:
    # Fallback for when running as part of package
    from ..models.data_models import (
        CharacterState,
        DialogueContext,
        DialogueStyle,
        MemoryFragment,
        ValidationError,
    )

logger = logging.getLogger(__name__)


@dataclass
class PersonalityTrait:
    """Represents a personality trait with its current value and stability."""
    name: str
    value: float  # -1.0 to 1.0
    stability: float = 0.8  # How resistant to change (0.0 to 1.0)
    last_updated: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate personality trait data."""
        if not -1.0 <= self.value <= 1.0:
            raise ValidationError(f"Personality trait '{self.name}' value must be between -1.0 and 1.0")
        if not 0.0 <= self.stability <= 1.0:
            raise ValidationError(f"Personality trait '{self.name}' stability must be between 0.0 and 1.0")
        return True


@dataclass
class Interaction:
    """Represents an interaction between characters or with the user."""
    interaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    participants: list[str] = field(default_factory=list)
    interaction_type: str = "dialogue"  # dialogue, action, therapeutic, conflict
    content: str = ""
    emotional_impact: float = 0.0  # -1.0 to 1.0
    therapeutic_value: float = 0.0  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    context_tags: list[str] = field(default_factory=list)

    def validate(self) -> bool:
        """Validate interaction data."""
        if len(self.participants) < 2:
            raise ValidationError("Interaction must have at least 2 participants")
        if not -1.0 <= self.emotional_impact <= 1.0:
            raise ValidationError("Emotional impact must be between -1.0 and 1.0")
        if not 0.0 <= self.therapeutic_value <= 1.0:
            raise ValidationError("Therapeutic value must be between 0.0 and 1.0")
        return True


class PersonalityManager:
    """Manages character personality traits and consistency."""

    def __init__(self):
        self.default_traits = {
            "openness": 0.0,
            "conscientiousness": 0.0,
            "extraversion": 0.0,
            "agreeableness": 0.0,
            "neuroticism": 0.0,
            "empathy": 0.5,
            "patience": 0.5,
            "wisdom": 0.0,
            "humor": 0.0,
            "supportiveness": 0.5
        }

    def initialize_personality(self, character_id: str, base_traits: dict[str, float] = None) -> dict[str, float]:
        """Initialize personality traits for a character."""
        traits = self.default_traits.copy()
        if base_traits:
            traits.update(base_traits)

        # Validate trait values
        for trait_name, value in traits.items():
            if not -1.0 <= value <= 1.0:
                logger.warning(f"Invalid trait value for {trait_name}: {value}. Clamping to valid range.")
                traits[trait_name] = max(-1.0, min(1.0, value))

        logger.info(f"Initialized personality for character {character_id} with {len(traits)} traits")
        return traits

    def update_trait(self, current_traits: dict[str, float], trait_name: str,
                    influence: float, stability: float = 0.8) -> float:
        """Update a personality trait based on influence and stability."""
        if trait_name not in current_traits:
            logger.warning(f"Unknown trait: {trait_name}")
            return current_traits.get(trait_name, 0.0)

        current_value = current_traits[trait_name]

        # Calculate change based on stability (higher stability = less change)
        change_factor = (1.0 - stability) * 0.1  # Max 10% change per update
        potential_change = influence * change_factor

        # Apply diminishing returns for extreme values
        if abs(current_value) > 0.7:
            potential_change *= (1.0 - abs(current_value))

        new_value = max(-1.0, min(1.0, current_value + potential_change))

        logger.debug(f"Updated trait {trait_name}: {current_value:.3f} -> {new_value:.3f}")
        return new_value

    def calculate_personality_compatibility(self, traits1: dict[str, float],
                                          traits2: dict[str, float]) -> float:
        """Calculate compatibility between two personality profiles."""
        if not traits1 or not traits2:
            return 0.5  # Neutral compatibility

        compatibility_factors = {
            "openness": 0.8,  # Similar openness is good
            "conscientiousness": 0.6,  # Some difference is okay
            "extraversion": 0.7,  # Complementary can work
            "agreeableness": 0.9,  # High agreeableness is always good
            "neuroticism": -0.8,  # Lower neuroticism is better
            "empathy": 0.9,  # High empathy is always good
            "patience": 0.8,  # Patience helps relationships
            "supportiveness": 0.9  # Supportiveness is crucial
        }

        total_score = 0.0
        total_weight = 0.0

        for trait, weight in compatibility_factors.items():
            if trait in traits1 and trait in traits2:
                value1, value2 = traits1[trait], traits2[trait]

                if weight > 0:
                    # For positive traits, similarity is good
                    similarity = 1.0 - abs(value1 - value2) / 2.0
                    score = similarity * abs(weight)
                else:
                    # For negative traits, lower values are better
                    score = (1.0 - max(abs(value1), abs(value2))) * abs(weight)

                total_score += score
                total_weight += abs(weight)

        if total_weight == 0:
            return 0.5

        compatibility = total_score / total_weight
        return max(0.0, min(1.0, compatibility))

    def generate_mood_from_traits(self, traits: dict[str, float],
                                 recent_interactions: list[Interaction] = None) -> str:
        """Generate current mood based on personality traits and recent interactions."""
        base_mood_score = 0.0

        # Base mood from personality
        if "neuroticism" in traits:
            base_mood_score -= traits["neuroticism"] * 0.3
        if "extraversion" in traits:
            base_mood_score += traits["extraversion"] * 0.2
        if "agreeableness" in traits:
            base_mood_score += traits["agreeableness"] * 0.1

        # Adjust based on recent interactions
        if recent_interactions:
            interaction_impact = sum(interaction.emotional_impact for interaction in recent_interactions[-5:])
            base_mood_score += interaction_impact * 0.1

        # Map score to mood
        if base_mood_score > 0.3:
            return "cheerful"
        elif base_mood_score > 0.1:
            return "content"
        elif base_mood_score > -0.1:
            return "neutral"
        elif base_mood_score > -0.3:
            return "melancholy"
        else:
            return "troubled"


class RelationshipTracker:
    """Manages character relationships and interactions."""

    def __init__(self):
        self.relationship_decay_rate = 0.01  # Daily decay rate for unused relationships
        self.interaction_impact_multiplier = 0.1

    def initialize_relationship(self, character1_id: str, character2_id: str) -> float:
        """Initialize a neutral relationship between two characters."""
        return 0.0

    def update_relationship_score(self, current_score: float, interaction: Interaction,
                                character_id: str) -> float:
        """Update relationship score based on an interaction."""
        if character_id not in interaction.participants:
            return current_score

        # Base impact from interaction
        impact = interaction.emotional_impact * self.interaction_impact_multiplier

        # Modify impact based on interaction type
        type_multipliers = {
            "dialogue": 1.0,
            "therapeutic": 1.5,  # Therapeutic interactions have more impact
            "conflict": 2.0,  # Conflicts have strong impact
            "supportive": 1.3,  # Supportive actions build relationships
            "action": 0.8  # Actions have less direct relationship impact
        }

        multiplier = type_multipliers.get(interaction.interaction_type, 1.0)
        impact *= multiplier

        # Apply diminishing returns for extreme relationships
        if abs(current_score) > 0.7:
            impact *= (1.0 - abs(current_score) * 0.5)

        new_score = max(-1.0, min(1.0, current_score + impact))

        logger.debug(f"Updated relationship score: {current_score:.3f} -> {new_score:.3f}")
        return new_score

    def calculate_relationship_evolution(self, character_state: CharacterState,
                                       interactions: list[Interaction],
                                       time_period: timedelta = None) -> dict[str, float]:
        """Calculate how relationships should evolve based on interactions."""
        if time_period is None:
            time_period = timedelta(days=1)

        evolved_scores = character_state.relationship_scores.copy()

        # Apply decay to unused relationships
        decay_factor = self.relationship_decay_rate * time_period.days
        for character_id in evolved_scores:
            # Check if there were recent interactions
            recent_interactions = [
                i for i in interactions
                if character_id in i.participants and
                (datetime.now() - i.timestamp) <= time_period
            ]

            if not recent_interactions:
                # Apply decay towards neutral
                current_score = evolved_scores[character_id]
                decay_amount = abs(current_score) * decay_factor
                if current_score > 0:
                    evolved_scores[character_id] = max(0.0, current_score - decay_amount)
                else:
                    evolved_scores[character_id] = min(0.0, current_score + decay_amount)

        # Apply interaction impacts
        for interaction in interactions:
            if (datetime.now() - interaction.timestamp) <= time_period:
                for participant in interaction.participants:
                    if participant != character_state.character_id and participant in evolved_scores:
                        evolved_scores[participant] = self.update_relationship_score(
                            evolved_scores[participant], interaction, participant
                        )

        return evolved_scores

    def get_relationship_description(self, score: float) -> str:
        """Get a textual description of a relationship score."""
        if score >= 0.8:
            return "deeply trusting"
        elif score >= 0.6:
            return "close friends"
        elif score >= 0.4:
            return "good friends"
        elif score >= 0.2:
            return "friendly"
        elif score >= -0.2:
            return "neutral"
        elif score >= -0.4:
            return "distant"
        elif score >= -0.6:
            return "unfriendly"
        elif score >= -0.8:
            return "hostile"
        else:
            return "enemies"


class CharacterMemoryManager:
    """Handles character memory and interaction history."""

    def __init__(self):
        self.max_memories_per_character = 100
        self.memory_decay_days = 30
        self.important_memory_threshold = 0.7

    def add_memory(self, character_state: CharacterState, content: str,
                  emotional_weight: float = 0.0, tags: list[str] = None) -> MemoryFragment:
        """Add a new memory to a character's memory collection."""
        memory = MemoryFragment(
            content=content,
            emotional_weight=emotional_weight,
            tags=tags or []
        )
        memory.validate()

        character_state.memory_fragments.append(memory)
        character_state.last_interaction = datetime.now()

        # Manage memory capacity
        self._manage_memory_capacity(character_state)

        logger.debug(f"Added memory to character {character_state.character_id}: {content[:50]}...")
        return memory

    def _manage_memory_capacity(self, character_state: CharacterState) -> None:
        """Manage memory capacity by removing old, less important memories."""
        if len(character_state.memory_fragments) <= self.max_memories_per_character:
            return

        # Sort memories by importance (emotional weight and recency)
        def memory_importance(memory: MemoryFragment) -> float:
            age_days = (datetime.now() - memory.timestamp).days
            age_factor = max(0.1, 1.0 - (age_days / self.memory_decay_days))
            return abs(memory.emotional_weight) * age_factor

        character_state.memory_fragments.sort(key=memory_importance, reverse=True)

        # Keep only the most important memories
        character_state.memory_fragments = character_state.memory_fragments[:self.max_memories_per_character]

        logger.debug(f"Trimmed memories for character {character_state.character_id} to {len(character_state.memory_fragments)}")

    def get_relevant_memories(self, character_state: CharacterState,
                            context_tags: list[str] = None,
                            emotional_threshold: float = 0.3,
                            max_memories: int = 10) -> list[MemoryFragment]:
        """Retrieve relevant memories based on context and emotional significance."""
        relevant_memories = []

        for memory in character_state.memory_fragments:
            relevance_score = 0.0

            # Score based on emotional weight
            relevance_score += abs(memory.emotional_weight)

            # Score based on tag matching
            if context_tags:
                matching_tags = set(memory.tags) & set(context_tags)
                relevance_score += len(matching_tags) * 0.3

            # Score based on recency
            age_days = (datetime.now() - memory.timestamp).days
            recency_score = max(0.1, 1.0 - (age_days / 30))  # 30-day decay
            relevance_score *= recency_score

            if relevance_score >= emotional_threshold:
                relevant_memories.append((memory, relevance_score))

        # Sort by relevance and return top memories
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in relevant_memories[:max_memories]]

    def create_memory_from_interaction(self, character_state: CharacterState,
                                     interaction: Interaction) -> MemoryFragment:
        """Create a memory fragment from an interaction."""
        # Determine memory content based on interaction
        if interaction.interaction_type == "therapeutic":
            content = f"Had a meaningful therapeutic conversation about {interaction.content[:100]}"
            tags = ["therapeutic", "meaningful"]
        elif interaction.interaction_type == "conflict":
            content = f"Had a difficult conversation: {interaction.content[:100]}"
            tags = ["conflict", "challenging"]
        else:
            content = f"Talked about: {interaction.content[:100]}"
            tags = ["conversation"]

        # Add participant information
        other_participants = [p for p in interaction.participants if p != character_state.character_id]
        if other_participants:
            tags.append(f"with_{other_participants[0]}")

        return self.add_memory(
            character_state,
            content,
            interaction.emotional_impact,
            tags
        )


class CharacterDevelopmentSystem:
    """Main system for character development, personality management, and relationship tracking."""

    def __init__(self):
        self.personality_manager = PersonalityManager()
        self.relationship_tracker = RelationshipTracker()
        self.memory_manager = CharacterMemoryManager()
        self.character_cache = {}  # In-memory cache for frequently accessed characters

        logger.info("Character Development System initialized")

    def create_character(self, character_id: str, name: str,
                        personality_traits: dict[str, float] = None,
                        therapeutic_role: str = "companion",
                        dialogue_style: DialogueStyle = None) -> CharacterState:
        """Create a new character with initialized personality and systems."""
        if dialogue_style is None:
            dialogue_style = DialogueStyle()

        # Initialize personality traits
        traits = self.personality_manager.initialize_personality(character_id, personality_traits)

        # Create character state
        character_state = CharacterState(
            character_id=character_id,
            name=name,
            personality_traits=traits,
            therapeutic_role=therapeutic_role,
            dialogue_style=dialogue_style
        )

        # Generate initial mood
        character_state.current_mood = self.personality_manager.generate_mood_from_traits(traits)

        # Validate and cache
        character_state.validate()
        self.character_cache[character_id] = character_state

        logger.info(f"Created character: {name} ({character_id}) with role: {therapeutic_role}")
        return character_state

    def get_character_state(self, character_id: str) -> CharacterState | None:
        """Retrieve character state from cache or storage."""
        if character_id in self.character_cache:
            return self.character_cache[character_id]

        # In a full implementation, this would load from Neo4j
        logger.warning(f"Character {character_id} not found in cache")
        return None

    def update_character_from_interaction(self, character_id: str, interaction: Interaction) -> bool:
        """Update character state based on an interaction."""
        character_state = self.get_character_state(character_id)
        if not character_state:
            logger.error(f"Character {character_id} not found")
            return False

        try:
            # Create memory from interaction
            self.memory_manager.create_memory_from_interaction(character_state, interaction)

            # Update relationships
            for participant in interaction.participants:
                if participant != character_id:
                    if participant not in character_state.relationship_scores:
                        character_state.relationship_scores[participant] = 0.0

                    character_state.relationship_scores[participant] = \
                        self.relationship_tracker.update_relationship_score(
                            character_state.relationship_scores[participant],
                            interaction,
                            participant
                        )

            # Update personality traits based on interaction
            self._update_personality_from_interaction(character_state, interaction)

            # Update mood
            recent_interactions = [interaction]  # In full implementation, get recent interactions
            character_state.current_mood = self.personality_manager.generate_mood_from_traits(
                character_state.personality_traits, recent_interactions
            )

            character_state.last_interaction = datetime.now()
            character_state.validate()

            logger.debug(f"Updated character {character_id} from interaction")
            return True

        except Exception as e:
            logger.error(f"Error updating character {character_id}: {e}")
            return False

    def _update_personality_from_interaction(self, character_state: CharacterState,
                                           interaction: Interaction) -> None:
        """Update personality traits based on interaction type and content."""
        trait_influences = {
            "therapeutic": {
                "empathy": 0.1,
                "patience": 0.05,
                "supportiveness": 0.1,
                "wisdom": 0.03
            },
            "conflict": {
                "neuroticism": 0.05,
                "agreeableness": -0.03,
                "patience": -0.02
            },
            "supportive": {
                "empathy": 0.08,
                "supportiveness": 0.1,
                "agreeableness": 0.05
            },
            "dialogue": {
                "extraversion": 0.02,
                "openness": 0.01
            }
        }

        influences = trait_influences.get(interaction.interaction_type, {})

        for trait_name, influence in influences.items():
            if trait_name in character_state.personality_traits:
                # Scale influence by interaction emotional impact
                scaled_influence = influence * (1.0 + abs(interaction.emotional_impact))

                character_state.personality_traits[trait_name] = \
                    self.personality_manager.update_trait(
                        character_state.personality_traits,
                        trait_name,
                        scaled_influence
                    )

    def evolve_character(self, character_id: str, story_events: list[dict[str, Any]],
                        time_period: timedelta = None) -> bool:
        """Evolve character based on story events and time passage."""
        character_state = self.get_character_state(character_id)
        if not character_state:
            return False

        if time_period is None:
            time_period = timedelta(days=1)

        try:
            # Convert story events to interactions for processing
            interactions = []
            for event in story_events:
                if "interaction" in event:
                    interactions.append(event["interaction"])

            # Evolve relationships
            evolved_relationships = self.relationship_tracker.calculate_relationship_evolution(
                character_state, interactions, time_period
            )
            character_state.relationship_scores = evolved_relationships

            # Update mood based on recent events
            character_state.current_mood = self.personality_manager.generate_mood_from_traits(
                character_state.personality_traits, interactions
            )

            character_state.validate()
            logger.info(f"Evolved character {character_id} over {time_period.days} days")
            return True

        except Exception as e:
            logger.error(f"Error evolving character {character_id}: {e}")
            return False

    def generate_character_dialogue_context(self, character_id: str,
                                          dialogue_context: DialogueContext) -> dict[str, Any]:
        """Generate context for character dialogue based on personality and relationships."""
        character_state = self.get_character_state(character_id)
        if not character_state:
            return {}

        # Get relevant memories
        context_tags = [dialogue_context.current_topic] if dialogue_context.current_topic else []
        relevant_memories = self.memory_manager.get_relevant_memories(
            character_state, context_tags, max_memories=5
        )

        # Get relationship information for other participants
        relationships = {}
        for participant in dialogue_context.participants:
            if participant != character_id and participant in character_state.relationship_scores:
                score = character_state.relationship_scores[participant]
                relationships[participant] = {
                    "score": score,
                    "description": self.relationship_tracker.get_relationship_description(score)
                }

        return {
            "character_id": character_id,
            "name": character_state.name,
            "personality_traits": character_state.personality_traits,
            "current_mood": character_state.current_mood,
            "therapeutic_role": character_state.therapeutic_role,
            "dialogue_style": character_state.dialogue_style,
            "relevant_memories": [
                {"content": m.content, "emotional_weight": m.emotional_weight}
                for m in relevant_memories
            ],
            "relationships": relationships,
            "last_interaction": character_state.last_interaction
        }

    def validate_character_consistency(self, character_id: str,
                                     proposed_dialogue: str,
                                     context: dict[str, Any]) -> tuple[bool, str]:
        """Validate that proposed dialogue is consistent with character personality."""
        character_state = self.get_character_state(character_id)
        if not character_state:
            return False, "Character not found"

        # This is a simplified consistency check
        # In a full implementation, this would use NLP to analyze dialogue tone

        style = character_state.dialogue_style

        # Check for basic consistency issues
        issues = []

        # Check formality level
        if style.formality_level > 0.7 and any(word in proposed_dialogue.lower()
                                              for word in ["hey", "yeah", "gonna", "wanna"]):
            issues.append("Dialogue too informal for character's style")

        # Check empathy level
        if style.empathy_level > 0.8 and any(phrase in proposed_dialogue.lower()
                                           for phrase in ["don't care", "not my problem", "whatever"]):
            issues.append("Dialogue lacks empathy for character's personality")

        # Check therapeutic role consistency
        if character_state.therapeutic_role == "therapist" and "I don't know" in proposed_dialogue:
            issues.append("Therapist character should be more knowledgeable")

        if issues:
            return False, "; ".join(issues)

        return True, "Dialogue is consistent with character"

    def get_character_development_summary(self, character_id: str) -> dict[str, Any]:
        """Get a summary of character development and current state."""
        character_state = self.get_character_state(character_id)
        if not character_state:
            return {}

        # Calculate relationship summary
        relationship_summary = {
            "total_relationships": len(character_state.relationship_scores),
            "positive_relationships": sum(1 for score in character_state.relationship_scores.values() if score > 0.2),
            "negative_relationships": sum(1 for score in character_state.relationship_scores.values() if score < -0.2),
            "strongest_relationship": max(character_state.relationship_scores.items(),
                                        key=lambda x: abs(x[1]), default=("none", 0.0))
        }

        # Calculate memory summary
        memory_summary = {
            "total_memories": len(character_state.memory_fragments),
            "positive_memories": sum(1 for m in character_state.memory_fragments if m.emotional_weight > 0.3),
            "negative_memories": sum(1 for m in character_state.memory_fragments if m.emotional_weight < -0.3),
            "recent_memories": sum(1 for m in character_state.memory_fragments
                                 if (datetime.now() - m.timestamp).days <= 7)
        }

        return {
            "character_id": character_id,
            "name": character_state.name,
            "current_mood": character_state.current_mood,
            "therapeutic_role": character_state.therapeutic_role,
            "personality_summary": {
                trait: round(value, 2) for trait, value in character_state.personality_traits.items()
            },
            "relationship_summary": relationship_summary,
            "memory_summary": memory_summary,
            "last_interaction": character_state.last_interaction,
            "dialogue_style": {
                "formality": character_state.dialogue_style.formality_level,
                "empathy": character_state.dialogue_style.empathy_level,
                "approach": character_state.dialogue_style.therapeutic_approach
            }
        }


# Utility functions for testing and validation
def create_test_character() -> CharacterState:
    """Create a test character for validation purposes."""
    system = CharacterDevelopmentSystem()
    return system.create_character(
        character_id="test_char_001",
        name="Dr. Sarah Chen",
        personality_traits={
            "empathy": 0.9,
            "patience": 0.8,
            "wisdom": 0.7,
            "supportiveness": 0.9,
            "openness": 0.6
        },
        therapeutic_role="therapist"
    )


def validate_character_development_system() -> bool:
    """Validate the character development system functionality."""
    try:
        system = CharacterDevelopmentSystem()

        # Test character creation
        character = system.create_character(
            character_id="test_char_001",
            name="Dr. Sarah Chen",
            personality_traits={
                "empathy": 0.9,
                "patience": 0.8,
                "wisdom": 0.7,
                "supportiveness": 0.9,
                "openness": 0.6
            },
            therapeutic_role="therapist"
        )
        assert character.validate()

        # Test interaction processing
        interaction = Interaction(
            participants=["test_char_001", "user_001"],
            interaction_type="therapeutic",
            content="Discussed coping strategies for anxiety",
            emotional_impact=0.5,
            therapeutic_value=0.8
        )
        interaction.validate()

        success = system.update_character_from_interaction("test_char_001", interaction)
        assert success

        # Test character evolution
        story_events = [{"interaction": interaction}]
        success = system.evolve_character("test_char_001", story_events)
        assert success

        # Test dialogue context generation
        dialogue_context = DialogueContext(
            participants=["test_char_001", "user_001"],
            current_topic="anxiety management"
        )
        context = system.generate_character_dialogue_context("test_char_001", dialogue_context)
        assert context

        # Test consistency validation
        is_consistent, message = system.validate_character_consistency(
            "test_char_001",
            "I understand how difficult this must be for you. Let's explore some coping strategies.",
            {}
        )
        assert is_consistent

        logger.info("Character Development System validation successful")
        return True

    except Exception as e:
        logger.error(f"Character Development System validation failed: {e}")
        return False


if __name__ == "__main__":
    # Run validation
    validate_character_development_system()
