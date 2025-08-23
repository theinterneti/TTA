import asyncio
import os
import pytest

from src.agent_orchestration import (
    AgentId, AgentType, MessagePriority, MessageType,
    Agent,
    AgentRegistry,
    InputProcessorAgentProxy,
    WorldBuilderAgentProxy,
    NarrativeGeneratorAgentProxy,
)


@pytest.mark.asyncio
async def test_agent_lifecycle_and_health():
    a = InputProcessorAgentProxy()
    await a.start()
    hc = await a.health_check()
    assert hc["status"] in ("healthy", "degraded")
    await a.stop()
    hc2 = await a.health_check()
    assert hc2["status"] in ("stopped", "degraded")


@pytest.mark.asyncio
async def test_agent_process_timeout_and_metrics():
    class SlowAgent(InputProcessorAgentProxy):
        async def process(self, input_payload: dict) -> dict:
            await asyncio.sleep(0.2)
            # Preserve IPA behavior after delay
            return await super().process(input_payload)

    a = SlowAgent()
    await a.start()
    # Short timeout to trigger
    with pytest.raises(asyncio.TimeoutError):
        await a.process_with_timeout({"text": "hi"}, timeout_s=0.05)
    # Normal path
    r = await a.process_with_timeout({"text": "hi"}, timeout_s=0.5)
    assert r["normalized_text"] == "hi"


@pytest.mark.asyncio
async def test_input_processor_validation_and_retry():
    a = InputProcessorAgentProxy()
    await a.start()
    with pytest.raises(ValueError):
        await a.process({})
    r = await a.handle_with_retry({"text": "  hello  "})
    assert r["normalized_text"] == "hello"


@pytest.mark.asyncio
async def test_world_builder_cache_and_updates():
    w = WorldBuilderAgentProxy()
    await w.start()
    # First fetch not cached
    res1 = await w.process({"world_id": "w1"})
    assert res1["cached"] is False
    # Second fetch should be cached
    res2 = await w.process({"world_id": "w1"})
    assert res2["cached"] is True
    # Apply update
    upd = await w.process({"world_id": "w1", "updates": {"regions": ["r1"]}})
    assert upd["updated"] is True
    res3 = await w.process({"world_id": "w1"})
    assert res3["world_state"]["regions"] == ["r1"]


@pytest.mark.asyncio
async def test_narrative_generator_filtering():
    n = NarrativeGeneratorAgentProxy()
    await n.start()
    res = await n.process({"prompt": "An epic tale with violence"})
    assert "[redacted]" in res["story"].lower()


@pytest.mark.asyncio
async def test_agent_registry_discovery_and_healthloop():
    reg = AgentRegistry()
    a1 = InputProcessorAgentProxy(instance="a")
    a2 = WorldBuilderAgentProxy(instance="b")
    await a1.start(); await a2.start()
    reg.register(a1); reg.register(a2)
    # Discover
    ds = reg.discover(AgentType.IPA)
    assert len(ds) == 1 and ds[0].name.startswith("ipa:")
    # Health check
    snap = await reg.run_health_checks_once()
    assert a1.name in snap and "status" in snap[a1.name]
    # Start periodic and stop
    reg.start_periodic_health_checks(interval_s=0.05)
    await asyncio.sleep(0.12)
    reg.stop_periodic_health_checks()

