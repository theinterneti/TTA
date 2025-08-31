"""
Core gateway data models for the API Gateway.

This module contains models for request/response handling,
routing, and gateway operations.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RequestMethod(str, Enum):
    """HTTP request method enumeration."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class RouteType(str, Enum):
    """Route type enumeration."""

    HTTP = "http"
    WEBSOCKET = "websocket"
    PROXY = "proxy"
    REDIRECT = "redirect"


class GatewayRequest(BaseModel):
    """Gateway request model."""

    # Request identification
    request_id: UUID = Field(
        default_factory=uuid4, description="Unique request identifier"
    )
    correlation_id: str = Field(..., description="Request correlation ID")

    # Request details
    method: RequestMethod = Field(..., description="HTTP method")
    path: str = Field(..., description="Request path")
    query_params: dict[str, str] = Field(
        default_factory=dict, description="Query parameters"
    )
    headers: dict[str, str] = Field(default_factory=dict, description="Request headers")
    body: bytes | None = Field(default=None, description="Request body")

    # Client information
    client_ip: str = Field(..., description="Client IP address")
    user_agent: str = Field(default="unknown", description="Client user agent")

    # Routing information
    target_service: str | None = Field(default=None, description="Target service name")
    route_type: RouteType = Field(default=RouteType.HTTP, description="Route type")

    # Authentication context
    auth_context: dict[str, Any] | None = Field(
        default=None, description="Authentication context"
    )

    # Timestamps
    received_at: datetime = Field(
        default_factory=datetime.utcnow, description="Request received timestamp"
    )

    # Therapeutic context
    therapeutic_session_id: UUID | None = Field(
        default=None, description="Therapeutic session ID"
    )
    is_therapeutic: bool = Field(default=False, description="Therapeutic request flag")
    crisis_mode: bool = Field(default=False, description="Crisis mode flag")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}

    def get_header(self, name: str, default: str | None = None) -> str | None:
        """Get header value by name (case-insensitive)."""
        for key, value in self.headers.items():
            if key.lower() == name.lower():
                return value
        return default

    def is_websocket(self) -> bool:
        """Check if request is a WebSocket upgrade."""
        connection = self.get_header("connection", "").lower()
        upgrade = self.get_header("upgrade", "").lower()
        return "upgrade" in connection and upgrade == "websocket"


class GatewayResponse(BaseModel):
    """Gateway response model."""

    # Response identification
    request_id: UUID = Field(..., description="Associated request ID")
    correlation_id: str = Field(..., description="Request correlation ID")

    # Response details
    status_code: int = Field(..., description="HTTP status code")
    headers: dict[str, str] = Field(
        default_factory=dict, description="Response headers"
    )
    body: bytes | None = Field(default=None, description="Response body")

    # Processing information
    service_name: str | None = Field(
        default=None, description="Service that handled the request"
    )
    processing_time: float = Field(..., description="Processing time in seconds")

    # Timestamps
    completed_at: datetime = Field(
        default_factory=datetime.utcnow, description="Response completion timestamp"
    )

    # Error information
    error: str | None = Field(default=None, description="Error message if any")
    error_code: str | None = Field(default=None, description="Error code if any")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}

    def is_success(self) -> bool:
        """Check if response indicates success."""
        return 200 <= self.status_code < 300

    def is_error(self) -> bool:
        """Check if response indicates an error."""
        return self.status_code >= 400


class RouteRule(BaseModel):
    """Route rule for request routing."""

    # Rule identification
    name: str = Field(..., description="Rule name")
    description: str | None = Field(default=None, description="Rule description")
    enabled: bool = Field(default=True, description="Rule enabled status")
    priority: int = Field(
        default=100, description="Rule priority (lower = higher priority)"
    )

    # Matching criteria
    path_pattern: str = Field(..., description="Path pattern to match")
    methods: list[RequestMethod] = Field(
        default_factory=list, description="HTTP methods to match"
    )
    headers: dict[str, str] = Field(
        default_factory=dict, description="Headers to match"
    )

    # Routing configuration
    target_service: str = Field(..., description="Target service name")
    route_type: RouteType = Field(default=RouteType.HTTP, description="Route type")
    path_rewrite: str | None = Field(default=None, description="Path rewrite pattern")

    # Load balancing
    load_balancing_enabled: bool = Field(
        default=True, description="Enable load balancing"
    )
    sticky_sessions: bool = Field(default=False, description="Enable sticky sessions")

    # Timeouts and retries
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retries: int = Field(default=3, description="Number of retries")

    # Therapeutic configuration
    therapeutic_priority: bool = Field(
        default=False, description="Therapeutic priority routing"
    )
    crisis_bypass: bool = Field(
        default=False, description="Bypass normal routing for crisis"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Rule creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Rule update timestamp"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    def matches_request(self, request: GatewayRequest) -> bool:
        """Check if rule matches a request."""
        import fnmatch

        # Check path pattern
        if not fnmatch.fnmatch(request.path, self.path_pattern):
            return False

        # Check methods
        if self.methods and request.method not in self.methods:
            return False

        # Check headers
        for header_name, header_value in self.headers.items():
            request_header = request.get_header(header_name)
            if not request_header or not fnmatch.fnmatch(request_header, header_value):
                return False

        return True


class RoutingConfig(BaseModel):
    """Complete routing configuration."""

    # Global configuration
    enabled: bool = Field(default=True, description="Routing enabled")
    default_timeout: int = Field(default=30, description="Default request timeout")
    default_retries: int = Field(default=3, description="Default retry count")

    # Rules
    rules: list[RouteRule] = Field(default_factory=list, description="Routing rules")

    # Load balancing
    default_load_balancing: str = Field(
        default="round_robin", description="Default load balancing algorithm"
    )
    health_check_enabled: bool = Field(
        default=True, description="Enable health checks for routing"
    )

    # Circuit breaker
    circuit_breaker_enabled: bool = Field(
        default=True, description="Enable circuit breaker"
    )
    failure_threshold: int = Field(
        default=5, description="Circuit breaker failure threshold"
    )
    recovery_timeout: int = Field(
        default=60, description="Circuit breaker recovery timeout"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}

    def get_matching_rules(self, request: GatewayRequest) -> list[RouteRule]:
        """Get matching rules for a request, sorted by priority."""
        matching_rules = [
            rule
            for rule in self.rules
            if rule.enabled and rule.matches_request(request)
        ]
        return sorted(matching_rules, key=lambda r: r.priority)


class WebSocketConnection(BaseModel):
    """WebSocket connection information."""

    # Connection identification
    connection_id: UUID = Field(
        default_factory=uuid4, description="Unique connection identifier"
    )
    user_id: UUID | None = Field(default=None, description="Associated user ID")
    session_id: str | None = Field(default=None, description="Session identifier")

    # Connection details
    client_ip: str = Field(..., description="Client IP address")
    user_agent: str = Field(default="unknown", description="Client user agent")

    # Routing information
    target_service: str = Field(..., description="Target service for WebSocket")
    path: str = Field(..., description="WebSocket path")

    # Status
    connected: bool = Field(default=True, description="Connection status")

    # Timestamps
    connected_at: datetime = Field(
        default_factory=datetime.utcnow, description="Connection timestamp"
    )
    last_activity: datetime = Field(
        default_factory=datetime.utcnow, description="Last activity timestamp"
    )

    # Therapeutic context
    therapeutic_session_id: UUID | None = Field(
        default=None, description="Therapeutic session ID"
    )
    is_therapeutic: bool = Field(
        default=False, description="Therapeutic connection flag"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
