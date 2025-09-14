"""
Integration Tests for Progress-Based Therapeutic Adaptation System

This module contains comprehensive integration tests for the progress-based therapeutic
adaptation system, including adaptive therapy orchestration, therapeutic journey planning,
intervention selection, and content difficulty adaptation.

Test Classes:
    TestAdaptationDecision: Tests for adaptation decision data model
    TestTherapeuticJourneyPlan: Tests for journey plan data model
    TestProgressBasedInterventionSelector: Tests for intervention selection
    TestContentDifficultyAdapter: Tests for content difficulty adaptation
    TestTherapeuticJourneyPlanner: Tests for journey planning
    TestAdaptiveTherapyOrchestrator: Tests for therapy orchestration
    TestProgressBasedTherapeuticAdaptation: Tests for main integration system
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
        CompletedIntervention,
        InterventionType,
        SessionState,
        TherapeuticGoal,
        TherapeuticGoalStatus,
        TherapeuticProgress,
        ValidationError,
    )
    from progress_based_therapeutic_adaptation import (
        AdaptationDecision,
        AdaptationStrategy,
        AdaptiveTherapyOrchestrator,
        ContentDifficultyAdapter,
        ProgressBasedInterventionSelector,
        ProgressBasedTherapeuticAdaptation,
        TherapeuticJourneyPlan,
        TherapeuticJourneyPlanner,
        TherapeuticPhase,
        create_sample_adaptation_context,
    )
    from progress_tracking_personalization import (
        PersonalizationProfile,
        ProgressAnalysisResult,
        ProgressMetric,
        ProgressMetricType,
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for testing
    class MockProgressBasedTherapeuticAdaptation:
        pass

    ProgressBasedTherapeuticAdaptation = MockProgressBasedTherapeuticAdaptation

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)


class TestAdaptationDecision(unittest.TestCase):
    """Test cases for AdaptationDecision data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_decision = AdaptationDecision(
            user_id="test_user",
            adaptation_strategy=AdaptationStrategy.ACCELERATE,
            rationale="High progress indicates readiness for acceleration",
            confidence_level=0.8
        )

    def test_valid_adaptation_decision_creation(self):
        """Test creating a valid adaptation decision."""
        self.assertTrue(self.valid_decision.validate())
        self.assertEqual(self.valid_decision.user_id, "test_user")
        self.assertEqual(self.valid_decision.adaptation_strategy, AdaptationStrategy.ACCELERATE)
        self.assertEqual(self.valid_decision.confidence_level, 0.8)

    def test_adaptation_decision_user_id_validation(self):
        """Test user ID validation."""
        with self.assertRaises(ValidationError):
            invalid_decision = AdaptationDecision(
                user_id="",
                rationale="Test rationale"
            )
            invalid_decision.validate()

    def test_adaptation_decision_rationale_validation(self):
        """Test rationale validation."""
        with self.assertRaises(ValidationError):
            invalid_decision = AdaptationDecision(
                user_id="test_user",
                rationale=""
            )
            invalid_decision.validate()

    def test_adaptation_decision_confidence_validation(self):
        """Test confidence level validation."""
        with self.assertRaises(ValidationError):
            invalid_decision = AdaptationDecision(
                user_id="test_user",
                rationale="Test rationale",
                confidence_level=-0.1
            )
            invalid_decision.validate()

        with self.assertRaises(ValidationError):
            invalid_decision = AdaptationDecision(
                user_id="test_user",
                rationale="Test rationale",
                confidence_level=1.1
            )
            invalid_decision.validate()


class TestTherapeuticJourneyPlan(unittest.TestCase):
    """Test cases for TherapeuticJourneyPlan data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_plan = TherapeuticJourneyPlan(
            user_id="test_user",
            current_phase=TherapeuticPhase.FOUNDATION_BUILDING,
            estimated_duration=12
        )

    def test_valid_journey_plan_creation(self):
        """Test creating a valid journey plan."""
        self.assertTrue(self.valid_plan.validate())
        self.assertEqual(self.valid_plan.user_id, "test_user")
        self.assertEqual(self.valid_plan.current_phase, TherapeuticPhase.FOUNDATION_BUILDING)
        self.assertEqual(self.valid_plan.estimated_duration, 12)

    def test_journey_plan_user_id_validation(self):
        """Test user ID validation."""
        with self.assertRaises(ValidationError):
            invalid_plan = TherapeuticJourneyPlan(user_id="", estimated_duration=12)
            invalid_plan.validate()

    def test_journey_plan_duration_validation(self):
        """Test estimated duration validation."""
        with self.assertRaises(ValidationError):
            invalid_plan = TherapeuticJourneyPlan(user_id="test_user", estimated_duration=0)
            invalid_plan.validate()

        with self.assertRaises(ValidationError):
            invalid_plan = TherapeuticJourneyPlan(user_id="test_user", estimated_duration=-5)
            invalid_plan.validate()


class TestProgressBasedInterventionSelector(unittest.TestCase):
    """Test cases for ProgressBasedInterventionSelector."""

    def setUp(self):
        """Set up test fixtures."""
        self.selector = ProgressBasedInterventionSelector()
        self.sample_progress_analysis = ProgressAnalysisResult(
            user_id="test_user",
            overall_progress_score=0.6,
            metric_trends={
                ProgressMetricType.EMOTIONAL_REGULATION: {
                    "current_value": 0.4,
                    "improvement_rate": 0.1,
                    "trend_slope": 0.02
                },
                ProgressMetricType.COPING_SKILLS_USAGE: {
                    "current_value": 0.7,
                    "improvement_rate": -0.05,
                    "trend_slope": -0.01
                }
            }
        )

    def test_select_interventions_basic_functionality(self):
        """Test basic intervention selection functionality."""
        current_interventions = [InterventionType.MINDFULNESS]

        selected = self.selector.select_interventions(
            self.sample_progress_analysis, current_interventions, max_interventions=3
        )

        self.assertIsInstance(selected, list)
        self.assertLessEqual(len(selected), 3)

        # All selected interventions should be valid InterventionType
        for intervention in selected:
            self.assertIsInstance(intervention, InterventionType)

    def test_select_interventions_low_progress(self):
        """Test intervention selection for low progress areas."""
        # Create progress analysis with low emotional regulation
        low_progress_analysis = ProgressAnalysisResult(
            user_id="test_user",
            metric_trends={
                ProgressMetricType.EMOTIONAL_REGULATION: {
                    "current_value": 0.2,  # Low progress
                    "improvement_rate": 0.0,
                    "trend_slope": 0.0
                }
            }
        )

        selected = self.selector.select_interventions(low_progress_analysis, [])

        # Should prioritize interventions for emotional regulation
        self.assertGreater(len(selected), 0)
        self.assertIn(InterventionType.MINDFULNESS, selected)

    def test_select_interventions_stagnation(self):
        """Test intervention selection for stagnant progress."""
        # Create progress analysis with stagnant improvement
        stagnant_analysis = ProgressAnalysisResult(
            user_id="test_user",
            metric_trends={
                ProgressMetricType.GOAL_ACHIEVEMENT: {
                    "current_value": 0.6,
                    "improvement_rate": 0.02,  # Very low improvement
                    "trend_slope": 0.0
                }
            }
        )

        current_interventions = [InterventionType.MINDFULNESS]
        selected = self.selector.select_interventions(stagnant_analysis, current_interventions)

        # Should suggest different interventions to break stagnation
        self.assertGreater(len(selected), 0)
        # Should not include current interventions (trying something new)
        self.assertNotIn(InterventionType.MINDFULNESS, selected)

    def test_assess_intervention_effectiveness(self):
        """Test intervention effectiveness assessment."""
        intervention_history = [
            CompletedIntervention(
                intervention_type=InterventionType.MINDFULNESS,
                description="Mindfulness session",
                effectiveness_rating=8.0
            ),
            CompletedIntervention(
                intervention_type=InterventionType.MINDFULNESS,
                description="Another mindfulness session",
                effectiveness_rating=7.0
            ),
            CompletedIntervention(
                intervention_type=InterventionType.COPING_SKILLS,
                description="Coping skills session",
                effectiveness_rating=6.0
            )
        ]

        effectiveness = self.selector.assess_intervention_effectiveness(intervention_history, [])

        self.assertIsInstance(effectiveness, dict)
        self.assertIn(InterventionType.MINDFULNESS, effectiveness)
        self.assertIn(InterventionType.COPING_SKILLS, effectiveness)

        # Mindfulness should have higher effectiveness (average of 8.0 and 7.0)
        self.assertAlmostEqual(effectiveness[InterventionType.MINDFULNESS], 0.75, places=2)
        self.assertAlmostEqual(effectiveness[InterventionType.COPING_SKILLS], 0.6, places=2)

    def test_recommend_intervention_adjustments(self):
        """Test intervention adjustment recommendations."""
        current_interventions = [InterventionType.MINDFULNESS, InterventionType.COPING_SKILLS]
        effectiveness_scores = {
            InterventionType.MINDFULNESS: 0.3,  # Low effectiveness
            InterventionType.COPING_SKILLS: 0.9  # High effectiveness
        }

        recommendations = self.selector.recommend_intervention_adjustments(
            current_interventions, effectiveness_scores, self.sample_progress_analysis
        )

        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), 2)

        # Should recommend discontinuing low-effectiveness intervention
        mindfulness_rec = next(r for r in recommendations if r["intervention"] == InterventionType.MINDFULNESS)
        self.assertEqual(mindfulness_rec["action"], "discontinue")

        # Should recommend intensifying high-effectiveness intervention
        coping_rec = next(r for r in recommendations if r["intervention"] == InterventionType.COPING_SKILLS)
        self.assertEqual(coping_rec["action"], "intensify")


class TestContentDifficultyAdapter(unittest.TestCase):
    """Test cases for ContentDifficultyAdapter."""

    def setUp(self):
        """Set up test fixtures."""
        self.adapter = ContentDifficultyAdapter()
        self.sample_progress_analysis = ProgressAnalysisResult(
            user_id="test_user",
            overall_progress_score=0.7,
            metric_trends={
                ProgressMetricType.GOAL_ACHIEVEMENT: {
                    "improvement_rate": 0.2
                }
            }
        )
        self.sample_user_characteristics = {
            "learning_style": {
                "fast_paced": 0.6
            }
        }

    def test_adapt_content_difficulty_basic_functionality(self):
        """Test basic content difficulty adaptation."""
        adaptation = self.adapter.adapt_content_difficulty(
            "intermediate", self.sample_progress_analysis, self.sample_user_characteristics
        )

        self.assertIsInstance(adaptation, dict)
        self.assertIn("previous_difficulty", adaptation)
        self.assertIn("new_difficulty", adaptation)
        self.assertIn("adaptation_strategy", adaptation)
        self.assertIn("rationale", adaptation)
        self.assertIn("confidence", adaptation)

        # New difficulty should be valid
        self.assertIn(adaptation["new_difficulty"], self.adapter.difficulty_levels)

    def test_adapt_content_difficulty_accelerate(self):
        """Test difficulty adaptation for acceleration."""
        # High progress with strong improvement should accelerate
        high_progress_analysis = ProgressAnalysisResult(
            user_id="test_user",
            overall_progress_score=0.85,
            metric_trends={
                ProgressMetricType.GOAL_ACHIEVEMENT: {
                    "improvement_rate": 0.4
                }
            }
        )

        adaptation = self.adapter.adapt_content_difficulty(
            "intermediate", high_progress_analysis, self.sample_user_characteristics
        )

        self.assertEqual(adaptation["adaptation_strategy"], "accelerate")
        # Should increase difficulty
        current_index = self.adapter.difficulty_levels.index("intermediate")
        new_index = self.adapter.difficulty_levels.index(adaptation["new_difficulty"])
        self.assertGreater(new_index, current_index)

    def test_adapt_content_difficulty_simplify(self):
        """Test difficulty adaptation for simplification."""
        # Low progress with declining performance should simplify
        low_progress_analysis = ProgressAnalysisResult(
            user_id="test_user",
            overall_progress_score=0.15,
            metric_trends={
                ProgressMetricType.GOAL_ACHIEVEMENT: {
                    "improvement_rate": -0.3
                }
            }
        )

        adaptation = self.adapter.adapt_content_difficulty(
            "intermediate", low_progress_analysis, self.sample_user_characteristics
        )

        self.assertEqual(adaptation["adaptation_strategy"], "simplify")
        # Should decrease difficulty
        current_index = self.adapter.difficulty_levels.index("intermediate")
        new_index = self.adapter.difficulty_levels.index(adaptation["new_difficulty"])
        self.assertLess(new_index, current_index)

    def test_adapt_content_difficulty_consolidate(self):
        """Test difficulty adaptation for consolidation."""
        # Good progress with steady improvement should consolidate
        steady_progress_analysis = ProgressAnalysisResult(
            user_id="test_user",
            overall_progress_score=0.65,
            metric_trends={
                ProgressMetricType.GOAL_ACHIEVEMENT: {
                    "improvement_rate": 0.15
                }
            }
        )

        adaptation = self.adapter.adapt_content_difficulty(
            "intermediate", steady_progress_analysis, self.sample_user_characteristics
        )

        self.assertEqual(adaptation["adaptation_strategy"], "consolidate")
        # Should maintain difficulty
        self.assertEqual(adaptation["new_difficulty"], "intermediate")

    def test_generate_difficulty_recommendations(self):
        """Test difficulty recommendation generation."""
        recommendations = self.adapter._generate_difficulty_recommendations("advanced", "accelerate")

        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

        # Should contain relevant recommendations for acceleration
        recommendation_text = " ".join(recommendations).lower()
        self.assertIn("advanced", recommendation_text)


class TestTherapeuticJourneyPlanner(unittest.TestCase):
    """Test cases for TherapeuticJourneyPlanner."""

    def setUp(self):
        """Set up test fixtures."""
        self.planner = TherapeuticJourneyPlanner()
        self.sample_assessment = {
            "therapeutic_readiness": 0.6,
            "prior_therapy_experience": False,
            "current_functioning_level": 0.5
        }
        self.sample_goals = [
            TherapeuticGoal(
                title="Manage Anxiety",
                description="Learn to manage anxiety symptoms",
                target_behaviors=["deep breathing", "mindfulness"]
            ),
            TherapeuticGoal(
                title="Improve Sleep",
                description="Establish healthy sleep patterns",
                target_behaviors=["sleep hygiene"]
            )
        ]

    def test_create_therapeutic_journey_plan_basic_functionality(self):
        """Test basic journey plan creation."""
        plan = self.planner.create_therapeutic_journey_plan(
            "test_user", self.sample_assessment, self.sample_goals
        )

        self.assertIsInstance(plan, TherapeuticJourneyPlan)
        self.assertTrue(plan.validate())
        self.assertEqual(plan.user_id, "test_user")
        self.assertGreater(len(plan.planned_phases), 0)
        self.assertGreater(len(plan.milestones), 0)
        self.assertGreater(plan.estimated_duration, 0)

    def test_determine_starting_phase_assessment(self):
        """Test starting phase determination for assessment."""
        low_readiness_assessment = {
            "therapeutic_readiness": 0.3,
            "prior_therapy_experience": False,
            "current_functioning_level": 0.4
        }

        starting_phase = self.planner._determine_starting_phase(low_readiness_assessment)
        self.assertEqual(starting_phase, TherapeuticPhase.ASSESSMENT)

    def test_determine_starting_phase_foundation_building(self):
        """Test starting phase determination for foundation building."""
        moderate_readiness_assessment = {
            "therapeutic_readiness": 0.7,
            "prior_therapy_experience": False,
            "current_functioning_level": 0.6
        }

        starting_phase = self.planner._determine_starting_phase(moderate_readiness_assessment)
        self.assertEqual(starting_phase, TherapeuticPhase.FOUNDATION_BUILDING)

    def test_determine_starting_phase_skill_development(self):
        """Test starting phase determination for skill development."""
        high_readiness_assessment = {
            "therapeutic_readiness": 0.9,
            "prior_therapy_experience": True,
            "current_functioning_level": 0.8
        }

        starting_phase = self.planner._determine_starting_phase(high_readiness_assessment)
        self.assertEqual(starting_phase, TherapeuticPhase.SKILL_DEVELOPMENT)

    def test_plan_therapeutic_phases(self):
        """Test therapeutic phase planning."""
        planned_phases = self.planner._plan_therapeutic_phases(
            TherapeuticPhase.FOUNDATION_BUILDING, self.sample_goals
        )

        self.assertIsInstance(planned_phases, list)
        self.assertGreater(len(planned_phases), 0)

        # First phase should be foundation building
        self.assertEqual(planned_phases[0]["phase"], TherapeuticPhase.FOUNDATION_BUILDING)

        # Each phase should have required fields
        for phase in planned_phases:
            self.assertIn("phase", phase)
            self.assertIn("duration_weeks", phase)
            self.assertIn("completion_criteria", phase)
            self.assertIn("key_metrics", phase)
            self.assertIn("relevant_goals", phase)

    def test_generate_milestones(self):
        """Test milestone generation."""
        planned_phases = [
            {
                "phase": TherapeuticPhase.FOUNDATION_BUILDING,
                "duration_weeks": 4,
                "completion_criteria": ["basic_skills_learned"]
            }
        ]

        milestones = self.planner._generate_milestones(planned_phases)

        self.assertIsInstance(milestones, list)
        self.assertGreater(len(milestones), 0)

        # Each milestone should have required fields
        for milestone in milestones:
            self.assertIn("name", milestone)
            self.assertIn("phase", milestone)
            self.assertIn("target_week", milestone)
            self.assertIn("type", milestone)
            self.assertIn("status", milestone)

    def test_update_journey_progress(self):
        """Test journey progress updating."""
        journey_plan = TherapeuticJourneyPlan(
            user_id="test_user",
            current_phase=TherapeuticPhase.FOUNDATION_BUILDING
        )

        progress_analysis = ProgressAnalysisResult(
            user_id="test_user",
            overall_progress_score=0.8,
            metric_trends={
                ProgressMetricType.COPING_SKILLS_USAGE: {
                    "current_value": 0.8
                },
                ProgressMetricType.ENGAGEMENT_LEVEL: {
                    "current_value": 0.7
                }
            }
        )

        update_result = self.planner.update_journey_progress(journey_plan, progress_analysis)

        self.assertIsInstance(update_result, dict)
        self.assertIn("current_phase", update_result)
        self.assertIn("phase_completion_percentage", update_result)
        self.assertIn("ready_for_next_phase", update_result)
        self.assertIn("recommendations", update_result)


class TestAdaptiveTherapyOrchestrator(unittest.TestCase):
    """Test cases for AdaptiveTherapyOrchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = AdaptiveTherapyOrchestrator()
        self.sample_progress_analysis = ProgressAnalysisResult(
            user_id="test_user",
            overall_progress_score=0.7,
            metric_trends={
                ProgressMetricType.EMOTIONAL_REGULATION: {
                    "current_value": 0.6,
                    "improvement_rate": 0.2,
                    "trend_slope": 0.05
                }
            }
        )
        self.sample_session = SessionState(
            session_id="test_session",
            user_id="test_user",
            narrative_position=5
        )
        self.sample_profile = PersonalizationProfile(
            user_id="test_user",
            learning_velocity=0.6
        )

    def test_make_adaptation_decision_basic_functionality(self):
        """Test basic adaptation decision making."""
        decision = self.orchestrator.make_adaptation_decision(
            "test_user", self.sample_progress_analysis, self.sample_session, self.sample_profile
        )

        self.assertIsInstance(decision, AdaptationDecision)
        self.assertTrue(decision.validate())
        self.assertEqual(decision.user_id, "test_user")
        self.assertIsInstance(decision.adaptation_strategy, AdaptationStrategy)
        self.assertGreater(len(decision.rationale), 0)
        self.assertGreater(len(decision.implementation_steps), 0)

    def test_analyze_current_situation(self):
        """Test current situation analysis."""
        situation = self.orchestrator._analyze_current_situation(
            self.sample_progress_analysis, self.sample_session, self.sample_profile
        )

        self.assertIsInstance(situation, dict)
        self.assertIn("overall_progress", situation)
        self.assertIn("progress_trend", situation)
        self.assertIn("engagement_level", situation)
        self.assertIn("learning_velocity", situation)

        # All values should be within reasonable ranges
        self.assertGreaterEqual(situation["overall_progress"], 0.0)
        self.assertLessEqual(situation["overall_progress"], 1.0)
        self.assertEqual(situation["learning_velocity"], 0.6)

    def test_determine_adaptation_strategy_accelerate(self):
        """Test adaptation strategy determination for acceleration."""
        high_performance_situation = {
            "overall_progress": 0.85,
            "progress_trend": 0.3,
            "learning_velocity": 0.8,
            "engagement_level": 0.7
        }

        strategy = self.orchestrator._determine_adaptation_strategy(high_performance_situation)
        self.assertEqual(strategy, AdaptationStrategy.ACCELERATE)

    def test_determine_adaptation_strategy_remediate(self):
        """Test adaptation strategy determination for remediation."""
        declining_situation = {
            "overall_progress": 0.6,
            "progress_trend": -0.2,
            "learning_velocity": 0.5,
            "engagement_level": 0.5
        }

        strategy = self.orchestrator._determine_adaptation_strategy(declining_situation)
        self.assertEqual(strategy, AdaptationStrategy.REMEDIATE)

    def test_determine_adaptation_strategy_simplify(self):
        """Test adaptation strategy determination for simplification."""
        low_performance_situation = {
            "overall_progress": 0.3,
            "progress_trend": -0.15,
            "learning_velocity": 0.3,
            "engagement_level": 0.4
        }

        strategy = self.orchestrator._determine_adaptation_strategy(low_performance_situation)
        self.assertEqual(strategy, AdaptationStrategy.SIMPLIFY)

    def test_generate_implementation_steps(self):
        """Test implementation steps generation."""
        steps = self.orchestrator._generate_implementation_steps(
            AdaptationStrategy.ACCELERATE, {}, None
        )

        self.assertIsInstance(steps, list)
        self.assertGreater(len(steps), 0)

        # Steps should be relevant to acceleration
        steps_text = " ".join(steps).lower()
        self.assertIn("increase", steps_text)

    def test_calculate_progress_trend(self):
        """Test progress trend calculation."""
        trend = self.orchestrator._calculate_progress_trend(self.sample_progress_analysis)

        self.assertIsInstance(trend, float)
        # Should be positive based on sample data
        self.assertGreater(trend, 0.0)

    def test_assess_engagement_level(self):
        """Test engagement level assessment."""
        engagement = self.orchestrator._assess_engagement_level(self.sample_session)

        self.assertIsInstance(engagement, float)
        self.assertGreaterEqual(engagement, 0.0)
        self.assertLessEqual(engagement, 1.0)


class TestProgressBasedTherapeuticAdaptation(unittest.TestCase):
    """Test cases for main ProgressBasedTherapeuticAdaptation integration system."""

    def setUp(self):
        """Set up test fixtures."""
        self.adaptation_system = ProgressBasedTherapeuticAdaptation()
        self.test_user_id = "test_user_123"
        self.session_state, self.profile, self.progress_analysis = create_sample_adaptation_context(self.test_user_id)

    def test_integrate_progress_with_therapy_basic_functionality(self):
        """Test basic integration functionality."""
        result = self.adaptation_system.integrate_progress_with_therapy(
            self.test_user_id, self.session_state, self.profile
        )

        self.assertIsInstance(result, dict)
        self.assertIn("progress_tracking", result)
        self.assertIn("adaptation_decision", result)
        self.assertIn("therapeutic_content", result)
        self.assertIn("journey_progress", result)
        self.assertIn("recommendations", result)
        self.assertIn("integration_metadata", result)

    def test_progress_tracking_integration(self):
        """Test progress tracking integration."""
        result = self.adaptation_system.integrate_progress_with_therapy(
            self.test_user_id, self.session_state, self.profile
        )

        progress_tracking = result["progress_tracking"]
        self.assertIn("metrics_recorded", progress_tracking)
        self.assertIn("overall_progress_score", progress_tracking)
        self.assertIn("next_focus", progress_tracking)

        # Progress score should be reasonable
        self.assertGreaterEqual(progress_tracking["overall_progress_score"], 0.0)
        self.assertLessEqual(progress_tracking["overall_progress_score"], 1.0)

    def test_adaptation_decision_integration(self):
        """Test adaptation decision integration."""
        result = self.adaptation_system.integrate_progress_with_therapy(
            self.test_user_id, self.session_state, self.profile
        )

        adaptation_decision = result["adaptation_decision"]
        self.assertIn("strategy", adaptation_decision)
        self.assertIn("rationale", adaptation_decision)
        self.assertIn("confidence", adaptation_decision)
        self.assertIn("implementation_steps", adaptation_decision)

        # Strategy should be valid
        valid_strategies = [s.value for s in AdaptationStrategy]
        self.assertIn(adaptation_decision["strategy"], valid_strategies)

        # Confidence should be within valid range
        self.assertGreaterEqual(adaptation_decision["confidence"], 0.0)
        self.assertLessEqual(adaptation_decision["confidence"], 1.0)

    def test_therapeutic_content_integration(self):
        """Test therapeutic content integration."""
        result = self.adaptation_system.integrate_progress_with_therapy(
            self.test_user_id, self.session_state, self.profile
        )

        therapeutic_content = result["therapeutic_content"]
        self.assertIsInstance(therapeutic_content, dict)

        # Should contain adapted content
        if "adapted_content" in therapeutic_content:
            adapted_content = therapeutic_content["adapted_content"]
            self.assertIn("title", adapted_content)
            self.assertIn("description", adapted_content)

    def test_journey_progress_integration(self):
        """Test journey progress integration."""
        result = self.adaptation_system.integrate_progress_with_therapy(
            self.test_user_id, self.session_state, self.profile
        )

        journey_progress = result["journey_progress"]
        self.assertIn("current_phase", journey_progress)
        self.assertIn("completion_percentage", journey_progress)
        self.assertIn("ready_for_next_phase", journey_progress)

        # Current phase should be valid
        valid_phases = [p.value for p in TherapeuticPhase]
        self.assertIn(journey_progress["current_phase"], valid_phases)

        # Completion percentage should be within valid range
        self.assertGreaterEqual(journey_progress["completion_percentage"], 0.0)
        self.assertLessEqual(journey_progress["completion_percentage"], 100.0)

    def test_recommendations_integration(self):
        """Test recommendations integration."""
        result = self.adaptation_system.integrate_progress_with_therapy(
            self.test_user_id, self.session_state, self.profile
        )

        recommendations = result["recommendations"]
        self.assertIsInstance(recommendations, list)

        # Each recommendation should have required fields
        for rec in recommendations:
            self.assertIn("type", rec)
            self.assertIn("title", rec)
            self.assertIn("description", rec)

    def test_journey_plan_creation_and_storage(self):
        """Test journey plan creation and storage."""
        # First integration should create journey plan
        self.adaptation_system.integrate_progress_with_therapy(
            self.test_user_id, self.session_state, self.profile
        )

        # Journey plan should be stored
        self.assertIn(self.test_user_id, self.adaptation_system.user_journey_plans)
        journey_plan = self.adaptation_system.user_journey_plans[self.test_user_id]
        self.assertIsInstance(journey_plan, TherapeuticJourneyPlan)

        # Second integration should use existing journey plan
        self.adaptation_system.integrate_progress_with_therapy(
            self.test_user_id, self.session_state, self.profile
        )

        # Should still have the same journey plan
        self.assertEqual(
            self.adaptation_system.user_journey_plans[self.test_user_id].plan_id,
            journey_plan.plan_id
        )

    def test_adaptation_decision_storage(self):
        """Test adaptation decision storage."""
        # Run integration multiple times
        for _i in range(3):
            self.adaptation_system.integrate_progress_with_therapy(
                self.test_user_id, self.session_state, self.profile
            )

        # Should have stored adaptation decisions
        self.assertIn(self.test_user_id, self.adaptation_system.adaptation_decisions)
        decisions = self.adaptation_system.adaptation_decisions[self.test_user_id]
        self.assertEqual(len(decisions), 3)

        # All decisions should be valid
        for decision in decisions:
            self.assertIsInstance(decision, AdaptationDecision)
            self.assertTrue(decision.validate())

    def test_get_adaptation_insights_no_data(self):
        """Test getting adaptation insights with no data."""
        insights = self.adaptation_system.get_adaptation_insights("nonexistent_user")

        self.assertIn("message", insights)
        self.assertEqual(insights["message"], "No adaptation data available")

    def test_get_adaptation_insights_with_data(self):
        """Test getting adaptation insights with existing data."""
        # Generate some adaptation data
        self.adaptation_system.integrate_progress_with_therapy(
            self.test_user_id, self.session_state, self.profile
        )

        insights = self.adaptation_system.get_adaptation_insights(self.test_user_id)

        self.assertIn("total_adaptations", insights)
        self.assertIn("most_common_strategy", insights)
        self.assertIn("strategy_distribution", insights)
        self.assertIn("average_confidence", insights)
        self.assertIn("adaptation_effectiveness", insights)
        self.assertIn("journey_progress", insights)
        self.assertIn("recent_adaptations", insights)

        # Should have at least one adaptation
        self.assertGreater(insights["total_adaptations"], 0)

        # Effectiveness should be within valid range
        self.assertGreaterEqual(insights["adaptation_effectiveness"], 0.0)
        self.assertLessEqual(insights["adaptation_effectiveness"], 1.0)

    def test_error_handling(self):
        """Test error handling in integration."""
        # Test with invalid session state
        invalid_session = SessionState(session_id="", user_id="")

        result = self.adaptation_system.integrate_progress_with_therapy(
            "invalid_user", invalid_session, self.profile
        )

        # Should handle error gracefully
        self.assertIn("error", result)
        self.assertIn("fallback_content", result)


class TestSampleDataGeneration(unittest.TestCase):
    """Test cases for sample data generation utilities."""

    def test_create_sample_adaptation_context(self):
        """Test creating sample adaptation context."""
        user_id = "test_user"
        session_state, profile, progress_analysis = create_sample_adaptation_context(user_id)

        self.assertIsInstance(session_state, SessionState)
        self.assertIsInstance(profile, PersonalizationProfile)
        self.assertIsInstance(progress_analysis, ProgressAnalysisResult)

        # All should have the same user ID
        self.assertEqual(session_state.user_id, user_id)
        self.assertEqual(profile.user_id, user_id)
        self.assertEqual(progress_analysis.user_id, user_id)


if __name__ == "__main__":
    # Configure test logging
    logging.basicConfig(level=logging.WARNING)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_classes = [
        TestAdaptationDecision,
        TestTherapeuticJourneyPlan,
        TestProgressBasedInterventionSelector,
        TestContentDifficultyAdapter,
        TestTherapeuticJourneyPlanner,
        TestAdaptiveTherapyOrchestrator,
        TestProgressBasedTherapeuticAdaptation,
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
