"""Tests for player_experience.api.routers.sessions module."""

# Logseq: [[TTA.dev/Tests/Player_experience/Api/Routers/Test_sessions]]


class TestSessionsRouter:
    """Tests for sessions router module."""

    def test_module_imports(self):
        """Test that module can be imported."""
        from src.player_experience.api.routers import sessions

        assert sessions is not None

    def test_module_has_expected_structure(self):
        """Test that module has expected structure."""
        from src.player_experience.api.routers import sessions

        assert hasattr(sessions, "__name__")

    def test_module_exposes_get_session_uow(self):
        """Test that get_session_uow dependency is available for override."""
        from src.player_experience.api.routers.sessions import get_session_uow

        assert callable(get_session_uow)

    def test_get_session_uow_returns_abstract_session_uow(self):
        """get_session_uow() returns an AbstractSessionUnitOfWork instance."""
        from src.player_experience.api.routers.sessions import get_session_uow
        from src.player_experience.uow.session_unit_of_work import (
            AbstractSessionUnitOfWork,
        )

        uow = get_session_uow()
        assert isinstance(uow, AbstractSessionUnitOfWork)
