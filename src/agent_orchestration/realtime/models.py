"""
Data models for real-time communication in agent orchestration.

This module defines Pydantic models for WebSocket events, agent status updates,
workflow progress messages, and other real-time communication data structures.
"""

from __future__ import annotations

import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict


class EventType(str, Enum):
    """Types of real-time events."""
    AGENT_STATUS = "agent_status"
    WORKFLOW_PROGRESS = "workflow_progress"
    SYSTEM_METRICS = "system_metrics"
    PROGRESSIVE_FEEDBACK = "progressive_feedback"
    OPTIMIZATION = "optimization"
    CONNECTION_STATUS = "connection_status"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class AgentStatus(str, Enum):
    """Agent status values."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    IDLE = "idle"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


class WorkflowStatus(str, Enum):
    """Workflow status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WebSocketEvent(BaseModel):
    """Base model for all WebSocket events."""
    
    event_id: str = Field(default_factory=lambda: uuid4().hex, description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of the event")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp when event was created")
    source: str = Field(..., description="Source component that generated the event")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data payload")

    model_config = ConfigDict(use_enum_values=True)


class AgentStatusEvent(WebSocketEvent):
    """Event for agent status changes."""

    event_type: Literal[EventType.AGENT_STATUS] = Field(default=EventType.AGENT_STATUS)
    agent_id: str = Field(..., description="Agent identifier")
    agent_type: str = Field(..., description="Type of agent (ipa, wba, nga)")
    instance: Optional[str] = Field(None, description="Agent instance identifier")
    status: AgentStatus = Field(..., description="Current agent status")
    previous_status: Optional[AgentStatus] = Field(None, description="Previous agent status")
    heartbeat_age: Optional[float] = Field(None, description="Age of last heartbeat in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional agent metadata")


class WorkflowProgressEvent(WebSocketEvent):
    """Event for workflow progress updates."""

    event_type: Literal[EventType.WORKFLOW_PROGRESS] = Field(default=EventType.WORKFLOW_PROGRESS)
    workflow_id: str = Field(..., description="Workflow identifier")
    workflow_type: str = Field(..., description="Type of workflow")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="Progress percentage (0-100)")
    current_step: Optional[str] = Field(None, description="Current workflow step")
    total_steps: Optional[int] = Field(None, description="Total number of steps")
    completed_steps: Optional[int] = Field(None, description="Number of completed steps")
    estimated_completion: Optional[float] = Field(None, description="Estimated completion timestamp")
    user_id: Optional[str] = Field(None, description="User associated with the workflow")


class SystemMetricsEvent(WebSocketEvent):
    """Event for system performance metrics."""

    event_type: Literal[EventType.SYSTEM_METRICS] = Field(default=EventType.SYSTEM_METRICS)
    cpu_usage: Optional[float] = Field(None, ge=0.0, le=100.0, description="CPU usage percentage")
    memory_usage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Memory usage percentage")
    memory_usage_mb: Optional[float] = Field(None, ge=0.0, description="Memory usage in MB")
    active_connections: Optional[int] = Field(None, ge=0, description="Number of active connections")
    active_workflows: Optional[int] = Field(None, ge=0, description="Number of active workflows")
    message_queue_size: Optional[int] = Field(None, ge=0, description="Message queue size")
    response_time_avg: Optional[float] = Field(None, ge=0.0, description="Average response time in seconds")
    error_rate: Optional[float] = Field(None, ge=0.0, le=100.0, description="Error rate percentage")


class ProgressiveFeedbackEvent(WebSocketEvent):
    """Event for progressive feedback during long-running operations."""

    event_type: Literal[EventType.PROGRESSIVE_FEEDBACK] = Field(default=EventType.PROGRESSIVE_FEEDBACK)
    operation_id: str = Field(..., description="Operation identifier")
    operation_type: str = Field(..., description="Type of operation")
    stage: str = Field(..., description="Current operation stage")
    message: str = Field(..., description="Human-readable progress message")
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    intermediate_result: Optional[Dict[str, Any]] = Field(None, description="Intermediate operation result")
    estimated_remaining: Optional[float] = Field(None, description="Estimated remaining time in seconds")
    user_id: Optional[str] = Field(None, description="User associated with the operation")


class OptimizationEvent(WebSocketEvent):
    """Event for performance optimization updates."""

    event_type: Literal[EventType.OPTIMIZATION] = Field(default=EventType.OPTIMIZATION)
    optimization_type: str = Field(..., description="Type of optimization")
    parameter_name: str = Field(..., description="Parameter being optimized")
    old_value: Union[float, int, str] = Field(..., description="Previous parameter value")
    new_value: Union[float, int, str] = Field(..., description="New parameter value")
    improvement_metric: Optional[str] = Field(None, description="Metric that improved")
    improvement_value: Optional[float] = Field(None, description="Amount of improvement")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in optimization")


class ConnectionStatusEvent(WebSocketEvent):
    """Event for WebSocket connection status changes."""

    event_type: Literal[EventType.CONNECTION_STATUS] = Field(default=EventType.CONNECTION_STATUS)
    connection_id: str = Field(..., description="Connection identifier")
    status: str = Field(..., description="Connection status (connected, disconnected, error)")
    user_id: Optional[str] = Field(None, description="User associated with the connection")
    client_info: Dict[str, Any] = Field(default_factory=dict, description="Client information")


class ErrorEvent(WebSocketEvent):
    """Event for error notifications."""

    event_type: Literal[EventType.ERROR] = Field(default=EventType.ERROR)
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    error_details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    severity: str = Field(default="error", description="Error severity (info, warning, error, critical)")
    component: Optional[str] = Field(None, description="Component that generated the error")


class HeartbeatEvent(WebSocketEvent):
    """Event for WebSocket heartbeat/ping."""

    event_type: Literal[EventType.HEARTBEAT] = Field(default=EventType.HEARTBEAT)
    connection_id: str = Field(..., description="Connection identifier")
    server_timestamp: float = Field(default_factory=time.time, description="Server timestamp")


# Event subscription models
class EventSubscription(BaseModel):
    """Model for event subscription requests."""
    
    event_types: List[EventType] = Field(..., description="List of event types to subscribe to")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Event filters")
    user_id: Optional[str] = Field(None, description="User ID for user-specific events")


class EventFilter(BaseModel):
    """Model for event filtering criteria."""

    agent_types: Optional[List[str]] = Field(None, description="Filter by agent types")
    workflow_types: Optional[List[str]] = Field(None, description="Filter by workflow types")
    user_ids: Optional[List[str]] = Field(None, description="Filter by user IDs")
    severity_levels: Optional[List[str]] = Field(None, description="Filter by error severity levels")
    min_progress: Optional[float] = Field(None, ge=0.0, le=100.0, description="Minimum progress percentage")
    max_progress: Optional[float] = Field(None, ge=0.0, le=100.0, description="Maximum progress percentage")


# Utility functions for event creation
def create_agent_status_event(
    agent_id: str,
    agent_type: str,
    status: AgentStatus,
    instance: Optional[str] = None,
    previous_status: Optional[AgentStatus] = None,
    heartbeat_age: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    source: str = "agent_registry"
) -> AgentStatusEvent:
    """Create an agent status event."""
    return AgentStatusEvent(
        agent_id=agent_id,
        agent_type=agent_type,
        instance=instance,
        status=status,
        previous_status=previous_status,
        heartbeat_age=heartbeat_age,
        metadata=metadata or {},
        source=source
    )


def create_workflow_progress_event(
    workflow_id: str,
    workflow_type: str,
    status: WorkflowStatus,
    progress_percentage: float,
    current_step: Optional[str] = None,
    total_steps: Optional[int] = None,
    completed_steps: Optional[int] = None,
    estimated_completion: Optional[float] = None,
    user_id: Optional[str] = None,
    source: str = "workflow_manager"
) -> WorkflowProgressEvent:
    """Create a workflow progress event."""
    return WorkflowProgressEvent(
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        status=status,
        progress_percentage=progress_percentage,
        current_step=current_step,
        total_steps=total_steps,
        completed_steps=completed_steps,
        estimated_completion=estimated_completion,
        user_id=user_id,
        source=source
    )


def create_progressive_feedback_event(
    operation_id: str,
    operation_type: str,
    stage: str,
    message: str,
    progress_percentage: float,
    intermediate_result: Optional[Dict[str, Any]] = None,
    estimated_remaining: Optional[float] = None,
    user_id: Optional[str] = None,
    source: str = "operation_manager"
) -> ProgressiveFeedbackEvent:
    """Create a progressive feedback event."""
    return ProgressiveFeedbackEvent(
        operation_id=operation_id,
        operation_type=operation_type,
        stage=stage,
        message=message,
        progress_percentage=progress_percentage,
        intermediate_result=intermediate_result,
        estimated_remaining=estimated_remaining,
        user_id=user_id,
        source=source
    )


def create_error_event(
    error_code: str,
    error_message: str,
    error_details: Optional[Dict[str, Any]] = None,
    severity: str = "error",
    component: Optional[str] = None,
    source: str = "system"
) -> ErrorEvent:
    """Create an error event."""
    return ErrorEvent(
        error_code=error_code,
        error_message=error_message,
        error_details=error_details or {},
        severity=severity,
        component=component,
        source=source
    )
