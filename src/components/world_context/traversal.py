"""Neo4jTraversalEngine — Cypher queries for WorldContextBuilder.

Performs a 3-tier traversal from a Location node and assembles a WorldContext.

Tier 1 (depth >= 1): location properties + rules directly bound to location
Tier 2 (depth >= 2): + NPCs, active WorldEvents, connected locations
Tier 3 (depth >= 3): + zone summary, zone/faction WorldRules

All tiers run in parallel via asyncio.gather for <50ms p99 target.

Issue: #275
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from neo4j import AsyncDriver

from src.common.neo4j_schema import WorldGraphSchema
from src.components.world_context.models import (
    ConnectedLocation,
    LocationFact,
    NPCState,
    WorldContext,
    WorldEventSummary,
    WorldRuleSummary,
    ZoneSummary,
)

logger = logging.getLogger(__name__)

N = WorldGraphSchema.Nodes
R = WorldGraphSchema.Rels


# ---------------------------------------------------------------------------
# Cypher queries (module-level constants for reuse / testability)
# ---------------------------------------------------------------------------

QUERY_LOCATION = f"""
MATCH (loc:{N.LOCATION} {{id: $location_id}})
RETURN loc
"""

QUERY_LOCATION_RULES = f"""
MATCH (rule:{N.WORLD_RULE})-[:{R.APPLIES_TO_LOCATION}]->(loc:{N.LOCATION} {{id: $location_id}})
WHERE rule.is_active = true
RETURN rule
ORDER BY rule.priority DESC
"""

QUERY_NPCS = f"""
MATCH (npc:{N.NPC})-[:{R.LIVES_IN}|{R.CURRENTLY_AT}]->(loc:{N.LOCATION} {{id: $location_id}})
WHERE npc.is_active = true
RETURN npc
ORDER BY npc.name
"""

QUERY_ACTIVE_EVENTS = f"""
MATCH (loc:{N.LOCATION} {{id: $location_id}})-[:{R.HAD_EVENT}]->(evt:{N.WORLD_EVENT})
WHERE evt.is_active = true
RETURN evt
ORDER BY evt.name
"""

QUERY_CONNECTED_LOCATIONS = f"""
MATCH (loc:{N.LOCATION} {{id: $location_id}})-[rel:{R.CONNECTED_TO}]->(target:{N.LOCATION})
RETURN target, rel.direction AS direction, rel.distance AS distance
ORDER BY target.name
"""

QUERY_ZONE = f"""
MATCH (loc:{N.LOCATION} {{id: $location_id}})-[:{R.IN_ZONE}]->(zone:{N.ZONE})
RETURN zone
LIMIT 1
"""

QUERY_ZONE_AND_FACTION_RULES = f"""
MATCH (loc:{N.LOCATION} {{id: $location_id}})-[:{R.IN_ZONE}]->(zone:{N.ZONE})
MATCH (rule:{N.WORLD_RULE})-[:{R.APPLIES_TO_ZONE}]->(zone)
WHERE rule.is_active = true
RETURN rule
ORDER BY rule.priority DESC
UNION
MATCH (loc:{N.LOCATION} {{id: $location_id}})-[:{R.GOVERNED_BY}]->(faction:{N.FACTION})
MATCH (rule:{N.WORLD_RULE})-[:{R.APPLIES_TO_ZONE}]->(faction)
WHERE rule.is_active = true
RETURN rule
ORDER BY rule.priority DESC
"""


def _location_from_record(props: dict[str, Any]) -> LocationFact:
    return LocationFact(
        id=props["id"],
        name=props["name"],
        description=props.get("description"),
        region=props.get("region"),
        atmosphere=props.get("atmosphere"),
        is_accessible=props.get("is_accessible", True),
        extra={
            k: v
            for k, v in props.items()
            if k not in {"id", "name", "description", "region", "atmosphere",
                         "is_accessible", "created_at", "updated_at"}
        },
    )


def _npc_from_record(props: dict[str, Any]) -> NPCState:
    return NPCState(
        id=props["id"],
        name=props["name"],
        role=props.get("role"),
        emotional_state=props.get("emotional_state"),
        disposition_toward_player=props.get("disposition_toward_player"),
        is_active=props.get("is_active", True),
        extra={
            k: v
            for k, v in props.items()
            if k not in {"id", "name", "role", "emotional_state",
                         "disposition_toward_player", "is_active",
                         "created_at", "updated_at"}
        },
    )


def _event_from_record(props: dict[str, Any]) -> WorldEventSummary:
    return WorldEventSummary(
        id=props["id"],
        name=props["name"],
        description=props.get("description"),
        event_type=props.get("event_type"),
        is_active=props.get("is_active", True),
        extra={
            k: v
            for k, v in props.items()
            if k not in {"id", "name", "description", "event_type", "is_active",
                         "created_at", "updated_at", "started_at", "ends_at"}
        },
    )


def _rule_from_record(props: dict[str, Any]) -> WorldRuleSummary:
    return WorldRuleSummary(
        id=props["id"],
        name=props["name"],
        rule_text=props.get("rule_text", ""),
        rule_type=props.get("rule_type"),
        scope=props.get("scope"),
        priority=props.get("priority", 0),
        extra={
            k: v
            for k, v in props.items()
            if k not in {"id", "name", "rule_text", "rule_type", "scope",
                         "priority", "is_active", "created_at", "updated_at"}
        },
    )


def _zone_from_record(props: dict[str, Any]) -> ZoneSummary:
    return ZoneSummary(
        id=props["id"],
        name=props["name"],
        description=props.get("description"),
        zone_type=props.get("zone_type"),
        extra={
            k: v
            for k, v in props.items()
            if k not in {"id", "name", "description", "zone_type",
                         "created_at", "updated_at"}
        },
    )


class Neo4jTraversalEngine:
    """Traverses the world graph and assembles a WorldContext.

    Usage::

        engine = Neo4jTraversalEngine(driver)
        ctx = await engine.build_context("loc-001", depth=3)
    """

    def __init__(self, driver: AsyncDriver) -> None:
        self._driver = driver

    # ------------------------------------------------------------------
    # Tier queries (each runs inside its own session for isolation)
    # ------------------------------------------------------------------

    async def _fetch_location(self, location_id: str) -> LocationFact | None:
        async with self._driver.session() as session:
            result = await session.run(  # type: ignore[arg-type]
                QUERY_LOCATION, location_id=location_id
            )
            record = await result.single()
            if record is None:
                return None
            return _location_from_record(dict(record["loc"]))

    async def _fetch_location_rules(
        self, location_id: str
    ) -> list[WorldRuleSummary]:
        async with self._driver.session() as session:
            result = await session.run(  # type: ignore[arg-type]
                QUERY_LOCATION_RULES, location_id=location_id
            )
            return [_rule_from_record(dict(r["rule"])) async for r in result]

    async def _fetch_npcs(self, location_id: str) -> list[NPCState]:
        async with self._driver.session() as session:
            result = await session.run(  # type: ignore[arg-type]
                QUERY_NPCS, location_id=location_id
            )
            return [_npc_from_record(dict(r["npc"])) async for r in result]

    async def _fetch_active_events(
        self, location_id: str
    ) -> list[WorldEventSummary]:
        async with self._driver.session() as session:
            result = await session.run(  # type: ignore[arg-type]
                QUERY_ACTIVE_EVENTS, location_id=location_id
            )
            return [_event_from_record(dict(r["evt"])) async for r in result]

    async def _fetch_connected_locations(
        self, location_id: str
    ) -> list[ConnectedLocation]:
        async with self._driver.session() as session:
            result = await session.run(  # type: ignore[arg-type]
                QUERY_CONNECTED_LOCATIONS, location_id=location_id
            )
            locations = []
            async for r in result:
                props = dict(r["target"])
                locations.append(
                    ConnectedLocation(
                        id=props["id"],
                        name=props["name"],
                        direction=r.get("direction"),
                        distance=r.get("distance"),
                        extra={
                            k: v
                            for k, v in props.items()
                            if k not in {"id", "name", "created_at", "updated_at"}
                        },
                    )
                )
            return locations

    async def _fetch_zone(self, location_id: str) -> ZoneSummary | None:
        async with self._driver.session() as session:
            result = await session.run(  # type: ignore[arg-type]
                QUERY_ZONE, location_id=location_id
            )
            record = await result.single()
            if record is None:
                return None
            return _zone_from_record(dict(record["zone"]))

    async def _fetch_zone_and_faction_rules(
        self, location_id: str
    ) -> list[WorldRuleSummary]:
        async with self._driver.session() as session:
            result = await session.run(  # type: ignore[arg-type]
                QUERY_ZONE_AND_FACTION_RULES, location_id=location_id
            )
            return [_rule_from_record(dict(r["rule"])) async for r in result]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def build_context(
        self,
        location_id: str,
        depth: int = 3,
    ) -> WorldContext | None:
        """Assemble a WorldContext via parallel Cypher traversal.

        Args:
            location_id: The ``id`` property of the Location node.
            depth: Traversal depth 1–3.  1 = location + rules only;
                   2 = + NPCs/events/connected; 3 = + zone/faction rules.

        Returns:
            Populated WorldContext, or None if the location does not exist.
        """
        depth = max(1, min(3, depth))
        t_start = time.perf_counter()

        # Always fetch tier 1 in parallel
        tier1_coros = [
            self._fetch_location(location_id),
            self._fetch_location_rules(location_id),
        ]

        tier2_coros: list[Any] = []
        tier3_coros: list[Any] = []

        if depth >= 2:
            tier2_coros = [
                self._fetch_npcs(location_id),
                self._fetch_active_events(location_id),
                self._fetch_connected_locations(location_id),
            ]
        if depth >= 3:
            tier3_coros = [
                self._fetch_zone(location_id),
                self._fetch_zone_and_faction_rules(location_id),
            ]

        results = await asyncio.gather(
            *tier1_coros, *tier2_coros, *tier3_coros
        )

        location_fact: LocationFact | None = results[0]
        if location_fact is None:
            logger.warning(
                "WorldContextBuilder: location %s not found", location_id
            )
            return None

        location_rules: list[WorldRuleSummary] = results[1]
        all_rules = list(location_rules)

        npcs: list[NPCState] = []
        active_events: list[WorldEventSummary] = []
        connected: list[ConnectedLocation] = []
        zone: ZoneSummary | None = None

        if depth >= 2:
            npcs = results[2]
            active_events = results[3]
            connected = results[4]

        if depth >= 3:
            zone = results[5]
            extra_rules: list[WorldRuleSummary] = results[6]
            # Deduplicate rules by id
            seen = {r.id for r in all_rules}
            all_rules += [r for r in extra_rules if r.id not in seen]

        elapsed_ms = (time.perf_counter() - t_start) * 1000
        logger.debug(
            "WorldContextBuilder: location=%s depth=%d rules=%d npcs=%d "
            "events=%d connected=%d zone=%s elapsed=%.1fms",
            location_id,
            depth,
            len(all_rules),
            len(npcs),
            len(active_events),
            len(connected),
            zone.name if zone else "none",
            elapsed_ms,
        )

        return WorldContext(
            location_id=location_id,
            location=location_fact,
            npcs=npcs,
            active_events=active_events,
            rules=all_rules,
            connected_locations=connected,
            zone=zone,
            traversal_depth=depth,
            query_time_ms=round(elapsed_ms, 2),
        )
