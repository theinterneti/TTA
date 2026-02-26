"""

# Logseq: [[TTA.dev/Agent_orchestration/Langgraph_orchestrator]]
LangGraph-integrated Agent Orchestrator.

This module integrates the unified agent orchestrator with LangGraph workflows
for therapeutic conversation management.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, TypedDict, cast

import redis.asyncio as aioredis
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import SecretStr
from tta_ai.prompts import PromptRegistry

from .unified_orchestrator import UnifiedAgentOrchestrator

logger = logging.getLogger(__name__)


class AgentWorkflowState(TypedDict):
    """State structure for agent-integrated LangGraph workflows."""

    messages: list[BaseMessage]
    player_id: str
    session_id: str
    user_input: str

    # Agent results
    ipa_result: dict[str, Any] | None
    wba_result: dict[str, Any] | None
    nga_result: dict[str, Any] | None

    # Context
    world_context: dict[str, Any]
    therapeutic_context: dict[str, Any]
    safety_level: str
    workflow_id: str | None

    # Output
    narrative_response: str
    next_actions: list[str]


class LangGraphAgentOrchestrator:
    """
    LangGraph-integrated orchestrator for therapeutic agent workflows.

    This orchestrator combines:
    - LangGraph workflow management
    - Unified agent coordination (IPA/WBA/NGA)
    - Therapeutic safety validation
    - State persistence
    """

    def __init__(
        self,
        openai_api_key: str,
        redis_url: str = "redis://localhost:6379",
        neo4j_manager: Any | None = None,
        model_name: str = "gpt-4-turbo-preview",
    ):
        """
        Initialize the LangGraph agent orchestrator.

        Args:
            openai_api_key: OpenAI API key for LLM
            redis_url: Redis connection URL
            neo4j_manager: Neo4j manager for world state
            model_name: OpenAI model name
        """
        self.openai_api_key = openai_api_key
        self.redis_url = redis_url
        self.neo4j_manager = neo4j_manager
        self.model_name = model_name

        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=SecretStr(openai_api_key), model=model_name, temperature=0.7, max_completion_tokens=1000
        )

        # Initialize unified orchestrator
        self.agent_orchestrator = UnifiedAgentOrchestrator(
            redis_url=redis_url,
            neo4j_manager=neo4j_manager,
            enable_real_agents=True,
        )

        # Redis for caching
        self.redis: aioredis.Redis | None = None

        # Workflows (compiled graph; StateGraph.compile() returns a CompiledStateGraph)
        self.workflow: Any = None
        self.initialized = False

        # Initialize prompt registry
        self.prompt_registry = PromptRegistry()

    async def initialize(self):
        """Initialize the orchestrator and create workflows."""
        try:
            # Initialize agent orchestrator
            await self.agent_orchestrator.initialize()

            # Connect to Redis
            self.redis = aioredis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()  # type: ignore[misc]

            # Create workflow
            await self._create_agent_workflow()

            self.initialized = True
            logger.info("LangGraph Agent Orchestrator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize LangGraph orchestrator: {e}")
            raise

    async def close(self):
        """Close connections and cleanup."""
        await self.agent_orchestrator.close()
        if self.redis:
            await self.redis.close()

    async def _create_agent_workflow(self):
        """Create the main agent coordination workflow."""
        workflow = StateGraph(AgentWorkflowState)

        # Add nodes for each phase
        workflow.add_node("process_input", self._process_input_node)
        workflow.add_node("safety_check", self._safety_check_node)
        workflow.add_node("coordinate_agents", self._coordinate_agents_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("handle_crisis", self._handle_crisis_node)

        # Define edges with conditions
        workflow.add_conditional_edges(
            "process_input",
            self._route_after_input,
            {
                "safety_check": "safety_check",
                "coordinate_agents": "coordinate_agents",
            },
        )

        workflow.add_conditional_edges(
            "safety_check",
            self._route_after_safety,
            {
                "crisis": "handle_crisis",
                "safe": "coordinate_agents",
            },
        )

        workflow.add_edge("coordinate_agents", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("handle_crisis", END)

        # Set entry point
        workflow.set_entry_point("process_input")

        # Compile workflow
        self.workflow = workflow.compile()

    async def process_user_input(
        self,
        user_input: str,
        session_id: str,
        player_id: str,
        world_context: dict[str, Any] | None = None,
        therapeutic_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process user input through the complete workflow.

        Args:
            user_input: User's input text
            session_id: Session identifier
            player_id: Player identifier
            world_context: Current world state
            therapeutic_context: Therapeutic session context

        Returns:
            Dict containing narrative response and metadata
        """
        if not self.initialized:
            await self.initialize()

        # Create initial state
        initial_state: AgentWorkflowState = {
            "messages": [HumanMessage(content=user_input)],
            "player_id": player_id,
            "session_id": session_id,
            "user_input": user_input,
            "ipa_result": None,
            "wba_result": None,
            "nga_result": None,
            "world_context": world_context or {},
            "therapeutic_context": therapeutic_context or {},
            "safety_level": "safe",
            "workflow_id": None,
            "narrative_response": "",
            "next_actions": [],
        }

        try:
            # Execute workflow
            result = await self.workflow.ainvoke(initial_state)

            # Extract and return response
            return {
                "success": True,
                "narrative": result["narrative_response"],
                "workflow_id": result.get("workflow_id"),
                "safety_level": result["safety_level"],
                "next_actions": result["next_actions"],
                "agent_results": {
                    "ipa": result.get("ipa_result"),
                    "wba": result.get("wba_result"),
                    "nga": result.get("nga_result"),
                },
            }

        except Exception as e:
            logger.error(f"Workflow execution error: {e}", exc_info=True)
            return {
                "success": False,
                "narrative": "I'm having trouble processing that. Could you try again?",
                "error": str(e),
                "safety_level": "safe",
            }

    async def _process_input_node(
        self, state: AgentWorkflowState
    ) -> AgentWorkflowState:
        """Process input and perform initial validation."""
        logger.info(f"Processing input for session {state['session_id']}")

        # Add processing message
        state["messages"].append(AIMessage(content="Processing your input..."))

        return state

    async def _safety_check_node(self, state: AgentWorkflowState) -> AgentWorkflowState:
        """Perform safety validation using versioned prompts."""
        logger.info(f"Performing safety check for session {state['session_id']}")

        # Use prompt registry for safety assessment
        start_time = time.time()
        try:
            safety_prompt = self.prompt_registry.render_prompt(
                "safety_check", user_input=state["user_input"]
            )

            response = await self.llm.ainvoke([SystemMessage(content=safety_prompt)])
            latency_ms = (time.time() - start_time) * 1000
            response_text = cast(str, response.content)

            # Parse response
            assessment = json.loads(response_text)
            state["safety_level"] = assessment["safety_level"]

            # Record metrics
            self.prompt_registry.record_metrics(
                "safety_check",
                tokens=len(response_text.split()),  # Approximate
                latency_ms=latency_ms,
                cost_usd=0.0002,  # Approximate based on model
                quality_score=8.5
                if assessment["safety_level"] in ["safe", "concern"]
                else 7.0,
            )

        except Exception as e:
            logger.error(f"Safety check error: {e}")
            state["safety_level"] = "safe"  # Default to safe on error

            # Record error
            self.prompt_registry.record_metrics(
                "safety_check",
                tokens=0,
                latency_ms=(time.time() - start_time) * 1000,
                cost_usd=0.0,
                error=True,
            )

        return state

    async def _coordinate_agents_node(
        self, state: AgentWorkflowState
    ) -> AgentWorkflowState:
        """Coordinate IPA, WBA, and NGA agents."""
        logger.info(f"Coordinating agents for session {state['session_id']}")

        try:
            # Use unified orchestrator for agent coordination
            result = await self.agent_orchestrator.process_user_input(
                user_input=state["user_input"],
                session_id=state["session_id"],
                player_id=state["player_id"],
                world_context=state["world_context"],
                therapeutic_context=state["therapeutic_context"],
            )

            # Update state with agent results
            state["workflow_id"] = result["workflow_id"]
            state["ipa_result"] = result["complete_state"]["ipa_result"]
            state["wba_result"] = result["complete_state"]["wba_result"]
            state["nga_result"] = result["complete_state"]["nga_result"]
            state["narrative_response"] = result["narrative"]
            state["safety_level"] = result["safety_level"]

        except Exception as e:
            logger.error(f"Agent coordination error: {e}")
            state["narrative_response"] = (
                "I'm having trouble coordinating a response. Let's try again."
            )

        return state

    async def _generate_response_node(
        self, state: AgentWorkflowState
    ) -> AgentWorkflowState:
        """Generate final response with therapeutic framing."""
        logger.info(f"Generating response for session {state['session_id']}")

        # If we already have a narrative from agents, use it
        if state["narrative_response"]:
            state["messages"].append(AIMessage(content=state["narrative_response"]))
            state["next_actions"] = ["continue", "reflect", "explore"]
            return state

        # Fallback: generate response using LLM with versioned prompts
        start_time = time.time()
        try:
            # Prepare context
            ipa_result = state["ipa_result"] or {}
            intent = ipa_result.get("routing", {}).get("intent", "unknown")
            world_context = json.dumps(state["world_context"], indent=2)[:200]

            # Use prompt registry for narrative generation
            response_prompt = self.prompt_registry.render_prompt(
                "narrative_generation",
                user_input=state["user_input"],
                intent=intent,
                world_context=world_context,
            )

            response = await self.llm.ainvoke([SystemMessage(content=response_prompt)])
            latency_ms = (time.time() - start_time) * 1000
            response_text2 = cast(str, response.content)

            state["narrative_response"] = response_text2
            state["messages"].append(AIMessage(content=response_text2))
            state["next_actions"] = ["continue", "reflect"]

            # Record metrics
            self.prompt_registry.record_metrics(
                "narrative_generation",
                tokens=len(response_text2.split()),  # Approximate
                latency_ms=latency_ms,
                cost_usd=0.0005,  # Approximate based on model
                quality_score=8.0,  # Default quality score
            )

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            state["narrative_response"] = (
                "Thank you for sharing. How would you like to proceed?"
            )
            state["messages"].append(AIMessage(content=state["narrative_response"]))

            # Record error
            self.prompt_registry.record_metrics(
                "narrative_generation",
                tokens=0,
                latency_ms=(time.time() - start_time) * 1000,
                cost_usd=0.0,
                error=True,
            )

        return state

    async def _handle_crisis_node(
        self, state: AgentWorkflowState
    ) -> AgentWorkflowState:
        """Handle crisis situations with appropriate interventions."""
        logger.warning(f"Crisis intervention for session {state['session_id']}")

        crisis_response = """
        I notice you might be going through a very difficult time right now.
        Your wellbeing is the most important thing.

        If you're in immediate danger, please:
        - Call 988 (Suicide & Crisis Lifeline) in the US
        - Text "HELLO" to 741741 (Crisis Text Line)
        - Go to your nearest emergency room

        I'm here to support you. Would you like to talk about what's happening?
        """

        state["narrative_response"] = crisis_response
        state["messages"].append(AIMessage(content=crisis_response))
        state["next_actions"] = ["crisis_resources", "talk", "pause"]

        return state

    def _route_after_input(self, state: AgentWorkflowState) -> str:
        """Route after input processing."""
        # Always perform safety check first
        return "safety_check"

    def _route_after_safety(self, state: AgentWorkflowState) -> str:
        """Route based on safety assessment."""
        safety_level = state["safety_level"]

        if safety_level in ["crisis", "high_risk"]:
            return "crisis"
        return "safe"
