# Redis Session Management Architecture

This document describes the comprehensive Redis-based session management system for the TTA (Therapeutic Text Adventure) gameplay loop.

## Overview

The Redis session management system provides real-time session persistence, caching strategies, and lifecycle management for therapeutic gameplay sessions. It ensures session data is available across server restarts and enables horizontal scaling.

## Core Components

### SessionState Model

The `SessionState` model represents the complete state of a therapeutic gameplay session:

**Core Properties:**
- `session_id`: Unique session identifier
- `user_id`: User identifier
- `state_type`: Current session state (initializing, active, paused, completed, etc.)
- `therapeutic_goals`: List of therapeutic objectives
- `safety_level`: Current safety assessment level

**Gameplay Context:**
- `current_scene_id`: Currently active scene
- `scene_history`: Chronological list of visited scenes
- `choice_history`: Chronological list of user choices
- `narrative_variables`: Dynamic story variables
- `emotional_state`: Current emotional state mapping

**Progress Tracking:**
- `session_metrics`: Performance and engagement metrics
- `progress_snapshots`: Periodic progress measurements
- `character_relationships`: NPC relationship values

**Cache Management:**
- `dirty_fields`: Fields requiring persistence
- `cache_version`: Version for cache invalidation
- `last_persisted`: Last successful persistence timestamp

### Session State Management

#### State Types
- **INITIALIZING**: Session being set up
- **ACTIVE**: Session in progress
- **PAUSED**: Session temporarily suspended
- **TRANSITIONING**: Moving between scenes
- **COMPLETED**: Session finished successfully
- **ERROR**: Session encountered an error
- **EXPIRED**: Session timed out

#### State Transitions
The system enforces valid state transitions with conditions:
- INITIALIZING → ACTIVE (when setup complete)
- ACTIVE → PAUSED (user request or safety concern)
- PAUSED → ACTIVE (resume request, safety cleared)
- ACTIVE → COMPLETED (completion criteria met)
- Any state → ERROR (on system errors)

#### Validation Rules
- Sessions must have valid user IDs
- Completed sessions must have completion timestamps
- Active sessions cannot have crisis safety levels
- Current scenes must exist in scene history

## Caching Strategies

### TTL (Time-To-Live) Cache Strategy

**Features:**
- Automatic expiration based on configurable TTL
- Background cleanup of expired entries
- Configurable maximum cache size
- Metrics tracking for performance monitoring

**Use Cases:**
- Session data with predictable access patterns
- Temporary narrative context
- User preference caching

**Configuration:**
```python
cache = TTLCacheStrategy(
    max_size=1000,
    default_ttl=timedelta(hours=2)
)
```

### LRU (Least Recently Used) Cache Strategy

**Features:**
- Evicts least recently accessed items when full
- Access-time tracking for all entries
- Optimal for frequently accessed data
- Memory-efficient for bounded datasets

**Use Cases:**
- Frequently accessed session data
- User profile information
- Recent interaction history

**Configuration:**
```python
cache = LRUCacheStrategy(max_size=500)
```

### Write-Back Cache Strategy

**Features:**
- Delayed persistence for performance
- Configurable write-back intervals
- Dirty entry tracking
- Batch persistence operations

**Use Cases:**
- High-frequency session updates
- Performance-critical operations
- Bulk data modifications

**Configuration:**
```python
cache = WriteBackCacheStrategy(
    max_size=1000,
    write_back_interval=timedelta(seconds=30)
)
```

### Write-Through Cache Strategy

**Features:**
- Immediate persistence on writes
- Strong consistency guarantees
- Automatic persistence callback integration
- Failure handling and rollback

**Use Cases:**
- Critical session data
- Therapeutic progress tracking
- Safety-critical information

## Redis Integration

### Connection Management

**Features:**
- Connection pooling with configurable pool size
- Automatic retry logic with exponential backoff
- Health check monitoring
- Graceful connection cleanup

**Configuration:**
```python
connection_manager = RedisConnectionManager(
    host="localhost",
    port=6379,
    password="secure_password",
    db=0,
    max_connections=20,
    retry_attempts=3
)
```

### Session Operations

#### Create Session
```python
success = await session_manager.create_session(session_state, ttl=timedelta(hours=24))
```

#### Get Session
```python
session_state = await session_manager.get_session(session_id)
```

#### Update Session
```python
success = await session_manager.update_session(session_state)
```

#### Delete Session
```python
success = await session_manager.delete_session(session_id)
```

### Key Management

**Key Patterns:**
- Sessions: `tta:session:{session_id}`
- Narrative Context: `tta:narrative:{session_id}:{context_type}`
- Progress Data: `tta:progress:{user_id}:{metric_type}`

**TTL Management:**
- Default session TTL: 24 hours
- Narrative context TTL: 4 hours
- Progress cache TTL: 12 hours
- Automatic TTL extension on access

## Specialized Caches

### Narrative Context Cache

**Purpose:** Cache narrative-specific data like character relationships, world state, and story variables.

**Features:**
- Context-type organization
- Automatic timestamping
- Bulk invalidation by session
- Configurable TTL per context type

**Usage:**
```python
await narrative_cache.set_context(
    session_id, "character_relationships", 
    {"alice": 0.8, "bob": 0.3}
)

relationships = await narrative_cache.get_context(
    session_id, "character_relationships"
)
```

### Progress Cache Manager

**Purpose:** Cache therapeutic progress data and metrics for quick access.

**Features:**
- Progress snapshot caching
- Metric aggregation
- Historical data preservation
- Performance optimization for analytics

**Usage:**
```python
await progress_cache.cache_progress_snapshot(
    user_id, {
        "overall_progress": 0.75,
        "skills_developed": ["breathing", "grounding"],
        "milestones_achieved": 3
    }
)
```

## Session Lifecycle Management

### Lifecycle Events
- **session_created**: New session established
- **session_updated**: Session data modified
- **session_expired**: Session reached TTL limit
- **session_deleted**: Session explicitly removed

### Callback System
```python
async def on_session_created(session_id, **kwargs):
    logger.info(f"Session created: {session_id}")

lifecycle_manager.register_callback("session_created", on_session_created)
```

### Automatic Cleanup

**Features:**
- Background cleanup task for expired sessions
- Configurable cleanup intervals
- Metrics tracking for cleanup operations
- Resource optimization

**Configuration:**
```python
lifecycle_manager = SessionLifecycleManager(
    session_manager,
    cleanup_interval=timedelta(minutes=30)
)
lifecycle_manager.start_cleanup_task()
```

## Performance Optimization

### Cache Metrics

**Tracked Metrics:**
- Hit rate and miss rate
- Cache size and utilization
- Eviction and expiration counts
- Average response times

**Monitoring:**
```python
metrics = cache_manager.get_cache_metrics()
print(f"Hit rate: {metrics.hit_rate():.2%}")
print(f"Cache size: {await cache.size()}")
```

### Memory Management

**Strategies:**
- Size-based eviction policies
- Memory usage estimation
- Configurable cache limits
- Automatic cleanup processes

### Connection Optimization

**Features:**
- Connection pooling
- Keep-alive mechanisms
- Timeout configuration
- Resource cleanup

## Error Handling and Recovery

### Connection Failures
- Automatic retry with exponential backoff
- Circuit breaker patterns
- Fallback to local cache
- Health check monitoring

### Data Consistency
- Dirty field tracking
- Atomic operations where possible
- Rollback on persistence failures
- Consistency validation

### Session Recovery
- Session state validation
- Automatic error state recovery
- Data integrity checks
- Graceful degradation

## Security Considerations

### Data Protection
- Sensitive data encryption at rest
- Secure connection protocols (TLS)
- Access control and authentication
- Audit logging for data access

### Session Security
- Session token validation
- TTL-based session expiration
- Secure session invalidation
- Protection against session hijacking

## Integration Points

The Redis session management system integrates with:

- **Neo4j Graph Database**: For persistent narrative and progress data
- **Therapeutic Safety System**: For real-time safety monitoring
- **Agent Orchestration**: For AI-driven session management
- **Progress Monitoring**: For therapeutic effectiveness tracking
- **Analytics Dashboard**: For session insights and reporting

## Configuration Examples

### Production Configuration
```python
# High-availability Redis setup
connection_manager = RedisConnectionManager(
    host="redis-cluster.internal",
    port=6379,
    password=os.getenv("REDIS_PASSWORD"),
    db=0,
    max_connections=50,
    retry_attempts=5
)

# Performance-optimized caching
cache_strategy = LRUCacheStrategy(max_size=10000)
session_manager = SessionCacheManager(redis_manager, cache_strategy)
```

### Development Configuration
```python
# Local Redis setup
connection_manager = RedisConnectionManager(
    host="localhost",
    port=6379,
    db=1,  # Use separate DB for development
    max_connections=10
)

# Simple TTL caching
cache_strategy = TTLCacheStrategy(
    max_size=100,
    default_ttl=timedelta(minutes=30)
)
```

## Testing

### Unit Tests
- Session state model validation
- Cache strategy functionality
- State transition logic
- Dirty field tracking

### Integration Tests
- Redis connection and operations
- Cache performance and eviction
- Session lifecycle management
- Error handling and recovery

### Performance Tests
- Cache hit/miss ratios
- Session operation latency
- Memory usage patterns
- Concurrent session handling

The Redis session management system provides a robust, scalable foundation for therapeutic gameplay sessions with comprehensive caching, lifecycle management, and performance optimization.
