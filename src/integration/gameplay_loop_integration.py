"""

# Logseq: [[TTA.dev/Integration/Gameplay_loop_integration]]
Gameplay Loop Integration Module

This module provides integration between the Core Gameplay Loop system and existing
TTA systems including authentication, safety validation, and agent orchestration.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from ..agent_orchestration.service import AgentOrchestrationService
from ..agent_orchestration.therapeutic_safety import SafetyLevel, SafetyService
from ..components.gameplay_loop_component import GameplayLoopComponent
from ..components.narrative_arc_orchestrator_component import (
    NarrativeArcOrchestratorComponent,
)
from ..player_experience.api.auth import AuthenticationError, verify_token

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
        narrative_orchestrator: NarrativeArcOrchestratorComponent | None = None,
    ):
        """
        Initialize the integration layer.

        Args:
            gameplay_component: The GameplayLoopComponent instance
            agent_orchestration: Optional agent orchestration service
            safety_service: Optional therapeutic safety service
            narrative_orchestrator: Optional narrative status enricher
        """
        self.gameplay_component = gameplay_component
        self.agent_orchestration = agent_orchestration
        self.safety_service = safety_service
        self.narrative_orchestrator = narrative_orchestrator

        logger.info("GameplayLoopIntegration initialized")

    async def _enrich_session_status(
        self,
        session_status: dict[str, Any] | None,
        therapeutic_context: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Add a narrative-orchestration snapshot when the adapter is available."""
        if not session_status or not self.narrative_orchestrator:
            return session_status

        try:
            session_id = session_status.get("session_id")
            if not isinstance(session_id, str) or not session_id:
                return session_status

            await self.narrative_orchestrator.initialize_session(
                session_id=session_id,
                character_id=str(
                    session_status.get("character_id", "gameplay-protagonist")
                ),
                world_id=str(session_status.get("world_id", "gameplay-world")),
                therapeutic_settings=self._build_therapeutic_settings(
                    session_status, therapeutic_context
                ),
            )
            await self.narrative_orchestrator.restore_session_state(
                session_id,
                self._build_narrative_session_payload(
                    session_status, therapeutic_context
                ),
            )
            snapshot = await self.narrative_orchestrator.get_session_state(session_id)
            if not snapshot:
                return session_status

            enriched_status = dict(session_status)
            enriched_status["narrative_orchestration"] = snapshot
            return enriched_status
        except Exception as exc:
            logger.warning(
                "Failed to enrich gameplay session %s with narrative status: %s",
                session_status.get("session_id"),
                exc,
            )
            return session_status

    async def _finalize_narrative_session(self, session_id: str) -> None:
        """Finalize orchestrator state when a gameplay session ends."""
        if not self.narrative_orchestrator:
            return

        try:
            await self.narrative_orchestrator.finalize_session(session_id)
        except Exception as exc:
            logger.warning(
                "Failed to finalize narrative session %s: %s",
                session_id,
                exc,
            )

    def _build_therapeutic_settings(
        self,
        session_status: dict[str, Any],
        therapeutic_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Project gameplay session context into the shared therapeutic settings shape."""
        merged_settings: dict[str, Any] = {}
        context = therapeutic_context or {}
        if isinstance(context, dict):
            merged_settings.update(context)

        emotional_state = session_status.get("emotional_state")
        focus = (
            str(emotional_state).lower()
            if isinstance(emotional_state, str) and emotional_state
            else "gameplay_support"
        )
        merged_settings.setdefault("therapeutic_focus", focus)
        return merged_settings

    def _build_narrative_session_payload(
        self,
        session_status: dict[str, Any],
        therapeutic_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Translate gameplay session status into an orchestrator session snapshot."""
        now = datetime.now(UTC).isoformat()
        total_choices = int(session_status.get("total_choices", 0))
        therapeutic_engagement = float(
            session_status.get("therapeutic_engagement", 0.5)
        )
        available_choices = session_status.get("available_choices", [])
        available_choices_count = int(
            session_status.get("available_choices_count", len(available_choices))
        )

        active_threads: list[str] = []
        current_scene_id = session_status.get("current_scene_id")
        if isinstance(current_scene_id, str) and current_scene_id:
            active_threads.append(f"scene:{current_scene_id}")
        emotional_state = session_status.get("emotional_state")
        if isinstance(emotional_state, str) and emotional_state:
            active_threads.append(f"emotion:{emotional_state.lower()}")
        if therapeutic_context:
            for goal in therapeutic_context.get("goals", []):
                if goal:
                    active_threads.append(f"goal:{goal}")

        return {
            "session_id": session_status["session_id"],
            "player_id": session_status.get("user_id"),
            "created_at": session_status.get("created_at", now),
            "last_updated": session_status.get("last_activity", now),
            "interaction_count": total_choices,
            "engagement_score": therapeutic_engagement,
            "coherence_score": min(
                1.0,
                max(0.35, 0.55 + (0.05 * min(available_choices_count, 5))),
            ),
            "therapeutic_alignment": min(1.0, max(0.0, therapeutic_engagement or 0.5)),
            "active_threads": active_threads,
            "therapeutic_settings": self._build_therapeutic_settings(
                session_status, therapeutic_context
            ),
        }

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
                token_data = verify_token(auth_token)
                user_id = token_data.player_id or token_data.username

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

                if validation_result.level == SafetyLevel.BLOCKED:  # Blocked content
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
            session_status = await self._enrich_session_status(
                session_status,
                therapeutic_context,
            )

            return {
                "success": True,
                "session_id": session_id,
                "user_id": user_id,
                "session_status": session_status,
                "created_at": datetime.now(UTC).isoformat(),
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
                token_data = verify_token(auth_token)
                user_id = token_data.player_id or token_data.username

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
                    "error": choice_result.get("error", "Choice processing failed")
                    if choice_result
                    else "Choice processing failed",  # type: ignore[union-attr]
                    "code": "CHOICE_ERROR",
                }

            # Validate generated content if safety service is available
            if self.safety_service and choice_result.get("next_scene"):
                scene_description = choice_result["next_scene"].get("description", "")
                if scene_description:
                    validation_result = await self.safety_service.validate_text(
                        scene_description
                    )

                    if (
                        validation_result.level == SafetyLevel.BLOCKED
                    ):  # Blocked content
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

            # Fetch updated session status so callers can see incremented total_choices
            updated_session_status = await self.gameplay_component.get_session_status(
                session_id
            )
            updated_session_status = await self._enrich_session_status(
                updated_session_status
            )

            return {
                "success": True,
                "session_id": session_id,
                "choice_result": choice_result,
                "session_status": updated_session_status,
                "processed_at": datetime.now(UTC).isoformat(),
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
                token_data = verify_token(auth_token)
                user_id = token_data.player_id or token_data.username

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

            session_status = await self._enrich_session_status(session_status)

            return {
                "success": True,
                "session_status": session_status,
                "retrieved_at": datetime.now(UTC).isoformat(),
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
                token_data = verify_token(auth_token)
                user_id = token_data.player_id or token_data.username

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

            await self._finalize_narrative_session(session_id)

            return {
                "success": True,
                "session_id": session_id,
                "ended_at": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to end session with auth: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "code": "INTERNAL_ERROR",
            }

    async def pause_session_with_auth(
        self, session_id: str, auth_token: str
    ) -> dict[str, Any]:
        """Pause a gameplay session and preserve synchronized narrative state."""
        try:
            try:
                token_data = verify_token(auth_token)
                user_id = token_data.player_id or token_data.username

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

            session_status = await self._enrich_session_status(session_status)

            success = await self.gameplay_component.pause_session(session_id)
            if not success:
                return {
                    "success": False,
                    "error": "Failed to pause session",
                    "code": "SESSION_ERROR",
                }

            return {
                "success": True,
                "session_id": session_id,
                "paused_at": datetime.now(UTC).isoformat(),
                "session_status": session_status,
            }
        except Exception as e:
            logger.error(f"Failed to pause session with auth: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "code": "INTERNAL_ERROR",
            }

    async def resume_session_with_auth(
        self, session_id: str, auth_token: str
    ) -> dict[str, Any]:
        """Resume a paused gameplay session and restore synchronized narrative state."""
        try:
            try:
                token_data = verify_token(auth_token)
                user_id = token_data.player_id or token_data.username

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

            session_data = await self.gameplay_component.resume_session(session_id)
            if not session_data:
                return {
                    "success": False,
                    "error": "Failed to resume session",
                    "code": "SESSION_ERROR",
                }

            resumed_status = await self.gameplay_component.get_session_status(
                session_id
            )
            resumed_status = await self._enrich_session_status(resumed_status)

            if resumed_status and "narrative_orchestration" in resumed_status:
                session_data = dict(session_data)
                session_data["narrative_orchestration"] = resumed_status[
                    "narrative_orchestration"
                ]

            return {
                "success": True,
                "session_id": session_id,
                "session_data": session_data,
                "resumed_at": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to resume session with auth: {e}")
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
                token_data = verify_token(auth_token)
                user_id = token_data.player_id or token_data.username

                if not user_id:
                    return {"error": "Invalid user information", "code": "AUTH_ERROR"}

            except AuthenticationError as e:
                return {
                    "error": f"Authentication failed: {str(e)}",
                    "code": "AUTH_ERROR",
                }

            sessions = await self.gameplay_component.get_user_sessions_for_player(
                user_id
            )
            enriched_sessions: list[dict[str, Any]] = []
            stable_sessions = 0
            strained_sessions = 0

            for session in sessions:
                enriched_session = await self._enrich_session_status(session)
                if not enriched_session:
                    continue

                narrative_state = enriched_session.get("narrative_orchestration", {})
                player_signals = (
                    narrative_state.get("player_signals", {})
                    if isinstance(narrative_state, dict)
                    else {}
                )
                coherence_status = player_signals.get("coherence_status")
                if coherence_status == "stable":
                    stable_sessions += 1
                elif coherence_status == "strained":
                    strained_sessions += 1

                enriched_sessions.append(enriched_session)

            return {
                "success": True,
                "user_id": user_id,
                "session_metrics": {
                    "sessions": enriched_sessions,
                    "total_count": len(enriched_sessions),
                    "narrative_summary": {
                        "stable_sessions": stable_sessions,
                        "strained_sessions": strained_sessions,
                    },
                },
                "retrieved_at": datetime.now(UTC).isoformat(),
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
