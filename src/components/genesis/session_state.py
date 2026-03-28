"""
Genesis Session state machine.

The Genesis Session is a five-act conversation that assembles the WorldSeed.
It begins in a featureless void and ends with the player already inside their world.

Acts:
  VOID              — narrator in the void, world-building questions
  BUILDING_WORLD    — core world questions, narrator comfortable and slightly stalling
  SLIP_PHASE        — narrator makes 1-2 'slips', character questions begin
  BUILDING_CHARACTER — character questions, void gaining texture
  FIRST_LIGHT       — first prose paragraph delivered, narrator faces transformation
  THE_BECOMING      — narrator takes in-world form, comedy of having existence
  THE_THRESHOLD     — character approaches entry point, guide peels off
  SESSION_BEGUN     — WorldSeed emitted, world generators fire

See: docs/design/genesis-session.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.components.gameplay_loop.models.world_seed import GuideCharacter


class Act(StrEnum):
    """The five acts of the Genesis Session plus terminal states."""

    VOID = "void"
    BUILDING_WORLD = "building_world"
    SLIP_PHASE = "slip_phase"
    BUILDING_CHARACTER = "building_character"
    FIRST_LIGHT = "first_light"
    THE_BECOMING = "the_becoming"
    THE_THRESHOLD = "the_threshold"
    SESSION_BEGUN = "session_begun"


# Turn count targets per act (minimum, standard, deep/slow)
ACT_TURN_TARGETS: dict[Act, tuple[int, int, int]] = {
    Act.VOID: (1, 3, 10),  # (min, standard, soft_max)
    Act.BUILDING_WORLD: (3, 6, 10),
    Act.SLIP_PHASE: (1, 2, 4),  # short — transition act
    Act.BUILDING_CHARACTER: (3, 6, 10),
    Act.FIRST_LIGHT: (2, 3, 5),
    Act.THE_BECOMING: (2, 4, 6),
    Act.THE_THRESHOLD: (3, 5, 8),
    Act.SESSION_BEGUN: (0, 0, 0),
}

# Valid act transitions
ACT_TRANSITIONS: dict[Act, list[Act]] = {
    Act.VOID: [Act.BUILDING_WORLD],
    Act.BUILDING_WORLD: [Act.SLIP_PHASE],
    Act.SLIP_PHASE: [Act.BUILDING_CHARACTER],
    Act.BUILDING_CHARACTER: [Act.FIRST_LIGHT],
    Act.FIRST_LIGHT: [
        Act.THE_BECOMING,
        Act.BUILDING_CHARACTER,
    ],  # can loop back if player redirects
    Act.THE_BECOMING: [Act.THE_THRESHOLD],
    Act.THE_THRESHOLD: [Act.SESSION_BEGUN],
    Act.SESSION_BEGUN: [],
}


@dataclass
class Turn:
    """A single exchange in the Genesis Session."""

    turn_number: int
    act: Act
    player_input: str
    agent_response: str
    seed_fields_established: list[str] = field(default_factory=list)
    is_slip: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class GenesisSessionState:
    """
    Mutable state of an in-progress Genesis Session.

    Holds the partial WorldSeed, turn history, current act,
    and any context needed for the agent to generate its next response.
    """

    session_id: str
    act: Act = Act.VOID
    turns: list[Turn] = field(default_factory=list)

    # Partial seed fields accumulated during the session
    # These mirror WorldSeed fields but are stored loosely until finalisation
    seed_fields: dict[str, Any] = field(default_factory=dict)

    # How many slips have been delivered (max 2)
    slips_delivered: int = 0

    # Whether the player has confirmed the first-light paragraph
    first_light_confirmed: bool = False

    # Whether the guide character has been introduced
    guide_introduced: bool = False

    # The derived guide character (stored so it doesn't need re-generation each request)
    guide_character: GuideCharacter | None = None

    # Flag: player asked to be surprised (agent makes seed choices)
    surprise_me: bool = False

    # The first-light prose paragraph (stored so it can be re-sent if player redirects)
    first_light_paragraph: str | None = None

    # Any cultural references the player made (for reference extraction)
    cultural_references: list[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # ── Computed properties ───────────────────────────────────────────────

    @property
    def total_turns(self) -> int:
        return len(self.turns)

    @property
    def turns_in_current_act(self) -> int:
        return sum(1 for t in self.turns if t.act == self.act)

    @property
    def minimum_viable_seed_complete(self) -> bool:
        """True when the 4 required WorldSeed fields are established."""
        required = {"tone", "power_source", "player_position", "one_specific_detail"}
        return required.issubset(self.seed_fields.keys())

    @property
    def character_fields_complete(self) -> bool:
        """True when enough character data exists to write them into the world."""
        return bool(
            self.seed_fields.get("character_name")
            and self.seed_fields.get("character_motivation")
        )

    @property
    def can_slip(self) -> bool:
        """True when a slip is appropriate and we haven't used both."""
        return self.slips_delivered < 2 and self.act in (
            Act.SLIP_PHASE,
            Act.BUILDING_CHARACTER,
        )

    # ── Transitions ──────────────────────────────────────────────────────

    def transition_to(self, next_act: Act) -> None:
        """Advance to the next act, validating the transition is legal."""
        valid = ACT_TRANSITIONS.get(self.act, [])
        if next_act not in valid:
            raise ValueError(
                f"Invalid act transition: {self.act} → {next_act}. "
                f"Valid transitions from {self.act}: {valid}"
            )
        self.act = next_act
        self.updated_at = datetime.now(UTC)

    def record_turn(
        self,
        player_input: str,
        agent_response: str,
        new_fields: dict[str, Any] | None = None,
        is_slip: bool = False,
    ) -> Turn:
        """Record a completed turn and update established seed fields."""
        if new_fields:
            self.seed_fields.update(new_fields)
        if is_slip:
            self.slips_delivered += 1

        turn = Turn(
            turn_number=self.total_turns + 1,
            act=self.act,
            player_input=player_input,
            agent_response=agent_response,
            seed_fields_established=list(new_fields.keys()) if new_fields else [],
            is_slip=is_slip,
        )
        self.turns.append(turn)
        self.updated_at = datetime.now(UTC)
        return turn

    def should_advance(self) -> bool:
        """
        Heuristic: should the session advance to the next act?

        The agent makes this call based on seed completeness and turn count,
        not on a rigid counter. This method provides guidance.
        """
        turns_here = self.turns_in_current_act
        _, standard, _ = ACT_TURN_TARGETS.get(self.act, (0, 0, 0))

        if self.act == Act.BUILDING_WORLD:
            # Advance when minimum viable seed is complete AND we've had
            # at least the minimum turns
            min_turns, _, _ = ACT_TURN_TARGETS[Act.BUILDING_WORLD]
            return self.minimum_viable_seed_complete and turns_here >= min_turns

        if self.act == Act.BUILDING_CHARACTER:
            return self.character_fields_complete and turns_here >= 2

        if self.act == Act.FIRST_LIGHT:
            return self.first_light_confirmed

        if self.act == Act.THE_BECOMING:
            return self.guide_introduced

        # Default: advance after standard turn count
        return turns_here >= standard
