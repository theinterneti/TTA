"""
Adventure Experience Optimization Tests

This module tests the complete therapeutic adventure experience, focusing on
engagement, fun factor, narrative immersion, and the balance between
therapeutic value and entertainment value.
"""

import asyncio
import time
from datetime import datetime, timezone

import pytest
import pytest_asyncio

from src.components.therapeutic_systems import (
    TherapeuticAdaptiveDifficultyEngine,
    TherapeuticCharacterDevelopmentSystem,
    TherapeuticCollaborativeSystem,
    TherapeuticConsequenceSystem,
    TherapeuticGameplayLoopController,
    TherapeuticIntegrationSystem,
    TherapeuticReplayabilitySystem,
)


def utc_now() -> datetime:
    """Get current UTC time with timezone awareness."""
    return datetime.now(timezone.utc)


class TestAdventureExperienceOptimization:
    """Test comprehensive adventure experience optimization."""

    @pytest_asyncio.fixture
    async def adventure_systems(self):
        """Create integrated adventure systems."""
        # Initialize all adventure-related systems
        gameplay_controller = TherapeuticGameplayLoopController()
        character_system = TherapeuticCharacterDevelopmentSystem()
        replayability_system = TherapeuticReplayabilitySystem()
        difficulty_engine = TherapeuticAdaptiveDifficultyEngine()
        consequence_system = TherapeuticConsequenceSystem()
        integration_system = TherapeuticIntegrationSystem()
        collaborative_system = TherapeuticCollaborativeSystem()

        # Initialize all systems
        await gameplay_controller.initialize()
        await character_system.initialize()
        await replayability_system.initialize()
        await difficulty_engine.initialize()
        await consequence_system.initialize()
        await integration_system.initialize()
        await collaborative_system.initialize()

        yield {
            "gameplay_controller": gameplay_controller,
            "character_system": character_system,
            "replayability_system": replayability_system,
            "difficulty_engine": difficulty_engine,
            "consequence_system": consequence_system,
            "integration_system": integration_system,
            "collaborative_system": collaborative_system,
        }

        # Cleanup (systems don't have shutdown methods, just let them be garbage collected)
        pass

    @pytest.mark.asyncio
    async def test_complete_adventure_session_flow(self, adventure_systems):
        """Test complete adventure session from character creation to conclusion."""
        gameplay = adventure_systems["gameplay_controller"]
        character_system = adventure_systems["character_system"]

        user_id = "adventure_player_001"

        # Phase 1: Start Adventure Session
        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=[
                "confidence_building",
                "social_skills",
                "emotional_regulation",
            ],
        )

        assert session_state is not None
        assert session_state.user_id == user_id
        session_id = session_state.session_id

        # Verify session is in character creation phase
        session_status = await gameplay.get_session_status(session_id)
        assert session_status["current_phase"] == "character_creation"

        # Phase 2: Character Creation Adventure
        character_creation_choices = [
            {
                "choice_type": "character_background",
                "selection": "brave_village_hero",
                "reasoning": "I want to help others and be courageous",
            },
            {
                "choice_type": "primary_strength",
                "selection": "empathy_and_wisdom",
                "reasoning": "I believe understanding others is important",
            },
            {
                "choice_type": "growth_goal",
                "selection": "overcome_social_anxiety",
                "reasoning": "I want to be more confident in social situations",
            },
        ]

        for choice in character_creation_choices:
            choice_response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice["selection"],
                choice_context={
                    "choice_type": choice["choice_type"],
                    "user_reasoning": choice["reasoning"],
                    "phase": "character_creation",
                },
            )

            assert choice_response["choice_processed"] is True
            assert choice_response["session_progress"]["therapeutic_value"] > 0.0
            assert "character_update" in choice_response
            assert "therapeutic_integration" in choice_response

        # Verify character attributes were initialized
        character_summary = await character_system.get_character_summary(user_id)
        assert character_summary is not None
        assert "error" not in character_summary
        assert "attributes" in character_summary
        assert len(character_summary["attributes"]) > 0

        # Store initial character profile for comparison
        initial_character_profile = await character_system.get_character_profile(
            user_id
        )

        # Phase 3: Adventure Gameplay Loop
        adventure_choices = [
            {
                "scenario": "village_crisis",
                "choice": "gather_information_first",
                "reasoning": "I want to understand the situation before acting",
            },
            {
                "scenario": "social_interaction",
                "choice": "approach_with_empathy",
                "reasoning": "I'll try to connect with the villager's feelings",
            },
            {
                "scenario": "conflict_resolution",
                "choice": "find_collaborative_solution",
                "reasoning": "Everyone should benefit from the solution",
            },
            {
                "scenario": "leadership_moment",
                "choice": "encourage_team_participation",
                "reasoning": "I want to help others feel valued and included",
            },
        ]

        therapeutic_value_accumulated = 0.0
        character_growth_tracked = []

        for i, adventure_choice in enumerate(adventure_choices):
            choice_response = await gameplay.process_choice(
                session_id=session_id,
                user_choice=adventure_choice["choice"],
                choice_context={
                    "scenario": adventure_choice["scenario"],
                    "user_reasoning": adventure_choice["reasoning"],
                    "phase": "active_gameplay",
                    "turn_number": i + 1,
                },
            )

            # Verify adventure response quality
            assert choice_response["success"] is True
            assert choice_response["therapeutic_value"] > 0.0
            assert choice_response["engagement_score"] > 0.6  # Should be engaging
            assert "narrative_response" in choice_response
            assert len(choice_response["narrative_response"]) > 50  # Rich narrative

            # Track therapeutic progress
            therapeutic_value_accumulated += choice_response["therapeutic_value"]

            # Verify character development
            if "character_development" in choice_response:
                character_growth_tracked.append(
                    choice_response["character_development"]
                )

            # Verify adventure immersion elements
            assert "world_state_changes" in choice_response
            assert "character_relationships" in choice_response
            assert "adventure_progression" in choice_response

        # Phase 4: Verify Adventure Experience Quality

        # Check therapeutic value accumulation
        assert therapeutic_value_accumulated > 2.0  # Significant therapeutic value

        # Check character growth
        assert len(character_growth_tracked) >= 3  # Multiple growth moments

        # Verify final character state
        final_character_profile = await character_system.get_character_profile(user_id)
        initial_confidence = initial_character_profile["attributes"]["confidence"]
        final_confidence = final_character_profile["attributes"]["confidence"]
        assert final_confidence > initial_confidence  # Character grew

        # Check session completion
        final_session_status = await gameplay.get_session_status(session_id)
        assert final_session_status["therapeutic_value_accumulated"] > 2.0
        assert final_session_status["choices_made"] == len(
            character_creation_choices
        ) + len(adventure_choices)
        assert final_session_status["engagement_metrics"]["average_engagement"] > 0.7

    @pytest.mark.asyncio
    async def test_adventure_engagement_optimization(self, adventure_systems):
        """Test that adventure elements maintain high engagement while delivering therapy."""
        gameplay = adventure_systems["gameplay_controller"]
        adventure_systems["difficulty_engine"]

        user_id = "engagement_test_user"

        # Start session with engagement tracking
        session_response = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["anxiety_management"],
            session_preferences={
                "engagement_priority": "high",
                "adventure_theme": "mystery_adventure",
                "pacing": "dynamic",
            },
        )

        session_id = session_response["session_id"]

        # Test various engagement scenarios
        engagement_scenarios = [
            {
                "scenario_type": "low_stakes_exploration",
                "expected_engagement": 0.6,
                "therapeutic_focus": "mindfulness",
            },
            {
                "scenario_type": "social_challenge",
                "expected_engagement": 0.8,
                "therapeutic_focus": "social_anxiety",
            },
            {
                "scenario_type": "problem_solving_puzzle",
                "expected_engagement": 0.9,
                "therapeutic_focus": "cognitive_flexibility",
            },
            {
                "scenario_type": "emotional_moment",
                "expected_engagement": 0.7,
                "therapeutic_focus": "emotional_regulation",
            },
        ]

        for scenario in engagement_scenarios:
            # Process scenario choice
            choice_response = await gameplay.process_choice(
                session_id=session_id,
                user_choice="engage_thoughtfully",
                choice_context={
                    "scenario_type": scenario["scenario_type"],
                    "therapeutic_focus": scenario["therapeutic_focus"],
                    "engagement_target": scenario["expected_engagement"],
                },
            )

            # Verify engagement meets expectations
            actual_engagement = choice_response.get("engagement_score", 0.0)
            expected_engagement = scenario["expected_engagement"]

            assert (
                actual_engagement >= expected_engagement * 0.9
            )  # Within 10% of target
            assert choice_response["therapeutic_value"] > 0.0

            # Verify adventure elements enhance rather than detract from therapy
            assert "immersive_elements" in choice_response
            assert "therapeutic_integration" in choice_response
            assert choice_response["therapeutic_integration"]["seamless"] is True

    @pytest.mark.asyncio
    async def test_replayability_and_exploration_value(self, adventure_systems):
        """Test that replayability system creates compelling alternative adventures."""
        replayability = adventure_systems["replayability_system"]
        gameplay = adventure_systems["gameplay_controller"]

        user_id = "exploration_test_user"

        # Create initial adventure session
        session_response = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["decision_making", "confidence_building"],
        )
        session_id = session_response["session_id"]

        # Make initial choices to create a baseline path
        initial_choices = [
            ("cautious_approach", "I want to be careful and think things through"),
            ("seek_help_from_others", "I believe collaboration is important"),
            ("prioritize_safety", "Safety should come first in any adventure"),
        ]

        for choice, reasoning in initial_choices:
            await gameplay.process_choice(
                session_id=session_id,
                user_choice=choice,
                choice_context={"user_reasoning": reasoning},
            )

        # Create exploration session to try alternative paths
        exploration_session = await replayability.create_exploration_session(
            user_id=user_id,
            base_session_id=session_id,
            exploration_mode="comparative",
            focus_areas=[
                "different_personality_approach",
                "alternative_therapeutic_strategies",
            ],
        )

        assert exploration_session["success"] is True
        exploration_id = exploration_session["exploration_id"]

        # Explore alternative choices
        alternative_choices = [
            ("bold_direct_approach", "This time I'll be more assertive and direct"),
            ("independent_action", "I'll try solving this on my own first"),
            (
                "calculated_risk_taking",
                "I'll take more strategic risks for better outcomes",
            ),
        ]

        for choice, reasoning in alternative_choices:
            exploration_response = await replayability.explore_alternative_choice(
                exploration_id=exploration_id,
                alternative_choice=choice,
                choice_context={"user_reasoning": reasoning},
            )

            assert exploration_response["success"] is True
            assert "outcome_comparison" in exploration_response
            assert "therapeutic_insights" in exploration_response
            assert exploration_response["engagement_maintained"] is True

        # Get comprehensive path comparison
        path_comparison = await replayability.compare_exploration_paths(
            exploration_id=exploration_id,
            comparison_metrics=[
                "therapeutic_value",
                "character_growth",
                "engagement_level",
            ],
        )

        assert path_comparison["paths_compared"] == 2  # Original + alternative
        assert "therapeutic_insights" in path_comparison
        assert "recommended_approach" in path_comparison
        assert path_comparison["exploration_value"] > 0.7  # High learning value

    @pytest.mark.asyncio
    async def test_adventure_performance_benchmarks(self, adventure_systems):
        """Test that adventure systems meet performance benchmarks for smooth gameplay."""
        gameplay = adventure_systems["gameplay_controller"]
        character_system = adventure_systems["character_system"]

        user_id = "performance_test_user"

        # Test session startup performance
        start_time = time.perf_counter()
        session_response = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["performance_testing"],
        )
        session_startup_time = (time.perf_counter() - start_time) * 1000

        assert session_startup_time < 500.0  # Should start in under 500ms
        assert session_response["success"] is True
        session_id = session_response["session_id"]

        # Test choice processing performance (critical for immersion)
        choice_processing_times = []

        for i in range(10):
            start_time = time.perf_counter()
            choice_response = await gameplay.process_choice(
                session_id=session_id,
                user_choice=f"test_choice_{i}",
                choice_context={"performance_test": True, "iteration": i},
            )
            processing_time = (time.perf_counter() - start_time) * 1000
            choice_processing_times.append(processing_time)

            assert choice_response["success"] is True
            assert processing_time < 200.0  # Each choice should process in under 200ms

        # Verify consistent performance
        average_processing_time = sum(choice_processing_times) / len(
            choice_processing_times
        )
        assert average_processing_time < 150.0  # Average should be even faster

        # Test character development performance
        start_time = time.perf_counter()
        character_profile = await character_system.get_character_profile(user_id)
        character_retrieval_time = (time.perf_counter() - start_time) * 1000

        assert character_retrieval_time < 50.0  # Character data should be very fast
        assert character_profile is not None

        # Test concurrent session handling
        concurrent_sessions = []
        for i in range(5):
            session_response = await gameplay.start_session(
                user_id=f"concurrent_user_{i}",
                therapeutic_goals=["concurrent_testing"],
            )
            concurrent_sessions.append(session_response["session_id"])

        # Process choices concurrently
        concurrent_tasks = []
        for session_id in concurrent_sessions:
            task = asyncio.create_task(
                gameplay.process_choice(
                    session_id=session_id,
                    user_choice="concurrent_test_choice",
                    choice_context={"concurrent_test": True},
                )
            )
            concurrent_tasks.append(task)

        start_time = time.perf_counter()
        concurrent_results = await asyncio.gather(*concurrent_tasks)
        concurrent_processing_time = (time.perf_counter() - start_time) * 1000

        # All should succeed and complete quickly
        assert all(result["success"] for result in concurrent_results)
        assert (
            concurrent_processing_time < 1000.0
        )  # 5 concurrent choices in under 1 second

    @pytest.mark.asyncio
    async def test_therapeutic_adventure_balance(self, adventure_systems):
        """Test that adventure elements enhance rather than compromise therapeutic value."""
        gameplay = adventure_systems["gameplay_controller"]
        adventure_systems["integration_system"]

        user_id = "balance_test_user"

        # Start session with specific therapeutic goals
        session_response = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["social_anxiety", "self_esteem", "communication_skills"],
            session_preferences={
                "therapeutic_priority": "high",
                "adventure_integration": "seamless",
            },
        )

        session_id = session_response["session_id"]

        # Test scenarios that require balancing fun and therapy
        balance_scenarios = [
            {
                "scenario": "social_gathering_adventure",
                "therapeutic_target": "social_anxiety",
                "fun_elements": [
                    "interesting_characters",
                    "engaging_dialogue",
                    "meaningful_choices",
                ],
                "expected_therapeutic_value": 0.8,
                "expected_engagement": 0.8,
            },
            {
                "scenario": "leadership_challenge_quest",
                "therapeutic_target": "self_esteem",
                "fun_elements": [
                    "strategic_thinking",
                    "character_growth",
                    "achievement_unlocks",
                ],
                "expected_therapeutic_value": 0.7,
                "expected_engagement": 0.9,
            },
            {
                "scenario": "communication_puzzle_adventure",
                "therapeutic_target": "communication_skills",
                "fun_elements": [
                    "creative_problem_solving",
                    "collaborative_elements",
                    "story_progression",
                ],
                "expected_therapeutic_value": 0.9,
                "expected_engagement": 0.7,
            },
        ]

        for scenario in balance_scenarios:
            choice_response = await gameplay.process_choice(
                session_id=session_id,
                user_choice="engage_with_scenario",
                choice_context={
                    "scenario": scenario["scenario"],
                    "therapeutic_target": scenario["therapeutic_target"],
                    "fun_elements": scenario["fun_elements"],
                },
            )

            # Verify therapeutic value is maintained
            therapeutic_value = choice_response.get("therapeutic_value", 0.0)
            assert therapeutic_value >= scenario["expected_therapeutic_value"] * 0.9

            # Verify engagement is maintained
            engagement_score = choice_response.get("engagement_score", 0.0)
            assert engagement_score >= scenario["expected_engagement"] * 0.9

            # Verify integration quality
            integration_quality = choice_response.get("integration_quality", {})
            assert integration_quality.get("therapeutic_alignment", 0.0) > 0.8
            assert integration_quality.get("narrative_coherence", 0.0) > 0.8
            assert integration_quality.get("engagement_enhancement", 0.0) > 0.7

            # Verify fun elements don't compromise therapeutic goals
            assert choice_response.get("therapeutic_compromise", False) is False
            assert choice_response.get("engagement_artificial", False) is False
