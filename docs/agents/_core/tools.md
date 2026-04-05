# Tool Protocols

These tools are available in every TTA development session. Use them deliberately.

## Serena — Structural code navigation

Prefer Serena over Grep/Glob for structural questions.

| Question | Tool |
|---|---|
| "What calls `X`?" | `mcp__plugin_serena_serena__find_referencing_symbols` |
| "What's defined in module Y?" | `mcp__plugin_serena_serena__get_symbols_overview` |
| "Show me the body of class/function Z" | `mcp__plugin_serena_serena__find_symbol` |

- Before any refactor: map all references to the target symbol with Serena first
- At session start: call `mcp__plugin_serena_serena__check_onboarding_performed` to confirm Serena is oriented

## CGC — Code graph analysis

Use before large refactors and for impact analysis.

| Use case | Tool |
|---|---|
| Scope a refactor | `mcp__codegraphcontext__analyze_code_relationships` |
| Find unused code | `mcp__codegraphcontext__find_dead_code` |
| Complexity hotspots | `mcp__codegraphcontext__find_most_complex_functions` |
| Semantic search | `mcp__codegraphcontext__find_code` |

CGC worktree note: orientation hook blocks Write calls in git worktrees.
Fix: create `/tmp/tta_hooks/<session-id>/cgc_oriented` manually, or symlink `scripts/hooks`.

## Hindsight — Persistent cross-session memory

MCP server: `http://localhost:8888/mcp/` | Start: `uvx --from hindsight-api hindsight-local-mcp`

**Every session start:**
1. `mcp__hindsight__recall` → `adam-global` — cross-project directives and preferences
2. `mcp__hindsight__recall` → `tta` — TTA-specific architecture, decisions, known issues

**After significant tasks:**
- Cross-project patterns → `adam-global`
- TTA-specific decisions, failures, patterns → `tta`

Rules: use `document_id` for evolving notes (same ID = upsert). Never retain secrets.
If Hindsight is unavailable, say so and continue — never pretend recall happened.

## Other MCP servers

- **Context7** — fetch current library/framework docs before implementing against an API
- **Sequential Thinking** — break down complex multi-step refactoring workflows
- **Redis MCP** — inspect session state and debug cache issues directly
