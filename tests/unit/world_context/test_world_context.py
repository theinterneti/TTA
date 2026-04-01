"""Unit tests for WorldContextBuilder — models and traversal engine.

Issue: #275
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.components.world_context import (
    ConnectedLocation,
    LocationFact,
    Neo4jTraversalEngine,
    NPCState,
    WorldContext,
    WorldEventSummary,
    WorldRuleSummary,
    ZoneSummary,
)
from src.components.world_context.traversal import (
    QUERY_ACTIVE_EVENTS,
    QUERY_CONNECTED_LOCATIONS,
    QUERY_LOCATION,
    QUERY_LOCATION_RULES,
    QUERY_NPCS,
    QUERY_ZONE,
    QUERY_ZONE_AND_FACTION_RULES,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_driver(
    *,
    location: dict[str, Any] | None = None,
    rules: list[dict[str, Any]] | None = None,
    npcs: list[dict[str, Any]] | None = None,
    events: list[dict[str, Any]] | None = None,
    connected: list[dict[str, Any]] | None = None,
    zone: dict[str, Any] | None = None,
    zone_rules: list[dict[str, Any]] | None = None,
) -> MagicMock:
    """Build a mock AsyncDriver that returns canned query results."""

    rules = rules or []
    npcs = npcs or []
    events = events or []
    connected = connected or []
    zone_rules = zone_rules or []

    def _make_async_iter(rows: list[dict[str, Any]], key: str = "node"):
        """Return an async iterator that yields mock records."""

        async def _iter():
            for row in rows:
                record = MagicMock()
                record.__getitem__ = MagicMock(side_effect=lambda k: row)
                record.get = MagicMock(side_effect=lambda k, d=None: row.get(k, d))
                yield record

        return _iter()

    async def run_side_effect(query: str, **params: Any):
        q = query.strip()

        if QUERY_LOCATION.strip() in q:
            result = AsyncMock()
            if location is not None:
                record = MagicMock()
                record.__getitem__ = MagicMock(return_value=location)
                result.single = AsyncMock(return_value=record)
            else:
                result.single = AsyncMock(return_value=None)
            return result

        if QUERY_LOCATION_RULES.strip() in q:
            rows = [{"rule": r} for r in rules]
            result = MagicMock()

            async def _aiter_rules():
                for row in rows:
                    r = MagicMock()
                    r.__getitem__ = MagicMock(side_effect=lambda k, _r=row: _r[k])
                    yield r

            result.__aiter__ = lambda self: _aiter_rules()
            return result

        if QUERY_NPCS.strip() in q:
            result = MagicMock()

            async def _aiter_npcs():
                for npc in npcs:
                    r = MagicMock()
                    r.__getitem__ = MagicMock(return_value=npc)
                    yield r

            result.__aiter__ = lambda self: _aiter_npcs()
            return result

        if QUERY_ACTIVE_EVENTS.strip() in q:
            result = MagicMock()

            async def _aiter_evts():
                for evt in events:
                    r = MagicMock()
                    r.__getitem__ = MagicMock(return_value=evt)
                    yield r

            result.__aiter__ = lambda self: _aiter_evts()
            return result

        if QUERY_CONNECTED_LOCATIONS.strip() in q:
            result = MagicMock()

            async def _aiter_conn():
                for conn in connected:
                    r = MagicMock()
                    r.__getitem__ = MagicMock(
                        side_effect=lambda k, _c=conn: _c.get(
                            "target" if k == "target" else k, None
                        )
                    )
                    r.get = MagicMock(
                        side_effect=lambda k, d=None, _c=conn: _c.get(k, d)
                    )
                    yield r

            result.__aiter__ = lambda self: _aiter_conn()
            return result

        if QUERY_ZONE.strip() in q:
            result = AsyncMock()
            if zone is not None:
                record = MagicMock()
                record.__getitem__ = MagicMock(return_value=zone)
                result.single = AsyncMock(return_value=record)
            else:
                result.single = AsyncMock(return_value=None)
            return result

        if QUERY_ZONE_AND_FACTION_RULES.strip() in q:
            result = MagicMock()

            async def _aiter_zrules():
                for zr in zone_rules:
                    r = MagicMock()
                    r.__getitem__ = MagicMock(return_value=zr)
                    yield r

            result.__aiter__ = lambda self: _aiter_zrules()
            return result

        # Default: empty async iterator
        result = MagicMock()
        result.__aiter__ = lambda self: (x for x in [])
        return result

    session = AsyncMock()
    session.run = AsyncMock(side_effect=run_side_effect)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)

    driver = MagicMock()
    driver.session = MagicMock(return_value=session)
    return driver


_LOC = {
    "id": "loc-001",
    "name": "Dark Forest",
    "description": "A dense, misty forest.",
    "region": "Northwood",
    "atmosphere": "eerie",
    "is_accessible": True,
}

_NPC = {
    "id": "npc-001",
    "name": "Elara",
    "role": "guide",
    "emotional_state": "calm",
    "disposition_toward_player": "friendly",
    "is_active": True,
}

_EVENT = {
    "id": "evt-001",
    "name": "Storm approaching",
    "description": "Dark clouds gather.",
    "event_type": "weather",
    "is_active": True,
}

_RULE = {
    "id": "rule-001",
    "name": "No fire",
    "rule_text": "Fires are forbidden in the forest.",
    "rule_type": "restriction",
    "scope": "location",
    "priority": 10,
    "is_active": True,
}

_ZONE_RULE = {
    "id": "rule-002",
    "name": "Zone silence",
    "rule_text": "Speak softly in the sacred zone.",
    "rule_type": "social",
    "scope": "zone",
    "priority": 5,
    "is_active": True,
}

_CONNECTED = {
    "target": {"id": "loc-002", "name": "Clearing"},
    "direction": "north",
    "distance": 1.5,
}

_ZONE = {
    "id": "zone-001",
    "name": "Sacred Wood",
    "description": "Ancient and revered.",
    "zone_type": "sacred",
}


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestWorldContextModel:
    def test_minimal_construction(self) -> None:
        """World Context Model: minimal construction."""
        ctx = WorldContext(
            location_id="loc-001",
            location=LocationFact(id="loc-001", name="Forest"),
        )
        assert ctx.location_id == "loc-001"
        assert ctx.npcs == []
        assert ctx.rules == []
        assert ctx.active_events == []
        assert ctx.connected_locations == []
        assert ctx.zone is None
        assert ctx.traversal_depth == 3

    def test_depth_clamped_by_validator(self) -> None:
        """World Context Model: depth clamped by validator."""
        ctx = WorldContext(
            location_id="x",
            location=LocationFact(id="x", name="X"),
            traversal_depth=1,
        )
        assert ctx.traversal_depth == 1

    def test_location_fact_extra_fields(self) -> None:
        """World Context Model: location fact extra fields."""
        loc = LocationFact(id="x", name="Y", extra={"custom": 42})
        assert loc.extra["custom"] == 42

    def test_npc_state_defaults(self) -> None:
        """World Context Model: npc state defaults."""
        npc = NPCState(id="n", name="Bob")
        assert npc.is_active is True
        assert npc.emotional_state is None

    def test_world_rule_priority_default(self) -> None:
        """World Context Model: world rule priority default."""
        rule = WorldRuleSummary(id="r", name="R", rule_text="text")
        assert rule.priority == 0

    def test_connected_location_optional_fields(self) -> None:
        """World Context Model: connected location optional fields."""
        cl = ConnectedLocation(id="l", name="Cave")
        assert cl.direction is None
        assert cl.distance is None


# ---------------------------------------------------------------------------
# Traversal engine tests
# ---------------------------------------------------------------------------

class TestNeo4jTraversalEngineDepth3:
    """Full depth-3 traversal (all tiers)."""

    @pytest.mark.asyncio
    async def test_returns_world_context(self) -> None:
        """Neo4j Traversal Engine Depth3: returns world context."""
        driver = _make_driver(
            location=_LOC, rules=[_RULE], npcs=[_NPC],
            events=[_EVENT], connected=[_CONNECTED],
            zone=_ZONE, zone_rules=[_ZONE_RULE],
        )
        engine = Neo4jTraversalEngine(driver)
        ctx = await engine.build_context("loc-001", depth=3)
        assert ctx is not None
        assert isinstance(ctx, WorldContext)

    @pytest.mark.asyncio
    async def test_location_populated(self) -> None:
        """Neo4j Traversal Engine Depth3: location populated."""
        driver = _make_driver(location=_LOC)
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001")
        assert ctx is not None
        assert ctx.location.name == "Dark Forest"
        assert ctx.location.region == "Northwood"
        assert ctx.location.atmosphere == "eerie"

    @pytest.mark.asyncio
    async def test_npcs_populated(self) -> None:
        """Neo4j Traversal Engine Depth3: npcs populated."""
        driver = _make_driver(location=_LOC, npcs=[_NPC])
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001")
        assert ctx is not None
        assert len(ctx.npcs) == 1
        assert ctx.npcs[0].name == "Elara"
        assert ctx.npcs[0].emotional_state == "calm"

    @pytest.mark.asyncio
    async def test_active_events_populated(self) -> None:
        """Neo4j Traversal Engine Depth3: active events populated."""
        driver = _make_driver(location=_LOC, events=[_EVENT])
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001")
        assert ctx is not None
        assert len(ctx.active_events) == 1
        assert ctx.active_events[0].event_type == "weather"

    @pytest.mark.asyncio
    async def test_rules_include_location_and_zone_rules(self) -> None:
        """Neo4j Traversal Engine Depth3: rules include location and zone rules."""
        driver = _make_driver(
            location=_LOC, rules=[_RULE],
            zone=_ZONE, zone_rules=[_ZONE_RULE],
        )
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001")
        assert ctx is not None
        rule_ids = {r.id for r in ctx.rules}
        assert "rule-001" in rule_ids
        assert "rule-002" in rule_ids

    @pytest.mark.asyncio
    async def test_zone_populated(self) -> None:
        """Neo4j Traversal Engine Depth3: zone populated."""
        driver = _make_driver(location=_LOC, zone=_ZONE)
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001")
        assert ctx is not None
        assert ctx.zone is not None
        assert ctx.zone.name == "Sacred Wood"

    @pytest.mark.asyncio
    async def test_traversal_depth_recorded(self) -> None:
        """Neo4j Traversal Engine Depth3: traversal depth recorded."""
        driver = _make_driver(location=_LOC)
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001", depth=3)
        assert ctx is not None
        assert ctx.traversal_depth == 3

    @pytest.mark.asyncio
    async def test_query_time_recorded(self) -> None:
        """Neo4j Traversal Engine Depth3: query time recorded."""
        driver = _make_driver(location=_LOC)
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001")
        assert ctx is not None
        assert ctx.query_time_ms is not None
        assert ctx.query_time_ms >= 0

    @pytest.mark.asyncio
    async def test_duplicate_rules_deduplicated(self) -> None:
        """Zone rules with the same id as location rules are not duplicated."""
        driver = _make_driver(
            location=_LOC,
            rules=[_RULE],
            zone=_ZONE,
            zone_rules=[_RULE],  # same rule returned from zone query
        )
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001")
        assert ctx is not None
        ids = [r.id for r in ctx.rules]
        assert ids.count("rule-001") == 1


class TestNeo4jTraversalEngineDepth1:
    """Depth-1: only location + direct rules."""

    @pytest.mark.asyncio
    async def test_depth1_no_npcs_or_events(self) -> None:
        """Neo4j Traversal Engine Depth1: depth1 no npcs or events."""
        driver = _make_driver(location=_LOC, npcs=[_NPC], events=[_EVENT])
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001", depth=1)
        assert ctx is not None
        assert ctx.npcs == []
        assert ctx.active_events == []
        assert ctx.connected_locations == []
        assert ctx.zone is None
        assert ctx.traversal_depth == 1

    @pytest.mark.asyncio
    async def test_depth1_rules_included(self) -> None:
        """Neo4j Traversal Engine Depth1: depth1 rules included."""
        driver = _make_driver(location=_LOC, rules=[_RULE])
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001", depth=1)
        assert ctx is not None
        assert len(ctx.rules) == 1


class TestNeo4jTraversalEngineDepth2:
    """Depth-2: location + rules + NPCs/events/connected but no zone."""

    @pytest.mark.asyncio
    async def test_depth2_has_npcs_and_events(self) -> None:
        """Neo4j Traversal Engine Depth2: depth2 has npcs and events."""
        driver = _make_driver(
            location=_LOC, npcs=[_NPC], events=[_EVENT], connected=[_CONNECTED]
        )
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001", depth=2)
        assert ctx is not None
        assert len(ctx.npcs) == 1
        assert len(ctx.active_events) == 1
        assert len(ctx.connected_locations) == 1

    @pytest.mark.asyncio
    async def test_depth2_no_zone(self) -> None:
        """Neo4j Traversal Engine Depth2: depth2 no zone."""
        driver = _make_driver(location=_LOC, zone=_ZONE)
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001", depth=2)
        assert ctx is not None
        assert ctx.zone is None
        assert ctx.traversal_depth == 2


class TestNeo4jTraversalEngineEdgeCases:
    @pytest.mark.asyncio
    async def test_returns_none_for_missing_location(self) -> None:
        """Neo4j Traversal Engine Edge Cases: returns none for missing location."""
        driver = _make_driver(location=None)
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-999")
        assert ctx is None

    @pytest.mark.asyncio
    async def test_depth_clamped_to_max_3(self) -> None:
        """Neo4j Traversal Engine Edge Cases: depth clamped to max 3."""
        driver = _make_driver(location=_LOC)
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001", depth=99)
        assert ctx is not None
        assert ctx.traversal_depth == 3

    @pytest.mark.asyncio
    async def test_depth_clamped_to_min_1(self) -> None:
        """Neo4j Traversal Engine Edge Cases: depth clamped to min 1."""
        driver = _make_driver(location=_LOC)
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001", depth=0)
        assert ctx is not None
        assert ctx.traversal_depth == 1

    @pytest.mark.asyncio
    async def test_no_zone_at_depth3_is_fine(self) -> None:
        """Neo4j Traversal Engine Edge Cases: no zone at depth3 is fine."""
        driver = _make_driver(location=_LOC, zone=None)
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001", depth=3)
        assert ctx is not None
        assert ctx.zone is None

    @pytest.mark.asyncio
    async def test_empty_graph_returns_bare_location(self) -> None:
        """Neo4j Traversal Engine Edge Cases: empty graph returns bare location."""
        driver = _make_driver(location=_LOC)
        ctx = await Neo4jTraversalEngine(driver).build_context("loc-001")
        assert ctx is not None
        assert ctx.npcs == []
        assert ctx.rules == []
        assert ctx.active_events == []


# ---------------------------------------------------------------------------
# Query constant tests (ensure Cypher strings reference correct labels)
# ---------------------------------------------------------------------------

class TestQueryConstants:
    def test_location_query_uses_correct_label(self) -> None:
        """Query Constants: location query uses correct label."""
        assert "Location" in QUERY_LOCATION
        assert "$location_id" in QUERY_LOCATION

    def test_npcs_query_uses_correct_relationship(self) -> None:
        """Query Constants: npcs query uses correct relationship."""
        assert "LIVES_IN" in QUERY_NPCS or "CURRENTLY_AT" in QUERY_NPCS

    def test_events_query_filters_active(self) -> None:
        """Query Constants: events query filters active."""
        assert "is_active" in QUERY_ACTIVE_EVENTS

    def test_zone_and_faction_rules_query_uses_union(self) -> None:
        """Query Constants: zone and faction rules query uses union."""
        assert "UNION" in QUERY_ZONE_AND_FACTION_RULES
