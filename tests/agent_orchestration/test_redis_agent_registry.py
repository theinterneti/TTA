import asyncio
import json
import time
import pytest

from src.agent_orchestration import AgentId, AgentType
from src.agent_orchestration.proxies import InputProcessorAgentProxy
from src.agent_orchestration.registries import RedisAgentRegistry


@pytest.mark.redis
@pytest.mark.asyncio
async def test_redis_agent_registry_register_heartbeat_and_discover(redis_client):
    reg = RedisAgentRegistry(redis_client, key_prefix="testao", heartbeat_ttl_s=1.0)

    # Create and register an agent
    a = InputProcessorAgentProxy(instance="x")
    await a.start()
    reg.register(a)

    # Persist happens async; give it a moment
    await asyncio.sleep(0.05)

    key = f"testao:agents:{a.agent_id.type.value}:{a.agent_id.instance or 'default'}"
    val = await redis_client.get(key)
    assert val is not None
    data = json.loads(val)
    assert data["name"].startswith("ipa:")

    # Heartbeats
    reg.start_heartbeats()
    await asyncio.sleep(0.2)
    lst = await reg.list_registered()
    assert any(d.get("name") == a.name and d.get("alive") for d in lst)

    # Wait for TTL to expire (no heartbeat)
    reg.stop_heartbeats()
    await asyncio.sleep(1.2)
    lst2 = await reg.list_registered()
    # The key might be gone due to TTL; allow both cases (gone or alive=False)
    if lst2:
        assert not any(d.get("name") == a.name and d.get("alive") for d in lst2)


@pytest.mark.redis
@pytest.mark.asyncio
async def test_snapshot_async_combines_local_and_redis(redis_client):
    reg = RedisAgentRegistry(redis_client, key_prefix="testao2", heartbeat_ttl_s=2.0)

    a = InputProcessorAgentProxy(instance="y")
    await a.start()
    reg.register(a)
    await asyncio.sleep(0.05)

    snap = await reg.snapshot_async()
    assert "local" in snap and "redis_index" in snap
    assert a.name in snap["local"]
    assert any((d.get("name") == a.name) for d in snap["redis_index"])

