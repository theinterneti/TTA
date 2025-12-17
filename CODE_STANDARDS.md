# TTA Storytelling - Code Review Standards

> These are the coding standards that ALL code must follow before being committed.
> AI reviewers: Respond with `STATUS: PASSED` or `STATUS: FAILED` with specific violations.

## Python Code Standards

### Type Hints (REQUIRED)
- All function parameters MUST have type hints
- All function return types MUST be annotated
- Use `Optional[T]` or `T | None` for nullable types
- Never use `Any` without justification in a comment
- Use `TypedDict`, `Protocol`, or dataclasses for complex types

```python
# ❌ BAD
def process_data(data, options=None):
    pass

# ✅ GOOD
def process_data(data: dict[str, Any], options: ProcessOptions | None = None) -> ProcessResult:
    pass
```

### Error Handling
- Never use bare `except:` - always specify exception types
- Never use `except Exception:` without re-raising or logging
- Use custom exceptions for domain-specific errors
- Log errors with appropriate context before handling

```python
# ❌ BAD
try:
    result = api_call()
except:
    pass

# ✅ GOOD
try:
    result = api_call()
except HTTPError as e:
    logger.error("API call failed", exc_info=True, extra={"url": url})
    raise ServiceUnavailableError(f"External API failed: {e}") from e
```

### Import Organization
- Standard library imports first
- Third-party imports second (separated by blank line)
- Local imports third (separated by blank line)
- Use absolute imports, not relative imports for cross-module
- No `from module import *`
- No unused imports

### Function & Method Standards
- Functions should do ONE thing
- Maximum 50 lines per function (prefer < 25)
- Maximum 4 parameters (use dataclass/TypedDict for more)
- No mutable default arguments (`def f(items=[])`)
- Private methods should start with underscore

### Class Standards
- Use `@dataclass` for data containers
- Use Pydantic models for API request/response
- Prefer composition over inheritance
- Keep classes focused - single responsibility

### Documentation
- All public functions need docstrings
- Use Google-style docstrings format
- Document parameters, return types, and raises
- Include usage examples for complex functions

```python
def calculate_narrative_arc(events: list[Event], config: ArcConfig) -> NarrativeArc:
    """Calculate the narrative arc from a sequence of events.

    Args:
        events: Ordered list of story events to analyze.
        config: Configuration for arc calculation parameters.

    Returns:
        NarrativeArc containing tension curve and key points.

    Raises:
        ValueError: If events list is empty.
        InvalidEventSequenceError: If events have invalid timestamps.

    Example:
        >>> arc = calculate_narrative_arc(story.events, default_config)
        >>> arc.climax_point
        Event(id='evt_123', tension=0.95)
    """
```

### Security Standards
- No hardcoded secrets, API keys, or passwords
- Use environment variables for configuration
- Sanitize all user inputs before processing
- No SQL string concatenation - use parameterized queries
- No `eval()`, `exec()`, or `__import__()` on user input

### Async/Await Standards
- Don't mix sync and async in the same function
- Use `asyncio.gather()` for concurrent operations
- Always handle cancellation properly
- Use async context managers for resources

### Testing Standards (for test files)
- Test names should describe the scenario: `test_login_fails_with_invalid_password`
- Use pytest fixtures for setup
- Each test should test ONE behavior
- Use meaningful assertions with descriptive messages

## FastAPI Specific

### API Endpoints
- Use Pydantic models for request/response bodies
- Always specify response_model in route decorators
- Use proper HTTP status codes (201 for create, 204 for delete, etc.)
- Validate path parameters with Path()
- Add summary and description to endpoints

```python
# ❌ BAD
@router.post("/stories")
async def create_story(data: dict):
    return {"id": save(data)}

# ✅ GOOD
@router.post(
    "/stories",
    response_model=StoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new story",
    description="Creates a new story with the provided narrative elements."
)
async def create_story(
    story: StoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StoryResponse:
    """Create a new story in the system."""
```

### Dependency Injection
- Use `Depends()` for all dependencies
- Database sessions must be dependency-injected
- Authentication should be a dependency, not inline code

## Code Smell Indicators (Always Flag)

- `# TODO` or `# FIXME` without issue reference
- `print()` statements (use logging instead)
- Magic numbers without named constants
- Commented-out code blocks
- Functions with more than 3 levels of nesting
- Variables named `data`, `result`, `temp`, `x`, `i` (without context)
- Duplicate code blocks (DRY violation)
- Empty `except` blocks
- `time.sleep()` in async code

## Git Commit Message Standards

- Use conventional commits format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- Keep first line under 72 characters
- Reference issue numbers when applicable

---

**Remember:** If any standard is violated, the commit MUST fail. Be strict.


---
**Logseq:** [[TTA.dev/Code_standards]]
