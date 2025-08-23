from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from .agents import Agent
from .interfaces import MessageCoordinator
from .models import AgentId, AgentType
from .messaging import FailureType

logger = logging.getLogger(__name__)


class InputProcessorAgentProxy(Agent):
    """Wraps Input Processor Agent functionality with validation and retry logic."""

    def __init__(self, *, coordinator: Optional[MessageCoordinator] = None, instance: Optional[str] = None, default_timeout_s: float = 8.0) -> None:
        super().__init__(agent_id=AgentId(type=AgentType.IPA, instance=instance), name=f"ipa:{instance or 'default'}", coordinator=coordinator, default_timeout_s=default_timeout_s)

    async def process(self, input_payload: dict) -> dict:
        # Validate user input
        text = (input_payload or {}).get("text", "").strip()
        if not text:
            raise ValueError("InputProcessorAgentProxy requires non-empty 'text'")
        # Basic routing hint extraction (placeholder for real implementation)
        routing = {"intent": "unknown"}
        # For now, the proxy returns a normalized structure
        return {"normalized_text": text, "routing": routing}

    async def handle_with_retry(self, payload: dict, *, retries: int = 2, backoff_s: float = 0.5) -> dict:
        attempt = 0
        while True:
            try:
                return await self.process_with_timeout(payload)
            except asyncio.TimeoutError:
                attempt += 1
                if attempt > retries:
                    raise
                await asyncio.sleep(backoff_s * attempt)
            except Exception:
                attempt += 1
                if attempt > retries:
                    raise
                await asyncio.sleep(backoff_s * attempt)


class WorldBuilderAgentProxy(Agent):
    """Wraps World Builder Agent functionality with world state caching."""

    def __init__(self, *, coordinator: Optional[MessageCoordinator] = None, instance: Optional[str] = None, default_timeout_s: float = 12.0) -> None:
        super().__init__(agent_id=AgentId(type=AgentType.WBA, instance=instance), name=f"wba:{instance or 'default'}", coordinator=coordinator, default_timeout_s=default_timeout_s)
        self._cache: Dict[str, Any] = {}
        self._cache_ttl_s = 30.0
        self._cache_times: Dict[str, float] = {}

    def _cache_get(self, key: str) -> Optional[Any]:
        ts = self._cache_times.get(key)
        if ts is None:
            return None
        if (time.time() - ts) > self._cache_ttl_s:
            self._cache.pop(key, None)
            self._cache_times.pop(key, None)
            return None
        return self._cache.get(key)

    def _cache_set(self, key: str, value: Any) -> None:
        self._cache[key] = value
        self._cache_times[key] = time.time()

    async def process(self, input_payload: dict) -> dict:
        # Expected payload: {"world_id": str, "updates": {...} or None}
        world_id = (input_payload or {}).get("world_id")
        if not world_id:
            raise ValueError("WorldBuilderAgentProxy requires 'world_id'")
        updates = (input_payload or {}).get("updates")
        cache_key = f"world:{world_id}"
        if updates is None:
            cached = self._cache_get(cache_key)
            if cached is not None:
                return {"world_id": world_id, "world_state": cached, "cached": True}
            # Simulate fetch world state (placeholder)
            world_state = {"id": world_id, "regions": [], "entities": []}
            self._cache_set(cache_key, world_state)
            return {"world_id": world_id, "world_state": world_state, "cached": False}
        # Apply updates (placeholder logic)
        current = self._cache_get(cache_key) or {"id": world_id, "regions": [], "entities": []}
        if isinstance(updates, dict):
            current.update(updates)
        self._cache_set(cache_key, current)
        return {"world_id": world_id, "world_state": current, "updated": True}


class NarrativeGeneratorAgentProxy(Agent):
    """Wraps Narrative Generator Agent functionality with content filtering."""

    def __init__(self, *, coordinator: Optional[MessageCoordinator] = None, instance: Optional[str] = None, default_timeout_s: float = 15.0) -> None:
        super().__init__(agent_id=AgentId(type=AgentType.NGA, instance=instance), name=f"nga:{instance or 'default'}", coordinator=coordinator, default_timeout_s=default_timeout_s)

    def _filter_content(self, text: str) -> str:
        # Very basic content filtering placeholder; real implementation would use safety policies
        banned = ["violence", "hate"]
        lowered = text.lower()
        for b in banned:
            lowered = lowered.replace(b, "[redacted]")
        return lowered

    async def process(self, input_payload: dict) -> dict:
        # Expected payload: {"prompt": str, "context": {...}}
        prompt = (input_payload or {}).get("prompt", "").strip()
        if not prompt:
            raise ValueError("NarrativeGeneratorAgentProxy requires non-empty 'prompt'")
        context = (input_payload or {}).get("context") or {}
        # Simulate story generation (placeholder)
        story = f"Story: {prompt[:64]}..."
        filtered = self._filter_content(story)
        return {"story": filtered, "raw": story, "context_used": bool(context)}

