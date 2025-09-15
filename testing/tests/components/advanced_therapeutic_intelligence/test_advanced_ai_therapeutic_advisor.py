"""
Tests for Advanced AI Therapeutic Advisor

This module tests the AI therapeutic advisor functionality including
real-time therapeutic guidance, optimal intervention strategies,
adaptive therapeutic approaches, and clinical validation integration.
"""

from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from src.components.advanced_therapeutic_intelligence.advanced_ai_therapeutic_advisor import (
    AdvancedAITherapeuticAdvisor,
    InterventionStrategy,
    TherapeuticApproach,
    TherapeuticDecision,
    TherapeuticGuidance,
    TherapeuticGuidanceType,
)


class TestAdvancedAITherapeuticAdvisor:
    """Test Advanced AI Therapeutic Advisor functionality."""

    @pytest_asyncio.fixture
    async def advisor_system(self):
        """Create test advisor system instance."""
        system = AdvancedAITherapeuticAdvisor()
        await system.initialize()
        yield system
        await system.shutdown()

    @pytest.fixture
    def mock_therapeutic_systems(self):
        """Create mock therapeutic systems."""
        systems = {}

        for system_name in [
            "consequence_system",
            "emotional_safety_system",
            "adaptive_difficulty_engine",
            "character_development_system",
            "therapeutic_integration_system",
            "gameplay_loop_controller",
            "replayability_system",
            "collaborative_system",
            "error_recovery_manager"
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}
            systems[system_name] = mock_system

        return systems

    @pytest.fixture
    def mock_integration_systems(self):
        """Create mock integration systems."""
        systems = {}

        for system_name in [
            "clinical_dashboard_manager",
            "cloud_deployment_manager",
            "clinical_validation_manager"
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}
            systems[system_name] = mock_system

        return systems

    @pytest.fixture
    def mock_personalization_engine(self):
        """Create mock personalization engine."""
        engine = AsyncMock()
        engine.health_check.return_value = {"status": "healthy"}

        # Mock user profile
        mock_profile = Mock()
        mock_profile.interaction_preferences = {"preferred_framework": "cognitive_behavioral"}
        mock_profile.therapeutic_preferences = {"current_framework": "cognitive_behavioral"}
        engine.get_user_profile.return_value = mock_profile

        return engine

    @pytest.fixture
    def mock_predictive_analytics(self):
        """Create mock predictive analytics."""
        analytics = AsyncMock()
        analytics.health_check.return_value = {"status": "healthy"}

        # Mock predictions
        mock_prediction = Mock()
        mock_prediction.prediction_type.value = "crisis_risk"
        mock_prediction.predicted_value = 0.3
        analytics.generate_therapeutic_predictions.return_value = [mock_prediction]

        return analytics

    @pytest.fixture
    def sample_guidance_context(self):
        """Create sample guidance context."""
        return {
            "primary_concerns": ["anxiety", "depression"],
            "crisis_indicators": {"immediate_risk": False, "risk_level": "low"},
            "progress_data": {
                "engagement_score": 0.7,
                "skill_acquisition": 0.6,
                "goal_progress": 0.5
            },
            "session_data": {
                "current_mood": "moderate",
                "energy_level": "low",
                "coping_utilization": "moderate"
            }
        }

    @pytest.mark.asyncio
    async def test_initialization(self, advisor_system):
        """Test advisor system initialization."""
        assert advisor_system.status == "running"
        assert len(advisor_system.guidance_models) == 5
        assert len(advisor_system.strategy_optimization_models) == 4
        assert len(advisor_system.decision_support_models) == 4

        # Should have background tasks running
        assert advisor_system._guidance_generation_task is not None
        assert advisor_system._strategy_optimization_task is not None
        assert advisor_system._decision_validation_task is not None
        assert advisor_system._knowledge_update_task is not None

    @pytest.mark.asyncio
    async def test_system_dependency_injection(self, advisor_system, mock_therapeutic_systems, mock_integration_systems, mock_personalization_engine, mock_predictive_analytics):
        """Test system dependency injection."""
        advisor_system.inject_therapeutic_systems(**mock_therapeutic_systems)
        advisor_system.inject_integration_systems(**mock_integration_systems)
        advisor_system.inject_personalization_engine(mock_personalization_engine)
        advisor_system.inject_predictive_analytics(mock_predictive_analytics)

        # Should have all systems injected
        assert len(advisor_system.therapeutic_systems) == 9
        assert advisor_system.clinical_dashboard_manager is not None
        assert advisor_system.cloud_deployment_manager is not None
        assert advisor_system.clinical_validation_manager is not None
        assert advisor_system.personalization_engine is not None
        assert advisor_system.predictive_analytics is not None

    @pytest.mark.asyncio
    async def test_generate_therapeutic_guidance(self, advisor_system, mock_personalization_engine, mock_predictive_analytics, sample_guidance_context):
        """Test therapeutic guidance generation."""
        advisor_system.inject_personalization_engine(mock_personalization_engine)
        advisor_system.inject_predictive_analytics(mock_predictive_analytics)

        user_id = "test_user_001"

        # Test different guidance types
        guidance_types = [
            TherapeuticGuidanceType.CRISIS_INTERVENTION,
            TherapeuticGuidanceType.INTERVENTION_STRATEGY,
            TherapeuticGuidanceType.THERAPEUTIC_APPROACH,
            TherapeuticGuidanceType.PROGRESS_OPTIMIZATION,
            TherapeuticGuidanceType.SESSION_PLANNING
        ]

        for guidance_type in guidance_types:
            guidance = await advisor_system.generate_therapeutic_guidance(
                user_id=user_id,
                guidance_type=guidance_type,
                context=sample_guidance_context
            )

            # Should generate valid guidance
            assert isinstance(guidance, TherapeuticGuidance)
            assert guidance.user_id == user_id
            assert guidance.guidance_type == guidance_type
            assert guidance.title != ""
            assert guidance.description != ""
            assert guidance.rationale != ""
            assert guidance.confidence_score >= 0.0 and guidance.confidence_score <= 1.0
            assert len(guidance.recommended_actions) > 0

        # Should store guidance
        assert user_id in advisor_system.active_guidance
        assert len(advisor_system.active_guidance[user_id]) == len(guidance_types)
        assert advisor_system.advisor_metrics["total_guidance_generated"] == len(guidance_types)

    @pytest.mark.asyncio
    async def test_suggest_optimal_intervention_strategy(self, advisor_system, mock_personalization_engine, mock_predictive_analytics):
        """Test optimal intervention strategy suggestion."""
        advisor_system.inject_personalization_engine(mock_personalization_engine)
        advisor_system.inject_predictive_analytics(mock_predictive_analytics)

        user_id = "test_user_002"
        target_outcomes = ["anxiety_reduction", "coping_skills", "emotional_regulation"]

        # Generate intervention strategy
        strategy = await advisor_system.suggest_optimal_intervention_strategy(
            user_id=user_id,
            target_outcomes=target_outcomes,
            constraints={"session_limit": 12, "intensity": "moderate"}
        )

        # Should generate valid strategy
        assert isinstance(strategy, InterventionStrategy)
        assert strategy.user_id == user_id
        assert strategy.strategy_name != ""
        assert strategy.description != ""
        assert strategy.target_outcomes == target_outcomes
        assert len(strategy.intervention_steps) > 0
        assert strategy.evidence_strength >= 0.0 and strategy.evidence_strength <= 1.0
        assert strategy.expected_effectiveness >= 0.0 and strategy.expected_effectiveness <= 1.0
        assert len(strategy.progress_indicators) > 0
        assert len(strategy.safety_considerations) > 0

        # Should store strategy
        assert user_id in advisor_system.intervention_strategies
        assert len(advisor_system.intervention_strategies[user_id]) == 1
        assert advisor_system.advisor_metrics["total_strategies_created"] == 1

    @pytest.mark.asyncio
    async def test_adapt_therapeutic_approach(self, advisor_system, mock_predictive_analytics):
        """Test therapeutic approach adaptation."""
        advisor_system.inject_predictive_analytics(mock_predictive_analytics)

        user_id = "test_user_003"
        current_approach = TherapeuticApproach.COGNITIVE_BEHAVIORAL

        # Test with poor progress (should suggest adaptation)
        poor_progress_data = {
            "effectiveness_score": 0.3,
            "engagement_score": 0.4,
            "goal_achievement": 0.2,
            "session_outcomes": ["poor", "poor", "moderate"]
        }

        guidance = await advisor_system.adapt_therapeutic_approach(
            user_id=user_id,
            current_approach=current_approach,
            progress_data=poor_progress_data
        )

        # Should generate adaptation guidance
        assert isinstance(guidance, TherapeuticGuidance)
        assert guidance.user_id == user_id
        assert guidance.guidance_type == TherapeuticGuidanceType.THERAPEUTIC_APPROACH
        assert guidance.title != ""
        assert guidance.description != ""
        assert guidance.rationale != ""
        assert len(guidance.recommended_actions) > 0

        # Test with good progress (should continue current approach)
        good_progress_data = {
            "effectiveness_score": 0.8,
            "engagement_score": 0.9,
            "goal_achievement": 0.7,
            "session_outcomes": ["good", "excellent", "good"]
        }

        guidance2 = await advisor_system.adapt_therapeutic_approach(
            user_id=user_id,
            current_approach=current_approach,
            progress_data=good_progress_data
        )

        # Should recommend continuing current approach
        assert guidance2.therapeutic_approach == current_approach
        assert "continue" in guidance2.title.lower()

    @pytest.mark.asyncio
    async def test_make_therapeutic_decision(self, advisor_system, mock_personalization_engine, mock_predictive_analytics):
        """Test AI therapeutic decision making."""
        advisor_system.inject_personalization_engine(mock_personalization_engine)
        advisor_system.inject_predictive_analytics(mock_predictive_analytics)

        user_id = "test_user_004"
        decision_context = "Treatment approach selection"
        available_options = [
            "cognitive_behavioral_therapy",
            "dialectical_behavioral_therapy",
            "acceptance_commitment_therapy"
        ]
        decision_criteria = {
            "effectiveness": 0.8,
            "user_preference": 0.7,
            "evidence_base": 0.9,
            "resource_availability": 0.6
        }

        # Make therapeutic decision
        decision = await advisor_system.make_therapeutic_decision(
            user_id=user_id,
            decision_context=decision_context,
            available_options=available_options,
            decision_criteria=decision_criteria
        )

        # Should generate valid decision
        assert isinstance(decision, TherapeuticDecision)
        assert decision.user_id == user_id
        assert decision.decision_context == decision_context
        assert decision.primary_recommendation in available_options
        assert len(decision.alternative_options) > 0
        assert decision.decision_rationale != ""
        assert len(decision.implementation_steps) > 0
        assert len(decision.contingency_plans) > 0

        # Should store decision
        assert user_id in advisor_system.therapeutic_decisions
        assert len(advisor_system.therapeutic_decisions[user_id]) == 1
        assert advisor_system.advisor_metrics["total_decisions_made"] == 1

    @pytest.mark.asyncio
    async def test_get_real_time_guidance(self, advisor_system, sample_guidance_context):
        """Test real-time guidance generation."""
        user_id = "test_user_005"

        # Test with crisis indicators
        crisis_session_data = {
            "crisis_indicators": {"immediate_risk": True, "risk_level": "high"},
            "current_mood": "very_low",
            "distress_level": "high",
            "coping_utilization": "poor"
        }

        guidance_list = await advisor_system.get_real_time_guidance(
            user_id=user_id,
            current_session_data=crisis_session_data
        )

        # Should generate multiple guidance items
        assert isinstance(guidance_list, list)
        assert len(guidance_list) > 0

        # Should include crisis intervention guidance
        crisis_guidance = [g for g in guidance_list if g.guidance_type == TherapeuticGuidanceType.CRISIS_INTERVENTION]
        assert len(crisis_guidance) > 0

        # Test with normal session data
        normal_session_data = {
            "crisis_indicators": {"immediate_risk": False, "risk_level": "low"},
            "current_mood": "moderate",
            "distress_level": "low",
            "coping_utilization": "good"
        }

        guidance_list2 = await advisor_system.get_real_time_guidance(
            user_id=user_id,
            current_session_data=normal_session_data
        )

        # Should generate session planning guidance
        assert len(guidance_list2) > 0
        session_guidance = [g for g in guidance_list2 if g.guidance_type == TherapeuticGuidanceType.SESSION_PLANNING]
        assert len(session_guidance) > 0

    @pytest.mark.asyncio
    async def test_validate_guidance_effectiveness(self, advisor_system):
        """Test guidance effectiveness validation."""
        user_id = "test_user_006"

        # Generate guidance first
        guidance = await advisor_system.generate_therapeutic_guidance(
            user_id=user_id,
            guidance_type=TherapeuticGuidanceType.INTERVENTION_STRATEGY
        )

        # Validate effectiveness
        outcome_data = {
            "effectiveness_score": 0.8,
            "user_satisfaction": 0.9,
            "goal_achievement": 0.7,
            "symptom_improvement": 0.6
        }

        await advisor_system.validate_guidance_effectiveness(
            guidance_id=guidance.guidance_id,
            outcome_data=outcome_data
        )

        # Should update guidance effectiveness
        assert guidance.effectiveness_score is not None
        assert guidance.effectiveness_score > 0.0
        assert guidance.status == "validated"

        # Should update metrics
        assert advisor_system.advisor_metrics["guidance_accuracy"] > 0.0

    @pytest.mark.asyncio
    async def test_get_advisor_insights(self, advisor_system, mock_personalization_engine, mock_predictive_analytics):
        """Test advisor insights generation."""
        advisor_system.inject_personalization_engine(mock_personalization_engine)
        advisor_system.inject_predictive_analytics(mock_predictive_analytics)

        user_id = "test_user_007"

        # Generate some guidance, strategies, and decisions
        await advisor_system.generate_therapeutic_guidance(
            user_id=user_id,
            guidance_type=TherapeuticGuidanceType.INTERVENTION_STRATEGY
        )

        await advisor_system.suggest_optimal_intervention_strategy(
            user_id=user_id,
            target_outcomes=["anxiety_reduction"]
        )

        await advisor_system.make_therapeutic_decision(
            user_id=user_id,
            decision_context="Treatment planning",
            available_options=["option_a", "option_b"],
            decision_criteria={"effectiveness": 0.8}
        )

        # Get insights
        insights = await advisor_system.get_advisor_insights(user_id)

        # Should return comprehensive insights
        assert "user_id" in insights
        assert "analysis_timestamp" in insights
        assert "guidance_summary" in insights
        assert "strategy_summary" in insights
        assert "decision_summary" in insights
        assert "therapeutic_recommendations" in insights
        assert "risk_assessment" in insights

        # Validate guidance summary
        guidance_summary = insights["guidance_summary"]
        assert guidance_summary["total_guidance_provided"] > 0
        assert len(guidance_summary["guidance_types"]) > 0
        assert guidance_summary["average_confidence"] >= 0.0

        # Validate strategy summary
        strategy_summary = insights["strategy_summary"]
        assert strategy_summary["total_strategies_created"] > 0
        assert len(strategy_summary["therapeutic_frameworks"]) > 0

        # Validate decision summary
        decision_summary = insights["decision_summary"]
        assert decision_summary["total_decisions_made"] > 0
        assert len(decision_summary["decision_contexts"]) > 0

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, advisor_system, mock_personalization_engine, mock_predictive_analytics, sample_guidance_context):
        """Test performance benchmarks for AI therapeutic advisor."""
        import time

        advisor_system.inject_personalization_engine(mock_personalization_engine)
        advisor_system.inject_predictive_analytics(mock_predictive_analytics)

        user_id = "performance_test_user"

        # Test guidance generation performance
        start_time = time.perf_counter()

        await advisor_system.generate_therapeutic_guidance(
            user_id=user_id,
            guidance_type=TherapeuticGuidanceType.INTERVENTION_STRATEGY,
            context=sample_guidance_context
        )

        guidance_time = (time.perf_counter() - start_time) * 1000
        assert guidance_time < 500.0  # Should be under 500ms

        # Test strategy suggestion performance
        start_time = time.perf_counter()

        await advisor_system.suggest_optimal_intervention_strategy(
            user_id=user_id,
            target_outcomes=["anxiety_reduction", "coping_skills"]
        )

        strategy_time = (time.perf_counter() - start_time) * 1000
        assert strategy_time < 500.0  # Should be under 500ms

        # Test decision making performance
        start_time = time.perf_counter()

        await advisor_system.make_therapeutic_decision(
            user_id=user_id,
            decision_context="Treatment approach",
            available_options=["cbt", "dbt", "act"],
            decision_criteria={"effectiveness": 0.8}
        )

        decision_time = (time.perf_counter() - start_time) * 1000
        assert decision_time < 500.0  # Should be under 500ms

        # Test real-time guidance performance
        start_time = time.perf_counter()

        await advisor_system.get_real_time_guidance(
            user_id=user_id,
            current_session_data=sample_guidance_context["session_data"]
        )

        real_time_time = (time.perf_counter() - start_time) * 1000
        assert real_time_time < 300.0  # Should be under 300ms

        # Test insights generation performance
        start_time = time.perf_counter()

        await advisor_system.get_advisor_insights(user_id)

        insights_time = (time.perf_counter() - start_time) * 1000
        assert insights_time < 300.0  # Should be under 300ms

    @pytest.mark.asyncio
    async def test_advisor_interface_compatibility(self, advisor_system, mock_therapeutic_systems, mock_integration_systems, mock_personalization_engine, mock_predictive_analytics):
        """Test compatibility with advisor interface expectations."""
        # Inject all dependencies
        advisor_system.inject_therapeutic_systems(**mock_therapeutic_systems)
        advisor_system.inject_integration_systems(**mock_integration_systems)
        advisor_system.inject_personalization_engine(mock_personalization_engine)
        advisor_system.inject_predictive_analytics(mock_predictive_analytics)

        user_id = "interface_test_user"

        # Test complete advisor workflow
        guidance = await advisor_system.generate_therapeutic_guidance(
            user_id=user_id,
            guidance_type=TherapeuticGuidanceType.INTERVENTION_STRATEGY
        )

        # Should match expected guidance structure
        assert hasattr(guidance, "guidance_id")
        assert hasattr(guidance, "guidance_type")
        assert hasattr(guidance, "title")
        assert hasattr(guidance, "description")
        assert hasattr(guidance, "rationale")
        assert hasattr(guidance, "confidence_score")
        assert hasattr(guidance, "recommended_actions")

        # Test strategy suggestion
        strategy = await advisor_system.suggest_optimal_intervention_strategy(
            user_id=user_id,
            target_outcomes=["test_outcome"]
        )

        # Should match expected strategy structure
        assert hasattr(strategy, "strategy_id")
        assert hasattr(strategy, "strategy_name")
        assert hasattr(strategy, "therapeutic_framework")
        assert hasattr(strategy, "intervention_steps")
        assert hasattr(strategy, "expected_effectiveness")

        # Test decision making
        decision = await advisor_system.make_therapeutic_decision(
            user_id=user_id,
            decision_context="test_context",
            available_options=["option1", "option2"],
            decision_criteria={"test": 0.5}
        )

        # Should match expected decision structure
        assert hasattr(decision, "decision_id")
        assert hasattr(decision, "primary_recommendation")
        assert hasattr(decision, "decision_rationale")
        assert hasattr(decision, "confidence_level")

        # Test health check
        health_check = await advisor_system.health_check()

        # Should match expected health check structure
        assert "status" in health_check
        assert "advisor_status" in health_check
        assert "total_active_guidance" in health_check
        assert "advisor_metrics" in health_check
