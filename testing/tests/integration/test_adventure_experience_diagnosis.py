"""
Adventure Experience Diagnosis Tests

This module diagnoses and tests the core adventure experience issues,
focusing on identifying problems and validating fixes.
"""

import time

import pytest
import pytest_asyncio

from src.components.therapeutic_systems import (
    TherapeuticAdaptiveDifficultyEngine,
    TherapeuticCharacterDevelopmentSystem,
    TherapeuticConsequenceSystem,
    TherapeuticEmotionalSafetySystem,
    TherapeuticGameplayLoopController,
)


class TestAdventureExperienceDiagnosis:
    """Diagnose and test adventure experience issues."""

    @pytest_asyncio.fixture
    async def basic_adventure_setup(self):
        """Create basic adventure setup for diagnosis."""
        # Initialize core systems
        gameplay_controller = TherapeuticGameplayLoopController()
        character_system = TherapeuticCharacterDevelopmentSystem()
        consequence_system = TherapeuticConsequenceSystem()
        safety_system = TherapeuticEmotionalSafetySystem()
        difficulty_engine = TherapeuticAdaptiveDifficultyEngine()

        # Initialize systems
        await gameplay_controller.initialize()
        await character_system.initialize()
        await consequence_system.initialize()
        await safety_system.initialize()
        await difficulty_engine.initialize()

        # Inject systems into gameplay controller
        gameplay_controller.inject_therapeutic_systems(
            consequence_system=consequence_system,
            emotional_safety_system=safety_system,
            adaptive_difficulty_engine=difficulty_engine,
            character_development_system=character_system,
            therapeutic_integration_system=None,  # Test without integration first
        )

        yield {
            "gameplay_controller": gameplay_controller,
            "character_system": character_system,
            "consequence_system": consequence_system,
            "safety_system": safety_system,
            "difficulty_engine": difficulty_engine,
        }

    @pytest.mark.asyncio
    async def test_diagnose_basic_adventure_flow(self, basic_adventure_setup):
        """Diagnose basic adventure flow issues."""
        systems = basic_adventure_setup
        gameplay = systems["gameplay_controller"]

        user_id = "diagnosis_user"

        # Test 1: Session Creation
        print("\n=== DIAGNOSING SESSION CREATION ===")
        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["diagnosis_test"],
        )

        assert session_state is not None, "Session creation failed"
        print(f"✓ Session created: {session_state.session_id}")
        print(f"✓ Session status: {session_state.status}")
        print(f"✓ Session phase: {session_state.current_phase}")

        session_id = session_state.session_id

        # Test 2: Session Status Check
        print("\n=== DIAGNOSING SESSION STATUS ===")
        status = await gameplay.get_session_status(session_id)
        assert status is not None, "Session status retrieval failed"
        print(f"✓ Status retrieved: {status}")

        # Test 3: Choice Processing
        print("\n=== DIAGNOSING CHOICE PROCESSING ===")
        response = await gameplay.process_user_choice(
            session_id=session_id,
            user_choice="diagnostic_choice",
            choice_context={"diagnosis": True}
        )

        assert response["choice_processed"] is True, "Choice processing failed"
        print("✓ Choice processed successfully")
        print(f"✓ Response keys: {list(response.keys())}")

        # Diagnose response structure
        print("\n=== DIAGNOSING RESPONSE STRUCTURE ===")
        if "session_progress" in response:
            progress = response["session_progress"]
            print(f"✓ Session progress: {progress}")
            print(f"  - Therapeutic value: {progress.get('therapeutic_value', 'MISSING')}")
            print(f"  - Engagement score: {progress.get('engagement_score', 'MISSING')}")
        else:
            print("✗ Missing session_progress in response")

        if "safety_assessment" in response:
            safety = response["safety_assessment"]
            print(f"✓ Safety assessment: {safety}")
        else:
            print("✗ Missing safety_assessment in response")

        if "consequence" in response:
            consequence = response["consequence"]
            print(f"✓ Consequence: {consequence}")
        else:
            print("✗ Missing consequence in response")

        if "therapeutic_integration" in response:
            integration = response["therapeutic_integration"]
            print(f"✓ Therapeutic integration: {integration}")
        else:
            print("✗ Missing therapeutic_integration in response")

        # Test 4: System Health
        print("\n=== DIAGNOSING SYSTEM HEALTH ===")
        health = await gameplay.health_check()
        print(f"✓ Gameplay controller health: {health}")

        character_health = await systems["character_system"].health_check()
        print(f"✓ Character system health: {character_health}")

        safety_health = await systems["safety_system"].health_check()
        print(f"✓ Safety system health: {safety_health}")

    @pytest.mark.asyncio
    async def test_diagnose_engagement_issues(self, basic_adventure_setup):
        """Diagnose engagement scoring issues."""
        systems = basic_adventure_setup
        gameplay = systems["gameplay_controller"]

        user_id = "engagement_diagnosis_user"

        print("\n=== DIAGNOSING ENGAGEMENT ISSUES ===")

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["engagement_testing"],
        )
        session_id = session_state.session_id

        # Test multiple choices and track engagement
        engagement_choices = [
            "exciting_adventure_choice",
            "challenging_puzzle_choice",
            "emotional_story_choice",
            "creative_solution_choice",
        ]

        for i, choice in enumerate(engagement_choices):
            print(f"\n--- Processing choice {i+1}: {choice} ---")

            response = await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=choice,
                choice_context={"engagement_test": True, "choice_number": i+1}
            )

            if "session_progress" in response:
                progress = response["session_progress"]
                engagement_score = progress.get("engagement_score", 0.0)
                therapeutic_value = progress.get("therapeutic_value", 0.0)

                print(f"  Engagement score: {engagement_score}")
                print(f"  Therapeutic value: {therapeutic_value}")

                if engagement_score == 0.0:
                    print("  ⚠️  ISSUE: Engagement score is 0.0")
                    print("  This suggests engagement calculation is not implemented")

                if therapeutic_value == 0.0:
                    print("  ⚠️  ISSUE: Therapeutic value is 0.0")
                    print("  This suggests therapeutic value calculation needs improvement")
            else:
                print("  ✗ Missing session_progress in response")

    @pytest.mark.asyncio
    async def test_diagnose_character_development_issues(self, basic_adventure_setup):
        """Diagnose character development integration issues."""
        systems = basic_adventure_setup
        gameplay = systems["gameplay_controller"]
        character_system = systems["character_system"]

        user_id = "character_diagnosis_user"

        print("\n=== DIAGNOSING CHARACTER DEVELOPMENT ISSUES ===")

        # Test character creation
        print("\n--- Testing Character Creation ---")
        try:
            character = await character_system.create_character(
                user_id=user_id,
                therapeutic_goals=["character_testing"],
                character_name="DiagnosisHero"
            )
            print(f"✓ Character created: {character.character_id}")
            print(f"✓ Character name: {character.name}")
            print(f"✓ Character attributes: {character.attributes}")
        except Exception as e:
            print(f"✗ Character creation failed: {e}")

        # Test character summary
        print("\n--- Testing Character Summary ---")
        try:
            summary = await character_system.get_character_summary(user_id)
            print("✓ Character summary retrieved")
            print(f"  Keys: {list(summary.keys())}")

            if "error" in summary:
                print(f"  ⚠️  Error in summary: {summary['error']}")

            if "attributes" in summary:
                print(f"  ✓ Attributes found: {summary['attributes']}")
            else:
                print("  ✗ No attributes in summary")

        except Exception as e:
            print(f"✗ Character summary failed: {e}")

        # Test character development through gameplay
        print("\n--- Testing Character Development Through Gameplay ---")
        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["character_development"],
        )
        session_id = session_state.session_id

        response = await gameplay.process_user_choice(
            session_id=session_id,
            user_choice="character_growth_choice",
            choice_context={"character_development": True}
        )

        if "character_update" in response:
            character_update = response["character_update"]
            print(f"✓ Character update in response: {character_update}")

            if character_update.get("character_updated", False):
                print("  ✓ Character was updated")
            else:
                print("  ⚠️  Character was not updated")
                print(f"  Reason: {character_update.get('error', 'Unknown')}")
        else:
            print("  ✗ No character_update in response")

    @pytest.mark.asyncio
    async def test_diagnose_therapeutic_integration_issues(self, basic_adventure_setup):
        """Diagnose therapeutic integration issues."""
        systems = basic_adventure_setup
        gameplay = systems["gameplay_controller"]

        user_id = "integration_diagnosis_user"

        print("\n=== DIAGNOSING THERAPEUTIC INTEGRATION ISSUES ===")

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["anxiety_management", "confidence_building"],
        )
        session_id = session_state.session_id

        # Test therapeutic integration response
        response = await gameplay.process_user_choice(
            session_id=session_id,
            user_choice="therapeutic_choice",
            choice_context={
                "therapeutic_focus": "anxiety_management",
                "scenario": "social_situation"
            }
        )

        if "therapeutic_integration" in response:
            integration = response["therapeutic_integration"]
            print(f"✓ Therapeutic integration in response: {integration}")

            # Check for expected integration fields
            expected_fields = [
                "therapeutic_alignment",
                "goal_progress",
                "framework_applied",
                "therapeutic_value"
            ]

            for field in expected_fields:
                if field in integration:
                    print(f"  ✓ {field}: {integration[field]}")
                else:
                    print(f"  ⚠️  Missing {field}")

            if integration.get("therapeutic_integration", True) is False:
                print(f"  ⚠️  Integration failed: {integration.get('reason', 'Unknown')}")
        else:
            print("  ✗ No therapeutic_integration in response")
            print("  This indicates the therapeutic integration system is not connected")

    @pytest.mark.asyncio
    async def test_diagnose_performance_issues(self, basic_adventure_setup):
        """Diagnose performance issues in adventure systems."""
        systems = basic_adventure_setup
        gameplay = systems["gameplay_controller"]

        user_id = "performance_diagnosis_user"

        print("\n=== DIAGNOSING PERFORMANCE ISSUES ===")

        # Test session startup performance
        print("\n--- Testing Session Startup Performance ---")
        start_time = time.perf_counter()
        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["performance_testing"],
        )
        startup_time = (time.perf_counter() - start_time) * 1000

        print(f"Session startup time: {startup_time:.2f}ms")
        if startup_time > 1000:
            print("  ⚠️  Startup time exceeds 1000ms - may impact user experience")
        elif startup_time > 500:
            print("  ⚠️  Startup time exceeds 500ms - room for improvement")
        else:
            print("  ✓ Startup time is acceptable")

        session_id = session_state.session_id

        # Test choice processing performance
        print("\n--- Testing Choice Processing Performance ---")
        processing_times = []

        for i in range(3):
            start_time = time.perf_counter()
            await gameplay.process_user_choice(
                session_id=session_id,
                user_choice=f"performance_test_choice_{i}",
                choice_context={"performance_test": True}
            )
            processing_time = (time.perf_counter() - start_time) * 1000
            processing_times.append(processing_time)

            print(f"Choice {i+1} processing time: {processing_time:.2f}ms")

            if processing_time > 500:
                print("  ⚠️  Choice processing time exceeds 500ms")
            elif processing_time > 200:
                print("  ⚠️  Choice processing time exceeds 200ms")

        avg_time = sum(processing_times) / len(processing_times)
        print(f"\nAverage processing time: {avg_time:.2f}ms")

        if avg_time > 300:
            print("  ⚠️  Average processing time may impact user experience")
        else:
            print("  ✓ Average processing time is acceptable")

    @pytest.mark.asyncio
    async def test_identify_missing_adventure_features(self, basic_adventure_setup):
        """Identify missing adventure features that impact engagement."""
        systems = basic_adventure_setup
        gameplay = systems["gameplay_controller"]

        user_id = "feature_diagnosis_user"

        print("\n=== IDENTIFYING MISSING ADVENTURE FEATURES ===")

        session_state = await gameplay.start_session(
            user_id=user_id,
            therapeutic_goals=["feature_testing"],
        )
        session_id = session_state.session_id

        response = await gameplay.process_user_choice(
            session_id=session_id,
            user_choice="adventure_feature_test",
            choice_context={"feature_test": True}
        )

        # Check for adventure-specific features
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

        for feature in adventure_features:
            if feature in response:
                print(f"  ✓ {feature}: Present")
            else:
                print(f"  ✗ {feature}: Missing")
                missing_features.append(feature)

        if missing_features:
            print(f"\n⚠️  Missing adventure features: {missing_features}")
            print("These features are important for creating an engaging adventure experience")
        else:
            print("\n✓ All expected adventure features are present")

        return missing_features
