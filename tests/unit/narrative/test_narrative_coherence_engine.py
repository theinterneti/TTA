"""Unit tests for src/components/narrative_coherence_engine.py.

This module had 0% unit-gate coverage. Tests cover:
- All dataclass models and enums
- CoherenceValidator (with empty lore/character databases)
- ContradictionDetector
- CausalValidator
- NarrativeCoherenceEngine lifecycle and public API
"""

from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.components.narrative_coherence_engine import (
    CausalValidator,
    CoherenceValidator,
    ConsistencyIssue,
    ConsistencyIssueType,
    Contradiction,
    ContradictionDetector,
    ConvergenceValidation,
    CreativeSolution,
    LoreEntry,
    NarrativeCoherenceEngine,
    NarrativeContent,
    NarrativeResolution,
    RetroactiveChange,
    StorylineThread,
    ValidationResult,
    ValidationSeverity,
)

pytestmark = pytest.mark.unit

# The engine re-exports CoherenceValidator/ContradictionDetector/CausalValidator
# from src.components.narrative_coherence.*, which return their own ValidationResult.
# Import the extracted ValidationResult for isinstance checks on those classes.
try:
    from src.components.narrative_coherence.models import (
        ValidationResult as _ExtractedValidationResult,
    )
except ImportError:
    _ExtractedValidationResult = ValidationResult  # type: ignore[assignment,misc]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _config() -> dict:
    """Minimal config dict accepted by NarrativeCoherenceEngine."""
    return {}


def _content(
    content_id: str = "c-1",
    content_type: str = "scene",
    text: str = "The hero walks into the forest.",
) -> NarrativeContent:
    return NarrativeContent(
        content_id=content_id,
        content_type=content_type,
        text=text,
    )


def _contradiction(cid: str = "cx-1", ctype: str = "direct") -> Contradiction:
    return Contradiction(
        contradiction_id=cid,
        type=ctype,
        severity=ValidationSeverity.WARNING,
        description="Test contradiction",
        conflicting_elements=["e1", "e2"],
        confidence_score=0.75,
    )


def _engine() -> NarrativeCoherenceEngine:
    return NarrativeCoherenceEngine(config=_config())


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


def test_validation_severity_values():
    """Validation severity values."""
    assert ValidationSeverity.INFO.value == "info"
    assert ValidationSeverity.WARNING.value == "warning"
    assert ValidationSeverity.ERROR.value == "error"
    assert ValidationSeverity.CRITICAL.value == "critical"


def test_consistency_issue_type_values():
    """Consistency issue type values."""
    assert ConsistencyIssueType.LORE_VIOLATION.value == "lore_violation"
    assert (
        ConsistencyIssueType.THERAPEUTIC_MISALIGNMENT.value
        == "therapeutic_misalignment"
    )


# ---------------------------------------------------------------------------
# Dataclass models
# ---------------------------------------------------------------------------


def test_consistency_issue_defaults():
    """Consistency issue defaults."""
    issue = ConsistencyIssue(
        issue_id="i-1",
        issue_type=ConsistencyIssueType.LORE_VIOLATION,
        severity=ValidationSeverity.ERROR,
        description="Missing lore reference",
    )
    assert issue.affected_elements == []
    assert issue.confidence_score == 0.0
    assert issue.suggested_fix is None
    assert isinstance(issue.metadata, dict)


def test_validation_result_defaults():
    """Validation result defaults."""
    vr = ValidationResult(is_valid=True, consistency_score=0.9)
    assert vr.detected_issues == []
    assert vr.lore_compliance == 0.0
    assert vr.character_consistency == 0.0
    assert vr.causal_consistency == 0.0
    assert vr.therapeutic_alignment == 0.0


def test_narrative_content_defaults():
    """Narrative content defaults."""
    c = _content()
    assert c.characters == []
    assert c.locations == []
    assert c.themes == []
    assert isinstance(c.timestamp, datetime)


def test_lore_entry_defaults():
    """Lore entry defaults."""
    le = LoreEntry(
        lore_id="l-1",
        category="location",
        title="The Dark Forest",
        description="A mysterious forest.",
    )
    assert le.constraints == []
    assert le.importance_weight == 1.0


def test_contradiction_defaults():
    """Contradiction defaults."""
    c = _contradiction()
    assert c.evidence == []
    assert c.resolution_suggestions == []
    assert isinstance(c.detected_at, datetime)


def test_creative_solution_defaults():
    """Creative solution defaults."""
    cs = CreativeSolution(
        solution_id="s-1",
        solution_type="character_driven",
        description="Character admits mistake",
    )
    assert cs.effectiveness_score == 0.0
    assert cs.narrative_cost == 0.0
    assert cs.player_impact == 0.0
    assert cs.required_changes == []


def test_narrative_resolution_defaults():
    """Narrative resolution defaults."""
    solution = CreativeSolution(
        solution_id="s-1", solution_type="character_driven", description="desc"
    )
    nr = NarrativeResolution(
        resolution_id="r-1",
        conflict_id="c-1",
        solution_used=solution,
        implementation_success=True,
    )
    assert nr.narrative_changes == []
    assert nr.effectiveness_rating == 0.0


def test_retroactive_change_fields():
    """Retroactive change fields."""
    rc = RetroactiveChange(
        change_id="rc-1",
        target_content_id="c-1",
        change_type="modification",
        original_content="original",
        modified_content="modified",
        justification="fix",
    )
    assert rc.in_world_explanation == ""
    assert rc.impact_scope == []


def test_storyline_thread_defaults():
    """Storyline thread defaults."""
    st = StorylineThread(thread_id="t-1", title="Main Quest")
    assert st.participants == []
    assert st.current_tension == 0.0
    assert st.resolution_target is None


def test_convergence_validation_fields():
    """Convergence validation fields."""
    cv = ConvergenceValidation(
        session_id="s-1",
        storyline_count=3,
        is_convergent=True,
        convergence_score=0.8,
    )
    assert cv.integration_issues == []
    assert cv.convergence_points == []
    assert isinstance(cv.validation_timestamp, datetime)


# ---------------------------------------------------------------------------
# CoherenceValidator
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_coherence_validator_valid_content():
    """Coherence validator valid content."""
    validator = CoherenceValidator(config={})
    content = _content()
    result = await validator.validate_narrative_consistency(content)
    assert isinstance(result, _ExtractedValidationResult)
    assert result.is_valid is True
    assert 0.0 <= result.consistency_score <= 1.0


@pytest.mark.asyncio
async def test_coherence_validator_empty_text():
    """Coherence validator empty text."""
    validator = CoherenceValidator(config={})
    content = _content(text="")
    result = await validator.validate_narrative_consistency(content)
    assert isinstance(result, _ExtractedValidationResult)


@pytest.mark.asyncio
async def test_coherence_validator_with_characters():
    """Coherence validator with characters."""
    validator = CoherenceValidator(config={})
    content = NarrativeContent(
        content_id="c-2",
        content_type="dialogue",
        text="Alice talks to Bob.",
        characters=["Alice", "Bob"],
    )
    result = await validator.validate_narrative_consistency(content)
    assert result is not None


@pytest.mark.asyncio
async def test_coherence_validator_with_lore_constraint_violation():
    """A character lore constraint 'must not contain X' that the content violates."""
    from src.components.narrative_coherence.models import LoreEntry as ExtLoreEntry

    validator = CoherenceValidator(config={})
    # Key must match the lookup pattern: "character_{character_name}"
    validator.lore_database["character_Wizard"] = ExtLoreEntry(
        lore_id="l-1",
        category="character",
        title="Wizard",
        description="The wizard.",
        constraints=["must not contain evil"],
    )
    content = NarrativeContent(
        content_id="c-x",
        content_type="scene",
        text="The wizard performed an evil ritual.",
        characters=["Wizard"],
    )
    result = await validator.validate_narrative_consistency(content)
    assert any(i.issue_type.value == "lore_violation" for i in result.detected_issues)


@pytest.mark.asyncio
async def test_coherence_validator_with_lore_positive_constraint():
    """A theme lore constraint 'must have X' that the content satisfies."""
    from src.components.narrative_coherence.models import LoreEntry as ExtLoreEntry

    validator = CoherenceValidator(config={})
    # Key must match "theme_{theme_name}"
    validator.lore_database["theme_Nature"] = ExtLoreEntry(
        lore_id="l-2",
        category="theme",
        title="Nature Theme",
        description="Must be about nature.",
        constraints=["must have forest"],
    )
    content = NarrativeContent(
        content_id="c-y",
        content_type="scene",
        text="They walked through the dense forest canopy.",
        themes=["Nature"],
    )
    result = await validator.validate_narrative_consistency(content)
    assert not any(
        i.issue_type.value == "lore_violation" for i in result.detected_issues
    )


@pytest.mark.asyncio
async def test_coherence_validator_consistency_threshold_config():
    """Coherence validator consistency threshold config."""
    validator = CoherenceValidator(config={"consistency_threshold": 0.5})
    assert validator.consistency_threshold == 0.5


# ---------------------------------------------------------------------------
# ContradictionDetector
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_contradiction_detector_empty_history():
    """Contradiction detector empty history."""
    detector = ContradictionDetector(config={})
    result = await detector.detect_contradictions([])
    assert result == []


@pytest.mark.asyncio
async def test_contradiction_detector_single_item():
    """Contradiction detector single item."""
    detector = ContradictionDetector(config={})
    result = await detector.detect_contradictions([_content()])
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_contradiction_detector_two_items():
    """Contradiction detector two items."""
    detector = ContradictionDetector(config={})
    c1 = _content("c1", text="The sky is blue.")
    c2 = _content("c2", text="The sky is green.")
    result = await detector.detect_contradictions([c1, c2])
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_contradiction_detector_returns_contradiction_objects():
    """Contradiction detector returns contradiction objects."""
    detector = ContradictionDetector(config={})
    c1 = _content("c1")
    c2 = _content("c2")
    result = await detector.detect_contradictions([c1, c2])
    for item in result:
        assert isinstance(item, Contradiction)


# ---------------------------------------------------------------------------
# CausalValidator
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_causal_validator_empty_branch():
    """Causal validator empty branch."""
    validator = CausalValidator(config={})
    result = await validator.validate_causal_logic([])
    assert isinstance(result, _ExtractedValidationResult)


@pytest.mark.asyncio
async def test_causal_validator_single_item():
    """Causal validator single item."""
    validator = CausalValidator(config={})
    result = await validator.validate_causal_logic([_content()])
    assert isinstance(result, _ExtractedValidationResult)
    assert 0.0 <= result.causal_consistency <= 1.0


@pytest.mark.asyncio
async def test_causal_validator_multiple_items():
    """Causal validator multiple items."""
    validator = CausalValidator(config={})
    branch = [_content(f"c-{i}", text=f"Event {i} occurred.") for i in range(3)]
    result = await validator.validate_causal_logic(branch)
    assert isinstance(result, _ExtractedValidationResult)


# ---------------------------------------------------------------------------
# NarrativeCoherenceEngine – construction and lifecycle
# ---------------------------------------------------------------------------


def test_engine_construction():
    """Engine construction."""
    engine = _engine()
    assert engine.coherence_validator is not None
    assert engine.contradiction_detector is not None
    assert engine.causal_validator is not None
    assert engine.content_history == {}
    assert engine.validation_cache == {}


def test_engine_start_stop():
    """Engine start stop."""
    engine = _engine()
    assert engine.start() is True
    assert engine.stop() is True
    assert engine.content_history == {}
    assert engine.validation_cache == {}


# ---------------------------------------------------------------------------
# NarrativeCoherenceEngine – validate_narrative_consistency
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_engine_validate_narrative_consistency_happy_path():
    """Engine validate narrative consistency happy path."""
    engine = _engine()
    content = _content()
    result = await engine.validate_narrative_consistency(content, "session-1")
    # Use duck-typing: the engine may return extracted or local ValidationResult
    assert hasattr(result, "is_valid")
    assert hasattr(result, "consistency_score")
    assert "session-1" in engine.content_history
    assert len(engine.content_history["session-1"]) == 1


@pytest.mark.asyncio
async def test_engine_validate_caches_result():
    """Engine validate caches result."""
    engine = _engine()
    content = _content()
    await engine.validate_narrative_consistency(content, "session-1")
    cache_key = f"session-1_{content.content_id}"
    assert cache_key in engine.validation_cache


@pytest.mark.asyncio
async def test_engine_validate_returns_cached_result():
    """Engine validate returns cached result."""
    engine = _engine()
    content = _content()
    result1 = await engine.validate_narrative_consistency(content, "session-1")
    result2 = await engine.validate_narrative_consistency(content, "session-1")
    assert result1 is result2  # same object returned from cache


@pytest.mark.asyncio
async def test_engine_validate_multiple_sessions_are_independent():
    """Engine validate multiple sessions are independent."""
    engine = _engine()
    c1 = _content("c1")
    c2 = _content("c2")
    await engine.validate_narrative_consistency(c1, "session-A")
    await engine.validate_narrative_consistency(c2, "session-B")
    assert len(engine.content_history["session-A"]) == 1
    assert len(engine.content_history["session-B"]) == 1


@pytest.mark.asyncio
async def test_engine_validate_error_returns_invalid_result():
    """Engine validate error returns invalid result."""
    engine = _engine()
    # Mock coherence_validator to raise
    engine.coherence_validator.validate_narrative_consistency = AsyncMock(
        side_effect=RuntimeError("validator down")
    )
    result = await engine.validate_narrative_consistency(_content(), "session-err")
    assert hasattr(result, "is_valid")
    assert result.is_valid is False
    assert len(result.detected_issues) >= 1


# ---------------------------------------------------------------------------
# NarrativeCoherenceEngine – detect_contradictions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_engine_detect_contradictions_empty_history():
    """Engine detect contradictions empty history."""
    engine = _engine()
    result = await engine.detect_contradictions("no-history")
    assert result == []


@pytest.mark.asyncio
async def test_engine_detect_contradictions_single_item_history():
    """Engine detect contradictions single item history."""
    engine = _engine()
    engine.content_history["s-1"] = [_content()]
    result = await engine.detect_contradictions("s-1")
    assert result == []


@pytest.mark.asyncio
async def test_engine_detect_contradictions_two_item_history():
    """Engine detect contradictions two item history."""
    engine = _engine()
    engine.content_history["s-1"] = [_content("c1"), _content("c2")]
    result = await engine.detect_contradictions("s-1")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_engine_detect_contradictions_error_returns_empty():
    """Engine detect contradictions error returns empty."""
    engine = _engine()
    engine.content_history["s-1"] = [_content("c1"), _content("c2")]
    engine.contradiction_detector.detect_contradictions = AsyncMock(
        side_effect=RuntimeError("detector down")
    )
    result = await engine.detect_contradictions("s-1")
    assert result == []


# ---------------------------------------------------------------------------
# NarrativeCoherenceEngine – validate_causal_logic
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_engine_validate_causal_logic():
    """Engine validate causal logic."""
    engine = _engine()
    branch = [_content(f"c{i}") for i in range(3)]
    result = await engine.validate_causal_logic(branch)
    assert hasattr(result, "is_valid")
    assert hasattr(result, "consistency_score")


@pytest.mark.asyncio
async def test_engine_validate_causal_logic_error_returns_invalid():
    """Engine validate causal logic error returns invalid."""
    engine = _engine()
    engine.causal_validator.validate_causal_logic = AsyncMock(
        side_effect=RuntimeError("causal down")
    )
    result = await engine.validate_causal_logic([_content()])
    assert hasattr(result, "is_valid")
    assert result.is_valid is False


# ---------------------------------------------------------------------------
# NarrativeCoherenceEngine – get_coherence_status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_engine_get_coherence_status_no_history():
    """Engine get coherence status no history."""
    engine = _engine()
    status = await engine.get_coherence_status("empty-session")
    assert status["content_count"] == 0
    assert status["overall_coherence"] == 1.0
    assert status["contradiction_count"] == 0


@pytest.mark.asyncio
async def test_engine_get_coherence_status_with_content():
    """Engine get coherence status with content."""
    engine = _engine()
    content = _content()
    await engine.validate_narrative_consistency(content, "s-1")
    status = await engine.get_coherence_status("s-1")
    assert status["content_count"] == 1
    assert "overall_coherence" in status


@pytest.mark.asyncio
async def test_engine_get_coherence_status_validation_error_handled():
    """When coherence_validator raises, engine wraps error in ValidationResult.
    get_coherence_status still returns a valid status dict (error is absorbed)."""
    engine = _engine()
    engine.content_history["s-err"] = [_content()]
    engine.coherence_validator.validate_narrative_consistency = AsyncMock(
        side_effect=RuntimeError("crash")
    )
    status = await engine.get_coherence_status("s-err")
    # Either the error is propagated to the status dict or absorbed —
    # either way the session_id must be present
    assert "session_id" in status
    assert status["session_id"] == "s-err"


# ---------------------------------------------------------------------------
# NarrativeCoherenceEngine – resolve_narrative_conflicts
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_engine_resolve_conflicts_empty_list():
    """Engine resolve conflicts empty list."""
    engine = _engine()
    result = await engine.resolve_narrative_conflicts([], "s-1")
    assert result == []


@pytest.mark.asyncio
async def test_engine_resolve_conflicts_returns_list():
    """Engine resolve conflicts returns list."""
    engine = _engine()
    contradiction = _contradiction()
    result = await engine.resolve_narrative_conflicts([contradiction], "s-1")
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# NarrativeCoherenceEngine – cache management
# ---------------------------------------------------------------------------


def test_engine_cache_miss_returns_none():
    """Engine cache miss returns none."""
    engine = _engine()
    assert engine._get_cached_validation("missing_key") is None


def test_engine_cache_store_and_retrieve():
    """Engine cache store and retrieve."""
    engine = _engine()
    vr = ValidationResult(is_valid=True, consistency_score=0.9)
    vr.validation_timestamp = datetime.now()
    engine._cache_validation_result("key1", vr)
    assert engine._get_cached_validation("key1") is vr


def test_engine_cache_expired_returns_none():
    """Engine cache expired returns none."""
    engine = _engine()
    engine.cache_ttl = 0  # immediate expiry
    vr = ValidationResult(is_valid=True, consistency_score=0.9)
    import time

    time.sleep(0.01)
    vr.validation_timestamp = datetime(2000, 1, 1)  # old timestamp
    engine.validation_cache["key"] = vr
    assert engine._get_cached_validation("key") is None


def test_engine_cleanup_cache_removes_expired():
    """Engine cleanup cache removes expired."""
    engine = _engine()
    engine.cache_ttl = 0
    vr = ValidationResult(is_valid=True, consistency_score=0.9)
    vr.validation_timestamp = datetime(2000, 1, 1)
    engine.validation_cache["old"] = vr
    engine._cleanup_cache()
    assert "old" not in engine.validation_cache
