"""
Enhanced service router with load balancing and circuit breaker integration.

This module provides advanced service routing capabilities including
load balancing algorithms, circuit breaker patterns, and failover mechanisms.
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..config import get_gateway_settings
from ..models import GatewayRequest, ServiceInfo
from ..services import ServiceDiscoveryManager
from .circuit_breaker import (
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitBreakerManager,
)
from .load_balancer import LoadBalancingStrategy, create_load_balancer

logger = logging.getLogger(__name__)


class FailoverStrategy(Enum):
    """Failover strategy types."""

    NONE = "none"
    IMMEDIATE = "immediate"
    RETRY_DIFFERENT_SERVICE = "retry_different_service"
    RETRY_WITH_BACKOFF = "retry_with_backoff"


@dataclass
class ServiceRouterConfig:
    """Configuration for service router."""

    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.HEALTH_BASED
    failover_strategy: FailoverStrategy = FailoverStrategy.RETRY_DIFFERENT_SERVICE
    max_retries: int = 3
    retry_delay: float = 1.0
    circuit_breaker_config: CircuitBreakerConfig | None = None

    # Therapeutic-specific settings
    therapeutic_max_retries: int = 5
    therapeutic_retry_delay: float = 0.5
    crisis_max_retries: int = 10  # More aggressive retries for crisis situations


class ServiceRouter:
    """
    Enhanced service router with load balancing and circuit breaker integration.

    Provides intelligent service selection, load balancing, circuit breaker protection,
    and failover mechanisms with special handling for therapeutic requests.
    """

    def __init__(
        self,
        discovery_manager: ServiceDiscoveryManager,
        config: ServiceRouterConfig | None = None,
    ):
        """
        Initialize the service router.

        Args:
            discovery_manager: Service discovery manager
            config: Router configuration
        """
        self.discovery_manager = discovery_manager
        self.config = config or ServiceRouterConfig()
        self.settings = get_gateway_settings()

        # Initialize load balancer
        self.load_balancer = create_load_balancer(self.config.load_balancing_strategy)

        # Initialize circuit breaker manager
        self.circuit_breaker_manager = CircuitBreakerManager(
            self.config.circuit_breaker_config
        )

        # Service selection cache
        self._service_cache: dict[str, list[ServiceInfo]] = {}
        self._cache_ttl = 30.0  # Cache TTL in seconds
        self._last_cache_update: dict[str, float] = {}

    async def select_service(
        self, service_name: str, gateway_request: GatewayRequest
    ) -> ServiceInfo | None:
        """
        Select the best service instance for a request.

        Args:
            service_name: Name of the service to select
            gateway_request: Gateway request context

        Returns:
            Selected service instance or None if no healthy service available
        """
        try:
            # Get available services
            services = await self._get_available_services(service_name)

            if not services:
                logger.warning(f"No services available for {service_name}")
                return None

            # Filter services through circuit breakers
            healthy_services = self.circuit_breaker_manager.get_healthy_services(
                services
            )

            if not healthy_services:
                logger.warning(f"No healthy services available for {service_name}")

                # In crisis mode, allow using unhealthy services as last resort
                if gateway_request.crisis_mode:
                    logger.warning(
                        f"Crisis mode: using potentially unhealthy services for {service_name}"
                    )
                    healthy_services = services
                else:
                    return None

            # Use load balancer to select service
            selected_service = self.load_balancer.select_service(
                healthy_services,
                therapeutic_priority=gateway_request.is_therapeutic,
                crisis_mode=gateway_request.crisis_mode,
            )

            if selected_service:
                # Update load balancer metrics
                self.load_balancer.increment_connections(str(selected_service.id))

                logger.debug(
                    f"Selected service {selected_service.name} (ID: {selected_service.id}) "
                    f"for request {gateway_request.correlation_id}"
                )

            return selected_service

        except Exception as e:
            logger.error(f"Error selecting service for {service_name}: {e}")
            return None

    async def route_request_with_failover(
        self,
        service_name: str,
        gateway_request: GatewayRequest,
        request_func,
        *args,
        **kwargs,
    ) -> Any:
        """
        Route request with failover and retry logic.

        Args:
            service_name: Name of the service
            gateway_request: Gateway request context
            request_func: Function to execute the request
            *args: Arguments for request function
            **kwargs: Keyword arguments for request function

        Returns:
            Response from the service

        Raises:
            Exception: If all retry attempts fail
        """
        # Determine retry parameters based on request type
        max_retries = self.config.max_retries
        retry_delay = self.config.retry_delay

        if gateway_request.crisis_mode:
            max_retries = self.config.crisis_max_retries
            retry_delay = self.config.therapeutic_retry_delay
        elif gateway_request.is_therapeutic:
            max_retries = self.config.therapeutic_max_retries
            retry_delay = self.config.therapeutic_retry_delay

        last_exception = None
        attempted_services = set()

        for attempt in range(max_retries + 1):
            try:
                # Select service for this attempt
                selected_service = await self.select_service(
                    service_name, gateway_request
                )

                if not selected_service:
                    raise Exception(f"No healthy services available for {service_name}")

                # Skip if we've already tried this service (unless it's the only option)
                service_id = str(selected_service.id)
                if service_id in attempted_services and len(attempted_services) > 1:
                    continue

                attempted_services.add(service_id)

                # Execute request through circuit breaker
                try:
                    result = await self.circuit_breaker_manager.call_service(
                        selected_service,
                        request_func,
                        selected_service,
                        *args,
                        therapeutic_request=gateway_request.is_therapeutic,
                        crisis_mode=gateway_request.crisis_mode,
                        **kwargs,
                    )

                    # Update load balancer with success
                    self.load_balancer.update_metrics(
                        service_id,
                        0.0,
                        True,  # Response time will be updated elsewhere
                        therapeutic=gateway_request.is_therapeutic,
                        crisis=gateway_request.crisis_mode,
                    )

                    return result

                except CircuitBreakerError as e:
                    logger.warning(
                        f"Circuit breaker open for {selected_service.name}: {e}"
                    )
                    last_exception = e
                    continue

                finally:
                    # Decrement connection count
                    self.load_balancer.decrement_connections(service_id)

            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1} failed for {service_name}: {e}",
                    extra={
                        "correlation_id": gateway_request.correlation_id,
                        "service_name": service_name,
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                    },
                )
                last_exception = e

                # Wait before retry (except on last attempt)
                if attempt < max_retries:
                    await asyncio.sleep(
                        retry_delay * (attempt + 1)
                    )  # Exponential backoff

        # All attempts failed
        logger.error(
            f"All {max_retries + 1} attempts failed for {service_name}",
            extra={
                "correlation_id": gateway_request.correlation_id,
                "service_name": service_name,
                "attempted_services": list(attempted_services),
            },
        )

        if last_exception:
            raise last_exception
        else:
            raise Exception(
                f"Failed to route request to {service_name} after {max_retries + 1} attempts"
            )

    async def _get_available_services(self, service_name: str) -> list[ServiceInfo]:
        """
        Get available services with caching.

        Args:
            service_name: Name of the service

        Returns:
            List of available services
        """
        import time

        current_time = time.time()

        # Check cache
        if (
            service_name in self._service_cache
            and service_name in self._last_cache_update
            and current_time - self._last_cache_update[service_name] < self._cache_ttl
        ):
            return self._service_cache[service_name]

        # Fetch from service discovery
        try:
            services = await self.discovery_manager.get_services_by_name(service_name)

            # Update cache
            self._service_cache[service_name] = services
            self._last_cache_update[service_name] = current_time

            return services

        except Exception as e:
            logger.error(f"Error fetching services for {service_name}: {e}")

            # Return cached data if available
            return self._service_cache.get(service_name, [])

    async def update_service_metrics(
        self,
        service_id: str,
        response_time: float,
        success: bool,
        therapeutic: bool = False,
        crisis: bool = False,
    ) -> None:
        """
        Update metrics for a service after request completion.

        Args:
            service_id: Service ID
            response_time: Response time in seconds
            success: Whether the request was successful
            therapeutic: Whether this was a therapeutic request
            crisis: Whether this was a crisis request
        """
        # Update load balancer metrics
        self.load_balancer.update_metrics(
            service_id, response_time, success, therapeutic, crisis
        )

        # Update service discovery metrics
        await self.discovery_manager.update_service_metrics(
            service_id, response_time, success
        )

    def get_load_balancer_metrics(self) -> dict[str, Any]:
        """Get load balancer metrics for all services."""
        metrics = {}

        for service_id, service_metrics in self.load_balancer.service_metrics.items():
            metrics[service_id] = {
                "active_connections": service_metrics.active_connections,
                "total_requests": service_metrics.total_requests,
                "successful_requests": service_metrics.successful_requests,
                "failed_requests": service_metrics.failed_requests,
                "average_response_time": service_metrics.average_response_time,
                "health_score": service_metrics.health_score,
                "therapeutic_load": service_metrics.therapeutic_load,
                "crisis_load": service_metrics.crisis_load,
            }

        return metrics

    async def get_circuit_breaker_status(self) -> dict[str, dict[str, Any]]:
        """Get circuit breaker status for all services."""
        return await self.circuit_breaker_manager.get_service_health_summary()

    def clear_service_cache(self, service_name: str | None = None) -> None:
        """
        Clear service cache.

        Args:
            service_name: Specific service to clear, or None to clear all
        """
        if service_name:
            self._service_cache.pop(service_name, None)
            self._last_cache_update.pop(service_name, None)
        else:
            self._service_cache.clear()
            self._last_cache_update.clear()

    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check of the service router.

        Returns:
            Health check results
        """
        try:
            # Get circuit breaker status
            circuit_breaker_status = await self.get_circuit_breaker_status()

            # Count healthy services
            healthy_services = sum(
                1 for status in circuit_breaker_status.values() if status["is_healthy"]
            )
            total_services = len(circuit_breaker_status)

            # Get load balancer metrics
            lb_metrics = self.get_load_balancer_metrics()

            return {
                "status": "healthy" if healthy_services > 0 else "unhealthy",
                "load_balancing_strategy": self.config.load_balancing_strategy.value,
                "failover_strategy": self.config.failover_strategy.value,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "circuit_breakers": circuit_breaker_status,
                "load_balancer_metrics": lb_metrics,
                "cache_size": len(self._service_cache),
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
