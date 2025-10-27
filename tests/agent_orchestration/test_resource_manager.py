import pytest
from tta_ai.orchestration.resources import ResourceManager, ResourceRequirements


@pytest.mark.asyncio
async def test_monitor_usage_produces_report():
    rm = ResourceManager()
    rep = await rm.monitor_usage()
    assert rep.usage is not None
    assert isinstance(rep.timestamp, float)


@pytest.mark.asyncio
async def test_allocate_resources_basic_cpu_ram():
    rm = ResourceManager(cpu_thread_limit=8)
    # Request fewer threads than limit
    req = ResourceRequirements(cpu_threads=2, ram_bytes=10 * 1024 * 1024)
    alloc = await rm.allocate_resources(agent_id=None, resource_requirements=req)
    assert alloc.granted is True


@pytest.mark.asyncio
async def test_allocate_resources_exceeds_cpu_limit():
    rm = ResourceManager(cpu_thread_limit=2)
    req = ResourceRequirements(cpu_threads=8)
    alloc = await rm.allocate_resources(agent_id=None, resource_requirements=req)
    assert alloc.granted is False
