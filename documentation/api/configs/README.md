# Tool Policy Configuration Examples

The tool policy system supports configuration via YAML/JSON file referenced by the environment variable `TTA_TOOL_POLICY_CONFIG`, with environment variables as a fallback. This README shows how to configure common scenarios.

## Using a YAML file

Create a YAML file and set `TTA_TOOL_POLICY_CONFIG=/absolute/path/to/policy.yaml`.

```yaml
# docs/configs/policy_permissive.yaml
callable_allowlist: []  # empty means allowlist disabled (all callables allowed)
allow_network_tools: true
allow_filesystem_tools: true
allow_process_tools: true
# Optional limits
default_timeout_ms: 2000
max_concurrency: 8
cpu_limit_percent: 80
memory_limit_mb: 1024
```

```yaml
# docs/configs/policy_locked_down.yaml
callable_allowlist:
  - "my.package.safe_fn"
  - "another.mod.fn"
allow_network_tools: false
allow_filesystem_tools: false
allow_process_tools: false
default_timeout_ms: 250
```

## Using a JSON file

```json
{
  "callable_allowlist": ["my.package.safe_fn"],
  "allow_network_tools": true,
  "allow_filesystem_tools": false,
  "allow_process_tools": false,
  "default_timeout_ms": 500
}
```

## Environment variable fallbacks

If no file is provided, or to override file values, set env vars:
- `TTA_ALLOWED_CALLABLES` — comma-separated allowlist of dotted paths
- `TTA_ALLOW_NETWORK_TOOLS` — true/false
- `TTA_ALLOW_FILESYSTEM_TOOLS` — true/false
- `TTA_ALLOW_PROCESS_TOOLS` — true/false
- `TTA_TOOL_TIMEOUT_MS` — integer timeout (ms)
- `TTA_TOOL_MAX_CONCURRENCY` — integer
- `TTA_TOOL_CPU_LIMIT_PERCENT` — integer
- `TTA_TOOL_MEMORY_LIMIT_MB` — integer

Example:

```bash
export TTA_ALLOWED_CALLABLES=my.package.safe_fn
export TTA_ALLOW_NETWORK_TOOLS=false
export TTA_TOOL_TIMEOUT_MS=100
```

## Notes
- File config values are loaded first, then environment variables override any matching keys.
- If YAML is used, ensure PyYAML is installed; otherwise JSON is recommended.
- Synchronous timeouts are best-effort and cannot forcibly terminate the running work; they raise `TimeoutError` while work may continue in a background thread.
