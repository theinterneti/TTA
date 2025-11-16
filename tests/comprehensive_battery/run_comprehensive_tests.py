#!/usr/bin/env python3
"""
Comprehensive Test Battery Execution Script

Main entry point for running the comprehensive test battery for the TTA storytelling system.
Provides command-line interface for test execution with various options and configurations.
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.comprehensive_battery.comprehensive_test_battery import (
    ComprehensiveTestBattery,
)
from tests.comprehensive_battery.utils.metrics_collector import TestMetricsCollector
from tests.comprehensive_battery.utils.report_generator import TestReportGenerator


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup logging configuration."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()), format=log_format, handlers=handlers
    )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive test battery for TTA storytelling system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all test categories
  python run_comprehensive_tests.py --all

  # Run specific categories
  python run_comprehensive_tests.py --categories standard adversarial

  # Run with custom configuration
  python run_comprehensive_tests.py --all --config custom_config.yaml

  # Run with detailed reporting
  python run_comprehensive_tests.py --all --detailed-report --metrics

  # Run with specific concurrency
  python run_comprehensive_tests.py --all --max-concurrent 10
        """,
    )

    # Test selection options
    test_group = parser.add_mutually_exclusive_group(required=True)
    test_group.add_argument(
        "--all", action="store_true", help="Run all test categories"
    )
    test_group.add_argument(
        "--categories",
        nargs="+",
        choices=[
            "standard",
            "adversarial",
            "load_stress",
            "data_pipeline",
            "dashboard",
        ],
        help="Specific test categories to run",
    )

    # Configuration options
    parser.add_argument(
        "--config",
        type=str,
        default="tests/comprehensive_battery/config/comprehensive_test_config.yaml",
        help="Path to configuration file (default: tests/comprehensive_battery/config/comprehensive_test_config.yaml)",
    )

    # Execution options
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum concurrent tests (default: 5)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Test timeout in seconds (default: 300)",
    )

    # Reporting options
    parser.add_argument(
        "--detailed-report",
        action="store_true",
        help="Generate detailed HTML and CSV reports",
    )
    parser.add_argument(
        "--metrics", action="store_true", help="Collect system metrics during testing"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./testing/results/comprehensive_battery",
        help="Output directory for reports (default: ./testing/results/comprehensive_battery)",
    )

    # Logging options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--log-file", type=str, help="Log file path (default: stdout only)"
    )

    # Database options
    parser.add_argument("--neo4j-uri", type=str, help="Neo4j URI override")
    parser.add_argument("--redis-url", type=str, help="Redis URL override")

    # Dry run option
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without running tests",
    )

    # Mock mode option
    parser.add_argument(
        "--force-mock",
        action="store_true",
        help="Force mock mode even if real services are available",
    )

    return parser.parse_args()


async def main():
    """Main execution function."""
    args = parse_arguments()

    # Setup logging
    log_file = args.log_file
    if log_file:
        # Ensure log directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    setup_logging(args.log_level, log_file)
    logger = logging.getLogger(__name__)

    logger.info("Starting TTA Comprehensive Test Battery")
    logger.info(f"Arguments: {vars(args)}")

    # Initialize variables
    metrics_collector = None

    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            return 1

        # Initialize metrics collector if requested
        metrics_collector = None
        if args.metrics:
            metrics_collector = TestMetricsCollector()
            await metrics_collector.start_collection()
            logger.info("Metrics collection started")

        # Initialize test battery
        test_battery = ComprehensiveTestBattery(
            config_path=str(config_path),
            max_concurrent_tests=args.max_concurrent,
            test_timeout_seconds=args.timeout,
            neo4j_uri_override=args.neo4j_uri,
            redis_url_override=args.redis_url,
            force_mock_mode=args.force_mock,
        )

        # Determine which categories to run
        if args.all:
            categories = [
                "standard",
                "adversarial",
                "load_stress",
                "data_pipeline",
                "dashboard",
            ]
        else:
            categories = args.categories

        logger.info(f"Test categories to execute: {categories}")

        # Dry run check
        if args.dry_run:
            logger.info("DRY RUN MODE - Tests would be executed but not actually run")
            logger.info(f"Categories: {categories}")
            logger.info(f"Max concurrent: {args.max_concurrent}")
            logger.info(f"Timeout: {args.timeout}s")
            logger.info(f"Output directory: {args.output_dir}")
            return 0

        # Initialize test battery
        logger.info("Initializing test battery...")
        initialization_success = await test_battery.initialize()
        if not initialization_success:
            logger.error("Failed to initialize test battery")
            return 1

        # Execute tests
        start_time = datetime.utcnow()
        logger.info(f"Test execution started at {start_time}")

        # Run selected test categories
        results = []

        if "standard" in categories:
            logger.info("Executing standard test suite...")
            standard_results = await test_battery.run_standard_tests()
            results.extend(standard_results)

        if "adversarial" in categories:
            logger.info("Executing adversarial test suite...")
            adversarial_results = await test_battery.run_adversarial_tests()
            results.extend(adversarial_results)

        if "load_stress" in categories:
            logger.info("Executing load/stress test suite...")
            load_results = await test_battery.run_load_stress_tests()
            results.extend(load_results)

        if "data_pipeline" in categories:
            logger.info("Executing data pipeline validation...")
            pipeline_results = await test_battery.run_data_pipeline_validation()
            results.extend(pipeline_results)

        if "dashboard" in categories:
            logger.info("Executing dashboard verification...")
            dashboard_results = await test_battery.run_dashboard_verification()
            results.extend(dashboard_results)

        end_time = datetime.utcnow()
        logger.info(f"Test execution completed at {end_time}")

        # Stop metrics collection
        metrics_data = None
        if metrics_collector:
            await metrics_collector.stop_collection()
            metrics_data = metrics_collector.get_comprehensive_report()
            logger.info("Metrics collection stopped")

        # Generate reports
        if args.detailed_report or args.metrics:
            logger.info("Generating comprehensive reports...")

            report_generator = TestReportGenerator(args.output_dir)
            report_result = await report_generator.generate_comprehensive_report(
                results=results,
                start_time=start_time,
                end_time=end_time,
                config=test_battery.config,
                metrics_data=metrics_data,
            )

            if report_result["report_generated"]:
                logger.info(f"Reports generated in: {report_result['report_path']}")
                for format_type, file_path in report_result["report_files"].items():
                    logger.info(f"  {format_type.upper()}: {file_path}")
            else:
                logger.error(f"Report generation failed: {report_result.get('error')}")

        # Print summary
        total_tests = len(results)
        passed_tests = len([r for r in results if r.passed])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        if failed_tests > 0:
            for result in results:
                if not result.passed:
                    pass

        # Return appropriate exit code
        return 0 if failed_tests == 0 else 1

    except KeyboardInterrupt:
        logger.info("Test execution interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Test execution failed: {e}", exc_info=True)
        return 1
    finally:
        # Cleanup
        if "test_battery" in locals():
            await test_battery.cleanup()
        if metrics_collector:
            await metrics_collector.stop_collection()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
