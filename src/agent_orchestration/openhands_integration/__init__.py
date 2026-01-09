"""

# Logseq: [[TTA.dev/Agent_orchestration/Openhands_integration/__init__]]
OpenHands integration for TTA multi-agent orchestration.

This package provides integration with the OpenHands Python SDK for development
tasks, following TTA's agent proxy pattern.

Components:
- OpenHandsClient: Low-level SDK wrapper
- OpenHandsAdapter: Communication layer with retry logic
- OpenHandsAgentProxy: TTA agent integration
- OpenHandsIntegrationConfig: Configuration management
- OpenHandsErrorRecovery: Error handling and recovery
- UnitTestGenerationService: Automated unit test generation

Example (Agent Proxy):
    # Load configuration from environment
    config = OpenHandsIntegrationConfig.from_env()

    # Create proxy
    proxy = OpenHandsAgentProxy(
        coordinator=message_coordinator,
        openhands_config=config,
        agent_registry=registry,
    )

    # Execute development task
    result = await proxy.execute_development_task(
        "Write a Python function to calculate fibonacci numbers"
    )

Example (Unit Test Generation):
    # Load configuration
    config = OpenHandsConfig.from_env()

    # Create service
    service = UnitTestGenerationService(config)

    # Generate tests
    spec = TestTaskSpecification(
        target_file=Path("src/agent_orchestration/tools/client.py"),
        coverage_threshold=80.0,
    )
    result = await service.generate_tests(spec)
"""

from .adapter import OpenHandsAdapter
from .client import OpenHandsClient, create_openhands_client
from .config import (
    FREE_MODELS,
    OpenHandsConfig,
    OpenHandsIntegrationConfig,
    OpenHandsModelConfig,
)
from .docker_client import DockerOpenHandsClient
from .error_recovery import OpenHandsErrorRecovery
from .execution_engine import ExecutionEngine
from .helpers import (
    generate_tests_for_file,
    generate_tests_for_package,
    validate_test_result,
)
from .metrics_collector import ExecutionMetrics, MetricsCollector, ModelMetrics
from .model_rotation import ModelRotationManager
from .model_selector import ModelSelector, TaskCategory, TaskRequirements
from .models import (
    RECOVERY_STRATEGIES,
    OpenHandsErrorType,
    OpenHandsRecoveryStrategy,
    OpenHandsTaskResult,
)
from .proxy import OpenHandsAgentProxy
from .result_validator import ResultValidator, ValidationResult
from .task_queue import QueuedTask, TaskPriority, TaskQueue, TaskStatus
from .test_generation_models import (
    TestGenerationError,
    TestTaskSpecification,
    TestValidationResult,
)
from .test_generation_service import UnitTestGenerationService

__all__ = [
    # Client and adapter
    "OpenHandsClient",
    "DockerOpenHandsClient",
    "create_openhands_client",
    "OpenHandsAdapter",
    "OpenHandsAgentProxy",
    # Configuration
    "OpenHandsConfig",
    "OpenHandsIntegrationConfig",
    "OpenHandsModelConfig",
    "FREE_MODELS",
    # Models
    "OpenHandsTaskResult",
    "OpenHandsErrorType",
    "OpenHandsRecoveryStrategy",
    "RECOVERY_STRATEGIES",
    # Error recovery
    "OpenHandsErrorRecovery",
    # Production system components
    "ExecutionEngine",
    "TaskQueue",
    "QueuedTask",
    "TaskStatus",
    "TaskPriority",
    "ModelSelector",
    "TaskRequirements",
    "TaskCategory",
    "ResultValidator",
    "ValidationResult",
    "MetricsCollector",
    "ExecutionMetrics",
    "ModelMetrics",
    "ModelRotationManager",
    # Test generation
    "UnitTestGenerationService",
    "TestTaskSpecification",
    "TestValidationResult",
    "TestGenerationError",
    # Helper utilities
    "generate_tests_for_file",
    "generate_tests_for_package",
    "validate_test_result",
]
