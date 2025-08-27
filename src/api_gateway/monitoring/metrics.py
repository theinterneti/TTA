"""
Metrics collection and Prometheus integration for the API Gateway.

This module provides comprehensive metrics collection for monitoring
gateway performance, therapeutic sessions, and system health.
"""

import time
from typing import Dict, Any

from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from ..config import get_gateway_settings


# Prometheus metrics
REQUEST_COUNT = Counter(
    'gateway_requests_total',
    'Total number of requests processed by the gateway',
    ['method', 'endpoint', 'status_code', 'service']
)

REQUEST_DURATION = Histogram(
    'gateway_request_duration_seconds',
    'Request processing duration in seconds',
    ['method', 'endpoint', 'service']
)

ACTIVE_CONNECTIONS = Gauge(
    'gateway_active_connections',
    'Number of active connections to the gateway'
)

SERVICE_HEALTH = Gauge(
    'gateway_service_health',
    'Health status of backend services (1=healthy, 0=unhealthy)',
    ['service_name']
)

THERAPEUTIC_SESSIONS = Gauge(
    'gateway_therapeutic_sessions_active',
    'Number of active therapeutic sessions'
)

CRISIS_EVENTS = Counter(
    'gateway_crisis_events_total',
    'Total number of crisis events detected',
    ['severity', 'intervention_type']
)

RATE_LIMIT_HITS = Counter(
    'gateway_rate_limit_hits_total',
    'Total number of rate limit hits',
    ['client_ip', 'endpoint']
)

AUTHENTICATION_EVENTS = Counter(
    'gateway_auth_events_total',
    'Total number of authentication events',
    ['event_type', 'status']
)


metrics_router = APIRouter()


class MetricsCollector:
    """
    Metrics collection service for the API Gateway.
    
    Provides comprehensive metrics collection for:
    - Request/response metrics
    - Service health metrics
    - Therapeutic session metrics
    - Security and safety metrics
    """
    
    def __init__(self):
        self.settings = get_gateway_settings()
        self.start_time = time.time()
    
    def record_request(self, method: str, endpoint: str, status_code: int, 
                      duration: float, service: str = "gateway"):
        """Record request metrics."""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            service=service
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint,
            service=service
        ).observe(duration)
    
    def update_active_connections(self, count: int):
        """Update active connections gauge."""
        ACTIVE_CONNECTIONS.set(count)
    
    def update_service_health(self, service_name: str, is_healthy: bool):
        """Update service health status."""
        SERVICE_HEALTH.labels(service_name=service_name).set(1 if is_healthy else 0)
    
    def update_therapeutic_sessions(self, count: int):
        """Update active therapeutic sessions count."""
        THERAPEUTIC_SESSIONS.set(count)
    
    def record_crisis_event(self, severity: str, intervention_type: str):
        """Record crisis event."""
        CRISIS_EVENTS.labels(
            severity=severity,
            intervention_type=intervention_type
        ).inc()
    
    def record_rate_limit_hit(self, client_ip: str, endpoint: str):
        """Record rate limit hit."""
        RATE_LIMIT_HITS.labels(
            client_ip=client_ip,
            endpoint=endpoint
        ).inc()
    
    def record_auth_event(self, event_type: str, status: str):
        """Record authentication event."""
        AUTHENTICATION_EVENTS.labels(
            event_type=event_type,
            status=status
        ).inc()
    
    def get_custom_metrics(self) -> Dict[str, Any]:
        """Get custom gateway metrics."""
        uptime = time.time() - self.start_time
        
        return {
            "gateway_uptime_seconds": uptime,
            "gateway_version": "1.0.0",
            "gateway_config": {
                "rate_limiting_enabled": self.settings.rate_limiting_enabled,
                "therapeutic_safety_enabled": self.settings.therapeutic_safety_enabled,
                "service_discovery_enabled": self.settings.service_discovery_enabled,
            }
        }


# Create metrics collector instance
metrics_collector = MetricsCollector()


@metrics_router.get("/prometheus")
async def get_prometheus_metrics():
    """
    Prometheus metrics endpoint.
    
    Returns:
        Response: Prometheus metrics in text format
    """
    metrics_data = generate_latest()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


@metrics_router.get("/")
async def get_metrics_summary():
    """
    Get metrics summary in JSON format.
    
    Returns:
        dict: Metrics summary
    """
    custom_metrics = metrics_collector.get_custom_metrics()
    
    return {
        "timestamp": time.time(),
        "metrics": custom_metrics,
        "prometheus_endpoint": "/metrics/prometheus"
    }


@metrics_router.get("/health-metrics")
async def get_health_metrics():
    """
    Get health-related metrics.
    
    Returns:
        dict: Health metrics
    """
    # TODO: Implement health metrics collection
    return {
        "timestamp": time.time(),
        "service_health": {},
        "system_metrics": {
            "uptime": time.time() - metrics_collector.start_time,
            "active_connections": 0,  # TODO: Get actual count
            "therapeutic_sessions": 0,  # TODO: Get actual count
        }
    }


@metrics_router.get("/therapeutic-metrics")
async def get_therapeutic_metrics():
    """
    Get therapeutic-specific metrics.
    
    Returns:
        dict: Therapeutic metrics
    """
    return {
        "timestamp": time.time(),
        "active_sessions": 0,  # TODO: Get actual count
        "crisis_events_24h": 0,  # TODO: Get actual count
        "safety_interventions": 0,  # TODO: Get actual count
        "therapeutic_endpoints_health": {}  # TODO: Get service health
    }
