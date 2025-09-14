"""
Load balancing algorithms for the API Gateway.

This module provides various load balancing strategies including round-robin,
weighted, health-based, and therapeutic priority-based load balancing.
"""

import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from ..models import ServiceInfo

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategy types."""

    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    HEALTH_BASED = "health_based"
    THERAPEUTIC_PRIORITY = "therapeutic_priority"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"


@dataclass
class ServiceMetrics:
    """Metrics for a service instance."""

    service_id: str
    active_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_health_check: float = field(default_factory=time.time)
    health_score: float = 1.0  # 0.0 to 1.0, where 1.0 is perfect health
    therapeutic_load: int = 0  # Number of active therapeutic sessions
    crisis_load: int = 0  # Number of active crisis sessions


class LoadBalancer(ABC):
    """Abstract base class for load balancing algorithms."""

    def __init__(self, strategy: LoadBalancingStrategy):
        """
        Initialize the load balancer.

        Args:
            strategy: Load balancing strategy
        """
        self.strategy = strategy
        self.service_metrics: dict[str, ServiceMetrics] = {}

    @abstractmethod
    def select_service(
        self,
        services: list[ServiceInfo],
        therapeutic_priority: bool = False,
        crisis_mode: bool = False,
    ) -> ServiceInfo | None:
        """
        Select a service from the available services.

        Args:
            services: List of available services
            therapeutic_priority: Whether this is a therapeutic request
            crisis_mode: Whether this is a crisis situation

        Returns:
            Selected service or None if no service available
        """
        pass

    def update_metrics(
        self,
        service_id: str,
        response_time: float,
        success: bool,
        therapeutic: bool = False,
        crisis: bool = False,
    ) -> None:
        """
        Update metrics for a service.

        Args:
            service_id: Service ID
            response_time: Response time in seconds
            success: Whether the request was successful
            therapeutic: Whether this was a therapeutic request
            crisis: Whether this was a crisis request
        """
        if service_id not in self.service_metrics:
            self.service_metrics[service_id] = ServiceMetrics(service_id=service_id)

        metrics = self.service_metrics[service_id]
        metrics.total_requests += 1

        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1

        # Update average response time (exponential moving average)
        alpha = 0.1  # Smoothing factor
        metrics.average_response_time = (
            alpha * response_time + (1 - alpha) * metrics.average_response_time
        )

        # Update health score based on success rate and response time
        success_rate = metrics.successful_requests / metrics.total_requests
        response_penalty = min(response_time / 5.0, 1.0)  # Penalty for slow responses
        metrics.health_score = success_rate * (1.0 - response_penalty * 0.5)

        # Update therapeutic/crisis load
        if therapeutic:
            if crisis:
                metrics.crisis_load += 1
            else:
                metrics.therapeutic_load += 1

    def increment_connections(self, service_id: str) -> None:
        """Increment active connections for a service."""
        if service_id not in self.service_metrics:
            self.service_metrics[service_id] = ServiceMetrics(service_id=service_id)
        self.service_metrics[service_id].active_connections += 1

    def decrement_connections(self, service_id: str) -> None:
        """Decrement active connections for a service."""
        if service_id in self.service_metrics:
            self.service_metrics[service_id].active_connections = max(
                0, self.service_metrics[service_id].active_connections - 1
            )

    def get_service_metrics(self, service_id: str) -> ServiceMetrics | None:
        """Get metrics for a service."""
        return self.service_metrics.get(service_id)

    def _filter_healthy_services(
        self, services: list[ServiceInfo]
    ) -> list[ServiceInfo]:
        """Filter services to only include healthy ones."""
        healthy_services = []

        for service in services:
            # Check if service is marked as healthy
            if not service.healthy:
                continue

            # Check metrics-based health
            metrics = self.service_metrics.get(str(service.id))
            if metrics and metrics.health_score < 0.3:  # Below 30% health
                continue

            healthy_services.append(service)

        return healthy_services


class RoundRobinLoadBalancer(LoadBalancer):
    """Round-robin load balancing algorithm."""

    def __init__(self):
        super().__init__(LoadBalancingStrategy.ROUND_ROBIN)
        self._current_index = 0

    def select_service(
        self,
        services: list[ServiceInfo],
        therapeutic_priority: bool = False,
        crisis_mode: bool = False,
    ) -> ServiceInfo | None:
        """Select service using round-robin algorithm."""
        healthy_services = self._filter_healthy_services(services)

        if not healthy_services:
            return None

        # Simple round-robin selection
        selected_service = healthy_services[self._current_index % len(healthy_services)]
        self._current_index += 1

        return selected_service


class WeightedRoundRobinLoadBalancer(LoadBalancer):
    """Weighted round-robin load balancing algorithm."""

    def __init__(self):
        super().__init__(LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN)
        self._current_weights: dict[str, int] = {}

    def select_service(
        self,
        services: list[ServiceInfo],
        therapeutic_priority: bool = False,
        crisis_mode: bool = False,
    ) -> ServiceInfo | None:
        """Select service using weighted round-robin algorithm."""
        healthy_services = self._filter_healthy_services(services)

        if not healthy_services:
            return None

        # Calculate effective weights
        max_weight = 0
        total_weight = 0

        for service in healthy_services:
            weight = service.weight

            # Boost weight for therapeutic priority services
            if therapeutic_priority and service.therapeutic_priority:
                weight = int(weight * 1.5)

            # Further boost for crisis mode
            if crisis_mode and service.therapeutic_priority:
                weight = int(weight * 2.0)

            total_weight += weight
            max_weight = max(max_weight, weight)

            service_id = str(service.id)
            if service_id not in self._current_weights:
                self._current_weights[service_id] = 0

        # Find service with highest current weight
        selected_service = None
        highest_weight = -1

        for service in healthy_services:
            service_id = str(service.id)
            current_weight = self._current_weights[service_id]

            if current_weight > highest_weight:
                highest_weight = current_weight
                selected_service = service

        if selected_service:
            service_id = str(selected_service.id)
            # Decrease selected service weight
            self._current_weights[service_id] -= total_weight

            # Increase all service weights by their configured weight
            for service in healthy_services:
                sid = str(service.id)
                weight = service.weight

                if therapeutic_priority and service.therapeutic_priority:
                    weight = int(weight * 1.5)
                if crisis_mode and service.therapeutic_priority:
                    weight = int(weight * 2.0)

                self._current_weights[sid] += weight

        return selected_service


class LeastConnectionsLoadBalancer(LoadBalancer):
    """Least connections load balancing algorithm."""

    def __init__(self):
        super().__init__(LoadBalancingStrategy.LEAST_CONNECTIONS)

    def select_service(
        self,
        services: list[ServiceInfo],
        therapeutic_priority: bool = False,
        crisis_mode: bool = False,
    ) -> ServiceInfo | None:
        """Select service with least active connections."""
        healthy_services = self._filter_healthy_services(services)

        if not healthy_services:
            return None

        # Find service with least connections
        selected_service = None
        min_connections = float("inf")

        for service in healthy_services:
            service_id = str(service.id)
            metrics = self.service_metrics.get(service_id)
            connections = metrics.active_connections if metrics else 0

            # Apply therapeutic priority
            if therapeutic_priority and service.therapeutic_priority:
                connections = int(connections * 0.7)  # Reduce effective load

            if crisis_mode and service.therapeutic_priority:
                connections = int(connections * 0.5)  # Further reduce for crisis

            if connections < min_connections:
                min_connections = connections
                selected_service = service

        return selected_service


class HealthBasedLoadBalancer(LoadBalancer):
    """Health-based load balancing algorithm."""

    def __init__(self):
        super().__init__(LoadBalancingStrategy.HEALTH_BASED)

    def select_service(
        self,
        services: list[ServiceInfo],
        therapeutic_priority: bool = False,
        crisis_mode: bool = False,
    ) -> ServiceInfo | None:
        """Select service based on health score and performance."""
        healthy_services = self._filter_healthy_services(services)

        if not healthy_services:
            return None

        # Calculate selection probability based on health and other factors
        service_scores = []
        total_score = 0

        for service in healthy_services:
            service_id = str(service.id)
            metrics = self.service_metrics.get(service_id)

            # Base score from health
            health_score = metrics.health_score if metrics else 1.0

            # Factor in response time (lower is better)
            response_time_score = 1.0
            if metrics and metrics.average_response_time > 0:
                response_time_score = 1.0 / (1.0 + metrics.average_response_time)

            # Factor in current load
            load_score = 1.0
            if metrics:
                # Penalize high connection count
                load_penalty = metrics.active_connections * 0.1
                load_score = max(0.1, 1.0 - load_penalty)

            # Combine scores
            combined_score = health_score * response_time_score * load_score

            # Apply therapeutic priority boost
            if therapeutic_priority and service.therapeutic_priority:
                combined_score *= 1.5

            if crisis_mode and service.therapeutic_priority:
                combined_score *= 2.0

            service_scores.append((service, combined_score))
            total_score += combined_score

        if total_score == 0:
            return healthy_services[0]  # Fallback to first service

        # Weighted random selection based on scores
        random_value = random.random() * total_score
        cumulative_score = 0

        for service, score in service_scores:
            cumulative_score += score
            if random_value <= cumulative_score:
                return service

        # Fallback to last service
        return service_scores[-1][0] if service_scores else None


class TherapeuticPriorityLoadBalancer(LoadBalancer):
    """Therapeutic priority-based load balancing algorithm."""

    def __init__(self):
        super().__init__(LoadBalancingStrategy.THERAPEUTIC_PRIORITY)
        self._fallback_balancer = HealthBasedLoadBalancer()

    def select_service(
        self,
        services: list[ServiceInfo],
        therapeutic_priority: bool = False,
        crisis_mode: bool = False,
    ) -> ServiceInfo | None:
        """Select service with therapeutic priority considerations."""
        healthy_services = self._filter_healthy_services(services)

        if not healthy_services:
            return None

        # Separate therapeutic and non-therapeutic services
        therapeutic_services = [s for s in healthy_services if s.therapeutic_priority]
        [
            s for s in healthy_services if not s.therapeutic_priority
        ]

        # For crisis mode, only use therapeutic services if available
        if crisis_mode and therapeutic_services:
            # Find service with lowest crisis load
            selected_service = None
            min_crisis_load = float("inf")

            for service in therapeutic_services:
                service_id = str(service.id)
                metrics = self.service_metrics.get(service_id)
                crisis_load = metrics.crisis_load if metrics else 0

                if crisis_load < min_crisis_load:
                    min_crisis_load = crisis_load
                    selected_service = service

            return selected_service

        # For therapeutic requests, prefer therapeutic services
        if therapeutic_priority and therapeutic_services:
            # Use health-based selection among therapeutic services
            return self._fallback_balancer.select_service(
                therapeutic_services, therapeutic_priority, crisis_mode
            )

        # For non-therapeutic requests, use all services
        return self._fallback_balancer.select_service(
            healthy_services, therapeutic_priority, crisis_mode
        )


def create_load_balancer(strategy: LoadBalancingStrategy) -> LoadBalancer:
    """
    Create a load balancer instance based on strategy.

    Args:
        strategy: Load balancing strategy

    Returns:
        LoadBalancer instance
    """
    if strategy == LoadBalancingStrategy.ROUND_ROBIN:
        return RoundRobinLoadBalancer()
    elif strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
        return WeightedRoundRobinLoadBalancer()
    elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
        return LeastConnectionsLoadBalancer()
    elif strategy == LoadBalancingStrategy.HEALTH_BASED:
        return HealthBasedLoadBalancer()
    elif strategy == LoadBalancingStrategy.THERAPEUTIC_PRIORITY:
        return TherapeuticPriorityLoadBalancer()
    else:
        # Default to health-based
        return HealthBasedLoadBalancer()
