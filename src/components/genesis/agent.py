"""
Genesis Agent — the LLM integration layer for the Genesis Session.

Drives the five-act onboarding conversation, extracts WorldSeed fields from
player responses, and transitions the state machine at the right moment.

Architecture:
  GenesisAgent.respond(state, player_input)
    ├── SeedExtractor        — parallel lightweight JSON call to extract fields
    ├── guide_generator      — single call in THE_BECOMING to create guide character
    └── _NarratorCall        — main conversational LLM call (narrator voice)
          wrapped in FallbackPrimitive(RetryPrimitive(...))

All LLM calls use TTA.dev's RetryPrimitive + FallbackPrimitive from
ttadev.primitives for provider selection.

See: docs/design/genesis-session.md
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from langchain_core.messages import AIMessage, HumanMessage

if TYPE_CHECKING:
    from ttadev.primitives import (
        FallbackPrimitive,
        RetryPrimitive,
        RetryStrategy,
        WorkflowContext,
        WorkflowPrimitive,
    )

with contextlib.suppress(ImportError):
    from ttadev.primitives import (
        FallbackPrimitive,
        RetryPrimitive,
        RetryStrategy,
        WorkflowContext,
        WorkflowPrimitive,
    )
from ttadev.agents import ModelRouterChatAdapter  # noqa: F401
from ttadev.agents.protocol import ChatMessage, ChatPrimitive
from ttadev.primitives.llm import ModelRouterPrimitive  # noqa: F401
from ttadev.primitives.recovery.circuit_breaker_primitive import (  # noqa: F401
    CircuitBreakerConfig,
    CircuitBreakerPrimitive,
)

from src.components.gameplay_loop.models.world_seed import GuideCharacter, WorldSeed
from src.components.model_management.mode_runner import MODES_PATH  # noqa: F401

from .guide_generator import derive_guide_character
from .narrator_voice import get_system_prompt
from .seed_extractor import SeedExtractor
from .session_state import Act, GenesisSessionState

logger = logging.getLogger(__name__)

# Phrases that trigger the "surprise me" path
_SURPRISE_PHRASES = frozenset(
    {
        "surprise me",
        "you choose",
        "you decide",
        "make the choices",
        "decide for me",
        "i don't mind",
        "whatever you think",
        "up to you",
    }
)

_SAFE_FALLBACK = (
    "I find myself momentarily at a loss. "
    "Take your time — the world isn't going anywhere."
)

# Fields checked for the minimum-viable-seed transition gate
_WORLD_FIELDS = {"tone", "power_source", "player_position", "one_specific_detail"}


# ── LLM call primitive ────────────────────────────────────────────────────────


@dataclass
class AgentResponse:
    """
    Result of a single Genesis Agent turn.

    Attributes:
        text:         The narrator's response text to send to the player.
        act:          The current act AFTER this turn (may have advanced).
        act_changed:  True if the act advanced during this turn.
        new_fields:   WorldSeed fields extracted from the player's input.
        is_complete:  True when SESSION_BEGUN — the WorldSeed is ready.
        world_seed:   Populated only when is_complete is True.
        guide:        Populated once the guide character has been generated.
    """

    text: str
    act: Act
    act_changed: bool = False
    new_fields: dict[str, Any] = field(default_factory=dict)
    is_complete: bool = False
    world_seed: WorldSeed | None = None
    guide: GuideCharacter | None = None


class _NarratorCall(WorkflowPrimitive):  # type: ignore[misc]
    """One LLM narrator call — wrapped in retry/fallback by the agent."""

    def __init__(self, adapter: ChatPrimitive) -> None:
        self._adapter = adapter

    async def execute(self, input_data: dict, context: WorkflowContext) -> str:
        system_prompt: str = input_data["system_prompt"]
        history: list[AIMessage | HumanMessage] = input_data["history"]
        player_input: str = input_data["player_input"]

        messages: list[ChatMessage] = [
            {
                "role": "assistant" if isinstance(msg, AIMessage) else "user",
                "content": str(msg.content),
            }
            for msg in history
        ]
        if player_input:
            messages.append({"role": "user", "content": player_input})

        content = await self._adapter.chat(messages, system_prompt, context)
        return content.strip()


class _NarratorFallback(WorkflowPrimitive):  # type: ignore[misc]
    async def execute(self, input_data: dict, context: WorkflowContext) -> str:
        return _SAFE_FALLBACK


# ── Act transition logic ──────────────────────────────────────────────────────


def _should_transition(
    state: GenesisSessionState,
    preview_fields: dict[str, Any],
) -> Act | None:
    """
    Determine whether the session should advance to the next act NOW, given
    the fields we're *about* to merge into state.

    Returns the target Act if a transition should happen, else None.
    The caller must advance the act BEFORE generating the response so the
    response is rendered in the new act's voice.

    Note: `turns_here` counts turns ALREADY RECORDED.  We're about to record
    one more, so the effective turn count is `turns_here + 1`.  This means
    transitions fire so the Nth response is rendered in the new act's voice.
    """
    act = state.act
    # +1 because record_turn() hasn't been called yet for the current turn
    effective_turns = state.turns_in_current_act + 1

    # Merge preview so completeness checks are accurate
    merged = {**state.seed_fields, **preview_fields}

    if act == Act.VOID:
        standard = 3
        return Act.BUILDING_WORLD if effective_turns >= standard else None

    if act == Act.BUILDING_WORLD:
        min_turns = 3
        has_required = _WORLD_FIELDS.issubset(merged.keys())
        if has_required and effective_turns >= min_turns:
            return Act.SLIP_PHASE
        return None

    if act == Act.SLIP_PHASE:
        standard = 2
        return Act.BUILDING_CHARACTER if effective_turns >= standard else None

    if act == Act.BUILDING_CHARACTER:
        has_char = bool(
            merged.get("character_name") and merged.get("character_motivation")
        )
        if has_char and effective_turns >= 2:
            return Act.FIRST_LIGHT
        return None

    if act == Act.FIRST_LIGHT:
        if state.first_light_confirmed:
            return Act.THE_BECOMING
        return None

    if act == Act.THE_BECOMING:
        if state.guide_introduced:
            return Act.THE_THRESHOLD
        return None

    if act == Act.THE_THRESHOLD:
        standard = 5
        return Act.SESSION_BEGUN if effective_turns >= standard else None

    return None


# ── History helper ────────────────────────────────────────────────────────────


def _build_history(state: GenesisSessionState, max_turns: int = 10) -> list:
    """Build the LangChain message history from state."""
    recent = state.turns[-max_turns:]
    messages: list = []
    for turn in recent:
        messages.append(HumanMessage(content=turn.player_input))
        messages.append(AIMessage(content=turn.agent_response))
    return messages


# ── World context for system prompt ──────────────────────────────────────────


def _build_world_context(
    state: GenesisSessionState,
    guide: GuideCharacter | None = None,
) -> dict[str, Any]:
    """Build the world_context dict consumed by get_system_prompt()."""
    ctx: dict[str, Any] = dict(state.seed_fields)
    if guide:
        ctx["guide_name"] = guide.name
        ctx["guide_entity_type"] = guide.entity_type
        ctx["guide_intro_line"] = guide.intro_line
    return ctx


# ── Surprise-me detection ─────────────────────────────────────────────────────


def _is_surprise_request(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in _SURPRISE_PHRASES)


# ── First-light confirmation detection ───────────────────────────────────────

_CONFIRM_PHRASES = frozenset(
    {"yes", "yeah", "yep", "sure", "absolutely", "perfect", "love it"}
)
_REDIRECT_PHRASES = frozenset(
    {"no", "change", "different", "not quite", "more like", "actually"}
)


def _check_first_light_response(player_input: str) -> str | None:
    """
    Returns 'confirm', 'redirect', or None based on player's response to first-light.
    """
    lower = player_input.lower()
    if any(p in lower for p in _CONFIRM_PHRASES):
        return "confirm"
    if any(p in lower for p in _REDIRECT_PHRASES):
        return "redirect"
    return None


# ── WorldSeed assembly ────────────────────────────────────────────────────────


def _assemble_world_seed(state: GenesisSessionState) -> WorldSeed | None:
    """
    Attempt to assemble a WorldSeed from the accumulated fields.
    Returns None if required fields are missing.
    """
    from src.components.gameplay_loop.models.world_seed import (
        MagicPresence,
        PlayerPosition,
        PowerSource,
        TechLevel,
        WorldScale,
        WorldTone,
    )

    fields = state.seed_fields
    try:
        return WorldSeed(
            tone=WorldTone(fields["tone"]),
            power_source=PowerSource(fields["power_source"]),
            player_position=PlayerPosition(fields["player_position"]),
            one_specific_detail=fields["one_specific_detail"],
            scale=WorldScale(fields["scale"]) if "scale" in fields else None,
            era_tech_level=TechLevel(fields["era_tech_level"])
            if "era_tech_level" in fields
            else None,
            magic_presence=MagicPresence(fields["magic_presence"])
            if "magic_presence" in fields
            else None,
            character_name=fields.get("character_name"),
            character_motivation=fields.get("character_motivation"),
        )
    except (KeyError, ValueError) as exc:
        logger.warning("genesis_agent: WorldSeed assembly failed: %s", exc)
        return None


# ── Main agent ────────────────────────────────────────────────────────────────


class GenesisAgent:
    """
    The Genesis Agent drives the Genesis Session conversation.

    Responsibilities:
    - Generate narrator responses in the correct voice for the current act
    - Extract WorldSeed fields from player input (parallel lightweight call)
    - Advance the state machine at the right moment
    - Generate the guide character before THE_BECOMING
    - Detect "surprise me" requests and handle them gracefully
    - Return a complete WorldSeed once SESSION_BEGUN is reached

    Usage::

        agent = GenesisAgent()
        state = GenesisSessionState(session_id="abc")
        response = await agent.respond(state, player_input="Hello")
        # response.text  — send this to the player
        # response.act   — may have advanced
        # response.is_complete  — True when WorldSeed is ready
    """

    def __init__(
        self,
        router: ModelRouterPrimitive | None = None,
    ) -> None:
        """
        Args:
            router: Pre-built ModelRouterPrimitive. Created from model_modes.yaml if None.
        """
        _router = router or ModelRouterPrimitive.from_yaml(MODES_PATH)
        self._narrator_adapter: ChatPrimitive = ModelRouterChatAdapter(
            _router, mode="narration"
        )
        self._extraction_adapter: ChatPrimitive = ModelRouterChatAdapter(
            _router, mode="extraction"
        )

        # Resilient narrator call — retry twice, then fallback to safe message
        self._narrator = FallbackPrimitive(  # type: ignore[arg-type]
            primary=RetryPrimitive(  # type: ignore[arg-type]
                _NarratorCall(self._narrator_adapter),
                strategy=RetryStrategy(max_retries=2, backoff_base=1.5),  # type: ignore[arg-type]
            ),
            fallback=_NarratorFallback(),
        )
        self._extractor = SeedExtractor(adapter=self._extraction_adapter)

        # Cached guide character once generated
        self._guide: GuideCharacter | None = None

    async def respond(
        self,
        state: GenesisSessionState,
        player_input: str,
    ) -> AgentResponse:
        """
        Generate the next narrator response and advance the state machine.

        This is the single public method callers use.  It mutates `state`
        in-place (calls `record_turn`, `transition_to`, etc.).

        Args:
            state:        Current Genesis Session state (mutated).
            player_input: What the player just typed.

        Returns:
            AgentResponse with the narrator's text, new act, new fields.
        """
        session_id = state.session_id
        context = WorkflowContext(workflow_id=session_id)
        act_changed = False

        # Restore persisted guide character so stateless callers work correctly
        if self._guide is None and state.guide_character is not None:
            self._guide = state.guide_character

        # ── 1. Handle "surprise me" ───────────────────────────────────────
        if _is_surprise_request(player_input) and not state.surprise_me:
            state.surprise_me = True
            surprise_fields = await self._extractor.generate_surprise_seed(session_id)
            state.seed_fields.update(surprise_fields)
            logger.info("genesis_agent[%s]: surprise seed generated", session_id)

        # ── 2. Extract fields (parallel with surprise check handled above) ─
        extraction_task = None
        if not state.surprise_me or state.act in (Act.BUILDING_CHARACTER,):
            # Always extract character-related fields even in surprise mode
            extraction_task = asyncio.create_task(
                self._extractor.extract(
                    player_input,
                    state.seed_fields,
                    state.act,
                    session_id,
                )
            )

        new_fields: dict[str, Any] = {}
        if extraction_task:
            new_fields = await extraction_task

        # ── 3. Handle FIRST_LIGHT confirmation / redirect ─────────────────
        if state.act == Act.FIRST_LIGHT and state.first_light_paragraph:
            fl_response = _check_first_light_response(player_input)
            if fl_response == "confirm":
                state.first_light_confirmed = True
            elif fl_response == "redirect":
                state.first_light_paragraph = None  # narrator will rewrite

        # ── 4. Check for act transition (uses preview of merged fields) ────
        next_act = _should_transition(state, new_fields)
        if next_act is not None:
            state.transition_to(next_act)
            act_changed = True
            logger.info("genesis_agent[%s]: advanced to act=%s", session_id, next_act)

        # ── 5. Generate guide character before THE_BECOMING response ──────
        if state.act == Act.THE_BECOMING and self._guide is None:
            merged = {**state.seed_fields, **new_fields}
            self._guide = await derive_guide_character(merged, session_id=session_id)
            state.guide_character = self._guide  # persist across requests
            logger.info(
                "genesis_agent[%s]: guide character generated: %s",
                session_id,
                self._guide.name,
            )

        # ── 6. Generate narrator response (in the new act's voice) ────────
        world_context = _build_world_context(state, guide=self._guide)
        system_prompt = get_system_prompt(state.act, world_context)
        history = _build_history(state)

        # Build contextual hints for the narrator
        narrator_input = _build_narrator_input(
            player_input, state, new_fields, self._guide
        )

        response_text = await self._narrator.execute(  # type: ignore[arg-type]
            {
                "system_prompt": system_prompt,
                "history": history,
                "player_input": narrator_input,
            },
            context,  # type: ignore[arg-type]
        )

        # ── 7. Handle THE_BECOMING first-response marking ────────────────
        if state.act == Act.THE_BECOMING and self._guide and not state.guide_introduced:
            state.guide_introduced = True
            logger.debug("genesis_agent[%s]: guide_introduced set", session_id)

        # ── 8. Store first-light paragraph ───────────────────────────────
        if state.act == Act.FIRST_LIGHT and state.first_light_paragraph is None:
            state.first_light_paragraph = response_text

        # ── 9. Record turn ────────────────────────────────────────────────
        state.record_turn(
            player_input=player_input,
            agent_response=response_text,
            new_fields=new_fields if new_fields else None,
            is_slip=_is_slip_appropriate(state),
        )

        # ── 10. Assemble WorldSeed if SESSION_BEGUN ───────────────────────
        world_seed: WorldSeed | None = None
        is_complete = state.act == Act.SESSION_BEGUN
        if is_complete:
            world_seed = _assemble_world_seed(state)
            logger.info(
                "genesis_agent[%s]: session complete — WorldSeed assembled: %s",
                session_id,
                world_seed is not None,
            )

        return AgentResponse(
            text=response_text,
            act=state.act,
            act_changed=act_changed,
            new_fields=new_fields,
            is_complete=is_complete,
            world_seed=world_seed,
            guide=self._guide,
        )

    async def reset(self) -> None:
        """Reset agent state (guide character) for a new session."""
        self._guide = None


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_narrator_input(
    player_input: str,
    state: GenesisSessionState,
    new_fields: dict[str, Any],
    guide: GuideCharacter | None,
) -> str:
    """
    Augment the raw player input with context the narrator needs.

    The narrator LLM receives the player_input but also gets inline hints so it
    knows what was just established without breaking the narrative frame.
    """
    parts = [player_input]

    if new_fields:
        hint = ", ".join(f"{k}" for k in new_fields)
        parts.append(f"[CONTEXT: player established {hint}]")

    if state.act == Act.FIRST_LIGHT and state.first_light_paragraph is None:
        parts.append(
            "[CONTEXT: write the first-light prose paragraph now — "
            "2-4 vivid sentences that place the player's character in the world]"
        )

    if state.act == Act.THE_BECOMING and guide and not state.guide_introduced:
        parts.append(
            f"[CONTEXT: you are now {guide.name}, {guide.entity_type}. "
            f"Begin with: {guide.intro_line!r}]"
        )

    if state.act == Act.SLIP_PHASE and state.can_slip:
        parts.append(
            "[CONTEXT: allow one slip — a small detail about the world "
            "that the narrator 'shouldn't know yet' — keep it subtle]"
        )

    return "\n".join(parts)


def _is_slip_appropriate(state: GenesisSessionState) -> bool:
    """True if this turn should be marked as a slip turn."""
    return state.act == Act.SLIP_PHASE and state.slips_delivered < 2
