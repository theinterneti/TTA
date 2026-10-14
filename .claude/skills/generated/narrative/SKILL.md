---
name: narrative
description: "Skill for the Narrative area of TTA. 97 symbols across 16 files."
---

# Narrative

97 symbols | 16 files | Cohesion: 69%

## When to Use

- Working with code in `src/`
- Understanding how test_engine_validate_narrative_consistency_happy_path, test_engine_validate_caches_result, test_engine_validate_returns_cached_result work
- Modifying narrative-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/unit/narrative/test_narrative_coherence_engine.py` | _content, _engine, test_engine_validate_narrative_consistency_happy_path, test_engine_validate_caches_result, test_engine_validate_returns_cached_result (+20) |
| `tests/unit/components/test_therapeutic_narrative_modules.py` | test_assess_performance_average_default, test_assess_performance_excelling, test_get_recommended_difficulty, test_adjust_difficulty_returns_scene, test_adjust_difficulty_preserves_title (+15) |
| `src/components/narrative_coherence_engine.py` | validate_narrative_consistency, detect_contradictions, validate_causal_logic, get_coherence_status, _cache_validation_result (+2) |
| `src/components/gameplay_loop/narrative/scene_generator.py` | generate_therapeutic_scene, _generate_scene_content, _generate_narrative_content, _generate_narrative_content_llm, _generate_narrative_content_template (+2) |
| `src/components/gameplay_loop/narrative/error_recovery_manager.py` | initialize, log_error, get_recovery_strategy, _classify_severity, restore_checkpoint (+1) |
| `src/components/gameplay_loop/narrative/adaptive_difficulty_engine.py` | initialize, assess_performance, get_recommended_difficulty, adjust_difficulty, _apply_adjustment |
| `src/components/gameplay_loop/narrative/character_development_system.py` | initialize, get_character_arc_summary, track_character_growth, _ensure_arc |
| `src/components/gameplay_loop/narrative/emotional_safety_system.py` | initialize, trigger_safety_intervention, check_emotional_boundaries, _emotional_state_risk |
| `src/components/gameplay_loop/narrative/therapeutic_storyteller.py` | enhance_scene_with_therapy, create_therapeutic_metaphor, _apply_storytelling_technique, _apply_metaphor_technique |
| `src/components/gameplay_loop/narrative/pacing_controller.py` | analyze_session_pacing, _calculate_pacing_metrics, apply_pacing_adjustments, _apply_dimension_adjustment |

## Entry Points

Start here when exploring this area:

- **`test_engine_validate_narrative_consistency_happy_path`** (Function) — `tests/unit/narrative/test_narrative_coherence_engine.py:429`
- **`test_engine_validate_caches_result`** (Function) — `tests/unit/narrative/test_narrative_coherence_engine.py:442`
- **`test_engine_validate_returns_cached_result`** (Function) — `tests/unit/narrative/test_narrative_coherence_engine.py:452`
- **`test_engine_validate_multiple_sessions_are_independent`** (Function) — `tests/unit/narrative/test_narrative_coherence_engine.py:462`
- **`test_engine_validate_error_returns_invalid_result`** (Function) — `tests/unit/narrative/test_narrative_coherence_engine.py:474`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_engine_validate_narrative_consistency_happy_path` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 429 |
| `test_engine_validate_caches_result` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 442 |
| `test_engine_validate_returns_cached_result` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 452 |
| `test_engine_validate_multiple_sessions_are_independent` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 462 |
| `test_engine_validate_error_returns_invalid_result` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 474 |
| `test_engine_detect_contradictions_empty_history` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 493 |
| `test_engine_detect_contradictions_single_item_history` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 501 |
| `test_engine_detect_contradictions_two_item_history` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 510 |
| `test_engine_detect_contradictions_error_returns_empty` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 519 |
| `test_engine_validate_causal_logic` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 536 |
| `test_engine_validate_causal_logic_error_returns_invalid` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 546 |
| `test_engine_get_coherence_status_no_history` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 563 |
| `test_engine_get_coherence_status_with_content` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 573 |
| `test_engine_get_coherence_status_validation_error_handled` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 584 |
| `test_engine_cache_store_and_retrieve` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 632 |
| `test_engine_cleanup_cache_removes_expired` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 654 |
| `test_contradiction_detector_single_item` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 340 |
| `test_contradiction_detector_two_items` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 348 |
| `test_contradiction_detector_returns_contradiction_objects` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 358 |
| `test_causal_validator_single_item` | Function | `tests/unit/narrative/test_narrative_coherence_engine.py` | 382 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Components | 23 calls |
| Narrative_coherence | 9 calls |

## How to Explore

1. `context({name: "test_engine_validate_narrative_consistency_happy_path"})` — see callers and callees
2. `query({search_query: "narrative"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
