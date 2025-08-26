"""
Event publisher for real-time agent orchestration communication.

This module provides a centralized event publishing system that broadcasts
agent status changes, workflow updates, and system events to WebSocket clients
and other subscribers through Redis pub/sub.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Union
from uuid import uuid4

from redis.asyncio import Redis

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
)

logger = logging.getLogger(__name__)


class EventPublisher:
    """Centralized event publisher for real-time communication."""
    
    def __init__(
        self,
        redis_client: Optional[Redis] = None,
        channel_prefix: str = "ao:events",
        enabled: bool = True,
        buffer_size: int = 1000,
        broadcast_agent_status: bool = True,
        broadcast_workflow_progress: bool = True,
        broadcast_system_metrics: bool = False,
    ):
        self.redis_client = redis_client
        self.channel_prefix = channel_prefix.rstrip(":")
        self.enabled = enabled
        self.buffer_size = buffer_size
        self.broadcast_agent_status = broadcast_agent_status
        self.broadcast_workflow_progress = broadcast_workflow_progress
        self.broadcast_system_metrics = broadcast_system_metrics
        
        # Event buffering for reliability
        self.event_buffer: List[WebSocketEvent] = []
        self.buffer_lock = asyncio.Lock()
        
        # Subscriber tracking
        self.websocket_managers: Set[Any] = set()  # WebSocket managers to notify
        
        # Statistics
        self.events_published = 0
        self.events_failed = 0
        self.last_publish_time = 0.0
        
        logger.info(f"EventPublisher initialized: enabled={enabled}, redis={'available' if redis_client else 'unavailable'}")
    
    def add_websocket_manager(self, manager: Any) -> None:
        """Add a WebSocket manager to receive events."""
        self.websocket_managers.add(manager)
        logger.debug(f"Added WebSocket manager: {len(self.websocket_managers)} total")
    
    def remove_websocket_manager(self, manager: Any) -> None:
        """Remove a WebSocket manager."""
        self.websocket_managers.discard(manager)
        logger.debug(f"Removed WebSocket manager: {len(self.websocket_managers)} remaining")
    
    async def publish_agent_status_event(
        self,
        agent_id: str,
        agent_type: str,
        status: Union[AgentStatus, str],
        instance: Optional[str] = None,
        previous_status: Optional[Union[AgentStatus, str]] = None,
        heartbeat_age: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Publish an agent status change event."""
        if not self.enabled or not self.broadcast_agent_status:
            return False
        
        try:
            # Convert string status to enum if needed
            if isinstance(status, str):
                status = AgentStatus(status)
            if isinstance(previous_status, str):
                previous_status = AgentStatus(previous_status)
            
            event = create_agent_status_event(
                agent_id=agent_id,
                agent_type=agent_type,
                status=status,
                instance=instance,
                previous_status=previous_status,
                heartbeat_age=heartbeat_age,
                metadata=metadata,
                source="event_publisher"
            )
            
            return await self._publish_event(event)
            
        except Exception as e:
            logger.error(f"Failed to publish agent status event: {e}")
            return False
    
    async def publish_workflow_progress_event(
        self,
        workflow_id: str,
        workflow_type: str,
        status: Union[WorkflowStatus, str],
        progress_percentage: float,
        current_step: Optional[str] = None,
        total_steps: Optional[int] = None,
        completed_steps: Optional[int] = None,
        estimated_completion: Optional[float] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """Publish a workflow progress event."""
        if not self.enabled or not self.broadcast_workflow_progress:
            return False
        
        try:
            # Convert string status to enum if needed
            if isinstance(status, str):
                status = WorkflowStatus(status)
            
            event = create_workflow_progress_event(
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                status=status,
                progress_percentage=progress_percentage,
                current_step=current_step,
                total_steps=total_steps,
                completed_steps=completed_steps,
                estimated_completion=estimated_completion,
                user_id=user_id,
                source="event_publisher"
            )
            
            return await self._publish_event(event)
            
        except Exception as e:
            logger.error(f"Failed to publish workflow progress event: {e}")
            return False
    
    async def publish_progressive_feedback_event(
        self,
        operation_id: str,
        operation_type: str,
        stage: str,
        message: str,
        progress_percentage: float,
        intermediate_result: Optional[Dict[str, Any]] = None,
        estimated_remaining: Optional[float] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """Publish a progressive feedback event."""
        if not self.enabled:
            return False
        
        try:
            event = create_progressive_feedback_event(
                operation_id=operation_id,
                operation_type=operation_type,
                stage=stage,
                message=message,
                progress_percentage=progress_percentage,
                intermediate_result=intermediate_result,
                estimated_remaining=estimated_remaining,
                user_id=user_id,
                source="event_publisher"
            )
            
            return await self._publish_event(event)
            
        except Exception as e:
            logger.error(f"Failed to publish progressive feedback event: {e}")
            return False
    
    async def publish_system_metrics_event(
        self,
        cpu_usage: Optional[float] = None,
        memory_usage: Optional[float] = None,
        memory_usage_mb: Optional[float] = None,
        active_connections: Optional[int] = None,
        active_workflows: Optional[int] = None,
        message_queue_size: Optional[int] = None,
        response_time_avg: Optional[float] = None,
        error_rate: Optional[float] = None,
    ) -> bool:
        """Publish a system metrics event."""
        if not self.enabled or not self.broadcast_system_metrics:
            return False
        
        try:
            event = SystemMetricsEvent(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                memory_usage_mb=memory_usage_mb,
                active_connections=active_connections,
                active_workflows=active_workflows,
                message_queue_size=message_queue_size,
                response_time_avg=response_time_avg,
                error_rate=error_rate,
                source="event_publisher"
            )
            
            return await self._publish_event(event)
            
        except Exception as e:
            logger.error(f"Failed to publish system metrics event: {e}")
            return False
    
    async def publish_optimization_event(
        self,
        optimization_type: str,
        parameter_name: str,
        old_value: Union[float, int, str],
        new_value: Union[float, int, str],
        improvement_metric: Optional[str] = None,
        improvement_value: Optional[float] = None,
        confidence_score: Optional[float] = None,
    ) -> bool:
        """Publish an optimization event."""
        if not self.enabled:
            return False
        
        try:
            event = OptimizationEvent(
                optimization_type=optimization_type,
                parameter_name=parameter_name,
                old_value=old_value,
                new_value=new_value,
                improvement_metric=improvement_metric,
                improvement_value=improvement_value,
                confidence_score=confidence_score,
                source="event_publisher"
            )
            
            return await self._publish_event(event)
            
        except Exception as e:
            logger.error(f"Failed to publish optimization event: {e}")
            return False
    
    async def _publish_event(self, event: WebSocketEvent) -> bool:
        """Internal method to publish an event to all channels."""
        if not self.enabled:
            return False
        
        success = True
        
        try:
            # Add to buffer for reliability
            async with self.buffer_lock:
                self.event_buffer.append(event)
                if len(self.event_buffer) > self.buffer_size:
                    self.event_buffer.pop(0)  # Remove oldest event
            
            # Publish to Redis if available
            if self.redis_client:
                redis_success = await self._publish_to_redis(event)
                success = success and redis_success
            
            # Broadcast to WebSocket managers
            websocket_success = await self._broadcast_to_websockets(event)
            success = success and websocket_success
            
            # Update statistics
            if success:
                self.events_published += 1
            else:
                self.events_failed += 1
            
            self.last_publish_time = time.time()
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            self.events_failed += 1
            return False
    
    async def _publish_to_redis(self, event: WebSocketEvent) -> bool:
        """Publish event to Redis pub/sub channels."""
        try:
            event_json = event.model_dump_json()
            
            # Publish to general event channel
            await self.redis_client.publish(
                f"{self.channel_prefix}:all",
                event_json
            )
            
            # Publish to event-type specific channel
            await self.redis_client.publish(
                f"{self.channel_prefix}:{event.event_type.value}",
                event_json
            )
            
            # Publish to user-specific channel if user_id is available
            if hasattr(event, 'user_id') and event.user_id:
                await self.redis_client.publish(
                    f"{self.channel_prefix}:user:{event.user_id}",
                    event_json
                )
            
            logger.debug(f"Published event to Redis: {event.event_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish to Redis: {e}")
            return False
    
    async def _broadcast_to_websockets(self, event: WebSocketEvent) -> bool:
        """Broadcast event to all registered WebSocket managers."""
        if not self.websocket_managers:
            return True  # No managers to broadcast to
        
        success_count = 0
        total_count = len(self.websocket_managers)
        
        # Create tasks for concurrent broadcasting
        tasks = []
        for manager in list(self.websocket_managers):  # Copy to avoid modification during iteration
            task = asyncio.create_task(self._broadcast_to_manager(manager, event))
            tasks.append(task)
        
        # Wait for all broadcasts to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for result in results if result is True)
        
        logger.debug(f"Broadcasted event to {success_count}/{total_count} WebSocket managers")
        return success_count == total_count
    
    async def _broadcast_to_manager(self, manager: Any, event: WebSocketEvent) -> bool:
        """Broadcast event to a single WebSocket manager."""
        try:
            if hasattr(manager, 'broadcast_event'):
                sent_count = await manager.broadcast_event(event)
                return sent_count >= 0  # Consider success if no error occurred
            else:
                logger.warning(f"WebSocket manager does not have broadcast_event method")
                return False
        except Exception as e:
            logger.error(f"Failed to broadcast to WebSocket manager: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event publisher statistics."""
        return {
            "enabled": self.enabled,
            "events_published": self.events_published,
            "events_failed": self.events_failed,
            "last_publish_time": self.last_publish_time,
            "buffer_size": len(self.event_buffer),
            "websocket_managers": len(self.websocket_managers),
            "configuration": {
                "channel_prefix": self.channel_prefix,
                "buffer_size": self.buffer_size,
                "broadcast_agent_status": self.broadcast_agent_status,
                "broadcast_workflow_progress": self.broadcast_workflow_progress,
                "broadcast_system_metrics": self.broadcast_system_metrics,
            }
        }
    
    async def get_recent_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent events from the buffer."""
        async with self.buffer_lock:
            recent_events = self.event_buffer[-count:] if count > 0 else self.event_buffer[:]
            return [event.model_dump() for event in recent_events]
    
    async def shutdown(self) -> None:
        """Shutdown the event publisher."""
        logger.info("Shutting down event publisher")
        self.enabled = False
        self.websocket_managers.clear()
        
        async with self.buffer_lock:
            self.event_buffer.clear()
