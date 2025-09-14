"""
Simple test for worldbuilding system functionality.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.worldbuilding_setting_management import (
    LocationDetails,
    LocationType,
    WorldbuildingSettingManagement,
    WorldChange,
    WorldChangeType,
    create_sample_location,
)
from models.data_models import NarrativeContext


def test_worldbuilding_system():
    """Test basic worldbuilding system functionality."""
    print("🧪 Testing Worldbuilding and Setting Management System")

    # Create worldbuilding manager
    world_manager = WorldbuildingSettingManagement()
    print("✅ WorldbuildingSettingManagement created successfully")

    # Create sample locations
    garden = create_sample_location("peaceful_garden", "Peaceful Garden", LocationType.THERAPEUTIC_ENVIRONMENT)
    library = create_sample_location("quiet_library", "Quiet Library", LocationType.SAFE_SPACE)
    challenge_area = create_sample_location("challenge_mountain", "Challenge Mountain", LocationType.CHALLENGE_AREA)

    # Test location validation
    try:
        garden.validate()
        library.validate()
        challenge_area.validate()
        print("✅ Location validation successful")
    except Exception as e:
        print(f"❌ Location validation failed: {e}")
        return False

    # Add connections
    garden.connected_locations = {"north": "quiet_library", "east": "challenge_mountain"}
    library.connected_locations = {"south": "peaceful_garden"}
    challenge_area.connected_locations = {"west": "peaceful_garden"}

    # Cache locations
    world_manager.locations_cache[garden.location_id] = garden
    world_manager.locations_cache[library.location_id] = library
    world_manager.locations_cache[challenge_area.location_id] = challenge_area

    print("✅ Test locations created and cached")

    # Test getting location details
    retrieved_garden = world_manager.get_location_details("peaceful_garden")
    if retrieved_garden and retrieved_garden.name == "Peaceful Garden":
        print("✅ Location retrieval successful")
    else:
        print("❌ Location retrieval failed")
        return False

    # Test setting description generation
    context = NarrativeContext(session_id="test_session")
    description = world_manager.generate_setting_description("peaceful_garden", context)
    if description and len(description) > 0:
        print(f"✅ Setting description generated: {description[:100]}...")
    else:
        print("❌ Setting description generation failed")
        return False

    # Test world state changes
    world_change = WorldChange(
        change_type=WorldChangeType.LOCATION_MODIFY,
        target_location_id="peaceful_garden",
        description="Change garden atmosphere to mysterious",
        changes={"atmosphere": "mysterious"}
    )

    try:
        world_change.validate()
        print("✅ World change validation successful")
    except Exception as e:
        print(f"❌ World change validation failed: {e}")
        return False

    # Apply world change
    result = world_manager.update_world_state([world_change])
    if result:
        print("✅ World state update successful")

        # Verify change was applied
        updated_garden = world_manager.get_location_details("peaceful_garden")
        if updated_garden.atmosphere == "mysterious":
            print("✅ World change applied correctly")
        else:
            print("❌ World change not applied correctly")
            return False
    else:
        print("❌ World state update failed")
        return False

    # Test world consistency validation
    validation_result = world_manager.validate_world_consistency()
    if validation_result:
        print("✅ World consistency validation completed")
        print(f"   - Valid: {validation_result.is_valid}")
        print(f"   - Issues: {len(validation_result.issues)}")
        print(f"   - Warnings: {validation_result.warnings_count}")
        print(f"   - Errors: {validation_result.errors_count}")
        print(f"   - Critical: {validation_result.critical_count}")
    else:
        print("❌ World consistency validation failed")
        return False

    # Test location unlocking
    challenge_area.unlock_conditions = ["flag:courage_gained"]
    unlock_change = WorldChange(
        change_type=WorldChangeType.LOCATION_UNLOCK,
        target_location_id="challenge_mountain",
        description="Unlock challenge mountain",
        changes={}
    )

    result = world_manager.update_world_state([unlock_change])
    if result:
        updated_challenge = world_manager.get_location_details("challenge_mountain")
        if len(updated_challenge.unlock_conditions) == 0:
            print("✅ Location unlocking successful")
        else:
            print("❌ Location unlocking failed - conditions not cleared")
            return False
    else:
        print("❌ Location unlocking failed")
        return False

    # Test serialization
    try:
        garden_dict = garden.to_dict()
        restored_garden = LocationDetails.from_dict(garden_dict)
        if restored_garden.location_id == garden.location_id:
            print("✅ Location serialization/deserialization successful")
        else:
            print("❌ Location serialization/deserialization failed")
            return False
    except Exception as e:
        print(f"❌ Location serialization failed: {e}")
        return False

    print("\n🎉 All worldbuilding system tests passed!")
    return True


def test_consistency_rules():
    """Test world consistency validation rules."""
    print("\n🔍 Testing World Consistency Rules")

    world_manager = WorldbuildingSettingManagement()

    # Create locations with potential issues
    safe_location = create_sample_location("safe_area", "Safe Area", LocationType.SAFE_SPACE)
    safe_location.safety_level = 0.9
    safe_location.therapeutic_themes = ["relaxation", "safety"]

    dangerous_location = create_sample_location("danger_zone", "Danger Zone", LocationType.CHALLENGE_AREA)
    dangerous_location.safety_level = 0.1
    dangerous_location.therapeutic_themes = ["high_stress", "risk_taking"]

    # Connect them directly (should trigger safety progression warning)
    safe_location.connected_locations = {"north": "danger_zone"}
    dangerous_location.connected_locations = {"south": "safe_area"}

    # Add isolated location (should trigger connectivity warning)
    isolated_location = create_sample_location("isolated", "Isolated Place", LocationType.EXPLORATION_ZONE)

    # Cache locations
    world_manager.locations_cache[safe_location.location_id] = safe_location
    world_manager.locations_cache[dangerous_location.location_id] = dangerous_location
    world_manager.locations_cache[isolated_location.location_id] = isolated_location

    # Run validation
    validation_result = world_manager.validate_world_consistency()

    print(f"   - Total issues found: {len(validation_result.issues)}")
    print(f"   - Warnings: {validation_result.warnings_count}")
    print(f"   - Errors: {validation_result.errors_count}")

    # Check for expected issues
    connectivity_issues = [issue for issue in validation_result.issues if issue.category == "connectivity"]
    safety_issues = [issue for issue in validation_result.issues if issue.category == "safety_progression"]
    therapeutic_issues = [issue for issue in validation_result.issues if issue.category == "therapeutic_coherence"]

    print(f"   - Connectivity issues: {len(connectivity_issues)}")
    print(f"   - Safety progression issues: {len(safety_issues)}")
    print(f"   - Therapeutic coherence issues: {len(therapeutic_issues)}")

    if len(connectivity_issues) > 0:
        print("✅ Connectivity validation working (found isolated location)")

    if len(safety_issues) > 0:
        print("✅ Safety progression validation working (found large safety gap)")

    if len(therapeutic_issues) > 0:
        print("✅ Therapeutic coherence validation working (found conflicting themes)")

    print("✅ Consistency rules testing completed")


if __name__ == "__main__":
    try:
        success = test_worldbuilding_system()
        if success:
            test_consistency_rules()
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n❌ Some tests failed")
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
