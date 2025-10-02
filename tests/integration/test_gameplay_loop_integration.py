"""
Integration tests for the Core Gameplay Loop system.

These tests validate the complete flow from user authentication through
gameplay session completion, ensuring all TTA systems work together correctly.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.components.gameplay_loop_component import GameplayLoopComponent
from src.integration.gameplay_loop_integration import GameplayLoopIntegration
from src.player_experience.services.gameplay_service import GameplayService


class TestGameplayLoopIntegration:
    """Test suite for gameplay loop integration with TTA systems."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            "core_gameplay_loop": {
                "enabled": True,
                "max_concurrent_sessions": 10,
                "session_timeout_minutes": 30,
                "enable_performance_tracking": True,
                "narrative_engine": {
                    "complexity_adaptation": True,
                    "immersion_tracking": True,
                    "max_description_length": 2000,
                    "min_description_length": 100,
                },
                "choice_architecture": {
                    "min_choices": 2,
                    "max_choices": 5,
                    "therapeutic_weighting": 0.4,
                },
                "consequence_system": {
                    "learning_emphasis": True,
                    "pattern_tracking": True,
                    "therapeutic_framing": True,
                },
                "session_manager": {
                    "auto_save_interval": 60,
                    "context_preservation": True,
                    "therapeutic_goal_tracking": True,
                },
            },
            "tta": {
                "prototype": {
                    "components": {
                        "neo4j": {
                            "port": 7688,
                            "username": "neo4j",
                            "password": "password",
                        }
                    }
                }
            },
        }

    @pytest.fixture
    def mock_gameplay_component(self, mock_config):
        """Mock GameplayLoopComponent for testing."""
        component = Mock(spec=GameplayLoopComponent)
        component.get_status_info.return_value = {
            "name": "core_gameplay_loop",
            "status": "running",
            "enabled": True,
            "active_sessions": 0,
            "max_concurrent_sessions": 10,
        }

        # Mock async methods
        component.create_gameplay_session = AsyncMock(return_value="test-session-123")
        component.get_session_status = AsyncMock(
            return_value={
                "session_id": "test-session-123",
                "user_id": "test-user",
                "status": "active",
                "current_scene": {"description": "Test scene"},
                "available_choices": [{"id": "choice-1", "text": "Test choice"}],
            }
        )
        component.process_user_choice = AsyncMock(
            return_value={
                "next_scene": {"description": "Next scene"},
                "available_choices": [{"id": "choice-2", "text": "Next choice"}],
                "consequences": {"therapeutic_insight": "Test insight"},
            }
        )
        component.end_session = AsyncMock(return_value=True)
        component.pause_session = AsyncMock(return_value=True)
        component.resume_session = AsyncMock(
            return_value={
                "session_id": "test-session-123",
                "current_scene": {"description": "Resumed scene"},
                "available_choices": [{"id": "choice-3", "text": "Resume choice"}],
            }
        )
        component.get_session_metrics = AsyncMock(
            return_value={
                "active_sessions": 1,
                "max_concurrent_sessions": 10,
                "session_utilization": 0.1,
            }
        )

        return component

    @pytest.fixture
    def mock_safety_service(self):
        """Mock SafetyService for testing."""
        safety_service = Mock()
        safety_service.is_enabled.return_value = True

        # Mock validation result
        validation_result = Mock()
        validation_result.level.value = 3  # Low risk level
        safety_service.validate_text = AsyncMock(return_value=validation_result)
        safety_service.suggest_alternative.return_value = "Safe alternative content"

        return safety_service

    @pytest.fixture
    def mock_agent_orchestration(self):
        """Mock AgentOrchestrationService for testing."""
        return Mock()

    @pytest.fixture
    def integration_layer(
        self, mock_gameplay_component, mock_safety_service, mock_agent_orchestration
    ):
        """Create GameplayLoopIntegration instance for testing."""
        return GameplayLoopIntegration(
            gameplay_component=mock_gameplay_component,
            agent_orchestration=mock_agent_orchestration,
            safety_service=mock_safety_service,
        )

    @pytest.mark.asyncio
    async def test_create_authenticated_session_success(self, integration_layer):
        """Test successful session creation with authentication."""
        # Mock authentication
        with patch(
            "src.integration.gameplay_loop_integration.get_current_player"
        ) as mock_auth:
            mock_auth.return_value = {"user_id": "test-user", "username": "testuser"}

            result = await integration_layer.create_authenticated_session(
                auth_token="valid-token",
                therapeutic_context={"goals": ["anxiety_management"]},
            )

            assert result["success"] is True
            assert result["session_id"] == "test-session-123"
            assert result["user_id"] == "test-user"
            assert "created_at" in result

    @pytest.mark.asyncio
    async def test_create_authenticated_session_auth_failure(self, integration_layer):
        """Test session creation with authentication failure."""
        from src.player_experience.api.auth import AuthenticationError

        with patch(
            "src.integration.gameplay_loop_integration.get_current_player"
        ) as mock_auth:
            mock_auth.side_effect = AuthenticationError("Invalid token")

            result = await integration_layer.create_authenticated_session(
                auth_token="invalid-token"
            )

            assert result["success"] is False
            assert result["code"] == "AUTH_ERROR"
            assert "Authentication failed" in result["error"]

    @pytest.mark.asyncio
    async def test_process_validated_choice_success(self, integration_layer):
        """Test successful choice processing with validation."""
        with patch(
            "src.integration.gameplay_loop_integration.get_current_player"
        ) as mock_auth:
            mock_auth.return_value = {"user_id": "test-user", "username": "testuser"}

            result = await integration_layer.process_validated_choice(
                session_id="test-session-123",
                choice_id="choice-1",
                auth_token="valid-token",
            )

            assert result["success"] is True
            assert result["session_id"] == "test-session-123"
            assert "choice_result" in result
            assert "processed_at" in result

    @pytest.mark.asyncio
    async def test_process_validated_choice_access_denied(
        self, integration_layer, mock_gameplay_component
    ):
        """Test choice processing with access denied."""
        # Mock session with different user
        mock_gameplay_component.get_session_status.return_value = {
            "session_id": "test-session-123",
            "user_id": "other-user",  # Different user
            "status": "active",
        }

        with patch(
            "src.integration.gameplay_loop_integration.get_current_player"
        ) as mock_auth:
            mock_auth.return_value = {"user_id": "test-user", "username": "testuser"}

            result = await integration_layer.process_validated_choice(
                session_id="test-session-123",
                choice_id="choice-1",
                auth_token="valid-token",
            )

            assert result["success"] is False
            assert result["code"] == "ACCESS_DENIED"

    @pytest.mark.asyncio
    async def test_safety_validation_high_risk_content(
        self, integration_layer, mock_safety_service
    ):
        """Test safety validation with high-risk content."""
        # Mock high-risk validation result
        validation_result = Mock()
        validation_result.level.value = 9  # High risk level
        mock_safety_service.validate_text.return_value = validation_result

        with patch(
            "src.integration.gameplay_loop_integration.get_current_player"
        ) as mock_auth:
            mock_auth.return_value = {"user_id": "test-user", "username": "testuser"}

            result = await integration_layer.create_authenticated_session(
                auth_token="valid-token",
                therapeutic_context={"goals": ["harmful_content"]},
            )

            assert result["success"] is False
            assert result["code"] == "SAFETY_ERROR"
            assert result["safety_level"] == 9

    @pytest.mark.asyncio
    async def test_get_session_with_auth_success(self, integration_layer):
        """Test getting session status with authentication."""
        with patch(
            "src.integration.gameplay_loop_integration.get_current_player"
        ) as mock_auth:
            mock_auth.return_value = {"user_id": "test-user", "username": "testuser"}

            result = await integration_layer.get_session_with_auth(
                session_id="test-session-123", auth_token="valid-token"
            )

            assert result["success"] is True
            assert "session_status" in result
            assert "retrieved_at" in result

    @pytest.mark.asyncio
    async def test_end_session_with_auth_success(self, integration_layer):
        """Test ending session with authentication."""
        with patch(
            "src.integration.gameplay_loop_integration.get_current_player"
        ) as mock_auth:
            mock_auth.return_value = {"user_id": "test-user", "username": "testuser"}

            result = await integration_layer.end_session_with_auth(
                session_id="test-session-123", auth_token="valid-token"
            )

            assert result["success"] is True
            assert result["session_id"] == "test-session-123"
            assert "ended_at" in result

    def test_get_integration_status(self, integration_layer):
        """Test getting integration status."""
        status = integration_layer.get_integration_status()

        assert "gameplay_component" in status
        assert "agent_orchestration" in status
        assert "safety_service" in status

        assert status["gameplay_component"]["available"] is True
        assert status["agent_orchestration"]["available"] is True
        assert status["safety_service"]["available"] is True


class TestGameplayService:
    """Test suite for GameplayService."""

    @pytest.fixture
    def mock_integration(self):
        """Mock GameplayLoopIntegration for testing."""
        integration = Mock(spec=GameplayLoopIntegration)

        # Mock async methods
        integration.create_authenticated_session = AsyncMock(
            return_value={
                "success": True,
                "session_id": "test-session-123",
                "user_id": "test-user",
            }
        )
        integration.process_validated_choice = AsyncMock(
            return_value={
                "success": True,
                "session_id": "test-session-123",
                "choice_result": {"next_scene": {"description": "Test scene"}},
            }
        )
        integration.get_session_with_auth = AsyncMock(
            return_value={"success": True, "session_status": {"status": "active"}}
        )
        integration.end_session_with_auth = AsyncMock(
            return_value={"success": True, "session_id": "test-session-123"}
        )
        integration.get_user_sessions = AsyncMock(
            return_value={"success": True, "session_metrics": {"active_sessions": 1}}
        )
        integration.get_integration_status.return_value = {
            "gameplay_component": {"available": True},
            "agent_orchestration": {"available": True},
            "safety_service": {"available": True},
        }

        return integration

    @pytest.fixture
    def gameplay_service(self, mock_integration):
        """Create GameplayService instance for testing."""
        service = GameplayService()
        service._integration = mock_integration
        service._initialized = True
        return service

    @pytest.mark.asyncio
    async def test_create_authenticated_session(
        self, gameplay_service, mock_integration
    ):
        """Test GameplayService session creation."""
        result = await gameplay_service.create_authenticated_session(
            auth_token="valid-token", therapeutic_context={"goals": ["test"]}
        )

        assert result["success"] is True
        assert result["session_id"] == "test-session-123"
        mock_integration.create_authenticated_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_validated_choice(self, gameplay_service, mock_integration):
        """Test GameplayService choice processing."""
        result = await gameplay_service.process_validated_choice(
            session_id="test-session-123",
            choice_id="choice-1",
            auth_token="valid-token",
        )

        assert result["success"] is True
        assert result["session_id"] == "test-session-123"
        mock_integration.process_validated_choice.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_not_initialized(self):
        """Test service behavior when not initialized."""
        service = GameplayService()
        # Don't initialize the service

        result = await service.create_authenticated_session(auth_token="valid-token")

        # Should attempt to initialize but fail gracefully
        assert "error" in result

    def test_get_integration_status(self, gameplay_service, mock_integration):
        """Test getting integration status from service."""
        status = gameplay_service.get_integration_status()

        assert "gameplay_service" in status
        assert status["gameplay_service"]["initialized"] is True
        assert status["gameplay_service"]["integration_available"] is True

        mock_integration.get_integration_status.assert_called_once()


class TestEndToEndFlow:
    """End-to-end integration tests for the complete gameplay flow."""

    @pytest.mark.asyncio
    async def test_complete_gameplay_session_flow(self):
        """Test complete flow from session creation to completion."""
        # This would be a comprehensive test that:
        # 1. Creates a session with authentication
        # 2. Processes multiple choices
        # 3. Validates therapeutic content
        # 4. Tracks progress
        # 5. Ends the session

        # For now, this is a placeholder that would be implemented
        # with actual TTA system integration
        pass

    @pytest.mark.asyncio
    async def test_concurrent_session_handling(self):
        """Test handling of multiple concurrent sessions."""
        # This would test the system's ability to handle
        # multiple users with concurrent sessions
        pass

    @pytest.mark.asyncio
    async def test_session_persistence_and_recovery(self):
        """Test session persistence and recovery after interruption."""
        # This would test the system's ability to persist
        # session state and recover from interruptions
        pass
