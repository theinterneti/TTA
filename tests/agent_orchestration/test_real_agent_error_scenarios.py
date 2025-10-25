"""
Error scenario testing for real agent communication.

This module tests error handling, failure conditions, and recovery mechanisms
in real agent communication workflows.
"""

import asyncio
import time
from unittest.mock import patch

import pytest
import pytest_asyncio
from tta_ai.orchestration import (
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    WorldBuilderAgentProxy,
)
from tta_ai.orchestration.adapters import AgentCommunicationError
from tta_ai.orchestration.enhanced_coordinator import EnhancedRedisMessageCoordinator


@pytest.mark.integration
@pytest.mark.redis
class TestRealAgentErrorScenarios:
    """Test error scenarios and failure conditions with real agents."""

    @pytest_asyncio.fixture
    async def error_prone_coordinator(self, redis_client):
        """Create coordinator configured for error testing."""
        return EnhancedRedisMessageCoordinator(
            redis=redis_client,
            key_prefix="test_errors",
            enable_real_agents=True,
            fallback_to_mock=True,
            retry_attempts=2,  # Reduced for faster testing
            backoff_base=0.1,  # Faster backoff for testing
        )

    @pytest_asyncio.fixture
    async def no_fallback_ipa(self, error_prone_coordinator):
        """Create IPA proxy without fallback for testing failures."""
        return InputProcessorAgentProxy(
            coordinator=error_prone_coordinator,
            instance="no_fallback",
            enable_real_agent=True,
            fallback_to_mock=False,  # No fallback to test error handling
        )

    @pytest_asyncio.fixture
    async def timeout_ipa(self, error_prone_coordinator):
        """Create IPA proxy with very short timeout."""
        return InputProcessorAgentProxy(
            coordinator=error_prone_coordinator,
            instance="timeout_test",
            default_timeout_s=0.001,  # Very short timeout
            enable_real_agent=True,
            fallback_to_mock=True,
        )

    async def test_communication_timeout_handling(self, timeout_ipa):
        """Test handling of communication timeouts."""
        start_time = time.time()

        try:
            result = await timeout_ipa.process({"text": "test timeout scenario"})

            # Should fallback to mock due to timeout
            assert result["source"] == "mock_fallback"

        except asyncio.TimeoutError:
            # Timeout is also acceptable behavior
            pass

        end_time = time.time()

        # Should not take too long due to short timeout
        assert end_time - start_time < 5.0

    async def test_retry_mechanism_exhaustion(self, no_fallback_ipa):
        """Test behavior when retry mechanism is exhausted."""
        # Mock the adapter to always fail
        with patch.object(no_fallback_ipa, "ipa_adapter") as mock_adapter:
            mock_adapter.process_input.side_effect = AgentCommunicationError(
                "Simulated failure"
            )

            with pytest.raises(AgentCommunicationError):
                await no_fallback_ipa.process({"text": "test retry exhaustion"})

    async def test_malformed_input_handling(self, error_prone_coordinator):
        """Test handling of malformed inputs."""
        proxies = [
            InputProcessorAgentProxy(
                coordinator=error_prone_coordinator,
                enable_real_agent=True,
                fallback_to_mock=True,
            ),
            WorldBuilderAgentProxy(
                coordinator=error_prone_coordinator,
                enable_real_agent=True,
                fallback_to_mock=True,
            ),
            NarrativeGeneratorAgentProxy(
                coordinator=error_prone_coordinator,
                enable_real_agent=True,
                fallback_to_mock=True,
            ),
        ]

        malformed_inputs = [
            None,
            {},
            {"invalid": "structure"},
            {"text": None},
            {"world_id": None},
            {"prompt": None},
            {"text": 12345},  # Wrong type
            {"world_id": []},  # Wrong type
            {"prompt": {"nested": "object"}},  # Wrong type
        ]

        error_results = []

        for proxy in proxies:
            for malformed_input in malformed_inputs:
                try:
                    if isinstance(proxy, InputProcessorAgentProxy):
                        if (
                            malformed_input is None
                            or "text" not in malformed_input
                            or not malformed_input.get("text")
                        ):
                            # Should raise ValueError for missing text
                            with pytest.raises(ValueError):
                                await proxy.process(malformed_input)
                            error_results.append(
                                {
                                    "proxy": "IPA",
                                    "input": malformed_input,
                                    "handled": True,
                                }
                            )
                        else:
                            result = await proxy.process(malformed_input)
                            error_results.append(
                                {
                                    "proxy": "IPA",
                                    "input": malformed_input,
                                    "result": result,
                                }
                            )

                    elif isinstance(proxy, WorldBuilderAgentProxy):
                        if (
                            malformed_input is None
                            or "world_id" not in malformed_input
                            or not malformed_input.get("world_id")
                        ):
                            # Should raise ValueError for missing world_id
                            with pytest.raises(ValueError):
                                await proxy.process(malformed_input)
                            error_results.append(
                                {
                                    "proxy": "WBA",
                                    "input": malformed_input,
                                    "handled": True,
                                }
                            )
                        else:
                            result = await proxy.process(malformed_input)
                            error_results.append(
                                {
                                    "proxy": "WBA",
                                    "input": malformed_input,
                                    "result": result,
                                }
                            )

                    elif isinstance(proxy, NarrativeGeneratorAgentProxy):
                        if (
                            malformed_input is None
                            or "prompt" not in malformed_input
                            or not malformed_input.get("prompt")
                        ):
                            # Should raise ValueError for missing prompt
                            with pytest.raises(ValueError):
                                await proxy.process(malformed_input)
                            error_results.append(
                                {
                                    "proxy": "NGA",
                                    "input": malformed_input,
                                    "handled": True,
                                }
                            )
                        else:
                            result = await proxy.process(malformed_input)
                            error_results.append(
                                {
                                    "proxy": "NGA",
                                    "input": malformed_input,
                                    "result": result,
                                }
                            )

                except Exception as e:
                    error_results.append(
                        {
                            "proxy": proxy.__class__.__name__,
                            "input": malformed_input,
                            "error": str(e),
                            "handled": False,
                        }
                    )

        # Verify that errors were handled appropriately
        handled_count = sum(
            1 for result in error_results if result.get("handled", False)
        )
        assert handled_count > 0, "Should have handled some malformed inputs"

        return error_results

    async def test_concurrent_failure_scenarios(self, error_prone_coordinator):
        """Test behavior under concurrent failure conditions."""
        num_concurrent = 10
        failure_rate = 0.3  # 30% of requests should fail

        # Create proxies with mixed configurations
        proxies = [
            InputProcessorAgentProxy(
                coordinator=error_prone_coordinator,
                instance=f"concurrent_{i}",
                enable_real_agent=True,
                fallback_to_mock=i % 2 == 0,  # Half with fallback, half without
            )
            for i in range(num_concurrent)
        ]

        async def process_with_potential_failure(proxy_id: int):
            """Process request with potential failure simulation."""
            proxy = proxies[proxy_id]

            # Simulate random failures
            import random

            if random.random() < failure_rate:
                # Mock the adapter to fail
                with patch.object(proxy, "ipa_adapter") as mock_adapter:
                    mock_adapter.process_input.side_effect = AgentCommunicationError(
                        "Simulated concurrent failure"
                    )

                    try:
                        result = await proxy.process(
                            {"text": f"concurrent test {proxy_id}"}
                        )
                        return {"proxy_id": proxy_id, "success": True, "result": result}
                    except Exception as e:
                        return {"proxy_id": proxy_id, "success": False, "error": str(e)}
            else:
                # Normal processing
                try:
                    result = await proxy.process(
                        {"text": f"concurrent test {proxy_id}"}
                    )
                    return {"proxy_id": proxy_id, "success": True, "result": result}
                except Exception as e:
                    return {"proxy_id": proxy_id, "success": False, "error": str(e)}

        # Run concurrent requests
        start_time = time.time()
        tasks = [process_with_potential_failure(i) for i in range(num_concurrent)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Analyze results
        successful_results = [
            r for r in results if isinstance(r, dict) and r.get("success", False)
        ]
        failed_results = [
            r for r in results if isinstance(r, dict) and not r.get("success", True)
        ]
        exception_results = [r for r in results if isinstance(r, Exception)]

        # Should have some successful results even with failures
        assert len(successful_results) > 0, "Should have some successful results"

        # Should complete within reasonable time even with failures
        total_time = end_time - start_time
        assert total_time < 30.0, f"Concurrent processing took too long: {total_time}s"

        return {
            "total_requests": num_concurrent,
            "successful": len(successful_results),
            "failed": len(failed_results),
            "exceptions": len(exception_results),
            "total_time": total_time,
            "success_rate": len(successful_results) / num_concurrent,
        }

    async def test_resource_exhaustion_handling(self, error_prone_coordinator):
        """Test handling of resource exhaustion scenarios."""
        # Create many proxies to simulate resource pressure
        num_proxies = 50
        proxies = [
            InputProcessorAgentProxy(
                coordinator=error_prone_coordinator,
                instance=f"resource_test_{i}",
                enable_real_agent=True,
                fallback_to_mock=True,
            )
            for i in range(num_proxies)
        ]

        # Process requests rapidly to create resource pressure
        async def rapid_processing(proxy_id: int):
            """Rapidly process multiple requests."""
            proxy = proxies[proxy_id]
            results = []

            for j in range(5):  # 5 requests per proxy
                try:
                    result = await proxy.process(
                        {"text": f"resource test {proxy_id}-{j}"}
                    )
                    results.append({"success": True, "source": result.get("source")})
                except Exception as e:
                    results.append({"success": False, "error": str(e)})

            return results

        # Execute rapid processing
        start_time = time.time()
        tasks = [rapid_processing(i) for i in range(num_proxies)]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Flatten results
        flattened_results = []
        for proxy_results in all_results:
            if isinstance(proxy_results, list):
                flattened_results.extend(proxy_results)
            else:
                flattened_results.append(
                    {"success": False, "error": str(proxy_results)}
                )

        # Analyze resource handling
        successful_count = sum(1 for r in flattened_results if r.get("success", False))
        fallback_count = sum(
            1 for r in flattened_results if r.get("source") == "mock_fallback"
        )

        total_requests = num_proxies * 5
        success_rate = successful_count / total_requests
        fallback_rate = fallback_count / total_requests

        # Should maintain reasonable success rate even under pressure
        assert (
            success_rate > 0.5
        ), f"Success rate too low under resource pressure: {success_rate}"

        # Should complete within reasonable time
        total_time = end_time - start_time
        assert (
            total_time < 60.0
        ), f"Resource exhaustion test took too long: {total_time}s"

        return {
            "total_requests": total_requests,
            "successful": successful_count,
            "fallback_used": fallback_count,
            "success_rate": success_rate,
            "fallback_rate": fallback_rate,
            "total_time": total_time,
            "requests_per_second": total_requests / total_time,
        }

    async def test_network_partition_simulation(self, error_prone_coordinator):
        """Test behavior during simulated network partitions."""
        # Create proxy for network partition testing
        partition_proxy = InputProcessorAgentProxy(
            coordinator=error_prone_coordinator,
            instance="partition_test",
            enable_real_agent=True,
            fallback_to_mock=True,
        )

        # Simulate network partition by making adapter unavailable
        with patch.object(partition_proxy, "ipa_adapter") as mock_adapter:
            mock_adapter._available = False
            mock_adapter.process_input.side_effect = AgentCommunicationError(
                "Network partition"
            )

            # Should fallback gracefully
            result = await partition_proxy.process({"text": "test during partition"})

            # Should use fallback
            assert result["source"] == "mock_fallback"
            assert "normalized_text" in result
            assert result["normalized_text"] == "test during partition"

        # After "partition" is resolved, should work normally
        normal_result = await partition_proxy.process({"text": "test after partition"})
        assert "source" in normal_result

        return {
            "partition_handled": True,
            "fallback_result": result,
            "recovery_result": normal_result,
        }
