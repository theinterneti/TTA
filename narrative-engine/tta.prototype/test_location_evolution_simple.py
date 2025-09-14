#!/usr/bin/env python3
"""
Simple test script for Location Evolution Manager

This script performs basic functionality tests for the LocationEvolutionManager
to verify the implementation works correctly.
"""

import sys
from pathlib import Path

# Add the core and models paths
core_path = Path(__file__).parent / "core"
models_path = Path(__file__).parent / "models"
sys.path.extend([str(core_path), str(models_path)])

try:
    from core.location_evolution_manager import (
        EnvironmentalFactor,
        EnvironmentalFactorType,
        LocationChange,
        LocationEvolutionManager,
        LocationHistory,
        Season,
    )
    from models.living_worlds_models import (
        EntityType,
        EventType,
        Timeline,
        TimelineEvent,
        ValidationError,
    )
    print("✓ Successfully imported LocationEvolutionManager and related classes")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

def test_environmental_factor():
    """Test EnvironmentalFactor class."""
    print("\n--- Testing EnvironmentalFactor ---")

    try:
        # Test creation
        factor = EnvironmentalFactor(
            factor_type=EnvironmentalFactorType.WEATHER,
            current_value="sunny",
            intensity=0.8,
            seasonal_variation=True,
            change_rate=0.2
        )

        # Test validation
        assert factor.validate()
        print("✓ EnvironmentalFactor creation and validation successful")

        # Test serialization
        factor_dict = factor.to_dict()
        restored_factor = EnvironmentalFactor.from_dict(factor_dict)
        assert restored_factor.factor_type == EnvironmentalFactorType.WEATHER
        assert restored_factor.current_value == "sunny"
        print("✓ EnvironmentalFactor serialization successful")

    except Exception as e:
        print(f"✗ EnvironmentalFactor test failed: {e}")
        return False

    return True

def test_location_change():
    """Test LocationChange class."""
    print("\n--- Testing LocationChange ---")

    try:
        # Test creation
        change = LocationChange(
            location_id='test_location',
            change_type='environmental',
            description='Weather changed from sunny to rainy',
            old_state={'weather': 'sunny'},
            new_state={'weather': 'rainy'},
            significance_level=5
        )

        # Test validation
        assert change.validate()
        print("✓ LocationChange creation and validation successful")

        # Test serialization
        change_dict = change.to_dict()
        restored_change = LocationChange.from_dict(change_dict)
        assert restored_change.location_id == 'test_location'
        assert restored_change.change_type == 'environmental'
        print("✓ LocationChange serialization successful")

    except Exception as e:
        print(f"✗ LocationChange test failed: {e}")
        return False

    return True

def test_location_history():
    """Test LocationHistory class."""
    print("\n--- Testing LocationHistory ---")

    try:
        # Test creation
        history = LocationHistory(location_id='test_location')

        # Test validation
        assert history.validate()
        print("✓ LocationHistory creation and validation successful")

        # Test adding events
        event = TimelineEvent(
            event_type=EventType.DISCOVERY,
            title="Ancient artifact found",
            description="A mysterious artifact was discovered",
            significance_level=8
        )

        result = history.add_significant_event(event)
        assert result
        assert len(history.significant_events) == 1
        print("✓ LocationHistory event addition successful")

        # Test adding changes
        change = LocationChange(
            location_id='test_location',
            change_type='environmental',
            description='Seasonal weather change',
            significance_level=5
        )

        result = history.add_environmental_change(change)
        assert result
        assert len(history.environmental_changes) == 1
        print("✓ LocationHistory change addition successful")

    except Exception as e:
        print(f"✗ LocationHistory test failed: {e}")
        return False

    return True

def test_location_evolution_manager():
    """Test LocationEvolutionManager class."""
    print("\n--- Testing LocationEvolutionManager ---")

    try:
        # Test creation
        manager = LocationEvolutionManager()
        print("✓ LocationEvolutionManager creation successful")

        # Test environmental factor initialization
        location_id = 'test_location_001'
        manager._initialize_environmental_factors(location_id, {})

        factors = manager.environmental_factors.get(location_id, {})
        assert len(factors) > 0
        print("✓ Environmental factors initialization successful")

        # Test seasonal change methods
        manager._apply_seasonal_weather(location_id, Season.SPRING)
        # Change might be None if weather was already correct, which is fine
        print("✓ Seasonal weather change method works")

        # Test history generation
        from core.worldbuilding_setting_management import LocationDetails, LocationType
        location_details = LocationDetails(
            location_id=location_id,
            name='Test Garden',
            description='A test garden',
            location_type=LocationType.SAFE_SPACE
        )

        history = manager._generate_location_history(location_details)
        assert history.location_id == location_id
        assert len(history.founding_events) > 0
        print("✓ Location history generation successful")

    except Exception as e:
        print(f"✗ LocationEvolutionManager test failed: {e}")
        return False

    return True

def main():
    """Run all tests."""
    print("Starting Location Evolution Manager Tests")
    print("=" * 50)

    tests = [
        test_environmental_factor,
        test_location_change,
        test_location_history,
        test_location_evolution_manager
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! Location Evolution Manager implementation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
