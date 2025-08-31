"""
Configuration settings for the Player Experience API.

This module provides configuration management for the FastAPI application.
"""

import os

from dotenv import load_dotenv
from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class APISettings(BaseSettings):
    """API configuration settings."""

    # Application settings
    app_name: str = "Player Experience Interface API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Development and Mock Settings
    development_mode: bool = os.getenv("TTA_DEVELOPMENT_MODE", "false").lower() in (
        "true",
        "1",
        "yes",
    )
    use_mocks: bool = os.getenv("TTA_USE_MOCKS", "false").lower() in (
        "true",
        "1",
        "yes",
    )
    use_neo4j: bool = os.getenv("TTA_USE_NEO4J", "0") == "1"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    reload: bool = False

    # Security settings
    jwt_secret_key: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY", ""),
        description="JWT secret key - MUST be set in production",
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Authentication database settings
    neo4j_url: str = Field(
        default_factory=lambda: os.getenv("NEO4J_URL", "bolt://localhost:7687"),
        description="Neo4j connection URL",
    )
    neo4j_username: str = Field(
        default_factory=lambda: os.getenv("NEO4J_USERNAME", "neo4j"),
        description="Neo4j username",
    )
    neo4j_password: str = Field(
        default_factory=lambda: os.getenv("NEO4J_PASSWORD", ""),
        description="Neo4j password - MUST be set in production",
    )

    # Security policy settings
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True

    # MFA settings
    mfa_enabled: bool = False
    mfa_issuer_name: str = "TTA Platform"
    mfa_email_enabled: bool = False

    # CORS settings
    cors_origins: str | None = None
    cors_allow_credentials: bool = True
    cors_allow_methods: str | None = None
    cors_allow_headers: str | None = None

    # Rate limiting settings
    rate_limit_calls: int = 100
    rate_limit_period: int = 60  # seconds

    # Database settings
    database_url: str | None = None
    redis_url: str = Field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"),
        description="Redis connection URL",
    )
    redis_password: str | None = Field(
        default_factory=lambda: os.getenv("REDIS_PASSWORD"),
        description="Redis password",
    )
    redis_db: int = Field(default=0, description="Redis database number")
    redis_max_connections: int = Field(
        default=20, description="Maximum Redis connections"
    )

    # Neo4j settings (consolidated - removing duplicates)
    neo4j_database: str = Field(default="neo4j", description="Neo4j database name")
    neo4j_max_connection_pool_size: int = Field(
        default=50, description="Neo4j max connection pool size"
    )
    neo4j_connection_timeout: int = Field(
        default=60, description="Neo4j connection timeout in seconds"
    )

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Therapeutic safety settings
    crisis_detection_enabled: bool = True
    crisis_hotline: str = "988"  # National Suicide Prevention Lifeline

    # Development Features
    enable_docs: bool = True
    enable_redoc: bool = True
    enable_openapi: bool = True

    # Service Connection Settings
    service_connection_timeout: int = Field(
        default=30, description="Service connection timeout in seconds"
    )
    service_retry_attempts: int = Field(
        default=5, description="Number of retry attempts for service connections"
    )
    service_retry_base_delay: float = Field(
        default=0.5, description="Base delay for exponential backoff"
    )
    service_retry_max_delay: float = Field(
        default=8.0, description="Maximum delay for exponential backoff"
    )

    # Health Check Settings
    health_check_interval: int = Field(
        default=60, description="Health check interval in seconds"
    )
    health_check_timeout: int = Field(
        default=10, description="Health check timeout in seconds"
    )

    # Environment Detection
    environment: str = Field(
        default="development",
        description="Environment name (development, production, test)",
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in test environment."""
        return self.environment.lower() in ("test", "testing")

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, v):
        """Ensure JWT secret key is set."""
        if not v or v.strip() == "":
            raise ValueError("JWT_SECRET_KEY environment variable must be set")
        if len(v) < 16:
            raise ValueError("JWT secret key must be at least 16 characters long")
        return v

    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable."""
        if v is None or v == "":
            return [
                "http://localhost:3000",
                "http://localhost:8080",
                "https://localhost:3000",
                "https://localhost:8080",
            ]
        if isinstance(v, str) and v.strip():
            return [i.strip() for i in v.split(",") if i.strip()]
        return [
            "http://localhost:3000",
            "http://localhost:8080",
            "https://localhost:3000",
            "https://localhost:8080",
        ]

    @field_validator("cors_allow_methods", mode="after")
    @classmethod
    def parse_cors_methods(cls, v):
        """Parse CORS methods from environment variable."""
        if v is None or v == "":
            return ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        if isinstance(v, str) and v.strip():
            return [i.strip() for i in v.split(",") if i.strip()]
        return ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

    @field_validator("cors_allow_headers", mode="after")
    @classmethod
    def parse_cors_headers(cls, v):
        """Parse CORS headers from environment variable."""
        if v is None or v == "":
            return ["*"]
        if isinstance(v, str) and v.strip():
            return [i.strip() for i in v.split(",") if i.strip()]
        return ["*"]

    model_config = ConfigDict(
        env_file=".env",
        env_prefix="API_",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from environment
    )


class DevelopmentSettings(APISettings):
    """Development environment settings."""

    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"

    # Use environment variables even in development for consistency
    jwt_secret_key: str = Field(
        default_factory=lambda: os.getenv(
            "JWT_SECRET_KEY", "dev-secret-key-not-for-production-change-me"
        ),
        description="JWT secret key for development",
    )
    neo4j_password: str = Field(
        default_factory=lambda: os.getenv("NEO4J_PASSWORD", "devpassword"),
        description="Neo4j password for development",
    )


class ProductionSettings(APISettings):
    """Production environment settings."""

    debug: bool = False
    reload: bool = False
    log_level: str = "WARNING"

    # Production security defaults
    max_login_attempts: int = 3
    lockout_duration_minutes: int = 30
    mfa_enabled: bool = True

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

    @field_validator("neo4j_password")
    @classmethod
    def validate_neo4j_password(cls, v):
        """Ensure Neo4j password is set in production."""
        if v == "password":
            raise ValueError("Must set a strong Neo4j password in production")
        if len(v) < 8:
            raise ValueError("Neo4j password must be at least 8 characters long")
        return v

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v):
        """Ensure CORS origins are properly configured for production."""
        if any("localhost" in origin for origin in v):
            raise ValueError("Remove localhost from CORS origins in production")
        return v


class TestingSettings(APISettings):
    """Test environment settings."""

    debug: bool = True
    log_level: str = "DEBUG"

    # Use in-memory databases for testing
    database_url: str = "sqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/1"  # Use different Redis DB for tests

    # Use test Neo4j database with environment variables
    neo4j_password: str = Field(
        default_factory=lambda: os.getenv("NEO4J_TEST_PASSWORD", "testpassword"),
        description="Neo4j password for testing",
    )

    # Relaxed security for testing
    max_login_attempts: int = 10
    lockout_duration_minutes: int = 1
    password_min_length: int = 6

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
