"""
Unit tests for src/player_experience/services/default_character_world_service.py.

Covers DefaultCharacterWorldService.initialize_default_character_and_world:
- player already has characters → (None, None, None)
- character creation fails → (None, None, None)
- world not found → (char_id, None, None)
- full success → (char_id, DEFAULT_WORLD_ID, session_id)
- unexpected exception during init → (None, None, None)

And private helpers:
- _create_default_character: success and exception paths
- _create_initial_session: always returns a UUID string
"""

from __future__ import annotations

from unittest.mock import MagicMock

from src.player_experience.services.default_character_world_service import (
    DefaultCharacterWorldService,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_service(
    *,
    player_characters=None,
    create_character_result=None,
    world_details=None,
) -> DefaultCharacterWorldService:
    """Build a service with fully mocked managers."""
    char_manager = MagicMock()
    world_manager = MagicMock()

    # Default: new player (no existing characters)
    char_manager.get_player_characters.return_value = player_characters if player_characters is not None else []

    # Default: character creation succeeds
    if create_character_result is None:
        char = MagicMock()
        char.character_id = "char-default"
        char_manager.create_character.return_value = char
    else:
        char_manager.create_character.return_value = create_character_result

    # Default: world exists
    world_manager.get_world_details.return_value = (
        world_details if world_details is not None else MagicMock()
    )

    return DefaultCharacterWorldService(
        character_manager=char_manager,
        world_manager=world_manager,
    )


# ---------------------------------------------------------------------------
# initialize_default_character_and_world
# ---------------------------------------------------------------------------


class TestInitializeDefaultCharacterAndWorld:
    def test_skips_when_player_has_existing_characters(self):
        existing = [MagicMock()]
        svc = _make_service(player_characters=existing)
        result = svc.initialize_default_character_and_world("p1")
        assert result == (None, None, None)

    def test_returns_none_triple_when_character_creation_fails(self):
        svc = _make_service()
        svc.character_manager.create_character.side_effect = RuntimeError("db error")
        result = svc.initialize_default_character_and_world("p1")
        assert result == (None, None, None)

    def test_returns_char_and_none_when_world_not_found(self):
        char = MagicMock()
        char.character_id = "char-123"
        svc = _make_service(create_character_result=char)
        svc.world_manager.get_world_details.return_value = None

        char_id, world_id, session_id = svc.initialize_default_character_and_world("p1")
        assert char_id == "char-123"
        assert world_id is None
        assert session_id is None

    def test_full_success_returns_all_three_ids(self):
        char = MagicMock()
        char.character_id = "char-456"
        svc = _make_service(create_character_result=char)

        char_id, world_id, session_id = svc.initialize_default_character_and_world("p1")
        assert char_id == "char-456"
        assert world_id == DefaultCharacterWorldService.DEFAULT_WORLD_ID
        assert session_id is not None and len(session_id) > 0

    def test_unexpected_exception_returns_none_triple(self):
        svc = _make_service()
        svc.character_manager.get_player_characters.side_effect = RuntimeError(
            "unexpected"
        )
        result = svc.initialize_default_character_and_world("p1")
        assert result == (None, None, None)

    def test_calls_get_player_characters_with_player_id(self):
        svc = _make_service()
        svc.initialize_default_character_and_world("player-42")
        svc.character_manager.get_player_characters.assert_called_once_with("player-42")

    def test_verifies_default_world_exists(self):
        svc = _make_service()
        svc.initialize_default_character_and_world("p1")
        svc.world_manager.get_world_details.assert_called_once_with(
            DefaultCharacterWorldService.DEFAULT_WORLD_ID
        )

    def test_world_check_skipped_when_char_creation_fails(self):
        svc = _make_service()
        svc.character_manager.create_character.side_effect = RuntimeError("fail")
        svc.initialize_default_character_and_world("p1")
        svc.world_manager.get_world_details.assert_not_called()


# ---------------------------------------------------------------------------
# _create_default_character
# ---------------------------------------------------------------------------


class TestCreateDefaultCharacter:
    def test_returns_character_id_on_success(self):
        char = MagicMock()
        char.character_id = "char-789"
        svc = _make_service(create_character_result=char)
        result = svc._create_default_character("p1")
        assert result == "char-789"

    def test_returns_none_on_exception(self):
        svc = _make_service()
        svc.character_manager.create_character.side_effect = ValueError("bad data")
        result = svc._create_default_character("p1")
        assert result is None

    def test_passes_player_id_to_manager(self):
        svc = _make_service()
        svc._create_default_character("player-99")
        call_args = svc.character_manager.create_character.call_args
        assert call_args[0][0] == "player-99"


# ---------------------------------------------------------------------------
# _create_initial_session
# ---------------------------------------------------------------------------


class TestCreateInitialSession:
    def test_returns_uuid_string(self):
        svc = _make_service()
        session_id = svc._create_initial_session("p1", "c1", "w1")
        assert session_id is not None
        assert len(session_id) == 36  # UUID4 string length
        assert "-" in session_id

    def test_returns_different_ids_each_call(self):
        svc = _make_service()
        s1 = svc._create_initial_session("p1", "c1", "w1")
        s2 = svc._create_initial_session("p1", "c1", "w1")
        assert s1 != s2
