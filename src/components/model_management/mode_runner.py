"""Route model calls to the right tier based on model_modes.yaml.

Usage:
    runner = ModeRunner()
    response = await runner.call("narration", prompt="You enter the tavern...")
    response = await runner.call("extraction", prompt="[narrative text]")
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import httpx
import yaml

logger = logging.getLogger(__name__)

MODES_PATH = Path(__file__).parent / "model_modes.yaml"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OR_URL = "https://openrouter.ai/api/v1/chat/completions"


class ModeRunner:
    def __init__(self, modes_path: Path = MODES_PATH) -> None:
        self._modes: dict[str, Any] = yaml.safe_load(modes_path.read_text())["modes"]

    async def call(
        self,
        mode: str,
        prompt: str,
        system: str | None = None,
        tier_override: int | None = None,
    ) -> str:
        """Call the best available model for the given mode.

        Args:
            mode: One of the mode keys in model_modes.yaml
            prompt: User/input content
            system: Optional system message override
            tier_override: Force a specific tier (1, 2, or 3)

        Returns:
            Model response text
        """
        config = self._modes.get(mode)
        if config is None:
            raise ValueError(f"Unknown mode: {mode!r}. Available: {list(self._modes)}")

        tiers = [1, 2, 3] if tier_override is None else [tier_override]

        for tier in tiers:
            tier_config = config.get(f"tier{tier}", {})
            model = tier_config.get("model")
            if model is None:
                continue

            params = tier_config.get("params", {})

            try:
                if tier == 1:
                    return await self._call_ollama(model, prompt, system, params)
                return await self._call_openrouter(model, prompt, system, params)
            except Exception as e:
                logger.warning("tier%d (%s) failed: %r — trying next", tier, model, e)

        raise RuntimeError(f"All tiers failed for mode {mode!r}")

    async def _call_ollama(
        self,
        model: str,
        prompt: str,
        system: str | None,
        params: dict[str, Any],
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": model, "messages": messages, "stream": False, **params},
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]

    async def _call_openrouter(
        self,
        model: str,
        prompt: str,
        system: str | None,
        params: dict[str, Any],
    ) -> str:
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/theinterneti/TTA",
        }

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                OR_URL,
                headers=headers,
                json={"model": model, "messages": messages, **params},
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
