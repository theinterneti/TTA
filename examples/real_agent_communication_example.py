"""

# Logseq: [[TTA.dev/Examples/Real_agent_communication_example]]
Example demonstrating enhanced agent proxy integration with real communication protocols.

This example shows how to use the enhanced agent proxies with real agent communication,
including complete IPA → WBA → NGA workflow chains and performance monitoring.
"""

import asyncio
import logging
from typing import Any

from tta_ai.orchestration import (
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    WorldBuilderAgentProxy,
)
from tta_ai.orchestration.config.real_agent_config import get_real_agent_config
from tta_ai.orchestration.enhanced_coordinator import (
    EnhancedRedisMessageCoordinator,
    ScalableWorkflowCoordinator,
)
from tta_ai.orchestration.monitoring import AlertManager, get_system_monitor
from tta_ai.orchestration.profiling import AgentCoordinationProfiler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_enhanced_coordination():
    """Set up enhanced coordination with real agent communication."""
    # Get configuration
    config = get_real_agent_config()

    # Create Redis client (you'll need to provide your Redis connection)
    import redis.asyncio as redis

    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

    # Create enhanced coordinator
    return EnhancedRedisMessageCoordinator(
        redis=redis_client,
        key_prefix="example_real_agents",
        enable_real_agents=config.enable_real_agents,
        fallback_to_mock=config.fallback_to_mock,
        retry_attempts=config.max_retries,
        backoff_base=config.base_delay,
        backoff_factor=config.exponential_base,
        backoff_max=config.max_delay,
    )


async def create_enhanced_proxies(coordinator):
    """Create enhanced agent proxies with real communication."""
    config = get_real_agent_config()

    # Create enhanced proxies
    ipa_proxy = InputProcessorAgentProxy(
        coordinator=coordinator,
        instance="example_ipa",
        enable_real_agent=config.enable_real_agents,
        fallback_to_mock=config.fallback_to_mock,
        default_timeout_s=config.ipa_timeout_s,
    )

    wba_proxy = WorldBuilderAgentProxy(
        coordinator=coordinator,
        instance="example_wba",
        enable_real_agent=config.enable_real_agents,
        fallback_to_mock=config.fallback_to_mock,
        default_timeout_s=config.wba_timeout_s,
        neo4j_manager=None,  # Provide your Neo4j manager here
    )

    nga_proxy = NarrativeGeneratorAgentProxy(
        coordinator=coordinator,
        instance="example_nga",
        enable_real_agent=config.enable_real_agents,
        fallback_to_mock=config.fallback_to_mock,
        default_timeout_s=config.nga_timeout_s,
    )

    return ipa_proxy, wba_proxy, nga_proxy


async def demonstrate_single_agent_communication():
    """Demonstrate communication with individual agents."""
    logger.info("=== Single Agent Communication Demo ===")

    coordinator = await setup_enhanced_coordination()
    ipa_proxy, wba_proxy, nga_proxy = await create_enhanced_proxies(coordinator)

    # Test IPA communication
    logger.info("Testing IPA communication...")
    ipa_result = await ipa_proxy.process(
        {"text": "I want to explore the mysterious ancient temple"}
    )
    logger.info(f"IPA Result: {ipa_result}")

    # Test WBA communication
    logger.info("Testing WBA communication...")
    wba_result = await wba_proxy.process(
        {
            "world_id": "demo_world_001",
            "updates": {
                "current_location": "ancient_temple",
                "player_action": ipa_result.get("routing", {}).get("intent", "explore"),
            },
        }
    )
    logger.info(f"WBA Result: {wba_result}")

    # Test NGA communication
    logger.info("Testing NGA communication...")
    nga_result = await nga_proxy.process(
        {
            "prompt": "Generate a story about exploring an ancient temple",
            "context": {
                "session_id": "demo_session_001",
                "world_state": wba_result.get("world_state", {}),
                "player_intent": ipa_result.get("routing", {}).get("intent"),
            },
        }
    )
    logger.info(f"NGA Result: {nga_result}")

    return ipa_result, wba_result, nga_result


async def demonstrate_complete_workflow():
    """Demonstrate complete IPA → WBA → NGA workflow chain."""
    logger.info("=== Complete Workflow Demo ===")

    coordinator = await setup_enhanced_coordination()

    # Create scalable workflow coordinator
    workflow_coordinator = ScalableWorkflowCoordinator(
        enhanced_coordinator=coordinator,
        max_concurrent_workflows=10,
        workflow_timeout_s=60.0,
        enable_batching=True,
    )

    # Define workflow steps
    workflow_steps = [
        {
            "type": "ipa",
            "config": {
                "text": "I carefully examine the ancient runes on the temple wall"
            },
            "update_context": True,
        },
        {
            "type": "wba",
            "config": {
                "world_id": "workflow_demo_world",
                "updates": {"discovered_runes": True, "location": "temple_wall"},
            },
            "update_context": True,
        },
        {
            "type": "nga",
            "config": {
                "prompt": "Continue the story based on the player examining ancient runes"
            },
            "update_context": True,
        },
    ]

    # Execute workflow
    workflow_result = await workflow_coordinator.execute_workflow(
        workflow_id="demo_workflow_001",
        workflow_steps=workflow_steps,
        context={"session_id": "demo_session_002"},
    )

    logger.info(f"Workflow Result: {workflow_result}")
    return workflow_result


async def demonstrate_concurrent_workflows():
    """Demonstrate concurrent workflow execution."""
    logger.info("=== Concurrent Workflows Demo ===")

    coordinator = await setup_enhanced_coordination()
    workflow_coordinator = ScalableWorkflowCoordinator(
        enhanced_coordinator=coordinator,
        max_concurrent_workflows=5,
        enable_batching=True,
    )

    # Create multiple concurrent workflows
    async def run_workflow(workflow_id: int):
        """Run a single workflow."""
        steps = [
            {
                "type": "ipa",
                "config": {"text": f"Player {workflow_id} explores the dungeon"},
                "update_context": True,
            },
            {
                "type": "wba",
                "config": {
                    "world_id": f"concurrent_world_{workflow_id}",
                    "updates": {"player_id": workflow_id, "location": "dungeon"},
                },
                "update_context": True,
            },
            {
                "type": "nga",
                "config": {
                    "prompt": f"Generate story for player {workflow_id} in dungeon"
                },
                "update_context": True,
            },
        ]

        return await workflow_coordinator.execute_workflow(
            workflow_id=f"concurrent_workflow_{workflow_id}",
            workflow_steps=steps,
            context={"session_id": f"concurrent_session_{workflow_id}"},
        )

    # Run 3 concurrent workflows
    tasks = [run_workflow(i) for i in range(3)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    logger.info(f"Concurrent workflow results: {len(results)} completed")
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Workflow {i} failed: {result}")
        else:
            logger.info(f"Workflow {i} succeeded")

    return results


async def demonstrate_monitoring_and_profiling():
    """Demonstrate monitoring and profiling capabilities."""
    logger.info("=== Monitoring and Profiling Demo ===")

    # Get system monitor
    system_monitor = get_system_monitor()

    # Set up alert manager
    async def alert_handler(alert: dict[str, Any]):
        """Handle alerts."""
        logger.warning(f"ALERT: {alert['message']} (Severity: {alert['severity']})")

    alert_manager = AlertManager([alert_handler])

    # Set up profiler
    profiler = AgentCoordinationProfiler()

    # Run some operations to generate metrics
    coordinator = await setup_enhanced_coordination()
    ipa_proxy, wba_proxy, nga_proxy = await create_enhanced_proxies(coordinator)

    # Profile concurrent operations
    async def coordination_func(request_id: int):
        """Function to profile."""
        await ipa_proxy.process({"text": f"profiling test {request_id}"})
        await wba_proxy.process({"world_id": f"profile_world_{request_id}"})
        await nga_proxy.process(
            {
                "prompt": f"profiling story {request_id}",
                "context": {"session_id": f"profile_session_{request_id}"},
            }
        )

    # Profile at different concurrency levels
    concurrency_results = await profiler.profile_concurrent_coordination(
        coordination_func, [1, 3, 5], requests_per_level=10
    )

    logger.info("Profiling Results:")
    for concurrency, metrics in concurrency_results.items():
        logger.info(
            f"  Concurrency {concurrency}: "
            f"{metrics.throughput_rps:.2f} RPS, "
            f"{metrics.average_response_time:.3f}s avg response time"
        )

    # Check for alerts
    await alert_manager.check_alerts(system_monitor)

    # Get system metrics
    system_metrics = system_monitor.get_system_metrics()
    agent_metrics = system_monitor.get_all_agent_metrics()

    logger.info(f"System Metrics: {system_metrics}")
    logger.info(f"Agent Metrics: {len(agent_metrics)} agents monitored")

    return concurrency_results, system_metrics, agent_metrics


async def main():
    """Main demonstration function."""
    logger.info("Starting Enhanced Agent Proxy Integration Demo")

    try:
        # Demonstrate single agent communication
        await demonstrate_single_agent_communication()

        # Demonstrate complete workflow
        await demonstrate_complete_workflow()

        # Demonstrate concurrent workflows
        await demonstrate_concurrent_workflows()

        # Demonstrate monitoring and profiling
        await demonstrate_monitoring_and_profiling()

        logger.info("Demo completed successfully!")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
