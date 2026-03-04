"""
Logseq: [[TTA.dev/Components/Gameplay_loop/Narrative/Error_recovery_manager]]

# Logseq: [[TTA/Components/Gameplay_loop/Narrative/Error_recovery_manager]]
Error Recovery Manager for Therapeutic Text Adventure

This module provides session fault tolerance through checkpointing,
error classification, and graceful recovery strategies that preserve
the player's therapeutic progress.
"""

from __future__ import annotations

import logging
import traceback
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from ..models.core import SessionState

logger = logging.getLogger(__name__)


class ErrorSeverity(StrEnum):
    """Severity classification of session errors."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(StrEnum):
    """Strategies for recovering from errors."""

    RETRY = "retry"
    FALLBACK = "fallback"
    CHECKPOINT_RESTORE = "checkpoint_restore"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    SESSION_RESET = "session_reset"


# Default strategy ordering by severity
_DEFAULT_STRATEGIES: dict[ErrorSeverity, list[RecoveryStrategy]] = {
    ErrorSeverity.LOW: [
        RecoveryStrategy.RETRY,
        RecoveryStrategy.FALLBACK,
    ],
    ErrorSeverity.MEDIUM: [
        RecoveryStrategy.RETRY,
        RecoveryStrategy.CHECKPOINT_RESTORE,
        RecoveryStrategy.FALLBACK,
    ],
    ErrorSeverity.HIGH: [
        RecoveryStrategy.CHECKPOINT_RESTORE,
        RecoveryStrategy.GRACEFUL_DEGRADATION,
    ],
    ErrorSeverity.CRITICAL: [
        RecoveryStrategy.CHECKPOINT_RESTORE,
        RecoveryStrategy.SESSION_RESET,
    ],
}


class ErrorRecoveryManager:
    """
    Manages session fault tolerance through checkpointing, error
    classification, and strategy-driven recovery to protect
    therapeutic progress.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        self.checkpoints: dict[str, dict[str, Any]] = {}
        self.error_log: list[dict[str, Any]] = []
        self.recovery_strategies: dict[ErrorSeverity, list[RecoveryStrategy]] = {}

        logger.info("ErrorRecoveryManager initialized")

    async def initialize(self) -> bool:
        """Initialize recovery strategies and checkpoint structures."""
        try:
            self.recovery_strategies = dict(_DEFAULT_STRATEGIES)

            # Allow config overrides
            custom = self.config.get("recovery_strategies")
            if isinstance(custom, dict):
                for sev_str, strats in custom.items():
                    try:
                        sev = ErrorSeverity(sev_str)
                        self.recovery_strategies[sev] = [
                            RecoveryStrategy(s) for s in strats
                        ]
                    except ValueError:
                        pass

            logger.info("ErrorRecoveryManager initialization completed")
            return True

        except Exception as e:
            logger.error(f"ErrorRecoveryManager initialization failed: {e}")
            return False

    async def create_checkpoint(self, session_state: SessionState) -> str:
        """
        Save a session checkpoint.

        Args:
            session_state: Current session state to snapshot

        Returns:
            Checkpoint identifier
        """
        try:
            checkpoint_id = str(uuid4())
            self.checkpoints[checkpoint_id] = {
                "checkpoint_id": checkpoint_id,
                "session_id": session_state.session_id,
                "state_json": session_state.model_dump(),
                "created_at": datetime.now(UTC).isoformat(),
            }

            # Prune old checkpoints for the same session
            max_per_session = int(self.config.get("max_checkpoints_per_session", 10))
            session_cps = sorted(
                (
                    (cid, cp)
                    for cid, cp in self.checkpoints.items()
                    if cp["session_id"] == session_state.session_id
                ),
                key=lambda x: x[1]["created_at"],
            )
            if len(session_cps) > max_per_session:
                for cid, _ in session_cps[: len(session_cps) - max_per_session]:
                    del self.checkpoints[cid]

            logger.info(
                f"Created checkpoint {checkpoint_id} for session "
                f"{session_state.session_id}"
            )
            return checkpoint_id

        except Exception as e:
            logger.error(f"Checkpoint creation failed: {e}")
            return ""

    async def restore_checkpoint(self, checkpoint_id: str) -> SessionState | None:
        """
        Restore a session from a checkpoint.

        Args:
            checkpoint_id: Checkpoint to restore

        Returns:
            Restored SessionState, or None if not found
        """
        try:
            cp = self.checkpoints.get(checkpoint_id)
            if cp is None:
                logger.warning(f"Checkpoint {checkpoint_id} not found")
                return None

            state = SessionState(**cp["state_json"])
            logger.info(
                f"Restored checkpoint {checkpoint_id} for session {state.session_id}"
            )
            return state

        except Exception as e:
            logger.error(f"Checkpoint restoration failed: {e}")
            return None

    async def handle_error(
        self, error: Exception, session_state: SessionState
    ) -> SessionState:
        """
        Handle an error and return a recovered session state.

        Args:
            error: The exception that occurred
            session_state: Session state at the time of error

        Returns:
            Recovered session state (may be original if recovery fails)
        """
        try:
            severity = self._classify_severity(error)
            strategy = await self.get_recovery_strategy(error)

            await self.log_error(session_state.session_id, error, severity)

            logger.info(
                f"Handling {severity} error with strategy {strategy}: "
                f"{type(error).__name__}"
            )

            if strategy == RecoveryStrategy.RETRY:
                # For retry, just return current state for the caller to retry
                return session_state

            if strategy == RecoveryStrategy.CHECKPOINT_RESTORE:
                restored = await self._restore_latest_checkpoint(
                    session_state.session_id
                )
                if restored is not None:
                    return restored

            if strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
                session_state.is_paused = True
                session_state.requires_therapeutic_intervention = False
                return session_state

            if strategy == RecoveryStrategy.SESSION_RESET:
                reset = SessionState(
                    user_id=session_state.user_id,
                    session_id=session_state.session_id,
                )
                logger.warning(
                    f"Session {session_state.session_id} reset due to critical error"
                )
                return reset

            # FALLBACK — return the current state unchanged
            return session_state

        except Exception as recovery_error:
            logger.error(f"Error recovery itself failed: {recovery_error}")
            return session_state

    async def get_recovery_strategy(self, error: Exception) -> RecoveryStrategy:
        """
        Determine the appropriate recovery strategy for an error.

        Args:
            error: The exception to analyze

        Returns:
            Selected recovery strategy
        """
        try:
            severity = self._classify_severity(error)
            strategies = self.recovery_strategies.get(severity, [])
            return strategies[0] if strategies else RecoveryStrategy.FALLBACK

        except Exception as e:
            logger.warning(f"Strategy determination failed: {e}")
            return RecoveryStrategy.FALLBACK

    async def log_error(
        self,
        session_id: str,
        error: Exception,
        severity: ErrorSeverity,
    ) -> None:
        """
        Log an error event.

        Args:
            session_id: Session where the error occurred
            error: The exception
            severity: Classified severity
        """
        try:
            entry: dict[str, Any] = {
                "session_id": session_id,
                "error_type": type(error).__name__,
                "message": str(error),
                "severity": str(severity),
                "traceback": traceback.format_exception(error)[-5:],
                "logged_at": datetime.now(UTC).isoformat(),
            }
            self.error_log.append(entry)

            max_log = int(self.config.get("max_error_log", 500))
            if len(self.error_log) > max_log:
                self.error_log = self.error_log[-max_log:]

            log_fn = (
                logger.error
                if severity in (ErrorSeverity.HIGH, ErrorSeverity.CRITICAL)
                else logger.warning
            )
            log_fn(
                f"Error logged for session {session_id}: "
                f"[{severity}] {type(error).__name__}: {error}"
            )

        except Exception as log_error:
            logger.error(f"Error logging itself failed: {log_error}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_severity(error: Exception) -> ErrorSeverity:
        """Classify the severity of an exception."""
        critical_types = (SystemExit, MemoryError, KeyboardInterrupt)
        high_types = (RuntimeError, OSError, ConnectionError)
        medium_types = (ValueError, TypeError, KeyError, AttributeError)

        if isinstance(error, critical_types):
            return ErrorSeverity.CRITICAL
        if isinstance(error, high_types):
            return ErrorSeverity.HIGH
        if isinstance(error, medium_types):
            return ErrorSeverity.MEDIUM
        return ErrorSeverity.LOW

    async def _restore_latest_checkpoint(self, session_id: str) -> SessionState | None:
        """Find and restore the most recent checkpoint for a session."""
        session_cps = sorted(
            (
                (cid, cp)
                for cid, cp in self.checkpoints.items()
                if cp["session_id"] == session_id
            ),
            key=lambda x: x[1]["created_at"],
            reverse=True,
        )
        if not session_cps:
            logger.warning(f"No checkpoints found for session {session_id}")
            return None

        return await self.restore_checkpoint(session_cps[0][0])
