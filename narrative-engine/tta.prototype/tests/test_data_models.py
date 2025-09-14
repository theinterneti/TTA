"""
Unit tests for TTA Prototype data models.

This module contains comprehensive tests for all data model classes,
including validation, serialization, and deserialization functionality.
"""

import json
import os
import sys
import unittest
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.data_models import (
    CharacterState,
    CompletedIntervention,
    CopingStrategy,
    DialogueContext,
    DialogueStyle,
    EmotionalState,
    EmotionalStateType,
    InterventionType,
    MemoryFragment,
    NarrativeContext,
    SessionState,
    TherapeuticGoal,
    TherapeuticGoalStatus,
    TherapeuticOpportunity,
    TherapeuticProgress,
    ValidationError,
    validate_all_models,
)


class TestMemoryFragment(unittest.TestCase):
    """Test cases for MemoryFragment class."""

    def test_memory_fragment_creation(self):
        """Test creating a memory fragment with default values."""
        memory = MemoryFragment(content="Test memory")
        self.assertEqual(memory.content, "Test memory")
        self.assertEqual(memory.emotional_weight, 0.0)
        self.assertIsInstance(memory.timestamp, datetime)
        self.assertEqual(memory.tags, [])
        self.assertTrue(memory.memory_id)

    def test_memory_fragment_validation_success(self):
        """Test successful memory fragment validation."""
        memory = MemoryFragment(
            content="Valid memory",
            emotional_weight=0.5,
            tags=["positive", "interaction"]
        )
        self.assertTrue(memory.validate())

    def test_memory_fragment_validation_empty_content(self):
        """Test memory fragment validation with empty content."""
        memory = MemoryFragment(content="")
        with self.assertRaises(ValidationError):
            memory.validate()

    def test_memory_fragment_validation_invalid_weight(self):
        """Test memory fragment validation with invalid emotional weight."""
        memory = MemoryFragment(content="Test", emotional_weight=2.0)
        with self.assertRaises(ValidationError):
            memory.validate()


class TestDialogueStyle(unittest.TestCase):
    """Test cases for DialogueStyle class."""

    def test_dialogue_style_creation(self):
        """Test creating dialogue style with default values."""
        style = DialogueStyle()
        self.assertEqual(style.formality_level, 0.5)
        self.assertEqual(style.empathy_level, 0.7)
        self.assertEqual(style.therapeutic_approach, "supportive")

    def test_dialogue_style_validation_success(self):
        """Test successful dialogue style validation."""
        style = DialogueStyle(
            formality_level=0.8,
            empathy_level=0.9,
            directness=0.6,
            humor_usage=0.2
        )
        self.assertTrue(style.validate())

    def test_dialogue_style_validation_invalid_values(self):
        """Test dialogue style validation with invalid values."""
        style = DialogueStyle(formality_level=1.5)
        with self.assertRaises(ValidationError):
            style.validate()


class TestCharacterState(unittest.TestCase):
    """Test cases for CharacterState class."""

    def test_character_state_creation(self):
        """Test creating character state with required fields."""
        character = CharacterState(character_id="char_1", name="Alice")
        self.assertEqual(character.character_id, "char_1")
        self.assertEqual(character.name, "Alice")
        self.assertEqual(character.current_mood, "neutral")
        self.assertEqual(character.therapeutic_role, "companion")
        self.assertIsInstance(character.dialogue_style, DialogueStyle)

    def test_character_state_validation_success(self):
        """Test successful character state validation."""
        character = CharacterState(
            character_id="char_1",
            name="Alice",
            personality_traits={"openness": 0.8, "conscientiousness": 0.6},
            relationship_scores={"user": 0.5}
        )
        self.assertTrue(character.validate())

    def test_character_state_validation_empty_id(self):
        """Test character state validation with empty ID."""
        character = CharacterState(character_id="", name="Alice")
        with self.assertRaises(ValidationError):
            character.validate()

    def test_character_state_validation_invalid_personality(self):
        """Test character state validation with invalid personality trait."""
        character = CharacterState(
            character_id="char_1",
            name="Alice",
            personality_traits={"openness": 2.0}
        )
        with self.assertRaises(ValidationError):
            character.validate()

    def test_add_memory(self):
        """Test adding memory to character."""
        character = CharacterState(character_id="char_1", name="Alice")
        character.add_memory("Had a great conversation", 0.8, ["positive"])

        self.assertEqual(len(character.memory_fragments), 1)
        memory = character.memory_fragments[0]
        self.assertEqual(memory.content, "Had a great conversation")
        self.assertEqual(memory.emotional_weight, 0.8)
        self.assertIn("positive", memory.tags)
        self.assertIsNotNone(character.last_interaction)

    def test_update_relationship(self):
        """Test updating relationship score."""
        character = CharacterState(character_id="char_1", name="Alice")
        character.update_relationship("user", 0.3)
        self.assertEqual(character.relationship_scores["user"], 0.3)

        # Test clamping to valid range
        character.update_relationship("user", 1.0)
        self.assertEqual(character.relationship_scores["user"], 1.0)


class TestTherapeuticGoal(unittest.TestCase):
    """Test cases for TherapeuticGoal class."""

    def test_therapeutic_goal_creation(self):
        """Test creating therapeutic goal."""
        goal = TherapeuticGoal(
            title="Reduce Anxiety",
            description="Learn coping strategies for anxiety management"
        )
        self.assertEqual(goal.title, "Reduce Anxiety")
        self.assertEqual(goal.progress_percentage, 0.0)
        self.assertEqual(goal.status, TherapeuticGoalStatus.ACTIVE)
        self.assertTrue(goal.goal_id)

    def test_therapeutic_goal_validation_success(self):
        """Test successful therapeutic goal validation."""
        goal = TherapeuticGoal(
            title="Test Goal",
            description="Test Description",
            progress_percentage=50.0
        )
        self.assertTrue(goal.validate())

    def test_therapeutic_goal_validation_empty_title(self):
        """Test therapeutic goal validation with empty title."""
        goal = TherapeuticGoal(title="", description="Test Description")
        with self.assertRaises(ValidationError):
            goal.validate()

    def test_therapeutic_goal_validation_invalid_progress(self):
        """Test therapeutic goal validation with invalid progress."""
        goal = TherapeuticGoal(
            title="Test Goal",
            description="Test Description",
            progress_percentage=150.0
        )
        with self.assertRaises(ValidationError):
            goal.validate()


class TestCompletedIntervention(unittest.TestCase):
    """Test cases for CompletedIntervention class."""

    def test_completed_intervention_creation(self):
        """Test creating completed intervention."""
        intervention = CompletedIntervention(
            description="Practiced deep breathing",
            effectiveness_rating=8.0
        )
        self.assertEqual(intervention.description, "Practiced deep breathing")
        self.assertEqual(intervention.effectiveness_rating, 8.0)
        self.assertEqual(intervention.intervention_type, InterventionType.COPING_SKILLS)
        self.assertTrue(intervention.intervention_id)

    def test_completed_intervention_validation_success(self):
        """Test successful completed intervention validation."""
        intervention = CompletedIntervention(
            description="Test intervention",
            effectiveness_rating=7.5
        )
        self.assertTrue(intervention.validate())

    def test_completed_intervention_validation_invalid_rating(self):
        """Test completed intervention validation with invalid rating."""
        intervention = CompletedIntervention(
            description="Test intervention",
            effectiveness_rating=15.0
        )
        with self.assertRaises(ValidationError):
            intervention.validate()


class TestCopingStrategy(unittest.TestCase):
    """Test cases for CopingStrategy class."""

    def test_coping_strategy_creation(self):
        """Test creating coping strategy."""
        strategy = CopingStrategy(
            name="Deep Breathing",
            description="Breathing technique for relaxation"
        )
        self.assertEqual(strategy.name, "Deep Breathing")
        self.assertEqual(strategy.usage_count, 0)
        self.assertTrue(strategy.strategy_id)

    def test_coping_strategy_validation_success(self):
        """Test successful coping strategy validation."""
        strategy = CopingStrategy(
            name="Test Strategy",
            description="Test Description",
            effectiveness_score=8.0
        )
        self.assertTrue(strategy.validate())

    def test_coping_strategy_validation_negative_usage(self):
        """Test coping strategy validation with negative usage count."""
        strategy = CopingStrategy(
            name="Test Strategy",
            description="Test Description",
            usage_count=-1
        )
        with self.assertRaises(ValidationError):
            strategy.validate()


class TestEmotionalState(unittest.TestCase):
    """Test cases for EmotionalState class."""

    def test_emotional_state_creation(self):
        """Test creating emotional state."""
        state = EmotionalState(
            primary_emotion=EmotionalStateType.ANXIOUS,
            intensity=0.7
        )
        self.assertEqual(state.primary_emotion, EmotionalStateType.ANXIOUS)
        self.assertEqual(state.intensity, 0.7)
        self.assertEqual(state.confidence_level, 0.7)

    def test_emotional_state_validation_success(self):
        """Test successful emotional state validation."""
        state = EmotionalState(intensity=0.8, confidence_level=0.9)
        self.assertTrue(state.validate())

    def test_emotional_state_validation_invalid_intensity(self):
        """Test emotional state validation with invalid intensity."""
        state = EmotionalState(intensity=1.5)
        with self.assertRaises(ValidationError):
            state.validate()


class TestTherapeuticProgress(unittest.TestCase):
    """Test cases for TherapeuticProgress class."""

    def test_therapeutic_progress_creation(self):
        """Test creating therapeutic progress."""
        progress = TherapeuticProgress(user_id="user_123")
        self.assertEqual(progress.user_id, "user_123")
        self.assertEqual(progress.overall_progress_score, 0.0)
        self.assertEqual(len(progress.therapeutic_goals), 0)

    def test_therapeutic_progress_validation_success(self):
        """Test successful therapeutic progress validation."""
        progress = TherapeuticProgress(
            user_id="user_123",
            overall_progress_score=75.0
        )
        self.assertTrue(progress.validate())

    def test_therapeutic_progress_validation_empty_user_id(self):
        """Test therapeutic progress validation with empty user ID."""
        progress = TherapeuticProgress(user_id="")
        with self.assertRaises(ValidationError):
            progress.validate()

    def test_add_goal(self):
        """Test adding therapeutic goal."""
        progress = TherapeuticProgress(user_id="user_123")
        goal = progress.add_goal("Test Goal", "Test Description", ["behavior1"])

        self.assertEqual(len(progress.therapeutic_goals), 1)
        self.assertEqual(goal.title, "Test Goal")
        self.assertEqual(goal.description, "Test Description")
        self.assertIn("behavior1", goal.target_behaviors)

    def test_complete_intervention(self):
        """Test completing intervention."""
        progress = TherapeuticProgress(user_id="user_123")
        intervention = progress.complete_intervention(
            InterventionType.MINDFULNESS,
            "Practiced mindfulness meditation",
            8.5,
            "Very helpful"
        )

        self.assertEqual(len(progress.completed_interventions), 1)
        self.assertEqual(intervention.intervention_type, InterventionType.MINDFULNESS)
        self.assertEqual(intervention.effectiveness_rating, 8.5)


class TestTherapeuticOpportunity(unittest.TestCase):
    """Test cases for TherapeuticOpportunity class."""

    def test_therapeutic_opportunity_creation(self):
        """Test creating therapeutic opportunity."""
        opportunity = TherapeuticOpportunity(
            trigger_event="User expressed anxiety",
            urgency_level=0.8
        )
        self.assertEqual(opportunity.trigger_event, "User expressed anxiety")
        self.assertEqual(opportunity.urgency_level, 0.8)
        self.assertTrue(opportunity.opportunity_id)

    def test_therapeutic_opportunity_validation_success(self):
        """Test successful therapeutic opportunity validation."""
        opportunity = TherapeuticOpportunity(
            trigger_event="Test event",
            urgency_level=0.5,
            estimated_duration=10
        )
        self.assertTrue(opportunity.validate())

    def test_therapeutic_opportunity_validation_invalid_duration(self):
        """Test therapeutic opportunity validation with invalid duration."""
        opportunity = TherapeuticOpportunity(
            trigger_event="Test event",
            estimated_duration=0
        )
        with self.assertRaises(ValidationError):
            opportunity.validate()


class TestDialogueContext(unittest.TestCase):
    """Test cases for DialogueContext class."""

    def test_dialogue_context_creation(self):
        """Test creating dialogue context."""
        context = DialogueContext(participants=["user", "character"])
        self.assertEqual(context.participants, ["user", "character"])
        self.assertEqual(context.current_topic, "")
        self.assertEqual(len(context.conversation_history), 0)
        self.assertTrue(context.context_id)

    def test_dialogue_context_validation_success(self):
        """Test successful dialogue context validation."""
        context = DialogueContext(participants=["user", "alice"])
        self.assertTrue(context.validate())

    def test_dialogue_context_validation_no_participants(self):
        """Test dialogue context validation with no participants."""
        context = DialogueContext(participants=[])
        with self.assertRaises(ValidationError):
            context.validate()

    def test_add_message(self):
        """Test adding message to dialogue context."""
        context = DialogueContext(participants=["user", "alice"])
        context.add_message("user", "Hello Alice!", "dialogue")

        self.assertEqual(len(context.conversation_history), 1)
        message = context.conversation_history[0]
        self.assertEqual(message["speaker"], "user")
        self.assertEqual(message["content"], "Hello Alice!")
        self.assertEqual(message["type"], "dialogue")
        self.assertIn("timestamp", message)


class TestNarrativeContext(unittest.TestCase):
    """Test cases for NarrativeContext class."""

    def test_narrative_context_creation(self):
        """Test creating narrative context."""
        context = NarrativeContext(session_id="session_123")
        self.assertEqual(context.session_id, "session_123")
        self.assertEqual(context.narrative_position, 0)
        self.assertEqual(len(context.therapeutic_opportunities), 0)

    def test_narrative_context_validation_success(self):
        """Test successful narrative context validation."""
        context = NarrativeContext(
            session_id="session_123",
            narrative_position=5
        )
        self.assertTrue(context.validate())

    def test_narrative_context_validation_negative_position(self):
        """Test narrative context validation with negative position."""
        context = NarrativeContext(
            session_id="session_123",
            narrative_position=-1
        )
        with self.assertRaises(ValidationError):
            context.validate()

    def test_add_choice(self):
        """Test adding choice to narrative context."""
        context = NarrativeContext(session_id="session_123")
        context.add_choice("Go left", "choice_1", ["entered forest"])

        self.assertEqual(len(context.user_choice_history), 1)
        choice = context.user_choice_history[0]
        self.assertEqual(choice["choice_text"], "Go left")
        self.assertEqual(choice["choice_id"], "choice_1")
        self.assertIn("entered forest", choice["consequences"])


class TestSessionState(unittest.TestCase):
    """Test cases for SessionState class."""

    def test_session_state_creation(self):
        """Test creating session state."""
        session = SessionState(session_id="session_123", user_id="user_456")
        self.assertEqual(session.session_id, "session_123")
        self.assertEqual(session.user_id, "user_456")
        self.assertEqual(session.narrative_position, 0)
        self.assertEqual(len(session.character_states), 0)

    def test_session_state_validation_success(self):
        """Test successful session state validation."""
        session = SessionState(
            session_id="session_123",
            user_id="user_456",
            narrative_position=10
        )
        self.assertTrue(session.validate())

    def test_session_state_validation_empty_session_id(self):
        """Test session state validation with empty session ID."""
        session = SessionState(session_id="", user_id="user_456")
        with self.assertRaises(ValidationError):
            session.validate()

    def test_session_state_with_character_states(self):
        """Test session state with character states."""
        character = CharacterState(character_id="char_1", name="Alice")
        session = SessionState(
            session_id="session_123",
            user_id="user_456",
            character_states={"char_1": character}
        )
        self.assertTrue(session.validate())

    def test_session_state_serialization(self):
        """Test session state serialization to JSON."""
        session = SessionState(
            session_id="session_123",
            user_id="user_456",
            current_scenario_id="scenario_1"
        )

        # Test to_dict
        data = session.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["session_id"], "session_123")
        self.assertEqual(data["user_id"], "user_456")

        # Test to_json
        json_str = session.to_json()
        self.assertIsInstance(json_str, str)

        # Verify JSON is valid
        parsed = json.loads(json_str)
        self.assertEqual(parsed["session_id"], "session_123")

    def test_session_state_deserialization(self):
        """Test session state deserialization from JSON."""
        original_session = SessionState(
            session_id="session_123",
            user_id="user_456",
            current_scenario_id="scenario_1"
        )

        # Serialize and deserialize
        json_str = original_session.to_json()
        restored_session = SessionState.from_json(json_str)

        self.assertEqual(restored_session.session_id, original_session.session_id)
        self.assertEqual(restored_session.user_id, original_session.user_id)
        self.assertEqual(restored_session.current_scenario_id, original_session.current_scenario_id)

    def test_session_state_complex_serialization(self):
        """Test session state serialization with complex nested objects."""
        # Create a complex session state
        character = CharacterState(character_id="char_1", name="Alice")
        character.add_memory("First meeting", 0.8, ["positive"])

        progress = TherapeuticProgress(user_id="user_456")
        progress.add_goal("Reduce Anxiety", "Learn coping strategies")

        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.CALM,
            intensity=0.6
        )

        narrative_context = NarrativeContext(session_id="session_123")
        narrative_context.add_choice("Go left", "choice_1", ["entered forest"])

        session = SessionState(
            session_id="session_123",
            user_id="user_456",
            character_states={"char_1": character},
            therapeutic_progress=progress,
            emotional_state=emotional_state,
            narrative_context=narrative_context
        )

        # Test serialization and deserialization
        json_str = session.to_json()
        restored_session = SessionState.from_json(json_str)

        self.assertEqual(restored_session.session_id, session.session_id)
        self.assertEqual(len(restored_session.character_states), 1)
        self.assertIsNotNone(restored_session.therapeutic_progress)
        self.assertIsNotNone(restored_session.emotional_state)
        self.assertIsNotNone(restored_session.narrative_context)


class TestValidationUtilities(unittest.TestCase):
    """Test cases for validation utility functions."""

    def test_validate_all_models(self):
        """Test the validate_all_models utility function."""
        self.assertTrue(validate_all_models())


if __name__ == '__main__':
    unittest.main()
