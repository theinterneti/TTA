"""
Agent Orchestration core package.

This package provides the foundational data models and interfaces used by the
Agent Orchestration Component to coordinate specialized AI agents.
"""

from .models import (
    AgentId,
    AgentType,
    MessageType,
    MessagePriority,
    AgentMessage,
    OrchestrationRequest,
    OrchestrationResponse,
)
from .messaging import (
    MessageResult,
    MessageSubscription,
    QueueMessage,
    ReceivedMessage,
    FailureType,
)
from .interfaces import MessageCoordinator, AgentProxy
from .agents import Agent, AgentRegistry
from .proxies import (
    InputProcessorAgentProxy,
    WorldBuilderAgentProxy,
    NarrativeGeneratorAgentProxy,
)
from .state import AgentContext, AgentState, SessionContext, AgentRuntimeStatus
from .workflow import (
    WorkflowType,
    ErrorHandlingStrategy,
    AgentStep,
    TimeoutConfiguration,
    WorkflowDefinition,
)
from .workflow_manager import WorkflowManager, WorkflowRunState, WorkflowRunStatus
from .resources import (
    ResourceManager,
    ResourceRequirements,
    ResourceAllocation,
    ResourceUsage,
    ResourceUsageReport,
    WorkloadMetrics,
    OptimizationResult,
)
from .performance import get_step_aggregator
# tools exports
try:
    from .tools.models import ToolSpec, ToolParameter, ToolRegistration, ToolInvocation, ToolPolicy, ToolStatus
    from .tools.redis_tool_registry import RedisToolRegistry
    from .tools.coordinator import ToolCoordinator
    from .tools.invocation_service import ToolInvocationService
except Exception:
    # Tools package may be optional during partial builds/tests
    ToolSpec = ToolParameter = ToolRegistration = ToolInvocation = ToolPolicy = ToolStatus = None
    RedisToolRegistry = ToolCoordinator = None

__all__ = [
    "AgentId",
    "AgentType",
    "MessageType",
    "MessagePriority",
    "AgentMessage",
    "OrchestrationRequest",
    "OrchestrationResponse",
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
    "ResourceUsage",
    "ResourceUsageReport",
    "WorkloadMetrics",
    "OptimizationResult",
    "get_step_aggregator",
]

