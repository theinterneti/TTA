#!/usr/bin/env python3
"""
Final Integration Test Runner for TTA Prototype

This script executes the comprehensive final integration and validation
of the therapeutic text adventure system, including all components,
security validation, performance testing, and production readiness assessment.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.final_integration_orchestrator import (
        FinalIntegrationOrchestrator,
        IntegrationStatus,
        SystemValidationManager,
    )
    print("✓ Successfully imported final integration components")
except ImportError as e:
    print(f"✗ Failed to import final integration components: {e}")
    sys.exit(1)


def print_banner():
    """Print the application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    TTA PROTOTYPE FINAL INTEGRATION                           ║
║                   Comprehensive System Validation                           ║
║                                                                              ║
║  This comprehensive integration validates all aspects of the therapeutic     ║
║  text adventure system for production deployment readiness.                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_integration_status(status: IntegrationStatus):
    """Print integration status with appropriate formatting."""
    status_icons = {
        IntegrationStatus.NOT_STARTED: "⏸",
        IntegrationStatus.IN_PROGRESS: "🔄",
        IntegrationStatus.VALIDATION_FAILED: "❌",
        IntegrationStatus.VALIDATION_PASSED: "✅",
        IntegrationStatus.PRODUCTION_READY: "🚀",
        IntegrationStatus.DEPLOYED: "🌟"
    }

    status_colors = {
        IntegrationStatus.NOT_STARTED: "\033[90m",  # Gray
        IntegrationStatus.IN_PROGRESS: "\033[93m",  # Yellow
        IntegrationStatus.VALIDATION_FAILED: "\033[91m",  # Red
        IntegrationStatus.VALIDATION_PASSED: "\033[92m",  # Green
        IntegrationStatus.PRODUCTION_READY: "\033[94m",  # Blue
        IntegrationStatus.DEPLOYED: "\033[95m"  # Magenta
    }

    reset_color = "\033[0m"

    icon = status_icons.get(status, "❓")
    color = status_colors.get(status, "")

    print(f"{color}{icon} Integration Status: {status.value.upper()}{reset_color}")


def print_component_statuses(component_statuses):
    """Print component status summary."""
    print("\n📊 COMPONENT STATUS SUMMARY")
    print("-" * 50)

    for component in component_statuses:
        status_icon = {
            "healthy": "✅",
            "degraded": "⚠️",
            "error": "❌",
            "offline": "⭕"
        }.get(component.status, "❓")

        health_bar = "█" * int(component.health_score * 10) + "░" * (10 - int(component.health_score * 10))

        print(f"  {status_icon} {component.component_name:<20} [{health_bar}] {component.health_score:.2f}")

        if component.error_details:
            print(f"     Error: {component.error_details}")


def print_validation_results(validation_results):
    """Print validation results summary."""
    if "error" in validation_results:
        print(f"\n❌ VALIDATION ERROR: {validation_results['error']}")
        return

    print("\n🔍 VALIDATION RESULTS")
    print("-" * 40)

    overall_status = validation_results.get("overall_status", "UNKNOWN")
    overall_score = validation_results.get("overall_score", 0)

    status_icon = "✅" if overall_status == "PASS" else "⚠️" if overall_status == "WARNING" else "❌"
    print(f"{status_icon} Overall Status: {overall_status}")
    print(f"📈 Overall Score: {overall_score:.2f}/1.0")

    # Summary statistics
    summary = validation_results.get("summary", {})
    if summary:
        print(f"📋 Tests: {summary.get('total_tests', 0)} total, "
              f"{summary.get('passed', 0)} passed, "
              f"{summary.get('warnings', 0)} warnings, "
              f"{summary.get('failed', 0)} failed")
        print(f"📊 Success Rate: {summary.get('success_rate', 0):.1%}")


def print_production_readiness(production_readiness):
    """Print production readiness assessment."""
    if "error" in production_readiness:
        print(f"\n❌ PRODUCTION READINESS ERROR: {production_readiness['error']}")
        return

    print("\n🚀 PRODUCTION READINESS ASSESSMENT")
    print("-" * 45)

    readiness_level = production_readiness.get("overall_readiness_level", "unknown")
    overall_score = production_readiness.get("overall_score", 0)
    critical_issues = production_readiness.get("critical_issues_count", 0)

    readiness_icons = {
        "production": "🚀",
        "staging": "🔧",
        "development": "🛠️",
        "not_ready": "❌"
    }

    icon = readiness_icons.get(readiness_level, "❓")
    print(f"{icon} Readiness Level: {readiness_level.upper()}")
    print(f"📈 Readiness Score: {overall_score:.2f}/1.0")
    print(f"🚨 Critical Issues: {critical_issues}")

    # Security compliance
    security_compliance = production_readiness.get("security_compliance", {})
    if security_compliance:
        security_score = security_compliance.get("overall_security_score", 0)
        security_icon = "🔒" if security_score >= 0.9 else "⚠️" if security_score >= 0.7 else "🔓"
        print(f"{security_icon} Security Score: {security_score:.2f}/1.0")

    # Therapeutic validation
    therapeutic_validation = production_readiness.get("therapeutic_validation", {})
    if therapeutic_validation:
        therapeutic_score = therapeutic_validation.get("overall_therapeutic_effectiveness", 0)
        therapeutic_icon = "🏥" if therapeutic_score >= 0.8 else "⚠️" if therapeutic_score >= 0.6 else "❌"
        print(f"{therapeutic_icon} Therapeutic Effectiveness: {therapeutic_score:.2f}/1.0")


def print_performance_metrics(performance_metrics):
    """Print performance metrics."""
    print("\n⚡ PERFORMANCE METRICS")
    print("-" * 30)

    print(f"📊 Sessions Created: {performance_metrics.get('total_sessions_created', 0)}")
    print(f"💬 Interactions Processed: {performance_metrics.get('total_interactions_processed', 0)}")
    print(f"⏱️ Average Response Time: {performance_metrics.get('average_response_time', 0):.0f}ms")
    print(f"❌ Error Count: {performance_metrics.get('error_count', 0)}")
    print(f"⏰ Uptime: {performance_metrics.get('uptime_percentage', 0):.1f}%")


def print_recommendations(recommendations):
    """Print system recommendations."""
    if not recommendations:
        return

    print("\n💡 RECOMMENDATIONS")
    print("-" * 25)

    for i, recommendation in enumerate(recommendations[:5], 1):  # Show top 5
        print(f"  {i}. {recommendation}")

    if len(recommendations) > 5:
        print(f"  ... and {len(recommendations) - 5} more recommendations")


def save_detailed_report(integration_report, output_file):
    """Save detailed integration report to file."""
    try:
        # Convert dataclass to dictionary for JSON serialization
        report_dict = {
            "integration_status": integration_report.integration_status.value,
            "overall_health_score": integration_report.overall_health_score,
            "component_statuses": [
                {
                    "component_name": cs.component_name,
                    "status": cs.status,
                    "health_score": cs.health_score,
                    "last_check": cs.last_check.isoformat(),
                    "error_details": cs.error_details,
                    "performance_metrics": cs.performance_metrics
                }
                for cs in integration_report.component_statuses
            ],
            "validation_results": integration_report.validation_results,
            "production_readiness": integration_report.production_readiness,
            "performance_metrics": integration_report.performance_metrics,
            "recommendations": integration_report.recommendations,
            "generated_at": integration_report.generated_at.isoformat(),
            "system_uptime": str(integration_report.system_uptime)
        }

        with open(output_file, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)

        print(f"\n📄 Detailed report saved to: {output_file}")

    except Exception as e:
        print(f"⚠️ Could not save detailed report: {e}")


async def run_final_integration(config_file=None, output_file=None, certification_mode=False):
    """Run the final integration process."""
    print_banner()

    # Load configuration
    config = {}
    if config_file and Path(config_file).exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
            print(f"✓ Configuration loaded from {config_file}")
        except Exception as e:
            print(f"⚠️ Could not load configuration: {e}")
            print("   Using default configuration...")

    # Set default configuration values
    default_config = {
        "redis": {
            "host": "localhost",
            "port": 6379,
            "db": 0
        },
        "neo4j": {
            "uri": "bolt://localhost:7687",
            "user": "neo4j",
            "password": "password"
        },
        "validation": {
            "therapeutic_effectiveness_threshold": 0.7,
            "performance_threshold_ms": 2000,
            "error_rate_threshold": 0.05
        }
    }

    # Merge configurations
    for key, value in default_config.items():
        if key not in config:
            config[key] = value

    print(f"🚀 Starting final integration at {datetime.now().isoformat()}")
    print()

    try:
        # Initialize orchestrator
        orchestrator = FinalIntegrationOrchestrator(config)

        # Run final integration
        print("🔄 Executing comprehensive final integration...")
        integration_report = await orchestrator.execute_final_integration()

        print("\n" + "=" * 80)
        print("FINAL INTEGRATION RESULTS")
        print("=" * 80)

        # Print integration status
        print_integration_status(integration_report.integration_status)
        print(f"📈 Overall Health Score: {integration_report.overall_health_score:.2f}/1.0")
        print(f"⏰ System Uptime: {integration_report.system_uptime}")

        # Print component statuses
        print_component_statuses(integration_report.component_statuses)

        # Print validation results
        print_validation_results(integration_report.validation_results)

        # Print production readiness
        print_production_readiness(integration_report.production_readiness)

        # Print performance metrics
        print_performance_metrics(integration_report.performance_metrics)

        # Print recommendations
        print_recommendations(integration_report.recommendations)

        # Save detailed report if requested
        if output_file:
            save_detailed_report(integration_report, output_file)

        # Run certification if requested
        if certification_mode:
            print("\n" + "=" * 80)
            print("SYSTEM CERTIFICATION")
            print("=" * 80)

            validation_manager = SystemValidationManager(orchestrator)
            certification_report = await validation_manager.certify_system_for_production()

            certification_status = certification_report["certification_status"]
            certification_icon = {
                "CERTIFIED_FOR_PRODUCTION": "🏆",
                "CERTIFIED_FOR_STAGING": "🔧",
                "CERTIFIED_FOR_DEVELOPMENT": "🛠️",
                "NOT_CERTIFIED": "❌"
            }.get(certification_status, "❓")

            print(f"{certification_icon} Certification Status: {certification_status}")

            if certification_status == "CERTIFIED_FOR_PRODUCTION":
                print("🎉 System is certified and ready for production deployment!")
            elif certification_status == "CERTIFIED_FOR_STAGING":
                print("⚠️ System is ready for staging environment with some limitations")
            elif certification_status == "CERTIFIED_FOR_DEVELOPMENT":
                print("🛠️ System is suitable for development environment only")
            else:
                print("❌ System is not certified for any deployment")

        # Determine exit code
        if integration_report.integration_status in [IntegrationStatus.PRODUCTION_READY, IntegrationStatus.VALIDATION_PASSED]:
            print("\n✅ FINAL INTEGRATION SUCCESSFUL!")
            return 0
        elif integration_report.integration_status == IntegrationStatus.VALIDATION_FAILED:
            print("\n❌ FINAL INTEGRATION FAILED!")
            print("   System requires significant improvements before deployment")
            return 1
        else:
            print("\n⚠️ FINAL INTEGRATION COMPLETED WITH WARNINGS")
            print("   System may need additional refinement")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️ Integration interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Unexpected error during final integration: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="TTA Prototype Final Integration Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_final_integration.py
  python run_final_integration.py --config config.json --output report.json
  python run_final_integration.py --certify --output certification_report.json
        """
    )

    parser.add_argument(
        "--config", "-c",
        help="Configuration file path (JSON format)",
        type=str
    )

    parser.add_argument(
        "--output", "-o",
        help="Output file for detailed report (JSON format)",
        type=str,
        default=f"final_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    parser.add_argument(
        "--certify",
        help="Run system certification for production",
        action="store_true"
    )

    parser.add_argument(
        "--verbose", "-v",
        help="Enable verbose output",
        action="store_true"
    )

    args = parser.parse_args()

    # Set up logging level
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)

    # Create reports directory
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Ensure output file is in reports directory
    if args.output and not Path(args.output).is_absolute():
        args.output = reports_dir / args.output

    # Run the final integration
    try:
        exit_code = asyncio.run(run_final_integration(
            config_file=args.config,
            output_file=args.output,
            certification_mode=args.certify
        ))
        sys.exit(exit_code)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
