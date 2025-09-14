"""
Integration Tests for Therapeutic Dialogue System

This module contains comprehensive integration tests for the therapeutic dialogue system,
including character management agent, voice consistency, and therapeutic intervention delivery.
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
    from character_development_system import CharacterDevelopmentSystem
    from data_models import (
        CharacterState,
        DialogueStyle,
        EmotionalState,
        EmotionalStateType,
        InterventionType,
    )
    from therapeutic_dialogue_system import (
        CharacterManagementAgent,
        CharacterVoiceManager,
        DialogueType,
        TherapeuticDialogueGenerator,
        TherapeuticDialogueRequest,
        TherapeuticDialogueResponse,
        TherapeuticInterventionDelivery,
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback for when running as part of package
    from ..core.therapeutic_dialogue_system import (
        CharacterManagementAgent,
        CharacterVoiceManager,
        DialogueType,
        TherapeuticDialogueGenerator,
        TherapeuticDialogueRequest,
        TherapeuticDialogueResponse,
        TherapeuticInterventionDelivery,
    )
    from ..models.data_models import (
        CharacterState,
        DialogueStyle,
        EmotionalState,
        EmotionalStateType,
        InterventionType,
    )


class TestTherapeuticDialogueRequest(unittest.TestCase):
    """Test TherapeuticDialogueRequest dataclass."""

    def test_valid_dialogue_request(self):
        """Test creating a valid dialogue request."""
        request = TherapeuticDialogueRequest(
            character_id="therapist_001",
            dialogue_type=DialogueType.INTERVENTION,
            intervention_type=InterventionType.MINDFULNESS,
            urgency_level=0.7
        )
        self.assertTrue(request.validate())

    def test_invalid_character_id(self):
        """Test validation fails for empty character ID."""
        with self.assertRaises(Exception):
            request = TherapeuticDialogueRequest(
                character_id="",
                dialogue_type=DialogueType.SUPPORT
            )
            request.validate()

    def test_invalid_urgency_level(self):
        """Test validation fails for invalid urgency level."""
        with self.assertRaises(Exception):
            request = TherapeuticDialogueRequest(
                character_id="therapist_001",
                dialogue_type=DialogueType.SUPPORT,
                urgency_level=1.5
            )
            request.validate()


class TestTherapeuticDialogueResponse(unittest.TestCase):
    """Test TherapeuticDialogueResponse dataclass."""

    def test_valid_dialogue_response(self):
        """Test creating a valid dialogue response."""
        response = TherapeuticDialogueResponse(
            character_id="therapist_001",
            dialogue_content="I understand how difficult this must be for you.",
            dialogue_type=DialogueType.SUPPORT,
            therapeutic_value=0.8,
            emotional_impact=0.5,
            character_consistency_score=0.9
        )
        self.assertTrue(response.validate())

    def test_invalid_empty_content(self):
        """Test validation fails for empty dialogue content."""
        with self.assertRaises(Exception):
            response = TherapeuticDialogueResponse(
                character_id="therapist_001",
                dialogue_content="",
                dialogue_type=DialogueType.SUPPORT
            )
            response.validate()

    def test_invalid_therapeutic_value(self):
        """Test validation fails for invalid therapeutic value."""
        with self.assertRaises(Exception):
            response = TherapeuticDialogueResponse(
                character_id="therapist_001",
                dialogue_content="Test content",
                dialogue_type=DialogueType.SUPPORT,
                therapeutic_value=1.5
            )
            response.validate()


class TestCharacterVoiceManager(unittest.TestCase):
    """Test CharacterVoiceManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.voice_manager = CharacterVoiceManager()
        self.therapist_character = CharacterState(
            character_id="therapist_001",
            name="Dr. Sarah Wilson",
            personality_traits={"empathy": 0.9, "patience": 0.8},
            therapeutic_role="therapist",
            dialogue_style=DialogueStyle(
                formality_level=0.8,
                empathy_level=0.9,
                directness=0.6,
                therapeutic_approach="supportive"
            )
        )

    def test_generate_character_voice_therapist(self):
        """Test generating character voice for therapist."""
        dialogue = "This is a difficult situation to handle."

        voiced_dialogue = self.voice_manager.generate_character_voice(
            self.therapist_character, dialogue
        )

        self.assertIsInstance(voiced_dialogue, str)
        self.assertIn("difficult", voiced_dialogue)
        # Should maintain formal language for high formality character
        self.assertNotIn("can't", voiced_dialogue)

    def test_generate_character_voice_with_intervention(self):
        """Test generating character voice with therapeutic intervention."""
        dialogue = "Let's work on managing your anxiety."

        voiced_dialogue = self.voice_manager.generate_character_voice(
            self.therapist_character, dialogue, InterventionType.MINDFULNESS
        )

        self.assertIsInstance(voiced_dialogue, str)
        self.assertGreater(len(voiced_dialogue), len(dialogue))  # Should be enhanced

    def test_validate_voice_consistency_consistent(self):
        """Test voice consistency validation for consistent dialogue."""
        consistent_dialogue = "I understand that this situation is challenging for you. Let us explore this together."

        consistency_score, issues = self.voice_manager.validate_voice_consistency(
            self.therapist_character, consistent_dialogue
        )

        self.assertGreaterEqual(consistency_score, 0.7)
        self.assertEqual(len(issues), 0)

    def test_validate_voice_consistency_inconsistent(self):
        """Test voice consistency validation for inconsistent dialogue."""
        inconsistent_dialogue = "Hey, yeah, whatever you wanna do is fine with me."

        consistency_score, issues = self.voice_manager.validate_voice_consistency(
            self.therapist_character, inconsistent_dialogue
        )

        self.assertLess(consistency_score, 0.7)
        self.assertGreater(len(issues), 0)

    def test_apply_character_style_formal(self):
        """Test applying formal character style."""
        content = "You're going to be fine, you can't give up now."

        styled_content = self.voice_manager._apply_character_style(
            content, self.therapist_character
        )

        # Should convert contractions for formal character
        self.assertIn("you are", styled_content)
        self.assertIn("cannot", styled_content)

    def test_apply_character_style_casual(self):
        """Test applying casual character style."""
        casual_character = CharacterState(
            character_id="companion_001",
            name="Alex",
            therapeutic_role="companion",
            dialogue_style=DialogueStyle(formality_level=0.2)
        )

        content = "You are going to be fine, you cannot give up now."

        styled_content = self.voice_manager._apply_character_style(
            content, casual_character
        )

        # Should add contractions for casual character
        self.assertIn("you're", styled_content)
        self.assertIn("can't", styled_content)


class TestTherapeuticDialogueGenerator(unittest.TestCase):
    """Test TherapeuticDialogueGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = TherapeuticDialogueGenerator()
        self.character_state = CharacterState(
            character_id="therapist_001",
            name="Dr. Sarah Wilson",
            therapeutic_role="therapist"
        )

    def test_generate_therapeutic_dialogue_intervention(self):
        """Test generating therapeutic dialogue for intervention."""
        request = TherapeuticDialogueRequest(
            character_id="therapist_001",
            dialogue_type=DialogueType.INTERVENTION,
            intervention_type=InterventionType.MINDFULNESS,
            narrative_context="User is feeling anxious"
        )

        dialogue = self.generator.generate_therapeutic_dialogue(request, self.character_state)

        self.assertIsInstance(dialogue, str)
        self.assertGreater(len(dialogue), 10)
        # Should contain mindfulness-related content
        self.assertTrue(any(word in dialogue.lower() for word in ["present", "breath", "moment", "ground"]))

    def test_generate_therapeutic_dialogue_support(self):
        """Test generating supportive therapeutic dialogue."""
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.ANXIOUS,
            intensity=0.7
        )

        request = TherapeuticDialogueRequest(
            character_id="therapist_001",
            dialogue_type=DialogueType.SUPPORT,
            user_emotional_state=emotional_state
        )

        dialogue = self.generator.generate_therapeutic_dialogue(request, self.character_state)

        self.assertIsInstance(dialogue, str)
        self.assertGreater(len(dialogue), 10)
        # Should contain supportive language
        self.assertTrue(any(word in dialogue.lower() for word in ["support", "here", "together", "understand"]))

    def test_generate_therapeutic_dialogue_assessment(self):
        """Test generating assessment dialogue."""
        request = TherapeuticDialogueRequest(
            character_id="therapist_001",
            dialogue_type=DialogueType.ASSESSMENT,
            narrative_context="Initial session"
        )

        dialogue = self.generator.generate_therapeutic_dialogue(request, self.character_state)

        self.assertIsInstance(dialogue, str)
        self.assertGreater(len(dialogue), 10)
        # Should contain assessment-related questions
        self.assertTrue(any(word in dialogue.lower() for word in ["how", "what", "feel", "experience"]))

    def test_enhance_with_character_context(self):
        """Test enhancing dialogue with character context."""
        base_dialogue = "I want to help you with this situation."

        # Add some memories to character
        self.character_state.memory_fragments = []
        self.character_state.add_memory("Previous discussion about anxiety", 0.6, ["anxiety"])

        request = TherapeuticDialogueRequest(
            character_id="therapist_001",
            dialogue_type=DialogueType.SUPPORT,
            narrative_context="anxiety management",
            relationship_context={"user": 0.7}
        )

        enhanced_dialogue = self.generator._enhance_with_character_context(
            base_dialogue, self.character_state, request
        )

        self.assertGreater(len(enhanced_dialogue), len(base_dialogue))
        # Should reference previous conversation or relationship
        self.assertTrue(any(word in enhanced_dialogue.lower()
                          for word in ["remember", "before", "connection", "comfortable"]))


class TestTherapeuticInterventionDelivery(unittest.TestCase):
    """Test TherapeuticInterventionDelivery class."""

    def setUp(self):
        """Set up test fixtures."""
        self.delivery = TherapeuticInterventionDelivery()
        self.therapist_character = CharacterState(
            character_id="therapist_001",
            name="Dr. Sarah Wilson",
            therapeutic_role="therapist",
            dialogue_style=DialogueStyle(empathy_level=0.9)
        )

    def test_deliver_mindfulness_intervention(self):
        """Test delivering mindfulness intervention."""
        response = self.delivery.deliver_intervention(
            InterventionType.MINDFULNESS,
            self.therapist_character,
            {"user_anxiety_level": 0.8}
        )

        self.assertIsInstance(response, TherapeuticDialogueResponse)
        self.assertEqual(response.intervention_delivered, InterventionType.MINDFULNESS)
        self.assertGreater(response.therapeutic_value, 0.5)
        self.assertGreater(response.emotional_impact, 0.0)
        # Should contain mindfulness-related content
        self.assertTrue(any(word in response.dialogue_content.lower()
                          for word in ["breath", "present", "moment", "ground"]))

    def test_deliver_cognitive_restructuring_intervention(self):
        """Test delivering cognitive restructuring intervention."""
        response = self.delivery.deliver_intervention(
            InterventionType.COGNITIVE_RESTRUCTURING,
            self.therapist_character,
            {"negative_thoughts": ["I'm a failure", "Nothing will work"]}
        )

        self.assertIsInstance(response, TherapeuticDialogueResponse)
        self.assertEqual(response.intervention_delivered, InterventionType.COGNITIVE_RESTRUCTURING)
        self.assertGreater(response.therapeutic_value, 0.5)
        # Should contain cognitive restructuring language
        self.assertTrue(any(word in response.dialogue_content.lower()
                          for word in ["examine", "thoughts", "perspective", "evidence"]))

    def test_deliver_intervention_mentor_role(self):
        """Test delivering intervention with mentor character."""
        mentor_character = CharacterState(
            character_id="mentor_001",
            name="Wise Guide",
            therapeutic_role="mentor",
            dialogue_style=DialogueStyle(empathy_level=0.8)
        )

        response = self.delivery.deliver_intervention(
            InterventionType.COPING_SKILLS,
            mentor_character,
            {}
        )

        self.assertIsInstance(response, TherapeuticDialogueResponse)
        # Should reflect mentor's wisdom-sharing approach
        self.assertTrue(any(word in response.dialogue_content.lower()
                          for word in ["experience", "learn", "wisdom", "share"]))

    def test_calculate_intervention_value(self):
        """Test calculating intervention therapeutic value."""
        value = self.delivery._calculate_intervention_value(
            InterventionType.EMOTIONAL_REGULATION,
            self.therapist_character,
            {}
        )

        self.assertIsInstance(value, float)
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)
        self.assertGreater(value, 0.5)  # Should be high for therapist with high empathy

    def test_calculate_emotional_impact(self):
        """Test calculating emotional impact of intervention."""
        impact = self.delivery._calculate_emotional_impact(
            InterventionType.MINDFULNESS,
            self.therapist_character,
            {}
        )

        self.assertIsInstance(impact, float)
        self.assertGreaterEqual(impact, 0.0)
        self.assertLessEqual(impact, 1.0)
        self.assertGreater(impact, 0.0)  # Should have positive impact


class TestCharacterManagementAgent(unittest.TestCase):
    """Test CharacterManagementAgent main class."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = CharacterManagementAgent()

        # Create test character
        self.test_character = self.agent.character_system.create_character(
            character_id="test_therapist",
            name="Dr. Emily Chen",
            personality_traits={
                "empathy": 0.9,
                "patience": 0.8,
                "wisdom": 0.7
            },
            therapeutic_role="therapist"
        )

    def test_generate_therapeutic_dialogue_intervention(self):
        """Test generating therapeutic dialogue for intervention."""
        request = TherapeuticDialogueRequest(
            character_id="test_therapist",
            dialogue_type=DialogueType.INTERVENTION,
            intervention_type=InterventionType.MINDFULNESS,
            narrative_context="User experiencing anxiety before presentation",
            urgency_level=0.6
        )

        response = self.agent.generate_therapeutic_dialogue(request)

        self.assertIsInstance(response, TherapeuticDialogueResponse)
        self.assertEqual(response.character_id, "test_therapist")
        self.assertEqual(response.dialogue_type, DialogueType.INTERVENTION)
        self.assertEqual(response.intervention_delivered, InterventionType.MINDFULNESS)
        self.assertGreater(response.therapeutic_value, 0.0)
        self.assertGreaterEqual(response.character_consistency_score, 0.5)
        self.assertTrue(response.validate())

    def test_generate_therapeutic_dialogue_support(self):
        """Test generating supportive therapeutic dialogue."""
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.DEPRESSED,
            intensity=0.8
        )

        request = TherapeuticDialogueRequest(
            character_id="test_therapist",
            dialogue_type=DialogueType.SUPPORT,
            user_emotional_state=emotional_state,
            narrative_context="User feeling hopeless about recovery"
        )

        response = self.agent.generate_therapeutic_dialogue(request)

        self.assertIsInstance(response, TherapeuticDialogueResponse)
        self.assertEqual(response.dialogue_type, DialogueType.SUPPORT)
        self.assertGreater(response.therapeutic_value, 0.0)
        self.assertGreater(response.emotional_impact, 0.0)  # Should be positive/supportive
        # Should contain supportive language for depression
        self.assertTrue(any(word in response.dialogue_content.lower()
                          for word in ["support", "alone", "here", "strength"]))

    def test_generate_therapeutic_dialogue_assessment(self):
        """Test generating assessment dialogue."""
        request = TherapeuticDialogueRequest(
            character_id="test_therapist",
            dialogue_type=DialogueType.ASSESSMENT,
            narrative_context="First therapy session",
            specific_goals=["understand anxiety triggers", "develop coping skills"]
        )

        response = self.agent.generate_therapeutic_dialogue(request)

        self.assertIsInstance(response, TherapeuticDialogueResponse)
        self.assertEqual(response.dialogue_type, DialogueType.ASSESSMENT)
        self.assertGreater(response.therapeutic_value, 0.0)
        # Should contain assessment questions
        self.assertTrue(any(word in response.dialogue_content.lower()
                          for word in ["how", "what", "tell", "describe", "experience"]))

    def test_generate_dialogue_nonexistent_character(self):
        """Test generating dialogue for non-existent character."""
        request = TherapeuticDialogueRequest(
            character_id="nonexistent_character",
            dialogue_type=DialogueType.SUPPORT
        )

        response = self.agent.generate_therapeutic_dialogue(request)

        self.assertIsInstance(response, TherapeuticDialogueResponse)
        self.assertIn("error", response.metadata)
        self.assertLess(response.therapeutic_value, 0.5)  # Should be low for error case

    def test_get_character_dialogue_context(self):
        """Test getting character dialogue context."""
        context = self.agent.get_character_dialogue_context(
            "test_therapist",
            {"user_id": "test_user", "session_id": "session_001"}
        )

        self.assertIsInstance(context, dict)
        self.assertIn("character_state", context)
        self.assertIn("development_summary", context)
        self.assertIn("recent_memories", context)

        # Check character state details
        char_state = context["character_state"]
        self.assertEqual(char_state["name"], "Dr. Emily Chen")
        self.assertEqual(char_state["therapeutic_role"], "therapist")
        self.assertIn("personality_traits", char_state)
        self.assertIn("dialogue_style", char_state)

    def test_get_dialogue_context_nonexistent_character(self):
        """Test getting dialogue context for non-existent character."""
        context = self.agent.get_character_dialogue_context(
            "nonexistent_character",
            {"user_id": "test_user"}
        )

        self.assertIn("error", context)

    def test_character_state_update_from_dialogue(self):
        """Test that character state is updated after dialogue generation."""
        # Get initial memory count
        initial_memories = len(self.test_character.memory_fragments)

        request = TherapeuticDialogueRequest(
            character_id="test_therapist",
            dialogue_type=DialogueType.INTERVENTION,
            intervention_type=InterventionType.EMOTIONAL_REGULATION,
            narrative_context="Helping user process grief"
        )

        self.agent.generate_therapeutic_dialogue(request)

        # Check that character was updated
        updated_character = self.agent.character_system.get_character_state("test_therapist")
        self.assertGreater(len(updated_character.memory_fragments), initial_memories)

    def test_voice_consistency_maintained(self):
        """Test that character voice consistency is maintained across interactions."""
        # Generate multiple dialogues and check consistency
        requests = [
            TherapeuticDialogueRequest(
                character_id="test_therapist",
                dialogue_type=DialogueType.ASSESSMENT,
                narrative_context="Initial session"
            ),
            TherapeuticDialogueRequest(
                character_id="test_therapist",
                dialogue_type=DialogueType.INTERVENTION,
                intervention_type=InterventionType.MINDFULNESS,
                narrative_context="Anxiety management"
            ),
            TherapeuticDialogueRequest(
                character_id="test_therapist",
                dialogue_type=DialogueType.SUPPORT,
                narrative_context="Emotional support needed"
            )
        ]

        responses = []
        for request in requests:
            response = self.agent.generate_therapeutic_dialogue(request)
            responses.append(response)

        # All responses should have good consistency scores
        for response in responses:
            self.assertGreaterEqual(response.character_consistency_score, 0.7)

        # Check that therapeutic role is maintained across all responses
        for response in responses:
            # Should contain professional therapeutic language
            self.assertTrue(any(word in response.dialogue_content.lower()
                              for word in ["understand", "explore", "help", "support", "together"]))


class TestSystemIntegration(unittest.TestCase):
    """Test integration between therapeutic dialogue system components."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = CharacterManagementAgent()

        # Create multiple test characters with different roles
        self.therapist = self.agent.character_system.create_character(
            character_id="integration_therapist",
            name="Dr. Sarah Martinez",
            personality_traits={"empathy": 0.9, "patience": 0.8, "wisdom": 0.8},
            therapeutic_role="therapist"
        )

        self.mentor = self.agent.character_system.create_character(
            character_id="integration_mentor",
            name="Wise Elder",
            personality_traits={"empathy": 0.7, "wisdom": 0.9, "patience": 0.9},
            therapeutic_role="mentor"
        )

        self.companion = self.agent.character_system.create_character(
            character_id="integration_companion",
            name="Caring Friend",
            personality_traits={"empathy": 0.8, "supportiveness": 0.9, "patience": 0.7},
            therapeutic_role="companion"
        )

    def test_multi_character_dialogue_consistency(self):
        """Test dialogue consistency across different character types."""
        # Same intervention request for different characters
        base_request = {
            "dialogue_type": DialogueType.INTERVENTION,
            "intervention_type": InterventionType.EMOTIONAL_REGULATION,
            "narrative_context": "User struggling with anger management",
            "urgency_level": 0.6
        }

        characters = ["integration_therapist", "integration_mentor", "integration_companion"]
        responses = {}

        for char_id in characters:
            request = TherapeuticDialogueRequest(character_id=char_id, **base_request)
            response = self.agent.generate_therapeutic_dialogue(request)
            responses[char_id] = response

        # All should be valid responses
        for response in responses.values():
            self.assertTrue(response.validate())
            self.assertGreater(response.therapeutic_value, 0.0)
            self.assertGreaterEqual(response.character_consistency_score, 0.7)

        # But should reflect different character approaches
        therapist_response = responses["integration_therapist"]
        mentor_response = responses["integration_mentor"]
        companion_response = responses["integration_companion"]

        # Therapist should use more clinical language
        self.assertTrue(any(word in therapist_response.dialogue_content.lower()
                          for word in ["examine", "explore", "understand", "technique"]))

        # Mentor should use wisdom-based language
        self.assertTrue(any(word in mentor_response.dialogue_content.lower()
                          for word in ["experience", "learn", "wisdom", "journey"]))

        # Companion should use supportive language
        self.assertTrue(any(word in companion_response.dialogue_content.lower()
                          for word in ["together", "support", "here", "care"]))

    def test_therapeutic_progression_over_time(self):
        """Test therapeutic dialogue progression over multiple sessions."""
        character_id = "integration_therapist"

        # Simulate progression from assessment to intervention to reflection
        session_requests = [
            TherapeuticDialogueRequest(
                character_id=character_id,
                dialogue_type=DialogueType.ASSESSMENT,
                narrative_context="First session - getting to know the user"
            ),
            TherapeuticDialogueRequest(
                character_id=character_id,
                dialogue_type=DialogueType.INTERVENTION,
                intervention_type=InterventionType.COGNITIVE_RESTRUCTURING,
                narrative_context="Working on negative thought patterns"
            ),
            TherapeuticDialogueRequest(
                character_id=character_id,
                dialogue_type=DialogueType.INTERVENTION,
                intervention_type=InterventionType.COPING_SKILLS,
                narrative_context="Building practical coping strategies"
            ),
            TherapeuticDialogueRequest(
                character_id=character_id,
                dialogue_type=DialogueType.REFLECTION,
                narrative_context="Reflecting on progress made"
            )
        ]

        responses = []
        for request in session_requests:
            response = self.agent.generate_therapeutic_dialogue(request)
            responses.append(response)

        # All responses should be valid
        for response in responses:
            self.assertTrue(response.validate())
            self.assertGreater(response.therapeutic_value, 0.0)

        # Character should maintain consistency across sessions
        for response in responses:
            self.assertGreaterEqual(response.character_consistency_score, 0.7)

        # Later sessions should reference relationship building
        final_context = self.agent.get_character_dialogue_context(character_id, {"user_id": "test_user"})
        self.assertGreater(len(final_context["recent_memories"]), 0)

    def test_crisis_intervention_handling(self):
        """Test handling of crisis intervention scenarios."""
        crisis_request = TherapeuticDialogueRequest(
            character_id="integration_therapist",
            dialogue_type=DialogueType.CRISIS,
            narrative_context="User expressing suicidal ideation",
            urgency_level=1.0
        )

        response = self.agent.generate_therapeutic_dialogue(crisis_request)

        self.assertTrue(response.validate())
        self.assertEqual(response.dialogue_type, DialogueType.CRISIS)
        self.assertGreater(response.therapeutic_value, 0.5)

        # Should contain crisis-appropriate language
        self.assertTrue(any(word in response.dialogue_content.lower()
                          for word in ["safety", "support", "help", "concern", "care"]))

        # Should maintain character consistency even in crisis
        self.assertGreaterEqual(response.character_consistency_score, 0.5)


if __name__ == "__main__":
    unittest.main()
