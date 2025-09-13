"""
Data models and schemas for the API Gateway system.

This module contains all the data models, Pydantic schemas, and validation
classes used throughout the API Gateway system.
"""

# Authentication models
from .auth import (
    AuthContext,
    AuthenticationMethod,
    AuthenticationRequest,
    AuthenticationResponse,
    PermissionLevel,
    TherapeuticPermission,
    TokenValidationResult,
    UserPermissions,
    UserRole,
)

# Gateway models
from .gateway import (
    GatewayRequest,
    GatewayResponse,
    RequestMethod,
    RouteRule,
    RouteType,
    RoutingConfig,
    WebSocketConnection,
)

# Rate limiting models
from .rate_limiting import (
    RateLimitConfig,
    RateLimitRule,
    RateLimitScope,
    RateLimitStatus,
    RateLimitType,
    TherapeuticEvent,
    TrafficPriority,
)

# Service models
from .service import (
    LoadBalancingAlgorithm,
    ServiceEndpoint,
    ServiceHealthCheck,
    ServiceInfo,
    ServiceMetrics,
    ServiceRegistry,
    ServiceStatus,
    ServiceType,
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
