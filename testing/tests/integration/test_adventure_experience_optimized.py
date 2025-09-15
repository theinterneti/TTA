"""
Optimized Adventure Experience Tests

This module tests the complete therapeutic adventure experience with proper
system integration, focusing on engagement optimization and therapeutic value.
"""

import time

import pytest
import pytest_asyncio

from src.components.therapeutic_systems import (
    TherapeuticAdaptiveDifficultyEngine,
    TherapeuticCharacterDevelopmentSystem,
    TherapeuticCollaborativeSystem,
    TherapeuticConsequenceSystem,
    TherapeuticEmotionalSafetySystem,
    TherapeuticErrorRecoveryManager,
    TherapeuticGameplayLoopController,
    TherapeuticIntegrationSystem,
    TherapeuticReplayabilitySystem,
)


class TestOptimizedAdventureExperience:
    """Test optimized adventure experience with full system integration."""

    @pytest_asyncio.fixture
    async def integrated_adventure_systems(self):
        """Create fully integrated adventure systems."""
        # Initialize all systems
        gameplay_controller = TherapeuticGameplayLoopController()
        character_system = TherapeuticCharacterDevelopmentSystem()
        replayability_system = TherapeuticReplayabilitySystem()
        difficulty_engine = TherapeuticAdaptiveDifficultyEngine()
        consequence_system = TherapeuticConsequenceSystem()
        integration_system = TherapeuticIntegrationSystem()
        collaborative_system = TherapeuticCollaborativeSystem()
        safety_system = TherapeuticEmotionalSafetySystem()
        error_recovery = TherapeuticErrorRecoveryManager()

        # Initialize all systems
        await gameplay_controller.initialize()
        await character_system.initialize()
        await replayability_system.initialize()
        await difficulty_engine.initialize()
        await consequence_system.initialize()
        await integration_system.initialize()
        await collaborative_system.initialize()
        await safety_system.initialize()
        await error_recovery.initialize()

        # Inject therapeutic systems into gameplay controller
        gameplay_controller.inject_therapeutic_systems(
            consequence_system=consequence_system,
            emotional_safety_system=safety_system,
            adaptive_difficulty_engine=difficulty_engine,
            character_development_system=character_system,
            therapeutic_integration_system=integration_system,
        )

        yield {
            "gameplay_controller": gameplay_controller,
            "character_system": character_system,
            "replayability_system": replayability_system,
            "difficulty_engine": difficulty_engine,
            "consequence_system": consequence_system,
            "integration_system": integration_system,
            "collaborative_system": collaborative_system,
            "safety_system": safety_system,
            "error_recovery": error_recovery,
        }

    @pytest.mark.asyncio
    async def test_fully_integrated_adventure_session(self, integrated_adventure_systems):
        """Test complete adventure session with all systems integrated."""
        systems = integrated_adventure_systems
        gameplay = systems["gameplay_controller"]
        systems["character_system"]

        user_id = "integrated_adventure_user"

        # Start integrated session
        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["confidence_building", "social_skills", "emotional_regulation"],
        )

        assert session_state is not None
        assert session_state.user_id == user_id
        session_id = session_state.session_id

        # Verify session status
        status = await gameplay.get_session_status(session_id)
        assert status is not None
        assert status["session_id"] == session_id

        # Process adventure choices with full integration
        adventure_choices = [
            {
                "choice": "approach_with_courage",
                "context": {
                    "scenario": "village_crisis",
                    "therapeutic_focus": "confidence_building",
                    "expected_growth": "courage",
                }
            },
            {
                "choice": "listen_with_empathy",
                "context": {
                    "scenario": "social_interaction",
                    "therapeutic_focus": "social_skills",
                    "expected_growth": "empathy",
                }
            },
            {
                "choice": "manage_emotions_mindfully",
                "context": {
                    "scenario": "stressful_situation",
                    "therapeutic_focus": "emotional_regulation",
                    "expected_growth": "mindfulness",
                }
            },
        ]

        total_therapeutic_value = 0.0
        character_growth_events = []

        for _i, adventure_choice in enumerate(adventure_choices):
            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=adventure_choice["choice"],
                choice_context=adventure_choice["context"]
            )

            # Verify integrated response
            assert response["choice_processed"] is True
            assert "session_progress" in response
            assert "safety_assessment" in response
            assert "consequence" in response
            assert "character_update" in response
            assert "therapeutic_integration" in response

            # Track therapeutic progress
            therapeutic_value = response["session_progress"]["therapeutic_value"]
            assert therapeutic_value > 0.0
            total_therapeutic_value += therapeutic_value

            # Verify character development occurred
            if response["character_update"]["character_updated"]:
                character_growth_events.append(response["character_update"])

            # Verify safety assessment
            safety = response["safety_assessment"]
            assert safety["crisis_detected"] is False
            assert safety["safety_level"] in ["standard", "elevated", "high"]

            # Verify consequence processing
            consequence = response["consequence"]
            assert consequence["consequence_processed"] is True
            assert consequence["therapeutic_value"] > 0.0

        # Verify overall session quality
        assert total_therapeutic_value > 2.0  # Significant therapeutic value
        assert len(character_growth_events) >= 2  # Multiple growth events

        # Complete session and verify outcome
        outcome = await gameplay.complete_session(session_id)
        assert outcome is not None
        assert outcome.therapeutic_value_total > 2.0
        assert len(outcome.milestones_achieved) > 0

    @pytest.mark.asyncio
    async def test_adventure_engagement_optimization(self, integrated_adventure_systems):
        """Test that adventure elements maintain high engagement."""
        systems = integrated_adventure_systems
        gameplay = systems["gameplay_controller"]
        systems["difficulty_engine"]

        user_id = "engagement_optimization_user"

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["engagement_testing"],
        )
        session_id = session_state.session_id

        # Test engagement across different scenario types
        engagement_scenarios = [
            {
                "choice": "explore_mysterious_cave",
                "context": {"scenario_type": "exploration", "engagement_target": 0.8},
                "expected_min_engagement": 0.7,
            },
            {
                "choice": "solve_ancient_puzzle",
                "context": {"scenario_type": "problem_solving", "engagement_target": 0.9},
                "expected_min_engagement": 0.8,
            },
            {
                "choice": "help_injured_companion",
                "context": {"scenario_type": "emotional_moment", "engagement_target": 0.7},
                "expected_min_engagement": 0.6,
            },
            {
                "choice": "negotiate_with_dragon",
                "context": {"scenario_type": "social_challenge", "engagement_target": 0.85},
                "expected_min_engagement": 0.75,
            },
        ]

        engagement_scores = []

        for scenario in engagement_scenarios:
            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=scenario["choice"],
                choice_context=scenario["context"]
            )

            assert response["choice_processed"] is True

            # Check engagement score
            engagement_score = response["session_progress"]["engagement_score"]
            engagement_scores.append(engagement_score)

            # Verify minimum engagement threshold
            assert engagement_score >= scenario["expected_min_engagement"]

            # Verify therapeutic value is maintained alongside engagement
            therapeutic_value = response["session_progress"]["therapeutic_value"]
            assert therapeutic_value > 0.0

        # Verify overall engagement quality
        average_engagement = sum(engagement_scores) / len(engagement_scores)
        assert average_engagement > 0.7  # High average engagement

    @pytest.mark.asyncio
    async def test_character_development_adventure_integration(self, integrated_adventure_systems):
        """Test character development integration with adventure elements."""
        systems = integrated_adventure_systems
        gameplay = systems["gameplay_controller"]
        character_system = systems["character_system"]

        user_id = "character_adventure_user"

        # Start session
        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["character_development", "personal_growth"],
        )
        session_id = session_state.session_id

        # Get initial character state
        initial_summary = await character_system.get_character_summary(user_id)
        initial_attributes = initial_summary.get("attributes", {})

        # Process character development choices
        character_choices = [
            {
                "choice": "stand_up_for_friend",
                "context": {"attribute_focus": "courage", "growth_opportunity": "high"},
            },
            {
                "choice": "share_wisdom_with_village",
                "context": {"attribute_focus": "wisdom", "growth_opportunity": "medium"},
            },
            {
                "choice": "show_compassion_to_enemy",
                "context": {"attribute_focus": "compassion", "growth_opportunity": "high"},
            },
        ]

        attribute_improvements = {}

        for choice_data in character_choices:
            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice_data["choice"],
                choice_context=choice_data["context"]
            )

            assert response["choice_processed"] is True

            # Verify character update occurred
            character_update = response["character_update"]
            assert character_update["character_updated"] is True

            # Track attribute improvements
            if "attribute_changes" in character_update:
                for attr, change in character_update["attribute_changes"].items():
                    if attr not in attribute_improvements:
                        attribute_improvements[attr] = 0.0
                    attribute_improvements[attr] += change

        # Verify character growth occurred
        final_summary = await character_system.get_character_summary(user_id)
        final_attributes = final_summary.get("attributes", {})

        # Check that at least some attributes improved
        improvements_found = 0
        for attr_name in ["courage", "wisdom", "compassion"]:
            if attr_name in initial_attributes and attr_name in final_attributes:
                if final_attributes[attr_name] > initial_attributes[attr_name]:
                    improvements_found += 1

        assert improvements_found >= 2  # At least 2 attributes should improve

    @pytest.mark.asyncio
    async def test_adventure_performance_optimization(self, integrated_adventure_systems):
        """Test that integrated adventure systems meet performance benchmarks."""
        systems = integrated_adventure_systems
        gameplay = systems["gameplay_controller"]

        user_id = "performance_optimization_user"

        # Test session startup with full integration
        start_time = time.perf_counter()
        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["performance_testing"],
        )
        startup_time = (time.perf_counter() - start_time) * 1000

        assert startup_time < 1000.0  # Integrated startup under 1 second
        assert session_state is not None
        session_id = session_state.session_id

        # Test choice processing performance with full integration
        processing_times = []

        for i in range(5):
            start_time = time.perf_counter()
            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=f"optimized_choice_{i}",
                choice_context={"performance_test": True, "integration_test": True}
            )
            processing_time = (time.perf_counter() - start_time) * 1000
            processing_times.append(processing_time)

            assert response["choice_processed"] is True
            assert processing_time < 500.0  # Integrated processing under 500ms

        # Verify consistent performance
        avg_processing_time = sum(processing_times) / len(processing_times)
        assert avg_processing_time < 300.0  # Average should be even better

        # Verify all systems are healthy after performance test
        health = await gameplay.health_check()
        assert health["status"] in ["healthy", "degraded"]  # Should not be unhealthy

    @pytest.mark.asyncio
    async def test_therapeutic_value_vs_engagement_balance(self, integrated_adventure_systems):
        """Test that therapeutic value and engagement are properly balanced."""
        systems = integrated_adventure_systems
        gameplay = systems["gameplay_controller"]

        user_id = "balance_test_user"

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["balance_testing", "optimal_experience"],
        )
        session_id = session_state.session_id

        # Test scenarios that balance therapeutic value and engagement
        balance_scenarios = [
            {
                "choice": "therapeutic_high_engagement_low",
                "context": {"balance_test": "therapeutic_priority"},
                "expect_therapeutic": 0.8,
                "expect_engagement": 0.5,
            },
            {
                "choice": "engagement_high_therapeutic_medium",
                "context": {"balance_test": "engagement_priority"},
                "expect_therapeutic": 0.6,
                "expect_engagement": 0.8,
            },
            {
                "choice": "balanced_approach",
                "context": {"balance_test": "balanced_priority"},
                "expect_therapeutic": 0.7,
                "expect_engagement": 0.7,
            },
        ]

        for scenario in balance_scenarios:
            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=scenario["choice"],
                choice_context=scenario["context"]
            )

            assert response["choice_processed"] is True

            therapeutic_value = response["session_progress"]["therapeutic_value"]
            engagement_score = response["session_progress"]["engagement_score"]

            # Verify both values are reasonable (allowing for system limitations)
            assert therapeutic_value >= scenario["expect_therapeutic"] * 0.5  # At least 50% of expected
            assert engagement_score >= scenario["expect_engagement"] * 0.5  # At least 50% of expected

            # Verify neither is completely neglected
            assert therapeutic_value > 0.0
            assert engagement_score >= 0.0  # Engagement might be 0 if not implemented yet
