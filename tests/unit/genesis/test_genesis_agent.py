"""
Tests for the Genesis Agent — seed extraction, guide generation, and orchestration.

All LLM calls are mocked via AsyncMock so tests run offline and fast.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from src.components.genesis.agent import (
    AgentResponse,
    GenesisAgent,
    _check_first_light_response,
    _is_surprise_request,
    _should_transition,
)
from src.components.genesis.guide_generator import _derive_structural, derive_guide_character
from src.components.genesis.seed_extractor import SeedExtractor, _validate_fields
from src.components.genesis.session_state import Act, GenesisSessionState


# ── Fixtures ──────────────────────────────────────────────────────────────────


def _make_llm(response: str = "A voice in the dark...") -> Any:
    """Return a mock LLM that always responds with `response`."""
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=AIMessage(content=response))
    return llm


def _fresh_state(session_id: str = "test-session") -> GenesisSessionState:
    return GenesisSessionState(session_id=session_id)


# ── SeedExtractor ─────────────────────────────────────────────────────────────


class TestSeedExtractor:
    @pytest.mark.asyncio
    async def test_extracts_clean_fields(self) -> None:
        llm = _make_llm('{"tone": "getting_worse", "power_source": "magic"}')
        extractor = SeedExtractor(llm=llm)
        result = await extractor.extract("A dying world of wizards", {}, Act.BUILDING_WORLD)
        assert result["tone"] == "getting_worse"
        assert result["power_source"] == "magic"

    @pytest.mark.asyncio
    async def test_skips_already_established_fields(self) -> None:
        llm = _make_llm('{"tone": "getting_better", "power_source": "magic"}')
        extractor = SeedExtractor(llm=llm)
        result = await extractor.extract(
            "A world of ancient magic",
            {"tone": "getting_worse"},  # already set
            Act.BUILDING_WORLD,
        )
        assert "tone" not in result  # must NOT overwrite
        assert result.get("power_source") == "magic"

    @pytest.mark.asyncio
    async def test_returns_empty_on_vague_input(self) -> None:
        llm = _make_llm("{}")
        extractor = SeedExtractor(llm=llm)
        result = await extractor.extract("I don't know", {}, Act.BUILDING_WORLD)
        assert result == {}

    @pytest.mark.asyncio
    async def test_handles_llm_failure_gracefully(self) -> None:
        llm = MagicMock()
        llm.ainvoke = AsyncMock(side_effect=Exception("network error"))
        extractor = SeedExtractor(llm=llm)
        # Should NOT raise — fallback returns {}
        result = await extractor.extract("Some input", {}, Act.BUILDING_WORLD)
        assert result == {}

    @pytest.mark.asyncio
    async def test_handles_malformed_json(self) -> None:
        llm = _make_llm("not json at all")
        extractor = SeedExtractor(llm=llm)
        result = await extractor.extract("Some input", {}, Act.BUILDING_WORLD)
        assert result == {}

    @pytest.mark.asyncio
    async def test_generates_surprise_seed(self) -> None:
        surprise_data = (
            '{"tone":"getting_worse","power_source":"magic","player_position":"outsider",'
            '"one_specific_detail":"a burning library","scale":"city",'
            '"era_tech_level":"renaissance","magic_presence":"rare"}'
        )
        llm = _make_llm(surprise_data)
        extractor = SeedExtractor(llm=llm)
        result = await extractor.generate_surprise_seed()
        assert result["tone"] == "getting_worse"
        assert result["one_specific_detail"] == "a burning library"

    def test_validate_fields_drops_invalid_enums(self) -> None:
        raw = {
            "tone": "getting_worse",
            "power_source": "INVALID_VALUE",
            "character_name": "Aelith",
        }
        clean = _validate_fields(raw)
        assert "tone" in clean
        assert "power_source" not in clean
        assert clean["character_name"] == "Aelith"

    def test_validate_fields_strips_whitespace(self) -> None:
        raw = {"character_name": "  Aelith  ", "character_trait": "  skilled thief  "}
        clean = _validate_fields(raw)
        assert clean["character_name"] == "Aelith"
        assert clean["character_trait"] == "skilled thief"


# ── GuideGenerator ────────────────────────────────────────────────────────────


class TestGuideGenerator:
    def test_derive_structural_fantasy(self) -> None:
        fields = {
            "tone": "getting_worse",
            "power_source": "magic",
            "player_position": "outsider",
            "era_tech_level": "medieval",
            "magic_presence": "common",
        }
        result = _derive_structural(fields)
        assert result["entity_type"] == "ancient mage"
        assert result["social_position"] == "keeper of arcane secrets"
        assert result["relationship_to_player"] == "fellow wanderer"
        assert "grave" in result["speech_register"]

    def test_derive_structural_cyberpunk(self) -> None:
        fields = {
            "tone": "getting_worse",
            "power_source": "technology",
            "player_position": "outsider",
            "era_tech_level": "information",
            "magic_presence": "none",
        }
        result = _derive_structural(fields)
        assert result["entity_type"] == "AI construct"
        assert result["social_position"] == "architect of systems"

    def test_derive_structural_defaults_gracefully(self) -> None:
        result = _derive_structural({})
        assert result["entity_type"] is not None
        assert result["social_position"] is not None

    @pytest.mark.asyncio
    async def test_derive_guide_character_returns_object(self) -> None:
        llm = _make_llm('{"name": "Veyra", "intro_line": "You arrived earlier than expected."}')
        fields = {
            "tone": "getting_worse",
            "power_source": "magic",
            "player_position": "outsider",
            "era_tech_level": "medieval",
            "magic_presence": "common",
        }
        guide = await derive_guide_character(fields, llm=llm)
        assert guide.name == "Veyra"
        assert guide.intro_line == "You arrived earlier than expected."
        assert guide.entity_type is not None

    @pytest.mark.asyncio
    async def test_guide_uses_fallback_on_llm_failure(self) -> None:
        llm = MagicMock()
        llm.ainvoke = AsyncMock(side_effect=RuntimeError("LLM down"))
        guide = await derive_guide_character({}, llm=llm)
        # Fallback name is "Meridian"
        assert guide.name == "Meridian"
        assert len(guide.intro_line) > 10


# ── Transition logic ──────────────────────────────────────────────────────────


class TestTransitionLogic:
    def _state_with_turns(self, act: Act, n_turns: int) -> GenesisSessionState:
        state = GenesisSessionState(session_id="t")
        state.act = act
        for i in range(n_turns):
            state.record_turn(f"input {i}", f"response {i}")
        return state

    def test_void_advances_after_three_turns(self) -> None:
        state = self._state_with_turns(Act.VOID, 2)  # 2 recorded + 1 in-flight = 3
        result = _should_transition(state, {})
        assert result == Act.BUILDING_WORLD

    def test_void_does_not_advance_too_early(self) -> None:
        state = self._state_with_turns(Act.VOID, 1)  # 1 recorded + 1 in-flight = 2 < 3
        result = _should_transition(state, {})
        assert result is None

    def test_building_world_advances_with_complete_fields(self) -> None:
        state = self._state_with_turns(Act.BUILDING_WORLD, 2)  # 2 recorded + 1 = 3 min
        preview = {
            "tone": "getting_worse",
            "power_source": "magic",
            "player_position": "outsider",
            "one_specific_detail": "a tower that rings at midnight",
        }
        result = _should_transition(state, preview)
        assert result == Act.SLIP_PHASE

    def test_building_world_does_not_advance_without_all_fields(self) -> None:
        state = self._state_with_turns(Act.BUILDING_WORLD, 5)
        preview = {"tone": "getting_worse"}  # missing 3 required fields
        result = _should_transition(state, preview)
        assert result is None

    def test_building_character_advances_when_char_fields_complete(self) -> None:
        state = self._state_with_turns(Act.BUILDING_CHARACTER, 1)  # 1 recorded + 1 = 2
        preview = {"character_name": "Aelith", "character_motivation": "curiosity"}
        result = _should_transition(state, preview)
        assert result == Act.FIRST_LIGHT

    def test_first_light_advances_only_when_confirmed(self) -> None:
        state = GenesisSessionState(session_id="t")
        state.act = Act.FIRST_LIGHT
        state.first_light_confirmed = False
        assert _should_transition(state, {}) is None
        state.first_light_confirmed = True
        assert _should_transition(state, {}) == Act.THE_BECOMING

    def test_the_becoming_advances_when_guide_introduced(self) -> None:
        state = GenesisSessionState(session_id="t")
        state.act = Act.THE_BECOMING
        state.guide_introduced = False
        assert _should_transition(state, {}) is None
        state.guide_introduced = True
        assert _should_transition(state, {}) == Act.THE_THRESHOLD

    def test_the_threshold_advances_after_five_turns(self) -> None:
        state = self._state_with_turns(Act.THE_THRESHOLD, 4)  # 4 recorded + 1 = 5
        assert _should_transition(state, {}) == Act.SESSION_BEGUN


# ── Helper functions ──────────────────────────────────────────────────────────


class TestHelpers:
    def test_surprise_request_detection(self) -> None:
        assert _is_surprise_request("surprise me")
        assert _is_surprise_request("You decide, I don't mind")
        assert _is_surprise_request("It's up to you")
        assert not _is_surprise_request("I want a dark world")

    def test_first_light_confirm_detect(self) -> None:
        assert _check_first_light_response("Yes, that's perfect") == "confirm"
        assert _check_first_light_response("Yeah I love it") == "confirm"

    def test_first_light_redirect_detect(self) -> None:
        assert _check_first_light_response("No, more like a desert") == "redirect"
        assert _check_first_light_response("Actually change the climate") == "redirect"

    def test_first_light_neutral(self) -> None:
        assert _check_first_light_response("Tell me more") is None


# ── GenesisAgent full flow ────────────────────────────────────────────────────


class TestGenesisAgent:
    def _make_agent(
        self,
        narrator_response: str = "Darkness stretches in every direction...",
        extractor_json: str = "{}",
    ) -> GenesisAgent:
        narrator_llm = _make_llm(narrator_response)
        extractor_llm = _make_llm(extractor_json)
        guide_llm = _make_llm('{"name":"Veyra","intro_line":"Come, there is little time."}')
        return GenesisAgent(
            narrator_llm=narrator_llm,
            extractor_llm=extractor_llm,
            guide_llm=guide_llm,
        )

    @pytest.mark.asyncio
    async def test_returns_agent_response(self) -> None:
        agent = self._make_agent()
        state = _fresh_state()
        response = await agent.respond(state, "Hello")
        assert isinstance(response, AgentResponse)
        assert len(response.text) > 0
        assert response.act == Act.VOID  # not enough turns to advance

    @pytest.mark.asyncio
    async def test_records_turn_in_state(self) -> None:
        agent = self._make_agent()
        state = _fresh_state()
        await agent.respond(state, "Hello world")
        assert state.total_turns == 1
        assert state.turns[0].player_input == "Hello world"

    @pytest.mark.asyncio
    async def test_merges_extracted_fields(self) -> None:
        agent = self._make_agent(extractor_json='{"tone":"getting_worse"}')
        state = _fresh_state()
        state.act = Act.BUILDING_WORLD
        response = await agent.respond(state, "This world is dying")
        assert response.new_fields.get("tone") == "getting_worse"
        assert state.seed_fields.get("tone") == "getting_worse"

    @pytest.mark.asyncio
    async def test_act_advances_in_void(self) -> None:
        agent = self._make_agent()
        state = _fresh_state()
        # Need 3 turns in VOID to advance
        for i in range(3):
            response = await agent.respond(state, f"turn {i}")
        assert response.act == Act.BUILDING_WORLD
        assert response.act_changed is True

    @pytest.mark.asyncio
    async def test_surprise_me_sets_flag(self) -> None:
        extractor_llm = _make_llm(
            '{"tone":"getting_worse","power_source":"magic",'
            '"player_position":"outsider","one_specific_detail":"a tower"}'
        )
        agent = self._make_agent()
        agent._extractor = SeedExtractor(llm=extractor_llm)
        state = _fresh_state()
        await agent.respond(state, "surprise me")
        assert state.surprise_me is True

    @pytest.mark.asyncio
    async def test_is_not_complete_before_session_begun(self) -> None:
        agent = self._make_agent()
        state = _fresh_state()
        response = await agent.respond(state, "Hello")
        assert response.is_complete is False
        assert response.world_seed is None

    @pytest.mark.asyncio
    async def test_guide_character_generated_in_becoming(self) -> None:
        guide_llm = _make_llm('{"name":"Veyra","intro_line":"You were not expected."}')
        agent = self._make_agent()
        agent._guide_llm = guide_llm

        state = _fresh_state()
        state.act = Act.THE_BECOMING
        state.seed_fields = {
            "tone": "getting_worse",
            "power_source": "magic",
            "player_position": "outsider",
            "one_specific_detail": "a tower",
            "era_tech_level": "medieval",
            "magic_presence": "common",
        }

        response = await agent.respond(state, "I'm ready")
        assert response.guide is not None
        assert response.guide.name == "Veyra"

    @pytest.mark.asyncio
    async def test_narrator_fallback_on_llm_failure(self) -> None:
        """Agent must never raise — it returns the safe fallback message."""
        narrator_llm = MagicMock()
        narrator_llm.ainvoke = AsyncMock(side_effect=Exception("LLM down"))
        extractor_llm = _make_llm("{}")
        guide_llm = _make_llm('{"name":"X","intro_line":"..."}')

        agent = GenesisAgent(
            narrator_llm=narrator_llm,
            extractor_llm=extractor_llm,
            guide_llm=guide_llm,
        )
        state = _fresh_state()
        response = await agent.respond(state, "Hello")
        assert isinstance(response.text, str)
        assert len(response.text) > 0  # fallback message delivered

    @pytest.mark.asyncio
    async def test_reset_clears_guide(self) -> None:
        agent = self._make_agent()
        agent._guide = MagicMock()  # simulate guide already generated
        await agent.reset()
        assert agent._guide is None
