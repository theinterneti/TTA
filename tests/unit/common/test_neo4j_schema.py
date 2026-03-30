"""Unit tests for WorldGraphSchema (src/common/neo4j_schema.py).

Issue: #272
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.common.neo4j_schema import WorldGraphSchema


class TestWorldGraphSchemaNodes:
    """Test node label constants."""

    def test_all_node_labels_defined(self) -> None:
        n = WorldGraphSchema.Nodes
        assert n.LOCATION == "Location"
        assert n.NPC == "NPC"
        assert n.WORLD_RULE == "WorldRule"
        assert n.WORLD_EVENT == "WorldEvent"
        assert n.PLAYER_CHARACTER == "PlayerCharacter"
        assert n.FACTION == "Faction"
        assert n.ZONE == "Zone"

    def test_node_labels_are_strings(self) -> None:
        n = WorldGraphSchema.Nodes
        for attr in ("LOCATION", "NPC", "WORLD_RULE", "WORLD_EVENT",
                     "PLAYER_CHARACTER", "FACTION", "ZONE"):
            assert isinstance(getattr(n, attr), str)


class TestWorldGraphSchemaRels:
    """Test relationship type constants."""

    def test_all_relationship_types_defined(self) -> None:
        r = WorldGraphSchema.Rels
        assert r.CONNECTED_TO == "CONNECTED_TO"
        assert r.LIVES_IN == "LIVES_IN"
        assert r.HAS_RELATIONSHIP == "HAS_RELATIONSHIP"
        assert r.HAD_EVENT == "HAD_EVENT"
        assert r.INVOLVED == "INVOLVED"
        assert r.IN_ZONE == "IN_ZONE"
        assert r.GOVERNED_BY == "GOVERNED_BY"
        assert r.MEMBER_OF == "MEMBER_OF"
        assert r.CURRENTLY_AT == "CURRENTLY_AT"
        assert r.AFFECTED_BY == "AFFECTED_BY"
        assert r.AFFECTS_ZONE == "AFFECTS_ZONE"
        assert r.APPLIES_TO_ZONE == "APPLIES_TO_ZONE"
        assert r.APPLIES_TO_LOCATION == "APPLIES_TO_LOCATION"


class TestGetConstraints:
    """Test constraint Cypher statement generation."""

    def test_returns_list_of_strings(self) -> None:
        stmts = WorldGraphSchema.get_constraints()
        assert isinstance(stmts, list)
        assert all(isinstance(s, str) for s in stmts)

    def test_covers_all_seven_node_labels(self) -> None:
        stmts = "\n".join(WorldGraphSchema.get_constraints())
        for label in ("Location", "NPC", "WorldRule", "WorldEvent",
                      "PlayerCharacter", "Faction", "Zone"):
            assert label in stmts, f"Expected {label} in constraints"

    def test_unique_constraints_use_if_not_exists(self) -> None:
        stmts = WorldGraphSchema.get_constraints()
        for stmt in stmts:
            assert "IF NOT EXISTS" in stmt

    def test_uniqueness_constraints_on_id(self) -> None:
        stmts = [s for s in WorldGraphSchema.get_constraints()
                 if "IS UNIQUE" in s]
        # One per node label
        assert len(stmts) == 7

    def test_not_null_constraints_present(self) -> None:
        stmts = [s for s in WorldGraphSchema.get_constraints()
                 if "IS NOT NULL" in s]
        assert len(stmts) >= 4

    def test_no_duplicate_constraint_names(self) -> None:
        import re
        stmts = WorldGraphSchema.get_constraints()
        names = []
        for stmt in stmts:
            m = re.search(r"CONSTRAINT (\w+) IF", stmt)
            if m:
                names.append(m.group(1))
        assert len(names) == len(set(names)), "Duplicate constraint names found"


class TestGetIndexes:
    """Test index Cypher statement generation."""

    def test_returns_list_of_strings(self) -> None:
        stmts = WorldGraphSchema.get_indexes()
        assert isinstance(stmts, list)
        assert all(isinstance(s, str) for s in stmts)

    def test_covers_all_seven_node_labels(self) -> None:
        stmts = "\n".join(WorldGraphSchema.get_indexes())
        for label in ("Location", "NPC", "WorldRule", "WorldEvent",
                      "PlayerCharacter", "Faction", "Zone"):
            assert label in stmts, f"Expected {label} in indexes"

    def test_indexes_use_if_not_exists(self) -> None:
        stmts = WorldGraphSchema.get_indexes()
        for stmt in stmts:
            assert "IF NOT EXISTS" in stmt

    def test_minimum_index_count(self) -> None:
        # At least one index per node label (7) plus extras
        assert len(WorldGraphSchema.get_indexes()) >= 7

    def test_no_duplicate_index_names(self) -> None:
        import re
        stmts = WorldGraphSchema.get_indexes()
        names = []
        for stmt in stmts:
            m = re.search(r"INDEX (\w+) IF", stmt)
            if m:
                names.append(m.group(1))
        assert len(names) == len(set(names)), "Duplicate index names found"

    def test_active_flag_indexed_for_world_event(self) -> None:
        stmts = "\n".join(WorldGraphSchema.get_indexes())
        assert "WorldEvent" in stmts
        assert "is_active" in stmts


class TestInitialize:
    """Test async initialize() with mocked Neo4j driver."""

    @pytest.fixture
    def mock_driver(self) -> MagicMock:
        session = AsyncMock()
        session.run = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        driver = MagicMock()
        driver.session = MagicMock(return_value=session)
        return driver

    @pytest.mark.asyncio
    async def test_returns_true_on_full_success(
        self, mock_driver: MagicMock
    ) -> None:
        result = await WorldGraphSchema.initialize(mock_driver)
        assert result is True

    @pytest.mark.asyncio
    async def test_calls_run_for_all_statements(
        self, mock_driver: MagicMock
    ) -> None:
        await WorldGraphSchema.initialize(mock_driver)
        session = mock_driver.session.return_value.__aenter__.return_value
        expected_calls = (
            len(WorldGraphSchema.get_constraints())
            + len(WorldGraphSchema.get_indexes())
        )
        assert session.run.call_count == expected_calls

    @pytest.mark.asyncio
    async def test_returns_false_on_partial_failure(self) -> None:
        session = AsyncMock()
        session.run = AsyncMock(side_effect=[Exception("already exists"), None])
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        driver = MagicMock()
        driver.session = MagicMock(return_value=session)

        result = await WorldGraphSchema.initialize(driver)
        assert result is False

    @pytest.mark.asyncio
    async def test_continues_after_partial_failure(self) -> None:
        """All statements attempted even when some fail."""
        call_count = 0

        async def run_side_effect(stmt: str) -> None:  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("already exists")

        session = AsyncMock()
        session.run = AsyncMock(side_effect=run_side_effect)
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        driver = MagicMock()
        driver.session = MagicMock(return_value=session)

        await WorldGraphSchema.initialize(driver)

        expected = (
            len(WorldGraphSchema.get_constraints())
            + len(WorldGraphSchema.get_indexes())
        )
        assert call_count == expected

    @pytest.mark.asyncio
    async def test_logs_success(
        self, mock_driver: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging
        with caplog.at_level(logging.INFO, logger="src.common.neo4j_schema"):
            await WorldGraphSchema.initialize(mock_driver)
        assert "initialized successfully" in caplog.text

    @pytest.mark.asyncio
    async def test_logs_warning_on_partial_failure(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging
        session = AsyncMock()
        session.run = AsyncMock(side_effect=Exception("constraint exists"))
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        driver = MagicMock()
        driver.session = MagicMock(return_value=session)

        with caplog.at_level(logging.WARNING, logger="src.common.neo4j_schema"):
            await WorldGraphSchema.initialize(driver)
        assert "skipped" in caplog.text
