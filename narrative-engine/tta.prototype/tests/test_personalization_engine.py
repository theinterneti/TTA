"""
Integration Tests for Personalization Engine and Content Adaptation

This module contains comprehensive integration tests for the personalization engine,
content adaptation system, recommendation system, and adaptive narrative generation.
These tests verify the integration between different personalization components.

Test Classes:
    TestPersonalizationContext: Tests for personalization context data model
    TestContentAdaptation: Tests for content adaptation data model
    TestUserProfileAnalyzer: Tests for user profile analysis
    TestContentAdaptationSystem: Tests for content adaptation functionality
    TestRecommendationSystem: Tests for recommendation generation
    TestAdaptiveNarrativeGenerator: Tests for adaptive narrative generation
    TestPersonalizationEngine: Tests for main personalization engine integration
"""

import logging
import sys
import unittest
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent.parent / "core"
models_path = Path(__file__).parent.parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    from data_models import (
        CopingStrategy,
        EmotionalState,
        EmotionalStateType,
        InterventionType,
        SessionState,
        TherapeuticGoal,
        TherapeuticProgress,
        ValidationError,
    )
    from personalization_engine import (
        AdaptiveNarrativeGenerator,
        ContentAdaptation,
        ContentAdaptationSystem,
        ContentAdaptationType,
        PersonalizationContext,
        PersonalizationEngine,
        PersonalizedRecommendation,
        RecommendationSystem,
        RecommendationType,
        UserProfileAnalyzer,
        create_sample_personalization_context,
    )
    from progress_tracking_personalization import (
        PersonalizationDimension,
        PersonalizationProfile,
        ProgressAnalysisResult,
        ProgressMetric,
        ProgressMetricType,
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for testing
    class MockPersonalizationEngine:
        pass

    PersonalizationEngine = MockPersonalizationEngine

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)


class TestPersonalizationContext(unittest.TestCase):
    """Test cases for PersonalizationContext data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.session_state = SessionState(
            session_id="test_session",
            user_id="test_user"
        )
        self.profile = PersonalizationProfile(
            user_id="test_user",
            learning_velocity=0.6
        )
        self.valid_context = PersonalizationContext(
            user_id="test_user",
            session_state=self.session_state,
            personalization_profile=self.profile
        )

    def test_valid_personalization_context_creation(self):
        """Test creating a valid personalization context."""
        self.assertTrue(self.valid_context.validate())
        self.assertEqual(self.valid_context.user_id, "test_user")
        self.assertEqual(self.valid_context.session_state, self.session_state)
        self.assertEqual(self.valid_context.personalization_profile, self.profile)

    def test_personalization_context_user_id_validation(self):
        """Test user ID validation."""
        with self.assertRaises(ValidationError):
            invalid_context = PersonalizationContext(
                user_id="",
                session_state=self.session_state,
                personalization_profile=self.profile
            )
            invalid_context.validate()

    def test_personalization_context_required_fields(self):
        """Test required fields validation."""
        with self.assertRaises(ValidationError):
            invalid_context = PersonalizationContext(
                user_id="test_user",
                session_state=None,
                personalization_profile=self.profile
            )
            invalid_context.validate()

        with self.assertRaises(ValidationError):
            invalid_context = PersonalizationContext(
                user_id="test_user",
                session_state=self.session_state,
                personalization_profile=None
            )
            invalid_context.validate()


class TestContentAdaptation(unittest.TestCase):
    """Test cases for ContentAdaptation data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_adaptation = ContentAdaptation(
            adaptation_type=ContentAdaptationType.DIFFICULTY_ADJUSTMENT,
            adaptation_rationale="Adjusted for user learning style",
            confidence_score=0.8
        )

    def test_valid_content_adaptation_creation(self):
        """Test creating a valid content adaptation."""
        self.assertTrue(self.valid_adaptation.validate())
        self.assertEqual(self.valid_adaptation.adaptation_type, ContentAdaptationType.DIFFICULTY_ADJUSTMENT)
        self.assertEqual(self.valid_adaptation.confidence_score, 0.8)

    def test_content_adaptation_rationale_validation(self):
        """Test adaptation rationale validation."""
        with self.assertRaises(ValidationError):
            invalid_adaptation = ContentAdaptation(adaptation_rationale="")
            invalid_adaptation.validate()

        with self.assertRaises(ValidationError):
            invalid_adaptation = ContentAdaptation(adaptation_rationale="   ")
            invalid_adaptation.validate()

    def test_content_adaptation_confidence_validation(self):
        """Test confidence score validation."""
        with self.assertRaises(ValidationError):
            invalid_adaptation = ContentAdaptation(
                adaptation_rationale="Test",
                confidence_score=-0.1
            )
            invalid_adaptation.validate()

        with self.assertRaises(ValidationError):
            invalid_adaptation = ContentAdaptation(
                adaptation_rationale="Test",
                confidence_score=1.1
            )
            invalid_adaptation.validate()


class TestPersonalizedRecommendation(unittest.TestCase):
    """Test cases for PersonalizedRecommendation data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_recommendation = PersonalizedRecommendation(
            recommendation_type=RecommendationType.NEXT_INTERVENTION,
            title="Try Mindfulness",
            description="Practice mindfulness meditation",
            priority_score=0.8,
            confidence_level=0.9,
            estimated_duration=15
        )

    def test_valid_recommendation_creation(self):
        """Test creating a valid recommendation."""
        self.assertTrue(self.valid_recommendation.validate())
        self.assertEqual(self.valid_recommendation.title, "Try Mindfulness")
        self.assertEqual(self.valid_recommendation.priority_score, 0.8)

    def test_recommendation_required_fields(self):
        """Test required fields validation."""
        with self.assertRaises(ValidationError):
            invalid_rec = PersonalizedRecommendation(title="", description="Test")
            invalid_rec.validate()

        with self.assertRaises(ValidationError):
            invalid_rec = PersonalizedRecommendation(title="Test", description="")
            invalid_rec.validate()

    def test_recommendation_score_validation(self):
        """Test score validation."""
        with self.assertRaises(ValidationError):
            invalid_rec = PersonalizedRecommendation(
                title="Test", description="Test", priority_score=-0.1
            )
            invalid_rec.validate()

        with self.assertRaises(ValidationError):
            invalid_rec = PersonalizedRecommendation(
                title="Test", description="Test", confidence_level=1.1
            )
            invalid_rec.validate()

    def test_recommendation_duration_validation(self):
        """Test estimated duration validation."""
        with self.assertRaises(ValidationError):
            invalid_rec = PersonalizedRecommendation(
                title="Test", description="Test", estimated_duration=0
            )
            invalid_rec.validate()


class TestUserProfileAnalyzer(unittest.TestCase):
    """Test cases for UserProfileAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = UserProfileAnalyzer()
        self.sample_profile = PersonalizationProfile(
            user_id="test_user",
            learning_velocity=0.6,
            optimal_session_length=25,
            preferred_intervention_types=[InterventionType.MINDFULNESS]
        )
        self.sample_progress = ProgressAnalysisResult(
            user_id="test_user",
            overall_progress_score=0.7
        )

    def test_analyze_user_characteristics(self):
        """Test analyzing user characteristics."""
        characteristics = self.analyzer.analyze_user_characteristics(
            self.sample_profile, self.sample_progress
        )

        self.assertIn("learning_style", characteristics)
        self.assertIn("engagement_preferences", characteristics)
        self.assertIn("therapeutic_readiness", characteristics)
        self.assertIn("content_preferences", characteristics)
        self.assertIn("interaction_style", characteristics)
        self.assertIn("pacing_preferences", characteristics)
        self.assertIn("support_needs", characteristics)
        self.assertIn("motivation_factors", characteristics)

        # Check that all characteristics contain valid data
        for _key, value in characteristics.items():
            self.assertIsInstance(value, dict)
            self.assertGreater(len(value), 0)

    def test_determine_learning_style_slow_learner(self):
        """Test learning style determination for slow learners."""
        slow_profile = PersonalizationProfile(
            user_id="test_user",
            learning_velocity=0.2  # Slow learner
        )

        learning_style = self.analyzer._determine_learning_style(slow_profile)

        self.assertGreater(learning_style.get("step_by_step", 0), 0.8)
        self.assertGreater(learning_style.get("visual", 0), 0.7)
        self.assertGreater(learning_style.get("self_paced", 0), 0.7)

    def test_determine_learning_style_fast_learner(self):
        """Test learning style determination for fast learners."""
        fast_profile = PersonalizationProfile(
            user_id="test_user",
            learning_velocity=0.8  # Fast learner
        )

        learning_style = self.analyzer._determine_learning_style(fast_profile)

        self.assertGreater(learning_style.get("challenge_seeking", 0), 0.7)
        self.assertGreater(learning_style.get("exploratory", 0), 0.8)
        self.assertGreater(learning_style.get("fast_paced", 0), 0.7)

    def test_assess_therapeutic_readiness(self):
        """Test therapeutic readiness assessment."""
        readiness = self.analyzer._assess_therapeutic_readiness(
            self.sample_profile, self.sample_progress
        )

        # Check that all readiness scores are within valid range
        for _key, value in readiness.items():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

        # High progress should increase readiness for advanced techniques
        self.assertGreater(readiness.get("advanced_techniques", 0), 0.5)

    def test_determine_content_preferences_with_mindfulness(self):
        """Test content preferences with mindfulness preference."""
        preferences = self.analyzer._determine_content_preferences(self.sample_profile)

        # Should prefer reflective and emotional content due to mindfulness preference
        self.assertGreater(preferences.get("reflective", 0), 0.8)
        self.assertGreater(preferences.get("emotional", 0), 0.7)


class TestContentAdaptationSystem(unittest.TestCase):
    """Test cases for ContentAdaptationSystem."""

    def setUp(self):
        """Set up test fixtures."""
        self.adaptation_system = ContentAdaptationSystem()
        self.sample_context = create_sample_personalization_context("test_user")
        self.sample_content = {
            "title": "Managing Stress",
            "description": "Learn effective stress management techniques",
            "difficulty": "medium",
            "instructions": "Follow these steps to reduce stress levels."
        }

    def test_adapt_content_basic_functionality(self):
        """Test basic content adaptation functionality."""
        adaptation = self.adaptation_system.adapt_content(
            self.sample_content, self.sample_context
        )

        self.assertIsInstance(adaptation, ContentAdaptation)
        self.assertTrue(adaptation.validate())
        self.assertIsInstance(adaptation.adapted_content, dict)
        self.assertGreater(len(adaptation.adaptation_rationale), 0)
        self.assertGreaterEqual(adaptation.confidence_score, 0.0)
        self.assertLessEqual(adaptation.confidence_score, 1.0)

    def test_assess_adaptation_needs(self):
        """Test adaptation needs assessment."""
        profile_analyzer = UserProfileAnalyzer()
        user_characteristics = profile_analyzer.analyze_user_characteristics(
            self.sample_context.personalization_profile
        )

        needs = self.adaptation_system._assess_adaptation_needs(
            self.sample_content, user_characteristics, self.sample_context
        )

        self.assertIsInstance(needs, dict)
        self.assertGreater(len(needs), 0)

        # All need scores should be within valid range
        for adaptation_type, score in needs.items():
            self.assertIsInstance(adaptation_type, ContentAdaptationType)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_select_primary_adaptation(self):
        """Test primary adaptation selection."""
        needs = {
            ContentAdaptationType.DIFFICULTY_ADJUSTMENT: 0.8,
            ContentAdaptationType.PACING_MODIFICATION: 0.3,
            ContentAdaptationType.STYLE_ADAPTATION: 0.5
        }

        primary = self.adaptation_system._select_primary_adaptation(needs)
        self.assertEqual(primary, ContentAdaptationType.DIFFICULTY_ADJUSTMENT)

    def test_adjust_difficulty_simplification(self):
        """Test difficulty adjustment for simplification."""
        # Create context that needs simplification
        simple_profile = PersonalizationProfile(
            user_id="test_user",
            learning_velocity=0.2  # Slow learner needs simplification
        )
        simple_context = PersonalizationContext(
            user_id="test_user",
            session_state=self.sample_context.session_state,
            personalization_profile=simple_profile
        )

        profile_analyzer = UserProfileAnalyzer()
        user_characteristics = profile_analyzer.analyze_user_characteristics(simple_profile)

        adapted = self.adaptation_system._adjust_difficulty(
            self.sample_content, user_characteristics, simple_context
        )

        self.assertIn("complexity_level", adapted)
        self.assertEqual(adapted["complexity_level"], "basic")

    def test_modify_pacing_slow_paced(self):
        """Test pacing modification for slow-paced users."""
        # Create characteristics for slow-paced user
        user_characteristics = {
            "pacing_preferences": {
                "slow_paced": 0.8,
                "user_controlled": 0.7
            }
        }

        adapted = self.adaptation_system._modify_pacing(
            self.sample_content, user_characteristics, self.sample_context
        )

        self.assertEqual(adapted.get("pacing"), "slow")
        self.assertEqual(adapted.get("review_frequency"), "high")
        self.assertTrue(adapted.get("user_pacing_control", False))


class TestRecommendationSystem(unittest.TestCase):
    """Test cases for RecommendationSystem."""

    def setUp(self):
        """Set up test fixtures."""
        self.recommendation_system = RecommendationSystem()
        self.sample_context = create_sample_personalization_context("test_user")

    def test_generate_recommendations_basic_functionality(self):
        """Test basic recommendation generation functionality."""
        recommendations = self.recommendation_system.generate_recommendations(
            self.sample_context, max_recommendations=3
        )

        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)

        # Validate all recommendations
        for rec in recommendations:
            self.assertIsInstance(rec, PersonalizedRecommendation)
            self.assertTrue(rec.validate())
            self.assertGreater(len(rec.title), 0)
            self.assertGreater(len(rec.description), 0)

    def test_generate_intervention_recommendations(self):
        """Test intervention recommendation generation."""
        profile_analyzer = UserProfileAnalyzer()
        user_characteristics = profile_analyzer.analyze_user_characteristics(
            self.sample_context.personalization_profile
        )

        recommendations = self.recommendation_system._generate_intervention_recommendations(
            self.sample_context, user_characteristics
        )

        self.assertIsInstance(recommendations, list)

        # Check that recommendations are intervention type
        for rec in recommendations:
            self.assertEqual(rec.recommendation_type, RecommendationType.NEXT_INTERVENTION)
            self.assertGreater(len(rec.implementation_steps), 0)

    def test_generate_content_focus_recommendations(self):
        """Test content focus recommendation generation."""
        # Create characteristics that prefer narrative content
        user_characteristics = {
            "content_preferences": {
                "narrative_heavy": 0.8
            }
        }

        recommendations = self.recommendation_system._generate_content_focus_recommendations(
            self.sample_context, user_characteristics
        )

        self.assertIsInstance(recommendations, list)

        # Should generate narrative-focused recommendations
        if recommendations:
            self.assertEqual(recommendations[0].recommendation_type, RecommendationType.CONTENT_FOCUS)
            self.assertIn("narrative", recommendations[0].title.lower() or recommendations[0].description.lower())

    def test_generate_session_structure_recommendations(self):
        """Test session structure recommendation generation."""
        # Create characteristics for user needing shorter sessions
        user_characteristics = {
            "engagement_preferences": {
                "sustained_focus": 0.3  # Low sustained focus
            }
        }

        recommendations = self.recommendation_system._generate_session_structure_recommendations(
            self.sample_context, user_characteristics
        )

        self.assertIsInstance(recommendations, list)

        # Should recommend shorter sessions
        if recommendations:
            self.assertEqual(recommendations[0].recommendation_type, RecommendationType.SESSION_STRUCTURE)
            self.assertIn("shorter", recommendations[0].title.lower() or recommendations[0].description.lower())


class TestAdaptiveNarrativeGenerator(unittest.TestCase):
    """Test cases for AdaptiveNarrativeGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.narrative_generator = AdaptiveNarrativeGenerator()
        self.sample_context = create_sample_personalization_context("test_user")
        self.sample_narrative_request = {
            "scene": "therapeutic_session",
            "characters": ["therapist", "user"],
            "theme": "anxiety_management",
            "content": "A conversation about managing anxiety"
        }

    def test_generate_personalized_narrative_basic_functionality(self):
        """Test basic narrative generation functionality."""
        personalized_narrative = self.narrative_generator.generate_personalized_narrative(
            self.sample_context, self.sample_narrative_request
        )

        self.assertIsInstance(personalized_narrative, dict)
        self.assertIn("tone", personalized_narrative)
        self.assertIn("themes", personalized_narrative)
        self.assertIn("pacing", personalized_narrative)
        self.assertIn("personalization_applied", personalized_narrative)

    def test_select_narrative_approach_supportive(self):
        """Test narrative approach selection for supportive users."""
        # Create characteristics needing support
        user_characteristics = {
            "support_needs": {
                "frequent_encouragement": 0.8
            },
            "interaction_style": {
                "challenging": 0.2
            }
        }

        approach = self.narrative_generator._select_narrative_approach(user_characteristics)
        self.assertEqual(approach, "supportive")

    def test_select_narrative_approach_challenging(self):
        """Test narrative approach selection for challenging users."""
        # Create characteristics preferring challenge
        user_characteristics = {
            "support_needs": {
                "frequent_encouragement": 0.3
            },
            "interaction_style": {
                "challenging": 0.7
            }
        }

        approach = self.narrative_generator._select_narrative_approach(user_characteristics)
        self.assertEqual(approach, "challenging")

    def test_create_narrative_content(self):
        """Test narrative content creation."""
        approach = "supportive"
        user_characteristics = {}

        narrative_content = self.narrative_generator._create_narrative_content(
            self.sample_narrative_request, approach, user_characteristics, self.sample_context
        )

        self.assertIsInstance(narrative_content, dict)
        self.assertEqual(narrative_content["tone"], "warm and encouraging")
        self.assertIn("growth", narrative_content["themes"])
        self.assertEqual(narrative_content["pacing"], "gentle")


class TestPersonalizationEngine(unittest.TestCase):
    """Test cases for main PersonalizationEngine integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.personalization_engine = PersonalizationEngine()
        self.test_user_id = "test_user_123"
        self.sample_context = create_sample_personalization_context(self.test_user_id)
        self.sample_content = {
            "title": "Stress Management",
            "description": "Learn to manage stress effectively",
            "difficulty": "medium",
            "duration": 20
        }

    def test_personalize_content_integration(self):
        """Test complete content personalization integration."""
        result = self.personalization_engine.personalize_content(
            self.test_user_id,
            self.sample_content,
            self.sample_context.session_state,
            self.sample_context.personalization_profile,
            self.sample_context.progress_analysis
        )

        self.assertIn("adapted_content", result)
        self.assertIn("adaptation_info", result)
        self.assertIn("recommendations", result)
        self.assertIn("personalization_metadata", result)

        # Check adaptation info
        adaptation_info = result["adaptation_info"]
        self.assertIn("type", adaptation_info)
        self.assertIn("rationale", adaptation_info)
        self.assertIn("confidence", adaptation_info)

        # Check recommendations
        recommendations = result["recommendations"]
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)

        for rec in recommendations:
            self.assertIn("type", rec)
            self.assertIn("title", rec)
            self.assertIn("description", rec)
            self.assertIn("priority", rec)

    def test_generate_adaptive_narrative_integration(self):
        """Test adaptive narrative generation integration."""
        narrative_request = {
            "scene": "therapy_session",
            "theme": "resilience_building",
            "content": "Building resilience through challenges"
        }

        result = self.personalization_engine.generate_adaptive_narrative(
            self.test_user_id,
            narrative_request,
            self.sample_context.session_state,
            self.sample_context.personalization_profile,
            self.sample_context.progress_analysis
        )

        self.assertIsInstance(result, dict)
        self.assertIn("personalization_applied", result)

        # Check that personalization was applied
        personalization_info = result["personalization_applied"]
        self.assertEqual(personalization_info["user_id"], self.test_user_id)
        self.assertIn("approach", personalization_info)

    def test_get_personalization_insights_no_data(self):
        """Test getting personalization insights with no data."""
        insights = self.personalization_engine.get_personalization_insights("nonexistent_user")

        self.assertIn("message", insights)
        self.assertEqual(insights["message"], "No personalization data available")

    def test_get_personalization_insights_with_data(self):
        """Test getting personalization insights with existing data."""
        # First generate some personalization data
        self.personalization_engine.personalize_content(
            self.test_user_id,
            self.sample_content,
            self.sample_context.session_state,
            self.sample_context.personalization_profile,
            self.sample_context.progress_analysis
        )

        # Then get insights
        insights = self.personalization_engine.get_personalization_insights(self.test_user_id)

        self.assertIn("total_adaptations", insights)
        self.assertIn("total_recommendations", insights)
        self.assertIn("personalization_effectiveness", insights)
        self.assertIn("recent_adaptations", insights)

        # Should have at least one adaptation
        self.assertGreater(insights["total_adaptations"], 0)

        # Effectiveness should be within valid range
        self.assertGreaterEqual(insights["personalization_effectiveness"], 0.0)
        self.assertLessEqual(insights["personalization_effectiveness"], 1.0)

    def test_personalization_history_tracking(self):
        """Test that personalization history is properly tracked."""
        # Generate multiple personalizations
        for i in range(3):
            content = {
                "title": f"Content {i}",
                "description": f"Description {i}",
                "difficulty": "medium"
            }

            self.personalization_engine.personalize_content(
                self.test_user_id,
                content,
                self.sample_context.session_state,
                self.sample_context.personalization_profile
            )

        # Check that history was tracked
        adaptations = self.personalization_engine.adaptation_history[self.test_user_id]
        recommendations = self.personalization_engine.recommendation_history[self.test_user_id]

        self.assertEqual(len(adaptations), 3)
        self.assertGreater(len(recommendations), 0)  # Should have some recommendations

        # Check that all adaptations are valid
        for adaptation in adaptations:
            self.assertIsInstance(adaptation, ContentAdaptation)
            self.assertTrue(adaptation.validate())


class TestSampleDataGeneration(unittest.TestCase):
    """Test cases for sample data generation utilities."""

    def test_create_sample_personalization_context(self):
        """Test creating sample personalization context."""
        user_id = "test_user"
        context = create_sample_personalization_context(user_id)

        self.assertIsInstance(context, PersonalizationContext)
        self.assertTrue(context.validate())
        self.assertEqual(context.user_id, user_id)
        self.assertIsInstance(context.session_state, SessionState)
        self.assertIsInstance(context.personalization_profile, PersonalizationProfile)
        self.assertIsInstance(context.progress_analysis, ProgressAnalysisResult)


if __name__ == "__main__":
    # Configure test logging
    logging.basicConfig(level=logging.WARNING)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_classes = [
        TestPersonalizationContext,
        TestContentAdaptation,
        TestPersonalizedRecommendation,
        TestUserProfileAnalyzer,
        TestContentAdaptationSystem,
        TestRecommendationSystem,
        TestAdaptiveNarrativeGenerator,
        TestPersonalizationEngine,
        TestSampleDataGeneration
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
