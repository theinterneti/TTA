"""
Mock Services for Development and Testing

This module provides mock implementations of external services to enable
running the FastAPI application without external dependencies like Neo4j and Redis.
"""

import asyncio
import logging
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MockServiceState(Enum):
    """Mock service operational states."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    OFFLINE = "offline"


@dataclass
class MockServiceConfig:
    """Configuration for mock service behavior."""

    # Performance characteristics
    base_latency_ms: float = 10.0
    latency_variance_ms: float = 5.0
    failure_rate: float = 0.0  # 0.0 = no failures, 1.0 = always fail

    # State management
    state: MockServiceState = MockServiceState.HEALTHY
    state_transition_probability: float = (
        0.01  # Probability of state change per operation
    )

    # Data persistence
    enable_persistence: bool = True
    max_memory_items: int = 10000
    ttl_seconds: int = 3600  # Default TTL for cached items

    # Monitoring
    enable_metrics: bool = True
    log_operations: bool = False


@dataclass
class MockServiceMetrics:
    """Metrics tracking for mock services."""

    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_latency_ms: float = 0.0
    state_changes: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_operations == 0:
            return 1.0
        return self.successful_operations / self.total_operations

    @property
    def average_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.successful_operations == 0:
            return 0.0
        return self.total_latency_ms / self.successful_operations

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": self.success_rate,
            "average_latency_ms": self.average_latency_ms,
            "state_changes": self.state_changes,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "uptime_seconds": (datetime.now() - self.created_at).total_seconds(),
        }


class MockNeo4jDriver:
    """Enhanced Mock Neo4j driver for development and testing."""

    def __init__(self, uri: str, auth: tuple, config: MockServiceConfig | None = None):
        self.uri = uri
        self.auth = auth
        self.connected = False
        self.config = config or MockServiceConfig()
        self.metrics = MockServiceMetrics()

        # Enhanced data storage with relationships and indexing
        self._nodes: dict[str, dict[str, Any]] = {}  # node_id -> node_data
        self._relationships: dict[str, dict[str, Any]] = {}  # rel_id -> rel_data
        self._indexes: dict[str, set[str]] = {}  # label -> set of node_ids
        self._node_counter = 0
        self._rel_counter = 0

        logger.info(f"Enhanced MockNeo4jDriver initialized for {uri}")

    def session(self):
        """Return a mock session context manager."""
        return MockNeo4jSession(self)

    def close(self):
        """Close the mock driver."""
        self.connected = False
        logger.debug("MockNeo4jDriver closed")

    async def _simulate_latency(self):
        """Simulate realistic database latency."""
        if self.config.base_latency_ms > 0:
            latency = max(
                0,
                random.gauss(
                    self.config.base_latency_ms, self.config.latency_variance_ms
                ),
            )
            await asyncio.sleep(latency / 1000.0)
            return latency
        return 0.0

    def _should_fail(self) -> bool:
        """Determine if operation should fail based on configuration."""
        return random.random() < self.config.failure_rate

    def _update_state(self):
        """Randomly update service state based on configuration."""
        if random.random() < self.config.state_transition_probability:
            states = list(MockServiceState)
            self.config.state = random.choice(states)
            self.metrics.state_changes += 1
            logger.debug(f"MockNeo4jDriver state changed to {self.config.state}")

    def get_metrics(self) -> dict[str, Any]:
        """Get service metrics."""
        return {
            "service": "neo4j",
            "state": self.config.state.value,
            "metrics": self.metrics.to_dict(),
            "data_stats": {
                "nodes": len(self._nodes),
                "relationships": len(self._relationships),
                "indexes": len(self._indexes),
            },
        }


class MockNeo4jSession:
    """Enhanced Mock Neo4j session with realistic query processing."""

    def __init__(self, driver: MockNeo4jDriver):
        self.driver = driver
        self.transaction_active = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.transaction_active:
            self.transaction_active = False

    def run_sync(self, query: str, **parameters):
        """Synchronous version for compatibility."""
        return asyncio.run(self._async_run(query, **parameters))

    # Alias for backward compatibility
    def run(self, query: str, **parameters):
        """Mock query execution (sync version for compatibility)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a task
                return asyncio.create_task(self._async_run(query, **parameters))
            else:
                return asyncio.run(self._async_run(query, **parameters))
        except RuntimeError:
            # Fallback to sync processing
            return self._sync_run(query, **parameters)

    def _sync_run(self, query: str, **parameters):
        """Synchronous query processing fallback."""
        self.driver.metrics.total_operations += 1
        self.driver._update_state()

        if self.driver.config.log_operations:
            logger.debug(
                f"Mock Neo4j query (sync): {query[:100]}... with params: {parameters}"
            )

        try:
            result = self._process_query_sync(query, parameters)
            self.driver.metrics.successful_operations += 1
            return result
        except Exception as e:
            self.driver.metrics.failed_operations += 1
            logger.error(f"Mock Neo4j query failed: {e}")
            raise

    async def _async_run(self, query: str, **parameters):
        """Async query processing."""
        time.time()

        self.driver.metrics.total_operations += 1
        self.driver._update_state()

        # Simulate latency
        latency = await self.driver._simulate_latency()

        # Check for failure simulation
        if self.driver._should_fail():
            self.driver.metrics.failed_operations += 1
            raise Exception("Simulated Neo4j failure")

        if self.driver.config.log_operations:
            logger.debug(
                f"Mock Neo4j query (async): {query[:100]}... with params: {parameters}"
            )

        try:
            result = await self._process_query(query, parameters)
            self.driver.metrics.successful_operations += 1
            self.driver.metrics.total_latency_ms += latency
            return result
        except Exception as e:
            self.driver.metrics.failed_operations += 1
            logger.error(f"Mock Neo4j query failed: {e}")
            raise

    async def _process_query(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Process query with realistic Neo4j-like behavior."""
        query_upper = query.upper().strip()

        # CREATE operations
        if query_upper.startswith("CREATE"):
            return await self._handle_create(query, parameters)

        # MATCH operations
        elif query_upper.startswith("MATCH"):
            return await self._handle_match(query, parameters)

        # MERGE operations
        elif query_upper.startswith("MERGE"):
            return await self._handle_merge(query, parameters)

        # DELETE operations
        elif query_upper.startswith("DELETE"):
            return await self._handle_delete(query, parameters)

        # RETURN operations (standalone)
        elif query_upper.startswith("RETURN"):
            return await self._handle_return(query, parameters)

        # Default fallback
        else:
            return MockNeo4jResult([{"result": "mock", "query_type": "unknown"}])

    def _process_query_sync(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Synchronous version of query processing."""
        query_upper = query.upper().strip()

        if query_upper.startswith("CREATE"):
            return self._handle_create_sync(query, parameters)
        elif query_upper.startswith("MATCH"):
            return self._handle_match_sync(query, parameters)
        elif query_upper.startswith("MERGE"):
            return self._handle_merge_sync(query, parameters)
        elif query_upper.startswith("DELETE"):
            return self._handle_delete_sync(query, parameters)
        elif query_upper.startswith("RETURN"):
            return self._handle_return_sync(query, parameters)
        else:
            return MockNeo4jResult([{"result": "mock", "query_type": "unknown"}])

    async def _handle_create(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Handle CREATE operations."""
        # Simple node creation simulation
        node_id = str(uuid.uuid4())
        self.driver._node_counter += 1

        # Extract basic node properties from parameters
        node_data = {
            "id": node_id,
            "created_at": datetime.now().isoformat(),
            **parameters,
        }

        self.driver._nodes[node_id] = node_data

        # Add to indexes (simulate labels)
        if "label" in parameters:
            label = parameters["label"]
            if label not in self.driver._indexes:
                self.driver._indexes[label] = set()
            self.driver._indexes[label].add(node_id)

        return MockNeo4jResult(
            [{"created": True, "node_id": node_id, "properties": node_data}]
        )

    def _handle_create_sync(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Synchronous CREATE handler."""
        node_id = str(uuid.uuid4())
        self.driver._node_counter += 1

        node_data = {
            "id": node_id,
            "created_at": datetime.now().isoformat(),
            **parameters,
        }

        self.driver._nodes[node_id] = node_data

        if "label" in parameters:
            label = parameters["label"]
            if label not in self.driver._indexes:
                self.driver._indexes[label] = set()
            self.driver._indexes[label].add(node_id)

        return MockNeo4jResult(
            [{"created": True, "node_id": node_id, "properties": node_data}]
        )

    async def _handle_match(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Handle MATCH operations."""
        # Simple matching simulation
        results = []

        # If specific parameters provided, try to find matching nodes
        if parameters:
            for _node_id, node_data in self.driver._nodes.items():
                match = True
                for key, value in parameters.items():
                    if key not in node_data or node_data[key] != value:
                        match = False
                        break
                if match:
                    results.append(node_data)
                    self.driver.metrics.cache_hits += 1
                else:
                    self.driver.metrics.cache_misses += 1

        # If no specific matches, return sample data for testing
        if not results and not parameters:
            results = [{"sample": "data", "query": "match"}]

        return MockNeo4jResult(results)

    def _handle_match_sync(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Synchronous MATCH handler."""
        results = []

        if parameters:
            for _node_id, node_data in self.driver._nodes.items():
                match = True
                for key, value in parameters.items():
                    if key not in node_data or node_data[key] != value:
                        match = False
                        break
                if match:
                    results.append(node_data)
                    self.driver.metrics.cache_hits += 1
                else:
                    self.driver.metrics.cache_misses += 1

        if not results and not parameters:
            results = [{"sample": "data", "query": "match"}]

        return MockNeo4jResult(results)

    async def _handle_merge(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Handle MERGE operations (CREATE if not exists)."""
        # Check if node exists
        existing = await self._handle_match(query, parameters)
        if existing.records:
            return existing
        else:
            return await self._handle_create(query, parameters)

    def _handle_merge_sync(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Synchronous MERGE handler."""
        existing = self._handle_match_sync(query, parameters)
        if existing.records:
            return existing
        else:
            return self._handle_create_sync(query, parameters)

    async def _handle_delete(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Handle DELETE operations."""
        deleted_count = 0
        nodes_to_delete = []

        # Find nodes to delete based on parameters
        if parameters:
            for node_id, node_data in self.driver._nodes.items():
                match = True
                for key, value in parameters.items():
                    if key not in node_data or node_data[key] != value:
                        match = False
                        break
                if match:
                    nodes_to_delete.append(node_id)

        # Delete the nodes
        for node_id in nodes_to_delete:
            if node_id in self.driver._nodes:
                del self.driver._nodes[node_id]
                deleted_count += 1

                # Remove from indexes
                for _label, node_set in self.driver._indexes.items():
                    node_set.discard(node_id)

        return MockNeo4jResult([{"deleted": deleted_count}])

    def _handle_delete_sync(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Synchronous DELETE handler."""
        deleted_count = 0
        nodes_to_delete = []

        if parameters:
            for node_id, node_data in self.driver._nodes.items():
                match = True
                for key, value in parameters.items():
                    if key not in node_data or node_data[key] != value:
                        match = False
                        break
                if match:
                    nodes_to_delete.append(node_id)

        for node_id in nodes_to_delete:
            if node_id in self.driver._nodes:
                del self.driver._nodes[node_id]
                deleted_count += 1

                for _label, node_set in self.driver._indexes.items():
                    node_set.discard(node_id)

        return MockNeo4jResult([{"deleted": deleted_count}])

    async def _handle_return(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Handle standalone RETURN operations."""
        # Simple return value simulation
        if parameters:
            return MockNeo4jResult([parameters])
        else:
            return MockNeo4jResult([{"returned": 1}])

    def _handle_return_sync(
        self, query: str, parameters: dict[str, Any]
    ) -> "MockNeo4jResult":
        """Synchronous RETURN handler."""
        if parameters:
            return MockNeo4jResult([parameters])
        else:
            return MockNeo4jResult([{"returned": 1}])


class MockNeo4jResult:
    """Enhanced Mock Neo4j query result with realistic behavior."""

    def __init__(self, records: list[dict[str, Any]]):
        self.records = records
        self._consumed = False
        self._current_index = 0

    def single(self) -> dict[str, Any] | None:
        """Return single record or None."""
        if not self.records:
            return None
        if len(self.records) > 1:
            logger.warning("Multiple records found, returning first one")
        return self.records[0]

    def data(self) -> list[dict[str, Any]]:
        """Return all records as list of dictionaries."""
        return list(self.records)

    def values(self) -> list[list[Any]]:
        """Return all records as list of value lists."""
        return [list(record.values()) for record in self.records]

    def keys(self) -> list[str]:
        """Return keys from first record."""
        if not self.records:
            return []
        return list(self.records[0].keys())

    def consume(self) -> list[dict[str, Any]]:
        """Consume and return all records."""
        self._consumed = True
        return self.records

    def peek(self) -> dict[str, Any] | None:
        """Peek at next record without consuming."""
        if self._current_index < len(self.records):
            return self.records[self._current_index]
        return None

    def __iter__(self):
        """Make result iterable."""
        return iter(self.records)

    def __len__(self):
        """Return number of records."""
        return len(self.records)

    def __bool__(self):
        """Return True if has records."""
        return bool(self.records)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "records": self.records,
            "record_count": len(self.records),
            "consumed": self._consumed,
            "keys": self.keys(),
        }


@dataclass
class MockRedisValue:
    """Enhanced Redis value with expiration and metadata."""

    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)

    def is_expired(self) -> bool:
        """Check if value has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def access(self) -> Any:
        """Access the value and update metadata."""
        if self.is_expired():
            return None
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.value


class MockRedisClient:
    """Enhanced Mock Redis client for development and testing."""

    def __init__(self, config: MockServiceConfig | None = None, **kwargs):
        self.host = kwargs.get("host", "localhost")
        self.port = kwargs.get("port", 6379)
        self.db = kwargs.get("db", 0)
        self.config = config or MockServiceConfig()
        self.metrics = MockServiceMetrics()

        # Enhanced data storage with expiration and metadata
        self._data: dict[str, MockRedisValue] = {}
        self._pubsub_channels: dict[str, list[Any]] = {}
        self.connected = False

        # Background cleanup task
        self._cleanup_task = None

        logger.info(
            f"Enhanced MockRedisClient initialized for {self.host}:{self.port}/{self.db}"
        )

    async def ping(self):
        """Mock ping operation with latency simulation."""
        await self._simulate_operation("ping")
        self.connected = True
        return b"PONG"

    async def get(self, key: str):
        """Enhanced mock get operation with expiration handling."""
        result = await self._simulate_operation("get")
        if result is False:  # Simulated failure
            return None

        if key in self._data:
            redis_value = self._data[key]
            if redis_value.is_expired():
                del self._data[key]
                self.metrics.cache_misses += 1
                return None
            else:
                self.metrics.cache_hits += 1
                return redis_value.access()
        else:
            self.metrics.cache_misses += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ex: int | None = None,
        px: int | None = None,
        nx: bool = False,
        xx: bool = False,
    ):
        """Enhanced mock set operation with expiration and conditions."""
        result = await self._simulate_operation("set")
        if result is False:  # Simulated failure
            return False

        # Handle conditional sets
        if nx and key in self._data and not self._data[key].is_expired():
            return False  # Key exists, nx (not exists) condition failed
        if xx and (key not in self._data or self._data[key].is_expired()):
            return False  # Key doesn't exist, xx (exists) condition failed

        # Calculate expiration
        expires_at = None
        if ex is not None:  # Seconds
            expires_at = datetime.now() + timedelta(seconds=ex)
        elif px is not None:  # Milliseconds
            expires_at = datetime.now() + timedelta(milliseconds=px)
        elif self.config.ttl_seconds > 0:  # Default TTL
            expires_at = datetime.now() + timedelta(seconds=self.config.ttl_seconds)

        # Store value
        self._data[key] = MockRedisValue(value=value, expires_at=expires_at)

        # Cleanup expired keys if storage is getting full
        if len(self._data) > self.config.max_memory_items:
            await self._cleanup_expired()

        return True

    async def delete(self, *keys: str):
        """Enhanced mock delete operation supporting multiple keys."""
        result = await self._simulate_operation("delete")
        if result is False:  # Simulated failure
            return 0

        deleted_count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                deleted_count += 1

        return deleted_count

    async def exists(self, *keys: str):
        """Enhanced mock exists operation supporting multiple keys."""
        result = await self._simulate_operation("exists")
        if result is False:  # Simulated failure
            return 0

        count = 0
        for key in keys:
            if key in self._data and not self._data[key].is_expired():
                count += 1

        return count

    async def expire(self, key: str, seconds: int):
        """Enhanced mock expire operation."""
        result = await self._simulate_operation("expire")
        if result is False:  # Simulated failure
            return False

        if key in self._data and not self._data[key].is_expired():
            self._data[key].expires_at = datetime.now() + timedelta(seconds=seconds)
            return True
        return False

    async def ttl(self, key: str):
        """Get time to live for a key."""
        result = await self._simulate_operation("ttl")
        if result is False:  # Simulated failure
            return -1

        if key not in self._data:
            return -2  # Key doesn't exist

        redis_value = self._data[key]
        if redis_value.expires_at is None:
            return -1  # No expiration set

        if redis_value.is_expired():
            del self._data[key]
            return -2  # Key expired

        remaining = redis_value.expires_at - datetime.now()
        return max(0, int(remaining.total_seconds()))

    async def close(self):
        """Enhanced mock close operation."""
        self.connected = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
        logger.debug("MockRedisClient closed")

    async def _simulate_operation(self, operation: str) -> bool:
        """Simulate operation with latency and failure handling."""
        self.metrics.total_operations += 1
        self.config._update_state() if hasattr(self.config, "_update_state") else None

        # Simulate latency
        if self.config.base_latency_ms > 0:
            latency = max(
                0,
                random.gauss(
                    self.config.base_latency_ms, self.config.latency_variance_ms
                ),
            )
            await asyncio.sleep(latency / 1000.0)
            self.metrics.total_latency_ms += latency

        # Check for failure simulation
        if random.random() < self.config.failure_rate:
            self.metrics.failed_operations += 1
            if self.config.log_operations:
                logger.warning(f"Simulated Redis {operation} failure")
            return False

        self.metrics.successful_operations += 1
        if self.config.log_operations:
            logger.debug(f"Mock Redis {operation} operation")

        return True

    async def _cleanup_expired(self):
        """Clean up expired keys."""
        expired_keys = []
        for key, redis_value in self._data.items():
            if redis_value.is_expired():
                expired_keys.append(key)

        for key in expired_keys:
            del self._data[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired Redis keys")

    def get_metrics(self) -> dict[str, Any]:
        """Get service metrics."""
        return {
            "service": "redis",
            "state": self.config.state.value,
            "metrics": self.metrics.to_dict(),
            "data_stats": {
                "keys": len(self._data),
                "expired_keys": sum(1 for v in self._data.values() if v.is_expired()),
                "channels": len(self._pubsub_channels),
            },
        }


class MockUserRepository:
    """Mock user repository for development and testing."""

    def __init__(self):
        self.users = {}
        self.connected = False
        logger.info("MockUserRepository initialized")

    def connect(self):
        """Mock connect operation."""
        self.connected = True
        logger.debug("MockUserRepository connected")

    def disconnect(self):
        """Mock disconnect operation."""
        self.connected = False
        logger.debug("MockUserRepository disconnected")

    def create_user(self, user) -> bool:
        """Mock user creation."""
        self.users[user.user_id] = user
        logger.debug(f"Mock user created: {user.username}")
        return True

    def get_user_by_username(self, username: str):
        """Mock user retrieval by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def get_user_by_email(self, email: str):
        """Mock user retrieval by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def update_user(self, user) -> bool:
        """Mock user update."""
        if user.user_id in self.users:
            self.users[user.user_id] = user
            logger.debug(f"Mock user updated: {user.username}")
            return True
        return False

    def delete_user(self, user_id: str) -> bool:
        """Mock user deletion."""
        if user_id in self.users:
            del self.users[user_id]
            logger.debug(f"Mock user deleted: {user_id}")
            return True
        return False


def create_mock_neo4j_driver(uri: str, auth: tuple):
    """Create a mock Neo4j driver."""
    return MockNeo4jDriver(uri, auth)


def create_mock_redis_client(**kwargs):
    """Create a mock Redis client."""
    return MockRedisClient(**kwargs)


def create_mock_user_repository():
    """Create a mock user repository."""
    return MockUserRepository()


# Mock service registry for easy access
MOCK_SERVICES = {
    "neo4j_driver": create_mock_neo4j_driver,
    "redis_client": create_mock_redis_client,
    "user_repository": create_mock_user_repository,
}


def get_mock_service(service_name: str, *args, **kwargs):
    """Get a mock service by name."""
    if service_name in MOCK_SERVICES:
        return MOCK_SERVICES[service_name](*args, **kwargs)
    else:
        raise ValueError(f"Unknown mock service: {service_name}")


def is_development_mode() -> bool:
    """Check if we're running in development mode."""
    import os

    return os.getenv("TTA_DEVELOPMENT_MODE", "false").lower() in ("true", "1", "yes")


def should_use_mocks() -> bool:
    """Check if we should use mock services."""
    import os

    return (
        is_development_mode()
        or os.getenv("TTA_USE_MOCKS", "false").lower() in ("true", "1", "yes")
        or os.getenv("TTA_USE_NEO4J", "0") != "1"
    )
