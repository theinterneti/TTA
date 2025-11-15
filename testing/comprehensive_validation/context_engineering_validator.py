"""
AI Agent Context Engineering Validation System for TTA

This module provides comprehensive validation of context prompt engineering
across different AI agents (narrative, therapeutic, world-building) with
focus on quality assessment, consistency verification, and therapeutic
appropriateness.

Key Features:
- Context prompt quality assessment for each agent type
- Therapeutic context integration validation
- Agent-specific context consistency verification
- Context adaptation effectiveness measurement
- Excellence-focused context engineering evaluation
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from tta_ai.orchestration.models import AgentType

from enhanced_preference_ai_server import EnhancedContext, PlayerPreferences
from src.components.therapeutic_systems_enhanced.therapeutic_integration_system import (
    TherapeuticIntegrationSystem,
)

logger = logging.getLogger(__name__)


class ContextQualityDimension(Enum):
    """Dimensions for evaluating context quality."""

    THERAPEUTIC_RELEVANCE = "therapeutic_relevance"
    PERSONALIZATION_DEPTH = "personalization_depth"
    NARRATIVE_COHERENCE = "narrative_coherence"
    AGENT_SPECIFICITY = "agent_specificity"
    CONSISTENCY_MAINTENANCE = "consistency_maintenance"
    SAFETY_COMPLIANCE = "safety_compliance"


@dataclass
class ContextValidationMetrics:
    """Metrics for context engineering validation."""

    agent_type: str
    test_scenario: str
    context_quality_score: float  # 0-10 scale
    therapeutic_relevance: float  # 0-10 scale
    personalization_effectiveness: float  # 0-10 scale
    consistency_score: float  # 0-10 scale
    safety_compliance: float  # 0-10 scale

    # Detailed assessments
    quality_dimensions: dict[str, float] = field(default_factory=dict)
    context_elements_validated: list[str] = field(default_factory=list)
    therapeutic_goals_addressed: list[str] = field(default_factory=list)
    personalization_factors: list[str] = field(default_factory=list)

    # Issues and recommendations
    issues_identified: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Performance metrics
    context_generation_time: float = 0.0
    context_size_tokens: int = 0


@dataclass
class TestScenario:
    """Test scenario for context engineering validation."""

    scenario_id: str
    name: str
    description: str
    player_preferences: PlayerPreferences
    therapeutic_context: dict[str, Any]
    expected_context_elements: list[str]
    target_agent: AgentType
    complexity_level: str  # "simple", "moderate", "complex"


class ContextEngineeringValidator:
    """
    Comprehensive validation system for AI agent context engineering.

    Validates context prompt engineering across different agents with focus
    on therapeutic appropriateness, personalization, and narrative quality.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.therapeutic_system = TherapeuticIntegrationSystem()

        # Excellence targets for context engineering
        self.excellence_targets = {
            "therapeutic_relevance": 8.0,
            "personalization_effectiveness": 8.5,
            "narrative_coherence": 8.5,
            "consistency_score": 9.0,
            "safety_compliance": 9.5,
        }

        # Test scenarios
        self.test_scenarios = self._create_test_scenarios()

        # Validation results
        self.validation_results: list[ContextValidationMetrics] = []

    def _create_test_scenarios(self) -> list[TestScenario]:
        """Create comprehensive test scenarios for context validation."""
        scenarios = []

        # Scenario 1: Anxiety Management with Narrative Agent
        scenarios.append(
            TestScenario(
                scenario_id="anxiety_narrative_001",
                name="Anxiety Management - Narrative Context",
                description="Test narrative agent context for anxiety management scenario",
                player_preferences=PlayerPreferences(
                    player_id="test_user_001",
                    intensity_level="medium",
                    preferred_approaches=["cbt", "mindfulness"],
                    therapeutic_goals=["anxiety_management", "self_reflection"],
                    conversation_style="supportive",
                    character_name="Sage",
                    preferred_setting="peaceful_garden",
                    comfort_topics=["nature", "mindfulness"],
                    trigger_topics=["violence", "trauma"],
                ),
                therapeutic_context={
                    "current_emotional_state": "anxious",
                    "session_progress": "early_stage",
                    "therapeutic_focus": "grounding_techniques",
                    "safety_level": "stable",
                },
                expected_context_elements=[
                    "anxiety_management_techniques",
                    "peaceful_setting_description",
                    "supportive_character_voice",
                    "mindfulness_integration",
                    "safety_considerations",
                ],
                target_agent=AgentType.NGA,
                complexity_level="moderate",
            )
        )

        # Scenario 2: Depression Support with Therapeutic Agent
        scenarios.append(
            TestScenario(
                scenario_id="depression_therapeutic_002",
                name="Depression Support - Therapeutic Context",
                description="Test therapeutic agent context for depression support",
                player_preferences=PlayerPreferences(
                    player_id="test_user_002",
                    intensity_level="gentle",
                    preferred_approaches=["humanistic", "mindfulness"],
                    therapeutic_goals=["mood_improvement", "self_compassion"],
                    conversation_style="gentle",
                    character_name="Luna",
                    preferred_setting="cozy_library",
                    comfort_topics=["books", "creativity"],
                    trigger_topics=["criticism", "failure"],
                ),
                therapeutic_context={
                    "current_emotional_state": "low_mood",
                    "session_progress": "mid_stage",
                    "therapeutic_focus": "self_compassion",
                    "safety_level": "stable",
                },
                expected_context_elements=[
                    "self_compassion_techniques",
                    "gentle_encouragement",
                    "creative_expression_opportunities",
                    "mood_lifting_elements",
                    "validation_and_support",
                ],
                target_agent=AgentType.IPA,
                complexity_level="complex",
            )
        )

        # Scenario 3: World Building with Complex Preferences
        scenarios.append(
            TestScenario(
                scenario_id="worldbuilding_complex_003",
                name="Complex World Building Context",
                description="Test world building agent with complex user preferences",
                player_preferences=PlayerPreferences(
                    player_id="test_user_003",
                    intensity_level="high",
                    preferred_approaches=["cbt", "exposure_therapy"],
                    therapeutic_goals=["confidence_building", "social_skills"],
                    conversation_style="direct",
                    character_name="Atlas",
                    preferred_setting="mountain_village",
                    comfort_topics=["adventure", "challenge"],
                    trigger_topics=["abandonment", "isolation"],
                ),
                therapeutic_context={
                    "current_emotional_state": "determined",
                    "session_progress": "advanced_stage",
                    "therapeutic_focus": "confidence_building",
                    "safety_level": "stable",
                },
                expected_context_elements=[
                    "confidence_building_scenarios",
                    "social_interaction_opportunities",
                    "challenging_but_safe_environments",
                    "achievement_recognition",
                    "progressive_difficulty",
                ],
                target_agent=AgentType.WBA,
                complexity_level="complex",
            )
        )

        return scenarios

    async def validate_agent_context_engineering(
        self, agent_type: AgentType
    ) -> list[ContextValidationMetrics]:
        """
        Validate context engineering for a specific agent type.

        Args:
            agent_type: The agent type to validate

        Returns:
            List of validation metrics for each test scenario
        """
        results = []

        # Filter scenarios for this agent type
        agent_scenarios = [
            s for s in self.test_scenarios if s.target_agent == agent_type
        ]

        for scenario in agent_scenarios:
            logger.info(
                f"🔍 Validating context for {agent_type.value} - {scenario.name}"
            )

            start_time = time.time()

            try:
                # Generate context for the scenario
                context = await self._generate_agent_context(agent_type, scenario)

                # Validate context quality
                metrics = await self._assess_context_quality(
                    agent_type, scenario, context, time.time() - start_time
                )

                results.append(metrics)

            except Exception as e:
                logger.error(
                    f"❌ Context validation failed for {scenario.scenario_id}: {e}"
                )

                # Create error metrics
                error_metrics = ContextValidationMetrics(
                    agent_type=agent_type.value,
                    test_scenario=scenario.scenario_id,
                    context_quality_score=0.0,
                    therapeutic_relevance=0.0,
                    personalization_effectiveness=0.0,
                    consistency_score=0.0,
                    safety_compliance=0.0,
                    issues_identified=[str(e)],
                    recommendations=[
                        "Fix context generation issues",
                        "Review agent configuration",
                    ],
                    context_generation_time=time.time() - start_time,
                )
                results.append(error_metrics)

        return results

    async def _generate_agent_context(
        self, agent_type: AgentType, scenario: TestScenario
    ) -> dict[str, Any]:
        """Generate context for the specified agent and scenario."""

        # Create enhanced context based on scenario
        enhanced_context = EnhancedContext(
            user_message="Test message for context validation",
            player_preferences=scenario.player_preferences,
            session_state=scenario.therapeutic_context,
            turn_count=1,
        )

        # Generate agent-specific context
        if agent_type == AgentType.NGA:
            return await self._generate_narrative_context(enhanced_context, scenario)
        if agent_type == AgentType.IPA:
            return await self._generate_therapeutic_context(enhanced_context, scenario)
        if agent_type == AgentType.WBA:
            return await self._generate_worldbuilding_context(
                enhanced_context, scenario
            )
        raise ValueError(f"Unsupported agent type: {agent_type}")

    async def _generate_narrative_context(
        self, enhanced_context: EnhancedContext, scenario: TestScenario
    ) -> dict[str, Any]:
        """Generate narrative agent context."""
        return {
            "agent_type": "narrative_generator",
            "therapeutic_context": enhanced_context.therapeutic_context,
            "narrative_elements": {
                "setting": enhanced_context.player_preferences.preferred_setting,
                "character": enhanced_context.player_preferences.character_name,
                "tone": enhanced_context.player_preferences.conversation_style,
                "therapeutic_goals": enhanced_context.player_preferences.therapeutic_goals,
            },
            "safety_considerations": {
                "trigger_topics": enhanced_context.player_preferences.trigger_topics,
                "comfort_topics": enhanced_context.player_preferences.comfort_topics,
                "intensity_level": enhanced_context.player_preferences.intensity_level,
            },
            "personalization_factors": {
                "preferred_approaches": enhanced_context.player_preferences.preferred_approaches,
                "conversation_style": enhanced_context.player_preferences.conversation_style,
            },
        }

    async def _generate_therapeutic_context(
        self, enhanced_context: EnhancedContext, scenario: TestScenario
    ) -> dict[str, Any]:
        """Generate therapeutic agent context."""
        return {
            "agent_type": "therapeutic_processor",
            "therapeutic_framework": enhanced_context.player_preferences.preferred_approaches[
                0
            ]
            if enhanced_context.player_preferences.preferred_approaches
            else "cbt",
            "therapeutic_goals": enhanced_context.player_preferences.therapeutic_goals,
            "emotional_context": enhanced_context.session_state,
            "personalization": {
                "intensity_level": enhanced_context.player_preferences.intensity_level,
                "conversation_style": enhanced_context.player_preferences.conversation_style,
                "comfort_topics": enhanced_context.player_preferences.comfort_topics,
            },
            "safety_protocols": {
                "trigger_avoidance": enhanced_context.player_preferences.trigger_topics,
                "crisis_indicators": [],
                "safety_level": scenario.therapeutic_context.get(
                    "safety_level", "stable"
                ),
            },
        }

    async def _generate_worldbuilding_context(
        self, enhanced_context: EnhancedContext, scenario: TestScenario
    ) -> dict[str, Any]:
        """Generate world building agent context."""
        return {
            "agent_type": "world_builder",
            "world_parameters": {
                "setting": enhanced_context.player_preferences.preferred_setting,
                "complexity_level": scenario.complexity_level,
                "therapeutic_integration": True,
            },
            "character_context": {
                "main_character": enhanced_context.player_preferences.character_name,
                "therapeutic_role": "guide_and_companion",
            },
            "therapeutic_elements": {
                "goals": enhanced_context.player_preferences.therapeutic_goals,
                "approaches": enhanced_context.player_preferences.preferred_approaches,
                "safety_considerations": enhanced_context.player_preferences.trigger_topics,
            },
            "narrative_constraints": {
                "avoid_topics": enhanced_context.player_preferences.trigger_topics,
                "emphasize_topics": enhanced_context.player_preferences.comfort_topics,
                "intensity_level": enhanced_context.player_preferences.intensity_level,
            },
        }

    async def _assess_context_quality(
        self,
        agent_type: AgentType,
        scenario: TestScenario,
        context: dict[str, Any],
        generation_time: float,
    ) -> ContextValidationMetrics:
        """Assess the quality of generated context."""

        # Assess therapeutic relevance
        therapeutic_relevance = self._assess_therapeutic_relevance(context, scenario)

        # Assess personalization effectiveness
        personalization_effectiveness = self._assess_personalization_effectiveness(
            context, scenario
        )

        # Assess narrative coherence
        narrative_coherence = self._assess_narrative_coherence(context, scenario)

        # Assess consistency
        consistency_score = self._assess_consistency(context, scenario)

        # Assess safety compliance
        safety_compliance = self._assess_safety_compliance(context, scenario)

        # Calculate overall context quality score
        context_quality_score = (
            therapeutic_relevance * 0.25
            + personalization_effectiveness * 0.25
            + narrative_coherence * 0.20
            + consistency_score * 0.15
            + safety_compliance * 0.15
        )

        # Identify issues and generate recommendations
        issues = self._identify_context_issues(context, scenario)
        recommendations = self._generate_context_recommendations(
            therapeutic_relevance,
            personalization_effectiveness,
            narrative_coherence,
            consistency_score,
            safety_compliance,
        )

        return ContextValidationMetrics(
            agent_type=agent_type.value,
            test_scenario=scenario.scenario_id,
            context_quality_score=context_quality_score,
            therapeutic_relevance=therapeutic_relevance,
            personalization_effectiveness=personalization_effectiveness,
            consistency_score=consistency_score,
            safety_compliance=safety_compliance,
            quality_dimensions={
                "therapeutic_relevance": therapeutic_relevance,
                "personalization_effectiveness": personalization_effectiveness,
                "narrative_coherence": narrative_coherence,
                "consistency_score": consistency_score,
                "safety_compliance": safety_compliance,
            },
            context_elements_validated=list(context.keys()),
            therapeutic_goals_addressed=scenario.player_preferences.therapeutic_goals,
            personalization_factors=scenario.player_preferences.preferred_approaches,
            issues_identified=issues,
            recommendations=recommendations,
            context_generation_time=generation_time,
            context_size_tokens=len(json.dumps(context).split()),
        )

    def _assess_therapeutic_relevance(
        self, context: dict[str, Any], scenario: TestScenario
    ) -> float:
        """Assess how well the context addresses therapeutic goals."""
        score = 7.0  # Base score

        # Check if therapeutic goals are addressed
        therapeutic_goals = scenario.player_preferences.therapeutic_goals
        context_str = json.dumps(context).lower()

        for goal in therapeutic_goals:
            if goal.replace("_", " ") in context_str:
                score += 0.5

        # Check for therapeutic framework integration
        preferred_approaches = scenario.player_preferences.preferred_approaches
        for approach in preferred_approaches:
            if approach in context_str:
                score += 0.3

        # Check for safety considerations
        if "safety" in context_str or "trigger" in context_str:
            score += 0.5

        return min(10.0, score)

    def _assess_personalization_effectiveness(
        self, context: dict[str, Any], scenario: TestScenario
    ) -> float:
        """Assess how well the context is personalized to user preferences."""
        score = 7.0  # Base score

        prefs = scenario.player_preferences
        context_str = json.dumps(context).lower()

        # Check character name integration
        if prefs.character_name.lower() in context_str:
            score += 0.5

        # Check setting integration
        if prefs.preferred_setting.replace("_", " ") in context_str:
            score += 0.5

        # Check conversation style
        if prefs.conversation_style in context_str:
            score += 0.5

        # Check comfort topics
        for topic in prefs.comfort_topics:
            if topic in context_str:
                score += 0.2

        # Check trigger topic avoidance
        trigger_mentioned = any(topic in context_str for topic in prefs.trigger_topics)
        if not trigger_mentioned:
            score += 0.5
        else:
            score -= 1.0  # Penalty for mentioning triggers inappropriately

        return min(10.0, max(0.0, score))

    def _assess_narrative_coherence(
        self, context: dict[str, Any], scenario: TestScenario
    ) -> float:
        """Assess narrative coherence and consistency of the context."""
        score = 8.0  # Base score for coherence

        # Check for required narrative elements
        required_elements = scenario.expected_context_elements
        context_str = json.dumps(context).lower()

        elements_found = 0
        for element in required_elements:
            if element.replace("_", " ") in context_str:
                elements_found += 1

        # Score based on element coverage
        element_coverage = (
            elements_found / len(required_elements) if required_elements else 1.0
        )
        score = score * element_coverage

        # Check for internal consistency
        if "agent_type" in context and context["agent_type"]:
            score += 0.5

        return min(10.0, max(0.0, score))

    def _assess_consistency(
        self, context: dict[str, Any], scenario: TestScenario
    ) -> float:
        """Assess consistency of context with scenario requirements."""
        score = 8.5  # Base consistency score

        # Check agent type consistency
        expected_agent = scenario.target_agent.value.lower()
        if "agent_type" in context:
            if expected_agent in context["agent_type"].lower():
                score += 0.5

        # Check therapeutic context consistency
        if scenario.therapeutic_context:
            for value in scenario.therapeutic_context.values():
                context_str = json.dumps(context).lower()
                if str(value).lower() in context_str:
                    score += 0.2

        return min(10.0, score)

    def _assess_safety_compliance(
        self, context: dict[str, Any], scenario: TestScenario
    ) -> float:
        """Assess safety compliance of the generated context."""
        score = 9.0  # High base score for safety

        # Check for trigger topic avoidance
        trigger_topics = scenario.player_preferences.trigger_topics
        context_str = json.dumps(context).lower()

        for trigger in trigger_topics:
            if trigger in context_str:
                # Check if it's mentioned in safety context (acceptable)
                if "avoid" in context_str or "trigger" in context_str:
                    continue  # Acceptable mention in safety context
                score -= 2.0  # Penalty for inappropriate trigger mention

        # Check for safety protocols
        if "safety" in context_str:
            score += 0.5

        # Check intensity level compliance
        intensity = scenario.player_preferences.intensity_level
        if (
            intensity == "gentle"
            and "gentle" in context_str
            or intensity == "high"
            and ("challenge" in context_str or "intensive" in context_str)
        ):
            score += 0.3

        return min(10.0, max(0.0, score))

    def _identify_context_issues(
        self, context: dict[str, Any], scenario: TestScenario
    ) -> list[str]:
        """Identify potential issues with the generated context."""
        issues = []

        # Check for missing required elements
        required_elements = scenario.expected_context_elements
        context_str = json.dumps(context).lower()

        missing_elements = []
        for element in required_elements:
            if element.replace("_", " ") not in context_str:
                missing_elements.append(element)

        if missing_elements:
            issues.append(f"Missing required elements: {', '.join(missing_elements)}")

        # Check for trigger topic mentions
        trigger_topics = scenario.player_preferences.trigger_topics
        for trigger in trigger_topics:
            if trigger in context_str and "avoid" not in context_str:
                issues.append(f"Inappropriate mention of trigger topic: {trigger}")

        # Check for agent type mismatch
        expected_agent = scenario.target_agent.value.lower()
        if "agent_type" in context:
            if expected_agent not in context["agent_type"].lower():
                issues.append(f"Agent type mismatch: expected {expected_agent}")

        return issues

    def _generate_context_recommendations(
        self,
        therapeutic_relevance: float,
        personalization_effectiveness: float,
        narrative_coherence: float,
        consistency_score: float,
        safety_compliance: float,
    ) -> list[str]:
        """Generate recommendations for context improvement."""
        recommendations = []

        if therapeutic_relevance < self.excellence_targets["therapeutic_relevance"]:
            recommendations.append("Improve therapeutic goal integration in context")
            recommendations.append("Enhance therapeutic framework alignment")

        if (
            personalization_effectiveness
            < self.excellence_targets["personalization_effectiveness"]
        ):
            recommendations.append("Increase personalization depth")
            recommendations.append("Better integrate user preferences")

        if narrative_coherence < self.excellence_targets["narrative_coherence"]:
            recommendations.append("Improve narrative element integration")
            recommendations.append("Enhance context coherence and flow")

        if consistency_score < self.excellence_targets["consistency_score"]:
            recommendations.append("Improve context consistency")
            recommendations.append("Align context with scenario requirements")

        if safety_compliance < self.excellence_targets["safety_compliance"]:
            recommendations.append("Strengthen safety protocols")
            recommendations.append("Review trigger topic handling")

        if not recommendations:
            recommendations.append("Context engineering meets excellence standards")

        return recommendations


async def run_context_engineering_validation(
    agent_types: list[AgentType] = None,
) -> dict[str, list[ContextValidationMetrics]]:
    """
    Run comprehensive context engineering validation.

    Args:
        agent_types: List of agent types to validate (default: all)

    Returns:
        Dictionary mapping agent types to validation results
    """
    if agent_types is None:
        agent_types = [AgentType.NGA, AgentType.IPA, AgentType.WBA]

    config = {
        "excellence_targets": {
            "therapeutic_relevance": 8.0,
            "personalization_effectiveness": 8.5,
            "narrative_coherence": 8.5,
            "consistency_score": 9.0,
            "safety_compliance": 9.5,
        }
    }

    validator = ContextEngineeringValidator(config)
    results = {}

    for agent_type in agent_types:
        logger.info(f"🔍 Validating context engineering for {agent_type.value}")
        results[agent_type.value] = await validator.validate_agent_context_engineering(
            agent_type
        )

    return results


if __name__ == "__main__":
    import asyncio

    async def main():
        results = await run_context_engineering_validation()

        for metrics_list in results.values():
            for metrics in metrics_list:
                if metrics.issues_identified:
                    for _issue in metrics.issues_identified[:2]:
                        pass

                if metrics.recommendations:
                    for _rec in metrics.recommendations[:2]:
                        pass

    asyncio.run(main())
