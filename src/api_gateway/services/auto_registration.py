"""
Automatic service registration for TTA components.

This module provides automatic discovery and registration of TTA services
based on configuration and component startup detection.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from uuid import uuid4

from ..config import get_gateway_settings, load_tta_config_integration
from ..models import ServiceInfo, ServiceType, ServiceEndpoint, ServiceHealthCheck
from .discovery_manager import ServiceDiscoveryManager


logger = logging.getLogger(__name__)


class AutoRegistrationService:
    """
    Automatic service registration for TTA components.
    
    Features:
    - Automatic discovery of TTA services
    - Registration based on configuration
    - Integration with existing TTA components
    - Health check configuration
    """
    
    def __init__(self, discovery_manager: ServiceDiscoveryManager):
        """
        Initialize the auto-registration service.
        
        Args:
            discovery_manager: Service discovery manager instance
        """
        self.discovery_manager = discovery_manager
        self.settings = get_gateway_settings()
        self.tta_config = load_tta_config_integration()
        self._registered_services: Dict[str, ServiceInfo] = {}
    
    async def register_tta_services(self) -> None:
        """Register all configured TTA services."""
        logger.info("Starting automatic registration of TTA services")
        
        # Register Player Experience Interface
        await self._register_player_experience_service()
        
        # Register Authentication Service
        await self._register_authentication_service()
        
        # Register Agent Orchestration Service
        await self._register_agent_orchestration_service()
        
        # Register Core Gameplay Loop Service
        await self._register_gameplay_loop_service()
        
        # Register Database Services
        await self._register_database_services()
        
        logger.info(f"Registered {len(self._registered_services)} TTA services")
    
    async def deregister_all_services(self) -> None:
        """Deregister all auto-registered services."""
        for service_name, service in self._registered_services.items():
            await self.discovery_manager.deregister_service(service.id)
            logger.info(f"Deregistered service: {service_name}")
        
        self._registered_services.clear()
    
    async def _register_player_experience_service(self) -> None:
        """Register the Player Experience Interface service."""
        try:
            # Default configuration for Player Experience Interface
            service = ServiceInfo(
                id=uuid4(),
                name="player-experience-interface",
                version="1.0.0",
                service_type=ServiceType.API,
                endpoint=ServiceEndpoint(
                    host="localhost",
                    port=8080,  # Default port for Player Experience Interface
                    path="/api/v1",
                    scheme="http"
                ),
                weight=100,
                priority=100,
                tags=["api", "player", "experience", "therapeutic"],
                metadata={
                    "description": "Player Experience Interface API",
                    "component": "player_experience",
                    "endpoints": [
                        "/api/v1/auth",
                        "/api/v1/players",
                        "/api/v1/characters",
                        "/api/v1/worlds",
                        "/api/v1/sessions"
                    ]
                },
                health_check=ServiceHealthCheck(
                    enabled=True,
                    endpoint="/health",
                    interval=30,
                    timeout=5,
                    retries=3
                ),
                therapeutic_priority=True,
                safety_validated=True
            )
            
            success = await self.discovery_manager.register_service(service)
            if success:
                self._registered_services["player-experience-interface"] = service
                logger.info("Registered Player Experience Interface service")
            
        except Exception as e:
            logger.error(f"Failed to register Player Experience Interface: {e}")
    
    async def _register_authentication_service(self) -> None:
        """Register the Authentication & User Management service."""
        try:
            service = ServiceInfo(
                id=uuid4(),
                name="authentication-service",
                version="1.0.0",
                service_type=ServiceType.AUTHENTICATION,
                endpoint=ServiceEndpoint(
                    host="localhost",
                    port=8081,  # Default port for Authentication service
                    path="/auth/v1",
                    scheme="http"
                ),
                weight=150,  # Higher weight for critical service
                priority=50,   # Higher priority
                tags=["auth", "authentication", "jwt", "security"],
                metadata={
                    "description": "Authentication & User Management Service",
                    "component": "authentication",
                    "endpoints": [
                        "/auth/v1/login",
                        "/auth/v1/logout",
                        "/auth/v1/refresh",
                        "/auth/v1/users",
                        "/auth/v1/roles"
                    ]
                },
                health_check=ServiceHealthCheck(
                    enabled=True,
                    endpoint="/health",
                    interval=15,  # More frequent health checks
                    timeout=3,
                    retries=2
                ),
                therapeutic_priority=False,
                safety_validated=True
            )
            
            success = await self.discovery_manager.register_service(service)
            if success:
                self._registered_services["authentication-service"] = service
                logger.info("Registered Authentication service")
            
        except Exception as e:
            logger.error(f"Failed to register Authentication service: {e}")
    
    async def _register_agent_orchestration_service(self) -> None:
        """Register the Agent Orchestration service if enabled."""
        try:
            if not self.tta_config.get("agent_orchestration_enabled", False):
                logger.info("Agent Orchestration service not enabled, skipping registration")
                return
            
            port = self.tta_config.get("agent_orchestration_port", 8503)
            
            service = ServiceInfo(
                id=uuid4(),
                name="agent-orchestration",
                version="1.0.0",
                service_type=ServiceType.API,
                endpoint=ServiceEndpoint(
                    host="localhost",
                    port=port,
                    path="/api/v1",
                    scheme="http"
                ),
                weight=120,
                priority=80,
                tags=["ai", "agents", "orchestration", "therapeutic"],
                metadata={
                    "description": "AI Agent Orchestration Service",
                    "component": "agent_orchestration",
                    "endpoints": [
                        "/api/v1/agents",
                        "/api/v1/workflows",
                        "/api/v1/capabilities"
                    ]
                },
                health_check=ServiceHealthCheck(
                    enabled=True,
                    endpoint="/health",
                    interval=30,
                    timeout=5,
                    retries=3
                ),
                therapeutic_priority=True,
                safety_validated=True
            )
            
            success = await self.discovery_manager.register_service(service)
            if success:
                self._registered_services["agent-orchestration"] = service
                logger.info("Registered Agent Orchestration service")
            
        except Exception as e:
            logger.error(f"Failed to register Agent Orchestration service: {e}")
    
    async def _register_gameplay_loop_service(self) -> None:
        """Register the Core Gameplay Loop service."""
        try:
            service = ServiceInfo(
                id=uuid4(),
                name="core-gameplay-loop",
                version="1.0.0",
                service_type=ServiceType.THERAPEUTIC,
                endpoint=ServiceEndpoint(
                    host="localhost",
                    port=8082,  # Default port for Gameplay Loop
                    path="/gameplay/v1",
                    scheme="http"
                ),
                weight=130,
                priority=60,
                tags=["gameplay", "therapeutic", "sessions", "progress"],
                metadata={
                    "description": "Core Gameplay Loop Service",
                    "component": "gameplay_loop",
                    "endpoints": [
                        "/gameplay/v1/sessions",
                        "/gameplay/v1/progress",
                        "/gameplay/v1/therapeutic"
                    ]
                },
                health_check=ServiceHealthCheck(
                    enabled=True,
                    endpoint="/health",
                    interval=30,
                    timeout=5,
                    retries=3
                ),
                therapeutic_priority=True,
                crisis_support=True,
                safety_validated=True
            )
            
            success = await self.discovery_manager.register_service(service)
            if success:
                self._registered_services["core-gameplay-loop"] = service
                logger.info("Registered Core Gameplay Loop service")
            
        except Exception as e:
            logger.error(f"Failed to register Core Gameplay Loop service: {e}")
    
    async def _register_database_services(self) -> None:
        """Register database services (Redis, Neo4j)."""
        try:
            # Register Redis service
            redis_service = ServiceInfo(
                id=uuid4(),
                name="redis-cache",
                version="1.0.0",
                service_type=ServiceType.CACHE,
                endpoint=ServiceEndpoint(
                    host="localhost",
                    port=6379,
                    path="/",
                    scheme="redis"
                ),
                weight=100,
                priority=90,
                tags=["cache", "redis", "storage"],
                metadata={
                    "description": "Redis Cache Service",
                    "component": "redis"
                },
                health_check=ServiceHealthCheck(
                    enabled=False  # Redis doesn't have HTTP health endpoint
                ),
                therapeutic_priority=False,
                safety_validated=True
            )
            
            success = await self.discovery_manager.register_service(redis_service, start_health_monitoring=False)
            if success:
                self._registered_services["redis-cache"] = redis_service
                logger.info("Registered Redis cache service")
            
            # Register Neo4j service
            neo4j_service = ServiceInfo(
                id=uuid4(),
                name="neo4j-database",
                version="1.0.0",
                service_type=ServiceType.DATABASE,
                endpoint=ServiceEndpoint(
                    host="localhost",
                    port=7474,  # HTTP port for Neo4j
                    path="/",
                    scheme="http"
                ),
                weight=100,
                priority=90,
                tags=["database", "neo4j", "graph"],
                metadata={
                    "description": "Neo4j Graph Database",
                    "component": "neo4j",
                    "bolt_port": 7687
                },
                health_check=ServiceHealthCheck(
                    enabled=True,
                    endpoint="/",
                    interval=60,  # Less frequent for database
                    timeout=10,
                    retries=3
                ),
                therapeutic_priority=False,
                safety_validated=True
            )
            
            success = await self.discovery_manager.register_service(neo4j_service)
            if success:
                self._registered_services["neo4j-database"] = neo4j_service
                logger.info("Registered Neo4j database service")
            
        except Exception as e:
            logger.error(f"Failed to register database services: {e}")
    
    def get_registered_services(self) -> Dict[str, ServiceInfo]:
        """Get all registered services."""
        return self._registered_services.copy()
    
    async def refresh_service_registration(self, service_name: str) -> bool:
        """
        Refresh registration for a specific service.
        
        Args:
            service_name: Name of the service to refresh
            
        Returns:
            bool: True if refresh successful
        """
        if service_name not in self._registered_services:
            logger.warning(f"Service {service_name} not found for refresh")
            return False
        
        service = self._registered_services[service_name]
        
        # Update last_seen timestamp
        service.last_seen = service.last_seen.__class__.utcnow()
        
        # Re-register the service
        success = await self.discovery_manager.register_service(service, start_health_monitoring=False)
        
        if success:
            logger.info(f"Refreshed registration for service: {service_name}")
        else:
            logger.error(f"Failed to refresh registration for service: {service_name}")
        
        return success
