"""
Service discovery manager for the API Gateway.

This module provides high-level service discovery management,
including automatic registration, health monitoring, and load balancing.
"""

import asyncio
import logging
from collections.abc import Callable
from uuid import UUID

from ..config import get_gateway_settings
from ..models import LoadBalancingAlgorithm, ServiceInfo, ServiceType
from .service_discovery import RedisServiceRegistry, ServiceDiscoveryError

logger = logging.getLogger(__name__)


class ServiceDiscoveryManager:
    """
    High-level service discovery manager.

    Features:
    - Service registration and lifecycle management
    - Health monitoring and automatic failover
    - Load balancing across healthy services
    - Service event notifications
    """

    def __init__(self):
        """Initialize the service discovery manager."""
        self.settings = get_gateway_settings()
        self.registry = RedisServiceRegistry()
        self._health_monitors: dict[UUID, asyncio.Task] = {}
        self._event_callbacks: list[Callable] = []
        self._load_balancer_state: dict[str, int] = {}  # For round-robin state

    async def initialize(self) -> None:
        """Initialize the service discovery manager."""
        try:
            await self.registry.initialize()
            logger.info("Service discovery manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize service discovery manager: {e}")
            raise ServiceDiscoveryError(f"Initialization failed: {e}")

    async def close(self) -> None:
        """Close the service discovery manager."""
        # Stop all health monitors
        for task in self._health_monitors.values():
            task.cancel()

        # Wait for tasks to complete
        if self._health_monitors:
            await asyncio.gather(
                *self._health_monitors.values(), return_exceptions=True
            )

        await self.registry.close()
        logger.info("Service discovery manager closed")

    async def register_service(
        self, service: ServiceInfo, start_health_monitoring: bool = True
    ) -> bool:
        """
        Register a service and optionally start health monitoring.

        Args:
            service: Service information to register
            start_health_monitoring: Whether to start health monitoring

        Returns:
            bool: True if registration successful
        """
        success = await self.registry.register_service(service)

        if success and start_health_monitoring and service.health_check.enabled:
            await self._start_health_monitoring(service)

        if success:
            await self._notify_service_event("registered", service)

        return success

    async def deregister_service(self, service_id: UUID) -> bool:
        """
        Deregister a service and stop health monitoring.

        Args:
            service_id: Service ID to deregister

        Returns:
            bool: True if deregistration successful
        """
        # Get service info before deregistration
        service = await self.registry.get_service(service_id)

        # Stop health monitoring
        await self._stop_health_monitoring(service_id)

        success = await self.registry.deregister_service(service_id)

        if success and service:
            await self._notify_service_event("deregistered", service)

        return success

    async def get_service_for_request(
        self,
        service_type: ServiceType | None = None,
        service_name: str | None = None,
        tags: list[str] | None = None,
        therapeutic_priority: bool = False,
    ) -> ServiceInfo | None:
        """
        Get a service for handling a request using load balancing.

        Args:
            service_type: Optional service type filter
            service_name: Optional service name filter
            tags: Optional tags filter
            therapeutic_priority: Whether to prioritize therapeutic services

        Returns:
            ServiceInfo: Selected service or None if no suitable service found
        """
        # Get healthy services
        if service_type:
            services = await self.registry.get_healthy_services(service_type)
        else:
            services = await self.registry.get_healthy_services()

        # Apply filters
        if service_name:
            services = [s for s in services if s.name == service_name]

        if tags:
            services = [s for s in services if any(tag in s.tags for tag in tags)]

        # Prioritize therapeutic services if requested
        if therapeutic_priority:
            therapeutic_services = [s for s in services if s.is_therapeutic()]
            if therapeutic_services:
                services = therapeutic_services

        if not services:
            return None

        # Apply load balancing
        return await self._select_service_with_load_balancing(services)

    async def get_all_healthy_services(
        self, service_type: ServiceType | None = None
    ) -> list[ServiceInfo]:
        """
        Get all healthy services, optionally filtered by type.

        Args:
            service_type: Optional service type filter

        Returns:
            List[ServiceInfo]: List of healthy services
        """
        return await self.registry.get_healthy_services(service_type)

    async def get_therapeutic_services(self) -> list[ServiceInfo]:
        """
        Get all healthy therapeutic services.

        Returns:
            List[ServiceInfo]: List of therapeutic services
        """
        services = await self.registry.get_healthy_services()
        return [s for s in services if s.is_therapeutic()]

    async def update_service_metrics(
        self, service_id: UUID, response_time: float, success: bool = True
    ) -> None:
        """
        Update service metrics after a request.

        Args:
            service_id: Service ID
            response_time: Response time in seconds
            success: Whether the request was successful
        """
        service = await self.registry.get_service(service_id)
        if service:
            service.update_metrics(response_time, success)
            await self.registry.register_service(service)  # Update in registry

    def add_event_callback(self, callback: Callable) -> None:
        """
        Add a callback for service events.

        Args:
            callback: Callback function that receives (event_type, service)
        """
        self._event_callbacks.append(callback)

    def remove_event_callback(self, callback: Callable) -> None:
        """
        Remove a service event callback.

        Args:
            callback: Callback function to remove
        """
        if callback in self._event_callbacks:
            self._event_callbacks.remove(callback)

    async def _start_health_monitoring(self, service: ServiceInfo) -> None:
        """Start health monitoring for a service."""
        if service.id in self._health_monitors:
            return  # Already monitoring

        task = asyncio.create_task(self._monitor_service_health(service))
        self._health_monitors[service.id] = task
        logger.info(f"Started health monitoring for service {service.name}")

    async def _stop_health_monitoring(self, service_id: UUID) -> None:
        """Stop health monitoring for a service."""
        if service_id in self._health_monitors:
            task = self._health_monitors.pop(service_id)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.info(f"Stopped health monitoring for service {service_id}")

    async def _monitor_service_health(self, service: ServiceInfo) -> None:
        """Monitor health of a specific service."""
        import aiohttp

        consecutive_failures = 0

        while True:
            try:
                await asyncio.sleep(service.health_check.interval)

                # Perform health check
                health_url = (
                    f"{service.endpoint.url.rstrip('/')}{service.health_check.endpoint}"
                )

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            health_url,
                            timeout=aiohttp.ClientTimeout(
                                total=service.health_check.timeout
                            ),
                        ) as response:
                            is_healthy = (
                                response.status == service.health_check.expected_status
                            )

                            if is_healthy:
                                consecutive_failures = 0
                                await self.registry.update_service_health(
                                    service.id, True
                                )
                            else:
                                consecutive_failures += 1
                                logger.warning(
                                    f"Health check failed for {service.name}: HTTP {response.status}"
                                )

                except Exception as e:
                    consecutive_failures += 1
                    logger.warning(f"Health check error for {service.name}: {e}")

                # Mark as unhealthy after consecutive failures
                if consecutive_failures >= service.health_check.retries:
                    await self.registry.update_service_health(service.id, False)
                    await self._notify_service_event("unhealthy", service)
                    consecutive_failures = 0  # Reset counter

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring for {service.name}: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _select_service_with_load_balancing(
        self, services: list[ServiceInfo]
    ) -> ServiceInfo | None:
        """Select a service using the configured load balancing algorithm."""
        if not services:
            return None

        if len(services) == 1:
            return services[0]

        algorithm = LoadBalancingAlgorithm.ROUND_ROBIN  # Default

        if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin_select(services)
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED:
            return self._weighted_select(services)
        elif algorithm == LoadBalancingAlgorithm.HEALTH_BASED:
            return self._health_based_select(services)
        elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections_select(services)
        else:
            return services[0]  # Fallback

    def _round_robin_select(self, services: list[ServiceInfo]) -> ServiceInfo:
        """Round-robin service selection."""
        services_key = ",".join(sorted([str(s.id) for s in services]))
        current_index = self._load_balancer_state.get(services_key, 0)

        selected_service = services[current_index % len(services)]
        self._load_balancer_state[services_key] = (current_index + 1) % len(services)

        return selected_service

    def _weighted_select(self, services: list[ServiceInfo]) -> ServiceInfo:
        """Weighted service selection based on service weight."""
        import random

        total_weight = sum(service.weight for service in services)
        if total_weight == 0:
            return random.choice(services)

        random_weight = random.randint(1, total_weight)
        current_weight = 0

        for service in services:
            current_weight += service.weight
            if random_weight <= current_weight:
                return service

        return services[-1]  # Fallback

    def _health_based_select(self, services: list[ServiceInfo]) -> ServiceInfo:
        """Health-based service selection (prefer better response times)."""
        # Sort by average response time (ascending)
        sorted_services = sorted(
            services, key=lambda s: s.metrics.average_response_time
        )
        return sorted_services[0]

    def _least_connections_select(self, services: list[ServiceInfo]) -> ServiceInfo:
        """Least connections service selection (simplified using request count)."""
        # Sort by request count (ascending) as a proxy for connections
        sorted_services = sorted(services, key=lambda s: s.metrics.request_count)
        return sorted_services[0]

    async def _notify_service_event(
        self, event_type: str, service: ServiceInfo
    ) -> None:
        """Notify all registered callbacks about a service event."""
        for callback in self._event_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, service)
                else:
                    callback(event_type, service)
            except Exception as e:
                logger.error(f"Error in service event callback: {e}")
