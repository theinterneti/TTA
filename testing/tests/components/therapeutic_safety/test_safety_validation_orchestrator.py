"""
Tests for SafetyValidationOrchestrator

This module tests the main orchestrator for therapeutic safety content validation.
"""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from src.components.gameplay_loop.narrative.events import EventBus
from src.components.therapeutic_safety.enums import (
    ContentType,
    CrisisLevel,
    SafetyLevel,
    ValidationAction,
    ValidationComponent,
    ValidationStatus,
)
from src.components.therapeutic_safety.models import (
    ContentPayload,
    ValidationContext,
    ValidationResult,
)
from src.components.therapeutic_safety.orchestrator import (
    SafetyValidationOrchestrator,
    ValidationPipeline,
)


class TestValidationPipeline:
    """Test ValidationPipeline functionality."""

    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = ValidationPipeline()
        assert len(pipeline.components) == 0
        assert len(pipeline.component_timeouts) == 0
        assert len(pipeline.component_priorities) == 0

    def test_register_component(self):
        """Test component registration."""
        pipeline = ValidationPipeline()
        mock_validator = Mock()

        pipeline.register_component(
            ValidationComponent.CONTENT_SAFETY,
            mock_validator,
            timeout_ms=100,
            priority=5,
        )

        assert ValidationComponent.CONTENT_SAFETY in pipeline.components
        assert pipeline.components[ValidationComponent.CONTENT_SAFETY] == mock_validator
        assert pipeline.component_timeouts[ValidationComponent.CONTENT_SAFETY] == 100
        assert pipeline.component_priorities[ValidationComponent.CONTENT_SAFETY] == 5

    def test_get_ordered_components(self):
        """Test component ordering by priority."""
        pipeline = ValidationPipeline()

        # Register components with different priorities
        pipeline.register_component(
            ValidationComponent.CONTENT_SAFETY, Mock(), priority=3
        )
        pipeline.register_component(
            ValidationComponent.CRISIS_DETECTION, Mock(), priority=10
        )
        pipeline.register_component(
            ValidationComponent.BIAS_DETECTION, Mock(), priority=1
        )

        ordered = pipeline.get_ordered_components()

        # Should be ordered by priority (highest first)
        assert ordered[0] == ValidationComponent.CRISIS_DETECTION  # priority 10
        assert ordered[1] == ValidationComponent.CONTENT_SAFETY  # priority 3
        assert ordered[2] == ValidationComponent.BIAS_DETECTION  # priority 1

    @pytest.mark.asyncio
    async def test_run_component_success(self):
        """Test successful component execution."""
        pipeline = ValidationPipeline()

        # Mock validator that returns a result
        mock_validator = AsyncMock(return_value={"status": "success", "score": 0.8})
        pipeline.register_component(
            ValidationComponent.CONTENT_SAFETY, mock_validator, timeout_ms=100
        )

        content = ContentPayload(content_text="Test content")
        context = ValidationContext(user_id="test_user")

        result = await pipeline.run_component(
            ValidationComponent.CONTENT_SAFETY, content, context
        )

        assert result["status"] == "success"
        assert result["score"] == 0.8
        mock_validator.assert_called_once_with(content, context)

    @pytest.mark.asyncio
    async def test_run_component_timeout(self):
        """Test component timeout handling."""
        pipeline = ValidationPipeline()

        # Mock validator that takes too long
        async def slow_validator(content, context):
            await asyncio.sleep(0.2)  # 200ms
            return {"status": "success"}

        pipeline.register_component(
            ValidationComponent.CONTENT_SAFETY, slow_validator, timeout_ms=50
        )

        content = ContentPayload(content_text="Test content")
        context = ValidationContext(user_id="test_user")

        result = await pipeline.run_component(
            ValidationComponent.CONTENT_SAFETY, content, context
        )

        assert result["status"] == "timeout"
        assert result["component"] == ValidationComponent.CONTENT_SAFETY.value


class TestSafetyValidationOrchestrator:
    """Test SafetyValidationOrchestrator functionality."""

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        return Mock(spec=EventBus)

    @pytest.fixture
    def cache_manager(self):
        """Create mock cache manager."""
        cache = Mock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock(return_value=True)
        return cache

    @pytest.fixture
    def orchestrator(self, event_bus, cache_manager):
        """Create orchestrator instance."""
        return SafetyValidationOrchestrator(event_bus, cache_manager)

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        # Mock validators
        orchestrator.content_safety_validator = Mock()
        orchestrator.crisis_detection_engine = Mock()
        orchestrator.bias_detection_validator = Mock()
        orchestrator.therapeutic_alignment_validator = Mock()

        await orchestrator.initialize()

        # Check that components are registered
        assert len(orchestrator.pipeline.components) == 4
        assert ValidationComponent.CONTENT_SAFETY in orchestrator.pipeline.components
        assert ValidationComponent.CRISIS_DETECTION in orchestrator.pipeline.components
        assert ValidationComponent.BIAS_DETECTION in orchestrator.pipeline.components
        assert (
            ValidationComponent.THERAPEUTIC_ALIGNMENT
            in orchestrator.pipeline.components
        )

    @pytest.mark.asyncio
    async def test_validate_content_success(self, orchestrator, event_bus):
        """Test successful content validation."""
        # Setup mock validators
        content_validator = AsyncMock(
            return_value={"safety_level": SafetyLevel.SAFE, "violations": []}
        )
        crisis_detector = AsyncMock(
            return_value={"crisis_level": CrisisLevel.NONE, "indicators": []}
        )

        orchestrator.content_safety_validator = Mock()
        orchestrator.content_safety_validator.validate = content_validator
        orchestrator.crisis_detection_engine = Mock()
        orchestrator.crisis_detection_engine.assess_crisis = crisis_detector

        await orchestrator.initialize()

        # Create test content and context
        content = ContentPayload(
            content_text="This is safe therapeutic content about coping strategies.",
            content_type=ContentType.NARRATIVE_SCENE,
        )
        context = ValidationContext(user_id="test_user", timeout_ms=200)

        # Validate content
        result = await orchestrator.validate_content(content, context)

        # Check result
        assert result.status == ValidationStatus.COMPLETED
        assert result.action == ValidationAction.APPROVE
        assert result.overall_safety_level == SafetyLevel.SAFE
        assert result.crisis_level == CrisisLevel.NONE
        assert result.processing_time_ms > 0

        # Check that validators were called
        content_validator.assert_called_once()
        crisis_detector.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_content_crisis_detected(self, orchestrator, event_bus):
        """Test content validation with crisis detection."""
        # Setup mock validators
        content_validator = AsyncMock(
            return_value={
                "safety_level": SafetyLevel.DANGER,
                "violations": ["self_harm_content"],
            }
        )
        crisis_detector = AsyncMock(
            return_value={
                "crisis_level": CrisisLevel.HIGH,
                "indicators": ["suicide ideation"],
                "immediate_intervention": True,
            }
        )

        orchestrator.content_safety_validator = Mock()
        orchestrator.content_safety_validator.validate = content_validator
        orchestrator.crisis_detection_engine = Mock()
        orchestrator.crisis_detection_engine.assess_crisis = crisis_detector

        await orchestrator.initialize()

        # Create test content with crisis indicators
        content = ContentPayload(
            content_text="I want to hurt myself and end it all.",
            content_type=ContentType.USER_INPUT,
        )
        context = ValidationContext(user_id="test_user", timeout_ms=200)

        # Validate content
        result = await orchestrator.validate_content(content, context)

        # Check result
        assert result.status == ValidationStatus.COMPLETED
        assert result.action == ValidationAction.ESCALATE
        assert result.crisis_level == CrisisLevel.HIGH
        assert result.immediate_intervention_needed
        assert "suicide ideation" in result.crisis_indicators

    @pytest.mark.asyncio
    async def test_validate_content_timeout(self, orchestrator, event_bus):
        """Test content validation timeout handling."""

        # Setup slow validator
        async def slow_validator(content, context):
            await asyncio.sleep(0.3)  # 300ms - longer than timeout
            return {"safety_level": SafetyLevel.SAFE}

        orchestrator.content_safety_validator = Mock()
        orchestrator.content_safety_validator.validate = slow_validator

        await orchestrator.initialize()

        # Create test content and context with short timeout
        content = ContentPayload(content_text="Test content")
        context = ValidationContext(
            user_id="test_user", timeout_ms=100
        )  # 100ms timeout

        # Validate content
        result = await orchestrator.validate_content(content, context)

        # Check result
        assert result.status == ValidationStatus.TIMEOUT
        assert result.processing_time_ms == 100  # Should match timeout

    @pytest.mark.asyncio
    async def test_validate_content_with_cache_hit(
        self, orchestrator, cache_manager, event_bus
    ):
        """Test content validation with cache hit."""
        # Setup cache to return a result
        cached_result = ValidationResult(
            validation_id="cached_validation",
            content_id="test_content",
            action=ValidationAction.APPROVE,
            overall_safety_level=SafetyLevel.SAFE,
        )
        cache_manager.get = AsyncMock(return_value=cached_result)

        # Create test content and context
        content = ContentPayload(content_text="Test content")
        context = ValidationContext(user_id="test_user")

        # Validate content
        result = await orchestrator.validate_content(content, context)

        # Check that cached result was returned
        assert result == cached_result
        assert result.cache_hit
        assert orchestrator.metrics["cache_hits"] == 1

        # Check that cache was queried
        cache_manager.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_content_cache_miss(
        self, orchestrator, cache_manager, event_bus
    ):
        """Test content validation with cache miss."""
        # Setup cache to return None (miss)
        cache_manager.get = AsyncMock(return_value=None)

        # Setup mock validator
        content_validator = AsyncMock(
            return_value={"safety_level": SafetyLevel.SAFE, "violations": []}
        )
        orchestrator.content_safety_validator = Mock()
        orchestrator.content_safety_validator.validate = content_validator

        await orchestrator.initialize()

        # Create test content and context
        content = ContentPayload(content_text="Test content")
        context = ValidationContext(user_id="test_user")

        # Validate content
        result = await orchestrator.validate_content(content, context)

        # Check that validation was performed
        assert result.status == ValidationStatus.COMPLETED
        assert orchestrator.metrics["cache_misses"] == 1

        # Check that result was cached
        cache_manager.set.assert_called_once()

    def test_get_metrics(self, orchestrator):
        """Test metrics collection."""
        # Update some metrics
        orchestrator.metrics["validations_completed"] = 10
        orchestrator.metrics["validations_failed"] = 2
        orchestrator.metrics["cache_hits"] = 5

        metrics = orchestrator.get_metrics()

        assert metrics["validations_completed"] == 10
        assert metrics["validations_failed"] == 2
        assert metrics["cache_hits"] == 5
        assert "active_validations" in metrics
        assert "registered_components" in metrics

    @pytest.mark.asyncio
    async def test_health_check(self, orchestrator):
        """Test health check functionality."""
        await orchestrator.initialize()

        health = await orchestrator.health_check()

        assert health["status"] == "healthy"
        assert "active_validations" in health
        assert "registered_components" in health
        assert "cache_enabled" in health
        assert "metrics" in health

    @pytest.mark.asyncio
    async def test_concurrent_validations(self, orchestrator, event_bus):
        """Test concurrent validation handling."""

        # Setup mock validator with delay
        async def delayed_validator(content, context):
            await asyncio.sleep(0.1)
            return {"safety_level": SafetyLevel.SAFE}

        orchestrator.content_safety_validator = Mock()
        orchestrator.content_safety_validator.validate = delayed_validator

        await orchestrator.initialize()

        # Create multiple validation tasks
        tasks = []
        for i in range(5):
            content = ContentPayload(content_text=f"Test content {i}")
            context = ValidationContext(user_id=f"user_{i}")
            task = orchestrator.validate_content(content, context)
            tasks.append(task)

        # Run all validations concurrently
        results = await asyncio.gather(*tasks)

        # Check that all validations completed
        assert len(results) == 5
        for result in results:
            assert result.status == ValidationStatus.COMPLETED
            assert result.action == ValidationAction.APPROVE

        # Check metrics
        assert orchestrator.metrics["validations_completed"] == 5
