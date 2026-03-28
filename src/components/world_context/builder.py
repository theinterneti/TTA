"""WorldContextBuilder — 6-tier context assembly for LLM prompts.

Assembles a structured, token-budgeted context string from:
  Tier 1 — system prompt / world constants (caller-supplied)
  Tier 2 — current scene: location, NPCs, active events (from Neo4j)
  Tier 3 — additional graph context: connections, zone (from Neo4j)
  Tier 4 — world rules and lore (from Neo4j)
  Tier 5 — session history / recent conversation turns
  Tier 6 — player character sheet

All tiers are optional; missing tiers are silently skipped.
Neo4j unavailability degrades gracefully to a Redis/history-only context.

Issue: #276 (token budget + assembly), #278 (integration + observability)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.components.world_context.budget import (
    ALL_TIERS,
    TIER_CHARACTER,
    TIER_HISTORY,
    TIER_NEO4J,
    TIER_RULES,
    TIER_SCENE,
    TIER_SYSTEM,
    TierBudget,
    TokenCounter,
)
from src.components.world_context.models import WorldContext
from src.components.world_context.traversal import Neo4jTraversalEngine

if TYPE_CHECKING:
    from neo4j import AsyncDriver

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional OpenTelemetry — no-op when not installed
# ---------------------------------------------------------------------------

try:
    from opentelemetry import trace as _otel_trace  # type: ignore[import-not-found]

    _tracer = _otel_trace.get_tracer("tta.world_context.builder")
    _otel_available = True
except Exception:
    _tracer = None  # type: ignore[assignment]
    _otel_available = False


# ---------------------------------------------------------------------------
# AssembledContext
# ---------------------------------------------------------------------------


@dataclass
class AssembledContext:
    """Result of a WorldContextBuilder.build() call.

    Attributes:
        text:              Full assembled context ready to inject into a prompt.
        tiers:             Mapping of tier name → rendered text (before concat).
        tier_token_counts: Mapping of tier name → token count.
        total_tokens:      Sum of all tier token counts.
        truncated_tiers:   Names of tiers that were truncated to fit their budget.
        assembly_time_ms:  Wall-clock time for the full build() call.
        neo4j_available:   Whether the Neo4j graph was reachable this call.
    """

    text: str
    tiers: dict[str, str] = field(default_factory=dict)
    tier_token_counts: dict[str, int] = field(default_factory=dict)
    total_tokens: int = 0
    truncated_tiers: list[str] = field(default_factory=list)
    assembly_time_ms: float = 0.0
    neo4j_available: bool = True


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


def _render_scene(ctx: WorldContext) -> str:
    """Render tiers 2 (scene) from a WorldContext."""
    lines: list[str] = []

    loc = ctx.location
    lines.append(f"## Location: {loc.name}")
    if loc.description:
        lines.append(loc.description)
    if loc.atmosphere:
        lines.append(f"*Atmosphere:* {loc.atmosphere}")
    if loc.region:
        lines.append(f"*Region:* {loc.region}")

    if ctx.npcs:
        lines.append("\n### Present Characters")
        for npc in ctx.npcs:
            parts = [f"- **{npc.name}**"]
            if npc.role:
                parts.append(f"({npc.role})")
            if npc.emotional_state:
                parts.append(f"— feels *{npc.emotional_state}*")
            if npc.disposition_toward_player:
                parts.append(f"[{npc.disposition_toward_player}]")
            lines.append(" ".join(parts))

    if ctx.active_events:
        lines.append("\n### Active Events")
        for evt in ctx.active_events:
            desc = f": {evt.description}" if evt.description else ""
            lines.append(f"- **{evt.name}**{desc}")

    return "\n".join(lines)


def _render_neo4j_extra(ctx: WorldContext) -> str:
    """Render tier 3 (additional graph context) from a WorldContext."""
    lines: list[str] = []

    if ctx.connected_locations:
        lines.append("## Nearby Locations")
        for conn in ctx.connected_locations:
            direction = f" ({conn.direction})" if conn.direction else ""
            dist = f" — {conn.distance} units" if conn.distance is not None else ""
            lines.append(f"- {conn.name}{direction}{dist}")

    if ctx.zone:
        lines.append(f"\n## Zone: {ctx.zone.name}")
        if ctx.zone.description:
            lines.append(ctx.zone.description)

    return "\n".join(lines)


def _render_rules(ctx: WorldContext) -> str:
    """Render tier 4 (world rules) from a WorldContext."""
    if not ctx.rules:
        return ""
    lines = ["## World Rules"]
    for rule in sorted(ctx.rules, key=lambda r: r.priority, reverse=True):
        tag = f" [{rule.rule_type}]" if rule.rule_type else ""
        lines.append(f"- **{rule.name}**{tag}: {rule.rule_text}")
    return "\n".join(lines)


def _render_history(messages: list[dict[str, str]]) -> str:
    """Render tier 5 (session history) from a list of {role, content} dicts."""
    if not messages:
        return ""
    lines = ["## Recent Conversation"]
    for msg in messages:
        role = msg.get("role", "user").capitalize()
        content = msg.get("content", "")
        lines.append(f"**{role}:** {content}")
    return "\n".join(lines)


def _render_character(character: dict[str, Any]) -> str:
    """Render tier 6 (player character sheet) from a dict."""
    if not character:
        return ""
    lines = ["## Player Character"]
    for key, val in character.items():
        if key in ("id", "created_at", "updated_at"):
            continue
        label = key.replace("_", " ").title()
        lines.append(f"- **{label}:** {val}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# WorldContextBuilder
# ---------------------------------------------------------------------------


class WorldContextBuilder:
    """Assembles a 6-tier, token-budgeted context for LLM prompts.

    Requires a Neo4j driver for tiers 2–4; session store for tier 5.
    Both are optional — missing tiers are silently omitted.

    Usage::

        builder = WorldContextBuilder(driver=driver, session_store=store)
        ctx = await builder.build(
            session_id="sess-001",
            location_id="loc-forest-clearing",
            player_id="player-001",
        )
        # inject ctx.text into your LLM prompt
    """

    def __init__(
        self,
        driver: AsyncDriver | None = None,
        session_store: Any | None = None,
        budget: TierBudget | None = None,
        counter: TokenCounter | None = None,
    ) -> None:
        self._driver = driver
        self._session_store = session_store
        self._budget = budget or TierBudget()
        self._counter = counter or TokenCounter()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def build(
        self,
        session_id: str,
        location_id: str,
        player_id: str,
        character_id: str | None = None,
        depth: int = 3,
        system_prompt: str = "",
        player_character: dict[str, Any] | None = None,
        history_limit: int = 20,
    ) -> AssembledContext:
        """Assemble a full 6-tier context.

        Args:
            session_id:       Active session ID (tier 5 history).
            location_id:      Current location node ``id`` (tier 2/3/4).
            player_id:        Player ID (for logging/observability).
            character_id:     Optional — passed to history_compressor if used.
            depth:            Neo4j traversal depth 1–3 (default 3).
            system_prompt:    Caller-supplied system text for tier 1.
            player_character: Dict of character properties for tier 6.
            history_limit:    Max recent messages to include in tier 5.

        Returns:
            AssembledContext with full text and per-tier metadata.
        """
        if _otel_available and _tracer is not None:
            with _tracer.start_as_current_span("world_context.build") as span:
                span.set_attribute("session_id", session_id)
                span.set_attribute("location_id", location_id)
                span.set_attribute("player_id", player_id)
                result = await self._build_inner(
                    session_id=session_id,
                    location_id=location_id,
                    player_id=player_id,
                    depth=depth,
                    system_prompt=system_prompt,
                    player_character=player_character,
                    history_limit=history_limit,
                )
                span.set_attribute("total_tokens", result.total_tokens)
                span.set_attribute("assembly_time_ms", result.assembly_time_ms)
                span.set_attribute("neo4j_available", result.neo4j_available)
                span.set_attribute("truncated_tiers", ",".join(result.truncated_tiers))
                return result

        return await self._build_inner(
            session_id=session_id,
            location_id=location_id,
            player_id=player_id,
            depth=depth,
            system_prompt=system_prompt,
            player_character=player_character,
            history_limit=history_limit,
        )

    # ------------------------------------------------------------------
    # Internal assembly
    # ------------------------------------------------------------------

    async def _build_inner(
        self,
        session_id: str,
        location_id: str,
        player_id: str,
        depth: int,
        system_prompt: str,
        player_character: dict[str, Any] | None,
        history_limit: int,
    ) -> AssembledContext:
        t_start = time.perf_counter()
        tiers: dict[str, str] = dict.fromkeys(ALL_TIERS, "")
        neo4j_available = True

        # --- Tier 1: system prompt / world constants ---
        tiers[TIER_SYSTEM] = system_prompt

        # --- Tiers 2–4: Neo4j graph (graceful fallback) ---
        world_ctx: WorldContext | None = None
        if self._driver is not None and location_id:
            try:
                engine = Neo4jTraversalEngine(self._driver)
                world_ctx = await engine.build_context(location_id, depth=depth)
            except Exception as exc:
                logger.warning(
                    "WorldContextBuilder: Neo4j unavailable, degrading to "
                    "history-only context. error=%s",
                    exc,
                )
                neo4j_available = False

        if world_ctx is not None:
            tiers[TIER_SCENE] = _render_scene(world_ctx)
            tiers[TIER_NEO4J] = _render_neo4j_extra(world_ctx)
            tiers[TIER_RULES] = _render_rules(world_ctx)
        else:
            neo4j_available = False

        # --- Tier 5: session history ---
        if self._session_store is not None and session_id:
            try:
                messages: list[dict[str, str]] = self._session_store.load_messages(
                    session_id
                )
                # Most-recent N turns
                if len(messages) > history_limit:
                    messages = messages[-history_limit:]
                tiers[TIER_HISTORY] = _render_history(messages)
            except Exception as exc:
                logger.warning(
                    "WorldContextBuilder: could not load session history: %s", exc
                )

        # --- Tier 6: player character ---
        if player_character:
            tiers[TIER_CHARACTER] = _render_character(player_character)

        # --- Apply token budgets ---
        truncated: list[str] = []
        for tier_name in ALL_TIERS:
            text = tiers[tier_name]
            if not text:
                continue
            budget = self._budget.budget_for(tier_name)
            if not self._counter.fits(text, budget):
                tiers[tier_name] = self._counter.truncate_to_budget(text, budget)
                truncated.append(tier_name)

        # --- Count tokens per tier ---
        tier_counts: dict[str, int] = {
            name: self._counter.count(text) for name, text in tiers.items()
        }
        total = sum(tier_counts.values())

        # --- Assemble final text ---
        parts = [tiers[t] for t in ALL_TIERS if tiers[t]]
        full_text = "\n\n".join(parts)

        elapsed_ms = (time.perf_counter() - t_start) * 1000
        logger.debug(
            "WorldContextBuilder: session=%s location=%s tokens=%d "
            "truncated=%s neo4j=%s elapsed=%.1fms",
            session_id,
            location_id,
            total,
            truncated or "none",
            neo4j_available,
            elapsed_ms,
        )

        return AssembledContext(
            text=full_text,
            tiers=tiers,
            tier_token_counts=tier_counts,
            total_tokens=total,
            truncated_tiers=truncated,
            assembly_time_ms=round(elapsed_ms, 2),
            neo4j_available=neo4j_available,
        )
