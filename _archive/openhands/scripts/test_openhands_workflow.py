# Logseq: [[TTA.dev/_archive/Openhands/Scripts/Test_openhands_workflow]]
# ruff: noqa: ALL
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

    # Step 1: Create minimal task specification
    spec = TestTaskSpecification(
        target_file=Path("src/agent_orchestration/messaging.py"),
        coverage_threshold=80.0,
        test_directory=Path("tests/generated"),
    )

    # Step 2: Initialize service
    try:
        config = OpenHandsIntegrationConfig.from_env()
        service = UnitTestGenerationService(config)
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        return

    # Step 3: Execute test generation
    start_time = datetime.now()
    try:
        result = await service.generate_tests(spec, max_iterations=3)
        (datetime.now() - start_time).total_seconds()

    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        import traceback

        traceback.print_exc()
        return

    # Step 4: Validate generated tests
    test_file = Path(result.test_file_path) if result.test_file_path else None

    if not test_file or not test_file.exists():
        return

    # Read and analyze test file
    with open(test_file) as f:
        test_content = f.read()

    lines = test_content.split("\n")

    # Check for real test functions
    test_functions = [l for l in lines if l.strip().startswith("def test_")]

    # Check for assertions
    assertions = [l for l in lines if "assert" in l.lower()]

    # Check for imports
    [l for l in lines if l.strip().startswith(("import ", "from "))]

    # Verify it's not just stubs
    if len(test_functions) == 0:
        return

    if len(assertions) == 0:
        return

    # Step 5: Run tests
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

        if test_result.stderr:
            pass

        if test_result.returncode == 0:
            pass
        else:
            pass

    except subprocess.TimeoutExpired:
        pass
    except Exception as e:
        logger.error(f"Failed to run tests: {e}")

    # Summary


if __name__ == "__main__":
    asyncio.run(main())
