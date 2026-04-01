"""
Unit tests for src/ai_components/llm_factory.py.

Tests cover:
- Provider auto-detection (env var, API key presence, default)
- Explicit provider selection via argument and TTA_LLM_PROVIDER
- Ollama URL normalisation (ensure /v1 suffix)
- Model name resolution priority (arg > env > default)
- OpenRouter raises ValueError when no API key
- ChatOpenAI is constructed with the right kwargs (no real network calls)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FACTORY = "src.ai_components.llm_factory"
_CHATOPENAI = f"{_FACTORY}.ChatOpenAI"


def _make_chat_mock():
    return MagicMock()


# ---------------------------------------------------------------------------
# _auto_detect_provider
# ---------------------------------------------------------------------------


class TestAutoDetectProvider:
    def test_returns_openrouter_when_key_present(self, monkeypatch):
        """Auto Detect Provider: returns openrouter when key present."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
        monkeypatch.delenv("TTA_LLM_PROVIDER", raising=False)
        from src.ai_components.llm_factory import _auto_detect_provider

        assert _auto_detect_provider() == "openrouter"

    def test_returns_ollama_when_no_key(self, monkeypatch):
        """Auto Detect Provider: returns ollama when no key."""
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        from src.ai_components.llm_factory import _auto_detect_provider

        assert _auto_detect_provider() == "ollama"


# ---------------------------------------------------------------------------
# get_llm — provider routing
# ---------------------------------------------------------------------------


class TestGetLlmProviderRouting:
    def test_explicit_ollama_argument(self, monkeypatch):
        """Get Llm Provider Routing: explicit ollama argument."""
        monkeypatch.delenv("TTA_LLM_PROVIDER", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch(_CHATOPENAI, return_value=_make_chat_mock()) as mock_cls:
            from src.ai_components.llm_factory import get_llm

            get_llm(provider="ollama")

        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["api_key"] == "ollama"
        assert "/v1" in call_kwargs["base_url"]

    def test_explicit_openrouter_argument(self, monkeypatch):
        """Get Llm Provider Routing: explicit openrouter argument."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
        with patch(_CHATOPENAI, return_value=_make_chat_mock()) as mock_cls:
            from src.ai_components.llm_factory import get_llm

            get_llm(provider="openrouter")

        call_kwargs = mock_cls.call_args.kwargs
        assert call_kwargs["api_key"] == "sk-test"
        assert "openrouter" in call_kwargs["base_url"]

    def test_env_var_selects_ollama(self, monkeypatch):
        """Get Llm Provider Routing: env var selects ollama."""
        monkeypatch.setenv("TTA_LLM_PROVIDER", "ollama")
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch(_CHATOPENAI, return_value=_make_chat_mock()) as mock_cls:
            from src.ai_components.llm_factory import get_llm

            get_llm()

        assert mock_cls.call_args.kwargs["api_key"] == "ollama"

    def test_env_var_selects_openrouter(self, monkeypatch):
        """Get Llm Provider Routing: env var selects openrouter."""
        monkeypatch.setenv("TTA_LLM_PROVIDER", "openrouter")
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
        with patch(_CHATOPENAI, return_value=_make_chat_mock()) as mock_cls:
            from src.ai_components.llm_factory import get_llm

            get_llm()

        assert mock_cls.call_args.kwargs["api_key"] == "sk-test"

    def test_auto_detect_falls_back_to_ollama(self, monkeypatch):
        """Get Llm Provider Routing: auto detect falls back to ollama."""
        monkeypatch.delenv("TTA_LLM_PROVIDER", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch(_CHATOPENAI, return_value=_make_chat_mock()) as mock_cls:
            from src.ai_components.llm_factory import get_llm

            get_llm()

        assert mock_cls.call_args.kwargs["api_key"] == "ollama"

    def test_auto_detect_uses_openrouter_when_key_set(self, monkeypatch):
        """Get Llm Provider Routing: auto detect uses openrouter when key set."""
        monkeypatch.delenv("TTA_LLM_PROVIDER", raising=False)
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-auto")
        with patch(_CHATOPENAI, return_value=_make_chat_mock()) as mock_cls:
            from src.ai_components.llm_factory import get_llm

            get_llm()

        assert mock_cls.call_args.kwargs["api_key"] == "sk-auto"


# ---------------------------------------------------------------------------
# Ollama URL normalisation
# ---------------------------------------------------------------------------


class TestOllamaUrlNormalisation:
    def _ollama_base_url(self, monkeypatch, raw_url: str) -> str:
        monkeypatch.setenv("OLLAMA_BASE_URL", raw_url)
        monkeypatch.delenv("TTA_LLM_PROVIDER", raising=False)
        with patch(_CHATOPENAI, return_value=_make_chat_mock()) as mock_cls:
            from src.ai_components.llm_factory import get_llm

            get_llm(provider="ollama")
        return mock_cls.call_args.kwargs["base_url"]

    def test_appends_v1_when_missing(self, monkeypatch):
        """Ollama Url Normalisation: appends v1 when missing."""
        url = self._ollama_base_url(monkeypatch, "http://localhost:11434")
        assert url == "http://localhost:11434/v1"

    def test_keeps_existing_v1(self, monkeypatch):
        """Ollama Url Normalisation: keeps existing v1."""
        url = self._ollama_base_url(monkeypatch, "http://localhost:11434/v1")
        assert url == "http://localhost:11434/v1"

    def test_strips_trailing_slash_before_v1_check(self, monkeypatch):
        """Ollama Url Normalisation: strips trailing slash before v1 check."""
        url = self._ollama_base_url(monkeypatch, "http://localhost:11434/v1/")
        assert url == "http://localhost:11434/v1"

    def test_default_url_used_when_env_absent(self, monkeypatch):
        """Ollama Url Normalisation: default url used when env absent."""
        monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
        with patch(_CHATOPENAI, return_value=_make_chat_mock()) as mock_cls:
            from src.ai_components.llm_factory import get_llm

            get_llm(provider="ollama")
        assert mock_cls.call_args.kwargs["base_url"] == "http://localhost:11434/v1"


# ---------------------------------------------------------------------------
# Ollama model name resolution
# ---------------------------------------------------------------------------


class TestOllamaModelResolution:
    def _ollama_model(self, monkeypatch, *, arg=None, env=None) -> str:
        if env:
            monkeypatch.setenv("OLLAMA_MODEL", env)
        else:
            monkeypatch.delenv("OLLAMA_MODEL", raising=False)
        with patch(_CHATOPENAI, return_value=_make_chat_mock()) as mock_cls:
            from src.ai_components.llm_factory import get_llm

            get_llm(provider="ollama", model=arg)
        return mock_cls.call_args.kwargs["model"]

    def test_explicit_arg_wins(self, monkeypatch):
        """Ollama Model Resolution: explicit arg wins."""
        assert (
            self._ollama_model(monkeypatch, arg="gemma3:4b", env="other") == "gemma3:4b"
        )

    def test_env_var_used_when_no_arg(self, monkeypatch):
        """Ollama Model Resolution: env var used when no arg."""
        assert self._ollama_model(monkeypatch, env="qwen3:1.7b") == "qwen3:1.7b"

    def test_default_used_when_no_arg_no_env(self, monkeypatch):
        """Ollama Model Resolution: default used when no arg no env."""
        from src.ai_components.llm_factory import _DEFAULT_OLLAMA_MODEL

        assert self._ollama_model(monkeypatch) == _DEFAULT_OLLAMA_MODEL


# ---------------------------------------------------------------------------
# OpenRouter raises ValueError without API key
# ---------------------------------------------------------------------------


class TestOpenRouterMissingKey:
    def test_raises_value_error_when_key_absent(self, monkeypatch):
        """Open Router Missing Key: raises value error when key absent."""
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        from src.ai_components.llm_factory import get_llm

        with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
            get_llm(provider="openrouter")


# ---------------------------------------------------------------------------
# OpenRouter model name resolution
# ---------------------------------------------------------------------------


class TestOpenRouterModelResolution:
    def _openrouter_model(
        self,
        monkeypatch,
        *,
        arg=None,
        tta_model=None,
        or_model=None,
    ) -> str:
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
        for var, val in [("TTA_LLM_MODEL", tta_model), ("OPENROUTER_MODEL", or_model)]:
            if val:
                monkeypatch.setenv(var, val)
            else:
                monkeypatch.delenv(var, raising=False)
        with patch(_CHATOPENAI, return_value=_make_chat_mock()) as mock_cls:
            from src.ai_components.llm_factory import get_llm

            get_llm(provider="openrouter", model=arg)
        return mock_cls.call_args.kwargs["model"]

    def test_explicit_arg_wins(self, monkeypatch):
        """Open Router Model Resolution: explicit arg wins."""
        assert (
            self._openrouter_model(
                monkeypatch, arg="my/model", tta_model="other", or_model="other2"
            )
            == "my/model"
        )

    def test_tta_llm_model_beats_openrouter_model(self, monkeypatch):
        """Open Router Model Resolution: tta llm model beats openrouter model."""
        assert (
            self._openrouter_model(
                monkeypatch, tta_model="tta/model", or_model="or/model"
            )
            == "tta/model"
        )

    def test_openrouter_model_env_used_when_no_tta(self, monkeypatch):
        """Open Router Model Resolution: openrouter model env used when no tta."""
        assert self._openrouter_model(monkeypatch, or_model="or/model") == "or/model"

    def test_default_used_when_no_env(self, monkeypatch):
        """Open Router Model Resolution: default used when no env."""
        from src.ai_components.llm_factory import _DEFAULT_OPENROUTER_MODEL

        assert self._openrouter_model(monkeypatch) == _DEFAULT_OPENROUTER_MODEL


# ---------------------------------------------------------------------------
# temperature / max_tokens forwarded
# ---------------------------------------------------------------------------


class TestGetLlmParameters:
    def test_temperature_and_max_tokens_passed_through(self, monkeypatch):
        """Get Llm Parameters: temperature and max tokens passed through."""
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch(_CHATOPENAI, return_value=_make_chat_mock()) as mock_cls:
            from src.ai_components.llm_factory import get_llm

            get_llm(provider="ollama", temperature=0.3, max_tokens=500)

        kw = mock_cls.call_args.kwargs
        assert kw["temperature"] == 0.3
        assert kw["max_tokens"] == 500
