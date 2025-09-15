"""
Tests for TherapeuticAdaptiveDifficultyEngine

This module tests the therapeutic adaptive difficulty engine implementation
including capability assessment, difficulty adaptation, and performance tracking.
"""


import pytest

from src.components.therapeutic_systems.adaptive_difficulty_engine import (
    AdaptationStrategy,
    AdjustmentTrigger,
    DifficultyLevel,
    PerformanceMetrics,
    TherapeuticAdaptiveDifficultyEngine,
)


class TestTherapeuticAdaptiveDifficultyEngine:
    """Test TherapeuticAdaptiveDifficultyEngine functionality."""

    @pytest.fixture
    def difficulty_engine(self):
        """Create therapeutic adaptive difficulty engine instance."""
        return TherapeuticAdaptiveDifficultyEngine()

    @pytest.mark.asyncio
    async def test_initialization(self, difficulty_engine):
        """Test system initialization."""
        await difficulty_engine.initialize()

        # Should have adaptation strategies configured
        assert len(difficulty_engine.adaptation_strategies) > 0
        assert AdaptationStrategy.IMMEDIATE_ADJUSTMENT in difficulty_engine.adaptation_strategies
        assert AdaptationStrategy.GRADUAL_INCREASE in difficulty_engine.adaptation_strategies

        # Should have difficulty levels available
        assert len(DifficultyLevel) == 6  # 6 difficulty levels

        # Should have performance tracking initialized
        assert isinstance(difficulty_engine.user_performance_history, dict)
        assert isinstance(difficulty_engine.difficulty_adjustments, dict)

    @pytest.mark.asyncio
    async def test_assess_user_capability_new_user(self, difficulty_engine):
        """Test capability assessment for new user."""
        await difficulty_engine.initialize()

        result = await difficulty_engine.assess_user_capability(
            user_id="test_user_001",
            session_id="test_session_001",
            therapeutic_goals=["anxiety_management", "confidence_building"]
        )

        # Should return expected structure
        assert "difficulty_level" in result
        assert "capability_score" in result
        assert "assessment_reasoning" in result
        assert "recommended_strategies" in result

        # Should have reasonable default values for new user
        assert result["capability_score"] == 0.5  # Default moderate capability
        assert result["difficulty_level"] == DifficultyLevel.MODERATE.name
        assert len(result["recommended_strategies"]) > 0

    @pytest.mark.asyncio
    async def test_assess_user_capability_with_history(self, difficulty_engine):
        """Test capability assessment with user history."""
        await difficulty_engine.initialize()

        # Simulate user history
        user_history = {
            "capability_score": 0.8,
            "therapeutic_progress": 0.3,
            "previous_sessions": 5
        }

        result = await difficulty_engine.assess_user_capability(
            user_id="test_user_002",
            session_id="test_session_002",
            therapeutic_goals=["social_skills"],
            user_history=user_history
        )

        # Should use history to inform assessment
        assert result["capability_score"] > 0.5  # Should be higher than default
        assert result["difficulty_level"] in [DifficultyLevel.CHALLENGING.name, DifficultyLevel.HARD.name]

    @pytest.mark.asyncio
    async def test_adapt_difficulty_no_adjustment_needed(self, difficulty_engine):
        """Test difficulty adaptation when no adjustment is needed."""
        await difficulty_engine.initialize()

        # Stable performance data
        performance_data = {
            "success_rate": 0.6,
            "response_time": 25.0,
            "engagement_level": 0.7,
            "emotional_stability": 0.8,
            "therapeutic_progress": 0.4
        }

        result = await difficulty_engine.adapt_difficulty(
            user_id="test_user_003",
            performance_data=performance_data
        )

        # Should not make adjustment
        assert result["adjustment_made"] is False
        assert result["new_difficulty_level"] == DifficultyLevel.MODERATE.name
        assert "no adjustment needed" in result["adaptation_reason"].lower()

    @pytest.mark.asyncio
    async def test_adapt_difficulty_poor_performance(self, difficulty_engine):
        """Test difficulty adaptation for poor performance."""
        await difficulty_engine.initialize()

        # Poor performance data
        performance_data = {
            "success_rate": 0.2,  # Very low success rate
            "response_time": 45.0,
            "engagement_level": 0.4,
            "emotional_stability": 0.6,
            "therapeutic_progress": 0.1
        }

        result = await difficulty_engine.adapt_difficulty(
            user_id="test_user_004",
            performance_data=performance_data
        )

        # Should make adjustment to decrease difficulty
        assert result["adjustment_made"] is True
        assert result["trigger"] == AdjustmentTrigger.POOR_PERFORMANCE.value
        assert result["strategy_applied"] == AdaptationStrategy.GRADUAL_DECREASE.value

        # New difficulty should be lower
        new_difficulty = DifficultyLevel[result["new_difficulty_level"]]
        assert new_difficulty < DifficultyLevel.MODERATE

    @pytest.mark.asyncio
    async def test_adapt_difficulty_excellent_performance(self, difficulty_engine):
        """Test difficulty adaptation for excellent performance."""
        await difficulty_engine.initialize()

        # Excellent performance data
        performance_data = {
            "success_rate": 0.9,  # Very high success rate
            "response_time": 15.0,
            "engagement_level": 0.8,
            "emotional_stability": 0.9,
            "therapeutic_progress": 0.7
        }

        result = await difficulty_engine.adapt_difficulty(
            user_id="test_user_005",
            performance_data=performance_data
        )

        # Should make adjustment to increase difficulty
        assert result["adjustment_made"] is True
        assert result["trigger"] == AdjustmentTrigger.EXCELLENT_PERFORMANCE.value
        assert result["strategy_applied"] == AdaptationStrategy.GRADUAL_INCREASE.value

        # New difficulty should be higher
        new_difficulty = DifficultyLevel[result["new_difficulty_level"]]
        assert new_difficulty > DifficultyLevel.MODERATE

    @pytest.mark.asyncio
    async def test_adapt_difficulty_emotional_distress(self, difficulty_engine):
        """Test difficulty adaptation for emotional distress."""
        await difficulty_engine.initialize()

        # Performance data with emotional state
        performance_data = {
            "success_rate": 0.5,
            "response_time": 30.0,
            "engagement_level": 0.6,
            "emotional_stability": 0.3,  # Low emotional stability
            "therapeutic_progress": 0.3
        }

        # Emotional state indicating crisis
        emotional_state = {
            "crisis_detected": True,
            "crisis_level": "HIGH",
            "immediate_intervention": True
        }

        result = await difficulty_engine.adapt_difficulty(
            user_id="test_user_006",
            performance_data=performance_data,
            emotional_state=emotional_state
        )

        # Should make immediate adjustment for emotional distress
        assert result["adjustment_made"] is True
        assert result["trigger"] == AdjustmentTrigger.EMOTIONAL_DISTRESS.value
        assert result["strategy_applied"] == AdaptationStrategy.IMMEDIATE_ADJUSTMENT.value

    @pytest.mark.asyncio
    async def test_adapt_difficulty_engagement_decline(self, difficulty_engine):
        """Test difficulty adaptation for declining engagement."""
        await difficulty_engine.initialize()

        # Performance data with low engagement
        performance_data = {
            "success_rate": 0.5,
            "response_time": 30.0,
            "engagement_level": 0.3,  # Very low engagement
            "emotional_stability": 0.7,
            "therapeutic_progress": 0.4
        }

        result = await difficulty_engine.adapt_difficulty(
            user_id="test_user_007",
            performance_data=performance_data
        )

        # Should use alternative path strategy for engagement issues
        assert result["adjustment_made"] is True
        assert result["trigger"] == AdjustmentTrigger.ENGAGEMENT_DECLINE.value
        assert result["strategy_applied"] == AdaptationStrategy.ALTERNATIVE_PATH.value

    @pytest.mark.asyncio
    async def test_get_difficulty_calibration(self, difficulty_engine):
        """Test getting difficulty calibration information."""
        await difficulty_engine.initialize()

        # First assess capability to set initial difficulty
        await difficulty_engine.assess_user_capability(
            user_id="test_user_008",
            session_id="test_session_008"
        )

        result = await difficulty_engine.get_difficulty_calibration(
            user_id="test_user_008"
        )

        # Should return calibration information
        assert result["difficulty_calibrated"] is True
        assert "current_difficulty" in result
        assert "calibration_confidence" in result
        assert result["current_difficulty"] == DifficultyLevel.MODERATE.name
        assert 0.0 <= result["calibration_confidence"] <= 1.0

    def test_calculate_baseline_capability_no_history(self, difficulty_engine):
        """Test baseline capability calculation with no history."""
        capability = difficulty_engine._calculate_baseline_capability("new_user", [], None)
        assert capability == 0.5  # Default moderate capability

    def test_calculate_baseline_capability_with_history(self, difficulty_engine):
        """Test baseline capability calculation with user history."""
        user_history = {
            "capability_score": 0.7,
            "therapeutic_progress": 0.2
        }

        capability = difficulty_engine._calculate_baseline_capability("user_with_history", [], user_history)
        assert capability > 0.5  # Should be higher than default
        assert capability <= 1.0

    def test_map_capability_to_difficulty(self, difficulty_engine):
        """Test mapping capability scores to difficulty levels."""
        # Test all difficulty level mappings
        assert difficulty_engine._map_capability_to_difficulty(0.95) == DifficultyLevel.VERY_HARD
        assert difficulty_engine._map_capability_to_difficulty(0.8) == DifficultyLevel.HARD
        assert difficulty_engine._map_capability_to_difficulty(0.65) == DifficultyLevel.CHALLENGING
        assert difficulty_engine._map_capability_to_difficulty(0.5) == DifficultyLevel.MODERATE
        assert difficulty_engine._map_capability_to_difficulty(0.3) == DifficultyLevel.EASY
        assert difficulty_engine._map_capability_to_difficulty(0.1) == DifficultyLevel.VERY_EASY

    def test_recommend_strategies(self, difficulty_engine):
        """Test strategy recommendations based on capability."""
        # Low capability should recommend supportive strategies
        low_strategies = difficulty_engine._recommend_strategies(0.2)
        assert "gradual_decrease" in low_strategies
        assert "contextual_support" in low_strategies

        # High capability should recommend challenging strategies
        high_strategies = difficulty_engine._recommend_strategies(0.9)
        assert "gradual_increase" in high_strategies
        assert "alternative_path" in high_strategies

    def test_determine_adjustment_trigger(self, difficulty_engine):
        """Test adjustment trigger determination."""
        metrics = PerformanceMetrics("test_user", "test_session")

        # Test emotional distress trigger (highest priority)
        emotional_state = {"crisis_detected": True}
        trigger = difficulty_engine._determine_adjustment_trigger(metrics, "stable", emotional_state)
        assert trigger == AdjustmentTrigger.EMOTIONAL_DISTRESS

        # Test poor performance trigger
        metrics.success_rate = 0.2
        trigger = difficulty_engine._determine_adjustment_trigger(metrics, "stable", None)
        assert trigger == AdjustmentTrigger.POOR_PERFORMANCE

        # Test excellent performance trigger
        metrics.success_rate = 0.9
        metrics.engagement_level = 0.8
        trigger = difficulty_engine._determine_adjustment_trigger(metrics, "stable", None)
        assert trigger == AdjustmentTrigger.EXCELLENT_PERFORMANCE

    def test_select_adaptation_strategy(self, difficulty_engine):
        """Test adaptation strategy selection."""
        metrics = PerformanceMetrics("test_user", "test_session")

        # Test emotional distress strategy
        strategy = difficulty_engine._select_adaptation_strategy(
            metrics, AdjustmentTrigger.EMOTIONAL_DISTRESS, None
        )
        assert strategy == AdaptationStrategy.IMMEDIATE_ADJUSTMENT

        # Test poor performance strategy
        metrics.emotional_stability = 0.6
        strategy = difficulty_engine._select_adaptation_strategy(
            metrics, AdjustmentTrigger.POOR_PERFORMANCE, None
        )
        assert strategy == AdaptationStrategy.GRADUAL_DECREASE

    def test_calculate_new_difficulty(self, difficulty_engine):
        """Test new difficulty calculation."""
        metrics = PerformanceMetrics("test_user", "test_session")

        # Test gradual increase
        new_difficulty = difficulty_engine._calculate_new_difficulty(
            DifficultyLevel.MODERATE, AdaptationStrategy.GRADUAL_INCREASE, metrics
        )
        assert new_difficulty > DifficultyLevel.MODERATE

        # Test gradual decrease
        new_difficulty = difficulty_engine._calculate_new_difficulty(
            DifficultyLevel.MODERATE, AdaptationStrategy.GRADUAL_DECREASE, metrics
        )
        assert new_difficulty < DifficultyLevel.MODERATE

        # Test contextual support (no change)
        new_difficulty = difficulty_engine._calculate_new_difficulty(
            DifficultyLevel.MODERATE, AdaptationStrategy.CONTEXTUAL_SUPPORT, metrics
        )
        assert new_difficulty == DifficultyLevel.MODERATE

    @pytest.mark.asyncio
    async def test_health_check(self, difficulty_engine):
        """Test system health check."""
        await difficulty_engine.initialize()

        health = await difficulty_engine.health_check()

        assert "status" in health
        assert health["status"] == "healthy"
        assert "difficulty_levels_configured" in health
        assert health["difficulty_levels_configured"] == 6
        assert "adaptation_strategies_available" in health
        assert health["adaptation_strategies_available"] > 0

    def test_get_metrics(self, difficulty_engine):
        """Test metrics collection."""
        metrics = difficulty_engine.get_metrics()

        assert isinstance(metrics, dict)
        assert "assessments_performed" in metrics
        assert "difficulty_adjustments" in metrics
        assert "adjustment_success_rate" in metrics
        assert "users_tracked" in metrics
        assert "difficulty_levels_available" in metrics
        assert metrics["difficulty_levels_available"] == 6

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(self, difficulty_engine):
        """Test compatibility with E2E test interface expectations."""
        await difficulty_engine.initialize()

        # Test assess_user_capability method (E2E interface)
        capability_result = await difficulty_engine.assess_user_capability(
            user_id="demo_user_001",
            session_id="demo_session_001"
        )

        # Should match E2E test expected structure
        expected_keys = ["difficulty_level", "capability_score"]
        for key in expected_keys:
            assert key in capability_result

        # Test adapt_difficulty method (E2E interface)
        performance_data = {
            "success_rate": 0.7,
            "response_time": 2.5,
            "engagement_level": 0.8,
        }

        adaptation_result = await difficulty_engine.adapt_difficulty(
            user_id="demo_user_001",
            performance_data=performance_data
        )

        # Should match E2E test expected structure
        expected_keys = ["new_difficulty_level", "adaptation_reason"]
        for key in expected_keys:
            assert key in adaptation_result

    @pytest.mark.asyncio
    async def test_error_handling(self, difficulty_engine):
        """Test error handling in difficulty assessment and adaptation."""
        await difficulty_engine.initialize()

        # Test with invalid input
        result = await difficulty_engine.assess_user_capability(
            user_id="",  # Empty user ID
            session_id=None
        )

        # Should handle gracefully and return valid structure
        assert "difficulty_level" in result
        assert "capability_score" in result
        assert result["difficulty_level"] == DifficultyLevel.MODERATE.name
        assert result["capability_score"] == 0.5
