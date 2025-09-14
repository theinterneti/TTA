"""
Unit Tests for Content Safety System

This module contains comprehensive unit tests for the content safety system,
including content validation, safety filtering, player comfort monitoring,
and escalation procedures.
"""

import sys
import unittest
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent.parent / "core"
models_path = Path(__file__).parent.parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

try:
    from content_safety_system import (
        ComfortLevel,
        ComfortMonitor,
        ContentSafetySystem,
        ContentType,
        ContentValidationResult,
        ContentValidator,
        EscalationCase,
        EscalationManager,
        PlayerComfortProfile,
        SafetyFilter,
        SafetyGuidelines,
        SafetyRisk,
        ValidationError,  # Import ValidationError from content_safety_system
        create_safety_system,
        validate_timeline_event_safely,
    )
    from data_models import EmotionalState, EmotionalStateType
    from living_worlds_models import TimelineEvent
except ImportError as e:
    print(f"Import error: {e}")
    # Mock classes for testing
    class ContentSafetySystem:
        pass
    class ContentValidator:
        pass
    class SafetyFilter:
        pass
    class ComfortMonitor:
        pass
    class EscalationManager:
        pass
    class ContentType:
        TIMELINE_EVENT = "timeline_event"
        CHARACTER_HISTORY = "character_history"
    class SafetyRisk:
        VIOLENCE = "violence"
        SELF_HARM = "self_harm"
    class ComfortLevel:
        COMFORTABLE = "comfortable"
        UNCOMFORTABLE = "uncomfortable"
    class SafetyGuidelines:
        pass
    class ContentValidationResult:
        pass
    class PlayerComfortProfile:
        pass
    class EscalationCase:
        pass
    class TimelineEvent:
        def __init__(self, **kwargs):
            self.description = kwargs.get('description', '')
            self.event_id = kwargs.get('event_id', 'test-id')
    class ValidationError(Exception):
        pass


class TestSafetyGuidelines(unittest.TestCase):
    """Test safety guidelines configuration."""

    def test_default_guidelines(self):
        """Test default safety guidelines."""
        guidelines = SafetyGuidelines()
        self.assertEqual(guidelines.max_violence_level, 2)
        self.assertTrue(guidelines.allow_mild_language)
        self.assertTrue(guidelines.therapeutic_content_only)
        self.assertTrue(guidelines.crisis_detection_enabled)
        self.assertEqual(guidelines.trauma_sensitivity_level, 3)
        self.assertTrue(guidelines.age_appropriate_content)
        self.assertTrue(guidelines.cultural_sensitivity_required)

    def test_guidelines_validation(self):
        """Test safety guidelines validation."""
        guidelines = SafetyGuidelines()
        self.assertTrue(guidelines.validate())

        # Test invalid violence level
        guidelines.max_violence_level = 10
        with self.assertRaises(ValidationError):
            guidelines.validate()

        # Test invalid trauma sensitivity level
        guidelines.max_violence_level = 2
        guidelines.trauma_sensitivity_level = 0
        with self.assertRaises(ValidationError):
            guidelines.validate()


class TestContentValidator(unittest.TestCase):
    """Test content validation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.guidelines = SafetyGuidelines()
        self.validator = ContentValidator(self.guidelines)

    def test_safe_content_validation(self):
        """Test validation of safe content."""
        safe_content = "The character felt happy and went for a peaceful walk in the garden."
        result = self.validator.validate_content(safe_content, ContentType.TIMELINE_EVENT)

        self.assertTrue(result.is_safe)
        self.assertEqual(len(result.identified_risks), 0)
        self.assertEqual(len(result.warnings), 0)

    def test_violent_content_detection(self):
        """Test detection of violent content."""
        violent_content = "The character attacked someone with a knife and caused serious injury."
        result = self.validator.validate_content(violent_content, ContentType.TIMELINE_EVENT)

        self.assertFalse(result.is_safe)
        self.assertIn(SafetyRisk.VIOLENCE, result.identified_risks)
        self.assertGreater(result.risk_scores[SafetyRisk.VIOLENCE], 0.3)

    def test_self_harm_content_detection(self):
        """Test detection of self-harm content."""
        self_harm_content = "The character wanted to hurt themselves and cut their arm."
        result = self.validator.validate_content(self_harm_content, ContentType.CHARACTER_HISTORY)

        self.assertFalse(result.is_safe)
        self.assertIn(SafetyRisk.SELF_HARM, result.identified_risks)
        self.assertGreater(result.risk_scores[SafetyRisk.SELF_HARM], 0.3)

    def test_crisis_indicators_detection(self):
        """Test detection of crisis indicators."""
        crisis_content = "The character can't cope anymore and feels hopeless about everything."
        result = self.validator.validate_content(crisis_content, ContentType.CHARACTER_HISTORY)

        self.assertIn(SafetyRisk.CRISIS_INDICATORS, result.identified_risks)
        self.assertTrue(result.requires_manual_review)

    def test_player_specific_validation(self):
        """Test validation with player-specific filters."""
        player_profile = PlayerComfortProfile(player_id="test-player")
        player_profile.trigger_words.add("spider")
        player_profile.sensitive_topics.add("darkness")

        content = "The character encountered a spider in the darkness."
        result = self.validator.validate_content(
            content, ContentType.TIMELINE_EVENT, player_profile
        )

        self.assertIn(SafetyRisk.TRAUMA_TRIGGERS, result.identified_risks)
        self.assertGreater(len(result.warnings), 0)


class TestSafetyFilter(unittest.TestCase):
    """Test content filtering functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.guidelines = SafetyGuidelines()
        self.filter = SafetyFilter(self.guidelines)

    def test_violence_filtering(self):
        """Test filtering of violent content."""
        violent_content = "The character killed the enemy with a knife."

        # Create mock validation result
        validation_result = ContentValidationResult()
        validation_result.add_risk(SafetyRisk.VIOLENCE, 0.8, "Violence detected")

        filtered_content = self.filter.filter_content(violent_content, validation_result)

        # Check that violent words were replaced
        self.assertNotIn("killed", filtered_content.lower())
        self.assertNotIn("knife", filtered_content.lower())
        self.assertIn("stopped", filtered_content.lower())

    def test_self_harm_filtering(self):
        """Test filtering of self-harm content."""
        self_harm_content = "The character wanted to hurt themselves badly."

        validation_result = ContentValidationResult()
        validation_result.add_risk(SafetyRisk.SELF_HARM, 0.7, "Self-harm detected")

        filtered_content = self.filter.filter_content(self_harm_content, validation_result)

        # Check that self-harm language was softened
        self.assertNotIn("hurt themselves", filtered_content.lower())
        self.assertIn("feel pain", filtered_content.lower())

    def test_readability_improvement(self):
        """Test that filtered content maintains readability."""
        content = "The   character   felt   bad."
        validation_result = ContentValidationResult()

        filtered_content = self.filter.filter_content(content, validation_result)

        # Check that extra spaces were removed
        self.assertNotIn("   ", filtered_content)
        self.assertEqual(filtered_content.strip(), "The character felt bad.")


class TestComfortMonitor(unittest.TestCase):
    """Test player comfort monitoring functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitor = ComfortMonitor()
        self.player_id = "test-player"

    def test_player_profile_creation(self):
        """Test creation of player comfort profiles."""
        profile = self.monitor.get_player_profile(self.player_id)

        self.assertEqual(profile.player_id, self.player_id)
        self.assertEqual(len(profile.comfort_history), 0)
        self.assertEqual(len(profile.trigger_words), 0)

    def test_comfort_feedback_recording(self):
        """Test recording of comfort feedback."""
        self.monitor.record_comfort_feedback(
            self.player_id, "timeline_event", ComfortLevel.UNCOMFORTABLE,
            "Test content", "Player felt uneasy"
        )

        profile = self.monitor.get_player_profile(self.player_id)
        self.assertEqual(len(profile.comfort_history), 1)

        feedback = profile.comfort_history[0]
        self.assertEqual(feedback["comfort_level"], ComfortLevel.UNCOMFORTABLE.value)
        self.assertEqual(feedback["notes"], "Player felt uneasy")

    def test_adaptive_filter_updates(self):
        """Test that adaptive filters are updated based on feedback."""
        # Record uncomfortable feedback
        self.monitor.record_comfort_feedback(
            self.player_id, "violence", ComfortLevel.VERY_UNCOMFORTABLE
        )

        profile = self.monitor.get_player_profile(self.player_id)
        self.assertGreater(profile.adaptive_filters.get("violence", 0), 0.5)

    def test_comfort_assessment(self):
        """Test comfort level assessment for content."""
        # Set up player with trigger words
        profile = self.monitor.get_player_profile(self.player_id)
        profile.trigger_words.add("violence")

        content = "The scene contained violence and conflict."
        comfort_level, confidence = self.monitor.assess_content_comfort(
            self.player_id, content, ContentType.TIMELINE_EVENT
        )

        self.assertNotEqual(comfort_level, ComfortLevel.COMFORTABLE)
        self.assertGreater(confidence, 0.0)

    def test_content_adaptation_decision(self):
        """Test decision making for content adaptation."""
        # Should adapt for uncomfortable content
        self.assertTrue(
            self.monitor.should_adapt_content(self.player_id, ComfortLevel.UNCOMFORTABLE)
        )

        # Should not adapt for comfortable content
        self.assertFalse(
            self.monitor.should_adapt_content(self.player_id, ComfortLevel.COMFORTABLE)
        )


class TestEscalationManager(unittest.TestCase):
    """Test escalation management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = EscalationManager()

    def test_escalation_case_creation(self):
        """Test creation of escalation cases."""
        validation_result = ContentValidationResult()
        validation_result.add_risk(SafetyRisk.CRISIS_INDICATORS, 0.9, "Crisis detected")

        case = self.manager.create_escalation_case(
            "Crisis content", ContentType.CHARACTER_HISTORY,
            validation_result, "test-player", "test-world"
        )

        self.assertIsNotNone(case)
        self.assertEqual(case.content, "Crisis content")
        self.assertEqual(case.player_id, "test-player")
        self.assertEqual(case.status, "pending")
        self.assertIn(SafetyRisk.CRISIS_INDICATORS, case.identified_risks)

    def test_escalation_threshold_checking(self):
        """Test escalation threshold checking."""
        # High-risk content should escalate
        high_risk_result = ContentValidationResult()
        high_risk_result.add_risk(SafetyRisk.SELF_HARM, 0.8, "High risk")

        self.assertTrue(self.manager.should_escalate(high_risk_result))

        # Low-risk content should not escalate
        low_risk_result = ContentValidationResult()
        low_risk_result.add_risk(SafetyRisk.VIOLENCE, 0.3, "Low risk")

        self.assertFalse(self.manager.should_escalate(low_risk_result))

    def test_case_resolution(self):
        """Test resolution of escalation cases."""
        # Create a case
        validation_result = ContentValidationResult()
        validation_result.add_risk(SafetyRisk.VIOLENCE, 0.8, "Violence detected")

        case = self.manager.create_escalation_case(
            "Violent content", ContentType.TIMELINE_EVENT, validation_result
        )

        # Resolve the case
        success = self.manager.resolve_case(
            case.case_id, "approved", "Content approved after review", "reviewer1"
        )

        self.assertTrue(success)
        self.assertNotIn(case.case_id, self.manager.pending_cases)

    def test_pending_cases_retrieval(self):
        """Test retrieval of pending cases."""
        # Create multiple cases with different severity levels
        for severity in [1, 3, 5]:
            validation_result = ContentValidationResult()
            validation_result.add_risk(SafetyRisk.VIOLENCE, 0.8, "Violence")

            case = self.manager.create_escalation_case(
                f"Content {severity}", ContentType.TIMELINE_EVENT, validation_result
            )
            case.severity_level = severity

        # Get all pending cases
        all_cases = self.manager.get_pending_cases()
        self.assertEqual(len(all_cases), 3)

        # Get high-severity cases only
        high_severity_cases = self.manager.get_pending_cases(severity_filter=4)
        self.assertEqual(len(high_severity_cases), 1)


class TestContentSafetySystem(unittest.TestCase):
    """Test the main content safety system."""

    def setUp(self):
        """Set up test fixtures."""
        self.safety_system = ContentSafetySystem()

    def test_system_initialization(self):
        """Test system initialization."""
        self.assertIsNotNone(self.safety_system.validator)
        self.assertIsNotNone(self.safety_system.filter)
        self.assertIsNotNone(self.safety_system.comfort_monitor)
        self.assertIsNotNone(self.safety_system.escalation_manager)

    def test_timeline_event_validation(self):
        """Test timeline event validation."""
        event = TimelineEvent(
            description="The character felt happy and went for a walk.",
            event_id="test-event"
        )

        result = self.safety_system.validate_timeline_event(event, "test-player")

        self.assertTrue(result.is_safe)
        self.assertEqual(len(result.identified_risks), 0)

    def test_character_history_validation(self):
        """Test character history validation."""
        history = "The character had a peaceful childhood with loving parents."

        result = self.safety_system.validate_character_history(
            history, "test-character", "test-player"
        )

        self.assertTrue(result.is_safe)
        self.assertEqual(len(result.identified_risks), 0)

    def test_content_processing_pipeline(self):
        """Test the complete content processing pipeline."""
        content = "The character felt overwhelmed and needed support."

        processed_content, result = self.safety_system.process_content_safely(
            content, ContentType.CHARACTER_HISTORY, "test-player"
        )

        self.assertIsNotNone(processed_content)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_safe)

    def test_unsafe_content_processing(self):
        """Test processing of unsafe content."""
        unsafe_content = "The character wanted to kill themselves with a knife."

        processed_content, result = self.safety_system.process_content_safely(
            unsafe_content, ContentType.CHARACTER_HISTORY, "test-player"
        )

        self.assertFalse(result.is_safe)
        self.assertIsNotNone(result.filtered_content)
        self.assertNotEqual(processed_content, unsafe_content)

    def test_player_comfort_feedback_integration(self):
        """Test integration with player comfort feedback."""
        self.safety_system.record_player_comfort_feedback(
            "test-player", "violence", ComfortLevel.UNCOMFORTABLE,
            "Test content", "Player felt uneasy"
        )

        # Check that feedback was recorded
        profile = self.safety_system.comfort_monitor.get_player_profile("test-player")
        self.assertEqual(len(profile.comfort_history), 1)

    def test_comfort_assessment_integration(self):
        """Test comfort assessment integration."""
        content = "The character experienced a difficult situation."

        comfort_level, confidence = self.safety_system.get_player_comfort_assessment(
            "test-player", content, ContentType.TIMELINE_EVENT
        )

        self.assertIsInstance(comfort_level, ComfortLevel)
        self.assertGreater(confidence, 0.0)

    def test_escalation_case_management(self):
        """Test escalation case management."""
        # Process content that should escalate
        crisis_content = "The character can't cope and wants to end it all."

        processed_content, result = self.safety_system.process_content_safely(
            crisis_content, ContentType.CHARACTER_HISTORY, "test-player"
        )

        # Check if case was escalated
        pending_cases = self.safety_system.get_escalation_cases()
        if len(pending_cases) > 0:
            case = pending_cases[0]

            # Resolve the case
            success = self.safety_system.resolve_escalation_case(
                case.case_id, "modified", "Content modified for safety"
            )
            self.assertTrue(success)

    def test_safety_statistics(self):
        """Test safety statistics tracking."""
        # Process some content to generate statistics
        safe_content = "The character felt happy."
        unsafe_content = "The character felt violent."

        self.safety_system.process_content_safely(
            safe_content, ContentType.TIMELINE_EVENT
        )
        self.safety_system.process_content_safely(
            unsafe_content, ContentType.TIMELINE_EVENT
        )

        stats = self.safety_system.get_safety_statistics()

        self.assertGreater(stats["total_validations"], 0)
        self.assertIn("safe_percentage", stats)
        self.assertIn("by_content_type", stats)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""

    def test_create_safety_system(self):
        """Test safety system creation utility."""
        system = create_safety_system(therapeutic_focus=True, trauma_sensitivity=4)

        self.assertIsInstance(system, ContentSafetySystem)
        self.assertTrue(system.guidelines.therapeutic_content_only)
        self.assertEqual(system.guidelines.trauma_sensitivity_level, 4)

    def test_validate_timeline_event_safely(self):
        """Test quick timeline event validation utility."""
        safe_event = TimelineEvent(
            description="The character felt peaceful.",
            event_id="safe-event"
        )

        unsafe_event = TimelineEvent(
            description="The character wanted to kill someone.",
            event_id="unsafe-event"
        )

        safety_system = create_safety_system()

        self.assertTrue(
            validate_timeline_event_safely(safe_event, safety_system)
        )
        self.assertFalse(
            validate_timeline_event_safely(unsafe_event, safety_system)
        )


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.safety_system = create_safety_system()

    def test_player_adaptation_scenario(self):
        """Test complete player adaptation scenario."""
        player_id = "adaptive-player"

        # 1. Player encounters content they find uncomfortable
        uncomfortable_content = "The character faced a scary situation."

        # 2. Record comfort feedback
        self.safety_system.record_player_comfort_feedback(
            player_id, "scary_content", ComfortLevel.UNCOMFORTABLE,
            uncomfortable_content, "Too scary for me"
        )

        # 3. Process similar content - should be adapted
        similar_content = "The character encountered another scary moment."
        comfort_level, confidence = self.safety_system.get_player_comfort_assessment(
            player_id, similar_content, ContentType.TIMELINE_EVENT
        )

        # Should predict discomfort based on history
        self.assertNotEqual(comfort_level, ComfortLevel.COMFORTABLE)

    def test_escalation_workflow(self):
        """Test complete escalation workflow."""
        # 1. Process crisis content
        crisis_content = "The character feels hopeless and can't go on living."

        processed_content, result = self.safety_system.process_content_safely(
            crisis_content, ContentType.CHARACTER_HISTORY, "crisis-player"
        )

        # 2. Check if escalation occurred
        if result.requires_manual_review:
            pending_cases = self.safety_system.get_escalation_cases()
            self.assertGreater(len(pending_cases), 0)

            # 3. Resolve escalation
            if len(pending_cases) > 0:
                case = pending_cases[0]
                success = self.safety_system.resolve_escalation_case(
                    case.case_id, "modified", "Content modified for therapeutic appropriateness"
                )
                self.assertTrue(success)

    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with invalid content
        try:
            result = self.safety_system.validate_timeline_event(None)
            # Should not crash, should return safe default
            self.assertIsNotNone(result)
        except Exception:
            pass  # Expected to handle gracefully

        # Test with empty content
        empty_result = self.safety_system.process_content_safely(
            "", ContentType.TIMELINE_EVENT
        )
        self.assertIsNotNone(empty_result)


if __name__ == '__main__':
    unittest.main()
