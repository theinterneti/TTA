"""
Gameplay Service

This module provides the service layer for gameplay loop operations,
integrating with the GameplayLoopIntegration layer and providing
a clean interface for API endpoints.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class GameplayService:
    """
    Service layer for gameplay loop operations.

    This service provides a clean interface for gameplay operations
    and handles integration with the underlying gameplay loop system.
    """

    def __init__(self):
        """Initialize the gameplay service."""
        self._integration = None
        self._initialized = False
        logger.info("GameplayService initialized")

    async def _ensure_integration(self):
        """Ensure the integration layer is initialized."""
        if self._initialized:
            return

        try:
            # Import here to avoid circular dependencies
            from ...integration.gameplay_loop_integration import GameplayLoopIntegration
            from ...orchestration.orchestrator import TTAOrchestrator

            # Get the orchestrator instance (this would be dependency injected in production)
            orchestrator = TTAOrchestrator()

            # Get the gameplay loop component
            gameplay_component = orchestrator.components.get("core_gameplay_loop")
            if not gameplay_component:
                logger.error("GameplayLoopComponent not found in orchestrator")
                return

            # Get agent orchestration service if available
            agent_orchestration_component = orchestrator.components.get(
                "agent_orchestration"
            )
            agent_orchestration = None
            if agent_orchestration_component:
                agent_orchestration = getattr(
                    agent_orchestration_component, "service", None
                )

            # Get safety service if available
            safety_service = None
            try:
                from ...agent_orchestration.therapeutic_safety import SafetyService

                safety_service = SafetyService(enabled=True)
            except Exception as e:
                logger.warning(f"Safety service not available: {e}")

            # Create integration layer
            self._integration = GameplayLoopIntegration(
                gameplay_component=gameplay_component,
                agent_orchestration=agent_orchestration,
                safety_service=safety_service,
            )

            self._initialized = True
            logger.info("GameplayService integration initialized")

        except Exception as e:
            logger.error(f"Failed to initialize gameplay service integration: {e}")

    async def create_authenticated_session(
        self, auth_token: str, therapeutic_context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Create a new gameplay session with authentication.

        Args:
            auth_token: JWT authentication token
            therapeutic_context: Optional therapeutic context and goals

        Returns:
            Dict containing session information or error
        """
        await self._ensure_integration()

        if not self._integration:
            return {"error": "Gameplay service not available", "code": "SERVICE_ERROR"}

        return await self._integration.create_authenticated_session(
            auth_token=auth_token, therapeutic_context=therapeutic_context
        )

    async def process_validated_choice(
        self, session_id: str, choice_id: str, auth_token: str
    ) -> dict[str, Any]:
        """
        Process a user choice with authentication and safety validation.

        Args:
            session_id: Session identifier
            choice_id: ID of the choice made by the user
            auth_token: JWT authentication token

        Returns:
            Dict containing choice processing results or error
        """
        await self._ensure_integration()

        if not self._integration:
            return {"error": "Gameplay service not available", "code": "SERVICE_ERROR"}

        return await self._integration.process_validated_choice(
            session_id=session_id, choice_id=choice_id, auth_token=auth_token
        )

    async def get_session_with_auth(
        self, session_id: str, auth_token: str
    ) -> dict[str, Any]:
        """
        Get session status with authentication verification.

        Args:
            session_id: Session identifier
            auth_token: JWT authentication token

        Returns:
            Dict containing session status or error
        """
        await self._ensure_integration()

        if not self._integration:
            return {"error": "Gameplay service not available", "code": "SERVICE_ERROR"}

        return await self._integration.get_session_with_auth(
            session_id=session_id, auth_token=auth_token
        )

    async def end_session_with_auth(
        self, session_id: str, auth_token: str
    ) -> dict[str, Any]:
        """
        End a session with authentication verification.

        Args:
            session_id: Session identifier
            auth_token: JWT authentication token

        Returns:
            Dict containing operation result
        """
        await self._ensure_integration()

        if not self._integration:
            return {"error": "Gameplay service not available", "code": "SERVICE_ERROR"}

        return await self._integration.end_session_with_auth(
            session_id=session_id, auth_token=auth_token
        )

    async def get_user_sessions(self, auth_token: str) -> dict[str, Any]:
        """
        Get all sessions for an authenticated user.

        Args:
            auth_token: JWT authentication token

        Returns:
            Dict containing user sessions or error
        """
        await self._ensure_integration()

        if not self._integration:
            return {"error": "Gameplay service not available", "code": "SERVICE_ERROR"}

        return await self._integration.get_user_sessions(auth_token=auth_token)

    def get_integration_status(self) -> dict[str, Any]:
        """
        Get the status of all integrated systems.

        Returns:
            Dict containing integration status
        """
        if not self._integration:
            return {
                "gameplay_service": {
                    "initialized": False,
                    "error": "Integration not initialized",
                }
            }

        status = self._integration.get_integration_status()
        status["gameplay_service"] = {
            "initialized": self._initialized,
            "integration_available": True,
        }

        return status

    async def pause_session(self, session_id: str, auth_token: str) -> dict[str, Any]:
        """
        Pause a gameplay session.

        Args:
            session_id: Session identifier
            auth_token: JWT authentication token

        Returns:
            Dict containing operation result
        """
        await self._ensure_integration()

        if not self._integration:
            return {"error": "Gameplay service not available", "code": "SERVICE_ERROR"}

        try:
            # Authenticate user first
            from ..api.auth import AuthenticationError, get_current_player

            try:
                user_info = get_current_player(auth_token)
                user_id = user_info.get("user_id") or user_info.get("username")

                if not user_id:
                    return {"error": "Invalid user information", "code": "AUTH_ERROR"}

            except AuthenticationError as e:
                return {
                    "error": f"Authentication failed: {str(e)}",
                    "code": "AUTH_ERROR",
                }

            # Verify session ownership
            session_status = (
                await self._integration.gameplay_component.get_session_status(
                    session_id
                )
            )
            if not session_status:
                return {"error": "Session not found", "code": "SESSION_NOT_FOUND"}

            if session_status.get("user_id") != user_id:
                return {"error": "Session access denied", "code": "ACCESS_DENIED"}

            # Pause the session
            success = await self._integration.gameplay_component.pause_session(
                session_id
            )

            if not success:
                return {"error": "Failed to pause session", "code": "SESSION_ERROR"}

            return {
                "success": True,
                "session_id": session_id,
                "paused_at": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            }

        except Exception as e:
            logger.error(f"Failed to pause session: {e}")
            return {"error": f"Internal error: {str(e)}", "code": "INTERNAL_ERROR"}

    async def resume_session(self, session_id: str, auth_token: str) -> dict[str, Any]:
        """
        Resume a paused gameplay session.

        Args:
            session_id: Session identifier
            auth_token: JWT authentication token

        Returns:
            Dict containing session resume information
        """
        await self._ensure_integration()

        if not self._integration:
            return {"error": "Gameplay service not available", "code": "SERVICE_ERROR"}

        try:
            # Authenticate user first
            from ..api.auth import AuthenticationError, get_current_player

            try:
                user_info = get_current_player(auth_token)
                user_id = user_info.get("user_id") or user_info.get("username")

                if not user_id:
                    return {"error": "Invalid user information", "code": "AUTH_ERROR"}

            except AuthenticationError as e:
                return {
                    "error": f"Authentication failed: {str(e)}",
                    "code": "AUTH_ERROR",
                }

            # Resume the session
            session_data = await self._integration.gameplay_component.resume_session(
                session_id
            )

            if not session_data:
                return {"error": "Failed to resume session", "code": "SESSION_ERROR"}

            return {
                "success": True,
                "session_data": session_data,
                "resumed_at": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            }

        except Exception as e:
            logger.error(f"Failed to resume session: {e}")
            return {"error": f"Internal error: {str(e)}", "code": "INTERNAL_ERROR"}
