"""
Integration tests for the Unified Agent Orchestrator.

Tests the complete IPA → WBA → NGA workflow with state persistence.
"""

import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from src.agent_orchestration.unified_orchestrator import (
    OrchestrationPhase,
    OrchestrationState,
    UnifiedAgentOrchestrator,
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
async def orchestrator(mock_redis):
    """Create an orchestrator instance with mocked dependencies."""
    with patch("redis.asyncio.from_url", return_value=mock_redis):
        orch = UnifiedAgentOrchestrator(
            redis_url="redis://localhost:6379",
            neo4j_manager=None,
            enable_real_agents=False,  # Use mock implementations
        )
        await orch.initialize()
        yield orch
        await orch.close()


class TestOrchestrationState:
    """Test OrchestrationState serialization and deserialization."""

    def test_state_to_dict(self):
        """Test converting state to dictionary."""
        state = OrchestrationState(
            workflow_id="test-workflow-123",
            session_id="session-456",
            player_id="player-789",
            phase=OrchestrationPhase.INPUT_PROCESSING,
            user_input="go north",
        )

        state_dict = state.to_dict()

        assert state_dict["workflow_id"] == "test-workflow-123"
        assert state_dict["session_id"] == "session-456"
        assert state_dict["player_id"] == "player-789"
        assert state_dict["phase"] == "input_processing"
        assert state_dict["user_input"] == "go north"

    def test_state_from_dict(self):
        """Test creating state from dictionary."""
        state_dict = {
            "workflow_id": "test-workflow-123",
            "session_id": "session-456",
            "player_id": "player-789",
            "phase": "input_processing",
            "user_input": "go north",
            "created_at": "2025-10-06T12:00:00",
            "updated_at": "2025-10-06T12:00:01",
            "ipa_result": {"intent": "move"},
            "wba_result": {"location": "north_room"},
            "nga_result": {"story": "You move north"},
            "world_context": {},
            "therapeutic_context": {},
            "safety_level": "safe",
            "error": None,
        }

        state = OrchestrationState.from_dict(state_dict)

        assert state.workflow_id == "test-workflow-123"
        assert state.phase == OrchestrationPhase.INPUT_PROCESSING
        assert state.ipa_result["intent"] == "move"


class TestUnifiedAgentOrchestrator:
    """Test the unified agent orchestrator."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_redis):
        """Test orchestrator initialization."""
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            orch = UnifiedAgentOrchestrator(redis_url="redis://localhost:6379")
            await orch.initialize()

            assert orch.initialized is True
            assert orch.redis is not None
            mock_redis.ping.assert_called_once()

            await orch.close()

    @pytest.mark.asyncio
    async def test_process_user_input_complete_workflow(self, orchestrator):
        """Test complete user input processing workflow."""
        result = await orchestrator.process_user_input(
            user_input="explore the forest",
            session_id="test-session-001",
            player_id="test-player-001",
            world_context={"current_location": "village"},
            therapeutic_context={"mood": "curious"},
        )

        # Verify result structure
        assert result["success"] is True
        assert "workflow_id" in result
        assert "narrative" in result
        assert "intent" in result
        assert result["safety_level"] == "safe"

        # Verify complete state is included
        assert "complete_state" in result
        complete_state = result["complete_state"]
        assert complete_state["phase"] == "complete"
        assert complete_state["ipa_result"] is not None
        assert complete_state["wba_result"] is not None
        assert complete_state["nga_result"] is not None

    @pytest.mark.asyncio
    async def test_process_input_phase(self, orchestrator):
        """Test input processing phase."""
        state = OrchestrationState(
            workflow_id="test-workflow",
            session_id="test-session",
            player_id="test-player",
            phase=OrchestrationPhase.INPUT_PROCESSING,
            user_input="look around",
        )

        result_state = await orchestrator._process_input_phase(state)

        # Verify phase progression
        assert result_state.phase == OrchestrationPhase.WORLD_BUILDING
        assert result_state.ipa_result is not None
        assert "routing" in result_state.ipa_result
        assert result_state.safety_level is not None

    @pytest.mark.asyncio
    async def test_process_world_building_phase(self, orchestrator):
        """Test world building phase."""
        state = OrchestrationState(
            workflow_id="test-workflow",
            session_id="test-session",
            player_id="test-player",
            phase=OrchestrationPhase.WORLD_BUILDING,
            user_input="go north",
            ipa_result={
                "routing": {
                    "intent": "move",
                    "entities": {"direction": "north"},
                }
            },
        )

        result_state = await orchestrator._process_world_building_phase(state)

        # Verify phase progression
        assert result_state.phase == OrchestrationPhase.NARRATIVE_GENERATION
        assert result_state.wba_result is not None

    @pytest.mark.asyncio
    async def test_process_narrative_phase(self, orchestrator):
        """Test narrative generation phase."""
        state = OrchestrationState(
            workflow_id="test-workflow",
            session_id="test-session",
            player_id="test-player",
            phase=OrchestrationPhase.NARRATIVE_GENERATION,
            user_input="examine the door",
            ipa_result={
                "routing": {"intent": "examine", "entities": {"object": "door"}}
            },
            wba_result={"description": "The door is old and wooden"},
        )

        result_state = await orchestrator._process_narrative_phase(state)

        # Verify narrative generation
        assert result_state.nga_result is not None
        assert "story" in result_state.nga_result

    @pytest.mark.asyncio
    async def test_safety_concern_handling(self, orchestrator):
        """Test handling of safety concerns."""
        # Mock safety service to return blocked (high risk)
        from src.agent_orchestration.therapeutic_safety import (
            SafetyLevel,
            ValidationResult,
        )

        mock_result = ValidationResult(
            level=SafetyLevel.BLOCKED,
            findings=[],
            score=0.3,
            audit=[],
            crisis_detected=True,
        )

        with patch.object(
            orchestrator.safety_service,
            "validate_text",
            return_value=mock_result,
        ):
            result = await orchestrator.process_user_input(
                user_input="I want to hurt myself",
                session_id="test-session-002",
                player_id="test-player-002",
            )

            # Verify safety intervention
            assert result["success"] is True
            assert result["safety_level"] in ["blocked", "warning"]
            assert (
                "safety_intervention" in result
                or "wellbeing" in result["narrative"].lower()
            )

    @pytest.mark.asyncio
    async def test_state_persistence(self, orchestrator, mock_redis):
        """Test state persistence to Redis."""
        state = OrchestrationState(
            workflow_id="test-workflow-persist",
            session_id="test-session-persist",
            player_id="test-player-persist",
            phase=OrchestrationPhase.COMPLETE,
            user_input="test input",
        )

        await orchestrator._save_state(state)

        # Verify Redis calls - should be called twice (workflow key and session key)
        assert mock_redis.setex.called
        assert mock_redis.setex.call_count == 2

        # Check first call (workflow key)
        first_call_args = mock_redis.setex.call_args_list[0][0]
        assert "orchestration:workflow:test-workflow-persist" in first_call_args[0]

        # Check second call (session key)
        second_call_args = mock_redis.setex.call_args_list[1][0]
        assert (
            "orchestration:session:test-session-persist:latest" in second_call_args[0]
        )

    @pytest.mark.asyncio
    async def test_get_workflow_state(self, orchestrator, mock_redis):
        """Test retrieving workflow state from Redis."""
        # Mock Redis to return a state
        test_state = OrchestrationState(
            workflow_id="test-workflow-retrieve",
            session_id="test-session",
            player_id="test-player",
            phase=OrchestrationPhase.COMPLETE,
            user_input="test",
        )

        mock_redis.get = AsyncMock(return_value=json.dumps(test_state.to_dict()))

        retrieved_state = await orchestrator.get_workflow_state(
            "test-workflow-retrieve"
        )

        assert retrieved_state is not None
        assert retrieved_state.workflow_id == "test-workflow-retrieve"
        assert retrieved_state.phase == OrchestrationPhase.COMPLETE

    @pytest.mark.asyncio
    async def test_error_handling(self, orchestrator):
        """Test error handling in workflow."""
        # Force an error by providing invalid input
        with patch.object(
            orchestrator.ipa_adapter,
            "process_input",
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
            assert "narrative" in result  # Should have fallback narrative

    @pytest.mark.asyncio
    async def test_concurrent_workflows(self, orchestrator):
        """Test handling multiple concurrent workflows."""
        # Create multiple workflows concurrently
        tasks = [
            orchestrator.process_user_input(
                user_input=f"test input {i}",
                session_id=f"session-{i}",
                player_id=f"player-{i}",
            )
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks)

        # Verify all workflows completed
        assert len(results) == 5
        for result in results:
            assert result["success"] is True
            assert "workflow_id" in result

        # Verify unique workflow IDs
        workflow_ids = [r["workflow_id"] for r in results]
        assert len(set(workflow_ids)) == 5  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
