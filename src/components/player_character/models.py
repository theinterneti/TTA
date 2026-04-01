"""
# Logseq: [[TTA/Components/Player_character/Models]]
PlayerCharacter Pydantic model and Neo4j node specification.

Issue: #283
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class PlayerCharacterStatus(StrEnum):
    """Lifecycle status of a player character."""

    DRAFT = "draft"  # Being created — not yet playable
    ACTIVE = "active"  # In an active session
    PAUSED = "paused"  # Session paused
    RETIRED = "retired"  # Player ended this character's story


class PlayerCharacter(BaseModel):
    """
    Represents the player's character in a TTA world.

    Created from WorldSeed + player preferences by PlayerCharacterService.
    Persisted as a Neo4j node with relationships to World and Location.

    Neo4j node: (PlayerCharacter {id, name, world_id, ...})
    Relationships:
      (PlayerCharacter)-[:IN_WORLD]->(World)
      (PlayerCharacter)-[:LOCATED_AT]->(Location)
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    world_id: str  # FK to WorldSeed.id / World Neo4j node
    background: str = ""  # Paragraph describing history
    traits: list[str] = Field(default_factory=list)  # e.g. ["curious", "cautious"]
    skills: list[str] = Field(default_factory=list)  # e.g. ["herbalism", "negotiation"]
    faction_eligibility: list[str] = Field(
        default_factory=list
    )  # world-specific factions
    starting_location: str = ""  # Location name/ID
    status: PlayerCharacterStatus = PlayerCharacterStatus.DRAFT
    player_id: str = ""  # Auth player ID
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_neo4j_properties(self) -> dict[str, Any]:
        """Serialize to a flat dict for Neo4j property storage."""
        return {
            "id": self.id,
            "name": self.name,
            "world_id": self.world_id,
            "background": self.background,
            "traits": self.traits,
            "skills": self.skills,
            "faction_eligibility": self.faction_eligibility,
            "starting_location": self.starting_location,
            "status": self.status.value,
            "player_id": self.player_id,
        }

    @classmethod
    def from_neo4j_properties(cls, props: dict[str, Any]) -> PlayerCharacter:
        """Deserialize from Neo4j property dict."""
        return cls(
            id=props["id"],
            name=props["name"],
            world_id=props["world_id"],
            background=props.get("background", ""),
            traits=props.get("traits", []),
            skills=props.get("skills", []),
            faction_eligibility=props.get("faction_eligibility", []),
            starting_location=props.get("starting_location", ""),
            status=PlayerCharacterStatus(props.get("status", "draft")),
            player_id=props.get("player_id", ""),
        )

    @property
    def character_sheet(self) -> dict[str, Any]:
        """Compact dict for passing to WBA/WorldContextBuilder."""
        return {
            "name": self.name,
            "background": self.background,
            "traits": self.traits,
            "skills": self.skills,
            "location": self.starting_location,
        }
