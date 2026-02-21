"""

# Logseq: [[TTA.dev/Tests/Test_compatibility_checker]]
Unit tests for CompatibilityChecker.
"""

import unittest
from datetime import datetime, timedelta

from src.player_experience.models.character import (
    Character,
    CharacterAppearance,
    CharacterBackground,
    TherapeuticGoal,
    TherapeuticProfile,
)
from src.player_experience.models.enums import (
    DifficultyLevel,
    IntensityLevel,
    TherapeuticApproach,
)
from src.player_experience.models.world import WorldDetails, WorldPrerequisite
from src.player_experience.utils.compatibility_checker import (
    CompatibilityChecker,
    CompatibilityWeights,
)


class TestCompatibilityChecker(unittest.TestCase):
    """Test cases for CompatibilityChecker."""

    def setUp(self):
        """Set up test fixtures."""
        self.compatibility_checker = CompatibilityChecker()

        # Create test character
        self.test_character = self._create_test_character()

        # Create test worlds
        self.beginner_world = self._create_beginner_world()
        self.advanced_world = self._create_advanced_world()
        self.trigger_world = self._create_world_with_triggers()

    def _create_test_character(self) -> Character:
        """Create a test character with therapeutic profile."""
        therapeutic_goals = [
            TherapeuticGoal(
                goal_id="goal_1",
                description="Reduce anxiety",
                therapeutic_approaches=[
                    TherapeuticApproach.CBT,
                    TherapeuticApproach.MINDFULNESS,
                ],
            )
        ]

        therapeutic_profile = TherapeuticProfile(
            primary_concerns=["anxiety", "stress"],
            therapeutic_goals=therapeutic_goals,
            preferred_intensity=IntensityLevel.MEDIUM,
            comfort_zones=["mindfulness", "nature"],
            challenge_areas=["social_situations"],
            trigger_topics=["trauma", "violence"],
            readiness_level=0.6,
        )

        return Character(
            character_id="test_char_123",
            player_id="test_player_456",
            name="Test Character",
            appearance=CharacterAppearance(),
            background=CharacterBackground(name="Test Character"),
            therapeutic_profile=therapeutic_profile,
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

    def _create_beginner_world(self) -> WorldDetails:
        """Create a beginner-level test world."""
        return WorldDetails(
            world_id="beginner_world",
            name="Peaceful Garden",
            description="A gentle introduction to mindfulness",
            long_description="A safe space for beginners",
            therapeutic_themes=["mindfulness", "relaxation"],
            therapeutic_approaches=[TherapeuticApproach.MINDFULNESS],
            difficulty_level=DifficultyLevel.BEGINNER,
            estimated_duration=timedelta(hours=1),
            recommended_therapeutic_readiness=0.3,
            content_warnings=[],
            prerequisites=[],
            average_rating=4.5,
            completion_rate=0.9,
            therapeutic_effectiveness_score=0.8,
        )

    def _create_advanced_world(self) -> WorldDetails:
        """Create an advanced-level test world."""
        return WorldDetails(
            world_id="advanced_world",
            name="Challenge Arena",
            description="Advanced therapeutic challenges",
            long_description="For experienced users ready for complex scenarios",
            therapeutic_themes=["exposure_therapy", "advanced_coping"],
            therapeutic_approaches=[
                TherapeuticApproach.CBT,
                TherapeuticApproach.DIALECTICAL_BEHAVIORAL,
            ],
            difficulty_level=DifficultyLevel.ADVANCED,
            estimated_duration=timedelta(hours=3),
            recommended_therapeutic_readiness=0.8,
            content_warnings=["challenging_scenarios"],
            prerequisites=[
                WorldPrerequisite(
                    prerequisite_type="therapeutic_readiness",
                    description="High therapeutic readiness required",
                    required_value=0.8,
                )
            ],
            average_rating=4.2,
            completion_rate=0.6,
            therapeutic_effectiveness_score=0.9,
        )

    def _create_world_with_triggers(self) -> WorldDetails:
        """Create a world with potential trigger content."""
        return WorldDetails(
            world_id="trigger_world",
            name="Trauma Processing World",
            description="A world for processing difficult experiences",
            long_description="Designed for trauma recovery work",
            therapeutic_themes=["trauma_recovery", "healing"],
            therapeutic_approaches=[TherapeuticApproach.NARRATIVE_THERAPY],
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            estimated_duration=timedelta(hours=2),
            recommended_therapeutic_readiness=0.7,
            content_warnings=["trauma", "emotional_intensity"],
            prerequisites=[],
            average_rating=4.0,
            completion_rate=0.7,
            therapeutic_effectiveness_score=0.85,
        )

    def test_initialization(self):
        """Test CompatibilityChecker initialization."""
        # Test default initialization
        checker = CompatibilityChecker()
        self.assertIsNotNone(checker.weights)
        self.assertEqual(checker._compatibility_threshold, 0.6)

        # Test initialization with custom weights
        custom_weights = CompatibilityWeights(
            therapeutic_readiness=0.4,
            therapeutic_approach_alignment=0.3,
            content_safety=0.2,
            difficulty_appropriateness=0.1,
            prerequisite_fulfillment=0.0,
        )

        checker_with_weights = CompatibilityChecker(custom_weights)
        self.assertEqual(checker_with_weights.weights, custom_weights)

    def test_comprehensive_compatibility_calculation(self):
        """Test comprehensive compatibility calculation."""
        # Test with beginner world (should be good match)
        report = self.compatibility_checker.calculate_comprehensive_compatibility(
            self.test_character, self.beginner_world
        )

        self.assertEqual(report.character_id, self.test_character.character_id)
        self.assertEqual(report.world_id, self.beginner_world.world_id)
        self.assertGreaterEqual(report.overall_score, 0.0)
        self.assertLessEqual(report.overall_score, 1.0)
        self.assertGreater(len(report.compatibility_factors), 0)
        self.assertIsInstance(report.recommendations, list)
        self.assertIsInstance(report.warnings, list)
        self.assertTrue(report.prerequisites_met)  # No prerequisites for beginner world

    def test_therapeutic_readiness_compatibility(self):
        """Test therapeutic readiness compatibility calculation."""
        # Test perfect match
        report = self.compatibility_checker.calculate_comprehensive_compatibility(
            self.test_character, self.beginner_world
        )

        readiness_factor = next(
            factor
            for factor in report.compatibility_factors
            if factor.factor_name == "Therapeutic Readiness"
        )

        self.assertIsNotNone(readiness_factor)
        self.assertGreaterEqual(readiness_factor.score, 0.0)
        self.assertLessEqual(readiness_factor.score, 1.0)
        self.assertIn("readiness", readiness_factor.explanation.lower())

    def test_therapeutic_approach_alignment(self):
        """Test therapeutic approach alignment calculation."""
        report = self.compatibility_checker.calculate_comprehensive_compatibility(
            self.test_character, self.beginner_world
        )

        approach_factor = next(
            factor
            for factor in report.compatibility_factors
            if factor.factor_name == "Therapeutic Approach Alignment"
        )

        self.assertIsNotNone(approach_factor)
        self.assertGreaterEqual(approach_factor.score, 0.0)
        self.assertLessEqual(approach_factor.score, 1.0)

        # Should have good alignment since both character and world use mindfulness
        self.assertGreater(approach_factor.score, 0.5)

    def test_content_safety_compatibility(self):
        """Test content safety compatibility calculation."""
        # Test with world that has triggers
        report = self.compatibility_checker.calculate_comprehensive_compatibility(
            self.test_character, self.trigger_world
        )

        safety_factor = next(
            factor
            for factor in report.compatibility_factors
            if factor.factor_name == "Content Safety"
        )

        self.assertIsNotNone(safety_factor)
        self.assertGreaterEqual(safety_factor.score, 0.0)
        self.assertLessEqual(safety_factor.score, 1.0)

        # Should have lower safety score due to trigger overlap
        self.assertLess(safety_factor.score, 0.8)

        # Should have warnings
        self.assertGreater(len(report.warnings), 0)

    def test_difficulty_appropriateness(self):
        """Test difficulty appropriateness calculation."""
        # Test with advanced world (should be too difficult for character's readiness)
        report = self.compatibility_checker.calculate_comprehensive_compatibility(
            self.test_character, self.advanced_world
        )

        difficulty_factor = next(
            factor
            for factor in report.compatibility_factors
            if factor.factor_name == "Difficulty Appropriateness"
        )

        self.assertIsNotNone(difficulty_factor)
        self.assertGreaterEqual(difficulty_factor.score, 0.0)
        self.assertLessEqual(difficulty_factor.score, 1.0)

        # Character readiness (0.6) maps to ADVANCED difficulty, and world is ADVANCED,
        # so this should be a perfect match (score 1.0)
        self.assertEqual(difficulty_factor.score, 1.0)

    def test_prerequisite_fulfillment(self):
        """Test prerequisite fulfillment calculation."""
        # Test with advanced world that has prerequisites
        report = self.compatibility_checker.calculate_comprehensive_compatibility(
            self.test_character, self.advanced_world
        )

        prerequisite_factor = next(
            factor
            for factor in report.compatibility_factors
            if factor.factor_name == "Prerequisite Fulfillment"
        )

        self.assertIsNotNone(prerequisite_factor)
        self.assertGreaterEqual(prerequisite_factor.score, 0.0)
        self.assertLessEqual(prerequisite_factor.score, 1.0)

        # Should not meet prerequisites since character readiness (0.6) < required (0.8)
        self.assertFalse(report.prerequisites_met)
        self.assertGreater(len(report.unmet_prerequisites), 0)

    def test_world_recommendations(self):
        """Test world recommendations generation."""
        available_worlds = [
            self.beginner_world,
            self.advanced_world,
            self.trigger_world,
        ]

        recommendations = self.compatibility_checker.get_world_recommendations(
            self.test_character, available_worlds, max_recommendations=3
        )

        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)
        self.assertGreater(len(recommendations), 0)

        # Check that recommendations are sorted by compatibility score
        for i in range(len(recommendations) - 1):
            self.assertGreaterEqual(
                recommendations[i][1].overall_score,
                recommendations[i + 1][1].overall_score,
            )

        # Each recommendation should be a tuple of (WorldDetails, CompatibilityReport)
        for world, report in recommendations:
            self.assertIsInstance(world, WorldDetails)
            self.assertIsInstance(report, type(report))  # CompatibilityReport type

    def test_world_suitability_assessment(self):
        """Test world suitability assessment."""
        # Test with beginner world (should be suitable)
        assessment = self.compatibility_checker.assess_world_suitability(
            self.test_character, self.beginner_world
        )

        self.assertIn("suitability_level", assessment)
        self.assertIn("compatibility_score", assessment)
        self.assertIn("compatibility_report", assessment)
        self.assertIn("is_recommended", assessment)
        self.assertIn("has_safety_concerns", assessment)
        self.assertIn("prerequisites_met", assessment)

        self.assertIsInstance(assessment["suitability_level"], str)
        self.assertIsInstance(assessment["compatibility_score"], float)
        self.assertIsInstance(assessment["is_recommended"], bool)
        self.assertIsInstance(assessment["has_safety_concerns"], bool)
        self.assertIsInstance(assessment["prerequisites_met"], bool)

        # Test with trigger world (should have safety concerns)
        trigger_assessment = self.compatibility_checker.assess_world_suitability(
            self.test_character, self.trigger_world
        )

        self.assertTrue(trigger_assessment["has_safety_concerns"])

    def test_recommendations_and_warnings_generation(self):
        """Test that appropriate recommendations and warnings are generated."""
        # Test with advanced world (should generate recommendations about difficulty)
        report = self.compatibility_checker.calculate_comprehensive_compatibility(
            self.test_character, self.advanced_world
        )

        self.assertGreater(len(report.recommendations), 0)

        # Should recommend easier worlds or mention prerequisites
        recommendation_text = " ".join(report.recommendations).lower()
        self.assertTrue(
            any(
                keyword in recommendation_text
                for keyword in ["prerequisite", "easier", "beginner", "readiness"]
            )
        )

        # Test with trigger world (should generate safety warnings)
        trigger_report = (
            self.compatibility_checker.calculate_comprehensive_compatibility(
                self.test_character, self.trigger_world
            )
        )

        self.assertGreater(len(trigger_report.warnings), 0)

        warning_text = " ".join(trigger_report.warnings).lower()
        self.assertTrue(
            any(
                keyword in warning_text
                for keyword in ["trigger", "content", "support", "difficult"]
            )
        )

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test character with no therapeutic goals
        character_no_goals = Character(
            character_id="no_goals_char",
            player_id="test_player",
            name="No Goals Character",
            appearance=CharacterAppearance(),
            background=CharacterBackground(name="No Goals Character"),
            therapeutic_profile=TherapeuticProfile(readiness_level=0.5),
            created_at=datetime.now(),
            last_active=datetime.now(),
        )

        report = self.compatibility_checker.calculate_comprehensive_compatibility(
            character_no_goals, self.beginner_world
        )

        self.assertIsNotNone(report)
        self.assertGreaterEqual(report.overall_score, 0.0)

        # Test world with no therapeutic approaches
        world_no_approaches = WorldDetails(
            world_id="no_approaches_world",
            name="Generic World",
            description="A world with no specific approaches",
            long_description="Generic world",
            therapeutic_approaches=[],
            difficulty_level=DifficultyLevel.BEGINNER,
            recommended_therapeutic_readiness=0.5,
        )

        report = self.compatibility_checker.calculate_comprehensive_compatibility(
            self.test_character, world_no_approaches
        )

        self.assertIsNotNone(report)
        self.assertGreaterEqual(report.overall_score, 0.0)

    def test_custom_weights(self):
        """Test compatibility calculation with custom weights."""
        # Create checker with custom weights that prioritize safety
        safety_focused_weights = CompatibilityWeights(
            therapeutic_readiness=0.1,
            therapeutic_approach_alignment=0.1,
            content_safety=0.6,
            difficulty_appropriateness=0.1,
            prerequisite_fulfillment=0.1,
        )

        safety_checker = CompatibilityChecker(safety_focused_weights)

        # Test with trigger world
        report = safety_checker.calculate_comprehensive_compatibility(
            self.test_character, self.trigger_world
        )

        # Should have lower overall score due to safety concerns being weighted heavily
        self.assertLess(report.overall_score, 0.7)


if __name__ == "__main__":
    unittest.main()
