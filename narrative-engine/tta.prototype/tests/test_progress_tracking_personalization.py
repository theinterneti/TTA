"""
Unit Tests for Progress Tracking and Personalization System

This module contains comprehensive unit tests for the progress tracking and personalization
system, including therapeutic progress analysis, emotional growth tracking, goal achievement
monitoring, and personalization engine functionality.

Test Classes:
    TestProgressMetric: Tests for progress metric data model
    TestPersonalizationProfile: Tests for personalization profile data model
    TestTherapeuticProgressAnalyzer: Tests for progress analysis functionality
    TestEmotionalGrowthTracker: Tests for emotional growth tracking
    TestGoalAchievementMonitor: Tests for goal achievement monitoring
    TestProgressTrackingPersonalization: Tests for main progress tracking system
"""

import logging
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
    from data_models import (
        CharacterState,
        CompletedIntervention,
        CopingStrategy,
        EmotionalState,
        EmotionalStateType,
        InterventionType,
        NarrativeContext,
        SessionState,
        TherapeuticGoal,
        TherapeuticGoalStatus,
        TherapeuticProgress,
        ValidationError,
    )
    from progress_tracking_personalization import (
        EmotionalGrowthTracker,
        GoalAchievementMonitor,
        PersonalizationDimension,
        PersonalizationProfile,
        ProgressAnalysisResult,
        ProgressMetric,
        ProgressMetricType,
        ProgressTrackingPersonalization,
        TherapeuticProgressAnalyzer,
        create_sample_progress_data,
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for testing
    class MockProgressTrackingPersonalization:
        pass

    ProgressTrackingPersonalization = MockProgressTrackingPersonalization

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)


class TestProgressMetric(unittest.TestCase):
    """Test cases for ProgressMetric data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_metric = ProgressMetric(
            metric_type=ProgressMetricType.EMOTIONAL_REGULATION,
            value=0.7,
            measurement_context="Test measurement"
        )

    def test_valid_progress_metric_creation(self):
        """Test creating a valid progress metric."""
        self.assertTrue(self.valid_metric.validate())
        self.assertEqual(self.valid_metric.metric_type, ProgressMetricType.EMOTIONAL_REGULATION)
        self.assertEqual(self.valid_metric.value, 0.7)
        self.assertIsInstance(self.valid_metric.timestamp, datetime)

    def test_progress_metric_value_validation(self):
        """Test progress metric value validation."""
        # Test invalid values
        with self.assertRaises(ValidationError):
            invalid_metric = ProgressMetric(value=-0.1)
            invalid_metric.validate()

        with self.assertRaises(ValidationError):
            invalid_metric = ProgressMetric(value=1.1)
            invalid_metric.validate()

        # Test boundary values
        boundary_metric_low = ProgressMetric(value=0.0)
        self.assertTrue(boundary_metric_low.validate())

        boundary_metric_high = ProgressMetric(value=1.0)
        self.assertTrue(boundary_metric_high.validate())

    def test_progress_metric_confidence_validation(self):
        """Test progress metric confidence level validation."""
        with self.assertRaises(ValidationError):
            invalid_metric = ProgressMetric(confidence_level=-0.1)
            invalid_metric.validate()

        with self.assertRaises(ValidationError):
            invalid_metric = ProgressMetric(confidence_level=1.1)
            invalid_metric.validate()


class TestPersonalizationProfile(unittest.TestCase):
    """Test cases for PersonalizationProfile data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_profile = PersonalizationProfile(
            user_id="test_user_123",
            learning_velocity=0.6,
            optimal_session_length=25
        )

    def test_valid_personalization_profile_creation(self):
        """Test creating a valid personalization profile."""
        self.assertTrue(self.valid_profile.validate())
        self.assertEqual(self.valid_profile.user_id, "test_user_123")
        self.assertEqual(self.valid_profile.learning_velocity, 0.6)
        self.assertEqual(self.valid_profile.optimal_session_length, 25)

    def test_personalization_profile_user_id_validation(self):
        """Test user ID validation."""
        with self.assertRaises(ValidationError):
            invalid_profile = PersonalizationProfile(user_id="")
            invalid_profile.validate()

        with self.assertRaises(ValidationError):
            invalid_profile = PersonalizationProfile(user_id="   ")
            invalid_profile.validate()

    def test_personalization_profile_learning_velocity_validation(self):
        """Test learning velocity validation."""
        with self.assertRaises(ValidationError):
            invalid_profile = PersonalizationProfile(user_id="test", learning_velocity=-0.1)
            invalid_profile.validate()

        with self.assertRaises(ValidationError):
            invalid_profile = PersonalizationProfile(user_id="test", learning_velocity=1.1)
            invalid_profile.validate()

    def test_personalization_profile_session_length_validation(self):
        """Test optimal session length validation."""
        with self.assertRaises(ValidationError):
            invalid_profile = PersonalizationProfile(user_id="test", optimal_session_length=0)
            invalid_profile.validate()

        with self.assertRaises(ValidationError):
            invalid_profile = PersonalizationProfile(user_id="test", optimal_session_length=-5)
            invalid_profile.validate()


class TestTherapeuticProgressAnalyzer(unittest.TestCase):
    """Test cases for TherapeuticProgressAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = TherapeuticProgressAnalyzer()
        self.sample_metrics = self._create_sample_metrics()

    def _create_sample_metrics(self) -> list[ProgressMetric]:
        """Create sample metrics for testing."""
        metrics = []
        base_time = datetime.now() - timedelta(days=10)

        for i in range(10):
            metrics.append(ProgressMetric(
                metric_type=ProgressMetricType.EMOTIONAL_REGULATION,
                value=0.3 + (i * 0.05),  # Improving trend
                timestamp=base_time + timedelta(days=i)
            ))

        return metrics

    def test_analyze_progress_metrics_empty_list(self):
        """Test analyzing empty metrics list."""
        result = self.analyzer.analyze_progress_metrics([])
        self.assertEqual(result, {})

    def test_analyze_progress_metrics_insufficient_data(self):
        """Test analyzing metrics with insufficient data points."""
        single_metric = [self.sample_metrics[0]]
        result = self.analyzer.analyze_progress_metrics(single_metric)
        self.assertEqual(result, {})  # Should return empty due to minimum data points requirement

    def test_analyze_progress_metrics_valid_data(self):
        """Test analyzing valid metrics data."""
        result = self.analyzer.analyze_progress_metrics(self.sample_metrics)

        self.assertIn(ProgressMetricType.EMOTIONAL_REGULATION, result)
        analysis = result[ProgressMetricType.EMOTIONAL_REGULATION]

        self.assertIn("current_value", analysis)
        self.assertIn("average_value", analysis)
        self.assertIn("trend_slope", analysis)
        self.assertIn("improvement_rate", analysis)

        # Check that trend slope is positive (improving trend)
        self.assertGreater(analysis["trend_slope"], 0)

        # Check that improvement rate is positive
        self.assertGreater(analysis["improvement_rate"], 0)

    def test_calculate_overall_progress_score_empty_analysis(self):
        """Test calculating overall progress score with empty analysis."""
        score = self.analyzer.calculate_overall_progress_score({})
        self.assertEqual(score, 0.0)

    def test_calculate_overall_progress_score_valid_analysis(self):
        """Test calculating overall progress score with valid analysis."""
        analysis = self.analyzer.analyze_progress_metrics(self.sample_metrics)
        score = self.analyzer.calculate_overall_progress_score(analysis)

        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        self.assertGreater(score, 0.5)  # Should be above 0.5 due to improving trend

    def test_identify_achievement_highlights(self):
        """Test identifying achievement highlights."""
        # Create metrics with high performance
        high_performance_metrics = []
        base_time = datetime.now() - timedelta(days=5)

        for i in range(5):
            high_performance_metrics.append(ProgressMetric(
                metric_type=ProgressMetricType.GOAL_ACHIEVEMENT,
                value=0.85 + (i * 0.02),  # High performance with improvement
                timestamp=base_time + timedelta(days=i)
            ))

        analysis = self.analyzer.analyze_progress_metrics(high_performance_metrics)
        highlights = self.analyzer.identify_achievement_highlights(analysis)

        self.assertIsInstance(highlights, list)
        self.assertGreater(len(highlights), 0)
        self.assertTrue(any("goal achievement" in highlight.lower() for highlight in highlights))

    def test_identify_improvement_areas(self):
        """Test identifying areas for improvement."""
        # Create metrics with low performance
        low_performance_metrics = []
        base_time = datetime.now() - timedelta(days=5)

        for i in range(5):
            low_performance_metrics.append(ProgressMetric(
                metric_type=ProgressMetricType.COPING_SKILLS_USAGE,
                value=0.3 - (i * 0.02),  # Low performance with decline
                timestamp=base_time + timedelta(days=i)
            ))

        analysis = self.analyzer.analyze_progress_metrics(low_performance_metrics)
        improvements = self.analyzer.identify_improvement_areas(analysis)

        self.assertIsInstance(improvements, list)
        self.assertGreater(len(improvements), 0)
        self.assertTrue(any("coping skills usage" in improvement.lower() for improvement in improvements))


class TestEmotionalGrowthTracker(unittest.TestCase):
    """Test cases for EmotionalGrowthTracker."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracker = EmotionalGrowthTracker()
        self.sample_emotional_states = self._create_sample_emotional_states()

    def _create_sample_emotional_states(self) -> list[EmotionalState]:
        """Create sample emotional states for testing."""
        states = []
        base_time = datetime.now() - timedelta(days=10)

        emotions = [EmotionalStateType.ANXIOUS, EmotionalStateType.CALM,
                   EmotionalStateType.HOPEFUL, EmotionalStateType.DEPRESSED]

        for i in range(10):
            states.append(EmotionalState(
                primary_emotion=emotions[i % len(emotions)],
                intensity=0.8 - (i * 0.05),  # Decreasing intensity over time
                timestamp=base_time + timedelta(days=i),
                confidence_level=0.7 + (i * 0.02)  # Increasing confidence
            ))

        return states

    def test_track_emotional_patterns_empty_list(self):
        """Test tracking emotional patterns with empty list."""
        result = self.tracker.track_emotional_patterns([])
        self.assertEqual(result, {})

    def test_track_emotional_patterns_valid_data(self):
        """Test tracking emotional patterns with valid data."""
        result = self.tracker.track_emotional_patterns(self.sample_emotional_states)

        self.assertIn("dominant_emotions", result)
        self.assertIn("emotional_diversity", result)
        self.assertIn("average_intensity", result)
        self.assertIn("emotional_stability_score", result)
        self.assertIn("positive_emotion_ratio", result)
        self.assertIn("emotional_regulation_trend", result)
        self.assertIn("growth_indicators", result)

        # Check that emotional diversity is reasonable
        self.assertGreater(result["emotional_diversity"], 0)
        self.assertLessEqual(result["emotional_diversity"], 4)  # We have 4 different emotions

        # Check that average intensity is within valid range
        self.assertGreaterEqual(result["average_intensity"], 0.0)
        self.assertLessEqual(result["average_intensity"], 1.0)

    def test_calculate_positive_emotion_ratio(self):
        """Test calculating positive emotion ratio."""
        # Create states with known positive/negative distribution
        positive_states = [
            EmotionalState(primary_emotion=EmotionalStateType.CALM),
            EmotionalState(primary_emotion=EmotionalStateType.HOPEFUL),
            EmotionalState(primary_emotion=EmotionalStateType.ANXIOUS),
            EmotionalState(primary_emotion=EmotionalStateType.DEPRESSED)
        ]

        ratio = self.tracker._calculate_positive_emotion_ratio(positive_states)
        self.assertEqual(ratio, 0.5)  # 2 positive out of 4 total

    def test_identify_growth_indicators(self):
        """Test identifying emotional growth indicators."""
        # Create states showing improvement over time
        improving_states = []
        base_time = datetime.now() - timedelta(days=10)

        for i in range(10):
            improving_states.append(EmotionalState(
                primary_emotion=EmotionalStateType.ANXIOUS if i < 5 else EmotionalStateType.CALM,
                intensity=0.8 - (i * 0.05),
                confidence_level=0.5 + (i * 0.05),  # Increasing confidence
                coping_resources=["breathing"] * (i + 1),  # Increasing coping resources
                timestamp=base_time + timedelta(days=i)
            ))

        indicators = self.tracker._identify_growth_indicators(improving_states)
        self.assertIsInstance(indicators, list)
        # Should identify increased awareness and coping resource utilization
        self.assertTrue(any("awareness" in indicator.lower() for indicator in indicators))


class TestGoalAchievementMonitor(unittest.TestCase):
    """Test cases for GoalAchievementMonitor."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitor = GoalAchievementMonitor()
        self.sample_goals = self._create_sample_goals()

    def _create_sample_goals(self) -> list[TherapeuticGoal]:
        """Create sample therapeutic goals for testing."""
        goals = []

        # Active goal with good progress
        goals.append(TherapeuticGoal(
            title="Manage Anxiety",
            description="Learn to manage anxiety symptoms",
            progress_percentage=75.0,
            status=TherapeuticGoalStatus.ACTIVE,
            target_behaviors=["deep breathing", "mindfulness"]
        ))

        # Completed goal
        goals.append(TherapeuticGoal(
            title="Sleep Hygiene",
            description="Establish good sleep habits",
            progress_percentage=100.0,
            status=TherapeuticGoalStatus.COMPLETED,
            target_behaviors=["regular bedtime"]
        ))

        # Stagnant goal
        goals.append(TherapeuticGoal(
            title="Social Skills",
            description="Improve social interactions",
            progress_percentage=15.0,
            status=TherapeuticGoalStatus.ACTIVE,
            target_behaviors=["eye contact", "active listening", "conversation starters"],
            created_at=datetime.now() - timedelta(days=30)
        ))

        return goals

    def test_monitor_goal_progress_empty_list(self):
        """Test monitoring goal progress with empty list."""
        result = self.monitor.monitor_goal_progress([])
        self.assertEqual(result, {})

    def test_monitor_goal_progress_valid_data(self):
        """Test monitoring goal progress with valid data."""
        result = self.monitor.monitor_goal_progress(self.sample_goals)

        self.assertIn("total_goals", result)
        self.assertIn("active_goals", result)
        self.assertIn("completed_goals", result)
        self.assertIn("completion_rate", result)
        self.assertIn("average_active_progress", result)
        self.assertIn("near_completion_count", result)
        self.assertIn("stagnant_goals_count", result)
        self.assertIn("achievement_momentum", result)

        # Check calculated values
        self.assertEqual(result["total_goals"], 3)
        self.assertEqual(result["active_goals"], 2)
        self.assertEqual(result["completed_goals"], 1)
        self.assertAlmostEqual(result["completion_rate"], 1/3, places=2)

        # Should identify one near-completion goal (75% progress)
        self.assertEqual(result["near_completion_count"], 1)

        # Should identify one stagnant goal
        self.assertEqual(result["stagnant_goals_count"], 1)

    def test_calculate_achievement_momentum(self):
        """Test calculating achievement momentum."""
        momentum = self.monitor._calculate_achievement_momentum(self.sample_goals)

        self.assertGreaterEqual(momentum, 0.0)
        self.assertLessEqual(momentum, 1.0)
        # Should have some momentum due to completed goal and near-completion goal
        self.assertGreater(momentum, 0.0)

    def test_analyze_goal_difficulty(self):
        """Test analyzing goal difficulty distribution."""
        difficulty = self.monitor._analyze_goal_difficulty(self.sample_goals)

        self.assertIn("easy", difficulty)
        self.assertIn("medium", difficulty)
        self.assertIn("hard", difficulty)

        # Check that counts add up to total goals
        total_difficulty_count = sum(difficulty.values())
        self.assertEqual(total_difficulty_count, len(self.sample_goals))

    def test_generate_goal_recommendations(self):
        """Test generating goal recommendations."""
        active_goals = [g for g in self.sample_goals if g.status == TherapeuticGoalStatus.ACTIVE]
        near_completion = [g for g in active_goals if g.progress_percentage >= 70]
        stagnant = [g for g in active_goals if self.monitor._is_goal_stagnant(g)]

        recommendations = self.monitor._generate_goal_recommendations(active_goals, stagnant, near_completion)

        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

        # Should recommend focusing on near-completion goals
        self.assertTrue(any("near completion" in rec.lower() for rec in recommendations))

        # Should recommend reviewing stagnant goals
        self.assertTrue(any("stagnant" in rec.lower() for rec in recommendations))


class TestProgressTrackingPersonalization(unittest.TestCase):
    """Test cases for main ProgressTrackingPersonalization system."""

    def setUp(self):
        """Set up test fixtures."""
        self.progress_system = ProgressTrackingPersonalization()
        self.test_user_id = "test_user_123"
        self.sample_session = self._create_sample_session()

    def _create_sample_session(self) -> SessionState:
        """Create a sample session state for testing."""
        # Create therapeutic progress
        therapeutic_progress = TherapeuticProgress(user_id=self.test_user_id)

        # Add a goal
        goal = therapeutic_progress.add_goal(
            title="Manage Stress",
            description="Learn stress management techniques",
            target_behaviors=["deep breathing", "progressive relaxation"]
        )
        goal.progress_percentage = 60.0

        # Add completed intervention
        therapeutic_progress.complete_intervention(
            intervention_type=InterventionType.MINDFULNESS,
            description="Mindfulness meditation session",
            effectiveness_rating=8.0,
            user_feedback="Very helpful"
        )

        # Add coping strategy
        strategy = CopingStrategy(
            name="Deep Breathing",
            description="4-7-8 breathing technique",
            effectiveness_score=7.5,
            usage_count=5
        )
        therapeutic_progress.coping_strategies_learned.append(strategy)

        # Create emotional state
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.CALM,
            intensity=0.6,
            confidence_level=0.8
        )

        # Create session state
        session = SessionState(
            session_id="test_session_123",
            user_id=self.test_user_id,
            therapeutic_progress=therapeutic_progress,
            emotional_state=emotional_state,
            narrative_position=5
        )

        return session

    def test_track_therapeutic_progress_valid_session(self):
        """Test tracking therapeutic progress with valid session data."""
        result = self.progress_system.track_therapeutic_progress(self.test_user_id, self.sample_session)

        self.assertIn("metrics_recorded", result)
        self.assertIn("overall_progress_score", result)
        self.assertIn("analysis_confidence", result)
        self.assertIn("next_focus", result)

        # Should record multiple metrics
        self.assertGreater(result["metrics_recorded"], 0)

        # Should have reasonable progress score
        self.assertGreaterEqual(result["overall_progress_score"], 0.0)
        self.assertLessEqual(result["overall_progress_score"], 1.0)

    def test_extract_progress_metrics(self):
        """Test extracting progress metrics from session data."""
        metrics = self.progress_system._extract_progress_metrics(self.test_user_id, self.sample_session)

        self.assertIsInstance(metrics, list)
        self.assertGreater(len(metrics), 0)

        # Should extract different types of metrics
        metric_types = {metric.metric_type for metric in metrics}
        self.assertIn(ProgressMetricType.GOAL_ACHIEVEMENT, metric_types)
        self.assertIn(ProgressMetricType.INTERVENTION_EFFECTIVENESS, metric_types)
        self.assertIn(ProgressMetricType.COPING_SKILLS_USAGE, metric_types)
        self.assertIn(ProgressMetricType.EMOTIONAL_REGULATION, metric_types)
        self.assertIn(ProgressMetricType.ENGAGEMENT_LEVEL, metric_types)

        # All metrics should be valid
        for metric in metrics:
            self.assertTrue(metric.validate())

    def test_analyze_user_progress_no_data(self):
        """Test analyzing user progress with no data."""
        result = self.progress_system._analyze_user_progress("nonexistent_user")

        self.assertEqual(result.user_id, "nonexistent_user")
        self.assertEqual(result.overall_progress_score, 0.0)
        self.assertEqual(result.confidence_level, 0.0)
        self.assertIn("Begin therapeutic journey", result.next_therapeutic_focus)

    def test_analyze_user_progress_with_data(self):
        """Test analyzing user progress with existing data."""
        # First track some progress
        self.progress_system.track_therapeutic_progress(self.test_user_id, self.sample_session)

        # Then analyze
        result = self.progress_system._analyze_user_progress(self.test_user_id)

        self.assertEqual(result.user_id, self.test_user_id)
        self.assertGreater(result.overall_progress_score, 0.0)
        self.assertGreater(result.confidence_level, 0.0)
        self.assertIsInstance(result.metric_trends, dict)
        self.assertIsInstance(result.achievement_highlights, list)
        self.assertIsInstance(result.areas_for_improvement, list)
        self.assertIsInstance(result.recommended_interventions, list)

    def test_determine_next_therapeutic_focus(self):
        """Test determining next therapeutic focus."""
        # Create mock metric analysis with low emotional regulation
        metric_analysis = {
            ProgressMetricType.EMOTIONAL_REGULATION: {"current_value": 0.3},
            ProgressMetricType.GOAL_ACHIEVEMENT: {"current_value": 0.7}
        }

        focus = self.progress_system._determine_next_therapeutic_focus(metric_analysis, [])
        self.assertIn("Emotional regulation", focus)

    def test_recommend_interventions(self):
        """Test recommending therapeutic interventions."""
        # Create mock metric analysis with low-performing metrics
        metric_analysis = {
            ProgressMetricType.EMOTIONAL_REGULATION: {
                "current_value": 0.3,
                "trend_slope": -0.01
            },
            ProgressMetricType.COPING_SKILLS_USAGE: {
                "current_value": 0.4,
                "trend_slope": 0.001
            }
        }

        interventions = self.progress_system._recommend_interventions(metric_analysis, [])

        self.assertIsInstance(interventions, list)
        self.assertLessEqual(len(interventions), 3)  # Should limit to 3
        self.assertIn(InterventionType.MINDFULNESS, interventions)  # For emotional regulation

    def test_analyze_user_patterns(self):
        """Test analyzing user patterns."""
        # Track some progress first
        self.progress_system.track_therapeutic_progress(self.test_user_id, self.sample_session)

        patterns = self.progress_system.analyze_user_patterns(self.test_user_id)

        self.assertIn("progress_trends", patterns)
        self.assertIn("temporal_patterns", patterns)
        self.assertIn("intervention_patterns", patterns)
        self.assertIn("engagement_patterns", patterns)
        self.assertIn("personalization_insights", patterns)

    def test_recommend_next_steps(self):
        """Test recommending next therapeutic steps."""
        # Track some progress first
        self.progress_system.track_therapeutic_progress(self.test_user_id, self.sample_session)

        recommendations = self.progress_system.recommend_next_steps(self.test_user_id)

        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

        # Each recommendation should have required fields
        for rec in recommendations:
            self.assertIn("type", rec)
            self.assertIn("priority", rec)
            self.assertIn("title", rec)
            self.assertIn("description", rec)
            self.assertIn("estimated_duration", rec)
            self.assertIn("expected_impact", rec)

    def test_update_personalization_profile(self):
        """Test updating personalization profile."""
        # Create analysis result
        analysis_result = ProgressAnalysisResult(
            user_id=self.test_user_id,
            overall_progress_score=0.7,
            metric_trends={
                ProgressMetricType.ENGAGEMENT_LEVEL: {
                    "current_value": 0.8,
                    "improvement_rate": 0.2
                }
            }
        )

        # Update profile
        self.progress_system._update_personalization_profile(
            self.test_user_id, self.sample_session, analysis_result
        )

        # Check that profile was created and updated
        self.assertIn(self.test_user_id, self.progress_system.personalization_profiles)
        profile = self.progress_system.personalization_profiles[self.test_user_id]

        self.assertEqual(profile.user_id, self.test_user_id)
        self.assertGreater(profile.learning_velocity, 0.5)  # Should be above baseline due to improvement
        self.assertIn("engagement", profile.engagement_patterns)


class TestSampleDataGeneration(unittest.TestCase):
    """Test cases for sample data generation utilities."""

    def test_create_sample_progress_data(self):
        """Test creating sample progress data."""
        user_id = "test_user"
        days = 30

        metrics = create_sample_progress_data(user_id, days)

        self.assertIsInstance(metrics, list)
        self.assertGreater(len(metrics), 0)

        # Check that metrics span the requested time period
        timestamps = [m.timestamp for m in metrics]
        time_span = max(timestamps) - min(timestamps)
        self.assertGreaterEqual(time_span.days, days - 1)

        # Check that all metrics are valid
        for metric in metrics:
            self.assertTrue(metric.validate())
            self.assertGreaterEqual(metric.value, 0.0)
            self.assertLessEqual(metric.value, 1.0)

        # Check that different metric types are represented
        metric_types = {m.metric_type for m in metrics}
        self.assertGreater(len(metric_types), 1)


if __name__ == "__main__":
    # Configure test logging
    logging.basicConfig(level=logging.WARNING)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_classes = [
        TestProgressMetric,
        TestPersonalizationProfile,
        TestTherapeuticProgressAnalyzer,
        TestEmotionalGrowthTracker,
        TestGoalAchievementMonitor,
        TestProgressTrackingPersonalization,
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
