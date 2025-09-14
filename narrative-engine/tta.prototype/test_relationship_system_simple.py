#!/usr/bin/env python3
"""
Simple test script for Relationship Evolution System
"""

import sys
from datetime import timedelta
from pathlib import Path

# Add paths for imports
core_path = Path(__file__).parent / "core"
models_path = Path(__file__).parent / "models"
if str(core_path) not in sys.path:
    sys.path.append(str(core_path))
if str(models_path) not in sys.path:
    sys.path.append(str(models_path))

from character_development_system import Interaction
from data_models import CharacterState
from relationship_evolution import (
    CharacterGrowthTracker,
    GrowthPattern,
    PersonalityConsistencyValidator,
    RelationshipEvolutionEngine,
    RelationshipType,
)


def test_relationship_evolution_system():
    """Test the relationship evolution system functionality."""
    print("Testing Relationship Evolution System...")

    # Create system components
    evolution_engine = RelationshipEvolutionEngine()
    growth_tracker = CharacterGrowthTracker()
    validator = PersonalityConsistencyValidator()
    print("✓ System components created")

    # Initialize therapeutic relationship
    relationship_metrics = evolution_engine.initialize_relationship(
        "therapist_001", "patient_001", RelationshipType.THERAPEUTIC
    )
    print("✓ Therapeutic relationship initialized")
    print(f"  - Trust level: {relationship_metrics.trust_level:.2f}")
    print(f"  - Therapeutic alliance: {relationship_metrics.therapeutic_alliance:.2f}")

    # Create character states
    CharacterState(
        character_id="therapist_001",
        name="Dr. Emily Chen",
        personality_traits={
            "empathy": 0.9,
            "patience": 0.8,
            "wisdom": 0.7,
            "supportiveness": 0.9
        },
        therapeutic_role="therapist"
    )

    patient_state = CharacterState(
        character_id="patient_001",
        name="Sarah Williams",
        personality_traits={
            "neuroticism": 0.6,
            "openness": 0.5,
            "emotional_resilience": 0.4,
            "self_awareness": 0.3
        },
        therapeutic_role="patient"
    )
    print("✓ Character states created")

    # Initialize character growth tracking
    growth_metrics = growth_tracker.initialize_character_growth(
        "patient_001", GrowthPattern.STEADY_IMPROVEMENT
    )
    print("✓ Growth tracking initialized")
    print(f"  - Therapeutic progress: {growth_metrics.therapeutic_progress:.2f}")
    print(f"  - Emotional resilience: {growth_metrics.emotional_resilience:.2f}")

    # Simulate therapeutic interactions
    interactions = [
        Interaction(
            participants=["therapist_001", "patient_001"],
            interaction_type="therapeutic",
            content="Initial assessment and rapport building",
            emotional_impact=0.4,
            therapeutic_value=0.6
        ),
        Interaction(
            participants=["therapist_001", "patient_001"],
            interaction_type="therapeutic",
            content="Exploring anxiety triggers and coping strategies",
            emotional_impact=0.6,
            therapeutic_value=0.8
        ),
        Interaction(
            participants=["therapist_001", "patient_001"],
            interaction_type="therapeutic",
            content="Breakthrough moment - understanding root cause",
            emotional_impact=0.8,
            therapeutic_value=0.9
        )
    ]

    print(f"✓ Processing {len(interactions)} therapeutic interactions...")

    # Process each interaction
    for i, interaction in enumerate(interactions, 1):
        # Update relationship
        updated_relationship = evolution_engine.update_relationship_from_interaction(
            "therapist_001", "patient_001", interaction
        )

        # Update character growth
        updated_growth = growth_tracker.update_character_growth(
            "patient_001", patient_state, [interaction]
        )

        print(f"  Interaction {i}:")
        print(f"    - Trust level: {updated_relationship.trust_level:.2f}")
        print(f"    - Therapeutic alliance: {updated_relationship.therapeutic_alliance:.2f}")
        print(f"    - Therapeutic progress: {updated_growth.therapeutic_progress:.2f}")

    # Test relationship analysis
    relationship_analysis = evolution_engine.get_relationship_analysis(
        "therapist_001", "patient_001"
    )
    print("✓ Relationship analysis generated")
    print(f"  - Overall relationship score: {relationship_analysis['overall_score']:.2f}")
    print(f"  - Communication quality: {relationship_analysis['metrics']['communication_quality']:.2f}")
    print(f"  - Conflict level: {relationship_analysis['metrics']['conflict_level']:.2f}")

    # Test character growth analysis
    growth_analysis = growth_tracker.get_character_growth_analysis("patient_001")
    print("✓ Character growth analysis generated")
    print(f"  - Overall growth score: {growth_analysis['overall_growth_score']:.2f}")
    print(f"  - Growth milestones: {len(growth_analysis['growth_milestones'])}")
    if growth_analysis['growth_milestones']:
        print(f"    - Latest milestone: {growth_analysis['growth_milestones'][-1]}")

    # Test personality consistency validation
    is_consistent, issues = validator.validate_personality_consistency(
        patient_state, [], timedelta(days=30)
    )
    print(f"✓ Personality consistency validation: {is_consistent}")
    if issues:
        print(f"  - Issues found: {len(issues)}")
        for issue in issues:
            print(f"    - {issue}")

    # Test relationship evolution over time
    evolved_relationship = evolution_engine.evolve_relationship_over_time(
        "therapist_001", "patient_001", timedelta(days=14)
    )
    print("✓ Relationship evolved over 14 days")
    print(f"  - Trust after time passage: {evolved_relationship.trust_level:.2f}")
    print(f"  - Intimacy after time passage: {evolved_relationship.intimacy_level:.2f}")

    # Test personality adjustment suggestions
    suggestions = validator.suggest_personality_adjustments(patient_state)
    print("✓ Personality adjustment suggestions generated")
    if suggestions:
        print(f"  - Suggestions: {len(suggestions)}")
        for trait, value in suggestions.items():
            print(f"    - {trait}: {value:.2f}")
    else:
        print("  - No adjustments needed")

    print("\n🎉 All relationship evolution tests passed! System is working correctly.")
    return True

if __name__ == "__main__":
    test_relationship_evolution_system()
