"""
Tests for AdaptiveDifficultyEngine

This module tests adaptive difficulty calibration, performance monitoring,
and intelligent challenge adjustment functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from src.components.gameplay_loop.narrative.adaptive_difficulty_engine import (
    AdaptiveDifficultyEngine, PerformanceSnapshot, DifficultyAdjustment, UserPreferences,
    DifficultyLevel, PerformanceMetric, AdjustmentTrigger, AdaptationStrategy
)
from src.components.gameplay_loop.services.session_state import SessionState
from src.components.gameplay_loop.narrative.events import EventBus


class TestAdaptiveDifficultyEngine:
    """Test AdaptiveDifficultyEngine functionality."""
    
    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        bus = Mock(spec=EventBus)
        bus.publish = AsyncMock()
        return bus
    
    @pytest.fixture
    def difficulty_engine(self, event_bus):
        """Create adaptive difficulty engine instance."""
        return AdaptiveDifficultyEngine(event_bus)
    
    @pytest.fixture
    def session_state(self):
        """Create mock session state."""
        state = Mock(spec=SessionState)
        state.session_id = "test_session_123"
        state.user_id = "test_user_456"
        state.therapeutic_goals = ["anxiety_management", "communication_skills"]
        state.progress_metrics = {"anxiety_management": 0.6, "communication_skills": 0.4}
        state.context = {
            "current_difficulty": DifficultyLevel.MODERATE.value,
            "consequence_history": [
                {"therapeutic_outcomes_count": 2, "learning_opportunities_count": 1},
                {"therapeutic_outcomes_count": 1, "learning_opportunities_count": 2},
                {"therapeutic_outcomes_count": 0, "learning_opportunities_count": 1}
            ],
            "session_duration_minutes": 25,
            "choices_made": ["choice1", "choice2", "choice3"],
            "scenes_visited": ["scene1", "scene2"],
            "decision_times": [15.0, 20.0, 25.0, 18.0],
            "help_requests_count": 1
        }
        state.emotional_state = {
            "calm": 0.6,
            "anxious": 0.3,
            "hopeful": 0.7,
            "confident": 0.5
        }
        return state
    
    @pytest.fixture
    def poor_performance_state(self):
        """Create session state with poor performance indicators."""
        state = Mock(spec=SessionState)
        state.session_id = "poor_session_789"
        state.user_id = "struggling_user_101"
        state.therapeutic_goals = ["anxiety_management"]
        state.progress_metrics = {"anxiety_management": 0.2}
        state.context = {
            "current_difficulty": DifficultyLevel.CHALLENGING.value,
            "consequence_history": [
                {"therapeutic_outcomes_count": 0, "learning_opportunities_count": 0},
                {"therapeutic_outcomes_count": 0, "learning_opportunities_count": 1},
                {"therapeutic_outcomes_count": 0, "learning_opportunities_count": 0}
            ],
            "session_duration_minutes": 10,
            "choices_made": ["choice1"],
            "scenes_visited": ["scene1"],
            "decision_times": [45.0, 60.0, 90.0],
            "help_requests_count": 5
        }
        state.emotional_state = {
            "anxious": 0.8,
            "overwhelmed": 0.7,
            "frustrated": 0.6,
            "calm": 0.1
        }
        return state
    
    @pytest.fixture
    def excellent_performance_state(self):
        """Create session state with excellent performance indicators."""
        state = Mock(spec=SessionState)
        state.session_id = "excellent_session_456"
        state.user_id = "excelling_user_202"
        state.therapeutic_goals = ["communication_skills", "emotional_regulation"]
        state.progress_metrics = {"communication_skills": 0.9, "emotional_regulation": 0.8}
        state.context = {
            "current_difficulty": DifficultyLevel.EASY.value,
            "consequence_history": [
                {"therapeutic_outcomes_count": 3, "learning_opportunities_count": 2},
                {"therapeutic_outcomes_count": 2, "learning_opportunities_count": 3},
                {"therapeutic_outcomes_count": 3, "learning_opportunities_count": 2}
            ],
            "session_duration_minutes": 35,
            "choices_made": ["choice1", "choice2", "choice3", "choice4", "choice5"],
            "scenes_visited": ["scene1", "scene2", "scene3"],
            "decision_times": [8.0, 12.0, 10.0, 15.0],
            "help_requests_count": 0
        }
        state.emotional_state = {
            "confident": 0.9,
            "hopeful": 0.8,
            "calm": 0.7,
            "excited": 0.6
        }
        return state
    
    @pytest.mark.asyncio
    async def test_monitor_performance_normal(self, difficulty_engine, session_state):
        """Test performance monitoring for normal performance."""
        interaction_data = {
            "response_time": 20.0,
            "choice_complexity": 0.6,
            "therapeutic_relevance": 0.7,
            "interaction_type": "choice_made"
        }
        
        snapshot = await difficulty_engine.monitor_performance(session_state, interaction_data)
        
        # Check snapshot structure
        assert isinstance(snapshot, PerformanceSnapshot)
        assert snapshot.user_id == session_state.user_id
        assert snapshot.session_id == session_state.session_id
        
        # Check performance calculations
        assert 0.0 <= snapshot.success_rate <= 1.0
        assert 0.0 <= snapshot.therapeutic_progress <= 1.0
        assert 0.0 <= snapshot.emotional_stability <= 1.0
        assert 0.0 <= snapshot.engagement_level <= 1.0
        assert 0.0 <= snapshot.completion_rate <= 1.0
        assert snapshot.average_decision_time > 0
        
        # Check that snapshot was stored
        assert session_state.user_id in difficulty_engine.performance_history
        assert len(difficulty_engine.performance_history[session_state.user_id]) == 1
    
    @pytest.mark.asyncio
    async def test_monitor_performance_poor(self, difficulty_engine, poor_performance_state, event_bus):
        """Test performance monitoring for poor performance."""
        interaction_data = {
            "response_time": 60.0,
            "choice_complexity": 0.2,
            "therapeutic_relevance": 0.1,
            "interaction_type": "choice_made"
        }
        
        # Add multiple snapshots to trigger adjustment
        for _ in range(3):
            await difficulty_engine.monitor_performance(poor_performance_state, interaction_data)
        
        # Check that adjustment was triggered
        user_id = poor_performance_state.user_id
        assert user_id in difficulty_engine.adjustment_history
        assert len(difficulty_engine.adjustment_history[user_id]) > 0
        
        # Check that difficulty was reduced
        latest_adjustment = difficulty_engine.adjustment_history[user_id][-1]
        assert latest_adjustment.to_difficulty < latest_adjustment.from_difficulty
        
        # Check that event was published
        event_bus.publish.assert_called()
    
    @pytest.mark.asyncio
    async def test_monitor_performance_excellent(self, difficulty_engine, excellent_performance_state, event_bus):
        """Test performance monitoring for excellent performance."""
        interaction_data = {
            "response_time": 10.0,
            "choice_complexity": 0.8,
            "therapeutic_relevance": 0.9,
            "interaction_type": "choice_made"
        }
        
        # Add multiple snapshots to trigger adjustment
        for _ in range(3):
            await difficulty_engine.monitor_performance(excellent_performance_state, interaction_data)
        
        # Check that adjustment was triggered
        user_id = excellent_performance_state.user_id
        assert user_id in difficulty_engine.adjustment_history
        assert len(difficulty_engine.adjustment_history[user_id]) > 0
        
        # Check that difficulty was increased or support was provided
        latest_adjustment = difficulty_engine.adjustment_history[user_id][-1]
        assert (latest_adjustment.to_difficulty > latest_adjustment.from_difficulty or
                latest_adjustment.strategy == AdaptationStrategy.CONTEXTUAL_SUPPORT)
    
    def test_calculate_success_rate(self, difficulty_engine, session_state):
        """Test success rate calculation."""
        success_rate = difficulty_engine._calculate_success_rate(session_state)
        
        # Should be based on consequence history
        assert 0.0 <= success_rate <= 1.0
        
        # With therapeutic outcomes in history, should be > 0
        assert success_rate > 0.0
    
    def test_calculate_therapeutic_progress(self, difficulty_engine, session_state):
        """Test therapeutic progress calculation."""
        progress = difficulty_engine._calculate_therapeutic_progress(session_state)
        
        # Should be average of progress metrics
        expected_progress = (0.6 + 0.4) / 2  # From fixture
        assert abs(progress - expected_progress) < 0.01
    
    def test_calculate_emotional_stability(self, difficulty_engine, session_state):
        """Test emotional stability calculation."""
        stability = difficulty_engine._calculate_emotional_stability(session_state)
        
        # Should be based on emotional balance
        assert 0.0 <= stability <= 1.0
        
        # With more positive emotions, should be > 0.5
        assert stability > 0.5
    
    def test_calculate_engagement_level(self, difficulty_engine, session_state):
        """Test engagement level calculation."""
        interaction_data = {
            "response_time": 20.0,
            "choice_complexity": 0.6,
            "therapeutic_relevance": 0.7
        }
        
        engagement = difficulty_engine._calculate_engagement_level(session_state, interaction_data)
        
        # Should be based on multiple indicators
        assert 0.0 <= engagement <= 1.0
        
        # With good indicators, should be > 0.5
        assert engagement > 0.5
    
    def test_difficulty_parameters_loading(self, difficulty_engine):
        """Test that difficulty parameters are properly loaded."""
        params = difficulty_engine.difficulty_parameters
        
        # Check that all difficulty levels have parameters
        for level in DifficultyLevel:
            assert level in params
            
            level_params = params[level]
            assert "choice_complexity" in level_params
            assert "emotional_intensity" in level_params
            assert "therapeutic_challenge" in level_params
            assert "support_availability" in level_params
            
            # Check parameter ranges
            for param_value in level_params.values():
                assert 0.0 <= param_value <= 1.0
    
    def test_adaptation_strategies_loading(self, difficulty_engine):
        """Test that adaptation strategies are properly loaded."""
        strategies = difficulty_engine.adaptation_strategies
        
        # Check that all strategies are loaded
        for strategy in AdaptationStrategy:
            assert strategy in strategies
            
            strategy_config = strategies[strategy]
            assert "description" in strategy_config
            assert "story_integration" in strategy_config
    
    def test_determine_adjustment_trigger(self, difficulty_engine, poor_performance_state):
        """Test adjustment trigger determination."""
        # Create snapshot with poor performance
        snapshot = PerformanceSnapshot(
            user_id=poor_performance_state.user_id,
            session_id=poor_performance_state.session_id,
            success_rate=0.2,
            engagement_level=0.3,
            emotional_stability=0.4
        )
        
        trigger = difficulty_engine._determine_adjustment_trigger(poor_performance_state, snapshot)
        
        # Should identify poor performance
        assert trigger == AdjustmentTrigger.POOR_PERFORMANCE
    
    def test_select_adaptation_strategy(self, difficulty_engine, session_state):
        """Test adaptation strategy selection."""
        snapshot = PerformanceSnapshot(
            user_id=session_state.user_id,
            session_id=session_state.session_id,
            success_rate=0.2,
            emotional_stability=0.1
        )
        
        # Test emotional distress trigger
        strategy = difficulty_engine._select_adaptation_strategy(
            session_state, snapshot, AdjustmentTrigger.EMOTIONAL_DISTRESS
        )
        assert strategy == AdaptationStrategy.IMMEDIATE_ADJUSTMENT
        
        # Test poor performance trigger
        strategy = difficulty_engine._select_adaptation_strategy(
            session_state, snapshot, AdjustmentTrigger.POOR_PERFORMANCE
        )
        assert strategy in [AdaptationStrategy.IMMEDIATE_ADJUSTMENT, AdaptationStrategy.GRADUAL_DECREASE]
    
    def test_calculate_new_difficulty(self, difficulty_engine, session_state):
        """Test new difficulty calculation."""
        snapshot = PerformanceSnapshot(
            current_difficulty=DifficultyLevel.MODERATE
        )
        
        # Test gradual decrease
        new_difficulty = difficulty_engine._calculate_new_difficulty(
            session_state, snapshot, AdaptationStrategy.GRADUAL_DECREASE
        )
        assert new_difficulty < DifficultyLevel.MODERATE
        
        # Test gradual increase
        new_difficulty = difficulty_engine._calculate_new_difficulty(
            session_state, snapshot, AdaptationStrategy.GRADUAL_INCREASE
        )
        assert new_difficulty > DifficultyLevel.MODERATE
        
        # Test contextual support (no change)
        new_difficulty = difficulty_engine._calculate_new_difficulty(
            session_state, snapshot, AdaptationStrategy.CONTEXTUAL_SUPPORT
        )
        assert new_difficulty == DifficultyLevel.MODERATE
    
    @pytest.mark.asyncio
    async def test_update_user_preferences(self, difficulty_engine):
        """Test user preference updates."""
        user_id = "test_user_123"
        preferences = {
            "preferred_difficulty": 4,
            "challenge_tolerance": 0.8,
            "adaptation_speed": 0.6,
            "wants_hints": False,
            "therapeutic_focus": ["anxiety_management"]
        }
        
        await difficulty_engine.update_user_preferences(user_id, preferences)
        
        # Check that preferences were updated
        user_prefs = difficulty_engine._get_user_preferences(user_id)
        assert user_prefs.preferred_difficulty == DifficultyLevel.CHALLENGING
        assert user_prefs.challenge_tolerance == 0.8
        assert user_prefs.adaptation_speed == 0.6
        assert user_prefs.wants_hints == False
        assert "anxiety_management" in user_prefs.therapeutic_focus
    
    @pytest.mark.asyncio
    async def test_request_difficulty_adjustment(self, difficulty_engine, session_state):
        """Test manual difficulty adjustment request."""
        success = await difficulty_engine.request_difficulty_adjustment(
            session_state, 
            requested_difficulty=DifficultyLevel.EASY,
            strategy=AdaptationStrategy.IMMEDIATE_ADJUSTMENT
        )
        
        assert success == True
        
        # Check that request flags were set
        assert session_state.context["difficulty_adjustment_requested"] == True
        assert session_state.context["requested_difficulty"] == DifficultyLevel.EASY.value
        assert session_state.context["requested_strategy"] == AdaptationStrategy.IMMEDIATE_ADJUSTMENT.value
    
    def test_get_current_difficulty_info(self, difficulty_engine, session_state):
        """Test current difficulty information retrieval."""
        info = difficulty_engine.get_current_difficulty_info(session_state)
        
        # Check info structure
        assert "current_difficulty" in info
        assert "difficulty_level" in info
        assert "parameters" in info
        assert "support_available" in info
        assert "user_preferences" in info
        
        # Check values
        assert info["current_difficulty"] == "MODERATE"
        assert info["difficulty_level"] == 3
        assert isinstance(info["parameters"], dict)
    
    def test_get_performance_summary(self, difficulty_engine, session_state):
        """Test performance summary generation."""
        # Add some performance history
        user_id = session_state.user_id
        snapshots = []
        for i in range(3):
            snapshot = PerformanceSnapshot(
                user_id=user_id,
                session_id=session_state.session_id,
                success_rate=0.5 + i * 0.1,
                engagement_level=0.6 + i * 0.1,
                emotional_stability=0.7 + i * 0.05,
                therapeutic_progress=0.4 + i * 0.1,
                current_difficulty=DifficultyLevel.MODERATE,
                created_at=datetime.utcnow() - timedelta(minutes=i * 10)
            )
            snapshots.append(snapshot)
        
        difficulty_engine.performance_history[user_id] = snapshots
        
        summary = difficulty_engine.get_performance_summary(user_id)
        
        # Check summary structure
        assert "snapshots_count" in summary
        assert "success_rate" in summary
        assert "engagement_level" in summary
        assert "emotional_stability" in summary
        assert "current_difficulty" in summary
        
        # Check that trends are calculated
        assert "trend" in summary["success_rate"]
        assert "trend" in summary["engagement_level"]
        assert "trend" in summary["emotional_stability"]
    
    def test_get_adjustment_history(self, difficulty_engine, session_state):
        """Test adjustment history retrieval."""
        # Add some adjustment history
        user_id = session_state.user_id
        adjustments = []
        for i in range(2):
            adjustment = DifficultyAdjustment(
                user_id=user_id,
                session_id=session_state.session_id,
                from_difficulty=DifficultyLevel.MODERATE,
                to_difficulty=DifficultyLevel.EASY,
                trigger=AdjustmentTrigger.POOR_PERFORMANCE,
                strategy=AdaptationStrategy.GRADUAL_DECREASE,
                adjustment_reason="Test adjustment",
                created_at=datetime.utcnow() - timedelta(hours=i)
            )
            adjustments.append(adjustment)
        
        difficulty_engine.adjustment_history[user_id] = adjustments
        
        history = difficulty_engine.get_adjustment_history(user_id)
        
        # Check history structure
        assert len(history) == 2
        
        for entry in history:
            assert "adjustment_id" in entry
            assert "from_difficulty" in entry
            assert "to_difficulty" in entry
            assert "trigger" in entry
            assert "strategy" in entry
            assert "reason" in entry
            assert "created_at" in entry
    
    def test_metrics_tracking(self, difficulty_engine):
        """Test metrics tracking."""
        initial_metrics = difficulty_engine.get_metrics()
        
        # Check metric structure
        assert "performance_snapshots_created" in initial_metrics
        assert "difficulty_adjustments_made" in initial_metrics
        assert "user_preferences_updated" in initial_metrics
        assert "active_users_monitored" in initial_metrics
        
        # Initially should be zero
        assert initial_metrics["performance_snapshots_created"] == 0
        assert initial_metrics["difficulty_adjustments_made"] == 0
    
    @pytest.mark.asyncio
    async def test_health_check(self, difficulty_engine):
        """Test health check functionality."""
        health = await difficulty_engine.health_check()
        
        assert health["status"] == "healthy"
        assert "difficulty_levels_configured" in health
        assert "adaptation_strategies_available" in health
        assert "performance_window_minutes" in health
        assert "adjustment_threshold" in health
        assert "metrics" in health
        
        # Should have loaded difficulty levels and strategies
        assert health["difficulty_levels_configured"] == 6  # 6 difficulty levels
        assert health["adaptation_strategies_available"] == 6  # 6 adaptation strategies
    
    def test_trend_calculation(self, difficulty_engine):
        """Test trend calculation functionality."""
        # Test increasing trend
        increasing_values = [0.2, 0.4, 0.6, 0.8]
        trend = difficulty_engine._calculate_trend(increasing_values)
        assert trend > 0
        
        # Test decreasing trend
        decreasing_values = [0.8, 0.6, 0.4, 0.2]
        trend = difficulty_engine._calculate_trend(decreasing_values)
        assert trend < 0
        
        # Test stable trend
        stable_values = [0.5, 0.5, 0.5, 0.5]
        trend = difficulty_engine._calculate_trend(stable_values)
        assert abs(trend) < 0.1  # Should be close to 0
    
    def test_pattern_detection(self, difficulty_engine):
        """Test performance pattern detection."""
        # Create snapshots with poor performance pattern
        poor_snapshots = [
            PerformanceSnapshot(success_rate=0.3, engagement_level=0.4),
            PerformanceSnapshot(success_rate=0.2, engagement_level=0.3),
            PerformanceSnapshot(success_rate=0.1, engagement_level=0.2)
        ]
        
        pattern_detected = difficulty_engine._detect_performance_pattern(poor_snapshots)
        assert pattern_detected == True
        
        # Create snapshots with excellent performance pattern
        excellent_snapshots = [
            PerformanceSnapshot(success_rate=0.9, engagement_level=0.8),
            PerformanceSnapshot(success_rate=0.8, engagement_level=0.9),
            PerformanceSnapshot(success_rate=0.9, engagement_level=0.8)
        ]
        
        pattern_detected = difficulty_engine._detect_performance_pattern(excellent_snapshots)
        assert pattern_detected == True
        
        # Create snapshots with normal performance (no pattern)
        normal_snapshots = [
            PerformanceSnapshot(success_rate=0.5, engagement_level=0.6),
            PerformanceSnapshot(success_rate=0.6, engagement_level=0.5),
            PerformanceSnapshot(success_rate=0.5, engagement_level=0.6)
        ]
        
        pattern_detected = difficulty_engine._detect_performance_pattern(normal_snapshots)
        assert pattern_detected == False
