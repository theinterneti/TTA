"""
Gameplay Loop Integration Module

This module provides integration between the Core Gameplay Loop system and existing
TTA systems including authentication, safety validation, and agent orchestration.
"""

import logging
from datetime import datetime
from typing import Any

from ..agent_orchestration.service import AgentOrchestrationService
from ..agent_orchestration.therapeutic_safety import SafetyService
from ..components.gameplay_loop_component import GameplayLoopComponent
from ..player_experience.api.auth import AuthenticationError, get_current_player

logger = logging.getLogger(__name__)


class GameplayLoopIntegration:
    """
    Integration layer that connects the Core Gameplay Loop with existing TTA systems.

    This class provides a unified interface for gameplay operations that automatically
    handles authentication, safety validation, and agent orchestration integration.
    """

    def __init__(
        self,
        gameplay_component: GameplayLoopComponent,
        agent_orchestration: AgentOrchestrationService | None = None,
        safety_service: SafetyService | None = None,
    ):
        """
        Initialize the integration layer.

        Args:
            gameplay_component: The GameplayLoopComponent instance
            agent_orchestration: Optional agent orchestration service
            safety_service: Optional therapeutic safety service
        """
        self.gameplay_component = gameplay_component
        self.agent_orchestration = agent_orchestration
        self.safety_service = safety_service

        logger.info("GameplayLoopIntegration initialized")

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
        try:
            # Authenticate user
            try:
                user_info = await get_current_player(auth_token)
                user_id = user_info.get("user_id") or user_info.get("username")

                if not user_id:
                    return {
                        "success": False,
                        "error": "Invalid user information",
                        "code": "AUTH_ERROR",
                    }

            except AuthenticationError as e:
                return {
                    "success": False,
                    "error": f"Authentication failed: {str(e)}",
                    "code": "AUTH_ERROR",
                }

            # Validate therapeutic context if safety service is available
            if self.safety_service and therapeutic_context:
                context_text = str(therapeutic_context)
                validation_result = await self.safety_service.validate_text(
                    context_text
                )

                if validation_result.level.value >= 8:  # High risk level
                    return {
                        "success": False,
                        "error": "Therapeutic context contains unsafe content",
                        "code": "SAFETY_ERROR",
                        "safety_level": validation_result.level.value,
                    }

            # Create gameplay session
            session_id = await self.gameplay_component.create_gameplay_session(
                user_id=user_id, therapeutic_context=therapeutic_context
            )

            if not session_id:
                return {
                    "success": False,
                    "error": "Failed to create gameplay session",
                    "code": "SESSION_ERROR",
                }

            # Get initial session state
            session_status = await self.gameplay_component.get_session_status(
                session_id
            )

            return {
                "success": True,
                "session_id": session_id,
                "user_id": user_id,
                "session_status": session_status,
                "created_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to create authenticated session: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "code": "INTERNAL_ERROR",
            }

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
        try:
            # Authenticate user
            try:
                user_info = await get_current_player(auth_token)
                user_id = user_info.get("user_id") or user_info.get("username")

                if not user_id:
                    return {
                        "success": False,
                        "error": "Invalid user information",
                        "code": "AUTH_ERROR",
                    }

            except AuthenticationError as e:
                return {
                    "success": False,
                    "error": f"Authentication failed: {str(e)}",
                    "code": "AUTH_ERROR",
                }

            # Verify session ownership
            session_status = await self.gameplay_component.get_session_status(
                session_id
            )
            if not session_status:
                return {
                    "success": False,
                    "error": "Session not found",
                    "code": "SESSION_NOT_FOUND",
                }

            if session_status.get("user_id") != user_id:
                return {
                    "success": False,
                    "error": "Session access denied",
                    "code": "ACCESS_DENIED",
                }

            # Process the choice
            choice_result = await self.gameplay_component.process_user_choice(
                session_id, choice_id
            )

            if not choice_result or "error" in choice_result:
                return {
                    "success": False,
                    "error": choice_result.get("error", "Choice processing failed"),
                    "code": "CHOICE_ERROR",
                }

            # Validate generated content if safety service is available
            if self.safety_service and choice_result.get("next_scene"):
                scene_description = choice_result["next_scene"].get("description", "")
                if scene_description:
                    validation_result = await self.safety_service.validate_text(
                        scene_description
                    )

                    if validation_result.level.value >= 8:  # High risk level
                        # Generate alternative content
                        alternative = self.safety_service.suggest_alternative(
                            validation_result.level, scene_description
                        )
                        choice_result["next_scene"]["description"] = alternative
                        choice_result["safety_warning"] = (
                            "Content was modified for therapeutic safety"
                        )

            # Integrate with agent orchestration if available
            if self.agent_orchestration:
                try:
                    # This could trigger additional narrative generation or therapeutic analysis
                    # For now, we'll just log the integration point
                    logger.info(
                        f"Agent orchestration integration point for session {session_id}"
                    )
                except Exception as e:
                    logger.warning(f"Agent orchestration integration failed: {e}")

            return {
                "success": True,
                "session_id": session_id,
                "choice_result": choice_result,
                "processed_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to process validated choice: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "code": "INTERNAL_ERROR",
            }

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
        try:
            # Authenticate user
            try:
                user_info = await get_current_player(auth_token)
                user_id = user_info.get("user_id") or user_info.get("username")

                if not user_id:
                    return {
                        "success": False,
                        "error": "Invalid user information",
                        "code": "AUTH_ERROR",
                    }

            except AuthenticationError as e:
                return {
                    "success": False,
                    "error": f"Authentication failed: {str(e)}",
                    "code": "AUTH_ERROR",
                }

            # Get session status
            session_status = await self.gameplay_component.get_session_status(
                session_id
            )
            if not session_status:
                return {
                    "success": False,
                    "error": "Session not found",
                    "code": "SESSION_NOT_FOUND",
                }

            # Verify session ownership
            if session_status.get("user_id") != user_id:
                return {
                    "success": False,
                    "error": "Session access denied",
                    "code": "ACCESS_DENIED",
                }

            return {
                "success": True,
                "session_status": session_status,
                "retrieved_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get session with auth: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "code": "INTERNAL_ERROR",
            }

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
        try:
            # Authenticate user
            try:
                user_info = await get_current_player(auth_token)
                user_id = user_info.get("user_id") or user_info.get("username")

                if not user_id:
                    return {
                        "success": False,
                        "error": "Invalid user information",
                        "code": "AUTH_ERROR",
                    }

            except AuthenticationError as e:
                return {
                    "success": False,
                    "error": f"Authentication failed: {str(e)}",
                    "code": "AUTH_ERROR",
                }

            # Verify session ownership
            session_status = await self.gameplay_component.get_session_status(
                session_id
            )
            if not session_status:
                return {
                    "success": False,
                    "error": "Session not found",
                    "code": "SESSION_NOT_FOUND",
                }

            if session_status.get("user_id") != user_id:
                return {
                    "success": False,
                    "error": "Session access denied",
                    "code": "ACCESS_DENIED",
                }

            # End the session
            success = await self.gameplay_component.end_session(session_id)

            if not success:
                return {
                    "success": False,
                    "error": "Failed to end session",
                    "code": "SESSION_ERROR",
                }

            return {
                "success": True,
                "session_id": session_id,
                "ended_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to end session with auth: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "code": "INTERNAL_ERROR",
            }

    async def get_user_sessions(self, auth_token: str) -> dict[str, Any]:
        """
        Get all sessions for an authenticated user.

        Args:
            auth_token: JWT authentication token

        Returns:
            Dict containing user sessions or error
        """
        try:
            # Authenticate user
            try:
                user_info = await get_current_player(auth_token)
                user_id = user_info.get("user_id") or user_info.get("username")

                if not user_id:
                    return {"error": "Invalid user information", "code": "AUTH_ERROR"}

            except AuthenticationError as e:
                return {
                    "error": f"Authentication failed: {str(e)}",
                    "code": "AUTH_ERROR",
                }

            # Get session metrics (this would need to be enhanced to filter by user)
            session_metrics = await self.gameplay_component.get_session_metrics()

            return {
                "success": True,
                "user_id": user_id,
                "session_metrics": session_metrics,
                "retrieved_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "code": "INTERNAL_ERROR",
            }

    def get_integration_status(self) -> dict[str, Any]:
        """
        Get the status of all integrated systems.

        Returns:
            Dict containing integration status
        """
        return {
            "gameplay_component": {
                "available": self.gameplay_component is not None,
                "status": (
                    self.gameplay_component.get_status_info()
                    if self.gameplay_component
                    else None
                ),
            },
            "agent_orchestration": {
                "available": self.agent_orchestration is not None,
                "initialized": (
                    getattr(self.agent_orchestration, "_initialized", False)
                    if self.agent_orchestration
                    else False
                ),
            },
            "safety_service": {
                "available": self.safety_service is not None,
                "enabled": (
                    self.safety_service.is_enabled() if self.safety_service else False
                ),
            },
        }
