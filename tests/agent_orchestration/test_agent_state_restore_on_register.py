import asyncio
import json

import pytest
from tta_ai.orchestration.proxies import InputProcessorAgentProxy
from tta_ai.orchestration.registries import RedisAgentRegistry


@pytest.mark.redis
@pytest.mark.asyncio
async def test_state_restore_on_register(redis_client):
    reg = RedisAgentRegistry(
        redis_client, key_prefix="testao_state", heartbeat_ttl_s=1.0
    )

    class StatefulIPA(InputProcessorAgentProxy):
        def __init__(self, **kw):
            super().__init__(**kw)
            self._flag = 0

        async def export_state(self):
            return {"flag": self._flag}

        async def import_state(self, state):
            self._flag = int(state.get("flag", 0))

    a1 = StatefulIPA(instance="s1")
    await a1.start()
    a1._flag = 41
    reg.register(a1)
    await asyncio.sleep(0.05)

    key = "testao_state:agents:input_processor:s1"
    val = await redis_client.get(key)
    data = json.loads(val)
    assert data.get("state", {}).get("flag") == 41

    # Simulate process restart: new agent object with same id
    a2 = StatefulIPA(instance="s1")
    await a2.start()
    reg.register(a2)
    await asyncio.sleep(0.05)

    # After registration, state should be restored into a2
    assert a2._flag == 41
