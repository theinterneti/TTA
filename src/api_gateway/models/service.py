"""
Service-related data models for the API Gateway.

This module contains models for service discovery, registration,
and health monitoring.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class ServiceStatus(str, Enum):
    """Service health status enumeration."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ServiceType(str, Enum):
    """Service type enumeration."""

    API = "api"
    WEBSOCKET = "websocket"
    THERAPEUTIC = "therapeutic"
    AUTHENTICATION = "authentication"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGING = "messaging"


class LoadBalancingAlgorithm(str, Enum):
    """Load balancing algorithm enumeration."""

    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    HEALTH_BASED = "health_based"
    LEAST_CONNECTIONS = "least_connections"


class ServiceEndpoint(BaseModel):
    """Service endpoint information."""

    host: str = Field(..., description="Service host address")
    port: int = Field(..., ge=1, le=65535, description="Service port number")
    path: str = Field(default="/", description="Service base path")
    scheme: str = Field(
        default="http", description="Service scheme (http/https/ws/wss)"
    )

    @property
    def url(self) -> str:
        """Get the full service URL."""
        return f"{self.scheme}://{self.host}:{self.port}{self.path}"

    @field_validator("scheme")
    @classmethod
    def validate_scheme(cls, v):
        """Validate service scheme."""
        allowed_schemes = ["http", "https", "ws", "wss"]
        if v not in allowed_schemes:
            raise ValueError(f"Scheme must be one of {allowed_schemes}")
        return v


class ServiceHealthCheck(BaseModel):
    """Service health check configuration."""

    enabled: bool = Field(default=True, description="Enable health checks")
    endpoint: str = Field(default="/health", description="Health check endpoint")
    interval: int = Field(
        default=30, ge=1, description="Health check interval in seconds"
    )
    timeout: int = Field(default=5, ge=1, description="Health check timeout in seconds")
    retries: int = Field(
        default=3, ge=1, description="Number of retries before marking unhealthy"
    )
    expected_status: int = Field(default=200, description="Expected HTTP status code")


class ServiceMetrics(BaseModel):
    """Service performance metrics."""

    request_count: int = Field(default=0, description="Total request count")
    error_count: int = Field(default=0, description="Total error count")
    average_response_time: float = Field(
        default=0.0, description="Average response time in seconds"
    )
    last_response_time: float = Field(
        default=0.0, description="Last response time in seconds"
    )
    uptime: float = Field(default=0.0, description="Service uptime in seconds")
    last_health_check: datetime | None = Field(
        default=None, description="Last health check timestamp"
    )


class ServiceInfo(BaseModel):
    """Complete service information for service discovery."""

    # Basic service information
    id: UUID = Field(default_factory=uuid4, description="Unique service identifier")
    name: str = Field(..., description="Service name")
    version: str = Field(default="1.0.0", description="Service version")
    service_type: ServiceType = Field(..., description="Type of service")

    # Service endpoint information
    endpoint: ServiceEndpoint = Field(..., description="Service endpoint details")

    # Service configuration
    weight: int = Field(default=100, ge=1, le=1000, description="Load balancing weight")
    priority: int = Field(default=100, ge=1, le=1000, description="Service priority")
    tags: list[str] = Field(
        default_factory=list, description="Service tags for filtering"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional service metadata"
    )

    # Health and monitoring
    status: ServiceStatus = Field(
        default=ServiceStatus.UNKNOWN, description="Current service status"
    )
    health_check: ServiceHealthCheck = Field(
        default_factory=ServiceHealthCheck, description="Health check configuration"
    )
    metrics: ServiceMetrics = Field(
        default_factory=ServiceMetrics, description="Service metrics"
    )

    # Timestamps
    registered_at: datetime = Field(
        default_factory=datetime.utcnow, description="Service registration timestamp"
    )
    last_seen: datetime = Field(
        default_factory=datetime.utcnow, description="Last heartbeat timestamp"
    )

    # Therapeutic-specific fields
    therapeutic_priority: bool = Field(
        default=False, description="High priority for therapeutic sessions"
    )
    crisis_support: bool = Field(
        default=False, description="Supports crisis intervention"
    )
    safety_validated: bool = Field(
        default=False, description="Validated for therapeutic safety"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        """Validate service tags."""
        if v:
            # Ensure all tags are lowercase and alphanumeric
            return [tag.lower().strip() for tag in v if tag.strip()]
        return []

    def is_healthy(self) -> bool:
        """Check if service is healthy."""
        return self.status == ServiceStatus.HEALTHY

    def is_therapeutic(self) -> bool:
        """Check if service is therapeutic-related."""
        return (
            self.service_type == ServiceType.THERAPEUTIC
            or self.therapeutic_priority
            or "therapeutic" in self.tags
        )

    def update_metrics(self, response_time: float, success: bool = True):
        """Update service metrics."""
        self.metrics.request_count += 1
        if not success:
            self.metrics.error_count += 1

        # Update response time (simple moving average)
        if self.metrics.request_count == 1:
            self.metrics.average_response_time = response_time
        else:
            # Simple exponential moving average
            alpha = 0.1
            self.metrics.average_response_time = (
                alpha * response_time + (1 - alpha) * self.metrics.average_response_time
            )

        self.metrics.last_response_time = response_time
        self.last_seen = datetime.utcnow()


class ServiceRegistry(BaseModel):
    """Service registry containing all registered services."""

    services: dict[str, ServiceInfo] = Field(
        default_factory=dict, description="Registered services by ID"
    )
    load_balancing: LoadBalancingAlgorithm = Field(
        default=LoadBalancingAlgorithm.ROUND_ROBIN,
        description="Load balancing algorithm",
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow, description="Last registry update"
    )

    def add_service(self, service: ServiceInfo) -> None:
        """Add a service to the registry."""
        self.services[str(service.id)] = service
        self.last_updated = datetime.utcnow()

    def remove_service(self, service_id: str) -> bool:
        """Remove a service from the registry."""
        if service_id in self.services:
            del self.services[service_id]
            self.last_updated = datetime.utcnow()
            return True
        return False

    def get_healthy_services(
        self, service_type: ServiceType | None = None
    ) -> list[ServiceInfo]:
        """Get all healthy services, optionally filtered by type."""
        services = [
            service for service in self.services.values() if service.is_healthy()
        ]

        if service_type:
            services = [s for s in services if s.service_type == service_type]

        return services

    def get_therapeutic_services(self) -> list[ServiceInfo]:
        """Get all therapeutic-priority services."""
        return [
            service
            for service in self.services.values()
            if service.is_therapeutic() and service.is_healthy()
        ]
