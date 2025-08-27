"""
Service layer for the API Gateway system.

This module contains all the business logic services for the API Gateway,
including service discovery, authentication, routing, and monitoring.
"""

# Service discovery components
from .service_discovery import RedisServiceRegistry, ServiceDiscoveryError
from .discovery_manager import ServiceDiscoveryManager
from .auto_registration import AutoRegistrationService

# Authentication components
from .auth_service import GatewayAuthService, gateway_auth_service

__all__ = [
    "RedisServiceRegistry",
    "ServiceDiscoveryError",
    "ServiceDiscoveryManager",
    "AutoRegistrationService",
    "GatewayAuthService",
    "gateway_auth_service",
]
