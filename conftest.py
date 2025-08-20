import os
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--neo4j", action="store_true", default=False,
        help="Run tests that require a running Neo4j instance",
    )
    parser.addoption(
        "--redis", action="store_true", default=False,
        help="Run tests that require a running Redis instance",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "neo4j: test requires Neo4j")
    config.addinivalue_line("markers", "redis: test requires Redis")


@pytest.fixture(autouse=True)
def _skip_neo4j_marker(request):
    marker = request.node.get_closest_marker("neo4j")
    if marker is not None:
        if not request.config.getoption("--neo4j") and os.environ.get("RUN_NEO4J_TESTS") not in {"1", "true", "True"}:
            pytest.skip("Skipping Neo4j tests (enable with --neo4j or RUN_NEO4J_TESTS=1)")


@pytest.fixture(autouse=True)
def _skip_redis_marker(request):
    marker = request.node.get_closest_marker("redis")
    if marker is not None:
        if not request.config.getoption("--redis") and os.environ.get("RUN_REDIS_TESTS") not in {"1", "true", "True"}:
            pytest.skip("Skipping Redis tests (enable with --redis or RUN_REDIS_TESTS=1)")

