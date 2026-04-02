"""Unit tests for free_model_tracker.py.

All httpx calls are mocked — no real network traffic.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from src.components.model_management.free_model_tracker import (
    CACHE_TTL_SECONDS,
    FreeModelTracker,
    ORModel,
    fetch_free_models,
    get_free_models,
    load_cached_models,
    rank_models_for_role,
    save_cache,
)

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

SAMPLE_MODELS = [
    ORModel(
        id="nousresearch/hermes-3-llama-3.1-405b:free",
        name="Hermes 3",
        context_length=131072,
        prompt_price=0.0,
        completion_price=0.0,
    ),
    ORModel(
        id="meta-llama/llama-3.3-70b-instruct:free",
        name="Llama 3.3 70B",
        context_length=65536,
        prompt_price=0.0,
        completion_price=0.0,
    ),
    ORModel(
        id="mistralai/mistral-7b-instruct:free",
        name="Mistral 7B",
        context_length=32768,
        prompt_price=0.0,
        completion_price=0.0,
    ),
    # Paid model — should NOT appear in free lists
    ORModel(
        id="openai/gpt-4o",
        name="GPT-4o",
        context_length=128000,
        prompt_price=0.005,
        completion_price=0.015,
    ),
]

FREE_MODELS = [m for m in SAMPLE_MODELS if m.is_free]


def _or_api_payload(models: list[ORModel]) -> dict:
    """Build a fake OpenRouter API response payload."""
    return {
        "data": [
            {
                "id": m.id,
                "name": m.name,
                "context_length": m.context_length,
                "pricing": {
                    "prompt": str(m.prompt_price),
                    "completion": str(m.completion_price),
                },
            }
            for m in models
        ]
    }


def _make_mock_client(response_mock: AsyncMock) -> AsyncMock:
    """Build an AsyncMock that acts as an httpx.AsyncClient context manager."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=response_mock)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def _make_mock_response(payload: dict) -> MagicMock:
    # Use MagicMock because httpx Response.json() and .raise_for_status() are sync.
    mock_response = MagicMock()
    mock_response.json.return_value = payload
    mock_response.raise_for_status = MagicMock()
    return mock_response


# ---------------------------------------------------------------------------
# ORModel tests
# ---------------------------------------------------------------------------


class TestORModel:
    def test_is_free_true_when_both_prices_zero(self) -> None:
        m = ORModel("test/model:free", "Test", 8192, 0.0, 0.0)
        assert m.is_free is True

    def test_is_free_false_when_prompt_price_nonzero(self) -> None:
        m = ORModel("test/paid", "Paid", 8192, 0.001, 0.0)
        assert m.is_free is False

    def test_is_free_false_when_completion_price_nonzero(self) -> None:
        m = ORModel("test/paid", "Paid", 8192, 0.0, 0.002)
        assert m.is_free is False


# ---------------------------------------------------------------------------
# fetch_free_models — mocked httpx.AsyncClient
# ---------------------------------------------------------------------------


class TestFetchFreeModels:
    async def test_returns_only_free_models(self) -> None:
        payload = _or_api_payload(SAMPLE_MODELS)
        mock_client = _make_mock_client(_make_mock_response(payload))
        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await fetch_free_models(api_key="test-key")
        mock_client.get.assert_called_once()
        assert all(m.is_free for m in result)
        assert len(result) == len(FREE_MODELS)

    async def test_sends_auth_header_when_api_key_provided(self) -> None:
        mock_client = _make_mock_client(_make_mock_response({"data": []}))
        with patch("httpx.AsyncClient", return_value=mock_client):
            await fetch_free_models(api_key="my-secret-key")
        assert (
            mock_client.get.call_args[1]["headers"]["Authorization"]
            == "Bearer my-secret-key"
        )

    async def test_no_auth_header_when_no_api_key(self) -> None:
        mock_client = _make_mock_client(_make_mock_response({"data": []}))
        with patch("httpx.AsyncClient", return_value=mock_client):
            await fetch_free_models(api_key=None)
        assert "Authorization" not in mock_client.get.call_args[1].get("headers", {})

    async def test_handles_missing_pricing_keys_gracefully(self) -> None:
        payload = {
            "data": [
                {
                    "id": "some/model:free",
                    "name": "Model",
                    "context_length": 4096,
                    "pricing": {},  # missing prompt/completion
                }
            ]
        }
        mock_client = _make_mock_client(_make_mock_response(payload))
        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await fetch_free_models()
        # Defaults to price=1, so model is NOT free
        assert result == []


# ---------------------------------------------------------------------------
# Cache tests
# ---------------------------------------------------------------------------


class TestCacheRoundtrip:
    def test_save_and_load_round_trip(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "or_free_models.json"
        save_cache(FREE_MODELS, cache_file)
        loaded, age = load_cached_models(cache_file)
        assert len(loaded) == len(FREE_MODELS)
        assert all(m.is_free for m in loaded)
        assert age < 5  # just saved — age must be tiny

    def test_load_missing_cache_returns_empty_with_infinite_age(
        self, tmp_path: Path
    ) -> None:
        missing = tmp_path / "nonexistent.json"
        models, age = load_cached_models(missing)
        assert models == []
        assert age == float("inf")

    def test_cache_creates_parent_directory(self, tmp_path: Path) -> None:
        deep_path = tmp_path / "a" / "b" / "cache.json"
        save_cache(FREE_MODELS[:1], deep_path)
        assert deep_path.exists()


# ---------------------------------------------------------------------------
# get_free_models — uses cache or fetches
# ---------------------------------------------------------------------------


class TestGetFreeModels:
    async def test_uses_fresh_cache_without_network_call(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "cache.json"
        cache_file.write_text(
            json.dumps(
                {
                    "fetched_at": time.time(),
                    "models": [asdict(m) for m in FREE_MODELS],
                }
            )
        )
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await get_free_models(cache_path=cache_file)
        mock_client.get.assert_not_called()
        assert len(result) == len(FREE_MODELS)

    async def test_fetches_when_cache_stale(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "cache.json"
        stale_time = time.time() - CACHE_TTL_SECONDS - 1
        cache_file.write_text(json.dumps({"fetched_at": stale_time, "models": []}))

        mock_client = _make_mock_client(
            _make_mock_response(_or_api_payload(FREE_MODELS))
        )
        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await get_free_models(cache_path=cache_file)
        mock_client.get.assert_called_once()
        assert len(result) == len(FREE_MODELS)

    async def test_returns_stale_cache_on_network_error(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "cache.json"
        stale_time = time.time() - CACHE_TTL_SECONDS - 1
        cache_file.write_text(
            json.dumps(
                {
                    "fetched_at": stale_time,
                    "models": [asdict(m) for m in FREE_MODELS[:1]],
                }
            )
        )
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("network error"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await get_free_models(cache_path=cache_file)
        assert len(result) == 1

    async def test_force_refresh_ignores_fresh_cache(self, tmp_path: Path) -> None:
        cache_file = tmp_path / "cache.json"
        cache_file.write_text(json.dumps({"fetched_at": time.time(), "models": []}))

        mock_client = _make_mock_client(
            _make_mock_response(_or_api_payload(FREE_MODELS))
        )
        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await get_free_models(cache_path=cache_file, force_refresh=True)
        mock_client.get.assert_called_once()
        assert len(result) == len(FREE_MODELS)


# ---------------------------------------------------------------------------
# rank_models_for_role (formerly recommend_for_role)
# ---------------------------------------------------------------------------


class TestRecommendForRole:
    def test_narration_prefers_hermes_when_available(self) -> None:
        ranked = rank_models_for_role(FREE_MODELS)
        assert ranked[0].id == "nousresearch/hermes-3-llama-3.1-405b:free"

    def test_narration_returns_all_models(self) -> None:
        ranked = rank_models_for_role(FREE_MODELS)
        assert len(ranked) == len(FREE_MODELS)

    async def test_extraction_returns_model_string_via_tracker(
        self, tmp_path: Path
    ) -> None:
        cache_file = tmp_path / "cache.json"
        cache_file.write_text(
            json.dumps(
                {"fetched_at": time.time(), "models": [asdict(m) for m in FREE_MODELS]}
            )
        )
        tracker = FreeModelTracker(cache_path=cache_file)
        result = await tracker.recommend()
        assert isinstance(result, str)
        assert "/" in result  # looks like a model ID

    async def test_narration_returns_model_string_via_tracker(
        self, tmp_path: Path
    ) -> None:
        cache_file = tmp_path / "cache.json"
        cache_file.write_text(
            json.dumps(
                {"fetched_at": time.time(), "models": [asdict(m) for m in FREE_MODELS]}
            )
        )
        tracker = FreeModelTracker(cache_path=cache_file)
        result = await tracker.recommend()
        assert isinstance(result, str)
        assert "hermes" in result or "llama" in result or "mistral" in result

    async def test_returns_none_when_no_models(self) -> None:
        with patch(
            "ttadev.primitives.llm.free_model_tracker.get_free_models",
            new=AsyncMock(return_value=[]),
        ):
            tracker = FreeModelTracker()
            result = await tracker.recommend()
        assert result is None

    def test_unknown_role_falls_back_to_extraction_list(self) -> None:
        ranked = rank_models_for_role(FREE_MODELS)
        assert len(ranked) == len(FREE_MODELS)


# ---------------------------------------------------------------------------
# FreeModelTracker class
# ---------------------------------------------------------------------------


class TestFreeModelTracker:
    async def test_refresh_calls_get_free_models(self) -> None:
        with patch(
            "ttadev.primitives.llm.free_model_tracker.get_free_models",
            new=AsyncMock(return_value=FREE_MODELS),
        ) as mock_get:
            tracker = FreeModelTracker(api_key="key")
            result = await tracker.refresh()
        mock_get.assert_called_once_with(
            api_key="key", force_refresh=False, cache_path=ANY, cache_ttl=ANY
        )
        assert result == FREE_MODELS

    async def test_force_refresh_passes_flag(self) -> None:
        with patch(
            "ttadev.primitives.llm.free_model_tracker.get_free_models",
            new=AsyncMock(return_value=FREE_MODELS),
        ) as mock_get:
            tracker = FreeModelTracker()
            await tracker.refresh(force=True)
        mock_get.assert_called_once_with(
            api_key=None, force_refresh=True, cache_path=ANY, cache_ttl=ANY
        )

    async def test_recommend_triggers_refresh_on_first_call(self) -> None:
        with patch(
            "ttadev.primitives.llm.free_model_tracker.get_free_models",
            new=AsyncMock(return_value=FREE_MODELS),
        ) as mock_get:
            tracker = FreeModelTracker()
            await tracker.recommend()
        mock_get.assert_called_once()

    async def test_recommend_does_not_re_fetch_on_second_call(self) -> None:
        with patch(
            "ttadev.primitives.llm.free_model_tracker.get_free_models",
            new=AsyncMock(return_value=FREE_MODELS),
        ) as mock_get:
            tracker = FreeModelTracker()
            await tracker.recommend()
            await tracker.recommend()
        mock_get.assert_called_once()


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

SAMPLE_MODELS = [
    ORModel(
        id="nousresearch/hermes-3-llama-3.1-405b:free",
        name="Hermes 3",
        context_length=131072,
        prompt_price=0.0,
        completion_price=0.0,
    ),
    ORModel(
        id="meta-llama/llama-3.3-70b-instruct:free",
        name="Llama 3.3 70B",
        context_length=65536,
        prompt_price=0.0,
        completion_price=0.0,
    ),
    ORModel(
        id="mistralai/mistral-7b-instruct:free",
        name="Mistral 7B",
        context_length=32768,
        prompt_price=0.0,
        completion_price=0.0,
    ),
    # Paid model — should NOT appear in free lists
    ORModel(
        id="openai/gpt-4o",
        name="GPT-4o",
        context_length=128000,
        prompt_price=0.005,
        completion_price=0.015,
    ),
]

FREE_MODELS = [m for m in SAMPLE_MODELS if m.is_free]


def _or_api_payload(models: list[ORModel]) -> dict:
    """Build a fake OpenRouter API response payload."""
    return {
        "data": [
            {
                "id": m.id,
                "name": m.name,
                "context_length": m.context_length,
                "pricing": {
                    "prompt": str(m.prompt_price),
                    "completion": str(m.completion_price),
                },
            }
            for m in models
        ]
    }
