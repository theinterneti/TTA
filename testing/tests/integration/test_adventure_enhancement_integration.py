"""
Adventure Enhancement Integration Tests

This module tests the integration of the adventure enhancement system
with the therapeutic gaming platform.
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


class TestAdventureEnhancementIntegration:
    """Test adventure enhancement system integration."""

    @pytest_asyncio.fixture
    async def enhanced_adventure_systems(self):
        """Create adventure systems with enhancement integration."""
        # Initialize core systems
        gameplay_controller = TherapeuticGameplayLoopController()
        character_system = TherapeuticCharacterDevelopmentSystem()
        consequence_system = TherapeuticConsequenceSystem()
        safety_system = TherapeuticEmotionalSafetySystem()
        difficulty_engine = TherapeuticAdaptiveDifficultyEngine()

        # Initialize adventure enhancement system
        adventure_enhancer = AdventureEnhancementSystem()

        # Initialize all systems
        await gameplay_controller.initialize()
        await character_system.initialize()
        await consequence_system.initialize()
        await safety_system.initialize()
        await difficulty_engine.initialize()
        await adventure_enhancer.initialize()

        # Inject systems into gameplay controller
        gameplay_controller.inject_therapeutic_systems(
            consequence_system=consequence_system,
            emotional_safety_system=safety_system,
            adaptive_difficulty_engine=difficulty_engine,
            character_development_system=character_system,
            therapeutic_integration_system=None,
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
    async def test_adventure_enhancement_integration(self, enhanced_adventure_systems):
        """Test that adventure enhancement integrates with therapeutic systems."""
        systems = enhanced_adventure_systems
        gameplay = systems["gameplay_controller"]
        enhancer = systems["adventure_enhancer"]

        user_id = "enhanced_adventure_user"

        # Start session
        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["adventure_enhancement_testing"],
        )
        session_id = session_state.session_id

        # Process choice and get base response
        base_response = await gameplay.process_user_choice(
            session_id=session_id,
            user_choice="explore_the_magical_forest_with_courage",
            choice_context={
                "adventure_theme": "fantasy_quest",
                "scenario_type": "exploration",
                "challenge_level": "moderate",
            }
        )

        # Enhance the response with adventure elements
        enhanced_response = enhancer.enhance_choice_response(
            session_id=session_id,
            user_choice="explore_the_magical_forest_with_courage",
            choice_context={
                "adventure_theme": "fantasy_quest",
                "scenario_type": "exploration",
                "challenge_level": "moderate",
            },
            base_response=base_response
        )

        # Verify enhancement worked
        assert "engagement_score" in enhanced_response
        assert enhanced_response["engagement_score"] > 0.0

        # Verify adventure features are present
        adventure_features = [
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
            assert feature in enhanced_response, f"Missing adventure feature: {feature}"

        # Verify narrative response is rich
        narrative = enhanced_response["narrative_response"]
        assert len(narrative) > 50, "Narrative response should be rich and detailed"
        assert "magical" in narrative.lower() or "forest" in narrative.lower()

        # Verify world state changes
        world_changes = enhanced_response["world_state_changes"]
        assert isinstance(world_changes, list)

        # Verify exploration opportunities
        exploration = enhanced_response["exploration_opportunities"]
        assert isinstance(exploration, list)
        assert len(exploration) > 0, "Should provide exploration opportunities"

        # Verify story context
        story_context = enhanced_response["story_context"]
        assert "theme" in story_context
        assert story_context["theme"] == "fantasy_quest"

        # Verify immersive elements
        immersion = enhanced_response["immersive_elements"]
        assert isinstance(immersion, list)
        assert len(immersion) > 0, "Should provide immersive elements"

    @pytest.mark.asyncio
    async def test_engagement_score_calculation(self, enhanced_adventure_systems):
        """Test that engagement scores are calculated correctly."""
        systems = enhanced_adventure_systems
        gameplay = systems["gameplay_controller"]
        enhancer = systems["adventure_enhancer"]

        user_id = "engagement_test_user"

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["engagement_testing"],
        )
        session_id = session_state.session_id

        # Test different types of choices and their engagement scores
        test_choices = [
            {
                "choice": "help_villager_with_creative_solution",
                "context": {"scenario_type": "social_interaction", "challenge_level": "moderate"},
                "expected_min_engagement": 0.6,
            },
            {
                "choice": "explore_mysterious_ancient_ruins_carefully",
                "context": {"scenario_type": "exploration", "challenge_level": "hard"},
                "expected_min_engagement": 0.7,
            },
            {
                "choice": "use_innovative_magic_to_solve_puzzle",
                "context": {"scenario_type": "problem_solving", "challenge_level": "expert"},
                "expected_min_engagement": 0.8,
            },
        ]

        for test_choice in test_choices:
            # Get base response
            base_response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=test_choice["choice"],
                choice_context=test_choice["context"]
            )

            # Enhance response
            enhanced_response = enhancer.enhance_choice_response(
                session_id=session_id,
                user_choice=test_choice["choice"],
                choice_context=test_choice["context"],
                base_response=base_response
            )

            # Verify engagement score
            engagement_score = enhanced_response["engagement_score"]
            assert engagement_score >= test_choice["expected_min_engagement"]
            assert engagement_score <= 1.0

            # Verify engagement is reflected in session progress
            if "session_progress" in enhanced_response:
                session_engagement = enhanced_response["session_progress"]["engagement_score"]
                assert session_engagement == engagement_score

    @pytest.mark.asyncio
    async def test_adventure_theme_consistency(self, enhanced_adventure_systems):
        """Test that adventure themes are consistent throughout the experience."""
        systems = enhanced_adventure_systems
        gameplay = systems["gameplay_controller"]
        enhancer = systems["adventure_enhancer"]

        user_id = "theme_consistency_user"

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["theme_testing"],
        )
        session_id = session_state.session_id

        # Test fantasy quest theme
        fantasy_choices = [
            "cast_healing_spell_on_wounded_companion",
            "negotiate_with_dragon_using_ancient_wisdom",
            "explore_enchanted_forest_for_magical_herbs",
        ]

        for choice in fantasy_choices:
            base_response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice,
                choice_context={"adventure_theme": "fantasy_quest"}
            )

            enhanced_response = enhancer.enhance_choice_response(
                session_id=session_id,
                user_choice=choice,
                choice_context={"adventure_theme": "fantasy_quest"},
                base_response=base_response
            )

            # Verify fantasy theme consistency
            story_context = enhanced_response["story_context"]
            assert story_context["theme"] == "fantasy_quest"

            narrative = enhanced_response["narrative_response"].lower()
            fantasy_keywords = ["magic", "mystical", "ancient", "realm", "enchanted"]
            assert any(keyword in narrative for keyword in fantasy_keywords), \
                f"Fantasy narrative should contain fantasy elements: {narrative}"

            # Verify immersive elements match theme
            immersion = enhanced_response["immersive_elements"]
            immersion_text = " ".join(immersion).lower()
            assert any(keyword in immersion_text for keyword in fantasy_keywords), \
                "Immersive elements should match fantasy theme"

    @pytest.mark.asyncio
    async def test_adventure_progression_tracking(self, enhanced_adventure_systems):
        """Test that adventure progression is tracked correctly."""
        systems = enhanced_adventure_systems
        gameplay = systems["gameplay_controller"]
        enhancer = systems["adventure_enhancer"]

        user_id = "progression_test_user"

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["progression_testing"],
        )
        session_id = session_state.session_id

        # Process multiple choices and track progression
        progression_choices = [
            "help_first_villager",
            "explore_nearby_cave",
            "solve_ancient_riddle",
            "form_alliance_with_mentor",
            "complete_heroic_quest",
        ]

        previous_progression = 0.0

        for i, choice in enumerate(progression_choices):
            base_response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice,
                choice_context={"progression_step": i + 1}
            )

            enhanced_response = enhancer.enhance_choice_response(
                session_id=session_id,
                user_choice=choice,
                choice_context={"progression_step": i + 1},
                base_response=base_response
            )

            # Verify progression tracking
            adventure_progression = enhanced_response["adventure_progression"]
            assert "story_completion" in adventure_progression

            current_progression = adventure_progression["story_completion"]
            assert current_progression >= previous_progression, \
                "Story progression should increase or stay the same"

            # Verify other progression metrics
            assert "areas_explored" in adventure_progression
            assert "relationships_formed" in adventure_progression
            assert "world_impact_score" in adventure_progression

            previous_progression = current_progression

    @pytest.mark.asyncio
    async def test_adventure_enhancement_performance(self, enhanced_adventure_systems):
        """Test that adventure enhancement doesn't significantly impact performance."""
        systems = enhanced_adventure_systems
        gameplay = systems["gameplay_controller"]
        enhancer = systems["adventure_enhancer"]

        user_id = "performance_test_user"

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["performance_testing"],
        )
        session_id = session_state.session_id

        # Test enhancement performance
        enhancement_times = []

        for i in range(5):
            # Get base response
            base_response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=f"performance_test_choice_{i}",
                choice_context={"performance_test": True}
            )

            # Time the enhancement
            start_time = time.perf_counter()
            enhanced_response = enhancer.enhance_choice_response(
                session_id=session_id,
                user_choice=f"performance_test_choice_{i}",
                choice_context={"performance_test": True},
                base_response=base_response
            )
            enhancement_time = (time.perf_counter() - start_time) * 1000
            enhancement_times.append(enhancement_time)

            # Verify enhancement worked
            assert "engagement_score" in enhanced_response
            assert enhanced_response["engagement_score"] > 0.0

            # Verify performance is acceptable
            assert enhancement_time < 100.0, f"Enhancement took {enhancement_time:.2f}ms, should be under 100ms"

        # Verify consistent performance
        avg_enhancement_time = sum(enhancement_times) / len(enhancement_times)
        assert avg_enhancement_time < 50.0, f"Average enhancement time {avg_enhancement_time:.2f}ms should be under 50ms"

    @pytest.mark.asyncio
    async def test_adventure_enhancement_system_health(self, enhanced_adventure_systems):
        """Test that adventure enhancement system reports healthy status."""
        systems = enhanced_adventure_systems
        enhancer = systems["adventure_enhancer"]

        # Check system health
        health = await enhancer.health_check()

        assert health["status"] == "healthy"
        assert "adventure_contexts_active" in health
        assert "engagement_metrics_tracked" in health
        assert "narrative_templates_loaded" in health
        assert health["narrative_templates_loaded"] > 0
        assert health["ready_for_adventure_enhancement"] is True
        assert "metrics" in health

        # Verify metrics are being tracked
        metrics = health["metrics"]
        expected_metrics = [
            "adventures_enhanced",
            "engagement_calculations",
            "narrative_responses_generated",
            "world_state_updates",
            "exploration_opportunities_created",
        ]

        for metric in expected_metrics:
            assert metric in metrics
