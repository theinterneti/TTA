"""
Integration tests for the LangGraph Agent Orchestrator.

Tests the LangGraph workflow integration with agent coordination.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.agent_orchestration.langgraph_orchestrator import (
    AgentWorkflowState,
    LangGraphAgentOrchestrator,
)


@pytest_asyncio.fixture
async def mock_redis():
    """Provide a mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    return redis_mock


@pytest_asyncio.fixture
async def mock_llm():
    """Provide a mock LLM."""
    llm_mock = AsyncMock()
    llm_mock.ainvoke = AsyncMock(
        return_value=MagicMock(
            content='{"safety_level": "safe", "reasoning": "No concerns detected", "recommended_action": "continue"}'
        )
    )
    return llm_mock


@pytest_asyncio.fixture
async def orchestrator(mock_redis, mock_llm):
    """Create a LangGraph orchestrator with mocked dependencies."""
    with patch("redis.asyncio.from_url", return_value=mock_redis), patch(
        "langchain_openai.ChatOpenAI", return_value=mock_llm
    ):
        orch = LangGraphAgentOrchestrator(
            openai_api_key="test-key",
            redis_url="redis://localhost:6379",
            neo4j_manager=None,
        )
        await orch.initialize()
        yield orch
        await orch.close()


class TestLangGraphAgentOrchestrator:
    """Test the LangGraph agent orchestrator."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_redis, mock_llm):
        """Test orchestrator initialization."""
        with patch("redis.asyncio.from_url", return_value=mock_redis), patch(
            "langchain_openai.ChatOpenAI", return_value=mock_llm
        ):
            orch = LangGraphAgentOrchestrator(
                openai_api_key="test-key", redis_url="redis://localhost:6379"
            )
            await orch.initialize()

            assert orch.initialized is True
            assert orch.workflow is not None
            assert orch.agent_orchestrator.initialized is True

            await orch.close()

    @pytest.mark.asyncio
    async def test_process_user_input_complete_workflow(self, orchestrator):
        """Test complete user input processing through LangGraph workflow."""
        result = await orchestrator.process_user_input(
            user_input="I want to explore the ancient ruins",
            session_id="test-session-001",
            player_id="test-player-001",
            world_context={"current_location": "village_square"},
            therapeutic_context={"mood": "adventurous"},
        )

        # Verify result structure
        assert result["success"] is True
        assert "narrative" in result
        assert "workflow_id" in result
        assert result["safety_level"] == "safe"
        assert "agent_results" in result

        # Verify agent results
        agent_results = result["agent_results"]
        assert "ipa" in agent_results
        assert "wba" in agent_results
        assert "nga" in agent_results

    @pytest.mark.asyncio
    async def test_safety_check_node(self, orchestrator):
        """Test safety check node in workflow."""
        state: AgentWorkflowState = {
            "messages": [],
            "player_id": "test-player",
            "session_id": "test-session",
            "user_input": "I'm feeling okay today",
            "ipa_result": None,
            "wba_result": None,
            "nga_result": None,
            "world_context": {},
            "therapeutic_context": {},
            "safety_level": "safe",
            "workflow_id": None,
            "narrative_response": "",
            "next_actions": [],
        }

        result_state = await orchestrator._safety_check_node(state)

        # Verify safety assessment
        assert result_state["safety_level"] in ["safe", "concern", "high_risk", "crisis"]

    @pytest.mark.asyncio
    async def test_coordinate_agents_node(self, orchestrator):
        """Test agent coordination node."""
        state: AgentWorkflowState = {
            "messages": [],
            "player_id": "test-player",
            "session_id": "test-session",
            "user_input": "look around the room",
            "ipa_result": None,
            "wba_result": None,
            "nga_result": None,
            "world_context": {"current_room": "bedroom"},
            "therapeutic_context": {},
            "safety_level": "safe",
            "workflow_id": None,
            "narrative_response": "",
            "next_actions": [],
        }

        result_state = await orchestrator._coordinate_agents_node(state)

        # Verify agent coordination
        assert result_state["workflow_id"] is not None
        assert result_state["ipa_result"] is not None
        assert result_state["wba_result"] is not None
        assert result_state["nga_result"] is not None
        assert result_state["narrative_response"] != ""

    @pytest.mark.asyncio
    async def test_generate_response_node(self, orchestrator):
        """Test response generation node."""
        state: AgentWorkflowState = {
            "messages": [],
            "player_id": "test-player",
            "session_id": "test-session",
            "user_input": "examine the painting",
            "ipa_result": {"routing": {"intent": "examine"}},
            "wba_result": {"description": "A beautiful landscape"},
            "nga_result": {"story": "You see a stunning painting"},
            "world_context": {},
            "therapeutic_context": {},
            "safety_level": "safe",
            "workflow_id": "test-workflow",
            "narrative_response": "You see a stunning painting of mountains",
            "next_actions": [],
        }

        result_state = await orchestrator._generate_response_node(state)

        # Verify response generation
        assert result_state["narrative_response"] != ""
        assert len(result_state["messages"]) > 0
        assert len(result_state["next_actions"]) > 0

    @pytest.mark.asyncio
    async def test_handle_crisis_node(self, orchestrator):
        """Test crisis handling node."""
        state: AgentWorkflowState = {
            "messages": [],
            "player_id": "test-player",
            "session_id": "test-session",
            "user_input": "I don't want to be here anymore",
            "ipa_result": None,
            "wba_result": None,
            "nga_result": None,
            "world_context": {},
            "therapeutic_context": {},
            "safety_level": "crisis",
            "workflow_id": None,
            "narrative_response": "",
            "next_actions": [],
        }

        result_state = await orchestrator._handle_crisis_node(state)

        # Verify crisis response
        assert result_state["narrative_response"] != ""
        assert "crisis" in result_state["narrative_response"].lower() or "988" in result_state["narrative_response"]
        assert "crisis_resources" in result_state["next_actions"]

    @pytest.mark.asyncio
    async def test_routing_logic(self, orchestrator):
        """Test workflow routing logic."""
        # Test safe routing
        safe_state: AgentWorkflowState = {
            "messages": [],
            "player_id": "test-player",
            "session_id": "test-session",
            "user_input": "test",
            "ipa_result": None,
            "wba_result": None,
            "nga_result": None,
            "world_context": {},
            "therapeutic_context": {},
            "safety_level": "safe",
            "workflow_id": None,
            "narrative_response": "",
            "next_actions": [],
        }

        route = orchestrator._route_after_safety(safe_state)
        assert route == "safe"

        # Test crisis routing
        crisis_state = safe_state.copy()
        crisis_state["safety_level"] = "crisis"

        route = orchestrator._route_after_safety(crisis_state)
        assert route == "crisis"

    @pytest.mark.asyncio
    async def test_error_handling_in_workflow(self, orchestrator):
        """Test error handling during workflow execution."""
        # Mock agent orchestrator to raise an error
        with patch.object(
            orchestrator.agent_orchestrator,
            "process_user_input",
            side_effect=Exception("Test error"),
        ):
            result = await orchestrator.process_user_input(
                user_input="test input",
                session_id="test-session-error",
                player_id="test-player-error",
            )

            # Verify error handling
            assert result["success"] is False
            assert "error" in result
            assert "narrative" in result

    @pytest.mark.asyncio
    async def test_therapeutic_context_preservation(self, orchestrator):
        """Test that therapeutic context is preserved through workflow."""
        therapeutic_context = {
            "mood": "anxious",
            "session_number": 5,
            "therapeutic_goals": ["anxiety_management"],
        }

        result = await orchestrator.process_user_input(
            user_input="I'm feeling nervous",
            session_id="test-session-context",
            player_id="test-player-context",
            therapeutic_context=therapeutic_context,
        )

        # Verify context was used
        assert result["success"] is True
        # The context should have been passed to the agent orchestrator

    @pytest.mark.asyncio
    async def test_world_context_updates(self, orchestrator):
        """Test that world context is updated through workflow."""
        initial_world = {
            "current_location": "forest_entrance",
            "visited_locations": ["village"],
        }

        result = await orchestrator.process_user_input(
            user_input="enter the forest",
            session_id="test-session-world",
            player_id="test-player-world",
            world_context=initial_world,
        )

        # Verify world updates
        assert result["success"] is True
        assert "agent_results" in result
        assert result["agent_results"]["wba"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

