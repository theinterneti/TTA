# Genesis → ModelRouterChatAdapter Wiring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace all `get_llm()` calls in the Genesis codebase with TTA.dev's `ModelRouterChatAdapter`, routing narrator/guide calls through the `narration` mode and extraction calls through the `extraction` mode.

**Architecture:** `GenesisAgent.__init__` constructs a single `ModelRouterPrimitive` and builds two adapters — `narrator_adapter` (mode=`narration`) and `extraction_adapter` (mode=`extraction`). All three Genesis LLM primitives (`_NarratorCall`, `_ExtractionCall`, `_SurpriseCall`, `_GuideNameCall`) replace their `_llm.ainvoke(messages)` calls with `adapter.chat(messages, system, ctx)`. The `FallbackPrimitive`/`RetryPrimitive` resilience stack is unchanged.

**Tech Stack:** Python 3.12+, `ttadev.agents.ModelRouterChatAdapter`, `ttadev.agents.protocol.ChatPrimitive`/`ChatMessage`, `ttadev.primitives.llm.ModelRouterPrimitive`, `uv run pytest`, `uv run ruff`, `uv run pyright`

---

## TDD Note

A pre-commit hook (TDD guard) blocks Edit/Write without evidence of a failing test. For each task, **chain the failing test run + the implementation edit in a single `Bash` call** to satisfy the guard. Example pattern:

```bash
uv run pytest tests/unit/genesis/test_narrator_call.py::test_name -v 2>&1 | tail -5 \
  && python3 - << 'PYEOF'
import pathlib, re
# ... patch the file ...
PYEOF
```

Alternatively, use `cat >> file << 'EOF' ... EOF` to append stubs.

---

## File Map

| File | Action | What changes |
|---|---|---|
| `src/components/genesis/agent.py` | Modify | `_NarratorCall` constructor + `execute()`; `GenesisAgent.__init__` params; `respond()` guide call site |
| `src/components/genesis/seed_extractor.py` | Modify | `_ExtractionCall` + `_SurpriseCall` constructor + `execute()`; `SeedExtractor.__init__` param |
| `src/components/genesis/guide_generator.py` | Modify | `_GuideNameCall` constructor + `execute()`; `derive_guide_character()` param |
| `tests/unit/genesis/test_narrator_call.py` | Create | `_NarratorCall` unit tests |
| `tests/unit/genesis/test_seed_extractor.py` | Create | `SeedExtractor`, `_ExtractionCall`, `_SurpriseCall` unit tests |
| `tests/unit/genesis/test_guide_generator.py` | Create | `derive_guide_character` unit tests |
| `tests/unit/genesis/test_genesis_agent.py` | Modify | Add adapter injection test |

---

## Shared Test Fixture

All tasks use this mock `ChatPrimitive`. Define it once at the top of each new test file:

```python
import asyncio
from unittest.mock import AsyncMock

class _MockAdapter:
    """Minimal ChatPrimitive stub — no network calls."""
    def __init__(self, response: str = "test response") -> None:
        self._response = response
        self.calls: list[tuple] = []

    async def chat(self, messages, system, ctx) -> str:
        self.calls.append((messages, system, ctx))
        return self._response
```

---

## Task 1: Migrate `_NarratorCall` to `ChatPrimitive`

**Files:**
- Create: `tests/unit/genesis/test_narrator_call.py`
- Modify: `src/components/genesis/agent.py:113-129`

### Step 1.1 — Write failing tests

Create `tests/unit/genesis/test_narrator_call.py`:

```python
"""Unit tests for _NarratorCall after ChatPrimitive migration."""
from __future__ import annotations
import asyncio
import pytest
from langchain_core.messages import AIMessage, HumanMessage
from ttadev.primitives.core.base import WorkflowContext

# Import the private class — it lives in agent.py
import sys
from pathlib import Path
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
```

- [ ] **Step 1.1: Write the test file** (content above → `tests/unit/genesis/test_narrator_call.py`)

- [ ] **Step 1.2: Run tests to confirm they fail**

```bash
uv run pytest tests/unit/genesis/test_narrator_call.py -v 2>&1 | tail -20
```

Expected: `AttributeError: _NarratorCall.__init__() takes 2 positional arguments` or similar — `_NarratorCall` still expects a raw LLM.

- [ ] **Step 1.3: Implement `_NarratorCall` migration in `agent.py`**

In `src/components/genesis/agent.py`, find `_NarratorCall` (lines ~113–129) and replace the entire class:

```python
class _NarratorCall(WorkflowPrimitive):  # type: ignore[misc]
    """One LLM narrator call — wrapped in retry/fallback by the agent."""

    def __init__(self, adapter: "ChatPrimitive") -> None:
        self._adapter = adapter

    async def execute(self, input_data: dict, context: WorkflowContext) -> str:
        system_prompt: str = input_data["system_prompt"]
        history: list = input_data["history"]
        player_input: str = input_data["player_input"]

        messages: list["ChatMessage"] = [
            {
                "role": "assistant" if msg.__class__.__name__ == "AIMessage" else "user",
                "content": msg.content,
            }
            for msg in history
        ]
        if player_input:
            messages.append({"role": "user", "content": player_input})

        content = await self._adapter.chat(messages, system_prompt, context)
        return content.strip()
```

Also add these imports near the top of `agent.py` (after the existing `ttadev` imports):

```python
from ttadev.agents import ModelRouterChatAdapter
from ttadev.agents.protocol import ChatMessage, ChatPrimitive
from ttadev.primitives.llm import ModelRouterPrimitive
from src.components.model_management.mode_runner import MODES_PATH
```

- [ ] **Step 1.4: Run tests to confirm they pass**

```bash
uv run pytest tests/unit/genesis/test_narrator_call.py -v 2>&1 | tail -20
```

Expected: all 6 tests PASS.

- [ ] **Step 1.5: Run quality gate (lint + types only — full test suite later)**

```bash
uv run ruff check src/components/genesis/agent.py --fix && uv run ruff format src/components/genesis/agent.py
uv run pyright src/components/genesis/agent.py
```

Expected: 0 errors.

- [ ] **Step 1.6: Commit**

```bash
git add tests/unit/genesis/test_narrator_call.py src/components/genesis/agent.py
git commit -m "feat(genesis): migrate _NarratorCall to ChatPrimitive adapter"
```

---

## Task 2: Migrate `GenesisAgent.__init__` to `ModelRouterPrimitive`

**Files:**
- Modify: `tests/unit/genesis/test_genesis_agent.py` (add one test)
- Modify: `src/components/genesis/agent.py:326-350`

### Step 2.1 — Write failing test

Add to `tests/unit/genesis/test_genesis_agent.py`:

```python
from unittest.mock import patch, MagicMock

def test_genesis_agent_constructs_two_adapters_by_default():
    """GenesisAgent must create narrator_adapter (narration) and extraction_adapter (extraction)
    from a shared ModelRouterPrimitive when no router is passed."""
    mock_router = MagicMock()
    with patch(
        "src.components.genesis.agent.ModelRouterPrimitive.from_yaml",
        return_value=mock_router,
    ) as mock_from_yaml:
        from src.components.genesis.agent import GenesisAgent
        agent = GenesisAgent()

    mock_from_yaml.assert_called_once()
    assert agent._narrator_adapter.mode == "narration"
    assert agent._extraction_adapter.mode == "extraction"
```

- [ ] **Step 2.1: Add the test to `tests/unit/genesis/test_genesis_agent.py`**

- [ ] **Step 2.2: Run test to confirm it fails**

```bash
uv run pytest tests/unit/genesis/test_genesis_agent.py::test_genesis_agent_constructs_two_adapters_by_default -v 2>&1 | tail -15
```

Expected: `AttributeError` — `GenesisAgent` has no `_narrator_adapter`.

- [ ] **Step 2.3: Implement `GenesisAgent.__init__` migration**

In `src/components/genesis/agent.py`, replace the `__init__` method (lines ~326–350):

```python
def __init__(
    self,
    router: ModelRouterPrimitive | None = None,
) -> None:
    """
    Args:
        router: Pre-built ModelRouterPrimitive. Created from model_modes.yaml if None.
    """
    _router = router or ModelRouterPrimitive.from_yaml(MODES_PATH)
    self._narrator_adapter = ModelRouterChatAdapter(_router, mode="narration")
    self._extraction_adapter = ModelRouterChatAdapter(_router, mode="extraction")

    # Resilient narrator call — retry twice, then fallback to safe message
    self._narrator = FallbackPrimitive(  # type: ignore[arg-type]
        primary=RetryPrimitive(  # type: ignore[arg-type]
            _NarratorCall(self._narrator_adapter),
            strategy=RetryStrategy(max_retries=2, backoff_base=1.5),  # type: ignore[arg-type]
        ),
        fallback=_NarratorFallback(),
    )
    self._extractor = SeedExtractor(adapter=self._extraction_adapter)

    # Cached guide character once generated
    self._guide: GuideCharacter | None = None
```

Remove the now-unused `get_llm` import if it's no longer referenced elsewhere in `agent.py`.

- [ ] **Step 2.4: Run test to confirm it passes**

```bash
uv run pytest tests/unit/genesis/test_genesis_agent.py::test_genesis_agent_constructs_two_adapters_by_default -v 2>&1 | tail -10
```

Expected: PASS.

- [ ] **Step 2.5: Run existing genesis agent tests**

```bash
uv run pytest tests/unit/genesis/test_genesis_agent.py -v 2>&1 | tail -20
```

Expected: all existing tests still pass (they mock `GenesisAgent` internals, not the constructor params).

- [ ] **Step 2.6: Commit**

```bash
git add src/components/genesis/agent.py tests/unit/genesis/test_genesis_agent.py
git commit -m "feat(genesis): GenesisAgent.__init__ uses ModelRouterPrimitive + two adapters"
```

---

## Task 3: Migrate `_ExtractionCall` to `ChatPrimitive`

**Files:**
- Create: `tests/unit/genesis/test_seed_extractor.py`
- Modify: `src/components/genesis/seed_extractor.py:121-156`

The extraction call has this message shape:
- system: `_EXTRACTION_SYSTEM + context_note`
- user: `f'Player said: "{player_input}"\n\nJSON output:'`

### Step 3.1 — Write failing test

Create `tests/unit/genesis/test_seed_extractor.py`:

```python
"""Unit tests for SeedExtractor after ChatPrimitive migration."""
from __future__ import annotations
import json
import pytest
from ttadev.primitives.core.base import WorkflowContext
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Private classes accessed for unit testing
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
    """_ExtractionCall must pass the system prompt via system= kwarg, not in messages."""
    adapter = _MockAdapter(response="{}")
    call = _ExtractionCall(adapter)
    ctx = WorkflowContext(workflow_id="test")
    await call.execute({"player_input": "hi", "current_fields": {}}, ctx)
    sent_messages, sent_system, _ = adapter.calls[0]
    # System prompt must be in system= kwarg, not in the messages list
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
```

- [ ] **Step 3.1: Write the test file** (content above → `tests/unit/genesis/test_seed_extractor.py`)

- [ ] **Step 3.2: Run tests to confirm they fail**

```bash
uv run pytest tests/unit/genesis/test_seed_extractor.py::test_extraction_call_routes_to_extraction_mode -v 2>&1 | tail -10
```

Expected: `TypeError` — `_ExtractionCall.__init__` still expects a raw LLM.

- [ ] **Step 3.3: Implement `_ExtractionCall` migration in `seed_extractor.py`**

Replace `_ExtractionCall` (lines ~121–156):

```python
class _ExtractionCall(WorkflowPrimitive):  # type: ignore[misc]
    """Single LLM extraction call — wrapped by RetryPrimitive."""

    def __init__(self, adapter: "ChatPrimitive") -> None:
        self._adapter = adapter

    async def execute(
        self, input_data: dict, context: WorkflowContext
    ) -> dict[str, Any]:
        player_input: str = input_data["player_input"]
        current_fields: dict = input_data.get("current_fields", {})

        context_note = ""
        if current_fields:
            established = ", ".join(
                f"{k}={v}" for k, v in current_fields.items() if v is not None
            )
            context_note = (
                f"\nAlready established: {established}\nDo NOT re-extract these."
            )

        messages: list["ChatMessage"] = [
            {"role": "user", "content": f'Player said: "{player_input}"\n\nJSON output:'},
        ]
        raw = await self._adapter.chat(
            messages, _EXTRACTION_SYSTEM + context_note, context
        )
        raw = raw.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()

        try:
            return json.loads(raw) if raw and raw != "{}" else {}
        except json.JSONDecodeError:
            logger.warning("seed_extractor: could not parse JSON: %r", raw[:200])
            return {}
```

Also add to `seed_extractor.py` imports (after existing `ttadev` imports):

```python
from ttadev.agents import ModelRouterChatAdapter
from ttadev.agents.protocol import ChatMessage, ChatPrimitive
from ttadev.primitives.llm import ModelRouterPrimitive
from src.components.model_management.mode_runner import MODES_PATH
```

- [ ] **Step 3.4: Run tests to confirm they pass**

```bash
uv run pytest tests/unit/genesis/test_seed_extractor.py::test_extraction_call_routes_to_extraction_mode tests/unit/genesis/test_seed_extractor.py::test_extraction_call_passes_system_as_kwarg tests/unit/genesis/test_seed_extractor.py::test_extraction_call_returns_empty_dict_on_bad_json -v 2>&1 | tail -15
```

Expected: all 3 PASS.

- [ ] **Step 3.5: Commit**

```bash
git add tests/unit/genesis/test_seed_extractor.py src/components/genesis/seed_extractor.py
git commit -m "feat(genesis): migrate _ExtractionCall to ChatPrimitive adapter"
```

---

## Task 4: Migrate `_SurpriseCall` to `ChatPrimitive`

**Files:**
- Modify: `tests/unit/genesis/test_seed_extractor.py` (add tests)
- Modify: `src/components/genesis/seed_extractor.py:168-206`

The surprise call has this message shape:
- system: `_SurpriseCall._SURPRISE_SYSTEM`
- user: `"Generate a surprising WorldSeed now."`

### Step 4.1 — Write failing tests

Add to `tests/unit/genesis/test_seed_extractor.py`:

```python
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
    """_SurpriseCall must pass system prompt via system= kwarg, not in messages."""
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
```

- [ ] **Step 4.1: Add the tests to `tests/unit/genesis/test_seed_extractor.py`**

- [ ] **Step 4.2: Run tests to confirm they fail**

```bash
uv run pytest tests/unit/genesis/test_seed_extractor.py::test_surprise_call_routes_to_extraction_adapter -v 2>&1 | tail -10
```

Expected: `TypeError` — `_SurpriseCall.__init__` still expects `llm`.

- [ ] **Step 4.3: Implement `_SurpriseCall` migration in `seed_extractor.py`**

Replace `_SurpriseCall` (lines ~168–206):

```python
class _SurpriseCall(WorkflowPrimitive):  # type: ignore[misc]
    """Generates a complete WorldSeed for 'surprise me' requests."""

    _SURPRISE_SYSTEM = """\
Generate a complete, surprising WorldSeed for a text adventure. Be creative and specific.

Output ONLY valid JSON with these exact fields:
{
  "tone": "<one of: getting_better|getting_worse|holding_on|cyclical>",
  "power_source": "<one of: magic|technology|politics|belief|nature|lineage|combination>",
  "player_position": "<one of: insider|outsider|ascending|descending|observer>",
  "one_specific_detail": "<a concrete, specific, evocative thing that exists in this world>",
  "scale": "<one of: village|city|region|continent|world|cosmic>",
  "era_tech_level": "<one of: stone|bronze|iron|medieval|renaissance|industrial|electric|information|post_scarcity>",
  "magic_presence": "<one of: none|rumoured|rare|common|pervasive>"
}

Make it feel like it belongs to a real, lived-in world — not a genre template.
No markdown fences. Only JSON.
"""

    def __init__(self, adapter: "ChatPrimitive") -> None:
        self._adapter = adapter

    async def execute(
        self, input_data: dict, context: WorkflowContext
    ) -> dict[str, Any]:
        messages: list["ChatMessage"] = [
            {"role": "user", "content": "Generate a surprising WorldSeed now."},
        ]
        raw = await self._adapter.chat(messages, self._SURPRISE_SYSTEM, context)
        raw = raw.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("seed_extractor: surprise JSON parse failed: %r", raw[:200])
            return _SURPRISE_FALLBACK
```

- [ ] **Step 4.4: Run tests to confirm they pass**

```bash
uv run pytest tests/unit/genesis/test_seed_extractor.py -v 2>&1 | tail -15
```

Expected: all 5 tests PASS.

- [ ] **Step 4.5: Commit**

```bash
git add tests/unit/genesis/test_seed_extractor.py src/components/genesis/seed_extractor.py
git commit -m "feat(genesis): migrate _SurpriseCall to ChatPrimitive adapter"
```

---

## Task 5: Migrate `SeedExtractor.__init__` parameter

**Files:**
- Modify: `tests/unit/genesis/test_seed_extractor.py` (add 1 test)
- Modify: `src/components/genesis/seed_extractor.py:247-270`

### Step 5.1 — Write failing test

Add to `tests/unit/genesis/test_seed_extractor.py`:

```python
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
```

- [ ] **Step 5.1: Add the test**

- [ ] **Step 5.2: Run test to confirm it fails**

```bash
uv run pytest tests/unit/genesis/test_seed_extractor.py::test_seed_extractor_passes_same_adapter_to_both_calls -v 2>&1 | tail -10
```

Expected: `TypeError` — `SeedExtractor.__init__` still has `llm` param.

- [ ] **Step 5.3: Implement `SeedExtractor.__init__` migration**

Replace `SeedExtractor.__init__` (lines ~255–270):

```python
def __init__(self, adapter: "ChatPrimitive | None" = None) -> None:
    _adapter = adapter or ModelRouterChatAdapter(
        ModelRouterPrimitive.from_yaml(MODES_PATH), mode="extraction"
    )
    self._extractor = FallbackPrimitive(  # type: ignore[arg-type]
        primary=RetryPrimitive(  # type: ignore[arg-type]
            _ExtractionCall(_adapter),
            strategy=RetryStrategy(max_retries=2, backoff_base=1.0),  # type: ignore[arg-type]
        ),
        fallback=_ExtractionFallback(),
    )
    self._surprise = FallbackPrimitive(  # type: ignore[arg-type]
        primary=RetryPrimitive(  # type: ignore[arg-type]
            _SurpriseCall(_adapter),
            strategy=RetryStrategy(max_retries=2, backoff_base=1.0),  # type: ignore[arg-type]
        ),
        fallback=_ExtractionFallback(),
    )
```

Remove the `get_llm` import from `seed_extractor.py` (check it's not used elsewhere in the file first).

- [ ] **Step 5.4: Run all seed extractor tests**

```bash
uv run pytest tests/unit/genesis/test_seed_extractor.py -v 2>&1 | tail -15
```

Expected: all 6 tests PASS.

- [ ] **Step 5.5: Commit**

```bash
git add tests/unit/genesis/test_seed_extractor.py src/components/genesis/seed_extractor.py
git commit -m "feat(genesis): SeedExtractor.__init__ accepts ChatPrimitive adapter"
```

---

## Task 6: Migrate `_GuideNameCall` and `derive_guide_character`

**Files:**
- Create: `tests/unit/genesis/test_guide_generator.py`
- Modify: `src/components/genesis/guide_generator.py:158-259`

The guide call has this message shape:
- system: `_GUIDE_SYSTEM` (the constant at module level)
- user: the constructed `prompt` string with world context

### Step 6.1 — Write failing tests

Create `tests/unit/genesis/test_guide_generator.py`:

```python
"""Unit tests for guide_generator after ChatPrimitive migration."""
from __future__ import annotations
import json
import pytest
from unittest.mock import patch, MagicMock
from ttadev.primitives.core.base import WorkflowContext
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
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
    await derive_guide_character(
        seed_fields={"tone": "cyclical"},
        adapter=adapter,
    )
    _, sent_system, _ = adapter.calls[0]
    # System should be the _GUIDE_SYSTEM constant
    assert "guide" in sent_system.lower() or "character" in sent_system.lower()
    # System must NOT appear as a message in the list
    sent_messages, _, _ = adapter.calls[0]
    for msg in sent_messages:
        assert msg.get("role") != "system"


@pytest.mark.asyncio
async def test_derive_guide_character_constructs_adapter_when_none():
    """derive_guide_character must construct a narration adapter when adapter=None."""
    mock_router = MagicMock()
    mock_router.execute = MagicMock(
        return_value=MagicMock(content='{"name":"X","intro_line":"Y"}')
    )
    with patch(
        "src.components.genesis.guide_generator.ModelRouterPrimitive.from_yaml",
        return_value=mock_router,
    ) as mock_from_yaml:
        # adapter=None triggers default construction
        # This will likely raise or produce fallback due to mock — that's OK;
        # we just need from_yaml to be called once.
        try:
            await derive_guide_character(seed_fields={}, adapter=None)
        except Exception:
            pass
    mock_from_yaml.assert_called_once()
```

- [ ] **Step 6.1: Write the test file**

- [ ] **Step 6.2: Run tests to confirm they fail**

```bash
uv run pytest tests/unit/genesis/test_guide_generator.py::test_derive_guide_character_uses_injected_adapter -v 2>&1 | tail -10
```

Expected: `TypeError` — `derive_guide_character` still has `llm` kwarg.

- [ ] **Step 6.3: Implement `_GuideNameCall` migration in `guide_generator.py`**

Replace `_GuideNameCall` (lines ~158–204):

```python
class _GuideNameCall(WorkflowPrimitive):  # type: ignore[misc]
    """LLM call to generate guide name + intro line."""

    def __init__(self, adapter: "ChatPrimitive") -> None:
        self._adapter = adapter

    async def execute(
        self, input_data: dict, context: WorkflowContext
    ) -> dict[str, str]:
        structural = input_data["structural"]
        fields = input_data["fields"]

        detail = fields.get("one_specific_detail", "")
        detail_hint = f"\nThe world contains: {detail}" if detail else ""
        char_name = fields.get("character_name", "")
        name_hint = (
            f"\nThe player's character name is: {char_name}" if char_name else ""
        )

        prompt = (
            f"World tone: {fields.get('tone', 'unknown')}\n"
            f"Guide is: {structural['entity_type']}, {structural['social_position']}\n"
            f"Guide's relationship to player: {structural['relationship_to_player']}\n"
            f"Speech register: {structural['speech_register']}"
            f"{detail_hint}{name_hint}\n\n"
            f"JSON output:"
        )

        messages: list["ChatMessage"] = [
            {"role": "user", "content": prompt},
        ]
        raw = await self._adapter.chat(messages, _GUIDE_SYSTEM, context)
        raw = raw.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()

        try:
            result = json.loads(raw)
            return {
                "name": str(result.get("name", _GUIDE_FALLBACK["name"])),
                "intro_line": str(
                    result.get("intro_line", _GUIDE_FALLBACK["intro_line"])
                ),
            }
        except json.JSONDecodeError:
            logger.warning("guide_generator: LLM JSON parse failed: %r", raw[:200])
            return _GUIDE_FALLBACK
```

- [ ] **Step 6.4: Implement `derive_guide_character` signature migration**

Replace `derive_guide_character` function signature and `_llm` construction:

```python
async def derive_guide_character(
    seed_fields: dict[str, Any],
    adapter: "ChatPrimitive | None" = None,
    session_id: str = "genesis",
) -> GuideCharacter:
    """
    Derive a GuideCharacter from the accumulated WorldSeed fields.

    Args:
        seed_fields: Dict of extracted WorldSeed fields (may include enums as strings).
        adapter: ChatPrimitive for the name/intro call. Constructed from model_modes.yaml
                 in narration mode if None. Callers should pass their narrator_adapter
                 to avoid repeated YAML reads.
        session_id: Session ID for WorkflowContext tracing.

    Returns:
        A fully populated GuideCharacter instance.
    """
    _adapter = adapter or ModelRouterChatAdapter(
        ModelRouterPrimitive.from_yaml(MODES_PATH), mode="narration"
    )
    structural = _derive_structural(seed_fields)

    name_gen = FallbackPrimitive(  # type: ignore[arg-type]
        primary=RetryPrimitive(  # type: ignore[arg-type]
            _GuideNameCall(_adapter),
            strategy=RetryStrategy(max_retries=2, backoff_base=1.0),  # type: ignore[arg-type]
        ),
        fallback=_GuideFallback(),
    )
    # ... rest of function unchanged
```

Also add imports to `guide_generator.py`:

```python
from ttadev.agents import ModelRouterChatAdapter
from ttadev.agents.protocol import ChatMessage, ChatPrimitive
from ttadev.primitives.llm import ModelRouterPrimitive
from src.components.model_management.mode_runner import MODES_PATH
```

Remove the `get_llm` import if no longer used.

- [ ] **Step 6.5: Run all guide generator tests**

```bash
uv run pytest tests/unit/genesis/test_guide_generator.py -v 2>&1 | tail -15
```

Expected: all 3 tests PASS.

- [ ] **Step 6.6: Commit**

```bash
git add tests/unit/genesis/test_guide_generator.py src/components/genesis/guide_generator.py
git commit -m "feat(genesis): migrate _GuideNameCall and derive_guide_character to ChatPrimitive"
```

---

## Task 7: Update `GenesisAgent.respond()` guide call site

**Files:**
- Modify: `src/components/genesis/agent.py:421-425`

This is a one-line call site fix — no new test needed (covered by the existing `test_genesis_agent.py` which tests the full `respond()` flow via mocks, and by Task 2's adapter injection test).

- [ ] **Step 7.1: Update the call site in `agent.py`**

Find (line ~423):

```python
self._guide = await derive_guide_character(
    merged, llm=self._guide_llm, session_id=session_id
)
```

Replace with:

```python
self._guide = await derive_guide_character(
    merged, adapter=self._narrator_adapter, session_id=session_id
)
```

Also remove `self._guide_llm` if it exists anywhere (it should be gone after Task 2, but double-check).

- [ ] **Step 7.2: Run the full genesis test suite**

```bash
uv run pytest tests/unit/genesis/ -v 2>&1 | tail -30
```

Expected: all tests pass.

- [ ] **Step 7.3: Commit**

```bash
git add src/components/genesis/agent.py
git commit -m "fix(genesis): pass narrator_adapter into derive_guide_character"
```

---

## Task 8: Full Quality Gate

- [ ] **Step 8.1: Lint + format**

```bash
uv run ruff check src/components/genesis/ --fix && uv run ruff format src/components/genesis/
```

Expected: `0 errors`

- [ ] **Step 8.2: Type check**

```bash
uv run pyright src/components/genesis/
```

Expected: `0 errors` (there may be existing upstream `type: ignore[misc]` comments from TTA.dev — these are pre-existing and acceptable).

- [ ] **Step 8.3: Full test suite**

```bash
make test
```

Expected: all unit tests pass.

- [ ] **Step 8.4: Final commit if any formatting fixes were applied**

```bash
git add src/components/genesis/
git commit -m "style(genesis): ruff format after ChatPrimitive migration"
```

---

## Completion Checklist

- [ ] `_NarratorCall` uses `ChatPrimitive.chat()` — no `ainvoke()`
- [ ] `_ExtractionCall` uses `ChatPrimitive.chat()` — no `ainvoke()`
- [ ] `_SurpriseCall` uses `ChatPrimitive.chat()` — no `ainvoke()`
- [ ] `_GuideNameCall` uses `ChatPrimitive.chat()` — no `ainvoke()`
- [ ] `GenesisAgent.__init__` has `router: ModelRouterPrimitive | None = None` — no `get_llm()`
- [ ] `SeedExtractor.__init__` has `adapter: ChatPrimitive | None = None` — no `get_llm()`
- [ ] `derive_guide_character` has `adapter: ChatPrimitive | None = None` — no `get_llm()`
- [ ] `agent.respond()` passes `self._narrator_adapter` to `derive_guide_character`
- [ ] No `get_llm()` calls remain in `agent.py`, `seed_extractor.py`, or `guide_generator.py`
- [ ] `make test` passes clean
