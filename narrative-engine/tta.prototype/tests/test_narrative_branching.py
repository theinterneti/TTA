"""
Integration tests for Narrative Branching and Choice Processing

This module contains comprehensive tests for the NarrativeBranchingChoice class,
covering choice generation, validation, consequence processing, and story impact calculation.
"""

# Import the classes to test
import sys
import unittest
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tta.prototype.core.narrative_branching import (
    BranchingPoint,
    ChoiceConsequence,
    ChoiceOption,
    ChoiceType,
    ConsequenceType,
    ImpactLevel,
    NarrativeBranch,
    NarrativeBranchingChoice,
    StoryImpact,
)


class TestNarrativeBranchingChoice(unittest.TestCase):
    """Test cases for NarrativeBranchingChoice."""

    def setUp(self):
        """Set up test fixtures."""
        self.branching_system = NarrativeBranchingChoice()
        self.test_session_id = "test_session_123"
        self.test_context = {
            "session_id": self.test_session_id,
            "location_id": "garden",
            "characters": ["therapist", "companion"],
            "emotional_state": {
                "primary_emotion": "anxious",
                "intensity": 0.8
            },
            "therapeutic_opportunities": ["anxiety_management"]
        }

    def test_initialization(self):
        """Test system initialization."""
        self.assertIsInstance(self.branching_system.therapeutic_choice_templates, dict)
        self.assertIn("anxiety_management", self.branching_system.therapeutic_choice_templates)
        self.assertIn("emotional_regulation", self.branching_system.therapeutic_choice_templates)
        self.assertIn("social_interaction", self.branching_system.therapeutic_choice_templates)

    def test_generate_choice_options_basic(self):
        """Test basic choice option generation."""
        choices = self.branching_system.generate_choice_options(self.test_context)

        self.assertIsInstance(choices, list)
        self.assertGreater(len(choices), 0)
        self.assertLessEqual(len(choices), 6)  # Should limit to 6 choices

        # Check that all choices are valid ChoiceOption objects
        for choice in choices:
            self.assertIsInstance(choice, ChoiceOption)
            self.assertTrue(choice.choice_id)
            self.assertTrue(choice.choice_text)
            self.assertIsInstance(choice.choice_type, ChoiceType)

    def test_generate_choice_options_garden_location(self):
        """Test choice generation for garden location."""
        choices = self.branching_system.generate_choice_options(self.test_context)

        # Should include garden-specific choices
        choice_texts = [choice.choice_text for choice in choices]
        garden_related = any("flower" in text.lower() or "bench" in text.lower()
                           for text in choice_texts)
        self.assertTrue(garden_related, "Should include garden-related choices")

    def test_generate_choice_options_high_anxiety(self):
        """Test choice generation for high anxiety state."""
        choices = self.branching_system.generate_choice_options(self.test_context)

        # Should include anxiety management choices
        therapeutic_choices = [c for c in choices if c.choice_type == ChoiceType.THERAPEUTIC]
        self.assertGreater(len(therapeutic_choices), 0, "Should include therapeutic choices for high anxiety")

        # Check for specific anxiety management techniques
        choice_texts = [choice.choice_text for choice in choices]
        breathing_related = any("breath" in text.lower() for text in choice_texts)
        grounding_related = any("grounding" in text.lower() for text in choice_texts)
        self.assertTrue(breathing_related or grounding_related,
                       "Should include anxiety management techniques")

    def test_generate_choice_options_character_interactions(self):
        """Test choice generation with characters present."""
        choices = self.branching_system.generate_choice_options(self.test_context)

        # Should include character interaction choices
        dialogue_choices = [c for c in choices if c.choice_type == ChoiceType.DIALOGUE]
        self.assertGreater(len(dialogue_choices), 0, "Should include dialogue choices with characters present")

        # Check for character-specific choices
        choice_texts = [choice.choice_text for choice in choices]
        character_related = any("therapist" in text.lower() or "companion" in text.lower()
                              for text in choice_texts)
        self.assertTrue(character_related, "Should include character-specific choices")

    def test_generate_choice_options_fallback(self):
        """Test fallback choice generation."""
        empty_context = {"session_id": self.test_session_id}
        choices = self.branching_system.generate_choice_options(empty_context)

        self.assertGreater(len(choices), 0, "Should generate fallback choices")

        # Should include basic choices
        choice_ids = [choice.choice_id for choice in choices]
        basic_choices = ["continue", "reflect", "look_around"]
        has_basic = any(basic_id in choice_ids for basic_id in basic_choices)
        self.assertTrue(has_basic, "Should include basic fallback choices")

    def test_process_user_choice_therapeutic(self):
        """Test processing a therapeutic choice."""
        choice = ChoiceOption(
            choice_id="breathing_exercise",
            choice_text="Take a moment to focus on your breathing",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_weight=0.8,
            emotional_tone="calming",
            consequences=["reduced_anxiety", "increased_mindfulness"]
        )

        consequence = self.branching_system.process_user_choice(choice, self.test_context)

        self.assertIsInstance(consequence, ChoiceConsequence)
        self.assertEqual(consequence.choice_id, choice.choice_id)
        self.assertEqual(consequence.consequence_type, ConsequenceType.THERAPEUTIC)
        self.assertEqual(consequence.impact_level, ImpactLevel.MODERATE)
        self.assertEqual(consequence.therapeutic_impact, 0.8)
        self.assertIn("reduced_anxiety", consequence.narrative_flags)
        self.assertIn("increased_mindfulness", consequence.narrative_flags)

    def test_process_user_choice_dialogue(self):
        """Test processing a dialogue choice."""
        choice = ChoiceOption(
            choice_id="talk_to_therapist",
            choice_text="Talk to the therapist",
            choice_type=ChoiceType.DIALOGUE,
            therapeutic_weight=0.4,
            consequences=["social_connection"]
        )

        consequence = self.branching_system.process_user_choice(choice, self.test_context)

        self.assertEqual(consequence.consequence_type, ConsequenceType.RELATIONSHIP)
        self.assertEqual(consequence.impact_level, ImpactLevel.MINOR)
        self.assertIn("therapist", consequence.affected_entities)
        self.assertIn("companion", consequence.affected_entities)

    def test_process_user_choice_movement(self):
        """Test processing a movement choice."""
        choice = ChoiceOption(
            choice_id="move_forward",
            choice_text="Continue moving forward",
            choice_type=ChoiceType.MOVEMENT,
            therapeutic_weight=0.2
        )

        consequence = self.branching_system.process_user_choice(choice, self.test_context)

        self.assertEqual(consequence.consequence_type, ConsequenceType.WORLD_STATE)
        self.assertTrue(consequence.world_state_changes.get("player_moved"))
        self.assertIn("player_location", consequence.affected_entities)

    def test_story_impact_tracking(self):
        """Test story impact tracking across multiple choices."""
        # Make several choices
        choices = [
            ChoiceOption("choice1", "Therapeutic choice 1", ChoiceType.THERAPEUTIC, 0.6),
            ChoiceOption("choice2", "Dialogue choice", ChoiceType.DIALOGUE, 0.3),
            ChoiceOption("choice3", "Therapeutic choice 2", ChoiceType.THERAPEUTIC, 0.8)
        ]

        for choice in choices:
            self.branching_system.process_user_choice(choice, self.test_context)

        # Check story impact
        impact = self.branching_system.calculate_story_impact(self.test_session_id)
        self.assertIsNotNone(impact)
        self.assertEqual(impact.session_id, self.test_session_id)
        self.assertAlmostEqual(impact.cumulative_therapeutic_score, 1.7, places=1)
        self.assertEqual(len(impact.emotional_journey), 3)

    def test_create_narrative_branch_therapeutic_focus(self):
        """Test creating a narrative branch with therapeutic focus."""
        # Create choice history with therapeutic focus
        choice_history = [
            ChoiceConsequence(
                choice_id="therapeutic1",
                consequence_type=ConsequenceType.THERAPEUTIC,
                therapeutic_impact=0.7
            ),
            ChoiceConsequence(
                choice_id="therapeutic2",
                consequence_type=ConsequenceType.THERAPEUTIC,
                therapeutic_impact=0.6
            ),
            ChoiceConsequence(
                choice_id="dialogue1",
                consequence_type=ConsequenceType.RELATIONSHIP,
                therapeutic_impact=0.3
            )
        ]

        branching_point = BranchingPoint(
            narrative_position=5,
            location_id="therapy_room",
            available_branches=["intensive_therapy"]
        )

        branch = self.branching_system.create_narrative_branch(branching_point, choice_history)

        self.assertIsNotNone(branch)
        self.assertEqual(branch.therapeutic_theme, "intensive_therapy")
        self.assertIn("deep_emotional_processing", branch.therapeutic_opportunities)
        self.assertIn("coping_skill_development", branch.therapeutic_opportunities)
        self.assertEqual(len(branch.required_choices), 3)  # Last 3 choices

    def test_create_narrative_branch_social_focus(self):
        """Test creating a narrative branch with social focus."""
        # Create choice history with social focus
        choice_history = [
            ChoiceConsequence(
                choice_id="social1",
                consequence_type=ConsequenceType.RELATIONSHIP,
                therapeutic_impact=0.4
            ),
            ChoiceConsequence(
                choice_id="social2",
                consequence_type=ConsequenceType.RELATIONSHIP,
                therapeutic_impact=0.5
            ),
            ChoiceConsequence(
                choice_id="therapeutic1",
                consequence_type=ConsequenceType.THERAPEUTIC,
                therapeutic_impact=0.3
            )
        ]

        branching_point = BranchingPoint(
            narrative_position=3,
            location_id="social_area"
        )

        branch = self.branching_system.create_narrative_branch(branching_point, choice_history)

        self.assertIsNotNone(branch)
        self.assertEqual(branch.therapeutic_theme, "social_connection")
        self.assertIn("relationship_building", branch.therapeutic_opportunities)
        self.assertIn("communication_skills", branch.therapeutic_opportunities)

    def test_get_available_branches(self):
        """Test getting available narrative branches."""
        # Create some branches
        choice_history = [
            ChoiceConsequence(choice_id="req_choice1"),
            ChoiceConsequence(choice_id="req_choice2")
        ]

        # Store choice history
        self.branching_system.choice_history[self.test_session_id] = choice_history

        # Create a branch with requirements
        branch = NarrativeBranch(
            branch_name="Test Branch",
            description="Test branch",
            required_choices=["req_choice1", "req_choice2"]
        )
        self.branching_system.narrative_branches[branch.branch_id] = branch

        # Get available branches
        available = self.branching_system.get_available_branches(self.test_session_id, self.test_context)

        self.assertEqual(len(available), 1)
        self.assertEqual(available[0].branch_id, branch.branch_id)

    def test_get_available_branches_requirements_not_met(self):
        """Test getting available branches when requirements are not met."""
        # Create choice history that doesn't meet requirements
        choice_history = [
            ChoiceConsequence(choice_id="other_choice1"),
            ChoiceConsequence(choice_id="other_choice2")
        ]

        self.branching_system.choice_history[self.test_session_id] = choice_history

        # Create a branch with different requirements
        branch = NarrativeBranch(
            branch_name="Test Branch",
            description="Test branch",
            required_choices=["req_choice1", "req_choice2"]
        )
        self.branching_system.narrative_branches[branch.branch_id] = branch

        # Get available branches
        available = self.branching_system.get_available_branches(self.test_session_id, self.test_context)

        self.assertEqual(len(available), 0)

    def test_get_choice_history(self):
        """Test getting choice history for a session."""
        # Add some choices
        choices = [
            ChoiceOption("choice1", "First choice", ChoiceType.DIALOGUE),
            ChoiceOption("choice2", "Second choice", ChoiceType.THERAPEUTIC)
        ]

        for choice in choices:
            self.branching_system.process_user_choice(choice, self.test_context)

        history = self.branching_system.get_choice_history(self.test_session_id)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].choice_id, "choice1")
        self.assertEqual(history[1].choice_id, "choice2")

    def test_clear_session_data(self):
        """Test clearing session data."""
        # Add some data
        choice = ChoiceOption("test_choice", "Test choice", ChoiceType.DIALOGUE)
        self.branching_system.process_user_choice(choice, self.test_context)

        # Verify data exists
        self.assertIn(self.test_session_id, self.branching_system.choice_history)
        self.assertIn(self.test_session_id, self.branching_system.story_impacts)

        # Clear data
        success = self.branching_system.clear_session_data(self.test_session_id)

        self.assertTrue(success)
        self.assertNotIn(self.test_session_id, self.branching_system.choice_history)
        self.assertNotIn(self.test_session_id, self.branching_system.story_impacts)

    def test_emotional_impact_processing(self):
        """Test emotional impact processing for different choice tones."""
        # Test calming choice
        calming_choice = ChoiceOption(
            choice_id="calm_choice",
            choice_text="Take deep breaths",
            choice_type=ChoiceType.THERAPEUTIC,
            emotional_tone="calming"
        )

        consequence = self.branching_system.process_user_choice(calming_choice, self.test_context)

        self.assertIn("anxiety", consequence.emotional_impact)
        self.assertIn("peace", consequence.emotional_impact)
        self.assertLess(consequence.emotional_impact["anxiety"], 0)  # Should reduce anxiety
        self.assertGreater(consequence.emotional_impact["peace"], 0)  # Should increase peace

        # Test hopeful choice
        hopeful_choice = ChoiceOption(
            choice_id="hope_choice",
            choice_text="Think positively",
            choice_type=ChoiceType.THERAPEUTIC,
            emotional_tone="hopeful"
        )

        consequence = self.branching_system.process_user_choice(hopeful_choice, self.test_context)

        self.assertIn("depression", consequence.emotional_impact)
        self.assertIn("optimism", consequence.emotional_impact)
        self.assertLess(consequence.emotional_impact["depression"], 0)  # Should reduce depression
        self.assertGreater(consequence.emotional_impact["optimism"], 0)  # Should increase optimism


class TestChoiceOption(unittest.TestCase):
    """Test cases for ChoiceOption dataclass."""

    def test_choice_option_creation(self):
        """Test ChoiceOption creation and validation."""
        choice = ChoiceOption(
            choice_id="test_choice",
            choice_text="Test choice text",
            choice_type=ChoiceType.THERAPEUTIC,
            therapeutic_weight=0.7,
            emotional_tone="positive"
        )

        self.assertTrue(choice.validate())
        self.assertEqual(choice.choice_id, "test_choice")
        self.assertEqual(choice.choice_text, "Test choice text")
        self.assertEqual(choice.choice_type, ChoiceType.THERAPEUTIC)
        self.assertEqual(choice.therapeutic_weight, 0.7)
        self.assertEqual(choice.emotional_tone, "positive")

    def test_choice_option_validation_errors(self):
        """Test ChoiceOption validation errors."""
        # Empty choice ID
        with self.assertRaises(ValueError):
            choice = ChoiceOption(choice_id="", choice_text="Test")
            choice.validate()

        # Empty choice text
        with self.assertRaises(ValueError):
            choice = ChoiceOption(choice_id="test", choice_text="")
            choice.validate()

        # Invalid therapeutic weight
        with self.assertRaises(ValueError):
            choice = ChoiceOption(choice_id="test", choice_text="Test", therapeutic_weight=2.0)
            choice.validate()


class TestChoiceConsequence(unittest.TestCase):
    """Test cases for ChoiceConsequence dataclass."""

    def test_choice_consequence_creation(self):
        """Test ChoiceConsequence creation and validation."""
        consequence = ChoiceConsequence(
            choice_id="test_choice",
            description="Test consequence",
            consequence_type=ConsequenceType.THERAPEUTIC,
            impact_level=ImpactLevel.MODERATE,
            therapeutic_impact=0.5
        )

        self.assertTrue(consequence.validate())
        self.assertEqual(consequence.choice_id, "test_choice")
        self.assertEqual(consequence.description, "Test consequence")
        self.assertEqual(consequence.consequence_type, ConsequenceType.THERAPEUTIC)
        self.assertEqual(consequence.impact_level, ImpactLevel.MODERATE)
        self.assertEqual(consequence.therapeutic_impact, 0.5)

    def test_choice_consequence_validation_errors(self):
        """Test ChoiceConsequence validation errors."""
        # Empty description
        with self.assertRaises(ValueError):
            consequence = ChoiceConsequence(description="")
            consequence.validate()

        # Invalid therapeutic impact
        with self.assertRaises(ValueError):
            consequence = ChoiceConsequence(description="Test", therapeutic_impact=2.0)
            consequence.validate()


class TestStoryImpact(unittest.TestCase):
    """Test cases for StoryImpact dataclass."""

    def test_story_impact_creation(self):
        """Test StoryImpact creation and validation."""
        impact = StoryImpact(
            session_id="test_session",
            cumulative_therapeutic_score=1.5,
            major_decisions=["decision1", "decision2"]
        )

        self.assertTrue(impact.validate())
        self.assertEqual(impact.session_id, "test_session")
        self.assertEqual(impact.cumulative_therapeutic_score, 1.5)
        self.assertEqual(len(impact.major_decisions), 2)

    def test_story_impact_validation_error(self):
        """Test StoryImpact validation error."""
        with self.assertRaises(ValueError):
            impact = StoryImpact(session_id="")
            impact.validate()


if __name__ == '__main__':
    unittest.main()
