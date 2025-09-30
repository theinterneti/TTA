import os
import pytest
import logging
import sys
from pathlib import Path
from unittest.mock import Mock

# Add project root to path for comprehensive test battery integration
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import comprehensive test battery components
try:
    from tests.comprehensive_battery.mocks.mock_services import MockServiceManager
    from tests.comprehensive_battery.comprehensive_test_battery import TestBatteryConfig
    COMPREHENSIVE_TEST_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_TEST_AVAILABLE = False


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
    from unittest.mock import AsyncMock
    mock_driver = Mock()
    mock_session_ctx = Mock()
    mock_driver.session.return_value = mock_session_ctx

    # Mock session methods
    mock_session = Mock()
    mock_session.run = Mock(return_value=Mock(single=Mock(return_value=None)))
    mock_session.close = AsyncMock()
    mock_session_ctx.__enter__.return_value = mock_session
    mock_session_ctx.__exit__.return_value = None
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

    # Mock driver methods
    mock_driver.close = Mock()
    mock_driver.verify_connectivity = Mock()

    return mock_driver


@pytest.fixture()
def mock_redis_client():
    """Provide a simple mock Redis client for unit tests."""
    from unittest.mock import AsyncMock
    mock_client = Mock()

    # Mock common Redis methods
    mock_client.get = AsyncMock(return_value=None)
    mock_client.set = AsyncMock(return_value=True)
    mock_client.delete = AsyncMock(return_value=1)
    mock_client.exists = AsyncMock(return_value=0)
    mock_client.ping = AsyncMock(return_value=True)
    mock_client.close = AsyncMock()
    mock_client.aclose = AsyncMock()

    # Mock hash operations
    mock_client.hget = AsyncMock(return_value=None)
    mock_client.hset = AsyncMock(return_value=1)
    mock_client.hgetall = AsyncMock(return_value={})
    mock_client.hdel = AsyncMock(return_value=1)

    # Mock list operations
    mock_client.lpush = AsyncMock(return_value=1)
    mock_client.rpush = AsyncMock(return_value=1)
    mock_client.lpop = AsyncMock(return_value=None)
    mock_client.rpop = AsyncMock(return_value=None)
    mock_client.lrange = AsyncMock(return_value=[])

    # Mock set operations
    mock_client.sadd = AsyncMock(return_value=1)
    mock_client.smembers = AsyncMock(return_value=set())
    mock_client.srem = AsyncMock(return_value=1)

    return mock_client


# --- Testcontainers: Neo4j & Redis fixtures ---
@pytest.fixture(scope="session")
def neo4j_container(pytestconfig):
    if not (pytestconfig.getoption("--neo4j") or os.environ.get("RUN_NEO4J_TESTS") in {"1","true","True"}):
        pytest.skip("Neo4j not requested; use --neo4j or RUN_NEO4J_TESTS=1")

    # If CI provides a service, prefer it to avoid nested containers
    svc_uri = os.environ.get("TEST_NEO4J_URI")
    if svc_uri:
        yield {
            "uri": svc_uri,
            "username": os.environ.get("TEST_NEO4J_USERNAME", "neo4j"),
            "password": os.environ.get("TEST_NEO4J_PASSWORD", "testpassword"),
        }
        return

    from testcontainers.neo4j import Neo4jContainer
    with (
        Neo4jContainer("neo4j:5-community")
        .with_env("NEO4J_AUTH", "neo4j/testpassword")
        .with_env("NEO4J_ACCEPT_LICENSE_AGREEMENT", "yes")
    ) as neo4j:
        # Readiness probe: wait for auth subsystem to be fully initialized
        try:
            from neo4j import GraphDatabase
            from neo4j.exceptions import AuthError, ServiceUnavailable as _ServiceUnavailable, ClientError as _ClientError
        except Exception:
            GraphDatabase = None  # type: ignore
            AuthError = Exception  # type: ignore
            _ServiceUnavailable = Exception  # type: ignore
            _ClientError = Exception  # type: ignore
        import time as _t, logging as _logging
        _logger = _logging.getLogger(__name__)
        uri = neo4j.get_connection_url()
        username = "neo4j"
        password = "testpassword"
        if GraphDatabase is not None:
            # Small initial wait to avoid early unauthorized during server auth init
            try:
                _logger.debug("Neo4j Testcontainer initial wait 10.0s before readiness probe")
                _t.sleep(10.0)
            except Exception:
                pass
            base_delay = 0.5
            attempts = 10
            for attempt in range(attempts):
                try:
                    d = GraphDatabase.driver(uri, auth=(username, password))
                    try:
                        with d.session() as s:
                            s.run("RETURN 1")
                        _logger.debug("Neo4j container ready after attempt %s", attempt + 1)
                        break
                    finally:
                        d.close()
                except (AuthError, _ServiceUnavailable) as e:
                    delay = min(base_delay * (2 ** attempt), 8.0)
                    _logger.debug("Neo4j container not ready (%s); retry in %.1fs", type(e).__name__, delay)
                    if attempt < (attempts - 1):
                        _t.sleep(delay)
                    else:
                        _logger.warning("Neo4j readiness probe exhausted attempts with %s; proceeding to yield credentials and let client retry", type(e).__name__)
                        break
                except _ClientError as e:
                    emsg = str(e)
                    if ("AuthenticationRateLimit" in emsg) or ("authentication details too many times" in emsg):
                        delay = min(base_delay * (2 ** attempt), 8.0)
                        _logger.debug("Neo4j container rate limited; retry in %.1fs", delay)
                        if attempt < (attempts - 1):
                            _t.sleep(delay)
                        else:
                            _logger.warning("Neo4j readiness probe exhausted attempts on AuthenticationRateLimit; proceeding to yield credentials")
                            break
                    else:
                        _logger.warning("Neo4j readiness probe got unexpected ClientError: %s; proceeding without blocking", emsg)
                        break
                except Exception as e:
                    # Do not fail the entire test session; proceed and let client retry
                    _logger.warning("Neo4j readiness probe encountered unexpected error: %s; proceeding", e)
                    break
        yield {
            "uri": uri,
            "username": username,
            "password": password,
        }


@pytest.fixture(scope="session")
def neo4j_driver(neo4j_container):
    # Hardened readiness: retry to avoid AuthenticationRateLimit/Unauthorized races
    from neo4j import GraphDatabase
    try:
        from neo4j.exceptions import AuthError, ServiceUnavailable as _ServiceUnavailable, ClientError as _ClientError
    except Exception:
        AuthError = Exception  # type: ignore
        _ServiceUnavailable = Exception  # type: ignore
        _ClientError = Exception  # type: ignore
    import time as _t, logging as _logging
    _logger = _logging.getLogger(__name__)

    uri = neo4j_container["uri"]
    username = neo4j_container["username"]
    password = neo4j_container["password"]

    base_delay = 0.5
    attempts = 10
    last_exc = None
    d = None
    for attempt in range(attempts):
        try:
            d = GraphDatabase.driver(uri, auth=(username, password))
            with d.session() as s:
                s.run("RETURN 1")
            # Success
            try:
                yield d
            finally:
                try:
                    d.close()
                except Exception:
                    pass
            return
        except (AuthError, _ServiceUnavailable) as e:
            last_exc = e
            delay = min(base_delay * (2 ** attempt), 8.0)
            _logger.debug("neo4j_driver readiness attempt %d/%d failed (%s); retry in %.1fs", attempt + 1, attempts, type(e).__name__, delay)
            try:
                if d:
                    d.close()
            except Exception:
                pass
            if attempt < (attempts - 1):
                _t.sleep(delay)
            else:
                break
        except _ClientError as e:
            emsg = str(e)
            last_exc = e
            if ("AuthenticationRateLimit" in emsg) or ("authentication details too many times" in emsg):
                delay = min(base_delay * (2 ** attempt), 8.0)
                _logger.debug("neo4j_driver readiness hit AuthenticationRateLimit; retry in %.1fs", delay)
                try:
                    if d:
                        d.close()
                except Exception:
                    pass
                if attempt < (attempts - 1):
                    _t.sleep(delay)
                else:
                    break
            else:
                # Unexpected ClientError: do not retry endlessly
                try:
                    if d:
                        d.close()
                except Exception:
                    pass
                raise
        except Exception as e:
            last_exc = e
            try:
                if d:
                    d.close()
            except Exception:
                pass
            raise
    # Exhausted retries
    if last_exc:
        raise last_exc
    raise RuntimeError("neo4j_driver readiness failed without exception")


@pytest.fixture(scope="session")
def redis_container(pytestconfig):
    if not (pytestconfig.getoption("--redis") or os.environ.get("RUN_REDIS_TESTS") in {"1","true","True"}):
        pytest.skip("Redis container not requested; use --redis or RUN_REDIS_TESTS=1")

    # Prefer CI-provided service if available
    svc_uri = os.environ.get("TEST_REDIS_URI")
    if svc_uri:
        yield svc_uri
        return

    from testcontainers.redis import RedisContainer
    prev_env = os.environ.get("TEST_REDIS_URI")
    try:
        with RedisContainer("redis:7") as rc:
            host = rc.get_container_host_ip()
            port = rc.get_exposed_port(6379)
            uri = f"redis://{host}:{port}/0"
            # Export for tests that read from env
            os.environ["TEST_REDIS_URI"] = uri
            yield uri
    finally:
        # Restore previous value
        if prev_env is None:
            os.environ.pop("TEST_REDIS_URI", None)
        else:
            os.environ["TEST_REDIS_URI"] = prev_env


import pytest_asyncio


@pytest.fixture(scope="session")
def redis_client_sync(redis_container):
    # Synchronous client for sync tests
    import redis
    client = redis.Redis.from_url(redis_container)
    try:
        client.ping()
        yield client
    finally:
        client.close()


@pytest_asyncio.fixture()
async def redis_client(redis_container):
    # Async client for async repository tests
    import redis.asyncio as aioredis
    client = aioredis.from_url(redis_container)
    try:
        await client.ping()
        yield client
    finally:
        await client.aclose()



@pytest.fixture()
def redis_client_sync(redis_container):
    """Synchronous Redis client for simple integration tests.
    Returns redis.Redis so .get/.exists return concrete results, not coroutines.
    """
    import redis
    client = redis.from_url(redis_container)
    try:
        # Basic liveness check
        client.ping()
        yield client
    finally:
        try:
            client.close()
        except Exception:
            pass


# Comprehensive Test Battery Integration
@pytest.fixture(scope="session")
async def comprehensive_test_config():
    """Provide comprehensive test battery configuration."""
    if not COMPREHENSIVE_TEST_AVAILABLE:
        pytest.skip("Comprehensive test battery not available")

    config = TestBatteryConfig()

    # Override with test-specific settings
    config.neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    config.neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    config.neo4j_password = os.getenv('NEO4J_PASSWORD', 'testpassword')
    config.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

    # Test-specific overrides
    config.max_concurrent_tests = 2
    config.test_timeout_seconds = 300
    config.cleanup_between_tests = True

    return config


@pytest.fixture(scope="session")
async def mock_service_manager():
    """Provide mock service manager for comprehensive testing."""
    if not COMPREHENSIVE_TEST_AVAILABLE:
        pytest.skip("Comprehensive test battery not available")

    manager = MockServiceManager()
    yield manager
    await manager.cleanup()


# Pytest configuration for comprehensive test battery
def pytest_configure(config):
    """Configure pytest with comprehensive test battery markers."""
    config.addinivalue_line(
        "markers", "comprehensive: mark test as part of comprehensive test battery"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "mock_only: mark test to run only in mock mode"
    )
    config.addinivalue_line(
        "markers", "real_services: mark test to require real services"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment and comprehensive test battery settings."""
    # Skip real service tests in CI if services aren't available
    if os.getenv('CI') == 'true' and os.getenv('SKIP_REAL_SERVICE_TESTS') == 'true':
        skip_real = pytest.mark.skip(reason="Real services not available in CI")
        for item in items:
            if "real_services" in item.keywords:
                item.add_marker(skip_real)

    # Add slow marker to integration tests
    for item in items:
        if "integration" in item.keywords or "comprehensive" in item.keywords:
            item.add_marker(pytest.mark.slow)

    # Skip comprehensive tests if not available
    if not COMPREHENSIVE_TEST_AVAILABLE:
        skip_comprehensive = pytest.mark.skip(reason="Comprehensive test battery not available")
        for item in items:
            if "comprehensive" in item.keywords:
                item.add_marker(skip_comprehensive)


# Test environment setup
@pytest.fixture(autouse=True)
def test_environment_setup():
    """Set up test environment variables for comprehensive test battery integration."""
    # Ensure we're in test mode
    os.environ['TESTING'] = 'true'
    os.environ['LOG_LEVEL'] = os.getenv('LOG_LEVEL', 'INFO')

    # Mock mode settings for CI environments
    if os.getenv('CI') == 'true':
        os.environ['FORCE_MOCK_MODE'] = os.getenv('FORCE_MOCK_MODE', 'true')

    # Comprehensive test mode flag
    if os.getenv('COMPREHENSIVE_TEST_MODE') == 'true':
        os.environ['COMPREHENSIVE_TEST_ACTIVE'] = 'true'

    yield

    # Cleanup
    os.environ.pop('TESTING', None)
    os.environ.pop('COMPREHENSIVE_TEST_ACTIVE', None)

