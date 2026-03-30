#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Setup_neo4j_schema]]
Setup Neo4j Schema for TTA Living Worlds

Applies WorldGraphSchema constraints and indexes (world graph: Location, NPC,
WorldRule, WorldEvent, PlayerCharacter, Faction, Zone) and GameplayLoopSchema
constraints (therapeutic sessions, scenes, choices).

All statements use IF NOT EXISTS — safe to run on every deploy.

Issue: #272
"""

from __future__ import annotations

import asyncio
import logging
import os

from neo4j import AsyncGraphDatabase

from src.common.neo4j_schema import WorldGraphSchema
from src.components.gameplay_loop.database.schema import GameplayLoopSchema

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


async def setup_schema() -> bool:
    """Apply all Neo4j constraints and indexes idempotently.

    Returns:
        True if all statements succeeded (or already existed).
    """
    driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        await driver.verify_connectivity()
        logger.info("Connected to Neo4j at %s", NEO4J_URI)

        logger.info("Applying WorldGraphSchema (world graph)…")
        world_ok = await WorldGraphSchema.initialize(driver)

        logger.info("Applying GameplayLoopSchema (therapeutic sessions)…")
        gameplay_ok = await GameplayLoopSchema.initialize_schema(driver)

        if world_ok and gameplay_ok:
            logger.info("✓ Schema setup completed successfully")
        else:
            logger.warning(
                "⚠ Schema setup finished with some skipped statements "
                "(world=%s gameplay=%s)",
                world_ok,
                gameplay_ok,
            )

        return world_ok and gameplay_ok

    except Exception as exc:
        logger.error("Schema setup failed: %s", exc)
        return False
    finally:
        await driver.close()


if __name__ == "__main__":
    import sys

    success = asyncio.run(setup_schema())
    sys.exit(0 if success else 1)
