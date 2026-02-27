"""
Factory for creating free or local LLM clients.

Supports two providers (both free):
- Ollama: fully local, no API key required
- OpenRouter: cloud gateway with a free-tier of open-source models

Provider selection order (first match wins):
1. Explicit ``provider`` argument or ``TTA_LLM_PROVIDER`` env var
2. ``OPENROUTER_API_KEY`` present → openrouter
3. Default → ollama (http://localhost:11434/v1)

Both providers are accessed via ``langchain-openai``'s ``ChatOpenAI``
because they both expose an OpenAI-compatible API endpoint.
"""

from __future__ import annotations

import logging
import os

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

# Provider base URLs
_OLLAMA_BASE_URL = "http://localhost:11434/v1"
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Default free models
_DEFAULT_OLLAMA_MODEL = "llama3.2"
_DEFAULT_OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct:free"


def get_llm(
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> ChatOpenAI:
    """Return a configured LLM client using only free or local providers.

    Args:
        provider: ``"ollama"`` or ``"openrouter"``. Auto-detected when omitted.
        model: Model name override. Falls back to env var or sensible default.
        temperature: Sampling temperature (0.0–1.0).
        max_tokens: Maximum tokens to generate per response.

    Returns:
        Configured ``ChatOpenAI``-compatible client.

    Raises:
        ValueError: If OpenRouter is selected but ``OPENROUTER_API_KEY`` is unset.
    """
    effective_provider = (
        provider
        or os.environ.get("TTA_LLM_PROVIDER", "").lower()
        or _auto_detect_provider()
    )

    if effective_provider == "openrouter":
        return _make_openrouter_llm(model, temperature, max_tokens)
    return _make_ollama_llm(model, temperature, max_tokens)


def _auto_detect_provider() -> str:
    if os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter"
    return "ollama"


def _make_ollama_llm(
    model: str | None, temperature: float, max_tokens: int
) -> ChatOpenAI:
    model_name = model or os.environ.get("OLLAMA_MODEL", _DEFAULT_OLLAMA_MODEL)
    raw_url = os.environ.get("OLLAMA_BASE_URL", _OLLAMA_BASE_URL)
    # Ensure the URL ends with /v1 (OpenAI-compatible path)
    base_url = raw_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    logger.info("LLM: Ollama %s @ %s", model_name, base_url)
    return ChatOpenAI(
        api_key="ollama",  # Ollama ignores the key; placeholder required by client
        base_url=base_url,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,  # type: ignore[call-arg]
    )


def _make_openrouter_llm(
    model: str | None, temperature: float, max_tokens: int
) -> ChatOpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is required"
            " for the openrouter provider"
        )
    # Check TTA_LLM_MODEL first, then OPENROUTER_MODEL (existing convention), then default
    model_name = (
        model
        or os.environ.get("TTA_LLM_MODEL")
        or os.environ.get("OPENROUTER_MODEL", _DEFAULT_OPENROUTER_MODEL)
    )
    logger.info("LLM: OpenRouter %s", model_name)
    return ChatOpenAI(
        api_key=api_key,
        base_url=_OPENROUTER_BASE_URL,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,  # type: ignore[call-arg]
    )
