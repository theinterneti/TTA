"""

# Logseq: [[TTA.dev/Tests/Integration/Test_core_gameplay_loop]]
Integration Tests for Core Gameplay Loop

This module contains comprehensive integration tests for the Core Gameplay Loop
system, validating the complete therapeutic text adventure experience from
session start to completion.
"""

import asyncio
from datetime import datetime

import pytest
import pytest_asyncio

from src.components.gameplay_loop import GameplayLoopController
from src.components.gameplay_loop.models.core import ChoiceType, EmotionalState


class TestCoreGameplayLoopIntegration:
    """Integration tests for the complete Core Gameplay Loop system."""

    @pytest_asyncio.fixture
    async def gameplay_controller(self, neo4j_config, redis_config):
        """Create and initialize a GameplayLoopController for testing."""
        config = {
            "database": {
                "neo4j_uri": neo4j_config["uri"],
                "neo4j_user": neo4j_config["user"],
                "neo4j_password": neo4j_config["password"],
                "redis_host": redis_config["host"],
                "redis_port": redis_config["port"],
                "redis_db": redis_config["db"],
            },
            "narrative": {
                "complexity_adaptation_enabled": True,
                "immersion_techniques_enabled": True,
                "pacing_control_enabled": True,
            },
            "choice_architecture": {
                "agency_protection_enabled": True,
                "therapeutic_validation_enabled": True,
            },
            "consequence_system": {
                "therapeutic_framing_enabled": True,
                "causality_explanation_enabled": True,
                "progress_tracking_enabled": True,
            },
            "response_time_target": 2.0,
            "session_timeout": 3600,
        }

        controller = GameplayLoopController(config)

        # Initialize controller (in real implementation, this would connect to actual databases)
        # For testing, we'll mock the initialization
        controller.database_manager.initialize = lambda: True
        controller.narrative_engine.initialize = lambda: True
        controller.choice_architecture.initialize = lambda: True
        controller.consequence_system.initialize = lambda: True

        await controller.initialize()
        return controller

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Core gameplay loop components not fully implemented")
    async def test_complete_gameplay_session_flow(self, gameplay_controller):
        """Test complete gameplay session from start to end."""
        controller = gameplay_controller
        user_id = "test_user_001"

        # Test 1: Start new session
        session = await controller.start_session(
            user_id=user_id,
            therapeutic_context={
                "primary_goals": ["anxiety_management", "self_compassion"],
                "difficulty_preference": "gentle",
                "therapeutic_focus": "mindfulness",
            },
        )

        assert session is not None
        assert session.user_id == user_id
        assert session.is_active is True
        assert session.current_scene is not None
        assert len(session.available_choices) > 0
        assert session.session_state.emotional_state == EmotionalState.CALM

        # Test 2: Process user choices
        choice_count = 0
        max_choices = 5  # Test with 5 choices to validate progression

        while choice_count < max_choices and session.available_choices:
            # Select first available choice for testing
            selected_choice = session.available_choices[0]

            # Process the choice
            start_time = datetime.utcnow()
            (
                next_scene,
                new_choices,
                consequences,
            ) = await controller.process_user_choice(
                session.session_id, selected_choice.choice_id
            )
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Validate response time requirement (<2 seconds)
            assert processing_time < 2.0, (
                f"Processing took {processing_time:.2f}s (target: <2.0s)"
            )

            # Validate scene progression
            assert next_scene is not None, "Next scene should be generated"
            assert len(new_choices) > 0, "New choices should be available"
            assert consequences is not None, "Consequences should be generated"

            # Validate therapeutic integration
            assert consequences.therapeutic_value_realized > 0, (
                "Should have therapeutic value"
            )
            assert len(consequences.therapeutic_insights) > 0, (
                "Should have therapeutic insights"
            )
            assert len(consequences.learning_opportunities) > 0, (
                "Should have learning opportunities"
            )

            # Update session for next iteration
            session.current_scene = next_scene
            session.available_choices = new_choices
            choice_count += 1

        # Test 3: Validate session state progression
        session_status = await controller.get_session_status(session.session_id)
        assert session_status is not None
        assert session_status["total_choices"] == max_choices
        assert session_status["therapeutic_engagement"] > 0

        # Test 4: Pause and resume session
        pause_success = await controller.pause_session(session.session_id)
        assert pause_success is True

        resumed_session = await controller.resume_session(session.session_id)
        assert resumed_session is not None
        assert resumed_session.session_id == session.session_id
        assert resumed_session.session_recap is not None
        assert "Welcome back" in resumed_session.session_recap

        # Test 5: End session
        end_success = await controller.end_session(session.session_id)
        assert end_success is True

        # Validate session is no longer active
        final_status = await controller.get_session_status(session.session_id)
        assert final_status is None  # Should be None as session is ended

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Core gameplay loop components not fully implemented")
    async def test_therapeutic_progression_validation(self, gameplay_controller):
        """Test that therapeutic elements are properly integrated throughout gameplay."""
        controller = gameplay_controller
        user_id = "test_user_002"

        # Start session with specific therapeutic focus
        session = await controller.start_session(
            user_id=user_id,
            therapeutic_context={
                "primary_goals": ["emotional_regulation", "resilience_building"],
                "current_emotional_state": "anxious",
                "therapeutic_focus": "coping_skills",
            },
        )

        # Process several choices and validate therapeutic integration
        therapeutic_values = []
        therapeutic_insights = []
        learning_opportunities = []

        for _ in range(3):
            if not session.available_choices:
                break

            # Select a therapeutic choice if available
            therapeutic_choice = None
            for choice in session.available_choices:
                if choice.choice_type == ChoiceType.THERAPEUTIC:
                    therapeutic_choice = choice
                    break

            # If no therapeutic choice, select first available
            selected_choice = therapeutic_choice or session.available_choices[0]

            # Process choice
            (
                next_scene,
                new_choices,
                consequences,
            ) = await controller.process_user_choice(
                session.session_id, selected_choice.choice_id
            )

            # Collect therapeutic data
            therapeutic_values.append(consequences.therapeutic_value_realized)
            therapeutic_insights.extend(consequences.therapeutic_insights)
            learning_opportunities.extend(consequences.learning_opportunities)

            # Update session
            session.current_scene = next_scene
            session.available_choices = new_choices

        # Validate therapeutic integration
        assert len(therapeutic_values) > 0, "Should have therapeutic values"
        assert all(value > 0 for value in therapeutic_values), (
            "All choices should have therapeutic value"
        )
        assert len(therapeutic_insights) > 0, "Should have therapeutic insights"
        assert len(learning_opportunities) > 0, "Should have learning opportunities"

        # Validate therapeutic progression
        if len(therapeutic_values) > 1:
            # Check for therapeutic engagement (not necessarily increasing, but present)
            avg_therapeutic_value = sum(therapeutic_values) / len(therapeutic_values)
            assert avg_therapeutic_value > 0.3, (
                "Should maintain meaningful therapeutic engagement"
            )

        await controller.end_session(session.session_id)

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Core gameplay loop components not fully implemented")
    async def test_emotional_state_adaptation(self, gameplay_controller):
        """Test that the system adapts to different emotional states."""
        controller = gameplay_controller
        user_id = "test_user_003"

        # Test different emotional states
        emotional_states = [
            EmotionalState.CALM,
            EmotionalState.ANXIOUS,
            EmotionalState.OVERWHELMED,
        ]

        for emotional_state in emotional_states:
            session = await controller.start_session(
                user_id=f"{user_id}_{emotional_state.value}",
                therapeutic_context={
                    "current_emotional_state": emotional_state.value,
                    "primary_goals": ["emotional_regulation"],
                    "difficulty_preference": "adaptive",
                },
            )

            # Validate initial adaptation
            assert session.session_state.emotional_state == emotional_state

            # Process one choice to see adaptation
            if session.available_choices:
                selected_choice = session.available_choices[0]
                (
                    next_scene,
                    new_choices,
                    consequences,
                ) = await controller.process_user_choice(
                    session.session_id, selected_choice.choice_id
                )

                # Validate emotional adaptation in consequences
                assert consequences is not None
                assert consequences.therapeutic_value_realized > 0

                # Validate that insights are appropriate for emotional state
                insights_text = " ".join(consequences.therapeutic_insights).lower()

                if emotional_state == EmotionalState.ANXIOUS:
                    # Should contain calming or reassuring language
                    assert any(
                        word in insights_text
                        for word in ["calm", "safe", "gentle", "peace"]
                    )
                elif emotional_state == EmotionalState.OVERWHELMED:
                    # Should contain simplifying or supportive language
                    assert any(
                        word in insights_text
                        for word in ["simple", "step", "support", "manageable"]
                    )

            await controller.end_session(session.session_id)

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Core gameplay loop components not fully implemented")
    async def test_session_lifecycle_management(self, gameplay_controller):
        """Test comprehensive session lifecycle management."""
        controller = gameplay_controller
        user_id = "test_user_004"

        # Test 1: Multiple concurrent sessions
        session1 = await controller.start_session(user_id + "_1")
        session2 = await controller.start_session(user_id + "_2")

        assert session1.session_id != session2.session_id
        assert len(controller.active_sessions) == 2

        # Test 2: Session status tracking
        status1 = await controller.get_session_status(session1.session_id)
        status2 = await controller.get_session_status(session2.session_id)

        assert status1["session_id"] == session1.session_id
        assert status2["session_id"] == session2.session_id
        assert status1["is_active"] is True
        assert status2["is_active"] is True

        # Test 3: Session cleanup
        await controller.pause_session(session1.session_id)
        assert len(controller.active_sessions) == 1

        await controller.end_session(session2.session_id)
        assert len(controller.active_sessions) == 0

        # Test 4: Resume paused session
        resumed_session = await controller.resume_session(session1.session_id)
        assert resumed_session is not None
        assert resumed_session.session_id == session1.session_id
        assert len(controller.active_sessions) == 1

        await controller.end_session(session1.session_id)


if __name__ == "__main__":
    # Run basic integration test
    async def run_basic_test():
        """Run a basic integration test."""

        # Create controller with minimal config
        config = {"response_time_target": 2.0}
        controller = GameplayLoopController(config)

        # Mock initialization for basic test
        controller.database_manager.initialize = lambda: True
        controller.narrative_engine.initialize = lambda: True
        controller.choice_architecture.initialize = lambda: True
        controller.consequence_system.initialize = lambda: True

        await controller.initialize()

        # Test basic session flow
        session = await controller.start_session("test_user")

        if session.available_choices:
            choice = session.available_choices[0]
            start_time = datetime.utcnow()

            (
                next_scene,
                new_choices,
                consequences,
            ) = await controller.process_user_choice(
                session.session_id, choice.choice_id
            )

            (datetime.utcnow() - start_time).total_seconds()

        await controller.end_session(session.session_id)

    # Run the test
    asyncio.run(run_basic_test())
