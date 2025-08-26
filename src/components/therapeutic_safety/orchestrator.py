"""
Safety Validation Orchestrator

This module provides the main orchestrator for therapeutic safety content validation,
coordinating all validation components with timeout handling and result caching.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from contextlib import asynccontextmanager

from src.components.gameplay_loop.narrative.events import EventBus, EventType
from .models import (
    ContentPayload, ValidationContext, ValidationResult, TherapeuticContext,
    UserContext, ContentPreferences
)
from .enums import (
    ValidationStatus, ValidationAction, SafetyLevel, ValidationComponent,
    ValidationPriority, CrisisLevel
)
from .events import (
    create_safety_event, create_validation_failure_event, create_validation_timeout_event
)


logger = logging.getLogger(__name__)


class ValidationTimeout(Exception):
    """Exception raised when validation times out."""
    def __init__(self, timeout_ms: int, completed_components: List[ValidationComponent]):
        self.timeout_ms = timeout_ms
        self.completed_components = completed_components
        super().__init__(f"Validation timed out after {timeout_ms}ms")


class ValidationPipeline:
    """Pipeline for coordinating validation components."""
    
    def __init__(self):
        self.components: Dict[ValidationComponent, Callable] = {}
        self.component_timeouts: Dict[ValidationComponent, int] = {}
        self.component_priorities: Dict[ValidationComponent, int] = {}
    
    def register_component(self, component_type: ValidationComponent, 
                          validator: Callable, timeout_ms: int = 50,
                          priority: int = 1) -> None:
        """Register a validation component."""
        self.components[component_type] = validator
        self.component_timeouts[component_type] = timeout_ms
        self.component_priorities[component_type] = priority
    
    def get_ordered_components(self) -> List[ValidationComponent]:
        """Get components ordered by priority."""
        return sorted(
            self.components.keys(),
            key=lambda comp: self.component_priorities.get(comp, 1),
            reverse=True
        )
    
    async def run_component(self, component_type: ValidationComponent,
                           content: ContentPayload, context: ValidationContext) -> Dict[str, Any]:
        """Run a single validation component with timeout."""
        validator = self.components[component_type]
        timeout_ms = self.component_timeouts[component_type]
        
        try:
            result = await asyncio.wait_for(
                validator(content, context),
                timeout=timeout_ms / 1000.0
            )
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Component {component_type.value} timed out after {timeout_ms}ms")
            return {"status": "timeout", "component": component_type.value}


class SafetyValidationOrchestrator:
    """Main orchestrator for safety validation."""
    
    def __init__(self, event_bus: EventBus, cache_manager=None):
        self.event_bus = event_bus
        self.cache_manager = cache_manager
        self.pipeline = ValidationPipeline()
        
        # Validation state
        self.active_validations: Dict[str, ValidationResult] = {}
        self.validation_locks: Dict[str, asyncio.Lock] = {}
        
        # Configuration
        self.default_timeout_ms = 200
        self.max_concurrent_validations = 100
        self.enable_caching = True
        
        # Metrics
        self.metrics = {
            "validations_started": 0,
            "validations_completed": 0,
            "validations_failed": 0,
            "validations_timed_out": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_processing_time_ms": 0.0
        }
        
        # Component managers (will be injected)
        self.content_safety_validator = None
        self.crisis_detection_engine = None
        self.bias_detection_validator = None
        self.therapeutic_alignment_validator = None
    
    async def initialize(self) -> None:
        """Initialize the orchestrator and register components."""
        logger.info("Initializing SafetyValidationOrchestrator...")
        
        # Register validation components (will be implemented)
        if self.content_safety_validator:
            self.pipeline.register_component(
                ValidationComponent.CONTENT_SAFETY,
                self.content_safety_validator.validate,
                timeout_ms=80,
                priority=5
            )
        
        if self.crisis_detection_engine:
            self.pipeline.register_component(
                ValidationComponent.CRISIS_DETECTION,
                self.crisis_detection_engine.assess_crisis,
                timeout_ms=60,
                priority=10  # Highest priority
            )
        
        if self.bias_detection_validator:
            self.pipeline.register_component(
                ValidationComponent.BIAS_DETECTION,
                self.bias_detection_validator.detect_bias,
                timeout_ms=40,
                priority=3
            )
        
        if self.therapeutic_alignment_validator:
            self.pipeline.register_component(
                ValidationComponent.THERAPEUTIC_ALIGNMENT,
                self.therapeutic_alignment_validator.assess_alignment,
                timeout_ms=50,
                priority=4
            )
        
        logger.info(f"Registered {len(self.pipeline.components)} validation components")
    
    async def validate_content(self, content: ContentPayload, 
                             context: ValidationContext) -> ValidationResult:
        """Main validation method with timeout handling."""
        start_time = datetime.utcnow()
        validation_id = context.validation_id
        
        # Check if validation is already in progress
        if validation_id in self.active_validations:
            logger.warning(f"Validation {validation_id} already in progress")
            return self.active_validations[validation_id]
        
        # Check cache first
        if self.enable_caching and self.cache_manager:
            cached_result = await self._check_cache(content, context)
            if cached_result:
                self.metrics["cache_hits"] += 1
                return cached_result
            self.metrics["cache_misses"] += 1
        
        # Create validation result
        result = ValidationResult(
            validation_id=validation_id,
            content_id=content.content_id,
            started_at=start_time
        )
        
        # Add to active validations
        self.active_validations[validation_id] = result
        self.validation_locks[validation_id] = asyncio.Lock()
        
        try:
            # Run validation with timeout
            await self._run_validation_pipeline(content, context, result)
            
            # Finalize result
            result.completed_at = datetime.utcnow()
            result.processing_time_ms = (result.completed_at - start_time).total_seconds() * 1000
            result.status = ValidationStatus.COMPLETED
            
            # Cache result
            if self.enable_caching and self.cache_manager:
                await self._cache_result(content, context, result)
            
            # Publish completion event
            await self._publish_validation_event(context, result)
            
            self.metrics["validations_completed"] += 1
            self._update_average_processing_time(result.processing_time_ms)
            
            logger.debug(f"Validation {validation_id} completed in {result.processing_time_ms:.2f}ms")
            
        except ValidationTimeout as e:
            result.status = ValidationStatus.TIMEOUT
            result.completed_at = datetime.utcnow()
            result.processing_time_ms = e.timeout_ms
            
            # Publish timeout event
            await self._publish_timeout_event(context, result, e)
            
            self.metrics["validations_timed_out"] += 1
            logger.warning(f"Validation {validation_id} timed out after {e.timeout_ms}ms")
            
        except Exception as e:
            result.status = ValidationStatus.FAILED
            result.completed_at = datetime.utcnow()
            
            # Publish failure event
            await self._publish_failure_event(context, result, str(e))
            
            self.metrics["validations_failed"] += 1
            logger.error(f"Validation {validation_id} failed: {e}")
            
        finally:
            # Clean up
            if validation_id in self.active_validations:
                del self.active_validations[validation_id]
            if validation_id in self.validation_locks:
                del self.validation_locks[validation_id]
        
        return result
    
    async def _run_validation_pipeline(self, content: ContentPayload,
                                     context: ValidationContext,
                                     result: ValidationResult) -> None:
        """Run the validation pipeline with timeout."""
        timeout_ms = context.timeout_ms
        components = self.pipeline.get_ordered_components()
        completed_components = []
        
        try:
            # Run components with overall timeout
            async with asyncio.timeout(timeout_ms / 1000.0):
                for component_type in components:
                    try:
                        component_result = await self.pipeline.run_component(
                            component_type, content, context
                        )
                        
                        result.component_results[component_type] = component_result
                        result.validation_components_used.append(component_type)
                        completed_components.append(component_type)
                        
                        # Process component result
                        await self._process_component_result(
                            component_type, component_result, result
                        )
                        
                    except Exception as e:
                        logger.error(f"Component {component_type.value} failed: {e}")
                        result.component_results[component_type] = {
                            "status": "error",
                            "error": str(e)
                        }
            
            # Calculate overall result
            await self._calculate_overall_result(result)
            
        except asyncio.TimeoutError:
            pending_components = [comp for comp in components if comp not in completed_components]
            raise ValidationTimeout(timeout_ms, completed_components)
    
    async def _process_component_result(self, component_type: ValidationComponent,
                                      component_result: Dict[str, Any],
                                      result: ValidationResult) -> None:
        """Process individual component results."""
        if component_type == ValidationComponent.CRISIS_DETECTION:
            crisis_level = component_result.get("crisis_level", CrisisLevel.NONE)
            result.crisis_level = max(result.crisis_level, crisis_level)
            result.crisis_indicators.extend(component_result.get("indicators", []))
            
            if crisis_level >= CrisisLevel.HIGH:
                result.immediate_intervention_needed = True
        
        elif component_type == ValidationComponent.CONTENT_SAFETY:
            safety_level = component_result.get("safety_level", SafetyLevel.SAFE)
            if safety_level.value > result.overall_safety_level.value:
                result.overall_safety_level = safety_level
        
        elif component_type == ValidationComponent.BIAS_DETECTION:
            detected_biases = component_result.get("detected_biases", [])
            result.detected_biases.extend(detected_biases)
            
            bias_scores = component_result.get("bias_scores", {})
            result.bias_scores.update(bias_scores)
        
        elif component_type == ValidationComponent.THERAPEUTIC_ALIGNMENT:
            alignment_score = component_result.get("alignment_score", 0.0)
            result.therapeutic_alignment_score = max(
                result.therapeutic_alignment_score, alignment_score
            )
    
    async def _calculate_overall_result(self, result: ValidationResult) -> None:
        """Calculate overall validation result."""
        # Determine action based on component results
        if result.immediate_intervention_needed or result.crisis_level >= CrisisLevel.HIGH:
            result.action = ValidationAction.ESCALATE
        elif result.overall_safety_level in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]:
            result.action = ValidationAction.REJECT
        elif result.overall_safety_level == SafetyLevel.WARNING:
            result.action = ValidationAction.FLAG_FOR_REVIEW
        elif result.detected_biases or result.therapeutic_alignment_score < 0.5:
            result.action = ValidationAction.MODIFY
        else:
            result.action = ValidationAction.APPROVE
        
        # Calculate confidence score
        component_count = len(result.validation_components_used)
        if component_count > 0:
            # Simple confidence calculation based on component agreement
            result.confidence_score = min(1.0, component_count / len(ValidationComponent))
    
    async def _check_cache(self, content: ContentPayload, 
                          context: ValidationContext) -> Optional[ValidationResult]:
        """Check cache for existing validation result."""
        if not self.cache_manager:
            return None
        
        cache_key = f"validation:{content.content_id}:{hash(content.content_text)}"
        return await self.cache_manager.get(cache_key)
    
    async def _cache_result(self, content: ContentPayload,
                           context: ValidationContext,
                           result: ValidationResult) -> None:
        """Cache validation result."""
        if not self.cache_manager:
            return
        
        cache_key = f"validation:{content.content_id}:{hash(content.content_text)}"
        ttl = timedelta(hours=1)  # Cache for 1 hour
        
        await self.cache_manager.set(cache_key, result, ttl)
    
    async def _publish_validation_event(self, context: ValidationContext,
                                       result: ValidationResult) -> None:
        """Publish validation completion event."""
        event = create_safety_event(
            EventType.SAFETY_CHECK_TRIGGERED,
            context.session_id or "",
            context.user_id,
            result.content_id,
            result.action,
            result.overall_safety_level,
            result.confidence_score
        )
        await self.event_bus.publish(event)
    
    async def _publish_timeout_event(self, context: ValidationContext,
                                    result: ValidationResult,
                                    timeout_error: ValidationTimeout) -> None:
        """Publish validation timeout event."""
        event = create_validation_timeout_event(
            context.session_id or "",
            context.user_id,
            result.content_id,
            result.validation_id,
            timeout_error.timeout_ms,
            timeout_error.completed_components
        )
        await self.event_bus.publish(event)
    
    async def _publish_failure_event(self, context: ValidationContext,
                                    result: ValidationResult,
                                    error_message: str) -> None:
        """Publish validation failure event."""
        event = create_validation_failure_event(
            EventType.SAFETY_CONCERN_DETECTED,
            context.session_id or "",
            context.user_id,
            result.content_id,
            result.validation_id,
            error_message
        )
        await self.event_bus.publish(event)
    
    def _update_average_processing_time(self, processing_time_ms: float) -> None:
        """Update average processing time metric."""
        current_avg = self.metrics["average_processing_time_ms"]
        completed_count = self.metrics["validations_completed"]
        
        if completed_count == 1:
            self.metrics["average_processing_time_ms"] = processing_time_ms
        else:
            # Running average calculation
            self.metrics["average_processing_time_ms"] = (
                (current_avg * (completed_count - 1) + processing_time_ms) / completed_count
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics."""
        return {
            **self.metrics,
            "active_validations": len(self.active_validations),
            "registered_components": len(self.pipeline.components)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            "status": "healthy",
            "active_validations": len(self.active_validations),
            "registered_components": len(self.pipeline.components),
            "cache_enabled": self.enable_caching,
            "metrics": self.get_metrics()
        }
