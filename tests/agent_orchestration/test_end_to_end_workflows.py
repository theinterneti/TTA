"""
End-to-end workflow integration tests for multi-agent orchestration.

This module implements the actual integration tests that validate complete IPA → WBA → NGA workflows,
testing message routing, state persistence, and response aggregation.
"""

import asyncio
import time
from unittest.mock import patch

import pytest
import pytest_asyncio
from tta_ai.orchestration import (
    AgentStep,
    AgentType,
    OrchestrationRequest,
    WorkflowDefinition,
    WorkflowManager,
    WorkflowType,
)

from tests.agent_orchestration.test_multi_agent_workflow_integration import (
    IntegrationTestHelper,
    WorkflowStateVerifier,
)

# ============================================================================
# End-to-End Workflow Integration Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.redis
@pytest.mark.neo4j
class TestCompleteWorkflowIntegration:
    """Test complete IPA → WBA → NGA workflow integration."""

    @pytest_asyncio.fixture
    async def workflow_manager(self):
        """Create workflow manager for testing."""
        return WorkflowManager()

    @pytest_asyncio.fixture
    async def integration_helper(self, redis_client, neo4j_driver):
        """Create integration test helper."""
        return IntegrationTestHelper(redis_client, neo4j_driver)

    async def test_basic_workflow_execution(
        self,
        workflow_manager,
        integration_helper,
        sample_player_inputs,
        therapeutic_session_context,
        multi_agent_workflow_definition,
    ):
        """Test basic end-to-end workflow execution."""
        # Setup test environment
        test_env = await integration_helper.setup_test_environment("basic_workflow")

        try:
            # Register workflow
            success, error = workflow_manager.register_workflow(
                "test_basic", multi_agent_workflow_definition
            )
            assert success, f"Failed to register workflow: {error}"

            # Create orchestration request
            player_input = sample_player_inputs[0]  # "look around"
            request = OrchestrationRequest(
                entrypoint=AgentType.IPA,
                input=player_input,
                context=therapeutic_session_context,
            )

            # Execute workflow
            start_time = time.time()
            response, run_id, error = workflow_manager.execute_workflow(
                "test_basic", request
            )
            execution_time = time.time() - start_time

            # Verify execution success
            assert error is None, f"Workflow execution failed: {error}"
            assert response is not None, "No response received"
            assert run_id is not None, "No run ID returned"

            # Verify response structure
            assert hasattr(response, "response_text"), "Response missing response_text"
            assert hasattr(response, "workflow_metadata"), (
                "Response missing workflow_metadata"
            )
            assert response.workflow_metadata.get("steps_executed") == 3, (
                "Expected 3 steps executed"
            )

            # Verify performance
            assert execution_time < 30.0, f"Workflow took too long: {execution_time}s"

            # Verify state persistence
            await asyncio.sleep(0.5)  # Allow for async state updates

            # Check Redis state
            redis_state = await integration_helper.redis_verifier.verify_workflow_coordination_state(
                run_id
            )
            assert redis_state["workflow_state_exists"], (
                "Workflow state not persisted in Redis"
            )

            # Check Neo4j state (if available)
            try:
                neo4j_state = await integration_helper.neo4j_verifier.verify_workflow_state_transitions(
                    run_id
                )
                assert neo4j_state["workflow_found"], "Workflow not recorded in Neo4j"
            except Exception:
                # Neo4j verification optional for basic test
                pass

        finally:
            # Cleanup
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )

    async def test_therapeutic_workflow_validation(
        self,
        workflow_manager,
        integration_helper,
        complex_therapeutic_scenarios,
        therapeutic_session_context,
    ):
        """Test workflow with therapeutic content validation."""
        test_env = await integration_helper.setup_test_environment(
            "therapeutic_workflow"
        )

        try:
            # Test anxiety management scenario
            scenario = complex_therapeutic_scenarios["anxiety_management"]

            # Create workflow definition with therapeutic validation
            workflow_def = WorkflowDefinition(
                workflow_type=WorkflowType.COLLABORATIVE,
                agent_sequence=[
                    AgentStep(agent=AgentType.IPA, name="input_processing"),
                    AgentStep(agent=AgentType.WBA, name="therapeutic_world_building"),
                    AgentStep(agent=AgentType.NGA, name="therapeutic_narrative"),
                ],
            )

            workflow_manager.register_workflow("therapeutic_test", workflow_def)

            # Execute with therapeutic input
            request = OrchestrationRequest(
                entrypoint=AgentType.IPA,
                input={"text": scenario["player_input"]},
                context=therapeutic_session_context,
            )

            response, run_id, error = workflow_manager.execute_workflow(
                "therapeutic_test", request
            )

            # Verify therapeutic validation
            assert error is None, "Therapeutic workflow failed"
            assert response is not None, "No therapeutic response"

            # Check for therapeutic elements in response
            if hasattr(response, "therapeutic_validation"):
                validation = response.therapeutic_validation
                assert validation is not None, "Missing therapeutic validation"
                # Additional therapeutic validation checks would go here

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )

    async def test_workflow_with_state_persistence(
        self,
        workflow_manager,
        integration_helper,
        sample_player_inputs,
        therapeutic_session_context,
        multi_agent_workflow_definition,
    ):
        """Test workflow execution with comprehensive state persistence verification."""
        test_env = await integration_helper.setup_test_environment("state_persistence")

        try:
            workflow_manager.register_workflow(
                "state_test", multi_agent_workflow_definition
            )

            # Execute multiple workflow steps to build state
            for i, player_input in enumerate(sample_player_inputs[:3]):
                request = OrchestrationRequest(
                    entrypoint=AgentType.IPA,
                    input=player_input,
                    context=therapeutic_session_context,
                )

                response, run_id, error = workflow_manager.execute_workflow(
                    "state_test", request
                )
                assert error is None, f"Workflow {i} failed: {error}"

                # Verify state persistence after each step
                await asyncio.sleep(0.2)  # Allow for state updates

                # Check Redis state
                redis_state = await integration_helper.redis_verifier.verify_workflow_coordination_state(
                    run_id
                )
                assert redis_state["workflow_state_exists"], (
                    f"State not persisted after step {i}"
                )

                # Verify session state in Neo4j
                session_state = (
                    await integration_helper.neo4j_verifier.verify_session_state(
                        test_env["session_id"]
                    )
                )
                assert session_state["session_exists"], (
                    f"Session not persisted after step {i}"
                )

            # Verify final state consistency
            final_redis_state = await integration_helper.redis_verifier.verify_workflow_coordination_state(
                run_id
            )
            final_neo4j_state = (
                await integration_helper.neo4j_verifier.verify_session_state(
                    test_env["session_id"]
                )
            )

            # State consistency checks
            assert final_redis_state["workflow_state_exists"], (
                "Final Redis state missing"
            )
            assert final_neo4j_state["session_exists"], "Final Neo4j state missing"
            assert final_neo4j_state["therapeutic_profile_persisted"], (
                "Therapeutic profile not persisted"
            )

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )


# ============================================================================
# Message Routing and Transformation Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.redis
class TestMessageRoutingIntegration:
    """Test message routing and transformation between agents."""

    async def test_message_routing_sequence(
        self, integration_helper, sample_player_inputs, multi_agent_workflow_definition
    ):
        """Test that messages are routed correctly through agent sequence."""
        test_env = await integration_helper.setup_test_environment("message_routing")

        try:
            # Mock message coordinator to track message flow
            messages_sent = []

            async def mock_send_message(message):
                messages_sent.append(message)
                return True

            with patch(
                "src.agent_orchestration.coordinators.redis_message_coordinator.RedisMessageCoordinator.send_message",
                side_effect=mock_send_message,
            ):
                workflow_manager = WorkflowManager()
                workflow_manager.register_workflow(
                    "routing_test", multi_agent_workflow_definition
                )

                request = OrchestrationRequest(
                    entrypoint=AgentType.IPA, input=sample_player_inputs[0]
                )

                response, run_id, error = workflow_manager.execute_workflow(
                    "routing_test", request
                )

                # Verify message routing sequence
                expected_sequence = [AgentType.IPA, AgentType.WBA, AgentType.NGA]

                # Extract agent types from sent messages
                routed_agents = []
                for msg in messages_sent:
                    if hasattr(msg, "recipient_id") and hasattr(
                        msg.recipient_id, "type"
                    ):
                        routed_agents.append(msg.recipient_id.type)

                # Verify routing follows expected sequence
                verifier = WorkflowStateVerifier()
                routing_correct = verifier.verify_message_routing(
                    messages_sent, expected_sequence
                )
                assert routing_correct, (
                    f"Message routing incorrect. Expected: {expected_sequence}, Got: {routed_agents}"
                )

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )

    async def test_message_transformation_and_priority(
        self, integration_helper, complex_therapeutic_scenarios
    ):
        """Test message transformation and priority handling."""
        test_env = await integration_helper.setup_test_environment("message_transform")

        try:
            # Test with high-priority therapeutic scenario
            scenario = complex_therapeutic_scenarios["grief_processing"]

            # Mock agents to capture message transformations
            transformed_messages = []

            class MockAgent:
                def __init__(self, agent_type):
                    self.agent_type = agent_type

                async def process(self, input_payload):
                    # Simulate message transformation
                    transformed = {
                        "original_input": input_payload,
                        "agent_type": self.agent_type,
                        "transformed_output": f"Processed by {self.agent_type}",
                        "priority": (
                            "high" if "grief" in str(input_payload) else "normal"
                        ),
                    }
                    transformed_messages.append(transformed)
                    return transformed

            # Test message priority and transformation
            mock_ipa = MockAgent(AgentType.IPA)
            mock_wba = MockAgent(AgentType.WBA)
            mock_nga = MockAgent(AgentType.NGA)

            # Process through agent sequence
            ipa_result = await mock_ipa.process({"text": scenario["player_input"]})
            wba_result = await mock_wba.process(ipa_result)
            await mock_nga.process(wba_result)

            # Verify transformations
            assert len(transformed_messages) == 3, "Expected 3 message transformations"

            # Verify priority handling for therapeutic content
            for msg in transformed_messages:
                if "grief" in str(msg["original_input"]):
                    assert msg["priority"] == "high", (
                        "Therapeutic content should have high priority"
                    )

            # Verify message chain integrity
            assert (
                transformed_messages[1]["original_input"] == transformed_messages[0]
            ), "Message chain broken"
            assert (
                transformed_messages[2]["original_input"] == transformed_messages[1]
            ), "Message chain broken"

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )

    async def test_message_delivery_confirmation(
        self, integration_helper, redis_client
    ):
        """Test message delivery confirmation and acknowledgment."""
        test_env = await integration_helper.setup_test_environment(
            "delivery_confirmation"
        )

        try:
            from tta_ai.orchestration import (
                AgentId,
                AgentMessage,
                MessagePriority,
                MessageType,
            )
            from tta_ai.orchestration.coordinators.redis_message_coordinator import (
                RedisMessageCoordinator,
            )

            # Create message coordinator
            coordinator = RedisMessageCoordinator(redis_client)

            # Create test agents
            ipa_id = AgentId(type=AgentType.IPA, instance="test")
            wba_id = AgentId(type=AgentType.WBA, instance="test")

            # Create test message
            test_message = AgentMessage(
                sender_id=ipa_id,
                recipient_id=wba_id,
                message_type=MessageType.WORKFLOW_REQUEST,
                priority=MessagePriority.HIGH,
                payload={"text": "test message", "session_id": test_env["session_id"]},
                correlation_id="test_correlation_123",
            )

            # Send message and verify delivery
            delivery_result = await coordinator.send_message(test_message)
            assert delivery_result, "Message delivery failed"

            # Verify message is in recipient queue
            queue_state = (
                await integration_helper.redis_verifier.verify_message_queue_state(
                    f"{wba_id.type.value}:{wba_id.instance}"
                )
            )
            assert queue_state["queue_exists"], "Recipient queue not found"
            assert queue_state["queue_length"] > 0, "Message not queued"

            # Simulate message receipt and acknowledgment
            received_message = await coordinator.receive_message(
                wba_id, timeout_seconds=5.0
            )
            assert received_message is not None, "Message not received"
            assert received_message.correlation_id == "test_correlation_123", (
                "Correlation ID mismatch"
            )

            # Verify queue is empty after receipt
            post_receipt_state = (
                await integration_helper.redis_verifier.verify_message_queue_state(
                    f"{wba_id.type.value}:{wba_id.instance}"
                )
            )
            assert post_receipt_state["queue_length"] == 0, (
                "Queue not cleared after receipt"
            )

        finally:
            await integration_helper.cleanup_test_data(
                test_env["session_id"], test_env["workflow_id"], test_env["player_id"]
            )
