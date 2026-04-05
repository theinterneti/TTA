# Quality Gate & Standards

## Mandatory quality gate

**Run all three before finishing any task. All must pass.**

```bash
uv run ruff check src/ --fix && uv run ruff format src/
uv run pyright src/
make test
```

## Non-negotiable standards

| Constraint | Rule |
|---|---|
| Python version | 3.12+ (`requires-python = ">=3.12"`) |
| Package manager | `uv` only — never `pip install`, never `pip -e .` |
| Type hints | `str \| None` not `Optional[str]`; 3.10+ union syntax |
| Line length | 88 chars (Ruff) |
| Type checker | Pyright in `standard` mode |
| Test framework | pytest, `asyncio_mode = "auto"` |
| Commit style | Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`) |

## Strict boundaries

1. Never remove failing tests unless explicitly authorized by the repository owner
2. Follow AAA (Arrange-Act-Assert) pattern for all tests; 100% coverage for new code
3. Never push broken commits to `main` — branch and PR instead
4. Never commit `.log`, `.sqlite`, `.db`, coverage reports, or test output files
5. Never add `torch`, `transformers`, or GPU deps without explicit justification
6. Never add CI/CD workflows without strong justification (suite was reduced from 35 to 6)

## Common commands

```bash
uv sync --all-extras                                          # Install all deps
uv run ruff check src/ --fix && uv run ruff format src/      # Lint + format
uv run pyright src/                                           # Type check
make test                                                     # Unit tests (no services)
make test-integration                                         # Full suite (Neo4j + Redis)
make watch                                                    # Continuous unit tests
uv run pytest --cov=src --cov-report=term-missing tests/      # Coverage report
uv run python src/main.py start                               # Start API server
```
