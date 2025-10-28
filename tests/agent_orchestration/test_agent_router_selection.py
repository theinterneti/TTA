import pytest
from tta_ai.orchestration.models import AgentId, AgentType
from tta_ai.orchestration.router import AgentRouter


class DummyMetrics:
    def __init__(self, requests=0, errors=0):
        self.requests = requests
        self.errors = errors


class DummyAgent:
    def __init__(
        self,
        atype: AgentType,
        instance: str,
        running=True,
        degraded=False,
        requests=0,
        errors=0,
    ):
        self.agent_id = AgentId(type=atype, instance=instance)
        self._running = running
        self._degraded = degraded
        self._metrics = DummyMetrics(requests=requests, errors=errors)
        self.name = f"{atype.value}:{instance}"


class DummyRegistry:
    def __init__(self, agents):
        self._agents = agents

    def all(self):
        return list(self._agents)


class DummyRedis:
    def __init__(self, llen_map=None, heartbeat_map=None):
        self.llen_map = llen_map or {}
        self.heartbeat_map = heartbeat_map or {}

    async def llen(self, key: str):
        return int(self.llen_map.get(key, 0))

    async def get(self, key: str):
        v = self.heartbeat_map.get(key)
        if v is None:
            return None
        import json

        return (json.dumps(v)).encode()


@pytest.mark.asyncio
async def test_shortest_queue_wins():
    at = AgentType.IPA
    a1 = DummyAgent(at, "a1")
    a2 = DummyAgent(at, "a2")
    a3 = DummyAgent(at, "a3")
    reg = DummyRegistry([a1, a2, a3])
    llen_map = {
        f"ao:queue:{at.value}:a1": 10,
        f"ao:queue:{at.value}:a2": 2,
        f"ao:queue:{at.value}:a3": 5,
    }
    # Heartbeats all fresh and identical
    import time

    now = time.time()
    hb = {
        f"ao:agents:{at.value}:{i}": {"last_heartbeat": now} for i in ("a1", "a2", "a3")
    }
    r = DummyRedis(llen_map=llen_map, heartbeat_map=hb)
    router = AgentRouter(reg, r, heartbeat_fresh_s=30.0)
    res = await router.resolve_healthy_instance(at)
    assert res.instance == "a2"


@pytest.mark.asyncio
async def test_degraded_agents_excluded():
    at = AgentType.IPA
    a1 = DummyAgent(at, "a1", degraded=True)
    a2 = DummyAgent(at, "a2", degraded=False)
    reg = DummyRegistry([a1, a2])
    r = DummyRedis()
    router = AgentRouter(reg, r)
    res = await router.resolve_healthy_instance(at)
    assert res.instance == "a2"


@pytest.mark.asyncio
async def test_heartbeat_freshness_preference():
    at = AgentType.IPA
    a1 = DummyAgent(at, "a1")
    a2 = DummyAgent(at, "a2")
    reg = DummyRegistry([a1, a2])
    import time

    now = time.time()
    # same queue, but a1 is stale heartbeat (older)
    llen_map = {f"ao:queue:{at.value}:a1": 3, f"ao:queue:{at.value}:a2": 3}
    hb = {
        f"ao:agents:{at.value}:a1": {"last_heartbeat": now - 120},
        f"ao:agents:{at.value}:a2": {"last_heartbeat": now - 2},
    }
    r = DummyRedis(llen_map=llen_map, heartbeat_map=hb)
    router = AgentRouter(reg, r, heartbeat_fresh_s=30.0)
    res = await router.resolve_healthy_instance(at)
    assert res.instance == "a2"


@pytest.mark.asyncio
async def test_configured_weights_flow_into_preview():
    # Two agents to allow preview; configure via ctor args explicitly
    at = AgentType.IPA
    a1 = DummyAgent(at, "a1")
    a2 = DummyAgent(at, "a2")
    reg = DummyRegistry([a1, a2])
    import time

    now = time.time()
    hb = {f"ao:agents:{at.value}:{i}": {"last_heartbeat": now} for i in ("a1", "a2")}
    llen_map = {f"ao:queue:{at.value}:{i}": 1 for i in ("a1", "a2")}
    r = DummyRedis(llen_map=llen_map, heartbeat_map=hb)
    router = AgentRouter(
        reg, r, heartbeat_fresh_s=45.0, w_queue=0.5, w_heartbeat=0.3, w_success=0.2
    )
    preview = await router.preview(at)
    assert preview["configured_weights"] == {
        "queue": 0.5,
        "heartbeat": 0.3,
        "success": 0.2,
    }
    assert preview["configured_heartbeat_fresh_seconds"] == 45.0


@pytest.mark.asyncio
async def test_preview_exclusion_reasons_and_summary():
    at = AgentType.IPA
    # Mix: wrong type, not running, degraded, healthy
    a_wrong = DummyAgent(AgentType.WBA, "w1")
    a_down = DummyAgent(at, "d1", running=False)
    a_deg = DummyAgent(at, "g1", degraded=True)
    a_ok = DummyAgent(at, "ok1", running=True, degraded=False)
    reg = DummyRegistry([a_wrong, a_down, a_deg, a_ok])
    r = DummyRedis()
    router = AgentRouter(reg, r)
    preview = await router.preview(at, exclude_degraded=True)
    reasons = {e["instance"]: e["reason"] for e in preview.get("excluded", [])}
    assert reasons.get("w1") == "wrong_type"
    assert reasons.get("d1") == "not_running"
    assert reasons.get("g1") == "degraded"
    summary = preview.get("summary", {})
    assert summary.get("total_agents") == 4
    assert summary.get("excluded_count") == 3
    counts = summary.get("exclusion_reasons", {})
    assert counts.get("wrong_type") == 1
    assert counts.get("not_running") == 1
    assert counts.get("degraded") == 1
    assert summary.get("healthy_candidates") == 1


@pytest.mark.asyncio
async def test_show_all_candidates_includes_excluded_agents():
    at = AgentType.IPA
    # Healthy agents
    a_ok1 = DummyAgent(at, "ok1", running=True, degraded=False)
    a_ok2 = DummyAgent(at, "ok2", running=True, degraded=False)
    # Degraded target-type agent
    a_deg = DummyAgent(at, "g1", degraded=True)
    # Wrong type agent
    a_wrong = DummyAgent(AgentType.WBA, "w1")
    # Not running target-type agent
    a_down = DummyAgent(at, "d1", running=False)

    reg = DummyRegistry([a_ok1, a_ok2, a_deg, a_wrong, a_down])
    # Provide equal queues and fresh heartbeats so scoring differences do not affect presence checks
    import time

    now = time.time()
    llen_map = {
        f"ao:queue:{at.value}:ok1": 1,
        f"ao:queue:{at.value}:ok2": 1,
        f"ao:queue:{at.value}:g1": 1,
        f"ao:queue:{AgentType.WBA.value}:w1": 1,
        f"ao:queue:{at.value}:d1": 1,
    }
    hb = {
        f"ao:agents:{at.value}:ok1": {"last_heartbeat": now},
        f"ao:agents:{at.value}:ok2": {"last_heartbeat": now},
        f"ao:agents:{at.value}:g1": {"last_heartbeat": now},
        f"ao:agents:{AgentType.WBA.value}:w1": {"last_heartbeat": now},
        f"ao:agents:{at.value}:d1": {"last_heartbeat": now},
    }
    r = DummyRedis(llen_map=llen_map, heartbeat_map=hb)
    router = AgentRouter(reg, r)

    preview = await router.preview(at, exclude_degraded=True, show_all_candidates=True)

    # Candidates should include ok1/ok2 as excluded=False and g1,d1 as excluded=True with reasons
    cands = preview.get("candidates", [])
    by_inst = {c["instance"]: c for c in cands}
    # Healthy
    assert by_inst["ok1"]["excluded"] is False
    assert by_inst["ok2"]["excluded"] is False
    assert isinstance(by_inst["ok1"].get("score"), float)
    assert isinstance(by_inst["ok2"].get("score"), float)
    # Excluded but shown
    assert by_inst["g1"]["excluded"] is True
    assert by_inst["g1"]["exclusion_reason"] == "degraded"
    assert by_inst["g1"].get("score") is None
    assert by_inst["d1"]["excluded"] is True
    assert by_inst["d1"]["exclusion_reason"] == "not_running"
    assert by_inst["d1"].get("score") is None
    # Wrong type must not appear in candidates
    assert "w1" not in by_inst

    # Summary healthy_candidates should count only non-excluded entries added by scoring
    summary = preview.get("summary", {})
    assert summary.get("healthy_candidates") == 2
