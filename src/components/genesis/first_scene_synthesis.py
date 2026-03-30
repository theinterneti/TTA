"""
FirstSceneSynthesisService — generate the opening scene from a completed WorldSeed.

Given a WorldSeed (and optional player character overrides), the service:
  1. Calls an LLM to produce structured scene data (Location, NPCs, opening text).
  2. Writes Location, NPC, and initial WorldEvent nodes into Neo4j.
  3. Returns a FirstScene dataclass containing the scene text + all created node IDs.

See: docs/design/genesis-session.md
Issue: #287
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
try:
    from ttadev.primitives import (
        FallbackPrimitive,
        RetryPrimitive,
        RetryStrategy,
        WorkflowContext,
        WorkflowPrimitive,
    )
except ImportError:
    from tta_dev_primitives import (  # type: ignore[no-redef]
        FallbackPrimitive,
        RetryPrimitive,
        RetryStrategy,
        WorkflowContext,
        WorkflowPrimitive,
    )

from src.ai_components.llm_factory import get_llm
from src.components.gameplay_loop.models.world_seed import WorldSeed

if TYPE_CHECKING:
    from neo4j import AsyncDriver

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

_SYNTHESIS_SCHEMA = {
    "scene_text": "string — 2-4 paragraph evocative opening narration",
    "location": {
        "name": "string",
        "description": "string",
        "location_type": "string (e.g. tavern, crossroads, market, forest)",
        "atmosphere": "string — one sentence sensory detail",
    },
    "npcs": [
        {
            "name": "string",
            "role": "string (e.g. innkeeper, merchant, wanderer)",
            "description": "string — one sentence",
            "disposition": "string (friendly, neutral, suspicious, hostile)",
        }
    ],
}

_SYSTEM_PROMPT = f"""\
You are a world-builder for a therapeutic text adventure. Given a WorldSeed, \
produce a JSON object describing the player's opening scene.

Rules:
- The scene must feel grounded in the WorldSeed's tone, power source, and detail.
- Include 1-3 NPCs present in the location (can be 0 if solitary arrival fits).
- scene_text is first-person present tense ("You step into…").
- Keep descriptions evocative but concise.
- Return ONLY valid JSON matching this schema (no markdown fences):
{json.dumps(_SYNTHESIS_SCHEMA, indent=2)}
"""


@dataclass
class FirstScene:
    """The synthesised opening scene returned to callers.

    Attributes:
        scene_text:    The narrative opening text shown to the player.
        location_id:   Neo4j node ID of the created Location.
        npc_ids:       Neo4j node IDs of all created NPC nodes.
        event_id:      Neo4j node ID of the 'player_arrival' WorldEvent.
        location_name: Human-readable location name.
        raw_synthesis: The raw LLM output dict for debugging / audit.
    """

    scene_text: str
    location_id: str
    npc_ids: list[str] = field(default_factory=list)
    event_id: str = ""
    location_name: str = ""
    raw_synthesis: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# LLM call primitives
# ---------------------------------------------------------------------------


class _SynthesisCall(WorkflowPrimitive):
    """Call the LLM to produce structured scene JSON."""

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        llm = input_data["llm"]
        messages = input_data["messages"]
        response = await llm.ainvoke(messages)
        text: str = response.content if hasattr(response, "content") else str(response)
        # Strip optional markdown fences if the model adds them
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0]
        return json.loads(text)


class _SynthesisFallback(WorkflowPrimitive):
    """Return a minimal deterministic scene when the LLM call fails."""

    async def execute(
        self, input_data: dict[str, Any], context: WorkflowContext
    ) -> dict[str, Any]:
        seed: WorldSeed = input_data["seed"]
        detail = seed.one_specific_detail
        return {
            "scene_text": (
                f"You arrive at the edge of a world shaped by {seed.tone.value} forces, "
                f"where {seed.power_source.value} holds sway. "
                f"One thing is immediately clear: {detail}. "
                "The path ahead awaits."
            ),
            "location": {
                "name": "The Threshold",
                "description": f"A liminal place touched by {seed.tone.value}.",
                "location_type": "crossroads",
                "atmosphere": "The air carries the weight of possibility.",
            },
            "npcs": [],
        }


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class FirstSceneSynthesisService:
    """
    Synthesise the opening scene from a completed WorldSeed.

    Example::

        service = FirstSceneSynthesisService(neo4j_driver)
        first_scene = await service.synthesize(world_seed)
        print(first_scene.scene_text)
    """

    def __init__(
        self,
        neo4j_driver: AsyncDriver | None = None,
        *,
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0.8,
        max_retries: int = 3,
    ) -> None:
        """
        Args:
            neo4j_driver: Live Neo4j driver for writing nodes.  If ``None``,
                          Neo4j writes are skipped (useful for testing / dry-run).
            model:        LLM model identifier passed to :func:`get_llm`.
            temperature:  Sampling temperature for the scene narration call.
            max_retries:  Maximum LLM retry attempts.
        """
        self._driver = neo4j_driver
        self._model = model
        self._temperature = temperature
        self._strategy = RetryStrategy(
            max_retries=max_retries,
            backoff_base=1.0,
            max_backoff=30.0,
            jitter=True,
        )

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    async def synthesize(
        self,
        world_seed: WorldSeed,
        player_character: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> FirstScene:
        """Generate the opening scene and persist nodes to Neo4j.

        Args:
            world_seed:        Completed WorldSeed from the Genesis Session.
            player_character:  Optional character overrides (name, background, etc.).
            session_id:        Session ID for WorkflowContext tracing.

        Returns:
            :class:`FirstScene` with narrative text and Neo4j node IDs.
        """
        sid = session_id or f"synthesis-{uuid4()}"
        ctx = WorkflowContext(workflow_id=sid)

        synthesis = await self._call_llm(world_seed, player_character, ctx)
        location_id, npc_ids, event_id = await self._write_neo4j(
            synthesis, world_seed, player_character, sid
        )

        return FirstScene(
            scene_text=synthesis.get("scene_text", ""),
            location_id=location_id,
            npc_ids=npc_ids,
            event_id=event_id,
            location_name=synthesis.get("location", {}).get("name", ""),
            raw_synthesis=synthesis,
        )

    # ------------------------------------------------------------------ #
    # Internal: LLM call                                                   #
    # ------------------------------------------------------------------ #

    async def _call_llm(
        self,
        world_seed: WorldSeed,
        player_character: dict[str, Any] | None,
        ctx: WorkflowContext,
    ) -> dict[str, Any]:
        llm = get_llm(model=self._model, temperature=self._temperature)
        messages = self._build_messages(world_seed, player_character)

        input_data: dict[str, Any] = {
            "llm": llm,
            "messages": messages,
            "seed": world_seed,
        }

        primitive: WorkflowPrimitive = FallbackPrimitive(
            RetryPrimitive(_SynthesisCall(), strategy=self._strategy),
            _SynthesisFallback(),
        )
        result: dict[str, Any] = await primitive.execute(input_data, ctx)
        return result

    def _build_messages(
        self,
        seed: WorldSeed,
        player_character: dict[str, Any] | None,
    ) -> list[SystemMessage | HumanMessage]:
        seed_summary = (
            f"- Tone: {seed.tone.value}\n"
            f"- Power source: {seed.power_source.value}\n"
            f"- Player position: {seed.player_position.value}\n"
            f"- Key detail: {seed.one_specific_detail}\n"
        )
        if seed.geography_archetype:
            seed_summary += f"- Geography: {seed.geography_archetype}\n"
        if seed.culture_tone:
            seed_summary += f"- Culture: {seed.culture_tone}\n"
        if seed.cultural_tension:
            seed_summary += f"- Tension: {seed.cultural_tension}\n"

        char_summary = ""
        if player_character:
            name = player_character.get("name") or seed.character_name or "the player"
            bg = player_character.get("background") or seed.character_background
            char_summary = f"\nPlayer character: {name}"
            if bg:
                char_summary += f", background: {bg}"
        elif seed.character_name:
            char_summary = f"\nPlayer character: {seed.character_name}"
            if seed.character_background:
                char_summary += f", background: {seed.character_background}"

        human_text = (
            f"WorldSeed:\n{seed_summary}"
            f"{char_summary}\n\n"
            "Generate the opening scene JSON."
        )
        return [SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=human_text)]

    # ------------------------------------------------------------------ #
    # Internal: Neo4j writes                                               #
    # ------------------------------------------------------------------ #

    async def _write_neo4j(
        self,
        synthesis: dict[str, Any],
        world_seed: WorldSeed,
        player_character: dict[str, Any] | None,
        session_id: str,
    ) -> tuple[str, list[str], str]:
        """Write Location, NPC, and WorldEvent nodes; return their IDs."""
        if self._driver is None:
            logger.info("Neo4j driver not set — skipping graph writes")
            return str(uuid4()), [], str(uuid4())

        location_id = str(uuid4())
        loc_data = synthesis.get("location", {})
        npc_ids: list[str] = []
        event_id = str(uuid4())

        async with self._driver.session() as neo_session:
            # ── Location ──────────────────────────────────────────────
            await neo_session.run(
                """
                MERGE (l:Location {id: $id})
                SET l.name        = $name,
                    l.description = $desc,
                    l.location_type = $ltype,
                    l.atmosphere  = $atm,
                    l.session_id  = $session_id,
                    l.created_at  = datetime()
                """,
                id=location_id,
                name=loc_data.get("name", "Unknown"),
                desc=loc_data.get("description", ""),
                ltype=loc_data.get("location_type", "unknown"),
                atm=loc_data.get("atmosphere", ""),
                session_id=session_id,
            )
            logger.debug(
                "Created Location node %s: %s", location_id, loc_data.get("name")
            )

            # ── NPCs ──────────────────────────────────────────────────
            for npc_data in synthesis.get("npcs", []):
                npc_id = str(uuid4())
                await neo_session.run(
                    """
                    MERGE (n:NPC {id: $id})
                    SET n.name                = $name,
                        n.role                = $role,
                        n.description         = $desc,
                        n.disposition         = $disposition,
                        n.current_location_id = $location_id,
                        n.is_active           = true,
                        n.session_id          = $session_id,
                        n.created_at          = datetime()
                    WITH n
                    MATCH (l:Location {id: $location_id})
                    MERGE (n)-[:LIVES_IN]->(l)
                    """,
                    id=npc_id,
                    name=npc_data.get("name", "Unknown"),
                    role=npc_data.get("role", ""),
                    desc=npc_data.get("description", ""),
                    disposition=npc_data.get("disposition", "neutral"),
                    location_id=location_id,
                    session_id=session_id,
                )
                npc_ids.append(npc_id)
                logger.debug("Created NPC node %s: %s", npc_id, npc_data.get("name"))

            # ── WorldEvent: player_arrival ────────────────────────────
            await neo_session.run(
                """
                MERGE (e:WorldEvent {id: $id})
                SET e.name        = 'player_arrival',
                    e.event_type  = 'player_arrival',
                    e.description = $desc,
                    e.location_id = $location_id,
                    e.is_active   = true,
                    e.session_id  = $session_id,
                    e.created_at  = datetime()
                WITH e
                MATCH (l:Location {id: $location_id})
                MERGE (e)-[:HAD_EVENT]->(l)
                """,
                id=event_id,
                desc=f"Player arrived at {loc_data.get('name', 'the location')}.",
                location_id=location_id,
                session_id=session_id,
            )
            logger.debug("Created WorldEvent player_arrival %s", event_id)

        return location_id, npc_ids, event_id
