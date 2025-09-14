"""
Integration tests for LangGraph Integration

This module contains comprehensive tests for the therapeutic agent integration,
covering IPA and NGA enhancements, context passing, and error handling.
"""

# Import the classes to test
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tta.prototype.core.langgraph_integration import (
    AgentResponse,
    TherapeuticAgentOrchestrator,
    TherapeuticContext,
    TherapeuticIPA,
    TherapeuticNGA,
)


class TestTherapeuticContext(unittest.TestCase):
    """Test cases for TherapeuticContext."""

    def test_therapeutic_context_creation(self):
        """Test TherapeuticContext creation and conversion."""
        context = TherapeuticContext(
            session_id="test_session",
            user_emotional_state={"anxiety": 0.7},
            therapeutic_goals=["manage_anxiety", "improve_mood"],
            current_location="therapy_room",
            available_characters=["therapist", "companion"]
        )

        self.assertEqual(context.session_id, "test_session")
        self.assertEqual(context.user_emotional_state["anxiety"], 0.7)
        self.assertEqual(len(context.therapeutic_goals), 2)

        # Test dictionary conversion
        context_dict = context.to_dict()
        self.assertIn("session_id", context_dict)
        self.assertIn("emotional_state", context_dict)
        self.assertIn("therapeutic_goals", context_dict)


class TestTherapeuticIPA(unittest.TestCase):
    """Test cases for TherapeuticIPA."""

    def setUp(self):
        """Set up test fixtures."""
        self.ipa = TherapeuticIPA()
        self.test_context = TherapeuticContext(
            session_id="test_session",
            therapeutic_goals=["anxiety_management"],
            current_location="garden",
            therapeutic_opportunities=["breathing_exercise"]
        )

    def test_initialization(self):
        """Test IPA initialization."""
        self.assertIsInstance(self.ipa.therapeutic_intent_patterns, dict)
        self.assertIn("anxiety_management", self.ipa.therapeutic_intent_patterns)
        self.assertIn("emotional_regulation", self.ipa.therapeutic_intent_patterns)
        self.assertIsInstance(self.ipa.emotional_indicators, dict)

    def test_basic_input_parsing(self):
        """Test basic input parsing functionality."""
        # Test look command
        result = self.ipa._basic_input_parsing("look around")
        self.assertEqual(result["intent"], "look")

        # Test movement command
        result = self.ipa._basic_input_parsing("go north")
        self.assertEqual(result["intent"], "move")
        self.assertEqual(result["direction"], "north")

        # Test character interaction
        result = self.ipa._basic_input_parsing("talk to therapist")
        self.assertEqual(result["intent"], "talk")
        self.assertEqual(result["character_name"], "therapist")

    def test_therapeutic_intent_analysis(self):
        """Test therapeutic intent analysis."""
        # Test anxiety-related input
        anxiety_input = "I'm feeling really anxious and need to calm down"
        intents = self.ipa._analyze_therapeutic_intent(anxiety_input)
        self.assertIn("anxiety_management", intents)

        # Test emotional regulation input
        emotion_input = "I'm angry and need to control my feelings"
        intents = self.ipa._analyze_therapeutic_intent(emotion_input)
        self.assertIn("emotional_regulation", intents)

        # Test social connection input
        social_input = "I feel lonely and want to connect with someone"
        intents = self.ipa._analyze_therapeutic_intent(social_input)
        self.assertIn("social_connection", intents)

    def test_emotional_indicator_detection(self):
        """Test emotional indicator detection."""
        # Test anxious indicators
        anxious_input = "I'm worried and nervous about this"
        emotions = self.ipa._detect_emotional_indicators(anxious_input)
        self.assertIn("anxious", emotions)
        self.assertGreater(emotions["anxious"], 0)

        # Test calm indicators
        calm_input = "I feel peaceful and relaxed now"
        emotions = self.ipa._detect_emotional_indicators(calm_input)
        self.assertIn("calm", emotions)

        # Test multiple emotions
        mixed_input = "I'm sad but also excited about the future"
        emotions = self.ipa._detect_emotional_indicators(mixed_input)
        self.assertIn("depressed", emotions)  # "sad" maps to "depressed"
        self.assertIn("excited", emotions)

    def test_context_enhancement(self):
        """Test context-based enhancement."""
        parsed_input = {
            "intent": "talk",
            "character_name": "therapist",
            "original_input": "talk to therapist about anxiety"
        }

        # Add character relationship to context
        self.test_context.character_relationships["therapist"] = 0.8

        enhancements = self.ipa._enhance_with_context(parsed_input, self.test_context)

        self.assertIn("character_relationship_score", enhancements)
        self.assertEqual(enhancements["character_relationship_score"], 0.8)

    def test_therapeutic_priority_calculation(self):
        """Test therapeutic priority calculation."""
        high_priority_input = {
            "therapeutic_intent": ["anxiety_management", "emotional_regulation"],
            "detected_emotions": {"anxious": 0.8, "worried": 0.6},
            "relevant_therapeutic_goals": ["manage_anxiety"]
        }

        priority = self.ipa._calculate_therapeutic_priority(high_priority_input, self.test_context)
        self.assertGreater(priority, 0.5)

        low_priority_input = {
            "therapeutic_intent": [],
            "detected_emotions": {},
            "relevant_therapeutic_goals": []
        }

        priority = self.ipa._calculate_therapeutic_priority(low_priority_input, self.test_context)
        self.assertLess(priority, 0.3)

    def test_full_input_processing(self):
        """Test complete input processing pipeline."""
        user_input = "I'm feeling anxious and want to practice breathing"

        result = self.ipa.process_input(user_input, self.test_context)

        self.assertIn("intent", result)
        self.assertIn("therapeutic_intent", result)
        self.assertIn("detected_emotions", result)
        self.assertIn("therapeutic_priority", result)

        # Should detect anxiety management intent
        self.assertIn("anxiety_management", result["therapeutic_intent"])

        # Should detect anxious emotion
        self.assertIn("anxious", result["detected_emotions"])

        # Should have high therapeutic priority
        self.assertGreater(result["therapeutic_priority"], 0.3)

    def test_fallback_parsing(self):
        """Test fallback parsing mechanism."""
        result = self.ipa._fallback_parsing("some random input")

        self.assertEqual(result["intent"], "unknown")
        self.assertIn("original_input", result)
        self.assertIn("therapeutic_intent", result)
        self.assertIn("error", result)


class TestTherapeuticNGA(unittest.TestCase):
    """Test cases for TherapeuticNGA."""

    def setUp(self):
        """Set up test fixtures."""
        self.nga = TherapeuticNGA()
        self.test_context = TherapeuticContext(
            session_id="test_session",
            user_emotional_state={"anxious": 0.7},
            therapeutic_goals=["anxiety_management"],
            user_progress={"anxiety_management": 0.3}
        )

    def test_initialization(self):
        """Test NGA initialization."""
        self.assertIsInstance(self.nga.therapeutic_narrative_templates, dict)
        self.assertIn("anxiety_management", self.nga.therapeutic_narrative_templates)
        self.assertIsInstance(self.nga.emotional_tone_mappings, dict)

    def test_narrative_type_determination(self):
        """Test narrative type determination."""
        # High therapeutic priority input
        high_priority_input = {
            "therapeutic_priority": 0.8,
            "therapeutic_intent": ["anxiety_management"]
        }

        narrative_type = self.nga._determine_narrative_type(high_priority_input, self.test_context)
        self.assertEqual(narrative_type, "anxiety_management")

        # Emotional indicator input
        emotional_input = {
            "therapeutic_priority": 0.3,
            "detected_emotions": {"anxious": 0.8}
        }

        narrative_type = self.nga._determine_narrative_type(emotional_input, self.test_context)
        self.assertEqual(narrative_type, "anxiety_management")

    def test_base_narrative_generation(self):
        """Test base narrative generation."""
        # Test look intent
        look_input = {"intent": "look"}
        narrative = self.nga._generate_base_narrative(look_input, "general_therapeutic")
        self.assertIn("observe", narrative.lower())

        # Test move intent
        move_input = {"intent": "move", "direction": "north"}
        narrative = self.nga._generate_base_narrative(move_input, "general_therapeutic")
        self.assertIn("north", narrative.lower())

        # Test talk intent
        talk_input = {"intent": "talk", "character_name": "therapist"}
        narrative = self.nga._generate_base_narrative(talk_input, "general_therapeutic")
        self.assertIn("therapist", narrative.lower())

    def test_therapeutic_enhancements(self):
        """Test therapeutic enhancement addition."""
        base_content = "You take a deep breath."

        therapeutic_input = {
            "therapeutic_intent": ["anxiety_management"]
        }

        enhanced = self.nga._add_therapeutic_enhancements(
            base_content, therapeutic_input, self.test_context
        )

        self.assertNotEqual(enhanced, base_content)
        self.assertIn(base_content, enhanced)

    def test_emotional_tone_application(self):
        """Test emotional tone application."""
        content = "You practice mindfulness."

        calming_input = {
            "therapeutic_intent": ["anxiety_management"]
        }

        toned_content = self.nga._apply_emotional_tone(
            content, calming_input, self.test_context
        )

        self.assertIn("peaceful", toned_content.lower())

    def test_therapeutic_value_calculation(self):
        """Test therapeutic value calculation."""
        high_value_input = {
            "therapeutic_priority": 0.8,
            "relevant_therapeutic_goals": ["anxiety_management"],
            "detected_emotions": {"anxious": 0.7}
        }

        value = self.nga._calculate_therapeutic_value(high_value_input, self.test_context)
        self.assertGreater(value, 0.5)

        low_value_input = {
            "therapeutic_priority": 0.1,
            "relevant_therapeutic_goals": [],
            "detected_emotions": {}
        }

        value = self.nga._calculate_therapeutic_value(low_value_input, self.test_context)
        self.assertLess(value, 0.3)

    def test_full_narrative_generation(self):
        """Test complete narrative generation."""
        parsed_input = {
            "intent": "look",
            "therapeutic_intent": ["anxiety_management"],
            "detected_emotions": {"anxious": 0.6},
            "therapeutic_priority": 0.7
        }

        response = self.nga.generate_narrative(parsed_input, self.test_context)

        self.assertIsInstance(response, AgentResponse)
        self.assertTrue(response.success)
        self.assertGreater(len(response.content), 0)
        self.assertGreater(response.therapeutic_value, 0)
        self.assertEqual(response.agent_type, "therapeutic_nga")

    def test_fallback_narrative(self):
        """Test fallback narrative generation."""
        response = self.nga._generate_fallback_narrative({})

        self.assertIsInstance(response, AgentResponse)
        self.assertTrue(response.success)
        self.assertIn("therapeutic journey", response.content)
        self.assertGreater(response.therapeutic_value, 0)


class TestTherapeuticAgentOrchestrator(unittest.TestCase):
    """Test cases for TherapeuticAgentOrchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = TherapeuticAgentOrchestrator()
        self.test_context = TherapeuticContext(
            session_id="test_session",
            therapeutic_goals=["anxiety_management"],
            current_location="therapy_room"
        )

    def test_initialization(self):
        """Test orchestrator initialization."""
        self.assertIsInstance(self.orchestrator.ipa, TherapeuticIPA)
        self.assertIsInstance(self.orchestrator.nga, TherapeuticNGA)
        self.assertEqual(self.orchestrator.error_count, 0)

    def test_successful_interaction_processing(self):
        """Test successful user interaction processing."""
        user_input = "I'm feeling anxious and want to practice breathing"

        response, updated_context = self.orchestrator.process_user_interaction(
            user_input, self.test_context
        )

        self.assertIsInstance(response, AgentResponse)
        self.assertTrue(response.success)
        self.assertGreater(len(response.content), 0)
        self.assertIsInstance(updated_context, TherapeuticContext)

        # Check that context was updated
        self.assertGreater(len(updated_context.narrative_history), 0)

    def test_context_updating(self):
        """Test therapeutic context updating."""
        parsed_input = {
            "detected_emotions": {"anxious": 0.7},
            "therapeutic_intent": ["anxiety_management"]
        }

        nga_response = AgentResponse(
            agent_type="therapeutic_nga",
            success=True,
            content="You practice breathing.",
            therapeutic_value=0.6
        )

        updated_context = self.orchestrator._update_therapeutic_context(
            self.test_context, parsed_input, nga_response
        )

        # Check narrative history was updated
        self.assertIn("You practice breathing.", updated_context.narrative_history)

        # Check emotional state was updated
        self.assertIn("anxious", updated_context.user_emotional_state)

        # Check progress was updated
        self.assertIn("anxiety_management", updated_context.user_progress)
        self.assertGreater(updated_context.user_progress["anxiety_management"], 0)

    def test_error_handling(self):
        """Test error handling mechanisms."""
        # Test with invalid input that might cause errors
        user_input = ""

        response, updated_context = self.orchestrator.process_user_interaction(
            user_input, self.test_context
        )

        # Should still return a valid response
        self.assertIsInstance(response, AgentResponse)
        self.assertTrue(response.success)
        self.assertIsInstance(updated_context, TherapeuticContext)

    @patch.object(TherapeuticIPA, 'process_input')
    def test_ipa_failure_handling(self, mock_process_input):
        """Test IPA failure handling."""
        mock_process_input.side_effect = Exception("IPA Error")

        response, updated_context = self.orchestrator.process_user_interaction(
            "test input", self.test_context
        )

        self.assertIsInstance(response, AgentResponse)
        self.assertTrue(response.success)
        self.assertIn("fallback", response.metadata.get("fallback_reason", ""))

    @patch.object(TherapeuticNGA, 'generate_narrative')
    def test_nga_failure_handling(self, mock_generate_narrative):
        """Test NGA failure handling."""
        mock_generate_narrative.return_value = AgentResponse(
            agent_type="therapeutic_nga",
            success=False,
            error_message="NGA Error"
        )

        response, updated_context = self.orchestrator.process_user_interaction(
            "test input", self.test_context
        )

        self.assertIsInstance(response, AgentResponse)
        self.assertTrue(response.success)
        self.assertIn("fallback", response.metadata.get("fallback_reason", ""))

    def test_agent_status(self):
        """Test agent status reporting."""
        status = self.orchestrator.get_agent_status()

        self.assertIn("ipa_status", status)
        self.assertIn("nga_status", status)
        self.assertIn("error_count", status)
        self.assertIn("health", status)
        self.assertEqual(status["health"], "healthy")

    def test_error_count_management(self):
        """Test error count management."""

        # Simulate errors
        self.orchestrator.error_count = 2
        self.assertEqual(self.orchestrator.error_count, 2)

        # Reset error count
        self.orchestrator.reset_error_count()
        self.assertEqual(self.orchestrator.error_count, 0)


class TestAgentResponse(unittest.TestCase):
    """Test cases for AgentResponse."""

    def test_agent_response_creation(self):
        """Test AgentResponse creation."""
        response = AgentResponse(
            agent_type="test_agent",
            success=True,
            content="Test content",
            therapeutic_value=0.5
        )

        self.assertEqual(response.agent_type, "test_agent")
        self.assertTrue(response.success)
        self.assertEqual(response.content, "Test content")
        self.assertEqual(response.therapeutic_value, 0.5)

    def test_response_validation(self):
        """Test response validation."""
        valid_response = AgentResponse(
            agent_type="test",
            success=True,
            content="Valid content"
        )
        self.assertTrue(valid_response.is_valid())

        invalid_response = AgentResponse(
            agent_type="test",
            success=False,
            content="Content"
        )
        self.assertFalse(invalid_response.is_valid())

        empty_response = AgentResponse(
            agent_type="test",
            success=True,
            content=""
        )
        self.assertFalse(empty_response.is_valid())


if __name__ == '__main__':
    unittest.main()
