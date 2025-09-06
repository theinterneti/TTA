import os
from unittest.mock import Mock

import pytest
import pytest_asyncio


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
    mock_session_ctx.__enter__.return_value = Mock(
        run=Mock(return_value=Mock(single=Mock(return_value=None)))
    )
    mock_session_ctx.__exit__.return_value = None
    return mock_driver


# --- Testcontainers: Neo4j & Redis fixtures ---
@pytest.fixture(scope="session")
def neo4j_container(pytestconfig):
    if not (
        pytestconfig.getoption("--neo4j")
        or os.environ.get("RUN_NEO4J_TESTS") in {"1", "true", "True"}
    ):
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
            from neo4j.exceptions import (
                AuthError,
            )
            from neo4j.exceptions import ClientError as _ClientError
            from neo4j.exceptions import ServiceUnavailable as _ServiceUnavailable
        except Exception:
            GraphDatabase = None  # type: ignore
            AuthError = Exception  # type: ignore
            _ServiceUnavailable = Exception  # type: ignore
            _ClientError = Exception  # type: ignore
        import logging as _logging
        import time as _t

        _logger = _logging.getLogger(__name__)
        uri = neo4j.get_connection_url()
        username = "neo4j"
        password = "testpassword"
        if GraphDatabase is not None:
            # Small initial wait to avoid early unauthorized during server auth init
            try:
                _logger.debug(
                    "Neo4j Testcontainer initial wait 10.0s before readiness probe"
                )
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
                        _logger.debug(
                            "Neo4j container ready after attempt %s", attempt + 1
                        )
                        break
                    finally:
                        d.close()
                except (AuthError, _ServiceUnavailable) as e:
                    delay = min(base_delay * (2**attempt), 8.0)
                    _logger.debug(
                        "Neo4j container not ready (%s); retry in %.1fs",
                        type(e).__name__,
                        delay,
                    )
                    if attempt < (attempts - 1):
                        _t.sleep(delay)
                    else:
                        _logger.warning(
                            "Neo4j readiness probe exhausted attempts with %s; proceeding to yield credentials and let client retry",
                            type(e).__name__,
                        )
                        break
                except _ClientError as e:
                    emsg = str(e)
                    if ("AuthenticationRateLimit" in emsg) or (
                        "authentication details too many times" in emsg
                    ):
                        delay = min(base_delay * (2**attempt), 8.0)
                        _logger.debug(
                            "Neo4j container rate limited; retry in %.1fs", delay
                        )
                        if attempt < (attempts - 1):
                            _t.sleep(delay)
                        else:
                            _logger.warning(
                                "Neo4j readiness probe exhausted attempts on AuthenticationRateLimit; proceeding to yield credentials"
                            )
                            break
                    else:
                        _logger.warning(
                            "Neo4j readiness probe got unexpected ClientError: %s; proceeding without blocking",
                            emsg,
                        )
                        break
                except Exception as e:
                    # Do not fail the entire test session; proceed and let client retry
                    _logger.warning(
                        "Neo4j readiness probe encountered unexpected error: %s; proceeding",
                        e,
                    )
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
        from neo4j.exceptions import (
            AuthError,
        )
        from neo4j.exceptions import ClientError as _ClientError
        from neo4j.exceptions import ServiceUnavailable as _ServiceUnavailable
    except Exception:
        AuthError = Exception  # type: ignore
        _ServiceUnavailable = Exception  # type: ignore
        _ClientError = Exception  # type: ignore
    import logging as _logging
    import time as _t

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
            delay = min(base_delay * (2**attempt), 8.0)
            _logger.debug(
                "neo4j_driver readiness attempt %d/%d failed (%s); retry in %.1fs",
                attempt + 1,
                attempts,
                type(e).__name__,
                delay,
            )
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
            if ("AuthenticationRateLimit" in emsg) or (
                "authentication details too many times" in emsg
            ):
                delay = min(base_delay * (2**attempt), 8.0)
                _logger.debug(
                    "neo4j_driver readiness hit AuthenticationRateLimit; retry in %.1fs",
                    delay,
                )
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
    if not (
        pytestconfig.getoption("--redis")
        or os.environ.get("RUN_REDIS_TESTS") in {"1", "true", "True"}
    ):
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
