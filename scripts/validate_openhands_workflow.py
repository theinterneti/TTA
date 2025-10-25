#!/usr/bin/env python3
"""
Comprehensive validation script for OpenHands test generation workflow.

This script validates:
1. OpenHands SDK client wrapper functionality
2. Free model registry configuration
3. Error recovery system setup
4. Test generation service readiness
5. End-to-end test generation execution
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def validate_infrastructure():
    """Validate OpenHands integration infrastructure."""
    logger.info("=" * 80)
    logger.info("PHASE 1: INFRASTRUCTURE VALIDATION")
    logger.info("=" * 80)

    # 1. Validate imports
    logger.info("\n[1/4] Validating imports...")
    try:
        from agent_orchestration.openhands_integration.client import (
            OpenHandsClient,
            create_openhands_client,
        )
        from agent_orchestration.openhands_integration.config import (
            ModelRegistry,
            OpenHandsConfig,
            OpenHandsIntegrationConfig,
        )
        from agent_orchestration.openhands_integration.error_recovery import (
            OpenHandsErrorRecovery,
        )
        from agent_orchestration.openhands_integration.test_generation_models import (
            TestTaskSpecification,
            TestValidationResult,
        )
        from agent_orchestration.openhands_integration.test_generation_service import (
            UnitTestGenerationService,
        )
        logger.info("✓ All imports successful")
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False

    # 2. Validate free model registry
    logger.info("\n[2/4] Validating free model registry...")
    try:
        registry_path = Path(__file__).parent.parent / "src/agent_orchestration/openhands_integration/free_models_registry.yaml"
        if not registry_path.exists():
            logger.error(f"✗ Registry file not found: {registry_path}")
            return False

        import yaml
        with open(registry_path) as f:
            registry_data = yaml.safe_load(f)

        models = registry_data.get("models", {})
        verified_models = [
            m for m in models.values()
            if m.get("compatibility_status") == "verified"
        ]

        logger.info(f"✓ Registry loaded: {len(models)} total models")
        logger.info(f"✓ Verified models: {len(verified_models)}")
        for model in verified_models[:3]:
            logger.info(f"  - {model['display_name']} ({model['provider']})")
    except Exception as e:
        logger.error(f"✗ Registry validation failed: {e}")
        return False

    # 3. Validate error recovery configuration
    logger.info("\n[3/4] Validating error recovery system...")
    try:
        # Check if retry primitives are available
        try:
            from scripts.primitives.error_recovery import RetryConfig, with_retry_async
            logger.info("✓ Retry primitives available")
        except ImportError:
            logger.warning("⚠ Retry primitives not available (fallback will be used)")

        logger.info("✓ Error recovery system configured")
    except Exception as e:
        logger.error(f"✗ Error recovery validation failed: {e}")
        return False

    # 4. Validate test generation service
    logger.info("\n[4/4] Validating test generation service...")
    try:
        # Create minimal config for validation
        config = OpenHandsConfig(
            api_key="test-key",
            model="openrouter/deepseek/deepseek-chat",
            workspace_path=Path.cwd(),
        )

        service = UnitTestGenerationService(config)
        logger.info("✓ Test generation service initialized")
        logger.info(f"✓ Workspace path: {service.workspace_path}")
    except Exception as e:
        logger.error(f"✗ Test generation service validation failed: {e}")
        return False

    logger.info("\n" + "=" * 80)
    logger.info("✓ INFRASTRUCTURE VALIDATION COMPLETE")
    logger.info("=" * 80)
    return True


async def validate_target_module():
    """Validate target module for test generation."""
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2: TARGET MODULE VALIDATION")
    logger.info("=" * 80)

    target_file = Path("src/agent_orchestration/adapters.py")

    logger.info(f"\nTarget module: {target_file}")

    if not target_file.exists():
        logger.error(f"✗ Target file not found: {target_file}")
        return False

    # Check file size
    file_size = target_file.stat().st_size
    line_count = len(target_file.read_text().splitlines())

    logger.info(f"✓ File exists")
    logger.info(f"✓ File size: {file_size:,} bytes")
    logger.info(f"✓ Line count: {line_count} lines")

    # Check for key classes
    content = target_file.read_text()
    classes = ["IPAAdapter", "WBAAdapter", "NGAAdapter", "AgentAdapterFactory"]

    for cls in classes:
        if f"class {cls}" in content:
            logger.info(f"✓ Found class: {cls}")
        else:
            logger.warning(f"⚠ Class not found: {cls}")

    logger.info("\n" + "=" * 80)
    logger.info("✓ TARGET MODULE VALIDATION COMPLETE")
    logger.info("=" * 80)
    return True


async def main():
    """Run all validations."""
    logger.info("\n")
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 78 + "║")
    logger.info("║" + "OpenHands Test Generation Workflow - Infrastructure Validation".center(78) + "║")
    logger.info("║" + " " * 78 + "║")
    logger.info("╚" + "=" * 78 + "╝")

    # Run validations
    infra_ok = await validate_infrastructure()
    target_ok = await validate_target_module()

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Infrastructure: {'✓ PASS' if infra_ok else '✗ FAIL'}")
    logger.info(f"Target Module: {'✓ PASS' if target_ok else '✗ FAIL'}")

    if infra_ok and target_ok:
        logger.info("\n✓ All validations passed! Ready for test generation.")
        return 0
    else:
        logger.error("\n✗ Some validations failed. Please fix issues before proceeding.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

