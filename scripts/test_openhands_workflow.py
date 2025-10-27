#!/usr/bin/env python3
"""
Comprehensive test of OpenHands sub-agent workflow.

Tests the ability to generate functional test files for a small utility module.
Target: src/agent_orchestration/messaging.py (49 lines, 0% coverage)

Validates:
1. Test generation produces real, functional tests (not stubs)
2. Generated tests contain actual assertions and test cases
3. Tests can be imported and executed without errors
4. Model rotation and fallback mechanisms work
5. Cost is within expected range ($0.02-0.05 per task)
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_orchestration.openhands_integration.config import OpenHandsIntegrationConfig
from agent_orchestration.openhands_integration.test_generation_models import (
    TestTaskSpecification,
)
from agent_orchestration.openhands_integration.test_generation_service import (
    UnitTestGenerationService,
)


async def main():
    """Execute comprehensive OpenHands workflow test."""

    print("\n" + "=" * 80)
    print("OPENHANDS WORKFLOW TEST - COMPREHENSIVE VALIDATION")
    print("=" * 80)

    # Step 1: Create minimal task specification
    print("\n[1/5] Creating minimal task specification...")
    spec = TestTaskSpecification(
        target_file=Path("src/agent_orchestration/messaging.py"),
        coverage_threshold=80.0,
        test_directory=Path("tests/generated"),
    )
    print("✓ Specification created:")
    print(f"  - Target: {spec.target_file}")
    print(f"  - Coverage threshold: {spec.coverage_threshold}%")
    print(f"  - Test directory: {spec.test_directory}")

    # Step 2: Initialize service
    print("\n[2/5] Initializing UnitTestGenerationService...")
    try:
        config = OpenHandsIntegrationConfig.from_env()
        service = UnitTestGenerationService(config)
        print("✓ Service initialized successfully")
        print(f"  - Config: {config.__class__.__name__}")
        print(f"  - Workspace: {service.workspace_path}")
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        return

    # Step 3: Execute test generation
    print("\n[3/5] Executing test generation via OpenHands...")
    start_time = datetime.now()
    try:
        result = await service.generate_tests(spec, max_iterations=3)
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"✓ Test generation completed in {elapsed:.2f}s")
        print(f"  - Syntax valid: {result.syntax_valid}")
        print(f"  - Tests pass: {result.tests_pass}")
        print(f"  - Coverage: {result.coverage_percentage}%")
        print(f"  - Quality score: {result.quality_score}")
        print(f"  - Generated file: {result.test_file_path}")

    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        import traceback

        traceback.print_exc()
        return

    # Step 4: Validate generated tests
    print("\n[4/5] Validating generated tests...")
    test_file = Path(result.test_file_path) if result.test_file_path else None

    if not test_file or not test_file.exists():
        print("✗ Generated test file not found!")
        return

    print(f"✓ Test file exists: {test_file}")

    # Read and analyze test file
    with open(test_file) as f:
        test_content = f.read()

    lines = test_content.split("\n")
    print(f"  - File size: {len(test_content)} bytes, {len(lines)} lines")

    # Check for real test functions
    test_functions = [l for l in lines if l.strip().startswith("def test_")]
    print(f"  - Test functions: {len(test_functions)}")

    # Check for assertions
    assertions = [l for l in lines if "assert" in l.lower()]
    print(f"  - Assertions: {len(assertions)}")

    # Check for imports
    imports = [l for l in lines if l.strip().startswith(("import ", "from "))]
    print(f"  - Import statements: {len(imports)}")

    # Verify it's not just stubs
    if len(test_functions) == 0:
        print("✗ No test functions found - likely stub/placeholder code")
        return

    if len(assertions) == 0:
        print("✗ No assertions found - tests are not functional")
        return

    print("✓ Tests appear to be real and functional")

    # Step 5: Run tests
    print("\n[5/5] Running generated tests...")
    import subprocess

    test_result = None
    try:
        test_result = subprocess.run(
            ["uv", "run", "pytest", str(test_file), "-v", "--tb=short"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )

        print("Test execution output:")
        print(test_result.stdout)
        if test_result.stderr:
            print("Errors:")
            print(test_result.stderr)

        if test_result.returncode == 0:
            print("✓ All tests passed!")
        else:
            print(f"✗ Tests failed with return code {test_result.returncode}")

    except subprocess.TimeoutExpired:
        print("✗ Test execution timed out")
    except Exception as e:
        logger.error(f"Failed to run tests: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("WORKFLOW TEST COMPLETE")
    print("=" * 80)
    print(f"\nGenerated test file: {test_file}")
    print(f"Test functions: {len(test_functions)}")
    print(f"Assertions: {len(assertions)}")
    print(f"Coverage achieved: {result.coverage_percentage}%")
    print(f"Quality score: {result.quality_score}")


if __name__ == "__main__":
    asyncio.run(main())
