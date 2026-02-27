"""
Logseq: [[TTA.dev/Player_experience/Services/Message_service]]
AI-powered message service for active gameplay sessions.

Handles real-time narrative generation using the LLM factory,
maintaining per-session conversation history for contextual responses.
Auto-saves every message to SessionStore (SQLite-backed) so conversations
persist across server restarts and survive logout/login.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.ai_components.llm_factory import get_llm

from .session_store import SessionStore

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)

# Per-session in-memory cache: {session_id: [{role, content}]}
# Populated on first access from SessionStore; acts as a write-through cache.
_SESSION_HISTORY: dict[str, list[dict[str, str]]] = {}

_MAX_HISTORY_MESSAGES = 20  # Trim to last N turns to keep context window bounded

_SYSTEM_PROMPT_TEMPLATE = """\
You are a compassionate therapeutic narrative guide in the Therapeutic Text Adventure (TTA).
Respond to the player in a warm, immersive narrative voice that draws them deeper into the story.

Character: {character_name}
World: {world_name}

Guidelines:
- Write 2–4 sentences of immersive narrative that responds to and advances the player's input.
- Weave in therapeutic themes naturally: mindfulness, resilience, self-compassion, grounding.
- If the player expresses distress or fear, respond with gentle grounding language and support.
- End each response with a subtle narrative invitation to continue exploring or reflecting.
- Never break character to discuss game mechanics or therapy explicitly.
"""

_FALLBACK_RESPONSE = (
    "The world around you shimmers gently, as if pausing to let you breathe. "
    "The path ahead is yours to choose — take all the time you need."
)


class MessageService:
    """AI-powered message handler for active gameplay sessions."""

    def __init__(self, session_store: SessionStore | None = None) -> None:
        self._llm: BaseChatModel | None = None
        self._store = session_store or SessionStore()
        logger.info("MessageService initialized")

    def _get_llm(self) -> BaseChatModel | None:
        """Lazy-load the LLM. Returns None if no provider is configured."""
        if self._llm is None:
            try:
                self._llm = get_llm()
            except Exception as exc:
                logger.warning("LLM unavailable for MessageService: %s", exc)
        return self._llm

    def _load_history_from_store(self, session_id: str) -> list[dict[str, str]]:
        """Populate the in-memory cache from the store if not already loaded."""
        if session_id not in _SESSION_HISTORY:
            stored = self._store.load_messages(session_id)
            _SESSION_HISTORY[session_id] = stored
        return _SESSION_HISTORY[session_id]

    async def send_message(
        self,
        session_id: str,
        player_id: str,
        message: str,
        character_name: str | None = None,
        world_name: str | None = None,
    ) -> dict[str, Any]:
        """Process a player message and return an AI narrative response.

        Auto-saves both the user message and AI response to the SessionStore
        so the full conversation persists across server restarts.

        Args:
            session_id: Active session identifier.
            player_id: Authenticated player's ID.
            message: The player's input text.
            character_name: Character name for narrative framing.
            world_name: World name for narrative framing.

        Returns:
            dict with keys: success, message_id, session_id, response, timestamp.
        """
        # Restore from store if this is the first access after a restart
        history = self._load_history_from_store(session_id)

        now = datetime.now(UTC).isoformat()
        user_mid = str(uuid.uuid4())
        history.append({"role": "user", "content": message})
        self._store.save_message(session_id, player_id, "user", message, user_mid, now)

        response_text = await self._generate_response(
            history=history,
            character_name=character_name or "a brave soul",
            world_name=world_name or "a mindfulness garden",
        )

        ai_mid = str(uuid.uuid4())
        ai_ts = datetime.now(UTC).isoformat()
        history.append({"role": "assistant", "content": response_text})
        self._store.save_message(
            session_id, player_id, "assistant", response_text, ai_mid, ai_ts
        )

        # Trim in-memory cache to avoid unbounded growth
        if len(history) > _MAX_HISTORY_MESSAGES * 2:
            _SESSION_HISTORY[session_id] = history[-_MAX_HISTORY_MESSAGES:]

        logger.info("Message processed for session %s player %s", session_id, player_id)
        return {
            "success": True,
            "message_id": ai_mid,
            "session_id": session_id,
            "response": response_text,
            "timestamp": ai_ts,
        }

    async def _generate_response(
        self,
        history: list[dict[str, str]],
        character_name: str,
        world_name: str,
    ) -> str:
        """Call the LLM with conversation history. Falls back to a static response."""
        llm = self._get_llm()
        if llm is None:
            logger.warning("No LLM configured; returning fallback narrative response")
            return _FALLBACK_RESPONSE

        try:
            system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
                character_name=character_name,
                world_name=world_name,
            )
            lc_messages: list[Any] = [SystemMessage(content=system_prompt)]

            for turn in history[-_MAX_HISTORY_MESSAGES:]:
                if turn["role"] == "user":
                    lc_messages.append(HumanMessage(content=turn["content"]))
                else:
                    lc_messages.append(AIMessage(content=turn["content"]))

            ai_response = await llm.ainvoke(lc_messages)
            return ai_response.content.strip()  # type: ignore[union-attr]

        except Exception as exc:
            logger.warning("LLM call failed; returning fallback response: %s", exc)
            return _FALLBACK_RESPONSE

    def clear_session_history(self, session_id: str) -> None:
        """Remove conversation history for a session from cache and store."""
        _SESSION_HISTORY.pop(session_id, None)
        self._store.clear_messages(session_id)
        logger.debug("Cleared conversation history for session %s", session_id)

    def get_session_history(self, session_id: str) -> list[dict[str, str]]:
        """Return a copy of the conversation history for a session."""
        return list(self._load_history_from_store(session_id))
