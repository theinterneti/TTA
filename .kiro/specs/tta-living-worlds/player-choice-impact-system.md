# Player Choice Impact System Spec (Focused)

## Purpose
Implements processing of player choices, consequence propagation, preference tracking, and feedback. Provides guidance for world evolution and exposes an integration entry point via WorldStateManager.

## Scope
- Choice ingestion via ChoiceOption and context
- PlayerChoice construction and validation
- ChoiceImpact computation (scope, strength, affected entities)
- ConsequencePropagation across characters, locations, and objects
- Preference tracking (PlayerPreferenceTracker) and influence computation
- Feedback via ChoiceImpactVisualizer
- Integration with WorldStateManager.process_player_choice
- Persistence of evolution_preference_bias for world evolution

## Data Flow
1. UI/backend passes a ChoiceOption + context to WorldStateManager.process_player_choice
2. WSM delegates to PlayerChoiceImpactSystem.process_player_choice
3. System constructs PlayerChoice, validates, computes initial ChoiceImpact
4. NarrativeBranching processes choice; result integrated into impact
5. ConsequencePropagation generates TimelineEvents across affected entities
6. PreferenceTracker updates category preferences and computes influence
7. Visualizer creates feedback summary
8. WSM stores evolution_preference_bias flag based on influence map
9. WSM persists world state

## Integration Contract
- Input: ChoiceOption, context including player_id, world_id, characters_present, current_location, objects_present, etc.
- Output: dict with success, impact summary, feedback, world_evolution_guidance, propagation event ids
- Side effects: Timeline events created; preference tracker updated; evolution_preference_bias set on world state

## Evolution Bias Application
- WorldStateManager._generate_time_period_events reads evolution_preference_bias
- Applies category-weighted multipliers to event generators:
  - Social/emotional/therapeutic -> social interactions
  - Exploration/creative/action -> environmental changes
  - Reflection -> daily life events
- Multiplier function maps [-1..1] bias to [0.5..1.5]

## Validation and Tests
- Unit: PlayerPreference thresholds and update logic; impact scope and strength
- Integration: WSM.process_player_choice creates timeline events; object propagation; bias flag set after repeated choices

## Open Questions / Future Work
- Tagging generated evolution events with content categories for stronger bias verification
- Persisting preference summaries across sessions via persistence layer
- Surfacing feedback visualization to UI layer with consistent schema

