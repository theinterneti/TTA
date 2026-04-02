"""
Logseq: [[TTA.dev/Ai_components/Llm_factory]]
Factory for creating free or local LLM clients.

Supports three providers (all free):
- Ollama: fully local, no API key required
- OpenRouter: cloud gateway with a free-tier of open-source models
- Groq: fast cloud inference with a generous free tier (GROQ_API_KEY required)

Provider selection order (first match wins):
1. Explicit ``provider`` argument or ``TTA_LLM_PROVIDER`` env var
2. ``OPENROUTER_API_KEY`` present → openrouter
3. Default → ollama (http://localhost:11434/v1)

All providers are accessed via ``langchain-openai``'s ``ChatOpenAI``
because they all expose an OpenAI-compatible API endpoint.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Provider base URLs
_OLLAMA_BASE_URL = "http://localhost:11434/v1"
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
_GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Default free models
_DEFAULT_OLLAMA_MODEL = "llama3.2"
# Pinned to best free narration model (405B, no moderation, top prose quality).
# Override via OR_NARRATOR_MODEL env var or --model CLI flag.
# Fallback chain: hermes-3-405b → llama-3.3-70b → local:gemma3:4b
_DEFAULT_OPENROUTER_MODEL = "nousresearch/hermes-3-llama-3.1-405b:free"
# Best free Groq model for narration (70B, fast inference, generous quota).
_DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"

# Keep the client import lazy for runtime compatibility, but expose a patchable
# module attribute so unit tests can replace it without importing the provider.
ChatOpenAI: Any | None = None


def get_llm(
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
):
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
        ValueError: If Groq is selected but ``GROQ_API_KEY`` is unset.
    """

    effective_provider = (
        provider
        or os.environ.get("TTA_LLM_PROVIDER", "").lower()
        or _auto_detect_provider()
    )

    if effective_provider == "openrouter":
        return _make_openrouter_llm(model, temperature, max_tokens)
    if effective_provider == "groq":
        return _make_groq_llm(model, temperature, max_tokens)
    return _make_ollama_llm(model, temperature, max_tokens)


def _auto_detect_provider() -> str:
    if os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter"
    return "ollama"


def _get_chat_openai():
    global ChatOpenAI
    if ChatOpenAI is None:
        from langchain_openai import ChatOpenAI as langchain_chat_openai

        ChatOpenAI = langchain_chat_openai
    return ChatOpenAI


def _make_ollama_llm(model: str | None, temperature: float, max_tokens: int):
    model_name = model or os.environ.get("OLLAMA_MODEL", _DEFAULT_OLLAMA_MODEL)
    raw_url = os.environ.get("OLLAMA_BASE_URL", _OLLAMA_BASE_URL)
    # Ensure the URL ends with /v1 (OpenAI-compatible path)
    base_url = raw_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    logger.info("LLM: Ollama %s @ %s", model_name, base_url)
    return _get_chat_openai()(
        api_key="ollama",  # Ollama ignores the key; placeholder required by client
        base_url=base_url,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,  # type: ignore[call-arg]
    )


def _make_openrouter_llm(model: str | None, temperature: float, max_tokens: int):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is required"
            " for the openrouter provider"
        )
    # Priority: explicit arg → OR_NARRATOR_MODEL → TTA_LLM_MODEL → OPENROUTER_MODEL → default
    model_name = (
        model
        or os.environ.get("OR_NARRATOR_MODEL")
        or os.environ.get("TTA_LLM_MODEL")
        or os.environ.get("OPENROUTER_MODEL", _DEFAULT_OPENROUTER_MODEL)
    )
    logger.info("LLM: OpenRouter %s", model_name)
    return _get_chat_openai()(
        api_key=api_key,
        base_url=_OPENROUTER_BASE_URL,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,  # type: ignore[call-arg]
    )


def _make_groq_llm(model: str | None, temperature: float, max_tokens: int):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is required for the groq provider")
    model_name = model or os.environ.get("GROQ_MODEL", _DEFAULT_GROQ_MODEL)
    logger.info("LLM: Groq %s", model_name)
    return _get_chat_openai()(
        api_key=api_key,
        base_url=_GROQ_BASE_URL,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,  # type: ignore[call-arg]
    )
