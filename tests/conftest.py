import os
import pytest
from unittest.mock import Mock


def has_neo4j():
    try:
        import neo4j  # noqa: F401
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def neo4j_available():
    # Respect CLI flag or env var first
    if os.environ.get("RUN_NEO4J_TESTS") in {"1", "true", "True"}:
        return True
    # If user explicitly passed --neo4j, the global conftest gate will allow it
    return has_neo4j()


@pytest.fixture()
def mock_neo4j_driver():
    """Provide a simple mock Neo4j driver/session for unit tests."""
    mock_driver = Mock()
    mock_session_ctx = Mock()
    mock_driver.session.return_value = mock_session_ctx
    mock_session_ctx.__enter__.return_value = Mock(run=Mock(return_value=Mock(single=Mock(return_value=None))))
    mock_session_ctx.__exit__.return_value = None
    return mock_driver


# --- Testcontainers: Neo4j & Redis fixtures ---
@pytest.fixture(scope="session")
def neo4j_container(pytestconfig):
    if not (pytestconfig.getoption("--neo4j") or os.environ.get("RUN_NEO4J_TESTS") in {"1","true","True"}):
        pytest.skip("Neo4j not requested; use --neo4j or RUN_NEO4J_TESTS=1")

    # If CI provides a service, prefer it to avoid nested containers
    svc_uri = os.environ.get("TEST_NEO4J_URI")
    if svc_uri:
        return {
            "uri": svc_uri,
            "username": os.environ.get("TEST_NEO4J_USERNAME", "neo4j"),
            "password": os.environ.get("TEST_NEO4J_PASSWORD", "testpassword"),
        }

    from testcontainers.neo4j import Neo4jContainer
    with (
        Neo4jContainer("neo4j:5-community")
        .with_env("NEO4J_AUTH", "neo4j/testpassword")
        .with_env("NEO4J_ACCEPT_LICENSE_AGREEMENT", "yes")
    ) as neo4j:
        yield {
            "uri": neo4j.get_connection_url(),
            "username": "neo4j",
            "password": "testpassword",
        }


@pytest.fixture(scope="session")
def neo4j_driver(neo4j_container):
    from neo4j import GraphDatabase
    d = GraphDatabase.driver(neo4j_container["uri"], auth=(neo4j_container["username"], neo4j_container["password"]))
    try:
        with d.session() as s:
            s.run("RETURN 1")
        yield d
    finally:
        d.close()


@pytest.fixture(scope="session")
def redis_container(pytestconfig):
    if not (pytestconfig.getoption("--redis") or os.environ.get("RUN_REDIS_TESTS") in {"1","true","True"}):
        pytest.skip("Redis container not requested; use --redis or RUN_REDIS_TESTS=1")
    from testcontainers.redis import RedisContainer
    with RedisContainer("redis:7") as rc:
        yield rc.get_connection_url()


import pytest_asyncio


@pytest_asyncio.fixture()
async def redis_client(redis_container):
    # Use asyncio Redis client for compatibility with async code
    import redis.asyncio as aioredis
    client = aioredis.from_url(redis_container)
    try:
        await client.ping()
        yield client
    finally:
        await client.close()

