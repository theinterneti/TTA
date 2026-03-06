"""Unit tests for src/ai_components/llm_factory.py."""

from __future__ import annotations

import os
import sys
from unittest.mock import patch

import pytest

# Skip all tests in this module on Python 3.14 due to langchain_openai segfault
pytestmark = pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="langchain_openai causes segfault on Python 3.14",
)

if sys.version_info < (3, 14):
    from langchain_openai import ChatOpenAI

    from src.ai_components.llm_factory import get_llm
else:
    # Dummy imports to avoid collection errors
    ChatOpenAI = None  # type: ignore[misc,assignment]

    def get_llm(*args, **kwargs):  # type: ignore[misc]
        """Dummy function for Python 3.14+"""


class TestGetLlm:
    def test_ollama_explicit(self):
        llm = get_llm(provider="ollama", model="mistral")
        assert isinstance(llm, ChatOpenAI)
        assert llm.model_name == "mistral"
        assert "11434" in str(llm.openai_api_base)

    def test_openrouter_explicit(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            llm = get_llm(
                provider="openrouter", model="mistralai/mistral-7b-instruct:free"
            )
        assert isinstance(llm, ChatOpenAI)
        assert llm.model_name == "mistralai/mistral-7b-instruct:free"
        assert "openrouter.ai" in str(llm.openai_api_base)

    def test_openrouter_requires_api_key(self):
        env = {k: v for k, v in os.environ.items() if k != "OPENROUTER_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
                get_llm(provider="openrouter")

    def test_auto_detect_openrouter_when_key_present(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            llm = get_llm()
        assert "openrouter.ai" in str(llm.openai_api_base)

    def test_auto_detect_ollama_when_no_key(self):
        env = {k: v for k, v in os.environ.items() if k != "OPENROUTER_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            # Also clear TTA_LLM_PROVIDER so auto-detect runs
            env.pop("TTA_LLM_PROVIDER", None)
            with patch.dict(os.environ, env, clear=True):
                llm = get_llm()
        assert "11434" in str(llm.openai_api_base)

    def test_env_var_provider_override(self):
        with patch.dict(os.environ, {"TTA_LLM_PROVIDER": "ollama"}):
            llm = get_llm()
        assert "11434" in str(llm.openai_api_base)

    def test_ollama_custom_base_url(self):
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://my-server:11434/v1"}):
            llm = get_llm(provider="ollama")
        assert "my-server" in str(llm.openai_api_base)

    def test_default_temperature_and_max_tokens(self):
        llm = get_llm(provider="ollama")
        assert llm.temperature == 0.7
        assert llm.max_tokens == 1000

    def test_custom_temperature_and_max_tokens(self):
        llm = get_llm(provider="ollama", temperature=0.3, max_tokens=500)
        assert llm.temperature == 0.3
        assert llm.max_tokens == 500
