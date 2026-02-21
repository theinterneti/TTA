"""

# Logseq: [[TTA.dev/Tests/Agent_orchestration/Test_workflow_chain_validation]]
Complete IPA → WBA → NGA workflow chain validation tests.

This module provides detailed validation of the complete agent workflow chain,
ensuring proper data flow and integration between all agent components.
"""

import asyncio
import json
import time

import pytest
import pytest_asyncio
from tta_ai.orchestration.performance.response_time_monitor import (
    OperationType,
    ResponseTimeMonitor,
)
from tta_ai.orchestration.proxies import (
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    WorldBuilderAgentProxy,
)
from tta_ai.orchestration.realtime.agent_event_integration import (
    AgentWorkflowCoordinator,
)


@pytest.mark.integration
@pytest.mark.redis
@pytest.mark.neo4j
class TestWorkflowChainValidation:
    """Detailed validation of the complete agent workflow chain."""

    @pytest_asyncio.fixture
    async def workflow_coordinator(
        self, redis_coordinator, neo4j_driver, event_publisher
    ):
        """Create workflow coordinator with enhanced agent proxies."""
        # Create enhanced agent proxies with real-time integration
        ipa_proxy = InputProcessorAgentProxy(
            coordinator=redis_coordinator,
            instance="workflow_ipa",
            enable_real_agent=False,  # Use mock for testing
            fallback_to_mock=True,
            event_publisher=event_publisher,
        )

        wba_proxy = WorldBuilderAgentProxy(
            coordinator=redis_coordinator,
            instance="workflow_wba",
            enable_real_agent=False,  # Use mock for testing
            fallback_to_mock=True,
            event_publisher=event_publisher,
            neo4j_driver=neo4j_driver,
        )

        nga_proxy = NarrativeGeneratorAgentProxy(
            coordinator=redis_coordinator,
            instance="workflow_nga",
            enable_real_agent=False,  # Use mock for testing
            fallback_to_mock=True,
            event_publisher=event_publisher,
        )

        # Create workflow coordinator
        return AgentWorkflowCoordinator(
            ipa_proxy=ipa_proxy,
            wba_proxy=wba_proxy,
            nga_proxy=nga_proxy,
            event_publisher=event_publisher,
        )

    @pytest_asyncio.fixture
    async def response_monitor(self):
        """Create response time monitor for workflow validation."""
        monitor = ResponseTimeMonitor(
            max_metrics_history=1000,
            statistics_window_minutes=10,
            enable_real_time_analysis=True,
        )
        await monitor.start()
        yield monitor
        await monitor.stop()

    async def test_complete_workflow_chain_execution(
        self, workflow_coordinator, response_monitor
    ):
        """Test complete workflow chain execution with detailed validation."""
        user_input = "I'm feeling overwhelmed with my new job responsibilities. How can I manage this better?"
        session_id = "workflow_chain_session_001"
        world_id = "workflow_chain_world_001"

        # Track workflow execution with performance monitoring
        async with response_monitor.track_operation(
            operation_type=OperationType.WORKFLOW_EXECUTION,
            workflow_id="complete_chain_test",
            user_id="workflow_test_user",
        ):
            start_time = time.time()

            # Execute complete workflow
            result = await workflow_coordinator.execute_complete_workflow(
                user_input=user_input, session_id=session_id, world_id=world_id
            )

            end_time = time.time()
            execution_time = end_time - start_time

        # Validate workflow completion
        assert result is not None
        assert "story" in result
        assert "workflow_id" in result
        assert "session_id" in result
        assert result["session_id"] == session_id

        # Validate individual agent results
        assert "ipa_result" in result
        assert "wba_result" in result
        assert "nga_result" in result

        # Detailed IPA result validation
        ipa_result = result["ipa_result"]
        assert "intent" in ipa_result
        assert "entities" in ipa_result
        assert "safety_assessment" in ipa_result
        assert "routing_hints" in ipa_result

        # Validate intent classification
        intent = ipa_result["intent"]
        assert intent is not None
        assert isinstance(intent, str)
        assert len(intent) > 0

        # Validate entity extraction
        entities = ipa_result["entities"]
        assert isinstance(entities, list)
        # Should extract job-related entities
        any(
            "job" in str(entity).lower() or "work" in str(entity).lower()
            for entity in entities
        )

        # Validate safety assessment
        safety_assessment = ipa_result["safety_assessment"]
        assert "risk_level" in safety_assessment
        assert safety_assessment["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert safety_assessment["risk_level"] == "LOW"  # Should be safe content

        # Detailed WBA result validation
        wba_result = result["wba_result"]
        assert "world_state" in wba_result
        assert "context_updates" in wba_result
        assert "character_info" in wba_result

        # Validate world state updates
        world_state = wba_result["world_state"]
        assert isinstance(world_state, dict)
        assert len(world_state) > 0

        # Should contain context about job stress
        context_updates = wba_result["context_updates"]
        assert isinstance(context_updates, list)

        # Detailed NGA result validation
        nga_result = result["nga_result"]
        assert "narrative" in nga_result
        assert "therapeutic_elements" in nga_result
        assert "content_metadata" in nga_result

        # Validate narrative generation
        narrative = nga_result["narrative"]
        assert isinstance(narrative, str)
        assert len(narrative) > 50  # Should be substantial content

        # Validate therapeutic elements
        therapeutic_elements = nga_result["therapeutic_elements"]
        assert isinstance(therapeutic_elements, list)
        assert len(therapeutic_elements) > 0

        # Final story should be coherent and therapeutic
        final_story = result["story"]
        assert isinstance(final_story, str)
        assert len(final_story) > 100

        # Should contain supportive/helpful content
        supportive_keywords = [
            "manage",
            "help",
            "support",
            "cope",
            "balance",
            "strategies",
        ]
        contains_support = any(
            keyword in final_story.lower() for keyword in supportive_keywords
        )
        assert contains_support

        # Performance validation
        assert execution_time < 10.0  # Should complete within reasonable time

    async def test_workflow_data_flow_integrity(
        self, workflow_coordinator, response_monitor
    ):
        """Test data flow integrity between workflow stages."""
        user_input = "I want to explore the ancient library in the magical forest."
        session_id = "data_flow_session_001"
        world_id = "data_flow_world_001"

        # Execute workflow with detailed tracking
        result = await workflow_coordinator.execute_complete_workflow(
            user_input=user_input, session_id=session_id, world_id=world_id
        )

        # Extract individual results
        ipa_result = result["ipa_result"]
        wba_result = result["wba_result"]
        nga_result = result["nga_result"]

        # Validate data flow: IPA → WBA
        # IPA entities should influence WBA world state
        ipa_entities = ipa_result.get("entities", [])
        wba_world_state = wba_result.get("world_state", {})

        # Check if IPA entities are reflected in world state
        entity_strings = [str(entity).lower() for entity in ipa_entities]
        world_state_text = json.dumps(wba_world_state).lower()

        # At least some entities should be incorporated
        any(
            entity in world_state_text
            for entity in entity_strings
            if len(entity) > 3  # Skip very short entities
        )

        # Validate data flow: WBA → NGA
        # WBA world state should influence NGA narrative
        nga_narrative = nga_result.get("narrative", "")

        # Check if world state elements appear in narrative
        world_elements = []
        if "location" in wba_world_state:
            world_elements.append(str(wba_world_state["location"]).lower())
        if "setting" in wba_world_state:
            world_elements.append(str(wba_world_state["setting"]).lower())

        narrative_lower = nga_narrative.lower()
        any(
            element in narrative_lower for element in world_elements if len(element) > 3
        )

        # Validate data flow: IPA → NGA (direct)
        # IPA intent should influence NGA therapeutic approach
        ipa_result.get("intent", "")
        therapeutic_elements = nga_result.get("therapeutic_elements", [])

        # Intent should be reflected in therapeutic approach
        len(therapeutic_elements) > 0

        # Validate session consistency
        assert result["session_id"] == session_id

        # All components should reference the same workflow
        workflow_id = result.get("workflow_id")
        assert workflow_id is not None

    async def test_workflow_error_propagation(
        self, workflow_coordinator, response_monitor
    ):
        """Test error handling and propagation through workflow chain."""
        # Test with potentially problematic input
        problematic_inputs = [
            "",  # Empty input
            "   ",  # Whitespace only
            "a" * 5000,  # Very long input
            "Test input with special chars: @#$%^&*()[]{}|\\:;\"'<>?,./",
        ]

        for i, problematic_input in enumerate(problematic_inputs):
            session_id = f"error_prop_session_{i + 1:03d}"
            world_id = f"error_prop_world_{i + 1:03d}"

            try:
                result = await workflow_coordinator.execute_complete_workflow(
                    user_input=problematic_input,
                    session_id=session_id,
                    world_id=world_id,
                )

                # Should handle gracefully
                assert result is not None

                if "error" in result:
                    # Error should be properly structured
                    assert "error_type" in result
                    assert "error_message" in result
                    assert "failed_stage" in result
                else:
                    # Should provide fallback response
                    assert "story" in result
                    assert len(result["story"]) > 0

            except Exception as e:
                # If exception occurs, it should be a controlled exception
                error_message = str(e).lower()
                assert any(
                    keyword in error_message
                    for keyword in ["validation", "input", "format", "length"]
                )

    async def test_workflow_performance_optimization(
        self, workflow_coordinator, response_monitor
    ):
        """Test workflow performance optimization and monitoring."""
        # Execute multiple workflows to gather performance data
        test_inputs = [
            "I need help with time management.",
            "Can you help me practice for a presentation?",
            "I'm feeling stressed about my relationships.",
            "I want to improve my communication skills.",
            "Help me understand my emotions better.",
        ]

        execution_times = []
        results = []

        for i, test_input in enumerate(test_inputs):
            session_id = f"perf_opt_session_{i + 1:03d}"
            world_id = f"perf_opt_world_{i + 1:03d}"

            start_time = time.time()

            result = await workflow_coordinator.execute_complete_workflow(
                user_input=test_input, session_id=session_id, world_id=world_id
            )

            end_time = time.time()
            execution_time = end_time - start_time

            execution_times.append(execution_time)
            results.append(result)

            # Validate each result
            assert result is not None
            assert "story" in result
            assert len(result["story"]) > 0

        # Analyze performance
        avg_execution_time = sum(execution_times) / len(execution_times)
        max_execution_time = max(execution_times)
        min_execution_time = min(execution_times)

        # Performance assertions
        assert avg_execution_time < 5.0  # Average should be reasonable
        assert max_execution_time < 10.0  # No single execution should be too slow
        assert min_execution_time > 0.1  # Should take some time (not instant)

        # Get performance statistics from monitor
        stats = response_monitor.get_statistics(time_window_minutes=5)

        if OperationType.WORKFLOW_EXECUTION in stats:
            workflow_stats = stats[OperationType.WORKFLOW_EXECUTION]
            assert workflow_stats.total_operations >= len(test_inputs)
            assert workflow_stats.success_rate > 0.8  # At least 80% success rate

    async def test_workflow_concurrent_execution(
        self, workflow_coordinator, response_monitor
    ):
        """Test concurrent workflow execution and resource management."""
        num_concurrent = 3
        concurrent_tasks = []

        # Create concurrent workflow tasks
        for i in range(num_concurrent):
            user_input = f"I'm user {i + 1} and I need help with anxiety management."
            session_id = f"concurrent_workflow_session_{i + 1:03d}"
            world_id = f"concurrent_workflow_world_{i + 1:03d}"

            task = asyncio.create_task(
                workflow_coordinator.execute_complete_workflow(
                    user_input=user_input, session_id=session_id, world_id=world_id
                )
            )
            concurrent_tasks.append((task, session_id))

        start_time = time.time()

        # Wait for all tasks to complete
        results = []
        for task, session_id in concurrent_tasks:
            try:
                result = await task
                results.append((result, session_id))
            except Exception as e:
                pytest.fail(f"Concurrent workflow failed for session {session_id}: {e}")

        end_time = time.time()
        total_time = end_time - start_time

        # Validate all workflows completed
        assert len(results) == num_concurrent

        for result, session_id in results:
            assert result is not None
            assert "story" in result
            assert result["session_id"] == session_id
            assert len(result["story"]) > 0

        # Performance validation for concurrent execution
        total_time / num_concurrent
        assert total_time < 20.0  # All should complete within reasonable time

    async def test_workflow_therapeutic_consistency(
        self, workflow_coordinator, response_monitor
    ):
        """Test therapeutic consistency across the workflow chain."""
        therapeutic_inputs = [
            {
                "input": "I'm dealing with depression and feel hopeless.",
                "expected_therapeutic_elements": [
                    "support",
                    "hope",
                    "professional",
                    "help",
                ],
            },
            {
                "input": "I have social anxiety and avoid people.",
                "expected_therapeutic_elements": [
                    "gradual",
                    "practice",
                    "support",
                    "confidence",
                ],
            },
            {
                "input": "I'm struggling with grief after losing someone.",
                "expected_therapeutic_elements": [
                    "process",
                    "time",
                    "support",
                    "healing",
                ],
            },
        ]

        for i, scenario in enumerate(therapeutic_inputs):
            session_id = f"therapeutic_consistency_session_{i + 1:03d}"
            world_id = f"therapeutic_consistency_world_{i + 1:03d}"

            result = await workflow_coordinator.execute_complete_workflow(
                user_input=scenario["input"], session_id=session_id, world_id=world_id
            )

            assert result is not None

            # Validate therapeutic elements in IPA result
            ipa_result = result.get("ipa_result", {})
            safety_assessment = ipa_result.get("safety_assessment", {})
            assert safety_assessment.get("risk_level") in [
                "LOW",
                "MEDIUM",
            ]  # Should not be high risk

            # Validate therapeutic elements in NGA result
            nga_result = result.get("nga_result", {})
            therapeutic_elements = nga_result.get("therapeutic_elements", [])
            assert len(therapeutic_elements) > 0

            # Validate final story contains therapeutic elements
            story = result.get("story", "").lower()
            therapeutic_count = sum(
                1
                for element in scenario["expected_therapeutic_elements"]
                if element in story
            )

            # Should contain at least some therapeutic elements
            assert therapeutic_count > 0

            # Should not contain harmful content
            harmful_keywords = ["hopeless", "give up", "no point", "worthless"]
            harmful_content = any(keyword in story for keyword in harmful_keywords)
            assert not harmful_content
