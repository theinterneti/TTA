"""
Neo4j world graph schema: constraints, indexes, and node/relationship constants.

Manages the world-graph nodes (Location, NPC, WorldRule, WorldEvent,
PlayerCharacter, Faction, Zone) used by WorldContextBuilder and the living
worlds system.

See: docs/architecture/neo4j-schema.md for full specification.
Issue: #272
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neo4j import AsyncDriver

logger = logging.getLogger(__name__)


class WorldGraphSchema:
    """Constraint, index, and node-label definitions for the TTA world graph."""

    # ------------------------------------------------------------------ #
    # Node labels                                                          #
    # ------------------------------------------------------------------ #
    class Nodes:
        LOCATION = "Location"
        NPC = "NPC"
        WORLD_RULE = "WorldRule"
        WORLD_EVENT = "WorldEvent"
        PLAYER_CHARACTER = "PlayerCharacter"
        FACTION = "Faction"
        ZONE = "Zone"

    # ------------------------------------------------------------------ #
    # Relationship types                                                   #
    # ------------------------------------------------------------------ #
    class Rels:
        CONNECTED_TO = "CONNECTED_TO"
        LIVES_IN = "LIVES_IN"
        HAS_RELATIONSHIP = "HAS_RELATIONSHIP"
        HAD_EVENT = "HAD_EVENT"
        INVOLVED = "INVOLVED"
        IN_ZONE = "IN_ZONE"
        GOVERNED_BY = "GOVERNED_BY"
        MEMBER_OF = "MEMBER_OF"
        CURRENTLY_AT = "CURRENTLY_AT"
        AFFECTED_BY = "AFFECTED_BY"
        AFFECTS_ZONE = "AFFECTS_ZONE"
        APPLIES_TO_ZONE = "APPLIES_TO_ZONE"
        APPLIES_TO_LOCATION = "APPLIES_TO_LOCATION"

    # ------------------------------------------------------------------ #
    # Constraints                                                          #
    # ------------------------------------------------------------------ #
    @classmethod
    def get_constraints(cls) -> list[str]:
        """Return Cypher statements to create all uniqueness constraints."""
        n = cls.Nodes
        return [
            f"CREATE CONSTRAINT location_id_unique IF NOT EXISTS "
            f"FOR (n:{n.LOCATION}) REQUIRE n.id IS UNIQUE",
            f"CREATE CONSTRAINT npc_id_unique IF NOT EXISTS "
            f"FOR (n:{n.NPC}) REQUIRE n.id IS UNIQUE",
            f"CREATE CONSTRAINT world_rule_id_unique IF NOT EXISTS "
            f"FOR (n:{n.WORLD_RULE}) REQUIRE n.id IS UNIQUE",
            f"CREATE CONSTRAINT world_event_id_unique IF NOT EXISTS "
            f"FOR (n:{n.WORLD_EVENT}) REQUIRE n.id IS UNIQUE",
            f"CREATE CONSTRAINT player_character_id_unique IF NOT EXISTS "
            f"FOR (n:{n.PLAYER_CHARACTER}) REQUIRE n.id IS UNIQUE",
            f"CREATE CONSTRAINT faction_id_unique IF NOT EXISTS "
            f"FOR (n:{n.FACTION}) REQUIRE n.id IS UNIQUE",
            f"CREATE CONSTRAINT zone_id_unique IF NOT EXISTS "
            f"FOR (n:{n.ZONE}) REQUIRE n.id IS UNIQUE",
            # Required-property (NOT NULL) constraints
            f"CREATE CONSTRAINT location_name_exists IF NOT EXISTS "
            f"FOR (n:{n.LOCATION}) REQUIRE n.name IS NOT NULL",
            f"CREATE CONSTRAINT npc_name_exists IF NOT EXISTS "
            f"FOR (n:{n.NPC}) REQUIRE n.name IS NOT NULL",
            f"CREATE CONSTRAINT world_rule_description_exists IF NOT EXISTS "
            f"FOR (n:{n.WORLD_RULE}) REQUIRE n.description IS NOT NULL",
            f"CREATE CONSTRAINT world_event_name_exists IF NOT EXISTS "
            f"FOR (n:{n.WORLD_EVENT}) REQUIRE n.name IS NOT NULL",
            f"CREATE CONSTRAINT player_character_player_id_exists IF NOT EXISTS "
            f"FOR (n:{n.PLAYER_CHARACTER}) REQUIRE n.player_id IS NOT NULL",
        ]

    # ------------------------------------------------------------------ #
    # Indexes                                                              #
    # ------------------------------------------------------------------ #
    @classmethod
    def get_indexes(cls) -> list[str]:
        """Return Cypher statements to create performance indexes."""
        n = cls.Nodes
        return [
            # Location
            f"CREATE INDEX location_name_idx IF NOT EXISTS "
            f"FOR (n:{n.LOCATION}) ON (n.name)",
            f"CREATE INDEX location_zone_idx IF NOT EXISTS "
            f"FOR (n:{n.LOCATION}) ON (n.zone_id)",
            f"CREATE INDEX location_type_idx IF NOT EXISTS "
            f"FOR (n:{n.LOCATION}) ON (n.location_type)",
            # NPC
            f"CREATE INDEX npc_name_idx IF NOT EXISTS "
            f"FOR (n:{n.NPC}) ON (n.name)",
            f"CREATE INDEX npc_faction_idx IF NOT EXISTS "
            f"FOR (n:{n.NPC}) ON (n.faction_id)",
            f"CREATE INDEX npc_location_idx IF NOT EXISTS "
            f"FOR (n:{n.NPC}) ON (n.current_location_id)",
            f"CREATE INDEX npc_active_idx IF NOT EXISTS "
            f"FOR (n:{n.NPC}) ON (n.is_active)",
            # WorldRule
            f"CREATE INDEX world_rule_scope_idx IF NOT EXISTS "
            f"FOR (n:{n.WORLD_RULE}) ON (n.scope)",
            f"CREATE INDEX world_rule_scope_id_idx IF NOT EXISTS "
            f"FOR (n:{n.WORLD_RULE}) ON (n.scope_id)",
            f"CREATE INDEX world_rule_active_idx IF NOT EXISTS "
            f"FOR (n:{n.WORLD_RULE}) ON (n.is_active)",
            f"CREATE INDEX world_rule_category_idx IF NOT EXISTS "
            f"FOR (n:{n.WORLD_RULE}) ON (n.category)",
            # WorldEvent
            f"CREATE INDEX world_event_active_idx IF NOT EXISTS "
            f"FOR (n:{n.WORLD_EVENT}) ON (n.is_active)",
            f"CREATE INDEX world_event_location_idx IF NOT EXISTS "
            f"FOR (n:{n.WORLD_EVENT}) ON (n.location_id)",
            f"CREATE INDEX world_event_zone_idx IF NOT EXISTS "
            f"FOR (n:{n.WORLD_EVENT}) ON (n.zone_id)",
            f"CREATE INDEX world_event_type_idx IF NOT EXISTS "
            f"FOR (n:{n.WORLD_EVENT}) ON (n.event_type)",
            f"CREATE INDEX world_event_expires_idx IF NOT EXISTS "
            f"FOR (n:{n.WORLD_EVENT}) ON (n.expires_at)",
            # PlayerCharacter
            f"CREATE INDEX player_char_player_idx IF NOT EXISTS "
            f"FOR (n:{n.PLAYER_CHARACTER}) ON (n.player_id)",
            f"CREATE INDEX player_char_location_idx IF NOT EXISTS "
            f"FOR (n:{n.PLAYER_CHARACTER}) ON (n.current_location_id)",
            # Faction
            f"CREATE INDEX faction_name_idx IF NOT EXISTS "
            f"FOR (n:{n.FACTION}) ON (n.name)",
            f"CREATE INDEX faction_active_idx IF NOT EXISTS "
            f"FOR (n:{n.FACTION}) ON (n.is_active)",
            # Zone
            f"CREATE INDEX zone_name_idx IF NOT EXISTS "
            f"FOR (n:{n.ZONE}) ON (n.name)",
            f"CREATE INDEX zone_type_idx IF NOT EXISTS "
            f"FOR (n:{n.ZONE}) ON (n.zone_type)",
        ]

    # ------------------------------------------------------------------ #
    # Initialization                                                       #
    # ------------------------------------------------------------------ #
    @classmethod
    async def initialize(cls, driver: AsyncDriver) -> bool:
        """Apply all constraints and indexes to Neo4j.

        Safe to call on every startup — all statements use IF NOT EXISTS.

        Args:
            driver: Connected AsyncDriver instance.

        Returns:
            True if all statements succeeded (or already existed).
        """
        success = True
        async with driver.session() as session:
            for stmt in cls.get_constraints():
                try:
                    await session.run(stmt)  # type: ignore[arg-type]
                    logger.debug("Schema: applied constraint")
                except Exception as exc:
                    logger.warning("Schema constraint skipped: %s", exc)
                    success = False

            for stmt in cls.get_indexes():
                try:
                    await session.run(stmt)  # type: ignore[arg-type]
                    logger.debug("Schema: applied index")
                except Exception as exc:
                    logger.warning("Schema index skipped: %s", exc)
                    success = False

        if success:
            logger.info("WorldGraphSchema initialized successfully")
        else:
            logger.warning(
                "WorldGraphSchema initialized with some skipped statements"
            )
        return success
