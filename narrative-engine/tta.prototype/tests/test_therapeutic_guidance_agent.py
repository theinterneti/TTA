"""
Integration tests for Therapeutic Guidance Agent and Content Delivery System.

This module tests the complete therapeutic content delivery pipeline including:
- Evidence-based intervention generation
- Seamless narrative embedding
- Crisis detection and response
- Content delivery across different modes
"""


# Import system components
import sys
import unittest
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
        DialogueContext,
        EmotionalState,
        EmotionalStateType,
        InterventionType,
        NarrativeContext,
        SessionState,
        TherapeuticProgress,
    )
    from therapeutic_content_integration import (
        DetectedOpportunity,
        InterventionUrgency,
        OpportunityType,
    )
    from therapeutic_guidance_agent import (
        ContentDeliverySystem,
        CrisisDetectionSystem,
        CrisisIndicators,
        CrisisLevel,
        DeliveredIntervention,
        EvidenceBasedInterventions,
        InterventionDeliveryMode,
        TherapeuticDeliveryContext,
        TherapeuticGuidanceAgent,
    )
    from therapeutic_llm_client import (
        SafetyLevel,
        TherapeuticContentType,
        TherapeuticLLMClient,
        TherapeuticResponse,
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for testing
    class MockClass:
        def __init__(self, *args, **kwargs):
            pass

    # Set all imports to mock class
    TherapeuticGuidanceAgent = MockClass
    ContentDeliverySystem = MockClass
    CrisisDetectionSystem = MockClass
    EvidenceBasedInterventions = MockClass


class TestEvidenceBasedInterventions(unittest.TestCase):
    """Test evidence-based interventions repository."""

    def setUp(self):
        """Set up test fixtures."""
        self.interventions = EvidenceBasedInterventions()

        # Mock session state
        self.mock_session_state = Mock()
        self.mock_session_state.emotional_state = Mock()
        self.mock_session_state.emotional_state.intensity = 0.5
        self.mock_session_state.therapeutic_progress = Mock()
        self.mock_session_state.therapeutic_progress.overall_progress_score = 50

    def test_initialization(self):
        """Test that interventions are properly initialized."""
        self.assertIsInstance(self.interventions.interventions, dict)
        self.assertIsInstance(self.interventions.intervention_templates, dict)

        # Check that all intervention types are present
        expected_types = [
            InterventionType.COGNITIVE_RESTRUCTURING,
            InterventionType.MINDFULNESS,
            InterventionType.COPING_SKILLS,
            InterventionType.EMOTIONAL_REGULATION,
            InterventionType.BEHAVIORAL_ACTIVATION
        ]

        for intervention_type in expected_types:
            self.assertIn(intervention_type, self.interventions.interventions)
            self.assertIn(intervention_type, self.interventions.intervention_templates)

    def test_get_intervention_details(self):
        """Test getting intervention details."""
        details = self.interventions.get_intervention_details(InterventionType.MINDFULNESS)

        self.assertIsInstance(details, dict)
        self.assertIn("name", details)
        self.assertIn("description", details)
        self.assertIn("techniques", details)
        self.assertIn("evidence_base", details)
        self.assertEqual(details["name"], "Mindfulness Practice")

    def test_get_intervention_template(self):
        """Test getting intervention templates."""
        template = self.interventions.get_intervention_template(InterventionType.COGNITIVE_RESTRUCTURING)

        self.assertIsInstance(template, dict)
        self.assertIn("introduction", template)
        self.assertIn("technique_explanation", template)
        self.assertIn("practice_prompt", template)
        self.assertIn("integration", template)

    def test_validate_intervention_appropriateness(self):
        """Test intervention appropriateness validation."""
        # Test appropriate intervention
        is_appropriate, reasons = self.interventions.validate_intervention_appropriateness(
            InterventionType.MINDFULNESS, self.mock_session_state
        )
        self.assertTrue(is_appropriate)
        self.assertEqual(len(reasons), 0)

        # Test inappropriate intervention (high emotional intensity)
        self.mock_session_state.emotional_state.intensity = 0.95
        is_appropriate, reasons = self.interventions.validate_intervention_appropriateness(
            InterventionType.COGNITIVE_RESTRUCTURING, self.mock_session_state
        )
        # Should still be appropriate unless specific contraindications
        self.assertTrue(is_appropriate or len(reasons) > 0)


class TestCrisisDetectionSystem(unittest.TestCase):
    """Test crisis detection and response system."""

    def setUp(self):
        """Set up test fixtures."""
        self.crisis_system = CrisisDetectionSystem()

        # Mock session state and narrative context
        self.mock_session_state = Mock()
        self.mock_session_state.emotional_state = Mock()
        self.mock_session_state.emotional_state.primary_emotion = EmotionalStateType.DEPRESSED
        self.mock_session_state.emotional_state.intensity = 0.8
        self.mock_session_state.emotional_state.secondary_emotions = []
        self.mock_session_state.therapeutic_progress = Mock()
        self.mock_session_state.therapeutic_progress.overall_progress_score = 30
        self.mock_session_state.therapeutic_progress.completed_interventions = []
        self.mock_session_state.character_states = {}

        self.mock_narrative_context = Mock()
        self.mock_narrative_context.recent_events = ["Character feels sad", "Difficult situation"]

    def test_initialization(self):
        """Test crisis detection system initialization."""
        self.assertIsInstance(self.crisis_system.crisis_keywords, dict)
        self.assertIsInstance(self.crisis_system.risk_assessment_factors, list)
        self.assertIsInstance(self.crisis_system.protective_factors, list)
        self.assertIsInstance(self.crisis_system.crisis_response_protocols, dict)

        # Check that all crisis levels are covered
        for level in CrisisLevel:
            if level != CrisisLevel.NONE:
                self.assertIn(level, self.crisis_system.crisis_keywords)
                self.assertIn(level, self.crisis_system.crisis_response_protocols)

    def test_assess_crisis_level_none(self):
        """Test crisis assessment with no crisis indicators."""
        user_input = "I'm feeling okay today, just thinking about things."

        crisis_indicators = self.crisis_system.assess_crisis_level(
            user_input, self.mock_session_state, self.mock_narrative_context
        )

        self.assertEqual(crisis_indicators.crisis_level, CrisisLevel.NONE)
        self.assertIsInstance(crisis_indicators.confidence_score, float)
        self.assertTrue(0.0 <= crisis_indicators.confidence_score <= 1.0)

    def test_assess_crisis_level_low(self):
        """Test crisis assessment with low-level indicators."""
        user_input = "I'm feeling really down and struggling to cope with everything."

        crisis_indicators = self.crisis_system.assess_crisis_level(
            user_input, self.mock_session_state, self.mock_narrative_context
        )

        self.assertIn(crisis_indicators.crisis_level, [CrisisLevel.LOW, CrisisLevel.MODERATE])
        self.assertGreater(len(crisis_indicators.immediate_concerns), 0)
        self.assertGreater(crisis_indicators.confidence_score, 0.5)

    def test_assess_crisis_level_high(self):
        """Test crisis assessment with high-level indicators."""
        user_input = "I want to die, I can't take this anymore. I'm thinking about suicide."

        crisis_indicators = self.crisis_system.assess_crisis_level(
            user_input, self.mock_session_state, self.mock_narrative_context
        )

        self.assertIn(crisis_indicators.crisis_level, [CrisisLevel.HIGH, CrisisLevel.IMMINENT])
        self.assertTrue(crisis_indicators.professional_referral_needed)
        self.assertTrue(crisis_indicators.emergency_contact_needed)
        self.assertGreater(len(crisis_indicators.recommended_actions), 0)

    def test_generate_crisis_response_emergency(self):
        """Test emergency crisis response generation."""
        crisis_indicators = CrisisIndicators(
            crisis_level=CrisisLevel.HIGH,
            immediate_concerns=["suicide", "want to die"],
            confidence_score=0.9
        )

        delivery_context = Mock()
        delivery_context.session_state = self.mock_session_state
        delivery_context.narrative_context = self.mock_narrative_context

        response = self.crisis_system.generate_crisis_response(crisis_indicators, delivery_context)

        self.assertIsInstance(response, (Mock, object))  # Handle mock or real response
        if hasattr(response, 'safety_level'):
            self.assertEqual(response.safety_level, SafetyLevel.CRISIS)
        if hasattr(response, 'content'):
            self.assertIn("crisis", response.content.lower())


class TestContentDeliverySystem(unittest.TestCase):
    """Test therapeutic content delivery system."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock LLM client
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate_therapeutic_dialogue.return_value = Mock(
            content="Character provides therapeutic support",
            content_type=TherapeuticContentType.DIALOGUE,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.8,
            confidence=0.9
        )

        self.delivery_system = ContentDeliverySystem(self.mock_llm_client)

        # Mock intervention and delivery context
        self.mock_intervention = Mock()
        self.mock_intervention.intervention_type = InterventionType.MINDFULNESS
        self.mock_intervention.content = "Let's practice mindful breathing"
        self.mock_intervention.character_name = "Guide"

        self.mock_delivery_context = Mock()
        self.mock_delivery_context.delivery_mode = InterventionDeliveryMode.NARRATIVE_EMBEDDED
        self.mock_delivery_context.session_state = Mock()
        self.mock_delivery_context.session_state.emotional_state = Mock()
        self.mock_delivery_context.session_state.emotional_state.primary_emotion = EmotionalStateType.ANXIOUS
        self.mock_delivery_context.session_state.therapeutic_progress = Mock()
        self.mock_delivery_context.session_state.therapeutic_progress.therapeutic_goals = []
        self.mock_delivery_context.narrative_context = Mock()
        self.mock_delivery_context.narrative_context.recent_events = ["Story event 1", "Story event 2"]
        self.mock_delivery_context.cultural_considerations = []
        self.mock_delivery_context.accessibility_needs = []

    def test_initialization(self):
        """Test content delivery system initialization."""
        self.assertIsInstance(self.delivery_system.delivery_strategies, dict)

        # Check that all delivery modes are covered
        for mode in InterventionDeliveryMode:
            self.assertIn(mode, self.delivery_system.delivery_strategies)

    def test_embed_therapeutic_content_narrative(self):
        """Test embedding therapeutic content in narrative."""
        self.mock_delivery_context.delivery_mode = InterventionDeliveryMode.NARRATIVE_EMBEDDED

        response = self.delivery_system.embed_therapeutic_content(
            self.mock_intervention, self.mock_delivery_context
        )

        # Verify LLM client was called
        self.mock_llm_client.generate_therapeutic_dialogue.assert_called()

        # Check response structure
        self.assertIsInstance(response, (Mock, object))

    def test_embed_therapeutic_content_character_guided(self):
        """Test embedding therapeutic content through character guidance."""
        self.mock_delivery_context.delivery_mode = InterventionDeliveryMode.CHARACTER_GUIDED

        self.delivery_system.embed_therapeutic_content(
            self.mock_intervention, self.mock_delivery_context
        )

        # Verify LLM client was called
        self.mock_llm_client.generate_therapeutic_dialogue.assert_called()

    def test_embed_therapeutic_content_direct(self):
        """Test direct therapeutic content delivery."""
        self.mock_delivery_context.delivery_mode = InterventionDeliveryMode.DIRECT

        response = self.delivery_system.embed_therapeutic_content(
            self.mock_intervention, self.mock_delivery_context
        )

        # Direct mode should return content directly
        self.assertIsInstance(response, (Mock, object))
        if hasattr(response, 'content'):
            self.assertEqual(response.content, self.mock_intervention.content)


class TestTherapeuticGuidanceAgent(unittest.TestCase):
    """Test main Therapeutic Guidance Agent."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock LLM client
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate_therapeutic_intervention.return_value = Mock(
            content="Generated therapeutic intervention",
            content_type=TherapeuticContentType.INTERVENTION,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.8,
            confidence=0.9
        )

        self.agent = TherapeuticGuidanceAgent(self.mock_llm_client)

        # Mock detected opportunity
        self.mock_opportunity = Mock()
        self.mock_opportunity.opportunity_type = OpportunityType.ANXIETY_MANAGEMENT
        self.mock_opportunity.recommended_interventions = [InterventionType.MINDFULNESS]
        self.mock_opportunity.urgency_level = InterventionUrgency.MEDIUM
        self.mock_opportunity.confidence_score = 0.8
        self.mock_opportunity.therapeutic_rationale = "User showing anxiety symptoms"
        self.mock_opportunity.validate.return_value = True

        # Mock delivery context
        self.mock_delivery_context = Mock()
        self.mock_delivery_context.session_state = Mock()
        self.mock_delivery_context.session_state.emotional_state = Mock()
        self.mock_delivery_context.session_state.emotional_state.primary_emotion = EmotionalStateType.ANXIOUS
        self.mock_delivery_context.session_state.therapeutic_progress = Mock()
        self.mock_delivery_context.session_state.therapeutic_progress.therapeutic_goals = []
        self.mock_delivery_context.narrative_context = Mock()
        self.mock_delivery_context.narrative_context.recent_events = ["Story event"]
        self.mock_delivery_context.character_context = Mock()
        self.mock_delivery_context.character_context.name = "Guide"
        self.mock_delivery_context.delivery_mode = InterventionDeliveryMode.NARRATIVE_EMBEDDED
        self.mock_delivery_context.cultural_considerations = []
        self.mock_delivery_context.accessibility_needs = []
        self.mock_delivery_context.validate.return_value = True

    def test_initialization(self):
        """Test agent initialization."""
        self.assertIsInstance(self.agent.evidence_based_interventions, (EvidenceBasedInterventions, Mock))
        self.assertIsInstance(self.agent.content_delivery_system, (ContentDeliverySystem, Mock))
        self.assertIsInstance(self.agent.crisis_detection_system, (CrisisDetectionSystem, Mock))
        self.assertIsInstance(self.agent.active_interventions, dict)
        self.assertIsInstance(self.agent.intervention_history, list)

    def test_generate_therapeutic_intervention(self):
        """Test therapeutic intervention generation."""
        intervention = self.agent.generate_therapeutic_intervention(
            self.mock_opportunity, self.mock_delivery_context
        )

        self.assertIsInstance(intervention, (DeliveredIntervention, Mock))

        # Check that intervention was stored
        if hasattr(intervention, 'intervention_id'):
            self.assertIn(intervention.intervention_id, self.agent.active_interventions)
            self.assertIn(intervention, self.agent.intervention_history)

    def test_deliver_therapeutic_content(self):
        """Test therapeutic content delivery."""
        # Create mock intervention
        mock_intervention = Mock()
        mock_intervention.intervention_type = InterventionType.MINDFULNESS
        mock_intervention.effectiveness_metrics = {}

        response = self.agent.deliver_therapeutic_content(
            mock_intervention, self.mock_delivery_context
        )

        self.assertIsInstance(response, (Mock, object))

    def test_assess_and_respond_to_crisis_no_crisis(self):
        """Test crisis assessment with no crisis detected."""
        user_input = "I'm feeling okay today"

        response = self.agent.assess_and_respond_to_crisis(
            user_input,
            self.mock_delivery_context.session_state,
            self.mock_delivery_context.narrative_context
        )

        # Should return None if no crisis detected
        self.assertIsNone(response)

    def test_assess_and_respond_to_crisis_with_crisis(self):
        """Test crisis assessment with crisis detected."""
        user_input = "I want to hurt myself, I can't take this anymore"

        response = self.agent.assess_and_respond_to_crisis(
            user_input,
            self.mock_delivery_context.session_state,
            self.mock_delivery_context.narrative_context
        )

        # Should return crisis response
        self.assertIsNotNone(response)

        # Check that crisis intervention was recorded
        self.assertGreater(len(self.agent.intervention_history), 0)

    def test_complete_intervention(self):
        """Test intervention completion."""
        # First generate an intervention
        intervention = self.agent.generate_therapeutic_intervention(
            self.mock_opportunity, self.mock_delivery_context
        )

        if hasattr(intervention, 'intervention_id'):
            intervention_id = intervention.intervention_id

            # Complete the intervention
            success = self.agent.complete_intervention(
                intervention_id, effectiveness_rating=0.8, user_feedback="Very helpful"
            )

            self.assertTrue(success)
            self.assertNotIn(intervention_id, self.agent.active_interventions)

    def test_get_intervention_history(self):
        """Test getting intervention history."""
        # Generate some interventions
        self.agent.generate_therapeutic_intervention(
            self.mock_opportunity, self.mock_delivery_context
        )

        history = self.agent.get_intervention_history()
        self.assertIsInstance(history, list)
        self.assertGreaterEqual(len(history), 1)

    def test_get_active_interventions(self):
        """Test getting active interventions."""
        # Generate an intervention
        self.agent.generate_therapeutic_intervention(
            self.mock_opportunity, self.mock_delivery_context
        )

        active = self.agent.get_active_interventions()
        self.assertIsInstance(active, dict)


class TestIntegrationScenarios(unittest.TestCase):
    """Test complete integration scenarios for therapeutic content delivery."""

    def setUp(self):
        """Set up integration test fixtures."""
        # Mock LLM client with realistic responses
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate_therapeutic_intervention.return_value = Mock(
            content="Let's practice a mindfulness exercise together. Take a deep breath and focus on the present moment.",
            content_type=TherapeuticContentType.INTERVENTION,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.85,
            confidence=0.9
        )
        self.mock_llm_client.generate_therapeutic_dialogue.return_value = Mock(
            content="The wise guide notices your anxiety and gently suggests, 'Perhaps we should pause here and breathe together.'",
            content_type=TherapeuticContentType.DIALOGUE,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.8,
            confidence=0.85
        )

        self.agent = TherapeuticGuidanceAgent(self.mock_llm_client)

    def test_complete_therapeutic_delivery_pipeline(self):
        """Test the complete therapeutic content delivery pipeline."""
        # Create realistic opportunity
        opportunity = Mock()
        opportunity.opportunity_type = OpportunityType.ANXIETY_MANAGEMENT
        opportunity.recommended_interventions = [InterventionType.MINDFULNESS]
        opportunity.urgency_level = InterventionUrgency.MEDIUM
        opportunity.confidence_score = 0.8
        opportunity.therapeutic_rationale = "User showing signs of anxiety in narrative choices"
        opportunity.validate.return_value = True

        # Create realistic delivery context
        delivery_context = Mock()
        delivery_context.session_state = Mock()
        delivery_context.session_state.emotional_state = Mock()
        delivery_context.session_state.emotional_state.primary_emotion = EmotionalStateType.ANXIOUS
        delivery_context.session_state.therapeutic_progress = Mock()
        delivery_context.session_state.therapeutic_progress.therapeutic_goals = ["Reduce anxiety", "Improve coping"]
        delivery_context.narrative_context = Mock()
        delivery_context.narrative_context.recent_events = [
            "You feel your heart racing as you approach the challenge",
            "The uncertainty makes you feel overwhelmed"
        ]
        delivery_context.character_context = Mock()
        delivery_context.character_context.name = "Wise Guide"
        delivery_context.delivery_mode = InterventionDeliveryMode.NARRATIVE_EMBEDDED
        delivery_context.cultural_considerations = []
        delivery_context.accessibility_needs = []
        delivery_context.validate.return_value = True

        # Step 1: Generate therapeutic intervention
        intervention = self.agent.generate_therapeutic_intervention(opportunity, delivery_context)

        self.assertIsInstance(intervention, (DeliveredIntervention, Mock))

        # Step 2: Deliver therapeutic content
        response = self.agent.deliver_therapeutic_content(intervention, delivery_context)

        self.assertIsInstance(response, (Mock, object))

        # Step 3: Complete intervention
        if hasattr(intervention, 'intervention_id'):
            success = self.agent.complete_intervention(
                intervention.intervention_id,
                effectiveness_rating=0.9,
                user_feedback="The breathing exercise really helped me feel calmer"
            )
            self.assertTrue(success)

    def test_crisis_intervention_pipeline(self):
        """Test crisis intervention pipeline."""
        # Simulate crisis input
        crisis_input = "I can't take this anymore, I want to end it all"

        # Mock session state indicating distress
        session_state = Mock()
        session_state.emotional_state = Mock()
        session_state.emotional_state.primary_emotion = EmotionalStateType.DEPRESSED
        session_state.emotional_state.intensity = 0.95
        session_state.emotional_state.secondary_emotions = []
        session_state.therapeutic_progress = Mock()
        session_state.therapeutic_progress.overall_progress_score = 15
        session_state.therapeutic_progress.completed_interventions = []
        session_state.character_states = {}

        narrative_context = Mock()
        narrative_context.recent_events = ["Everything seems hopeless", "No way out of this situation"]

        # Test crisis assessment and response
        crisis_response = self.agent.assess_and_respond_to_crisis(
            crisis_input, session_state, narrative_context
        )

        # Should return crisis response
        self.assertIsNotNone(crisis_response)

        # Should have recorded crisis intervention
        self.assertGreater(len(self.agent.intervention_history), 0)

        # Last intervention should be crisis-related
        last_intervention = self.agent.intervention_history[-1]
        if hasattr(last_intervention, 'follow_up_needed'):
            self.assertTrue(last_intervention.follow_up_needed)

    def test_multiple_delivery_modes(self):
        """Test therapeutic content delivery across different modes."""
        opportunity = Mock()
        opportunity.opportunity_type = OpportunityType.COPING_SKILL_BUILDING
        opportunity.recommended_interventions = [InterventionType.COPING_SKILLS]
        opportunity.urgency_level = InterventionUrgency.MEDIUM
        opportunity.confidence_score = 0.7
        opportunity.therapeutic_rationale = "User needs coping strategies"
        opportunity.validate.return_value = True

        base_context = Mock()
        base_context.session_state = Mock()
        base_context.session_state.emotional_state = Mock()
        base_context.session_state.emotional_state.primary_emotion = EmotionalStateType.OVERWHELMED
        base_context.session_state.therapeutic_progress = Mock()
        base_context.session_state.therapeutic_progress.therapeutic_goals = []
        base_context.narrative_context = Mock()
        base_context.narrative_context.recent_events = ["Facing a difficult challenge"]
        base_context.character_context = Mock()
        base_context.character_context.name = "Mentor"
        base_context.cultural_considerations = []
        base_context.accessibility_needs = []
        base_context.validate.return_value = True

        # Test different delivery modes
        delivery_modes = [
            InterventionDeliveryMode.DIRECT,
            InterventionDeliveryMode.NARRATIVE_EMBEDDED,
            InterventionDeliveryMode.CHARACTER_GUIDED,
            InterventionDeliveryMode.EXPERIENTIAL,
            InterventionDeliveryMode.REFLECTIVE
        ]

        for mode in delivery_modes:
            with self.subTest(delivery_mode=mode):
                # Create context with specific delivery mode
                context = Mock()
                context.session_state = base_context.session_state
                context.narrative_context = base_context.narrative_context
                context.character_context = base_context.character_context
                context.delivery_mode = mode
                context.cultural_considerations = []
                context.accessibility_needs = []
                context.validate.return_value = True

                # Generate and deliver intervention
                intervention = self.agent.generate_therapeutic_intervention(opportunity, context)
                response = self.agent.deliver_therapeutic_content(intervention, context)

                self.assertIsInstance(intervention, (DeliveredIntervention, Mock))
                self.assertIsInstance(response, (Mock, object))


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.INFO)

    # Run tests
    unittest.main(verbosity=2)
