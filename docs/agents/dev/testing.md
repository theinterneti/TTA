# Testing Reference

## Test tiers

| Tier | Marker | Requires | Command |
|---|---|---|---|
| Unit | (none) | Nothing | `make test` |
| Integration | `@pytest.mark.integration` | Redis + Neo4j | `make test-integration` |
| E2E / post-deploy | `@pytest.mark.e2e` | Live deployment | Never run locally |

## Test patterns

```python
# Unit test — no external services
async def test_something():
    # Arrange
    input_data = ProcessedInput(intent="explore", ...)
    # Act
    result = await process(input_data)
    # Assert
    assert result.status == "ok"

# Integration test — requires Redis
@pytest.mark.integration
@pytest.mark.redis
async def test_with_redis(redis_client):
    ...

# Integration test — requires Neo4j
@pytest.mark.integration
@pytest.mark.neo4j
async def test_with_neo4j(neo4j_driver):
    ...
```

## AAA pattern (mandatory)

Every test must follow Arrange-Act-Assert with clear separation:
```python
async def test_ipa_classifies_explore_intent():
    # Arrange
    agent = IPAAgent(llm=mock_llm)
    raw_input = "I want to look around the room"
    # Act
    result = await agent.process(raw_input)
    # Assert
    assert result.intent == Intent.EXPLORE
    assert result.intent_confidence > 0.8
```

## Coverage rules

- 100% coverage for all new code
- Run: `uv run pytest --cov=src --cov-report=term-missing tests/`
- Never commit with uncovered lines in new modules

## Continuous testing

```bash
make watch       # Reruns unit tests on every .py/.toml save
make watch-all   # Same, includes integration tests (needs Redis + Neo4j)
```

## Fixtures

`tests/conftest.py` provides fixtures with automatic mock fallbacks — if Redis/Neo4j
are not running, integration fixtures return mocks rather than failing.

Do **not** use `tests/post_deployment/` locally — these require a live deployment.
