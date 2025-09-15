"""
Tests for Predictive Therapeutic Analytics

This module tests the predictive analytics system functionality including
therapeutic pattern analysis, crisis prediction, intervention optimization,
and predictive modeling capabilities.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src.components.advanced_therapeutic_intelligence.predictive_therapeutic_analytics import (
    AnalyticsTimeframe,
    InterventionOptimization,
    PredictionType,
    PredictiveTherapeuticAnalytics,
    TherapeuticPattern,
    TherapeuticPrediction,
)


class TestPredictiveTherapeuticAnalytics:
    """Test Predictive Therapeutic Analytics functionality."""

    @pytest_asyncio.fixture
    async def analytics_system(self):
        """Create test analytics system instance."""
        system = PredictiveTherapeuticAnalytics()
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
        return engine

    @pytest.fixture
    def sample_interaction_data(self):
        """Create sample interaction data."""
        return [
            {
                "timestamp": datetime.utcnow() - timedelta(hours=i),
                "system_name": "consequence_system",
                "engagement_score": 0.7 + (i % 3) * 0.1,
                "satisfaction_score": 0.6 + (i % 4) * 0.1,
                "therapeutic_response": 0.8 - (i % 2) * 0.2,
                "effectiveness": 0.75 + (i % 3) * 0.05,
                "intervention_data": {"effectiveness": 0.7 + (i % 2) * 0.1},
                "crisis_indicators": {"risk_score": 0.2 + (i % 5) * 0.1}
            }
            for i in range(15)
        ]

    @pytest.mark.asyncio
    async def test_initialization(self, analytics_system):
        """Test analytics system initialization."""
        assert analytics_system.status == "running"
        assert len(analytics_system.prediction_models) == 5
        assert len(analytics_system.pattern_recognition_models) == 4
        assert len(analytics_system.optimization_models) == 3

        # Should have background tasks running
        assert analytics_system._pattern_analysis_task is not None
        assert analytics_system._prediction_generation_task is not None
        assert analytics_system._optimization_task is not None
        assert analytics_system._model_training_task is not None

    @pytest.mark.asyncio
    async def test_system_dependency_injection(self, analytics_system, mock_therapeutic_systems, mock_integration_systems, mock_personalization_engine):
        """Test system dependency injection."""
        analytics_system.inject_therapeutic_systems(**mock_therapeutic_systems)
        analytics_system.inject_integration_systems(**mock_integration_systems)
        analytics_system.inject_personalization_engine(mock_personalization_engine)

        # Should have all systems injected
        assert len(analytics_system.therapeutic_systems) == 9
        assert analytics_system.clinical_dashboard_manager is not None
        assert analytics_system.cloud_deployment_manager is not None
        assert analytics_system.clinical_validation_manager is not None
        assert analytics_system.personalization_engine is not None

    @pytest.mark.asyncio
    async def test_analyze_therapeutic_patterns(self, analytics_system, sample_interaction_data):
        """Test therapeutic pattern analysis."""
        user_id = "test_user_001"

        # Add interaction history
        for interaction in sample_interaction_data:
            await analytics_system.record_user_interaction(user_id, interaction)

        # Analyze patterns
        patterns = await analytics_system.analyze_therapeutic_patterns(
            user_id=user_id,
            analysis_timeframe=AnalyticsTimeframe.MEDIUM_TERM
        )

        # Should identify patterns
        assert isinstance(patterns, list)
        assert len(patterns) > 0

        # Should have valid pattern structure
        for pattern in patterns:
            assert isinstance(pattern, TherapeuticPattern)
            assert pattern.pattern_type != ""
            assert pattern.pattern_name != ""
            assert pattern.frequency > 0.0
            assert pattern.strength >= 0.0
            assert pattern.significance >= 0.0
            assert len(pattern.data_points) > 0

        # Should store patterns
        assert len(analytics_system.therapeutic_patterns) >= len(patterns)
        assert analytics_system.analytics_metrics["total_patterns_identified"] >= len(patterns)

    @pytest.mark.asyncio
    async def test_generate_therapeutic_predictions(self, analytics_system, sample_interaction_data):
        """Test therapeutic prediction generation."""
        user_id = "test_user_002"

        # Add interaction history
        for interaction in sample_interaction_data:
            await analytics_system.record_user_interaction(user_id, interaction)

        # Generate predictions
        predictions = await analytics_system.generate_therapeutic_predictions(
            user_id=user_id,
            prediction_types=[
                PredictionType.CRISIS_RISK,
                PredictionType.USER_ENGAGEMENT,
                PredictionType.THERAPEUTIC_OUTCOME
            ],
            timeframe=AnalyticsTimeframe.SHORT_TERM
        )

        # Should generate predictions
        assert isinstance(predictions, list)
        assert len(predictions) > 0

        # Should have valid prediction structure
        for prediction in predictions:
            assert isinstance(prediction, TherapeuticPrediction)
            assert prediction.user_id == user_id
            assert prediction.prediction_type in [
                PredictionType.CRISIS_RISK,
                PredictionType.USER_ENGAGEMENT,
                PredictionType.THERAPEUTIC_OUTCOME
            ]
            assert prediction.predicted_value >= 0.0 and prediction.predicted_value <= 1.0
            assert prediction.confidence_score >= 0.0 and prediction.confidence_score <= 1.0
            assert prediction.predicted_category != ""

        # Should store predictions
        assert user_id in analytics_system.active_predictions
        assert len(analytics_system.active_predictions[user_id]) >= len(predictions)
        assert analytics_system.analytics_metrics["total_predictions_generated"] >= len(predictions)

    @pytest.mark.asyncio
    async def test_predict_crisis_risk(self, analytics_system, sample_interaction_data):
        """Test crisis risk prediction."""
        user_id = "test_user_003"

        # Add interaction history with crisis indicators
        crisis_data = sample_interaction_data.copy()
        for i, interaction in enumerate(crisis_data):
            # Simulate escalating crisis risk
            interaction["crisis_indicators"]["risk_score"] = 0.1 + (i * 0.05)
            interaction["engagement_score"] = max(0.1, 0.8 - (i * 0.04))
            interaction["emotional_distress"] = min(0.9, 0.2 + (i * 0.04))

        for interaction in crisis_data:
            await analytics_system.record_user_interaction(user_id, interaction)

        # Predict crisis risk
        prediction = await analytics_system.predict_crisis_risk(
            user_id=user_id,
            timeframe=AnalyticsTimeframe.IMMEDIATE
        )

        # Should generate crisis prediction
        assert isinstance(prediction, TherapeuticPrediction)
        assert prediction.prediction_type == PredictionType.CRISIS_RISK
        assert prediction.user_id == user_id
        assert prediction.predicted_value >= 0.0
        assert prediction.confidence_score > 0.0

        # Should have risk factors and recommendations
        assert len(prediction.risk_factors) > 0
        if prediction.predicted_value > 0.4:
            assert len(prediction.recommended_interventions) > 0
            assert len(prediction.preventive_actions) > 0

    @pytest.mark.asyncio
    async def test_optimize_therapeutic_interventions(self, analytics_system, mock_therapeutic_systems, sample_interaction_data):
        """Test therapeutic intervention optimization."""
        user_id = "test_user_004"

        # Inject therapeutic systems
        analytics_system.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Add interaction history with intervention data
        for interaction in sample_interaction_data:
            await analytics_system.record_user_interaction(user_id, interaction)

        # Optimize interventions
        optimizations = await analytics_system.optimize_therapeutic_interventions(
            user_id=user_id,
            target_systems=["consequence_system", "emotional_safety_system"]
        )

        # Should generate optimizations
        assert isinstance(optimizations, list)
        assert len(optimizations) > 0

        # Should have valid optimization structure
        for optimization in optimizations:
            assert isinstance(optimization, InterventionOptimization)
            assert optimization.user_id == user_id
            assert optimization.target_system in ["consequence_system", "emotional_safety_system"]
            assert optimization.current_effectiveness >= 0.0
            assert optimization.predicted_effectiveness >= 0.0
            assert optimization.improvement_potential >= 0.0
            assert optimization.optimization_rationale != ""

        # Should store optimizations
        assert user_id in analytics_system.intervention_optimizations
        assert len(analytics_system.intervention_optimizations[user_id]) >= len(optimizations)
        assert analytics_system.analytics_metrics["total_optimizations_created"] >= len(optimizations)

    @pytest.mark.asyncio
    async def test_record_user_interaction(self, analytics_system):
        """Test user interaction recording."""
        user_id = "test_user_005"

        interaction_data = {
            "system_name": "consequence_system",
            "engagement_score": 0.8,
            "satisfaction_score": 0.7,
            "therapeutic_response": 0.9
        }

        # Record interaction
        await analytics_system.record_user_interaction(user_id, interaction_data)

        # Should store interaction
        assert user_id in analytics_system.user_interaction_history
        assert len(analytics_system.user_interaction_history[user_id]) == 1

        stored_interaction = analytics_system.user_interaction_history[user_id][0]
        assert stored_interaction["system_name"] == "consequence_system"
        assert stored_interaction["engagement_score"] == 0.8
        assert "timestamp" in stored_interaction

    @pytest.mark.asyncio
    async def test_record_therapeutic_outcome(self, analytics_system):
        """Test therapeutic outcome recording."""
        user_id = "test_user_006"

        outcome_data = {
            "outcome_score": 0.85,
            "therapeutic_progress": 0.7,
            "symptom_improvement": 0.6
        }

        # Record outcome
        await analytics_system.record_therapeutic_outcome(user_id, outcome_data)

        # Should store outcome
        assert user_id in analytics_system.therapeutic_outcome_history
        assert len(analytics_system.therapeutic_outcome_history[user_id]) == 1

        stored_outcome = analytics_system.therapeutic_outcome_history[user_id][0]
        assert stored_outcome["outcome_score"] == 0.85
        assert "timestamp" in stored_outcome

    @pytest.mark.asyncio
    async def test_record_crisis_event(self, analytics_system):
        """Test crisis event recording."""
        user_id = "test_user_007"

        crisis_data = {
            "crisis_type": "anxiety_spike",
            "severity": 0.8,
            "intervention_applied": True,
            "resolution_time": 300
        }

        # Record crisis event
        await analytics_system.record_crisis_event(user_id, crisis_data)

        # Should store crisis event
        assert user_id in analytics_system.crisis_event_history
        assert len(analytics_system.crisis_event_history[user_id]) == 1

        stored_crisis = analytics_system.crisis_event_history[user_id][0]
        assert stored_crisis["crisis_type"] == "anxiety_spike"
        assert stored_crisis["severity"] == 0.8
        assert "timestamp" in stored_crisis

    @pytest.mark.asyncio
    async def test_get_predictive_insights(self, analytics_system, sample_interaction_data):
        """Test predictive insights generation."""
        user_id = "test_user_008"

        # Add comprehensive data
        for interaction in sample_interaction_data:
            await analytics_system.record_user_interaction(user_id, interaction)

        # Add some outcomes
        for i in range(3):
            await analytics_system.record_therapeutic_outcome(user_id, {
                "outcome_score": 0.7 + (i * 0.1),
                "therapeutic_progress": 0.6 + (i * 0.1)
            })

        # Analyze patterns and generate predictions
        await analytics_system.analyze_therapeutic_patterns(user_id)
        await analytics_system.generate_therapeutic_predictions(user_id)
        await analytics_system.optimize_therapeutic_interventions(user_id)

        # Get insights
        insights = await analytics_system.get_predictive_insights(user_id)

        # Should return comprehensive insights
        assert "user_id" in insights
        assert "analysis_timestamp" in insights
        assert "pattern_analysis" in insights
        assert "prediction_summary" in insights
        assert "optimization_summary" in insights
        assert "interaction_analysis" in insights
        assert "recommendations" in insights

        # Validate pattern analysis
        pattern_analysis = insights["pattern_analysis"]
        assert "total_patterns_identified" in pattern_analysis
        assert "pattern_types" in pattern_analysis

        # Validate prediction summary
        prediction_summary = insights["prediction_summary"]
        assert "total_active_predictions" in prediction_summary
        assert "prediction_types" in prediction_summary
        assert "crisis_risk_level" in prediction_summary

        # Validate optimization summary
        optimization_summary = insights["optimization_summary"]
        assert "total_optimizations" in optimization_summary
        assert "average_improvement_potential" in optimization_summary

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, analytics_system, sample_interaction_data):
        """Test performance benchmarks for predictive analytics."""
        import time

        user_id = "performance_test_user"

        # Add interaction history
        for interaction in sample_interaction_data:
            await analytics_system.record_user_interaction(user_id, interaction)

        # Test pattern analysis performance
        start_time = time.perf_counter()

        await analytics_system.analyze_therapeutic_patterns(user_id)

        pattern_time = (time.perf_counter() - start_time) * 1000
        assert pattern_time < 500.0  # Should be under 500ms

        # Test prediction generation performance
        start_time = time.perf_counter()

        await analytics_system.generate_therapeutic_predictions(user_id)

        prediction_time = (time.perf_counter() - start_time) * 1000
        assert prediction_time < 500.0  # Should be under 500ms

        # Test crisis prediction performance
        start_time = time.perf_counter()

        await analytics_system.predict_crisis_risk(user_id)

        crisis_time = (time.perf_counter() - start_time) * 1000
        assert crisis_time < 200.0  # Should be under 200ms

        # Test insights generation performance
        start_time = time.perf_counter()

        await analytics_system.get_predictive_insights(user_id)

        insights_time = (time.perf_counter() - start_time) * 1000
        assert insights_time < 300.0  # Should be under 300ms

    @pytest.mark.asyncio
    async def test_analytics_interface_compatibility(self, analytics_system, mock_therapeutic_systems, mock_integration_systems, mock_personalization_engine):
        """Test compatibility with analytics interface expectations."""
        # Inject all dependencies
        analytics_system.inject_therapeutic_systems(**mock_therapeutic_systems)
        analytics_system.inject_integration_systems(**mock_integration_systems)
        analytics_system.inject_personalization_engine(mock_personalization_engine)

        user_id = "interface_test_user"

        # Test complete analytics workflow
        interaction_data = {
            "system_name": "consequence_system",
            "engagement_score": 0.8,
            "satisfaction_score": 0.7
        }

        await analytics_system.record_user_interaction(user_id, interaction_data)

        # Test pattern analysis
        patterns = await analytics_system.analyze_therapeutic_patterns(user_id)

        # Should match expected pattern structure
        for pattern in patterns:
            assert hasattr(pattern, "pattern_id")
            assert hasattr(pattern, "pattern_type")
            assert hasattr(pattern, "frequency")
            assert hasattr(pattern, "strength")
            assert hasattr(pattern, "significance")

        # Test prediction generation
        predictions = await analytics_system.generate_therapeutic_predictions(user_id)

        # Should match expected prediction structure
        for prediction in predictions:
            assert hasattr(prediction, "prediction_id")
            assert hasattr(prediction, "prediction_type")
            assert hasattr(prediction, "predicted_value")
            assert hasattr(prediction, "confidence_score")
            assert hasattr(prediction, "recommended_interventions")

        # Test insights generation
        insights = await analytics_system.get_predictive_insights(user_id)

        # Should match expected insights structure
        assert "pattern_analysis" in insights
        assert "prediction_summary" in insights
        assert "optimization_summary" in insights

        # Test health check
        health_check = await analytics_system.health_check()

        # Should match expected health check structure
        assert "status" in health_check
        assert "analytics_status" in health_check
        assert "total_patterns_identified" in health_check
        assert "active_predictions" in health_check
        assert "analytics_metrics" in health_check
