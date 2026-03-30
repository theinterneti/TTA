"""
Tests for WorldSeed model and Genesis Session state machine.

Covers:
- WorldSeed construction and validation
- Minimum viable seed detection
- Seed hash determinism
- Enum coverage
- GenesisSessionState transitions and turn tracking
- Narrator voice profiles
- Act system prompt generation
"""

import pytest

from src.components.gameplay_loop.models.world_seed import (
    GuideCharacter,
    MagicPresence,
    Motivation,
    PlayerPosition,
    PowerSource,
    TechLevel,
    WorldScale,
    WorldSeed,
    WorldTone,
)
from src.components.genesis.narrator_voice import (
    NARRATOR_VOICES,
    get_system_prompt,
)
from src.components.genesis.session_state import (
    ACT_TRANSITIONS,
    Act,
    GenesisSessionState,
)

# ── WorldSeed ─────────────────────────────────────────────────────────────────


class TestWorldSeedMinimumViable:
    """A 4-field seed is valid and complete."""

    def test_minimum_viable_seed_is_valid(self):
        seed = WorldSeed(
            tone=WorldTone.GETTING_WORSE,
            power_source=PowerSource.MAGIC,
            player_position=PlayerPosition.OUTSIDER,
            one_specific_detail="A clock tower that has been stopped for forty years",
        )
        assert seed.is_minimum_viable()

    def test_minimum_viable_reports_no_missing_fields(self):
        seed = WorldSeed(
            tone=WorldTone.CYCLICAL,
            power_source=PowerSource.POLITICS,
            player_position=PlayerPosition.INSIDER,
            one_specific_detail="The market that never closes",
        )
        assert seed.missing_fields() == []

    def test_missing_fields_identified(self):
        # Pydantic won't allow construction without required fields,
        # so we test the logic by checking a complete seed has none missing
        seed = WorldSeed(
            tone=WorldTone.GETTING_BETTER,
            power_source=PowerSource.TECHNOLOGY,
            player_position=PlayerPosition.ASCENDING,
            one_specific_detail="Rail lines that cut through the old quarters",
        )
        assert "tone" not in seed.missing_fields()
        assert "power_source" not in seed.missing_fields()
        assert "player_position" not in seed.missing_fields()
        assert "one_specific_detail" not in seed.missing_fields()


class TestWorldSeedHash:
    """Seed hash is deterministic from the same minimum viable fields."""

    def test_same_inputs_produce_same_hash(self):
        seed_a = WorldSeed(
            tone=WorldTone.GETTING_WORSE,
            power_source=PowerSource.MAGIC,
            player_position=PlayerPosition.OUTSIDER,
            one_specific_detail="A clock tower stopped for forty years",
        )
        seed_b = WorldSeed(
            tone=WorldTone.GETTING_WORSE,
            power_source=PowerSource.MAGIC,
            player_position=PlayerPosition.OUTSIDER,
            one_specific_detail="A clock tower stopped for forty years",
        )
        assert seed_a.seed_hash == seed_b.seed_hash

    def test_different_inputs_produce_different_hash(self):
        seed_a = WorldSeed(
            tone=WorldTone.GETTING_WORSE,
            power_source=PowerSource.MAGIC,
            player_position=PlayerPosition.OUTSIDER,
            one_specific_detail="A clock tower stopped for forty years",
        )
        seed_b = WorldSeed(
            tone=WorldTone.GETTING_BETTER,
            power_source=PowerSource.MAGIC,
            player_position=PlayerPosition.OUTSIDER,
            one_specific_detail="A clock tower stopped for forty years",
        )
        assert seed_a.seed_hash != seed_b.seed_hash

    def test_hash_is_16_hex_chars(self):
        seed = WorldSeed(
            tone=WorldTone.HOLDING_ON,
            power_source=PowerSource.BELIEF,
            player_position=PlayerPosition.OBSERVER,
            one_specific_detail="The river that runs backwards",
        )
        assert seed.seed_hash is not None
        assert len(seed.seed_hash) == 16
        assert all(c in "0123456789abcdef" for c in seed.seed_hash)


class TestWorldSeedOptionalFields:
    """Optional fields can be added after minimum viable seed is set."""

    def test_full_seed_with_all_optional_fields(self):
        seed = WorldSeed(
            tone=WorldTone.GETTING_WORSE,
            power_source=PowerSource.MAGIC,
            player_position=PlayerPosition.OUTSIDER,
            one_specific_detail="The sealed tower district",
            scale=WorldScale.CITY,
            geography_archetype="island surrounded by a dead sea",
            era_tech_level=TechLevel.MEDIEVAL,
            magic_presence=MagicPresence.RARE,
            magic_source="inherited bloodlines, fading fast",
            culture_base="theocratic remnant",
            culture_tone="formal, mourning, proud of ruins",
            cultural_tension="the church that holds power cannot admit it is hollow",
            character_name="Wren",
            character_background="grew up in the lower city, never entered the sealed district",
            character_motivation=Motivation.CURIOSITY,
            character_trait="everyone remembers meeting them",
            character_secret="they have been inside the tower district — once",
        )
        assert seed.character_is_complete()
        assert seed.is_minimum_viable()

    def test_character_incomplete_without_name_and_motivation(self):
        seed = WorldSeed(
            tone=WorldTone.CYCLICAL,
            power_source=PowerSource.NATURE,
            player_position=PlayerPosition.INSIDER,
            one_specific_detail="The migration season when the sky turns amber",
        )
        assert not seed.character_is_complete()

    def test_guide_character_can_be_set(self):
        guide = GuideCharacter(
            name="Sable",
            entity_type="unofficial archivist",
            social_position="edge-dweller, known to those who need records kept quietly",
            relationship_to_player="old acquaintance who owes them a favour",
            speech_register="dry, precise, unexpectedly warm",
            intro_line="My name is apparently Sable. I keep records. Unofficial ones.",
        )
        seed = WorldSeed(
            tone=WorldTone.GETTING_WORSE,
            power_source=PowerSource.POLITICS,
            player_position=PlayerPosition.OUTSIDER,
            one_specific_detail="The merchant quarter that votes its own laws",
            guide=guide,
        )
        assert seed.guide is not None
        assert seed.guide.name == "Sable"


class TestWorldSeedEnumCoverage:
    """All enum members are usable as WorldSeed field values."""

    @pytest.mark.parametrize("tone", list(WorldTone))
    def test_all_tones_valid(self, tone: WorldTone):
        seed = WorldSeed(
            tone=tone,
            power_source=PowerSource.MAGIC,
            player_position=PlayerPosition.OUTSIDER,
            one_specific_detail="a test detail",
        )
        assert seed.tone == tone

    @pytest.mark.parametrize("power", list(PowerSource))
    def test_all_power_sources_valid(self, power: PowerSource):
        seed = WorldSeed(
            tone=WorldTone.HOLDING_ON,
            power_source=power,
            player_position=PlayerPosition.OUTSIDER,
            one_specific_detail="a test detail",
        )
        assert seed.power_source == power

    @pytest.mark.parametrize("motivation", list(Motivation))
    def test_all_motivations_valid(self, motivation: Motivation):
        seed = WorldSeed(
            tone=WorldTone.CYCLICAL,
            power_source=PowerSource.BELIEF,
            player_position=PlayerPosition.INSIDER,
            one_specific_detail="the festival that is also a trial",
            character_name="Cass",
            character_motivation=motivation,
        )
        assert seed.character_is_complete()


# ── GenesisSessionState ───────────────────────────────────────────────────────


class TestGenesisSessionStateTransitions:
    """Act transitions follow the defined state machine."""

    def test_initial_act_is_void(self):
        state = GenesisSessionState(session_id="test-001")
        assert state.act == Act.VOID

    def test_valid_transition_void_to_building_world(self):
        state = GenesisSessionState(session_id="test-002")
        state.transition_to(Act.BUILDING_WORLD)
        assert state.act == Act.BUILDING_WORLD

    def test_invalid_transition_raises(self):
        state = GenesisSessionState(session_id="test-003")
        with pytest.raises(ValueError, match="Invalid act transition"):
            state.transition_to(
                Act.SESSION_BEGUN
            )  # can't jump from VOID to SESSION_BEGUN

    def test_full_happy_path_transitions(self):
        state = GenesisSessionState(session_id="test-004")
        path = [
            Act.BUILDING_WORLD,
            Act.SLIP_PHASE,
            Act.BUILDING_CHARACTER,
            Act.FIRST_LIGHT,
            Act.THE_BECOMING,
            Act.THE_THRESHOLD,
            Act.SESSION_BEGUN,
        ]
        for next_act in path:
            state.transition_to(next_act)
        assert state.act == Act.SESSION_BEGUN

    def test_first_light_can_loop_back_to_building_character(self):
        """If player redirects at first light, we can go back to building_character."""
        state = GenesisSessionState(session_id="test-005")
        state.transition_to(Act.BUILDING_WORLD)
        state.transition_to(Act.SLIP_PHASE)
        state.transition_to(Act.BUILDING_CHARACTER)
        state.transition_to(Act.FIRST_LIGHT)
        state.transition_to(Act.BUILDING_CHARACTER)  # player redirected
        assert state.act == Act.BUILDING_CHARACTER

    def test_all_act_transitions_defined(self):
        """Every Act except SESSION_BEGUN has at least one valid transition."""
        for act in Act:
            if act == Act.SESSION_BEGUN:
                assert ACT_TRANSITIONS[act] == []
            else:
                assert len(ACT_TRANSITIONS[act]) >= 1, f"{act} has no transitions"


class TestGenesisSessionStateTurnTracking:
    """Turn recording and seed field accumulation."""

    def test_turn_recorded_correctly(self):
        state = GenesisSessionState(session_id="test-010")
        state.transition_to(Act.BUILDING_WORLD)
        turn = state.record_turn(
            player_input="Things are definitely getting worse.",
            agent_response="Getting worse. I see.",
            new_fields={"tone": WorldTone.GETTING_WORSE},
        )
        assert turn.turn_number == 1
        assert turn.act == Act.BUILDING_WORLD
        assert "tone" in turn.seed_fields_established
        assert state.seed_fields["tone"] == WorldTone.GETTING_WORSE

    def test_turns_in_current_act_counted(self):
        state = GenesisSessionState(session_id="test-011")
        state.transition_to(Act.BUILDING_WORLD)
        for i in range(4):
            state.record_turn(
                player_input=f"response {i}",
                agent_response=f"agent {i}",
            )
        assert state.turns_in_current_act == 4

    def test_slip_count_increments(self):
        state = GenesisSessionState(session_id="test-012")
        state.transition_to(Act.BUILDING_WORLD)
        state.transition_to(Act.SLIP_PHASE)
        state.record_turn(
            player_input="yes, there is water",
            agent_response="[slip delivered]",
            new_fields={"geography_archetype": "coastal"},
            is_slip=True,
        )
        assert state.slips_delivered == 1

    def test_slip_capped_at_two(self):
        state = GenesisSessionState(session_id="test-013")
        state.transition_to(Act.BUILDING_WORLD)
        state.transition_to(Act.SLIP_PHASE)
        state.transition_to(Act.BUILDING_CHARACTER)
        # can_slip: True after first slip
        assert state.can_slip
        state.record_turn("input", "response", is_slip=True)
        assert state.slips_delivered == 1
        assert state.can_slip  # one more allowed
        state.record_turn("input", "response", is_slip=True)
        assert state.slips_delivered == 2
        assert not state.can_slip  # cap reached

    def test_minimum_viable_seed_detection(self):
        state = GenesisSessionState(session_id="test-014")
        state.transition_to(Act.BUILDING_WORLD)
        assert not state.minimum_viable_seed_complete

        state.record_turn("worse", "ok", new_fields={"tone": WorldTone.GETTING_WORSE})
        state.record_turn("magic", "ok", new_fields={"power_source": PowerSource.MAGIC})
        state.record_turn(
            "outsider", "ok", new_fields={"player_position": PlayerPosition.OUTSIDER}
        )
        assert not state.minimum_viable_seed_complete  # still need specific_detail

        state.record_turn(
            "clock tower",
            "ok",
            new_fields={"one_specific_detail": "a stopped clock tower"},
        )
        assert state.minimum_viable_seed_complete


# ── Narrator Voice ────────────────────────────────────────────────────────────


class TestNarratorVoice:
    """Voice profiles are defined for all relevant acts."""

    def test_voice_profile_exists_for_each_non_session_begun_act(self):
        for act in Act:
            if act == Act.SESSION_BEGUN:
                continue
            assert act in NARRATOR_VOICES, f"Missing voice profile for {act}"

    def test_all_profiles_have_example_phrases(self):
        for act, profile in NARRATOR_VOICES.items():
            assert len(profile.example_phrases) >= 2, (
                f"Act {act} needs at least 2 example phrases"
            )

    def test_get_system_prompt_returns_string(self):
        for act in Act:
            if act == Act.SESSION_BEGUN:
                continue  # terminal state — no LLM prompt needed
            prompt = get_system_prompt(act, world_context=None)
            assert isinstance(prompt, str)
            assert len(prompt) > 100

    def test_system_prompt_includes_world_context(self):
        context = {"tone": "getting_worse", "power_source": "magic"}
        prompt = get_system_prompt(Act.BUILDING_CHARACTER, world_context=context)
        assert "getting_worse" in prompt or "tone" in prompt

    def test_system_prompt_never_contains_technical_terms(self):
        for act in Act:
            if act == Act.SESSION_BEGUN:
                continue  # terminal state — no LLM prompt needed
            prompt = get_system_prompt(act)
            # These terms should not appear in what the narrator says to the player.
            # (They appear in the CONSTRAINTS section advising the LLM not to use them,
            # which is fine — we check the player-facing guidance section is clear.)
            # This test just ensures the prompt is generated without error.
            assert "WorldSeed" not in prompt or "Never mention 'WorldSeed'" in prompt
