"""
Unit Tests for Character Development System

This module contains comprehensive unit tests for the character development system,
including personality management, relationship tracking, and character memory management.
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent.parent / "core"
models_path = Path(__file__).parent.parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    from character_development_system import (
        CharacterDevelopmentSystem,
        CharacterMemoryManager,
        Interaction,
        PersonalityManager,
        PersonalityTrait,
        RelationshipTracker,
    )
    from data_models import (
        CharacterState,
        DialogueContext,
        DialogueStyle,
        MemoryFragment,
        ValidationError,
    )
except ImportError:
    # Fallback for when running as part of package
    from ..core.character_development_system import (
        CharacterDevelopmentSystem,
        CharacterMemoryManager,
        Interaction,
        PersonalityManager,
        PersonalityTrait,
        RelationshipTracker,
    )
    from ..models.data_models import (
        CharacterState,
        DialogueContext,
        DialogueStyle,
        MemoryFragment,
        ValidationError,
    )


class TestPersonalityTrait(unittest.TestCase):
    """Test PersonalityTrait dataclass."""

    def test_valid_personality_trait(self):
        """Test creating a valid personality trait."""
        trait = PersonalityTrait(name="empathy", value=0.8, stability=0.9)
        self.assertTrue(trait.validate())
        self.assertEqual(trait.name, "empathy")
        self.assertEqual(trait.value, 0.8)
        self.assertEqual(trait.stability, 0.9)

    def test_invalid_trait_value(self):
        """Test validation fails for invalid trait values."""
        with self.assertRaises(ValidationError):
            trait = PersonalityTrait(name="empathy", value=1.5)
            trait.validate()

        with self.assertRaises(ValidationError):
            trait = PersonalityTrait(name="empathy", value=-1.5)
            trait.validate()

    def test_invalid_stability_value(self):
        """Test validation fails for invalid stability values."""
        with self.assertRaises(ValidationError):
            trait = PersonalityTrait(name="empathy", value=0.5, stability=1.5)
            trait.validate()


class TestInteraction(unittest.TestCase):
    """Test Interaction dataclass."""

    def test_valid_interaction(self):
        """Test creating a valid interaction."""
        interaction = Interaction(
            participants=["char1", "char2"],
            interaction_type="dialogue",
            content="Hello there!",
            emotional_impact=0.3,
            therapeutic_value=0.5
        )
        self.assertTrue(interaction.validate())

    def test_insufficient_participants(self):
        """Test validation fails with insufficient participants."""
        with self.assertRaises(ValidationError):
            interaction = Interaction(participants=["char1"])
            interaction.validate()

    def test_invalid_emotional_impact(self):
        """Test validation fails for invalid emotional impact."""
        with self.assertRaises(ValidationError):
            interaction = Interaction(
                participants=["char1", "char2"],
                emotional_impact=1.5
            )
            interaction.validate()

    def test_invalid_therapeutic_value(self):
        """Test validation fails for invalid therapeutic value."""
        with self.assertRaises(ValidationError):
            interaction = Interaction(
                participants=["char1", "char2"],
                therapeutic_value=1.5
            )
            interaction.validate()


class TestPersonalityManager(unittest.TestCase):
    """Test PersonalityManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PersonalityManager()

    def test_initialize_personality_default(self):
        """Test initializing personality with default traits."""
        traits = self.manager.initialize_personality("test_char")
        self.assertIsInstance(traits, dict)
        self.assertIn("empathy", traits)
        self.assertIn("patience", traits)
        self.assertTrue(all(-1.0 <= v <= 1.0 for v in traits.values()))

    def test_initialize_personality_custom(self):
        """Test initializing personality with custom traits."""
        custom_traits = {"empathy": 0.9, "patience": 0.7}
        traits = self.manager.initialize_personality("test_char", custom_traits)
        self.assertEqual(traits["empathy"], 0.9)
        self.assertEqual(traits["patience"], 0.7)

    def test_initialize_personality_invalid_values(self):
        """Test initializing personality clamps invalid values."""
        custom_traits = {"empathy": 1.5, "patience": -1.5}
        traits = self.manager.initialize_personality("test_char", custom_traits)
        self.assertEqual(traits["empathy"], 1.0)
        self.assertEqual(traits["patience"], -1.0)

    def test_update_trait(self):
        """Test updating a personality trait."""
        traits = {"empathy": 0.5}
        new_value = self.manager.update_trait(traits, "empathy", 0.2, stability=0.5)
        self.assertGreater(new_value, 0.5)
        self.assertLessEqual(new_value, 1.0)

    def test_update_trait_with_stability(self):
        """Test trait update respects stability."""
        traits = {"empathy": 0.5}
        # High stability should result in smaller changes
        high_stability_change = self.manager.update_trait(traits, "empathy", 0.5, stability=0.9)
        low_stability_change = self.manager.update_trait(traits, "empathy", 0.5, stability=0.1)

        self.assertLess(abs(high_stability_change - 0.5), abs(low_stability_change - 0.5))

    def test_update_nonexistent_trait(self):
        """Test updating a non-existent trait."""
        traits = {"empathy": 0.5}
        result = self.manager.update_trait(traits, "nonexistent", 0.2)
        self.assertEqual(result, 0.0)

    def test_calculate_personality_compatibility(self):
        """Test personality compatibility calculation."""
        traits1 = {"empathy": 0.8, "patience": 0.7, "agreeableness": 0.6}
        traits2 = {"empathy": 0.9, "patience": 0.8, "agreeableness": 0.7}

        compatibility = self.manager.calculate_personality_compatibility(traits1, traits2)
        self.assertIsInstance(compatibility, float)
        self.assertGreaterEqual(compatibility, 0.0)
        self.assertLessEqual(compatibility, 1.0)
        self.assertGreater(compatibility, 0.5)  # Should be high compatibility

    def test_calculate_compatibility_empty_traits(self):
        """Test compatibility calculation with empty traits."""
        compatibility = self.manager.calculate_personality_compatibility({}, {})
        self.assertEqual(compatibility, 0.5)

    def test_generate_mood_from_traits(self):
        """Test mood generation from personality traits."""
        positive_traits = {"extraversion": 0.8, "agreeableness": 0.7, "neuroticism": -0.5}
        mood = self.manager.generate_mood_from_traits(positive_traits)
        self.assertIn(mood, ["cheerful", "content", "neutral", "melancholy", "troubled"])
        self.assertIn(mood, ["cheerful", "content"])  # Should be positive

    def test_generate_mood_with_interactions(self):
        """Test mood generation considers recent interactions."""
        traits = {"neuroticism": 0.0}
        positive_interaction = Interaction(
            participants=["char1", "char2"],
            emotional_impact=0.8
        )

        mood = self.manager.generate_mood_from_traits(traits, [positive_interaction])
        self.assertIn(mood, ["cheerful", "content", "neutral"])


class TestRelationshipTracker(unittest.TestCase):
    """Test RelationshipTracker class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracker = RelationshipTracker()

    def test_initialize_relationship(self):
        """Test initializing a neutral relationship."""
        score = self.tracker.initialize_relationship("char1", "char2")
        self.assertEqual(score, 0.0)

    def test_update_relationship_score(self):
        """Test updating relationship score from interaction."""
        interaction = Interaction(
            participants=["char1", "char2"],
            emotional_impact=0.5,
            interaction_type="dialogue"
        )

        new_score = self.tracker.update_relationship_score(0.0, interaction, "char2")
        self.assertGreater(new_score, 0.0)

    def test_update_relationship_therapeutic_bonus(self):
        """Test therapeutic interactions have higher impact."""
        therapeutic_interaction = Interaction(
            participants=["char1", "char2"],
            emotional_impact=0.3,
            interaction_type="therapeutic"
        )

        regular_interaction = Interaction(
            participants=["char1", "char2"],
            emotional_impact=0.3,
            interaction_type="dialogue"
        )

        therapeutic_score = self.tracker.update_relationship_score(0.0, therapeutic_interaction, "char2")
        regular_score = self.tracker.update_relationship_score(0.0, regular_interaction, "char2")

        self.assertGreater(therapeutic_score, regular_score)

    def test_update_relationship_not_participant(self):
        """Test relationship doesn't update if character not in interaction."""
        interaction = Interaction(
            participants=["char1", "char2"],
            emotional_impact=0.5
        )

        score = self.tracker.update_relationship_score(0.3, interaction, "char3")
        self.assertEqual(score, 0.3)  # Should remain unchanged

    def test_calculate_relationship_evolution(self):
        """Test relationship evolution over time."""
        character_state = CharacterState(
            character_id="char1",
            name="Test Character",
            relationship_scores={"char2": 0.5}
        )

        interactions = [
            Interaction(
                participants=["char1", "char2"],
                emotional_impact=0.3,
                timestamp=datetime.now() - timedelta(hours=1)
            )
        ]

        evolved_scores = self.tracker.calculate_relationship_evolution(
            character_state, interactions, timedelta(days=1)
        )

        self.assertIn("char2", evolved_scores)
        self.assertIsInstance(evolved_scores["char2"], float)

    def test_relationship_decay(self):
        """Test relationship decay for unused relationships."""
        character_state = CharacterState(
            character_id="char1",
            name="Test Character",
            relationship_scores={"char2": 0.8}
        )

        # No recent interactions
        evolved_scores = self.tracker.calculate_relationship_evolution(
            character_state, [], timedelta(days=30)
        )

        # Relationship should decay towards neutral
        self.assertLess(evolved_scores["char2"], 0.8)

    def test_get_relationship_description(self):
        """Test relationship description generation."""
        descriptions = [
            (0.9, "deeply trusting"),
            (0.5, "good friends"),
            (0.0, "neutral"),
            (-0.5, "unfriendly"),
            (-0.9, "enemies")
        ]

        for score, expected in descriptions:
            description = self.tracker.get_relationship_description(score)
            self.assertEqual(description, expected)


class TestCharacterMemoryManager(unittest.TestCase):
    """Test CharacterMemoryManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = CharacterMemoryManager()
        self.character_state = CharacterState(
            character_id="test_char",
            name="Test Character"
        )

    def test_add_memory(self):
        """Test adding a memory to character."""
        memory = self.manager.add_memory(
            self.character_state,
            "Had a great conversation about life",
            emotional_weight=0.7,
            tags=["conversation", "positive"]
        )

        self.assertIsInstance(memory, MemoryFragment)
        self.assertEqual(len(self.character_state.memory_fragments), 1)
        self.assertEqual(memory.content, "Had a great conversation about life")
        self.assertEqual(memory.emotional_weight, 0.7)
        self.assertIn("conversation", memory.tags)

    def test_memory_capacity_management(self):
        """Test memory capacity is managed properly."""
        # Add more memories than the limit
        for i in range(self.manager.max_memories_per_character + 10):
            self.manager.add_memory(
                self.character_state,
                f"Memory {i}",
                emotional_weight=0.1 * (i % 10)  # Varying importance
            )

        # Should not exceed capacity
        self.assertLessEqual(
            len(self.character_state.memory_fragments),
            self.manager.max_memories_per_character
        )

    def test_get_relevant_memories(self):
        """Test retrieving relevant memories."""
        # Add memories with different tags and emotional weights
        self.manager.add_memory(
            self.character_state, "Therapeutic session", 0.8, ["therapeutic"]
        )
        self.manager.add_memory(
            self.character_state, "Casual chat", 0.2, ["casual"]
        )
        self.manager.add_memory(
            self.character_state, "Important therapeutic breakthrough", 0.9, ["therapeutic", "breakthrough"]
        )

        relevant = self.manager.get_relevant_memories(
            self.character_state,
            context_tags=["therapeutic"],
            max_memories=5
        )

        self.assertGreater(len(relevant), 0)
        # Should prioritize therapeutic memories
        therapeutic_memories = [m for m in relevant if "therapeutic" in m.tags]
        self.assertGreater(len(therapeutic_memories), 0)

    def test_create_memory_from_interaction(self):
        """Test creating memory from interaction."""
        interaction = Interaction(
            participants=["test_char", "user1"],
            interaction_type="therapeutic",
            content="Discussed coping strategies for anxiety",
            emotional_impact=0.6
        )

        memory = self.manager.create_memory_from_interaction(
            self.character_state, interaction
        )

        self.assertIsInstance(memory, MemoryFragment)
        self.assertIn("therapeutic", memory.tags)
        self.assertEqual(memory.emotional_weight, 0.6)
        self.assertIn("coping strategies", memory.content)


class TestCharacterDevelopmentSystem(unittest.TestCase):
    """Test CharacterDevelopmentSystem main class."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = CharacterDevelopmentSystem()

    def test_create_character(self):
        """Test creating a new character."""
        character = self.system.create_character(
            character_id="test_001",
            name="Dr. Smith",
            personality_traits={"empathy": 0.9, "patience": 0.8},
            therapeutic_role="therapist"
        )

        self.assertIsInstance(character, CharacterState)
        self.assertEqual(character.character_id, "test_001")
        self.assertEqual(character.name, "Dr. Smith")
        self.assertEqual(character.personality_traits["empathy"], 0.9)
        self.assertEqual(character.therapeutic_role, "therapist")
        self.assertTrue(character.validate())

    def test_get_character_state(self):
        """Test retrieving character state."""
        # Create character first
        self.system.create_character("test_002", "Test Character")

        # Retrieve it
        retrieved = self.system.get_character_state("test_002")

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.character_id, "test_002")
        self.assertEqual(retrieved.name, "Test Character")

    def test_get_nonexistent_character(self):
        """Test retrieving non-existent character returns None."""
        result = self.system.get_character_state("nonexistent")
        self.assertIsNone(result)

    def test_update_character_from_interaction(self):
        """Test updating character from interaction."""
        # Create character
        character = self.system.create_character("test_003", "Test Character")
        original_memory_count = len(character.memory_fragments)

        # Create interaction
        interaction = Interaction(
            participants=["test_003", "user1"],
            interaction_type="therapeutic",
            content="Discussed mindfulness techniques",
            emotional_impact=0.5,
            therapeutic_value=0.8
        )

        # Update character
        success = self.system.update_character_from_interaction("test_003", interaction)

        self.assertTrue(success)

        # Verify updates
        updated_character = self.system.get_character_state("test_003")
        self.assertGreater(len(updated_character.memory_fragments), original_memory_count)
        self.assertIn("user1", updated_character.relationship_scores)

    def test_update_nonexistent_character(self):
        """Test updating non-existent character fails gracefully."""
        interaction = Interaction(participants=["nonexistent", "user1"])
        success = self.system.update_character_from_interaction("nonexistent", interaction)
        self.assertFalse(success)

    def test_evolve_character(self):
        """Test character evolution over time."""
        # Create character
        self.system.create_character("test_004", "Test Character")

        # Create story events
        interaction = Interaction(
            participants=["test_004", "user1"],
            interaction_type="supportive",
            emotional_impact=0.3
        )
        story_events = [{"interaction": interaction}]

        # Evolve character
        success = self.system.evolve_character("test_004", story_events, timedelta(days=1))

        self.assertTrue(success)

    def test_generate_character_dialogue_context(self):
        """Test generating dialogue context for character."""
        # Create character with some history
        character = self.system.create_character("test_005", "Test Character")

        # Add some memories
        self.system.memory_manager.add_memory(
            character, "Previous conversation about anxiety", 0.5, ["anxiety"]
        )

        # Create dialogue context
        dialogue_context = DialogueContext(
            participants=["test_005", "user1"],
            current_topic="anxiety"
        )

        # Generate context
        context = self.system.generate_character_dialogue_context("test_005", dialogue_context)

        self.assertIsInstance(context, dict)
        self.assertEqual(context["character_id"], "test_005")
        self.assertIn("personality_traits", context)
        self.assertIn("relevant_memories", context)
        self.assertIn("dialogue_style", context)

    def test_validate_character_consistency(self):
        """Test character dialogue consistency validation."""
        # Create formal character
        self.system.create_character(
            "test_006", "Formal Character",
            dialogue_style=DialogueStyle(formality_level=0.9, empathy_level=0.8)
        )

        # Test consistent dialogue
        is_consistent, message = self.system.validate_character_consistency(
            "test_006",
            "I understand your concerns and would like to help you address them.",
            {}
        )
        self.assertTrue(is_consistent)

        # Test inconsistent dialogue (too informal)
        is_consistent, message = self.system.validate_character_consistency(
            "test_006",
            "Hey, yeah, whatever you wanna do is fine.",
            {}
        )
        self.assertFalse(is_consistent)
        self.assertIn("informal", message)

    def test_get_character_development_summary(self):
        """Test getting character development summary."""
        # Create character with some development
        character = self.system.create_character("test_007", "Test Character")

        # Add some relationships and memories
        character.relationship_scores["user1"] = 0.7
        character.relationship_scores["user2"] = -0.3
        self.system.memory_manager.add_memory(character, "Positive memory", 0.5)
        self.system.memory_manager.add_memory(character, "Negative memory", -0.4)

        # Get summary
        summary = self.system.get_character_development_summary("test_007")

        self.assertIsInstance(summary, dict)
        self.assertEqual(summary["character_id"], "test_007")
        self.assertIn("relationship_summary", summary)
        self.assertIn("memory_summary", summary)
        self.assertIn("personality_summary", summary)

        # Check relationship summary
        rel_summary = summary["relationship_summary"]
        self.assertEqual(rel_summary["total_relationships"], 2)
        self.assertEqual(rel_summary["positive_relationships"], 1)
        self.assertEqual(rel_summary["negative_relationships"], 1)

        # Check memory summary
        mem_summary = summary["memory_summary"]
        self.assertEqual(mem_summary["total_memories"], 2)
        self.assertEqual(mem_summary["positive_memories"], 1)
        self.assertEqual(mem_summary["negative_memories"], 1)

    def test_get_summary_nonexistent_character(self):
        """Test getting summary for non-existent character."""
        summary = self.system.get_character_development_summary("nonexistent")
        self.assertEqual(summary, {})


class TestSystemIntegration(unittest.TestCase):
    """Test integration between system components."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = CharacterDevelopmentSystem()

    def test_full_character_lifecycle(self):
        """Test complete character lifecycle from creation to evolution."""
        # Create character
        self.system.create_character(
            "lifecycle_test",
            "Dr. Integration Test",
            personality_traits={"empathy": 0.7, "patience": 0.6},
            therapeutic_role="therapist"
        )

        # Simulate multiple interactions
        interactions = [
            Interaction(
                participants=["lifecycle_test", "patient1"],
                interaction_type="therapeutic",
                content="Initial assessment session",
                emotional_impact=0.3,
                therapeutic_value=0.7
            ),
            Interaction(
                participants=["lifecycle_test", "patient1"],
                interaction_type="therapeutic",
                content="Cognitive behavioral therapy session",
                emotional_impact=0.5,
                therapeutic_value=0.9
            ),
            Interaction(
                participants=["lifecycle_test", "colleague1"],
                interaction_type="dialogue",
                content="Case consultation",
                emotional_impact=0.2,
                therapeutic_value=0.3
            )
        ]

        # Process interactions
        for interaction in interactions:
            success = self.system.update_character_from_interaction("lifecycle_test", interaction)
            self.assertTrue(success)

        # Evolve character
        story_events = [{"interaction": interaction} for interaction in interactions]
        success = self.system.evolve_character("lifecycle_test", story_events)
        self.assertTrue(success)

        # Verify final state
        final_character = self.system.get_character_state("lifecycle_test")
        self.assertIsNotNone(final_character)
        self.assertGreater(len(final_character.memory_fragments), 0)
        self.assertIn("patient1", final_character.relationship_scores)
        self.assertIn("colleague1", final_character.relationship_scores)

        # Get development summary
        summary = self.system.get_character_development_summary("lifecycle_test")
        self.assertGreater(summary["relationship_summary"]["total_relationships"], 0)
        self.assertGreater(summary["memory_summary"]["total_memories"], 0)


if __name__ == "__main__":
    unittest.main()
