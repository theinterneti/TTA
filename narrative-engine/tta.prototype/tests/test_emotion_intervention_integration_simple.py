"""
Simple integration test for Emotion-Intervention Integration System

This test verifies that the core integration functionality works correctly
with mock data, focusing on the main integration workflow.
"""

import sys
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent.parent / "core"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))

def test_emotion_intervention_integration():
    """Test the main emotion-intervention integration workflow."""
    print("Testing Emotion-Intervention Integration System...")

    try:
        from emotion_intervention_integration import (
            EmotionBasedInterventionSelector,
            EmotionInterventionIntegrator,
            SafeExposureTherapyManager,
        )

        # Test 1: Initialize components
        print("✓ Successfully imported integration components")

        integrator = EmotionInterventionIntegrator()
        selector = EmotionBasedInterventionSelector()
        exposure_manager = SafeExposureTherapyManager()

        print("✓ Successfully initialized integration components")

        # Test 2: Create mock emotional analysis
        class MockEmotionalAnalysis:
            def __init__(self):
                self.detected_emotion = MockEmotionalState()
                self.confidence_level = 0.8
                self.crisis_indicators = []
                self.detected_triggers = [MockTrigger()]

        class MockEmotionalState:
            def __init__(self):
                self.primary_emotion = "anxious"
                self.intensity = 0.5
                self.triggers = ["presentation"]
                self.confidence_level = 0.8

        class MockTrigger:
            def __init__(self):
                self.description = "public speaking anxiety"

        class MockSessionState:
            def __init__(self):
                self.therapeutic_progress = MockTherapeuticProgress()
                self.character_states = {}
                self.emotional_state = MockEmotionalState()

        class MockTherapeuticProgress:
            def __init__(self):
                self.overall_progress_score = 50
                self.completed_interventions = []
                self.coping_strategies_learned = ["breathing", "grounding"]

        class MockNarrativeContext:
            def __init__(self):
                self.recent_events = ["User mentioned upcoming presentation"]
                self.active_characters = []

        # Test 3: Run integration
        emotional_analysis = MockEmotionalAnalysis()
        session_state = MockSessionState()
        narrative_context = MockNarrativeContext()

        result = integrator.integrate_emotion_with_interventions(
            emotional_analysis, session_state, narrative_context
        )

        print("✓ Successfully ran emotion-intervention integration")

        # Test 4: Verify result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "selected_interventions" in result, "Result should contain selected interventions"
        assert "safety_assessment" in result, "Result should contain safety assessment"
        assert "integration_success" in result, "Result should contain integration success flag"

        print("✓ Integration result has correct structure")

        # Test 5: Test intervention selection
        interventions = selector.select_interventions(
            emotional_analysis.detected_emotion, session_state, narrative_context
        )

        assert isinstance(interventions, list), "Interventions should be a list"
        assert len(interventions) > 0, "Should select at least one intervention"

        print("✓ Intervention selection works correctly")

        # Test 6: Test exposure therapy assessment
        assessment = exposure_manager.assess_exposure_readiness(
            emotional_analysis.detected_emotion, session_state, "social anxiety"
        )

        assert isinstance(assessment, dict), "Assessment should be a dictionary"
        assert "ready" in assessment, "Assessment should contain readiness flag"
        assert "readiness_score" in assessment, "Assessment should contain readiness score"

        print("✓ Exposure therapy assessment works correctly")

        # Test 7: Test safety validation
        safety_assessment = integrator._perform_comprehensive_safety_assessment(
            emotional_analysis, session_state, narrative_context
        )

        assert isinstance(safety_assessment, dict), "Safety assessment should be a dictionary"
        assert "crisis_detected" in safety_assessment, "Should contain crisis detection"
        assert "safety_concerns" in safety_assessment, "Should contain safety concerns"

        print("✓ Safety validation works correctly")

        print("\n🎉 All integration tests passed successfully!")
        print(f"Integration success: {result['integration_success']}")
        print(f"Selected interventions: {len(result['selected_interventions'])}")
        print(f"Crisis detected: {result['safety_assessment']['crisis_detected']}")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crisis_handling():
    """Test crisis handling functionality."""
    print("\nTesting Crisis Handling...")

    try:
        from emotion_intervention_integration import EmotionInterventionIntegrator

        integrator = EmotionInterventionIntegrator()

        # Create crisis-level emotional state
        class MockCrisisAnalysis:
            def __init__(self):
                self.detected_emotion = MockCrisisEmotionalState()
                self.confidence_level = 0.9
                self.crisis_indicators = ["suicidal ideation"]
                self.detected_triggers = []

        class MockCrisisEmotionalState:
            def __init__(self):
                self.primary_emotion = "depressed"
                self.intensity = 0.9  # Crisis level
                self.triggers = ["hopelessness"]
                self.confidence_level = 0.9

        class MockSessionState:
            def __init__(self):
                self.therapeutic_progress = None
                self.character_states = {}
                self.emotional_state = MockCrisisEmotionalState()

        class MockNarrativeContext:
            def __init__(self):
                self.recent_events = ["User expressed hopelessness"]
                self.active_characters = []

        crisis_analysis = MockCrisisAnalysis()
        session_state = MockSessionState()
        narrative_context = MockNarrativeContext()

        result = integrator.integrate_emotion_with_interventions(
            crisis_analysis, session_state, narrative_context
        )

        # Verify crisis handling
        assert result["safety_assessment"]["crisis_detected"], "Should detect crisis"
        assert result["crisis_response"] is not None, "Should provide crisis response"
        assert result["integration_success"], "Crisis handling should succeed"

        print("✓ Crisis detection and handling works correctly")
        print(f"Crisis response provided: {result['crisis_response'] is not None}")

        return True

    except Exception as e:
        print(f"❌ Crisis handling test failed: {e}")
        return False

def test_exposure_therapy_safety():
    """Test exposure therapy safety mechanisms."""
    print("\nTesting Exposure Therapy Safety...")

    try:
        from emotion_intervention_integration import (
            ExposureTherapyType,
            SafeExposureTherapyManager,
        )

        manager = SafeExposureTherapyManager()

        # Test safe conditions
        class MockSafeEmotionalState:
            def __init__(self):
                self.primary_emotion = "anxious"
                self.intensity = 0.4  # Safe level
                self.triggers = ["social_situations"]

        class MockGoodProgress:
            def __init__(self):
                self.overall_progress_score = 70
                self.coping_strategies_learned = ["breathing", "grounding", "self-talk"]
                self.completed_interventions = []

        class MockSafeSessionState:
            def __init__(self):
                self.therapeutic_progress = MockGoodProgress()
                self.character_states = {}

        class MockNarrativeContext:
            def __init__(self):
                self.active_characters = []
                self.current_location = "Safe space"

        safe_state = MockSafeEmotionalState()
        safe_session = MockSafeSessionState()
        narrative_context = MockNarrativeContext()

        # Test readiness assessment
        assessment = manager.assess_exposure_readiness(
            safe_state, safe_session, "social anxiety"
        )

        print("✓ Exposure readiness assessment completed")
        print(f"Ready for exposure: {assessment['ready']}")
        print(f"Readiness score: {assessment['readiness_score']:.2f}")

        # Test session creation if ready
        if assessment["ready"]:
            session = manager.create_exposure_session(
                ExposureTherapyType.IMAGINAL,
                "social anxiety",
                safe_state,
                narrative_context
            )

            if session:
                print("✓ Exposure session created successfully")
                print(f"Session intensity: {session.exposure_intensity:.2f}")
                print(f"Safety measures: {len(session.safety_measures)}")
                print(f"Escape mechanisms: {len(session.escape_mechanisms)}")
            else:
                print("⚠ Exposure session not created (safety restrictions)")

        return True

    except Exception as e:
        print(f"❌ Exposure therapy safety test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("EMOTION-INTERVENTION INTEGRATION TESTS")
    print("=" * 60)

    all_passed = True

    # Run main integration test
    all_passed &= test_emotion_intervention_integration()

    # Run crisis handling test
    all_passed &= test_crisis_handling()

    # Run exposure therapy safety test
    all_passed &= test_exposure_therapy_safety()

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Integration system is working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Please review the implementation")
    print("=" * 60)
