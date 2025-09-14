"""
Unit tests for Emotion-Intervention Integration System

Tests the integration between emotional state recognition and therapeutic interventions,
including emotion-based intervention selection, safe exposure therapy, and safety validation.
"""

import sys
import unittest
from datetime import datetime
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
        CharacterState,
        CompletedIntervention,
        EmotionalState,
        EmotionalStateType,
        InterventionType,
        NarrativeContext,
        SessionState,
        TherapeuticProgress,
    )
    from emotion_intervention_integration import (
        AdaptedIntervention,
        EmotionBasedInterventionSelector,
        EmotionInterventionIntegrator,
        EmotionInterventionMapping,
        ExposureTherapySession,
        ExposureTherapyType,
        SafeExposureTherapyManager,
        SafetyValidationLevel,
    )
except ImportError:
    # Create mock classes for testing
    class MockEmotionalState:
        def __init__(self, primary_emotion="calm", intensity=0.5, **kwargs):
            self.primary_emotion = primary_emotion
            self.intensity = intensity
            self.secondary_emotions = kwargs.get('secondary_emotions', [])
            self.triggers = kwargs.get('triggers', [])
            self.timestamp = datetime.now()
            self.confidence_level = kwargs.get('confidence_level', 0.7)

    class MockEmotionalStateType:
        CALM = "calm"
        ANXIOUS = "anxious"
        DEPRESSED = "depressed"
        EXCITED = "excited"
        ANGRY = "angry"
        CONFUSED = "confused"
        HOPEFUL = "hopeful"
        OVERWHELMED = "overwhelmed"

    # Set mock classes
    EmotionalState = MockEmotionalState
    EmotionalStateType = MockEmotionalStateType


class TestEmotionBasedInterventionSelector(unittest.TestCase):
    """Test the emotion-based intervention selector."""

    def setUp(self):
        """Set up test fixtures."""
        self.selector = EmotionBasedInterventionSelector()

        # Create mock emotional state
        self.mock_emotional_state = Mock()
        self.mock_emotional_state.primary_emotion = EmotionalStateType.ANXIOUS
        self.mock_emotional_state.intensity = 0.5
        self.mock_emotional_state.triggers = ["social_situation"]
        self.mock_emotional_state.confidence_level = 0.8

        # Create mock session state
        self.mock_session_state = Mock()
        self.mock_session_state.therapeutic_progress = Mock()
        self.mock_session_state.therapeutic_progress.overall_progress_score = 50
        self.mock_session_state.therapeutic_progress.completed_interventions = []
        self.mock_session_state.therapeutic_progress.coping_strategies_learned = ["breathing", "grounding"]
        self.mock_session_state.character_states = {}

        # Create mock narrative context
        self.mock_narrative_context = Mock()
        self.mock_narrative_context.recent_events = ["User expressed anxiety about upcoming presentation"]
        self.mock_narrative_context.active_characters = []

    def test_select_interventions_for_moderate_anxiety(self):
        """Test intervention selection for moderate anxiety."""
        interventions = self.selector.select_interventions(
            self.mock_emotional_state, self.mock_session_state, self.mock_narrative_context
        )

        self.assertIsInstance(interventions, list)
        self.assertGreater(len(interventions), 0)

        # Check that appropriate interventions are selected
        intervention_types = [intervention.base_intervention_type for intervention in interventions]
        self.assertIn(InterventionType.MINDFULNESS, intervention_types)

    def test_select_interventions_for_high_intensity_emotion(self):
        """Test intervention selection for high intensity emotions."""
        self.mock_emotional_state.intensity = 0.9

        interventions = self.selector.select_interventions(
            self.mock_emotional_state, self.mock_session_state, self.mock_narrative_context
        )

        # Should get crisis-appropriate interventions
        self.assertIsInstance(interventions, list)
        if interventions:
            self.assertEqual(interventions[0].safety_level, SafetyValidationLevel.MAXIMUM)

    def test_safety_level_determination(self):
        """Test safety level determination based on emotional state."""
        # Test standard safety level
        safety_level = self.selector._determine_safety_level(
            self.mock_emotional_state, self.mock_session_state
        )
        self.assertEqual(safety_level, SafetyValidationLevel.STANDARD)

        # Test enhanced safety level for high intensity
        self.mock_emotional_state.intensity = 0.8
        self.mock_emotional_state.primary_emotion = EmotionalStateType.DEPRESSED

        safety_level = self.selector._determine_safety_level(
            self.mock_emotional_state, self.mock_session_state
        )
        self.assertEqual(safety_level, SafetyValidationLevel.ENHANCED)

    def test_intervention_adaptation(self):
        """Test intervention adaptation for emotional context."""
        mapping = EmotionInterventionMapping(
            emotion_type=EmotionalStateType.ANXIOUS,
            intensity_range=(0.0, 0.7),
            primary_interventions=[InterventionType.MINDFULNESS],
            adaptation_strategies=["use_calming_tone", "slower_pacing"]
        )

        adapted_intervention = self.selector._adapt_intervention(
            InterventionType.MINDFULNESS,
            self.mock_emotional_state,
            mapping,
            self.mock_session_state,
            self.mock_narrative_context,
            SafetyValidationLevel.STANDARD
        )

        self.assertIsNotNone(adapted_intervention)
        self.assertIsInstance(adapted_intervention, AdaptedIntervention)
        self.assertEqual(adapted_intervention.base_intervention_type, InterventionType.MINDFULNESS)
        self.assertTrue(adapted_intervention.contraindications_checked)

    def test_safety_validation(self):
        """Test safety validation for interventions."""
        content = "Let's practice some mindful breathing to help you feel more calm and centered."

        validation_result = self.selector._perform_safety_validation(
            content, InterventionType.MINDFULNESS, self.mock_emotional_state, SafetyValidationLevel.STANDARD
        )

        self.assertIsInstance(validation_result, dict)
        self.assertIn("passed", validation_result)
        self.assertIn("validations", validation_result)

    def test_default_interventions_fallback(self):
        """Test fallback to default interventions when mappings unavailable."""
        # Create emotional state with unmapped emotion
        unknown_emotional_state = Mock()
        unknown_emotional_state.primary_emotion = "unknown_emotion"
        unknown_emotional_state.intensity = 0.5
        unknown_emotional_state.triggers = []

        interventions = self.selector.select_interventions(
            unknown_emotional_state, self.mock_session_state, self.mock_narrative_context
        )

        self.assertIsInstance(interventions, list)
        self.assertGreater(len(interventions), 0)
        self.assertEqual(interventions[0].base_intervention_type, InterventionType.COPING_SKILLS)


class TestSafeExposureTherapyManager(unittest.TestCase):
    """Test the safe exposure therapy manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.exposure_manager = SafeExposureTherapyManager()

        # Create mock emotional state suitable for exposure
        self.mock_emotional_state = Mock()
        self.mock_emotional_state.primary_emotion = EmotionalStateType.ANXIOUS
        self.mock_emotional_state.intensity = 0.4  # Moderate, suitable for exposure
        self.mock_emotional_state.triggers = ["social_situations"]

        # Create mock session state with good progress
        self.mock_session_state = Mock()
        self.mock_session_state.therapeutic_progress = Mock()
        self.mock_session_state.therapeutic_progress.overall_progress_score = 60
        self.mock_session_state.therapeutic_progress.coping_strategies_learned = ["breathing", "grounding", "self-talk"]
        self.mock_session_state.therapeutic_progress.completed_interventions = []

        # Create mock narrative context
        self.mock_narrative_context = Mock()
        self.mock_narrative_context.active_characters = [Mock(name="Therapist")]
        self.mock_narrative_context.current_location = "Safe therapy room"

    def test_assess_exposure_readiness_positive(self):
        """Test exposure readiness assessment for suitable candidate."""
        assessment = self.exposure_manager.assess_exposure_readiness(
            self.mock_emotional_state, self.mock_session_state, "social anxiety"
        )

        self.assertIsInstance(assessment, dict)
        self.assertIn("ready", assessment)
        self.assertIn("readiness_score", assessment)
        self.assertIn("recommended_type", assessment)

        # Should be ready with good progress and moderate intensity
        self.assertTrue(assessment["ready"])
        self.assertGreater(assessment["readiness_score"], 0.5)

    def test_assess_exposure_readiness_negative_high_intensity(self):
        """Test exposure readiness assessment for high intensity emotions."""
        self.mock_emotional_state.intensity = 0.9  # Too high for exposure

        assessment = self.exposure_manager.assess_exposure_readiness(
            self.mock_emotional_state, self.mock_session_state, "social anxiety"
        )

        self.assertFalse(assessment["ready"])
        self.assertIn("High emotional intensity", assessment["safety_concerns"])

    def test_assess_exposure_readiness_negative_crisis_state(self):
        """Test exposure readiness assessment for crisis states."""
        self.mock_emotional_state.primary_emotion = EmotionalStateType.DEPRESSED
        self.mock_emotional_state.intensity = 0.9

        assessment = self.exposure_manager.assess_exposure_readiness(
            self.mock_emotional_state, self.mock_session_state, "social anxiety"
        )

        self.assertFalse(assessment["ready"])
        self.assertIn("Crisis-level emotional state", assessment["contraindications"])

    def test_create_exposure_session_imaginal(self):
        """Test creation of imaginal exposure therapy session."""
        session = self.exposure_manager.create_exposure_session(
            ExposureTherapyType.IMAGINAL,
            "social anxiety",
            self.mock_emotional_state,
            self.mock_narrative_context
        )

        self.assertIsNotNone(session)
        self.assertIsInstance(session, ExposureTherapySession)
        self.assertEqual(session.exposure_type, ExposureTherapyType.IMAGINAL)
        self.assertEqual(session.target_fear_or_trigger, "social anxiety")
        self.assertLessEqual(session.exposure_intensity, 0.4)  # Should be low intensity
        self.assertGreater(len(session.safety_measures), 0)
        self.assertGreater(len(session.escape_mechanisms), 0)

    def test_create_exposure_session_with_contraindications(self):
        """Test that exposure session creation respects contraindications."""
        # Set up high intensity state that should be contraindicated
        self.mock_emotional_state.intensity = 0.9

        session = self.exposure_manager.create_exposure_session(
            ExposureTherapyType.IMAGINAL,
            "social anxiety",
            self.mock_emotional_state,
            self.mock_narrative_context
        )

        # Should return None due to contraindications
        self.assertIsNone(session)

    def test_exposure_scenario_creation(self):
        """Test creation of exposure scenarios."""
        scenario = self.exposure_manager._create_exposure_scenario(
            "social anxiety", 0.3, self.mock_narrative_context
        )

        self.assertIsInstance(scenario, str)
        self.assertGreater(len(scenario), 0)
        self.assertIn("safe", scenario.lower())  # Should emphasize safety

    def test_contraindication_checking(self):
        """Test contraindication checking logic."""
        contraindications = ["active_crisis", "severe_trauma"]

        # Test with crisis-level intensity
        self.mock_emotional_state.intensity = 0.9
        has_contraindications = self.exposure_manager._check_contraindications(
            contraindications, self.mock_emotional_state
        )
        self.assertTrue(has_contraindications)

        # Test with normal intensity
        self.mock_emotional_state.intensity = 0.4
        has_contraindications = self.exposure_manager._check_contraindications(
            contraindications, self.mock_emotional_state
        )
        self.assertFalse(has_contraindications)


class TestEmotionInterventionIntegrator(unittest.TestCase):
    """Test the main emotion-intervention integrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.integrator = EmotionInterventionIntegrator()

        # Create mock emotional analysis result
        self.mock_emotional_analysis = Mock()
        self.mock_emotional_analysis.detected_emotion = Mock()
        self.mock_emotional_analysis.detected_emotion.primary_emotion = EmotionalStateType.ANXIOUS
        self.mock_emotional_analysis.detected_emotion.intensity = 0.5
        self.mock_emotional_analysis.detected_emotion.triggers = ["presentation"]
        self.mock_emotional_analysis.confidence_level = 0.8
        self.mock_emotional_analysis.crisis_indicators = []
        self.mock_emotional_analysis.detected_triggers = [
            Mock(description="public speaking anxiety")
        ]

        # Create mock session state
        self.mock_session_state = Mock()
        self.mock_session_state.therapeutic_progress = Mock()
        self.mock_session_state.therapeutic_progress.overall_progress_score = 50
        self.mock_session_state.therapeutic_progress.completed_interventions = []
        self.mock_session_state.therapeutic_progress.coping_strategies_learned = ["breathing", "grounding"]
        self.mock_session_state.character_states = {}

        # Create mock narrative context
        self.mock_narrative_context = Mock()
        self.mock_narrative_context.recent_events = ["User mentioned upcoming presentation"]
        self.mock_narrative_context.active_characters = [Mock(name="Guide")]

    def test_integrate_emotion_with_interventions_success(self):
        """Test successful emotion-intervention integration."""
        result = self.integrator.integrate_emotion_with_interventions(
            self.mock_emotional_analysis, self.mock_session_state, self.mock_narrative_context
        )

        self.assertIsInstance(result, dict)
        self.assertIn("selected_interventions", result)
        self.assertIn("safety_assessment", result)
        self.assertIn("integration_success", result)

        # Should succeed for moderate anxiety
        self.assertTrue(result["integration_success"])
        self.assertIsInstance(result["selected_interventions"], list)

    def test_integrate_emotion_with_interventions_crisis(self):
        """Test integration when crisis is detected."""
        # Set up crisis-level emotional state
        self.mock_emotional_analysis.detected_emotion.intensity = 0.9
        self.mock_emotional_analysis.crisis_indicators = ["suicidal ideation"]

        result = self.integrator.integrate_emotion_with_interventions(
            self.mock_emotional_analysis, self.mock_session_state, self.mock_narrative_context
        )

        self.assertTrue(result["integration_success"])
        self.assertIsNotNone(result["crisis_response"])
        self.assertTrue(result["safety_assessment"]["crisis_detected"])

    def test_comprehensive_safety_assessment(self):
        """Test comprehensive safety assessment."""
        assessment = self.integrator._perform_comprehensive_safety_assessment(
            self.mock_emotional_analysis, self.mock_session_state, self.mock_narrative_context
        )

        self.assertIsInstance(assessment, dict)
        self.assertIn("crisis_detected", assessment)
        self.assertIn("safety_concerns", assessment)
        self.assertIn("protective_factors", assessment)
        self.assertIn("monitoring_requirements", assessment)

        # Should not detect crisis for moderate anxiety
        self.assertFalse(assessment["crisis_detected"])

    def test_should_consider_exposure_therapy(self):
        """Test exposure therapy consideration logic."""
        # Should consider for moderate anxiety with triggers
        should_consider = self.integrator._should_consider_exposure_therapy(
            self.mock_emotional_analysis, self.mock_session_state
        )
        self.assertTrue(should_consider)

        # Should not consider for high intensity
        self.mock_emotional_analysis.detected_emotion.intensity = 0.9
        should_consider = self.integrator._should_consider_exposure_therapy(
            self.mock_emotional_analysis, self.mock_session_state
        )
        self.assertFalse(should_consider)

    def test_generate_adaptation_metadata(self):
        """Test generation of adaptation metadata."""
        mock_interventions = [
            Mock(
                base_intervention_type=InterventionType.MINDFULNESS,
                therapeutic_effectiveness_score=0.8,
                safety_level=SafetyValidationLevel.STANDARD,
                narrative_integration_points=["Character provides guidance"]
            )
        ]

        metadata = self.integrator._generate_adaptation_metadata(
            self.mock_emotional_analysis, mock_interventions, self.mock_session_state
        )

        self.assertIsInstance(metadata, dict)
        self.assertIn("emotional_context", metadata)
        self.assertIn("intervention_selection", metadata)
        self.assertIn("adaptation_strategies", metadata)
        self.assertIn("session_context", metadata)

    def test_validate_integration(self):
        """Test integration validation."""
        mock_integration_result = {
            "selected_interventions": [Mock()],
            "crisis_response": None,
            "exposure_therapy_session": None
        }

        mock_safety_assessment = {
            "crisis_detected": False,
            "safety_concerns": []
        }

        validation = self.integrator._validate_integration(
            mock_integration_result, mock_safety_assessment
        )

        self.assertIsInstance(validation, dict)
        self.assertIn("success", validation)
        self.assertIn("validation_checks", validation)
        self.assertTrue(validation["success"])

    def test_fallback_interventions(self):
        """Test generation of fallback interventions."""
        fallback_interventions = self.integrator._generate_fallback_interventions(
            self.mock_emotional_analysis.detected_emotion
        )

        self.assertIsInstance(fallback_interventions, list)
        self.assertGreater(len(fallback_interventions), 0)
        self.assertEqual(fallback_interventions[0].base_intervention_type, InterventionType.COPING_SKILLS)
        self.assertEqual(fallback_interventions[0].safety_level, SafetyValidationLevel.ENHANCED)

    def test_emergency_integration_response(self):
        """Test emergency integration response."""
        emergency_response = self.integrator._generate_emergency_integration_response(
            self.mock_emotional_analysis
        )

        self.assertIsInstance(emergency_response, dict)
        self.assertIn("crisis_response", emergency_response)
        self.assertFalse(emergency_response["integration_success"])
        self.assertTrue(emergency_response["error_handled"])
        self.assertIn("safety_resources", emergency_response["crisis_response"])


class TestDataModels(unittest.TestCase):
    """Test data model validation and functionality."""

    def test_emotion_intervention_mapping_validation(self):
        """Test emotion-intervention mapping validation."""
        mapping = EmotionInterventionMapping(
            emotion_type=EmotionalStateType.ANXIOUS,
            intensity_range=(0.0, 0.7),
            primary_interventions=[InterventionType.MINDFULNESS],
            crisis_threshold=0.8
        )

        self.assertTrue(mapping.validate())

        # Test invalid intensity range
        mapping.intensity_range = (0.8, 0.3)  # Invalid: min > max
        with self.assertRaises(Exception):
            mapping.validate()

    def test_adapted_intervention_validation(self):
        """Test adapted intervention validation."""
        intervention = AdaptedIntervention(
            base_intervention_type=InterventionType.MINDFULNESS,
            adapted_content="Practice mindful breathing",
            therapeutic_effectiveness_score=0.8
        )

        self.assertTrue(intervention.validate())

        # Test empty content
        intervention.adapted_content = ""
        with self.assertRaises(Exception):
            intervention.validate()

    def test_exposure_therapy_session_validation(self):
        """Test exposure therapy session validation."""
        session = ExposureTherapySession(
            target_fear_or_trigger="social anxiety",
            exposure_intensity=0.3,
            session_duration_minutes=10
        )

        self.assertTrue(session.validate())

        # Test empty target fear
        session.target_fear_or_trigger = ""
        with self.assertRaises(Exception):
            session.validate()


if __name__ == '__main__':
    unittest.main()
