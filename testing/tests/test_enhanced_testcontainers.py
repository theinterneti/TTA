"""
Tests for enhanced Testcontainers reliability features.

This module tests the enhanced reliability utilities and fixtures
to ensure they work correctly and provide better error handling.
"""

import logging
from unittest.mock import Mock, patch

import pytest

from tests.utils.testcontainer_reliability import (
    ContainerHealthError,
    ContainerTimeoutError,
    HealthChecker,
    Neo4jHealthChecker,
    RedisHealthChecker,
    async_retry_with_backoff,
    container_logs_on_failure,
    retry_with_backoff,
)

logger = logging.getLogger(__name__)


class TestRetryMechanisms:
    """Test retry mechanisms and backoff strategies."""

    def test_retry_with_backoff_success_first_attempt(self):
        """Test that successful operations don't retry."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        def successful_operation():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_operation()
        assert result == "success"
        assert call_count == 1

    def test_retry_with_backoff_success_after_retries(self):
        """Test that operations succeed after retries."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        def eventually_successful_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Not ready yet")
            return "success"

        result = eventually_successful_operation()
        assert result == "success"
        assert call_count == 3

    def test_retry_with_backoff_exhausts_attempts(self):
        """Test that retry exhausts attempts and raises final exception."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        def always_failing_operation():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError, match="Always fails"):
            always_failing_operation()

        assert call_count == 3

    def test_retry_with_backoff_custom_exceptions(self):
        """Test that retry only catches specified exceptions."""

        @retry_with_backoff(max_attempts=3, base_delay=0.1, exceptions=(ValueError,))
        def operation_with_wrong_exception():
            raise ConnectionError("Wrong exception type")

        # Should not retry ConnectionError when only ValueError is specified
        with pytest.raises(ConnectionError):
            operation_with_wrong_exception()

    def test_retry_callback(self):
        """Test that retry callback is called correctly."""
        callback_calls = []

        def on_retry(attempt, exception):
            callback_calls.append((attempt, type(exception).__name__))

        @retry_with_backoff(max_attempts=3, base_delay=0.1, on_retry=on_retry)
        def failing_operation():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_operation()

        assert len(callback_calls) == 2  # Called on attempts 1 and 2, not 3 (final)
        assert callback_calls[0] == (1, "ValueError")
        assert callback_calls[1] == (2, "ValueError")

    @pytest.mark.asyncio
    async def test_async_retry_with_backoff(self):
        """Test async retry mechanism."""
        call_count = 0

        async def eventually_successful_async_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Not ready yet")
            return "async_success"

        result = await async_retry_with_backoff(
            eventually_successful_async_operation, max_attempts=3, base_delay=0.1
        )

        assert result == "async_success"
        assert call_count == 3


class TestHealthCheckers:
    """Test health checking functionality."""

    def test_health_checker_success(self):
        """Test successful health check."""

        def always_healthy():
            return True

        checker = HealthChecker(
            check_function=always_healthy,
            max_attempts=3,
            check_interval=0.1,
            timeout=5.0,
            name="test",
        )

        result = checker.wait_for_healthy()
        assert result is True

    def test_health_checker_eventually_healthy(self):
        """Test health checker that becomes healthy after attempts."""
        call_count = 0

        def eventually_healthy():
            nonlocal call_count
            call_count += 1
            return call_count >= 3

        checker = HealthChecker(
            check_function=eventually_healthy,
            max_attempts=5,
            check_interval=0.1,
            timeout=5.0,
            name="test",
        )

        result = checker.wait_for_healthy()
        assert result is True
        assert call_count >= 3

    def test_health_checker_timeout(self):
        """Test health checker timeout."""

        def never_healthy():
            return False

        checker = HealthChecker(
            check_function=never_healthy,
            max_attempts=10,
            check_interval=0.1,
            timeout=0.2,  # Very short timeout
            name="test",
        )

        with pytest.raises(ContainerTimeoutError, match="timed out"):
            checker.wait_for_healthy()

    def test_health_checker_max_attempts(self):
        """Test health checker max attempts."""

        def never_healthy():
            return False

        checker = HealthChecker(
            check_function=never_healthy,
            max_attempts=3,
            check_interval=0.1,
            timeout=10.0,  # Long timeout, should hit max_attempts first
            name="test",
        )

        with pytest.raises(ContainerHealthError, match="never became healthy"):
            checker.wait_for_healthy()

    def test_health_checker_exception_handling(self):
        """Test health checker handles exceptions properly."""
        call_count = 0

        def sometimes_throws():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Not ready")
            return True

        checker = HealthChecker(
            check_function=sometimes_throws,
            max_attempts=5,
            check_interval=0.1,
            timeout=5.0,
            name="test",
        )

        result = checker.wait_for_healthy()
        assert result is True
        assert call_count >= 3


class TestSpecializedHealthCheckers:
    """Test specialized health checkers for specific services."""

    @patch("tests.utils.testcontainer_reliability.GraphDatabase")
    def test_neo4j_health_checker_success(self, mock_graphdb):
        """Test Neo4j health checker success case."""
        # Mock successful Neo4j connection
        mock_driver = Mock()
        mock_session = Mock()
        mock_result = Mock()
        mock_record = Mock()

        mock_graphdb.driver.return_value = mock_driver
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = mock_result
        mock_result.single.return_value = mock_record
        mock_record.__getitem__.return_value = 1

        checker = Neo4jHealthChecker(max_attempts=3, check_interval=0.1)
        result = checker.wait_for_healthy("bolt://localhost:7687", "neo4j", "password")

        assert result is True
        mock_graphdb.driver.assert_called_with(
            "bolt://localhost:7687", auth=("neo4j", "password")
        )

    @patch("tests.utils.testcontainer_reliability.redis")
    def test_redis_health_checker_success(self, mock_redis_module):
        """Test Redis health checker success case."""
        # Mock successful Redis connection
        mock_client = Mock()
        mock_redis_module.from_url.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.get.return_value = b"ok"
        mock_client.set.return_value = True
        mock_client.delete.return_value = 1

        checker = RedisHealthChecker(max_attempts=3, check_interval=0.1)
        result = checker.wait_for_healthy("redis://localhost:6379/0")

        assert result is True
        mock_redis_module.from_url.assert_called_with("redis://localhost:6379/0")
        mock_client.ping.assert_called_once()


class TestContainerLogsOnFailure:
    """Test container log capture on failure."""

    def test_container_logs_captured_on_exception(self):
        """Test that container logs are captured when function raises exception."""
        mock_container = Mock()
        mock_container.get_logs.return_value = "Container log output"

        @container_logs_on_failure(mock_container)
        def failing_function():
            raise ValueError("Test failure")

        with patch("tests.utils.testcontainer_reliability.logger") as mock_logger:
            with pytest.raises(ValueError, match="Test failure"):
                failing_function()

            # Verify logs were captured
            mock_container.get_logs.assert_called_once()
            mock_logger.error.assert_called_once()
            assert "Container log output" in str(mock_logger.error.call_args)

    def test_container_logs_not_captured_on_success(self):
        """Test that container logs are not captured on successful execution."""
        mock_container = Mock()

        @container_logs_on_failure(mock_container)
        def successful_function():
            return "success"

        result = successful_function()

        assert result == "success"
        mock_container.get_logs.assert_not_called()

    def test_container_logs_handles_log_capture_failure(self):
        """Test graceful handling when log capture itself fails."""
        mock_container = Mock()
        mock_container.get_logs.side_effect = Exception("Log capture failed")

        @container_logs_on_failure(mock_container)
        def failing_function():
            raise ValueError("Test failure")

        with patch("tests.utils.testcontainer_reliability.logger") as mock_logger:
            with pytest.raises(ValueError, match="Test failure"):
                failing_function()

            # Should log warning about log capture failure
            mock_logger.warning.assert_called_once()
            assert "Failed to capture container logs" in str(
                mock_logger.warning.call_args
            )


@pytest.mark.integration
class TestEnhancedContainerIntegration:
    """Integration tests for enhanced container functionality."""

    @pytest.mark.neo4j
    def test_enhanced_neo4j_container_integration(self, enhanced_neo4j_container):
        """Test enhanced Neo4j container integration."""
        # This test requires the enhanced_neo4j_container fixture
        # and will only run with --neo4j flag

        assert "uri" in enhanced_neo4j_container
        assert "username" in enhanced_neo4j_container
        assert "password" in enhanced_neo4j_container

        # Test that we can connect to the container
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            enhanced_neo4j_container["uri"],
            auth=(
                enhanced_neo4j_container["username"],
                enhanced_neo4j_container["password"],
            ),
        )

        try:
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                assert record["test"] == 1
        finally:
            driver.close()

    @pytest.mark.redis
    def test_enhanced_redis_container_integration(self, enhanced_redis_container):
        """Test enhanced Redis container integration."""
        # This test requires the enhanced_redis_container fixture
        # and will only run with --redis flag

        import redis

        client = redis.from_url(enhanced_redis_container)

        try:
            # Test basic operations
            assert client.ping() is True

            # Test set/get operations
            client.set("test_key", "test_value")
            assert client.get("test_key").decode() == "test_value"

            # Cleanup
            client.delete("test_key")

        finally:
            client.close()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
