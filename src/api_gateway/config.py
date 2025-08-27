"""
Configuration management for the API Gateway system.

This module provides configuration classes and settings management
that integrates with TTA's existing configuration system.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewaySettings(BaseSettings):
    """
    API Gateway configuration settings.

    Integrates with TTA's existing configuration system and provides
    environment-based configuration overrides.
    """

    model_config = SettingsConfigDict(
        env_prefix="TTA_GATEWAY_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def __init__(self, **kwargs):
        """Initialize settings with TTA config integration."""
        # Load TTA config integration first
        tta_config = load_tta_config_integration()

        # Apply TTA config defaults
        if tta_config:
            # Override defaults with TTA config values
            if "log_level" in tta_config:
                kwargs.setdefault("log_level", tta_config["log_level"].upper())
            if "websocket_enabled" in tta_config:
                kwargs.setdefault("websocket_enabled", tta_config["websocket_enabled"])
            if "websocket_timeout" in tta_config:
                kwargs.setdefault("websocket_timeout", int(tta_config["websocket_timeout"]))
            if "environment" in tta_config:
                kwargs.setdefault("debug", tta_config["environment"] == "development")

        super().__init__(**kwargs)
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Gateway server host")
    port: int = Field(default=8000, description="Gateway server port")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Security Configuration
    trusted_hosts: Optional[List[str]] = Field(
        default=None,
        description="List of trusted hostnames for security"
    )
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "https://localhost:3000",
            "http://localhost:8080",
            "https://localhost:8080",
        ],
        description="CORS allowed origins"
    )
    
    # Authentication Configuration (integrates with existing auth system)
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT secret key for token validation"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(default=30, description="JWT token expiration in minutes")
    
    # Service Discovery Configuration
    service_discovery_enabled: bool = Field(
        default=True,
        description="Enable service discovery"
    )
    service_registry_backend: str = Field(
        default="redis",
        description="Service registry backend (redis, consul)"
    )
    
    # Redis Configuration (for service discovery and rate limiting)
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # Rate Limiting Configuration
    rate_limiting_enabled: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    default_rate_limit: str = Field(
        default="100/minute",
        description="Default rate limit (requests/time_window)"
    )
    therapeutic_rate_limit: str = Field(
        default="200/minute",
        description="Rate limit for therapeutic sessions"
    )
    
    # Health Monitoring Configuration
    health_check_interval: int = Field(
        default=30,
        description="Health check interval in seconds"
    )
    health_check_timeout: int = Field(
        default=5,
        description="Health check timeout in seconds"
    )
    
    # Therapeutic Safety Configuration
    therapeutic_safety_enabled: bool = Field(
        default=True,
        description="Enable therapeutic safety monitoring"
    )
    crisis_detection_enabled: bool = Field(
        default=True,
        description="Enable crisis detection"
    )
    safety_monitoring_interval: int = Field(
        default=300,
        description="Safety monitoring interval in seconds"
    )
    
    # Monitoring and Observability
    metrics_enabled: bool = Field(
        default=True,
        description="Enable metrics collection"
    )
    prometheus_metrics_path: str = Field(
        default="/metrics",
        description="Prometheus metrics endpoint path"
    )
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    structured_logging: bool = Field(
        default=True,
        description="Enable structured logging"
    )
    
    # Circuit Breaker Configuration
    circuit_breaker_enabled: bool = Field(
        default=True,
        description="Enable circuit breaker pattern"
    )
    circuit_breaker_failure_threshold: int = Field(
        default=5,
        description="Circuit breaker failure threshold"
    )
    circuit_breaker_timeout: int = Field(
        default=60,
        description="Circuit breaker timeout in seconds"
    )
    
    # Load Balancing Configuration
    load_balancing_algorithm: str = Field(
        default="round_robin",
        description="Load balancing algorithm (round_robin, weighted, health_based)"
    )
    
    # WebSocket Configuration
    websocket_enabled: bool = Field(
        default=True,
        description="Enable WebSocket proxying"
    )
    websocket_timeout: int = Field(
        default=300,
        description="WebSocket connection timeout in seconds"
    )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return os.getenv("TTA_ENVIRONMENT", "development").lower() == "production"
    
    @property
    def redis_connection_kwargs(self) -> dict:
        """Get Redis connection parameters."""
        kwargs = {
            "db": self.redis_db,
            "decode_responses": True,
        }
        if self.redis_password:
            kwargs["password"] = self.redis_password
        return kwargs


@lru_cache()
def get_gateway_settings() -> GatewaySettings:
    """
    Get cached gateway settings instance.
    
    Returns:
        GatewaySettings: Cached settings instance
    """
    return GatewaySettings()


def load_tta_config_integration() -> dict:
    """
    Load configuration from TTA's main config system.

    This function integrates with the existing TTA configuration
    to inherit settings from the main tta_config.yaml file.

    Returns:
        dict: Configuration dictionary from TTA config
    """
    try:
        from src.orchestration.config import TTAConfig

        # Load TTA configuration
        tta_config = TTAConfig()

        # Extract relevant configuration for the gateway
        gateway_config = {}

        # Get environment settings
        environment = tta_config.get("environment", {})
        gateway_config["environment"] = environment.get("name", "development")
        gateway_config["log_level"] = environment.get("log_level", "info")

        # Get agent orchestration settings for integration
        agent_orchestration = tta_config.get("agent_orchestration", {})
        if agent_orchestration.get("enabled", False):
            gateway_config["agent_orchestration_enabled"] = True
            gateway_config["agent_orchestration_port"] = agent_orchestration.get("port", 8503)

        # Get realtime settings for WebSocket integration
        realtime = agent_orchestration.get("realtime", {})
        if realtime.get("enabled", False):
            websocket_config = realtime.get("websocket", {})
            gateway_config["websocket_enabled"] = websocket_config.get("enabled", False)
            gateway_config["websocket_path"] = websocket_config.get("path", "/ws")
            gateway_config["websocket_timeout"] = websocket_config.get("connection_timeout", 60.0)

        # Get Docker settings for deployment
        docker_config = tta_config.get("docker", {})
        gateway_config["docker_enabled"] = docker_config.get("enabled", True)

        return gateway_config

    except ImportError as e:
        # Fallback if TTA config system is not available
        print(f"Warning: Could not import TTA config system: {e}")
        return {}
    except Exception as e:
        # Fallback for any other errors
        print(f"Warning: Error loading TTA config: {e}")
        return {}
