# Database Stack Audit: SQLAlchemy, Neo4j, Redis, Dolt

**Issue**: #(Audit Database Stack)
**Date**: 2026-03-04
**Priority**: High
**Effort Estimate**: 4 hours
**Status**: Complete

---

## Executive Summary

This document audits TTA's database dependencies (SQLAlchemy, Neo4j, Redis) and evaluates Dolt as a new addition to the stack. It covers Python 3.14 compatibility, async improvements, protocol upgrades, version fragmentation across the repository, and migration effort.

**Key findings:**

- All three existing database libraries have current versions that support Python 3.14.
- The repository has significant **version fragmentation**: 5+ different Neo4j and Redis versions are pinned across various requirements files.
- Dolt integrates via MySQL-compatible protocol using SQLAlchemy — no dedicated Python client needed (DoltPy is deprecated).
- RESP3 protocol adoption for Redis is recommended for richer type support and performance gains.
- Migration effort is **low** for version bumps and **medium** for Dolt integration.

---

## 1. Compatibility Matrix

### Current vs Latest Versions

| Dependency | pyproject.toml (min) | Resolved (uv.lock) | Latest Stable | Python 3.14 | Status |
|---|---|---|---|---|---|
| SQLAlchemy | `>=2.0.0` | 2.0.46 | **2.0.48** | ✅ (since 2.0.41) | Update min to `>=2.0.46` |
| Neo4j | `>=5.8.0` | 6.1.0 | **6.1.0** | ✅ | Update min to `>=6.0.0` |
| Redis (redis-py) | `>=6.0.0` | 7.2.0 | **7.2.1** | ✅ | Update min to `>=7.0.0` |
| types-redis | `>=4.6.0` | 4.6.0.20241004 | 4.6.0.20241004 | ✅ | No change needed |
| aiomysql | `>=0.3.2` | 0.3.2 | 0.3.2 | ✅ | No change needed |
| Dolt (via MySQL) | N/A | N/A | Server 1.x | ✅ (via connectors) | New addition |

### Version Fragmentation Across Repository

The repository has inconsistent database dependency versions across multiple requirements files:

| File | Neo4j | Redis | SQLAlchemy |
|---|---|---|---|
| `pyproject.toml` (min) | >=5.8.0 | >=6.0.0 | >=2.0.0 |
| `requirements.docker.txt` (resolved) | 6.1.0 | 7.2.0 | 2.0.46 |
| `testing/requirements-testing.txt` | 5.14.1 | 5.0.1 | — |
| `monitoring/health-check-service/requirements.txt` | 5.15.0 | 5.0.1 | — |
| `src/analytics/requirements.txt` | — | 5.0.1 | 2.0.23 |
| `src/player_experience/api/requirements.txt` | 5.15.0 | 5.0.1 | — |

**⚠️ Risk**: Testing and monitoring environments use Redis 5.0.1 while production resolves to 7.2.0. This 2-major-version gap may mask compatibility issues. Similarly, Neo4j ranges from 5.14.1 to 6.1.0 — a major version boundary.

**Recommendation**: Consolidate all requirements files to use the `pyproject.toml` version specifiers as the single source of truth. Scattered `requirements.txt` files should either be removed or generated from pyproject.toml.

---

## 2. SQLAlchemy 2.0.46+ Async ORM Improvements

### Current State

TTA uses `SQLAlchemy>=2.0.0` with the actual resolved version being **2.0.46**. The latest available is **2.0.48** (released March 2, 2026).

### Key Improvements (2.0.0 → 2.0.48)

#### Python 3.14 Compatibility
- **2.0.41**: Initial Python 3.14 beta support, including new language feature adaptations.
- **2.0.44**: Greenlet wheels available for Python 3.14, unblocking asyncio support.
- **2.0.47**: PEP 649 (deferred evaluation of annotations) fixes for ORM mappings on Python 3.14.
- **2.0.48**: Concurrency fix for custom "on connect" routines — improves async stability.

#### Async ORM Enhancements
- **Greenlet on 3.14**: As of 2.0.44, `greenlet` is available for Python 3.14, enabling the async bridge that SQLAlchemy's `create_async_engine` relies on.
- **Connection stability**: 2.0.48 fixes a shared mutable collection issue in connection arguments that could affect concurrent async connections.
- **Typing improvements**: 2.0.46 adds better type hints for ORM mapped classes and aliased entities in result rows — better IDE support for async code.

#### Dialect Improvements
- PostgreSQL: Better unicode support, JSONB operator fixes.
- MariaDB/MySQL: Improved compatibility — relevant for Dolt integration.
- SQLite: Various fixes.

### Recommendation

Update minimum to `>=2.0.46` (current resolved). The jump from 2.0.0 to 2.0.46 is **fully backward-compatible** within the 2.0.x line — no API changes, only bug fixes and improvements.

### SQLAlchemy 2.1 (Beta)

SQLAlchemy 2.1.0b1 was released January 2026. Notable features:
- Template string support for queries.
- Further Python 3.14 improvements.
- Not recommended for production yet, but worth tracking.

---

## 3. Neo4j Driver Python 3.14 Support

### Current State

TTA specifies `neo4j>=5.8.0` but resolves to **6.1.0** (the latest). The `neo4j-driver` package name was deprecated in favor of `neo4j` since 6.0.0.

### Key Changes (5.8.0 → 6.1.0)

#### Major Version Boundary (5.x → 6.x)
- **Package rename**: `neo4j-driver` → `neo4j` (import path unchanged).
- **Python support**: 6.1.0 supports Python 3.10, 3.11, 3.12, 3.13, **3.14**.
- **Server compatibility**: Works with Neo4j server 4.4.x, 5.x.
- **Optional Rust extensions**: Available for performance, not required.

#### Python 3.14 Compatibility
- ✅ Fully supported in Neo4j driver 6.1.0.
- Tested against Python 3.14 release candidates.

#### Breaking Changes (5.x → 6.x)
- Some deprecated APIs removed — need to verify TTA's usage.
- Connection configuration changes may apply.
- The TTA codebase already resolves to 6.1.0, indicating compatibility.

### Recommendation

Update minimum to `>=6.0.0` to match actual resolved version and get Python 3.14 support. Since the lock file already resolves to 6.1.0 and tests pass, the migration is already effectively done.

---

## 4. Redis RESP3 Protocol Benefits

### Current State

TTA uses `redis>=6.0.0` and resolves to **7.2.0**. RESP3 has been supported since redis-py 5.0 but is not currently enabled in TTA.

### RESP3 vs RESP2 Comparison

| Feature | RESP2 (Current) | RESP3 |
|---|---|---|
| Data types | Strings, arrays, integers, errors, bulk strings | + Maps, sets, doubles, booleans, big numbers, verbatim strings, push data |
| Wire format | All responses as arrays/strings | Native typed responses (~50% smaller for maps) |
| Client-side caching | Not supported | ✅ Push notifications for invalidation |
| Boolean values | Returned as integers (0/1) | Native boolean type |
| Map responses | Flat arrays requiring client parsing | Native map type |
| Push notifications | Not supported | ✅ Server-initiated messages |

### Benefits for TTA

1. **Performance**: Map-type responses are ~50% smaller on the wire. Relevant for TTA's Redis-based message coordination where `RedisMessageCoordinator` exchanges structured data between agents.

2. **Type safety**: Native booleans and maps reduce parsing overhead and bugs. Currently TTA likely converts `0`/`1` to `True`/`False` manually.

3. **Client-side caching**: Push-based cache invalidation enables efficient local caching of frequently-read keys (player state, session data, circuit breaker state).

4. **Push notifications**: Server-initiated messages enable real-time event streaming — useful for agent-to-agent communication without polling.

### Enabling RESP3

```python
import redis

# Enable RESP3
r = redis.Redis(host='localhost', port=6379, db=0, protocol=3)

# Or via URL
r = redis.from_url("redis://localhost:6379?protocol=3")
```

### Recommendation

1. Update minimum to `>=7.0.0` to match resolved version.
2. Enable RESP3 (`protocol=3`) in `RedisMessageCoordinator` and other Redis clients.
3. Install `hiredis` optional dependency for faster parsing: `redis[hiredis]>=7.0.0`.
4. Test thoroughly — some response shapes change with RESP3 (maps instead of flat arrays).

---

## 5. Dolt Integration Path

### Overview

Dolt is a MySQL-compatible, version-controlled database that brings Git-like operations (branching, merging, committing) to SQL tables. TTA's architecture document mentions migrating to Dolt where "branch = universe, commit = game state."

### Integration Strategy

Since DoltPy (the dedicated Python client) is **deprecated** (last release: v2.0.14, January 2023), the recommended approach is:

1. **Run Dolt as a MySQL server**: `dolt sql-server`
2. **Connect via SQLAlchemy**: Using MySQL dialect (already in TTA's dependency stack via `aiomysql`)
3. **Version control via SQL**: Use Dolt's stored procedures (`CALL DOLT_COMMIT(...)`, `CALL DOLT_BRANCH(...)`, etc.)

### Connection Example

```python
from sqlalchemy import create_engine

# Dolt exposes MySQL-compatible protocol
engine = create_engine('mysql+aiomysql://root@localhost:3306/tta_dev')

# Standard SQLAlchemy ORM operations work
with engine.connect() as conn:
    # Regular SQL
    result = conn.execute(text("SELECT * FROM players"))

    # Dolt version control via SQL procedures
    conn.execute(text("CALL DOLT_COMMIT('-am', 'Save player state')"))
    conn.execute(text("CALL DOLT_BRANCH('universe_branch_42')"))
    conn.execute(text("CALL DOLT_CHECKOUT('universe_branch_42')"))
```

### TTA-Specific Benefits

| Feature | Neo4j (Current) | Dolt (Addition) |
|---|---|---|
| **Branching universes** | Manual graph traversal | Native `DOLT_BRANCH()` — Git-like |
| **Game state snapshots** | Custom serialization | Native `DOLT_COMMIT()` — automatic |
| **Time travel queries** | Not built-in | `AS OF 'commit_hash'` syntax |
| **Merge narratives** | Complex graph operations | `DOLT_MERGE()` with conflict resolution |
| **Diff between states** | Custom comparison logic | `DOLT_DIFF()` built-in |
| **Audit trail** | Manual logging | Automatic commit history |

### Dependencies Required

No new Python packages needed. Dolt connects through MySQL protocol using existing `aiomysql` + `SQLAlchemy`:

```toml
# Already in pyproject.toml
"SQLAlchemy>=2.0.46"
"aiomysql>=0.3.2"
```

### Docker Integration

```yaml
# docker-compose addition for Dolt
services:
  dolt:
    image: dolthub/dolt-sql-server:latest
    ports:
      - "3306:3306"
    volumes:
      - dolt_data:/var/lib/dolt
    environment:
      DOLT_ROOT_PASSWORD: "${DOLT_PASSWORD}"
```

---

## 6. Migration Effort Estimate

### Version Bumps (Low Effort — 2 hours)

| Task | Effort | Risk |
|---|---|---|
| Update pyproject.toml version specifiers | 15 min | Low — already resolved to these versions |
| Update scattered requirements.txt files | 30 min | Low — align with pyproject.toml |
| Run full test suite to verify | 30 min | Low — uv.lock already resolves correctly |
| Update documentation | 30 min | None |
| **Total** | **~2 hours** | **Low** |

### RESP3 Protocol Migration (Medium Effort — 4 hours)

| Task | Effort | Risk |
|---|---|---|
| Add `protocol=3` to Redis client initialization | 30 min | Low |
| Update `RedisMessageCoordinator` for RESP3 types | 1 hour | Medium — response shape changes |
| Update circuit breaker Redis persistence | 30 min | Medium |
| Update tests for new response types | 1 hour | Low |
| Performance benchmarking | 1 hour | None |
| **Total** | **~4 hours** | **Medium** |

### Dolt Integration (Medium-High Effort — 8-12 hours)

| Task | Effort | Risk |
|---|---|---|
| Docker Compose configuration | 1 hour | Low |
| SQLAlchemy engine configuration for Dolt | 1 hour | Low |
| Schema design (players, worlds, narratives) | 2 hours | Medium |
| Version control wrapper (commit, branch, merge) | 3 hours | Medium |
| Migration of game state from Neo4j | 2-4 hours | Medium-High |
| Integration tests | 2 hours | Low |
| **Total** | **~8-12 hours** | **Medium-High** |

### Requirements File Consolidation (Low Effort — 1 hour)

| Task | Effort | Risk |
|---|---|---|
| Audit all requirements.txt files | 15 min | None |
| Remove or update stale requirements | 30 min | Low |
| Document single-source-of-truth approach | 15 min | None |
| **Total** | **~1 hour** | **Low** |

---

## 7. Recommendations Summary

### Immediate Actions (This PR)

1. ✅ Update `pyproject.toml` minimum version specifiers:
   - `SQLAlchemy>=2.0.46` (from `>=2.0.0`)
   - `neo4j>=6.0.0` (from `>=5.8.0`)
   - `redis>=7.0.0` (from `>=6.0.0`)

2. ✅ Update scattered requirements files for consistency.

### Short-Term (Next Sprint)

3. Enable RESP3 protocol in Redis clients.
4. Add `redis[hiredis]` for faster parsing.
5. Consolidate requirements files to derive from pyproject.toml.

### Medium-Term (Post-MVP)

6. Integrate Dolt via Docker Compose and SQLAlchemy MySQL dialect.
7. Design Dolt schema for branching universes and game state.
8. Implement version control wrapper for game state operations.

---

## 8. Resources

- [SQLAlchemy 2.0 Changelog](https://docs.sqlalchemy.org/en/20/changelog/)
- [SQLAlchemy 2.1 Beta Blog Post](https://www.sqlalchemy.org/blog/2026/01/21/sqlalchemy-2.1.0b1-released/)
- [Neo4j Python Driver 6.x Changelog](https://github.com/neo4j/neo4j-python-driver/wiki/6.x-Changelog)
- [Neo4j Python Driver Docs](https://neo4j.com/docs/api/python-driver/current/)
- [Redis-py Releases](https://github.com/redis/redis-py/releases)
- [RESP3 Protocol Features](https://redis.readthedocs.io/en/v6.3.0/resp3_features.html)
- [Dolt + SQLAlchemy Getting Started](https://www.dolthub.com/blog/2023-07-12-sql-alchemy-getting-started/)
- [Dolt MySQL Connector Guide](https://www.dolthub.com/blog/2024-11-01-dolt-with-mysql-connector-in-python/)
- [Dolt Time Travel with SQLAlchemy](https://www.dolthub.com/blog/2023-04-12-dolt-sqlalchemy/)
