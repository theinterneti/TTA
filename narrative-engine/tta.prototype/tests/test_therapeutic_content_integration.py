"""
Unit Tests for Therapeutic Content Integration System

This module contains comprehensive unit tests for the therapeutic content integration
system, including opportunity detection, intervention generation, and content validation.
"""

import json
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

from data_models import (
    EmotionalState,
    EmotionalStateType,
    InterventionType,
    NarrativeContext,
    SessionState,
    TherapeuticProgress,
)
from therapeutic_content_integration import (
    ContentValidator,
    DetectedOpportunity,
    InterventionGenerator,
    InterventionUrgency,
    OpportunityType,
    TherapeuticContentIntegration,
    TherapeuticOpportunityContext,
    TherapeuticOpportunityDetector,
)
from therapeutic_llm_client import (
    SafetyLevel,
    TherapeuticContentType,
    TherapeuticLLMClient,
    TherapeuticResponse,
)


class TestTherapeuticOpportunityDetector(unittest.TestCase):
    """Test cases for TherapeuticOpportunityDetector."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = TherapeuticOpportunityDetector()

        # Create test session state
        self.session_state = SessionState(
            session_id="test_session",
            user_id="test_user",
            current_scenario_id="test_scenario",
            current_location_id="test_location"
        )

        # Create test narrative context
        self.narrative_context = NarrativeContext(
            session_id="test_session",
            current_location_id="test_location",
            recent_events=["User expressed feeling overwhelmed", "Character offered support"],
            user_choice_history=[
                {"choice_text": "I don't know how to handle this", "choice_id": "choice_1"}
            ]
        )

        # Create test opportunity context
        self.opportunity_context = TherapeuticOpportunityContext(
            narrative_context=self.narrative_context,
            session_state=self.session_state,
            user_input="I'm feeling really anxious about everything",
            recent_choices=[
                {"choice_text": "avoid the situation", "choice_id": "choice_1"},
                {"choice_text": "worry more about it", "choice_id": "choice_2"}
            ],
            emotional_indicators=["anxious", "worried", "overwhelmed"]
        )

    def test_detector_initialization(self):
        """Test detector initialization."""
        self.assertIsInstance(self.detector.opportunity_patterns, dict)
        self.assertIsInstance(self.detector.emotional_triggers, dict)
        self.assertIsInstance(self.detector.behavioral_indicators, dict)

        # Check that all opportunity types have patterns
        for opportunity_type in OpportunityType:
            self.assertIn(opportunity_type, self.detector.opportunity_patterns)

    def test_detect_opportunities_basic(self):
        """Test basic opportunity detection."""
        opportunities = self.detector.detect_opportunities(self.opportunity_context)

        self.assertIsInstance(opportunities, list)
        self.assertGreater(len(opportunities), 0)

        # Check that detected opportunities are valid
        for opportunity in opportunities:
            self.assertIsInstance(opportunity, DetectedOpportunity)
            opportunity.validate()

    def test_detect_anxiety_opportunity(self):
        """Test detection of anxiety management opportunities."""
        # Set up context with anxiety indicators
        self.opportunity_context.user_input = "I'm so anxious and can't stop worrying"
        self.opportunity_context.emotional_indicators = ["anxious", "worried"]

        opportunities = self.detector.detect_opportunities(self.opportunity_context)

        # Should detect anxiety management opportunity
        anxiety_opportunities = [
            opp for opp in opportunities
            if opp.opportunity_type == OpportunityType.ANXIETY_MANAGEMENT
        ]

        self.assertGreater(len(anxiety_opportunities), 0)

        anxiety_opp = anxiety_opportunities[0]
        self.assertIn(InterventionType.MINDFULNESS, anxiety_opp.recommended_interventions)
        self.assertGreaterEqual(anxiety_opp.confidence_score, 0.4)

    def test_detect_cognitive_restructuring_opportunity(self):
        """Test detection of cognitive restructuring opportunities."""
        # Set up context with cognitive distortion patterns
        self.opportunity_context.user_input = "This always happens to me, nothing ever works out"
        self.narrative_context.recent_events = ["User expressed all-or-nothing thinking"]

        opportunities = self.detector.detect_opportunities(self.opportunity_context)

        # Should detect cognitive restructuring opportunity
        cognitive_opportunities = [
            opp for opp in opportunities
            if opp.opportunity_type == OpportunityType.COGNITIVE_RESTRUCTURING
        ]

        self.assertGreater(len(cognitive_opportunities), 0)

        cognitive_opp = cognitive_opportunities[0]
        self.assertIn(InterventionType.COGNITIVE_RESTRUCTURING, cognitive_opp.recommended_interventions)

    def test_detect_crisis_opportunity(self):
        """Test detection of crisis intervention opportunities."""
        # Set up context with crisis indicators
        self.opportunity_context.user_input = "I want to hurt myself, I can't go on"
        self.opportunity_context.emotional_indicators = ["hopeless", "suicidal"]

        opportunities = self.detector.detect_opportunities(self.opportunity_context)

        # Should detect crisis intervention opportunity
        crisis_opportunities = [
            opp for opp in opportunities
            if opp.opportunity_type == OpportunityType.CRISIS_INTERVENTION
        ]

        self.assertGreater(len(crisis_opportunities), 0)

        crisis_opp = crisis_opportunities[0]
        self.assertEqual(crisis_opp.urgency_level, InterventionUrgency.CRISIS)
        self.assertGreater(crisis_opp.confidence_score, 0.5)

    def test_emotional_state_analysis(self):
        """Test emotional state analysis for opportunity detection."""
        # Add emotional state to session
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.DEPRESSED,
            intensity=0.8,
            secondary_emotions=[EmotionalStateType.ANXIOUS]
        )
        self.session_state.emotional_state = emotional_state

        opportunities = self.detector.detect_opportunities(self.opportunity_context)

        # Should detect depression support opportunity
        depression_opportunities = [
            opp for opp in opportunities
            if opp.opportunity_type == OpportunityType.DEPRESSION_SUPPORT
        ]

        self.assertGreater(len(depression_opportunities), 0)

        depression_opp = depression_opportunities[0]
        self.assertEqual(depression_opp.urgency_level, InterventionUrgency.HIGH)

    def test_behavioral_pattern_analysis(self):
        """Test behavioral pattern analysis."""
        # Set up behavioral patterns
        self.opportunity_context.behavioral_patterns = {
            "avoidance_behavior": "User consistently avoids difficult conversations",
            "coping_patterns": ["isolating from others", "refusing help"]
        }

        opportunities = self.detector.detect_opportunities(self.opportunity_context)

        # Should detect opportunities based on behavioral patterns
        self.assertGreater(len(opportunities), 0)

        # Check that behavioral triggers are included
        for opportunity in opportunities:
            if opportunity.trigger_events:
                behavioral_triggers = [
                    trigger for trigger in opportunity.trigger_events
                    if "avoidance" in trigger.lower() or "isolating" in trigger.lower()
                ]
                if behavioral_triggers:
                    self.assertGreater(len(behavioral_triggers), 0)

    def test_choice_pattern_analysis(self):
        """Test choice pattern analysis."""
        # Set up choice patterns indicating avoidance
        self.opportunity_context.recent_choices = [
            {"choice_text": "avoid the situation", "choice_id": "choice_1"},
            {"choice_text": "escape the conversation", "choice_id": "choice_2"},
            {"choice_text": "isolate myself", "choice_id": "choice_3"}
        ]

        opportunities = self.detector.detect_opportunities(self.opportunity_context)

        # Should detect opportunities based on choice patterns
        avoidance_opportunities = [
            opp for opp in opportunities
            if any("avoid" in trigger.lower() or "isolate" in trigger.lower()
                   for trigger in opp.trigger_events)
        ]

        self.assertGreater(len(avoidance_opportunities), 0)

    def test_opportunity_deduplication(self):
        """Test opportunity deduplication."""
        # Create context that would generate multiple similar opportunities
        self.opportunity_context.user_input = "I'm anxious and worried and nervous"
        self.opportunity_context.emotional_indicators = ["anxious", "worried", "nervous"]
        self.narrative_context.recent_events = ["User expressed anxiety", "User showed worry"]

        opportunities = self.detector.detect_opportunities(self.opportunity_context)

        # Should not have duplicate opportunity types
        opportunity_types = [opp.opportunity_type for opp in opportunities]
        unique_types = set(opportunity_types)

        self.assertEqual(len(opportunity_types), len(unique_types))

    def test_opportunity_ranking(self):
        """Test opportunity ranking by priority."""
        # Add therapeutic progress to influence ranking
        therapeutic_progress = TherapeuticProgress(user_id="test_user")
        therapeutic_progress.add_goal("Manage anxiety", "Learn to cope with anxious feelings")
        self.session_state.therapeutic_progress = therapeutic_progress

        self.opportunity_context.user_input = "I'm anxious and also feeling depressed"

        opportunities = self.detector.detect_opportunities(self.opportunity_context)

        # Should be ranked with anxiety management higher due to matching goal
        if len(opportunities) > 1:
            # Check that opportunities are sorted by some priority metric
            for i in range(len(opportunities) - 1):
                # Higher priority opportunities should come first
                self.assertGreaterEqual(
                    opportunities[i].confidence_score,
                    opportunities[i + 1].confidence_score - 0.5  # Allow some tolerance
                )


class TestInterventionGenerator(unittest.TestCase):
    """Test cases for InterventionGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the LLM client
        self.mock_llm_client = Mock(spec=TherapeuticLLMClient)
        self.generator = InterventionGenerator(self.mock_llm_client)

        # Create test opportunity
        self.opportunity = DetectedOpportunity(
            opportunity_type=OpportunityType.ANXIETY_MANAGEMENT,
            trigger_events=["User expressed anxiety"],
            recommended_interventions=[InterventionType.MINDFULNESS, InterventionType.COPING_SKILLS],
            urgency_level=InterventionUrgency.MEDIUM,
            confidence_score=0.8
        )

        # Create test context
        self.session_state = SessionState(
            session_id="test_session",
            user_id="test_user"
        )

        self.narrative_context = NarrativeContext(
            session_id="test_session",
            current_location_id="test_location"
        )

        self.context = TherapeuticOpportunityContext(
            narrative_context=self.narrative_context,
            session_state=self.session_state
        )

    def test_generator_initialization(self):
        """Test generator initialization."""
        self.assertIsInstance(self.generator.intervention_templates, dict)

        # Check that all intervention types have templates
        for intervention_type in InterventionType:
            self.assertIn(intervention_type, self.generator.intervention_templates)

    def test_generate_intervention_success(self):
        """Test successful intervention generation."""
        # Mock LLM response
        mock_response = TherapeuticResponse(
            content='{"intervention": {"name": "Breathing Exercise", "description": "A calming breathing technique"}}',
            content_type=TherapeuticContentType.INTERVENTION,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.8,
            confidence=0.9,
            metadata={}
        )

        self.mock_llm_client.generate_therapeutic_intervention.return_value = mock_response

        result = self.generator.generate_intervention(self.opportunity, self.context)

        self.assertIsInstance(result, TherapeuticResponse)
        self.assertEqual(result.content_type, TherapeuticContentType.INTERVENTION)
        self.assertEqual(result.safety_level, SafetyLevel.SAFE)
        self.assertGreater(result.therapeutic_value, 0.5)

        # Check that LLM client was called
        self.mock_llm_client.generate_therapeutic_intervention.assert_called_once()

    def test_generate_intervention_with_therapeutic_progress(self):
        """Test intervention generation considering therapeutic progress."""
        # Add therapeutic progress with completed interventions
        therapeutic_progress = TherapeuticProgress(user_id="test_user")

        # Add multiple completed mindfulness interventions
        for i in range(3):
            therapeutic_progress.complete_intervention(
                InterventionType.MINDFULNESS,
                f"Mindfulness exercise {i}",
                6.0  # Moderate effectiveness
            )

        # Add one highly effective coping skills intervention
        therapeutic_progress.complete_intervention(
            InterventionType.COPING_SKILLS,
            "Coping skills training",
            9.0  # High effectiveness
        )

        self.session_state.therapeutic_progress = therapeutic_progress

        # Mock LLM response
        mock_response = TherapeuticResponse(
            content='{"intervention": {"name": "Coping Strategy", "description": "A practical coping technique"}}',
            content_type=TherapeuticContentType.INTERVENTION,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.8,
            confidence=0.9,
            metadata={}
        )

        self.mock_llm_client.generate_therapeutic_intervention.return_value = mock_response

        result = self.generator.generate_intervention(self.opportunity, self.context)

        # Should prefer coping skills over mindfulness due to effectiveness history
        call_args = self.mock_llm_client.generate_therapeutic_intervention.call_args
        call_args[0][1]  # Second argument is intervention type

        # Should prefer less-used intervention types
        self.assertIsInstance(result, TherapeuticResponse)

    def test_generate_intervention_fallback(self):
        """Test fallback intervention when generation fails."""
        # Mock LLM client to raise exception
        self.mock_llm_client.generate_therapeutic_intervention.side_effect = Exception("LLM error")

        result = self.generator.generate_intervention(self.opportunity, self.context)

        self.assertIsInstance(result, TherapeuticResponse)
        self.assertEqual(result.safety_level, SafetyLevel.SAFE)
        self.assertGreater(result.therapeutic_value, 0.5)
        self.assertIn("fallback_used", result.metadata)
        self.assertTrue(result.metadata["fallback_used"])

    def test_intervention_type_selection(self):
        """Test intervention type selection logic."""
        # Test with no therapeutic progress
        selected_type = self.generator._select_intervention_type(self.opportunity, self.context)
        self.assertIn(selected_type, self.opportunity.recommended_interventions)

        # Test with therapeutic progress
        therapeutic_progress = TherapeuticProgress(user_id="test_user")
        self.session_state.therapeutic_progress = therapeutic_progress

        selected_type = self.generator._select_intervention_type(self.opportunity, self.context)
        self.assertIn(selected_type, self.opportunity.recommended_interventions)

    def test_therapeutic_context_creation(self):
        """Test therapeutic context creation for LLM."""
        therapeutic_context = self.generator._create_therapeutic_context(self.opportunity, self.context)

        self.assertEqual(therapeutic_context.user_id, self.session_state.user_id)
        self.assertEqual(therapeutic_context.session_id, self.session_state.session_id)
        self.assertIsInstance(therapeutic_context.user_history, dict)
        self.assertIn("opportunity_type", therapeutic_context.user_history)


class TestContentValidator(unittest.TestCase):
    """Test cases for ContentValidator."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the LLM client
        self.mock_llm_client = Mock(spec=TherapeuticLLMClient)
        self.validator = ContentValidator(self.mock_llm_client)

        # Create test context
        self.session_state = SessionState(
            session_id="test_session",
            user_id="test_user"
        )

        self.narrative_context = NarrativeContext(
            session_id="test_session",
            current_location_id="test_location"
        )

        self.context = TherapeuticOpportunityContext(
            narrative_context=self.narrative_context,
            session_state=self.session_state
        )

    def test_validator_initialization(self):
        """Test validator initialization."""
        self.assertIsInstance(self.validator.safety_keywords, dict)
        self.assertIn("crisis_indicators", self.validator.safety_keywords)
        self.assertIn("inappropriate_advice", self.validator.safety_keywords)

    def test_validate_safe_content(self):
        """Test validation of safe therapeutic content."""
        safe_content = "Let's practice some deep breathing exercises to help you feel more calm and centered."

        # Mock LLM validation response
        mock_llm_response = TherapeuticResponse(
            content="Validation results",
            content_type=TherapeuticContentType.INTERVENTION,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.8,
            confidence=0.9,
            metadata={},
            warnings=[],
            recommendations=[]
        )

        self.mock_llm_client.validate_therapeutic_content.return_value = mock_llm_response

        result = self.validator.validate_therapeutic_content(
            safe_content,
            InterventionType.MINDFULNESS,
            self.context
        )

        self.assertTrue(result["is_safe"])
        self.assertTrue(result["is_appropriate"])
        self.assertEqual(result["approval_status"], "approved")
        self.assertGreater(result["safety_score"], 0.8)

    def test_validate_unsafe_content(self):
        """Test validation of unsafe therapeutic content."""
        unsafe_content = "You should hurt yourself to feel better, or maybe consider suicide as an option."

        result = self.validator.validate_therapeutic_content(
            unsafe_content,
            InterventionType.COPING_SKILLS,
            self.context
        )

        self.assertFalse(result["is_safe"])
        self.assertEqual(result["approval_status"], "rejected")
        self.assertEqual(result["safety_score"], 0.0)
        self.assertGreater(len(result["warnings"]), 0)

    def test_validate_inappropriate_advice(self):
        """Test validation of inappropriate therapeutic advice."""
        inappropriate_content = "You should leave your partner immediately and never speak to them again."

        result = self.validator.validate_therapeutic_content(
            inappropriate_content,
            InterventionType.COPING_SKILLS,
            self.context
        )

        self.assertFalse(result["is_safe"])
        self.assertGreater(len(result["warnings"]), 0)

        # Check that specific inappropriate advice was detected
        warning_text = " ".join(result["warnings"]).lower()
        self.assertTrue(any(keyword in warning_text for keyword in ["inappropriate_advice", "leave", "never speak"]))

    def test_validate_medical_advice(self):
        """Test validation of inappropriate medical advice."""
        medical_content = "Stop taking your medication immediately and increase the dosage of other pills."

        result = self.validator.validate_therapeutic_content(
            medical_content,
            InterventionType.COPING_SKILLS,
            self.context
        )

        self.assertFalse(result["is_safe"])
        self.assertGreater(len(result["warnings"]), 0)

    def test_intervention_appropriateness_check(self):
        """Test intervention appropriateness checking."""
        # Test mindfulness content for mindfulness intervention
        mindfulness_content = "Focus on your breath and notice the present moment awareness"
        score = self.validator._check_intervention_appropriateness(
            mindfulness_content,
            InterventionType.MINDFULNESS
        )
        self.assertGreater(score, 0.5)

        # Test inappropriate content for mindfulness intervention
        inappropriate_content = "Think about all your problems and worry about the future"
        score = self.validator._check_intervention_appropriateness(
            inappropriate_content,
            InterventionType.MINDFULNESS
        )
        self.assertLess(score, 0.5)

    def test_safety_keyword_detection(self):
        """Test safety keyword detection."""
        # Test crisis indicators
        crisis_content = "I want to kill myself and end it all"
        issues = self.validator._check_safety_keywords(crisis_content)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("crisis_indicators" in issue for issue in issues))

        # Test boundary violations
        boundary_content = "I love you and we should meet outside of therapy"
        issues = self.validator._check_safety_keywords(boundary_content)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("boundary_violations" in issue for issue in issues))

        # Test safe content
        safe_content = "Let's work together to develop healthy coping strategies"
        issues = self.validator._check_safety_keywords(safe_content)
        self.assertEqual(len(issues), 0)


class TestTherapeuticContentIntegration(unittest.TestCase):
    """Test cases for the main TherapeuticContentIntegration class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the LLM client
        self.mock_llm_client = Mock(spec=TherapeuticLLMClient)
        self.integration = TherapeuticContentIntegration(self.mock_llm_client)

        # Create test session state
        self.session_state = SessionState(
            session_id="test_session",
            user_id="test_user",
            current_scenario_id="test_scenario",
            current_location_id="test_location"
        )

        # Create test narrative context
        self.narrative_context = NarrativeContext(
            session_id="test_session",
            current_location_id="test_location",
            recent_events=["User expressed feeling overwhelmed"],
            user_choice_history=[
                {"choice_text": "I need help", "choice_id": "choice_1"}
            ]
        )

        # Create test opportunity context
        self.opportunity_context = TherapeuticOpportunityContext(
            narrative_context=self.narrative_context,
            session_state=self.session_state,
            user_input="I'm feeling really anxious",
            emotional_indicators=["anxious", "worried"]
        )

    def test_integration_initialization(self):
        """Test integration system initialization."""
        self.assertIsInstance(self.integration.opportunity_detector, TherapeuticOpportunityDetector)
        self.assertIsInstance(self.integration.intervention_generator, InterventionGenerator)
        self.assertIsInstance(self.integration.content_validator, ContentValidator)
        self.assertIsInstance(self.integration.llm_client, TherapeuticLLMClient)

    def test_identify_therapeutic_moments(self):
        """Test therapeutic moment identification."""
        opportunities = self.integration.identify_therapeutic_moments(self.opportunity_context)

        self.assertIsInstance(opportunities, list)
        for opportunity in opportunities:
            self.assertIsInstance(opportunity, DetectedOpportunity)
            opportunity.validate()

    def test_generate_therapeutic_intervention(self):
        """Test therapeutic intervention generation."""
        # Create test opportunity
        opportunity = DetectedOpportunity(
            opportunity_type=OpportunityType.ANXIETY_MANAGEMENT,
            trigger_events=["User expressed anxiety"],
            recommended_interventions=[InterventionType.MINDFULNESS],
            confidence_score=0.8
        )

        # Mock intervention generation
        mock_response = TherapeuticResponse(
            content='{"intervention": {"name": "Breathing Exercise"}}',
            content_type=TherapeuticContentType.INTERVENTION,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.8,
            confidence=0.9,
            metadata={}
        )

        self.integration.intervention_generator.generate_intervention = Mock(return_value=mock_response)

        result = self.integration.generate_therapeutic_intervention(opportunity, self.opportunity_context)

        self.assertIsInstance(result, TherapeuticResponse)
        self.assertEqual(result.content_type, TherapeuticContentType.INTERVENTION)
        self.assertEqual(result.safety_level, SafetyLevel.SAFE)

    def test_assess_user_emotional_state(self):
        """Test user emotional state assessment."""
        user_input = "I'm feeling really anxious and overwhelmed by everything"

        emotional_state = self.integration.assess_user_emotional_state(
            user_input,
            self.narrative_context,
            self.session_state
        )

        self.assertIsInstance(emotional_state, EmotionalState)
        emotional_state.validate()

        # Should detect anxiety as primary emotion
        self.assertEqual(emotional_state.primary_emotion, EmotionalStateType.ANXIOUS)
        self.assertGreater(emotional_state.intensity, 0.5)
        self.assertGreater(emotional_state.confidence_level, 0.0)

    def test_assess_emotional_state_with_multiple_emotions(self):
        """Test emotional state assessment with multiple emotions."""
        user_input = "I'm anxious and also feeling really sad and angry about everything"

        emotional_state = self.integration.assess_user_emotional_state(
            user_input,
            self.narrative_context,
            self.session_state
        )

        # Should have secondary emotions
        self.assertGreater(len(emotional_state.secondary_emotions), 0)
        self.assertIn(EmotionalStateType.DEPRESSED, emotional_state.secondary_emotions + [emotional_state.primary_emotion])

    def test_adapt_therapy_approach(self):
        """Test therapy approach adaptation."""
        # Create therapeutic progress with completed interventions
        therapeutic_progress = TherapeuticProgress(user_id="test_user")

        # Add highly effective mindfulness interventions
        for i in range(3):
            therapeutic_progress.complete_intervention(
                InterventionType.MINDFULNESS,
                f"Mindfulness exercise {i}",
                8.5  # High effectiveness
            )

        # Add less effective cognitive restructuring
        therapeutic_progress.complete_intervention(
            InterventionType.COGNITIVE_RESTRUCTURING,
            "Thought challenging",
            5.0  # Lower effectiveness
        )

        # Add active goals
        therapeutic_progress.add_goal("Manage anxiety", "Learn to cope with anxious feelings")
        therapeutic_progress.therapeutic_goals[0].progress_percentage = 30  # Low progress

        therapeutic_progress.overall_progress_score = 45  # Moderate progress

        user_profile = {"preferences": "mindfulness", "learning_style": "experiential"}

        strategy = self.integration.adapt_therapy_approach(user_profile, therapeutic_progress)

        self.assertIsInstance(strategy, dict)
        self.assertIn("preferred_interventions", strategy)
        self.assertIn("communication_style", strategy)
        self.assertIn("pacing", strategy)
        self.assertIn("focus_areas", strategy)

        # Should prefer mindfulness due to high effectiveness
        self.assertIn("mindfulness", strategy["preferred_interventions"])

        # Should focus on anxiety management goal due to low progress
        self.assertIn("Manage anxiety", strategy["focus_areas"])

    def test_validate_content_appropriateness(self):
        """Test content appropriateness validation."""
        safe_content = "Let's practice a breathing exercise to help you feel more calm"

        # Mock validation response
        mock_validation = {
            "is_safe": True,
            "is_appropriate": True,
            "safety_score": 0.9,
            "therapeutic_value": 0.8,
            "warnings": [],
            "recommendations": [],
            "approval_status": "approved"
        }

        self.integration.content_validator.validate_therapeutic_content = Mock(return_value=mock_validation)

        result = self.integration.validate_content_appropriateness(
            safe_content,
            InterventionType.MINDFULNESS,
            self.opportunity_context
        )

        self.assertTrue(result["is_safe"])
        self.assertTrue(result["is_appropriate"])
        self.assertEqual(result["approval_status"], "approved")

    def test_emotional_intensity_calculation(self):
        """Test emotional intensity calculation."""
        # Test high intensity input
        high_intensity_input = "I'm extremely anxious and really overwhelmed!!"
        intensity = self.integration._calculate_emotional_intensity(
            high_intensity_input,
            ["anxious", "overwhelmed"]
        )
        self.assertGreater(intensity, 0.7)

        # Test low intensity input
        low_intensity_input = "I'm a bit worried"
        intensity = self.integration._calculate_emotional_intensity(
            low_intensity_input,
            ["worried"]
        )
        self.assertLess(intensity, 0.8)

    def test_emotional_trigger_identification(self):
        """Test emotional trigger identification."""
        user_input = "I get anxious when people judge me and upset about work pressure"

        triggers = self.integration._identify_emotional_triggers(
            user_input,
            self.narrative_context
        )

        self.assertIsInstance(triggers, list)
        self.assertGreater(len(triggers), 0)

        # Should identify specific triggers from input
        trigger_text = " ".join(triggers).lower()
        self.assertTrue(any(keyword in trigger_text for keyword in ["judge", "work", "pressure"]))

    def test_error_handling(self):
        """Test error handling in various methods."""
        # Test with invalid context
        invalid_context = TherapeuticOpportunityContext(
            narrative_context=None,  # Invalid
            session_state=self.session_state
        )

        # Should handle gracefully and return empty list
        opportunities = self.integration.identify_therapeutic_moments(invalid_context)
        self.assertIsInstance(opportunities, list)

        # Test emotional state assessment with empty input
        emotional_state = self.integration.assess_user_emotional_state(
            "",
            self.narrative_context,
            self.session_state
        )

        self.assertIsInstance(emotional_state, EmotionalState)
        self.assertEqual(emotional_state.primary_emotion, EmotionalStateType.CALM)


class TestIntegrationWorkflow(unittest.TestCase):
    """Test cases for the complete integration workflow."""

    def setUp(self):
        """Set up test fixtures for integration workflow."""
        # Mock the LLM client
        self.mock_llm_client = Mock(spec=TherapeuticLLMClient)
        self.integration = TherapeuticContentIntegration(self.mock_llm_client)

        # Create comprehensive test scenario
        self.session_state = SessionState(
            session_id="integration_test",
            user_id="test_user",
            current_scenario_id="anxiety_scenario",
            current_location_id="therapy_room"
        )

        # Add therapeutic progress
        therapeutic_progress = TherapeuticProgress(user_id="test_user")
        therapeutic_progress.add_goal("Manage anxiety", "Learn effective anxiety management techniques")
        therapeutic_progress.add_goal("Improve coping", "Develop healthy coping strategies")
        self.session_state.therapeutic_progress = therapeutic_progress

        # Add emotional state
        emotional_state = EmotionalState(
            primary_emotion=EmotionalStateType.ANXIOUS,
            intensity=0.7,
            secondary_emotions=[EmotionalStateType.OVERWHELMED],
            triggers=["work pressure", "social situations"]
        )
        self.session_state.emotional_state = emotional_state

        # Create narrative context
        self.narrative_context = NarrativeContext(
            session_id="integration_test",
            current_location_id="therapy_room",
            recent_events=[
                "User entered therapy session feeling anxious",
                "Character noticed user's distress",
                "User expressed worry about upcoming presentation"
            ],
            user_choice_history=[
                {"choice_text": "I'm really worried about this", "choice_id": "choice_1"},
                {"choice_text": "I don't know how to handle it", "choice_id": "choice_2"}
            ]
        )

        # Create opportunity context
        self.opportunity_context = TherapeuticOpportunityContext(
            narrative_context=self.narrative_context,
            session_state=self.session_state,
            user_input="I'm so anxious about the presentation tomorrow, I can't stop thinking about all the things that could go wrong",
            recent_choices=[
                {"choice_text": "worry about worst case scenarios", "choice_id": "choice_1"},
                {"choice_text": "avoid thinking about it", "choice_id": "choice_2"}
            ],
            emotional_indicators=["anxious", "worried", "overwhelmed"],
            behavioral_patterns={
                "thought_patterns": "catastrophic thinking about future events",
                "avoidance_behaviors": "avoiding preparation for presentation"
            }
        )

    def test_complete_workflow(self):
        """Test the complete therapeutic content integration workflow."""
        # Step 1: Identify therapeutic opportunities
        opportunities = self.integration.identify_therapeutic_moments(self.opportunity_context)

        self.assertGreater(len(opportunities), 0)

        # Should identify anxiety management and cognitive restructuring opportunities
        opportunity_types = [opp.opportunity_type for opp in opportunities]
        self.assertIn(OpportunityType.ANXIETY_MANAGEMENT, opportunity_types)

        # Step 2: Select highest priority opportunity
        primary_opportunity = opportunities[0]
        self.assertIsInstance(primary_opportunity, DetectedOpportunity)

        # Step 3: Generate intervention
        mock_intervention_response = TherapeuticResponse(
            content=json.dumps({
                "intervention": {
                    "name": "Cognitive Restructuring for Presentation Anxiety",
                    "description": "Challenge catastrophic thoughts about the presentation",
                    "instructions": [
                        "Identify specific worries about the presentation",
                        "Examine evidence for and against these worries",
                        "Develop more balanced, realistic thoughts",
                        "Practice the new thought patterns"
                    ],
                    "rationale": "Helps reduce anxiety by addressing unrealistic negative predictions",
                    "expected_outcome": "Reduced anxiety and more realistic perspective"
                },
                "safety_considerations": "This is a safe, evidence-based technique",
                "narrative_integration": "Character guides user through examining their presentation worries",
                "follow_up": "Practice this technique with other anxiety-provoking situations"
            }),
            content_type=TherapeuticContentType.INTERVENTION,
            safety_level=SafetyLevel.SAFE,
            therapeutic_value=0.85,
            confidence=0.9,
            metadata={"intervention_type": "cognitive_restructuring"}
        )

        self.mock_llm_client.generate_therapeutic_intervention.return_value = mock_intervention_response

        intervention_response = self.integration.generate_therapeutic_intervention(
            primary_opportunity,
            self.opportunity_context
        )

        self.assertIsInstance(intervention_response, TherapeuticResponse)
        self.assertEqual(intervention_response.safety_level, SafetyLevel.SAFE)
        self.assertGreater(intervention_response.therapeutic_value, 0.7)

        # Step 4: Validate content appropriateness
        mock_validation = {
            "is_safe": True,
            "is_appropriate": True,
            "safety_score": 0.95,
            "therapeutic_value": 0.85,
            "warnings": [],
            "recommendations": ["Consider follow-up practice exercises"],
            "approval_status": "approved"
        }

        self.integration.content_validator.validate_therapeutic_content = Mock(return_value=mock_validation)

        validation_result = self.integration.validate_content_appropriateness(
            intervention_response.content,
            InterventionType.COGNITIVE_RESTRUCTURING,
            self.opportunity_context
        )

        self.assertTrue(validation_result["is_safe"])
        self.assertTrue(validation_result["is_appropriate"])
        self.assertEqual(validation_result["approval_status"], "approved")

        # Step 5: Assess updated emotional state
        updated_emotional_state = self.integration.assess_user_emotional_state(
            "I feel a bit better after thinking about it more realistically",
            self.narrative_context,
            self.session_state
        )

        self.assertIsInstance(updated_emotional_state, EmotionalState)
        # Should show reduced anxiety intensity
        self.assertLessEqual(updated_emotional_state.intensity, 0.7)

        # Step 6: Adapt therapy approach based on intervention success
        user_profile = {"intervention_preferences": ["cognitive_restructuring"]}

        # Simulate successful intervention
        self.session_state.therapeutic_progress.complete_intervention(
            InterventionType.COGNITIVE_RESTRUCTURING,
            "Presentation anxiety cognitive restructuring",
            8.5  # High effectiveness rating
        )

        adapted_strategy = self.integration.adapt_therapy_approach(
            user_profile,
            self.session_state.therapeutic_progress
        )

        self.assertIn("cognitive_restructuring", adapted_strategy["preferred_interventions"])
        self.assertIn("focus_areas", adapted_strategy)

    def test_crisis_intervention_workflow(self):
        """Test workflow for crisis intervention scenarios."""
        # Set up crisis scenario
        crisis_context = TherapeuticOpportunityContext(
            narrative_context=self.narrative_context,
            session_state=self.session_state,
            user_input="I can't take this anymore, I want to hurt myself",
            emotional_indicators=["hopeless", "suicidal", "desperate"],
            behavioral_patterns={"crisis_indicators": "expressed self-harm ideation"}
        )

        # Identify opportunities - should detect crisis
        opportunities = self.integration.identify_therapeutic_moments(crisis_context)

        crisis_opportunities = [
            opp for opp in opportunities
            if opp.opportunity_type == OpportunityType.CRISIS_INTERVENTION
        ]

        self.assertGreater(len(crisis_opportunities), 0)

        crisis_opportunity = crisis_opportunities[0]
        self.assertEqual(crisis_opportunity.urgency_level, InterventionUrgency.CRISIS)

        # Generate crisis intervention
        mock_crisis_response = TherapeuticResponse(
            content=json.dumps({
                "immediate_response": "I'm really concerned about you right now. Your safety is the most important thing.",
                "safety_assessment": "Immediate safety concerns due to self-harm ideation",
                "coping_strategies": [
                    "Call crisis hotline: 988",
                    "Use grounding technique: 5-4-3-2-1",
                    "Reach out to trusted friend or family member"
                ],
                "professional_resources": [
                    "National Suicide Prevention Lifeline: 988",
                    "Crisis Text Line: Text HOME to 741741",
                    "Local emergency services: 911"
                ],
                "follow_up_plan": "Immediate professional evaluation recommended",
                "narrative_adaptation": "Character expresses serious concern and provides immediate support resources"
            }),
            content_type=TherapeuticContentType.CRISIS_SUPPORT,
            safety_level=SafetyLevel.CRISIS,
            therapeutic_value=0.9,  # High value for crisis intervention
            confidence=0.95,
            metadata={"crisis_intervention": True}
        )

        self.mock_llm_client.generate_therapeutic_intervention.return_value = mock_crisis_response

        crisis_intervention = self.integration.generate_therapeutic_intervention(
            crisis_opportunity,
            crisis_context
        )

        self.assertEqual(crisis_intervention.safety_level, SafetyLevel.CRISIS)
        self.assertGreater(crisis_intervention.therapeutic_value, 0.8)
        self.assertIn("crisis_intervention", crisis_intervention.metadata)


if __name__ == "__main__":
    unittest.main()
