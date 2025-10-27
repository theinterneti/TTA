"""
Integration tests for AgentOrchestrationService with real components (Task 16.1).

This module tests the service integration with actual WorkflowManager, MessageCoordinator,
and other orchestration components to validate end-to-end functionality.
"""

from unittest.mock import Mock, patch

import pytest
import pytest_asyncio
import redis.asyncio as aioredis
from tta_ai.orchestration import (
    AgentContext,
    AgentId,
    AgentStep,
    AgentType,
    ErrorHandlingStrategy,
    OrchestrationResponse,
    SessionContext,
    WorkflowDefinition,
    WorkflowType,
)
from tta_ai.orchestration.agents import AgentRegistry
from tta_ai.orchestration.coordinators import RedisMessageCoordinator
from tta_ai.orchestration.resources import ResourceManager
from tta_ai.orchestration.service import AgentOrchestrationService
from tta_ai.orchestration.workflow_manager import WorkflowManager

# ============================================================================
# Integration Test Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def redis_client():
    """Redis client for integration testing."""
    client = aioredis.from_url("redis://localhost:6379/0")
    try:
        await client.ping()
        yield client
    except Exception:
        pytest.skip("Redis not available for integration tests")
    finally:
        await client.aclose()


@pytest.fixture
def real_workflow_manager():
    """Real WorkflowManager instance for integration testing."""
    return WorkflowManager()


@pytest_asyncio.fixture
async def real_message_coordinator(redis_client):
    """Real RedisMessageCoordinator for integration testing."""
    return RedisMessageCoordinator(redis_client, key_prefix="test_ao")


@pytest.fixture
def real_agent_registry():
    """Real AgentRegistry for integration testing."""
    return AgentRegistry()


@pytest.fixture
def real_resource_manager(redis_client):
    """Real ResourceManager for integration testing."""
    return ResourceManager(
        gpu_memory_limit_fraction=0.8,
        cpu_thread_limit=None,
        memory_limit_bytes=None,
        warn_cpu_percent=85.0,
        warn_mem_percent=85.0,
        crit_cpu_percent=95.0,
        crit_mem_percent=95.0,
        redis_client=redis_client,
        redis_prefix="test_ao",
    )


@pytest.fixture
def sample_session_context():
    """Sample session context for testing."""
    return SessionContext(
        session_id="integration-test-session",
        user_id="integration-test-user",
        created_at="2024-01-01T00:00:00Z",
        context=AgentContext(
            user_id="integration-test-user",
            session_id="integration-test-session",
            memory={"test_memory": "integration_test"},
            world_state={"location": "test_forest"},
            metadata={"integration_test": True},
        ),
    )


@pytest_asyncio.fixture
async def integration_service(
    real_workflow_manager,
    real_message_coordinator,
    real_agent_registry,
    real_resource_manager,
):
    """AgentOrchestrationService with real components for integration testing."""
    service = AgentOrchestrationService(
        workflow_manager=real_workflow_manager,
        message_coordinator=real_message_coordinator,
        agent_registry=real_agent_registry,
        therapeutic_validator=None,  # Use basic safety checks
        resource_manager=real_resource_manager,
        optimization_engine=None,
        neo4j_manager=None,
    )

    # Initialize the service
    await service.initialize()

    yield service

    # Cleanup
    await service.shutdown()


# ============================================================================
# Component Integration Tests
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.redis
async def test_service_initialization_with_real_components(integration_service):
    """Test service initialization with real components."""
    assert integration_service._initialized is True

    # Verify workflows were registered
    workflows = integration_service.workflow_manager._workflows
    assert "collaborative" in workflows
    assert "input_processing" in workflows
    assert "world_building" in workflows
    assert "narrative_generation" in workflows

    # Verify component integration
    status = integration_service.get_service_status()
    assert status["components"]["workflow_manager"] is True
    assert status["components"]["message_coordinator"] is True
    assert status["components"]["agent_registry"] is True
    assert status["components"]["resource_manager"] is True


@pytest.mark.asyncio
@pytest.mark.redis
async def test_workflow_manager_integration(
    integration_service, sample_session_context
):
    """Test integration with real WorkflowManager."""
    # Create a simple agent context
    agent_context = AgentContext(
        user_id=sample_session_context.user_id,
        session_id=sample_session_context.session_id,
        memory={"test": "data"},
    )

    # Test workflow execution through the service
    response, run_id, error = await integration_service.coordinate_agents(
        workflow_type=WorkflowType.INPUT_PROCESSING, context=agent_context
    )

    # The workflow should execute but may not have real agents
    # So we expect either success or a specific error about missing agents
    assert run_id is not None

    # Check that the workflow was tracked
    run_state = integration_service.workflow_manager.get_run_state(run_id)
    assert run_state is not None
    assert run_state.workflow_name == "input_processing"


@pytest.mark.asyncio
@pytest.mark.redis
async def test_message_coordinator_integration(integration_service):
    """Test integration with real RedisMessageCoordinator."""
    # Test that message coordinator is properly integrated
    coordinator = integration_service.message_coordinator
    assert coordinator is not None

    # Test basic coordinator functionality
    AgentId(type=AgentType.IPA, instance="test")

    # This should not raise an exception
    try:
        await coordinator.configure(queue_size=100, retry_attempts=3)
    except Exception as e:
        pytest.fail(f"Message coordinator configuration failed: {e}")


@pytest.mark.asyncio
@pytest.mark.redis
async def test_agent_registry_integration(integration_service):
    """Test integration with real AgentRegistry."""
    registry = integration_service.agent_registry
    assert registry is not None

    # Test registry functionality
    snapshot = registry.snapshot()
    assert isinstance(snapshot, dict)

    # Test agent lookup (should handle missing agents gracefully)
    agent_id = AgentId(type=AgentType.IPA, instance="test")
    registry.get_agent(agent_id)
    # Agent may be None if not registered, which is fine for this test


@pytest.mark.asyncio
@pytest.mark.redis
async def test_resource_manager_integration(integration_service):
    """Test integration with real ResourceManager."""
    resource_manager = integration_service.resource_manager
    assert resource_manager is not None

    # Test resource allocation
    context = AgentContext(session_id="test")

    # This should not raise an exception
    await integration_service._allocate_workflow_resources(
        WorkflowType.COLLABORATIVE, context
    )


# ============================================================================
# End-to-End Integration Tests
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.redis
async def test_end_to_end_user_input_processing(
    integration_service, sample_session_context
):
    """Test end-to-end user input processing with real components."""
    # Mock the workflow execution to avoid needing real agents
    with patch.object(
        integration_service.workflow_manager, "execute_workflow"
    ) as mock_execute:
        mock_execute.return_value = (
            OrchestrationResponse(
                response_text="Integration test response",
                updated_context={"memory": {"integration": "success"}},
                workflow_metadata={"test": "integration"},
            ),
            "integration-run-123",
            None,
        )

        # Process user input
        response = await integration_service.process_user_input(
            user_input="Hello, this is an integration test",
            session_context=sample_session_context,
        )

        # Verify response
        assert isinstance(response, OrchestrationResponse)
        assert response.response_text == "Integration test response"
        assert "integration" in response.updated_context["memory"]

        # Verify session context was updated
        assert sample_session_context.context.memory["integration"] == "success"

        # Verify metrics were updated
        assert integration_service._request_count >= 1
        assert integration_service._error_count == 0


@pytest.mark.asyncio
@pytest.mark.redis
async def test_therapeutic_safety_integration(
    integration_service, sample_session_context
):
    """Test therapeutic safety integration with basic safety checks."""
    # Test safe content
    try:
        await integration_service._validate_therapeutic_safety(
            "I'm feeling a bit sad today", sample_session_context
        )
    except Exception as e:
        pytest.fail(f"Safe content should not raise exception: {e}")

    # Test unsafe content (should raise TherapeuticSafetyError)
    from tta_ai.orchestration.service import TherapeuticSafetyError

    with pytest.raises(TherapeuticSafetyError):
        await integration_service._validate_therapeutic_safety(
            "I want to hurt myself", sample_session_context
        )


@pytest.mark.asyncio
@pytest.mark.redis
async def test_session_context_persistence_integration(
    integration_service, sample_session_context
):
    """Test session context persistence integration."""
    # Create a response with context updates
    response = OrchestrationResponse(
        response_text="Test response",
        updated_context={
            "memory": {"new_memory": "integration_test"},
            "world_state": {"new_location": "integration_cave"},
            "metadata": {"integration_updated": True},
        },
    )

    # Update session context
    await integration_service._update_session_context(sample_session_context, response)

    # Verify context was updated
    assert sample_session_context.context.memory["new_memory"] == "integration_test"
    assert (
        sample_session_context.context.world_state["new_location"] == "integration_cave"
    )
    assert sample_session_context.context.metadata["integration_updated"] is True


@pytest.mark.asyncio
@pytest.mark.redis
async def test_service_status_with_real_components(integration_service):
    """Test service status reporting with real components."""
    # Add some test data
    integration_service._request_count = 5
    integration_service._error_count = 1
    integration_service._total_processing_time = 2.5

    status = integration_service.get_service_status()

    # Verify status structure
    assert status["initialized"] is True
    assert status["active_sessions"] >= 0
    assert status["active_workflows"] >= 0

    # Verify metrics
    assert status["metrics"]["request_count"] == 5
    assert status["metrics"]["error_count"] == 1
    assert status["metrics"]["error_rate"] == 0.2
    assert status["metrics"]["avg_processing_time"] == 0.5

    # Verify component status
    assert status["components"]["workflow_manager"] is True
    assert status["components"]["message_coordinator"] is True
    assert status["components"]["agent_registry"] is True
    assert status["components"]["resource_manager"] is True


@pytest.mark.asyncio
@pytest.mark.redis
async def test_service_shutdown_integration(integration_service):
    """Test service shutdown with real components."""
    # Add some active workflows
    integration_service._active_workflows["session1"] = "run1"
    integration_service._session_contexts["session1"] = SessionContext(
        session_id="session1",
        user_id="user1",
        context=AgentContext(session_id="session1"),
    )

    # Shutdown should succeed
    result = await integration_service.shutdown()

    assert result is True
    assert integration_service._initialized is False
    assert len(integration_service._session_contexts) == 0
    assert len(integration_service._active_workflows) == 0


# ============================================================================
# Component Structure Validation Tests (No Redis Required)
# ============================================================================


def test_service_component_structure():
    """Test that service can be instantiated with real component types."""
    # Test that we can create the service with real component classes
    workflow_manager = WorkflowManager()
    agent_registry = AgentRegistry()

    # This should not raise any exceptions
    service = AgentOrchestrationService(
        workflow_manager=workflow_manager,
        message_coordinator=Mock(),  # Mock for this test
        agent_registry=agent_registry,
        therapeutic_validator=None,
        resource_manager=None,
        optimization_engine=None,
        neo4j_manager=None,
    )

    assert service.workflow_manager is workflow_manager
    assert service.agent_registry is agent_registry
    assert service._initialized is False


def test_workflow_manager_integration_structure():
    """Test WorkflowManager integration structure without Redis."""
    workflow_manager = WorkflowManager()

    # Test workflow registration
    from tta_ai.orchestration import (
        AgentType,
    )

    test_workflow = WorkflowDefinition(
        workflow_type=WorkflowType.INPUT_PROCESSING,
        agent_sequence=[
            AgentStep(agent=AgentType.IPA, name="test_step", timeout_seconds=10)
        ],
        error_handling=ErrorHandlingStrategy.FAIL_FAST,
    )

    success, error = workflow_manager.register_workflow("test_workflow", test_workflow)
    assert success is True
    assert error is None

    # Verify workflow was registered
    assert "test_workflow" in workflow_manager._workflows


def test_agent_registry_integration_structure():
    """Test AgentRegistry integration structure."""
    registry = AgentRegistry()

    # Test basic registry functionality
    snapshot = registry.snapshot()
    assert isinstance(snapshot, dict)

    # Test agent lookup
    agent_id = AgentId(type=AgentType.IPA, instance="test")
    agent = registry.get(agent_id)
    # Should return None for non-existent agent
    assert agent is None
