"""
Unit tests for src/common/health_checks.py.

Tests cover:
- HealthCheckResult.to_dict() shape and field serialisation
- HealthChecker.register_check / check_component (unknown, success, exception)
- HealthChecker.check_all and get_system_status aggregation
- Standalone helpers: check_redis_health, check_neo4j_health,
  check_agent_orchestration_health, check_openrouter_health
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.common.health_checks import (
    HealthChecker,
    HealthCheckResult,
    HealthStatus,
    check_agent_orchestration_health,
    check_neo4j_health,
    check_openrouter_health,
    check_redis_health,
    get_health_checker,
)

# ---------------------------------------------------------------------------
# HealthCheckResult
# ---------------------------------------------------------------------------


class TestHealthCheckResult:
    def test_to_dict_shape(self):
        now = datetime(2025, 1, 1, 12, 0, 0)
        result = HealthCheckResult(
            component="redis",
            status=HealthStatus.HEALTHY,
            message="ok",
            details={"version": "7.0"},
            checked_at=now,
            response_time_ms=12.5,
        )
        d = result.to_dict()
        assert d["component"] == "redis"
        assert d["status"] == "healthy"
        assert d["message"] == "ok"
        assert d["details"] == {"version": "7.0"}
        assert d["response_time_ms"] == 12.5
        assert "2025-01-01" in d["checked_at"]

    def test_to_dict_none_fields(self):
        result = HealthCheckResult(
            component="x", status=HealthStatus.UNKNOWN, message="no info"
        )
        d = result.to_dict()
        assert d["details"] == {}
        assert d["checked_at"] is None
        assert d["response_time_ms"] is None

    def test_status_is_strenum(self):
        assert isinstance(HealthStatus.HEALTHY, str)
        assert HealthStatus.HEALTHY == "healthy"


# ---------------------------------------------------------------------------
# HealthChecker
# ---------------------------------------------------------------------------


class TestHealthCheckerRegisterAndCheck:
    async def test_unknown_component_returns_unknown_status(self):
        checker = HealthChecker()
        result = await checker.check_component("nonexistent")
        assert result.status == HealthStatus.UNKNOWN
        assert "nonexistent" in result.message
        assert result.component == "nonexistent"

    async def test_successful_check_sets_response_time_and_checked_at(self):
        checker = HealthChecker()

        async def _ok():
            return HealthCheckResult(
                component="db", status=HealthStatus.HEALTHY, message="ok"
            )

        checker.register_check("db", _ok)
        result = await checker.check_component("db")

        assert result.status == HealthStatus.HEALTHY
        assert result.response_time_ms is not None
        assert result.response_time_ms >= 0
        assert result.checked_at is not None

    async def test_exception_in_check_returns_unhealthy(self):
        checker = HealthChecker()

        async def _boom():
            raise RuntimeError("db is down")

        checker.register_check("db", _boom)
        result = await checker.check_component("db")

        assert result.status == HealthStatus.UNHEALTHY
        assert "db is down" in result.message
        assert result.response_time_ms is not None

    async def test_check_all_runs_all_checks(self):
        checker = HealthChecker()

        async def _a():
            return HealthCheckResult(
                component="a", status=HealthStatus.HEALTHY, message=""
            )

        async def _b():
            return HealthCheckResult(
                component="b", status=HealthStatus.DEGRADED, message=""
            )

        checker.register_check("a", _a)
        checker.register_check("b", _b)
        results = await checker.check_all()

        assert set(results.keys()) == {"a", "b"}
        assert results["a"].status == HealthStatus.HEALTHY
        assert results["b"].status == HealthStatus.DEGRADED


# ---------------------------------------------------------------------------
# get_system_status aggregation
# ---------------------------------------------------------------------------


class TestGetSystemStatus:
    async def _status_for(self, statuses: list[HealthStatus]) -> HealthStatus:
        checker = HealthChecker()
        for i, s in enumerate(statuses):
            captured = s

            async def _check(status=captured):
                return HealthCheckResult(component="x", status=status, message="")

            checker.register_check(f"comp_{i}", _check)
        overall, _ = await checker.get_system_status()
        return overall

    async def test_all_healthy_returns_healthy(self):
        assert (
            await self._status_for([HealthStatus.HEALTHY, HealthStatus.HEALTHY])
            == HealthStatus.HEALTHY
        )

    async def test_any_unhealthy_returns_unhealthy(self):
        assert (
            await self._status_for([HealthStatus.HEALTHY, HealthStatus.UNHEALTHY])
            == HealthStatus.UNHEALTHY
        )

    async def test_degraded_without_unhealthy_returns_degraded(self):
        assert (
            await self._status_for([HealthStatus.HEALTHY, HealthStatus.DEGRADED])
            == HealthStatus.DEGRADED
        )

    async def test_empty_checks_returns_healthy(self):
        # all(...) on an empty iterable is vacuously True → HEALTHY
        checker = HealthChecker()
        overall, details = await checker.get_system_status()
        assert overall == HealthStatus.HEALTHY

    async def test_unknown_present_returns_unknown(self):
        assert (
            await self._status_for([HealthStatus.HEALTHY, HealthStatus.UNKNOWN])
            == HealthStatus.UNKNOWN
        )

    async def test_details_dict_contains_to_dict_output(self):
        checker = HealthChecker()

        async def _ok():
            return HealthCheckResult(
                component="svc", status=HealthStatus.HEALTHY, message="up"
            )

        checker.register_check("svc", _ok)
        _, details = await checker.get_system_status()
        assert "svc" in details
        assert details["svc"]["status"] == "healthy"


# ---------------------------------------------------------------------------
# check_redis_health
# ---------------------------------------------------------------------------


class TestCheckRedisHealth:
    async def test_healthy_when_ping_succeeds(self):
        client = AsyncMock()
        client.ping = AsyncMock()
        client.info = AsyncMock(
            return_value={"redis_version": "7.0.5", "uptime_in_seconds": 3600}
        )
        result = await check_redis_health(client)
        assert result.status == HealthStatus.HEALTHY
        assert result.details["version"] == "7.0.5"

    async def test_unhealthy_when_ping_raises(self):
        client = AsyncMock()
        client.ping = AsyncMock(side_effect=ConnectionError("refused"))
        result = await check_redis_health(client)
        assert result.status == HealthStatus.UNHEALTHY
        assert "refused" in result.message


# ---------------------------------------------------------------------------
# check_neo4j_health
# ---------------------------------------------------------------------------


class TestCheckNeo4jHealth:
    async def test_healthy_when_connectivity_ok(self):
        driver = AsyncMock()
        driver.verify_connectivity = AsyncMock()
        record = MagicMock()
        record.__getitem__ = lambda self, key: ["5.0.0"] if key == "versions" else None
        session_mock = AsyncMock()
        result_mock = AsyncMock()
        result_mock.single = AsyncMock(return_value=record)
        session_mock.run = AsyncMock(return_value=result_mock)
        session_mock.__aenter__ = AsyncMock(return_value=session_mock)
        session_mock.__aexit__ = AsyncMock(return_value=False)
        driver.session = MagicMock(return_value=session_mock)

        result = await check_neo4j_health(driver)
        assert result.status == HealthStatus.HEALTHY
        assert result.details["version"] == "5.0.0"

    async def test_unhealthy_when_connectivity_fails(self):
        driver = AsyncMock()
        driver.verify_connectivity = AsyncMock(side_effect=Exception("auth failed"))
        result = await check_neo4j_health(driver)
        assert result.status == HealthStatus.UNHEALTHY
        assert "auth failed" in result.message


# ---------------------------------------------------------------------------
# check_agent_orchestration_health
# ---------------------------------------------------------------------------


class TestCheckAgentOrchestrationHealth:
    async def test_degraded_when_no_args(self):
        result = await check_agent_orchestration_health()
        assert result.status == HealthStatus.DEGRADED

    async def test_healthy_when_registry_provided(self):
        result = await check_agent_orchestration_health(agent_registry=MagicMock())
        assert result.status == HealthStatus.HEALTHY

    async def test_healthy_when_both_provided(self):
        result = await check_agent_orchestration_health(
            agent_registry=MagicMock(), workflow_manager=MagicMock()
        )
        assert result.status == HealthStatus.HEALTHY
        assert "agents_registered" in result.details
        assert "workflow_manager" in result.details


# ---------------------------------------------------------------------------
# check_openrouter_health
# ---------------------------------------------------------------------------


class TestCheckOpenRouterHealth:
    async def test_degraded_when_no_api_key(self):
        result = await check_openrouter_health(api_key=None)
        assert result.status == HealthStatus.DEGRADED
        assert "not configured" in result.message

    async def test_healthy_when_200(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": ["m1", "m2", "m3"]}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await check_openrouter_health(api_key="sk-test")

        assert result.status == HealthStatus.HEALTHY
        assert result.details["models_available"] == 3

    async def test_degraded_when_non_200(self):
        mock_response = MagicMock()
        mock_response.status_code = 401

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await check_openrouter_health(api_key="sk-bad")

        assert result.status == HealthStatus.DEGRADED

    async def test_unhealthy_when_network_error(self):
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("timeout"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await check_openrouter_health(api_key="sk-test")

        assert result.status == HealthStatus.UNHEALTHY


# ---------------------------------------------------------------------------
# get_health_checker singleton
# ---------------------------------------------------------------------------


class TestGetHealthCheckerSingleton:
    def test_returns_same_instance(self):
        import src.common.health_checks as hc

        hc._health_checker = None  # reset
        a = get_health_checker()
        b = get_health_checker()
        assert a is b

    def test_returns_health_checker_instance(self):
        import src.common.health_checks as hc

        hc._health_checker = None
        checker = get_health_checker()
        assert isinstance(checker, HealthChecker)
