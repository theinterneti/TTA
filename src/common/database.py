"""

# Logseq: [[TTA.dev/Common/Database]]
Async SQLAlchemy 2.0 database utilities for TTA.

Provides an async-first database layer built on SQLAlchemy 2.0 async extensions:
- ``AsyncEngine`` and ``async_sessionmaker`` factory helpers
- ``AsyncSession`` context managers with automatic transaction management
- AUTOCOMMIT execution option for read-only operations
- ``asyncio.gather()``-safe frozen (immutable) result sets
- Convenience helpers for parallel queries
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)


# Base declarative class
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy ORM models in TTA."""


# ---------------------------------------------------------------------------
# Engine factory
# ---------------------------------------------------------------------------


def make_engine(
    url: str,
    *,
    echo: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_pre_ping: bool = True,
) -> AsyncEngine:
    """Create an ``AsyncEngine`` for the given database URL.

    Args:
        url: SQLAlchemy async database URL, e.g.
             ``"sqlite+aiosqlite:///./tta.db"`` or
             ``"postgresql+asyncpg://user:pass@host/db"``.
        echo: When *True*, log all emitted SQL statements.
        pool_size: Number of connections to maintain in the pool.
        max_overflow: Extra connections allowed beyond *pool_size*.
        pool_pre_ping: Verify connections on checkout to detect stale handles.

    Returns:
        A configured :class:`sqlalchemy.ext.asyncio.AsyncEngine`.
    """
    connect_args: dict[str, Any] = {}
    # SQLite requires check_same_thread=False for async usage
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        return create_async_engine(url, echo=echo, connect_args=connect_args)

    return create_async_engine(
        url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        connect_args=connect_args,
    )


# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------


def make_session_factory(
    engine: AsyncEngine,
    *,
    expire_on_commit: bool = False,
) -> async_sessionmaker[AsyncSession]:
    """Return an :class:`~sqlalchemy.ext.asyncio.async_sessionmaker` bound to *engine*.

    ``expire_on_commit=False`` is the recommended default for async usage: it
    prevents implicit lazy loads after ``commit()``, keeping attribute access
    safe outside the session context.

    Args:
        engine: The async engine to bind sessions to.
        expire_on_commit: Whether to expire ORM attributes after ``commit()``.

    Returns:
        A configured :class:`~sqlalchemy.ext.asyncio.async_sessionmaker`.
    """
    return async_sessionmaker(engine, expire_on_commit=expire_on_commit)


# ---------------------------------------------------------------------------
# Session context managers
# ---------------------------------------------------------------------------


@asynccontextmanager
async def session_context(
    factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    """Async context manager that yields a session with an open transaction.

    The transaction is committed on successful exit and rolled back on any
    exception, then the session is closed in both cases.

    Usage::

        async with session_context(Session) as session:
            session.add(SomeModel(...))

    Args:
        factory: The :class:`~sqlalchemy.ext.asyncio.async_sessionmaker` to use.

    Yields:
        An :class:`~sqlalchemy.ext.asyncio.AsyncSession` with an open
        transaction.
    """
    async with factory() as session, session.begin():
        yield session


@asynccontextmanager
async def readonly_session_context(
    factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    """Async context manager that yields a read-only session in AUTOCOMMIT mode.

    AUTOCOMMIT skips the implicit ``BEGIN``/``COMMIT`` round-trips for every
    statement, which improves throughput for pure read queries.  No changes
    should be flushed inside this context.

    Usage::

        async with readonly_session_context(Session) as session:
            result = await session.execute(select(Player))

    Args:
        factory: The :class:`~sqlalchemy.ext.asyncio.async_sessionmaker` to use.

    Yields:
        An :class:`~sqlalchemy.ext.asyncio.AsyncSession` configured with the
        ``AUTOCOMMIT`` execution option.
    """
    async with factory() as session:
        await session.connection(execution_options={"isolation_level": "AUTOCOMMIT"})
        yield session


# ---------------------------------------------------------------------------
# Parallel query helpers
# ---------------------------------------------------------------------------


async def gather_queries(
    *coros: Any,
    return_exceptions: bool = False,
) -> list[Any]:
    """Execute multiple async queries concurrently via :func:`asyncio.gather`.

    Each *coro* should be an awaitable produced by a session query call.
    Results are returned in the same order as the input coroutines.

    Args:
        *coros: Awaitable query coroutines to run in parallel.
        return_exceptions: When *True*, exceptions are returned as results
            rather than propagated.

    Returns:
        A list of resolved results in the same order as *coros*.

    Example::

        players, worlds = await gather_queries(
            session.scalars(select(Player)),
            session.scalars(select(World)),
        )
    """
    return list(await asyncio.gather(*coros, return_exceptions=return_exceptions))


# ---------------------------------------------------------------------------
# Frozen (immutable) result helper
# ---------------------------------------------------------------------------


def freeze_result[T](rows: Sequence[T]) -> tuple[T, ...]:
    """Convert a mutable result sequence to an immutable tuple.

    SQLAlchemy ``ScalarResult`` and ``Result`` objects are not safe to share
    across coroutines after the session has been closed.  Freezing the rows
    into a plain :class:`tuple` makes them safe to pass between tasks.

    Args:
        rows: An iterable of ORM instances or row objects.

    Returns:
        An immutable :class:`tuple` of the same rows.
    """
    return tuple(rows)


# ---------------------------------------------------------------------------
# Low-level connection helper (DDL / raw SQL)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def connection_context(
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncConnection]:
    """Async context manager that yields a raw ``AsyncConnection``.

    Useful for DDL operations (``CREATE TABLE``, schema migrations) or raw
    SQL that bypasses the ORM session layer.

    Args:
        engine: The async engine to connect with.

    Yields:
        An :class:`~sqlalchemy.ext.asyncio.AsyncConnection`.
    """
    async with engine.begin() as conn:
        yield conn


# ---------------------------------------------------------------------------
# Schema initialisation
# ---------------------------------------------------------------------------


async def init_db(engine: AsyncEngine) -> None:
    """Create all tables defined in :class:`Base` metadata.

    This is a convenience wrapper around
    ``Base.metadata.create_all(connection)``.  In production, prefer
    Alembic migrations over this helper.

    Args:
        engine: The async engine to use for DDL.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialised")


async def drop_db(engine: AsyncEngine) -> None:
    """Drop all tables defined in :class:`Base` metadata.

    Intended for test tear-down only — use with caution in production.

    Args:
        engine: The async engine to use for DDL.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Database schema dropped")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


async def check_database_health(engine: AsyncEngine) -> dict[str, Any]:
    """Ping the database and return basic health information.

    Args:
        engine: The async engine to test.

    Returns:
        A dictionary with keys ``"healthy"`` (bool), ``"url"`` (str), and
        ``"error"`` (str | None).
    """
    url_repr = engine.url.render_as_string(hide_password=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"healthy": True, "url": url_repr, "error": None}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Database health check failed: %s", exc)
        return {"healthy": False, "url": url_repr, "error": str(exc)}
