"""
Service layer for the API Gateway system.

This module contains all the business logic services for the API Gateway,
including service discovery, authentication, routing, and monitoring.
"""

# Authentication components
from .auth_service import GatewayAuthService, gateway_auth_service
from .auto_registration import AutoRegistrationService
from .discovery_manager import ServiceDiscoveryManager

# Service discovery components
from .service_discovery import RedisServiceRegistry, ServiceDiscoveryError

__all__ = [
    "RedisServiceRegistry",
    "ServiceDiscoveryError",
    "ServiceDiscoveryManager",
    "AutoRegistrationService",
    "GatewayAuthService",
    "gateway_auth_service",
]
