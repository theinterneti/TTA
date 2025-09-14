"""
Unit tests for Redis caching operations.

This module contains tests for Redis connection management, session caching,
and cache invalidation functionality.
"""

import json
import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Add the database directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from database.redis_cache import (
        REDIS_AVAILABLE,
        CacheInvalidationManager,
        RedisCacheError,
        RedisConnectionManager,
        SessionCacheManager,
        create_redis_connection,
        get_cache_invalidation_manager,
        get_session_cache_manager,
    )
    REDIS_CACHE_AVAILABLE = True
except ImportError as e:
    print(f"Redis cache not available for testing: {e}")
    REDIS_CACHE_AVAILABLE = False

# Mock data models if not available
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
    from data_models import (
        CharacterState,
        EmotionalState,
        NarrativeContext,
        SessionState,
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

    class CharacterState:
        def __init__(self, character_id, name):
            self.character_id = character_id
            self.name = name

    class EmotionalState:
        def __init__(self, primary_emotion="calm"):
            self.primary_emotion = primary_emotion

    class NarrativeContext:
        def __init__(self, session_id):
            self.session_id = session_id

    DATA_MODELS_AVAILABLE = False


@unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Redis cache package not available")
class TestRedisConnectionManager(unittest.TestCase):
    """Test cases for RedisConnectionManager class."""

    def test_connection_manager_creation(self):
        """Test creating connection manager with default parameters."""
        manager = RedisConnectionManager()
        self.assertEqual(manager.host, "localhost")
        self.assertEqual(manager.port, 6379)
        self.assertEqual(manager.db, 0)
        self.assertEqual(manager.default_ttl, 3600)
        self.assertEqual(manager.session_ttl, 86400)

    def test_connection_manager_custom_params(self):
        """Test creating connection manager with custom parameters."""
        manager = RedisConnectionManager(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret",
            max_connections=100
        )
        self.assertEqual(manager.host, "redis.example.com")
        self.assertEqual(manager.port, 6380)
        self.assertEqual(manager.db, 1)
        self.assertEqual(manager.password, "secret")
        self.assertEqual(manager.max_connections, 100)

    @patch('database.redis_cache.redis')
    def test_connect_success(self, mock_redis):
        """Test successful connection to Redis."""
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        manager = RedisConnectionManager()
        manager.connect()

        mock_redis.ConnectionPool.assert_called_once()
        mock_redis.Redis.assert_called_once_with(connection_pool=mock_pool)
        mock_client.ping.assert_called_once()
        self.assertEqual(manager._redis_client, mock_client)

    @patch('database.redis_cache.redis')
    def test_connect_failure(self, mock_redis):
        """Test connection failure handling."""
        from redis.exceptions import ConnectionError
        mock_redis.ConnectionPool.side_effect = ConnectionError("Connection failed")

        manager = RedisConnectionManager()

        with self.assertRaises(RedisCacheError):
            manager.connect()

    @patch('database.redis_cache.redis')
    def test_disconnect(self, mock_redis):
        """Test disconnecting from Redis."""
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        manager = RedisConnectionManager()
        manager.connect()
        manager.disconnect()

        mock_pool.disconnect.assert_called_once()
        self.assertIsNone(manager._redis_client)

    @patch('database.redis_cache.redis')
    def test_is_connected(self, mock_redis):
        """Test connection status checking."""
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        manager = RedisConnectionManager()

        # Not connected initially
        self.assertFalse(manager.is_connected())

        # Connected after connect()
        manager.connect()
        self.assertTrue(manager.is_connected())

        # Test ping failure
        mock_client.ping.side_effect = Exception("Ping failed")
        self.assertFalse(manager.is_connected())

    @patch('database.redis_cache.redis')
    def test_context_manager(self, mock_redis):
        """Test using connection manager as context manager."""
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        manager = RedisConnectionManager()

        with manager as conn_manager:
            self.assertEqual(conn_manager, manager)
            self.assertIsNotNone(conn_manager._redis_client)

        mock_pool.disconnect.assert_called_once()

    def test_get_connection_info(self):
        """Test getting connection information."""
        manager = RedisConnectionManager(host="test.redis.com", port=6380)
        info = manager.get_connection_info()

        self.assertEqual(info["host"], "test.redis.com")
        self.assertEqual(info["port"], 6380)
        self.assertEqual(info["db"], 0)
        self.assertFalse(info["connected"])  # Not connected yet


@unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Redis cache package not available")
class TestSessionCacheManager(unittest.TestCase):
    """Test cases for SessionCacheManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection_manager = MagicMock()
        self.mock_redis_client = MagicMock()
        self.mock_connection_manager.get_client.return_value = self.mock_redis_client
        self.mock_connection_manager.session_ttl = 86400
        self.mock_connection_manager.character_ttl = 7200
        self.mock_connection_manager.narrative_ttl = 1800
        self.mock_connection_manager.default_ttl = 3600

        self.cache_manager = SessionCacheManager(self.mock_connection_manager)

    def test_cache_manager_creation(self):
        """Test creating session cache manager."""
        self.assertEqual(self.cache_manager.connection_manager, self.mock_connection_manager)
        self.assertEqual(self.cache_manager.redis_client, self.mock_redis_client)
        self.assertEqual(self.cache_manager.session_prefix, "tta:session:")
        self.assertEqual(self.cache_manager.character_prefix, "tta:character:")

    def test_generate_keys(self):
        """Test key generation methods."""
        session_key = self.cache_manager._generate_session_key("session123")
        self.assertEqual(session_key, "tta:session:session123")

        character_key = self.cache_manager._generate_character_key("char1", "session123")
        self.assertEqual(character_key, "tta:character:session123:char1")

        character_key_no_session = self.cache_manager._generate_character_key("char1")
        self.assertEqual(character_key_no_session, "tta:character:char1")

        narrative_key = self.cache_manager._generate_narrative_key("session123")
        self.assertEqual(narrative_key, "tta:narrative:session123")

        emotional_key = self.cache_manager._generate_emotional_key("user123")
        self.assertEqual(emotional_key, "tta:emotional:user123")

        user_sessions_key = self.cache_manager._generate_user_sessions_key("user123")
        self.assertEqual(user_sessions_key, "tta:user:user123:sessions")

    def test_cache_session_state(self):
        """Test caching session state."""
        session_state = SessionState("session123", "user456")

        result = self.cache_manager.cache_session_state(session_state)

        self.assertTrue(result)
        self.mock_redis_client.setex.assert_called_once()
        self.mock_redis_client.sadd.assert_called_once()
        self.mock_redis_client.expire.assert_called_once()

        # Check the setex call
        setex_call = self.mock_redis_client.setex.call_args
        self.assertEqual(setex_call[0][0], "tta:session:session123")  # key
        self.assertEqual(setex_call[0][1], 86400)  # ttl
        # Third argument is JSON data

    def test_get_session_state(self):
        """Test retrieving session state."""
        # Mock Redis response
        session_data = SessionState("session123", "user456").to_json()
        self.mock_redis_client.get.return_value = session_data

        result = self.cache_manager.get_session_state("session123")

        self.assertIsNotNone(result)
        self.assertEqual(result.session_id, "session123")
        self.assertEqual(result.user_id, "user456")
        self.mock_redis_client.get.assert_called_once_with("tta:session:session123")

    def test_get_session_state_not_found(self):
        """Test retrieving non-existent session state."""
        self.mock_redis_client.get.return_value = None

        result = self.cache_manager.get_session_state("nonexistent")

        self.assertIsNone(result)

    def test_cache_character_state(self):
        """Test caching character state."""
        character_state = CharacterState("char1", "Alice")

        result = self.cache_manager.cache_character_state(character_state, "session123")

        self.assertTrue(result)
        self.mock_redis_client.setex.assert_called_once()

        # Check the setex call
        setex_call = self.mock_redis_client.setex.call_args
        self.assertEqual(setex_call[0][0], "tta:character:session123:char1")  # key
        self.assertEqual(setex_call[0][1], 7200)  # ttl

    def test_get_user_sessions(self):
        """Test getting user sessions."""
        self.mock_redis_client.smembers.return_value = {"session1", "session2", "session3"}

        sessions = self.cache_manager.get_user_sessions("user123")

        self.assertEqual(len(sessions), 3)
        self.assertIn("session1", sessions)
        self.mock_redis_client.smembers.assert_called_once_with("tta:user:user123:sessions")

    def test_update_session_timestamp(self):
        """Test updating session timestamp."""
        self.mock_redis_client.exists.return_value = True
        self.mock_redis_client.ttl.return_value = 3600

        result = self.cache_manager.update_session_timestamp("session123")

        self.assertTrue(result)
        self.mock_redis_client.expire.assert_called_once_with("tta:session:session123", 3600)

    def test_update_session_timestamp_not_found(self):
        """Test updating timestamp for non-existent session."""
        self.mock_redis_client.exists.return_value = False

        result = self.cache_manager.update_session_timestamp("nonexistent")

        self.assertFalse(result)


@unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Redis cache package not available")
class TestCacheInvalidationManager(unittest.TestCase):
    """Test cases for CacheInvalidationManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection_manager = MagicMock()
        self.mock_redis_client = MagicMock()
        self.mock_connection_manager.get_client.return_value = self.mock_redis_client

        self.invalidation_manager = CacheInvalidationManager(self.mock_connection_manager)

    def test_invalidation_manager_creation(self):
        """Test creating cache invalidation manager."""
        self.assertEqual(self.invalidation_manager.connection_manager, self.mock_connection_manager)
        self.assertEqual(self.invalidation_manager.redis_client, self.mock_redis_client)
        self.assertEqual(self.invalidation_manager.session_pattern, "tta:session:*")

    def test_invalidate_session(self):
        """Test invalidating session cache."""
        # Mock character keys for the session
        self.mock_redis_client.keys.return_value = [
            "tta:character:session123:char1",
            "tta:character:session123:char2"
        ]
        self.mock_redis_client.delete.return_value = 4  # 4 keys deleted

        result = self.invalidation_manager.invalidate_session("session123")

        self.assertTrue(result)
        self.mock_redis_client.keys.assert_called_once_with("tta:character:session123:*")
        self.mock_redis_client.delete.assert_called_once()

        # Check that all expected keys were included in delete call
        delete_call = self.mock_redis_client.delete.call_args[0]
        expected_keys = [
            "tta:session:session123",
            "tta:narrative:session123",
            "tta:character:session123:char1",
            "tta:character:session123:char2"
        ]
        for key in expected_keys:
            self.assertIn(key, delete_call)

    def test_invalidate_user_data(self):
        """Test invalidating user cache data."""
        # Mock user sessions
        self.mock_redis_client.smembers.return_value = {"session1", "session2"}
        self.mock_redis_client.keys.return_value = []  # No character keys
        self.mock_redis_client.delete.return_value = 2

        result = self.invalidation_manager.invalidate_user_data("user123")

        self.assertTrue(result)
        # Should call smembers to get user sessions
        self.mock_redis_client.smembers.assert_called_once_with("tta:user:user123:sessions")
        # Should call delete for emotional and user sessions keys
        self.mock_redis_client.delete.assert_called()

    def test_invalidate_character(self):
        """Test invalidating character cache."""
        # Test with specific session
        self.mock_redis_client.delete.return_value = 1

        result = self.invalidation_manager.invalidate_character("char1", "session123")

        self.assertTrue(result)
        self.mock_redis_client.delete.assert_called_once_with("tta:character:session123:char1")

    def test_invalidate_character_all_sessions(self):
        """Test invalidating character cache for all sessions."""
        # Mock character keys across sessions
        self.mock_redis_client.keys.return_value = [
            "tta:character:session1:char1",
            "tta:character:session2:char1"
        ]
        self.mock_redis_client.delete.return_value = 2

        result = self.invalidation_manager.invalidate_character("char1")

        self.assertTrue(result)
        self.mock_redis_client.keys.assert_called_once_with("tta:character:*:char1")
        self.mock_redis_client.delete.assert_called_once()

    def test_cleanup_expired_sessions(self):
        """Test cleaning up expired sessions."""
        # Mock session keys
        self.mock_redis_client.keys.return_value = [
            "tta:session:session1",
            "tta:session:session2"
        ]

        # Mock old session data
        old_session = SessionState("session1", "user1")
        old_session.last_updated = datetime.now() - timedelta(hours=25)  # Older than 24 hours

        recent_session = SessionState("session2", "user2")
        recent_session.last_updated = datetime.now() - timedelta(hours=1)  # Recent

        self.mock_redis_client.get.side_effect = [
            old_session.to_json(),
            recent_session.to_json()
        ]

        # Mock the invalidate_session method
        with patch.object(self.invalidation_manager, 'invalidate_session') as mock_invalidate:
            result = self.invalidation_manager.cleanup_expired_sessions(max_age_hours=24)

        self.assertEqual(result, 1)  # Only one session should be cleaned up
        mock_invalidate.assert_called_once_with("session1")

    def test_get_cache_statistics(self):
        """Test getting cache statistics."""
        # Mock key counts
        self.mock_redis_client.keys.side_effect = [
            ["session1", "session2"],  # session keys
            ["char1", "char2", "char3"],  # character keys
            ["narrative1"],  # narrative keys
            ["emotional1", "emotional2"],  # emotional keys
            ["user1"]  # user keys
        ]

        # Mock Redis info
        self.mock_redis_client.info.return_value = {
            "used_memory": 1024000,
            "connected_clients": 5
        }

        stats = self.invalidation_manager.get_cache_statistics()

        self.assertEqual(stats["session_keys"], 2)
        self.assertEqual(stats["character_keys"], 3)
        self.assertEqual(stats["narrative_keys"], 1)
        self.assertEqual(stats["emotional_keys"], 2)
        self.assertEqual(stats["user_keys"], 1)
        self.assertEqual(stats["total_keys"], 9)
        self.assertEqual(stats["memory_usage"], 1024000)
        self.assertEqual(stats["connected_clients"], 5)

    def test_clear_all_cache(self):
        """Test clearing all cache entries."""
        # Mock keys for each pattern
        self.mock_redis_client.keys.side_effect = [
            ["session1", "session2"],
            ["char1", "char2"],
            ["narrative1"],
            ["emotional1"],
            ["user1"]
        ]
        self.mock_redis_client.delete.side_effect = [2, 2, 1, 1, 1]  # Return counts for each delete

        result = self.invalidation_manager.clear_all_cache()

        self.assertTrue(result)
        # Should call keys for each pattern
        self.assertEqual(self.mock_redis_client.keys.call_count, 5)
        # Should call delete for each non-empty key set
        self.assertEqual(self.mock_redis_client.delete.call_count, 5)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    @unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Redis cache package not available")
    def test_create_redis_connection(self):
        """Test creating Redis connection manager."""
        manager = create_redis_connection(host="test.redis.com", port=6380)
        self.assertIsInstance(manager, RedisConnectionManager)
        self.assertEqual(manager.host, "test.redis.com")
        self.assertEqual(manager.port, 6380)

    @unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Redis cache package not available")
    def test_get_session_cache_manager(self):
        """Test creating session cache manager."""
        mock_connection_manager = MagicMock()
        manager = get_session_cache_manager(mock_connection_manager)
        self.assertIsInstance(manager, SessionCacheManager)
        self.assertEqual(manager.connection_manager, mock_connection_manager)

    @unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Redis cache package not available")
    def test_get_cache_invalidation_manager(self):
        """Test creating cache invalidation manager."""
        mock_connection_manager = MagicMock()
        manager = get_cache_invalidation_manager(mock_connection_manager)
        self.assertIsInstance(manager, CacheInvalidationManager)
        self.assertEqual(manager.connection_manager, mock_connection_manager)


class TestRedisIntegration(unittest.TestCase):
    """Integration tests for Redis cache functionality."""

    @unittest.skipUnless(REDIS_CACHE_AVAILABLE, "Redis cache package not available")
    @patch('database.redis_cache.redis')
    def test_full_session_workflow(self, mock_redis):
        """Test complete session caching workflow."""
        # Setup mocks
        mock_pool = MagicMock()
        mock_client = MagicMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client

        # Create managers
        with create_redis_connection() as conn_manager:
            session_cache = get_session_cache_manager(conn_manager)
            invalidation_manager = get_cache_invalidation_manager(conn_manager)

            # Test session caching
            session_state = SessionState("session123", "user456")
            result = session_cache.cache_session_state(session_state)
            self.assertTrue(result)

            # Test session retrieval
            mock_client.get.return_value = session_state.to_json()
            retrieved_session = session_cache.get_session_state("session123")
            self.assertIsNotNone(retrieved_session)
            self.assertEqual(retrieved_session.session_id, "session123")

            # Test session invalidation
            mock_client.keys.return_value = []
            mock_client.delete.return_value = 2
            result = invalidation_manager.invalidate_session("session123")
            self.assertTrue(result)


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.INFO)

    # Run tests
    unittest.main(verbosity=2)
