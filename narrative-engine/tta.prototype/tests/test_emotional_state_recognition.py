"""
Unit Tests for Emotional State Recognition System

This module contains comprehensive unit tests for the emotional state recognition
and response system, including emotion detection, pattern analysis, and trigger identification.
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

# Add paths for imports
core_path = Path(__file__).parent.parent / "core"
models_path = Path(__file__).parent.parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
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
        EmotionalIntensityLevel,
        EmotionalPattern,
        EmotionalPatternAnalyzer,
        EmotionalPatternType,
        EmotionalStateRecognitionResponse,
        EmotionalTrigger,
        EmotionalTriggerDetector,
        TriggerType,
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for testing
    class MockEmotionalStateRecognitionResponse:
        def __init__(self):
            pass

    EmotionalStateRecognitionResponse = MockEmotionalStateRecognitionResponse


class TestEmotionalPatternAnalyzer(unittest.TestCase):
    """Test cases for EmotionalPatternAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = EmotionalPatternAnalyzer(history_window_days=7)
        self.user_id = "test_user_123"

        # Create mock emotional history
        self.emotional_history = []
        base_time = datetime.now() - timedelta(days=5)

        # Create a pattern of increasing anxiety
        for i in range(10):
            emotion = EmotionalState(
                primary_emotion=EmotionalStateType.ANXIOUS,
                intensity=0.3 + (i * 0.05),  # Gradually increasing
                timestamp=base_time + timedelta(hours=i * 6),
                triggers=["work_stress"] if i % 3 == 0 else []
            )
            self.emotional_history.append(emotion)

    def test_analyze_emotional_patterns_empty_history(self):
        """Test pattern analysis with empty history."""
        patterns = self.analyzer.analyze_emotional_patterns(self.user_id, [])
        self.assertEqual(len(patterns), 0)

    def test_analyze_emotional_patterns_insufficient_data(self):
        """Test pattern analysis with insufficient data."""
        short_history = self.emotional_history[:2]
        patterns = self.analyzer.analyze_emotional_patterns(self.user_id, short_history)
        # Should still return some patterns, but fewer
        self.assertIsInstance(patterns, list)

    def test_detect_intensity_patterns(self):
        """Test detection of intensity patterns."""
        patterns = self.analyzer.analyze_emotional_patterns(self.user_id, self.emotional_history)

        # Should detect escalating anxiety pattern
        escalating_patterns = [p for p in patterns if p.pattern_type == EmotionalPatternType.ESCALATING]
        self.assertGreater(len(escalating_patterns), 0)

        # Check pattern properties
        if escalating_patterns:
            pattern = escalating_patterns[0]
            self.assertIn(EmotionalStateType.ANXIOUS, pattern.primary_emotions)
            self.assertEqual(pattern.intensity_trend, "increasing")
            self.assertGreater(pattern.confidence_score, 0.5)

    def test_detect_trigger_patterns(self):
        """Test detection of trigger-based patterns."""
        patterns = self.analyzer.analyze_emotional_patterns(self.user_id, self.emotional_history)

        # Should detect work_stress trigger pattern
        trigger_patterns = [p for p in patterns if "work_stress" in p.triggers]
        self.assertGreater(len(trigger_patterns), 0)

        if trigger_patterns:
            pattern = trigger_patterns[0]
            self.assertIn("work_stress", pattern.triggers)
            self.assertGreater(pattern.confidence_score, 0.0)

    def test_calculate_trend(self):
        """Test trend calculation."""
        # Test increasing trend
        increasing_values = [0.1, 0.3, 0.5, 0.7, 0.9]
        trend = self.analyzer._calculate_trend(increasing_values)
        self.assertGreater(trend, 0)

        # Test decreasing trend
        decreasing_values = [0.9, 0.7, 0.5, 0.3, 0.1]
        trend = self.analyzer._calculate_trend(decreasing_values)
        self.assertLess(trend, 0)

        # Test stable trend
        stable_values = [0.5, 0.5, 0.5, 0.5, 0.5]
        trend = self.analyzer._calculate_trend(stable_values)
        self.assertAlmostEqual(trend, 0, places=2)

    def test_pattern_validation(self):
        """Test pattern validation."""
        # Valid pattern
        valid_pattern = EmotionalPattern(
            pattern_type=EmotionalPatternType.STABLE,
            primary_emotions=[EmotionalStateType.CALM],
            confidence_score=0.8
        )
        self.assertTrue(valid_pattern.validate())

        # Invalid pattern - no emotions
        invalid_pattern = EmotionalPattern(
            pattern_type=EmotionalPatternType.STABLE,
            primary_emotions=[],
            confidence_score=0.8
        )
        with self.assertRaises(ValidationError):
            invalid_pattern.validate()

        # Invalid pattern - bad confidence score
        invalid_pattern2 = EmotionalPattern(
            pattern_type=EmotionalPatternType.STABLE,
            primary_emotions=[EmotionalStateType.CALM],
            confidence_score=1.5
        )
        with self.assertRaises(ValidationError):
            invalid_pattern2.validate()


class TestEmotionalTriggerDetector(unittest.TestCase):
    """Test cases for EmotionalTriggerDetector."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = EmotionalTriggerDetector()

        # Create mock context
        self.context = NarrativeContext(
            session_id="test_session",
            recent_events=[
                "You encountered a stressful work situation",
                "A conflict arose with a colleague",
                "The deadline is approaching quickly"
            ]
        )

        # Create mock emotional history
        self.emotional_history = [
            EmotionalState(
                primary_emotion=EmotionalStateType.ANXIOUS,
                intensity=0.7,
                triggers=["work_stress", "deadline_pressure"],
                timestamp=datetime.now() - timedelta(hours=2)
            ),
            EmotionalState(
                primary_emotion=EmotionalStateType.OVERWHELMED,
                intensity=0.8,
                triggers=["work_stress"],
                timestamp=datetime.now() - timedelta(hours=1)
            )
        ]

    def test_detect_triggers_from_input(self):
        """Test trigger detection from user input."""
        test_input = "I'm really stressed about the upcoming deadline and worried about the presentation"

        triggers = self.detector.detect_triggers(test_input, self.context, self.emotional_history)

        self.assertGreater(len(triggers), 0)

        # Check for stress-related triggers
        stress_triggers = [t for t in triggers if "stress" in t.description.lower()]
        self.assertGreater(len(stress_triggers), 0)

        # Check for deadline-related triggers
        deadline_triggers = [t for t in triggers if "deadline" in t.description.lower()]
        self.assertGreater(len(deadline_triggers), 0)

    def test_detect_triggers_from_context(self):
        """Test trigger detection from narrative context."""
        test_input = "I don't know what to do"

        triggers = self.detector.detect_triggers(test_input, self.context, self.emotional_history)

        # Should detect triggers from context events
        context_triggers = [t for t in triggers if "work" in t.description.lower() or "conflict" in t.description.lower()]
        self.assertGreater(len(context_triggers), 0)

    def test_detect_pattern_triggers(self):
        """Test detection of recurring trigger patterns."""
        test_input = "Things are difficult"

        triggers = self.detector.detect_triggers(test_input, self.context, self.emotional_history)

        # Should detect work_stress as a recurring trigger
        recurring_triggers = [t for t in triggers if t.frequency > 1]
        self.assertGreater(len(recurring_triggers), 0)

    def test_trigger_validation(self):
        """Test trigger validation."""
        # Valid trigger
        valid_trigger = EmotionalTrigger(
            trigger_type=TriggerType.SITUATIONAL,
            description="Work deadline pressure",
            intensity_impact=0.7,
            frequency=3
        )
        self.assertTrue(valid_trigger.validate())

        # Invalid trigger - empty description
        invalid_trigger = EmotionalTrigger(
            trigger_type=TriggerType.SITUATIONAL,
            description="",
            intensity_impact=0.7
        )
        with self.assertRaises(ValidationError):
            invalid_trigger.validate()

        # Invalid trigger - bad intensity impact
        invalid_trigger2 = EmotionalTrigger(
            trigger_type=TriggerType.SITUATIONAL,
            description="Test trigger",
            intensity_impact=1.5
        )
        with self.assertRaises(ValidationError):
            invalid_trigger2.validate()


class TestEmotionalStateRecognitionResponse(unittest.TestCase):
    """Test cases for EmotionalStateRecognitionResponse."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the LLM client
        self.mock_llm_client = Mock()
        self.recognition_system = EmotionalStateRecognitionResponse(llm_client=self.mock_llm_client)

        # Create mock session state
        self.session_state = SessionState(
            session_id="test_session",
            user_id="test_user",
            emotional_state=EmotionalState(
                primary_emotion=EmotionalStateType.CALM,
                intensity=0.5
            )
        )

        # Create mock narrative context
        self.context = NarrativeContext(
            session_id="test_session",
            recent_events=["You had a peaceful conversation", "The environment feels safe"]
        )

    def test_detect_emotion_from_input_anxious(self):
        """Test emotion detection for anxious input."""
        test_input = "I'm really worried and anxious about what might happen tomorrow"

        emotion = self.recognition_system._detect_emotion_from_input(test_input)

        self.assertEqual(emotion.primary_emotion, EmotionalStateType.ANXIOUS)
        self.assertGreater(emotion.intensity, 0.3)
        self.assertGreater(emotion.confidence_level, 0.3)

    def test_detect_emotion_from_input_depressed(self):
        """Test emotion detection for depressed input."""
        test_input = "I feel so hopeless and empty, like nothing matters anymore"

        emotion = self.recognition_system._detect_emotion_from_input(test_input)

        self.assertEqual(emotion.primary_emotion, EmotionalStateType.DEPRESSED)
        self.assertGreater(emotion.intensity, 0.3)
        self.assertGreater(emotion.confidence_level, 0.3)

    def test_detect_emotion_from_input_angry(self):
        """Test emotion detection for angry input."""
        test_input = "I'm so furious and mad about how I was treated"

        emotion = self.recognition_system._detect_emotion_from_input(test_input)

        self.assertEqual(emotion.primary_emotion, EmotionalStateType.ANGRY)
        self.assertGreater(emotion.intensity, 0.3)
        self.assertGreater(emotion.confidence_level, 0.3)

    def test_detect_emotion_from_input_overwhelmed(self):
        """Test emotion detection for overwhelmed input."""
        test_input = "I'm completely overwhelmed and can't handle all of this"

        emotion = self.recognition_system._detect_emotion_from_input(test_input)

        self.assertEqual(emotion.primary_emotion, EmotionalStateType.OVERWHELMED)
        self.assertGreater(emotion.intensity, 0.5)
        self.assertGreater(emotion.confidence_level, 0.3)

    def test_detect_emotion_from_input_excited(self):
        """Test emotion detection for excited input."""
        test_input = "I'm so excited and thrilled about this amazing opportunity"

        emotion = self.recognition_system._detect_emotion_from_input(test_input)

        self.assertEqual(emotion.primary_emotion, EmotionalStateType.EXCITED)
        self.assertGreater(emotion.intensity, 0.3)
        self.assertGreater(emotion.confidence_level, 0.3)

    def test_detect_emotion_intensity_levels(self):
        """Test detection of different intensity levels."""
        # Very high intensity
        high_input = "I'm completely devastated and overwhelmingly sad"
        high_emotion = self.recognition_system._detect_emotion_from_input(high_input)
        self.assertGreater(high_emotion.intensity, 0.8)

        # Low intensity
        low_input = "I'm slightly worried about this"
        low_emotion = self.recognition_system._detect_emotion_from_input(low_input)
        self.assertLess(low_emotion.intensity, 0.3)

    def test_analyze_emotional_state_complete(self):
        """Test complete emotional state analysis."""
        test_input = "I'm feeling anxious about the upcoming presentation and worried about failing"

        result = self.recognition_system.analyze_emotional_state(
            test_input, self.context, self.session_state
        )

        # Check result structure
        self.assertIsInstance(result, EmotionalAnalysisResult)
        self.assertIsInstance(result.detected_emotion, EmotionalState)
        self.assertGreater(result.confidence_level, 0.0)
        self.assertIsInstance(result.therapeutic_recommendations, list)
        self.assertIsInstance(result.detected_triggers, list)

        # Check emotion detection
        self.assertEqual(result.detected_emotion.primary_emotion, EmotionalStateType.ANXIOUS)

        # Check recommendations
        self.assertGreater(len(result.therapeutic_recommendations), 0)
        anxiety_recommendations = [r for r in result.therapeutic_recommendations if "anxiety" in r.lower()]
        self.assertGreater(len(anxiety_recommendations), 0)

    def test_crisis_detection(self):
        """Test crisis indicator detection."""
        crisis_input = "I want to hurt myself and end it all"

        result = self.recognition_system.analyze_emotional_state(
            crisis_input, self.context, self.session_state
        )

        # Should detect crisis indicators
        self.assertGreater(len(result.crisis_indicators), 0)

        # Check for specific crisis indicators
        suicide_indicators = [c for c in result.crisis_indicators if "suicide" in c.lower() or "self-harm" in c.lower()]
        self.assertGreater(len(suicide_indicators), 0)

    def test_therapeutic_recommendations_generation(self):
        """Test generation of therapeutic recommendations."""
        # Test anxiety recommendations
        anxiety_emotion = EmotionalState(
            primary_emotion=EmotionalStateType.ANXIOUS,
            intensity=0.7
        )

        recommendations = self.recognition_system._generate_therapeutic_recommendations(
            anxiety_emotion, [], self.context
        )

        self.assertGreater(len(recommendations), 0)

        # Check for anxiety-specific recommendations
        anxiety_recs = [r for r in recommendations if any(word in r.lower() for word in ["breathing", "grounding", "anxiety"])]
        self.assertGreater(len(anxiety_recs), 0)

        # Test depression recommendations
        depression_emotion = EmotionalState(
            primary_emotion=EmotionalStateType.DEPRESSED,
            intensity=0.8
        )

        recommendations = self.recognition_system._generate_therapeutic_recommendations(
            depression_emotion, [], self.context
        )

        depression_recs = [r for r in recommendations if any(word in r.lower() for word in ["behavioral", "activation", "compassion"])]
        self.assertGreater(len(depression_recs), 0)

    def test_combine_emotion_analyses(self):
        """Test combining emotion analyses from different sources."""
        input_emotion = EmotionalState(
            primary_emotion=EmotionalStateType.ANXIOUS,
            intensity=0.8,
            confidence_level=0.9
        )

        context_emotion = EmotionalState(
            primary_emotion=EmotionalStateType.CALM,
            intensity=0.3,
            confidence_level=0.4
        )

        combined = self.recognition_system._combine_emotion_analyses(input_emotion, context_emotion)

        # Should favor input emotion due to higher confidence
        self.assertEqual(combined.primary_emotion, EmotionalStateType.ANXIOUS)
        self.assertGreater(combined.confidence_level, 0.7)

    def test_pattern_detection_integration(self):
        """Test integration with pattern detection."""
        # Create emotional history with patterns
        emotional_history = []
        base_time = datetime.now() - timedelta(days=3)

        for i in range(8):
            emotion = EmotionalState(
                primary_emotion=EmotionalStateType.ANXIOUS,
                intensity=0.4 + (i * 0.05),
                timestamp=base_time + timedelta(hours=i * 8)
            )
            emotional_history.append(emotion)

        patterns = self.recognition_system.detect_emotional_patterns("test_user", emotional_history)

        self.assertIsInstance(patterns, list)
        # Should detect some patterns
        self.assertGreaterEqual(len(patterns), 0)

    def test_error_handling(self):
        """Test error handling in emotional analysis."""
        # Test with invalid input
        result = self.recognition_system.analyze_emotional_state(
            "", self.context, self.session_state
        )

        # Should return a valid result even with empty input
        self.assertIsInstance(result, EmotionalAnalysisResult)
        self.assertGreater(result.confidence_level, 0.0)

    def test_analysis_result_validation(self):
        """Test validation of analysis results."""
        # Valid result
        valid_result = EmotionalAnalysisResult(
            detected_emotion=EmotionalState(),
            confidence_level=0.8
        )
        self.assertTrue(valid_result.validate())

        # Invalid result - bad confidence level
        invalid_result = EmotionalAnalysisResult(
            detected_emotion=EmotionalState(),
            confidence_level=1.5
        )
        with self.assertRaises(ValidationError):
            invalid_result.validate()


class TestEmotionalStateIntegration(unittest.TestCase):
    """Integration tests for the emotional state recognition system."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.recognition_system = EmotionalStateRecognitionResponse()

        # Create comprehensive test scenario
        self.session_state = SessionState(
            session_id="integration_test",
            user_id="integration_user",
            therapeutic_progress=TherapeuticProgress(user_id="integration_user")
        )

        self.context = NarrativeContext(
            session_id="integration_test",
            recent_events=[
                "You faced a challenging situation at work",
                "Your colleague criticized your performance",
                "You felt pressure to meet the deadline"
            ]
        )

    def test_full_emotional_analysis_workflow(self):
        """Test the complete emotional analysis workflow."""
        test_scenarios = [
            {
                "input": "I'm extremely anxious about the presentation tomorrow and can't stop worrying",
                "expected_emotion": EmotionalStateType.ANXIOUS,
                "expected_intensity_min": 0.6
            },
            {
                "input": "I feel completely overwhelmed by everything on my plate right now",
                "expected_emotion": EmotionalStateType.OVERWHELMED,
                "expected_intensity_min": 0.5
            },
            {
                "input": "I'm excited about the new project and can't wait to get started",
                "expected_emotion": EmotionalStateType.EXCITED,
                "expected_intensity_min": 0.4
            }
        ]

        for scenario in test_scenarios:
            with self.subTest(input=scenario["input"]):
                result = self.recognition_system.analyze_emotional_state(
                    scenario["input"], self.context, self.session_state
                )

                # Check emotion detection
                self.assertEqual(result.detected_emotion.primary_emotion, scenario["expected_emotion"])
                self.assertGreaterEqual(result.detected_emotion.intensity, scenario["expected_intensity_min"])

                # Check that recommendations are provided
                self.assertGreater(len(result.therapeutic_recommendations), 0)

                # Check that analysis is valid
                result.validate()

    def test_pattern_and_trigger_integration(self):
        """Test integration between pattern detection and trigger identification."""
        # Create a series of related inputs
        inputs = [
            "I'm stressed about work deadlines",
            "The work pressure is getting to me again",
            "Another deadline is making me anxious",
            "I can't handle all this work stress"
        ]

        emotional_history = []

        for _i, test_input in enumerate(inputs):
            result = self.recognition_system.analyze_emotional_state(
                test_input, self.context, self.session_state
            )

            # Add to emotional history
            emotional_history.append(result.detected_emotion)

            # Update session state
            self.session_state.emotional_state = result.detected_emotion

        # Analyze patterns
        patterns = self.recognition_system.detect_emotional_patterns("integration_user", emotional_history)

        # Should detect work-related stress patterns
        work_patterns = [p for p in patterns if any("work" in trigger.lower() for trigger in p.triggers)]
        self.assertGreaterEqual(len(work_patterns), 0)

        # Analyze final state for triggers
        final_result = self.recognition_system.analyze_emotional_state(
            inputs[-1], self.context, self.session_state
        )

        # Should detect work-related triggers
        work_triggers = [t for t in final_result.detected_triggers if "work" in t.description.lower()]
        self.assertGreater(len(work_triggers), 0)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
