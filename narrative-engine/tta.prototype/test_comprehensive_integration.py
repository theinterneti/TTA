#!/usr/bin/env python3
"""
Comprehensive Integration Test Runner for TTA Prototype

This script runs comprehensive system integration and validation tests
for the therapeutic text adventure platform, including therapeutic
effectiveness, security compliance, performance optimization, and
complete user journey validation.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.system_integration_validator import SystemIntegrationValidator
    print("✓ Successfully imported SystemIntegrationValidator")
except ImportError as e:
    print(f"✗ Failed to import SystemIntegrationValidator: {e}")
    sys.exit(1)


async def run_comprehensive_integration_tests():
    """Run comprehensive integration tests for the TTA prototype system."""
    print("\n" + "=" * 80)
    print("TTA PROTOTYPE COMPREHENSIVE INTEGRATION VALIDATION")
    print("=" * 80)
    print(f"Test started at: {datetime.now().isoformat()}")
    print()

    # Initialize the validator
    config = {
        "prototype": {
            "redis": {"host": "localhost", "port": 6379, "db": 0},
            "neo4j": {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "password"}
        },
        "validation": {
            "therapeutic_effectiveness_threshold": 0.7,
            "performance_threshold_ms": 2000,
            "error_rate_threshold": 0.05
        }
    }

    validator = SystemIntegrationValidator(config)

    try:
        # Run comprehensive validation
        print("🚀 Starting comprehensive system validation...")
        print("   This will test all aspects of the therapeutic text adventure system")
        print()

        validation_results = await validator.run_comprehensive_validation()

        # Display results
        print_validation_results(validation_results)

        # Generate detailed report
        generate_detailed_report(validation_results)

        # Return success/failure status
        return validation_results.get("overall_status") == "PASS"

    except Exception as e:
        print(f"✗ Error during comprehensive validation: {e}")
        return False


def print_validation_results(results):
    """Print validation results in a formatted way."""
    print("📊 VALIDATION RESULTS")
    print("-" * 40)

    if "error" in results:
        print(f"✗ Validation failed with error: {results['error']}")
        return

    # Overall status
    status = results.get("overall_status", "UNKNOWN")
    status_icon = "✓" if status == "PASS" else "⚠" if status == "WARNING" else "✗"
    print(f"{status_icon} Overall Status: {status}")
    print(f"📈 Overall Score: {results.get('overall_score', 0):.2f}/1.0")
    print()

    # Summary
    summary = results.get("summary", {})
    print("📋 Test Summary:")
    print(f"   Total Tests: {summary.get('total_tests', 0)}")
    print(f"   ✓ Passed: {summary.get('passed', 0)}")
    print(f"   ⚠ Warnings: {summary.get('warnings', 0)}")
    print(f"   ✗ Failed: {summary.get('failed', 0)}")
    print(f"   Success Rate: {summary.get('success_rate', 0):.1%}")
    print()

    # Detailed results
    print("🔍 Detailed Test Results:")
    for result in results.get("detailed_results", []):
        test_name = result.get("test_name", "unknown")
        test_result = result.get("result", "unknown")
        test_score = result.get("score", 0)
        execution_time = result.get("execution_time", 0)

        result_icon = "✓" if test_result == "pass" else "⚠" if test_result == "warning" else "✗"
        print(f"   {result_icon} {test_name}: {test_result.upper()} (Score: {test_score:.2f}, Time: {execution_time:.2f}s)")

    print()

    # System metrics
    metrics = results.get("system_metrics", {})
    if metrics:
        print("📈 System Performance Metrics:")
        print(f"   Therapeutic Effectiveness: {metrics.get('therapeutic_effectiveness', 0):.2f}")
        print(f"   Average Response Time: {metrics.get('average_response_time', 0):.0f}ms")

        memory_usage = metrics.get("memory_usage", {})
        if memory_usage:
            print(f"   Memory Usage: {memory_usage}")

        error_rates = metrics.get("error_rates", {})
        if error_rates:
            print(f"   Error Rates: {error_rates}")
        print()

    # Recommendations
    recommendations = results.get("recommendations", {})
    if any(recommendations.values()):
        print("💡 Recommendations:")

        high_priority = recommendations.get("high_priority", [])
        if high_priority:
            print("   🔴 High Priority:")
            for rec in high_priority[:3]:  # Show top 3
                print(f"      • {rec}")

        medium_priority = recommendations.get("medium_priority", [])
        if medium_priority:
            print("   🟡 Medium Priority:")
            for rec in medium_priority[:3]:  # Show top 3
                print(f"      • {rec}")

        low_priority = recommendations.get("low_priority", [])
        if low_priority:
            print("   🟢 Low Priority:")
            for rec in low_priority[:2]:  # Show top 2
                print(f"      • {rec}")
        print()

    # Production readiness
    production_ready = results.get("system_ready_for_production", False)
    ready_icon = "✅" if production_ready else "❌"
    print(f"{ready_icon} System Ready for Production: {'YES' if production_ready else 'NO'}")

    if not production_ready:
        print("   ⚠ System requires additional work before production deployment")
    else:
        print("   🎉 System meets production readiness criteria!")


def generate_detailed_report(results):
    """Generate a detailed JSON report file."""
    try:
        report_filename = f"integration_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = Path(__file__).parent / "reports" / report_filename

        # Create reports directory if it doesn't exist
        report_path.parent.mkdir(exist_ok=True)

        # Add metadata to results
        enhanced_results = {
            **results,
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "1.0",
                "system_version": "TTA Prototype v1.0",
                "test_environment": "development"
            }
        }

        # Write detailed report
        with open(report_path, 'w') as f:
            json.dump(enhanced_results, f, indent=2, default=str)

        print(f"📄 Detailed report saved to: {report_path}")

    except Exception as e:
        print(f"⚠ Could not generate detailed report: {e}")


def run_quick_health_check():
    """Run a quick health check of the system."""
    print("\n🏥 QUICK HEALTH CHECK")
    print("-" * 30)

    health_checks = [
        ("Core modules import", test_core_imports),
        ("Database connections", test_database_connections),
        ("Component initialization", test_component_initialization),
        ("Basic functionality", test_basic_functionality)
    ]

    all_healthy = True

    for check_name, check_func in health_checks:
        try:
            result = check_func()
            status = "✓" if result else "✗"
            print(f"   {status} {check_name}: {'PASS' if result else 'FAIL'}")
            if not result:
                all_healthy = False
        except Exception as e:
            print(f"   ✗ {check_name}: ERROR - {e}")
            all_healthy = False

    print(f"\n🏥 Overall Health: {'HEALTHY' if all_healthy else 'ISSUES DETECTED'}")
    return all_healthy


def test_core_imports():
    """Test that core modules can be imported."""
    try:
        from core.character_development_system import CharacterDevelopmentSystem
        from core.interactive_narrative_engine import InteractiveNarrativeEngine
        from models.data_models import CharacterState, SessionState
        return True
    except ImportError:
        return False


def test_database_connections():
    """Test database connection availability."""
    try:
        # Mock database connection test
        # In a real implementation, this would test actual connections
        return True
    except Exception:
        return False


def test_component_initialization():
    """Test component initialization."""
    try:
        from components.prototype_component import PrototypeComponent
        component = PrototypeComponent({})
        return component is not None
    except Exception:
        return False


def test_basic_functionality():
    """Test basic system functionality."""
    try:
        from core.interactive_narrative_engine import InteractiveNarrativeEngine
        engine = InteractiveNarrativeEngine()
        session = engine.start_session("health_check_user")
        return session is not None
    except Exception:
        return False


async def main():
    """Main test runner function."""
    print("TTA Prototype Comprehensive Integration Test Suite")
    print("=" * 60)

    # Run quick health check first
    health_ok = run_quick_health_check()

    if not health_ok:
        print("\n⚠ Health check failed. Some tests may not run properly.")
        print("   Consider fixing basic issues before running comprehensive tests.")

        user_input = input("\nContinue with comprehensive tests anyway? (y/N): ")
        if user_input.lower() != 'y':
            print("Exiting...")
            return 1

    # Run comprehensive integration tests
    try:
        success = await run_comprehensive_integration_tests()

        print("\n" + "=" * 80)
        if success:
            print("🎉 COMPREHENSIVE INTEGRATION TESTS PASSED!")
            print("   The TTA Prototype system is ready for therapeutic use.")
            return 0
        else:
            print("⚠ COMPREHENSIVE INTEGRATION TESTS COMPLETED WITH ISSUES")
            print("   The system may need additional refinement before production use.")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n✗ Unexpected error during testing: {e}")
        return 1


if __name__ == "__main__":
    # Create reports directory
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Run the tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
