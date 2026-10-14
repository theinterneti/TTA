---
name: tools
description: "Skill for the Tools area of TTA. 86 symbols across 20 files."
---

# Tools

86 symbols | 20 files | Cohesion: 96%

## When to Use

- Working with code in `src/`
- Understanding how get_cursor_manager, tool_exec_context, run_with_metrics work
- Modifying tools-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/tools/test_cursor.py` | test_encode_decode_roundtrip, test_tampered_cursor_rejected, test_expired_cursor_rejected, test_future_timestamp_rejected, test_invalid_cursor_format (+6) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py` | _key, record_success, record_failure, _wrapped, _awaitable (+3) |
| `src/agent_orchestration/tools/metrics.py` | _key, record_success, record_failure, _wrapped, _awaitable (+3) |
| `src/agent_orchestration/tools/redis_tool_registry.py` | get_tool, list_tools, _key, _status_key, register_tool (+2) |
| `packages/tta-ai-framework/src/tta_ai/orchestration/tools/redis_tool_registry.py` | _key, _status_key, register_tool, deprecate_tool, cleanup_expired (+2) |
| `src/agent_orchestration/tools/cursor.py` | encode_cursor, decode_cursor, is_valid_cursor, create_cursor, get_cursor_manager |
| `packages/tta-ai-framework/src/tta_ai/orchestration/tools/invocation_service.py` | _callable_dotted_path, invoke_tool, invoke_tool_by_spec, register_and_invoke |
| `packages/tta-ai-framework/src/tta_ai/orchestration/tools/models.py` | _effective, is_capability_allowed, validate_safety_flags, check_safety |
| `packages/tta-ai-framework/src/tta_ai/orchestration/tools/response_utils.py` | success_response, error_response, async_wrapper, sync_wrapper |
| `src/agent_orchestration/tools/invocation_service.py` | _callable_dotted_path, invoke_tool, invoke_tool_by_spec, register_and_invoke |

## Entry Points

Start here when exploring this area:

- **`get_cursor_manager`** (Function) — `src/agent_orchestration/tools/cursor.py:273`
- **`tool_exec_context`** (Function) — `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py:132`
- **`run_with_metrics`** (Function) — `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py:146`
- **`get_tool_metrics`** (Function) — `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py:156`
- **`tool_exec_context`** (Function) — `src/agent_orchestration/tools/metrics.py:132`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `get_cursor_manager` | Function | `src/agent_orchestration/tools/cursor.py` | 273 |
| `tool_exec_context` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py` | 132 |
| `run_with_metrics` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py` | 146 |
| `get_tool_metrics` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/metrics.py` | 156 |
| `tool_exec_context` | Function | `src/agent_orchestration/tools/metrics.py` | 132 |
| `run_with_metrics` | Function | `src/agent_orchestration/tools/metrics.py` | 146 |
| `get_tool_metrics` | Function | `src/agent_orchestration/tools/metrics.py` | 158 |
| `success_response` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/response_utils.py` | 32 |
| `error_response` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/response_utils.py` | 82 |
| `async_wrapper` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/response_utils.py` | 248 |
| `sync_wrapper` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/response_utils.py` | 275 |
| `success_response` | Function | `src/agent_orchestration/tools/response_utils.py` | 32 |
| `error_response` | Function | `src/agent_orchestration/tools/response_utils.py` | 82 |
| `async_wrapper` | Function | `src/agent_orchestration/tools/response_utils.py` | 247 |
| `sync_wrapper` | Function | `src/agent_orchestration/tools/response_utils.py` | 274 |
| `load_tool_policy_config` | Function | `packages/tta-ai-framework/src/tta_ai/orchestration/tools/policy_config.py` | 93 |
| `audit_tools` | Function | `scripts/tools/audit_tools.py` | 63 |
| `main` | Function | `scripts/tools/audit_tools.py` | 131 |
| `load_tool_policy_config` | Function | `src/agent_orchestration/tools/policy_config.py` | 94 |
| `encode_cursor` | Method | `src/agent_orchestration/tools/cursor.py` | 94 |

## How to Explore

1. `context({name: "get_cursor_manager"})` — see callers and callees
2. `query({search_query: "tools"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
