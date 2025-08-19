"""
Configuration settings for the Player Experience API.

This module provides configuration management for the FastAPI application.
"""

import os
from typing import List, Optional

from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """API configuration settings."""
    
    # Application settings
    app_name: str = "Player Experience Interface API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    reload: bool = False
    
    # Security settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://localhost:3000",
        "https://localhost:8080",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]
    
    # Rate limiting settings
    rate_limit_calls: int = 100
    rate_limit_period: int = 60  # seconds
    
    # Database settings
    database_url: Optional[str] = None
    redis_url: str = "redis://localhost:6379"
    neo4j_url: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Therapeutic safety settings
    crisis_detection_enabled: bool = True
    crisis_hotline: str = "988"  # National Suicide Prevention Lifeline
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from environment variable."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def assemble_cors_methods(cls, v):
        """Parse CORS methods from environment variable."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def assemble_cors_headers(cls, v):
        """Parse CORS headers from environment variable."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    model_config = ConfigDict(
        env_file=".env",
        env_prefix="API_",
        case_sensitive=False,
    )


class DevelopmentSettings(APISettings):
    """Development environment settings."""
    
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"
    
    # Use weaker security for development
    jwt_secret_key: str = "dev-secret-key-not-for-production"


class ProductionSettings(APISettings):
    """Production environment settings."""
    
    debug: bool = False
    reload: bool = False
    log_level: str = "WARNING"
    
    # Require strong security settings in production
    @field_validator("jwt_secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        """Ensure secret key is strong in production."""
        if v == "your-secret-key-change-in-production":
            raise ValueError("Must set a strong JWT secret key in production")
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v


class TestingSettings(APISettings):
    """Test environment settings."""
    
    debug: bool = True
    log_level: str = "DEBUG"
    
    # Use in-memory databases for testing
    database_url: str = "sqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/1"  # Use different Redis DB for tests
    
    # Disable rate limiting for tests
    rate_limit_calls: int = 10000
    rate_limit_period: int = 1


def get_settings() -> APISettings:
    """
    Get the appropriate settings based on the environment.
    
    Returns:
        APISettings: The configuration settings
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "test":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()