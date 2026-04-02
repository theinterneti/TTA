"""Unit tests for mode_runner.py.

All httpx calls are mocked — no real network traffic.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml

from src.components.model_management.mode_runner import ModeRunner

# ---------------------------------------------------------------------------
# Minimal YAML fixture
# ---------------------------------------------------------------------------

MINIMAL_MODES = {
    "modes": {
        "narration": {
            "description": "Narrative prose",
            "tier1": {"model": "local-narration", "params": {"temperature": 0.8}},
            "tier2": {
                "model": "free/narration-model:free",
                "params": {"temperature": 0.8},
            },
            "tier3": {"model": "openrouter/free", "params": {"temperature": 0.8}},
        },
        "extraction": {
            "description": "Extract structured data",
            "tier1": {"model": None},  # no local model
            "tier2": {
                "model": "free/extraction-model:free",
                "params": {"temperature": 0.0},
            },
            "tier3": {"model": "openrouter/free", "params": {"temperature": 0.0}},
        },
        "no_tiers": {
            "description": "Mode with no valid tier models",
            "tier1": {"model": None},
            "tier2": {"model": None},
            "tier3": {"model": None},
        },
    }
}


@pytest.fixture
def modes_yaml(tmp_path: Path) -> Path:
    """Write a minimal modes YAML and return its path."""
    p = tmp_path / "model_modes.yaml"
    p.write_text(yaml.dump(MINIMAL_MODES))
    return p


@pytest.fixture
def runner(modes_yaml: Path) -> ModeRunner:
    return ModeRunner(modes_path=modes_yaml)


# ---------------------------------------------------------------------------
# Helper: build a mock httpx async context-manager response
# ---------------------------------------------------------------------------


def _mock_ollama_response(content: str) -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"message": {"content": content}}
    return resp


def _mock_openrouter_response(content: str) -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"choices": [{"message": {"content": content}}]}
    return resp


def _async_client_ctx(mock_resp: MagicMock) -> MagicMock:
    """Return a mock that works as `async with httpx.AsyncClient() as client`."""
    mock_post = AsyncMock(return_value=mock_resp)
    mock_client = MagicMock()
    mock_client.post = mock_post
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_client)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


# ---------------------------------------------------------------------------
# Basic construction
# ---------------------------------------------------------------------------


class TestModeRunnerInit:
    def test_loads_modes_from_yaml(self, runner: ModeRunner) -> None:
        assert "narration" in runner._modes
        assert "extraction" in runner._modes

    def test_raises_on_missing_yaml(self, tmp_path: Path) -> None:
        missing = tmp_path / "does_not_exist.yaml"
        with pytest.raises(FileNotFoundError):
            ModeRunner(modes_path=missing)


# ---------------------------------------------------------------------------
# Tier 1 — Ollama success path
# ---------------------------------------------------------------------------


class TestTier1OllamaSuccess:
    async def test_returns_ollama_response(self, runner: ModeRunner) -> None:
        mock_resp = _mock_ollama_response("You step into the tavern.")
        ctx = _async_client_ctx(mock_resp)

        with patch("httpx.AsyncClient", return_value=ctx):
            result = await runner.call("narration", prompt="enter tavern")

        assert result == "You step into the tavern."

    async def test_ollama_called_with_correct_model(self, runner: ModeRunner) -> None:
        mock_resp = _mock_ollama_response("response")
        ctx = _async_client_ctx(mock_resp)

        with patch("httpx.AsyncClient", return_value=ctx):
            await runner.call("narration", prompt="test")

        post_call = ctx.__aenter__.return_value.post
        call_kwargs = post_call.call_args
        body = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
        assert body["model"] == "local-narration"

    async def test_system_message_included_when_provided(
        self, runner: ModeRunner
    ) -> None:
        mock_resp = _mock_ollama_response("ok")
        ctx = _async_client_ctx(mock_resp)

        with patch("httpx.AsyncClient", return_value=ctx):
            await runner.call("narration", prompt="p", system="You are a narrator.")

        post_call = ctx.__aenter__.return_value.post
        body = post_call.call_args.kwargs["json"]
        messages = body["messages"]
        assert messages[0]["role"] == "system"
        assert "narrator" in messages[0]["content"]

    async def test_no_system_message_when_not_provided(
        self, runner: ModeRunner
    ) -> None:
        mock_resp = _mock_ollama_response("ok")
        ctx = _async_client_ctx(mock_resp)

        with patch("httpx.AsyncClient", return_value=ctx):
            await runner.call("narration", prompt="p")

        post_call = ctx.__aenter__.return_value.post
        body = post_call.call_args.kwargs["json"]
        roles = [m["role"] for m in body["messages"]]
        assert "system" not in roles


# ---------------------------------------------------------------------------
# Tier 2 fallback — Ollama unavailable
# ---------------------------------------------------------------------------


class TestTier2Fallback:
    async def test_falls_back_to_tier2_on_ollama_error(
        self, runner: ModeRunner
    ) -> None:
        or_resp = _mock_openrouter_response("Tier-2 narrative response.")

        call_count = 0

        def client_factory(**_kwargs):
            nonlocal call_count
            call_count += 1
            # First call (tier1 Ollama) raises
            if call_count == 1:
                ctx = MagicMock()
                ctx.__aenter__ = AsyncMock(side_effect=Exception("Ollama offline"))
                ctx.__aexit__ = AsyncMock(return_value=False)
                return ctx
            # Second call (tier2 OR) succeeds
            return _async_client_ctx(or_resp)

        with patch("httpx.AsyncClient", side_effect=client_factory):
            result = await runner.call("narration", prompt="test")

        assert result == "Tier-2 narrative response."

    async def test_extraction_skips_null_tier1_and_calls_tier2(
        self, runner: ModeRunner
    ) -> None:
        """Extraction tier1 model is null — should go directly to tier2."""
        or_resp = _mock_openrouter_response("[STATE]...[/STATE]")
        ctx = _async_client_ctx(or_resp)

        with patch("httpx.AsyncClient", return_value=ctx):
            result = await runner.call("extraction", prompt="narrative text")

        assert "[STATE]" in result

    async def test_tier2_called_with_correct_model(self, runner: ModeRunner) -> None:
        or_resp = _mock_openrouter_response("response")

        call_count = 0

        def client_factory(**_kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                ctx = MagicMock()
                ctx.__aenter__ = AsyncMock(side_effect=Exception("down"))
                ctx.__aexit__ = AsyncMock(return_value=False)
                return ctx
            return _async_client_ctx(or_resp)

        with patch("httpx.AsyncClient", side_effect=client_factory):
            await runner.call("narration", prompt="test")

        # Verify via the real call — check posted model name indirectly
        # by re-running with tier_override=2
        ctx2 = _async_client_ctx(or_resp)
        with patch("httpx.AsyncClient", return_value=ctx2):
            await runner.call("narration", prompt="test", tier_override=2)

        body = ctx2.__aenter__.return_value.post.call_args.kwargs["json"]
        assert body["model"] == "free/narration-model:free"


# ---------------------------------------------------------------------------
# Tier 3 fallback — tier2 also fails
# ---------------------------------------------------------------------------


class TestTier3Fallback:
    async def test_falls_back_to_tier3_when_tier2_fails(
        self, runner: ModeRunner
    ) -> None:
        tier3_resp = _mock_openrouter_response("Tier-3 response")

        call_count = 0

        def client_factory(**_kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # tier1 and tier2 both fail
                ctx = MagicMock()
                ctx.__aenter__ = AsyncMock(side_effect=Exception("unavailable"))
                ctx.__aexit__ = AsyncMock(return_value=False)
                return ctx
            return _async_client_ctx(tier3_resp)

        with patch("httpx.AsyncClient", side_effect=client_factory):
            result = await runner.call("narration", prompt="test")

        assert result == "Tier-3 response"

    async def test_raises_runtime_error_when_all_tiers_fail(
        self, runner: ModeRunner
    ) -> None:
        def failing_client(**_kwargs):
            ctx = MagicMock()
            ctx.__aenter__ = AsyncMock(side_effect=Exception("fail"))
            ctx.__aexit__ = AsyncMock(return_value=False)
            return ctx

        with patch("httpx.AsyncClient", side_effect=failing_client):
            with pytest.raises(RuntimeError, match="All tiers failed"):
                await runner.call("narration", prompt="test")

    async def test_all_null_models_raises_runtime_error(
        self, runner: ModeRunner
    ) -> None:
        with pytest.raises(RuntimeError, match="All tiers failed"):
            await runner.call("no_tiers", prompt="test")


# ---------------------------------------------------------------------------
# Unknown mode
# ---------------------------------------------------------------------------


class TestUnknownMode:
    async def test_raises_value_error_for_unknown_mode(
        self, runner: ModeRunner
    ) -> None:
        with pytest.raises(ValueError, match="Unknown mode"):
            await runner.call("does_not_exist", prompt="test")


# ---------------------------------------------------------------------------
# tier_override
# ---------------------------------------------------------------------------


class TestTierOverride:
    async def test_tier_override_1_calls_ollama(self, runner: ModeRunner) -> None:
        mock_resp = _mock_ollama_response("ollama result")
        ctx = _async_client_ctx(mock_resp)

        with patch("httpx.AsyncClient", return_value=ctx):
            result = await runner.call("narration", prompt="p", tier_override=1)

        assert result == "ollama result"

    async def test_tier_override_2_calls_openrouter(self, runner: ModeRunner) -> None:
        mock_resp = _mock_openrouter_response("or result")
        ctx = _async_client_ctx(mock_resp)

        with patch("httpx.AsyncClient", return_value=ctx):
            result = await runner.call("narration", prompt="p", tier_override=2)

        assert result == "or result"

    async def test_tier_override_skips_other_tiers(self, runner: ModeRunner) -> None:
        """tier_override=3 should not attempt tier1 or tier2."""
        mock_resp = _mock_openrouter_response("tier3 only")
        ctx = _async_client_ctx(mock_resp)

        with patch("httpx.AsyncClient", return_value=ctx) as mock_cls:
            result = await runner.call("narration", prompt="p", tier_override=3)

        # httpx.AsyncClient constructed exactly once (tier3 only)
        assert mock_cls.call_count == 1
        assert result == "tier3 only"
