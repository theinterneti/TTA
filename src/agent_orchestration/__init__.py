"""
Agent Orchestration core package.

This package provides the foundational data models and interfaces used by the
Agent Orchestration Component to coordinate specialized AI agents.
"""

from .agents import Agent, AgentRegistry
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitBreakerState,
)
from .circuit_breaker_config import (
    CircuitBreakerConfigManager,
    WorkflowErrorHandlingConfigSchema,
)
from .circuit_breaker_metrics import (
    CircuitBreakerLogger,
    CircuitBreakerMetricsCollector,
)
from .circuit_breaker_registry import CircuitBreakerRegistry
from .interfaces import AgentProxy, MessageCoordinator
from .messaging import (
    FailureType,
    MessageResult,
    MessageSubscription,
    QueueMessage,
    ReceivedMessage,
)
from .models import (  # Capability system models
    AgentCapability,
    AgentCapabilitySet,
    AgentId,
    AgentMessage,
    AgentType,
    CapabilityDiscoveryRequest,
    CapabilityDiscoveryResponse,
    CapabilityMatchCriteria,
    CapabilityMatchResult,
    CapabilityScope,
    CapabilityStatus,
    CapabilityType,
    MessagePriority,
    MessageType,
    OrchestrationRequest,
    OrchestrationResponse,
)
from .performance import get_step_aggregator
from .proxies import (
    InputProcessorAgentProxy,
    NarrativeGeneratorAgentProxy,
    WorldBuilderAgentProxy,
)
from .resource_exhaustion_detector import (
    ResourceExhaustionDetector,
    ResourceExhaustionEvent,
    ResourceThresholds,
)
from .resources import (
    OptimizationResult,
    ResourceAllocation,
    ResourceManager,
    ResourceRequirements,
    ResourceUsage,
    ResourceUsageReport,
    WorkloadMetrics,
)

# main service
from .service import AgentOrchestrationService
from .state import AgentContext, AgentRuntimeStatus, AgentState, SessionContext
from .therapeutic_safety import (
    SafetyLevel,
    SafetyService,
    TherapeuticValidator,
    get_global_safety_service,
)
from .workflow import (
    AgentStep,
    ErrorHandlingStrategy,
    TimeoutConfiguration,
    WorkflowDefinition,
    WorkflowType,
)
from .workflow_manager import WorkflowManager, WorkflowRunState, WorkflowRunStatus

# tools exports
try:
    from .tools.coordinator import ToolCoordinator
    from .tools.invocation_service import ToolInvocationService
    from .tools.models import (
        ToolInvocation,
        ToolParameter,
        ToolPolicy,
        ToolRegistration,
        ToolSpec,
        ToolStatus,
    )
    from .tools.redis_tool_registry import RedisToolRegistry
except Exception:
    # Tools package may be optional during partial builds/tests
    ToolSpec = ToolParameter = ToolRegistration = ToolInvocation = ToolPolicy = (
        ToolStatus
    ) = None
    RedisToolRegistry = ToolCoordinator = None

__all__ = [
    "AgentId",
    "AgentType",
    "MessageType",
    "MessagePriority",
    "AgentMessage",
    "OrchestrationRequest",
    "OrchestrationResponse",
    # Capability system models
    "CapabilityType",
    "CapabilityScope",
    "CapabilityStatus",
    "AgentCapability",
    "AgentCapabilitySet",
    "CapabilityMatchCriteria",
    "CapabilityMatchResult",
    "CapabilityDiscoveryRequest",
    "CapabilityDiscoveryResponse",
    "MessageResult",
    "MessageSubscription",
    "QueueMessage",
    "ReceivedMessage",
    "FailureType",
    "MessageCoordinator",
    "AgentProxy",
    # new agent base + registry + proxies
    "Agent",
    "AgentRegistry",
    "InputProcessorAgentProxy",
    "WorldBuilderAgentProxy",
    "NarrativeGeneratorAgentProxy",
    # state
    "AgentContext",
    "AgentState",
    "SessionContext",
    "AgentRuntimeStatus",
    # workflow
    "WorkflowType",
    "ErrorHandlingStrategy",
    "AgentStep",
    "TimeoutConfiguration",
    "WorkflowDefinition",
    # workflow manager
    "WorkflowManager",
    "WorkflowRunState",
    "WorkflowRunStatus",
    # resources + perf
    "ResourceManager",
    "ResourceRequirements",
    "ResourceAllocation",
    # circuit breaker
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerState",
    "CircuitBreakerOpenError",
    "CircuitBreakerRegistry",
    "CircuitBreakerMetricsCollector",
    "CircuitBreakerLogger",
    "CircuitBreakerConfigManager",
    "WorkflowErrorHandlingConfigSchema",
    "ResourceExhaustionDetector",
    "ResourceThresholds",
    "ResourceExhaustionEvent",
    "ResourceUsage",
    "ResourceUsageReport",
    "WorkloadMetrics",
    "OptimizationResult",
    "get_step_aggregator",
    # safety exports
    "TherapeuticValidator",
    "SafetyLevel",
    "SafetyService",
    "get_global_safety_service",
    # main service
    "AgentOrchestrationService",
]
