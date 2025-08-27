"""
TTA System Integration for Core Gameplay Loop

This module provides comprehensive integration with existing TTA infrastructure including
Character Development System integration, Therapeutic Content Management integration,
Safety Monitoring System integration, Progress Tracking System integration, and
seamless data exchange functions for production-ready system interoperability.
"""

from .tta_system_integration import (
    TTASystemIntegration,
    IntegrationEndpoint,
    IntegrationRequest,
    IntegrationResponse,
    IntegrationType,
    IntegrationStatus
)

__all__ = [
    "TTASystemIntegration",
    "IntegrationEndpoint", 
    "IntegrationRequest",
    "IntegrationResponse",
    "IntegrationType",
    "IntegrationStatus"
]
