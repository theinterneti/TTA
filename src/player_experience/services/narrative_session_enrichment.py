"""Shared helpers for enriching session payloads with narrative orchestration."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _get_narrative_orchestrator():
    """Lazily resolve the shared narrative orchestrator from the conversation router."""
    from ..api.routers.conversation import _get_narrative_orchestrator as factory

    return factory()


async def enrich_session_payloads(
    sessions: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Attach narrative orchestration snapshots to session payloads when available."""
    orchestrator = _get_narrative_orchestrator()
    enriched_sessions: list[dict[str, Any]] = []
    stable_sessions = 0
    strained_sessions = 0

    for session in sessions:
        enriched_session = dict(session)
        session_id = session.get("session_id")
        if not session_id:
            enriched_sessions.append(enriched_session)
            continue

        try:
            narrative_state = await orchestrator.get_session_state(str(session_id))
        except Exception as exc:
            logger.warning(
                "Failed to load narrative orchestration for session %s: %s",
                session_id,
                exc,
            )
            enriched_sessions.append(enriched_session)
            continue

        if isinstance(narrative_state, dict) and narrative_state:
            enriched_session["narrative_orchestration"] = narrative_state
            player_signals = narrative_state.get("player_signals", {})
            coherence_status = (
                player_signals.get("coherence_status")
                if isinstance(player_signals, dict)
                else None
            )
            if coherence_status == "stable":
                stable_sessions += 1
            elif coherence_status == "strained":
                strained_sessions += 1

        enriched_sessions.append(enriched_session)

    return enriched_sessions, {
        "stable_sessions": stable_sessions,
        "strained_sessions": strained_sessions,
    }
