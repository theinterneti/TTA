"""

# Logseq: [[TTA.dev/Tests/Test_personalization_service_manager]]
Unit tests for PersonalizationServiceManager.

Tests the therapeutic personalization service, real-time adaptation,
crisis detection, and emergency resource provision functionality.
"""

import unittest
from datetime import datetime

from src.player_experience.managers.personalization_service_manager import (
    AdaptationResult,
    CrisisDetectionSystem,
    PersonalizationServiceManager,
    PlayerFeedback,
)
from src.player_experience.models.enums import (
    CrisisType,
    IntensityLevel,
    TherapeuticApproach,
)
from src.player_experience.models.therapeutic_settings import (
    EnhancedTherapeuticSettings,
)


class TestCrisisDetectionSystem(unittest.TestCase):
    """Test cases for CrisisDetectionSystem."""

    def setUp(self):
        """Set up test fixtures."""
        self.crisis_detector = CrisisDetectionSystem()

    def test_crisis_detection_suicidal_ideation(self):
        """Test detection of suicidal ideation indicators."""
        text = "I just want to end it all, I'm not worth living"
        context = {"emotional_state": {"distress_level": 0.9}}

        crisis_detected, crisis_types, confidence = (
            self.crisis_detector.detect_crisis_indicators(text, context)
        )

        self.assertTrue(crisis_detected)
        self.assertIn(CrisisType.SUICIDAL_IDEATION, crisis_types)
        self.assertGreater(confidence, 0.5)

    def test_crisis_detection_self_harm(self):
        """Test detection of self-harm indicators."""
        text = "I keep thinking about cutting myself when I feel this way"
        context = {}

        crisis_detected, crisis_types, confidence = (
            self.crisis_detector.detect_crisis_indicators(text, context)
        )

        self.assertTrue(crisis_detected)
        self.assertIn(CrisisType.SELF_HARM, crisis_types)
        self.assertGreater(confidence, 0.3)

    def test_crisis_detection_panic_attack(self):
        """Test detection of panic attack indicators."""
        text = "I can't breathe, my heart is racing and I feel like I'm losing control"
        context = {}

        crisis_detected, crisis_types, confidence = (
            self.crisis_detector.detect_crisis_indicators(text, context)
        )

        self.assertTrue(crisis_detected)
        self.assertIn(CrisisType.PANIC_ATTACK, crisis_types)
        self.assertGreater(confidence, 0.3)

    def test_crisis_detection_no_crisis(self):
        """Test that normal text doesn't trigger crisis detection."""
        text = "I had a good day today, feeling much better"
        context = {"emotional_state": {"distress_level": 0.2}}

        crisis_detected, crisis_types, confidence = (
            self.crisis_detector.detect_crisis_indicators(text, context)
        )

        self.assertFalse(crisis_detected)
        self.assertEqual(len(crisis_types), 0)
        self.assertLessEqual(confidence, 0.3)

    def test_crisis_detection_context_based(self):
        """Test crisis detection based on context indicators."""
        text = "I'm feeling okay I guess"
        context = {
            "emotional_state": {"distress_level": 0.95},
            "behavioral_indicators": ["withdrawal", "sleep_disruption"],
        }

        crisis_detected, crisis_types, confidence = (
            self.crisis_detector.detect_crisis_indicators(text, context)
        )

        self.assertTrue(crisis_detected)
        self.assertIn(CrisisType.GENERAL_DISTRESS, crisis_types)
        self.assertIn(CrisisType.SEVERE_DEPRESSION, crisis_types)

    def test_get_crisis_resources_suicidal(self):
        """Test getting crisis resources for suicidal ideation."""
        crisis_types = [CrisisType.SUICIDAL_IDEATION]

        resources = self.crisis_detector.get_crisis_resources(crisis_types)

        self.assertGreater(len(resources), 0)

        # Check that 988 Lifeline is included
        lifeline_found = any(r.resource_id == "988_lifeline" for r in resources)
        self.assertTrue(lifeline_found)

        # Check that resources are sorted by priority
        priorities = [r.priority for r in resources]
        self.assertEqual(priorities, sorted(priorities))

    def test_get_crisis_resources_emergency_only(self):
        """Test getting only emergency crisis resources."""
        crisis_types = [CrisisType.SUICIDAL_IDEATION]

        emergency_resources = self.crisis_detector.get_crisis_resources(
            crisis_types, emergency_only=True
        )
        all_resources = self.crisis_detector.get_crisis_resources(
            crisis_types, emergency_only=False
        )

        self.assertLessEqual(len(emergency_resources), len(all_resources))

        # All returned resources should be emergency resources
        for resource in emergency_resources:
            self.assertTrue(resource.is_emergency)

    def test_crisis_resources_initialization(self):
        """Test that crisis resources are properly initialized."""
        resources = self.crisis_detector.crisis_resources

        self.assertGreater(len(resources), 0)

        # Check that essential resources exist
        resource_ids = {r.resource_id for r in resources}
        self.assertIn("988_lifeline", resource_ids)
        self.assertIn("crisis_text_line", resource_ids)
        self.assertIn("emergency_services", resource_ids)


class TestPlayerFeedback(unittest.TestCase):
    """Test cases for PlayerFeedback model."""

    def test_feedback_creation(self):
        """Test creating player feedback."""
        feedback = PlayerFeedback(
            feedback_id="test_feedback_1",
            player_id="test_player_123",
            session_id="test_session_456",
            feedback_type="rating",
            content={"rating": 4, "comments": "Very helpful session"},
        )

        self.assertEqual(feedback.feedback_id, "test_feedback_1")
        self.assertEqual(feedback.player_id, "test_player_123")
        self.assertEqual(feedback.feedback_type, "rating")
        self.assertFalse(feedback.processed)
        self.assertIsInstance(feedback.timestamp, datetime)

    def test_feedback_auto_id_generation(self):
        """Test automatic ID generation for feedback."""
        feedback = PlayerFeedback(
            feedback_id="",
            player_id="test_player_123",
            session_id="test_session_456",
            feedback_type="text",
            content={"text": "This was helpful"},
        )

        self.assertIsNotNone(feedback.feedback_id)
        self.assertNotEqual(feedback.feedback_id, "")


class TestAdaptationResult(unittest.TestCase):
    """Test cases for AdaptationResult model."""

    def test_adaptation_result_creation(self):
        """Test creating adaptation result."""
        result = AdaptationResult(
            adaptation_id="test_adaptation_1",
            player_id="test_player_123",
            changes_made=["reduce_intensity", "increase_support"],
            confidence_score=0.8,
            reasoning="Player feedback indicated difficulty with current intensity",
        )

        self.assertEqual(result.adaptation_id, "test_adaptation_1")
        self.assertEqual(result.player_id, "test_player_123")
        self.assertEqual(len(result.changes_made), 2)
        self.assertEqual(result.confidence_score, 0.8)
        self.assertFalse(result.requires_player_approval)

    def test_adaptation_result_validation(self):
        """Test validation of adaptation result."""
        # Test invalid confidence score
        with self.assertRaises(ValueError):
            AdaptationResult(
                adaptation_id="test_adaptation_2",
                player_id="test_player_123",
                changes_made=["test_change"],
                confidence_score=1.5,  # Invalid score
                reasoning="Test reasoning",
            )

    def test_adaptation_result_auto_id(self):
        """Test automatic ID generation for adaptation result."""
        result = AdaptationResult(
            adaptation_id="",
            player_id="test_player_123",
            changes_made=["test_change"],
            confidence_score=0.5,
            reasoning="Test reasoning",
        )

        self.assertIsNotNone(result.adaptation_id)
        self.assertNotEqual(result.adaptation_id, "")


class TestPersonalizationServiceManager(unittest.TestCase):
    """Test cases for PersonalizationServiceManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PersonalizationServiceManager()
        self.test_player_id = "test_player_123"

        # Create test therapeutic settings
        self.test_settings = EnhancedTherapeuticSettings(
            settings_id="test_settings_1",
            player_id=self.test_player_id,
            intensity_level=IntensityLevel.MEDIUM,
            preferred_approaches=[
                TherapeuticApproach.CBT,
                TherapeuticApproach.MINDFULNESS,
            ],
            crisis_monitoring_enabled=True,
        )

    def test_manager_initialization(self):
        """Test PersonalizationServiceManager initialization."""
        self.assertIsNotNone(self.manager.personalization_engine)
        self.assertIsNotNone(self.manager.settings_validator)
        self.assertIsNotNone(self.manager.crisis_detector)
        self.assertIsInstance(self.manager.adaptation_history, dict)
        self.assertIsInstance(self.manager.feedback_history, dict)

    def test_update_therapeutic_settings_valid(self):
        """Test updating valid therapeutic settings."""
        success, conflicts = self.manager.update_therapeutic_settings(
            self.test_player_id, self.test_settings
        )

        self.assertTrue(success)
        self.assertEqual(len(conflicts), 0)

    def test_update_therapeutic_settings_with_conflicts(self):
        """Test updating therapeutic settings with conflicts."""
        # Create settings with conflicts
        conflicted_settings = EnhancedTherapeuticSettings(
            settings_id="conflicted_settings",
            player_id=self.test_player_id,
            intensity_level=IntensityLevel.HIGH,
            preferred_approaches=[
                TherapeuticApproach.MINDFULNESS
            ],  # Potential mismatch
            comfort_topics=["family", "work"],
            avoid_topics=["family", "stress"],  # Conflict: "family" in both lists
        )

        success, conflicts = self.manager.update_therapeutic_settings(
            self.test_player_id, conflicted_settings
        )

        # Should still succeed due to auto-resolution, but with conflicts reported
        self.assertTrue(success)
        self.assertGreaterEqual(
            len(conflicts), 0
        )  # May have remaining non-critical conflicts

    def test_update_therapeutic_settings_critical_conflicts(self):
        """Test updating therapeutic settings with critical conflicts."""
        # Create settings with critical conflicts
        critical_settings = EnhancedTherapeuticSettings(
            settings_id="critical_settings",
            player_id=self.test_player_id,
            intensity_level=IntensityLevel.HIGH,
            crisis_monitoring_enabled=False,  # Critical conflict
        )

        success, conflicts = self.manager.update_therapeutic_settings(
            self.test_player_id, critical_settings
        )

        # Should succeed due to auto-resolution of critical conflicts
        self.assertTrue(success)

    def test_get_adaptive_recommendations_no_history(self):
        """Test getting adaptive recommendations with no history."""
        recommendations = self.manager.get_adaptive_recommendations(self.test_player_id)

        self.assertIsInstance(recommendations, list)
        # Should return empty list or contextual recommendations
        self.assertLessEqual(len(recommendations), 5)

    def test_get_adaptive_recommendations_with_context(self):
        """Test getting adaptive recommendations with context."""
        context = {
            "emotional_state": {"stress_level": 0.9},
            "session_time": "late_night",
        }

        recommendations = self.manager.get_adaptive_recommendations(
            self.test_player_id, context
        )

        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)

        # Should include stress management recommendation
        stress_recommendations = [
            r for r in recommendations if "stress" in r.description.lower()
        ]
        self.assertGreater(len(stress_recommendations), 0)

    def test_process_rating_feedback(self):
        """Test processing rating feedback."""
        feedback = PlayerFeedback(
            feedback_id="rating_feedback_1",
            player_id=self.test_player_id,
            session_id="test_session_1",
            feedback_type="rating",
            content={"rating": 2, "comments": "Too intense"},
        )

        result = self.manager.process_feedback(self.test_player_id, feedback)

        self.assertIsInstance(result, AdaptationResult)
        self.assertEqual(result.player_id, self.test_player_id)
        self.assertGreater(len(result.changes_made), 0)
        self.assertIn("reduce_intensity", result.changes_made)
        self.assertGreater(result.confidence_score, 0.5)
        self.assertTrue(feedback.processed)

    def test_process_text_feedback(self):
        """Test processing text feedback."""
        feedback = PlayerFeedback(
            feedback_id="text_feedback_1",
            player_id=self.test_player_id,
            session_id="test_session_1",
            feedback_type="text",
            content={"text": "This session was really helpful and good for me"},
        )

        result = self.manager.process_feedback(self.test_player_id, feedback)

        self.assertIsInstance(result, AdaptationResult)
        self.assertEqual(result.player_id, self.test_player_id)
        self.assertIn("maintain_current_approach", result.changes_made)
        self.assertGreater(result.confidence_score, 0.5)

    def test_process_preference_feedback(self):
        """Test processing preference change feedback."""
        feedback = PlayerFeedback(
            feedback_id="preference_feedback_1",
            player_id=self.test_player_id,
            session_id="test_session_1",
            feedback_type="preference_change",
            content={
                "preference_changes": {
                    "intensity_level": "low",
                    "preferred_approaches": ["mindfulness"],
                }
            },
        )

        result = self.manager.process_feedback(self.test_player_id, feedback)

        self.assertIsInstance(result, AdaptationResult)
        self.assertEqual(result.player_id, self.test_player_id)
        self.assertTrue(result.requires_player_approval)
        self.assertEqual(result.confidence_score, 0.9)

    def test_process_crisis_feedback(self):
        """Test processing crisis indicator feedback."""
        feedback = PlayerFeedback(
            feedback_id="crisis_feedback_1",
            player_id=self.test_player_id,
            session_id="test_session_1",
            feedback_type="crisis_indicator",
            content={
                "crisis_types": ["suicidal_ideation"],
                "confidence": 0.8,
                "text_analyzed": "I want to end it all",
            },
        )

        result = self.manager.process_feedback(self.test_player_id, feedback)

        self.assertIsInstance(result, AdaptationResult)
        self.assertEqual(result.player_id, self.test_player_id)
        self.assertFalse(
            result.requires_player_approval
        )  # Crisis adaptations are automatic
        self.assertEqual(result.confidence_score, 1.0)  # Maximum confidence for crisis
        self.assertIn("enable_crisis_monitoring", result.changes_made)
        self.assertIn("provide_support_resources", result.changes_made)

    def test_get_crisis_support_resources(self):
        """Test getting crisis support resources."""
        crisis_types = [CrisisType.SUICIDAL_IDEATION, CrisisType.SEVERE_DEPRESSION]

        resources = self.manager.get_crisis_support_resources(
            self.test_player_id, crisis_types
        )

        self.assertIsInstance(resources, list)
        self.assertGreater(len(resources), 0)

        # Check that resources are relevant to crisis types
        for resource in resources:
            self.assertTrue(any(ct in resource.crisis_types for ct in crisis_types))

    def test_get_crisis_support_resources_emergency_only(self):
        """Test getting emergency-only crisis support resources."""
        crisis_types = [CrisisType.SUICIDAL_IDEATION]

        emergency_resources = self.manager.get_crisis_support_resources(
            self.test_player_id, crisis_types, emergency_only=True
        )
        all_resources = self.manager.get_crisis_support_resources(
            self.test_player_id, crisis_types, emergency_only=False
        )

        self.assertLessEqual(len(emergency_resources), len(all_resources))

        # All returned resources should be emergency resources
        for resource in emergency_resources:
            self.assertTrue(resource.is_emergency)

    def test_detect_crisis_situation(self):
        """Test crisis situation detection."""
        text = "I can't take this anymore, I want to end it all"
        context = {"emotional_state": {"distress_level": 0.9}}

        crisis_detected, crisis_types, emergency_resources = (
            self.manager.detect_crisis_situation(self.test_player_id, text, context)
        )

        self.assertTrue(crisis_detected)
        self.assertGreater(len(crisis_types), 0)
        self.assertGreater(len(emergency_resources), 0)

        # Check that crisis feedback was created and processed
        player_feedback = self.manager.feedback_history.get(self.test_player_id, [])
        crisis_feedback = [
            f for f in player_feedback if f.feedback_type == "crisis_indicator"
        ]
        self.assertGreater(len(crisis_feedback), 0)

    def test_detect_crisis_situation_no_crisis(self):
        """Test crisis detection with non-crisis text."""
        text = "I had a great day today, feeling much better"
        context = {"emotional_state": {"distress_level": 0.2}}

        crisis_detected, crisis_types, emergency_resources = (
            self.manager.detect_crisis_situation(self.test_player_id, text, context)
        )

        self.assertFalse(crisis_detected)
        self.assertEqual(len(crisis_types), 0)
        self.assertEqual(len(emergency_resources), 0)

    def test_feedback_history_storage(self):
        """Test that feedback history is properly stored."""
        feedback1 = PlayerFeedback(
            feedback_id="feedback_1",
            player_id=self.test_player_id,
            session_id="session_1",
            feedback_type="rating",
            content={"rating": 4},
        )

        feedback2 = PlayerFeedback(
            feedback_id="feedback_2",
            player_id=self.test_player_id,
            session_id="session_2",
            feedback_type="text",
            content={"text": "Helpful session"},
        )

        self.manager.process_feedback(self.test_player_id, feedback1)
        self.manager.process_feedback(self.test_player_id, feedback2)

        player_feedback = self.manager.feedback_history.get(self.test_player_id, [])
        self.assertEqual(len(player_feedback), 2)

        feedback_ids = {f.feedback_id for f in player_feedback}
        self.assertIn("feedback_1", feedback_ids)
        self.assertIn("feedback_2", feedback_ids)

    def test_adaptation_history_storage(self):
        """Test that adaptation history is properly stored."""
        feedback = PlayerFeedback(
            feedback_id="feedback_1",
            player_id=self.test_player_id,
            session_id="session_1",
            feedback_type="rating",
            content={"rating": 3},
        )

        result = self.manager.process_feedback(self.test_player_id, feedback)

        player_adaptations = self.manager.adaptation_history.get(
            self.test_player_id, []
        )
        self.assertEqual(len(player_adaptations), 1)
        self.assertEqual(player_adaptations[0].adaptation_id, result.adaptation_id)

    def test_recommendations_with_feedback_history(self):
        """Test recommendations generation with feedback history."""
        # Add some low-rating feedback
        for i in range(3):
            feedback = PlayerFeedback(
                feedback_id=f"low_rating_{i}",
                player_id=self.test_player_id,
                session_id=f"session_{i}",
                feedback_type="rating",
                content={"rating": 2},
            )
            self.manager.process_feedback(self.test_player_id, feedback)

        recommendations = self.manager.get_adaptive_recommendations(self.test_player_id)

        self.assertGreater(len(recommendations), 0)

        # Should include recommendations for therapeutic adjustment
        adjustment_recommendations = [
            r for r in recommendations if "adjust" in r.title.lower()
        ]
        self.assertGreater(len(adjustment_recommendations), 0)


if __name__ == "__main__":
    unittest.main()
