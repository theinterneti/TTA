"""
API Gateway & Service Integration System for TTA Platform.

This module provides a comprehensive API Gateway that serves as the unified entry point
for all TTA services, providing centralized routing, authentication, rate limiting,
service discovery, and therapeutic safety monitoring.

Key Components:
- Gateway Core: Main request processing engine
- Service Discovery: Dynamic service registration and health monitoring  
- Authentication: JWT-based authentication with therapeutic role management
- Rate Limiting: Intelligent traffic management with therapeutic prioritization
- WebSocket Manager: Real-time communication handler for therapeutic sessions
- Security Scanner: Therapeutic content safety and security validation
- Monitoring: Comprehensive observability and audit logging

The gateway integrates seamlessly with:
- Authentication & User Management System (JWT tokens, user roles, MFA)
- Player Experience Interface (API endpoints, WebSocket chat)
- Core Gameplay Loop (therapeutic session management)
- AI Agent Orchestration (intelligent routing and load balancing)
"""

__version__ = "1.0.0"
__author__ = "TTA Development Team"

# Core gateway components will be imported here as they are implemented
