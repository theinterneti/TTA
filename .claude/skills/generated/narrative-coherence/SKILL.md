---
name: narrative-coherence
description: "Skill for the Narrative_coherence area of TTA. 76 symbols across 5 files."
---

# Narrative_coherence

76 symbols | 5 files | Cohesion: 83%

## When to Use

- Working with code in `src/`
- Understanding how test_coherence_validator_valid_content, test_coherence_validator_empty_text, validate_narrative_consistency work
- Modifying narrative_coherence-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/components/narrative_coherence/coherence_validator.py` | validate_narrative_consistency, _calculate_lore_compliance_score, _calculate_character_consistency_score, _calculate_therapeutic_alignment_score, _calculate_overall_consistency_score (+24) |
| `src/components/narrative_coherence/causal_validator.py` | __init__, _load_causal_rules, _load_logical_operators, _load_consequence_patterns, _validate_logical_consistency (+12) |
| `src/components/narrative_coherence_engine.py` | validate_narrative_consistency, _validate_lore_compliance, _validate_world_rules, _validate_therapeutic_alignment, __init__ (+9) |
| `src/components/narrative_coherence/contradiction_detector.py` | __init__, _load_contradiction_patterns, _load_temporal_markers, _load_causal_indicators, _detect_direct_contradictions (+9) |
| `tests/unit/narrative/test_narrative_coherence_engine.py` | test_coherence_validator_valid_content, test_coherence_validator_empty_text |

## Entry Points

Start here when exploring this area:

- **`test_coherence_validator_valid_content`** (Function) — `tests/unit/narrative/test_narrative_coherence_engine.py:236`
- **`test_coherence_validator_empty_text`** (Function) — `tests/unit/narrative/test_narrative_coherence_engine.py:247`
- **`validate_narrative_consistency`** (Method) — `src/components/narrative_coherence/coherence_validator.py:46`
- **`validate_narrative_consistency`** (Method) — `src/components/narrative_coherence_engine.py:228`
- **`detect_contradictions`** (Method) — `src/components/narrative_coherence_engine.py:904`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_coherence_validator_valid_content` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 236 |
| `test_coherence_validator_empty_text` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 247 |
| `validate_narrative_consistency` | Method | `src/components/narrative_coherence/coherence_validator.py` | 46 |
| `validate_narrative_consistency` | Method | `src/components/narrative_coherence_engine.py` | 228 |
| `detect_contradictions` | Method | `src/components/narrative_coherence_engine.py` | 904 |
| `validate_causal_logic` | Method | `src/components/narrative_coherence_engine.py` | 1204 |
| `_calculate_lore_compliance_score` | Method | `src/components/narrative_coherence/coherence_validator.py` | 386 |
| `_calculate_character_consistency_score` | Method | `src/components/narrative_coherence/coherence_validator.py` | 395 |
| `_calculate_therapeutic_alignment_score` | Method | `src/components/narrative_coherence/coherence_validator.py` | 407 |
| `_calculate_overall_consistency_score` | Method | `src/components/narrative_coherence/coherence_validator.py` | 419 |
| `_generate_corrections` | Method | `src/components/narrative_coherence/coherence_validator.py` | 428 |
| `_generate_generic_correction` | Method | `src/components/narrative_coherence/coherence_validator.py` | 439 |
| `_validate_lore_compliance` | Method | `src/components/narrative_coherence/coherence_validator.py` | 113 |
| `_get_character_lore` | Method | `src/components/narrative_coherence/coherence_validator.py` | 246 |
| `_get_location_lore` | Method | `src/components/narrative_coherence/coherence_validator.py` | 249 |
| `_get_theme_lore` | Method | `src/components/narrative_coherence/coherence_validator.py` | 252 |
| `_check_character_lore_compliance` | Method | `src/components/narrative_coherence/coherence_validator.py` | 256 |
| `_check_location_lore_compliance` | Method | `src/components/narrative_coherence/coherence_validator.py` | 274 |
| `_check_theme_lore_compliance` | Method | `src/components/narrative_coherence/coherence_validator.py` | 292 |
| `_check_constraint_compliance` | Method | `src/components/narrative_coherence/coherence_validator.py` | 310 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Narrative | 2 calls |

## How to Explore

1. `context({name: "test_coherence_validator_valid_content"})` — see callers and callees
2. `query({search_query: "narrative_coherence"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
