"""
Core Gameplay Loop Component

This component provides the main integration point for the therapeutic text adventure
gameplay loop system, coordinating narrative presentation, choice architecture,
consequence systems, and session management.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Dict, Any, Optional, List

from src.components.base import Component
from .gameplay_loop.base import GameplayLoopManager, ComponentPriority
from .gameplay_loop.session_manager import SessionManager
from .gameplay_loop.narrative_engine import NarrativeEngine
from .gameplay_loop.choice_architecture import ChoiceArchitectureManager
from .gameplay_loop.consequence_system import ConsequenceSystem

logger = logging.getLogger(__name__)


class GameplayLoopComponent(Component):
    """
    Main component for the Core Gameplay Loop system.
    
    Integrates with the TTA component system to provide therapeutic text adventure
    gameplay mechanics including narrative presentation, choice architecture,
    consequence systems, and session management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="GameplayLoopComponent",
            dependencies=["AgentOrchestrationComponent"],  # Depends on agent orchestration
            config=config or {}
        )
        
        # Configuration
        self.gameplay_config = self.config.get("core_gameplay_loop", {})
        self.enabled = self.gameplay_config.get("enabled", True)
        
        # Core manager
        self._manager: Optional[GameplayLoopManager] = None
        
        # Component instances
        self._session_manager: Optional[SessionManager] = None
        self._narrative_engine: Optional[NarrativeEngine] = None
        self._choice_architecture: Optional[ChoiceArchitectureManager] = None
        self._consequence_system: Optional[ConsequenceSystem] = None
        
        logger.info("GameplayLoopComponent initialized")
    
    async def start(self) -> None:
        """Start the gameplay loop component."""
        if not self.enabled:
            logger.info("GameplayLoopComponent is disabled")
            return
        
        await super().start()
        
        try:
            # Initialize the gameplay loop manager
            self._manager = GameplayLoopManager(config=self.gameplay_config)
            
            # Create and register core components
            await self._initialize_core_components()
            
            # Start the manager (which starts all registered components)
            await self._manager.start()
            
            logger.info("GameplayLoopComponent started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start GameplayLoopComponent: {e}")
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Stop the gameplay loop component."""
        try:
            if self._manager:
                await self._manager.stop()
                self._manager = None
            
            # Clear component references
            self._session_manager = None
            self._narrative_engine = None
            self._choice_architecture = None
            self._consequence_system = None
            
            await super().stop()
            logger.info("GameplayLoopComponent stopped")
            
        except Exception as e:
            logger.error(f"Error stopping GameplayLoopComponent: {e}")
    
    async def _initialize_core_components(self) -> None:
        """Initialize and register core gameplay loop components."""
        
        # Session Manager (Critical - must be available)
        session_config = self.gameplay_config.get("session_manager", {})
        if session_config.get("enabled", True):
            self._session_manager = SessionManager(
                name="SessionManager",
                priority=ComponentPriority.CRITICAL,
                config=session_config
            )
            self._manager.register_component(self._session_manager)
        
        # Narrative Engine (High priority - core gameplay)
        narrative_config = self.gameplay_config.get("narrative_engine", {})
        if narrative_config.get("enabled", True):
            self._narrative_engine = NarrativeEngine(
                name="NarrativeEngine",
                priority=ComponentPriority.HIGH,
                dependencies=["SessionManager"],
                config=narrative_config
            )
            self._manager.register_component(self._narrative_engine)
        
        # Choice Architecture Manager (High priority - core gameplay)
        choice_config = self.gameplay_config.get("choice_architecture", {})
        if choice_config.get("enabled", True):
            self._choice_architecture = ChoiceArchitectureManager(
                name="ChoiceArchitectureManager",
                priority=ComponentPriority.HIGH,
                dependencies=["SessionManager", "NarrativeEngine"],
                config=choice_config
            )
            self._manager.register_component(self._choice_architecture)
        
        # Consequence System (Normal priority - important but not critical)
        consequence_config = self.gameplay_config.get("consequence_system", {})
        if consequence_config.get("enabled", True):
            self._consequence_system = ConsequenceSystem(
                name="ConsequenceSystem",
                priority=ComponentPriority.NORMAL,
                dependencies=["SessionManager", "ChoiceArchitectureManager"],
                config=consequence_config
            )
            self._manager.register_component(self._consequence_system)
        
        logger.info("Core gameplay loop components initialized")
    
    def get_manager(self) -> Optional[GameplayLoopManager]:
        """Get the gameplay loop manager."""
        return self._manager
    
    def get_session_manager(self) -> Optional[SessionManager]:
        """Get the session manager component."""
        return self._session_manager
    
    def get_narrative_engine(self) -> Optional[NarrativeEngine]:
        """Get the narrative engine component."""
        return self._narrative_engine
    
    def get_choice_architecture(self) -> Optional[ChoiceArchitectureManager]:
        """Get the choice architecture manager component."""
        return self._choice_architecture
    
    def get_consequence_system(self) -> Optional[ConsequenceSystem]:
        """Get the consequence system component."""
        return self._consequence_system
    
    async def create_gameplay_session(
        self,
        user_id: str,
        character_id: Optional[str] = None,
        world_id: Optional[str] = None,
        therapeutic_goals: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Create a new gameplay session.
        
        Args:
            user_id: User identifier
            character_id: Optional character identifier
            world_id: Optional world identifier
            therapeutic_goals: Optional list of therapeutic goals
            
        Returns:
            Session ID if successful, None otherwise
        """
        if not self._session_manager:
            logger.error("Session manager not available")
            return None
        
        try:
            return await self._session_manager.create_session(
                user_id=user_id,
                character_id=character_id,
                world_id=world_id,
                therapeutic_goals=therapeutic_goals or []
            )
        except Exception as e:
            logger.error(f"Failed to create gameplay session: {e}")
            return None
    
    async def process_user_action(
        self,
        session_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Process a user action within a gameplay session.
        
        Args:
            session_id: Session identifier
            action_type: Type of action (e.g., "choice", "input", "command")
            action_data: Action-specific data
            
        Returns:
            Response data if successful, None otherwise
        """
        if not self._manager:
            logger.error("Gameplay loop manager not available")
            return None
        
        try:
            # Get session context
            session_context = None
            if self._session_manager:
                session_context = await self._session_manager.get_session_context(session_id)
            
            if not session_context:
                logger.error(f"Session {session_id} not found")
                return None
            
            # Process action based on type
            if action_type == "choice" and self._choice_architecture:
                return await self._choice_architecture.process_choice(
                    session_id, action_data
                )
            elif action_type == "narrative_request" and self._narrative_engine:
                return await self._narrative_engine.generate_narrative(
                    session_id, action_data
                )
            elif action_type == "consequence_query" and self._consequence_system:
                return await self._consequence_system.evaluate_consequences(
                    session_id, action_data
                )
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return {"error": f"Unknown action type: {action_type}"}
        
        except Exception as e:
            logger.error(f"Failed to process user action: {e}")
            return {"error": str(e)}
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a gameplay session."""
        if not self._session_manager:
            return None
        
        try:
            return await self._session_manager.get_session_status(session_id)
        except Exception as e:
            logger.error(f"Failed to get session status: {e}")
            return None
    
    async def end_session(self, session_id: str) -> bool:
        """End a gameplay session."""
        if not self._session_manager:
            return False
        
        try:
            return await self._session_manager.end_session(session_id)
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform component health check."""
        base_health = await super().health_check()
        
        if not self.enabled:
            return {**base_health, "status": "disabled"}
        
        if not self._manager:
            return {**base_health, "status": "error", "message": "Manager not initialized"}
        
        try:
            # Get system health from manager
            system_health = await self._manager.get_system_health()
            
            return {
                **base_health,
                "status": system_health.get("overall_status", "unknown"),
                "gameplay_loop": system_health
            }
        
        except Exception as e:
            return {
                **base_health,
                "status": "error",
                "message": f"Health check failed: {e}"
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get component metrics."""
        base_metrics = super().get_metrics()
        
        if not self._manager:
            return base_metrics
        
        # Collect metrics from all registered components
        component_metrics = {}
        for name, component in self._manager._components.items():
            try:
                component_metrics[name] = component.get_performance_metrics()
            except Exception as e:
                component_metrics[name] = {"error": str(e)}
        
        return {
            **base_metrics,
            "enabled": self.enabled,
            "components": component_metrics
        }
