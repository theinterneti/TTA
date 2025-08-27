"""
Tests for the API Gateway load balancing algorithms.

This module contains unit tests for various load balancing strategies
including round-robin, weighted, health-based, and therapeutic priority.
"""

import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from src.api_gateway.core.load_balancer import (
    LoadBalancingStrategy, create_load_balancer, ServiceMetrics,
    RoundRobinLoadBalancer, WeightedRoundRobinLoadBalancer,
    LeastConnectionsLoadBalancer, HealthBasedLoadBalancer,
    TherapeuticPriorityLoadBalancer
)
from src.api_gateway.models import ServiceInfo, ServiceType, ServiceEndpoint


@pytest.fixture
def sample_services():
    """Create sample services for testing."""
    services = []
    
    # Service 1: Regular service
    services.append(ServiceInfo(
        id=uuid4(),
        name="service-1",
        service_type=ServiceType.API,
        endpoint=ServiceEndpoint(host="localhost", port=8001),
        weight=100,
        priority=100,
        healthy=True,
        therapeutic_priority=False
    ))
    
    # Service 2: Therapeutic service with higher weight
    services.append(ServiceInfo(
        id=uuid4(),
        name="service-2",
        service_type=ServiceType.API,
        endpoint=ServiceEndpoint(host="localhost", port=8002),
        weight=150,
        priority=90,
        healthy=True,
        therapeutic_priority=True
    ))
    
    # Service 3: Regular service with lower weight
    services.append(ServiceInfo(
        id=uuid4(),
        name="service-3",
        service_type=ServiceType.API,
        endpoint=ServiceEndpoint(host="localhost", port=8003),
        weight=50,
        priority=80,
        healthy=True,
        therapeutic_priority=False
    ))
    
    # Service 4: Unhealthy service
    services.append(ServiceInfo(
        id=uuid4(),
        name="service-4",
        service_type=ServiceType.API,
        endpoint=ServiceEndpoint(host="localhost", port=8004),
        weight=100,
        priority=70,
        healthy=False,
        therapeutic_priority=False
    ))
    
    return services


class TestRoundRobinLoadBalancer:
    """Test cases for round-robin load balancer."""
    
    def test_round_robin_selection(self, sample_services):
        """Test basic round-robin selection."""
        balancer = RoundRobinLoadBalancer()
        healthy_services = [s for s in sample_services if s.healthy]
        
        # Test multiple selections
        selections = []
        for _ in range(6):  # More than the number of services
            selected = balancer.select_service(healthy_services)
            selections.append(selected.name)
        
        # Should cycle through services
        assert selections[0] == selections[3]  # After 3 services, should repeat
        assert selections[1] == selections[4]
        assert selections[2] == selections[5]
    
    def test_round_robin_filters_unhealthy(self, sample_services):
        """Test that round-robin filters out unhealthy services."""
        balancer = RoundRobinLoadBalancer()
        
        selected = balancer.select_service(sample_services)
        
        # Should not select the unhealthy service
        assert selected.healthy is True
        assert selected.name != "service-4"
    
    def test_round_robin_no_healthy_services(self, sample_services):
        """Test round-robin with no healthy services."""
        balancer = RoundRobinLoadBalancer()
        unhealthy_services = [s for s in sample_services if not s.healthy]
        
        selected = balancer.select_service(unhealthy_services)
        
        assert selected is None


class TestWeightedRoundRobinLoadBalancer:
    """Test cases for weighted round-robin load balancer."""
    
    def test_weighted_selection_distribution(self, sample_services):
        """Test that weighted selection respects service weights."""
        balancer = WeightedRoundRobinLoadBalancer()
        healthy_services = [s for s in sample_services if s.healthy]
        
        # Track selections over many iterations
        selections = {}
        for _ in range(300):  # Large number to see distribution
            selected = balancer.select_service(healthy_services)
            if selected:
                selections[selected.name] = selections.get(selected.name, 0) + 1
        
        # Service-2 has weight 150, should be selected more often
        # Service-1 has weight 100
        # Service-3 has weight 50, should be selected least often
        assert selections["service-2"] > selections["service-1"]
        assert selections["service-1"] > selections["service-3"]
    
    def test_therapeutic_priority_boost(self, sample_services):
        """Test therapeutic priority weight boost."""
        balancer = WeightedRoundRobinLoadBalancer()
        healthy_services = [s for s in sample_services if s.healthy]
        
        # Track selections with therapeutic priority
        selections = {}
        for _ in range(200):
            selected = balancer.select_service(
                healthy_services, 
                therapeutic_priority=True
            )
            if selected:
                selections[selected.name] = selections.get(selected.name, 0) + 1
        
        # Service-2 is therapeutic and should get even more selections
        therapeutic_service_selections = selections.get("service-2", 0)
        regular_service_selections = selections.get("service-1", 0)
        
        assert therapeutic_service_selections > regular_service_selections
    
    def test_crisis_mode_boost(self, sample_services):
        """Test crisis mode weight boost."""
        balancer = WeightedRoundRobinLoadBalancer()
        healthy_services = [s for s in sample_services if s.healthy]
        
        # Track selections with crisis mode
        selections = {}
        for _ in range(200):
            selected = balancer.select_service(
                healthy_services, 
                therapeutic_priority=True,
                crisis_mode=True
            )
            if selected:
                selections[selected.name] = selections.get(selected.name, 0) + 1
        
        # Service-2 should dominate in crisis mode
        therapeutic_service_selections = selections.get("service-2", 0)
        total_selections = sum(selections.values())
        
        # Should get majority of selections in crisis mode
        assert therapeutic_service_selections > total_selections * 0.6


class TestLeastConnectionsLoadBalancer:
    """Test cases for least connections load balancer."""
    
    def test_least_connections_selection(self, sample_services):
        """Test least connections selection logic."""
        balancer = LeastConnectionsLoadBalancer()
        healthy_services = [s for s in sample_services if s.healthy]
        
        # Set up different connection counts
        balancer.service_metrics[str(healthy_services[0].id)] = ServiceMetrics(
            service_id=str(healthy_services[0].id),
            active_connections=5
        )
        balancer.service_metrics[str(healthy_services[1].id)] = ServiceMetrics(
            service_id=str(healthy_services[1].id),
            active_connections=2
        )
        balancer.service_metrics[str(healthy_services[2].id)] = ServiceMetrics(
            service_id=str(healthy_services[2].id),
            active_connections=8
        )
        
        selected = balancer.select_service(healthy_services)
        
        # Should select service with least connections (service-2 with 2 connections)
        assert str(selected.id) == str(healthy_services[1].id)
    
    def test_therapeutic_priority_connection_reduction(self, sample_services):
        """Test therapeutic priority reduces effective connection count."""
        balancer = LeastConnectionsLoadBalancer()
        healthy_services = [s for s in sample_services if s.healthy]
        
        # Set up connection counts where therapeutic service has more connections
        # but should still be selected due to priority
        balancer.service_metrics[str(healthy_services[0].id)] = ServiceMetrics(
            service_id=str(healthy_services[0].id),
            active_connections=3
        )
        balancer.service_metrics[str(healthy_services[1].id)] = ServiceMetrics(
            service_id=str(healthy_services[1].id),
            active_connections=5  # More connections but therapeutic
        )
        
        selected = balancer.select_service(
            healthy_services, 
            therapeutic_priority=True
        )
        
        # Should select therapeutic service despite higher connection count
        # because therapeutic priority reduces effective load
        assert selected.therapeutic_priority is True


class TestHealthBasedLoadBalancer:
    """Test cases for health-based load balancer."""
    
    def test_health_based_selection(self, sample_services):
        """Test health-based selection considers multiple factors."""
        balancer = HealthBasedLoadBalancer()
        healthy_services = [s for s in sample_services if s.healthy]
        
        # Set up different health scores
        balancer.service_metrics[str(healthy_services[0].id)] = ServiceMetrics(
            service_id=str(healthy_services[0].id),
            health_score=0.9,
            average_response_time=0.1,
            active_connections=2
        )
        balancer.service_metrics[str(healthy_services[1].id)] = ServiceMetrics(
            service_id=str(healthy_services[1].id),
            health_score=0.7,
            average_response_time=0.5,
            active_connections=1
        )
        balancer.service_metrics[str(healthy_services[2].id)] = ServiceMetrics(
            service_id=str(healthy_services[2].id),
            health_score=0.5,
            average_response_time=1.0,
            active_connections=5
        )
        
        # Run multiple selections to see distribution
        selections = {}
        for _ in range(100):
            selected = balancer.select_service(healthy_services)
            if selected:
                selections[str(selected.id)] = selections.get(str(selected.id), 0) + 1
        
        # Service with best health score should be selected most often
        best_service_id = str(healthy_services[0].id)
        assert selections[best_service_id] > selections.get(str(healthy_services[1].id), 0)


class TestTherapeuticPriorityLoadBalancer:
    """Test cases for therapeutic priority load balancer."""
    
    def test_crisis_mode_therapeutic_only(self, sample_services):
        """Test crisis mode only uses therapeutic services."""
        balancer = TherapeuticPriorityLoadBalancer()
        healthy_services = [s for s in sample_services if s.healthy]
        
        # Set up crisis loads
        therapeutic_service = next(s for s in healthy_services if s.therapeutic_priority)
        balancer.service_metrics[str(therapeutic_service.id)] = ServiceMetrics(
            service_id=str(therapeutic_service.id),
            crisis_load=1
        )
        
        selected = balancer.select_service(
            healthy_services,
            crisis_mode=True
        )
        
        # Should select therapeutic service in crisis mode
        assert selected.therapeutic_priority is True
    
    def test_therapeutic_request_prefers_therapeutic_services(self, sample_services):
        """Test therapeutic requests prefer therapeutic services."""
        balancer = TherapeuticPriorityLoadBalancer()
        healthy_services = [s for s in sample_services if s.healthy]
        
        # Run multiple selections
        selections = {}
        for _ in range(50):
            selected = balancer.select_service(
                healthy_services,
                therapeutic_priority=True
            )
            if selected:
                selections[selected.therapeutic_priority] = selections.get(selected.therapeutic_priority, 0) + 1
        
        # Should prefer therapeutic services
        therapeutic_selections = selections.get(True, 0)
        non_therapeutic_selections = selections.get(False, 0)
        
        assert therapeutic_selections > non_therapeutic_selections
    
    def test_non_therapeutic_request_uses_all_services(self, sample_services):
        """Test non-therapeutic requests can use all services."""
        balancer = TherapeuticPriorityLoadBalancer()
        healthy_services = [s for s in sample_services if s.healthy]
        
        # Run multiple selections
        selected_services = set()
        for _ in range(20):
            selected = balancer.select_service(healthy_services)
            if selected:
                selected_services.add(selected.name)
        
        # Should use both therapeutic and non-therapeutic services
        assert len(selected_services) > 1


class TestLoadBalancerFactory:
    """Test cases for load balancer factory function."""
    
    def test_create_round_robin_balancer(self):
        """Test creating round-robin load balancer."""
        balancer = create_load_balancer(LoadBalancingStrategy.ROUND_ROBIN)
        assert isinstance(balancer, RoundRobinLoadBalancer)
    
    def test_create_weighted_round_robin_balancer(self):
        """Test creating weighted round-robin load balancer."""
        balancer = create_load_balancer(LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN)
        assert isinstance(balancer, WeightedRoundRobinLoadBalancer)
    
    def test_create_least_connections_balancer(self):
        """Test creating least connections load balancer."""
        balancer = create_load_balancer(LoadBalancingStrategy.LEAST_CONNECTIONS)
        assert isinstance(balancer, LeastConnectionsLoadBalancer)
    
    def test_create_health_based_balancer(self):
        """Test creating health-based load balancer."""
        balancer = create_load_balancer(LoadBalancingStrategy.HEALTH_BASED)
        assert isinstance(balancer, HealthBasedLoadBalancer)
    
    def test_create_therapeutic_priority_balancer(self):
        """Test creating therapeutic priority load balancer."""
        balancer = create_load_balancer(LoadBalancingStrategy.THERAPEUTIC_PRIORITY)
        assert isinstance(balancer, TherapeuticPriorityLoadBalancer)
    
    def test_create_default_balancer(self):
        """Test creating default load balancer for unknown strategy."""
        balancer = create_load_balancer(LoadBalancingStrategy.RANDOM)
        assert isinstance(balancer, HealthBasedLoadBalancer)  # Default fallback


class TestServiceMetrics:
    """Test cases for service metrics tracking."""
    
    def test_metrics_update_success(self):
        """Test updating metrics for successful request."""
        balancer = RoundRobinLoadBalancer()
        service_id = "test-service"
        
        balancer.update_metrics(service_id, 0.5, True)
        
        metrics = balancer.get_service_metrics(service_id)
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0
        assert metrics.average_response_time == 0.5
        assert metrics.health_score > 0.5
    
    def test_metrics_update_failure(self):
        """Test updating metrics for failed request."""
        balancer = RoundRobinLoadBalancer()
        service_id = "test-service"
        
        balancer.update_metrics(service_id, 2.0, False)
        
        metrics = balancer.get_service_metrics(service_id)
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 1
        assert metrics.health_score < 0.5  # Should be penalized
    
    def test_connection_tracking(self):
        """Test connection count tracking."""
        balancer = RoundRobinLoadBalancer()
        service_id = "test-service"
        
        balancer.increment_connections(service_id)
        balancer.increment_connections(service_id)
        
        metrics = balancer.get_service_metrics(service_id)
        assert metrics.active_connections == 2
        
        balancer.decrement_connections(service_id)
        
        metrics = balancer.get_service_metrics(service_id)
        assert metrics.active_connections == 1
    
    def test_therapeutic_load_tracking(self):
        """Test therapeutic and crisis load tracking."""
        balancer = RoundRobinLoadBalancer()
        service_id = "test-service"
        
        # Update with therapeutic request
        balancer.update_metrics(service_id, 0.3, True, therapeutic=True)
        
        metrics = balancer.get_service_metrics(service_id)
        assert metrics.therapeutic_load == 1
        assert metrics.crisis_load == 0
        
        # Update with crisis request
        balancer.update_metrics(service_id, 0.4, True, therapeutic=True, crisis=True)
        
        metrics = balancer.get_service_metrics(service_id)
        assert metrics.therapeutic_load == 1  # Still 1
        assert metrics.crisis_load == 1  # Now 1
