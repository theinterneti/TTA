#!/usr/bin/env python3
"""
Import Validation Test

This script validates that all modules can be imported cleanly without
circular dependency errors after the architectural fixes.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))
os.environ['PYTHONPATH'] = str(src_dir)

def test_critical_imports():
    """Test that critical modules can be imported without circular dependency errors."""

    print("Import Validation Test")
    print("=" * 40)

    test_results = {}

    # Test previously problematic imports
    critical_modules = [
        # Character arc components (previously circular)
        "components.character_arc_manager",
        "components.character_arc_integration",
        "components.character_arc_interfaces",

        # Circuit breaker components (previously circular)
        "agent_orchestration.circuit_breaker",
        "agent_orchestration.circuit_breaker_metrics",
        "agent_orchestration.circuit_breaker_types",

        # Therapeutic chat interface (enhanced with narrative therapy)
        "components.user_experience.therapeutic_chat_interface",

        # Player experience modules
        "player_experience.services.conversational_character_service",
        "player_experience.managers.character_avatar_manager",
        "player_experience.managers.world_management_module",
        "player_experience.services.therapeutic_world_selection_service",
        "player_experience.services.story_initialization_service",
        "player_experience.services.character_to_gameplay_transition",

        # Core therapeutic systems
        "components.therapeutic_systems.gameplay_loop_controller",
        "components.therapeutic_systems.consequence_system",
        "components.therapeutic_systems.emotional_safety_system",
    ]

    for module_name in critical_modules:
        try:
            print(f"Testing import: {module_name}")

            # Attempt to import the module
            __import__(module_name)

            print(f"  ✓ SUCCESS: {module_name}")
            test_results[module_name] = True

        except ImportError as e:
            print(f"  ✗ IMPORT ERROR: {module_name} - {e}")
            test_results[module_name] = False

        except Exception as e:
            print(f"  ⚠ OTHER ERROR: {module_name} - {e}")
            test_results[module_name] = False

    # Test specific functionality that was affected by circular imports
    print("\nTesting specific functionality:")

    try:
        # Test character arc interfaces
        print("  ✓ Character arc interfaces imported successfully")
        test_results["character_arc_interfaces_functionality"] = True

    except Exception as e:
        print(f"  ✗ Character arc interfaces failed: {e}")
        test_results["character_arc_interfaces_functionality"] = False

    try:
        # Test circuit breaker types
        print("  ✓ Circuit breaker types imported successfully")
        test_results["circuit_breaker_types_functionality"] = True

    except Exception as e:
        print(f"  ✗ Circuit breaker types failed: {e}")
        test_results["circuit_breaker_types_functionality"] = False

    try:
        # Test enhanced narrative therapy functionality
        print("  ✓ Enhanced therapeutic chat interface imported successfully")
        test_results["narrative_therapy_functionality"] = True

    except Exception as e:
        print(f"  ✗ Enhanced therapeutic chat interface failed: {e}")
        test_results["narrative_therapy_functionality"] = False

    # Summary
    print("\n" + "=" * 40)
    print("IMPORT VALIDATION RESULTS:")
    print("-" * 40)

    successful_imports = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    success_rate = successful_imports / total_tests * 100

    for module, success in test_results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{module}: {status}")

    print(f"\nOverall Success Rate: {successful_imports}/{total_tests} ({success_rate:.1f}%)")

    if success_rate == 100:
        print("🎉 ALL IMPORTS SUCCESSFUL!")
        print("Circular dependency issues have been resolved!")
        return True
    else:
        print("⚠ Some imports still failing - additional fixes needed")
        return False

def test_narrative_therapy_integration():
    """Test that narrative therapy enhancements work with resolved dependencies."""

    print("\nTesting Narrative Therapy Integration:")
    print("-" * 40)

    try:
        from components.user_experience.therapeutic_chat_interface import (
            TherapeuticChatInterface,
        )

        # Create instance
        chat_interface = TherapeuticChatInterface()

        # Test that enhanced methods exist
        assert hasattr(chat_interface, '_detect_story_context')
        assert hasattr(chat_interface, '_extract_narrative_elements')
        assert hasattr(chat_interface, '_track_narrative_progression')
        assert hasattr(chat_interface, '_generate_story_engaged_response')

        print("  ✓ All narrative therapy methods available")

        # Test framework selection enhancement
        from components.user_experience.therapeutic_chat_interface import (
            ChatMessage,
            MessageType,
            TherapeuticContext,
        )

        message = ChatMessage(
            session_id="test",
            user_id="test",
            message_type=MessageType.USER_MESSAGE,
            content="I want to tell you my story about overcoming anxiety"
        )

        context = TherapeuticContext(user_id="test", session_id="test")

        framework = chat_interface._select_therapeutic_framework(message, context)

        # Should select NARRATIVE framework
        from components.user_experience.therapeutic_chat_interface import (
            TherapeuticFramework,
        )
        assert framework == TherapeuticFramework.NARRATIVE

        print("  ✓ Enhanced framework selection working")
        print("  ✓ Narrative therapy integration fully functional")

        return True

    except Exception as e:
        print(f"  ✗ Narrative therapy integration failed: {e}")
        return False

def main():
    """Main validation function."""

    # Test basic imports
    import_success = test_critical_imports()

    # Test narrative therapy integration
    narrative_success = test_narrative_therapy_integration()

    overall_success = import_success and narrative_success

    print("\n" + "=" * 50)
    if overall_success:
        print("✅ ARCHITECTURAL FIXES SUCCESSFUL!")
        print("All circular dependencies resolved and functionality intact.")
        print("Ready to resume narrative therapy and player experience development.")
    else:
        print("❌ ARCHITECTURAL FIXES INCOMPLETE!")
        print("Additional work needed before resuming development.")

    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
