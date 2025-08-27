"""
Service discovery and registration system for the API Gateway.

This module provides Redis-backed service discovery with automatic
registration, health monitoring, and service lifecycle management.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from uuid import UUID

import redis.asyncio as redis
from redis.exceptions import ConnectionError, RedisError

from ..config import get_gateway_settings
from ..models import ServiceInfo, ServiceStatus, ServiceType, ServiceRegistry


logger = logging.getLogger(__name__)


class ServiceDiscoveryError(Exception):
    """Service discovery related errors."""
    pass


class RedisServiceRegistry:
    """
    Redis-backed service registry for service discovery.
    
    Features:
    - Service registration and deregistration
    - Health monitoring with TTL
    - Service lookup and filtering
    - Automatic cleanup of stale services
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize the Redis service registry.
        
        Args:
            redis_client: Optional Redis client instance
        """
        self.settings = get_gateway_settings()
        self.redis_client = redis_client
        self._registry_key = "tta:gateway:services"
        self._health_key_prefix = "tta:gateway:health"
        self._lock_key = "tta:gateway:registry_lock"
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> None:
        """Initialize the service registry."""
        if self.redis_client is None:
            try:
                self.redis_client = redis.from_url(
                    self.settings.redis_url,
                    **self.settings.redis_connection_kwargs
                )
                # Test connection
                await self.redis_client.ping()
                logger.info("Connected to Redis for service discovery")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise ServiceDiscoveryError(f"Redis connection failed: {e}")
        
        # Start cleanup task
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_stale_services())
    
    async def close(self) -> None:
        """Close the service registry and cleanup resources."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_client:
            await self.redis_client.close()
    
    async def register_service(self, service: ServiceInfo) -> bool:
        """
        Register a service in the registry.
        
        Args:
            service: Service information to register
            
        Returns:
            bool: True if registration successful
        """
        try:
            service_key = f"{self._registry_key}:{service.id}"
            health_key = f"{self._health_key_prefix}:{service.id}"
            
            # Serialize service info
            service_data = service.json()
            
            # Use pipeline for atomic operations
            async with self.redis_client.pipeline() as pipe:
                # Store service info
                pipe.hset(self._registry_key, str(service.id), service_data)
                
                # Set health status with TTL
                pipe.setex(
                    health_key,
                    self.settings.health_check_interval * 3,  # 3x interval for TTL
                    "healthy"
                )
                
                # Add to service type index
                type_key = f"{self._registry_key}:type:{service.service_type}"
                pipe.sadd(type_key, str(service.id))
                
                # Add to tags index
                for tag in service.tags:
                    tag_key = f"{self._registry_key}:tag:{tag}"
                    pipe.sadd(tag_key, str(service.id))
                
                await pipe.execute()
            
            logger.info(f"Registered service {service.name} ({service.id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service.id}: {e}")
            return False
    
    async def deregister_service(self, service_id: UUID) -> bool:
        """
        Deregister a service from the registry.
        
        Args:
            service_id: Service ID to deregister
            
        Returns:
            bool: True if deregistration successful
        """
        try:
            service_id_str = str(service_id)
            
            # Get service info first
            service_data = await self.redis_client.hget(self._registry_key, service_id_str)
            if not service_data:
                logger.warning(f"Service {service_id} not found for deregistration")
                return False
            
            service = ServiceInfo.parse_raw(service_data)
            
            # Use pipeline for atomic operations
            async with self.redis_client.pipeline() as pipe:
                # Remove from main registry
                pipe.hdel(self._registry_key, service_id_str)
                
                # Remove health key
                health_key = f"{self._health_key_prefix}:{service_id}"
                pipe.delete(health_key)
                
                # Remove from type index
                type_key = f"{self._registry_key}:type:{service.service_type}"
                pipe.srem(type_key, service_id_str)
                
                # Remove from tags index
                for tag in service.tags:
                    tag_key = f"{self._registry_key}:tag:{tag}"
                    pipe.srem(tag_key, service_id_str)
                
                await pipe.execute()
            
            logger.info(f"Deregistered service {service.name} ({service_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deregister service {service_id}: {e}")
            return False
    
    async def get_service(self, service_id: UUID) -> Optional[ServiceInfo]:
        """
        Get a specific service by ID.
        
        Args:
            service_id: Service ID to retrieve
            
        Returns:
            ServiceInfo: Service information if found
        """
        try:
            service_data = await self.redis_client.hget(self._registry_key, str(service_id))
            if service_data:
                return ServiceInfo.parse_raw(service_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get service {service_id}: {e}")
            return None
    
    async def get_all_services(self) -> List[ServiceInfo]:
        """
        Get all registered services.
        
        Returns:
            List[ServiceInfo]: List of all services
        """
        try:
            services_data = await self.redis_client.hgetall(self._registry_key)
            services = []
            
            for service_data in services_data.values():
                try:
                    service = ServiceInfo.parse_raw(service_data)
                    services.append(service)
                except Exception as e:
                    logger.warning(f"Failed to parse service data: {e}")
            
            return services
        except Exception as e:
            logger.error(f"Failed to get all services: {e}")
            return []
    
    async def get_services_by_type(self, service_type: ServiceType) -> List[ServiceInfo]:
        """
        Get services by type.
        
        Args:
            service_type: Service type to filter by
            
        Returns:
            List[ServiceInfo]: List of services of the specified type
        """
        try:
            type_key = f"{self._registry_key}:type:{service_type}"
            service_ids = await self.redis_client.smembers(type_key)
            
            services = []
            for service_id in service_ids:
                service = await self.get_service(UUID(service_id))
                if service:
                    services.append(service)
            
            return services
        except Exception as e:
            logger.error(f"Failed to get services by type {service_type}: {e}")
            return []
    
    async def get_services_by_tag(self, tag: str) -> List[ServiceInfo]:
        """
        Get services by tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List[ServiceInfo]: List of services with the specified tag
        """
        try:
            tag_key = f"{self._registry_key}:tag:{tag}"
            service_ids = await self.redis_client.smembers(tag_key)
            
            services = []
            for service_id in service_ids:
                service = await self.get_service(UUID(service_id))
                if service:
                    services.append(service)
            
            return services
        except Exception as e:
            logger.error(f"Failed to get services by tag {tag}: {e}")
            return []
    
    async def get_healthy_services(self, service_type: Optional[ServiceType] = None) -> List[ServiceInfo]:
        """
        Get all healthy services, optionally filtered by type.
        
        Args:
            service_type: Optional service type filter
            
        Returns:
            List[ServiceInfo]: List of healthy services
        """
        if service_type:
            services = await self.get_services_by_type(service_type)
        else:
            services = await self.get_all_services()
        
        # Filter by health status
        healthy_services = []
        for service in services:
            if await self._is_service_healthy(service.id):
                service.status = ServiceStatus.HEALTHY
                healthy_services.append(service)
            else:
                service.status = ServiceStatus.UNHEALTHY
        
        return healthy_services
    
    async def update_service_health(self, service_id: UUID, is_healthy: bool) -> bool:
        """
        Update service health status.
        
        Args:
            service_id: Service ID
            is_healthy: Health status
            
        Returns:
            bool: True if update successful
        """
        try:
            health_key = f"{self._health_key_prefix}:{service_id}"
            
            if is_healthy:
                # Set health with TTL
                await self.redis_client.setex(
                    health_key,
                    self.settings.health_check_interval * 3,
                    "healthy"
                )
            else:
                # Mark as unhealthy
                await self.redis_client.setex(
                    health_key,
                    self.settings.health_check_interval,
                    "unhealthy"
                )
            
            return True
        except Exception as e:
            logger.error(f"Failed to update health for service {service_id}: {e}")
            return False
    
    async def _is_service_healthy(self, service_id: UUID) -> bool:
        """Check if a service is healthy based on TTL."""
        try:
            health_key = f"{self._health_key_prefix}:{service_id}"
            health_status = await self.redis_client.get(health_key)
            return health_status == "healthy"
        except Exception:
            return False
    
    async def _cleanup_stale_services(self) -> None:
        """Background task to cleanup stale services."""
        while True:
            try:
                await asyncio.sleep(self.settings.health_check_interval)
                
                # Get all services
                services = await self.get_all_services()
                
                for service in services:
                    if not await self._is_service_healthy(service.id):
                        logger.info(f"Removing stale service {service.name} ({service.id})")
                        await self.deregister_service(service.id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(5)  # Wait before retrying
