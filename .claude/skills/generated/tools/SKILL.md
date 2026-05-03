---
name: tools
description: "Skill for the Tools area of TTA. 84 symbols across 19 files."
---

# Tools

84 symbols | 19 files | Cohesion: 89%

## When to Use

- Working with code in `src/`
- Understanding how record_success, record_failure, tool_exec_context work
- Modifying tools-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/tools/test_cursor.py` | test_encode_decode_roundtrip, test_expired_cursor_rejected, test_create_cursor_convenience, test_different_secret_keys_incompatible, test_tampering_always_detected (+6) |
| `src/agent_orchestration/tools/metrics.py` | _key, record_success, record_failure, _wrapped, _awaitable (+3) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py` | _key, record_success, record_failure, _wrapped, _awaitable (+3) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/tools/redis_tool_registry.py` | _key, _status_key, register_tool, get_tool, list_tools (+2) |
| `src/agent_orchestration/tools/redis_tool_registry.py` | _key, _status_key, register_tool, deprecate_tool, cleanup_expired (+2) |
| `src/agent_orchestration/tools/cursor.py` | encode_cursor, create_cursor, decode_cursor, is_valid_cursor, get_cursor_manager |
| `src/agent_orchestration/tools/response_utils.py` | success_response, error_response, async_wrapper, sync_wrapper |
| `src/agent_orchestration/tools/models.py` | _effective, is_capability_allowed, validate_safety_flags, check_safety |
| `src/agent_orchestration/tools/invocation_service.py` | _callable_dotted_path, invoke_tool, invoke_tool_by_spec, register_and_invoke |
| `packages/tta-ai-framework/src/tta_ai/orchestration/tools/response_utils.py` | success_response, error_response, async_wrapper, sync_wrapper |

## Entry Points

Start here when exploring this area:

- **`record_success`** (Function) — `src/agent_orchestration/tools/metrics.py:71`
- **`record_failure`** (Function) — `src/agent_orchestration/tools/metrics.py:76`
- **`tool_exec_context`** (Function) — `src/agent_orchestration/tools/metrics.py:132`
- **`run_with_metrics`** (Function) — `src/agent_orchestration/tools/metrics.py:146`
- **`get_tool_metrics`** (Function) — `src/agent_orchestration/tools/metrics.py:158`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `record_success` | Function | `src/agent_orchestration/tools/metrics.py` | 71 |
| `record_failure` | Function | `src/agent_orchestration/tools/metrics.py` | 76 |
| `tool_exec_context` | Function | `src/agent_orchestration/tools/metrics.py` | 132 |
| `run_with_metrics` | Function | `src/agent_orchestration/tools/metrics.py` | 146 |
| `get_tool_metrics` | Function | `src/agent_orchestration/tools/metrics.py` | 158 |
| `run_tool` | Function | `src/agent_orchestration/tools/coordinator.py` | 63 |
| `record_success` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py` | 71 |
| `record_failure` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py` | 76 |
| `tool_exec_context` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py` | 132 |
| `run_with_metrics` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py` | 146 |
| `get_tool_metrics` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py` | 156 |
| `run_tool` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/coordinator.py` | 57 |
| `test_encode_decode_roundtrip` | Function | `tests/unit/tools/test_cursor.py` | 44 |
| `test_expired_cursor_rejected` | Function | `tests/unit/tools/test_cursor.py` | 77 |
| `test_create_cursor_convenience` | Function | `tests/unit/tools/test_cursor.py` | 118 |
| `test_different_secret_keys_incompatible` | Function | `tests/unit/tools/test_cursor.py` | 131 |
| `test_tampering_always_detected` | Function | `tests/unit/tools/test_cursor.py` | 179 |
| `encode_cursor` | Function | `src/agent_orchestration/tools/cursor.py` | 94 |
| `create_cursor` | Function | `src/agent_orchestration/tools/cursor.py` | 237 |
| `test_tampered_cursor_rejected` | Function | `tests/unit/tools/test_cursor.py` | 65 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_tool → _key` | intra_community | 3 |
| `Run_tool → Tool_execution` | intra_community | 3 |

## How to Explore

1. `gitnexus_context({name: "record_success"})` — see callers and callees
2. `gitnexus_query({query: "tools"})` — find related execution flows
3. Read key files listed above for implementation details
