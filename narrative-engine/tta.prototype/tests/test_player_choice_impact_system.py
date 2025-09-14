"""
Unit tests for Player Choice Impact System

This module contains comprehensive unit tests for the player choice impact system,
including tests for choice impact calculation, timeline integration, consequence
propagation, preference tracking, and visualization feedback mechanisms.
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

# Add the core path to sys.path for imports
core_path = Path(__file__).parent.parent / "core"
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

models_path = Path(__file__).parent.parent / "models"
if str(models_path) not in sys.path:
    sys.path.insert(0, str(models_path))

from living_worlds_models import EventType, TimelineEvent, ValidationError
from narrative_branching import ChoiceOption, ChoiceType, ImpactLevel
from player_choice_impact_system import (
    ChoiceCategory,
    ChoiceImpact,
    ChoiceImpactVisualizer,
    ConsequencePropagation,
    ImpactScope,
    PlayerChoice,
    PlayerChoiceImpactSystem,
    PlayerPreference,
    PlayerPreferenceTracker,
    PreferenceStrength,
)


class TestPlayerChoice(unittest.TestCase):
    """Test PlayerChoice data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_choice_data = {
            "player_id": "player_123",
            "world_id": "world_456",
            "choice_text": "Help the injured character",
            "choice_category": ChoiceCategory.SOCIAL,
            "confidence_level": 0.8,
            "response_time": 5.2
        }

    def test_player_choice_creation(self):
        """Test creating a valid PlayerChoice."""
        choice = PlayerChoice(**self.valid_choice_data)

        self.assertEqual(choice.player_id, "player_123")
        self.assertEqual(choice.world_id, "world_456")
        self.assertEqual(choice.choice_text, "Help the injured character")
        self.assertEqual(choice.choice_category, ChoiceCategory.SOCIAL)
        self.assertEqual(choice.confidence_level, 0.8)
        self.assertEqual(choice.response_time, 5.2)
        self.assertIsInstance(choice.timestamp, datetime)

    def test_player_choice_validation_success(self):
        """Test successful validation of PlayerChoice."""
        choice = PlayerChoice(**self.valid_choice_data)
        self.assertTrue(choice.validate())

    def test_player_choice_validation_empty_fields(self):
        """Test validation failure with empty required fields."""
        # Empty player_id
        invalid_data = self.valid_choice_data.copy()
        invalid_data["player_id"] = ""
        choice = PlayerChoice(**invalid_data)

        with self.assertRaises(ValidationError):
            choice.validate()

        # Empty world_id
        invalid_data = self.valid_choice_data.copy()
        invalid_data["world_id"] = ""
        choice = PlayerChoice(**invalid_data)

        with self.assertRaises(ValidationError):
            choice.validate()

        # Empty choice_text
        invalid_data = self.valid_choice_data.copy()
        invalid_data["choice_text"] = ""
        choice = PlayerChoice(**invalid_data)

        with self.assertRaises(ValidationError):
            choice.validate()

    def test_player_choice_validation_invalid_ranges(self):
        """Test validation failure with invalid value ranges."""
        # Invalid confidence_level
        invalid_data = self.valid_choice_data.copy()
        invalid_data["confidence_level"] = 1.5
        choice = PlayerChoice(**invalid_data)

        with self.assertRaises(ValidationError):
            choice.validate()

        # Negative response_time
        invalid_data = self.valid_choice_data.copy()
        invalid_data["response_time"] = -1.0
        choice = PlayerChoice(**invalid_data)

        with self.assertRaises(ValidationError):
            choice.validate()

    def test_player_choice_serialization(self):
        """Test PlayerChoice serialization and deserialization."""
        choice = PlayerChoice(**self.valid_choice_data)

        # Test to_dict
        choice_dict = choice.to_dict()
        self.assertIsInstance(choice_dict, dict)
        self.assertEqual(choice_dict["player_id"], "player_123")
        self.assertEqual(choice_dict["choice_category"], "social")
        self.assertIsInstance(choice_dict["timestamp"], str)

        # Test from_dict
        reconstructed_choice = PlayerChoice.from_dict(choice_dict)
        self.assertEqual(reconstructed_choice.player_id, choice.player_id)
        self.assertEqual(reconstructed_choice.choice_category, choice.choice_category)
        self.assertEqual(reconstructed_choice.timestamp, choice.timestamp)


class TestChoiceImpact(unittest.TestCase):
    """Test ChoiceImpact data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.choice_impact = ChoiceImpact(
            choice_id="choice_123",
            impact_scope=ImpactScope.LOCAL,
            impact_strength=0.7
        )

    def test_choice_impact_creation(self):
        """Test creating a ChoiceImpact."""
        self.assertEqual(self.choice_impact.choice_id, "choice_123")
        self.assertEqual(self.choice_impact.impact_scope, ImpactScope.LOCAL)
        self.assertEqual(self.choice_impact.impact_strength, 0.7)
        self.assertIsInstance(self.choice_impact.affected_entities, dict)
        self.assertIsInstance(self.choice_impact.timeline_events_created, list)

    def test_add_affected_entity(self):
        """Test adding affected entities."""
        self.choice_impact.add_affected_entity("character", "char_1")
        self.choice_impact.add_affected_entity("character", "char_2")
        self.choice_impact.add_affected_entity("location", "loc_1")

        self.assertIn("character", self.choice_impact.affected_entities)
        self.assertIn("location", self.choice_impact.affected_entities)
        self.assertEqual(len(self.choice_impact.affected_entities["character"]), 2)
        self.assertEqual(len(self.choice_impact.affected_entities["location"]), 1)

        # Test duplicate prevention
        self.choice_impact.add_affected_entity("character", "char_1")
        self.assertEqual(len(self.choice_impact.affected_entities["character"]), 2)

    def test_get_total_affected_entities(self):
        """Test counting total affected entities."""
        self.assertEqual(self.choice_impact.get_total_affected_entities(), 0)

        self.choice_impact.add_affected_entity("character", "char_1")
        self.choice_impact.add_affected_entity("character", "char_2")
        self.choice_impact.add_affected_entity("location", "loc_1")

        self.assertEqual(self.choice_impact.get_total_affected_entities(), 3)

    def test_choice_impact_validation(self):
        """Test ChoiceImpact validation."""
        # Valid impact
        self.assertTrue(self.choice_impact.validate())

        # Invalid choice_id
        invalid_impact = ChoiceImpact(choice_id="", impact_strength=0.5)
        with self.assertRaises(ValidationError):
            invalid_impact.validate()

        # Invalid impact_strength
        invalid_impact = ChoiceImpact(choice_id="test", impact_strength=1.5)
        with self.assertRaises(ValidationError):
            invalid_impact.validate()


class TestPlayerPreference(unittest.TestCase):
    """Test PlayerPreference data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.preference = PlayerPreference(
            player_id="player_123",
            category=ChoiceCategory.SOCIAL,
            preference_value=0.6,
            strength=PreferenceStrength.MODERATE,
            confidence=0.7,
            evidence_count=5
        )

    def test_player_preference_creation(self):
        """Test creating a PlayerPreference."""
        self.assertEqual(self.preference.player_id, "player_123")
        self.assertEqual(self.preference.category, ChoiceCategory.SOCIAL)
        self.assertEqual(self.preference.preference_value, 0.6)
        self.assertEqual(self.preference.strength, PreferenceStrength.MODERATE)
        self.assertEqual(self.preference.confidence, 0.7)
        self.assertEqual(self.preference.evidence_count, 5)

    def test_player_preference_validation(self):
        """Test PlayerPreference validation."""
        # Valid preference
        self.assertTrue(self.preference.validate())

        # Invalid player_id
        invalid_pref = PlayerPreference(player_id="", category=ChoiceCategory.SOCIAL)
        with self.assertRaises(ValidationError):
            invalid_pref.validate()

        # Invalid preference_value
        invalid_pref = PlayerPreference(
            player_id="test", category=ChoiceCategory.SOCIAL, preference_value=2.0
        )
        with self.assertRaises(ValidationError):
            invalid_pref.validate()

        # Invalid confidence
        invalid_pref = PlayerPreference(
            player_id="test", category=ChoiceCategory.SOCIAL, confidence=1.5
        )
        with self.assertRaises(ValidationError):
            invalid_pref.validate()

        # Invalid evidence_count
        invalid_pref = PlayerPreference(
            player_id="test", category=ChoiceCategory.SOCIAL, evidence_count=-1
        )
        with self.assertRaises(ValidationError):
            invalid_pref.validate()

    def test_update_preference(self):
        """Test updating preference with new evidence."""
        initial_value = self.preference.preference_value
        initial_count = self.preference.evidence_count

        # Update with positive evidence
        self.preference.update_preference(0.8, weight=1.0)

        self.assertGreater(self.preference.preference_value, initial_value)
        self.assertEqual(self.preference.evidence_count, initial_count + 1)

        # Test strength update with more evidence
        for _ in range(10):
            self.preference.update_preference(0.7, weight=1.0)

        self.assertEqual(self.preference.strength, PreferenceStrength.VERY_STRONG)

    def test_preference_strength_calculation(self):
        """Test automatic strength calculation based on evidence."""
        # Start with weak preference
        pref = PlayerPreference(
            player_id="test", category=ChoiceCategory.SOCIAL,
            preference_value=0.2, evidence_count=1
        )
        pref.update_preference(0.3)
        self.assertEqual(pref.strength, PreferenceStrength.WEAK)

        # Build to moderate
        for _ in range(3):
            pref.update_preference(0.4)
        self.assertEqual(pref.strength, PreferenceStrength.MODERATE)

        # Build to strong
        for _ in range(3):
            pref.update_preference(0.6)
        self.assertEqual(pref.strength, PreferenceStrength.STRONG)


class TestConsequencePropagation(unittest.TestCase):
    """Test ConsequencePropagation system."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_timeline_engine = Mock()
        self.mock_world_state_manager = Mock()
        self.propagation = ConsequencePropagation(
            self.mock_timeline_engine, self.mock_world_state_manager
        )

        # Mock world state
        self.mock_world_state = Mock()
        self.mock_world_state.active_characters = {
            "char_1": {"location_id": "loc_1", "relationships": {"char_2": 0.8}},
            "char_2": {"location_id": "loc_1", "relationships": {"char_1": 0.7}}
        }
        self.mock_world_state.active_locations = {
            "loc_1": {"connected_locations": ["loc_2"]},
            "loc_2": {"connected_locations": ["loc_1"]}
        }
        self.mock_world_state.active_objects = {
            "obj_1": {"location_id": "loc_1", "owner_id": "char_1"}
        }

        self.mock_world_state_manager.get_world_state.return_value = self.mock_world_state

    def test_propagation_rules_initialization(self):
        """Test initialization of propagation rules."""
        rules = self.propagation.propagation_rules

        self.assertIn("social_interaction", rules)
        self.assertIn("environmental_change", rules)
        self.assertIn("emotional_expression", rules)
        self.assertIn("creative_action", rules)

        # Check rule structure
        social_rules = rules["social_interaction"]
        self.assertIn("primary_entities", social_rules)
        self.assertIn("propagation_decay", social_rules)
        self.assertIn("max_hops", social_rules)

    def test_get_propagation_type(self):
        """Test mapping choice categories to propagation types."""
        self.assertEqual(
            self.propagation._get_propagation_type(ChoiceCategory.SOCIAL),
            "social_interaction"
        )
        self.assertEqual(
            self.propagation._get_propagation_type(ChoiceCategory.EXPLORATION),
            "environmental_change"
        )
        self.assertEqual(
            self.propagation._get_propagation_type(ChoiceCategory.EMOTIONAL),
            "emotional_expression"
        )
        self.assertEqual(
            self.propagation._get_propagation_type(ChoiceCategory.CREATIVE),
            "creative_action"
        )

    def test_find_connected_entities_character(self):
        """Test finding entities connected to a character."""
        connected = self.propagation._find_connected_entities(
            "character", "char_1", self.mock_world_state, {}
        )

        # Should find location and other character
        entity_types = [conn[0] for conn in connected]
        entity_ids = [conn[1] for conn in connected]

        self.assertIn("location", entity_types)
        self.assertIn("character", entity_types)
        self.assertIn("loc_1", entity_ids)
        self.assertIn("char_2", entity_ids)

    def test_find_connected_entities_location(self):
        """Test finding entities connected to a location."""
        connected = self.propagation._find_connected_entities(
            "location", "loc_1", self.mock_world_state, {}
        )

        entity_types = [conn[0] for conn in connected]
        entity_ids = [conn[1] for conn in connected]

        self.assertIn("character", entity_types)
        self.assertIn("object", entity_types)
        self.assertIn("location", entity_types)
        self.assertIn("char_1", entity_ids)
        self.assertIn("obj_1", entity_ids)
        self.assertIn("loc_2", entity_ids)

    def test_create_propagation_event(self):
        """Test creating propagation events."""
        choice = PlayerChoice(
            player_id="player_1",
            world_id="world_1",
            choice_text="Test choice",
            choice_category=ChoiceCategory.SOCIAL
        )

        impact = ChoiceImpact(choice_id=choice.choice_id)

        event = self.propagation._create_propagation_event(
            choice, impact, "character", "char_1", 0.8, 1
        )

        self.assertIsInstance(event, TimelineEvent)
        self.assertEqual(event.event_type, EventType.RELATIONSHIP_CHANGE)
        self.assertIn("char_1", event.participants)
        self.assertIn("player_1", event.participants)
        self.assertEqual(event.significance_level, 8)  # 0.8 * 10
        self.assertIn("player_choice", event.tags)
        self.assertIn("social", event.tags)
        self.assertIn("hop_1", event.tags)

    @patch('player_choice_impact_system.logger')
    def test_propagate_consequences_success(self, mock_logger):
        """Test successful consequence propagation."""
        choice = PlayerChoice(
            player_id="player_1",
            world_id="world_1",
            choice_text="Help character",
            choice_category=ChoiceCategory.SOCIAL
        )

        impact = ChoiceImpact(choice_id=choice.choice_id)
        impact.add_affected_entity("character", "char_1")

        # Mock timeline engine to return True for add_event
        self.mock_timeline_engine.add_event.return_value = True

        events = self.propagation.propagate_consequences(choice, impact, "world_1")

        self.assertIsInstance(events, list)
        self.mock_world_state_manager.get_world_state.assert_called_with("world_1")

        # Should have created propagation chain
        self.assertIsInstance(impact.propagation_chain, list)

    def test_propagate_consequences_no_world(self):
        """Test propagation when world is not found."""
        self.mock_world_state_manager.get_world_state.return_value = None

        choice = PlayerChoice(
            player_id="player_1",
            world_id="nonexistent_world",
            choice_text="Test choice",
            choice_category=ChoiceCategory.SOCIAL
        )

        impact = ChoiceImpact(choice_id=choice.choice_id)

        events = self.propagation.propagate_consequences(choice, impact, "nonexistent_world")

        self.assertEqual(events, [])


class TestPlayerPreferenceTracker(unittest.TestCase):
    """Test PlayerPreferenceTracker system."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracker = PlayerPreferenceTracker()

        self.test_choice = PlayerChoice(
            player_id="player_123",
            world_id="world_456",
            choice_text="Help the injured character",
            choice_category=ChoiceCategory.SOCIAL,
            confidence_level=0.8,
            response_time=3.5,
            emotional_state_before={"happiness": 0.6, "anxiety": 0.2}
        )

    def test_track_choice_initialization(self):
        """Test tracking first choice for a player."""
        self.tracker.track_choice(self.test_choice)

        self.assertIn("player_123", self.tracker.player_preferences)
        self.assertIn("player_123", self.tracker.choice_history)
        self.assertEqual(len(self.tracker.choice_history["player_123"]), 1)
        self.assertIn(ChoiceCategory.SOCIAL, self.tracker.player_preferences["player_123"])

    def test_calculate_choice_evidence(self):
        """Test calculating evidence from choice characteristics."""
        evidence = self.tracker._calculate_choice_evidence(self.test_choice)

        # Should be positive due to high confidence and positive emotions
        self.assertGreater(evidence, 0.0)
        self.assertLessEqual(evidence, 1.0)

        # Test with negative choice
        negative_choice = PlayerChoice(
            player_id="player_123",
            world_id="world_456",
            choice_text="Reluctantly avoid the situation",
            choice_category=ChoiceCategory.SOCIAL,
            confidence_level=0.3,
            emotional_state_before={"anxiety": 0.8, "happiness": 0.1}
        )

        negative_evidence = self.tracker._calculate_choice_evidence(negative_choice)
        self.assertLess(negative_evidence, evidence)

    def test_update_context_factors(self):
        """Test updating contextual factors."""
        preference = PlayerPreference(
            player_id="player_123",
            category=ChoiceCategory.SOCIAL
        )

        self.tracker._update_context_factors(preference, self.test_choice)

        # Should have time and emotion factors
        self.assertIn("happiness", preference.context_factors)

        # Time factor depends on when test runs, but should be one of the time periods
        time_factors = ["morning", "afternoon", "evening", "night"]
        has_time_factor = any(factor in preference.context_factors for factor in time_factors)
        self.assertTrue(has_time_factor)

    def test_analyze_preference_patterns(self):
        """Test analyzing patterns in player choices."""
        player_id = "player_123"

        # Add multiple choices of the same category
        for i in range(5):
            choice = PlayerChoice(
                player_id=player_id,
                world_id="world_456",
                choice_text=f"Social choice {i}",
                choice_category=ChoiceCategory.SOCIAL,
                confidence_level=0.8,
                response_time=2.0
            )
            self.tracker.track_choice(choice)

        # Add one choice of different category
        therapeutic_choice = PlayerChoice(
            player_id=player_id,
            world_id="world_456",
            choice_text="Therapeutic choice",
            choice_category=ChoiceCategory.THERAPEUTIC,
            confidence_level=0.6,
            response_time=8.0
        )
        self.tracker.track_choice(therapeutic_choice)

        # Analyze patterns
        self.tracker._analyze_preference_patterns(player_id)

        # Social category should have strong preference due to frequency
        social_pref = self.tracker.player_preferences[player_id][ChoiceCategory.SOCIAL]
        self.assertGreater(social_pref.preference_value, 0.5)

        # Quick response times should increase confidence
        self.assertGreater(social_pref.confidence, 0.5)

    def test_get_preference_influence(self):
        """Test calculating preference influence."""
        player_id = "player_123"

        # Create a strong preference
        strong_pref = PlayerPreference(
            player_id=player_id,
            category=ChoiceCategory.SOCIAL,
            preference_value=0.8,
            strength=PreferenceStrength.STRONG,
            confidence=0.9
        )

        self.tracker.player_preferences[player_id] = {ChoiceCategory.SOCIAL: strong_pref}

        influence = self.tracker.get_preference_influence(player_id, ChoiceCategory.SOCIAL)

        # Should be high influence (0.8 * 0.8 * 0.9 = 0.576)
        self.assertGreater(influence, 0.5)

        # Test non-existent preference
        no_influence = self.tracker.get_preference_influence(player_id, ChoiceCategory.CREATIVE)
        self.assertEqual(no_influence, 0.0)

    def test_get_world_evolution_guidance(self):
        """Test generating world evolution guidance."""
        player_id = "player_123"

        # Create preferences
        strong_social = PlayerPreference(
            player_id=player_id,
            category=ChoiceCategory.SOCIAL,
            preference_value=0.8,
            strength=PreferenceStrength.STRONG,
            confidence=0.9
        )

        weak_avoided = PlayerPreference(
            player_id=player_id,
            category=ChoiceCategory.ACTION,
            preference_value=-0.6,
            strength=PreferenceStrength.STRONG,
            confidence=0.8
        )

        self.tracker.player_preferences[player_id] = {
            ChoiceCategory.SOCIAL: strong_social,
            ChoiceCategory.ACTION: weak_avoided
        }

        guidance = self.tracker.get_world_evolution_guidance(player_id)

        self.assertIn("preferred_content_types", guidance)
        self.assertIn("avoided_content_types", guidance)
        self.assertIn("emphasis_areas", guidance)
        self.assertIn("adaptation_suggestions", guidance)

        self.assertIn("social", guidance["preferred_content_types"])
        self.assertIn("action", guidance["avoided_content_types"])
        self.assertGreater(len(guidance["adaptation_suggestions"]), 0)


class TestChoiceImpactVisualizer(unittest.TestCase):
    """Test ChoiceImpactVisualizer system."""

    def setUp(self):
        """Set up test fixtures."""
        self.visualizer = ChoiceImpactVisualizer()

        self.test_choice = PlayerChoice(
            player_id="player_123",
            world_id="world_456",
            choice_text="Help the injured character",
            choice_category=ChoiceCategory.SOCIAL
        )

        self.test_impact = ChoiceImpact(
            choice_id=self.test_choice.choice_id,
            impact_strength=0.7
        )
        self.test_impact.add_affected_entity("character", "char_1")
        self.test_impact.add_affected_entity("character", "char_2")
        self.test_impact.relationship_changes = {"char_1": 0.3, "char_2": -0.2}
        self.test_impact.world_state_changes = {"mood_improved": True, "trust_level": 0.5}
        self.test_impact.long_term_consequences = ["stronger_friendship", "increased_reputation"]

    def test_visualization_templates_initialization(self):
        """Test initialization of visualization templates."""
        templates = self.visualizer.visualization_templates

        self.assertIn("immediate_feedback", templates)
        self.assertIn("relationship_changes", templates)
        self.assertIn("world_changes", templates)
        self.assertIn("long_term_preview", templates)

        # Check template structure
        immediate = templates["immediate_feedback"]
        self.assertIn("template", immediate)
        self.assertIn("icons", immediate)

    def test_generate_immediate_feedback(self):
        """Test generating immediate feedback."""
        feedback = self.visualizer.generate_immediate_feedback(self.test_choice, self.test_impact)

        self.assertEqual(feedback["type"], "immediate_feedback")
        self.assertIn("text", feedback)
        self.assertEqual(feedback["impact_level"], "high")  # 0.7 strength
        self.assertEqual(feedback["affected_count"], 2)
        self.assertIn("visual_elements", feedback)
        self.assertIn("🔶", feedback["text"])  # High impact icon

    def test_generate_relationship_feedback(self):
        """Test generating relationship feedback."""
        feedback = self.visualizer.generate_relationship_feedback(self.test_choice, self.test_impact)

        self.assertEqual(feedback["type"], "relationship_feedback")
        self.assertIn("relationships", feedback)
        self.assertEqual(len(feedback["relationships"]), 2)

        # Check relationship indicators
        relationships = feedback["relationships"]
        char_1_rel = next(r for r in relationships if r["character_id"] == "char_1")
        char_2_rel = next(r for r in relationships if r["character_id"] == "char_2")

        self.assertEqual(char_1_rel["indicator"], "💚")  # Positive change
        self.assertEqual(char_2_rel["indicator"], "💔")  # Negative change

    def test_generate_world_change_narrative(self):
        """Test generating world change narrative."""
        narrative = self.visualizer.generate_world_change_narrative(self.test_choice, self.test_impact)

        self.assertEqual(narrative["type"], "world_narrative")
        self.assertIn("text", narrative)
        self.assertIn("changes", narrative)
        self.assertGreater(len(narrative["changes"]), 0)

        # Should contain the template text
        self.assertIn("world around you shifts", narrative["text"])

    def test_generate_long_term_preview(self):
        """Test generating long-term consequence preview."""
        preview = self.visualizer.generate_long_term_preview(self.test_choice, self.test_impact)

        self.assertEqual(preview["type"], "long_term_preview")
        self.assertIn("text", preview)
        self.assertIn("consequences", preview)
        self.assertEqual(len(preview["consequences"]), 2)
        self.assertIn("uncertainty_level", preview)

        # Should contain uncertainty words
        self.assertIn("may", preview["text"])
        self.assertIn("stronger_friendship", preview["text"])

    def test_generate_comprehensive_feedback(self):
        """Test generating comprehensive feedback."""
        feedback = self.visualizer.generate_comprehensive_feedback(self.test_choice, self.test_impact)

        self.assertIn("choice_id", feedback)
        self.assertIn("timestamp", feedback)
        self.assertIn("components", feedback)
        self.assertIn("summary", feedback)

        components = feedback["components"]
        self.assertIn("immediate", components)
        self.assertIn("relationships", components)
        self.assertIn("world_changes", components)
        self.assertIn("long_term", components)

        # Summary should combine information
        summary = feedback["summary"]
        self.assertIn("high impact", summary)
        self.assertIn("2 relationships", summary)

    def test_get_impact_color(self):
        """Test impact color mapping."""
        self.assertEqual(self.visualizer._get_impact_color(0.9), "#FF4444")  # Very high
        self.assertEqual(self.visualizer._get_impact_color(0.7), "#FF8844")  # High
        self.assertEqual(self.visualizer._get_impact_color(0.4), "#FFDD44")  # Medium
        self.assertEqual(self.visualizer._get_impact_color(0.2), "#44DDFF")  # Low

    def test_categorize_world_change(self):
        """Test categorizing world state changes."""
        self.assertEqual(
            self.visualizer._categorize_world_change("location_mood", True),
            "environmental"
        )
        self.assertEqual(
            self.visualizer._categorize_world_change("character_relationship", 0.5),
            "social"
        )
        self.assertEqual(
            self.visualizer._categorize_world_change("emotional_state", -0.3),
            "emotional"
        )
        self.assertEqual(
            self.visualizer._categorize_world_change("unknown_change", "value"),
            "environmental"  # Default
        )

    def test_get_change_verb(self):
        """Test getting appropriate change verbs."""
        self.assertEqual(self.visualizer._get_change_verb(True), "activates")
        self.assertEqual(self.visualizer._get_change_verb(False), "settles")
        self.assertEqual(self.visualizer._get_change_verb(0.5), "brightens")
        self.assertEqual(self.visualizer._get_change_verb(-0.3), "darkens")
        self.assertEqual(self.visualizer._get_change_verb(0.0), "stabilizes")
        self.assertEqual(self.visualizer._get_change_verb("string"), "transforms")

    def test_get_uncertainty_word(self):
        """Test getting uncertainty words based on impact strength."""
        self.assertEqual(self.visualizer._get_uncertainty_word(0.9), "will likely")
        self.assertEqual(self.visualizer._get_uncertainty_word(0.7), "may")
        self.assertEqual(self.visualizer._get_uncertainty_word(0.4), "might")
        self.assertEqual(self.visualizer._get_uncertainty_word(0.2), "could possibly")


class TestPlayerChoiceImpactSystem(unittest.TestCase):
    """Test PlayerChoiceImpactSystem integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_timeline_engine = Mock()
        self.mock_world_state_manager = Mock()
        self.mock_character_system = Mock()
        self.mock_narrative_branching = Mock()

        self.system = PlayerChoiceImpactSystem(
            self.mock_timeline_engine,
            self.mock_world_state_manager,
            self.mock_character_system,
            self.mock_narrative_branching
        )

        # Mock world state
        self.mock_world_state = Mock()
        self.mock_world_state.active_characters = {
            "char_1": {"location_id": "loc_1", "relationships": {}, "emotional_state": {}}
        }
        self.mock_world_state_manager.get_world_state.return_value = self.mock_world_state

        # Mock narrative consequence
        self.mock_consequence = Mock()
        self.mock_consequence.consequence_id = "consequence_123"
        self.mock_consequence.impact_level = ImpactLevel.MODERATE
        self.mock_consequence.therapeutic_impact = 0.5
        self.mock_consequence.emotional_impact = {"char_1": 0.3}
        self.mock_consequence.world_state_changes = {"mood": "improved"}
        self.mock_consequence.affected_entities = ["char_1"]
        self.mock_consequence.narrative_flags = ["friendship_building"]

        self.mock_narrative_branching.process_user_choice.return_value = self.mock_consequence

    def test_system_initialization(self):
        """Test system initialization."""
        self.assertIsNotNone(self.system.consequence_propagation)
        self.assertIsNotNone(self.system.preference_tracker)
        self.assertIsNotNone(self.system.impact_visualizer)
        self.assertIsInstance(self.system.processed_choices, dict)
        self.assertIsInstance(self.system.choice_impacts, dict)

    def test_map_choice_type_to_category(self):
        """Test mapping choice types to categories."""
        self.assertEqual(
            self.system._map_choice_type_to_category(ChoiceType.DIALOGUE),
            ChoiceCategory.SOCIAL
        )
        self.assertEqual(
            self.system._map_choice_type_to_category(ChoiceType.THERAPEUTIC),
            ChoiceCategory.THERAPEUTIC
        )
        self.assertEqual(
            self.system._map_choice_type_to_category(ChoiceType.EXPLORATION),
            ChoiceCategory.EXPLORATION
        )

    def test_determine_impact_scope(self):
        """Test determining impact scope."""
        # High confidence + strong emotion = regional
        choice = PlayerChoice(
            player_id="player_1",
            world_id="world_1",
            choice_text="Test",
            confidence_level=0.9,
            emotional_state_before={"happiness": 0.8}
        )
        scope = self.system._determine_impact_scope(choice, {})
        self.assertEqual(scope, ImpactScope.REGIONAL)

        # Therapeutic choice = regional
        therapeutic_choice = PlayerChoice(
            player_id="player_1",
            world_id="world_1",
            choice_text="Test",
            choice_category=ChoiceCategory.THERAPEUTIC
        )
        scope = self.system._determine_impact_scope(therapeutic_choice, {})
        self.assertEqual(scope, ImpactScope.REGIONAL)

        # Social choice = local
        social_choice = PlayerChoice(
            player_id="player_1",
            world_id="world_1",
            choice_text="Test",
            choice_category=ChoiceCategory.SOCIAL
        )
        scope = self.system._determine_impact_scope(social_choice, {})
        self.assertEqual(scope, ImpactScope.LOCAL)

        # Default = personal
        default_choice = PlayerChoice(
            player_id="player_1",
            world_id="world_1",
            choice_text="Test"
        )
        scope = self.system._determine_impact_scope(default_choice, {})
        self.assertEqual(scope, ImpactScope.PERSONAL)

    def test_calculate_impact_strength(self):
        """Test calculating impact strength."""
        # High confidence, quick response, strong emotion, therapeutic
        choice = PlayerChoice(
            player_id="player_1",
            world_id="world_1",
            choice_text="Test",
            choice_category=ChoiceCategory.THERAPEUTIC,
            confidence_level=0.9,
            response_time=3.0,
            emotional_state_before={"happiness": 0.8}
        )

        strength = self.system._calculate_impact_strength(choice, {})

        # Should be high due to all positive factors
        self.assertGreater(strength, 0.7)
        self.assertLessEqual(strength, 1.0)

        # Low confidence, slow response, weak emotion
        weak_choice = PlayerChoice(
            player_id="player_1",
            world_id="world_1",
            choice_text="Test",
            confidence_level=0.2,
            response_time=35.0,
            emotional_state_before={"happiness": 0.1}
        )

        weak_strength = self.system._calculate_impact_strength(weak_choice, {})
        self.assertLess(weak_strength, strength)

    @patch('player_choice_impact_system.logger')
    def test_process_player_choice_success(self, mock_logger):
        """Test successful player choice processing."""
        choice_option = ChoiceOption(
            choice_id="choice_123",
            choice_text="Help the character",
            choice_type=ChoiceType.DIALOGUE,
            therapeutic_weight=0.6
        )

        context = {
            "player_id": "player_1",
            "world_id": "world_1",
            "characters_present": ["char_1"],
            "current_location": "loc_1",
            "emotional_state": {"happiness": 0.6},
            "confidence_level": 0.8,
            "response_time": 4.5
        }

        # Mock propagation to return empty list
        with patch.object(self.system.consequence_propagation, 'propagate_consequences', return_value=[]):
            result = self.system.process_player_choice(choice_option, context)

        self.assertTrue(result["success"])
        self.assertIn("choice_id", result)
        self.assertIn("impact", result)
        self.assertIn("feedback", result)
        self.assertIn("world_evolution_guidance", result)
        self.assertIn("narrative_consequence", result)

        # Check that choice was stored
        choice_id = result["choice_id"]
        self.assertIn(choice_id, self.system.processed_choices)
        self.assertIn(choice_id, self.system.choice_impacts)

        # Check impact details
        impact_info = result["impact"]
        self.assertIn("scope", impact_info)
        self.assertIn("strength", impact_info)
        self.assertIn("affected_entities", impact_info)

    def test_get_choice_impact_history(self):
        """Test getting choice impact history."""
        # Add some test choices
        for i in range(3):
            choice = PlayerChoice(
                player_id="player_1",
                world_id="world_1",
                choice_text=f"Choice {i}",
                timestamp=datetime.now() - timedelta(hours=i)
            )
            impact = ChoiceImpact(choice_id=choice.choice_id, impact_strength=0.5 + i * 0.1)
            impact.timeline_events_created = [f"event_{i}_1", f"event_{i}_2"]

            self.system.processed_choices[choice.choice_id] = choice
            self.system.choice_impacts[choice.choice_id] = impact

        history = self.system.get_choice_impact_history("player_1", limit=2)

        self.assertEqual(len(history), 2)

        # Should be sorted by timestamp (most recent first)
        self.assertEqual(history[0]["choice_text"], "Choice 0")
        self.assertEqual(history[1]["choice_text"], "Choice 1")

        # Check history structure
        for entry in history:
            self.assertIn("choice_id", entry)
            self.assertIn("choice_text", entry)
            self.assertIn("category", entry)
            self.assertIn("timestamp", entry)
            self.assertIn("impact_strength", entry)
            self.assertIn("affected_entities", entry)
            self.assertIn("timeline_events", entry)

    def test_get_player_preference_summary(self):
        """Test getting player preference summary."""
        player_id = "player_1"

        # Add some preferences to the tracker
        strong_pref = PlayerPreference(
            player_id=player_id,
            category=ChoiceCategory.SOCIAL,
            preference_value=0.8,
            strength=PreferenceStrength.STRONG,
            confidence=0.9,
            evidence_count=8
        )

        weak_pref = PlayerPreference(
            player_id=player_id,
            category=ChoiceCategory.ACTION,
            preference_value=0.3,
            strength=PreferenceStrength.WEAK,
            confidence=0.4,
            evidence_count=2
        )

        self.system.preference_tracker.player_preferences[player_id] = {
            ChoiceCategory.SOCIAL: strong_pref,
            ChoiceCategory.ACTION: weak_pref
        }

        summary = self.system.get_player_preference_summary(player_id)

        self.assertEqual(summary["player_id"], player_id)
        self.assertEqual(summary["total_preferences"], 2)
        self.assertEqual(len(summary["strong_preferences"]), 1)
        self.assertEqual(len(summary["weak_preferences"]), 1)
        self.assertIn("evolution_guidance", summary)

        # Check preference details
        strong_pref_data = summary["strong_preferences"][0]
        self.assertEqual(strong_pref_data["category"], "social")
        self.assertEqual(strong_pref_data["strength"], "strong")

    def test_calculate_choice_impact_metrics(self):
        """Test calculating choice impact metrics."""
        world_id = "world_1"

        # Add test choices within time period
        for i in range(3):
            choice = PlayerChoice(
                player_id="player_1",
                world_id=world_id,
                choice_text=f"Choice {i}",
                choice_category=ChoiceCategory.SOCIAL if i < 2 else ChoiceCategory.THERAPEUTIC,
                response_time=5.0 + i,
                timestamp=datetime.now() - timedelta(hours=i)
            )

            impact = ChoiceImpact(choice_id=choice.choice_id, impact_strength=0.5 + i * 0.1)
            impact.add_affected_entity("character", f"char_{i}")
            impact.timeline_events_created = [f"event_{i}"]

            self.system.processed_choices[choice.choice_id] = choice
            self.system.choice_impacts[choice.choice_id] = impact

        # Add choice outside time period
        old_choice = PlayerChoice(
            player_id="player_1",
            world_id=world_id,
            choice_text="Old choice",
            timestamp=datetime.now() - timedelta(days=10)
        )
        self.system.processed_choices[old_choice.choice_id] = old_choice

        metrics = self.system.calculate_choice_impact_metrics(world_id, timedelta(days=1))

        self.assertEqual(metrics["world_id"], world_id)
        self.assertEqual(metrics["total_choices"], 3)  # Only recent choices

        metrics_data = metrics["metrics"]
        self.assertIn("average_impact_strength", metrics_data)
        self.assertIn("total_affected_entities", metrics_data)
        self.assertIn("category_distribution", metrics_data)
        self.assertIn("most_popular_category", metrics_data)

        # Social should be most popular (2 out of 3)
        self.assertEqual(metrics_data["most_popular_category"], "social")
        self.assertEqual(metrics_data["category_distribution"]["social"], 2)
        self.assertEqual(metrics_data["category_distribution"]["therapeutic"], 1)


if __name__ == '__main__':
    unittest.main()
