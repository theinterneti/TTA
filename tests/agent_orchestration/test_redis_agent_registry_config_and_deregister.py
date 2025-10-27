import asyncio
import json

import pytest

from tta_ai.orchestration.proxies import InputProcessorAgentProxy
from tta_ai.orchestration.registries import RedisAgentRegistry


@pytest.mark.redis
@pytest.mark.asyncio
async def test_registry_ttl_and_interval_config_and_deregister(redis_client):
    # Use short TTL/interval for test
    reg = RedisAgentRegistry(
        redis_client,
        key_prefix="testao3",
        heartbeat_ttl_s=0.8,
        heartbeat_interval_s=0.2,
    )

    a = InputProcessorAgentProxy(instance="confA")
    await a.start()
    reg.register(a)

    # Persist + heartbeat
    await asyncio.sleep(0.05)
    key = "testao3:agents:input_processor:confA"
    assert await redis_client.get(key) is not None

    # One heartbeat cycle
    reg.start_heartbeats()
    await asyncio.sleep(0.25)

    # Ensure state persistence field appears and last_heartbeat updates
    # (default export_state returns empty dict, so no 'state' key)
    val1 = await redis_client.get(key)
    data1 = json.loads(val1)
    assert "status" in data1 and "last_heartbeat" in data1
    t1 = float(data1["last_heartbeat"]) if isinstance(data1, dict) else 0.0

    # Heartbeats
    reg.start_heartbeats()
    await asyncio.sleep(0.25)
    val2 = await redis_client.get(key)
    data2 = json.loads(val2)
    assert float(data2["last_heartbeat"]) >= t1

    # Deregister should remove key and index
    reg.deregister(a.agent_id)
    await asyncio.sleep(0.05)
    assert await redis_client.get(key) is None
    # Ensure index doesn't include key
    assert key.encode() not in (await redis_client.smembers("testao3:agents:index"))
