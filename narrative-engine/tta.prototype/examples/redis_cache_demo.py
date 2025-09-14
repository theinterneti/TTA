#!/usr/bin/env python3
"""
Redis Cache Enhanced Demo

This script demonstrates the enhanced Redis caching layer functionality
for the TTA prototype therapeutic text adventure system.

Features demonstrated:
- Enhanced connection management with health monitoring
- Advanced session caching with compression and batch operations
- Comprehensive cache invalidation and cleanup
- Performance metrics and monitoring
- Error handling and recovery mechanisms

Usage:
    python3 redis_cache_demo.py [--with-redis]

    --with-redis: Attempt to connect to actual Redis server (requires redis package)
"""

import argparse
import os
import sys
import time
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Mock Redis if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    print("Redis package not available. Running in mock mode.")
    REDIS_AVAILABLE = False

    # Create mock redis module
    class MockRedis:
        def __init__(self, *args, **kwargs):
            self.data = {}
            self.sets = {}

        def ping(self):
            return True

        def get(self, key):
            return self.data.get(key)

        def set(self, key, value):
            self.data[key] = value
            return True

        def setex(self, key, ttl, value):
            self.data[key] = value
            return True

        def delete(self, *keys):
            count = 0
            for key in keys:
                if key in self.data:
                    del self.data[key]
                    count += 1
            return count

        def keys(self, pattern):
            import fnmatch
            return [k for k in self.data.keys() if fnmatch.fnmatch(k, pattern)]

        def exists(self, key):
            return key in self.data

        def sadd(self, key, *values):
            if key not in self.sets:
                self.sets[key] = set()
            for value in values:
                self.sets[key].add(value)
            return len(values)

        def smembers(self, key):
            return self.sets.get(key, set())

        def expire(self, key, ttl):
            return True

        def ttl(self, key):
            return 3600  # Mock TTL

        def info(self):
            return {
                "redis_version": "mock-6.2.0",
                "used_memory": 1024000,
                "used_memory_human": "1000K",
                "connected_clients": 1,
                "keyspace_hits": 100,
                "keyspace_misses": 20,
                "total_commands_processed": 1000,
                "uptime_in_seconds": 3600,
                "role": "master"
            }

        def pipeline(self):
            return MockPipeline(self)

        def mget(self, keys):
            return [self.data.get(key) for key in keys]

        def scan(self, cursor, match=None, count=None):
            keys = list(self.data.keys())
            if match:
                import fnmatch
                keys = [k for k in keys if fnmatch.fnmatch(k, match)]
            return (0, keys)

        def memory_usage(self, key):
            return 1024  # Mock memory usage

    class MockPipeline:
        def __init__(self, redis_client):
            self.redis_client = redis_client
            self.commands = []

        def setex(self, key, ttl, value):
            self.commands.append(('setex', key, ttl, value))
            return self

        def sadd(self, key, *values):
            self.commands.append(('sadd', key, values))
            return self

        def expire(self, key, ttl):
            self.commands.append(('expire', key, ttl))
            return self

        def execute(self):
            results = []
            for cmd in self.commands:
                if cmd[0] == 'setex':
                    results.append(self.redis_client.setex(cmd[1], cmd[2], cmd[3]))
                elif cmd[0] == 'sadd':
                    results.append(self.redis_client.sadd(cmd[1], *cmd[2]))
                elif cmd[0] == 'expire':
                    results.append(self.redis_client.expire(cmd[1], cmd[2]))
            self.commands = []
            return results

    class MockConnectionPool:
        def __init__(self, *args, **kwargs):
            pass

        def disconnect(self):
            pass

    # Mock the redis module
    sys.modules['redis'] = type('MockRedisModule', (), {
        'Redis': MockRedis,
        'ConnectionPool': MockConnectionPool,
        'exceptions': type('MockExceptions', (), {
            'ConnectionError': Exception,
            'TimeoutError': Exception,
            'RedisError': Exception
        })()
    })()

# Mock data models
class MockSessionState:
    def __init__(self, session_id, user_id):
        self.session_id = session_id
        self.user_id = user_id
        self.last_updated = datetime.now()
        self.current_scenario_id = f"scenario_{session_id}"
        self.narrative_position = 0

    def to_json(self):
        import json
        return json.dumps({
            'session_id': self.session_id,
            'user_id': self.user_id,
            'last_updated': self.last_updated.isoformat(),
            'current_scenario_id': self.current_scenario_id,
            'narrative_position': self.narrative_position
        })

    @classmethod
    def from_json(cls, json_str):
        import json
        data = json.loads(json_str)
        instance = cls(data['session_id'], data['user_id'])
        instance.last_updated = datetime.fromisoformat(data['last_updated'])
        instance.current_scenario_id = data.get('current_scenario_id', '')
        instance.narrative_position = data.get('narrative_position', 0)
        return instance

class MockTherapeuticProgress:
    def __init__(self, user_id):
        self.user_id = user_id
        self.overall_progress_score = 0.0
        self.therapeutic_goals = []

    def to_json(self):
        import json
        return json.dumps({
            'user_id': self.user_id,
            'overall_progress_score': self.overall_progress_score,
            'therapeutic_goals': self.therapeutic_goals
        })

    @classmethod
    def from_json(cls, json_str):
        import json
        data = json.loads(json_str)
        instance = cls(data['user_id'])
        instance.overall_progress_score = data.get('overall_progress_score', 0.0)
        instance.therapeutic_goals = data.get('therapeutic_goals', [])
        return instance

# Patch the data models
sys.modules['data_models'] = type('MockDataModels', (), {
    'SessionState': MockSessionState,
    'TherapeuticProgress': MockTherapeuticProgress,
    'CharacterState': None,
    'EmotionalState': None,
    'NarrativeContext': None
})()

# Now import our enhanced cache modules
try:
    from database.redis_cache_enhanced import (
        CacheMetrics,
        create_cache_system,
        get_tta_redis_config,
        health_check_cache_system,
    )
    CACHE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced cache modules not available: {e}")
    CACHE_MODULES_AVAILABLE = False


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subsection(title):
    """Print a formatted subsection header."""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def demonstrate_connection_management():
    """Demonstrate enhanced connection management features."""
    print_section("Enhanced Connection Management")

    # Get TTA-optimized configuration
    config = get_tta_redis_config()
    print("TTA Redis Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")

    # Create connection manager
    print("\nCreating Redis connection manager...")
    conn_manager, session_cache, invalidation_manager = create_cache_system(**config)

    # Connect to Redis
    print("Connecting to Redis...")
    try:
        conn_manager.connect()
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None, None, None

    # Get connection statistics
    print("\nConnection Statistics:")
    stats = conn_manager.get_connection_stats()

    conn_info = stats.get("connection_info", {})
    print(f"  Host: {conn_info.get('host', 'unknown')}")
    print(f"  Port: {conn_info.get('port', 'unknown')}")
    print(f"  Connected: {conn_info.get('connected', False)}")
    print(f"  Max Connections: {conn_info.get('max_connections', 'unknown')}")

    redis_info = stats.get("redis_server_info", {})
    if redis_info:
        print(f"  Redis Version: {redis_info.get('redis_version', 'unknown')}")
        print(f"  Memory Usage: {redis_info.get('used_memory_human', 'unknown')}")
        print(f"  Connected Clients: {redis_info.get('connected_clients', 'unknown')}")
        print(f"  Hit Rate: {redis_info.get('hit_rate', 0):.2%}")

    return conn_manager, session_cache, invalidation_manager


def demonstrate_session_caching(session_cache, conn_manager):
    """Demonstrate enhanced session caching features."""
    print_section("Enhanced Session Caching")

    # Create sample sessions
    sessions = [
        MockSessionState(f"session_{i}", f"user_{i % 3}")
        for i in range(1, 11)
    ]

    print(f"Created {len(sessions)} sample sessions")

    # Single session caching
    print_subsection("Single Session Caching")
    session = sessions[0]
    print(f"Caching session: {session.session_id} for user: {session.user_id}")

    start_time = time.time()
    result = session_cache.cache_session_state(session)
    cache_time = time.time() - start_time

    print(f"✓ Cached successfully: {result} (took {cache_time:.3f}s)")

    # Retrieve session
    print(f"Retrieving session: {session.session_id}")
    start_time = time.time()
    retrieved_session = session_cache.get_session_state(session.session_id)
    retrieve_time = time.time() - start_time

    if retrieved_session:
        print(f"✓ Retrieved successfully (took {retrieve_time:.3f}s)")
        print(f"  Session ID: {retrieved_session.session_id}")
        print(f"  User ID: {retrieved_session.user_id}")
        print(f"  Last Updated: {retrieved_session.last_updated}")
    else:
        print("✗ Failed to retrieve session")

    # Batch session caching
    print_subsection("Batch Session Caching")
    print(f"Caching {len(sessions)} sessions in batch...")

    start_time = time.time()
    cached_count = session_cache.cache_multiple_sessions(sessions)
    batch_cache_time = time.time() - start_time

    print(f"✓ Cached {cached_count} sessions (took {batch_cache_time:.3f}s)")
    print(f"  Average time per session: {batch_cache_time/len(sessions):.3f}s")

    # Batch session retrieval
    session_ids = [s.session_id for s in sessions[:5]]
    print(f"Retrieving {len(session_ids)} sessions in batch...")

    start_time = time.time()
    retrieved_sessions = session_cache.get_multiple_sessions(session_ids)
    batch_retrieve_time = time.time() - start_time

    print(f"✓ Retrieved {len(retrieved_sessions)} sessions (took {batch_retrieve_time:.3f}s)")

    # Therapeutic progress caching
    print_subsection("Therapeutic Progress Caching")
    progress = MockTherapeuticProgress("user_1")
    progress.overall_progress_score = 75.5

    print(f"Caching therapeutic progress for user: {progress.user_id}")
    result = session_cache.cache_therapeutic_progress(progress, progress.user_id)
    print(f"✓ Cached therapeutic progress: {result}")

    retrieved_progress = session_cache.get_therapeutic_progress(progress.user_id)
    if retrieved_progress:
        print("✓ Retrieved therapeutic progress")
        print(f"  User ID: {retrieved_progress.user_id}")
        print(f"  Progress Score: {retrieved_progress.overall_progress_score}")

    # Cache size information
    print_subsection("Cache Size Information")
    size_info = session_cache.get_cache_size_info()
    if size_info:
        print("Cache size breakdown:")
        for key, value in size_info.items():
            if isinstance(value, int | float):
                if 'memory' in key.lower():
                    print(f"  {key}: {value:,.0f} bytes")
                else:
                    print(f"  {key}: {value}")

    # Performance metrics
    print_subsection("Performance Metrics")
    metrics = conn_manager.metrics.get_stats()
    print("Cache performance metrics:")
    print(f"  Total Operations: {metrics.get('total_operations', 0)}")
    print(f"  Cache Hits: {metrics.get('hits', 0)}")
    print(f"  Cache Misses: {metrics.get('misses', 0)}")
    print(f"  Hit Rate: {metrics.get('hit_rate', 0):.2%}")
    print(f"  Average Response Time: {metrics.get('average_response_time', 0):.3f}s")
    print(f"  Operations/Second: {metrics.get('operations_per_second', 0):.1f}")


def demonstrate_cache_invalidation(invalidation_manager):
    """Demonstrate enhanced cache invalidation features."""
    print_section("Enhanced Cache Invalidation")

    # Session invalidation
    print_subsection("Session Invalidation")
    session_id = "session_1"
    print(f"Invalidating session: {session_id}")

    deleted_counts = invalidation_manager.invalidate_session(session_id, cascade=True)
    print("Invalidation results:")
    for key, count in deleted_counts.items():
        print(f"  {key}: {count} keys deleted")

    # User data invalidation
    print_subsection("User Data Invalidation")
    user_id = "user_1"
    print(f"Invalidating all data for user: {user_id}")

    deleted_counts = invalidation_manager.invalidate_user_data(user_id, preserve_therapeutic=True)
    print("User data invalidation results:")
    for key, count in deleted_counts.items():
        print(f"  {key}: {count} keys deleted")

    # Cache statistics
    print_subsection("Cache Statistics")
    stats = invalidation_manager.get_cache_statistics()

    if "key_counts" in stats:
        print("Key counts by type:")
        for key_type, count in stats["key_counts"].items():
            print(f"  {key_type}: {count}")

    if "redis_info" in stats:
        redis_info = stats["redis_info"]
        print("\nRedis server statistics:")
        print(f"  Memory Usage: {redis_info.get('used_memory_human', 'unknown')}")
        print(f"  Hit Rate: {redis_info.get('hit_rate', 0):.2%}")
        print(f"  Expired Keys: {redis_info.get('expired_keys', 0)}")
        print(f"  Evicted Keys: {redis_info.get('evicted_keys', 0)}")

    # Cleanup operations
    print_subsection("Cleanup Operations")

    # Dry run cleanup
    print("Performing dry run cleanup of expired sessions...")
    cleanup_stats = invalidation_manager.cleanup_expired_sessions(max_age_hours=1, dry_run=True)

    print("Cleanup statistics (dry run):")
    for key, value in cleanup_stats.items():
        if isinstance(value, bool):
            print(f"  {key}: {value}")
        elif isinstance(value, int | float):
            if 'time' in key.lower():
                print(f"  {key}: {value:.3f}s")
            else:
                print(f"  {key}: {value}")

    # Orphaned data cleanup
    print("\nCleaning up orphaned data...")
    orphaned_stats = invalidation_manager.cleanup_orphaned_data(dry_run=True)

    print("Orphaned data cleanup (dry run):")
    for key, value in orphaned_stats.items():
        print(f"  {key}: {value}")


def demonstrate_health_monitoring(conn_manager):
    """Demonstrate health monitoring and diagnostics."""
    print_section("Health Monitoring & Diagnostics")

    # Comprehensive health check
    print("Performing comprehensive health check...")
    health_status = health_check_cache_system(conn_manager)

    print(f"Overall Status: {health_status['overall_status'].upper()}")
    print(f"Connection Status: {health_status['connection_status'].upper()}")
    print(f"Performance Status: {health_status['performance_status'].upper()}")

    if health_status.get("issues"):
        print("\nIssues detected:")
        for issue in health_status["issues"]:
            print(f"  ⚠ {issue}")

    if health_status.get("recommendations"):
        print("\nRecommendations:")
        for rec in health_status["recommendations"]:
            print(f"  💡 {rec}")

    # Detailed statistics
    if "stats" in health_status:
        stats = health_status["stats"]

        print_subsection("Detailed Statistics")

        # Cache metrics
        cache_metrics = stats.get("cache_metrics", {})
        if cache_metrics:
            print("Cache Performance:")
            print(f"  Uptime: {cache_metrics.get('uptime_seconds', 0):.0f} seconds")
            print(f"  Total Operations: {cache_metrics.get('total_operations', 0)}")
            print(f"  Hit Rate: {cache_metrics.get('hit_rate', 0):.2%}")
            print(f"  Average Response Time: {cache_metrics.get('average_response_time', 0):.3f}s")
            print(f"  Operations/Second: {cache_metrics.get('operations_per_second', 0):.1f}")

        # Redis server info
        redis_info = stats.get("redis_server_info", {})
        if redis_info:
            print("\nRedis Server:")
            print(f"  Version: {redis_info.get('redis_version', 'unknown')}")
            print(f"  Memory Usage: {redis_info.get('used_memory_human', 'unknown')}")
            print(f"  Connected Clients: {redis_info.get('connected_clients', 0)}")
            print(f"  Commands Processed: {redis_info.get('total_commands_processed', 0):,}")
            print(f"  Uptime: {redis_info.get('uptime_in_seconds', 0):,} seconds")


def demonstrate_error_handling(conn_manager, session_cache):
    """Demonstrate error handling and recovery mechanisms."""
    print_section("Error Handling & Recovery")

    print("Testing error handling scenarios...")

    # Test graceful handling of missing data
    print_subsection("Missing Data Handling")
    result = session_cache.get_session_state("nonexistent_session")
    print(f"Retrieving nonexistent session: {result is None}")

    # Test batch operations with mixed results
    print_subsection("Batch Operations Error Handling")
    mixed_session_ids = ["session_1", "nonexistent", "session_2", "also_nonexistent"]
    retrieved_sessions = session_cache.get_multiple_sessions(mixed_session_ids)
    print("Batch retrieval with missing sessions:")
    print(f"  Requested: {len(mixed_session_ids)} sessions")
    print(f"  Retrieved: {len(retrieved_sessions)} sessions")
    print(f"  Success rate: {len(retrieved_sessions)/len(mixed_session_ids):.1%}")

    # Test metrics after errors
    print_subsection("Error Metrics")
    metrics = conn_manager.metrics.get_stats()
    print("Metrics after error scenarios:")
    print(f"  Total Operations: {metrics.get('total_operations', 0)}")
    print(f"  Errors: {metrics.get('errors', 0)}")
    print(f"  Hit Rate: {metrics.get('hit_rate', 0):.2%}")


def main():
    """Main demonstration function."""
    parser = argparse.ArgumentParser(description="Redis Cache Enhanced Demo")
    parser.add_argument("--with-redis", action="store_true",
                       help="Attempt to connect to actual Redis server")
    args = parser.parse_args()

    if not CACHE_MODULES_AVAILABLE:
        print("❌ Enhanced cache modules are not available.")
        print("Please ensure the redis_cache_enhanced.py file is properly installed.")
        return 1

    print("🚀 Redis Cache Enhanced Demo")
    print("=" * 60)

    if not args.with_redis and not REDIS_AVAILABLE:
        print("Running in MOCK MODE (no Redis package installed)")
        print("Use --with-redis flag to attempt real Redis connection")
    elif args.with_redis and REDIS_AVAILABLE:
        print("Attempting connection to REAL Redis server")
    else:
        print("Running in MOCK MODE")

    try:
        # Demonstrate connection management
        conn_manager, session_cache, invalidation_manager = demonstrate_connection_management()

        if not conn_manager:
            print("❌ Failed to establish connection. Exiting.")
            return 1

        # Demonstrate session caching
        demonstrate_session_caching(session_cache, conn_manager)

        # Demonstrate cache invalidation
        demonstrate_cache_invalidation(invalidation_manager)

        # Demonstrate health monitoring
        demonstrate_health_monitoring(conn_manager)

        # Demonstrate error handling
        demonstrate_error_handling(conn_manager, session_cache)

        # Final summary
        print_section("Demo Summary")
        print("✅ All demonstrations completed successfully!")

        final_stats = conn_manager.get_connection_stats()
        cache_metrics = final_stats.get("cache_metrics", {})

        print("\nFinal Performance Summary:")
        print(f"  Total Operations: {cache_metrics.get('total_operations', 0)}")
        print(f"  Cache Hit Rate: {cache_metrics.get('hit_rate', 0):.2%}")
        print(f"  Average Response Time: {cache_metrics.get('average_response_time', 0):.3f}s")
        print(f"  Operations/Second: {cache_metrics.get('operations_per_second', 0):.1f}")
        print(f"  Errors Encountered: {cache_metrics.get('errors', 0)}")

        # Cleanup
        print("\nCleaning up...")
        conn_manager.disconnect()
        print("✅ Disconnected from Redis")

        return 0

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
