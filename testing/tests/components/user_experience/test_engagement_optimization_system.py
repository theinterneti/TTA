"""
Tests for Engagement Optimization System

This module tests the comprehensive engagement system including therapeutic
gamification, motivation tracking, achievement systems, progress visualization,
and user journey optimization.
"""

from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from src.components.user_experience.engagement_optimization_system import (
    EngagementLevel,
    EngagementMetrics,
    EngagementOptimizationSystem,
    MotivationProfile,
    ProgressVisualization,
    UserAchievement,
    VisualizationType,
)


class TestEngagementOptimizationSystem:
    """Test Engagement Optimization System functionality."""

    @pytest_asyncio.fixture
    async def engagement_system(self):
        """Create test engagement system instance."""
        system = EngagementOptimizationSystem()
        await system.initialize()
        yield system
        await system.shutdown()

    @pytest.fixture
    def mock_accessibility_system(self):
        """Create mock accessibility system."""
        system = AsyncMock()
        system.accessibility_profiles = {
            "test_user_001": Mock(
                disability_types=["visual"],
                enabled_features={"screen_reader", "high_contrast"},
                font_size_multiplier=1.2,
            )
        }
        return system

    @pytest.fixture
    def mock_ui_engine(self):
        """Create mock UI engine."""
        engine = AsyncMock()
        engine.interface_configurations = {}
        engine.interface_layouts = {}
        return engine

    @pytest.fixture
    def mock_personalization_engine(self):
        """Create mock personalization engine."""
        engine = AsyncMock()

        # Mock user profile
        mock_profile = Mock()
        mock_profile.therapeutic_preferences = {
            "focus_areas": ["anxiety", "depression"],
            "approaches": ["cbt", "mindfulness"],
        }
        mock_profile.engagement_metrics = {
            "session_frequency": 0.8,
            "completion_rate": 0.75,
        }
        mock_profile.learning_characteristics = {
            "learning_style": "visual",
            "preferred_pace": "moderate",
        }

        engine.get_user_profile.return_value = mock_profile
        return engine

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
            "error_recovery_manager",
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}
            systems[system_name] = mock_system

        return systems

    @pytest.fixture
    def sample_therapeutic_goals(self):
        """Create sample therapeutic goals."""
        return [
            "anxiety_management",
            "depression_recovery",
            "stress_reduction",
            "mindfulness_practice",
        ]

    @pytest.fixture
    def sample_user_preferences(self):
        """Create sample user preferences."""
        return {
            "intrinsic_motivation": True,
            "social_motivation": False,
            "achievement_motivation": True,
            "progress_tracking": True,
            "achievements": True,
            "points": False,
            "social_features": False,
            "session_length": 25,
            "challenge_level": 3,
            "social_preference": 0.3,
        }

    @pytest.mark.asyncio
    async def test_initialization(self, engagement_system):
        """Test engagement system initialization."""
        assert engagement_system.status == "running"
        assert (
            len(engagement_system.achievement_definitions) == 6
        )  # 6 predefined achievements
        assert (
            len(engagement_system.gamification_rules) == 4
        )  # 4 gamification rule categories
        assert len(engagement_system.motivation_strategies) == 5  # 5 motivation types
        assert (
            len(engagement_system.visualization_templates) == 8
        )  # 8 visualization types
        assert (
            len(engagement_system.progress_tracking_systems) == 4
        )  # 4 tracking systems

        # Should have background tasks running
        assert engagement_system._engagement_monitoring_task is not None
        assert engagement_system._motivation_optimization_task is not None
        assert engagement_system._achievement_processing_task is not None
        assert engagement_system._progress_analysis_task is not None

    @pytest.mark.asyncio
    async def test_system_dependency_injection(
        self,
        engagement_system,
        mock_accessibility_system,
        mock_ui_engine,
        mock_personalization_engine,
        mock_therapeutic_systems,
    ):
        """Test system dependency injection."""
        engagement_system.inject_accessibility_system(mock_accessibility_system)
        engagement_system.inject_ui_engine(mock_ui_engine)
        engagement_system.inject_personalization_engine(mock_personalization_engine)
        engagement_system.inject_therapeutic_systems(**mock_therapeutic_systems)
        engagement_system.inject_integration_systems(
            clinical_dashboard_manager=AsyncMock(), cloud_deployment_manager=AsyncMock()
        )

        # Should have all systems injected
        assert engagement_system.accessibility_system is not None
        assert engagement_system.ui_engine is not None
        assert engagement_system.personalization_engine is not None
        assert len(engagement_system.therapeutic_systems) == 9
        assert engagement_system.clinical_dashboard_manager is not None
        assert engagement_system.cloud_deployment_manager is not None

    @pytest.mark.asyncio
    async def test_create_motivation_profile(
        self,
        engagement_system,
        mock_personalization_engine,
        sample_therapeutic_goals,
        sample_user_preferences,
    ):
        """Test motivation profile creation."""
        # Inject dependencies
        engagement_system.inject_personalization_engine(mock_personalization_engine)

        user_id = "motivation_user_001"

        profile = await engagement_system.create_motivation_profile(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals,
            preferences=sample_user_preferences,
        )

        # Should create valid profile
        assert isinstance(profile, MotivationProfile)
        assert profile.user_id == user_id
        assert profile.therapeutic_goals == sample_therapeutic_goals
        assert len(profile.primary_motivation_types) > 0
        assert len(profile.preferred_gamification_elements) > 0
        assert profile.optimal_session_length == 25
        assert profile.preferred_challenge_level == 3
        assert profile.social_engagement_preference == 0.3

        # Should include expected motivation types
        motivation_type_values = [mt.value for mt in profile.primary_motivation_types]
        assert "intrinsic" in motivation_type_values
        assert "mastery" in motivation_type_values

        # Should include expected gamification elements
        gamification_element_values = [
            ge.value for ge in profile.preferred_gamification_elements
        ]
        assert "progress_bars" in gamification_element_values
        assert "achievements" in gamification_element_values

        # Should store profile
        assert user_id in engagement_system.motivation_profiles
        assert engagement_system.engagement_system_metrics["total_active_users"] == 1

    @pytest.mark.asyncio
    async def test_track_user_engagement(
        self, engagement_system, sample_therapeutic_goals
    ):
        """Test user engagement tracking."""
        user_id = "engagement_user_001"

        # Create motivation profile first
        await engagement_system.create_motivation_profile(
            user_id=user_id, therapeutic_goals=sample_therapeutic_goals, preferences={}
        )

        # Test engagement tracking
        session_data = {
            "duration": 30,
            "completion_rate": 0.85,
            "points_earned": 150,
            "challenges_completed": 2,
            "interaction_depth": 0.7,
            "exploration_rate": 0.6,
        }

        therapeutic_context = {
            "progress": 0.65,
            "goal_achievement_rate": 0.4,
            "therapeutic_session": "cbt_anxiety",
        }

        metrics = await engagement_system.track_user_engagement(
            user_id=user_id,
            session_data=session_data,
            therapeutic_context=therapeutic_context,
        )

        # Should create valid metrics
        assert isinstance(metrics, EngagementMetrics)
        assert metrics.user_id == user_id
        assert metrics.session_duration == 30
        assert metrics.completion_rate == 0.85
        assert metrics.points_earned == 150
        assert metrics.challenges_completed == 2
        assert metrics.therapeutic_progress == 0.65
        assert metrics.goal_achievement_rate == 0.4
        assert metrics.interaction_depth == 0.7
        assert metrics.exploration_rate == 0.6

        # Should store metrics
        assert user_id in engagement_system.engagement_metrics

    @pytest.mark.asyncio
    async def test_process_achievement_unlock(
        self, engagement_system, sample_therapeutic_goals
    ):
        """Test achievement processing and unlocking."""
        user_id = "achievement_user_001"

        # Create motivation profile first
        await engagement_system.create_motivation_profile(
            user_id=user_id, therapeutic_goals=sample_therapeutic_goals, preferences={}
        )

        # Test achievement unlock for first session
        achievement_criteria = {"sessions_completed": 1, "goal_progress_percentage": 25}

        session_context = {
            "session_id": "session_001",
            "therapeutic_context": {"framework": "cbt", "focus_area": "anxiety"},
        }

        unlocked_achievements = await engagement_system.process_achievement_unlock(
            user_id=user_id,
            achievement_criteria=achievement_criteria,
            session_context=session_context,
        )

        # Should unlock achievements
        assert len(unlocked_achievements) > 0

        # Check first achievement (First Steps)
        first_achievement = unlocked_achievements[0]
        assert isinstance(first_achievement, UserAchievement)
        assert first_achievement.user_id == user_id
        assert first_achievement.points_earned > 0
        assert first_achievement.session_id == "session_001"

        # Should store user achievements
        assert user_id in engagement_system.user_achievements
        assert len(engagement_system.user_achievements[user_id]) > 0

        # Should update system metrics
        assert (
            engagement_system.engagement_system_metrics["total_achievements_earned"] > 0
        )

    @pytest.mark.asyncio
    async def test_generate_progress_visualization(
        self, engagement_system, mock_accessibility_system, sample_therapeutic_goals
    ):
        """Test progress visualization generation."""
        # Inject dependencies
        engagement_system.inject_accessibility_system(mock_accessibility_system)

        user_id = "visualization_user_001"

        # Create motivation profile first
        await engagement_system.create_motivation_profile(
            user_id=user_id, therapeutic_goals=sample_therapeutic_goals, preferences={}
        )

        # Test visualization generation
        therapeutic_context = {
            "current_goals": sample_therapeutic_goals,
            "progress_data": {"anxiety_management": 0.6, "stress_reduction": 0.4},
            "session_history": ["session_001", "session_002"],
        }

        visualization = await engagement_system.generate_progress_visualization(
            user_id=user_id,
            visualization_type=VisualizationType.LINEAR_PROGRESS,
            therapeutic_context=therapeutic_context,
        )

        # Should create valid visualization
        assert isinstance(visualization, ProgressVisualization)
        assert visualization.user_id == user_id
        assert visualization.visualization_type == VisualizationType.LINEAR_PROGRESS
        assert visualization.title == "Linear Progress Tracker"
        assert visualization.description == "Track your progress along a linear path"
        assert len(visualization.data_sources) > 0
        assert visualization.therapeutic_goals == sample_therapeutic_goals

        # Should store visualization
        assert user_id in engagement_system.progress_visualizations
        assert len(engagement_system.progress_visualizations[user_id]) == 1

        # Should update usage metrics
        assert (
            engagement_system.engagement_system_metrics["progress_visualization_usage"]
            == 1
        )

    @pytest.mark.asyncio
    async def test_optimize_user_motivation(
        self, engagement_system, mock_personalization_engine, sample_therapeutic_goals
    ):
        """Test user motivation optimization."""
        # Inject dependencies
        engagement_system.inject_personalization_engine(mock_personalization_engine)

        user_id = "motivation_optimization_user_001"

        # Create motivation profile first
        await engagement_system.create_motivation_profile(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals,
            preferences={"intrinsic_motivation": True, "achievement_motivation": True},
        )

        # Test motivation optimization
        therapeutic_context = {
            "therapeutic_goals": sample_therapeutic_goals,
            "current_challenges": ["low_engagement", "missed_sessions"],
            "recent_progress": 0.3,
        }

        intervention_plan = await engagement_system.optimize_user_motivation(
            user_id=user_id,
            current_engagement=EngagementLevel.LOW,
            therapeutic_context=therapeutic_context,
        )

        # Should create valid intervention plan
        assert "user_id" in intervention_plan
        assert "current_engagement" in intervention_plan
        assert "motivation_strategies" in intervention_plan
        assert "gamification_optimizations" in intervention_plan
        assert "recommended_actions" in intervention_plan
        assert "expected_impact" in intervention_plan
        assert "implementation_timeline" in intervention_plan

        assert intervention_plan["user_id"] == user_id
        assert intervention_plan["current_engagement"] == "low"
        assert isinstance(intervention_plan["motivation_strategies"], list)
        assert isinstance(intervention_plan["gamification_optimizations"], dict)
        assert isinstance(intervention_plan["recommended_actions"], list)

        # Should update system metrics
        assert (
            engagement_system.engagement_system_metrics["motivation_effectiveness"]
            > 0.0
        )

    @pytest.mark.asyncio
    async def test_get_engagement_analytics(
        self, engagement_system, mock_personalization_engine, sample_therapeutic_goals
    ):
        """Test engagement analytics generation."""
        # Inject dependencies
        engagement_system.inject_personalization_engine(mock_personalization_engine)

        user_id = "analytics_user_001"

        # Create motivation profile
        await engagement_system.create_motivation_profile(
            user_id=user_id, therapeutic_goals=sample_therapeutic_goals, preferences={}
        )

        # Track some engagement
        session_data = {
            "duration": 25,
            "completion_rate": 0.9,
            "points_earned": 200,
            "challenges_completed": 1,
        }

        therapeutic_context = {"progress": 0.7, "goal_achievement_rate": 0.5}

        await engagement_system.track_user_engagement(
            user_id=user_id,
            session_data=session_data,
            therapeutic_context=therapeutic_context,
        )

        # Process some achievements
        achievement_criteria = {"sessions_completed": 1}
        session_context = {"session_id": "analytics_session"}

        achievements = await engagement_system.process_achievement_unlock(
            user_id=user_id,
            achievement_criteria=achievement_criteria,
            session_context=session_context,
        )

        # Generate visualization
        await engagement_system.generate_progress_visualization(
            user_id=user_id,
            visualization_type=VisualizationType.CIRCULAR_PROGRESS,
            therapeutic_context=therapeutic_context,
        )

        # Get analytics
        analytics = await engagement_system.get_engagement_analytics(user_id)

        # Should return comprehensive analytics
        assert "user_id" in analytics
        assert "analysis_timestamp" in analytics
        assert "engagement_metrics" in analytics
        assert "gamification_metrics" in analytics
        assert "therapeutic_metrics" in analytics
        assert "motivation_analysis" in analytics
        assert "progress_visualizations" in analytics
        assert "recommendations" in analytics
        assert "trends" in analytics

        # Validate engagement metrics
        engagement_data = analytics["engagement_metrics"]
        assert engagement_data["session_duration"] == 25
        assert engagement_data["completion_rate"] == 0.9
        assert "engagement_level" in engagement_data

        # Validate gamification metrics
        gamification_data = analytics["gamification_metrics"]
        assert gamification_data["points_earned"] == 200
        assert gamification_data["achievements_unlocked"] == len(achievements)
        assert gamification_data["challenges_completed"] == 1

        # Validate therapeutic metrics
        therapeutic_data = analytics["therapeutic_metrics"]
        assert therapeutic_data["therapeutic_progress"] == 0.7
        assert therapeutic_data["goal_achievement_rate"] == 0.5

        # Validate other data
        assert analytics["progress_visualizations"] == 1
        assert isinstance(analytics["recommendations"], list)
        assert isinstance(analytics["trends"], dict)

    @pytest.mark.asyncio
    async def test_performance_benchmarks(
        self,
        engagement_system,
        mock_personalization_engine,
        sample_therapeutic_goals,
        sample_user_preferences,
    ):
        """Test performance benchmarks for engagement operations."""
        import time

        # Inject dependencies
        engagement_system.inject_personalization_engine(mock_personalization_engine)

        user_id = "performance_user_001"

        # Test motivation profile creation performance
        start_time = time.perf_counter()

        await engagement_system.create_motivation_profile(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals,
            preferences=sample_user_preferences,
        )

        profile_time = (time.perf_counter() - start_time) * 1000
        assert profile_time < 200.0  # Should be under 200ms

        # Test engagement tracking performance
        start_time = time.perf_counter()

        session_data = {"duration": 30, "completion_rate": 0.8, "points_earned": 100}
        therapeutic_context = {"progress": 0.6, "goal_achievement_rate": 0.4}

        await engagement_system.track_user_engagement(
            user_id=user_id,
            session_data=session_data,
            therapeutic_context=therapeutic_context,
        )

        tracking_time = (time.perf_counter() - start_time) * 1000
        assert tracking_time < 100.0  # Should be under 100ms

        # Test achievement processing performance
        start_time = time.perf_counter()

        achievement_criteria = {"sessions_completed": 1}
        session_context = {"session_id": "perf_session"}

        await engagement_system.process_achievement_unlock(
            user_id=user_id,
            achievement_criteria=achievement_criteria,
            session_context=session_context,
        )

        achievement_time = (time.perf_counter() - start_time) * 1000
        assert achievement_time < 150.0  # Should be under 150ms

        # Test visualization generation performance
        start_time = time.perf_counter()

        await engagement_system.generate_progress_visualization(
            user_id=user_id,
            visualization_type=VisualizationType.JOURNEY_MAP,
            therapeutic_context=therapeutic_context,
        )

        visualization_time = (time.perf_counter() - start_time) * 1000
        assert visualization_time < 200.0  # Should be under 200ms

        # Test motivation optimization performance
        start_time = time.perf_counter()

        await engagement_system.optimize_user_motivation(
            user_id=user_id,
            current_engagement=EngagementLevel.MODERATE,
            therapeutic_context=therapeutic_context,
        )

        optimization_time = (time.perf_counter() - start_time) * 1000
        assert optimization_time < 300.0  # Should be under 300ms

    @pytest.mark.asyncio
    async def test_engagement_system_interface_compatibility(
        self,
        engagement_system,
        mock_accessibility_system,
        mock_ui_engine,
        mock_personalization_engine,
        mock_therapeutic_systems,
        sample_therapeutic_goals,
    ):
        """Test compatibility with engagement system interface expectations."""
        # Inject all dependencies
        engagement_system.inject_accessibility_system(mock_accessibility_system)
        engagement_system.inject_ui_engine(mock_ui_engine)
        engagement_system.inject_personalization_engine(mock_personalization_engine)
        engagement_system.inject_therapeutic_systems(**mock_therapeutic_systems)
        engagement_system.inject_integration_systems(
            clinical_dashboard_manager=AsyncMock(), cloud_deployment_manager=AsyncMock()
        )

        user_id = "interface_compatibility_user"

        # Test complete engagement workflow
        profile = await engagement_system.create_motivation_profile(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals,
            preferences={"intrinsic_motivation": True},
        )

        # Should match expected profile structure
        assert hasattr(profile, "profile_id")
        assert hasattr(profile, "user_id")
        assert hasattr(profile, "primary_motivation_types")
        assert hasattr(profile, "preferred_gamification_elements")
        assert hasattr(profile, "therapeutic_goals")
        assert hasattr(profile, "optimal_session_length")

        # Test engagement tracking
        metrics = await engagement_system.track_user_engagement(
            user_id=user_id,
            session_data={"duration": 30, "completion_rate": 0.8},
            therapeutic_context={"progress": 0.6},
        )

        # Should match expected metrics structure
        assert hasattr(metrics, "metrics_id")
        assert hasattr(metrics, "user_id")
        assert hasattr(metrics, "session_frequency")
        assert hasattr(metrics, "completion_rate")
        assert hasattr(metrics, "points_earned")
        assert hasattr(metrics, "therapeutic_progress")

        # Test achievement processing
        achievements = await engagement_system.process_achievement_unlock(
            user_id=user_id,
            achievement_criteria={"sessions_completed": 1},
            session_context={"session_id": "test_session"},
        )

        # Should return list of UserAchievement objects
        assert isinstance(achievements, list)
        if achievements:
            achievement = achievements[0]
            assert hasattr(achievement, "user_achievement_id")
            assert hasattr(achievement, "user_id")
            assert hasattr(achievement, "achievement_id")
            assert hasattr(achievement, "points_earned")

        # Test health check
        health_check = await engagement_system.health_check()

        # Should match expected health check structure
        assert "status" in health_check
        assert "engagement_status" in health_check
        assert "total_active_users" in health_check
        assert "engagement_system_metrics" in health_check
        assert "system_integrations" in health_check
