#!/usr/bin/env python3
"""
Test OpenHands integration helpers with real API calls.

This script tests the helper functions with actual OpenRouter API calls
to verify end-to-end functionality.

Usage:
    python scripts/test_openhands_real_api.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.agent_orchestration.openhands_integration.helpers import (
    generate_tests_for_file,
    validate_test_result,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_generate_tests_for_file():
    """Test generate_tests_for_file with real API."""
    logger.info("=" * 80)
    logger.info("TEST 1: generate_tests_for_file with real API")
    logger.info("=" * 80)
    
    # Target file for test generation
    target_file = project_root / "src/agent_orchestration/tools/callable_registry.py"
    
    if not target_file.exists():
        logger.error(f"Target file not found: {target_file}")
        return None
    
    logger.info(f"Target file: {target_file}")
    logger.info(f"Coverage threshold: 70%")
    logger.info(f"Max iterations: 5")
    logger.info("")
    logger.info("Starting test generation (this may take 2-5 minutes)...")
    logger.info("")
    
    try:
        # Generate tests with real API
        result = await generate_tests_for_file(
            file_path=target_file,
            coverage_threshold=70.0,
            max_iterations=5,
        )
        
        logger.info("")
        logger.info("✓ Test generation completed!")
        logger.info("")
        logger.info("Results:")
        logger.info(f"  Syntax valid: {result.syntax_valid}")
        logger.info(f"  Tests pass: {result.tests_pass}")
        logger.info(f"  Coverage: {result.coverage_percentage}%")
        logger.info(f"  Conventions followed: {result.conventions_followed}")
        logger.info(f"  Quality score: {result.quality_score}")
        logger.info(f"  Issues: {len(result.issues)}")
        
        if result.issues:
            logger.info("")
            logger.info("Issues found:")
            for issue in result.issues:
                logger.info(f"  - {issue}")
        
        return result
        
    except Exception as e:
        logger.error(f"✗ Test generation failed: {e}")
        logger.exception("Full traceback:")
        return None


async def test_validate_test_result(result):
    """Test validate_test_result with real result."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 2: validate_test_result with real result")
    logger.info("=" * 80)
    
    if result is None:
        logger.warning("Skipping validation test (no result from previous test)")
        return False
    
    try:
        success, issues = validate_test_result(result, coverage_threshold=70.0)
        
        logger.info("")
        logger.info("Validation results:")
        logger.info(f"  Success: {success}")
        logger.info(f"  Issues: {len(issues)}")
        
        if issues:
            logger.info("")
            logger.info("Validation issues:")
            for issue in issues:
                logger.info(f"  - {issue}")
        
        if success:
            logger.info("")
            logger.info("✓ Validation passed!")
        else:
            logger.info("")
            logger.info("✗ Validation failed")
        
        return success
        
    except Exception as e:
        logger.error(f"✗ Validation test failed: {e}")
        logger.exception("Full traceback:")
        return False


async def verify_ai_context_session():
    """Verify AI context session was created."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 3: Verify AI context session creation")
    logger.info("=" * 80)
    
    sessions_dir = project_root / ".augment/context/sessions"
    
    if not sessions_dir.exists():
        logger.warning(f"Sessions directory not found: {sessions_dir}")
        return False
    
    # Look for recent session files matching pattern: openhands-test-gen-*
    session_files = list(sessions_dir.glob("openhands-test-gen-*.json"))
    
    if not session_files:
        logger.warning("No OpenHands test generation session files found")
        return False
    
    # Get most recent session
    latest_session = max(session_files, key=lambda p: p.stat().st_mtime)
    
    logger.info(f"✓ Found session file: {latest_session.name}")
    logger.info(f"  Size: {latest_session.stat().st_size} bytes")
    logger.info(f"  Modified: {latest_session.stat().st_mtime}")
    
    return True


async def verify_observability_metrics():
    """Verify observability metrics were created."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 4: Verify observability metrics creation")
    logger.info("=" * 80)
    
    metrics_dir = project_root / ".metrics"
    
    if not metrics_dir.exists():
        logger.warning(f"Metrics directory not found: {metrics_dir}")
        return False
    
    # Look for today's metrics file
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    metrics_file = metrics_dir / f"{today}.jsonl"
    
    if not metrics_file.exists():
        logger.warning(f"Today's metrics file not found: {metrics_file}")
        return False
    
    logger.info(f"✓ Found metrics file: {metrics_file.name}")
    logger.info(f"  Size: {metrics_file.stat().st_size} bytes")
    
    # Read and display recent metrics
    try:
        with open(metrics_file, "r") as f:
            lines = f.readlines()
            
        logger.info(f"  Total metrics: {len(lines)}")
        
        # Look for OpenHands-related metrics
        openhands_metrics = [
            line for line in lines 
            if "openhands" in line.lower()
        ]
        
        if openhands_metrics:
            logger.info(f"  OpenHands metrics: {len(openhands_metrics)}")
        
    except Exception as e:
        logger.warning(f"Failed to read metrics file: {e}")
    
    return True


async def main():
    """Run all tests."""
    logger.info("")
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 20 + "OpenHands Real API Testing" + " " * 32 + "║")
    logger.info("╚" + "=" * 78 + "╝")
    logger.info("")
    
    # Test 1: Generate tests with real API
    result = await test_generate_tests_for_file()
    
    # Test 2: Validate result
    validation_success = await test_validate_test_result(result)
    
    # Test 3: Verify AI context session
    session_created = await verify_ai_context_session()
    
    # Test 4: Verify observability metrics
    metrics_created = await verify_observability_metrics()
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"  Test generation: {'✓ PASS' if result else '✗ FAIL'}")
    logger.info(f"  Validation: {'✓ PASS' if validation_success else '✗ FAIL'}")
    logger.info(f"  AI context session: {'✓ CREATED' if session_created else '✗ NOT FOUND'}")
    logger.info(f"  Observability metrics: {'✓ CREATED' if metrics_created else '✗ NOT FOUND'}")
    logger.info("")
    
    # Overall result
    all_passed = result and validation_success
    
    if all_passed:
        logger.info("╔" + "=" * 78 + "╗")
        logger.info("║" + " " * 30 + "ALL TESTS PASSED!" + " " * 30 + "║")
        logger.info("╚" + "=" * 78 + "╝")
        return 0
    else:
        logger.info("╔" + "=" * 78 + "╗")
        logger.info("║" + " " * 30 + "SOME TESTS FAILED" + " " * 30 + "║")
        logger.info("╚" + "=" * 78 + "╝")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

