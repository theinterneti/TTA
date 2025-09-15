"""
Final Adventure Experience Validation Tests

This module validates that all adventure experience issues have been resolved
and that the therapeutic gaming platform now provides an engaging, immersive,
and therapeutically effective adventure experience.
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


class TestFinalAdventureExperienceValidation:
    """Final validation of the complete adventure experience."""

    @pytest_asyncio.fixture
    async def complete_adventure_system(self):
        """Create complete adventure system with all enhancements."""
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
    async def test_all_adventure_features_now_present(self, complete_adventure_system):
        """Test that all previously missing adventure features are now present."""
        systems = complete_adventure_system
        gameplay = systems["gameplay_controller"]

        user_id = "final_validation_user"

        print("\n=== FINAL ADVENTURE EXPERIENCE VALIDATION ===")

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["final_validation"],
        )
        session_id = session_state.session_id

        response = await gameplay.process_user_choice(
            session_id=session_id,
            user_choice="embark_on_epic_adventure_with_courage_and_wisdom",
            choice_context={
                "adventure_theme": "fantasy_quest",
                "scenario_type": "exploration",
                "challenge_level": "moderate",
            }
        )

        # Check for all adventure features that were previously missing
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

        print("\n--- Checking for Adventure Features ---")
        missing_features = []
        present_features = []

        for feature in adventure_features:
            if feature in response:
                print(f"  ✓ {feature}: Present")
                present_features.append(feature)
            else:
                print(f"  ✗ {feature}: Missing")
                missing_features.append(feature)

        # Verify all features are now present
        assert len(missing_features) == 0, f"Missing adventure features: {missing_features}"
        assert len(present_features) == len(adventure_features), "All adventure features should be present"

        print(f"\n✅ SUCCESS: All {len(adventure_features)} adventure features are now present!")

        return present_features

    @pytest.mark.asyncio
    async def test_engagement_score_now_calculated(self, complete_adventure_system):
        """Test that engagement scores are now properly calculated (was 0.0 before)."""
        systems = complete_adventure_system
        gameplay = systems["gameplay_controller"]

        user_id = "engagement_validation_user"

        print("\n=== ENGAGEMENT SCORE VALIDATION ===")

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["engagement_validation"],
        )
        session_id = session_state.session_id

        # Test different types of engaging choices
        engaging_choices = [
            {
                "choice": "creatively_solve_ancient_puzzle_with_innovative_thinking",
                "context": {"scenario_type": "problem_solving", "challenge_level": "hard"},
                "expected_min": 0.7,
            },
            {
                "choice": "explore_mysterious_enchanted_forest_with_curiosity",
                "context": {"scenario_type": "exploration", "challenge_level": "moderate"},
                "expected_min": 0.6,
            },
            {
                "choice": "help_villagers_with_empathy_and_wisdom",
                "context": {"scenario_type": "social_interaction", "challenge_level": "moderate"},
                "expected_min": 0.6,
            },
        ]

        engagement_scores = []

        for i, choice_data in enumerate(engaging_choices):
            print(f"\n--- Testing Choice {i+1}: {choice_data['choice'][:50]}... ---")

            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice_data["choice"],
                choice_context=choice_data["context"]
            )

            # Verify engagement score is present and calculated
            assert "engagement_score" in response, "Engagement score should be present"
            engagement_score = response["engagement_score"]
            engagement_scores.append(engagement_score)

            print(f"  Engagement score: {engagement_score:.3f}")

            # Verify engagement score is not 0.0 (the previous issue)
            assert engagement_score > 0.0, "Engagement score should not be 0.0"
            assert engagement_score <= 1.0, "Engagement score should not exceed 1.0"

            # Verify it meets minimum expectations for engaging choices
            assert engagement_score >= choice_data["expected_min"] * 0.8, \
                f"Engagement score {engagement_score} should be at least {choice_data['expected_min'] * 0.8}"

            # Verify session progress includes engagement
            session_progress = response["session_progress"]
            assert session_progress["engagement_score"] == engagement_score

        average_engagement = sum(engagement_scores) / len(engagement_scores)
        print(f"\n✅ SUCCESS: Average engagement score is {average_engagement:.3f} (was 0.0 before)")

        assert average_engagement > 0.5, "Average engagement should be above 0.5 for engaging choices"

    @pytest.mark.asyncio
    async def test_narrative_richness_and_immersion(self, complete_adventure_system):
        """Test that narrative responses are rich, immersive, and contextual."""
        systems = complete_adventure_system
        gameplay = systems["gameplay_controller"]

        user_id = "narrative_validation_user"

        print("\n=== NARRATIVE RICHNESS VALIDATION ===")

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["narrative_validation"],
        )
        session_id = session_state.session_id

        response = await gameplay.process_user_choice(
            session_id=session_id,
            user_choice="approach_the_ancient_dragon_with_respect_and_wisdom",
            choice_context={
                "adventure_theme": "fantasy_quest",
                "scenario_type": "social_interaction",
                "emotional_tone": "respectful",
            }
        )

        # Verify narrative response quality
        narrative = response["narrative_response"]
        print(f"\nNarrative Response: {narrative}")

        assert len(narrative) > 50, "Narrative should be detailed and rich"
        assert any(keyword in narrative.lower() for keyword in ["mystical", "ancient", "dragon", "wisdom", "respect"]), \
            "Narrative should be contextually relevant"

        # Verify immersive elements
        immersive_elements = response["immersive_elements"]
        print(f"Immersive Elements: {immersive_elements}")

        assert len(immersive_elements) > 0, "Should provide immersive elements"
        assert all(len(element) > 10 for element in immersive_elements), "Immersive elements should be descriptive"

        # Verify flavor text if present
        if "flavor_text" in response:
            flavor_text = response["flavor_text"]
            print(f"Flavor Text: {flavor_text}")
            assert len(flavor_text) > 10, "Flavor text should be meaningful"

        print("\n✅ SUCCESS: Narrative responses are now rich and immersive!")

    @pytest.mark.asyncio
    async def test_world_building_and_progression(self, complete_adventure_system):
        """Test that world building and adventure progression work correctly."""
        systems = complete_adventure_system
        gameplay = systems["gameplay_controller"]

        user_id = "world_building_user"

        print("\n=== WORLD BUILDING VALIDATION ===")

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["world_building_validation"],
        )
        session_id = session_state.session_id

        # Process multiple choices to build the world
        world_building_choices = [
            "help_the_village_elder_with_ancient_wisdom",
            "explore_the_mysterious_crystal_caves",
            "solve_the_riddle_of_the_forgotten_temple",
        ]

        progressions = []

        for i, choice in enumerate(world_building_choices):
            print(f"\n--- Choice {i+1}: {choice} ---")

            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice,
                choice_context={"world_building": True}
            )

            # Verify world state changes
            world_changes = response["world_state_changes"]
            print(f"World Changes: {world_changes}")
            assert isinstance(world_changes, list), "World changes should be a list"

            # Verify adventure progression
            adventure_progression = response["adventure_progression"]
            print(f"Adventure Progression: {adventure_progression}")
            assert "story_completion" in adventure_progression
            assert "areas_explored" in adventure_progression
            assert "world_impact_score" in adventure_progression

            progressions.append(adventure_progression["story_completion"])

            # Verify story context
            story_context = response["story_context"]
            print(f"Story Context: {story_context}")
            assert "theme" in story_context
            assert "current_location" in story_context
            assert "story_progression" in story_context

        # Verify progression over time
        assert progressions[-1] >= progressions[0], "Story progression should advance"

        print("\n✅ SUCCESS: World building and progression systems are working!")

    @pytest.mark.asyncio
    async def test_therapeutic_value_maintained_with_adventure(self, complete_adventure_system):
        """Test that therapeutic value is maintained while adding adventure elements."""
        systems = complete_adventure_system
        gameplay = systems["gameplay_controller"]

        user_id = "therapeutic_balance_user"

        print("\n=== THERAPEUTIC VALUE BALANCE VALIDATION ===")

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["anxiety_management", "confidence_building"],
        )
        session_id = session_state.session_id

        therapeutic_choices = [
            {
                "choice": "face_the_scary_dragon_with_gradual_courage_building",
                "therapeutic_focus": "anxiety_management",
            },
            {
                "choice": "lead_the_village_celebration_with_growing_confidence",
                "therapeutic_focus": "confidence_building",
            },
            {
                "choice": "practice_mindful_breathing_while_exploring_peaceful_garden",
                "therapeutic_focus": "anxiety_management",
            },
        ]

        total_therapeutic_value = 0.0
        total_engagement = 0.0

        for choice_data in therapeutic_choices:
            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice_data["choice"],
                choice_context=choice_data
            )

            # Verify therapeutic value is present
            therapeutic_value = response["session_progress"]["therapeutic_value"]
            engagement_score = response["engagement_score"]

            print(f"Choice: {choice_data['choice'][:50]}...")
            print(f"  Therapeutic Value: {therapeutic_value:.3f}")
            print(f"  Engagement Score: {engagement_score:.3f}")

            assert therapeutic_value > 0.0, "Therapeutic value should be maintained"
            assert engagement_score > 0.0, "Engagement should be present"

            total_therapeutic_value += therapeutic_value
            total_engagement += engagement_score

        # Verify both therapeutic value and engagement are maintained
        avg_therapeutic = total_therapeutic_value / len(therapeutic_choices)
        avg_engagement = total_engagement / len(therapeutic_choices)

        print(f"\nAverage Therapeutic Value: {avg_therapeutic:.3f}")
        print(f"Average Engagement Score: {avg_engagement:.3f}")

        assert avg_therapeutic > 0.5, "Average therapeutic value should be significant"
        assert avg_engagement > 0.5, "Average engagement should be significant"

        print("\n✅ SUCCESS: Therapeutic value is maintained while adding engaging adventure elements!")

    @pytest.mark.asyncio
    async def test_performance_with_adventure_enhancement(self, complete_adventure_system):
        """Test that performance remains acceptable with adventure enhancement."""
        systems = complete_adventure_system
        gameplay = systems["gameplay_controller"]

        user_id = "performance_validation_user"

        print("\n=== PERFORMANCE VALIDATION ===")

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["performance_validation"],
        )
        session_id = session_state.session_id

        # Test processing times
        processing_times = []

        for i in range(5):
            start_time = time.perf_counter()
            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=f"enhanced_adventure_choice_with_rich_narrative_{i}",
                choice_context={"performance_test": True}
            )
            processing_time = (time.perf_counter() - start_time) * 1000
            processing_times.append(processing_time)

            # Verify enhancement was applied
            assert "engagement_score" in response
            assert "narrative_response" in response
            assert len(response["narrative_response"]) > 30

            print(f"Choice {i+1} processing time: {processing_time:.2f}ms")

        avg_time = sum(processing_times) / len(processing_times)
        max_time = max(processing_times)

        print(f"\nAverage processing time: {avg_time:.2f}ms")
        print(f"Maximum processing time: {max_time:.2f}ms")

        # Performance should be acceptable for real-time gaming
        assert avg_time < 500.0, f"Average processing time {avg_time:.2f}ms should be under 500ms"
        assert max_time < 1000.0, f"Maximum processing time {max_time:.2f}ms should be under 1000ms"

        print("\n✅ SUCCESS: Performance remains excellent with adventure enhancement!")

    @pytest.mark.asyncio
    async def test_complete_adventure_session_experience(self, complete_adventure_system):
        """Test a complete adventure session from start to finish."""
        systems = complete_adventure_system
        gameplay = systems["gameplay_controller"]

        user_id = "complete_experience_user"

        print("\n=== COMPLETE ADVENTURE EXPERIENCE VALIDATION ===")

        # Start adventure session
        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["complete_adventure_experience"],
        )
        session_id = session_state.session_id

        print(f"Started adventure session: {session_id}")

        # Complete adventure journey
        adventure_journey = [
            "begin_quest_with_determination_and_hope",
            "meet_wise_mentor_and_learn_valuable_lessons",
            "face_first_challenge_with_growing_courage",
            "help_fellow_travelers_with_compassion",
            "solve_ancient_mystery_with_creative_thinking",
            "overcome_final_obstacle_with_wisdom_and_strength",
        ]

        journey_metrics = {
            "therapeutic_values": [],
            "engagement_scores": [],
            "narrative_lengths": [],
            "world_changes": 0,
            "relationships_formed": 0,
        }

        for i, choice in enumerate(adventure_journey):
            print(f"\n--- Adventure Step {i+1}: {choice[:40]}... ---")

            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice,
                choice_context={"journey_step": i+1}
            )

            # Collect metrics
            therapeutic_value = response["session_progress"]["therapeutic_value"]
            engagement_score = response["engagement_score"]
            narrative_length = len(response["narrative_response"])

            journey_metrics["therapeutic_values"].append(therapeutic_value)
            journey_metrics["engagement_scores"].append(engagement_score)
            journey_metrics["narrative_lengths"].append(narrative_length)

            if response["world_state_changes"]:
                journey_metrics["world_changes"] += len(response["world_state_changes"])

            if response["character_relationships"]:
                journey_metrics["relationships_formed"] = len(response["character_relationships"])

            print(f"  Therapeutic Value: {therapeutic_value:.3f}")
            print(f"  Engagement Score: {engagement_score:.3f}")
            print(f"  Narrative Length: {narrative_length} characters")

        # Complete the session
        outcome = await gameplay.complete_session(session_id)

        print("\n--- Session Completed ---")
        print(f"Total Therapeutic Value: {outcome.therapeutic_value_total:.3f}")
        print(f"Milestones Achieved: {len(outcome.milestones_achieved)}")

        # Validate complete experience
        avg_therapeutic = sum(journey_metrics["therapeutic_values"]) / len(journey_metrics["therapeutic_values"])
        avg_engagement = sum(journey_metrics["engagement_scores"]) / len(journey_metrics["engagement_scores"])
        avg_narrative_length = sum(journey_metrics["narrative_lengths"]) / len(journey_metrics["narrative_lengths"])

        print("\n--- Journey Summary ---")
        print(f"Average Therapeutic Value: {avg_therapeutic:.3f}")
        print(f"Average Engagement Score: {avg_engagement:.3f}")
        print(f"Average Narrative Length: {avg_narrative_length:.0f} characters")
        print(f"World Changes Made: {journey_metrics['world_changes']}")
        print(f"Relationships Formed: {journey_metrics['relationships_formed']}")

        # Verify complete experience quality
        assert avg_therapeutic > 0.5, "Adventure should maintain high therapeutic value"
        assert avg_engagement > 0.5, "Adventure should maintain high engagement"
        assert avg_narrative_length > 50, "Narratives should be rich and detailed"
        assert outcome.therapeutic_value_total > 3.0, "Complete session should have significant therapeutic value"

        print("\n🎉 SUCCESS: Complete adventure experience is engaging, therapeutic, and immersive!")

        return {
            "session_completed": True,
            "avg_therapeutic_value": avg_therapeutic,
            "avg_engagement_score": avg_engagement,
            "total_therapeutic_value": outcome.therapeutic_value_total,
            "adventure_features_working": True,
        }
