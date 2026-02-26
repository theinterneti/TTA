"""

# Logseq: [[TTA.dev/Agent_orchestration/Performance/Optimization]]
Intelligent agent coordination optimization with predictive scheduling.

This module provides advanced optimization algorithms for agent coordination,
predictive scheduling, and performance optimization to achieve sub-2-second response times.
"""

from __future__ import annotations

import asyncio
import contextlib
import heapq
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from ..models import AgentType
from .response_time_monitor import ResponseTimeMonitor

logger = logging.getLogger(__name__)


class OptimizationStrategy(StrEnum):
    """Optimization strategies."""

    FASTEST_FIRST = "fastest_first"
    LOAD_BALANCED = "load_balanced"
    PREDICTIVE = "predictive"
    ADAPTIVE = "adaptive"


class AgentLoadLevel(StrEnum):
    """Agent load levels."""

    IDLE = "idle"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    OVERLOADED = "overloaded"


@dataclass
class AgentPerformanceProfile:
    """Performance profile for an agent."""

    agent_id: str
    agent_type: AgentType
    average_response_time: float
    success_rate: float
    current_load: int
    max_concurrent: int
    last_activity: float
    performance_trend: float  # Positive = improving, negative = degrading
    reliability_score: float  # 0.0 to 1.0

    @property
    def load_level(self) -> AgentLoadLevel:
        """Calculate current load level."""
        if self.current_load == 0:
            return AgentLoadLevel.IDLE

        load_ratio = self.current_load / max(self.max_concurrent, 1)

        if load_ratio >= 1.0:
            return AgentLoadLevel.OVERLOADED
        if load_ratio >= 0.8:
            return AgentLoadLevel.HIGH
        if load_ratio >= 0.5:
            return AgentLoadLevel.MEDIUM
        return AgentLoadLevel.LOW

    @property
    def efficiency_score(self) -> float:
        """Calculate efficiency score (lower response time + higher success rate = better)."""
        if self.average_response_time <= 0:
            return 0.0

        # Normalize response time (assume 5s is worst case)
        time_score = max(0, 1 - (self.average_response_time / 5.0))

        # Combine with success rate and reliability
        return time_score * 0.4 + self.success_rate * 0.4 + self.reliability_score * 0.2


@dataclass
class WorkflowRequest:
    """Workflow execution request."""

    request_id: str
    workflow_type: str
    priority: int  # 1 (highest) to 5 (lowest)
    estimated_duration: float
    required_agents: list[AgentType]
    user_id: str | None = None
    deadline: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SchedulingDecision:
    """Agent scheduling decision."""

    request_id: str
    selected_agents: dict[AgentType, str]  # agent_type -> agent_id
    estimated_completion_time: float
    confidence: float
    reasoning: str


class IntelligentAgentCoordinator:
    """Intelligent agent coordination with predictive scheduling."""

    def __init__(
        self,
        response_time_monitor: ResponseTimeMonitor,
        optimization_strategy: OptimizationStrategy = OptimizationStrategy.ADAPTIVE,
        target_response_time: float = 2.0,
    ):
        self.response_time_monitor = response_time_monitor
        self.optimization_strategy = optimization_strategy
        self.target_response_time = target_response_time

        # Agent tracking
        self.agent_profiles: dict[str, AgentPerformanceProfile] = {}
        self.agent_queues: dict[str, deque] = defaultdict(deque)
        self.active_requests: dict[str, WorkflowRequest] = {}

        # Scheduling queue (priority queue)
        self.scheduling_queue: list[tuple[float, WorkflowRequest]] = []

        # Performance tracking
        self.optimization_history: deque = deque(maxlen=1000)
        self.prediction_accuracy: deque = deque(maxlen=100)

        # Background tasks
        self.scheduler_task: asyncio.Task | None = None
        self.profile_update_task: asyncio.Task | None = None
        self.is_running = False

        logger.info("IntelligentAgentCoordinator initialized")

    async def start(self) -> None:
        """Start the intelligent coordinator."""
        if self.is_running:
            return

        self.is_running = True

        # Start background tasks
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.profile_update_task = asyncio.create_task(self._profile_update_loop())

        logger.info("IntelligentAgentCoordinator started")

    async def stop(self) -> None:
        """Stop the intelligent coordinator."""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel background tasks
        for task in [self.scheduler_task, self.profile_update_task]:
            if task:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        logger.info("IntelligentAgentCoordinator stopped")

    def register_agent(
        self, agent_id: str, agent_type: AgentType, max_concurrent: int = 5
    ) -> None:
        """Register an agent with the coordinator."""
        profile = AgentPerformanceProfile(
            agent_id=agent_id,
            agent_type=agent_type,
            average_response_time=1.0,  # Default
            success_rate=1.0,  # Default
            current_load=0,
            max_concurrent=max_concurrent,
            last_activity=time.time(),
            performance_trend=0.0,
            reliability_score=1.0,
        )

        self.agent_profiles[agent_id] = profile
        logger.info(f"Registered agent {agent_id} ({agent_type.value})")

    async def schedule_workflow(self, request: WorkflowRequest) -> SchedulingDecision:
        """Schedule a workflow for execution."""
        # Add to scheduling queue with priority
        priority_score = self._calculate_priority_score(request)
        heapq.heappush(self.scheduling_queue, (priority_score, request))

        # Immediate scheduling attempt
        decision = await self._make_scheduling_decision(request)

        if decision:
            # Reserve agents
            await self._reserve_agents(decision)
            self.active_requests[request.request_id] = request

        return decision

    async def _make_scheduling_decision(
        self, request: WorkflowRequest
    ) -> SchedulingDecision | None:
        """Make intelligent scheduling decision for a request."""
        if self.optimization_strategy == OptimizationStrategy.FASTEST_FIRST:
            return await self._schedule_fastest_first(request)
        if self.optimization_strategy == OptimizationStrategy.LOAD_BALANCED:
            return await self._schedule_load_balanced(request)
        if self.optimization_strategy == OptimizationStrategy.PREDICTIVE:
            return await self._schedule_predictive(request)
        # ADAPTIVE
        return await self._schedule_adaptive(request)

    async def _schedule_fastest_first(
        self, request: WorkflowRequest
    ) -> SchedulingDecision | None:
        """Schedule using fastest available agents."""
        selected_agents = {}
        total_estimated_time = 0.0

        for agent_type in request.required_agents:
            # Find fastest available agent of this type
            available_agents = [
                profile
                for profile in self.agent_profiles.values()
                if (
                    profile.agent_type == agent_type
                    and profile.load_level != AgentLoadLevel.OVERLOADED
                )
            ]

            if not available_agents:
                return None  # No available agents

            # Sort by efficiency score (fastest + most reliable)
            available_agents.sort(key=lambda a: a.efficiency_score, reverse=True)
            best_agent = available_agents[0]

            selected_agents[agent_type] = best_agent.agent_id
            total_estimated_time = max(
                total_estimated_time, best_agent.average_response_time
            )

        return SchedulingDecision(
            request_id=request.request_id,
            selected_agents=selected_agents,
            estimated_completion_time=total_estimated_time,
            confidence=0.8,
            reasoning="Selected fastest available agents",
        )

    async def _schedule_load_balanced(
        self, request: WorkflowRequest
    ) -> SchedulingDecision | None:
        """Schedule using load balancing."""
        selected_agents = {}
        total_estimated_time = 0.0

        for agent_type in request.required_agents:
            # Find least loaded available agent of this type
            available_agents = [
                profile
                for profile in self.agent_profiles.values()
                if (
                    profile.agent_type == agent_type
                    and profile.load_level != AgentLoadLevel.OVERLOADED
                )
            ]

            if not available_agents:
                return None

            # Sort by load level (least loaded first)
            available_agents.sort(key=lambda a: a.current_load)
            best_agent = available_agents[0]

            selected_agents[agent_type] = best_agent.agent_id

            # Estimate completion time considering current load
            load_factor = 1.0 + (
                best_agent.current_load * 0.2
            )  # 20% penalty per concurrent task
            estimated_time = best_agent.average_response_time * load_factor
            total_estimated_time = max(total_estimated_time, estimated_time)

        return SchedulingDecision(
            request_id=request.request_id,
            selected_agents=selected_agents,
            estimated_completion_time=total_estimated_time,
            confidence=0.7,
            reasoning="Selected least loaded agents",
        )

    async def _schedule_predictive(
        self, request: WorkflowRequest
    ) -> SchedulingDecision | None:
        """Schedule using predictive algorithms."""
        selected_agents = {}
        total_estimated_time = 0.0
        confidence_scores = []

        for agent_type in request.required_agents:
            available_agents = [
                profile
                for profile in self.agent_profiles.values()
                if (
                    profile.agent_type == agent_type
                    and profile.load_level != AgentLoadLevel.OVERLOADED
                )
            ]

            if not available_agents:
                return None

            # Predict performance for each agent
            best_agent = None
            best_predicted_time = float("inf")
            best_confidence = 0.0

            for agent in available_agents:
                predicted_time, confidence = self._predict_agent_performance(
                    agent, request.estimated_duration
                )

                if predicted_time < best_predicted_time:
                    best_predicted_time = predicted_time
                    best_agent = agent
                    best_confidence = confidence

            if best_agent:
                selected_agents[agent_type] = best_agent.agent_id
                total_estimated_time = max(total_estimated_time, best_predicted_time)
                confidence_scores.append(best_confidence)

        overall_confidence = (
            statistics.mean(confidence_scores) if confidence_scores else 0.0
        )

        return SchedulingDecision(
            request_id=request.request_id,
            selected_agents=selected_agents,
            estimated_completion_time=total_estimated_time,
            confidence=overall_confidence,
            reasoning="Selected agents using predictive performance modeling",
        )

    async def _schedule_adaptive(
        self, request: WorkflowRequest
    ) -> SchedulingDecision | None:
        """Schedule using adaptive strategy based on current conditions."""
        # Analyze current system state
        system_load = self._calculate_system_load()
        performance_variance = self._calculate_performance_variance()

        # Choose strategy based on conditions
        if system_load < 0.3:  # Low load - prioritize speed
            return await self._schedule_fastest_first(request)
        if system_load > 0.8:  # High load - balance load
            return await self._schedule_load_balanced(request)
        if performance_variance > 0.5:  # High variance - use prediction
            return await self._schedule_predictive(request)
        # Balanced conditions - use load balancing
        return await self._schedule_load_balanced(request)

    def _predict_agent_performance(
        self, agent: AgentPerformanceProfile, estimated_duration: float
    ) -> tuple[float, float]:
        """Predict agent performance for a given task."""
        # Base prediction on historical performance
        base_time = agent.average_response_time

        # Adjust for current load
        load_factor = 1.0 + (agent.current_load * 0.15)

        # Adjust for performance trend
        trend_factor = 1.0 - (agent.performance_trend * 0.1)

        # Adjust for task complexity (estimated duration)
        complexity_factor = 1.0 + max(0, (estimated_duration - 1.0) * 0.1)

        predicted_time = base_time * load_factor * trend_factor * complexity_factor

        # Calculate confidence based on reliability and recent activity
        time_since_activity = time.time() - agent.last_activity
        activity_factor = max(
            0.5, 1.0 - (time_since_activity / 3600)
        )  # Decay over 1 hour

        confidence = agent.reliability_score * activity_factor

        return predicted_time, confidence

    def _calculate_priority_score(self, request: WorkflowRequest) -> float:
        """Calculate priority score for scheduling queue."""
        # Lower score = higher priority
        base_priority = request.priority

        # Adjust for deadline urgency
        if request.deadline:
            time_to_deadline = request.deadline - time.time()
            urgency_factor = max(
                0.1, 1.0 / max(time_to_deadline / 60, 1)
            )  # Minutes to deadline
            base_priority *= urgency_factor

        return base_priority

    def _calculate_system_load(self) -> float:
        """Calculate overall system load."""
        if not self.agent_profiles:
            return 0.0

        total_load = sum(
            profile.current_load / max(profile.max_concurrent, 1)
            for profile in self.agent_profiles.values()
        )

        return total_load / len(self.agent_profiles)

    def _calculate_performance_variance(self) -> float:
        """Calculate performance variance across agents."""
        if len(self.agent_profiles) < 2:
            return 0.0

        response_times = [
            profile.average_response_time for profile in self.agent_profiles.values()
        ]

        try:
            return statistics.stdev(response_times) / statistics.mean(response_times)
        except (statistics.StatisticsError, ZeroDivisionError):
            return 0.0

    async def _reserve_agents(self, decision: SchedulingDecision) -> None:
        """Reserve agents for a scheduling decision."""
        for agent_id in decision.selected_agents.values():
            if agent_id in self.agent_profiles:
                self.agent_profiles[agent_id].current_load += 1

    async def _release_agents(self, decision: SchedulingDecision) -> None:
        """Release agents after workflow completion."""
        for agent_id in decision.selected_agents.values():
            if agent_id in self.agent_profiles:
                self.agent_profiles[agent_id].current_load = max(
                    0, self.agent_profiles[agent_id].current_load - 1
                )
                self.agent_profiles[agent_id].last_activity = time.time()

    async def _scheduler_loop(self) -> None:
        """Background scheduler loop."""
        while self.is_running:
            try:
                # Process scheduling queue
                while self.scheduling_queue:
                    priority_score, request = heapq.heappop(self.scheduling_queue)

                    # Try to schedule if not already scheduled
                    if request.request_id not in self.active_requests:
                        decision = await self._make_scheduling_decision(request)
                        if decision:
                            await self._reserve_agents(decision)
                            self.active_requests[request.request_id] = request

                await asyncio.sleep(1.0)  # Check every second

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(5.0)

    async def _profile_update_loop(self) -> None:
        """Background task to update agent profiles."""
        while self.is_running:
            try:
                await self._update_agent_profiles()
                await asyncio.sleep(30.0)  # Update every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in profile update loop: {e}")
                await asyncio.sleep(30.0)

    async def _update_agent_profiles(self) -> None:
        """Update agent performance profiles from monitoring data."""
        # Get recent performance statistics
        statistics = self.response_time_monitor.get_statistics(time_window_minutes=10)

        for agent_id, profile in self.agent_profiles.items():
            # Update profile based on recent performance
            agent_stats = None
            for op_type, stats in statistics.items():
                # This is a simplified approach - in practice, you'd need to
                # correlate operation types with specific agents
                if op_type.value in agent_id.lower():
                    agent_stats = stats
                    break

            if agent_stats:
                # Update performance metrics
                old_response_time = profile.average_response_time
                profile.average_response_time = agent_stats.average_duration
                profile.success_rate = agent_stats.success_rate

                # Calculate performance trend
                profile.performance_trend = (
                    old_response_time - profile.average_response_time
                ) / max(old_response_time, 0.1)

                # Update reliability score based on success rate and consistency
                profile.reliability_score = min(1.0, agent_stats.success_rate * 1.1)

    def get_optimization_statistics(self) -> dict[str, Any]:
        """Get optimization statistics."""
        return {
            "registered_agents": len(self.agent_profiles),
            "active_requests": len(self.active_requests),
            "queued_requests": len(self.scheduling_queue),
            "optimization_strategy": self.optimization_strategy.value,
            "target_response_time": self.target_response_time,
            "system_load": self._calculate_system_load(),
            "performance_variance": self._calculate_performance_variance(),
            "agent_profiles": {
                agent_id: {
                    "agent_type": profile.agent_type.value,
                    "average_response_time": profile.average_response_time,
                    "success_rate": profile.success_rate,
                    "current_load": profile.current_load,
                    "load_level": profile.load_level.value,
                    "efficiency_score": profile.efficiency_score,
                    "reliability_score": profile.reliability_score,
                }
                for agent_id, profile in self.agent_profiles.items()
            },
        }
