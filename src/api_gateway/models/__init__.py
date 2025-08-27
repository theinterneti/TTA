"""
Data models and schemas for the API Gateway system.

This module contains all the data models, Pydantic schemas, and validation
classes used throughout the API Gateway system.
"""

# Service models
from .service import (
    ServiceStatus,
    ServiceType,
    LoadBalancingAlgorithm,
    ServiceEndpoint,
    ServiceHealthCheck,
    ServiceMetrics,
    ServiceInfo,
    ServiceRegistry,
)

# Authentication models
from .auth import (
    UserRole,
    AuthenticationMethod,
    PermissionLevel,
    TherapeuticPermission,
    UserPermissions,
    AuthContext,
    AuthenticationRequest,
    AuthenticationResponse,
    TokenValidationResult,
)

# Rate limiting models
from .rate_limiting import (
    RateLimitType,
    RateLimitScope,
    TrafficPriority,
    RateLimitRule,
    RateLimitConfig,
    RateLimitStatus,
    TherapeuticEvent,
)

# Gateway models
from .gateway import (
    RequestMethod,
    RouteType,
    GatewayRequest,
    GatewayResponse,
    RouteRule,
    RoutingConfig,
    WebSocketConnection,
)

__all__ = [
    # Service models
    "ServiceStatus",
    "ServiceType",
    "LoadBalancingAlgorithm",
    "ServiceEndpoint",
    "ServiceHealthCheck",
    "ServiceMetrics",
    "ServiceInfo",
    "ServiceRegistry",
    # Authentication models
    "UserRole",
    "AuthenticationMethod",
    "PermissionLevel",
    "TherapeuticPermission",
    "UserPermissions",
    "AuthContext",
    "AuthenticationRequest",
    "AuthenticationResponse",
    "TokenValidationResult",
    # Rate limiting models
    "RateLimitType",
    "RateLimitScope",
    "TrafficPriority",
    "RateLimitRule",
    "RateLimitConfig",
    "RateLimitStatus",
    "TherapeuticEvent",
    # Gateway models
    "RequestMethod",
    "RouteType",
    "GatewayRequest",
    "GatewayResponse",
    "RouteRule",
    "RoutingConfig",
    "WebSocketConnection",
]
