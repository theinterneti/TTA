"""Snapshot and track available OpenRouter free models.

Stores a local JSON cache so the game always has a known-good free model list,
even between OR free-tier churn events.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

CACHE_PATH = Path("~/.cache/tta/or_free_models.json").expanduser()
CACHE_TTL_SECONDS = 7 * 24 * 3600  # 1 week
OR_MODELS_URL = "https://openrouter.ai/api/v1/models"


@dataclass
class ORModel:
    id: str
    name: str
    context_length: int
    prompt_price: float  # per 1M tokens
    completion_price: float
    tags: list[str] = field(default_factory=list)

    @property
    def is_free(self) -> bool:
        return self.prompt_price == 0 and self.completion_price == 0


def fetch_free_models(api_key: str | None = None) -> list[ORModel]:
    """Fetch current free models from OpenRouter API."""
    headers: dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    resp = httpx.get(OR_MODELS_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    models = []
    for m in data.get("data", []):
        pricing = m.get("pricing", {})
        try:
            prompt_price = float(pricing.get("prompt", "1") or "1")
            completion_price = float(pricing.get("completion", "1") or "1")
        except (ValueError, TypeError):
            prompt_price = 1.0
            completion_price = 1.0

        models.append(
            ORModel(
                id=m["id"],
                name=m.get("name", m["id"]),
                context_length=m.get("context_length", 4096),
                prompt_price=prompt_price,
                completion_price=completion_price,
            )
        )

    return [m for m in models if m.is_free]


def load_cached_models() -> tuple[list[ORModel], float]:
    """Load cached model list. Returns (models, cache_age_seconds)."""
    if not CACHE_PATH.exists():
        return [], float("inf")

    data: dict[str, Any] = json.loads(CACHE_PATH.read_text())
    age = time.time() - data.get("fetched_at", 0)
    models = [ORModel(**m) for m in data.get("models", [])]
    return models, age


def save_cache(models: list[ORModel]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(
            {
                "fetched_at": time.time(),
                "models": [m.__dict__ for m in models],
            },
            indent=2,
        )
    )


def get_free_models(
    api_key: str | None = None, force_refresh: bool = False
) -> list[ORModel]:
    """Return free OR models, using cache if fresh (< 1 week)."""
    cached, age = load_cached_models()
    if cached and age < CACHE_TTL_SECONDS and not force_refresh:
        return cached

    try:
        models = fetch_free_models(api_key)
        save_cache(models)
        return models
    except Exception:
        logger.warning(
            "Failed to fetch OR models; returning stale cache (%d models)", len(cached)
        )
        return cached


def recommend_for_role(role: str, models: list[ORModel]) -> list[ORModel]:
    """Rank free models for a given role ('narration' or 'extraction')."""
    # Prefer large context + known quality models
    PREFERRED_NARRATION = [
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "qwen/qwen3-235b-a22b:free",
        "mistralai/mistral-7b-instruct:free",
    ]
    PREFERRED_EXTRACTION = [
        "qwen/qwen3-235b-a22b:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
    ]

    preferred = PREFERRED_NARRATION if role == "narration" else PREFERRED_EXTRACTION
    model_ids = {m.id for m in models}

    ordered: list[ORModel] = []
    # First: preferred models that are actually available
    for pid in preferred:
        if pid in model_ids:
            ordered.extend(m for m in models if m.id == pid)
    # Then: everything else sorted by context length (larger = better for narrative)
    rest = [m for m in models if m.id not in {o.id for o in ordered}]
    rest.sort(key=lambda m: m.context_length, reverse=True)
    return ordered + rest


class FreeModelTracker:
    """Convenience wrapper around the module-level free-model functions.

    Holds an optional API key and caches the fetched model list for the
    lifetime of the instance so callers don't need to manage cache state
    themselves.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key
        self._models: list[ORModel] | None = None

    def refresh(self, force: bool = False) -> list[ORModel]:
        """Fetch (or return cached) free model list."""
        self._models = get_free_models(api_key=self._api_key, force_refresh=force)
        return self._models

    def recommend_for_role(self, role: str) -> str | None:
        """Return the best free model ID for *role*, or None if no models known.

        Calls :func:`recommend_for_role` with the current model list,
        triggering a cache load/refresh if needed.
        """
        models = self._models if self._models is not None else self.refresh()
        ranked = recommend_for_role(role, models)
        return ranked[0].id if ranked else None


if __name__ == "__main__":
    import os
    from datetime import datetime

    logging.basicConfig(level=logging.WARNING)
    api_key = os.getenv("OPENROUTER_API_KEY")
    print("Fetching free models from OpenRouter...")  # noqa: T201
    models = get_free_models(api_key=api_key, force_refresh=True)
    print(f"Found {len(models)} free models (fetched at {datetime.now():%H:%M})\n")  # noqa: T201

    print("=== Top picks for NARRATION ===")  # noqa: T201
    for m in recommend_for_role("narration", models)[:5]:
        print(f"  {m.id}  (ctx={m.context_length:,})")  # noqa: T201

    print("\n=== Top picks for EXTRACTION ===")  # noqa: T201
    for m in recommend_for_role("extraction", models)[:5]:
        print(f"  {m.id}  (ctx={m.context_length:,})")  # noqa: T201
