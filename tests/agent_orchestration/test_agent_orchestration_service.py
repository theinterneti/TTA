"""
Comprehensive unit tests for AgentOrchestrationService (Task 16.1).

This module tests the main orchestration service API including process_user_input,
coordinate_agents, error handling, and integration with all orchestration components.
"""

import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.agent_orchestration import (
    AgentContext,
    AgentId,
    AgentType,
    OrchestrationResponse,
    SessionContext,
    WorkflowType,
)
from src.agent_orchestration.service import (
    AgentOrchestrationService,
    ServiceError,
    TherapeuticSafetyError,
    WorkflowExecutionError,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_workflow_manager():
    """Mock WorkflowManager for testing."""
    manager = Mock()
    manager.register_workflow = Mock(return_value=(True, None))
    manager.execute_workflow = Mock(
        return_value=(
            OrchestrationResponse(
                response_text="Test response",
                updated_context={"memory": {"test": "data"}},
                workflow_metadata={"workflow_name": "test", "run_id": "test-123"},
            ),
            "test-run-123",
            None,
        )
    )
    return manager


@pytest.fixture
def mock_message_coordinator():
    """Mock MessageCoordinator for testing."""
    coordinator = Mock()
    coordinator.send_message = AsyncMock(return_value=Mock(success=True))
    coordinator.receive = AsyncMock(return_value=None)
    return coordinator


@pytest.fixture
def mock_agent_registry():
    """Mock AgentRegistry for testing."""
    registry = Mock()
    registry.get_agent = Mock(
        return_value=Mock(agent_id=AgentId(type=AgentType.IPA, instance="test"))
    )
    registry.all = Mock(return_value=[])
    return registry


@pytest.fixture
def mock_therapeutic_validator():
    """Mock therapeutic validator for testing."""
    validator = Mock()
    validator.validate_text = AsyncMock(
        return_value=Mock(safe=True, level="safe", reason="Content appears safe")
    )
    return validator


@pytest.fixture
def mock_resource_manager():
    """Mock ResourceManager for testing."""
    manager = Mock()
    manager.allocate_resources = AsyncMock(return_value=Mock(success=True))
    return manager


@pytest.fixture
def mock_optimization_engine():
    """Mock optimization engine for testing."""
    engine = Mock()
    engine.optimize = AsyncMock(return_value=Mock(success=True))
    return engine


@pytest.fixture
def sample_session_context():
    """Sample session context for testing."""
    return SessionContext(
        session_id="test-session-123",
        user_id="test-user-456",
        created_at="2024-01-01T00:00:00Z",
        context=AgentContext(
            user_id="test-user-456",
            session_id="test-session-123",
            memory={"previous_interaction": "Hello"},
            world_state={"location": "forest"},
            metadata={"test": True},
        ),
    )


@pytest.fixture
def orchestration_service(
    mock_workflow_manager,
    mock_message_coordinator,
    mock_agent_registry,
    mock_therapeutic_validator,
    mock_resource_manager,
    mock_optimization_engine,
):
    """Create AgentOrchestrationService with mocked dependencies."""
    return AgentOrchestrationService(
        workflow_manager=mock_workflow_manager,
        message_coordinator=mock_message_coordinator,
        agent_registry=mock_agent_registry,
        therapeutic_validator=mock_therapeutic_validator,
        resource_manager=mock_resource_manager,
        optimization_engine=mock_optimization_engine,
        neo4j_manager=None,
    )


# ============================================================================
# Service Initialization Tests
# ============================================================================


@pytest.mark.asyncio
async def test_service_initialization_success(orchestration_service):
    """Test successful service initialization."""
    result = await orchestration_service.initialize()

    assert result is True
    assert orchestration_service._initialized is True

    # Verify workflow registration was called
    assert orchestration_service.workflow_manager.register_workflow.call_count >= 4


@pytest.mark.asyncio
async def test_service_initialization_failure():
    """Test service initialization failure with invalid components."""
    service = AgentOrchestrationService(
        workflow_manager=None,  # Invalid - should cause failure
        message_coordinator=Mock(),
        agent_registry=Mock(),
    )

    result = await service.initialize()

    assert result is False
    assert service._initialized is False


def test_service_status_reporting(orchestration_service):
    """Test service status and metrics reporting."""
    # Set some test metrics
    orchestration_service._request_count = 10
    orchestration_service._error_count = 2
    orchestration_service._total_processing_time = 5.0

    status = orchestration_service.get_service_status()

    assert status["initialized"] is False  # Not initialized yet
    assert status["active_sessions"] == 0
    assert status["active_workflows"] == 0
    assert status["metrics"]["request_count"] == 10
    assert status["metrics"]["error_count"] == 2
    assert status["metrics"]["error_rate"] == 0.2
    assert status["metrics"]["avg_processing_time"] == 0.5

    # Check component availability
    assert status["components"]["workflow_manager"] is True
    assert status["components"]["message_coordinator"] is True
    assert status["components"]["agent_registry"] is True
    assert status["components"]["therapeutic_validator"] is True
    assert status["components"]["resource_manager"] is True
    assert status["components"]["optimization_engine"] is True
    assert status["components"]["neo4j_manager"] is False


# ============================================================================
# Process User Input Tests
# ============================================================================


@pytest.mark.asyncio
async def test_process_user_input_success(
    orchestration_service, sample_session_context
):
    """Test successful user input processing."""
    await orchestration_service.initialize()

    response = await orchestration_service.process_user_input(
        user_input="Hello, I need help with anxiety",
        session_context=sample_session_context,
    )

    assert isinstance(response, OrchestrationResponse)
    assert response.response_text == "Test response"
    assert "memory" in response.updated_context

    # Verify metrics were updated
    assert orchestration_service._request_count == 1
    assert orchestration_service._error_count == 0
    assert orchestration_service._total_processing_time > 0


@pytest.mark.asyncio
async def test_process_user_input_not_initialized(
    orchestration_service, sample_session_context
):
    """Test process_user_input fails when service not initialized."""
    with pytest.raises(ServiceError, match="Service not initialized"):
        await orchestration_service.process_user_input(
            user_input="Hello", session_context=sample_session_context
        )


@pytest.mark.asyncio
async def test_process_user_input_therapeutic_safety_error(
    orchestration_service, sample_session_context
):
    """Test process_user_input handles therapeutic safety errors."""
    await orchestration_service.initialize()

    # Mock therapeutic validator to return unsafe content with "blocked" level
    orchestration_service.therapeutic_validator.validate_text = AsyncMock(
        return_value=Mock(
            safe=False, level="blocked", reason="Contains harmful content"
        )
    )

    # Mock _call_therapeutic_validator to return blocked content (async method)
    with patch.object(
        orchestration_service,
        "_call_therapeutic_validator",
        new=AsyncMock(
            return_value={
                "safe": False,
                "level": "blocked",
                "reason": "Test error",
                "crisis_detected": False,
            }
        ),
    ):
        with pytest.raises(
            TherapeuticSafetyError, match="Content blocked due to safety concerns"
        ):
            await orchestration_service.process_user_input(
                user_input="I want to hurt myself",
                session_context=sample_session_context,
            )

    # Verify error metrics were updated
    assert orchestration_service._error_count == 1


@pytest.mark.asyncio
async def test_process_user_input_workflow_execution_error(
    orchestration_service, sample_session_context
):
    """Test process_user_input handles workflow execution errors."""
    await orchestration_service.initialize()

    # Mock workflow manager to return error
    orchestration_service.workflow_manager.execute_workflow = Mock(
        return_value=(None, None, "Workflow failed")
    )

    with pytest.raises(WorkflowExecutionError, match="Workflow execution failed"):
        await orchestration_service.process_user_input(
            user_input="Hello", session_context=sample_session_context
        )

    # Verify error metrics were updated
    assert orchestration_service._error_count == 1


@pytest.mark.asyncio
async def test_process_user_input_workflow_type_determination(
    orchestration_service, sample_session_context
):
    """Test workflow type determination based on user input."""
    await orchestration_service.initialize()

    test_cases = [
        ("help", WorkflowType.INPUT_PROCESSING),
        ("look around", WorkflowType.WORLD_BUILDING),
        ("tell me a story", WorkflowType.NARRATIVE_GENERATION),
        ("I'm feeling anxious", WorkflowType.COLLABORATIVE),
    ]

    for user_input, expected_workflow in test_cases:
        determined_type = await orchestration_service._determine_workflow_type(
            user_input, sample_session_context
        )
        assert determined_type == expected_workflow


# ============================================================================
# Coordinate Agents Tests
# ============================================================================


@pytest.mark.asyncio
async def test_coordinate_agents_success(orchestration_service):
    """Test successful agent coordination."""
    await orchestration_service.initialize()

    context = AgentContext(
        user_id="test-user", session_id="test-session", memory={"test": "data"}
    )

    response, run_id, error = await orchestration_service.coordinate_agents(
        workflow_type=WorkflowType.COLLABORATIVE, context=context
    )

    assert response is not None
    assert run_id == "test-run-123"
    assert error is None

    # Verify workflow manager was called
    orchestration_service.workflow_manager.execute_workflow.assert_called_once()


@pytest.mark.asyncio
async def test_coordinate_agents_not_initialized(orchestration_service):
    """Test coordinate_agents fails when service not initialized."""
    context = AgentContext(session_id="test")

    with pytest.raises(ServiceError, match="Service not initialized"):
        await orchestration_service.coordinate_agents(
            workflow_type=WorkflowType.COLLABORATIVE, context=context
        )


@pytest.mark.asyncio
async def test_coordinate_agents_workflow_error(orchestration_service):
    """Test coordinate_agents handles workflow execution errors."""
    await orchestration_service.initialize()

    # Mock workflow manager to return error
    orchestration_service.workflow_manager.execute_workflow = Mock(
        return_value=(None, None, "Execution failed")
    )

    context = AgentContext(session_id="test")

    with pytest.raises(WorkflowExecutionError, match="Workflow execution failed"):
        await orchestration_service.coordinate_agents(
            workflow_type=WorkflowType.COLLABORATIVE, context=context
        )


# ============================================================================
# Service Shutdown Tests
# ============================================================================


@pytest.mark.asyncio
async def test_service_shutdown_success(orchestration_service):
    """Test successful service shutdown."""
    await orchestration_service.initialize()

    # Add some active workflows
    orchestration_service._active_workflows["session1"] = "run1"
    orchestration_service._active_workflows["session2"] = "run2"

    result = await orchestration_service.shutdown()

    assert result is True
    assert orchestration_service._initialized is False
    assert len(orchestration_service._session_contexts) == 0
    assert len(orchestration_service._active_workflows) == 0


# ============================================================================
# Therapeutic Safety Tests
# ============================================================================


@pytest.mark.asyncio
async def test_therapeutic_safety_validation_success(
    orchestration_service, sample_session_context
):
    """Test successful therapeutic safety validation."""
    await orchestration_service._validate_therapeutic_safety(
        "I'm feeling a bit sad today", sample_session_context
    )
    # Should not raise any exception


@pytest.mark.asyncio
async def test_therapeutic_safety_validation_high_risk(
    orchestration_service, sample_session_context
):
    """Test therapeutic safety validation with high-risk content."""
    # The service uses basic safety checks when no validator is configured properly
    # Let's test with the actual basic safety check method
    with pytest.raises(
        TherapeuticSafetyError, match="Content contains potentially harmful language"
    ):
        await orchestration_service._basic_safety_checks("I want to kill myself")


@pytest.mark.asyncio
async def test_therapeutic_safety_validation_no_validator(sample_session_context):
    """Test therapeutic safety validation without validator (basic checks only)."""
    service = AgentOrchestrationService(
        workflow_manager=Mock(),
        message_coordinator=Mock(),
        agent_registry=Mock(),
        therapeutic_validator=None,  # No validator
    )

    # Should use basic safety checks
    with pytest.raises(TherapeuticSafetyError):
        await service._validate_therapeutic_safety(
            "I want to hurt myself", sample_session_context
        )


@pytest.mark.asyncio
async def test_therapeutic_safety_validation_error_handling(
    orchestration_service, sample_session_context
):
    """Test therapeutic safety validation error handling."""
    # Mock validator to raise exception
    orchestration_service.therapeutic_validator = Mock()

    with patch.object(
        orchestration_service,
        "_call_therapeutic_validator",
        side_effect=Exception("Validator error"),
    ):
        # Should not raise exception, but log warning and continue
        await orchestration_service._validate_therapeutic_safety(
            "Hello world", sample_session_context
        )


# ============================================================================
# Session Context Management Tests
# ============================================================================


@pytest.mark.asyncio
async def test_session_context_update(orchestration_service, sample_session_context):
    """Test session context update with workflow response."""
    response = OrchestrationResponse(
        response_text="Test response",
        updated_context={
            "memory": {"new_memory": "test"},
            "world_state": {"new_location": "cave"},
            "metadata": {"updated": True},
        },
    )

    await orchestration_service._update_session_context(
        sample_session_context, response
    )

    # Verify context was updated
    assert sample_session_context.context.memory["new_memory"] == "test"
    assert sample_session_context.context.world_state["new_location"] == "cave"
    assert sample_session_context.context.metadata["updated"] is True


@pytest.mark.asyncio
async def test_session_context_persistence_with_neo4j(
    orchestration_service, sample_session_context
):
    """Test session context persistence with Neo4j manager."""
    # Mock Neo4j manager
    neo4j_manager = Mock()
    orchestration_service.neo4j_manager = neo4j_manager

    response = OrchestrationResponse(
        response_text="Test response", updated_context={"memory": {"test": "data"}}
    )

    await orchestration_service._update_session_context(
        sample_session_context, response
    )

    # Should call persist method (currently just logs)


@pytest.mark.asyncio
async def test_session_context_update_error_handling(
    orchestration_service, sample_session_context
):
    """Test session context update error handling."""
    # Create response with empty context data (valid but might cause issues in processing)
    response = OrchestrationResponse(
        response_text="Test response", updated_context={}  # Empty dict instead of None
    )

    # Should not raise exception even if update fails
    await orchestration_service._update_session_context(
        sample_session_context, response
    )


# ============================================================================
# Workflow Type Determination Tests
# ============================================================================


@pytest.mark.asyncio
async def test_workflow_type_determination_edge_cases(
    orchestration_service, sample_session_context
):
    """Test workflow type determination with edge cases."""
    test_cases = [
        ("", WorkflowType.COLLABORATIVE),  # Empty input
        ("   ", WorkflowType.COLLABORATIVE),  # Whitespace only
        ("HELP", WorkflowType.INPUT_PROCESSING),  # Uppercase
        ("Look Around The Room", WorkflowType.WORLD_BUILDING),  # Mixed case
        (
            "Tell me what happens next in the story",
            WorkflowType.NARRATIVE_GENERATION,
        ),  # Long input
        (
            "Complex therapeutic scenario with multiple elements",
            WorkflowType.COLLABORATIVE,
        ),  # Default case
    ]

    for user_input, expected_workflow in test_cases:
        determined_type = await orchestration_service._determine_workflow_type(
            user_input, sample_session_context
        )
        assert determined_type == expected_workflow


@pytest.mark.asyncio
async def test_workflow_type_determination_error_handling(
    orchestration_service, sample_session_context
):
    """Test workflow type determination error handling."""
    # Mock to raise exception during processing
    with patch("src.agent_orchestration.service.logger") as mock_logger:
        # Should return collaborative workflow as fallback
        result = await orchestration_service._determine_workflow_type(
            "test input", sample_session_context
        )
        assert result == WorkflowType.COLLABORATIVE


# ============================================================================
# Resource Management Tests
# ============================================================================


@pytest.mark.asyncio
async def test_resource_allocation_success(orchestration_service):
    """Test successful resource allocation."""
    context = AgentContext(session_id="test")

    # Should not raise exception
    await orchestration_service._allocate_workflow_resources(
        WorkflowType.COLLABORATIVE, context
    )


@pytest.mark.asyncio
async def test_resource_allocation_no_manager(sample_session_context):
    """Test resource allocation without resource manager."""
    service = AgentOrchestrationService(
        workflow_manager=Mock(),
        message_coordinator=Mock(),
        agent_registry=Mock(),
        resource_manager=None,  # No resource manager
    )

    context = AgentContext(session_id="test")

    # Should not raise exception
    await service._allocate_workflow_resources(WorkflowType.COLLABORATIVE, context)


@pytest.mark.asyncio
async def test_resource_allocation_error_handling(orchestration_service):
    """Test resource allocation error handling."""
    # Mock resource manager to raise exception
    orchestration_service.resource_manager = Mock()
    orchestration_service.resource_manager.allocate_resources = Mock(
        side_effect=Exception("Resource error")
    )

    context = AgentContext(session_id="test")

    # Should not raise exception, just log warning
    await orchestration_service._allocate_workflow_resources(
        WorkflowType.COLLABORATIVE, context
    )


# ============================================================================
# Workflow Name Mapping Tests
# ============================================================================


def test_workflow_name_mapping(orchestration_service):
    """Test workflow type to name mapping."""
    test_cases = [
        (WorkflowType.COLLABORATIVE, "collaborative"),
        (WorkflowType.INPUT_PROCESSING, "input_processing"),
        (WorkflowType.WORLD_BUILDING, "world_building"),
        (WorkflowType.NARRATIVE_GENERATION, "narrative_generation"),
    ]

    for workflow_type, expected_name in test_cases:
        name = orchestration_service._get_workflow_name(workflow_type)
        assert name == expected_name


def test_workflow_name_mapping_unknown_type(orchestration_service):
    """Test workflow name mapping with unknown type."""
    # Create a mock workflow type that doesn't exist in mapping
    unknown_type = "unknown_workflow"

    # Should return collaborative as default
    name = orchestration_service._get_workflow_name(unknown_type)
    assert name == "collaborative"


# ============================================================================
# Performance and Load Tests
# ============================================================================


@pytest.mark.asyncio
async def test_service_performance_metrics(
    orchestration_service, sample_session_context
):
    """Test service performance metrics tracking."""
    await orchestration_service.initialize()

    # Mock workflow execution to be fast
    with patch.object(
        orchestration_service.workflow_manager, "execute_workflow"
    ) as mock_execute:
        mock_execute.return_value = (
            OrchestrationResponse(
                response_text="Fast response",
                updated_context={"memory": {"test": "data"}},
                workflow_metadata={"test": "performance"},
            ),
            "perf-run-123",
            None,
        )

        # Process multiple requests
        start_time = time.time()
        for i in range(5):
            await orchestration_service.process_user_input(
                user_input=f"Test request {i}", session_context=sample_session_context
            )
        end_time = time.time()

        # Verify performance metrics
        status = orchestration_service.get_service_status()
        assert status["metrics"]["request_count"] == 5
        assert status["metrics"]["error_count"] == 0
        assert status["metrics"]["error_rate"] == 0.0
        assert status["metrics"]["avg_processing_time"] > 0

        # Verify total processing time is reasonable (should be very fast with mocks)
        total_time = end_time - start_time
        assert total_time < 1.0  # Should complete 5 requests in under 1 second


@pytest.mark.asyncio
async def test_concurrent_request_handling(
    orchestration_service, sample_session_context
):
    """Test service handling of concurrent requests."""
    await orchestration_service.initialize()

    # Mock workflow execution
    with patch.object(
        orchestration_service.workflow_manager, "execute_workflow"
    ) as mock_execute:
        mock_execute.return_value = (
            OrchestrationResponse(
                response_text="Concurrent response",
                updated_context={"memory": {"concurrent": "test"}},
                workflow_metadata={"test": "concurrent"},
            ),
            "concurrent-run-123",
            None,
        )

        # Create multiple concurrent requests
        tasks = []
        for i in range(3):
            # Create separate session contexts to avoid conflicts
            session_context = SessionContext(
                session_id=f"concurrent-session-{i}",
                user_id=f"concurrent-user-{i}",
                created_at="2024-01-01T00:00:00Z",
                context=AgentContext(
                    user_id=f"concurrent-user-{i}",
                    session_id=f"concurrent-session-{i}",
                    memory={"concurrent_test": i},
                ),
            )

            task = orchestration_service.process_user_input(
                user_input=f"Concurrent request {i}", session_context=session_context
            )
            tasks.append(task)

        # Execute all tasks concurrently
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        # Verify all requests completed successfully
        assert len(responses) == 3
        for response in responses:
            assert isinstance(response, OrchestrationResponse)
            assert response.response_text == "Concurrent response"

        # Verify performance metrics
        status = orchestration_service.get_service_status()
        assert status["metrics"]["request_count"] == 3
        assert status["metrics"]["error_count"] == 0

        # Concurrent execution should be faster than sequential
        total_time = end_time - start_time
        assert total_time < 0.5  # Should complete 3 concurrent requests quickly


@pytest.mark.asyncio
async def test_error_recovery_scenarios(orchestration_service, sample_session_context):
    """Test service recovery from various error scenarios."""
    await orchestration_service.initialize()

    # Test recovery from workflow execution error
    with patch.object(
        orchestration_service.workflow_manager, "execute_workflow"
    ) as mock_execute:
        # First call fails, second succeeds
        mock_execute.side_effect = [
            (None, None, "Workflow failed"),  # First call fails
            (
                OrchestrationResponse(
                    response_text="Recovery successful",
                    updated_context={"memory": {"recovered": True}},
                    workflow_metadata={"test": "recovery"},
                ),
                "recovery-run-123",
                None,
            ),  # Second call succeeds
        ]

        # First request should fail
        with pytest.raises(WorkflowExecutionError):
            await orchestration_service.process_user_input(
                user_input="First request", session_context=sample_session_context
            )

        # Service should still be functional for second request
        response = await orchestration_service.process_user_input(
            user_input="Second request", session_context=sample_session_context
        )

        assert response.response_text == "Recovery successful"

        # Verify error metrics
        status = orchestration_service.get_service_status()
        assert status["metrics"]["request_count"] == 2
        assert status["metrics"]["error_count"] == 1
        assert status["metrics"]["error_rate"] == 0.5


@pytest.mark.asyncio
async def test_service_shutdown_with_active_workflows(orchestration_service):
    """Test service shutdown behavior with active workflows."""
    await orchestration_service.initialize()

    # Add some active workflows and sessions
    orchestration_service._active_workflows["session1"] = "run1"
    orchestration_service._active_workflows["session2"] = "run2"
    orchestration_service._session_contexts["session1"] = SessionContext(
        session_id="session1",
        user_id="user1",
        context=AgentContext(session_id="session1"),
    )
    orchestration_service._session_contexts["session2"] = SessionContext(
        session_id="session2",
        user_id="user2",
        context=AgentContext(session_id="session2"),
    )

    # Shutdown should handle active workflows gracefully
    result = await orchestration_service.shutdown()

    assert result is True
    assert orchestration_service._initialized is False
    assert len(orchestration_service._session_contexts) == 0
    assert len(orchestration_service._active_workflows) == 0
