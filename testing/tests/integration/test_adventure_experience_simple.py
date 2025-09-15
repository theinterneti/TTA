"""
Simple Adventure Experience Tests

This module tests the core therapeutic adventure experience functionality
with focus on engagement, therapeutic value, and system integration.
"""

import asyncio
import time

import pytest
import pytest_asyncio

from src.components.therapeutic_systems import (
    TherapeuticCharacterDevelopmentSystem,
    TherapeuticGameplayLoopController,
)


class TestSimpleAdventureExperience:
    """Test core adventure experience functionality."""

    @pytest_asyncio.fixture
    async def gameplay_controller(self):
        """Create gameplay controller."""
        controller = TherapeuticGameplayLoopController()
        await controller.initialize()
        yield controller

    @pytest_asyncio.fixture
    async def character_system(self):
        """Create character development system."""
        system = TherapeuticCharacterDevelopmentSystem()
        await system.initialize()
        yield system

    @pytest.mark.asyncio
    async def test_basic_adventure_session(self, gameplay_controller):
        """Test basic adventure session functionality."""
        user_id = "test_adventure_user"

        # Start session
        session_state = await gameplay_controller.start_session(
            user_id=user_id,
            therapeutic_goals=["confidence_building", "social_skills"],
        )

        assert session_state is not None
        assert session_state.user_id == user_id
        session_id = session_state.session_id

        # Check session status
        status = await gameplay_controller.get_session_status(session_id)
        assert status is not None
        assert status["session_id"] == session_id
        assert status["user_id"] == user_id

        # Process some choices
        choices = [
            "explore_carefully",
            "help_others",
            "solve_problem_creatively",
            "communicate_clearly",
        ]

        total_therapeutic_value = 0.0

        for i, choice in enumerate(choices):
            response = await gameplay_controller.process_user_choice(
                session_id=session_id,
                user_choice=choice,
                choice_context={"turn": i + 1},
            )

            # Verify response structure
            assert response["choice_processed"] is True
            assert "session_progress" in response
            assert "safety_assessment" in response
            assert "consequence" in response
            assert "therapeutic_integration" in response

            # Track therapeutic value
            therapeutic_value = response["session_progress"]["therapeutic_value"]
            assert therapeutic_value >= 0.0
            total_therapeutic_value += therapeutic_value

        # Verify therapeutic value accumulation
        assert total_therapeutic_value > 0.0

        # Complete session
        outcome = await gameplay_controller.complete_session(session_id)
        assert outcome is not None
        assert outcome.session_id == session_id
        assert outcome.therapeutic_value_total > 0.0

    @pytest.mark.asyncio
    async def test_character_development_integration(self, character_system):
        """Test character development system integration."""
        user_id = "character_test_user"

        # Create character
        character = await character_system.create_character(
            user_id=user_id,
            therapeutic_goals=["confidence", "empathy"],
            character_name="Hero",
        )

        assert character is not None
        assert character.user_id == user_id
        assert character.character_name == "Hero"

        # Process therapeutic consequences
        consequence_data = {
            "choice": "help_villager",
            "outcome": "positive",
            "therapeutic_value": 1.5,
            "attributes_affected": ["empathy", "confidence"],
        }

        result = await character_system.process_therapeutic_consequence(
            user_id=user_id,
            consequence_data=consequence_data,
        )

        assert result["character_updated"] is True
        assert result["therapeutic_value"] > 0.0
        assert "milestone_progress" in result

        # Get character summary
        summary = await character_system.get_character_summary(user_id)
        assert summary is not None
        assert "error" not in summary
        assert "attributes" in summary
        assert summary["total_therapeutic_value"] > 0.0

    @pytest.mark.asyncio
    async def test_adventure_performance_benchmarks(self, gameplay_controller):
        """Test adventure system performance meets benchmarks."""
        user_id = "performance_test_user"

        # Test session startup performance
        start_time = time.perf_counter()
        session_state = await gameplay_controller.start_session(
            user_id=user_id,
            therapeutic_goals=["performance_testing"],
        )
        startup_time = (time.perf_counter() - start_time) * 1000

        assert startup_time < 500.0  # Should start in under 500ms
        assert session_state is not None
        session_id = session_state.session_id

        # Test choice processing performance
        choice_times = []
        for i in range(5):
            start_time = time.perf_counter()
            response = await gameplay_controller.process_user_choice(
                session_id=session_id,
                user_choice=f"test_choice_{i}",
                choice_context={"performance_test": True},
            )
            processing_time = (time.perf_counter() - start_time) * 1000
            choice_times.append(processing_time)

            assert response["choice_processed"] is True
            assert processing_time < 200.0  # Each choice under 200ms

        # Verify consistent performance
        avg_time = sum(choice_times) / len(choice_times)
        assert avg_time < 150.0  # Average should be even faster

    @pytest.mark.asyncio
    async def test_therapeutic_value_optimization(self, gameplay_controller):
        """Test that adventure choices generate meaningful therapeutic value."""
        user_id = "therapeutic_value_user"

        session_state = await gameplay_controller.start_session(
            user_id=user_id,
            therapeutic_goals=["anxiety_management", "self_esteem"],
        )
        session_id = session_state.session_id

        # Test different types of therapeutic choices
        therapeutic_scenarios = [
            {
                "choice": "face_fear_gradually",
                "context": {"therapeutic_focus": "anxiety_management"},
                "expected_min_value": 0.5,
            },
            {
                "choice": "celebrate_small_victory",
                "context": {"therapeutic_focus": "self_esteem"},
                "expected_min_value": 0.7,
            },
            {
                "choice": "practice_mindfulness",
                "context": {"therapeutic_focus": "anxiety_management"},
                "expected_min_value": 0.6,
            },
            {
                "choice": "help_team_member",
                "context": {"therapeutic_focus": "self_esteem"},
                "expected_min_value": 0.8,
            },
        ]

        for scenario in therapeutic_scenarios:
            response = await gameplay_controller.process_user_choice(
                session_id=session_id,
                user_choice=scenario["choice"],
                choice_context=scenario["context"],
            )

            assert response["choice_processed"] is True
            therapeutic_value = response["session_progress"]["therapeutic_value"]
            assert therapeutic_value >= scenario["expected_min_value"]

            # Verify therapeutic integration quality
            integration = response["therapeutic_integration"]
            assert integration.get("therapeutic_alignment", 0.0) > 0.5
            assert integration.get("goal_progress", 0.0) > 0.0

    @pytest.mark.asyncio
    async def test_engagement_maintenance(self, gameplay_controller):
        """Test that adventure maintains high engagement throughout session."""
        user_id = "engagement_test_user"

        session_state = await gameplay_controller.start_session(
            user_id=user_id,
            therapeutic_goals=["engagement_testing"],
        )
        session_id = session_state.session_id

        # Process multiple choices and track engagement
        engagement_scores = []

        for i in range(8):  # Longer session to test engagement maintenance
            response = await gameplay_controller.process_user_choice(
                session_id=session_id,
                user_choice=f"engaging_choice_{i}",
                choice_context={"engagement_test": True, "turn": i + 1},
            )

            assert response["choice_processed"] is True
            engagement_score = response["session_progress"]["engagement_score"]
            engagement_scores.append(engagement_score)

            # Each individual choice should maintain good engagement
            assert engagement_score > 0.5  # Minimum engagement threshold

        # Verify engagement doesn't decline significantly over time
        first_half_avg = sum(engagement_scores[:4]) / 4
        second_half_avg = sum(engagement_scores[4:]) / 4

        # Engagement should not drop by more than 20%
        assert second_half_avg >= first_half_avg * 0.8

        # Overall average should be good
        overall_avg = sum(engagement_scores) / len(engagement_scores)
        assert overall_avg > 0.6

    @pytest.mark.asyncio
    async def test_concurrent_adventure_sessions(self, gameplay_controller):
        """Test system stability with multiple concurrent adventure sessions."""
        # Create multiple concurrent sessions
        session_tasks = []
        for i in range(3):
            task = asyncio.create_task(
                gameplay_controller.start_session(
                    user_id=f"concurrent_user_{i}",
                    therapeutic_goals=["concurrent_testing"],
                )
            )
            session_tasks.append(task)

        # Wait for all sessions to start
        session_states = await asyncio.gather(*session_tasks)

        # Verify all sessions started successfully
        assert len(session_states) == 3
        for session_state in session_states:
            assert session_state is not None
            assert session_state.user_id.startswith("concurrent_user_")

        # Process choices concurrently
        choice_tasks = []
        for session_state in session_states:
            task = asyncio.create_task(
                gameplay_controller.process_user_choice(
                    session_id=session_state.session_id,
                    user_choice="concurrent_test_choice",
                    choice_context={"concurrent_test": True},
                )
            )
            choice_tasks.append(task)

        # Wait for all choices to process
        choice_responses = await asyncio.gather(*choice_tasks)

        # Verify all choices processed successfully
        assert len(choice_responses) == 3
        for response in choice_responses:
            assert response["choice_processed"] is True
            assert response["session_progress"]["therapeutic_value"] >= 0.0

    @pytest.mark.asyncio
    async def test_system_health_monitoring(
        self, gameplay_controller, character_system
    ):
        """Test that adventure systems maintain healthy status."""
        # Check gameplay controller health
        gameplay_health = await gameplay_controller.health_check()
        assert gameplay_health["status"] == "healthy"
        assert "active_sessions" in gameplay_health
        assert "metrics" in gameplay_health

        # Check character system health
        character_health = await character_system.health_check()
        assert character_health["status"] == "healthy"
        assert "characters_tracked" in character_health
        assert "metrics" in character_health

        # Verify systems are ready for adventure experiences
        assert gameplay_health["ready_for_sessions"] is True
        assert character_health["ready_for_character_creation"] is True
