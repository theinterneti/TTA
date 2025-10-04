"""
Core Gameplay Loop Component

This component provides the main integration point for the therapeutic text adventure
gameplay loop system, coordinating narrative presentation, choice architecture,
consequence systems, and session management.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from ..orchestration.component import Component, ComponentStatus
from ..orchestration.decorators import log_entry_exit, require_config, timing_decorator
from .gameplay_loop import GameplayLoopController

logger = logging.getLogger(__name__)


class GameplayLoopComponent(Component):
    """
    TTA Component wrapper for the Core Gameplay Loop system.

    This component manages the lifecycle of the GameplayLoopController and integrates
    it with the TTA orchestration system, providing session management, narrative
    progression, choice processing, and therapeutic consequence generation.
    """

    def __init__(self, config: Any):
        """
        Initialize the Gameplay Loop component.

        Args:
            config: Configuration object
        """
        super().__init__(
            config,
            name="core_gameplay_loop",
            dependencies=[
                "tta.prototype_neo4j"
            ],  # Depends on Neo4j for data persistence
        )

        self.root_dir = Path(__file__).parent.parent.parent
        self.gameplay_controller: GameplayLoopController | None = None

        # Get Gameplay Loop configuration
        self.enabled = self.config.get("core_gameplay_loop.enabled", True)
        self.max_concurrent_sessions = self.config.get(
            "core_gameplay_loop.max_concurrent_sessions", 100
        )
        self.session_timeout_minutes = self.config.get(
            "core_gameplay_loop.session_timeout_minutes", 30
        )
        self.performance_tracking = self.config.get(
            "core_gameplay_loop.enable_performance_tracking", True
        )

        # Component-specific configuration
        self.narrative_config = self.config.get(
            "core_gameplay_loop.narrative_engine", {}
        )
        self.choice_config = self.config.get(
            "core_gameplay_loop.choice_architecture", {}
        )
        self.consequence_config = self.config.get(
            "core_gameplay_loop.consequence_system", {}
        )
        self.session_config = self.config.get("core_gameplay_loop.session_manager", {})

        # Database configuration
        self.neo4j_config = {
            "uri": f"bolt://localhost:{self.config.get('tta.prototype.components.neo4j.port', 7688)}",
            "username": self.config.get(
                "tta.prototype.components.neo4j.username", "neo4j"
            ),
            "password": self.config.get(
                "tta.prototype.components.neo4j.password", "password"
            ),
        }

        self.redis_config = {
            "host": "localhost",
            "port": 6379,
            "db": 2,  # Use separate database for gameplay loop
        }

        logger.info(f"Initialized Gameplay Loop component (enabled: {self.enabled})")

    @log_entry_exit
    @timing_decorator
    @require_config(["core_gameplay_loop.enabled"])
    def _start_impl(self) -> bool:
        """
        Start the Gameplay Loop component.

        Returns:
            bool: True if started successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Gameplay Loop component is disabled")
            self.status = ComponentStatus.STOPPED
            return True

        try:
            logger.info("Starting Gameplay Loop component...")

            # Create gameplay controller configuration
            controller_config = {
                "database": {
                    "neo4j_uri": self.neo4j_config["uri"],
                    "neo4j_user": self.neo4j_config["username"],
                    "neo4j_password": self.neo4j_config["password"],
                    "redis_host": self.redis_config["host"],
                    "redis_port": self.redis_config["port"],
                    "redis_db": self.redis_config["db"],
                },
                "narrative": {
                    "complexity_adaptation_enabled": self.narrative_config.get(
                        "complexity_adaptation", True
                    ),
                    "immersion_tracking_enabled": self.narrative_config.get(
                        "immersion_tracking", True
                    ),
                    "max_description_length": self.narrative_config.get(
                        "max_description_length", 2000
                    ),
                    "min_description_length": self.narrative_config.get(
                        "min_description_length", 100
                    ),
                },
                "choice_architecture": {
                    "min_choices": self.choice_config.get("min_choices", 2),
                    "max_choices": self.choice_config.get("max_choices", 5),
                    "therapeutic_weighting": self.choice_config.get(
                        "therapeutic_weighting", 0.4
                    ),
                    "agency_protection_enabled": True,
                    "therapeutic_validation_enabled": True,
                },
                "consequence_system": {
                    "learning_emphasis_enabled": self.consequence_config.get(
                        "learning_emphasis", True
                    ),
                    "pattern_tracking_enabled": self.consequence_config.get(
                        "pattern_tracking", True
                    ),
                    "therapeutic_framing_enabled": self.consequence_config.get(
                        "therapeutic_framing", True
                    ),
                    "causality_explanation_enabled": True,
                    "progress_tracking_enabled": True,
                },
                "session_management": {
                    "auto_save_interval": self.session_config.get(
                        "auto_save_interval", 60
                    ),
                    "context_preservation": self.session_config.get(
                        "context_preservation", True
                    ),
                    "therapeutic_goal_tracking": self.session_config.get(
                        "therapeutic_goal_tracking", True
                    ),
                },
                "response_time_target": 2.0,
                "session_timeout": self.session_timeout_minutes * 60,
                "max_concurrent_sessions": self.max_concurrent_sessions,
                "performance_tracking_enabled": self.performance_tracking,
            }

            # Create and initialize gameplay controller
            self.gameplay_controller = GameplayLoopController(controller_config)

            # Initialize controller asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                initialization_success = loop.run_until_complete(
                    self.gameplay_controller.initialize()
                )

                if not initialization_success:
                    logger.error("Failed to initialize GameplayLoopController")
                    return False

                logger.info("Gameplay Loop component started successfully")
                return True

            finally:
                loop.close()

        except Exception as e:
            logger.error(f"Failed to start Gameplay Loop component: {e}")
            return False

    @log_entry_exit
    @timing_decorator
    def _stop_impl(self) -> bool:
        """
        Stop the Gameplay Loop component.

        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            logger.info("Stopping Gameplay Loop component...")

            if self.gameplay_controller:
                # Clean up active sessions
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    # End all active sessions gracefully
                    active_session_ids = list(
                        self.gameplay_controller.active_sessions.keys()
                    )
                    for session_id in active_session_ids:
                        loop.run_until_complete(
                            self.gameplay_controller.end_session(session_id)
                        )

                    logger.info(f"Ended {len(active_session_ids)} active sessions")

                finally:
                    loop.close()

                self.gameplay_controller = None

            logger.info("Gameplay Loop component stopped successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to stop Gameplay Loop component: {e}")
            return False

    def get_controller(self) -> GameplayLoopController | None:
        """
        Get the GameplayLoopController instance.

        Returns:
            Optional[GameplayLoopController]: The controller instance if available
        """
        return self.gameplay_controller

    def get_status_info(self) -> dict[str, Any]:
        """
        Get detailed status information about the component.

        Returns:
            Dict[str, Any]: Status information
        """
        base_info = {
            "name": self.name,
            "status": self.status.value,
            "enabled": self.enabled,
            "dependencies": self.dependencies,
        }

        if self.gameplay_controller:
            base_info.update(
                {
                    "active_sessions": len(self.gameplay_controller.active_sessions),
                    "max_concurrent_sessions": self.max_concurrent_sessions,
                    "session_timeout_minutes": self.session_timeout_minutes,
                    "performance_tracking": self.performance_tracking,
                }
            )

        return base_info

    async def get_session_metrics(self) -> dict[str, Any]:
        """
        Get session metrics from the gameplay controller.

        Returns:
            Dict[str, Any]: Session metrics
        """
        if not self.gameplay_controller:
            return {"error": "Controller not available"}

        try:
            active_sessions = len(self.gameplay_controller.active_sessions)

            # Calculate session statistics
            session_stats = {
                "active_sessions": active_sessions,
                "max_concurrent_sessions": self.max_concurrent_sessions,
                "session_utilization": (
                    active_sessions / self.max_concurrent_sessions
                    if self.max_concurrent_sessions > 0
                    else 0
                ),
                "sessions_by_status": {},
            }

            # Get detailed session information
            for _, session in self.gameplay_controller.active_sessions.items():
                status = "active" if session.is_active else "inactive"
                session_stats["sessions_by_status"][status] = (
                    session_stats["sessions_by_status"].get(status, 0) + 1
                )

            return session_stats

        except Exception as e:
            logger.error(f"Failed to get session metrics: {e}")
            return {"error": str(e)}

    async def cleanup_inactive_sessions(self) -> int:
        """
        Clean up inactive sessions.

        Returns:
            int: Number of sessions cleaned up
        """
        if not self.gameplay_controller:
            return 0

        try:
            return await self.gameplay_controller.cleanup_inactive_sessions()
        except Exception as e:
            logger.error(f"Failed to cleanup inactive sessions: {e}")
            return 0

    # Integration methods for TTA systems
    async def create_gameplay_session(
        self, user_id: str, therapeutic_context: dict[str, Any] | None = None
    ) -> str | None:
        """
        Create a new gameplay session.

        Args:
            user_id: User identifier
            therapeutic_context: Optional therapeutic context and goals

        Returns:
            Session ID if successful, None otherwise
        """
        if not self.gameplay_controller:
            logger.error("Gameplay controller not available")
            return None

        try:
            session = await self.gameplay_controller.start_session(
                user_id=user_id, therapeutic_context=therapeutic_context
            )
            return session.session_id if session else None
        except Exception as e:
            logger.error(f"Failed to create gameplay session: {e}")
            return None

    async def process_user_choice(
        self, session_id: str, choice_id: str
    ) -> dict[str, Any] | None:
        """
        Process a user choice within a gameplay session.

        Args:
            session_id: Session identifier
            choice_id: ID of the choice made by the user

        Returns:
            Response data if successful, None otherwise
        """
        if not self.gameplay_controller:
            logger.error("Gameplay controller not available")
            return None

        try:
            next_scene, new_choices, consequences = (
                await self.gameplay_controller.process_user_choice(
                    session_id, choice_id
                )
            )

            return {
                "next_scene": next_scene.model_dump() if next_scene else None,
                "available_choices": [choice.model_dump() for choice in new_choices],
                "consequences": consequences.model_dump() if consequences else None,
            }
        except Exception as e:
            logger.error(f"Failed to process user choice: {e}")
            return {"error": str(e)}

    async def get_session_status(self, session_id: str) -> dict[str, Any] | None:
        """Get the status of a gameplay session."""
        if not self.gameplay_controller:
            return None

        try:
            return await self.gameplay_controller.get_session_status(session_id)
        except Exception as e:
            logger.error(f"Failed to get session status: {e}")
            return None

    async def resume_session(self, session_id: str) -> dict[str, Any] | None:
        """Resume a paused gameplay session."""
        if not self.gameplay_controller:
            return None

        try:
            session = await self.gameplay_controller.resume_session(session_id)
            if session:
                return {
                    "session_id": session.session_id,
                    "current_scene": (
                        session.current_scene.model_dump()
                        if session.current_scene
                        else None
                    ),
                    "available_choices": [
                        choice.model_dump() for choice in session.available_choices
                    ],
                    "session_recap": session.session_recap,
                }
            return None
        except Exception as e:
            logger.error(f"Failed to resume session: {e}")
            return None

    async def pause_session(self, session_id: str) -> bool:
        """Pause a gameplay session."""
        if not self.gameplay_controller:
            return False

        try:
            return await self.gameplay_controller.pause_session(session_id)
        except Exception as e:
            logger.error(f"Failed to pause session: {e}")
            return False

    async def end_session(self, session_id: str) -> bool:
        """End a gameplay session."""
        if not self.gameplay_controller:
            return False

        try:
            return await self.gameplay_controller.end_session(session_id)
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False

    def health_check(self) -> dict[str, Any]:
        """Perform component health check."""
        base_health = {
            "name": self.name,
            "status": self.status.value,
            "enabled": self.enabled,
        }

        if not self.enabled:
            return {**base_health, "status": "disabled"}

        if not self.gameplay_controller:
            return {
                **base_health,
                "status": "error",
                "message": "Controller not initialized",
            }

        try:
            # Basic health check
            active_sessions = len(self.gameplay_controller.active_sessions)

            return {
                **base_health,
                "status": "healthy",
                "active_sessions": active_sessions,
                "max_concurrent_sessions": self.max_concurrent_sessions,
                "session_utilization": (
                    active_sessions / self.max_concurrent_sessions
                    if self.max_concurrent_sessions > 0
                    else 0
                ),
            }

        except Exception as e:
            return {
                **base_health,
                "status": "error",
                "message": f"Health check failed: {e}",
            }
