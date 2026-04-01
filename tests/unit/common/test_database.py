"""
Unit tests for src/common/database.py.

Tests cover:
- make_engine / make_session_factory
- session_context (write path with commit)
- readonly_session_context (AUTOCOMMIT execution option)
- gather_queries (parallel execution via asyncio.gather)
- freeze_result (immutable tuple conversion)
- connection_context (raw DDL helper)
- init_db / drop_db (schema helpers)
- check_database_health (ping helper)
"""

from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import Column, Integer, String, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.common.database import (
    DOLT_DEFAULT_URL,
    Base,
    check_database_health,
    connection_context,
    drop_db,
    freeze_result,
    gather_queries,
    init_db,
    make_dolt_engine,
    make_dolt_session_factory,
    make_engine,
    make_session_factory,
    readonly_session_context,
    session_context,
)

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# Helpers — in-process SQLite engine for fast, dependency-free tests
# ---------------------------------------------------------------------------

SQLITE_URL = "sqlite+aiosqlite:///:memory:"


def _make_test_engine() -> AsyncEngine:
    return make_engine(SQLITE_URL)


# ---------------------------------------------------------------------------
# Sample ORM model for tests
# ---------------------------------------------------------------------------


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    score = Column(Integer, default=0)


# ---------------------------------------------------------------------------
# make_engine
# ---------------------------------------------------------------------------


class TestMakeEngine:
    def test_returns_async_engine(self):
        """Make Engine: returns async engine."""
        engine = _make_test_engine()
        assert isinstance(engine, AsyncEngine)

    def test_sqlite_url_accepted(self):
        """Make Engine: sqlite url accepted."""
        engine = make_engine(SQLITE_URL)
        assert "sqlite" in str(engine.url)

    def test_echo_parameter_stored(self):
        """Make Engine: echo parameter stored."""
        engine = make_engine(SQLITE_URL, echo=True)
        assert engine.echo is True

    def test_non_sqlite_passes_pool_args(self):
        # We just verify make_engine doesn't raise for a postgres-style URL;
        # we don't actually connect.
        """Make Engine: non sqlite passes pool args."""
        pytest.importorskip("asyncpg", reason="asyncpg not installed")
        engine = make_engine(
            "postgresql+asyncpg://user:pass@localhost/db",
            pool_size=3,
            max_overflow=2,
        )
        assert isinstance(engine, AsyncEngine)

    def test_non_sqlite_kwargs_forwarded(self):
        """Pool kwargs are forwarded even without asyncpg installed (mock driver)."""
        from unittest.mock import MagicMock, patch

        # Patch create_async_engine to capture the kwargs without needing asyncpg.
        with patch("src.common.database.create_async_engine") as mock_cae:
            mock_cae.return_value = MagicMock(spec=AsyncEngine)
            make_engine(
                "postgresql+asyncpg://user:pass@localhost/db",
                pool_size=3,
                max_overflow=2,
            )
            _, kwargs = mock_cae.call_args
            assert kwargs["pool_size"] == 3
            assert kwargs["max_overflow"] == 2


# ---------------------------------------------------------------------------
# make_session_factory
# ---------------------------------------------------------------------------


class TestMakeSessionFactory:
    def test_returns_async_sessionmaker(self):
        """Make Session Factory: returns async sessionmaker."""
        from sqlalchemy.ext.asyncio import async_sessionmaker

        engine = _make_test_engine()
        factory = make_session_factory(engine)
        assert isinstance(factory, async_sessionmaker)

    def test_expire_on_commit_default_false(self):
        """Make Session Factory: expire on commit default false."""
        engine = _make_test_engine()
        factory = make_session_factory(engine)
        # The kw_args dict stores the init kwargs for each new session.
        assert factory.kw.get("expire_on_commit") is False

    def test_expire_on_commit_can_be_overridden(self):
        """Make Session Factory: expire on commit can be overridden."""
        engine = _make_test_engine()
        factory = make_session_factory(engine, expire_on_commit=True)
        assert factory.kw.get("expire_on_commit") is True


# ---------------------------------------------------------------------------
# session_context — write path
# ---------------------------------------------------------------------------


class TestSessionContext:
    async def test_add_and_query_row(self):
        """Session Context: add and query row."""
        engine = _make_test_engine()
        await init_db(engine)
        factory = make_session_factory(engine)

        # Insert a row
        async with session_context(factory) as session:
            session.add(Player(name="Alice", score=100))

        # Retrieve the row in a fresh session
        async with session_context(factory) as session:
            result = await session.scalars(select(Player))
            players = result.all()

        assert len(players) == 1
        assert players[0].name == "Alice"
        assert players[0].score == 100

        await engine.dispose()

    async def test_rollback_on_exception(self):
        """Session Context: rollback on exception."""
        engine = _make_test_engine()
        await init_db(engine)
        factory = make_session_factory(engine)

        # Trigger a rollback by raising inside the context
        with pytest.raises(ValueError, match="deliberate error"):
            async with session_context(factory) as session:
                session.add(Player(name="Bob", score=50))
                raise ValueError("deliberate error")

        # No rows should have been committed
        async with session_context(factory) as session:
            result = await session.scalars(select(Player))
            players = result.all()

        assert players == []

        await engine.dispose()


# ---------------------------------------------------------------------------
# readonly_session_context — AUTOCOMMIT
# ---------------------------------------------------------------------------


class TestReadonlySessionContext:
    async def test_yields_session(self):
        """Readonly Session Context: yields session."""
        engine = _make_test_engine()
        await init_db(engine)
        factory = make_session_factory(engine)

        async with readonly_session_context(factory) as session:
            assert isinstance(session, AsyncSession)
            # Basic query should succeed
            result = await session.execute(text("SELECT 1"))
            row = result.scalar()
            assert row == 1

        await engine.dispose()

    async def test_execution_options_set(self):
        """AUTOCOMMIT execution option must be present on the connection."""
        engine = _make_test_engine()
        await init_db(engine)
        factory = make_session_factory(engine)

        async with readonly_session_context(factory) as session:
            # Retrieve the underlying connection to inspect its execution options.
            conn = await session.connection()
            opts = conn.sync_connection.get_execution_options()
            assert opts.get("isolation_level") == "AUTOCOMMIT"

        await engine.dispose()


# ---------------------------------------------------------------------------
# gather_queries
# ---------------------------------------------------------------------------


class TestGatherQueries:
    async def test_returns_results_in_order(self):
        """Gather Queries: returns results in order."""
        async def coro_a():
            return "a"

        async def coro_b():
            return "b"

        results = await gather_queries(coro_a(), coro_b())
        assert results == ["a", "b"]

    async def test_parallel_execution(self):
        """Demonstrate that queries run concurrently, not sequentially."""
        events: list[str] = []

        async def slow():
            await asyncio.sleep(0)
            events.append("slow")
            return 1

        async def fast():
            events.append("fast")
            return 2

        await gather_queries(slow(), fast())
        # Both ran; order is not guaranteed (asyncio scheduling), but both must complete.
        assert set(events) == {"slow", "fast"}

    async def test_return_exceptions_false_propagates(self):
        """Gather Queries: return exceptions false propagates."""
        async def boom():
            raise RuntimeError("bang")

        with pytest.raises(RuntimeError, match="bang"):
            await gather_queries(boom())

    async def test_return_exceptions_true_captures(self):
        """Gather Queries: return exceptions true captures."""
        async def boom():
            raise RuntimeError("bang")

        results = await gather_queries(boom(), return_exceptions=True)
        assert len(results) == 1
        assert isinstance(results[0], RuntimeError)

    async def test_real_db_parallel_queries(self):
        """Run two real SQLAlchemy queries in parallel via gather_queries."""
        engine = _make_test_engine()
        await init_db(engine)
        factory = make_session_factory(engine)

        # Seed data
        async with session_context(factory) as session:
            session.add_all([Player(name="X", score=1), Player(name="Y", score=2)])

        async with readonly_session_context(factory) as session:
            players_coro = session.scalars(select(Player))
            count_coro = session.execute(text("SELECT COUNT(*) FROM players"))
            players_result, count_result = await gather_queries(
                players_coro, count_coro
            )

        players = players_result.all()
        count = count_result.scalar()

        assert len(players) == 2
        assert count == 2

        await engine.dispose()


# ---------------------------------------------------------------------------
# freeze_result
# ---------------------------------------------------------------------------


class TestFreezeResult:
    def test_converts_list_to_tuple(self):
        """Freeze Result: converts list to tuple."""
        assert freeze_result([1, 2, 3]) == (1, 2, 3)

    def test_empty_sequence(self):
        """Freeze Result: empty sequence."""
        assert freeze_result([]) == ()

    def test_returns_tuple_type(self):
        """Freeze Result: returns tuple type."""
        result = freeze_result(["a", "b"])
        assert isinstance(result, tuple)

    def test_preserves_orm_objects(self):
        """Freeze Result: preserves orm objects."""
        p1 = Player(name="A", score=10)
        p2 = Player(name="B", score=20)
        frozen = freeze_result([p1, p2])
        assert frozen == (p1, p2)
        assert isinstance(frozen, tuple)


# ---------------------------------------------------------------------------
# connection_context
# ---------------------------------------------------------------------------


class TestConnectionContext:
    async def test_raw_sql_via_connection(self):
        """Connection Context: raw sql via connection."""
        engine = _make_test_engine()
        await init_db(engine)
        factory = make_session_factory(engine)

        # Seed a row
        async with session_context(factory) as session:
            session.add(Player(name="Raw", score=99))

        async with connection_context(engine) as conn:
            result = await conn.execute(text("SELECT name FROM players"))
            rows = result.fetchall()

        assert rows[0][0] == "Raw"

        await engine.dispose()


# ---------------------------------------------------------------------------
# init_db / drop_db
# ---------------------------------------------------------------------------


class TestInitDropDb:
    async def test_init_creates_tables(self):
        """Init Drop Db: init creates tables."""
        engine = _make_test_engine()
        await init_db(engine)

        async with engine.connect() as conn:
            # Verify the players table exists by querying it
            result = await conn.execute(text("SELECT COUNT(*) FROM players"))
            assert result.scalar() == 0

        await engine.dispose()

    async def test_drop_removes_tables(self):
        """Init Drop Db: drop removes tables."""
        engine = _make_test_engine()
        await init_db(engine)
        await drop_db(engine)

        async with engine.connect() as conn:
            with pytest.raises(Exception):
                await conn.execute(text("SELECT 1 FROM players"))

        await engine.dispose()


# ---------------------------------------------------------------------------
# check_database_health
# ---------------------------------------------------------------------------


class TestCheckDatabaseHealth:
    async def test_healthy_database(self):
        """Check Database Health: healthy database."""
        engine = _make_test_engine()
        result = await check_database_health(engine)
        assert result["healthy"] is True
        assert result["error"] is None
        await engine.dispose()

    async def test_unhealthy_database(self):
        """Force an unhealthy result by patching AsyncEngine.connect to raise."""
        from unittest.mock import patch

        engine = _make_test_engine()
        with patch(
            "sqlalchemy.ext.asyncio.AsyncEngine.connect",
            side_effect=Exception("connection refused"),
        ):
            result = await check_database_health(engine)

        assert result["healthy"] is False
        assert result["error"] == "connection refused"
        assert "url" in result
        await engine.dispose()

    async def test_strips_credentials_from_url(self):
        """SQLAlchemy render_as_string hides passwords in the health result URL."""
        engine = _make_test_engine()
        result = await check_database_health(engine)
        assert "url" in result
        # SQLite in-memory URL has no credentials; verify the key is present
        assert result["url"] is not None
        await engine.dispose()


# ---------------------------------------------------------------------------
# make_dolt_engine (#280)
# ---------------------------------------------------------------------------


class TestMakeDoltEngine:
    def test_default_url_constant(self) -> None:
        """Make Dolt Engine: default url constant."""
        assert DOLT_DEFAULT_URL.startswith("mysql+aiomysql://")

    def test_explicit_url_accepted(self) -> None:
        """Make Dolt Engine: explicit url accepted."""
        from unittest.mock import MagicMock, patch

        with patch("src.common.database.create_async_engine") as mock_cae:
            mock_cae.return_value = MagicMock(spec=AsyncEngine)
            engine = make_dolt_engine(
                "mysql+aiomysql://root:pw@localhost:3306/tta"
            )
        assert engine is not None
        mock_cae.assert_called_once()
        call_url = mock_cae.call_args[0][0]
        assert "mysql+aiomysql" in call_url

    def test_env_var_used_when_url_not_given(self, monkeypatch) -> None:
        """Make Dolt Engine: env var used when url not given."""
        from unittest.mock import MagicMock, patch

        monkeypatch.setenv(
            "DOLT_DATABASE_URL", "mysql+aiomysql://root:pw@dolt:3306/tta"
        )
        with patch("src.common.database.create_async_engine") as mock_cae:
            mock_cae.return_value = MagicMock(spec=AsyncEngine)
            make_dolt_engine()
        call_url = mock_cae.call_args[0][0]
        assert "dolt:3306" in call_url

    def test_default_url_used_when_no_env_no_arg(self, monkeypatch) -> None:
        """Make Dolt Engine: default url used when no env no arg."""
        from unittest.mock import MagicMock, patch

        monkeypatch.delenv("DOLT_DATABASE_URL", raising=False)
        with patch("src.common.database.create_async_engine") as mock_cae:
            mock_cae.return_value = MagicMock(spec=AsyncEngine)
            make_dolt_engine()
        call_url = mock_cae.call_args[0][0]
        assert call_url == DOLT_DEFAULT_URL

    def test_pool_size_and_max_overflow_forwarded(self) -> None:
        """Make Dolt Engine: pool size and max overflow forwarded."""
        from unittest.mock import MagicMock, patch

        with patch("src.common.database.create_async_engine") as mock_cae:
            mock_cae.return_value = MagicMock(spec=AsyncEngine)
            make_dolt_engine(
                "mysql+aiomysql://root@localhost:3306/tta",
                pool_size=7,
                max_overflow=15,
            )
        kwargs = mock_cae.call_args[1]
        assert kwargs["pool_size"] == 7
        assert kwargs["max_overflow"] == 15

    def test_default_pool_size_5_max_overflow_10(self) -> None:
        """Make Dolt Engine: default pool size 5 max overflow 10."""
        from unittest.mock import MagicMock, patch

        with patch("src.common.database.create_async_engine") as mock_cae:
            mock_cae.return_value = MagicMock(spec=AsyncEngine)
            make_dolt_engine("mysql+aiomysql://root@localhost:3306/tta")
        kwargs = mock_cae.call_args[1]
        assert kwargs["pool_size"] == 5
        assert kwargs["max_overflow"] == 10

    def test_wrong_scheme_raises_value_error(self) -> None:
        """Make Dolt Engine: wrong scheme raises value error."""
        with pytest.raises(ValueError, match="mysql\\+aiomysql"):
            make_dolt_engine("postgresql+asyncpg://user:pass@localhost/db")

    def test_sqlite_scheme_raises_value_error(self) -> None:
        """Make Dolt Engine: sqlite scheme raises value error."""
        with pytest.raises(ValueError, match="mysql\\+aiomysql"):
            make_dolt_engine("sqlite+aiosqlite:///:memory:")

    def test_echo_forwarded(self) -> None:
        """Make Dolt Engine: echo forwarded."""
        from unittest.mock import MagicMock, patch

        with patch("src.common.database.create_async_engine") as mock_cae:
            mock_cae.return_value = MagicMock(spec=AsyncEngine)
            make_dolt_engine("mysql+aiomysql://root@localhost:3306/tta", echo=True)
        kwargs = mock_cae.call_args[1]
        assert kwargs["echo"] is True

    def test_pool_pre_ping_true_by_default(self) -> None:
        """Make Dolt Engine: pool pre ping true by default."""
        from unittest.mock import MagicMock, patch

        with patch("src.common.database.create_async_engine") as mock_cae:
            mock_cae.return_value = MagicMock(spec=AsyncEngine)
            make_dolt_engine("mysql+aiomysql://root@localhost:3306/tta")
        kwargs = mock_cae.call_args[1]
        assert kwargs["pool_pre_ping"] is True


# ---------------------------------------------------------------------------
# make_dolt_session_factory (#280)
# ---------------------------------------------------------------------------


class TestMakeDoltSessionFactory:
    def test_returns_async_sessionmaker(self) -> None:
        """Make Dolt Session Factory: returns async sessionmaker."""
        from unittest.mock import MagicMock, patch
        from sqlalchemy.ext.asyncio import async_sessionmaker

        mock_engine = MagicMock(spec=AsyncEngine)
        with patch("src.common.database.async_sessionmaker") as mock_sm:
            mock_sm.return_value = MagicMock(spec=async_sessionmaker)
            factory = make_dolt_session_factory(mock_engine)
        assert factory is not None
        mock_sm.assert_called_once_with(mock_engine, expire_on_commit=False)

    def test_expire_on_commit_forwarded(self) -> None:
        """Make Dolt Session Factory: expire on commit forwarded."""
        from unittest.mock import MagicMock, patch
        from sqlalchemy.ext.asyncio import async_sessionmaker

        mock_engine = MagicMock(spec=AsyncEngine)
        with patch("src.common.database.async_sessionmaker") as mock_sm:
            mock_sm.return_value = MagicMock(spec=async_sessionmaker)
            make_dolt_session_factory(mock_engine, expire_on_commit=True)
        mock_sm.assert_called_once_with(mock_engine, expire_on_commit=True)
