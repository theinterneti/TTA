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
from .messaging import MessageResult, MessageSubscription, QueueMessage
from .interfaces import MessageCoordinator, AgentProxy
from .state import AgentContext, AgentState, SessionContext, AgentRuntimeStatus
from .workflow import (
    WorkflowType,
    ErrorHandlingStrategy,
    AgentStep,
    TimeoutConfiguration,
    WorkflowDefinition,
)
from .workflow_manager import WorkflowManager, WorkflowRunState, WorkflowRunStatus

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
    "MessageCoordinator",
    "AgentProxy",
    "AgentContext",
    "AgentState",
    "SessionContext",
    "AgentRuntimeStatus",
    "WorkflowType",
    "ErrorHandlingStrategy",
    "AgentStep",
    "TimeoutConfiguration",
    "WorkflowDefinition",
    "WorkflowManager",
    "WorkflowRunState",
    "WorkflowRunStatus",
]

