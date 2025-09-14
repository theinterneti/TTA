"""
Enhanced Redis Caching Layer for TTA Prototype Session Management

This module provides enhanced Redis connection management, session caching utilities,
cache invalidation mechanisms, and advanced caching strategies for the therapeutic
text adventure system.

Classes:
    RedisConnectionManager: Enhanced Redis connection management with health monitoring
    SessionCacheManager: Advanced session state caching and retrieval
    CacheInvalidationManager: Comprehensive cache cleanup and invalidation
    CacheMetricsCollector: Cache performance monitoring and metrics
"""

import json
import logging
import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any, Optional

try:
    import redis
    from redis.exceptions import ConnectionError, RedisError, TimeoutError

    REDIS_AVAILABLE = True
except ImportError:
    print("Warning: redis package not installed. Install with: pip install redis")
    redis = None
    ConnectionError = Exception
    TimeoutError = Exception
    RedisError = Exception
    REDIS_AVAILABLE = False

# Import data models
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))

try:
    from data_models import (
        CharacterState,
        EmotionalState,
        NarrativeContext,
        SessionState,
        TherapeuticProgress,
    )
except ImportError:
    # Fallback for different import contexts
    SessionState = None
    CharacterState = None
    EmotionalState = None
    NarrativeContext = None
    TherapeuticProgress = None

logger = logging.getLogger(__name__)


class RedisCacheError(Exception):
    """Raised when Redis cache operations fail."""

    pass


class CacheMetrics:
    """Container for cache performance metrics."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.errors = 0
        self.total_response_time = 0.0
        self.operation_counts = defaultdict(int)
        self.start_time = datetime.now()
        self._lock = threading.Lock()

    def record_hit(self, response_time: float = 0.0):
        """Record a cache hit."""
        with self._lock:
            self.hits += 1
            self.total_response_time += response_time

    def record_miss(self, response_time: float = 0.0):
        """Record a cache miss."""
        with self._lock:
            self.misses += 1
            self.total_response_time += response_time

    def record_set(self, response_time: float = 0.0):
        """Record a cache set operation."""
        with self._lock:
            self.sets += 1
            self.total_response_time += response_time

    def record_delete(self, response_time: float = 0.0):
        """Record a cache delete operation."""
        with self._lock:
            self.deletes += 1
            self.total_response_time += response_time

    def record_error(self):
        """Record a cache error."""
        with self._lock:
            self.errors += 1

    def record_operation(self, operation: str, response_time: float = 0.0):
        """Record a specific operation."""
        with self._lock:
            self.operation_counts[operation] += 1
            self.total_response_time += response_time

    def get_stats(self) -> dict[str, Any]:
        """Get current metrics statistics."""
        with self._lock:
            total_operations = self.hits + self.misses + self.sets + self.deletes
            hit_rate = (self.hits / total_operations) if total_operations > 0 else 0.0
            avg_response_time = (
                (self.total_response_time / total_operations)
                if total_operations > 0
                else 0.0
            )
            uptime = (datetime.now() - self.start_time).total_seconds()

            return {
                "hits": self.hits,
                "misses": self.misses,
                "sets": self.sets,
                "deletes": self.deletes,
                "errors": self.errors,
                "total_operations": total_operations,
                "hit_rate": hit_rate,
                "average_response_time": avg_response_time,
                "uptime_seconds": uptime,
                "operations_per_second": (
                    total_operations / uptime if uptime > 0 else 0.0
                ),
                "operation_breakdown": dict(self.operation_counts),
            }

    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self.hits = 0
            self.misses = 0
            self.sets = 0
            self.deletes = 0
            self.errors = 0
            self.total_response_time = 0.0
            self.operation_counts.clear()
            self.start_time = datetime.now()


class RedisConnectionManager:
    """
    Enhanced Redis connection manager with health monitoring, automatic reconnection,
    and comprehensive connection statistics.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 5.0,
        max_connections: int = 50,
        decode_responses: bool = True,
        retry_on_timeout: bool = True,
        health_check_interval: int = 30,
        max_connection_failures: int = 3,
    ):
        """
        Initialize enhanced Redis connection manager.

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Socket connection timeout in seconds
            max_connections: Maximum connections in pool
            decode_responses: Whether to decode responses to strings
            retry_on_timeout: Whether to retry operations on timeout
            health_check_interval: Health check interval in seconds
            max_connection_failures: Maximum failures before reconnection attempt
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis package is required. Install with: pip install redis"
            )

        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.max_connections = max_connections
        self.decode_responses = decode_responses
        self.retry_on_timeout = retry_on_timeout
        self.health_check_interval = health_check_interval
        self.max_connection_failures = max_connection_failures

        self._connection_pool: Any | None = None
        self._redis_client: Any | None = None
        self._last_health_check: datetime | None = None
        self._connection_failures = 0
        self._connection_lock = threading.Lock()

        # Enhanced cache configuration with different TTLs for different data types
        self.ttl_config = {
            "default": 3600,  # 1 hour default TTL
            "session": 86400,  # 24 hours for sessions
            "character": 7200,  # 2 hours for character states
            "narrative": 1800,  # 30 minutes for narrative context
            "emotional": 3600,  # 1 hour for emotional states
            "therapeutic": 604800,  # 1 week for therapeutic progress
            "user_preferences": 2592000,  # 30 days for user preferences
            "temporary": 300,  # 5 minutes for temporary data
            "long_term": 7776000,  # 90 days for long-term data
        }

        # Metrics tracking
        self.metrics = CacheMetrics()

    def connect(self) -> None:
        """Establish connection to Redis server with enhanced error handling."""
        with self._connection_lock:
            try:
                # Create connection pool with enhanced configuration
                self._connection_pool = redis.ConnectionPool(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    socket_timeout=self.socket_timeout,
                    socket_connect_timeout=self.socket_connect_timeout,
                    max_connections=self.max_connections,
                    decode_responses=self.decode_responses,
                    retry_on_timeout=self.retry_on_timeout,
                )

                # Create Redis client
                self._redis_client = redis.Redis(connection_pool=self._connection_pool)

                # Test connection
                self._redis_client.ping()

                # Reset failure count on successful connection
                self._connection_failures = 0
                self._last_health_check = datetime.now()

                logger.info(
                    f"Connected to Redis at {self.host}:{self.port} (db: {self.db})"
                )

            except ConnectionError as e:
                self._connection_failures += 1
                raise RedisCacheError(f"Failed to connect to Redis: {e}") from e
            except Exception as e:
                self._connection_failures += 1
                raise RedisCacheError(
                    f"Unexpected error connecting to Redis: {e}"
                ) from e

    def disconnect(self) -> None:
        """Close connection to Redis server."""
        with self._connection_lock:
            if self._connection_pool:
                self._connection_pool.disconnect()
                self._connection_pool = None

            if self._redis_client:
                self._redis_client = None

            logger.info("Disconnected from Redis")

    def get_client(self):
        """
        Get Redis client instance with connection validation.

        Returns:
            redis.Redis: Redis client instance

        Raises:
            RedisCacheError: If not connected to Redis
        """
        if not self._redis_client:
            raise RedisCacheError("Not connected to Redis. Call connect() first.")

        # Validate connection health
        if not self.is_connected():
            raise RedisCacheError("Redis connection is not healthy")

        return self._redis_client

    def is_connected(self) -> bool:
        """
        Check if connected to Redis with enhanced health monitoring.

        Returns:
            bool: True if connected and responsive
        """
        if not self._redis_client:
            return False

        try:
            # Perform health check if interval has passed
            now = datetime.now()
            if (
                self._last_health_check is None
                or (now - self._last_health_check).seconds >= self.health_check_interval
            ):

                start_time = time.time()
                self._redis_client.ping()
                response_time = time.time() - start_time

                self._last_health_check = now
                self._connection_failures = 0  # Reset failure count on successful ping
                self.metrics.record_operation("health_check", response_time)
                return True

            # If within health check interval, assume connected
            return True

        except Exception as e:
            self._connection_failures += 1
            self.metrics.record_error()
            logger.warning(
                f"Redis health check failed (attempt {self._connection_failures}): {e}"
            )

            # Attempt reconnection if failures exceed threshold
            if self._connection_failures >= self.max_connection_failures:
                logger.info("Attempting Redis reconnection due to repeated failures")
                try:
                    self.reconnect()
                    return True
                except Exception as reconnect_error:
                    logger.error(f"Redis reconnection failed: {reconnect_error}")

            return False

    def reconnect(self) -> None:
        """Attempt to reconnect to Redis server."""
        try:
            logger.info("Reconnecting to Redis...")
            self.disconnect()
            self.connect()
            logger.info("Redis reconnection successful")
        except Exception as e:
            logger.error(f"Redis reconnection failed: {e}")
            raise RedisCacheError(f"Failed to reconnect to Redis: {e}") from e

    def get_ttl(self, data_type: str) -> int:
        """
        Get TTL for specific data type.

        Args:
            data_type: Type of data (session, character, narrative, etc.)

        Returns:
            int: TTL in seconds
        """
        return self.ttl_config.get(data_type, self.ttl_config["default"])

    def get_connection_stats(self) -> dict[str, Any]:
        """
        Get comprehensive connection statistics and health metrics.

        Returns:
            Dict[str, Any]: Connection statistics and health metrics
        """
        stats = {
            "connection_info": {
                "host": self.host,
                "port": self.port,
                "db": self.db,
                "connected": self.is_connected(),
                "max_connections": self.max_connections,
                "connection_failures": self._connection_failures,
                "last_health_check": (
                    self._last_health_check.isoformat()
                    if self._last_health_check
                    else None
                ),
            },
            "ttl_config": self.ttl_config.copy(),
            "cache_metrics": self.metrics.get_stats(),
        }

        # Add Redis server info if connected
        if self.is_connected():
            try:
                redis_info = self._redis_client.info()
                stats["redis_server_info"] = {
                    "redis_version": redis_info.get("redis_version", "unknown"),
                    "used_memory": redis_info.get("used_memory", 0),
                    "used_memory_human": redis_info.get("used_memory_human", "0B"),
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "total_commands_processed": redis_info.get(
                        "total_commands_processed", 0
                    ),
                    "keyspace_hits": redis_info.get("keyspace_hits", 0),
                    "keyspace_misses": redis_info.get("keyspace_misses", 0),
                    "uptime_in_seconds": redis_info.get("uptime_in_seconds", 0),
                    "role": redis_info.get("role", "unknown"),
                }

                # Calculate hit rate
                hits = redis_info.get("keyspace_hits", 0)
                misses = redis_info.get("keyspace_misses", 0)
                total_requests = hits + misses
                hit_rate = (hits / total_requests) if total_requests > 0 else 0.0
                stats["redis_server_info"]["hit_rate"] = hit_rate

            except Exception as e:
                logger.warning(f"Could not retrieve Redis server info: {e}")
                stats["redis_server_info"] = {"error": str(e)}

        return stats

    @contextmanager
    def get_client_context(self):
        """Context manager for Redis client operations with error handling."""
        try:
            client = self.get_client()
            yield client
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"Redis operation failed: {e}")
            raise

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class SessionCacheManager:
    """
    Enhanced session state caching and retrieval with advanced serialization strategies,
    compression, and performance optimization.
    """

    def __init__(self, connection_manager: RedisConnectionManager):
        """
        Initialize enhanced session cache manager.

        Args:
            connection_manager: Redis connection manager instance
        """
        self.connection_manager = connection_manager

        # Key prefixes for different data types
        self.key_prefixes = {
            "session": "tta:session:",
            "character": "tta:character:",
            "narrative": "tta:narrative:",
            "emotional": "tta:emotional:",
            "therapeutic": "tta:therapeutic:",
            "user": "tta:user:",
            "user_sessions": "tta:user:{user_id}:sessions",
            "session_lock": "tta:lock:session:",
            "batch": "tta:batch:",
        }

        # Serialization settings
        self.json_settings = {
            "ensure_ascii": False,
            "separators": (",", ":"),
            "default": self._json_serializer,
        }

        # Cache strategies
        self.compression_threshold = 1024  # Compress data larger than 1KB
        self.batch_size = 100  # Maximum batch size for bulk operations

    def _json_serializer(self, obj: Any) -> Any:
        """Enhanced JSON serializer for complex objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, "__dict__"):
            return asdict(obj) if hasattr(obj, "__dataclass_fields__") else obj.__dict__
        elif hasattr(obj, "value"):  # For Enum objects
            return obj.value
        elif isinstance(obj, set):
            return list(obj)
        return str(obj)

    def _generate_key(self, key_type: str, *args) -> str:
        """Generate Redis key with proper formatting."""
        if key_type == "user_sessions":
            return self.key_prefixes[key_type].format(user_id=args[0])
        elif key_type == "character" and len(args) == 2:
            return f"{self.key_prefixes[key_type]}{args[1]}:{args[0]}"  # session_id:character_id
        else:
            return f"{self.key_prefixes[key_type]}{':'.join(str(arg) for arg in args)}"

    def _serialize_data(self, data: Any) -> str:
        """Serialize data with optional compression."""
        if hasattr(data, "to_json"):
            json_str = data.to_json()
        else:
            json_str = json.dumps(data, **self.json_settings)

        # Apply compression if data is large
        if len(json_str) > self.compression_threshold:
            try:
                import gzip

                compressed = gzip.compress(json_str.encode("utf-8"))
                # Add compression marker
                return f"GZIP:{compressed.hex()}"
            except ImportError:
                logger.warning("gzip not available, storing uncompressed data")

        return json_str

    def _deserialize_data(self, data_str: str, data_class=None):
        """Deserialize data with decompression support."""
        if data_str.startswith("GZIP:"):
            try:
                import gzip

                compressed_hex = data_str[5:]  # Remove "GZIP:" prefix
                compressed = bytes.fromhex(compressed_hex)
                json_str = gzip.decompress(compressed).decode("utf-8")
            except ImportError as e:
                raise RedisCacheError("gzip not available for decompression") from e
        else:
            json_str = data_str

        if data_class and hasattr(data_class, "from_json"):
            return data_class.from_json(json_str)
        else:
            return json.loads(json_str)

    def _execute_with_metrics(self, operation: str, func, *args, **kwargs):
        """Execute Redis operation with metrics tracking."""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            response_time = time.time() - start_time

            if operation in ["get", "mget"]:
                if result:
                    self.connection_manager.metrics.record_hit(response_time)
                else:
                    self.connection_manager.metrics.record_miss(response_time)
            elif operation in ["set", "setex", "mset"]:
                self.connection_manager.metrics.record_set(response_time)
            elif operation in ["delete", "del"]:
                self.connection_manager.metrics.record_delete(response_time)

            self.connection_manager.metrics.record_operation(operation, response_time)
            return result

        except Exception:
            self.connection_manager.metrics.record_error()
            raise

    def cache_session_state(
        self, session_state: "SessionState", ttl: int | None = None
    ) -> bool:
        """
        Cache session state with enhanced serialization and error handling.

        Args:
            session_state: Session state object to cache
            ttl: Time to live in seconds (uses default if None)

        Returns:
            bool: True if caching was successful
        """
        if not SessionState:
            logger.error("SessionState class not available")
            return False

        try:
            with self.connection_manager.get_client_context() as client:
                session_key = self._generate_key("session", session_state.session_id)
                ttl = ttl or self.connection_manager.get_ttl("session")

                # Serialize session state with compression
                session_data = self._serialize_data(session_state)

                # Cache in Redis with pipeline for atomic operations
                pipe = client.pipeline()
                pipe.setex(session_key, ttl, session_data)

                # Add to user's session list
                user_sessions_key = self._generate_key(
                    "user_sessions", session_state.user_id
                )
                pipe.sadd(user_sessions_key, session_state.session_id)
                pipe.expire(user_sessions_key, ttl)

                # Execute pipeline
                self._execute_with_metrics("setex", pipe.execute)

                logger.debug(f"Cached session state: {session_state.session_id}")
                return True

        except Exception as e:
            logger.error(f"Error caching session state: {e}")
            return False

    def get_session_state(self, session_id: str) -> Optional["SessionState"]:
        """
        Retrieve session state with enhanced deserialization.

        Args:
            session_id: Session identifier

        Returns:
            Optional[SessionState]: Session state object or None if not found
        """
        if not SessionState:
            logger.error("SessionState class not available")
            return None

        try:
            with self.connection_manager.get_client_context() as client:
                session_key = self._generate_key("session", session_id)
                session_data = self._execute_with_metrics(
                    "get", client.get, session_key
                )

                if session_data:
                    return self._deserialize_data(session_data, SessionState)

                logger.debug(f"Session state not found in cache: {session_id}")
                return None

        except Exception as e:
            logger.error(f"Error retrieving session state: {e}")
            return None

    def cache_multiple_sessions(
        self, sessions: list["SessionState"], ttl: int | None = None
    ) -> int:
        """
        Cache multiple session states in a batch operation.

        Args:
            sessions: List of session state objects to cache
            ttl: Time to live in seconds (uses default if None)

        Returns:
            int: Number of sessions successfully cached
        """
        if not SessionState or not sessions:
            return 0

        try:
            with self.connection_manager.get_client_context() as client:
                ttl = ttl or self.connection_manager.get_ttl("session")
                cached_count = 0

                # Process in batches
                for i in range(0, len(sessions), self.batch_size):
                    batch = sessions[i : i + self.batch_size]
                    pipe = client.pipeline()

                    for session in batch:
                        session_key = self._generate_key("session", session.session_id)
                        session_data = self._serialize_data(session)
                        pipe.setex(session_key, ttl, session_data)

                        # Add to user's session list
                        user_sessions_key = self._generate_key(
                            "user_sessions", session.user_id
                        )
                        pipe.sadd(user_sessions_key, session.session_id)
                        pipe.expire(user_sessions_key, ttl)

                    results = self._execute_with_metrics("mset", pipe.execute)
                    cached_count += len([r for r in results if r])

                logger.info(f"Cached {cached_count} session states in batch")
                return cached_count

        except Exception as e:
            logger.error(f"Error caching multiple sessions: {e}")
            return 0

    def get_multiple_sessions(
        self, session_ids: list[str]
    ) -> dict[str, "SessionState"]:
        """
        Retrieve multiple session states in a batch operation.

        Args:
            session_ids: List of session identifiers

        Returns:
            Dict[str, SessionState]: Dictionary mapping session IDs to session states
        """
        if not SessionState or not session_ids:
            return {}

        try:
            with self.connection_manager.get_client_context() as client:
                session_keys = [
                    self._generate_key("session", sid) for sid in session_ids
                ]
                session_data_list = self._execute_with_metrics(
                    "mget", client.mget, session_keys
                )

                results = {}
                for session_id, session_data in zip(
                    session_ids, session_data_list, strict=False
                ):
                    if session_data:
                        try:
                            results[session_id] = self._deserialize_data(
                                session_data, SessionState
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to deserialize session {session_id}: {e}"
                            )

                logger.debug(
                    f"Retrieved {len(results)} session states from {len(session_ids)} requested"
                )
                return results

        except Exception as e:
            logger.error(f"Error retrieving multiple sessions: {e}")
            return {}

    def cache_therapeutic_progress(
        self, progress: "TherapeuticProgress", user_id: str, ttl: int | None = None
    ) -> bool:
        """
        Cache therapeutic progress with long-term storage.

        Args:
            progress: Therapeutic progress object to cache
            user_id: User identifier
            ttl: Time to live in seconds (uses therapeutic TTL if None)

        Returns:
            bool: True if caching was successful
        """
        if not TherapeuticProgress:
            logger.error("TherapeuticProgress class not available")
            return False

        try:
            with self.connection_manager.get_client_context() as client:
                progress_key = self._generate_key("therapeutic", user_id)
                ttl = ttl or self.connection_manager.get_ttl("therapeutic")

                # Serialize therapeutic progress
                progress_data = self._serialize_data(progress)

                # Cache with extended TTL for therapeutic data
                self._execute_with_metrics(
                    "setex", client.setex, progress_key, ttl, progress_data
                )

                logger.debug(f"Cached therapeutic progress for user: {user_id}")
                return True

        except Exception as e:
            logger.error(f"Error caching therapeutic progress: {e}")
            return False

    def get_therapeutic_progress(self, user_id: str) -> Optional["TherapeuticProgress"]:
        """
        Retrieve therapeutic progress from cache.

        Args:
            user_id: User identifier

        Returns:
            Optional[TherapeuticProgress]: Therapeutic progress object or None if not found
        """
        if not TherapeuticProgress:
            logger.error("TherapeuticProgress class not available")
            return None

        try:
            with self.connection_manager.get_client_context() as client:
                progress_key = self._generate_key("therapeutic", user_id)
                progress_data = self._execute_with_metrics(
                    "get", client.get, progress_key
                )

                if progress_data:
                    return self._deserialize_data(progress_data, TherapeuticProgress)

                logger.debug(f"Therapeutic progress not found in cache: {user_id}")
                return None

        except Exception as e:
            logger.error(f"Error retrieving therapeutic progress: {e}")
            return None

    def update_session_timestamp(
        self, session_id: str, extend_ttl: bool = True
    ) -> bool:
        """
        Update session last access timestamp with optional TTL extension.

        Args:
            session_id: Session identifier
            extend_ttl: Whether to extend the TTL

        Returns:
            bool: True if update was successful
        """
        try:
            with self.connection_manager.get_client_context() as client:
                session_key = self._generate_key("session", session_id)

                # Check if session exists
                if self._execute_with_metrics("exists", client.exists, session_key):
                    if extend_ttl:
                        # Extend TTL to full session TTL
                        ttl = self.connection_manager.get_ttl("session")
                        self._execute_with_metrics(
                            "expire", client.expire, session_key, ttl
                        )

                    # Update timestamp in session data if needed
                    # This could be implemented by retrieving, updating, and storing back
                    return True

                return False

        except Exception as e:
            logger.error(f"Error updating session timestamp: {e}")
            return False

    def get_user_sessions(self, user_id: str) -> list[str]:
        """
        Get list of session IDs for a user with enhanced error handling.

        Args:
            user_id: User identifier

        Returns:
            List[str]: List of session IDs
        """
        try:
            with self.connection_manager.get_client_context() as client:
                user_sessions_key = self._generate_key("user_sessions", user_id)
                sessions = self._execute_with_metrics(
                    "smembers", client.smembers, user_sessions_key
                )
                return list(sessions) if sessions else []

        except Exception as e:
            logger.error(f"Error retrieving user sessions: {e}")
            return []

    def get_cache_size_info(self) -> dict[str, Any]:
        """
        Get information about cache size and memory usage.

        Returns:
            Dict[str, Any]: Cache size information
        """
        try:
            with self.connection_manager.get_client_context() as client:
                info = {}

                # Count keys by type
                for key_type, prefix in self.key_prefixes.items():
                    if "{" not in prefix:  # Skip template keys
                        pattern = f"{prefix}*"
                        keys = client.keys(pattern)
                        info[f"{key_type}_count"] = len(keys)

                        # Sample memory usage for first few keys
                        if keys:
                            sample_keys = keys[: min(10, len(keys))]
                            total_memory = sum(
                                client.memory_usage(key) or 0 for key in sample_keys
                            )
                            avg_memory = (
                                total_memory / len(sample_keys) if sample_keys else 0
                            )
                            info[f"{key_type}_avg_memory"] = avg_memory
                            info[f"{key_type}_estimated_total_memory"] = (
                                avg_memory * len(keys)
                            )

                return info

        except Exception as e:
            logger.error(f"Error getting cache size info: {e}")
            return {}


class CacheInvalidationManager:
    """
    Enhanced cache cleanup and invalidation with advanced strategies,
    batch operations, and comprehensive cleanup mechanisms.
    """

    def __init__(self, connection_manager: RedisConnectionManager):
        """
        Initialize enhanced cache invalidation manager.

        Args:
            connection_manager: Redis connection manager instance
        """
        self.connection_manager = connection_manager

        # Key patterns for different data types
        self.key_patterns = {
            "session": "tta:session:*",
            "character": "tta:character:*",
            "narrative": "tta:narrative:*",
            "emotional": "tta:emotional:*",
            "therapeutic": "tta:therapeutic:*",
            "user": "tta:user:*",
            "all_tta": "tta:*",
        }

        # Cleanup strategies
        self.cleanup_batch_size = 1000
        self.max_cleanup_time = 300  # 5 minutes maximum cleanup time

    def invalidate_session(
        self, session_id: str, cascade: bool = True
    ) -> dict[str, int]:
        """
        Invalidate all cache entries for a session with detailed reporting.

        Args:
            session_id: Session identifier
            cascade: Whether to cascade delete related data

        Returns:
            Dict[str, int]: Count of deleted keys by type
        """
        deleted_counts = {"session": 0, "narrative": 0, "character": 0, "total": 0}

        try:
            with self.connection_manager.get_client_context() as client:
                keys_to_delete = []

                # Session state key
                session_key = f"tta:session:{session_id}"
                if client.exists(session_key):
                    keys_to_delete.append(session_key)
                    deleted_counts["session"] = 1

                # Narrative context key
                narrative_key = f"tta:narrative:{session_id}"
                if client.exists(narrative_key):
                    keys_to_delete.append(narrative_key)
                    deleted_counts["narrative"] = 1

                if cascade:
                    # Character state keys for this session
                    character_pattern = f"tta:character:{session_id}:*"
                    character_keys = client.keys(character_pattern)
                    keys_to_delete.extend(character_keys)
                    deleted_counts["character"] = len(character_keys)

                # Delete all keys in batch
                if keys_to_delete:
                    deleted_count = (
                        self.connection_manager.metrics._execute_with_metrics(
                            "delete", client.delete, *keys_to_delete
                        )
                    )
                    deleted_counts["total"] = deleted_count
                    logger.info(
                        f"Invalidated {deleted_count} cache entries for session: {session_id}"
                    )

                return deleted_counts

        except Exception as e:
            logger.error(f"Error invalidating session cache: {e}")
            return deleted_counts

    def invalidate_user_data(
        self, user_id: str, preserve_therapeutic: bool = True
    ) -> dict[str, int]:
        """
        Invalidate all cache entries for a user with options to preserve important data.

        Args:
            user_id: User identifier
            preserve_therapeutic: Whether to preserve therapeutic progress data

        Returns:
            Dict[str, int]: Count of deleted keys by type
        """
        deleted_counts = {
            "sessions": 0,
            "emotional": 0,
            "user_data": 0,
            "therapeutic": 0,
            "total": 0,
        }

        try:
            with self.connection_manager.get_client_context() as client:
                # Get user sessions
                user_sessions_key = f"tta:user:{user_id}:sessions"
                sessions = client.smembers(user_sessions_key)

                # Invalidate each session
                for session_id in sessions:
                    session_counts = self.invalidate_session(session_id)
                    deleted_counts["sessions"] += session_counts["total"]

                keys_to_delete = []

                # Emotional state key
                emotional_key = f"tta:emotional:{user_id}"
                if client.exists(emotional_key):
                    keys_to_delete.append(emotional_key)
                    deleted_counts["emotional"] = 1

                # User sessions key
                if client.exists(user_sessions_key):
                    keys_to_delete.append(user_sessions_key)
                    deleted_counts["user_data"] += 1

                # Therapeutic data (optional)
                if not preserve_therapeutic:
                    therapeutic_key = f"tta:therapeutic:{user_id}"
                    if client.exists(therapeutic_key):
                        keys_to_delete.append(therapeutic_key)
                        deleted_counts["therapeutic"] = 1

                # Delete remaining keys
                if keys_to_delete:
                    additional_deleted = client.delete(*keys_to_delete)
                    deleted_counts["total"] = (
                        deleted_counts["sessions"] + additional_deleted
                    )
                    logger.info(
                        f"Invalidated {additional_deleted} additional cache entries for user: {user_id}"
                    )

                return deleted_counts

        except Exception as e:
            logger.error(f"Error invalidating user cache: {e}")
            return deleted_counts

    def invalidate_character(self, character_id: str, session_id: str = None) -> int:
        """
        Invalidate cache entries for a character with enhanced pattern matching.

        Args:
            character_id: Character identifier
            session_id: Session ID (if None, invalidates all sessions)

        Returns:
            int: Number of keys deleted
        """
        try:
            with self.connection_manager.get_client_context() as client:
                if session_id:
                    # Invalidate specific session character
                    character_key = f"tta:character:{session_id}:{character_id}"
                    deleted_count = client.delete(character_key)
                else:
                    # Invalidate all sessions for this character
                    character_pattern = f"tta:character:*:{character_id}"
                    character_keys = client.keys(character_pattern)
                    if character_keys:
                        deleted_count = client.delete(*character_keys)
                    else:
                        deleted_count = 0

                logger.info(
                    f"Invalidated {deleted_count} character cache entries: {character_id}"
                )
                return deleted_count

        except Exception as e:
            logger.error(f"Error invalidating character cache: {e}")
            return 0

    def cleanup_expired_sessions(
        self, max_age_hours: int = 24, dry_run: bool = False
    ) -> dict[str, Any]:
        """
        Clean up expired session data with comprehensive reporting.

        Args:
            max_age_hours: Maximum age in hours for session data
            dry_run: If True, only report what would be cleaned without deleting

        Returns:
            Dict[str, Any]: Cleanup results and statistics
        """
        cleanup_stats = {
            "sessions_processed": 0,
            "sessions_expired": 0,
            "sessions_cleaned": 0,
            "total_keys_deleted": 0,
            "errors": 0,
            "processing_time": 0,
            "dry_run": dry_run,
        }

        start_time = time.time()

        try:
            with self.connection_manager.get_client_context() as client:
                cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

                # Get all session keys in batches
                session_pattern = self.key_patterns["session"]
                cursor = 0

                while True:
                    cursor, session_keys = client.scan(
                        cursor, match=session_pattern, count=self.cleanup_batch_size
                    )

                    if not session_keys:
                        if cursor == 0:
                            break
                        continue

                    # Process batch
                    for session_key in session_keys:
                        cleanup_stats["sessions_processed"] += 1

                        try:
                            # Get session data
                            session_data = client.get(session_key)
                            if session_data and SessionState:
                                session_state = SessionState.from_json(session_data)

                                # Check if session is too old
                                if session_state.last_updated < cutoff_time:
                                    cleanup_stats["sessions_expired"] += 1

                                    if not dry_run:
                                        session_id = session_state.session_id
                                        deleted_counts = self.invalidate_session(
                                            session_id
                                        )
                                        cleanup_stats["sessions_cleaned"] += 1
                                        cleanup_stats[
                                            "total_keys_deleted"
                                        ] += deleted_counts["total"]

                        except Exception as e:
                            cleanup_stats["errors"] += 1
                            logger.warning(
                                f"Error processing session key {session_key}: {e}"
                            )
                            continue

                    # Check if we've exceeded maximum cleanup time
                    if time.time() - start_time > self.max_cleanup_time:
                        logger.warning("Cleanup time limit exceeded, stopping")
                        break

                    if cursor == 0:
                        break

                cleanup_stats["processing_time"] = time.time() - start_time

                if dry_run:
                    logger.info(
                        f"Dry run: Would clean up {cleanup_stats['sessions_expired']} expired sessions"
                    )
                else:
                    logger.info(
                        f"Cleaned up {cleanup_stats['sessions_cleaned']} expired sessions"
                    )

                return cleanup_stats

        except Exception as e:
            cleanup_stats["errors"] += 1
            cleanup_stats["processing_time"] = time.time() - start_time
            logger.error(f"Error during cleanup: {e}")
            return cleanup_stats

    def cleanup_orphaned_data(self, dry_run: bool = False) -> dict[str, Any]:
        """
        Clean up orphaned cache entries that no longer have valid references.

        Args:
            dry_run: If True, only report what would be cleaned without deleting

        Returns:
            Dict[str, Any]: Cleanup results
        """
        cleanup_stats = {
            "orphaned_characters": 0,
            "orphaned_narratives": 0,
            "orphaned_emotional": 0,
            "total_orphaned": 0,
            "dry_run": dry_run,
        }

        try:
            with self.connection_manager.get_client_context() as client:
                # Get all session IDs
                session_keys = client.keys(self.key_patterns["session"])
                valid_session_ids = set()

                for session_key in session_keys:
                    session_id = session_key.split(":")[-1]
                    valid_session_ids.add(session_id)

                # Check character keys
                character_keys = client.keys(self.key_patterns["character"])
                orphaned_characters = []

                for char_key in character_keys:
                    # Extract session ID from character key (format: tta:character:session_id:character_id)
                    parts = char_key.split(":")
                    if len(parts) >= 4:
                        session_id = parts[2]
                        if session_id not in valid_session_ids:
                            orphaned_characters.append(char_key)

                cleanup_stats["orphaned_characters"] = len(orphaned_characters)

                # Check narrative keys
                narrative_keys = client.keys(self.key_patterns["narrative"])
                orphaned_narratives = []

                for narr_key in narrative_keys:
                    session_id = narr_key.split(":")[-1]
                    if session_id not in valid_session_ids:
                        orphaned_narratives.append(narr_key)

                cleanup_stats["orphaned_narratives"] = len(orphaned_narratives)

                # Clean up orphaned data if not dry run
                if not dry_run:
                    all_orphaned = orphaned_characters + orphaned_narratives
                    if all_orphaned:
                        deleted_count = client.delete(*all_orphaned)
                        cleanup_stats["total_orphaned"] = deleted_count
                        logger.info(
                            f"Cleaned up {deleted_count} orphaned cache entries"
                        )
                else:
                    cleanup_stats["total_orphaned"] = len(orphaned_characters) + len(
                        orphaned_narratives
                    )
                    logger.info(
                        f"Dry run: Would clean up {cleanup_stats['total_orphaned']} orphaned entries"
                    )

                return cleanup_stats

        except Exception as e:
            logger.error(f"Error cleaning up orphaned data: {e}")
            return cleanup_stats

    def get_cache_statistics(self) -> dict[str, Any]:
        """
        Get comprehensive cache statistics and health information.

        Returns:
            Dict[str, Any]: Detailed cache statistics
        """
        try:
            with self.connection_manager.get_client_context() as client:
                stats = {
                    "key_counts": {},
                    "memory_usage": {},
                    "ttl_distribution": {},
                    "redis_info": {},
                }

                # Count keys by pattern
                total_keys = 0
                for key_type, pattern in self.key_patterns.items():
                    if key_type != "all_tta":  # Skip the catch-all pattern
                        keys = client.keys(pattern)
                        count = len(keys)
                        stats["key_counts"][key_type] = count
                        total_keys += count

                        # Sample TTL distribution
                        if keys:
                            sample_keys = keys[: min(100, len(keys))]
                            ttls = []
                            for key in sample_keys:
                                ttl = client.ttl(key)
                                if ttl > 0:
                                    ttls.append(ttl)

                            if ttls:
                                stats["ttl_distribution"][key_type] = {
                                    "min": min(ttls),
                                    "max": max(ttls),
                                    "avg": sum(ttls) / len(ttls),
                                    "sample_size": len(ttls),
                                }

                stats["key_counts"]["total"] = total_keys

                # Get Redis server info
                redis_info = client.info()
                stats["redis_info"] = {
                    "used_memory": redis_info.get("used_memory", 0),
                    "used_memory_human": redis_info.get("used_memory_human", "0B"),
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "total_commands_processed": redis_info.get(
                        "total_commands_processed", 0
                    ),
                    "keyspace_hits": redis_info.get("keyspace_hits", 0),
                    "keyspace_misses": redis_info.get("keyspace_misses", 0),
                    "expired_keys": redis_info.get("expired_keys", 0),
                    "evicted_keys": redis_info.get("evicted_keys", 0),
                }

                # Calculate hit rate
                hits = redis_info.get("keyspace_hits", 0)
                misses = redis_info.get("keyspace_misses", 0)
                total_requests = hits + misses
                stats["redis_info"]["hit_rate"] = (
                    (hits / total_requests) if total_requests > 0 else 0.0
                )

                return stats

        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {}

    def clear_all_cache(self, confirm_token: str = None) -> dict[str, Any]:
        """
        Clear all TTA-related cache entries with safety confirmation.
        WARNING: This is destructive and should only be used for testing or maintenance.

        Args:
            confirm_token: Safety token to confirm destructive operation

        Returns:
            Dict[str, Any]: Results of the clear operation
        """
        if confirm_token != "CONFIRM_CLEAR_ALL_CACHE":
            return {
                "error": "Invalid confirmation token. Use 'CONFIRM_CLEAR_ALL_CACHE' to confirm.",
                "cleared": False,
            }

        try:
            with self.connection_manager.get_client_context() as client:
                # Get all TTA keys
                all_keys = client.keys(self.key_patterns["all_tta"])

                if not all_keys:
                    return {
                        "message": "No TTA cache entries found",
                        "cleared": True,
                        "keys_deleted": 0,
                    }

                # Delete in batches to avoid blocking Redis
                total_deleted = 0
                batch_size = 1000

                for i in range(0, len(all_keys), batch_size):
                    batch = all_keys[i : i + batch_size]
                    deleted_count = client.delete(*batch)
                    total_deleted += deleted_count

                logger.warning(f"Cleared all cache - deleted {total_deleted} keys")

                return {
                    "message": "Successfully cleared all TTA cache entries",
                    "cleared": True,
                    "keys_deleted": total_deleted,
                }

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return {"error": str(e), "cleared": False}


# Enhanced utility functions for Redis cache operations
def create_redis_connection(
    host: str = "localhost", port: int = 6379, **kwargs
) -> RedisConnectionManager:
    """
    Create Redis connection manager with enhanced configuration.

    Args:
        host: Redis server host
        port: Redis server port
        **kwargs: Additional connection parameters

    Returns:
        RedisConnectionManager: Configured connection manager
    """
    return RedisConnectionManager(host=host, port=port, **kwargs)


def get_session_cache_manager(
    connection_manager: RedisConnectionManager,
) -> SessionCacheManager:
    """
    Create session cache manager instance.

    Args:
        connection_manager: Redis connection manager

    Returns:
        SessionCacheManager: Session cache manager instance
    """
    return SessionCacheManager(connection_manager)


def get_cache_invalidation_manager(
    connection_manager: RedisConnectionManager,
) -> CacheInvalidationManager:
    """
    Create cache invalidation manager instance.

    Args:
        connection_manager: Redis connection manager

    Returns:
        CacheInvalidationManager: Cache invalidation manager instance
    """
    return CacheInvalidationManager(connection_manager)


def create_cache_system(
    host: str = "localhost", port: int = 6379, **kwargs
) -> tuple[RedisConnectionManager, SessionCacheManager, CacheInvalidationManager]:
    """
    Create complete cache system with all managers.

    Args:
        host: Redis server host
        port: Redis server port
        **kwargs: Additional connection parameters

    Returns:
        Tuple: (connection_manager, session_cache_manager, invalidation_manager)
    """
    connection_manager = create_redis_connection(host, port, **kwargs)
    session_cache_manager = get_session_cache_manager(connection_manager)
    invalidation_manager = get_cache_invalidation_manager(connection_manager)

    return connection_manager, session_cache_manager, invalidation_manager


def health_check_cache_system(
    connection_manager: RedisConnectionManager,
) -> dict[str, Any]:
    """
    Perform comprehensive health check of the cache system.

    Args:
        connection_manager: Redis connection manager

    Returns:
        Dict[str, Any]: Health check results
    """
    health_status = {
        "overall_status": "unknown",
        "connection_status": "unknown",
        "performance_status": "unknown",
        "issues": [],
        "recommendations": [],
    }

    try:
        # Check connection
        if connection_manager.is_connected():
            health_status["connection_status"] = "healthy"
        else:
            health_status["connection_status"] = "unhealthy"
            health_status["issues"].append("Redis connection is not healthy")

        # Get connection stats
        stats = connection_manager.get_connection_stats()

        # Check performance metrics
        cache_metrics = stats.get("cache_metrics", {})
        hit_rate = cache_metrics.get("hit_rate", 0.0)
        avg_response_time = cache_metrics.get("average_response_time", 0.0)

        if hit_rate < 0.5:
            health_status["issues"].append(f"Low cache hit rate: {hit_rate:.2%}")
            health_status["recommendations"].append(
                "Consider adjusting TTL values or cache warming strategies"
            )

        if avg_response_time > 0.1:  # 100ms
            health_status["issues"].append(
                f"High average response time: {avg_response_time:.3f}s"
            )
            health_status["recommendations"].append(
                "Consider Redis performance tuning or connection optimization"
            )

        # Check Redis server health
        redis_info = stats.get("redis_server_info", {})
        used_memory = redis_info.get("used_memory", 0)
        connected_clients = redis_info.get("connected_clients", 0)

        if used_memory > 1024 * 1024 * 1024:  # 1GB
            health_status["issues"].append(
                f"High memory usage: {redis_info.get('used_memory_human', 'unknown')}"
            )
            health_status["recommendations"].append(
                "Consider implementing more aggressive cache cleanup policies"
            )

        if connected_clients > 100:
            health_status["issues"].append(
                f"High number of connected clients: {connected_clients}"
            )
            health_status["recommendations"].append(
                "Monitor connection pooling and client management"
            )

        # Determine overall status
        if not health_status["issues"]:
            health_status["overall_status"] = "healthy"
            health_status["performance_status"] = "good"
        elif len(health_status["issues"]) <= 2:
            health_status["overall_status"] = "warning"
            health_status["performance_status"] = "acceptable"
        else:
            health_status["overall_status"] = "critical"
            health_status["performance_status"] = "poor"

        health_status["stats"] = stats

    except Exception as e:
        health_status["overall_status"] = "error"
        health_status["connection_status"] = "error"
        health_status["performance_status"] = "error"
        health_status["issues"].append(f"Health check failed: {str(e)}")

    return health_status


# Configuration helper for TTA integration
def get_tta_redis_config() -> dict[str, Any]:
    """
    Get Redis configuration optimized for TTA therapeutic text adventure.

    Returns:
        Dict[str, Any]: Recommended Redis configuration
    """
    return {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "socket_timeout": 5.0,
        "socket_connect_timeout": 5.0,
        "max_connections": 50,
        "decode_responses": True,
        "retry_on_timeout": True,
        "health_check_interval": 30,
        "max_connection_failures": 3,
    }


if __name__ == "__main__":
    # Example usage and testing
    import logging

    logging.basicConfig(level=logging.INFO)

    # Create cache system
    try:
        config = get_tta_redis_config()
        conn_manager, session_cache, invalidation_manager = create_cache_system(
            **config
        )

        # Connect and perform health check
        conn_manager.connect()
        health_status = health_check_cache_system(conn_manager)

        print("Cache System Health Check:")
        print(f"Overall Status: {health_status['overall_status']}")
        print(f"Connection Status: {health_status['connection_status']}")
        print(f"Performance Status: {health_status['performance_status']}")

        if health_status["issues"]:
            print("\nIssues:")
            for issue in health_status["issues"]:
                print(f"  - {issue}")

        if health_status["recommendations"]:
            print("\nRecommendations:")
            for rec in health_status["recommendations"]:
                print(f"  - {rec}")

        # Get cache statistics
        stats = invalidation_manager.get_cache_statistics()
        print("\nCache Statistics:")
        print(f"Total Keys: {stats.get('key_counts', {}).get('total', 0)}")
        print(
            f"Memory Usage: {stats.get('redis_info', {}).get('used_memory_human', 'unknown')}"
        )
        print(f"Hit Rate: {stats.get('redis_info', {}).get('hit_rate', 0):.2%}")

        conn_manager.disconnect()

    except Exception as e:
        print(f"Error testing cache system: {e}")
