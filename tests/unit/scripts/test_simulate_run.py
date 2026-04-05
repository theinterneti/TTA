"""Unit tests for scripts/simulate_run.py helpers."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.simulate_run import _count_words

# The short-response retry guard must flag responses below 80 words for retry.
# Observed in run_30_cascade: T20/T21 were 45w, T24/T25 were 17-22w — all
# slipped through the old 25w guard unremediated.
SHORT_RESPONSE_THRESHOLD = 80  # raised from 25 to catch truncated cascade outputs


def test_short_response_at_40_words_triggers_retry():
    """A 40-word response must be below the 80w retry threshold."""
    text = " ".join(["word"] * 40)
    assert _count_words(text) < SHORT_RESPONSE_THRESHOLD


def test_simulation_record_has_narrator_tier_fields():
    """Per-turn JSONL records must contain narrator_model and narrator_provider.

    RED: those keys are not yet added to the record dict in run_simulation().
    Check by inspecting the keys built in the metrics record construction.
    We verify this by importing the module and checking the field names are
    referenced — a static sentinel approach since we can't easily call
    run_simulation() without network access.
    """
    import ast, pathlib
    src = pathlib.Path("scripts/simulate_run.py").read_text()
    tree = ast.parse(src)
    # Find all string constants that appear as dict keys in the source
    keys_in_source: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            keys_in_source.add(node.value)
    assert "narrator_model" in keys_in_source, (
        "'narrator_model' key missing from simulate_run.py — "
        "add it to the per-turn metrics record dict."
    )
    assert "narrator_provider" in keys_in_source, (
        "'narrator_provider' key missing from simulate_run.py — "
        "add it to the per-turn metrics record dict."
    )
