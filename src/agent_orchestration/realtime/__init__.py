"""
Real-time interaction management for agent orchestration.

This module provides WebSocket-based real-time communication, event broadcasting,
progressive feedback mechanisms, and performance optimization for the TTA agent
orchestration system.
"""

from .models import (
    WebSocketEvent,
    AgentStatusEvent,
    WorkflowProgressEvent,
    SystemMetricsEvent,
    ProgressiveFeedbackEvent,
    OptimizationEvent,
    EventType,
    AgentStatus,
    WorkflowStatus,
    create_agent_status_event,
    create_workflow_progress_event,
    create_progressive_feedback_event,
    create_error_event,
)

__all__ = [
    "WebSocketEvent",
    "AgentStatusEvent",
    "WorkflowProgressEvent",
    "SystemMetricsEvent",
    "ProgressiveFeedbackEvent",
    "OptimizationEvent",
    "EventType",
    "AgentStatus",
    "WorkflowStatus",
    "create_agent_status_event",
    "create_workflow_progress_event",
    "create_progressive_feedback_event",
    "create_error_event",
]
