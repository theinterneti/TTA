"""
Tests for TTA System Integration

This module tests comprehensive integration with existing TTA infrastructure including
Character Development System integration, Therapeutic Content Management integration,
Safety Monitoring System integration, Progress Tracking System integration, and
seamless data exchange functions for production-ready system interoperability.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from src.components.gameplay_loop.integration.tta_system_integration import (
    TTASystemIntegration, IntegrationEndpoint, IntegrationRequest, IntegrationResponse,
    IntegrationType, IntegrationStatus
)
from src.components.gameplay_loop.narrative.events import EventBus
from src.components.gameplay_loop.services.session_state import SessionState, SessionStateType


class TestTTASystemIntegration:
    """Test TTA System Integration functionality."""
    
    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        bus = Mock(spec=EventBus)
        bus.publish = AsyncMock()
        return bus
    
    @pytest.fixture
    def tta_integration(self, event_bus):
        """Create TTA system integration instance."""
        return TTASystemIntegration(event_bus)
    
    @pytest.fixture
    def sample_session_state(self):
        """Create sample session state."""
        return SessionState(
            session_id="test_session_123",
            user_id="test_user_456",
            state_type=SessionStateType.ACTIVE,
            current_scene_id="scene_1",
            narrative_context={"test": "context"}
        )
    
    @pytest.fixture
    def sample_integration_request(self):
        """Create sample integration request."""
        return IntegrationRequest(
            integration_type=IntegrationType.CHARACTER_DEVELOPMENT,
            operation="post",
            endpoint="/character/update",
            payload={
                "user_id": "test_user_456",
                "attribute": "courage",
                "change": 1.5
            }
        )
    
    def test_initialization(self, tta_integration):
        """Test TTA system integration initialization."""
        # Check initialization
        assert isinstance(tta_integration, TTASystemIntegration)
        assert len(tta_integration.endpoints) == 4  # Default endpoints
        assert len(tta_integration.integration_status) == len(IntegrationType)
        
        # Check default endpoints are configured
        assert IntegrationType.CHARACTER_DEVELOPMENT in tta_integration.endpoints
        assert IntegrationType.THERAPEUTIC_CONTENT in tta_integration.endpoints
        assert IntegrationType.SAFETY_MONITORING in tta_integration.endpoints
        assert IntegrationType.PROGRESS_TRACKING in tta_integration.endpoints
        
        # Check all integrations start as disconnected
        for status in tta_integration.integration_status.values():
            assert status == IntegrationStatus.DISCONNECTED
    
    @pytest.mark.asyncio
    async def test_connect_integration(self, tta_integration, event_bus):
        """Test connecting to an integration."""
        # Test successful connection
        success = await tta_integration.connect_integration(IntegrationType.CHARACTER_DEVELOPMENT)
        
        assert success == True
        assert tta_integration.integration_status[IntegrationType.CHARACTER_DEVELOPMENT] == IntegrationStatus.CONNECTED
        assert tta_integration.metrics["integrations_active"] == 1
        
        # Check event was published
        event_bus.publish.assert_called()
        
        # Test connecting to non-existent integration
        tta_integration.endpoints.pop(IntegrationType.THERAPEUTIC_CONTENT)
        success = await tta_integration.connect_integration(IntegrationType.THERAPEUTIC_CONTENT)
        assert success == False
    
    @pytest.mark.asyncio
    async def test_disconnect_integration(self, tta_integration, event_bus):
        """Test disconnecting from an integration."""
        # Connect first
        await tta_integration.connect_integration(IntegrationType.CHARACTER_DEVELOPMENT)
        
        # Test disconnection
        success = await tta_integration.disconnect_integration(IntegrationType.CHARACTER_DEVELOPMENT)
        
        assert success == True
        assert tta_integration.integration_status[IntegrationType.CHARACTER_DEVELOPMENT] == IntegrationStatus.DISCONNECTED
        assert tta_integration.metrics["integrations_active"] == 0
        
        # Check event was published
        assert event_bus.publish.call_count == 2  # Connect + disconnect
    
    @pytest.mark.asyncio
    async def test_send_integration_request_disconnected(self, tta_integration, sample_integration_request):
        """Test sending request to disconnected integration."""
        response = await tta_integration.send_integration_request(sample_integration_request)
        
        assert response.success == False
        assert "not connected" in response.error_message.lower()
        assert response.integration_type == IntegrationType.CHARACTER_DEVELOPMENT
    
    @pytest.mark.asyncio
    async def test_send_integration_request_connected(self, tta_integration, sample_integration_request):
        """Test sending request to connected integration."""
        # Connect first
        await tta_integration.connect_integration(IntegrationType.CHARACTER_DEVELOPMENT)
        
        # Send request
        response = await tta_integration.send_integration_request(sample_integration_request)
        
        assert response.success == True
        assert response.status_code == 200
        assert "user_id" in response.response_data
        assert response.processing_time_ms > 0
        assert tta_integration.metrics["requests_sent"] == 1
        assert tta_integration.metrics["requests_successful"] == 1
    
    @pytest.mark.asyncio
    async def test_character_development_integration(self, tta_integration, sample_session_state):
        """Test character development system integration."""
        # Connect integration
        await tta_integration.connect_integration(IntegrationType.CHARACTER_DEVELOPMENT)
        
        # Sync character development
        result = await tta_integration.sync_character_development(
            sample_session_state, "courage", 2.0, {"story_context": "brave_choice"}
        )
        
        assert "user_id" in result
        assert "attribute" in result
        assert "change_applied" in result
        assert result["user_id"] == sample_session_state.user_id
    
    @pytest.mark.asyncio
    async def test_therapeutic_content_integration(self, tta_integration):
        """Test therapeutic content management integration."""
        # Connect integration
        await tta_integration.connect_integration(IntegrationType.THERAPEUTIC_CONTENT)
        
        # Get therapeutic content
        result = await tta_integration.get_therapeutic_content(
            "scenario", "CBT", {"difficulty": "medium"}, {"session_phase": "exploration"}
        )
        
        assert "content_id" in result
        assert "content_type" in result
        assert "therapeutic_framework" in result
        assert result["content_type"] == "scenario"
        assert result["therapeutic_framework"] == "CBT"
    
    @pytest.mark.asyncio
    async def test_safety_monitoring_integration(self, tta_integration):
        """Test safety monitoring system integration."""
        # Connect integration
        await tta_integration.connect_integration(IntegrationType.SAFETY_MONITORING)
        
        # Validate safety
        result = await tta_integration.validate_safety(
            "test_user_456", "Test content for validation", 
            {"emotional_state": "calm"}, "test_session_123"
        )
        
        assert "safety_assessment" in result
        assert "content_analysis" in result
        assert "recommendations" in result
        assert result["user_id"] == "test_user_456"
    
    @pytest.mark.asyncio
    async def test_progress_tracking_integration(self, tta_integration):
        """Test progress tracking system integration."""
        # Connect integration
        await tta_integration.connect_integration(IntegrationType.PROGRESS_TRACKING)
        
        # Update progress
        progress_data = {
            "therapeutic_progress": 0.75,
            "session_engagement": 0.85,
            "goals_achieved": 3
        }
        
        result = await tta_integration.update_progress_tracking(
            "test_user_456", progress_data, "test_session_123", {"milestone": "first_breakthrough"}
        )
        
        assert "progress_update" in result
        assert "analytics" in result
        assert "next_recommendations" in result
        assert result["user_id"] == "test_user_456"
    
    @pytest.mark.asyncio
    async def test_caching_functionality(self, tta_integration, sample_integration_request):
        """Test request caching functionality."""
        # Connect integration
        await tta_integration.connect_integration(IntegrationType.CHARACTER_DEVELOPMENT)
        
        # Make GET request (cacheable)
        get_request = IntegrationRequest(
            integration_type=IntegrationType.CHARACTER_DEVELOPMENT,
            operation="get",
            endpoint="/character/status",
            payload={"user_id": "test_user_456"}
        )
        
        # First request - should miss cache
        response1 = await tta_integration.send_integration_request(get_request)
        assert response1.success == True
        assert response1.cached_response == False
        assert tta_integration.metrics["cache_misses"] == 1
        
        # Second identical request - should hit cache
        response2 = await tta_integration.send_integration_request(get_request)
        assert response2.success == True
        assert response2.cached_response == True
        assert tta_integration.metrics["cache_hits"] == 1
    
    @pytest.mark.asyncio
    async def test_health_checks(self, tta_integration):
        """Test health check functionality."""
        # Connect some integrations
        await tta_integration.connect_integration(IntegrationType.CHARACTER_DEVELOPMENT)
        await tta_integration.connect_integration(IntegrationType.SAFETY_MONITORING)
        
        # Perform health checks
        health_results = await tta_integration.perform_health_checks()
        
        assert "overall_health" in health_results
        assert "integration_health" in health_results
        assert "metrics" in health_results
        
        # Check individual integration health
        char_dev_health = health_results["integration_health"]["character_development"]
        assert char_dev_health["healthy"] == True
        assert char_dev_health["status"] == "connected"
        
        safety_health = health_results["integration_health"]["safety_monitoring"]
        assert safety_health["healthy"] == True
        assert safety_health["status"] == "connected"
    
    @pytest.mark.asyncio
    async def test_connect_all_integrations(self, tta_integration):
        """Test connecting to all integrations."""
        results = await tta_integration.connect_all_integrations()
        
        # Check all integrations were attempted
        assert len(results) == len(IntegrationType)
        
        # Check all succeeded (in simulation)
        for integration_type, success in results.items():
            assert success == True
        
        # Check metrics
        assert tta_integration.metrics["integrations_active"] == len(IntegrationType)
    
    @pytest.mark.asyncio
    async def test_disconnect_all_integrations(self, tta_integration):
        """Test disconnecting from all integrations."""
        # Connect first
        await tta_integration.connect_all_integrations()
        
        # Disconnect all
        results = await tta_integration.disconnect_all_integrations()
        
        # Check all integrations were disconnected
        assert len(results) == len(IntegrationType)
        for integration_type, success in results.items():
            assert success == True
        
        # Check metrics
        assert tta_integration.metrics["integrations_active"] == 0
    
    def test_get_integration_status(self, tta_integration):
        """Test getting integration status."""
        status = tta_integration.get_integration_status()
        
        assert "integration_status" in status
        assert "endpoint_health" in status
        assert "pending_requests" in status
        assert "cache_size" in status
        assert "metrics" in status
        
        # Check integration status format
        for integration_type in IntegrationType:
            assert integration_type.value in status["integration_status"]
    
    def test_metrics_tracking(self, tta_integration):
        """Test metrics tracking."""
        initial_metrics = tta_integration.get_metrics()
        
        # Check metric structure
        assert "requests_sent" in initial_metrics
        assert "requests_successful" in initial_metrics
        assert "requests_failed" in initial_metrics
        assert "integrations_active" in initial_metrics
        assert "cache_hits" in initial_metrics
        assert "cache_misses" in initial_metrics
        assert "success_rate" in initial_metrics
        assert "cache_hit_rate" in initial_metrics
        
        # Initially should be zero or default values
        assert initial_metrics["requests_sent"] == 0
        assert initial_metrics["requests_successful"] == 0
        assert initial_metrics["requests_failed"] == 0
        assert initial_metrics["integrations_active"] == 0
        assert initial_metrics["success_rate"] == 1.0  # No requests = 100% success
        assert initial_metrics["cache_hit_rate"] == 0.0  # No cache requests = 0% hit rate
    
    @pytest.mark.asyncio
    async def test_health_check(self, tta_integration):
        """Test health check functionality."""
        health = await tta_integration.health_check()
        
        assert "status" in health
        assert "integrations_configured" in health
        assert "integrations_connected" in health
        assert "health_check_enabled" in health
        assert "cache_enabled" in health
        assert "integration_health" in health
        assert "metrics" in health
        
        # Should have configured integrations
        assert health["integrations_configured"] == len(IntegrationType)
        assert health["integrations_connected"] == 0  # None connected initially
        assert health["health_check_enabled"] == True
        assert health["cache_enabled"] == True
    
    def test_cache_key_generation(self, tta_integration, sample_integration_request):
        """Test cache key generation."""
        cache_key1 = tta_integration._generate_cache_key(sample_integration_request)
        cache_key2 = tta_integration._generate_cache_key(sample_integration_request)
        
        # Same request should generate same cache key
        assert cache_key1 == cache_key2
        assert cache_key1.startswith("integration_cache_")
        
        # Different request should generate different cache key
        different_request = IntegrationRequest(
            integration_type=IntegrationType.THERAPEUTIC_CONTENT,
            operation="get",
            endpoint="/content/retrieve",
            payload={"content_type": "scenario"}
        )
        
        cache_key3 = tta_integration._generate_cache_key(different_request)
        assert cache_key3 != cache_key1
    
    def test_integration_endpoint_configuration(self, tta_integration):
        """Test integration endpoint configuration."""
        # Check character development endpoint
        char_dev_endpoint = tta_integration.endpoints[IntegrationType.CHARACTER_DEVELOPMENT]
        assert char_dev_endpoint.service_name == "character_development_system"
        assert char_dev_endpoint.endpoint_url == "/api/v1/character"
        assert "user_id" in char_dev_endpoint.required_fields
        assert "attribute" in char_dev_endpoint.required_fields
        assert "change" in char_dev_endpoint.required_fields
        
        # Check therapeutic content endpoint
        content_endpoint = tta_integration.endpoints[IntegrationType.THERAPEUTIC_CONTENT]
        assert content_endpoint.service_name == "therapeutic_content_management"
        assert content_endpoint.endpoint_url == "/api/v1/content"
        assert "content_type" in content_endpoint.required_fields
        assert "therapeutic_framework" in content_endpoint.required_fields
        
        # Check safety monitoring endpoint
        safety_endpoint = tta_integration.endpoints[IntegrationType.SAFETY_MONITORING]
        assert safety_endpoint.service_name == "safety_monitoring_system"
        assert safety_endpoint.endpoint_url == "/api/v1/safety"
        assert "user_id" in safety_endpoint.required_fields
        assert "content" in safety_endpoint.required_fields
        assert "context" in safety_endpoint.required_fields
        
        # Check progress tracking endpoint
        progress_endpoint = tta_integration.endpoints[IntegrationType.PROGRESS_TRACKING]
        assert progress_endpoint.service_name == "progress_tracking_system"
        assert progress_endpoint.endpoint_url == "/api/v1/progress"
        assert "user_id" in progress_endpoint.required_fields
        assert "progress_data" in progress_endpoint.required_fields
