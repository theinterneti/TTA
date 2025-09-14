#!/usr/bin/env python3
"""
Direct test script for Location Evolution Manager

This script tests the LocationEvolutionManager implementation directly
without relying on complex import chains.
"""

import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


# Define minimal required classes for testing
class EntityType(Enum):
    CHARACTER = "character"
    LOCATION = "location"
    OBJECT = "object"
    WORLD = "world"


class EventType(Enum):
    DISCOVERY = "discovery"
    SEASONAL_CHANGE = "seasonal_change"
    PLAYER_INTERACTION = "player_interaction"
    ENVIRONMENTAL_CHANGE = "environmental_change"
    CONFLICT = "conflict"
    CELEBRATION = "celebration"
    CREATION = "creation"


class ValidationError(Exception):
    pass


class EnvironmentalFactorType(Enum):
    WEATHER = "weather"
    SEASON = "season"
    TIME_OF_DAY = "time_of_day"
    POPULATION = "population"
    ECONOMY = "economy"


@dataclass
class EnvironmentalFactor:
    factor_type: EnvironmentalFactorType
    current_value: str
    intensity: float = 1.0
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LocationChange:
    change_id: str
    change_type: str
    description: str
    timestamp: datetime
    environmental_factors: list[EnvironmentalFactor] = None

    def __post_init__(self):
        if self.environmental_factors is None:
            self.environmental_factors = []


@dataclass
class LocationHistory:
    location_id: str
    changes: list[LocationChange] = None

    def __post_init__(self):
        if self.changes is None:
            self.changes = []


@dataclass
class TimelineEvent:
    event_id: str = ""
    event_type: EventType = EventType.DISCOVERY
    title: str = ""
    description: str = ""
    participants: list[str] = None
    location_id: str | None = None
    timestamp: datetime = None
    consequences: list[str] = None
    emotional_impact: float = 0.0
    significance_level: int = 5
    tags: list[str] = None
    metadata: dict[str, Any] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.event_id == "":
            self.event_id = str(uuid.uuid4())
        if self.participants is None:
            self.participants = []
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.consequences is None:
            self.consequences = []
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()

    def validate(self) -> bool:
        if not self.event_id.strip():
            raise ValidationError("Event ID cannot be empty")
        if not self.title.strip():
            raise ValidationError("Event title cannot be empty")
        if not self.description.strip():
            raise ValidationError("Event description cannot be empty")
        if not -1.0 <= self.emotional_impact <= 1.0:
            raise ValidationError("Emotional impact must be between -1.0 and 1.0")
        if not 1 <= self.significance_level <= 10:
            raise ValidationError("Significance level must be between 1 and 10")
        return True


# Now test the core classes from location_evolution_manager
def test_environmental_factor():
    """Test EnvironmentalFactor class."""
    print("\n--- Testing EnvironmentalFactor ---")

    try:
        # Import the actual class
        exec(open("core/location_evolution_manager.py").read(), globals())

        # Test creation
        factor = EnvironmentalFactor(
            factor_type=EnvironmentalFactorType.WEATHER,
            current_value="sunny",
            intensity=0.8,
            seasonal_variation=True,
            change_rate=0.2,
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

        return True

    except Exception as e:
        print(f"✗ EnvironmentalFactor test failed: {e}")
        return False


def test_location_change():
    """Test LocationChange class."""
    print("\n--- Testing LocationChange ---")

    try:
        # Import the actual class
        exec(open("core/location_evolution_manager.py").read(), globals())

        # Test creation
        change = LocationChange(
            location_id="test_location",
            change_type="environmental",
            description="Weather changed from sunny to rainy",
            old_state={"weather": "sunny"},
            new_state={"weather": "rainy"},
            significance_level=5,
        )

        # Test validation
        assert change.validate()
        print("✓ LocationChange creation and validation successful")

        # Test serialization
        change_dict = change.to_dict()
        restored_change = LocationChange.from_dict(change_dict)
        assert restored_change.location_id == "test_location"
        assert restored_change.change_type == "environmental"
        print("✓ LocationChange serialization successful")

        return True

    except Exception as e:
        print(f"✗ LocationChange test failed: {e}")
        return False


def test_location_history():
    """Test LocationHistory class."""
    print("\n--- Testing LocationHistory ---")

    try:
        # Import the actual class
        exec(open("core/location_evolution_manager.py").read(), globals())

        # Test creation
        history = LocationHistory(location_id="test_location")

        # Test validation
        assert history.validate()
        print("✓ LocationHistory creation and validation successful")

        # Test adding events
        event = TimelineEvent(
            event_type=EventType.DISCOVERY,
            title="Ancient artifact found",
            description="A mysterious artifact was discovered",
            significance_level=8,
        )

        result = history.add_significant_event(event)
        assert result
        assert len(history.significant_events) == 1
        print("✓ LocationHistory event addition successful")

        # Test adding changes
        change = LocationChange(
            location_id="test_location",
            change_type="environmental",
            description="Seasonal weather change",
            significance_level=5,
        )

        result = history.add_environmental_change(change)
        assert result
        assert len(history.environmental_changes) == 1
        print("✓ LocationHistory change addition successful")

        return True

    except Exception as e:
        print(f"✗ LocationHistory test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Starting Location Evolution Manager Direct Tests")
    print("=" * 60)

    # Check if the file exists
    file_path = "core/location_evolution_manager.py"
    if not os.path.exists(file_path):
        # Try alternative path
        file_path = "../tta.prototype/core/location_evolution_manager.py"
        if not os.path.exists(file_path):
            print("✗ location_evolution_manager.py not found")
            print(f"Current directory: {os.getcwd()}")
            print(f"Looking for: {file_path}")
            return False

    tests = [test_environmental_factor, test_location_change, test_location_history]

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

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print(
            "🎉 All tests passed! Location Evolution Manager core classes are working correctly."
        )
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
