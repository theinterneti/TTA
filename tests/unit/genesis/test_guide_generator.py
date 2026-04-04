"""Unit tests for guide_generator after ChatPrimitive migration."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.components.genesis.guide_generator import derive_guide_character


class _MockAdapter:
    def __init__(self, response: str = '{"name": "Varek", "intro_line": "Follow me."}') -> None:
        self._response = response
        self.calls: list[tuple] = []

    async def chat(self, messages, system, ctx) -> str:
        self.calls.append((messages, system, ctx))
        return self._response


@pytest.mark.asyncio
async def test_derive_guide_character_uses_injected_adapter():
    """derive_guide_character must use the passed-in adapter — no new from_yaml call."""
    adapter = _MockAdapter()
    result = await derive_guide_character(
        seed_fields={"tone": "getting_worse", "power_source": "magic"},
        adapter=adapter,
    )
    assert result.name == "Varek"
    assert len(adapter.calls) >= 1


@pytest.mark.asyncio
async def test_derive_guide_character_passes_system_as_kwarg():
    """_GuideNameCall must pass the system prompt via system= kwarg."""
    adapter = _MockAdapter()
    await derive_guide_character(seed_fields={"tone": "cyclical"}, adapter=adapter)
    _, sent_system, _ = adapter.calls[0]
    assert "guide" in sent_system.lower() or "character" in sent_system.lower()
    sent_messages, _, _ = adapter.calls[0]
    for msg in sent_messages:
        assert msg.get("role") != "system"


@pytest.mark.asyncio
async def test_derive_guide_character_constructs_adapter_when_none():
    """derive_guide_character constructs a narration adapter when adapter=None."""
    mock_router = MagicMock()
    with patch(
        "src.components.genesis.guide_generator.ModelRouterPrimitive.from_yaml",
        return_value=mock_router,
    ) as mock_from_yaml:
        await derive_guide_character(seed_fields={}, adapter=None)
    mock_from_yaml.assert_called_once()
