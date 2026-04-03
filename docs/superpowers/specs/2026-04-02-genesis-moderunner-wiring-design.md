# Genesis → ModeRunner Wiring Design

**Date:** 2026-04-02
**Status:** Approved
**Scope:** Wire the three Genesis LLM calls to TTA.dev's `ModelRouterChatAdapter` (Approach A — direct injection)

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
| `ChatMessage` | `ttadev.agents.protocol` | Typed dict `{"role": "user"/"assistant", "content": str}` |
| `ChatPrimitive` | `ttadev.agents.protocol` | Protocol type hint for the adapter |

`ModelRouterChatAdapter` already handles message flattening and system prompt injection
internally — no custom flatten helper is needed.

---

## Architecture

```
Before:
  GenesisAgent.__init__ → get_llm(temp=0.85) → _NarratorCall._llm.ainvoke(messages)
  SeedExtractor.__init__ → get_llm(temp=0.1)  → _ExtractorCall._llm.ainvoke(messages)
  guide_generator()      → get_llm(temp=0.8)  → _GuideCall._llm.ainvoke(messages)

After:
  GenesisAgent.__init__ → ModelRouterChatAdapter(router, mode="narration")
                            → _NarratorCall.adapter.chat(messages, system, ctx)
  SeedExtractor.__init__ → ModelRouterChatAdapter(router, mode="extraction")
                            → _ExtractorCall.adapter.chat(messages, system, ctx)
  guide_generator()      → ModelRouterChatAdapter(router, mode="narration")
                            → adapter.chat(messages, system, ctx)
```

`first_scene_synthesis.py` is out of scope — it is post-genesis and has distinct ownership.

---

## Components

### 1. `_NarratorCall` (`agent.py:113`)

Replace `_llm: Any` with `_adapter: ChatPrimitive`. Convert LangChain message objects to
`ChatMessage` typed dicts and delegate to `adapter.chat()`:

```python
class _NarratorCall(WorkflowPrimitive):
    def __init__(self, adapter: ChatPrimitive) -> None:
        self._adapter = adapter

    async def execute(self, input_data: dict, context: WorkflowContext) -> str:
        system_prompt: str = input_data["system_prompt"]
        history: list = input_data["history"]
        player_input: str = input_data["player_input"]

        messages: list[ChatMessage] = []
        for msg in history:
            role = "assistant" if msg.__class__.__name__ == "AIMessage" else "user"
            messages.append({"role": role, "content": msg.content})
        if player_input:
            messages.append({"role": "user", "content": player_input})

        content = await self._adapter.chat(messages, system_prompt, context)
        return content.strip()
```

### 2. `GenesisAgent.__init__` (`agent.py:338`)

Replace `narrator_llm`, `extractor_llm`, `guide_llm` parameters (raw LLM objects) with a single
`chat_adapter: ChatPrimitive | None = None`. When `None`, construct a
`ModelRouterChatAdapter(ModelRouterPrimitive.from_yaml(...), mode="narration")` internally.
Pass the adapter into `_NarratorCall` and `SeedExtractor`.

### 3. `SeedExtractor.__init__` (`seed_extractor.py:255`)

Replace `llm` parameter with `chat_adapter: ChatPrimitive | None = None`. Construct a
`ModelRouterChatAdapter(..., mode="extraction")` when `None`. The inner `_ExtractorCall.execute()`
calls `adapter.chat(messages, system, ctx)`.

### 4. `derive_guide_character()` (`guide_generator.py:238`)

Replace the `llm` kwarg with `chat_adapter: ChatPrimitive | None = None`. Construct a
`ModelRouterChatAdapter(..., mode="narration")` when `None`. Guide shares the `narration`
cascade — narration models produce better prose than a separate guide-specific mode would.

---

## Data Flow

```
GenesisAgent.process_turn(player_input)
  → build system_prompt (get_system_prompt(act, world_context))
  → FallbackPrimitive.execute({system_prompt, history, player_input})
      → RetryPrimitive (max 2 retries, 1.5x backoff)
          → _NarratorCall.execute()
              → convert LangChain msgs → list[ChatMessage]
              → ModelRouterChatAdapter.chat(messages, system_prompt, ctx)
                  → ModelRouterPrimitive → cascade tier selection
              → returns content str
              → returns content.strip()
      → on exhaustion → _NarratorFallback returns _SAFE_FALLBACK
```

---

## Error Handling

- **Resilience stack unchanged.** `call_with_meta()` raises on failure identically to `ainvoke()`.
  `RetryPrimitive` catches and retries; `FallbackPrimitive` catches and invokes `_NarratorFallback`.
- **Cascade exhaustion.** `ModeRunner` raises before returning if all tiers fail — this surfaces
  to `RetryPrimitive` as a normal exception.
- **Parallel extraction.** `SeedExtractor` runs concurrently per turn. `ModeRunner` is stateless;
  sharing a single instance across concurrent calls is safe.

---

## Out of Scope

- `first_scene_synthesis.py` — post-genesis, separate ownership, separate PR.
- Temperature / max_tokens per-call overrides — these are baked into `model_modes.yaml` per mode.
  The per-call values that `get_llm()` accepted are dropped; `narration` and `extraction` modes
  already have appropriate defaults.
- Adding a `genesis_narration` mode to `model_modes.yaml` — deferred until there is evidence
  that per-act token tuning is needed.

---

## Testing

Follow strict TDD: one failing test → implementation → pass → next test.

| Test | Location | What it verifies |
|---|---|---|
| `_NarratorCall` accepts `ChatPrimitive`, not raw LLM | `tests/unit/genesis/test_narrator_call.py` | Constructor signature changed |
| LangChain `AIMessage` → `{"role": "assistant", ...}` conversion | same file | Message conversion logic |
| LangChain `HumanMessage` → `{"role": "user", ...}` conversion | same file | Message conversion logic |
| `GenesisAgent` constructs `ModelRouterChatAdapter` when none provided | `tests/unit/genesis/test_genesis_agent.py` | Default injection |
| `SeedExtractor` routes to `"extraction"` mode | `tests/unit/genesis/test_seed_extractor.py` | Mode string passed to adapter |
| `derive_guide_character` routes to `"narration"` mode | `tests/unit/genesis/test_guide_generator.py` | Shared cascade decision |

All new tests use a mock `ChatPrimitive` (stub with a `chat()` coroutine) — no network calls.
