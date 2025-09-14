#!/usr/bin/env python3
"""
Simple test for Player Choice Impact System

This script performs basic tests to verify the player choice impact system
is working correctly without requiring all dependencies.
"""

import sys
from pathlib import Path

# Add paths for imports
current_dir = Path(__file__).parent
core_path = current_dir / "core"
models_path = current_dir / "models"

sys.path.insert(0, str(core_path))
sys.path.insert(0, str(models_path))

def test_basic_imports():
    """Test basic imports and class creation."""
    print("Testing basic imports...")

    try:
        from player_choice_impact_system import (
            ChoiceCategory,
            ChoiceImpact,
            ImpactScope,
            PlayerChoice,
            PlayerPreference,
            PreferenceStrength,
        )
        print("✓ Basic classes imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_player_choice():
    """Test PlayerChoice functionality."""
    print("\nTesting PlayerChoice...")

    try:
        from player_choice_impact_system import ChoiceCategory, PlayerChoice

        # Create a player choice
        choice = PlayerChoice(
            player_id="test_player",
            world_id="test_world",
            choice_text="Help the injured character",
            choice_category=ChoiceCategory.SOCIAL,
            confidence_level=0.8,
            response_time=5.2
        )

        print("✓ PlayerChoice created successfully")
        print(f"  - Choice ID: {choice.choice_id}")
        print(f"  - Player ID: {choice.player_id}")
        print(f"  - Category: {choice.choice_category.value}")
        print(f"  - Confidence: {choice.confidence_level}")

        # Test validation
        choice.validate()
        print("✓ PlayerChoice validation passed")

        # Test serialization
        choice_dict = choice.to_dict()
        PlayerChoice.from_dict(choice_dict)
        print("✓ PlayerChoice serialization/deserialization works")

        return True

    except Exception as e:
        print(f"✗ PlayerChoice test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_choice_impact():
    """Test ChoiceImpact functionality."""
    print("\nTesting ChoiceImpact...")

    try:
        from player_choice_impact_system import ChoiceImpact, ImpactScope

        # Create a choice impact
        impact = ChoiceImpact(
            choice_id="test_choice_123",
            impact_scope=ImpactScope.LOCAL,
            impact_strength=0.7
        )

        print("✓ ChoiceImpact created successfully")
        print(f"  - Choice ID: {impact.choice_id}")
        print(f"  - Scope: {impact.impact_scope.value}")
        print(f"  - Strength: {impact.impact_strength}")

        # Test adding affected entities
        impact.add_affected_entity("character", "alice")
        impact.add_affected_entity("character", "bob")
        impact.add_affected_entity("location", "garden")

        total_affected = impact.get_total_affected_entities()
        print(f"✓ Added affected entities: {total_affected} total")

        # Test validation
        impact.validate()
        print("✓ ChoiceImpact validation passed")

        return True

    except Exception as e:
        print(f"✗ ChoiceImpact test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_player_preference():
    """Test PlayerPreference functionality."""
    print("\nTesting PlayerPreference...")

    try:
        from player_choice_impact_system import (
            ChoiceCategory,
            PlayerPreference,
            PreferenceStrength,
        )

        # Create a player preference
        preference = PlayerPreference(
            player_id="test_player",
            category=ChoiceCategory.SOCIAL,
            preference_value=0.6,
            strength=PreferenceStrength.MODERATE,
            confidence=0.7,
            evidence_count=5
        )

        print("✓ PlayerPreference created successfully")
        print(f"  - Player ID: {preference.player_id}")
        print(f"  - Category: {preference.category.value}")
        print(f"  - Value: {preference.preference_value}")
        print(f"  - Strength: {preference.strength.value}")

        # Test preference update
        initial_value = preference.preference_value
        preference.update_preference(0.8, weight=1.0)
        print(f"✓ Preference updated: {initial_value:.2f} -> {preference.preference_value:.2f}")

        # Test validation
        preference.validate()
        print("✓ PlayerPreference validation passed")

        return True

    except Exception as e:
        print(f"✗ PlayerPreference test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enums():
    """Test enum definitions."""
    print("\nTesting Enums...")

    try:
        from player_choice_impact_system import (
            ChoiceCategory,
            ImpactScope,
            PreferenceStrength,
        )

        # Test ChoiceCategory
        categories = list(ChoiceCategory)
        print(f"✓ ChoiceCategory has {len(categories)} values: {[c.value for c in categories]}")

        # Test ImpactScope
        scopes = list(ImpactScope)
        print(f"✓ ImpactScope has {len(scopes)} values: {[s.value for s in scopes]}")

        # Test PreferenceStrength
        strengths = list(PreferenceStrength)
        print(f"✓ PreferenceStrength has {len(strengths)} values: {[s.value for s in strengths]}")

        return True

    except Exception as e:
        print(f"✗ Enum test failed: {e}")
        return False

def main():
    """Run all basic tests."""
    print("=" * 60)
    print("Player Choice Impact System - Basic Functionality Test")
    print("=" * 60)

    tests = [
        test_basic_imports,
        test_enums,
        test_player_choice,
        test_choice_impact,
        test_player_preference
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("Test failed!")
        except Exception as e:
            print(f"Test error: {e}")

    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL BASIC TESTS PASSED!")
        print("Player Choice Impact System basic functionality is working correctly.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the errors above.")

    print("=" * 60)

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
