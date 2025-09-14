"""
Integration Tests for Adaptive Response System and Crisis Support

This module contains comprehensive integration tests for the adaptive response system,
crisis detection, emotional growth tracking, and narrative tone adaptation.
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent.parent / "core"
models_path = Path(__file__).parent.parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    from adaptive_response_system import (
        AdaptationStrategy,
        AdaptiveResponse,
        AdaptiveResponseSystem,
        CrisisDetectionSystem,
        CrisisIndicator,
        CrisisLevel,
        EmotionalGrowthMoment,
        EmotionalGrowthTracker,
        NarrativeToneAdapter,
        ResponseTone,
    )
    from data_models import (
        EmotionalState,
        EmotionalStateType,
        NarrativeContext,
        SessionState,
        TherapeuticProgress,
        ValidationError,
    )
    from emotional_state_recognition import (
        EmotionalAnalysisResult,
        EmotionalStateRecognitionResponse,
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for testing
    class MockAdaptiveResponseSystem:
        def __init__(self):
            pass

    AdaptiveResponseSystem = MockAdaptiveResponseSystem


class TestCrisisDetectionSystem(unittest.TestCase):
    """Test cases for CrisisDetectionSystem."""

    def setUp(self):
        """Set up test fixtures."""
        self.crisis_detector = CrisisDetectionSystem()

        # Create mock context
        self.context = NarrativeContext(
            session_id="test_session",
            recent_events=["You're facing a difficult situation"]
        )

    def test_detect_moderate_crisis(self):
        """Test detection of moderate crisis level."""
        test_input = "I feel completely hopeless and don't know what to do anymore"
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.DEPRESSED,
            intensity=0.8
        )

        crisis_level, indicators = self.crisis_detector.detect_crisis_level(
            test_input, emotional_state, self.context
        )

        self.assertEqual(crisis_level, CrisisLevel.MODERATE)
        self.assertGreater(len(indicators), 0)

        # Check indicator properties
        hopeless_indicators = [i for i in indicators if "hopeless" in i.description.lower()]
        self.assertGreater(len(hopeless_indicators), 0)

    def test_detect_high_crisis(self):
        """Test detection of high crisis level."""
        test_input = "I want to hurt myself and can't take this pain anymore"
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.DEPRESSED,
            intensity=0.9
        )

        crisis_level, indicators = self.crisis_detector.detect_crisis_level(
            test_input, emotional_state, self.context
        )

        self.assertEqual(crisis_level, CrisisLevel.HIGH)
        self.assertGreater(len(indicators), 0)

        # Check for immediate action requirement
        immediate_action_indicators = [i for i in indicators if i.immediate_action_required]
        self.assertGreater(len(immediate_action_indicators), 0)

    def test_detect_severe_crisis(self):
        """Test detection of severe crisis level."""
        test_input = "I'm going to kill myself tonight, I have a plan"
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.DEPRESSED,
            intensity=0.95
        )

        crisis_level, indicators = self.crisis_detector.detect_crisis_level(
            test_input, emotional_state, self.context
        )

        self.assertEqual(crisis_level, CrisisLevel.SEVERE)
        self.assertGreater(len(indicators), 0)

        # Check for professional referral
        referral_indicators = [i for i in indicators if i.professional_referral_needed]
        self.assertGreater(len(referral_indicators), 0)

    def test_detect_emergency_crisis(self):
        """Test detection of emergency crisis level."""
        test_input = "I'm going to kill myself right now, goodbye forever"
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.DEPRESSED,
            intensity=1.0
        )

        crisis_level, indicators = self.crisis_detector.detect_crisis_level(
            test_input, emotional_state, self.context
        )

        self.assertEqual(crisis_level, CrisisLevel.EMERGENCY)
        self.assertGreater(len(indicators), 0)

        # All indicators should require immediate action
        for indicator in indicators:
            self.assertTrue(indicator.immediate_action_required)

    def test_no_crisis_detection(self):
        """Test when no crisis is detected."""
        test_input = "I'm feeling a bit sad today but I'll be okay"
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.DEPRESSED,
            intensity=0.3
        )

        crisis_level, indicators = self.crisis_detector.detect_crisis_level(
            test_input, emotional_state, self.context
        )

        self.assertEqual(crisis_level, CrisisLevel.NONE)
        self.assertEqual(len(indicators), 0)

    def test_generate_crisis_response_moderate(self):
        """Test crisis response generation for moderate level."""
        indicators = [
            CrisisIndicator(
                indicator_type="keyword_match",
                severity_level=CrisisLevel.MODERATE,
                description="Hopelessness detected",
                confidence_score=0.8
            )
        ]

        response = self.crisis_detector.generate_crisis_response(
            CrisisLevel.MODERATE, indicators, self.context
        )

        self.assertIsInstance(response, AdaptiveResponse)
        self.assertEqual(response.crisis_level, CrisisLevel.MODERATE)
        self.assertIn("difficult time", response.adapted_content.lower())
        self.assertTrue(response.follow_up_needed)

    def test_generate_crisis_response_emergency(self):
        """Test crisis response generation for emergency level."""
        indicators = [
            CrisisIndicator(
                indicator_type="pattern_match",
                severity_level=CrisisLevel.EMERGENCY,
                description="Immediate suicide threat",
                confidence_score=0.95,
                immediate_action_required=True
            )
        ]

        response = self.crisis_detector.generate_crisis_response(
            CrisisLevel.EMERGENCY, indicators, self.context
        )

        self.assertIsInstance(response, AdaptiveResponse)
        self.assertEqual(response.crisis_level, CrisisLevel.EMERGENCY)
        self.assertIn("911", response.adapted_content)
        self.assertIn("988", response.adapted_content)
        self.assertTrue(response.follow_up_needed)

    def test_crisis_indicator_validation(self):
        """Test crisis indicator validation."""
        # Valid indicator
        valid_indicator = CrisisIndicator(
            description="Test crisis indicator",
            confidence_score=0.8
        )
        self.assertTrue(valid_indicator.validate())

        # Invalid indicator - empty description
        invalid_indicator = CrisisIndicator(
            description="",
            confidence_score=0.8
        )
        with self.assertRaises(ValidationError):
            invalid_indicator.validate()

        # Invalid indicator - bad confidence score
        invalid_indicator2 = CrisisIndicator(
            description="Test indicator",
            confidence_score=1.5
        )
        with self.assertRaises(ValidationError):
            invalid_indicator2.validate()


class TestEmotionalGrowthTracker(unittest.TestCase):
    """Test cases for EmotionalGrowthTracker."""

    def setUp(self):
        """Set up test fixtures."""
        self.growth_tracker = EmotionalGrowthTracker()

        # Create mock context
        self.context = NarrativeContext(
            session_id="test_session",
            recent_events=["You successfully handled a challenge"]
        )

    def test_detect_intensity_improvement(self):
        """Test detection of emotional intensity improvement."""
        # Previous state with high intensity
        previous_state = EmotionalState(
            primary_emotion=EmotionalStateType.ANXIOUS,
            intensity=0.8,
            timestamp=datetime.now() - timedelta(minutes=30)
        )

        # Current state with lower intensity
        current_state = EmotionalState(
            primary_emotion=EmotionalStateType.ANXIOUS,
            intensity=0.4,
            timestamp=datetime.now()
        )

        growth_moments = self.growth_tracker.detect_emotional_growth(
            current_state, [previous_state], "I'm feeling much better now", self.context
        )

        # Should detect intensity improvement
        intensity_improvements = [g for g in growth_moments if g.growth_type == "intensity_improvement"]
        self.assertGreater(len(intensity_improvements), 0)

        if intensity_improvements:
            growth = intensity_improvements[0]
            self.assertGreater(growth.therapeutic_significance, 0.5)
            self.assertIsNotNone(growth.reinforcement_message)

    def test_detect_coping_strategy_use(self):
        """Test detection of coping strategy use."""
        current_state = EmotionalState(
            primary_emotion=EmotionalStateType.CALM,
            intensity=0.5
        )

        test_input = "I used breathing exercises and grounding techniques to calm down"

        growth_moments = self.growth_tracker.detect_emotional_growth(
            current_state, [], test_input, self.context
        )

        # Should detect coping strategy use
        coping_moments = [g for g in growth_moments if g.growth_type == "coping_strategy_use"]
        self.assertGreater(len(coping_moments), 0)

        if coping_moments:
            growth = coping_moments[0]
            self.assertIn("breathing", growth.improvement_indicators[0].lower())

    def test_detect_emotional_awareness(self):
        """Test detection of emotional awareness growth."""
        current_state = EmotionalState(
            primary_emotion=EmotionalStateType.CALM,
            intensity=0.6
        )

        test_input = "I notice that I'm feeling anxious and I realize it's because of the upcoming meeting"

        growth_moments = self.growth_tracker.detect_emotional_growth(
            current_state, [], test_input, self.context
        )

        # Should detect emotional awareness
        awareness_moments = [g for g in growth_moments if g.growth_type == "emotional_awareness"]
        self.assertGreater(len(awareness_moments), 0)

    def test_detect_positive_reframing(self):
        """Test detection of positive reframing."""
        current_state = EmotionalState(
            primary_emotion=EmotionalStateType.HOPEFUL,
            intensity=0.7
        )

        test_input = "This is challenging, but on the other hand, it's also an opportunity to learn"

        growth_moments = self.growth_tracker.detect_emotional_growth(
            current_state, [], test_input, self.context
        )

        # Should detect positive reframing
        reframing_moments = [g for g in growth_moments if g.growth_type == "positive_reframing"]
        self.assertGreater(len(reframing_moments), 0)

    def test_detect_help_seeking(self):
        """Test detection of help-seeking behavior."""
        current_state = EmotionalState(
            primary_emotion=EmotionalStateType.HOPEFUL,
            intensity=0.6
        )

        test_input = "I decided to reach out for help and talk to my therapist about this"

        growth_moments = self.growth_tracker.detect_emotional_growth(
            current_state, [], test_input, self.context
        )

        # Should detect help-seeking
        help_seeking_moments = [g for g in growth_moments if g.growth_type == "help_seeking"]
        self.assertGreater(len(help_seeking_moments), 0)

    def test_generate_reinforcement_messages(self):
        """Test generation of appropriate reinforcement messages."""
        # High significance growth
        high_significance_growth = EmotionalGrowthMoment(
            growth_type="coping_strategy_use",
            description="User applied coping strategies",
            therapeutic_significance=0.9
        )

        message = self.growth_tracker._generate_reinforcement_message(high_significance_growth)
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 10)

        # Low significance growth
        low_significance_growth = EmotionalGrowthMoment(
            growth_type="emotional_awareness",
            description="Minor awareness increase",
            therapeutic_significance=0.3
        )

        message = self.growth_tracker._generate_reinforcement_message(low_significance_growth)
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 10)

    def test_growth_moment_validation(self):
        """Test emotional growth moment validation."""
        # Valid growth moment
        valid_moment = EmotionalGrowthMoment(
            description="Test growth moment",
            therapeutic_significance=0.7
        )
        self.assertTrue(valid_moment.validate())

        # Invalid moment - empty description
        invalid_moment = EmotionalGrowthMoment(
            description="",
            therapeutic_significance=0.7
        )
        with self.assertRaises(ValidationError):
            invalid_moment.validate()


class TestNarrativeToneAdapter(unittest.TestCase):
    """Test cases for NarrativeToneAdapter."""

    def setUp(self):
        """Set up test fixtures."""
        self.tone_adapter = NarrativeToneAdapter()

        # Create mock context
        self.context = NarrativeContext(
            session_id="test_session",
            recent_events=["A situation unfolds before you"]
        )

    def test_adapt_tone_for_anxious_state(self):
        """Test tone adaptation for anxious emotional state."""
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.ANXIOUS,
            intensity=0.7,
            confidence_level=0.8
        )

        original_content = "You must quickly decide what to do next in this urgent situation."

        response = self.tone_adapter.adapt_narrative_tone(
            original_content, emotional_state, self.context
        )

        self.assertEqual(response.response_tone, ResponseTone.CALMING)
        self.assertNotEqual(response.adapted_content, original_content)

        # Should remove urgent language
        self.assertNotIn("quickly", response.adapted_content.lower())
        self.assertNotIn("urgent", response.adapted_content.lower())

    def test_adapt_tone_for_depressed_state(self):
        """Test tone adaptation for depressed emotional state."""
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.DEPRESSED,
            intensity=0.6,
            confidence_level=0.8
        )

        original_content = "The situation looks challenging and difficult to handle."

        response = self.tone_adapter.adapt_narrative_tone(
            original_content, emotional_state, self.context
        )

        self.assertEqual(response.response_tone, ResponseTone.VALIDATING)

        # Should include validation
        validation_words = ["understand", "makes sense", "valid", "natural"]
        has_validation = any(word in response.adapted_content.lower() for word in validation_words)
        self.assertTrue(has_validation)

    def test_adapt_tone_for_angry_state(self):
        """Test tone adaptation for angry emotional state."""
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.ANGRY,
            intensity=0.8,
            confidence_level=0.9
        )

        original_content = "This situation is frustrating and unfair."

        response = self.tone_adapter.adapt_narrative_tone(
            original_content, emotional_state, self.context
        )

        self.assertEqual(response.response_tone, ResponseTone.VALIDATING)

        # Should validate the anger
        self.assertIn("anger", response.adapted_content.lower())

    def test_adapt_tone_for_overwhelmed_state(self):
        """Test tone adaptation for overwhelmed emotional state."""
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.OVERWHELMED,
            intensity=0.9,
            confidence_level=0.8
        )

        original_content = "There are many complex options and considerations to think about."

        response = self.tone_adapter.adapt_narrative_tone(
            original_content, emotional_state, self.context
        )

        self.assertEqual(response.response_tone, ResponseTone.GROUNDING)

        # Should include grounding elements
        grounding_words = ["ground", "feet", "breathe", "air", "see", "hear"]
        has_grounding = any(word in response.adapted_content.lower() for word in grounding_words)
        self.assertTrue(has_grounding)

    def test_adapt_tone_for_excited_state(self):
        """Test tone adaptation for excited emotional state."""
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.EXCITED,
            intensity=0.8,
            confidence_level=0.9
        )

        original_content = "An interesting opportunity presents itself."

        response = self.tone_adapter.adapt_narrative_tone(
            original_content, emotional_state, self.context
        )

        self.assertEqual(response.response_tone, ResponseTone.ENERGIZING)

        # Should maintain or enhance positive energy
        self.assertGreater(len(response.adapted_content), len(original_content))

    def test_adapt_tone_for_hopeful_state(self):
        """Test tone adaptation for hopeful emotional state."""
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.HOPEFUL,
            intensity=0.7,
            confidence_level=0.8
        )

        original_content = "You see a path forward through the challenges."

        response = self.tone_adapter.adapt_narrative_tone(
            original_content, emotional_state, self.context
        )

        self.assertEqual(response.response_tone, ResponseTone.ENCOURAGING)

        # Should include encouraging elements
        encouraging_words = ["great", "strength", "positive", "capable", "doing"]
        has_encouragement = any(word in response.adapted_content.lower() for word in encouraging_words)
        self.assertTrue(has_encouragement)

    def test_adaptation_strategies_applied(self):
        """Test that appropriate adaptation strategies are applied."""
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.ANXIOUS,
            intensity=0.8,
            confidence_level=0.9
        )

        original_content = "You must act quickly in this urgent situation."

        response = self.tone_adapter.adapt_narrative_tone(
            original_content, emotional_state, self.context
        )

        # Should include tone adjustment
        self.assertIn(AdaptationStrategy.TONE_ADJUSTMENT, response.adaptation_strategies)

        # Should include pacing modification for high intensity
        self.assertIn(AdaptationStrategy.PACING_MODIFICATION, response.adaptation_strategies)

        # Should include support escalation for high intensity
        self.assertIn(AdaptationStrategy.SUPPORT_ESCALATION, response.adaptation_strategies)

    def test_adaptive_response_validation(self):
        """Test adaptive response validation."""
        # Valid response
        valid_response = AdaptiveResponse(
            adapted_content="Test adapted content",
            therapeutic_value=0.8
        )
        self.assertTrue(valid_response.validate())

        # Invalid response - empty content
        invalid_response = AdaptiveResponse(
            adapted_content="",
            therapeutic_value=0.8
        )
        with self.assertRaises(ValidationError):
            invalid_response.validate()


class TestAdaptiveResponseSystemIntegration(unittest.TestCase):
    """Integration tests for the complete adaptive response system."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.adaptive_system = AdaptiveResponseSystem()

        # Create comprehensive test scenario
        self.session_state = SessionState(
            session_id="integration_test",
            user_id="integration_user",
            therapeutic_progress=TherapeuticProgress(user_id="integration_user")
        )

        self.context = NarrativeContext(
            session_id="integration_test",
            recent_events=[
                "You encountered a stressful situation",
                "The pressure is mounting",
                "You need to make a decision"
            ]
        )

    def test_full_adaptive_response_workflow_anxious(self):
        """Test complete adaptive response workflow for anxious state."""
        # Create emotional analysis result
        emotional_analysis = EmotionalAnalysisResult(
            detected_emotion=EmotionalState(
                primary_emotion=EmotionalStateType.ANXIOUS,
                intensity=0.7,
                confidence_level=0.8
            ),
            therapeutic_recommendations=["Practice deep breathing exercises", "Use grounding techniques"]
        )

        original_content = "You must quickly decide what to do in this urgent and stressful situation."

        response = self.adaptive_system.generate_adaptive_response(
            original_content, emotional_analysis, self.context, self.session_state
        )

        # Check response properties
        self.assertIsInstance(response, AdaptiveResponse)
        self.assertEqual(response.response_tone, ResponseTone.CALMING)
        self.assertNotEqual(response.adapted_content, original_content)

        # Should remove urgent language
        self.assertNotIn("quickly", response.adapted_content.lower())
        self.assertNotIn("urgent", response.adapted_content.lower())

        # Should include therapeutic recommendations
        self.assertIn("breathing", response.adapted_content.lower())

        # Should have appropriate therapeutic value
        self.assertGreater(response.therapeutic_value, 0.5)

    def test_crisis_response_prioritization(self):
        """Test that crisis responses are prioritized over regular adaptations."""
        # Create crisis-level emotional analysis
        emotional_analysis = EmotionalAnalysisResult(
            detected_emotion=EmotionalState(
                primary_emotion=EmotionalStateType.DEPRESSED,
                intensity=0.9,
                confidence_level=0.9
            ),
            crisis_indicators=["Suicide ideation detected"],
            therapeutic_recommendations=["Seek immediate professional help"]
        )

        original_content = "I want to hurt myself and end it all"

        response = self.adaptive_system.generate_adaptive_response(
            original_content, emotional_analysis, self.context, self.session_state
        )

        # Should be a crisis response
        self.assertNotEqual(response.crisis_level, CrisisLevel.NONE)
        self.assertEqual(response.response_tone, ResponseTone.CRISIS_FOCUSED)

        # Should include crisis resources
        self.assertIn("988", response.adapted_content)
        self.assertTrue(response.follow_up_needed)

    def test_emotional_growth_acknowledgment(self):
        """Test emotional growth acknowledgment in responses."""
        # Create previous emotional state (high intensity)
        previous_state = EmotionalState(
            primary_emotion=EmotionalStateType.ANXIOUS,
            intensity=0.9,
            timestamp=datetime.now() - timedelta(minutes=30)
        )

        # Update session state with previous emotional state
        self.session_state.emotional_state = previous_state

        # Create current emotional analysis (improved state)
        emotional_analysis = EmotionalAnalysisResult(
            detected_emotion=EmotionalState(
                primary_emotion=EmotionalStateType.ANXIOUS,
                intensity=0.4,
                confidence_level=0.8
            ),
            therapeutic_recommendations=["Continue using coping strategies"]
        )

        original_content = "I used breathing techniques and I'm feeling much calmer now."

        response = self.adaptive_system.generate_adaptive_response(
            original_content, emotional_analysis, self.context, self.session_state
        )

        # Should include growth acknowledgment
        self.assertIn(AdaptationStrategy.GROWTH_REINFORCEMENT, response.adaptation_strategies)

        # Should have high therapeutic value due to growth acknowledgment
        self.assertGreater(response.therapeutic_value, 0.7)

    def test_response_history_tracking(self):
        """Test that response history is properly tracked."""
        emotional_analysis = EmotionalAnalysisResult(
            detected_emotion=EmotionalState(
                primary_emotion=EmotionalStateType.CALM,
                intensity=0.5,
                confidence_level=0.7
            )
        )

        original_content = "You continue on your journey."

        # Generate multiple responses
        for i in range(3):
            self.adaptive_system.generate_adaptive_response(
                f"{original_content} {i}", emotional_analysis, self.context, self.session_state
            )

        # Check response history
        metrics = self.adaptive_system.get_response_effectiveness_metrics("integration_user")

        self.assertEqual(metrics["total_responses"], 3)
        self.assertIn("average_therapeutic_value", metrics)
        self.assertIn("tone_distribution", metrics)
        self.assertIn("strategy_usage", metrics)

    def test_multiple_emotional_states_handling(self):
        """Test handling of different emotional states in sequence."""
        test_scenarios = [
            {
                "emotion": EmotionalStateType.ANXIOUS,
                "intensity": 0.8,
                "content": "This situation is making me very nervous and worried.",
                "expected_tone": ResponseTone.CALMING
            },
            {
                "emotion": EmotionalStateType.DEPRESSED,
                "intensity": 0.6,
                "content": "I feel sad and hopeless about everything.",
                "expected_tone": ResponseTone.VALIDATING
            },
            {
                "emotion": EmotionalStateType.EXCITED,
                "intensity": 0.7,
                "content": "I'm so excited about this new opportunity!",
                "expected_tone": ResponseTone.ENERGIZING
            },
            {
                "emotion": EmotionalStateType.OVERWHELMED,
                "intensity": 0.9,
                "content": "There's just too much to handle all at once.",
                "expected_tone": ResponseTone.GROUNDING
            }
        ]

        for scenario in test_scenarios:
            with self.subTest(emotion=scenario["emotion"]):
                emotional_analysis = EmotionalAnalysisResult(
                    detected_emotion=EmotionalState(
                        primary_emotion=scenario["emotion"],
                        intensity=scenario["intensity"],
                        confidence_level=0.8
                    )
                )

                response = self.adaptive_system.generate_adaptive_response(
                    scenario["content"], emotional_analysis, self.context, self.session_state
                )

                # Check that appropriate tone is applied
                self.assertEqual(response.response_tone, scenario["expected_tone"])

                # Check that content is adapted
                self.assertNotEqual(response.adapted_content, scenario["content"])

                # Check therapeutic value
                self.assertGreater(response.therapeutic_value, 0.3)

    def test_error_handling_and_fallbacks(self):
        """Test error handling and fallback mechanisms."""
        # Test with invalid emotional analysis
        invalid_analysis = EmotionalAnalysisResult(
            detected_emotion=EmotionalState(
                primary_emotion=EmotionalStateType.CALM,
                intensity=0.5
            )
        )

        # Simulate error condition by passing None as content
        response = self.adaptive_system.generate_adaptive_response(
            "", invalid_analysis, self.context, self.session_state
        )

        # Should return a valid fallback response
        self.assertIsInstance(response, AdaptiveResponse)
        self.assertEqual(response.response_tone, ResponseTone.SUPPORTIVE)
        self.assertIsNotNone(response.adapted_content)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
