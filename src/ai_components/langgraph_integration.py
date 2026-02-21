"""

# Logseq: [[TTA.dev/Ai_components/Langgraph_integration]]
LangGraph Integration for AI-Powered Narrative Workflows
Manages complex therapeutic conversation flows and decision trees
"""

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, TypedDict

import redis.asyncio as aioredis
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from .llm_factory import get_llm

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State structure for LangGraph workflows"""

    messages: list[BaseMessage]
    patient_id: str
    session_id: str
    therapeutic_context: dict[str, Any]
    emotional_state: dict[str, float]
    intervention_history: list[dict[str, Any]]
    current_scenario: str
    decision_points: list[dict[str, Any]]
    feature_flags: dict[str, bool]


class TherapeuticIntent(Enum):
    """Types of therapeutic intents"""

    EMOTIONAL_SUPPORT = "emotional_support"
    CRISIS_INTERVENTION = "crisis_intervention"
    SKILL_BUILDING = "skill_building"
    NARRATIVE_PROGRESSION = "narrative_progression"
    ASSESSMENT = "assessment"
    REFLECTION = "reflection"


@dataclass
class WorkflowNode:
    """Represents a node in the therapeutic workflow"""

    name: str
    function: Callable
    conditions: dict[str, Any]
    therapeutic_intent: TherapeuticIntent
    safety_checks: list[str]


class TherapeuticWorkflowManager:
    """Manages LangGraph-based therapeutic workflows"""

    def __init__(
        self,
        openai_api_key: str = "",  # kept for backward-compat; ignored when provider set
        redis_url: str = "redis://localhost:6379",
        model_name: str | None = None,
        provider: str | None = None,
    ):
        self.redis_url = redis_url
        self.model_name = model_name

        self.llm: ChatOpenAI = get_llm(
            provider=provider,
            model=model_name,
            temperature=0.7,
            max_tokens=1000,
        )

        self.redis: aioredis.Redis | None = None
        self.workflows: dict[str, StateGraph] = {}
        self.initialized = False

    async def initialize(self):
        """Initialize the workflow manager"""
        try:
            # Initialize Redis connection
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()

            # Create therapeutic workflows
            await self._create_therapeutic_workflows()

            self.initialized = True
            logger.info("Therapeutic Workflow Manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Therapeutic Workflow Manager: {str(e)}")
            raise

    async def _create_therapeutic_workflows(self):
        """Create the main therapeutic workflows"""

        # Main therapeutic conversation workflow
        main_workflow = StateGraph(WorkflowState)

        # Add nodes
        main_workflow.add_node("assess_emotional_state", self._assess_emotional_state)
        main_workflow.add_node("safety_check", self._safety_check)
        main_workflow.add_node("generate_response", self._generate_therapeutic_response)
        main_workflow.add_node("update_narrative", self._update_narrative_context)
        main_workflow.add_node("crisis_intervention", self._handle_crisis_intervention)
        main_workflow.add_node("skill_building", self._provide_skill_building)
        main_workflow.add_node("reflection", self._facilitate_reflection)

        # Define workflow edges with conditions
        main_workflow.add_conditional_edges(
            "assess_emotional_state",
            self._route_based_on_emotional_state,
            {
                "crisis": "crisis_intervention",
                "distressed": "safety_check",
                "stable": "generate_response",
                "engaged": "update_narrative",
            },
        )

        main_workflow.add_conditional_edges(
            "safety_check",
            self._route_based_on_safety,
            {
                "safe": "generate_response",
                "needs_support": "skill_building",
                "crisis": "crisis_intervention",
            },
        )

        main_workflow.add_edge("generate_response", "update_narrative")
        main_workflow.add_edge("update_narrative", "reflection")
        main_workflow.add_edge("skill_building", "reflection")
        main_workflow.add_edge("reflection", END)
        main_workflow.add_edge("crisis_intervention", END)

        # Set entry point
        main_workflow.set_entry_point("assess_emotional_state")

        # Compile the workflow
        self.workflows["main_therapeutic"] = main_workflow.compile()

        # Create specialized workflows
        await self._create_crisis_workflow()
        await self._create_skill_building_workflow()

    async def _create_crisis_workflow(self):
        """Create specialized crisis intervention workflow"""
        crisis_workflow = StateGraph(WorkflowState)

        crisis_workflow.add_node("immediate_safety", self._ensure_immediate_safety)
        crisis_workflow.add_node("crisis_assessment", self._assess_crisis_severity)
        crisis_workflow.add_node(
            "emergency_contacts", self._activate_emergency_contacts
        )
        crisis_workflow.add_node("stabilization", self._provide_stabilization)
        crisis_workflow.add_node("follow_up_plan", self._create_follow_up_plan)

        crisis_workflow.add_conditional_edges(
            "immediate_safety",
            self._route_crisis_severity,
            {
                "emergency": "emergency_contacts",
                "high_risk": "crisis_assessment",
                "stabilizing": "stabilization",
            },
        )

        crisis_workflow.add_edge("crisis_assessment", "stabilization")
        crisis_workflow.add_edge("emergency_contacts", "follow_up_plan")
        crisis_workflow.add_edge("stabilization", "follow_up_plan")
        crisis_workflow.add_edge("follow_up_plan", END)

        crisis_workflow.set_entry_point("immediate_safety")
        self.workflows["crisis_intervention"] = crisis_workflow.compile()

    async def _create_skill_building_workflow(self):
        """Create skill-building workflow"""
        skill_workflow = StateGraph(WorkflowState)

        skill_workflow.add_node("identify_skill_gap", self._identify_skill_gap)
        skill_workflow.add_node("select_technique", self._select_therapeutic_technique)
        skill_workflow.add_node("guided_practice", self._provide_guided_practice)
        skill_workflow.add_node("skill_assessment", self._assess_skill_progress)
        skill_workflow.add_node("reinforcement", self._provide_reinforcement)

        skill_workflow.add_edge("identify_skill_gap", "select_technique")
        skill_workflow.add_edge("select_technique", "guided_practice")
        skill_workflow.add_edge("guided_practice", "skill_assessment")
        skill_workflow.add_edge("skill_assessment", "reinforcement")
        skill_workflow.add_edge("reinforcement", END)

        skill_workflow.set_entry_point("identify_skill_gap")
        self.workflows["skill_building"] = skill_workflow.compile()

    async def process_patient_input(
        self,
        patient_id: str,
        session_id: str,
        user_message: str,
        therapeutic_context: dict[str, Any],
        feature_flags: dict[str, bool],
    ) -> dict[str, Any]:
        """Process patient input through the therapeutic workflow"""

        if not self.initialized:
            await self.initialize()

        # Create initial state
        initial_state = WorkflowState(
            messages=[HumanMessage(content=user_message)],
            patient_id=patient_id,
            session_id=session_id,
            therapeutic_context=therapeutic_context,
            emotional_state=therapeutic_context.get("emotional_state", {}),
            intervention_history=therapeutic_context.get("intervention_history", []),
            current_scenario=therapeutic_context.get("current_scenario", ""),
            decision_points=[],
            feature_flags=feature_flags,
        )

        # Select appropriate workflow
        workflow_name = self._select_workflow(initial_state)
        workflow = self.workflows.get(workflow_name, self.workflows["main_therapeutic"])

        try:
            # Execute workflow
            result = await workflow.ainvoke(initial_state)

            # Extract response
            response = self._extract_workflow_response(result)

            # Cache result for quick access
            await self._cache_workflow_result(session_id, response)

            logger.info(
                f"Processed patient input for session {session_id} using {workflow_name} workflow"
            )
            return response

        except Exception as e:
            logger.error(f"Error processing patient input: {str(e)}")
            return {
                "response": "I'm here to support you. Let me know how you're feeling.",
                "therapeutic_intent": "emotional_support",
                "safety_level": "safe",
                "next_actions": [],
            }

    async def _assess_emotional_state(self, state: WorkflowState) -> WorkflowState:
        """Assess patient's emotional state from their message"""
        user_message = state["messages"][-1].content

        assessment_prompt = f"""
        Analyze the emotional state of this patient message: "{user_message}"

        Consider:
        - Emotional valence (positive/negative)
        - Arousal level (calm/excited)
        - Crisis indicators
        - Therapeutic needs

        Respond with a JSON object containing:
        - valence: float (-1.0 to 1.0)
        - arousal: float (0.0 to 1.0)
        - crisis_risk: string (low/medium/high/crisis)
        - primary_emotion: string
        - therapeutic_needs: list of strings
        """

        response = await self.llm.ainvoke([SystemMessage(content=assessment_prompt)])

        try:
            assessment = json.loads(response.content)
            state["emotional_state"] = assessment
            state["messages"].append(AIMessage(content="Emotional state assessed"))
        except json.JSONDecodeError:
            # Fallback assessment
            state["emotional_state"] = {
                "valence": 0.0,
                "arousal": 0.5,
                "crisis_risk": "low",
                "primary_emotion": "neutral",
                "therapeutic_needs": ["support"],
            }

        return state

    async def _safety_check(self, state: WorkflowState) -> WorkflowState:
        """Perform safety assessment"""
        emotional_state = state["emotional_state"]
        crisis_risk = emotional_state.get("crisis_risk", "low")

        # Enhanced safety check based on multiple factors
        safety_factors = {
            "crisis_keywords": self._check_crisis_keywords(
                state["messages"][-1].content
            ),
            "emotional_distress": emotional_state.get("valence", 0) < -0.7,
            "high_arousal": emotional_state.get("arousal", 0) > 0.8,
            "previous_interventions": len(state["intervention_history"]) > 3,
        }

        safety_level = "safe"
        if any(safety_factors.values()) or crisis_risk in ["high", "crisis"]:
            safety_level = "needs_support" if crisis_risk != "crisis" else "crisis"

        state["therapeutic_context"]["safety_level"] = safety_level
        state["messages"].append(
            AIMessage(content=f"Safety check completed: {safety_level}")
        )

        return state

    async def _generate_therapeutic_response(
        self, state: WorkflowState
    ) -> WorkflowState:
        """Generate contextual therapeutic response"""
        user_message = state["messages"][-1].content if state["messages"] else ""
        emotional_state = state["emotional_state"]
        therapeutic_context = state["therapeutic_context"]

        # Build therapeutic prompt
        therapeutic_prompt = f"""
        You are a compassionate AI therapeutic assistant. Respond to this patient message: "{user_message}"

        Patient context:
        - Emotional state: {emotional_state}
        - Current scenario: {state["current_scenario"]}
        - Therapeutic framework: {therapeutic_context.get("framework", "CBT")}
        - Safety level: {therapeutic_context.get("safety_level", "safe")}

        Guidelines:
        - Be empathetic and validating
        - Use therapeutic techniques appropriate to the framework
        - Encourage reflection and growth
        - Maintain professional boundaries
        - If crisis indicators present, prioritize safety

        Provide a supportive, therapeutic response that helps the patient process their experience.
        """

        response = await self.llm.ainvoke(
            [
                SystemMessage(content=therapeutic_prompt),
                HumanMessage(content=user_message),
            ]
        )

        state["messages"].append(response)
        return state

    async def _update_narrative_context(self, state: WorkflowState) -> WorkflowState:
        """Update the narrative context based on the interaction"""
        if state["feature_flags"].get("living_worlds_system", False):
            # Update living world context
            narrative_update = {
                "patient_choice": (
                    state["messages"][-2].content if len(state["messages"]) >= 2 else ""
                ),
                "ai_response": state["messages"][-1].content,
                "emotional_impact": state["emotional_state"],
                "timestamp": datetime.utcnow().isoformat(),
            }

            state["decision_points"].append(narrative_update)

            # Cache narrative progression
            await self.redis.setex(
                f"narrative:{state['session_id']}",
                3600,  # 1 hour TTL
                json.dumps(narrative_update),
            )

        return state

    async def _handle_crisis_intervention(self, state: WorkflowState) -> WorkflowState:
        """Handle crisis intervention workflow"""
        crisis_response = """
        I'm concerned about your safety and wellbeing. You're not alone, and help is available.

        Immediate resources:
        • National Suicide Prevention Lifeline: 988
        • Crisis Text Line: Text HOME to 741741
        • Emergency Services: 911

        Please reach out to one of these resources or a trusted person in your life.
        Would you like me to help you create a safety plan?
        """

        state["messages"].append(AIMessage(content=crisis_response))

        # Log crisis intervention
        intervention = {
            "type": "crisis_intervention",
            "timestamp": datetime.utcnow().isoformat(),
            "patient_id": state["patient_id"],
            "session_id": state["session_id"],
            "trigger": state["emotional_state"],
        }

        state["intervention_history"].append(intervention)

        return state

    def _route_based_on_emotional_state(self, state: WorkflowState) -> str:
        """Route workflow based on emotional state assessment"""
        crisis_risk = state["emotional_state"].get("crisis_risk", "low")
        valence = state["emotional_state"].get("valence", 0)

        if crisis_risk == "crisis":
            return "crisis"
        if crisis_risk == "high" or valence < -0.6:
            return "distressed"
        if valence > 0.3:
            return "engaged"
        return "stable"

    def _route_based_on_safety(self, state: WorkflowState) -> str:
        """Route workflow based on safety assessment"""
        safety_level = state["therapeutic_context"].get("safety_level", "safe")

        if safety_level == "crisis":
            return "crisis"
        if safety_level == "needs_support":
            return "needs_support"
        return "safe"

    def _check_crisis_keywords(self, message: str) -> bool:
        """Check for crisis-related keywords"""
        crisis_keywords = [
            "suicide",
            "kill myself",
            "end it all",
            "can't go on",
            "hopeless",
            "worthless",
            "better off dead",
            "hurt myself",
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in crisis_keywords)

    def _select_workflow(self, state: WorkflowState) -> str:
        """Select appropriate workflow based on state"""
        crisis_risk = state["emotional_state"].get("crisis_risk", "low")

        if crisis_risk in ["high", "crisis"]:
            return "crisis_intervention"
        if state["therapeutic_context"].get("skill_building_needed", False):
            return "skill_building"
        return "main_therapeutic"

    def _extract_workflow_response(self, result: WorkflowState) -> dict[str, Any]:
        """Extract structured response from workflow result"""
        last_ai_message = None
        for message in reversed(result["messages"]):
            if isinstance(message, AIMessage):
                last_ai_message = message
                break

        return {
            "response": (
                last_ai_message.content
                if last_ai_message
                else "I'm here to support you."
            ),
            "emotional_state": result["emotional_state"],
            "safety_level": result["therapeutic_context"].get("safety_level", "safe"),
            "interventions_triggered": result["intervention_history"],
            "decision_points": result["decision_points"],
            "next_actions": result["therapeutic_context"].get("next_actions", []),
        }

    async def _cache_workflow_result(self, session_id: str, response: dict[str, Any]):
        """Cache workflow result for quick access"""
        await self.redis.setex(
            f"workflow_result:{session_id}",
            1800,  # 30 minutes TTL
            json.dumps(response, default=str),
        )

    # Placeholder methods for additional workflow nodes
    async def _provide_skill_building(self, state: WorkflowState) -> WorkflowState:
        """Provide skill-building intervention"""
        # Implementation would include specific therapeutic techniques
        state["messages"].append(
            AIMessage(content="Let's work on building some coping skills together.")
        )
        return state

    async def _facilitate_reflection(self, state: WorkflowState) -> WorkflowState:
        """Facilitate patient reflection"""
        state["messages"].append(
            AIMessage(content="Take a moment to reflect on what we've discussed.")
        )
        return state

    # Crisis workflow methods (simplified implementations)
    async def _ensure_immediate_safety(self, state: WorkflowState) -> WorkflowState:
        state["therapeutic_context"]["safety_ensured"] = True
        return state

    async def _assess_crisis_severity(self, state: WorkflowState) -> WorkflowState:
        state["therapeutic_context"]["crisis_severity"] = "high"
        return state

    async def _activate_emergency_contacts(self, state: WorkflowState) -> WorkflowState:
        state["therapeutic_context"]["emergency_activated"] = True
        return state

    async def _provide_stabilization(self, state: WorkflowState) -> WorkflowState:
        state["therapeutic_context"]["stabilization_provided"] = True
        return state

    async def _create_follow_up_plan(self, state: WorkflowState) -> WorkflowState:
        state["therapeutic_context"]["follow_up_planned"] = True
        return state

    def _route_crisis_severity(self, state: WorkflowState) -> str:
        return "stabilizing"  # Simplified routing

    # Skill building workflow methods (simplified implementations)
    async def _identify_skill_gap(self, state: WorkflowState) -> WorkflowState:
        return state

    async def _select_therapeutic_technique(
        self, state: WorkflowState
    ) -> WorkflowState:
        return state

    async def _provide_guided_practice(self, state: WorkflowState) -> WorkflowState:
        return state

    async def _assess_skill_progress(self, state: WorkflowState) -> WorkflowState:
        return state

    async def _provide_reinforcement(self, state: WorkflowState) -> WorkflowState:
        return state


# Global instance
therapeutic_workflow_manager = TherapeuticWorkflowManager(
    openai_api_key="your-openai-api-key-here"  # Should be loaded from environment
)
