"""
Tests for Intelligent Personalization Engine

This module tests the AI-driven personalization engine functionality including
user profile creation, recommendation generation, adaptation application,
learning from interactions, and personalization insights.
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src.components.advanced_therapeutic_intelligence.intelligent_personalization_engine import (
    IntelligentPersonalizationEngine,
    LearningMode,
    PersonalizationDomain,
    PersonalizationLevel,
    PersonalizationRecommendation,
    UserPersonalizationProfile,
)


class TestIntelligentPersonalizationEngine:
    """Test Intelligent Personalization Engine functionality."""

    @pytest_asyncio.fixture
    async def personalization_engine(self):
        """Create test personalization engine instance."""
        engine = IntelligentPersonalizationEngine()
        await engine.initialize()
        yield engine
        await engine.shutdown()

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
            mock_system.adapt_therapeutic_approach.return_value = {"success": True, "adaptation_applied": True}
            mock_system.adapt_difficulty_settings.return_value = {"success": True, "difficulty_adjusted": True}
            mock_system.update_user_preferences.return_value = {"success": True, "preferences_updated": True}
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

    @pytest.mark.asyncio
    async def test_initialization(self, personalization_engine):
        """Test personalization engine initialization."""
        assert personalization_engine.status == "running"
        assert len(personalization_engine.user_profiles) == 0
        assert len(personalization_engine.active_recommendations) == 0
        assert len(personalization_engine.learning_models) == 5

        # Should have background tasks running
        assert personalization_engine._learning_task is not None
        assert personalization_engine._adaptation_task is not None
        assert personalization_engine._recommendation_task is not None

    @pytest.mark.asyncio
    async def test_therapeutic_system_injection(self, personalization_engine, mock_therapeutic_systems):
        """Test therapeutic system dependency injection."""
        personalization_engine.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Should have all therapeutic systems injected
        assert personalization_engine.consequence_system is not None
        assert personalization_engine.emotional_safety_system is not None
        assert personalization_engine.adaptive_difficulty_engine is not None
        assert personalization_engine.character_development_system is not None
        assert personalization_engine.therapeutic_integration_system is not None
        assert personalization_engine.gameplay_loop_controller is not None
        assert personalization_engine.replayability_system is not None
        assert personalization_engine.collaborative_system is not None
        assert personalization_engine.error_recovery_manager is not None

    @pytest.mark.asyncio
    async def test_integration_system_injection(self, personalization_engine, mock_integration_systems):
        """Test integration system dependency injection."""
        personalization_engine.inject_integration_systems(**mock_integration_systems)

        # Should have integration systems injected
        assert personalization_engine.clinical_dashboard_manager is not None
        assert personalization_engine.cloud_deployment_manager is not None
        assert personalization_engine.clinical_validation_manager is not None

    @pytest.mark.asyncio
    async def test_create_user_personalization_profile(self, personalization_engine):
        """Test user personalization profile creation."""
        user_id = "test_user_001"
        initial_preferences = {
            "therapeutic_approaches": ["CBT", "Mindfulness"],
            "interaction_style": "supportive",
            "personalization_level": "adaptive",
            "learning_mode": "active"
        }

        profile = await personalization_engine.create_user_personalization_profile(
            user_id=user_id,
            initial_preferences=initial_preferences,
            consent_level="full"
        )

        # Should create valid profile
        assert isinstance(profile, UserPersonalizationProfile)
        assert profile.user_id == user_id
        assert profile.consent_level == "full"
        assert profile.personalization_level == PersonalizationLevel.ADAPTIVE
        assert profile.learning_mode == LearningMode.ACTIVE
        assert profile.preferred_therapeutic_approaches == ["CBT", "Mindfulness"]
        assert profile.interaction_preferences["style"] == "supportive"

        # Should be stored in engine
        assert user_id in personalization_engine.user_profiles
        assert personalization_engine.personalization_metrics["total_users_profiled"] == 1

        # Should have system interactions initialized
        assert len(profile.system_interactions) == 9
        for system_name in profile.system_interactions:
            system_data = profile.system_interactions[system_name]
            assert system_data["interaction_count"] == 0
            assert system_data["positive_outcomes"] == 0
            assert system_data["negative_outcomes"] == 0

    @pytest.mark.asyncio
    async def test_generate_personalization_recommendations(self, personalization_engine):
        """Test personalization recommendation generation."""
        user_id = "test_user_002"

        # Create user profile first
        await personalization_engine.create_user_personalization_profile(user_id)

        # Add some interaction history to generate meaningful recommendations
        profile = personalization_engine.user_profiles[user_id]
        profile.system_interactions["consequence_system"]["positive_outcomes"] = 5
        profile.system_interactions["consequence_system"]["interaction_count"] = 8
        profile.system_interactions["emotional_safety_system"]["average_engagement"] = 0.4

        # Generate recommendations
        recommendations = await personalization_engine.generate_personalization_recommendations(
            user_id=user_id,
            context={"session_type": "therapeutic", "current_mood": "neutral"}
        )

        # Should generate recommendations
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Should have valid recommendation structure
        for rec in recommendations:
            assert isinstance(rec, PersonalizationRecommendation)
            assert rec.user_id == user_id
            assert rec.confidence_score > 0.0
            assert rec.expected_impact > 0.0
            assert rec.reasoning != ""
            assert rec.priority >= 1 and rec.priority <= 10

        # Should be stored in active recommendations
        assert user_id in personalization_engine.active_recommendations
        assert len(personalization_engine.active_recommendations[user_id]) == len(recommendations)

        # Should update metrics
        assert personalization_engine.personalization_metrics["total_recommendations_generated"] == len(recommendations)

    @pytest.mark.asyncio
    async def test_apply_personalization_adaptation(self, personalization_engine, mock_therapeutic_systems):
        """Test personalization adaptation application."""
        user_id = "test_user_003"

        # Inject therapeutic systems
        personalization_engine.inject_therapeutic_systems(**mock_therapeutic_systems)

        # Create user profile
        await personalization_engine.create_user_personalization_profile(user_id)

        # Create test recommendation
        recommendation = PersonalizationRecommendation(
            user_id=user_id,
            target_system="therapeutic_integration_system",
            domain=PersonalizationDomain.THERAPEUTIC_APPROACH,
            recommendation_type="prioritize_approach",
            recommendation_data={
                "preferred_system": "consequence_system",
                "confidence_boost": 0.2
            },
            confidence_score=0.8,
            expected_impact=0.15
        )

        # Apply adaptation
        result = await personalization_engine.apply_personalization_adaptation(
            user_id=user_id,
            recommendation=recommendation
        )

        # Should apply adaptation successfully
        assert result["success"] is True
        assert "result" in result

        # Should update profile adaptation history
        profile = personalization_engine.user_profiles[user_id]
        assert len(profile.adaptation_history) == 1

        adaptation_record = profile.adaptation_history[0]
        assert adaptation_record["recommendation_id"] == recommendation.recommendation_id
        assert adaptation_record["target_system"] == "therapeutic_integration_system"
        assert adaptation_record["domain"] == PersonalizationDomain.THERAPEUTIC_APPROACH.value

        # Should update recommendation status
        assert recommendation.validation_status == "applied"

        # Should update metrics
        assert personalization_engine.personalization_metrics["total_adaptations_applied"] == 1

    @pytest.mark.asyncio
    async def test_learn_from_user_interaction(self, personalization_engine):
        """Test learning from user interactions."""
        user_id = "test_user_004"

        # Create user profile
        await personalization_engine.create_user_personalization_profile(user_id)

        # Simulate user interaction
        interaction_data = {
            "engagement_score": 0.8,
            "interaction_duration": 300,
            "user_actions": 15
        }

        outcome_data = {
            "satisfaction_score": 0.9,
            "therapeutic_progress": 0.7,
            "completion_rate": 1.0
        }

        # Learn from interaction
        await personalization_engine.learn_from_user_interaction(
            user_id=user_id,
            system_name="consequence_system",
            interaction_data=interaction_data,
            outcome_data=outcome_data
        )

        # Should update profile system interactions
        profile = personalization_engine.user_profiles[user_id]
        system_data = profile.system_interactions["consequence_system"]

        assert system_data["interaction_count"] == 1
        assert system_data["positive_outcomes"] == 1  # satisfaction_score > 0.6
        assert system_data["average_engagement"] == 0.8

        # Should update learning models
        assert personalization_engine.personalization_metrics["learning_model_accuracy"] > 0.0

    @pytest.mark.asyncio
    async def test_get_personalization_insights(self, personalization_engine):
        """Test personalization insights generation."""
        user_id = "test_user_005"

        # Create user profile with some history
        await personalization_engine.create_user_personalization_profile(user_id)

        # Add interaction history
        profile = personalization_engine.user_profiles[user_id]
        profile.system_interactions["consequence_system"]["interaction_count"] = 10
        profile.system_interactions["consequence_system"]["positive_outcomes"] = 8
        profile.system_interactions["consequence_system"]["average_engagement"] = 0.85

        # Add therapeutic outcomes
        profile.therapeutic_outcomes["anxiety_reduction"] = [0.6, 0.7, 0.8, 0.9]

        # Add adaptation history
        profile.adaptation_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "recommendation_id": "test_rec_001",
            "target_system": "consequence_system",
            "domain": "therapeutic_approach",
            "result": {"success": True}
        })

        # Generate insights
        insights = await personalization_engine.get_personalization_insights(user_id)

        # Should return comprehensive insights
        assert "profile_summary" in insights
        assert "interaction_summary" in insights
        assert "therapeutic_effectiveness" in insights
        assert "personalization_accuracy" in insights
        assert "recommendations_summary" in insights
        assert "learning_progress" in insights

        # Validate profile summary
        profile_summary = insights["profile_summary"]
        assert profile_summary["user_id"] == user_id
        assert profile_summary["personalization_level"] == "adaptive"
        assert profile_summary["learning_mode"] == "active"

        # Validate interaction summary
        interaction_summary = insights["interaction_summary"]
        assert interaction_summary["total_interactions"] == 10
        assert interaction_summary["positive_outcome_rate"] == 0.8
        assert interaction_summary["average_engagement"] == 0.85
        assert interaction_summary["most_used_system"] == "consequence_system"

        # Validate therapeutic effectiveness
        effectiveness = insights["therapeutic_effectiveness"]
        assert effectiveness["effectiveness_score"] > 0.0
        assert effectiveness["total_outcomes_measured"] == 4

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, personalization_engine, mock_therapeutic_systems):
        """Test performance benchmarks for personalization engine."""
        import time

        # Inject systems
        personalization_engine.inject_therapeutic_systems(**mock_therapeutic_systems)

        user_id = "performance_test_user"

        # Test profile creation performance
        start_time = time.perf_counter()

        await personalization_engine.create_user_personalization_profile(user_id)

        profile_creation_time = (time.perf_counter() - start_time) * 1000
        assert profile_creation_time < 100.0  # Should be under 100ms

        # Test recommendation generation performance
        start_time = time.perf_counter()

        recommendations = await personalization_engine.generate_personalization_recommendations(user_id)

        recommendation_time = (time.perf_counter() - start_time) * 1000
        assert recommendation_time < 500.0  # Should be under 500ms

        # Test adaptation application performance
        if recommendations:
            start_time = time.perf_counter()

            await personalization_engine.apply_personalization_adaptation(
                user_id=user_id,
                recommendation=recommendations[0]
            )

            adaptation_time = (time.perf_counter() - start_time) * 1000
            assert adaptation_time < 200.0  # Should be under 200ms

        # Test insights generation performance
        start_time = time.perf_counter()

        await personalization_engine.get_personalization_insights(user_id)

        insights_time = (time.perf_counter() - start_time) * 1000
        assert insights_time < 300.0  # Should be under 300ms

    @pytest.mark.asyncio
    async def test_personalization_interface_compatibility(self, personalization_engine, mock_therapeutic_systems, mock_integration_systems):
        """Test compatibility with personalization interface expectations."""
        # Inject all dependencies
        personalization_engine.inject_therapeutic_systems(**mock_therapeutic_systems)
        personalization_engine.inject_integration_systems(**mock_integration_systems)

        user_id = "interface_test_user"

        # Test complete personalization workflow
        profile = await personalization_engine.create_user_personalization_profile(user_id)

        # Should match expected profile structure
        assert hasattr(profile, "user_id")
        assert hasattr(profile, "personalization_level")
        assert hasattr(profile, "learning_mode")
        assert hasattr(profile, "system_interactions")
        assert hasattr(profile, "adaptation_history")

        # Test recommendation generation
        recommendations = await personalization_engine.generate_personalization_recommendations(user_id)

        # Should match expected recommendation structure
        for rec in recommendations:
            assert hasattr(rec, "recommendation_id")
            assert hasattr(rec, "target_system")
            assert hasattr(rec, "domain")
            assert hasattr(rec, "confidence_score")
            assert hasattr(rec, "expected_impact")

        # Test insights generation
        insights = await personalization_engine.get_personalization_insights(user_id)

        # Should match expected insights structure
        assert "profile_summary" in insights
        assert "interaction_summary" in insights
        assert "therapeutic_effectiveness" in insights

        # Test health check
        health_check = await personalization_engine.health_check()

        # Should match expected health check structure
        assert "status" in health_check
        assert "engine_status" in health_check
        assert "user_profiles" in health_check
        assert "therapeutic_systems_available" in health_check
        assert "personalization_metrics" in health_check
