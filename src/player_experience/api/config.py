"""
Configuration settings for the Player Experience API.

This module provides configuration management for the FastAPI application.
"""

import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    cors_origins: str | None = Field(default=None, validation_alias="API_CORS_ORIGINS")
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    cors_allow_headers: list[str] = ["*"]

    # Rate limiting settings
    rate_limit_calls: int = 100
    rate_limit_period: int = 60  # seconds

    # Database settings
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", validation_alias="REDIS_URL")
    neo4j_uri: str = Field(default="bolt://localhost:7687", validation_alias="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", validation_alias="NEO4J_USER")
    neo4j_password: str = Field(default="password", validation_alias="NEO4J_PASSWORD")

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Therapeutic safety settings
    crisis_detection_enabled: bool = True
    crisis_hotline: str = "988"  # National Suicide Prevention Lifeline

    # Error Monitoring and Performance Tracking (Sentry)
    sentry_dsn: str | None = Field(default=None, validation_alias="SENTRY_DSN")
    sentry_environment: str = Field(
        default="development", validation_alias="SENTRY_ENVIRONMENT"
    )
    sentry_traces_sample_rate: float = Field(
        default=1.0, validation_alias="SENTRY_TRACES_SAMPLE_RATE"
    )
    sentry_profiles_sample_rate: float = Field(
        default=1.0, validation_alias="SENTRY_PROFILES_SAMPLE_RATE"
    )
    sentry_send_default_pii: bool = Field(
        default=False, validation_alias="SENTRY_SEND_DEFAULT_PII"
    )
    sentry_enable_logs: bool = Field(default=True, validation_alias="SENTRY_ENABLE_LOGS")

    @field_validator("cors_origins", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from environment variable."""
        if v is None:
            # Return default values
            return [
                "http://localhost:3000",
                "http://localhost:8080",
                "https://localhost:3000",
                "https://localhost:8080",
            ]
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

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_parse_none_str="",
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

    # Production Sentry settings
    sentry_environment: str = "production"
    sentry_traces_sample_rate: float = 0.1  # Lower sampling for production
    sentry_profiles_sample_rate: float = 0.1  # Lower profiling for production
    sentry_send_default_pii: bool = False  # Never send PII in production

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


class StagingSettings(APISettings):
    """Staging environment settings."""

    debug: bool = False
    reload: bool = False
    log_level: str = "INFO"

    # Staging Sentry settings
    sentry_environment: str = "staging"
    sentry_traces_sample_rate: float = 0.2  # Higher sampling for staging testing
    sentry_profiles_sample_rate: float = 0.2
    sentry_send_default_pii: bool = False  # Never send PII


class TestingSettings(APISettings):
    """Test environment settings."""

    debug: bool = True
    log_level: str = "DEBUG"

    # Use in-memory databases for testing
    database_url: str | None = "sqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/1"  # Use different Redis DB for tests

    # Disable rate limiting for tests
    rate_limit_calls: int = 10000
    rate_limit_period: int = 1

    # Disable Sentry for tests
    sentry_dsn: str | None = None


def get_settings() -> APISettings:
    """
    Get the appropriate settings based on the environment.

    Returns:
        APISettings: The configuration settings
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        return ProductionSettings()
    elif environment == "staging":
        return StagingSettings()
    elif environment == "test":
        return TestingSettings()
    else:
        return DevelopmentSettings()
