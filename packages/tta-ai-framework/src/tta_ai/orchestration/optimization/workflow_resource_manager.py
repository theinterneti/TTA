"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Optimization/Workflow_resource_manager]]
Workflow resource manager for concurrent workflow optimization.

This module provides efficient resource allocation and scheduling for
multiple simultaneous workflows with load balancing and prioritization.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..realtime.workflow_progress import WorkflowProgressTracker
from .response_time_monitor import ResponseTimeCategory, ResponseTimeCollector

logger = logging.getLogger(__name__)


class WorkflowPriority(str, Enum):
    """Workflow priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ResourceType(str, Enum):
    """Types of resources that can be allocated."""

    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    AGENT_SLOTS = "agent_slots"
    CONCURRENT_WORKFLOWS = "concurrent_workflows"
    MESSAGE_QUEUE_CAPACITY = "message_queue_capacity"


@dataclass
class ResourceAllocation:
    """Resource allocation for a workflow."""

    workflow_id: str
    resource_type: ResourceType
    allocated_amount: float
    max_amount: float
    allocated_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)

    def utilization_percentage(self) -> float:
        """Calculate resource utilization percentage."""
        return (self.allocated_amount / self.max_amount) * 100.0 if self.max_amount > 0 else 0.0


@dataclass
class WorkflowResourceRequest:
    """Resource request for a workflow."""

    workflow_id: str
    workflow_type: str
    priority: WorkflowPriority
    user_id: str | None
    estimated_duration: float | None
    resource_requirements: dict[ResourceType, float]
    max_concurrent_agents: int = 5
    requested_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourcePool:
    """Resource pool for managing available resources."""

    resource_type: ResourceType
    total_capacity: float
    allocated_capacity: float = 0.0
    reserved_capacity: float = 0.0

    def available_capacity(self) -> float:
        """Get available capacity."""
        return self.total_capacity - self.allocated_capacity - self.reserved_capacity

    def utilization_percentage(self) -> float:
        """Get utilization percentage."""
        return (
            ((self.allocated_capacity + self.reserved_capacity) / self.total_capacity) * 100.0
            if self.total_capacity > 0
            else 0.0
        )

    def can_allocate(self, amount: float) -> bool:
        """Check if amount can be allocated."""
        return self.available_capacity() >= amount


class WorkflowScheduler:
    """Schedules workflows based on priority and resource availability."""

    def __init__(
        self,
        max_concurrent_workflows: int = 10,
        priority_weights: dict[WorkflowPriority, float] | None = None,
    ):
        self.max_concurrent_workflows = max_concurrent_workflows
        self.priority_weights = priority_weights or {
            WorkflowPriority.CRITICAL: 4.0,
            WorkflowPriority.HIGH: 3.0,
            WorkflowPriority.NORMAL: 2.0,
            WorkflowPriority.LOW: 1.0,
        }

        # Workflow queues by priority
        self.workflow_queues: dict[WorkflowPriority, deque[WorkflowResourceRequest]] = {
            priority: deque() for priority in WorkflowPriority
        }

        # Currently running workflows
        self.running_workflows: dict[str, WorkflowResourceRequest] = {}

        # Scheduling statistics
        self.total_scheduled = 0
        self.total_completed = 0
        self.total_failed = 0

    def enqueue_workflow(self, request: WorkflowResourceRequest) -> bool:
        """Enqueue a workflow for scheduling."""
        if request.workflow_id in self.running_workflows:
            logger.warning(f"Workflow already running: {request.workflow_id}")
            return False

        # Check if already in queue
        for queue in self.workflow_queues.values():
            if any(w.workflow_id == request.workflow_id for w in queue):
                logger.warning(f"Workflow already queued: {request.workflow_id}")
                return False

        # Add to appropriate priority queue
        self.workflow_queues[request.priority].append(request)
        logger.info(
            f"Enqueued workflow {request.workflow_id} with priority {request.priority.value}"
        )
        return True

    def get_next_workflow(self) -> WorkflowResourceRequest | None:
        """Get the next workflow to schedule based on priority."""
        if len(self.running_workflows) >= self.max_concurrent_workflows:
            return None

        # Check queues in priority order
        for priority in [
            WorkflowPriority.CRITICAL,
            WorkflowPriority.HIGH,
            WorkflowPriority.NORMAL,
            WorkflowPriority.LOW,
        ]:
            queue = self.workflow_queues[priority]
            if queue:
                return queue.popleft()

        return None

    def start_workflow(self, request: WorkflowResourceRequest) -> bool:
        """Mark a workflow as started."""
        if len(self.running_workflows) >= self.max_concurrent_workflows:
            return False

        self.running_workflows[request.workflow_id] = request
        self.total_scheduled += 1
        logger.info(f"Started workflow {request.workflow_id}")
        return True

    def complete_workflow(self, workflow_id: str, success: bool = True) -> bool:
        """Mark a workflow as completed."""
        if workflow_id not in self.running_workflows:
            return False

        self.running_workflows.pop(workflow_id)

        if success:
            self.total_completed += 1
        else:
            self.total_failed += 1

        logger.info(f"Completed workflow {workflow_id} ({'success' if success else 'failed'})")
        return True

    def get_queue_stats(self) -> dict[str, Any]:
        """Get scheduling statistics."""
        return {
            "running_workflows": len(self.running_workflows),
            "max_concurrent": self.max_concurrent_workflows,
            "queued_workflows": {
                priority.value: len(queue) for priority, queue in self.workflow_queues.items()
            },
            "total_queued": sum(len(queue) for queue in self.workflow_queues.values()),
            "total_scheduled": self.total_scheduled,
            "total_completed": self.total_completed,
            "total_failed": self.total_failed,
            "success_rate": self.total_completed / max(1, self.total_scheduled),
        }


class WorkflowResourceManager:
    """Manages resources for concurrent workflow execution."""

    def __init__(
        self,
        workflow_tracker: WorkflowProgressTracker | None = None,
        response_time_collector: ResponseTimeCollector | None = None,
        event_publisher: Any | None = None,
        max_concurrent_workflows: int = 10,
        resource_monitoring_interval: float = 30.0,
    ):
        self.workflow_tracker = workflow_tracker
        self.response_time_collector = response_time_collector
        self.event_publisher = event_publisher
        self.resource_monitoring_interval = resource_monitoring_interval

        # Resource pools
        self.resource_pools: dict[ResourceType, ResourcePool] = {
            ResourceType.CPU: ResourcePool(ResourceType.CPU, 100.0),  # 100% CPU
            ResourceType.MEMORY: ResourcePool(ResourceType.MEMORY, 8192.0),  # 8GB memory
            ResourceType.NETWORK: ResourcePool(ResourceType.NETWORK, 1000.0),  # 1000 Mbps
            ResourceType.AGENT_SLOTS: ResourcePool(
                ResourceType.AGENT_SLOTS, 50.0
            ),  # 50 agent slots
            ResourceType.CONCURRENT_WORKFLOWS: ResourcePool(
                ResourceType.CONCURRENT_WORKFLOWS, float(max_concurrent_workflows)
            ),
            ResourceType.MESSAGE_QUEUE_CAPACITY: ResourcePool(
                ResourceType.MESSAGE_QUEUE_CAPACITY, 10000.0
            ),  # 10k messages
        }

        # Workflow scheduler
        self.scheduler = WorkflowScheduler(max_concurrent_workflows)

        # Resource allocations
        self.allocations: dict[str, list[ResourceAllocation]] = defaultdict(list)

        # Load balancing
        self.load_balancer = WorkflowLoadBalancer()

        # Background tasks
        self._monitoring_task: asyncio.Task | None = None
        self._scheduling_task: asyncio.Task | None = None
        self._is_running = False

        logger.info("WorkflowResourceManager initialized")

    async def start(self) -> None:
        """Start the resource manager."""
        if self._is_running:
            return

        self._is_running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._scheduling_task = asyncio.create_task(self._scheduling_loop())
        logger.info("WorkflowResourceManager started")

    async def stop(self) -> None:
        """Stop the resource manager."""
        if not self._is_running:
            return

        self._is_running = False

        # Cancel background tasks
        for task in [self._monitoring_task, self._scheduling_task]:
            if task:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        logger.info("WorkflowResourceManager stopped")

    async def request_workflow_resources(
        self,
        workflow_id: str,
        workflow_type: str,
        priority: WorkflowPriority = WorkflowPriority.NORMAL,
        user_id: str | None = None,
        estimated_duration: float | None = None,
        resource_requirements: dict[ResourceType, float] | None = None,
        max_concurrent_agents: int = 5,
    ) -> bool:
        """Request resources for a workflow."""
        # Default resource requirements
        if resource_requirements is None:
            resource_requirements = {
                ResourceType.CPU: 10.0,  # 10% CPU
                ResourceType.MEMORY: 512.0,  # 512MB memory
                ResourceType.AGENT_SLOTS: float(max_concurrent_agents),
                ResourceType.CONCURRENT_WORKFLOWS: 1.0,
            }

        # Create resource request
        request = WorkflowResourceRequest(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            priority=priority,
            user_id=user_id,
            estimated_duration=estimated_duration,
            resource_requirements=resource_requirements,
            max_concurrent_agents=max_concurrent_agents,
        )

        # Check if resources can be allocated immediately
        if self._can_allocate_resources(request):
            return await self._allocate_workflow_resources(request)
        # Queue for later scheduling
        return self.scheduler.enqueue_workflow(request)

    async def release_workflow_resources(self, workflow_id: str) -> bool:
        """Release resources allocated to a workflow."""
        if workflow_id not in self.allocations:
            return False

        # Release all allocations for this workflow
        allocations = self.allocations.pop(workflow_id)

        for allocation in allocations:
            pool = self.resource_pools[allocation.resource_type]
            pool.allocated_capacity -= allocation.allocated_amount
            pool.allocated_capacity = max(0.0, pool.allocated_capacity)

        # Mark workflow as completed in scheduler
        self.scheduler.complete_workflow(workflow_id, success=True)

        logger.info(f"Released resources for workflow: {workflow_id}")
        return True

    def _can_allocate_resources(self, request: WorkflowResourceRequest) -> bool:
        """Check if resources can be allocated for a request."""
        for resource_type, amount in request.resource_requirements.items():
            pool = self.resource_pools.get(resource_type)
            if not pool or not pool.can_allocate(amount):
                return False
        return True

    async def _allocate_workflow_resources(self, request: WorkflowResourceRequest) -> bool:
        """Allocate resources for a workflow."""
        if not self._can_allocate_resources(request):
            return False

        # Allocate resources
        allocations = []

        for resource_type, amount in request.resource_requirements.items():
            pool = self.resource_pools[resource_type]

            allocation = ResourceAllocation(
                workflow_id=request.workflow_id,
                resource_type=resource_type,
                allocated_amount=amount,
                max_amount=pool.total_capacity,
            )

            pool.allocated_capacity += amount
            allocations.append(allocation)

        # Store allocations
        self.allocations[request.workflow_id] = allocations

        # Start workflow in scheduler
        self.scheduler.start_workflow(request)

        # Start workflow tracking if available
        if self.workflow_tracker:
            await self.workflow_tracker.start_workflow(
                workflow_type=request.workflow_type,
                workflow_id=request.workflow_id,
                user_id=request.user_id,
                estimated_duration=request.estimated_duration,
            )

        logger.info(f"Allocated resources for workflow: {request.workflow_id}")
        return True

    async def _scheduling_loop(self) -> None:
        """Background scheduling loop."""
        while self._is_running:
            try:
                await asyncio.sleep(1.0)  # Check every second

                # Try to schedule queued workflows
                next_workflow = self.scheduler.get_next_workflow()
                if next_workflow and self._can_allocate_resources(next_workflow):
                    await self._allocate_workflow_resources(next_workflow)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduling loop: {e}")

    async def _monitoring_loop(self) -> None:
        """Background resource monitoring loop."""
        while self._is_running:
            try:
                await asyncio.sleep(self.resource_monitoring_interval)

                # Monitor resource utilization
                await self._monitor_resource_utilization()

                # Clean up stale allocations
                await self._cleanup_stale_allocations()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

    async def _monitor_resource_utilization(self) -> None:
        """Monitor and log resource utilization."""
        for resource_type, pool in self.resource_pools.items():
            utilization = pool.utilization_percentage()

            if utilization > 90.0:  # High utilization warning
                logger.warning(f"High {resource_type.value} utilization: {utilization:.1f}%")

            # Record utilization metric
            if self.response_time_collector:
                self.response_time_collector.record_duration(
                    category=ResponseTimeCategory.SYSTEM_OPERATION,
                    operation=f"resource_utilization_{resource_type.value}",
                    duration=utilization / 100.0,  # Normalize to 0-1
                    metadata={
                        "resource_type": resource_type.value,
                        "utilization_percent": utilization,
                    },
                )

    async def _cleanup_stale_allocations(self) -> None:
        """Clean up allocations for workflows that are no longer active."""
        current_time = time.time()
        stale_threshold = 3600.0  # 1 hour

        stale_workflows = []

        for workflow_id, allocations in self.allocations.items():
            # Check if any allocation is stale
            if allocations and current_time - allocations[0].allocated_at > stale_threshold:
                # Check if workflow is still active in tracker
                if self.workflow_tracker:
                    workflow_status = self.workflow_tracker.get_workflow_status(workflow_id)
                    if not workflow_status:  # Workflow not found in tracker
                        stale_workflows.append(workflow_id)
                else:
                    # No tracker, assume stale after threshold
                    stale_workflows.append(workflow_id)

        # Clean up stale workflows
        for workflow_id in stale_workflows:
            await self.release_workflow_resources(workflow_id)
            logger.info(f"Cleaned up stale workflow: {workflow_id}")

    def get_statistics(self) -> dict[str, Any]:
        """Get resource manager statistics."""
        return {
            "is_running": self._is_running,
            "resource_pools": {
                resource_type.value: {
                    "total_capacity": pool.total_capacity,
                    "allocated_capacity": pool.allocated_capacity,
                    "available_capacity": pool.available_capacity(),
                    "utilization_percent": pool.utilization_percentage(),
                }
                for resource_type, pool in self.resource_pools.items()
            },
            "scheduler_stats": self.scheduler.get_queue_stats(),
            "active_allocations": len(self.allocations),
            "total_allocated_workflows": sum(len(allocs) for allocs in self.allocations.values()),
        }


class WorkflowLoadBalancer:
    """Load balancer for distributing workflows across resources."""

    def __init__(self):
        self.agent_loads: dict[str, float] = defaultdict(float)
        self.workflow_assignments: dict[str, list[str]] = defaultdict(list)

    def assign_agents_to_workflow(
        self,
        workflow_id: str,
        available_agents: list[str],
        required_agents: int,
    ) -> list[str]:
        """Assign agents to a workflow using load balancing."""
        # Sort agents by current load (ascending)
        sorted_agents = sorted(available_agents, key=lambda a: self.agent_loads[a])

        # Assign the least loaded agents
        assigned_agents = sorted_agents[:required_agents]

        # Update load tracking
        for agent_id in assigned_agents:
            self.agent_loads[agent_id] += 1.0
            self.workflow_assignments[workflow_id].append(agent_id)

        return assigned_agents

    def release_agents_from_workflow(self, workflow_id: str) -> None:
        """Release agents assigned to a workflow."""
        assigned_agents = self.workflow_assignments.pop(workflow_id, [])

        for agent_id in assigned_agents:
            self.agent_loads[agent_id] = max(0.0, self.agent_loads[agent_id] - 1.0)

    def get_load_stats(self) -> dict[str, Any]:
        """Get load balancing statistics."""
        return {
            "agent_loads": dict(self.agent_loads),
            "active_assignments": len(self.workflow_assignments),
            "total_assigned_agents": sum(
                len(agents) for agents in self.workflow_assignments.values()
            ),
        }
