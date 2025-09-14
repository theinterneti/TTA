"""
Tests for Therapeutic LLM Client

This module contains tests for the therapeutic LLM client functionality,
including dialogue generation, content validation, and safety checks.
"""

import json

# Import the modules to test
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.append(str(Path(__file__).parent.parent))

from models.therapeutic_llm_client import (
    SafetyLevel,
    TherapeuticContentType,
    TherapeuticContentValidator,
    TherapeuticContext,
    TherapeuticLLMClient,
    TherapeuticPromptTemplate,
    TherapeuticResponse,
    get_therapeutic_llm_client,
)


class TestTherapeuticPromptTemplate:
    """Test therapeutic prompt template functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.template_system = TherapeuticPromptTemplate()

    def test_template_initialization(self):
        """Test template system initialization."""
        assert len(self.template_system.templates) > 0
        assert "dialogue_generation" in self.template_system.templates
        assert "intervention_generation" in self.template_system.templates
        assert "content_validation" in self.template_system.templates
        assert "crisis_support" in self.template_system.templates

    def test_get_template(self):
        """Test getting a template."""
        template = self.template_system.get_template("dialogue_generation")

        assert template is not None
        assert "system" in template
        assert "user" in template
        assert "therapeutic" in template["system"].lower()

    def test_get_nonexistent_template(self):
        """Test getting a non-existent template."""
        template = self.template_system.get_template("nonexistent_template")
        assert template is None

    def test_format_template(self):
        """Test formatting a template with variables."""
        template_vars = {
            "emotional_state": "feeling anxious",
            "therapeutic_goals": "manage anxiety, build confidence",
            "narrative_context": "character is in a forest",
            "character_context": "wise mentor",
            "user_history": "{}",
            "content_type": "dialogue"
        }

        result = self.template_system.format_template("dialogue_generation", **template_vars)

        assert result is not None
        system_prompt, user_prompt = result
        assert "therapeutic" in system_prompt.lower()
        assert "feeling anxious" in user_prompt
        assert "manage anxiety" in user_prompt

    def test_format_template_missing_variables(self):
        """Test formatting template with missing variables."""
        result = self.template_system.format_template("dialogue_generation", emotional_state="anxious")

        # Should return None due to missing required variables
        assert result is None

    def test_crisis_support_template(self):
        """Test crisis support template."""
        template = self.template_system.get_template("crisis_support")

        assert template is not None
        assert "crisis" in template["system"].lower()
        assert "safety" in template["system"].lower()
        assert "professional help" in template["system"].lower()


class TestTherapeuticContentValidator:
    """Test therapeutic content validator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = TherapeuticContentValidator()

    def test_validator_initialization(self):
        """Test validator initialization."""
        assert len(self.validator.crisis_keywords) > 0
        assert len(self.validator.warning_keywords) > 0
        assert len(self.validator.positive_indicators) > 0
        assert "suicide" in self.validator.crisis_keywords
        assert "hope" in self.validator.positive_indicators

    def test_validate_safe_content(self):
        """Test validating safe therapeutic content."""
        safe_content = "I understand you're feeling anxious. Let's try some deep breathing exercises together."

        validation = self.validator.validate_content(safe_content, TherapeuticContentType.DIALOGUE)

        assert validation["safety_level"] == SafetyLevel.SAFE
        assert validation["safety_score"] > 0.8
        assert len(validation["crisis_indicators"]) == 0
        assert validation["therapeutic_value"] > 0.5

    def test_validate_crisis_content(self):
        """Test validating content with crisis indicators."""
        crisis_content = "I want to kill myself and end it all"

        validation = self.validator.validate_content(crisis_content, TherapeuticContentType.DIALOGUE)

        assert validation["safety_level"] == SafetyLevel.CRISIS
        assert validation["safety_score"] == 0.0
        assert len(validation["crisis_indicators"]) > 0
        assert "CRISIS" in validation["warnings"][0]

    def test_validate_warning_content(self):
        """Test validating content with warning indicators."""
        warning_content = "The character discusses their history of abuse and trauma"

        validation = self.validator.validate_content(warning_content, TherapeuticContentType.NARRATIVE)

        assert validation["safety_level"] == SafetyLevel.CAUTION
        assert validation["safety_score"] < 1.0
        assert len(validation["warnings"]) > 0
        assert "sensitive topics" in validation["warnings"][0].lower()

    def test_validate_positive_content(self):
        """Test validating content with positive therapeutic indicators."""
        positive_content = "This therapy session helped me find hope and develop coping strategies for healing"

        validation = self.validator.validate_content(positive_content, TherapeuticContentType.DIALOGUE)

        assert validation["safety_level"] == SafetyLevel.SAFE
        assert validation["therapeutic_value"] > 0.7
        assert len(validation["positive_indicators"]) > 0

    def test_is_content_safe(self):
        """Test quick safety check."""
        safe_content = "Let's practice mindfulness together"
        unsafe_content = "I want to hurt myself"

        assert self.validator.is_content_safe(safe_content) is True
        assert self.validator.is_content_safe(unsafe_content) is False

    def test_extract_crisis_indicators(self):
        """Test extracting crisis indicators."""
        crisis_content = "I'm thinking about suicide and want to end it all"

        indicators = self.validator.extract_crisis_indicators(crisis_content)

        assert len(indicators) > 0
        assert "suicide" in indicators


class TestTherapeuticLLMClient:
    """Test therapeutic LLM client functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock the base LLM client
        self.mock_base_client = Mock()
        self.therapeutic_client = TherapeuticLLMClient(self.mock_base_client)

        # Sample therapeutic context
        self.sample_context = TherapeuticContext(
            user_id="test_user",
            session_id="test_session",
            emotional_state="feeling anxious and worried",
            therapeutic_goals=["manage_anxiety", "build_confidence"],
            narrative_context="The character is standing at a crossroads in a peaceful forest",
            character_context="A wise mentor who provides guidance and support",
            user_history={
                "sessions": [{"primary_emotion": "anxiety"}],
                "therapeutic_goals": ["manage_anxiety"],
                "preferred_difficulty": "medium"
            }
        )

    def test_client_initialization(self):
        """Test therapeutic LLM client initialization."""
        assert self.therapeutic_client.base_client is not None
        assert self.therapeutic_client.prompt_templates is not None
        assert self.therapeutic_client.content_validator is not None
        assert self.therapeutic_client.therapeutic_temperature == 0.7
        assert self.therapeutic_client.therapeutic_max_tokens == 1024

    def test_generate_therapeutic_dialogue_success(self):
        """Test successful therapeutic dialogue generation."""
        # Mock successful LLM response
        mock_response = json.dumps({
            "dialogue": "I can see you're feeling anxious. That's completely understandable. Let's take a moment to breathe together and explore what's causing these feelings.",
            "therapeutic_rationale": "Using validation and grounding techniques",
            "safety_considerations": "Content is safe and supportive",
            "narrative_integration": "Fits naturally into mentor character role"
        })

        self.mock_base_client.generate.return_value = mock_response

        response = self.therapeutic_client.generate_therapeutic_dialogue(
            self.sample_context,
            character_name="Wise Mentor"
        )

        assert isinstance(response, TherapeuticResponse)
        assert response.content_type == TherapeuticContentType.DIALOGUE
        assert response.safety_level == SafetyLevel.SAFE
        assert response.confidence > 0.0
        assert response.therapeutic_value > 0.0
        assert "anxious" in response.content.lower()
        assert response.metadata["character_name"] == "Wise Mentor"

    def test_generate_therapeutic_dialogue_json_parse_error(self):
        """Test dialogue generation with JSON parse error."""
        # Mock LLM response that's not valid JSON
        self.mock_base_client.generate.return_value = "I understand you're feeling anxious. Let's work through this together."

        response = self.therapeutic_client.generate_therapeutic_dialogue(self.sample_context)

        assert isinstance(response, TherapeuticResponse)
        assert response.content_type == TherapeuticContentType.DIALOGUE
        assert "anxious" in response.content.lower()
        # Should still work with fallback parsing

    def test_generate_therapeutic_dialogue_with_validation(self):
        """Test dialogue generation with content validation."""
        # Mock safe dialogue response
        mock_response = json.dumps({
            "dialogue": "Let's practice some breathing exercises to help with your anxiety."
        })

        self.mock_base_client.generate.return_value = mock_response

        response = self.therapeutic_client.generate_therapeutic_dialogue(
            self.sample_context,
            validate_content=True
        )

        assert response.safety_level == SafetyLevel.SAFE
        assert response.metadata["validation_performed"] is True

    def test_generate_therapeutic_dialogue_crisis_content(self):
        """Test dialogue generation that produces crisis content."""
        # Mock response with crisis indicators
        mock_response = json.dumps({
            "dialogue": "I understand you want to hurt yourself, but let's talk about this."
        })

        self.mock_base_client.generate.return_value = mock_response

        response = self.therapeutic_client.generate_therapeutic_dialogue(
            self.sample_context,
            validate_content=True
        )

        # Should detect crisis content
        assert response.safety_level == SafetyLevel.CRISIS
        assert len(response.warnings) > 0

    def test_generate_therapeutic_dialogue_error_handling(self):
        """Test dialogue generation error handling."""
        # Mock LLM client to raise an exception
        self.mock_base_client.generate.side_effect = Exception("LLM API error")

        response = self.therapeutic_client.generate_therapeutic_dialogue(self.sample_context)

        assert isinstance(response, TherapeuticResponse)
        assert response.content_type == TherapeuticContentType.DIALOGUE
        assert response.safety_level == SafetyLevel.SAFE  # Fallback is safe
        assert response.metadata["fallback_used"] is True
        assert len(response.warnings) > 0

    def test_generate_therapeutic_intervention(self):
        """Test therapeutic intervention generation."""
        # Mock intervention response
        mock_response = json.dumps({
            "intervention": {
                "name": "Deep Breathing Exercise",
                "description": "A simple breathing technique to reduce anxiety",
                "instructions": "Breathe in for 4 counts, hold for 4, breathe out for 6",
                "rationale": "Activates the parasympathetic nervous system",
                "expected_outcome": "Reduced anxiety and increased calm"
            },
            "safety_considerations": "Safe for most people",
            "narrative_integration": "Character guides user through the exercise"
        })

        self.mock_base_client.generate.return_value = mock_response

        response = self.therapeutic_client.generate_therapeutic_intervention(
            self.sample_context,
            intervention_type="breathing_exercise"
        )

        assert isinstance(response, TherapeuticResponse)
        assert response.content_type == TherapeuticContentType.INTERVENTION
        assert response.confidence > 0.0
        assert "breathing" in response.content.lower()
        assert response.metadata["intervention_type"] == "breathing_exercise"

    def test_generate_therapeutic_intervention_error(self):
        """Test intervention generation error handling."""
        self.mock_base_client.generate.side_effect = Exception("Generation error")

        response = self.therapeutic_client.generate_therapeutic_intervention(self.sample_context)

        assert isinstance(response, TherapeuticResponse)
        assert response.content_type == TherapeuticContentType.INTERVENTION
        assert response.safety_level == SafetyLevel.SAFE
        assert "breathe" in response.content.lower()  # Fallback breathing exercise
        assert response.metadata["fallback_used"] is True

    def test_validate_therapeutic_content(self):
        """Test LLM-based content validation."""
        # Mock validation response
        mock_response = json.dumps({
            "safety_assessment": {
                "safety_level": "safe",
                "risk_factors": [],
                "safety_score": 0.9
            },
            "therapeutic_assessment": {
                "therapeutic_value": 0.8,
                "alignment_with_goals": 0.9,
                "evidence_based": True
            },
            "quality_assessment": {
                "empathy_score": 0.8,
                "clarity_score": 0.9,
                "appropriateness_score": 0.8
            },
            "recommendations": ["Continue with supportive approach"],
            "warnings": [],
            "overall_score": 0.85,
            "approval_status": "approved"
        })

        self.mock_base_client.generate.return_value = mock_response

        content_to_validate = "I understand you're going through a difficult time. Let's work together to find some coping strategies."

        response = self.therapeutic_client.validate_therapeutic_content(
            content_to_validate,
            TherapeuticContentType.DIALOGUE,
            ["emotional_support", "coping_strategies"]
        )

        assert isinstance(response, TherapeuticResponse)
        assert response.content_type == TherapeuticContentType.REFLECTION
        assert response.safety_level == SafetyLevel.SAFE
        assert response.confidence == 0.9
        assert response.therapeutic_value == 0.8

    def test_validate_therapeutic_content_error(self):
        """Test content validation error handling."""
        self.mock_base_client.generate.side_effect = Exception("Validation error")

        content_to_validate = "Test content for validation"

        response = self.therapeutic_client.validate_therapeutic_content(
            content_to_validate,
            TherapeuticContentType.DIALOGUE
        )

        assert isinstance(response, TherapeuticResponse)
        assert response.metadata["fallback_validation"] is True
        # Should fall back to rule-based validation

    def test_generate_crisis_support(self):
        """Test crisis support generation."""
        # Create crisis context
        crisis_context = TherapeuticContext(
            user_id="crisis_user",
            session_id="crisis_session",
            emotional_state="feeling suicidal and hopeless",
            therapeutic_goals=["crisis_support"],
            narrative_context="Character is in a dark place",
            character_context="Crisis counselor",
            user_history={},
            crisis_indicators=["suicide", "hopeless"]
        )

        # Mock crisis support response
        mock_response = json.dumps({
            "immediate_response": "I'm very concerned about you and want to help. You don't have to go through this alone. Please reach out to a mental health professional immediately.",
            "safety_assessment": "High risk situation requiring immediate intervention",
            "coping_strategies": ["Call crisis hotline", "Reach out to trusted person", "Go to emergency room if needed"],
            "professional_resources": ["988 Suicide & Crisis Lifeline", "Local emergency services"],
            "follow_up_plan": "Immediate professional intervention required"
        })

        self.mock_base_client.generate.return_value = mock_response

        response = self.therapeutic_client.generate_crisis_support(crisis_context)

        assert isinstance(response, TherapeuticResponse)
        assert response.content_type == TherapeuticContentType.CRISIS_SUPPORT
        assert response.safety_level == SafetyLevel.CRISIS
        assert response.therapeutic_value > 0.8
        assert response.metadata["crisis_response"] is True
        assert len(response.warnings) > 0
        assert "professional help" in response.warnings[0].lower()

    def test_generate_crisis_support_error(self):
        """Test crisis support generation error handling."""
        crisis_context = TherapeuticContext(
            user_id="crisis_user",
            session_id="crisis_session",
            emotional_state="suicidal thoughts",
            therapeutic_goals=["crisis_support"],
            narrative_context="",
            character_context="",
            user_history={},
            crisis_indicators=["suicide"]
        )

        self.mock_base_client.generate.side_effect = Exception("Crisis generation error")

        response = self.therapeutic_client.generate_crisis_support(crisis_context)

        assert isinstance(response, TherapeuticResponse)
        assert response.content_type == TherapeuticContentType.CRISIS_SUPPORT
        assert response.safety_level == SafetyLevel.CRISIS
        assert "988" in response.content  # Should include crisis hotline in fallback
        assert response.metadata["fallback_crisis_response"] is True

    def test_get_therapeutic_prompt_suggestions(self):
        """Test getting therapeutic prompt suggestions."""
        suggestions = self.therapeutic_client.get_therapeutic_prompt_suggestions(self.sample_context)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert len(suggestions) <= 10  # Should be limited to 10

        # Should include anxiety-specific suggestions
        anxiety_suggestions = [s for s in suggestions if "anxious" in s.lower() or "anxiety" in s.lower()]
        assert len(anxiety_suggestions) > 0

    def test_get_therapeutic_prompt_suggestions_depression(self):
        """Test prompt suggestions for depression context."""
        depression_context = TherapeuticContext(
            user_id="test_user",
            session_id="test_session",
            emotional_state="feeling sad and depressed",
            therapeutic_goals=["mood_improvement"],
            narrative_context="",
            character_context="",
            user_history={}
        )

        suggestions = self.therapeutic_client.get_therapeutic_prompt_suggestions(depression_context)

        # Should include depression-specific suggestions
        depression_suggestions = [s for s in suggestions if "comfort" in s.lower() or "hopeful" in s.lower()]
        assert len(depression_suggestions) > 0

    def test_get_therapeutic_prompt_suggestions_anger(self):
        """Test prompt suggestions for anger context."""
        anger_context = TherapeuticContext(
            user_id="test_user",
            session_id="test_session",
            emotional_state="feeling angry and frustrated",
            therapeutic_goals=["anger_management"],
            narrative_context="",
            character_context="",
            user_history={}
        )

        suggestions = self.therapeutic_client.get_therapeutic_prompt_suggestions(anger_context)

        # Should include anger-specific suggestions
        anger_suggestions = [s for s in suggestions if "anger" in s.lower() or "underneath" in s.lower()]
        assert len(anger_suggestions) > 0


class TestSingletonFunction:
    """Test singleton function for therapeutic LLM client."""

    def test_get_therapeutic_llm_client_singleton(self):
        """Test that get_therapeutic_llm_client returns singleton instance."""
        client1 = get_therapeutic_llm_client()
        client2 = get_therapeutic_llm_client()

        assert client1 is client2
        assert isinstance(client1, TherapeuticLLMClient)


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple components."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_base_client = Mock()
        self.therapeutic_client = TherapeuticLLMClient(self.mock_base_client)

    def test_full_therapeutic_workflow(self):
        """Test a complete therapeutic workflow."""
        # Context for anxious user
        context = TherapeuticContext(
            user_id="workflow_user",
            session_id="workflow_session",
            emotional_state="feeling overwhelmed with work stress",
            therapeutic_goals=["stress_management", "work_life_balance"],
            narrative_context="Character is facing multiple deadlines",
            character_context="Supportive colleague",
            user_history={
                "sessions": [{"primary_emotion": "stress"}],
                "successful_strategies": ["deep_breathing"]
            }
        )

        # Mock dialogue response
        dialogue_response = json.dumps({
            "dialogue": "I can see you're feeling overwhelmed with all these deadlines. That's a lot to handle. Let's take a step back and see how we can break this down into manageable pieces."
        })

        # Mock intervention response
        intervention_response = json.dumps({
            "intervention": {
                "name": "Priority Matrix",
                "description": "Organize tasks by urgency and importance",
                "instructions": "List all tasks, then categorize them into urgent/important quadrants"
            }
        })

        self.mock_base_client.generate.side_effect = [dialogue_response, intervention_response]

        # Generate dialogue
        dialogue_result = self.therapeutic_client.generate_therapeutic_dialogue(context)
        assert dialogue_result.content_type == TherapeuticContentType.DIALOGUE
        assert "overwhelmed" in dialogue_result.content.lower()

        # Generate intervention
        intervention_result = self.therapeutic_client.generate_therapeutic_intervention(context)
        assert intervention_result.content_type == TherapeuticContentType.INTERVENTION
        assert "priority" in intervention_result.content.lower()

        # Get prompt suggestions
        suggestions = self.therapeutic_client.get_therapeutic_prompt_suggestions(context)
        assert len(suggestions) > 0

    def test_crisis_detection_and_response_workflow(self):
        """Test crisis detection and response workflow."""
        # Context with crisis indicators
        crisis_context = TherapeuticContext(
            user_id="crisis_user",
            session_id="crisis_session",
            emotional_state="I don't want to live anymore",
            therapeutic_goals=["crisis_support"],
            narrative_context="Character is alone and desperate",
            character_context="Crisis counselor",
            user_history={},
            crisis_indicators=["suicide", "don't want to live"]
        )

        # First, validate the emotional state content
        validator = TherapeuticContentValidator()
        validation = validator.validate_content(
            crisis_context.emotional_state,
            TherapeuticContentType.DIALOGUE
        )

        assert validation["safety_level"] == SafetyLevel.CRISIS
        assert len(validation["crisis_indicators"]) > 0

        # Generate crisis support
        crisis_response = json.dumps({
            "immediate_response": "I'm very concerned about you. Please know that you're not alone and there is help available. Let's get you connected with someone who can provide immediate support."
        })

        self.mock_base_client.generate.return_value = crisis_response

        support_result = self.therapeutic_client.generate_crisis_support(crisis_context)

        assert support_result.content_type == TherapeuticContentType.CRISIS_SUPPORT
        assert support_result.safety_level == SafetyLevel.CRISIS
        assert support_result.therapeutic_value > 0.8
        assert "concerned" in support_result.content.lower()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
