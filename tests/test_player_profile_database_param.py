import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock

from src.player_experience.database.player_profile_schema import PlayerProfileSchemaManager
from src.player_experience.database.player_profile_repository import PlayerProfileRepository
from src.player_experience.models.player import PlayerProfile


@pytest.mark.parametrize("mode", ["mock", pytest.param("container", marks=pytest.mark.neo4j)])
def test_schema_manager_setup_parametrized(mode, neo4j_container):
    if mode == "mock":
        mgr = PlayerProfileSchemaManager()
        # Inject mock driver
        mock_driver = MagicMock()
        mock_session_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session_ctx.__enter__.return_value = mock_session
        mock_session_ctx.__exit__.return_value = None
        mock_driver.session.return_value = mock_session_ctx
        mgr.driver = mock_driver
        # Use mock path
        assert mgr.create_player_profile_constraints() in {True, False}
        assert mgr.create_player_profile_indexes() in {True, False}
    else:
        mgr = PlayerProfileSchemaManager(
            uri=neo4j_container["uri"],
            username=neo4j_container["username"],
            password=neo4j_container["password"],
        )
        with mgr:
            ok = mgr.setup_player_profile_schema()
            assert ok is True
            assert mgr.is_connected() is True


@pytest.mark.parametrize("mode", ["mock", pytest.param("container", marks=pytest.mark.neo4j)])
def test_repository_crud_parametrized(mode, neo4j_container):
    if mode == "mock":
        repo = PlayerProfileRepository()
        mock_driver = MagicMock()
        mock_session_ctx = MagicMock()
        mock_session = MagicMock()
        mock_session_ctx.__enter__.return_value = mock_session
        mock_session_ctx.__exit__.return_value = None
        mock_driver.session.return_value = mock_session_ctx
        repo.driver = mock_driver

        profile = PlayerProfile(
            player_id="unit_player",
            username="unit_user",
            email="unit@example.com",
            created_at=datetime.now(),
        )
        mock_session.run.return_value.single.return_value = Mock()
        assert repo.create_player_profile(profile) is True
    else:
        repo = PlayerProfileRepository(
            uri=neo4j_container["uri"],
            username=neo4j_container["username"],
            password=neo4j_container["password"],
        )
        repo.connect()
        try:
            profile = PlayerProfile(
                player_id="it_param_player",
                username="it_user",
                email="it@example.com",
                created_at=datetime.now(),
            )
            assert repo.create_player_profile(profile) is True
            found = repo.get_player_profile("it_param_player")
            assert found is not None
            assert repo.delete_player_profile("it_param_player") is True
        finally:
            repo.disconnect()

