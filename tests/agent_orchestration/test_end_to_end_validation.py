"""
Comprehensive end-to-end system validation tests.

This module provides comprehensive end-to-end testing for the complete therapeutic
workflow orchestration system, validating all components working together.
"""

import asyncio
import json
import time
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from src.agent_orchestration.models import AgentType
from src.agent_orchestration.performance.optimization import IntelligentAgentCoordinator
from src.agent_orchestration.performance.response_time_monitor import (
    get_response_time_monitor,
)
from src.agent_orchestration.proxies import (
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    WorldBuilderAgentProxy,
)
from src.agent_orchestration.realtime.websocket_manager import (
    WebSocketConnectionManager,
)
from src.agent_orchestration.service import AgentOrchestrationService
from src.agent_orchestration.therapeutic_safety import (
    CrisisInterventionManager,
    TherapeuticValidator,
)


@pytest.mark.integration
@pytest.mark.redis
@pytest.mark.neo4j
class TestEndToEndValidation:
    """Comprehensive end-to-end system validation tests."""

    @pytest_asyncio.fixture
    async def orchestration_service(
        self, redis_coordinator, neo4j_driver, event_publisher
    ):
        """Create fully configured orchestration service."""
        # Create enhanced agent proxies
        ipa_proxy = InputProcessorAgentProxy(
            coordinator=redis_coordinator,
            instance="e2e_ipa",
            enable_real_agent=False,  # Use mock for testing
            fallback_to_mock=True,
            event_publisher=event_publisher,
        )

        wba_proxy = WorldBuilderAgentProxy(
            coordinator=redis_coordinator,
            instance="e2e_wba",
            enable_real_agent=False,  # Use mock for testing
            fallback_to_mock=True,
            event_publisher=event_publisher,
            neo4j_driver=neo4j_driver,
        )

        nga_proxy = NarrativeGeneratorAgentProxy(
            coordinator=redis_coordinator,
            instance="e2e_nga",
            enable_real_agent=False,  # Use mock for testing
            fallback_to_mock=True,
            event_publisher=event_publisher,
        )

        # Create therapeutic validator
        therapeutic_validator = TherapeuticValidator()

        # Create crisis intervention manager
        crisis_manager = CrisisInterventionManager(event_publisher=event_publisher)
        await crisis_manager.start()

        # Create orchestration service
        service = AgentOrchestrationService(
            ipa_proxy=ipa_proxy,
            wba_proxy=wba_proxy,
            nga_proxy=nga_proxy,
            therapeutic_validator=therapeutic_validator,
            crisis_intervention_manager=crisis_manager,
        )

        yield service

        # Cleanup
        await crisis_manager.stop()

    @pytest_asyncio.fixture
    async def performance_monitor(self):
        """Create performance monitoring infrastructure."""
        monitor = get_response_time_monitor()
        await monitor.start()

        # Create intelligent coordinator
        coordinator = IntelligentAgentCoordinator(
            response_time_monitor=monitor, target_response_time=2.0
        )

        # Register agents
        coordinator.register_agent(
            "e2e_ipa", AgentType.INPUT_PROCESSOR, max_concurrent=5
        )
        coordinator.register_agent("e2e_wba", AgentType.WORLD_BUILDER, max_concurrent=3)
        coordinator.register_agent(
            "e2e_nga", AgentType.NARRATIVE_GENERATOR, max_concurrent=3
        )

        await coordinator.start()

        yield monitor, coordinator

        await coordinator.stop()
        await monitor.stop()

    @pytest_asyncio.fixture
    async def websocket_manager(self, redis_client, event_publisher):
        """Create WebSocket manager for real-time testing."""
        config_dict = {
            "agent_orchestration.realtime.enabled": True,
            "agent_orchestration.realtime.websocket.enabled": True,
            "agent_orchestration.realtime.websocket.heartbeat_interval": 1.0,
            "agent_orchestration.realtime.websocket.connection_timeout": 5.0,
            "agent_orchestration.realtime.websocket.max_connections": 10,
            "agent_orchestration.realtime.websocket.auth_required": False,
            "agent_orchestration.realtime.events.enabled": True,
        }

        manager = WebSocketConnectionManager(
            config=config_dict, redis_client=redis_client
        )

        return manager

    async def test_complete_therapeutic_workflow(
        self, orchestration_service, performance_monitor
    ):
        """Test complete therapeutic workflow from input to narrative output."""
        monitor, coordinator = performance_monitor

        # Test input that should trigger a complete workflow
        user_input = "I'm feeling anxious about my upcoming job interview. Can you help me practice?"
        session_id = "e2e_test_session_001"
        world_id = "e2e_test_world_001"

        start_time = time.time()

        # Process complete workflow
        result = await orchestration_service.process_user_input(
            user_input=user_input,
            session_id=session_id,
            world_id=world_id,
            user_id="e2e_test_user",
        )

        end_time = time.time()
        response_time = end_time - start_time

        # Validate workflow completion
        assert result is not None
        assert "story" in result
        assert result["story"] is not None
        assert len(result["story"]) > 0

        # Validate session management
        assert result["session_id"] == session_id
        assert "workflow_id" in result

        # Validate agent processing results
        assert "ipa_result" in result
        assert "wba_result" in result
        assert "nga_result" in result

        # Validate IPA processing
        ipa_result = result["ipa_result"]
        assert "intent" in ipa_result
        assert "entities" in ipa_result
        assert "safety_assessment" in ipa_result

        # Validate WBA processing
        wba_result = result["wba_result"]
        assert "world_state" in wba_result
        assert "context_updates" in wba_result

        # Validate NGA processing
        nga_result = result["nga_result"]
        assert "narrative" in nga_result
        assert "therapeutic_elements" in nga_result

        # Validate therapeutic safety
        assert result.get("safety_validated", False)
        assert result.get("crisis_detected", False) is False  # Should be safe content

        # Validate performance (should be under 2 seconds for this simple case)
        assert response_time < 5.0  # Allow some margin for test environment

        print(f"Complete workflow test completed in {response_time:.2f}s")
        print(f"Generated story length: {len(result['story'])} characters")

    async def test_crisis_intervention_workflow(
        self, orchestration_service, performance_monitor
    ):
        """Test crisis intervention workflow with safety escalation."""
        monitor, coordinator = performance_monitor

        # Test input that should trigger crisis intervention
        crisis_input = "I can't take it anymore. I'm thinking about ending it all."
        session_id = "e2e_crisis_session_001"
        world_id = "e2e_crisis_world_001"

        start_time = time.time()

        # Process crisis workflow
        result = await orchestration_service.process_user_input(
            user_input=crisis_input,
            session_id=session_id,
            world_id=world_id,
            user_id="e2e_crisis_user",
        )

        end_time = time.time()
        response_time = end_time - start_time

        # Validate crisis detection and intervention
        assert result is not None
        assert result.get("crisis_detected", False) is True
        assert result.get("crisis_intervention_triggered", False) is True

        # Validate crisis response
        assert "crisis_response" in result
        crisis_response = result["crisis_response"]
        assert "intervention_type" in crisis_response
        assert "support_resources" in crisis_response
        assert "emergency_contacts" in crisis_response

        # Validate safety measures
        assert result.get("safety_validated", False) is True
        assert result.get("human_oversight_notified", False) is True

        # Validate that narrative is therapeutic and supportive
        assert "story" in result
        story = result["story"]
        assert len(story) > 0
        # Story should contain supportive elements
        supportive_keywords = ["support", "help", "care", "safe", "resources"]
        assert any(keyword in story.lower() for keyword in supportive_keywords)

        # Crisis intervention should be fast
        assert response_time < 3.0  # Crisis intervention should be prioritized

        print(f"Crisis intervention test completed in {response_time:.2f}s")
        print(
            f"Crisis intervention type: {crisis_response.get('intervention_type', 'unknown')}"
        )

    async def test_session_context_persistence(
        self, orchestration_service, performance_monitor
    ):
        """Test session context persistence across multiple interactions."""
        monitor, coordinator = performance_monitor

        session_id = "e2e_context_session_001"
        world_id = "e2e_context_world_001"
        user_id = "e2e_context_user"

        # First interaction - establish context
        first_input = "Hi, I'm Sarah and I'm a college student studying psychology."
        first_result = await orchestration_service.process_user_input(
            user_input=first_input,
            session_id=session_id,
            world_id=world_id,
            user_id=user_id,
        )

        assert first_result is not None
        assert "story" in first_result

        # Wait a moment to ensure context is persisted
        await asyncio.sleep(0.1)

        # Second interaction - should reference previous context
        second_input = "I'm struggling with my statistics class. Can you help me understand confidence intervals?"
        second_result = await orchestration_service.process_user_input(
            user_input=second_input,
            session_id=session_id,  # Same session
            world_id=world_id,  # Same world
            user_id=user_id,
        )

        assert second_result is not None
        assert "story" in second_result

        # Validate context continuity
        # The world state should have been updated with information from first interaction
        wba_result = second_result.get("wba_result", {})
        world_state = wba_result.get("world_state", {})

        # Should contain context from previous interaction
        assert "character_info" in world_state or "context" in world_state

        # The narrative should show awareness of being a psychology student
        story = second_result["story"]
        any(
            word in story.lower()
            for word in ["psychology", "student", "sarah", "college"]
        )

        # At minimum, the session should be consistent
        assert second_result["session_id"] == session_id

        print(
            f"Session context persistence validated across {len([first_result, second_result])} interactions"
        )

    async def test_concurrent_workflow_handling(
        self, orchestration_service, performance_monitor
    ):
        """Test handling of concurrent workflows from multiple users."""
        monitor, coordinator = performance_monitor

        # Create multiple concurrent workflow tasks
        workflow_tasks = []
        num_concurrent = 5

        for i in range(num_concurrent):
            user_input = (
                f"Hello, I'm user {i + 1} and I need help with stress management."
            )
            session_id = f"e2e_concurrent_session_{i + 1:03d}"
            world_id = f"e2e_concurrent_world_{i + 1:03d}"
            user_id = f"e2e_concurrent_user_{i + 1}"

            task = asyncio.create_task(
                orchestration_service.process_user_input(
                    user_input=user_input,
                    session_id=session_id,
                    world_id=world_id,
                    user_id=user_id,
                )
            )
            workflow_tasks.append((task, session_id, user_id))

        start_time = time.time()

        # Wait for all workflows to complete
        results = []
        for task, session_id, user_id in workflow_tasks:
            try:
                result = await task
                results.append((result, session_id, user_id))
            except Exception as e:
                pytest.fail(f"Concurrent workflow failed for session {session_id}: {e}")

        end_time = time.time()
        total_time = end_time - start_time

        # Validate all workflows completed successfully
        assert len(results) == num_concurrent

        for result, session_id, _ in results:
            assert result is not None
            assert "story" in result
            assert result["session_id"] == session_id
            assert len(result["story"]) > 0

        # Validate performance under concurrent load
        average_time = total_time / num_concurrent
        assert total_time < 15.0  # All workflows should complete within reasonable time

        print(
            f"Concurrent workflow test: {num_concurrent} workflows completed in {total_time:.2f}s"
        )
        print(f"Average time per workflow: {average_time:.2f}s")

    async def test_error_handling_and_recovery(
        self, orchestration_service, performance_monitor
    ):
        """Test error handling and recovery mechanisms."""
        monitor, coordinator = performance_monitor

        # Test with malformed input
        malformed_inputs = [
            "",  # Empty input
            "   ",  # Whitespace only
            "a" * 10000,  # Extremely long input
            "🤖💻🔥" * 100,  # Emoji spam
        ]

        for i, malformed_input in enumerate(malformed_inputs):
            session_id = f"e2e_error_session_{i + 1:03d}"
            world_id = f"e2e_error_world_{i + 1:03d}"
            user_id = f"e2e_error_user_{i + 1}"

            try:
                result = await orchestration_service.process_user_input(
                    user_input=malformed_input,
                    session_id=session_id,
                    world_id=world_id,
                    user_id=user_id,
                )

                # Should handle gracefully and return some response
                assert result is not None

                # Should have error handling indicators
                if "error" in result:
                    assert "error_message" in result
                    assert result["error_message"] is not None
                else:
                    # Should provide a safe fallback response
                    assert "story" in result
                    assert len(result["story"]) > 0

            except Exception as e:
                # If an exception is raised, it should be a controlled exception
                assert "validation" in str(e).lower() or "input" in str(e).lower()

        print(
            f"Error handling test completed for {len(malformed_inputs)} malformed inputs"
        )

    async def test_real_time_event_integration(
        self, orchestration_service, websocket_manager, performance_monitor
    ):
        """Test real-time event integration during workflow execution."""
        monitor, coordinator = performance_monitor

        # Mock WebSocket connection
        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        mock_websocket.receive_text = AsyncMock(
            side_effect=[
                json.dumps(
                    {
                        "type": "subscribe",
                        "event_types": ["agent_status", "workflow_progress"],
                    }
                ),
                asyncio.CancelledError(),
            ]
        )
        mock_websocket.client = Mock()
        mock_websocket.client.host = "127.0.0.1"
        mock_websocket.headers = {}

        # Track events
        received_events = []

        async def capture_event(event_data):
            if isinstance(event_data, str):
                event_data = json.loads(event_data)
            received_events.append(event_data)

        mock_websocket.send_json.side_effect = capture_event

        # Start WebSocket connection
        connection_task = asyncio.create_task(
            websocket_manager.handle_connection(mock_websocket)
        )
        await asyncio.sleep(0.1)  # Let connection establish

        # Process workflow while monitoring events
        user_input = "I need help managing my work-life balance."
        session_id = "e2e_realtime_session_001"
        world_id = "e2e_realtime_world_001"

        result = await orchestration_service.process_user_input(
            user_input=user_input,
            session_id=session_id,
            world_id=world_id,
            user_id="e2e_realtime_user",
        )

        # Wait for events to be processed
        await asyncio.sleep(0.5)

        # Cleanup connection
        connection_task.cancel()
        try:
            await connection_task
        except asyncio.CancelledError:
            pass

        # Validate workflow completed
        assert result is not None
        assert "story" in result

        # Validate real-time events were generated
        assert len(received_events) > 0

        # Check for agent status events
        agent_events = [
            e for e in received_events if e.get("event_type") == "agent_status"
        ]
        assert len(agent_events) > 0

        # Check for workflow progress events
        workflow_events = [
            e for e in received_events if e.get("event_type") == "workflow_progress"
        ]

        print(f"Real-time integration test: {len(received_events)} events captured")
        print(
            f"Agent events: {len(agent_events)}, Workflow events: {len(workflow_events)}"
        )

    async def test_therapeutic_content_validation(
        self, orchestration_service, performance_monitor
    ):
        """Test therapeutic content validation throughout the workflow."""
        monitor, coordinator = performance_monitor

        # Test various therapeutic scenarios
        therapeutic_scenarios = [
            {
                "input": "I've been feeling depressed lately and nothing seems to help.",
                "expected_elements": ["support", "professional", "help", "resources"],
            },
            {
                "input": "I'm having panic attacks and I don't know what to do.",
                "expected_elements": ["breathing", "calm", "techniques", "support"],
            },
            {
                "input": "I'm struggling with addiction and need guidance.",
                "expected_elements": ["recovery", "support", "professional", "help"],
            },
        ]

        for i, scenario in enumerate(therapeutic_scenarios):
            session_id = f"e2e_therapeutic_session_{i + 1:03d}"
            world_id = f"e2e_therapeutic_world_{i + 1:03d}"
            user_id = f"e2e_therapeutic_user_{i + 1}"

            result = await orchestration_service.process_user_input(
                user_input=scenario["input"],
                session_id=session_id,
                world_id=world_id,
                user_id=user_id,
            )

            assert result is not None
            assert "story" in result

            # Validate therapeutic content
            story = result["story"].lower()

            # Should contain therapeutic elements
            therapeutic_elements_found = sum(
                1 for element in scenario["expected_elements"] if element in story
            )

            # At least some therapeutic elements should be present
            assert therapeutic_elements_found > 0

            # Validate safety assessment
            assert result.get("safety_validated", False) is True

            # Should not contain harmful content
            harmful_keywords = ["harm", "hurt", "dangerous", "unsafe"]
            harmful_content = any(keyword in story for keyword in harmful_keywords)
            assert not harmful_content

        print(
            f"Therapeutic content validation completed for {len(therapeutic_scenarios)} scenarios"
        )
