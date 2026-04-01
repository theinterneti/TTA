"""

# Logseq: [[TTA.dev/Agent_orchestration/__init__]]
Agent Orchestration core package.

This package provides the foundational data models and interfaces used by the
Agent Orchestration Component to coordinate specialized AI agents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .proxies import (
        InputProcessorAgentProxy,
        NarrativeGeneratorAgentProxy,
        WorldBuilderAgentProxy,
    )

from .agents import Agent, AgentRegistry
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

# Proxy imports are deferred via __getattr__ to avoid circular imports with
# src.components.ipa / wba / nga which are referenced by adapters.py.
_PROXY_NAMES = {
    "InputProcessorAgentProxy",
    "NarrativeGeneratorAgentProxy",
    "WorldBuilderAgentProxy",
}


def __getattr__(name: str) -> object:  # noqa: ANN001
    if name in _PROXY_NAMES:
        from .proxies import (  # noqa: PLC0415
            InputProcessorAgentProxy,
            NarrativeGeneratorAgentProxy,
            WorldBuilderAgentProxy,
        )

        mapping = {
            "InputProcessorAgentProxy": InputProcessorAgentProxy,
            "NarrativeGeneratorAgentProxy": NarrativeGeneratorAgentProxy,
            "WorldBuilderAgentProxy": WorldBuilderAgentProxy,
        }
        return mapping[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
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
    # circuit breaker (now from ttadev)
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
