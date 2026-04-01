"""Tests for PlayerCharacter model and PlayerCharacterService.

Issues: #283, #284
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from src.components.player_character.models import PlayerCharacter, PlayerCharacterStatus
from src.components.player_character.service import (
    PlayerCharacterService,
    _build_world_description,
    _derive_faction_eligibility,
    _derive_skills,
)


# ── Model Tests ──────────────────────────────────────────────────────────────


class TestPlayerCharacterModel:
    def test_default_id_generated(self) -> None:
        pc = PlayerCharacter(name="Kira", world_id="w1")
        assert pc.id != ""
        assert len(pc.id) > 0

    def test_required_fields(self) -> None:
        pc = PlayerCharacter(name="Aryn", world_id="seed-42")
        assert pc.name == "Aryn"
        assert pc.world_id == "seed-42"
        # all other fields have defaults
        assert pc.background == ""
        assert pc.traits == []
        assert pc.skills == []
        assert pc.faction_eligibility == []
        assert pc.starting_location == ""
        assert pc.player_id == ""
        assert pc.metadata == {}

    def test_to_neo4j_properties(self) -> None:
        pc = PlayerCharacter(
            name="Kira",
            world_id="w1",
            background="A healer.",
            traits=["empathetic"],
            skills=["foraging"],
            faction_eligibility=["wanderers"],
            starting_location="forest edge",
            player_id="p-1",
            status=PlayerCharacterStatus.ACTIVE,
        )
        props = pc.to_neo4j_properties()
        assert props["name"] == "Kira"
        assert props["world_id"] == "w1"
        assert props["background"] == "A healer."
        assert props["traits"] == ["empathetic"]
        assert props["skills"] == ["foraging"]
        assert props["faction_eligibility"] == ["wanderers"]
        assert props["starting_location"] == "forest edge"
        assert props["player_id"] == "p-1"
        # status stored as string value
        assert props["status"] == "active"
        # id present
        assert "id" in props

    def test_from_neo4j_properties_roundtrip(self) -> None:
        original = PlayerCharacter(
            name="Elan",
            world_id="w2",
            background="A scholar.",
            traits=["curious", "careful"],
            skills=["reading", "translation"],
            faction_eligibility=["scholars"],
            starting_location="archive",
            player_id="p-2",
            status=PlayerCharacterStatus.PAUSED,
        )
        props = original.to_neo4j_properties()
        # inject id since to_neo4j includes it
        restored = PlayerCharacter.from_neo4j_properties(props)
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.world_id == original.world_id
        assert restored.background == original.background
        assert restored.traits == original.traits
        assert restored.skills == original.skills
        assert restored.faction_eligibility == original.faction_eligibility
        assert restored.starting_location == original.starting_location
        assert restored.player_id == original.player_id
        assert restored.status == PlayerCharacterStatus.PAUSED

    def test_character_sheet_property(self) -> None:
        pc = PlayerCharacter(
            name="Sable",
            world_id="w3",
            background="Grew up near the docks.",
            traits=["resourceful"],
            skills=["navigation"],
            starting_location="harbour district",
        )
        sheet = pc.character_sheet
        assert sheet["name"] == "Sable"
        assert sheet["background"] == "Grew up near the docks."
        assert sheet["traits"] == ["resourceful"]
        assert sheet["skills"] == ["navigation"]
        assert sheet["location"] == "harbour district"

    def test_status_defaults_to_draft(self) -> None:
        pc = PlayerCharacter(name="Test", world_id="w1")
        assert pc.status == PlayerCharacterStatus.DRAFT

    def test_name_min_length_validation(self) -> None:
        with pytest.raises(ValidationError):
            PlayerCharacter(name="", world_id="w1")

    def test_unique_ids_per_instance(self) -> None:
        pc1 = PlayerCharacter(name="Alpha", world_id="w1")
        pc2 = PlayerCharacter(name="Beta", world_id="w1")
        assert pc1.id != pc2.id

    def test_from_neo4j_defaults_on_missing_fields(self) -> None:
        minimal = {"id": "x1", "name": "Ghost", "world_id": "w9"}
        pc = PlayerCharacter.from_neo4j_properties(minimal)
        assert pc.background == ""
        assert pc.traits == []
        assert pc.status == PlayerCharacterStatus.DRAFT


# ── Skill Derivation Tests ────────────────────────────────────────────────────


class TestSkillDerivation:
    def test_magic_world_gives_arcane_skills(self) -> None:
        skills = _derive_skills({"power_source": "magic", "scale": "village"})
        assert "arcane reading" in skills
        assert "ritual preparation" in skills

    def test_technology_world_gives_engineering_skills(self) -> None:
        skills = _derive_skills({"power_source": "technology", "scale": "city"})
        assert "mechanical repair" in skills

    def test_nature_world_gives_foraging_skills(self) -> None:
        skills = _derive_skills({"power_source": "nature", "scale": "village"})
        assert "foraging" in skills

    def test_city_scale_bonus_skill(self) -> None:
        skills = _derive_skills({"power_source": "magic", "scale": "city"})
        assert "urban navigation" in skills

    def test_village_scale_bonus_skill(self) -> None:
        skills = _derive_skills({"power_source": "belief", "scale": "village"})
        assert "community trust" in skills

    def test_unknown_power_source_fallback(self) -> None:
        skills = _derive_skills({"power_source": "unknown_source", "scale": "village"})
        assert "observation" in skills or "adaptability" in skills

    def test_world_scale_key_also_accepted(self) -> None:
        # service stores both 'scale' and 'world_scale' in dicts
        skills = _derive_skills({"power_source": "nature", "world_scale": "region"})
        assert "geography" in skills

    def test_returns_three_skills(self) -> None:
        skills = _derive_skills({"power_source": "politics", "scale": "continent"})
        assert len(skills) == 3

    def test_politics_gives_negotiation(self) -> None:
        skills = _derive_skills({"power_source": "politics", "scale": "village"})
        assert "negotiation" in skills


# ── Faction Eligibility Tests ─────────────────────────────────────────────────


class TestFactionEligibility:
    def test_insider_gets_ruling_faction(self) -> None:
        factions = _derive_faction_eligibility({}, "insider")
        assert "ruling faction" in factions

    def test_outsider_gets_resistance(self) -> None:
        factions = _derive_faction_eligibility({}, "outsider")
        assert "resistance movements" in factions

    def test_observer_gets_scholars(self) -> None:
        factions = _derive_faction_eligibility({}, "observer")
        assert "scholars" in factions

    def test_ascending_gets_reform_movements(self) -> None:
        factions = _derive_faction_eligibility({}, "ascending")
        assert "reform movements" in factions

    def test_descending_gets_exile_communities(self) -> None:
        factions = _derive_faction_eligibility({}, "descending")
        assert "exile communities" in factions

    def test_unknown_position_fallback(self) -> None:
        factions = _derive_faction_eligibility({}, "unknown_position")
        assert factions == ["independent"]

    def test_case_insensitive(self) -> None:
        factions = _derive_faction_eligibility({}, "INSIDER")
        assert "ruling faction" in factions


# ── World Description Builder Tests ──────────────────────────────────────────


class TestWorldDescriptionBuilder:
    def test_all_fields_present(self) -> None:
        seed = {
            "tone": "getting_better",
            "power_source": "magic",
            "scale": "city",
            "player_position": "outsider",
            "world_tagline": "A city of whispered secrets.",
        }
        desc = _build_world_description(seed, {})
        assert "getting_better" in desc
        assert "magic" in desc
        assert "city" in desc
        assert "outsider" in desc
        assert "A city of whispered secrets." in desc

    def test_empty_seed_gives_fallback_string(self) -> None:
        desc = _build_world_description({}, {})
        assert desc == "A mysterious world of untold stories."

    def test_player_prefs_included(self) -> None:
        desc = _build_world_description(
            {"tone": "cyclical"},
            {"background_hint": "former soldier", "preferred_name": "Mira"},
        )
        assert "former soldier" in desc
        assert "Mira" in desc

    def test_world_scale_key_accepted(self) -> None:
        desc = _build_world_description({"world_scale": "continent"}, {})
        assert "continent" in desc


# ── Service Tests ─────────────────────────────────────────────────────────────


class TestPlayerCharacterService:
    @pytest.fixture
    def mock_llm(self):  # type: ignore[no-untyped-def]
        from unittest.mock import AsyncMock, MagicMock

        llm = MagicMock()
        llm.ainvoke = AsyncMock(
            return_value=MagicMock(
                content=json.dumps(
                    {
                        "name": "Kira Ashwood",
                        "background": "A healer from the northern forests.",
                        "traits": ["empathetic", "observant", "stubborn"],
                        "starting_location": "forest edge village",
                    }
                )
            )
        )
        return llm

    @pytest.fixture
    def sample_world_seed(self) -> dict:
        return {
            "id": "seed-123",
            "tone": "getting_better",
            "power_source": "nature",
            "world_scale": "village",
            "player_position": "outsider",
        }

    @pytest.mark.asyncio
    async def test_create_from_seed_dict(self, mock_llm, sample_world_seed) -> None:
        service = PlayerCharacterService(llm=mock_llm)
        pc = await service.create_from_seed(sample_world_seed)
        assert pc.name == "Kira Ashwood"
        assert pc.world_id == "seed-123"
        assert len(pc.skills) > 0
        assert len(pc.faction_eligibility) > 0
        assert pc.status == PlayerCharacterStatus.DRAFT

    @pytest.mark.asyncio
    async def test_create_from_seed_with_world_seed_model(self, mock_llm) -> None:
        from src.components.gameplay_loop.models.world_seed import (
            PlayerPosition,
            PowerSource,
            WorldSeed,
            WorldTone,
        )

        seed = WorldSeed(
            tone=WorldTone.GETTING_BETTER,
            power_source=PowerSource.NATURE,
            player_position=PlayerPosition.OUTSIDER,
            one_specific_detail="A great tree that blooms in winter",
        )
        service = PlayerCharacterService(llm=mock_llm)
        pc = await service.create_from_seed(seed)
        assert pc.name == "Kira Ashwood"
        # world_id derived from session_id for WorldSeed
        assert pc.world_id == seed.session_id

    @pytest.mark.asyncio
    async def test_llm_failure_uses_fallback(self, sample_world_seed) -> None:
        from unittest.mock import AsyncMock, MagicMock

        bad_llm = MagicMock()
        bad_llm.ainvoke = AsyncMock(side_effect=Exception("LLM down"))
        service = PlayerCharacterService(llm=bad_llm)
        pc = await service.create_from_seed(sample_world_seed)
        assert pc.name == "The Wanderer"

    @pytest.mark.asyncio
    async def test_player_prefs_passed_to_llm(
        self, mock_llm, sample_world_seed
    ) -> None:
        service = PlayerCharacterService(llm=mock_llm)
        await service.create_from_seed(
            sample_world_seed,
            player_prefs={"preferred_name": "Mira", "background_hint": "healer"},
        )
        call_args = mock_llm.ainvoke.call_args
        messages = call_args[0][0]
        # human message content should include the prefs
        human_msg = messages[1].content
        assert "Mira" in human_msg
        assert "healer" in human_msg

    @pytest.mark.asyncio
    async def test_player_id_attached(self, mock_llm, sample_world_seed) -> None:
        service = PlayerCharacterService(llm=mock_llm)
        pc = await service.create_from_seed(
            sample_world_seed, player_id="player-1"
        )
        assert pc.player_id == "player-1"

    @pytest.mark.asyncio
    async def test_background_from_llm_stored(
        self, mock_llm, sample_world_seed
    ) -> None:
        service = PlayerCharacterService(llm=mock_llm)
        pc = await service.create_from_seed(sample_world_seed)
        assert pc.background == "A healer from the northern forests."

    @pytest.mark.asyncio
    async def test_traits_from_llm_stored(
        self, mock_llm, sample_world_seed
    ) -> None:
        service = PlayerCharacterService(llm=mock_llm)
        pc = await service.create_from_seed(sample_world_seed)
        assert "empathetic" in pc.traits

    @pytest.mark.asyncio
    async def test_skills_are_rule_derived(
        self, mock_llm, sample_world_seed
    ) -> None:
        service = PlayerCharacterService(llm=mock_llm)
        pc = await service.create_from_seed(sample_world_seed)
        # nature + village → foraging + community trust
        assert "foraging" in pc.skills

    @pytest.mark.asyncio
    async def test_faction_eligibility_from_position(
        self, mock_llm, sample_world_seed
    ) -> None:
        service = PlayerCharacterService(llm=mock_llm)
        pc = await service.create_from_seed(sample_world_seed)
        # outsider → resistance movements
        assert "resistance movements" in pc.faction_eligibility

    @pytest.mark.asyncio
    async def test_character_sheet_usable_after_creation(
        self, mock_llm, sample_world_seed
    ) -> None:
        service = PlayerCharacterService(llm=mock_llm)
        pc = await service.create_from_seed(sample_world_seed)
        sheet = pc.character_sheet
        assert sheet["name"] == "Kira Ashwood"
        assert "location" in sheet
