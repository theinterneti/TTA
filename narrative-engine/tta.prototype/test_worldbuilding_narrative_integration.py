"""
Integration tests for worldbuilding and narrative integration functionality.

This test suite validates the integration between worldbuilding and narrative progression,
including location unlocking mechanics, exploration systems, and world evolution based
on user actions and therapeutic progress.
"""

import logging
import unittest
from dataclasses import dataclass, field
from typing import Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the integration module
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock classes for testing
@dataclass
class MockSessionState:
    session_id: str = "test_session"
    user_id: str = "test_user"
    current_location_id: str = "starting_area"
    narrative_position: int = 0
    therapeutic_progress: Any = None
    visited_locations: list[str] = field(default_factory=list)

@dataclass
class MockTherapeuticProgress:
    user_id: str = "test_user"
    overall_progress_score: float = 0.0
    therapeutic_goals: list = field(default_factory=list)

@dataclass
class MockNarrativeContext:
    session_id: str = "test_session"
    current_location_id: str = "starting_area"
    therapeutic_opportunities: list[str] = field(default_factory=list)

@dataclass
class MockUserChoice:
    choice_id: str = "test_choice"
    choice_text: str = "Test choice"
    therapeutic_weight: float = 0.0

@dataclass
class MockNarrativeEvent:
    event_id: str = "test_event"
    event_type: str = "test_event_type"
    description: str = "Test event description"

# Patch imports in the integration module
import core.worldbuilding_narrative_integration as wni

wni.SessionState = MockSessionState
wni.TherapeuticProgress = MockTherapeuticProgress
wni.NarrativeContext = MockNarrativeContext
wni.UserChoice = MockUserChoice
wni.NarrativeEvent = MockNarrativeEvent

from core.worldbuilding_narrative_integration import (
    NarrativeWorldIntegrator,
    UnlockConditionType,
    create_basic_exploration_mechanic,
    create_exploration_condition,
    create_story_milestone_condition,
    create_therapeutic_progress_condition,
)
from core.worldbuilding_setting_management import (
    LocationType,
    WorldbuildingSettingManagement,
    create_sample_location,
)


class TestWorldbuildingNarrativeIntegration(unittest.TestCase):
    """Test suite for worldbuilding and narrative integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.world_manager = WorldbuildingSettingManagement()
        self.integrator = NarrativeWorldIntegrator(self.world_manager)

        # Create test locations
        self.starting_area = create_sample_location("starting_area", "Starting Area", LocationType.SAFE_SPACE)
        self.therapeutic_garden = create_sample_location("therapeutic_garden", "Therapeutic Garden", LocationType.THERAPEUTIC_ENVIRONMENT)
        self.challenge_mountain = create_sample_location("challenge_mountain", "Challenge Mountain", LocationType.CHALLENGE_AREA)

        # Add locations to world manager
        self.world_manager.locations_cache["starting_area"] = self.starting_area
        self.world_manager.locations_cache["therapeutic_garden"] = self.therapeutic_garden
        self.world_manager.locations_cache["challenge_mountain"] = self.challenge_mountain

        # Create test session state
        self.session_state = MockSessionState()
        self.session_state.therapeutic_progress = MockTherapeuticProgress()

        # Create test context
        self.context = MockNarrativeContext()

        logger.info("Test fixtures set up successfully")

    def test_location_unlock_conditions_creation(self):
        """Test creation of location unlock conditions."""
        logger.info("🧪 Testing location unlock conditions creation")

        # Create different types of unlock conditions
        therapeutic_condition = create_therapeutic_progress_condition(0.5, "Achieve 50% therapeutic progress")
        story_condition = create_story_milestone_condition(10, "Reach story position 10")
        exploration_condition = create_exploration_condition(3, "Explore 3 locations")

        # Validate conditions
        self.assertEqual(therapeutic_condition.condition_type, UnlockConditionType.THERAPEUTIC_PROGRESS)
        self.assertEqual(therapeutic_condition.target_value, 0.5)
        self.assertEqual(story_condition.condition_type, UnlockConditionType.STORY_MILESTONE)
        self.assertEqual(story_condition.target_value, 10)
        self.assertEqual(exploration_condition.condition_type, UnlockConditionType.EXPLORATION_COUNT)
        self.assertEqual(exploration_condition.target_value, 3)

        logger.info("✅ Location unlock conditions created successfully")

    def test_world_state_story_progression_connection(self):
        """Test connecting world state changes with story progression."""
        logger.info("🧪 Testing world state and story progression connection")

        # Create a therapeutic breakthrough event
        breakthrough_event = MockNarrativeEvent(
            event_id="breakthrough_001",
            event_type="therapeutic_breakthrough",
            description="User achieved significant therapeutic insight"
        )

        # Set up session state with some progress
        self.session_state.therapeutic_progress.overall_progress_score = 0.6

        # Connect world state with story progression
        world_changes = self.integrator.connect_world_state_with_story_progression(
            self.session_state, breakthrough_event
        )

        # Validate that world changes were generated
        self.assertGreater(len(world_changes), 0, "World changes should be generated from story progression")

        # Check that changes are related to therapeutic breakthrough
        breakthrough_change = next((change for change in world_changes
                                  if "breakthrough" in change.description.lower()), None)
        self.assertIsNotNone(breakthrough_change, "Should have breakthrough-related world change")

        logger.info("✅ World state successfully connected with story progression")

    def test_location_unlocking_mechanics(self):
        """Test implementation of location unlocking mechanics."""
        logger.info("🧪 Testing location unlocking mechanics")

        # Create unlock conditions for therapeutic garden
        unlock_conditions = [
            create_therapeutic_progress_condition(0.3, "Achieve basic therapeutic progress"),
            create_story_milestone_condition(5, "Complete initial story arc")
        ]

        # Implement unlock mechanics
        success = self.integrator.implement_location_unlocking_mechanics(
            "therapeutic_garden", unlock_conditions
        )
        self.assertTrue(success, "Location unlock mechanics should be implemented successfully")

        # Test condition checking with insufficient progress
        self.session_state.therapeutic_progress.overall_progress_score = 0.2
        self.session_state.narrative_position = 3

        unlockable = self.integrator.check_location_unlock_conditions(self.session_state, self.context)
        self.assertNotIn("therapeutic_garden", unlockable, "Garden should not be unlockable with insufficient progress")

        # Test condition checking with sufficient progress
        self.session_state.therapeutic_progress.overall_progress_score = 0.4
        self.session_state.narrative_position = 6

        unlockable = self.integrator.check_location_unlock_conditions(self.session_state, self.context)
        self.assertIn("therapeutic_garden", unlockable, "Garden should be unlockable with sufficient progress")

        logger.info("✅ Location unlocking mechanics working correctly")

    def test_exploration_mechanics(self):
        """Test location exploration mechanics."""
        logger.info("🧪 Testing exploration mechanics")

        # Create exploration mechanic for starting area
        exploration_mechanic = create_basic_exploration_mechanic(
            "starting_area",
            ["mindfulness", "self-reflection"],
            max_explorations=2
        )

        # Implement exploration mechanics
        success = self.integrator.implement_exploration_mechanics("starting_area", exploration_mechanic)
        self.assertTrue(success, "Exploration mechanics should be implemented successfully")

        # Test first exploration
        results = self.integrator.perform_location_exploration("starting_area", self.session_state)
        self.assertTrue(results["success"], "First exploration should succeed")
        self.assertEqual(results["exploration_count"], 1, "Exploration count should be 1")
        self.assertGreater(len(results["discoveries"]), 0, "Should have discoveries")

        # Test second exploration
        results = self.integrator.perform_location_exploration("starting_area", self.session_state)
        self.assertTrue(results["success"], "Second exploration should succeed")
        self.assertEqual(results["exploration_count"], 2, "Exploration count should be 2")

        # Test exploration limit reached
        results = self.integrator.perform_location_exploration("starting_area", self.session_state)
        self.assertFalse(results["success"], "Third exploration should fail due to limit")

        logger.info("✅ Exploration mechanics working correctly")

    def test_world_evolution_user_actions(self):
        """Test world evolution based on user actions and therapeutic progress."""
        logger.info("🧪 Testing world evolution based on user actions")

        # Create positive therapeutic choice
        positive_choice = MockUserChoice(
            choice_id="positive_001",
            choice_text="I choose to practice mindfulness",
            therapeutic_weight=0.8
        )

        # Set up therapeutic progress
        therapeutic_progress = MockTherapeuticProgress(
            user_id="test_user",
            overall_progress_score=0.7
        )

        # Test world evolution from positive choice
        evolution_events = self.integrator.add_world_evolution_based_on_user_actions(
            self.session_state, positive_choice, therapeutic_progress
        )

        self.assertGreater(len(evolution_events), 0, "Should generate evolution events from positive choice")

        # Check for positive evolution event
        positive_event = next((event for event in evolution_events
                             if event.therapeutic_impact > 0), None)
        self.assertIsNotNone(positive_event, "Should have positive therapeutic impact event")

        # Test negative choice
        negative_choice = MockUserChoice(
            choice_id="negative_001",
            choice_text="I choose to avoid the challenge",
            therapeutic_weight=-0.6
        )

        evolution_events = self.integrator.add_world_evolution_based_on_user_actions(
            self.session_state, negative_choice, therapeutic_progress
        )

        # Should still generate learning opportunities from negative choices
        self.assertGreater(len(evolution_events), 0, "Should generate learning events from negative choice")

        logger.info("✅ World evolution based on user actions working correctly")

    def test_narrative_event_world_changes(self):
        """Test different narrative events triggering world changes."""
        logger.info("🧪 Testing narrative events triggering world changes")

        # Test character interaction event
        character_event = MockNarrativeEvent(
            event_id="char_001",
            event_type="character_interaction",
            description="Meaningful conversation with therapeutic guide"
        )

        world_changes = self.integrator.connect_world_state_with_story_progression(
            self.session_state, character_event
        )

        self.assertGreater(len(world_changes), 0, "Character interaction should generate world changes")

        # Test story milestone event
        milestone_event = MockNarrativeEvent(
            event_id="milestone_001",
            event_type="story_milestone",
            description="Completed first therapeutic module"
        )

        world_changes = self.integrator.connect_world_state_with_story_progression(
            self.session_state, milestone_event
        )

        self.assertGreater(len(world_changes), 0, "Story milestone should generate world changes")

        # Test emotional change event
        emotional_event = MockNarrativeEvent(
            event_id="emotion_001",
            event_type="emotional_change",
            description="User experienced increased confidence"
        )

        world_changes = self.integrator.connect_world_state_with_story_progression(
            self.session_state, emotional_event
        )

        self.assertGreater(len(world_changes), 0, "Emotional change should generate world changes")

        logger.info("✅ Narrative events successfully triggering world changes")

    def test_therapeutic_progress_unlocks(self):
        """Test that therapeutic progress unlocks appropriate locations."""
        logger.info("🧪 Testing therapeutic progress unlocks")

        # Set up challenge mountain with high therapeutic progress requirement
        challenge_conditions = [
            create_therapeutic_progress_condition(0.8, "Achieve advanced therapeutic progress")
        ]

        self.integrator.implement_location_unlocking_mechanics("challenge_mountain", challenge_conditions)

        # Test with low progress - should not unlock
        self.session_state.therapeutic_progress.overall_progress_score = 0.5
        unlockable = self.integrator.check_location_unlock_conditions(self.session_state, self.context)
        self.assertNotIn("challenge_mountain", unlockable, "Challenge mountain should not unlock with low progress")

        # Test with high progress - should unlock
        self.session_state.therapeutic_progress.overall_progress_score = 0.9
        unlockable = self.integrator.check_location_unlock_conditions(self.session_state, self.context)
        self.assertIn("challenge_mountain", unlockable, "Challenge mountain should unlock with high progress")

        logger.info("✅ Therapeutic progress unlocks working correctly")

    def test_world_evolution_history_tracking(self):
        """Test that world evolution events are properly tracked."""
        logger.info("🧪 Testing world evolution history tracking")

        initial_history_count = len(self.integrator.world_evolution_history)

        # Create and apply evolution event
        positive_choice = MockUserChoice(therapeutic_weight=0.7)
        therapeutic_progress = MockTherapeuticProgress(overall_progress_score=0.6)

        self.integrator.add_world_evolution_based_on_user_actions(
            self.session_state, positive_choice, therapeutic_progress
        )

        # Check that history was updated
        final_history_count = len(self.integrator.world_evolution_history)
        self.assertGreater(final_history_count, initial_history_count,
                          "World evolution history should be updated")

        logger.info("✅ World evolution history tracking working correctly")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
