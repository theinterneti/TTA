"""
Integration tests for enhanced mock services.

This module provides comprehensive testing for the mock service implementations
to ensure they behave realistically and support the development workflow.
"""

import time
from datetime import datetime, timedelta

import pytest

from src.player_experience.api.mock_services import (
    MockNeo4jDriver,
    MockRedisClient,
    MockServiceConfig,
    MockServiceMetrics,
    MockServiceState,
)


class TestMockServiceConfig:
    """Test mock service configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MockServiceConfig()
        assert config.base_latency_ms == 10.0
        assert config.latency_variance_ms == 5.0
        assert config.failure_rate == 0.0
        assert config.state == MockServiceState.HEALTHY
        assert config.enable_persistence is True
        assert config.max_memory_items == 10000

    def test_custom_config(self):
        """Test custom configuration values."""
        config = MockServiceConfig(
            base_latency_ms=50.0,
            failure_rate=0.1,
            state=MockServiceState.DEGRADED,
            max_memory_items=5000,
        )
        assert config.base_latency_ms == 50.0
        assert config.failure_rate == 0.1
        assert config.state == MockServiceState.DEGRADED
        assert config.max_memory_items == 5000


class TestMockServiceMetrics:
    """Test mock service metrics tracking."""

    def test_initial_metrics(self):
        """Test initial metrics state."""
        metrics = MockServiceMetrics()
        assert metrics.total_operations == 0
        assert metrics.successful_operations == 0
        assert metrics.failed_operations == 0
        assert metrics.success_rate == 1.0
        assert metrics.average_latency_ms == 0.0

    def test_metrics_calculation(self):
        """Test metrics calculations."""
        metrics = MockServiceMetrics()
        metrics.total_operations = 10
        metrics.successful_operations = 8
        metrics.failed_operations = 2
        metrics.total_latency_ms = 80.0

        assert metrics.success_rate == 0.8
        assert metrics.average_latency_ms == 10.0

    def test_metrics_to_dict(self):
        """Test metrics dictionary conversion."""
        metrics = MockServiceMetrics()
        metrics.total_operations = 5
        metrics.successful_operations = 4
        metrics.failed_operations = 1

        result = metrics.to_dict()
        assert isinstance(result, dict)
        assert result["total_operations"] == 5
        assert result["successful_operations"] == 4
        assert result["failed_operations"] == 1
        assert result["success_rate"] == 0.8


class TestMockNeo4jDriver:
    """Test enhanced Neo4j mock driver."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = MockServiceConfig(base_latency_ms=0.0, log_operations=False)
        self.driver = MockNeo4jDriver(
            "bolt://localhost:7687", ("neo4j", "password"), self.config
        )

    def test_driver_initialization(self):
        """Test driver initialization."""
        assert self.driver.uri == "bolt://localhost:7687"
        assert self.driver.auth == ("neo4j", "password")
        assert self.driver.connected is False
        assert len(self.driver._nodes) == 0
        assert len(self.driver._relationships) == 0

    def test_session_creation(self):
        """Test session creation."""
        session = self.driver.session()
        assert session is not None
        assert session.driver == self.driver

    def test_create_operation(self):
        """Test CREATE operation."""
        with self.driver.session() as session:
            result = session._sync_run(
                "CREATE (n:User {name: $name, email: $email})",
                name="test_user",
                email="test@example.com",
            )

            assert len(result.records) == 1
            record = result.single()
            assert record["created"] is True
            assert "node_id" in record
            assert record["properties"]["name"] == "test_user"
            assert record["properties"]["email"] == "test@example.com"

            # Verify data was stored
            assert len(self.driver._nodes) == 1

    def test_match_operation(self):
        """Test MATCH operation."""
        with self.driver.session() as session:
            # First create a node
            session._sync_run("CREATE (n:User {name: $name})", name="test_user")

            # Then match it
            result = session._sync_run(
                "MATCH (n:User) WHERE n.name = $name RETURN n", name="test_user"
            )

            assert len(result.records) == 1
            record = result.single()
            assert record["name"] == "test_user"

    def test_delete_operation(self):
        """Test DELETE operation."""
        with self.driver.session() as session:
            # Create a node
            session._sync_run("CREATE (n:User {name: $name})", name="test_user")
            assert len(self.driver._nodes) == 1

            # Delete it
            result = session._sync_run(
                "DELETE n WHERE n.name = $name", name="test_user"
            )

            record = result.single()
            assert record["deleted"] == 1
            assert len(self.driver._nodes) == 0

    def test_metrics_tracking(self):
        """Test metrics tracking."""
        with self.driver.session() as session:
            session._sync_run("CREATE (n:Test)")
            session._sync_run("MATCH (n:Test) RETURN n")

            metrics = self.driver.get_metrics()
            assert metrics["service"] == "neo4j"
            assert metrics["metrics"]["total_operations"] == 2
            assert metrics["metrics"]["successful_operations"] == 2
            assert metrics["data_stats"]["nodes"] == 1


class TestMockRedisClient:
    """Test enhanced Redis mock client."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = MockServiceConfig(base_latency_ms=0.0, log_operations=False)
        self.redis = MockRedisClient(self.config)

    def teardown_method(self):
        """Clean up after tests."""
        # Note: We'll handle async cleanup in individual tests if needed
        pass

    @pytest.mark.asyncio
    async def test_ping_operation(self):
        """Test ping operation."""
        result = await self.redis.ping()
        assert result == b"PONG"
        assert self.redis.connected is True

    @pytest.mark.asyncio
    async def test_set_get_operations(self):
        """Test set and get operations."""
        # Set a value
        result = await self.redis.set("test_key", "test_value")
        assert result is True

        # Get the value
        value = await self.redis.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_expiration_handling(self):
        """Test key expiration handling."""
        # Set with expiration (longer time to avoid timing issues)
        await self.redis.set("expire_key", "expire_value", ex=10)

        # Should exist immediately
        exists = await self.redis.exists("expire_key")
        assert exists == 1

        # Check TTL (should be close to 10 seconds)
        ttl = await self.redis.ttl("expire_key")
        assert 5 <= ttl <= 10  # Allow some variance for processing time

        # Wait for expiration (simulate by manually setting expiration)
        self.redis._data["expire_key"].expires_at = datetime.now() - timedelta(
            seconds=1
        )

        # Should be expired now
        value = await self.redis.get("expire_key")
        assert value is None

        exists = await self.redis.exists("expire_key")
        assert exists == 0

    @pytest.mark.asyncio
    async def test_delete_operation(self):
        """Test delete operation."""
        # Set multiple keys
        await self.redis.set("key1", "value1")
        await self.redis.set("key2", "value2")

        # Delete them
        deleted = await self.redis.delete("key1", "key2")
        assert deleted == 2

        # Verify they're gone
        assert await self.redis.get("key1") is None
        assert await self.redis.get("key2") is None

    @pytest.mark.asyncio
    async def test_conditional_set_operations(self):
        """Test conditional set operations (NX, XX)."""
        # Test NX (not exists)
        result = await self.redis.set("nx_key", "value1", nx=True)
        assert result is True

        # Should fail because key exists
        result = await self.redis.set("nx_key", "value2", nx=True)
        assert result is False

        # Test XX (exists)
        result = await self.redis.set("nx_key", "value3", xx=True)
        assert result is True

        # Should fail because key doesn't exist
        result = await self.redis.set("nonexistent", "value", xx=True)
        assert result is False

    @pytest.mark.asyncio
    async def test_metrics_tracking(self):
        """Test metrics tracking."""
        await self.redis.ping()
        await self.redis.set("key", "value")
        await self.redis.get("key")
        await self.redis.get("nonexistent")

        metrics = self.redis.get_metrics()
        assert metrics["service"] == "redis"
        assert metrics["metrics"]["total_operations"] == 4
        assert metrics["metrics"]["successful_operations"] == 4
        assert metrics["metrics"]["cache_hits"] == 1
        assert metrics["metrics"]["cache_misses"] == 1


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.neo4j_config = MockServiceConfig(base_latency_ms=5.0, log_operations=False)
        self.redis_config = MockServiceConfig(base_latency_ms=2.0, log_operations=False)

        self.neo4j = MockNeo4jDriver(
            "bolt://localhost:7687", ("neo4j", "password"), self.neo4j_config
        )
        self.redis = MockRedisClient(self.redis_config)

    @pytest.mark.asyncio
    async def test_user_session_scenario(self):
        """Test a realistic user session scenario."""
        # Create user in Neo4j
        with self.neo4j.session() as session:
            result = session._sync_run(
                "CREATE (u:User {id: $id, username: $username, email: $email})",
                id="user123",
                username="testuser",
                email="test@example.com",
            )
            assert result.single()["created"] is True

        # Store session in Redis
        session_data = {
            "user_id": "user123",
            "username": "testuser",
            "login_time": datetime.now().isoformat(),
        }
        await self.redis.set("session:user123", str(session_data), ex=3600)

        # Retrieve session
        cached_session = await self.redis.get("session:user123")
        assert cached_session is not None

        # Verify user exists in Neo4j
        with self.neo4j.session() as session:
            result = session._sync_run(
                "MATCH (u:User {id: $id}) RETURN u", id="user123"
            )
            user = result.single()
            assert user["username"] == "testuser"
            assert user["email"] == "test@example.com"

        # Clean up
        await self.redis.close()

    def test_performance_characteristics(self):
        """Test performance characteristics of mock services."""
        # Test with latency simulation
        config = MockServiceConfig(base_latency_ms=10.0, latency_variance_ms=2.0)
        driver = MockNeo4jDriver("bolt://localhost:7687", ("neo4j", "password"), config)

        time.time()
        with driver.session() as session:
            for i in range(5):
                session._sync_run(f"CREATE (n:Test{i})")
        time.time()

        # Should have some measurable latency (though minimal in sync mode)
        metrics = driver.get_metrics()
        assert metrics["metrics"]["total_operations"] == 5
        assert metrics["metrics"]["successful_operations"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
