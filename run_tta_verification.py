#!/usr/bin/env python3
"""
TTA Data Flow Verification Runner

This script provides an easy way to run the TTA data flow and context engineering
verification suite with different configurations and options.

Usage:
    python run_tta_verification.py [options]

Options:
    --quick         Run only basic connectivity tests
    --full          Run complete verification suite (default)
    --performance   Focus on performance testing
    --context-only  Test only context engineering
    --output-dir    Directory to save results (default: current directory)
    --verbose       Enable verbose logging
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_tta_data_flow_verification import (
    DatabaseConnectivityTester,
    TTAAgentContextTester,
    TTADataFlowVerificationSuite,
)


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                f"tta_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            ),
        ],
    )


async def run_quick_test():
    """Run quick connectivity tests only"""
    print("🚀 Running Quick Connectivity Tests")
    print("=" * 50)

    db_tester = DatabaseConnectivityTester()

    try:
        connections = await db_tester.initialize_connections()

        results = {
            "test_type": "quick",
            "timestamp": datetime.utcnow().isoformat(),
            "connections": connections,
            "redis_test": {},
            "neo4j_test": {},
        }

        if connections.get("redis"):
            print("📊 Testing Redis operations...")
            results["redis_test"] = await db_tester.test_redis_operations()

        if connections.get("neo4j"):
            print("🗄️ Testing Neo4j operations...")
            results["neo4j_test"] = await db_tester.test_neo4j_operations()

        # Print summary
        print("\n📋 QUICK TEST SUMMARY")
        print("=" * 50)
        print(f"Redis Connected: {'✅' if connections.get('redis') else '❌'}")
        print(f"Neo4j Connected: {'✅' if connections.get('neo4j') else '❌'}")

        if connections.get("redis"):
            redis_success = (
                results["redis_test"]
                .get("basic_operations", {})
                .get("data_integrity", False)
            )
            print(f"Redis Operations: {'✅' if redis_success else '❌'}")

        if connections.get("neo4j"):
            neo4j_success = results["neo4j_test"].get("basic_connectivity", False)
            print(f"Neo4j Operations: {'✅' if neo4j_success else '❌'}")

        return results

    finally:
        await db_tester.cleanup()


async def run_performance_test():
    """Run performance-focused tests"""
    print("🚀 Running Performance Tests")
    print("=" * 50)

    db_tester = DatabaseConnectivityTester()

    try:
        connections = await db_tester.initialize_connections()

        if not all(connections.values()):
            print("❌ Cannot run performance tests without both Redis and Neo4j")
            return None

        # Run multiple iterations for performance analysis
        iterations = 10
        all_metrics = []

        print(f"🔄 Running {iterations} iterations for performance analysis...")

        for i in range(iterations):
            print(f"  Iteration {i + 1}/{iterations}")

            # Redis performance test
            redis_results = await db_tester.test_redis_operations()

            # Neo4j performance test
            neo4j_results = await db_tester.test_neo4j_operations()

            all_metrics.extend(db_tester.metrics)
            db_tester.metrics.clear()  # Clear for next iteration

        # Analyze performance metrics
        operation_times = {}
        for metric in all_metrics:
            if metric.operation not in operation_times:
                operation_times[metric.operation] = []
            if metric.success:
                operation_times[metric.operation].append(metric.duration_ms)

        performance_summary = {}
        for operation, times in operation_times.items():
            if times:
                performance_summary[operation] = {
                    "avg_ms": sum(times) / len(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                    "iterations": len(times),
                }

        print("\n📈 PERFORMANCE SUMMARY")
        print("=" * 50)
        for operation, stats in performance_summary.items():
            print(f"{operation}:")
            print(f"  Average: {stats['avg_ms']:.2f}ms")
            print(f"  Range: {stats['min_ms']:.2f}ms - {stats['max_ms']:.2f}ms")
            print(f"  Iterations: {stats['iterations']}")

        return {
            "test_type": "performance",
            "timestamp": datetime.utcnow().isoformat(),
            "iterations": iterations,
            "performance_summary": performance_summary,
            "total_operations": len(all_metrics),
        }

    finally:
        await db_tester.cleanup()


async def run_context_only_test():
    """Run context engineering tests only"""
    print("🚀 Running Context Engineering Tests")
    print("=" * 50)

    db_tester = DatabaseConnectivityTester()

    try:
        connections = await db_tester.initialize_connections()

        if not all(connections.values()):
            print("❌ Cannot run context tests without both Redis and Neo4j")
            return None

        context_tester = TTAAgentContextTester(
            db_tester.redis_client, db_tester.neo4j_driver
        )

        print("🧠 Testing agent context retrieval...")
        results = await context_tester.test_agent_context_retrieval()

        print("\n🧠 CONTEXT ENGINEERING SUMMARY")
        print("=" * 50)

        for agent_type, agent_results in results.items():
            if isinstance(agent_results, dict):
                success = agent_results.get("context_retrieved", False)
                size = agent_results.get("context_size", 0)
                print(f"{agent_type}: {'✅' if success else '❌'} ({size} bytes)")

                structure = agent_results.get("context_structure", {})
                if structure and not structure.get("error"):
                    print(f"  Keys: {structure.get('total_keys', 0)}")
                    print(
                        f"  Therapeutic: {'✅' if structure.get('has_therapeutic_data') else '❌'}"
                    )
            else:
                print(f"{agent_type}: ❌ Error")

        return {
            "test_type": "context_only",
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
        }

    finally:
        await db_tester.cleanup()


async def run_full_verification():
    """Run the complete verification suite"""
    print("🚀 Running Full Verification Suite")
    print("=" * 50)

    suite = TTADataFlowVerificationSuite()
    return await suite.run_comprehensive_verification()


def save_results(results: dict, output_dir: str):
    """Save results to file"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_type = results.get("test_type", "full")
    filename = f"tta_verification_{test_type}_{timestamp}.json"

    filepath = output_path / filename

    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Results saved to: {filepath}")
    return filepath


def print_final_summary(results: dict):
    """Print final summary based on test type"""
    test_type = results.get("test_type", "full")

    print(f"\n🎯 FINAL SUMMARY - {test_type.upper()} TEST")
    print("=" * 60)

    if test_type == "full":
        success = results.get("overall_success", False)
        print(f"Overall Result: {'✅ PASS' if success else '❌ FAIL'}")

        recommendations = results.get("recommendations", [])
        if recommendations:
            high_priority = [r for r in recommendations if r.get("priority") == "HIGH"]
            medium_priority = [
                r for r in recommendations if r.get("priority") == "MEDIUM"
            ]

            print(f"High Priority Issues: {len(high_priority)}")
            print(f"Medium Priority Issues: {len(medium_priority)}")

            if high_priority:
                print("\n🚨 HIGH PRIORITY ISSUES:")
                for issue in high_priority:
                    print(f"  • {issue['category']}: {issue['issue']}")

    elif test_type in ["quick", "performance", "context_only"]:
        print("Test completed successfully!")

        if test_type == "performance":
            total_ops = results.get("total_operations", 0)
            print(f"Total Operations Tested: {total_ops}")

        elif test_type == "context_only":
            context_results = results.get("results", {})
            successful_agents = sum(
                1
                for r in context_results.values()
                if isinstance(r, dict) and r.get("context_retrieved", False)
            )
            print(
                f"Agents Successfully Tested: {successful_agents}/{len(context_results)}"
            )


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="TTA Data Flow Verification Runner")
    parser.add_argument(
        "--quick", action="store_true", help="Run only basic connectivity tests"
    )
    parser.add_argument(
        "--full", action="store_true", help="Run complete verification suite (default)"
    )
    parser.add_argument(
        "--performance", action="store_true", help="Focus on performance testing"
    )
    parser.add_argument(
        "--context-only", action="store_true", help="Test only context engineering"
    )
    parser.add_argument("--output-dir", default=".", help="Directory to save results")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Determine test type
    if args.quick:
        test_func = run_quick_test
    elif args.performance:
        test_func = run_performance_test
    elif args.context_only:
        test_func = run_context_only_test
    else:
        test_func = run_full_verification

    try:
        # Run the selected test
        results = await test_func()

        if results:
            # Save results
            save_results(results, args.output_dir)

            # Print summary
            print_final_summary(results)
        else:
            print("❌ Test failed to produce results")
            return 1

        return 0

    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.exception("Test execution failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
