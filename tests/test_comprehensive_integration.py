"""
Integration tests that demonstrate comprehensive test battery integration.

These tests show how existing test suites can leverage the comprehensive
test battery framework for enhanced testing capabilities.
"""

import json
import os

import pytest

# Mark all tests in this module as comprehensive
pytestmark = pytest.mark.comprehensive


@pytest.mark.asyncio
async def test_comprehensive_framework_integration(
    mock_service_manager, comprehensive_test_config
):
    """Test that comprehensive test battery integrates with existing test framework."""

    # Verify mock service manager is available
    assert mock_service_manager is not None

    # Test Neo4j integration
    neo4j_driver = await mock_service_manager.get_neo4j_driver(
        comprehensive_test_config.neo4j_uri,
        auth=(
            comprehensive_test_config.neo4j_user,
            comprehensive_test_config.neo4j_password,
        ),
    )

    async with neo4j_driver.session() as session:
        result = await session.run(
            "CREATE (n:TestNode {name: $name}) RETURN n", name="integration_test"
        )
        record = await result.single()
        assert record is not None

    # Test Redis integration
    redis_client = await mock_service_manager.get_redis_client(
        comprehensive_test_config.redis_url
    )

    await redis_client.set("test:integration", "success", ex=300)
    value = await redis_client.get("test:integration")
    assert value in {b"success", "success"}

    # Cleanup
    await neo4j_driver.close()
    await redis_client.close()


@pytest.mark.asyncio
async def test_service_status_reporting(mock_service_manager):
    """Test that service status is properly reported."""

    status = await mock_service_manager.get_service_status()

    assert "neo4j" in status
    assert "redis" in status

    # Each service should have status and details
    for service_info in status.values():
        assert "status" in service_info
        assert service_info["status"] in ["real", "mock"]

        if service_info["status"] == "mock":
            assert "reason" in service_info


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mixed_service_environment(
    mock_service_manager, comprehensive_test_config
):
    """Test operation in mixed real/mock service environment."""

    # Get both services
    neo4j_driver = await mock_service_manager.get_neo4j_driver(
        comprehensive_test_config.neo4j_uri,
        auth=(
            comprehensive_test_config.neo4j_user,
            comprehensive_test_config.neo4j_password,
        ),
    )
    redis_client = await mock_service_manager.get_redis_client(
        comprehensive_test_config.redis_url
    )

    # Test cross-service operation
    user_id = "test_user_mixed_env"

    # Store user in Neo4j
    async with neo4j_driver.session() as session:
        await session.run(
            "CREATE (u:User {id: $id, name: $name, created_at: $created_at})",
            id=user_id,
            name="Mixed Environment Test User",
            created_at="2025-09-15T12:00:00Z",
        )

    # Store session data in Redis
    session_data = {
        "user_id": user_id,
        "session_start": "2025-09-15T12:00:00Z",
        "last_activity": "2025-09-15T12:05:00Z",
    }
    await redis_client.hset(
        f"session:{user_id}", mapping={k: str(v) for k, v in session_data.items()}
    )

    # Verify data consistency
    async with neo4j_driver.session() as session:
        result = await session.run("MATCH (u:User {id: $id}) RETURN u", id=user_id)
        user_record = await result.single()
        assert user_record is not None
        assert user_record["u"]["name"] == "Mixed Environment Test User"

    stored_session = await redis_client.hgetall(f"session:{user_id}")
    assert (
        stored_session[b"user_id"] == user_id.encode()
        or stored_session["user_id"] == user_id
    )

    # Cleanup
    async with neo4j_driver.session() as session:
        await session.run("MATCH (u:User {id: $id}) DELETE u", id=user_id)
    await redis_client.delete(f"session:{user_id}")

    await neo4j_driver.close()
    await redis_client.close()


@pytest.mark.slow
@pytest.mark.asyncio
async def test_comprehensive_test_data_generation():
    """Test integration with comprehensive test battery data generation."""

    try:
        from tests.comprehensive_battery.utils.test_data_generator import (
            TestDataGenerator,
        )

        generator = TestDataGenerator()

        # Generate test users
        users = await generator.generate_test_users(count=3)
        assert len(users) == 3

        for user in users:
            assert hasattr(user, "user_id")
            assert hasattr(user, "username")
            assert hasattr(user, "email")
            assert hasattr(user, "gaming_experience")
            assert hasattr(user, "preferences")

        # Generate test scenarios
        scenarios = await generator.generate_story_scenarios(count=2)
        assert len(scenarios) == 2

        for scenario in scenarios:
            assert hasattr(scenario, "scenario_id")
            assert hasattr(scenario, "name")
            assert hasattr(scenario, "description")
            assert hasattr(scenario, "duration_minutes")

    except ImportError:
        pytest.skip("Test data generator not available")


@pytest.mark.mock_only
@pytest.mark.asyncio
async def test_mock_only_functionality(mock_service_manager):
    """Test functionality that should only run in mock mode."""

    # Force mock mode for this test
    os.environ["FORCE_MOCK_MODE"] = "true"

    try:
        # Get services (should be mocked)
        neo4j_driver = await mock_service_manager.get_neo4j_driver(
            "bolt://localhost:7687", auth=("neo4j", "testpassword")
        )
        redis_client = await mock_service_manager.get_redis_client(
            "redis://localhost:6379"
        )

        # Verify they are mock implementations
        status = await mock_service_manager.get_service_status()
        assert status["neo4j"]["status"] == "mock"

        # Test mock-specific behavior
        async with neo4j_driver.session() as session:
            # Mock should handle any query
            result = await session.run("MATCH (n) RETURN count(n) as total")
            record = await result.single()
            assert record is not None

        # Test Redis mock
        await redis_client.set("mock:test", "mock_value")
        value = await redis_client.get("mock:test")
        assert value is not None

        await neo4j_driver.close()
        await redis_client.close()

    finally:
        os.environ.pop("FORCE_MOCK_MODE", None)


def test_comprehensive_test_environment_setup():
    """Test that comprehensive test environment is properly configured."""

    # Check environment variables
    assert os.getenv("TESTING") == "true"
    assert os.getenv("LOG_LEVEL") is not None

    # Check comprehensive test availability
    if os.getenv("COMPREHENSIVE_TEST_ACTIVE") == "true":
        assert os.getenv("COMPREHENSIVE_TEST_MODE") == "true"


@pytest.mark.asyncio
async def test_test_result_integration():
    """Test that test results integrate with comprehensive test battery reporting."""

    # Simulate test execution with results
    test_results = {
        "test_name": "test_comprehensive_integration",
        "status": "passed",
        "duration": 1.5,
        "framework": "pytest",
        "comprehensive_integration": True,
    }

    # If in comprehensive test mode, results should be collected
    if os.getenv("COMPREHENSIVE_TEST_MODE") == "true":
        output_dir = os.getenv("TEST_OUTPUT_DIR", "./test-results")
        os.makedirs(output_dir, exist_ok=True)

        # Write integration test results
        with open(f"{output_dir}/integration_test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)

        # Verify file was created
        assert os.path.exists(f"{output_dir}/integration_test_results.json")


@pytest.mark.real_services
@pytest.mark.asyncio
async def test_real_services_required():
    """Test that requires real services (will be skipped in CI if not available)."""

    # This test would only run when real services are available
    # It demonstrates how to mark tests that need actual database connections

    if os.getenv("FORCE_MOCK_MODE") == "true":
        pytest.skip("Test requires real services but mock mode is forced")

    # Test would use real Neo4j and Redis connections here
    # For now, just verify the test environment
    assert os.getenv("TESTING") == "true"


class TestComprehensiveIntegration:
    """Test class demonstrating comprehensive test battery integration patterns."""

    @pytest.mark.asyncio
    async def test_class_based_integration(self, mock_service_manager):
        """Test comprehensive integration in class-based tests."""

        # Verify service manager is available
        assert mock_service_manager is not None

        # Test service status
        status = await mock_service_manager.get_service_status()
        assert isinstance(status, dict)
        assert len(status) > 0

    def test_sync_integration(self):
        """Test synchronous integration with comprehensive framework."""

        # Verify environment setup
        assert os.getenv("TESTING") == "true"

        # Test can access comprehensive test configuration
        if os.getenv("COMPREHENSIVE_TEST_ACTIVE") == "true":
            assert os.getenv("LOG_LEVEL") is not None

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_performance_integration(self, mock_service_manager):
        """Test performance aspects of comprehensive integration."""

        import time

        start_time = time.time()

        # Simulate multiple service operations
        neo4j_driver = await mock_service_manager.get_neo4j_driver(
            "bolt://localhost:7687", auth=("neo4j", "testpassword")
        )
        redis_client = await mock_service_manager.get_redis_client(
            "redis://localhost:6379"
        )

        # Perform multiple operations
        for i in range(10):
            async with neo4j_driver.session() as session:
                await session.run(f"CREATE (n:PerfTest {{id: {i}}}) RETURN n")

            await redis_client.set(f"perf:test:{i}", f"value_{i}")

        end_time = time.time()
        duration = end_time - start_time

        # Performance should be reasonable even with mock services
        assert duration < 5.0  # Should complete within 5 seconds

        await neo4j_driver.close()
        await redis_client.close()
