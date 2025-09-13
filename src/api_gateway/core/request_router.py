"""
Request router for the API Gateway.

This module provides request routing functionality that integrates with
the gateway core and service discovery system.
"""

import logging

from fastapi import APIRouter, Request, Response

from ..config import get_gateway_settings
from ..models import RequestMethod, RouteRule, RouteType
from ..services import ServiceDiscoveryManager
from .gateway_core import GatewayCore

logger = logging.getLogger(__name__)


class RequestRouter:
    """
    Request router that handles dynamic routing and rule management.

    Integrates with GatewayCore for request processing and ServiceDiscoveryManager
    for service discovery.
    """

    def __init__(
        self, gateway_core: GatewayCore, discovery_manager: ServiceDiscoveryManager
    ):
        """
        Initialize the request router.

        Args:
            gateway_core: Gateway core instance
            discovery_manager: Service discovery manager
        """
        self.gateway_core = gateway_core
        self.discovery_manager = discovery_manager
        self.settings = get_gateway_settings()
        self._default_routes = self._create_default_routes()

    async def initialize(self) -> None:
        """Initialize the request router with default routes."""
        # Add default routes to gateway core
        for route in self._default_routes:
            await self.gateway_core.add_route_rule(route)

        logger.info(
            f"Request router initialized with {len(self._default_routes)} default routes"
        )

    def _create_default_routes(self) -> list[RouteRule]:
        """
        Create default route rules for TTA services.

        Returns:
            List[RouteRule]: Default route rules
        """
        routes = []

        # Authentication service routes
        routes.append(
            RouteRule(
                name="auth-login",
                description="Authentication login endpoint",
                path_pattern="/api/v1/auth/login",
                methods=[RequestMethod.POST],
                target_service="authentication-service",
                route_type=RouteType.HTTP,
                path_rewrite="/auth/v1/login",
                priority=10,
                therapeutic_priority=False,
                timeout=10,
            )
        )

        routes.append(
            RouteRule(
                name="auth-logout",
                description="Authentication logout endpoint",
                path_pattern="/api/v1/auth/logout",
                methods=[RequestMethod.POST],
                target_service="authentication-service",
                route_type=RouteType.HTTP,
                path_rewrite="/auth/v1/logout",
                priority=10,
                therapeutic_priority=False,
                timeout=5,
            )
        )

        routes.append(
            RouteRule(
                name="auth-refresh",
                description="Token refresh endpoint",
                path_pattern="/api/v1/auth/refresh",
                methods=[RequestMethod.POST],
                target_service="authentication-service",
                route_type=RouteType.HTTP,
                path_rewrite="/auth/v1/refresh",
                priority=10,
                therapeutic_priority=False,
                timeout=5,
            )
        )

        # Player Experience Interface routes
        routes.append(
            RouteRule(
                name="players-api",
                description="Player management API",
                path_pattern="/api/v1/players/*",
                methods=[
                    RequestMethod.GET,
                    RequestMethod.POST,
                    RequestMethod.PUT,
                    RequestMethod.DELETE,
                ],
                target_service="player-experience-interface",
                route_type=RouteType.HTTP,
                path_rewrite="/api/v1/players/$1",
                priority=20,
                therapeutic_priority=True,
                timeout=30,
            )
        )

        routes.append(
            RouteRule(
                name="characters-api",
                description="Character management API",
                path_pattern="/api/v1/characters/*",
                methods=[
                    RequestMethod.GET,
                    RequestMethod.POST,
                    RequestMethod.PUT,
                    RequestMethod.DELETE,
                ],
                target_service="player-experience-interface",
                route_type=RouteType.HTTP,
                path_rewrite="/api/v1/characters/$1",
                priority=20,
                therapeutic_priority=True,
                timeout=30,
            )
        )

        routes.append(
            RouteRule(
                name="worlds-api",
                description="World management API",
                path_pattern="/api/v1/worlds/*",
                methods=[
                    RequestMethod.GET,
                    RequestMethod.POST,
                    RequestMethod.PUT,
                    RequestMethod.DELETE,
                ],
                target_service="player-experience-interface",
                route_type=RouteType.HTTP,
                path_rewrite="/api/v1/worlds/$1",
                priority=20,
                therapeutic_priority=True,
                timeout=30,
            )
        )

        # Core Gameplay Loop routes
        routes.append(
            RouteRule(
                name="sessions-api",
                description="Therapeutic session management API",
                path_pattern="/api/v1/sessions/*",
                methods=[
                    RequestMethod.GET,
                    RequestMethod.POST,
                    RequestMethod.PUT,
                    RequestMethod.DELETE,
                ],
                target_service="core-gameplay-loop",
                route_type=RouteType.HTTP,
                path_rewrite="/gameplay/v1/sessions/$1",
                priority=15,
                therapeutic_priority=True,
                crisis_bypass=True,
                timeout=60,
            )
        )

        routes.append(
            RouteRule(
                name="gameplay-api",
                description="Gameplay mechanics API",
                path_pattern="/api/v1/gameplay/*",
                methods=[RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT],
                target_service="core-gameplay-loop",
                route_type=RouteType.HTTP,
                path_rewrite="/gameplay/v1/$1",
                priority=20,
                therapeutic_priority=True,
                timeout=45,
            )
        )

        # Agent Orchestration routes
        routes.append(
            RouteRule(
                name="agents-api",
                description="AI Agent orchestration API",
                path_pattern="/api/v1/agents/*",
                methods=[RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT],
                target_service="agent-orchestration",
                route_type=RouteType.HTTP,
                path_rewrite="/api/v1/agents/$1",
                priority=25,
                therapeutic_priority=True,
                timeout=120,  # Longer timeout for AI operations
            )
        )

        # WebSocket routes
        routes.append(
            RouteRule(
                name="chat-websocket",
                description="Chat WebSocket endpoint",
                path_pattern="/ws/chat",
                methods=[RequestMethod.GET],  # WebSocket upgrade
                target_service="player-experience-interface",
                route_type=RouteType.WEBSOCKET,
                path_rewrite="/ws/chat",
                priority=5,
                therapeutic_priority=True,
                crisis_bypass=True,
                timeout=300,
            )
        )

        return routes

    async def add_dynamic_route(self, route_rule: RouteRule) -> bool:
        """
        Add a dynamic route rule.

        Args:
            route_rule: Route rule to add

        Returns:
            bool: True if route was added successfully
        """
        try:
            await self.gateway_core.add_route_rule(route_rule)
            logger.info(f"Added dynamic route: {route_rule.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add dynamic route {route_rule.name}: {e}")
            return False

    async def remove_dynamic_route(self, route_name: str) -> bool:
        """
        Remove a dynamic route rule.

        Args:
            route_name: Name of the route to remove

        Returns:
            bool: True if route was removed successfully
        """
        try:
            removed = await self.gateway_core.remove_route_rule(route_name)
            if removed:
                logger.info(f"Removed dynamic route: {route_name}")
            return removed
        except Exception as e:
            logger.error(f"Failed to remove dynamic route {route_name}: {e}")
            return False

    def get_route_rules(self) -> list[RouteRule]:
        """
        Get all current route rules.

        Returns:
            List[RouteRule]: Current route rules
        """
        return self.gateway_core.get_routing_config().rules

    async def update_routes_from_services(self) -> None:
        """
        Update routes based on available services from service discovery.
        """
        try:
            # Get all healthy services
            services = await self.discovery_manager.get_all_healthy_services()

            # Create dynamic routes for services that don't have explicit routes
            existing_services = {rule.target_service for rule in self.get_route_rules()}

            for service in services:
                if service.name not in existing_services:
                    # Create a generic route for the service
                    dynamic_route = RouteRule(
                        name=f"dynamic-{service.name}",
                        description=f"Dynamic route for {service.name}",
                        path_pattern=f"/api/v1/{service.name.replace('-', '/')}/*",
                        methods=[
                            RequestMethod.GET,
                            RequestMethod.POST,
                            RequestMethod.PUT,
                            RequestMethod.DELETE,
                        ],
                        target_service=service.name,
                        route_type=RouteType.HTTP,
                        path_rewrite="/$1",
                        priority=100,  # Lower priority than explicit routes
                        therapeutic_priority=service.is_therapeutic(),
                        timeout=30,
                    )

                    await self.add_dynamic_route(dynamic_route)

            logger.info("Updated routes from service discovery")

        except Exception as e:
            logger.error(f"Failed to update routes from services: {e}")


def create_gateway_router(
    gateway_core: GatewayCore, discovery_manager: ServiceDiscoveryManager
) -> APIRouter:
    """
    Create FastAPI router for gateway endpoints.

    Args:
        gateway_core: Gateway core instance
        discovery_manager: Service discovery manager

    Returns:
        APIRouter: Configured router
    """
    router = APIRouter()
    RequestRouter(gateway_core, discovery_manager)

    @router.api_route(
        "/{path:path}",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    )
    async def gateway_route(request: Request, path: str) -> Response:
        """
        Main gateway route handler.

        Args:
            request: FastAPI request
            path: Request path

        Returns:
            Response: Processed response
        """
        return await gateway_core.process_request(request)

    return router
