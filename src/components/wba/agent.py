"""WBA — World Building Agent implementation.

Receives a ProcessedInput from the IPA, queries Neo4j (via WorldContextBuilder)
for location/NPC/event/rule data, and returns an enriched WorldContext for the NGA.

Architecture:
  WBAAgent.build(processed_input, ...)
    └── WorldContextBuilder.build()  — 6-tier Neo4j traversal
          world context assembled from location_id in ProcessedInput
    Returns WorldContext (or a minimal stub when Neo4j is unavailable)

The WBA does not make an LLM call — it is purely a context assembly layer.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from src.components.world_context.models import (
    LocationFact,
    WorldContext,
)

if TYPE_CHECKING:
    from src.components.world_context.builder import WorldContextBuilder

from src.components.ipa.models import ProcessedInput

logger = logging.getLogger(__name__)


def _minimal_world_context(location_id: str) -> WorldContext:
    """Return a minimal stub WorldContext when Neo4j is unavailable."""
    return WorldContext(
        location_id=location_id,
        location=LocationFact(
            id=location_id,
            name="Unknown Location",
            description="The world is quiet. Details are unavailable right now.",
        ),
        traversal_depth=1,
    )


class WBAAgent:
    """World Building Agent — second stage of the IPA → WBA → NGA pipeline.

    Takes a ProcessedInput and assembles a WorldContext by traversing Neo4j.
    Degrades gracefully to a minimal stub when Neo4j is unavailable.

    Usage::

        agent = WBAAgent(builder=world_context_builder)
        ctx = await agent.build(processed_input)
        # ctx.location.name, ctx.npcs, ctx.active_events, ...
    """

    def __init__(
        self,
        builder: WorldContextBuilder | None = None,
        player_character: dict[str, Any] | None = None,
    ) -> None:
        """
        Args:
            builder:          WorldContextBuilder for Neo4j traversal.
                              When None the agent returns minimal stubs.
            player_character: Optional character sheet forwarded to tier-6 context.
        """
        self._builder = builder
        self._player_character = player_character

    async def build(
        self,
        processed_input: ProcessedInput,
        player_character: dict[str, Any] | None = None,
    ) -> WorldContext:
        """Assemble WorldContext from a ProcessedInput.

        Args:
            processed_input: Structured output from the IPA.
            player_character: Optional override for character sheet data.

        Returns:
            WorldContext with location, NPCs, events, rules, and connections.
        """
        session_id = processed_input.session_id
        player_id = processed_input.player_id
        location_id = processed_input.location_id

        if not location_id:
            logger.warning(
                "wba: session=%s no location_id in ProcessedInput — using stub",
                session_id,
            )
            return _minimal_world_context("unknown")

        if self._builder is None:
            logger.warning(
                "wba: session=%s no WorldContextBuilder configured — using stub",
                session_id,
            )
            return _minimal_world_context(location_id)

        char = player_character or self._player_character
        try:
            assembled = await self._builder.build(
                session_id=session_id,
                location_id=location_id,
                player_id=player_id,
                player_character=char,
            )

            logger.info(
                "wba: session=%s location=%s tokens=%d neo4j=%s",
                session_id,
                location_id,
                assembled.total_tokens,
                assembled.neo4j_available,
            )

            # The builder returns AssembledContext; we need WorldContext.
            # The traversal engine stores the raw WorldContext inside neo4j_context.
            neo4j_ctx: WorldContext | None = getattr(assembled, "neo4j_context", None)
            if neo4j_ctx is not None:
                return neo4j_ctx

            # Fallback: builder ran but didn't expose WorldContext directly.
            # This means Neo4j was unavailable — return a minimal stub so the
            # NGA can still generate a response.
            logger.debug(
                "wba: session=%s no neo4j_context on AssembledContext — using stub",
                session_id,
            )
            return _minimal_world_context(location_id)

        except Exception as exc:
            logger.error(
                "wba: session=%s world context build failed: %s", session_id, exc
            )
            return _minimal_world_context(location_id)
