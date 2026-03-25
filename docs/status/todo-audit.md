# TODO & GitHub Audit

This document is the entry point for TODO hygiene in TTA.

## Current status

- The old `.augment/TODO-AUDIT.md` and `.augment/README-TODO-AUDIT.md` files are no
  longer present.
- `scripts/todo-audit.py` is now the source of truth for live TODO, issue, and
  milestone state.
- Historical counts in earlier versions of this document should be treated as
  snapshots, not current project state.

## What the audit script does

`scripts/todo-audit.py` combines three views of project state:

- tracked code TODOs from the current repository
- live GitHub issues from `gh issue list`
- live GitHub milestones from `gh api`

Supported commands:

```bash
python3 scripts/todo-audit.py scan
python3 scripts/todo-audit.py orphans
python3 scripts/todo-audit.py sync
python3 scripts/todo-audit.py report
python3 scripts/todo-audit.py report --format json
```

## Recommended workflow

### Daily

```bash
python3 scripts/todo-audit.py report
python3 scripts/todo-audit.py scan
```

### Before starting a workstream

```bash
python3 scripts/todo-audit.py report
python3 scripts/todo-audit.py orphans
```

### Before release or milestone review

```bash
python3 scripts/todo-audit.py sync
python3 scripts/todo-audit.py report --format json
```

## Best practice for TODO comments

Prefer TODOs that can be traced back to a GitHub issue when one exists:

```python
# TODO(#55): Implement component registry module
# TODO: Remove temporary fallback after auth persistence lands
```

Avoid vague TODOs that do not describe the missing behavior:

```python
# TODO: fix this
```

## Milestone hygiene

- Treat GitHub milestones as the live planning surface.
- Treat `docs/milestones/` as historical or explanatory documentation unless a
  milestone document explicitly says otherwise.
- If script output and a milestone doc disagree, trust the script and GitHub,
  then update the doc.

## Related files

- `scripts/todo-audit.py`
- `docs/status/current-sprint.md`
- `docs/milestones/milestone-2-tracking.md`
