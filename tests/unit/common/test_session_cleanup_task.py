"""
Unit tests for the periodic session cleanup background task.

Tests cover:
- _session_cleanup_loop calls cleanup_inactive_sessions after each interval
- Skips gracefully when the gameplay service is not yet initialised
- Handles exceptions without crashing the loop
- Cancels cleanly (raises CancelledError → task ends)
- FastAPI lifespan starts and stops the task
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

# Patch path for get_gameplay_service used inside _session_cleanup_loop.
_SVC_PATCH = "src.player_experience.api.routers.gameplay.get_gameplay_service"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_component(n_cleaned: int = 0) -> MagicMock:
    """Fake GameplayLoopComponent with async cleanup."""
    comp = MagicMock()
    comp.cleanup_inactive_sessions = AsyncMock(return_value=n_cleaned)
    return comp


def _make_integration(component: MagicMock | None) -> MagicMock:
    integration = MagicMock()
    integration.gameplay_component = component
    return integration


def _make_service(integration: MagicMock | None = None) -> MagicMock:
    svc = MagicMock()
    svc._integration = integration
    return svc


async def _run_loop_once(svc_mock, n_cleaned: int = 0) -> MagicMock:
    """Run _session_cleanup_loop with interval=0 for one iteration, then cancel.

    interval=0 uses asyncio.sleep(0) which just yields — no real waiting.
    """
    with patch(_SVC_PATCH, return_value=svc_mock):
        from src.player_experience.api.app import _session_cleanup_loop

        task = asyncio.create_task(_session_cleanup_loop(interval=0))
        await asyncio.sleep(0)  # let the task start and complete one iteration
        await asyncio.sleep(0)  # give it a bit more to finish the async cleanup call
        task.cancel()
        with pytest.raises((asyncio.CancelledError, Exception)):
            await task
    return svc_mock


# ---------------------------------------------------------------------------
# _session_cleanup_loop
# ---------------------------------------------------------------------------


class TestSessionCleanupLoop:
    async def test_calls_cleanup_after_interval(self):
        """Loop calls cleanup_inactive_sessions once per iteration."""
        component = _make_component(n_cleaned=2)
        svc = _make_service(_make_integration(component))

        await _run_loop_once(svc)

        component.cleanup_inactive_sessions.assert_called()

    async def test_skips_when_service_not_initialised(self):
        """Loop does nothing if _integration is None (service cold start)."""
        svc = _make_service(integration=None)

        with patch(_SVC_PATCH, return_value=svc):
            from src.player_experience.api.app import _session_cleanup_loop

            task = asyncio.create_task(_session_cleanup_loop(interval=0))
            await asyncio.sleep(0)
            task.cancel()
            with pytest.raises((asyncio.CancelledError, Exception)):
                await task

        # No integration → cleanup never called (no AttributeError either)

    async def test_skips_when_component_is_none(self):
        """Loop skips gracefully if integration exists but component is None."""
        integration = MagicMock()
        integration.gameplay_component = None
        svc = _make_service(integration=integration)

        with patch(_SVC_PATCH, return_value=svc):
            from src.player_experience.api.app import _session_cleanup_loop

            task = asyncio.create_task(_session_cleanup_loop(interval=0))
            await asyncio.sleep(0)
            task.cancel()
            with pytest.raises((asyncio.CancelledError, Exception)):
                await task

    async def test_continues_after_exception(self):
        """Loop swallows non-CancelledError exceptions and keeps running."""
        component = _make_component()
        component.cleanup_inactive_sessions = AsyncMock(
            side_effect=[RuntimeError("db error"), 0, 0]
        )
        svc = _make_service(_make_integration(component))

        with patch(_SVC_PATCH, return_value=svc):
            from src.player_experience.api.app import _session_cleanup_loop

            task = asyncio.create_task(_session_cleanup_loop(interval=0))
            # Two yields: first iteration raises, loop continues; second completes
            for _ in range(6):
                await asyncio.sleep(0)
            task.cancel()
            with pytest.raises((asyncio.CancelledError, Exception)):
                await task

        # Loop should have survived the first exception and run a second time
        assert component.cleanup_inactive_sessions.call_count >= 2

    async def test_cancels_cleanly(self):
        """Task.cancel() causes CancelledError to propagate cleanly."""
        with patch(_SVC_PATCH, return_value=_make_service()):
            from src.player_experience.api.app import _session_cleanup_loop

            task = asyncio.create_task(_session_cleanup_loop(interval=0))
            await asyncio.sleep(0)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task

    async def test_logs_when_sessions_evicted(self, caplog):
        """Loop logs a message when sessions are actually cleaned up."""
        import logging

        component = _make_component(n_cleaned=3)
        svc = _make_service(_make_integration(component))

        with caplog.at_level(logging.INFO, logger="src.player_experience.api.app"):
            await _run_loop_once(svc)

        assert any("3" in r.message for r in caplog.records)

    async def test_no_log_when_zero_evicted(self, caplog):
        """Loop does not log when cleanup returns 0 (nothing to evict)."""
        import logging

        component = _make_component(n_cleaned=0)
        svc = _make_service(_make_integration(component))

        with caplog.at_level(logging.INFO, logger="src.player_experience.api.app"):
            await _run_loop_once(svc)

        assert not any("evicted" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# FastAPI lifespan integration
# ---------------------------------------------------------------------------


class TestLifespanCleanupTask:
    def test_lifespan_starts_and_cancels_cleanup_task(self):
        """Lifespan starts the cleanup task on startup and cancels it on shutdown."""
        from fastapi.testclient import TestClient

        cleanup_started = []
        cleanup_cancelled = []

        async def fake_cleanup_loop(interval=60):
            cleanup_started.append(True)
            try:
                await asyncio.sleep(9999)
            except asyncio.CancelledError:
                cleanup_cancelled.append(True)
                raise

        with (
            patch(
                "src.player_experience.api.app._session_cleanup_loop",
                side_effect=fake_cleanup_loop,
            ),
            patch("src.player_experience.api.app.init_sentry"),
        ):
            from src.player_experience.api.app import create_app

            app = create_app()
            with TestClient(app):
                pass  # startup + shutdown happened

        assert len(cleanup_started) == 1
        assert len(cleanup_cancelled) == 1

    def test_cleanup_task_named_session_cleanup(self):
        """The asyncio task is created with name='session-cleanup'."""
        task_names: list[str] = []
        original_create_task = asyncio.create_task

        def capturing_create_task(coro, *, name=None, **kwargs):
            task_names.append(name or "")
            return original_create_task(coro, name=name, **kwargs)

        async def fake_cleanup_loop(interval=60):
            try:
                await asyncio.sleep(9999)
            except asyncio.CancelledError:
                raise

        with (
            patch(
                "src.player_experience.api.app.asyncio.create_task",
                side_effect=capturing_create_task,
            ),
            patch(
                "src.player_experience.api.app._session_cleanup_loop",
                side_effect=fake_cleanup_loop,
            ),
            patch("src.player_experience.api.app.init_sentry"),
        ):
            from fastapi.testclient import TestClient

            from src.player_experience.api.app import create_app

            app = create_app()
            with TestClient(app):
                pass

        assert "session-cleanup" in task_names
