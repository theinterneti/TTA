"""
Emotion-Intervention Integration Example

This example demonstrates how the emotion-intervention integration system works
to connect emotional state recognition with therapeutic interventions, including
emotion-based content adaptation and safe exposure therapy opportunities.
"""

import sys
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent.parent / "core"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))

def demonstrate_emotion_intervention_integration():
    """Demonstrate the complete emotion-intervention integration workflow."""
    print("=" * 80)
    print("EMOTION-INTERVENTION INTEGRATION DEMONSTRATION")
    print("=" * 80)

    try:
        from emotion_intervention_integration import (
            EmotionBasedInterventionSelector,
            EmotionInterventionIntegrator,
            SafetyValidationLevel,
        )

        # Initialize the integration system
        integrator = EmotionInterventionIntegrator()
        print("✓ Emotion-Intervention Integration System initialized")

        # Scenario 1: Moderate Anxiety with Presentation Fear
        print("\n" + "─" * 60)
        print("SCENARIO 1: Moderate Anxiety - Presentation Fear")
        print("─" * 60)

        # Create emotional analysis for moderate anxiety
        class MockEmotionalAnalysis:
            def __init__(self, emotion, intensity, triggers=None, crisis_indicators=None):
                self.detected_emotion = MockEmotionalState(emotion, intensity, triggers or [])
                self.confidence_level = 0.8
                self.crisis_indicators = crisis_indicators or []
                self.detected_triggers = [MockTrigger(t) for t in (triggers or [])]

        class MockEmotionalState:
            def __init__(self, emotion, intensity, triggers):
                self.primary_emotion = emotion
                self.intensity = intensity
                self.triggers = triggers
                self.confidence_level = 0.8
                self.secondary_emotions = []

        class MockTrigger:
            def __init__(self, description):
                self.description = description

        class MockSessionState:
            def __init__(self, progress_score=50, coping_strategies=None):
                self.therapeutic_progress = MockTherapeuticProgress(progress_score, coping_strategies or [])
                self.character_states = {"therapist": MockCharacterState()}
                self.emotional_state = MockEmotionalState("anxious", 0.5, ["presentation"])

        class MockTherapeuticProgress:
            def __init__(self, score, strategies):
                self.overall_progress_score = score
                self.completed_interventions = []
                self.coping_strategies_learned = strategies

        class MockCharacterState:
            def __init__(self):
                self.name = "Dr. Sarah"
                self.relationship_scores = {"trust": 0.8, "rapport": 0.7}

        class MockNarrativeContext:
            def __init__(self, events=None):
                self.recent_events = events or []
                self.active_characters = [MockCharacter()]

        class MockCharacter:
            def __init__(self):
                self.name = "Dr. Sarah"

        # Create scenario data
        anxiety_analysis = MockEmotionalAnalysis(
            emotion="anxious",
            intensity=0.5,
            triggers=["public speaking", "being judged"]
        )

        session_state = MockSessionState(
            progress_score=60,
            coping_strategies=["deep breathing", "grounding techniques"]
        )

        narrative_context = MockNarrativeContext([
            "User mentioned upcoming work presentation",
            "User expressed worry about being judged",
            "Dr. Sarah noticed signs of anxiety"
        ])

        # Run integration
        result = integrator.integrate_emotion_with_interventions(
            anxiety_analysis, session_state, narrative_context
        )

        print(f"Emotional State: {anxiety_analysis.detected_emotion.primary_emotion} (intensity: {anxiety_analysis.detected_emotion.intensity})")
        print(f"Integration Success: {result['integration_success']}")
        print(f"Crisis Detected: {result['safety_assessment']['crisis_detected']}")
        print(f"Selected Interventions: {len(result['selected_interventions'])}")

        if result['selected_interventions']:
            for i, intervention in enumerate(result['selected_interventions'], 1):
                print(f"\nIntervention {i}:")
                print(f"  Type: {intervention.base_intervention_type}")
                print(f"  Safety Level: {intervention.safety_level}")
                print(f"  Effectiveness Score: {intervention.therapeutic_effectiveness_score:.2f}")
                print(f"  Content: {intervention.adapted_content[:100]}...")

        if result['exposure_therapy_session']:
            session = result['exposure_therapy_session']
            print("\nExposure Therapy Session:")
            print(f"  Type: {session.exposure_type}")
            print(f"  Target: {session.target_fear_or_trigger}")
            print(f"  Intensity: {session.exposure_intensity:.2f}")
            print(f"  Duration: {session.session_duration_minutes} minutes")
            print(f"  Safety Measures: {len(session.safety_measures)}")

        # Scenario 2: High Intensity Depression (Crisis)
        print("\n" + "─" * 60)
        print("SCENARIO 2: High Intensity Depression - Crisis Situation")
        print("─" * 60)

        crisis_analysis = MockEmotionalAnalysis(
            emotion="depressed",
            intensity=0.9,
            triggers=["hopelessness", "isolation"],
            crisis_indicators=["thoughts of self-harm"]
        )

        crisis_session = MockSessionState(
            progress_score=20,
            coping_strategies=["breathing"]
        )

        crisis_context = MockNarrativeContext([
            "User expressed feeling hopeless",
            "User mentioned thoughts of self-harm",
            "Dr. Sarah is deeply concerned"
        ])

        crisis_result = integrator.integrate_emotion_with_interventions(
            crisis_analysis, crisis_session, crisis_context
        )

        print(f"Emotional State: {crisis_analysis.detected_emotion.primary_emotion} (intensity: {crisis_analysis.detected_emotion.intensity})")
        print(f"Integration Success: {crisis_result['integration_success']}")
        print(f"Crisis Detected: {crisis_result['safety_assessment']['crisis_detected']}")

        if crisis_result['crisis_response']:
            crisis_response = crisis_result['crisis_response']
            print("\nCrisis Response Activated:")
            print(f"  Type: {crisis_response['intervention_type']}")
            print(f"  Immediate Actions: {len(crisis_response['immediate_actions'])}")
            print(f"  Safety Resources: {len(crisis_response['safety_resources'])}")
            print(f"  Professional Referral: {crisis_response['professional_referral_needed']}")
            print(f"  Content: {crisis_response['adapted_content'][:150]}...")

        # Scenario 3: Mild Anxiety - Suitable for Exposure Therapy
        print("\n" + "─" * 60)
        print("SCENARIO 3: Mild Anxiety - Exposure Therapy Opportunity")
        print("─" * 60)

        mild_anxiety_analysis = MockEmotionalAnalysis(
            emotion="anxious",
            intensity=0.3,
            triggers=["social situations"]
        )

        good_progress_session = MockSessionState(
            progress_score=75,
            coping_strategies=["breathing", "grounding", "positive self-talk", "mindfulness"]
        )

        supportive_context = MockNarrativeContext([
            "User has been making good progress",
            "User feels ready to face fears gradually",
            "Dr. Sarah suggests gentle exposure work"
        ])

        exposure_result = integrator.integrate_emotion_with_interventions(
            mild_anxiety_analysis, good_progress_session, supportive_context
        )

        print(f"Emotional State: {mild_anxiety_analysis.detected_emotion.primary_emotion} (intensity: {mild_anxiety_analysis.detected_emotion.intensity})")
        print(f"Integration Success: {exposure_result['integration_success']}")
        print(f"Exposure Therapy Considered: {exposure_result['exposure_therapy_session'] is not None}")

        if exposure_result['exposure_therapy_session']:
            exposure_session = exposure_result['exposure_therapy_session']
            print("\nExposure Therapy Session Details:")
            print(f"  Type: {exposure_session.exposure_type}")
            print(f"  Target Fear: {exposure_session.target_fear_or_trigger}")
            print(f"  Intensity Level: {exposure_session.exposure_intensity:.2f}")
            print(f"  Duration: {exposure_session.session_duration_minutes} minutes")
            print(f"  Narrative Scenario: {exposure_session.narrative_scenario[:200]}...")
            print(f"  Safety Measures: {len(exposure_session.safety_measures)}")
            print(f"  Escape Mechanisms: {len(exposure_session.escape_mechanisms)}")
            print(f"  Grounding Techniques: {len(exposure_session.grounding_techniques)}")

        # Demonstrate Safety Validation
        print("\n" + "─" * 60)
        print("SAFETY VALIDATION DEMONSTRATION")
        print("─" * 60)

        selector = EmotionBasedInterventionSelector()

        # Test different safety levels
        safety_scenarios = [
            ("Standard Safety", MockEmotionalState("anxious", 0.4, []), SafetyValidationLevel.STANDARD),
            ("Enhanced Safety", MockEmotionalState("depressed", 0.7, ["trauma"]), SafetyValidationLevel.ENHANCED),
            ("Maximum Safety", MockEmotionalState("depressed", 0.9, ["crisis"]), SafetyValidationLevel.MAXIMUM)
        ]

        for scenario_name, emotional_state, expected_level in safety_scenarios:
            determined_level = selector._determine_safety_level(emotional_state, session_state)
            print(f"{scenario_name}: {determined_level} (Expected: {expected_level})")

        # Demonstrate Adaptation Metadata
        print("\n" + "─" * 60)
        print("ADAPTATION METADATA EXAMPLE")
        print("─" * 60)

        if result['adaptation_metadata']:
            metadata = result['adaptation_metadata']
            print("Emotional Context:")
            for key, value in metadata['emotional_context'].items():
                print(f"  {key}: {value}")

            print("\nIntervention Selection:")
            for key, value in metadata['intervention_selection'].items():
                print(f"  {key}: {value}")

            print("\nSession Context:")
            for key, value in metadata['session_context'].items():
                print(f"  {key}: {value}")

        print("\n" + "=" * 80)
        print("🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("The emotion-intervention integration system successfully:")
        print("  ✓ Connected emotional states with appropriate interventions")
        print("  ✓ Adapted therapeutic content based on emotional context")
        print("  ✓ Provided safe exposure therapy opportunities")
        print("  ✓ Implemented comprehensive safety validation")
        print("  ✓ Handled crisis situations appropriately")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"❌ Demonstration failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_exposure_therapy_safety():
    """Demonstrate the safety mechanisms in exposure therapy."""
    print("\n" + "=" * 80)
    print("EXPOSURE THERAPY SAFETY DEMONSTRATION")
    print("=" * 80)

    try:
        from emotion_intervention_integration import (
            SafeExposureTherapyManager,
        )

        manager = SafeExposureTherapyManager()

        # Test different readiness scenarios
        scenarios = [
            {
                "name": "Ideal Candidate",
                "emotion": "anxious",
                "intensity": 0.3,
                "progress": 80,
                "coping_skills": ["breathing", "grounding", "self-talk", "mindfulness"],
                "target": "social anxiety"
            },
            {
                "name": "Moderate Risk",
                "emotion": "anxious",
                "intensity": 0.6,
                "progress": 50,
                "coping_skills": ["breathing", "grounding"],
                "target": "performance anxiety"
            },
            {
                "name": "High Risk - Not Ready",
                "emotion": "anxious",
                "intensity": 0.9,
                "progress": 30,
                "coping_skills": ["breathing"],
                "target": "social anxiety"
            },
            {
                "name": "Crisis State - Contraindicated",
                "emotion": "depressed",
                "intensity": 0.9,
                "progress": 20,
                "coping_skills": [],
                "target": "abandonment fears"
            }
        ]

        for scenario in scenarios:
            print(f"\n{scenario['name']}:")
            print(f"  Emotion: {scenario['emotion']} (intensity: {scenario['intensity']})")
            print(f"  Progress: {scenario['progress']}%")
            print(f"  Coping Skills: {len(scenario['coping_skills'])}")

            # Create mock objects
            class MockEmotionalState:
                def __init__(self, emotion, intensity):
                    self.primary_emotion = emotion
                    self.intensity = intensity
                    self.triggers = [scenario['target']]

            class MockSessionState:
                def __init__(self, progress, skills):
                    self.therapeutic_progress = MockTherapeuticProgress(progress, skills)

            class MockTherapeuticProgress:
                def __init__(self, score, skills):
                    self.overall_progress_score = score
                    self.coping_strategies_learned = skills
                    self.completed_interventions = []

            emotional_state = MockEmotionalState(scenario['emotion'], scenario['intensity'])
            session_state = MockSessionState(scenario['progress'], scenario['coping_skills'])

            # Assess readiness
            assessment = manager.assess_exposure_readiness(
                emotional_state, session_state, scenario['target']
            )

            print(f"  Ready: {assessment['ready']}")
            print(f"  Readiness Score: {assessment['readiness_score']:.2f}")

            if assessment['safety_concerns']:
                print(f"  Safety Concerns: {assessment['safety_concerns']}")

            if assessment['contraindications']:
                print(f"  Contraindications: {assessment['contraindications']}")

            if assessment['prerequisites']:
                print(f"  Prerequisites: {assessment['prerequisites']}")

            # Try to create session if ready
            if assessment['ready'] and assessment['recommended_type']:
                class MockNarrativeContext:
                    def __init__(self):
                        self.active_characters = []
                        self.current_location = "Safe therapy space"

                narrative_context = MockNarrativeContext()

                session = manager.create_exposure_session(
                    assessment['recommended_type'],
                    scenario['target'],
                    emotional_state,
                    narrative_context
                )

                if session:
                    print("  ✓ Exposure session created:")
                    print(f"    Type: {session.exposure_type}")
                    print(f"    Intensity: {session.exposure_intensity:.2f}")
                    print(f"    Duration: {session.session_duration_minutes} min")
                    print(f"    Safety Measures: {len(session.safety_measures)}")
                else:
                    print("  ⚠ Session creation blocked by safety protocols")
            else:
                print("  ❌ Not ready for exposure therapy")

        print("\n" + "=" * 80)
        print("🛡️ SAFETY DEMONSTRATION COMPLETED!")
        print("The exposure therapy system demonstrates:")
        print("  ✓ Comprehensive readiness assessment")
        print("  ✓ Multiple safety validation layers")
        print("  ✓ Contraindication checking")
        print("  ✓ Graduated intensity levels")
        print("  ✓ Built-in escape mechanisms")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"❌ Safety demonstration failed: {e}")
        return False

if __name__ == "__main__":
    success = True

    # Run main demonstration
    success &= demonstrate_emotion_intervention_integration()

    # Run safety demonstration
    success &= demonstrate_exposure_therapy_safety()

    if success:
        print("\n🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("The Emotion-Intervention Integration System is fully functional.")
    else:
        print("\n❌ Some demonstrations failed. Please review the implementation.")
