"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Base]]

# Logseq: [[TTA/Components/Gameplay_loop/Base]]
Base classes and interfaces for the Core Gameplay Loop system.

This module provides the foundational abstract classes and interfaces that all
gameplay loop components inherit from, ensuring consistent architecture and
integration with the TTA component system.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from tta_ai.orchestration.service import AgentOrchestrationService

try:
    from src.components.base import Component  # type: ignore[import]
except ImportError:

    class Component(ABC):  # type: ignore[no-redef]  # noqa: B024
        """Stub Component base class when src.components.base is not available."""

        name: str = ""

        def __init__(self, name: str, dependencies: list, config: dict) -> None:
            self.name = name
            self.dependencies = dependencies
            self.config = config

        async def start(self) -> None:  # noqa: B027
            pass

        async def stop(self) -> None:  # noqa: B027
            pass

        async def health_check(self) -> dict:
            return {"status": "unknown"}

        def get_component(self, component_type: type) -> object | None:  # noqa: ARG002
            return None


logger = logging.getLogger(__name__)


class GameplayLoopState(StrEnum):
    """States of the gameplay loop."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    TRANSITIONING = "transitioning"
    COMPLETED = "completed"
    ERROR = "error"


class ComponentPriority(int, Enum):
    """Priority levels for gameplay loop components."""

    CRITICAL = 1  # Core systems that must be available
    HIGH = 2  # Important systems for full functionality
    NORMAL = 3  # Standard gameplay features
    LOW = 4  # Optional enhancements
    BACKGROUND = 5  # Background processing and analytics


@dataclass
class GameplayLoopContext:
    """Context information for gameplay loop operations."""

    session_id: str
    user_id: str
    character_id: str | None = None
    world_id: str | None = None
    current_scene_id: str | None = None

    # Therapeutic context
    therapeutic_goals: list[str] = field(default_factory=list)
    safety_level: str = "standard"  # "standard", "elevated", "crisis"

    # Session state
    session_start_time: datetime = field(default_factory=datetime.utcnow)
    last_activity_time: datetime = field(default_factory=datetime.utcnow)
    total_session_time: float = 0.0

    # Gameplay state
    current_state: GameplayLoopState = GameplayLoopState.INITIALIZING
    narrative_context: dict[str, Any] = field(default_factory=dict)
    choice_history: list[dict[str, Any]] = field(default_factory=list)
    consequence_stack: list[dict[str, Any]] = field(default_factory=list)

    # Performance tracking
    response_times: list[float] = field(default_factory=list)
    error_count: int = 0
    last_error: str | None = None


class GameplayLoopComponent(Component, ABC):  # type: ignore[misc]
    """
    Abstract base class for all gameplay loop components.

    Extends the TTA Component base class with gameplay-specific functionality
    including integration with the agent orchestration system, therapeutic
    context management, and performance monitoring.
    """

    def __init__(
        self,
        name: str,
        priority: ComponentPriority = ComponentPriority.NORMAL,
        dependencies: list[str] | None = None,
        config: dict[str, Any] | None = None,
    ):
        super().__init__(name, dependencies or [], config or {})
        self.priority = priority
        self.gameplay_config = config or {}

        # Agent orchestration integration
        self._agent_orchestration: AgentOrchestrationService | None = None

        # Component state
        self._active_contexts: dict[str, GameplayLoopContext] = {}
        self._performance_metrics: dict[str, Any] = {}

        # Configuration
        self._max_concurrent_sessions = self.gameplay_config.get(
            "max_concurrent_sessions", 100
        )
        self._session_timeout_minutes = self.gameplay_config.get(
            "session_timeout_minutes", 30
        )
        self._enable_performance_tracking = self.gameplay_config.get(
            "enable_performance_tracking", True
        )

        logger.info(
            f"GameplayLoopComponent {name} initialized with priority {priority.name}"
        )

    async def start(self) -> None:
        """Start the gameplay loop component."""
        await super().start()

        # Initialize agent orchestration integration
        try:
            from src.components.agent_orchestration_component import (  # noqa: PLC0415
                AgentOrchestrationComponent,
            )

            orchestration_component = self.get_component(AgentOrchestrationComponent)
            if orchestration_component:
                self._agent_orchestration = orchestration_component.get_service()
                logger.info(f"Component {self.name} connected to agent orchestration")
        except Exception as e:
            logger.warning(
                f"Component {self.name} could not connect to agent orchestration: {e}"
            )

        # Start component-specific initialization
        await self._initialize_component()

        logger.info(f"GameplayLoopComponent {self.name} started successfully")

    async def stop(self) -> None:
        """Stop the gameplay loop component."""
        # Clean up active contexts
        for session_id in list(self._active_contexts.keys()):
            await self._cleanup_session_context(session_id)

        # Component-specific cleanup
        await self._cleanup_component()

        await super().stop()
        logger.info(f"GameplayLoopComponent {self.name} stopped")

    @abstractmethod
    async def _initialize_component(self) -> None:
        """Initialize component-specific resources."""
        pass

    @abstractmethod
    async def _cleanup_component(self) -> None:
        """Clean up component-specific resources."""
        pass

    async def create_session_context(
        self, session_id: str, user_id: str, **kwargs
    ) -> GameplayLoopContext:
        """Create a new gameplay loop context for a session."""
        if session_id in self._active_contexts:
            raise ValueError(f"Session context {session_id} already exists")

        if len(self._active_contexts) >= self._max_concurrent_sessions:
            raise RuntimeError(
                f"Maximum concurrent sessions ({self._max_concurrent_sessions}) reached"
            )

        context = GameplayLoopContext(session_id=session_id, user_id=user_id, **kwargs)

        self._active_contexts[session_id] = context

        # Initialize component-specific context
        await self._initialize_session_context(context)

        logger.info(f"Created session context {session_id} for user {user_id}")
        return context

    async def get_session_context(self, session_id: str) -> GameplayLoopContext | None:
        """Get an existing session context."""
        context = self._active_contexts.get(session_id)
        if context:
            # Update last activity time
            context.last_activity_time = datetime.utcnow()
        return context

    async def update_session_context(
        self, session_id: str, updates: dict[str, Any]
    ) -> bool:
        """Update an existing session context."""
        context = self._active_contexts.get(session_id)
        if not context:
            return False

        # Apply updates
        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)

        context.last_activity_time = datetime.utcnow()

        # Notify component of context update
        await self._on_session_context_updated(context)

        return True

    async def remove_session_context(self, session_id: str) -> bool:
        """Remove a session context."""
        if session_id not in self._active_contexts:
            return False

        await self._cleanup_session_context(session_id)
        del self._active_contexts[session_id]

        logger.info(f"Removed session context {session_id}")
        return True

    @abstractmethod
    async def _initialize_session_context(self, context: GameplayLoopContext) -> None:
        """Initialize component-specific session context."""
        pass

    @abstractmethod
    async def _on_session_context_updated(self, context: GameplayLoopContext) -> None:
        """Handle session context updates."""
        pass

    async def _cleanup_session_context(self, session_id: str) -> None:
        """Clean up a session context."""
        context = self._active_contexts.get(session_id)
        if context:
            # Component-specific cleanup
            await self._cleanup_session_context_impl(context)

            # Update performance metrics
            if self._enable_performance_tracking:
                self._update_performance_metrics(context)

    @abstractmethod
    async def _cleanup_session_context_impl(self, context: GameplayLoopContext) -> None:
        """Component-specific session context cleanup."""
        pass

    def _update_performance_metrics(self, context: GameplayLoopContext) -> None:
        """Update performance metrics for a completed session."""
        session_duration = (
            datetime.utcnow() - context.session_start_time
        ).total_seconds()

        if "sessions" not in self._performance_metrics:
            self._performance_metrics["sessions"] = {
                "total_count": 0,
                "total_duration": 0.0,
                "average_duration": 0.0,
                "error_count": 0,
                "error_rate": 0.0,
            }

        metrics = self._performance_metrics["sessions"]
        metrics["total_count"] += 1
        metrics["total_duration"] += session_duration
        metrics["average_duration"] = metrics["total_duration"] / metrics["total_count"]
        metrics["error_count"] += context.error_count
        metrics["error_rate"] = metrics["error_count"] / metrics["total_count"]

    async def get_agent_orchestration(self) -> AgentOrchestrationService | None:
        """Get the agent orchestration service."""
        return self._agent_orchestration

    def get_active_session_count(self) -> int:
        """Get the number of active sessions."""
        return len(self._active_contexts)

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for this component."""
        return {
            "component_name": self.name,
            "priority": self.priority.name,
            "active_sessions": self.get_active_session_count(),
            "max_concurrent_sessions": self._max_concurrent_sessions,
            "performance_tracking_enabled": self._enable_performance_tracking,
            "metrics": self._performance_metrics.copy(),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform component health check."""
        base_health = await super().health_check()

        # Add gameplay-specific health information
        gameplay_health = {
            "active_sessions": self.get_active_session_count(),
            "session_capacity_usage": self.get_active_session_count()
            / self._max_concurrent_sessions,
            "agent_orchestration_connected": self._agent_orchestration is not None,
            "performance_metrics": self.get_performance_metrics(),
        }

        # Determine health status
        capacity_usage = gameplay_health["session_capacity_usage"]
        if capacity_usage > 0.9:
            gameplay_health["status"] = "warning"
            gameplay_health["message"] = "High session capacity usage"
        elif not gameplay_health["agent_orchestration_connected"]:
            gameplay_health["status"] = "warning"
            gameplay_health["message"] = "Agent orchestration not connected"
        else:
            gameplay_health["status"] = "healthy"

        return {**base_health, **gameplay_health}


class GameplayLoopManager:
    """
    Manager for coordinating multiple gameplay loop components.

    Provides centralized management of gameplay loop components, session
    coordination, and integration with the agent orchestration system.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._components: dict[str, GameplayLoopComponent] = {}
        self._component_priorities: dict[str, ComponentPriority] = {}
        self._is_running = False

        logger.info("GameplayLoopManager initialized")

    def register_component(self, component: GameplayLoopComponent) -> None:
        """Register a gameplay loop component."""
        if component.name in self._components:
            raise ValueError(f"Component {component.name} already registered")

        self._components[component.name] = component
        self._component_priorities[component.name] = component.priority

        logger.info(
            f"Registered component {component.name} with priority {component.priority.name}"
        )

    def get_component(self, name: str) -> GameplayLoopComponent | None:
        """Get a registered component by name."""
        return self._components.get(name)

    def get_components_by_priority(
        self, priority: ComponentPriority
    ) -> list[GameplayLoopComponent]:
        """Get all components with a specific priority."""
        return [
            component
            for component in self._components.values()
            if component.priority == priority
        ]

    async def start(self) -> None:
        """Start all registered components in priority order."""
        if self._is_running:
            return

        # Sort components by priority
        sorted_components = sorted(
            self._components.values(), key=lambda c: c.priority.value
        )

        # Start components in priority order
        for component in sorted_components:
            try:
                await component.start()
                logger.info(f"Started component {component.name}")
            except Exception as e:
                logger.error(f"Failed to start component {component.name}: {e}")
                # For critical components, fail the entire startup
                if component.priority == ComponentPriority.CRITICAL:
                    raise

        self._is_running = True
        logger.info("GameplayLoopManager started successfully")

    async def stop(self) -> None:
        """Stop all registered components in reverse priority order."""
        if not self._is_running:
            return

        # Sort components by reverse priority
        sorted_components = sorted(
            self._components.values(), key=lambda c: c.priority.value, reverse=True
        )

        # Stop components in reverse priority order
        for component in sorted_components:
            try:
                await component.stop()
                logger.info(f"Stopped component {component.name}")
            except Exception as e:
                logger.error(f"Failed to stop component {component.name}: {e}")

        self._is_running = False
        logger.info("GameplayLoopManager stopped")

    async def get_system_health(self) -> dict[str, Any]:
        """Get health status for all components."""
        health_status = {
            "manager_running": self._is_running,
            "total_components": len(self._components),
            "components": {},
        }

        for name, component in self._components.items():
            try:
                component_health = await component.health_check()
                health_status["components"][name] = component_health
            except Exception as e:
                health_status["components"][name] = {"status": "error", "error": str(e)}

        # Determine overall system health
        component_statuses = [
            comp.get("status", "unknown")
            for comp in health_status["components"].values()
        ]

        if "error" in component_statuses:
            health_status["overall_status"] = "error"
        elif "warning" in component_statuses:
            health_status["overall_status"] = "warning"
        else:
            health_status["overall_status"] = "healthy"

        return health_status
