"""

# Logseq: [[TTA.dev/Tests/Post_deployment/Conftest]]
Shared fixtures for post-deployment integration tests.

These fixtures provide configuration and utilities for testing against
deployed environments (staging, production).
"""

import os
from typing import Any

import httpx
import pytest


@pytest.fixture(scope="session")
def deployment_env() -> str:
    """
    Get the deployment environment to test against.

    Returns:
        str: Environment name ('staging', 'production', or 'local')

    Environment variable: DEPLOYMENT_ENV
    """
    return os.getenv("DEPLOYMENT_ENV", "staging")


@pytest.fixture(scope="session")
def api_base_url(deployment_env: str) -> str:
    """
    Get the API base URL for the deployment environment.

    Args:
        deployment_env: The deployment environment

    Returns:
        str: API base URL

    Environment variable: API_BASE_URL (overrides default)
    """
    # Allow explicit override via environment variable
    if override_url := os.getenv("API_BASE_URL"):
        return override_url

    # Default URLs per environment
    env_urls = {
        "staging": "http://localhost:8081",
        "production": "https://api.tta.example.com",  # Update with actual production URL
        "local": "http://localhost:8080",
    }

    return env_urls.get(deployment_env, env_urls["staging"])


@pytest.fixture(scope="session")
def frontend_base_url(deployment_env: str) -> str:
    """
    Get the frontend base URL for the deployment environment.

    Args:
        deployment_env: The deployment environment

    Returns:
        str: Frontend base URL

    Environment variable: FRONTEND_BASE_URL (overrides default)
    """
    # Allow explicit override via environment variable
    if override_url := os.getenv("FRONTEND_BASE_URL"):
        return override_url

    # Default URLs per environment
    env_urls = {
        "staging": "http://localhost:3001",
        "production": "https://tta.example.com",  # Update with actual production URL
        "local": "http://localhost:3000",
    }

    return env_urls.get(deployment_env, env_urls["staging"])


@pytest.fixture(scope="session")
async def api_client(api_base_url: str) -> httpx.AsyncClient:
    """
    Create an async HTTP client for API requests.

    Args:
        api_base_url: The API base URL

    Yields:
        httpx.AsyncClient: Configured async HTTP client
    """
    async with httpx.AsyncClient(
        base_url=api_base_url,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture(scope="session")
def test_user_credentials() -> dict[str, str]:
    """
    Get test user credentials for authentication tests.

    Returns:
        dict: Test user credentials

    Environment variables:
        TEST_USER_USERNAME: Test user username (default: 'test_deployment_user')
        TEST_USER_PASSWORD: Test user password (default: 'TestPassword123!')
        TEST_USER_EMAIL: Test user email (default: 'test_deployment@example.com')
    """
    return {
        "username": os.getenv("TEST_USER_USERNAME", "test_deployment_user"),
        "password": os.getenv("TEST_USER_PASSWORD", "TestPassword123!"),
        "email": os.getenv("TEST_USER_EMAIL", "test_deployment@example.com"),
    }


@pytest.fixture
async def health_check(api_client: httpx.AsyncClient) -> dict[str, Any]:
    """
    Perform health check before running tests.

    Args:
        api_client: The API client

    Returns:
        dict: Health check response

    Raises:
        pytest.skip: If health check fails
    """
    try:
        response = await api_client.get("/api/v1/health/")
        response.raise_for_status()
        health_data = response.json()

        # Skip tests if system is not healthy
        if health_data.get("status") != "healthy":
            pytest.skip(
                f"System health check failed: {health_data.get('status')}. "
                "Skipping post-deployment tests."
            )

        return health_data

    except Exception as e:
        pytest.skip(
            f"Health check endpoint unavailable: {e}. Skipping post-deployment tests."
        )


@pytest.fixture
def skip_if_production(deployment_env: str):
    """
    Skip test if running against production environment.

    Use this fixture for tests that should not run in production
    (e.g., tests that create test data).

    Args:
        deployment_env: The deployment environment

    Raises:
        pytest.skip: If environment is production
    """
    if deployment_env == "production":
        pytest.skip("Test skipped in production environment")


@pytest.fixture(scope="session")
def neo4j_config(deployment_env: str) -> dict[str, str]:
    """
    Get Neo4j configuration for the deployment environment.

    Args:
        deployment_env: The deployment environment

    Returns:
        dict: Neo4j connection configuration

    Environment variables:
        NEO4J_URI: Neo4j URI (default: bolt://localhost:7687)
        NEO4J_USERNAME: Neo4j username (default: neo4j)
        NEO4J_PASSWORD: Neo4j password (default: test_password)
    """
    return {
        "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "username": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", "test_password"),
    }


@pytest.fixture(scope="session")
def redis_config(deployment_env: str) -> dict[str, Any]:
    """
    Get Redis configuration for the deployment environment.

    Args:
        deployment_env: The deployment environment

    Returns:
        dict: Redis connection configuration

    Environment variables:
        REDIS_HOST: Redis host (default: localhost)
        REDIS_PORT: Redis port (default: 6379)
        REDIS_PASSWORD: Redis password (optional)
        REDIS_DB: Redis database number (default: 0)
    """
    return {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "password": os.getenv("REDIS_PASSWORD"),
        "db": int(os.getenv("REDIS_DB", "0")),
    }


@pytest.fixture
async def authenticated_client(
    api_client: httpx.AsyncClient,
    test_user_credentials: dict[str, str],
    skip_if_production: None,
) -> tuple[httpx.AsyncClient, dict[str, Any]]:
    """
    Create an authenticated API client with test user.

    This fixture creates a test user (if needed), authenticates,
    and returns a client with authorization headers set.

    Args:
        api_client: The base API client
        test_user_credentials: Test user credentials
        skip_if_production: Skip in production

    Returns:
        tuple: (authenticated_client, token_data)

    Note: This fixture is skipped in production to avoid creating test users.
    """
    # Try to login first (user might already exist)
    login_response = await api_client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"],
        },
    )

    # If login fails, try to register the user
    if login_response.status_code == 401:
        register_response = await api_client.post(
            "/api/v1/auth/register",
            json=test_user_credentials,
        )
        register_response.raise_for_status()

        # Login after registration
        login_response = await api_client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user_credentials["username"],
                "password": test_user_credentials["password"],
            },
        )

    login_response.raise_for_status()
    token_data = login_response.json()

    # Create new client with authorization header
    auth_client = httpx.AsyncClient(
        base_url=api_client.base_url,
        timeout=api_client.timeout,
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
        follow_redirects=True,
    )

    yield auth_client, token_data

    # Cleanup
    await auth_client.aclose()
