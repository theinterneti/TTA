"""Token budget management for WorldContextBuilder.

Provides TierBudget (configurable per-tier token allocations) and
TokenCounter (tiktoken-backed with char-count fallback when not installed).

Issue: #276
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tier names (used as dict keys throughout the builder)
# ---------------------------------------------------------------------------

TIER_SYSTEM = "tier1_system"
TIER_SCENE = "tier2_scene"
TIER_NEO4J = "tier3_neo4j"
TIER_RULES = "tier4_rules"
TIER_HISTORY = "tier5_history"
TIER_CHARACTER = "tier6_character"

ALL_TIERS = [
    TIER_SYSTEM,
    TIER_SCENE,
    TIER_NEO4J,
    TIER_RULES,
    TIER_HISTORY,
    TIER_CHARACTER,
]


# ---------------------------------------------------------------------------
# TierBudget
# ---------------------------------------------------------------------------


@dataclass
class TierBudget:
    """Per-tier token allocations for the 6-tier WorldContext assembly.

    Default total: 7 500 tokens.  Tier allocations must not exceed total.

    Attributes:
        total:           Maximum tokens for the full assembled context.
        tier1_system:    System prompt + world constants.
        tier2_scene:     Current scene (location, NPCs, immediate events).
        tier3_neo4j:     Additional Neo4j graph context (connections, zone).
        tier4_rules:     World rules and lore.
        tier5_history:   Session history (recent conversation turns).
        tier6_character: Player character sheet.
    """

    total: int = 7500
    tier1_system: int = 800
    tier2_scene: int = 1500
    tier3_neo4j: int = 1000
    tier4_rules: int = 600
    tier5_history: int = 2300
    tier6_character: int = 300

    def __post_init__(self) -> None:
        allocated = self._allocated()
        if allocated > self.total:
            raise ValueError(
                f"Tier allocations ({allocated}) exceed total budget ({self.total}). "
                "Reduce one or more tier budgets."
            )

    def _allocated(self) -> int:
        return (
            self.tier1_system
            + self.tier2_scene
            + self.tier3_neo4j
            + self.tier4_rules
            + self.tier5_history
            + self.tier6_character
        )

    def budget_for(self, tier: str) -> int:
        """Return the token budget for a named tier."""
        budgets: dict[str, int] = {
            TIER_SYSTEM: self.tier1_system,
            TIER_SCENE: self.tier2_scene,
            TIER_NEO4J: self.tier3_neo4j,
            TIER_RULES: self.tier4_rules,
            TIER_HISTORY: self.tier5_history,
            TIER_CHARACTER: self.tier6_character,
        }
        if tier not in budgets:
            raise KeyError(f"Unknown tier: {tier!r}")
        return budgets[tier]

    @classmethod
    def minimal(cls) -> TierBudget:
        """Minimal budget for testing (1 200 token total)."""
        return cls(
            total=1200,
            tier1_system=200,
            tier2_scene=250,
            tier3_neo4j=200,
            tier4_rules=150,
            tier5_history=300,
            tier6_character=100,
        )


# ---------------------------------------------------------------------------
# TokenCounter
# ---------------------------------------------------------------------------

_CHARS_PER_TOKEN = 4  # rough approximation: 1 token ≈ 4 characters


class TokenCounter:
    """Count and truncate tokens.

    Uses tiktoken (cl100k_base encoding, compatible with GPT-4) when
    available; falls back to ``len(text) // 4`` otherwise.

    The fallback is conservative — it slightly over-counts — which means
    we truncate a little early rather than a little late.  That is safe.
    """

    def __init__(self) -> None:
        self._enc = None
        try:
            import tiktoken  # type: ignore[import-not-found]

            self._enc = tiktoken.get_encoding("cl100k_base")
            logger.debug("TokenCounter: using tiktoken cl100k_base")
        except Exception:
            logger.debug(
                "TokenCounter: tiktoken unavailable; using char-count fallback"
            )

    @property
    def backend(self) -> str:
        """Name of the active backend."""
        return "tiktoken" if self._enc is not None else "char_count"

    def count(self, text: str) -> int:
        """Return approximate token count for *text*."""
        if not text:
            return 0
        if self._enc is not None:
            return len(self._enc.encode(text))
        return max(1, len(text) // _CHARS_PER_TOKEN)

    def fits(self, text: str, budget: int) -> bool:
        """Return True if *text* fits within *budget* tokens."""
        return self.count(text) <= budget

    def truncate_to_budget(self, text: str, budget: int) -> str:
        """Return *text* truncated to at most *budget* tokens.

        If *text* already fits, it is returned unchanged.
        A ``"…"`` marker is appended when truncation occurs.
        """
        if not text or budget <= 0:
            return ""
        if self.fits(text, budget):
            return text

        if self._enc is not None:
            tokens = self._enc.encode(text)
            # Reserve 1 token for ellipsis marker
            truncated = self._enc.decode(tokens[: max(0, budget - 1)])
            return truncated + "…"

        # Char-count fallback
        max_chars = budget * _CHARS_PER_TOKEN
        return text[: max(0, max_chars - 1)] + "…"
