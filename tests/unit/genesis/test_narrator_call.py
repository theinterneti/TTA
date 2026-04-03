"""Unit tests for _NarratorCall after ChatPrimitive migration."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from ttadev.primitives.core.base import WorkflowContext

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.components.genesis.agent import _NarratorCall


class _MockAdapter:
    def __init__(self, response: str = "narrator reply") -> None:
        self._response = response
        self.calls: list[tuple] = []

    async def chat(self, messages, system, ctx) -> str:
        self.calls.append((messages, system, ctx))
        return self._response


def test_narrator_call_accepts_chat_primitive():
    """_NarratorCall must accept a ChatPrimitive, not a raw LLM."""
    adapter = _MockAdapter()
    call = _NarratorCall(adapter)
    assert call._adapter is adapter


@pytest.mark.asyncio
async def test_narrator_call_converts_ai_message_to_assistant_role():
    """AIMessage objects in history must become {"role": "assistant", ...}."""
    adapter = _MockAdapter()
    call = _NarratorCall(adapter)
    ctx = WorkflowContext(workflow_id="test")
    history = [AIMessage(content="I am the narrator.")]
    await call.execute(
        {"system_prompt": "sys", "history": history, "player_input": ""},
        ctx,
    )
    sent_messages, _, _ = adapter.calls[0]
    assert sent_messages[0]["role"] == "assistant"
    assert sent_messages[0]["content"] == "I am the narrator."


@pytest.mark.asyncio
async def test_narrator_call_converts_human_message_to_user_role():
    """HumanMessage objects in history must become {"role": "user", ...}."""
    adapter = _MockAdapter()
    call = _NarratorCall(adapter)
    ctx = WorkflowContext(workflow_id="test")
    history = [HumanMessage(content="Hello world")]
    await call.execute(
        {"system_prompt": "sys", "history": history, "player_input": ""},
        ctx,
    )
    sent_messages, _, _ = adapter.calls[0]
    assert sent_messages[0]["role"] == "user"
    assert sent_messages[0]["content"] == "Hello world"


@pytest.mark.asyncio
async def test_narrator_call_appends_player_input_as_user():
    """player_input must be appended as {"role": "user", ...} after history."""
    adapter = _MockAdapter()
    call = _NarratorCall(adapter)
    ctx = WorkflowContext(workflow_id="test")
    await call.execute(
        {"system_prompt": "sys", "history": [], "player_input": "What is this place?"},
        ctx,
    )
    sent_messages, _, _ = adapter.calls[0]
    assert sent_messages[-1] == {"role": "user", "content": "What is this place?"}


@pytest.mark.asyncio
async def test_narrator_call_passes_system_prompt():
    """system_prompt must be passed as the system= kwarg to adapter.chat()."""
    adapter = _MockAdapter()
    call = _NarratorCall(adapter)
    ctx = WorkflowContext(workflow_id="test")
    await call.execute(
        {"system_prompt": "You are the void.", "history": [], "player_input": "hi"},
        ctx,
    )
    _, sent_system, _ = adapter.calls[0]
    assert sent_system == "You are the void."


@pytest.mark.asyncio
async def test_narrator_call_strips_whitespace():
    """execute() must strip leading/trailing whitespace from the response."""
    adapter = _MockAdapter(response="  hello  ")
    call = _NarratorCall(adapter)
    ctx = WorkflowContext(workflow_id="test")
    result = await call.execute(
        {"system_prompt": "s", "history": [], "player_input": "hi"},
        ctx,
    )
    assert result == "hello"
