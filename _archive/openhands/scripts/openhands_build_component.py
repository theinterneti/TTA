#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/_archive/Openhands/Scripts/Openhands_build_component]]
Use OpenHands to build a practical component for TTA.

Task: Create a Redis Connection Pool Manager utility
- Manages Redis connection pools with health monitoring
- Provides connection lifecycle management
- Implements circuit breaker pattern for Redis connections
- Includes comprehensive error handling and retry logic
"""

import asyncio
import logging
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from pydantic import SecretStr

from agent_orchestration.openhands_integration import (
    DockerOpenHandsClient,
    OpenHandsConfig,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def build_redis_pool_manager():
    """Use OpenHands to build a Redis Connection Pool Manager."""
    logger.info("=" * 80)
    logger.info("OPENHANDS COMPONENT BUILD: Redis Connection Pool Manager")
    logger.info("=" * 80)

    # Create workspace
    workspace = Path(tempfile.mkdtemp(prefix="openhands_build_"))
    logger.info(f"Workspace: {workspace}")

    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key.startswith("your_"):
        logger.error("OPENROUTER_API_KEY not set properly")
        return None

    # Create config with extended timeout for code generation
    config = OpenHandsConfig(
        api_key=SecretStr(api_key),
        model="openrouter/deepseek/deepseek-chat-v3.1:free",
        workspace_path=workspace,
        timeout_seconds=180,  # 3 minutes for code generation
    )

    # Create client
    client = DockerOpenHandsClient(config)
    logger.info(f"Client initialized: {client.openhands_image}")

    # Define detailed task
    task_description = """
Create a Python module named 'redis_pool_manager.py' with the following requirements:

1. **RedisPoolManager class** that manages Redis connection pools:
   - Initialize with Redis URL and pool configuration (max_connections, timeout)
   - Create and manage connection pool lifecycle
   - Provide get_connection() and release_connection() methods
   - Implement health check for pool status
   - Track pool metrics (active connections, idle connections, total requests)

2. **Circuit Breaker Integration**:
   - Wrap Redis operations with circuit breaker pattern
   - Track failure rates and open circuit on threshold
   - Implement half-open state for recovery testing
   - Provide circuit status monitoring

3. **Error Handling**:
   - Retry logic with exponential backoff for transient failures
   - Connection timeout handling
   - Pool exhaustion handling with waiting queue
   - Graceful degradation when Redis is unavailable

4. **Monitoring & Metrics**:
   - Connection pool statistics (size, active, idle)
   - Operation metrics (success rate, latency, errors)
   - Circuit breaker state tracking
   - Health check endpoint data

5. **Code Quality**:
   - Type hints for all functions
   - Comprehensive docstrings
   - Async/await pattern using redis.asyncio
   - Proper resource cleanup with context managers

6. **Testing**:
   - Create a separate test file 'test_redis_pool_manager.py'
   - Unit tests for pool lifecycle
   - Tests for circuit breaker behavior
   - Tests for error handling and retry logic
   - Mock Redis client for testing

The module should be production-ready and follow TTA's coding standards.
Use redis.asyncio for async Redis operations.
Include proper logging using Python's logging module.

IMPORTANT: Write all code to actual files in the workspace. Create both:
- redis_pool_manager.py (main module)
- test_redis_pool_manager.py (test file)
"""

    logger.info("Task Description:")
    logger.info("-" * 80)
    logger.info(task_description)
    logger.info("-" * 80)

    # Execute task with detailed monitoring
    try:
        logger.info(
            f"\n🚀 Executing OpenHands task (timeout: {config.timeout_seconds}s)..."
        )
        logger.info(f"Start time: {datetime.now().isoformat()}")

        result = await client.execute_task(
            task_description=task_description,
            workspace_path=workspace,
            timeout=config.timeout_seconds,
        )

        logger.info(f"End time: {datetime.now().isoformat()}")
        logger.info(f"\n{'=' * 80}")
        logger.info("EXECUTION RESULTS")
        logger.info("=" * 80)
        logger.info(f"Success: {result.success}")
        logger.info(f"Execution time: {result.execution_time:.2f}s")
        logger.info(f"Output length: {len(result.output)} chars")

        # Log output
        logger.info(f"\n{'=' * 80}")
        logger.info("DOCKER OUTPUT")
        logger.info("=" * 80)
        logger.info(result.output)

        # Check workspace contents
        logger.info(f"\n{'=' * 80}")
        logger.info("WORKSPACE CONTENTS")
        logger.info("=" * 80)

        workspace_files = list(workspace.rglob("*"))
        logger.info(f"Total items in workspace: {len(workspace_files)}")

        for item in sorted(workspace_files):
            if item.is_file():
                size = item.stat().st_size
                logger.info(f"  📄 {item.relative_to(workspace)} ({size} bytes)")
            elif item.is_dir():
                logger.info(f"  📁 {item.relative_to(workspace)}/")

        # Look for generated files
        logger.info(f"\n{'=' * 80}")
        logger.info("GENERATED FILES CHECK")
        logger.info("=" * 80)

        expected_files = ["redis_pool_manager.py", "test_redis_pool_manager.py"]

        found_files = {}
        for expected in expected_files:
            file_path = workspace / expected
            if file_path.exists():
                content = file_path.read_text()
                found_files[expected] = content
                logger.info(
                    f"✅ Found: {expected} ({len(content)} chars, {len(content.splitlines())} lines)"
                )
            else:
                logger.warning(f"❌ Missing: {expected}")

        # If files were generated, show preview
        if found_files:
            logger.info(f"\n{'=' * 80}")
            logger.info("GENERATED CODE PREVIEW")
            logger.info("=" * 80)

            for filename, content in found_files.items():
                logger.info(f"\n--- {filename} (first 50 lines) ---")
                lines = content.splitlines()[:50]
                for i, line in enumerate(lines, 1):
                    logger.info(f"{i:3d} | {line}")
                if len(content.splitlines()) > 50:
                    logger.info(f"... ({len(content.splitlines()) - 50} more lines)")

        return {
            "success": result.success,
            "workspace": workspace,
            "files": found_files,
            "execution_time": result.execution_time,
            "output": result.output,
        }

    except Exception as e:
        logger.error(f"❌ Task execution failed: {e}")
        import traceback

        traceback.print_exc()
        return None
    finally:
        # Don't cleanup yet - we want to inspect the workspace
        logger.info(f"\n⚠️  Workspace preserved at: {workspace}")
        logger.info("   (for manual inspection)")


async def main():
    """Run the component build."""
    logger.info("\n🏗️  Starting OpenHands Component Build\n")

    result = await build_redis_pool_manager()

    if result:
        logger.info("\n" + "=" * 80)
        logger.info("BUILD SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Success: {result['success']}")
        logger.info(f"Execution time: {result['execution_time']:.2f}s")
        logger.info(f"Files generated: {len(result['files'])}")
        logger.info(f"Workspace: {result['workspace']}")

        if result["files"]:
            logger.info("\n✅ Generated files:")
            for filename in result["files"]:
                logger.info(f"   - {filename}")
        else:
            logger.warning("\n⚠️  No files were generated (known issue)")
            logger.info("   This is the documented file generation problem.")
            logger.info(
                "   The Docker container executed but didn't create output files."
            )

        logger.info("=" * 80 + "\n")
        return 0 if result["files"] else 1
    logger.error("\n❌ Build failed\n")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
