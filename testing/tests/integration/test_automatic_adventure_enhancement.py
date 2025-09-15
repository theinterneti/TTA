"""
Automatic Adventure Enhancement Tests

This module tests that adventure enhancement is automatically applied
to all therapeutic gaming sessions without manual intervention.
"""

import time

import pytest
import pytest_asyncio

from src.components.adventure_experience.adventure_enhancement_system import (
    AdventureEnhancementSystem,
)
from src.components.therapeutic_systems import (
    TherapeuticAdaptiveDifficultyEngine,
    TherapeuticCharacterDevelopmentSystem,
    TherapeuticConsequenceSystem,
    TherapeuticEmotionalSafetySystem,
    TherapeuticGameplayLoopController,
)


class TestAutomaticAdventureEnhancement:
    """Test automatic adventure enhancement in therapeutic gaming."""

    @pytest_asyncio.fixture
    async def auto_enhanced_gameplay(self):
        """Create gameplay system with automatic adventure enhancement."""
        # Initialize all systems
        gameplay_controller = TherapeuticGameplayLoopController()
        character_system = TherapeuticCharacterDevelopmentSystem()
        consequence_system = TherapeuticConsequenceSystem()
        safety_system = TherapeuticEmotionalSafetySystem()
        difficulty_engine = TherapeuticAdaptiveDifficultyEngine()
        adventure_enhancer = AdventureEnhancementSystem()

        # Initialize systems
        await gameplay_controller.initialize()
        await character_system.initialize()
        await consequence_system.initialize()
        await safety_system.initialize()
        await difficulty_engine.initialize()
        await adventure_enhancer.initialize()

        # Inject systems including adventure enhancer
        gameplay_controller.inject_therapeutic_systems(
            consequence_system=consequence_system,
            emotional_safety_system=safety_system,
            adaptive_difficulty_engine=difficulty_engine,
            character_development_system=character_system,
            therapeutic_integration_system=None,
            adventure_enhancer=adventure_enhancer,
        )

        yield {
            "gameplay_controller": gameplay_controller,
            "character_system": character_system,
            "consequence_system": consequence_system,
            "safety_system": safety_system,
            "difficulty_engine": difficulty_engine,
            "adventure_enhancer": adventure_enhancer,
        }

    @pytest.mark.asyncio
    async def test_automatic_adventure_enhancement(self, auto_enhanced_gameplay):
        """Test that adventure enhancement is automatically applied to all choices."""
        systems = auto_enhanced_gameplay
        gameplay = systems["gameplay_controller"]

        user_id = "auto_enhanced_user"

        # Start session
        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["automatic_enhancement_testing"],
        )
        session_id = session_state.session_id

        # Process choice - should automatically get adventure enhancement
        response = await gameplay.process_user_choice(
            session_id=session_id,
            user_choice="explore_the_mysterious_ancient_temple_with_wisdom",
            choice_context={
                "adventure_theme": "fantasy_quest",
                "scenario_type": "exploration",
                "challenge_level": "moderate",
            },
        )

        # Verify base therapeutic response is present
        assert response["choice_processed"] is True
        assert "safety_assessment" in response
        assert "consequence" in response
        assert "session_progress" in response

        # Verify adventure enhancement was automatically applied
        adventure_features = [
            "engagement_score",
            "narrative_response",
            "world_state_changes",
            "character_relationships",
            "adventure_progression",
            "story_context",
            "immersive_elements",
            "choice_consequences",
            "exploration_opportunities",
        ]

        for feature in adventure_features:
            assert (
                feature in response
            ), f"Missing automatically enhanced feature: {feature}"

        # Verify engagement score is calculated and applied
        engagement_score = response["engagement_score"]
        assert engagement_score > 0.0
        assert engagement_score <= 1.0

        # Verify session progress includes engagement
        session_progress = response["session_progress"]
        assert session_progress["engagement_score"] == engagement_score

        # Verify narrative response is rich and contextual
        narrative = response["narrative_response"]
        assert len(narrative) > 50
        assert any(
            keyword in narrative.lower()
            for keyword in ["mystical", "ancient", "temple", "wisdom"]
        )

    @pytest.mark.asyncio
    async def test_adventure_enhancement_with_different_themes(
        self, auto_enhanced_gameplay
    ):
        """Test automatic enhancement maintains theme consistency within a session."""
        systems = auto_enhanced_gameplay
        gameplay = systems["gameplay_controller"]

        # Test theme consistency - once a theme is established, it should be maintained
        user_id = "theme_consistency_user"

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["theme_testing"],
        )
        session_id = session_state.session_id

        # First choice establishes the theme
        first_response = await gameplay.process_user_choice(
            session_id=session_id,
            user_choice="investigate_crime_scene_methodically",
            choice_context={"adventure_theme": "modern_mystery"},
        )

        # Verify enhancement was applied
        assert "engagement_score" in first_response
        assert "narrative_response" in first_response
        assert "story_context" in first_response

        # Get the established theme
        established_theme = first_response["story_context"]["theme"]

        # Subsequent choices should maintain the same theme for consistency
        subsequent_choices = [
            {
                "choice": "explore_alien_ruins_cautiously",
                "context": {
                    "adventure_theme": "space_exploration"
                },  # This will be ignored
            },
            {
                "choice": "learn_magic_spell_from_mentor",
                "context": {"adventure_theme": "fantasy_quest"},  # This will be ignored
            },
        ]

        for choice_data in subsequent_choices:
            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice_data["choice"],
                choice_context=choice_data["context"],
            )

            # Verify enhancement was applied
            assert "engagement_score" in response
            assert "narrative_response" in response
            assert "story_context" in response

            # Verify theme consistency - should maintain the established theme
            story_context = response["story_context"]
            assert (
                story_context["theme"] == established_theme
            ), f"Theme should remain consistent throughout session: {established_theme}"

            # Verify narrative is enhanced regardless of theme
            narrative = response["narrative_response"]
            assert len(narrative) > 30, "Narrative should be enhanced"

    @pytest.mark.asyncio
    async def test_engagement_progression_over_session(self, auto_enhanced_gameplay):
        """Test that engagement is tracked and maintained over a session."""
        systems = auto_enhanced_gameplay
        gameplay = systems["gameplay_controller"]

        user_id = "engagement_progression_user"

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["engagement_progression_testing"],
        )
        session_id = session_state.session_id

        # Process multiple choices and track engagement
        engagement_choices = [
            "help_villager_with_creative_solution",
            "explore_mysterious_cave_carefully",
            "solve_ancient_puzzle_with_wisdom",
            "form_alliance_with_magical_creature",
            "use_innovative_approach_to_overcome_challenge",
        ]

        engagement_scores = []

        for i, choice in enumerate(engagement_choices):
            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice,
                choice_context={
                    "scenario_type": (
                        "exploration" if i % 2 == 0 else "social_interaction"
                    ),
                    "challenge_level": "moderate",
                    "turn": i + 1,
                },
            )

            # Verify enhancement is applied
            assert "engagement_score" in response
            engagement_score = response["engagement_score"]
            engagement_scores.append(engagement_score)

            # Verify engagement is reasonable
            assert engagement_score > 0.0
            assert engagement_score <= 1.0

            # Verify session progress tracks engagement
            session_progress = response["session_progress"]
            assert session_progress["engagement_score"] == engagement_score

        # Verify engagement is maintained throughout session
        average_engagement = sum(engagement_scores) / len(engagement_scores)
        assert (
            average_engagement > 0.5
        ), "Average engagement should be maintained above 0.5"

        # Verify no dramatic drops in engagement
        for i in range(1, len(engagement_scores)):
            engagement_drop = engagement_scores[i - 1] - engagement_scores[i]
            assert (
                engagement_drop < 0.5
            ), f"Engagement should not drop dramatically between choices: {engagement_scores}"

    @pytest.mark.asyncio
    async def test_adventure_enhancement_performance_impact(
        self, auto_enhanced_gameplay
    ):
        """Test that automatic adventure enhancement doesn't significantly impact performance."""
        systems = auto_enhanced_gameplay
        gameplay = systems["gameplay_controller"]

        user_id = "performance_impact_user"

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["performance_testing"],
        )
        session_id = session_state.session_id

        # Test processing times with enhancement
        processing_times = []

        for i in range(5):
            start_time = time.perf_counter()
            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=f"enhanced_performance_test_choice_{i}",
                choice_context={"performance_test": True},
            )
            processing_time = (time.perf_counter() - start_time) * 1000
            processing_times.append(processing_time)

            # Verify enhancement was applied
            assert "engagement_score" in response
            assert "narrative_response" in response

            # Verify processing time is acceptable
            assert (
                processing_time < 1000.0
            ), f"Processing with enhancement took {processing_time:.2f}ms, should be under 1000ms"

        # Verify consistent performance
        avg_processing_time = sum(processing_times) / len(processing_times)
        assert (
            avg_processing_time < 500.0
        ), f"Average processing time {avg_processing_time:.2f}ms should be under 500ms"

    @pytest.mark.asyncio
    async def test_adventure_enhancement_error_handling(self, auto_enhanced_gameplay):
        """Test that errors in adventure enhancement don't break the therapeutic system."""
        systems = auto_enhanced_gameplay
        gameplay = systems["gameplay_controller"]

        user_id = "error_handling_user"

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["error_handling_testing"],
        )
        session_id = session_state.session_id

        # Test with potentially problematic input
        problematic_choices = [
            "",  # Empty choice
            "a" * 1000,  # Very long choice
            "choice_with_special_chars_!@#$%^&*()",
            "choice\nwith\nnewlines",
            "choice with unicode: 🎮🎯🎲",
        ]

        for choice in problematic_choices:
            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice,
                choice_context={"error_test": True},
            )

            # Verify basic therapeutic response is always present
            assert response["choice_processed"] is True
            assert "safety_assessment" in response
            assert "consequence" in response
            assert "session_progress" in response

            # Adventure enhancement might fail, but basic response should work
            # If enhancement succeeded, verify it's present
            if "engagement_score" in response:
                assert response["engagement_score"] >= 0.0
                assert response["engagement_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_system_health_with_adventure_enhancement(
        self, auto_enhanced_gameplay
    ):
        """Test that system health includes adventure enhancement status."""
        systems = auto_enhanced_gameplay
        gameplay = systems["gameplay_controller"]
        adventure_enhancer = systems["adventure_enhancer"]

        # Check gameplay controller health
        gameplay_health = await gameplay.health_check()

        assert gameplay_health["status"] in ["healthy", "degraded"]
        assert "therapeutic_systems" in gameplay_health

        # Verify adventure enhancer is included in system status
        therapeutic_systems = gameplay_health["therapeutic_systems"]
        assert "adventure_enhancer" in therapeutic_systems
        assert therapeutic_systems["adventure_enhancer"] is True

        # Verify system count includes adventure enhancer
        systems_available = gameplay_health["systems_available"]
        assert "6" in systems_available  # Should be X/6 now instead of X/5

        # Check adventure enhancer health directly
        enhancer_health = await adventure_enhancer.health_check()
        assert enhancer_health["status"] == "healthy"
        assert enhancer_health["ready_for_adventure_enhancement"] is True
