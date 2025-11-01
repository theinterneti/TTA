# Agent Orchestration Tools: Configuration and Metrics

This document describes configuration keys, security models, caching, and metrics for the dynamic tools subsystem under `agent_orchestration.tools`.

## Configuration Keys

- redis_key_prefix (string, default: "ao")
- cache_ttl_s (number, default: 300): LRU TTL (seconds) for in-memory ToolSpec lookups.
- cache_max_items (int, default: 512): LRU capacity.
- max_schema_depth (int, default: 5): Maximum JSON-schema nesting for parameters/returns.
- max_prometheus_tools (int, default: 200): Limit number of unique tools exported with labels to Prometheus to control cardinality.
- allow_network_tools (bool, default: false)
- allow_filesystem_tools (bool, default: false)
- allow_process_tools (bool, default: false)
- allow_subprocess_tools (bool, default: false)
- allow_shell_exec (bool, default: false)
- allowed_callables (list[string], default: []): Dot-path allowlist for wrapped callables.
- max_idle_seconds (number, default: 86400): Consider tools unused beyond this idle time; subject to cleanup/deprecation policies.

### Example: Development

```
agent_orchestration:
  tools:
    redis_key_prefix: "ao-dev"
    cache_ttl_s: 120
    cache_max_items: 256
    max_schema_depth: 5
    allow_network_tools: true
    allow_filesystem_tools: true
    allowed_callables:
      - mypkg.tools.fetch_url
      - mypkg.tools.read_text
```

### Example: Production (hardened)

```
agent_orchestration:
  tools:
    redis_key_prefix: "ao"
    cache_ttl_s: 300
    cache_max_items: 512
    max_schema_depth: 5
    allow_network_tools: false
    allow_filesystem_tools: false
    allow_process_tools: false
    allow_subprocess_tools: false
    allow_shell_exec: false
    allowed_callables: []
    max_prometheus_tools: 100
    max_idle_seconds: 172800
```

## Security Model

- Safety flags on ToolSpec: ["network", "filesystem", "process", "subprocess", "shell"].
- ToolPolicy enforces allowlist controls for these flags; violations raise validation errors.
- `allowed_callables` controls which Python callables can be wrapped. If non-empty, any callable not present will be rejected.

## Caching and Performance

- In-memory LRU (per-process) caches ToolSpec objects with `cache_ttl_s` and `cache_max_items`.
- Choose smaller TTL for highly dynamic tool generation; larger TTL for stable tool sets to reduce Redis load.
- `max_idle_seconds` controls cleanup aggressiveness; lower values reduce memory/Redis usage but can deprecate rarely used tools sooner.

## Callable Registry

A thread-safe in-process CallableRegistry maps ToolSpec (name/version) to Python callables and supports "latest" version fallback. It is designed for pluggable backends if you want distributed resolution.

- Registration: register_callable(tool_name, version, callable_fn)
- Lookup: resolve_callable(spec) -> callable
- Extension: subclass CallableRegistry for Redis-backed or service-mesh-backed lookup, or introduce a new backend implementing the same methods.

Example:

```
from src.agent_orchestration.tools.callable_registry import CallableRegistry
creg = CallableRegistry()
creg.register_callable("math.add", "1.0.0", add)
fn = creg.resolve_callable(spec)  # spec.name="math.add", spec.version="1.0.0"
```

### Diagnostics execution endpoint

- POST /tools/execute (gated by agent_orchestration.diagnostics.allow_tool_execution=false by default)
- Body: {"tool_name": str, "version": str?, "arguments": dict}
- Security:
  - Optional API key via header X-AO-DIAG-KEY when agent_orchestration.diagnostics.tool_exec_api_key is set
  - Optional allowed tools filter agent_orchestration.diagnostics.allowed_tools: list of patterns like ["math.add:*", "kg.query:1.*"]
  - Per-process soft rate limit (agent_orchestration.diagnostics.max_tool_exec_per_min)
  - Timeout (agent_orchestration.diagnostics.tool_exec_timeout_s)
- Returns: {ok, result?, error?, duration_ms, metrics}

## Metrics and Diagnostics

- JSON `/metrics` includes:
  - `tools`: total, active, deprecated, cache stats
  - `tool_exec`: per-tool successes, failures, error_rate, avg_ms, histogram buckets
- Prometheus `/metrics-prom` includes:
  - agent_orchestration_tool_invocations_total{tool,version}
  - agent_orchestration_tool_success_total{tool,version}
  - agent_orchestration_tool_failure_total{tool,version}
  - agent_orchestration_tool_duration_seconds_bucket{tool,version,...}
  - Export respects `max_prometheus_tools` to limit cardinality.

## Tools Management API

- GET `/tools`: returns list of tools with status and metadata.
- GET `/tools/summary`: pagination and filtering with query params:
  - `page`, `limit`, `status`, `name_prefix`, `sort_by` (last_used_at|name|version|status), `order` (asc|desc)
  - Includes summary counts and naive most/least used derivations from in-memory metrics.
