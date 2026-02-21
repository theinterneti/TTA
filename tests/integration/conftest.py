"""

# Logseq: [[TTA.dev/Tests/Integration/Conftest]]
Integration test configuration for TTA staging environment.

This module provides fixtures and configuration for integration tests
that run against the staging environment with correct ports and credentials.
"""

import os
from typing import Any

import pytest
import pytest_asyncio


def get_staging_config() -> dict[str, Any]:
    """
    Get staging environment configuration.

    Returns configuration with correct ports for staging environment:
    - Neo4j: 7688 (bolt), 7475 (http)
    - Redis: 6380
    - PostgreSQL: 5433
    - Player API: 3004
    - Frontend: 3000
    """
    environment = os.environ.get("ENVIRONMENT", "development")

    if environment == "staging":
        return {
            "neo4j": {
                "uri": "bolt://localhost:7688",
                "user": "neo4j",
                "password": os.environ.get(
                    "NEO4J_STAGING_PASSWORD", "staging_neo4j_secure_pass_2024"
                ),
            },
            "redis": {
                "host": "localhost",
                "port": 6380,
                "password": os.environ.get(
                    "REDIS_STAGING_PASSWORD", "staging_redis_secure_pass_2024"
                ),
                "db": 0,
            },
            "postgres": {
                "host": "localhost",
                "port": 5433,
                "database": "tta_staging",
                "user": "tta_user",
                "password": os.environ.get(
                    "POSTGRES_STAGING_PASSWORD", "staging_postgres_secure_pass_2024"
                ),
            },
            "api": {
                "base_url": "http://localhost:3004",
                "health_endpoint": "/health",
                "api_prefix": "/api/v1",
            },
            "frontend": {
                "base_url": "http://localhost:3000",
            },
        }
    # Development/test environment (default ports)
    return {
        "neo4j": {
            "uri": "bolt://localhost:7687",
            "user": "neo4j",
            "password": "test_password",
        },
        "redis": {
            "host": "localhost",
            "port": 6379,
            "password": None,
            "db": 1,  # Use test database
        },
        "postgres": {
            "host": "localhost",
            "port": 5432,
            "database": "tta_test",
            "user": "tta_user",
            "password": "test_password",
        },
        "api": {
            "base_url": "http://localhost:8080",
            "health_endpoint": "/health",
            "api_prefix": "/api/v1",
        },
        "frontend": {
            "base_url": "http://localhost:3000",
        },
    }


@pytest.fixture(scope="session")
def staging_config():
    """Provide staging environment configuration."""
    return get_staging_config()


@pytest.fixture(scope="session")
def neo4j_config(staging_config):
    """Provide Neo4j configuration for current environment."""
    return staging_config["neo4j"]


@pytest.fixture(scope="session")
def redis_config(staging_config):
    """Provide Redis configuration for current environment."""
    return staging_config["redis"]


@pytest.fixture(scope="session")
def postgres_config(staging_config):
    """Provide PostgreSQL configuration for current environment."""
    return staging_config["postgres"]


@pytest.fixture(scope="session")
def api_config(staging_config):
    """Provide API configuration for current environment."""
    return staging_config["api"]


@pytest_asyncio.fixture
async def redis_client(redis_config):
    """Provide Redis client for integration tests."""
    import redis.asyncio as aioredis

    redis_url = (
        f"redis://{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"
    )
    if redis_config.get("password"):
        redis_url = f"redis://:{redis_config['password']}@{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"

    client = aioredis.from_url(redis_url, decode_responses=True)

    yield client

    # Cleanup
    await client.close()


@pytest_asyncio.fixture
async def neo4j_driver(neo4j_config):
    """Provide Neo4j driver for integration tests."""
    from neo4j import AsyncGraphDatabase

    driver = AsyncGraphDatabase.driver(
        neo4j_config["uri"], auth=(neo4j_config["user"], neo4j_config["password"])
    )

    yield driver

    # Cleanup
    await driver.close()


@pytest.fixture
def api_base_url(api_config):
    """Provide API base URL for integration tests."""
    return api_config["base_url"]


@pytest.fixture
def api_client(api_base_url):
    """Provide HTTP client for API integration tests."""
    import aiohttp

    async def _make_client():
        return aiohttp.ClientSession(base_url=api_base_url)

    return _make_client
