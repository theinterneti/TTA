#!/usr/bin/env python3
"""
Generate tests for multiple high-priority modules using OpenHands integration.

This script generates tests for:
1. src/agent_orchestration/protocol_bridge.py (385 lines, 0% coverage)
2. src/agent_orchestration/capability_matcher.py (482 lines, 0% coverage)
3. src/agent_orchestration/circuit_breaker.py (443 lines, 21.79% coverage)

Each module targets 70% coverage threshold.
"""

import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env file before anything else
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=False)
    print(f"✓ Loaded .env from: {env_path}")
else:
    print(f"⚠ .env not found at: {env_path}")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_generation_modules.log'),
    ]
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# Target modules for test generation
TARGET_MODULES = [
    {
        "name": "protocol_bridge",
        "file": "src/agent_orchestration/protocol_bridge.py",
        "lines": 385,
        "coverage": 0,
        "description": "Protocol bridge for translating between orchestration system messages and real agent communication",
    },
    {
        "name": "capability_matcher",
        "file": "src/agent_orchestration/capability_matcher.py",
        "lines": 482,
        "coverage": 0,
        "description": "Capability matching system for agent selection",
    },
    {
        "name": "circuit_breaker",
        "file": "src/agent_orchestration/circuit_breaker.py",
        "lines": 443,
        "coverage": 21.79,
        "description": "Circuit breaker pattern implementation for fault tolerance",
    },
]


async def generate_tests_for_module(module_info: dict) -> bool:
    """Generate tests for a single module."""
    logger.info("=" * 80)
    logger.info(f"Generating tests for: {module_info['name']}")
    logger.info("=" * 80)
    logger.info(f"File: {module_info['file']}")
    logger.info(f"Lines: {module_info['lines']}")
    logger.info(f"Current coverage: {module_info['coverage']}%")
    logger.info(f"Description: {module_info['description']}")
    
    try:
        from agent_orchestration.openhands_integration.config import (
            OpenHandsIntegrationConfig,
        )
        from agent_orchestration.openhands_integration.test_generation_service import (
            UnitTestGenerationService,
        )
        from agent_orchestration.openhands_integration.test_generation_models import (
            TestTaskSpecification,
        )
        
        logger.info("\n[1/3] Creating TestTaskSpecification...")
        spec = TestTaskSpecification(
            target_file=Path(module_info["file"]),
            coverage_threshold=70.0,
            test_framework="pytest",
            test_directory=Path("tests"),
            timeout_seconds=600.0,
        )
        logger.info(f"✓ Specification created for {module_info['name']}")
        
        logger.info("\n[2/3] Initializing UnitTestGenerationService...")
        config = OpenHandsIntegrationConfig.from_env()
        service = UnitTestGenerationService(config)
        logger.info("✓ Service initialized")
        
        logger.info("\n[3/3] Executing test generation...")
        result = await service.generate_tests(spec, max_iterations=3)
        
        logger.info(f"\n✓ Test generation completed for {module_info['name']}")
        logger.info(f"  - Syntax valid: {result.syntax_valid}")
        logger.info(f"  - Tests pass: {result.tests_pass}")
        logger.info(f"  - Coverage: {result.coverage_percentage}%")
        logger.info(f"  - Quality score: {result.quality_score}")
        
        if result.test_file_path:
            logger.info(f"  - Generated file: {result.test_file_path}")
        
        return result.syntax_valid and result.tests_pass
        
    except Exception as e:
        logger.error(f"✗ Test generation failed for {module_info['name']}: {e}", exc_info=True)
        return False


async def main():
    """Generate tests for all target modules."""
    logger.info("\n")
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 78 + "║")
    logger.info("║" + "OpenHands Test Generation - Multiple Modules".center(78) + "║")
    logger.info("║" + " " * 78 + "║")
    logger.info("╚" + "=" * 78 + "╝")
    
    results = {}
    
    for module_info in TARGET_MODULES:
        try:
            success = await generate_tests_for_module(module_info)
            results[module_info["name"]] = success
        except Exception as e:
            logger.error(f"Error processing {module_info['name']}: {e}")
            results[module_info["name"]] = False
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    
    for module_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status}: {module_name}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    logger.info(f"\nTotal: {passed}/{total} modules completed successfully")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

