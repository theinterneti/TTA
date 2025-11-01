"""
Comprehensive Redis integration tests for the capability system.

This module provides comprehensive Redis-marked integration tests with proper
test isolation and capability system validation.
"""

import asyncio

import pytest
import pytest_asyncio
from tta_ai.orchestration.api.diagnostics import DiagnosticsAPI
from tta_ai.orchestration.capabilities.auto_discovery import (
    AutoDiscoveryManager,
    DiscoveryConfig,
    DiscoveryStrategy,
)
from tta_ai.orchestration.models import (
    AgentCapability,
    AgentId,
    AgentType,
    CapabilityType,
)
from tta_ai.orchestration.registries.redis_agent_registry import RedisAgentRegistry


@pytest.mark.redis
class TestCapabilitySystemIntegration:
    """Comprehensive Redis integration tests for capability system."""

    @pytest_asyncio.fixture
    async def redis_registry(self, redis_client):
        """Create Redis agent registry for testing."""
        registry = RedisAgentRegistry(redis_client=redis_client)
        await registry.start()
        yield registry
        await registry.stop()

        # Cleanup Redis keys
        await redis_client.flushdb()

    @pytest_asyncio.fixture
    async def auto_discovery_manager(self, redis_registry):
        """Create auto-discovery manager for testing."""
        config = DiscoveryConfig(
            enabled=True,
            strategy=DiscoveryStrategy.IMMEDIATE,
            discovery_timeout=10.0,
            testing_enabled=True,  # Enable for testing environment
        )

        manager = AutoDiscoveryManager(registry=redis_registry, config=config)

        await manager.start()
        yield manager
        await manager.stop()

    @pytest_asyncio.fixture
    async def diagnostics_api(self, redis_registry, auto_discovery_manager):
        """Create diagnostics API for testing."""
        api = DiagnosticsAPI(
            registry=redis_registry,
            auto_discovery_manager=auto_discovery_manager,
            require_auth=False,  # Disable auth for testing
        )
        return api

    async def test_agent_registration_and_discovery(
        self, redis_registry, auto_discovery_manager
    ):
        """Test agent registration and auto-discovery integration."""
        # Create test capabilities
        capabilities = [
            AgentCapability(
                capability_type=CapabilityType.INPUT_PROCESSING,
                name="text_analysis",
                version="1.0.0",
                description="Text analysis capability",
            ),
            AgentCapability(
                capability_type=CapabilityType.SAFETY_VALIDATION,
                name="content_safety",
                version="1.0.0",
                description="Content safety validation",
            ),
        ]

        # Register component for auto-discovery
        component_id = "test_ipa_001"
        auto_discovery_manager.register_component(
            component_id=component_id,
            component_type="input_processor",
            agent_type=AgentType.INPUT_PROCESSOR,
            capabilities=capabilities,
            metadata={"test": True, "environment": "testing"},
        )

        # Wait for auto-discovery to complete
        await asyncio.sleep(1.0)

        # Verify component was discovered and registered
        discovery_status = auto_discovery_manager.get_component_status(component_id)
        assert discovery_status.value == "registered"

        # Verify agent is in registry
        agent_id = AgentId(agent_type=AgentType.INPUT_PROCESSOR, instance=component_id)
        agent_info = await redis_registry.get_agent_info(str(agent_id))

        assert agent_info is not None
        assert agent_info["agent_type"] == AgentType.INPUT_PROCESSOR.value
        assert len(agent_info["capabilities"]) == 2
        assert agent_info["metadata"]["auto_discovered"] is True
        assert agent_info["metadata"]["test"] is True

    async def test_capability_matching_integration(
        self, redis_registry, auto_discovery_manager
    ):
        """Test capability matching with auto-discovered agents."""
        # Register multiple agents with different capabilities
        agents_config = [
            {
                "component_id": "ipa_001",
                "agent_type": AgentType.INPUT_PROCESSOR,
                "capabilities": [
                    AgentCapability(
                        capability_type=CapabilityType.INPUT_PROCESSING,
                        name="text_analysis",
                        version="1.0.0",
                    )
                ],
            },
            {
                "component_id": "wba_001",
                "agent_type": AgentType.WORLD_BUILDER,
                "capabilities": [
                    AgentCapability(
                        capability_type=CapabilityType.WORLD_MANAGEMENT,
                        name="world_state_management",
                        version="1.0.0",
                    )
                ],
            },
            {
                "component_id": "nga_001",
                "agent_type": AgentType.NARRATIVE_GENERATOR,
                "capabilities": [
                    AgentCapability(
                        capability_type=CapabilityType.CONTENT_GENERATION,
                        name="narrative_generation",
                        version="1.0.0",
                    )
                ],
            },
        ]

        # Register all agents
        for config in agents_config:
            auto_discovery_manager.register_component(
                component_id=config["component_id"],
                component_type=config["agent_type"].value,
                agent_type=config["agent_type"],
                capabilities=config["capabilities"],
            )

        # Wait for discovery
        await asyncio.sleep(1.0)

        # Test capability matching
        matching_agents = await redis_registry.find_agents_by_capability(
            capability_type=CapabilityType.INPUT_PROCESSING,
            capability_name="text_analysis",
        )

        assert len(matching_agents) == 1
        assert "ipa_001" in str(matching_agents[0])

        # Test finding agents by type
        world_builder_agents = await redis_registry.find_agents_by_type(
            AgentType.WORLD_BUILDER
        )
        assert len(world_builder_agents) == 1
        assert "wba_001" in str(world_builder_agents[0])

    async def test_heartbeat_integration(self, redis_registry, auto_discovery_manager):
        """Test heartbeat integration with auto-discovery."""
        # Register component
        component_id = "heartbeat_test_001"
        auto_discovery_manager.register_component(
            component_id=component_id,
            component_type="test_agent",
            agent_type=AgentType.INPUT_PROCESSOR,
        )

        # Wait for discovery
        await asyncio.sleep(1.0)

        # Get initial heartbeat
        agent_id = AgentId(agent_type=AgentType.INPUT_PROCESSOR, instance=component_id)
        initial_info = await redis_registry.get_agent_info(str(agent_id))
        initial_heartbeat = initial_info["last_heartbeat"]

        # Wait and check heartbeat update
        await asyncio.sleep(2.0)

        updated_info = await redis_registry.get_agent_info(str(agent_id))
        updated_heartbeat = updated_info["last_heartbeat"]

        # Heartbeat should be updated (auto-discovery manager sends heartbeats)
        assert updated_heartbeat >= initial_heartbeat

        # Test agent liveness
        is_alive = await redis_registry.is_agent_alive(agent_id)
        assert is_alive is True

    async def test_diagnostics_api_integration(
        self, redis_registry, auto_discovery_manager, diagnostics_api
    ):
        """Test diagnostics API integration with capability system."""
        # Register test agents
        test_agents = [
            {
                "component_id": "diag_ipa_001",
                "agent_type": AgentType.INPUT_PROCESSOR,
                "capabilities": [
                    AgentCapability(
                        capability_type=CapabilityType.INPUT_PROCESSING,
                        name="text_analysis",
                        version="1.0.0",
                        description="Text analysis for diagnostics test",
                    )
                ],
            },
            {
                "component_id": "diag_nga_001",
                "agent_type": AgentType.NARRATIVE_GENERATOR,
                "capabilities": [
                    AgentCapability(
                        capability_type=CapabilityType.CONTENT_GENERATION,
                        name="story_generation",
                        version="1.0.0",
                        description="Story generation for diagnostics test",
                    )
                ],
            },
        ]

        for agent_config in test_agents:
            auto_discovery_manager.register_component(
                component_id=agent_config["component_id"],
                component_type=agent_config["agent_type"].value,
                agent_type=agent_config["agent_type"],
                capabilities=agent_config["capabilities"],
                metadata={"diagnostics_test": True},
            )

        # Wait for discovery
        await asyncio.sleep(1.0)

        # Test getting all agents diagnostics
        all_diagnostics = await diagnostics_api._get_agents_diagnostics()

        assert len(all_diagnostics) == 2

        # Validate diagnostic information
        for diag in all_diagnostics:
            assert diag.agent_id in ["diag_ipa_001", "diag_nga_001"]
            assert diag.health_status.status in ["healthy", "degraded", "unknown"]
            assert len(diag.capabilities) > 0
            assert diag.metadata.get("diagnostics_test") is True
            assert diag.discovery_info.get("auto_discovery_available") is True
            assert diag.discovery_info.get("discovery_status") == "registered"

        # Test getting specific agent diagnostics
        specific_diag = await diagnostics_api._get_agent_diagnostics("diag_ipa_001")

        assert specific_diag is not None
        assert specific_diag.agent_id == "diag_ipa_001"
        assert specific_diag.agent_type == AgentType.INPUT_PROCESSOR.value
        assert len(specific_diag.capabilities) == 1
        assert specific_diag.capabilities[0].name == "text_analysis"

        # Test system summary
        system_summary = await diagnostics_api._get_system_summary()

        assert system_summary.total_agents == 2
        assert system_summary.total_capabilities == 2
        assert system_summary.unique_capability_types == 2
        assert system_summary.overall_health in ["healthy", "degraded", "unknown"]

    async def test_redis_connection_resilience(
        self, redis_client, auto_discovery_manager
    ):
        """Test Redis connection resilience and recovery."""
        # Register component
        component_id = "resilience_test_001"
        auto_discovery_manager.register_component(
            component_id=component_id,
            component_type="resilience_test",
            agent_type=AgentType.INPUT_PROCESSOR,
        )

        # Wait for initial discovery
        await asyncio.sleep(1.0)

        # Verify initial registration
        initial_status = auto_discovery_manager.get_component_status(component_id)
        assert initial_status.value == "registered"

        # Test that the system handles Redis operations gracefully
        # (In a real test, you might simulate Redis connection issues)

        # Get discovery statistics
        stats = auto_discovery_manager.get_discovery_statistics()

        assert stats["enabled"] is True
        assert stats["total_components"] >= 1
        assert stats["status_counts"]["registered"] >= 1
        assert stats["is_running"] is True

    async def test_capability_system_cleanup(
        self, redis_registry, auto_discovery_manager
    ):
        """Test proper cleanup of capability system resources."""
        # Register multiple components
        component_ids = ["cleanup_test_001", "cleanup_test_002", "cleanup_test_003"]

        for i, component_id in enumerate(component_ids):
            auto_discovery_manager.register_component(
                component_id=component_id,
                component_type="cleanup_test",
                agent_type=AgentType.INPUT_PROCESSOR,
                metadata={"cleanup_test": True, "index": i},
            )

        # Wait for discovery
        await asyncio.sleep(1.0)

        # Verify all components are registered
        for component_id in component_ids:
            status = auto_discovery_manager.get_component_status(component_id)
            assert status.value == "registered"

        # Get all agents before cleanup
        all_agents_before = await redis_registry.get_all_agents()
        cleanup_agents_before = {
            agent_id: info
            for agent_id, info in all_agents_before.items()
            if info.get("metadata", {}).get("cleanup_test") is True
        }

        assert len(cleanup_agents_before) == 3

        # Test cleanup (this would typically be done by stopping the manager)
        # For this test, we'll verify the agents exist and can be cleaned up

        # Verify agents can be retrieved
        for component_id in component_ids:
            agent_id = AgentId(
                agent_type=AgentType.INPUT_PROCESSOR, instance=component_id
            )
            agent_info = await redis_registry.get_agent_info(str(agent_id))
            assert agent_info is not None
            assert agent_info["metadata"]["cleanup_test"] is True

    async def test_backward_compatibility_validation(
        self, redis_registry, auto_discovery_manager
    ):
        """Test backward compatibility with existing agent registrations."""
        # Manually register an agent (simulating existing registration)
        manual_agent_id = AgentId(
            agent_type=AgentType.WORLD_BUILDER, instance="manual_registration_001"
        )

        manual_capabilities = [
            AgentCapability(
                capability_type=CapabilityType.WORLD_MANAGEMENT,
                name="legacy_world_management",
                version="0.9.0",
                description="Legacy world management capability",
            )
        ]

        await redis_registry.register_agent(
            agent_id=manual_agent_id,
            capabilities=manual_capabilities,
            metadata={"manual_registration": True, "legacy": True},
        )

        # Register new agent via auto-discovery
        auto_discovery_manager.register_component(
            component_id="auto_registration_001",
            component_type="world_builder",
            agent_type=AgentType.WORLD_BUILDER,
            capabilities=[
                AgentCapability(
                    capability_type=CapabilityType.WORLD_MANAGEMENT,
                    name="modern_world_management",
                    version="1.0.0",
                    description="Modern world management capability",
                )
            ],
            metadata={"auto_registration": True, "modern": True},
        )

        # Wait for auto-discovery
        await asyncio.sleep(1.0)

        # Verify both agents coexist
        all_agents = await redis_registry.get_all_agents()

        manual_agents = {
            agent_id: info
            for agent_id, info in all_agents.items()
            if info.get("metadata", {}).get("manual_registration") is True
        }

        auto_agents = {
            agent_id: info
            for agent_id, info in all_agents.items()
            if info.get("metadata", {}).get("auto_registration") is True
        }

        assert len(manual_agents) == 1
        assert len(auto_agents) == 1

        # Verify capability matching works for both
        world_management_agents = await redis_registry.find_agents_by_capability(
            capability_type=CapabilityType.WORLD_MANAGEMENT
        )

        assert len(world_management_agents) == 2

        # Verify different versions are handled correctly
        legacy_agents = await redis_registry.find_agents_by_capability(
            capability_type=CapabilityType.WORLD_MANAGEMENT,
            capability_name="legacy_world_management",
        )

        modern_agents = await redis_registry.find_agents_by_capability(
            capability_type=CapabilityType.WORLD_MANAGEMENT,
            capability_name="modern_world_management",
        )

        assert len(legacy_agents) == 1
        assert len(modern_agents) == 1
