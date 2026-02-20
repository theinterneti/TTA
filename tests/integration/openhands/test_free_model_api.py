"""

# Logseq: [[TTA.dev/Tests/Integration/Openhands/Test_free_model_api]]
Minimal API test for free model registry integration with OpenRouter.

This test validates that the free model registry can successfully interact with
the OpenRouter API using litellm. It tests the complete pipeline:
1. Environment configuration (API key loading)
2. Model initialization
3. API call execution
4. Response parsing
5. Error handling

The test uses DeepSeek Chat as it's verified to work reliably.
"""

import os

import pytest
from dotenv import load_dotenv

# Load .env file for API key
load_dotenv()


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def openrouter_api_key():
    """Load OPENROUTER_API_KEY from environment."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        pytest.skip("OPENROUTER_API_KEY not set in environment")
    return api_key


@pytest.fixture(scope="module")
def verified_model_id():
    """Return the verified working model ID from the registry."""
    # From free_models_registry.yaml - verified working model
    return "openrouter/deepseek/deepseek-chat"


# ============================================================================
# Basic API Call Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deepseek_chat_basic_call(openrouter_api_key, verified_model_id):
    """Test basic API call to DeepSeek Chat via OpenRouter.

    This test validates:
    - API key is valid
    - Model ID is correct
    - API endpoint is accessible
    - Response structure is correct
    - Basic text generation works
    """
    try:
        import litellm
    except ImportError:
        pytest.skip("litellm not installed")

    # Configure litellm for OpenRouter
    litellm.api_key = openrouter_api_key

    # Simple test prompt
    messages = [{"role": "user", "content": "Say 'Hello, TTA!' and nothing else."}]

    try:
        # Make API call
        response = await litellm.acompletion(
            model=verified_model_id,
            messages=messages,
            max_tokens=50,
            temperature=0.1,  # Low temperature for deterministic response
            timeout=30.0,
        )

        # Validate response structure
        assert response is not None, "Response is None"
        assert hasattr(response, "choices"), "Response missing 'choices'"
        assert len(response.choices) > 0, "Response has no choices"

        # Extract and validate content
        content = response.choices[0].message.content
        assert content is not None, "Response content is None"
        assert len(content) > 0, "Response content is empty"
        assert isinstance(content, str), (
            f"Response content is not string: {type(content)}"
        )

        # Validate usage information
        assert hasattr(response, "usage"), "Response missing 'usage'"
        assert response.usage.total_tokens > 0, "Total tokens is 0"

    except Exception as e:
        # Skip on authentication/authorization failures (invalid/expired key)
        err_str = str(e).lower()
        if any(
            kw in err_str
            for kw in ("401", "unauthorized", "authentication", "user not found")
        ):
            pytest.skip(f"OPENROUTER_API_KEY is set but invalid/expired: {e}")
        pytest.fail(f"API call failed: {type(e).__name__}: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_response_parsing(openrouter_api_key, verified_model_id):
    """Test response parsing and structure validation.

    This test validates:
    - Response has expected structure
    - All required fields are present
    - Data types are correct
    - Usage metrics are populated
    """
    try:
        import litellm
    except ImportError:
        pytest.skip("litellm not installed")

    litellm.api_key = openrouter_api_key

    messages = [
        {"role": "user", "content": "What is 2+2? Answer with just the number."}
    ]

    try:
        response = await litellm.acompletion(
            model=verified_model_id,
            messages=messages,
            max_tokens=10,
            temperature=0.0,
            timeout=30.0,
        )

        # Validate response object structure
        assert hasattr(response, "id"), "Response missing 'id'"
        assert hasattr(response, "model"), "Response missing 'model'"
        assert hasattr(response, "choices"), "Response missing 'choices'"
        assert hasattr(response, "usage"), "Response missing 'usage'"

        # Validate choices structure
        choice = response.choices[0]
        assert hasattr(choice, "message"), "Choice missing 'message'"
        assert hasattr(choice.message, "content"), "Message missing 'content'"
        assert hasattr(choice.message, "role"), "Message missing 'role'"
        assert choice.message.role == "assistant", (
            f"Unexpected role: {choice.message.role}"
        )

        # Validate usage structure
        usage = response.usage
        assert hasattr(usage, "prompt_tokens"), "Usage missing 'prompt_tokens'"
        assert hasattr(usage, "completion_tokens"), "Usage missing 'completion_tokens'"
        assert hasattr(usage, "total_tokens"), "Usage missing 'total_tokens'"

        # Validate usage values
        assert usage.prompt_tokens > 0, "Prompt tokens is 0"
        assert usage.completion_tokens > 0, "Completion tokens is 0"
        assert usage.total_tokens == usage.prompt_tokens + usage.completion_tokens, (
            "Total tokens doesn't match sum"
        )

    except Exception as e:
        err_str = str(e).lower()
        if any(
            kw in err_str
            for kw in ("401", "unauthorized", "authentication", "user not found")
        ):
            pytest.skip(f"OPENROUTER_API_KEY is set but invalid/expired: {e}")
        pytest.fail(f"Response parsing failed: {type(e).__name__}: {e}")


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_api_key_handling():
    """Test error handling for invalid API key.

    This test validates:
    - Invalid API key is detected
    - Appropriate error is raised
    - Error message is informative
    """
    try:
        import litellm
    except ImportError:
        pytest.skip("litellm not installed")

    # Use invalid API key
    litellm.api_key = "invalid_key_12345"

    messages = [{"role": "user", "content": "Test"}]

    with pytest.raises(Exception) as exc_info:
        await litellm.acompletion(
            model="openrouter/deepseek/deepseek-chat",
            messages=messages,
            max_tokens=10,
            timeout=30.0,
        )

    # Validate error type and message
    error = exc_info.value
    error_str = str(error).lower()

    # Should contain authentication-related error
    assert any(
        keyword in error_str for keyword in ["auth", "key", "unauthorized", "401"]
    ), f"Unexpected error message: {error}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_model_id_handling(openrouter_api_key):
    """Test error handling for invalid model ID.

    This test validates:
    - Invalid model ID is detected
    - Appropriate error is raised
    - Error message is informative
    """
    try:
        import litellm
    except ImportError:
        pytest.skip("litellm not installed")

    litellm.api_key = openrouter_api_key

    messages = [{"role": "user", "content": "Test"}]

    # Use invalid model ID (missing openrouter/ prefix)
    with pytest.raises(Exception):
        await litellm.acompletion(
            model="deepseek/invalid-model-12345",
            messages=messages,
            max_tokens=10,
            timeout=30.0,
        )

    # Validate error occurred


# ============================================================================
# Configuration Tests
# ============================================================================


@pytest.mark.integration
def test_api_key_loaded_from_env():
    """Test that API key can be loaded from .env file.

    This test validates:
    - .env file is loaded correctly
    - OPENROUTER_API_KEY is present
    - API key has reasonable format
    """
    api_key = os.getenv("OPENROUTER_API_KEY")

    assert api_key is not None, "OPENROUTER_API_KEY not found in environment"
    assert len(api_key) > 10, f"API key too short: {len(api_key)} chars"
    assert isinstance(api_key, str), f"API key is not string: {type(api_key)}"


@pytest.mark.integration
def test_model_id_format():
    """Test that model ID has correct format.

    This test validates:
    - Model ID includes openrouter/ prefix
    - Model ID follows expected pattern
    """
    from src.agent_orchestration.openhands_integration.config import load_model_registry

    registry = load_model_registry()
    assert registry is not None, "Registry failed to load"

    # Check verified models have correct format
    verified_models = [
        model_id
        for model_id, entry in registry.models.items()
        if entry.compatibility_status.value == "verified"
    ]

    assert len(verified_models) > 0, "No verified models in registry"

    for model_id in verified_models:
        assert model_id.startswith("openrouter/"), (
            f"Model ID missing openrouter/ prefix: {model_id}"
        )
