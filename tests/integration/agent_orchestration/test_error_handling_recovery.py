"""

# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_error_handling_recovery]]
Error handling and recovery integration tests for multi-agent workflows.

This module implements comprehensive tests for error scenarios, failover mechanisms,
and recovery patterns in the agent orchestration system.
"""

import asyncio
import time
from unittest.mock import patch

import pytest
import pytest_asyncio
from tta_ai.orchestration import (
    AgentStep,
    AgentType,
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    OrchestrationRequest,
    WorkflowDefinition,
    WorkflowManager,
    WorkflowType,
    WorldBuilderAgentProxy,
)

from tests.agent_orchestration.test_multi_agent_workflow_integration import (
    IntegrationTestHelper,
)

# ============================================================================
# Error Handling and Recovery Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.redis
@pytest.mark.neo4j
class TestAgentFailureScenarios:
    """Test agent unavailability and failover mechanisms."""

    @pytest_asyncio.fixture
    async def integration_helper(self, redis_client, neo4j_driver):
        """Create integration test helper."""
        return IntegrationTestHelper(redis_client, neo4j_driver)

    async def test_agent_unavailability_failover(
        self, integration_helper, workflow_error_scenarios, sample_player_inputs
    ):
        """Test failover when an agent becomes unavailable."""
        test_env = await integration_helper.setup_test_environment("agent_failover")

        try:
            # Create workflow manager
            workflow_manager = WorkflowManager()

            # Register workflow with failover configuration
            workflow_def = WorkflowDefinition(
                workflow_type=WorkflowType.COLLABORATIVE,
                agent_sequence=[
                    AgentStep(
                        agent=AgentType.IPA, name="input_processing", timeout_seconds=5
                    ),
                    AgentStep(
                        agent=AgentType.WBA, name="world_building", timeout_seconds=5
                    ),
                    AgentStep(
                        agent=AgentType.NGA,
                        name="narrative_generation",
                        timeout_seconds=5,
                    ),
                ],
                error_handling="retry",  # Enable retry on failure
            )

            workflow_manager.register_workflow("failover_test", workflow_def)

            # Simulate WBA unavailability
            wba_agent_id = "WBA:test"
            await integration_helper.simulate_agent_failure(
                wba_agent_id, failure_duration=3.0
            )

            # Execute workflow during failure
            request = OrchestrationRequest(
                entrypoint=AgentType.IPA, input=sample_player_inputs[0]
            )

            start_time = time.time()
            response, run_id, error = workflow_manager.execute_workflow(
                "failover_test", request
            )
            execution_time = time.time() - start_time

            # Verify failover behavior
            if error is not None:
                # If workflow failed, verify it was due to agent unavailability
                assert (
                    "unavailable" in str(error).lower()
                    or "timeout" in str(error).lower()
                ), f"Unexpected error type: {error}"

                # Verify retry was attempted (execution should take longer than normal)
                assert execution_time > 3.0, "Retry mechanism not triggered"
            else:
                # If workflow succeeded, verify it used fallback mechanisms
                assert response is not None, "No response despite success"

                # Check if fallback strategies were used
                metadata = response.workflow_metadata
                assert (
                    "fallback" in str(metadata).lower()
                    or "retry" in str(metadata).lower()
                ), "Fallback mechanisms not indicated in metadata"

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )

    async def test_circuit_breaker_pattern(
        self, integration_helper, sample_player_inputs
    ):
        """Test circuit breaker pattern for failing agents."""
        test_env = await integration_helper.setup_test_environment("circuit_breaker")

        try:
            # Track failure counts
            failure_count = 0
            circuit_opened = False

            class FailingAgent(WorldBuilderAgentProxy):
                async def process(self, input_payload: dict) -> dict:
                    nonlocal failure_count, circuit_opened
                    failure_count += 1

                    # Simulate consistent failures
                    if failure_count < 5:
                        raise Exception(f"Simulated failure #{failure_count}")

                    # After 5 failures, circuit should be open
                    if failure_count >= 5:
                        circuit_opened = True
                        raise Exception("Circuit breaker opened - agent unavailable")

            # Create workflow with failing agent
            workflow_manager = WorkflowManager()

            # Mock agent registry to return failing agent
            with patch(
                "src.agent_orchestration.agents.AgentRegistry.get_agent"
            ) as mock_get_agent:
                failing_wba = FailingAgent(instance="failing")
                mock_get_agent.return_value = failing_wba

                workflow_def = WorkflowDefinition(
                    workflow_type=WorkflowType.COLLABORATIVE,
                    agent_sequence=[
                        AgentStep(agent=AgentType.IPA, name="input_processing"),
                        AgentStep(agent=AgentType.WBA, name="failing_world_building"),
                        AgentStep(agent=AgentType.NGA, name="narrative_generation"),
                    ],
                )

                workflow_manager.register_workflow("circuit_test", workflow_def)

                # Execute multiple workflows to trigger circuit breaker
                for i in range(6):
                    request = OrchestrationRequest(
                        entrypoint=AgentType.IPA, input=sample_player_inputs[0]
                    )

                    response, run_id, error = workflow_manager.execute_workflow(
                        "circuit_test", request
                    )

                    # All should fail, but behavior should change after circuit opens
                    assert error is not None, f"Expected failure on attempt {i + 1}"

                    if i >= 4:  # After 5 failures, circuit should be open
                        assert circuit_opened, "Circuit breaker should be open"
                        assert (
                            "circuit" in str(error).lower()
                            or "unavailable" in str(error).lower()
                        ), "Error should indicate circuit breaker state"

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )


@pytest.mark.integration
@pytest.mark.redis
class TestNetworkFailureScenarios:
    """Test network communication failure handling."""

    async def test_redis_connection_failure(
        self, integration_helper, sample_player_inputs
    ):
        """Test handling of Redis connection failures."""
        test_env = await integration_helper.setup_test_environment("redis_failure")

        try:
            # Create workflow manager
            workflow_manager = WorkflowManager()

            workflow_def = WorkflowDefinition(
                workflow_type=WorkflowType.COLLABORATIVE,
                agent_sequence=[
                    AgentStep(agent=AgentType.IPA, name="input_processing"),
                    AgentStep(agent=AgentType.WBA, name="world_building"),
                    AgentStep(agent=AgentType.NGA, name="narrative_generation"),
                ],
            )

            workflow_manager.register_workflow("redis_failure_test", workflow_def)

            # Mock Redis connection failure
            with patch(
                "src.agent_orchestration.coordinators.redis_message_coordinator.RedisMessageCoordinator.send_message"
            ) as mock_send:
                # Simulate connection failure
                mock_send.side_effect = ConnectionError("Redis connection lost")

                request = OrchestrationRequest(
                    entrypoint=AgentType.IPA, input=sample_player_inputs[0]
                )

                response, run_id, error = workflow_manager.execute_workflow(
                    "redis_failure_test", request
                )

                # Verify graceful handling of Redis failure
                if error is not None:
                    assert (
                        "connection" in str(error).lower()
                        or "redis" in str(error).lower()
                    ), f"Error should indicate connection issue: {error}"
                else:
                    # If workflow succeeded, verify fallback was used
                    assert response is not None, (
                        "Response should exist if workflow succeeded"
                    )
                    metadata = response.workflow_metadata
                    assert (
                        "fallback" in str(metadata).lower()
                        or "degraded" in str(metadata).lower()
                    ), "Metadata should indicate fallback mode"

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )

    async def test_neo4j_write_failure_recovery(
        self, integration_helper, sample_player_inputs
    ):
        """Test recovery from Neo4j write failures."""
        test_env = await integration_helper.setup_test_environment("neo4j_failure")

        try:
            # Mock Neo4j write failure
            write_attempts = 0

            def mock_neo4j_write(*args, **kwargs):
                nonlocal write_attempts
                write_attempts += 1

                # Fail first two attempts, succeed on third
                if write_attempts <= 2:
                    raise Exception(f"Neo4j write failure #{write_attempts}")
                return True

            with patch(
                "src.components.neo4j_manager.Neo4jManager.execute_write"
            ) as mock_write:
                mock_write.side_effect = mock_neo4j_write

                workflow_manager = WorkflowManager()

                workflow_def = WorkflowDefinition(
                    workflow_type=WorkflowType.COLLABORATIVE,
                    agent_sequence=[
                        AgentStep(agent=AgentType.IPA, name="input_processing"),
                        AgentStep(agent=AgentType.WBA, name="world_building"),
                        AgentStep(agent=AgentType.NGA, name="narrative_generation"),
                    ],
                )

                workflow_manager.register_workflow("neo4j_failure_test", workflow_def)

                request = OrchestrationRequest(
                    entrypoint=AgentType.IPA, input=sample_player_inputs[0]
                )

                response, run_id, error = workflow_manager.execute_workflow(
                    "neo4j_failure_test", request
                )

                # Verify retry mechanism worked
                assert write_attempts >= 2, "Retry mechanism should have been triggered"

                if error is None:
                    # If successful, verify eventual consistency
                    assert response is not None, "Response should exist on success"
                    assert write_attempts == 3, "Should have succeeded on third attempt"
                else:
                    # If failed, verify appropriate error handling
                    assert (
                        "neo4j" in str(error).lower()
                        or "database" in str(error).lower()
                    ), f"Error should indicate database issue: {error}"

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )


@pytest.mark.integration
@pytest.mark.redis
class TestMessageValidationFailures:
    """Test handling of invalid message formats and validation failures."""

    async def test_invalid_message_format_handling(
        self, integration_helper, redis_client
    ):
        """Test handling of malformed messages."""
        test_env = await integration_helper.setup_test_environment("invalid_message")

        try:
            from tta_ai.orchestration import AgentId, AgentType
            from tta_ai.orchestration.coordinators.redis_message_coordinator import (
                RedisMessageCoordinator,
            )

            coordinator = RedisMessageCoordinator(redis_client)
            agent_id = AgentId(type=AgentType.NGA, instance="test")

            # Inject malformed message directly into Redis queue
            queue_key = f"agent_queue:{agent_id.type.value}:{agent_id.instance}"
            malformed_messages = [
                '{"invalid": "json"',  # Invalid JSON
                '{"missing_required_fields": true}',  # Missing required fields
                "not_json_at_all",  # Not JSON
                '{"sender_id": "invalid_format", "payload": null}',  # Invalid field formats
            ]

            for msg in malformed_messages:
                await redis_client.lpush(queue_key, msg)

            # Try to receive messages - should handle malformed ones gracefully
            valid_messages_received = 0
            errors_handled = 0

            for _ in range(len(malformed_messages)):
                try:
                    received = await coordinator.receive_message(
                        agent_id, timeout_seconds=1.0
                    )
                    if received is not None:
                        valid_messages_received += 1
                except Exception as e:
                    errors_handled += 1
                    # Verify error is handled appropriately
                    assert (
                        "format" in str(e).lower()
                        or "validation" in str(e).lower()
                        or "json" in str(e).lower()
                    ), f"Unexpected error type for malformed message: {e}"

            # Verify system handled malformed messages without crashing
            assert errors_handled > 0, (
                "Should have encountered errors with malformed messages"
            )

            # Verify queue is cleaned up (malformed messages removed or handled)
            final_queue_length = await redis_client.llen(queue_key)
            assert final_queue_length == 0, (
                "Queue should be cleaned of malformed messages"
            )

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )


# ============================================================================
# Timeout Handling Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.redis
class TestTimeoutHandlingScenarios:
    """Test timeout handling for agent communication."""

    async def test_agent_timeout_and_recovery(
        self, integration_helper, sample_player_inputs
    ):
        """Test timeout handling and recovery for slow agents."""
        test_env = await integration_helper.setup_test_environment("timeout_recovery")

        try:
            # Create slow agent that exceeds timeout
            class SlowAgent(WorldBuilderAgentProxy):
                def __init__(self, delay_seconds=10.0, **kwargs):
                    super().__init__(**kwargs)
                    self.delay_seconds = delay_seconds

                async def process(self, input_payload: dict) -> dict:
                    # Simulate slow processing
                    await asyncio.sleep(self.delay_seconds)
                    return await super().process(input_payload)

            workflow_manager = WorkflowManager()

            # Create workflow with short timeout
            workflow_def = WorkflowDefinition(
                workflow_type=WorkflowType.COLLABORATIVE,
                agent_sequence=[
                    AgentStep(agent=AgentType.IPA, name="fast_ipa", timeout_seconds=5),
                    AgentStep(
                        agent=AgentType.WBA, name="slow_wba", timeout_seconds=3
                    ),  # Will timeout
                    AgentStep(agent=AgentType.NGA, name="fast_nga", timeout_seconds=5),
                ],
                error_handling="retry",
            )

            workflow_manager.register_workflow("timeout_test", workflow_def)

            # Mock agent registry to return slow agent
            with patch(
                "src.agent_orchestration.agents.AgentRegistry.get_agent"
            ) as mock_get_agent:

                def get_agent(agent_id):
                    if agent_id.type == AgentType.WBA:
                        return SlowAgent(delay_seconds=5.0, instance="slow")
                    if agent_id.type == AgentType.IPA:
                        return InputProcessorAgentProxy(instance="fast")
                    if agent_id.type == AgentType.NGA:
                        return NarrativeGeneratorAgentProxy(instance="fast")
                    return None

                mock_get_agent.side_effect = get_agent

                # Execute workflow - should timeout on WBA
                request = OrchestrationRequest(
                    entrypoint=AgentType.IPA, input=sample_player_inputs[0]
                )

                start_time = time.time()
                response, run_id, error = workflow_manager.execute_workflow(
                    "timeout_test", request
                )
                execution_time = time.time() - start_time

                # Verify timeout behavior
                if error is not None:
                    # Should timeout and fail
                    assert "timeout" in str(error).lower(), (
                        f"Expected timeout error, got: {error}"
                    )
                    assert execution_time < 10.0, (
                        "Should have timed out before slow agent completed"
                    )
                    assert execution_time >= 3.0, (
                        "Should have waited for timeout period"
                    )
                else:
                    # If succeeded, should have used recovery mechanism
                    assert response is not None, (
                        "Response should exist if workflow succeeded"
                    )
                    metadata = response.workflow_metadata
                    assert (
                        "timeout" in str(metadata).lower()
                        or "recovery" in str(metadata).lower()
                    ), "Metadata should indicate timeout recovery"

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )
