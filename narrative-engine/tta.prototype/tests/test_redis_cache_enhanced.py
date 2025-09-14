"""
Comprehensive unit tests for enhanced Redis caching operations.

This module contains extensive tests for Redis connection management, session caching,
cache invalidation, metrics collection, and performance optimization functionality.
"""

import json
import os
import sys
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Add the database directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from database.redis_cache_enhanced import (
        REDIS_AVAILABLE,
        CacheInvalidationManager,
        CacheMetrics,
        RedisCacheError,
        RedisConnectionManager,
        SessionCacheManager,
        create_cache_system,
        create_redis_connection,
        get_cache_invalidation_manager,
        get_session_cache_manager,
        get_tta_redis_config,
        health_check_cache_system,
    )
    REDIS_CACHE_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced Redis cache not available for testing: {e}")
    REDIS_CACHE_AVAILABLE = False

# Mock data models if not available
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
    from data_models import (
        CharacterState,
        EmotionalState,
        NarrativeContext,
        SessionState,
        TherapeuticProgress,
    )
    DATA_MODELS_AVAILABLE = True
except ImportError:
    # Create mock classes for testing
    class SessionState:
        def __init__(self, session_id, user_id):
            self.session_id = session_id
            self.user_id = user_id
            self.last_updated = datetime.now()

        def to_json(self):
            return json.dumps({
                'session_id': self.session_id,
                'user_id': self.user_id,
                'last_updated': self.last_updated.isoformat()
            })

        @classmethod
        def from_json(cls, json_str):
            data = json.loads(json_str)
            instance = cls(data['session_id'], data['user_id'])
            instance.last_updated = datetime.fromisoformat(data['last_updated'])
            return instance

    class TherapeuticProgress:
        def __init__(self, user_id):
            self.user_id = user_id

        def to_json(self):
            return json.dumps({'user_id': self.user_id})

        @classmethod
        def from_json(cls, json_str):
            data = json.loads(json_str)
            return cls(data['user_id'])

    DATA_MODELS_AVAILABLE = False


@unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Enhanced Redis cache package not available")
class TestCacheMetrics(unittest.TestCase):
    """Test cases for CacheMetrics class."""

    def setUp(self):
        """Set up test fixtures."""
        self.metrics = CacheMetrics()

    def test_metrics_initialization(self):
        """Test metrics initialization."""
        self.assertEqual(self.metrics.hits, 0)
        self.assertEqual(self.metrics.misses, 0)
        self.assertEqual(self.metrics.sets, 0)
        self.assertEqual(self.metrics.deletes, 0)
        self.assertEqual(self.metrics.errors, 0)
        self.assertEqual(self.metrics.total_response_time, 0.0)
        self.assertIsInstance(self.metrics.start_time, datetime)

    def test_record_operations(self):
        """Test recording different operations."""
        self.metrics.record_hit(0.1)
        self.metrics.record_miss(0.2)
        self.metrics.record_set(0.05)
        self.metrics.record_delete(0.03)
        self.metrics.record_error()

        self.assertEqual(self.metrics.hits, 1)
        self.assertEqual(self.metrics.misses, 1)
        self.assertEqual(self.metrics.sets, 1)
        self.assertEqual(self.metrics.deletes, 1)
        self.assertEqual(self.metrics.errors, 1)
        self.assertAlmostEqual(self.metrics.total_response_time, 0.38, places=2)

    def test_get_stats(self):
        """Test getting statistics."""
        self.metrics.record_hit(0.1)
        self.metrics.record_miss(0.2)
        self.metrics.record_set(0.05)

        stats = self.metrics.get_stats()

        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["sets"], 1)
        self.assertEqual(stats["total_operations"], 3)
        self.assertAlmostEqual(stats["hit_rate"], 1/3, places=2)
        self.assertAlmostEqual(stats["average_response_time"], 0.35/3, places=2)
        self.assertGreater(stats["uptime_seconds"], 0)

    def test_reset_metrics(self):
        """Test resetting metrics."""
        self.metrics.record_hit(0.1)
        self.metrics.record_miss(0.2)

        self.metrics.reset()

        self.assertEqual(self.metrics.hits, 0)
        self.assertEqual(self.metrics.misses, 0)
        self.assertEqual(self.metrics.total_response_time, 0.0)
        self.assertEqual(len(self.metrics.operation_counts), 0)


@unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Enhanced Redis cache package not available")
class TestEnhancedRedisConnectionManager(unittest.TestCase):
    """Test cases for enhanced RedisConnectionManager class."""

    def test_enhanced_connection_manager_creation(self):
        """Test creating enhanced connection manager with new parameters."""
        manager = RedisConnectionManager(
            host="redis.example.com",
            port=6380,
            retry_on_timeout=True,
            health_check_interval=60,
            max_connection_failures=5
        )

        self.assertEqual(manager.host, "redis.example.com")
        self.assertEqual(manager.port, 6380)
        self.assertTrue(manager.retry_on_timeout)
        self.assertEqual(manager.health_check_interval, 60)
        self.assertEqual(manager.max_connection_failures, 5)
        self.assertIsInstance(manager.metrics, CacheMetrics)

    def test_ttl_configuration(self):
        """Test TTL configuration for different data types."""
        manager = RedisConnectionManager()

        self.assertEqual(manager.get_ttl("session"), 86400)
        self.assertEqual(manager.get_ttl("character"), 7200)
        self.assertEqual(manager.get_ttl("narrative"), 1800)
        self.assertEqual(manager.get_ttl("therapeutic"), 604800)
        self.assertEqual(manager.get_ttl("unknown_type"), 3600)  # default

    @patch('database.redis_cache_enhanced.redis')
    def test_enhanced_connect_with_retry(self, mock_redis):
        """Test enhanced connection with retry configuration."""
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        manager = RedisConnectionManager(retry_on_timeout=True)
        manager.connect()

        # Verify retry_on_timeout is passed to connection pool
        mock_redis.ConnectionPool.assert_called_once()
        call_kwargs = mock_redis.ConnectionPool.call_args[1]
        self.assertTrue(call_kwargs.get('retry_on_timeout'))

    @patch('database.redis_cache_enhanced.redis')
    def test_health_check_with_interval(self, mock_redis):
        """Test health check with interval management."""
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        manager = RedisConnectionManager(health_check_interval=1)  # 1 second interval
        manager.connect()

        # First health check should ping
        self.assertTrue(manager.is_connected())
        self.assertEqual(mock_client.ping.call_count, 2)  # Once in connect, once in is_connected

        # Second immediate check should not ping (within interval)
        self.assertTrue(manager.is_connected())
        self.assertEqual(mock_client.ping.call_count, 2)  # No additional ping

        # Wait for interval to pass and check again
        time.sleep(1.1)
        self.assertTrue(manager.is_connected())
        self.assertEqual(mock_client.ping.call_count, 3)  # Additional ping after interval

    @patch('database.redis_cache_enhanced.redis')
    def test_connection_failure_handling(self, mock_redis):
        """Test connection failure handling and reconnection."""
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        manager = RedisConnectionManager(max_connection_failures=2)
        manager.connect()

        # Simulate ping failures
        mock_client.ping.side_effect = Exception("Connection lost")

        # First failure
        self.assertFalse(manager.is_connected())
        self.assertEqual(manager._connection_failures, 1)

        # Second failure should trigger reconnection attempt
        with patch.object(manager, 'reconnect') as mock_reconnect:
            mock_reconnect.return_value = None
            self.assertFalse(manager.is_connected())
            mock_reconnect.assert_called_once()

    @patch('database.redis_cache_enhanced.redis')
    def test_get_connection_stats(self, mock_redis):
        """Test getting comprehensive connection statistics."""
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        # Mock Redis info
        mock_client.info.return_value = {
            "redis_version": "6.2.0",
            "used_memory": 1024000,
            "used_memory_human": "1000K",
            "connected_clients": 5,
            "keyspace_hits": 100,
            "keyspace_misses": 20
        }

        manager = RedisConnectionManager()
        manager.connect()

        stats = manager.get_connection_stats()

        self.assertIn("connection_info", stats)
        self.assertIn("ttl_config", stats)
        self.assertIn("cache_metrics", stats)
        self.assertIn("redis_server_info", stats)

        # Check connection info
        conn_info = stats["connection_info"]
        self.assertEqual(conn_info["host"], "localhost")
        self.assertEqual(conn_info["port"], 6379)
        self.assertTrue(conn_info["connected"])

        # Check Redis server info
        server_info = stats["redis_server_info"]
        self.assertEqual(server_info["redis_version"], "6.2.0")
        self.assertEqual(server_info["used_memory"], 1024000)
        self.assertEqual(server_info["connected_clients"], 5)
        self.assertAlmostEqual(server_info["hit_rate"], 100/120, places=2)


@unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Enhanced Redis cache package not available")
class TestEnhancedSessionCacheManager(unittest.TestCase):
    """Test cases for enhanced SessionCacheManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection_manager = MagicMock()
        self.mock_redis_client = MagicMock()
        self.mock_connection_manager.get_client_context.return_value.__enter__.return_value = self.mock_redis_client
        self.mock_connection_manager.get_client_context.return_value.__exit__.return_value = None
        self.mock_connection_manager.get_ttl.return_value = 3600
        self.mock_connection_manager.metrics = CacheMetrics()

        self.cache_manager = SessionCacheManager(self.mock_connection_manager)

    def test_enhanced_key_generation(self):
        """Test enhanced key generation methods."""
        # Test session key
        session_key = self.cache_manager._generate_key("session", "session123")
        self.assertEqual(session_key, "tta:session:session123")

        # Test character key with session
        character_key = self.cache_manager._generate_key("character", "char1", "session123")
        self.assertEqual(character_key, "tta:character:session123:char1")

        # Test user sessions key
        user_sessions_key = self.cache_manager._generate_key("user_sessions", "user123")
        self.assertEqual(user_sessions_key, "tta:user:user123:sessions")

    def test_data_serialization_compression(self):
        """Test data serialization with compression."""
        # Test small data (no compression)
        small_data = {"test": "data"}
        serialized = self.cache_manager._serialize_data(small_data)
        self.assertFalse(serialized.startswith("GZIP:"))

        # Test large data (should compress if gzip available)
        large_data = {"test": "x" * 2000}  # Large enough to trigger compression
        serialized = self.cache_manager._serialize_data(large_data)
        # May or may not compress depending on gzip availability

        # Test deserialization
        deserialized = self.cache_manager._deserialize_data(serialized)
        self.assertEqual(deserialized["test"], large_data["test"])

    def test_cache_session_state_enhanced(self):
        """Test enhanced session state caching with pipeline operations."""
        session_state = SessionState("session123", "user456")

        # Mock pipeline
        mock_pipeline = MagicMock()
        self.mock_redis_client.pipeline.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [True, 1, True]

        result = self.cache_manager.cache_session_state(session_state)

        self.assertTrue(result)
        self.mock_redis_client.pipeline.assert_called_once()
        mock_pipeline.setex.assert_called_once()
        mock_pipeline.sadd.assert_called_once()
        mock_pipeline.expire.assert_called_once()
        mock_pipeline.execute.assert_called_once()

    def test_cache_multiple_sessions(self):
        """Test batch caching of multiple sessions."""
        sessions = [
            SessionState("session1", "user1"),
            SessionState("session2", "user2"),
            SessionState("session3", "user1")
        ]

        # Mock pipeline
        mock_pipeline = MagicMock()
        self.mock_redis_client.pipeline.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [True] * 9  # 3 sessions * 3 operations each

        result = self.cache_manager.cache_multiple_sessions(sessions)

        self.assertEqual(result, 3)
        self.mock_redis_client.pipeline.assert_called()
        # Should have 3 setex calls (one per session)
        self.assertEqual(mock_pipeline.setex.call_count, 3)

    def test_get_multiple_sessions(self):
        """Test batch retrieval of multiple sessions."""
        session_ids = ["session1", "session2", "session3"]

        # Mock session data
        session_data = [
            SessionState("session1", "user1").to_json(),
            SessionState("session2", "user2").to_json(),
            None  # session3 not found
        ]
        self.mock_redis_client.mget.return_value = session_data

        results = self.cache_manager.get_multiple_sessions(session_ids)

        self.assertEqual(len(results), 2)  # Only 2 sessions found
        self.assertIn("session1", results)
        self.assertIn("session2", results)
        self.assertNotIn("session3", results)

        self.mock_redis_client.mget.assert_called_once()

    def test_cache_therapeutic_progress(self):
        """Test caching therapeutic progress with long-term TTL."""
        progress = TherapeuticProgress("user123")

        # Mock long TTL for therapeutic data
        self.mock_connection_manager.get_ttl.return_value = 604800  # 1 week

        result = self.cache_manager.cache_therapeutic_progress(progress, "user123")

        self.assertTrue(result)
        self.mock_redis_client.setex.assert_called_once()

        # Verify TTL was requested for therapeutic data
        self.mock_connection_manager.get_ttl.assert_called_with("therapeutic")

    def test_get_cache_size_info(self):
        """Test getting cache size information."""
        # Mock keys for different types
        self.mock_redis_client.keys.side_effect = [
            ["tta:session:1", "tta:session:2"],  # session keys
            ["tta:character:1:a", "tta:character:2:b"],  # character keys
            ["tta:narrative:1"]  # narrative keys
        ]

        # Mock memory usage
        self.mock_redis_client.memory_usage.return_value = 1024

        size_info = self.cache_manager.get_cache_size_info()

        self.assertEqual(size_info["session_count"], 2)
        self.assertEqual(size_info["character_count"], 2)
        self.assertEqual(size_info["narrative_count"], 1)
        self.assertIn("session_avg_memory", size_info)
        self.assertIn("session_estimated_total_memory", size_info)


@unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Enhanced Redis cache package not available")
class TestEnhancedCacheInvalidationManager(unittest.TestCase):
    """Test cases for enhanced CacheInvalidationManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection_manager = MagicMock()
        self.mock_redis_client = MagicMock()
        self.mock_connection_manager.get_client_context.return_value.__enter__.return_value = self.mock_redis_client
        self.mock_connection_manager.get_client_context.return_value.__exit__.return_value = None

        self.invalidation_manager = CacheInvalidationManager(self.mock_connection_manager)

    def test_invalidate_session_with_reporting(self):
        """Test session invalidation with detailed reporting."""
        # Mock key existence and character keys
        self.mock_redis_client.exists.side_effect = [True, True]  # session and narrative exist
        self.mock_redis_client.keys.return_value = ["tta:character:session123:char1", "tta:character:session123:char2"]
        self.mock_redis_client.delete.return_value = 4

        result = self.invalidation_manager.invalidate_session("session123", cascade=True)

        self.assertEqual(result["session"], 1)
        self.assertEqual(result["narrative"], 1)
        self.assertEqual(result["character"], 2)
        self.assertEqual(result["total"], 4)

        self.mock_redis_client.delete.assert_called_once()

    def test_invalidate_user_data_with_preservation(self):
        """Test user data invalidation with therapeutic data preservation."""
        # Mock user sessions
        self.mock_redis_client.smembers.return_value = {"session1", "session2"}
        self.mock_redis_client.exists.side_effect = [True, True, True]  # emotional, user_data, therapeutic
        self.mock_redis_client.delete.return_value = 2

        # Mock session invalidation
        with patch.object(self.invalidation_manager, 'invalidate_session') as mock_invalidate:
            mock_invalidate.return_value = {"total": 3}

            result = self.invalidation_manager.invalidate_user_data("user123", preserve_therapeutic=True)

        self.assertEqual(result["sessions"], 6)  # 2 sessions * 3 keys each
        self.assertEqual(result["emotional"], 1)
        self.assertEqual(result["user_data"], 1)
        self.assertEqual(result["therapeutic"], 0)  # Preserved

        # Should have called invalidate_session for each user session
        self.assertEqual(mock_invalidate.call_count, 2)

    def test_cleanup_expired_sessions_with_stats(self):
        """Test expired session cleanup with comprehensive statistics."""
        # Mock scan results
        self.mock_redis_client.scan.side_effect = [
            (0, ["tta:session:session1", "tta:session:session2"]),  # First batch
        ]

        # Mock session data - one expired, one current
        old_session = SessionState("session1", "user1")
        old_session.last_updated = datetime.now() - timedelta(hours=25)

        current_session = SessionState("session2", "user2")
        current_session.last_updated = datetime.now() - timedelta(hours=1)

        self.mock_redis_client.get.side_effect = [
            old_session.to_json(),
            current_session.to_json()
        ]

        # Mock invalidate_session
        with patch.object(self.invalidation_manager, 'invalidate_session') as mock_invalidate:
            mock_invalidate.return_value = {"total": 3}

            result = self.invalidation_manager.cleanup_expired_sessions(max_age_hours=24, dry_run=False)

        self.assertEqual(result["sessions_processed"], 2)
        self.assertEqual(result["sessions_expired"], 1)
        self.assertEqual(result["sessions_cleaned"], 1)
        self.assertEqual(result["total_keys_deleted"], 3)
        self.assertEqual(result["errors"], 0)
        self.assertFalse(result["dry_run"])
        self.assertGreater(result["processing_time"], 0)

        # Should have called invalidate_session only for expired session
        mock_invalidate.assert_called_once_with("session1")

    def test_cleanup_expired_sessions_dry_run(self):
        """Test expired session cleanup in dry run mode."""
        # Mock scan results
        self.mock_redis_client.scan.side_effect = [
            (0, ["tta:session:session1"]),
        ]

        # Mock expired session
        old_session = SessionState("session1", "user1")
        old_session.last_updated = datetime.now() - timedelta(hours=25)
        self.mock_redis_client.get.return_value = old_session.to_json()

        result = self.invalidation_manager.cleanup_expired_sessions(max_age_hours=24, dry_run=True)

        self.assertEqual(result["sessions_processed"], 1)
        self.assertEqual(result["sessions_expired"], 1)
        self.assertEqual(result["sessions_cleaned"], 0)  # No actual cleanup in dry run
        self.assertEqual(result["total_keys_deleted"], 0)
        self.assertTrue(result["dry_run"])

    def test_cleanup_orphaned_data(self):
        """Test cleanup of orphaned cache entries."""
        # Mock session keys
        self.mock_redis_client.keys.side_effect = [
            ["tta:session:session1", "tta:session:session2"],  # Valid sessions
            ["tta:character:session1:char1", "tta:character:session3:char2"],  # One orphaned character
            ["tta:narrative:session1", "tta:narrative:session4"]  # One orphaned narrative
        ]

        self.mock_redis_client.delete.return_value = 2

        result = self.invalidation_manager.cleanup_orphaned_data(dry_run=False)

        self.assertEqual(result["orphaned_characters"], 1)
        self.assertEqual(result["orphaned_narratives"], 1)
        self.assertEqual(result["total_orphaned"], 2)
        self.assertFalse(result["dry_run"])

        # Should have deleted orphaned keys
        self.mock_redis_client.delete.assert_called_once()

    def test_get_comprehensive_cache_statistics(self):
        """Test getting comprehensive cache statistics."""
        # Mock key counts
        self.mock_redis_client.keys.side_effect = [
            ["tta:session:1", "tta:session:2"],  # 2 session keys
            ["tta:character:1:a"],  # 1 character key
            ["tta:narrative:1"],  # 1 narrative key
            [],  # 0 emotional keys
            []   # 0 therapeutic keys
        ]

        # Mock TTL sampling
        self.mock_redis_client.ttl.side_effect = [3600, 1800, 7200, 900]

        # Mock Redis info
        self.mock_redis_client.info.return_value = {
            "used_memory": 2048000,
            "used_memory_human": "2M",
            "keyspace_hits": 150,
            "keyspace_misses": 50,
            "expired_keys": 10,
            "evicted_keys": 5
        }

        stats = self.invalidation_manager.get_cache_statistics()

        self.assertEqual(stats["key_counts"]["session"], 2)
        self.assertEqual(stats["key_counts"]["character"], 1)
        self.assertEqual(stats["key_counts"]["narrative"], 1)
        self.assertEqual(stats["key_counts"]["total"], 4)

        self.assertIn("ttl_distribution", stats)
        self.assertIn("redis_info", stats)

        # Check calculated hit rate
        self.assertAlmostEqual(stats["redis_info"]["hit_rate"], 150/200, places=2)

    def test_clear_all_cache_with_confirmation(self):
        """Test clearing all cache with safety confirmation."""
        # Test without confirmation token
        result = self.invalidation_manager.clear_all_cache()
        self.assertIn("error", result)
        self.assertFalse(result["cleared"])

        # Test with correct confirmation token
        self.mock_redis_client.keys.return_value = ["tta:session:1", "tta:character:1:a", "tta:narrative:1"]
        self.mock_redis_client.delete.return_value = 3

        result = self.invalidation_manager.clear_all_cache("CONFIRM_CLEAR_ALL_CACHE")

        self.assertTrue(result["cleared"])
        self.assertEqual(result["keys_deleted"], 3)
        self.mock_redis_client.delete.assert_called_once()


@unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Enhanced Redis cache package not available")
class TestUtilityFunctions(unittest.TestCase):
    """Test cases for enhanced utility functions."""

    def test_create_cache_system(self):
        """Test creating complete cache system."""
        conn_manager, session_cache, invalidation_manager = create_cache_system(
            host="test.redis.com",
            port=6380,
            max_connections=100
        )

        self.assertIsInstance(conn_manager, RedisConnectionManager)
        self.assertIsInstance(session_cache, SessionCacheManager)
        self.assertIsInstance(invalidation_manager, CacheInvalidationManager)

        self.assertEqual(conn_manager.host, "test.redis.com")
        self.assertEqual(conn_manager.port, 6380)
        self.assertEqual(conn_manager.max_connections, 100)

    @patch('database.redis_cache_enhanced.redis')
    def test_health_check_cache_system(self, mock_redis):
        """Test comprehensive cache system health check."""
        # Setup mocks
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        # Mock Redis info for health check
        mock_client.info.return_value = {
            "redis_version": "6.2.0",
            "used_memory": 512 * 1024 * 1024,  # 512MB
            "used_memory_human": "512M",
            "connected_clients": 10,
            "keyspace_hits": 800,
            "keyspace_misses": 200
        }

        conn_manager = create_redis_connection()
        conn_manager.connect()

        # Set up good metrics
        conn_manager.metrics.record_hit(0.05)
        conn_manager.metrics.record_hit(0.03)
        conn_manager.metrics.record_miss(0.08)

        health_status = health_check_cache_system(conn_manager)

        self.assertEqual(health_status["overall_status"], "healthy")
        self.assertEqual(health_status["connection_status"], "healthy")
        self.assertEqual(health_status["performance_status"], "good")
        self.assertEqual(len(health_status["issues"]), 0)
        self.assertIn("stats", health_status)

    @patch('database.redis_cache_enhanced.redis')
    def test_health_check_with_issues(self, mock_redis):
        """Test health check with performance issues."""
        # Setup mocks
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        # Mock Redis info with issues
        mock_client.info.return_value = {
            "used_memory": 2 * 1024 * 1024 * 1024,  # 2GB (high)
            "used_memory_human": "2G",
            "connected_clients": 150,  # High
            "keyspace_hits": 100,
            "keyspace_misses": 400  # Low hit rate
        }

        conn_manager = create_redis_connection()
        conn_manager.connect()

        # Set up poor metrics
        conn_manager.metrics.record_hit(0.2)  # High response time
        conn_manager.metrics.record_miss(0.3)
        conn_manager.metrics.record_miss(0.25)
        conn_manager.metrics.record_miss(0.15)

        health_status = health_check_cache_system(conn_manager)

        self.assertIn(health_status["overall_status"], ["warning", "critical"])
        self.assertGreater(len(health_status["issues"]), 0)
        self.assertGreater(len(health_status["recommendations"]), 0)

    def test_get_tta_redis_config(self):
        """Test getting TTA-optimized Redis configuration."""
        config = get_tta_redis_config()

        self.assertEqual(config["host"], "localhost")
        self.assertEqual(config["port"], 6379)
        self.assertEqual(config["db"], 0)
        self.assertTrue(config["decode_responses"])
        self.assertTrue(config["retry_on_timeout"])
        self.assertEqual(config["health_check_interval"], 30)
        self.assertEqual(config["max_connection_failures"], 3)


@unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Enhanced Redis cache package not available")
class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complex caching scenarios."""

    @patch('database.redis_cache_enhanced.redis')
    def test_complete_session_lifecycle(self, mock_redis):
        """Test complete session lifecycle with caching."""
        # Setup mocks
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        # Create cache system
        conn_manager, session_cache, invalidation_manager = create_cache_system()
        conn_manager.connect()

        # Mock pipeline for batch operations
        mock_pipeline = MagicMock()
        mock_client.pipeline.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [True, 1, True]

        # Test session creation and caching
        session = SessionState("session123", "user456")
        result = session_cache.cache_session_state(session)
        self.assertTrue(result)

        # Test session retrieval
        mock_client.get.return_value = session.to_json()
        retrieved_session = session_cache.get_session_state("session123")
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.session_id, "session123")

        # Test session invalidation
        mock_client.exists.side_effect = [True, True]
        mock_client.keys.return_value = []
        mock_client.delete.return_value = 2

        deleted_counts = invalidation_manager.invalidate_session("session123")
        self.assertGreater(deleted_counts["total"], 0)

    @patch('database.redis_cache_enhanced.redis')
    def test_batch_operations_performance(self, mock_redis):
        """Test batch operations for performance optimization."""
        # Setup mocks
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        conn_manager, session_cache, _ = create_cache_system()
        conn_manager.connect()

        # Create multiple sessions
        sessions = [SessionState(f"session{i}", f"user{i}") for i in range(10)]

        # Mock pipeline for batch caching
        mock_pipeline = MagicMock()
        mock_client.pipeline.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [True] * 30  # 10 sessions * 3 operations each

        # Test batch caching
        cached_count = session_cache.cache_multiple_sessions(sessions)
        self.assertEqual(cached_count, 10)

        # Test batch retrieval
        session_ids = [f"session{i}" for i in range(10)]
        session_data = [sessions[i].to_json() for i in range(10)]
        mock_client.mget.return_value = session_data

        retrieved_sessions = session_cache.get_multiple_sessions(session_ids)
        self.assertEqual(len(retrieved_sessions), 10)

    @patch('database.redis_cache_enhanced.redis')
    def test_error_handling_and_recovery(self, mock_redis):
        """Test error handling and recovery mechanisms."""
        # Setup mocks
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        conn_manager, session_cache, _ = create_cache_system()
        conn_manager.connect()

        # Test Redis operation failure
        mock_client.get.side_effect = Exception("Redis operation failed")

        # Should handle error gracefully
        result = session_cache.get_session_state("session123")
        self.assertIsNone(result)

        # Metrics should record the error
        self.assertGreater(conn_manager.metrics.errors, 0)


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.INFO)

    # Run tests with detailed output
    unittest.main(verbosity=2)
