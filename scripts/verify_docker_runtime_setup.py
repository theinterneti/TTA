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
    print("\n" + "=" * 80)
    print("✓ STEP 1: Verify Docker is Available")
    print("=" * 80)

    try:
        result = subprocess.run(
            ["docker", "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            print(f"✅ Docker available: {result.stdout.strip()}")
            return True
        print(f"❌ Docker error: {result.stderr}")
        return False
    except Exception as e:
        print(f"❌ Docker not available: {e}")
        return False


def check_env_configuration():
    """Check .env configuration."""
    print("\n" + "=" * 80)
    print("✓ STEP 2: Verify .env Configuration")
    print("=" * 80)

    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
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
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        all_passed = all_passed and passed

    return all_passed


def check_config_loading():
    """Check if configuration loads correctly."""
    print("\n" + "=" * 80)
    print("✓ STEP 3: Verify Configuration Loading")
    print("=" * 80)

    try:
        config = OpenHandsIntegrationConfig.from_env()

        print("✅ Configuration loaded successfully")
        print(f"   Model preset: {config.model_preset}")
        print(f"   Base URL: {config.base_url}")
        print(f"   Workspace root: {config.workspace_root}")
        print(f"   Docker runtime enabled: {config.use_docker_runtime}")
        print(f"   Docker image: {config.docker_image}")
        print(f"   Docker runtime image: {config.docker_runtime_image}")
        print(f"   Docker timeout: {config.docker_timeout}s")

        if config.use_docker_runtime:
            print("\n✅ Docker runtime is ENABLED in configuration")
            return True
        print("\n⚠️  Docker runtime is DISABLED in configuration")
        print(
            "   (This is expected if OPENHANDS_USE_DOCKER_RUNTIME is not set to 'true')"
        )
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_docker_client_init():
    """Check if Docker client can be initialized."""
    print("\n" + "=" * 80)
    print("✓ STEP 4: Verify Docker Client Initialization")
    print("=" * 80)

    try:
        integration_config = OpenHandsIntegrationConfig.from_env()

        # Convert to OpenHandsConfig
        config = OpenHandsConfig(
            api_key=integration_config.api_key,
            model=integration_config.model_preset,
            base_url=integration_config.base_url,
            workspace_path=integration_config.workspace_root,
        )

        client = DockerOpenHandsClient(config)

        print("✅ Docker client initialized successfully")
        print(f"   OpenHands image: {client.openhands_image}")
        print(f"   Runtime image: {client.runtime_image}")
        print(f"   Config model: {client.config.model}")
        print(f"   Config workspace: {client.config.workspace_path}")

        return True
    except Exception as e:
        print(f"❌ Docker client initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_execution_engine():
    """Check if execution engine can use Docker runtime."""
    print("\n" + "=" * 80)
    print("✓ STEP 5: Verify Execution Engine Configuration")
    print("=" * 80)

    try:
        from agent_orchestration.openhands_integration.execution_engine import (
            ExecutionEngine,
        )

        integration_config = OpenHandsIntegrationConfig.from_env()

        # Create execution engine
        engine = ExecutionEngine(config=integration_config, max_concurrent_tasks=1)

        # Check which client is being used
        client_type = type(engine.client).__name__
        adapter_fallback = engine.adapter.fallback_to_mock

        print("✅ Execution engine initialized successfully")
        print(f"   Client type: {client_type}")
        print(f"   Adapter fallback to mock: {adapter_fallback}")

        if integration_config.use_docker_runtime:
            if client_type == "DockerOpenHandsClient":
                print("\n✅ Docker runtime is properly configured in execution engine")
                print("   - Using DockerOpenHandsClient")
                print("   - Mock fallback disabled (Docker has full tool access)")
                return True
            print(f"\n⚠️  Docker runtime enabled but using {client_type}")
            return False
        if client_type == "OptimizedOpenHandsClient":
            print("\n✅ SDK mode is properly configured in execution engine")
            print("   - Using OptimizedOpenHandsClient")
            print("   - Mock fallback enabled (SDK has limited tools)")
            return True
        print(f"\n⚠️  Unexpected client type: {client_type}")
        return False
    except Exception as e:
        print(f"❌ Execution engine check failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 80)
    print("DOCKER RUNTIME SETUP VERIFICATION")
    print("=" * 80)

    results = {
        "Docker Available": check_docker_available(),
        ".env Configuration": check_env_configuration(),
        "Config Loading": check_config_loading(),
        "Docker Client Init": check_docker_client_init(),
        "Execution Engine": check_execution_engine(),
    }

    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"\nTotal: {passed_count}/{total_count} checks passed")

    if passed_count == total_count:
        print("\n🚀 Docker runtime setup is complete and verified!")
        print("\nNext steps:")
        print("1. Run a single test task: python scripts/test_single_task.py")
        print("2. Compare Docker runtime vs mock fallback quality")
        print("3. Update batch execution to use Docker runtime")
        return 0
    print(f"\n⚠️  {total_count - passed_count} check(s) failed")
    print("Please review the errors above and fix the configuration")
    return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
