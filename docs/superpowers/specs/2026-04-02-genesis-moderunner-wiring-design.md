# Genesis → ModelRouterChatAdapter Wiring Design

**Date:** 2026-04-02
**Status:** Approved
**Scope:** Wire the three Genesis LLM call sites to TTA.dev's `ModelRouterChatAdapter` (Approach A — direct injection)

---

## Problem

`GenesisAgent`, `SeedExtractor`, and `guide_generator` each construct their own LLM client
via `get_llm()` (LangChain). This bypasses the 9-tier narration cascade and extraction routing
configured in `model_modes.yaml`, makes provider selection invisible, and couples Genesis
directly to the LangChain interface.

## Goal

Replace all `get_llm()` calls in the Genesis codebase with TTA.dev's `ModelRouterChatAdapter`,
routing narrator/guide calls through the `narration` mode and extraction calls through the
`extraction` mode. The existing `FallbackPrimitive`/`RetryPrimitive` resilience stack is
preserved unchanged.

---

## TTA.dev Assets Used

| Asset | Import | Purpose |
|---|---|---|
| `ModelRouterPrimitive` | `ttadev.primitives.llm` | YAML-configured cascade router |
| `ModelRouterChatAdapter` | `ttadev.agents` | Bridges router to `chat(messages, system, ctx) → str` |
| `ChatMessage` | `ttadev.agents.protocol` | TypedDict `{"role": "user"/"assistant"/"system", "content": str}` |
| `ChatPrimitive` | `ttadev.agents.protocol` | Protocol type hint for the adapter |

---

## Architecture

```
Before:
  GenesisAgent.__init__ → get_llm(temp=0.85) → _NarratorCall._llm.ainvoke(messages)
  SeedExtractor.__init__ → get_llm(temp=0.1)  → _ExtractionCall._llm.ainvoke(messages)
                                               → _SurpriseCall._llm.ainvoke(messages)
  guide_generator()      → get_llm(temp=0.8)  → _GuideCall._llm.ainvoke(messages)

After:
  GenesisAgent.__init__ → router: ModelRouterPrimitive
                            → narrator_adapter = ModelRouterChatAdapter(router, mode="narration")
                            → _NarratorCall(narrator_adapter).chat(messages, system, ctx)
  SeedExtractor.__init__ → extraction_adapter = ModelRouterChatAdapter(router, mode="extraction")
                            → _ExtractionCall(extraction_adapter).chat(messages, system, ctx)
                            → _SurpriseCall(extraction_adapter).chat(messages, system, ctx)
  derive_guide_character() → narrator_adapter passed in from GenesisAgent
                            → _GuideCall(narrator_adapter).chat(messages, system, ctx)
```

`first_scene_synthesis.py` is out of scope — it is post-genesis and has distinct ownership.

---

## Message Flattening Tradeoff

`ModelRouterChatAdapter.chat()` collapses the full message list into a single flat prompt string
(system prompt + messages joined with `\n\n`, assistant turns prefixed with `[assistant]:`).
This is the same pattern already used in `simulate_run.py`, which achieves 80% coherence on
30-turn runs. **Multi-turn structure is not preserved as a proper chat array** — this is an
accepted tradeoff for moving off LangChain. Genesis sessions are short enough (7 acts, ≤ ~15
turns per session) that flat-prompt coherence is acceptable.

`SystemMessage` objects are **never** present in the `history` list passed to `_NarratorCall`.
The system prompt travels separately via the `system=` argument to `adapter.chat()`. Role
conversion therefore handles exactly two types: `AIMessage` → `"assistant"`, everything else →
`"user"`.

**Adapter limitation:** `ModelRouterChatAdapter.chat()` silently ignores any `ChatMessage` with
`role="system"` in the `messages` list. The system prompt must always travel via the `system=`
kwarg — never as a message in the list.

---

## Components

### 1. `_NarratorCall` (`agent.py:113`)

Replace `_llm: Any` with `_adapter: ChatPrimitive`. Convert LangChain message objects to
`ChatMessage` typed dicts (two roles only — see tradeoff note above):

```python
class _NarratorCall(WorkflowPrimitive):
    def __init__(self, adapter: ChatPrimitive) -> None:
        self._adapter = adapter

    async def execute(self, input_data: dict, context: WorkflowContext) -> str:
        system_prompt: str = input_data["system_prompt"]
        history: list = input_data["history"]
        player_input: str = input_data["player_input"]

        messages: list[ChatMessage] = [
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

### 2. `GenesisAgent.__init__` (`agent.py:338`)

Replace `narrator_llm`, `extractor_llm`, `guide_llm` parameters with a single
`router: ModelRouterPrimitive | None = None`. When `None`, construct using `MODES_PATH`:

```python
from src.components.model_management.mode_runner import MODES_PATH
from ttadev.agents import ModelRouterChatAdapter
from ttadev.primitives.llm import ModelRouterPrimitive

_router = router or ModelRouterPrimitive.from_yaml(MODES_PATH)
self._narrator_adapter = ModelRouterChatAdapter(_router, mode="narration")
self._extraction_adapter = ModelRouterChatAdapter(_router, mode="extraction")
```

Pass `self._narrator_adapter` into `_NarratorCall` and store `self._extraction_adapter` for
`SeedExtractor`. Store `self._narrator_adapter` for passing into `derive_guide_character()`.

**Two distinct adapters are needed** — narrator/guide use `mode="narration"`, extraction uses
`mode="extraction"`. Both share the same underlying `ModelRouterPrimitive` instance.

### 3. `SeedExtractor.__init__` (`seed_extractor.py:255`)

Replace `llm` parameter with `adapter: ChatPrimitive | None = None`. When `None`, construct an
extraction adapter using `MODES_PATH`. Pass the **same** adapter to **both** `_ExtractionCall`
and `_SurpriseCall` — both primitive classes perform extraction-class tasks and must use the
`extraction` mode.

```python
from src.components.model_management.mode_runner import MODES_PATH
from ttadev.agents import ModelRouterChatAdapter
from ttadev.primitives.llm import ModelRouterPrimitive

_adapter = adapter or ModelRouterChatAdapter(
    ModelRouterPrimitive.from_yaml(MODES_PATH), mode="extraction"
)
# pass _adapter into both _ExtractionCall(_adapter) and _SurpriseCall(_adapter)
```

### 4. `_ExtractionCall` and `_SurpriseCall` (`seed_extractor.py`)

Both replace `_llm: Any` with `_adapter: ChatPrimitive`. Their `execute()` methods convert
messages and call `adapter.chat(messages, system, ctx)`.

### 5. `derive_guide_character()` (`guide_generator.py:238`)

Replace the `llm` kwarg with `adapter: ChatPrimitive | None = None`. When `None`, construct
`ModelRouterChatAdapter(ModelRouterPrimitive.from_yaml(MODES_PATH), mode="narration")`.

**Caller responsibility:** `GenesisAgent` already owns `self._narrator_adapter` — it should
pass this in rather than letting `derive_guide_character` construct its own adapter (avoids a
`from_yaml` file read per guide call). The `GenesisAgent.respond()` call site should become:

```python
guide = await derive_guide_character(seed_fields, adapter=self._narrator_adapter, ...)
```

---

## Error Handling

- **`model_modes.yaml` not found.** `ModelRouterPrimitive.from_yaml(MODES_PATH)` raises
  `FileNotFoundError` at construction time. `MODES_PATH` is an absolute path constant derived
  from the module file location — the same path already used by `ModeRunner` in the existing
  codebase, so this is not a new failure mode.
- **Cascade exhaustion.** `ModelRouterPrimitive` raises `RuntimeError("All N tiers failed")`
  when every tier fails. This surfaces to `RetryPrimitive` → `FallbackPrimitive` → fallback
  primitive as normal. No changes to error handling are needed.
- **Parallel extraction.** `SeedExtractor` runs concurrently per turn. `ModelRouterPrimitive`
  and `ModelRouterChatAdapter` are both stateless for concurrent use (the internal cooldown lock
  is not awaited in practice). Sharing one adapter instance is safe.

---

## Out of Scope

- `first_scene_synthesis.py` — post-genesis, separate ownership, separate PR.
- Temperature / max_tokens per-call overrides — baked into `model_modes.yaml` per mode.
- Adding a `genesis_narration` mode — deferred until evidence of per-act token tuning need.

---

## Testing

Follow strict TDD: one failing test → implementation → pass → next test.

| Test | Location | What it verifies |
|---|---|---|
| `_NarratorCall` accepts `ChatPrimitive`, not raw LLM | `tests/unit/genesis/test_narrator_call.py` | Constructor signature changed |
| `AIMessage` → `{"role": "assistant", ...}` conversion | same | Message conversion (assistant) |
| `HumanMessage` → `{"role": "user", ...}` conversion | same | Message conversion (user) |
| `GenesisAgent` constructs two adapters (narration + extraction) when no router provided | `tests/unit/genesis/test_genesis_agent.py` | Default injection, two modes |
| `SeedExtractor._ExtractionCall` routes to `"extraction"` mode | `tests/unit/genesis/test_seed_extractor.py` | Mode string passed to adapter |
| `SeedExtractor._SurpriseCall` routes to `"extraction"` mode | same | `_SurpriseCall` also migrated |
| `derive_guide_character` uses passed-in adapter (no new `from_yaml` call) | `tests/unit/genesis/test_guide_generator.py` | Caller-injected adapter |
| `derive_guide_character` constructs narration adapter when `adapter=None` | same | Default injection fallback |

All new tests use a mock `ChatPrimitive` (stub with an async `chat()` coroutine) — no network
calls. `ModelRouterPrimitive.from_yaml` is mocked at the module level where the default
construction path is tested.
