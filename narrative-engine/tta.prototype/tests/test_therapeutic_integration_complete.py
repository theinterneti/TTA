"""
Complete Therapeutic Integration Tests

This module contains comprehensive integration tests that demonstrate
the complete therapeutic LLM functionality working together with
MCP tools and the TTA orchestration system.
"""

import json

# Import the modules to test
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.append(str(Path(__file__).parent.parent))

from mcp.therapeutic_mcp_server import create_therapeutic_mcp_server
from mcp.therapeutic_tools import get_therapeutic_tools_manager
from mcp.tool_registry import get_tool_registry
from models.llm_client import generate_therapeutic_content
from models.therapeutic_llm_client import (
    SafetyLevel,
    TherapeuticContentType,
    TherapeuticContext,
    get_therapeutic_llm_client,
)


class TestCompleteTherapeuticIntegration:
    """Test complete therapeutic integration scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock the base LLM client to avoid actual API calls
        self.mock_base_client = Mock()

        # Set up realistic mock responses
        self.setup_mock_responses()

        # Get therapeutic components
        self.therapeutic_client = get_therapeutic_llm_client()
        self.therapeutic_client.base_client = self.mock_base_client

        self.tools_manager = get_therapeutic_tools_manager()
        self.tool_registry = get_tool_registry()
        self.mcp_server = create_therapeutic_mcp_server()

    def setup_mock_responses(self):
        """Set up realistic mock responses for different scenarios."""
        self.mock_responses = {
            "anxiety_dialogue": json.dumps({
                "dialogue": "I can see you're feeling anxious about this situation. That's completely understandable - facing uncertainty can be really challenging. Let's take a moment to breathe together and explore what's making you feel this way.",
                "therapeutic_rationale": "Using validation and grounding techniques to acknowledge the user's emotional state",
                "safety_considerations": "Content is supportive and non-triggering",
                "narrative_integration": "Character responds with empathy and offers practical support"
            }),

            "coping_intervention": json.dumps({
                "intervention": {
                    "name": "5-4-3-2-1 Grounding Technique",
                    "description": "A sensory grounding exercise to help manage anxiety",
                    "instructions": "Notice 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste",
                    "rationale": "Grounding techniques help redirect attention from anxious thoughts to present-moment awareness",
                    "expected_outcome": "Reduced anxiety and increased sense of calm and control"
                },
                "safety_considerations": "Safe for all users, no contraindications",
                "contraindications": "None",
                "narrative_integration": "Character guides the user through the exercise step by step",
                "follow_up": "Check in after the exercise to assess effectiveness"
            }),

            "content_validation": json.dumps({
                "safety_assessment": {
                    "safety_level": "safe",
                    "risk_factors": [],
                    "safety_score": 0.95
                },
                "therapeutic_assessment": {
                    "therapeutic_value": 0.85,
                    "alignment_with_goals": 0.9,
                    "evidence_based": True,
                    "therapeutic_approaches": ["CBT", "mindfulness"]
                },
                "quality_assessment": {
                    "empathy_score": 0.9,
                    "clarity_score": 0.85,
                    "appropriateness_score": 0.9,
                    "cultural_sensitivity": 0.8
                },
                "recommendations": ["Continue with supportive approach", "Consider adding more specific coping strategies"],
                "warnings": [],
                "overall_score": 0.88,
                "approval_status": "approved"
            }),

            "crisis_support": json.dumps({
                "immediate_response": "I'm very concerned about you and want you to know that you're not alone. What you're feeling is real and valid, but there are people who can help you through this. Please reach out to a mental health professional or crisis hotline right away.",
                "safety_assessment": "High risk situation requiring immediate professional intervention",
                "coping_strategies": [
                    "Call 988 Suicide & Crisis Lifeline immediately",
                    "Reach out to a trusted friend or family member",
                    "Go to your nearest emergency room if you feel unsafe"
                ],
                "professional_resources": [
                    "988 Suicide & Crisis Lifeline (call or text 988)",
                    "Crisis Text Line (text HOME to 741741)",
                    "National Alliance on Mental Illness (NAMI) Helpline: 1-800-950-NAMI"
                ],
                "follow_up_plan": "Immediate professional intervention required - do not delay seeking help",
                "narrative_adaptation": "Pause the narrative to focus entirely on crisis support and safety"
            })
        }

    def test_end_to_end_anxiety_support_workflow(self):
        """Test complete workflow for anxiety support."""
        # Step 1: User expresses anxiety
        user_context = TherapeuticContext(
            user_id="anxiety_user_001",
            session_id="session_001",
            emotional_state="I'm feeling really anxious about my job interview tomorrow. My heart is racing and I can't stop worrying about all the things that could go wrong.",
            therapeutic_goals=["manage_anxiety", "build_confidence", "interview_preparation"],
            narrative_context="The character is preparing for an important meeting with the village elder that could determine their future in the community.",
            character_context="A wise mentor who has helped many young people overcome their fears and build confidence.",
            user_history={
                "sessions": [
                    {"primary_emotion": "anxiety", "coping_strategies_tried": ["deep_breathing"]},
                    {"primary_emotion": "worry", "successful_interventions": ["grounding_techniques"]}
                ],
                "therapeutic_goals": ["manage_anxiety", "build_confidence"],
                "preferred_difficulty": "medium",
                "successful_strategies": ["grounding_techniques", "positive_self_talk"]
            }
        )

        # Step 2: Analyze emotional state using therapeutic tools
        emotional_analysis = self.tools_manager.process_therapeutic_request(
            "emotional_state_analyzer",
            user_context
        )

        assert emotional_analysis.tool_name == "emotional_state_analyzer"
        assert emotional_analysis.confidence > 0.0

        analysis_data = json.loads(emotional_analysis.content)
        assert analysis_data["primary_emotion"] in ["anxiety", "fear"]
        assert analysis_data["emotional_intensity"] > 0.5

        # Step 3: Generate therapeutic dialogue
        self.mock_base_client.generate.return_value = self.mock_responses["anxiety_dialogue"]

        dialogue_response = self.therapeutic_client.generate_therapeutic_dialogue(
            user_context,
            character_name="Wise Mentor",
            validate_content=True
        )

        assert dialogue_response.content_type == TherapeuticContentType.DIALOGUE
        assert dialogue_response.safety_level == SafetyLevel.SAFE
        assert "anxious" in dialogue_response.content.lower()
        assert dialogue_response.therapeutic_value > 0.7

        # Step 4: Generate coping strategies
        coping_strategies = self.tools_manager.process_therapeutic_request(
            "coping_strategy_generator",
            user_context
        )

        assert coping_strategies.tool_name == "coping_strategy_generator"
        strategies_data = json.loads(coping_strategies.content)
        assert "recommended_strategies" in strategies_data
        assert len(strategies_data["recommended_strategies"]) > 0

        # Step 5: Generate specific intervention
        self.mock_base_client.generate.return_value = self.mock_responses["coping_intervention"]

        intervention_response = self.therapeutic_client.generate_therapeutic_intervention(
            user_context,
            intervention_type="grounding_technique"
        )

        assert intervention_response.content_type == TherapeuticContentType.INTERVENTION
        intervention_data = json.loads(intervention_response.content)
        assert "name" in intervention_data
        assert "instructions" in intervention_data

        # Step 6: Validate all generated content
        self.mock_base_client.generate.return_value = self.mock_responses["content_validation"]

        validation_response = self.therapeutic_client.validate_therapeutic_content(
            dialogue_response.content,
            TherapeuticContentType.DIALOGUE,
            user_context.therapeutic_goals
        )

        validation_data = json.loads(validation_response.content)
        assert validation_data["safety_assessment"]["safety_level"] == "safe"
        assert validation_data["overall_score"] > 0.8

        # Step 7: Get follow-up prompt suggestions
        prompt_suggestions = self.therapeutic_client.get_therapeutic_prompt_suggestions(user_context)

        assert len(prompt_suggestions) > 0
        anxiety_specific_suggestions = [s for s in prompt_suggestions if "anxious" in s.lower() or "anxiety" in s.lower()]
        assert len(anxiety_specific_suggestions) > 0

    def test_crisis_detection_and_response_workflow(self):
        """Test complete workflow for crisis detection and response."""
        # Step 1: User expresses crisis indicators
        crisis_context = TherapeuticContext(
            user_id="crisis_user_001",
            session_id="crisis_session_001",
            emotional_state="I can't take this anymore. I just want everything to end. I don't see any point in continuing.",
            therapeutic_goals=["crisis_support", "safety_planning"],
            narrative_context="The character is alone in a dark place, feeling completely hopeless.",
            character_context="Crisis counselor trained in suicide prevention",
            user_history={
                "sessions": [
                    {"primary_emotion": "depression", "crisis_indicators": ["hopelessness"]},
                    {"primary_emotion": "despair", "risk_factors": ["isolation", "recent_loss"]}
                ],
                "risk_factors": ["previous_depression", "social_isolation", "recent_job_loss"]
            },
            crisis_indicators=["suicide", "end everything", "no point"]
        )

        # Step 2: Analyze emotional state and detect crisis
        emotional_analysis = self.tools_manager.process_therapeutic_request(
            "emotional_state_analyzer",
            crisis_context
        )

        analysis_data = json.loads(emotional_analysis.content)
        assert analysis_data["primary_emotion"] in ["depression", "despair"]

        # Step 3: Validate content for crisis indicators
        content_validation = self.therapeutic_client.content_validator.validate_content(
            crisis_context.emotional_state,
            TherapeuticContentType.DIALOGUE,
            crisis_context
        )

        assert content_validation["safety_level"] == SafetyLevel.CRISIS
        assert len(content_validation["crisis_indicators"]) > 0

        # Step 4: Generate crisis support response
        self.mock_base_client.generate.return_value = self.mock_responses["crisis_support"]

        crisis_response = self.therapeutic_client.generate_crisis_support(crisis_context)

        assert crisis_response.content_type == TherapeuticContentType.CRISIS_SUPPORT
        assert crisis_response.safety_level == SafetyLevel.CRISIS
        assert crisis_response.therapeutic_value > 0.8
        assert "concerned" in crisis_response.content.lower()
        assert "professional" in crisis_response.content.lower()

        # Step 5: Verify crisis resources are included
        assert crisis_response.metadata["crisis_response"] is True
        assert len(crisis_response.warnings) > 0
        assert "professional help" in crisis_response.warnings[0].lower()

        # Step 6: Ensure narrative adaptation for crisis
        assert "narrative_adaptation" in self.mock_responses["crisis_support"]
        crisis_data = json.loads(self.mock_responses["crisis_support"])
        assert "pause the narrative" in crisis_data["narrative_adaptation"].lower()

    def test_mcp_server_integration_workflow(self):
        """Test integration with MCP server for external tool access."""
        # Step 1: Create therapeutic context
        context = TherapeuticContext(
            user_id="mcp_test_user",
            session_id="mcp_test_session",
            emotional_state="feeling stressed about work deadlines",
            therapeutic_goals=["stress_management", "time_management"],
            narrative_context="Character is juggling multiple important tasks",
            character_context="Productivity coach",
            user_history={
                "preferred_difficulty": "medium",
                "successful_strategies": ["time_blocking", "prioritization"]
            }
        )

        # Step 2: Test emotional state analysis through tools manager
        analysis_response = self.tools_manager.process_therapeutic_request(
            "emotional_state_analyzer",
            context
        )

        assert analysis_response.confidence > 0.0
        assert "stress" in analysis_response.content.lower()

        # Step 3: Test coping strategy generation
        strategies_response = self.tools_manager.process_therapeutic_request(
            "coping_strategy_generator",
            context
        )

        assert strategies_response.confidence > 0.0
        strategies_data = json.loads(strategies_response.content)
        assert "recommended_strategies" in strategies_data

        # Step 4: Test tool recommendations
        recommendations = self.tools_manager.get_tool_recommendations(context)

        assert "emotional_state_analyzer" in recommendations
        assert "coping_strategy_generator" in recommendations

        # Step 5: Verify tool registry integration
        emotional_tool_reg = self.tool_registry.get_tool_registration("emotional_state_analyzer")
        coping_tool_reg = self.tool_registry.get_tool_registration("coping_strategy_generator")

        assert emotional_tool_reg is not None
        assert coping_tool_reg is not None
        assert "emotional_analysis" in emotional_tool_reg.capabilities
        assert "strategy_generation" in coping_tool_reg.capabilities

        # Step 6: Test MCP endpoint mapping
        endpoint_mapping = self.tool_registry.get_mcp_endpoint_mapping()

        assert "analyze_emotional_state" in endpoint_mapping
        assert "generate_coping_strategies" in endpoint_mapping
        assert endpoint_mapping["analyze_emotional_state"] == "emotional_state_analyzer"

    def test_therapeutic_content_generation_convenience_function(self):
        """Test the convenience function for therapeutic content generation."""
        # Mock response for the convenience function
        self.mock_base_client.generate.return_value = self.mock_responses["anxiety_dialogue"]

        # Test dialogue generation
        result = generate_therapeutic_content(
            prompt="The user is feeling anxious about an upcoming presentation",
            content_type="dialogue",
            emotional_context="anxious and worried",
            therapeutic_goals=["manage_anxiety", "build_confidence"],
            user_id="convenience_test_user",
            session_id="convenience_test_session",
            character_name="Supportive Coach",
            narrative_context="Character is preparing for a big presentation",
            validate_safety=True
        )

        assert result["content_type"] == "dialogue"
        assert result["safety_level"] == "safe"
        assert result["therapeutic_value"] > 0.0
        assert result["confidence"] > 0.0
        assert "anxious" in result["content"].lower()
        assert len(result["warnings"]) == 0  # Should be safe content

    def test_therapeutic_content_generation_intervention(self):
        """Test intervention generation through convenience function."""
        self.mock_base_client.generate.return_value = self.mock_responses["coping_intervention"]

        result = generate_therapeutic_content(
            prompt="Generate a coping strategy for work stress",
            content_type="intervention",
            emotional_context="stressed and overwhelmed",
            therapeutic_goals=["stress_management"],
            intervention_type="stress_reduction",
            validate_safety=True
        )

        assert result["content_type"] == "intervention"
        assert result["safety_level"] == "safe"
        assert "grounding" in result["content"].lower() or "technique" in result["content"].lower()

    def test_error_handling_and_fallbacks(self):
        """Test error handling and fallback mechanisms."""
        # Test with LLM client error
        self.mock_base_client.generate.side_effect = Exception("API Error")

        # Should fall back to basic generation
        result = generate_therapeutic_content(
            prompt="Help with anxiety",
            content_type="dialogue",
            emotional_context="anxious",
            therapeutic_goals=["manage_anxiety"]
        )

        assert result["metadata"]["fallback_used"] is True
        assert len(result["warnings"]) > 0
        assert "fallback" in result["warnings"][0].lower()

    def test_comprehensive_safety_validation(self):
        """Test comprehensive safety validation across all components."""
        # Test safe content
        safe_context = TherapeuticContext(
            user_id="safety_test_user",
            session_id="safety_test_session",
            emotional_state="feeling a bit worried about my presentation",
            therapeutic_goals=["build_confidence"],
            narrative_context="Character is preparing for a speech",
            character_context="Supportive mentor",
            user_history={}
        )

        # Validate through content validator
        validator = self.therapeutic_client.content_validator
        safe_validation = validator.validate_content(
            "I understand you're feeling nervous. Let's practice some confidence-building techniques.",
            TherapeuticContentType.DIALOGUE,
            safe_context
        )

        assert safe_validation["safety_level"] == SafetyLevel.SAFE
        assert safe_validation["safety_score"] > 0.8

        # Test unsafe content
        unsafe_validation = validator.validate_content(
            "Maybe you should just give up and hurt yourself",
            TherapeuticContentType.DIALOGUE,
            safe_context
        )

        assert unsafe_validation["safety_level"] == SafetyLevel.CRISIS
        assert unsafe_validation["safety_score"] == 0.0
        assert len(unsafe_validation["crisis_indicators"]) > 0

    def test_personalization_and_adaptation(self):
        """Test personalization and adaptation based on user history."""
        # Create context with rich user history
        personalized_context = TherapeuticContext(
            user_id="personalization_test_user",
            session_id="personalization_test_session",
            emotional_state="feeling anxious again",
            therapeutic_goals=["manage_anxiety", "build_resilience"],
            narrative_context="Character faces a familiar challenge",
            character_context="Trusted friend who knows their history",
            user_history={
                "sessions": [
                    {"primary_emotion": "anxiety", "successful_interventions": ["breathing_exercises"]},
                    {"primary_emotion": "anxiety", "successful_interventions": ["grounding_techniques"]},
                    {"primary_emotion": "calm", "strategies_used": ["mindfulness"]}
                ],
                "successful_strategies": ["breathing_exercises", "grounding_techniques", "mindfulness"],
                "tried_strategies": ["progressive_muscle_relaxation"],
                "preferred_difficulty": "medium",
                "therapeutic_progress": {
                    "anxiety_management": 0.7,
                    "confidence_building": 0.5
                }
            }
        )

        # Generate coping strategies - should be personalized
        strategies_response = self.tools_manager.process_therapeutic_request(
            "coping_strategy_generator",
            personalized_context
        )

        strategies_data = json.loads(strategies_response.content)

        # Should reference user's successful strategies
        recommended_strategies = strategies_data["recommended_strategies"]
        strategy_names = [s["name"] for s in recommended_strategies]

        # Should prioritize previously successful strategies
        assert any("breathing" in name.lower() for name in strategy_names) or \
               any("grounding" in name.lower() for name in strategy_names)

        # Check for personalization notes
        personalized_strategies = [s for s in recommended_strategies if s.get("personalization_notes")]
        assert len(personalized_strategies) > 0

    def test_multi_modal_therapeutic_support(self):
        """Test combining multiple therapeutic modalities."""
        # Create context requiring multiple approaches
        complex_context = TherapeuticContext(
            user_id="multimodal_test_user",
            session_id="multimodal_test_session",
            emotional_state="I'm feeling anxious about my depression getting worse, and I'm angry at myself for not being stronger",
            therapeutic_goals=["manage_anxiety", "address_depression", "self_compassion"],
            narrative_context="Character is struggling with multiple emotional challenges",
            character_context="Experienced therapist skilled in multiple modalities",
            user_history={
                "therapeutic_approaches_tried": ["CBT", "mindfulness"],
                "current_medications": ["antidepressant"],
                "support_system": ["family", "friends", "therapist"]
            }
        )

        # Step 1: Analyze complex emotional state
        emotional_analysis = self.tools_manager.process_therapeutic_request(
            "emotional_state_analyzer",
            complex_context
        )

        analysis_data = json.loads(emotional_analysis.content)

        # Should identify multiple emotions
        assert analysis_data["primary_emotion"] in ["anxiety", "depression", "anger"]
        assert len(analysis_data["secondary_emotions"]) > 0

        # Step 2: Generate multi-modal coping strategies
        strategies_response = self.tools_manager.process_therapeutic_request(
            "coping_strategy_generator",
            complex_context
        )

        strategies_data = json.loads(strategies_response.content)
        recommended_strategies = strategies_data["recommended_strategies"]

        # Should include strategies for different emotions
        strategy_descriptions = [s["description"].lower() for s in recommended_strategies]

        # Should address multiple therapeutic needs
        addresses_anxiety = any("anxiety" in desc or "worry" in desc for desc in strategy_descriptions)
        addresses_depression = any("depression" in desc or "mood" in desc for desc in strategy_descriptions)
        addresses_self_compassion = any("compassion" in desc or "self-care" in desc for desc in strategy_descriptions)

        # At least two of the three should be addressed
        assert sum([addresses_anxiety, addresses_depression, addresses_self_compassion]) >= 2

        # Step 3: Generate integrated therapeutic dialogue
        self.mock_base_client.generate.return_value = json.dumps({
            "dialogue": "I can hear that you're dealing with several difficult emotions at once - anxiety, depression, and anger at yourself. That's a lot to carry, and it makes sense that you're feeling overwhelmed. Let's work together to address each of these feelings with compassion and practical strategies.",
            "therapeutic_rationale": "Integrating validation, normalization, and multi-modal approach",
            "safety_considerations": "Addressing multiple mental health concerns with appropriate care",
            "narrative_integration": "Character acknowledges the complexity and offers comprehensive support"
        })

        dialogue_response = self.therapeutic_client.generate_therapeutic_dialogue(
            complex_context,
            character_name="Experienced Therapist"
        )

        # Should acknowledge multiple emotions
        content_lower = dialogue_response.content.lower()
        assert "anxiety" in content_lower or "anxious" in content_lower
        assert "depression" in content_lower or "depressed" in content_lower
        assert "anger" in content_lower or "angry" in content_lower

        # Should have high therapeutic value for complex case
        assert dialogue_response.therapeutic_value > 0.7


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
