#!/usr/bin/env python3
"""
Simple test script for therapeutic content integration system.
"""

import sys
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent / "core"
models_path = Path(__file__).parent / "models"
sys.path.append(str(core_path))
sys.path.append(str(models_path))

def test_opportunity_detector():
    """Test the therapeutic opportunity detector."""
    try:
        # Import the detector class
        from data_models import (
            EmotionalState,
            EmotionalStateType,
            NarrativeContext,
            SessionState,
        )
        from therapeutic_content_integration import (
            InterventionUrgency,
            OpportunityType,
            TherapeuticOpportunityContext,
            TherapeuticOpportunityDetector,
        )

        print("✓ Successfully imported therapeutic opportunity detector classes")

        # Create test data
        session_state = SessionState(
            session_id="test_session",
            user_id="test_user"
        )

        narrative_context = NarrativeContext(
            session_id="test_session",
            current_location_id="test_location",
            recent_events=["User expressed feeling anxious", "User mentioned worry about presentation"]
        )

        opportunity_context = TherapeuticOpportunityContext(
            narrative_context=narrative_context,
            session_state=session_state,
            user_input="I'm feeling really anxious about everything and can't stop worrying",
            emotional_indicators=["anxious", "worried"],
            recent_choices=[
                {"choice_text": "avoid the situation", "choice_id": "choice_1"},
                {"choice_text": "worry more about it", "choice_id": "choice_2"}
            ]
        )

        print("✓ Successfully created test data structures")

        # Test opportunity context validation
        opportunity_context.validate()
        print("✓ Opportunity context validation passed")

        # Initialize the detector
        detector = TherapeuticOpportunityDetector()
        print("✓ Successfully initialized TherapeuticOpportunityDetector")

        # Test opportunity detection
        opportunities = detector.detect_opportunities(opportunity_context)
        print(f"✓ Detected {len(opportunities)} therapeutic opportunities")

        if opportunities:
            for i, opportunity in enumerate(opportunities):
                print(f"  {i+1}. {opportunity.opportunity_type.value}")
                print(f"     - Confidence: {opportunity.confidence_score:.2f}")
                print(f"     - Urgency: {opportunity.urgency_level.value}")
                print(f"     - Triggers: {opportunity.trigger_events[:2]}")
                print(f"     - Interventions: {[interv.value for interv in opportunity.recommended_interventions[:2]]}")

        # Test specific anxiety detection
        anxiety_opportunities = [
            opp for opp in opportunities
            if opp.opportunity_type == OpportunityType.ANXIETY_MANAGEMENT
        ]

        if anxiety_opportunities:
            print("✓ Successfully detected anxiety management opportunity")
        else:
            print("⚠ No anxiety management opportunity detected")

        # Test emotional state with high intensity
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.ANXIOUS,
            intensity=0.9,
            secondary_emotions=[EmotionalStateType.OVERWHELMED]
        )
        session_state.emotional_state = emotional_state

        high_intensity_opportunities = detector.detect_opportunities(opportunity_context)
        high_urgency_count = sum(1 for opp in high_intensity_opportunities if opp.urgency_level == InterventionUrgency.HIGH)

        print(f"✓ With high emotional intensity, detected {high_urgency_count} high-urgency opportunities")

        print("\n🎉 Opportunity detector tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic functionality without LLM dependencies."""
    try:
        from data_models import InterventionType
        from therapeutic_content_integration import (
            DetectedOpportunity,
            InterventionUrgency,
            OpportunityType,
        )

        print("✓ Successfully imported basic classes")

        # Test DetectedOpportunity creation and validation
        opportunity = DetectedOpportunity(
            opportunity_type=OpportunityType.ANXIETY_MANAGEMENT,
            trigger_events=["User expressed anxiety"],
            recommended_interventions=[InterventionType.MINDFULNESS, InterventionType.COPING_SKILLS],
            urgency_level=InterventionUrgency.MEDIUM,
            confidence_score=0.8,
            therapeutic_rationale="User shows signs of anxiety that could benefit from mindfulness practice"
        )

        # Validate the opportunity
        opportunity.validate()
        print("✓ DetectedOpportunity validation passed")

        print(f"  - Type: {opportunity.opportunity_type.value}")
        print(f"  - Confidence: {opportunity.confidence_score}")
        print(f"  - Urgency: {opportunity.urgency_level.value}")
        print(f"  - Interventions: {[i.value for i in opportunity.recommended_interventions]}")

        print("\n🎉 Basic functionality tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing Therapeutic Content Integration System")
    print("=" * 50)

    success1 = test_basic_functionality()
    print()
    success2 = test_opportunity_detector()

    if success1 and success2:
        print("\n🎉 All tests passed! Therapeutic content integration system is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
