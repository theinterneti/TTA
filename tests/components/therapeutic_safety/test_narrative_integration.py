"""
Integration Tests for Therapeutic Safety with Narrative Engine

This module tests the integration between the therapeutic safety validation system
and the narrative engine components.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.components.therapeutic_safety import (
    ContentPayload, ValidationContext, ValidationResult,
    SafetyValidationOrchestrator, ContentSafetyValidator, CrisisDetectionEngine
)
from src.components.therapeutic_safety.enums import (
    ValidationAction, SafetyLevel, CrisisLevel, ContentType, ValidationStatus
)
from src.components.gameplay_loop.narrative.therapeutic_integrator import TherapeuticIntegrator
from src.components.gameplay_loop.models.core import NarrativeScene
from src.components.gameplay_loop.services.session_state import SessionState
from src.components.gameplay_loop.narrative.events import EventBus


class TestNarrativeIntegration:
    """Test integration between safety validation and narrative engine."""
    
    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        return Mock(spec=EventBus)
    
    @pytest.fixture
    def safety_service(self):
        """Create mock safety service."""
        service = Mock()
        service.validate_content = AsyncMock()
        service.validate_user_input = AsyncMock()
        return service
    
    @pytest.fixture
    def narrative_engine(self, safety_service):
        """Create mock narrative engine with safety service."""
        engine = Mock()
        engine.safety_service = safety_service
        return engine
    
    @pytest.fixture
    def therapeutic_integrator(self, narrative_engine):
        """Create therapeutic integrator instance."""
        integrator = TherapeuticIntegrator(narrative_engine)
        return integrator
    
    @pytest.fixture
    def session_state(self):
        """Create mock session state."""
        state = Mock(spec=SessionState)
        state.session_id = "test_session_123"
        state.user_id = "test_user_456"
        state.context = {
            "therapeutic_goals": ["anxiety_management", "stress_management"],
            "safety_level": "standard",
            "risk_factors": [],
            "protective_factors": ["social_support"],
            "progress_metrics": {}
        }
        return state
    
    @pytest.fixture
    def narrative_scene(self):
        """Create mock narrative scene."""
        scene = Mock(spec=NarrativeScene)
        scene.scene_id = "scene_001"
        scene.scene_type = "therapeutic_interaction"
        scene.description = "You find yourself in a peaceful garden where you can practice mindfulness."
        scene.choices = [
            {"id": "choice_1", "text": "Take deep breaths and focus on the present moment"},
            {"id": "choice_2", "text": "Explore the garden and notice the details around you"}
        ]
        return scene
    
    @pytest.mark.asyncio
    async def test_therapeutic_integrator_initialization(self, therapeutic_integrator, safety_service):
        """Test therapeutic integrator initialization with safety service."""
        await therapeutic_integrator.initialize()
        
        # Should have connected to safety service
        assert therapeutic_integrator.safety_service == safety_service
    
    @pytest.mark.asyncio
    async def test_session_initialization(self, therapeutic_integrator, session_state):
        """Test session initialization with therapeutic context."""
        await therapeutic_integrator.initialize_session(session_state)
        
        # Should create therapeutic context
        assert session_state.session_id in therapeutic_integrator.session_contexts
        assert session_state.session_id in therapeutic_integrator.safety_monitors
        assert session_state.session_id in therapeutic_integrator.progress_trackers
        
        # Check therapeutic context
        context = therapeutic_integrator.session_contexts[session_state.session_id]
        assert context.session_id == session_state.session_id
        assert context.therapeutic_goals == ["anxiety_management", "stress_management"]
    
    @pytest.mark.asyncio
    async def test_safe_scene_validation(self, therapeutic_integrator, session_state, narrative_scene, safety_service):
        """Test validation of safe narrative scene."""
        # Setup safety service to return safe result
        safe_result = ValidationResult(
            validation_id="val_123",
            content_id="scene_001",
            action=ValidationAction.APPROVE,
            overall_safety_level=SafetyLevel.SAFE,
            crisis_level=CrisisLevel.NONE,
            status=ValidationStatus.COMPLETED
        )
        safety_service.validate_content.return_value = safe_result
        
        await therapeutic_integrator.initialize()
        await therapeutic_integrator.initialize_session(session_state)
        
        # Validate scene
        is_safe = await therapeutic_integrator.validate_scene_safety(session_state, narrative_scene)
        
        assert is_safe == True
        assert therapeutic_integrator.validation_count == 1
        assert therapeutic_integrator.safety_violations == 0
        
        # Check that safety service was called correctly
        safety_service.validate_content.assert_called_once()
        call_args = safety_service.validate_content.call_args
        content_payload = call_args[0][0]
        validation_context = call_args[0][1]
        
        assert content_payload.content_text == narrative_scene.description
        assert content_payload.content_type == ContentType.NARRATIVE_SCENE
        assert validation_context.user_id == session_state.user_id
        assert validation_context.session_id == session_state.session_id
    
    @pytest.mark.asyncio
    async def test_unsafe_scene_validation(self, therapeutic_integrator, session_state, safety_service):
        """Test validation of unsafe narrative scene."""
        # Create unsafe scene
        unsafe_scene = Mock(spec=NarrativeScene)
        unsafe_scene.scene_id = "unsafe_scene"
        unsafe_scene.scene_type = "narrative"
        unsafe_scene.description = "You feel overwhelmed and think about hurting yourself."
        unsafe_scene.choices = []
        
        # Setup safety service to return unsafe result
        unsafe_result = ValidationResult(
            validation_id="val_456",
            content_id="unsafe_scene",
            action=ValidationAction.REJECT,
            overall_safety_level=SafetyLevel.DANGER,
            crisis_level=CrisisLevel.HIGH,
            status=ValidationStatus.COMPLETED,
            crisis_indicators=["self_harm_ideation"],
            immediate_intervention_needed=True
        )
        safety_service.validate_content.return_value = unsafe_result
        
        await therapeutic_integrator.initialize()
        await therapeutic_integrator.initialize_session(session_state)
        
        # Validate scene
        is_safe = await therapeutic_integrator.validate_scene_safety(session_state, unsafe_scene)
        
        assert is_safe == False
        assert therapeutic_integrator.validation_count == 1
        assert therapeutic_integrator.safety_violations == 1
    
    @pytest.mark.asyncio
    async def test_crisis_intervention_handling(self, therapeutic_integrator, session_state, safety_service):
        """Test crisis intervention handling."""
        # Setup safety service to return crisis result
        crisis_result = ValidationResult(
            validation_id="val_crisis",
            content_id="crisis_content",
            action=ValidationAction.ESCALATE,
            overall_safety_level=SafetyLevel.CRITICAL,
            crisis_level=CrisisLevel.CRITICAL,
            status=ValidationStatus.COMPLETED,
            crisis_indicators=["suicide_ideation", "immediate_plan"],
            immediate_intervention_needed=True
        )
        safety_service.validate_content.return_value = crisis_result
        
        await therapeutic_integrator.initialize()
        await therapeutic_integrator.initialize_session(session_state)
        
        # Create crisis scene
        crisis_scene = Mock(spec=NarrativeScene)
        crisis_scene.scene_id = "crisis_scene"
        crisis_scene.description = "I want to end my life tonight."
        crisis_scene.choices = []
        
        # Validate scene
        is_safe = await therapeutic_integrator.validate_scene_safety(session_state, crisis_scene)
        
        assert is_safe == False
        assert therapeutic_integrator.crisis_interventions == 1
        
        # Check that crisis information was added to session context
        assert session_state.context["crisis_detected"] == True
        assert session_state.context["crisis_level"] == CrisisLevel.CRITICAL.value
        assert session_state.context["intervention_needed"] == True
        assert "suicide_ideation" in session_state.context["crisis_indicators"]
    
    @pytest.mark.asyncio
    async def test_user_input_validation(self, therapeutic_integrator, session_state, safety_service):
        """Test user input validation."""
        # Setup safety service for user input validation
        user_input_result = ValidationResult(
            validation_id="val_input",
            content_id="user_input",
            action=ValidationAction.APPROVE,
            overall_safety_level=SafetyLevel.SAFE,
            crisis_level=CrisisLevel.NONE,
            status=ValidationStatus.COMPLETED
        )
        safety_service.validate_user_input.return_value = user_input_result
        
        await therapeutic_integrator.initialize()
        await therapeutic_integrator.initialize_session(session_state)
        
        # Validate user input
        user_input = "I'm feeling better today and want to try some coping strategies."
        result = await therapeutic_integrator.validate_user_input_safety(session_state, user_input)
        
        assert result == user_input_result
        
        # Check that safety service was called correctly
        safety_service.validate_user_input.assert_called_once_with(
            user_input=user_input,
            user_id=session_state.user_id,
            session_id=session_state.session_id,
            validation_scope=ValidationScope.COMPREHENSIVE,
            timeout_ms=200
        )
    
    @pytest.mark.asyncio
    async def test_user_input_crisis_detection(self, therapeutic_integrator, session_state, safety_service):
        """Test crisis detection in user input."""
        # Setup safety service to detect crisis in user input
        crisis_input_result = ValidationResult(
            validation_id="val_crisis_input",
            content_id="crisis_user_input",
            action=ValidationAction.ESCALATE,
            overall_safety_level=SafetyLevel.CRITICAL,
            crisis_level=CrisisLevel.HIGH,
            status=ValidationStatus.COMPLETED,
            crisis_indicators=["suicide_ideation"],
            immediate_intervention_needed=True
        )
        safety_service.validate_user_input.return_value = crisis_input_result
        
        await therapeutic_integrator.initialize()
        await therapeutic_integrator.initialize_session(session_state)
        
        # Validate crisis user input
        crisis_input = "I want to kill myself and end everything."
        result = await therapeutic_integrator.validate_user_input_safety(session_state, crisis_input)
        
        assert result == crisis_input_result
        assert therapeutic_integrator.crisis_interventions == 1
        
        # Check that crisis was handled
        assert session_state.context["crisis_detected"] == True
        assert session_state.context["crisis_level"] == CrisisLevel.HIGH.value
    
    @pytest.mark.asyncio
    async def test_fallback_validation_without_safety_service(self, therapeutic_integrator, session_state, narrative_scene):
        """Test fallback validation when safety service is unavailable."""
        # Initialize without safety service
        therapeutic_integrator.narrative_engine.safety_service = None
        await therapeutic_integrator.initialize()
        await therapeutic_integrator.initialize_session(session_state)
        
        # Validate safe scene
        is_safe = await therapeutic_integrator.validate_scene_safety(session_state, narrative_scene)
        
        # Should use fallback validation and return True for safe content
        assert is_safe == True
    
    @pytest.mark.asyncio
    async def test_fallback_validation_unsafe_content(self, therapeutic_integrator, session_state):
        """Test fallback validation with unsafe content."""
        # Initialize without safety service
        therapeutic_integrator.narrative_engine.safety_service = None
        await therapeutic_integrator.initialize()
        await therapeutic_integrator.initialize_session(session_state)
        
        # Create unsafe scene with keywords
        unsafe_scene = Mock(spec=NarrativeScene)
        unsafe_scene.scene_id = "unsafe_fallback"
        unsafe_scene.description = "You think about suicide and want to kill yourself."
        unsafe_scene.choices = []
        
        # Validate unsafe scene
        is_safe = await therapeutic_integrator.validate_scene_safety(session_state, unsafe_scene)
        
        # Should detect unsafe keywords and return False
        assert is_safe == False
    
    @pytest.mark.asyncio
    async def test_session_safety_monitoring(self, therapeutic_integrator, session_state):
        """Test ongoing session safety monitoring."""
        await therapeutic_integrator.initialize()
        await therapeutic_integrator.initialize_session(session_state)
        
        # Add recent interactions with safety concerns
        session_state.context["recent_interactions"] = [
            {"id": "int_1", "safety_concern": True},
            {"id": "int_2", "safety_concern": False},
            {"id": "int_3", "safety_concern": True},
            {"id": "int_4", "safety_concern": True}
        ]
        
        # Monitor session safety
        await therapeutic_integrator.monitor_session_safety(session_state)
        
        # Should detect concerning pattern
        assert session_state.context.get("safety_alert") == True
        
        # Safety level should be updated
        safety_monitor = therapeutic_integrator.safety_monitors[session_state.session_id]
        assert safety_monitor.safety_level == "elevated"
    
    @pytest.mark.asyncio
    async def test_session_finalization(self, therapeutic_integrator, session_state):
        """Test session finalization with progress tracking."""
        await therapeutic_integrator.initialize()
        await therapeutic_integrator.initialize_session(session_state)
        
        # Update progress tracker
        progress_tracker = therapeutic_integrator.progress_trackers[session_state.session_id]
        progress_tracker.metrics["anxiety_reduction"] = 0.7
        progress_tracker.milestones.append("completed_breathing_exercise")
        
        # Finalize session
        await therapeutic_integrator.finalize_session(session_state)
        
        # Check that progress was saved to session context
        assert session_state.context["progress_metrics"]["anxiety_reduction"] == 0.7
        assert "completed_breathing_exercise" in session_state.context["milestones"]
        
        # Check that session data was cleaned up
        assert session_state.session_id not in therapeutic_integrator.session_contexts
        assert session_state.session_id not in therapeutic_integrator.safety_monitors
        assert session_state.session_id not in therapeutic_integrator.progress_trackers
    
    def test_validation_context_creation(self, therapeutic_integrator, session_state):
        """Test validation context creation from session state."""
        # Initialize session
        therapeutic_integrator.session_contexts[session_state.session_id] = Mock()
        therapeutic_integrator.session_contexts[session_state.session_id].therapeutic_goals = ["anxiety_management"]
        
        therapeutic_integrator.safety_monitors[session_state.session_id] = Mock()
        therapeutic_integrator.safety_monitors[session_state.session_id].risk_factors = ["stress"]
        
        # Create validation context
        context = therapeutic_integrator._create_validation_context(session_state)
        
        assert context.user_id == session_state.user_id
        assert context.session_id == session_state.session_id
        assert context.user_therapeutic_goals == ["anxiety_management"]
        assert context.user_risk_factors == ["stress"]
        assert context.timeout_ms == 200
    
    def test_get_metrics(self, therapeutic_integrator):
        """Test metrics collection."""
        # Set some metrics
        therapeutic_integrator.validation_count = 5
        therapeutic_integrator.safety_violations = 2
        therapeutic_integrator.crisis_interventions = 1
        
        # Add some active sessions
        therapeutic_integrator.session_contexts["session_1"] = Mock()
        therapeutic_integrator.safety_monitors["session_1"] = Mock()
        therapeutic_integrator.progress_trackers["session_1"] = Mock()
        
        metrics = therapeutic_integrator.get_metrics()
        
        assert metrics["validation_count"] == 5
        assert metrics["safety_violations"] == 2
        assert metrics["crisis_interventions"] == 1
        assert metrics["active_sessions"] == 1
        assert metrics["safety_monitors"] == 1
        assert metrics["progress_trackers"] == 1
