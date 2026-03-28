"""WorldContextBuilder: Neo4j traversal module.

Assembles a grounded WorldContext from the world graph for each player turn.
Used by the IPA agent to provide scene context to WBA/NGA.

Issue: #275

Quickstart::

    from src.components.world_context import Neo4jTraversalEngine, WorldContext

    engine = Neo4jTraversalEngine(driver)
    ctx: WorldContext | None = await engine.build_context("loc-001", depth=3)
"""

from src.components.world_context.models import (
    ConnectedLocation,
    LocationFact,
    NPCState,
    WorldContext,
    WorldEventSummary,
    WorldRuleSummary,
    ZoneSummary,
)
from src.components.world_context.traversal import Neo4jTraversalEngine

__all__ = [
    "Neo4jTraversalEngine",
    "WorldContext",
    "LocationFact",
    "NPCState",
    "WorldEventSummary",
    "WorldRuleSummary",
    "ConnectedLocation",
    "ZoneSummary",
]
