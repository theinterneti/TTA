"""Unit tests for SeedExtractor after ChatPrimitive migration."""
from __future__ import annotations
import json
import pytest
from ttadev.primitives.core.base import WorkflowContext
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.components.genesis.seed_extractor import _ExtractionCall, _SurpriseCall, SeedExtractor


class _MockAdapter:
    def __init__(self, response: str = "{}") -> None:
        self._response = response
        self.calls: list[tuple] = []

    async def chat(self, messages, system, ctx) -> str:
        self.calls.append((messages, system, ctx))
        return self._response


@pytest.mark.asyncio
async def test_extraction_call_routes_to_extraction_mode():
    """_ExtractionCall must call adapter.chat() and return parsed JSON."""
    adapter = _MockAdapter(response='{"tone": "getting_worse"}')
    call = _ExtractionCall(adapter)
    ctx = WorkflowContext(workflow_id="test")
    result = await call.execute(
        {"player_input": "Dark dystopian world", "current_fields": {}},
        ctx,
    )
    assert result == {"tone": "getting_worse"}
    assert len(adapter.calls) == 1


@pytest.mark.asyncio
async def test_extraction_call_passes_system_as_kwarg():
    """_ExtractionCall must pass the system prompt via system= position, not in messages."""
    adapter = _MockAdapter(response="{}")
    call = _ExtractionCall(adapter)
    ctx = WorkflowContext(workflow_id="test")
    await call.execute({"player_input": "hi", "current_fields": {}}, ctx)
    sent_messages, sent_system, _ = adapter.calls[0]
    for msg in sent_messages:
        assert msg.get("role") != "system", "system prompt must not be in messages list"
    assert "extract" in sent_system.lower() or "world" in sent_system.lower()


@pytest.mark.asyncio
async def test_extraction_call_returns_empty_dict_on_bad_json():
    """_ExtractionCall must return {} when the model returns invalid JSON."""
    adapter = _MockAdapter(response="not json at all")
    call = _ExtractionCall(adapter)
    ctx = WorkflowContext(workflow_id="test")
    result = await call.execute({"player_input": "hi", "current_fields": {}}, ctx)
    assert result == {}


@pytest.mark.asyncio
async def test_surprise_call_routes_to_extraction_adapter():
    """_SurpriseCall must call adapter.chat() — same extraction adapter."""
    valid_seed = json.dumps({
        "tone": "cyclical", "power_source": "magic",
        "player_position": "outsider", "one_specific_detail": "A floating market",
        "scale": "city", "era_tech_level": "medieval", "magic_presence": "common",
    })
    adapter = _MockAdapter(response=valid_seed)
    call = _SurpriseCall(adapter)
    ctx = WorkflowContext(workflow_id="test")
    result = await call.execute({}, ctx)
    assert result["tone"] == "cyclical"
    assert len(adapter.calls) == 1


@pytest.mark.asyncio
async def test_surprise_call_passes_system_as_kwarg():
    """_SurpriseCall must pass system prompt via system= position, not in messages."""
    adapter = _MockAdapter(response='{"tone":"cyclical","power_source":"magic",'
                           '"player_position":"outsider","one_specific_detail":"x",'
                           '"scale":"city","era_tech_level":"medieval","magic_presence":"none"}')
    call = _SurpriseCall(adapter)
    ctx = WorkflowContext(workflow_id="test")
    await call.execute({}, ctx)
    sent_messages, sent_system, _ = adapter.calls[0]
    for msg in sent_messages:
        assert msg.get("role") != "system"
    assert "WorldSeed" in sent_system


def test_seed_extractor_passes_same_adapter_to_both_calls():
    """SeedExtractor must pass the same ChatPrimitive adapter to both
    _ExtractionCall and _SurpriseCall — they share one extraction adapter."""
    adapter = _MockAdapter()
    extractor = SeedExtractor(adapter=adapter)
    # FallbackPrimitive.primary and RetryPrimitive.primitive are public attributes
    extraction_inner = extractor._extractor.primary.primitive
    surprise_inner = extractor._surprise.primary.primitive
    assert extraction_inner._adapter is adapter
    assert surprise_inner._adapter is adapter
