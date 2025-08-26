"""
Therapeutic Safety Component

This module provides the main TTA component for therapeutic safety content validation,
integrating with the existing TTA component system and narrative engine.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.components.base import Component
from src.components.gameplay_loop.narrative.events import EventBus
from src.components.therapeutic_safety import (
    SafetyValidationOrchestrator,
    ContentSafetyValidator,
    CrisisDetectionEngine,
    BiasDetectionValidator,
    TherapeuticAlignmentValidator,
    ValidationCache,
    SafetyResultCache,
    ContentPayload,
    ValidationContext,
    ValidationResult
)


logger = logging.getLogger(__name__)


class TherapeuticSafetyComponent(Component):
    """Main component for therapeutic safety content validation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.component_name = "therapeutic_safety"
        
        # Core components
        self.orchestrator: Optional[SafetyValidationOrchestrator] = None
        self.content_validator: Optional[ContentSafetyValidator] = None
        self.crisis_detector: Optional[CrisisDetectionEngine] = None
        self.bias_detector: Optional[BiasDetectionValidator] = None
        self.alignment_validator: Optional[TherapeuticAlignmentValidator] = None
        
        # Caching
        self.validation_cache: Optional[ValidationCache] = None
        self.safety_cache: Optional[SafetyResultCache] = None
        
        # Event system
        self.event_bus: Optional[EventBus] = None
        
        # Configuration
        self.safety_config = config.get("therapeutic_safety", {})
        self.validation_config = self.safety_config.get("validation", {})
        self.cache_config = self.safety_config.get("cache", {})
        
        # Component state
        self.is_initialized = False
        self.validation_count = 0
        self.last_validation_time: Optional[datetime] = None
    
    async def initialize(self) -> None:
        """Initialize the therapeutic safety component."""
        logger.info("Initializing TherapeuticSafetyComponent...")
        
        try:
            # Get dependencies
            await self._setup_dependencies()
            
            # Initialize validation components
            await self._initialize_validators()
            
            # Initialize caching
            await self._initialize_caching()
            
            # Initialize orchestrator
            await self._initialize_orchestrator()
            
            # Register with event system
            await self._register_event_handlers()
            
            self.is_initialized = True
            logger.info("TherapeuticSafetyComponent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TherapeuticSafetyComponent: {e}")
            raise
    
    async def _setup_dependencies(self) -> None:
        """Set up component dependencies."""
        # Get event bus from narrative engine or create new one
        try:
            # Try to get existing event bus from gameplay loop component
            gameplay_component = self.get_dependency("gameplay_loop")
            if gameplay_component and hasattr(gameplay_component, 'event_bus'):
                self.event_bus = gameplay_component.event_bus
                logger.info("Using existing event bus from gameplay loop")
            else:
                # Create new event bus if not available
                self.event_bus = EventBus()
                logger.info("Created new event bus for therapeutic safety")
        except Exception as e:
            logger.warning(f"Could not get event bus dependency: {e}")
            self.event_bus = EventBus()
    
    async def _initialize_validators(self) -> None:
        """Initialize validation components."""
        logger.info("Initializing validation components...")
        
        # Initialize content safety validator
        self.content_validator = ContentSafetyValidator()
        logger.debug("ContentSafetyValidator initialized")
        
        # Initialize crisis detection engine
        self.crisis_detector = CrisisDetectionEngine()
        logger.debug("CrisisDetectionEngine initialized")
        
        # Initialize bias detection validator
        self.bias_detector = BiasDetectionValidator()
        logger.debug("BiasDetectionValidator initialized")
        
        # Initialize therapeutic alignment validator
        self.alignment_validator = TherapeuticAlignmentValidator()
        logger.debug("TherapeuticAlignmentValidator initialized")
    
    async def _initialize_caching(self) -> None:
        """Initialize caching components."""
        if not self.cache_config.get("enabled", True):
            logger.info("Validation caching disabled")
            return
        
        try:
            # Get Redis client from dependencies
            redis_client = None
            try:
                redis_component = self.get_dependency("redis")
                if redis_component:
                    redis_client = redis_component.client
            except Exception as e:
                logger.warning(f"Could not get Redis dependency: {e}")
            
            # Initialize validation cache
            cache_prefix = self.cache_config.get("key_prefix", "tta:safety:validation")
            self.validation_cache = ValidationCache(
                redis_client=redis_client,
                key_prefix=cache_prefix
            )
            
            # Initialize safety result cache
            self.safety_cache = SafetyResultCache(self.validation_cache)
            
            logger.info("Validation caching initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize caching: {e}")
            # Continue without caching
            self.validation_cache = None
            self.safety_cache = None
    
    async def _initialize_orchestrator(self) -> None:
        """Initialize the safety validation orchestrator."""
        logger.info("Initializing SafetyValidationOrchestrator...")
        
        # Create orchestrator
        self.orchestrator = SafetyValidationOrchestrator(
            event_bus=self.event_bus,
            cache_manager=self.validation_cache
        )
        
        # Inject validators
        self.orchestrator.content_safety_validator = self.content_validator
        self.orchestrator.crisis_detection_engine = self.crisis_detector
        self.orchestrator.bias_detection_validator = self.bias_detector
        self.orchestrator.therapeutic_alignment_validator = self.alignment_validator
        
        # Configure orchestrator
        orchestrator_config = self.validation_config.get("orchestrator", {})
        self.orchestrator.default_timeout_ms = orchestrator_config.get("timeout_ms", 200)
        self.orchestrator.max_concurrent_validations = orchestrator_config.get("max_concurrent", 100)
        self.orchestrator.enable_caching = self.cache_config.get("enabled", True)
        
        # Initialize orchestrator
        await self.orchestrator.initialize()
        
        logger.info("SafetyValidationOrchestrator initialized")
    
    async def _register_event_handlers(self) -> None:
        """Register event handlers with the event bus."""
        if not self.event_bus:
            return
        
        # Register handlers for safety-related events
        # These would be implemented based on specific event handling needs
        logger.debug("Event handlers registered")
    
    async def validate_content(self, content: ContentPayload, 
                             context: ValidationContext) -> ValidationResult:
        """Main method to validate content for therapeutic safety."""
        if not self.is_initialized:
            raise RuntimeError("TherapeuticSafetyComponent not initialized")
        
        if not self.orchestrator:
            raise RuntimeError("SafetyValidationOrchestrator not available")
        
        try:
            # Update validation metrics
            self.validation_count += 1
            self.last_validation_time = datetime.utcnow()
            
            # Perform validation
            result = await self.orchestrator.validate_content(content, context)
            
            logger.debug(f"Content validation completed: {result.validation_id}")
            return result
            
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            raise
    
    async def validate_user_input(self, user_input: str, user_id: str, 
                                session_id: Optional[str] = None,
                                **context_kwargs) -> ValidationResult:
        """Convenience method to validate user input."""
        # Create content payload
        content = ContentPayload(
            content_text=user_input,
            content_type="user_input",
            source="user_generated"
        )
        
        # Create validation context
        context = ValidationContext(
            user_id=user_id,
            session_id=session_id,
            **context_kwargs
        )
        
        return await self.validate_content(content, context)
    
    async def validate_generated_content(self, generated_content: str, 
                                       content_type: str = "ai_generated",
                                       user_id: str = "",
                                       session_id: Optional[str] = None,
                                       **context_kwargs) -> ValidationResult:
        """Convenience method to validate AI-generated content."""
        # Create content payload
        content = ContentPayload(
            content_text=generated_content,
            content_type=content_type,
            source="ai_generated"
        )
        
        # Create validation context
        context = ValidationContext(
            user_id=user_id,
            session_id=session_id,
            **context_kwargs
        )
        
        return await self.validate_content(content, context)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform component health check."""
        health_status = {
            "component": "therapeutic_safety",
            "status": "healthy" if self.is_initialized else "not_initialized",
            "initialized": self.is_initialized,
            "validation_count": self.validation_count,
            "last_validation": self.last_validation_time.isoformat() if self.last_validation_time else None
        }
        
        # Check orchestrator health
        if self.orchestrator:
            orchestrator_health = await self.orchestrator.health_check()
            health_status["orchestrator"] = orchestrator_health
        
        # Check cache health
        if self.validation_cache:
            cache_health = await self.validation_cache.health_check()
            health_status["cache"] = cache_health
        
        # Check validator metrics
        validator_metrics = {}
        if self.content_validator:
            validator_metrics["content_safety"] = self.content_validator.get_metrics()
        if self.crisis_detector:
            validator_metrics["crisis_detection"] = self.crisis_detector.get_metrics()
        if self.bias_detector:
            validator_metrics["bias_detection"] = self.bias_detector.get_metrics()
        if self.alignment_validator:
            validator_metrics["therapeutic_alignment"] = self.alignment_validator.get_metrics()
        
        health_status["validator_metrics"] = validator_metrics
        
        return health_status
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get component metrics."""
        metrics = {
            "component": "therapeutic_safety",
            "validation_count": self.validation_count,
            "last_validation": self.last_validation_time.isoformat() if self.last_validation_time else None,
            "is_initialized": self.is_initialized
        }
        
        # Add orchestrator metrics
        if self.orchestrator:
            metrics["orchestrator"] = self.orchestrator.get_metrics()
        
        # Add cache metrics
        if self.validation_cache:
            metrics["cache"] = self.validation_cache.get_stats()
        
        # Add validator metrics
        validator_metrics = {}
        if self.content_validator:
            validator_metrics["content_safety"] = self.content_validator.get_metrics()
        if self.crisis_detector:
            validator_metrics["crisis_detection"] = self.crisis_detector.get_metrics()
        if self.bias_detector:
            validator_metrics["bias_detection"] = self.bias_detector.get_metrics()
        if self.alignment_validator:
            validator_metrics["therapeutic_alignment"] = self.alignment_validator.get_metrics()
        
        metrics["validators"] = validator_metrics
        
        return metrics
    
    async def shutdown(self) -> None:
        """Shutdown the component."""
        logger.info("Shutting down TherapeuticSafetyComponent...")
        
        # Clean up resources
        if self.orchestrator:
            # Clear active validations
            self.orchestrator.active_validations.clear()
            self.orchestrator.validation_locks.clear()
        
        self.is_initialized = False
        logger.info("TherapeuticSafetyComponent shutdown complete")
    
    def get_service(self) -> 'TherapeuticSafetyService':
        """Get the therapeutic safety service interface."""
        return TherapeuticSafetyService(self)


class TherapeuticSafetyService:
    """Service interface for therapeutic safety validation."""
    
    def __init__(self, component: TherapeuticSafetyComponent):
        self.component = component
    
    async def validate_content(self, content: ContentPayload, 
                             context: ValidationContext) -> ValidationResult:
        """Validate content for therapeutic safety."""
        return await self.component.validate_content(content, context)
    
    async def validate_user_input(self, user_input: str, user_id: str,
                                session_id: Optional[str] = None,
                                **context_kwargs) -> ValidationResult:
        """Validate user input."""
        return await self.component.validate_user_input(
            user_input, user_id, session_id, **context_kwargs
        )
    
    async def validate_generated_content(self, generated_content: str,
                                       content_type: str = "ai_generated",
                                       user_id: str = "",
                                       session_id: Optional[str] = None,
                                       **context_kwargs) -> ValidationResult:
        """Validate AI-generated content."""
        return await self.component.validate_generated_content(
            generated_content, content_type, user_id, session_id, **context_kwargs
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get validation metrics."""
        return await self.component.get_metrics()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return await self.component.health_check()
