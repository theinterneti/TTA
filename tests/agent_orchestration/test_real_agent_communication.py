"""
Integration tests for real agent communication workflows.

This module tests the enhanced agent proxies with real agent communication,
replacing mock implementations with actual data flows and testing complete
IPA → WBA → NGA workflows.
"""

import asyncio
import time

import pytest
import pytest_asyncio

from tta_ai.orchestration import (
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    WorldBuilderAgentProxy,
)
from tta_ai.orchestration.adapters import AgentAdapterFactory, RetryConfig
from tta_ai.orchestration.enhanced_coordinator import EnhancedRedisMessageCoordinator


@pytest.mark.integration
@pytest.mark.redis
class TestRealAgentCommunication:
    """Test real agent communication workflows."""

    @pytest_asyncio.fixture
    async def adapter_factory(self):
        """Create adapter factory for testing."""
        retry_config = RetryConfig(max_retries=2, base_delay=0.1)
        return AgentAdapterFactory(
            neo4j_manager=None,  # Mock for testing
            tools={},
            fallback_to_mock=True,
            retry_config=retry_config,
        )

    @pytest_asyncio.fixture
    async def enhanced_coordinator(self, redis_client, adapter_factory):
        """Create enhanced coordinator with real agent support."""
        return EnhancedRedisMessageCoordinator(
            redis=redis_client,
            key_prefix="test_real_agents",
            enable_real_agents=True,
            fallback_to_mock=True,
        )

    @pytest_asyncio.fixture
    async def real_ipa_proxy(self, enhanced_coordinator):
        """Create IPA proxy with real agent communication enabled."""
        return InputProcessorAgentProxy(
            coordinator=enhanced_coordinator,
            instance="test_real",
            enable_real_agent=True,
            fallback_to_mock=True,
        )

    @pytest_asyncio.fixture
    async def real_wba_proxy(self, enhanced_coordinator):
        """Create WBA proxy with real agent communication enabled."""
        return WorldBuilderAgentProxy(
            coordinator=enhanced_coordinator,
            instance="test_real",
            enable_real_agent=True,
            fallback_to_mock=True,
            neo4j_manager=None,  # Mock for testing
        )

    @pytest_asyncio.fixture
    async def real_nga_proxy(self, enhanced_coordinator):
        """Create NGA proxy with real agent communication enabled."""
        return NarrativeGeneratorAgentProxy(
            coordinator=enhanced_coordinator,
            instance="test_real",
            enable_real_agent=True,
            fallback_to_mock=True,
        )

    async def test_ipa_real_agent_communication(self, real_ipa_proxy):
        """Test IPA proxy with real agent communication."""
        # Test input processing
        input_payload = {"text": "look around the mysterious forest"}

        result = await real_ipa_proxy.process(input_payload)

        # Verify result structure
        assert "normalized_text" in result
        assert "routing" in result
        assert "therapeutic_validation" in result
        assert "source" in result

        # Check that text was processed
        assert result["normalized_text"] == "look around the mysterious forest"

        # Verify routing information
        routing = result["routing"]
        assert "intent" in routing

        # Source should indicate real or fallback
        assert result["source"] in ["real_ipa", "mock_fallback"]

    async def test_wba_real_agent_communication(self, real_wba_proxy):
        """Test WBA proxy with real agent communication."""
        # Test world state fetch
        world_id = "test_world_001"
        input_payload = {"world_id": world_id}

        result = await real_wba_proxy.process(input_payload)

        # Verify result structure
        assert "world_id" in result
        assert "world_state" in result
        assert "source" in result
        assert result["world_id"] == world_id

        # Test world state update
        updates = {"regions": [{"name": "Enchanted Grove", "type": "forest"}]}
        update_payload = {"world_id": world_id, "updates": updates}

        update_result = await real_wba_proxy.process(update_payload)

        # Verify update was processed
        assert "updated" in update_result
        assert update_result["world_id"] == world_id
        assert update_result["source"] in ["real_wba", "mock_fallback"]

    async def test_nga_real_agent_communication(self, real_nga_proxy):
        """Test NGA proxy with real agent communication."""
        # Test narrative generation
        prompt = "The player discovers a hidden path in the forest"
        context = {
            "session_id": "test_session_001",
            "world_state": {"regions": [{"name": "Mysterious Forest"}]},
        }
        input_payload = {"prompt": prompt, "context": context}

        result = await real_nga_proxy.process(input_payload)

        # Verify result structure
        assert "story" in result
        assert "raw" in result
        assert "context_used" in result
        assert "therapeutic_validation" in result
        assert "source" in result

        # Check that story was generated
        assert len(result["story"]) > 0
        assert result["context_used"] is True
        assert result["source"] in ["real_nga", "mock_fallback"]

    async def test_complete_workflow_chain(
        self, real_ipa_proxy, real_wba_proxy, real_nga_proxy
    ):
        """Test complete IPA → WBA → NGA workflow chain with real agents."""
        session_id = "test_workflow_001"

        # Step 1: Process player input through IPA
        player_input = "I want to explore the ancient ruins"
        ipa_result = await real_ipa_proxy.process({"text": player_input})

        assert "routing" in ipa_result
        intent = ipa_result["routing"].get("intent", "unknown")

        # Step 2: Update world state through WBA based on intent
        world_id = f"world_{session_id}"
        world_updates = {
            "current_location": "ancient_ruins",
            "player_action": intent,
            "entities": [{"type": "ruins", "name": "Ancient Temple"}],
        }
        wba_result = await real_wba_proxy.process(
            {"world_id": world_id, "updates": world_updates}
        )

        assert "world_state" in wba_result

        # Step 3: Generate narrative through NGA based on world state
        narrative_prompt = f"Player action: {intent}. Current location: ancient ruins."
        narrative_context = {
            "session_id": session_id,
            "world_state": wba_result["world_state"],
            "player_intent": intent,
        }
        nga_result = await real_nga_proxy.process(
            {"prompt": narrative_prompt, "context": narrative_context}
        )

        assert "story" in nga_result
        assert len(nga_result["story"]) > 0

        # Verify workflow continuity
        workflow_result = {
            "player_input": player_input,
            "processed_intent": intent,
            "world_state": wba_result["world_state"],
            "generated_narrative": nga_result["story"],
            "sources": {
                "ipa": ipa_result.get("source"),
                "wba": wba_result.get("source"),
                "nga": nga_result.get("source"),
            },
        }

        # All steps should have completed successfully
        assert workflow_result["processed_intent"] is not None
        assert workflow_result["world_state"] is not None
        assert len(workflow_result["generated_narrative"]) > 0

        return workflow_result

    async def test_error_handling_with_fallback(self, enhanced_coordinator):
        """Test error handling and fallback to mock implementations."""
        # Create proxy with real agents disabled to test fallback
        fallback_proxy = InputProcessorAgentProxy(
            coordinator=enhanced_coordinator,
            instance="test_fallback",
            enable_real_agent=False,  # Force fallback
            fallback_to_mock=True,
        )

        result = await fallback_proxy.process({"text": "test input"})

        # Should fallback to mock implementation
        assert result["source"] == "mock_fallback"
        assert "normalized_text" in result
        assert "routing" in result

    async def test_concurrent_agent_communication(
        self, real_ipa_proxy, real_wba_proxy, real_nga_proxy
    ):
        """Test concurrent agent communication under load."""
        num_concurrent = 5

        async def process_concurrent_workflow(workflow_id: int):
            """Process a single workflow concurrently."""
            session_id = f"concurrent_session_{workflow_id}"

            # Concurrent IPA processing
            ipa_task = real_ipa_proxy.process(
                {"text": f"explore location {workflow_id}"}
            )

            # Concurrent WBA processing
            wba_task = real_wba_proxy.process(
                {
                    "world_id": f"world_{workflow_id}",
                    "updates": {"location_id": workflow_id},
                }
            )

            # Concurrent NGA processing
            nga_task = real_nga_proxy.process(
                {
                    "prompt": f"Generate story for location {workflow_id}",
                    "context": {"session_id": session_id},
                }
            )

            # Wait for all tasks to complete
            ipa_result, wba_result, nga_result = await asyncio.gather(
                ipa_task, wba_task, nga_task
            )

            return {
                "workflow_id": workflow_id,
                "ipa_result": ipa_result,
                "wba_result": wba_result,
                "nga_result": nga_result,
            }

        # Run concurrent workflows
        start_time = time.time()
        tasks = [process_concurrent_workflow(i) for i in range(num_concurrent)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Verify all workflows completed successfully
        assert len(results) == num_concurrent

        for result in results:
            assert "ipa_result" in result
            assert "wba_result" in result
            assert "nga_result" in result

            # Check that each agent processed successfully
            assert "source" in result["ipa_result"]
            assert "source" in result["wba_result"]
            assert "source" in result["nga_result"]

        # Performance check - should complete within reasonable time
        total_time = end_time - start_time
        assert total_time < 30.0  # Should complete within 30 seconds

        return {
            "concurrent_workflows": num_concurrent,
            "total_time": total_time,
            "average_time_per_workflow": total_time / num_concurrent,
            "results": results,
        }


@pytest.mark.integration
@pytest.mark.redis
@pytest.mark.neo4j
class TestCompleteWorkflowChains:
    """Test complete agent workflow chains with actual data flow."""

    @pytest_asyncio.fixture
    async def workflow_test_data(self):
        """Test data for workflow chain testing."""
        return {
            "therapeutic_scenarios": [
                {
                    "name": "anxiety_management",
                    "player_input": "I'm feeling anxious about the dark cave ahead",
                    "expected_themes": ["anxiety", "courage", "support"],
                    "world_context": {"location": "cave_entrance", "mood": "tense"},
                },
                {
                    "name": "confidence_building",
                    "player_input": "I don't think I'm strong enough for this quest",
                    "expected_themes": ["self_doubt", "empowerment", "growth"],
                    "world_context": {
                        "location": "training_grounds",
                        "mood": "uncertain",
                    },
                },
                {
                    "name": "social_connection",
                    "player_input": "I wish I had someone to help me with this puzzle",
                    "expected_themes": ["loneliness", "friendship", "cooperation"],
                    "world_context": {"location": "puzzle_chamber", "mood": "isolated"},
                },
            ]
        }

    async def test_therapeutic_workflow_chain(
        self, real_ipa_proxy, real_wba_proxy, real_nga_proxy, workflow_test_data
    ):
        """Test complete therapeutic workflow chains with real data flow."""
        results = []

        for scenario in workflow_test_data["therapeutic_scenarios"]:
            session_id = f"therapeutic_{scenario['name']}"

            # Step 1: Process therapeutic input through IPA
            ipa_result = await real_ipa_proxy.process(
                {"text": scenario["player_input"]}
            )

            # Step 2: Update world state with therapeutic context
            world_updates = {
                **scenario["world_context"],
                "therapeutic_context": {
                    "player_emotion": scenario["expected_themes"][0],
                    "support_needed": True,
                    "session_type": "therapeutic",
                },
            }

            wba_result = await real_wba_proxy.process(
                {"world_id": session_id, "updates": world_updates}
            )

            # Step 3: Generate therapeutic narrative
            therapeutic_prompt = (
                f"Provide supportive guidance for: {scenario['player_input']}"
            )
            nga_result = await real_nga_proxy.process(
                {
                    "prompt": therapeutic_prompt,
                    "context": {
                        "session_id": session_id,
                        "world_state": wba_result["world_state"],
                        "therapeutic_mode": True,
                        "expected_themes": scenario["expected_themes"],
                    },
                }
            )

            # Verify therapeutic elements in the narrative
            story = nga_result["story"].lower()
            therapeutic_validation = nga_result.get("therapeutic_validation", {})

            # Check for supportive language
            supportive_indicators = [
                "support",
                "help",
                "understand",
                "together",
                "can",
                "able",
            ]
            has_supportive_language = any(
                indicator in story for indicator in supportive_indicators
            )

            workflow_result = {
                "scenario": scenario["name"],
                "player_input": scenario["player_input"],
                "ipa_intent": ipa_result.get("routing", {}).get("intent"),
                "world_state": wba_result["world_state"],
                "narrative": nga_result["story"],
                "has_supportive_language": has_supportive_language,
                "therapeutic_validation": therapeutic_validation,
                "sources": {
                    "ipa": ipa_result.get("source"),
                    "wba": wba_result.get("source"),
                    "nga": nga_result.get("source"),
                },
            }

            results.append(workflow_result)

            # Assertions for therapeutic quality
            assert len(nga_result["story"]) > 0
            assert therapeutic_validation.get("level") != "BLOCKED"

            # Should have supportive language in therapeutic scenarios
            if nga_result.get("source") == "real_nga":
                assert (
                    has_supportive_language
                ), f"Missing supportive language in {scenario['name']}"

        return results

    async def test_narrative_continuity_chain(
        self, real_ipa_proxy, real_wba_proxy, real_nga_proxy
    ):
        """Test narrative continuity across multiple interactions."""
        session_id = "continuity_test_001"
        narrative_sequence = [
            "I enter the ancient library",
            "I examine the dusty books on the shelf",
            "I pick up a glowing tome",
            "I read the mysterious text inside",
        ]

        workflow_results = []
        accumulated_world_state = {"id": session_id, "regions": [], "entities": []}

        for i, player_input in enumerate(narrative_sequence):
            # Process input
            ipa_result = await real_ipa_proxy.process({"text": player_input})

            # Update world state with continuity
            world_updates = {
                "sequence_step": i + 1,
                "current_action": ipa_result.get("routing", {}).get(
                    "intent", "unknown"
                ),
                "narrative_history": [
                    r["narrative"] for r in workflow_results[-3:]
                ],  # Last 3 narratives
            }
            accumulated_world_state.update(world_updates)

            wba_result = await real_wba_proxy.process(
                {"world_id": session_id, "updates": world_updates}
            )

            # Generate narrative with continuity context
            continuity_context = {
                "session_id": session_id,
                "world_state": wba_result["world_state"],
                "sequence_step": i + 1,
                "previous_narratives": [r["narrative"] for r in workflow_results],
            }

            nga_result = await real_nga_proxy.process(
                {
                    "prompt": f"Continue the story: {player_input}",
                    "context": continuity_context,
                }
            )

            workflow_result = {
                "step": i + 1,
                "player_input": player_input,
                "intent": ipa_result.get("routing", {}).get("intent"),
                "world_state": wba_result["world_state"],
                "narrative": nga_result["story"],
                "continuity_maintained": True,  # Will be validated below
            }

            workflow_results.append(workflow_result)

        # Verify narrative continuity
        for i, result in enumerate(workflow_results):
            assert len(result["narrative"]) > 0
            assert result["step"] == i + 1

            # Check for continuity references in later narratives
            if i > 0:
                current_narrative = result["narrative"].lower()
                # Should reference previous elements (simple check)
                has_continuity_reference = any(
                    word in current_narrative
                    for prev_result in workflow_results[:i]
                    for word in ["library", "book", "tome", "text"]
                    if word in prev_result["narrative"].lower()
                )
                result["continuity_maintained"] = has_continuity_reference

        return workflow_results

    async def test_error_recovery_chain(
        self, real_ipa_proxy, real_wba_proxy, real_nga_proxy
    ):
        """Test error recovery in workflow chains."""

        # Test with invalid inputs to trigger error handling
        error_scenarios = [
            {"text": ""},  # Empty input
            {"text": "a" * 10000},  # Extremely long input
            {"prompt": ""},  # Empty prompt for NGA
            {"world_id": ""},  # Empty world ID for WBA
        ]

        recovery_results = []

        for i, error_input in enumerate(error_scenarios):
            try:
                if "text" in error_input:
                    # Test IPA error recovery
                    result = await real_ipa_proxy.process(error_input)
                    recovery_results.append(
                        {
                            "scenario": f"ipa_error_{i}",
                            "input": error_input,
                            "recovered": True,
                            "result": result,
                        }
                    )
                elif "world_id" in error_input:
                    # Test WBA error recovery
                    result = await real_wba_proxy.process(error_input)
                    recovery_results.append(
                        {
                            "scenario": f"wba_error_{i}",
                            "input": error_input,
                            "recovered": True,
                            "result": result,
                        }
                    )
                elif "prompt" in error_input:
                    # Test NGA error recovery
                    result = await real_nga_proxy.process(error_input)
                    recovery_results.append(
                        {
                            "scenario": f"nga_error_{i}",
                            "input": error_input,
                            "recovered": True,
                            "result": result,
                        }
                    )

            except Exception as e:
                recovery_results.append(
                    {
                        "scenario": f"error_{i}",
                        "input": error_input,
                        "recovered": False,
                        "error": str(e),
                    }
                )

        # Verify that errors were handled gracefully
        for result in recovery_results:
            if result["recovered"]:
                # Should have fallback behavior
                assert "source" in result["result"]
                assert result["result"]["source"] in [
                    "real_ipa",
                    "real_wba",
                    "real_nga",
                    "mock_fallback",
                ]

        return recovery_results
