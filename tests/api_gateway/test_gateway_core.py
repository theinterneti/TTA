"""
Tests for the API Gateway core request processing engine.

This module contains unit tests for the GatewayCore class,
request processing, routing, and response transformation.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import aiohttp
from fastapi import Request
from fastapi.testclient import TestClient

from src.api_gateway.core import GatewayCore
from src.api_gateway.models import (
    GatewayRequest, ServiceInfo, ServiceType, ServiceEndpoint, 
    RouteRule, RequestMethod, RouteType
)
from src.api_gateway.services import ServiceDiscoveryManager


@pytest.fixture
def mock_discovery_manager():
    """Create a mock service discovery manager."""
    manager = AsyncMock(spec=ServiceDiscoveryManager)
    
    # Mock service
    mock_service = ServiceInfo(
        id=uuid4(),
        name="test-service",
        version="1.0.0",
        service_type=ServiceType.API,
        endpoint=ServiceEndpoint(
            host="localhost",
            port=8080,
            path="/api/v1",
            scheme="http"
        ),
        weight=100,
        priority=100,
        tags=["test"],
        therapeutic_priority=False,
        safety_validated=True
    )
    
    manager.get_service_for_request.return_value = mock_service
    manager.get_all_healthy_services.return_value = [mock_service]
    manager.update_service_metrics.return_value = None
    
    return manager


@pytest.fixture
async def gateway_core(mock_discovery_manager):
    """Create a gateway core instance."""
    core = GatewayCore(mock_discovery_manager)
    await core.initialize()
    yield core
    await core.close()


@pytest.fixture
def mock_request():
    """Create a mock FastAPI request."""
    request = MagicMock(spec=Request)
    request.method = "GET"
    request.url.path = "/api/v1/test"
    request.query_params = {}
    request.headers = {
        "content-type": "application/json",
        "user-agent": "test-client"
    }
    request.client.host = "127.0.0.1"
    request.state = MagicMock()
    request.state.correlation_id = str(uuid4())
    request.state.auth_context = None
    
    # Mock body method
    async def mock_body():
        return b'{"test": "data"}'
    
    request.body = mock_body
    
    return request


class TestGatewayCore:
    """Test cases for GatewayCore."""
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_discovery_manager):
        """Test successful gateway core initialization."""
        core = GatewayCore(mock_discovery_manager)
        
        await core.initialize()
        
        assert core._http_session is not None
        assert isinstance(core._http_session, aiohttp.ClientSession)
        
        await core.close()
    
    @pytest.mark.asyncio
    async def test_close_cleanup(self, gateway_core):
        """Test proper cleanup on close."""
        # Verify session exists
        assert gateway_core._http_session is not None
        
        await gateway_core.close()
        
        # Session should be closed
        assert gateway_core._http_session.closed
    
    @pytest.mark.asyncio
    async def test_create_gateway_request(self, gateway_core, mock_request):
        """Test conversion of FastAPI request to gateway request."""
        correlation_id = "test-correlation-id"
        
        gateway_request = await gateway_core._create_gateway_request(mock_request, correlation_id)
        
        assert isinstance(gateway_request, GatewayRequest)
        assert gateway_request.correlation_id == correlation_id
        assert gateway_request.method == RequestMethod.GET
        assert gateway_request.path == "/api/v1/test"
        assert gateway_request.client_ip == "127.0.0.1"
        assert gateway_request.body is not None
    
    @pytest.mark.asyncio
    async def test_create_gateway_request_with_auth(self, gateway_core, mock_request):
        """Test gateway request creation with authentication context."""
        # Add auth context to request
        mock_auth_context = MagicMock()
        mock_auth_context.user_id = uuid4()
        mock_auth_context.username = "test_user"
        mock_auth_context.permissions.role.value = "patient"
        mock_auth_context.is_therapeutic_context.return_value = True
        mock_auth_context.crisis_mode = False
        
        mock_request.state.auth_context = mock_auth_context
        mock_request.state.is_therapeutic_context = True
        
        correlation_id = "test-correlation-id"
        gateway_request = await gateway_core._create_gateway_request(mock_request, correlation_id)
        
        assert gateway_request.auth_context is not None
        assert gateway_request.auth_context["username"] == "test_user"
        assert gateway_request.auth_context["role"] == "patient"
        assert gateway_request.auth_context["therapeutic_context"] is True
        assert gateway_request.is_therapeutic is True
    
    @pytest.mark.asyncio
    async def test_find_matching_route_with_rules(self, gateway_core):
        """Test finding matching route with configured rules."""
        # Add a test route rule
        test_rule = RouteRule(
            name="test-rule",
            path_pattern="/api/v1/test",
            methods=[RequestMethod.GET],
            target_service="test-service",
            priority=10
        )
        
        await gateway_core.add_route_rule(test_rule)
        
        # Create test request
        gateway_request = GatewayRequest(
            correlation_id="test",
            method=RequestMethod.GET,
            path="/api/v1/test",
            client_ip="127.0.0.1"
        )
        
        matching_rule = await gateway_core._find_matching_route(gateway_request)
        
        assert matching_rule is not None
        assert matching_rule.name == "test-rule"
        assert matching_rule.target_service == "test-service"
    
    @pytest.mark.asyncio
    async def test_create_dynamic_route(self, gateway_core, mock_discovery_manager):
        """Test dynamic route creation based on path."""
        # Mock service discovery to return a service
        mock_service = ServiceInfo(
            id=uuid4(),
            name="player-experience-interface",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8080)
        )
        mock_discovery_manager.get_all_healthy_services.return_value = [mock_service]
        
        gateway_request = GatewayRequest(
            correlation_id="test",
            method=RequestMethod.GET,
            path="/api/players/123",
            client_ip="127.0.0.1"
        )
        
        dynamic_route = await gateway_core._create_dynamic_route(gateway_request)
        
        assert dynamic_route is not None
        assert dynamic_route.name == "dynamic-players"
        assert dynamic_route.target_service == "player-experience-interface"
        assert dynamic_route.therapeutic_priority is False
    
    @pytest.mark.asyncio
    async def test_get_target_service(self, gateway_core, mock_discovery_manager):
        """Test getting target service for a route."""
        route_rule = RouteRule(
            name="test-rule",
            path_pattern="/api/v1/test",
            target_service="test-service",
            therapeutic_priority=True
        )
        
        gateway_request = GatewayRequest(
            correlation_id="test",
            method=RequestMethod.GET,
            path="/api/v1/test",
            client_ip="127.0.0.1",
            is_therapeutic=True
        )
        
        service = await gateway_core._get_target_service(route_rule, gateway_request)
        
        assert service is not None
        mock_discovery_manager.get_service_for_request.assert_called_once_with(
            service_name="test-service",
            therapeutic_priority=True
        )
    
    def test_transform_request_path_no_rewrite(self, gateway_core):
        """Test path transformation without rewrite rule."""
        route_rule = RouteRule(
            name="test-rule",
            path_pattern="/api/v1/test",
            target_service="test-service"
        )
        
        original_path = "/api/v1/test"
        transformed_path = gateway_core._transform_request_path(original_path, route_rule)
        
        assert transformed_path == original_path
    
    def test_transform_request_path_with_rewrite(self, gateway_core):
        """Test path transformation with rewrite rule."""
        route_rule = RouteRule(
            name="test-rule",
            path_pattern="/api/v1/test/*",
            target_service="test-service",
            path_rewrite="/service/v1/$1"
        )
        
        original_path = "/api/v1/test/123"
        transformed_path = gateway_core._transform_request_path(original_path, route_rule)
        
        assert transformed_path == "/service/v1/123"
    
    def test_prepare_request_headers(self, gateway_core):
        """Test request header preparation."""
        gateway_request = GatewayRequest(
            correlation_id="test-123",
            method=RequestMethod.GET,
            path="/api/v1/test",
            headers={
                "content-type": "application/json",
                "authorization": "Bearer token123",
                "connection": "keep-alive"  # Should be removed
            },
            client_ip="192.168.1.1",
            auth_context={
                "user_id": "user-123",
                "role": "patient",
                "therapeutic_context": True
            },
            is_therapeutic=True,
            crisis_mode=False
        )
        
        target_service = ServiceInfo(
            id=uuid4(),
            name="test-service",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8080)
        )
        
        headers = gateway_core._prepare_request_headers(gateway_request, target_service)
        
        # Check that hop-by-hop headers are removed
        assert "connection" not in headers
        
        # Check that gateway headers are added
        assert headers["X-Forwarded-For"] == "192.168.1.1"
        assert headers["X-Gateway-Request-ID"] == "test-123"
        assert headers["X-Gateway-Service"] == "test-service"
        
        # Check authentication headers
        assert headers["X-User-ID"] == "user-123"
        assert headers["X-User-Role"] == "patient"
        assert headers["X-Therapeutic-Context"] == "True"
        
        # Check therapeutic headers
        assert headers["X-Therapeutic-Session"] == "true"
    
    def test_create_error_response(self, gateway_core):
        """Test error response creation."""
        response = gateway_core._create_error_response(404, "Not found", "test-123")
        
        assert response.status_code == 404
        assert "X-Gateway-Request-ID" in response.headers
        assert response.headers["X-Gateway-Request-ID"] == "test-123"
        
        # Check response content
        content = json.loads(response.body.decode())
        assert content["error"]["code"] == 404
        assert content["error"]["message"] == "Not found"
        assert content["error"]["request_id"] == "test-123"
    
    @pytest.mark.asyncio
    async def test_add_route_rule(self, gateway_core):
        """Test adding a route rule."""
        rule = RouteRule(
            name="new-rule",
            path_pattern="/api/v1/new",
            target_service="new-service",
            priority=50
        )
        
        await gateway_core.add_route_rule(rule)
        
        rules = gateway_core.get_routing_config().rules
        assert any(r.name == "new-rule" for r in rules)
        
        # Check that rules are sorted by priority
        priorities = [r.priority for r in rules]
        assert priorities == sorted(priorities)
    
    @pytest.mark.asyncio
    async def test_remove_route_rule(self, gateway_core):
        """Test removing a route rule."""
        # Add a rule first
        rule = RouteRule(
            name="temp-rule",
            path_pattern="/api/v1/temp",
            target_service="temp-service"
        )
        
        await gateway_core.add_route_rule(rule)
        
        # Verify it was added
        rules = gateway_core.get_routing_config().rules
        assert any(r.name == "temp-rule" for r in rules)
        
        # Remove the rule
        removed = await gateway_core.remove_route_rule("temp-rule")
        
        assert removed is True
        
        # Verify it was removed
        rules = gateway_core.get_routing_config().rules
        assert not any(r.name == "temp-rule" for r in rules)
    
    def test_get_active_requests(self, gateway_core):
        """Test getting active requests."""
        # Add a mock active request
        test_request = GatewayRequest(
            correlation_id="test-123",
            method=RequestMethod.GET,
            path="/api/v1/test",
            client_ip="127.0.0.1"
        )
        
        gateway_core._active_requests["test-123"] = test_request
        
        active_requests = gateway_core.get_active_requests()
        
        assert "test-123" in active_requests
        assert active_requests["test-123"] == test_request
        
        # Verify it's a copy (not the original dict)
        active_requests["new-key"] = "new-value"
        assert "new-key" not in gateway_core._active_requests


@pytest.mark.asyncio
async def test_gateway_core_integration():
    """Integration test for gateway core with mocked HTTP session."""
    mock_discovery_manager = AsyncMock(spec=ServiceDiscoveryManager)
    
    # Mock service
    mock_service = ServiceInfo(
        id=uuid4(),
        name="test-service",
        service_type=ServiceType.API,
        endpoint=ServiceEndpoint(host="localhost", port=8080, path="/api/v1")
    )
    mock_discovery_manager.get_service_for_request.return_value = mock_service
    mock_discovery_manager.update_service_metrics.return_value = None
    
    # Create gateway core
    gateway_core = GatewayCore(mock_discovery_manager)
    
    # Mock HTTP session
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"content-type": "application/json"}
    mock_response.read.return_value = b'{"result": "success"}'
    
    mock_session = AsyncMock()
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    gateway_core._http_session = mock_session
    
    # Create test request
    mock_request = MagicMock(spec=Request)
    mock_request.method = "GET"
    mock_request.url.path = "/api/v1/test"
    mock_request.query_params = {}
    mock_request.headers = {"content-type": "application/json"}
    mock_request.client.host = "127.0.0.1"
    mock_request.state.correlation_id = "test-123"
    mock_request.body = AsyncMock(return_value=b'{}')
    
    # Add a route rule
    rule = RouteRule(
        name="test-rule",
        path_pattern="/api/v1/test",
        methods=[RequestMethod.GET],
        target_service="test-service"
    )
    await gateway_core.add_route_rule(rule)
    
    # Process request
    response = await gateway_core.process_request(mock_request)
    
    # Verify response
    assert response.status_code == 200
    
    # Verify service was called
    mock_discovery_manager.get_service_for_request.assert_called()
    mock_discovery_manager.update_service_metrics.assert_called()
    
    await gateway_core.close()
