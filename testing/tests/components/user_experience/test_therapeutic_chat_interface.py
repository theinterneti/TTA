"""
Tests for Therapeutic Chat Interface System.

This module tests the comprehensive therapeutic chat interface including
real-time messaging, therapeutic response generation, session management,
and integration with all therapeutic systems.
"""

from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from src.components.user_experience.therapeutic_chat_interface import (
    ChatMessage,
    ChatSession,
    ConversationState,
    MessageType,
    ResponsePriority,
    TherapeuticChatInterface,
    TherapeuticFramework,
)


class TestTherapeuticChatInterface:
    """Test Therapeutic Chat Interface functionality."""

    @pytest_asyncio.fixture
    async def chat_interface(self):
        """Create test chat interface instance."""
        interface = TherapeuticChatInterface()
        await interface.initialize()
        yield interface
        await interface.shutdown()

    @pytest.fixture
    def mock_accessibility_system(self):
        """Create mock accessibility system."""
        system = AsyncMock()
        system.accessibility_profiles = {
            "test_user_001": Mock(
                disability_types=["visual"],
                enabled_features={"screen_reader", "high_contrast"},
                font_size_multiplier=1.2
            )
        }
        return system

    @pytest.fixture
    def mock_ui_engine(self):
        """Create mock UI engine."""
        engine = AsyncMock()
        engine.interface_configurations = {}
        engine.interface_layouts = {}
        return engine

    @pytest.fixture
    def mock_engagement_system(self):
        """Create mock engagement system."""
        system = AsyncMock()
        system.track_user_engagement.return_value = Mock(
            session_frequency=0.8,
            completion_rate=0.9,
            engagement_level="high"
        )
        return system

    @pytest.fixture
    def mock_personalization_engine(self):
        """Create mock personalization engine."""
        engine = AsyncMock()

        # Mock user profile
        mock_profile = Mock()
        mock_profile.therapeutic_preferences = {
            "focus_areas": ["anxiety", "depression"],
            "approaches": ["cbt", "mindfulness"]
        }
        mock_profile.engagement_metrics = {
            "session_frequency": 0.8,
            "completion_rate": 0.75
        }

        engine.get_user_profile.return_value = mock_profile
        return engine

    @pytest.fixture
    def mock_therapeutic_systems(self):
        """Create mock therapeutic systems."""
        systems = {}

        # Mock emotional safety system
        emotional_safety = AsyncMock()
        emotional_safety.assess_crisis_risk.return_value = {"risk_level": 0.1}
        emotional_safety.provide_crisis_intervention.return_value = {
            "intervention_message": "I'm here to help you through this difficult time."
        }
        systems["emotional_safety_system"] = emotional_safety

        # Mock therapeutic integration system
        therapeutic_integration = AsyncMock()
        therapeutic_integration.generate_therapeutic_response.return_value = {
            "response_text": "That's a thoughtful observation. Let's explore that further."
        }
        systems["therapeutic_integration_system"] = therapeutic_integration

        # Add other therapeutic systems
        for system_name in [
            "consequence_system",
            "adaptive_difficulty_engine",
            "character_development_system",
            "gameplay_loop_controller",
            "replayability_system",
            "collaborative_system",
            "error_recovery_manager"
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}
            systems[system_name] = mock_system

        return systems

    @pytest.fixture
    def sample_therapeutic_goals(self):
        """Create sample therapeutic goals."""
        return ["anxiety_management", "stress_reduction", "mindfulness_practice"]

    @pytest.fixture
    def sample_session_config(self):
        """Create sample session configuration."""
        return {
            "max_duration": 45,
            "auto_save_interval": 300,
            "enable_crisis_detection": True
        }

    @pytest.mark.asyncio
    async def test_initialization(self, chat_interface):
        """Test chat interface initialization."""
        assert chat_interface.status == "running"
        assert len(chat_interface.message_processors) == 8  # 8 message types
        assert len(chat_interface.response_generators) == 8  # 8 therapeutic frameworks
        assert len(chat_interface.intervention_handlers) == 8  # 8 intervention types
        assert len(chat_interface.conversation_flow_templates) == 3  # 3 flow templates
        assert len(chat_interface.therapeutic_templates) == 5  # 5 template categories

        # Should have background tasks running
        assert chat_interface._message_processing_task is not None
        assert chat_interface._session_management_task is not None
        assert chat_interface._therapeutic_monitoring_task is not None
        assert chat_interface._performance_monitoring_task is not None

    @pytest.mark.asyncio
    async def test_system_dependency_injection(self, chat_interface, mock_accessibility_system, mock_ui_engine, mock_engagement_system, mock_personalization_engine, mock_therapeutic_systems):
        """Test system dependency injection."""
        chat_interface.inject_accessibility_system(mock_accessibility_system)
        chat_interface.inject_ui_engine(mock_ui_engine)
        chat_interface.inject_engagement_system(mock_engagement_system)
        chat_interface.inject_personalization_engine(mock_personalization_engine)
        chat_interface.inject_therapeutic_systems(**mock_therapeutic_systems)
        chat_interface.inject_integration_systems(
            clinical_dashboard_manager=AsyncMock(),
            cloud_deployment_manager=AsyncMock()
        )

        # Should have all systems injected
        assert chat_interface.accessibility_system is not None
        assert chat_interface.ui_engine is not None
        assert chat_interface.engagement_system is not None
        assert chat_interface.personalization_engine is not None
        assert len(chat_interface.therapeutic_systems) == 9
        assert chat_interface.clinical_dashboard_manager is not None
        assert chat_interface.cloud_deployment_manager is not None

    @pytest.mark.asyncio
    async def test_start_chat_session(self, chat_interface, mock_personalization_engine, sample_therapeutic_goals, sample_session_config):
        """Test starting a new chat session."""
        # Inject dependencies
        chat_interface.inject_personalization_engine(mock_personalization_engine)

        user_id = "chat_user_001"

        session = await chat_interface.start_chat_session(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals,
            session_config=sample_session_config
        )

        # Should create valid session
        assert isinstance(session, ChatSession)
        assert session.user_id == user_id
        assert session.session_goals == sample_therapeutic_goals
        assert session.max_duration_minutes == 45
        assert session.conversation_state == ConversationState.INITIALIZING
        assert session.is_active is True

        # Should store session data
        assert session.session_id in chat_interface.active_sessions
        assert session.session_id in chat_interface.therapeutic_contexts
        assert session.session_id in chat_interface.conversation_flows

        # Should have welcome message
        assert len(session.messages) == 1
        welcome_message = session.messages[0]
        assert welcome_message.message_type == MessageType.THERAPEUTIC_RESPONSE
        assert len(welcome_message.content) > 0

        # Should update metrics
        assert chat_interface.chat_system_metrics["total_active_sessions"] == 1
        assert chat_interface.chat_system_metrics["concurrent_users"] == 1

    @pytest.mark.asyncio
    async def test_process_user_message(self, chat_interface, mock_therapeutic_systems, mock_engagement_system, sample_therapeutic_goals):
        """Test processing user messages."""
        # Inject dependencies
        chat_interface.inject_therapeutic_systems(**mock_therapeutic_systems)
        chat_interface.inject_engagement_system(mock_engagement_system)

        user_id = "message_user_001"

        # Start session
        session = await chat_interface.start_chat_session(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals
        )

        # Process user message
        user_message_content = "I've been feeling really anxious lately and having trouble sleeping."

        import time
        start_time = time.perf_counter()

        response_message = await chat_interface.process_user_message(
            session_id=session.session_id,
            message_content=user_message_content,
            message_metadata={"context": "anxiety_discussion"}
        )

        processing_time = (time.perf_counter() - start_time) * 1000

        # Should create valid response
        assert isinstance(response_message, ChatMessage)
        assert response_message.message_type == MessageType.THERAPEUTIC_RESPONSE
        assert len(response_message.content) > 0
        assert response_message.session_id == session.session_id
        assert response_message.user_id == user_id
        assert response_message.processing_time_ms > 0

        # Should meet performance requirements
        assert processing_time < 1000  # Should be under 1 second

        # Should update session
        updated_session = chat_interface.active_sessions[session.session_id]
        assert updated_session.message_count == 3  # Welcome + user + response
        assert len(updated_session.messages) == 3

        # Should analyze message content
        user_message = updated_session.messages[1]  # Second message is user message
        assert user_message.message_type == MessageType.USER_MESSAGE
        assert user_message.content == user_message_content
        assert "negative" in user_message.emotional_indicators
        assert user_message.emotional_indicators["negative"] > 0

        # Should update metrics
        assert chat_interface.chat_system_metrics["total_messages_processed"] > 0
        assert chat_interface.chat_system_metrics["average_response_time_ms"] > 0

    @pytest.mark.asyncio
    async def test_crisis_detection_and_response(self, chat_interface, mock_therapeutic_systems, sample_therapeutic_goals):
        """Test crisis detection and intervention."""
        # Inject dependencies
        chat_interface.inject_therapeutic_systems(**mock_therapeutic_systems)

        user_id = "crisis_user_001"

        # Start session
        session = await chat_interface.start_chat_session(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals
        )

        # Process crisis message
        crisis_message = "I can't take this anymore. I just want to end it all."

        response_message = await chat_interface.process_user_message(
            session_id=session.session_id,
            message_content=crisis_message
        )

        # Should detect crisis and respond appropriately
        assert response_message.message_type == MessageType.CRISIS_INTERVENTION
        assert response_message.response_priority == ResponsePriority.CRISIS
        assert response_message.requires_human_review is True
        assert len(response_message.content) > 0

        # Should update crisis metrics
        assert chat_interface.chat_system_metrics["crisis_interventions"] == 1

        # Should assess crisis risk
        updated_session = chat_interface.active_sessions[session.session_id]
        user_message = updated_session.messages[1]  # User's crisis message
        assert user_message.crisis_risk_level > 0.3
        assert "crisis" in user_message.emotional_indicators

    @pytest.mark.asyncio
    async def test_therapeutic_framework_selection(self, chat_interface, sample_therapeutic_goals):
        """Test therapeutic framework selection for responses."""
        user_id = "framework_user_001"

        # Start session
        session = await chat_interface.start_chat_session(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals
        )

        # Test CBT framework selection
        cbt_message = "I keep thinking that everything will go wrong."
        response = await chat_interface.process_user_message(
            session_id=session.session_id,
            message_content=cbt_message
        )

        # Should select CBT framework
        assert TherapeuticFramework.CBT in response.therapeutic_frameworks
        assert "thought" in response.content.lower()

        # Test mindfulness framework selection
        mindfulness_message = "I want to be more present and mindful."
        response = await chat_interface.process_user_message(
            session_id=session.session_id,
            message_content=mindfulness_message
        )

        # Should select mindfulness framework
        assert TherapeuticFramework.MINDFULNESS in response.therapeutic_frameworks
        assert any(word in response.content.lower() for word in ["present", "notice", "breath"])

    @pytest.mark.asyncio
    async def test_session_history_and_management(self, chat_interface, sample_therapeutic_goals):
        """Test session history and management."""
        user_id = "history_user_001"

        # Start session
        session = await chat_interface.start_chat_session(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals
        )

        # Send multiple messages
        messages = [
            "Hello, I'm feeling anxious today.",
            "I had a panic attack yesterday.",
            "I want to learn coping strategies."
        ]

        for message in messages:
            await chat_interface.process_user_message(
                session_id=session.session_id,
                message_content=message
            )

        # Get session history
        history = await chat_interface.get_session_history(session.session_id)

        # Should return all messages (welcome + user messages + responses)
        assert len(history) == 7  # 1 welcome + 3 user + 3 responses

        # Test limited history
        limited_history = await chat_interface.get_session_history(session.session_id, limit=3)
        assert len(limited_history) == 3

        # Test therapeutic goals update
        new_goals = ["depression_management", "sleep_improvement"]
        success = await chat_interface.update_therapeutic_goals(
            session_id=session.session_id,
            new_goals=new_goals
        )

        assert success is True
        updated_session = chat_interface.active_sessions[session.session_id]
        assert updated_session.session_goals == new_goals

    @pytest.mark.asyncio
    async def test_session_completion_and_summary(self, chat_interface, mock_engagement_system, sample_therapeutic_goals):
        """Test session completion and summary generation."""
        # Inject dependencies
        chat_interface.inject_engagement_system(mock_engagement_system)

        user_id = "completion_user_001"

        # Start session
        session = await chat_interface.start_chat_session(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals
        )

        # Send some messages
        await chat_interface.process_user_message(
            session_id=session.session_id,
            message_content="I've been working on my anxiety management."
        )

        await chat_interface.process_user_message(
            session_id=session.session_id,
            message_content="I feel like I'm making progress."
        )

        # End session
        summary = await chat_interface.end_chat_session(
            session_id=session.session_id,
            session_summary="Great progress on anxiety management techniques."
        )

        # Should generate valid summary
        assert "session_id" in summary
        assert "user_id" in summary
        assert "duration_minutes" in summary
        assert "message_count" in summary
        assert "therapeutic_goals" in summary
        assert "summary_text" in summary

        # Should clean up session
        assert session.session_id not in chat_interface.active_sessions
        assert session.session_id not in chat_interface.therapeutic_contexts
        assert session.session_id not in chat_interface.conversation_flows

        # Should update metrics
        assert chat_interface.chat_system_metrics["total_active_sessions"] == 0
        assert chat_interface.chat_system_metrics["concurrent_users"] == 0

    @pytest.mark.asyncio
    async def test_therapeutic_insights(self, chat_interface, sample_therapeutic_goals):
        """Test therapeutic insights generation."""
        user_id = "insights_user_001"

        # Start session
        session = await chat_interface.start_chat_session(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals
        )

        # Send messages to build context
        await chat_interface.process_user_message(
            session_id=session.session_id,
            message_content="I'm feeling much better today."
        )

        # Get therapeutic insights
        insights = await chat_interface.get_therapeutic_insights(session.session_id)

        # Should return comprehensive insights
        assert "session_id" in insights
        assert "user_id" in insights
        assert "session_duration" in insights
        assert "message_count" in insights
        assert "conversation_state" in insights
        assert "therapeutic_progress" in insights
        assert "emotional_journey" in insights
        assert "engagement_metrics" in insights
        assert "recommendations" in insights

        assert insights["session_id"] == session.session_id
        assert insights["user_id"] == user_id
        assert insights["message_count"] > 0
        assert isinstance(insights["recommendations"], list)

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, chat_interface, mock_therapeutic_systems, mock_engagement_system, sample_therapeutic_goals):
        """Test performance benchmarks for chat operations."""
        import time

        # Inject dependencies
        chat_interface.inject_therapeutic_systems(**mock_therapeutic_systems)
        chat_interface.inject_engagement_system(mock_engagement_system)

        user_id = "performance_user_001"

        # Test session creation performance
        start_time = time.perf_counter()

        session = await chat_interface.start_chat_session(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals
        )

        session_creation_time = (time.perf_counter() - start_time) * 1000
        assert session_creation_time < 500.0  # Should be under 500ms

        # Test message processing performance
        messages = [
            "I'm feeling anxious about work.",
            "I had trouble sleeping last night.",
            "I want to learn relaxation techniques.",
            "Can you help me with breathing exercises?",
            "I think I'm making progress."
        ]

        total_processing_time = 0

        for message in messages:
            start_time = time.perf_counter()

            response = await chat_interface.process_user_message(
                session_id=session.session_id,
                message_content=message
            )

            processing_time = (time.perf_counter() - start_time) * 1000
            total_processing_time += processing_time

            # Each message should be processed under 1 second
            assert processing_time < 1000.0
            assert response.processing_time_ms > 0

        # Average processing time should be reasonable
        average_processing_time = total_processing_time / len(messages)
        assert average_processing_time < 800.0  # Should average under 800ms

        # Test session completion performance
        start_time = time.perf_counter()

        await chat_interface.end_chat_session(session.session_id)

        completion_time = (time.perf_counter() - start_time) * 1000
        assert completion_time < 300.0  # Should be under 300ms

    @pytest.mark.asyncio
    async def test_chat_interface_integration_compatibility(self, chat_interface, mock_accessibility_system, mock_ui_engine, mock_engagement_system, mock_personalization_engine, mock_therapeutic_systems, sample_therapeutic_goals):
        """Test compatibility with chat interface integration expectations."""
        # Inject all dependencies
        chat_interface.inject_accessibility_system(mock_accessibility_system)
        chat_interface.inject_ui_engine(mock_ui_engine)
        chat_interface.inject_engagement_system(mock_engagement_system)
        chat_interface.inject_personalization_engine(mock_personalization_engine)
        chat_interface.inject_therapeutic_systems(**mock_therapeutic_systems)
        chat_interface.inject_integration_systems(
            clinical_dashboard_manager=AsyncMock(),
            cloud_deployment_manager=AsyncMock()
        )

        user_id = "integration_user_001"

        # Test complete chat workflow
        session = await chat_interface.start_chat_session(
            user_id=user_id,
            therapeutic_goals=sample_therapeutic_goals
        )

        # Should match expected session structure
        assert hasattr(session, "session_id")
        assert hasattr(session, "user_id")
        assert hasattr(session, "conversation_state")
        assert hasattr(session, "session_goals")
        assert hasattr(session, "messages")
        assert hasattr(session, "message_count")

        # Test message processing
        response = await chat_interface.process_user_message(
            session_id=session.session_id,
            message_content="I'm feeling overwhelmed with work stress."
        )

        # Should match expected message structure
        assert hasattr(response, "message_id")
        assert hasattr(response, "session_id")
        assert hasattr(response, "user_id")
        assert hasattr(response, "message_type")
        assert hasattr(response, "content")
        assert hasattr(response, "therapeutic_context")
        assert hasattr(response, "processing_time_ms")

        # Test therapeutic insights
        insights = await chat_interface.get_therapeutic_insights(session.session_id)

        # Should match expected insights structure
        assert "session_id" in insights
        assert "therapeutic_progress" in insights
        assert "emotional_journey" in insights
        assert "recommendations" in insights

        # Test health check
        health_check = await chat_interface.health_check()

        # Should match expected health check structure
        assert "status" in health_check
        assert "chat_interface_status" in health_check
        assert "active_sessions" in health_check
        assert "chat_system_metrics" in health_check
        assert "system_integrations" in health_check
