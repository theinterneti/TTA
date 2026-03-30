"""Safety service orchestration and global service management."""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Safety_monitoring/Service]]

from __future__ import annotations

import contextlib  # BUG FIX: Added missing import (line 3513 uses contextlib.suppress())
import json

from ..safety_validation.enums import SafetyLevel
from ..safety_validation.models import ValidationResult
from ..therapeutic_scoring.validator import TherapeuticValidator
from .provider import SafetyRulesProvider, _Redis


class SafetyService:
    """Orchestrates validation using a rules provider and enabled flag.

    Provides async validate method and caches compiled validator, refreshing when
    the underlying raw JSON changes (TTL handled by provider).
    """

    def __init__(self, enabled: bool = False, provider: SafetyRulesProvider | None = None) -> None:
        self._enabled = bool(enabled)
        self._provider = provider or SafetyRulesProvider(redis_client=None)
        self._last_raw: str | None = None
        self._validator: TherapeuticValidator | None = None

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    def is_enabled(self) -> bool:
        return self._enabled

    async def _ensure_validator(self) -> TherapeuticValidator:
        cfg = await self._provider.get_config()
        raw = json.dumps(cfg)
        if (self._validator is None) or (raw != self._last_raw):
            self._validator = TherapeuticValidator(config=cfg)
            self._last_raw = raw
        return self._validator

    async def validate_text(self, text: str) -> ValidationResult:
        if not self._enabled:
            # Fast path when disabled
            return ValidationResult(
                level=SafetyLevel.SAFE,
                findings=[],
                score=1.0,
                audit=[{"event": "disabled"}],
            )
        v = await self._ensure_validator()
        return v.validate_text(text)

    def suggest_alternative(self, level: SafetyLevel, original: str) -> str:
        """Suggest alternative content for unsafe text."""
        self._validator or TherapeuticValidator()
        # Generate therapeutic alternative based on level
        if level == SafetyLevel.BLOCKED:
            return (
                "I understand you're going through a difficult time. "
                "Let's focus on finding healthy ways to cope with these feelings. "
                "Would you like to talk about what's troubling you?"
            )
        if level == SafetyLevel.WARNING:
            return (
                "I hear that you're struggling. It's important to approach this "
                "in a way that supports your wellbeing. Can we explore this together "
                "in a more constructive way?"
            )
        return original


# Global service management
_global_safety_service: SafetyService | None = None
_global_safety_locked: bool = False  # When True, do not auto-refresh from env (component-managed)


def get_global_safety_service() -> SafetyService:
    """Returns process-wide SafetyService. Attempts to initialize a Redis client
    using TEST_REDIS_URI or default localhost. Disabled by default, can be enabled
    via env AGENT_ORCHESTRATION_SAFETY_ENABLED=true for ad-hoc use or via tests.
    """
    global _global_safety_service, _global_safety_locked
    import os

    if _global_safety_service is None:
        enabled = False
        try:
            enabled = str(
                os.environ.get("AGENT_ORCHESTRATION_SAFETY_ENABLED", "false")
            ).lower() in ("1", "true", "yes")
            redis_client = None
            if _Redis is not None:
                url = os.environ.get("TEST_REDIS_URI") or "redis://localhost:6379/0"
                try:
                    import redis.asyncio as aioredis  # type: ignore

                    redis_client = aioredis.from_url(url)
                except Exception:
                    redis_client = None
            provider = SafetyRulesProvider(redis_client=redis_client)
            _global_safety_service = SafetyService(enabled=enabled, provider=provider)
        except Exception:
            _global_safety_service = SafetyService(
                enabled=False, provider=SafetyRulesProvider(redis_client=None)
            )
    elif not _global_safety_locked:
        with contextlib.suppress(Exception):
            enabled = str(
                os.environ.get("AGENT_ORCHESTRATION_SAFETY_ENABLED", "false")
            ).lower() in ("1", "true", "yes")
            _global_safety_service.set_enabled(enabled)

    return _global_safety_service


def set_global_safety_service_for_testing(svc: SafetyService) -> None:
    """Set global safety service for testing purposes."""
    global _global_safety_service, _global_safety_locked
    _global_safety_service = svc
    _global_safety_locked = True
