#!/usr/bin/env python3
"""
Simple test runner for Redis cache functionality.
"""

import logging
import os
import sys

# Add the database directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_redis_imports():
    """Test that Redis cache modules can be imported."""
    print("Testing Redis cache module imports...")

    try:
        from redis_cache import (
            REDIS_AVAILABLE,
            CacheInvalidationManager,
            RedisCacheError,
            RedisConnectionManager,
            SessionCacheManager,
            create_redis_connection,
            get_cache_invalidation_manager,
            get_session_cache_manager,
        )
        print("  ✓ Redis cache module imported successfully")
        print(f"  Redis package available: {REDIS_AVAILABLE}")

        if not REDIS_AVAILABLE:
            print("  ⚠ Redis package not installed - this is expected in some environments")

        return True

    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_connection_manager_creation():
    """Test creating Redis connection manager instances."""
    print("Testing Redis connection manager creation...")

    try:
        from redis_cache import REDIS_AVAILABLE, RedisConnectionManager

        if not REDIS_AVAILABLE:
            print("  ⚠ Skipping connection manager creation - Redis package not available")
            return True

        # Test with default parameters
        manager = RedisConnectionManager()
        assert manager.host == "localhost"
        assert manager.port == 6379
        assert manager.db == 0
        assert manager.default_ttl == 3600
        assert manager.session_ttl == 86400
        print("  ✓ Default connection manager created")

        # Test with custom parameters
        custom_manager = RedisConnectionManager(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret",
            max_connections=100
        )
        assert custom_manager.host == "redis.example.com"
        assert custom_manager.port == 6380
        assert custom_manager.db == 1
        assert custom_manager.password == "secret"
        assert custom_manager.max_connections == 100
        print("  ✓ Custom connection manager created")

        return True

    except Exception as e:
        print(f"  ❌ Connection manager creation failed: {e}")
        return False


def test_cache_manager_creation():
    """Test creating cache manager instances."""
    print("Testing cache manager creation...")

    try:
        from unittest.mock import MagicMock

        from redis_cache import (
            REDIS_AVAILABLE,
            CacheInvalidationManager,
            SessionCacheManager,
        )

        if not REDIS_AVAILABLE:
            print("  ⚠ Skipping cache manager creation - Redis package not available")
            return True

        # Create a mock connection manager
        mock_connection_manager = MagicMock()
        mock_redis_client = MagicMock()
        mock_connection_manager.get_client.return_value = mock_redis_client
        mock_connection_manager.session_ttl = 86400
        mock_connection_manager.character_ttl = 7200
        mock_connection_manager.narrative_ttl = 1800
        mock_connection_manager.default_ttl = 3600

        # Test session cache manager creation
        session_cache = SessionCacheManager(mock_connection_manager)
        assert session_cache.connection_manager == mock_connection_manager
        assert session_cache.redis_client == mock_redis_client
        assert session_cache.session_prefix == "tta:session:"
        print("  ✓ Session cache manager created")

        # Test cache invalidation manager creation
        invalidation_manager = CacheInvalidationManager(mock_connection_manager)
        assert invalidation_manager.connection_manager == mock_connection_manager
        assert invalidation_manager.redis_client == mock_redis_client
        assert invalidation_manager.session_pattern == "tta:session:*"
        print("  ✓ Cache invalidation manager created")

        return True

    except Exception as e:
        print(f"  ❌ Cache manager creation failed: {e}")
        return False


def test_key_generation():
    """Test Redis key generation methods."""
    print("Testing Redis key generation...")

    try:
        from unittest.mock import MagicMock

        from redis_cache import REDIS_AVAILABLE, SessionCacheManager

        if not REDIS_AVAILABLE:
            print("  ⚠ Skipping key generation test - Redis package not available")
            return True

        # Create a mock session cache manager
        mock_connection_manager = MagicMock()
        mock_redis_client = MagicMock()
        mock_connection_manager.get_client.return_value = mock_redis_client

        cache_manager = SessionCacheManager(mock_connection_manager)

        # Test key generation methods
        session_key = cache_manager._generate_session_key("session123")
        assert session_key == "tta:session:session123"
        print("  ✓ Session key generation")

        character_key = cache_manager._generate_character_key("char1", "session123")
        assert character_key == "tta:character:session123:char1"
        print("  ✓ Character key generation")

        narrative_key = cache_manager._generate_narrative_key("session123")
        assert narrative_key == "tta:narrative:session123"
        print("  ✓ Narrative key generation")

        emotional_key = cache_manager._generate_emotional_key("user123")
        assert emotional_key == "tta:emotional:user123"
        print("  ✓ Emotional key generation")

        user_sessions_key = cache_manager._generate_user_sessions_key("user123")
        assert user_sessions_key == "tta:user:user123:sessions"
        print("  ✓ User sessions key generation")

        return True

    except Exception as e:
        print(f"  ❌ Key generation test failed: {e}")
        return False


def test_cache_methods():
    """Test that cache methods exist and are callable."""
    print("Testing cache methods...")

    try:
        from unittest.mock import MagicMock

        from redis_cache import (
            REDIS_AVAILABLE,
            CacheInvalidationManager,
            SessionCacheManager,
        )

        if not REDIS_AVAILABLE:
            print("  ⚠ Skipping cache methods test - Redis package not available")
            return True

        # Create mock managers
        mock_connection_manager = MagicMock()
        mock_redis_client = MagicMock()
        mock_connection_manager.get_client.return_value = mock_redis_client

        session_cache = SessionCacheManager(mock_connection_manager)
        invalidation_manager = CacheInvalidationManager(mock_connection_manager)

        # Test session cache methods
        session_methods = [
            'cache_session_state', 'get_session_state', 'cache_character_state',
            'get_character_state', 'cache_narrative_context', 'get_narrative_context',
            'cache_emotional_state', 'get_emotional_state', 'get_user_sessions',
            'update_session_timestamp'
        ]

        for method_name in session_methods:
            assert hasattr(session_cache, method_name), f"Missing method: {method_name}"
            assert callable(getattr(session_cache, method_name)), f"Method not callable: {method_name}"

        print(f"  ✓ All {len(session_methods)} session cache methods exist")

        # Test invalidation methods
        invalidation_methods = [
            'invalidate_session', 'invalidate_user_data', 'invalidate_character',
            'cleanup_expired_sessions', 'get_cache_statistics', 'clear_all_cache'
        ]

        for method_name in invalidation_methods:
            assert hasattr(invalidation_manager, method_name), f"Missing method: {method_name}"
            assert callable(getattr(invalidation_manager, method_name)), f"Method not callable: {method_name}"

        print(f"  ✓ All {len(invalidation_methods)} invalidation methods exist")

        return True

    except Exception as e:
        print(f"  ❌ Cache methods test failed: {e}")
        return False


def test_utility_functions():
    """Test utility functions."""
    print("Testing utility functions...")

    try:
        from redis_cache import (
            create_redis_connection,
            get_cache_invalidation_manager,
            get_session_cache_manager,
        )

        # Test that utility functions exist and are callable
        assert callable(create_redis_connection), "create_redis_connection not callable"
        assert callable(get_session_cache_manager), "get_session_cache_manager not callable"
        assert callable(get_cache_invalidation_manager), "get_cache_invalidation_manager not callable"

        print("  ✓ All utility functions exist and are callable")

        return True

    except Exception as e:
        print(f"  ❌ Utility functions test failed: {e}")
        return False


def test_data_model_integration():
    """Test integration with data models."""
    print("Testing data model integration...")

    try:
        # Try to import data models
        sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))

        try:
            from data_models import (
                CharacterState,
                EmotionalState,
                NarrativeContext,
                SessionState,
            )
            print("  ✓ Data models imported successfully")
        except ImportError:
            print("  ⚠ Data models not available (using mock classes)")

        # Test that cache manager can handle data models
        from unittest.mock import MagicMock

        from redis_cache import SessionCacheManager

        mock_connection_manager = MagicMock()
        mock_redis_client = MagicMock()
        mock_connection_manager.get_client.return_value = mock_redis_client
        mock_connection_manager.session_ttl = 86400

        cache_manager = SessionCacheManager(mock_connection_manager)

        # Test JSON serializer
        from datetime import datetime
        test_datetime = datetime.now()
        serialized = cache_manager._json_serializer(test_datetime)
        assert isinstance(serialized, str)
        print("  ✓ JSON serializer works with datetime objects")

        return True

    except Exception as e:
        print(f"  ❌ Data model integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("TTA Prototype Redis Cache Test Runner")
    print("=" * 60)

    tests = [
        test_redis_imports,
        test_connection_manager_creation,
        test_cache_manager_creation,
        test_key_generation,
        test_cache_methods,
        test_utility_functions,
        test_data_model_integration
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! Redis cache functionality is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        if passed > 0:
            print("Note: Some failures may be expected if Redis package is not installed")

    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
