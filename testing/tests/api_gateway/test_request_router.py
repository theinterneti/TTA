"""
Tests for the API Gateway request router.

This module contains unit tests for the RequestRouter class
and route management functionality.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.api_gateway.core import GatewayCore, RequestRouter
from src.api_gateway.models import (
    RequestMethod,
    RouteRule,
    RouteType,
    ServiceEndpoint,
    ServiceInfo,
    ServiceType,
)
from src.api_gateway.services import ServiceDiscoveryManager


@pytest.fixture
def mock_discovery_manager():
    """Create a mock service discovery manager."""
    manager = AsyncMock(spec=ServiceDiscoveryManager)

    # Mock services
    auth_service = ServiceInfo(
        id=uuid4(),
        name="authentication-service",
        service_type=ServiceType.AUTHENTICATION,
        endpoint=ServiceEndpoint(host="localhost", port=8081, path="/auth/v1"),
    )

    player_service = ServiceInfo(
        id=uuid4(),
        name="player-experience-interface",
        service_type=ServiceType.API,
        endpoint=ServiceEndpoint(host="localhost", port=8080, path="/api/v1"),
    )

    manager.get_all_healthy_services.return_value = [auth_service, player_service]

    return manager


@pytest.fixture
def mock_gateway_core():
    """Create a mock gateway core."""
    core = AsyncMock(spec=GatewayCore)
    core.add_route_rule.return_value = None
    core.remove_route_rule.return_value = True
    core.get_routing_config.return_value.rules = []
    return core


@pytest.fixture
async def request_router(mock_gateway_core, mock_discovery_manager):
    """Create a request router instance."""
    router = RequestRouter(mock_gateway_core, mock_discovery_manager)
    await router.initialize()
    return router


class TestRequestRouter:
    """Test cases for RequestRouter."""

    @pytest.mark.asyncio
    async def test_initialize_with_default_routes(
        self, mock_gateway_core, mock_discovery_manager
    ):
        """Test router initialization with default routes."""
        router = RequestRouter(mock_gateway_core, mock_discovery_manager)

        await router.initialize()

        # Should have added default routes to gateway core
        assert mock_gateway_core.add_route_rule.call_count > 0

        # Check that authentication routes were added
        added_rules = [
            call.args[0] for call in mock_gateway_core.add_route_rule.call_args_list
        ]
        rule_names = [rule.name for rule in added_rules]

        assert "auth-login" in rule_names
        assert "auth-logout" in rule_names
        assert "auth-refresh" in rule_names
        assert "players-api" in rule_names
        assert "characters-api" in rule_names
        assert "sessions-api" in rule_names

    def test_create_default_routes(self, mock_gateway_core, mock_discovery_manager):
        """Test creation of default route rules."""
        router = RequestRouter(mock_gateway_core, mock_discovery_manager)

        default_routes = router._create_default_routes()

        assert len(default_routes) > 0

        # Check authentication routes
        auth_login_route = next(
            (r for r in default_routes if r.name == "auth-login"), None
        )
        assert auth_login_route is not None
        assert auth_login_route.path_pattern == "/api/v1/auth/login"
        assert auth_login_route.target_service == "authentication-service"
        assert auth_login_route.path_rewrite == "/auth/v1/login"
        assert RequestMethod.POST in auth_login_route.methods

        # Check player routes
        players_route = next(
            (r for r in default_routes if r.name == "players-api"), None
        )
        assert players_route is not None
        assert players_route.path_pattern == "/api/v1/players/*"
        assert players_route.target_service == "player-experience-interface"
        assert players_route.therapeutic_priority is True

        # Check therapeutic session routes
        sessions_route = next(
            (r for r in default_routes if r.name == "sessions-api"), None
        )
        assert sessions_route is not None
        assert sessions_route.path_pattern == "/api/v1/sessions/*"
        assert sessions_route.target_service == "core-gameplay-loop"
        assert sessions_route.therapeutic_priority is True
        assert sessions_route.crisis_bypass is True

        # Check WebSocket routes
        chat_ws_route = next(
            (r for r in default_routes if r.name == "chat-websocket"), None
        )
        assert chat_ws_route is not None
        assert chat_ws_route.path_pattern == "/ws/chat"
        assert chat_ws_route.route_type == RouteType.WEBSOCKET
        assert chat_ws_route.therapeutic_priority is True

    @pytest.mark.asyncio
    async def test_add_dynamic_route_success(self, request_router, mock_gateway_core):
        """Test successful addition of dynamic route."""
        new_rule = RouteRule(
            name="dynamic-test",
            path_pattern="/api/v1/test/*",
            target_service="test-service",
        )

        result = await request_router.add_dynamic_route(new_rule)

        assert result is True
        mock_gateway_core.add_route_rule.assert_called_with(new_rule)

    @pytest.mark.asyncio
    async def test_add_dynamic_route_failure(self, request_router, mock_gateway_core):
        """Test failed addition of dynamic route."""
        mock_gateway_core.add_route_rule.side_effect = Exception("Failed to add route")

        new_rule = RouteRule(
            name="dynamic-test",
            path_pattern="/api/v1/test/*",
            target_service="test-service",
        )

        result = await request_router.add_dynamic_route(new_rule)

        assert result is False

    @pytest.mark.asyncio
    async def test_remove_dynamic_route_success(
        self, request_router, mock_gateway_core
    ):
        """Test successful removal of dynamic route."""
        mock_gateway_core.remove_route_rule.return_value = True

        result = await request_router.remove_dynamic_route("test-route")

        assert result is True
        mock_gateway_core.remove_route_rule.assert_called_with("test-route")

    @pytest.mark.asyncio
    async def test_remove_dynamic_route_not_found(
        self, request_router, mock_gateway_core
    ):
        """Test removal of non-existent route."""
        mock_gateway_core.remove_route_rule.return_value = False

        result = await request_router.remove_dynamic_route("non-existent")

        assert result is False

    def test_get_route_rules(self, request_router, mock_gateway_core):
        """Test getting current route rules."""
        mock_rules = [
            RouteRule(
                name="rule1", path_pattern="/api/v1/test1", target_service="service1"
            ),
            RouteRule(
                name="rule2", path_pattern="/api/v1/test2", target_service="service2"
            ),
        ]

        mock_routing_config = MagicMock()
        mock_routing_config.rules = mock_rules
        mock_gateway_core.get_routing_config.return_value = mock_routing_config

        rules = request_router.get_route_rules()

        assert len(rules) == 2
        assert rules[0].name == "rule1"
        assert rules[1].name == "rule2"

    @pytest.mark.asyncio
    async def test_update_routes_from_services(
        self, request_router, mock_discovery_manager, mock_gateway_core
    ):
        """Test updating routes based on available services."""
        # Mock existing rules (empty for this test)
        mock_routing_config = MagicMock()
        mock_routing_config.rules = []
        mock_gateway_core.get_routing_config.return_value = mock_routing_config

        # Mock available services
        new_service = ServiceInfo(
            id=uuid4(),
            name="new-service",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8090),
            therapeutic_priority=True,
        )

        mock_discovery_manager.get_all_healthy_services.return_value = [new_service]

        await request_router.update_routes_from_services()

        # Should have added a dynamic route for the new service
        mock_gateway_core.add_route_rule.assert_called()

        # Get the added rule
        added_rule = mock_gateway_core.add_route_rule.call_args[0][0]
        assert added_rule.name == "dynamic-new-service"
        assert added_rule.target_service == "new-service"
        assert added_rule.therapeutic_priority is True
        assert added_rule.priority == 100  # Lower priority than explicit routes

    @pytest.mark.asyncio
    async def test_update_routes_from_services_no_duplicates(
        self, request_router, mock_discovery_manager, mock_gateway_core
    ):
        """Test that existing services don't get duplicate routes."""
        # Mock existing rules with one service already configured
        existing_rule = RouteRule(
            name="existing-rule",
            path_pattern="/api/v1/existing",
            target_service="existing-service",
        )

        mock_routing_config = MagicMock()
        mock_routing_config.rules = [existing_rule]
        mock_gateway_core.get_routing_config.return_value = mock_routing_config

        # Mock services including the existing one
        existing_service = ServiceInfo(
            id=uuid4(),
            name="existing-service",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8080),
        )

        new_service = ServiceInfo(
            id=uuid4(),
            name="new-service",
            service_type=ServiceType.API,
            endpoint=ServiceEndpoint(host="localhost", port=8090),
        )

        mock_discovery_manager.get_all_healthy_services.return_value = [
            existing_service,
            new_service,
        ]

        await request_router.update_routes_from_services()

        # Should only add route for the new service, not the existing one
        mock_gateway_core.add_route_rule.assert_called_once()

        added_rule = mock_gateway_core.add_route_rule.call_args[0][0]
        assert added_rule.target_service == "new-service"

    @pytest.mark.asyncio
    async def test_update_routes_from_services_error_handling(
        self, request_router, mock_discovery_manager, mock_gateway_core
    ):
        """Test error handling in route updates."""
        mock_discovery_manager.get_all_healthy_services.side_effect = Exception(
            "Service discovery failed"
        )

        # Should not raise exception
        await request_router.update_routes_from_services()

        # Should not have tried to add any routes
        mock_gateway_core.add_route_rule.assert_not_called()


class TestRouteRuleProperties:
    """Test cases for route rule properties and validation."""

    def test_authentication_route_properties(self):
        """Test authentication route properties."""
        router = RequestRouter(MagicMock(), MagicMock())
        routes = router._create_default_routes()

        auth_routes = [
            r for r in routes if r.target_service == "authentication-service"
        ]

        for route in auth_routes:
            assert (
                route.therapeutic_priority is False
            )  # Auth routes are not therapeutic
            assert route.timeout <= 10  # Auth should be fast
            assert route.priority <= 20  # High priority

    def test_therapeutic_route_properties(self):
        """Test therapeutic route properties."""
        router = RequestRouter(MagicMock(), MagicMock())
        routes = router._create_default_routes()

        therapeutic_routes = [r for r in routes if r.therapeutic_priority is True]

        assert len(therapeutic_routes) > 0

        for route in therapeutic_routes:
            assert route.therapeutic_priority is True
            # Therapeutic routes should have reasonable timeouts
            assert route.timeout >= 30

    def test_crisis_bypass_routes(self):
        """Test routes with crisis bypass capability."""
        router = RequestRouter(MagicMock(), MagicMock())
        routes = router._create_default_routes()

        crisis_routes = [r for r in routes if r.crisis_bypass is True]

        # Should have at least sessions and chat routes with crisis bypass
        assert len(crisis_routes) >= 2

        crisis_route_names = [r.name for r in crisis_routes]
        assert "sessions-api" in crisis_route_names
        assert "chat-websocket" in crisis_route_names

    def test_websocket_route_properties(self):
        """Test WebSocket route properties."""
        router = RequestRouter(MagicMock(), MagicMock())
        routes = router._create_default_routes()

        websocket_routes = [r for r in routes if r.route_type == RouteType.WEBSOCKET]

        assert len(websocket_routes) > 0

        for route in websocket_routes:
            assert route.route_type == RouteType.WEBSOCKET
            assert RequestMethod.GET in route.methods  # WebSocket upgrade uses GET
            assert route.timeout >= 300  # WebSocket connections need longer timeouts

    def test_path_rewrite_patterns(self):
        """Test path rewrite patterns in routes."""
        router = RequestRouter(MagicMock(), MagicMock())
        routes = router._create_default_routes()

        # Check auth routes have proper rewrites
        auth_login = next(r for r in routes if r.name == "auth-login")
        assert auth_login.path_rewrite == "/auth/v1/login"

        # Check wildcard routes have proper rewrites
        players_route = next(r for r in routes if r.name == "players-api")
        assert players_route.path_rewrite == "/api/v1/players/$1"

        sessions_route = next(r for r in routes if r.name == "sessions-api")
        assert sessions_route.path_rewrite == "/gameplay/v1/sessions/$1"
