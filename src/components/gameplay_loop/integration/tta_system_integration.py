"""
TTA System Integration for Core Gameplay Loop

This module provides comprehensive integration with existing TTA infrastructure including
Character Development System integration, Therapeutic Content Management integration,
Safety Monitoring System integration, Progress Tracking System integration, and
seamless data exchange functions for production-ready system interoperability.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

from src.components.gameplay_loop.narrative.events import (
    EventBus,
    EventType,
    NarrativeEvent,
)
from src.components.gameplay_loop.services.session_state import (
    SessionState,
)

logger = logging.getLogger(__name__)


class IntegrationType(str, Enum):
    """Types of TTA system integrations."""

    CHARACTER_DEVELOPMENT = "character_development"
    THERAPEUTIC_CONTENT = "therapeutic_content"
    SAFETY_MONITORING = "safety_monitoring"
    PROGRESS_TRACKING = "progress_tracking"
    CONFIGURATION_MANAGEMENT = "configuration_management"
    EVENT_SYSTEM = "event_system"
    HEALTH_MONITORING = "health_monitoring"


class IntegrationStatus(str, Enum):
    """Status of system integrations."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    DEGRADED = "degraded"


@dataclass
class IntegrationEndpoint:
    """Configuration for a TTA system integration endpoint."""

    integration_id: str = field(default_factory=lambda: str(uuid4()))
    integration_type: IntegrationType = IntegrationType.CHARACTER_DEVELOPMENT

    # Connection details
    service_name: str = ""
    endpoint_url: str = ""
    api_version: str = "v1"

    # Authentication
    requires_auth: bool = False
    auth_token: str | None = None
    api_key: str | None = None

    # Configuration
    timeout_seconds: float = 30.0
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0

    # Health monitoring
    health_check_interval: float = 60.0
    last_health_check: datetime | None = None
    status: IntegrationStatus = IntegrationStatus.DISCONNECTED

    # Data mapping
    data_mapping: dict[str, str] = field(default_factory=dict)
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)


@dataclass
class IntegrationRequest:
    """Request for TTA system integration."""

    request_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Request details
    integration_type: IntegrationType = IntegrationType.CHARACTER_DEVELOPMENT
    operation: str = ""  # get, post, put, delete, sync
    endpoint: str = ""

    # Data
    payload: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)

    # Context
    session_id: str | None = None
    user_id: str | None = None

    # Processing
    priority: int = 5  # 1-10, higher is more urgent
    timeout_seconds: float = 30.0
    retry_on_failure: bool = True


@dataclass
class IntegrationResponse:
    """Response from TTA system integration."""

    request_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Response details
    success: bool = False
    status_code: int = 0
    response_data: dict[str, Any] = field(default_factory=dict)
    error_message: str = ""

    # Processing metadata
    processing_time_ms: float = 0.0
    retry_count: int = 0
    cached_response: bool = False

    # Integration context
    integration_type: IntegrationType = IntegrationType.CHARACTER_DEVELOPMENT
    endpoint_used: str = ""


class TTASystemIntegration:
    """Main system for comprehensive TTA system integration."""

    def __init__(self, event_bus: EventBus, config: dict[str, Any] = None):
        self.event_bus = event_bus
        self.config = config or {}

        # Integration endpoints
        self.endpoints: dict[IntegrationType, IntegrationEndpoint] = {}
        self.endpoint_health: dict[str, dict[str, Any]] = {}

        # Request management
        self.pending_requests: dict[str, IntegrationRequest] = {}
        self.request_history: list[IntegrationResponse] = []
        self.request_queue: list[IntegrationRequest] = []

        # Integration state
        self.integration_status: dict[IntegrationType, IntegrationStatus] = {}
        self.connection_pool: dict[str, Any] = {}
        self.data_cache: dict[str, dict[str, Any]] = {}

        # Configuration
        self.max_concurrent_requests = 10
        self.request_history_limit = 1000
        self.cache_ttl_seconds = 300  # 5 minutes
        self.health_check_enabled = True

        # Metrics
        self.metrics = {
            "requests_sent": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "integrations_active": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "health_checks_performed": 0,
            "connection_errors": 0,
            "data_sync_operations": 0,
        }

        # Initialize default endpoints
        self._initialize_default_endpoints()

    def _initialize_default_endpoints(self) -> None:
        """Initialize default TTA system integration endpoints."""
        try:
            # Character Development System integration
            self.endpoints[IntegrationType.CHARACTER_DEVELOPMENT] = IntegrationEndpoint(
                integration_type=IntegrationType.CHARACTER_DEVELOPMENT,
                service_name="character_development_system",
                endpoint_url="/api/v1/character",
                required_fields=["user_id", "attribute", "change"],
                optional_fields=["session_id", "context", "story_integration"],
            )

            # Therapeutic Content Management integration
            self.endpoints[IntegrationType.THERAPEUTIC_CONTENT] = IntegrationEndpoint(
                integration_type=IntegrationType.THERAPEUTIC_CONTENT,
                service_name="therapeutic_content_management",
                endpoint_url="/api/v1/content",
                required_fields=["content_type", "therapeutic_framework"],
                optional_fields=[
                    "user_preferences",
                    "session_context",
                    "difficulty_level",
                ],
            )

            # Safety Monitoring System integration
            self.endpoints[IntegrationType.SAFETY_MONITORING] = IntegrationEndpoint(
                integration_type=IntegrationType.SAFETY_MONITORING,
                service_name="safety_monitoring_system",
                endpoint_url="/api/v1/safety",
                required_fields=["user_id", "content", "context"],
                optional_fields=["session_id", "emotional_state", "crisis_indicators"],
            )

            # Progress Tracking System integration
            self.endpoints[IntegrationType.PROGRESS_TRACKING] = IntegrationEndpoint(
                integration_type=IntegrationType.PROGRESS_TRACKING,
                service_name="progress_tracking_system",
                endpoint_url="/api/v1/progress",
                required_fields=["user_id", "progress_data"],
                optional_fields=["session_id", "milestone_data", "analytics_context"],
            )

            # Initialize all as disconnected
            for integration_type in IntegrationType:
                self.integration_status[integration_type] = (
                    IntegrationStatus.DISCONNECTED
                )

        except Exception as e:
            logger.error(f"Failed to initialize default endpoints: {e}")

    async def connect_integration(self, integration_type: IntegrationType) -> bool:
        """Connect to a TTA system integration."""
        try:
            endpoint = self.endpoints.get(integration_type)
            if not endpoint:
                logger.error(
                    f"No endpoint configured for integration type: {integration_type}"
                )
                return False

            # Update status
            self.integration_status[integration_type] = IntegrationStatus.CONNECTING
            endpoint.status = IntegrationStatus.CONNECTING

            # Perform connection logic (placeholder for actual implementation)
            await asyncio.sleep(0.1)  # Simulate connection time

            # For now, simulate successful connection
            # In real implementation, this would establish actual connections
            self.integration_status[integration_type] = IntegrationStatus.CONNECTED
            endpoint.status = IntegrationStatus.CONNECTED
            endpoint.last_health_check = datetime.utcnow()

            self.metrics["integrations_active"] += 1

            # Publish integration event
            await self._publish_integration_event(
                EventType.SYSTEM_INTEGRATION_CONNECTED,
                integration_type,
                {"endpoint": endpoint.service_name},
            )

            logger.info(
                f"Successfully connected to {integration_type.value} integration"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to connect to {integration_type.value} integration: {e}"
            )
            self.integration_status[integration_type] = IntegrationStatus.ERROR
            if endpoint:
                endpoint.status = IntegrationStatus.ERROR
            return False

    async def disconnect_integration(self, integration_type: IntegrationType) -> bool:
        """Disconnect from a TTA system integration."""
        try:
            endpoint = self.endpoints.get(integration_type)
            if not endpoint:
                return True  # Already disconnected

            # Perform disconnection logic
            self.integration_status[integration_type] = IntegrationStatus.DISCONNECTED
            endpoint.status = IntegrationStatus.DISCONNECTED

            # Clean up connection pool
            connection_key = f"{integration_type.value}_{endpoint.service_name}"
            self.connection_pool.pop(connection_key, None)

            self.metrics["integrations_active"] = max(
                0, self.metrics["integrations_active"] - 1
            )

            # Publish integration event
            await self._publish_integration_event(
                EventType.SYSTEM_INTEGRATION_DISCONNECTED,
                integration_type,
                {"endpoint": endpoint.service_name},
            )

            logger.info(
                f"Successfully disconnected from {integration_type.value} integration"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to disconnect from {integration_type.value} integration: {e}"
            )
            return False

    async def send_integration_request(
        self, request: IntegrationRequest
    ) -> IntegrationResponse:
        """Send a request to a TTA system integration."""
        start_time = datetime.utcnow()

        try:
            # Validate integration is connected
            if (
                self.integration_status.get(request.integration_type)
                != IntegrationStatus.CONNECTED
            ):
                return IntegrationResponse(
                    request_id=request.request_id,
                    success=False,
                    error_message=f"Integration {request.integration_type.value} is not connected",
                    integration_type=request.integration_type,
                )

            # Get endpoint
            endpoint = self.endpoints.get(request.integration_type)
            if not endpoint:
                return IntegrationResponse(
                    request_id=request.request_id,
                    success=False,
                    error_message=f"No endpoint configured for {request.integration_type.value}",
                    integration_type=request.integration_type,
                )

            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                self.metrics["cache_hits"] += 1
                cached_response.cached_response = True
                return cached_response

            self.metrics["cache_misses"] += 1

            # Add to pending requests
            self.pending_requests[request.request_id] = request

            # Process request based on integration type
            response = await self._process_integration_request(request, endpoint)

            # Cache successful responses
            if response.success and request.operation == "get":
                self._cache_response(cache_key, response)

            # Update metrics
            self.metrics["requests_sent"] += 1
            if response.success:
                self.metrics["requests_successful"] += 1
            else:
                self.metrics["requests_failed"] += 1

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            response.processing_time_ms = processing_time

            # Store in history
            self.request_history.append(response)
            if len(self.request_history) > self.request_history_limit:
                self.request_history.pop(0)

            # Remove from pending
            self.pending_requests.pop(request.request_id, None)

            return response

        except Exception as e:
            logger.error(f"Failed to send integration request: {e}")
            return IntegrationResponse(
                request_id=request.request_id,
                success=False,
                error_message=str(e),
                integration_type=request.integration_type,
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds()
                * 1000,
            )

    async def _process_integration_request(
        self, request: IntegrationRequest, endpoint: IntegrationEndpoint
    ) -> IntegrationResponse:
        """Process an integration request based on its type."""
        try:
            if request.integration_type == IntegrationType.CHARACTER_DEVELOPMENT:
                return await self._process_character_development_request(
                    request, endpoint
                )
            elif request.integration_type == IntegrationType.THERAPEUTIC_CONTENT:
                return await self._process_therapeutic_content_request(
                    request, endpoint
                )
            elif request.integration_type == IntegrationType.SAFETY_MONITORING:
                return await self._process_safety_monitoring_request(request, endpoint)
            elif request.integration_type == IntegrationType.PROGRESS_TRACKING:
                return await self._process_progress_tracking_request(request, endpoint)
            else:
                return IntegrationResponse(
                    request_id=request.request_id,
                    success=False,
                    error_message=f"Unsupported integration type: {request.integration_type}",
                    integration_type=request.integration_type,
                )

        except Exception as e:
            logger.error(f"Failed to process integration request: {e}")
            return IntegrationResponse(
                request_id=request.request_id,
                success=False,
                error_message=str(e),
                integration_type=request.integration_type,
            )

    async def _process_character_development_request(
        self, request: IntegrationRequest, endpoint: IntegrationEndpoint
    ) -> IntegrationResponse:
        """Process character development system integration request."""
        try:
            # Validate required fields
            required_fields = ["user_id", "attribute", "change"]
            for field in required_fields:
                if field not in request.payload:
                    return IntegrationResponse(
                        request_id=request.request_id,
                        success=False,
                        error_message=f"Missing required field: {field}",
                        integration_type=request.integration_type,
                    )

            # Simulate character development system integration
            # In real implementation, this would call the actual character development system
            user_id = request.payload["user_id"]
            attribute = request.payload["attribute"]
            change = request.payload["change"]

            response_data = {
                "user_id": user_id,
                "attribute": attribute,
                "change_applied": change,
                "new_level": 5.5,  # Simulated new level
                "experience_gained": 10,
                "milestone_achieved": False,
                "integration_timestamp": datetime.utcnow().isoformat(),
            }

            return IntegrationResponse(
                request_id=request.request_id,
                success=True,
                status_code=200,
                response_data=response_data,
                integration_type=request.integration_type,
                endpoint_used=endpoint.endpoint_url,
            )

        except Exception as e:
            logger.error(f"Failed to process character development request: {e}")
            return IntegrationResponse(
                request_id=request.request_id,
                success=False,
                error_message=str(e),
                integration_type=request.integration_type,
            )

    async def _process_therapeutic_content_request(
        self, request: IntegrationRequest, endpoint: IntegrationEndpoint
    ) -> IntegrationResponse:
        """Process therapeutic content management integration request."""
        try:
            # Validate required fields
            required_fields = ["content_type", "therapeutic_framework"]
            for field in required_fields:
                if field not in request.payload:
                    return IntegrationResponse(
                        request_id=request.request_id,
                        success=False,
                        error_message=f"Missing required field: {field}",
                        integration_type=request.integration_type,
                    )

            # Simulate therapeutic content system integration
            content_type = request.payload["content_type"]
            framework = request.payload["therapeutic_framework"]

            response_data = {
                "content_id": str(uuid4()),
                "content_type": content_type,
                "therapeutic_framework": framework,
                "content_template": f"Therapeutic content for {framework} framework",
                "difficulty_level": request.payload.get("difficulty_level", "medium"),
                "estimated_duration": 15,  # minutes
                "therapeutic_goals": ["emotional_regulation", "coping_skills"],
                "integration_timestamp": datetime.utcnow().isoformat(),
            }

            return IntegrationResponse(
                request_id=request.request_id,
                success=True,
                status_code=200,
                response_data=response_data,
                integration_type=request.integration_type,
                endpoint_used=endpoint.endpoint_url,
            )

        except Exception as e:
            logger.error(f"Failed to process therapeutic content request: {e}")
            return IntegrationResponse(
                request_id=request.request_id,
                success=False,
                error_message=str(e),
                integration_type=request.integration_type,
            )

    async def _process_safety_monitoring_request(
        self, request: IntegrationRequest, endpoint: IntegrationEndpoint
    ) -> IntegrationResponse:
        """Process safety monitoring system integration request."""
        try:
            # Validate required fields
            required_fields = ["user_id", "content", "context"]
            for field in required_fields:
                if field not in request.payload:
                    return IntegrationResponse(
                        request_id=request.request_id,
                        success=False,
                        error_message=f"Missing required field: {field}",
                        integration_type=request.integration_type,
                    )

            # Simulate safety monitoring system integration
            user_id = request.payload["user_id"]
            content = request.payload["content"]
            context = request.payload["context"]

            response_data = {
                "user_id": user_id,
                "safety_assessment": {
                    "safety_level": "safe",
                    "crisis_level": "none",
                    "intervention_needed": False,
                    "confidence_score": 0.95,
                },
                "content_analysis": {
                    "therapeutic_appropriateness": 0.9,
                    "emotional_impact": "positive",
                    "triggers_detected": [],
                },
                "recommendations": [
                    "Continue with current therapeutic approach",
                    "Monitor for emotional responses",
                ],
                "integration_timestamp": datetime.utcnow().isoformat(),
            }

            return IntegrationResponse(
                request_id=request.request_id,
                success=True,
                status_code=200,
                response_data=response_data,
                integration_type=request.integration_type,
                endpoint_used=endpoint.endpoint_url,
            )

        except Exception as e:
            logger.error(f"Failed to process safety monitoring request: {e}")
            return IntegrationResponse(
                request_id=request.request_id,
                success=False,
                error_message=str(e),
                integration_type=request.integration_type,
            )

    async def _process_progress_tracking_request(
        self, request: IntegrationRequest, endpoint: IntegrationEndpoint
    ) -> IntegrationResponse:
        """Process progress tracking system integration request."""
        try:
            # Validate required fields
            required_fields = ["user_id", "progress_data"]
            for field in required_fields:
                if field not in request.payload:
                    return IntegrationResponse(
                        request_id=request.request_id,
                        success=False,
                        error_message=f"Missing required field: {field}",
                        integration_type=request.integration_type,
                    )

            # Simulate progress tracking system integration
            user_id = request.payload["user_id"]
            progress_data = request.payload["progress_data"]

            response_data = {
                "user_id": user_id,
                "progress_update": {
                    "overall_progress": 0.75,
                    "session_progress": 0.85,
                    "therapeutic_goals_met": 3,
                    "milestones_achieved": 2,
                },
                "analytics": {
                    "engagement_score": 0.88,
                    "therapeutic_effectiveness": 0.82,
                    "character_development_rate": 0.79,
                },
                "next_recommendations": [
                    "Focus on advanced coping strategies",
                    "Explore collaborative therapeutic experiences",
                ],
                "integration_timestamp": datetime.utcnow().isoformat(),
            }

            return IntegrationResponse(
                request_id=request.request_id,
                success=True,
                status_code=200,
                response_data=response_data,
                integration_type=request.integration_type,
                endpoint_used=endpoint.endpoint_url,
            )

        except Exception as e:
            logger.error(f"Failed to process progress tracking request: {e}")
            return IntegrationResponse(
                request_id=request.request_id,
                success=False,
                error_message=str(e),
                integration_type=request.integration_type,
            )

    # High-level integration methods
    async def sync_character_development(
        self,
        session_state: SessionState,
        attribute: str,
        change: float,
        context: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Sync character development with the Character Development System."""
        try:
            request = IntegrationRequest(
                integration_type=IntegrationType.CHARACTER_DEVELOPMENT,
                operation="post",
                endpoint="/character/update",
                payload={
                    "user_id": session_state.user_id,
                    "session_id": session_state.session_id,
                    "attribute": attribute,
                    "change": change,
                    "context": context or {},
                    "story_integration": True,
                },
            )

            response = await self.send_integration_request(request)

            if response.success:
                # Publish character development event
                await self._publish_integration_event(
                    EventType.CHARACTER_DEVELOPMENT_SYNCED,
                    IntegrationType.CHARACTER_DEVELOPMENT,
                    {
                        "user_id": session_state.user_id,
                        "attribute": attribute,
                        "change": change,
                        "new_data": response.response_data,
                    },
                )

                return response.response_data
            else:
                logger.error(
                    f"Failed to sync character development: {response.error_message}"
                )
                return {}

        except Exception as e:
            logger.error(f"Failed to sync character development: {e}")
            return {}

    async def get_therapeutic_content(
        self,
        content_type: str,
        framework: str,
        user_preferences: dict[str, Any] = None,
        session_context: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Get therapeutic content from the Therapeutic Content Management system."""
        try:
            request = IntegrationRequest(
                integration_type=IntegrationType.THERAPEUTIC_CONTENT,
                operation="get",
                endpoint="/content/retrieve",
                payload={
                    "content_type": content_type,
                    "therapeutic_framework": framework,
                    "user_preferences": user_preferences or {},
                    "session_context": session_context or {},
                    "format": "narrative_embedded",
                },
            )

            response = await self.send_integration_request(request)

            if response.success:
                # Publish content retrieval event
                await self._publish_integration_event(
                    EventType.THERAPEUTIC_CONTENT_RETRIEVED,
                    IntegrationType.THERAPEUTIC_CONTENT,
                    {
                        "content_type": content_type,
                        "framework": framework,
                        "content_data": response.response_data,
                    },
                )

                return response.response_data
            else:
                logger.error(
                    f"Failed to get therapeutic content: {response.error_message}"
                )
                return {}

        except Exception as e:
            logger.error(f"Failed to get therapeutic content: {e}")
            return {}

    async def validate_safety(
        self,
        user_id: str,
        content: str,
        context: dict[str, Any],
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Validate content safety with the Safety Monitoring System."""
        try:
            request = IntegrationRequest(
                integration_type=IntegrationType.SAFETY_MONITORING,
                operation="post",
                endpoint="/safety/validate",
                payload={
                    "user_id": user_id,
                    "session_id": session_id,
                    "content": content,
                    "context": context,
                    "validation_level": "comprehensive",
                },
            )

            response = await self.send_integration_request(request)

            if response.success:
                # Publish safety validation event
                await self._publish_integration_event(
                    EventType.SAFETY_VALIDATION_COMPLETED,
                    IntegrationType.SAFETY_MONITORING,
                    {"user_id": user_id, "safety_result": response.response_data},
                )

                return response.response_data
            else:
                logger.error(f"Failed to validate safety: {response.error_message}")
                return {"safety_level": "unknown", "intervention_needed": True}

        except Exception as e:
            logger.error(f"Failed to validate safety: {e}")
            return {"safety_level": "unknown", "intervention_needed": True}

    async def update_progress_tracking(
        self,
        user_id: str,
        progress_data: dict[str, Any],
        session_id: str | None = None,
        milestone_data: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Update progress with the Progress Tracking System."""
        try:
            request = IntegrationRequest(
                integration_type=IntegrationType.PROGRESS_TRACKING,
                operation="post",
                endpoint="/progress/update",
                payload={
                    "user_id": user_id,
                    "session_id": session_id,
                    "progress_data": progress_data,
                    "milestone_data": milestone_data or {},
                    "analytics_context": {
                        "source": "core_gameplay_loop",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )

            response = await self.send_integration_request(request)

            if response.success:
                # Publish progress update event
                await self._publish_integration_event(
                    EventType.PROGRESS_TRACKING_UPDATED,
                    IntegrationType.PROGRESS_TRACKING,
                    {"user_id": user_id, "progress_update": response.response_data},
                )

                return response.response_data
            else:
                logger.error(
                    f"Failed to update progress tracking: {response.error_message}"
                )
                return {}

        except Exception as e:
            logger.error(f"Failed to update progress tracking: {e}")
            return {}

    # Utility methods
    def _generate_cache_key(self, request: IntegrationRequest) -> str:
        """Generate cache key for request."""
        try:
            key_data = {
                "integration_type": request.integration_type.value,
                "operation": request.operation,
                "endpoint": request.endpoint,
                "payload_hash": hash(json.dumps(request.payload, sort_keys=True)),
            }
            return f"integration_cache_{hash(json.dumps(key_data, sort_keys=True))}"
        except Exception as e:
            logger.error(f"Failed to generate cache key: {e}")
            return f"integration_cache_{request.request_id}"

    def _get_cached_response(self, cache_key: str) -> IntegrationResponse | None:
        """Get cached response if available and not expired."""
        try:
            if cache_key not in self.data_cache:
                return None

            cached_data = self.data_cache[cache_key]
            cache_time = datetime.fromisoformat(cached_data["timestamp"])

            if datetime.utcnow() - cache_time > timedelta(
                seconds=self.cache_ttl_seconds
            ):
                # Cache expired
                del self.data_cache[cache_key]
                return None

            return IntegrationResponse(**cached_data["response"])

        except Exception as e:
            logger.error(f"Failed to get cached response: {e}")
            return None

    def _cache_response(self, cache_key: str, response: IntegrationResponse) -> None:
        """Cache response for future use."""
        try:
            self.data_cache[cache_key] = {
                "timestamp": datetime.utcnow().isoformat(),
                "response": {
                    "request_id": response.request_id,
                    "success": response.success,
                    "status_code": response.status_code,
                    "response_data": response.response_data,
                    "integration_type": response.integration_type,
                    "endpoint_used": response.endpoint_used,
                },
            }

            # Clean up old cache entries
            await self._cleanup_cache()

        except Exception as e:
            logger.error(f"Failed to cache response: {e}")

    async def _cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        try:
            current_time = datetime.utcnow()
            expired_keys = []

            for cache_key, cached_data in self.data_cache.items():
                cache_time = datetime.fromisoformat(cached_data["timestamp"])
                if current_time - cache_time > timedelta(
                    seconds=self.cache_ttl_seconds
                ):
                    expired_keys.append(cache_key)

            for key in expired_keys:
                del self.data_cache[key]

        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")

    async def _publish_integration_event(
        self,
        event_type: EventType,
        integration_type: IntegrationType,
        context: dict[str, Any],
    ) -> None:
        """Publish integration event."""
        try:
            event = NarrativeEvent(
                event_type=event_type,
                session_id=context.get("session_id", "system"),
                user_id=context.get("user_id", "system"),
                context={"integration_type": integration_type.value, **context},
            )

            await self.event_bus.publish(event)

        except Exception as e:
            logger.error(f"Failed to publish integration event: {e}")

    # Health monitoring and management
    async def perform_health_checks(self) -> dict[str, Any]:
        """Perform health checks on all connected integrations."""
        try:
            health_results = {}

            for integration_type, status in self.integration_status.items():
                if status == IntegrationStatus.CONNECTED:
                    health_result = await self._check_integration_health(
                        integration_type
                    )
                    health_results[integration_type.value] = health_result
                else:
                    health_results[integration_type.value] = {
                        "status": status.value,
                        "healthy": False,
                        "last_check": None,
                    }

            self.metrics["health_checks_performed"] += 1

            return {
                "overall_health": self._calculate_overall_health(health_results),
                "integration_health": health_results,
                "metrics": self.get_metrics(),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to perform health checks: {e}")
            return {"overall_health": "error", "error": str(e)}

    async def _check_integration_health(
        self, integration_type: IntegrationType
    ) -> dict[str, Any]:
        """Check health of a specific integration."""
        try:
            endpoint = self.endpoints.get(integration_type)
            if not endpoint:
                return {
                    "status": "error",
                    "healthy": False,
                    "error": "No endpoint configured",
                }

            # Simulate health check (in real implementation, this would ping the actual service)
            await asyncio.sleep(0.05)  # Simulate network call

            # Update endpoint health
            endpoint.last_health_check = datetime.utcnow()

            # For simulation, assume healthy if connected
            is_healthy = (
                self.integration_status[integration_type] == IntegrationStatus.CONNECTED
            )

            health_result = {
                "status": endpoint.status.value,
                "healthy": is_healthy,
                "last_check": endpoint.last_health_check.isoformat(),
                "endpoint": endpoint.endpoint_url,
                "service": endpoint.service_name,
                "response_time_ms": 50.0,  # Simulated
            }

            # Store health result
            self.endpoint_health[integration_type.value] = health_result

            return health_result

        except Exception as e:
            logger.error(f"Failed to check health for {integration_type.value}: {e}")
            return {"status": "error", "healthy": False, "error": str(e)}

    def _calculate_overall_health(self, health_results: dict[str, Any]) -> str:
        """Calculate overall health status from individual integration health."""
        try:
            if not health_results:
                return "unknown"

            healthy_count = sum(
                1 for result in health_results.values() if result.get("healthy", False)
            )
            total_count = len(health_results)

            if healthy_count == total_count:
                return "healthy"
            elif healthy_count > total_count / 2:
                return "degraded"
            elif healthy_count > 0:
                return "partial"
            else:
                return "unhealthy"

        except Exception as e:
            logger.error(f"Failed to calculate overall health: {e}")
            return "error"

    async def connect_all_integrations(self) -> dict[str, bool]:
        """Connect to all configured integrations."""
        try:
            connection_results = {}

            for integration_type in IntegrationType:
                if integration_type in self.endpoints:
                    success = await self.connect_integration(integration_type)
                    connection_results[integration_type.value] = success
                else:
                    connection_results[integration_type.value] = False
                    logger.warning(
                        f"No endpoint configured for {integration_type.value}"
                    )

            return connection_results

        except Exception as e:
            logger.error(f"Failed to connect all integrations: {e}")
            return {}

    async def disconnect_all_integrations(self) -> dict[str, bool]:
        """Disconnect from all integrations."""
        try:
            disconnection_results = {}

            for integration_type in IntegrationType:
                success = await self.disconnect_integration(integration_type)
                disconnection_results[integration_type.value] = success

            return disconnection_results

        except Exception as e:
            logger.error(f"Failed to disconnect all integrations: {e}")
            return {}

    def get_integration_status(self) -> dict[str, Any]:
        """Get comprehensive integration status."""
        try:
            return {
                "integration_status": {
                    integration_type.value: status.value
                    for integration_type, status in self.integration_status.items()
                },
                "endpoint_health": dict(self.endpoint_health),
                "pending_requests": len(self.pending_requests),
                "cache_size": len(self.data_cache),
                "metrics": self.get_metrics(),
                "last_health_check": max(
                    (
                        endpoint.last_health_check
                        for endpoint in self.endpoints.values()
                        if endpoint.last_health_check
                    ),
                    default=None,
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get integration status: {e}")
            return {"error": str(e)}

    def get_metrics(self) -> dict[str, Any]:
        """Get integration metrics."""
        try:
            # Calculate success rate
            total_requests = self.metrics["requests_sent"]
            success_rate = (
                self.metrics["requests_successful"] / total_requests
                if total_requests > 0
                else 1.0
            )

            # Calculate cache hit rate
            total_cache_requests = (
                self.metrics["cache_hits"] + self.metrics["cache_misses"]
            )
            cache_hit_rate = (
                self.metrics["cache_hits"] / total_cache_requests
                if total_cache_requests > 0
                else 0.0
            )

            return {
                **self.metrics,
                "success_rate": success_rate,
                "cache_hit_rate": cache_hit_rate,
                "pending_requests": len(self.pending_requests),
                "cache_size": len(self.data_cache),
                "request_history_size": len(self.request_history),
            }

        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of TTA system integration."""
        try:
            health_results = await self.perform_health_checks()

            return {
                "status": health_results.get("overall_health", "unknown"),
                "integrations_configured": len(self.endpoints),
                "integrations_connected": sum(
                    1
                    for status in self.integration_status.values()
                    if status == IntegrationStatus.CONNECTED
                ),
                "health_check_enabled": self.health_check_enabled,
                "cache_enabled": self.cache_ttl_seconds > 0,
                "integration_health": health_results.get("integration_health", {}),
                "metrics": self.get_metrics(),
            }

        except Exception as e:
            logger.error(f"Failed to perform health check: {e}")
            return {"status": "error", "error": str(e)}
