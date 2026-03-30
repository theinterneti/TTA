"""Unit tests for src/components/narrative_coherence/.

Covers five previously 0%-coverage modules:
- rules.py (constants)
- models.py (data classes / enums)
- causal_validator.py (CausalValidator)
- coherence_validator.py (CoherenceValidator)
"""

from __future__ import annotations

import pytest

from src.components.narrative_coherence.causal_validator import CausalValidator
from src.components.narrative_coherence.coherence_validator import CoherenceValidator
from src.components.narrative_coherence.models import (
    ConsistencyIssue,
    ConsistencyIssueType,
    Contradiction,
    ConvergenceValidation,
    CreativeSolution,
    LoreEntry,
    NarrativeContent,
    NarrativeResolution,
    RetroactiveChange,
    StorylineThread,
    ValidationResult,
    ValidationSeverity,
)
from src.components.narrative_coherence.rules import (
    OVERALL_WEIGHTS,
    SEVERITY_WEIGHTS_LORE,
    SEVERITY_WEIGHTS_THERAPEUTIC,
)

# ---------------------------------------------------------------------------
# rules.py — constants
# ---------------------------------------------------------------------------


def test_severity_weights_lore_expected_keys():
    assert set(SEVERITY_WEIGHTS_LORE) == {"INFO", "WARNING", "ERROR", "CRITICAL"}


def test_severity_weights_lore_ordered():
    w = SEVERITY_WEIGHTS_LORE
    assert w["INFO"] < w["WARNING"] < w["ERROR"] < w["CRITICAL"]


def test_severity_weights_therapeutic_expected_keys():
    assert set(SEVERITY_WEIGHTS_THERAPEUTIC) == {"INFO", "WARNING", "ERROR", "CRITICAL"}


def test_overall_weights_sum_to_one():
    assert sum(OVERALL_WEIGHTS.values()) == pytest.approx(1.0)


def test_overall_weights_expected_components():
    assert set(OVERALL_WEIGHTS) == {"lore", "character", "causal", "therapeutic"}


# ---------------------------------------------------------------------------
# models.py — enums
# ---------------------------------------------------------------------------


def test_validation_severity_values():
    assert ValidationSeverity.INFO.value == "info"
    assert ValidationSeverity.WARNING.value == "warning"
    assert ValidationSeverity.ERROR.value == "error"
    assert ValidationSeverity.CRITICAL.value == "critical"


def test_consistency_issue_type_values():
    assert ConsistencyIssueType.LORE_VIOLATION.value == "lore_violation"
    assert (
        ConsistencyIssueType.THERAPEUTIC_MISALIGNMENT.value
        == "therapeutic_misalignment"
    )


# ---------------------------------------------------------------------------
# models.py — data classes
# ---------------------------------------------------------------------------


def test_narrative_content_defaults():
    content = NarrativeContent(content_id="c1", content_type="scene", text="A forest.")
    assert content.related_characters == []
    assert content.themes == []
    assert content.therapeutic_concepts == []
    assert content.metadata == {}


def test_narrative_content_character_alias():
    content = NarrativeContent(
        content_id="c1",
        content_type="scene",
        text="text",
        related_characters=["hero"],
        related_locations=["forest"],
    )
    assert content.characters == ["hero"]
    assert content.locations == ["forest"]


def test_validation_result_defaults():
    result = ValidationResult(is_valid=True, consistency_score=0.9)
    assert result.detected_issues == []
    assert result.suggested_corrections == []
    assert result.lore_compliance == 0.0


def test_consistency_issue_defaults():
    issue = ConsistencyIssue(
        issue_id="i1",
        issue_type=ConsistencyIssueType.LORE_VIOLATION,
        severity=ValidationSeverity.WARNING,
        description="Test issue",
    )
    assert issue.confidence_score == 0.0
    assert issue.affected_elements == []
    assert issue.suggested_fix == ""


def test_lore_entry_defaults():
    entry = LoreEntry(
        lore_id="l1", category="character", title="Hero", description="A brave hero."
    )
    assert entry.canonical is True
    assert entry.constraints == []
    assert entry.importance_weight == 1.0


def test_storyline_thread_defaults():
    thread = StorylineThread(thread_id="t1", title="Main quest")
    assert thread.participants == []
    assert thread.resolution_target is None


def test_convergence_validation_defaults():
    cv = ConvergenceValidation(session_id="s1", storyline_count=3, is_convergent=True)
    assert cv.strong_connections == []
    assert cv.convergence_score == 0.0


def test_contradiction_defaults():
    c = Contradiction(
        contradiction_id="x1",
        type="temporal",
        severity=ValidationSeverity.ERROR,
        description="Paradox detected",
    )
    assert c.confidence_score == 0.0
    assert c.related_issues == []


def test_creative_solution_defaults():
    cs = CreativeSolution(
        solution_id="s1", solution_type="rewrite", description="Rewrite scene"
    )
    assert cs.narrative_cost == 0.0
    assert cs.player_impact == 0.0


# ---------------------------------------------------------------------------
# causal_validator.py — init
# ---------------------------------------------------------------------------


def test_causal_validator_init_loads_rules():
    v = CausalValidator(config={})
    assert "temporal_precedence" in v.causal_rules
    assert "logical_necessity" in v.causal_rules
    assert "proportional_response" in v.causal_rules
    assert "causal_sufficiency" in v.causal_rules


def test_causal_validator_init_loads_logical_operators():
    v = CausalValidator(config={})
    assert "if" in v.logical_operators
    assert "therefore" in v.logical_operators
    assert "caused by" in v.logical_operators


def test_causal_validator_init_loads_consequence_patterns():
    v = CausalValidator(config={})
    assert "immediate" in v.consequence_patterns
    assert "delayed" in v.consequence_patterns
    assert "gradual" in v.consequence_patterns
    assert "sudden" in v.consequence_patterns


# ---------------------------------------------------------------------------
# causal_validator.py — validate_causal_logic (empty branch)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_causal_validator_empty_branch_valid():
    v = CausalValidator(config={})
    result = await v.validate_causal_logic([])
    assert result.is_valid is True
    assert result.causal_consistency == pytest.approx(1.0)
    assert result.detected_issues == []


@pytest.mark.asyncio
async def test_causal_validator_empty_branch_returns_corrections():
    v = CausalValidator(config={})
    result = await v.validate_causal_logic([])
    assert result.suggested_corrections == []


# ---------------------------------------------------------------------------
# causal_validator.py — validate_causal_logic (non-empty branch with placeholders)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_causal_validator_non_empty_branch_no_issues():
    v = CausalValidator(config={})
    content = NarrativeContent(
        content_id="c1", content_type="scene", text="A begins, B follows."
    )
    result = await v.validate_causal_logic([content])
    # All sub-validators are placeholders returning []
    assert result.is_valid is True
    assert result.causal_consistency == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_causal_validator_respects_custom_threshold():
    v = CausalValidator(config={"causal_threshold": 0.99})
    result = await v.validate_causal_logic([])
    # score=1.0 still passes even with 0.99 threshold
    assert result.is_valid is True


# ---------------------------------------------------------------------------
# causal_validator.py — _calculate_causal_consistency_score
# ---------------------------------------------------------------------------


def test_causal_consistency_score_no_issues():
    v = CausalValidator(config={})
    assert v._calculate_causal_consistency_score([]) == pytest.approx(1.0)


def test_causal_consistency_score_with_critical_issue():
    v = CausalValidator(config={})
    issue = ConsistencyIssue(
        issue_id="i1",
        issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
        severity=ValidationSeverity.CRITICAL,
        description="Critical causal flaw",
        confidence_score=1.0,
    )
    score = v._calculate_causal_consistency_score([issue])
    # penalty = 1.0 * 1.0 = 1.0; max_penalty = 1.0 → score = max(0, 1 - 1) = 0
    assert score == pytest.approx(0.0)


def test_causal_consistency_score_with_low_confidence():
    v = CausalValidator(config={})
    issue = ConsistencyIssue(
        issue_id="i1",
        issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
        severity=ValidationSeverity.ERROR,
        description="Low confidence error",
        confidence_score=0.0,  # zero confidence → no penalty
    )
    score = v._calculate_causal_consistency_score([issue])
    assert score == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# causal_validator.py — corrections generation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_causal_generate_corrections_for_issues():
    v = CausalValidator(config={})
    issue = ConsistencyIssue(
        issue_id="i1",
        issue_type=ConsistencyIssueType.CAUSAL_INCONSISTENCY,
        severity=ValidationSeverity.WARNING,
        description="Broken chain",
        confidence_score=0.0,
    )
    corrections = await v._generate_causal_corrections([issue])
    assert len(corrections) == 1
    assert "Broken chain" in corrections[0]


# ---------------------------------------------------------------------------
# coherence_validator.py — init
# ---------------------------------------------------------------------------


def test_coherence_validator_init_default_thresholds():
    v = CoherenceValidator(config={})
    assert v.consistency_threshold == pytest.approx(0.7)
    assert v.lore_compliance_threshold == pytest.approx(0.8)
    assert v.character_consistency_threshold == pytest.approx(0.75)


def test_coherence_validator_init_custom_thresholds():
    v = CoherenceValidator(config={"consistency_threshold": 0.5})
    assert v.consistency_threshold == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# coherence_validator.py — validate_narrative_consistency (clean content)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_coherence_validator_clean_content_is_valid():
    v = CoherenceValidator(config={})
    content = NarrativeContent(
        content_id="c1", content_type="scene", text="The hero walks through the forest."
    )
    result = await v.validate_narrative_consistency(content)
    assert result.is_valid is True
    # causal_consistency is 0.0 (not set by coherence_validator); overall = 0.75
    assert result.consistency_score == pytest.approx(0.75)
    assert result.detected_issues == []


@pytest.mark.asyncio
async def test_coherence_validator_clean_content_scores_all_ones():
    v = CoherenceValidator(config={})
    content = NarrativeContent(
        content_id="c2", content_type="dialogue", text="Hello world."
    )
    result = await v.validate_narrative_consistency(content)
    assert result.lore_compliance == pytest.approx(1.0)
    assert result.character_consistency == pytest.approx(1.0)
    assert result.therapeutic_alignment == pytest.approx(1.0)
    assert result.causal_consistency == pytest.approx(
        0.0
    )  # not set by coherence_validator


# ---------------------------------------------------------------------------
# coherence_validator.py — unknown character triggers WARNING issue
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_coherence_validator_unknown_character_emits_warning():
    v = CoherenceValidator(config={"character_consistency_threshold": 0.0})
    content = NarrativeContent(
        content_id="c3",
        content_type="scene",
        text="The stranger speaks.",
        related_characters=["stranger"],
    )
    result = await v.validate_narrative_consistency(content)
    char_issues = [
        i
        for i in result.detected_issues
        if i.issue_type == ConsistencyIssueType.CHARACTER_INCONSISTENCY
    ]
    assert len(char_issues) == 1
    assert char_issues[0].severity == ValidationSeverity.WARNING
    assert "stranger" in char_issues[0].description


# ---------------------------------------------------------------------------
# coherence_validator.py — lore constraints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_coherence_validator_lore_must_not_constraint_violation():
    v = CoherenceValidator(config={})
    lore = LoreEntry(
        lore_id="l1",
        category="character",
        title="Hero",
        description="A brave hero.",
        constraints=["must not betray the party"],
    )
    v.lore_database["character_hero"] = lore
    content = NarrativeContent(
        content_id="c4",
        content_type="scene",
        text="The hero decides to betray the party.",
        related_characters=["hero"],
    )
    result = await v.validate_narrative_consistency(content)
    lore_issues = [
        i
        for i in result.detected_issues
        if i.issue_type == ConsistencyIssueType.LORE_VIOLATION
    ]
    assert len(lore_issues) >= 1


@pytest.mark.asyncio
async def test_coherence_validator_lore_must_have_constraint_satisfied():
    v = CoherenceValidator(config={})
    lore = LoreEntry(
        lore_id="l2",
        category="character",
        title="Hero",
        description="A brave hero.",
        constraints=["must have sword"],
    )
    v.lore_database["character_hero"] = lore
    content = NarrativeContent(
        content_id="c5",
        content_type="scene",
        text="The hero raises the sword high.",
        related_characters=["hero"],
    )
    result = await v.validate_narrative_consistency(content)
    lore_issues = [
        i
        for i in result.detected_issues
        if i.issue_type == ConsistencyIssueType.LORE_VIOLATION
    ]
    # "sword" is present → no lore violation
    assert len(lore_issues) == 0


@pytest.mark.asyncio
async def test_coherence_validator_lore_must_have_constraint_violated():
    v = CoherenceValidator(config={})
    lore = LoreEntry(
        lore_id="l3",
        category="character",
        title="Hero",
        description="A brave hero.",
        constraints=["must have staff"],
    )
    v.lore_database["character_hero"] = lore
    content = NarrativeContent(
        content_id="c6",
        content_type="scene",
        text="The hero walks unarmed.",
        related_characters=["hero"],
    )
    result = await v.validate_narrative_consistency(content)
    lore_issues = [
        i
        for i in result.detected_issues
        if i.issue_type == ConsistencyIssueType.LORE_VIOLATION
    ]
    assert len(lore_issues) >= 1


# ---------------------------------------------------------------------------
# coherence_validator.py — scoring helpers (direct calls)
# ---------------------------------------------------------------------------


def test_calculate_lore_compliance_no_issues():
    v = CoherenceValidator(config={})
    assert v._calculate_lore_compliance_score([]) == pytest.approx(1.0)


def test_calculate_lore_compliance_critical_full_penalty():
    v = CoherenceValidator(config={})
    issue = ConsistencyIssue(
        issue_id="i1",
        issue_type=ConsistencyIssueType.LORE_VIOLATION,
        severity=ValidationSeverity.CRITICAL,
        description="Critical lore breach",
    )
    score = v._calculate_lore_compliance_score([issue])
    # penalty = 1.0; max_penalty = 1.0 → score = max(0, 0) = 0
    assert score == pytest.approx(0.0)


def test_calculate_therapeutic_alignment_no_issues():
    v = CoherenceValidator(config={})
    assert v._calculate_therapeutic_alignment_score([]) == pytest.approx(1.0)


def test_calculate_overall_consistency_score():
    v = CoherenceValidator(config={})
    result = ValidationResult(
        is_valid=True,
        consistency_score=0.0,
        lore_compliance=1.0,
        character_consistency=1.0,
        causal_consistency=1.0,
        therapeutic_alignment=1.0,
    )
    score = v._calculate_overall_consistency_score(result)
    assert score == pytest.approx(1.0)


def test_calculate_overall_consistency_score_partial():
    v = CoherenceValidator(config={})
    result = ValidationResult(
        is_valid=True,
        consistency_score=0.0,
        lore_compliance=0.0,
        character_consistency=0.0,
        causal_consistency=0.0,
        therapeutic_alignment=0.0,
    )
    assert v._calculate_overall_consistency_score(result) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# coherence_validator.py — generic corrections
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_generic_correction_lore_violation():
    v = CoherenceValidator(config={})
    issue = ConsistencyIssue(
        issue_id="i1",
        issue_type=ConsistencyIssueType.LORE_VIOLATION,
        severity=ValidationSeverity.WARNING,
        description="Lore problem",
        affected_elements=["hero"],
    )
    correction = await v._generate_generic_correction(issue)
    assert correction is not None
    assert "hero" in correction


@pytest.mark.asyncio
async def test_generate_generic_correction_character_inconsistency():
    v = CoherenceValidator(config={})
    issue = ConsistencyIssue(
        issue_id="i2",
        issue_type=ConsistencyIssueType.CHARACTER_INCONSISTENCY,
        severity=ValidationSeverity.WARNING,
        description="Char problem",
        affected_elements=["npc"],
    )
    correction = await v._generate_generic_correction(issue)
    assert correction is not None
    assert "npc" in correction


@pytest.mark.asyncio
async def test_generate_corrections_uses_suggested_fix_when_present():
    v = CoherenceValidator(config={})
    issue = ConsistencyIssue(
        issue_id="i3",
        issue_type=ConsistencyIssueType.LORE_VIOLATION,
        severity=ValidationSeverity.WARNING,
        description="Problem",
        suggested_fix="Use canonical name",
    )
    corrections = await v._generate_corrections([issue])
    assert "Use canonical name" in corrections


@pytest.mark.asyncio
async def test_generate_corrections_therapeutic_misalignment():
    v = CoherenceValidator(config={})
    issue = ConsistencyIssue(
        issue_id="i4",
        issue_type=ConsistencyIssueType.THERAPEUTIC_MISALIGNMENT,
        severity=ValidationSeverity.ERROR,
        description="Therapeutic issue",
    )
    correction = await v._generate_generic_correction(issue)
    assert correction is not None
    assert "therapeutic" in correction.lower()


# ---------------------------------------------------------------------------
# contradiction_detector.py — ContradictionDetector
# ---------------------------------------------------------------------------


from src.components.narrative_coherence.contradiction_detector import (
    ContradictionDetector,
)


def test_contradiction_detector_init_loads_patterns():
    d = ContradictionDetector(config={})
    assert "negation" in d.contradiction_patterns
    assert "affirmation" in d.contradiction_patterns
    assert "temporal_conflict" in d.contradiction_patterns
    assert "state_change" in d.contradiction_patterns
    assert "existence" in d.contradiction_patterns


def test_contradiction_detector_init_loads_temporal_markers():
    d = ContradictionDetector(config={})
    assert "yesterday" in d.temporal_markers
    assert "tomorrow" in d.temporal_markers
    assert "before" in d.temporal_markers


def test_contradiction_detector_init_loads_causal_indicators():
    d = ContradictionDetector(config={})
    assert "because" in d.causal_indicators
    assert "therefore" in d.causal_indicators
    assert "caused by" in d.causal_indicators


@pytest.mark.asyncio
async def test_contradiction_detector_empty_history_returns_empty():
    d = ContradictionDetector(config={})
    result = await d.detect_contradictions([])
    assert result == []


@pytest.mark.asyncio
async def test_contradiction_detector_single_item_returns_empty():
    d = ContradictionDetector(config={})
    content = NarrativeContent(
        content_id="c1", content_type="scene", text="The hero walks."
    )
    result = await d.detect_contradictions([content])
    assert result == []


@pytest.mark.asyncio
async def test_contradiction_detector_multiple_items_no_contradictions():
    d = ContradictionDetector(config={})
    items = [
        NarrativeContent(content_id=f"c{i}", content_type="scene", text=f"Scene {i}.")
        for i in range(3)
    ]
    result = await d.detect_contradictions(items)
    # All sub-methods are placeholders returning [] → no contradictions
    assert result == []
