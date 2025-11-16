# TTA Testing Strategies

## Environment-Specific Test Organization

### Development Environment - Unit Tests

**Location**: `tests/unit/`

**Purpose**: Fast, isolated tests for individual components

**Characteristics**:
- No external dependencies (mocked databases, APIs)
- Fast execution (< 1 second per test)
- High coverage of business logic
- Run on every commit via pre-commit hooks

**Example**:
```python
@pytest.mark.unit
async def test_workflow_definition_validation():
    """Test workflow definition validates correctly."""
    workflow = WorkflowDefinition(
        workflow_type=WorkflowType.NARRATIVE_GENERATION,
        agent_sequence=[AgentStep(agent=AgentType.STORYTELLER)]
    )
    assert workflow.workflow_type == WorkflowType.NARRATIVE_GENERATION
```

### Staging Environment - Integration Tests

**Location**: `tests/integration/`

**Purpose**: Validate component interactions with real dependencies

**Characteristics**:
- Real database connections (Redis, Neo4j)
- Multi-component workflows
- Moderate execution time (1-10 seconds per test)
- Run before staging deployment

**Example**:
```python
@pytest.mark.integration
@pytest.mark.redis
@pytest.mark.neo4j
async def test_story_creation_flow():
    """Test complete story creation with database persistence."""
    # Create story via API
    story = await create_story(title="Test Story")

    # Verify Redis state
    session_state = await redis_client.get(f"story:{story.id}")
    assert session_state is not None

    # Verify Neo4j graph
    story_node = await neo4j_client.get_story_node(story.id)
    assert story_node.title == "Test Story"
```

### Production Environment - End-to-End Tests

**Location**: `tests/e2e/`, `tests/e2e-staging/`

**Purpose**: Validate complete user journeys in production-like environment

**Characteristics**:
- Full system deployment (Docker Compose)
- Browser automation (Playwright)
- Real user workflows (OAuth → gameplay)
- Longer execution time (10-60 seconds per test)
- Run before production deployment

**Example**:
```typescript
// tests/e2e-staging/test_user_journey.spec.ts
test('complete user journey from OAuth to gameplay', async ({ page }) => {
  // OAuth sign-in
  await page.goto('http://localhost:3000');
  await page.click('text=Sign In');

  // Create character
  await page.fill('[name="character_name"]', 'Test Hero');
  await page.click('text=Start Adventure');

  // Verify gameplay
  await expect(page.locator('.story-text')).toBeVisible();
});
```

## pytest-asyncio Usage Patterns

### Fixture Decorator Validation

**Pre-commit Hook**: Validates all async fixtures use `@pytest_asyncio.fixture` (not `@pytest.fixture`)

**Correct Pattern**:
```python
import pytest_asyncio

@pytest_asyncio.fixture
async def redis_client():
    """Provide Redis client for tests."""
    client = await create_redis_client()
    yield client
    await client.close()
```

**Incorrect Pattern** (caught by pre-commit):
```python
import pytest

@pytest.fixture  # ❌ Wrong decorator for async fixture
async def redis_client():
    ...
```

### Async Test Patterns

**Standard async test**:
```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result == expected_value
```

**With fixtures**:
```python
@pytest.mark.asyncio
async def test_with_fixtures(redis_client, neo4j_client):
    await redis_client.set("key", "value")
    node = await neo4j_client.create_node({"type": "story"})
    assert node.id is not None
```

## Coverage Thresholds

### Staging Promotion Criteria

**Minimum Coverage**: **70%** overall

**Component-Specific**:
- Critical paths (authentication, story creation): **90%+**
- Business logic (agent orchestration, narrative engine): **80%+**
- Utilities and helpers: **70%+**
- UI components: **60%+** (focus on integration tests)

**Measurement**:
```bash
# Run with coverage
uvx pytest tests/ --cov=src --cov-report=term --cov-report=html

# Check threshold
uvx pytest tests/ --cov=src --cov-fail-under=70
```

**Enforcement**: CI/CD pipeline fails if coverage drops below threshold

### Coverage Discrepancy Investigation

**Preference**: Investigate and resolve coverage discrepancies before staging deployment, even when all quality checks pass. Strict adherence to maturity criteria over immediate deployment.

## Test Markers

### Database Markers

```python
@pytest.mark.redis      # Requires Redis connection
@pytest.mark.neo4j      # Requires Neo4j connection
@pytest.mark.database   # Requires any database
```

### Environment Markers

```python
@pytest.mark.unit           # Unit test (no external deps)
@pytest.mark.integration    # Integration test (real deps)
@pytest.mark.e2e           # End-to-end test (full system)
```

### Component Markers

```python
@pytest.mark.agent_orchestration
@pytest.mark.player_experience
@pytest.mark.narrative_engine
```

### Running Specific Tests

```bash
# Run only Redis tests
uvx pytest -m redis

# Run integration tests excluding slow ones
uvx pytest -m "integration and not slow"

# Run all tests for a component
uvx pytest -m agent_orchestration
```

## Integration Testing Approach

### Database Persistence Validation

**Philosophy**: Comprehensive integration testing validates complete system including **real database persistence** (Redis/Neo4j) rather than mock-only testing for production readiness.

**Pattern**:
```python
@pytest.mark.integration
@pytest.mark.redis
@pytest.mark.neo4j
async def test_story_persistence(redis_client, neo4j_client):
    """Validate story persists across Redis and Neo4j."""
    # Create story
    story_id = await create_story_session(redis_client)

    # Verify Redis state
    state = await redis_client.hgetall(f"story:{story_id}")
    assert state["status"] == "active"

    # Create narrative node
    node_id = await create_story_node(neo4j_client, story_id)

    # Verify Neo4j graph
    query = "MATCH (s:Story {id: $story_id}) RETURN s"
    result = await neo4j_client.run(query, story_id=story_id)
    assert result is not None

    # Verify cross-database consistency
    assert state["current_node"] == str(node_id)
```

## End-to-End Testing with Playwright

### Test Organization

**Location**: `tests/e2e-staging/`

**Configuration**: `playwright.staging.config.ts`

### Six Validation Areas

1. **Core User Journey**: OAuth sign-in → character creation → gameplay
2. **UI/UX Functionality**: Forms, buttons, navigation, responsive design
3. **Integration Points**: Database persistence, API calls, WebSocket connections
4. **Error Handling**: Network failures, validation errors, timeout scenarios
5. **Browser Compatibility**: Chromium, Firefox, WebKit
6. **Responsive Design**: Desktop, tablet, mobile viewports

### Playwright Patterns

**Wait Strategies**:
```typescript
// Wait for element
await page.waitForSelector('.story-text', { timeout: 5000 });

// Wait for network
await page.waitForResponse(resp => resp.url().includes('/api/story'));

// Wait for navigation
await page.waitForNavigation({ waitUntil: 'networkidle' });
```

**Screenshot/Video on Failure**:
```typescript
// playwright.staging.config.ts
export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});
```

### Success Criteria

- **Zero-instruction usability**: Players can navigate without documentation
- **Error-free flows**: No console errors, failed requests, or UI glitches
- **Data persistence**: All user actions persist correctly across sessions
- **Acceptable performance**: Page loads < 3s, interactions < 500ms

## Test Execution Workflow

### Local Development

```bash
# Run unit tests (fast)
uvx pytest tests/unit/ -v

# Run integration tests (requires databases)
docker-compose up -d redis neo4j
uvx pytest tests/integration/ -v

# Run E2E tests (requires full stack)
docker-compose -f docker-compose.staging.yml up -d
uvx playwright test
```

### CI/CD Pipeline

**PR Checks**:
1. Unit tests (all must pass)
2. Linting (ruff check)
3. Type checking (pyright)
4. Security scan (bandit, detect-secrets)

**Staging Deployment**:
1. Integration tests (all must pass)
2. Coverage check (≥70%)
3. E2E smoke tests (critical paths)

**Production Deployment**:
1. Full E2E test suite (all must pass)
2. Performance benchmarks
3. Security audit
4. Manual QA approval
