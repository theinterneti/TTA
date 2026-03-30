# Logseq: [[TTA.dev/Scripts/Verify_docker_runtime_setup]]
# ruff: noqa: ALL
#!/usr/bin/env python3
"""
Verify Docker runtime setup for OpenHands integration.

This script verifies:
1. Docker is available
2. Docker runtime configuration is enabled
3. Client can be initialized
4. Configuration is properly loaded from .env
"""

import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


from agent_orchestration.openhands_integration.config import (
    OpenHandsConfig,
    OpenHandsIntegrationConfig,
)
from agent_orchestration.openhands_integration.docker_client import (
    DockerOpenHandsClient,
)


def check_docker_available():
    """Check if Docker is available."""

    try:
        result = subprocess.run(
            ["docker", "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def check_env_configuration():
    """Check .env configuration."""

    env_file = Path(".env")
    if not env_file.exists():
        return False

    with open(env_file) as f:
        content = f.read()

    checks = {
        "OPENHANDS_USE_DOCKER_RUNTIME=true": "Docker runtime enabled" in content
        or "OPENHANDS_USE_DOCKER_RUNTIME=true" in content,
        "OPENHANDS_DOCKER_IMAGE": "OPENHANDS_DOCKER_IMAGE" in content,
        "OPENHANDS_DOCKER_RUNTIME_IMAGE": "OPENHANDS_DOCKER_RUNTIME_IMAGE" in content,
        "OPENHANDS_DOCKER_TIMEOUT": "OPENHANDS_DOCKER_TIMEOUT" in content,
    }

    all_passed = True
    for passed in checks.values():
        all_passed = all_passed and passed

    return all_passed


def check_config_loading():
    """Check if configuration loads correctly."""

    try:
        config = OpenHandsIntegrationConfig.from_env()

        if config.use_docker_runtime:
            return True
        return True
    except Exception:
        import traceback

        traceback.print_exc()
        return False


def check_docker_client_init():
    """Check if Docker client can be initialized."""

    try:
        integration_config = OpenHandsIntegrationConfig.from_env()

        # Convert to OpenHandsConfig
        config = OpenHandsConfig(
            api_key=integration_config.api_key,
            model=integration_config.model_preset,
            base_url=integration_config.base_url,
            workspace_path=integration_config.workspace_root,
        )

        DockerOpenHandsClient(config)

        return True
    except Exception:
        import traceback

        traceback.print_exc()
        return False


def check_execution_engine():
    """Check if execution engine can use Docker runtime."""

    try:
        from agent_orchestration.openhands_integration.execution_engine import (
            ExecutionEngine,
        )

        integration_config = OpenHandsIntegrationConfig.from_env()

        # Create execution engine
        engine = ExecutionEngine(config=integration_config, max_concurrent_tasks=1)

        # Check which client is being used
        client_type = type(engine.client).__name__

        if integration_config.use_docker_runtime:
            return client_type == "DockerOpenHandsClient"
        return client_type == "OptimizedOpenHandsClient"
    except Exception:
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""

    results = {
        "Docker Available": check_docker_available(),
        ".env Configuration": check_env_configuration(),
        "Config Loading": check_config_loading(),
        "Docker Client Init": check_docker_client_init(),
        "Execution Engine": check_execution_engine(),
    }

    for _check_name, _passed in results.items():
        pass

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    if passed_count == total_count:
        return 0
    return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
