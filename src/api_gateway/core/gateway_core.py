"""
Core gateway request processing engine for the API Gateway.

This module provides the main GatewayCore class that handles async request processing,
routing logic with service discovery integration, and request/response transformation.
"""

import asyncio
import logging
import time
from uuid import uuid4

import aiohttp
from fastapi import Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from ..config import get_gateway_settings
from ..models import (
    GatewayRequest,
    RequestMethod,
    RouteRule,
    RoutingConfig,
    ServiceInfo,
)
from ..monitoring.metrics import metrics_collector
from ..services import ServiceDiscoveryManager
from .service_router import ServiceRouter

logger = logging.getLogger(__name__)


class GatewayCore:
    """
    Core gateway request processing engine.

    Handles async request processing, routing logic with service discovery integration,
    and request/response transformation capabilities.
    """

    def __init__(self, discovery_manager: ServiceDiscoveryManager):
        """
        Initialize the gateway core.

        Args:
            discovery_manager: Service discovery manager instance
        """
        self.settings = get_gateway_settings()
        self.discovery_manager = discovery_manager
        self.routing_config = RoutingConfig()
        self._http_session: aiohttp.ClientSession | None = None
        self._active_requests: dict[str, GatewayRequest] = {}

        # Initialize service router with load balancing and circuit breakers
        self.service_router = ServiceRouter(discovery_manager)

    async def initialize(self) -> None:
        """Initialize the gateway core."""
        # Create HTTP session for backend requests
        timeout = aiohttp.ClientTimeout(total=self.settings.health_check_timeout)
        connector = aiohttp.TCPConnector(
            limit=100,  # Connection pool limit
            limit_per_host=30,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )

        self._http_session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                "User-Agent": "TTA-API-Gateway/1.0.0",
                "X-Gateway-Version": "1.0.0",
            },
        )

        logger.info("Gateway core initialized")

    async def close(self) -> None:
        """Close the gateway core and cleanup resources."""
        if self._http_session:
            await self._http_session.close()

        logger.info("Gateway core closed")

    async def process_request(self, request: Request) -> Response:
        """
        Process an incoming request through the gateway.

        Args:
            request: The incoming FastAPI request

        Returns:
            Response: The processed response
        """
        start_time = time.time()
        correlation_id = getattr(request.state, "correlation_id", str(uuid4()))

        try:
            # Convert FastAPI request to gateway request
            gateway_request = await self._create_gateway_request(
                request, correlation_id
            )

            # Store active request for monitoring
            self._active_requests[correlation_id] = gateway_request

            # Find matching route
            route_rule = await self._find_matching_route(gateway_request)
            if not route_rule:
                return self._create_error_response(
                    404, "Route not found", correlation_id
                )

            # Get target service
            target_service = await self._get_target_service(route_rule, gateway_request)
            if not target_service:
                return self._create_error_response(
                    503, "Service unavailable", correlation_id
                )

            # Process the request
            response = await self._route_request(
                gateway_request, route_rule, target_service
            )

            # Record metrics
            processing_time = time.time() - start_time
            metrics_collector.record_request(
                gateway_request.method.value,
                gateway_request.path,
                response.status_code,
                processing_time,
                target_service.name,
            )

            # Update service metrics through service router
            await self.service_router.update_service_metrics(
                str(target_service.id),
                processing_time,
                response.status_code < 400,
                therapeutic=gateway_request.is_therapeutic,
                crisis=gateway_request.crisis_mode,
            )

            return response

        except Exception as e:
            logger.error(
                f"Error processing request {correlation_id}: {e}",
                extra={
                    "correlation_id": correlation_id,
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(e),
                },
                exc_info=True,
            )

            processing_time = time.time() - start_time
            metrics_collector.record_request(
                request.method, request.url.path, 500, processing_time, "gateway"
            )

            return self._create_error_response(
                500, "Internal gateway error", correlation_id
            )

        finally:
            # Remove from active requests
            self._active_requests.pop(correlation_id, None)

    async def _create_gateway_request(
        self, request: Request, correlation_id: str
    ) -> GatewayRequest:
        """
        Convert FastAPI request to gateway request.

        Args:
            request: FastAPI request
            correlation_id: Request correlation ID

        Returns:
            GatewayRequest: Gateway request object
        """
        # Read request body
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
            except Exception as e:
                logger.warning(f"Failed to read request body: {e}")

        # Extract authentication context
        auth_context = getattr(request.state, "auth_context", None)
        auth_context_dict = None
        if auth_context:
            auth_context_dict = {
                "user_id": str(auth_context.user_id),
                "username": auth_context.username,
                "role": auth_context.permissions.role.value,
                "therapeutic_context": auth_context.is_therapeutic_context(),
                "crisis_mode": auth_context.crisis_mode,
            }

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        return GatewayRequest(
            correlation_id=correlation_id,
            method=RequestMethod(request.method),
            path=request.url.path,
            query_params=dict(request.query_params),
            headers=dict(request.headers),
            body=body,
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent", "unknown"),
            auth_context=auth_context_dict,
            therapeutic_session_id=getattr(
                request.state, "therapeutic_session_id", None
            ),
            is_therapeutic=getattr(request.state, "is_therapeutic_context", False),
            crisis_mode=getattr(request.state, "crisis_mode", False),
        )

    async def _find_matching_route(
        self, gateway_request: GatewayRequest
    ) -> RouteRule | None:
        """
        Find matching route rule for the request.

        Args:
            gateway_request: Gateway request

        Returns:
            Optional[RouteRule]: Matching route rule if found
        """
        matching_rules = self.routing_config.get_matching_rules(gateway_request)

        if not matching_rules:
            # Try to create dynamic route based on path
            return await self._create_dynamic_route(gateway_request)

        # Return the highest priority rule
        return matching_rules[0]

    async def _create_dynamic_route(
        self, gateway_request: GatewayRequest
    ) -> RouteRule | None:
        """
        Create dynamic route based on request path and available services.

        Args:
            gateway_request: Gateway request

        Returns:
            Optional[RouteRule]: Dynamic route rule if service found
        """
        path_parts = gateway_request.path.strip("/").split("/")

        # Try to match path to service name
        if len(path_parts) >= 2 and path_parts[0] == "api":
            service_name = path_parts[1]

            # Map common service names
            service_mapping = {
                "auth": "authentication-service",
                "players": "player-experience-interface",
                "characters": "player-experience-interface",
                "worlds": "player-experience-interface",
                "sessions": "core-gameplay-loop",
                "gameplay": "core-gameplay-loop",
                "agents": "agent-orchestration",
            }

            target_service_name = service_mapping.get(service_name, service_name)

            # Check if service exists
            services = await self.discovery_manager.get_all_healthy_services()
            target_service = next(
                (s for s in services if s.name == target_service_name), None
            )

            if target_service:
                return RouteRule(
                    name=f"dynamic-{service_name}",
                    description=f"Dynamic route for {service_name}",
                    path_pattern=f"/api/{service_name}/*",
                    methods=[gateway_request.method],
                    target_service=target_service_name,
                    therapeutic_priority=gateway_request.is_therapeutic,
                    priority=200,  # Lower priority than configured routes
                )

        return None

    async def _get_target_service(
        self, route_rule: RouteRule, gateway_request: GatewayRequest
    ) -> ServiceInfo | None:
        """
        Get target service for the route using service router with load balancing.

        Args:
            route_rule: Route rule
            gateway_request: Gateway request

        Returns:
            Optional[ServiceInfo]: Target service if available
        """
        # Use service router for intelligent service selection with load balancing
        service = await self.service_router.select_service(
            service_name=route_rule.target_service, gateway_request=gateway_request
        )

        return service

    async def _route_request(
        self,
        gateway_request: GatewayRequest,
        route_rule: RouteRule,
        target_service: ServiceInfo,
    ) -> Response:
        """
        Route request to target service with failover and circuit breaker protection.

        Args:
            gateway_request: Gateway request
            route_rule: Route rule
            target_service: Target service

        Returns:
            Response: Service response
        """
        # Use service router for request routing with failover
        try:
            response = await self.service_router.route_request_with_failover(
                service_name=route_rule.target_service,
                gateway_request=gateway_request,
                request_func=self._make_http_request,
                route_rule=route_rule,
            )
            return response

        except Exception as e:
            logger.error(
                f"Failed to route request after all retries: {e}",
                extra={
                    "correlation_id": gateway_request.correlation_id,
                    "service": route_rule.target_service,
                    "error": str(e),
                },
            )
            return self._create_error_response(
                503, "Service unavailable after retries", gateway_request.correlation_id
            )

    async def _make_http_request(
        self,
        target_service: ServiceInfo,
        route_rule: RouteRule,
        gateway_request: GatewayRequest,
    ) -> Response:
        """
        Make HTTP request to target service.

        Args:
            target_service: Target service
            route_rule: Route rule
            gateway_request: Gateway request

        Returns:
            Response: Service response
        """
        try:
            # Transform request path if needed
            target_path = self._transform_request_path(gateway_request.path, route_rule)

            # Build target URL
            target_url = f"{target_service.endpoint.url.rstrip('/')}{target_path}"

            # Prepare headers
            headers = self._prepare_request_headers(gateway_request, target_service)

            # Make request to target service
            async with self._http_session.request(
                method=gateway_request.method.value,
                url=target_url,
                params=gateway_request.query_params,
                headers=headers,
                data=gateway_request.body,
                timeout=aiohttp.ClientTimeout(total=route_rule.timeout),
            ) as response:
                # Read response
                response_body = await response.read()

                # Transform response
                return await self._transform_response(
                    response, response_body, gateway_request, target_service
                )

        except asyncio.TimeoutError:
            logger.warning(
                f"Request timeout to service {target_service.name}",
                extra={
                    "correlation_id": gateway_request.correlation_id,
                    "service": target_service.name,
                    "timeout": route_rule.timeout,
                },
            )
            raise Exception(f"Service timeout: {target_service.name}") from None

        except aiohttp.ClientError as e:
            logger.error(
                f"Client error routing to service {target_service.name}: {e}",
                extra={
                    "correlation_id": gateway_request.correlation_id,
                    "service": target_service.name,
                    "error": str(e),
                },
            )
            raise Exception(f"Service connection error: {target_service.name}") from e

    def _transform_request_path(self, original_path: str, route_rule: RouteRule) -> str:
        """
        Transform request path based on route rule.

        Args:
            original_path: Original request path
            route_rule: Route rule

        Returns:
            str: Transformed path
        """
        if route_rule.path_rewrite:
            # Apply path rewrite pattern
            import re

            pattern = route_rule.path_pattern.replace("*", "(.*)")
            match = re.match(pattern, original_path)
            if match:
                # Replace placeholders in rewrite pattern
                transformed_path = route_rule.path_rewrite
                for i, group in enumerate(match.groups()):
                    transformed_path = transformed_path.replace(f"${i + 1}", group)
                return transformed_path

        return original_path

    def _prepare_request_headers(
        self, gateway_request: GatewayRequest, target_service: ServiceInfo
    ) -> dict[str, str]:
        """
        Prepare headers for the target service request.

        Args:
            gateway_request: Gateway request
            target_service: Target service

        Returns:
            Dict[str, str]: Prepared headers
        """
        headers = gateway_request.headers.copy()

        # Remove hop-by-hop headers
        hop_by_hop_headers = {
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
        }

        for header in hop_by_hop_headers:
            headers.pop(header, None)

        # Add gateway headers
        headers["X-Forwarded-For"] = gateway_request.client_ip
        headers["X-Forwarded-Proto"] = (
            "https" if self.settings.is_production else "http"
        )
        headers["X-Forwarded-Host"] = headers.get("host", "localhost")
        headers["X-Gateway-Request-ID"] = gateway_request.correlation_id
        headers["X-Gateway-Service"] = target_service.name

        # Add authentication context if available
        if gateway_request.auth_context:
            headers["X-User-ID"] = gateway_request.auth_context.get("user_id", "")
            headers["X-User-Role"] = gateway_request.auth_context.get("role", "")
            headers["X-Therapeutic-Context"] = str(
                gateway_request.auth_context.get("therapeutic_context", False)
            )

        # Add therapeutic headers
        if gateway_request.is_therapeutic:
            headers["X-Therapeutic-Session"] = "true"
            if gateway_request.therapeutic_session_id:
                headers["X-Therapeutic-Session-ID"] = str(
                    gateway_request.therapeutic_session_id
                )

        if gateway_request.crisis_mode:
            headers["X-Crisis-Mode"] = "true"

        return headers

    async def _transform_response(
        self,
        aiohttp_response: aiohttp.ClientResponse,
        response_body: bytes,
        gateway_request: GatewayRequest,
        target_service: ServiceInfo,
    ) -> Response:
        """
        Transform service response for the client.

        Args:
            aiohttp_response: aiohttp response from service
            response_body: Response body bytes
            gateway_request: Original gateway request
            target_service: Target service info

        Returns:
            Response: Transformed response
        """
        # Prepare response headers
        response_headers = {}

        # Copy safe headers from service response
        safe_headers = {
            "content-type",
            "content-length",
            "cache-control",
            "expires",
            "last-modified",
            "etag",
            "vary",
            "content-encoding",
            "content-language",
        }

        for header_name, header_value in aiohttp_response.headers.items():
            if header_name.lower() in safe_headers:
                response_headers[header_name] = header_value

        # Add gateway headers
        response_headers["X-Gateway-Service"] = target_service.name
        response_headers["X-Gateway-Request-ID"] = gateway_request.correlation_id
        response_headers["X-Gateway-Version"] = "1.0.0"

        # Add therapeutic safety headers if applicable
        if gateway_request.is_therapeutic:
            response_headers["X-Therapeutic-Response"] = "true"
            response_headers["X-Therapeutic-Safety"] = "validated"

        # Handle different content types
        content_type = aiohttp_response.headers.get("content-type", "").lower()

        if "application/json" in content_type:
            # Handle JSON responses
            try:
                import json

                response_data = json.loads(response_body.decode("utf-8"))

                # Add gateway metadata to JSON responses
                if isinstance(response_data, dict):
                    response_data["_gateway"] = {
                        "service": target_service.name,
                        "request_id": gateway_request.correlation_id,
                        "version": "1.0.0",
                    }

                return JSONResponse(
                    content=response_data,
                    status_code=aiohttp_response.status,
                    headers=response_headers,
                )
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fallback to raw response if JSON parsing fails
                pass

        # Handle streaming responses
        if (
            "text/event-stream" in content_type
            or "application/octet-stream" in content_type
        ):

            async def stream_response():
                yield response_body

            return StreamingResponse(
                stream_response(),
                status_code=aiohttp_response.status,
                headers=response_headers,
                media_type=content_type,
            )

        # Default response handling
        return Response(
            content=response_body,
            status_code=aiohttp_response.status,
            headers=response_headers,
            media_type=content_type.split(";")[0] if content_type else None,
        )

    def _create_error_response(
        self, status_code: int, message: str, correlation_id: str
    ) -> JSONResponse:
        """
        Create standardized error response.

        Args:
            status_code: HTTP status code
            message: Error message
            correlation_id: Request correlation ID

        Returns:
            JSONResponse: Error response
        """
        error_response = {
            "error": {
                "code": status_code,
                "message": message,
                "request_id": correlation_id,
                "timestamp": time.time(),
                "gateway_version": "1.0.0",
            }
        }

        return JSONResponse(
            content=error_response,
            status_code=status_code,
            headers={
                "X-Gateway-Request-ID": correlation_id,
                "X-Gateway-Version": "1.0.0",
                "Content-Type": "application/json",
            },
        )

    def get_active_requests(self) -> dict[str, GatewayRequest]:
        """
        Get currently active requests.

        Returns:
            Dict[str, GatewayRequest]: Active requests by correlation ID
        """
        return self._active_requests.copy()

    def get_routing_config(self) -> RoutingConfig:
        """
        Get current routing configuration.

        Returns:
            RoutingConfig: Current routing configuration
        """
        return self.routing_config

    def update_routing_config(self, config: RoutingConfig) -> None:
        """
        Update routing configuration.

        Args:
            config: New routing configuration
        """
        self.routing_config = config
        logger.info("Routing configuration updated")

    async def add_route_rule(self, rule: RouteRule) -> None:
        """
        Add a new route rule.

        Args:
            rule: Route rule to add
        """
        self.routing_config.rules.append(rule)
        # Sort rules by priority
        self.routing_config.rules.sort(key=lambda r: r.priority)

        logger.info(f"Added route rule: {rule.name}")

    async def remove_route_rule(self, rule_name: str) -> bool:
        """
        Remove a route rule by name.

        Args:
            rule_name: Name of the rule to remove

        Returns:
            bool: True if rule was removed
        """
        original_count = len(self.routing_config.rules)
        self.routing_config.rules = [
            rule for rule in self.routing_config.rules if rule.name != rule_name
        ]

        removed = len(self.routing_config.rules) < original_count
        if removed:
            logger.info(f"Removed route rule: {rule_name}")

        return removed
